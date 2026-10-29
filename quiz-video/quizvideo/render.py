"""Monta el vídeo: calcula la línea de tiempo, dibuja los fotogramas y exporta a MP4."""

import math
import os
import random
import subprocess
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from . import audio

W, H = 1080, 1920
FPS = 30
LETTERS = "ABCD"

FONT_DIRS = [os.path.join(os.path.dirname(__file__), "..", "fuentes")]
FONT_FALLBACKS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]

# Zona segura de TikTok: evitamos ~150 px arriba, ~370 px abajo y ~120 px a la derecha.
CARD_Y, CARD_H = 290, 420
TIMER_C, TIMER_R = (540, 835), 92
OPT_Y, OPT_H, OPT_GAP = 970, 128, 22
OPT_X0, OPT_X1 = 70, 1010

DIFICULTAD = {"facil": "FÁCIL", "fácil": "FÁCIL", "media": "MEDIO", "medio": "MEDIO",
              "dificil": "DIFÍCIL", "difícil": "DIFÍCIL"}

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
USUARIO = "@hora.delquiz"
USER_Y = 1665  # nombre de usuario fijo abajo
IMG_SIZE, IMG_C = 250, (215, 840)  # imagen de la pregunta: a la izquierda del cronómetro
BPM = 118  # mismo tempo que la música, para que el fondo "lata" al ritmo

# Frases para narrar la respuesta correcta (se alternan)
FRASES_CORRECTA = ["¡Es la {L}! {O}.", "¡La correcta es la {L}! {O}.", "¡Correcto, la {L}! {O}."]
FRASE_SIN_RESPUESTA = "¡Escríbelo en los comentarios si te lo sabes!"

# Modos de plantilla. "trivial" = quiz con respuesta correcta; "pareja" = ¿cuánto conoces a tu pareja?
MODOS = {
    "trivial": {
        "intro_voz": "¡Es hora del quiz! ¿Estás preparado? ¡Vamos!",
        "intro_l1": "¡ES HORA", "intro_l2": "DEL QUIZ!", "pill_intro": None,
        "comentarios_voz": FRASE_SIN_RESPUESTA, "comentarios_pill": "¡ESCRÍBELO EN COMENTARIOS!",
        "outro_voz": "¿Cuántas has acertado?", "outro_titulo": "¿Cuántas has acertado?",
        "outro_sub": "¡Escríbelo en comentarios!", "final_voz": "¡Sígueme para más!",
        "musica": "pop", "bpm": 118, "estilo_voz": "", "tag_final": "[shouting excitedly]",
        "tempo": 1.15, "paleta": "verde", "fin": None,
    },
    "pareja": {
        "intro_voz": "¡Es hora del quiz de parejas! ¿Cuánto conoces a tu pareja? Vamos a comprobarlo...",
        "intro_l1": "¡QUIZ DE", "intro_l2": "PAREJAS!", "pill_intro": "¡JUGAD EN PAREJA!",
        "comentarios_voz": "¡Escribe tu respuesta en los comentarios!",
        "comentarios_pill": "¡ESCRÍBELO EN COMENTARIOS!",
        "outro_voz": "¿Cuántas habéis acertado?", "outro_titulo": "¿Cuántas habéis acertado?",
        "outro_sub": "¡Etiqueta a tu pareja!", "final_voz": "¡Etiqueta a tu pareja y sígueme para más!",
        "musica": "romantica", "bpm": 92, "estilo_voz": "[warm, playful and a little flirty]",
        "tag_final": "[cheerful and playful]", "tempo": 1.08, "paleta": "romantico",
        # frase tras la cuenta atrás (voz, cartel); se van alternando
        "fin": [
            ("¿Habéis coincidido?", "¿HABÉIS COINCIDIDO?"),
            ("¿Lo ha acertado tu pareja?", "¿LO HA ACERTADO?"),
            ("Uy, uy, uy... ¿qué ha contestado?", "UY, UY, UY…"),
            ("¡Esta da para discutir!", "¡ESTA DA PARA DISCUTIR!"),
            ("¿Os conocéis o no?", "¿OS CONOCÉIS O NO?"),
            ("¡Sed sinceros, eh!", "¡SED SINCEROS!"),
        ],
    },
}


# Frases "salseantes" para empezar cada quiz (se elige una distinta por vídeo, ver frases_intro.py)
from .frases_intro import FRASES_INTRO  # noqa: E402


def modo_de(quiz):
    return MODOS.get(quiz.get("modo", "trivial"), MODOS["trivial"])



# ------------------------------------------------------------------ utilidades

def ease_out_back(x):
    x = min(max(x, 0.0), 1.0)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = min(max(x, 0.0), 1.0)
    return x ** 3


def _font_path(kind="texto"):
    for d in FONT_DIRS:
        p = os.path.join(d, f"{kind}.ttf")
        if os.path.exists(p):
            return p
    for f in FONT_FALLBACKS:
        if os.path.exists(f):
            return f
    raise SystemExit("No encuentro ninguna fuente TTF.")


_FONT_CACHE = {}


def font(size, kind="texto"):
    """kind: 'texto' (Baloo 2 ExtraBold) o 'titulo' (Lilita One)."""
    size = max(8, int(size))
    if (size, kind) not in _FONT_CACHE:
        _FONT_CACHE[(size, kind)] = ImageFont.truetype(_font_path(kind), size)
    return _FONT_CACHE[(size, kind)]


def tfont(size):
    return font(size, "titulo")


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=fnt) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, max_w, max_h, start, minimum=28, spacing=1.12):
    size = start
    while size >= minimum:
        f = font(size)
        lines = wrap(draw, text, f, max_w)
        lh = size * spacing
        if len(lines) * lh <= max_h and all(draw.textlength(l, font=f) <= max_w for l in lines):
            return f, lines, lh
        size -= 3
    f = font(minimum)
    return f, wrap(draw, text, f, max_w), minimum * spacing


def draw_lines(draw, lines, fnt, lh, cx, cy, fill, stroke=0, stroke_fill=None):
    total = lh * len(lines)
    y = cy - total / 2 + lh / 2
    for line in lines:
        draw.text((cx, y), line, font=fnt, fill=fill, anchor="mm",
                  stroke_width=stroke, stroke_fill=stroke_fill)
        y += lh


def with_alpha(c, a):
    return (c[0], c[1], c[2], int(max(0, min(1, a)) * 255))


def shadow_box(draw, box, radius, alpha=0.28, off=12):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle((x0, y0 + off, x1, y1 + off), radius, fill=(0, 0, 0, int(255 * alpha)))


# ------------------------------------------------------------------ línea de tiempo

def build_timeline(quiz, voice, countdown=5):
    """Devuelve (escenas, eventos_de_audio, duración_total)."""
    scenes, events = [], []
    t = 0.0
    n = len(quiz["preguntas"])
    tema = quiz["tema"]

    modo = modo_de(quiz)
    if hasattr(voice, "configure"):
        voice.configure(style=modo["estilo_voz"], final_tag=modo["tag_final"], tempo=modo["tempo"])

    def say(text):
        sig, dur = voice.say(text)
        return sig, dur

    # Intro
    intro_text = quiz.get("titulo") or f"¿Cuánto sabes de {tema}?"
    salsa = quiz.get("frase_intro")
    saludo = "¡Es hora del quiz de parejas!" if modo["fin"] is not None else "¡Es hora del quiz!"
    sig, d = say(f"{saludo} {salsa}" if salsa else modo["intro_voz"])
    dur = max(2.8, 0.3 + d + 0.2)
    events += [("fx", "whoosh", t), ("voice", sig, t + 0.35)]
    scenes.append({"kind": "intro", "start": t, "dur": dur, "title": intro_text,
                   "salsa": salsa})
    t += dur

    n_reg = sum(1 for q in quiz["preguntas"] if not q.get("sin_respuesta"))
    for qi, q in enumerate(quiz["preguntas"]):
        st = t
        loc = 0.35
        extra = bool(q.get("sin_respuesta")) and qi == n - 1 and n_reg >= 1
        etiqueta = "¡Pregunta extra!" if extra else f"¡Pregunta {qi + 1}!"
        sig, dq = say(f"{etiqueta} " + q.get("pregunta_voz", q["pregunta"]))
        events += [("fx", "whoosh", st), ("voice", sig, st + loc)]
        loc += max(0.3, dq - 0.4)  # las opciones entran al final de la pregunta
        opt_times = []
        for k, o in enumerate(q["opciones"]):
            # las opciones solo se muestran (no se narran)
            opt_times.append(loc)
            events.append(("fx", "pop", st + loc))
            loc += 0.18
        cd_start = loc + 0.1
        events.append(("music_boost", cd_start, cd_start + countdown))
        # cuenta atrás con tensión: tic-tac, latido, subida (riser) y tics dobles al final
        events.append(("fx", "riser", st + cd_start))
        for s in range(countdown):
            ts = st + cd_start + s
            events.append(("fx", "heart", ts))
            events.append(("fx", "tick_high" if s >= countdown - 2 else "tick", ts))
            events.append(("fx", "tock", ts + 0.5))
            if s >= countdown - 2:
                events.append(("fx", "tick_high", ts + 0.25))
                events.append(("fx", "tick_high", ts + 0.75))
        rv = cd_start + countdown
        ci = LETTERS.index(q["correcta"].upper()) if q.get("correcta") else -1
        comentarios = bool(q.get("sin_respuesta"))
        nores = comentarios or modo["fin"] is not None
        end_pill = None
        if nores:
            # no se revela respuesta: invitación a comentar o frase pícara (modo pareja)
            if comentarios:
                frase, end_pill = modo["comentarios_voz"], modo["comentarios_pill"]
            else:
                frase, end_pill = modo["fin"][qi % len(modo["fin"])]
            sig, dv = say(frase)
            fx_end = "buzz" if modo["fin"] is None else "chime"
            events += [("fx", fx_end, st + rv), ("voice", sig, st + rv + 0.35)]
            rdur = max(2.3, 0.35 + dv + 0.5)
        else:
            # se narra solo la opción correcta
            texto = FRASES_CORRECTA[qi % len(FRASES_CORRECTA)].format(
                L=LETTERS[ci], O=q.get("opcion_voz", q["opciones"])[ci].rstrip("."))
            texto = texto.replace("!.", "!").replace("?.", "?")
            sig, dv = say(texto)
            events += [("fx", "buzz", st + rv), ("fx", "correct", st + rv + 0.15), ("voice", sig, st + rv + 0.4)]
            rdur = max(2.0, 0.4 + dv + 0.15)
        dur = rv + rdur
        scenes.append({"kind": "question", "start": st, "dur": dur, "q": q, "index": qi, "total": n,
                       "opt_times": opt_times, "cd_start": cd_start, "countdown": countdown,
                       "reveal": rv, "correct": ci, "nores": nores, "end_pill": end_pill,
                       "extra": extra, "n_reg": n_reg})
        t += dur

    last_nores = bool(quiz["preguntas"][-1].get("sin_respuesta")) or modo["fin"] is not None
    sig, d = say(modo["outro_voz"] if last_nores else "¿Cuántas has acertado? ¡Déjamelo en comentarios!")
    shout_at = 0.4 + d + 0.1
    sig2, d2 = voice.say(modo["final_voz"], shout=True)
    dur = max(3.5, shout_at + d2 + 0.9)
    events += [("fx", "whoosh", t), ("voice", sig, t + 0.4), ("voice", sig2, t + shout_at),
               ("fx", "applause", t + shout_at)]
    scenes.append({"kind": "outro", "start": t, "dur": dur, "shout_at": shout_at})
    t += dur
    return scenes, events, t


def build_audio(events, total, path, music_on=True, music_style="pop", countdown_len=5):
    mix = audio.Mixer(total)
    fx = {
        "whoosh": audio.sfx_whoosh(), "pop": audio.sfx_pop(), "tick": audio.sfx_tick(),
        "tick_high": audio.sfx_tick(True), "buzz": audio.sfx_buzz_end(), "correct": audio.sfx_correct(), "applause": audio.sfx_applause(), "chime": audio.sfx_correct(),
        "riser": audio.sfx_riser(countdown_len), "heart": audio.sfx_heartbeat(), "tock": audio.sfx_tock(),
    }
    gains = {"whoosh": 0.5, "pop": 0.6, "tick": 1.35, "tick_high": 1.5, "buzz": 0.6, "correct": 0.9, "applause": 0.8, "chime": 0.5, "riser": 0.55, "heart": 0.9, "tock": 1.0}
    boosts = [(a, b) for kind, a, b in events if kind == "music_boost"]
    for kind, what, at in events:
        if kind == "music_boost":
            continue
        if kind == "fx":
            mix.add_fx(fx[what], at, gains[what])
        elif what is not None:
            mix.add_voice(what, at, 1.0)
    music = audio.music(total, style=music_style) if music_on else np.zeros(int(total * audio.SR))
    audio.write_wav(path, mix.render(music, boosts=boosts))


# ------------------------------------------------------------------ dibujo

_STATE = {}


def _init(state):
    _STATE.update(state)
    th = state["theme"]
    top, bot = np.array(th["bg_top"], float), np.array(th["bg_bottom"], float)
    lime = np.array(th.get("bg_mid", (120, 230, 40)), float)
    teal = np.array(th.get("bg_alt", (0, 170, 140)), float)
    # degradado cíclico (periodo H) en una imagen de 2H de alto: se desplaza para dar movimiento
    yy = np.linspace(0, 2, 2 * H)[:, None, None]
    xx = np.linspace(0, 1, W)[None, :, None]
    ph = 2 * np.pi * (yy + 0.35 * xx)
    w1 = (np.cos(ph) + 1) / 2
    w2 = (np.cos(ph * 2 + 1.3) + 1) / 2
    g = top * w1 + bot * (1 - w1)
    g = g * (1 - 0.35 * w2) + (lime * (xx < 2) * 0.6 + teal * 0.4) * 0.35 * w2
    _STATE["bg"] = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    # imágenes de las preguntas (PNG con fondo transparente en assets/imagenes/)
    _STATE["imgs"] = {}
    for sc in state["scenes"]:
        name = sc.get("q", {}).get("imagen") if sc["kind"] == "question" else None
        if name and name not in _STATE["imgs"]:
            ip = os.path.join(ASSETS, "imagenes", name)
            if os.path.exists(ip):
                im = Image.open(ip).convert("RGBA")
                im.thumbnail((IMG_SIZE, IMG_SIZE), Image.LANCZOS)
                _STATE["imgs"][name] = im
    yy, xx = np.mgrid[0:H:4, 0:W:4]
    rr = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    va = (np.clip((rr - 0.7) / 0.5, 0, 1) ** 1.3 * 235).astype(np.uint8)
    vig = Image.new("RGBA", (W // 4, H // 4), (230, 20, 40, 0))
    vig.putalpha(Image.fromarray(va, "L"))
    _STATE["vignette"] = vig.resize((W, H), Image.BILINEAR)
    lp = os.path.join(ASSETS, "logo.png")
    _STATE["logo"] = Image.open(lp).convert("RGBA").resize((800, 800), Image.LANCZOS) if os.path.exists(lp) else None
    rnd = random.Random(11)
    _STATE["bubbles"] = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(40, 160), rnd.uniform(40, 120),
                          rnd.uniform(0.08, 0.18), rnd.uniform(0, 6.28)) for _ in range(12)]
    # formas de colores flotando: (x, y, tamaño, velocidad, giro, fase, tipo, color)
    _STATE["shapes"] = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(18, 48), rnd.uniform(60, 180),
                         rnd.uniform(-2, 2), rnd.uniform(0, 6.28), rnd.randint(0, 3), rnd.randint(0, 4))
                        for _ in range(26)]
    _STATE["confetti"] = [(rnd.uniform(-1, 1), rnd.uniform(-1.4, -0.4), rnd.randint(0, 4),
                           rnd.uniform(12, 26), rnd.uniform(0, 6.28)) for _ in range(70)]


def _shape(d, kind, x, y, s, ang, col):
    if kind == 0:  # anillo
        d.ellipse((x - s, y - s, x + s, y + s), outline=col, width=max(4, int(s / 4)))
    elif kind == 1:  # cruz / signo más
        for a in (ang, ang + math.pi / 2):
            dx, dy = math.cos(a) * s, math.sin(a) * s
            d.line([(x - dx, y - dy), (x + dx, y + dy)], fill=col, width=max(5, int(s / 3)))
    elif kind == 2:  # triángulo
        d.polygon([(x + s * math.cos(ang + k * 2.094), y + s * math.sin(ang + k * 2.094)) for k in range(3)],
                  fill=col)
    elif kind == 4:  # corazón
        _heart(d, x, y, s, ang, col)
    else:  # estrella
        pts = []
        for k in range(10):
            r = s if k % 2 == 0 else s * 0.45
            a = ang + k * math.pi / 5
            pts.append((x + r * math.cos(a), y + r * math.sin(a)))
        d.polygon(pts, fill=col)


def _heart(d, x, y, s, ang, col):
    pts = []
    ca, sa = math.cos(ang * 0.3), math.sin(ang * 0.3)
    for k in range(28):
        u = k / 28 * 2 * math.pi
        hx = 16 * math.sin(u) ** 3
        hy = -(13 * math.cos(u) - 5 * math.cos(2 * u) - 2 * math.cos(3 * u) - math.cos(4 * u))
        hx, hy = hx * s / 17, hy * s / 17
        pts.append((x + hx * ca - hy * sa, y + hx * sa + hy * ca))
    d.polygon(pts, fill=col)


def _background(t):
    th = _STATE["theme"]
    off = int((t * 70) % H)  # el degradado sube poco a poco
    img = _STATE["bg"].crop((0, off, W, off + H))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # rayos giratorios de concurso que laten al ritmo de la música
    bpm = _STATE.get("bpm", BPM)
    beat = (t % (60 / bpm)) / (60 / bpm)
    glow = (16 + 20 * math.exp(-beat * 5)) * th.get("rayos", 1.0)
    cx, cy, R = 540, 880, 2200
    base = math.radians(t * 12)
    for k in range(18):
        a0 = base + k * 2 * math.pi / 18
        a1 = a0 + math.pi / 18
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                   (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=(255, 255, 255, int(glow)))
    for x0, y0, r, sp, a, ph in _STATE["bubbles"]:
        y = (y0 - sp * t) % (H + 2 * r) - r
        x = x0 + 40 * math.sin(t * 0.9 + ph)
        rr = r * (1 + 0.06 * math.exp(-beat * 5))
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=with_alpha(th["blob"], a))
    cols = th["options"] + [th["accent"]]
    for x0, y0, s, sp, rot, ph, kind, ci in _STATE["shapes"]:
        y = (y0 - sp * t) % (H + 120) - 60
        x = x0 + 50 * math.sin(t * 1.3 + ph)
        if th.get("formas") == "corazones":
            kind = 4 if kind != 3 else 3  # casi todo corazones, algún destello
            ang = ph + 0.4 * math.sin(t * 1.5 + ph)
        else:
            ang = ph + rot * t
        _shape(d, kind, x, y, s * (1.25 if kind == 4 else 1), ang, with_alpha(cols[ci], 0.75))
    img.alpha_composite(layer)
    return img


def _pill(d, cx, cy, text, size, bg, fg, pad=(36, 18)):
    f = tfont(size)
    w = d.textlength(text, font=f)
    box = (cx - w / 2 - pad[0], cy - size / 2 - pad[1], cx + w / 2 + pad[0], cy + size / 2 + pad[1])
    shadow_box(d, box, (box[3] - box[1]) / 2, 0.25, 7)
    d.rounded_rectangle(box, (box[3] - box[1]) / 2, fill=bg)
    d.rounded_rectangle((box[0] + 6, box[1] + 4, box[2] - 6, box[1] + (box[3] - box[1]) * 0.42),
                        (box[3] - box[1]) / 4, fill=(255, 255, 255, 28))
    d.text((cx, cy + size * 0.04), text, font=f, fill=fg, anchor="mm")


def _check(d, cx, cy, s, color, width=10):
    d.line([(cx - s * 0.5, cy), (cx - s * 0.12, cy + s * 0.4), (cx + s * 0.55, cy - s * 0.45)],
           fill=color, width=width, joint="curve")


def _draw_intro(layer, sc, lt):
    th = _STATE["theme"]
    d = ImageDraw.Draw(layer)
    quiz = _STATE["quiz"]
    # "¡ES HORA DEL QUIZ!" que rebota
    p = ease_out_back(lt / 0.6)
    wob = math.sin(lt * 5)
    modo = modo_de(quiz)
    d.text((540, 365), modo["intro_l1"], font=tfont((34 + 104 * p) * (1 + 0.025 * wob)), fill=th["text_light"],
           anchor="mm", stroke_width=12, stroke_fill=th["text_dark"])
    d.text((540, 515), modo["intro_l2"], font=tfont((44 + 128 * p) * (1 - 0.025 * wob)), fill=th["accent"],
           anchor="mm", stroke_width=14, stroke_fill=th["text_dark"])
    # tarjeta con el título
    a = ease_out_back((lt - 0.25) / 0.5)
    y = 650 + (1 - a) * 900
    box = (80, y, 1000, y + 440)
    shadow_box(d, box, 50)
    d.rounded_rectangle(box, 50, fill=th["card"])
    if sc.get("salsa"):
        f, lines, lh = fit(d, sc["title"], 820, 150, 70, 40, 1.0)
        draw_lines(d, lines, f, lh, 540, y + 95, th["text_dark"])
        d.line((240, y + 185, 840, y + 185), fill=th["accent2"], width=6)
        f2, l2, lh2 = fit(d, sc["salsa"], 820, 220, 50, 30, 1.05)
        draw_lines(d, l2, f2, lh2, 540, y + 315, th["accent2"])
    else:
        f, lines, lh = fit(d, sc["title"], 820, 360, 86)
        draw_lines(d, lines, f, lh, 540, y + 220, th["text_dark"])
    # etiquetas
    b = ease_out_back((lt - 0.55) / 0.45)
    if b > 0:
        dif = DIFICULTAD.get(str(quiz.get("dificultad", "media")).lower(), str(quiz.get("dificultad", "")).upper())
        _pill(d, 540 - (1 - b) * 1200, 1230, modo["pill_intro"] or f"NIVEL: {dif}", 50,
              th["accent2"], th["text_light"])
        n = len(quiz["preguntas"])
        n_reg = sum(1 for q in quiz["preguntas"] if not q.get("sin_respuesta"))
        txt_n = f"{n_reg} PREGUNTAS + EXTRA" if n_reg < n else f"{n} PREGUNTAS"
        _pill(d, 540 + (1 - b) * 1200, 1360, f"{txt_n} · {_STATE['countdown']} S", 44, th["accent"], th["text_dark"])


def _draw_outro(layer, sc, lt):
    th = _STATE["theme"]
    d = ImageDraw.Draw(layer)
    modo = modo_de(_STATE["quiz"])
    a = ease_out_back(lt / 0.5)
    y = 250 + (1 - a) * -800
    box = (80, y, 1000, y + 520)
    shadow_box(d, box, 50)
    d.rounded_rectangle(box, 50, fill=th["card"])
    f, lines, lh = fit(d, modo["outro_titulo"], 820, 300, 110)
    draw_lines(d, lines, f, lh, 540, y + 200, th["text_dark"])
    d.text((540, y + 420), modo["outro_sub"], font=font(54), fill=th["accent2"], anchor="mm")
    b = ease_out_back((lt - sc.get("shout_at", 0.5) + 0.15) / 0.4)
    if b > 0:
        pulse = 1 + 0.07 * math.sin(lt * 9)
        _pill(d, 540, 900 + (1 - b) * 900, "¡SÍGUEME PARA MÁS!", int(64 * pulse), th["accent"], th["text_dark"])
    c = ease_out_back((lt - sc.get("shout_at", 0.5) - 0.2) / 0.6)
    if c > 0 and _STATE.get("logo") is not None:
        size = int(400 * c * (1 + 0.025 * math.sin(lt * 4)))
        if size > 4:
            logo = _STATE["logo"].resize((size, size), Image.LANCZOS)
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sh).ellipse((540 - size / 2, 1300 - size / 2 + 12, 540 + size / 2, 1300 + size / 2 + 12),
                                       fill=(0, 0, 0, 70))
            layer.alpha_composite(sh)
            layer.alpha_composite(logo, (540 - size // 2, 1300 - size // 2))


def _draw_question(layer, sc, lt):
    th = _STATE["theme"]
    d = ImageDraw.Draw(layer)
    q = sc["q"]
    nores = sc.get("nores", False)
    ended = lt >= sc["reveal"]
    revealed = ended and not nores  # se muestra la correcta
    rlt = lt - sc["reveal"]

    # cabecera: pregunta X/N + puntos de progreso
    a = ease_out_back(lt / 0.45)
    if sc.get("extra"):
        yh = 175 - (1 - a) * 300
        _pill(d, 540, yh, "PREGUNTA EXTRA", 48, th["accent2"], th["text_light"])
        wtxt = d.textlength("PREGUNTA EXTRA", font=tfont(48))
        for sx in (-1, 1):
            _shape(d, 3, 540 + sx * (wtxt / 2 + 80), yh, 26 + 3 * math.sin(lt * 6), lt * 2 * sx, th["accent"])
    else:
        tot = sc.get("n_reg") or sc["total"]
        _pill(d, 540, 175 - (1 - a) * 300, f"PREGUNTA {sc['index'] + 1}/{tot}", 48, th["accent"], th["text_dark"])
    # barra de progreso por segmentos
    segs = sc["total"]
    sw, gap = 70, 12
    x0 = 540 - (segs * sw + (segs - 1) * gap) / 2
    for k in range(segs):
        xs = x0 + k * (sw + gap)
        col = th["accent"] if k < sc["index"] else ((255, 255, 255, 235) if k == sc["index"] else (255, 255, 255, 70))
        d.rounded_rectangle((xs, 248 - (1 - a) * 300, xs + sw, 260 - (1 - a) * 300), 6, fill=col)

    # tarjeta de la pregunta
    a = ease_out_back((lt - 0.05) / 0.5)
    y = CARD_Y + (1 - a) * -700
    box = (OPT_X0, y, OPT_X1, y + CARD_H)
    shadow_box(d, box, 44)
    d.rounded_rectangle(box, 44, fill=th["card"])
    f, lines, lh = fit(d, q["pregunta"], 840, CARD_H - 70, 78, 40)
    draw_lines(d, lines, f, lh, 540, y + CARD_H / 2, th["text_dark"])

    # imagen de la pregunta (entra con rebote, flota y se aparta si sale el cartel final)
    im = _STATE["imgs"].get(q.get("imagen"))
    if im is not None and lt > 0.5:
        ip = ease_out_back((lt - 0.5) / 0.5)
        fade = 1.0
        if nores and ended:
            fade = max(0.0, 1 - rlt / 0.3)
        if fade > 0 and ip > 0.05:
            sc_ = ip * (1 + 0.03 * math.sin(lt * 3))
            w_, h_ = max(4, int(im.width * sc_)), max(4, int(im.height * sc_))
            img2 = im.resize((w_, h_), Image.BILINEAR).rotate(6 * math.sin(lt * 1.7), resample=Image.BICUBIC, expand=True)
            if fade < 1:
                a_ = img2.getchannel("A").point(lambda v: int(v * fade))
                img2.putalpha(a_)
            cx_, cy_ = IMG_C[0], IMG_C[1] + 10 * math.sin(lt * 2.2)
            d.ellipse((cx_ - w_ * 0.38, IMG_C[1] + IMG_SIZE * 0.47 - 14, cx_ + w_ * 0.38, IMG_C[1] + IMG_SIZE * 0.47 + 14),
                      fill=(0, 0, 0, int(60 * fade * ip)))
            layer.alpha_composite(img2, (int(cx_ - img2.width / 2), int(cy_ - img2.height / 2)))

    # cronómetro
    cs, n = sc["cd_start"], sc["countdown"]
    if nores and ended:
        # en vez del cronómetro: invitación a comentar
        pp = ease_out_back(rlt / 0.45)
        pulse = 1 + 0.05 * math.sin(rlt * 9)
        _pill(d, 540, 840, sc.get("end_pill") or "¡ESCRÍBELO EN COMENTARIOS!", int(max(10, 52 * pp * pulse)),
              th["accent2"], th["text_light"])
        if th.get("formas") == "corazones" and rlt < 2.2:
            # corazones que suben desde el cartel
            cols = th["options"] + [th["accent"]]
            for vx, vy, ci, sz, ph in _STATE["confetti"][:30]:
                hx = 540 + vx * 420 + 25 * math.sin(rlt * 4 + ph)
                hy = 840 - (0.6 - vy) * 520 * rlt
                al = 1 - max(0, (rlt - 1.4) / 0.8)
                _heart(d, hx, hy, sz * 1.1, ph, with_alpha(cols[ci], al))
    elif lt >= cs - 0.3:
        ap = ease_out_back((lt - cs + 0.3) / 0.35)
        cx, cy = TIMER_C
        r = TIMER_R * ap
        remaining = max(0.0, n - (lt - cs)) if lt >= cs else n
        frac = remaining / n
        col = th["correct"] if frac > 0.6 else ((255, 190, 0) if frac > 0.3 else (255, 60, 60))
        if revealed:
            col = th["accent2"]
        shake = 6 * math.sin(lt * 60) if (0 < remaining <= 2 and not revealed) else 0
        cx += shake
        if not revealed and lt >= cs:
            g_ = 10 + 8 * (1 - ((lt - cs) % 1))
            d.ellipse((cx - r - g_ - 8, cy - r - g_ - 8, cx + r + g_ + 8, cy + r + g_ + 8), fill=col + (70,))
        d.ellipse((cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8), fill=(0, 0, 0, 60))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, 255))
        if r > 10:
            d.arc((cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6), -90, -90 + 360 * frac, fill=col, width=18)
        if revealed:
            _check(d, cx, cy, r * 0.9, th["correct"], 16)
        else:
            num = math.ceil(remaining) if lt >= cs else n
            beat = (lt - cs) % 1 if lt >= cs else 1
            pop = 1 + 0.35 * (1 - ease_out(beat / 0.25)) if lt >= cs else 1
            d.text((cx, cy + 6), str(max(1, num)), font=tfont(104 * pop * ap), fill=th["text_dark"], anchor="mm")

    # opciones
    for k, opt in enumerate(q["opciones"]):
        ot = sc["opt_times"][k]
        if lt < ot:
            continue
        p = ease_out_back((lt - ot) / 0.4)
        yy = OPT_Y + k * (OPT_H + OPT_GAP)
        xoff = (1 - p) * 1100
        x0, x1 = OPT_X0 + xoff, OPT_X1 + xoff
        is_ok = k == sc["correct"]
        fill, txt, badge, btxt = th["card"], th["text_dark"], th["options"][k], th["text_light"]
        grow = 0
        if revealed:
            rp = ease_out(rlt / 0.35)
            if is_ok:
                fill, txt, badge, btxt = th["correct"], th["text_light"], th["text_light"], th["correct"]
                grow = 14 * ease_out_back(rlt / 0.4) + 4 * math.sin(rlt * 8) * (rlt > 0.4)
            else:
                g = th["wrong"]
                fill = tuple(int(th["card"][i] * (1 - rp) + g[i] * rp) for i in range(3))
                txt = tuple(int(th["text_dark"][i] * (1 - rp) + 235 * rp) for i in range(3))
                badge = tuple(int(th["options"][k][i] * (1 - rp) + 150 * rp) for i in range(3))
        b = (x0 - grow, yy - grow / 2, x1 + grow, yy + OPT_H + grow / 2)
        shadow_box(d, b, 36, 0.22, 14)
        edge = tuple(max(0, int(c * 0.78)) for c in fill[:3])
        d.rounded_rectangle((b[0], b[1] + 8, b[2], b[3] + 8), 36, fill=edge)
        d.rounded_rectangle(b, 36, fill=fill)
        bc = (x0 + 70 - grow, yy + OPT_H / 2)
        d.ellipse((bc[0] - 46, bc[1] - 46, bc[0] + 46, bc[1] + 46), fill=badge)
        if revealed and is_ok:
            _check(d, bc[0], bc[1], 52, btxt, 11)
        else:
            d.text((bc[0], bc[1] + 3), LETTERS[k], font=tfont(58), fill=btxt, anchor="mm")
        f, lines, lh = fit(d, opt, x1 - x0 - 190, OPT_H - 24, 54, 30)
        draw_lines(d, lines, f, lh, (x0 + 140 + x1) / 2, yy + OPT_H / 2, txt)

    # confeti en la revelación
    if revealed and rlt < 2.5:
        yy = OPT_Y + sc["correct"] * (OPT_H + OPT_GAP) + OPT_H / 2
        cols = th["options"] + [th["accent"]]
        for vx, vy, ci, s, ph in _STATE["confetti"]:
            tt = rlt
            x = 540 + vx * 900 * tt
            y = yy + vy * 1300 * tt + 1400 * tt * tt
            ang = ph + tt * 8
            dx, dy = math.cos(ang) * s, math.sin(ang) * s * 0.5
            alpha = 1 - max(0, (tt - 1.6) / 0.9)
            d.polygon([(x - dx, y - dy), (x + dy, y - dx), (x + dx, y + dy), (x - dy, y + dx)],
                      fill=with_alpha(cols[ci], alpha))


def render_frame(i):
    t = i / FPS
    scenes = _STATE["scenes"]
    img = _background(t)
    for sc in scenes:
        lt = t - sc["start"]
        if 0 <= lt < sc["dur"]:
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            {"intro": _draw_intro, "question": _draw_question, "outro": _draw_outro}[sc["kind"]](layer, sc, lt)
            out_t = sc["dur"] - lt
            if out_t < 0.3 and sc is not scenes[-1]:
                # transición de salida: desliza hacia la izquierda
                shift = int(-ease_in(1 - out_t / 0.3) * W)
                moved = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                moved.paste(layer, (shift, 0))
                layer = moved
            if sc["kind"] == "question":
                # viñeta roja que late en los últimos 2,5 s de la cuenta atrás (solo sobre el fondo)
                t_end = sc["cd_start"] + sc["countdown"]
                if t_end - 2.5 <= lt < t_end:
                    k = (lt - (t_end - 2.5)) / 2.5
                    beat = 0.5 + 0.5 * math.cos((lt - sc["cd_start"]) * 2 * math.pi * 2)
                    alpha = (0.35 + 0.65 * k) * (0.6 + 0.4 * beat)
                    v = _STATE["vignette"].copy()
                    v.putalpha(v.getchannel("A").point(lambda x, a_=alpha: int(x * a_)))
                    img.alpha_composite(v)
            img.alpha_composite(layer)
            break
    _username(img)
    return img.convert("RGB").tobytes()


def _username(img):
    th = _STATE["theme"]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(50)
    w = d.textlength(USUARIO, font=f)
    box = (540 - w / 2 - 34, USER_Y - 44, 540 + w / 2 + 34, USER_Y + 44)
    d.rounded_rectangle(box, 44, fill=(0, 0, 0, 120))
    d.text((540, USER_Y), USUARIO, font=f, fill=th["text_light"], anchor="mm",
           stroke_width=3, stroke_fill=(0, 0, 0, 160))
    img.alpha_composite(layer)


# ------------------------------------------------------------------ exportación

def render_video(quiz, theme, voice, out_path, countdown=5, workers=None, music_on=True, preview=None):
    scenes, events, total = build_timeline(quiz, voice, countdown)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    wav = out_path + ".audio.wav"
    modo = modo_de(quiz)
    build_audio(events, total, wav, music_on, modo["musica"], countdown)
    frames = int(total * FPS)
    state = {"scenes": scenes, "theme": theme, "quiz": quiz, "countdown": countdown, "bpm": modo["bpm"]}

    if preview is not None:  # solo un fotograma PNG para revisar el diseño
        _init(state)
        Image.frombytes("RGB", (W, H), render_frame(int(preview * FPS))).save(out_path)
        os.remove(wav)
        return total

    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav,
           "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-level", "4.1",
           "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
           "-shortest", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers or os.cpu_count(), initializer=_init, initargs=(state,)) as pool:
        for k, fr in enumerate(pool.imap(render_frame, range(frames), chunksize=8)):
            proc.stdin.write(fr)
            if k % (FPS * 5) == 0:
                print(f"  fotograma {k}/{frames}", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg falló al exportar el vídeo.")
    os.remove(wav)
    return total

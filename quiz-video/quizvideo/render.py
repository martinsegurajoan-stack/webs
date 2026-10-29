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
BPM = 118  # mismo tempo que la música, para que el fondo "lata" al ritmo

# Frases para narrar la respuesta correcta (se alternan)
FRASES_CORRECTA = ["¡Es la {L}! {O}.", "¡La correcta es la {L}! {O}.", "¡Correcto, la {L}! {O}."]
FRASE_SIN_RESPUESTA = "¡Escríbelo en los comentarios si te lo sabes!"



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


def _font_path():
    for d in FONT_DIRS:
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.lower().endswith((".ttf", ".otf")):
                    return os.path.join(d, f)
    for f in FONT_FALLBACKS:
        if os.path.exists(f):
            return f
    raise SystemExit("No encuentro ninguna fuente TTF.")


_FONT_CACHE = {}


def font(size):
    size = max(8, int(size))
    if size not in _FONT_CACHE:
        _FONT_CACHE[size] = ImageFont.truetype(_font_path(), size)
    return _FONT_CACHE[size]


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

    def say(text):
        sig, dur = voice.say(text)
        return sig, dur

    # Intro
    intro_text = quiz.get("titulo") or f"¿Cuánto sabes de {tema}?"
    sig, d = say(f"¡Es hora del quiz! {intro_text} ¡Vamos!")
    dur = max(2.8, 0.35 + d + 0.35)
    events += [("fx", "whoosh", t), ("voice", sig, t + 0.35)]
    scenes.append({"kind": "intro", "start": t, "dur": dur, "title": intro_text})
    t += dur

    for qi, q in enumerate(quiz["preguntas"]):
        st = t
        loc = 0.5
        sig, dq = say(f"¡Pregunta {qi + 1}! " + q.get("pregunta_voz", q["pregunta"]))
        events += [("fx", "whoosh", st), ("voice", sig, st + loc)]
        loc += dq + 0.15
        opt_times = []
        for k, o in enumerate(q["opciones"]):
            # las opciones solo se muestran (no se narran)
            opt_times.append(loc)
            events.append(("fx", "pop", st + loc))
            loc += 0.22
        cd_start = loc + 0.2
        events.append(("music_boost", cd_start, cd_start + countdown))
        for s in range(countdown):
            events.append(("fx", "tick_high" if s >= countdown - 2 else "tick", st + cd_start + s))
        rv = cd_start + countdown
        ci = LETTERS.index(q["correcta"].upper())
        nores = bool(q.get("sin_respuesta"))
        if nores:
            # pregunta para comentarios: no se revela la respuesta
            sig, dv = say(FRASE_SIN_RESPUESTA)
            events += [("fx", "buzz", st + rv), ("voice", sig, st + rv + 0.35)]
            rdur = max(2.3, 0.35 + dv + 0.5)
        else:
            # se narra solo la opción correcta
            texto = FRASES_CORRECTA[qi % len(FRASES_CORRECTA)].format(
                L=LETTERS[ci], O=q.get("opcion_voz", q["opciones"])[ci])
            sig, dv = say(texto)
            events += [("fx", "buzz", st + rv), ("fx", "correct", st + rv + 0.15), ("voice", sig, st + rv + 0.5)]
            rdur = max(2.0, 0.5 + dv + 0.25)
        dur = rv + rdur
        scenes.append({"kind": "question", "start": st, "dur": dur, "q": q, "index": qi, "total": n,
                       "opt_times": opt_times, "cd_start": cd_start, "countdown": countdown,
                       "reveal": rv, "correct": ci, "nores": nores})
        t += dur

    last_nores = bool(quiz["preguntas"][-1].get("sin_respuesta"))
    sig, d = say("¿Cuántas has acertado?" if last_nores else "¿Cuántas has acertado? ¡Déjamelo en comentarios!")
    shout_at = 0.4 + d + 0.1
    sig2, d2 = voice.say("¡Sígueme para más!", shout=True)
    dur = max(3.5, shout_at + d2 + 1.0)
    events += [("fx", "whoosh", t), ("voice", sig, t + 0.4), ("voice", sig2, t + shout_at),
               ("fx", "applause", t + shout_at)]
    scenes.append({"kind": "outro", "start": t, "dur": dur, "shout_at": shout_at})
    t += dur
    return scenes, events, t


def build_audio(events, total, path, music_on=True):
    mix = audio.Mixer(total)
    fx = {
        "whoosh": audio.sfx_whoosh(), "pop": audio.sfx_pop(), "tick": audio.sfx_tick(),
        "tick_high": audio.sfx_tick(True), "buzz": audio.sfx_buzz_end(), "correct": audio.sfx_correct(), "applause": audio.sfx_applause(),
    }
    gains = {"whoosh": 0.5, "pop": 0.6, "tick": 1.35, "tick_high": 1.5, "buzz": 0.6, "correct": 0.9, "applause": 0.8}
    boosts = [(a, b) for kind, a, b in events if kind == "music_boost"]
    for kind, what, at in events:
        if kind == "music_boost":
            continue
        if kind == "fx":
            mix.add_fx(fx[what], at, gains[what])
        elif what is not None:
            mix.add_voice(what, at, 1.0)
    music = audio.music(total) if music_on else np.zeros(int(total * audio.SR))
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
    else:  # estrella
        pts = []
        for k in range(10):
            r = s if k % 2 == 0 else s * 0.45
            a = ang + k * math.pi / 5
            pts.append((x + r * math.cos(a), y + r * math.sin(a)))
        d.polygon(pts, fill=col)


def _background(t):
    th = _STATE["theme"]
    off = int((t * 70) % H)  # el degradado sube poco a poco
    img = _STATE["bg"].crop((0, off, W, off + H))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # rayos giratorios de concurso que laten al ritmo de la música
    beat = (t % (60 / BPM)) / (60 / BPM)
    glow = 16 + 20 * math.exp(-beat * 5)
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
        _shape(d, kind, x, y, s, ph + rot * t, with_alpha(cols[ci], 0.75))
    img.alpha_composite(layer)
    return img


def _pill(d, cx, cy, text, size, bg, fg, pad=(34, 16)):
    f = font(size)
    w = d.textlength(text, font=f)
    box = (cx - w / 2 - pad[0], cy - size / 2 - pad[1], cx + w / 2 + pad[0], cy + size / 2 + pad[1])
    shadow_box(d, box, (box[3] - box[1]) / 2, 0.25, 7)
    d.rounded_rectangle(box, (box[3] - box[1]) / 2, fill=bg)
    d.text((cx, cy), text, font=f, fill=fg, anchor="mm")


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
    d.text((540, 365), "¡ES HORA", font=font((30 + 92 * p) * (1 + 0.025 * wob)), fill=th["text_light"],
           anchor="mm", stroke_width=12, stroke_fill=th["text_dark"])
    d.text((540, 515), "DEL QUIZ!", font=font((40 + 112 * p) * (1 - 0.025 * wob)), fill=th["accent"],
           anchor="mm", stroke_width=14, stroke_fill=th["text_dark"])
    # tarjeta con el título
    a = ease_out_back((lt - 0.25) / 0.5)
    y = 650 + (1 - a) * 900
    box = (80, y, 1000, y + 440)
    shadow_box(d, box, 50)
    d.rounded_rectangle(box, 50, fill=th["card"])
    f, lines, lh = fit(d, sc["title"], 820, 360, 86)
    draw_lines(d, lines, f, lh, 540, y + 220, th["text_dark"])
    # etiquetas
    b = ease_out_back((lt - 0.55) / 0.45)
    if b > 0:
        dif = DIFICULTAD.get(str(quiz.get("dificultad", "media")).lower(), str(quiz.get("dificultad", "")).upper())
        _pill(d, 540 - (1 - b) * 1200, 1230, f"NIVEL: {dif}", 50, th["accent2"], th["text_light"])
        n = len(quiz["preguntas"])
        _pill(d, 540 + (1 - b) * 1200, 1360,
              f"{n} PREGUNTAS · {_STATE['countdown']} SEGUNDOS", 44, th["accent"], th["text_dark"])


def _draw_outro(layer, sc, lt):
    th = _STATE["theme"]
    d = ImageDraw.Draw(layer)
    a = ease_out_back(lt / 0.5)
    y = 250 + (1 - a) * -800
    box = (80, y, 1000, y + 520)
    shadow_box(d, box, 50)
    d.rounded_rectangle(box, 50, fill=th["card"])
    f, lines, lh = fit(d, "¿Cuántas has acertado?", 820, 300, 110)
    draw_lines(d, lines, f, lh, 540, y + 200, th["text_dark"])
    d.text((540, y + 420), "¡Escríbelo en comentarios!", font=font(54), fill=th["accent2"], anchor="mm")
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
    _pill(d, 540, 175 - (1 - a) * 300, f"PREGUNTA {sc['index'] + 1}/{sc['total']}", 46,
          th["accent"], th["text_dark"])

    # tarjeta de la pregunta
    a = ease_out_back((lt - 0.05) / 0.5)
    y = CARD_Y + (1 - a) * -700
    box = (OPT_X0, y, OPT_X1, y + CARD_H)
    shadow_box(d, box, 44)
    d.rounded_rectangle(box, 44, fill=th["card"])
    f, lines, lh = fit(d, q["pregunta"], 840, CARD_H - 70, 78, 40)
    draw_lines(d, lines, f, lh, 540, y + CARD_H / 2, th["text_dark"])

    # cronómetro
    cs, n = sc["cd_start"], sc["countdown"]
    if nores and ended:
        # en vez del cronómetro: invitación a comentar
        pp = ease_out_back(rlt / 0.45)
        pulse = 1 + 0.05 * math.sin(rlt * 9)
        _pill(d, 540, 840, "¡ESCRÍBELO EN COMENTARIOS!", int(max(10, 52 * pp * pulse)), th["accent2"], th["text_light"])
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
            d.text((cx, cy + 4), str(max(1, num)), font=font(96 * pop * ap), fill=th["text_dark"], anchor="mm")

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
        shadow_box(d, b, 36, 0.25, 9)
        d.rounded_rectangle(b, 36, fill=fill)
        bc = (x0 + 70 - grow, yy + OPT_H / 2)
        d.ellipse((bc[0] - 46, bc[1] - 46, bc[0] + 46, bc[1] + 46), fill=badge)
        if revealed and is_ok:
            _check(d, bc[0], bc[1], 52, btxt, 11)
        else:
            d.text(bc, LETTERS[k], font=font(56), fill=btxt, anchor="mm")
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
    build_audio(events, total, wav, music_on)
    frames = int(total * FPS)
    state = {"scenes": scenes, "theme": theme, "quiz": quiz, "countdown": countdown}

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

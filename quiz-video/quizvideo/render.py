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
              "dificil": "DIFÍCIL", "difícil": "DIFÍCIL", "alto": "ALTO", "alta": "ALTO"}

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


MODOS["halloween"] = dict(MODOS["trivial"], **{
    "saludo": "¡Es hora del quiz de Halloween!",
    "intro_l1": "¡QUIZ DE", "intro_l2": "HALLOWEEN!",
    "comentarios_voz": "¡Escríbelo en los comentarios… si te atreves!",
    "outro_sub": "¡Escríbelo en comentarios… si te atreves!",
    "final_voz": "¡Sígueme para más, si no te da miedo!",
    "musica": "halloween", "bpm": 104, "estilo_voz": "[playful and spooky]",
    "tag_final": "[spooky, shouting excitedly]", "tempo": 1.12,
})
MODOS["futbol"] = dict(MODOS["trivial"], **{
    "saludo": "¡Es hora del quiz de fútbol!",
    "intro_l1": "¡QUIZ DE", "intro_l2": "FÚTBOL!",
    "comentarios_voz": "¡Escríbelo en los comentarios si eres un crack!",
    "comentarios_pill": "¡ESCRÍBELO EN COMENTARIOS!",
    "outro_sub": "¡Escríbelo en comentarios!",
    "final_voz": "¡Sígueme para más, crack!",
    "musica": "futbol", "bpm": 122, "estilo_voz": "[excited sports commentator]",
    "tag_final": "[shouting, stadium announcer]", "tempo": 1.12,
    "gancho_primero": True,  # la frase gancho va ANTES del saludo
})
MODOS["gamer"] = dict(MODOS["trivial"], **{
    "saludo": "¡Es hora del quiz gamer!",
    "intro_l1": "¡QUIZ", "intro_l2": "GAMER!",
    "outro_voz": "¡Dime tu rango en los comentarios!", "outro_titulo": "¿Qué rango tienes?",
    "outro_sub": "¡Escríbelo en comentarios!",
    "musica": "gamer", "bpm": 128,
})
MODOS["trivial"]["saludo"] = "¡Es hora del quiz!"
# QUIZ "DEL COLE": trivial con decorado escolar (lápices, libros, fórmulas de tiza) y notas al final
MODOS["cole"] = dict(MODOS["trivial"], **{
    "outro_voz": "¡Dime tu nota en los comentarios!", "outro_titulo": "¿Qué nota has sacado?",
    "outro_sub": "¡Escríbelo en comentarios!",
})
# GANCHO PRIMERO en todos los modos (regla del usuario): la frase gancho va antes del saludo
for _m in ("trivial", "pareja", "halloween", "futbol", "gamer", "cole"):
    MODOS[_m]["gancho_primero"] = True
MODOS["pareja"]["saludo"] = "¡Es hora del quiz de parejas!"
# QUIZ DE MASCOTAS: como el de parejas (no hay respuesta correcta), decorado de perros, gatos, conejos…
MODOS["mascota"] = dict(MODOS["pareja"], **{
    "saludo": "¡Es hora del quiz de mascotas!",
    "intro_l1": "¡QUIZ DE", "intro_l2": "MASCOTAS!", "pill_intro": "¡PIENSA EN TU MASCOTA!",
    "comentarios_voz": "¡Escribe en los comentarios qué haría la tuya!",
    "comentarios_pill": "¡DÍMELO EN COMENTARIOS!",
    "outro_voz": "¿Conoces de verdad a tu mascota? ¡Cuéntamelo en comentarios!",
    "outro_titulo": "¿Conoces de verdad a tu mascota?", "outro_sub": "¡Cuéntamelo en comentarios!",
    "final_voz": "Si te ha gustado y quieres la parte dos, ¡sígueme y apoya el vídeo!",
    "outro_pill": "¡SÍGUEME PARA LA PARTE 2!", "outro_pill2": "APOYA EL VÍDEO",
    "musica": "pop", "bpm": 118, "estilo_voz": "[cheerful and playful]",
    "tag_final": "[excited, cheerful]", "tempo": 1.12,
    "fin": [
        ("¿Lo sabías seguro?", "¿LO SABÍAS SEGURO?"),
        ("¡Ay, pobrecito!", "¡AY, POBRECITO!"),
        ("¡El rey de la casa!", "¡EL REY DE LA CASA!"),
        ("¡Qué penita da!", "¡QUÉ PENITA!"),
        ("¿Viene o pasa de ti?", "¿VIENE O PASA DE TI?"),
    ],
    "gancho_primero": True,
})


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
        voice.configure(style=modo["estilo_voz"], final_tag=modo["tag_final"], tempo=quiz.get("tempo", modo["tempo"]))

    def say(text):
        sig, dur = voice.say(text)
        return sig, dur

    # Intro
    intro_text = quiz.get("titulo") or f"¿Cuánto sabes de {tema}?"
    salsa = quiz.get("frase_intro")
    saludo = modo["saludo"]
    if salsa and modo.get("gancho_primero"):
        sig, d = say(f"{salsa} {saludo}")
    else:
        sig, d = say(f"{saludo} {salsa}" if salsa else modo["intro_voz"])
    dur = max(2.8, 0.3 + d + 0.2)
    # GANCHO: la voz suena desde el primer fotograma (regla del usuario)
    events += [("fx", "whoosh", t), ("voice", sig, t + 0.05)]
    scenes.append({"kind": "intro", "start": t, "dur": dur, "title": intro_text,
                   "salsa": salsa})
    t += dur

    n_reg = sum(1 for q in quiz["preguntas"] if not q.get("sin_respuesta"))
    for qi, q in enumerate(quiz["preguntas"]):
        st = t
        loc = 0.35
        extra = bool(q.get("sin_respuesta")) and qi == n - 1 and n_reg >= 1
        etiqueta = q.get("etiqueta_voz") or ("¡Pregunta extra!" if extra else f"¡Pregunta {qi + 1}!")
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
                frase, end_pill = q.get("fin") or modo["fin"][qi % len(modo["fin"])]
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
            if q.get("comentario", q.get("chiste")):
                # chiste corto después de la respuesta (se ve en la tarjeta mientras se dice)
                sigj, dj = say(q.get("comentario", q.get("chiste")))
                joke_at = rv + 0.4 + dv + 0.2
                events.append(("voice", sigj, st + joke_at))
                rdur = max(rdur, joke_at - rv + dj + 0.3)
        joke_t = (rv + 0.4 + dv + 0.2) if (q.get("comentario", q.get("chiste")) and not nores) else None
        dur = rv + rdur
        scenes.append({"kind": "question", "start": st, "dur": dur, "q": q, "index": qi, "total": n,
                       "opt_times": opt_times, "cd_start": cd_start, "countdown": countdown,
                       "reveal": rv, "correct": ci, "nores": nores, "end_pill": end_pill,
                       "extra": extra, "n_reg": n_reg, "joke_t": joke_t})
        t += dur

    if quiz.get("rangos"):
        # pantalla de rangos: cada rango entra y se ilumina mientras se dice
        st = t
        sig, d0 = say(quiz.get("rangos_voz", "¿Cuántas has acertado? ¡Mira tu rango!"))
        events += [("fx", "whoosh", st), ("voice", sig, st + 0.25)]
        loc = 0.25 + d0 + 0.1
        times = []
        if quiz.get("rangos_rapido"):
            # versión corta: las notas entran seguidas mientras suena una sola frase
            loc = 0.6
            for r in quiz["rangos"]:
                times.append(loc)
                events.append(("fx", "pop", st + loc))
                loc += 0.55
            loc = max(loc, 0.25 + d0 + 0.2)
        for r in ([] if quiz.get("rangos_rapido") else quiz["rangos"]):
            sigr, dr = say(r["voz"])
            times.append(loc)
            events += [("fx", "pop", st + loc), ("voice", sigr, st + loc + 0.1)]
            loc += 0.1 + dr + 0.15
        events += [("fx", "correct", st + times[-1]), ("fx", "applause", st + times[-1] + 0.2)]
        dur = loc + 0.7
        scenes.append({"kind": "rangos", "start": st, "dur": dur, "times": times})
        t += dur

    last_nores = bool(quiz["preguntas"][-1].get("sin_respuesta")) or modo["fin"] is not None
    if quiz.get("rangos_rapido"):
        sig, d = None, 0.0  # la pantalla de notas ya pide comentar: solo queda el «¡Sígueme!»
    else:
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
    _STATE["rimgs"] = {}
    for r in state["quiz"].get("rangos", []):
        ip = os.path.join(ASSETS, "imagenes", r["imagen"])
        if os.path.exists(ip):
            _STATE["rimgs"][r["imagen"]] = Image.open(ip).convert("RGBA").resize((150, 150), Image.LANCZOS)
    _STATE["decor"] = {}
    if th.get("formas") == "gamer":
        _init_gamer(th)
    if th.get("formas") == "cole":
        _init_cole(th)
    if th.get("formas") == "futbol":
        _init_futbol(th)
    if th.get("formas") == "mascotas":
        _init_mascotas(th)
    if th.get("formas") == "halloween":
        dd = os.path.join(ASSETS, "decor_halloween")

        def spr(name, size):
            im = Image.open(os.path.join(dd, name + ".png")).convert("RGBA")
            return im.resize((size, size), Image.LANCZOS)

        D = _STATE["decor"]
        D["luna"] = spr("luna", 250)
        D["telarana"] = spr("telarana", 300)
        D["arana"] = spr("arana", 90)
        D["calabaza_s"] = spr("calabaza", 110)
        D["sprites"] = {n: [spr(n, sz) for sz in (70, 100, 130)]
                        for n in ("murcielago", "fantasma", "calabaza", "calavera", "caramelo", "piruleta")}
        # halo de la luna
        gy, gx = np.mgrid[0:500, 0:500]
        gr = np.sqrt((gx - 250) ** 2 + (gy - 250) ** 2) / 250
        halo = Image.new("RGBA", (500, 500), (255, 200, 120, 0))
        halo.putalpha(Image.fromarray((np.clip(1 - gr, 0, 1) ** 2 * 150).astype(np.uint8), "L"))
        D["halo"] = halo
        # niebla: franja de nubes blancas semitransparentes (se desplaza en horizontal)
        fog = Image.new("RGBA", (W * 2, 520), (0, 0, 0, 0))
        fd = ImageDraw.Draw(fog)
        rf = random.Random(5)
        for _ in range(40):
            fx, fy = rf.uniform(0, W * 2), rf.uniform(150, 520)
            fw, fh = rf.uniform(180, 420), rf.uniform(60, 140)
            fd.ellipse((fx - fw, fy - fh, fx + fw, fy + fh), fill=(235, 225, 255, rf.randint(18, 40)))
        from PIL import ImageFilter

        D["fog"] = fog.filter(ImageFilter.GaussianBlur(30))
        rs = random.Random(21)
        names = ["murcielago"] * 6 + ["fantasma"] * 4 + ["calavera", "caramelo", "piruleta", "calabaza"] * 2
        D["flyers"] = [(n, rs.randint(0, 2), rs.uniform(0, W), rs.uniform(0, H), rs.uniform(40, 110),
                        rs.uniform(0, 6.28), rs.choice((-1, 1))) for n in names]
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


def _init_gamer(th):
    """Decorado gamer: sprites 3D (mandos, monedas, gemas, invasores…), bloques de píxel y estrellas."""
    D = _STATE["decor"]
    dd = os.path.join(ASSETS, "decor_gamer")
    names = ("mando", "joystick", "invasor", "moneda", "gema", "seta", "estrella", "corazon", "trofeo", "espada")
    D["sprites"] = {n: [Image.open(os.path.join(dd, n + ".png")).convert("RGBA").resize((sz, sz), Image.LANCZOS)
                        for sz in (62, 86, 112)] for n in names}
    rs = random.Random(13)
    lst = ["mando", "invasor", "moneda", "moneda", "gema", "seta", "estrella", "corazon", "joystick",
           "trofeo", "espada", "invasor", "moneda", "estrella", "gema"]
    D["flyers"] = [(n, rs.randint(0, 2), rs.uniform(0, W), rs.uniform(0, H), rs.uniform(40, 95),
                    rs.uniform(0, 6.28)) for n in lst]
    D["blocks"] = [(rs.uniform(0, W), rs.uniform(0, H), rs.choice((24, 32, 42, 54)), rs.uniform(30, 85),
                    rs.uniform(0, 6.28), rs.randint(0, 4)) for _ in range(20)]
    D["stars"] = [(rs.uniform(0, W), rs.uniform(0, 1260), rs.choice((5, 7, 9)), rs.uniform(0, 6.28))
                  for _ in range(36)]


def _gamer(img, t, beat):
    """Estrellas de píxel, rejilla synthwave al ritmo, bloques de píxel subiendo y sprites gamer."""
    th = _STATE["theme"]
    D = _STATE["decor"]
    pulse = math.exp(-beat * 5)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x, y, s, ph in D["stars"]:
        a = 0.3 + 0.7 * abs(math.sin(t * 2.2 + ph))
        d.rectangle((x - s / 2, y - s * 1.5, x + s / 2, y + s * 1.5), fill=(255, 255, 255, int(160 * a)))
        d.rectangle((x - s * 1.5, y - s / 2, x + s * 1.5, y + s / 2), fill=(255, 255, 255, int(160 * a)))
    hz = 1300
    gc = th["accent"]
    d.rectangle((0, hz - 5, W, hz + 5), fill=gc + (int(110 + 90 * pulse),))
    for k in range(14):
        z = ((k + t * 1.5) % 14) / 14
        y = hz + (H - hz) * z ** 2.2
        d.line((0, y, W, y), fill=gc + (int(30 + 110 * z),), width=max(2, int(2 + 5 * z)))
    for k in range(-11, 12):
        d.line((540 + k * 16, hz, 540 + k * 230, H), fill=gc + (85,), width=3)
    cols = th["options"] + [th["accent"]]
    for x0, y0, s, sp, ph, ci in D["blocks"]:
        y = (y0 - sp * t) % (H + 120) - 60
        x = x0 + 22 * math.sin(t * 0.8 + ph)
        c = cols[ci]
        d.rectangle((x - s / 2, y - s / 2, x + s / 2, y + s / 2), fill=c + (190,))
        d.rectangle((x - s / 2, y - s / 2, x + s / 2, y - s / 2 + s * 0.24), fill=(255, 255, 255, 90))
        d.rectangle((x - s / 2, y + s / 2 - s * 0.24, x + s / 2, y + s / 2), fill=(0, 0, 0, 70))
        d.rectangle((x - s / 2, y - s / 2, x + s / 2, y + s / 2), outline=(0, 0, 0, 110), width=3)
    img.alpha_composite(layer)
    for n, si, x0, y0, sp, ph in D["flyers"]:
        im = D["sprites"][n][si]
        x = x0 + 45 * math.sin(t * 0.7 + ph)
        y = (y0 - sp * t) % (H + 260) - 130
        if n == "moneda":  # gira como una moneda
            fl = abs(math.cos(t * 3 + ph))
            im = im.resize((max(6, int(im.width * fl)), im.height), Image.BILINEAR)
        else:
            im = im.rotate(16 * math.sin(t * 1.4 + ph), resample=Image.BICUBIC, expand=True)
        img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def _init_futbol(th):
    """Campo de fútbol visto desde arriba (césped a rayas y líneas) + sprites del decorado."""
    c1, c2 = np.array(th["cesped1"], float), np.array(th["cesped2"], float)
    yy = np.arange(H)[:, None]
    band = ((yy // 160) % 2).astype(float)
    rng = np.random.default_rng(3)
    grass = c1 * (1 - band[..., None]) + c2 * band[..., None]
    grass = np.repeat(grass, W, axis=1)
    grass += rng.normal(0, 4, (H, W, 1))                       # textura de césped
    xx = np.linspace(-1, 1, W)[None, :, None]
    yv = np.linspace(-1, 1, H)[:, None, None]
    grass *= (1 - 0.28 * (xx ** 2 + 0.6 * yv ** 2))[..., :]     # luz de estadio en el centro
    pitch = Image.fromarray(np.clip(grass, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    ln = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ln)
    col, w = (255, 255, 255, 170), 7
    x0, y0, x1, y1 = 60, 110, W - 60, H - 110
    d.rectangle((x0, y0, x1, y1), outline=col, width=w)
    d.line((x0, H / 2, x1, H / 2), fill=col, width=w)
    d.ellipse((540 - 175, H / 2 - 175, 540 + 175, H / 2 + 175), outline=col, width=w)
    d.ellipse((540 - 10, H / 2 - 10, 540 + 10, H / 2 + 10), fill=col)
    for top in (True, False):
        ya, yb = (y0, y0 + 300) if top else (y1 - 300, y1)
        d.rectangle((230, ya, 850, yb), outline=col, width=w)
        ga, gb = (y0, y0 + 120) if top else (y1 - 120, y1)
        d.rectangle((380, ga, 700, gb), outline=col, width=w)
        sp = y0 + 215 if top else y1 - 215
        d.ellipse((540 - 9, sp - 9, 540 + 9, sp + 9), fill=col)
        if top:
            d.arc((540 - 165, sp - 165, 540 + 165, sp + 165), 37, 143, fill=col, width=w)
        else:
            d.arc((540 - 165, sp - 165, 540 + 165, sp + 165), 217, 323, fill=col, width=w)
        # portería con red
        gy = y0 - 50 if top else y1
        d.rectangle((440, gy, 640, gy + 50), outline=(255, 255, 255, 210), width=6)
        for k in range(441, 640, 16):
            d.line((k, gy, k, gy + 50), fill=(255, 255, 255, 70), width=2)
    for cx_, cy_, a0 in ((x0, y0, 0), (x1, y0, 90), (x1, y1, 180), (x0, y1, 270)):
        d.arc((cx_ - 30, cy_ - 30, cx_ + 30, cy_ + 30), a0, a0 + 90, fill=col, width=w)
    from PIL import ImageFilter
    pitch.alpha_composite(ln.filter(ImageFilter.GaussianBlur(1.2)))
    _STATE["pitch"] = pitch
    # brillo de focos (se dibuja latiendo en cada fotograma)
    gy, gx = np.mgrid[0:700, 0:700]
    gr = np.sqrt((gx - 350) ** 2 + (gy - 350) ** 2) / 350
    flare = Image.new("RGBA", (700, 700), (255, 255, 235, 0))
    flare.putalpha(Image.fromarray((np.clip(1 - gr, 0, 1) ** 2.2 * 150).astype(np.uint8), "L"))
    D = _STATE["decor"]
    D["flare"] = flare
    dd = os.path.join(ASSETS, "decor_futbol")

    def spr(name, size):
        im = Image.open(os.path.join(dd, name + ".png")).convert("RGBA")
        return im.resize((size, size), Image.LANCZOS)

    D["sprites"] = {n: [spr(n, sz) for sz in (70, 100, 130)]
                    for n in ("balon", "tarjeta_amarilla", "tarjeta_roja", "trofeo", "bota", "medalla", "megafono")}
    rs = random.Random(8)
    names = ["balon"] * 6 + ["tarjeta_amarilla", "tarjeta_roja"] * 3 + ["trofeo", "bota", "medalla", "megafono"]
    D["flyers"] = [(n, rs.randint(0, 2), rs.uniform(0, W), rs.uniform(0, H), rs.uniform(50, 120),
                    rs.uniform(0, 6.28), rs.choice((-1, 1))) for n in names]
    D["confeti"] = [(rs.uniform(0, W), rs.uniform(0, H), rs.uniform(60, 160), rs.uniform(0, 6.28),
                     rs.choice([(255, 221, 0), (255, 255, 255), (0, 200, 255), (255, 70, 90)])) for _ in range(46)]


def _futbol(img, t, beat):
    """Decorado de fútbol: focos que laten, balones botando, tarjetas girando, trofeos y confeti."""
    D = _STATE["decor"]
    pulse = math.exp(-beat * 4)
    for x in (-120, W - 580):
        fl = D["flare"]
        a = 0.55 + 0.35 * pulse
        f2 = fl.copy()
        f2.putalpha(f2.getchannel("A").point(lambda v, a_=a: int(v * a_)))
        img.alpha_composite(f2, (x, -260))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x0, y0, sp, ph, col in D["confeti"]:
        y = (y0 + sp * t) % (H + 40) - 20
        x = x0 + 30 * math.sin(t * 1.4 + ph)
        s = 7 + 3 * math.sin(t * 5 + ph)
        d.rectangle((x - s, y - s * 0.45, x + s, y + s * 0.45), fill=col + (170,))
    img.alpha_composite(layer)
    for n, si, x0, y0, sp, ph, dirx in D["flyers"]:
        im = D["sprites"][n][si]
        if n == "balon":  # cruza botando y girando
            x = (x0 + dirx * sp * 1.8 * t) % (W + 260) - 130
            y = y0 + (-160 * abs(math.sin(t * 2.2 + ph)))
            im = im.rotate(-dirx * t * 220 % 360, resample=Image.BICUBIC)
        elif n.startswith("tarjeta"):  # tarjetas que caen girando como una moneda
            x = x0 + 50 * math.sin(t * 0.7 + ph)
            y = (y0 + sp * 0.9 * t) % (H + 300) - 150
            flip = abs(math.cos(t * 2.5 + ph))
            im = im.resize((max(6, int(im.width * flip)), im.height), Image.BILINEAR)
        else:
            x = x0 + 40 * math.sin(t * 0.8 + ph)
            y = (y0 - sp * t) % (H + 300) - 150
            im = im.rotate(18 * math.sin(t * 1.5 + ph), resample=Image.BICUBIC, expand=True)
        img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def _background(t):
    th = _STATE["theme"]
    if th.get("formas") == "futbol":
        bpm = _STATE.get("bpm", BPM)
        beat = (t % (60 / bpm)) / (60 / bpm)
        img = _STATE["pitch"].copy()
        _futbol(img, t, beat)
        return img
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
    if th.get("formas") == "halloween":
        img.alpha_composite(layer)
        _halloween(img, t, beat)
        return img
    if th.get("formas") == "gamer":
        img.alpha_composite(layer)
        _gamer(img, t, beat)
        return img
    if th.get("formas") == "cole":
        img.alpha_composite(layer)
        _cole(img, t, beat)
        return img
    if th.get("formas") == "mascotas":
        img.alpha_composite(layer)
        _mascotas(img, t, beat)
        return img
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


def _halloween(img, t, beat):
    """Decorado de Halloween: luna con halo, telarañas, araña colgando, murciélagos, fantasmas,
    caramelos y calaveras flotando, niebla y calabazas abajo."""
    D = _STATE["decor"]
    # luna arriba a la derecha con halo que late suave
    hs = int(500 * (1 + 0.04 * math.sin(t * 1.3)))
    halo = D["halo"].resize((hs, hs), Image.BILINEAR)
    img.alpha_composite(halo, (int(890 - hs / 2), int(110 - hs / 2)))
    img.alpha_composite(D["luna"], (890 - 125, 110 - 125))
    # telarañas en las esquinas superiores
    img.alpha_composite(D["telarana"], (-70, -70))
    # araña bajando y subiendo de su hilo
    sy = 230 + 120 * (0.5 + 0.5 * math.sin(t * 0.9))
    dr = ImageDraw.Draw(img)
    dr.line((60, 40, 60, sy - 30), fill=(230, 230, 240, 200), width=3)
    img.alpha_composite(D["arana"], (60 - 45, int(sy - 45)))
    # bichos y dulces volando
    for n, si, x0, y0, sp, ph, dirx in D["flyers"]:
        im = D["sprites"][n][si]
        if n == "murcielago":
            # cruzan en horizontal aleteando
            x = (x0 + dirx * sp * 2.2 * t) % (W + 300) - 150
            y = y0 + 60 * math.sin(t * 2 + ph)
            flap = 0.55 + 0.45 * abs(math.sin(t * 9 + ph))
            im = im.resize((max(8, int(im.width * flap)), im.height), Image.BILINEAR)
            if dirx < 0:
                im = im.transpose(Image.FLIP_LEFT_RIGHT)
        elif n == "fantasma":
            x = x0 + 70 * math.sin(t * 0.6 + ph)
            y = (y0 - sp * 0.8 * t) % (H + 300) - 150
            a = im.getchannel("A").point(lambda v: int(v * 0.8))
            im = im.copy()
            im.putalpha(a)
        else:
            x = x0 + 40 * math.sin(t * 0.8 + ph)
            y = (y0 - sp * t) % (H + 300) - 150
            im = im.rotate(20 * math.sin(t * 1.5 + ph), resample=Image.BICUBIC, expand=True)
        img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
    # niebla abajo moviéndose
    off = int((t * 40) % W)
    fog = D["fog"].crop((off, 0, off + W, D["fog"].height))
    img.alpha_composite(fog, (0, H - fog.height))
    # calabazas en el suelo que "laten" con la música
    for k, (px, sz) in enumerate(((120, 2), (330, 1), (760, 1), (960, 2))):
        im = D["sprites"]["calabaza"][sz]
        bump = int(8 * math.exp(-beat * 5))
        img.alpha_composite(im, (int(px - im.width / 2), int(H - 90 - im.height / 2 - bump)))


def _init_cole(th):
    """Decorado escolar: lápices, libros, reglas, manzanas… flotando y fórmulas de tiza."""
    dd = os.path.join(ASSETS, "decor_cole")

    def spr(name, size):
        im = Image.open(os.path.join(dd, name + ".png")).convert("RGBA")
        return im.resize((size, size), Image.LANCZOS)

    D = _STATE["decor"]
    nombres = ("lapiz", "libro", "regla", "mochila", "globo", "abaco", "manzana", "bombilla", "birrete",
               "microscopio", "libros", "probeta", "escuadra")
    D["sprites"] = {n: [spr(n, sz) for sz in (80, 110, 140)] for n in nombres}
    D["burst"] = [spr(n, 120) for n in ("lapiz", "libro", "regla", "manzana", "bombilla", "birrete", "escuadra")]
    rs = random.Random(44)
    names = list(nombres) + ["lapiz", "libro", "bombilla"]
    D["flyers"] = [(n, rs.randint(0, 2), rs.uniform(0, W), rs.uniform(0, H), rs.uniform(45, 95),
                    rs.uniform(0, 6.28), rs.choice((-1, 1))) for n in names]
    # fórmulas de tiza que flotan (texto blanco semitransparente)
    formulas = ["2+2=4", "3x3=9", "H2O", "10:2=5", "7x8=?", "ABC", "1/2", "%", "x+y", "?", "A+B", "100%", "5+5=10", "!"]
    D["tiza"] = []
    for k, f in enumerate(formulas):
        fnt = tfont(rs.choice((54, 64, 78)))
        tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        w_ = int(tmp.textlength(f, font=fnt)) + 20
        im = Image.new("RGBA", (w_, fnt.size + 30), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 6), f, font=fnt, fill=(255, 255, 255, 95))
        D["tiza"].append((im, rs.uniform(0, W), rs.uniform(0, H), rs.uniform(25, 55), rs.uniform(0, 6.28)))
    # cuadrícula de cuaderno muy suave
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(0, W, 60):
        gd.line((x, 0, x, H), fill=(255, 255, 255, 22), width=2)
    for y in range(0, H, 60):
        gd.line((0, y, W, y), fill=(255, 255, 255, 22), width=2)
    gd.line((110, 0, 110, H), fill=(255, 90, 110, 70), width=4)  # margen rojo del cuaderno
    D["grid"] = grid


def _cole(img, t, beat):
    D = _STATE["decor"]
    off = int((t * 20) % 60)
    img.alpha_composite(D["grid"].crop((0, 0, W, H - off)), (0, off))
    for im, x0, y0, sp, ph in D["tiza"]:
        x = x0 + 30 * math.sin(t * 0.5 + ph)
        y = (y0 - sp * t) % (H + 200) - 100
        img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
    for n, si, x0, y0, sp, ph, dirx in D["flyers"]:
        im = D["sprites"][n][si]
        x = x0 + 45 * math.sin(t * 0.8 + ph)
        y = (y0 - sp * t) % (H + 300) - 150
        bote = 1 + 0.07 * math.exp(-beat * 5)
        im = im.resize((int(im.width * bote), int(im.height * bote)), Image.BILINEAR)
        im = im.rotate(20 * math.sin(t * 1.4 + ph) + (t * 25 * dirx if n == "lapiz" else 0),
                       resample=Image.BICUBIC, expand=True)
        im.putalpha(im.getchannel("A").point(lambda v: int(v * 0.85)))
        img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def _init_mascotas(th):
    """Sprites del decorado de mascotas (perros, gatos, conejos, huellas, huesos…)."""
    dd = os.path.join(ASSETS, "decor_mascotas")

    def spr(name, size):
        im = Image.open(os.path.join(dd, name + ".png")).convert("RGBA")
        return im.resize((size, size), Image.LANCZOS)

    D = _STATE["decor"]
    nombres = ("perro", "gato", "conejo", "hamster", "hueso", "pez", "ovillo", "pelota", "loro", "tortuga",
               "corazon")
    D["sprites"] = {n: [spr(n, sz) for sz in (80, 110, 140)] for n in nombres}
    # huella blanca semitransparente (rastro de patitas que cruza la pantalla)
    hu = spr("huella", 64)
    blanca = Image.new("RGBA", hu.size, (255, 255, 255, 0))
    blanca.putalpha(hu.getchannel("A").point(lambda v: int(v * 0.5)))
    D["huella"] = blanca
    D["asomados"] = {n: spr(n + "_cuerpo", 260) for n in ("perro", "gato")}
    D["conejo_asoma"] = spr("conejo", 210)
    D["lluvia"] = [spr(n, 70) for n in ("huella", "hueso", "corazon", "pez", "pelota", "huella")]
    rs = random.Random(31)
    names = ["perro", "gato", "conejo", "hamster"] * 2 + ["hueso", "pez", "ovillo", "pelota", "loro",
                                                         "tortuga", "corazon", "corazon"]
    D["flyers"] = [(n, rs.randint(0, 2), rs.uniform(0, W), rs.uniform(0, H), rs.uniform(45, 100),
                    rs.uniform(0, 6.28), rs.choice((-1, 1))) for n in names]
    # rastros de huellas: (y inicial, inclinación, velocidad, desfase)
    D["rastros"] = [(rs.uniform(200, H - 200), rs.uniform(-0.35, 0.35), rs.uniform(130, 190), rs.uniform(0, 30))
                    for _ in range(3)]


def _mascotas(img, t, beat):
    """Decorado de mascotas: rastros de huellas, animalitos y juguetes flotando y mascotas asomándose."""
    D = _STATE["decor"]
    hu = D["huella"]
    for k, (y0, inc, sp, ph) in enumerate(D["rastros"]):
        # las patitas aparecen una a una (como si alguien caminara) y se desvanecen
        paso, n_huellas = 95, 9
        cab = (t * sp + ph * 40) % (W + n_huellas * paso + 400) - 200
        for j in range(n_huellas):
            x = cab - j * paso
            if not -80 < x < W + 80:
                continue
            y = y0 + inc * x + (22 if j % 2 else -22)
            a = 1 - j / n_huellas
            im = hu.rotate(-90 - math.degrees(math.atan(inc)), resample=Image.BICUBIC, expand=True)
            if a < 1:
                im.putalpha(im.getchannel("A").point(lambda v, a_=a: int(v * a_)))
            img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
    for n, si, x0, y0, sp, ph, dirx in D["flyers"]:
        im = D["sprites"][n][si]
        x = x0 + 50 * math.sin(t * 0.7 + ph)
        y = (y0 - sp * t) % (H + 300) - 150
        if n in ("perro", "gato", "conejo", "hamster"):
            bote = 1 + 0.08 * math.exp(-beat * 5)  # laten con la música
            im = im.resize((int(im.width * bote), int(im.height * bote)), Image.BILINEAR)
        im = im.rotate(16 * math.sin(t * 1.6 + ph), resample=Image.BICUBIC, expand=True)
        a = im.getchannel("A").point(lambda v: int(v * 0.85))
        im.putalpha(a)
        img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
    # perro y gato que se asoman por abajo a los lados (suben y bajan por turnos)
    for k, (n, x) in enumerate((("perro", 105), ("gato", W - 105))):
        ciclo = (t + k * 3.5) % 7
        sube = ease_out_back(ciclo / 0.6) if ciclo < 3.5 else max(0.0, 1 - (ciclo - 3.5) / 0.5)
        sube = max(0.0, min(1.1, sube))
        im = D["asomados"][n]
        if k == 1:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        im = im.rotate(8 * math.sin(t * 3 + k) * (-1 if k else 1), resample=Image.BICUBIC)
        y = H + 30 - sube * 230 - 6 * math.exp(-beat * 5)
        img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def _polaroid(im, th):
    """Pone la imagen de la pregunta en una foto tipo polaroid (marco blanco con pie más ancho)."""
    m, pie = 22, 58
    w, h = im.width + 2 * m, im.height + m + pie
    ph = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(ph)
    d.rounded_rectangle((8, 14, w + 8, h + 14), 14, fill=(0, 0, 0, 70))
    d.rounded_rectangle((0, 0, w, h), 14, fill=(255, 255, 255))
    d.rectangle((m, m, w - m, m + im.height), fill=th["blob"])
    ph.alpha_composite(im, (m, m))
    # cinta adhesiva arriba
    d.rectangle((w / 2 - 55, -2, w / 2 + 55, 30), fill=(255, 240, 180, 200))
    _heart(d, w / 2, m + im.height + pie / 2, 17, 0, (230, 30, 50))
    return ph


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
    p = 0.72 + 0.28 * ease_out_back(lt / 0.35)  # grande desde el primer fotograma
    wob = math.sin(lt * 5)
    modo = modo_de(quiz)
    d.text((540, 365), modo["intro_l1"], font=tfont((34 + 104 * p) * (1 + 0.025 * wob)), fill=th["text_light"],
           anchor="mm", stroke_width=12, stroke_fill=th["text_dark"])
    d.text((540, 515), modo["intro_l2"], font=tfont((44 + 128 * p) * (1 - 0.025 * wob)), fill=th["accent"],
           anchor="mm", stroke_width=14, stroke_fill=th["text_dark"])
    # tarjeta con el título
    a = ease_out_back(lt / 0.35)
    y = 650 + (1 - a) * 140  # la tarjeta con el gancho se ve desde el primer fotograma
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
    if quiz.get("pegatina_gancho"):
        c = ease_out_back((lt - 0.3) / 0.4)
        if c > 0:
            pulse = 1 + 0.06 * math.sin(lt * 9)
            _pill(d, 540, 1500 + (1 - c) * 400, quiz["pegatina_gancho"], int(max(10, 66 * pulse)),
                  (235, 35, 60), (255, 255, 255), pad=(46, 24))
    if th.get("formas") == "cole" and lt < 1.8:
        # GANCHO: destello + estallido de lápices, libros y reglas desde el título
        D = _STATE["decor"]
        if lt < 0.18:
            ImageDraw.Draw(layer).rectangle((0, 0, W, H), fill=(255, 255, 255, int(110 * (1 - lt / 0.18))))
        for j, (vx, vy, ci, s_, ph) in enumerate(_STATE["confetti"][:22]):
            im = D["burst"][j % len(D["burst"])]
            x = 540 + vx * 900 * lt
            y = 450 + vy * 1000 * lt + 1100 * lt * lt
            al = max(0.0, 1 - lt / 1.8)
            im2 = im.rotate(math.degrees(ph + lt * 6 * (1 if j % 2 else -1)), resample=Image.BICUBIC)
            if al < 1:
                im2.putalpha(im2.getchannel("A").point(lambda v, a_=al: int(v * a_)))
            layer.alpha_composite(im2, (int(x - im2.width / 2), int(y - im2.height / 2)))
    if th.get("formas") == "gamer":
        # estallido de bloques de píxel desde el título en el primer segundo
        fx = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(fx)
        if lt < 1.6:
            cols = th["options"] + [th["accent"]]
            for vx, vy, ci, s, ph in _STATE["confetti"]:
                x = 540 + vx * 820 * lt
                y = 450 + vy * 900 * lt + 900 * lt * lt
                al = max(0.0, 1 - lt / 1.6)
                d.rectangle((x - s / 2, y - s / 2, x + s / 2, y + s / 2), fill=with_alpha(cols[ci], al),
                            outline=(0, 0, 0, int(120 * al)), width=3)
        if lt < 0.15:
            d.rectangle((0, 0, W, H), fill=(255, 255, 255, int(90 * (1 - lt / 0.15))))
        layer.alpha_composite(fx)


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
    fs, ls_, lhs = fit(d, modo["outro_sub"], 840, 110, 54, 30, 1.05)
    draw_lines(d, ls_, fs, lhs, 540, y + 420, th["accent2"])
    b = ease_out_back((lt - sc.get("shout_at", 0.5) + 0.15) / 0.4)
    if b > 0:
        pulse = 1 + 0.07 * math.sin(lt * 9)
        _pill(d, 540, 900 + (1 - b) * 900, modo.get("outro_pill", "¡SÍGUEME PARA MÁS!"), int(64 * pulse),
              th["accent"], th["text_dark"])
    if modo.get("outro_pill2"):
        b2 = ease_out_back((lt - sc.get("shout_at", 0.5) - 1.1) / 0.4)
        if b2 > 0:
            yb = 1040 + (1 - b2) * 900
            _pill(d, 590, yb, modo["outro_pill2"], 54, (230, 30, 50), (255, 255, 255), pad=(36, 16))
            fw = d.textlength(modo["outro_pill2"], font=tfont(54))
            hb = 1 + 0.25 * abs(math.sin(lt * 6))
            hx = 590 - fw / 2 - 36 - 52
            _heart(d, hx, yb + 2, 40 * hb + 7, 0, (255, 255, 255))
            _heart(d, hx, yb + 2, 40 * hb, 0, (230, 30, 50))
    c = ease_out_back((lt - sc.get("shout_at", 0.5) - 0.2) / 0.6)
    ly = 1360 if modo.get("outro_pill2") else 1300
    if c > 0 and _STATE.get("logo") is not None:
        size = int((330 if modo.get("outro_pill2") else 400) * c * (1 + 0.025 * math.sin(lt * 4)))
        if size > 4:
            logo = _STATE["logo"].resize((size, size), Image.LANCZOS)
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sh).ellipse((540 - size / 2, ly - size / 2 + 12, 540 + size / 2, ly + size / 2 + 12),
                                       fill=(0, 0, 0, 70))
            layer.alpha_composite(sh)
            layer.alpha_composite(logo, (540 - size // 2, ly - size // 2))


def _draw_rangos(layer, sc, lt):
    th = _STATE["theme"]
    d = ImageDraw.Draw(layer)
    rangos = _STATE["quiz"]["rangos"]
    a = ease_out_back(lt / 0.4)
    d.text((540, 240 - (1 - a) * 400), "¿CUÁNTAS", font=tfont(118), fill=th["text_light"], anchor="mm",
           stroke_width=12, stroke_fill=th["text_dark"])
    d.text((540, 375 - (1 - a) * 400), "HAS ACERTADO?", font=tfont(108), fill=th["accent"], anchor="mm",
           stroke_width=12, stroke_fill=th["text_dark"])
    times = sc["times"]
    cur = max([i for i, tt in enumerate(times) if lt >= tt], default=-1)
    n = len(rangos)
    h, gap, y0 = 200, 26, 520
    gold = (255, 196, 30)
    for i, r in enumerate(rangos):
        tt = times[i]
        if lt < tt:
            continue
        p = ease_out_back((lt - tt) / 0.4)
        on = i == cur
        last = i == n - 1
        y = y0 + i * (h + gap)
        xo = (1 - p) * (1100 if i % 2 == 0 else -1100)
        grow = (12 + 4 * math.sin((lt - tt) * 7)) if on else 0
        box = (70 + xo - grow, y - grow / 2, 1010 + xo + grow, y + h + grow / 2)
        if on:
            gl = 0.45 + 0.25 * math.sin(lt * 8)
            d.rounded_rectangle((box[0] - 16, box[1] - 16, box[2] + 16, box[3] + 16), 56,
                                fill=with_alpha(gold if last else th["accent"], gl))
        fill = (255, 232, 140) if last else th["card"]
        shadow_box(d, box, 40, 0.25, 12)
        d.rounded_rectangle((box[0], box[1] + 8, box[2], box[3] + 8), 40,
                            fill=tuple(max(0, int(c * 0.78)) for c in fill[:3]))
        d.rounded_rectangle(box, 40, fill=fill)
        bc = gold if last else th["options"][i % 4]
        bb = (box[0] + 20, box[1] + 22, box[0] + 250, box[3] - 22)
        d.rounded_rectangle(bb, 32, fill=bc)
        d.rounded_rectangle((bb[0] + 8, bb[1] + 6, bb[2] - 8, bb[1] + (bb[3] - bb[1]) * 0.4), 20,
                            fill=(255, 255, 255, 45))
        d.text(((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2 + 4), r["rango"], font=tfont(80),
               fill=th["text_light"], anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0, 90))
        f = tfont(76)
        while d.textlength(r["nombre"].upper(), font=f) > 470 and f.size > 40:
            f = tfont(f.size - 4)
        d.text((box[0] + 285, (box[1] + box[3]) / 2 + 4), r["nombre"].upper(), font=f,
               fill=th["text_dark"], anchor="lm")
        im = _STATE["rimgs"].get(r["imagen"])
        if im is not None:
            bob = 8 * math.sin(lt * 4 + i)
            im2 = im.rotate(8 * math.sin(lt * 3 + i), resample=Image.BICUBIC, expand=True)
            layer.alpha_composite(im2, (int(box[2] - 100 - im2.width / 2), int((box[1] + box[3]) / 2 - im2.height / 2 + bob)))
    # confeti al llegar a la leyenda
    rl = lt - times[-1]
    if 0 <= rl < 2.5:
        cols = th["options"] + [th["accent"], gold]
        yy = y0 + (n - 1) * (h + gap) + h / 2
        for vx, vy, ci, s, ph in _STATE["confetti"]:
            x = 540 + vx * 900 * rl
            y = yy + vy * 1300 * rl + 1400 * rl * rl
            ang = ph + rl * 8
            dx, dy = math.cos(ang) * s, math.sin(ang) * s * 0.5
            al = 1 - max(0, (rl - 1.6) / 0.9)
            d.polygon([(x - dx, y - dy), (x + dy, y - dx), (x + dx, y + dy), (x - dy, y + dx)],
                      fill=with_alpha(cols[ci % len(cols)], al))


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
        cab = q.get("cabecera", q.get("etiqueta", "PREGUNTA EXTRA"))
        _pill(d, 540, yh, cab, 48, th["accent2"], th["text_light"])
        wtxt = d.textlength(cab, font=tfont(48))
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
    jt = sc.get("joke_t")
    if jt is not None and lt >= jt:
        # el texto de la tarjeta pasa a ser el chiste, con un pequeño rebote
        jp = ease_out_back((lt - jt) / 0.35)
        f, lines, lh = fit(d, q.get("comentario", q.get("chiste")), 820, CARD_H - 90, int(78 * (0.85 + 0.15 * jp)), 34, 1.08)
        draw_lines(d, lines, f, lh, 540, y + CARD_H / 2 + 6, th["accent2"])
        sprite = _STATE.get("decor", {}).get("calabaza_s")
        if sprite is not None:
            layer.alpha_composite(sprite, (int(OPT_X1 - 70), int(y - 40 + 6 * math.sin(lt * 8))))
    else:
        f, lines, lh = fit(d, q["pregunta"], 840, CARD_H - 70, 78, 40)
        draw_lines(d, lines, f, lh, 540, y + CARD_H / 2 + (22 if q.get("pegatina") else 0), th["text_dark"])
    if q.get("pegatina") and lt > 0.35:
        sp = ease_out_back((lt - 0.35) / 0.45)
        txt = q["pegatina"]
        fs = tfont(44)
        tw = d.textlength(txt, font=fs)
        st = Image.new("RGBA", (int(tw + 90), 110), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        sd.rounded_rectangle((6, 12, st.width - 6, st.height - 4), 30, fill=(0, 0, 0, 80))
        sd.rounded_rectangle((0, 0, st.width - 8, st.height - 14), 30, fill=(230, 30, 50),
                             outline=(255, 255, 255), width=6)
        sd.text(((st.width - 8) / 2, (st.height - 14) / 2 + 2), txt, font=fs, fill=(255, 255, 255), anchor="mm")
        k = max(0.05, sp * (1 + 0.04 * math.sin(lt * 7)))
        st = st.resize((max(2, int(st.width * k)), max(2, int(st.height * k))), Image.BILINEAR)
        st = st.rotate(-3, resample=Image.BICUBIC, expand=True)
        layer.alpha_composite(st, (int(540 - st.width / 2), int(y - st.height / 2 + 6)))

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
            img2 = im.resize((w_, h_), Image.BILINEAR)
            if th.get("formas") == "mascotas":
                img2 = _polaroid(img2.resize((int(w_ * 0.76), int(h_ * 0.76)), Image.BILINEAR), th)
            img2 = img2.rotate(6 * math.sin(lt * 1.7), resample=Image.BICUBIC, expand=True)
            if fade < 1:
                a_ = img2.getchannel("A").point(lambda v: int(v * fade))
                img2.putalpha(a_)
            cx_, cy_ = IMG_C[0], IMG_C[1] + 10 * math.sin(lt * 2.2) + (14 if th.get("formas") == "mascotas" else 0)
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
        if th.get("formas") == "mascotas" and rlt < 2.4:
            # lluvia de huellas, huesos y corazones que sale del cartel
            sp_ = _STATE["decor"]["lluvia"]
            for j, (vx, vy, ci, sz, ph) in enumerate(_STATE["confetti"][:26]):
                im_ = sp_[j % len(sp_)]
                hx = 540 + vx * 620 * rlt + 20 * math.sin(rlt * 4 + ph)
                hy = 840 + vy * 600 * rlt + 1300 * rlt * rlt
                al = 1 - max(0, (rlt - 1.6) / 0.8)
                im2 = im_.rotate(math.degrees(ph + rlt * 3 * (1 if j % 2 else -1)), resample=Image.BICUBIC)
                if al < 1:
                    im2.putalpha(im2.getchannel("A").point(lambda v, a_=al: int(v * a_)))
                layer.alpha_composite(im2, (int(hx - im2.width / 2), int(hy - im2.height / 2)))
            _pill(d, 540, 840, sc.get("end_pill") or "¡ESCRÍBELO EN COMENTARIOS!", int(max(10, 52 * pp * pulse)),
                  th["accent2"], th["text_light"])  # el cartel queda por encima de la lluvia
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

    # pegatina "pique" junto al cronómetro durante la cuenta atrás (solo texto, sin voz)
    if q.get("pique") and cs <= lt < sc["reveal"]:
        pp = ease_out_back((lt - cs - 0.6) / 0.35)
        if pp > 0:
            lines_ = q["pique"].upper().split("|")
            fs = tfont(46)
            tw = max(d.textlength(l_, font=fs) for l_ in lines_)
            st = Image.new("RGBA", (int(tw + 60), int(56 * len(lines_) + 50)), (0, 0, 0, 0))
            sd = ImageDraw.Draw(st)
            sd.rounded_rectangle((6, 12, st.width - 2, st.height - 2), 26, fill=(0, 0, 0, 80))
            sd.rounded_rectangle((0, 0, st.width - 8, st.height - 12), 26, fill=th["accent"],
                                 outline=th["text_dark"], width=5)
            for li, l_ in enumerate(lines_):
                sd.text(((st.width - 8) / 2, 25 + 28 + li * 56), l_, font=fs, fill=th["text_dark"], anchor="mm")
            k_ = max(0.05, pp * (1 + 0.05 * math.sin(lt * 8)))
            st = st.resize((max(2, int(st.width * k_)), max(2, int(st.height * k_))), Image.BILINEAR)
            st = st.rotate(8 + 3 * math.sin(lt * 5), resample=Image.BICUBIC, expand=True)
            layer.alpha_composite(st, (int(845 - st.width / 2), int(835 - st.height / 2)))

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
            {"intro": _draw_intro, "question": _draw_question, "rangos": _draw_rangos, "outro": _draw_outro}[sc["kind"]](layer, sc, lt)
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

"""Formato "NIVELES": cada ronda es un nivel con su color y una mecánica distinta.

Gancho → (cartel de nivel + prueba) x5 → nivel IMPOSIBLE (sin respuesta) → cierre.
Mecánicas: secuencia, busca (encuentra el diferente), logica, memoria, acertijo, reloj.
Reutiliza la voz, los efectos, la música y la exportación de render.py.
"""

import math
import os
import random
import subprocess
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import themes
from .render import (FPS, USUARIO, USER_Y, W, H, build_audio, ease_in, ease_out, ease_out_back, fit,
                     font, tfont)

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
LETTERS = "ABCD"
COUNTDOWN = 5
WHITE = (255, 255, 255)
GREEN = (22, 196, 98)
GREEN_D = (10, 110, 55)
RED = (239, 55, 70)
YEL = (255, 212, 0)

# top, bottom, color principal, color oscuro (texto)
LEVELS = [
    ((88, 226, 140), (18, 140, 72), (24, 178, 92), (8, 82, 42)),       # 1 verde
    ((255, 214, 70), (235, 150, 0), (240, 170, 0), (120, 70, 0)),      # 2 amarillo
    ((255, 156, 80), (230, 82, 14), (245, 110, 30), (122, 40, 6)),     # 3 naranja
    ((252, 110, 120), (196, 24, 52), (228, 48, 72), (110, 10, 28)),    # 4 rojo
    ((170, 140, 255), (102, 44, 214), (128, 76, 245), (50, 18, 120)),  # 5 morado
    ((70, 12, 26), (8, 3, 10), (239, 55, 70), (30, 6, 12)),            # imposible
]

# Gama alternativa (vídeo nº2): turquesa, azul, fucsia, lima, carmesí e imposible negro/verde tóxico.
# Se elige con "colores": "B" en el JSON para que cada vídeo se vea distinto.
LEVELS_B = [
    ((90, 232, 222), (0, 138, 150), (0, 182, 188), (0, 66, 76)),        # 1 turquesa
    ((120, 176, 255), (30, 66, 210), (52, 112, 242), (14, 32, 110)),    # 2 azul
    ((255, 124, 204), (196, 18, 128), (230, 50, 160), (98, 6, 60)),     # 3 fucsia
    ((196, 240, 70), (86, 164, 0), (128, 198, 20), (38, 76, 0)),        # 4 lima
    ((255, 96, 96), (160, 0, 26), (218, 28, 48), (86, 0, 14)),          # 5 carmesí
    ((12, 44, 26), (2, 8, 5), (60, 240, 120), (6, 26, 14)),             # imposible (verde tóxico)
]
PALETAS = {"A": list(LEVELS), "B": LEVELS_B}

# posiciones de los elementos de cada mecánica
LAYOUT = {
    "secuencia": {"card": (290, 520), "vis": 770, "timer": (540, 1045), "opts": ("grid", 1140)},
    "busca": {"card": (290, 470), "vis": 860, "timer": (540, 1305), "opts": ("rows", 520)},
    "logica": {"card": (290, 600), "vis": 770, "timer": (540, 1040), "opts": ("grid", 1140)},
    "memoria": {"card": (290, 470), "vis": 700, "timer": (540, 1045), "opts": ("grid", 1140)},
    "acertijo": {"card": (290, 620), "vis": 775, "timer": (540, 955), "opts": ("list", 1035)},
    "reloj": {"card": (290, 510), "vis": 770, "timer": (540, 1050), "opts": ("grid", 1140)},
    # minijuegos (niveles_02)
    "fugitivo": {"card": (290, 540), "vis": 810, "timer": (540, 1050), "opts": ("grid", 1140)},
    "rojo": {"card": (290, 540), "vis": 820, "timer": (540, 1050), "opts": ("grid", 1140)},
    "memoria6": {"card": (290, 540), "vis": 800, "timer": (540, 1080), "opts": ("grid", 1160)},
    "infiltrado": {"card": (290, 470), "vis": 865, "timer": (960, 865), "opts": ("grid", 1250)},
    "ilusion": {"card": (290, 540), "vis": 800, "timer": (540, 1050), "opts": ("grid", 1140)},
    "pixel": {"card": (290, 470), "vis": 860, "timer": (540, 1290), "opts": ("grid", 1400)},
}
NUEVOS = ("fugitivo", "rojo", "memoria6", "infiltrado", "ilusion", "pixel")
ROJO_COLS = {"V": (34, 200, 84), "R": (239, 40, 55), "A": (40, 120, 255), "M": (255, 205, 0),
             "Z": (150, 80, 240), "N": (255, 135, 0)}
NODES_Y = 200
NODES_X = [150 + i * 156 for i in range(6)]


# ------------------------------------------------------------------ línea de tiempo

def _countdown_events(ev, at, n=COUNTDOWN, riser=True):
    if riser:
        ev.append(("fx", "riser", at))
    ev.append(("music_boost", at, at + n))
    for s in range(n):
        ts = at + s
        ev.append(("fx", "heart", ts))
        ev.append(("fx", "tick_high" if s >= n - 2 else "tick", ts))
        ev.append(("fx", "tock", ts + 0.5))
        if s >= n - 2:
            ev += [("fx", "tick_high", ts + 0.25), ("fx", "tick_high", ts + 0.75)]


def build_timeline(c, voice):
    scenes, ev = [], []
    rondas = c["rondas"]

    # GANCHO: voz desde el fotograma 0 y escalera de niveles que se enciende
    sig, d = voice.say(c["gancho"]["voz"])
    ev.append(("voice", sig, 0.05))
    dur = max(3.0, d + 0.45)
    span = min(d, 3.2) - 0.35
    lights = [0.2 + i * span / 5 for i in range(6)]
    for i, tl in enumerate(lights):
        ev.append(("fx", "pop" if i < 5 else "buzz", tl))
    ev.append(("fx", "whoosh", dur - 0.25))
    scenes.append({"kind": "hook", "start": 0.0, "dur": dur, "lights": lights, "lv": -1})
    t = dur

    for k, r in enumerate(rondas):
        extra = bool(r.get("extra"))
        lay = LAYOUT[r["tipo"]]
        if r["tipo"] in NUEVOS:
            t = _ronda_nueva(r, k, extra, lay, voice, ev, scenes, t)
            continue
        # cartel de nivel
        sig, d = voice.say(r["anuncio"])
        cdur = max(1.6, 0.25 + d + 0.15)
        ev += [("fx", "whoosh", t), ("voice", sig, t + 0.25)]
        ev += [("fx", "heart", t + 0.3), ("fx", "heart", t + 0.95), ("fx", "buzz", t + 0.3)] if extra \
            else [("fx", "pop", t + 0.4), ("fx", "chime", t + 0.55)]
        scenes.append({"kind": "card", "start": t, "dur": cdur, "k": k, "r": r, "lv": k})
        t += cdur

        # prueba
        st, loc = t, 0.3
        sc = {"kind": "q", "start": st, "k": k, "r": r, "lv": k, "lay": lay, "extra": extra}
        ev.append(("fx", "whoosh", st))
        if r["tipo"] == "memoria":
            sig, d = voice.say(r["memoriza_voz"])
            ev.append(("voice", sig, st + loc))
            sc["tiles_t"] = loc
            m0 = loc + 0.6
            for i in range(len(r["numeros"])):
                ev.append(("fx", "pop", st + loc + 0.08 * i))
            _countdown_events(ev, st + m0, riser=False)
            sc["memo"] = (m0, m0 + COUNTDOWN)
            loc = m0 + COUNTDOWN
            ev.append(("fx", "whoosh", st + loc))
            loc += 0.45
        sig, d = voice.say(r.get("voz", r["pregunta"]))
        sc["q_t"] = loc
        ev.append(("voice", sig, st + loc))
        if r["tipo"] == "secuencia":
            sc["tiles_t"] = loc
            for i in range(len(r["serie"]) + 1):
                ev.append(("fx", "pop", st + loc + 0.15 + 0.16 * i))
        loc += max(0.5, d - 0.35)
        opt_times = []
        for _ in r["opciones"]:
            opt_times.append(loc)
            ev.append(("fx", "pop", st + loc))
            loc += 0.16
        cd = loc + 0.15
        _countdown_events(ev, st + cd)
        rv = cd + COUNTDOWN
        sig, dv = voice.say(r["respuesta_voz"])
        if extra:
            ev += [("fx", "buzz", st + rv), ("voice", sig, st + rv + 0.35)]
            rdur = max(2.6, 0.35 + dv + 0.5)
            stamp = None
        else:
            ev += [("fx", "buzz", st + rv), ("fx", "correct", st + rv + 0.15), ("voice", sig, st + rv + 0.4)]
            stamp = rv + 0.4 + min(dv, 1.2)
            ev += [("fx", "pop", st + stamp), ("fx", "chime", st + stamp + 0.05)]
            rdur = max(0.4 + dv + 0.2, stamp - rv + 0.95)
        sc.update({"opt_times": opt_times, "cd": cd, "reveal": rv, "stamp": stamp,
                   "correct": LETTERS.index(r["correcta"]), "dur": rv + rdur})
        scenes.append(sc)
        t += sc["dur"]

    # cierre
    sig, d = voice.say(c["cierre_voz"])
    shout_at = 0.35 + d + 0.1
    sig2, d2 = voice.say("¡Sígueme para más!", shout=True)
    dur = max(3.6, shout_at + d2 + 1.0)
    ev += [("fx", "whoosh", t), ("voice", sig, t + 0.35), ("voice", sig2, t + shout_at),
           ("fx", "applause", t + shout_at)]
    scenes.append({"kind": "outro", "start": t, "dur": dur, "shout_at": shout_at, "lv": 6})
    t += dur
    return scenes, ev, t


def _ronda_nueva(r, k, extra, lay, voice, ev, scenes, t):
    """Minijuegos rápidos: cartel corto → estímulo → pregunta → cuenta atrás corta → respuesta."""
    sig, d = voice.say(r["anuncio"])
    cdur = max(1.3, 0.2 + d + 0.1)
    ev += [("fx", "whoosh", t), ("voice", sig, t + 0.2)]
    ev += [("fx", "heart", t + 0.3), ("fx", "heart", t + 0.95), ("fx", "buzz", t + 0.3)] if extra \
        else [("fx", "pop", t + 0.35), ("fx", "chime", t + 0.5)]
    scenes.append({"kind": "card", "start": t, "dur": cdur, "k": k, "r": r, "lv": k})
    t += cdur
    st = t
    n = r.get("cuenta", COUNTDOWN)
    sc = {"kind": "q", "start": st, "k": k, "r": r, "lv": k, "lay": lay, "extra": extra, "n": n}
    ev.append(("fx", "whoosh", st))
    tipo = r["tipo"]
    loc = 0.25
    if tipo == "fugitivo":
        rit = r["ritmo"]
        for i in range(len(r["numeros"])):
            ev.append(("fx", "tick_high" if i == 0 else "tick", st + loc + i * rit))
        sc["stim"] = (loc, loc + len(r["numeros"]) * rit)
        loc = sc["stim"][1] + 0.2
    elif tipo == "rojo":
        rit = r["ritmo"]
        for i, p in enumerate(r["pasos"]):
            ev.append(("fx", "buzz" if "R" in p else "pop", st + loc + i * rit))
        sc["stim"] = (loc, loc + len(r["pasos"]) * rit)
        loc = sc["stim"][1] + 0.2
    elif tipo == "memoria6":
        for i in range(6):
            ev.append(("fx", "pop", st + loc + 0.06 * i))
        m0 = loc + 0.45
        _countdown_events(ev, st + m0, 3, riser=False)
        sc["memo"] = (m0, m0 + 3)
        ev += [("fx", "whoosh", st + m0 + 3), ("fx", "pop", st + m0 + 3.5)]
        sc["stim"] = (loc, m0 + 3.5)
        loc = m0 + 3.9
    sc["q_t"] = loc
    sig, d = voice.say(r.get("voz", r["pregunta"]))
    ev.append(("voice", sig, st + loc))
    loc += max(0.5, d - 0.35)
    opt_times = []
    for _ in r["opciones"]:
        opt_times.append(loc)
        ev.append(("fx", "pop", st + loc))
        loc += 0.14
    if tipo == "pixel":
        loc = sc["q_t"] + d + 0.1
    cd = loc + 0.1
    if tipo == "infiltrado":
        ev.append(("fx", "whoosh", st + cd - 0.15))
    _countdown_events(ev, st + cd, n)
    rv = cd + n
    sig, dv = voice.say(r["respuesta_voz"])
    if extra:
        ev += [("fx", "chime", st + rv), ("fx", "applause", st + rv + 0.1), ("voice", sig, st + rv + 0.6)]
        rdur = max(2.6, 0.6 + dv + 0.6)
        stp = None
    else:
        ev += [("fx", "buzz", st + rv), ("fx", "correct", st + rv + 0.12), ("voice", sig, st + rv + 0.35)]
        stp = rv + 0.35 + min(dv, 1.0)
        ev += [("fx", "pop", st + stp), ("fx", "chime", st + stp + 0.05)]
        rdur = max(0.35 + dv + 0.15, stp - rv + 0.8)
    sc.update({"opt_times": opt_times, "cd": cd, "reveal": rv, "stamp": stp,
               "correct": LETTERS.index(r["correcta"]), "dur": rv + rdur})
    scenes.append(sc)
    return t + sc["dur"]


# ------------------------------------------------------------------ utilidades de dibujo

_S = {}


def _sprite(path, size):
    key = (path, size)
    if key not in _S["spr"]:
        im = Image.open(os.path.join(ASSETS, path)).convert("RGBA")
        _S["spr"][key] = im.resize((size, size), Image.LANCZOS)
    return _S["spr"][key]


def paste_c(img, spr, cx, cy, scale=1.0, alpha=1.0, angle=0.0):
    if scale <= 0.02 or alpha <= 0.01:
        return
    s = spr
    if scale != 1.0:
        s = s.resize((max(1, int(s.width * scale)), max(1, int(s.height * scale))), Image.LANCZOS)
    if angle:
        s = s.rotate(angle, resample=Image.BICUBIC, expand=True)
    if alpha < 1.0:
        s = s.copy()
        s.putalpha(s.getchannel("A").point(lambda v: int(v * alpha)))
    img.paste(s, (int(cx - s.width / 2), int(cy - s.height / 2)), s)


def mix(c1, c2, k):
    return tuple(int(a + (b - a) * k) for a, b in zip(c1, c2))


def lvl(k):
    return LEVELS[min(k, 5)]


def rr(d, box, r, fill, outline=None, width=0):
    d.rounded_rectangle([int(v) for v in box], int(r), fill=fill, outline=outline, width=width)


def shadow(d, box, r, off=12, a=60):
    x0, y0, x1, y1 = box
    rr(d, (x0 + 4, y0 + off, x1 + 4, y1 + off), r, (0, 0, 0, a))


def text(d, xy, s, f, fill, stroke=0, sfill=None, sh=0):
    if sh:
        d.text((xy[0], xy[1] + sh), s, font=f, fill=(0, 0, 0, 70), anchor="mm",
               stroke_width=stroke, stroke_fill=(0, 0, 0, 70))
    d.text(xy, s, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=sfill)


def pill(d, cx, cy, s, size, bg, fg, pad=(34, 16), kind="titulo", outline=None):
    f = tfont(size) if kind == "titulo" else font(size)
    w = d.textlength(s, font=f)
    box = (cx - w / 2 - pad[0], cy - size / 2 - pad[1], cx + w / 2 + pad[0], cy + size / 2 + pad[1])
    shadow(d, box, (box[3] - box[1]) / 2, 8, 50)
    rr(d, box, (box[3] - box[1]) / 2, bg, outline, 5 if outline else 0)
    d.text((cx, cy + (2 if kind == "titulo" else 0)), s, font=f, fill=fg, anchor="mm")
    return box


def check(d, cx, cy, s, color, width=9):
    d.line([(cx - s * 0.45, cy), (cx - s * 0.1, cy + s * 0.35), (cx + s * 0.5, cy - s * 0.35)],
           fill=color, width=width, joint="curve")


def pop(lt, t0, dur=0.35):
    return ease_out_back((lt - t0) / dur) if lt >= t0 else 0.0


# ------------------------------------------------------------------ fondo

def _gradient(top, bot):
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(-1, 1, W)[None, :]
    k = np.clip(y * 0.85 + x * 0.08 + 0.04, 0, 1)
    arr = np.zeros((H, W, 3))
    for ch in range(3):
        arr[..., ch] = top[ch] + (bot[ch] - top[ch]) * k
    # brillo suave arriba
    glow = np.exp(-(((x * 0.9) ** 2) + ((y - 0.18) / 0.35) ** 2)) * 26
    arr += glow[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def _init(state):
    _S.clear()
    _S.update(state)
    LEVELS[:] = PALETAS[state["c"].get("colores", "A")]
    _S["spr"] = {}
    h = state["tono"]
    dark_top, dark_bot = themes._hsv(h, 0.72, 0.36), themes._hsv(h + 12, 0.9, 0.11)
    _S["bg"] = {-1: _gradient(dark_top, dark_bot), 6: _gradient(dark_top, dark_bot)}
    for k, L in enumerate(LEVELS):
        _S["bg"][k] = _gradient(L[0], L[1])
    _S["dark"] = (dark_top, dark_bot)
    blob = Image.new("L", (640, 640), 0)
    ImageDraw.Draw(blob).ellipse((120, 120, 520, 520), fill=255)
    blob = blob.filter(ImageFilter.GaussianBlur(70))
    spr = Image.new("RGBA", blob.size, (255, 255, 255, 0))
    spr.putalpha(blob.point(lambda v: int(v * 0.16)))
    _S["blob"] = spr
    rnd = random.Random(11)
    _S["shapes"] = [(rnd.random() * W, rnd.random() * H, rnd.uniform(18, 46), rnd.choice("ocsp"),
                     rnd.uniform(0.15, 0.5), rnd.random() * 6.28) for _ in range(16)]
    # viñeta roja para el final de la cuenta atrás
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    _S["vig"] = Image.fromarray((np.clip((dist - 0.75) / 0.6, 0, 1) * 200).astype(np.uint8), "L")
    _S["logo"] = Image.open(os.path.join(ASSETS, "logo.png")).convert("RGBA")
    _S["pix"] = {}
    for r in state["c"]["rondas"]:
        if r.get("foto"):
            _S["foto"] = Image.open(os.path.join(ASSETS, r["foto"])).convert("RGB").resize((620, 620), Image.LANCZOS)
        if r["tipo"] == "rojo":
            rp = random.Random(42)
            pos = []
            for p in r["pasos"]:
                pos.append([(rp.uniform(190, 890), rp.uniform(620, 1020), rp.uniform(62, 90)) for _ in p])
            _S["rojo_pos"] = pos
    # confeti fijo
    rc = random.Random(5)
    cols = [YEL, (0, 222, 205), (255, 64, 160), WHITE, (138, 58, 255), GREEN]
    _S["confeti"] = [(rc.uniform(-1, 1), rc.uniform(-1.4, -0.3), rc.choice(cols), rc.uniform(10, 22),
                      rc.uniform(0, 6.28)) for _ in range(40)]


def _bg_frame(lv, t):
    img = _S["bg"][lv].copy()
    for i, (bx, by, sp) in enumerate([(180, 420, 0.21), (900, 980, 0.17), (360, 1500, 0.13)]):
        x = bx + math.sin(t * sp + i) * 90
        y = by + math.cos(t * sp * 1.3 + i * 2) * 70
        img.paste(_S["blob"], (int(x - 320), int(y - 320)), _S["blob"])
    d = ImageDraw.Draw(img, "RGBA")
    for (x0, y0, s, kind, sp, ph) in _S["shapes"]:
        y = (y0 - t * 40 * sp) % (H + 200) - 100
        x = x0 + math.sin(t * sp + ph) * 30
        a = (255, 255, 255, 38)
        ang = t * sp + ph
        if kind == "o":
            d.ellipse((x - s / 2, y - s / 2, x + s / 2, y + s / 2), outline=a, width=5)
        elif kind == "c":
            pts = [(x + s * 0.6 * math.cos(ang + j * math.pi / 2), y + s * 0.6 * math.sin(ang + j * math.pi / 2))
                   for j in range(4)]
            d.polygon(pts, outline=a, width=5)
        elif kind == "s":
            d.line((x - s / 2, y, x + s / 2, y), fill=a, width=6)
            d.line((x, y - s / 2, x, y + s / 2), fill=a, width=6)
        else:
            d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=a)
    return img


def background(sc, lt, t):
    lv = sc["lv"]
    img = _bg_frame(lv, t)
    if sc["kind"] == "card" and lt < 0.5:
        prev = -1 if sc["k"] == 0 else sc["k"] - 1
        old = _bg_frame(prev, t)
        r = ease_in(lt / 0.5) * 1400 + 10
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).ellipse((540 - r, 800 - r, 540 + r, 800 + r), fill=255)
        img = Image.composite(img, old, mask)
    if sc["kind"] == "outro" and lt < 0.5:
        old = _bg_frame(5, t)
        r = ease_in(lt / 0.5) * 1400 + 10
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).ellipse((540 - r, 800 - r, 540 + r, 800 + r), fill=255)
        img = Image.composite(img, old, mask)
    return img


# ------------------------------------------------------------------ piezas comunes

def path_bar(img, d, cur, done, lt, fill_k=1.0):
    """Barra de niveles arriba: `done` niveles superados; `cur` el actual."""
    y = NODES_Y
    d.line((NODES_X[0], y, NODES_X[-1], y), fill=(255, 255, 255, 80), width=10)
    if done > 0:
        xe = NODES_X[min(done - 1, 5)] + (NODES_X[min(done, 5)] - NODES_X[min(done - 1, 5)]) * fill_k
        d.line((NODES_X[0], y, xe, y), fill=WHITE, width=10)
    for i, x in enumerate(NODES_X):
        col = lvl(i)[2]
        if i < done:
            r = 32
            rr(d, (x - r, y - r + 5, x + r, y + r + 5), r, (0, 0, 0, 50))
            d.ellipse((x - r, y - r, x + r, y + r), fill=col, outline=WHITE, width=5)
            check(d, x, y + 2, 30, WHITE, 8)
        elif i == cur:
            r = 42 + 3 * math.sin(lt * 6)
            d.ellipse((x - r - 12, y - r - 12, x + r + 12, y + r + 12), fill=(255, 255, 255, 60))
            d.ellipse((x - r, y - r, x + r, y + r), fill=WHITE, outline=col, width=8)
            if i == 5:
                paste_c(img, _sprite("imagenes/calavera_3d.png", 60), x, y)
            else:
                d.text((x, y + 3), str(i + 1), font=tfont(50), fill=lvl(i)[3], anchor="mm")
        else:
            r = 30
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 70), outline=(255, 255, 255, 150), width=4)
            if i == 5:
                paste_c(img, _sprite("imagenes/calavera_3d.png", 44), x, y, alpha=0.75)
            else:
                d.text((x, y + 3), str(i + 1), font=tfont(40), fill=WHITE, anchor="mm")


def q_card(img, d, sc, lt, txt, t0=0.0):
    k, r = sc["k"], sc["r"]
    L = lvl(k)
    y0, y1 = sc["lay"]["card"]
    a = pop(lt, t0, 0.4)
    if a <= 0:
        return
    cy = (y0 + y1) / 2
    hh = (y1 - y0) / 2 * (0.85 + 0.15 * a)
    box = (70, cy - hh, 1010, cy + hh)
    shadow(d, box, 44, 14, 60)
    rr(d, box, 44, WHITE)
    head = ("NIVEL IMPOSIBLE" if sc["extra"] else f"NIVEL {k + 1} · {r['nombre']}")
    d.text((540, box[1] + 42), head, font=tfont(36), fill=L[2] if not sc["extra"] else RED, anchor="mm")
    f, lines, lh = fit(d, txt, 850, (y1 - y0) - 110, 64, 34, 1.08)
    yy = box[1] + 70 + ((y1 - y0) - 90) / 2 - lh * len(lines) / 2 + lh / 2
    for ln in lines:
        d.text((540, yy), ln, font=f, fill=L[3] if not sc["extra"] else (30, 10, 20), anchor="mm")
        yy += lh


def timer(img, d, sc, lt):
    cx, cy = sc["lay"]["timer"]
    cd = sc["cd"]
    if lt < cd - 0.3 or lt > sc["reveal"] + 0.35:
        return
    a = pop(lt, cd - 0.3, 0.35)
    if lt > sc["reveal"]:
        a = 1 - ease_in((lt - sc["reveal"]) / 0.35)
    N = sc.get("n", COUNTDOWN)
    rem = max(0.0, cd + N - lt)
    n = min(N, int(math.ceil(rem))) if lt >= cd else N
    urgent = lt >= cd and rem <= 2
    col = RED if urgent else lvl(sc["k"])[2]
    beat = 1 + (0.08 * max(0, math.cos((lt - cd) * 2 * math.pi)) if urgent else 0)
    R = 66 * a * beat
    if R < 16:
        return
    d.ellipse((cx - R + 4, cy - R + 10, cx + R + 4, cy + R + 10), fill=(0, 0, 0, 60))
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=WHITE)
    frac = rem / N if lt >= cd else 1.0
    d.arc((cx - R + 7, cy - R + 7, cx + R - 7, cy + R - 7), -90, -90 + 360 * frac, fill=col, width=int(12 * a))
    if n > 0:
        d.text((cx, cy + 4), str(n), font=tfont(int(76 * a * beat)), fill=col if urgent else (30, 24, 40),
               anchor="mm")


def vignette(img, sc, lt):
    end = sc["cd"] + sc.get("n", COUNTDOWN)
    if end - 2.5 <= lt < end:
        k = (lt - (end - 2.5)) / 2.5
        beat = 0.5 + 0.5 * math.cos((lt - sc["cd"]) * 2 * math.pi * 2)
        alpha = (0.35 + 0.65 * k) * (0.6 + 0.4 * beat)
        m = _S["vig"].point(lambda v, a_=alpha: int(v * a_))
        img.paste((230, 20, 40), (0, 0), m)


def opt_boxes(sc):
    kind, y0 = sc["lay"]["opts"]
    if kind == "grid":
        cw, h, g = 460, 150, 20
        return [(70 + (i % 2) * (cw + g), y0 + (i // 2) * (h + g), 70 + (i % 2) * (cw + g) + cw,
                 y0 + (i // 2) * (h + g) + h) for i in range(4)]
    if kind == "list":
        h, g = 118, 14
        return [(70, y0 + i * (h + g), 1010, y0 + i * (h + g) + h) for i in range(4)]
    h, g = 150, 22  # filas de "busca"
    return [(70, y0 + i * (h + g), 1010, y0 + i * (h + g) + h) for i in range(4)]


def options(img, d, sc, lt):
    L = lvl(sc["k"])
    revealed = lt >= sc["reveal"] and not sc["extra"]
    rows = sc["lay"]["opts"][0] == "rows"
    for i, box in enumerate(opt_boxes(sc)):
        a = pop(lt, sc["opt_times"][i] - (0.9 if rows else 0), 0.35)
        if rows:  # en "busca" las filas aparecen con la pregunta
            a = pop(lt, 0.25 + 0.12 * i, 0.35)
        if a <= 0:
            continue
        x0, y0, x1, y1 = box
        dy = (1 - a) * 160
        good = revealed and i == sc["correct"]
        bad = revealed and not good
        s = 1.0 + (0.035 * math.sin((lt - sc["reveal"]) * 8) if good else 0)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + dy
        hw, hh = (x1 - x0) / 2 * s, (y1 - y0) / 2 * s
        b = (cx - hw, cy - hh, cx + hw, cy + hh)
        rad = 34
        if not bad:
            shadow(d, b, rad, 10, 55)
        fill = GREEN if good else ((255, 255, 255, 105) if bad else WHITE)
        rr(d, b, rad, fill, outline=WHITE if good else None, width=6 if good else 0)
        lc = (b[0] + 62, cy)
        circ = WHITE if good else ((255, 255, 255, 120) if bad else L[2])
        d.ellipse((lc[0] - 36, lc[1] - 36, lc[0] + 36, lc[1] + 36), fill=circ)
        d.text((lc[0], lc[1] + 3), LETTERS[i], font=tfont(44),
               fill=GREEN if good else ((120, 120, 130) if bad else WHITE), anchor="mm")
        tcol = WHITE if good else ((90, 90, 100, 150) if bad else L[3])
        if rows:
            row = sc["r"]["filas"][i]
            f = font(78)
            for j, ch in enumerate(row):
                d.text((b[0] + 155 + j * 77, cy + 4), ch, font=f, fill=tcol, anchor="mm")
            continue
        if good:
            check(d, b[2] - 52, cy, 40, WHITE, 10)
        tx0 = b[0] + 115
        tw = (b[2] - 40 - (60 if good else 0)) - tx0
        o = sc["r"]["opciones"][i]
        f, lines, lh = fit(d, o, tw, (b[3] - b[1]) - 22, 58 if sc["lay"]["opts"][0] == "grid" else 40, 26, 1.05)
        yy = cy - lh * len(lines) / 2 + lh / 2
        for ln in lines:
            d.text((tx0 + tw / 2, yy + 2), ln, font=f, fill=tcol, anchor="mm")
            yy += lh


def stamp(img, d, sc, lt):
    if sc["stamp"] is None or lt < sc["stamp"]:
        return
    lt2 = lt - sc["stamp"]
    k = sc["k"]
    key = ("stamp", k)
    if key not in _S["spr"]:
        L = lvl(k)
        s = Image.new("RGBA", (820, 200), (0, 0, 0, 0))
        sd = ImageDraw.Draw(s)
        rr(sd, (14, 24, 806, 186), 80, (0, 0, 0, 70))
        rr(sd, (6, 10, 798, 172), 80, WHITE, outline=GREEN, width=10)
        sd.ellipse((40, 36, 150, 146), fill=GREEN)
        check(sd, 95, 92, 56, WHITE, 12)
        sd.text((470, 94), f"¡NIVEL {k + 1} SUPERADO!", font=tfont(70), fill=GREEN_D, anchor="mm")
        _S["spr"][key] = s.rotate(6, resample=Image.BICUBIC, expand=True)
    a = ease_out(lt2 / 0.22)
    scale = 1.55 - 0.55 * a
    cy = sc["lay"]["vis"] if sc["r"]["tipo"] not in ("busca", "infiltrado") else 1305
    if sc["r"]["tipo"] in NUEVOS:
        cy = 1060
    paste_c(img, _S["spr"][key], 540, cy, scale * 0.95, alpha=min(1, a * 1.3))
    # confeti
    if lt2 < 1.6:
        for (vx, vy, col, sz, ph) in _S["confeti"]:
            x = 540 + vx * 620 * lt2
            y = cy + vy * 700 * lt2 + 900 * lt2 * lt2
            ang = ph + lt2 * 8
            pts = [(x + sz * math.cos(ang + j * math.pi / 2) * (1 if j % 2 else 0.5),
                    y + sz * math.sin(ang + j * math.pi / 2) * (1 if j % 2 else 0.5)) for j in range(4)]
            d.polygon(pts, fill=col + (int(255 * max(0, 1 - lt2 / 1.6)),))


def tile(d, cx, cy, w, h, s, bg, fg, size=84, flip=1.0, outline=None):
    ww = w * abs(flip)
    if ww < 3:
        return
    box = (cx - ww / 2, cy - h / 2, cx + ww / 2, cy + h / 2)
    shadow(d, box, 28, 10, 55)
    rr(d, box, 28, bg, outline=outline, width=6 if outline else 0)
    if abs(flip) > 0.35:
        d.text((cx, cy + 5), s, font=tfont(int(size * min(1, abs(flip) * 1.2))), fill=fg, anchor="mm")


# ------------------------------------------------------------------ mecánicas

def vis_secuencia(img, d, sc, lt):
    r, L = sc["r"], lvl(sc["k"])
    serie = r["serie"]
    n = len(serie) + 1
    w, g = 150, 24
    x0 = 540 - (n * w + (n - 1) * g) / 2 + w / 2
    cy = sc["lay"]["vis"]
    t0 = sc["tiles_t"] + 0.15
    rv = sc["reveal"]
    for i in range(n):
        a = pop(lt, t0 + 0.16 * i, 0.35)
        if a <= 0:
            continue
        cx = x0 + i * (w + g)
        yy = cy + (1 - a) * 120
        if i < len(serie):
            tile(d, cx, yy, w, 170, serie[i], WHITE, L[3], 84)
        else:
            if lt < rv:
                p = 1 + 0.05 * math.sin(lt * 7)
                tile(d, cx, yy, w * p, 170 * p, "?", L[3], WHITE, 96, outline=WHITE)
            else:
                fl = math.cos(min(1, (lt - rv) / 0.4) * math.pi)
                if fl > 0:
                    tile(d, cx, yy, w, 170, "?", L[3], WHITE, 96, flip=fl, outline=WHITE)
                else:
                    tile(d, cx, yy, w, 170, r["opciones"][sc["correct"]], GREEN, WHITE, 84, flip=fl,
                         outline=WHITE)
    if lt >= rv + 0.3 and r.get("salto"):
        a = pop(lt, rv + 0.3, 0.35)
        for i in range(n - 1):
            cx = x0 + i * (w + g) + (w + g) / 2
            pill(d, cx, cy - 120 - (1 - a) * 30, r["salto"], int(34 * max(a, 0.1)), YEL, (60, 40, 0), pad=(14, 8))


def vis_logica(img, d, sc, lt):
    cy = sc["lay"]["vis"]
    a = pop(lt, 0.2, 0.5)
    rv = sc["reveal"]
    if lt < rv + 0.3:
        bob = math.sin(lt * 2.4) * 14
        al = 1.0 if lt < rv else max(0, 1 - (lt - rv) / 0.3)
        paste_c(img, _sprite("imagenes/" + sc["r"].get("imagen", "cerebro_3d.png"), 250), 540, cy + bob,
                a, alpha=al)
        for j, (dx, dy, ph) in enumerate([(-190, -60, 0), (180, -90, 1.7), (205, 70, 3.1), (-170, 90, 4.4)]):
            s = 50 + 8 * math.sin(lt * 3 + ph)
            d.text((540 + dx, cy + dy + math.sin(lt * 2 + ph) * 10), "?", font=tfont(int(s * a)),
                   fill=(255, 255, 255, int(200 * al)), anchor="mm")
    if lt >= rv + 0.3 and sc["r"].get("explicacion"):
        b = pop(lt, rv + 0.3, 0.4)
        pill(d, 540, cy + (1 - b) * 60, sc["r"]["explicacion"], int(64 * max(b, 0.1)), WHITE, GREEN_D,
             pad=(40, 22))


def vis_memoria(img, d, sc, lt):
    r, L = sc["r"], lvl(sc["k"])
    nums = r["numeros"]
    n = len(nums)
    w, g = 132, 16
    x0 = 540 - (n * w + (n - 1) * g) / 2 + w / 2
    cy = sc["lay"]["vis"]
    m0, m1 = sc["memo"]
    rv = sc["reveal"]
    pos = r["posicion"] - 1
    for i in range(n):
        a = pop(lt, sc["tiles_t"] + 0.08 * i, 0.35)
        if a <= 0:
            continue
        cx = x0 + i * (w + g)
        yy = cy + (1 - a) * 120
        d.text((cx, yy - 118), f"{i + 1}ª", font=tfont(38), fill=(255, 255, 255, 220), anchor="mm")
        if lt < m1:
            tile(d, cx, yy, w, 170, nums[i], WHITE, L[3], 90)
        elif lt < rv:
            fl = math.cos(min(1, (lt - m1) / 0.35) * math.pi)
            if fl > 0:
                tile(d, cx, yy, w, 170, nums[i], WHITE, L[3], 90, flip=fl)
            else:
                tile(d, cx, yy, w, 170, "?", L[3], WHITE, 90, flip=fl, outline=WHITE)
        else:
            fl = math.cos(min(1, (lt - rv) / 0.4) * math.pi)
            good = i == pos
            lift = -26 * ease_out((lt - rv - 0.4) / 0.3) if good else 0
            if fl > 0:
                tile(d, cx, yy, w, 170, "?", L[3], WHITE, 90, flip=fl, outline=WHITE)
            else:
                tile(d, cx, yy + lift, w, 170, nums[i], GREEN if good else (255, 255, 255, 140),
                     WHITE if good else (110, 110, 120), 90, flip=fl, outline=WHITE if good else None)
    # barra de tiempo para memorizar
    if m0 - 0.3 <= lt < m1 + 0.3:
        a = pop(lt, m0 - 0.3, 0.3) if lt < m1 else 1 - ease_in((lt - m1) / 0.3)
        frac = max(0.0, min(1.0, (m1 - lt) / (m1 - m0)))
        bw = 760 * a
        by = cy + 140
        rr(d, (540 - bw / 2, by - 16, 540 + bw / 2, by + 16), 16, (0, 0, 0, 70))
        if frac > 0:
            rr(d, (540 - bw / 2, by - 16, 540 - bw / 2 + bw * frac, by + 16), 16, WHITE if frac > 0.4 else YEL)
        if a > 0.5:
            pill(d, 540, by + 92, "¡NADA DE CAPTURAS!", 40, L[3], WHITE, pad=(26, 12))


def _rope(d, y, x0, x1, ph):
    pts = [(x, y + math.sin(x / 55 + ph) * 9) for x in range(int(x0), int(x1) + 1, 12)]
    d.line(pts, fill=(92, 55, 26), width=34, joint="curve")
    d.line(pts, fill=(196, 140, 78), width=24, joint="curve")
    for x in range(int(x0) + 10, int(x1) - 10, 26):
        yy = y + math.sin(x / 55 + ph) * 9
        d.line((x - 8, yy - 9, x + 8, yy + 9), fill=(140, 92, 46), width=5)


def vis_acertijo(img, d, sc, lt):
    cy = sc["lay"]["vis"]
    rv = sc["reveal"]
    a = pop(lt, 0.25, 0.45)
    if a <= 0:
        return
    if sc["r"].get("imagen"):
        if lt < rv + 0.3:
            al = 1.0 if lt < rv else max(0, 1 - (lt - rv) / 0.3)
            paste_c(img, _sprite("imagenes/" + sc["r"]["imagen"], 190), 540, cy + math.sin(lt * 2.4) * 10,
                    a, alpha=al, angle=8 * math.sin(lt * 1.7))
            for dx in (-200, 200):
                d.text((540 + dx, cy + math.sin(lt * 2 + dx) * 10), "?", font=tfont(int(60 * a)),
                       fill=(255, 255, 255, int(200 * al)), anchor="mm")
        if lt >= rv + 0.3 and sc["r"].get("explicacion"):
            b = pop(lt, rv + 0.3, 0.4)
            pill(d, 540, cy, sc["r"]["explicacion"], int(56 * max(b, 0.1)), WHITE, GREEN_D, pad=(38, 20))
        return
    xr = 170 + (1 - a) * 400
    for j, yy in enumerate((cy - 60, cy + 55)):
        _rope(d, yy, xr, 840, j * 1.3)
        pill(d, 505, yy, "60 MIN", 32, WHITE, (90, 55, 26), pad=(16, 8))
    fl = 1 + 0.08 * math.sin(lt * 13) + 0.05 * math.sin(lt * 7.3)
    paste_c(img, _sprite("portada/fuego.png", 120), 925, cy - 5 + math.sin(lt * 3) * 6, fl * a)
    if lt >= rv + 0.3 and sc["r"].get("explicacion"):
        b = pop(lt, rv + 0.3, 0.4)
        pill(d, 540, cy, sc["r"]["explicacion"], int(60 * max(b, 0.1)), WHITE, GREEN_D, pad=(38, 20))


def vis_reloj(img, d, sc, lt):
    cy = sc["lay"]["vis"]
    a = pop(lt, 0.2, 0.5)
    if a <= 0:
        return
    hh, mm = sc["r"]["hora"]
    R = 200 * a
    shake = math.sin(lt * 40) * 6 if lt < 0.6 else 0
    cx = 540 + shake
    glow = 0.5 + 0.5 * math.sin(lt * 3)
    d.ellipse((cx - R - 30, cy - R - 30, cx + R + 30, cy + R + 30), fill=(239, 55, 70, int(40 + 50 * glow)))
    d.ellipse((cx - R + 6, cy - R + 14, cx + R + 6, cy + R + 14), fill=(0, 0, 0, 90))
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=WHITE, outline=(40, 12, 20), width=int(14 * a))
    for i in range(60):
        ang = math.radians(i * 6 - 90)
        big = i % 5 == 0
        r0 = R * (0.82 if big else 0.88)
        d.line((cx + r0 * math.cos(ang), cy + r0 * math.sin(ang), cx + R * 0.93 * math.cos(ang),
                cy + R * 0.93 * math.sin(ang)), fill=(40, 12, 20), width=6 if big else 2)
    for num, ang in ((12, -90), (3, 0), (6, 90), (9, 180)):
        rad = math.radians(ang)
        d.text((cx + R * 0.66 * math.cos(rad), cy + R * 0.66 * math.sin(rad) + 3), str(num),
               font=tfont(int(54 * a)), fill=(40, 12, 20), anchor="mm")
    am = math.radians(mm * 6 - 90)
    ah = math.radians((hh % 12) * 30 + mm * 0.5 - 90)
    d.line((cx, cy, cx + R * 0.48 * math.cos(ah), cy + R * 0.48 * math.sin(ah)), fill=(40, 12, 20),
           width=int(18 * a))
    d.line((cx, cy, cx + R * 0.78 * math.cos(am), cy + R * 0.78 * math.sin(am)), fill=RED, width=int(11 * a))
    d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=(40, 12, 20))
    paste_c(img, _sprite("imagenes/calavera_3d.png", 110), cx + R * 0.95, cy - R * 0.85,
            a * (1 + 0.05 * math.sin(lt * 5)), angle=12)


def vis_busca(img, d, sc, lt):
    rv = sc["reveal"]
    if lt < rv + 0.2:
        return
    i = sc["correct"]
    row = sc["r"]["filas"][i]
    j = next(n for n, ch in enumerate(row) if ch != row[0]) if len(set(row)) > 1 else 0
    box = opt_boxes(sc)[i]
    x = box[0] + 155 + j * 77
    y = (box[1] + box[3]) / 2 + 4
    a = pop(lt, rv + 0.2, 0.35)
    R = 56 * a * (1 + 0.06 * math.sin(lt * 9))
    d.ellipse((x - R, y - R, x + R, y + R), outline=YEL, width=9)


def _pixelada(b):
    if b not in _S["pix"]:
        f = _S["foto"]
        if b <= 1:
            _S["pix"][b] = f
        else:
            sm = f.resize((max(1, 620 // b), max(1, 620 // b)), Image.BILINEAR)
            _S["pix"][b] = sm.resize((620, 620), Image.NEAREST)
    return _S["pix"][b]


def _marco_foto(img, d, im, cx, cy, glow_col, lt, scale=1.0, glitch=0):
    s = int(620 * scale)
    if s < 10:
        return
    g = 0.5 + 0.5 * math.sin(lt * 6)
    for w, a in ((40, 40), (24, 70), (12, 130)):
        rr(d, (cx - s / 2 - w, cy - s / 2 - w, cx + s / 2 + w, cy + s / 2 + w), 46 + w,
           glow_col + (int(a * (0.6 + 0.4 * g)),))
    pic = im if s == 620 else im.resize((s, s), Image.BILINEAR)
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, s - 1, s - 1), 40, fill=255)
    if glitch:
        r_, g_, b_ = pic.split()
        pic = Image.merge("RGB", (r_.transform(pic.size, Image.AFFINE, (1, 0, glitch, 0, 1, 0)), g_,
                                  b_.transform(pic.size, Image.AFFINE, (1, 0, -glitch, 0, 1, 0))))
    img.paste(pic, (int(cx - s / 2), int(cy - s / 2)), m)
    rr(d, (cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2), 40, None, outline=WHITE, width=8)


def vis_fugitivo(img, d, sc, lt):
    r, L = sc["r"], lvl(sc["k"])
    s0, s1 = sc["stim"]
    cy = sc["lay"]["vis"]
    nums = r["numeros"]
    cols = [(255, 255, 255), (255, 220, 90), (120, 230, 255), (255, 150, 200), (190, 255, 140)]
    if s0 <= lt < s1:
        i = int((lt - s0) / r["ritmo"])
        q = ((lt - s0) % r["ritmo"]) / r["ritmo"]
        a = ease_out_back(min(1, q / 0.25))
        jx = (i * 37 % 7 - 3) * 22
        tile(d, 540 + jx, cy, 360 * a, 300 * a, nums[i], cols[i % len(cols)], L[3], int(210 * a))
        # contador de destellos
        for j in range(len(nums)):
            x = 540 + (j - (len(nums) - 1) / 2) * 34
            d.ellipse((x - 9, cy + 200 - 9, x + 9, cy + 200 + 9), fill=WHITE if j <= i else (255, 255, 255, 70))
    elif lt >= s1:
        rv = sc["reveal"]
        if lt < rv:
            p = 1 + 0.05 * math.sin(lt * 7)
            tile(d, 540, cy, 300 * p, 260 * p, "?", L[3], WHITE, 190, outline=WHITE)
        else:
            a = pop(lt, rv, 0.35)
            tile(d, 540, cy, 320, 270, nums[0], GREEN, WHITE, 190, outline=WHITE)
            pill(d, 700, cy - 130, "×2", int(64 * max(a, 0.1)), YEL, (60, 40, 0), pad=(22, 10))


def vis_rojo(img, d, sc, lt):
    r = sc["r"]
    s0, s1 = sc["stim"]
    cy = sc["lay"]["vis"]
    if s0 <= lt < s1:
        i = int((lt - s0) / r["ritmo"])
        q = ((lt - s0) % r["ritmo"]) / r["ritmo"]
        a = ease_out_back(min(1, q / 0.3)) * (1 if q < 0.85 else max(0, (1 - q) / 0.15))
        red = "R" in r["pasos"][i]
        if red:
            for w, al in ((50, 90), (90, 40)):
                d.rectangle((0, 0, W, H), outline=RED + (al,), width=w)
        for ch, (x, y, rad) in zip(r["pasos"][i], _S["rojo_pos"][i]):
            col = ROJO_COLS[ch]
            R = rad * a * (1.2 if ch == "R" else 1)
            if R < 2:
                continue
            d.ellipse((x - R + 5, y - R + 10, x + R + 5, y + R + 10), fill=(0, 0, 0, 60))
            d.ellipse((x - R, y - R, x + R, y + R), fill=col, outline=WHITE, width=6)
            d.ellipse((x - R * 0.55, y - R * 0.7, x + R * 0.1, y - R * 0.2), fill=(255, 255, 255, 70))
    elif lt >= s1:
        rv = sc["reveal"]
        if lt < rv:
            k = 1 + 0.06 * math.sin(lt * 7)
            text(d, (540, cy), "¿CUÁNTOS?", tfont(int(110 * k)), WHITE, 12, (20, 10, 40), sh=8)
        else:
            nv = sum(p.count("V") for p in r["pasos"])
            for j in range(nv):
                a = pop(lt, rv + 0.05 * j, 0.3)
                x = 540 + (j - (nv - 1) / 2) * 100
                R = 38 * a
                d.ellipse((x - R, cy - R, x + R, cy + R), fill=ROJO_COLS["V"], outline=WHITE, width=5)


def _obj_card(img, d, name, cx, cy, s=1.0, flip=1.0, good=False):
    w = 194 * s * abs(flip)
    h = 194 * s
    if w < 4:
        return
    box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    shadow(d, box, 34, 10, 60)
    rr(d, box, 34, GREEN if good else WHITE, outline=WHITE if good else None, width=6 if good else 0)
    if name and abs(flip) > 0.3:
        spr = _sprite("niveles2/%s.png" % name, int(148 * s))
        if flip != 1.0:
            spr = spr.resize((max(2, int(spr.width * abs(flip))), spr.height))
        paste_c(img, spr, cx, cy)


def vis_memoria6(img, d, sc, lt):
    r, L = sc["r"], lvl(sc["k"])
    cy = sc["lay"]["vis"]
    m0, m1 = sc["memo"]
    rv = sc["reveal"]
    slots = [(540 + (i % 3 - 1) * 250, cy - 112 + (i // 3) * 222) for i in range(6)]
    for i, (x, y) in enumerate(slots):
        a = pop(lt, 0.25 + 0.06 * i, 0.35)
        if a <= 0:
            continue
        if lt < m1:
            _obj_card(img, d, r["objetos"][i], x, y, a)
        elif lt < m1 + 0.5:
            fl = math.cos(min(1, (lt - m1) / 0.25) * math.pi)
            if fl > 0:
                _obj_card(img, d, r["objetos"][i], x, y, 1, fl)
            else:
                box = (x - 97, y - 97, x + 97, y + 97)
                rr(d, box, 34, L[3], outline=WHITE, width=6)
                d.text((x, y + 6), "?", font=tfont(110), fill=WHITE, anchor="mm")
        else:
            nm = r["orden2"][i]
            q = pop(lt, m1 + 0.5 + 0.05 * i, 0.3)
            if nm is None:
                if lt >= rv + 0.1:
                    _obj_card(img, d, r["falta"], x, y, pop(lt, rv + 0.1, 0.35), good=True)
                else:
                    box = (x - 97, y - 97, x + 97, y + 97)
                    rr(d, box, 34, (255, 255, 255, 50), outline=(255, 255, 255, 200), width=5)
                    d.text((x, y + 6), "?", font=tfont(int(110 * (1 + 0.06 * math.sin(lt * 7)))), fill=WHITE,
                           anchor="mm")
            else:
                _obj_card(img, d, nm, x, y, q)
    if m0 - 0.3 <= lt < m1 + 0.3:
        a = pop(lt, m0 - 0.3, 0.3) if lt < m1 else 1 - ease_in((lt - m1) / 0.3)
        frac = max(0.0, min(1.0, (m1 - lt) / (m1 - m0)))
        bw = 760 * a
        by = cy + 248
        rr(d, (540 - bw / 2, by - 16, 540 + bw / 2, by + 16), 16, (0, 0, 0, 70))
        if frac > 0:
            rr(d, (540 - bw / 2, by - 16, 540 - bw / 2 + bw * frac, by + 16), 16, WHITE if frac > 0.4 else YEL)


def vis_infiltrado(img, d, sc, lt):
    r = sc["r"]
    cd, rv = sc["cd"], sc["reveal"]
    nf, nc = r["filas"], r["columnas"]
    fr, fc = r["pos"]
    cy = sc["lay"]["vis"]
    step_y, step_x, size = 94, 118, 84
    y0 = cy - (nf - 1) / 2 * step_y
    x0 = 540 - (nc - 1) / 2 * step_x
    if lt < cd - 0.2:
        k = 1 + 0.07 * math.sin(lt * 8)
        text(d, (540, cy - 40), "¿PREPARADO?", tfont(int(100 * k)), WHITE, 12, (20, 10, 40), sh=8)
        text(d, (540, cy + 80), "40 CARAS · 5 SEGUNDOS", tfont(52), YEL, 8, (20, 10, 40))
        return
    for i in range(nf):
        y = y0 + i * step_y
        pill(d, x0 - 115, y, str(i + 1), 40, WHITE, lvl(sc["k"])[3], pad=(16, 6))
        for j in range(nc):
            a = pop(lt, cd - 0.2 + 0.012 * (i * nc + j), 0.25)
            odd = (i + 1, j + 1) == (fr, fc)
            nm = r["diferente"] if odd else r["figura"]
            al = 1.0
            if lt >= rv and not odd:
                al = max(0.25, 1 - (lt - rv) / 0.3)
            paste_c(img, _sprite("niveles2/%s.png" % nm, size), x0 + j * step_x, y, a, alpha=al)
    if lt >= rv + 0.1:
        x, y = x0 + (fc - 1) * step_x, y0 + (fr - 1) * step_y
        a = pop(lt, rv + 0.1, 0.35)
        R = 64 * a * (1 + 0.06 * math.sin(lt * 9))
        d.ellipse((x - R, y - R, x + R, y + R), outline=YEL, width=10)


def vis_ilusion(img, d, sc, lt):
    r = sc["r"]
    cy = sc["lay"]["vis"]
    rv = sc["reveal"]
    rl, rd = r["radios"]
    a = pop(lt, 0.25, 0.5)
    if a <= 0:
        return
    fade = 1.0 if lt < rv else max(0.0, 1 - (lt - rv) / 0.35)
    mv = 0.0 if lt < rv + 0.35 else ease_out((lt - rv - 0.35) / 0.5)
    lx, rx = 290 + 140 * mv, 790 - 140 * mv
    grey = (215, 215, 225)
    if fade > 0:
        for j in range(6):
            ang = j * math.pi / 3
            x, y = 290 + 165 * math.cos(ang), cy + 165 * math.sin(ang)
            R = 80 * a
            d.ellipse((x - R, y - R, x + R, y + R), fill=grey + (int(255 * fade),))
        for j in range(8):
            ang = j * math.pi / 4
            x, y = 790 + 102 * math.cos(ang), cy + 102 * math.sin(ang)
            R = 23 * a
            d.ellipse((x - R, y - R, x + R, y + R), fill=grey + (int(255 * fade),))
    org = (255, 128, 0)
    for x, R in ((lx, rl * a), (rx, rd * a)):
        d.ellipse((x - R, cy - R, x + R, cy + R), fill=org)
    if mv > 0.9:
        b = pop(lt, rv + 0.85, 0.35)
        for yy in (cy - rl, cy + rl):
            for xx in range(int(lx - rl), int(rx + rd), 30):
                d.line((xx, yy, xx + 16, yy), fill=YEL, width=6)
        pill(d, 540, cy - 165 - (1 - b) * 40, "¡EL IZQUIERDO ES MÁS GRANDE!", int(50 * max(b, 0.1)), WHITE, GREEN_D,
             pad=(30, 16))


PIX_STAGES = [100, 66, 44, 28, 17, 10]


def vis_pixel(img, d, sc, lt):
    r = sc["r"]
    cy = sc["lay"]["vis"]
    cd, rv, n = sc["cd"], sc["reveal"], sc["n"]
    a = pop(lt, 0.2, 0.45)
    if a <= 0:
        return
    if lt < cd:
        b = 150
    elif lt < rv:
        b = PIX_STAGES[min(len(PIX_STAGES) - 1, int((lt - cd) / n * len(PIX_STAGES)))]
    else:
        b = 1
    gl = int(10 * math.sin(lt * 31)) if lt < rv and (lt * 7) % 1 < 0.25 else 0
    sc_ = a * (1 + (0.04 * max(0, 1 - (lt - rv) / 0.4) if lt >= rv else 0))
    _marco_foto(img, d, _pixelada(b), 540, cy, RED if lt < rv else GREEN, lt, sc_, gl)
    if lt < rv:
        for j, (dx, dy, ph) in enumerate([(-360, -250, 0), (365, -200, 1.7), (-370, 230, 3.1), (360, 260, 4.4)]):
            s = 70 + 10 * math.sin(lt * 3 + ph)
            text(d, (540 + dx, cy + dy + math.sin(lt * 2 + ph) * 12), "?", tfont(int(s)), YEL, 8, (40, 0, 10))
    else:
        if lt < rv + 0.25:
            img.paste((255, 255, 255), (0, 0), Image.new("L", (W, H), int(200 * (1 - (lt - rv) / 0.25))))
        e = lt - rv
        if e < 1.8:
            for (vx, vy, col, sz, ph) in _S["confeti"]:
                x = 540 + vx * 620 * e
                y = cy + vy * 700 * e + 900 * e * e
                ang = ph + e * 8
                pts = [(x + sz * math.cos(ang + j * math.pi / 2) * (1 if j % 2 else 0.5),
                        y + sz * math.sin(ang + j * math.pi / 2) * (1 if j % 2 else 0.5)) for j in range(4)]
                d.polygon(pts, fill=col + (int(255 * max(0, 1 - e / 1.8)),))


VIS = {"fugitivo": vis_fugitivo, "rojo": vis_rojo, "memoria6": vis_memoria6, "infiltrado": vis_infiltrado,
       "ilusion": vis_ilusion, "pixel": vis_pixel,
       "secuencia": vis_secuencia, "logica": vis_logica, "memoria": vis_memoria, "acertijo": vis_acertijo,
       "reloj": vis_reloj, "busca": vis_busca}


# ------------------------------------------------------------------ escenas

LADDER = ["FÁCIL", "MEDIA", "DIFÍCIL", "MUY DIFÍCIL", "EXPERTO", "IMPOSIBLE"]


def draw_ladder(img, d, lights, lt, y_top=760, step=148):
    for i in range(6):
        y = y_top + (5 - i) * step
        w = 560 + i * 60
        on = lt >= lights[i]
        a = pop(lt, lights[i], 0.3) if on else 0
        L = lvl(i)
        sh = (math.sin(lt * 45) * 7 if (i == 5 and on) else 0)
        s = 1 + 0.12 * max(0, 1 - (lt - lights[i]) / 0.25) if on else 1
        box = (540 - w / 2 * s + sh, y - 54 * s, 540 + w / 2 * s + sh, y + 54 * s)
        if on:
            if i == 5:
                g = 0.5 + 0.5 * math.sin(lt * 6)
                rr(d, (box[0] - 22, box[1] - 22, box[2] + 22, box[3] + 22), 70, (239, 55, 70, int(60 + 70 * g)))
            shadow(d, box, 54, 10, 70)
            rr(d, box, 54, (30, 6, 12) if i == 5 else L[2], outline=RED if i == 5 else WHITE, width=6)
        else:
            rr(d, box, 54, (255, 255, 255, 26), outline=(255, 255, 255, 70), width=4)
        col = WHITE if on else (255, 255, 255, 120)
        lab = "NIVEL ☠" if i == 5 else f"NIVEL {i + 1}"
        if i == 5:
            d.text((box[0] + 46, y + 3), "NIVEL", font=tfont(52), fill=col, anchor="lm")
            paste_c(img, _sprite("imagenes/calavera_3d.png", 74), box[0] + 245, y,
                    1 + (0.1 * math.sin(lt * 8) if on else 0), alpha=1 if on else 0.5)
        else:
            d.text((box[0] + 46, y + 3), lab, font=tfont(52), fill=col, anchor="lm")
        d.text((box[2] - 46, y + 3), LADDER[i], font=tfont(44), fill=(YEL if i == 5 and on else col), anchor="rm")
        if on and a < 1:
            pass


def draw_hook(img, d, sc, lt):
    c = _S["c"]
    l1, l2 = c["gancho"]["texto"]
    # texto grande desde el primer fotograma, con golpe de zoom y sacudida
    p = ease_out(lt / 0.28)
    s = 1.12 - 0.12 * p
    sh = math.sin(lt * 50) * 10 * max(0, 1 - lt / 0.35)
    text(d, (540 + sh, 330), l1, tfont(int(118 * s)), WHITE, 12, (20, 10, 40), sh=10)
    text(d, (540 - sh, 470), l2, tfont(int(128 * s)), YEL, 13, (20, 10, 40), sh=10)
    if c["gancho"].get("teaser") and _S.get("foto") is not None:
        b = 140 if int(lt * 7) % 2 == 0 else 110
        gl = int(14 * math.sin(lt * 40))
        a = ease_out_back(min(1, lt / 0.35))
        _marco_foto(img, d, _pixelada(b), 540 + math.sin(lt * 45) * 8 * max(0, 1 - lt / 0.5), 980,
                    RED, lt, 0.92 * (0.75 + 0.25 * a), gl)
        for j, (dx, dy, ph) in enumerate([(-360, -250, 0), (360, -200, 1.7), (-360, 250, 3.1), (360, 270, 4.4)]):
            s_ = 80 + 12 * math.sin(lt * 3 + ph)
            text(d, (540 + dx, 980 + dy + math.sin(lt * 2 + ph) * 12), "?", tfont(int(s_)), YEL, 8, (40, 0, 10))
        st = pop(lt, 0.35, 0.35)
        if st > 0:
            stp = Image.new("RGBA", (640, 150), (0, 0, 0, 0))
            sd = ImageDraw.Draw(stp)
            rr(sd, (6, 6, 634, 144), 30, RED + (235,), outline=WHITE, width=8)
            sd.text((320, 78), "NIVEL IMPOSIBLE", font=tfont(78), fill=WHITE, anchor="mm")
            paste_c(img, stp, 540, 1015, 1.6 - 0.6 * st, angle=-10)
        q = pop(lt, 0.7, 0.4)
        if q > 0:
            pill(d, 540, 1400 + (1 - q) * 120, "¿QUIÉN ES?", int(80 * max(q, 0.1)), YEL, (40, 20, 0), pad=(46, 22))
    else:
        draw_ladder(img, d, sc["lights"], lt)
        peg = c["gancho"].get("pegatina")
        if peg:
            # pegatina de reto que entra de golpe y late
            a = pop(lt, 0.15, 0.3)
            if a > 0:
                f = tfont(50)
                tw = d.textlength(peg, font=f)
                st = Image.new("RGBA", (int(tw + 90), 120), (0, 0, 0, 0))
                sd = ImageDraw.Draw(st)
                rr(sd, (8, 14, st.width - 2, 118), 48, (0, 0, 0, 80))
                rr(sd, (0, 2, st.width - 10, 106), 48, RED, outline=WHITE, width=6)
                sd.text(((st.width - 10) / 2, 55), peg, font=f, fill=WHITE, anchor="mm")
                paste_c(img, st, 540, 600, a * (1 + 0.05 * math.sin(lt * 9)), angle=-4)
    # destello al encenderse el nivel imposible
    tl = sc["lights"][5]
    if tl <= lt < tl + 0.25:
        img.paste((255, 255, 255), (0, 0),
                  Image.new("L", (W, H), int(150 * (1 - (lt - tl) / 0.25))))


def draw_card(img, d, sc, lt):
    k, r = sc["k"], sc["r"]
    L = lvl(k)
    extra = bool(r.get("extra"))
    path_bar(img, d, k, k, lt)
    a = pop(lt, 0.25, 0.45)
    if a > 0:
        d.text((540, 560), "NIVEL", font=tfont(int(90 * a)), fill=(255, 255, 255, 230), anchor="mm",
               stroke_width=8, stroke_fill=L[3])
        if extra:
            sh = math.sin(lt * 38) * 9
            paste_c(img, _sprite("imagenes/calavera_3d.png", 300), 540 + sh, 800, a * (1 + 0.05 * math.sin(lt * 6)))
        else:
            text(d, (540, 790), str(k + 1), tfont(int(300 * a)), WHITE, 16, L[3], sh=14)
    b = pop(lt, 0.45, 0.4)
    if b > 0:
        pill(d, 540, 1030 + (1 - b) * 200, r["nombre"], 76, RED if extra else WHITE, WHITE if extra else L[3],
             pad=(46, 22))
    # medidor de dificultad
    for i in range(5):
        tb = 0.65 + 0.09 * i
        on = (i <= k) and lt >= tb
        x = 540 - 2 * 136 + i * 136
        box = (x - 58, 1165, x + 58, 1205)
        if on:
            q = pop(lt, tb, 0.25)
            col = RED if extra else WHITE
            rr(d, (x - 58 * q, 1165, x + 58 * q, 1205), 20, col)
        else:
            rr(d, box, 20, (255, 255, 255, 60))
    c2 = pop(lt, 0.8, 0.4)
    if c2 > 0:
        d.text((540, 1268), f"DIFICULTAD: {r['dificultad']}", font=tfont(int(54 * c2)),
               fill=YEL if extra else WHITE, anchor="mm", stroke_width=6, stroke_fill=L[3])


def draw_q(img, d, sc, lt):
    r = sc["r"]
    k = sc["k"]
    done = k
    fill_k = 1.0
    if sc["stamp"] is not None and lt >= sc["stamp"]:
        done = k + 1
        fill_k = ease_out((lt - sc["stamp"]) / 0.5)
    path_bar(img, d, k if done == k else min(k + 1, 5), done, lt, fill_k)
    if r["tipo"] == "memoria" or (r["tipo"] in NUEVOS and r.get("memoriza")):
        txt = r["memoriza"] if lt < sc["q_t"] else r["pregunta"]
        q_card(img, d, sc, lt, txt, 0.0 if lt < sc["q_t"] else sc["q_t"])
    else:
        q_card(img, d, sc, lt, r["pregunta"])
    if r["tipo"] == "busca":
        options(img, d, sc, lt)
        VIS["busca"](img, d, sc, lt)
    else:
        VIS[r["tipo"]](img, d, sc, lt)
        if r["opciones"]:
            options(img, d, sc, lt)
    timer(img, d, sc, lt)
    if sc["extra"] and lt >= sc["reveal"] and r.get("pill_final"):
        b = pop(lt, sc["reveal"] + 0.3, 0.4)
        cx, cy = sc["lay"]["timer"]
        pulse = 1 + 0.05 * math.sin(lt * 8)
        pill(d, 540, cy + 30 + (1 - b) * 80, r["pill_final"], int(52 * max(b, 0.1) * pulse), YEL, (40, 20, 0),
             pad=(36, 18))
    elif sc["extra"] and lt >= sc["reveal"]:
        b = pop(lt, sc["reveal"] + 0.1, 0.4)
        cx, cy = sc["lay"]["timer"]
        pill(d, 540, cy + (1 - b) * 80, "¡ESCRÍBELO EN COMENTARIOS!", int(50 * max(b, 0.1)), YEL, (40, 20, 0),
             pad=(36, 18))
    stamp(img, d, sc, lt)


def draw_outro(img, d, sc, lt):
    # chips de todos los niveles
    for i in range(6):
        a = pop(lt, 0.15 + 0.07 * i, 0.35)
        if a <= 0:
            continue
        x = NODES_X[i]
        bounce = math.sin(lt * 5 - i * 0.7) * 10
        r = 46 * a
        y = 300 + bounce
        d.ellipse((x - r + 3, y - r + 9, x + r + 3, y + r + 9), fill=(0, 0, 0, 60))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(30, 6, 12) if i == 5 else lvl(i)[2], outline=WHITE, width=5)
        if i == 5:
            paste_c(img, _sprite("imagenes/calavera_3d.png", 62), x, y, a)
        else:
            d.text((x, y + 3), str(i + 1), font=tfont(int(54 * a)), fill=WHITE, anchor="mm")
    a = pop(lt, 0.1, 0.45)
    y = 420 + (1 - a) * -600
    box = (80, y, 1000, y + 420)
    shadow(d, box, 48, 14, 70)
    rr(d, box, 48, WHITE)
    f, lines, lh = fit(d, "¿Hasta qué nivel has llegado?", 820, 240, 104)
    yy = y + 150 - lh * len(lines) / 2 + lh / 2
    for ln in lines:
        d.text((540, yy), ln, font=f, fill=(30, 20, 60), anchor="mm")
        yy += lh
    d.text((540, y + 340), "¡Coméntalo abajo!", font=font(56), fill=(128, 76, 245),
           anchor="mm")
    b = pop(lt, sc["shout_at"] - 0.15, 0.4)
    if b > 0:
        pulse = 1 + 0.07 * math.sin(lt * 9)
        pill(d, 540, 960 + (1 - b) * 900, "¡SÍGUEME PARA MÁS!", int(64 * pulse), YEL, (40, 20, 0))
    c = pop(lt, sc["shout_at"] + 0.2, 0.6)
    if c > 0:
        size = int(380 * c * (1 + 0.025 * math.sin(lt * 4)))
        if size > 4:
            d.ellipse((540 - size / 2, 1290 - size / 2 + 14, 540 + size / 2, 1290 + size / 2 + 14), fill=(0, 0, 0, 70))
            paste_c(img, _S["logo"], 540, 1290, size / _S["logo"].width)


def username(img, y=USER_Y):
    d = ImageDraw.Draw(img, "RGBA")
    f = font(50)
    w = d.textlength(USUARIO, font=f)
    rr(d, (540 - w / 2 - 34, y - 44, 540 + w / 2 + 34, y + 44), 44, (0, 0, 0, 110))
    d.text((540, y), USUARIO, font=f, fill=WHITE, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0, 160))


DRAW = {"hook": draw_hook, "card": draw_card, "q": draw_q, "outro": draw_outro}


def render_frame(i):
    t = i / FPS
    scenes = _S["scenes"]
    sc = scenes[-1]
    for s in scenes:
        if s["start"] <= t < s["start"] + s["dur"]:
            sc = s
            break
    lt = t - sc["start"]
    bg = background(sc, lt, t)
    if sc["kind"] == "q":
        vignette(bg, sc, lt)
    img = bg.copy()
    d = ImageDraw.Draw(img, "RGBA")
    DRAW[sc["kind"]](img, d, sc, lt)
    out_t = sc["dur"] - lt
    fade = 0.22
    if out_t < fade and sc is not scenes[-1] and scenes[scenes.index(sc) + 1]["kind"] == "q":
        img = Image.blend(bg, img, max(0.0, out_t / fade))
    elif out_t < fade and sc["kind"] == "q":
        img = Image.blend(bg, img, max(0.0, out_t / fade))
    username(img)
    return img.tobytes()


# ------------------------------------------------------------------ portada

def portada(c, state, out_dir):
    _init(state)
    img = _bg_frame(-1, 2.0)
    d = ImageDraw.Draw(img, "RGBA")
    l1, l2 = c["portada"]["titulo"]
    text(d, (540, 330), l1, tfont(120), WHITE, 12, (20, 10, 40), sh=10)
    text(d, (540, 470), l2, tfont(132), YEL, 13, (20, 10, 40), sh=10)
    if c["gancho"].get("teaser") and _S.get("foto") is not None:
        _marco_foto(img, d, _pixelada(120), 540, 960, RED, 0.3, 0.9, 6)
        for (dx, dy) in [(-350, -230), (350, -190), (-350, 230), (350, 250)]:
            text(d, (540 + dx, 960 + dy), "?", tfont(96), YEL, 8, (40, 0, 10))
        stp = Image.new("RGBA", (640, 150), (0, 0, 0, 0))
        sd0 = ImageDraw.Draw(stp)
        rr(sd0, (6, 6, 634, 144), 30, RED + (235,), outline=WHITE, width=8)
        sd0.text((320, 78), "NIVEL IMPOSIBLE", font=tfont(78), fill=WHITE, anchor="mm")
        paste_c(img, stp, 540, 990, 1.0, angle=-10)
        pill(d, 540, 1325, "¿QUIÉN ES?", 80, YEL, (40, 20, 0), pad=(46, 22))
    else:
        draw_ladder(img, d, [0] * 6, 5.0, y_top=680, step=134)
    # pegatina
    st = Image.new("RGBA", (900, 150), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    rr(sd, (8, 16, 892, 146), 60, (0, 0, 0, 80))
    rr(sd, (0, 4, 884, 134), 60, RED, outline=WHITE, width=7)
    f = tfont(54)
    txt = c["portada"]["pegatina"]
    while sd.textlength(txt, font=f) > 800:
        f = tfont(f.size - 3)
    sd.text((442, 72), txt, font=f, fill=WHITE, anchor="mm")
    paste_c(img, st, 540, 1500, 1.0, angle=-4)
    username(img, 1616)
    p916 = os.path.join(out_dir, f"{c['video']}_9x16.png")
    p34 = os.path.join(out_dir, f"{c['video']}_3x4.png")
    img.save(p916)
    img.crop((0, 240, 1080, 1680)).save(p34)
    return p916, p34


# ------------------------------------------------------------------ exportación

def render_video(c, voice, out_path, tono, workers=None, preview=None):
    scenes, events, total = build_timeline(c, voice)
    state = {"scenes": scenes, "c": c, "tono": tono}
    if preview is not None:
        _init(state)
        outs = []
        for s in preview:
            p = f"{out_path}_{s:05.1f}.png"
            Image.frombytes("RGB", (W, H), render_frame(int(s * FPS))).save(p)
            outs.append(p)
        return total, outs
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    wav = out_path + ".audio.wav"
    build_audio(events, total, wav, True, "pop", COUNTDOWN)
    frames = int(total * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-level", "4.1", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
           "-shortest", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers or os.cpu_count(), initializer=_init, initargs=(state,)) as pool:
        for k, fr in enumerate(pool.imap(render_frame, range(frames), chunksize=6)):
            proc.stdin.write(fr)
            if k % (FPS * 10) == 0:
                print(f"  fotograma {k}/{frames}", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg falló al exportar el vídeo.")
    os.remove(wav)
    return total, [out_path]

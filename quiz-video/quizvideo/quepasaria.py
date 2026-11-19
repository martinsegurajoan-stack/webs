"""Formato "¿QUÉ PASARÍA SI…?": explicación narrada y animada por código (sin imágenes de pago).

Un personaje dibujado por código cambia según avanza el tiempo (nº1: el pelo crece mes a mes),
con contador de tiempo arriba, regla de centímetros, iconos 3D que saltan, subtítulos palabra a palabra
y voz de narrador. Reutiliza la voz/caché, el alineado de palabras y la música de misterio.
"""

import math
import os
import random
import subprocess
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import audio, themes
from .misterio import _atempo, _compact, _decode, faltan, limpio, music_thriller, ruta_voz, sfx_golpe
from .personalidad import align_words, caption_chunks
from .render import FPS, USUARIO, W, H, ease_in, ease_out, ease_out_back, font, tfont

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
SR = audio.SR
WHITE = (255, 255, 255)
YEL = (255, 214, 0)
RED = (235, 40, 60)
INK = (20, 12, 40)
HAIR = (62, 38, 26)
HAIR_HI = (110, 72, 46)
SKIN = (246, 196, 160)
SKIN_D = (220, 160, 125)

__all__ = ["faltan", "build", "render", "portada"]


# ------------------------------------------------------------------ línea de tiempo

def build(c, sin_voz=False):
    tempo = c.get("tempo", 1.0)
    t = 0.0
    clips, subs, voices = [], [], []
    prev_cm = c["clips"][0].get("cm", 1.0)
    for k, cl in enumerate(c["clips"]):
        p = ruta_voz(c, cl)
        sig = None
        if os.path.exists(p) and not sin_voz:
            sig = _atempo(_compact(_decode(p)), tempo)
            sig = sig / (np.max(np.abs(sig)) or 1) * 0.92
        d = len(sig) / SR if sig is not None else len(limpio(cl["texto"])) / 15 / tempo
        start = t + (0.0 if k == 0 else 0.15)
        voices.append((sig, start))
        words, times = align_words(limpio(cl["texto"]), sig, d)
        for ch in caption_chunks(words, times, start, maxw=3, maxc=16):
            subs.append(ch)
        end = start + d + cl.get("pausa", 0.25)
        clips.append({"clip": cl, "start": t, "vstart": start, "vend": start + d, "end": end,
                      "cm0": prev_cm, "cm1": cl.get("cm", prev_cm)})
        prev_cm = cl.get("cm", prev_cm)
        t = end
    # cierre (tarjeta final, sin voz nueva: la última frase ya pide comentar y seguir)
    fin = {"start": t, "end": t + 2.2}
    total = fin["end"]
    for k in range(len(subs) - 1):
        subs[k]["end"] = min(subs[k]["end"], subs[k + 1]["start"])
    return {"clips": clips, "subs": subs, "voices": voices, "fin": fin, "total": total}


def build_audio(tl, path):
    total = tl["total"]
    mix = audio.Mixer(total)
    for sig, at in tl["voices"]:
        if sig is not None:
            mix.add_voice(sig, at, 1.0)
    whoosh, pop, tick = audio.sfx_whoosh(), audio.sfx_pop(), audio.sfx_tick()
    for k, ci in enumerate(tl["clips"]):
        cl = ci["clip"]
        if k > 0:
            mix.add_fx(whoosh, ci["start"], 0.45)
        for ic in cl.get("iconos", []):
            mix.add_fx(pop, ci["vstart"] + ic.get("desde", 0.3) * (ci["vend"] - ci["vstart"]), 0.6)
        if cl.get("efecto") == "stop":
            mix.add_fx(sfx_golpe(1.3), ci["vstart"] + cl.get("stop_en", 0.45) * (ci["vend"] - ci["vstart"]), 0.9)
        if ci["cm1"] > ci["cm0"] + 0.5 or cl.get("efecto") == "preview":
            # tic-tac del tiempo que pasa mientras crece
            g0, g1 = ci["vstart"], ci["vstart"] + 0.7 * (ci["vend"] - ci["vstart"])
            tt = g0
            while tt < g1:
                mix.add_fx(tick, tt, 0.35)
                tt += 0.25
    mix.add_fx(sfx_golpe(1.0), tl["fin"]["start"], 0.7)
    mix.add_fx(audio.sfx_applause(), tl["fin"]["start"] + 0.2, 0.5)
    stop_t = next((ci["vstart"] for ci in tl["clips"] if ci["clip"].get("efecto") == "stop"), total * 0.7)
    music = music_thriller(total, seed=11, marcas={"cuenta": stop_t, "final": tl["fin"]["start"]})
    audio.write_wav(path, mix.render(music, music_gain=0.3))


# ------------------------------------------------------------------ dibujo

_S = {}


def _spr(name, size):
    key = (name, size)
    if key not in _S["spr"]:
        im = Image.open(os.path.join(ASSETS, "quepasaria", name + ".png")).convert("RGBA")
        _S["spr"][key] = im.resize((size, size), Image.LANCZOS)
    return _S["spr"][key]


def paste_c(img, im, cx, cy, scale=1.0, ang=0.0, alpha=1.0):
    if scale <= 0.02 or alpha <= 0.01:
        return
    if abs(scale - 1) > 1e-3:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if ang:
        im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def pill(d, cx, cy, text, size, bg, fg, pad=(30, 14), outline=None):
    f = tfont(size)
    w = d.textlength(text, font=f)
    box = (cx - w / 2 - pad[0], cy - size / 2 - pad[1], cx + w / 2 + pad[0], cy + size / 2 + pad[1])
    r = (box[3] - box[1]) / 2
    d.rounded_rectangle((box[0] + 5, box[1] + 9, box[2] + 5, box[3] + 9), r, fill=(0, 0, 0, 90))
    d.rounded_rectangle(box, r, fill=bg, outline=outline, width=5 if outline else 0)
    d.text((cx, cy + size * 0.04), text, font=f, fill=fg, anchor="mm")


def _init(state):
    _S.clear()
    _S.update(state)
    _S["spr"] = {}
    h = state["tono"]
    top, bot = np.array(themes._hsv(h, 0.75, 0.42), float), np.array(themes._hsv(h + 25, 0.9, 0.12), float)
    y = np.linspace(0, 1, H)[:, None, None]
    x = np.linspace(-1, 1, W)[None, :, None]
    g = top * (1 - y) + bot * y + np.exp(-((x * 1.1) ** 2 + ((y - 0.42) / 0.33) ** 2)) * 70  # foco
    _S["bg"] = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    _S["acc"] = themes._hsv(h + 180, 0.7, 1.0)
    rnd = random.Random(4)
    _S["bokeh"] = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(20, 70), rnd.uniform(10, 40),
                    rnd.uniform(0.05, 0.16), rnd.uniform(0, 6.28)) for _ in range(22)]
    rc = random.Random(9)
    _S["pelos"] = [(rc.uniform(80, 1000), rc.uniform(-400, 0), rc.uniform(160, 320), rc.uniform(0, 6.28))
                   for _ in range(60)]
    _S["logo"] = Image.open(os.path.join(ASSETS, "logo.png")).convert("RGBA")
    # envolvente de la voz (para pequeñas reacciones del personaje)
    _S["cache"] = {}


def background(t):
    img = _S["bg"].copy()
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for x0, y0, r, sp, a, ph in _S["bokeh"]:
        y = (y0 - sp * t) % (H + 200) - 100
        x = x0 + 30 * math.sin(t * 0.4 + ph)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, int(255 * a * 0.5)))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6)))
    return img


# ---------------------------------------------------------------- personaje

S2 = 2  # se dibuja al doble y se reduce (bordes suaves)
CX, HEAD_Y = 540, 600


def _hair_bottom(cm):
    return 560 + cm * 10.0


def character(cm, t, cara="normal", puntas=0.0, sway=1.0):
    """Personaje (RGBA W×H) con el pelo de `cm` centímetros."""
    key = (round(cm, 1), round(t * 10) / 10, cara, round(puntas, 1))
    s = S2
    lay = Image.new("RGBA", (W * s, 1500 * s), (0, 0, 0, 0))  # al doble: bordes suaves al reducir
    sc = s
    d = ImageDraw.Draw(lay)

    def P(x, y):
        return (x * sc, y * sc)

    def poly(pts, fill):
        d.polygon([P(x, y) for x, y in pts], fill=fill)

    def ell(x0, y0, x1, y1, fill, outline=None, width=0):
        d.ellipse((*P(x0, y0), *P(x1, y1)), fill=fill, outline=outline, width=int(width * sc))

    rx, ry = 118, 140
    hb = _hair_bottom(cm)
    sw = math.sin(t * 1.6) * 6 * sway
    # --- pelo de detrás
    if cm > 3:
        half = min(150, 112 + cm * 2.2)
        pts_l, pts_r = [], []
        steps = 18
        for i in range(steps + 1):
            yy = 520 + (hb - 520) * i / steps
            grow = min(1, (yy - 520) / 260)
            wv = half + 40 * grow + (yy - 520) * 0.05
            off = sw * (yy - 520) / max(1, hb - 520)
            pts_l.append((CX - wv + off, yy))
            pts_r.append((CX + wv + off, yy))
        # borde inferior ondulado (mechones)
        bottom = []
        n = 9
        for i in range(n + 1):
            x = pts_l[-1][0] + (pts_r[-1][0] - pts_l[-1][0]) * i / n
            bottom.append((x, hb + (14 if i % 2 else -6)))
        poly(pts_l + bottom + pts_r[::-1], HAIR)
        if puntas > 0 and cm > 12:  # puntas abiertas: banda más clara y deshilachada abajo
            band = min(60, 20 + cm * 0.6)
            col = tuple(int(HAIR[i] + (200 - HAIR[i]) * 0.35 * puntas) for i in range(3))
            for i in range(n):
                x = pts_l[-1][0] + (pts_r[-1][0] - pts_l[-1][0]) * (i + 0.5) / n
                d.line((*P(x, hb - band), *P(x + (i % 3 - 1) * 8, hb + 12)), fill=col, width=int(9 * sc))
    # --- cuerpo (camiseta)
    shirt = _S.get("shirt", (60, 130, 230))
    poly([(CX - 60, 760), (CX + 60, 760), (CX + 210, 840), (CX + 200, 1450), (CX - 200, 1450),
          (CX - 210, 840)], shirt)
    poly([(CX - 46, 740), (CX + 46, 740), (CX + 40, 800), (CX - 40, 800)], SKIN_D)  # cuello
    ell(CX - 52, 770, CX + 52, 830, SKIN_D)
    # --- cabeza
    ell(CX - rx - 16, HEAD_Y - 18, CX - rx + 18, HEAD_Y + 40, SKIN)  # orejas
    ell(CX + rx - 18, HEAD_Y - 18, CX + rx + 16, HEAD_Y + 40, SKIN)
    ell(CX - rx, HEAD_Y - ry, CX + rx, HEAD_Y + ry, SKIN)
    # mejillas
    ell(CX - 88, HEAD_Y + 40, CX - 48, HEAD_Y + 66, (250, 160, 150))
    ell(CX + 48, HEAD_Y + 40, CX + 88, HEAD_Y + 66, (250, 160, 150))
    # ojos (parpadeo)
    blink = (t % 3.4) < 0.12
    ey = HEAD_Y + 4
    for sx in (-1, 1):
        ex = CX + sx * 46
        if blink:
            d.line((*P(ex - 20, ey), *P(ex + 20, ey)), fill=INK, width=int(6 * sc))
        else:
            big = 1.25 if cara == "sorprendido" else 1.0
            ell(ex - 20 * big, ey - 24 * big, ex + 20 * big, ey + 24 * big, WHITE)
            ell(ex - 11, ey - 11, ex + 11, ey + 13, INK)
            ell(ex - 6, ey - 8, ex, ey - 2, WHITE)
        # cejas
        by = ey - 40 - (10 if cara == "sorprendido" else 0)
        tilt = {"agobiado": -10, "triste": -12, "pensativo": 6}.get(cara, 0) * sx
        d.line((*P(ex - 22, by + tilt), *P(ex + 22, by - tilt)), fill=HAIR, width=int(9 * sc))
    # boca
    my = HEAD_Y + 78
    if cara == "sorprendido":
        ell(CX - 16, my - 18, CX + 16, my + 20, (120, 30, 40))
    elif cara in ("agobiado", "triste"):
        d.arc((*P(CX - 34, my), *P(CX + 34, my + 34)), 200, 340, fill=(120, 30, 40), width=int(7 * sc))
    else:
        d.chord((*P(CX - 40, my - 26), *P(CX + 40, my + 22)), 10, 170, fill=(120, 30, 40))
        d.chord((*P(CX - 30, my - 8), *P(CX + 30, my + 20)), 30, 150, fill=(240, 110, 120))
    if cara == "agobiado":  # gota de sudor
        ell(CX + 96, HEAD_Y - 70, CX + 118, HEAD_Y - 40, (120, 200, 255))
    # --- pelo de arriba (casquete) y flequillo
    cap_h = 30 + min(cm, 15) * 2
    d.pieslice((*P(CX - rx - 8, HEAD_Y - ry - 10 - cap_h * 0.3), *P(CX + rx + 8, HEAD_Y + ry * 0.6)),
               180, 360, fill=HAIR)
    if cm <= 12:
        drop = 10 + min(cm, 8) * 13  # el flequillo baja hasta los ojos (fase incómoda)
        pts = [(CX - rx - 4, HEAD_Y - 40)]
        n = 7
        for i in range(n + 1):
            x = CX - rx + (2 * rx) * i / n
            pts.append((x + sw * 0.4, HEAD_Y - 70 + drop + (16 if i % 2 else 0)))
        pts.append((CX + rx + 4, HEAD_Y - 40))
        poly(pts, HAIR)
    else:  # raya al medio: cortinas laterales
        for sx in (-1, 1):
            poly([(CX, HEAD_Y - ry + 6), (CX + sx * (rx + 10), HEAD_Y - 60), (CX + sx * (rx + 12), HEAD_Y + 60),
                  (CX + sx * (rx - 18), HEAD_Y + 10), (CX + sx * 20, HEAD_Y - 90)], HAIR)
    # mechones delanteros sobre los hombros (pelo largo)
    if cm > 22:
        for sx in (-1, 1):
            x0 = CX + sx * (rx - 6)
            yb = min(hb + 10, 1440)
            pts = []
            for i in range(13):
                yy = HEAD_Y + 20 + (yb - HEAD_Y - 20) * i / 12
                off = sx * (10 + 30 * min(1, (yy - HEAD_Y) / 260)) + sw * (i / 12)
                pts.append((x0 + off, yy))
            wid = 34
            left = [(x - wid / 2, y) for x, y in pts]
            right = [(x + wid / 2, y) for x, y in pts][::-1]
            poly(left + right, HAIR)
            d.line([P(x + 6, y) for x, y in pts[2:]], fill=HAIR_HI, width=int(5 * sc))
    if cm > 4:  # brillo del pelo
        d.arc((*P(CX - 80, HEAD_Y - ry + 4), *P(CX + 40, HEAD_Y - 40)), 200, 280, fill=HAIR_HI, width=int(9 * sc))
    return lay.reduce(s)


# ---------------------------------------------------------------- piezas de pantalla

def hud_tiempo(img, d, etiqueta, frac, lt, frozen=False):
    p = ease_out_back(min(1, lt / 0.35))
    size = int(118 * (0.6 + 0.4 * p))
    col = RED if frozen else WHITE
    d.text((540, 205), etiqueta, font=tfont(size), fill=col, anchor="mm", stroke_width=12, stroke_fill=INK)
    # barra 0 → 5 años
    x0, x1, y = 140, 940, 318
    d.rounded_rectangle((x0, y - 13, x1, y + 13), 13, fill=(0, 0, 0, 110))
    fx = x0 + (x1 - x0) * max(0.0, min(1.0, frac))
    if fx > x0 + 4:
        d.rounded_rectangle((x0, y - 13, fx, y + 13), 13, fill=RED if frozen else YEL)
    for k in range(6):
        xx = x0 + (x1 - x0) * k / 5
        d.text((xx, y + 40), f"{k}", font=tfont(30), fill=(255, 255, 255, 200), anchor="mm")
    d.ellipse((fx - 20, y - 20, fx + 20, y + 20), fill=WHITE, outline=INK, width=5)


def regla(img, d, cm, t):
    x = 1000
    y0, y1 = _hair_bottom(0), _hair_bottom(80)
    d.rounded_rectangle((x - 26, y0 - 10, x + 26, y1 + 10), 12, fill=(255, 236, 160, 230), outline=INK, width=4)
    for k in range(0, 81, 5):
        yy = _hair_bottom(k)
        ln = 26 if k % 10 == 0 else 14
        d.line((x - 26, yy, x - 26 + ln, yy), fill=INK, width=4 if k % 10 == 0 else 2)
        if k % 20 == 0 and k:
            d.text((x + 10, yy), str(k), font=font(24), fill=INK, anchor="mm")
    yy = _hair_bottom(cm)
    d.line((690, yy, x - 30, yy), fill=(255, 255, 255, 160), width=3)
    pill(d, x - 110, yy, f"{cm:.0f} CM" if cm >= 1 else f"{cm:.1f} CM", 38, YEL, INK, pad=(16, 8))


def icono(img, d, ic, lt, k):
    a = ease_out_back(min(1, lt / 0.4))
    if a <= 0:
        return
    left = ic.get("lado", "izq" if k % 2 == 0 else "der") == "izq"
    cx = 175 if left else 870
    cy = ic.get("y", 930 + (k % 2) * 40)
    bob = 8 * math.sin(lt * 3 + k)
    paste_c(img, _spr(ic["img"], 170), cx, cy + bob, a, ang=(8 if left else -8) * math.sin(lt * 2))
    if ic.get("texto"):
        lines = ic["texto"].split("|")
        for i, ln in enumerate(lines):
            fs = 42
            pill(d, cx, cy + 120 + i * 62 + (1 - a) * 80, ln, fs, WHITE if i else _S["acc"], INK, pad=(18, 10))


def subtitulos(img, t):
    for ch in _S["tl"]["subs"]:
        if not (ch["start"] <= t < ch["end"]):
            continue
        words = [w.upper() for w, _, _ in ch["words"]]
        act = [i for i, (_, a, b) in enumerate(ch["words"]) if a <= t]
        cur = act[-1] if act else 0
        size = 84
        tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        while True:
            f = tfont(size)
            ws = [tmp.textlength(w, font=f) for w in words]
            tot = sum(ws) + 24 * (len(ws) - 1)
            if tot <= 980 or size <= 52:
                break
            size -= 4
        d = ImageDraw.Draw(img)
        p = min(1, (t - ch["start"]) / 0.12)
        y = 1515 + 10 * (1 - p)
        x = 540 - tot / 2
        for i, (w, wd) in enumerate(zip(words, ws)):
            col = YEL if i == cur else WHITE
            sz = size + (8 if i == cur else 0)
            d.text((x + wd / 2, y), w, font=tfont(sz), fill=col, anchor="mm", stroke_width=10, stroke_fill=INK)
            x += wd + 24
        break


def marca(img):
    d = ImageDraw.Draw(img)
    f = font(36)
    w = d.textlength(USUARIO, font=f)
    d.rounded_rectangle((540 - w / 2 - 26, 1690, 540 + w / 2 + 26, 1752), 31, fill=(0, 0, 0, 120))
    d.text((540, 1721), USUARIO, font=f, fill=WHITE, anchor="mm")


def flash(img, a):
    if a > 0:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(220 * min(1, a)))))


# ---------------------------------------------------------------- fotograma

def _estado(t):
    tl = _S["tl"]
    for k, ci in enumerate(tl["clips"]):
        if t < ci["end"]:
            return k, ci
    return len(tl["clips"]) - 1, tl["clips"][-1]


def cm_en(ci, t):
    cl = ci["clip"]
    lt = t - ci["vstart"]
    dur = max(0.5, ci["vend"] - ci["vstart"])
    if cl.get("efecto") == "preview":  # time-lapse del gancho: crece del todo y vuelve
        maxcm = cl.get("cm_max", 75)
        u = max(0.0, min(1.0, t / max(0.5, ci["end"])))
        return ci["cm0"] + (maxcm - ci["cm0"]) * math.sin(math.pi * min(1, u * 1.05)) ** 0.8
    k = ease_out(max(0.0, min(1.0, lt / (dur * 0.7))))
    cm = ci["cm0"] + (ci["cm1"] - ci["cm0"]) * k
    if cl.get("efecto") == "stop":  # se queda clavado a partir del STOP
        st = cl.get("stop_en", 0.45) * dur
        if lt > st:
            cm = ci["cm0"] + (ci["cm1"] - ci["cm0"]) * ease_out(st / (dur * 0.7))
    return cm


def render_frame(i):
    t = i / FPS
    tl = _S["tl"]
    c = _S["c"]
    img = background(t)
    d = ImageDraw.Draw(img)
    if t >= tl["fin"]["start"]:
        return final(img, t - tl["fin"]["start"], t)
    k, ci = _estado(t)
    cl = ci["clip"]
    lt = t - ci["start"]
    cm = cm_en(ci, t)
    meses = cl.get("meses", 0)
    frozen = False
    if cl.get("efecto") == "stop":
        dur = max(0.5, ci["vend"] - ci["vstart"])
        frozen = t - ci["vstart"] > cl.get("stop_en", 0.45) * dur
    # personaje (con ligero zoom de cámara por escena)
    ch = character(cm, t, cl.get("cara", "normal"), cl.get("puntas", 0.0))
    zoom = 1.0 + 0.035 * ease_in_out(min(1, lt / max(1, ci["end"] - ci["start"])))
    shake = (math.sin(t * 60) * 12 * max(0, 1 - (t - ci["vstart"] - cl.get("stop_en", 0.45) *
                                               (ci["vend"] - ci["vstart"])) / 0.4)) if frozen else 0
    if k == 0:
        shake = math.sin(t * 55) * 14 * max(0, 1 - t / 0.5)
    chz = ch.resize((int(ch.width * zoom), int(ch.height * zoom)), Image.BILINEAR)
    img.alpha_composite(chz, (int(540 - chz.width / 2 + shake), int(150 + (1500 - chz.height) / 2 - 40)))
    d = ImageDraw.Draw(img)
    if k == 0:
        gancho(img, d, cl, t)
    else:
        hud_tiempo(img, d, cl.get("etiqueta", ""), meses / 60.0 if not frozen else meses / 60.0, lt, frozen)
        regla(img, d, cm, t)
    for j, ic in enumerate(cl.get("iconos", [])):
        t0 = ci["vstart"] + ic.get("desde", 0.3) * (ci["vend"] - ci["vstart"])
        if t >= t0:
            icono(img, d, ic, t - t0, j + k)
    if cl.get("efecto") == "stop" and frozen:
        st = ci["vstart"] + cl.get("stop_en", 0.45) * (ci["vend"] - ci["vstart"])
        a = ease_out_back(min(1, (t - st) / 0.3))
        stamp = Image.new("RGBA", (520, 200), (0, 0, 0, 0))
        sd = ImageDraw.Draw(stamp)
        sd.rounded_rectangle((6, 6, 514, 194), 30, outline=RED, width=14, fill=(255, 255, 255, 40))
        sd.text((260, 102), "¡STOP!", font=tfont(120), fill=RED, anchor="mm")
        paste_c(img, stamp, 540, 1180, (1.6 - 0.6 * a), ang=-8, alpha=min(1, a * 1.5))
        flash(img, 0.6 * max(0, 1 - (t - st) / 0.2))
    if cl.get("efecto") == "contador":
        contador(img, d, cl, t - ci["vstart"], ci["vend"] - ci["vstart"])
    subtitulos(img, t)
    marca(img)
    if k > 0 and lt < 0.12:
        flash(img, 0.35 * (1 - lt / 0.12))
    return img.convert("RGB").tobytes()


def ease_in_out(x):
    x = max(0.0, min(1.0, x))
    return 0.5 - 0.5 * math.cos(math.pi * x)


def gancho(img, d, cl, t):
    """Texto ENORME desde el fotograma 0, con golpe de zoom, sacudida y destello."""
    lines = _S["c"]["gancho"]["texto"]
    p = ease_out(min(1, t / 0.25))
    sh = math.sin(t * 50) * 10 * max(0, 1 - t / 0.4)
    sizes = [96, 128, 96]
    y = 190
    for i, ln in enumerate(lines):
        s = int(sizes[i % 3] * (1.15 - 0.15 * p))
        col = YEL if i == 1 else WHITE
        d.text((540 + (sh if i % 2 else -sh), y), ln, font=tfont(s), fill=col, anchor="mm", stroke_width=12,
               stroke_fill=INK)
        y += s * 0.95
    peg = _S["c"]["gancho"].get("pegatina")
    if peg:
        a = ease_out_back(min(1, max(0, t - 0.6) / 0.35))
        if a > 0:
            st = Image.new("RGBA", (1000, 130), (0, 0, 0, 0))
            sd = ImageDraw.Draw(st)
            f = tfont(52)
            w = sd.textlength(peg, font=f)
            box = (500 - w / 2 - 34, 10, 500 + w / 2 + 34, 118)
            sd.rounded_rectangle((box[0] + 6, box[1] + 8, box[2] + 6, box[3] + 8), 50, fill=(0, 0, 0, 90))
            sd.rounded_rectangle(box, 50, fill=RED, outline=WHITE, width=6)
            sd.text((500, 66), peg, font=f, fill=WHITE, anchor="mm")
            paste_c(img, st, 540, 1300, a * (1 + 0.04 * math.sin(t * 9)), ang=-4)
    flash(img, 0.9 * max(0, 1 - t / 0.18))


def contador(img, d, cl, lt, dur):
    """Número que sube (p. ej. pelos caídos) con pelos cayendo."""
    a, b = cl["contador"]["de"], cl["contador"]["a"]
    k = ease_out(max(0.0, min(1.0, (lt - 0.3) / max(0.5, dur * 0.6))))
    v = int(a + (b - a) * k)
    txt = f"{v:,}".replace(",", ".")
    p = ease_out_back(min(1, max(0, lt) / 0.35))
    d.text((540, 1190), txt, font=tfont(int(130 * max(0.1, p))), fill=YEL, anchor="mm", stroke_width=12,
           stroke_fill=INK)
    d.text((540, 1290), cl["contador"]["texto"], font=tfont(50), fill=WHITE, anchor="mm", stroke_width=8,
           stroke_fill=INK)
    for x0, y0, sp, ph in _S["pelos"]:
        y = y0 + sp * lt
        if y > 1650:
            continue
        x = x0 + 30 * math.sin(lt * 2 + ph)
        d.arc((x - 30, y - 10, x + 30, y + 40), 200 + 20 * math.sin(ph), 330, fill=HAIR, width=4)


def final(img, lt, t):
    d = ImageDraw.Draw(img)
    c = _S["c"]
    ch = character(c["clips"][-1].get("cm", 75), t, "feliz", 1.0)
    chs = ch.resize((int(ch.width * 0.62), int(ch.height * 0.62)), Image.BILINEAR)
    img.alpha_composite(chs, (int(540 - chs.width / 2), 560))
    d = ImageDraw.Draw(img)
    a = ease_out_back(min(1, lt / 0.4))
    l1, l2 = c["cierre"]["titulo"]
    d.text((540, 230 - (1 - a) * 300), l1, font=tfont(96), fill=WHITE, anchor="mm", stroke_width=12, stroke_fill=INK)
    d.text((540, 345 - (1 - a) * 300), l2, font=tfont(110), fill=YEL, anchor="mm", stroke_width=12, stroke_fill=INK)
    b = ease_out_back(min(1, max(0, lt - 0.35) / 0.35))
    if b > 0:
        pill(d, 540, 470, c["cierre"]["pill"], int(52 * b), RED, WHITE, outline=WHITE)
    e = ease_out_back(min(1, max(0, lt - 0.7) / 0.4))
    if e > 0:
        pill(d, 540, 1470, "¡SÍGUEME PARA MÁS!", int(60 * e * (1 + 0.05 * math.sin(lt * 9))), YEL, INK)
        lg = _S["logo"].resize((220, 220), Image.LANCZOS)
        paste_c(img, lg, 540, 1600, e)
    flash(img, 0.7 * max(0, 1 - lt / 0.2))
    marca(img)
    return img.convert("RGB").tobytes()


# ---------------------------------------------------------------- exportación

def render(c, out_path, tono, preview=None, workers=None, sin_voz=False):
    tl = build(c, sin_voz=sin_voz)
    state = {"c": c, "tl": tl, "tono": tono}
    if preview is not None:
        _init(state)
        outs = []
        for s in preview:
            p = f"{out_path}_{s:05.1f}.png"
            Image.frombytes("RGB", (W, H), render_frame(int(s * FPS))).save(p)
            outs.append(p)
        return tl["total"], outs
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    wav = out_path + ".audio.wav"
    build_audio(tl, wav)
    frames = int(tl["total"] * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "21",
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1", "-c:a", "aac", "-b:a", "192k",
           "-ar", "44100", "-shortest", "-movflags", "+faststart", out_path]
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
    return tl["total"], [out_path]


def portada(c, tono, out_dir):
    _init({"c": c, "tl": {"subs": []}, "tono": tono})
    img = background(3.0)
    ch = character(c["portada"].get("cm", 75), 1.0, c["portada"].get("cara", "sorprendido"), 1.0)
    img.alpha_composite(ch, (0, 330))
    d = ImageDraw.Draw(img)
    l1, l2, l3 = c["portada"]["titulo"]
    d.text((540, 330), l1, font=tfont(84), fill=WHITE, anchor="mm", stroke_width=12, stroke_fill=INK)
    d.text((540, 440), l2, font=tfont(118), fill=YEL, anchor="mm", stroke_width=13, stroke_fill=INK)
    d.text((540, 550), l3, font=tfont(84), fill=WHITE, anchor="mm", stroke_width=12, stroke_fill=INK)
    st = Image.new("RGBA", (1000, 140), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    f = tfont(56)
    peg = c["portada"]["pegatina"]
    w = sd.textlength(peg, font=f)
    box = (500 - w / 2 - 36, 12, 500 + w / 2 + 36, 126)
    sd.rounded_rectangle(box, 54, fill=RED, outline=WHITE, width=7)
    sd.text((500, 70), peg, font=f, fill=WHITE, anchor="mm")
    paste_c(img, st, 540, 1440, 1.0, ang=-4)
    paste_c(img, _spr("tijeras", 200).copy(), 170, 900, 1.0, ang=15)
    paste_c(img, _spr("prohibido", 230), 170, 900, 1.0)
    paste_c(img, _spr("reloj_arena", 190), 900, 980, 1.0, ang=-10)
    marca(img)
    os.makedirs(out_dir, exist_ok=True)
    p916 = os.path.join(out_dir, f"{c['video']}_9x16.png")
    p34 = os.path.join(out_dir, f"{c['video']}_3x4.png")
    rgb = img.convert("RGB")
    rgb.save(p916)
    rgb.crop((0, 240, 1080, 1680)).save(p34)
    return p916, p34

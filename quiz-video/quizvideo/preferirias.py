"""Formato "¿QUÉ PREFERIRÍAS?" (dilemas con dos opciones y % de la gente al terminar la cuenta atrás).

El juego EMPIEZA EN EL FOTOGRAMA 0 (la pregunta 1 hace de gancho). Cada pregunta: foto grande + dos tarjetas
(A roja / B azul) + VS con cuenta atrás de 3 s → las barras se llenan con los % y la opción más elegida se corona.
EXTRA sin %: modo suspense («?» que giran) para que se peleen en comentarios. Cierre: «¡Coméntalo y sígueme para
más vídeos como este!». Subtítulos grandes estilo TikTok de la voz. Duración objetivo ≤ 60 s.
"""

import math
import os
import random
import subprocess
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from .evita import build_audio
from .fiesta import vsay
from .niveles import paste_c, pill, pop, rr, text, username
from .render import FPS, W, H, ease_in, ease_out, ease_out_back, font, tfont, fit

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
DECOR = os.path.join(ASSETS, "preferirias")
WHITE, YEL, DARK = (255, 255, 255), (255, 214, 0), (20, 10, 30)
COL_A, COL_B = (236, 40, 80), (30, 120, 255)
CD = 3
BGS = [((70, 0, 20), (10, 0, 6), (220, 30, 60)), ((0, 110, 120), (0, 20, 40), (0, 220, 220)),
       ((200, 90, 0), (40, 10, 0), (255, 180, 40)), ((110, 30, 200), (20, 0, 50), (200, 100, 255)),
       ((0, 130, 60), (0, 30, 15), (80, 230, 120)), ((120, 0, 90), (20, 0, 25), (255, 40, 160))]
CONF = [YEL, (0, 230, 210), (255, 70, 170), WHITE, (160, 90, 255), (60, 220, 120)]


def comp(img, im, pos):
    img.paste(im, (int(pos[0]), int(pos[1])), im)


def mix(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def _words(txt):
    import re
    return re.sub(r"\[[^\]]*\]", "", txt).split()


# ------------------------------------------------------------------ línea de tiempo

def build_timeline(c, voice):
    scenes, ev = [], []
    t = 0.0
    n = len(c["preguntas"])
    for k, q in enumerate(c["preguntas"]):
        st = t
        extra = bool(q.get("extra"))
        v0 = 0.0 if k == 0 else 0.12
        sig, d = vsay(voice, q["voz"])
        ev += [("voice", sig, st + v0), ("fx", "impact" if (k == 0 or extra) else "whoosh", st)]
        if extra:
            ev += [("fx", "buzz", st + 0.05), ("fx", "impact", st + 0.4)]
        T = {"voz": (v0, d, q["voz"]), "cards": 1.1 if extra else 0.0}
        T["cd"] = float(q.get("cd_inicio", v0 + d + 0.05))
        ev += [("fx", "riser", st + T["cd"]), ("music_boost", st + T["cd"], st + T["cd"] + CD)]
        for s in range(CD):
            ts = st + T["cd"] + s
            ev += [("fx", "heart", ts), ("fx", "tick_high" if s == CD - 1 else "tick", ts), ("fx", "tock", ts + 0.5)]
        T["rv"] = T["cd"] + CD
        ev += [("fx", "impact", st + T["rv"]), ("fx", "whoosh", st + T["rv"])]
        if extra:
            ev += [("fx", "boing", st + T["rv"] + 0.1)]
            dur = T["rv"] + 1.6
        else:
            for j in range(6):
                ev.append(("fx", "pop", st + T["rv"] + 0.1 + j * 0.13))
            ev += [("fx", "correct", st + T["rv"] + 0.95)]
            dur = T["rv"] + 2.0
        scenes.append({"kind": "q", "start": st, "dur": dur, "k": k, "n": n, "q": q, "T": T, "extra": extra})
        t += dur
    sig, d = vsay(voice, c["cierre_voz"])
    ev += [("fx", "whoosh", t), ("voice", sig, t + 0.15), ("fx", "applause", t + 0.15 + d * 0.6),
           ("fx", "correct", t + 0.15 + d * 0.55)]
    dur = max(4.0, 0.15 + d + 1.2)
    scenes.append({"kind": "outro", "start": t, "dur": dur, "T": {"voz": (0.15, d, c["cierre_voz"])}})
    return scenes, ev, t + dur


# ------------------------------------------------------------------ recursos

_S = {}


def spr(name, size):
    key = (name, size)
    if key not in _S["spr"]:
        im = Image.open(os.path.join(DECOR, name + ".png")).convert("RGBA")
        k = size / max(im.size)
        _S["spr"][key] = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    return _S["spr"][key]


def _gradient(top, bot, glow):
    yy = np.linspace(0, 1, H)[:, None, None]
    xx = np.linspace(-1, 1, W)[None, :, None]
    g = np.array(top, float) * (1 - yy) + np.array(bot, float) * yy
    r = np.sqrt(xx ** 2 + ((yy - 0.42) * 1.6) ** 2)
    g = g + np.array(glow, float) * np.clip(1 - r, 0, 1) ** 2 * 0.55
    g = np.broadcast_to(g, (H, W, 3))
    return Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def vgrad(w, h, c1, c2):
    yy = np.linspace(0, 1, h)[:, None, None]
    g = np.array(c1, float) * (1 - yy) + np.array(c2, float) * yy
    return Image.fromarray(np.broadcast_to(g, (h, w, 3)).astype(np.uint8), "RGB").convert("RGBA")


def hgrad(w, h, c1, c2):
    xx = np.linspace(0, 1, w)[None, :, None]
    g = np.array(c1, float) * (1 - xx) + np.array(c2, float) * xx
    return Image.fromarray(np.broadcast_to(g, (h, w, 3)).astype(np.uint8), "RGB").convert("RGBA")


def rmask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    return m


def soft_shadow(w, h, r, blur=16, alpha=120, off=14):
    pad = blur * 3
    sh = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + off, pad + w, pad + h + off), r, fill=(0, 0, 0, alpha))
    return sh.filter(ImageFilter.GaussianBlur(blur)), pad


def shadow_text(d, xy, s, f, fill, stroke=4, sfill=DARK, sh=6):
    d.text((xy[0], xy[1] + sh), s, font=f, fill=(0, 0, 0, 110), anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0, 110))
    d.text(xy, s, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=sfill)


def over(im, fn):
    """Dibuja con transparencia mezclando de verdad (en capa aparte) sobre una imagen RGBA."""
    L = Image.new("RGBA", im.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(L, "RGBA"))
    im.alpha_composite(L)


def nice_pill(txt, size, c1, c2, fg, outline=WHITE):
    """Pastilla con degradado, borde blanco, brillo y sombra (se cachea y se escala)."""
    key = ("pill", txt, size, c1, c2, fg)
    if key in _S["cache"]:
        return _S["cache"][key]
    f = tfont(size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tw = int(tmp.textlength(txt, font=f))
    w, h = tw + size * 1.3, int(size * 1.55)
    w = int(w)
    body = vgrad(w, h, c1, c2)
    over(body, lambda dd: dd.rounded_rectangle((10, 6, w - 10, h * 0.45), h // 4, fill=(255, 255, 255, 60)))
    over(body, lambda dd: shadow_text(dd, (w / 2, h / 2 + 3), txt, f, fg, 0, None, 4))
    body.putalpha(rmask(w, h, h // 2))
    ImageDraw.Draw(body).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, outline=outline, width=6)
    sh, pad = soft_shadow(w, h, h // 2, 12, 110, 10)
    sh.alpha_composite(body, (pad, pad))
    _S["cache"][key] = sh
    return sh


PH_BOX, PH_C = (960, 620), (540, 660)   # marco de la foto (y 350-970); la foto va ENTERA dentro, nunca recortada
BORDER = 14


def _photo(name):
    """Foto ENTERA (contain) en un marco blanco 3:2 relleno con la misma foto desenfocada + fondo a pantalla completa."""
    im = Image.open(os.path.join(DECOR, name + ".png")).convert("RGBA")
    bg = Image.new("RGBA", im.size, WHITE + (255,))
    bg.alpha_composite(im)
    im = bg.convert("RGB")
    iw, ih = PH_BOX[0] - 2 * BORDER, PH_BOX[1] - 2 * BORDER
    k2 = max(iw / im.width, ih / im.height)
    fill = im.resize((int(im.width * k2) + 1, int(im.height * k2) + 1), Image.LANCZOS)
    ox, oy = (fill.width - iw) // 2, (fill.height - ih) // 2
    inner = fill.crop((ox, oy, ox + iw, oy + ih)).filter(ImageFilter.GaussianBlur(22))
    inner = Image.blend(inner, Image.new("RGB", inner.size, (30, 20, 50)), 0.25)
    k = min(iw / im.width, ih / im.height)
    fg = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    inner.paste(fg, ((iw - fg.width) // 2, (ih - fg.height) // 2))
    frame = Image.new("RGBA", PH_BOX, (0, 0, 0, 0))
    ImageDraw.Draw(frame).rounded_rectangle((0, 0, PH_BOX[0] - 1, PH_BOX[1] - 1), 46, fill=WHITE)
    frame.paste(inner, (BORDER, BORDER), rmask(iw, ih, 34))
    sh, pad = soft_shadow(PH_BOX[0], PH_BOX[1], 46, 22, 140, 20)
    sh.alpha_composite(frame, (pad, pad))
    k3 = max(W / im.width, H / im.height)
    cv = im.resize((int(im.width * k3) + 1, int(im.height * k3) + 1), Image.LANCZOS)
    ox, oy = (cv.width - W) // 2, (cv.height - H) // 2
    cv = cv.crop((ox, oy, ox + W, oy + H)).filter(ImageFilter.GaussianBlur(30))
    return sh, cv


def _vignette():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.72)) ** 2)
    a = (np.clip(r - 0.45, 0, 1) * 330).clip(0, 200).astype(np.uint8)
    v = Image.new("RGBA", (W, H), (5, 0, 15, 0))
    v.putalpha(Image.fromarray(a, "L"))
    return v


def _bokeh(seed):
    rnd = random.Random(seed)
    lay = Image.new("RGBA", (W, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(26):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H * 2), rnd.uniform(18, 70)
        col = rnd.choice(CONF)
        d.ellipse((x - r, y - r, x + r, y + r), fill=col + (int(rnd.uniform(25, 60)),))
    lay = lay.filter(ImageFilter.GaussianBlur(6))
    d = ImageDraw.Draw(lay)
    for _ in range(40):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H * 2), rnd.uniform(2, 4.5)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 160))
    return lay


def _init(state):
    _S.clear()
    _S.update(state)
    _S["spr"], _S["cache"], _S["card"] = {}, {}, {}
    c = state["c"]
    _S["bg"], _S["fotos"] = {}, {}
    vig = _vignette()
    for k, q in enumerate(c["preguntas"]):
        top, bot, glow = BGS[q.get("fondo", k) % len(BGS)]
        fr, cv = _photo(q["foto"])
        _S["fotos"][k] = fr
        b = Image.blend(cv, _gradient(top, bot, glow).convert("RGB"), 0.5).convert("RGBA")
        b.alpha_composite(vig)
        _S["bg"][k] = b
    o = _gradient((255, 90, 170), (110, 30, 210), (255, 220, 80))
    _S["bg"]["outro"] = o
    _S["bokeh"] = _bokeh(5)
    rnd = random.Random(9)
    _S["burst"] = [(rnd.uniform(-1, 1), rnd.uniform(-1.5, -0.4), rnd.choice(CONF), rnd.uniform(9, 20),
                    rnd.uniform(0, 6.28)) for _ in range(60)]
    _S["logo"] = Image.open(os.path.join(ASSETS, "logo.png")).convert("RGBA")
    # insignia VS
    R = 66
    vsb = Image.new("RGBA", (2 * R + 40, 2 * R + 40), (0, 0, 0, 0))
    disc = vgrad(2 * R, 2 * R, (255, 236, 80), (255, 140, 0))
    m = Image.new("L", (2 * R, 2 * R), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 2 * R - 1, 2 * R - 1), fill=255)
    vd = ImageDraw.Draw(vsb)
    vd.ellipse((8, 14, 2 * R + 32, 2 * R + 38), fill=(0, 0, 0, 110))
    vsb = vsb.filter(ImageFilter.GaussianBlur(6))
    vsb.paste(disc, (20, 20), m)
    over(vsb, lambda vd: vd.chord((34, 30, 6 + 2 * R, 10 + R), 180, 360, fill=(255, 255, 255, 70)))
    over(vsb, lambda vd: shadow_text(vd, (20 + R, 22 + R), "VS", tfont(66), (210, 20, 60), 3, WHITE, 4))
    ImageDraw.Draw(vsb).ellipse((20, 20, 20 + 2 * R, 20 + 2 * R), outline=WHITE, width=8)
    _S["vs"] = vsb


# ------------------------------------------------------------------ fondo

def background(sc, lt, t):
    key = sc["k"] if sc["kind"] == "q" else "outro"
    img = _S["bg"][key].copy()
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy, R = 540, 660, 2300
    base = math.radians(t * 10)
    for j in range(16):
        a0 = base + j * 2 * math.pi / 16
        a1 = a0 + math.pi / 16
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                   (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=(255, 255, 255, 13))
    img.alpha_composite(lay)
    off = int(t * 35) % H
    img.alpha_composite(_S["bokeh"].crop((0, H - off, W, 2 * H - off)))
    return img


# ------------------------------------------------------------------ piezas

def captions(img, d, lt, voz, y=290):
    """Subtítulos grandes estilo TikTok: 1-3 palabras, la que suena salta en amarillo."""
    v0, dur, txt = voz
    words = _words(txt)
    if not words or lt < v0 or lt > v0 + dur + 0.2:
        return
    w_len = [len(w) + 2 for w in words]
    tot = sum(w_len)
    times, acc = [], 0
    for wl in w_len:
        times.append(v0 + dur * acc / tot)
        acc += wl
    cur = max(i for i, tt in enumerate(times) if tt <= lt) if lt >= times[0] else 0
    g0 = (cur // 3) * 3
    chunk = words[g0:g0 + 3]
    f = tfont(72)
    parts = [(w.upper(), i + g0 == cur) for i, w in enumerate(chunk)]
    tw = sum(d.textlength(p + " ", font=f) for p, _ in parts)
    while tw > 960 and f.size > 40:
        f = tfont(f.size - 4)
        tw = sum(d.textlength(p + " ", font=f) for p, _ in parts)
    x = 540 - tw / 2
    for p, on in parts:
        wd = d.textlength(p + " ", font=f)
        ff = tfont(int(f.size * 1.12)) if on else f
        shadow_text(d, (x + d.textlength(p, font=f) / 2, y), p, ff, YEL if on else WHITE, 8, DARK, 7)
        x += wd


def header(img, d, sc, lt):
    k, n = sc["k"], sc["n"]
    extra = sc.get("extra")
    if extra:
        pl = nice_pill("PREGUNTA EXTRA", 62, (200, 60, 255), (255, 50, 140), WHITE)
    else:
        pl = nice_pill("¿QUÉ PREFERIRÍAS?", 62, (255, 70, 120), (255, 150, 30), WHITE)
    s = 1.0
    if k == 0:
        s = 1.15 - 0.15 * ease_out_back(min(1, lt / 0.35))
    paste_c(img, pl, 540, 140, s, angle=1.5 * math.sin(lt * 2))
    # barra de progreso por segmentos
    sw, gap, y = 104, 14, 228
    x0 = 540 - (n * sw + (n - 1) * gap) / 2
    for i in range(n):
        x = x0 + i * (sw + gap)
        rr(d, (x, y - 9, x + sw, y + 9), 9, (0, 0, 0, 90))
        if i < k:
            rr(d, (x, y - 9, x + sw, y + 9), 9, WHITE)
        elif i == k:
            p = min(1.0, lt / max(0.1, sc["dur"]))
            col = (255, 70, 170) if extra else YEL
            rr(d, (x, y - 9, x + max(18, sw * p), y + 9), 9, col)
            rr(d, (x - 3, y - 12, x + sw + 3, y + 12), 12, None, outline=WHITE, width=3)


def photo(img, d, sc, lt):
    fr = _S["fotos"][sc["k"]]
    a = 1.0 if sc["k"] == 0 else min(1.0, pop(lt, 0.0, 0.4))
    if a <= 0.02:
        return
    z = a * (1.0 + 0.025 * math.sin(lt * 1.3))
    paste_c(img, fr, PH_C[0], PH_C[1] + 6 * math.sin(lt * 1.6), z, angle=-1.2 * math.sin(lt * 0.9))


CW, CH, CR = 980, 190, 46
CARD_Y = {"a": 1010, "b": 1310}
VS_Y = 1255
PCT_W = 190          # panel del % a la derecha
BAR_W = CW - PCT_W - 22


def _card_assets(k, which, q):
    key = (k, which)
    if key in _S["card"]:
        return _S["card"][key]
    col = COL_A if which == "a" else COL_B
    light, deep = mix(col, WHITE, 0.32), mix(col, DARK, 0.22)
    full = vgrad(CW, CH, light, deep)
    over(full, lambda fd: fd.rounded_rectangle((16, 8, CW - 16, int(CH * 0.42)), 28, fill=(255, 255, 255, 50)))
    bar = vgrad(CW, CH, mix(col, WHITE, 0.45), col)
    over(bar, lambda bd: bd.rounded_rectangle((16, 8, CW - 16, int(CH * 0.40)), 26, fill=(255, 255, 255, 70)))
    stripes = Image.new("RGBA", (CW + 140, CH), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripes)
    for x in range(-CH, CW + 140, 70):
        sd.polygon([(x, CH), (x + 30, CH), (x + 30 + CH, 0), (x + CH, 0)], fill=(255, 255, 255, 30))
    track = vgrad(CW, CH, mix(col, DARK, 0.72), mix(col, DARK, 0.55))
    over(track, lambda td: td.rounded_rectangle((0, 0, CW - 1, CH - 1), CR, outline=(0, 0, 0, 90), width=12))
    sh, pad = soft_shadow(CW, CH, CR, 16, 130, 14)
    glow = Image.new("RGBA", (CW + 90, CH + 90), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle((30, 30, CW + 60, CH + 60), CR + 16, fill=YEL + (255,))
    glow = glow.filter(ImageFilter.GaussianBlur(16))
    tile = vgrad(150, 150, WHITE, (225, 228, 240))
    tile.putalpha(rmask(150, 150, 38))
    ImageDraw.Draw(tile).rounded_rectangle((0, 0, 149, 149), 38, outline=mix(col, DARK, 0.15), width=5)
    txt = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    tdd = ImageDraw.Draw(txt)
    tx0, tx1 = 196, CW - PCT_W - 24
    f, lines, lh = fit(tdd, q[which]["texto"], tx1 - tx0, CH - 40, 64, 30, 1.04)
    y = CH / 2 - lh * len(lines) / 2 + lh / 2 + 2
    for ln in lines:
        shadow_text(tdd, ((tx0 + tx1) / 2, y), ln, f, WHITE, 3, mix(col, DARK, 0.6), 4)
        y += lh
    A = {"full": full, "bar": bar, "stripes": stripes, "track": track, "sh": sh, "pad": pad, "glow": glow,
         "tile": tile, "txt": txt, "col": col, "mask": rmask(CW, CH, CR)}
    _S["card"][key] = A
    return A


def card_image(A, frac, badge, revealed, win=False, lose=False, t=0.0, bump=1.0):
    col = A["col"]
    if not revealed:
        im = A["full"].copy()
        off = int(t * 60) % 70
        im.alpha_composite(A["stripes"].crop((off, 0, off + CW, CH)))
    else:
        im = A["track"].copy()
        bw = int(BAR_W * max(0.0, min(1.0, frac)))
        if bw > 6:
            part = A["bar"].crop((0, 0, bw, CH))
            off = int(t * 90) % 70
            part.alpha_composite(A["stripes"].crop((off, 0, off + bw, CH)))
            im.paste(part, (0, 0), rmask(bw, CH, CR) if bw > 2 * CR else None)
            over(im, lambda dd: dd.rounded_rectangle((bw - 12, 14, bw - 3, CH - 14), 5, fill=(255, 255, 255, 190)))
    im.alpha_composite(A["txt"])
    if lose:
        im.alpha_composite(Image.new("RGBA", (CW, CH), (10, 10, 20, 95)))
    im.putalpha(A["mask"])
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((0, 0, CW - 1, CH - 1), CR, outline=YEL if win else WHITE, width=9 if win else 7)
    im.alpha_composite(A["tile"], (20, (CH - 150) // 2))
    # panel del %
    px0, py0, px1, py1 = CW - PCT_W - 8, 16, CW - 16, CH - 16
    if revealed:
        if win:
            pnl = vgrad(px1 - px0, py1 - py0, (255, 240, 120), (255, 170, 0))
        else:
            pnl = vgrad(px1 - px0, py1 - py0, WHITE, (225, 228, 240))
        pnl.putalpha(rmask(px1 - px0, py1 - py0, 34))
        im.alpha_composite(pnl, (px0, py0))
        num = badge.rstrip("%")
        fc = DARK if win else mix(col, DARK, 0.25)
        f1 = tfont(int(88 * bump))
        f2 = tfont(int(44 * bump))
        w1 = d.textlength(num, font=f1)
        w2 = d.textlength("%", font=f2)
        cx = (px0 + px1) / 2 - (w1 + w2) / 2
        d.text((cx + w1 / 2, CH / 2 + 4), num, font=f1, fill=fc, anchor="mm")
        d.text((cx + w1 + w2 / 2 + 2, CH / 2 + 18), "%", font=f2, fill=fc, anchor="mm")
    else:
        over(im, lambda dd: dd.rounded_rectangle((px0, py0, px1, py1), 34, fill=(0, 0, 0, 60), outline=(255, 255, 255, 150), width=4))
        over(im, lambda dd: shadow_text(dd, ((px0 + px1) / 2, CH / 2 + 4), "?", tfont(int(100 * bump)), WHITE, 4, mix(col, DARK, 0.5), 5))
    return im


def card(img, d, sc, lt, which):
    q, T = sc["q"], sc["T"]
    opt = q[which]
    A = _card_assets(sc["k"], which, q)
    a = pop(lt, T["cards"] + (0.0 if which == "a" else 0.12), 0.35)
    if sc["k"] == 0:
        a = 1.0
    if a <= 0.02:
        return
    dx = (1 - min(1.0, a)) * (900 if which == "a" else -900)
    rl = lt - T["rv"]
    pct = opt.get("pct", 50)
    other = q["b" if which == "a" else "a"].get("pct", 50)
    revealed = rl >= 0 and not sc["extra"]
    win, lose = revealed and pct > other and rl > 1.15, revealed and pct < other and rl > 1.15
    bump, frac, badge, rev = 1.0, 1.0, "?", False
    if revealed:
        rev = True
        frac = pct / 100 * ease_out(min(1, rl / 1.15))
        badge = f"{int(round(pct * ease_out(min(1, rl / 1.15))))}%"
        if rl > 1.15:
            bump = 1 + 0.22 * math.exp(-(rl - 1.15) * 6)
    elif sc["extra"] and rl >= 0:  # suspense: las barras suben y bajan sin parar
        rev = True
        frac = 0.5 + 0.42 * math.sin(rl * 5 + (0 if which == "a" else math.pi))
        badge = "?"
    s = 1.0 + (0.035 * math.exp(-(rl - 1.15) * 4) if win else 0)
    x0 = 50 + dx
    y0 = CARD_Y[which] + 4 * math.sin(lt * 2.2 + (0 if which == "a" else 1.5))
    cx, cy = x0 + CW / 2, y0 + CH / 2
    if win:
        paste_c(img, A["glow"], cx, cy, s, 0.55 + 0.45 * math.sin(lt * 8))
    paste_c(img, A["sh"], cx, cy, s)
    im = card_image(A, frac, badge, rev, win, lose, lt, bump)
    if sc["extra"] and rl >= 0:
        px0, py0, px1, py1 = CW - PCT_W - 8, 16, CW - 16, CH - 16
        ImageDraw.Draw(im).rounded_rectangle((px0, py0, px1, py1), 34, fill=(255, 70, 170), outline=WHITE, width=4)
        over(im, lambda dd: shadow_text(dd, ((px0 + px1) / 2, CH / 2 + 4), "?", tfont(int(104 * (1 + 0.08 * math.sin(lt * 9)))), WHITE, 4, (120, 0, 60), 5))
    paste_c(img, im, cx, cy, s)
    paste_c(img, spr(opt["icono"], 116), x0 + 20 + 75 - (s - 1) * CW / 2, cy + 3 * math.sin(lt * 4), s)
    if win:
        paste_c(img, spr("corona", 110), x0 + 70, y0 - 30, 1.0, angle=-16 + 6 * math.sin(lt * 5))


def vs(img, d, sc, lt):
    T = sc["T"]
    a = 1.0 if sc["k"] == 0 else min(1.0, pop(lt, T["cards"] + 0.1, 0.3))
    if a <= 0.02:
        return
    pulse = 1 + 0.06 * math.sin(lt * 6)
    paste_c(img, _S["vs"], 540, VS_Y, a * pulse, angle=6 * math.sin(lt * 3))
    if T["cd"] <= lt < T["rv"]:  # cuenta atrás GRANDE encima de la foto (no tapa las opciones)
        n = CD - int(lt - T["cd"])
        pz = 1 + 0.28 * math.exp(-((lt - T["cd"]) % 1) * 6)
        frac = (lt - T["cd"]) / CD
        X, Y, R = 540, PH_C[1], 118 * pz
        d.ellipse((X - R - 22, Y - R - 10, X + R + 22, Y + R + 34), fill=(0, 0, 0, 80))
        d.ellipse((X - R - 30, Y - R - 30, X + R + 30, Y + R + 30), fill=(0, 0, 0, 120))
        d.arc((X - R - 26, Y - R - 26, X + R + 26, Y + R + 26), -90, -90 + 360 * (1 - frac), fill=YEL, width=16)
        d.ellipse((X - R - 4, Y - R - 4, X + R + 4, Y + R + 4), fill=WHITE)
        d.ellipse((X - R + 6, Y - R + 6, X + R - 6, Y + R - 6), fill=(235, 35, 70))
        d.chord((X - R + 24, Y - R + 14, X + R - 24, Y + 10), 180, 360, fill=(255, 255, 255, 50))
        shadow_text(d, (X, Y + 10), str(n), tfont(int(176 * pz)), WHITE, 6, (140, 0, 30), 8)


def bottom(img, d, sc, lt):
    T = sc["T"]
    if T["cd"] <= lt < T["rv"]:
        e = min(1.0, pop(lt, T["cd"], 0.3))
        paste_c(img, nice_pill("¡ELIGE YA!", 58, (255, 236, 80), (255, 160, 0), DARK), 540, 1580,
                e * (1 + 0.06 * math.sin(lt * 10)))
    elif lt >= T["rv"] and sc["extra"]:
        e = min(1.0, pop(lt, T["rv"], 0.35))
        paste_c(img, nice_pill("¡DEFIÉNDELO EN COMENTARIOS!", 46, (255, 100, 190), (220, 30, 120), WHITE), 540, 1580,
                e * (1 + 0.05 * math.sin(lt * 9)))


def extra_intro(img, d, sc, lt):
    """Antes de las tarjetas de la extra: «ROMPEPAREJAS» cae de golpe con corazones rotos."""
    if lt > 1.3:
        return
    k = ease_out(min(1, lt / 0.18))
    s_ = 1.8 - 0.8 * k
    al = 1.0 if lt < 1.0 else max(0.0, 1 - (lt - 1.0) / 0.3)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    f = tfont(int(150 * s_))
    ld.text((540, 1100), "ROMPE", font=f, fill=WHITE, anchor="mm", stroke_width=16, stroke_fill=(120, 0, 60))
    ld.text((540, 1260), "PAREJAS", font=f, fill=(255, 70, 170), anchor="mm", stroke_width=16, stroke_fill=WHITE)
    for j, xx in enumerate((150, 930)):
        paste_c(lay, spr("corazon_roto", 170), xx, 1180 + 15 * math.sin(lt * 8 + j), 1.0, angle=20 * math.sin(lt * 6 + j))
    if al < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v, a_=al: int(v * a_)))
    comp(img, lay, (0, 0))
    if lt < 0.12:
        fl = Image.new("RGBA", (W, H), (255, 70, 170, int(120 * (1 - lt / 0.12)))); comp(img, fl, (0, 0))


def burst_confetti(img, d, sl, cy=VS_Y):
    if 0 < sl < 1.6:
        for vx, vy, col, sz_, ph in _S["burst"][:40]:
            x = 540 + vx * 800 * sl
            y = cy + vy * 900 * sl + 1100 * sl * sl
            w_ = sz_ * abs(math.cos(sl * 6 + ph))
            d.rectangle((x - w_, y - sz_ * 0.45, x + w_, y + sz_ * 0.45), fill=col + (230,))


def draw_q(img, d, sc, lt):
    T = sc["T"]
    header(img, d, sc, lt)
    photo(img, d, sc, lt)
    captions(img, d, lt, T["voz"])
    if sc["extra"]:
        extra_intro(img, d, sc, lt)
    card(img, d, sc, lt, "a")
    card(img, d, sc, lt, "b")
    vs(img, d, sc, lt)
    bottom(img, d, sc, lt)
    if not sc["extra"]:
        burst_confetti(img, d, lt - T["rv"] - 1.15)


def draw_outro(img, d, sc, lt):
    for j, (vx, vy, col, sz_, ph) in enumerate(_S["burst"]):
        x = (vx + 1) / 2 * W + 40 * math.sin(lt * 2 + ph)
        y = ((lt * (220 + sz_ * 12) + j * 97) % (H + 100)) - 50
        w_ = sz_ * abs(math.cos(lt * 4 + ph))
        d.rectangle((x - w_, y - sz_ * 0.45, x + w_, y + sz_ * 0.45), fill=col + (235,))
    for j in range(6):
        x = 120 + j * 170 + 20 * math.sin(lt * 2 + j)
        y = H + 120 - ((lt * 240 + j * 260) % (H + 300))
        paste_c(img, spr("globo", 120), x, y, 1.0, 0.95, angle=8 * math.sin(lt * 2 + j))
    a = pop(lt, 0.0, 0.4)
    y = 300 + (1 - a) * -500
    rr(d, (78, y + 14, 1008, y + 374), 50, (0, 0, 0, 80))
    rr(d, (70, y, 1000, y + 360), 50, WHITE, outline=YEL, width=10)
    d.text((540, y + 110), "¿Y TÚ QUÉ", font=tfont(100), fill=DARK, anchor="mm")
    d.text((540, y + 230), "HABRÍAS ELEGIDO?", font=tfont(84), fill=(236, 40, 80), anchor="mm")
    paste_c(img, spr("pensativo", 150), 130, y - 10 + 10 * math.sin(lt * 5), a, angle=-12)
    paste_c(img, spr("bocadillo", 140), 950, y - 10 + 10 * math.sin(lt * 5 + 1), a, angle=10)
    e = pop(lt, 0.5, 0.4)
    if e > 0:
        paste_c(img, nice_pill("¡COMÉNTALO!", 76, (255, 236, 80), (255, 160, 0), DARK), 540, 790 + (1 - e) * 200,
                min(1.0, e) * (1 + 0.06 * math.sin(lt * 9)))
    b = pop(lt, 1.0, 0.4)
    if b > 0:
        paste_c(img, nice_pill("¡SÍGUEME PARA MÁS!", 62, (255, 90, 120), (210, 20, 70), WHITE), 540, 945 + (1 - b) * 200,
                min(1.0, b) * (1 + 0.07 * math.sin(lt * 9)))
        lg = _S["logo"].resize((max(2, int(320 * b)), max(2, int(320 * b))), Image.LANCZOS)
        comp(img, lg, (540 - lg.width // 2, 1250 - lg.height // 2))
        pz = 1 + 0.15 * abs(math.sin(lt * 5))
        bx, by = 540 + 120 * b, 1250 + 120 * b
        d.ellipse((bx - 45 * pz, by - 45 * pz, bx + 45 * pz, by + 45 * pz), fill=(236, 40, 80), outline=WHITE, width=6)
        d.line([(bx - 22, by), (bx + 22, by)], fill=WHITE, width=9)
        d.line([(bx, by - 22), (bx, by + 22)], fill=WHITE, width=9)
    captions(img, d, lt, sc["T"]["voz"], y=1530)


DRAW = {"q": draw_q, "outro": draw_outro}


def shake(sc, lt):
    if sc["kind"] != "q":
        return 0, 0
    T = sc["T"]
    amp = 0.0
    for t0, a in ((0.0, 0.9 if sc["k"] == 0 or sc["extra"] else 0.3), (T["rv"], 0.8)):
        if 0 <= lt - t0 < 0.35:
            amp = max(amp, a * (1 - (lt - t0) / 0.35))
    if amp <= 0:
        return 0, 0
    return int(math.sin(lt * 80) * 16 * amp), int(math.cos(lt * 67) * 12 * amp)


def render_frame(i):
    t = i / FPS
    scenes = _S["scenes"]
    sc = scenes[-1]
    for s in scenes:
        if s["start"] <= t < s["start"] + s["dur"]:
            sc = s
            break
    lt = t - sc["start"]
    bg = background(sc, lt, t).convert("RGB")
    img = bg.copy()
    d = ImageDraw.Draw(img, "RGBA")
    DRAW[sc["kind"]](img, d, sc, lt)
    dx, dy = shake(sc, lt)
    if dx or dy:
        img = ImageChops.offset(img, dx, dy)
    out_t = sc["dur"] - lt
    if out_t < 0.12 and sc is not scenes[-1]:
        img = Image.blend(bg, img, max(0.0, out_t / 0.12))
    username(img, 1705)
    return img.convert("RGB").tobytes()


# ------------------------------------------------------------------ portada (exagerada)

def portada(c, state, out_dir):
    """Portada exagerada: pantalla partida rojo/azul con rayo, título gigante en 3D, dos medallones enormes y VS."""
    _init(state)
    q = c["preguntas"][0]
    yy, xx = np.mgrid[0:H, 0:W]
    side = (yy - 980) * 1.0 + (xx - 540) * 0.55  # diagonal
    red = vgrad(W, H, (255, 70, 100), (150, 0, 40))
    blue = vgrad(W, H, (40, 140, 255), (0, 30, 130))
    m = Image.fromarray(np.where(side < 0, 255, 0).astype(np.uint8), "L")
    img = blue.copy()
    img.paste(red, (0, 0), m)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for j in range(20):  # rayos desde el centro
        a0 = j * 2 * math.pi / 20
        a1 = a0 + math.pi / 20
        ld.polygon([(540, 1000), (540 + 2300 * math.cos(a0), 1000 + 2300 * math.sin(a0)),
                    (540 + 2300 * math.cos(a1), 1000 + 2300 * math.sin(a1))], fill=(255, 255, 255, 22))
    img.alpha_composite(lay)
    img.alpha_composite(_bokeh(11).crop((0, 0, W, H)))
    img = img.convert("RGBA")
    # rayo blanco en la frontera
    seam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(seam)
    pts = []
    for k in range(9):
        x = -40 + k * 145
        y = 980 - (x - 540) * 0.55 / 1.0 + (28 if k % 2 else -28)
        pts.append((x, y))
    sd.line(pts, fill=(255, 255, 255, 255), width=18, joint="curve")
    glow = seam.filter(ImageFilter.GaussianBlur(18))
    img.alpha_composite(glow)
    img.alpha_composite(glow)
    img.alpha_composite(seam)
    img = img.convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")

    def big_title(txt, y, size, fill):
        f = tfont(size)
        for k in range(14, 0, -2):  # extrusión 3D
            d.text((540 + k * 0.5, y + k), txt, font=f, fill=(40, 0, 30), anchor="mm", stroke_width=14, stroke_fill=(40, 0, 30))
        d.text((540, y), txt, font=f, fill=fill, anchor="mm", stroke_width=14, stroke_fill=DARK)

    big_title("¿QUÉ", 400, 170, WHITE)
    big_title("PREFERIRÍAS?", 560, 158, YEL)

    def medallon(cx, cy, icon, label, col):
        R = 195
        sh, pad = soft_shadow(2 * R, 2 * R, R, 22, 150, 22)
        comp(img, sh, (cx - R - pad, cy - R - pad))
        disc = vgrad(2 * R, 2 * R, WHITE, (220, 225, 240))
        mk = Image.new("L", (2 * R, 2 * R), 0)
        ImageDraw.Draw(mk).ellipse((0, 0, 2 * R - 1, 2 * R - 1), fill=255)
        img.paste(disc, (cx - R, cy - R), mk)
        d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=col, width=16)
        d.ellipse((cx - R - 8, cy - R - 8, cx + R + 8, cy + R + 8), outline=WHITE, width=8)
        ic = Image.open(os.path.join(DECOR, icon + ".png")).convert("RGBA").resize((270, 270), Image.LANCZOS)
        comp(img, ic, (cx - 135, cy - 145))
        pl = nice_pill(label, 60, mix(col, WHITE, 0.25), mix(col, DARK, 0.2), WHITE)
        paste_c(img, pl, cx, cy + R + 10, 1.0)

    medallon(275, 860, q["a"]["icono"], "¿CUÁNDO?", COL_A)
    medallon(805, 1290, q["b"]["icono"], "¿CÓMO?", COL_B)
    paste_c(img, _S["vs"], 545, 1080, 1.5, angle=-8)
    paste_c(img, spr("calavera", 180), 850, 800, 1.0, angle=14)
    paste_c(img, spr("sorpresa", 200), 230, 1330, 1.0, angle=-12)
    # pegatina gancho
    st = nice_pill("LA ÚLTIMA ROMPE PAREJAS", 56, (255, 240, 90), (255, 175, 0), DARK)
    paste_c(img, st, 540, 1585, 1.0, angle=-4)
    paste_c(img, spr("corazon_roto", 120), 930, 1545, 1.0, angle=18)
    username(img, 1760)
    os.makedirs(out_dir, exist_ok=True)
    rgb = img.convert("RGB")
    p916 = os.path.join(out_dir, f"{c['video']}_9x16.png")
    p34 = os.path.join(out_dir, f"{c['video']}_3x4.png")
    rgb.save(p916, optimize=True)
    rgb.crop((0, 260, W, 1700)).save(p34, optimize=True)
    return p916, p34


# ------------------------------------------------------------------ exportación

def render_video(c, voice, out_path, preview=None, workers=None):
    scenes, events, total = build_timeline(c, voice)
    state = {"scenes": scenes, "c": c}
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
    build_audio(events, total, wav)
    frames = int(total * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "23",
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
    return total, [out_path]

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


PH_BOX, PH_C = (1040, 720), (540, 640)   # foto ENTERA (sin recortar) en y 280-1000


def _photo(name):
    """Foto completa (contain, nunca se recorta) con bordes difuminados + versión desenfocada a pantalla completa."""
    im = Image.open(os.path.join(DECOR, name + ".png")).convert("RGBA")
    bg = Image.new("RGBA", im.size, WHITE + (255,))
    bg.alpha_composite(im)
    im = bg.convert("RGB")
    k = min(PH_BOX[0] / im.width, PH_BOX[1] / im.height)
    fg = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", fg.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((22, 22, fg.width - 23, fg.height - 23), 40, fill=255)
    fg.putalpha(m.filter(ImageFilter.GaussianBlur(14)))
    k2 = max(W / im.width, H / im.height)
    cv = im.resize((int(im.width * k2) + 1, int(im.height * k2) + 1), Image.LANCZOS)
    ox, oy = (cv.width - W) // 2, (cv.height - H) // 2
    cv = cv.crop((ox, oy, ox + W, oy + H)).filter(ImageFilter.GaussianBlur(26))
    return fg, cv


def _init(state):
    _S.clear()
    _S.update(state)
    _S["spr"] = {}
    c = state["c"]
    _S["bg"] = {}
    _S["fotos"] = {}
    for k, q in enumerate(c["preguntas"]):
        top, bot, glow = BGS[q.get("fondo", k) % len(BGS)]
        fg, cv = _photo(q["foto"])
        _S.setdefault("fotos", {})[k] = fg
        _S["bg"][k] = Image.blend(cv, _gradient(top, bot, glow).convert("RGB"), 0.55).convert("RGBA")
    _S["bg"]["outro"] = _gradient((255, 90, 170), (110, 30, 210), (255, 220, 80))
    _S["card"] = {}
    rnd = random.Random(9)
    _S["dust"] = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.choice(CONF), rnd.uniform(3, 7), rnd.uniform(30, 90),
                   rnd.uniform(0, 6.28)) for _ in range(50)]
    _S["flo"] = [(rnd.uniform(60, W - 60), rnd.uniform(0, H), rnd.choice((70, 90, 110)), rnd.uniform(30, 70),
                  rnd.uniform(0, 6.28)) for _ in range(8)]
    _S["burst"] = [(rnd.uniform(-1, 1), rnd.uniform(-1.5, -0.4), rnd.choice(CONF), rnd.uniform(9, 20),
                    rnd.uniform(0, 6.28)) for _ in range(60)]
    _S["logo"] = Image.open(os.path.join(ASSETS, "logo.png")).convert("RGBA")


# ------------------------------------------------------------------ fondo

def background(sc, lt, t):
    key = sc["k"] if sc["kind"] == "q" else "outro"
    img = _S["bg"][key].copy()
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy, R = 540, 900, 2300
    base = math.radians(t * 14)
    for j in range(18):
        a0 = base + j * 2 * math.pi / 18
        a1 = a0 + math.pi / 18
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                   (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=(255, 255, 255, 16))
    for x0, y0, col, s, sp, ph in _S["dust"]:
        y = (y0 - sp * t) % (H + 20) - 10
        x = x0 + 25 * math.sin(t * 1.1 + ph)
        d.ellipse((x - s, y - s, x + s, y + s), fill=col + (120,))
    img.alpha_composite(lay)
    if sc["kind"] == "q":
        names = [sc["q"]["a"]["icono"], sc["q"]["b"]["icono"]]
        for j, (x0, y0, sz, sp, ph) in enumerate(_S["flo"]):
            im = spr(names[j % 2], sz)
            y = (y0 - sp * t) % (H + 200) - 100
            x = x0 + 40 * math.sin(t * 0.7 + ph)
            im2 = im.rotate(18 * math.sin(t * 1.4 + ph), resample=Image.BICUBIC, expand=True)
            im2.putalpha(im2.getchannel("A").point(lambda v: int(v * 0.25)))
            img.alpha_composite(im2, (int(x - im2.width / 2), int(y - im2.height / 2)))
    return img


# ------------------------------------------------------------------ piezas

def captions(img, d, lt, voz, y=318):
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
    f = tfont(70)
    parts = [(w.upper(), i + g0 == cur) for i, w in enumerate(chunk)]
    tw = sum(d.textlength(p + " ", font=f) for p, _ in parts)
    while tw > 980 and f.size > 40:
        f = tfont(f.size - 4)
        tw = sum(d.textlength(p + " ", font=f) for p, _ in parts)
    x = 540 - tw / 2
    for p, on in parts:
        wd = d.textlength(p + " ", font=f)
        sz = 1.12 if on else 1.0
        ff = tfont(int(f.size * sz)) if on else f
        d.text((x + d.textlength(p, font=f) / 2, y), p, font=ff, fill=YEL if on else WHITE, anchor="mm",
               stroke_width=10, stroke_fill=DARK)
        x += wd


def header(img, d, sc, lt):
    k, n = sc["k"], sc["n"]
    extra = sc.get("extra")
    s = 1.0
    if k == 0:
        s = 1.12 - 0.12 * ease_out_back(min(1, lt / 0.3))
    lab = "PREGUNTA EXTRA" if extra else "¿QUÉ PREFERIRÍAS?"
    f = tfont(int(78 * s))
    text(d, (540, 165), lab, f, (255, 70, 170) if extra else YEL, 12, DARK, sh=9)
    # puntos de progreso
    xs = [540 + (i - (n - 1) / 2) * 56 for i in range(n)]
    for i, x in enumerate(xs):
        if i < k:
            d.ellipse((x - 11, 234 - 11, x + 11, 234 + 11), fill=WHITE)
        elif i == k:
            r_ = 15 + 2 * math.sin(lt * 8)
            d.ellipse((x - r_, 234 - r_, x + r_, 234 + r_), fill=(255, 70, 170) if i == n - 1 else YEL, outline=WHITE, width=4)
        else:
            d.ellipse((x - 11, 234 - 11, x + 11, 234 + 11), fill=(0, 0, 0, 90), outline=(255, 255, 255, 140), width=3)


def photo(img, d, sc, lt):
    fg = _S["fotos"][sc["k"]]
    a = 1.0 if sc["k"] == 0 else min(1.0, pop(lt, 0.0, 0.4))
    if a <= 0.02:
        return
    z = a * (1.0 + 0.035 * min(1, lt / max(1, sc["dur"])))
    im = fg if abs(z - 1) < 0.003 else fg.resize((max(2, int(fg.width * z)), max(2, int(fg.height * z))), Image.BILINEAR)
    comp(img, im, (PH_C[0] - im.width / 2, PH_C[1] + 5 * math.sin(lt * 1.6) - im.height / 2))


CW, CH = 980, 195
CARD_Y = {"a": 1030, "b": 1330}
VS_Y = 1278


def _card_assets(k, which, q):
    key = (k, which)
    if key in _S["card"]:
        return _S["card"][key]
    col = COL_A if which == "a" else COL_B
    R = CH // 2
    yy = np.linspace(0, 1, CH)[:, None, None]
    top, bot = np.array(mix(col, WHITE, 0.30), float), np.array(mix(col, DARK, 0.18), float)
    g = np.broadcast_to(top * (1 - yy) + bot * yy, (CH, CW, 3))
    fill = Image.fromarray(g.astype(np.uint8), "RGB").convert("RGBA")
    fd = ImageDraw.Draw(fill, "RGBA")
    fd.rounded_rectangle((18, 10, CW - 18, int(CH * 0.42)), 30, fill=(255, 255, 255, 55))
    stripes = Image.new("RGBA", (CW + 140, CH), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripes)
    for x in range(-CH, CW + 140, 70):
        sd.polygon([(x, CH), (x + 32, CH), (x + 32 + CH, 0), (x + CH, 0)], fill=(255, 255, 255, 26))
    track = Image.new("RGBA", (CW, CH), mix(col, DARK, 0.62) + (255,))
    ImageDraw.Draw(track, "RGBA").rounded_rectangle((10, 10, CW - 10, CH - 10), R - 10, outline=(0, 0, 0, 60), width=6)
    mask = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, CW - 1, CH - 1), R, fill=255)
    border = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    ImageDraw.Draw(border).rounded_rectangle((0, 0, CW - 1, CH - 1), R, outline=WHITE, width=8)
    sh = Image.new("RGBA", (CW + 80, CH + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 54, CW + 40, CH + 54), R, fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    glow = Image.new("RGBA", (CW + 80, CH + 80), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle((26, 26, CW + 54, CH + 54), R + 14, fill=YEL + (255,))
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    # texto (zona fija: entre el icono y la chapa del %); si no cabe, se encoge la letra
    txt = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    td = ImageDraw.Draw(txt)
    tx0, tx1 = 200, CW - 190
    f, lines, lh = fit(td, q[which]["texto"], tx1 - tx0, CH - 44, 62, 28, 1.04)
    y = CH / 2 - lh * len(lines) / 2 + lh / 2
    for ln in lines:
        td.text(((tx0 + tx1) / 2, y), ln, font=f, fill=WHITE, anchor="mm", stroke_width=5, stroke_fill=mix(col, DARK, 0.7))
        y += lh
    A = {"fill": fill, "stripes": stripes, "track": track, "mask": mask, "border": border, "sh": sh, "glow": glow,
         "txt": txt, "col": col}
    _S["card"][key] = A
    return A


def card_image(A, frac, badge, win=False, lose=False, t=0.0, bump=1.0):
    col = A["col"]
    im = A["track"].copy()
    bw = int(CW * max(0.0, min(1.0, frac)))
    if bw > 4:
        part = A["fill"].crop((0, 0, bw, CH))
        off = int(t * 90) % 70
        part.alpha_composite(A["stripes"].crop((off, 0, off + bw, CH)))
        im.paste(part, (0, 0))
        if bw < CW - 6:  # punta brillante de la barra
            ImageDraw.Draw(im, "RGBA").rounded_rectangle((bw - 14, 12, bw - 4, CH - 12), 5, fill=(255, 255, 255, 170))
    im.alpha_composite(A["txt"])
    if lose:
        im.alpha_composite(Image.new("RGBA", (CW, CH), (0, 0, 0, 70)))
    im.putalpha(A["mask"])
    im.alpha_composite(A["border"])
    d = ImageDraw.Draw(im, "RGBA")
    # círculo del icono
    d.ellipse((22, CH / 2 - 78, 178, CH / 2 + 78), fill=WHITE, outline=mix(col, DARK, 0.3), width=6)
    # chapa del %
    bx, by, br = CW - 98, CH / 2, 76 * bump
    d.ellipse((bx - br - 6, by - br - 6, bx + br + 6, by + br + 6), fill=(0, 0, 0, 70))
    d.ellipse((bx - br, by - br, bx + br, by + br), fill=YEL if win else WHITE, outline=mix(col, DARK, 0.25), width=7)
    f = tfont(int((64 if len(badge) >= 3 else 80) * bump))
    d.text((bx, by + 4), badge, font=f, fill=DARK if win else mix(col, DARK, 0.2), anchor="mm")
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
    x0 = 50 + dx
    y0 = CARD_Y[which] + 5 * math.sin(lt * 2.2 + (0 if which == "a" else 1.5))
    rl = lt - T["rv"]
    pct = opt.get("pct", 50)
    other = q["b" if which == "a" else "a"].get("pct", 50)
    revealed = rl >= 0 and not sc["extra"]
    win, lose = revealed and pct > other and rl > 1.15, revealed and pct < other and rl > 1.15
    bump = 1.0
    if revealed:
        if rl < 0.15:
            frac = 1 - rl / 0.15
        else:
            frac = pct / 100 * ease_out(min(1, (rl - 0.15) / 1.0))
        num = int(round(pct * ease_out(min(1, max(0, rl - 0.15) / 1.0))))
        badge = f"{num}%"
        if rl > 1.15:
            bump = 1 + 0.25 * math.exp(-(rl - 1.15) * 6)
    elif sc["extra"] and rl >= 0:
        frac = 0.5 + 0.42 * math.sin(rl * 5 + (0 if which == "a" else math.pi))
        badge = "?"
        bump = 1 + 0.08 * math.sin(lt * 9 + (0 if which == "a" else 1.5))
    else:
        frac, badge = 1.0, "?"
    if win:
        g = 0.55 + 0.45 * math.sin(lt * 8)
        paste_c(img, A["glow"], x0 + CW / 2, y0 + CH / 2, 1.0, g)
    comp(img, A["sh"], (x0 - 40, y0 - 40))
    comp(img, card_image(A, frac, badge, win, lose, lt, bump), (x0, y0))
    paste_c(img, spr(opt["icono"], 118), x0 + 100, y0 + CH / 2 + 4 * math.sin(lt * 4), 1.0)
    if win:
        paste_c(img, spr("corona", 120), x0 + CW - 98, y0 - 40, 1.0, angle=8 * math.sin(lt * 5))


def vs(img, d, sc, lt):
    T = sc["T"]
    cx, cy = 540, VS_Y
    a = pop(lt, T["cards"] + 0.1, 0.3)
    if sc["k"] == 0:
        a = max(a, 0.9)
    if a <= 0.02:
        return
    counting = T["cd"] <= lt < T["rv"]
    R = 60 * min(1.0, a)
    d.ellipse((cx - R - 9, cy - R - 9, cx + R + 9, cy + R + 9), fill=WHITE)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=DARK)
    d.text((cx, cy + 4), "VS", font=tfont(max(8, int(60 * min(1.0, a)))), fill=YEL, anchor="mm")
    if counting:  # cuenta atrás GRANDE encima de la foto (no tapa las opciones)
        n = CD - int(lt - T["cd"])
        pz = 1 + 0.3 * math.exp(-((lt - T["cd"]) % 1) * 6)
        frac = (lt - T["cd"]) / CD
        X, Y, R = 540, PH_C[1], 120 * pz
        d.ellipse((X - R - 16, Y - R - 10, X + R + 16, Y + R + 22), fill=(0, 0, 0, 90))
        d.ellipse((X - R - 14, Y - R - 14, X + R + 14, Y + R + 14), fill=WHITE)
        d.ellipse((X - R, Y - R, X + R, Y + R), fill=(230, 30, 60))
        d.arc((X - R - 30, Y - R - 30, X + R + 30, Y + R + 30), -90, -90 + 360 * (1 - frac), fill=YEL, width=14)
        d.text((X, Y + 8), str(n), font=tfont(int(170 * pz)), fill=WHITE, anchor="mm", stroke_width=6, stroke_fill=(140, 0, 30))


def bottom(img, d, sc, lt):
    T = sc["T"]
    if T["cd"] <= lt < T["rv"]:
        e = pop(lt, T["cd"], 0.3)
        pulse = 1 + 0.07 * math.sin(lt * 10)
        pill(d, 540, 1598, "¡ELIGE YA!", int(60 * e * pulse), YEL, DARK, pad=(38, 12))
    elif lt >= T["rv"] and sc["extra"]:
        e = pop(lt, T["rv"], 0.35)
        pulse = 1 + 0.06 * math.sin(lt * 9)
        pill(d, 540, 1598, "¡DEFIÉNDELO EN COMENTARIOS!", int(46 * e * pulse), (255, 70, 170), WHITE, pad=(32, 12))


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
        pulse = 1 + 0.06 * math.sin(lt * 9)
        pill(d, 540, 790 + (1 - e) * 200, "¡COMÉNTALO!", int(78 * pulse * e), YEL, DARK, pad=(48, 20))
    b = pop(lt, 1.0, 0.4)
    if b > 0:
        pulse = 1 + 0.07 * math.sin(lt * 9)
        pill(d, 540, 935 + (1 - b) * 200, "¡SÍGUEME PARA MÁS!", int(64 * pulse * b), (236, 40, 80), WHITE, pad=(40, 18))
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
    _init(state)
    q = c["preguntas"][0]
    img = Image.blend(_S["bg"][0].convert("RGB"), _gradient((150, 0, 40), (15, 0, 10), (255, 40, 80)).convert("RGB"), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy, R = 540, 900, 2300
    for j in range(18):
        a0 = j * 2 * math.pi / 18
        a1 = a0 + math.pi / 18
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                   (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=(255, 255, 255, 22))
    text(d, (540, 470), "¿QUÉ", tfont(150), WHITE, 16, DARK, sh=12)
    text(d, (540, 615), "PREFERIRÍAS?", tfont(150), YEL, 16, DARK, sh=12)
    sc = {"kind": "q", "k": 0, "dur": 10, "q": q, "T": {"cards": 0, "cd": 99, "rv": 99}, "extra": False, "n": 6}
    # fondo: la foto desenfocada; encima la foto ENTERA, grande y sin recortar
    fg = _S["fotos"][0]
    k = min(1000 / fg.width, 440 / fg.height)
    fgp = fg.resize((int(fg.width * k), int(fg.height * k)), Image.LANCZOS)
    comp(img, fgp, (540 - fgp.width / 2, 925 - fgp.height / 2))
    for which, y in (("a", 1170), ("b", 1450)):
        A = _card_assets(0, which, q)
        comp(img, A["sh"], (50 - 40, y - 40))
        comp(img, card_image(A, 1.0, "?"), (50, y))
        paste_c(img, spr(q[which]["icono"], 118), 150, y + CH / 2, 1.0)
    vy = 1408
    d.ellipse((540 - 84, vy - 84, 540 + 84, vy + 84), fill=WHITE)
    d.ellipse((540 - 72, vy - 72, 540 + 72, vy + 72), fill=DARK)
    d.text((540, vy + 4), "VS", font=tfont(84), fill=YEL, anchor="mm")
    paste_c(img, spr("sorpresa", 210), 950, 930, 1.0, angle=12)
    paste_c(img, spr("pensativo", 200), 130, 930, 1.0, angle=-10)
    lay = Image.new("RGBA", (880, 150), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle((6, 6, 874, 144), 30, fill=(255, 214, 0), outline=WHITE, width=8)
    ld.text((440, 80), c.get("portada", {}).get("pegatina", "LA EXTRA ROMPE PAREJAS"), font=tfont(70), fill=DARK, anchor="mm")
    lay = lay.rotate(-4, resample=Image.BICUBIC, expand=True)
    comp(img, lay, (540 - lay.width // 2, 330 - lay.height // 2))
    username(img, 1760)
    os.makedirs(out_dir, exist_ok=True)
    rgb = img.convert("RGB")
    p916 = os.path.join(out_dir, f"{c['video']}_9x16.png")
    p34 = os.path.join(out_dir, f"{c['video']}_3x4.png")
    rgb.save(p916, optimize=True)
    rgb.crop((0, 240, W, 1680)).save(p34, optimize=True)
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

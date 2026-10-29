"""Vídeo de TEST DE PERSONALIDAD (Hora del Quiz ⚡).

Reutiliza las piezas del quiz (tipografías, voz ElevenLabs con caché, efectos, música, mezcla y
exportación) con una estructura propia: gancho → 9 preguntas sin respuesta correcta (cuenta atrás de
5 s y sello «¡APÚNTALA!») → resultados por letra → llamada a la acción.
Colores de marca pedidos por el usuario: amarillo, turquesa, morado y negro.
"""

import math
import os
import random
import re
import subprocess
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import audio
from .render import (FPS, USUARIO, USER_Y, W, H, ease_in, ease_out, ease_out_back, fit, font, tfont,
                     with_alpha, _shape)

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
IMGS = os.path.join(ASSETS, "personalidad")

YEL = (255, 212, 0)
TURQ = (0, 222, 205)
PURP = (138, 58, 255)
PURP_D = (58, 18, 128)
BLACK = (14, 8, 26)
WHITE = (255, 255, 255)
PINK = (255, 64, 160)
RED = (255, 50, 70)
# tarjetas A-D: (fondo, texto, borde)
OPT = [(YEL, BLACK, (190, 140, 0)), (TURQ, BLACK, (0, 150, 140)), (PURP, WHITE, (90, 30, 190)),
       ((26, 18, 44), WHITE, YEL)]
LETTERS = "ABCD"
COUNTDOWN = 5
BPM = 118
TONO = 270  # tono registrado en paletas_usadas.json (morado de marca)

SIDE_EMOJI = ["pensativo", "ojos", "mente_explota"]


# ---------------------------------------------------------------- subtítulos palabra a palabra

PUNCT = re.compile(r"[,.!?:;…]$")


def align_words(text, sig, dur):
    """Tiempo (inicio, fin) de cada palabra. Usa las pausas reales del audio para colocar los signos
    de puntuación y reparte las palabras de cada tramo según su longitud."""
    words = text.split()
    wts = [len(w) + 1 for w in words]
    bounds = [i for i, w in enumerate(words[:-1]) if PUNCT.search(w)]
    gaps = []
    if sig is not None and len(sig) > 0:
        fr = int(0.01 * audio.SR)
        n = len(sig) // fr
        e = np.sqrt(np.mean(sig[: n * fr].reshape(n, fr) ** 2, axis=1))
        silent = e < max(e) * 0.07
        k = 0
        while k < n:
            if silent[k]:
                j = k
                while j < n and silent[j]:
                    j += 1
                if j - k >= 7 and k > 5 and j < n - 5:
                    gaps.append((k * 0.01, j * 0.01))
                k = j
            else:
                k += 1
    tot = sum(wts)
    cum = np.cumsum(wts)
    cuts = []  # (índice de palabra, inicio de pausa, fin de pausa)
    used = set()
    for b in bounds:
        exp = dur * cum[b] / tot
        best = None
        for gi, (ga, gb) in enumerate(gaps):
            if gi in used:
                continue
            dist = abs((ga + gb) / 2 - exp)
            if dist < max(0.6, dur * 0.2) and (best is None or dist < best[0]):
                best = (dist, gi)
        if best:
            used.add(best[1])
            cuts.append((b, gaps[best[1]][0], gaps[best[1]][1]))
    cuts.sort(key=lambda c: c[1])
    # quita cortes desordenados
    clean, last_b = [], -1
    for c_ in cuts:
        if c_[0] > last_b:
            clean.append(c_)
            last_b = c_[0]
    out = [None] * len(words)
    seg_start_w, seg_t = 0, 0.0
    for b, ga, gb in clean + [(len(words) - 1, dur, dur)]:
        ws = list(range(seg_start_w, b + 1))
        span = max(0.05, ga - seg_t)
        sw = sum(wts[i] for i in ws)
        t = seg_t
        for i in ws:
            d = span * wts[i] / sw
            out[i] = (t, t + d)
            t += d
        seg_start_w, seg_t = b + 1, gb
    return words, out


def caption_chunks(words, times, at, maxw=3, maxc=17):
    """Agrupa palabras en golpes de 1-3 palabras (corta en signos de puntuación)."""
    res, cur = [], []
    for w, (a, b) in zip(words, times):
        cur.append((w, at + a, at + b))
        txt = " ".join(x[0] for x in cur)
        if len(cur) >= maxw or len(txt) >= maxc or PUNCT.search(w):
            res.append(cur)
            cur = []
    if cur:
        res.append(cur)
    out = []
    for k, ch in enumerate(res):
        start = ch[0][1]
        end = res[k + 1][0][1] if k + 1 < len(res) else ch[-1][2] + 0.25
        out.append({"start": start, "end": end, "words": ch})
    return out


# ---------------------------------------------------------------- línea de tiempo

REACT_STYLE = "[playful, laughing a little]"


def build_timeline(c, voice):
    events, subs, scenes = [], [], []

    def fx(name, at, gain=1.0):
        events.append(("fx", name, at, gain))

    def speak(text, at, show_subs=True, style=None):
        old = voice.style
        if style:
            voice.style = style
        sig, dur = voice.say(text)
        voice.style = old
        events.append(("voice", sig, at, 1.0))
        words, times = align_words(text, sig, dur)
        if show_subs:
            subs.extend(caption_chunks(words, times, at))
        return dur, [(w, at + a, at + b) for w, (a, b) in zip(words, times)]

    t = 0.0
    # ---- gancho: el titular cae al ritmo de las palabras
    v0 = 0.45
    fx("impact", 0.0, 1.0)
    fx("whoosh", 0.0, 0.5)
    dv, wt = speak(c["intro"]["voz"], v0)
    nt = sum(len(l[0].split()) for l in c["intro"]["titulo"])
    title_times, k = [], 0
    for l in c["intro"]["titulo"]:
        n = len(l[0].split())
        title_times.append(wt[min(k, len(wt) - 1)][1])
        k += n
    for tt in title_times:
        fx("pop", tt, 0.6)
    del nt
    dur = v0 + dv + 0.35
    scenes.append({"kind": "intro", "start": t, "dur": dur, "title_times": [x - t for x in title_times],
                   "pill_t": title_times[-1] + 0.5})
    t += dur

    # ---- preguntas
    nq = len(c["preguntas"])
    for i, q in enumerate(c["preguntas"]):
        sc = {"kind": "q", "i": i, "n": nq, "q": q, "start": t}
        fx("whoosh", t, 0.5)
        for k in range(4):
            fx("pop", t + 0.5 + 0.08 * k, 0.3)
        vq = 0.3
        dq, qwords = speak(q["pregunta"], t + vq, show_subs=False)  # la propia tarjeta hace de subtítulo
        sc["qwords"] = [(w, a - t, b - t) for w, a, b in qwords]
        cd = vq + dq + 0.2
        sc["cd_start"] = cd
        fx("riser", t + cd, 0.5)
        events.append(("boost", t + cd, t + cd + COUNTDOWN, 0))
        for k in range(COUNTDOWN):
            tk = t + cd + k
            fx("tick_high" if k >= COUNTDOWN - 2 else "tick", tk, 1.25)
            fx("heart", tk, 0.75)
            if k >= COUNTDOWN - 2:
                fx("tock", tk + 0.5, 0.9)
        cend = cd + COUNTDOWN
        sc["cd_end"] = cend
        fx("buzz", t + cend, 0.45)
        fx("boing", t + cend + 0.02, 0.8)
        dr, _ = speak(q["reaccion"], t + cend + 0.12, show_subs=True, style=REACT_STYLE)
        sc["react_end"] = cend + 0.12 + dr
        sc["dur"] = cend + max(1.0, 0.12 + dr + 0.05)
        scenes.append(sc)
        t += sc["dur"]

    # ---- resultados
    r = c["resultado"]
    sc = {"kind": "res", "start": t, "r": r}
    fx("drum", t, 0.8)
    fx("riser_short", t, 0.5)
    rev = 1.0
    fx("impact", t + rev, 0.9)
    fx("correct", t + rev, 0.8)
    fx("applause", t + rev, 0.5)
    sc["reveal"] = rev
    a = rev + 0.35
    if r.get("voz"):
        d, _ = speak(r["voz"], t + a)
        a += d + 0.15
    sc["perfiles"] = []
    for p in r["perfiles"]:
        fx("pop", t + a - 0.1, 0.6)
        fx("whoosh", t + a - 0.2, 0.35)
        d, _ = speak(p["voz"], t + a)
        sc["perfiles"].append((a - 0.15, a, a + d))
        a += d + 0.12
    sc["tie_start"] = a - 0.1
    fx("boing", t + a - 0.05, 0.6)
    a += 1.4
    sc["dur"] = a
    scenes.append(sc)
    t += a

    # ---- llamada a la acción
    cc = c["cierre"]
    sc = {"kind": "cta", "start": t, "c": cc}
    fx("whoosh", t, 0.6)
    fx("impact", t + 0.05, 0.8)
    v = 0.45
    d, _ = speak(cc["voz"], t + v)
    sc["vstart"], sc["vdur"] = v, d
    sc["follow"] = v + d * 0.82
    sc["typing"] = v + 1.2
    fx("correct", t + sc["follow"], 0.55)
    fx("applause", t + v + d - 0.2, 0.55)
    for k in range(16):
        fx("type", t + sc["typing"] + 0.06 * k, 0.35)
    sc["dur"] = v + d + 1.4
    scenes.append(sc)
    t += sc["dur"]
    return scenes, events, subs, t


# ---------------------------------------------------------------- audio

def sfx_impact():
    t = np.arange(int(0.7 * audio.SR)) / audio.SR
    f = 40 + 90 * np.exp(-t * 12)
    boom = np.sin(2 * np.pi * np.cumsum(f) / audio.SR) * np.exp(-t * 5)
    noise = np.random.default_rng(2).standard_normal(len(t)) * np.exp(-t * 30) * 0.4
    return 0.9 * (boom + noise)


def sfx_drum(dur=1.4):
    """Redoble de tambor que acelera (golpes de ruido filtrado)."""
    n = int(dur * audio.SR)
    out = np.zeros(n)
    rng = np.random.default_rng(8)
    hit = rng.standard_normal(int(0.05 * audio.SR)) * np.exp(-np.arange(int(0.05 * audio.SR)) / audio.SR * 70)
    tt = 0.0
    while tt < dur - 0.05:
        s = int(tt * audio.SR)
        g = 0.3 + 0.7 * tt / dur
        out[s:s + len(hit)] += g * hit[: n - s]
        tt += 0.09 - 0.06 * tt / dur
    return 0.35 * out


def sfx_stamp():
    t = np.arange(int(0.25 * audio.SR)) / audio.SR
    thump = np.sin(2 * np.pi * (90 + 160 * np.exp(-t * 40)) * t) * np.exp(-t * 18)
    return 0.8 * thump


def sfx_boing():
    t = np.arange(int(0.45 * audio.SR)) / audio.SR
    f = 180 + 260 * np.exp(-t * 9) * (1 + 0.35 * np.sin(2 * np.pi * 14 * t))
    return 0.55 * np.sin(2 * np.pi * np.cumsum(f) / audio.SR) * np.exp(-t * 6)


def build_audio(events, total, path):
    mix = audio.Mixer(total)
    fx = {"whoosh": audio.sfx_whoosh(), "pop": audio.sfx_pop(), "tick": audio.sfx_tick(),
          "tick_high": audio.sfx_tick(True), "tock": audio.sfx_tock(), "heart": audio.sfx_heartbeat(),
          "riser": audio.sfx_riser(COUNTDOWN), "riser_short": audio.sfx_riser(1.4), "buzz": audio.sfx_buzz_end(),
          "correct": audio.sfx_correct(), "applause": audio.sfx_applause(), "chime": audio.sfx_correct(),
          "impact": sfx_impact(), "drum": sfx_drum(), "stamp": sfx_stamp(), "boing": sfx_boing(), "type": audio.sfx_tick() * 0.5}
    boosts = []
    for ev in events:
        if ev[0] == "fx":
            mix.add_fx(fx[ev[1]], ev[2], ev[3])
        elif ev[0] == "voice" and ev[1] is not None:
            mix.add_voice(ev[1], ev[2], 1.0)
        elif ev[0] == "boost":
            boosts.append((ev[1], ev[2]))
    music = audio.music(total, bpm=BPM, style="pop")
    audio.write_wav(path, mix.render(music, music_gain=0.26, boosts=boosts, boost=1.3))


# ---------------------------------------------------------------- utilidades de dibujo

_S = {}


def _img(name, size):
    key = (name, size)
    if key not in _S["imgcache"]:
        im = Image.open(os.path.join(IMGS, name if name.endswith(".png") else name + ".png")).convert("RGBA")
        k = size / max(im.size)
        _S["imgcache"][key] = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    return _S["imgcache"][key]


def paste_c(base, im, cx, cy, scale=1.0, ang=0.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if ang:
        im = im.rotate(ang, Image.BICUBIC, expand=True)
    if alpha < 1.0:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda a: int(a * alpha)))
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def bolt(d, cx, cy, s, col, outline=None):
    """Rayo ⚡ dibujado (la tipografía no tiene el emoji)."""
    pts = [(0.15, -1), (-0.55, 0.12), (-0.05, 0.12), (-0.25, 1), (0.55, -0.2), (0.05, -0.2), (0.35, -1)]
    P = [(cx + x * s, cy + y * s) for x, y in pts]
    if outline:
        d.polygon(P, fill=col, outline=outline, width=max(2, int(s / 10)))
    else:
        d.polygon(P, fill=col)


def text_sprite(lines, size, fill_map, stroke=12, shadow=True, maxw=960):
    """Titular con contorno negro grueso y sombra. lines = [(texto, 'w'|'y'|'t')]."""
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    sizes = []
    for txt, _ in lines:
        s = size
        while tmp.textlength(txt, font=tfont(s)) > maxw and s > 40:
            s -= 4
        sizes.append(s)
    h = int(sum(s * 1.02 for s in sizes)) + 60
    spr = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(spr)
    y = 30
    for (txt, c), s in zip(lines, sizes):
        col = fill_map[c]
        if shadow:
            d.text((W / 2 + 8, y + s / 2 + 12), txt, font=tfont(s), anchor="mm", fill=(0, 0, 0, 150),
                   stroke_width=stroke + 2, stroke_fill=(0, 0, 0, 150))
        d.text((W / 2, y + s / 2), txt, font=tfont(s), anchor="mm", fill=col, stroke_width=stroke,
               stroke_fill=BLACK)
        y += s * 1.02
    return spr


FILL = {"w": WHITE, "y": YEL, "t": TURQ, "p": PINK}


def pill(d, cx, cy, text, size, bg, fg, pad=(34, 16), outline=None):
    f = tfont(size)
    w = d.textlength(text, font=f)
    box = (cx - w / 2 - pad[0], cy - size / 2 - pad[1], cx + w / 2 + pad[0], cy + size / 2 + pad[1])
    r = (box[3] - box[1]) / 2
    d.rounded_rectangle((box[0], box[1] + 7, box[2], box[3] + 7), r, fill=(0, 0, 0, 90))
    d.rounded_rectangle(box, r, fill=bg, outline=outline, width=4 if outline else 0)
    d.text((cx, cy + size * 0.04), text, font=f, fill=fg, anchor="mm")
    return box


# ---------------------------------------------------------------- inicialización (cada proceso)

def _init(state):
    _S.clear()
    _S.update(state)
    _S["imgcache"] = {}
    _S["cache"] = {}
    # degradado base morado → negro con banda turquesa suave
    yy = np.linspace(0, 1, H)[:, None, None]
    xx = np.linspace(0, 1, W)[None, :, None]
    top = np.array(PURP_D, float)
    mid = np.array((96, 30, 190), float)
    bot = np.array(BLACK, float)
    g = np.where(yy < 0.45, top + (mid - top) * (yy / 0.45), mid + (bot - mid) * ((yy - 0.45) / 0.55))
    g = g + np.array(TURQ, float) * 0.10 * np.exp(-((xx - 0.2) ** 2 + (yy - 0.25) ** 2) / 0.05)
    _S["bg"] = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8).repeat(1, 1), "RGB").convert("RGBA")

    def glow(col, r, a):
        gy, gx = np.mgrid[0:2 * r, 0:2 * r]
        gr = np.sqrt((gx - r) ** 2 + (gy - r) ** 2) / r
        im = Image.new("RGBA", (2 * r, 2 * r), col + (0,))
        im.putalpha(Image.fromarray((np.clip(1 - gr, 0, 1) ** 2 * a).astype(np.uint8), "L"))
        return im

    _S["glow_t"] = glow(TURQ, 420, 120)
    _S["glow_y"] = glow(YEL, 360, 80)
    _S["glow_p"] = glow(PINK, 380, 90)
    _S["glow_w"] = glow(WHITE, 260, 160)
    rnd = random.Random(42)
    # símbolos flotando: letras A-D, interrogaciones, rayos y estrellas
    syms = []
    cols = [YEL, TURQ, PINK, WHITE, PURP]
    for k in range(22):
        kind = rnd.choice(["A", "B", "C", "D", "?", "?", "bolt", "star", "ring"])
        size = rnd.randint(46, 110)
        col = rnd.choice(cols)
        spr = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(spr)
        a = rnd.uniform(0.22, 0.42)
        if kind == "bolt":
            bolt(d, size, size, size * 0.8, with_alpha(YEL if rnd.random() < 0.7 else TURQ, a + 0.1))
        elif kind == "star":
            _shape(d, 3, size, size, size * 0.7, rnd.uniform(0, 6), with_alpha(col, a))
        elif kind == "ring":
            _shape(d, 0, size, size, size * 0.55, 0, with_alpha(col, a))
        else:
            d.text((size, size), kind, font=tfont(int(size * 1.2)), anchor="mm", fill=with_alpha(col, a))
        syms.append((spr, rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(25, 70), rnd.uniform(-25, 25),
                     rnd.uniform(0, 6.28)))
    _S["syms"] = syms
    _S["sparks"] = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(2, 5), rnd.uniform(0, 6.28),
                     rnd.uniform(1.5, 4)) for _ in range(60)]
    _S["confetti"] = [(rnd.uniform(-1, 1), rnd.uniform(-1.5, -0.5), rnd.choice([YEL, TURQ, PINK, WHITE, PURP]),
                       rnd.uniform(10, 22), rnd.uniform(0, 6.28)) for _ in range(90)]
    lp = os.path.join(ASSETS, "logo.png")
    logo = Image.open(lp).convert("RGBA")
    _S["logo_s"] = logo.resize((92, 92), Image.LANCZOS)
    _S["logo_b"] = logo.resize((300, 300), Image.LANCZOS)


# ---------------------------------------------------------------- fondo

def background(t):
    img = _S["bg"].copy()
    beat = (t % (60 / BPM)) / (60 / BPM)
    pulse = math.exp(-beat * 5)
    # brillos que se desplazan
    img.alpha_composite(_S["glow_t"], (int(-220 + 120 * math.sin(t * 0.35)), int(180 + 90 * math.cos(t * 0.3))))
    img.alpha_composite(_S["glow_p"], (int(560 + 110 * math.cos(t * 0.27)), int(1150 + 120 * math.sin(t * 0.33))))
    img.alpha_composite(_S["glow_y"], (int(300 + 200 * math.sin(t * 0.21)), int(650 + 160 * math.sin(t * 0.4 + 1))))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # rayos de concurso que giran y laten con la música
    cx, cy, R = 540, 820, 2300
    base = math.radians(t * 10)
    a_ray = int(14 + 16 * pulse)
    for k in range(16):
        a0 = base + k * 2 * math.pi / 16
        a1 = a0 + math.pi / 16
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                   (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=(255, 255, 255, a_ray))
    # chispas que parpadean
    for x, y, s, ph, sp in _S["sparks"]:
        a = (math.sin(t * sp + ph) + 1) / 2
        if a > 0.55:
            ss = s * (0.6 + a)
            d.ellipse((x - ss, y - ss, x + ss, y + ss), fill=(255, 255, 255, int(200 * (a - 0.5) * 2)))
    img.alpha_composite(layer)
    # símbolos flotando (suben girando)
    for spr, x0, y0, sp, rot, ph in _S["syms"]:
        y = (y0 - sp * t) % (H + 240) - 120
        x = x0 + 40 * math.sin(t * 0.8 + ph)
        paste_c(img, spr, x, y, 1.0 + 0.05 * pulse, rot * t * 0.3 + 15 * math.sin(t + ph))
    return img


# ---------------------------------------------------------------- piezas fijas

def logo_badge(img, alpha=1.0):
    layer = Image.new("RGBA", (420, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    tw = d.textlength("HORA DEL QUIZ", font=tfont(36))
    d.rounded_rectangle((4, 14, 112 + tw + 62, 106), 46, fill=(0, 0, 0, 110))
    layer.alpha_composite(_S["logo_s"], (8, 14))
    d.text((112, 60), "HORA DEL QUIZ", font=tfont(36), fill=WHITE, anchor="lm")
    bolt(d, 112 + tw + 28, 58, 26, YEL)
    paste_c(img, layer, 70 + 210, 205, alpha=alpha)


def username(img):
    d = ImageDraw.Draw(img)
    f = font(48)
    w = d.textlength(USUARIO, font=f)
    box = (540 - w / 2 - 32, USER_Y - 42, 540 + w / 2 + 32, USER_Y + 42)
    d.rounded_rectangle(box, 42, fill=(0, 0, 0, 130))
    d.text((540, USER_Y), USUARIO, font=f, fill=WHITE, anchor="mm")


def subtitles(img, t):
    """Subtítulos estilo TikTok: 1-3 palabras gordas con contorno; la palabra que suena salta en color."""
    for k, ch in enumerate(_S["subs"]):
        if not (ch["start"] <= t < ch["end"]):
            continue
        words = [w.upper() for w, _, _ in ch["words"]]
        size = 84
        tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        sp = 22
        while True:
            f = tfont(size)
            ws = [tmp.textlength(w, font=f) for w in words]
            total = sum(ws) + sp * (len(words) - 1)
            if total <= 940 or size <= 48:
                break
            size -= 4
        hl = YEL if k % 2 == 0 else TURQ
        acts = [a <= t < b + 0.05 for _, a, b in ch["words"]]
        sizes = [int(size * 1.12) if ac else size for ac in acts]
        wds = [tmp.textlength(w, font=tfont(sz)) for w, sz in zip(words, sizes)]
        total = sum(wds) + sp * (len(words) - 1)
        lay = Image.new("RGBA", (W + 200, 240), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        x = (W + 200) / 2 - total / 2
        for (w, a, b), txt, wd, sz, active in zip(ch["words"], words, wds, sizes, acts):
            fill = hl if active else WHITE
            cx = x + wd / 2
            yoff = -10 * math.sin(min(1, (t - a) / 0.14) * math.pi) if active else 0
            d.text((cx + 5, 128 + 7 + yoff), txt, font=tfont(sz), anchor="mm", fill=(0, 0, 0, 170),
                   stroke_width=11, stroke_fill=(0, 0, 0, 170))
            d.text((cx, 128 + yoff), txt, font=tfont(sz), anchor="mm", fill=fill, stroke_width=10,
                   stroke_fill=BLACK)
            x += wd + sp
        p = ease_out_back(min(1, (t - ch["start"]) / 0.16))
        paste_c(img, lay, 540, 1470, 0.75 + 0.25 * p, 3 if k % 2 else -3)
        break


def flash(img, a):
    if a > 0.01:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * min(1, a)))))


def confetti(img, lt, cx=540, cy=700, power=1.0):
    if lt < 0 or lt > 3.2:
        return
    d = ImageDraw.Draw(img)
    for vx, vy, col, s, ph in _S["confetti"]:
        x = cx + vx * 900 * power * lt
        y = cy + vy * 1300 * power * lt + 1400 * lt * lt
        if -50 < y < H + 50:
            a = ph + lt * 9
            w, h = s, s * 0.45 * abs(math.cos(a))
            ca, sa = math.cos(ph + lt * 3), math.sin(ph + lt * 3)
            pts = [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in
                   ((-w, -h), (w, -h), (w, h), (-w, h))]
            d.polygon(pts, fill=col + (int(255 * max(0, 1 - lt / 3.2)),))


# ---------------------------------------------------------------- escena: gancho

def draw_intro(img, sc, lt):
    if "intro_title" not in _S["cache"]:
        _S["cache"]["intro_title"] = [text_sprite([l], 150 if l[1] == "y" else 118, FILL, stroke=12)
                                      for l in [tuple(x) for x in _S["c"]["intro"]["titulo"]]]
    sprites = _S["cache"]["intro_title"]
    if lt < 0.4:  # rayo
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bolt(ImageDraw.Draw(lay), 540, 780, 520 * ease_out(lt / 0.18), YEL, outline=WHITE)
        paste_c(img, lay, 540, 960, alpha=max(0, 1 - max(0, (lt - 0.22) / 0.18)))
    flash(img, 0.85 * max(0, 1 - lt / 0.22) if lt > 0.04 else 0)
    ys = [470, 640, 805, 950]
    for k, spr in enumerate(sprites):
        a0 = sc["title_times"][k] - 0.05
        if lt < a0:
            continue
        p = (lt - a0) / 0.3
        sc_ = 2.4 - 1.4 * ease_out_back(p) if p < 1 else 1.0 + 0.025 * math.sin(lt * 3 + k)
        paste_c(img, spr, 540, ys[k], sc_, 3 * math.sin(lt * 1.7 + k) - 2, alpha=min(1, p * 3))
    pt = sc["pill_t"]
    if lt > pt:
        p = ease_out_back((lt - pt) / 0.35)
        lay = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
        pill(ImageDraw.Draw(lay), 540, 100, "TEST DE PERSONALIDAD", 56, TURQ, BLACK)
        paste_c(img, lay, 540 + (1 - p) * 700, 1130, 1, -2)
    for k, (name, x, y, s) in enumerate([("mascaras", 150, 380, 190), ("cerebro", 940, 560, 170),
                                         ("pensativo", 135, 1010, 170), ("ojos", 945, 1050, 160)]):
        a0 = 0.5 + 0.12 * k
        if lt > a0:
            p = ease_out_back((lt - a0) / 0.35)
            paste_c(img, _img(name, s), x, y + 14 * math.sin(lt * 2.2 + k), p, 10 * math.sin(lt * 1.6 + k))


# ---------------------------------------------------------------- escena: pregunta

def q_layout(sc):
    """Coloca las palabras de la pregunta (para iluminarlas una a una)."""
    key = ("qlay", sc["i"])
    if key not in _S["cache"]:
        tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        f, lines, lh = fit(tmp, sc["q"]["pregunta"], 850, 250, 80, minimum=46, spacing=1.08)
        sp = tmp.textlength(" ", font=f)
        pos = []
        y = 157 - lh * len(lines) / 2 + lh / 2
        for l in lines:
            ws = l.split()
            wl = [tmp.textlength(w, font=f) for w in ws]
            x = 480 - (sum(wl) + sp * (len(ws) - 1)) / 2
            for w, wd in zip(ws, wl):
                pos.append((w, x + wd / 2, y))
                x += wd + sp
            y += lh
        bg = Image.new("RGBA", (960, 330), (0, 0, 0, 0))
        d = ImageDraw.Draw(bg)
        d.rounded_rectangle((10, 26, 950, 326), 48, fill=(90, 30, 190))
        d.rounded_rectangle((10, 8, 950, 306), 48, fill=WHITE)
        d.rounded_rectangle((26, 18, 934, 90), 32, fill=(244, 238, 255))
        _S["cache"][key] = (f, pos, bg)
    return _S["cache"][key]


def q_card(sc, lt):
    f, pos, bg = q_layout(sc)
    card = bg.copy()
    d = ImageDraw.Draw(card)
    qw = sc["qwords"]
    done = lt >= qw[-1][2] + 0.1
    for k, (w, x, y) in enumerate(pos):
        a, b = (qw[k][1], qw[k][2]) if k < len(qw) else (0, 0)
        if done or lt >= b:
            d.text((x, y), w, font=f, fill=(48, 14, 104), anchor="mm")
        elif lt >= a:  # palabra que suena: salta en color
            p = min(1, (lt - a) / 0.12)
            fs = tfont(int(f.size * (1.0 + 0.12 * math.sin(p * math.pi))))
            d.text((x, y - 6 * math.sin(p * math.pi)), w, font=fs, fill=PURP, anchor="mm")
        else:
            d.text((x, y), w, font=f, fill=(48, 14, 104, 45), anchor="mm")
    return card


def opt_card(sc, k, hl=False):
    key = ("opt", sc["i"], k, hl)
    if key not in _S["cache"]:
        bg, fg, edge = OPT[k]
        card = Image.new("RGBA", (940, 132), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        if hl:
            d.rounded_rectangle((0, 0, 939, 131), 40, outline=WHITE, width=8)
        d.rounded_rectangle((12, 22, 928, 124), 34, fill=edge if k != 3 else (8, 4, 16))
        d.rounded_rectangle((12, 12, 928, 114), 34, fill=bg, outline=YEL if k == 3 else None,
                            width=4 if k == 3 else 0)
        hl_l = Image.new("RGBA", card.size, (0, 0, 0, 0))
        ImageDraw.Draw(hl_l).rounded_rectangle((26, 18, 914, 52), 18,
                                               fill=(255, 255, 255, 60) if k != 3 else (255, 255, 255, 22))
        card.alpha_composite(hl_l)
        cx, cy = 74, 63
        d.ellipse((cx - 40, cy - 40, cx + 40, cy + 40), fill=WHITE if k != 3 else YEL)
        d.text((cx, cy + 3), LETTERS[k], font=tfont(54), fill=(bg if k != 3 else BLACK) if k in (2, 3) else BLACK,
               anchor="mm")
        f, lines, lh = fit(d, sc["q"]["opciones"][k], 740, 92, 56, minimum=30, spacing=1.0)
        y = cy - lh * len(lines) / 2 + lh / 2 + 2
        for l in lines:
            d.text((528, y), l, font=f, fill=fg, anchor="mm")
            y += lh
        _S["cache"][key] = card
    return _S["cache"][key]


def countdown_ring(img, sc, lt, cx=540, cy=800):
    cd0 = sc["cd_start"]
    p_in = ease_out_back((lt - 0.5) / 0.4)
    if p_in <= 0:
        return
    rem = COUNTDOWN - (lt - cd0)
    running = 0 <= lt - cd0 < COUNTDOWN
    frac = 1.0 if lt < cd0 else max(0.0, rem / COUNTDOWN)
    num = COUNTDOWN if lt < cd0 else max(0, math.ceil(rem))
    shake = 0
    if running and rem < 2:
        shake = 7 * math.sin(lt * 70)
    col = TURQ if frac > 0.6 else (YEL if frac > 0.4 else RED)
    lay = Image.new("RGBA", (260, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.ellipse((20, 26, 240, 246), fill=(0, 0, 0, 110))
    d.ellipse((20, 18, 240, 238), fill=BLACK)
    d.arc((30, 28, 230, 228), 0, 360, fill=(255, 255, 255, 60), width=16)
    if frac > 0:
        d.arc((30, 28, 230, 228), -90, -90 + 360 * frac, fill=col, width=16)
    sec_p = (lt - cd0) % 1 if running else 1
    s_num = 1.0 + 0.35 * max(0, 1 - sec_p / 0.25) if running else 1.0
    f = tfont(int(104 * s_num))
    d.text((130, 132), str(num), font=f, fill=WHITE if num > 2 or not running else RED, anchor="mm",
           stroke_width=4, stroke_fill=BLACK)
    paste_c(img, lay, cx + shake, cy, p_in)


def draw_question(img, sc, lt):
    i = sc["i"]
    d = ImageDraw.Draw(img)
    lay = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
    pill(ImageDraw.Draw(lay), 838, 105, f"PREGUNTA {i + 1}/{sc['n']}", 44, YEL, BLACK)
    paste_c(img, lay, 540, 205, 1.0)
    x0, x1, yb = 90, 990, 292
    seg = (x1 - x0 - 10 * (sc["n"] - 1)) / sc["n"]
    for k in range(sc["n"]):
        xa = x0 + k * (seg + 10)
        if k < i:
            col = YEL
        elif k > i:
            col = (255, 255, 255, 70)
        else:
            col = TURQ if int(lt * 4) % 2 == 0 else (120, 255, 240)
        d.rounded_rectangle((xa, yb - 8, xa + seg, yb + 8), 8, fill=col)

    p = min(1.0, lt / 0.45)
    mode = i % 4
    card = q_card(sc, lt)
    cx, cy, s, ang, alpha = 540, 505, 1.0, -1.0 + 0.6 * math.sin(lt * 1.3), 1.0
    if mode == 0:
        cx = 540 + (1 - ease_out_back(p)) * 1100
    elif mode == 1:
        s = 0.2 + 0.8 * ease_out_back(p)
        alpha = min(1, p * 2.5)
    elif mode == 2:
        cy = 505 - (1 - ease_out_back(p)) * 900
    elif p < 1:
        card = card.resize((max(1, int(card.width * max(0.02, ease_out_back(p)))), card.height), Image.BILINEAR)
    paste_c(img, card, cx, cy, s, ang, alpha)

    if lt > 0.4:
        pe = ease_out_back((lt - 0.4) / 0.35)
        paste_c(img, _img(sc["q"]["imagen"], 190), 230, 800 + 12 * math.sin(lt * 2.4), pe, 8 * math.sin(lt * 1.8))
        paste_c(img, _img(SIDE_EMOJI[i % 3], 150), 852, 800 + 12 * math.sin(lt * 2.4 + 2), pe,
                -8 * math.sin(lt * 1.5))
    countdown_ring(img, sc, lt)

    cd_end = sc["cd_end"]
    for k in range(4):
        a0 = 0.5 + 0.08 * k
        if lt < a0:
            continue
        pk = ease_out_back((lt - a0) / 0.4)
        side = -1 if (k + i) % 2 == 0 else 1
        x = 540 + side * (1 - pk) * 1150
        y = 965 + k * 128 + 4 * math.sin(lt * 2.6 + k * 1.3)
        s = 1.0
        ang = 0
        if 0 <= lt - sc["cd_start"] < COUNTDOWN and COUNTDOWN - (lt - sc["cd_start"]) < 2:
            s += 0.015 * math.sin(lt * 20 + k)
        if lt >= cd_end:  # las tarjetas tiemblan con la reacción
            e = max(0, 1 - (lt - cd_end) / 0.6)
            ang = 4 * e * math.sin((lt - cd_end) * 40 + k)
        paste_c(img, opt_card(sc, k), x, y, s, ang)

    # reacción divertida (pegatina + emoji 3D)
    if lt >= cd_end:
        q = (lt - cd_end) / 0.22
        key = ("react", i)
        if key not in _S["cache"]:
            txt = sc["q"]["reaccion"].upper()
            fs_ = 100
            while ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(txt, font=tfont(fs_)) > 700:
                fs_ -= 4
            f = tfont(fs_)
            tw = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(txt, font=f)
            st = Image.new("RGBA", (int(tw) + 300, 230), (0, 0, 0, 0))
            sd = ImageDraw.Draw(st)
            sd.rounded_rectangle((14, 30, st.width - 6, 222), 46, fill=(0, 0, 0, 120))
            sd.rounded_rectangle((6, 14, st.width - 14, 206), 46, fill=PINK, outline=WHITE, width=10)
            sd.text(((st.width - 200) / 2 + 200 - 10, 112), txt, font=f, fill=WHITE, anchor="mm",
                    stroke_width=7, stroke_fill=BLACK)
            em = _img(sc["q"]["reaccion_emoji"], 190)
            st.alpha_composite(em, (20, 112 - em.height // 2))
            _S["cache"][key] = st
        sc_ = 2.3 - 1.3 * ease_out_back(q) if q < 1 else 1.0 + 0.04 * math.sin((lt - cd_end) * 12)
        paste_c(img, _S["cache"][key], 540, 1150, sc_, -5 + 3 * math.sin((lt - cd_end) * 9), min(1, q * 3))
    flash(img, 0.4 * max(0, 1 - (lt - cd_end) / 0.15) if lt >= cd_end else 0)


# ---------------------------------------------------------------- escena: resultados

def profile_tile(p, k):
    key = ("tile", k)
    if key not in _S["cache"]:
        bg, fg, edge = OPT[k]
        card = Image.new("RGBA", (460, 350), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle((8, 22, 452, 346), 44, fill=edge if k != 3 else (8, 4, 16))
        d.rounded_rectangle((8, 8, 452, 332), 44, fill=bg, outline=YEL if k == 3 else WHITE, width=6)
        d.ellipse((24, 22, 124, 122), fill=WHITE if k != 3 else YEL)
        d.text((74, 74), p["letra"], font=tfont(72), fill=bg if k == 2 else BLACK, anchor="mm")
        em = _img(p["imagen"], 170)
        card.alpha_composite(em, (280 - em.width // 2 + 30, 110 - em.height // 2 + 10))
        f, lines, lh = fit(d, p["nombre"], 400, 120, 50, minimum=30, spacing=1.0)
        lines = [l.upper() for l in lines]
        y = 262 - lh * len(lines) / 2 + lh / 2
        for l in lines:
            d.text((230, y), l, font=tfont(f.size), fill=fg, anchor="mm")
            y += lh
        _S["cache"][key] = card
    return _S["cache"][key]


def draw_results(img, sc, lt):
    r = sc["r"]
    rev = sc["reveal"]
    if lt < rev:  # redoble: letras A-D girando cada vez más rápido
        sp = 2 + 12 * (lt / rev) ** 2
        for k in range(4):
            a = lt * sp + k * math.pi / 2
            rad = 260 - 90 * (lt / rev)
            lay = Image.new("RGBA", (190, 190), (0, 0, 0, 0))
            ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle((10, 10, 180, 180), 40, fill=OPT[k][0], outline=WHITE, width=6)
            ld.text((95, 100), LETTERS[k], font=tfont(110), fill=BLACK if k < 2 else WHITE, anchor="mm")
            paste_c(img, lay, 540 + rad * math.cos(a), 900 + rad * math.sin(a), 1.0, math.degrees(-a) * 0.2)
        return
    lr = lt - rev
    flash(img, 0.7 * max(0, 1 - lr / 0.2))
    if "res_title" not in _S["cache"]:
        _S["cache"]["res_title"] = text_sprite([tuple(x) for x in r["titulo"]], 120, FILL, stroke=12)
    st = _S["cache"]["res_title"]
    s = 2.0 - ease_out_back(min(1, lr / 0.4)) if lr < 0.4 else 1 + 0.02 * math.sin(lt * 3)
    paste_c(img, st, 540, 450, s, -2)
    centers = [(290, 760), (790, 760), (290, 1110), (790, 1110)]
    tie = sc["tie_start"]
    for k, (p, (ap, va, vb)) in enumerate(zip(r["perfiles"], sc["perfiles"])):
        if lt < ap:
            continue
        pk = ease_out_back((lt - ap) / 0.4)
        active = va <= lt < vb + 0.1
        s = 1.08 + 0.02 * math.sin(lt * 7) if active else 0.94
        alpha = 1.0 if active or lt >= tie else 0.55
        ang = 3 * math.sin(lt * 5) if active else 0
        cx, cy = centers[k]
        if active:
            paste_c(img, _S["glow_w"], cx, cy, 1.0, 0, 0.5)
        paste_c(img, profile_tile(p, k), cx, cy, s * pk, ang, alpha)
    if lt >= tie:
        q = ease_out_back((lt - tie) / 0.35)
        lay = Image.new("RGBA", (W, 230), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        pill(ld, 540, 70, r["empate"], 50, BLACK, YEL, outline=YEL)
        f, lines, lh = fit(ld, r["aviso"], 900, 90, 30, minimum=24)
        y = 170 - lh * len(lines) / 2 + lh / 2
        for l in lines:
            ld.text((540, y), l, font=f, fill=WHITE, anchor="mm", stroke_width=4, stroke_fill=BLACK)
            y += lh
        paste_c(img, lay, 540, 1385, q)
    confetti(img, lr, 540, 520, 1.0)


# ---------------------------------------------------------------- escena: llamada a la acción

def draw_cta(img, sc, lt):
    cc = sc["c"]
    if "cta_title" not in _S["cache"]:
        _S["cache"]["cta_title"] = text_sprite([tuple(x) for x in cc["titulo"]], 128, FILL, stroke=12)
    st = _S["cache"]["cta_title"]
    p = min(1, lt / 0.4)
    s = 2.3 - 1.3 * ease_out_back(p) if p < 1 else 1 + 0.025 * math.sin(lt * 4)
    paste_c(img, st, 540, 450, s, 2 * math.sin(lt * 2))
    flash(img, 0.6 * max(0, 1 - lt / 0.2))
    follow = sc["follow"]
    # mano señalando abajo (a los comentarios)
    if lt > 0.5:
        pe = ease_out_back((lt - 0.5) / 0.4)
        paste_c(img, _img("mano_abajo", 170), 540, 700 + 26 * abs(math.sin(lt * 4)), pe)
    # fichas A B C D botando en ola
    for k in range(4):
        a0 = 0.8 + 0.12 * k
        if lt < a0:
            continue
        pk = ease_out_back((lt - a0) / 0.35)
        lay = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((12, 22, 188, 196), 44, fill=(0, 0, 0, 120))
        ld.rounded_rectangle((12, 10, 188, 184), 44, fill=OPT[k][0], outline=WHITE, width=7)
        ld.text((100, 100), LETTERS[k], font=tfont(120), fill=BLACK if k < 2 else WHITE, anchor="mm")
        jump = 40 * max(0, math.sin(lt * 4.5 - k * 0.8))
        paste_c(img, lay, 180 + k * 240, 905 - jump, pk, 6 * math.sin(lt * 3 + k))
    hide = max(0.0, min(1.0, (lt - follow) / 0.3))
    # comentarios que se escriben solos
    tp = sc["typing"]
    comments = [("¡Me ha salido la C!", tp, PINK), ("@tu_amigo ¡hazlo ya!", tp + 1.3, TURQ)]
    for k, (txt, a0, col) in enumerate(comments):
        if lt < a0 or hide >= 1:
            continue
        n = int(min(len(txt), (lt - a0) / 0.06))
        pk = ease_out_back((lt - a0) / 0.35)
        lay = Image.new("RGBA", (900, 140), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((10, 18, 890, 132), 40, fill=(0, 0, 0, 100))
        ld.rounded_rectangle((10, 8, 890, 122), 40, fill=WHITE)
        ld.ellipse((28, 24, 108, 104), fill=col)
        ld.text((68, 66), "?" if k == 0 else "@", font=tfont(50), fill=WHITE, anchor="mm")
        ld.text((130, 65), txt[:n] + ("|" if n < len(txt) and int(lt * 4) % 2 == 0 else ""), font=font(40),
                fill=BLACK, anchor="lm")
        if n >= len(txt):
            hp = ease_out_back((lt - a0 - len(txt) * 0.06) / 0.3)
            if hp > 0:
                hx, hy, hs = 850, 64, 22 * hp
                ld.ellipse((hx - hs, hy - hs, hx + hs, hy + hs), fill=RED)
        paste_c(img, lay, 540, 1100 + k * 150, pk * (1 - 0.3 * hide), 0, 1 - hide)
    # logo + «síguenos» al final
    if lt >= follow:
        q = ease_out_back((lt - follow) / 0.45)
        glow = _S["glow_w"]
        paste_c(img, glow, 540, 1130, 1.2 + 0.1 * math.sin(lt * 5), 0, 0.8 * q)
        paste_c(img, _S["logo_b"], 540, 1130, q * (1 + 0.03 * math.sin(lt * 4)), 4 * math.sin(lt * 2))
        lay = Image.new("RGBA", (W, 160), (0, 0, 0, 0))
        b = pill(ImageDraw.Draw(lay), 520, 80, "SÍGUENOS: HORA DEL QUIZ", 50, YEL, BLACK)
        bolt(ImageDraw.Draw(lay), b[2] - 6, 76, 46, TURQ, outline=BLACK)
        paste_c(img, lay, 540, 1320, q)
        confetti(img, lt - follow, 540, 1100, 0.9)


# ---------------------------------------------------------------- fotograma

def render_frame(i):
    t = i / FPS
    img = background(t)
    scenes = _S["scenes"]
    for k, sc in enumerate(scenes):
        lt = t - sc["start"]
        if 0 <= lt < sc["dur"]:
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            {"intro": draw_intro, "q": draw_question, "res": draw_results, "cta": draw_cta}[sc["kind"]](lay, sc, lt)
            out = sc["dur"] - lt
            if out < 0.35 and k < len(scenes) - 1:  # transición de salida variada
                e = ease_in(1 - out / 0.35)
                mode = k % 3
                if mode == 0:
                    moved = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    moved.paste(lay, (int(-e * W), 0))
                    lay = moved
                elif mode == 1:
                    s = 1 - 0.85 * e
                    small = lay.resize((max(1, int(W * s)), max(1, int(H * s))), Image.BILINEAR)
                    small.putalpha(small.getchannel("A").point(lambda a: int(a * (1 - e))))
                    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    lay.alpha_composite(small, ((W - small.width) // 2, (H - small.height) // 2))
                else:
                    moved = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    moved.paste(lay, (0, int(-e * H)))
                    lay = moved
            img.alpha_composite(lay)
            break
    if t >= 0.4:
        logo_badge(img, min(1, (t - 0.4) / 0.4))
    subtitles(img, t)
    username(img)
    return img.convert("RGB").tobytes()


# ---------------------------------------------------------------- exportación

def render_video(content, voice, out_path, workers=None, preview=None):
    scenes, events, subs, total = build_timeline(content, voice)
    state = {"scenes": scenes, "subs": subs, "c": content}
    if preview is not None:  # lista de segundos → PNGs
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
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav,
           "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-level", "4.1",
           "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
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
    return total, subs

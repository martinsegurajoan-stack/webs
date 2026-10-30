"""Formato "STREAMER": quiz sobre un streamer con estética de directo (Twitch).

Gancho con FOTO REAL a pantalla completa → 5 preguntas + 1 extra como encuestas de directo
(cámara del streamer, chat en vivo, barras de votos, alerta al acertar) → cierre.
El aviso del gancho (`aviso`) se queda fijo arriba durante todo el vídeo.
"""

import math
import os
import random
import subprocess
import zlib
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from . import audio, themes
from .niveles import check, paste_c, pill, pop, rr, text, username
from .render import FPS, W, H, ease_in, ease_out, fit, font, tfont

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
BASE = os.path.join(os.path.dirname(__file__), "..")
LETTERS = "ABCD"
COUNTDOWN = 5
WHITE = (255, 255, 255)
YEL = (255, 212, 0)
RED = (235, 25, 60)
GREEN = (0, 200, 110)
INK = (16, 10, 30)
FRASES_CORRECTA = ["¡Es la {L}! {O}.", "¡La correcta es la {L}! {O}.", "¡Correcto, la {L}! {O}."]
CHAT_USERS = [("pepitogamer", (255, 90, 90)), ("lauritaa_", (90, 200, 255)), ("elcrack99", (120, 255, 140)),
              ("noob_master", (255, 200, 60)), ("sara.xd", (255, 120, 220)), ("burlao_oficial", (170, 140, 255)),
              ("mr_tostada", (255, 160, 80)), ("yoquese_", (100, 240, 220))]
CHAT_MSG = ["VAMOOOS", "esta me la sé", "ni idea jajaja", "KEKW", "IMPOSIBLE", "top 1 fan aquí", "¿¿en serio??",
            "ojo con la extra", "esta es trampa", "facilísima", "GG", "no puede ser", "lo sabía", "F en el chat",
            "piensa, piensa…", "hoy acierto todas"]


# ------------------------------------------------------------------ línea de tiempo

def _countdown(ev, at):
    ev += [("fx", "riser", at), ("music_boost", at, at + COUNTDOWN)]
    for s in range(COUNTDOWN):
        ts = at + s
        ev += [("fx", "heart", ts), ("fx", "tick_high" if s >= COUNTDOWN - 2 else "tick", ts), ("fx", "tock", ts + 0.5)]
        if s >= COUNTDOWN - 2:
            ev += [("fx", "tick_high", ts + 0.25), ("fx", "tick_high", ts + 0.75)]


def build_timeline(c, voice):
    scenes, ev = [], []
    sig, d = voice.say(c["gancho"]["voz"])
    ev += [("voice", sig, 0.05), ("fx", "impact", 0.0), ("fx", "whoosh", 0.02)]
    dur = max(3.0, d + 0.45)
    scenes.append({"kind": "hook", "start": 0.0, "dur": dur})
    t = dur
    qs = c["preguntas"]
    n_reg = sum(1 for q in qs if not q.get("sin_respuesta"))
    for qi, q in enumerate(qs):
        st = t
        extra = bool(q.get("sin_respuesta"))
        etiqueta = "¡Pregunta extra!" if extra else f"¡Pregunta {qi + 1}!"
        sig, dq = voice.say(f"{etiqueta} " + q.get("pregunta_voz", q["pregunta"]))
        ev += [("fx", "whoosh", st), ("voice", sig, st + 0.3)]
        loc = 0.3 + max(0.4, dq - 0.4)
        opt_t = []
        for _ in q["opciones"]:
            opt_t.append(loc)
            ev.append(("fx", "pop", st + loc))
            loc += 0.16
        cd = loc + 0.1
        _countdown(ev, st + cd)
        rv = cd + COUNTDOWN
        ci = LETTERS.index(q["correcta"])
        if extra:
            sig, dv = voice.say("¡Escríbelo en los comentarios si te lo sabes!")
            ev += [("fx", "buzz", st + rv), ("voice", sig, st + rv + 0.35)]
            rdur = max(2.6, 0.35 + dv + 0.6)
        else:
            frase = q.get("respuesta_voz") or FRASES_CORRECTA[qi % 3].format(
                L=LETTERS[ci], O=q.get("opcion_voz", q["opciones"][ci]).rstrip("."))
            sig, dv = voice.say(frase)
            ev += [("fx", "buzz", st + rv), ("fx", "correct", st + rv + 0.15), ("fx", "alert", st + rv + 0.5),
                   ("voice", sig, st + rv + 0.4)]
            rdur = max(2.4, 0.4 + dv + 0.4)
        scenes.append({"kind": "q", "start": st, "dur": rv + rdur, "q": q, "i": qi, "n": n_reg, "extra": extra,
                       "opt_t": opt_t, "cd": cd, "rv": rv, "ci": ci})
        t += rv + rdur
    sig, d = voice.say(c.get("cierre_voz", "¿Cuántas has acertado?"))
    shout_at = 0.35 + d + 0.1
    sig2, d2 = voice.say("¡Sígueme para más!", shout=True)
    dur = max(3.6, shout_at + d2 + 1.0)
    ev += [("fx", "whoosh", t), ("voice", sig, t + 0.35), ("voice", sig2, t + shout_at), ("fx", "applause", t + shout_at)]
    scenes.append({"kind": "outro", "start": t, "dur": dur, "shout_at": shout_at})
    return scenes, ev, t + dur


# ------------------------------------------------------------------ audio

def sfx_alert():
    sr = audio.SR
    out = np.zeros(int(0.7 * sr))
    for k, f in enumerate([880, 1175, 1568]):
        t = np.arange(int(0.25 * sr)) / sr
        tone = np.sin(2 * np.pi * f * t) * np.exp(-t * 9)
        s = int(k * 0.09 * sr)
        out[s:s + len(tone)] += tone
    return 0.35 * out


def build_audio(events, total, path, seed):
    from .personalidad import sfx_impact
    mix = audio.Mixer(total)
    fx = {"whoosh": audio.sfx_whoosh(), "pop": audio.sfx_pop(), "tick": audio.sfx_tick(), "tick_high": audio.sfx_tick(True),
          "tock": audio.sfx_tock(), "heart": audio.sfx_heartbeat(), "riser": audio.sfx_riser(COUNTDOWN),
          "buzz": audio.sfx_buzz_end(), "correct": audio.sfx_correct(), "applause": audio.sfx_applause(),
          "impact": sfx_impact(), "alert": sfx_alert()}
    gains = {"whoosh": 0.5, "pop": 0.6, "tick": 1.3, "tick_high": 1.45, "tock": 0.95, "heart": 0.85, "riser": 0.5,
             "buzz": 0.6, "correct": 0.9, "applause": 0.8, "impact": 0.75, "alert": 0.8}
    boosts = [(a, b) for k, a, b in events if k == "music_boost"]
    for kind, what, at in events:
        if kind == "music_boost":
            continue
        if kind == "fx":
            mix.add_fx(fx[what], at, gains[what])
        elif what is not None:
            mix.add_voice(what, at, 1.0)
    audio.write_wav(path, mix.render(audio.music_pop(total, bpm=126, seed=seed), music_gain=0.34, boosts=boosts))


# ------------------------------------------------------------------ recursos

_S = {}


def _cover(im, w, h, foco=None, zoom=1.0):
    sw, sh = im.size
    fx, fy = foco or (sw / 2, sh / 2)
    s = max(w / sw, h / sh) * zoom
    cw, ch = w / s, h / s
    x0 = min(max(fx - cw / 2, 0), sw - cw)
    y0 = min(max(fy - ch * 0.42, 0), sh - ch)
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((w, h), Image.LANCZOS)


def _placeholder(w, h):
    im = Image.new("RGB", (w, h), (60, 40, 90))
    d = ImageDraw.Draw(im)
    d.ellipse((w * 0.3, h * 0.18, w * 0.7, h * 0.52), fill=(120, 100, 150))
    d.ellipse((w * 0.12, h * 0.55, w * 0.88, h * 1.2), fill=(120, 100, 150))
    d.text((w / 2, h * 0.9), "FOTO PENDIENTE", font=tfont(int(w / 12)), fill=WHITE, anchor="mm")
    return im


def _init(state):
    _S.clear()
    _S.update(state)
    c = state["c"]
    h = state["tono"]
    _S["acc"] = themes._hsv(h, 0.72, 1.0)
    _S["acc_d"] = themes._hsv(h, 0.85, 0.45)
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(-1, 1, W)[None, :]
    top, bot = themes._hsv(h, 0.75, 0.28), (8, 5, 16)
    k = np.clip(y * 0.95 + x * 0.05, 0, 1)
    arr = np.zeros((H, W, 3))
    for ch in range(3):
        arr[..., ch] = top[ch] + (bot[ch] - top[ch]) * k
    arr += (np.exp(-((x * 1.1) ** 2 + ((y - 0.35) / 0.35) ** 2)) * 28)[..., None]
    bg = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(bg, "RGBA")
    for yy in range(0, H, 6):  # líneas de escaneo muy suaves
        d.line((0, yy, W, yy), fill=(0, 0, 0, 22))
    for xx in range(0, W, 90):  # rejilla neón
        d.line((xx, 0, xx, H), fill=_S["acc"] + (10,))
    for yy in range(0, H, 90):
        d.line((0, yy, W, yy), fill=_S["acc"] + (10,))
    _S["bg"] = bg
    p = c.get("foto")
    src = None
    if p and os.path.exists(os.path.join(BASE, p)):
        src = ImageOps.exif_transpose(Image.open(os.path.join(BASE, p))).convert("RGB")
    _S["foto"] = src
    foco = c.get("foco")
    # fondo: la foto desenfocada y oscurecida; delante, la foto nítida enmarcada (fotos pequeñas no se pixelan)
    base = _cover(src, W, H, foco) if src else _placeholder(W, H)
    _S["hook_img"] = Image.blend(base.filter(ImageFilter.GaussianBlur(30)), Image.new("RGB", (W, H), (12, 6, 26)), 0.35)
    card = _cover(src, 880, 880, foco, zoom=1.0) if src else _placeholder(880, 880)
    card = card.filter(ImageFilter.UnsharpMask(2, 80, 2)).convert("RGBA")
    mk = Image.new("L", card.size, 0)
    ImageDraw.Draw(mk).rounded_rectangle((0, 0, 879, 879), 60, fill=255)
    card.putalpha(mk)
    _S["hook_card"] = card
    cam = _cover(src, 270, 270, foco, zoom=float(c.get("zoom_cam", 1.6))) if src else _placeholder(270, 270)
    m = Image.new("L", cam.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, 269, 269), 26, fill=255)
    cam = cam.convert("RGBA")
    cam.putalpha(m)
    _S["cam"] = cam
    big = _cover(src, 560, 560, foco, zoom=float(c.get("zoom_cam", 1.6))) if src else _placeholder(560, 560)
    m2 = Image.new("L", big.size, 0)
    ImageDraw.Draw(m2).ellipse((0, 0, 559, 559), fill=255)
    big = big.convert("RGBA")
    big.putalpha(m2)
    _S["cam_big"] = big
    blur = (_cover(src, W, H, foco) if src else _placeholder(W, H)).filter(ImageFilter.GaussianBlur(26))
    _S["outro_bg"] = Image.blend(blur, Image.new("RGB", (W, H), (10, 6, 20)), 0.55)
    _S["logo"] = Image.open(os.path.join(ASSETS, "logo.png")).convert("RGBA")
    seed = zlib.crc32(c["video"].encode())
    r = random.Random(seed)
    chat = []
    while len(chat) < 400:  # sin mensajes repetidos seguidos
        msgs = CHAT_MSG[:]
        r.shuffle(msgs)
        chat += [(r.choice(CHAT_USERS), m) for m in msgs]
    _S["chat"] = chat
    _S["polls"] = []
    for q in c["preguntas"]:
        v = [r.uniform(8, 40) for _ in range(4)]
        tot = sum(v)
        pc = [int(round(x / tot * 100)) for x in v]
        pc[0] += 100 - sum(pc)
        _S["polls"].append(pc)
    rb = random.Random(4)
    cols = [YEL, (0, 230, 210), (255, 70, 170), WHITE, _S["acc"], GREEN]
    _S["burst"] = [(rb.uniform(-1, 1), rb.uniform(-1.5, -0.4), rb.choice(cols), rb.uniform(9, 20),
                    rb.uniform(0, 6.28)) for _ in range(44)]
    _S["viewers0"] = 8000 + seed % 9000
    rp = random.Random(seed + 7)
    _S["parts"] = [(rp.uniform(0, W), rp.uniform(0, H), rp.uniform(0.5, 1.4), rp.uniform(2.5, 5.5),
                    rp.uniform(0, 6.28)) for _ in range(26)]


# ------------------------------------------------------------------ piezas

def warn_icon(d, cx, cy, s, col=INK, bg=YEL):
    d.polygon([(cx, cy - s), (cx + s * 1.1, cy + s * 0.85), (cx - s * 1.1, cy + s * 0.85)], fill=col)
    d.polygon([(cx, cy - s * 0.62), (cx + s * 0.75, cy + s * 0.62), (cx - s * 0.75, cy + s * 0.62)], fill=bg)
    d.rounded_rectangle((cx - s * 0.1, cy - s * 0.35, cx + s * 0.1, cy + s * 0.25), 3, fill=col)
    d.ellipse((cx - s * 0.11, cy + s * 0.35, cx + s * 0.11, cy + s * 0.55), fill=col)


def banner(img, d, t, dy=0):
    """Aviso fijo arriba durante todo el vídeo (cinta de advertencia)."""
    l1, l2 = _S["c"]["aviso"]
    pulse = 1 + 0.015 * math.sin(t * 6)
    x0, x1, y0, y1 = 60, 1020, 160 + dy, 300 + dy
    rr(d, (x0 + 6, y0 + 10, x1 + 6, y1 + 10), 26, (0, 0, 0, 90))
    rr(d, (x0, y0, x1, y1), 26, YEL)
    # rayas de advertencia en los extremos
    for side in (0, 1):
        bx0 = x0 if side == 0 else x1 - 120
        strip = Image.new("RGBA", (120, y1 - y0), (0, 0, 0, 0))
        sd = ImageDraw.Draw(strip)
        off = (t * 60) % 40
        for k in range(-4, 10):
            xx = k * 40 - off
            sd.polygon([(xx, 0), (xx + 20, 0), (xx - 20 + 20, y1 - y0), (xx - 20, y1 - y0)], fill=INK)
        m = Image.new("L", strip.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0 if side == 0 else -40, 0, 160 if side == 0 else 119, y1 - y0 - 1), 26,
                                            fill=255)
        strip.putalpha(Image.fromarray(np.minimum(np.array(strip.getchannel("A")), np.array(m))))
        img.paste(strip, (bx0, y0), strip)
    rr(d, (x0 + 110, y0 + 8, x1 - 110, y1 - 8), 18, YEL)
    warn_icon(d, x0 + 160, (y0 + y1) / 2 - 2, 30)
    f1 = tfont(int(44 * pulse))
    f2 = tfont(int(50 * pulse))
    cx = (x0 + 200 + x1 - 120) / 2
    for s_, f in ((l1, f1),):
        while d.textlength(s_, font=f) > x1 - x0 - 330:
            f = tfont(f.size - 2)
        d.text((cx, y0 + 46), s_, font=f, fill=INK, anchor="mm")
    while d.textlength(l2, font=f2) > x1 - x0 - 330:
        f2 = tfont(f2.size - 2)
    d.text((cx, y0 + 100), l2, font=f2, fill=RED, anchor="mm")


def live_badge(d, x, y, t, size=34):
    blink = 0.6 + 0.4 * (math.sin(t * 6) > 0)
    f = tfont(size)
    w = d.textlength("EN DIRECTO", font=f)
    rr(d, (x, y - size * 0.75, x + w + size * 1.6, y + size * 0.75), size * 0.4, RED)
    d.ellipse((x + size * 0.35, y - size * 0.22, x + size * 0.79, y + size * 0.22), fill=(255, 255, 255, int(255 * blink)))
    d.text((x + size * 1.05, y + 2), "EN DIRECTO", font=f, fill=WHITE, anchor="lm")
    return x + w + size * 1.6


def viewers(d, x, y, t, size=30):
    n = _S["viewers0"] + int(t * 37) + int(40 * math.sin(t * 1.3))
    s = f"{n:,}".replace(",", ".")
    f = tfont(size)
    w = d.textlength(s, font=f)
    rr(d, (x, y - size * 0.75, x + w + size * 2.0, y + size * 0.75), size * 0.4, (0, 0, 0, 150))
    cx = x + size * 0.75
    d.ellipse((cx - size * 0.42, y - size * 0.24, cx + size * 0.42, y + size * 0.24), outline=WHITE, width=3)
    d.ellipse((cx - size * 0.12, y - size * 0.12, cx + size * 0.12, y + size * 0.12), fill=WHITE)
    d.text((x + size * 1.45, y + 2), s, font=f, fill=WHITE, anchor="lm")


def chat_panel(img, d, t, box, idx0=0, rate=1.25, burst_t=None):
    x0, y0, x1, y1 = box
    rr(d, (x0 + 5, y0 + 9, x1 + 5, y1 + 9), 24, (0, 0, 0, 80))
    rr(d, box, 24, (14, 9, 28, 225), outline=_S["acc"] + (160,), width=3)
    d.text((x0 + 24, y0 + 30), "CHAT EN DIRECTO", font=tfont(30), fill=_S["acc"], anchor="lm")
    d.ellipse((x1 - 44, y0 + 22, x1 - 28, y0 + 38), fill=RED)
    n = int(t * rate) + idx0
    lines = 4
    lh = (y1 - y0 - 70) / lines
    frac = (t * rate) % 1
    slide = ease_out(min(1, frac / 0.25))
    for j in range(lines):
        k = n - (lines - 1 - j)
        if k < 0:
            continue
        (user, col), msg = _S["chat"][k % len(_S["chat"])]
        yy = y0 + 70 + j * lh + lh / 2 + (1 - slide) * lh
        if yy > y1 - 12:
            continue
        fu = font(30)
        d.text((x0 + 24, yy), user + ":", font=fu, fill=col, anchor="lm")
        wu = d.textlength(user + ": ", font=fu)
        d.text((x0 + 24 + wu, yy), msg, font=font(30), fill=WHITE, anchor="lm")


def cam_frame(img, d, t, x, y, label):
    glow = 0.5 + 0.5 * math.sin(t * 3)
    rr(d, (x - 10, y - 10, x + 280, y + 280), 34, _S["acc"] + (int(60 + 60 * glow),))
    rr(d, (x - 4, y - 4, x + 274, y + 274), 30, _S["acc"])
    img.paste(_S["cam"], (int(x), int(y)), _S["cam"])
    live_badge(d, x + 12, y + 32, t, 22)
    f = tfont(30)
    w = d.textlength(label, font=f)
    rr(d, (x + 135 - w / 2 - 18, y + 236, x + 135 + w / 2 + 18, y + 284), 18, INK)
    d.text((x + 135, y + 261), label, font=f, fill=WHITE, anchor="mm")


def burst(d, lt, cx, cy, dur=1.5):
    if not 0 <= lt < dur:
        return
    for (vx, vy, col, sz, ph) in _S["burst"]:
        x = cx + vx * 600 * lt
        y = cy + vy * 700 * lt + 900 * lt * lt
        ang = ph + lt * 8
        pts = [(x + sz * math.cos(ang + j * math.pi / 2) * (1 if j % 2 else 0.5),
                y + sz * math.sin(ang + j * math.pi / 2) * (1 if j % 2 else 0.5)) for j in range(4)]
        d.polygon(pts, fill=col + (int(255 * max(0, 1 - lt / dur)),))


# ------------------------------------------------------------------ escenas

def draw_hook(img, d, sc, lt, t):
    c = _S["c"]
    img.paste(_S["hook_img"])
    dd = ImageDraw.Draw(img, "RGBA")
    z = 1.25 - 0.25 * ease_out(lt / 0.45) + 0.02 * lt
    sh = math.sin(lt * 55) * 18 * max(0, 1 - lt / 0.4)
    cy0 = 760
    g = 0.5 + 0.5 * math.sin(lt * 5)
    R = 440 * z
    rr(dd, (540 - R - 22 + sh, cy0 - R - 22, 540 + R + 22 + sh, cy0 + R + 22), 80, _S["acc"] + (int(90 + 80 * g),))
    rr(dd, (540 - R - 10 + sh, cy0 - R - 10, 540 + R + 10 + sh, cy0 + R + 10), 70, YEL)
    paste_c(img, _S["hook_card"], 540 + sh, cy0, z)
    # glitch RGB los primeros instantes
    if lt < 0.35:
        r, g, b = img.split()
        off = int(16 * (1 - lt / 0.35))
        r = r.transform(r.size, Image.AFFINE, (1, 0, -off, 0, 1, 0))
        b = b.transform(b.size, Image.AFFINE, (1, 0, off, 0, 1, 0))
        img.paste(Image.merge("RGB", (r, g, b)))
    d2 = ImageDraw.Draw(img, "RGBA")
    live_badge(d2, 150, 380, lt, 38)
    viewers(d2, 460, 380, lt, 34)
    l1, l2 = c["gancho"]["texto"]
    p = ease_out(lt / 0.25)
    s = 1.12 - 0.12 * p
    text(d2, (540, 1300), l1, tfont(int(90 * s)), WHITE, 11, INK, sh=10)
    f = tfont(int(178 * s))
    while d2.textlength(l2, font=f) > 1000:
        f = tfont(f.size - 4)
    text(d2, (540, 1435), l2, f, YEL, 15, INK, sh=12)
    b = pop(lt, 0.45, 0.35)
    if b > 0:
        flash = 0.75 + 0.25 * (math.sin(lt * 14) > 0)
        pill(d2, 540, 1570 + (1 - b) * 100, c["gancho"]["pegatina"], int(62 * max(b, 0.1)),
             tuple(int(v * flash) for v in RED), WHITE, pad=(40, 22))
    banner(img, d2, t)
    if lt < 0.15:
        img.paste(WHITE, (0, 0), Image.new("L", (W, H), int(220 * (1 - lt / 0.15))))


def opt_boxes():
    h, g, y0 = 132, 18, 905
    return [(70, y0 + i * (h + g), 1010, y0 + i * (h + g) + h) for i in range(4)]


def particles(d, t):
    """Chispas de neón que suben despacio y titilan (fondo con vida)."""
    for k, (x0, y0, sp, sz, ph) in enumerate(_S["parts"]):
        y = (y0 - t * 55 * sp) % (H + 80) - 40
        x = x0 + math.sin(t * 0.9 * sp + ph) * 26
        tw = 0.5 + 0.5 * math.sin(t * 3 * sp + ph)
        col = _S["acc"] if k % 3 else YEL
        r = sz * (0.7 + 0.5 * tw)
        d.ellipse((x - r * 2.4, y - r * 2.4, x + r * 2.4, y + r * 2.4), fill=col + (int(26 * tw),))
        d.ellipse((x - r, y - r, x + r, y + r), fill=col + (int(110 + 120 * tw),))


def draw_q(img, d, sc, lt, t):
    q = sc["q"]
    acc = _S["acc"]
    particles(d, t)
    banner(img, d, t)
    # fila superior: chat + cámara
    a = pop(lt, 0.0, 0.35)
    chat_panel(img, d, t, (70, 330 + (1 - a) * 30, 690, 590 + (1 - a) * 30), idx0=sc["i"] * 7)
    cam_frame(img, d, t, 720, 325, _S["c"]["nombre"].upper())
    # tarjeta de pregunta (oscura, borde neón)
    b = pop(lt, 0.1, 0.4)
    fq = math.sin(t * 1.4) * 5
    y0, y1 = 625 + fq, 870 + fq
    cy = (y0 + y1) / 2
    hh = (y1 - y0) / 2 * (0.85 + 0.15 * b)
    box = (70, cy - hh, 1010, cy + hh)
    rr(d, (box[0] + 6, box[1] + 12, box[2] + 6, box[3] + 12), 30, (0, 0, 0, 100))
    rr(d, box, 30, (20, 13, 38, 240), outline=acc, width=5)
    f, lines, lh = fit(d, q["pregunta"], 700, 170, 58, 32, 1.06)
    yy = cy + 14 - lh * len(lines) / 2 + lh / 2
    for ln in lines:
        d.text((485, yy), ln, font=f, fill=WHITE, anchor="mm")
        yy += lh
    lab = "PREGUNTA EXTRA · SOLO FANS" if sc["extra"] else f"PREGUNTA {sc['i'] + 1}/{sc['n']}"
    pill(d, 330, box[1], lab, 36, RED if sc["extra"] else YEL, WHITE if sc["extra"] else INK, pad=(26, 12))
    # temporizador en la esquina de la tarjeta
    cd, rv = sc["cd"], sc["rv"]
    if cd - 0.3 <= lt < rv + 0.3:
        ta = pop(lt, cd - 0.3, 0.35) if lt < rv else 1 - ease_in((lt - rv) / 0.3)
        rem = max(0.0, cd + COUNTDOWN - lt)
        nn = min(COUNTDOWN, int(math.ceil(rem))) if lt >= cd else COUNTDOWN
        urgent = lt >= cd and rem <= 2
        col = RED if urgent else acc
        beat = 1 + (0.09 * max(0, math.cos((lt - cd) * 2 * math.pi)) if urgent else 0)
        R = 62 * ta * beat
        cx_, cy_ = 935, cy + 10
        if R > 16:
            d.ellipse((cx_ - R - 6, cy_ - R - 6, cx_ + R + 6, cy_ + R + 6), fill=col + (90,))
            d.ellipse((cx_ - R, cy_ - R, cx_ + R, cy_ + R), fill=INK)
            frac = rem / COUNTDOWN if lt >= cd else 1.0
            d.arc((cx_ - R + 6, cy_ - R + 6, cx_ + R - 6, cy_ + R - 6), -90, -90 + 360 * frac, fill=col,
                  width=max(1, int(11 * ta)))
            if nn > 0:
                d.text((cx_, cy_ + 3), str(nn), font=tfont(int(66 * ta * beat)), fill=WHITE, anchor="mm")
    # opciones como encuesta del directo
    pcs = _S["polls"][sc["i"]]
    revealed = lt >= rv and not sc["extra"]
    vote = min(1.0, max(0.0, (lt - cd) / COUNTDOWN)) if lt >= cd else 0.0
    vote = ease_out(vote)
    for i, bx in enumerate(opt_boxes()):
        a2 = pop(lt, sc["opt_t"][i], 0.35)
        if a2 <= 0:
            continue
        x0, y0b, x1, y1b = bx
        dx = (1 - a2) * -300
        good = revealed and i == sc["ci"]
        bad = revealed and not good
        # las respuestas FLOTAN: cada una con su propio vaivén suave
        fy = math.sin(t * 1.9 + i * 1.4) * 9
        fx = math.sin(t * 1.2 + i * 2.1) * 6
        if good:
            fy -= 10 * ease_out(min(1, (lt - rv) / 0.3))
        b2 = (x0 + dx + fx, y0b + fy, x1 + dx + fx, y1b + fy)
        lift = 9 - fy * 0.6
        if good:
            gg = 0.5 + 0.5 * math.sin(lt * 7)
            rr(d, (b2[0] - 10, b2[1] - 10, b2[2] + 10, b2[3] + 10), 36, GREEN + (int(60 + 60 * gg),))
        elif not bad:
            rr(d, (b2[0] - 4, b2[1] - 4, b2[2] + 4, b2[3] + 4), 32, acc + (28,))
        rr(d, (b2[0] + 5, b2[1] + lift, b2[2] + 5, b2[3] + lift), 28, (0, 0, 0, 90))
        rr(d, b2, 28, (24, 16, 44, 235) if not bad else (24, 16, 44, 130),
           outline=(GREEN if good else acc + ((90,) if bad else (200,))), width=5 if good else 3)
        # brillo de cristal en la mitad superior
        rr(d, (b2[0] + 10, b2[1] + 6, b2[2] - 10, b2[1] + (b2[3] - b2[1]) * 0.42), 22,
           (255, 255, 255, 14 if not bad else 6))
        # barra de votos
        fw = (b2[2] - b2[0] - 16) * pcs[i] / 100 * vote
        if fw > 30:
            rr(d, (b2[0] + 8, b2[1] + 8, b2[0] + 8 + fw, b2[3] - 8), 22,
               (GREEN + (200,)) if good else (acc + ((55,) if bad else (95,))))
        lc = (b2[0] + 62, (b2[1] + b2[3]) / 2)
        d.ellipse((lc[0] - 36, lc[1] - 36, lc[0] + 36, lc[1] + 36), fill=WHITE if good else (acc if not bad else acc + (110,)))
        d.text((lc[0], lc[1] + 3), LETTERS[i], font=tfont(42), fill=GREEN if good else WHITE, anchor="mm")
        tcol = WHITE if not bad else (255, 255, 255, 120)
        o = q["opciones"][i]
        tw = b2[2] - b2[0] - 280
        f, lines, lh = fit(d, o, tw, 110, 48, 28, 1.04)
        yy = lc[1] - lh * len(lines) / 2 + lh / 2 + 2
        for ln in lines:
            d.text((b2[0] + 125, yy), ln, font=f, fill=tcol, anchor="lm")
            yy += lh
        if vote > 0:
            d.text((b2[2] - 40, lc[1] + 2), f"{int(pcs[i] * vote)}%", font=tfont(40), fill=tcol, anchor="rm")
        if good:
            check(d, b2[2] - 150, lc[1], 40, GREEN, 10)
    # alerta al acertar / comentario en la extra
    if lt >= rv:
        lt2 = lt - rv
        if sc["extra"]:
            e = pop(lt, rv + 0.1, 0.4)
            pill(d, 540, 1545 + (1 - e) * 60, "¡ESCRÍBELO EN COMENTARIOS!", int(50 * max(e, 0.1)), YEL, INK, pad=(36, 18))
        else:
            e = pop(lt, rv + 0.5, 0.35)
            if e > 0:
                ax, ay = 380, 460 + (1 - e) * -120
                rr(d, (ax - 300 + 6, ay - 70 + 10, ax + 300 + 6, ay + 70 + 10), 30, (0, 0, 0, 110))
                rr(d, (ax - 300, ay - 70, ax + 300, ay + 70), 30, GREEN, outline=WHITE, width=5)
                d.text((ax, ay - 18), "¡CORRECTA!", font=tfont(58), fill=WHITE, anchor="mm")
                d.text((ax, ay + 36), "+1 PUNTO DE FAN", font=tfont(34), fill=INK, anchor="mm")
            burst(d, lt2 - 0.5, 380, 460)
    # viñeta roja al final de la cuenta atrás
    end = cd + COUNTDOWN
    if end - 2.5 <= lt < end:
        k = (lt - (end - 2.5)) / 2.5
        al = (0.35 + 0.65 * k) * (0.6 + 0.4 * (0.5 + 0.5 * math.cos((lt - cd) * 4 * math.pi)))
        v = _S.get("vig")
        if v is None:
            yy_, xx_ = np.mgrid[0:H, 0:W]
            dist = np.sqrt(((xx_ - W / 2) / (W / 2)) ** 2 + ((yy_ - H / 2) / (H / 2)) ** 2)
            v = _S["vig"] = Image.fromarray((np.clip((dist - 0.75) / 0.6, 0, 1) * 190).astype(np.uint8), "L")
        img.paste((230, 20, 40), (0, 0), v.point(lambda x, a_=al: int(x * a_)))


def draw_outro(img, d, sc, lt, t):
    img.paste(_S["outro_bg"])
    d = ImageDraw.Draw(img, "RGBA")
    banner(img, d, t)
    a = pop(lt, 0.05, 0.45)
    if a > 0:
        R = 280 * a
        g = 0.5 + 0.5 * math.sin(lt * 4)
        d.ellipse((540 - R - 22, 640 - R - 22, 540 + R + 22, 640 + R + 22), fill=_S["acc"] + (int(70 + 70 * g),))
        d.ellipse((540 - R - 9, 640 - R - 9, 540 + R + 9, 640 + R + 9), fill=_S["acc"])
        paste_c(img, _S["cam_big"], 540, 640, a)
        live_badge(d, 410, 360 + (1 - a) * 40, t, 30)
    b = pop(lt, 0.25, 0.45)
    if b > 0:
        y = 1000 + (1 - b) * 300
        rr(d, (90 + 6, y + 12, 990 + 6, y + 232 + 12), 36, (0, 0, 0, 110))
        rr(d, (90, y, 990, y + 232), 36, (20, 13, 38, 245), outline=_S["acc"], width=5)
        d.text((540, y + 80), "¿CUÁNTAS HAS ACERTADO?", font=tfont(66), fill=WHITE, anchor="mm")
        d.text((540, y + 162), "¡Dímelo en comentarios!", font=font(50), fill=YEL, anchor="mm")
    c2 = pop(lt, sc["shout_at"] - 0.15, 0.4)
    if c2 > 0:
        pulse = 1 + 0.07 * math.sin(lt * 9)
        pill(d, 540, 1340 + (1 - c2) * 500, "¡SÍGUEME PARA MÁS!", int(62 * pulse), YEL, INK)
    c3 = pop(lt, sc["shout_at"] + 0.2, 0.5)
    if c3 > 0:
        size = 210 * c3
        paste_c(img, _S["logo"], 540, 1510, size / _S["logo"].width)
    burst(d, lt - sc["shout_at"], 540, 1200, 1.8)


def render_frame(i):
    t = i / FPS
    scenes = _S["scenes"]
    sc = scenes[-1]
    for s in scenes:
        if s["start"] <= t < s["start"] + s["dur"]:
            sc = s
            break
    lt = t - sc["start"]
    bg = _S["bg"].copy()
    img = bg.copy()
    d = ImageDraw.Draw(img, "RGBA")
    {"hook": draw_hook, "q": draw_q, "outro": draw_outro}[sc["kind"]](img, d, sc, lt, t)
    out_t = sc["dur"] - lt
    if out_t < 0.2 and sc is not scenes[-1]:
        nxt = scenes[scenes.index(sc) + 1]
        if nxt["kind"] == "q":
            base = bg.copy()
            banner(base, ImageDraw.Draw(base, "RGBA"), t)
            img = Image.blend(base, img, max(0.0, out_t / 0.2))
    username(img)
    return img.tobytes()


# ------------------------------------------------------------------ portada

def portada(c, state, out_dir):
    _init(state)
    img = _S["hook_img"].copy()
    d = ImageDraw.Draw(img, "RGBA")
    R = 375
    rr(d, (540 - R - 24, 875 - R - 24, 540 + R + 24, 875 + R + 24), 80, _S["acc"] + (150,))
    rr(d, (540 - R - 10, 875 - R - 10, 540 + R + 10, 875 + R + 10), 70, YEL)
    paste_c(img, _S["hook_card"], 540, 875, R / 440)
    banner(img, d, 0.0, dy=95)
    live_badge(d, 200, 520, 0.0, 30)
    viewers(d, 480, 520, 0.0, 26)
    l1, l2 = c["portada"]["titulo"]
    text(d, (540, 1330), l1, tfont(90), WHITE, 11, INK, sh=10)
    f = tfont(178)
    while d.textlength(l2, font=f) > 1000:
        f = tfont(f.size - 4)
    text(d, (540, 1458), l2, f, YEL, 15, INK, sh=12)
    st = Image.new("RGBA", (900, 130), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    rr(sd, (8, 14, 892, 126), 52, (0, 0, 0, 80))
    rr(sd, (0, 4, 884, 116), 52, RED, outline=WHITE, width=7)
    f2 = tfont(58)
    while sd.textlength(c["portada"]["pegatina"], font=f2) > 800:
        f2 = tfont(f2.size - 3)
    sd.text((442, 62), c["portada"]["pegatina"], font=f2, fill=WHITE, anchor="mm")
    paste_c(img, st, 540, 1612, 0.95, angle=-3)
    p916 = os.path.join(out_dir, f"{c['video']}_9x16.png")
    p34 = os.path.join(out_dir, f"{c['video']}_3x4.png")
    full = img.copy()
    username(full, 1745)
    full.save(p916)
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
    build_audio(events, total, wav, zlib.crc32(c["video"].encode()) % 1000)
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

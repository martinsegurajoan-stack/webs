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
    tz = c["gancho"].get("teaser")
    if tz:  # GANCHO v2: primero se ve la PREGUNTA EXTRA bloqueada con alarma y luego la foto
        s1, d1 = voice.say(tz["voz"])
        s2, d2 = voice.say(c["gancho"]["voz"])
        ta = max(1.6, d1 + 0.2)
        ev += [("voice", s1, 0.03), ("fx", "impact", 0.0), ("fx", "siren", 0.0),
               ("fx", "whoosh", ta - 0.08), ("fx", "impact", ta), ("voice", s2, ta + 0.08)]
        for k in range(4):
            ev.append(("fx", "pop", 0.12 + k * 0.08))
        dur = ta + 0.08 + d2 + 0.35
        scenes.append({"kind": "hook", "start": 0.0, "dur": dur, "ta": ta})
    else:
        sig, d = voice.say(c["gancho"]["voz"])
        ev += [("voice", sig, 0.05), ("fx", "impact", 0.0), ("fx", "whoosh", 0.02)]
        dur = max(3.0, d + 0.45)
        scenes.append({"kind": "hook", "start": 0.0, "dur": dur})
    t = dur
    qs = c["preguntas"]
    n_reg = sum(1 for q in qs if not q.get("sin_respuesta"))
    for qi, q in enumerate(qs):
        extra = bool(q.get("sin_respuesta"))
        intro = extra and c.get("extra_intro_voz")
        if intro:  # escena de alarma: «PREGUNTA EXTRA · SOLO PARA FANS DE VERDAD»
            si, di = voice.say(c["extra_intro_voz"])
            ev += [("fx", "siren", t), ("fx", "impact", t + 0.15), ("fx", "impact", t + 0.32),
                   ("voice", si, t + 0.35), ("fx", "heart", t + 0.9), ("fx", "heart", t + 1.6)]
            di_ = 0.35 + di + 0.35
            scenes.append({"kind": "extra_intro", "start": t, "dur": di_})
            t += di_
        st = t
        etiqueta = "" if intro else ("¡Pregunta extra!" if extra else f"¡Pregunta {qi + 1}!")
        sig, dq = voice.say((f"{etiqueta} " + q.get("pregunta_voz", q["pregunta"])).strip())
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
    if c.get("final_voz"):  # FINAL v2: «¡AHORA DECIDES TÚ!» + encuesta del siguiente + comentario escribiéndose
        sc_, dc = voice.say(c.get("cierre_voz", "¿Cuántas has acertado?"))
        sw = 0.3 + dc + 0.1
        sf, df = voice.say(c["final_voz"])
        shout_at = sw + df + 0.1
        s2, d2 = voice.say("¡Sígueme para más!", shout=True)
        dur = shout_at + d2 + 1.0
        ev += [("fx", "whoosh", t), ("voice", sc_, t + 0.3), ("fx", "impact", t + sw), ("fx", "correct", t + sw + 0.05),
               ("voice", sf, t + sw + 0.1), ("voice", s2, t + shout_at), ("fx", "applause", t + shout_at)]
        for k in range(4):
            ev.append(("fx", "pop", t + sw + 0.5 + k * 0.12))
        scenes.append({"kind": "outro", "start": t, "dur": dur, "shout_at": shout_at, "sw": sw, "v2": True})
        return scenes, ev, t + dur
    sig, d = voice.say(c.get("cierre_voz", "¿Cuántas has acertado?"))
    ev += [("fx", "whoosh", t), ("voice", sig, t + 0.35)]
    sig_at = None
    if c.get("siguiente_voz"):  # «¿Quién quieres que sea el siguiente? ¡Coméntalo y apoya el vídeo!»
        sig_at = 0.35 + d + 0.15
        s3, d3 = voice.say(c["siguiente_voz"])
        ev += [("voice", s3, t + sig_at), ("fx", "pop", t + sig_at), ("fx", "correct", t + sig_at + 0.05)]
        d = sig_at - 0.35 + d3
    shout_at = 0.35 + d + 0.1
    sig2, d2 = voice.say("¡Sígueme para más!", shout=True)
    dur = max(3.6, shout_at + d2 + 1.0)
    ev += [("voice", sig2, t + shout_at), ("fx", "applause", t + shout_at)]
    scenes.append({"kind": "outro", "start": t, "dur": dur, "shout_at": shout_at, "sig_at": sig_at})
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


def sfx_siren(dur=1.3):
    sr = audio.SR
    tt = np.arange(int(dur * sr)) / sr
    f = 760 + 340 * np.sin(2 * np.pi * 2.4 * tt - np.pi / 2)
    ph = 2 * np.pi * np.cumsum(f) / sr
    sig = np.sin(ph) * 0.6 + np.sign(np.sin(ph)) * 0.15
    env = np.minimum(1, tt / 0.03) * np.clip((dur - tt) / 0.35, 0, 1)
    return 0.35 * sig * env


def build_audio(events, total, path, seed):
    from .personalidad import sfx_impact
    mix = audio.Mixer(total)
    fx = {"whoosh": audio.sfx_whoosh(), "pop": audio.sfx_pop(), "tick": audio.sfx_tick(), "tick_high": audio.sfx_tick(True),
          "tock": audio.sfx_tock(), "heart": audio.sfx_heartbeat(), "riser": audio.sfx_riser(COUNTDOWN),
          "buzz": audio.sfx_buzz_end(), "correct": audio.sfx_correct(), "applause": audio.sfx_applause(),
          "impact": sfx_impact(), "alert": sfx_alert(), "siren": sfx_siren()}
    gains = {"whoosh": 0.5, "pop": 0.6, "tick": 1.3, "tick_high": 1.45, "tock": 0.95, "heart": 0.85, "riser": 0.5,
             "buzz": 0.6, "correct": 0.9, "applause": 0.8, "impact": 0.75, "alert": 0.8, "siren": 0.45}
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


USER_COLS = [(255, 90, 90), (90, 200, 255), (120, 255, 140), (255, 200, 60), (255, 120, 220), (170, 140, 255),
             (255, 160, 80), (100, 240, 220), (200, 255, 90), (255, 140, 160)]
RATE_GUION = 1.0  # mensajes por segundo en el chat con guion (se pueden leer)


def _ucol(u):
    return USER_COLS[zlib.crc32(u.encode()) % len(USER_COLS)]


def _guion(c, r):
    """Chat con guion por pregunta: conversaciones entre usuarios (sin repetir mensajes), un MOD serio que
    dice la respuesta justo después de revelarla y relleno random si sobra hueco."""
    g = c.get("chat_guion")
    scenes = _S.get("scenes")
    _S["chat_q"] = {}
    if not g or not scenes:
        return
    mod = c.get("chat_mod", "")
    usados = set()
    relleno = [m for m in (c.get("chat_random") or []) + (c.get("chat") or [])]
    r.shuffle(relleno)
    todos = [m for b in g for k in ("antes", "despues") for _, m in b.get(k, [])]
    relleno = [m for m in relleno if m not in todos]

    def item(u, m):
        usados.add(m)
        return (u, _ucol(u), m, u == mod)

    def hueco():
        while relleno:
            m = relleno.pop()
            if m not in usados:
                return item(r.choice(CHAT_USERS)[0], m)
        return None

    for s in scenes:
        if s["kind"] != "q" or s["i"] >= len(g):
            continue
        b = g[s["i"]]
        n = int(s["dur"] * RATE_GUION) + 5
        rs = int((s["rv"] + 0.8) * RATE_GUION) + 3  # hueco del MOD (3 mensajes ya visibles al empezar)
        antes = [item(u, m) for u, m in b.get("antes", [])][:rs]
        while len(antes) < rs:
            x = hueco()
            if not x:
                break
            antes.append(x)
        seq = antes + ([item(*b["serio"])] if b.get("serio") else [])
        seq += [item(u, m) for u, m in b.get("despues", [])]
        while len(seq) < n:
            x = hueco()
            if not x:
                break
            seq.append(x)
        _S["chat_q"][s["i"]] = seq


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
    _S["teaser_bg"] = Image.blend(_S["hook_img"], Image.new("RGB", (W, H), (40, 4, 12)), 0.55)
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
    tema = c.get("chat") or []          # comentarios graciosos sobre el streamer
    raros = c.get("chat_random") or []  # cosas MUY random de vez en cuando
    while len(chat) < 400:  # sin mensajes repetidos seguidos
        msgs = (tema + CHAT_MSG[:6]) if tema else CHAT_MSG[:]
        r.shuffle(msgs)
        rnd = raros[:]
        r.shuffle(rnd)
        for i, m in enumerate(msgs):
            chat.append((r.choice(CHAT_USERS), m))
            if rnd and i % 4 == 3:
                chat.append((r.choice(CHAT_USERS), rnd.pop()))
    _S["chat"] = chat
    _guion(c, r)
    _S["polls"] = []
    for q in c["preguntas"]:
        v = [r.uniform(8, 40) for _ in range(4)]
        if q.get("encuesta"):  # porcentajes fijados a mano (p. ej. que la correcta no destaque)
            _S["polls"].append(list(q["encuesta"]))
            continue
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


def _chat_line(d, x, yy, wmax, user, col, msg, mod=False):
    sz = 30
    while sz > 20:
        fu = font(sz)
        wb = (d.textlength("MOD", font=tfont(sz - 8)) + 22) if mod else 0
        if wb + d.textlength(user + ": " + msg, font=fu) <= wmax:
            break
        sz -= 1
    fu = font(sz)
    if mod:  # insignia de moderador (el que responde en serio)
        fb = tfont(sz - 8)
        wbx = d.textlength("MOD", font=fb) + 14
        rr(d, (x, yy - sz * 0.45, x + wbx, yy + sz * 0.45), 8, GREEN)
        d.text((x + wbx / 2, yy + 1), "MOD", font=fb, fill=WHITE, anchor="mm")
        x += wbx + 8
    d.text((x, yy), user + ":", font=fu, fill=col, anchor="lm")
    wu = d.textlength(user + ": ", font=fu)
    d.text((x + wu, yy), msg, font=fu, fill=(200, 255, 210) if mod else WHITE, anchor="lm")


def chat_panel(img, d, t, box, idx0=0, rate=1.25, burst_t=None, seq=None, lt=0.0):
    x0, y0, x1, y1 = box
    rr(d, (x0 + 5, y0 + 9, x1 + 5, y1 + 9), 24, (0, 0, 0, 80))
    rr(d, box, 24, (14, 9, 28, 225), outline=_S["acc"] + (160,), width=3)
    d.text((x0 + 24, y0 + 30), "CHAT EN DIRECTO", font=tfont(30), fill=_S["acc"], anchor="lm")
    d.ellipse((x1 - 44, y0 + 22, x1 - 28, y0 + 38), fill=RED)
    if seq:
        rate = RATE_GUION
        n = int(lt * rate) + 3
        frac = (lt * rate) % 1
    else:
        n = int(t * rate) + idx0
        frac = (t * rate) % 1
    lines = 4
    lh = (y1 - y0 - 70) / lines
    slide = ease_out(min(1, frac / 0.25))
    for j in range(lines):
        k = n - (lines - 1 - j)
        if k < 0:
            continue
        yy = y0 + 70 + j * lh + lh / 2 + (1 - slide) * lh
        if yy > y1 - 12:
            continue
        if seq:
            user, col, msg, mod = seq[min(k, len(seq) - 1)]
            _chat_line(d, x0 + 24, yy, x1 - x0 - 44, user, col, msg, mod)
            continue
        (user, col), msg = _S["chat"][k % len(_S["chat"])]
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

def _red_vig(img, al):
    v = _S.get("vig")
    if v is None:
        yy_, xx_ = np.mgrid[0:H, 0:W]
        dist = np.sqrt(((xx_ - W / 2) / (W / 2)) ** 2 + ((yy_ - H / 2) / (H / 2)) ** 2)
        v = _S["vig"] = Image.fromarray((np.clip((dist - 0.75) / 0.6, 0, 1) * 190).astype(np.uint8), "L")
    img.paste((230, 20, 40), (0, 0), v.point(lambda x, a_=max(0.0, min(1.0, al)): int(x * a_)))


def _beams(d, lt):
    """Luces de alarma que barren desde las esquinas."""
    for k, (bx, base) in enumerate([(0, 0.25), (W, math.pi - 0.25)]):
        a = base + math.sin(lt * 4.5 + k * 1.7) * 0.75 * (1 if k == 0 else -1)
        for wdt, al in ((0.22, 40), (0.1, 55)):
            p1 = (bx + math.cos(a - wdt) * 2400, 230 + math.sin(a - wdt) * 2400)
            p2 = (bx + math.cos(a + wdt) * 2400, 230 + math.sin(a + wdt) * 2400)
            d.polygon([(bx, 230), p1, p2], fill=(255, 40, 60, al))


def _glitch(img, k):
    if k <= 0:
        return
    r, g, b = img.split()
    off = int(18 * k)
    r = r.transform(r.size, Image.AFFINE, (1, 0, -off, 0, 1, 0))
    b = b.transform(b.size, Image.AFFINE, (1, 0, off, 0, 1, 0))
    img.paste(Image.merge("RGB", (r, g, b)))


def _padlock(d, cx, cy, s, col):
    d.arc((cx - s * 0.55, cy - s * 1.15, cx + s * 0.55, cy + s * 0.1), 180, 360, fill=col, width=max(3, int(s * 0.22)))
    rr(d, (cx - s * 0.8, cy - s * 0.4, cx + s * 0.8, cy + s * 0.75), s * 0.2, col)
    d.ellipse((cx - s * 0.14, cy - s * 0.05, cx + s * 0.14, cy + s * 0.23), fill=INK)


def _draw_teaser(img, sc, lt, t):
    """Gancho v2, fase 1: la pregunta extra bloqueada, con alarma, sacudida y destello."""
    c = _S["c"]
    tz = c["gancho"]["teaser"]
    img.paste(_S["teaser_bg"])
    d = ImageDraw.Draw(img, "RGBA")
    _beams(d, lt)
    _red_vig(img, 0.45 + 0.4 * (0.5 + 0.5 * math.sin(lt * 2 * math.pi * 2.4)))
    d = ImageDraw.Draw(img, "RGBA")
    sh = math.sin(lt * 60) * 18 * max(0, 1 - lt / 0.4)
    # titular que cae de golpe
    k = ease_out(min(1, lt / 0.22))
    sz = 1.7 - 0.7 * k
    text(d, (370 + sh, 410), "LA ÚLTIMA", tfont(int(92 * sz)), WHITE, 10, INK, sh=8)
    text(d, (370 + sh, 530), "PREGUNTA", tfont(int(122 * sz)), RED, 12, WHITE, sh=10)
    cam_frame(img, d, t, 740, 330, c.get("nombre_cam", c["nombre"].upper()))
    # tarjeta con la pregunta extra
    b = pop(lt, 0.05, 0.3)
    fq = math.sin(t * 1.4) * 5
    y0, y1 = 655 + fq, 865 + fq
    cy = (y0 + y1) / 2
    hh = (y1 - y0) / 2 * (0.8 + 0.2 * b)
    box = (70 + sh, cy - hh, 1010 + sh, cy + hh)
    gl = 0.5 + 0.5 * math.sin(lt * 12)
    rr(d, (box[0] - 10, box[1] - 10, box[2] + 10, box[3] + 10), 36, RED + (int(60 + 80 * gl),))
    rr(d, box, 30, (20, 10, 26, 245), outline=RED, width=6)
    f, lines, lh = fit(d, tz["pregunta"], 860, 150, 62, 34, 1.06)
    yy = cy + 12 - lh * len(lines) / 2 + lh / 2
    for ln in lines:
        d.text((540 + sh, yy), ln, font=f, fill=WHITE, anchor="mm")
        yy += lh
    pill(d, 540 + sh, box[1], f"PREGUNTA {c.get('extra_nombre', 'EXTRA')} · SOLO FANS", 36, RED, WHITE, pad=(26, 12))
    # opciones bloqueadas
    for i, bx in enumerate(opt_boxes()):
        a2 = pop(lt, 0.12 + i * 0.08, 0.25)
        if a2 <= 0:
            continue
        x0, yb0, x1, yb1 = bx
        dx = (1 - a2) * 400 + math.sin(lt * 38 + i * 2) * 3 + sh
        b2 = (x0 + dx, yb0, x1 + dx, yb1)
        rr(d, (b2[0] + 5, b2[1] + 9, b2[2] + 5, b2[3] + 9), 28, (0, 0, 0, 90))
        rr(d, b2, 28, (30, 14, 34, 235), outline=RED + (200,), width=3)
        lc = (b2[0] + 62, (b2[1] + b2[3]) / 2)
        d.ellipse((lc[0] - 36, lc[1] - 36, lc[0] + 36, lc[1] + 36), fill=RED)
        d.text((lc[0], lc[1] + 3), LETTERS[i], font=tfont(42), fill=WHITE, anchor="mm")
        d.text((b2[0] + 130, lc[1] + 2), "? ? ? ? ? ?", font=tfont(46), fill=(255, 255, 255, 150), anchor="lm")
        _padlock(d, b2[2] - 70, lc[1] + 4, 26, YEL)
    e = pop(lt, 0.4, 0.3)
    if e > 0:
        pulse = 1 + 0.06 * math.sin(lt * 10)
        text(d, (540, 1555 + (1 - e) * 80), tz.get("reto", "¿LLEGAS HASTA AQUÍ?"), tfont(int(92 * e * pulse)), YEL, 12, INK, sh=10)
    banner(img, d, t)
    _glitch(img, 1 - lt / 0.3 if lt < 0.3 else 0)
    if lt < 0.14:
        img.paste(WHITE, (0, 0), Image.new("L", (W, H), int(140 * (1 - lt / 0.14))))
    ta = sc["ta"]
    if lt > ta - 0.1:  # destello de paso a la foto
        img.paste(WHITE, (0, 0), Image.new("L", (W, H), int(200 * (lt - (ta - 0.1)) / 0.1)))


def draw_extra_intro(img, d, sc, lt, t):
    """Antes de la extra: alarma, «PREGUNTA EXTRA» que cae con glitch y «SOLO PARA FANS DE VERDAD»."""
    d.rectangle((0, 0, W, H), fill=(0, 0, 0, 120))
    _beams(d, lt)
    particles(d, t)
    _red_vig(img, 0.5 + 0.45 * (0.5 + 0.5 * math.sin(lt * 2 * math.pi * 2.2)))
    d = ImageDraw.Draw(img, "RGBA")
    sh = math.sin(lt * 60) * 20 * max(0, 1 - abs(lt - 0.32) / 0.35) if lt > 0.15 else 0
    a = pop(lt, 0.0, 0.35)
    if a > 0:
        g = 0.5 + 0.5 * math.sin(lt * 9)
        R = 175 * a * (1 + 0.03 * math.sin(lt * 7))
        d.ellipse((540 - R - 22 + sh, 560 - R - 22, 540 + R + 22 + sh, 560 + R + 22), fill=RED + (int(80 + 100 * g),))
        d.ellipse((540 - R - 9 + sh, 560 - R - 9, 540 + R + 9 + sh, 560 + R + 9), fill=YEL)
        paste_c(img, _S["cam_big"], 540 + sh, 560, R / 280)
    for k, (word, y, size, col, st, at) in enumerate([("PREGUNTA", 860, 150, WHITE, RED, 0.15), (_S["c"].get("extra_nombre", "EXTRA"), 1040, 230, RED, WHITE, 0.32)]):
        if lt < at:
            continue
        kk = ease_out(min(1, (lt - at) / 0.16))
        fw = tfont(int(size * (2.0 - kk)))
        while d.textlength(word, font=fw) > 660 and fw.size > 40:  # palabras largas («EXCLUSIVA») caben entre los avisos
            fw = tfont(fw.size - 6)
        text(d, (540 + sh, y), word, fw, col, 14, st, sh=12)
    if lt > 0.32:
        p = 0.5 + 0.5 * math.sin(lt * 8)
        warn_icon(d, 140 + sh, 1040, 52 + 8 * p, INK, YEL)
        warn_icon(d, 940 + sh, 1040, 52 + 8 * p, INK, YEL)
    e = pop(lt, 0.6, 0.35)
    if e > 0:
        pill(d, 540, 1225 + (1 - e) * 80, "SOLO PARA FANS DE VERDAD", int(56 * max(e, 0.1)), YEL, INK, pad=(36, 18))
    banner(img, d, t)
    if 0.32 <= lt < 0.55:
        _glitch(img, 1 - (lt - 0.32) / 0.23)
    for at in (0.15, 0.32):
        if at <= lt < at + 0.1:
            img.paste(WHITE, (0, 0), Image.new("L", (W, H), int(170 * (1 - (lt - at) / 0.1))))


def draw_hook(img, d, sc, lt, t):
    c = _S["c"]
    if sc.get("ta") is not None:
        if lt < sc["ta"]:
            return _draw_teaser(img, sc, lt, t)
        lt -= sc["ta"]
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
    chat_panel(img, d, t, (70, 330 + (1 - a) * 30, 690, 590 + (1 - a) * 30), idx0=sc["i"] * 7,
               seq=_S.get("chat_q", {}).get(sc["i"]), lt=lt)
    cam_frame(img, d, t, 720, 325, _S["c"].get("nombre_cam", _S["c"]["nombre"].upper()))
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
    lab = f"PREGUNTA {_S['c'].get('extra_nombre', 'EXTRA')} · SOLO FANS" if sc["extra"] else f"PREGUNTA {sc['i'] + 1}/{sc['n']}"
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
                ax, ay = 540, 748 + (1 - e) * -120
                rr(d, (ax - 300 + 6, ay - 70 + 10, ax + 300 + 6, ay + 70 + 10), 30, (0, 0, 0, 110))
                rr(d, (ax - 300, ay - 70, ax + 300, ay + 70), 30, GREEN, outline=WHITE, width=5)
                d.text((ax, ay - 18), "¡CORRECTA!", font=tfont(58), fill=WHITE, anchor="mm")
                d.text((ax, ay + 36), "+1 PUNTO DE FAN", font=tfont(34), fill=INK, anchor="mm")
            burst(d, lt2 - 0.5, 540, 748)
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


def _outro_v2(img, d, sc, lt, t):
    """Final v2: «¿CUÁNTAS HAS ACERTADO?» → «¡AHORA DECIDES TÚ!» con encuesta del siguiente streamer
    (barras que compiten), comentario que se escribe solo con propuestas y flecha hacia él."""
    c = _S["c"]
    acc = _S["acc"]
    sw = sc["sw"]
    lt2 = lt - sw
    # corazones subiendo detrás de todo
    if lt2 > 0:
        for k in range(16):
            ph = (lt2 * 0.42 + k / 16) % 1
            hx = 90 + (k * 137) % 900 + math.sin(lt * 2 + k) * 25
            _heart(d, hx, 1650 - ph * 1450, 13 + (k % 3) * 6, (255, 60 + (k % 4) * 30, 120, int(170 * (1 - ph))))
    banner(img, d, t)
    sh = math.sin(lt2 * 55) * 16 * max(0, 1 - lt2 / 0.35) if lt2 > 0 else 0
    # foto
    a = pop(lt, 0.05, 0.4)
    if a > 0:
        g = 0.5 + 0.5 * math.sin(lt * 4)
        R = (150 if lt2 > 0 else 230) * a * (1 + 0.025 * math.sin(lt * 6))
        cy = 600 if lt2 > 0 else 680
        d.ellipse((540 - R - 20 + sh, cy - R - 20, 540 + R + 20 + sh, cy + R + 20), fill=acc + (int(70 + 70 * g),))
        d.ellipse((540 - R - 8 + sh, cy - R - 8, 540 + R + 8 + sh, cy + R + 8), fill=YEL)
        paste_c(img, _S["cam_big"], 540 + sh, cy, R / 280)
    if lt2 < 0:
        b = pop(lt, 0.2, 0.4)
        if b > 0:
            y = 1020 + (1 - b) * 200
            rr(d, (96, y + 12, 996, y + 232 + 12), 36, (0, 0, 0, 110))
            rr(d, (90, y, 990, y + 232), 36, (20, 13, 38, 245), outline=acc, width=5)
            d.text((540, y + 80), "¿CUÁNTAS HAS ACERTADO?", font=tfont(66), fill=WHITE, anchor="mm")
            d.text((540, y + 162), "¡Dímelo en comentarios!", font=font(50), fill=YEL, anchor="mm")
        return
    # titular que cae
    k = ease_out(min(1, lt2 / 0.2))
    text(d, (540 + sh, 370), "¡AHORA DECIDES TÚ!", tfont(int(96 * (1.6 - 0.6 * k))), YEL, 13, INK, sh=10)
    # pregunta
    e = pop(lt2, 0.1, 0.35)
    y = 790 + (1 - e) * 60
    rr(d, (96, y + 10, 996, y + 150 + 10), 32, (0, 0, 0, 110))
    rr(d, (90, y, 990, y + 150), 32, (20, 13, 38, 245), outline=YEL, width=6)
    d.text((540, y + 48), "¿QUIÉN QUIERES QUE SEA", font=tfont(54), fill=WHITE, anchor="mm")
    d.text((540, y + 108), "EL SIGUIENTE?", font=tfont(70), fill=YEL, anchor="mm")
    # encuesta en directo: las barras compiten
    names = c.get("siguiente", [])[:4]
    base = [31, 27, 23, 19]
    vals = [base[i] + 5 * math.sin(lt2 * 1.8 + i * 1.9) for i in range(len(names))]
    tot = sum(vals) or 1
    pcs = [v / tot * 100 for v in vals]
    lead = max(range(len(pcs)), key=lambda i: pcs[i]) if pcs else -1
    grow = ease_out(min(1, max(0, (lt2 - 0.5) / 1.2)))
    for i, nm in enumerate(names):
        ai = pop(lt2, 0.5 + i * 0.12, 0.3)
        if ai <= 0:
            continue
        y0 = 970 + i * 92
        dx = (1 - ai) * -400
        bx = (90 + dx, y0, 990 + dx, y0 + 78)
        rr(d, (bx[0] + 5, bx[1] + 8, bx[2] + 5, bx[3] + 8), 24, (0, 0, 0, 90))
        rr(d, bx, 24, (24, 16, 44, 235), outline=(YEL if i == lead else acc) + (220,), width=4 if i == lead else 3)
        fw = (bx[2] - bx[0] - 12) * pcs[i] / 100 * grow * 1.6
        if fw > 30:
            rr(d, (bx[0] + 6, bx[1] + 6, bx[0] + 6 + fw, bx[3] - 6), 20, (YEL + (150,)) if i == lead else (acc + (110,)))
        d.text((bx[0] + 34, (bx[1] + bx[3]) / 2 + 2), nm, font=tfont(44), fill=WHITE, anchor="lm")
        d.text((bx[2] - 30, (bx[1] + bx[3]) / 2 + 2), f"{int(pcs[i] * grow)}%", font=tfont(42), fill=WHITE, anchor="rm")
        if i == lead and grow > 0.5:
            _heart(d, bx[2] - 150, (bx[1] + bx[3]) / 2 - 2, 15, (255, 60, 110))
    # comentario que se escribe solo
    ec = pop(lt2, 1.0, 0.35)
    if ec > 0:
        y0 = 1345 + (1 - ec) * 60
        rr(d, (96, y0 + 8, 966, y0 + 96), 46, (0, 0, 0, 100))
        rr(d, (90, y0, 960, y0 + 88), 44, WHITE)
        d.ellipse((108, y0 + 14, 168, y0 + 74), fill=acc)
        d.text((138, y0 + 46), "TÚ", font=tfont(26), fill=WHITE, anchor="mm")
        frases = c.get("siguiente_escribe") or [f"que sea {n}!!" for n in c.get("siguiente", [])]
        per = 1.7
        tl = max(0.0, lt2 - 1.0)
        fr = frases[int(tl / per) % len(frases)] if frases else ""
        u = tl % per
        n = int(len(fr) * min(1, u / 0.85)) if u < 1.3 else int(len(fr) * max(0, 1 - (u - 1.3) / 0.35))
        txt = fr[:n]
        fnt = font(42)
        if txt:
            d.text((190, y0 + 45), txt, font=fnt, fill=INK, anchor="lm")
        else:
            d.text((190, y0 + 45), "Añade un comentario...", font=fnt, fill=(150, 150, 160), anchor="lm")
        if (lt * 2.5) % 1 < 0.55:
            cx = 190 + (d.textlength(txt, font=fnt) if txt else 0) + 4
            d.rectangle((cx, y0 + 22, cx + 4, y0 + 68), fill=acc)
        d.polygon([(900, y0 + 26), (938, y0 + 44), (900, y0 + 62), (908, y0 + 44)], fill=acc)
        bo = math.sin(lt * 8) * 14
        ax = 1035 + bo
        d.polygon([(ax - 40, y0 + 44), (ax, y0 + 14), (ax, y0 + 30), (ax + 30, y0 + 30), (ax + 30, y0 + 58),
                   (ax, y0 + 58), (ax, y0 + 74)], fill=YEL, outline=INK)
    c2 = pop(lt, sc["shout_at"] - 0.15, 0.4)
    if c2 > 0:
        pulse = 1 + 0.07 * math.sin(lt * 9)
        pill(d, 500, 1530 + (1 - c2) * 400, "¡SÍGUEME PARA MÁS!", int(60 * pulse), YEL, INK)
    c3 = pop(lt, sc["shout_at"] + 0.2, 0.5)
    if c3 > 0:
        paste_c(img, _S["logo"], 935, 1530, 130 * c3 / _S["logo"].width)
    burst(d, lt2, 540, 860, 1.6)
    burst(d, lt - sc["shout_at"], 500, 1450, 1.8)


def draw_outro(img, d, sc, lt, t):
    img.paste(_S["outro_bg"])
    d = ImageDraw.Draw(img, "RGBA")
    if sc.get("v2"):
        return _outro_v2(img, d, sc, lt, t)
    banner(img, d, t)
    a = pop(lt, 0.05, 0.45)
    if a > 0:
        R = 280 * a
        g = 0.5 + 0.5 * math.sin(lt * 4)
        d.ellipse((540 - R - 22, 640 - R - 22, 540 + R + 22, 640 + R + 22), fill=_S["acc"] + (int(70 + 70 * g),))
        d.ellipse((540 - R - 9, 640 - R - 9, 540 + R + 9, 640 + R + 9), fill=_S["acc"])
        paste_c(img, _S["cam_big"], 540, 640, a)
        live_badge(d, 410, 360 + (1 - a) * 40, t, 30)
    sa = sc.get("sig_at")
    if sa is not None and lt >= sa - 0.1:
        _outro_siguiente(img, d, sc, lt, t, sa)
        return
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


def _heart(d, cx, cy, s, col):
    d.ellipse((cx - s, cy - s * 0.75, cx, cy + s * 0.2), fill=col)
    d.ellipse((cx, cy - s * 0.75, cx + s, cy + s * 0.2), fill=col)
    d.polygon([(cx - s * 0.97, cy - s * 0.1), (cx + s * 0.97, cy - s * 0.1), (cx, cy + s * 1.0)], fill=col)


BURBUJAS = [(240, 430, -6), (850, 450, 5), (205, 700, 4), (875, 720, -5), (255, 925, 3), (830, 935, -3)]


def _outro_siguiente(img, d, sc, lt, t, sa):
    """Cierre: «¿QUIÉN QUIERES QUE SEA EL SIGUIENTE?» con comentarios de nombres que saltan alrededor."""
    lt2 = lt - sa
    acc = _S["acc"]
    # corazones subiendo
    for k in range(14):
        ph = (lt2 * 0.45 + k / 14) % 1
        hx = 120 + (k * 137) % 840 + math.sin(lt * 2 + k) * 25
        hy = 1700 - ph * 1500
        _heart(d, hx, hy, 14 + (k % 3) * 6, (255, 60 + (k % 4) * 30, 120, int(200 * (1 - ph))))
    g = 0.5 + 0.5 * math.sin(lt * 4)
    R = 280 * (1 + 0.025 * math.sin(lt * 6))
    d.ellipse((540 - R - 22, 640 - R - 22, 540 + R + 22, 640 + R + 22), fill=acc + (int(70 + 70 * g),))
    d.ellipse((540 - R - 9, 640 - R - 9, 540 + R + 9, 640 + R + 9), fill=YEL)
    paste_c(img, _S["cam_big"], 540, 640, R / 280)
    live_badge(d, 410, 360, t, 30)
    # comentarios con propuestas (salen uno a uno y flotan)
    for k, nm in enumerate(_S["c"].get("siguiente", [])[:len(BURBUJAS)]):
        e = pop(lt2, 0.25 + k * 0.32, 0.35)
        if e <= 0:
            continue
        bx, by, ang = BURBUJAS[k]
        by += math.sin(t * 2 + k) * 8
        u = CHAT_USERS[k % len(CHAT_USERS)]
        lay = Image.new("RGBA", (440, 130), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        fm = tfont(40)
        w = max(ld.textlength(nm, font=fm), ld.textlength(u[0], font=font(26))) + 50
        x0 = (440 - w) / 2
        rr(ld, (x0 + 4, 12, x0 + w + 4, 112), 26, (0, 0, 0, 90))
        rr(ld, (x0, 6, x0 + w, 106), 26, WHITE)
        ld.polygon([(x0 + 40, 104), (x0 + 72, 104), (x0 + 36, 126)], fill=WHITE)
        ld.text((x0 + 25, 32), u[0], font=font(26), fill=tuple(int(v * 0.7) for v in u[1]), anchor="lm")
        ld.text((x0 + 25, 74), nm, font=fm, fill=INK, anchor="lm")
        paste_c(img, lay, bx, by, 0.6 + 0.4 * e, angle=ang)
    # tarjeta con la pregunta
    e = pop(lt2, 0.0, 0.4)
    y = 990 + (1 - e) * 60
    sz = 1 + 0.04 * max(0, math.sin(lt2 * 7)) * (1 if lt2 < 1.2 else 0)
    rr(d, (90 + 6, y + 12, 990 + 6, y + 280 + 12), 36, (0, 0, 0, 110))
    rr(d, (90, y, 990, y + 280), 36, (20, 13, 38, 245), outline=YEL, width=6)
    d.text((540, y + 66), "¿QUIÉN QUIERES QUE SEA", font=tfont(int(62 * sz)), fill=WHITE, anchor="mm")
    d.text((540, y + 140), "EL SIGUIENTE?", font=tfont(int(80 * sz)), fill=YEL, anchor="mm")
    f = font(44)
    s1 = "¡Coméntalo y apoya el vídeo!"
    wv = d.textlength(s1, font=f)
    d.text((540 + 26, y + 222), s1, font=f, fill=WHITE, anchor="mm")
    hb = 1 + 0.18 * max(0, math.sin(lt * 8))
    _heart(d, 540 - wv / 2 - 14, y + 218, 20 * hb, (255, 60, 110))
    c2 = pop(lt, sc["shout_at"] - 0.15, 0.4)
    if c2 > 0:
        pulse = 1 + 0.07 * math.sin(lt * 9)
        pill(d, 540, 1365 + (1 - c2) * 500, "¡SÍGUEME PARA MÁS!", int(62 * pulse), YEL, INK)
    c3 = pop(lt, sc["shout_at"] + 0.2, 0.5)
    if c3 > 0:
        paste_c(img, _S["logo"], 540, 1530, 200 * c3 / _S["logo"].width)
    burst(d, lt2, 540, 1130, 1.6)
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
    {"hook": draw_hook, "q": draw_q, "outro": draw_outro, "extra_intro": draw_extra_intro}[sc["kind"]](img, d, sc, lt, t)
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

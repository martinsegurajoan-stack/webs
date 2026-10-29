"""Vídeo de MISTERIO CRIMINAL (Hora del Quiz ⚡): historia narrada con imágenes cinematográficas.

Reutiliza del proyecto: caché de voz ElevenLabs, sincronía de subtítulos (`personalidad.align_words`),
efectos y mezcla (`audio`) y exportación a MP4. Estética propia: oscura y elegante, colores de marca
(amarillo, turquesa, morado) solo en detalles, tipografías Montserrat y Bebas Neue.
"""

import hashlib
import json
import math
import os
import random
import re
import subprocess
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from . import audio
from .personalidad import align_words, caption_chunks
from .render import FPS, USUARIO, W, H, ease_in, ease_out, ease_out_back

BASE = os.path.join(os.path.dirname(__file__), "..")
CACHE = os.path.join(BASE, "assets", "voz_eleven", "cache")
FUENTES = os.path.join(BASE, "fuentes")
MODEL = "eleven_v4"
SR = audio.SR

YEL = (255, 212, 0)
TURQ = (0, 222, 205)
PURP = (150, 80, 255)
WHITE = (255, 255, 255)
XF = 0.4            # fundido entre planos
MAX_TOTAL = 88.0    # margen bajo los 90 s
MAX_TEMPO = 1.14    # nunca acelerar más de esto


def F(kind, size):
    name = {"bold": "serio_bold.ttf", "semi": "serio_semi.ttf", "titulo": "serio_titulo.ttf"}[kind]
    key = (kind, int(size))
    if key not in _FC:
        _FC[key] = ImageFont.truetype(os.path.join(FUENTES, name), int(size))
    return _FC[key]


_FC = {}


# ---------------------------------------------------------------- voz

def prompt_de(c, clip):
    return f"{c['voz']['estilo']} {clip['texto']}"


def ruta_voz(c, clip):
    key = hashlib.sha1(f"{c['voz']['voice_id']}|{MODEL}|{prompt_de(c, clip)}".encode("utf-8")).hexdigest()[:16]
    return os.path.join(CACHE, key + ".mp3")


def _decode(path):
    raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", str(SR),
                                   "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32).astype(np.float64)


def _compact(sig, max_pause=0.35):
    """Recorta el silencio de los extremos y acorta las pausas internas largas (sin acelerar)."""
    idx = np.where(np.abs(sig) > 0.01)[0]
    if len(idx) == 0:
        return sig
    sig = sig[max(0, idx[0] - int(0.02 * SR)): idx[-1] + int(0.08 * SR)]
    fr = int(0.01 * SR)
    n = len(sig) // fr
    e = np.sqrt(np.mean(sig[: n * fr].reshape(n, fr) ** 2, axis=1))
    sil = e < e.max() * 0.04
    keep = np.ones(len(sig), bool)
    k = 0
    while k < n:
        if sil[k]:
            j = k
            while j < n and sil[j]:
                j += 1
            run = (j - k) * 0.01
            if run > max_pause:
                cut0 = int((k * 0.01 + max_pause / 2) * SR)
                cut1 = int((j * 0.01 - max_pause / 2) * SR)
                keep[cut0:cut1] = False
            k = j
        else:
            k += 1
    return sig[keep]


def _atempo(sig, tempo):
    if abs(tempo - 1.0) < 1e-3:
        return sig
    p = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-af", f"atempo={tempo:.4f}", "-f", "f32le", "-"],
                       input=sig.astype(np.float32).tobytes(), stdout=subprocess.PIPE, check=True)
    return np.frombuffer(p.stdout, np.float32).astype(np.float64)


def faltan(c):
    return [{"archivo": os.path.relpath(ruta_voz(c, cl), BASE), "texto": prompt_de(c, cl)}
            for cl in c["clips"] if not os.path.exists(ruta_voz(c, cl))]


# ---------------------------------------------------------------- línea de tiempo

def _destacados(c, words):
    """Color por palabra: frases/nombres de marca (amarillo / turquesa)."""
    norm = [re.sub(r"[^\wáéíóúñü]", "", w.lower()) for w in words]
    col = [None] * len(words)
    for color, lista in (("t", c["destacar"]["turquesa"]), ("y", c["destacar"]["amarillo"])):
        for fr in lista:
            fw = fr.lower().split()
            for i in range(len(norm) - len(fw) + 1):
                if norm[i:i + len(fw)] == fw:
                    for j in range(i, i + len(fw)):
                        col[j] = col[j] or color
    return col


def build(c, sin_voz=False):
    # 1) audios procesados (sin acelerar todavía)
    sigs = []
    for cl in c["clips"]:
        p = ruta_voz(c, cl)
        if os.path.exists(p) and not sin_voz:
            sigs.append(_compact(_decode(p)))
        else:
            sigs.append(None)
    raw_d = [len(s) / SR if s is not None else len(cl["texto"]) / 14 for s, cl in zip(sigs, c["clips"])]
    fijo = 0.3 + sum(cl.get("pausa", 0.2) + cl.get("silencio_antes", 0) + cl.get("cuenta_atras", 0)
                     for cl in c["clips"])
    tempo = min(MAX_TEMPO, max(1.0, sum(raw_d) / max(1.0, MAX_TOTAL - fijo)))
    # 2) cronología
    t = 0.3
    clips, shots, subs, voices = [], [], [], []
    for cl, s, d0 in zip(c["clips"], sigs, raw_d):
        t += cl.get("silencio_antes", 0)
        sig = _atempo(s, tempo) if s is not None else None
        d = len(sig) / SR if sig is not None else d0 / tempo
        if sig is not None:
            sig = sig / (np.max(np.abs(sig)) or 1) * 0.9
        voices.append((sig, t))
        words, times = align_words(cl["texto"], sig, d)
        cols = _destacados(c, words)
        idx = 0
        for ch in caption_chunks(words, times, t, maxw=3, maxc=18):
            ch["cols"] = cols[idx: idx + len(ch["words"])]  # color de cada palabra del golpe
            idx += len(ch["words"])
            subs.append(ch)
        end_voice = t + d
        extra = cl.get("pausa", 0.2) + cl.get("cuenta_atras", 0)
        info = {"clip": cl, "start": t, "voice_end": end_voice, "end": end_voice + extra}
        if cl.get("cuenta_atras"):
            info["cd_start"] = end_voice + cl.get("pausa", 0.2)
        clips.append(info)
        for k, pl in enumerate(cl["planos"]):
            st = t + d * pl.get("desde", 0.0)
            shots.append(dict(pl, start=st, clip=len(clips) - 1))
        t = info["end"]
    total = t
    for k, sh in enumerate(shots):
        sh["end"] = shots[k + 1]["start"] if k + 1 < len(shots) else total
    shots[0]["start"] = 0.0
    # 3) subtítulos: el último golpe de cada frase no pisa el siguiente
    for k in range(len(subs) - 1):
        subs[k]["end"] = min(subs[k]["end"], subs[k + 1]["start"])
    return {"clips": clips, "shots": shots, "subs": subs, "voices": voices, "total": total, "tempo": tempo}


# ---------------------------------------------------------------- audio

def _lp(x, fc):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x))


def _env_note(n, a, r):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / r)


def music_thriller(dur, seed=3):
    """Base oscura original: dron grave, acordes menores filtrados, notas sueltas de piano con eco,
    pulso grave y textura de ruido. Generada aquí: sin licencias de terceros."""
    n = int(dur * SR) + SR
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    out = 0.35 * np.sin(2 * np.pi * 55 * t) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * t))
    out += 0.18 * np.sin(2 * np.pi * 82.41 * t + 0.6 * np.sin(2 * np.pi * 0.11 * t))
    saw = 2 * ((t * 55.3) % 1) - 1
    out += 0.12 * _lp(saw, 180)
    # acordes: Am – F – Dm – E (4,8 s cada uno)
    chords = [[57, 60, 64], [53, 57, 60], [50, 53, 57], [52, 56, 59]]
    seg = 4.8
    pad = np.zeros(n)
    k = 0
    while k * seg < dur + seg:
        s0 = int(k * seg * SR)
        if s0 >= n:
            break
        L = int((seg + 2.0) * SR)
        tt = np.arange(L) / SR
        env = np.minimum(1, tt / 1.6) * np.minimum(1, np.maximum(0, (seg + 2.0 - tt) / 2.0))
        sig = np.zeros(L)
        for m in chords[k % 4]:
            f = 440 * 2 ** ((m - 12 - 69) / 12)
            for det in (0.997, 1.0, 1.004):
                sig += np.sin(2 * np.pi * f * det * tt + rng.uniform(0, 6))
        e = min(n, s0 + L)
        pad[s0:e] += (0.05 * env * sig)[: e - s0]
        k += 1
    out += _lp(pad, 900)
    # notas de piano sueltas (La menor) con eco
    notes = [69, 72, 76, 74, 71, 67, 64]
    pn = np.zeros(n)
    tn = 1.2
    while tn < dur:
        m = rng.choice(notes)
        f = 440 * 2 ** ((m - 69) / 12)
        L = int(2.4 * SR)
        tt = np.arange(L) / SR
        s = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt) + 0.12 * np.sin(2 * np.pi * 3.01 * f * tt))
        s *= _env_note(L, 0.004, 0.7)
        for dly, g in ((0, 1.0), (0.38, 0.35), (0.76, 0.15)):
            s0 = int((tn + dly) * SR)
            e = min(n, s0 + L)
            if s0 < n:
                pn[s0:e] += 0.07 * g * s[: e - s0]
        tn += rng.choice([2.4, 3.2, 4.0])
    out += pn
    # textura de ruido muy suave
    out += 0.02 * _lp(rng.standard_normal(n), 400)
    out = out[: int(dur * SR)]
    out /= np.max(np.abs(out)) or 1
    f_ = int(1.0 * SR)
    out[:f_] *= np.linspace(0, 1, f_)
    out[-int(1.5 * SR):] *= np.linspace(1, 0, int(1.5 * SR))
    return out


def sfx_golpe(power=1.0):
    t = np.arange(int(1.6 * SR)) / SR
    f = 32 + 70 * np.exp(-t * 9)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.6)
    noise = _lp(np.random.default_rng(5).standard_normal(len(t)), 900) * np.exp(-t * 7) * 0.6
    return 0.9 * power * (boom + noise)


def sfx_pista():
    t = np.arange(int(1.4 * SR)) / SR
    ping = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((1760, 0.5), (2637, 0.25), (3951, 0.12)))
    ping *= np.exp(-t * 4.0)
    return 0.45 * ping + 0.6 * sfx_golpe(0.6)[: len(t)]


def sfx_swell(dur=1.6):
    t = np.arange(int(dur * SR)) / SR
    noise = _lp(np.random.default_rng(9).standard_normal(len(t)), 1500)
    return 0.35 * noise * (t / dur) ** 3


def build_audio(tl, c, path):
    total = tl["total"]
    mix = audio.Mixer(total)
    for sig, at in tl["voices"]:
        if sig is not None:
            mix.add_voice(sig, at, 1.0)
    whoosh = audio.sfx_whoosh(0.6)
    music = music_thriller(total)
    env = np.full(len(music), 0.30)
    for info in tl["clips"]:
        cl = info["clip"]
        s = cl.get("sfx")
        if s == "golpe":
            mix.add_fx(sfx_golpe(), max(0, info["start"] - 0.05), 0.8)
        elif s == "pista":
            mix.add_fx(sfx_pista(), max(0, info["start"] - 0.05), 0.7)
        elif s == "suave":
            mix.add_fx(whoosh, max(0, info["start"] - 0.3), 0.25)
        elif s == "revelacion":
            mix.add_fx(sfx_swell(1.4), max(0, info["start"] - 1.4), 0.7)
            mix.add_fx(sfx_golpe(1.2), info["start"] - 0.02, 0.9)
            a = int((info["start"] - cl.get("silencio_antes", 0.7)) * SR)
            b = int(info["start"] * SR)
            env[a:b] = np.linspace(0.30, 0.04, b - a)  # silencio estratégico
            env[b:b + int(1.2 * SR)] = np.linspace(0.04, 0.30, int(1.2 * SR))[: len(env[b:b + int(1.2 * SR)])]
        if cl.get("rotulo", {}).get("tipo") == "sospechoso":
            mix.add_fx(whoosh, max(0, info["start"] - 0.2), 0.2)
        if cl.get("cuenta_atras"):
            cd = info["cd_start"]
            for k in range(cl["cuenta_atras"]):
                mix.add_fx(audio.sfx_tick(k >= cl["cuenta_atras"] - 2), cd + k, 0.7)
                mix.add_fx(audio.sfx_heartbeat(), cd + k + 0.02, 0.6)
            a, b = int(cd * SR), int((cd + cl["cuenta_atras"]) * SR)
            env[a:b] = np.linspace(0.35, 0.5, b - a)
    for k, sh in enumerate(tl["shots"][1:], 1):  # transición suave en cada cambio de plano
        mix.add_fx(whoosh, max(0, sh["start"] - 0.25), 0.07)
    audio.write_wav(path, mix.render(music * env, music_gain=1.0))


# ---------------------------------------------------------------- dibujo

_S = {}


def _load(name):
    if name not in _S["img"]:
        _S["img"][name] = Image.open(os.path.join(BASE, _S["c"]["imagenes"], name + ".jpg")).convert("RGB")
    return _S["img"][name]


def _gray(name):
    key = name + "#g"
    if key not in _S["img"]:
        im = _load(name)
        g = ImageEnhance.Color(im).enhance(0.25)
        _S["img"][key] = ImageEnhance.Brightness(g).enhance(0.8)
    return _S["img"][key]


def _triptico():
    """Las tres caras en columnas (texto arriba, cuenta atrás y subtítulos abajo)."""
    if "trip" in _S:
        return _S["trip"]
    im = Image.new("RGB", (W, H), (6, 4, 12))
    d = ImageDraw.Draw(im)
    items = [("clara", "CLARA", "La esposa"), ("roberto", "ROBERTO", "El abogado"), ("sofia", "SOFÍA", "La cocinera")]
    cw, y0, y1, gap = 352, 560, 1330, 12
    chh = y1 - y0
    for k, (n, nom, rol) in enumerate(items):
        src = _load(n)
        cx, cy = _S["c"]["focos"][n]
        sh = 1150
        sw = int(sh * cw / chh)
        sx = max(0, min(src.width - sw, cx - sw // 2))
        sy = max(0, min(src.height - sh, cy - sh // 2 + 120))
        col = src.crop((sx, sy, sx + sw, sy + sh)).resize((cw, chh), Image.LANCZOS)
        x = 6 + k * (cw + gap)
        im.paste(col, (x, y0))
        grad = Image.new("L", (cw, chh), 0)
        gd = ImageDraw.Draw(grad)
        for yy in range(chh):
            gd.line([(0, yy), (cw, yy)], fill=int(230 * max(0, (yy - chh * 0.6) / (chh * 0.4))))
        im.paste((0, 0, 0), (x, y0), grad)
        d.text((x + cw / 2, y1 - 120), nom, font=F("titulo", 84), fill=WHITE, anchor="ma")
        d.text((x + cw / 2, y1 - 40), rol, font=F("semi", 28), fill=(210, 210, 220), anchor="ma")
        d.rectangle((x + cw / 2 - 40, y1 - 132, x + cw / 2 + 40, y1 - 127), fill=YEL)
    _S["trip"] = im
    return im


def _shot_frame(sh, t):
    p = (t - sh["start"]) / max(0.01, sh["end"] + XF - sh["start"])
    p = max(0.0, min(1.0, p))
    e = 0.5 - 0.5 * math.cos(math.pi * p)  # suave
    x0, y0, z0 = sh["de"]
    x1, y1, z1 = sh["a"]
    z = z0 + (z1 - z0) * e
    cl = _S["tl"]["clips"][sh["clip"]]["clip"]
    if cl.get("sfx") in ("pista", "revelacion", "golpe"):  # golpe de zoom al aparecer
        z *= 1 + 0.04 * max(0, 1 - (t - sh["start"]) / 0.35)
    if sh["img"] == "triptico":
        base = _triptico()
        if z <= 1.001:
            return base.copy()
        w, h = int(W / z), int(H / z)
        return base.crop(((W - w) // 2, (H - h) // 2, (W + w) // 2, (H + h) // 2)).resize((W, H), Image.BICUBIC)
    src = _gray(sh["img"]) if sh.get("gris") else _load(sh["img"])
    cx, cy = x0 + (x1 - x0) * e, y0 + (y1 - y0) * e
    ch = src.height / z
    cw = ch * W / H
    cx = max(cw / 2, min(src.width - cw / 2, cx))
    cy = max(ch / 2, min(src.height - ch / 2, cy))
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return src.resize((W, H), Image.BICUBIC, box=box)


def _init(state):
    _S.clear()
    _S.update(state)
    _S["img"] = {}
    _S["cache"] = {}
    # viñeta
    yy, xx = np.mgrid[0:H:4, 0:W:4]
    rr = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.45) / (H / 2)) ** 2)
    a = (np.clip((rr - 0.55) / 0.75, 0, 1) ** 1.6 * 210).astype(np.uint8)
    v = Image.new("RGBA", (W // 4, H // 4), (4, 2, 10, 0))
    v.putalpha(Image.fromarray(a, "L"))
    _S["vig"] = v.resize((W, H), Image.BILINEAR)
    # grano
    rng = np.random.default_rng(1)
    _S["grain"] = []
    for _ in range(6):
        g = rng.integers(0, 255, (H // 3, W // 3), dtype=np.uint8)
        gi = Image.fromarray(g, "L").resize((W, H), Image.NEAREST)
        layer = Image.new("RGBA", (W, H), (128, 128, 128, 0))
        layer.putalpha(gi.point(lambda x: int(abs(x - 128) / 128 * 22)))
        _S["grain"].append(layer)
    # niebla
    fog = Image.new("RGBA", (W * 2, 700), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    rf = random.Random(4)
    for _ in range(46):
        x, y = rf.uniform(0, W * 2), rf.uniform(200, 700)
        w, h = rf.uniform(200, 460), rf.uniform(60, 150)
        fd.ellipse((x - w, y - h, x + w, y + h), fill=(200, 205, 235, rf.randint(14, 30)))
    _S["fog"] = fog.filter(ImageFilter.GaussianBlur(34))
    lp = os.path.join(BASE, "assets", "logo.png")
    _S["logo"] = Image.open(lp).convert("RGBA").resize((86, 86), Image.LANCZOS)


NIEBLA = {"mansion", "pasillo", "biblioteca", "escena_cuerpo", "roberto_jardin"}


def _alpha_img(im, a):
    if a >= 0.999:
        return im
    im = im.copy()
    im.putalpha(im.getchannel("A").point(lambda x: int(x * a)))
    return im


def _fade(t, a, b, fi=0.3, fo=0.3):
    if t < a or t > b:
        return 0.0
    return max(0.0, min(1.0, (t - a) / fi, (b - t) / fo))


def _text_shadow(lay, xy, txt, font, fill, anchor="la", blur=8, sh=(0, 0, 0, 200)):
    s = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).text((xy[0] + 3, xy[1] + 4), txt, font=font, fill=sh, anchor=anchor)
    lay.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(lay).text(xy, txt, font=font, fill=fill, anchor=anchor)


def _rotulo(img, info, t):
    cl = info["clip"]
    r = cl.get("rotulo")
    if not r:
        return
    a = _fade(t, info["start"] + 0.15, info["end"] - 0.05, 0.35, 0.3)
    if a <= 0:
        return
    key = ("rot", id(cl))
    if key not in _S["cache"]:
        lay = Image.new("RGBA", (W, 700), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        tp = r["tipo"]
        if tp == "sospechoso":
            d.rectangle((70, 40, 76, 300), fill=YEL)
            _text_shadow(lay, (100, 40), r["num"], F("semi", 32), TURQ)
            _text_shadow(lay, (96, 82), r["nombre"], F("titulo", 150), WHITE)
            _text_shadow(lay, (100, 240), r["rol"], F("semi", 42), (225, 225, 235))
        elif tp == "pista":
            d.rectangle((70, 40, 76, 210), fill=TURQ)
            _text_shadow(lay, (100, 36), r["num"], F("titulo", 96), YEL)
            _text_shadow(lay, (100, 140), r["texto"], F("semi", 44), WHITE)
        elif tp == "caso":
            _text_shadow(lay, (W / 2, 60), r["texto"], F("titulo", 130), WHITE, "ma")
            d.rectangle((W / 2 - 140, 205, W / 2 + 140, 210), fill=YEL)
            _text_shadow(lay, (W / 2, 230), r["sub"], F("semi", 42), TURQ, "ma")
        elif tp == "titular":
            _text_shadow(lay, (W / 2, 60), r["texto"], F("titulo", 180), WHITE, "ma", blur=14,
                         sh=(0, 140, 130, 230))
        elif tp == "veredicto":
            _text_shadow(lay, (W / 2, 50), "CLARA", F("titulo", 200), YEL, "ma", blur=14)
            _text_shadow(lay, (W / 2, 250), "SE CONTRADICE", F("titulo", 110), WHITE, "ma")
        elif tp == "cta":
            for k, line in enumerate(["¿LO HABÍAS", "DETECTADO?"]):
                _text_shadow(lay, (W / 2, 30 + k * 150), line, F("titulo", 160), WHITE if k == 0 else YEL, "ma")
            f = F("bold", 40)
            tw = d.textlength(r["sub"], font=f)
            d.rounded_rectangle((W / 2 - tw / 2 - 40, 380, W / 2 + tw / 2 + 40, 470), 45, fill=TURQ)
            d.text((W / 2, 425), r["sub"], font=f, fill=(10, 8, 20), anchor="mm")
        _S["cache"][key] = lay
    lay = _S["cache"][key]
    y = {"cta": 520, "titular": 200, "veredicto": 230}.get(r["tipo"], 230)
    dx = int((1 - ease_out(min(1, (t - info["start"] - 0.15) / 0.45))) * -40) if r["tipo"] in ("sospechoso", "pista") else 0
    img.alpha_composite(_alpha_img(lay, a), (dx, y))


def _tarjetas(img, info, t):
    cl = info["clip"]
    tj = cl.get("tarjetas")
    if not tj:
        return
    span = info["voice_end"] - info["start"]
    ys = [960, 1140]
    k_card = 0
    for k, c_ in enumerate(tj):
        t0 = info["start"] + span * c_["en"]
        a = _fade(t, t0, info["end"] - 0.05, 0.3, 0.3)
        if a <= 0:
            if not c_.get("sello"):
                k_card += 1
            continue
        key = ("tj", id(cl), k)
        if c_.get("sello"):
            if key not in _S["cache"]:
                st = Image.new("RGBA", (760, 200), (0, 0, 0, 0))
                sd = ImageDraw.Draw(st)
                sd.rounded_rectangle((8, 8, 752, 192), 18, outline=YEL, width=8)
                sd.text((380, 104), c_["texto"], font=F("titulo", 120), fill=YEL, anchor="mm")
                _S["cache"][key] = st.rotate(-6, Image.BICUBIC, expand=True)
            st = _S["cache"][key]
            p = min(1, (t - t0) / 0.25)
            s = 1.6 - 0.6 * ease_out(p)
            st2 = st.resize((int(st.width * s), int(st.height * s)), Image.BICUBIC)
            img.alpha_composite(_alpha_img(st2, a * min(1, p * 2)), (int(W / 2 - st2.width / 2), int(470 - st2.height / 2)))
            continue
        if key not in _S["cache"]:
            single = len([x for x in tj if not x.get("sello")]) == 1
            hh = 230 if single else 160
            card = Image.new("RGBA", (920, hh), (0, 0, 0, 0))
            cd = ImageDraw.Draw(card)
            cd.rounded_rectangle((0, 0, 919, hh - 1), 22, fill=(10, 8, 22, 205))
            cd.rectangle((0, 18, 8, hh - 18), fill=YEL)
            if c_["titulo"]:
                cd.text((40, 26), c_["titulo"], font=F("semi", 28), fill=TURQ)
            f = F("bold", 46 if not single else 42)
            words, lines, cur = c_["texto"].split(), [], ""
            for w in words:
                test = (cur + " " + w).strip()
                if cd.textlength(test, font=f) > 840 and cur:
                    lines.append(cur)
                    cur = w
                else:
                    cur = test
            lines.append(cur)
            for j, l in enumerate(lines):
                cd.text((40, 66 + j * 54), l, font=f, fill=WHITE)
            _S["cache"][key] = card
        card = _S["cache"][key]
        dy = int((1 - ease_out(min(1, (t - t0) / 0.4))) * 30)
        y = ys[min(k_card, 1)] if len(tj) > 1 else 990
        img.alpha_composite(_alpha_img(card, a), (80, y + dy))
        k_card += 1


def _cuenta_atras(img, info, t):
    cl = info["clip"]
    n = cl.get("cuenta_atras")
    if not n:
        return
    cd = info["cd_start"]
    if not (cd - 0.3 <= t < cd + n + 0.1):
        return
    dark = Image.new("RGBA", (W, H), (0, 0, 0, int(60 * min(1, (t - cd + 0.3) / 0.3))))
    img.alpha_composite(dark)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    _text_shadow(lay, (W / 2, 250), "¿QUIÉN SE", F("titulo", 130), WHITE, "ma")
    _text_shadow(lay, (W / 2, 380), "CONTRADICE?", F("titulo", 130), YEL, "ma")
    el = max(0.0, t - cd)
    rem = max(0.0, n - el)
    num = max(1, math.ceil(rem)) if el < n else 0
    frac = rem / n
    beat = 1 + 0.06 * math.exp(-((el % 1) / 0.12))
    R = int(130 * beat)
    cx, cy = W / 2, 1540
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(8, 6, 16, 170))
    d.arc((cx - R, cy - R, cx + R, cy + R), 0, 360, fill=(255, 255, 255, 50), width=8)
    col = TURQ if frac > 0.4 else YEL
    d.arc((cx - R, cy - R, cx + R, cy + R), -90, -90 + 360 * frac, fill=col, width=10)
    if num:
        d.text((cx, cy + 8), str(num), font=F("titulo", int(190 * beat)), fill=WHITE, anchor="mm")
    img.alpha_composite(lay)


def _subtitulos(img, t):
    for k, ch in enumerate(_S["tl"]["subs"]):
        if not (ch["start"] <= t < ch["end"]):
            continue
        words = [w.upper() for w, _, _ in ch["words"]]
        act = [i for i, (_, a, b) in enumerate(ch["words"]) if a <= t]
        last = act[-1] if act else -1
        key = ("sub", k, last)
        if key not in _S["cache"]:
            f = F("bold", 64)
            tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
            size = 64
            while True:
                f = F("bold", size)
                ws = [tmp.textlength(w, font=f) for w in words]
                tot = sum(ws) + 20 * (len(ws) - 1)
                if tot <= 960 or size <= 44:
                    break
                size -= 4
            lay = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
            sh = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
            sd, d = ImageDraw.Draw(sh), ImageDraw.Draw(lay)
            x = W / 2 - tot / 2
            for i, (w, wd) in enumerate(zip(words, ws)):
                said = i <= last
                c = ch["cols"][i]
                col = YEL if c == "y" else TURQ if c == "t" else WHITE
                alpha = 255 if said else 95
                sd.text((x + 3, 104), w, font=f, fill=(0, 0, 0, 230), anchor="lm")
                d.text((x, 100), w, font=f, fill=col + (alpha,), anchor="lm")
                if said and c:
                    d.rectangle((x, 140, x + wd, 145), fill=col + (200,))
                x += wd + 20
            out = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
            out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)))
            out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)))
            out.alpha_composite(lay)
            _S["cache"][key] = out
        p = min(1, (t - ch["start"]) / 0.18)
        lay = _alpha_img(_S["cache"][key], p)
        img.alpha_composite(lay, (0, int(1370 + 12 * (1 - ease_out(p)))))
        break


def _marca(img, t):
    a = 0.85
    img.alpha_composite(_alpha_img(_S["logo"], a), (W - 86 - 60, 190))
    d = ImageDraw.Draw(img)
    d.text((W / 2, 1712), USUARIO, font=F("semi", 34), fill=(255, 255, 255, 170), anchor="mm")


def render_frame(i):
    t = i / FPS
    shots = _S["tl"]["shots"]
    k = next((j for j, sh in enumerate(shots) if sh["start"] <= t < sh["end"]), len(shots) - 1)
    frame = _shot_frame(shots[k], t)
    if k > 0 and t < shots[k]["start"] + XF:  # fundido desde el plano anterior
        prev = _shot_frame(shots[k - 1], t)
        frame = Image.blend(prev, frame, ease_out((t - shots[k]["start"]) / XF))
    img = frame.convert("RGBA")
    if shots[k]["img"] in NIEBLA:
        fog = _S["fog"]
        off = int((t * 40) % W)
        img.alpha_composite(fog.crop((off, 0, off + W, fog.height)), (0, H - fog.height - 180))
    img.alpha_composite(_S["vig"])
    info = next((c for c in _S["tl"]["clips"] if c["start"] - c["clip"].get("silencio_antes", 0) <= t < c["end"]),
                None)
    if info:
        cl = info["clip"]
        if cl.get("sfx") in ("pista", "revelacion"):  # destello sutil
            fl = max(0, 1 - (t - info["start"]) / 0.25)
            if fl > 0:
                img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(70 * fl))))
        _rotulo(img, info, t)
        _tarjetas(img, info, t)
        _cuenta_atras(img, info, t)
    _subtitulos(img, t)
    _marca(img, t)
    img.alpha_composite(_S["grain"][i % len(_S["grain"])])
    if t < 0.25:  # entrada desde negro
        img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - t / 0.25)))))
    return img.convert("RGB").tobytes()


# ---------------------------------------------------------------- exportación

def render(c, out_path, preview=None, workers=None):
    tl = build(c, sin_voz=False)
    state = {"c": c, "tl": tl}
    if preview is not None:
        _init(state)
        outs = []
        for s in preview:
            p = f"{out_path}_{s:05.1f}.png"
            Image.frombytes("RGB", (W, H), render_frame(int(s * FPS))).save(p)
            outs.append(p)
        return tl, outs
    wav = out_path + ".audio.wav"
    build_audio(tl, c, wav)
    frames = int(tl["total"] * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "23",
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1", "-c:a", "aac", "-b:a", "192k",
           "-ar", "44100", "-shortest", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers or os.cpu_count(), initializer=_init, initargs=(state,)) as pool:
        for k, fr in enumerate(pool.imap(render_frame, range(frames), chunksize=4)):
            proc.stdin.write(fr)
            if k % (FPS * 10) == 0:
                print(f"  fotograma {k}/{frames}", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg falló")
    os.remove(wav)
    return tl, None

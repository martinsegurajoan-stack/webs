"""Formato "FIESTA" (pruebas para beber con amigos; cada prueba con una mecánica distinta).

Gancho → reglas → pruebas (ruleta, dedo acusador, yo nunca, reflejos, bomba, esto o aquello) →
PRUEBA IMPOSIBLE (trabalenguas maldito) → brindis final con fuegos artificiales → cierre.
Estética de discoteca: focos de bola de disco, láseres, ecualizador al ritmo de la música, confeti.
"""

import math
import os
import random
import subprocess
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from . import audio, themes
from .cartas import _fit_t, sfx_clink, sfx_flip
from .niveles import check, paste_c, pill, pop, rr, text, username
from .personalidad import sfx_boing, sfx_impact
from .render import FPS, W, H, ease_in, ease_out, ease_out_back, font, tfont

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
BPM = 128
BEAT = 60.0 / BPM
WHITE = (255, 255, 255)
YEL = (255, 212, 0)
DARK = (26, 12, 44)
RED = (239, 45, 70)
GOLD = (255, 196, 40)
IDLE = 22.0          # giro lento de la ruleta antes de lanzarla (grados/s)
SPIN = 4.2           # duración del giro de la ruleta

NEON = {
    "ruleta": (255, 60, 170), "senalar": (0, 214, 255), "yo_nunca": (255, 138, 30),
    "reflejos": (60, 232, 120), "bomba": (255, 70, 60), "esto_aquello": (130, 110, 255),
    "final": (255, 40, 60),
}
WHEEL_COLS = [(255, 60, 170), (255, 196, 0), (0, 200, 255), (150, 80, 255), (255, 120, 30),
              (40, 210, 110), (60, 110, 255), (239, 45, 70)]
CONF_COLS = [YEL, (0, 230, 210), (255, 70, 170), WHITE, (160, 90, 255), (60, 220, 120)]


# ------------------------------------------------------------------ audio

def _t(d):
    return np.arange(int(d * audio.SR)) / audio.SR


def _norm(x, peak):
    return x / (np.max(np.abs(x)) or 1) * peak


def sfx_airhorn():
    """Bocina de discoteca: ¡pa-pa-paaa!"""
    out = []
    for dur in (0.15, 0.15, 0.6):
        t = _t(dur)
        f = 466 * (1 + 0.012 * np.sin(2 * np.pi * 7 * t))
        s = sum(a * np.sign(np.sin(2 * np.pi * np.cumsum(f * m) / audio.SR))
                for m, a in ((1, 1), (1.007, 0.8), (1.498, 0.45), (0.5, 0.6)))
        env = np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.04)
        out += [s * env, np.zeros(int(0.05 * audio.SR))]
    return _norm(audio._lp_fft(np.concatenate(out), 3200), 0.45)


def sfx_explosion():
    t = _t(2.2)
    rng = np.random.default_rng(9)
    low = audio._lp_fft(rng.standard_normal(len(t)), 500) * np.exp(-t * 2.2)
    boom = np.sin(2 * np.pi * np.cumsum(28 + 80 * np.exp(-t * 7)) / audio.SR) * np.exp(-t * 2.6)
    crack = rng.standard_normal(len(t)) * np.exp(-t * 25)
    return _norm(_norm(low, 1) + 0.9 * boom + 0.35 * crack, 0.95)


def sfx_firework(seed):
    rng = np.random.default_rng(seed)
    t = _t(1.8)
    out = np.zeros(len(t))
    wl = int(0.55 * audio.SR)
    tw = t[:wl]
    out[:wl] += 0.12 * np.sin(2 * np.pi * np.cumsum(1300 + 1500 * tw / 0.55) / audio.SR) * np.minimum(1, tw / 0.1)
    tc = t[wl:] - t[wl]
    out[wl:] += 0.7 * audio._lp_fft(rng.standard_normal(len(tc)), 2500) * np.exp(-tc * 9)
    for _ in range(26):
        s = wl + int(rng.uniform(0.1, 1.1) * audio.SR)
        n = int(0.012 * audio.SR)
        if s + n < len(out):
            out[s:s + n] += rng.standard_normal(n) * np.exp(-np.arange(n) / 120) * rng.uniform(0.1, 0.3)
    return out


def sfx_hiss(dur):
    rng = np.random.default_rng(3)
    x = rng.standard_normal(int(dur * audio.SR))
    x = x - audio._lp_fft(x, 3500)
    t = _t(dur)
    return 0.12 * x * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * t)) * np.minimum(1, t / 0.1)


def sfx_thunder():
    t = _t(2.5)
    rng = np.random.default_rng(17)
    x = audio._lp_fft(rng.standard_normal(len(t)), 260) * (np.exp(-t * 1.6) + 0.6 * np.exp(-np.abs(t - 0.35) * 8))
    return _norm(x, 0.8)


def build_audio(events, total, path):
    mix = audio.Mixer(total)
    fx = {"whoosh": audio.sfx_whoosh(), "pop": audio.sfx_pop(), "tick": audio.sfx_tick(),
          "tick_high": audio.sfx_tick(True), "tock": audio.sfx_tock(), "heart": audio.sfx_heartbeat(),
          "riser": audio.sfx_riser(7), "flip": sfx_flip(), "impact": sfx_impact(), "boing": sfx_boing(),
          "clink": sfx_clink(), "applause": audio.sfx_applause(), "correct": audio.sfx_correct(),
          "airhorn": sfx_airhorn(), "explosion": sfx_explosion(), "thunder": sfx_thunder(),
          "fw0": sfx_firework(1), "fw1": sfx_firework(2), "fw2": sfx_firework(3)}
    gains = {"whoosh": 0.5, "pop": 0.6, "tick": 0.9, "tick_high": 1.3, "tock": 0.9, "heart": 0.85,
             "riser": 0.45, "flip": 0.8, "impact": 0.7, "boing": 0.8, "clink": 1.0, "applause": 0.8,
             "correct": 0.6, "airhorn": 0.8, "explosion": 1.0, "thunder": 0.9, "fw0": 0.8, "fw1": 0.8,
             "fw2": 0.8}
    boosts = [(a, b) for kind, a, b in events if kind == "music_boost"]
    ducks = [(a, b) for kind, a, b in events if kind == "music_duck"]
    for kind, what, at in events:
        if kind in ("music_boost", "music_duck"):
            continue
        if kind == "fx":
            mix.add_fx(fx[what], at, gains[what])
        elif kind == "hiss":
            mix.add_fx(sfx_hiss(what[1]), what[0], 1.0)
        elif what is not None:
            mix.add_voice(what, at, 1.0)
    music = audio.music_pop(total, bpm=BPM, seed=11)
    g = np.ones(len(music))
    for a, b in ducks:
        g[int(a * audio.SR):int(b * audio.SR)] = 0.25
    ramp = int(0.3 * audio.SR)
    g = np.convolve(g, np.ones(ramp) / ramp, mode="same")
    audio.write_wav(path, mix.render(music * g, music_gain=0.38, boosts=boosts))


# ------------------------------------------------------------------ línea de tiempo

def vsay(voice, txt, shout=False):
    """Las frases que ya traen su etiqueta ([whispers], [excited]…) van sin el estilo general."""
    if not shout and txt.startswith("["):
        st = voice.style
        voice.style = ""
        try:
            return voice.say(txt)
        finally:
            voice.style = st
    return voice.say(txt, shout)


def wheel_phi(T, lt):
    if lt < T["spin"]:
        return IDLE * lt
    p = min(1.0, (lt - T["spin"]) / SPIN)
    return T["phi0"] + (T["phi1"] - T["phi0"]) * (1 - (1 - p) ** 3.2)


def _count3(ev, at):
    for s in range(3):
        ev += [("fx", "heart", at + s), ("fx", "tick_high", at + s), ("fx", "tock", at + s + 0.5)]


def t_ruleta(p, voice, ev, st, T):
    n = len(p["sectores"])
    seg = 360 / n
    T["spin"] = T["m0"] + 0.25
    T["phi0"] = IDLE * T["spin"]
    target = (-(p["gana"] * seg) + seg * 0.28) % 360
    k = math.ceil((T["phi0"] + 1500 - target) / 360)
    T["phi1"] = target + 360 * k
    T["seg"] = seg
    ev += [("fx", "whoosh", st + T["spin"]), ("music_boost", st + T["spin"], st + T["spin"] + SPIN)]
    last, last_t = None, -1
    for i in range(int(SPIN * 250)):
        lt = T["spin"] + i / 250
        c = math.floor((wheel_phi(T, lt) + seg / 2) / seg)
        if last is not None and c != last and lt - last_t > 0.035:
            ev.append(("fx", "tick", st + lt))
            last_t = lt
        last = c
    T["res"] = T["spin"] + SPIN
    ev += [("fx", "impact", st + T["res"]), ("fx", "correct", st + T["res"] + 0.05)]
    sig, d = vsay(voice, p["resultado_voz"])
    ev += [("voice", sig, st + T["res"] + 0.2), ("fx", "clink", st + T["res"] + 0.4 + d)]
    T["shakes"] = [(T["res"], 0.7)]
    return T["res"] + 0.2 + d + 0.85


def t_senalar(p, voice, ev, st, T):
    sig, d = vsay(voice, p["voz"])
    ev.append(("voice", sig, st + T["m0"]))
    T["cd"] = T["m0"] + d + 0.1
    _count3(ev, st + T["cd"])
    T["go"] = T["cd"] + 3
    ev += [("fx", "airhorn", st + T["go"]), ("fx", "impact", st + T["go"])]
    sig, d = vsay(voice, p["resultado_voz"])
    T["res"] = T["go"] + 1.1
    ev.append(("voice", sig, st + T["res"]))
    T["shakes"] = [(T["go"], 1.0)]
    return T["res"] + d + 0.75


def t_yo_nunca(p, voice, ev, st, T):
    tt = T["m0"]
    T["frases"] = []
    for i, (_, vz) in enumerate(p["frases"]):
        ev += [("fx", "whoosh", st + tt), ("fx", "flip", st + tt + 0.1)]
        sig, d = vsay(voice, vz)
        ev.append(("voice", sig, st + tt + 0.25))
        stamp = tt + 0.25 + d + 0.05
        ev += [("fx", "impact", st + stamp), ("fx", "clink", st + stamp + 0.15)]
        T["frases"].append((tt, stamp))
        tt = stamp + 1.25
    T["shakes"] = [(s, 0.5) for _, s in T["frases"]]
    return tt + 0.2


def t_reflejos(p, voice, ev, st, T):
    gaps = [0.75, 0.6, 0.85, 0.55, 0.9, 0.7, 0.8]
    tt = T["m0"] + 0.5
    T["items"] = []
    for i, name in enumerate(p["secuencia"]):
        T["items"].append((name, tt))
        if name == "cerveza":
            T["ya"] = tt
            break
        ev += [("fx", "pop", st + tt), ("fx", "heart", st + tt)]
        if name in p.get("trampas", []):
            ev.append(("fx", "boing", st + tt + 0.05))
        tt += gaps[i % len(gaps)]
    sig, d = vsay(voice, "¡Ya!", shout=True)
    ev += [("fx", "airhorn", st + T["ya"]), ("fx", "impact", st + T["ya"]), ("voice", sig, st + T["ya"])]
    sig, d = vsay(voice, p["resultado_voz"])
    T["res"] = T["ya"] + 1.3
    ev.append(("voice", sig, st + T["res"]))
    T["shakes"] = [(T["ya"], 1.2)]
    return T["res"] + d + 0.75


def t_bomba(p, voice, ev, st, T):
    sig, d = vsay(voice, p["voz"])
    ev.append(("voice", sig, st + T["m0"]))
    S = p.get("segundos", 8)
    T["fuse"] = T["m0"] + d + 0.25
    T["S"] = S
    ev += [("hiss", (st + T["fuse"], S), None), ("music_boost", st + T["fuse"], st + T["fuse"] + S)]
    x = 0.0
    while x < S - 0.05:
        ev.append(("fx", "tick_high" if x > S * 0.6 else "tick", st + T["fuse"] + x))
        x += 0.5 - 0.37 * (x / S) ** 1.3
    T["boom"] = T["fuse"] + S
    ev.append(("fx", "explosion", st + T["boom"]))
    sig, d = vsay(voice, p["resultado_voz"])
    T["res"] = T["boom"] + 0.75
    ev.append(("voice", sig, st + T["res"]))
    T["shakes"] = [(T["boom"], 1.6)]
    return T["res"] + d + 0.8


def t_esto_aquello(p, voice, ev, st, T):
    sig, d = vsay(voice, p["voz"])
    ev.append(("voice", sig, st + T["m0"]))
    T["cd"] = T["m0"] + d + 0.1
    _count3(ev, st + T["cd"])
    T["go"] = T["cd"] + 3
    ev += [("fx", "airhorn", st + T["go"]), ("fx", "impact", st + T["go"])]
    sig, d = vsay(voice, p["resultado_voz"])
    T["res"] = T["go"] + 1.1
    ev.append(("voice", sig, st + T["res"]))
    T["shakes"] = [(T["go"], 1.0)]
    return T["res"] + d + 0.75


def t_final(p, voice, ev, st, T):
    ev += [("fx", "thunder", st + 0.05), ("music_duck", st, st + T["m0"] + 0.2)]
    sig, d = vsay(voice, p["voz"])
    ev += [("fx", "impact", st + T["m0"]), ("voice", sig, st + T["m0"] + 0.1)]
    T["tw"] = T["m0"] + 0.1 + d + 0.25
    sig, d2 = vsay(voice, p["trabalenguas_voz"])
    ev += [("fx", "whoosh", st + T["tw"]), ("voice", sig, st + T["tw"] + 0.3)]
    T["tw_v"], T["tw_d"] = T["tw"] + 0.3, d2
    S = p.get("segundos", 7)
    T["turno"] = T["tw_v"] + d2 + 0.45
    T["S"] = S
    ev += [("fx", "airhorn", st + T["turno"]), ("fx", "riser", st + T["turno"]),
           ("music_boost", st + T["turno"], st + T["turno"] + S)]
    for s in range(S):
        ts = st + T["turno"] + 0.6 + s
        if s < S - 1:
            ev += [("fx", "heart", ts), ("fx", "tick_high" if s >= S - 3 else "tick", ts), ("fx", "tock", ts + 0.5)]
    T["res"] = T["turno"] + S + 0.2
    sig, d3 = vsay(voice, p["resultado_voz"])
    ev += [("fx", "impact", st + T["res"]), ("voice", sig, st + T["res"] + 0.1)]
    T["crown"] = T["res"] + 0.1 + d3 * 0.42
    ev += [("fx", "correct", st + T["crown"]), ("fx", "pop", st + T["crown"])]
    T["shakes"] = [(0.05, 1.3), (T["m0"], 0.8), (T["res"], 0.6)]
    T["flashes"] = [0.05, 0.9, T["m0"]]
    return T["res"] + 0.1 + d3 + 0.5


TIMELINE = {"ruleta": t_ruleta, "senalar": t_senalar, "yo_nunca": t_yo_nunca, "reflejos": t_reflejos,
            "bomba": t_bomba, "esto_aquello": t_esto_aquello, "final": t_final}


def build_timeline(c, voice):
    scenes, ev = [], []
    sig, d = vsay(voice, c["gancho"]["voz"])
    ev += [("voice", sig, 0.0), ("fx", "impact", 0.0), ("fx", "airhorn", d + 0.05)]
    for i in range(7):
        ev.append(("fx", "pop", 0.2 + 0.09 * i))
    dur = max(3.4, d + 1.0)
    scenes.append({"kind": "hook", "start": 0.0, "dur": dur, "bg": "club", "shakes": [(0.0, 1.0), (d + 0.05, 0.6)]})
    t = dur

    sig, d = vsay(voice, c["instrucciones"]["voz"])
    ev += [("fx", "whoosh", t), ("voice", sig, t + 0.15)]
    for i in range(3):
        ev.append(("fx", "pop", t + 0.35 + 0.3 * i))
    dur = max(3.4, 0.15 + d + 0.25)
    scenes.append({"kind": "instr", "start": t, "dur": dur, "bg": "club"})
    t += dur

    n = len(c["pruebas"])
    for k, p in enumerate(c["pruebas"]):
        st = t
        ev += [("fx", "whoosh", st), ("fx", "impact", st + 0.05)]
        sig, d = vsay(voice, p["anuncio"])
        ev.append(("voice", sig, st + 0.15))
        T = {"m0": max(1.7, 0.15 + d + 0.15)}
        loc = TIMELINE[p["tipo"]](p, voice, ev, st, T)
        sh = [(0.05, 0.8)] + T.get("shakes", [])
        scenes.append({"kind": "prueba", "start": st, "dur": loc, "k": k, "p": p, "T": T, "n": n,
                       "bg": p["tipo"], "shakes": sh})
        t += loc
        if p["tipo"] == "final":
            sig, d = vsay(voice, p["brindis_voz"])
            ev += [("fx", "airhorn", t), ("voice", sig, t + 0.25), ("fx", "clink", t + 0.35 + d),
                   ("fx", "applause", t + 0.3 + d)]
            fws = [(0.3, 250, 420), (0.75, 830, 360), (1.3, 540, 300), (1.9, 200, 640), (2.4, 880, 600),
                   (2.9, 540, 470), (3.3, 330, 330)]
            for j, (ft, _, _) in enumerate(fws):
                ev.append(("fx", f"fw{j % 3}", t + ft - 0.55))
            dur = max(4.6, 0.25 + d + 2.6)
            scenes.append({"kind": "brindis", "start": t, "dur": dur, "bg": "brindis", "clink": 0.35 + d,
                           "fws": fws, "shakes": [(0.0, 0.8), (0.35 + d, 0.8)]})
            t += dur

    sig, d = vsay(voice, c["cierre_voz"])
    shout_at = 0.3 + d + 0.1
    sig2, d2 = vsay(voice, "¡Sígueme para más!", shout=True)
    dur = max(3.6, shout_at + d2 + 1.0)
    ev += [("fx", "whoosh", t), ("voice", sig, t + 0.3), ("voice", sig2, t + shout_at),
           ("fx", "applause", t + shout_at)]
    scenes.append({"kind": "outro", "start": t, "dur": dur, "shout_at": shout_at, "bg": "club"})
    return scenes, ev, t + dur


# ------------------------------------------------------------------ recursos

_S = {}


def mix(c1, c2, k):
    return tuple(int(a + (b - a) * k) for a, b in zip(c1, c2))


def spr(name, size):
    key = (name, size)
    if key not in _S["spr"]:
        if name == "_ruleta":
            im = _S["wheel"]
        else:
            im = Image.open(os.path.join(ASSETS, "fiesta", name + ".png")).convert("RGBA")
        _S["spr"][key] = im.resize((size, size), Image.LANCZOS)
    return _S["spr"][key]


def _gradient(top, bot, glow_col=None):
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(-1, 1, W)[None, :]
    k = np.clip(y * 0.95 + x * 0.05, 0, 1)
    arr = np.zeros((H, W, 3))
    for ch in range(3):
        arr[..., ch] = top[ch] + (bot[ch] - top[ch]) * k
    if glow_col is not None:
        g = np.exp(-((x * 0.85) ** 2 + ((y - 0.5) / 0.38) ** 2))
        for ch in range(3):
            arr[..., ch] += g * glow_col[ch] * 0.28
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def make_wheel(sectores, R=360):
    S = 2 * R
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    n = len(sectores)
    seg = 360 / n
    for i, s in enumerate(sectores):
        th = i * seg
        col = WHEEL_COLS[i % len(WHEEL_COLS)]
        d.pieslice((0, 0, S - 1, S - 1), th - 90 - seg / 2, th - 90 + seg / 2, fill=col)
        d.pieslice((R * 0.08, R * 0.08, S - R * 0.08, S - R * 0.08), th - 90 - seg / 2, th - 90 + seg / 2,
                   fill=mix(col, WHITE, 0.12))
    for i in range(n):
        a = math.radians(i * seg - seg / 2 - 90)
        d.line([(R, R), (R + R * math.cos(a), R + R * math.sin(a))], fill=WHITE, width=6)
    for i, s in enumerate(sectores):
        th = i * seg
        f = tfont(38)
        while d.textlength(s, font=f) > R * 0.62 and f.size > 22:
            f = tfont(f.size - 2)
        tw = int(d.textlength(s, font=f)) + 20
        ti = Image.new("RGBA", (tw, 60), (0, 0, 0, 0))
        ImageDraw.Draw(ti).text((tw / 2, 30), s, font=f, fill=WHITE, anchor="mm", stroke_width=4,
                                stroke_fill=(30, 10, 40))
        ti = ti.rotate(90 - th, resample=Image.BICUBIC, expand=True)
        r = R * 0.6
        cx, cy = R + r * math.sin(math.radians(th)), R - r * math.cos(math.radians(th))
        img.alpha_composite(ti, (int(cx - ti.width / 2), int(cy - ti.height / 2)))
    d.ellipse((0, 0, S - 1, S - 1), outline=WHITE, width=10)
    return img


def _card_yo(txt, i, n, col):
    cw, ch = 900, 560
    g = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(g, "RGBA")
    d.rounded_rectangle((0, 0, cw - 1, ch - 1), 44, fill=(255, 252, 246))
    d.rounded_rectangle((0, 0, cw - 1, 150), 44, fill=col)
    d.rectangle((0, 100, cw - 1, 150), fill=col)
    d.text((cw / 2, 80), "YO NUNCA…", font=tfont(96), fill=WHITE, anchor="mm", stroke_width=6,
           stroke_fill=mix(col, (0, 0, 0), 0.45))
    f, lines, lh = _fit_t(d, txt, cw - 110, 300, 82, 40)
    yy = 360 - lh * len(lines) / 2 + lh / 2
    for ln in lines:
        d.text((cw / 2, yy), ln, font=f, fill=DARK, anchor="mm")
        yy += lh
    d.text((cw - 60, ch - 44), f"{i + 1}/{n}", font=tfont(40), fill=mix(col, DARK, 0.3), anchor="mm")
    d.rounded_rectangle((0, 0, cw - 1, ch - 1), 44, outline=WHITE, width=8)
    return g


def _init(state):
    _S.clear()
    _S.update(state)
    _S["spr"] = {}
    c = state["c"]
    h = state["tono"]
    club_top, club_bot = themes._hsv(h, 0.85, 0.34), themes._hsv(h + 25, 0.9, 0.07)
    _S["bg"] = {"club": _gradient(club_top, club_bot, themes._hsv(h, 0.7, 1.0)),
                "brindis": _gradient((120, 40, 170), (40, 8, 60), GOLD)}
    for tipo, col in NEON.items():
        if tipo == "final":
            _S["bg"][tipo] = _gradient((70, 6, 16), (8, 2, 6), (200, 20, 30))
        else:
            _S["bg"][tipo] = _gradient(mix(col, (14, 6, 30), 0.62), mix(club_bot, (0, 0, 0), 0.2), col)
    rnd = random.Random(8)
    _S["confeti"] = [(rnd.random() * W, rnd.random() * H, rnd.choice(CONF_COLS), rnd.uniform(8, 16),
                      rnd.uniform(0.4, 1.0), rnd.random() * 6.28) for _ in range(40)]
    rb = random.Random(3)
    _S["burst"] = [(rb.uniform(-1, 1), rb.uniform(-1.5, -0.4), rb.choice(CONF_COLS), rb.uniform(10, 22),
                    rb.uniform(0, 6.28)) for _ in range(54)]
    rd = random.Random(5)
    _S["dots"] = [(rd.uniform(0, 6.283), rd.uniform(150, 1900), rd.uniform(5, 13), rd.random() < 0.3)
                  for _ in range(70)]
    _S["eq"] = [(random.Random(i).uniform(0, 6.28), random.Random(i * 7).uniform(1.5, 3.5)) for i in range(20)]
    _S["logo"] = Image.open(os.path.join(ASSETS, "logo.png")).convert("RGBA")
    rul = next((p for p in c["pruebas"] if p["tipo"] == "ruleta"), None)
    _S["wheel"] = make_wheel(rul["sectores"] if rul else ["?"] * 8)
    _S["yo"] = {}
    for k, p in enumerate(c["pruebas"]):
        if p["tipo"] == "yo_nunca":
            for i, (txt, _) in enumerate(p["frases"]):
                _S["yo"][(k, i)] = _card_yo(txt, i, len(p["frases"]), NEON["yo_nunca"])


# ------------------------------------------------------------------ fondo

def beat_k(t):
    return math.exp(-((t % BEAT) / BEAT) * 5)


def _bg_frame(key, t):
    img = _S["bg"][key].copy()
    d = ImageDraw.Draw(img, "RGBA")
    acc = NEON.get(key, (255, 80, 200))
    if key == "brindis":
        acc = GOLD
    bk = beat_k(t)
    # láseres que barren desde las esquinas de abajo
    for j, (x0, ph, col) in enumerate([(0, 0.0, acc), (W, 1.7, (0, 230, 255)), (0, 3.1, YEL), (W, 4.4, acc)]):
        ang = -math.pi / 2 + math.sin(t * 0.8 + ph) * 0.7 + (0.35 if x0 == 0 else -0.35)
        x1, y1 = x0 + 2600 * math.cos(ang), H + 2600 * math.sin(ang)
        d.line([(x0, H), (x1, y1)], fill=col + (int(26 + 30 * bk),), width=16)
        d.line([(x0, H), (x1, y1)], fill=col + (int(90 + 60 * bk),), width=3)
    # reflejos de la bola de disco girando
    for (a0, r, s, colored) in _S["dots"]:
        a = a0 + t * 0.35
        x = 540 + r * math.cos(a)
        y = 180 + r * math.sin(a) * 0.75
        if -20 < x < W + 20 and -20 < y < H + 20:
            col = acc if colored else WHITE
            d.ellipse((x - s, y - s, x + s, y + s), fill=col + (int(70 + 70 * bk),))
    # confeti suave
    for (x0, y0, col, s, sp, ph) in _S["confeti"][:24]:
        y = (y0 + t * 100 * sp) % (H + 60) - 30
        x = x0 + math.sin(t * 1.5 * sp + ph) * 30
        ang = ph + t * 3 * sp
        pts = [(x + s * math.cos(ang + q * math.pi / 2) * (1 if q % 2 else 0.45),
                y + s * math.sin(ang + q * math.pi / 2) * (1 if q % 2 else 0.45)) for q in range(4)]
        d.polygon(pts, fill=col + (110,))
    # ecualizador al ritmo de la música (abajo, bajo el @usuario)
    nb = len(_S["eq"])
    bw = W / nb
    for i, (ph, sp) in enumerate(_S["eq"]):
        hgt = 40 + 120 * (0.45 + 0.35 * math.sin(t * sp * 3 + ph) + 0.2 * math.sin(t * 9 + i)) * (0.6 + 0.4 * bk)
        col = mix(acc, YEL, i / nb)
        x0 = i * bw + 6
        for yy in range(int(H - hgt), H, 22):
            d.rectangle((x0, yy, x0 + bw - 12, yy + 14), fill=col + (150,))
    return img


def background(sc, lt, t):
    img = _bg_frame(sc["bg"], t)
    prev = sc.get("prev_bg")
    if prev and prev != sc["bg"] and lt < 0.45:
        old = _bg_frame(prev, t)
        r = ease_in(lt / 0.45) * 1300 + 10
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).ellipse((540 - r, 960 - r, 540 + r, 960 + r), fill=255)
        img = Image.composite(img, old, mask)
    return img


# ------------------------------------------------------------------ piezas

def burst(d, lt, cx, cy, dur=1.6, power=1.0):
    if not 0 <= lt < dur:
        return
    for (vx, vy, col, sz, ph) in _S["burst"]:
        x = cx + vx * 640 * lt * power
        y = cy + vy * 760 * lt * power + 950 * lt * lt
        ang = ph + lt * 8
        pts = [(x + sz * math.cos(ang + j * math.pi / 2) * (1 if j % 2 else 0.5),
                y + sz * math.sin(ang + j * math.pi / 2) * (1 if j % 2 else 0.5)) for j in range(4)]
        d.polygon(pts, fill=col + (int(255 * max(0, 1 - lt / dur)),))


def flash(img, lt, t0, dur=0.22, a=210):
    if t0 <= lt < t0 + dur:
        img.paste(WHITE, (0, 0), Image.new("L", (W, H), int(a * (1 - (lt - t0) / dur))))


def white_card(d, box, r=40, outline=None):
    rr(d, (box[0] + 6, box[1] + 14, box[2] + 6, box[3] + 14), r, (0, 0, 0, 80))
    rr(d, box, r, (255, 252, 246), outline, 8 if outline else 0)


def neon_box(d, box, col, r=40):
    for w, a in ((26, 30), (16, 60), (8, 120)):
        rr(d, (box[0] - w / 2, box[1] - w / 2, box[2] + w / 2, box[3] + w / 2), r + w / 2, None, col + (a,), 4)
    rr(d, box, r, (16, 8, 30, 225), col, 6)


def sticker(img, s, cx, cy, size, bg, fg, angle=-3, scale=1.0):
    if scale <= 0.02:
        return
    f = tfont(size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    w = int(tmp.textlength(s, font=f)) + 90
    h = size + 60
    st = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    rr(sd, (10, 18, w + 10, h + 14), h / 2, (0, 0, 0, 90))
    rr(sd, (4, 4, w, h), h / 2, bg, WHITE, 7)
    sd.text((w / 2 + 2, h / 2 + 6), s, font=f, fill=fg, anchor="mm")
    paste_c(img, st, cx, cy, scale, angle=angle)


def big_count(d, cx, cy, lt, t0, n, col, R=130):
    """Cuenta 3-2-1 en un círculo que late."""
    if not t0 <= lt < t0 + n:
        return
    s = int(lt - t0)
    num = n - s
    fr = (lt - t0) - s
    k = ease_out_back(min(1, fr / 0.25))
    rad = R * (0.75 + 0.25 * k)
    d.ellipse((cx - rad + 6, cy - rad + 14, cx + rad + 6, cy + rad + 14), fill=(0, 0, 0, 80))
    d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=WHITE)
    d.arc((cx - rad + 10, cy - rad + 10, cx + rad - 10, cy + rad - 10), -90, -90 + 360 * (1 - fr), fill=col,
          width=16)
    d.text((cx, cy + 6), str(num), font=tfont(int(170 * k)), fill=col, anchor="mm")


def shout_text(d, s, cx, cy, lt, t0, size, fill=YEL, dur=None):
    if lt < t0 or (dur and lt > t0 + dur):
        return
    k = ease_out_back(min(1, (lt - t0) / 0.3))
    sz = int(size * (1.6 - 0.6 * k))
    a = 255 if not dur else int(255 * min(1, (t0 + dur - lt) / 0.25))
    sh = math.sin(lt * 60) * 10 * max(0, 1 - (lt - t0) / 0.4)
    d.text((cx + sh + 6, cy + 14), s, font=tfont(sz), fill=(0, 0, 0, int(a * 0.4)), anchor="mm",
           stroke_width=14, stroke_fill=(0, 0, 0, int(a * 0.4)))
    d.text((cx + sh, cy), s, font=tfont(sz), fill=fill + (a,), anchor="mm", stroke_width=14,
           stroke_fill=DARK + (a,))


def result_pill(d, img, s, y, lt, t0, col, size=60, emoji="cerveza"):
    b = pop(lt, t0, 0.4)
    if b <= 0:
        return
    pulse = 1 + 0.03 * math.sin(lt * 7)
    box = pill(d, 560, y + (1 - b) * 120, s, int(size * max(b, 0.1) * pulse), WHITE, col, pad=(46, 26))
    paste_c(img, spr(emoji, 140), box[0] - 34, y + (1 - b) * 120 + math.sin(lt * 5) * 6, b, angle=-12)


# ------------------------------------------------------------------ cabecera de prueba

def meter(img, d, sc, lt):
    n, k = sc["n"], sc["k"]
    c = _S["c"]
    y = 125
    xs = [540 + (i - (n - 1) / 2) * 132 for i in range(n)]
    d.line([(xs[0], y), (xs[-1], y)], fill=(255, 255, 255, 70), width=8)
    if k > 0:
        d.line([(xs[0], y), (xs[k], y)], fill=YEL + (230,), width=8)
    for i, x in enumerate(xs):
        p = c["pruebas"][i]
        col = NEON[p["tipo"]]
        if i == k:
            rad = 52 + 4 * math.sin(lt * 7)
            d.ellipse((x - rad - 10, y - rad - 10, x + rad + 10, y + rad + 10), fill=col + (90,))
            d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=WHITE, outline=col, width=7)
            paste_c(img, spr(p["icono"], 72), x, y, 1.0)
        elif i < k:
            d.ellipse((x - 40, y - 40, x + 40, y + 40), fill=WHITE)
            paste_c(img, spr(p["icono"], 54), x, y, 1.0, 0.45)
            check(d, x, y + 2, 40, (22, 170, 90), 9)
        else:
            d.ellipse((x - 40, y - 40, x + 40, y + 40), fill=(0, 0, 0, 90), outline=(255, 255, 255, 90), width=4)
            if p["tipo"] == "final":
                d.text((x, y + 4), "?", font=tfont(56), fill=RED, anchor="mm", stroke_width=4, stroke_fill=WHITE)
            else:
                paste_c(img, spr(p["icono"], 54), x, y, 1.0, 0.5)


def header(img, d, sc, lt):
    p, k, T = sc["p"], sc["k"], sc["T"]
    col = NEON[p["tipo"]]
    m0 = T["m0"]
    final = p["tipo"] == "final"
    # vuelo: grande en el centro durante el anuncio → sube a la cabecera
    mv = ease_in(min(1, max(0, (lt - (m0 - 0.4)) / 0.4)))
    a = pop(lt, 0.0, 0.35)
    if a <= 0:
        return
    y1 = 830 + (240 - 830) * mv
    s = (1.5 - 0.5 * mv) * a
    sh = math.sin(lt * 55) * 14 * max(0, 1 - lt / 0.4)
    if mv < 1:
        ic = spr(p["icono"], 300)
        paste_c(img, ic, 540, 560 + math.sin(lt * 4) * 12 - 200 * mv, (1 - mv) * a, 1 - mv,
                angle=math.sin(lt * 3) * 8 + (1 - a) * 90)
    lab = "PRUEBA FINAL" if final else f"PRUEBA {k + 1}"
    pill(d, 540 + sh, y1, lab, int(46 * s), col if not final else WHITE, WHITE if not final else RED,
         pad=(30, 12))
    f = tfont(int(100 * s))
    name = p["nombre"]
    while d.textlength(name, font=f) > 1000 and f.size > 40:
        f = tfont(f.size - 4)
    yn = y1 + 105 * s
    if final:
        g = 10 * (1 - mv) + 4
        jx = math.sin(lt * 37) * g
        d.text((540 + jx - 8, yn), name, font=f, fill=(0, 255, 255, 170), anchor="mm")
        d.text((540 - jx + 8, yn), name, font=f, fill=(255, 0, 80, 170), anchor="mm")
        text(d, (540 + sh, yn), name, f, WHITE, 12, (60, 0, 10), sh=8)
    else:
        text(d, (540 + sh, yn), name, f, WHITE, 12, mix(col, (0, 0, 0), 0.6), sh=10)


# ------------------------------------------------------------------ mecánicas

def appear(lt, T, d=0.45):
    return pop(lt, T["m0"] - 0.25, d)


def draw_ruleta(img, d, sc, lt):
    p, T = sc["p"], sc["T"]
    a = appear(lt, T)
    if a <= 0:
        return
    cx, cy, R = 540, 945, 360
    phi = wheel_phi(T, lt)
    spinning = T["spin"] <= lt < T["res"]
    # halo y aro con bombillas
    bk = beat_k(lt)
    rad = (R + 46) * a
    d.ellipse((cx - rad - 24, cy - rad - 24, cx + rad + 24, cy + rad + 24), fill=NEON["ruleta"] + (int(50 + 50 * bk),))
    d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=(40, 16, 60), outline=YEL, width=8)
    for i in range(24):
        ang = math.radians(i * 15)
        bx, by = cx + (R + 24) * a * math.sin(ang), cy - (R + 24) * a * math.cos(ang)
        on = (i + int(lt * (14 if spinning else 4))) % 2 == 0
        r0 = 11 * a
        d.ellipse((bx - r0, by - r0, bx + r0, by + r0), fill=(255, 250, 200) if on else (150, 90, 40))
        if on:
            d.ellipse((bx - r0 * 2, by - r0 * 2, bx + r0 * 2, by + r0 * 2), fill=(255, 240, 150, 50))
    w = _S["wheel"].rotate(-phi, resample=Image.BICUBIC)
    paste_c(img, w, cx, cy, a)
    seg = T["seg"]
    if lt >= T["res"]:
        off = ((p["gana"] * seg + phi + 180) % 360) - 180
        gl = 0.5 + 0.5 * math.sin((lt - T["res"]) * 10)
        d.pieslice((cx - R, cy - R, cx + R, cy + R), -90 + off - seg / 2, -90 + off + seg / 2,
                   fill=(255, 255, 255, int(40 + 70 * gl)), outline=YEL, width=8)
    # centro
    d.ellipse((cx - 78 * a, cy - 78 * a, cx + 78 * a, cy + 78 * a), fill=WHITE, outline=YEL, width=8)
    paste_c(img, spr("rayo", 100), cx, cy, a)
    # puntero que se engancha con cada sector
    frac = ((phi + seg / 2) / seg) % 1
    tilt = -22 * max(0, 1 - frac * 4) if spinning else 0
    px, py = cx, cy - R - 30
    pts = [(-40, -40), (40, -40), (0, 50)]
    ca, sa = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    poly = [(px + x * ca - y * sa, py + x * sa + y * ca) for x, y in pts]
    d.polygon([(x + 5, y + 8) for x, y in poly], fill=(0, 0, 0, 90))
    d.polygon(poly, fill=YEL, outline=DARK, width=5)
    d.ellipse((px - 16, py - 56, px + 16, py - 24), fill=RED, outline=WHITE, width=4)
    if lt < T["res"]:
        if lt > T["m0"] + 0.1:
            k = 1 + 0.05 * math.sin(lt * 8)
            pill(d, 540, 1490, "¿A QUIÉN LE TOCA?", int(56 * k), WHITE, NEON["ruleta"], pad=(40, 22))
    else:
        b = pop(lt, T["res"] + 0.1, 0.4)
        y0 = 1395 + (1 - b) * 200
        box = (70, y0, 1010, y0 + 200)
        white_card(d, box, 44, NEON["ruleta"])
        f, lines, lh = _fit_t(d, p["resultado"].upper(), 680, 160, 66, 36)
        yy = y0 + 100 - lh * len(lines) / 2 + lh / 2
        for ln in lines:
            d.text((620, yy), ln, font=f, fill=DARK, anchor="mm")
            yy += lh
        paste_c(img, spr("cerveza", 150), 165, y0 + 100 + math.sin(lt * 6) * 6, b, angle=-12)
        burst(d, lt - T["res"], 540, 900, 1.6)


def draw_senalar(img, d, sc, lt):
    p, T = sc["p"], sc["T"]
    col = NEON["senalar"]
    a = appear(lt, T)
    if a <= 0:
        return
    y0 = 430 + (1 - a) * 300
    box = (70, y0, 1010, y0 + 400)
    white_card(d, box, 46, col)
    d.text((500, y0 + 70), "¿QUIÉN ES MÁS PROBABLE QUE…", font=tfont(48), fill=mix(col, DARK, 0.35), anchor="mm")
    f, lines, lh = _fit_t(d, p["pregunta"], 820, 240, 92, 44)
    yy = y0 + 240 - lh * len(lines) / 2 + lh / 2
    for ln in lines:
        d.text((540, yy), ln, font=f, fill=DARK, anchor="mm")
        yy += lh
    paste_c(img, spr(p["emoji"], 170), 975, y0 - 30 + math.sin(lt * 3) * 10, a, angle=10)
    cy = 1185
    if lt < T["cd"]:
        k = 1 + 0.06 * math.sin(lt * 6)
        pill(d, 540, cy, "A LA DE 3… ¡SEÑALAD!", int(60 * k), col, WHITE, pad=(40, 22))
        paste_c(img, spr("senala", 170), 540 + math.sin(lt * 5) * 30, cy + 170, a)
    big_count(d, 540, cy + 30, lt, T["cd"], 3, mix(col, DARK, 0.2))
    go = T["go"]
    if lt >= go:
        k = ease_out(min(1, (lt - go) / 0.35))
        for j in range(6):
            al = math.radians(j * 60 + 30)
            r = 560 - 270 * k
            x, y = 540 + r * math.cos(al), cy + 30 + r * math.sin(al) * 0.9
            ang = -math.degrees(math.atan2(-(math.sin(al) * 0.9), -math.cos(al)))
            paste_c(img, spr("senala", 170), x, y + math.sin(lt * 12 + j) * 6, 1.0,
                    angle=-ang + math.sin(lt * 14 + j) * 5)
        shout_text(d, "¡SEÑALAD!", 540, cy + 30, lt, go, 150, YEL, dur=(T["res"] - go))
        flash(img, lt, go)
        burst(d, lt - go, 540, cy, 1.5)
    if lt >= T["res"]:
        result_pill(d, img, p["resultado"].upper(), cy + 30, lt, T["res"], mix(col, DARK, 0.25), 58)


def draw_yo_nunca(img, d, sc, lt):
    p, T = sc["p"], sc["T"]
    col = NEON["yo_nunca"]
    k = sc["k"]
    a = appear(lt, T)
    if a <= 0:
        return
    fr = T["frases"]
    for i, (tt, stamp) in enumerate(fr):
        nxt = fr[i + 1][0] if i + 1 < len(fr) else None
        if lt < tt - 0.02 or (nxt is not None and lt > nxt + 0.45):
            continue
        q = ease_out_back(min(1, (lt - tt) / 0.5))
        x = 1500 + (540 - 1500) * q
        ang = 25 * (1 - q) - 3 + math.sin(lt * 2 + i) * 1.5
        if nxt is not None and lt > nxt:
            e = ease_in(min(1, (lt - nxt) / 0.45))
            x = 540 - 1100 * e
            ang = -3 + 30 * e
        paste_c(img, _S["yo"][(k, i)], x, 900 + math.sin(lt * 2.4 + i) * 10, 1.0, angle=ang)
        if lt >= stamp and (nxt is None or lt < nxt):
            b = ease_out_back(min(1, (lt - stamp) / 0.3))
            st_im = Image.new("RGBA", (380, 200), (0, 0, 0, 0))
            sd = ImageDraw.Draw(st_im)
            rr(sd, (6, 6, 374, 194), 36, RED + (235,), WHITE, 9)
            sd.text((190, 104), "¡BEBE!", font=tfont(120), fill=WHITE, anchor="mm")
            paste_c(img, st_im, 790, 1170, 1.7 - 0.7 * b, angle=-12)
            paste_c(img, spr("cervezas", 230), 270, 1180 + math.sin((lt - stamp) * 14) * 10, b,
                    angle=math.sin((lt - stamp) * 12) * 8)
            burst(d, lt - stamp, 540, 1000, 1.4, 0.9)
    pk = 1 + 0.04 * math.sin(lt * 6)
    pill(d, 540, 1480 + (1 - a) * 200, "SI LO HAS HECHO… ¡BEBE!", int(60 * pk), WHITE, mix(col, DARK, 0.2),
         pad=(44, 24))


def draw_reflejos(img, d, sc, lt):
    p, T = sc["p"], sc["T"]
    col = NEON["reflejos"]
    a = appear(lt, T)
    if a <= 0:
        return
    y0 = 420 + (1 - a) * 300
    white_card(d, (70, y0, 1010, y0 + 230), 44, col)
    paste_c(img, spr("cerveza", 170), 175, y0 + 115 + math.sin(lt * 4) * 6, a, angle=-10)
    d.text((620, y0 + 75), "CUANDO SALGA LA CERVEZA", font=tfont(50), fill=DARK, anchor="mm")
    d.text((620, y0 + 155), "¡GOLPEAD LA MESA!", font=tfont(74), fill=mix(col, DARK, 0.4), anchor="mm")
    cx, cy = 540, 1060
    cur = None
    for name, at in T["items"]:
        if lt >= at:
            cur = (name, at)
    # rayos giratorios detrás
    bk = beat_k(lt)
    rays = 14
    rot = lt * 0.8
    R = 430
    hot = cur and cur[0] == "cerveza"
    rc = YEL if hot else col
    for i in range(rays):
        a0 = rot + i * 2 * math.pi / rays
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                   (cx + R * math.cos(a0 + 0.13), cy + R * math.sin(a0 + 0.13))], fill=rc + (int(40 + 40 * bk),))
    d.ellipse((cx - 230, cy - 230, cx + 230, cy + 230), fill=(255, 255, 255, 40), outline=rc + (200,), width=8)
    if cur is None:
        k = 1 + 0.08 * math.sin(lt * 9)
        text(d, (cx, cy), "¡ATENTOS!", tfont(int(110 * k)), WHITE, 12, DARK, sh=8)
    else:
        name, at = cur
        q = ease_out_back(min(1, (lt - at) / 0.22))
        ang = math.sin(lt * 30) * 8 if name in p.get("trampas", []) else 0
        size = 420 if name != "cerveza" else int(470 * (1 + 0.04 * math.sin(lt * 10)))
        paste_c(img, spr(name, 256), cx, cy, size / 256 * q, angle=ang)
    ya = T["ya"]
    if lt >= ya:
        flash(img, lt, ya, 0.3, 230)
        shout_text(d, "¡YA!", cx, 1360, lt, ya, 230, YEL, dur=T["res"] - ya)
        for j, x in enumerate((170, 910)):
            k = ease_out_back(min(1, (lt - ya) / 0.3))
            paste_c(img, spr("mano", 220), x, 1650 - 300 * k + abs(math.sin((lt - ya) * 14)) * 30, 1.0,
                    angle=(15 if j else -15))
        burst(d, lt - ya, cx, cy, 1.6, 1.1)
    if lt >= T["res"]:
        l1, l2 = p["resultado"]
        b = pop(lt, T["res"], 0.4)
        pill(d, 540, 1395 + (1 - b) * 150, l1, int(70 * max(b, 0.1)), WHITE, DARK, pad=(44, 22))
        b2 = pop(lt, T["res"] + 0.6, 0.4)
        if b2 > 0:
            pill(d, 540, 1520 + (1 - b2) * 150, l2, int(50 * b2), mix(col, DARK, 0.35), WHITE, pad=(36, 20))


def _fuse_pts(cx, cy, s):
    x0, y0 = cx + 0.30 * s, cy - 0.36 * s
    pts = []
    for i in range(41):
        u = i / 40
        pts.append((x0 + 150 * u + 40 * math.sin(u * 5), y0 - 210 * u + 30 * math.sin(u * 7)))
    return pts


def draw_bomba(img, d, sc, lt):
    p, T = sc["p"], sc["T"]
    col = NEON["bomba"]
    a = appear(lt, T)
    if a <= 0:
        return
    y0 = 420 + (1 - a) * 300
    white_card(d, (70, y0, 1010, y0 + 220), 44, col)
    d.text((520, y0 + 62), "POR TURNOS · SIN REPETIR", font=tfont(44), fill=mix(col, DARK, 0.3), anchor="mm")
    f = tfont(84)
    while d.textlength(p["categoria"], font=f) > 760:
        f = tfont(f.size - 4)
    d.text((520, y0 + 150), p["categoria"], font=f, fill=DARK, anchor="mm")
    paste_c(img, spr(p["emoji"], 170), 935, y0 + 10 + math.sin(lt * 3) * 8, a, angle=8)
    boom = T["boom"]
    fs, S = T["fuse"], T["S"]
    cx, cy, s = 540, 1130, 400 * a
    if lt < boom:
        prog = min(1, max(0, (lt - fs) / S))
        amp = 2 + 16 * prog ** 2
        rate = 3 + 14 * prog
        pk = 0.5 + 0.5 * math.sin(lt * rate)
        jx, jy = math.sin(lt * 47) * amp, math.cos(lt * 53) * amp
        d.ellipse((cx - 300, cy - 300, cx + 300, cy + 300), fill=(255, 40, 40, int(30 + 90 * pk * (0.3 + prog))))
        pts = _fuse_pts(cx + jx, cy + jy, s)
        keep = max(2, int(len(pts) * (1 - prog)))
        d.line(pts[:keep], fill=(220, 190, 140), width=12, joint="curve")
        d.line(pts[:keep], fill=(120, 90, 60), width=4, joint="curve")
        if lt >= fs:
            ex, ey = pts[keep - 1]
            rnd = random.Random(int(lt * FPS))
            for _ in range(14):
                ang = rnd.uniform(0, 6.28)
                r = rnd.uniform(10, 60)
                c2 = rnd.choice([(255, 230, 80), (255, 150, 30), WHITE])
                d.line([(ex, ey), (ex + r * math.cos(ang), ey + r * math.sin(ang))], fill=c2, width=4)
            d.ellipse((ex - 18, ey - 18, ex + 18, ey + 18), fill=(255, 240, 160))
        paste_c(img, spr("bomba", 256), cx + jx, cy + jy, s / 256 * (1 + 0.05 * pk * prog))
        rem = S if lt < fs else max(1, math.ceil(S - (lt - fs)))
        text(d, (cx + jx - 10, cy + jy + 40), str(rem), tfont(int(150 * a)), WHITE, 10, (60, 0, 0))
        if lt < fs and lt > T["m0"]:
            pill(d, 540, 1560, "¿PREPARADOS?", 52, WHITE, col, pad=(36, 20))
    else:
        e = lt - boom
        flash(img, lt, boom, 0.35, 255)
        if e < 1.2:
            paste_c(img, spr("explosion", 256), cx, cy, (1.2 + 3.0 * ease_out(e / 0.5)) * 400 / 256 * 0.6,
                    max(0, 1 - e / 1.2), angle=e * 40)
        burst(d, e, cx, cy - 100, 1.8, 1.4)
        shout_text(d, "¡BOOM!", 540, 1050, lt, boom, 220, YEL)
        if lt >= T["res"]:
            result_pill(d, img, p["resultado"], 1300, lt, T["res"], RED, 70)
            b = pop(lt, T["res"] + 0.4, 0.4)
            if b > 0:
                d.text((540, 1430), "A QUIEN LE HAYA EXPLOTADO", font=tfont(int(50 * b)), fill=WHITE, anchor="mm",
                       stroke_width=8, stroke_fill=DARK)


def draw_esto_aquello(img, d, sc, lt):
    p, T = sc["p"], sc["T"]
    col = NEON["esto_aquello"]
    a = appear(lt, T)
    if a <= 0:
        return
    l1, l2 = p["pregunta"]
    text(d, (540, 480), l1, tfont(int(80 * a)), WHITE, 11, DARK, sh=8)
    text(d, (540, 570), l2, tfont(int(80 * a)), YEL, 11, DARK, sh=8)
    ca, cb = (255, 150, 40), col
    for j, (lab, emo) in enumerate((p["a"], p["b"])):
        side = -1 if j == 0 else 1
        x = 540 + side * 245 + side * (1 - a) * 700
        y = 935 + math.sin(lt * 2.2 + j * 2) * 12
        cc = ca if j == 0 else cb
        box = (x - 215, y - 250, x + 215, y + 250)
        for w, al in ((26, 30), (14, 70)):
            rr(d, (box[0] - w / 2, box[1] - w / 2, box[2] + w / 2, box[3] + w / 2), 40 + w / 2, None, cc + (al,), 4)
        rr(d, box, 40, mix(cc, (20, 10, 40), 0.25), WHITE, 7)
        paste_c(img, spr("huevo", 200), x - (40 if j == 0 else 0), y - 70, 1.0)
        if j == 0:
            paste_c(img, spr(emo, 150), x + 70, y - 20, 1.0, angle=12)
        else:
            paste_c(img, spr("cebolla", 120), x + 70, y - 10, 1.0, 0.7)
            d.ellipse((x + 10, y - 70, x + 130, y + 50), outline=RED, width=12)
            d.line([(x + 28, y + 32), (x + 112, y - 52)], fill=RED, width=12)
        f = tfont(52)
        while d.textlength(lab, font=f) > 380:
            f = tfont(f.size - 2)
        d.text((x, y + 180), lab, font=f, fill=WHITE, anchor="mm", stroke_width=6, stroke_fill=DARK)
    # VS
    bk = beat_k(lt)
    r = 82 * a * (1 + 0.08 * bk)
    d.ellipse((540 - r - 12, 935 - r - 12, 540 + r + 12, 935 + r + 12), fill=YEL + (80,))
    d.ellipse((540 - r, 935 - r, 540 + r, 935 + r), fill=YEL, outline=WHITE, width=7)
    d.text((540, 941), "VS", font=tfont(int(84 * a)), fill=DARK, anchor="mm")
    cy = 1360
    if lt < T["cd"]:
        k = 1 + 0.06 * math.sin(lt * 6)
        pill(d, 540, cy, "A LA DE 3… ¡VOTAD!", int(58 * k), col, WHITE, pad=(40, 22))
    big_count(d, 540, cy, lt, T["cd"], 3, col, R=115)
    go = T["go"]
    if lt >= go:
        for j in range(4):
            x = 150 + j * 260
            k = ease_out_back(min(1, max(0, (lt - go - j * 0.06) / 0.35)))
            paste_c(img, spr("mano", 170), x, 1900 - 330 * k + math.sin(lt * 10 + j) * 12, 1.0,
                    angle=math.sin(lt * 8 + j) * 10)
        shout_text(d, "¡VOTAD!", 540, cy, lt, go, 170, YEL, dur=T["res"] - go)
        flash(img, lt, go)
        burst(d, lt - go, 540, 900, 1.5)
    if lt >= T["res"]:
        result_pill(d, img, p["resultado"].upper(), cy, lt, T["res"], mix(col, DARK, 0.2), 44)


def draw_final(img, d, sc, lt):
    p, T = sc["p"], sc["T"]
    m0 = T["m0"]
    a = pop(lt, m0 - 0.1, 0.45)
    if a > 0:
        b = pop(lt, m0, 0.4)
        pill(d, 540, 440, "EL TRABALENGUAS MALDITO", int(54 * max(b, 0.1)), RED, WHITE, pad=(40, 20))
        y0 = 540 + (1 - a) * 400
        box = (70, y0, 1010, y0 + 470)
        neon_box(d, box, GOLD, 44)
        words = p["trabalenguas"].split()
        tot = sum(len(w) + 1 for w in words)
        v0, vd = T["tw_v"], T["tw_d"]
        f = tfont(92)
        lines, cur = [], []
        for w in words:
            if cur and d.textlength(" ".join(cur + [w]), font=f) > 860:
                lines.append(cur)
                cur = []
            cur.append(w)
        lines.append(cur)
        lh = 112
        yy = y0 + 235 - lh * len(lines) / 2 + lh / 2
        acc = 0
        for ln in lines:
            widths = [d.textlength(w, font=f) for w in ln]
            sp = d.textlength(" ", font=f)
            x = 540 - (sum(widths) + sp * (len(ln) - 1)) / 2
            for w, ww in zip(ln, widths):
                tw0 = v0 + vd * acc / tot
                tw1 = v0 + vd * (acc + len(w) + 1) / tot
                acc += len(w) + 1
                if lt >= tw0 - 0.05 or lt >= T["turno"]:
                    q = ease_out_back(min(1, (lt - tw0) / 0.2)) if lt < T["turno"] else 1
                    on = tw0 <= lt < tw1 + 0.1
                    fill = YEL if on else WHITE
                    ff = tfont(int(92 * (0.6 + 0.4 * q) * (1.08 if on else 1)))
                    d.text((x + ww / 2, yy), w, font=ff, fill=fill, anchor="mm", stroke_width=6, stroke_fill=DARK)
                x += ww + sp
            yy += lh
        if lt >= T["tw"]:
            q = pop(lt, T["tw"], 0.4)
            paste_c(img, spr("tigre", 200), 160, y0 + 470 + math.sin(lt * 7) * 12 - 10, q, angle=-8)
            paste_c(img, spr("trigo", 170), 930, y0 + 460 + math.sin(lt * 6 + 1) * 10, q, angle=10)
            sticker(img, "×3 SIN FALLAR", 830, y0 - 8, 44, YEL, DARK, angle=8, scale=q)
    tu, S = T["turno"], T["S"]
    if tu <= lt < T["res"]:
        b = pop(lt, tu, 0.4)
        k = 1 + 0.05 * math.sin(lt * 8)
        pill(d, 540, 1165, "¡VUESTRO TURNO!", int(76 * max(b, 0.1) * k), YEL, DARK, pad=(46, 24))
        rem = max(0.0, tu + S - lt)
        n = int(math.ceil(rem))
        cx, cy, R = 540, 1360, 105 * b
        urgent = rem <= 3
        cc = RED if urgent else GOLD
        if R > 20:
            d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=WHITE)
            d.arc((cx - R + 8, cy - R + 8, cx + R - 8, cy + R - 8), -90, -90 + 360 * rem / S, fill=cc, width=15)
            d.text((cx, cy + 5), str(max(n, 1)), font=tfont(int(110 * b)), fill=cc if urgent else DARK, anchor="mm")
        d.text((540, 1530), "UNO POR UNO · PAUSA SI HACE FALTA", font=tfont(44), fill=WHITE, anchor="mm",
               stroke_width=7, stroke_fill=DARK)
        if urgent:
            v = 0.5 + 0.5 * math.sin(lt * 2 * math.pi * 2)
            for w, al in ((40, 60), (80, 30)):
                d.rectangle((0, 0, W, H), outline=RED + (int(al * v),), width=w)
    if lt >= T["res"]:
        b = pop(lt, T["res"], 0.4)
        pill(d, 540, 1160 + (1 - b) * 150, "¿FALLAS? ¡BEBE!", int(70 * max(b, 0.1)), RED, WHITE, pad=(44, 22))
        c2 = pop(lt, T["crown"], 0.45)
        if c2 > 0:
            y0 = 1290 + (1 - c2) * 200
            box = (90, y0, 990, y0 + 270)
            gl = 0.5 + 0.5 * math.sin(lt * 6)
            d.rounded_rectangle((box[0] - 18, box[1] - 18, box[2] + 18, box[3] + 18), 56, fill=GOLD + (int(50 + 60 * gl),))
            rr(d, box, 44, (255, 246, 214), GOLD, 9)
            d.text((540, y0 + 95), "¿LO CONSIGUES?", font=tfont(56), fill=(170, 100, 0), anchor="mm")
            d.text((540, y0 + 185), "REY DE LA FIESTA: REPARTES 5", font=tfont(56), fill=DARK, anchor="mm")
            ce = ease_out_back(min(1, (lt - T["crown"]) / 0.5))
            paste_c(img, spr("corona", 200), 540, y0 - 30 - (1 - ce) * 500 + math.sin(lt * 4) * 8, 1.0,
                    angle=math.sin(lt * 3) * 8)
            burst(d, lt - T["crown"], 540, y0, 1.6)
    # relámpagos
    for f0 in T["flashes"]:
        if f0 <= lt < f0 + 0.35:
            k = 1 - (lt - f0) / 0.35
            img.paste((255, 230, 230), (0, 0), Image.new("L", (W, H), int(170 * k * (0.6 + 0.4 * math.sin(lt * 90)))))


MECH = {"ruleta": draw_ruleta, "senalar": draw_senalar, "yo_nunca": draw_yo_nunca, "reflejos": draw_reflejos,
        "bomba": draw_bomba, "esto_aquello": draw_esto_aquello, "final": draw_final}


def draw_prueba(img, d, sc, lt):
    meter(img, d, sc, lt)
    MECH[sc["p"]["tipo"]](img, d, sc, lt)
    header(img, d, sc, lt)


# ------------------------------------------------------------------ escenas

def disco_ball(img, d, cx, cy, size, t, rays=True):
    if rays:
        for i in range(10):
            a = t * 0.9 + i * 2 * math.pi / 10
            col = CONF_COLS[i % len(CONF_COLS)]
            L = 1500
            d.polygon([(cx, cy), (cx + L * math.cos(a - 0.04), cy + L * math.sin(a - 0.04)),
                       (cx + L * math.cos(a + 0.04), cy + L * math.sin(a + 0.04))], fill=col + (38,))
    d.line([(cx, 0), (cx, cy - size / 2)], fill=(220, 220, 230), width=5)
    paste_c(img, spr("bola_disco", 256), cx, cy, size / 256, angle=math.sin(t * 1.5) * 6)
    ph = (t * 3) % 1
    sx, sy = cx - size * 0.18, cy - size * 0.12
    r = 18 * math.sin(ph * math.pi)
    d.polygon([(sx, sy - r * 2), (sx + r * 0.4, sy), (sx, sy + r * 2), (sx - r * 0.4, sy)], fill=WHITE)
    d.polygon([(sx - r * 2, sy), (sx, sy - r * 0.4), (sx + r * 2, sy), (sx, sy + r * 0.4)], fill=WHITE)


def draw_hook(img, d, sc, lt):
    c = _S["c"]
    l1, l2 = c["gancho"]["texto"]
    drop = ease_out_back(min(1, lt / 0.5))
    disco_ball(img, d, 540, -160 + 400 * drop, 260, lt)
    # carrusel con las pruebas girando (la última, bloqueada)
    items = []
    n = len(c["pruebas"])
    for i, p in enumerate(c["pruebas"]):
        ang = 2 * math.pi * i / n + lt * 1.1
        depth = (math.sin(ang) + 1) / 2
        items.append((depth, i, p, ang))
    for depth, i, p, ang in sorted(items, key=lambda x: x[0]):
        a = pop(lt, 0.2 + 0.09 * i, 0.35)
        x = 540 + 390 * math.cos(ang)
        y = 1110 + 140 * math.sin(ang)
        s = (0.6 + 0.5 * depth) * a
        if s <= 0:
            continue
        if p["tipo"] == "final":
            rad = 90 * s
            d.ellipse((x - rad - 14, y - rad - 14, x + rad + 14, y + rad + 14), fill=RED + (90,))
            d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(30, 0, 8), outline=RED, width=6)
            paste_c(img, spr("calavera", 120), x, y, s, 0.5 + 0.5 * depth)
            d.text((x, y + 4), "?", font=tfont(max(10, int(120 * s))), fill=WHITE, anchor="mm", stroke_width=6,
                   stroke_fill=RED)
        else:
            rad = 86 * s
            d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=WHITE, outline=NEON[p["tipo"]], width=7)
            paste_c(img, spr(p["icono"], 120), x, y, s * 1.05)
    p_ = ease_out(min(1, lt / 0.28))
    sh = math.sin(lt * 50) * 12 * max(0, 1 - lt / 0.4)
    sc_ = 1.18 - 0.18 * p_
    text(d, (540 + sh, 560), l1, tfont(int(118 * sc_)), WHITE, 14, DARK, sh=10)
    text(d, (540 - sh, 710), l2, tfont(int(118 * sc_)), YEL, 14, DARK, sh=10)
    b = pop(lt, 0.55, 0.4)
    sticker(img, c["gancho"]["pegatina"], 560, 1420 + math.sin(lt * 4) * 6, 58, RED, WHITE, angle=-3,
            scale=b * (1 + 0.04 * math.sin(lt * 8)))
    if b > 0:
        paste_c(img, spr("calavera", 130), 135, 1405, b, angle=-14 + math.sin(lt * 6) * 6)
    for j, (nm, x) in enumerate((("coctel", 130), ("champan", 950))):
        a = pop(lt, 0.3 + 0.15 * j, 0.4)
        paste_c(img, spr(nm, 170), x, 1580 + math.sin(lt * 4 + j) * 14, a, angle=(-15 if j == 0 else 15))
    burst(d, lt - 0.05, 540, 700, 1.5, 1.2)
    flash(img, lt, 0.0, 0.2, 220)


def draw_instr(img, d, sc, lt):
    c = _S["c"]
    disco_ball(img, d, 540, 150, 170, lt, rays=False)
    text(d, (540, 360), "¿CÓMO SE JUEGA?", tfont(92), WHITE, 12, DARK, sh=10)
    for i, (emo, s) in enumerate(c["instrucciones"]["pasos"]):
        a = pop(lt, 0.3 + 0.3 * i, 0.4)
        if a <= 0:
            continue
        y = 560 + i * 210 + math.sin(lt * 3 + i) * 6
        x0 = 90 + (1 - a) * (-900 if i % 2 == 0 else 900)
        box = (x0, y - 85, x0 + 900, y + 85)
        white_card(d, box, 44, CONF_COLS[(i * 2 + 1) % len(CONF_COLS)])
        paste_c(img, spr(emo, 130), x0 + 100, y, 1.0, angle=-8)
        f = tfont(58)
        while d.textlength(s, font=f) > 680:
            f = tfont(f.size - 2)
        d.text((x0 + 190, y + 2), s, font=f, fill=DARK, anchor="lm")
    a = pop(lt, 1.2, 0.4)
    if a > 0:
        d.text((540, 1215), c["instrucciones"]["nota"], font=font(int(44 * a)), fill=WHITE, anchor="mm",
               stroke_width=4, stroke_fill=DARK)
    b = pop(lt, 0.9, 0.4)
    if b > 0:
        k = 1 + 0.05 * math.sin(lt * 8)
        box = pill(d, 600, 1390, "PAUSA SI HACE FALTA", int(62 * b * k), YEL, DARK, pad=(48, 26))
        bx = box[0] - 30
        d.ellipse((bx - 58, 1332, bx + 58, 1448), fill=DARK, outline=WHITE, width=6)
        d.rounded_rectangle((bx - 24, 1360, bx - 8, 1420), 4, fill=WHITE)
        d.rounded_rectangle((bx + 8, 1360, bx + 24, 1420), 4, fill=WHITE)


def fireworks(d, lt, fws):
    for j, (t0, x, y) in enumerate(fws):
        col = CONF_COLS[j % len(CONF_COLS)]
        if t0 - 0.55 <= lt < t0:
            q = (lt - (t0 - 0.55)) / 0.55
            ry = H - 200 + (y - (H - 200)) * ease_out(q)
            d.line([(x, ry), (x, ry + 60)], fill=col + (200,), width=6)
            d.ellipse((x - 8, ry - 8, x + 8, ry + 8), fill=WHITE)
        e = lt - t0
        if 0 <= e < 1.6:
            n = 30
            rnd = random.Random(j)
            for i in range(n):
                ang = 2 * math.pi * i / n + rnd.uniform(-0.05, 0.05)
                sp = rnd.uniform(260, 380)
                px = x + math.cos(ang) * sp * ease_out(min(1, e / 1.0))
                py = y + math.sin(ang) * sp * ease_out(min(1, e / 1.0)) + 120 * e * e
                al = int(255 * max(0, 1 - e / 1.6))
                r = 7 * (1 - e / 2)
                d.line([(px, py), (px - math.cos(ang) * 30, py - math.sin(ang) * 30 - 10 * e)],
                       fill=col + (al // 2,), width=4)
                d.ellipse((px - r, py - r, px + r, py + r), fill=col + (al,))


def draw_brindis(img, d, sc, lt):
    fireworks(d, lt, sc["fws"])
    a = pop(lt, 0.05, 0.4)
    sh = math.sin(lt * 50) * 12 * max(0, 1 - lt / 0.4)
    text(d, (540 + sh, 640), "¡BRINDIS", tfont(int(150 * max(a, 0.05))), WHITE, 14, (90, 30, 0), sh=10)
    text(d, (540 - sh, 800), "FINAL!", tfont(int(170 * max(a, 0.05))), GOLD, 15, (90, 30, 0), sh=10)
    ck = sc["clink"]
    hit = max(0, 1 - abs(lt - ck) / 0.25)
    for j, x in enumerate((330, 750)):
        side = -1 if j == 0 else 1
        b = pop(lt, 0.15 + 0.1 * j, 0.45)
        xx = x - side * 60 * hit + side * 40 * max(0, 1 - lt / ck) if ck > 0 else x
        paste_c(img, spr("cerveza", 256), xx, 1130 + math.sin(lt * 5 + j) * 10, b * 1.3,
                angle=side * (-14 + 10 * hit))
    if lt >= ck:
        burst(d, lt - ck, 540, 1050, 1.8, 1.3)
        e = lt - ck
        rnd = random.Random(int(lt * FPS) // 2)
        for _ in range(30):
            ang = rnd.uniform(-2.6, -0.5)
            r = rnd.uniform(40, 360) * min(1, e / 0.5)
            x, y = 540 + r * math.cos(ang), 1000 + r * math.sin(ang) + 200 * e * e
            s = rnd.uniform(6, 14)
            d.ellipse((x - s, y - s, x + s, y + s), fill=(255, 250, 220, int(200 * max(0, 1 - e / 2))))
    for j, x in enumerate((140, 940)):
        b = pop(lt, 0.4 + 0.1 * j, 0.4)
        paste_c(img, spr("champan", 200), x, 1350 + math.sin(lt * 4 + j) * 8, b, angle=(-25 if j == 0 else 25))
    c2 = pop(lt, ck - 0.1, 0.4)
    if c2 > 0:
        k = 1 + 0.05 * math.sin(lt * 8)
        pill(d, 540, 1470, "¡TODOS ARRIBA!", int(78 * c2 * k), GOLD, DARK, pad=(50, 26))
    disco_ball(img, d, 540, 230, 220, lt)
    flash(img, lt, 0.0, 0.25, 200)


def draw_outro(img, d, sc, lt):
    a = pop(lt, 0.1, 0.45)
    y = 330 + (1 - a) * -600
    box = (80, y, 1000, y + 400)
    white_card(d, box, 48, NEON["ruleta"])
    f = tfont(92)
    d.text((540, y + 120), "¿QUIÉN HA GANADO", font=f, fill=DARK, anchor="mm")
    d.text((540, y + 225), "LA FIESTA?", font=f, fill=(214, 40, 110), anchor="mm")
    d.text((540, y + 330), "¡Etiqueta a tus amigos!", font=font(52), fill=(120, 60, 200), anchor="mm")
    paste_c(img, spr("corona", 170), 540, y - 30 + math.sin(lt * 4) * 8, a, angle=math.sin(lt * 3) * 8)
    c = _S["c"]
    n = len(c["pruebas"])
    for i, p in enumerate(c["pruebas"]):
        b = pop(lt, 0.3 + 0.07 * i, 0.4)
        x = 540 + (i - (n - 1) / 2) * 135
        yy = 900 + math.sin(lt * 5 + i * 0.8) * 16
        if b > 0:
            d.ellipse((x - 58 * b, yy - 58 * b, x + 58 * b, yy + 58 * b), fill=WHITE, outline=NEON[p["tipo"]], width=6)
            paste_c(img, spr(p["icono"], 80), x, yy, b)
    c2 = pop(lt, sc["shout_at"] - 0.15, 0.4)
    if c2 > 0:
        pulse = 1 + 0.07 * math.sin(lt * 9)
        pill(d, 540, 1150 + (1 - c2) * 700, "¡SÍGUEME PARA MÁS!", int(64 * pulse), YEL, DARK)
    c3 = pop(lt, sc["shout_at"] + 0.2, 0.6)
    if c3 > 0:
        size = 290 * c3 * (1 + 0.025 * math.sin(lt * 4))
        d.ellipse((540 - size / 2, 1400 - size / 2 + 14, 540 + size / 2, 1400 + size / 2 + 14), fill=(0, 0, 0, 70))
        paste_c(img, _S["logo"], 540, 1400, size / _S["logo"].width)
    burst(d, lt - sc["shout_at"], 540, 1000, 1.8, 1.2)


DRAW = {"hook": draw_hook, "instr": draw_instr, "prueba": draw_prueba, "brindis": draw_brindis,
        "outro": draw_outro}


def shake_off(sc, lt):
    mag = 0.0
    for t0, pw in sc.get("shakes", []):
        if t0 <= lt < t0 + 0.5:
            mag = max(mag, pw * math.exp(-(lt - t0) * 9))
    if mag < 0.05:
        return 0, 0
    return int(math.sin(lt * 95) * 22 * mag), int(math.cos(lt * 83) * 16 * mag)


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
    img = bg.copy()
    d = ImageDraw.Draw(img, "RGBA")
    DRAW[sc["kind"]](img, d, sc, lt)
    dx, dy = shake_off(sc, lt)
    if dx or dy:
        img = ImageChops.offset(img, dx, dy)
    out_t = sc["dur"] - lt
    if out_t < 0.18 and sc is not scenes[-1]:
        img = Image.blend(bg, img, max(0.0, out_t / 0.18))
    username(img)
    return img.tobytes()


# ------------------------------------------------------------------ portada

def portada(c, state, out_dir):
    _init(state)
    img = _bg_frame("club", 1.3)
    d = ImageDraw.Draw(img, "RGBA")
    disco_ball(img, d, 540, 330, 230, 0.7)
    l1, l2 = c["portada"]["titulo"]
    text(d, (540, 600), l1, tfont(124), WHITE, 15, DARK, sh=12)
    text(d, (540, 750), l2, tfont(124), YEL, 15, DARK, sh=12)
    n = len(c["pruebas"])
    for i, p in enumerate(c["pruebas"]):
        x = 540 + (i - (n - 1) / 2) * 140
        y = 960 + (25 if i % 2 else -25)
        if p["tipo"] == "final":
            d.ellipse((x - 72, y - 72, x + 72, y + 72), fill=(30, 0, 8), outline=RED, width=7)
            d.text((x, y + 4), "?", font=tfont(100), fill=WHITE, anchor="mm", stroke_width=6, stroke_fill=RED)
        else:
            d.ellipse((x - 66, y - 66, x + 66, y + 66), fill=WHITE, outline=NEON[p["tipo"]], width=7)
            paste_c(img, spr(p["icono"], 96), x, y, 1.0)
    big = spr("_ruleta", 360)
    paste_c(img, big.rotate(20, resample=Image.BICUBIC), 290, 1230, 1.0)
    paste_c(img, spr("bomba", 256), 800, 1210, 1.25, angle=-10)
    paste_c(img, spr("cervezas", 256), 560, 1270, 0.95)
    sticker(img, c["portada"]["pegatina"], 540, 1470, 62, RED, WHITE, angle=-3)
    paste_c(img, spr("calavera", 120), 120, 1450, 1.0, angle=-14)
    username(img, 1616)
    p916 = os.path.join(out_dir, f"{c['video']}_9x16.png")
    p34 = os.path.join(out_dir, f"{c['video']}_3x4.png")
    img.save(p916)
    img.crop((0, 240, 1080, 1680)).save(p34)
    return p916, p34


# ------------------------------------------------------------------ exportación

def _link(scenes):
    prev = None
    for s in scenes:
        s["prev_bg"] = prev
        prev = s["bg"]


def render_video(c, voice, out_path, tono, workers=None, preview=None):
    scenes, events, total = build_timeline(c, voice)
    _link(scenes)
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
    build_audio(events, total, wav)
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

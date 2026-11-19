#!/usr/bin/env python3
"""Mezcla voz + efectos (efectos.json, sintetizados: whoosh, pop, clic, golpe, portazo) + música muy baja,
y normaliza a −14 LUFS → assets/mezcla.wav"""
import json, os, subprocess, sys
import numpy as np
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "..", ".."))
from quizvideo import audio
from quizvideo.misterio import sfx_golpe
SR = audio.SR
raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", os.path.join(BASE, "assets", "voz.wav"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"])
voz = np.frombuffer(raw, np.float32).astype(np.float64)
dur = len(voz) / SR
mix = audio.Mixer(dur)
mix.add_voice(voz, 0, 1.0)
def campanita(f0=1320.0, dur=0.9):
    t = np.arange(int(dur * SR)) / SR
    env = np.exp(-t * 5.5) * np.minimum(1, t * 400)
    return env * (0.6 * np.sin(2 * np.pi * f0 * t) + 0.3 * np.sin(2 * np.pi * f0 * 1.5 * t) + 0.15 * np.sin(2 * np.pi * f0 * 2.01 * t))
def transicion():
    """Whoosh suave + campanita: se oye un pelín, sin molestar."""
    w = audio.sfx_whoosh(0.75)
    c = campanita(1568.0, 0.8)
    n = max(len(w), len(c) + int(0.25 * SR))
    out = np.zeros(n); out[:len(w)] += w * 0.8; out[int(0.25 * SR):int(0.25 * SR) + len(c)] += c * 0.5
    return out
def brillo():
    out = np.zeros(int(1.4 * SR))
    for k, f in enumerate((1047, 1319, 1568, 2093)):
        c = campanita(f, 0.9); i = int(k * 0.11 * SR); out[i:i + len(c)] += c[: len(out) - i] * 0.5
    return out
def sube(d=0.9, f0=320.0, f1=760.0):
    """«Uiii» que sube de tono (crecer), con vibrato: divertido."""
    t = np.arange(int(d * SR)) / SR
    f = f0 + (f1 - f0) * (t / d) ** 1.3 + 14 * np.sin(2 * np.pi * 9 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.minimum(1, t * 30) * np.minimum(1, (d - t) * 12)
    return env * (0.55 * np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph))
def boing():
    t = np.arange(int(0.6 * SR)) / SR
    f = 180 + 260 * np.exp(-t * 7) * (1 + 0.5 * np.sin(2 * np.pi * 14 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.exp(-t * 4.5) * np.minimum(1, t * 300) * np.sin(ph)
def timbre(d=1.6):
    """Despertador: campanilla rápida (ring-ring)."""
    t = np.arange(int(d * SR)) / SR
    gate = (np.sin(2 * np.pi * 18 * t) > 0).astype(float)
    return gate * np.minimum(1, (d - t) * 6) * (0.5 * np.sin(2 * np.pi * 2350 * t) + 0.35 * np.sin(2 * np.pi * 3100 * t))
def papel():
    """Pasar página: ruido de papel suave (ruido filtrado con envolvente)."""
    rng = np.random.default_rng(3); n = int(0.45 * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); x = np.convolve(x, np.ones(6) / 6, mode="same")
    return x * np.sin(np.pi * t / 0.45) ** 2 * 0.6
def lapiz():
    """Boli sobre papel: rasgueo muy bajito."""
    rng = np.random.default_rng(5); n = int(0.5 * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); x = x - np.convolve(x, np.ones(3) / 3, mode="same")
    return x * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t)) * np.minimum(1, t * 20) * np.minimum(1, (0.5 - t) * 20) * 0.5
def riser(d=1.0):
    """Subida de tensión (ruido filtrado + tono que sube) que acaba justo en el golpe."""
    rng = np.random.default_rng(12); n = int(d * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); x = x - np.convolve(x, np.ones(4) / 4, mode="same")
    f = 200 + 900 * (t / d) ** 2
    tono = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return (x * 0.5 + tono * 0.5) * (t / d) ** 2.2
def boom(d=2.0):
    rng = np.random.default_rng(9); n = int(d * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    for _ in range(4):
        x = np.convolve(x, np.ones(9) / 9, mode="same")
    sub = np.sin(2 * np.pi * (60 - 25 * t / d) * t)
    return (x * 5 + sub) * np.exp(-t * 2.4) * np.minimum(1, t * 300) * 0.6
def granizo_fx(d=2.5):
    rng = np.random.default_rng(21); n = int(d * SR); out = np.zeros(n)
    for _ in range(int(d * 40)):
        i = rng.integers(0, n - 800); f = rng.uniform(2500, 5000); t = np.arange(600) / SR
        out[i:i + 600] += np.sin(2 * np.pi * f * t) * np.exp(-t * 900) * rng.uniform(0.2, 0.6)
    env = np.minimum(1, np.arange(n) / (0.3 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.5 * SR))
    return out * env * 0.5
def crack_fx():
    rng = np.random.default_rng(4); n = int(0.35 * SR); t = np.arange(n) / SR
    return rng.standard_normal(n) * np.exp(-t * 18) * 0.5
def trueno_fx(d=2.6):
    rng = np.random.default_rng(8); n = int(d * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    for _ in range(6):
        x = np.convolve(x, np.ones(15) / 15, mode="same")
    return x * 8 * np.exp(-t * 1.4) * np.minimum(1, t * 6)
def tambor_fx():
    n = int(0.25 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (140 - 60 * t) * t) * np.exp(-t * 22)
def agua_fx(d=3.0):
    rng = np.random.default_rng(6); n = int(d * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); x = np.convolve(x, np.ones(30) / 30, mode="same")
    return x * 4 * np.minimum(1, t) * np.minimum(1, (d - t) * 2)
def arranque_fx():
    """Arranque flojito: motor de arranque (zumbido a pulsos) y el motor que coge ralentí."""
    n = int(1.5 * SR); t = np.arange(n) / SR
    st = (t < 0.45) * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t)) * np.sin(2 * np.pi * 210 * t) * 0.35
    rpm = np.where(t < 0.45, 0, 1) * (1 + 0.6 * np.exp(-(t - 0.45) * 5) * (t >= 0.45))
    ph = 2 * np.pi * np.cumsum(38 * rpm) / SR
    mot = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph)) * (t >= 0.45) * np.minimum(1, (t - 0.45).clip(0) * 8)
    return (st + mot * 0.6) * np.minimum(1, (1.5 - t) * 3)
def derrape_fx(d=0.9):
    rng = np.random.default_rng(31); n = int(d * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); x = np.convolve(x, np.ones(3) / 3, mode="same") - np.convolve(x, np.ones(25) / 25, mode="same")
    tono = np.sin(2 * np.pi * np.cumsum(1700 + 120 * np.sin(2 * np.pi * 7 * t)) / SR)
    return (x * 0.6 + tono * 0.25) * np.minimum(1, t * 10) * np.exp(-t * 2.2)
def impacto_fx():
    """Golpe seco + hielo que se rompe en trozos (tintineo)."""
    rng = np.random.default_rng(17); n = int(1.2 * SR); t = np.arange(n) / SR
    out = np.sin(2 * np.pi * (90 - 40 * t) * t) * np.exp(-t * 14) * 0.9
    out += rng.standard_normal(n) * np.exp(-t * 30) * 0.5
    for _ in range(26):
        i = int(rng.uniform(0.02, 0.7) * SR); f = rng.uniform(2800, 6500); tt = np.arange(1500) / SR
        out[i:i + 1500] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 260) * rng.uniform(0.15, 0.45)
    return out
fx = {"tic": (audio.sfx_tick(False), 0.10), "tic2": (audio.sfx_tick(True), 0.22), "posit": (sfx_golpe(0.5), 0.22), "sello": (sfx_golpe(1.1), 0.32), "pagina": (papel(), 0.22), "lapiz": (lapiz(), 0.06), "baja": (sube(1.0, 1100, 260), 0.32), "sube": (sube(), 0.3), "sube2": (sube(1.2, 420, 1100), 0.32), "boing": (boing(), 0.45), "timbre": (timbre(), 0.13), "suave": (transicion(), 0.16), "brillo": (brillo(), 0.2), "whoosh": (audio.sfx_whoosh(0.6), 0.35), "pop": (audio.sfx_pop(), 0.35), "clic": (audio.sfx_tick(True), 0.6),
      "golpe": (sfx_golpe(1.0), 0.55), "portazo": (sfx_golpe(1.5), 0.8), "riser": (riser(), 0.22), "granizo": (granizo_fx(), 0.35), "crack": (crack_fx(), 0.3), "trueno": (trueno_fx(), 0.5), "tambor": (tambor_fx(), 0.6), "agua": (agua_fx(), 0.35), "boom": (boom(), 0.7), "arranque": (arranque_fx(), 0.35), "derrape": (derrape_fx(), 0.22), "impacto": (impacto_fx(), 0.9)}
# --- MEZCLA LIMPIA (usuario, 02-11-2026: «no hagas tanto ruido… no se te oye»): la VOZ manda siempre.
FX_GAIN = 0.35                       # todos los efectos mucho más bajos
DENSO = {"clic", "lapiz", "tic", "tic2"}
ult = {}
for k, t in sorted(json.load(open(os.path.join(BASE, "efectos.json"))), key=lambda e: e[1]):
    if k in DENSO and t - ult.get(k, -9) < (0.9 if k in ("tic", "tic2") else 0.22):
        continue                     # nada de ráfagas de clics
    if k not in DENSO and t - ult.get("_", -9) < 0.15:
        continue                     # no se amontonan dos golpes a la vez
    ult[k] = t
    if k not in DENSO:
        ult["_"] = t
    s, g = fx[k]
    mix.add_fx(s, t, g * FX_GAIN)
def ambiente(d):
    """Base documental: acordes graves muy suaves (Re menor) con pulso lento, sin percusión."""
    t = np.arange(int(d * SR)) / SR
    out = np.zeros_like(t)
    acordes = ((146.8, 174.6, 220.0), (116.5, 146.8, 174.6), (130.8, 164.8, 196.0), (110.0, 138.6, 164.8))
    blo = 8.0
    for i in range(int(d / blo) + 1):
        a0, a1 = i * blo, min(d, (i + 1) * blo + 1.5)
        m = (t >= a0) & (t < a1)
        tt = t[m] - a0
        env = np.minimum(1, tt / 2.0) * np.minimum(1, (a1 - a0 - tt) / 2.0)
        for f in acordes[i % 4]:
            out[m] += env * (0.5 * np.sin(2 * np.pi * f * tt) + 0.2 * np.sin(2 * np.pi * f * 2 * tt + 0.3)) / 3
    out += 0.25 * np.sin(2 * np.pi * 55 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * t)) ** 2
    return out / (np.max(np.abs(out)) or 1)
music = ambiente(dur)
vozv = mix.voice / (np.max(np.abs(mix.voice)) or 1) * 0.9
env = np.convolve(np.abs(vozv), np.ones(int(0.05 * SR)) / int(0.05 * SR), mode="same")
env = np.clip(env * 14, 0, 1)
env = np.convolve(env, np.ones(int(0.2 * SR)) / int(0.2 * SR), mode="same")
fxs = mix.fx * (1.0 - 0.55 * env)                 # los efectos se apartan cuando habla la voz
fxs = np.tanh(fxs * 2.5) / 2.5                     # limitador suave: ningún golpe por encima de la voz
mus = np.zeros_like(vozv); mus[:min(len(mus), len(music))] = music[:len(mus)]
mus = mus * 0.09 * (1.0 - 0.5 * env)
out = vozv + fxs + mus
out = out / (np.max(np.abs(out)) or 1) * 0.95
import sys
if "--stems" in sys.argv:
    for nom, sig in (("voz", vozv), ("fx", fxs), ("mus", mus)):
        for a, b in ((0, 1), (1, 3), (20, 25)):
            seg = sig[int(a * SR):int(b * SR)]
            print(nom, a, b, round(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9), 1))
tmp = os.path.join(BASE, "assets", "mezcla_bruta.wav")
audio.write_wav(tmp, out)
subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100,alimiter=limit=0.85:level=false",
                       "-ar", "44100", "-c:a", "pcm_s16le", os.path.join(BASE, "assets", "mezcla.wav")])
os.remove(tmp)
print("mezcla.wav", round(dur, 2), "s")

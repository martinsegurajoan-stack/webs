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
def ruido(n, seed, suav=1):
    x = np.random.default_rng(seed).standard_normal(n)
    return np.convolve(x, np.ones(suav) / suav, mode="same") if suav > 1 else x
def env(n, a=0.01, d=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a)
    return e * (np.exp(-t * d) if d else 1)
def boom_fx(d=2.5, f0=55):
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * (f0 - 20 * t / d) * t) + 0.4 * ruido(n, 3, 40) * 3) * np.exp(-t * 2.2) * np.minimum(1, t * 200)
def aparece_fx():
    n = int(1.8 * SR); t = np.arange(n) / SR
    sweep = np.sin(2 * np.pi * np.cumsum(200 + 1800 * (t / 1.8) ** 2) / SR) * (t / 1.8) ** 2 * 0.35
    b = np.zeros(n); bb = boom_fx(1.6, 48); k = int(0.45 * SR); b[k:k + len(bb)] += bb[: n - k]
    sh = ruido(n, 9) * 0.25 * np.exp(-np.abs(t - 0.5) * 6)
    return sweep * (t < 0.5) + b * 0.9 + sh
def tic_fx():
    n = int(0.08 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 90)
def paso_fx():
    n = int(0.6 * SR); t = np.arange(n) / SR
    return ruido(n, 4, 8) * np.sin(np.pi * t / 0.6) ** 2 * 0.6
def pomo_fx():
    out = np.zeros(int(0.9 * SR))
    for k in range(5):
        c = tic_fx()[: int(0.05 * SR)] * 0.6; i = int(k * 0.14 * SR); out[i:i + len(c)] += c
        m = np.sin(2 * np.pi * 380 * np.arange(int(0.06 * SR)) / SR) * np.exp(-np.arange(int(0.06 * SR)) / SR * 50) * 0.5; out[i:i + len(m)] += m
    return out
def sirena_fx(d=3.0):
    t = np.arange(int(d * SR)) / SR
    f = np.where((t * 1.4) % 1 < 0.5, 960, 770)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35 * np.minimum(1, t) * np.minimum(1, (d - t))
def creak_fx(d=1.2, f0=90):
    t = np.arange(int(d * SR)) / SR
    f = f0 + 40 * np.sin(2 * np.pi * 1.3 * t)
    pulsos = (np.sin(2 * np.pi * np.cumsum(f) / SR) > 0.95).astype(float)
    return np.convolve(pulsos, np.exp(-np.arange(200) / 30), mode="same") * 0.25 * np.sin(np.pi * t / d)
def monedas_fx():
    n = int(1.6 * SR); out = np.zeros(n); r = np.random.default_rng(8)
    for _ in range(40):
        i = int(r.uniform(0, 1.3) * SR); f = r.uniform(3000, 6500); tt = np.arange(1800) / SR
        out[i:i + 1800] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 200) * r.uniform(0.1, 0.35)
    return out
def olas_fx(d=3.0):
    t = np.arange(int(d * SR)) / SR
    return ruido(len(t), 5, 30) * 2 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.35 * t)) * np.minimum(1, t) * np.minimum(1, d - t)
def metal_fx():
    n = int(1.5 * SR); t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dcy) for f, dcy in ((420, 3), (1130, 4), (2210, 6), (3170, 8))) * 0.35 + ruido(n, 6) * np.exp(-t * 40) * 0.5
def cruce_fx():
    n = int(0.8 * SR); t = np.arange(n) / SR
    return ruido(n, 7, 6) * np.sin(np.pi * t / 0.8) ** 3 * 0.5 + np.sin(2 * np.pi * 60 * t) * np.exp(-t * 4) * 0.4
def apagado_fx(d=2.5):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(500 * np.exp(-t * 1.2) + 60) / SR) * np.exp(-t * 0.9) * 0.4
def grabado_fx(d=5.0):
    t = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * 880 * t) * 0.3 + np.sin(2 * np.pi * 1320 * t) * 0.2) * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * t)) * np.minimum(1, t / 1.5) * np.minimum(1, (d - t) / 1.5) * 0.3
def clic_fx(f=1.0):
    n = int(0.18 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1800 * f * t) * np.exp(-t * 120) + ruido(n, 3, 2) * np.exp(-t * 200) * 0.6 + np.sin(2 * np.pi * 120 * t) * np.exp(-t * 40) * 0.8)
def vibra_fx():
    t = np.arange(int(0.7 * SR)) / SR
    return np.sin(2 * np.pi * 160 * t) * (np.sin(2 * np.pi * 9 * t) > 0) * 0.6 * np.minimum(1, (0.7 - t) * 6)
def caja_fx():
    out = monedas_fx(); t = np.arange(len(out)) / SR
    return out + np.sin(2 * np.pi * 1318 * t) * np.exp(-t * 6) * 0.3 + np.sin(2 * np.pi * 1760 * t) * np.exp(-t * 6) * 0.2
def perdida_fx():
    t = np.arange(int(1.6 * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(220 * np.exp(-t * 1.2) + 50) / SR) * np.exp(-t * 1.4) * 0.8 + boom_fx(1.6, 45)[: len(t)] * 0.6
def coro_fx(d=1.6):
    out = np.zeros(int(d * SR)); r = np.random.default_rng(5)
    for _ in range(40):
        c = clic_fx(r.uniform(0.8, 1.3)) * r.uniform(0.2, 0.5); i = int(r.uniform(0, d - 0.2) * SR); out[i:i + len(c)] += c
    return out
def murmullo_fx(d=3.0):
    t = np.arange(int(d * SR)) / SR
    return ruido(len(t), 8, 60) * 4 * (0.6 + 0.4 * np.sin(2 * np.pi * 2.3 * t)) * np.minimum(1, t) * np.minimum(1, d - t)
def denegada_fx():
    t = np.arange(int(0.6 * SR)) / SR
    return np.sin(2 * np.pi * 300 * t) * ((t < 0.22) | (t > 0.32)) * 0.5
def apagon_fx():
    t = np.arange(int(0.5 * SR)) / SR
    return np.sin(2 * np.pi * (180 - 120 * t) * t) * np.exp(-t * 7) * 0.7
def latido_fx():
    out = np.zeros(int(1.6 * SR))
    for k0 in (0.0, 0.28, 0.8, 1.08):
        b = boom_fx(0.35, 48) * 0.8; i = int(k0 * SR); out[i:i + len(b)] += b[: len(out) - i]
    return out
fx = {"clic": (clic_fx(), 0.45), "clic2": (clic_fx(0.85) * 1.3, 0.6), "vibra": (vibra_fx(), 0.35), "caja": (caja_fx(), 0.55), "perdida": (perdida_fx(), 0.8),
      "whoosh": (audio.sfx_whoosh(0.6), 0.4), "coro": (coro_fx(), 0.6), "golpe": (boom_fx(2.0, 50), 0.8), "murmullo": (murmullo_fx(), 0.3),
      "rompe": (metal_fx(), 0.4), "denegada": (denegada_fx(), 0.45), "apagon": (apagon_fx(), 0.35), "latido": (latido_fx(), 0.9),
      "sello": (boom_fx(0.6, 90), 0.8), "final": (boom_fx(3.5, 36), 1.3)}
def bola_fx():
    """Golpe de raqueta: chasquido corto + cuerpo grave."""
    n = int(0.12 * SR); t = np.arange(n) / SR
    rng = np.random.default_rng(7); x = rng.standard_normal(n); x = x - np.convolve(x, np.ones(5) / 5, mode="same")
    return (x * np.exp(-t * 90) * 0.6 + np.sin(2 * np.pi * 210 * t) * np.exp(-t * 40) * 0.8)
def bote_fx():
    n = int(0.1 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 130 * t) * np.exp(-t * 55) * 0.7
def rebobina_fx(d=1.7):
    """Rebobinado: barrido rápido que baja de tono."""
    t = np.arange(int(d * SR)) / SR
    f = 1400 * np.exp(-t * 1.2) + 200
    ph = 2 * np.pi * np.cumsum(f) / SR
    rng = np.random.default_rng(2); nz = np.convolve(rng.standard_normal(len(t)), np.ones(8) / 8, mode="same")
    env = np.minimum(1, t * 8) * np.minimum(1, (d - t) * 4)
    return env * (0.3 * np.sin(ph) * (0.6 + 0.4 * np.sin(2 * np.pi * 22 * t)) + 0.5 * nz)
def rasca_fx(d=0.45):
    t = np.arange(int(d * SR)) / SR
    f = 900 * np.exp(-t * 6) + 120
    ph = 2 * np.pi * np.cumsum(f) / SR
    rng = np.random.default_rng(6); nz = np.convolve(rng.standard_normal(len(t)), np.ones(4) / 4, mode="same")
    return (0.6 * np.sign(np.sin(ph)) * 0.3 + 0.5 * nz) * np.minimum(1, t * 60) * np.exp(-t * 3)
def pop_fx():
    t = np.arange(int(0.12 * SR)) / SR
    return np.sin(2 * np.pi * (700 - 2500 * t) * t) * np.exp(-t * 35)
def ding_fx():
    t = np.arange(int(0.9 * SR)) / SR
    return (np.sin(2 * np.pi * 1760 * t) * 0.6 + np.sin(2 * np.pi * 2637 * t) * 0.3) * np.exp(-t * 5)
def tos_fx():
    rng = np.random.default_rng(11); out = np.zeros(int(0.9 * SR))
    for k0 in (0.0, 0.32):
        n = int(0.22 * SR); t = np.arange(n) / SR
        x = np.convolve(rng.standard_normal(n), np.ones(18) / 18, mode="same") * np.exp(-t * 14) * np.minimum(1, t * 200)
        i = int(k0 * SR); out[i:i + n] += x * 3
    return out
def cuenta_fx(d=1.0):
    out = np.zeros(int(d * SR)); t = np.arange(int(0.02 * SR)) / SR
    tic = np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 300)
    for k in range(int(d / 0.06)):
        i = int(k * 0.06 * SR); out[i:i + len(tic)] += tic * (1 - k * 0.06 / d)
    return out
def sirena_fx(d=2.4):
    t = np.arange(int(d * SR)) / SR
    f = np.where((t * 1.6) % 1 < 0.5, 660, 520)
    return 0.4 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t * 4) * np.minimum(1, (d - t) * 4)
def alarma_fx(d=1.4):
    t = np.arange(int(d * SR)) / SR
    gate = ((t * 8) % 1 < 0.5).astype(float)
    return gate * (0.5 * np.sin(2 * np.pi * 1900 * t) + 0.3 * np.sin(2 * np.pi * 2850 * t)) * np.minimum(1, (d - t) * 6)
fx.update({"alarma": (alarma_fx(), 0.45)})
fx.update({"tos": (tos_fx(), 0.8), "cuenta": (cuenta_fx(), 0.5), "tic": (cuenta_fx(0.5), 0.5), "sirena": (sirena_fx(), 0.35)})
fx.update({"rasca": (rasca_fx(), 0.9), "pop": (pop_fx(), 0.6), "ding": (ding_fx(), 0.6), "riser": (riser(1.0), 0.6)})
fx.update({"bola": (bola_fx(), 0.9), "bote": (bote_fx(), 0.5), "rebobina": (rebobina_fx(), 0.9)})
# --- MEZCLA LIMPIA (usuario, 02-11-2026: «no hagas tanto ruido… no se te oye»): la VOZ manda siempre.
FX_GAIN = 0.32                       # todos los efectos mucho más bajos
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
    if k == "final":
        continue                     # sin «boom» de cierre (usuario, 08-11-2026)
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
# murmullo del público: sube y baja con la gente que queda en la grada
amb = json.load(open(os.path.join(BASE, "ambiente.json")))
_rng = np.random.default_rng(9); gente = _rng.standard_normal(int(dur * SR))
for _ in range(3):
    gente = np.convolve(gente, np.ones(40) / 40, mode="same")
gente = gente / (np.max(np.abs(gente)) or 1)
gente *= np.interp(np.arange(len(gente)) / SR, [a for a, b in amb], [b for a, b in amb])
mix.fx[:len(gente)] += gente[:len(mix.fx)] * 0.1
T = json.load(open(os.path.join(BASE, "tiempos.json")))
F_ = [f["ini"] for f in T["frases"]]
tt = np.arange(len(music)) / SR
FIN = [p["ini"] for p in T["palabras"]][-1] + 0.75            # golpe final: corte a negro
pulso = np.sin(2 * np.pi * 50 * tt) * np.exp(-((tt * 1.6) % 1.0) * 8)          # latido grave (96 lpm) en el caos
caja = np.random.default_rng(1).standard_normal(len(tt)); caja = np.convolve(caja, np.ones(4) / 4, mode="same") * np.exp(-((tt * 1.6 + 0.5) % 1.0) * 30)
tension = np.interp(tt, [0, F_[1], F_[4], F_[6], F_[8], F_[9], F_[10], F_[12], dur], [0.3, 0.25, 0.35, 0.6, 0.85, 1.0, 0.3, 0.35, 0.3])
alto = np.sin(2 * np.pi * 587.3 * tt) * 0.2 + np.sin(2 * np.pi * 880 * tt) * 0.12
alto *= np.interp(tt, [0, 2, F_[6], F_[10], dur], [0.3, 0.4, 0.4, 0.2, 0.3])
base = music * np.interp(tt, [0, 3, dur], [0.8, 1, 1])
# sin ruido tipo radio (nada de caja de ruido blanco) y la música baja SUAVE al final (usuario, 08-11-2026)
def fiesta(d, bpm=124.0):
    """Ritmo de fiesta amortiguado (como desde otra habitación): bombo, charles a contratiempo, bajo y acordes."""
    n = int(d * SR); t = np.arange(n) / SR; b = 60.0 / bpm
    out = np.zeros(n)
    kick_t = np.arange(int(0.25 * SR)) / SR
    kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-kick_t * 30)) * kick_t) * np.exp(-kick_t * 9)
    rng = np.random.default_rng(4); hat = rng.standard_normal(int(0.06 * SR)); hat = (hat - np.convolve(hat, np.ones(3) / 3, "same")) * np.exp(-np.arange(len(hat)) / SR * 70)
    k = 0
    while k * b < d:
        i = int(k * b * SR); out[i:i + len(kick)] += kick[:n - i] * 0.9
        j = int((k + 0.5) * b * SR); out[j:j + len(hat)] += hat[:max(0, n - j)] * 0.25
        k += 1
    notas = [55.0, 55.0, 65.4, 49.0]
    for c in range(int(d / (4 * b)) + 1):
        f = notas[c % 4]
        for q in range(8):
            a0 = (c * 4 + q * 0.5 + 0.25) * b
            i = int(a0 * SR); m = min(n, i + int(0.2 * SR))
            if i >= n: break
            tt_ = t[i:m] - a0
            out[i:m] += 0.35 * np.sin(2 * np.pi * f * tt_) * np.exp(-tt_ * 8)
    acordes = ((220.0, 261.6, 329.6), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (196.0, 246.9, 293.7))
    for c in range(int(d / (4 * b)) + 1):
        for q in (0.5, 1.5, 2.5, 3.5):
            a0 = (c * 4 + q) * b; i = int(a0 * SR); m = min(n, i + int(0.18 * SR))
            if i >= n: break
            tt_ = t[i:m] - a0
            for f in acordes[c % 4]:
                out[i:m] += 0.08 * np.sin(2 * np.pi * f * tt_) * np.exp(-tt_ * 14)
    out = np.convolve(out, np.ones(12) / 12, mode="same")          # amortiguado
    return out / (np.max(np.abs(out)) or 1)
music = ambiente(dur) * np.interp(tt, [0, 1.0, dur - 2.5, dur], [0.85, 1, 1, 0.15])
music = music / (np.max(np.abs(music)) or 1)
vozv = mix.voice / (np.max(np.abs(mix.voice)) or 1) * 0.9
env = np.convolve(np.abs(vozv), np.ones(int(0.05 * SR)) / int(0.05 * SR), mode="same")
env = np.clip(env * 14, 0, 1)
env = np.convolve(env, np.ones(int(0.2 * SR)) / int(0.2 * SR), mode="same")
fxs = mix.fx * (1.0 - 0.55 * env)                 # los efectos se apartan cuando habla la voz
fxs = np.tanh(fxs * 2.5) / 2.5                     # limitador suave: ningún golpe por encima de la voz
mus = np.zeros_like(vozv); mus[:min(len(mus), len(music))] = music[:len(mus)]
mus = mus * 0.13 * (1.0 - 0.55 * env)
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

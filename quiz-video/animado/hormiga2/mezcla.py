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
fx = {"sube": (sube(), 0.3), "sube2": (sube(1.2, 420, 1100), 0.32), "boing": (boing(), 0.45), "timbre": (timbre(), 0.13), "suave": (transicion(), 0.16), "brillo": (brillo(), 0.2), "whoosh": (audio.sfx_whoosh(0.6), 0.35), "pop": (audio.sfx_pop(), 0.35), "clic": (audio.sfx_tick(True), 0.6),
      "golpe": (sfx_golpe(1.0), 0.55), "portazo": (sfx_golpe(1.5), 0.8)}
for k, t in json.load(open(os.path.join(BASE, "efectos.json"))):
    s, g = fx[k]
    mix.add_fx(s, t, g)
music = audio.music(dur, style="pop", bpm=100, seed=21)
out = mix.render(music, music_gain=0.12)
tmp = os.path.join(BASE, "assets", "mezcla_bruta.wav")
audio.write_wav(tmp, out)
subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                       "-ar", "44100", os.path.join(BASE, "assets", "mezcla.wav")])
os.remove(tmp)
print("mezcla.wav", round(dur, 2), "s")

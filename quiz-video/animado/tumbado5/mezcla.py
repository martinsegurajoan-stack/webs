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
fx = {"whoosh": (audio.sfx_whoosh(0.6), 0.35), "pop": (audio.sfx_pop(), 0.35), "clic": (audio.sfx_tick(True), 0.6),
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

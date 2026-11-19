#!/usr/bin/env python3
"""Censura: sustituye en assets/mezcla.wav los tramos de censura.json por un pitido de 1 kHz (insultos)."""
import json, os, subprocess, numpy as np, wave
B = os.path.dirname(os.path.abspath(__file__)); f = os.path.join(B, "assets", "mezcla.wav")
w = wave.open(f); sr, ch, sw, n = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
a = np.frombuffer(w.readframes(n), dtype=np.int16).reshape(-1, ch).astype(np.float32); w.close()
for t0, t1 in json.load(open(os.path.join(B, "censura.json"))):
    i0, i1 = int(t0 * sr), int(t1 * sr); m = i1 - i0
    tt = np.arange(m) / sr
    env = np.minimum(1, np.minimum(tt, tt[::-1]) / 0.008)
    lvl = 0.30 * 32767
    for c in range(ch):
        a[i0:i1, c] = np.sin(2 * np.pi * 1000 * tt) * env * lvl
o = wave.open(f, "w"); o.setnchannels(ch); o.setsampwidth(sw); o.setframerate(sr)
o.writeframes(np.clip(a, -32767, 32767).astype(np.int16).tobytes()); o.close()
print("pitidos:", len(json.load(open(os.path.join(B, "censura.json")))))

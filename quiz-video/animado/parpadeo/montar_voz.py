#!/usr/bin/env python3
"""Une las frases de voz (voz/lN.wav) con 0,25 s entre ellas → assets/voz.wav + tiempos.json
(inicio/fin de cada frase y de cada palabra, para pegar la animación a la voz)."""
import json, os, subprocess, sys
import numpy as np
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "..", ".."))
from quizvideo.personalidad import align_words   # reparte palabras usando las pausas reales
from quizvideo import audio
SR = audio.SR
GAP = 0.14
EXTRA = {1: 0.25, 2: 0.3, 10: 0.2, 13: 0.2, 14: 0.45, 15: 0.3, 19: 0.3, 20: 0.25}

def load(p):
    raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"])
    s = np.frombuffer(raw, np.float32).astype(np.float64)
    idx = np.where(np.abs(s) > 0.01)[0]
    return s[max(0, idx[0] - int(0.02 * SR)): idx[-1] + int(0.06 * SR)]

lines = [l.strip() for l in open(os.path.join(BASE, "guion.txt"), encoding="utf-8") if l.strip()]
INICIO = 0.5                                   # la voz empieza medio segundo más tarde (regla del usuario, todos los vídeos)
out, t, frases, palabras = [np.zeros(int(INICIO * SR))], INICIO, [], []
for i, txt in enumerate(lines, 1):
    s = load(os.path.join(BASE, "voz", f"l{i}.wav"))
    d = len(s) / SR
    ws, times = align_words(txt, s, d)
    frases.append({"n": i, "texto": txt, "ini": round(t, 3), "fin": round(t + d, 3)})
    for w, (a, b) in zip(ws, times):
        palabras.append({"w": w, "ini": round(t + a, 3), "fin": round(t + b, 3), "frase": i})
    out.append(s)
    t += d
    if i < len(lines):
        g = GAP + EXTRA.get(i, 0.0)
        out.append(np.zeros(int(g * SR))); t += g
COLA = 1.4
out.append(np.zeros(int(COLA * SR))); t += COLA
sig = np.concatenate(out)
sig = sig / (np.max(np.abs(sig)) or 1) * 0.9
os.makedirs(os.path.join(BASE, "assets"), exist_ok=True)
audio.write_wav(os.path.join(BASE, "assets", "voz.wav"), sig)
json.dump({"duracion": round(len(sig) / SR, 3), "frases": frases, "palabras": palabras},
          open(os.path.join(BASE, "tiempos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("duración", round(len(sig) / SR, 2))

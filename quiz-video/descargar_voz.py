#!/usr/bin/env python3
"""Descarga audios de ElevenLabs a la caché de la voz QUIZ.

Entrada: archivo TSV con líneas "<texto EXACTO enviado a ElevenLabs>\t<url del mp3>"
(el texto es el campo "texto" de `generar.py --frases-pendientes`, etiquetas incluidas).
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quizvideo.tts_eleven import cache_path  # noqa: E402

for line in open(sys.argv[1], encoding="utf-8"):
    if not line.strip():
        continue
    prompt, url = line.rstrip("\n").split("\t")
    dest = cache_path(prompt)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    subprocess.check_call(["curl", "-sS", "--fail", "--max-time", "60", "-o", dest, url])
    dur = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "default=nw=1:nk=1", dest]).decode().strip()
    print(f"OK {os.path.basename(dest)} {float(dur):.1f}s  {prompt}")

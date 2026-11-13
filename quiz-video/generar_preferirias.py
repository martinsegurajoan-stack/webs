#!/usr/bin/env python3
"""Genera un vídeo «¿QUÉ PREFERIRÍAS?» + sus 2 portadas.

  python3 generar_evita.py quizzes/preferirias_01.json --frases-pendientes
  python3 generar_evita.py quizzes/preferirias_01.json --preview 0.5,6,10 -o /tmp/prev
  python3 generar_evita.py quizzes/preferirias_01.json
"""
import argparse
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from quizvideo import preferirias as evita  # noqa: E402
from quizvideo.tts_eleven import ElevenVoice  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("contenido")
    ap.add_argument("-o", "--salida")
    ap.add_argument("--frases-pendientes", action="store_true")
    ap.add_argument("--preview")
    ap.add_argument("--solo-portada", action="store_true")
    a = ap.parse_args()
    c = json.load(open(a.contenido, encoding="utf-8"))
    out = a.salida or os.path.join(BASE, "salida", c["video"] + ".mp4")
    voice = ElevenVoice()
    voice.configure(style=c.get("estilo_voz", ""), tempo=float(c.get("tempo", 1.3)))
    if a.frases_pendientes:
        _, _, total = evita.build_timeline(c, voice)
        print(f"Duración estimada: {total:.1f}s", file=sys.stderr)
        print(voice.pending_json())
        return
    if a.preview:
        total, outs = evita.render_video(c, voice, out, preview=[float(x) for x in a.preview.split(",")])
        print(f"Duración estimada: {total:.1f}s")
        print("\n".join(outs))
        return
    if a.solo_portada:
        print(*evita.portada(c, {"c": c, "scenes": []}, os.path.join(BASE, "portadas")))
        return
    evita.build_timeline(c, voice)
    if voice.missing:
        raise SystemExit("Faltan audios de voz. Ejecuta con --frases-pendientes.")
    if os.path.exists(out):
        raise SystemExit(f"Ya existe {out}: no lo sobrescribo.")
    evita.render_video(c, voice, out)
    j = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                                            "stream=codec_type,width,height,codec_name:format=duration", "-of", "json", out]))
    v = [s for s in j["streams"] if s["codec_type"] == "video"]
    au = [s for s in j["streams"] if s["codec_type"] == "audio"]
    ok = v and au and v[0]["width"] == 1080 and v[0]["height"] == 1920
    print(("OK" if ok else "ERROR") + f": {out} · {float(j['format']['duration']):.1f}s · {os.path.getsize(out) / 1e6:.1f} MB")
    if ok:
        print(*evita.portada(c, {"c": c, "scenes": []}, os.path.join(BASE, "portadas")))


if __name__ == "__main__":
    main()

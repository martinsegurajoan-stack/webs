#!/usr/bin/env python3
"""Genera un vídeo del formato NIVELES (cada ronda, una mecánica distinta) + sus 2 portadas.

  python3 generar_niveles.py quizzes/niveles_01.json --frases-pendientes
  python3 generar_niveles.py quizzes/niveles_01.json --preview 1,5,12 -o /tmp/prev
  python3 generar_niveles.py quizzes/niveles_01.json
"""
import argparse
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from quizvideo import niveles, themes  # noqa: E402
from quizvideo.tts_eleven import ElevenVoice  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("contenido")
    ap.add_argument("-o", "--salida")
    ap.add_argument("--frases-pendientes", action="store_true")
    ap.add_argument("--preview", help="segundos separados por comas → PNGs (sin gastar créditos)")
    ap.add_argument("--solo-portada", action="store_true")
    a = ap.parse_args()
    c = json.load(open(a.contenido, encoding="utf-8"))
    out = a.salida or os.path.join(BASE, "salida", c["video"] + ".mp4")
    voice = ElevenVoice()
    voice.configure(style="", tempo=c.get("tempo", 1.18))
    tono = themes.elegir_tono(c["video"], tuple(c["rango_tono"]) if c.get("rango_tono") else None)  # tono del fondo oscuro del gancho y del cierre
    state = {"c": c, "tono": tono}

    if a.frases_pendientes:
        niveles.build_timeline(c, voice)
        print(voice.pending_json())
        return
    if a.preview:
        secs = [float(x) for x in a.preview.split(",")]
        total, outs = niveles.render_video(c, voice, out, tono, preview=secs)
        print(f"Duración estimada: {total:.1f}s")
        print("\n".join(outs))
        return
    if a.solo_portada:
        print(*niveles.portada(c, state, os.path.join(BASE, "portadas")))
        return
    niveles.build_timeline(c, voice)
    if voice.missing:
        raise SystemExit("Faltan audios de voz. Ejecuta con --frases-pendientes.")
    if os.path.exists(out):
        raise SystemExit(f"Ya existe {out}: no lo sobrescribo (bórralo o usa -o).")
    niveles.render_video(c, voice, out, tono)
    j = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                                            "stream=codec_type,codec_name,width,height:format=duration",
                                            "-of", "json", out]))
    v = [s for s in j["streams"] if s["codec_type"] == "video"]
    au = [s for s in j["streams"] if s["codec_type"] == "audio"]
    ok = v and au and v[0]["width"] == 1080 and v[0]["height"] == 1920
    print(("OK" if ok else "ERROR") + f": {out} · {v[0]['width']}x{v[0]['height']} · audio "
          f"{au[0]['codec_name'] if au else 'NO'} · {float(j['format']['duration']):.1f}s · "
          f"{os.path.getsize(out) / 1e6:.1f} MB")
    if ok:
        themes.registrar_tono(c["video"], tono)
        print(*niveles.portada(c, state, os.path.join(BASE, "portadas")))


if __name__ == "__main__":
    main()

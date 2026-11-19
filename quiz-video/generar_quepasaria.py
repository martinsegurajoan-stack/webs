#!/usr/bin/env python3
"""Vídeo del formato «¿QUÉ PASARÍA SI…?» (narración + animación por código) y sus 2 portadas.

  python3 generar_quepasaria.py quizzes/quepasaria_01.json --faltan
  python3 generar_quepasaria.py quizzes/quepasaria_01.json --preview 1,10,30 -o /tmp/p
  python3 generar_quepasaria.py quizzes/quepasaria_01.json
"""
import argparse
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from quizvideo import quepasaria, themes  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("contenido")
    ap.add_argument("-o", "--salida")
    ap.add_argument("--faltan", action="store_true", help="frases de voz que faltan (archivo + texto)")
    ap.add_argument("--preview", help="segundos separados por comas → PNGs (sin gastar créditos)")
    ap.add_argument("--sin-voz", action="store_true")
    ap.add_argument("--solo-portada", action="store_true")
    a = ap.parse_args()
    c = json.load(open(a.contenido, encoding="utf-8"))
    out = a.salida or os.path.join(BASE, "salida", c["video"] + ".mp4")
    tono = themes.elegir_tono(c["video"], tuple(c["rango_tono"]) if c.get("rango_tono") else None)
    if a.faltan:
        print(json.dumps(quepasaria.faltan(c), ensure_ascii=False, indent=2))
        return
    if a.preview:
        total, outs = quepasaria.render(c, out, tono, preview=[float(x) for x in a.preview.split(",")],
                                        sin_voz=a.sin_voz)
        print(f"Duración: {total:.1f}s")
        print("\n".join(outs))
        return
    if a.solo_portada:
        print(*quepasaria.portada(c, tono, os.path.join(BASE, "portadas")))
        return
    if quepasaria.faltan(c):
        raise SystemExit("Faltan audios de voz. Ejecuta con --faltan.")
    quepasaria.render(c, out, tono)
    j = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                                            "stream=codec_type,codec_name,width,height:format=duration",
                                            "-of", "json", out]))
    v = [s for s in j["streams"] if s["codec_type"] == "video"]
    au = [s for s in j["streams"] if s["codec_type"] == "audio"]
    ok = v and au and v[0]["width"] == 1080 and v[0]["height"] == 1920
    print(("OK" if ok else "ERROR") + f": {out} · audio {au[0]['codec_name'] if au else 'NO'} · "
          f"{float(j['format']['duration']):.1f}s · {os.path.getsize(out) / 1e6:.1f} MB")
    if ok:
        themes.registrar_tono(c["video"], tono)
        print(*quepasaria.portada(c, tono, os.path.join(BASE, "portadas")))


if __name__ == "__main__":
    main()

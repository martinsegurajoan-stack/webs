#!/usr/bin/env python3
"""Genera el vídeo de TEST DE PERSONALIDAD de Hora del Quiz.

  python3 generar_personalidad.py quiz_personalidad/contenido.json --frases-pendientes
  python3 generar_personalidad.py quiz_personalidad/contenido.json --preview 1,8,20 -o /tmp/prev
  python3 generar_personalidad.py quiz_personalidad/contenido.json
"""
import argparse
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from quizvideo import personalidad, themes  # noqa: E402
from quizvideo.tts_eleven import ElevenVoice  # noqa: E402

ESTILO_VOZ = "[playful and a little cheeky]"  # natural, cercana, divertida y algo provocadora


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("contenido")
    ap.add_argument("-o", "--salida")
    ap.add_argument("--frases-pendientes", action="store_true")
    ap.add_argument("--preview", help="segundos separados por comas → PNGs (sin gastar créditos)")
    a = ap.parse_args()
    c = json.load(open(a.contenido, encoding="utf-8"))
    carpeta = os.path.dirname(os.path.abspath(a.contenido))
    out = a.salida or os.path.join(carpeta, c["video"] + ".mp4")

    voice = ElevenVoice()
    voice.configure(style=ESTILO_VOZ, tempo=float(c.get("tempo", 1.0)))  # 1.0 = sin acelerar la voz
    tono = personalidad.TONO
    if c.get("rango_tono"):  # color de fondo nuevo en cada test
        tono = themes.elegir_tono(c["video"], tuple(c["rango_tono"]))
        c["tono_fondo"] = tono

    if a.frases_pendientes:
        personalidad.build_timeline(c, voice)
        print(voice.pending_json())
        return
    if a.preview:
        secs = [float(x) for x in a.preview.split(",")]
        total, outs = personalidad.render_video(c, voice, out, preview=secs)
        print(f"Duración estimada: {total:.1f}s")
        print("\n".join(outs))
        return
    personalidad.build_timeline(c, voice)
    if voice.missing:
        raise SystemExit("Faltan audios de voz. Ejecuta con --frases-pendientes.")
    if os.path.exists(out):
        raise SystemExit(f"Ya existe {out}: no lo sobrescribo (bórralo o usa -o).")
    total, _ = personalidad.render_video(c, voice, out)
    info = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                                    "stream=codec_type,codec_name,width,height:format=duration",
                                    "-of", "json", out]).decode()
    j = json.loads(info)
    v = [s for s in j["streams"] if s["codec_type"] == "video"]
    au = [s for s in j["streams"] if s["codec_type"] == "audio"]
    dur = float(j["format"]["duration"])
    ok = v and au and v[0]["width"] == 1080 and v[0]["height"] == 1920
    if ok:
        themes.registrar_tono(c["video"], tono)
    print(("OK" if ok else "ERROR") + f": {out} · {v[0]['codec_name']} {v[0]['width']}x{v[0]['height']} · "
          f"audio {au[0]['codec_name'] if au else 'NO'} · duración {dur:.1f}s · "
          f"{os.path.getsize(out) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()

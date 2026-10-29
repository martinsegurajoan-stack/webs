#!/usr/bin/env python3
"""Genera un vídeo de quiz vertical (1080x1920) en MP4.

Ejemplo:
  python3 generar.py quizzes/geografia_espana.json --tema-color verde --voz kokoro:ef_dora
"""

import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quizvideo import render, themes, tts  # noqa: E402
from quizvideo.validate import load_quiz  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Generador de vídeos de quiz para TikTok")
    ap.add_argument("quiz", help="Archivo JSON con el quiz")
    ap.add_argument("-o", "--salida", help="Ruta del MP4 (por defecto salida/<nombre>.mp4)")
    ap.add_argument("--tema-color", default="verde", help=f"Paleta: {', '.join(themes.THEMES)}")
    ap.add_argument("--voz", default="kokoro:ef_dora", help="'ninguna' o 'kokoro:<voz>' (p. ej. kokoro:ef_dora)")
    ap.add_argument("--velocidad-voz", type=float, default=1.15)
    ap.add_argument("--preguntas", type=int, help="Usar solo las N primeras preguntas")
    ap.add_argument("--duracion-max", type=float, default=None,
                    help="Segundos máximos: si se pasa, se quitan preguntas del final")
    ap.add_argument("--cuenta-atras", type=int, default=5, help="Segundos por pregunta")
    ap.add_argument("--sin-musica", action="store_true")
    ap.add_argument("--preview", type=float, help="Guardar solo el fotograma de este segundo como PNG")
    args = ap.parse_args()

    quiz = load_quiz(args.quiz)
    if args.preguntas:
        quiz["preguntas"] = quiz["preguntas"][: args.preguntas]
    theme = themes.get_theme(args.tema_color)
    voice = tts.get_voice(args.voz, args.velocidad_voz)

    # Ajusta el número de preguntas a la duración máxima
    while True:
        _, _, total = render.build_timeline(quiz, voice, args.cuenta_atras)
        if args.duracion_max is None:
            if not 30 <= total <= 62:
                print(f"AVISO: duración estimada {total:.1f}s (objetivo 30-60s).")
            break
        if total <= args.duracion_max or len(quiz["preguntas"]) == 1:
            break
        quiz["preguntas"] = quiz["preguntas"][:-1]
        print(f"Duración {total:.1f}s > {args.duracion_max}s: uso {len(quiz['preguntas'])} preguntas.")

    base = os.path.splitext(os.path.basename(args.quiz))[0]
    out = args.salida or os.path.join(os.path.dirname(os.path.abspath(__file__)), "salida",
                                       base + (".png" if args.preview is not None else ".mp4"))
    print(f"Quiz: {quiz['tema']} · {len(quiz['preguntas'])} preguntas · voz: {voice.name} · paleta: {args.tema_color}")
    t0 = time.time()
    total = render.render_video(quiz, theme, voice, out, args.cuenta_atras,
                                music_on=not args.sin_musica, preview=args.preview)
    if args.preview is not None:
        print(f"Fotograma guardado en {out}")
        return

    # Verificación del archivo final con ffprobe
    info = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate",
         "-of", "json", out]))
    streams = {s["codec_type"]: s for s in info["streams"]}
    v, a = streams.get("video"), streams.get("audio")
    ok = v and a and v["width"] == 1080 and v["height"] == 1920
    print(f"\n{'OK' if ok else 'ERROR'}: {out}")
    print(f"  vídeo {v['codec_name']} {v['width']}x{v['height']} @ {v['r_frame_rate']} · "
          f"audio {a['codec_name'] if a else 'ninguno'}")
    print(f"  duración {float(info['format']['duration']):.1f}s · {int(info['format']['size']) / 1e6:.1f} MB · "
          f"renderizado en {time.time() - t0:.0f}s")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()

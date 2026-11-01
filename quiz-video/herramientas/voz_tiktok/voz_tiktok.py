#!/usr/bin/env python3
"""Voces en off para TikTok con ElevenLabs (voz «Juanjo Viral – Energetic & Punchy»).

Uso:
  python3 voz_tiktok.py                  → pega el guion y termina con una línea vacía (o Ctrl+D)
  python3 voz_tiktok.py guion.txt        → lee el guion de un archivo
  python3 voz_tiktok.py guion.txt -n pelo → nombre para los archivos (si no, «voz»)

Genera en la carpeta «audios»:
  <nombre>_<fecha-hora>.mp3   (el audio)
  <nombre>_<fecha-hora>.srt   (subtítulos PALABRA A PALABRA con los tiempos que devuelve la API)

La API key se lee de un archivo .env (ELEVENLABS_API_KEY=...) junto a este script. No la escribas en el código.
"""
import argparse
import base64
import datetime as dt
import os
import re
import sys

import requests
from dotenv import load_dotenv

VOICE_ID = "30jLfQdV8RTduXvosh02"          # Juanjo Viral – Energetic & Punchy
MODELOS = ["eleven_v4", "eleven_multilingual_v2"]   # si el primero da error, prueba el segundo
URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128"
AQUI = os.path.dirname(os.path.abspath(__file__))


def leer_guion(ruta):
    if ruta:
        with open(ruta, encoding="utf-8") as f:
            return f.read().strip()
    print("Pega tu guion. Para terminar, deja una línea vacía (o pulsa Ctrl+D):")
    lineas = []
    try:
        while True:
            linea = input()
            if not linea.strip():
                break
            lineas.append(linea)
    except EOFError:
        pass
    return "\n".join(lineas).strip()


def generar(texto, api_key):
    ultimo_error = None
    for modelo in MODELOS:
        r = requests.post(URL.format(voice=VOICE_ID),
                          headers={"xi-api-key": api_key, "Content-Type": "application/json"},
                          json={"text": texto, "model_id": modelo, "language_code": "es"}, timeout=300)
        if r.status_code == 200:
            print(f"Generado con {modelo}.")
            return r.json()
        ultimo_error = f"{modelo}: {r.status_code} {r.text[:300]}"
        print(f"Error con {modelo} → pruebo el siguiente modelo. ({ultimo_error})")
    sys.exit(f"No se pudo generar el audio. Último error: {ultimo_error}")


def palabras(alineacion):
    """Convierte la alineación por caracteres de la API en palabras con inicio y fin."""
    chars = alineacion["characters"]
    ini = alineacion["character_start_times_seconds"]
    fin = alineacion["character_end_times_seconds"]
    out, actual, t0, t1 = [], "", None, None
    for c, a, b in zip(chars, ini, fin):
        if c.isspace():
            if actual:
                out.append((actual, t0, t1))
            actual, t0 = "", None
            continue
        if t0 is None:
            t0 = a
        actual += c
        t1 = b
    if actual:
        out.append((actual, t0, t1))
    # quita etiquetas de emoción tipo [excited] si las hubiera
    return [(w, a, b) for w, a, b in out if not re.fullmatch(r"\[[^\]]*\]", w)]


def hms(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main():
    ap = argparse.ArgumentParser(description="Voz en off para TikTok con ElevenLabs")
    ap.add_argument("guion", nargs="?", help="archivo .txt con el guion (opcional)")
    ap.add_argument("-n", "--nombre", default="voz", help="nombre base de los archivos")
    args = ap.parse_args()

    load_dotenv(os.path.join(AQUI, ".env"))
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        sys.exit("Falta ELEVENLABS_API_KEY. Crea un archivo .env junto al script con: ELEVENLABS_API_KEY=tu_clave")

    texto = leer_guion(args.guion)
    if not texto:
        sys.exit("El guion está vacío.")

    datos = generar(texto, api_key)
    carpeta = os.path.join(AQUI, "audios")
    os.makedirs(carpeta, exist_ok=True)
    nombre = re.sub(r"[^\w-]+", "_", args.nombre).strip("_") or "voz"
    base = os.path.join(carpeta, f"{nombre}_{dt.datetime.now():%Y-%m-%d_%H-%M-%S}")

    with open(base + ".mp3", "wb") as f:
        f.write(base64.b64decode(datos["audio_base64"]))
    print("Audio:", base + ".mp3")

    al = datos.get("normalized_alignment") or datos.get("alignment")
    if al:
        with open(base + ".srt", "w", encoding="utf-8") as f:
            for i, (w, a, b) in enumerate(palabras(al), 1):
                f.write(f"{i}\n{hms(a)} --> {hms(max(b, a + 0.05))}\n{w}\n\n")
        print("Subtítulos:", base + ".srt")
    else:
        print("La API no devolvió tiempos: no se ha creado el .srt.")


if __name__ == "__main__":
    main()

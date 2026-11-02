#!/bin/bash
# Renderiza el vídeo final CON subtítulos (lo único que se entrega)
set -e
cd "$(dirname "$0")"
python3 montar_voz.py
python3 gen.py
python3 mezcla.py
npx -y hyperframes render -o salida/video-FINAL.mp4 --quality delivery --quiet
echo HECHO

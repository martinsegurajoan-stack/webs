#!/bin/bash
# Renderiza las dos versiones (con y sin subtítulos)
set -e
cd "$(dirname "$0")"
python3 gen.py --sin-subs
npx -y hyperframes render -o salida/video-SIN-SUBTITULOS.mp4 --quality delivery --quiet
python3 gen.py
npx -y hyperframes render -o salida/video-FINAL.mp4 --quality delivery --quiet
echo HECHO

# Hormiga v2 (vídeo 9 rehecho, estilo Netflix)
Estado: voz v2 HECHA (Juanjo, 1.323 créditos, sin susurros) → voz_el/narrador.mp3, voz/lN.wav, tiempos.json (80,4 s).
Escenas nuevas en `escenas2.py` (casa de verdad: dormitorio, pasillo, comedor, cocina, salón), sin desenfoques.
Pasos: python3 gen.py → snapshots → python3 mezcla.py → npx -y hyperframes render -o salida/video-FINAL.mp4 --quality delivery
→ node miniatura/hacer.js → descripciones/animado_hormiga2.md → commit/push → enviar MP4 + miniatura + textos.

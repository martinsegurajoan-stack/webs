# Cómo rehacer el vídeo «¿Qué pasaría si no te cortas el pelo en 5 años?»

Carpeta: `quiz-video/animado/pelo5/`. Todo se rehace solo si cambias una frase o la voz.

## 1 · Herramientas (una vez)
```bash
node --version            # 22 o superior
npx hyperframes skills
npx hyperframes browser ensure
pip install kokoro-onnx soundfile   # voz gratis
```

## 2 · Voz gratis (una frase por línea en guion.txt)
```bash
i=0; while IFS= read -r l; do i=$((i+1)); printf '%s\n' "$l" > voz/l$i.txt; npx hyperframes tts voz/l$i.txt --voice em_alex --lang es -o voz/l$i.wav; done < guion.txt
python3 montar_voz.py     # une las frases (0,25 s entre ellas + pausas extra tras «cien mil» y «sopa») → assets/voz.wav + tiempos.json (cada palabra)
```

## 3 · Animación + sonido
```bash
python3 gen.py            # index.html con subtítulos (todo pegado a la voz con P("palabra", n))
python3 mezcla.py         # voz + efectos + música baja, −14 LUFS → assets/mezcla.wav
npx hyperframes check
npx hyperframes render -o salida/video-FINAL.mp4 --quality delivery
# o todo de una vez: bash render_todo.sh   (solo se entrega la versión CON subtítulos)
```

## Notas
- Si cambias el guion, revisa en `gen.py` las llamadas `P("palabra", n)` (n = qué vez se dice esa palabra).
- Whisper large-v3 no se pudo usar (Hugging Face bloqueado en la sesión): los tiempos de cada palabra salen de
  generar la voz frase a frase + las pausas reales del audio (`align_words`).
- Estilo: ilustración plana con degradados sobre fondo lila propio con vida (rayos que giran, manchas de luz,
  garabatos de pelo flotando, tono cálido que respira); un solo mundo 2D con cámara que viaja entre 7 estaciones.
- Personaje: HOMBRE; el pelo crece por etapas y la barba (castaño rojizo, con contorno, distinta del pelo) también.
- Cámara: deriva suave continua (#camA), golpes de zoom en palabras fuertes y giros de ángulo en viajes,
  portazo, «dejar de crecer», etc. (#camB). Todo cuadra en el último fotograma para el bucle.
- Subtítulos: arriba, 2 líneas, palabra dicha en blanco, palabras clave con recuadro azul de selección.
- Sopa: el mechón derecho cuelga desde la cabeza y entra en el plato (salpica, ondas, pelos flotando).

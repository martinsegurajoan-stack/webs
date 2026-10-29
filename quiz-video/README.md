# Generador de vídeos de quiz para TikTok

Crea vídeos verticales 1080x1920 (MP4 H.264 + AAC, 30 fps) listos para TikTok, Reels y Shorts:
intro, preguntas con 4 opciones (A–D), cuenta atrás animada con tic-tac, revelación con
confeti y efecto de sonido, música de fondo y cierre con llamada a comentar/seguir.

Todo es código abierto y gratuito: Python + Pillow + numpy para gráficos y audio, ffmpeg para exportar.
La música y los efectos se sintetizan por código (sin problemas de derechos de autor).

## Uso

```bash
python3 generar.py quizzes/geografia_espana.json
python3 generar.py quizzes/geografia_espana.json --tema-color neon --preguntas 3 --duracion-max 45
python3 generar.py quizzes/geografia_espana.json --preview 16.8   # un fotograma PNG para revisar
```

Opciones: `--tema-color` (verde, lima, neon, tropical), `--voz`, `--velocidad-voz`,
`--preguntas`, `--duracion-max`, `--cuenta-atras`, `--sin-musica`.

## Formato del quiz (JSON)

```json
{
  "tema": "geografía de España",
  "titulo": "¿Cuánto sabes de geografía de España?",
  "dificultad": "media",
  "preguntas": [
    {"pregunta": "¿...?", "opciones": ["A", "B", "C", "D"], "correcta": "D", "fuente": "por qué es correcta"}
  ]
}
```

El validador comprueba 4 opciones distintas, una letra correcta válida y longitudes legibles.
Las preguntas las redacta y verifica Claude cuando le pides un tema; el campo `fuente`
documenta por qué la respuesta es correcta.

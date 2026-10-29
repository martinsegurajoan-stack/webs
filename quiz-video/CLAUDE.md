# quiz-video — plantilla FINAL de @hora.delquiz

Flujo: el usuario SOLO escribe las preguntas (con opciones y respuesta). Sin pedir más instrucciones,
genera el vídeo con esta plantilla y envíale el MP4 (SendUserFile, display "attach"). No cambies el
diseño ni la voz salvo que lo pida.

## Plantilla (ya implementada en el código)
- 1080x1920 MP4, paleta `verde` con fondo dinámico (degradado en movimiento, rayos que laten con la
  música, formas de colores flotando). Cuenta atrás de 5 s, tic-tac fuerte, música más alta al pensar.
- Intro "¡ES HORA DEL QUIZ!" + título + "NIVEL: MEDIO" (FÁCIL/MEDIO/DIFÍCIL) + nº de preguntas.
- `@hora.delquiz` fijo abajo siempre. Logo `assets/logo.png` en el cierre bajo "¡SÍGUEME PARA MÁS!".
- VOZ: ElevenLabs, voz "QUIZ" de la cuenta del usuario (voice_id `7Jak8XD0XjFEAyIV8XkL`, modelo
  `eleven_v4`), acelerada x1.15 al montar. El usuario tiene plan Starter (uso comercial permitido).
- Narración: "¡Es hora del quiz! ¿Estás preparado? ¡Vamos!", "¡Pregunta N!" + pregunta, y SOLO la
  opción correcta al revelarla. Nunca lee las opciones.
- Pregunta con `"sin_respuesta": true`: no se revela; al acabar el tiempo dice
  "¡Escríbelo en los comentarios si te lo sabes!" y sale ese cartel (úsalo si el usuario pide que no
  se diga la respuesta / que la pongan en comentarios).
- Cierre: "¿Cuántas has acertado?" y "¡Sígueme para más!" gritado con aplausos.
- Las frases fijas ya están en `assets/voz_eleven/cache/` y se reutilizan (no se regeneran).

## Pasos para un vídeo nuevo
1. Crea `quizzes/hora_del_quiz_NN.json` (siguiente número libre; formato en README) con el texto del
   usuario (ortografía corregida, mayúsculas normales). `titulo` "¿Cuánto sabes de <tema>?",
   `dificultad` "medio" salvo que diga otra. Verifica cada respuesta (web si es actualidad) en `fuente`;
   si alguna es errónea o ambigua, avísale en el mensaje final.
2. `python3 generar.py quizzes/hora_del_quiz_NN.json --frases-pendientes` → lista de frases que faltan.
3. Para cada frase: `creative_generate_speech` (conector ElevenLabs; carga con ToolSearch
   "elevenlabs generate speech") con `prompt` = el "texto" EXACTO de la lista, `voice_id`
   `7Jak8XD0XjFEAyIV8XkL`, `model_id` `eleven_v4`, `generations_count` 1. Luego
   `creative_get_flow_run_status` hasta completar. Escribe un TSV "<texto>\t<url mp3>" y ejecuta
   `python3 descargar_voz.py archivo.tsv` (guarda cada mp3 con el nombre correcto en la caché).
   Si dice que está saturado, espera un minuto y reintenta (nunca repitas una generación que sí arrancó).
4. `python3 generar.py quizzes/hora_del_quiz_NN.json` (~2-3 min, timeout 600000 ms). Objetivo ≤ 60 s
   (con 4 preguntas sale ~60 s); si se pasa mucho, avisa.
5. Verifica la salida de ffprobe ("OK", 1080x1920, aac) y una hoja de fotogramas:
   `ffmpeg -i X.mp4 -vf "fps=1,scale=180:320,tile=12x6" -frames:v 1 hoja.png`.
   No digas que hay vídeo si el MP4 no existe o no pasó la verificación.
6. Commit del JSON, audios nuevos de la caché y MP4 (`salida/`), push, envía el MP4. Mensaje corto:
   duración + créditos aproximados + avisos sobre respuestas.

## Alternativa gratuita (si ElevenLabs no está disponible)
`--voz kokoro:ef_dora` (requiere `./instalar_voz.sh`; adapta tono a `assets/voz_ref/perfil.npz`).

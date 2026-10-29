# quiz-video — plantilla de @hora.delquiz (DEFINITIVA)

Flujo del usuario: solo escribe las preguntas, opciones y respuestas. Tú generas el vídeo con esta
plantilla SIN cambiar nada del diseño ni de la voz, y le envías el MP4 (SendUserFile, display "attach").

## Plantilla fija (ya implementada en el código; no tocar salvo que el usuario lo pida)
- 1080x1920, MP4, paleta `verde`, cuenta atrás de 5 s con tic-tac fuerte y música algo más alta al pensar.
- Intro: "¡ES HORA DEL QUIZ!" + título + "NIVEL: MEDIO" (masculino: FÁCIL / MEDIO / DIFÍCIL) + nº de preguntas.
- `@hora.delquiz` fijo abajo todo el vídeo. Logo `assets/logo.png` en el cierre bajo "¡SÍGUEME PARA MÁS!".
- Voz: FEMENINA, divertida y amigable: `kokoro:ef_dora`, velocidad 1.15, entonación exagerada con pyworld
  (EXPAND/PITCH en `quizvideo/tts_kokoro.py`).
- La voz SOLO narra: intro, "¡Pregunta N!" + la pregunta, y el cierre. NUNCA lee las opciones ni la respuesta.
- Cierre: "¿Cuántas has acertado? ¡Déjamelo en comentarios!" y después "¡Sígueme para más!" GRITADO
  (más fuerte y agudo) con aplausos.

## Pasos
1. Si no existe `modelos/`, ejecuta `./instalar_voz.sh` (gratis, solo PyPI/npm; en la nube, nunca en el PC del usuario).
2. Crea `quizzes/hora_del_quiz_NN.json` (siguiente número libre) con el texto del usuario tal cual.
   `titulo`: "¿Cuánto sabes de <tema>?" según las preguntas; `dificultad`: "medio" salvo que diga otra.
   Verifica cada respuesta (busca en la web si es actualidad) y anótalo en `fuente`.
   Si una respuesta es errónea o ambigua, avísale en el mensaje final (no la cambies sin decírselo).
3. `python3 generar.py quizzes/hora_del_quiz_NN.json` (~2-3 min, pon timeout de 600000 ms).
4. Comprueba la salida de ffprobe ("OK", 1080x1920, audio aac) y mira 2-3 fotogramas con ffmpeg.
   No digas que hay vídeo si el MP4 no existe o no pasó la verificación.
5. Commit del JSON y del MP4 en `salida/`, push a la rama de trabajo, y envía el MP4 al usuario.
6. Respuesta corta: duración del vídeo + avisos sobre respuestas dudosas, si los hay.

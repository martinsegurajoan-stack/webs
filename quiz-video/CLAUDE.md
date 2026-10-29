# quiz-video — plantilla FINAL de @hora.delquiz

Flujo: el usuario SOLO escribe las preguntas (con opciones y respuesta). Sin pedir más instrucciones,
genera el vídeo con esta plantilla y envíale el MP4 (SendUserFile, display "attach"). No cambies el
diseño ni la voz salvo que lo pida.

## Plantilla (ya implementada en el código)
- 1080x1920 MP4, paleta `verde` con fondo dinámico (degradado en movimiento, rayos giratorios que laten
  con la música, formas de colores flotando). Cuenta atrás de 5 s, tic-tac fuerte, música más alta al pensar.
- Intro "¡ES HORA DEL QUIZ!" + título + "NIVEL: MEDIO" (FÁCIL/MEDIO/DIFÍCIL) + nº de preguntas.
- `@hora.delquiz` fijo abajo siempre. Logo `assets/logo.png` en el cierre bajo "¡SÍGUEME PARA MÁS!".
- Voz femenina alegre: `kokoro:ef_dora` a 1.22, adaptada a la voz de referencia del usuario mediante
  `assets/voz_ref/perfil.npz` (tono ~255 Hz, entonación muy expresiva). No borres ese perfil.
- Narración: intro, "¡Pregunta N!" + pregunta, y SOLO la opción correcta al revelarla
  ("¡Es la B! ..."). Nunca lee las opciones.
- Pregunta con `"sin_respuesta": true`: no se revela; al acabar el tiempo dice
  "¡Escríbelo en los comentarios si te lo sabes!" y aparece ese cartel. Úsalo cuando el usuario diga
  que no se diga la respuesta / que la pongan en comentarios (suele ser la última).
- Cierre: "¿Cuántas has acertado?" y "¡Sígueme para más!" gritado con aplausos.

## Pasos
1. Si no existe `modelos/`, ejecuta `./instalar_voz.sh` (gratis, PyPI/npm, solo en la nube).
2. Crea `quizzes/hora_del_quiz_NN.json` (siguiente número libre; formato en README) con el texto del
   usuario (ortografía corregida, mayúsculas normales). `titulo` "¿Cuánto sabes de <tema>?",
   `dificultad` "medio" salvo que diga otra. Verifica cada respuesta (web si es actualidad) en `fuente`;
   si alguna es errónea o ambigua, avísale en el mensaje final.
3. `python3 generar.py quizzes/hora_del_quiz_NN.json` (~3 min, timeout 600000 ms). Objetivo ≤ 60 s;
   si se pasa, avisa (no quites preguntas sin decírselo).
4. Verifica la salida de ffprobe ("OK", 1080x1920, aac) y una hoja de fotogramas:
   `ffmpeg -i X.mp4 -vf "fps=1,scale=180:320,tile=12x5" -frames:v 1 hoja.png`.
   No digas que hay vídeo si el MP4 no existe o no pasó la verificación.
5. Commit del JSON y MP4 (`salida/`), push, envía el MP4. Mensaje corto: duración + avisos.

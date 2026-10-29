# quiz-video — plantilla de @hora.delquiz

El usuario normalmente solo dará preguntas y respuestas. Usa SIEMPRE la misma plantilla:
paleta verde, voz `kokoro:em_alex` a 1.2, intro "¡ES HORA DEL QUIZ!", `@hora.delquiz` abajo,
logo en el cierre, cuenta atrás de 5 s, nivel MEDIO salvo que diga otro.

1. Si `modelos/` no existe, ejecuta `./instalar_voz.sh` (solo PyPI/npm, gratis).
2. Crea `quizzes/hora_del_quiz_NN.json` (siguiente número) con sus preguntas tal cual.
   Verifica cada respuesta (busca en la web si es actualidad) y anota en `fuente` por qué es correcta.
   Si una respuesta parece errónea o ambigua, avisa al usuario antes de publicar.
3. `python3 generar.py quizzes/hora_del_quiz_NN.json` (tarda ~3 min). Objetivo 30-60 s.
4. Revisa fotogramas con ffmpeg y la salida de ffprobe. No digas que hay vídeo sin MP4 verificado.
5. Haz commit del JSON y el MP4 en `salida/`, push, y envía el MP4 al usuario.

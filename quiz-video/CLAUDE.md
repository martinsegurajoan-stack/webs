# quiz-video

Cuando el usuario pida un quiz (tema, nº de preguntas, dificultad, colores, voz, duración):
1. Redacta las preguntas en español de España en `quizzes/<tema>.json` (formato en README).
   Varía la letra correcta, verifica cada respuesta y explica en `fuente` por qué es correcta.
2. Ejecuta `python3 generar.py quizzes/<tema>.json` con las opciones pedidas.
3. Comprueba la salida de ffprobe que imprime el script y revisa fotogramas con `--preview` o ffmpeg.
4. No digas que hay vídeo si el MP4 no existe y no ha pasado la verificación.

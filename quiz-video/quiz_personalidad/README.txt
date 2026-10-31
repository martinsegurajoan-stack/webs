HORA DEL QUIZ ⚡ — TEST DE PERSONALIDAD
=======================================

Archivos de esta carpeta
- hora_del_quiz_personalidad.mp4  Vídeo final (1080x1920, H.264 + AAC, 30 fps).
- contenido.json                  Todo el contenido: gancho, 9 preguntas, resultados, cierre y portada.

Piezas que usa (en la carpeta quiz-video/)
- generar_personalidad.py         Programa que monta el vídeo.
- quizvideo/personalidad.py       Diseño, animaciones, línea de tiempo, subtítulos y audio de este formato.
- quizvideo/audio.py              Música original sintetizada y efectos (sin licencias externas).
- quizvideo/tts_eleven.py         Voz "QUIZ" de ElevenLabs (caché en assets/voz_eleven/cache/).
- assets/personalidad/*.png       Dibujos 3D (Fluent Emoji 3D, licencia MIT).
- fuentes/                        Lilita One y Baloo 2 (licencia OFL).

Cómo volver a generarlo (desde quiz-video/)
1. Comprobar que están todas las voces (no gasta créditos):
     python3 generar_personalidad.py quiz_personalidad/contenido.json --frases-pendientes
   Debe imprimir []. Si cambias algún texto de "voz", "pregunta" o "leer_opciones", aparecerá la
   frase nueva: genérala con ElevenLabs (voz QUIZ 7Jak8XD0XjFEAyIV8XkL, modelo eleven_v4, texto
   EXACTO de la lista con la etiqueta [playful and a little cheeky]) y descárgala con
     python3 descargar_voz.py archivo.tsv     (líneas "<texto exacto>\t<url del mp3>")
2. Vista previa gratis de algunos segundos (PNG):
     python3 generar_personalidad.py quiz_personalidad/contenido.json --preview 2,15,120 -o /tmp/prev
3. Montar el vídeo (unos minutos):
     python3 generar_personalidad.py quiz_personalidad/contenido.json
   No sobrescribe un MP4 existente: bórralo o usa -o otra_ruta.mp4.
   Al terminar verifica resolución, audio y duración con ffprobe.
4. Portadas: python3 portada.py quiz_personalidad/contenido.json  → portadas/hora_del_quiz_personalidad_*.png

Notas
- La voz NO se acelera (tempo 1,0). Duración objetivo 1:30-1:45.
- Subtítulos estilo TikTok sincronizados con las pausas reales del audio.

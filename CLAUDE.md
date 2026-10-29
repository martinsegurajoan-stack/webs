# Repositorio webs

Vídeos de quiz de TikTok (@hora.delquiz): si el usuario escribe preguntas de quiz, sigue
`quiz-video/CLAUDE.md` y genera el vídeo con la plantilla guardada.
Con CADA vídeo envía SIEMPRE, aunque no lo pida: el MP4, las 2 portadas (9:16 para Instagram,
Facebook y YouTube Shorts; 3:4 para TikTok) y título + descripción + hashtags por plataforma
(sección "ENTREGA OBLIGATORIA" de `quiz-video/CLAUDE.md`).

- Proyecto: carpeta `quiz-video/`, en la rama `claude/tiktok-quiz-video-generator-nub6w6`
  (si estás en `main` y no ves `quiz-video/`, cambia a esa rama).
- Vídeos: `quiz-video/salida/*.mp4`. Contenido de cada vídeo: `quiz-video/quizzes/*.json`.
- Plantillas de referencia: `quiz-video/quizzes/hora_del_quiz_02.json` (quiz) y
  `quiz-video/quizzes/pareja_01.json` (quiz de parejas). Generador: `quiz-video/generar.py`.
- Portadas: `quiz-video/portada.py` → `quiz-video/portadas/`. Textos para redes: `quiz-video/descripciones/`.
- Presentador fijo DON QUIZÁS (vídeos de concurso con presentador): `quiz-video/quizvideo/presentador.py`,
  ficha `quiz-video/presentador/don_quizas_ficha.png`. Misma cara siempre; traje y plató según el vídeo.

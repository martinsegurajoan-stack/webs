# Repositorio webs

Vídeos de quiz de TikTok (@hora.delquiz): si el usuario escribe preguntas de quiz, sigue
`quiz-video/CLAUDE.md` y genera el vídeo con la plantilla guardada.
Con CADA vídeo envía SIEMPRE, aunque no lo pida: el MP4, las 2 portadas (9:16 para Instagram,
Facebook y YouTube Shorts; 3:4 para TikTok) y título + descripción + hashtags por plataforma
(sección "ENTREGA OBLIGATORIA" de `quiz-video/CLAUDE.md`).
Plataformas de los textos: TikTok, YouTube Shorts, Instagram, Facebook y TWITTER/X (≤280 caracteres con hashtags).
Banner de X: `quiz-video/banner_twitter.py` → `quiz-video/portadas/twitter_banner_1500x500.png` (1500x500).
Hashtags: MÁXIMO 4 en TODAS las plataformas: #fyp #viral #test #trending.

- GANCHO FUERTE al principio de TODOS los vídeos (antes del saludo, voz y texto desde el fotograma 0):
  ver "GANCHO INICIAL" en `quiz-video/CLAUDE.md`. El usuario lo ha repetido: SIEMPRE gancho espectacular que
  incite a quedarse hasta el final.
- Quiz de VIDEOJUEGOS: modo `gamer` (`quizzes/hora_del_quiz_05.json`), con pantalla de RANGOS al final.
- VÍDEO PARA BEBER / FIESTA CON AMIGOS (concepto aprobado por el usuario, úsalo siempre): pruebas variadas, plantilla `quiz-video/plantillas-quiz/fiesta.json` +
  `generar_fiesta.py` (ver "FIESTA" en `quiz-video/CLAUDE.md`). Solo cartas: `cartas.json`.
- QUIZ DE STREAMERS (AuronPlay, etc.): plantilla `quiz-video/plantillas-quiz/streamer.json` + `generar_streamer.py`
  (necesita FOTO REAL que manda el usuario). Mejorar la estética un poco en cada vídeo nuevo.
- Proyecto: carpeta `quiz-video/`, en la rama `claude/tiktok-quiz-video-generator-nub6w6`
  (si estás en `main` y no ves `quiz-video/`, cambia a esa rama).
- Vídeos: `quiz-video/salida/*.mp4`. Contenido de cada vídeo: `quiz-video/quizzes/*.json`.
- Plantillas de referencia: `quiz-video/quizzes/hora_del_quiz_02.json` (quiz) y
  `quiz-video/quizzes/pareja_01.json` (quiz de parejas). Generador: `quiz-video/generar.py`.
- Portadas: `quiz-video/portada.py` → `quiz-video/portadas/`. Textos para redes: `quiz-video/descripciones/`.
- Presentador fijo DON QUIZÁS (vídeos de concurso con presentador): `quiz-video/quizvideo/presentador.py`,
  ficha `quiz-video/presentador/don_quizas_ficha.png`. Misma cara siempre; traje y plató según el vídeo.

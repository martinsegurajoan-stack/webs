# Repositorio webs

Vídeos de quiz de TikTok (@hora.delquiz): si el usuario escribe preguntas de quiz, sigue
`quiz-video/CLAUDE.md` y genera el vídeo con la plantilla guardada.
Con CADA vídeo envía SIEMPRE, aunque no lo pida: el MP4, las 2 portadas (9:16 para Instagram,
Facebook y YouTube Shorts; 3:4 para TikTok) y título + descripción + hashtags por plataforma
(sección "ENTREGA OBLIGATORIA" de `quiz-video/CLAUDE.md`).
Plataformas de los textos: TikTok, YouTube Shorts, Instagram, Facebook y TWITTER/X (≤280 caracteres, SIN hashtags).
Banner de X: `quiz-video/banner_twitter.py` → `quiz-video/portadas/twitter_banner_1500x500.png` (1500x500).
Hashtags (regla del usuario 01-11-2026): 4 SOLO en TikTok, YouTube Shorts, Instagram y Facebook: SIEMPRE #fyp + los 3
hashtags del TEMA del vídeo que más clics tienen (p. ej. #fyp #mexico #quiz #trivia). En X, sin hashtags.

REGLAS PERMANENTES PARA TODOS LOS QUIZZES (usuario, 31-10-2026; ver «REGLAS PERMANENTES» en `quiz-video/CLAUDE.md`):
1. FINAL QUE INCITA A INTERACTUAR: pedir que comenten cuántas han acertado, de qué quieren el siguiente vídeo,
   que apoyen el vídeo… (voz + carteles muy animados).
2. IMÁGENES REALES en las preguntas (como el quiz de México: foto de fondo + polaroid), sin dar nunca la respuesta.
   ANTES de generarlas, PREGUNTAR SIEMPRE el coste (~212 créditos por foto) y esperar el sí.
3. GANCHO INICIAL y PREGUNTA EXTRA mejorados al máximo: cada vídeo MEJOR que el anterior.
4. Decorar el vídeo entero y añadir cosas durante las preguntas para que la gente no se aburra.

- GANCHO FUERTE al principio de TODOS los vídeos (antes del saludo, voz y texto desde el fotograma 0):
  ver "GANCHO INICIAL" en `quiz-video/CLAUDE.md`. El usuario lo ha repetido: SIEMPRE gancho espectacular que
  incite a quedarse hasta el final.
- QUIZ DE UN PAÍS (México, etc.): modo `mexico` como plantilla (`quiz-video/quizzes/hora_del_quiz_08.json`):
  TODO del país (bandera grande al principio y en portada, colores, dibujos, música, acento del país riendo),
  PRIMER FOTOGRAMA COLORIDO DEL PAÍS con la extra bloqueada, y la extra vendida con mucha emoción
  (ver «Modo "mexico"» en `quiz-video/CLAUDE.md`).
- JUEGO «NO DIGAS LO MISMO QUE YO» (evita decir lo mismo que yo o quedas fuera): plantilla `quiz-video/plantillas-quiz/evita.json`
  + `generar_evita.py`, con todas las mejoras v2 (ver «NO DIGAS LO MISMO QUE YO» en `quiz-video/CLAUDE.md`).
- Quiz de VIDEOJUEGOS: modo `gamer` (`quizzes/hora_del_quiz_05.json`), con pantalla de RANGOS al final.
- VÍDEO PARA BEBER / FIESTA CON AMIGOS (concepto aprobado por el usuario, úsalo siempre): pruebas variadas, plantilla `quiz-video/plantillas-quiz/fiesta.json` +
  `generar_fiesta.py` (ver "FIESTA" en `quiz-video/CLAUDE.md`). Solo cartas: `cartas.json`.
- «¿QUÉ PREFERIRÍAS?» (dilemas con % en barras, ≤60 s): plantilla `quiz-video/plantillas-quiz/preferirias.json` + `generar_preferirias.py`, foto ENTERA de fondo sin recortar (ver sección en `quiz-video/CLAUDE.md`).
- QUIZ DE STREAMERS (AuronPlay, etc.): plantilla `quiz-video/plantillas-quiz/streamer.json` + `generar_streamer.py`
  (necesita FOTO REAL que manda el usuario). Mejorar la estética un poco en cada vídeo nuevo.
  Chat con guion (`chat_guion`: conversaciones entre usuarios sin repetir, piques sin insultos, cosas random,
  MOD serio que dice la respuesta) y cierre SIEMPRE «¿Quién quieres que sea el siguiente? ¡Coméntalo y apoya el vídeo!».
- VÍDEO ANIMADO 2D / cuenta @mundo.supuesto: LEE `quiz-video/animado/INSTRUCCIONES.md` (todas las reglas).
  SIEMPRE: skills al máximo, cada vídeo más profesional, ESCENARIOS distintos según lo que se cuenta (baño, hospital…),
  y entregar MP4 + miniatura TikTok/Instagram + descripción.
- VÍDEO ANIMADO 2D «¿QUÉ PASARÍA SI…?» (HyperFrames, `quiz-video/animado/`): solo contar la historia, final en bucle,
  subtítulos arriba que se iluminan palabra a palabra con recuadro azul de selección en lo importante, fondo propio, voz gratis; ENTREGAR SOLO el MP4 con subtítulos + descripción para
  copiar (subtítulos + invitar a compartir y seguir + 4 hashtags del tema). Cámara adictiva (zooms, ángulos), fondo con
  vida, revisar TODOS los planos. Ver la sección en `quiz-video/CLAUDE.md`.
  Cuenta @mundo.supuesto: MARCA DE AGUA «@mundo.supuesto» SIEMPRE (abajo, horizontal, centrada, transparente, pequeña).
  Voz FIJA: ElevenLabs «Juanjo Viral» (30jLfQdV8RTduXvosh02, eleven_v4) SIN risas, personaje animado que camina y
  gesticula, sin enumerar etapas, y enviar SIEMPRE también la MINIATURA 9:16.
  ESTILO NETFLIX (01-11-2026, para siempre): colores VIVOS, NADA de fondos desenfocados, casa de verdad llena de objetos,
  planos abiertos, comparaciones dibujadas (edificio de 50 pisos), voz sin susurros (mismo tono), transiciones bonitas (no iris),
  primer plano HOOK espectacular, hasta 105 s. Ver «0b» en `quiz-video/animado/INSTRUCCIONES.md`.
- VÍDEO POLÍTICO «¿Y SI GANA <PARTIDO>?» EN 60 s (serie de partidos, @mundo.supuesto, 02-11-2026): plantilla
  `quiz-video/animado/vox29n/` (leer `PLANTILLA.md`): estilo CLARO y decorativo (tarjetas blancas, nada de libreta literal) para adultos, cronómetro de 60 s,
  color del partido suavizado, narrador neutro, datos reales verificados (buenos y malos) con fuente en pantalla,
  bocetos a tinta solo donde ayudan, miniatura sobria de libreta (`miniatura/hacer.js` lee `partido.json`).
- Proyecto: carpeta `quiz-video/`, en la rama `claude/tiktok-quiz-video-generator-nub6w6`
  (si estás en `main` y no ves `quiz-video/`, cambia a esa rama).
- Vídeos: `quiz-video/salida/*.mp4`. Contenido de cada vídeo: `quiz-video/quizzes/*.json`.
- Plantillas de referencia: `quiz-video/quizzes/hora_del_quiz_02.json` (quiz) y
  `quiz-video/quizzes/pareja_01.json` (quiz de parejas). Generador: `quiz-video/generar.py`.
- Portadas: `quiz-video/portada.py` → `quiz-video/portadas/`. Textos para redes: `quiz-video/descripciones/`.
- Presentador fijo DON QUIZÁS (vídeos de concurso con presentador): `quiz-video/quizvideo/presentador.py`,
  ficha `quiz-video/presentador/don_quizas_ficha.png`. Misma cara siempre; traje y plató según el vídeo.

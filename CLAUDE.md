# Repositorio webs — vídeos de TikTok (@hora.delquiz y @mundo.supuesto)
Proyecto en `quiz-video/`, rama `claude/tiktok-quiz-video-generator-nub6w6` (si estás en `main`, cambia a esa rama).
Índice corto: `quiz-video/CLAUDE.md`. Reglas íntegras: `quiz-video/REGLAS_USUARIO_COMPLETAS.md`. Lee SOLO lo del formato pedido.

## Ahorro de tokens (usuario, 08-11-2026)
Una conversación por vídeo. No leer archivos enteros si basta una sección (grep). Revisar con UNA hoja de fotogramas
pequeña. Reutilizar plantillas en vez de reescribir código. Si falta algo importante del encargo (tono, estilo), preguntar
UNA vez al principio para no rehacer.

## Seguridad y gasto
- ElevenLabs: la clave va como variable de entorno; nunca escribirla en archivos.
- No generar voces, imágenes ni renders si el usuario no lo pide por escrito. Fotos: preguntar SIEMPRE el coste
  (~212 créditos/foto) y esperar el sí.

## Reglas de TODOS los vídeos
- Primera palabra en el segundo 0,5 (todo retrasado 0,5 s a la vez: INICIO = 0.5 en montar_voz.py).
- ≥ 61 s (se cobra por visitas); animados entre 75 y 100 s. Comprobar con ffprobe.
- Gancho fuerte desde el fotograma 0, cada vez mejor. CERO CORRECCIONES: estética, gancho y guion cuidados; revisar todo antes de entregar.
- Mejora continua (también portadas): cada vídeo mejor que el anterior; decir qué se ha mejorado. Ver `quiz-video/animado/MEJORA_CONTINUA.md`.
- Skills de vídeo: `.claude/skills/GUIA-SKILLS-VIDEO.md`.

## Quizzes (@hora.delquiz) — detalle en `quiz-video/FORMATOS.md`
- Entregar SIEMPRE: MP4 + 2 portadas (9:16 y 3:4) + textos para TikTok, YouTube Shorts, Instagram, Facebook y X
  (X: ≤ 280 caracteres, sin hashtags). Hashtags: 4 (#fyp + 3 del tema más populares), salvo en X.
- Final que invita a comentar (aciertos, de qué el siguiente, apoyar el vídeo). Imágenes reales en preguntas (preguntar coste).
  Decorar todo y añadir cosas durante las preguntas. Pregunta extra al máximo.
- Formatos con plantilla: país (`mexico`), «no digas lo mismo que yo» (`evita`), gamer, fiesta/beber, cartas,
  ¿qué preferirías?, streamer (foto real del usuario), niveles, misterio, personalidad, presentador Don Quizás.

## Animados (@mundo.supuesto) — leer `quiz-video/animado/INSTRUCCIONES.md`
- Voz FIJA «Juanjo Viral» (30jLfQdV8RTduXvosh02, eleven_v4, 1 toma, guion entero en una llamada), sin risas.
- Marca de agua «@mundo.supuesto» abajo, centrada, pequeña y transparente. Subtítulos arriba palabra a palabra con recuadro azul.
- Entregar MP4 + miniatura 9:16 (y recorte 3:4 TikTok, contenido entre y 240-1680) + descripción (+ invitar a compartir y seguir + 4 hashtags).
- Guion adictivo sin tramos aburridos; final en seco pero no tan brusco (nunca «el siguiente eres tú»), y el FINAL CUADRA SIEMPRE
  con el PRINCIPIO (bucle: última frase enlaza con la primera, último fotograma = primero). Sin ruido tipo radio al final.
  Vídeos MUY decorados, visuales y adictivos.
- «¿QUÉ PASARÍA SI…?» INFORMATIVO (preferido desde 08-11-2026): `quiz-video/animado/PLANTILLA_INFORMATIVO.md`
  (narrador serio y neutro, sin humor, datos reales, UN SOLO PLANO siguiendo al protagonista, sin transiciones, información
  sencilla junto a él, decorado y luz cuidados).
- Político «¿Y si gana…?»: `animado/vox29n/PLANTILLA.md`. Geopolítico con mapa: `animado/marruecos/PLANTILLA.md`.

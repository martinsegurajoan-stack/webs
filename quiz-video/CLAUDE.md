# quiz-video — plantilla FINAL de @hora.delquiz

## EMPEZAR EN UNA CONVERSACIÓN NUEVA (leer primero)
- Repositorio: `martinsegurajoan-stack/webs`. TODO el proyecto está en la rama
  `claude/tiktok-quiz-video-generator-nub6w6` (NO está en `main` mientras el usuario no pida fusionarlo).
  Si la sesión arranca en `main` y no existe `quiz-video/`, haz
  `git fetch origin claude/tiktok-quiz-video-generator-nub6w6 && git checkout claude/tiktok-quiz-video-generator-nub6w6`.
- Carpeta del proyecto: `quiz-video/` (rutas de abajo relativas a ella). Ejecuta los comandos desde ahí.
- Requisitos ya presentes en el entorno: Python 3 con Pillow y numpy, ffmpeg/ffprobe, npm. Comprueba
  con `python3 -c "import PIL, numpy"` y `ffmpeg -version`. No hace falta instalar nada más para la voz
  ElevenLabs (los audios se guardan en el repo). Kokoro (`modelos/`) solo es la alternativa gratis.
- Conector ElevenLabs: cárgalo con ToolSearch ("elevenlabs generate speech"). Usa el conector completo
  (`mcp__ElevenLabs-ef767449__*`) o el restringido; ambos tienen `creative_generate_speech`.
- Antes de nada, prueba que todo funciona sin gastar créditos:
  `python3 generar.py quizzes/hora_del_quiz_02.json --frases-pendientes` → debe imprimir `[]`.

## GANCHO INICIAL — OBLIGATORIO EN TODOS LOS VÍDEOS (regla del usuario, mejorarlo siempre)
Los 2 primeros segundos deciden si la gente se queda. En CUALQUIER formato (quiz, parejas, temático,
niveles, personalidad, misterio…):
- El gancho va PRIMERO, antes del saludo «¡Es hora del quiz!». La voz suena desde el fotograma 0 (sin
  silencio ni whoosh antes) y hay texto GRANDE en pantalla desde el primer fotograma (nada de fundidos lentos).
- Frase muy corta (≤ 3 s) de reto, curiosidad o tensión, hablándole al espectador: «Casi nadie llega al
  final… ¿hasta dónde llegas tú?», «Si aciertas la última eres un genio», «La pregunta 5 la falla todo el mundo».
  NUNCA estadísticas inventadas («el 97 % falla») ni prometer algo que el vídeo no cumple.
- Adelanta lo más llamativo que viene (la pregunta extra, el nivel imposible, el giro) sin revelar respuestas.
- Movimiento fuerte en el primer segundo (zoom, sacudida, destello, piezas que se encienden).
- Distinto en cada vídeo. Si dudas entre dos, elige el más provocador.
- REGLA REPETIDA POR EL USUARIO (30-10-2026): «quiero un gancho espectacular al principio incitando que se
  queden todo el vídeo. Recuérdalo siempre». Además del texto, refuerza con pegatina de reto («¿LLEGAS AL 6/6?»)
  y anticipa la pregunta final/imposible para que esperen hasta el final.

## ENTREGA OBLIGATORIA DE CADA VÍDEO (aunque el usuario no lo pida)
Cada vez que el usuario pida un vídeo (quiz, quiz de parejas, temático…), envía SIEMPRE, sin preguntar:
1. El MP4 (`SendUserFile`, display "attach").
2. Las 2 portadas (`SendUserFile`, display "render"): `portadas/<video>_9x16.png` (Instagram Reels,
   Facebook Reels, YouTube Shorts) y `portadas/<video>_3x4.png` (TikTok).
3. En el mensaje, título + descripción + hashtags para cada plataforma, VÍDEO A VÍDEO (sin mezclar
   vídeos) y en bloques de código para copiar: TikTok, YouTube Shorts, Instagram, Facebook.
   Reglas: TikTok/Instagram/Facebook no tienen campo título → el "título" es la 1ª línea del texto;
   YouTube: título ≤100 caracteres con `#shorts`; Instagram también con muchos hashtags (ya NO hay máximo de 5); siempre `#horadelquiz`;
   nunca revelar respuestas; CTA a comentar la puntuación (parejas: etiquetar a la pareja).
   Guarda esos textos en `descripciones/<video>.md`.
   HASHTAGS (petición del usuario 30-10-2026): MUCHOS MÁS y más virales. TikTok: 15-20 (virales #fyp #foryou
   #parati #viral #viralvideo #trending #tiktokespaña #xyzbca + los del tema del vídeo + #quiz #horadelquiz).
   YouTube: 10-15 en la descripción (#shorts #viral #fyp #trending + tema). Facebook: 10-15 (#reels #viral
   #fyp #parati + tema). Instagram: 15-20 también (#fyp #viral #explore #reels #parati + tema + #horadelquiz).

## INVENTARIO (estado a 29-10-2026)
Vídeos terminados (1080x1920, H.264 + AAC), en `salida/`:
| Archivo | Quiz (JSON) | Duración | Notas |
|---|---|---|---|
| `salida/geografia_espana.mp4` | `quizzes/geografia_espana.json` | 50 s | Prueba v1 sin voz (estilo antiguo, no publicar) |
| `salida/hora_del_quiz_01.mp4` | `quizzes/hora_del_quiz_01.json` | 61 s | Trivial nº1 (verde, 3+1, estilo anterior a las mejoras) |
| `salida/hora_del_quiz_02.mp4` | `quizzes/hora_del_quiz_02.json` | 88 s | Trivial nº2 acertijos (azul, 5+extra) = PLANTILLA TRIVIAL DE REFERENCIA |
| `salida/pareja_01.mp4` | `quizzes/pareja_01.json` | 84 s | Parejas nº1 (rosa, 5+extra) = PLANTILLA PAREJA DE REFERENCIA |
| `salida/pareja_02.mp4` | `quizzes/pareja_02.json` | 81 s | Parejas nº2 (rojo coral, 5+extra, portada cartel) |
| `salida/hora_del_quiz_06.mp4` | `quizzes/hora_del_quiz_06.json` | 89 s | QUIZ DEL COLE (modo `cole`, verde, fácil→muy difícil sin avisar, notas al final) = PLANTILLA COLE |
| `salida/mascota_01.mp4` | `quizzes/mascota_01.json` | 87 s | QUIZ DE MASCOTAS nº1 (modo `mascota`, amarillo, 5+exclusiva, cierre parte 2) = PLANTILLA MASCOTAS |
| `salida/hora_del_quiz_03.mp4` | `quizzes/hora_del_quiz_03.json` | 105 s | Quiz de HALLOWEEN (modo `halloween`, 5+extra, comentarios cortos, dibujos genéricos) = PLANTILLA TEMÁTICA DE REFERENCIA |
| `salida/hora_del_quiz_04.mp4` | `quizzes/hora_del_quiz_04.json` | 106 s | Quiz de FÚTBOL nivel ALTO (modo `futbol`, campo de fútbol) = PLANTILLA FÚTBOL |
| `salida/misterio_01.mp4` | `quizzes/misterio_01.json` | 81 s | MISTERIO CRIMINAL nº1 v2 (sin revelar culpable, final con gancho) = PLANTILLA DE MISTERIO |
| `salida/niveles_01.mp4` | `quizzes/niveles_01.json` | 105 s | NIVELES nº1 (6 pruebas distintas, nivel imposible a comentarios) = PLANTILLA DE NIVELES |
| `salida/niveles_02.mp4` | `quizzes/niveles_02.json` | 111 s | NIVELES nº2 «PARTE 2: MÁS DIFÍCIL» (gama de colores B, pruebas más duras, imposible = reloj 22 superposiciones) |
| `salida/niveles_03.mp4` | `quizzes/niveles_03.json` | 88 s | NIVELES nº3: MINIJUEGOS rápidos (fugitivo, rojo, memoria6, infiltrado, ilusión) + foto pixelada imposible |
| `salida/cartas_01.mp4` | `quizzes/cartas_01.json` | 109 s | ELIGE UNA CARTA nº1 (juego para beber con amigos) = PLANTILLA DE CARTAS |
| `salida/hora_del_quiz_05.mp4` | `quizzes/hora_del_quiz_05.json` | 101 s | Quiz GAMER (modo `gamer`, 5 + PREGUNTA IMPOSIBLE, pantalla de RANGOS) = PLANTILLA GAMER |
| `salida/hora_del_quiz_07.mp4` | `quizzes/hora_del_quiz_07.json` | 89 s | Quiz GAMER nº2 (modo `gamer`, piques + comentarios, PREGUNTA TRAMPA, rangos rápidos, tempo 1,28) |
| `salida/fiesta_01.mp4` | `quizzes/fiesta_01.json` | 119 s | FIESTA nº1 (7 pruebas distintas para beber + prueba imposible + brindis final) = PLANTILLA FIESTA |
| `salida/streamer_01.mp4` | `quizzes/streamer_01.json` | 84 s | STREAMER nº1: AuronPlay (foto real, estética de directo) = PLANTILLA STREAMER |
| `quiz_personalidad/hora_del_quiz_personalidad.mp4` | `quiz_personalidad/contenido.json` | 103 s | TEST DE PERSONALIDAD v2 (6 preguntas, reacciones, subtítulos TikTok) = PLANTILLA DE TEST DE PERSONALIDAD |
Ojo: regenerar `hora_del_quiz_01` con el código actual le aplicaría el estilo nuevo (y gastaría créditos
en frases nuevas). No regeneres vídeos ya entregados salvo que el usuario lo pida.

Plantillas y piezas reutilizables:
- PLANTILLAS LISTAS PARA COPIAR (una por tipo de vídeo) + índice: `plantillas-quiz/` (`LEEME.md`).
- Contenido de ejemplo (copiar para vídeos nuevos): `quizzes/hora_del_quiz_02.json` (trivial) y
  `quizzes/pareja_01.json` (pareja).
- Generador: `generar.py` (CLI) + `quizvideo/` (`render.py` diseño/animación/modos, `themes.py` paletas,
  `audio.py` música y efectos, `frases_intro.py` frases salseantes, `tts_eleven.py` voz, `validate.py`).
- Voz: `descargar_voz.py` (baja los mp3 de ElevenLabs a la caché), caché `assets/voz_eleven/cache/*.mp3`.
- Recursos: `assets/logo.png`, `assets/imagenes/*_3d.png`, `fuentes/titulo.ttf`, `fuentes/texto.ttf`.
- Registros (NO borrar, hacer commit tras cada vídeo): `assets/paletas_usadas.json` (colores usados),
  `assets/frases_usadas.json` y `assets/frases_pareja_usadas.json` (frases de intro usadas).
- No están en git a propósito: `modelos/` (Kokoro, se reinstala con `./instalar_voz.sh`) y
  `assets/voz_ref/referencia.wav` (audio de referencia del usuario; solo se guarda `perfil.npz`).

## Nombres de archivo
- Trivial (y temáticos como Halloween): `quizzes/hora_del_quiz_NN.json` → `salida/hora_del_quiz_NN.mp4` (siguiente: 08).
- Pareja: `quizzes/pareja_NN.json` → `salida/pareja_NN.mp4` (siguiente: 03).
- Mascotas: `quizzes/mascota_NN.json` → `salida/mascota_NN.mp4` (siguiente: 02).
- Niveles: `quizzes/niveles_NN.json` → `salida/niveles_NN.mp4` (siguiente: 04).
- Cartas: `quizzes/cartas_NN.json` → `salida/cartas_NN.mp4` (siguiente: 02).
- Fiesta: `quizzes/fiesta_NN.json` → `salida/fiesta_NN.mp4` (siguiente: 02).
- Streamer: `quizzes/streamer_NN.json` → `salida/streamer_NN.mp4` (nº1 = AuronPlay, siguiente: 02).

RESUMEN: "quiz" → plantilla trivial; "quiz de parejas" → plantilla pareja. Ambos con TODAS las mejoras,
5 preguntas + 1 extra sin respuesta (comentarios), y se envía el MP4 sin pedir más instrucciones.

Flujo: el usuario SOLO escribe las preguntas (con opciones y respuesta). Sin pedir más instrucciones,
genera el vídeo con esta plantilla y envíale el MP4 (SendUserFile, display "attach"). No cambies el
diseño ni la voz salvo que lo pida.

## Formato (desde el vídeo 2)
- QUIZ: 5 preguntas + 1 EXTRA sin respuesta al final (`"sin_respuesta": true`, cabecera "PREGUNTA EXTRA",
  voz "¡Pregunta extra!", pide escribirla en comentarios). Si el usuario manda menos de 5 normales,
  completa tú con un acertijo/pregunta verificada del mismo estilo y díselo.
- PAREJA: igual que el quiz: 5 preguntas + 1 EXTRA de comentarios (6 en total).
- INTRO del quiz: "¡Es hora del quiz!" + una frase SALSEANTE distinta en cada vídeo, elegida sola de
  `quizvideo/frases_intro.py` (registro `assets/frases_usadas.json`). Si se agotan, añade más frases de
  ese estilo al final de la lista (picantes, de reto, en español de España).
- Duración esperada: ~85-90 s (5+1). No recortes preguntas.

## Plantilla (ya implementada en el código)
- COLOR: NUNCA repetir el color de fondo entre vídeos. Por defecto la paleta es `auto`: `generar.py`
  elige el tono más alejado de los ya usados (registro `assets/paletas_usadas.json`, se actualiza solo
  tras un render correcto; regenerar el mismo vídeo reutiliza su tono). No pases `--tema-color`.
- IMÁGENES — REGLA DEL USUARIO: el dibujo NUNCA puede mostrar ni insinuar la respuesta correcta ni
  ninguna opción (nada de gato negro en "¿qué animal…?", bandera en "¿qué país…?"). Usa un dibujo
  GENÉRICO del tema (en Halloween: calabaza, fantasma, calavera, araña, piruleta, telaraña…).
- IMÁGENES: cada pregunta lleva `"imagen": "<nombre>_3d.png"` (dibujo 3D gratis con fondo
  transparente, a la izquierda del cronómetro). Salen del paquete npm `@lobehub/fluent-emoji-3d`
  (MIT): `npm pack @lobehub/fluent-emoji-3d`, buscar el emoji por su código Unicode en
  `package/assets/<codigo>.webp` (p. ej. pulpo 1f419, calendario 1f4c6, caramelo 1f36c, bandera 1f3c1)
  y guardarlo como PNG en `assets/imagenes/`. Elige el objeto que mejor represente la pregunta.
  El usuario eligió estos dibujos gratis frente a imágenes realistas de pago (~212 créditos c/u).
- Tipografías: `fuentes/titulo.ttf` (Lilita One) y `fuentes/texto.ttf` (Baloo 2 ExtraBold), OFL.
- Cuenta atrás con tensión: tic-tac de madera, latido grave, subida (riser), tics dobles en los 2 últimos
  segundos y viñeta roja pulsante en los bordes. Barra de progreso por segmentos bajo la cabecera.
- Fondo dinámico (degradado en movimiento, rayos que laten con la
  música, formas de colores flotando). Cuenta atrás de 5 s, tic-tac fuerte, música más alta al pensar.
- Intro "¡ES HORA DEL QUIZ!" + título + "NIVEL: MEDIO" (FÁCIL/MEDIO/DIFÍCIL) + nº de preguntas.
- `@hora.delquiz` fijo abajo siempre. Logo `assets/logo.png` en el cierre bajo "¡SÍGUEME PARA MÁS!".
- VOZ: ElevenLabs, voz "QUIZ" de la cuenta del usuario (voice_id `7Jak8XD0XjFEAyIV8XkL`, modelo
  `eleven_v4`), acelerada x1.15 al montar. El usuario tiene plan Starter (uso comercial permitido).
- Narración: "¡Es hora del quiz! <frase salseante>", "¡Pregunta N!" + pregunta, y SOLO la
  opción correcta al revelarla. Nunca lee las opciones.
- Pregunta con `"sin_respuesta": true`: no se revela; al acabar el tiempo dice
  "¡Escríbelo en los comentarios si te lo sabes!" y sale ese cartel (úsalo si el usuario pide que no
  se diga la respuesta / que la pongan en comentarios).
- Cierre: "¿Cuántas has acertado?" y "¡Sígueme para más!" gritado con aplausos.
- Las frases fijas ya están en `assets/voz_eleven/cache/` y se reutilizan (no se regeneran).

## Modo "pareja" (QUIZ DE PAREJAS / ¿Cuánto conoces a tu pareja?)
MISMA DINÁMICA Y CALIDAD QUE EL TRIVIAL (petición expresa del usuario), solo cambia el estilo:
- `"modo": "pareja"` en el JSON (ver `quizzes/pareja_01.json`). 5 preguntas + 1 EXTRA de
  comentarios al final (`"sin_respuesta": true`, cabecera "PREGUNTA EXTRA"). Si el usuario manda
  más, pregunta cuál quitar; si manda menos, completa tú con una del mismo estilo y díselo.
- Intro: "¡Es hora del quiz de parejas!" + frase salseante romántica/pícara distinta en cada vídeo
  (lista `FRASES_PAREJA` en `quizvideo/frases_intro.py`, registro `assets/frases_pareja_usadas.json`).
- Imagen 3D en cada pregunta (igual que el trivial; elige algo romántico/relacionado: corazón 2764-fe0f,
  rosa 1f339, anillo 1f48d, besos 1f48b, pareja 1f491, sofá 1f6cb-fe0f, avión 2708-fe0f, dinero 1f4b0...).
- Color: tono nuevo cada vídeo dentro de rosas/rojos/morados (`paleta_romantica`, automático),
  corazones flotando, música romántica suave, mismas tipografías, cronómetro con tensión, barra de
  progreso, relieve, etc.
- Voz QUIZ con etiqueta "[warm, playful and a little flirty]" (contenta pero no eufórica, romántica y
  bromista), tempo x1.08. No hay respuesta correcta: tras la cuenta atrás sale una frase pícara
  rotatoria ("¿Habéis coincidido?", ...) con lluvia de corazones. No hace falta `correcta`.
- Cierre: "¿Cuántas habéis acertado?" + "¡Etiqueta a tu pareja y sígueme para más!" + logo.
- Coste aproximado: ~85 créditos por pregunta (la etiqueta de tono también cuenta).

## Modo "cole" (QUIZ DEL COLE / «lo sabe hasta un niño de 13 años»)
- `"modo": "cole"` (ver `quizzes/hora_del_quiz_06.json`): trivial con respuesta narrada. Se VENDE como fácil
  («NIVEL: FÁCIL», «lo sabe hasta un niño de 13 años») pero las preguntas se ponen difíciles sin avisar
  (1-3 asequibles, 4-6 muy difíciles: cosas de primaria que se estudiaron y se olvidan).
- Decorado `_cole()` (sprites en `assets/decor_cole/`): cuadrícula de cuaderno con margen rojo, lápices,
  libros, reglas, manzanas, bombillas… flotando y fórmulas de tiza; estallido de material + destello en el
  gancho. Paleta `paleta_desde_tono(tono, "cole")` (tono auto).
- Por pregunta: `comentario` (voz, 2-4 palabras, aleatorio y gracioso) y `pique` (pegatina SOLO de texto junto
  al cronómetro durante la cuenta atrás, «|» = salto de línea; no gasta créditos).
- Final: `rangos` + `"rangos_rapido": true` (las 4 notas entran seguidas con UNA frase de voz y el cierre
  solo grita «¡Sígueme para más!»). `tempo` en el JSON acelera la voz para no pasar de 90 s (nº1: 1,28).
- Nº1: 89 s, ~695 créditos de voz (18 frases).

## Modo "mascota" (QUIZ DE MASCOTAS / ¿Cuánto conoces a tu mascota?)
- `"modo": "mascota"` (ver `quizzes/mascota_01.json`): como el de parejas (sin respuesta correcta, no hace
  falta `correcta`), 5 + 1 EXTRA de comentarios. Gancho de `FRASES_MASCOTA` ANTES de «¡Es hora del quiz de
  mascotas!» (registro `assets/frases_mascota_usadas.json`).
- Decorado `_mascotas()` en `render.py` (sprites en `assets/decor_mascotas/`): rastros de huellas que cruzan,
  perros/gatos/conejos/hámsters latiendo con la música, huesos, peces, ovillos, pelotas, y un perro y un gato
  que se asoman por abajo. El dibujo de cada pregunta sale en una FOTO POLAROID. Tras la cuenta atrás: frase
  graciosa (campo `fin`: [voz, CARTEL] por pregunta) con lluvia de huellas, huesos y corazones.
- Paleta `paleta_mascota` (tonos cálidos 25-80, nº1 amarillo 57). Música pop. Voz QUIZ "[cheerful and playful]",
  tempo x1.12; final "[excited, cheerful]".
- Campos por pregunta (sirven en cualquier modo): `cabecera` (p. ej. "PREGUNTA EXCLUSIVA"), `etiqueta_voz`
  ("¡Pregunta exclusiva!"), `pegatina` (cartel rojo inclinado sobre la tarjeta), `pregunta_voz`, `fin`.
- Cierre: «¿Conoces de verdad a tu mascota?» + «Si te ha gustado y quieres la parte dos, ¡sígueme y apoya
  el vídeo!» con «¡SÍGUEME PARA LA PARTE 2!» y «♥ APOYA EL VÍDEO» (claves `outro_pill`/`outro_pill2` del modo).
- Nº1: 87 s, ~1.075 créditos de voz (15 frases). Dibujos 3D gratis (el usuario pidió «fotos»; se usaron
  los dibujos 3D gratis de siempre).

## Modo "halloween" (quiz temático) y CHISTES
- `"modo": "halloween"`: misma dinámica que el trivial (5+extra, respuesta narrada, cronómetro con
  tensión...) pero TODO Halloween: paleta `paleta_halloween` (noche morada/negra + naranja, tono
  registrado en 262-300), decorado `_halloween()` en `render.py` (luna con halo, telaraña con araña
  colgando, murciélagos aleteando, fantasmas, calaveras y dulces flotando, niebla y calabazas que laten),
  sprites en `assets/decor_halloween/`, música `music_halloween` (La menor, órgano, clavecín, theremin),
  voz con etiqueta "[playful and spooky]", intro "¡Es hora del quiz de Halloween!" + frase de
  `FRASES_HALLOWEEN` (registro `assets/frases_halloween_usadas.json`), cierre "…si te atreves".
- COMENTARIOS (NO chistes, petición del usuario): campo opcional `"comentario"` en cada pregunta con
  respuesta: una frase MUY corta (2-5 palabras) relacionada con el tema, que se dice justo después de
  la respuesta y sustituye un momento al texto de la tarjeta. Ej. Halloween: "¡Miau… qué escalofrío!",
  "¡Drácula ya está temblando!", "¡Abracadabra, acertaste!". (~45 créditos y ~2,5 s cada uno.)
- Para otras temáticas (Navidad, verano...) crea un modo nuevo igual que `halloween` (paleta,
  decorado, música, frases) y pregúntale al usuario solo si no está claro el estilo.

## Modo "futbol" (quiz temático de fútbol)
- `"modo": "futbol"` (ver `quizzes/hora_del_quiz_04.json`): misma dinámica que el trivial (5+extra,
  respuesta narrada, `comentario` corto tras cada respuesta). Fondo = CAMPO DE FÚTBOL (`_init_futbol`:
  césped a rayas, líneas, porterías, focos de estadio que laten), decorado `_futbol()` (balones botando,
  tarjetas amarilla/roja girando, trofeos, medallas, confeti), sprites en `assets/decor_futbol/`.
  Paleta `paleta_futbol` (tono verde nuevo en 95-140, correcta en dorado). Música `music_futbol`
  (pop + murmullo de afición + palmas de grada). Voz QUIZ "[excited sports commentator]", tempo x1.12.
- GANCHO PRIMERO: la frase de `FRASES_FUTBOL` va ANTES de "¡Es hora del quiz de fútbol!" (registro
  `assets/frases_futbol_usadas.json`). Dificultad admite "alto" → "NIVEL: ALTO".
- Imágenes genéricas de fútbol (trofeo, balón, tarjeta roja, medalla, portería, pizarra): nunca la respuesta.
- Etiquetas de voz cortas (se cobran en cada frase). Coste quiz 1: ~1.550 créditos.

## Modo "gamer" (quiz de videojuegos) y PANTALLA DE RANGOS
- `"modo": "gamer"` (ver `quizzes/hora_del_quiz_05.json`): MISMA plantilla que el trivial (el usuario lo pidió
  así: mismo estilo, sin calcar colores, muy decorado). Paleta `paleta_gamer` (synthwave oscuro, tono nuevo en
  160-300, amarillo + fucsia), decorado `_gamer()` en `render.py`: estrellas de píxel, rejilla synthwave que
  avanza al ritmo, bloques de píxel subiendo y sprites 3D (`assets/decor_gamer/`: mandos, monedas que giran,
  gemas, invasores, setas…). Música chiptune `music_gamer` (128 bpm). Voz QUIZ sin etiqueta (reutiliza caché).
- Gancho: `frase_intro` propia del vídeo (adelanta la trampa/la imposible) + «¡Es hora del quiz gamer!»,
  estallido de píxeles y `pegatina_gancho` («¿LLEGAS AL 6/6?»). Lista de reserva `FRASES_GAMER`.
- Pregunta extra con otro nombre: `"etiqueta": "PREGUNTA IMPOSIBLE"`, `"etiqueta_voz": "¡Pregunta imposible!"`
  (sirve en cualquier modo).
- RANGOS (cualquier modo): `"rangos_voz"` + lista `"rangos"` con `rango` («0–2»), `nombre`, `imagen` 3D y
  `voz`. Escena antes del cierre: cada rango entra y se ilumina al decirse; el último en dorado con confeti.
  En modo gamer el cierre pide «¡Dime tu rango en los comentarios!».
- Gamer nº2 (`hora_del_quiz_07`, ≤90 s): `pique` + `comentario` en cada pregunta (diversión), `pregunta_voz` más
  corta que el texto en pantalla para ahorrar segundos, `rangos_rapido` (reutiliza `rangos_voz` y el «¡Sígueme!»
  de la caché), `tempo` 1,28. ~620 créditos de voz.

## Formato "TEST DE PERSONALIDAD" (no es un quiz: no hay respuesta correcta)
`quiz_personalidad/contenido.json` → `generar_personalidad.py` + `quizvideo/personalidad.py`
(reutiliza voz, efectos, música y exportación). Al usuario SOLO se le envía MP4 + 2 portadas + textos.
REGLAS DEL USUARIO (v2): duración 1:30-1:45 MÁXIMO, poca letra, muy divertido.
- 6 preguntas, opciones MUY cortas (2-4 palabras). La pregunta se ilumina palabra a palabra al
  decirse (sin subtítulo duplicado). Cuenta atrás de 5 s con anillo, tic-tac, latido y riser.
- Tras cada cuenta atrás: REACCIÓN graciosa de la voz (campo `reaccion`, etiqueta
  "[playful, laughing a little]") + pegatina rosa con emoji 3D (`reaccion_emoji`) + "boing".
- Resultados: redoble con letras girando → "TU RESULTADO" + 4 fichas 2x2 (letra, emoji, nombre corto)
  que se iluminan al narrarse ("¿Mayoría de A? Tranquilo y práctico: cero dramas.") → pastilla
  "¿EMPATE? ¡ERES UNA MEZCLA!" + aviso "Resultado orientativo · test de entretenimiento".
- Cierre: «¿QUÉ LETRA TE HA SALIDO?», mano 👇, fichas A-D botando, comentarios que se escriben solos,
  logo + "SÍGUENOS".
- SUBTÍTULOS estilo TikTok (distintos de la etiqueta @hora.delquiz): 1-3 palabras en MAYÚSCULAS,
  Lilita gorda con contorno negro y sombra, la palabra que suena salta en amarillo/turquesa.
  Sincronía: pausas reales del audio + reparto por longitud (`align_words`).
- Colores de marca: amarillo, turquesa, morado y negro. Logo "HORA DEL QUIZ ⚡" arriba a la izquierda.
- Voz QUIZ "[playful and a little cheeky]" SIN acelerar (tempo 1,0). v2: 103 s, ~940 créditos nuevos.

## Formato "NIVELES" (ir pasando niveles, cada uno con una prueba distinta)
`quizzes/niveles_NN.json` → `generar_niveles.py` + `quizvideo/niveles.py` → `salida/niveles_NN.mp4` y
`portadas/niveles_NN_*.png` (las portadas salen solas tras el render; `--solo-portada` para rehacerlas).
- Gancho: «¿HASTA QUÉ NIVEL LLEGAS?» + escalera de 6 niveles que se encienden con la voz (el imposible
  tiembla en rojo con destello). Voz desde el fotograma 0.
- Cada nivel: cartel (fondo nuevo que entra en círculo, «NIVEL N» gigante, nombre, medidor de dificultad)
  y prueba con mecánica distinta. Tipos: `secuencia` (fichas + «?» que gira), `busca` (filas de dígitos =
  opciones A-D, círculo en el diferente), `logica` (dibujo 3D + `explicacion`), `memoria` (fichas 5 s con
  barra, se dan la vuelta y luego la pregunta), `acertijo` (cuerdas, opciones en lista, `explicacion`),
  `reloj` (reloj dibujado con la hora `hora`). Cualquier tipo puede ser la ronda `extra` (sin respuesta).
- Barra de niveles arriba (se marcan con ✓ al superar), sello «¡NIVEL N SUPERADO!» con confeti, cuenta
  atrás de 5 s con tic-tac/latido/riser y viñeta roja. Colores fijos por nivel: verde, amarillo, naranja,
  rojo, morado e imposible (negro/rojo); el fondo oscuro del gancho/cierre cambia de tono en cada vídeo.
- Voz QUIZ sin etiqueta (salvo `[excited]` en el gancho y `[whispers]` en el nivel imposible), tempo x1.18.
- Cierre: chips 1-5 + ☠, «¿Hasta qué nivel has llegado?», «¡SÍGUEME PARA MÁS!» y logo.
- Nº1: 105 s, ~1.000 créditos de voz (20 frases).
- COLORES: `"colores": "B"` en el JSON usa otra gama de niveles (turquesa, azul, fucsia, lima, carmesí e imposible
  negro/verde tóxico) para que cada vídeo se vea distinto (A = la del nº1). Añade gamas nuevas en `PALETAS`.
- Gancho: `gancho.pegatina` = pegatina roja de reto bajo el titular. `acertijo` con `imagen` muestra un dibujo 3D
  en vez de las cuerdas (sirve para cualquier acertijo).
- Nº2 («PARTE 2: MÁS DIFÍCIL», gama B): secuencia +3+5+7, un 6 entre nueves, memoria de 7 números, 5 máquinas,
  bate y pelota, imposible = ¿cuántas veces se superponen las agujas en 24 h? (22). 111 s, ~770 créditos de voz.
- MINIJUEGOS (niveles_03, petición del usuario: 90 s MÁXIMO, cada vez más imposible, más difícil que los
  anteriores, muy decorado). Tipos nuevos (`_ronda_nueva`): `fugitivo` (números muy rápidos, ¿cuántas veces
  volvió el primero?), `rojo` (círculos de colores a toda velocidad, contar verdes; los rojos dan destello y
  zumbido), `memoria6` (6 objetos 3 s, se tapan, se barajan y falta uno; usar objetos parecidos), `infiltrado`
  (40 caras 3D casi iguales 😀/😃 en filas, 5 s), `ilusion` (Ebbinghaus con DOBLE trampa: el que parece
  pequeño ES más grande, así fallan también los que «se saben» la ilusión) y `pixel` (EXTRA: foto del usuario
  que se va despixelando por segundos; al final «¿En qué segundo lo adivinaste?»). Campos: `cuenta` (seg. de
  cuenta atrás por ronda), `ritmo`, `memoriza`, `tempo` y `rango_tono` en el JSON. Gancho con `teaser`: la foto
  muy pixelada + «NIVEL IMPOSIBLE» + «¿QUIÉN ES?» (también en la portada). Fotos de personas: solo las que manda
  el usuario (se mejoran con Pillow; quitar el fondo necesitaría instalar una herramienta → preguntar antes).

## Formato "ELIGE UNA CARTA" (juego para beber con amigos)
`quizzes/cartas_NN.json` → `generar_cartas.py` + `quizvideo/cartas.py` → `salida/cartas_NN.mp4` + portadas
(salen solas; `--solo-portada` para rehacerlas). REGLAS DEL USUARIO: muy divertido y alegre, que la gente
PAUSE e interactúe entre ellos, que beban, NADA guarro/sexual. Usar «sorbos» (no chupitos ni «fondo»)
y la nota «Vale con cualquier bebida» (ayuda con TikTok, que limita contenido que incita a beber).
- Gancho: «ELIGE UNA CARTA» desde el fotograma 0 con destello, cartas que salen girando del mazo,
  confeti y pegatina «¡Y QUE BEBA QUIEN TOQUE!». Luego «¿CÓMO SE JUEGA?» con pastilla de pausa.
- Ronda: fondo de color nuevo que entra en círculo (turquesa, naranja, rosa, azul, morado, dorado),
  puntos de progreso, «RONDA N» + nombre, 3 cartas boca abajo flotando (dorso con rombos y número),
  cuenta atrás 5 s + «¡PAUSA Y ELEGID!», las cartas se giran una a una (cara: emoji 3D de
  `assets/cartas/`, texto, cinta de color según `tag`) y al final «¡SALUD!» con copas y confeti.
  Giros: carta TRAMPA que castiga a otra carta, «¿seguro?», MALDICIÓN, ronda final con `dorada` y
  `orden` para dejar la carta dorada para el final.
- Fondo de fiesta: degradado, focos que barren, confeti cayendo; gancho/cierre en morado/fucsia (tono 280-340).
- Voz QUIZ con estilo `[cheerful and excited]` (en el JSON), tempo x1.25. Música pop a 124 bpm.
- Nº1: 109 s, ~1.740 créditos de voz (30 frases; las 3 reacciones de voz se quitaron por ritmo).

## Formato "FIESTA" (pruebas para beber con amigos, cada una con mecánica distinta)
CONCEPTO APROBADO POR EL USUARIO (30-10-2026): CUANDO PIDA UN VÍDEO PARA BEBER / DE FIESTA / CON AMIGOS →
USAR ESTE CONCEPTO (`plantillas-quiz/fiesta.json`) sin preguntar. Se mantiene SIEMPRE: gancho espectacular
de «la última prueba es imposible», pruebas con mecánicas distintas (no solo cartas), estética de discoteca,
prueba final IMPOSIBLE grandiosa y gran final (brindis, fuegos artificiales). En cada vídeo nuevo cambian:
las pruebas y retos (mezclar tipos existentes con tipos nuevos de la lista de ideas), la prueba imposible
(inventar otra grandiosa: no repetir el trabalenguas), el texto del gancho y el color del fondo.
`quizzes/fiesta_NN.json` → `generar_fiesta.py` + `quizvideo/fiesta.py` → MP4 + portadas solas
(`--preview s1,s2 -o ruta` para revisar gratis; `--solo-portada`). Úsalo cuando pida «otro para beber»
que NO sea solo elegir cartas. MISMAS REGLAS que cartas: nada guarro, «sorbos», «Vale con cualquier bebida»,
que pausen e interactúen. Cambiar pruebas y retos en cada vídeo (no repetir frases de «yo nunca», categorías…).
- Estética de DISCOTECA: bola de disco con rayos, reflejos que giran, láseres desde las esquinas, ecualizador
  abajo al ritmo (128 bpm), confeti, bocina de fiesta, sacudidas de pantalla en los golpes.
- Gancho: «¿QUIÉN AGUANTA HASTA EL FINAL?» + carrusel 3D con los iconos de las pruebas (la última bloqueada
  con «?» en rojo) + pegatina «LA ÚLTIMA ES IMPOSIBLE». Luego «¿CÓMO SE JUEGA?» (3 fichas + pausa).
- Cada prueba: fondo neón propio que entra en círculo, barra de pruebas arriba (✓), título que entra
  gigante y sube a la cabecera. Tipos (`tipo`): `ruleta` (8 `sectores`, `gana` = índice; ticks reales al
  pasar cada sector), `senalar` («¿quién es más probable que…?» + 3-2-1 + manos señalando),
  `yo_nunca` (3 `frases` en tarjetas que vuelan + sello «¡BEBE!»), `reflejos` (`secuencia` de emojis,
  `trampas` que tiemblan, al salir la cerveza «¡YA!»), `bomba` (`categoria`, mecha que se quema,
  tic-tac que acelera, explosión), `esto_aquello` (dos cartas VS + 3-2-1 «¡VOTAD!», bebe la minoría) y
  `final` (PRUEBA IMPOSIBLE: susurro, relámpagos, título con glitch, trabalenguas palabra a palabra,
  «¡VUESTRO TURNO!» con cuenta atrás, «¿FALLAS? ¡BEBE!» y corona de REY DE LA FIESTA) → escena de
  BRINDIS FINAL con fuegos artificiales, cervezas chocando y champán. Cierre «¿QUIÉN HA GANADO LA FIESTA?».
- Emojis 3D en `assets/fiesta/` (de `@lobehub/fluent-emoji-3d`). Voz QUIZ `[cheerful and excited]`, tempo
  x1,27; las frases que empiezan con etiqueta (`[whispers]`, `[excited]`) van sin el estilo general.
- Nº1: 119 s, ~1.750 créditos de voz (26 frases). Ideas para el siguiente: «la patata caliente» (pasar el
  móvil), «piedra papel tijera» contra la pantalla, «el dado», «verdad o sorbo», «cadena de palabras».

## Formato "STREAMER" (quiz sobre un streamer, estética de directo) — serie de 5-6 vídeos
CUANDO EL USUARIO PIDA UN QUIZ DE UN STREAMER (cualquiera) → USAR ESTA PLANTILLA (`plantillas-quiz/streamer.json`,
referencia `quizzes/streamer_01.json`). REGLA DEL USUARIO: en cada vídeo nuevo MEJORARLA un poco más en
estética (sin perder el estilo reconocible). Ya hecho tras el nº1: respuestas que FLOTAN (vaivén propio
cada una, la correcta se eleva y brilla), tarjeta de pregunta flotando, halo neón y brillo de cristal en
las opciones, chispas de neón subiendo por el fondo. Ideas para los siguientes: emotes que suben por el
chat, «¡NUEVO SUSCRIPTOR!»/donaciones falsas como transiciones, foto con recorte y contorno (pegatina),
barra de «hype train» que se llena con las preguntas, cámara que se mueve un poco, partículas al revelar.
`quizzes/streamer_NN.json` → `generar_streamer.py` + `quizvideo/streamer.py` → MP4 + portadas solas.
NO es la plantilla trivial (petición del usuario): mismo ADN de marca (Lilita/Baloo, amarillo, logo,
@hora.delquiz, voz QUIZ alegre, cuenta atrás con tensión) pero con look de directo de Twitch.
- FOTO REAL del streamer OBLIGATORIA (`foto`, en `assets/streamers/`): gancho a pantalla completa con
  zoom, sacudida, glitch RGB y destello, «EN DIRECTO» + espectadores, «QUIZ DE <NOMBRE>» y pegatina
  «NIVEL: IMPOSIBLE». `foco` = [x, y] de la cara en la foto original (para recortar), `zoom_cam`.
  La red de la sesión bloquea Wikipedia/Wikimedia: la foto la tiene que mandar el usuario (o subirla
  al repo en esa carpeta). Nunca generar con IA la cara de una persona real. `generar_streamer.py`
  se niega a renderizar sin foto.
- `aviso` (2 líneas) = cinta amarilla de advertencia FIJA arriba durante TODO el vídeo.
- Preguntas: chat en directo con mensajes genéricos que suben, cámara del streamer (su foto) con
  «EN DIRECTO», tarjeta oscura con borde neón, opciones como ENCUESTA de directo con barras y % que
  suben durante la cuenta atrás (aleatorios, no indican la respuesta), alerta «¡CORRECTA! +1 PUNTO DE
  FAN» con confeti. Extra → «PREGUNTA EXTRA · SOLO FANS» y «¡ESCRÍBELO EN COMENTARIOS!».
- Color neón distinto en cada vídeo (tono 200-330 registrado), música pop con semilla por vídeo.
- Voz QUIZ sin etiqueta (gancho `[excited]`), tempo x1.15; reutiliza las frases fijas de la caché.
- Fotos pequeñas (la de Auron es 350x350): en el gancho va ENMARCADA (880 px, con enfoque) sobre la
  misma foto desenfocada, así no se pixela. Nº1: 84 s, ~640 créditos de voz.

## Formato "MISTERIO CRIMINAL" (historia narrada, NO es un quiz)
`quizzes/misterio_NN.json` → `generar_misterio.py` + `quizvideo/misterio.py` → `salida/misterio_NN.mp4`,
`portadas/misterio_NN_*.png`, `descripciones/misterio_NN.md`. Entrega LIMPIA: solo MP4 + 2 miniaturas + textos.
- Estética de thriller, seria y NO infantil: imágenes cinematográficas generadas con ElevenLabs
  (`bytedance-seedream-5-lite`, ~212 créditos c/u, salen 2560x1440 y se recortan en vertical con
  movimiento de cámara). Personajes coherentes: primero el RETRATO de cada uno y luego sus escenas con
  `creative_edit_image` usando el retrato como referencia. Imágenes en `assets/misterio_NN/`.
  Coordenadas de la cara/zona de interés en `focos` del JSON.
- Voz DISTINTA a la de los quizzes: "Jose Conde" (`Otf4KTIb4E5xLTCtWfye`, castellano, grave) con
  etiqueta "[mysterious]", una frase por clip (cada clip = un plano). Caché normal de voces.
- Duración máx. 90 s: se acortan pausas largas y la voz se acelera solo lo necesario (tope x1.14).
- Tipografías serias: `fuentes/serio_bold.ttf`/`serio_semi.ttf` (Montserrat) y `serio_titulo.ttf`
  (Bebas Neue). Subtítulos blancos en mayúsculas, palabras clave en amarillo/turquesa (`destacar`),
  palabra a palabra con sincronía real. Rótulos de sospechoso/pista arriba a la izquierda,
  tarjetas de declaración, tríptico de sospechosos en columnas, cuenta atrás de 5 s, sello, CTA.
- Música de thriller original sintetizada (`music_thriller`), golpes en pistas, silencio antes de la revelación.
- Coste caso 1: ~2.970 créditos de imágenes (14) + ~1.600 de voz (v1) + ~1.250 de voz (v2).
- REGLAS DEL USUARIO (v2): NO revelar al culpable ni dar pistas de quién es ("sin embargo, antes había
  dicho…", "busca quién se contradice" PROHIBIDO). Final con gancho y emoción: «¿QUIÉN MIENTE?», caras que
  se iluminan por turnos, comentarios que se escriben solos, pedir la teoría en comentarios y seguir.
  Voz v2: "Juanjo TikTok" (`30jLfQdV8RTduXvosh02`, castellano, enérgico) con etiquetas de v4 por frase
  ([suspenseful], [intrigued], [whispers], [excited]) y SIN acelerar (tope x1.05). Música con pulso que crece.

## PRESENTADOR FIJO: "DON QUIZÁS" (cuando el usuario pida vídeo con presentador / concurso)
- Personaje dibujado por código en `quizvideo/presentador.py` (gratis, siempre idéntico):
  `presentador(traje, expresion, boca=0..1, parpadeo, mirada, gesto="dedo"|"abierto")` → RGBA 600x900.
- RASGOS FIJOS (no cambiar NUNCA): cabeza redonda, tupé amarillo eléctrico con forma de rayo, bigotón
  castaño rizado, nariz redonda, cejas gruesas, mejillas sonrosadas, diente separado, micro con rayo.
- Cambia en cada vídeo: TRAJE (`TRAJES`: clasico, personalidad, halloween, parejas, trivial; añade
  uno nuevo por temática) y PLATÓ (`plato(nombre)`: clasico, personalidad, halloween, parejas, trivial).
- Expresiones: feliz, sorprendido, picaro, riendo, sospecha. Para hablar, anima `boca` con el volumen
  de la voz y parpadea cada 3-4 s.
- Muletilla: «¿Quizás sí… o quizás no?». Saludo: «¡Bienvenidos a la Hora del Quiz!».
- Ficha de personaje: `presentador/don_quizas_ficha.png` (se regenera con `python3 presentador/ficha.py`).

## Pasos para un vídeo nuevo
1. Crea `quizzes/hora_del_quiz_NN.json` o `quizzes/pareja_NN.json` (siguiente número libre; copia la
   estructura de `hora_del_quiz_02.json` / `pareja_01.json`; añade la imagen 3D de cada pregunta) con el texto del
   usuario (ortografía corregida, mayúsculas normales). `titulo` "¿Cuánto sabes de <tema>?",
   `dificultad` "medio" salvo que diga otra. Si falta el enunciado de alguna pregunta, pregúntalo
  (AskUserQuestion) antes de gastar créditos. Verifica cada respuesta (web si es actualidad) en `fuente`;
   si alguna es errónea o ambigua, avísale en el mensaje final.
2. `python3 generar.py quizzes/hora_del_quiz_NN.json --frases-pendientes` → lista de frases que faltan.
3. Para cada frase: `creative_generate_speech` (conector ElevenLabs; carga con ToolSearch
   "elevenlabs generate speech") con `prompt` = el "texto" EXACTO de la lista, `voice_id`
   `7Jak8XD0XjFEAyIV8XkL`, `model_id` `eleven_v4`, `generations_count` 1. Luego
   `creative_get_flow_run_status` hasta completar. Escribe un TSV "<texto>\t<url mp3>" y ejecuta
   `python3 descargar_voz.py archivo.tsv` (guarda cada mp3 con el nombre correcto en la caché;
   el texto del TSV debe ser el "texto" exacto, etiquetas entre corchetes incluidas).
   Si dice que está saturado, espera un minuto y reintenta (nunca repitas una generación que sí arrancó).
   Las URLs de los mp3 caducan a las 2 h: descárgalas en cuanto terminen. Comprueba después que
   `--frases-pendientes` devuelve `[]`.
4. `python3 generar.py quizzes/<archivo>.json` (~3-4 min con 5+1, timeout 600000 ms). Duración
   esperada ~85-90 s; no recortes preguntas. Antes, si quieres revisar el diseño gratis:
   `--voz ninguna --preview <segundo> -o /ruta/prueba.png` (no gasta créditos ni toca registros).
5. Verifica la salida de ffprobe ("OK", 1080x1920, aac) y una hoja de fotogramas:
   `ffmpeg -i X.mp4 -vf "fps=1,scale=180:320,tile=12x6" -frames:v 1 hoja.png`.
   No digas que hay vídeo si el MP4 no existe o no pasó la verificación.
6. PORTADAS (siempre): añade la clave `"portada"` al JSON (ver sección Portadas; alterna el `estilo`
   respecto al vídeo anterior) y ejecuta `python3 portada.py quizzes/<archivo>.json` DESPUÉS del render
   (así usa el mismo color). Revisa la imagen (que nada se solape y que NO marque la respuesta).
7. TEXTOS (siempre): crea `descripciones/<video>.md` con el formato de `descripciones/hora_del_quiz_02.md`.
8. Commit del JSON, audios nuevos de la caché, MP4, portadas y descripción; push.
9. ENTREGA (ver "ENTREGA OBLIGATORIA" arriba): MP4 + 2 portadas + textos por plataforma en el mensaje.
   Mensaje corto: duración + créditos aproximados + avisos sobre respuestas.

## Alternativa gratuita (si ElevenLabs no está disponible)
`--voz kokoro:ef_dora` (requiere `./instalar_voz.sh`; adapta tono a `assets/voz_ref/perfil.npz`).

## Portadas / miniaturas (SIEMPRE con cada vídeo)
`python3 portada.py quizzes/<video>.json` → `portadas/<video>_9x16.png` (1080x1920: Reels, Shorts,
Facebook) y `portadas/<video>_3x4.png` (1080x1440: portada de TikTok). Textos de cada portada: en vídeos nuevos,
clave `"portada"` dentro del JSON del quiz (los 3 primeros están en el diccionario `PORTADAS` de
`portada.py`; copia su forma, `titulo` como lista de pares [texto, "w"|"a"], sin `paleta`): etiqueta de arriba,
titular gigante (línea "a" = color de acento), pregunta de muestra (índice), 2 emojis 3D de
`assets/portada/`, pegatina gancho y subtítulo. La tarjeta NUNCA marca la respuesta correcta; lo
importante queda en la franja central 3:4. Usa la misma paleta que el vídeo (registro de tonos).
Sin "5 preguntas + 1 extra". Cada portada debe verse DISTINTA con el mismo estilo: clave `estilo` =
`clasica` (pegatina alargada debajo, flecha izq.), `sello` (espejo, sello redondo, flecha dcha.) o
`cartel` (centrado y recto, pegatina arriba, emojis a ambos lados); ve alternándolos.

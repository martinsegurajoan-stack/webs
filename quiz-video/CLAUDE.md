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

## ENTREGA OBLIGATORIA DE CADA VÍDEO (aunque el usuario no lo pida)
Cada vez que el usuario pida un vídeo (quiz, quiz de parejas, temático…), envía SIEMPRE, sin preguntar:
1. El MP4 (`SendUserFile`, display "attach").
2. Las 2 portadas (`SendUserFile`, display "render"): `portadas/<video>_9x16.png` (Instagram Reels,
   Facebook Reels, YouTube Shorts) y `portadas/<video>_3x4.png` (TikTok).
3. En el mensaje, título + descripción + hashtags para cada plataforma, VÍDEO A VÍDEO (sin mezclar
   vídeos) y en bloques de código para copiar: TikTok, YouTube Shorts, Instagram, Facebook.
   Reglas: TikTok/Instagram/Facebook no tienen campo título → el "título" es la 1ª línea del texto;
   YouTube: título ≤100 caracteres con `#shorts`; Instagram MÁXIMO 5 hashtags; siempre `#horadelquiz`;
   nunca revelar respuestas; CTA a comentar la puntuación (parejas: etiquetar a la pareja).
   Guarda esos textos en `descripciones/<video>.md`.

## INVENTARIO (estado a 29-10-2026)
Vídeos terminados (1080x1920, H.264 + AAC), en `salida/`:
| Archivo | Quiz (JSON) | Duración | Notas |
|---|---|---|---|
| `salida/geografia_espana.mp4` | `quizzes/geografia_espana.json` | 50 s | Prueba v1 sin voz (estilo antiguo, no publicar) |
| `salida/hora_del_quiz_01.mp4` | `quizzes/hora_del_quiz_01.json` | 61 s | Trivial nº1 (verde, 3+1, estilo anterior a las mejoras) |
| `salida/hora_del_quiz_02.mp4` | `quizzes/hora_del_quiz_02.json` | 88 s | Trivial nº2 acertijos (azul, 5+extra) = PLANTILLA TRIVIAL DE REFERENCIA |
| `salida/pareja_01.mp4` | `quizzes/pareja_01.json` | 84 s | Parejas nº1 (rosa, 5+extra) = PLANTILLA PAREJA DE REFERENCIA |
| `salida/hora_del_quiz_03.mp4` | `quizzes/hora_del_quiz_03.json` | 105 s | Quiz de HALLOWEEN (modo `halloween`, 5+extra, comentarios cortos, dibujos genéricos) = PLANTILLA TEMÁTICA DE REFERENCIA |
Ojo: regenerar `hora_del_quiz_01` con el código actual le aplicaría el estilo nuevo (y gastaría créditos
en frases nuevas). No regeneres vídeos ya entregados salvo que el usuario lo pida.

Plantillas y piezas reutilizables:
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
- Trivial (y temáticos como Halloween): `quizzes/hora_del_quiz_NN.json` → `salida/hora_del_quiz_NN.mp4` (siguiente: 04).
- Pareja: `quizzes/pareja_NN.json` → `salida/pareja_NN.mp4` (siguiente: 02).

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

## Formato "TEST DE PERSONALIDAD" (no es un quiz: no hay respuesta correcta)
Carpeta `quiz_personalidad/` (contenido.json, MP4, guion.txt, preguntas.txt, README.txt). Programa
`generar_personalidad.py` + `quizvideo/personalidad.py` (reutiliza voz, efectos, música y exportación).
- Colores de marca: amarillo, turquesa, morado y negro (tarjetas A amarilla, B turquesa, C morada,
  D negra con borde amarillo). Logo "HORA DEL QUIZ ⚡" discreto arriba a la izquierda todo el vídeo.
- Estructura: gancho (rayo + titular que cae palabra a palabra + emojis 3D) → 9 preguntas (entradas
  variadas: deslizar, zoom, caída, giro; opciones que entran por los lados con rebote; dibujo 3D a la
  izquierda y emoji de pensar a la derecha del cronómetro; cuenta atrás de 5 s con anillo que se
  vacía, tic-tac, latido y riser; sello «¡APÚNTALA!») → resultados (redoble con letras girando,
  confeti, tarjeta por letra que se resalta mientras se narra, panel de empate + aviso "test de
  entretenimiento") → cierre «¿QUÉ LETRA TE HA SALIDO?» (mano 👇, fichas A-D botando, comentarios que
  se escriben solos, logo + "SÍGUENOS").
- Subtítulos sincronizados abajo (fragmentos repartidos según la duración real de cada audio).
- Voz QUIZ con etiqueta "[playful and a little cheeky]" y SIN acelerar (tempo 1,0, petición del
  usuario: la duración se ajusta al audio real). Solo la pregunta 1 lee las opciones (campo
  `leer_opciones`); las demás solo la pregunta. Coste: ~2.200 créditos el primero (18 frases).
- Con 9 preguntas dura ~170 s (por debajo de los 3 min de Shorts/Reels). Para acercarse a 90 s hay que
  quitar preguntas o acortar la narración de los resultados.
- Portada: clave "portada" en contenido.json (modo personalidad → paleta de marca en portada.py).

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

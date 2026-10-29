# Plantillas de vídeo — Hora del Quiz ⚡ (@hora.delquiz)

Cada archivo es una plantilla **completa y lista para usar**: es el contenido real del vídeo de
referencia ya entregado (preguntas, voz, portada…) más dos campos de ayuda (`_plantilla` y `_uso`)
que los generadores ignoran. Para un vídeo nuevo: **copia la plantilla, cambia el contenido y
ejecuta los comandos de su fila**. Todos los comandos se lanzan desde la carpeta `quiz-video/`.

| Archivo | Tipo de vídeo | Qué hace | Generador | Vídeo de referencia |
|---|---|---|---|---|
| `trivial.json` | Quiz normal | 5 preguntas + 1 EXTRA sin respuesta (a comentarios). Frase gancho salseante, cuenta atrás de 5 s con tensión, voz QUIZ narra la pregunta y la respuesta correcta, color de fondo nuevo cada vez. | `generar.py` | `salida/hora_del_quiz_02.mp4` |
| `pareja.json` | Quiz de parejas | «¿Cuánto conoces a tu pareja?»: 5 + 1 extra, sin respuesta correcta, frase pícara tras cada cuenta atrás, corazones, música romántica, voz cariñosa y bromista. | `generar.py` | `salida/pareja_01.mp4` |
| `halloween.json` | Quiz temático Halloween | Como el trivial pero todo Halloween: luna, telarañas, murciélagos, fantasmas, música de miedo, voz «spooky» y comentario corto tras cada respuesta. | `generar.py` | `salida/hora_del_quiz_03.mp4` |
| `futbol.json` | Quiz temático fútbol | Fondo de campo de fútbol, balones y tarjetas, música de estadio, voz de comentarista, gancho fuerte ANTES del saludo, «NIVEL: ALTO». | `generar.py` | `salida/hora_del_quiz_04.mp4` |
| `personalidad.json` | Test de personalidad | 6 preguntas con opciones A-D cortas, la pregunta se ilumina palabra a palabra, reacción graciosa tras cada cuenta atrás, resultados por letra mayoritaria, subtítulos estilo TikTok. 1:30-1:45. | `generar_personalidad.py` | `quiz_personalidad/hora_del_quiz_personalidad.mp4` |
| `misterio.json` | Misterio criminal | Historia narrada con imágenes cinematográficas realistas (personajes con la misma cara), voz de thriller con emoción, pistas, cuenta atrás y final «¿QUIÉN MIENTE?» SIN revelar al culpable. Máx. 90 s. | `generar_misterio.py` | `salida/misterio_01.mp4` |

## Cómo se usa cada una

### Quizzes (`trivial`, `pareja`, `halloween`, `futbol`)
1. `cp plantillas-quiz/trivial.json quizzes/hora_del_quiz_NN.json` (parejas: `quizzes/pareja_NN.json`).
2. Cambia `tema`, `titulo`, `dificultad` («medio», «alto»…) y las `preguntas`: `pregunta`, 4 `opciones`,
   `correcta` (A-D), `imagen` (dibujo 3D genérico de `assets/imagenes/`, que NUNCA revele la respuesta),
   `comentario` opcional (2-5 palabras, temáticos). La última lleva `"sin_respuesta": true`.
   Ajusta el bloque `portada` (titular, pregunta de muestra, emojis, `estilo` alternando
   clasica / sello / cartel). No hace falta poner `frase_intro`: se elige sola y nunca se repite.
3. `python3 generar.py quizzes/hora_del_quiz_NN.json --frases-pendientes` → lista de voces que faltan.
4. Genera esas voces con ElevenLabs (voz QUIZ `7Jak8XD0XjFEAyIV8XkL`, modelo `eleven_v4`, texto EXACTO)
   y descárgalas con `python3 descargar_voz.py archivo.tsv`.
5. `python3 generar.py quizzes/hora_del_quiz_NN.json` → `salida/hora_del_quiz_NN.mp4`.
6. `python3 portada.py quizzes/hora_del_quiz_NN.json` → `portadas/..._9x16.png` y `..._3x4.png`.

### Test de personalidad (`personalidad`)
1. `cp plantillas-quiz/personalidad.json quiz_personalidad/<nombre>.json` y cambia `video` a `<nombre>`.
2. Cambia el gancho (`intro`), las 6 `preguntas` (opciones muy cortas, `reaccion` y `reaccion_emoji`),
   los 4 `perfiles` del `resultado`, el `cierre` y la `portada`.
3. `python3 generar_personalidad.py quiz_personalidad/<nombre>.json --frases-pendientes` → voces que faltan
   → genéralas (voz QUIZ) → `python3 generar_personalidad.py quiz_personalidad/<nombre>.json`
   → `python3 portada.py quiz_personalidad/<nombre>.json`.

### Misterio criminal (`misterio`)
1. `cp plantillas-quiz/misterio.json quizzes/misterio_NN.json` y cambia `video`, `titulo` e `imagenes`
   (`assets/misterio_NN`).
2. Genera las imágenes con ElevenLabs (`bytedance-seedream-5-lite`, ~212 créditos c/u): primero el
   RETRATO de cada sospechoso y luego sus escenas con edición desde el retrato (misma cara). Apunta en
   `focos` dónde está la cara o la zona importante de cada imagen.
3. Escribe los `clips` (una frase de voz = un plano, con etiquetas de interpretación como
   `[suspenseful]`, `[intrigued]`, `[whispers]`, `[excited]`), `rotulo`, `tarjetas`, la `cuenta_atras`
   y el clip `final`. Nunca reveles al culpable.
4. `python3 generar_misterio.py quizzes/misterio_NN.json --faltan` → voces que faltan (voz Juanjo
   `30jLfQdV8RTduXvosh02`) → `python3 generar_misterio.py quizzes/misterio_NN.json` (MP4 + portadas).

## Siempre, con cada vídeo
- Entregar SOLO: el MP4, las 2 miniaturas (9:16 para Instagram/Facebook/Shorts y 3:4 para TikTok) y
  título + descripción + hashtags por plataforma (guardados en `descripciones/<video>.md`).
- Comprobar el MP4 (1080x1920, con audio, duración correcta) y revisar una hoja de fotogramas.
- Si el MP4 supera 100 MB, comprimirlo antes de subirlo a GitHub.
- Presentador fijo DON QUIZÁS para vídeos con presentador: `quizvideo/presentador.py` (ficha en
  `presentador/don_quizas_ficha.png`).
- Detalle completo de reglas y estilos: `quiz-video/CLAUDE.md`.

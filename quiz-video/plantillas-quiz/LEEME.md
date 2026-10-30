# Plantillas de vídeo — Hora del Quiz ⚡ (@hora.delquiz)

Cada archivo es una plantilla **completa y lista para usar**: es el contenido real del vídeo de
referencia ya entregado (preguntas, voz, portada…) más dos campos de ayuda (`_plantilla` y `_uso`)
que los generadores ignoran. Para un vídeo nuevo: **copia la plantilla, cambia el contenido y
ejecuta los comandos de su fila**. Todos los comandos se lanzan desde la carpeta `quiz-video/`.

| Archivo | Tipo de vídeo | Qué hace | Generador | Vídeo de referencia |
|---|---|---|---|---|
| `trivial.json` | Quiz normal | 5 preguntas + 1 EXTRA sin respuesta (a comentarios). Frase gancho salseante, cuenta atrás de 5 s con tensión, voz QUIZ narra la pregunta y la respuesta correcta, color de fondo nuevo cada vez. | `generar.py` | `salida/hora_del_quiz_02.mp4` |
| `pareja.json` | Quiz de parejas | «¿Cuánto conoces a tu pareja?»: 5 + 1 extra, sin respuesta correcta, frase pícara tras cada cuenta atrás, corazones, música romántica, voz cariñosa y bromista. | `generar.py` | `salida/pareja_01.mp4` |
| `mascota.json` | Quiz de mascotas | «¿Cuánto conoces a tu mascota?»: 5 + 1 pregunta EXCLUSIVA con pegatina, sin respuesta correcta, frase graciosa tras cada cuenta atrás con lluvia de huellas y huesos, fondo cálido con perros, gatos, conejos, rastros de huellas y mascotas que se asoman, dibujo de cada pregunta en foto polaroid, cierre «¡SÍGUEME PARA LA PARTE 2!» + «APOYA EL VÍDEO». | `generar.py` | `salida/mascota_01.mp4` |
| `halloween.json` | Quiz temático Halloween | Como el trivial pero todo Halloween: luna, telarañas, murciélagos, fantasmas, música de miedo, voz «spooky» y comentario corto tras cada respuesta. | `generar.py` | `salida/hora_del_quiz_03.mp4` |
| `futbol.json` | Quiz temático fútbol | Fondo de campo de fútbol, balones y tarjetas, música de estadio, voz de comentarista, gancho fuerte ANTES del saludo, «NIVEL: ALTO». | `generar.py` | `salida/hora_del_quiz_04.mp4` |
| `gamer.json` | Quiz GAMER (videojuegos) | Plantilla trivial con decorado gamer synthwave (píxeles, rejilla neón, mandos, monedas), música chiptune, PREGUNTA IMPOSIBLE y pantalla de RANGOS (novato → leyenda). ~1:40. | `generar.py` | `salida/hora_del_quiz_05.mp4` |
| `personalidad.json` | Test de personalidad | 6 preguntas con opciones A-D cortas, la pregunta se ilumina palabra a palabra, reacción graciosa tras cada cuenta atrás, resultados por letra mayoritaria, subtítulos estilo TikTok. 1:30-1:45. | `generar_personalidad.py` | `quiz_personalidad/hora_del_quiz_personalidad.mp4` |
| `niveles.json` | Niveles (pruebas distintas) | Gancho con escalera de niveles que se enciende, 5 niveles con color propio (verde→amarillo→naranja→rojo→morado) y mecánica distinta (secuencia, encuentra el diferente, lógica, memoria, acertijo), cartel «NIVEL N», sello «¡NIVEL SUPERADO!» con confeti y barra de progreso arriba; nivel IMPOSIBLE (reloj) a comentarios. ~1:45. | `generar_niveles.py` | `salida/niveles_01.mp4` |
| `cartas.json` | Elige una carta (beber con amigos) | Gancho con cartas que salen del mazo, «¿cómo se juega?», 6 rondas de 3 cartas boca abajo con cuenta atrás «¡PAUSA Y ELEGID!», se giran una a una con su prueba (sorbos, brindis, trampas, maldiciones…), choque de copas y confeti, carta dorada final. Sin contenido guarro. ~1:50. | `generar_cartas.py` | `salida/cartas_01.mp4` |
| `fiesta.json` | FIESTA: pruebas para beber con amigos (cada una distinta) | Discoteca (bola de disco, láseres, ecualizador, bocina). Gancho «¿QUIÉN AGUANTA HASTA EL FINAL?» con carrusel de pruebas y la última bloqueada. Tipos: `ruleta`, `senalar`, `yo_nunca`, `reflejos`, `bomba`, `esto_aquello` y `final` (prueba imposible: trabalenguas + rey de la fiesta) + brindis final con fuegos artificiales. ~2:00. | `generar_fiesta.py` | `salida/fiesta_01.mp4` |
| `streamer.json` | Quiz de streamer (serie) | Gancho con FOTO REAL enmarcada sobre la misma foto desenfocada, «EN DIRECTO», «QUIZ DE <NOMBRE>», «NIVEL: IMPOSIBLE»; aviso amarillo fijo arriba todo el vídeo; chat en vivo, cámara con su foto, encuesta con barras de votos, alerta «¡CORRECTA!». ~85 s. | `generar_streamer.py` | `salida/streamer_01.mp4` |
| `misterio.json` | Misterio criminal | Historia narrada con imágenes cinematográficas realistas (personajes con la misma cara), voz de thriller con emoción, pistas, cuenta atrás y final «¿QUIÉN MIENTE?» SIN revelar al culpable. Máx. 90 s. | `generar_misterio.py` | `salida/misterio_01.mp4` |

## Cómo se usa cada una

### Quizzes (`trivial`, `pareja`, `mascota`, `halloween`, `futbol`)
1. `cp plantillas-quiz/trivial.json quizzes/hora_del_quiz_NN.json` (parejas: `quizzes/pareja_NN.json`; mascotas: `quizzes/mascota_NN.json`).
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

### Niveles (`niveles`)
1. `cp plantillas-quiz/niveles.json quizzes/niveles_NN.json` y cambia `video`, `gancho` y las `rondas`
   (cada `tipo` tiene sus campos: `serie`, `filas`, `numeros`+`posicion`, `explicacion`, `hora`…).
2. `python3 generar_niveles.py quizzes/niveles_NN.json --preview 1,10,20 -o /tmp/p` (diseño gratis) →
   `--frases-pendientes` → voces (voz QUIZ) → `python3 generar_niveles.py quizzes/niveles_NN.json`.

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
- GANCHO FUERTE al principio (antes del saludo, voz y texto desde el fotograma 0). Ver `quiz-video/CLAUDE.md`.
- Entregar SOLO: el MP4, las 2 miniaturas (9:16 para Instagram/Facebook/Shorts y 3:4 para TikTok) y
  título + descripción + hashtags por plataforma (guardados en `descripciones/<video>.md`).
- Comprobar el MP4 (1080x1920, con audio, duración correcta) y revisar una hoja de fotogramas.
- Si el MP4 supera 100 MB, comprimirlo antes de subirlo a GitHub.
- Presentador fijo DON QUIZÁS para vídeos con presentador: `quizvideo/presentador.py` (ficha en
  `presentador/don_quizas_ficha.png`).
- Detalle completo de reglas y estilos: `quiz-video/CLAUDE.md`.

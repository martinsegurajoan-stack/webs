# PLANTILLA «¿QUÉ PASARÍA SI…?» INFORMATIVO EN UN SOLO PLANO (@mundo.supuesto)
Referencia: `animado/burbuja5/` (burbuja desde 1.000 m, 08-11-2026). Usar para cualquier «¿qué pasaría si…?» serio.

## Lo que pidió el usuario (correcciones de las versiones 1-4 de la burbuja)
- Narración SERIA e INFORMATIVA, narrador neutro todo el rato, SIN humor (nada de chistes ni «mirando gatos»).
- Decir de verdad lo que pasaría (datos reales y razonados: velocidades, g, lesiones, etc.).
- (usuario, 08-11-2026, vídeo del tenis) Si el supuesto es imposible o casi: decir PRIMERO por qué no podría pasar (dato real),
  después qué pasaría de verdad y con un FINAL REAL (nunca una historia que no acaba). Referencia: `animado/tenis/`.
- UN SOLO PLANO CONTINUO: la cámara sigue al protagonista todo el rato (la bola cayendo); el mundo pasa a su
  alrededor (nubes, horizonte, suelo que llega). SIN transiciones ni cortes. Nada de quitar zoom y volver a ponerlo.
- La información aparece JUNTO al protagonista (número grande debajo, chips a los lados, cotas dibujadas), poca a la vez:
  «hazlo gráficamente más sencillo, hay mucha información y mucho gráfico».
- Personaje cuidado (adulto con ropa, cara, arnés), luz de sol lateral, decorado completo (nubes, pájaros, horizonte con
  pueblo, parque con casa, árboles, valla, farola, camino, flores). Nada de gráficas con ejes ni fórmulas.
- Gancho fuerte desde el fotograma 0 (frase corta y dato enorme: «1.000 m»).
- DURACIÓN, FINAL Y BUCLE (usuario, 08-11-2026, SUSTITUYE a lo anterior): animados de 75 a 100 s. Final en seco pero NO tan brusco (la última frase se deja respirar 1-2 s y la música baja suave; nada de corte a negro de golpe). El FINAL CUADRA SIEMPRE CON EL PRINCIPIO: la última frase enlaza con la primera y el último fotograma es igual al primero (bucle invisible). SIN ruidos tipo radio/estática al final (nada de ruido blanco, golpes ni «boom» de cierre). Vídeos MUY decorados, visuales y adictivos.
  (burbuja5 es anterior a esta regla: dura 74,6 s, acaba en negro y no hace bucle; en el siguiente, aplicarla.)
- Primera palabra en 0,5 s. Marca de agua @mundo.supuesto. Subtítulos de siempre (arriba, palabra a palabra,
  recuadro azul en lo importante).

## Pasos (gastando lo mínimo)
1. `mkdir animado/NUEVO && cp -r burbuja5/{assets,mezcla.py,montar_voz.py,.gitignore,voz_el,gen.py,miniatura} NUEVO/`
   (borrar `voz_el/narrador.*`). Escribir `guion.txt` (una frase por línea, ~18-22 líneas ≈ 1.300-1.700 caracteres ≈ 75-100 s). La última frase
   enlaza con la primera (bucle) y en `gen.py` el último plano vuelve al encuadre del fotograma 0 (cambiar el fundido a negro final).
   `mezcla.py` ya no mete ruido ni «boom» al final: la música baja suave.
2. Voz: `creative_generate_speech` con TODO el guion en una llamada, voz «Juanjo Viral» `30jLfQdV8RTduXvosh02`,
   `eleven_v4`, `generations_count` 1 (~1.200 créditos). Bajar el mp3 → `voz_el/narrador.wav` (ffmpeg, mono 44,1 kHz).
3. `mkdir -p voz && python3 voz_el/partir.py && python3 voz_el/acortar.py && python3 montar_voz.py`
   Si pasa de 75 s: `atempo=1.03` a cada `voz/lN.wav` y bajar `COLA`/`EXTRA` en montar_voz.py.
4. Adaptar `gen.py`: los tiempos se toman de palabras del guion con `P("palabra", n)` (n = enésima vez que se dice)
   y `F(n)` (inicio de la frase n). Cambiar el protagonista, el mundo y los textos (`OVR`) de cada momento.
5. `python3 gen.py && python3 mezcla.py` (ajustar índices `F_[...]` de la tensión al nº de frases).
6. Revisar con UNA hoja pequeña: `npx hyperframes snapshot -o /tmp/s --no-end --at t1,t2,...` (10-12 tiempos).
7. Render: `npx -y hyperframes render -o salida/video-bruto.mp4 --quality delivery --quiet` y comprimir:
   `ffmpeg -i salida/video-bruto.mp4 -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -movflags +faststart -c:a copy salida/video-FINAL.mp4`
8. Miniatura: `node miniatura/hacer.js` (cambiar textos). Descripción en `descripciones/animado_<tema>.md`.
9. `git add -f salida/video-FINAL.mp4` (si < 100 MB) + commit + push. Entregar MP4 + miniaturas + descripción.

## Trampas técnicas de GSAP ya resueltas
- Nunca animar x/y/rotación de un elemento SVG que tenga su propio `transform="translate(...)"`: envolverlo en un
  `<g transform>` y animar el `<g>` interior (si no, desaparece o se va a 0,0).
- `svgOrigin` va en coordenadas del padre; para escalar/girar textos HTML usar `transformOrigin`.
- Contadores con nombre único (`contador()` ya lo hace). Números con punto de miles: ya formateado en `contador()`.
- Un `fromTo` con `repeat` largo pisa a otros tweens del mismo elemento: limitar su `repeat` (p. ej. la respiración).

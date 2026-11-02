# MEJORA CONTINUA — regla del usuario (02-11-2026), OBLIGATORIA en TODOS los vídeos Y PORTADAS

> «Estas mejoras aplícalas siempre. También en portadas.» (usuario, 02-11-2026)

> «Cada vídeo tiene que ser mejor que el anterior. Siento que estamos estancados. Más visual, que se vea mejor todo.
> El siguiente vídeo que te pida, mejóramelo por 1000.»

## Antes de empezar cualquier vídeo nuevo
1. Mira el último vídeo del mismo tipo (hoja de fotogramas) y escribe 5 mejoras CONCRETAS que vas a hacer.
   Díselas al usuario en una línea al entregar («Mejoras respecto al anterior: …»).
2. Elige piezas del KIT (`animado/kit/`, abajo) y úsalas: nada de hacerlo todo a mano si ya hay un componente mejor.
3. Si hace falta algo que no está, búscalo: `npx hyperframes catalog --query "<efecto en inglés>" --json` y
   `npx hyperframes add <nombre>` (dentro de `animado/kit/` o del proyecto).

## Nivel mínimo de calidad (lo que faltaba en los anteriores)
- **Primer segundo de cine**: movimiento de cámara + golpe visual (headline-slam / char-slam-explode, camera-shake,
  destello o light-leak) + sonido de impacto, todo en el fotograma 0. Nunca un plano quieto.
- **Algo nuevo cada 2-3 s** (rompe el patrón): punch-in de cámara, corte, transición (whip-pan, cinematic-zoom,
  zoom-through), cambio de encuadre, elemento que entra. Ningún plano dura más de 3 s igual.
- **Profundidad y acabado**: capas con parallax (camera-rig-depth-stack / parallax-zoom), sombras suaves, grano muy
  sutil (grain-overlay), viñeta, destellos de luz (lens-flare, vfx-anamorphic-flare) en las revelaciones.
- **Tipografía cinética** en los datos: números que ruedan (number-wheel / count-up / number-pop-in), letras que caen
  (bottom-up-letters, blur-in), texto con glitch (rgb-glitch-text) en los giros.
- **Partículas** en cada revelación importante (caption-particle-burst, confetti) y transiciones con sonido.
- **Subtítulos** más vivos (caption-pill-karaoke / caption-kinetic-slam / caption-highlight), siempre legibles.
- **Diseño de sonido**: whoosh en cada transición, riser antes de cada dato fuerte, impacto al revelar, música con
  subidas; la voz siempre por encima (ducking).
- **Imágenes reales** cuando ayuden (ElevenLabs ~212 créditos/foto: PREGUNTAR el coste antes).
- **Miniatura de póster**: personaje/objeto protagonista grande, título de 2-4 palabras enorme, contraste alto.

## Control de calidad (errores que ya pasaron: que no se repitan)
- Hoja de fotogramas cada 1 s del vídeo final y revisar UNO A UNO: textos que se pisan, cosas que salen antes de
  tiempo (P(palabra) coge la 1.ª vez que se dice), números mal formateados, elementos cortados por los bordes.
- La miniatura sin solapes y con todo dentro de 300-1620 px.

## KIT instalado (`animado/kit/compositions/`, componentes del registro de HyperFrames)
Bloques: cinematic-zoom, whip-pan, glitch, light-leak, organic-light-leak-overlay, lens-flare, vfx-anamorphic-flare,
world-map, spain-map.
Componentes (`components/`): grain-overlay, camera-shake, camera-rig-depth-stack, parallax-zoom,
zoom-through-transition, headline-slam, char-slam-explode, caption-kinetic-slam, caption-pill-karaoke,
caption-neon-glow, caption-highlight, caption-particle-burst, particle-text-dissolve, confetti, count-up,
number-wheel, number-pop-in, rgb-glitch-text, blur-in, bottom-up-letters, tilt-card.
Uso: bloque → copiar `compositions/<n>.html` al proyecto y montarlo con `data-composition-src`; componente → copiar
su HTML/estilo/script a la escena (ver el comentario de cada archivo).

## Aprendido investigando edición profesional (02-11-2026)
- Interrupción de patrón cada 2-4 s (punch-in, corte, cambio de ángulo, gráfico que salta); el gancho para el scroll y
  las siguientes interrupciones mantienen. Cada efecto con un propósito, no por poner.
- Movimiento: easing SIEMPRE (nada lineal salvo derivas), anticipación (pequeño gesto contrario antes), rebote
  al llegar (back/elastic), acción escalonada (stagger) y capas con parallax.
- Sonido: el whoosh dura lo mismo que el movimiento y acaba en golpe; el riser llega a su pico justo en el corte o
  la revelación; golpe en cada aparición; música por debajo de la voz (−6 a −12 dB cuando suenan efectos).
- Técnico HyperFrames/GSAP: en elementos SVG con `transform="translate(...)"` usar y:"-=N" (relativo) o GSAP pisa la
  posición; números con punto de miles → columnas de dígitos (no `innerHTML` con «89.300», GSAP lo hace 89,3).
- Referencia de nivel: `animado/marruecos2/` (mapa 3D inclinado, nubes en parallax, cartas VS a pantalla completa con
  números que ruedan, barridos, sellos con sacudida, ranking que se desplaza, grano, viñeta, destellos, karaoke).

## PORTADAS / MINIATURAS (siempre, mismo nivel que el vídeo)
- PÓSTER, no captura: fondo sacado del vídeo pero apagado (saturate 0.75, brightness 0.8) + viñeta y degradado.
- Título gigante con RELIEVE (sombras apiladas tipo 3D), una palabra en caja de color inclinada, colores del tema.
- Elemento central fuerte (medallón VS con banderas, personaje, objeto) + 2 siluetas grandes que lo enmarquen.
- Pegatina/nota con el dato gancho («solo 14 km de mar»), franja inferior con los temas, destellos de luz.
- Contraste alto, nada de solapes, todo dentro de 300-1620 px. Referencia: `animado/marruecos2/miniatura/hacer.js`.
- Tras el render, COMPRIMIR siempre (el grano dispara el peso: 207 MB): `ffmpeg -i video-FINAL.mp4 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -movflags +faststart -c:a copy` (GitHub no admite >100 MB).

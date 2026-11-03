# MEJORA CONTINUA — regla del usuario (02-11-2026), OBLIGATORIA en TODOS los vídeos Y PORTADAS

> «Estas mejoras aplícalas siempre. También en portadas.» (usuario, 02-11-2026)

> «Cada vídeo tiene que ser mejor que el anterior. Siento que estamos estancados. Más visual, que se vea mejor todo.
> El siguiente vídeo que te pida, mejóramelo por 1000.»

## DURACIÓN: MÍNIMO 61 s (usuario, 02-11-2026: monetización, nunca menos de 60 s)
- Guion de ~180-200 palabras; atempo de la voz ≤ 1,10. Si queda corto, bajar atempo o añadir escenas. Verificar con ffprobe.

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
- COMPARATIVAS (usuario, 02-11-2026): el VS NO ocupa toda la pantalla. Tarjeta blanca COMPACTA sobre el mapa (velo
  suave detrás): título arriba, dos columnas claras (bandera + nombre), VS pequeño entre los nombres SIN tapar nada,
  número que rueda solo cuando se dice, iconos del mismo tamaño en las dos columnas, la que gana con recuadro verde y
  pestaña «VENTAJA» junto al nombre, la que pierde se apaga; unidad («1 muñeco = 10.000») abajo. Entra desde abajo o
  desde la derecha y sale hacia el lado. Referencia: `carta()` en `animado/marruecos2/gen.py`.
- Revisar en cada escena: banderas/chinchetas que asoman por los bordes, etiquetas cortadas, nombres del mapa que
  asoman bajo los subtítulos en planos cercanos.
- `P(palabra)` coge la PRIMERA vez que se dice en TODO el guion: antes de usarla, comprobar que no sale antes (pasó con «mar» y «solo»; usar `P("solo", 2)`).

## SONIDO (usuario, 02-11-2026: «no hagas tanto ruido… empiezas con un sonido fortísimo y no se te oye»)
- LA VOZ MANDA SIEMPRE: efectos ×0,35, se apartan (−55 %) mientras habla la voz, limitador suave (tanh) y música al 7 %.
- NADA de golpes fuertes ni «boom» al empezar: el primer segundo solo voz + un whoosh suave.
- Sin ráfagas: como mucho un clic cada 0,22 s, un tic por segundo, y nunca dos golpes a la vez (separación 0,15 s).
- Final: loudnorm −14 LUFS + `alimiter=limit=0.85` + pcm_s16le. Comprobar con `volumedetect` (pico ≤ −1 dB) y que
  la voz quede 15-20 dB por encima de efectos y música (`python3 mezcla.py --stems`). Referencia: `animado/marruecos2/mezcla.py`.

## ESTILO SERIO Y PROFESIONAL (usuario, 02-11-2026, vídeo del granizo: «no lo quiero tan de dibujos, es para un niño de 5 años»)
- Nada de dibujos infantiles ni onomatopeyas escritas («TUM TUM»): estética de DOCUMENTAL / informe (fondos oscuros de
  cine, siluetas de ciudad con luces, objetos realistas con degradado y brillo, diagramas técnicos, mapas reales,
  paneles de datos, gráficas). Música ambiental grave, no pop.
- PERSONAJE SOLO SI PINTA ALGO: nada de meterlo en todas las escenas (p. ej. junto a las bolas de tamaños). Por defecto, sin personaje.
- CÁMARA: un movimiento con intención por plano (push-in, travelling, tilt), eased; nunca planos quietos.
- MONTAJE: cortes secos por defecto; como mucho 3 transiciones en todo el vídeo, solo en cambios de bloque.
- FÍSICA: lo que se acumula crece DESDE EL SUELO (el hielo no puede flotar ni dejar ver el suelo debajo).
- Referencia: `animado/granizo30/gen.py` (v2) y su miniatura.

## CERO CORRECCIONES (usuario, 02-11-2026, OBLIGATORIO)
«No me envíes el vídeo rápido y mal hecho, no importa si tardas más. Tienes que anticiparte a mis correcciones.»
Lo más importante para el usuario: 1) ESTÉTICA, 2) GANCHO, 3) GUION. Antes de enviar NADA, revisar con esta lista
(son correcciones reales que ya hizo; si alguna falla, arreglarla antes de entregar):
- GUION: directo, con tensión y pegadizo; nada de explicaciones largas ni ejemplos/casos de relleno; cada frase suma.
  Gancho sin pregunta, contundente, desde el fotograma 0 (texto grande + voz).
- NOTAS EN PANTALLA: en cristal translúcido (desenfoque + borde fino + color de acento) que case con el fondo.
  PROHIBIDO cuadros negros/opacos grandes sobre fondos de color. Decorar solo lo importante.
- DIBUJOS: calidad alta (degradados, volumen, luz). Nada que parezca diagrama simple o «de niño». Si un plano puede ser 3D
  real (avión, motor, ala, cabina), hacerlo 3D; los esquemas 2D, con fondo del mismo mundo (cielo, paisaje), no fondo plano.
- SONIDO: efectos pocos y MUY bajos, de fondo (FX_GAIN ≈ 0,16). La voz manda. Nada de golpes fuertes.
- FÍSICA Y REALISMO: nada flota, los impactos estallan de verdad (trozos con parábola, polvo, rebote), los vehículos
  se mueven con sentido (arrancan, derrapan), las nubes crecen y se mueven.
- Revisar TODOS los planos con snapshots (cada ~2 s) y mirar cada fotograma como lo miraría el usuario: encuadres
  (que el protagonista esté en plano), textos que no se partan, nada tapado, nada ridículo.
- No enviar hasta que todo lo anterior esté bien. Mejor tardar más que gastar una corrección.
- NOTAS (usuario, 02-11-2026, NORMA PRINCIPAL): las notas/recuadros NUNCA tapan a un personaje ni lo importante del plano.
  Siempre COMPACTAS (píldora pequeña, ~28 px), dinámicas (entran deslizándose y se van solas en ~2,5 s) y colocadas en
  zonas vacías. Menos estorbo, más práctico.
- CONTINUIDAD DE OBJETOS: si un objeto protagonista se repite (p. ej. la puerta), SIEMPRE el mismo diseño en todos los
  planos; nada de versiones «cutres» distintas. Puertas entreabiertas en perspectiva (la hoja gira hacia cámara), nunca
  «media puerta» plana. Si una puerta se abre en la historia, se VE la animación de apertura.
- PERSONAJES: revisar que las siluetas no se solapen/choquen (abrazos bien construidos), que nadie aparezca, desaparezca
  y reaparezca sin motivo. Textos escritos SOBRE objetos (una puerta, un papel): zoom al objeto y texto integrado
  (grabado/quemado en la superficie), nunca letras flotando.
- DOPAMINA (usuario, 02-11-2026, SIEMPRE): edición adictiva y decorada en TODOS los planos, también los que el usuario no
  ha visto: cada plano con vida (detalles que se mueven, objetos, luz, partículas, expresiones), ideas visuales bonitas,
  ritmo y sorpresa. Revisar cada rincón de cada plano (≈10 vistazos) antes de enviar. Personajes CON CARA y expresiones
  (nada de maniquíes ni siluetas negras en vídeos luminosos), manos con dedos, interfaces (móvil/banco) cuidadas y fondos
  llenos (ciudad, barrio, playa…), nunca vacíos.
- TODO EL VÍDEO +0,5 s (usuario, 02/03-11-2026, TODOS LOS VÍDEOS): la PRIMERA PALABRA empieza en 0,5 s y TODO el vídeo
  (voz, subtítulos, animaciones y cortes) se retrasa medio segundo junto, SIN desfase voz-imagen (INICIO = 0.5 en
  montar_voz.py; gen.py y mezcla.py leen tiempos.json). Motivo: habla rápido y al abrir el vídeo se pierde el primer
  segundo. El fotograma 0 ya muestra el gancho (no negro), y en ese medio segundo arranca su movimiento.
- EDIFICIOS: si se muestran muchas habitaciones, que se vea un EDIFICIO de verdad (fachada, pisos, paredes que separan,
  tejado, calle, edificios vecinos), nunca cuadrados flotando. Personajes SIEMPRE con cuello. Nadie «de pie sobre» un
  atril o un micrófono: atriles con la persona detrás. Carteles/sellos que no tapen el objeto protagonista.
- PORTADA TIKTOK: lo importante dentro del recorte 3:4 central (y 240-1680) y gancho fuerte de curiosidad.

## GUION CAÓTICO, FINAL EN SECO Y GANCHO MÁS FUERTE (usuario, 03-11-2026, TODOS los vídeos animados en adelante)
- GUION CAÓTICO Y ADICTIVO, nada aburrido ni «de documental»: escalada rápida, giros, situaciones locas y concretas que
  se ven (gente haciendo locuras, peleas por el botón, ciudades enteras en caos, cosas absurdas y graciosas), cada frase
  más fuerte que la anterior. FUERA los tramos institucionales y lentos (gobiernos, parlamentos, leyes, bancos que
  «reciben reclamaciones»…): en el vídeo del botón sobraban los gobiernos. Cada escena tiene que ser ADICTIVA.
- FINAL EN SECO Y CON EMOCIÓN: nada de cierres tipo «y el siguiente eres tú» / «ahora te toca a ti» (le aburren).
  Terminar en el punto de máxima tensión, con un golpe (giro brutal, imagen impactante, corte seco a negro en mitad
  del clímax). Si es en bucle, que el corte en seco enlace con la primera frase.
- GANCHO INICIAL MEJOR EN CADA VÍDEO: la primera frase tiene que ser la más loca/impactante de todo el vídeo
  (situación extrema o pregunta imposible de ignorar) con imagen espectacular moviéndose desde el fotograma 0.
  Revisar el gancho del vídeo anterior y superarlo.
- DURACIÓN (usuario, 03-11-2026): vídeos animados de 61 a 75 s como MÁXIMO (nunca menos de 61 s ni más de 75 s).

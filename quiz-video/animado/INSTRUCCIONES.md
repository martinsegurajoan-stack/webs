**LEE TAMBIÉN `MEJORA_CONTINUA.md` (regla del usuario 02-11-2026: cada vídeo mejor que el anterior, kit de efectos en `kit/`).**

# Vídeos animados 2D de @mundo.supuesto — TODAS las instrucciones del usuario

Léelo entero antes de hacer un vídeo de este estilo («¿Qué pasaría si…?» y cualquier historia animada para la
cuenta @mundo.supuesto). Proyecto de referencia: `quiz-video/animado/pelo5/` (cómo rehacerlo:
`quiz-video/animado/pelo5/COMO-REHACERLO.md`). Rama: `claude/tiktok-quiz-video-generator-nub6w6`.
Haz SIEMPRE `git pull` antes de empezar y `git commit` + `git push` al acabar.

## 0. REGLAS GENERALES (usuario, 01-11-2026 — SIEMPRE)
- **NUNCA generar un vídeo (ni voces, ni renders) sin que el usuario lo pida EXPRESAMENTE por escrito.** Si pregunta,
  comenta o da un consejo, solo se apunta o se responde: no se rehace nada.
- TRANSICIONES suaves y decorativas (corrección del vídeo tumbado5: «muy bruscas»): nada de cortes secos con
  oscurecido. Usar transiciones con forma y estilo (cortina/círculo que se abre, barrido con formas de color, zoom a un
  objeto que se convierte en la siguiente escena, deslizamiento con desenfoque leve…) de ~0,6-0,9 s, con un SONIDO
  acorde (whoosh suave, campanita…) que se oiga un pelín pero bajito.
- Cada vídeo se hace con TODAS las skills instaladas aplicadas al máximo (HyperFrames + registry de transiciones,
  cámara y tipografía cinética; Remotion como apoyo), y cada vídeo tiene que ser MÁS PROFESIONAL que el anterior.
- ESCENARIOS DISTINTOS según lo que se cuenta: no tiene por qué ser la misma escena todo el rato. Ej.: «¿qué pasa si
  te ingresan en el hospital?» → plano del baño cuando va al baño, la habitación, el pasillo, el quirófano… Cada
  etapa en su escenario dibujado, con transiciones con sentido entre ellos.
- ENTREGA SIEMPRE (usuario, 01-11-2026): MP4 + `miniatura_9x16.png` + DOS textos para copiar y pegar:
  1) descripción de TikTok/Instagram (subtítulos + compartir/seguir + #fyp y 3 del tema);
  2) YouTube Shorts: TÍTULO (≤100 caracteres, con #shorts) + DESCRIPCIÓN corta (gancho + suscríbete/comparte +
     #shorts y 3 del tema). Guardar ambos en `descripciones/animado_<video>.md`.

## 0b. ESTILO «PELÍCULA DE NETFLIX» (usuario, 01-11-2026, vídeo de la hormiga — PARA SIEMPRE)
- **NADA de fondos desenfocados**: el fondo se DECORA con objetos nítidos y dibujados, no se emborrona. Ningún cartel
  ni objeto del fondo puede verse borroso (p. ej. el cartel «COCINA» al principio).
- **Colores VIVOS y saturados** en todo el vídeo, como una película de animación profesional de Netflix/Pixar:
  luz cálida, sombras de color, contraste alto. Nada apagado ni gris.
- **QUE PAREZCA UNA CASA DE VERDAD**, no «un cuadrado vacío con un grifo»: cada plano lleno de objetos de casa
  (muebles, electrodomésticos, plantas, cuadros, libros, juguetes, enchufes, cables, zapatillas, alfombras,
  botes, frutas, imanes en la nevera, ventanas con vistas…). Cuantos más objetos con sentido, mejor.
- **Planos ABIERTOS**: no acercar tanto la cámara (los planos del agua y del pan estaban demasiado cerca). Alejar
  para que se vea el sitio entero (la encimera, el fregadero, la cocina…) y el personaje pequeño dentro.
- **Comparaciones VISUALES**: si se dice «tan alto como un edificio de 50 pisos», se DIBUJA el edificio de 50
  pisos bien estructurado (plantas contadas, ventanas, azotea) al lado de lo comparado.
- **NARRADOR NEUTRO** (usuario, 02-11-2026): nada de exclamaciones ni tono eufórico; un punto neutro y tranquilo todo el
  vídeo. Guion sin «¡!», sin etiquetas [excited]/[surprised]; como mucho [calm]. Adaptar el diálogo si hace falta.
- **ALEJAR LA CÁMARA SOLO LO NECESARIO** (02-11-2026): nada de enseñar la casa entera una y otra vez («súper forzado»);
  al cambiar de habitación basta con ver las dos habitaciones implicadas. La casa entera, como mucho, una vez y solo si aporta.
- **Voz con el MISMO TONO todo el rato**: NADA de [whispers] ni susurros (tampoco [dramatically] que baje la voz).
  Solo [excited]/[curious]/[surprised] con energía constante.
- **Transiciones bonitas**: el círculo de color (iris) quedó «muy poco estético». Usar transiciones con estilo:
  barrido diagonal con 2-3 franjas de colores de la marca con sombra, o la cámara viaja por la casa (paneo continuo
  de una habitación a otra), o un objeto que se acerca y tapa el plano (match cut). Siempre suaves y con sonido bajito.
- **Momentos divertidos inventados**: al cambiar de tamaño (crecer/encoger) poner una animación graciosa (cinta
  métrica o regla que sube con números de centímetros, sonido que sube de tono «uiiii», boing al final…).
- **EL PRIMER PLANO ES EL MÁS IMPORTANTE (HOOK)**: fondo espectacular, colorido, con movimiento y algo sorprendente
  desde el fotograma 0 (p. ej. zoom desde una casa enorme hasta el personaje diminuto, objetos gigantes alrededor,
  título grande). Nunca un fondo soso.
- Duración: si hace falta, hasta **105 s máximo**.
- **CASA COMPLETA EN LOS PLANOS ABIERTOS** (usuario, 02-11-2026): al alejar la cámara se ve la casa entera en corte,
  con planta de arriba (baño, cuarto infantil, despacho, música, juegos), BUHARDILLA bajo el tejado de tejas (ventana
  redonda, baúl, cajas, caballito…), chimenea con humo, SÓTANO (garaje con coche, trastero, lavadero, ping-pong) y
  jardines a los lados (árboles, valla, caseta del perro, columpio, globo y pájaros). Referencia: `hormiga2/casa_extra.py`.
- **PERSONAJE CON ARTICULACIONES** (02-11-2026): codos y rodillas, CAMINA DE PERFIL (no de frente), caras según la
  acción (frío = cara azul + dientes que castañetean + copos; miedo = sudor y piernas que tiemblan; fuerza = músculo
  y rubor…). Animales igual: el gato camina de perfil con 4 patas, cola, parpadeos. Ver `hormiga2/perfil.py` y `gato2.py`.
- **NADA de empezar con un zoom a un objeto** (usuario, 02-11-2026, «algo mejor que un zoom completo a un reloj»):
  el primer segundo tiene que tener una ACCIÓN sorprendente del propio tema (p. ej. en la hormiga: te desperezas a
  tamaño normal y ENCOGES girando con «fiuuu» y pop, y el plano se abre a la casa entera). Inventar algo así siempre.
- **SUELOS A LA MISMA ALTURA** (usuario, 02-11-2026: «está súper mal hecha la casa»): todas las habitaciones de una
  planta comparten la MISMA línea de suelo y el mismo grosor; los muebles y personajes se apoyan a la misma profundidad
  (45 px dentro de la franja del suelo) en TODAS las plantas; alfombras a la misma altura. Nada de escaleras o
  elementos que salgan de la nada. Revisar siempre con una foto de la casa entera (cámara muy alejada).
- Lo que va a ser sorpresa (el gato) NO puede verse antes de tiempo en ningún plano abierto.
- Skill instalada: `svg-character-animation` (pivotes estables, timelines por escenas, poses que se lean).
- **MINIATURA CURRADÍSIMA** (usuario, 02-11-2026: «es la primera impresión junto al primer segundo del vídeo»):
  diseñarla aparte como un póster de película: escena dibujada a propósito (no solo dos capturas), personaje grande
  con expresión exagerada, el objeto/peligro gigante, título enorme de 2-4 palabras con contorno y sombra, colores
  vivos y contraste alto, flechas/círculos que guíen la mirada, profundidad (primer plano, plano medio, fondo).
  Todo lo importante dentro de 300-1620 px de alto.
  SIN SATURAR (usuario, 02-11-2026: «un pelín más sencilla, se satura con tanto color»): fondo apagado y desaturado,
  solo los protagonistas a todo color, título blanco + un color, y como mucho un aro y una etiqueta sencillos.
- Si el usuario dice «si me quedo sin tokens déjalo pendiente»: guardar el estado en `COMO-REHACERLO.md` del
  proyecto y retomar el trabajo en cuanto se pueda, sin pedir autorización.

## 1. Cuenta y marca
- Nombre en TikTok, Instagram, Facebook y YouTube: **@mundo.supuesto**.
- Foto de perfil: `quiz-video/marca/perfil_mundo_supuesto.png` (planeta coral con anillo en bucle, fondo lila).
- Bio genérica (no hablar de «qué pasaría si» ni de «historias animadas»). La elegida:
  ```
  🌍 Lo que podría ser
  ✨ Ideas que no esperabas
  🔁 Míralo dos veces
  👇 Tú eliges el próximo
  ```
- **Marca de agua SIEMPRE**: «@mundo.supuesto» ABAJO, en HORIZONTAL, centrada, pequeña y transparente
  (en `gen.py`: `#marca` top 1775px, Inter 700 28px, blanco, opacidad 0,32). Que no moleste.

## 2. Historia y guion
- SOLO contar la historia por etapas, de principio a fin. NADA de votaciones ni «escribe X en comentarios».
- Gancho desde el fotograma 0: la pregunta del título con algo moviéndose.
- NO enumerar etapas («Uno. Mes seis…»). Decirlo directo: «A los seis meses, ¡ya tienes siete centímetros!».
- Varios ejemplos/escenarios concretos, cada uno con su representación gráfica (la puerta, la sopa…).
- Un dato sorprendente en el tramo final («lo que casi nadie sabe»).
- Final en BUCLE: la última frase enlaza con la primera y el último fotograma es igual al primero.
- Duración 60-80 s (hasta 105 s si hace falta, ver 0b).
- (ANTIGUO) Puntuación: ahora el narrador es NEUTRO, sin «¡!» (ver 0b).

## 3. Voz
- **VOZ FIJA DE ESTE FORMATO (usuario, 01-11-2026: «siempre te pediré con esta voz»):** ElevenLabs
  **«Juanjo Viral – Energetic & Punchy»**, voice_id `30jLfQdV8RTduXvosh02`, modelo `eleven_v4` (si falla,
  `eleven_multilingual_v2`), UNA toma con todo el guion (~900 créditos). Etiquetas solo [curious], [surprised],
  [excited], [warmly] (NADA de [whispers] ni [dramatically]: mismo tono siempre, ver 0b). **PROHIBIDO que se ría**: nada de [laughs], [laughs softly],
  [amused] ni [mischievously]. Ralentizar con `atempo=0.94` y trocear con `voz_el/partir.py` (revisar los cortes
  con silencedetect y corregirlos a mano en `voz_el/cortes.txt` si alguna frase queda mal). Proyecto: `animado/pelo10b/`.
- Lo de abajo (Álvaro, Sara, Piper) queda como alternativa SOLO si el usuario lo pide.
- La voz de Kokoro (em_alex) NO: al usuario le pareció horrible.
- **Opción gratis (la que quiere probar ahora el usuario):** Microsoft **es-ES-AlvaroNeural** con `edge-tts`
  (`pip install edge-tts`), tono animado: `--rate=+8% --pitch=+2Hz` como punto de partida. Antes de hacer el
  vídeo entero, pasar al usuario una PRUEBA DE UNA FRASE para que la apruebe. Generar una línea de `guion.txt` por
  archivo (`voz/lN.wav`, 44100 Hz mono) y luego `python3 montar_voz.py`.
  (En la nube de claude.ai está bloqueada: solo funciona en la sesión local).
- **Opción ElevenLabs (cuesta créditos, avisar SIEMPRE del coste antes):** «Sara Martin 3»
  (voice_id `gD1IexrzCvsXPHUuT0s3`), IDÉNTICA, sin tocar ajustes, `eleven_multilingual_v2`, UNA sola toma con
  TODO el guion en una llamada (~940 créditos). Luego `python3 voz_el/partir.py` → `montar_voz.py`.
  La narración de Sara del vídeo del pelo ya está guardada en `pelo5/voz_el/narrador.mp3` (no regenerar).
- La narración NO puede dormir: ritmo vivo, un pelín alegre y adictivo. Pausas entre frases cortas (GAP 0,12 s).

## 3b. Correcciones del usuario (vídeo de 10 años, 01-11-2026)
- Voz «un poco más lenta»: Sara Martin 3 con `eleven_v4` y ETIQUETAS de emoción por frase ([curious], [excited],
  [laughs], [whispers], [surprised], [warmly]…) para que SIENTA las exclamaciones; la locución se ralentiza con
  `ffmpeg -af atempo=0.9` antes de trocearla, y GAP 0,22 s entre frases. (~960 créditos por vídeo).
- NADA de destellos ni mareos: sin desenfoque ni giro de cámara al cambiar de etapa, sin rayos que giran, sin
  estrellitas ni puntos que parpadean. Viajes de cámara suaves (1,2 s) y solo 2 golpes de zoom suaves en todo el vídeo.
- El bucle final se hace con un CORTE limpio (oscurecido breve) al decir «con un solo pelo», no con un barrido.
- Duración máxima 80 s. Proyecto de este vídeo: `animado/pelo10/`.

## 3c. El paso del tiempo SE ENSEÑA, no se rotula (usuario, 01-11-2026)
- NO poner la línea de tiempo (HUD) en todos los vídeos: es repetitiva. Usarla solo si de verdad aporta algo.
- El tiempo se cuenta con detalles visuales dentro de la escena: zoom al reloj de pared y las agujas giran 2 horas;
  el calendario arranca hojas; la luz de la ventana pasa de día a noche; crece el pelo o la barba; se acumulan platos,
  polvo o telarañas; una planta se seca… Que se vea editado, visual, fácil de entender y adictivo.

## 3d. Línea de tiempo (HUD) — solo si se usa
- Bajo los subtítulos, una línea «0 · 1 · 3 · 5 · 7 · 10 años» con un punto que avanza y una etiqueta con la etapa
  («AÑO 3 · 45 cm», «7 AÑOS · SE PARA»…). Se aparta cuando hay una gráfica o un plano grande (récord).

## 4. Estilo visual
- Ilustración 2D cuidada y ADULTA, nada infantil («no un dibujo de niño de 4 años»).
- (ANTIGUO, ver 0b: ahora colores VIVOS y sin desenfoque) Fondo propio, colorido, CON VIDA pero tranquilo: manchas
  de luz que flotan despacio, viñeta y grano suave (SIN rayos que giran ni destellos: marean). No copiar los fondos de los vídeos de
  ejemplo del usuario.
- Un solo mundo y una sola cámara que viaja por un camino entre etapas.
- ESCENARIOS DECORADOS DEL TEMA (usuario 01-11-2026: «no una pared azul seca al fondo»): cada etapa en su set dibujado
  (dormitorio, baño, espacio, consulta, gimnasio…) con muebles y detalles; las habitaciones van seguidas como una casa
  de muñecas y la cámara pasa de una a otra. Referencia: `animado/tumbado5/`.
- LÓGICA DE LOS SITIOS (usuario 01-11-2026: «¿el universo dentro de casa?»): cada cosa en un lugar que tenga sentido.
  Dentro de casa solo lo que hay en una casa; el espacio se enseña SUBIENDO AL CIELO desde el tejado (nubes, pájaros
  y aviones que cruzan) y luego el espacio con la Tierra abajo; para cambiar de lugar se usa un corte limpio
  (`corte()` en tumbado5/gen.py). Nada de planetas pegados a una pared. Revisar también detalles como que la manta
  se quede plana cuando el personaje se levanta.
- Técnico: un movimiento de cámara tiene que TERMINAR antes del siguiente corte (si no, arrastra el plano a otro sitio).
- Personaje: HOMBRE (si el tema lo permite), proporciones de adulto, ojos con blanco y párpado, nariz definida, sin
  coloretes, ropa con sombras. Si tiene barba y pelo: de COLOR DISTINTO (barba castaño rojizo con contorno).
- El personaje NUNCA está quieto: camina hasta cada etapa (pasos alternos), se balancea, mueve cabeza y brazos, y
  gesticula con lo que se cuenta (encogerse de hombros, soplarse el flequillo, señalar…).
- Cámara: deriva suave continua y zooms naturales que encuadran lo que se cuenta; impactos solo en 1-2 momentos
  (portazo, sopa). Nada de giros ni desenfoques en los viajes. Todo debe cuadrar en el bucle.
- Animaciones con sentido físico: nada sale «de la nada» (un mechón nace de la melena; el pelo que cae sale de la
  raíz y cae hacia fuera; el pelo nuevo nace de la raíz y crece hacia arriba).

## 5. Subtítulos (estilo de la captura «Magia desde 0»)
- ARRIBA, 2 líneas centradas, letra grande de peso medio.
- Palabras aún no dichas en gris suave; la que se dice se ILUMINA en blanco y negrita (y se queda blanca).
- Lo importante se marca con un RECUADRO AZUL tipo selección de texto (borde azul fino + dos puntitos en las
  esquinas). Nada de fondos de color rellenos.

## 6. Revisión antes de entregar (obligatoria)
- `npx hyperframes snapshot` cada ~2 s de TODO el vídeo y mirar cada plano:
  - nada cortado por los bordes (y que no aparezca nada antes de que la cámara se aleje);
  - carteles que no tapen al personaje;
  - nada que se quede colgado al cambiar de escena;
  - gráficas que no se vean vacías;
  - nada flotando (el primer pelo nace del cráneo también en el fotograma 0).
- Comprobar: 1080×1920, audio AAC, sin negros, voz y subtítulos sincronizados.

## 7. Entrega (SIEMPRE, solo esto)
1. El **MP4 con subtítulos** (no hacer versión sin subtítulos).
2. Las **miniaturas** (`node miniatura/hacer.js`): `miniatura_9x16.png` + recortes exactos `miniatura_tiktok_3x4.png`
   (1080x1440) y `miniatura_instagram_4x5.png` (1080x1350). TODO lo importante (título, personajes, etiquetas,
   marca) dentro de la franja central y 300-1620 px de alto: TikTok e Instagram recortan arriba y abajo (usuario 01-11-2026).
   AL USUARIO SOLO SE LE ENVÍA `miniatura_9x16.png` (las otras no hacen falta).
3. En el mensaje, **una descripción para copiar y pegar**:
   - el texto de los subtítulos;
   - una frase que invite a COMPARTIR y a SEGUIR a @mundo.supuesto para más (antes de los hashtags);
   - 4 hashtags: #fyp + los 3 del tema que más clics tienen (buscarlos en la web).

## 8. Comunicación con el usuario
- Es nuevo en esto: explicar paso a paso y fácil.
- Avisar del coste en créditos ANTES de gastar (ElevenLabs, imágenes).
- Enviar solo lo que pide (MP4 + miniatura + descripción), sin archivos de trabajo.

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

## ACTUALIZACIÓN 08-11-2026 (manda sobre todo lo anterior)
- DURACIÓN, FINAL Y BUCLE (usuario, 08-11-2026, SUSTITUYE a lo anterior): animados de 75 a 100 s. Final en seco pero NO tan brusco (la última frase se deja respirar 1-2 s y la música baja suave; nada de corte a negro de golpe). El FINAL CUADRA SIEMPRE CON EL PRINCIPIO: la última frase enlaza con la primera y el último fotograma es igual al primero (bucle invisible). SIN ruidos tipo radio/estática al final (nada de ruido blanco, golpes ni «boom» de cierre). Vídeos MUY decorados, visuales y adictivos.
- (09-11-2026, puente) NO hacer 3D realista con perspectiva tipo el vídeo del avión («muy 3D se ve feo»). Estilo que gustó:
  MAQUETA ISOMÉTRICA PLANA (cámara ortográfica, sombreado plano de 3 tonos `MeshToonMaterial`, sin brillos), fondo gris
  carbón neutro, paleta casi monocroma (blanco/grises, agua gris azulada) y UN solo acento azul (#4ea3ff) para resaltar.
  Base reutilizable: `puente/iso.js` (estado de obra `E.st` + `aplica()` + `resalta()`) y `puente/gen.py`.
- (09-11-2026, puente v2) Usuario: «muchos sonidos molestos innecesarios» → SIN efectos de sonido (fx() vacío): solo
  voz + música suave. El narrador empieza NEUTRO desde la primera frase: etiqueta [calm] al principio, sin [curious],
  y frases iniciales unidas (no telegráficas). Más visual e interactivo: cielo azul con nubes, césped, árboles, casas,
  veleros y pájaros moviéndose, barra de PASOS de la obra que avanza, contadores animados y cámara que «respira».
- (09-11-2026, puente v3) Errores que vio el usuario: CÉSPED «bugeado» = z-fighting (caras coplanarias de dos cajas:
  nunca dos cajas con la misma cara; cámara ortográfica con near/far ajustados 1–4000, no ±6000). BARCOS que salen del
  agua y vuelven de golpe: los objetos que se mueven deben ir en BUCLE DENTRO del agua y desvanecerse en los bordes
  (nunca tl.set que teletransporte). Nubes solo arriba (abajo parece que la maqueta flota). Revisar SIEMPRE una hoja de
  fotogramas cada 4 s y recortes ampliados antes de entregar.
- (09-11-2026) EMPEZAR DIRECTO con una pregunta al espectador («¿Alguna vez te has preguntado cómo se construye…?»),
  NUNCA como si se contara una historia («Mil metros de mar…»): aburre. Primera frase = el tema del vídeo en pregunta.
- (13-11-2026, viento v2) «Parece infantil» → estándar PROFESIONAL para ilustración plana: profundidad (capas con
  parallax y bruma en el horizonte, perspectiva atmosférica: lo lejano más claro/azulado), degradados en mar/arena/hierba,
  sombras suaves, fenómenos visibles (estelas de viento, partículas, reflejo en el agua en calma), tinte de color por
  escena (niebla sepia, sequía naranja), viñeta. Mapas/planetas con DATOS REALES (Natural Earth vía world-atlas +
  d3-geo, ortográfica, con atmósfera y lado de noche), nada de continentes «manchurrón» ni iconos tipo emoji.
  Tarjetas de cristal (backdrop-filter) con barra de acento; contadores que suben; contador de progreso (DÍA n).
  Transiciones de cámara que pasen por algo (nubes al subir al espacio), nunca segundos de fondo vacío.
  Evitar triángulos/montañas gigantes detrás del personaje y bordes rectos duros (orilla, niebla).
- (13-11-2026, viento v3) Usuario: «sin dibujitos, real y serio; nada de contadores tipo "días sin viento"; textos que no
  estorben». → Estilo DOCUMENTAL DE DATOS: planeta real en canvas (Natural Earth 1:50m + d3-geo ortográfica, fondo espacio
  oscuro, atmósfera), partículas de viento deterministas (dependen de un «tiempo de viento» S.W para poder congelarlas y
  hacer bucle exacto), datos dibujados SOBRE el mapa (rutas, penachos, círculos, partículas) y rótulos mínimos sin cajas
  (kicker azul + texto fino con sombra). Vuelos de cámara: alejar → girar → acercar (nunca zoom a mitad de océano).
  Narración: datos MUY sorprendentes y comprensibles (Londres vs Nueva York, olas de la Antártida a Alaska, Bodélé…).
- (13-11-2026, viento v5) «Se ve pobre/cutre» → planeta 3D REAL con three.js y texturas NASA Blue Marble (día, luces
  nocturnas, nubes, máscara de océano; sacadas gratis de los paquetes npm `three-globe` y `earth-visualization`) en
  `viento/assets/tierra/`, shader propio: terminador día/noche, luces de ciudades, brillo del mar, atmósfera, nubes con luz.
  IMPORTANTE: desde file:// WebGL bloquea imágenes locales → incrustarlas en base64 (data URI) y crear las THREE.Texture
  SOLO cuando todas las <img> estén completas (si no: «Offset overflows texture dimensions»). Las <img> con display:none.
  Plantilla reutilizable: `viento/_plantilla.html` + `viento/gen.py`.
- (13-11-2026, uñas v2) Usuario: «represéntalo con un muñeco y que se vean los problemas del día a día». → Mezclar
  primer plano realista (canvas) con ESCENAS DEL MUÑECO (_rig.py) viviendo cada problema (sofá con el móvil, espejo,
  moneda, cama, zapato), alternando con un fundido (S.vista). Uñas del muñeco = trazos con stroke-dashoffset (pathLength
  100) dentro de P_manoN/P_manoF. Al sentar/tumbar: ocultar P_sombra y colocar la cadera a la altura del asiento.
- (13-11-2026, calvos) PROHIBIDO empezar con «¿Qué pasaría si…?» → gancho directo en 2.ª persona («¿Y si mañana te
  despertaras sin…? Ni tú, ni nadie. Nunca más.»). PROHIBIDO el final tipo «Así que, aunque no lo parezca… Ahora imagina…»
  o preguntas de cierre: acabar con el DATO MÁS SORPRENDENTE dicho con pausa («…que ni los ves.»).
- (13-11-2026) TRAMPA: una excepción a mitad de frame() en canvas (p. ej. ellipse con radio negativo al parpadear) deja
  save/clip/filter sin cerrar y estropea TODO el render aunque las capturas sueltas salgan bien. Antes de renderizar,
  recorrer el timeline entero cada 0,04 s comprobando que no hay errores, y empezar frame() con `cv.width = cv.width`.

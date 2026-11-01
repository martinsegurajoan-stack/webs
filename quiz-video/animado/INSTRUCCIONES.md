# Vídeos animados 2D de @mundo.supuesto — TODAS las instrucciones del usuario

Léelo entero antes de hacer un vídeo de este estilo («¿Qué pasaría si…?» y cualquier historia animada para la
cuenta @mundo.supuesto). Proyecto de referencia: `quiz-video/animado/pelo5/` (cómo rehacerlo:
`quiz-video/animado/pelo5/COMO-REHACERLO.md`). Rama: `claude/tiktok-quiz-video-generator-nub6w6`.
Haz SIEMPRE `git pull` antes de empezar y `git commit` + `git push` al acabar.

## 0. REGLAS GENERALES (usuario, 01-11-2026 — SIEMPRE)
- Cada vídeo se hace con TODAS las skills instaladas aplicadas al máximo (HyperFrames + registry de transiciones,
  cámara y tipografía cinética; Remotion como apoyo), y cada vídeo tiene que ser MÁS PROFESIONAL que el anterior.
- ESCENARIOS DISTINTOS según lo que se cuenta: no tiene por qué ser la misma escena todo el rato. Ej.: «¿qué pasa si
  te ingresan en el hospital?» → plano del baño cuando va al baño, la habitación, el pasillo, el quirófano… Cada
  etapa en su escenario dibujado, con transiciones con sentido entre ellos.
- ENTREGA SIEMPRE: MP4 + miniatura para TikTok/Instagram + descripción para copiar y pegar.

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
- Duración 60-80 s.
- Puntuación que dé vida a la voz: «¡…!» en los datos fuertes y «…» para crear intriga.

## 3. Voz
- **VOZ FIJA DE ESTE FORMATO (usuario, 01-11-2026: «siempre te pediré con esta voz»):** ElevenLabs
  **«Juanjo Viral – Energetic & Punchy»**, voice_id `30jLfQdV8RTduXvosh02`, modelo `eleven_v4` (si falla,
  `eleven_multilingual_v2`), UNA toma con todo el guion (~900 créditos). Etiquetas solo [curious], [surprised],
  [excited], [whispers], [dramatically], [warmly]. **PROHIBIDO que se ría**: nada de [laughs], [laughs softly],
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

## 3c. Línea de tiempo (HUD)
- Bajo los subtítulos, una línea «0 · 1 · 3 · 5 · 7 · 10 años» con un punto que avanza y una etiqueta con la etapa
  («AÑO 3 · 45 cm», «7 AÑOS · SE PARA»…). Se aparta cuando hay una gráfica o un plano grande (récord).

## 4. Estilo visual
- Ilustración 2D cuidada y ADULTA, nada infantil («no un dibujo de niño de 4 años»).
- Fondo propio, neutro y fijo (no cambia de escenario), colorido pero apagado (lila), CON VIDA pero tranquilo: manchas
  de luz que flotan despacio, viñeta y grano suave (SIN rayos que giran ni destellos: marean). No copiar los fondos de los vídeos de
  ejemplo del usuario.
- Un solo mundo y una sola cámara que viaja por un camino entre etapas.
- ESCENARIOS DECORADOS DEL TEMA (usuario 01-11-2026: «no una pared azul seca al fondo»): cada etapa en su set dibujado
  (dormitorio, baño, espacio, consulta, gimnasio…) con muebles y detalles; las habitaciones van seguidas como una casa
  de muñecas y la cámara pasa de una a otra. Referencia: `animado/tumbado5/`.
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

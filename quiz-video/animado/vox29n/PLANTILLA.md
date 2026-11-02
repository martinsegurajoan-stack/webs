# PLANTILLA «¿Y si gana <PARTIDO>?» en 60 segundos (estilo libreta, adultos)

Formato pedido por el usuario (02-11-2026) para hacer la serie con todos los partidos:
- Presentación «te lo cuento en 60 segundos» + CRONÓMETRO pequeño contando de 60 a 0 todo el vídeo.
- ESTILO CLARO Y DECORATIVO (usuario 02-11-2026: «fondo más claro, más blanco, que no sea una libreta literal»):
  fondo blanco roto con puntitos y formas suaves del color del partido, TARJETAS blancas con banda de color arriba y
  cintas decorativas, que se deslizan fuera al cambiar de tema; subtítulos oscuros. Dentro de cada tarjeta: notas escritas a mano que se escriben solas con un boli, títulos
  en rotulador del COLOR DEL PARTIDO (suavizado, que se vea pero sin saturar), subrayados, círculos y tachones a mano,
  bocetos a tinta solo donde ayudan (cartera, casa, tarta, mujer embarazada, mapa, edificio, Europa, balanza, urna,
  hemiciclo), pasar página de libreta de espiral con sonido de papel, fuente de los datos en cada página.
- Narrador neutro (Juanjo, [calm]), palabras sencillas, datos reales y verificados (buenos y malos), ≤ 60 s.
- Miniatura sobria: hoja de libreta con logo, «¿Y SI GANA / PARTIDO?» en el color del partido, «29-N» rodeado y
  cronómetro «60s».

## Variedad visual (usuario, 02-11-2026: «que no sea todo el rato escribiendo en la libreta»)
- Cámara que respira (empuje lento por página) y pequeño golpe de zoom en cada dato.
- Pósits amarillos con la CIFRA clave que caen sobre la página (`posit` en partido.json).
- Sello «PROPUESTA / DATOS / OPINIONES» en la esquina de cada tema (`sello`).
- Papel distinto según la página (rayas o cuadrícula: `papel`).
- RECORTES a pantalla completa que saltan sobre la mesa y salen (`recorte`): gráfico de barras impreso o ficha de
  prensa (solo con datos reales y su fuente; nunca titulares inventados).
- Mesa con vida: café con vapor, gafas, luz de flexo.

## Hacer otro partido
1. Copia esta carpeta: `cp -r animado/vox29n animado/<partido>29n` (y borra `salida/`, `voz/`, `.hyperframes/`).
2. `assets/logo_partido.png`: el logo que mande el usuario (recortado y con fondo transparente, ver comando en el historial).
3. `partido.json`: `partido`, `color` (suavizado), `color_claro`, `portada` y las `paginas` (cada una con `lineas` del
   guion, `titulo`, `notas` con la palabra `cuando` aparece, `boceto` y `fuente`). `clave` = palabras con recuadro.
4. `guion.txt` (≈170 palabras = 60 s) con datos verificados en la web (encuestas, programa, cifras oficiales).
5. Voz: ElevenLabs Juanjo `30jLfQdV8RTduXvosh02`, eleven_v4, «[calm]» al principio, una toma (~1.000 créditos).
   `ffmpeg -af atempo=1.08` si pasa de 60 s → `python3 voz_el/partir.py` → `python3 montar_voz.py`.
6. `python3 gen.py` → `python3 mezcla.py` → `npx -y hyperframes render -o salida/video-FINAL.mp4 --quality delivery`.
7. `node miniatura/hacer.js` → `miniatura/miniatura_9x16.png`. Textos en `descripciones/<partido>29n.md`.
Componentes del registro instalados (HyperFrames): hw-boil, hw-underline, hw-arrow, hw-box-label, marker-highlight,
cursor-annotate, marker-checklist-card (fuentes Caveat, Permanent Marker y Courier Prime en assets/fonts).

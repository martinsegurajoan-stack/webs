# Formato «¿QUÉ PASARÍA SI…?» GEOPOLÍTICO en 60 s (infografía animada) — usuario 02-11-2026
Pedido: «de este estilo (serie política), un poco más animado, que no sea de escribir; ni 2D como el del niño ni libreta;
comparativas (soldados, maquinaria…), súper adictivo desde el primer segundo (imagen + gancho de guion), datos en notitas».
- Fondo = MAPA vectorial (lon/lat → mundo en `gen.py`) con cámara que viaja (zoom al Estrecho, vista general, Ceuta/Melilla).
- Gancho desde el fotograma 0: título grande «¿Y SI … ?» + banderas VS, lanchas que cruzan, radar, regla «14 km», «?».
- PANEL VS blanco que sube desde abajo: banderas, contador que cuenta (miles con <span>.</span> para que GSAP no lo
  convierta en decimal), iconos que aparecen (1 icono = N), etiqueta «VENTAJA», ranking con barra 1.º-145.º.
- NOTITAS amarillas (posit) con cada dato y su FUENTE. Cuenta atrás 60 s audible, subtítulos con recuadro, marca de agua.
- Voz Juanjo `[calm]` una toma (~1.000 créditos), atempo para ≤ 60 s. Ojo: `P(palabra)` busca la 1.ª vez que se dice
  (usar `P("mar", 2)` si la palabra ya salió antes). Lo que aparece más tarde lleva `style="opacity:0"` en el HTML.
- `python3 gen.py` → `python3 mezcla.py` → render → `node miniatura/hacer.js` (captura del gancho + pegatina «60 s»).

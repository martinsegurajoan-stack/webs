// Maqueta 3D del puente colgante: fondo neutro, corte de mar transparente (se ven cimientos y fondo marino),
// torres coral con arcos, cables plateados. Expone window.ESC con cámara, piezas y resaltado.
(function () {
  const W = 1080, H = 1920;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1); renderer.setSize(W, H);
  renderer.outputEncoding = THREE.sRGBEncoding; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 0.92;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.localClippingEnabled = true;
  document.getElementById('gl').appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  const cam = new THREE.PerspectiveCamera(34, W / H, 1, 20000);

  scene.add(new THREE.HemisphereLight(0xcfdcf0, 0x2a2e36, 0.5));
  const sol = new THREE.DirectionalLight(0xfff4e6, 1.35); sol.position.set(-900, 1400, 900); sol.castShadow = true;
  sol.shadow.mapSize.set(2048, 2048); Object.assign(sol.shadow.camera, { left: -1400, right: 1400, top: 900, bottom: -900, near: 10, far: 4000 }); scene.add(sol);
  const contra = new THREE.DirectionalLight(0x9fc8ff, 0.45); contra.position.set(900, 500, -1200); scene.add(contra);

  const M = (c, o = {}) => new THREE.MeshStandardMaterial(Object.assign({ color: c, roughness: 0.6, metalness: 0.05 }, o));
  const sombra = (m) => { m.castShadow = true; m.receiveShadow = true; return m; };

  // ---------------- dimensiones de la maqueta
  const SPAN = 1000, TX = SPAN / 2, TH = 240, DECK = 78, LARGO = 1500, FONDO = 420, PROF = 120;   // PROF = profundidad del mar
  const ANCLA = LARGO / 2 + 90;
  const base = new THREE.Group(); scene.add(base);

  // ---------------- corte de terreno y mar (diorama)
  const rocaMat = M(0x6a5d55, { roughness: 0.95 });
  const arenaMat = M(0xb8925e, { roughness: 1 });
  function tierra(signo) {
    const g = new THREE.Group();
    const w = 520;
    const capas = [[0x4a3e3a, -PROF - 60, 60], [0x6a5a50, -PROF, PROF - 4], [0x5fa04a, -4, 10]];
    capas.forEach(([c, y, h]) => { const b = sombra(new THREE.Mesh(new THREE.BoxGeometry(w, h, FONDO), M(c, { roughness: 0.95 }))); b.position.set(signo * (LARGO / 2 + w / 2 - 40), y + h / 2, 0); g.add(b); });
    // acantilado con escalones suaves hacia el agua
    for (let i = 0; i < 4; i++) { const b = sombra(new THREE.Mesh(new THREE.BoxGeometry(40, PROF - i * 22, FONDO), M(0x7a6a5e, { roughness: 0.95 }))); b.position.set(signo * (LARGO / 2 - 40 - i * 34), -PROF + (PROF - i * 22) / 2, 0); g.add(b); }
    base.add(g);
  }
  tierra(1); tierra(-1);
  // fondo marino con capas en el corte
  const lecho = sombra(new THREE.Mesh(new THREE.BoxGeometry(LARGO, 30, FONDO), arenaMat)); lecho.position.set(0, -PROF - 15, 0); base.add(lecho);
  const roca = sombra(new THREE.Mesh(new THREE.BoxGeometry(LARGO + 1040, 60, FONDO), rocaMat)); roca.position.set(0, -PROF - 60, 0); base.add(roca);
  for (let i = 0; i < 40; i++) { const p = new THREE.Mesh(new THREE.DodecahedronGeometry(6 + Math.random() * 10, 0), M(0x8a7a6a, { flatShading: true })); p.position.set(-LARGO / 2 + Math.random() * LARGO, -PROF, -FONDO / 2 + Math.random() * FONDO); base.add(p); }
  // algas
  for (let i = 0; i < 26; i++) { const a = new THREE.Mesh(new THREE.ConeGeometry(3, 30 + Math.random() * 30, 5), M(0x3fa66b, { roughness: 0.8 })); a.position.set(-LARGO / 2 + 60 + Math.random() * (LARGO - 120), -PROF + 18, -FONDO / 2 + Math.random() * FONDO); base.add(a); }
  // agua: volumen transparente + superficie con brillo
  const aguaMat = new THREE.MeshPhysicalMaterial({ color: 0x0a8fb0, transparent: true, opacity: 0.62, roughness: 0.15, metalness: 0.0, transmission: 0.0, depthWrite: false, side: THREE.DoubleSide });
  const agua = new THREE.Mesh(new THREE.BoxGeometry(LARGO, PROF, FONDO), aguaMat); agua.position.set(0, -PROF / 2, 0); agua.renderOrder = 5; base.add(agua);
  const supMat = new THREE.MeshStandardMaterial({ color: 0x2ec6dc, transparent: true, opacity: 0.45, roughness: 0.08, metalness: 0.35, depthWrite: false });
  const sup = new THREE.Mesh(new THREE.PlaneGeometry(LARGO, FONDO, 60, 20), supMat); sup.rotation.x = -Math.PI / 2; sup.position.y = 0.5; sup.renderOrder = 6; base.add(sup);
  const ondas = new THREE.Mesh(new THREE.PlaneGeometry(LARGO, FONDO), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.0, depthWrite: false })); base.add(ondas);
  // canal de navegación marcado (boyas)
  const boyas = new THREE.Group();
  for (const s of [-1, 1]) for (let z = -160; z <= 160; z += 80) { const b = new THREE.Mesh(new THREE.CylinderGeometry(4, 5, 12, 10), M(s > 0 ? 0x35d987 : 0xff5a4f)); b.position.set(s * 230, 4, z); boyas.add(b); }
  base.add(boyas);

  // ---------------- cimientos (cajones de hormigón hasta la roca) — se ven bajo el agua
  const cajMat = M(0xd9dee4, { roughness: 0.75 });
  const cimientos = [];
  for (const s of [-1, 1]) {
    const gc = new THREE.CylinderGeometry(46, 52, PROF + 70, 32); gc.translate(0, (PROF + 70) / 2, 0);
    const c = sombra(new THREE.Mesh(gc, cajMat)); c.position.set(s * TX, -PROF - 64, 0); base.add(c); cimientos.push(c);
    const cap = sombra(new THREE.Mesh(new THREE.CylinderGeometry(50, 50, 12, 32), M(0x9aa2ac))); cap.position.set(s * TX, 6, 0); base.add(cap); c.userData.cap = cap;
  }

  // ---------------- torres coral con arcos (el «aro» de arriba)
  const coral = M(0xff4f3a, { roughness: 0.42, metalness: 0.1 });
  const torres = [], arcos = [];
  function torre(x) {
    const g = new THREE.Group();
    const sh = new THREE.Shape();
    const wb = 30, wt = 24, h = TH;
    sh.moveTo(-wb - 8, 0); sh.lineTo(wb + 8, 0); sh.lineTo(wt + 6, h); sh.lineTo(-wt - 6, h); sh.lineTo(-wb - 8, 0);
    const hueco = (y0, y1, ww) => { const p = new THREE.Path(); p.moveTo(-ww, y0); p.lineTo(ww, y0); p.lineTo(ww, y1 - ww); p.absarc(0, y1 - ww, ww, 0, Math.PI, false); p.lineTo(-ww, y0); return p; };
    sh.holes.push(hueco(DECK + 14, 150, 18)); sh.holes.push(hueco(162, 222, 15));
    const geo = new THREE.ExtrudeGeometry(sh, { depth: 14, bevelEnabled: true, bevelSize: 2, bevelThickness: 2, bevelSegments: 2 });
    geo.translate(0, 0, -7); geo.rotateY(Math.PI / 2);
    for (const z of [-22, 22]) { const m = sombra(new THREE.Mesh(geo, coral)); m.position.z = z; g.add(m); }
    // vigas entre las dos caras y remate
    for (const y of [DECK - 4, 154, 226]) { const v = sombra(new THREE.Mesh(new THREE.BoxGeometry(16, 10, 44), coral)); v.position.set(0, y, 0); g.add(v); }
    const sillin = sombra(new THREE.Mesh(new THREE.BoxGeometry(22, 10, 56), M(0x2c3038, { metalness: 0.6, roughness: 0.3 }))); sillin.position.set(0, TH + 6, 0); g.add(sillin);
    g.position.x = x; base.add(g); torres.push(g); arcos.push(g.children[0], g.children[1]);
    return g;
  }
  torre(-TX); torre(TX);

  // ---------------- tablero (cajón aerodinámico) con carriles
  const tablero = new THREE.Group(); base.add(tablero);
  const dovelas = [];
  const NDOV = 26, LDOV = (2 * ANCLA) / NDOV;
  for (let i = 0; i < NDOV; i++) {
    const d = new THREE.Group();
    const caja = sombra(new THREE.Mesh(new THREE.BoxGeometry(LDOV - 1.5, 8, 34), M(0x5a6270, { roughness: 0.5, metalness: 0.3 }))); d.add(caja);
    const asf = new THREE.Mesh(new THREE.BoxGeometry(LDOV - 1.5, 0.6, 30), M(0x2c3038, { roughness: 0.9 })); asf.position.y = 4.3; d.add(asf);
    for (const z of [-5, 5]) { const l = new THREE.Mesh(new THREE.BoxGeometry(LDOV * 0.5, 0.4, 0.8), new THREE.MeshBasicMaterial({ color: 0xffffff })); l.position.set(0, 4.7, z); d.add(l); }
    const amar = new THREE.Mesh(new THREE.BoxGeometry(LDOV - 1.5, 0.4, 0.8), new THREE.MeshBasicMaterial({ color: 0xffc24a })); amar.position.set(0, 4.7, 0); d.add(amar);
    for (const z of [-17, 17]) { const b = new THREE.Mesh(new THREE.BoxGeometry(LDOV - 1.5, 3, 0.8), M(0xd8dde4)); b.position.set(0, 6, z); d.add(b); }
    d.position.set(-ANCLA + LDOV * (i + 0.5), DECK, 0); tablero.add(d); dovelas.push(d);
  }

  // ---------------- cables principales y péndolas
  const cableMat = M(0xe6ebf2, { roughness: 0.25, metalness: 0.85 });
  const yCable = (x) => {
    const ax = Math.abs(x);
    if (ax <= TX) return (DECK + 12) + (TH + 6 - (DECK + 12)) * Math.pow(ax / TX, 2);
    const u = (ax - TX) / (ANCLA - TX); return (TH + 6) + (12 - (TH + 6)) * u;
  };
  const cables = [], pendolas = [];
  for (const z of [-22, 22]) {
    const pts = []; for (let i = 0; i <= 200; i++) { const x = -ANCLA + 2 * ANCLA * i / 200; pts.push(new THREE.Vector3(x, yCable(x), z)); }
    const c = sombra(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 400, 2.4, 10, false), cableMat)); base.add(c); cables.push(c);
    for (let x = -TX + 25; x < TX; x += 25) {
      const h = yCable(x) - (DECK + 4);
      const p = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, h, 4), cableMat); p.position.set(x, DECK + 4 + h / 2, z); base.add(p); pendolas.push(p);
    }
  }
  // anclajes (macizos de hormigón en tierra)
  const anclajes = [];
  for (const s of [-1, 1]) { const a = sombra(new THREE.Mesh(new THREE.BoxGeometry(80, 60, 90), M(0xa8afb8, { roughness: 0.85 }))); a.position.set(s * ANCLA, 26, 0); base.add(a); anclajes.push(a); }

  // ---------------- barco (gálibo)
  const barco = new THREE.Group();
  const casco = sombra(new THREE.Mesh(new THREE.BoxGeometry(110, 16, 26), M(0x2c3e5e))); casco.position.y = 4; barco.add(casco);
  const proa = sombra(new THREE.Mesh(new THREE.ConeGeometry(13, 30, 4), M(0x2c3e5e))); proa.rotation.z = -Math.PI / 2; proa.rotation.x = Math.PI / 4; proa.position.set(68, 4, 0); barco.add(proa);
  const castillo = sombra(new THREE.Mesh(new THREE.BoxGeometry(20, 26, 22), M(0xf2f4f7))); castillo.position.set(-38, 25, 0); barco.add(castillo);
  [0xff5a4f, 0x35a3d9, 0xffc24a, 0x3fa66b, 0x7a5bd6].forEach((c, i) => { const b = sombra(new THREE.Mesh(new THREE.BoxGeometry(14, 12, 22), M(c))); b.position.set(-16 + i * 16, 18, 0); barco.add(b); });
  barco.position.set(0, 0, 560); barco.rotation.y = Math.PI / 2; scene.add(barco);

  // ---------------- piezas de la construcción
  const brillo = (c, op = 1) => new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: op, depthWrite: false });
  const curva = (z, dy = 0) => { const p = []; for (let i = 0; i <= 200; i++) { const x = -ANCLA + 2 * ANCLA * i / 200; p.push(new THREE.Vector3(x, yCable(x) + dy, z)); } return new THREE.CatmullRomCurve3(p); };
  const piloto = new THREE.Mesh(new THREE.TubeGeometry(curva(-22, 3), 400, 0.9, 6, false), brillo(0xffd27a)); base.add(piloto);
  const pasarelas = []; for (const z of [-22, 22]) { const p = new THREE.Mesh(new THREE.TubeGeometry(curva(z, -6), 300, 3.5, 4, false), brillo(0x9aa2ac, 0.0)); p.scale.z = 1; base.add(p); pasarelas.push(p); }
  const ruedas = []; for (const z of [-22, 22]) { const r = new THREE.Mesh(new THREE.TorusGeometry(7, 2, 8, 20), brillo(0xffd27a)); base.add(r); ruedas.push(r); const h = new THREE.Mesh(new THREE.SphereGeometry(16, 16, 16), brillo(0xffc24a, 0.25)); r.add(h); }
  const dron = new THREE.Group(); { const c = new THREE.Mesh(new THREE.BoxGeometry(14, 4, 14), M(0x2c3038)); dron.add(c); for (const [a, b] of [[-10, -10], [10, -10], [-10, 10], [10, 10]]) { const h = new THREE.Mesh(new THREE.CylinderGeometry(6, 6, 0.6, 16), brillo(0xffffff, 0.5)); h.position.set(a, 3, b); dron.add(h); } const l = new THREE.Mesh(new THREE.SphereGeometry(2, 8, 8), brillo(0x35d987)); l.position.y = -3; dron.add(l); } base.add(dron);
  // luces del puente (de noche no, solo puntos cálidos al final)
  const lamparas = []; for (let x = -ANCLA + 20; x <= ANCLA; x += 45) for (const z of [-17, 17]) { const l = new THREE.Mesh(new THREE.SphereGeometry(1.8, 8, 8), brillo(0xfff0c0, 0)); l.position.set(x, DECK + 12, z); base.add(l); lamparas.push(l); }
  const balizas = torres.map(t => { const b = new THREE.Mesh(new THREE.SphereGeometry(4, 12, 12), brillo(0xff3a2a, 0)); b.position.set(t.position.x, TH + 16, 0); base.add(b); return b; });
  // coches
  const coches = []; const cocheCol = [0xff5a4f, 0x35a3d9, 0xffc24a, 0xf2f4f7, 0x3fa66b, 0x7a5bd6, 0x2c3038];
  for (let i = 0; i < 18; i++) { const dir = i % 2 ? 1 : -1; const c = new THREE.Group(); const b = new THREE.Mesh(new THREE.BoxGeometry(12, 4, 6), M(cocheCol[i % 7], { roughness: 0.3, metalness: 0.4 })); b.position.y = 2; c.add(b); const t = new THREE.Mesh(new THREE.BoxGeometry(7, 3, 5.4), M(0x1d2433)); t.position.set(-1, 5, 0); c.add(t); c.userData = { dir, off: Math.random() * 2 * ANCLA, v: 60 + Math.random() * 30 }; c.position.set(0, DECK + 4.6, dir * 7.5); base.add(c); coches.push(c); }
  // barcaza con la dovela que sube
  const barcaza = new THREE.Group(); { const c = sombra(new THREE.Mesh(new THREE.BoxGeometry(70, 10, 46), M(0x3a4250))); c.position.y = 2; barcaza.add(c); } base.add(barcaza);
  const izado = new THREE.Group(); for (const z of [-12, 12]) { const l = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 1, 4), brillo(0xffd27a)); l.position.z = z; izado.add(l); } base.add(izado);
  // pilar fantasma (lo que NO se hace)
  const fantasma = new THREE.Mesh(new THREE.CylinderGeometry(40, 48, PROF + DECK + 60, 24), new THREE.MeshBasicMaterial({ color: 0xff5a4f, transparent: true, opacity: 0, depthWrite: false })); fantasma.position.set(0, (DECK - PROF) / 2 - 30, 0); base.add(fantasma);
  // flujo de fuerzas: partículas que recorren tablero → péndola → cable → torre → cimiento / anclaje
  const rutas = [];
  for (const s of [-1, 1]) {
    const pts = [new THREE.Vector3(s * 150, DECK + 4, 22), new THREE.Vector3(s * 150, yCable(s * 150), 22)];
    for (let i = 0; i <= 20; i++) { const x = s * (150 + (TX - 150) * i / 20); pts.push(new THREE.Vector3(x, yCable(x), 22)); }
    const ramaT = [...pts, new THREE.Vector3(s * TX, 0, 22), new THREE.Vector3(s * TX, -PROF - 60, 22)];
    const ramaA = [...pts]; for (let i = 1; i <= 12; i++) { const x = s * (TX + (ANCLA - TX) * i / 12); ramaA.push(new THREE.Vector3(x, yCable(x), 22)); }
    rutas.push(new THREE.CatmullRomCurve3(ramaT, false, 'catmullrom', 0.0), new THREE.CatmullRomCurve3(ramaA, false, 'catmullrom', 0.0));
  }
  const parts = []; for (let r = 0; r < rutas.length; r++) for (let k = 0; k < 14; k++) { const p = new THREE.Mesh(new THREE.SphereGeometry(4.5, 10, 10), brillo(0xffc24a, 0)); p.userData = { r, k }; base.add(p); parts.push(p); }
  const ORDEN = dovelas.map((d, i) => i).sort((a, b) => Math.abs(dovelas[a].position.x) - Math.abs(dovelas[b].position.x));
  const ORDENP = pendolas.map((p, i) => i).sort((a, b) => Math.abs(pendolas[a].position.x) - Math.abs(pendolas[b].position.x));
  const pmat = cables[0].material;
  const st = { cim: 1, tor: 1, pil: 0, pas: 0, hilo: 1, anc: 1, pen: 1, dov: 1, asf: 1, luz: 1, agua: 0.62, vien: 0, fza: 0, fzT: 0, barcoZ: 560, fan: 0, t: 0, coches: 1, rueda: 0 };
  function aplica() {
    cimientos.forEach(c => { c.position.y = -PROF - 64 + (1 - st.cim) * 150; c.visible = st.cim > 0.005; c.userData.cap.visible = st.cim > 0.98; });
    torres.forEach(t => { t.scale.y = Math.max(0.001, st.tor); t.visible = st.tor > 0.001; });
    balizas.forEach(b => b.material.opacity = st.luz);
    const nIdx = piloto.geometry.index.count; piloto.geometry.setDrawRange(0, Math.floor(nIdx * Math.min(1, st.pil))); piloto.visible = st.pil > 0 && st.hilo < 0.99;
    const pf = piloto.geometry.parameters.path.getPointAt(Math.min(0.999, Math.max(0.001, st.pil))); dron.position.set(pf.x, pf.y + 14, pf.z); dron.visible = st.pil > 0.01 && st.pil < 0.999;
    pasarelas.forEach(p => { p.material.opacity = 0.75 * st.pas * (1 - st.hilo); p.visible = st.pas > 0; });
    ruedas.forEach((r, i) => { const u = 0.5 + 0.5 * Math.sin(st.rueda * Math.PI * 2 * 3 + i); const p = cables[0].geometry.parameters.path.getPointAt(Math.min(0.999, Math.max(0.001, u))); r.position.set(p.x, p.y + 4, i ? 22 : -22); r.rotation.y = Math.PI / 2; r.visible = st.pas > 0.5 && st.hilo < 0.99; });
    cables.forEach(c => { c.visible = st.hilo > 0.02; c.material.transparent = st.hilo < 1; c.material.opacity = st.hilo; c.scale.set(1, 1, 1); });
    anclajes.forEach(a => { a.scale.y = Math.max(0.001, st.anc); a.position.y = 26 * st.anc; a.visible = st.anc > 0.01; });
    const np = Math.floor(st.pen * pendolas.length); pendolas.forEach((p, i) => p.visible = false); for (let k = 0; k < np; k++) pendolas[ORDENP[k]].visible = true;
    const nd = st.dov * dovelas.length, ent = Math.floor(nd), frac = nd - ent;
    dovelas.forEach(d => d.visible = false);
    for (let k = 0; k < ent; k++) { const d = dovelas[ORDEN[k]]; d.visible = true; d.position.y = DECK; }
    barcaza.visible = false; izado.visible = false;
    if (ent < dovelas.length && st.dov > 0 && st.dov < 1) {
      const d = dovelas[ORDEN[ent]]; d.visible = true; const y0 = 14; d.position.y = y0 + (DECK - y0) * Math.min(1, frac * 1.25);
      barcaza.visible = true; barcaza.position.set(d.position.x, 0, 0);
      izado.visible = true; izado.position.set(d.position.x, 0, 0); const top = yCable(d.position.x); izado.children.forEach(l => { const h = top - d.position.y; l.scale.y = Math.max(1, h); l.position.y = d.position.y + h / 2; });
    }
    tablero.children.forEach(d => { d.children[1].visible = st.asf > 0.5; d.children[2].visible = d.children[3].visible = d.children[4].visible = st.asf > 0.5; });
    lamparas.forEach(l => l.material.opacity = st.luz);
    tablero.position.z = Math.sin(st.t * 0.9) * 9 * st.vien; tablero.rotation.x = Math.sin(st.t * 0.9 + 0.5) * 0.015 * st.vien;
    coches.forEach(c => { const u = c.userData; c.visible = st.coches > 0.5 && st.dov >= 1; let x = ((u.off + u.dir * u.v * st.t) % (2 * ANCLA) + 2 * ANCLA) % (2 * ANCLA) - ANCLA; c.position.x = x; c.position.z = u.dir * 7.5 + tablero.position.z; c.rotation.y = u.dir > 0 ? 0 : Math.PI; });
    aguaMat.opacity = st.agua; sup.material.opacity = Math.min(0.45, st.agua * 0.72);
    barco.position.z = st.barcoZ;
    fantasma.material.opacity = st.fan;
    parts.forEach(p => { const u = p.userData; const c = rutas[u.r]; const v = ((st.fzT * 0.35 + u.k / 14) % 1); p.position.copy(c.getPointAt(v)); p.material.opacity = st.fza * (0.35 + 0.65 * Math.sin(v * Math.PI)); });
  }
  // ---------------- resaltado: contorno de luz sobre cualquier pieza
  const resMat = new THREE.LineBasicMaterial({ color: 0x4fd1ff, transparent: true, opacity: 0 });
  function resalta(objs) {
    const g = new THREE.Group();
    objs.forEach(o => {
      o.updateMatrixWorld(true);
      const e = new THREE.LineSegments(new THREE.EdgesGeometry(o.geometry, 25), resMat.clone());
      e.matrixAutoUpdate = false; e.matrix.copy(o.matrixWorld); g.add(e);
      const halo = new THREE.Mesh(o.geometry, new THREE.MeshBasicMaterial({ color: 0x4fd1ff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
      halo.matrixAutoUpdate = false; halo.matrix.copy(o.matrixWorld); g.add(halo);
    });
    scene.add(g);
    return { g, set(v) { g.children.forEach((c, i) => { c.material.opacity = c.isLineSegments ? v : v * 0.45; }); } };
  }
  function proyecta(v3) { const v = v3.clone().project(cam); return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H]; }

  window.ESC = { st, aplica, piloto, rutas, ruedas, barcaza, fantasma, renderer, scene, cam, base, agua, aguaMat, sup, cimientos, torres, arcos, tablero, dovelas, cables, pendolas, anclajes, barco, resalta, proyecta,
    TX, TH, DECK, PROF, ANCLA, yCable, render() { renderer.render(scene, cam); } };
})();

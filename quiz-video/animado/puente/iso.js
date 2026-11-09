// Maqueta isométrica del puente colgante (three.js r149, cámara ortográfica). Paleta sobria, sombras suaves.
(function () {
  const W = 1080, H = 1920;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1); renderer.setSize(W, H);
  renderer.outputEncoding = THREE.sRGBEncoding; renderer.toneMapping = THREE.NoToneMapping;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.getElementById('gl').appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  const FR = 900;                                   // mitad de la altura visible (zoom)
  const cam = new THREE.OrthographicCamera(-FR * W / H, FR * W / H, FR, -FR, -6000, 6000);
  scene.add(new THREE.HemisphereLight(0xe6e6e6, 0x4a4a4a, 0.5));
  const sol = new THREE.DirectionalLight(0xffffff, 1.05); sol.position.set(-700, 1300, 900); sol.castShadow = true;
  sol.shadow.mapSize.set(2048, 2048); Object.assign(sol.shadow.camera, { left: -1300, right: 1300, top: 1000, bottom: -1000, near: 10, far: 4000 }); sol.shadow.radius = 2; sol.shadow.bias = -0.0005;
  scene.add(sol); scene.add(sol.target);
  // sombreado plano tipo ilustración: 3 tonos por cara, sin brillos ni degradados realistas
  const GRAD = (() => { const d = new Uint8Array([90, 170, 255]); const t = new THREE.DataTexture(d, 3, 1, THREE.RedFormat); t.minFilter = t.magFilter = THREE.NearestFilter; t.needsUpdate = true; return t; })();
  const M = (c, o = {}) => { const { roughness, metalness, ...r } = o; return new THREE.MeshToonMaterial(Object.assign({ color: c, gradientMap: GRAD }, r)); };
  const S = (m) => { m.castShadow = true; m.receiveShadow = true; return m; };
  const caja = (w, h, d, mat, x, y, z) => { const m = S(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)); m.position.set(x, y, z); return m; };
  const base = new THREE.Group(); scene.add(base);

  // ---------------- medidas
  const SPAN = 900, TX = SPAN / 2, TH = 300, DECK = 96, LEN = 1300, D = 360, PROF = 130, LAND = 300;
  const ANCLA = LEN / 2 + 120;
  const C = { blanco: 0xf3f1ed, hueso: 0xe7e3dc, gris: 0x8d939b, pizarra: 0x3d434c, arena: 0xbfa77c, roca: 0x8c6a4c, rocaO: 0x6b4f39, hierba: 0x7fb85b, agua: 0x3f9ccc, acento: 0xef5b3b };

  // ---------------- maqueta: bloques de tierra con capas, fondo marino y agua
  for (const s of [-1, 1]) {
    const cx = s * (LEN / 2 + LAND / 2 - 2);
    base.add(caja(LAND, 60, D, M(C.rocaO), cx, -PROF - 50, 0));
    base.add(caja(LAND, PROF + 20, D, M(C.roca), cx, -PROF / 2 - 10 + 10, 0));
    base.add(caja(LAND, 14, D, M(C.hierba), cx, 6, 0));
    for (const y of [-30, -62, -94]) base.add(caja(LAND + 1, 2, D + 1, M(0x7d5c42), cx, y, 0));
    base.add(caja(LAND - 30, 2, 46, M(C.pizarra, { roughness: 0.9 }), cx + s * 10, 14, 0));
    // talud hacia el agua
    const t = S(new THREE.Mesh(new THREE.BoxGeometry(70, PROF, D), M(C.roca))); t.position.set(s * (LEN / 2 - 30), -PROF / 2 + 2, 0); t.rotation.z = s * 0.22; base.add(t);
    // árboles discretos
    for (let k = 0; k < 16; k++) {
      const tr = new THREE.Group(); const h = 30 + (k % 3) * 10;
      tr.add(S(new THREE.Mesh(new THREE.CylinderGeometry(2.5, 3, 12, 6), M(0x7a5a3c))));
      const cop = S(new THREE.Mesh(new THREE.IcosahedronGeometry(h * 0.45, 0), M(k % 2 ? 0x4f9a48 : 0x67ad52, { flatShading: true }))); cop.position.y = h * 0.6; tr.add(cop);
      { const zz = -D / 2 + 22 + ((k * 91) % (D - 44)); if (Math.abs(zz) < 34) continue; tr.position.set(s * (LEN / 2 + 50 + (k * 53) % 230), 14, zz); } tr.scale.setScalar(0.8 + (k % 4) * 0.12); base.add(tr);
    }
  }
  base.add(caja(LEN, 60, D, M(C.rocaO), 0, -PROF - 50, 0));
  base.add(caja(LEN, 22, D, M(C.arena), 0, -PROF - 9, 0));
  for (let k = 0; k < 30; k++) { const p = S(new THREE.Mesh(new THREE.DodecahedronGeometry(5 + (k % 4) * 3, 0), M(C.roca, { flatShading: true }))); p.position.set(-LEN / 2 + 40 + (k * 173) % (LEN - 80), -PROF + 2, -D / 2 + 20 + (k * 61) % (D - 40)); base.add(p); }
  const aguaMat = new THREE.MeshStandardMaterial({ color: C.agua, transparent: true, opacity: 0.8, roughness: 0.2, metalness: 0.0, depthWrite: false });
  const ag = new THREE.BoxGeometry(LEN - 4, PROF - 4, D - 4); const colA = [], cTop = new THREE.Color(0x2a86bf), cBot = new THREE.Color(0x0c3d66);
  for (let k = 0; k < ag.attributes.position.count; k++) { const y = ag.attributes.position.getY(k); const c = cBot.clone().lerp(cTop, (y + PROF / 2) / PROF); colA.push(c.r, c.g, c.b); }
  ag.setAttribute('color', new THREE.Float32BufferAttribute(colA, 3)); aguaMat.vertexColors = true; aguaMat.color.set(0xffffff);
  const agua = new THREE.Mesh(ag, aguaMat); agua.position.set(0, -PROF / 2 - 4, 0); agua.renderOrder = 10; base.add(agua);
  const supMat = new THREE.MeshStandardMaterial({ color: 0x2e8bc4, transparent: true, opacity: 0.82, roughness: 0.05, metalness: 0.1, depthWrite: false });
  const sup = new THREE.Mesh(new THREE.PlaneGeometry(LEN - 4, D - 4, 1, 1), supMat); sup.rotation.x = -Math.PI / 2; sup.position.y = -5; sup.renderOrder = 11; base.add(sup);
  // líneas de oleaje suaves en la superficie
  const olas = new THREE.Group(); for (let k = 0; k < 26; k++) { const o = new THREE.Mesh(new THREE.PlaneGeometry(40 + (k % 5) * 18, 2), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.45, depthWrite: false })); o.rotation.x = -Math.PI / 2; o.position.set(-LEN / 2 + 60 + (k * 211) % (LEN - 120), -4.5, -D / 2 + 20 + (k * 47) % (D - 40)); olas.add(o); } base.add(olas);

  { const cv = document.createElement('canvas'); cv.width = cv.height = 256; const x = cv.getContext('2d'); const g = x.createRadialGradient(128, 128, 10, 128, 128, 128); g.addColorStop(0, 'rgba(0,0,0,0.55)'); g.addColorStop(1, 'rgba(0,0,0,0)'); x.fillStyle = g; x.fillRect(0, 0, 256, 256);
    const sh = new THREE.Mesh(new THREE.PlaneGeometry(LEN + 2 * LAND + 500, D + 500), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(cv), transparent: true, depthWrite: false })); sh.rotation.x = -Math.PI / 2; sh.position.y = -PROF - 82; base.add(sh); }
  // ---------------- cimientos (cajones)
  const cimientos = [];
  for (const s of [-1, 1]) {
    const g = new THREE.CylinderGeometry(44, 50, PROF + 40, 40); g.translate(0, (PROF + 40) / 2, 0);
    const c = S(new THREE.Mesh(g, M(C.hueso))); c.position.set(s * TX, -PROF - 38, 0); base.add(c); cimientos.push(c);
  }
  // ---------------- torres: cara trapezoidal con tres arcos huecos (extruida) + remate
  const torres = [], huecos = [];
  const matT = M(C.blanco, { roughness: 0.55 });
  const niveles = [[DECK + 22, TH * 0.47], [TH * 0.52, TH * 0.74], [TH * 0.79, TH - 26]];
  function torre(x) {
    const g = new THREE.Group();
    const wb = 46, wt = 34, leg = 15;
    const sh = new THREE.Shape(); sh.moveTo(-wb, 0); sh.lineTo(wb, 0); sh.lineTo(wt, TH); sh.lineTo(-wt, TH); sh.lineTo(-wb, 0);
    const half = (y) => (wb + (wt - wb) * y / TH) - leg;
    for (const [y0, y1] of niveles) {
      const w0 = Math.min(half(y0), half(y1)); const r = w0;
      const p = new THREE.Path(); p.moveTo(-w0, y0); p.lineTo(w0, y0); p.lineTo(w0, y1 - r); p.absarc(0, y1 - r, r, 0, Math.PI, false); p.lineTo(-w0, y0); sh.holes.push(p);
    }
    const geo = new THREE.ExtrudeGeometry(sh, { depth: 16, bevelEnabled: true, bevelSize: 2.5, bevelThickness: 2.5, bevelSegments: 3, curveSegments: 24 });
    geo.translate(0, 0, -8); geo.rotateY(Math.PI / 2);
    g.add(S(new THREE.Mesh(geo, matT)));
    // base ancha y remate con silla del cable
    g.add(caja(30, 10, wb * 2 + 14, M(C.hueso), 0, 5, 0));
    g.add(caja(26, 10, wt * 2 + 16, M(C.hueso), 0, TH + 5, 0));
    for (const z of [-30, 30]) g.add(caja(20, 10, 16, M(C.pizarra, { roughness: 0.4, metalness: 0.4 }), 0, TH + 14, z));
    for (const [y0, y1] of niveles) {
      const hueco = new THREE.Mesh(new THREE.PlaneGeometry(2 * Math.min(half(y0), half(y1)), y1 - y0), new THREE.MeshBasicMaterial({ color: C.acento, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false }));
      hueco.position.set(0, (y0 + y1) / 2, 0); hueco.rotation.y = Math.PI / 2; g.add(hueco); huecos.push(hueco);
    }
    // luz roja de aviso arriba
    const b = new THREE.Mesh(new THREE.SphereGeometry(3, 10, 10), new THREE.MeshBasicMaterial({ color: 0xf3f1ed })); b.position.y = TH + 24; g.add(b);
    g.position.x = x; base.add(g); torres.push(g); return g;
  }
  torre(-TX); torre(TX);
  // espuma alrededor de las torres
  for (const s2 of [-1, 1]) { const e = new THREE.Mesh(new THREE.TorusGeometry(56, 3, 6, 40), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.55, depthWrite: false })); e.rotation.x = Math.PI / 2; e.position.set(s2 * TX, -4, 0); base.add(e); }
  // ---------------- tablero (tramos)
  const dovelas = []; const NDOV = 24; const LD = (2 * ANCLA) / NDOV;
  for (let i = 0; i < NDOV; i++) {
    const d = new THREE.Group();
    d.add(caja(LD - 0.6, 12, 56, M(C.blanco, { roughness: 0.5 }), 0, 0, 0));
    d.add(caja(LD - 0.6, 3, 57, M(C.gris), 0, -6.5, 0));
    const asf = caja(LD - 0.6, 1.2, 46, M(C.pizarra, { roughness: 0.9 }), 0, 6.6, 0); d.add(asf);
    for (const z of [-7, 7]) { const linea = new THREE.Mesh(new THREE.BoxGeometry(LD * 0.45, 0.4, 1), new THREE.MeshBasicMaterial({ color: 0xe9e6df })); linea.position.set(0, 7.4, z); d.add(linea); }
    for (const z of [-26, 26]) { d.add(caja(LD - 0.6, 5, 1.6, M(C.hueso), 0, 9.5, z)); }
    const far = new THREE.Mesh(new THREE.SphereGeometry(1.8, 8, 8), new THREE.MeshBasicMaterial({ color: 0x9a9a9a })); far.position.set(0, 16, 25); d.add(far);
    d.userData = { asf, far, lineas: d.children.filter(o => o.material && o.material.type === 'MeshBasicMaterial' && o !== far), x0: -ANCLA + LD * (i + 0.5) };
    d.position.set(-ANCLA + LD * (i + 0.5), DECK, 0); base.add(d); dovelas.push(d);
  }
  // ---------------- cables y péndolas
  const yC = (x) => { const ax = Math.abs(x); if (ax <= TX) return (DECK + 16) + (TH + 6 - (DECK + 16)) * (ax / TX) ** 2; const u = (ax - TX) / (ANCLA - TX); return (TH + 6) + (20 - (TH + 6)) * u; };
  const cabMat = M(0xd6d9de, { roughness: 0.35, metalness: 0.6 });
  const cables = [], pendolas = [];
  for (const z of [-30, 30]) {
    const pts = []; for (let i = 0; i <= 200; i++) { const x = -ANCLA + 2 * ANCLA * i / 200; pts.push(new THREE.Vector3(x, yC(x), z)); }
    const c = S(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 400, 3.6, 12, false), cabMat)); base.add(c); cables.push(c);
    for (let x = -ANCLA + 60; x < ANCLA - 40; x += 22) { if (Math.abs(Math.abs(x) - TX) < 10) continue; const h = yC(x) - DECK - 5; if (h < 6) continue; const p = new THREE.Mesh(new THREE.CylinderGeometry(0.75, 0.75, h, 5), cabMat); p.position.set(x, DECK + 5 + h / 2, z); base.add(p); pendolas.push(p); }
  }
  const anclajes = []; for (const s of [-1, 1]) { const sh = new THREE.Shape(); sh.moveTo(-50, 0); sh.lineTo(50, 0); sh.lineTo(30, 52); sh.lineTo(-30, 30); sh.lineTo(-50, 0);
    const g = new THREE.ExtrudeGeometry(sh, { depth: 100, bevelEnabled: true, bevelSize: 2, bevelThickness: 2, bevelSegments: 2 }); g.translate(0, 0, -50);
    const a = S(new THREE.Mesh(g, M(C.hueso))); a.position.set(s * ANCLA, 12, 0); a.scale.x = -s; base.add(a); anclajes.push(a); }

  // ---------------- barco
  const barco = new THREE.Group();
  barco.add(caja(140, 18, 34, M(C.pizarra), 0, 6, 0)); barco.add(caja(26, 30, 30, M(C.blanco), -48, 30, 0));
  [0x8d939b, 0xe7e3dc, 0x8d939b, 0xe7e3dc].forEach((c, i) => barco.add(caja(20, 16, 30, M(c), -18 + i * 22, 23, 0)));
  barco.position.set(0, -3, 260); barco.rotation.y = Math.PI / 2; base.add(barco);

  // ================= DECORADO VIVO: casas, veleros, pájaros
  for (const s of [-1, 1]) for (let k = 0; k < 3; k++) {
    const h = new THREE.Group(); const w = 34 + k * 6;
    h.add(caja(w, 22, 28, M(0xf6f1e7), 0, 11, 0));
    const tj = new THREE.Mesh(new THREE.CylinderGeometry(0, 24, 16, 4), M(k % 2 ? 0xc96f4a : 0x5d7b96, { flatShading: true })); tj.rotation.y = Math.PI / 4; tj.scale.set(w / 34, 1, 0.82); tj.position.y = 30; S(tj); h.add(tj);
    h.position.set(s * (LEN / 2 + LAND - 60 - k * 70), 14, (k % 2 ? 1 : -1) * (110 + k * 12)); base.add(h);
  }
  const veleros = [[-240, 0.9], [240, 0.6], [80, 1.1]].map(([x, v], k) => { const g = new THREE.Group(); g.add(caja(34, 7, 12, M(0xf6f1e7), 0, 2, 0));
    const vg = new THREE.BufferGeometry(); vg.setAttribute('position', new THREE.Float32BufferAttribute([0, 6, 0, 0, 46, 0, 22, 6, 0, 0, 6, 0, -14, 6, 0, 0, 40, 0], 3)); vg.computeVertexNormals();
    g.add(S(new THREE.Mesh(vg, new THREE.MeshToonMaterial({ color: 0xffffff, side: THREE.DoubleSide, gradientMap: GRAD })))); g.rotation.y = Math.PI / 2; g.position.x = x; g.userData = { v, k }; base.add(g); return g; });
  const pajaros = Array.from({ length: 7 }, (_, k) => { const g = new THREE.Group(); const mat = new THREE.MeshBasicMaterial({ color: 0x2b3440, side: THREE.DoubleSide });
    const a1 = new THREE.Mesh(new THREE.PlaneGeometry(9, 2.2), mat); a1.position.x = -4.5; const a2 = a1.clone(); a2.position.x = 4.5; const p1 = new THREE.Group(); p1.add(a1); const p2 = new THREE.Group(); p2.add(a2);
    g.add(p1, p2); g.userData = { p1, p2, k }; g.rotation.x = -Math.PI / 2; base.add(g); return g; });
  // ================= ESTADO DE OBRA (0 = sin construir, 1 = terminado) =================
  const ACC = 0x4ea3ff;
  const st = { t: 0, cim: 1, tor: 1, pil: 0, pas: 0, rueda: 0, ruedaOn: 0, hilo: 1, anc: 1, pen: 1, dov: 1, asf: 1, luz: 0, coches: 0, fza: 0, vien: 0, agua: 1, barcoZ: 260, fan: 0 };
  // cable piloto + dron
  const curva = (z, dy = 0) => new THREE.CatmullRomCurve3(Array.from({ length: 201 }, (_, i) => { const x = -ANCLA + 2 * ANCLA * i / 200; return new THREE.Vector3(x, yC(x) + dy, z); }));
  const pilGeo = new THREE.TubeGeometry(curva(0, 2), 400, 0.9, 6, false); const pilIdx = pilGeo.index.count;
  const piloto = new THREE.Mesh(pilGeo, new THREE.MeshBasicMaterial({ color: 0xffffff })); base.add(piloto);
  const dron = new THREE.Group(); dron.add(caja(10, 3, 10, M(C.pizarra), 0, 0, 0));
  const rotores = []; for (const [a, b] of [[-8, -8], [8, -8], [-8, 8], [8, 8]]) { const r = new THREE.Mesh(new THREE.CylinderGeometry(5, 5, 0.6, 16), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.6 })); r.position.set(a, 2.5, b); dron.add(r); rotores.push(r); }
  base.add(dron);
  // pasarela (barandillas siguiendo el cable) y rueda de hilado
  const pasMat = new THREE.MeshBasicMaterial({ color: 0xbfc3c8, transparent: true, opacity: 0 });
  const pasarela = new THREE.Group(); for (const z of [-38, -22, 22, 38]) pasarela.add(new THREE.Mesh(new THREE.TubeGeometry(curva(z, -4), 300, 0.6, 4, false), pasMat)); base.add(pasarela);
  const ruedas = []; for (const z of [-30, 30]) { const r = new THREE.Mesh(new THREE.TorusGeometry(7, 1.6, 8, 24), new THREE.MeshBasicMaterial({ color: ACC })); base.add(r); ruedas.push([r, z]); }
  // cables en tres grosores (hilado progresivo)
  const finos = [1.1, 2.2].map(rad => { const m = new THREE.Group(); for (const z of [-30, 30]) m.add(new THREE.Mesh(new THREE.TubeGeometry(curva(z), 300, rad, 8, false), cabMat)); base.add(m); return m; });
  // pilar fantasma (lo que NO se hace)
  const fan = new THREE.Mesh(new THREE.CylinderGeometry(40, 46, PROF + DECK + 30, 32), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, depthWrite: false }));
  fan.position.set(0, (DECK - PROF) / 2 - 10, 0); fan.renderOrder = 12; base.add(fan);
  // barcazas bajo los tramos que se izan
  const barcazas = [0, 1].map(() => { const b = new THREE.Group(); b.add(caja(LD + 10, 8, 70, M(C.pizarra), 0, 0, 0)); b.add(caja(6, 50, 6, M(0x9a9a9a), -LD / 2, 29, 30)); base.add(b); return b; });
  // coches
  const coches = Array.from({ length: 14 }, (_, k) => { const c = caja(14, 6, 8, M(k % 3 ? 0xd8d8d8 : 0x6c6c6c), 0, 0, 0); base.add(c); return c; });
  // flujo de fuerzas (puntos que viajan por el cable)
  const puntos = Array.from({ length: 28 }, () => { const p = new THREE.Mesh(new THREE.SphereGeometry(4, 10, 10), new THREE.MeshBasicMaterial({ color: ACC, transparent: true })); base.add(p); return p; });
  // halos de farolas
  const halos = dovelas.map(d => { const h = new THREE.Mesh(new THREE.SphereGeometry(6, 10, 10), new THREE.MeshBasicMaterial({ color: 0xfff6e0, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })); h.position.set(0, 16, 25); d.add(h); return h; });
  const ordenD = dovelas.map((d, i) => i).sort((a, b) => Math.abs(dovelas[a].userData.x0) - Math.abs(dovelas[b].userData.x0));
  const rangoD = []; ordenD.forEach((i, k) => rangoD[i] = Math.floor(k / 2));
  const ordenP = pendolas.map((p, i) => i).sort((a, b) => Math.abs(pendolas[a].position.x) - Math.abs(pendolas[b].position.x));
  const rangoP = []; ordenP.forEach((i, k) => rangoP[i] = k / pendolas.length);
  const cl = (v) => Math.max(0, Math.min(1, v)); const ease = (v) => v * v * (3 - 2 * v);
  const surf = supMat.opacity, aguaOp = aguaMat.opacity;
  const hemi = scene.children.find(o => o.isHemisphereLight);
  function aplica() {
    const t = st.t;
    olas.children.forEach((o, k) => { o.position.z = -D / 2 + 20 + ((k * 47 + t * 9) % (D - 40)); });
    // cimientos: bajan desde la superficie hasta la roca
    cimientos.forEach(c => { c.visible = st.cim > 0.001; c.position.y = -10 + (-PROF - 38 + 10) * ease(cl(st.cim)); });
    torres.forEach(g => { g.visible = st.tor > 0.005; g.scale.y = Math.max(0.005, ease(cl(st.tor))); });
    // piloto + dron
    const np = Math.floor(cl(st.pil) * pilIdx / 6) * 6; pilGeo.setDrawRange(0, np); piloto.visible = st.pil > 0.001 && st.hilo < 0.999;
    dron.visible = st.pil > 0.001 && st.pil < 0.999; { const x = -ANCLA + 2 * ANCLA * cl(st.pil); dron.position.set(x, yC(x) + 16 + 3 * Math.sin(t * 5), 0); rotores.forEach(r => r.rotation.y = t * 40); }
    pasMat.opacity = cl(st.pas) * 0.9; pasarela.visible = st.pas > 0.01;
    ruedas.forEach(([r, z]) => { const f = st.rueda % 2, u = f < 1 ? f : 2 - f; const x = -ANCLA + 2 * ANCLA * (0.04 + 0.92 * u); r.position.set(x, yC(x) + 2, z); r.rotation.y = Math.PI / 2; r.rotation.x = t * 8; r.visible = st.ruedaOn > 0.5; });
    finos[0].visible = st.hilo > 0.001 && st.hilo < 0.4; finos[1].visible = st.hilo >= 0.4 && st.hilo < 0.8; cables.forEach(c => c.visible = st.hilo >= 0.8);
    anclajes.forEach(a => { a.visible = st.anc > 0.005; a.scale.y = Math.max(0.005, ease(cl(st.anc))); });
    pendolas.forEach((p, i) => { const v = cl((st.pen - rangoP[i]) * 6); p.visible = v > 0.001; p.scale.y = Math.max(0.001, v); p.position.y = yC(p.position.x) - p.geometry.parameters.height * v / 2; });
    // tablero: del centro hacia fuera, izado desde barcazas
    const nR = Math.ceil(dovelas.length / 2), sw = Math.sin(t * 2.3);
    const bz = [];
    dovelas.forEach((d, i) => {
      const p = cl(st.dov * (nR + 1) - rangoD[i]); const x0 = d.userData.x0; const suelo = Math.abs(x0) < LEN / 2 ? 0 : 20;
      d.visible = p > 0.001; d.position.y = suelo + (DECK - suelo) * ease(cl(p * 1.15));
      d.position.z = st.vien * 14 * sw * Math.cos(Math.PI * x0 / (2 * ANCLA));
      if (p > 0.001 && p < 1 && Math.abs(x0) < LEN / 2) bz.push(x0);
      const a = cl((st.asf * (nR + 1)) - rangoD[i]); d.userData.asf.visible = a > 0.5; d.userData.lineas.forEach(l => l.visible = a > 0.5);
      d.userData.far.material.color.setHex(st.luz > 0.5 ? 0xfff6e0 : 0x9a9a9a);
    });
    halos.forEach(h => h.material.opacity = st.luz * 0.55);
    barcazas.forEach((b, k) => { b.visible = k < bz.length; if (k < bz.length) b.position.set(bz[k], -1, 0); });
    coches.forEach((c, k) => { const L = 2 * ANCLA - 60; const dir = k % 2 ? 1 : -1; const u = ((t * 70 + k * 157) % L); c.position.set(dir > 0 ? -L / 2 + u : L / 2 - u, DECK + 10, dir * 11 + (Math.sin(t * 2.3) * st.vien * 14 * Math.cos(Math.PI * (u - L / 2) / (2 * ANCLA)))); c.visible = st.coches > 0.5; });
    puntos.forEach((p, k) => { const s = k % 2 ? 1 : -1, z = (k >> 1) % 2 ? 30 : -30; const u = ((t * 0.35 + (k >> 2) / 7) % 1); const x = s * u * ANCLA; p.position.set(x, yC(x) + 1, z); p.visible = st.fza > 0.01; p.material.opacity = st.fza * Math.sin(Math.PI * u); });
    fan.material.opacity = st.fan * 0.35; fan.visible = st.fan > 0.01;
    aguaMat.opacity = aguaOp * st.agua; supMat.opacity = surf * st.agua; olas.visible = st.agua > 0.5;
    barco.position.z = st.barcoZ;
    veleros.forEach(g => { const { v, k } = g.userData; g.position.set(g.position.x, -3 + Math.sin(t * 2 + k) * 1.2, ((t * 14 * v + k * 120) % (D - 50)) - (D - 50) / 2); g.rotation.z = Math.sin(t * 1.6 + k) * 0.06; g.visible = st.agua > 0.5; });
    pajaros.forEach(g => { const { p1, p2, k } = g.userData; const u = ((t * 0.045 + k * 0.137) % 1); g.position.set(-900 + u * 1800, 360 + (k % 3) * 22 + Math.sin(t + k) * 6, -120 + (k * 47) % 240); const f = Math.sin(t * 9 + k) * 0.6; p1.rotation.y = f; p2.rotation.y = -f; });
    sol.intensity = 1.05 - 0.3 * st.luz; hemi.intensity = 0.5 - 0.12 * st.luz;
  }
  // resaltado azul pulsante sobre un conjunto de piezas
  function resalta(lista) {
    const mats = []; lista.forEach(o => o.traverse(m => { if (m.isMesh && m.material && m.material.emissive) { m.material = m.material.clone(); mats.push(m.material); } }));
    return { set(v) { mats.forEach(mm => { mm.emissive.setHex(ACC); mm.emissiveIntensity = v * 0.9; }); } };
  }
  const hueR = { set(v) { huecos.forEach(h => { h.material.color.setHex(ACC); h.material.opacity = v * 0.55; }); } };
  function proyecta(v3) { const v = v3.clone().project(cam); return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H]; }
  function pon(px, py, pz, tx, ty, tz, zoom) {
    cam.position.set(px, py, pz); cam.lookAt(tx, ty, tz); cam.zoom = zoom; cam.updateProjectionMatrix();
  }
  window.ESC = { st, aplica, resalta, hueR, renderer, scene, cam, base, agua, aguaMat, sup, olas, cimientos, torres, huecos, dovelas, cables, pendolas, anclajes, barco, proyecta, pon,
    TX, TH, DECK, PROF, ANCLA, LEN, D, yC, C, render() { renderer.render(scene, cam); } };
})();

// Maqueta isométrica del puente colgante (three.js r149, cámara ortográfica). Paleta sobria, sombras suaves.
(function () {
  const W = 1080, H = 1920;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1); renderer.setSize(W, H);
  renderer.outputEncoding = THREE.sRGBEncoding; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 0.78;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.getElementById('gl').appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  const FR = 900;                                   // mitad de la altura visible (zoom)
  const cam = new THREE.OrthographicCamera(-FR * W / H, FR * W / H, FR, -FR, -6000, 6000);
  scene.add(new THREE.HemisphereLight(0xdfe6ee, 0x4a4540, 0.5));
  const sol = new THREE.DirectionalLight(0xfff1e0, 1.5); sol.position.set(-700, 1300, 900); sol.castShadow = true;
  sol.shadow.mapSize.set(2048, 2048); Object.assign(sol.shadow.camera, { left: -1300, right: 1300, top: 1000, bottom: -1000, near: 10, far: 4000 }); sol.shadow.radius = 6; sol.shadow.bias = -0.0005;
  scene.add(sol); scene.add(sol.target);
  const M = (c, o = {}) => new THREE.MeshStandardMaterial(Object.assign({ color: c, roughness: 0.75, metalness: 0.0 }, o));
  const S = (m) => { m.castShadow = true; m.receiveShadow = true; return m; };
  const caja = (w, h, d, mat, x, y, z) => { const m = S(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)); m.position.set(x, y, z); return m; };
  const base = new THREE.Group(); scene.add(base);

  // ---------------- medidas
  const SPAN = 900, TX = SPAN / 2, TH = 300, DECK = 96, LEN = 1300, D = 360, PROF = 130, LAND = 300;
  const ANCLA = LEN / 2 + 120;
  const C = { blanco: 0xf3f1ed, hueso: 0xe7e3dc, gris: 0x8d939b, pizarra: 0x3d434c, arena: 0xa8875a, roca: 0x6b5d50, rocaO: 0x3f3731, hierba: 0x6c7a4c, agua: 0x1f5c6b, acento: 0xef5b3b };

  // ---------------- maqueta: bloques de tierra con capas, fondo marino y agua
  for (const s of [-1, 1]) {
    const cx = s * (LEN / 2 + LAND / 2 - 2);
    base.add(caja(LAND, 60, D, M(C.rocaO), cx, -PROF - 50, 0));
    base.add(caja(LAND, PROF + 20, D, M(C.roca), cx, -PROF / 2 - 10 + 10, 0));
    base.add(caja(LAND, 14, D, M(C.hierba), cx, 6, 0));
    for (const y of [-30, -62, -94]) base.add(caja(LAND + 1, 2, D + 1, M(0x4f453c), cx, y, 0));
    base.add(caja(LAND - 30, 2, 46, M(C.pizarra, { roughness: 0.9 }), cx + s * 10, 14, 0));
    // talud hacia el agua
    const t = S(new THREE.Mesh(new THREE.BoxGeometry(70, PROF, D), M(C.roca))); t.position.set(s * (LEN / 2 - 30), -PROF / 2 + 2, 0); t.rotation.z = s * 0.22; base.add(t);
    // árboles discretos
    for (let k = 0; k < 7; k++) {
      const tr = new THREE.Group(); const h = 30 + (k % 3) * 10;
      tr.add(S(new THREE.Mesh(new THREE.CylinderGeometry(2.5, 3, 12, 6), M(0x8a7a66))));
      const cop = S(new THREE.Mesh(new THREE.IcosahedronGeometry(h * 0.45, 0), M(0x6f7f58, { flatShading: true }))); cop.position.y = h * 0.6; tr.add(cop);
      tr.position.set(s * (LEN / 2 + 60 + (k * 37) % 220), 14, -D / 2 + 30 + ((k * 91) % (D - 60))); base.add(tr);
    }
  }
  base.add(caja(LEN, 60, D, M(C.rocaO), 0, -PROF - 50, 0));
  base.add(caja(LEN, 22, D, M(C.arena), 0, -PROF - 9, 0));
  for (let k = 0; k < 30; k++) { const p = S(new THREE.Mesh(new THREE.DodecahedronGeometry(5 + (k % 4) * 3, 0), M(C.roca, { flatShading: true }))); p.position.set(-LEN / 2 + 40 + (k * 173) % (LEN - 80), -PROF + 2, -D / 2 + 20 + (k * 61) % (D - 40)); base.add(p); }
  const aguaMat = new THREE.MeshStandardMaterial({ color: C.agua, transparent: true, opacity: 0.8, roughness: 0.2, metalness: 0.0, depthWrite: false });
  const ag = new THREE.BoxGeometry(LEN - 4, PROF - 4, D - 4); const colA = [], cTop = new THREE.Color(0x3d8fa0), cBot = new THREE.Color(0x0f3540);
  for (let k = 0; k < ag.attributes.position.count; k++) { const y = ag.attributes.position.getY(k); const c = cBot.clone().lerp(cTop, (y + PROF / 2) / PROF); colA.push(c.r, c.g, c.b); }
  ag.setAttribute('color', new THREE.Float32BufferAttribute(colA, 3)); aguaMat.vertexColors = true; aguaMat.color.set(0xffffff);
  const agua = new THREE.Mesh(ag, aguaMat); agua.position.set(0, -PROF / 2 - 4, 0); agua.renderOrder = 10; base.add(agua);
  const supMat = new THREE.MeshStandardMaterial({ color: 0x1a5866, transparent: true, opacity: 0.78, roughness: 0.05, metalness: 0.1, depthWrite: false });
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
    const b = new THREE.Mesh(new THREE.SphereGeometry(3, 10, 10), new THREE.MeshBasicMaterial({ color: 0xff5040 })); b.position.y = TH + 24; g.add(b);
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
    const far = new THREE.Mesh(new THREE.SphereGeometry(1.8, 8, 8), new THREE.MeshBasicMaterial({ color: 0xfff2cc })); far.position.set(0, 16, 25); d.add(far);
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

  function proyecta(v3) { const v = v3.clone().project(cam); return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H]; }
  function pon(px, py, pz, tx, ty, tz, zoom) {
    cam.position.set(px, py, pz); cam.lookAt(tx, ty, tz); cam.zoom = zoom; cam.updateProjectionMatrix();
  }
  window.ESC = { renderer, scene, cam, base, agua, aguaMat, sup, olas, cimientos, torres, huecos, dovelas, cables, pendolas, anclajes, barco, proyecta, pon,
    TX, TH, DECK, PROF, ANCLA, LEN, D, yC, C, render() { renderer.render(scene, cam); } };
})();

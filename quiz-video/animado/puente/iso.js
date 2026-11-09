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
  const aguaMat = new THREE.MeshStandardMaterial({ color: C.agua, transparent: true, opacity: 0.72, roughness: 0.2, metalness: 0.0, depthWrite: false });
  const agua = new THREE.Mesh(new THREE.BoxGeometry(LEN - 4, PROF - 4, D - 4), aguaMat); agua.position.set(0, -PROF / 2 - 4, 0); agua.renderOrder = 10; base.add(agua);
  const supMat = new THREE.MeshStandardMaterial({ color: 0x2a7586, transparent: true, opacity: 0.62, roughness: 0.05, metalness: 0.1, depthWrite: false });
  const sup = new THREE.Mesh(new THREE.PlaneGeometry(LEN - 4, D - 4, 1, 1), supMat); sup.rotation.x = -Math.PI / 2; sup.position.y = -5; sup.renderOrder = 11; base.add(sup);
  // líneas de oleaje suaves en la superficie
  const olas = new THREE.Group(); for (let k = 0; k < 26; k++) { const o = new THREE.Mesh(new THREE.PlaneGeometry(40 + (k % 5) * 18, 2), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.45, depthWrite: false })); o.rotation.x = -Math.PI / 2; o.position.set(-LEN / 2 + 60 + (k * 211) % (LEN - 120), -4.5, -D / 2 + 20 + (k * 47) % (D - 40)); olas.add(o); } base.add(olas);

  // ---------------- cimientos (cajones)
  const cimientos = [];
  for (const s of [-1, 1]) {
    const g = new THREE.CylinderGeometry(44, 50, PROF + 40, 40); g.translate(0, (PROF + 40) / 2, 0);
    const c = S(new THREE.Mesh(g, M(C.hueso))); c.position.set(s * TX, -PROF - 38, 0); base.add(c); cimientos.push(c);
  }
  // ---------------- torres (dos fustes, travesaños con arco)
  const torres = [], huecos = [];
  const matT = M(C.blanco, { roughness: 0.6 });
  function torre(x) {
    const g = new THREE.Group();
    for (const z of [-30, 30]) {
      const geo = new THREE.BoxGeometry(22, TH, 22); geo.translate(0, TH / 2, 0);
      const p = S(new THREE.Mesh(geo, matT)); p.position.z = z; p.scale.set(1, 1, 1); g.add(p);
    }
    for (const [y, h] of [[TH - 10, 20], [TH * 0.62, 16], [TH * 0.34, 14], [DECK - 14, 14]]) g.add(caja(16, h, 60, matT, 0, y, 0));
    g.add(caja(26, 12, 74, M(C.pizarra), 0, TH + 6, 0));
    // arcos (marcos huecos resaltables)
    for (const [y0, y1] of [[TH * 0.34 + 7, TH * 0.62 - 8], [TH * 0.62 + 8, TH - 20]]) {
      const hueco = new THREE.Mesh(new THREE.PlaneGeometry(36, y1 - y0), new THREE.MeshBasicMaterial({ color: C.acento, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false }));
      hueco.position.set(0, (y0 + y1) / 2, 0); hueco.rotation.y = Math.PI / 2; g.add(hueco); huecos.push(hueco);
    }
    g.position.x = x; base.add(g); torres.push(g); return g;
  }
  torre(-TX); torre(TX);
  // ---------------- tablero (tramos)
  const dovelas = []; const NDOV = 24; const LD = (2 * ANCLA) / NDOV;
  for (let i = 0; i < NDOV; i++) {
    const d = new THREE.Group();
    d.add(caja(LD - 1, 9, 50, M(C.blanco, { roughness: 0.55 }), 0, 0, 0));
    const asf = caja(LD - 1, 1.2, 40, M(C.pizarra, { roughness: 0.9 }), 0, 5.2, 0); d.add(asf);
    const linea = new THREE.Mesh(new THREE.BoxGeometry(LD * 0.5, 0.4, 1.2), new THREE.MeshBasicMaterial({ color: 0xf3f1ed })); linea.position.y = 6; d.add(linea);
    for (const z of [-24, 24]) d.add(caja(LD - 1, 4, 1.4, M(C.gris), 0, 7, z));
    d.position.set(-ANCLA + LD * (i + 0.5), DECK, 0); base.add(d); dovelas.push(d);
  }
  // ---------------- cables y péndolas
  const yC = (x) => { const ax = Math.abs(x); if (ax <= TX) return (DECK + 16) + (TH + 6 - (DECK + 16)) * (ax / TX) ** 2; const u = (ax - TX) / (ANCLA - TX); return (TH + 6) + (20 - (TH + 6)) * u; };
  const cabMat = M(0xd6d9de, { roughness: 0.35, metalness: 0.6 });
  const cables = [], pendolas = [];
  for (const z of [-30, 30]) {
    const pts = []; for (let i = 0; i <= 200; i++) { const x = -ANCLA + 2 * ANCLA * i / 200; pts.push(new THREE.Vector3(x, yC(x), z)); }
    const c = S(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 400, 2.6, 10, false), cabMat)); base.add(c); cables.push(c);
    for (let x = -ANCLA + 60; x < ANCLA - 40; x += 22) { if (Math.abs(Math.abs(x) - TX) < 10) continue; const h = yC(x) - DECK - 5; if (h < 6) continue; const p = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, h, 4), cabMat); p.position.set(x, DECK + 5 + h / 2, z); base.add(p); pendolas.push(p); }
  }
  const anclajes = []; for (const s of [-1, 1]) { const a = caja(70, 46, 96, M(C.hueso), s * ANCLA, 30, 0); base.add(a); anclajes.push(a); }

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

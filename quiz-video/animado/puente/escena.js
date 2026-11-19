// Escena 3D del puente colgante sobre el mar, estilo «Eixample de noche» (bloques achaflanados, luces cálidas, atardecer morado).
// Se usa igual en la prueba (preview.html) y en el vídeo (index.html). Expone window.ESC con la cámara y las piezas animables.
(function () {
  const W = 1080, H = 1920;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1); renderer.setSize(W, H);
  renderer.outputEncoding = THREE.sRGBEncoding; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
  document.getElementById('gl').appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0x3a2450, 1800, 7500);
  const cam = new THREE.PerspectiveCamera(38, W / H, 1, 9000);

  // luces: cielo morado + sol bajo naranja
  scene.add(new THREE.HemisphereLight(0x6a5aa0, 0x1a1028, 0.55));
  const sol = new THREE.DirectionalLight(0xffb070, 1.1); sol.position.set(-800, 300, -2500); scene.add(sol);
  const rel = new THREE.DirectionalLight(0x7a8aff, 0.35); rel.position.set(900, 800, 1200); scene.add(rel);

  const M = (c, o = {}) => new THREE.MeshStandardMaterial(Object.assign({ color: c, roughness: 0.85, metalness: 0.05 }, o));
  const brillo = (c, op = 1) => new THREE.MeshBasicMaterial({ color: c, transparent: op < 1, opacity: op, blending: op < 1 ? THREE.AdditiveBlending : THREE.NormalBlending, depthWrite: op >= 1, fog: true });

  // mar
  const olaTex = (() => { const cv = document.createElement('canvas'); cv.width = 512; cv.height = 512; const x = cv.getContext('2d');
    x.fillStyle = '#000'; x.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 260; i++) { x.fillStyle = `rgba(255,${150 + Math.random() * 80 | 0},120,${0.15 + Math.random() * 0.35})`; x.fillRect(Math.random() * 512, Math.random() * 512, 6 + Math.random() * 18, 1); }
    const t = new THREE.CanvasTexture(cv); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(30, 60); return t; })();
  const marG = new THREE.PlaneGeometry(12000, 12000, 1, 1);
  const mar = new THREE.Mesh(marG, M(0x1c1636, { roughness: 0.3, metalness: 0.6, emissive: 0xffffff, emissiveMap: olaTex, emissiveIntensity: 0.35 }));
  mar.rotation.x = -Math.PI / 2; scene.add(mar);
  // reflejo cálido del sol en el agua
  const ref = new THREE.Mesh(new THREE.PlaneGeometry(500, 5000), brillo(0xff9a50, 0.18)); ref.rotation.x = -Math.PI / 2; ref.position.set(-250, 0.5, -2600); scene.add(ref);

  const cieloMat = new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: {}, vertexShader: 'varying vec3 p; void main(){ p = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
    fragmentShader: 'varying vec3 p; void main(){ float h = p.y; vec3 c1 = vec3(0.07,0.04,0.13); vec3 c2 = vec3(0.30,0.16,0.34); vec3 c3 = vec3(0.95,0.52,0.30); vec3 c = mix(c3, c2, smoothstep(0.0, 0.10, h)); c = mix(c, c1, smoothstep(0.10, 0.45, h)); c = mix(c, vec3(0.15,0.09,0.18), smoothstep(0.0, -0.05, h)); gl_FragColor = vec4(c, 1.0); }' });
  scene.add(new THREE.Mesh(new THREE.SphereGeometry(8000, 32, 16), cieloMat));
  const solDisco = new THREE.Mesh(new THREE.CircleGeometry(140, 32), new THREE.MeshBasicMaterial({ color: 0xffd0a0, fog: false })); solDisco.position.set(-900, 60, -7000); scene.add(solDisco);
  // montañas lejanas
  const mont = new THREE.Group();
  for (let i = 0; i < 9; i++) {
    const g = new THREE.ConeGeometry(500 + (i % 3) * 180, 220 + (i % 4) * 70, 5);
    const m = new THREE.Mesh(g, M(0x2a1a36, { flatShading: true }));
    m.position.set(-4200 + i * 1050, 80, -4300 - (i % 2) * 300); m.scale.z = 0.35; mont.add(m);
  }
  scene.add(mont);

  // ---------------- orillas con manzanas de la Eixample (octógonos con patio, ventanas)
  const SPAN = 1000, TORRE_X = SPAN / 2, ORILLA = 680;          // el estrecho va de -ORILLA a +ORILLA en X
  const manzanaShape = (() => {
    const s = 56, c = 14, sh = new THREE.Shape();
    sh.moveTo(-s + c, -s); sh.lineTo(s - c, -s); sh.lineTo(s, -s + c); sh.lineTo(s, s - c); sh.lineTo(s - c, s); sh.lineTo(-s + c, s); sh.lineTo(-s, s - c); sh.lineTo(-s, -s + c); sh.lineTo(-s + c, -s);
    const h = new THREE.Path(); const i = 30, ic = 8;
    h.moveTo(-i + ic, -i); h.lineTo(i - ic, -i); h.lineTo(i, -i + ic); h.lineTo(i, i - ic); h.lineTo(i - ic, i); h.lineTo(-i + ic, i); h.lineTo(-i, i - ic); h.lineTo(-i, -i + ic); h.lineTo(-i + ic, -i);
    sh.holes.push(h); return sh;
  })();
  const ventTex = (() => {
    const cv = document.createElement('canvas'); cv.width = 128; cv.height = 64; const x = cv.getContext('2d');
    x.fillStyle = '#000000'; x.fillRect(0, 0, 128, 64);
    for (let r = 0; r < 5; r++) for (let k = 0; k < 16; k++) { if (Math.random() < 0.5) { x.fillStyle = Math.random() < 0.7 ? '#ffb860' : '#fff0c8'; x.fillRect(4 + k * 7.8, 6 + r * 11.5, 3, 4); } }
    const t = new THREE.CanvasTexture(cv); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(1 / 60, 1 / 30); return t;
  })();
  const manzanaGeo = new THREE.ExtrudeGeometry(manzanaShape, { depth: 30, bevelEnabled: false });
  manzanaGeo.rotateX(-Math.PI / 2);
  const matLados = M(0x2a2042, { emissive: 0xffffff, emissiveMap: ventTex, emissiveIntensity: 1.6, roughness: 0.9 });
  const matTecho = M(0x1c1530, { roughness: 0.95 });
  const ciudad = new THREE.Group();
  const lucesCalle = [];
  function orilla(signo) {
    const tierra = new THREE.Mesh(new THREE.BoxGeometry(3600, 40, 6000), M(0x1e1630));
    tierra.position.set(signo * (ORILLA + 1800), 0, -1200); ciudad.add(tierra);
    const muelle = new THREE.Mesh(new THREE.BoxGeometry(40, 46, 6000), M(0x5a4a6a)); muelle.position.set(signo * (ORILLA + 20), 0, -1200); ciudad.add(muelle);
    const paso = 140;
    for (let ix = 0; ix < 22; ix++) for (let iz = 0; iz < 36; iz++) {
      const x = signo * (ORILLA + 110 + ix * paso), z = 900 - iz * paso;
      if (Math.abs(z) < 90 && ix < 4) continue;                    // hueco para la carretera del puente
      const m = new THREE.Mesh(manzanaGeo, [matTecho, matLados]);
      m.position.set(x, 20, z); m.scale.y = 0.8 + Math.random() * 0.6; ciudad.add(m);
    }
    // calles con luz cálida (líneas que brillan)
    for (let ix = 0; ix < 23; ix++) {
      const x = signo * (ORILLA + 40 + ix * paso);
      const l = new THREE.Mesh(new THREE.BoxGeometry(12, 1, 5000), brillo(0xff9a30, 1)); l.position.set(x, 21.5, -1500); ciudad.add(l); lucesCalle.push(l);
    }
    for (let iz = 0; iz < 37; iz++) {
      const z = 970 - iz * paso;
      const l = new THREE.Mesh(new THREE.BoxGeometry(3200, 1, 12), brillo(0xff9a30, 1)); l.position.set(signo * (ORILLA + 1640), 21.5, z); ciudad.add(l); lucesCalle.push(l);
    }
  }
  orilla(1); orilla(-1); scene.add(ciudad);

  // ---------------- el puente colgante
  const puente = new THREE.Group(); scene.add(puente);
  const TH = 230, DECK = 70, ANCLA = ORILLA + 260;
  const matTorre = M(0x9a8ab8, { roughness: 0.55, emissive: 0x2a1a40, emissiveIntensity: 0.4 });
  const torres = [];
  function torre(x) {
    const g = new THREE.Group();
    for (const z of [-18, 18]) { const p = new THREE.Mesh(new THREE.BoxGeometry(12, TH, 10), matTorre); p.position.set(0, TH / 2, z); g.add(p); }
    for (const y of [DECK - 6, 150, TH - 6]) { const v = new THREE.Mesh(new THREE.BoxGeometry(10, 9, 46), matTorre); v.position.set(0, y, 0); g.add(v); }
    const base = new THREE.Mesh(new THREE.CylinderGeometry(30, 34, 24, 24), M(0x9a8ab0)); base.position.y = 4; g.add(base);
    const luz = new THREE.Mesh(new THREE.SphereGeometry(3, 12, 12), brillo(0xff4a3a)); luz.position.y = TH + 3; g.add(luz);
    g.position.x = x; puente.add(g); torres.push(g); return g;
  }
  const tA = torre(-TORRE_X), tB = torre(TORRE_X);
  // tablero
  const tablero = new THREE.Mesh(new THREE.BoxGeometry(2 * ANCLA, 6, 30), M(0x6a5a8a, { roughness: 0.7 }));
  tablero.position.set(0, DECK, 0); puente.add(tablero);
  const bordes = [];
  for (const z of [-15.5, 15.5]) { const b = new THREE.Mesh(new THREE.BoxGeometry(2 * ANCLA, 1.6, 1.2), brillo(0xffc070)); b.position.set(0, DECK + 3.8, z); puente.add(b); bordes.push(b); }
  // cables principales (parábola) + halo
  function curvaCable(z) {
    const pts = [];
    const sag = TH - 18 - (DECK + 10);
    for (let i = 0; i <= 120; i++) {
      const x = -ANCLA + (2 * ANCLA) * i / 120; let y;
      if (Math.abs(x) <= TORRE_X) y = (DECK + 10) + sag * Math.pow(x / TORRE_X, 2);
      else { const u = (Math.abs(x) - TORRE_X) / (ANCLA - TORRE_X); y = (TH - 2) + (DECK - 6 - (TH - 2)) * u; }
      pts.push(new THREE.Vector3(x, y, z));
    }
    return new THREE.CatmullRomCurve3(pts);
  }
  const cables = [], halos = [];
  for (const z of [-16, 16]) {
    const c = curvaCable(z);
    const m = new THREE.Mesh(new THREE.TubeGeometry(c, 300, 1.6, 8, false), brillo(0xffc070)); puente.add(m); cables.push(m);
    const h = new THREE.Mesh(new THREE.TubeGeometry(c, 300, 6, 8, false), brillo(0xff8a30, 0.35)); puente.add(h); halos.push(h);
    // péndolas
    const segs = [];
    for (let x = -TORRE_X + 20; x < TORRE_X; x += 20) {
      const y = (DECK + 10) + (TH - 18 - (DECK + 10)) * Math.pow(x / TORRE_X, 2);
      segs.push(x, DECK + 3, z, x, y, z);
    }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(segs, 3));
    const ls = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: 0xffc080, transparent: true, opacity: 0.9 })); puente.add(ls); cables.push(ls);
  }
  // anclajes en tierra
  for (const s of [-1, 1]) { const a = new THREE.Mesh(new THREE.BoxGeometry(60, 50, 70), M(0x7a6a90)); a.position.set(s * ANCLA, 25, 0); puente.add(a); }
  // luces del tablero
  for (let x = -ANCLA; x <= ANCLA; x += 40) for (const z of [-14, 14]) { const s = new THREE.Mesh(new THREE.SphereGeometry(1.4, 6, 6), brillo(0xfff0c0)); s.position.set(x, DECK + 8, z); puente.add(s); }

  const coches = [];
  for (let i = 0; i < 14; i++) {
    const dir = i % 2 ? 1 : -1;
    const c = new THREE.Mesh(new THREE.BoxGeometry(36, 2, 2.6), brillo(dir > 0 ? 0xfff2d0 : 0xff4a3a, 0.9));
    c.position.set(-ANCLA + Math.random() * 2 * ANCLA, DECK + 4.5, dir * 7); puente.add(c); coches.push({ m: c, dir, v: 80 + Math.random() * 40 });
  }
  // barco que pasa por debajo (gálibo)
  const barco = new THREE.Group();
  const casco = new THREE.Mesh(new THREE.BoxGeometry(90, 14, 22), M(0x2a2a3a)); casco.position.y = 7; barco.add(casco);
  const puenteB = new THREE.Mesh(new THREE.BoxGeometry(20, 22, 18), M(0xe9e2cf)); puenteB.position.set(-28, 24, 0); barco.add(puenteB);
  for (let i = 0; i < 4; i++) { const c = new THREE.Mesh(new THREE.BoxGeometry(14, 10, 18), M([0xff5a4f, 0x35a3d9, 0xffc24a, 0x3fa66b][i])); c.position.set(-4 + i * 15, 19, 0); barco.add(c); }
  barco.position.set(80, 0, 260); barco.rotation.y = Math.PI / 2.3; scene.add(barco);

  window.ESC = { renderer, scene, cam, coches, olaTex, puente, torres, tablero, cables, halos, bordes, barco, ciudad, lucesCalle, TORRE_X, TH, DECK, ANCLA,
    render() { renderer.render(scene, cam); } };
})();

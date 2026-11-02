// Motor 3D del vídeo «avión sin motores». Todo depende SOLO del tiempo t (render determinista frame a frame).
// window.K = tiempos clave (desde gen.py). render3d(t) se llama desde el onUpdate del timeline de GSAP.
(function () {
const K = window.K, W = 1080, H = 1920;
const canvas = document.getElementById('gl');
const R = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, alpha: false });
R.setPixelRatio(1); R.setSize(W, H, false);
R.toneMapping = THREE.ACESFilmicToneMapping; R.toneMappingExposure = 1.05;
R.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
const cam = new THREE.PerspectiveCamera(38, W / H, 0.5, 120000);
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const ease = k => (k = clamp(k, 0, 1), k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);
const eout = k => (k = clamp(k, 0, 1), 1 - Math.pow(1 - k, 3));
const ein = k => (k = clamp(k, 0, 1), k * k * k);
const prog = (t, a, b) => clamp((t - a) / (b - a), 0, 1);
function rng(s) { return () => (s = (s * 16807) % 2147483647) / 2147483647; }

// ------------------------------------------------------------------ cielo (cúpula con degradado + sol) y entorno PBR
const skyU = { top: { value: new THREE.Color() }, mid: { value: new THREE.Color() }, bot: { value: new THREE.Color() }, sun: { value: V3(1, 0.2, 0.3).normalize() }, sunC: { value: new THREE.Color() } };
const skyMat = new THREE.ShaderMaterial({ uniforms: skyU, side: THREE.BackSide, depthWrite: false,
  vertexShader: 'varying vec3 vd; void main(){ vd = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0);} ',
  fragmentShader: `uniform vec3 top, mid, bot, sun, sunC; varying vec3 vd;
    void main(){ float h = vd.y; vec3 c = h > 0.0 ? mix(mid, top, pow(clamp(h*1.6,0.0,1.0),0.7)) : mix(mid, bot, pow(clamp(-h*3.0,0.0,1.0),0.6));
      float s = max(dot(normalize(vd), normalize(sun)), 0.0); c += sunC * (pow(s, 900.0)*6.0 + pow(s, 12.0)*0.35 + pow(s,3.0)*0.12);
      gl_FragColor = vec4(c,1.0); }` });
const sky = new THREE.Mesh(new THREE.SphereGeometry(100000, 32, 16), skyMat); scene.add(sky);
const PAL = {
  ocaso: { top: '#1b2f5a', mid: '#f0a46c', bot: '#d9a990', sun: [1, 0.06, 0.55], sunC: '#ffb070', luz: '#ffd2a0', li: 2.6, hemi: ['#9db8e0', '#4a3a3a'], nube: '#ffe1cf', niebla: '#d9a58a' },
  alba: { top: '#24406e', mid: '#e9b38c', bot: '#6c7d8c', sun: [-1, 0.08, 0.35], sunC: '#ffc890', luz: '#ffe0bc', li: 2.2, hemi: ['#a9c2e2', '#3c4a40'], nube: '#ffe9da', niebla: '#c9b6a6' },
  gris: { top: '#5d6e86', mid: '#b9c4d0', bot: '#6d7884', sun: [0.4, 0.5, 0.6], sunC: '#fff4e6', luz: '#f2f4f8', li: 1.4, hemi: ['#c9d4e0', '#4a525a'], nube: '#e7ecf2', niebla: '#a9b4c0' },
};
const envCache = {};
const pmrem = new THREE.PMREMGenerator(R);
const sun = new THREE.DirectionalLight('#ffffff', 2.5); scene.add(sun, sun.target);
const hemi = new THREE.HemisphereLight('#ffffff', '#444444', 0.6); scene.add(hemi);
let palAct = null;
function paleta(n) {
  if (palAct === n) return; palAct = n; const p = PAL[n];
  skyU.top.value.set(p.top); skyU.mid.value.set(p.mid); skyU.bot.value.set(p.bot); skyU.sunC.value.set(p.sunC); skyU.sun.value.set(...p.sun).normalize();
  sun.color.set(p.luz); sun.intensity = p.li; sun.position.copy(skyU.sun.value).multiplyScalar(1000);
  hemi.color.set(p.hemi[0]); hemi.groundColor.set(p.hemi[1]);
  if (!envCache[n]) { const es = new THREE.Scene(); es.add(new THREE.Mesh(new THREE.SphereGeometry(100, 32, 16), skyMat)); envCache[n] = pmrem.fromScene(es, 0.02).texture; }
  scene.environment = envCache[n];
  scene.fog = new THREE.Fog(p.niebla, 9000, 60000);
  nubeMat.color.set(p.nube);
}

// ------------------------------------------------------------------ texturas por código
function lienzo(w, h, f) { const c = document.createElement('canvas'); c.width = w; c.height = h; f(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; }
const texNube = lienzo(256, 256, (g, w, h) => { const r = rng(7);
  for (let i = 0; i < 46; i++) { const x = 128 + (r() - 0.5) * 130, y = 140 + (r() - 0.5) * 70 - Math.abs(x - 128) * 0.25, s = 26 + r() * 46;
    const gr = g.createRadialGradient(x, y - s * 0.2, 0, x, y, s); gr.addColorStop(0, 'rgba(255,255,255,0.55)'); gr.addColorStop(0.6, 'rgba(240,240,245,0.25)'); gr.addColorStop(1, 'rgba(220,225,235,0)');
    g.fillStyle = gr; g.beginPath(); g.arc(x, y, s, 0, 7); g.fill(); } });
const nubeMat = new THREE.SpriteMaterial({ map: texNube, transparent: true, depthWrite: false, fog: true });
const texHumo = lienzo(128, 128, (g) => { const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(90,90,96,0.55)'); gr.addColorStop(1, 'rgba(90,90,96,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); });
const texSpray = lienzo(128, 128, (g) => { const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,255,255,0.9)'); gr.addColorStop(0.5, 'rgba(235,242,250,0.45)'); gr.addColorStop(1, 'rgba(230,240,250,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); });
// fuselaje: u = vuelta (0 lado derecho, 0.25 panza, 0.5 lado izq., 0.75 techo), v = largo (0 cola → 1 morro)
const texFus = lienzo(2048, 1024, (g, w, h) => {
  g.fillStyle = '#f4f6f8'; g.fillRect(0, 0, w, h);
  g.fillStyle = '#c9ced6'; g.fillRect(w * 0.12, 0, w * 0.26, h);                 // panza gris
  const franja = (u, col, a) => { g.fillStyle = col; g.fillRect(w * u, 0, w * a, h * 0.86); };
  franja(0.015, '#1d3a6e', 0.012); franja(0.473, '#1d3a6e', 0.012); franja(0.03, '#3e7ac0', 0.006); franja(0.464, '#3e7ac0', 0.006);
  const win = (u) => { for (let v = 0.2; v < 0.84; v += 0.0105) { if (Math.abs(v - 0.5) < 0.012 || Math.abs(v - 0.3) < 0.01) continue; g.fillStyle = '#1a2230'; g.beginPath(); g.ellipse(w * u, h * (1 - v), 6, 8, 0, 0, 7); g.fill(); } };
  win(0.962); win(0.538);
  g.strokeStyle = '#8f98a4'; g.lineWidth = 2;
  for (const [u, v] of [[0.955, 0.86], [0.955, 0.5], [0.955, 0.3], [0.955, 0.2], [0.545, 0.86], [0.545, 0.5], [0.545, 0.3], [0.545, 0.2]]) g.strokeRect(w * u - 12, h * (1 - v) - 22, 24, 44);
  g.fillStyle = '#121822';                                                    // ventanillas de cabina
  for (const [u0, u1] of [[0.9, 0.99], [0.51, 0.6]]) { g.beginPath(); g.moveTo(w * u0, h * (1 - 0.955)); g.lineTo(w * u1, h * (1 - 0.955)); g.lineTo(w * (u1 - 0.01), h * (1 - 0.935)); g.lineTo(w * (u0 + 0.01), h * (1 - 0.935)); g.fill(); }
  g.fillRect(w * 0.66, h * (1 - 0.96), w * 0.18, h * 0.02);
});
const blanco = new THREE.MeshStandardMaterial({ color: '#f1f3f6', metalness: 0.15, roughness: 0.35, envMapIntensity: 0.9 });
const gris = new THREE.MeshStandardMaterial({ color: '#b9c0ca', metalness: 0.6, roughness: 0.35 });
const oscuro = new THREE.MeshStandardMaterial({ color: '#15191f', metalness: 0.4, roughness: 0.55 });
const azul = new THREE.MeshStandardMaterial({ color: '#1d3a6e', metalness: 0.2, roughness: 0.4 });
const metal = new THREE.MeshStandardMaterial({ color: '#d7dde5', metalness: 0.9, roughness: 0.22 });

// ------------------------------------------------------------------ geometría: loft de secciones (alas, estabilizadores, deriva)
function perfil(c, t, n = 14) { const up = [], lo = [];
  for (let i = 0; i <= n; i++) { const x = (1 - Math.cos(Math.PI * i / n)) / 2; const yt = 5 * t * (0.2969 * Math.sqrt(x) - 0.126 * x - 0.3516 * x * x + 0.2843 * x ** 3 - 0.1036 * x ** 4); const cb = 0.02 * Math.sin(Math.PI * x);
    up.push([x * c, (cb + yt) * c]); lo.push([x * c, (cb - yt) * c]); }
  return up.reverse().concat(lo.slice(1, -1)); }
function loft(secs, mat) {
  const n = secs[0].length, pos = [], idx = [];
  secs.forEach(s => s.forEach(p => pos.push(p.x, p.y, p.z)));
  for (let k = 0; k < secs.length - 1; k++) for (let i = 0; i < n; i++) { const a = k * n + i, b = k * n + (i + 1) % n, c = a + n, d = b + n; idx.push(a, b, d, a, d, c); }
  const last = (secs.length - 1) * n; for (let i = 1; i < n - 1; i++) idx.push(last, last + i, last + i + 1);
  for (let i = 1; i < n - 1; i++) idx.push(0, i + 1, i);
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
  return new THREE.Mesh(g, mat); }
// sección horizontal (ala): borde de ataque en (x,y,z), cuerda c hacia -x
const secH = (x, y, z, c, t) => perfil(c, t).map(([u, v]) => V3(x - u, y + v, z));
// sección vertical (deriva): en el plano x-z a la altura y
const secV = (x, y, z, c, t) => perfil(c, t).map(([u, v]) => V3(x - u, y, z + v));

// ------------------------------------------------------------------ AVIÓN (bimotor de fuselaje ancho, librea genérica)
function avion() {
  const A = new THREE.Group();
  const prof = [];
  for (let i = 0; i <= 60; i++) { const y = -30 + i; let r = 2.85;
    if (y > 22) r = 2.85 * Math.sqrt(Math.max(0, 1 - Math.pow((y - 22) / 8.2, 2)));
    if (y < -12) r = lerp(2.85, 0.55, Math.pow((-12 - y) / 18, 1.25));
    prof.push(new THREE.Vector2(Math.max(r, 0.001), y)); }
  const gf = new THREE.LatheGeometry(prof, 64); gf.rotateZ(-Math.PI / 2);
  const p = gf.attributes.position;
  for (let i = 0; i < p.count; i++) { const x = p.getX(i); if (x < -12) p.setY(i, p.getY(i) + Math.pow((-12 - x) / 18, 1.7) * 1.9); if (x > 24) p.setY(i, p.getY(i) - Math.pow((x - 24) / 6, 2) * 0.5); }
  gf.computeVertexNormals();
  const fus = new THREE.Mesh(gf, new THREE.MeshStandardMaterial({ map: texFus, metalness: 0.15, roughness: 0.32 })); A.add(fus);
  // carenado ala-fuselaje
  const car = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 16), blanco); car.scale.set(9, 1.4, 2.9); car.position.set(1, -2.1, 0); A.add(car);
  for (const s of [1, -1]) {
    const ala = loft([secH(7, -1.4, 2.6 * s, 10.5, 0.13), secH(1.5, -0.9, 10 * s, 7.2, 0.115), secH(-9.4, 1.1, 28.6 * s, 2.6, 0.1)], blanco); A.add(ala);
    const wl = loft([secV(-9.2, 1.0, 28.7 * s, 2.6, 0.08), secV(-11.4, 4.2, 29.4 * s, 1.2, 0.08)], azul); A.add(wl);
    const hs = loft([secH(-22.2, 1.7, 1.0 * s, 5.4, 0.1), secH(-28.8, 2.4, 9.8 * s, 2.0, 0.09)], blanco); A.add(hs);
    // motor
    const M = new THREE.Group(); M.position.set(9.5, -3.6, 10.2 * s); A.add(M);
    const np = [[1.62, 0], [1.68, -0.3], [1.72, -1.4], [1.6, -3.4], [1.25, -5.0], [0.95, -5.6]].map(([r, x]) => new THREE.Vector2(r, x));
    const ng = new THREE.LatheGeometry(np, 48); ng.rotateZ(-Math.PI / 2); M.add(new THREE.Mesh(ng, blanco));
    const lip = new THREE.Mesh(new THREE.TorusGeometry(1.58, 0.1, 12, 48), metal); lip.rotation.y = Math.PI / 2; lip.position.x = 0.02; M.add(lip);
    const inner = new THREE.LatheGeometry([[1.5, 0.05], [1.45, -0.9]].map(([r, x]) => new THREE.Vector2(r, x)), 48); inner.rotateZ(-Math.PI / 2);
    M.add(new THREE.Mesh(inner, new THREE.MeshStandardMaterial({ color: '#2b3038', side: THREE.BackSide, metalness: 0.5, roughness: 0.5 })));
    const fan = new THREE.Group(); fan.position.x = -0.6; M.add(fan);
    const spin = new THREE.Mesh(new THREE.ConeGeometry(0.42, 0.9, 32), metal); spin.rotation.z = -Math.PI / 2; spin.position.x = 0.35; fan.add(spin);
    const bm = new THREE.MeshStandardMaterial({ color: '#3a4049', metalness: 0.85, roughness: 0.3 });
    for (let i = 0; i < 22; i++) { const b = new THREE.Mesh(new THREE.BoxGeometry(0.06, 1.15, 0.32), bm); b.position.set(0, 0.92, 0); b.rotation.y = 0.55;
      const piv = new THREE.Group(); piv.rotation.x = i / 22 * Math.PI * 2; piv.add(b); fan.add(piv); }
    const disco = new THREE.Mesh(new THREE.CircleGeometry(1.48, 48), new THREE.MeshStandardMaterial({ color: '#0d1014', roughness: 0.9 })); disco.rotation.y = Math.PI / 2; disco.position.x = -0.15; fan.add(disco);
    const tob = new THREE.Mesh(new THREE.ConeGeometry(0.75, 1.6, 32), oscuro); tob.rotation.z = Math.PI / 2; tob.position.x = -6.2; M.add(tob);
    const pil = new THREE.Mesh(new THREE.BoxGeometry(5.2, 1.6, 0.45), blanco); pil.position.set(-2.2, 1.35, 0); M.add(pil);
    M.userData = { fan, s }; A.userData['motor' + (s > 0 ? 'D' : 'I')] = M;
  }
  const vt = loft([secV(-19.5, 2.4, 0, 9.5, 0.1), secV(-27.5, 12.5, 0, 3.6, 0.09)], azul); A.add(vt);
  const vtb = loft([secV(-23.6, 7.5, 0.02, 2.4, 0.11), secV(-27.0, 11.5, 0.02, 1.4, 0.11)], new THREE.MeshStandardMaterial({ color: '#3e7ac0', roughness: 0.4 })); A.add(vtb);
  // tren (solo en el aterrizaje)
  const tren = new THREE.Group(); A.add(tren); A.userData.tren = tren;
  const rueda = () => { const g = new THREE.Group(); for (const dz of [-0.45, 0.45]) for (const dx of [-0.75, 0.75]) { const w = new THREE.Mesh(new THREE.CylinderGeometry(0.62, 0.62, 0.4, 24), oscuro); w.rotation.x = Math.PI / 2; w.position.set(dx, 0, dz); g.add(w); } return g; };
  for (const s of [1, -1]) { const pata = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 3, 12), gris); pata.position.set(-1, -3.6, 4.6 * s); tren.add(pata); const r = rueda(); r.position.set(-1, -5.1, 4.6 * s); tren.add(r); }
  const pn = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 2.6, 12), gris); pn.position.set(22, -3.4, 0); tren.add(pn);
  for (const dz of [-0.3, 0.3]) { const w = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.45, 0.3, 20), oscuro); w.rotation.x = Math.PI / 2; w.position.set(22, -4.7, dz); tren.add(w); }
  // RAT: brazo con hélice que sale de la panza (a la derecha, junto al ala)
  const rat = new THREE.Group(); rat.position.set(3.5, -2.55, 1.9); A.add(rat); A.userData.rat = rat;
  const brazo = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.12, 1.8, 12), gris); brazo.position.y = -0.9; rat.add(brazo);
  const cab = new THREE.Mesh(new THREE.SphereGeometry(0.22, 16, 12), metal); cab.scale.set(1.8, 1, 1); cab.position.set(0.15, -1.85, 0); rat.add(cab);
  const helice = new THREE.Group(); helice.position.set(0.5, -1.85, 0); rat.add(helice); A.userData.helice = helice;
  for (const a of [0, Math.PI]) { const b = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.85, 0.16), oscuro); b.position.y = 0.43; b.rotation.y = 0.4; const pv = new THREE.Group(); pv.rotation.x = a; pv.add(b); helice.add(pv); }
  const tapa = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.05, 0.7), blanco); tapa.position.set(3.4, -2.62, 1.75); A.add(tapa); A.userData.tapa = tapa;
  // luces de navegación
  const luz = (c, x, y, z) => { const m = new THREE.Mesh(new THREE.SphereGeometry(0.16, 8, 8), new THREE.MeshBasicMaterial({ color: c })); m.position.set(x, y, z); A.add(m); };
  luz('#ff3030', -9.6, 1.2, -28.9); luz('#30ff60', -9.6, 1.2, 28.9); luz('#ffffff', -30.3, 2.5, 0);
  return A;
}
const avi = avion(); scene.add(avi);

// ------------------------------------------------------------------ mar de nubes (sprites) y humo
const nubes = new THREE.Group(); scene.add(nubes);
const manto = new THREE.Mesh(new THREE.PlaneGeometry(200000, 200000), new THREE.MeshBasicMaterial({ color: '#e8c3ad', fog: true })); manto.rotation.x = -Math.PI / 2; nubes.add(manto);
const NUB = []; { const r = rng(11); for (let i = 0; i < 700; i++) { const s = new THREE.Sprite(nubeMat); const sc = 2200 + r() * 3000; s.scale.set(sc, sc * 0.55, 1); s.userData = { x: (r() - 0.5) * 60000, z: (r() - 0.5) * 60000, y: -2600 - r() * 700 }; nubes.add(s); NUB.push(s); } }
function ponNubes(t, vel, dy) { manto.position.y = -2650 + dy; manto.material.color.set(PAL[palAct].nube).multiplyScalar(0.93); const L = 60000; for (const s of NUB) { const u = s.userData; let x = ((u.x - vel * t) % L + L * 1.5) % L - L / 2; s.position.set(x, u.y + dy, u.z); } }
const humoMat = new THREE.SpriteMaterial({ map: texHumo, transparent: true, depthWrite: false });
const HUMO = []; for (let i = 0; i < 70; i++) { const s = new THREE.Sprite(humoMat.clone()); scene.add(s); HUMO.push(s); }
const sprayMat = new THREE.SpriteMaterial({ map: texSpray, transparent: true, depthWrite: false });
const SPRAY = []; for (let i = 0; i < 90; i++) { const s = new THREE.Sprite(sprayMat.clone()); scene.add(s); SPRAY.push(s); }
function ocultaParticulas() { HUMO.forEach(s => s.visible = false); SPRAY.forEach(s => s.visible = false); }

// ------------------------------------------------------------------ escenarios de suelo: mapa, pista en isla, río con ciudad
const suelo = new THREE.Group(); scene.add(suelo);
const texMapa = lienzo(2048, 2048, (g, w, h) => {
  const fx = X => (0.5 + X / 12000) * w, fy = Z => (0.5 + Z / 12000) * h;
  g.fillStyle = '#1f4a6e'; g.fillRect(0, 0, w, h);
  const r = rng(5); g.fillStyle = '#5d6b3c'; g.beginPath(); g.moveTo(0, 0);
  for (let y = 0; y <= h; y += 32) g.lineTo(fx(1500) + 70 * Math.sin(y / 170) + (r() - 0.5) * 18, y);
  g.lineTo(0, h); g.fill();
  g.strokeStyle = 'rgba(230,240,250,0.5)'; g.lineWidth = 5; g.beginPath(); for (let y = 0; y <= h; y += 32) g.lineTo(fx(1500) + 70 * Math.sin(y / 170) + 8, y); g.stroke();
  for (let i = 0; i < 420; i++) { g.fillStyle = ['#6f7c45', '#566436', '#7d8550', '#4e5b31', '#8b8a57', '#6a6a3c'][i % 6]; const x = r() * fx(1300), y = r() * h; g.save(); g.translate(x, y); g.rotate((r() - 0.5) * 0.5); g.fillRect(-40, -30, 40 + r() * 70, 30 + r() * 60); g.restore(); }
  g.strokeStyle = '#46505a'; g.lineWidth = 6; g.beginPath(); g.moveTo(0, fy(400)); g.bezierCurveTo(fx(-2000), fy(0), fx(-1000), fy(900), fx(1450), fy(500)); g.stroke();
  g.fillStyle = '#9a9c94'; g.fillRect(fx(-1700), fy(-1950), 300, 140);
  g.save(); g.translate(fx(-700), fy(-1500)); g.rotate(-0.42); g.fillStyle = '#2f3237'; g.fillRect(-256, -16, 512, 32); g.fillStyle = '#f2f2f2'; for (let k = -230; k < 230; k += 26) g.fillRect(k, -1.5, 14, 3); g.restore();
  g.fillStyle = '#b8b46a'; g.fillRect(fx(-800), fy(1250), 170, 120); g.strokeStyle = '#8f8c50'; g.lineWidth = 2; for (let k = 0; k < 170; k += 10) { g.beginPath(); g.moveTo(fx(-800) + k, fy(1250)); g.lineTo(fx(-800) + k, fy(1250) + 120); g.stroke(); }
  g.fillStyle = 'rgba(255,255,255,0.10)'; for (let i = 0; i < 70; i++) { g.beginPath(); g.ellipse(fx(1700) + r() * (w - fx(1700)), r() * h, 10 + r() * 24, 3, 0, 0, 7); g.fill(); }
});
texMapa.anisotropy = 8;
const mapa = new THREE.Mesh(new THREE.PlaneGeometry(12000, 12000), new THREE.MeshStandardMaterial({ map: texMapa, roughness: 0.95 })); mapa.rotation.x = -Math.PI / 2; suelo.add(mapa);
const agua = new THREE.Mesh(new THREE.PlaneGeometry(200000, 200000), new THREE.MeshStandardMaterial({ color: '#16324a', metalness: 0.2, roughness: 0.18, envMapIntensity: 1.2 })); agua.rotation.x = -Math.PI / 2; agua.position.y = -0.5; scene.add(agua);
const texPista = lienzo(256, 4096, (g, w, h) => { g.fillStyle = '#2c2f34'; g.fillRect(0, 0, w, h); g.fillStyle = '#f2f2f2';
  g.fillRect(6, 0, 6, h); g.fillRect(w - 12, 0, 6, h); for (let y = 200; y < h - 200; y += 120) g.fillRect(w / 2 - 3, y, 6, 60);
  for (let k = 0; k < 8; k++) { g.fillRect(24 + k * 26, 40, 14, 160); g.fillRect(24 + k * 26, h - 200, 14, 160); }
  for (const y of [700, h - 900]) { g.fillRect(40, y, 40, 160); g.fillRect(w - 80, y, 40, 160); } });
const pista = new THREE.Mesh(new THREE.PlaneGeometry(60, 3200), new THREE.MeshStandardMaterial({ map: texPista, roughness: 0.85 })); pista.rotation.x = -Math.PI / 2; pista.rotation.z = Math.PI / 2;
const isla = new THREE.Mesh(new THREE.CircleGeometry(4200, 64), new THREE.MeshStandardMaterial({ color: '#4c5a3a', roughness: 1 })); isla.rotation.x = -Math.PI / 2; isla.position.y = 0.1;
const luces = new THREE.Group(); for (let k = 0; k < 64; k++) for (const z of [-32, 32]) { const m = new THREE.Mesh(new THREE.SphereGeometry(0.25, 6, 6), new THREE.MeshBasicMaterial({ color: '#ffe3a0' })); m.position.set(-1600 + k * 50, 0.6, z); luces.add(m); }
const aeropuerto = new THREE.Group(); aeropuerto.add(isla, pista, luces); pista.position.y = 0.3; scene.add(aeropuerto);
const ciudad = new THREE.Group(); scene.add(ciudad);
{ const r = rng(23); const texVent = lienzo(64, 128, (g, w, h) => { g.fillStyle = '#3a4250'; g.fillRect(0, 0, w, h); for (let y = 4; y < h; y += 8) for (let x = 4; x < w; x += 8) { g.fillStyle = r() < 0.3 ? '#ffd99a' : '#56627a'; g.fillRect(x, y, 4, 5); } });
  texVent.wrapS = texVent.wrapT = THREE.RepeatWrapping;
  for (let i = 0; i < 140; i++) { const hgt = 30 + Math.pow(r(), 2.2) * 260, wd = 25 + r() * 40; const t = texVent.clone(); t.needsUpdate = true; t.repeat.set(wd / 40, hgt / 60);
    const m = new THREE.Mesh(new THREE.BoxGeometry(wd, hgt, wd), new THREE.MeshStandardMaterial({ map: t, roughness: 0.7, emissive: '#ffcf8a', emissiveMap: t, emissiveIntensity: 0.25 }));
    m.position.set(-3000 + i * 45 + r() * 20, hgt / 2, -900 - r() * 500); ciudad.add(m); }
  const orilla = new THREE.Mesh(new THREE.PlaneGeometry(12000, 2400), new THREE.MeshStandardMaterial({ color: '#3a3d40', roughness: 1 })); orilla.rotation.x = -Math.PI / 2; orilla.position.set(0, 0.2, -2000); ciudad.add(orilla); }
// línea de trayectoria (plano 2) y «piedra» que cae recta
const trayG = new THREE.BufferGeometry().setFromPoints(Array.from({ length: 200 }, (_, i) => V3(i * 40, -i * 40 / 16, 0)));
const tray = new THREE.Line(trayG, new THREE.LineDashedMaterial({ color: '#9fdcff', dashSize: 30, gapSize: 20, transparent: true, opacity: 0.9 })); tray.computeLineDistances(); scene.add(tray);
const roca = new THREE.Mesh(new THREE.DodecahedronGeometry(9, 1), new THREE.MeshStandardMaterial({ color: '#6b6460', roughness: 0.95, flatShading: true })); scene.add(roca);

// ------------------------------------------------------------------ utilidades de plano
function fanes(t, rpm) { for (const k of ['motorD', 'motorI']) { const M = avi.userData[k]; M.userData.fan.rotation.x = -rpm; } }
// ángulo acumulado del ventilador: gira rápido y se frena de forma exponencial tras el apagado
function giroFan(t, tOff) { const w0 = 38; if (tOff === null || t < tOff) return w0 * t; const d = t - tOff; return w0 * tOff + w0 / 0.9 * (1 - Math.exp(-0.9 * d)) + 1.2 * d; }
function estadoAvion(o) { avi.position.set(...(o.pos || [0, 0, 0])); avi.rotation.set(o.roll || 0, o.yaw || 0, o.pitch || 0); avi.userData.tren.visible = !!o.tren;
  const r = o.rat || 0; avi.userData.rat.rotation.z = lerp(Math.PI / 2 * 0.98, 0, r); avi.userData.rat.visible = r > 0.01; avi.userData.tapa.rotation.x = -1.2 * Math.min(1, r * 3); avi.userData.tapa.visible = true; }
function mira(p, l, fov) { cam.position.set(...p); cam.lookAt(...l); if (fov) { cam.fov = fov; cam.updateProjectionMatrix(); } }
function visibles(o) { nubes.visible = !!o.nubes; suelo.visible = !!o.mapa; agua.visible = !!o.agua; aeropuerto.visible = !!o.pista; ciudad.visible = !!o.ciudad; tray.visible = !!o.tray; roca.visible = !!o.roca; sky.visible = true; }
window.proyecta = (x, y, z) => { const v = V3(x, y, z).project(cam); return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H, v.z]; };

// ------------------------------------------------------------------ PLANOS
const PLANOS = [
  // 1 y 13: crucero al atardecer sobre el mar de nubes; cámara junto al motor derecho que se aleja
  { a: K.p1, b: K.p2, f(t) { paleta('ocaso'); visibles({ nubes: 1 }); ocultaParticulas(); ponNubes(t, 230, 0);
      estadoAvion({ roll: 0.02 * Math.sin(t * 0.7), pitch: 0.035 }); fanes(t, giroFan(t, K.apagado));
      humo(t, K.apagado + 0.15, K.p2, 'motorD'); humo(t, K.apagado + 0.5, K.p2, 'motorI');
      const k = ease(prog(t, 0, K.p2)); mira([lerp(16, 34, k), lerp(-1.5, 6, k), lerp(24, 92, k)], [lerp(6, -2, k), lerp(-3, -1, k), lerp(10, 4, k)], lerp(36, 40, k)); } },
  { a: K.p13, b: K.fin + 1, f(t) { paleta('ocaso'); visibles({ nubes: 1 }); ocultaParticulas(); ponNubes(t, 230, 0);
      estadoAvion({ roll: 0.02 * Math.sin(t * 0.7), pitch: 0.035 }); fanes(t, giroFan(t, null));
      const k = ease(prog(t, K.p13, K.fin)); mira([lerp(34, 16, k), lerp(6, -1.5, k), lerp(92, 24, k)], [lerp(-2, 6, k), lerp(-1, -3, k), lerp(4, 10, k)], lerp(40, 36, k)); } },
  // 2: plano lateral abierto: la piedra cae recta, el avión sigue una trayectoria larga y suave
  { a: K.p2, b: K.p3, f(t) { paleta('ocaso'); visibles({ nubes: 1, tray: 1, roca: 1 }); ocultaParticulas(); ponNubes(t, 60, 0);
      const k = prog(t, K.p2, K.p3); const x = -110 + k * 220; estadoAvion({ pos: [x, -x / 16 - 16, 0], pitch: -0.06 }); fanes(t, 0);
      tray.position.set(-110, 110 / 16 - 16, 0); trayG.setDrawRange(0, Math.floor(clamp((t - K.p2 - 0.3) / 3.5, 0, 1) * 200));
      const tr = Math.max(0, t - K.piedra); roca.position.set(-100, 110 / 16 - 22 - 4.9 * tr * tr * 14, 0); roca.rotation.set(tr * 2, tr * 1.3, 0); roca.visible = t > K.p2 + 0.2;
      mira([lerp(-30, 30, k), 20, 760], [lerp(-30, 30, k), -40, 0], 40); } },
  // 4: travelling lateral: el morro baja y el avión desciende entre las cimas de las nubes
  { a: K.p4, b: K.p5, f(t) { paleta('ocaso'); visibles({ nubes: 1 }); ocultaParticulas(); const k = prog(t, K.p4, K.p5); ponNubes(t, 230, lerp(0, 2400, ease(k)));
      const pit = -0.075 * ease(prog(t, K.morro - 0.4, K.morro + 0.8)); estadoAvion({ pitch: 0.03 + pit }); fanes(t, 0);
      mira([lerp(-8, 8, k), lerp(4, 0, k), 120], [lerp(-4, 4, k), -2, 0], 34); } },
  // 8: desde abajo: se abre la trampilla y sale la RAT con la hélice girando
  { a: K.p8, b: K.p9, f(t) { paleta('ocaso'); visibles({ nubes: 1 }); ocultaParticulas(); ponNubes(t, 230, 2200);
      const r = eout(prog(t, K.rat, K.rat + 1.1)); estadoAvion({ pitch: -0.04, rat: r }); fanes(t, 0);
      avi.userData.helice.rotation.x = -Math.max(0, t - K.rat - 0.6) * 22 * clamp((t - K.rat - 0.6) / 1.2, 0, 1);
      const k = ease(prog(t, K.p8, K.p9)); const ang = lerp(-0.7, 0.6, k); mira([3.5 + 11 * Math.cos(ang), -9, 1.9 + 11 * Math.sin(ang)], [3.6, -3.6, 1.9], 44); } },
  // 10: mapa desde arriba: tres opciones y el avión gira hacia la pista
  { a: K.p10, b: K.p11, f(t) { paleta('gris'); visibles({ mapa: 1 }); ocultaParticulas(); const k = prog(t, K.p10, K.p11);
      const q = ease(prog(t, K.p10 + 0.3, K.p11)); const A0 = [2600, 2600], B0 = [1300, 300], C0 = [-200, -700];
      const bz = (j) => (1 - q) * (1 - q) * A0[j] + 2 * (1 - q) * q * B0[j] + q * q * C0[j]; const dz = (j) => 2 * (1 - q) * (B0[j] - A0[j]) + 2 * q * (C0[j] - B0[j]);
      const yaw = Math.atan2(-dz(1), dz(0)); const curva = Math.sin(Math.PI * q);
      estadoAvion({ pos: [bz(0), 900, bz(1)], yaw, roll: 0.35 * curva, pitch: -0.05 }); avi.scale.setScalar(7); fanes(t, 0);
      mira([lerp(1700, 1000, k), lerp(8500, 6000, k), lerp(2600, 1500, k)], [lerp(600, 100, k), 0, lerp(300, -300, k)], 42); } },
  // 11: Azores 2001: aproximación sobre el mar y toma con humo de neumáticos (alba)
  { a: K.p11, b: K.p12, f(t) { paleta('alba'); visibles({ agua: 1, pista: 1 }); ocultaParticulas(); const td = K.toma; const dtt = t - td;
      let x, y; if (dtt < 0) { x = 1700 + dtt * 75; y = Math.max(5.2, -dtt * 75 / 18 + 5.2 + Math.max(0, -dtt) * 0.0); } else { x = 1700 + 75 * dtt - 12 * dtt * dtt; y = 5.2; }
      x = 1700 + (dtt < 0 ? dtt * 75 : 75 * dtt - 9 * dtt * dtt); estadoAvion({ pos: [x - 1700 + 0, y, 0], pitch: dtt < 0 ? 0.06 : lerp(0.06, 0, clamp(dtt / 1.2, 0, 1)), tren: 1 }); avi.scale.setScalar(1); fanes(t, 0);
      aeropuerto.position.set(-1700 + 1000, 0, 0);
      humoRuedas(t, td);
      const k = ease(prog(t, K.p11, K.p12)); mira([lerp(-160, 60, k), 3, 70], [avi.position.x, avi.position.y + 1, 0], 34); } },
  // 12: Hudson 2009: amerizaje con cortina de agua y el avión flotando
  { a: K.p12, b: K.p13, f(t) { paleta('gris'); visibles({ agua: 1, ciudad: 1 }); ocultaParticulas(); const ta = K.amera, d = t - ta;
      let x, y, pit; if (d < 0) { x = d * 70; y = Math.max(2.4, -d * 70 / 14 + 2.4); pit = 0.09; } else { x = 70 * (1 - Math.exp(-1.1 * d)) / 1.1; y = lerp(2.4, 1.6, clamp(d / 1.5, 0, 1)) + 0.15 * Math.sin(d * 2.2) * clamp(d - 1.5, 0, 1); pit = lerp(0.09, 0.02, clamp(d / 1.2, 0, 1)); }
      estadoAvion({ pos: [x, y, 0], pitch: pit, roll: 0.01 * Math.sin(t) }); avi.scale.setScalar(1); fanes(t, 0);
      spray(t, ta);
      const k = ease(prog(t, K.p12, K.p13)); mira([avi.position.x * 0.6 - 40, 8, 120], [avi.position.x * 0.85, 3, -10], 36); } },
];
function humo(t, t0, t1, motor) { const M = avi.userData[motor]; const base = V3(-6.6, 0, 0); M.updateWorldMatrix(true, false); const w = base.clone().applyMatrix4(M.matrixWorld);
  for (let i = 0; i < 30; i++) { const s = HUMO[i + (motor === 'motorD' ? 0 : 30)]; const te = t0 + i * 0.07; const a = t - te;
    if (t < te || a > 2.8 || te > t1) { s.visible = false; continue; } s.visible = true;
    s.position.set(w.x - a * 55, w.y + a * 1.2, w.z + Math.sin(i) * a * 1.5); const sc = 2 + a * 7; s.scale.set(sc, sc, 1); s.material.opacity = 0.75 * (1 - a / 2.8) * clamp((t1 - te) / 0.6, 0, 1); } }
function humoRuedas(t, td) { for (let i = 0; i < 40; i++) { const s = HUMO[i]; const te = td + (i % 2) * 0.04 + Math.floor(i / 2) * 0.05; const a = t - te;
    if (a < 0 || a > 2.5) { s.visible = false; continue; } s.visible = true; s.position.set(avi.position.x - 1 - a * 8, 0.8 + a * 1.4, (i % 2 ? 4.6 : -4.6) + Math.sin(i * 1.7) * a); const sc = 1.5 + a * 6; s.scale.set(sc, sc, 1); s.material.opacity = 0.6 * (1 - a / 2.5); s.material.color.set('#d8d8dc'); } }
function spray(t, ta) { const r = rng(77); for (let i = 0; i < SPRAY.length; i++) { const s = SPRAY[i]; const te = ta + r() * 2.2; const a = t - te; const vz = (r() - 0.5) * 30, vy = 8 + r() * 14, sx = r() * 30 - 10;
    if (a < 0 || a > 2.2) { s.visible = false; continue; } s.visible = true;
    const x0 = 70 * (1 - Math.exp(-1.1 * (te - ta))) / 1.1 - 4 + sx * 0.3; s.position.set(x0 - a * 6, Math.max(0.3, vy * a - 4.9 * a * a), (r() > 0.5 ? 1 : -1) * 3 + vz * a); const sc = 3 + a * 9; s.scale.set(sc, sc * 0.8, 1); s.material.opacity = 0.85 * (1 - a / 2.2); } }

window.render3d = function (t) {
  const P = PLANOS.find(p => t >= p.a && t < p.b);
  canvas.style.visibility = P ? 'visible' : 'hidden';
  if (!P) return;
  avi.scale.setScalar(1); aeropuerto.position.set(0, 0, 0);
  P.f(t);
  R.render(scene, cam);
};
paleta('ocaso');
})();

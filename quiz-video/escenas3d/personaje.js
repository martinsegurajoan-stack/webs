// Personaje 3D estilizado (primitivas de three.js, sin modelos externos) para la serie «¿QUÉ PASARÍA SI…?».
// Estilo "figura de animación": cabeza grande, ojos expresivos, camiseta, y PELO con textura de mechones
// que crece en centímetros (melena que sigue la forma de la cabeza, mechones delanteros y puntas abiertas).
import * as THREE from './three.module.min.js';

const SKIN = 0xf0b48c, SHIRT = 0x2d63f0, HAIR = 0x3b2417;

// ---------------------------------------------------------------- texturas pintadas en canvas
function hairTexture(tip = false) {
  const c = document.createElement('canvas'); c.width = 512; c.height = 512;
  const g = c.getContext('2d');
  g.fillStyle = '#3b2417'; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 900; i++) {           // mechones: líneas verticales de varios tonos
    const x = Math.random() * 512, w = 1 + Math.random() * 3;
    const l = 22 + Math.random() * 30, a = 0.25 + Math.random() * 0.5;
    g.strokeStyle = `hsla(24, 45%, ${l}%, ${a})`; g.lineWidth = w;
    g.beginPath(); g.moveTo(x, 0);
    g.bezierCurveTo(x + 6 * Math.sin(i), 170, x - 6 * Math.cos(i), 340, x + 4 * Math.sin(i * 2), 512); g.stroke();
  }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 4;
  return t;
}

let HT = null;
function hairMat() {
  HT = HT || hairTexture();
  const m = new THREE.MeshPhysicalMaterial({ color: 0x8a6a58, map: HT, roughness: 0.5, sheen: 0.5,
    sheenColor: new THREE.Color(0x6a4028), sheenRoughness: 0.45, clearcoat: 0.1, clearcoatRoughness: 0.5,
    side: THREE.DoubleSide, vertexColors: true });
  return m;
}

// ---------------------------------------------------------------- piezas
function lathe(profile, seg = 48) {
  return new THREE.LatheGeometry(profile.map(([r, y]) => new THREE.Vector2(r, y)), seg);
}

export function crearPersonaje() {
  const root = new THREE.Group();
  const skin = new THREE.MeshPhysicalMaterial({ color: SKIN, roughness: 0.55, sheen: 0.4,
    sheenColor: new THREE.Color(0xff9a7a) });
  const shirt = new THREE.MeshStandardMaterial({ color: SHIRT, roughness: 0.92 });
  const shirtDark = new THREE.MeshStandardMaterial({ color: 0x1f4bc4, roughness: 0.92 });
  const hm = hairMat();

  // ---- torso con hombros (perfil de revolución, aplanado) y mangas
  const torso = new THREE.Mesh(lathe([[0.0, -1.85], [0.6, -1.84], [0.66, -1.6], [0.7, -1.3], [0.74, -1.0],
    [0.78, -0.86], [0.7, -0.76], [0.42, -0.66], [0.25, -0.62], [0.0, -0.62]]), shirt);
  torso.scale.set(1.15, 1, 0.66); torso.castShadow = true; root.add(torso);
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.19, 0.22, 0.3, 24), skin);
  neck.position.y = -0.55; root.add(neck);
  const collar = new THREE.Mesh(new THREE.TorusGeometry(0.21, 0.045, 12, 32), shirtDark);
  collar.rotation.x = Math.PI / 2; collar.scale.set(1.1, 0.8, 1); collar.position.y = -0.64; root.add(collar);
  const pants = new THREE.MeshStandardMaterial({ color: 0x2b2f3a, roughness: 0.85 });
  const shoeM = new THREE.MeshPhysicalMaterial({ color: 0xf4f4f4, roughness: 0.5, clearcoat: 0.3 });
  const hips = new THREE.Mesh(new THREE.SphereGeometry(0.62, 32, 16), pants);
  hips.scale.set(1.12, 0.45, 0.66); hips.position.y = -1.86; hips.castShadow = true; root.add(hips);
  const legs = [];
  for (const s of [-1, 1]) {
    const leg = new THREE.Group(); leg.position.set(s * 0.33, -1.95, 0); root.add(leg);
    const thigh = new THREE.Mesh(new THREE.CapsuleGeometry(0.24, 0.55, 8, 20), pants);
    thigh.position.y = -0.4; thigh.castShadow = true; leg.add(thigh);
    const knee = new THREE.Group(); knee.position.y = -0.8; leg.add(knee);
    const shin = new THREE.Mesh(new THREE.CapsuleGeometry(0.21, 0.55, 8, 20), pants);
    shin.position.y = -0.38; shin.castShadow = true; knee.add(shin);
    const shoe = new THREE.Mesh(new THREE.CapsuleGeometry(0.17, 0.28, 8, 16), shoeM);
    shoe.rotation.x = Math.PI / 2; shoe.position.set(0, -0.78, 0.1); shoe.castShadow = true; knee.add(shoe);
    legs.push({ leg, knee });
  }
  const arms = [];
  for (const s of [-1, 1]) {
    const arm = new THREE.Group(); arm.position.set(s * 0.82, -0.9, 0); root.add(arm);
    const sleeve = new THREE.Mesh(new THREE.CapsuleGeometry(0.21, 0.42, 8, 20), shirt);
    sleeve.position.y = -0.25; sleeve.castShadow = true; arm.add(sleeve);
    const fore = new THREE.Mesh(new THREE.CapsuleGeometry(0.14, 0.65, 8, 20), skin);
    fore.position.y = -0.85; arm.add(fore);
    const hand = new THREE.Mesh(new THREE.SphereGeometry(0.17, 24, 16), skin);
    hand.scale.set(0.9, 1.1, 0.7); hand.position.y = -1.32; arm.add(hand);
    arm.rotation.z = s * 0.1; arms.push(arm);
  }

  // ---- cabeza
  const head = new THREE.Group(); head.position.y = 0.12; root.add(head);
  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.62, 64, 48), skin);
  skull.scale.set(0.93, 1.05, 0.98); skull.castShadow = true; head.add(skull);
  const jaw = new THREE.Mesh(new THREE.SphereGeometry(0.5, 48, 32), skin);
  jaw.scale.set(0.98, 0.72, 0.95); jaw.position.set(0, -0.28, 0.06); head.add(jaw);
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.085, 32, 24), skin);
  nose.scale.set(1, 0.95, 1.1); nose.position.set(0, -0.08, 0.6); head.add(nose);
  const ears = [];
  for (const s of [-1, 1]) {
    const ear = new THREE.Mesh(new THREE.SphereGeometry(0.12, 24, 16), skin);
    ear.scale.set(0.45, 1, 0.75); ear.position.set(s * 0.58, -0.04, 0.02); head.add(ear); ears.push(ear);
    const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.1, 20, 16),
      new THREE.MeshBasicMaterial({ color: 0xff7d7d, transparent: true, opacity: 0.28 }));
    cheek.scale.set(1.3, 0.75, 0.25); cheek.position.set(s * 0.3, -0.18, 0.54); head.add(cheek);
  }
  // ojos grandes y brillantes
  const eyes = [], lids = [], brows = [], pupils = [];
  const white = new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.1, clearcoat: 1 });
  const irisM = new THREE.MeshPhysicalMaterial({ color: 0x4a2c18, roughness: 0.15, clearcoat: 1 });
  const pupM = new THREE.MeshBasicMaterial({ color: 0x0c0806 });
  for (const s of [-1, 1]) {
    const g = new THREE.Group(); g.position.set(s * 0.21, 0.07, 0.5); head.add(g);
    const e = new THREE.Mesh(new THREE.SphereGeometry(0.11, 32, 24), white); e.scale.set(0.95, 1.12, 0.6); g.add(e);
    const ir = new THREE.Mesh(new THREE.CircleGeometry(0.068, 32), irisM); ir.position.z = 0.068; g.add(ir);
    const pu = new THREE.Mesh(new THREE.CircleGeometry(0.036, 24), pupM); pu.position.z = 0.07; g.add(pu);
    const hl = new THREE.Mesh(new THREE.CircleGeometry(0.02, 16), new THREE.MeshBasicMaterial({ color: 0xffffff }));
    hl.position.set(0.025, 0.03, 0.072); g.add(hl);
    const hl2 = new THREE.Mesh(new THREE.CircleGeometry(0.009, 12), new THREE.MeshBasicMaterial({ color: 0xffffff }));
    hl2.position.set(-0.02, -0.025, 0.072); g.add(hl2);
    eyes.push(g); pupils.push([ir, pu, hl, hl2]);
    // párpado superior (semiesfera de piel que baja para parpadear)
    const lid = new THREE.Mesh(new THREE.SphereGeometry(0.118, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), skin);
    lid.scale.set(0.98, 1.15, 0.66); lid.rotation.x = -1.35; g.add(lid); lids.push(lid);
    const brow = new THREE.Mesh(new THREE.CapsuleGeometry(0.028, 0.13, 6, 12),
      new THREE.MeshStandardMaterial({ color: 0x2c1a10, roughness: 0.8 }));
    brow.rotation.z = Math.PI / 2; brow.position.set(s * 0.21, 0.26, 0.55); head.add(brow); brows.push(brow);
  }
  const mouthMat = new THREE.MeshStandardMaterial({ color: 0x6e1f2a, roughness: 0.6 });
  const mouth = new THREE.Mesh(new THREE.TorusGeometry(0.09, 0.022, 12, 32, Math.PI), mouthMat);
  mouth.position.set(0, -0.28, 0.555); head.add(mouth);
  const mouthO = new THREE.Mesh(new THREE.SphereGeometry(0.06, 24, 16), mouthMat);
  mouthO.scale.set(0.85, 1.15, 0.4); mouthO.position.set(0, -0.3, 0.56); head.add(mouthO);
  const sweat = new THREE.Mesh(new THREE.SphereGeometry(0.05, 16, 12),
    new THREE.MeshPhysicalMaterial({ color: 0xa8dcff, roughness: 0.05, clearcoat: 1 }));
  sweat.scale.set(0.8, 1.3, 0.8); head.add(sweat);

  // ---- pelo
  const cap = new THREE.Mesh(new THREE.BufferGeometry(), hm); cap.castShadow = true; head.add(cap);
  const mane = new THREE.Mesh(new THREE.BufferGeometry(), hm); mane.castShadow = true; head.add(mane);
  const fringe = new THREE.Mesh(new THREE.BufferGeometry(), hm); head.add(fringe);
  const locks = [0, 1].map(() => { const l = new THREE.Mesh(new THREE.BufferGeometry(), hm); l.castShadow = true; head.add(l); return l; });

  root.userData = { head, eyes, lids, brows, pupils, mouth, mouthO, sweat, cap, mane, fringe, locks, torso, arms, ears, legs };
  return root;
}

// ---------------------------------------------------------------- geometría del pelo

function tint(geo, puntas, tipStart = 0.82) {
  // color por vértice: blanco (deja ver la textura) y puntas más claras y secas si hay desgaste
  const pos = geo.attributes.position, uv = geo.attributes.uv, n = pos.count, cols = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    const v = uv ? uv.getY(i) : 0;
    const k = Math.max(0, (v - tipStart) / (1 - tipStart)) * puntas;
    cols[i * 3] = 1 + 0.9 * k; cols[i * 3 + 1] = 1 + 0.7 * k; cols[i * 3 + 2] = 1 + 0.45 * k;
  }
  geo.setAttribute('color', new THREE.BufferAttribute(cols, 3));
}

// Casquete: sigue el cráneo; el nacimiento del pelo deja la frente libre
function geoCasquete(cm) {
  const R = 0.655 + Math.min(cm, 25) * 0.0016;
  const segU = 72, segV = 36, pos = [], uv = [], idx = [];
  for (let j = 0; j <= segV; j++) {
    const v = j / segV;
    for (let i = 0; i <= segU; i++) {
      const u = i / segU, th = u * Math.PI * 2;         // th=π/2 → delante (z+)
      const front = Math.max(0, Math.sin(th));            // 1 delante, 0 atrás
      const maxPhi = Math.PI * (0.58 - 0.26 * Math.pow(front, 1.5));  // atrás baja hasta la nuca; delante, frente
      const phi = maxPhi * v;
      const clump = 1 + 0.025 * Math.sin(th * 18 + v * 3) * v;
      const x = Math.cos(th) * Math.sin(phi) * R * 0.95 * clump;
      const y = Math.cos(phi) * R * 1.07 + 0.03;
      const z = Math.sin(th) * Math.sin(phi) * R * 1.0 * clump;
      pos.push(x, y, z); uv.push(u * 6, v * 0.5);
    }
  }
  for (let j = 0; j < segV; j++) for (let i = 0; i < segU; i++) {
    const a = j * (segU + 1) + i, b = a + segU + 1; idx.push(a, b, a + 1, b, b + 1, a + 1);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx); g.computeVertexNormals(); tint(g, 0);
  return g;
}

// Melena: lámina que nace en el contorno del casquete (lados y nuca) y cae; puntas en mechones
function geoMelena(largo, t, puntas, viento = 0, swing = 0) {
  const segU = 72, segV = 44, pos = [], uv = [], idx = [];
  const gap = 1.15;                                      // hueco delante para la cara (radianes)
  const th0 = Math.PI / 2 + gap / 2, span = Math.PI * 2 - gap;
  for (let j = 0; j <= segV; j++) {
    const v = j / segV;
    for (let i = 0; i <= segU; i++) {
      const u = i / segU, th = th0 + span * u;
      const clumps = 0.5 + 0.5 * Math.sin(u * 2 * Math.PI * 9);              // 9 mechones grandes
      const tipCut = v > 0.86 ? (1 - 0.12 * Math.pow(clumps, 2) - 0.05 * puntas * Math.sin(u * 61)) : 1;
      const y = 0.05 - (largo + 0.25) * v * tipCut;
      const spread = Math.min(1, (largo * v) / 0.9);
      const r = 0.62 + 0.16 * Math.sin(Math.min(1, v * 3) * Math.PI / 2) + 0.18 * spread
        + 0.035 * clumps * Math.min(1, v * 4);
      const sway = 0.05 * v * v * Math.sin(t * 1.2 + u * 3) + swing * v * v;
      const back = -viento * v * v * (largo + 0.25) * 0.45 - 0.04 * viento * Math.sin(t * 9 + u * 7) * v;
      pos.push(Math.cos(th) * r * 0.98 + sway, y + viento * v * v * 0.15, Math.sin(th) * r * 0.88 - 0.06 + back);
      uv.push(u * 9, v);
    }
  }
  for (let j = 0; j < segV; j++) for (let i = 0; i < segU; i++) {
    const a = j * (segU + 1) + i, b = a + segU + 1; idx.push(a, b, a + 1, b, b + 1, a + 1);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx); g.computeVertexNormals(); tint(g, puntas);
  return g;
}

// Mechón delantero (sobre el hombro y el pecho), plano y afilado en la punta
function geoMechon(largo, s, t, puntas) {
  const pts = [];
  for (let k = 0; k <= 20; k++) {
    const v = k / 20;
    pts.push(new THREE.Vector3(s * (0.5 + 0.28 * Math.sin(Math.min(1, v * 2.2) * Math.PI / 2)) + 0.03 * Math.sin(t * 1.3 + v * 4),
      -0.05 - largo * v, 0.28 + 0.18 * Math.sin(v * 2.5)));
  }
  const curve = new THREE.CatmullRomCurve3(pts);
  const g = new THREE.TubeGeometry(curve, 60, 0.13, 18, false);
  const p = g.attributes.position, uv = g.attributes.uv;
  for (let i = 0; i < p.count; i++) {
    const v = uv.getX(i), c = curve.getPoint(v), k = 1 - 0.8 * Math.pow(v, 2);
    p.setX(i, c.x + (p.getX(i) - c.x) * k * 1.25);
    p.setZ(i, c.z + (p.getZ(i) - c.z) * k * 0.45);
    uv.setXY(i, uv.getY(i) * 3, v);
  }
  g.computeVertexNormals(); tint(g, puntas);
  return g;
}

// Flequillo: cae sobre la frente; con 6-9 cm tapa los ojos (fase incómoda)
function geoFlequillo(cm, t) {
  const drop = Math.min(cm, 9) / 9;
  const segU = 40, segV = 14, pos = [], uv = [], idx = [];
  for (let j = 0; j <= segV; j++) {
    const v = j / segV;
    for (let i = 0; i <= segU; i++) {
      const u = i / segU, th = Math.PI / 2 + (u - 0.5) * 2.0;
      const phi = Math.PI * (0.12 + (0.2 + 0.24 * drop) * v);
      const R = 0.68 + 0.05 * v;
      const tips = v > 0.8 ? 0.03 * Math.sin(u * 2 * Math.PI * 7) : 0;
      pos.push(Math.cos(th) * Math.sin(phi) * R * 0.97, Math.cos(phi) * R * 1.07 + 0.03 + tips + 0.01 * Math.sin(t + u * 6),
        Math.sin(th) * Math.sin(phi) * R * 1.02);
      uv.push(u * 2, v * 0.4);
    }
  }
  for (let j = 0; j < segV; j++) for (let i = 0; i < segU; i++) {
    const a = j * (segU + 1) + i, b = a + segU + 1; idx.push(a, b, a + 1, b, b + 1, a + 1);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx); g.computeVertexNormals(); tint(g, 0);
  return g;
}

const CARAS = {
  normal: { brow: 0, tilt: 0, mouth: 'smile', lid: 0.15 },
  feliz: { brow: 0.03, tilt: 0, mouth: 'big', lid: 0.05 },
  sorprendido: { brow: 0.07, tilt: 0, mouth: 'o', lid: -0.1 },
  agobiado: { brow: -0.01, tilt: 0.3, mouth: 'frown', lid: 0.3, sweat: true },
  triste: { brow: -0.02, tilt: 0.35, mouth: 'frown', lid: 0.4 },
  pensativo: { brow: 0.02, tilt: -0.2, mouth: 'flat', lid: 0.3 },
};

// Actualiza el personaje para un fotograma
const cache = {};
export function poser(p, { cm = 2, t = 0, cara = 'normal', puntas = 0, mirar = 0, andar = 0, paso = 0, viento = 0, tiron = 0 }) {
  const U = p.userData;
  const largo = Math.max(0, cm) * 0.03;      // 75 cm ≈ hasta la cintura
  const ex = CARAS[cara] || CARAS.normal;
  const kc = Math.round(cm * 4) / 4;
  if (cache.cap !== Math.round(Math.min(cm, 25))) { U.cap.geometry.dispose(); U.cap.geometry = geoCasquete(cm); cache.cap = Math.round(Math.min(cm, 25)); }
  U.mane.visible = cm > 5;
  const swing = andar * 0.12 * Math.sin(paso);
  if (U.mane.visible) { U.mane.geometry.dispose(); U.mane.geometry = geoMelena(largo, t, puntas, viento + andar * 0.25, swing); }
  U.locks.forEach((l, k) => {
    l.visible = cm > 22;
    if (l.visible) { l.geometry.dispose(); l.geometry = geoMechon(largo - 0.35, k ? 1 : -1, t + k, puntas); }
  });
  U.fringe.visible = cm > 2 && cm < 15;
  if (U.fringe.visible) { U.fringe.geometry.dispose(); U.fringe.geometry = geoFlequillo(cm, t); }
  // ojos y cara
  const blink = (t % 3.3) < 0.12;
  U.lids.forEach(l => { l.rotation.x = blink ? -0.1 : -1.35 + ex.lid; });
  U.brows.forEach((b, k) => { const s = k ? 1 : -1; b.position.y = 0.26 + ex.brow; b.rotation.z = Math.PI / 2 + s * ex.tilt; });
  U.pupils.forEach(arr => arr.forEach(m => { m.position.x = (m.userData.x0 ??= m.position.x) + 0.02 * mirar; }));
  U.mouth.visible = ex.mouth !== 'o'; U.mouthO.visible = ex.mouth === 'o';
  if (ex.mouth === 'smile') { U.mouth.rotation.set(0, 0, Math.PI); U.mouth.scale.set(1, 0.8, 1); U.mouth.position.y = -0.24; }
  if (ex.mouth === 'big') { U.mouth.rotation.set(0, 0, Math.PI); U.mouth.scale.set(1.35, 1.2, 1); U.mouth.position.y = -0.22; }
  if (ex.mouth === 'frown') { U.mouth.rotation.set(0, 0, 0); U.mouth.scale.set(0.8, 0.55, 1); U.mouth.position.y = -0.34; }
  if (ex.mouth === 'flat') { U.mouth.rotation.set(0, 0, Math.PI); U.mouth.scale.set(0.8, 0.12, 1); U.mouth.position.y = -0.29; }
  U.sweat.visible = !!ex.sweat;
  if (ex.sweat) U.sweat.position.set(0.48, 0.32 - ((t * 0.25) % 0.25), 0.36);
  U.head.rotation.y = 0.1 * Math.sin(t * 0.5);
  U.head.rotation.z = 0.025 * Math.sin(t * 0.8);
  U.head.rotation.x = 0.03 * Math.sin(t * 0.6);
  U.torso.scale.y = 1 + 0.008 * Math.sin(t * 2);
  // andar: piernas, brazos y rebote del cuerpo
  U.legs.forEach(({ leg, knee }, k) => {
    const ph = paso + (k ? Math.PI : 0);
    leg.rotation.x = andar * 0.5 * Math.sin(ph);
    knee.rotation.x = andar * Math.max(0, 0.75 * Math.sin(ph - 1.4));
  });
  U.arms.forEach((a, k) => { a.rotation.x = 0.04 * Math.sin(t * 1.1 + k) - andar * 0.45 * Math.sin(paso + (k ? 0 : Math.PI)); });
  p.position.y = (p.userData.y0 ??= p.position.y) + andar * 0.06 * Math.abs(Math.sin(paso)) - tiron * 0.05;
  U.head.rotation.x += -tiron * 0.35;
  U.torso.rotation.x = -tiron * 0.12;
}

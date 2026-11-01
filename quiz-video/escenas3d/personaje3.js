// Personaje 3D v3 para «¿QUÉ PASARÍA SI…?» — cabeza esculpida (una malla deformada), ojos con párpados,
// cuerpo adulto con camiseta y PELO HECHO CON MECHONES (cientos de cintas con textura de pelo) que
// crecen en cm y caen sobre los hombros. Paleta apagada (sin colores saturados).
import * as THREE from './three.module.min.js';

const SKIN = 0xd9a283, SHIRT = 0x5a7391, PANTS = 0x343a44;
const HEAD_Y = 0.05, HR = 0.6;              // centro y radio base de la cabeza

function rng(seed) { let s = seed; return () => (s = (s * 16807) % 2147483647) / 2147483647; }

// ---------------------------------------------------------------- texturas de pelo
function strandTexture() {
  const c = document.createElement('canvas'); c.width = 128; c.height = 512;
  const g = c.getContext('2d'); g.clearRect(0, 0, 128, 512);
  const r = rng(11);
  for (let i = 0; i < 140; i++) {                      // pelos finos que forman un mechón afilado
    const x0 = 6 + r() * 116, w = 0.8 + r() * 1.8, l = 12 + r() * 22;
    g.strokeStyle = `hsla(24, ${22 + r() * 14}%, ${l}%, ${0.6 + r() * 0.4})`; g.lineWidth = w;
    g.beginPath(); g.moveTo(x0, 0);
    const xe = 64 + (x0 - 64) * (0.25 + r() * 0.3);
    g.bezierCurveTo(x0, 200, xe + (r() - 0.5) * 20, 380, xe + (r() - 0.5) * 16, 470 + r() * 40); g.stroke();
  }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  return t;
}
function scalpTexture() {
  const c = document.createElement('canvas'); c.width = 512; c.height = 256;
  const g = c.getContext('2d'); g.fillStyle = '#2a1b12'; g.fillRect(0, 0, 512, 256);
  const r = rng(5);
  for (let i = 0; i < 1500; i++) { g.strokeStyle = `hsla(24,28%,${10 + r() * 16}%,0.6)`; g.lineWidth = 1 + r() * 2;
    const x = r() * 512; g.beginPath(); g.moveTo(x, 0); g.lineTo(x + (r() - 0.5) * 10, 256); g.stroke(); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return t;
}

// ---------------------------------------------------------------- cabeza esculpida
function geoCabeza() {
  const g = new THREE.SphereGeometry(1, 120, 90);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    let x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    const below = Math.max(0, -y);
    x *= 0.8 * (1 - 0.28 * Math.pow(below, 1.6));                 // mandíbula más estrecha
    z *= 0.9 * (1 - 0.12 * below);
    y *= 1.04;
    if (y < -0.55) y = -0.55 - (y + 0.55) * 0.75;                     // barbilla menos puntiaguda
    const front = Math.max(0, z);
    z += 0.06 * Math.exp(-((y + 0.85) ** 2) / 0.02) * front;          // barbilla adelante
    z += 0.04 * Math.exp(-((y - 0.28) ** 2) / 0.01) * Math.pow(front, 3); // arco de las cejas
    for (const s of [-1, 1]) {                                        // cuencas de los ojos y pómulos
      const d2 = (x - s * 0.33) ** 2 + (y - 0.12) ** 2;
      z -= 0.05 * Math.exp(-d2 / 0.012) * front;
      const c2 = (x - s * 0.42) ** 2 + (y + 0.15) ** 2;
      z += 0.03 * Math.exp(-c2 / 0.03) * front;
    }
    p.setXYZ(i, x * HR, y * HR, z * HR);
  }
  g.computeVertexNormals();
  return g;
}

function curvaTubo(pts, r, mat, seg = 24) {
  const c = new THREE.CatmullRomCurve3(pts.map(a => new THREE.Vector3(...a)));
  return new THREE.Mesh(new THREE.TubeGeometry(c, seg, r, 10, false), mat);
}

export function crearPersonaje() {
  const root = new THREE.Group();
  const skin = new THREE.MeshPhysicalMaterial({ color: SKIN, roughness: 0.58, sheen: 0.35, sheenColor: new THREE.Color(0xff9c80) });
  const shirt = new THREE.MeshStandardMaterial({ color: SHIRT, roughness: 0.95 });
  const pants = new THREE.MeshStandardMaterial({ color: PANTS, roughness: 0.9 });

  // ---- torso (perfil de revolución aplanado), cuello y piernas
  const lathe = (pr, s = 64) => new THREE.LatheGeometry(pr.map(([r, y]) => new THREE.Vector2(r, y)), s);
  const torso = new THREE.Mesh(lathe([[0, -2.0], [0.56, -1.98], [0.56, -1.7], [0.58, -1.35], [0.68, -0.98], [0.76, -0.78],
    [0.72, -0.62], [0.5, -0.5], [0.24, -0.44], [0, -0.44]]), shirt);
  torso.scale.set(1.12, 1, 0.62); torso.castShadow = torso.receiveShadow = true; root.add(torso);
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.19, 0.22, 0.34, 32), skin);
  neck.position.y = -0.4; root.add(neck);
  const collar = new THREE.Mesh(new THREE.TorusGeometry(0.2, 0.03, 10, 40), new THREE.MeshStandardMaterial({ color: 0x4b6280, roughness: 0.95 }));
  collar.rotation.x = Math.PI / 2; collar.scale.set(1.15, 0.85, 1); collar.position.y = -0.47; root.add(collar);
  const hips = new THREE.Mesh(new THREE.SphereGeometry(0.6, 40, 20), pants);
  hips.scale.set(1.1, 0.42, 0.62); hips.position.y = -2.0; hips.castShadow = true; root.add(hips);
  const legs = [];
  for (const s of [-1, 1]) {
    const leg = new THREE.Group(); leg.position.set(s * 0.32, -2.08, 0); root.add(leg);
    const th = new THREE.Mesh(new THREE.CapsuleGeometry(0.23, 0.6, 8, 24), pants); th.position.y = -0.42; th.castShadow = true; leg.add(th);
    const knee = new THREE.Group(); knee.position.y = -0.85; leg.add(knee);
    const sh = new THREE.Mesh(new THREE.CapsuleGeometry(0.2, 0.6, 8, 24), pants); sh.position.y = -0.4; sh.castShadow = true; knee.add(sh);
    const shoe = new THREE.Mesh(new THREE.CapsuleGeometry(0.16, 0.3, 8, 20), new THREE.MeshStandardMaterial({ color: 0xe8e4dc, roughness: 0.6 }));
    shoe.rotation.x = Math.PI / 2; shoe.position.set(0, -0.82, 0.1); shoe.castShadow = true; knee.add(shoe);
    legs.push({ leg, knee });
  }
  // brazos con codo y mano
  const arms = [];
  for (const s of [-1, 1]) {
    const sh = new THREE.Group(); sh.position.set(s * 0.8, -0.72, 0); root.add(sh);
    const up = new THREE.Mesh(new THREE.CapsuleGeometry(0.17, 0.5, 8, 20), shirt); up.position.y = -0.3; up.castShadow = true; sh.add(up);
    const elbow = new THREE.Group(); elbow.position.y = -0.62; sh.add(elbow);
    const fore = new THREE.Mesh(new THREE.CapsuleGeometry(0.12, 0.5, 8, 20), skin); fore.position.y = -0.32; fore.castShadow = true; elbow.add(fore);
    const hand = new THREE.Group(); hand.position.y = -0.68; elbow.add(hand);
    const palm = new THREE.Mesh(new THREE.SphereGeometry(0.13, 24, 16), skin); palm.scale.set(0.85, 1.1, 0.55); hand.add(palm);
    const thumb = new THREE.Mesh(new THREE.CapsuleGeometry(0.04, 0.09, 6, 10), skin); thumb.position.set(-s * 0.1, 0.02, 0.05); thumb.rotation.z = s * 0.6; hand.add(thumb);
    sh.rotation.z = s * 0.08; arms.push({ sh, elbow, hand });
  }

  // ---- cabeza
  const head = new THREE.Group(); head.position.y = HEAD_Y; root.add(head);
  const skull = new THREE.Mesh(geoCabeza(), skin); skull.castShadow = true; head.add(skull);
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.075, 32, 24), skin);
  nose.scale.set(0.7, 1.7, 0.9); nose.position.set(0, -0.01, 0.55); nose.rotation.x = 0.3; head.add(nose);
  const tip = new THREE.Mesh(new THREE.SphereGeometry(0.042, 24, 16), skin); tip.scale.set(1.2, 0.9, 1); tip.position.set(0, -0.1, 0.585); head.add(tip);
  for (const s of [-1, 1]) {
    const ear = new THREE.Mesh(new THREE.SphereGeometry(0.11, 24, 16), skin);
    ear.scale.set(0.4, 1.05, 0.7); ear.position.set(s * 0.47, 0.0, -0.02); ear.rotation.y = s * 0.3; head.add(ear);
  }
  // ojos: blanco ligeramente hundido, iris, brillo, párpados y línea de pestañas
  const white = new THREE.MeshPhysicalMaterial({ color: 0xf3efe9, roughness: 0.15, clearcoat: 1 });
  const irisM = new THREE.MeshPhysicalMaterial({ color: 0x4a3324, roughness: 0.2, clearcoat: 1 });
  const dark = new THREE.MeshStandardMaterial({ color: 0x1e140e, roughness: 0.7 });
  const eyes = [], lids = [], brows = [];
  for (const s of [-1, 1]) {
    const g = new THREE.Group(); g.position.set(s * 0.2, 0.07, 0.46); head.add(g);
    const e = new THREE.Mesh(new THREE.SphereGeometry(0.075, 32, 24), white); e.scale.set(1.15, 0.85, 0.7); g.add(e);
    const look = new THREE.Group(); g.add(look);
    const ir = new THREE.Mesh(new THREE.CircleGeometry(0.043, 32), irisM); ir.position.z = 0.054; look.add(ir);
    const pu = new THREE.Mesh(new THREE.CircleGeometry(0.02, 24), new THREE.MeshBasicMaterial({ color: 0x0a0705 })); pu.position.z = 0.055; look.add(pu);
    const hl = new THREE.Mesh(new THREE.CircleGeometry(0.01, 12), new THREE.MeshBasicMaterial({ color: 0xffffff })); hl.position.set(0.014, 0.016, 0.056); look.add(hl);
    const lid = new THREE.Mesh(new THREE.SphereGeometry(0.08, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), skin);
    lid.scale.set(1.18, 0.9, 0.76); lid.rotation.x = -1.2; g.add(lid);
    const lash = curvaTubo([[-0.085, 0.005, 0.03], [-0.04, 0.045, 0.05], [0.03, 0.05, 0.05], [0.09, 0.015, 0.03]].map(([x, y, z]) => [x * s, y, z]), 0.009, dark);
    g.add(lash);
    const lower = new THREE.Mesh(new THREE.SphereGeometry(0.079, 32, 16, 0, Math.PI * 2, Math.PI * 0.62, Math.PI * 0.38), skin);
    lower.scale.set(1.16, 0.88, 0.74); g.add(lower);
    eyes.push({ g, look, lash }); lids.push(lid);
    const brow = curvaTubo([[-0.11, -0.01, 0], [-0.04, 0.02, 0.02], [0.05, 0.02, 0.015], [0.11, -0.005, -0.01]].map(([x, y, z]) => [x * s, y, z]), 0.016,
      new THREE.MeshStandardMaterial({ color: 0x3a2619, roughness: 0.9 }));
    brow.position.set(s * 0.2, 0.2, 0.5); head.add(brow); brows.push(brow);
  }
  // boca: labios finos (tubo) que cambian de curva según la expresión
  const lipM = new THREE.MeshStandardMaterial({ color: 0xa8645a, roughness: 0.6 });
  const mouth = new THREE.Mesh(new THREE.BufferGeometry(), lipM); head.add(mouth);
  const mouthO = new THREE.Mesh(new THREE.SphereGeometry(0.045, 24, 16), new THREE.MeshStandardMaterial({ color: 0x4d1f1f, roughness: 0.7 }));
  mouthO.scale.set(0.9, 1.15, 0.4); mouthO.position.set(0, -0.27, 0.5); head.add(mouthO);

  // ---- pelo: casquete con textura + mechones
  // cuero cabelludo con la MISMA línea del pelo que las raíces (frente libre)
  const sp = [], su = [], si = [], NU = 96, NV = 24;
  for (let j = 0; j <= NV; j++) for (let i = 0; i <= NU; i++) {
    const az = i / NU * Math.PI * 2, front = Math.cos(az - Math.PI);
    const pol = (j / NV) * (1.52 - 0.95 * Math.max(0, front) ** 1.1);
    const q = scalpPoint(az, pol, -0.004); sp.push(q.x, q.y - HEAD_Y, q.z); su.push(i / NU * 4, j / NV);
  }
  for (let j = 0; j < NV; j++) for (let i = 0; i < NU; i++) { const a = j * (NU + 1) + i, b = a + NU + 1; si.push(a, b, a + 1, b, b + 1, a + 1); }
  const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.Float32BufferAttribute(sp, 3));
  sg.setAttribute('uv', new THREE.Float32BufferAttribute(su, 2)); sg.setIndex(si); sg.computeVertexNormals();
  const scalp = new THREE.Mesh(sg, new THREE.MeshStandardMaterial({ map: scalpTexture(), roughness: 0.75, side: THREE.DoubleSide }));
  head.add(scalp);
  const hairMat = new THREE.MeshPhysicalMaterial({ map: strandTexture(), alphaTest: 0.35, side: THREE.DoubleSide,
    roughness: 0.5, sheen: 0.6, sheenColor: new THREE.Color(0x6b4a34), sheenRoughness: 0.4, color: 0xc8b6a8, vertexColors: true });
  const hair = new THREE.Mesh(new THREE.BufferGeometry(), hairMat); hair.castShadow = true; root.add(hair);
  const under = new THREE.Mesh(new THREE.BufferGeometry(), new THREE.MeshStandardMaterial({ color: 0x24170f, roughness: 0.8, side: THREE.DoubleSide }));
  root.add(under);

  // raíces de los mechones (sobre el cuero cabelludo, sin la cara)
  const r = rng(3), roots = [];
  for (let i = 0; i < 900; i++) {
    const az = r() * Math.PI * 2;                      // 0 = atrás (z-), π = delante (z+)
    const pol = Math.acos(1 - r() * 0.9) * 0.95;        // desde la coronilla
    const front = Math.cos(az - Math.PI);               // 1 delante
    const maxPol = 1.5 - 0.95 * Math.max(0, front) ** 1.1;  // la línea del pelo deja libre la frente
    if (pol > maxPol) continue;
    roots.push({ az, pol, w: 0.045 + r() * 0.04, j: r(), k: r() });
  }
  root.userData = { head, skull, eyes, lids, brows, mouth, mouthO, hair, under, roots, scalp, torso, arms, legs, collar };
  return root;
}

// posición sobre el cuero cabelludo (coords de la cabeza → mundo del personaje)
function scalpPoint(az, pol, lift = 0) {
  const R = HR * 1.02 + lift;
  const x = Math.sin(pol) * Math.sin(az) * R * 0.82;
  const y = Math.cos(pol) * R * 1.06;
  const z = -Math.sin(pol) * Math.cos(az) * R * 0.92;
  return new THREE.Vector3(x, y + HEAD_Y + 0.01, z);
}

// Radio del "obstáculo" (cabeza + hombros + espalda) a una altura y
function bodyRadius(y, az) {
  const head = y > HEAD_Y - 0.55 ? HR * 0.92 * Math.sqrt(Math.max(0, 1 - ((y - HEAD_Y) / (HR * 1.1)) ** 2)) + 0.04 : 0;
  let torso = 0;
  if (y < -0.5) {
    const sx = 0.86, sz = 0.52;                      // hombros/espalda (elipse)
    const k = Math.min(1, (-0.5 - y) / 0.35);
    const ex = sx * (0.6 + 0.4 * k), ez = sz * (0.6 + 0.4 * k);
    const c = Math.cos(az), s = Math.sin(az);
    torso = 1 / Math.sqrt((s / ex) ** 2 + (c / ez) ** 2) + 0.05;
  } else if (y < -0.25) torso = 0.3;
  return Math.max(head, torso);
}

// Construye todos los mechones para una longitud (cm)
function buildHair(U, cm, t, o) {
  const L = Math.max(0.01, cm) * 0.033;                // 75 cm ≈ cintura
  const pos = [], uv = [], col = [], idx = [];
  let base = 0;
  const SEG = 22;
  for (const rt of U.roots) {
    const len = L * (0.85 + 0.3 * rt.j) + 0.02;
    const front = Math.cos(rt.az - Math.PI);
    // flequillo: entre ~5 y 13 cm los mechones de delante caen hacia la frente; luego se apartan a los lados
    const fr = front > 0.55 ? Math.max(0, Math.min(1, (cm - 3) / 3)) * Math.max(0, Math.min(1, (14 - cm) / 3)) * (o.flequillo ?? 1) : 0;
    const partSide = rt.az > Math.PI ? 1 : -1;
    const pts = [];
    let p = scalpPoint(rt.az, rt.pol, 0.004);
    pts.push(p.clone());
    let az = rt.az, pol = rt.pol, y = p.y, step = len / SEG;
    for (let k = 1; k <= SEG; k++) {
      const v = k / SEG;
      if (fr > 0) {                                    // flequillo: avanza hacia delante y abajo
        pol += step / (HR) * 1.1;
        p = scalpPoint(az, Math.min(pol, 1.9), 0.01 + 0.03 * v);
        p.y -= v * 0.02;
      } else if (pol < 1.75 && y > HEAD_Y - HR * 0.5) {  // sigue la curva de la cabeza hacia abajo
        pol += step / HR;
        if (front > 0.2) az += partSide * step * 1.4 * front;   // se aparta de la cara
        p = scalpPoint(az, pol, 0.012 + 0.01 * v);
      } else {                                         // cae por gravedad rozando hombros y espalda
        y -= step;
        const swayA = (o.viento || 0) * 0.35 * v + 0.03 * Math.sin(t * 1.4 + rt.k * 6) * v;
        const rad = bodyRadius(y, az) * (1 + 0.04 * rt.k) + 0.015 * k / SEG;
        p = new THREE.Vector3(Math.sin(az) * rad, y, -Math.cos(az) * rad - swayA * 0.5);
        p.x += (o.swing || 0) * v * v;
      }
      y = p.y;
      pts.push(p.clone());
    }
    // cinta orientada según la superficie (normal radial respecto al eje del cuerpo)
    const tip = Math.max(0, (cm - 12) / 60) * (o.puntas || 0);
    for (let k = 0; k <= SEG; k++) {
      const a = pts[k], b = pts[Math.min(SEG, k + 1)], c0 = pts[Math.max(0, k - 1)];
      const tan = b.clone().sub(c0).normalize();
      const radial = new THREE.Vector3(a.x, 0, a.z - 0.0).normalize();
      if (a.y > HEAD_Y - HR * 0.6) radial.set(a.x, a.y - HEAD_Y, a.z).normalize();
      const side = new THREE.Vector3().crossVectors(tan, radial).normalize().multiplyScalar(rt.w * (1 - 0.5 * (k / SEG)) * (0.6 + Math.min(1, L * 2)));
      for (const sgn of [-1, 1]) {
        const q = a.clone().addScaledVector(side, sgn);
        pos.push(q.x, q.y, q.z); uv.push(sgn < 0 ? 0 : 1, k / SEG);
        const v = k / SEG, light = 0.85 + 0.25 * rt.k;   // variación de tono entre mechones
        const dry = tip * Math.max(0, (v - 0.75) / 0.25);
        col.push(light + dry * 0.9, light + dry * 0.65, light + dry * 0.4);
      }
    }
    for (let k = 0; k < SEG; k++) { const a = base + k * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
    base += (SEG + 1) * 2;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
  g.setIndex(idx); g.computeVertexNormals();
  return g;
}

function buildUnder(cm) {
  const L = Math.max(0, cm) * 0.033;
  const top = HEAD_Y - HR * 0.35, bottom = HEAD_Y - HR * 0.35 - L * 0.92;
  const segU = 48, segV = 30, pos = [], idx = [];
  const gap = 3.3, a0 = Math.PI + gap / 2, span = Math.PI * 2 - gap;     // solo detrás (espalda)
  for (let j = 0; j <= segV; j++) {
    const y = top + (bottom - top) * j / segV;
    for (let i = 0; i <= segU; i++) {
      const az = a0 + span * i / segU;
      const rad = bodyRadius(y, az) * 0.94;
      pos.push(Math.sin(az) * rad, y, -Math.cos(az) * rad);
    }
  }
  for (let j = 0; j < segV; j++) for (let i = 0; i < segU; i++) {
    const a = j * (segU + 1) + i, b = a + segU + 1; idx.push(a, b, a + 1, b, b + 1, a + 1);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
  return g;
}

function setMouth(U, kind) {
  const s = { smile: [0.006, -0.018], flat: [0, 0], frown: [-0.004, 0.015], big: [0.012, -0.03] }[kind] || [0, 0];
  const pts = [[-0.085, s[0] * 0 - s[1] * 0.3, 0], [-0.04, s[1], 0.012], [0.04, s[1], 0.012], [0.085, -s[1] * 0.3, 0]]
    .map(([x, y, z]) => new THREE.Vector3(x, y - 0.26, z + 0.5));
  // las comisuras suben (sonrisa) o bajan (pena)
  pts[0].y += s[0] * 3; pts[3].y += s[0] * 3;
  U.mouth.geometry.dispose();
  U.mouth.geometry = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 20, 0.012, 8, false);
}

const CARAS = {
  normal: { m: 'smile', lid: 0.0, brow: 0, tilt: 0 },
  feliz: { m: 'big', lid: 0.08, brow: 0.015, tilt: 0 },
  sorprendido: { m: 'o', lid: -0.25, brow: 0.04, tilt: 0 },
  agobiado: { m: 'frown', lid: 0.2, brow: -0.01, tilt: 0.25 },
  triste: { m: 'frown', lid: 0.3, brow: 0, tilt: 0.3 },
  pensativo: { m: 'flat', lid: 0.25, brow: 0.01, tilt: -0.15 },
  molesto: { m: 'flat', lid: 0.3, brow: -0.02, tilt: -0.3 },
};

let lastMouth = null;
export function poser(P, o) {
  const U = P.userData, t = o.t || 0, cm = o.cm ?? 1;
  U.hair.geometry.dispose();
  U.hair.geometry = buildHair(U, cm, t, o);
  U.under.visible = cm > 12;
  if (U.under.visible) { U.under.geometry.dispose(); U.under.geometry = buildUnder(cm); }
  U.scalp.visible = true;
  const ex = CARAS[o.cara] || CARAS.normal;
  const blink = (t % 3.7) < 0.12 || o.ojosCerrados;
  U.lids.forEach(l => { l.rotation.x = blink ? 0.15 : -1.2 + ex.lid; });
  U.eyes.forEach(({ look }) => { look.position.set(0.012 * (o.mirarX || 0), 0.01 * (o.mirarY || 0), 0); });
  U.brows.forEach((b, k) => { const s = k ? 1 : -1; b.position.y = 0.2 + ex.brow; b.rotation.z = s * ex.tilt * -0.5; });
  if (lastMouth !== ex.m) { if (ex.m !== 'o') setMouth(U, ex.m); lastMouth = ex.m; }
  U.mouth.visible = ex.m !== 'o'; U.mouthO.visible = ex.m === 'o';
  // cabeza viva, respiración
  U.head.rotation.y = (o.girarCabeza || 0) + 0.06 * Math.sin(t * 0.5);
  U.head.rotation.x = (o.inclinar || 0) + 0.02 * Math.sin(t * 0.7);
  U.head.rotation.z = 0.015 * Math.sin(t * 0.9);
  U.torso.scale.y = 1 + 0.006 * Math.sin(t * 1.8);
  // brazos: pose libre (rot hombro/codo) o reposo
  U.arms.forEach(({ sh, elbow }, k) => {
    const s = k ? 1 : -1, a = (o.brazos || [])[k];
    sh.rotation.set(a ? a[0] : 0.03 * Math.sin(t + k), 0, s * (a ? a[1] : 0.08));
    elbow.rotation.set(a ? a[2] : 0.05, 0, 0);
  });
  U.legs.forEach(({ leg, knee }, k) => {
    const ph = (o.paso || 0) + (k ? Math.PI : 0), an = o.andar || 0;
    leg.rotation.x = an * 0.45 * Math.sin(ph); knee.rotation.x = an * Math.max(0, 0.7 * Math.sin(ph - 1.4));
  });
  // el pelo pertenece al personaje pero no gira con la cabeza: compensación ligera
  U.hair.rotation.y = U.head.rotation.y * 0.6;
}

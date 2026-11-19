// Renderiza fotogramas 3D: node render3d.js estados.json carpeta_salida inicio fin
// estados.json = lista de estados (uno por fotograma). Escribe JPG con nombre f_000123.jpg.
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [, , file, out, a, b] = process.argv;
  const st = JSON.parse(fs.readFileSync(file, 'utf8'));
  const i0 = +a || 0, i1 = Math.min(+b || st.length, st.length);
  const br = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pg = await br.newPage({ viewport: { width: 1080, height: 1920 } });
  pg.on('pageerror', e => console.error('ERR', e.message));
  pg.on('console', m => { if (m.type() === 'error') console.error('CONSOLE', m.text()); });
  await pg.goto('http://127.0.0.1:8765/escenas3d/escena.html');
  await pg.waitForFunction(() => window.ok === true);
  await pg.evaluate(() => window.listo);
  const t0 = Date.now();
  for (let i = i0; i < i1; i++) {
    await pg.evaluate(s => window.pintar(s), st[i]);
    const buf = await pg.screenshot({ type: 'jpeg', quality: 92 });
    fs.writeFileSync(`${out}/f_${String(i).padStart(6, '0')}.jpg`, buf);
  }
  console.log(`hecho ${i1 - i0} fotogramas en ${((Date.now() - t0) / 1000).toFixed(1)} s`);
  await br.close();
})();

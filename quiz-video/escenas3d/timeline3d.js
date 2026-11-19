// Renderiza una escena con guion propio: node timeline3d.js pagina.html carpeta fps [t0] [t1] [solo_tiempos_csv]
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [, , page, out, fpsS, a, b, list] = process.argv;
  const fps = +fpsS || 30;
  const br = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pg = await br.newPage({ viewport: { width: 720, height: 1280 } });
  pg.on('pageerror', e => console.error('ERR', e.message));
  pg.on('console', m => { if (m.type() === 'error') console.error('CONSOLE', m.text()); });
  await pg.goto(`http://127.0.0.1:8765/escenas3d/${page}`);
  await pg.waitForFunction(() => window.ok === true, null, { timeout: 60000 });
  const dur = await pg.evaluate(() => window.DUR);
  let times = [];
  if (list) times = list.split(',').map(Number);
  else { const t0 = +a || 0, t1 = b ? +b : dur; for (let i = Math.round(t0 * fps); i < Math.round(t1 * fps); i++) times.push(i / fps); }
  const st = Date.now();
  for (const t of times) {
    await pg.evaluate(t => window.frame(t), t);
    const buf = await pg.screenshot({ type: 'jpeg', quality: 93 });
    fs.writeFileSync(`${out}/f_${String(Math.round(t * fps)).padStart(6, '0')}.jpg`, buf);
  }
  console.log(`${times.length} fotogramas en ${((Date.now() - st) / 1000).toFixed(1)} s`);
  await br.close();
})();

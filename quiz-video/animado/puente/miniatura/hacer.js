// Miniatura 9:16 (+ 3:4): el puente A MEDIO CONSTRUIR (tablero subiendo por tramos) con la pregunta del gancho.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(3000);
  await p.evaluate(() => {
    window.__timelines.main.seek(3.0);
    for (const s of ['#subs', '#grano', '#fxl', '#lineas', '#pasos']) document.querySelectorAll(s).forEach(e => e.style.display = 'none');
    const E = window.ESC; Object.assign(E.st, { dov: 0.3, asf: 0, luz: 0, coches: 0, pen: 1, hilo: 1 });
    E.pon(-1000 * 0.9, 640 * 0.9, 1080 * 0.9, 0, 110, 0, 0.82); E.aplica(); E.render();
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90;font-family:Inter;text-align:center';
    const sh = 'text-shadow:0 6px 24px rgba(8,30,60,0.55)';
    d.innerHTML = `
      <div style="position:absolute;left:0;right:0;top:270px">
        <div style="font:800 54px Inter;letter-spacing:1px;color:#fff;${sh}">¿CÓMO SE CONSTRUYE</div>
        <div style="margin-top:6px;font:900 150px/0.95 Inter;letter-spacing:-6px;color:#fff;${sh}">UN PUENTE</div>
        <div style="margin-top:6px;font:800 66px Inter;letter-spacing:1px;color:#fff;${sh}">SOBRE EL MAR?</div></div>
      <div style="position:absolute;left:0;right:0;top:1470px"><span style="display:inline-block;padding:18px 36px;border-radius:24px;background:rgba(14,30,52,0.82);font:700 44px Inter;color:#fff">1.000 m · <span style="color:#4ea3ff">0 columnas</span> en el agua</span></div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(800);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await p.screenshot({ path: dir + '/miniatura/miniatura_tiktok_3x4.png', clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await b.close();
})();

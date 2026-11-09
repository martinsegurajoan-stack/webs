// Miniatura 9:16 (+ 3:4): el puente terminado de noche con titular sobrio.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(3000);
  await p.evaluate(() => {
    window.__timelines.main.seek(5.0);
    for (const s of ['#subs', '#grano', '#fxl', '#lineas']) document.querySelectorAll(s).forEach(e => e.style.display = 'none');
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90;font-family:Inter;text-align:center';
    d.innerHTML = `
      <div style="position:absolute;left:0;right:0;top:300px">
        <div style="font:700 30px Inter;letter-spacing:10px;color:#4ea3ff">1.000 METROS DE MAR</div>
        <div style="margin-top:18px;font:800 132px/0.95 Inter;letter-spacing:-5px;color:#fff;text-shadow:0 10px 40px rgba(0,0,0,0.6)">NI UNA<br>COLUMNA</div>
        <div style="margin-top:22px;font:600 44px Inter;letter-spacing:2px;color:rgba(255,255,255,0.75)">¿Cómo se aguanta?</div></div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(800);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await p.screenshot({ path: dir + '/miniatura/miniatura_tiktok_3x4.png', clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await b.close();
})();

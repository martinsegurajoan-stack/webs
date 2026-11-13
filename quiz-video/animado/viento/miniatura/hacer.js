// Miniatura 9:16 (+ 3:4): la playa justo cuando el viento se para (cometa en el suelo, bandera caída) + titular.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => {
    window.__timelines.main.seek(9.0); frame();
    for (const s of ['#subs', '#grano', '#fxl', '#topsombra']) document.querySelectorAll(s).forEach(e => e.style.display = 'none');
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90;font-family:Inter;text-align:center';
    const sh = 'text-shadow:0 6px 24px rgba(8,30,60,0.6)';
    d.innerHTML = `
      <div style="position:absolute;left:0;right:0;top:250px">
        <div style="font:800 56px Inter;color:#fff;${sh}">¿Y SI MAÑANA EL</div>
        <div style="margin-top:4px;font:900 168px/0.95 Inter;letter-spacing:-6px;color:#fff;${sh}">VIENTO</div>
        <div style="margin-top:8px;font:800 62px Inter;color:#fff;${sh}">DESAPARECIERA?</div></div>
      <div style="position:absolute;left:0;right:0;top:1440px"><span style="display:inline-block;padding:16px 40px;border-radius:24px;background:rgba(14,30,52,0.86);font:300 110px Inter;letter-spacing:-3px;color:#ff6b5e">0 km/h</span></div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(600);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await p.screenshot({ path: dir + '/miniatura/miniatura_tiktok_3x4.png', clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await b.close();
})();

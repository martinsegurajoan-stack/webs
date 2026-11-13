// Miniatura 9:16 (+ 3:4): el planeta real con las partículas de viento + titular sobrio.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(3500);
  await p.evaluate(() => {
    window.__timelines.main.seek(1.5); S.sc = 470; frame();
    for (const s of ['#subs', '#grano', '#fxl', '#topsombra']) document.querySelectorAll(s).forEach(e => e.style.display = 'none');
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90;font-family:Inter;text-align:center';
    const sh = 'text-shadow:0 6px 30px rgba(0,0,0,0.9)';
    d.innerHTML = `
      <div style="position:absolute;left:0;right:0;top:250px">
        <div style="font:600 52px Inter;color:#fff;${sh}">¿Y si mañana el</div>
        <div style="margin-top:2px;font:800 170px/0.95 Inter;letter-spacing:-6px;color:#fff;${sh}">VIENTO</div>
        <div style="margin-top:10px;font:600 52px Inter;color:#fff;${sh}">se detuviera?</div></div>
      <div style="position:absolute;left:0;right:0;top:1500px;${sh}"><div style="font:700 22px Inter;letter-spacing:6px;color:#7fd3ff">EN TODO EL PLANETA</div><div style="font:200 130px/1.1 Inter;letter-spacing:-4px;color:#ff8a7e">0 km/h</div></div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(600);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await p.screenshot({ path: dir + '/miniatura/miniatura_tiktok_3x4.png', clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await b.close();
})();

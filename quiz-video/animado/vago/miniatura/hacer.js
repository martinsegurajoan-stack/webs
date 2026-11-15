// Miniatura 9:16 (+ 3:4 TikTok, contenido entre y 240-1680): sello VAGO + titular.
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(1500);
  await p.evaluate(() => {
    window.__timelines.main.seek(3.2);
    for (const s of ['#subs', '#grano', '#h1', '#h3']) document.querySelectorAll(s).forEach(e => e.style.visibility = 'hidden');
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90;font-family:Inter;text-align:center;color:#fff';
    const sh = 'text-shadow:0 8px 40px rgba(0,0,0,0.9)';
    d.innerHTML = `
      <div style="position:absolute;left:0;right:0;top:360px">
        <div style="font:700 64px Inter;${sh}">¿Y si dejas de hacer el</div></div>
      <div style="position:absolute;left:0;right:0;top:1330px">
        <div style="font:900 120px/1 Inter;letter-spacing:-3px;${sh}">y TRABAJAS?</div>
        <div style="margin-top:34px;font:700 40px Inter;letter-spacing:4px;color:#ffd166;${sh}">25 AÑOS EN EL SOFÁ DE PAPÁ 🛋️</div></div>`;
    document.querySelector('#root').appendChild(d);
    const h2 = document.querySelector('#h2'); h2.style.top = '680px'; h2.style.fontSize = '230px';
  });
  await p.waitForTimeout(400);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await p.screenshot({ path: dir + '/miniatura/miniatura_tiktok_3x4.png', clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await b.close();
})();

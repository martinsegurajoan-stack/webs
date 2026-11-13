// Portada 9:16: la puerta del final entreabierta con la luz saliendo y «¿QUÉ HAY DETRÁS?».
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(1500);
  await p.evaluate(() => {
    window.__timelines.main.seek(95.6);
    for (const s of ['#subs', '#marca', '#grano', '#negroF', '#topsombra']) { const e = document.querySelector(s); if (e) e.style.display = 'none'; }
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90';
    d.innerHTML = `
      <div style="position:absolute;inset:0;background:linear-gradient(rgba(2,3,6,0.9), rgba(2,3,6,0) 32%, rgba(2,3,6,0) 70%, rgba(2,3,6,0.7))"></div>
      <div style="position:absolute;left:0;right:0;top:250px;text-align:center;font-family:Inter;color:#fff">
        <div style="font:800 54px Inter;letter-spacing:14px;color:rgba(255,226,176,0.85)">¿QUÉ HAY</div>
        <div style="font:900 190px Inter;letter-spacing:-6px;line-height:0.95;color:#ffe2b0;text-shadow:0 0 60px rgba(255,190,110,0.55), 0 8px 30px rgba(0,0,0,0.6)">DETRÁS?</div></div>
      <div style="position:absolute;left:0;right:0;top:1660px;text-align:center;font:700 30px Inter;color:#fff;opacity:0.6">@mundo.supuesto</div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(600);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await b.close();
})();

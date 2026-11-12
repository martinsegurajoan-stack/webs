// Miniatura 9:16 (+ 3:4): el protagonista a 3,55 m junto a su casa (la puerta le llega por la cintura) + titular.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => {
    window.__timelines.main.seek(70.2); frame();
    for (const s of ['#subs', '#grano', '#fxl', '#hud', '#topsombra', '#sol']) document.querySelectorAll(s).forEach(e => e.style.display = 'none');
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90;font-family:Inter;text-align:center';
    const sh = 'text-shadow:0 6px 24px rgba(8,30,60,0.6)';
    d.innerHTML = `
      <div style="position:absolute;left:0;right:0;top:250px">
        <div style="font:800 52px Inter;color:#fff;${sh}">¿Y SI CADA VEZ QUE</div>
        <div style="margin-top:4px;font:900 128px/0.95 Inter;letter-spacing:-5px;color:#fff;${sh}">PARPADEAS</div>
        <div style="margin-top:6px;font:800 64px Inter;color:#fff;${sh}">CRECIERAS?</div></div>
      <div style="position:absolute;left:0;right:0;top:1500px"><span style="display:inline-block;padding:18px 36px;border-radius:24px;background:rgba(14,30,52,0.85);font:700 46px Inter;color:#fff">4 meses = <span style="color:#8cc4ff">3,55 m</span> · <span style="color:#ff6b5e">580 kg</span></span></div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(600);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await p.screenshot({ path: dir + '/miniatura/miniatura_tiktok_3x4.png', clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await b.close();
})();

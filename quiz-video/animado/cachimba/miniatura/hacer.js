// Miniatura 9:16 (+ recorte 3:4): pantalla partida a los 10 años, con el dinero gastado y el titular.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => {
    window.__timelines.main.seek(76.0);
    for (const s of ['#subs', '#grano', '#fxl']) document.querySelectorAll(s).forEach(e => e.style.display = 'none');
    document.querySelector('#cam').style.transform = 'none'; pinta(10);
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90;font-family:Inter;text-align:center';
    d.innerHTML = `
      <div style="position:absolute;left:0;right:0;top:250px">
        <div style="font:800 32px Inter;letter-spacing:8px;color:#ffc24a">DURANTE 10 AÑOS</div>
        <div style="margin-top:12px;font:900 76px/1.05 Inter;letter-spacing:-2px;color:#fff;text-shadow:0 8px 30px rgba(0,0,0,0.6)">¿QUIÉN ACABA PEOR?</div></div>
      <div style="position:absolute;right:50px;top:880px"><span style="display:inline-block;padding:10px 26px;border-radius:18px;background:rgba(10,6,22,0.88);border:3px solid #b98cff;font:900 70px Inter;color:#b98cff">87.600 €</span></div>
      <div style="position:absolute;left:0;right:0;top:1100px"><span style="display:inline-block;padding:6px 22px;border-radius:14px;background:#ff5a4f;font:900 46px Inter;color:#fff">VS</span></div>
      <div style="position:absolute;right:50px;top:1420px"><span style="display:inline-block;padding:10px 26px;border-radius:18px;background:rgba(10,6,22,0.88);border:3px solid #ff9a5a;font:900 70px Inter;color:#ff9a5a">73.000 🚬</span></div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(800);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await p.screenshot({ path: dir + '/miniatura/miniatura_tiktok_3x4.png', clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await b.close();
})();

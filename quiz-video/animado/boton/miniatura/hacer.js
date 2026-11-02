// Portada 9:16: persona sentada en una habitación luminosa con el botón rojo en primer plano y «¿PULSARÍAS EL BOTÓN?».
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(1500);
  await p.evaluate(() => {
    window.__timelines.main.seek(1.95);
    for (const s of ['#subs', '#gancho', '#marca', '#grano', '#negroF', '#topsombra', '#m1']) { const e = document.querySelector(s); if (e) e.style.display = 'none'; }
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90';
    d.innerHTML = `
      <div style="position:absolute;inset:0;background:linear-gradient(rgba(20,10,4,0.55), rgba(20,10,4,0) 34%)"></div>
      <div style="position:absolute;left:0;right:0;top:250px;text-align:center;font-family:Inter;color:#fff">
        <div style="font:800 64px Inter;letter-spacing:10px;text-shadow:0 4px 20px rgba(0,0,0,0.5)">¿PULSARÍAS</div>
        <div style="font:900 150px Inter;letter-spacing:-5px;line-height:1;color:#ffffff;text-shadow:0 8px 30px rgba(0,0,0,0.45)">EL <span style="color:#ff3b2f">BOTÓN?</span></div>
        <div style="display:inline-block;margin-top:22px;padding:10px 26px;border-radius:40px;background:rgba(14,20,34,0.55);font:800 40px Inter;color:#ffe08a">+1.000.000 €</div></div>
      <div style="position:absolute;left:0;right:0;top:1660px;text-align:center;font:700 30px Inter;color:#fff;opacity:0.7">@mundo.supuesto</div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(600);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await b.close();
})();

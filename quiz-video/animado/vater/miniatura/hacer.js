// Miniatura 9:16 (+ recorte 3:4 para TikTok): el avión en corte con la caca disparada por el tubo + título enorme.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(1500);
  await p.evaluate(() => {
    window.__timelines.main.seek(1.25);
    for (const s of ['#subs', '#gancho', '#marca', '#grano', '#negroF', '#topsombra', '.nota']) document.querySelectorAll(s).forEach(e => e.style.display = 'none');
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90;font-family:Inter;text-align:center';
    d.innerHTML = `
      <div style="position:absolute;left:0;right:0;top:0;height:640px;background:linear-gradient(rgba(8,18,40,0.82),rgba(8,18,40,0))"></div>
      <div style="position:absolute;left:0;right:0;top:300px">
        <div style="font:900 64px Inter;letter-spacing:6px;color:#fff;text-shadow:0 6px 24px rgba(0,0,0,0.5)">¿ADÓNDE VA</div>
        <div style="display:inline-block;margin-top:10px;padding:6px 34px 14px;background:#7a4a24;border:8px solid #fff;border-radius:26px;transform:rotate(-3deg);box-shadow:0 18px 40px rgba(0,0,0,0.45)">
          <div style="font:900 128px Inter;letter-spacing:-4px;line-height:1;color:#ffe08a">TU CACA?</div></div></div>
      <div style="position:absolute;left:0;right:0;top:1260px"><span style="display:inline-block;padding:16px 36px;border-radius:50px;background:linear-gradient(#4f9be8,#1f5fbf);border:5px solid #fff;font:900 50px Inter;color:#fff;box-shadow:0 10px 30px rgba(0,0,0,0.35)">✈ A 10.000 METROS</span></div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(600);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await p.screenshot({ path: dir + '/miniatura/miniatura_tiktok_3x4.png', clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await b.close();
})();

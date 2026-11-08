// Miniatura 9:16 (+ recorte 3:4 TikTok): la pista de noche con los focos, el reloj del tie-break enorme y el titular.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => {
    window.__timelines.main.seek(84.0);
    for (const s of ['#subs', '#grano', '#hud', '#relojes', '.chip', '#hook', '#cKcal']) document.querySelectorAll(s).forEach(e => e.style.display = 'none');
    document.querySelector('#topsombra').style.height = '360px';
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90;font-family:Inter;text-align:center';
    d.innerHTML = `
      <div style="position:absolute;left:0;right:0;top:300px">
        <div style="font:800 34px Inter;letter-spacing:10px;color:#ffc24a">¿QUÉ PASARÍA SI…?</div>
        <div style="margin-top:18px;font:900 74px/1.05 Inter;letter-spacing:-2px;color:#fff;text-shadow:0 8px 30px rgba(0,0,0,0.6)">UN TIE-BREAK<br>NO TERMINA NUNCA</div></div>
      <div style="position:absolute;left:0;right:0;top:1040px">
        <div style="display:inline-block;padding:18px 40px;border-radius:24px;background:rgba(4,10,20,0.82);border:2px solid rgba(255,255,255,0.25)">
          <div style="font:800 24px Inter;letter-spacing:6px;color:#b9c9da">TIEMPO DE PARTIDO</div>
          <div style="font:900 150px/1 Inter;letter-spacing:-4px;color:#fff;font-variant-numeric:tabular-nums">20:00:00</div></div>
        <div style="margin-top:24px;display:inline-block;padding:12px 26px;border-left:8px solid #ff5a4f;background:rgba(5,10,20,0.8);font:800 38px Inter;letter-spacing:3px;color:#ff8a80">¿QUÉ LE PASA AL CUERPO?</div></div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(800);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await p.screenshot({ path: dir + '/miniatura/miniatura_tiktok_3x4.png', clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await b.close();
})();

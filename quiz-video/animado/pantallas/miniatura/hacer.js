// Miniatura 9:16 (+ 3:4): primer plano con la cara azul de la pantalla, ojos rojos y titular.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => {
    window.__timelines.main.seek(0.05);
    for (const s of ['#subs', '#grano', '#fxl', '#hud']) document.querySelectorAll(s).forEach(e => e.style.display = 'none');
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90;font-family:Inter;text-align:center';
    d.innerHTML = `
      <div style="position:absolute;left:0;right:0;top:270px">
        <div style="font:800 34px Inter;letter-spacing:8px;color:#4fd1ff">¿QUÉ LE PASA A TU CUERPO?</div>
        <div style="margin-top:14px;font:900 150px/0.95 Inter;letter-spacing:-6px;color:#fff;text-shadow:0 10px 40px rgba(0,0,0,0.6)">100 HORAS</div>
        <div style="margin-top:12px;font:800 46px Inter;letter-spacing:4px;color:#d9e6f5">SIN SOLTAR LA PANTALLA</div></div>
      <div style="position:absolute;left:0;right:0;top:1460px"><span style="display:inline-block;padding:14px 30px;border-radius:20px;background:rgba(12,10,24,0.85);box-shadow:inset 6px 0 0 #ff5a4f;font:800 46px Inter;color:#fff">Solo 6 h de sueño</span></div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(800);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await p.screenshot({ path: dir + '/miniatura/miniatura_tiktok_3x4.png', clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await b.close();
})();

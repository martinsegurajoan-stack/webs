// Miniatura 9:16 (+ recorte 3:4 TikTok), estilo documental sobrio: helicóptero con la burbuja colgando y titular limpio.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(1500);
  await p.evaluate(() => {
    window.__timelines.main.seek(0.6);
    for (const s of ['#subs', '#marca', '#grano', '#tit1', '#topsombra']) document.querySelectorAll(s).forEach(e => e.style.display = 'none');
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90;font-family:Inter;text-align:center';
    d.innerHTML = `
      <div style="position:absolute;left:0;right:0;top:300px">
        <div style="font:800 34px Inter;letter-spacing:10px;color:#4fd1ff">¿QUÉ PASARÍA SI…?</div></div>
      <div style="position:absolute;left:0;right:0;top:1250px">
        <div style="font:900 150px Inter;letter-spacing:-6px;line-height:1;color:#fff;text-shadow:0 8px 30px rgba(0,0,0,0.5)">1.000 m</div>
        <div style="margin-top:22px;font:800 54px Inter;letter-spacing:-1px;color:#fff">DENTRO DE UNA BURBUJA</div>
        <div style="margin-top:22px;display:inline-block;padding:12px 26px;border-left:8px solid #ff5a4f;background:rgba(5,10,20,0.75);font:800 40px Inter;letter-spacing:3px;color:#ff8a80">¿QUÉ LE PASA A TU CUERPO?</div></div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(600);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await p.screenshot({ path: dir + '/miniatura/miniatura_tiktok_3x4.png', clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await b.close();
})();

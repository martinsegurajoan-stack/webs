// Miniatura 9:16 (+ recorte 3:4 TikTok): el helicóptero acaba de cortar la cuerda y la burbuja cae. Título enorme.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(1500);
  await p.evaluate(() => {
    window.__timelines.main.seek(7.0);
    gsap.set('#follow', { y: 960 - 2530 }); gsap.set('#zoom', { scale: 0.95 });
    for (const s of ['#subs', '#marca', '#grano', '#negroF', '#topsombra', '#altim', '#gancho', '.nota']) document.querySelectorAll(s).forEach(e => e.style.display = 'none');
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90;font-family:Inter;text-align:center';
    d.innerHTML = `
      <div style="position:absolute;left:0;right:0;top:520px">
        <div style="display:inline-block;padding:10px 34px 18px;background:#ffcf3a;border:8px solid #fff;border-radius:26px;transform:rotate(-3deg);box-shadow:0 18px 40px rgba(0,0,0,0.4)">
          <div style="font:900 104px Inter;letter-spacing:-3px;line-height:1;color:#1a1d22">1.000 METROS</div></div>
        <div style="margin-top:26px;font:900 76px Inter;color:#fff;text-shadow:0 6px 0 #0f3c8f, 0 0 30px rgba(0,0,0,0.4)">¿SOBREVIVES?</div></div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(600);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await p.screenshot({ path: dir + '/miniatura/miniatura_tiktok_3x4.png', clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await b.close();
})();

// Miniatura 9:16 + recorte 3:4 (TikTok): la portada de GTA 6 con la cruz y el gancho.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(1500);
  await p.evaluate(() => {
    window.__timelines.main.seek(4.9);
    for (const s of ['#subs', '#marca', '#grano', '#negroF', '#topsombra', '.nivel']) document.querySelectorAll(s).forEach(e => e.style.display = 'none');
    document.querySelector('#noh1').style.display = 'none';
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90;font-family:Inter;text-align:center';
    d.innerHTML = `
      <div style="position:absolute;left:0;right:0;top:250px">
        <div style="font:900 70px Inter;letter-spacing:4px;color:#ffcf3a;text-shadow:0 5px 0 #000">EL DÍA 1 DE GTA 6</div></div>
      <div style="position:absolute;left:0;right:0;top:1500px">
        <div style="display:inline-block;padding:8px 40px 18px;background:#ff1f3d;border:8px solid #fff;border-radius:26px;transform:rotate(-3deg);box-shadow:0 0 50px rgba(255,31,61,0.8)">
          <div style="font:900 120px Inter;letter-spacing:-4px;line-height:1;color:#fff">NO HAGAS ESTO</div></div></div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(600);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await p.screenshot({ path: dir + '/miniatura/miniatura_tiktok_3x4.png', clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await b.close();
})();

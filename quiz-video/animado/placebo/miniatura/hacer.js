// Miniatura 9:16 (+ recorte 3:4 TikTok): el protagonista bailando con el vaso, «0,00» y el titular.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => {
    window.__timelines.main.seek(0.6);
    for (const s of ['#subs', '#grano', '.chip', '#hook']) document.querySelectorAll(s).forEach(e => e.style.display = 'none');
    document.querySelector('#topsombra').style.height = '640px';
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90;font-family:Inter;text-align:center';
    d.innerHTML = `
      <div style="position:absolute;left:0;right:0;top:300px">
        <div style="font:800 34px Inter;letter-spacing:10px;color:#ffc24a">EFECTO PLACEBO</div>
        <div style="margin-top:18px;font:900 80px/1.05 Inter;letter-spacing:-2px;color:#fff;text-shadow:0 8px 30px rgba(0,0,0,0.6)">«VOY BORRACHO»</div></div>
      <div style="position:absolute;left:0;right:0;top:820px">
        <div style="display:inline-block;padding:14px 40px;border-radius:24px;background:rgba(10,6,22,0.85);border:3px solid #35d987">
          <div style="font:900 150px/1 Inter;letter-spacing:-4px;color:#35d987">0,00</div>
          <div style="margin-top:22px;font:800 26px Inter;letter-spacing:6px;color:#d9f7e8">GRAMOS DE ALCOHOL</div></div></div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(800);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await p.screenshot({ path: dir + '/miniatura/miniatura_tiktok_3x4.png', clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await b.close();
})();

// Miniatura 9:16 (+ 3:4): la cara calva, cayendo el último pelo + titular.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => {
    window.__timelines.main.seek(1); Object.assign(S, { pelo: 0, caida: 0, brillo: 1, z: 1.75, cy: -380 }); frame();
    for (const s of ['#subs', '#grano', '#fxl', '#topsombra']) document.querySelectorAll(s).forEach(e => e.style.display = 'none');
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90;font-family:Inter;text-align:center';
    const sh = 'text-shadow:0 6px 30px rgba(0,0,0,0.9)';
    d.innerHTML = `
      <div style="position:absolute;left:0;right:0;top:220px">
        <div style="font:600 54px Inter;color:#fff;${sh}">¿Y si mañana despertaras</div>
        <div style="margin-top:4px;font:800 200px/0.95 Inter;letter-spacing:-6px;color:#fff;${sh}">SIN PELO?</div>
        <div style="margin-top:18px;font:600 30px Inter;letter-spacing:6px;color:#9fdcff;${sh}">NI TÚ NI NADIE · NUNCA MÁS</div></div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(500);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await p.screenshot({ path: dir + '/miniatura/miniatura_tiktok_3x4.png', clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await b.close();
})();

// Miniatura 9:16 tipo póster: mapa 3D del Estrecho con las lanchas y la regla de 14 km, título grande y sello.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(1500);
  await p.evaluate(() => {
    const tl = window.__timelines.main; tl.seek(4.2);
    for (const s of ['#subs', '#crono', '#grano']) document.querySelector(s).style.display = 'none';
    const st = document.createElement('div');
    st.innerHTML = '<b style="color:#e0483c">14 km</b> DE MAR';
    st.style.cssText = 'white-space:nowrap;position:absolute;left:560px;top:330px;padding:14px 30px;background:#fff;border:7px solid #16203a;border-radius:24px;font:900 56px Inter;color:#16203a;transform:rotate(6deg);box-shadow:0 12px 0 #16203a;z-index:80';
    document.querySelector('#root').appendChild(st);
  });
  await p.waitForTimeout(500);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await b.close();
})();

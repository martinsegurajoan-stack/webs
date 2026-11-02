// Miniatura 9:16: el gancho del vídeo (mapa del Estrecho, lanchas, 14 km y título) sin subtítulos ni cronómetro,
// con una pegatina «60 s · DATOS REALES». Todo lo importante entre 300 y 1620 px.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(1200);
  await p.evaluate(() => {
    const tl = window.__timelines.main; tl.seek(3.4);
    for (const s of ['#subs', '#crono', '#lan3', '#lan4']) document.querySelector(s).style.display = 'none';
    const t = document.querySelector('#titulo'); t.style.top = '1060px';
    const st = document.createElement('div');
    st.innerHTML = '<b style="font:900 64px Inter;color:#d0453a">60 s</b> · DATOS REALES';
    st.style.cssText = 'white-space:nowrap;position:absolute;left:520px;top:350px;padding:16px 28px;background:#fff;border:6px solid #1d2433;border-radius:22px;font:900 40px Inter;color:#1d2433;transform:rotate(5deg);box-shadow:0 12px 0 #1d2433;z-index:60';
    document.querySelector('#root').appendChild(st);
  });
  await p.waitForTimeout(500);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await b.close();
})();

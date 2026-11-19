// Miniatura 9:16 seria (estilo documental): ciudad de noche bajo el granizo sacada del vídeo, una piedra de granizo
// enorme y realista en primer plano, título limpio y contador «DÍA 30/30». Todo lo importante entre 300 y 1620 px.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(1500);
  await p.evaluate(() => {
    const tl = window.__timelines.main; tl.seek(3.6);
    for (const s of ['#subs', '#titulo', '#marca', '#grano', '#pg', '#hud']) { const e = document.querySelector(s); if (e) e.style.display = 'none'; }
    const div = document.createElement('div');
    div.style.cssText = 'position:absolute;inset:0;z-index:80';
    div.innerHTML = `
      <div style="position:absolute;inset:0;background:linear-gradient(rgba(4,8,16,0.85), rgba(4,8,16,0.1) 40%, rgba(4,8,16,0.1) 70%, rgba(4,8,16,0.8))"></div>
      <svg style="position:absolute;left:330px;top:640px;overflow:visible" width="620" height="620" viewBox="-310 -310 620 620">
        <defs><radialGradient id="hm" cx="0.38" cy="0.35" r="0.7"><stop offset="0" stop-color="#ffffff"/><stop offset="0.45" stop-color="#e3f3ff"/><stop offset="0.85" stop-color="#9cc3dd"/><stop offset="1" stop-color="#6f97b4"/></radialGradient>
        <linearGradient id="em" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="0.8"/></linearGradient></defs>
        <path d="M-60,-1100 L0,0" stroke="url(#em)" stroke-width="300" stroke-linecap="round" opacity="0.3"/>
        <circle r="260" fill="url(#hm)"/><circle r="200" fill="none" stroke="#fff" stroke-width="5" opacity="0.22"/><circle r="140" fill="none" stroke="#fff" stroke-width="5" opacity="0.18"/><circle r="80" fill="none" stroke="#fff" stroke-width="5" opacity="0.15"/>
        <ellipse cx="-90" cy="-100" rx="70" ry="50" fill="#fff" opacity="0.9"/></svg>
      <div style="position:absolute;left:60px;top:330px;font:800 66px Inter;color:#c9d8ea;letter-spacing:2px">¿Y SI GRANIZARA</div>
      <div style="position:absolute;left:56px;top:410px;font:900 150px Inter;color:#fff;letter-spacing:-6px;line-height:0.95"><span style="color:#9fdcff">30</span> DÍAS<br>SEGUIDOS?</div>
      <div style="position:absolute;left:60px;top:1390px;width:270px;padding:12px 18px 16px;border-left:6px solid #9fdcff;background:rgba(7,12,22,0.8);color:#e9f1fb">
        <div style="font:800 24px Inter;letter-spacing:6px;color:#8796ad">DÍA</div><span style="font:900 84px Inter;letter-spacing:-2px">30</span><span style="font:800 36px Inter;color:#8796ad;margin-left:8px">/ 30</span>
        <div style="margin-top:10px;height:7px;background:#9fdcff"></div></div>
      <div style="position:absolute;left:0;right:0;top:1640px;text-align:center;font:700 30px Inter;color:#fff;opacity:0.6">@mundo.supuesto</div>`;
    document.querySelector('#root').appendChild(div);
  });
  await p.waitForTimeout(600);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await b.close();
})();

// Miniatura 9:16 tipo PÓSTER (MEJORA_CONTINUA): fondo = mapa 3D del Estrecho sacado del vídeo, apagado y con viñeta;
// encima, título gigante con relieve, medallón VS con banderas, siluetas grandes (tanque marroquí / buque español),
// pegatina «14 km de mar», franja de datos y destellos. Todo lo importante entre 300 y 1620 px.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(1500);
  await p.evaluate(() => {
    const tl = window.__timelines.main; tl.seek(4.6);
    for (const s of ['#subs', '#crono', '#grano', '#titulo', '#marca', '#regla', '#preg']) { const e = document.querySelector(s); if (e) e.style.display = 'none'; }
    document.querySelector('#escena').style.filter = 'saturate(0.75) brightness(0.8)';
    const ico = (id, col, s, extra = '') => `<svg width="${s}" height="${s}" viewBox="0 0 100 100" style="color:${col};overflow:visible;${extra}"><use href="#i-${id}" fill="currentColor"/></svg>`;
    const es = '<svg width="120" height="80" viewBox="0 0 120 80"><rect width="120" height="80" rx="8" fill="#c60b1e"/><rect y="20" width="120" height="40" fill="#ffc400"/></svg>';
    const ma = '<svg width="120" height="80" viewBox="0 0 120 80"><rect width="120" height="80" rx="8" fill="#c1272d"/><path d="M60,16 L70.6,48.5 L42.9,28.4 L77.1,28.4 L49.4,48.5 Z" fill="none" stroke="#006233" stroke-width="4.8" stroke-linejoin="round"/></svg>';
    const div = document.createElement('div');
    div.innerHTML = `
      <div style="position:absolute;inset:0;background:radial-gradient(90% 60% at 50% 45%, rgba(0,0,0,0) 40%, rgba(20,10,0,0.55)), linear-gradient(rgba(16,32,58,0.55), rgba(16,32,58,0) 30%, rgba(16,32,58,0) 65%, rgba(16,32,58,0.75));"></div>
      <div style="position:absolute;inset:-100px;mix-blend-mode:screen;background:radial-gradient(30% 22% at 12% 30%, rgba(255,150,60,0.55), rgba(255,150,60,0) 70%), radial-gradient(28% 20% at 92% 72%, rgba(255,70,90,0.45), rgba(255,70,90,0) 70%)"></div>
      <div style="position:absolute;left:0;right:0;top:300px;text-align:center">
        <div style="display:inline-block;font:900 92px Inter;color:#fff;letter-spacing:-2px;text-shadow:0 6px 0 #16203a, 0 12px 0 #0c1426, 0 20px 40px rgba(0,0,0,0.5)">¿Y SI MARRUECOS</div><br>
        <div style="display:inline-block;margin-top:10px;padding:6px 34px 14px;background:#e0483c;border-radius:26px;transform:rotate(-3deg);box-shadow:0 14px 0 #a8261d, 0 26px 50px rgba(0,0,0,0.45);font:900 120px Inter;color:#fff;letter-spacing:-4px;line-height:1">INVADIERA</div><br>
        <div style="display:inline-block;margin-top:18px;font:900 132px Inter;color:#f2b630;letter-spacing:-4px;line-height:1;text-shadow:0 7px 0 #a8650a, 0 14px 0 #6e4206, 0 24px 50px rgba(0,0,0,0.55)">ESPAÑA?</div>
      </div>
      <div style="position:absolute;left:390px;top:880px;width:300px;height:300px;border-radius:50%;background:#fff;box-shadow:0 0 0 14px rgba(255,255,255,0.35), 0 24px 60px rgba(0,0,0,0.45);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px">
        <div style="display:flex;gap:14px">${ma}${es}</div><div style="font:900 96px Inter;color:#16203a;line-height:1">VS</div></div>
      <div style="position:absolute;left:-40px;top:1080px;transform:rotate(-8deg);filter:drop-shadow(0 18px 0 rgba(0,0,0,0.25))">${ico('tanque', '#e0483c', 420)}</div>
      <div style="position:absolute;left:640px;top:1110px;transform:rotate(6deg) scaleX(-1);filter:drop-shadow(0 18px 0 rgba(0,0,0,0.25))">${ico('barco', '#f2b630', 440)}</div>
      <div style="position:absolute;left:560px;top:820px;padding:12px 26px;background:#fff6a8;border-radius:6px;transform:rotate(9deg);box-shadow:0 14px 26px rgba(0,0,0,0.35);font:700 58px Caveat;color:#16203a;white-space:nowrap;z-index:3">solo 14 km de mar</div>
      <div style="position:absolute;left:60px;right:60px;top:1500px;display:flex;justify-content:space-between;align-items:center;padding:20px 34px;background:#16203a;border-radius:30px;box-shadow:0 16px 40px rgba(0,0,0,0.45)">
        <span style="font:900 40px Inter;color:#fff">SOLDADOS</span><span style="color:#f2b630;font:900 40px Inter">·</span>
        <span style="font:900 40px Inter;color:#fff">TANQUES</span><span style="color:#f2b630;font:900 40px Inter">·</span>
        <span style="font:900 40px Inter;color:#fff">AVIONES</span></div>
      <div style="position:absolute;left:0;right:0;top:1650px;text-align:center;font:800 30px Inter;color:#fff;opacity:0.75">@mundo.supuesto</div>`;
    div.style.cssText = 'position:absolute;inset:0;z-index:90';
    document.querySelector('#root').appendChild(div);
  });
  await p.waitForTimeout(600);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await b.close();
})();

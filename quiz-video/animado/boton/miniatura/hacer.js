// Portada (9:16 y recorte 3:4 para TikTok): pantalla partida del propio vídeo. Arriba gana 1.000.000 €, abajo alguien lo pierde todo.
// Todo lo importante va dentro de la franja central 3:4 (y 240–1680).
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(1500);
  await p.evaluate(() => {
    window.__timelines.main.seek(27.9); if (window.gsap) gsap.set('#e8b-cam', {y: 190}); gsap.set('#m8', {x: 70});
    for (const s of ['#subs', '#gancho', '#marca', '#grano', '#negroF', '#topsombra', '.nota']) document.querySelectorAll(s).forEach(e => e.style.display = 'none');
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90;font-family:Inter';
    const pill = (top, bg, txt, col) => `<div style="position:absolute;left:0;right:0;top:${top}px;text-align:center"><span style="display:inline-block;padding:14px 34px;border-radius:50px;background:${bg};font:900 54px Inter;color:${col};box-shadow:0 10px 30px rgba(0,0,0,0.35);border:5px solid #fff">${txt}</span></div>`;
    d.innerHTML = `
      <div style="position:absolute;left:0;right:0;top:0;height:420px;background:linear-gradient(rgba(10,6,2,0.7),rgba(10,6,2,0))"></div>
      <div style="position:absolute;left:0;right:0;bottom:0;height:420px;background:linear-gradient(rgba(10,6,2,0),rgba(10,6,2,0.7))"></div>
      ${pill(280, 'linear-gradient(#2fd27a,#14984f)', '+1.000.000 € PARA TI', '#fff')}
      ${pill(1545, 'linear-gradient(#ff5a4a,#c8150c)', 'OTRO LO PIERDE TODO', '#fff')}
      <div style="position:absolute;left:0;right:0;top:860px;text-align:center">
        <div style="display:inline-block;padding:18px 40px 26px;background:#ffd23a;border-radius:28px;border:8px solid #fff;transform:rotate(-3deg);box-shadow:0 18px 50px rgba(0,0,0,0.5)">
          <div style="font:900 118px Inter;letter-spacing:-4px;line-height:1;color:#1a1a1a">¿LO PULSARÍAS?</div></div></div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(600);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await p.screenshot({ path: dir + '/miniatura/miniatura_tiktok_3x4.png', clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await b.close();
})();

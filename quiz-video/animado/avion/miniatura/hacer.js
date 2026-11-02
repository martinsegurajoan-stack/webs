// Portada 9:16 tipo póster: el avión real del vídeo sobre el mar de nubes, título grande y aviso de motores apagados.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(2500);
  await p.evaluate(() => {
    window.__timelines.main.seek(6.9); window.render3d(6.9);
    for (const s of ['#subs', '#gancho', '#marca', '#grano', '#ecam', '#cuenta', '#hud', '#topsombra']) { const e = document.querySelector(s); if (e) e.style.display = 'none'; }
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;inset:0;z-index:90';
    d.innerHTML = `
      <div style="position:absolute;inset:0;background:linear-gradient(rgba(6,8,14,0.85), rgba(6,8,14,0.15) 38%, rgba(6,8,14,0) 60%, rgba(6,8,14,0.55))"></div>
      <div style="position:absolute;left:60px;right:60px;top:300px;color:#fff;font-family:Inter">
        <div style="font:800 60px Inter;letter-spacing:3px;color:#ffd9b8">¿Y SI UN AVIÓN PIERDE</div>
        <div style="font:900 150px Inter;letter-spacing:-6px;line-height:0.95;text-shadow:0 8px 30px rgba(0,0,0,0.5)">LOS DOS<br><span style="color:#ff5a52">MOTORES?</span></div></div>
      <div style="position:absolute;left:60px;top:1330px;width:560px;padding:18px 24px;background:rgba(9,15,28,0.9);border-left:7px solid #ff5a52;border-radius:8px;font-family:'Courier New',monospace;color:#fff">
        <div style="font:800 22px Inter;letter-spacing:5px;color:#8796ad;margin-bottom:6px">AVISO · 11.000 m</div>
        <div style="font:800 42px 'Courier New';display:flex"><span>MOTOR 1</span><span style="margin-left:auto;color:#ff5a52">APAGADO</span></div>
        <div style="font:800 42px 'Courier New';display:flex"><span>MOTOR 2</span><span style="margin-left:auto;color:#ff5a52">APAGADO</span></div></div>
      <div style="position:absolute;left:0;right:0;top:1640px;text-align:center;font:700 30px Inter;color:#fff;opacity:0.7">@mundo.supuesto</div>`;
    document.querySelector('#root').appendChild(d);
  });
  await p.waitForTimeout(800);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await b.close();
})();

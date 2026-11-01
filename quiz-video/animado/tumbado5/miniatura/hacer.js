// Miniatura 9:16 (todo dentro de la zona que TikTok/Instagram no recortan): dos momentos del propio vídeo + título.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(800);
  const foto = async (t, clipX, file) => {
    await p.evaluate((t) => { window.__timelines.main.seek(t);
      for (const s of ['#subs', '#hud', '#marca', '#sombra-subs']) { const e = document.querySelector(s); if (e) e.style.display = 'none'; } }, t);
    await p.waitForTimeout(300);
    await p.screenshot({ path: dir + '/miniatura/' + file, clip: { x: clipX, y: 420, width: 540, height: 1100 } });
  };
  await foto(9.6, 140, '_a.png');
  await foto(52.0, 400, '_b.png');
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
  *{margin:0;padding:0;box-sizing:border-box} body{width:1080px;height:1920px;overflow:hidden;font-family:Inter,sans-serif;background:#2a2550}
  #bg{position:absolute;inset:0;background:radial-gradient(110% 70% at 50% 45%, #6c5fa8 0%, #3a2f6e 60%, #1c173d 100%)}
  .ph{position:absolute;top:640px;width:500px;height:840px;border-radius:36px;overflow:hidden;border:8px solid #fbf8f2;box-shadow:0 22px 50px rgba(0,0,0,0.45)}
  .ph img{width:100%;height:100%;object-fit:cover}
  h1{position:absolute;left:50px;right:50px;top:330px;text-align:center;color:#fff;font:900 96px/1.08 Inter;letter-spacing:-0.02em;text-shadow:0 6px 24px rgba(0,0,0,0.5)}
  .sel{position:relative;display:inline-block;padding:0 12px;color:#ffd24a} .sel span{position:relative}
  .sel i{position:absolute;inset:-2px -4px -2px -4px;border:6px solid #4f7dff;border-radius:10px;background:rgba(79,125,255,0.18)}
  .sel b{position:absolute;width:24px;height:24px;border-radius:50%;background:#dfe8ff;border:6px solid #4f7dff}
  .tag{position:absolute;top:1430px;padding:12px 30px;border-radius:24px;font:900 50px Inter;color:#1d2b33;background:#fbf8f2;box-shadow:0 14px 34px rgba(0,0,0,0.35)}
  #flecha{position:absolute;left:478px;top:1010px;z-index:3}
  #marca{position:absolute;left:0;right:0;top:1590px;text-align:center;font:700 30px Inter;color:#fff;opacity:0.45}
  </style></head><body><div id="bg"></div>
  <h1>¿Y si pasas <span class="sel"><i></i><b style="left:-16px;top:-16px"></b><b style="right:-16px;bottom:-14px"></b><span>5 años</span></span><br>TUMBADO?</h1>
  <div class="ph" style="left:28px;transform:rotate(-3deg)"><img src="file://${dir}/miniatura/_a.png"></div>
  <div class="ph" style="left:552px;transform:rotate(3deg)"><img src="file://${dir}/miniatura/_b.png"></div>
  <svg id="flecha" width="124" height="90" viewBox="0 0 140 90"><path d="M10,45 C50,10 90,10 120,40" stroke="#ffd24a" stroke-width="14" fill="none" stroke-linecap="round"/><path d="M98,22 L124,44 L94,58" stroke="#ffd24a" stroke-width="14" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
  <div class="tag" style="left:150px">DÍA 1</div><div class="tag" style="left:660px;color:#e5484d">AÑO 5</div>
  <div id="marca">@mundo.supuesto</div></body></html>`;
  await p.setContent(html); await p.waitForTimeout(500);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await b.close();
})();

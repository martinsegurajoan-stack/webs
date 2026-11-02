// Miniatura 9:16: saca los personajes del propio vídeo (p0 calvo y p5 con 75 cm) y monta la portada.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(800);
  const grab = async (t, id) => p.evaluate(([t, id]) => { const tl = window.__timelines.main; tl.seek(t); const s = document.getElementById(id).cloneNode(true); s.removeAttribute('style'); return s.outerHTML; }, [t, id]);
  const p0 = await grab(1.6, 'p0'); const p5 = await grab(42.5, 'p5');
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
  *{margin:0;padding:0;box-sizing:border-box} body{width:1080px;height:1920px;overflow:hidden;font-family:Inter,sans-serif}
  #bg{position:absolute;inset:0;background:radial-gradient(110% 65% at 50% 48%, #a1a5dd 0%, #7b7fc4 48%, #3f4288 100%)}
  #rayos{position:absolute;left:-260px;top:300px;width:1600px;height:1600px;border-radius:50%;background:repeating-conic-gradient(from 0deg, rgba(255,236,225,0.06) 0deg 7deg, rgba(255,236,225,0) 7deg 20deg);-webkit-mask-image:radial-gradient(circle,#000 12%,transparent 62%)}
  #vin{position:absolute;inset:0;background:radial-gradient(120% 80% at 50% 50%, transparent 55%, rgba(18,16,48,0.45) 100%)}
  .pj{position:absolute;top:0;width:1000px;height:1800px}
  .wrap{position:absolute;width:1000px;height:1800px;transform-origin:0 0}
  .suelo{position:absolute;width:380px;height:70px;border-radius:50%;background:radial-gradient(50% 50% at 50% 50%, rgba(20,18,60,0.35), rgba(20,18,60,0))}
  h1{position:absolute;left:60px;right:60px;top:330px;text-align:center;color:#fff;font:900 104px/1.08 Inter;letter-spacing:-0.02em;text-shadow:0 6px 24px rgba(20,18,50,0.55)}
  .sel{position:relative;display:inline-block;padding:0 12px;color:#ffd24a}
  .sel span{position:relative}
  .sel i{position:absolute;inset:-2px -4px -2px -4px;border:6px solid #4f7dff;border-radius:10px;background:rgba(79,125,255,0.18)}
  .sel b{position:absolute;width:24px;height:24px;border-radius:50%;background:#dfe8ff;border:6px solid #4f7dff}
  .tag{position:absolute;padding:14px 30px;border-radius:24px;font:900 50px Inter;color:#1d2b33;background:#fbf8f2;box-shadow:0 14px 34px rgba(0,0,0,0.3)}
  #flecha{position:absolute;left:470px;top:1060px}
  #marca{position:absolute;left:0;right:0;top:1590px;text-align:center;font:700 30px Inter;color:#fff;opacity:0.4}
  </style></head><body>
  <div id="bg"></div><div id="rayos"></div>
  <div class="suelo" style="left:85px;top:1440px"></div><div class="suelo" style="left:625px;top:1440px"></div>
  <div class="wrap" style="left:-80px;top:285px;transform:scale(0.7)">${p0}</div>
  <div class="wrap" style="left:460px;top:285px;transform:scale(0.7)">${p5}</div>
  <svg id="flecha" width="140" height="90" viewBox="0 0 140 90"><path d="M10,45 C50,10 90,10 120,40" stroke="#fbf3e6" stroke-width="12" fill="none" stroke-linecap="round"/><path d="M98,22 L124,44 L94,58" stroke="#fbf3e6" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
  <div class="tag" style="left:165px;top:1500px">DÍA 1</div>
  <div class="tag" style="left:690px;top:1500px;color:#e5484d">AÑO 10</div>
  <h1>¿Y si no te cortas el pelo en <span class="sel"><i></i><b style="left:-16px;top:-16px"></b><b style="right:-16px;bottom:-14px"></b><span>10 años?</span></span></h1>
  <div id="vin"></div><div id="marca">@mundo.supuesto</div>
  </body></html>`;
  await p.setContent(html); await p.waitForTimeout(400);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  // recortes exactos: TikTok 3:4 (1080x1440) e Instagram 4:5 (1080x1350), centrados
  await p.screenshot({ path: dir + '/miniatura/miniatura_tiktok_3x4.png', clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await p.screenshot({ path: dir + '/miniatura/miniatura_instagram_4x5.png', clip: { x: 0, y: 285, width: 1080, height: 1350 } });
  await b.close();
})();

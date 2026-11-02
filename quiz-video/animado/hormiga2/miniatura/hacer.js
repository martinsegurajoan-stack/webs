// Miniatura 9:16 tipo PÓSTER DE PELÍCULA: escena montada a propósito con las piezas del vídeo
// (el gato gigante, el edificio de 50 pisos y TÚ diminuto) + título enorme. Todo lo importante entre 300 y 1620 px.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(900);
  await p.evaluate(() => {
    const tl = window.__timelines.main; tl.seek(59.9);
    for (const s of ['#subs', '#marca', '#sombra-subs', '#wipe', '#vineta']) { const e = document.querySelector(s); if (e) e.style.display = 'none'; }
    const z = 1.05, cx = 10575, cy = 1135;
    gsap.set('#world', { x: 540 - cx * z, y: 960 - cy * z, scale: z });
    gsap.set('#camA', { scale: 1, rotation: 0 }); gsap.set('#camB', { scale: 1, rotation: 0 });
    gsap.set('#edif', { x: 150, opacity: 1, scaleY: 1 });
    gsap.set('#p5-w', { x: -95, scale: 0.22 });
    gsap.set('#p5-eyes', { scaleY: 1.35, svgOrigin: '500 742' }); gsap.set('#p5-mouthO', { opacity: 1 }); gsap.set('#p5-mouth', { opacity: 0 });
    gsap.set('#p5-armLg', { rotation: 150, svgOrigin: '356 985' }); gsap.set('#p5-armRg', { rotation: -150, svgOrigin: '644 985' });
    gsap.set('#gatoG', { x: 0, y: 0 });
    gsap.set('#gato .pup', { attr: { rx: 30 } });
  });
  await p.waitForTimeout(400);
  await p.screenshot({ path: dir + '/miniatura/_fondo.png' });
  // posición en pantalla del personaje (para el círculo y la flecha)
  const r = await p.evaluate(() => { const e = document.querySelector('#p5-w').getBoundingClientRect(); return { x: e.x + e.width / 2, y: e.y + e.height * 0.62 }; });
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
  *{margin:0;padding:0;box-sizing:border-box} body{width:1080px;height:1920px;overflow:hidden;font-family:Inter,sans-serif}
  #bg{position:absolute;inset:0;background:url('file://${dir}/miniatura/_fondo.png')}
  #sombra{position:absolute;left:0;right:0;top:0;height:760px;background:linear-gradient(rgba(20,8,60,0.85),rgba(20,8,60,0.55) 60%,rgba(20,8,60,0))}
  #vig{position:absolute;inset:0;background:radial-gradient(120% 80% at 50% 55%, rgba(0,0,0,0) 60%, rgba(10,0,40,0.45) 100%)}
  h1{position:absolute;left:0;right:0;top:300px;text-align:center;color:#fff;font:900 104px/1 Inter;letter-spacing:-0.02em;
     -webkit-text-stroke:10px #1b0b45;paint-order:stroke fill;text-shadow:0 10px 0 #1b0b45}
  #mm{position:absolute;left:0;right:0;top:405px;text-align:center;font:900 250px/1 Inter;letter-spacing:-0.04em;color:#ffd23f;
     -webkit-text-stroke:16px #1b0b45;paint-order:stroke fill;text-shadow:0 16px 0 #1b0b45;transform:rotate(-4deg)}
  #sub{position:absolute;left:0;right:0;top:660px;text-align:center;font:900 64px/1 Inter;color:#fff;-webkit-text-stroke:8px #1b0b45;paint-order:stroke fill}
  #aro{position:absolute;width:300px;height:300px;border-radius:50%;border:14px solid #ff3b5c;box-shadow:0 0 0 8px #fff, 0 0 40px rgba(255,59,92,0.8)}
  #tu{position:absolute;padding:10px 30px;border-radius:26px;background:#ffd23f;color:#1b0b45;font:900 72px Inter;box-shadow:0 10px 0 #1b0b45;transform:rotate(-6deg)}
  #flecha{position:absolute;overflow:visible}
  #pegatina{position:absolute;left:600px;top:1470px;padding:18px 30px;border-radius:24px;background:#ff3b5c;color:#fff;font:900 54px/1.05 Inter;
     transform:rotate(5deg);box-shadow:0 12px 0 #1b0b45;border:6px solid #fff;text-align:center}
  #marca{position:absolute;left:0;right:0;top:1650px;text-align:center;font:800 30px Inter;color:#fff;opacity:0.7;text-shadow:0 2px 8px rgba(0,0,0,0.6)}
  </style></head><body><div id="bg"></div><div id="vig"></div><div id="sombra"></div>
  <h1>¿Y SI MIDES</h1><div id="mm">3 mm?</div><div id="sub">EN TU PROPIA CASA</div>
  <div id="aro" style="left:${r.x - 150}px;top:${r.y - 150}px"></div>
  <div id="tu" style="left:${r.x - 380}px;top:${r.y - 260}px">TÚ</div>
  <svg id="flecha" width="10" height="10" style="left:${r.x - 250}px;top:${r.y - 150}px"><path d="M0,0 C40,10 70,30 90,60" stroke="#ffd23f" stroke-width="16" fill="none" stroke-linecap="round"/><path d="M58,62 L94,66 L92,28" stroke="#ffd23f" stroke-width="16" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
  
  <div id="marca">@mundo.supuesto</div></body></html>`;
  await p.setContent(html); await p.waitForTimeout(600);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await b.close();
})();

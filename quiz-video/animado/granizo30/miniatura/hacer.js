// Miniatura 9:16 tipo PÓSTER: calle con tormenta sacada del vídeo (apagada), protagonista GRANDE a todo color con el
// paraguas agujereado, piedra de granizo gigante cayendo, título enorme y calendario «DÍA 30». Todo entre 300 y 1620 px.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(() => { window.__timelines = {}; });
  await p.goto('file://' + dir + '/index.html'); await p.waitForTimeout(1500);
  await p.evaluate(() => {
    const tl = window.__timelines.main; tl.seek(3.0);
    for (const s of ['#subs', '#titulo', '#marca', '#grano', '#piedraG']) { const e = document.querySelector(s); if (e) e.style.display = 'none'; }
    document.querySelector('#e1').style.filter = 'saturate(0.55) brightness(0.72)';
    // protagonista grande, a todo color, delante
    const pj = document.querySelector('#p1').cloneNode(true);
    pj.id = 'pjG'; pj.querySelectorAll('[id]').forEach(n => n.id = n.id + 'G');
    pj.setAttribute('width', 760); pj.setAttribute('height', 1368);
    pj.style.cssText = 'position:absolute;left:-60px;top:560px;z-index:70;overflow:visible;filter:drop-shadow(0 20px 30px rgba(0,0,0,0.45))';
    pj.querySelector('#p1-agujerosG').setAttribute('opacity', '1');
    pj.querySelector('#p1-bocaOG').setAttribute('opacity', '1'); pj.querySelector('#p1-bocaG').setAttribute('opacity', '0');
    document.querySelector('#root').appendChild(pj);
    const div = document.createElement('div');
    div.style.cssText = 'position:absolute;inset:0;z-index:80';
    div.innerHTML = `
      <div style="position:absolute;inset:0;background:linear-gradient(rgba(14,18,40,0.75), rgba(14,18,40,0) 40%, rgba(14,18,40,0) 70%, rgba(14,18,40,0.6))"></div>
      <svg style="position:absolute;left:560px;top:520px;overflow:visible" width="380" height="380" viewBox="0 0 380 380">
        <path d="M60,40 L150,190 M120,10 L210,170 M10,110 L110,230" stroke="#ffffff" stroke-width="14" opacity="0.5" stroke-linecap="round"/>
        <circle cx="230" cy="230" r="140" fill="#f4fbff" stroke="#9fd2ee" stroke-width="10"/><circle cx="185" cy="180" r="42" fill="#ffffff"/>
        <path d="M150,290 q80,40 160,-20" stroke="#cfe9f7" stroke-width="10" fill="none"/><path d="M290,160 q20,40 0,80" stroke="#cfe9f7" stroke-width="8" fill="none"/></svg>
      <div style="position:absolute;left:0;right:0;top:310px;text-align:center">
        <div style="display:inline-block;font:900 96px Inter;color:#fff;letter-spacing:-3px;text-shadow:0 6px 0 #1b2340, 0 12px 0 #0e1328, 0 20px 40px rgba(0,0,0,0.5)">¿Y SI GRANIZARA</div><br>
        <div style="display:inline-block;margin-top:14px;padding:6px 34px 14px;background:#2f7de1;border-radius:26px;transform:rotate(-3deg);box-shadow:0 14px 0 #1d4f99, 0 26px 50px rgba(0,0,0,0.45);font:900 104px Inter;color:#fff;letter-spacing:-4px;line-height:1"><span style="color:#ffd34d">30</span> DÍAS?</div>
      </div>
      <div style="position:absolute;left:790px;top:1180px;width:230px;height:230px;background:#fff;border-radius:22px;transform:rotate(6deg);box-shadow:0 18px 40px rgba(0,0,0,0.45);text-align:center;overflow:hidden">
        <div style="height:60px;background:#ef4a4a;font:900 32px Inter;color:#fff;letter-spacing:4px;line-height:60px">DÍA</div>
        <div style="font:900 120px Inter;color:#1b2340;line-height:1.1">30</div></div>
      <div style="position:absolute;left:0;right:0;top:1640px;text-align:center;font:800 30px Inter;color:#fff;opacity:0.75">@mundo.supuesto</div>`;
    document.querySelector('#root').appendChild(div);
  });
  await p.waitForTimeout(600);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await b.close();
})();

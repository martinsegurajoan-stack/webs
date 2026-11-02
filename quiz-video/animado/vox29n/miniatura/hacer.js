// Miniatura 9:16 PLANTILLA «¿Y SI GANA <PARTIDO>?» (estilo libreta, sobria). Lee partido.json (color, logo, textos).
// Todo lo importante entre 300 y 1620 px de alto (TikTok/Instagram recortan arriba y abajo).
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const dir = path.resolve(__dirname, '..');
  const cfg = JSON.parse(fs.readFileSync(dir + '/partido.json', 'utf8'));
  const C = cfg.color, C2 = cfg.color_claro, P = cfg.portada;
  const f = (n) => 'file://' + dir + '/assets/fonts/' + n;
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
  @font-face{font-family:Caveat;src:url('${f('Caveat-700-latin.woff2')}');font-weight:700}
  @font-face{font-family:Marker;src:url('${f('permanent-marker-400.woff2')}')}
  @font-face{font-family:Courier;src:url('${f('courier-prime-700.woff2')}');font-weight:700}
  *{margin:0;padding:0;box-sizing:border-box} body{width:1080px;height:1920px;overflow:hidden;background:#2a1d14}
  #mesa{position:absolute;inset:0;background:linear-gradient(#3b2a20,#24180f)}
  #hoja{position:absolute;left:90px;top:300px;width:900px;height:1300px;transform:rotate(-2deg);border-radius:10px;box-shadow:0 40px 80px rgba(0,0,0,0.55);
    background:linear-gradient(90deg, transparent 98px, rgba(214,69,65,0.5) 98px, rgba(214,69,65,0.5) 101px, transparent 101px),
    repeating-linear-gradient(180deg,#fbf8f0 0,#fbf8f0 99px,rgba(80,120,190,0.25) 99px,rgba(80,120,190,0.25) 101px);background-color:#fbf8f0}
  #esp{position:absolute;left:110px;top:262px;transform:rotate(-2deg)}
  #logo{position:absolute;left:330px;top:120px;width:260px}
  .m{position:absolute;font-family:Marker;white-space:nowrap}
  #l1{left:140px;top:300px;font-size:120px;color:#222}
  #l2{left:140px;top:450px;font-size:210px;color:${C}}
  #sub{position:absolute;left:150px;top:975px;font:700 70px Caveat;color:#1f3a7a;white-space:nowrap}
  #fecha{left:150px;top:760px;font-size:120px;color:#c0392b}
  #crono{position:absolute;right:40px;top:740px}
  #fuente{position:absolute;left:150px;top:1215px;font:700 24px Courier;color:#888}
  #marca{position:absolute;left:0;right:0;top:1640px;text-align:center;font:800 30px Inter;color:#fff;opacity:0.6}
  </style></head><body><div id="mesa"></div>
  <div id="hoja">
    <img id="logo" src="file://${dir}/${cfg.logo}">
    <div class="m" id="l1">${P.linea1}</div><div class="m" id="l2">${P.linea2}</div>
    <svg width="900" height="1300" style="position:absolute;left:0;top:0">
      <path d="M140,700 C300,690 520,705 720,694" stroke="${C}" stroke-width="12" fill="none" stroke-linecap="round"/>
      <path d="M150,840 C120,780 230,750 330,755 C430,760 470,800 455,850 C440,900 330,915 240,905 C160,898 130,870 150,840" stroke="#c0392b" stroke-width="7" fill="none"/>
    </svg>
    <div class="m" id="fecha">${P.fecha}</div>
    <div id="sub">${P.sub}</div>
    <svg id="crono" width="200" height="200" viewBox="0 0 170 170"><rect x="72" y="2" width="26" height="18" rx="4" fill="#2b2b2b"/><circle cx="85" cy="92" r="72" fill="#fbf8f0" stroke="#2b2b2b" stroke-width="7"/>
      <circle cx="85" cy="92" r="58" fill="none" stroke="${C}" stroke-width="12" stroke-dasharray="270 400" transform="rotate(-90 85 92)"/><text x="85" y="110" text-anchor="middle" font-family="Marker" font-size="46" fill="#2b2b2b">60s</text></svg>
    <div id="fuente">Datos: encuestas y propuestas públicas · 29-N 2026</div>
  </div>
  <svg id="esp" width="900" height="70">${Array.from({length: 19}, (_, i) => `<rect x="${30 + i * 45}" y="6" width="14" height="58" rx="7" fill="#9aa0a8" stroke="#5d636b" stroke-width="3"/>`).join('')}</svg>
  <div id="marca">@mundo.supuesto</div></body></html>`;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  fs.writeFileSync(dir + '/miniatura/_mini.html', html); await p.goto('file://' + dir + '/miniatura/_mini.html'); await p.waitForTimeout(1200);
  await p.screenshot({ path: dir + '/miniatura/miniatura_9x16.png' });
  await b.close();
})();

#!/usr/bin/env python3
"""«Cómo se construye un puente colgante sobre el mar» — maqueta 3D (three.js, escena2.js) controlada por GSAP:
cámara de cine, construcción pieza a pieza, resaltados y etiquetas limpias. Fondo neutro.
  python3 gen.py → index.html + efectos.json + ambiente.json"""
import json, os, random, re, unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(BASE, "tiempos.json"), encoding="utf-8"))
DUR = T["duracion"]
def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9ñ]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))
WORDS = [(norm(p["w"]), p["ini"], p["fin"]) for p in T["palabras"]]
FR = T["frases"]
def P(word, n=1):
    k = 0
    for w, a, b in WORDS:
        if w == norm(word):
            k += 1
            if k == n:
                return a
    raise KeyError(f"{word} {n}")
def F(n): return FR[n - 1]["ini"]
def FE(n): return FR[n - 1]["fin"]
tl, FX, FXL = [], [], []
def J(s): tl.append(s)
def fx(k, t): FX.append([k, round(t, 3)])

# ------------------------------------------------------------------ cámara (proxy C) y estado de obra (E.st)
TX, TH, DECK, PROF, ANCLA = 500, 240, 78, 120, 840
HERO = ((-1250, 520, 1250), (80, 40, -40))
def cam(t, pos, tgt, d=1.6, ease="power2.inOut"):
    J(f'tl.to(C, {{px:{pos[0]}, py:{pos[1]}, pz:{pos[2]}, tx:{tgt[0]}, ty:{tgt[1]}, tz:{tgt[2]}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
    if d <= 1.0: fx("whoosh", t)
def st(t, d=0.8, ease="power2.inOut", **kv):
    props = ", ".join(f"{k}:{v}" for k, v in kv.items())
    J(f'tl.to(E.st, {{{props}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
def hl(nombre, t, hasta, d=0.4):
    J(f'tl.to(HL, {{{nombre}:1, duration:{d}}}, {t:.2f}); tl.to(HL, {{{nombre}:0, duration:0.5}}, {hasta:.2f});')
NL = [0]
def etiqueta(p3, lx, ly, kicker, titulo, sub, t, hasta):
    NL[0] += 1; i = NL[0]
    FXL.append(f'<div class="lab" id="lab{i}" style="left:{lx}px;top:{ly}px"><small>{kicker}</small><b>{titulo}</b>{f"<em>{sub}</em>" if sub else ""}</div>')
    J(f'LABS.push({{i:{i}, p:[{p3[0]},{p3[1]},{p3[2]}], lx:{lx}, ly:{ly}}});')
    J(f'tl.set("#lab{i}", {{opacity:0}}, 0); tl.fromTo(LV, {{l{i}:0}}, {{l{i}:1, duration:0.45, ease:"power2.out", immediateRender:false}}, {t:.2f}); tl.to(LV, {{l{i}:0, duration:0.3}}, {hasta:.2f});')
    J(f'LV.l{i} = 0;')
    fx("pop", t)
def dato(html, t, hasta, top=1420):
    NL[0] += 1; i = NL[0]
    FXL.append(f'<div class="dato" id="d{i}" style="top:{top}px">{html}</div>')
    J(f'tl.set("#d{i}", {{opacity:0}}, 0); tl.fromTo("#d{i}", {{opacity:0, y:30, letterSpacing:"8px"}}, {{opacity:1, y:0, letterSpacing:"0px", duration:0.6, ease:"power3.out", immediateRender:false}}, {t:.2f}); tl.to("#d{i}", {{opacity:0, y:-20, duration:0.3}}, {hasta:.2f});')
    fx("golpe", t)

# ------------------------------------------------------------------ GUION VISUAL
J(f'tl.to(E.st, {{t:{DUR:.2f}, duration:{DUR:.2f}, ease:"none"}}, 0);')
J(f'tl.to(E.st, {{fzT:{DUR * 0.6:.2f}, duration:{DUR:.2f}, ease:"none"}}, 0);')
# 1) gancho: el puente terminado, vuelo de cámara
cam(0.0, (-1050, 430, 1050), (60, 50, -30), FE(1), "sine.inOut")
dato('<b>1.000 m</b><small>NI UNA COLUMNA EN EL AGUA</small>', 0.0, P("coches") - 0.2)
J('tl.set("#d1", {opacity:1, y:0, letterSpacing:"0px"}, 0);')
dato('<b>¿Cómo se aguanta?</b>', P("aguanta") - 0.6, FE(1) + 0.2, top=1440)
# 2) por qué no hay columnas: profundidad, corrientes, barcos
cam(F(2) - 0.2, (-260, 40, 640), (120, 50, 0), 1.0)
st(F(2) + 0.6, FE(2) - F(2) + 0.6, "none", barcoZ=-620)
etiqueta((0, -PROF + 10, 160), 70, 1180, "PROFUNDIDAD", "Mar profundo", "", P("profundo") - 0.2, P("corrientes") - 0.1)
etiqueta((-200, 2, 200), 70, 1180, "CORRIENTES", "Fuertes", "", P("corrientes") - 0.1, P("barcos") - 0.3)
etiqueta((0, 40, 300), 560, 1240, "GÁLIBO", "Barcos enormes", "pasan por debajo", P("barcos") - 0.3, FE(2) + 0.2)
# 3) un pilar en medio sería un estorbo; lo cuelgan
cam(F(3) - 0.1, (-900, 260, 900), (0, 20, 0), 1.0)
st(P("pilar") - 0.1, 0.5, fan=0.55); st(P("estorbo") + 0.2, 0.4, fan=0)
FXL.append('<div class="tacha" id="tacha">✕</div>')
J(f'tl.set("#tacha", {{opacity:0}}, 0); tl.fromTo("#tacha", {{opacity:0, scale:2}}, {{opacity:1, scale:1, duration:0.3, ease:"back.out(2)", immediateRender:false}}, {P("estorbo") - 0.3:.2f}); tl.to("#tacha", {{opacity:0, duration:0.3}}, {P("estorbo") + 0.5:.2f});')
fx("denegada", P("estorbo") - 0.3)
cam(P("cuelgan") - 0.6, (-520, 300, 620), (0, 140, 0), 0.9)
hl("cab", P("cuelgan") - 0.3, FE(3) + 0.3)
dato('<b>Lo cuelgan</b>', P("cuelgan") - 0.2, FE(3) + 0.3, top=1440)
# 4) rebobinado a la obra: cajones de hormigón bajo el agua
fx("rebobina", F(4) - 0.3)
st(F(4) - 0.3, 0.7, "power2.in", tor=0, hilo=0, pen=0, dov=0, anc=0, asf=0, luz=0, coches=0, cim=0)
J(f'tl.set(E.st, {{barcoZ:620}}, {F(4) + 0.5:.2f});')
cam(F(4) - 0.2, (-180, -50, 560), (-TX, -70, 0), 1.2)
st(F(4) + 0.4, 0.6, agua=0.2)
st(P("hunde") - 0.1, P("firme") - P("hunde") + 0.4, "power1.inOut", cim=1)
fx("golpe", P("firme"))
hl("cim", P("cajon") - 0.1, FE(4) + 0.4)
etiqueta((-TX + 46, -PROF - 30, 30), 560, 1240, "CIMENTACIÓN", "Cajón de hormigón", "hundido hasta la roca", P("cajon") - 0.1, FE(4) + 0.3)
# 5) torres de más de 200 m; arriba, arcos huecos
st(F(5) - 0.1, 0.5, agua=0.62)
cam(F(5) - 0.2, (-960, 150, 560), (-TX, 130, 0), 1.2)
st(P("levantan") - 0.2, 2.6, "power2.out", tor=1)
dato('<b>+200 m</b><small>DE ALTURA</small>', P("doscientos") - 0.3, P("fijate") - 0.2, top=1440)
cam(P("fijate") - 0.4, (-330, 330, 260), (-TX, 190, 0), 1.1)
hl("arc", P("arriba") - 0.1, FE(5) + 0.3)
etiqueta((-TX, 200, 22), 600, 1250, "LA TORRE", "Arcos huecos", "menos peso, menos viento", P("arcos") - 0.3, FE(5) + 0.3)
# 6) el cable piloto cruza con un dron
cam(F(6) - 0.2, (0, 420, 1500), (0, 150, 0), 1.2)
st(P("cruzar") - 0.2, FE(6) - P("cruzar") + 0.2, "power1.inOut", pil=1)
etiqueta((0, 240, -22), 560, 1250, "CABLE PILOTO", "Un primer hilo", "de orilla a orilla", P("cable") - 0.1, FE(6) + 0.2)
# 7) pasarela e hilado: la rueda va y viene
st(P("pasarela") - 0.2, 0.8, pas=1)
cam(P("pasarela") - 0.3, (-160, 260, 300), (-160, 150, -22), 1.2)
st(P("hilado") - 0.2, FE(8) - P("hilado"), "none", rueda=3)
st(P("hilado") - 0.2, FE(7) - P("hilado") + 1, "power1.in", hilo=0.35)
etiqueta((-160, 160, -22), 600, 1250, "HILADO", "Alambres de 5 mm", "una rueda los lleva de lado a lado", P("rueda") - 0.2, FE(7) + 0.2)
# 8) decenas de miles de alambres → cable de más de un metro
cam(F(8) - 0.1, (40, 120, 110), (0, 92, -22), 1.2)
FXL.append('<div id="seccion" class="seccion"><svg viewBox="0 0 400 400" width="420" height="420"><circle cx="200" cy="200" r="190" fill="#1b1f27" stroke="#e6ebf2" stroke-width="6"/>'
           + "".join(f'<circle class="al" cx="{200 + r * __import__("math").cos(a):.1f}" cy="{200 + r * __import__("math").sin(a):.1f}" r="5" fill="#e6ebf2"/>'
                     for r, n in ((0, 1), (14, 6), (28, 12), (42, 18), (56, 24), (70, 30), (84, 36), (98, 42), (112, 48), (126, 54), (140, 60), (154, 66), (168, 72))
                     for a in [k * 2 * 3.14159 / n for k in range(n)])
           + '</svg><b id="alN">1</b><small>ALAMBRES</small></div>')
J('tl.set("#seccion", {opacity:0}, 0); tl.set(".al", {opacity:0}, 0);')
J(f'tl.fromTo("#seccion", {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.5, ease:"back.out(1.6)", immediateRender:false}}, {F(8):.2f}); tl.to(".al", {{opacity:1, duration:0.02, stagger:{2.4 / 469:.4f}}}, {F(8) + 0.2:.2f}); tl.to("#seccion", {{opacity:0, duration:0.3}}, {FE(8) + 0.2:.2f});')
J(f'const alv = {{v:1}}; tl.to(alv, {{v:36830, duration:2.6, ease:"power2.in", onUpdate:() => {{ document.getElementById("alN").textContent = String(Math.round(alv.v)).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, "."); }}}}, {F(8) + 0.2:.2f});')
fx("cuenta", F(8) + 0.2)
st(P("apretados") - 0.2, 1.2, hilo=1, pas=0)
dato('<b>&gt; 1 m</b><small>DE GROSOR</small>', P("grosor") - 0.6, FE(8) + 0.3, top=1460)
# 9) anclajes
cam(F(9) - 0.2, (-1180, 160, 420), (-ANCLA, 30, 0), 1.2)
st(F(9) + 0.3, 1.4, "power2.out", anc=1)
hl("anc", P("anclajes") - 0.2, FE(9) + 0.3)
etiqueta((-ANCLA, 50, 40), 560, 1250, "ANCLAJE", "Hormigón macizo", "sujeta el cable en tierra", P("anclajes") - 0.2, FE(9) + 0.3)
# 10) péndolas
cam(F(10) - 0.2, (0, 170, 560), (0, 130, 0), 1.0)
st(P("pendolas") - 0.4, FE(10) - P("pendolas") + 0.6, "power1.inOut", pen=1)
hl("pen", P("pendolas"), FE(10) + 0.3)
etiqueta((60, 120, 22), 600, 1270, "PÉNDOLAS", "Cables verticales", "cada pocos metros", P("pendolas") - 0.1, FE(10) + 0.3)
# 11-12) el tablero: barcazas, grúa, del centro hacia las torres
cam(F(11) - 0.2, (-120, 70, 330), (0, 50, 0), 1.0)
st(P("barcazas") - 0.3, FE(12) - P("barcazas") + 0.2, "none", dov=1)
etiqueta((0, 10, 30), 560, 1270, "BARCAZA", "Tramos ya fabricados", "una grúa los sube y engancha", P("barcazas") - 0.2, FE(11) + 0.2)
cam(F(12) - 0.2, (0, 1250, 980), (0, 40, 0), 1.4)
FXL.append('<div id="flechas" class="flechas"><span>⟵</span><span>CENTRO</span><span>⟶</span></div>')
J(f'tl.set("#flechas", {{opacity:0}}, 0); tl.to("#flechas", {{opacity:1, duration:0.3}}, {P("centro") - 0.2:.2f}); tl.to("#flechas", {{opacity:0, duration:0.3}}, {FE(12) + 0.2:.2f});')
# 13) el truco: el recorrido del peso
cam(F(13) - 0.2, (-760, 470, 1300), (0, 90, 0), 1.2)
st(F(13) + 0.1, 0.6, fza=1)
hl("pen", P("pendolas", 2) - 0.2, P("cable", 4) + 0.4); hl("cab", P("cable", 4) - 0.2, P("torres", 3) - 0.1)
hl("arc", P("torres", 3) - 0.2, FE(13) + 0.6); hl("anc", P("anclajes", 2) - 0.2, FE(13) + 0.6)
etiqueta((-TX, TH, 22), 600, 1250, "EL PESO VIAJA", "Péndolas → cable", "→ torres y anclajes", F(13) + 0.6, FE(13) + 0.3)
# 14) ni un kilo al mar
cam(F(14) - 0.2, (0, -60, 760), (0, -50, 0), 1.0)
st(F(14) - 0.2, 0.5, agua=0.22)
dato('<b>0 kg</b><small>SOBRE EL MAR</small>', P("kilo") - 0.2, FE(14) + 0.3, top=1440)
st(FE(14) + 0.2, 0.5, agua=0.62, fza=0)
# 15) último tramo, asfalto, luces
cam(F(15) - 0.2, (-620, 170, 540), (-260, 90, 0), 1.1)
st(F(15) + 0.1, 0.6, asf=1)
st(P("luces") - 0.2, 0.8, luz=1, coches=1)
fx("ding", P("luces"))
# 16) viento: el tablero se mueve
cam(F(16) - 0.2, (320, 130, 430), (0, 85, 0), 1.0)
st(F(16), 0.8, vien=1); st(FE(16) - 0.4, 0.8, vien=0)
FXL.append('<div id="viento" class="viento">' + "".join(f'<i style="top:{900 + k * 70}px;animation-delay:0s"></i>' for k in range(8)) + '</div>')
J('tl.set("#viento", {opacity:0}, 0);')
J(f'tl.to("#viento", {{opacity:1, duration:0.4}}, {F(16):.2f}); tl.fromTo("#viento i", {{x:-700}}, {{x:1400, duration:1.2, stagger:0.15, repeat:3, ease:"none", immediateRender:false}}, {F(16):.2f}); tl.to("#viento", {{opacity:0, duration:0.4}}, {FE(16):.2f});')
fx("whoosh", F(16))
etiqueta((0, DECK, 22), 560, 1260, "FLEXIBLE", "Se mueve varios metros", "si fuera rígido, se rompería", P("metros", 3) - 0.6, FE(16) + 0.2)
# 17) cierre: vuelve al plano del principio
cam(F(17) - 0.2, (-1250, 520, 1250), (80, 40, -40), DUR - F(17) + 0.2, "sine.inOut")
dato('<b>Colgado de dos cables</b>', P("cables", 2) - 0.6, DUR - 1.2, top=1440)
J(f'tl.fromTo("#d1", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.6, ease:"power3.out", immediateRender:false}}, {DUR - 1.0:.2f});')

# ------------------------------------------------------------------ montaje
_S = open(os.path.join(BASE, "_subs.py"), encoding="utf-8").read()
exec(re.sub(r"CLAVE = set\(.*?\]\)", lambda m: 'CLAVE = set(norm(w) for w in ["mil", "columna", "aguanta", "profundo", "corrientes", "barcos", "pilar", "cuelgan", "hormigon", "roca", "torres", "doscientos", "arcos", "huecos", "cable", "dron", "hilado", "cinco", "miles", "metro", "anclajes", "pendolas", "tablero", "centro", "truco", "kilo", "luces", "viento", "rigido", "colgado", "cables"])', _S, count=1, flags=re.S))
html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script><script src="assets/three.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#15181d}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;background:radial-gradient(120% 80% at 50% 48%, #3c414a 0%, #252930 55%, #15181d 100%);color:#fff}}
#gl{{position:absolute;inset:0}}
#fxl{{position:absolute;inset:0;z-index:58;pointer-events:none}} svg#lineas{{position:absolute;inset:0;z-index:57;pointer-events:none}}
.lab{{position:absolute;padding:16px 22px 18px;border-radius:16px;background:rgba(18,21,27,0.78);border:1px solid rgba(255,255,255,0.12);backdrop-filter:blur(6px);opacity:0}}
.lab small{{display:block;font:700 17px Inter;letter-spacing:5px;color:#4fd1ff;margin-bottom:6px}} .lab b{{display:block;font:600 42px/1.12 Inter;letter-spacing:-0.5px}}
.lab em{{display:block;font-style:normal;font:500 24px/1.3 Inter;color:rgba(255,255,255,0.68);margin-top:6px}}
.dato{{position:absolute;left:0;right:0;text-align:center;text-shadow:0 6px 30px rgba(0,0,0,0.5)}}
.dato b{{display:block;font:300 120px/1 Inter;letter-spacing:-4px}} .dato small{{display:block;margin-top:12px;font:600 22px Inter;letter-spacing:8px;color:rgba(255,255,255,0.7)}}
.tacha{{position:absolute;left:0;right:0;top:880px;text-align:center;font:200 300px/1 Inter;color:#ff5a4f}}
.seccion{{position:absolute;left:0;right:0;top:640px;text-align:center}} .seccion b{{display:block;font:300 100px/1 Inter;letter-spacing:-3px;margin-top:10px;font-variant-numeric:tabular-nums}} .seccion small{{font:600 22px Inter;letter-spacing:8px;color:rgba(255,255,255,0.7)}}
.flechas{{position:absolute;left:0;right:0;top:1440px;display:flex;justify-content:center;gap:40px;font:300 70px Inter;color:#4fd1ff}} .flechas span:nth-child(2){{font:600 26px Inter;letter-spacing:8px;color:#fff;align-self:center}}
.viento{{position:absolute;inset:0}} .viento i{{position:absolute;left:0;width:420px;height:3px;border-radius:2px;background:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,255,255,0.7),rgba(255,255,255,0))}}
#grano{{position:absolute;inset:0;z-index:56;pointer-events:none;opacity:0.03;background:url(assets/grano.png);mix-blend-mode:overlay}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:480px;z-index:55;pointer-events:none;background:linear-gradient(rgba(14,16,20,0.85),rgba(14,16,20,0))}}
#marca{{position:absolute;left:0;right:0;top:1820px;text-align:center;font:600 26px Inter;color:#ffffff;opacity:0.28;pointer-events:none;z-index:61}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 58px Inter;color:rgba(255,255,255,0.42);line-height:1.22;text-shadow:0 3px 12px rgba(0,0,0,0.6)}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:3px solid #4ea3ff;border-radius:6px;background:rgba(78,163,255,0.18);opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="gl"></div>
  <div id="topsombra"></div><div id="grano"></div>
  <svg id="lineas" width="1080" height="1920"></svg>
  <div id="fxl">{"".join(FXL)}</div>
  <div id="marca">@mundo.supuesto</div>
  <div id="subs" data-layout-allow-overlap>{"".join(SUBS)}</div>
  <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
</div>
<script src="escena2.js"></script>
<script>
const E = window.ESC;
E.aplica();
const R = {{ cim: E.resalta(E.cimientos), arc: E.resalta(E.arcos), anc: E.resalta(E.anclajes), pen: E.resalta(E.pendolas), cab: E.resalta(E.cables) }};
Object.values(R).forEach(r => r.set(0));
const HL = {{ cim:0, arc:0, anc:0, pen:0, cab:0 }};
const C = {{ px:{HERO[0][0]}, py:{HERO[0][1]}, pz:{HERO[0][2]}, tx:{HERO[1][0]}, ty:{HERO[1][1]}, tz:{HERO[1][2]} }};
const LABS = [], LV = {{}};
const SVGL = document.getElementById("lineas");
function frame() {{
  E.aplica();
  E.cam.position.set(C.px, C.py, C.pz); E.cam.lookAt(C.tx, C.ty, C.tz); E.cam.updateMatrixWorld();
  const pul = 0.75 + 0.25 * Math.sin(E.st.t * 6);
  for (const k in R) R[k].set(HL[k] * pul);
  let s = "";
  for (const L of LABS) {{
    const v = LV["l" + L.i] || 0; const el = document.getElementById("lab" + L.i); el.style.opacity = v;
    if (v > 0.01) {{ const [x, y] = E.proyecta(new THREE.Vector3(L.p[0], L.p[1], L.p[2]));
      const ex = L.lx + (L.lx < 400 ? 40 : 20), ey = L.ly + 4;
      s += `<path d="M${{x}},${{y}} L${{ex}},${{ey}}" stroke="#4fd1ff" stroke-width="2" fill="none" opacity="${{v}}"/><circle cx="${{x}}" cy="${{y}}" r="7" fill="#4fd1ff" opacity="${{v}}"/><circle cx="${{x}}" cy="${{y}}" r="${{14 + 8 * pul}}" fill="none" stroke="#4fd1ff" stroke-width="2" opacity="${{v * 0.5}}"/>`; }}
  }}
  SVGL.innerHTML = s;
  E.render();
}}
const tl = gsap.timeline({{ paused: true, onUpdate: frame }});
{chr(10).join(tl)}
tl.to({{}}, {{duration:0.01}}, {DUR - 0.01});
window.__timelines["main"] = tl;
tl.seek(0); frame();
</script>
</body></html>"""
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump(FX, open(os.path.join(BASE, "efectos.json"), "w"))
json.dump([[0, 0.0], [DUR, 0.0]], open(os.path.join(BASE, "ambiente.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones")

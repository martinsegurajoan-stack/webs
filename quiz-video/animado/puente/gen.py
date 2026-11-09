#!/usr/bin/env python3
"""«Cómo se construye un puente colgante sobre el mar» — maqueta isométrica plana (three.js, iso.js) controlada por GSAP:
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
def fx(k, t): pass   # usuario 09-11: fuera todos los efectos (solo voz + música suave)

# ------------------------------------------------------------------ cámara ortográfica (proxy C) y estado de obra (E.st)
TX, TH, DECK, PROF, ANCLA = 450, 300, 96, 130, 770
def yC(x):
    ax = abs(x)
    if ax <= TX: return (DECK + 16) + (TH + 6 - (DECK + 16)) * (ax / TX) ** 2
    return (TH + 6) + (20 - (TH + 6)) * (ax - TX) / (ANCLA - TX)
HERO = ((0, 90, 0), (-1, 0.76, 1), 0.66)
def cam(t, tgt, dr, z, d=1.4, ease="power2.inOut"):
    J(f'tl.to(C, {{tx:{tgt[0]}, ty:{tgt[1]}, tz:{tgt[2]}, dx:{dr[0]}, dy:{dr[1]}, dz:{dr[2]}, z:{z}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
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
    J(f'tl.fromTo(LV, {{l{i}:0}}, {{l{i}:1, duration:0.45, ease:"power2.out", immediateRender:false}}, {t:.2f}); tl.to(LV, {{l{i}:0, duration:0.3}}, {hasta:.2f});')
    J(f'LV.l{i} = 0;')
    fx("pop", t)
def dato(html, t, hasta, top=1420):
    NL[0] += 1; i = NL[0]
    FXL.append(f'<div class="dato" id="d{i}" style="top:{top}px">{html}</div>')
    J(f'tl.set("#d{i}", {{opacity:0}}, 0); tl.fromTo("#d{i}", {{opacity:0, y:30, letterSpacing:"8px"}}, {{opacity:1, y:0, letterSpacing:"0px", duration:0.6, ease:"power3.out", immediateRender:false}}, {t:.2f}); tl.to("#d{i}", {{opacity:0, y:-20, duration:0.3}}, {hasta:.2f});')
    fx("golpe", t)
    return i
def PL(word):
    n = sum(1 for w, a, b in WORDS if w == norm(word)); return P(word, n)

# ------------------------------------------------------------------ GUION VISUAL
J(f'tl.to(E.st, {{t:{DUR:.2f}, duration:{DUR:.2f}, ease:"none"}}, 0);')
J('Object.assign(E.st, {luz:1, coches:1});')
# 1) gancho: el puente terminado, de noche con tráfico; leve deriva de cámara
cam(0.0, (0, 80, 0), (-1, 0.72, 1.05), 0.72, FE(1), "sine.inOut")
d1 = dato('<b>1.000 m</b><small>NI UNA COLUMNA EN EL AGUA</small>', 0.0, P("coches") - 0.2, top=1440)
J('tl.set("#d1", {opacity:1, y:0, letterSpacing:"0px"}, 0);')
dato('<b>¿Cómo se aguanta?</b>', P("aguanta") - 0.6, FE(1) + 0.2, top=1460)
# 2) mar profundo, corrientes, barcos enormes
st(F(2) - 0.3, 0.6, luz=0, coches=0)
cam(F(2) - 0.2, (0, -40, 60), (-0.55, 0.42, 1), 1.35, 1.0)
st(F(2) + 0.2, 0.6, agua=0.45)
st(P("barcos") - 1.2, FE(2) - P("barcos") + 2.6, "none", barcoZ=-260)
etiqueta((0, -PROF + 10, 120), 70, 1250, "PROFUNDIDAD", "Mar profundo", "", P("profundo") - 0.2, P("corrientes") - 0.1)
etiqueta((-260, -6, 140), 70, 1250, "CORRIENTES", "Fuertes", "", P("corrientes") - 0.1, P("barcos") - 0.3)
etiqueta((0, 30, 120), 560, 1300, "PASO LIBRE", "Barcos enormes", "por debajo del puente", P("barcos") - 0.3, FE(2) + 0.2)
st(FE(2), 0.5, agua=1)
# 3) un pilar en medio: no. Lo cuelgan
cam(F(3) - 0.1, (0, 40, 0), (-1, 0.6, 1.1), 0.95, 1.0)
J(f'tl.set(E.st, {{barcoZ:260}}, {F(3) + 0.3:.2f});')
st(P("pilar") - 0.1, 0.5, fan=1); st(P("estorbo") + 0.2, 0.4, fan=0)
FXL.append('<div class="tacha" id="tacha">✕</div>')
J(f'tl.set("#tacha", {{opacity:0}}, 0); tl.fromTo("#tacha", {{opacity:0, scale:2}}, {{opacity:1, scale:1, duration:0.3, ease:"back.out(2)", immediateRender:false}}, {P("estorbo") - 0.3:.2f}); tl.to("#tacha", {{opacity:0, duration:0.3}}, {P("estorbo") + 0.5:.2f});')
fx("denegada", P("estorbo") - 0.3)
cam(P("cuelgan") - 0.7, (0, 190, 0), (-0.7, 0.45, 1), 1.25, 0.9)
hl("cab", P("cuelgan") - 0.3, FE(3) + 0.3)
dato('<b>Lo cuelgan</b>', P("cuelgan") - 0.2, FE(3) + 0.3, top=1440)
# 4) rebobinado: cajones de hormigón bajo el agua
fx("rebobina", F(4) - 0.3)
st(F(4) - 0.3, 0.7, "power2.in", tor=0, hilo=0, pen=0, dov=0, anc=0, asf=0, cim=0)
cam(F(4) - 0.2, (-TX, -60, 0), (-0.3, 0.22, 1), 2.3, 1.2)
st(F(4) + 0.4, 0.6, agua=0.22)
st(P("hunde") - 0.1, P("firme") - P("hunde") + 0.4, "power1.inOut", cim=1)
fx("golpe", P("firme"))
hl("cim", P("cajon") - 0.1, FE(4) + 0.4)
etiqueta((-TX + 40, -PROF + 20, 40), 560, 1300, "CIMENTACIÓN", "Cajón de hormigón", "hundido hasta la roca", P("cajon") - 0.1, FE(4) + 0.3)
# 5) torres de +200 m; arriba, arcos huecos
st(F(5) - 0.1, 0.5, agua=1)
cam(F(5) - 0.2, (-TX, 150, 0), (-1, 0.42, 0.75), 1.45, 1.2)
st(P("levantan") - 0.2, 2.6, "power2.out", tor=1)
i_alt = dato('<b><span id="altN">0</span> m</b><small>DE ALTURA</small>', P("levantan") - 0.2, P("fijate") - 0.2, top=1460)
J(f'const altv = {{v:0}}; tl.to(altv, {{v:210, duration:{P("doscientos") - P("levantan") + 0.6:.2f}, ease:"power2.out", onUpdate:() => {{ document.getElementById("altN").textContent = (altv.v > 205 ? "+" : "") + Math.round(Math.min(altv.v, 200)); }}}}, {P("levantan") - 0.2:.2f});')
cam(P("fijate") - 0.5, (-TX, 215, 0), (-1, 0.28, 0.32), 2.9, 1.1)
hl("arc", P("arriba") - 0.1, FE(5) + 0.3)
etiqueta((-TX, 230, 0), 600, 1300, "LA TORRE", "Arcos huecos", "menos peso, menos viento", P("arcos") - 0.3, FE(5) + 0.3)
# 6) el cable piloto cruza con un dron
cam(F(6) - 0.2, (0, 190, 0), (-0.45, 0.5, 1), 0.85, 1.2)
st(P("cruzar") - 0.2, FE(6) - P("cruzar") + 0.4, "power1.inOut", pil=1)
etiqueta((0, yC(0) + 2, 0), 560, 1300, "CABLE PILOTO", "Un primer hilo", "de orilla a orilla", P("cable") - 0.1, FE(6) + 0.2)
fx("whoosh", P("dron") - 0.2)
# 7) pasarela e hilado: la rueda va y viene
st(P("pasarela") - 0.2, 0.8, pas=1)
cam(P("pasarela") - 0.3, (-220, yC(-220) - 10, 0), (-0.75, 0.55, 1), 2.2, 1.2)
J(f'tl.set(E.st, {{ruedaOn:1, hilo:0.05}}, {P("hilado") - 0.2:.2f});')
st(P("hilado") - 0.2, FE(8) - P("hilado") + 0.2, "none", rueda=6)
etiqueta((-220, yC(-220), 30), 600, 1300, "HILADO", "Alambres de 5 mm", "una rueda los lleva de lado a lado", P("rueda") - 0.2, FE(7) + 0.2)
# 8) decenas de miles de alambres → cable de más de un metro
cam(F(8) - 0.1, (-TX + 60, yC(-TX + 60), 30), (-1, 0.35, 0.6), 4.2, 1.2)
st(F(8) + 0.2, 0.1, hilo=0.5)
FXL.append('<div id="seccion" class="seccion"><svg viewBox="0 0 400 400" width="420" height="420"><circle cx="200" cy="200" r="190" fill="#1b1f27" stroke="#e6ebf2" stroke-width="6"/>'
           + "".join(f'<circle class="al" cx="{200 + r * __import__("math").cos(a):.1f}" cy="{200 + r * __import__("math").sin(a):.1f}" r="5" fill="#e6ebf2"/>'
                     for r, n in ((0, 1), (14, 6), (28, 12), (42, 18), (56, 24), (70, 30), (84, 36), (98, 42), (112, 48), (126, 54), (140, 60), (154, 66), (168, 72))
                     for a in [k * 2 * 3.14159 / n for k in range(n)])
           + '</svg><b id="alN">1</b><small>ALAMBRES</small></div>')
J('tl.set("#seccion", {opacity:0}, 0); tl.set(".al", {opacity:0}, 0);')
J(f'tl.fromTo("#seccion", {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.5, ease:"back.out(1.6)", immediateRender:false}}, {F(8):.2f}); tl.to(".al", {{opacity:1, duration:0.02, stagger:{2.4 / 469:.4f}}}, {F(8) + 0.2:.2f}); tl.to("#seccion", {{opacity:0, duration:0.3}}, {FE(8) + 0.2:.2f});')
J(f'const alv = {{v:1}}; tl.to(alv, {{v:36830, duration:2.6, ease:"power2.in", onUpdate:() => {{ document.getElementById("alN").textContent = String(Math.round(alv.v)).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, "."); }}}}, {F(8) + 0.2:.2f});')
fx("cuenta", F(8) + 0.2)
st(P("apretados") - 0.2, 0.1, hilo=1)
st(P("apretados"), 0.6, pas=0)
J(f'tl.set(E.st, {{ruedaOn:0}}, {FE(8):.2f});')
dato('<b>&gt; 1 m</b><small>DE GROSOR</small>', P("grosor") - 0.6, FE(8) + 0.3, top=1460)
# 9) anclajes
cam(F(9) - 0.2, (-ANCLA, 40, 0), (-1, 0.6, 0.9), 2.0, 1.2)
st(F(9) + 0.3, 1.4, "power2.out", anc=1)
hl("anc", P("anclajes") - 0.2, FE(9) + 0.3)
etiqueta((-ANCLA, 50, 50), 560, 1300, "ANCLAJE", "Hormigón macizo", "sujeta el cable en tierra", P("anclajes") - 0.2, FE(9) + 0.3)
# 10) péndolas
cam(F(10) - 0.2, (0, 150, 0), (-0.4, 0.42, 1), 1.15, 1.0)
st(P("pendolas") - 0.4, FE(10) - P("pendolas") + 0.6, "power1.inOut", pen=1)
hl("pen", P("pendolas"), FE(10) + 0.3)
etiqueta((120, 150, 30), 600, 1300, "PÉNDOLAS", "Cables verticales", "cada pocos metros", P("pendolas") - 0.1, FE(10) + 0.3)
# 11-12) el tablero: barcazas, grúa, del centro hacia las torres
cam(F(11) - 0.2, (0, 50, 0), (-0.75, 0.5, 1), 2.0, 1.0)
st(P("barcazas") - 0.3, FE(12) - P("barcazas") + 0.2, "none", dov=1)
etiqueta((0, 10, 40), 560, 1300, "BARCAZA", "Tramos ya fabricados", "una grúa los sube y engancha", P("barcazas") - 0.2, FE(11) + 0.2)
cam(F(12) - 0.2, (0, 60, 0), (-0.25, 1.6, 0.8), 0.85, 1.4)
FXL.append('<div id="flechas" class="flechas"><span>⟵</span><span>CENTRO</span><span>⟶</span></div>')
J(f'tl.set("#flechas", {{opacity:0}}, 0); tl.to("#flechas", {{opacity:1, duration:0.3}}, {P("centro") - 0.2:.2f}); tl.to("#flechas", {{opacity:0, duration:0.3}}, {FE(12) + 0.2:.2f});')
# 13) el truco: el recorrido del peso
cam(F(13) - 0.2, (0, 110, 0), (-1, 0.62, 1.1), 0.82, 1.2)
st(F(13) + 0.1, 0.6, fza=1)
hl("pen", P("pendolas", 2) - 0.2, P("cable", 4) + 0.4); hl("cab", P("cable", 4) - 0.2, P("torres", 3) - 0.1)
hl("arc", P("torres", 3) - 0.2, FE(13) + 0.6); hl("anc", P("anclajes", 2) - 0.2, FE(13) + 0.6)
etiqueta((-TX, TH, 0), 600, 1300, "EL PESO VIAJA", "Péndolas → cable", "→ torres y anclajes", F(13) + 0.6, FE(13) + 0.3)
# 14) ni un kilo al mar
cam(F(14) - 0.2, (0, -50, 0), (-0.2, 0.25, 1), 1.3, 1.0)
st(F(14) - 0.2, 0.5, agua=0.25)
dato('<b><span id="kgN">250.000</span> kg</b><small>PESO QUE CAE SOBRE EL MAR</small>', P("kilo") - 0.4, FE(14) + 0.3, top=1440)
J(f'const kgv = {{v:250000}}; tl.to(kgv, {{v:0, duration:1.2, ease:"power2.in", onUpdate:() => {{ document.getElementById("kgN").textContent = String(Math.round(kgv.v)).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, "."); }}}}, {P("kilo") - 0.2:.2f});')
st(FE(14) + 0.2, 0.5, agua=1, fza=0)
# 15) último tramo, asfalto, luces
cam(F(15) - 0.2, (-260, 96, 0), (-0.8, 0.55, 1), 1.7, 1.1)
st(F(15) + 0.4, P("luces") - F(15) - 0.8, "power1.inOut", asf=1)
st(P("luces") - 0.2, 0.8, luz=1, coches=1)
fx("ding", P("luces"))
# 16) viento: el tablero se mueve
cam(F(16) - 0.2, (0, 100, 0), (0.15, 1.2, 1), 1.25, 1.0)
st(F(16), 0.8, vien=1); st(FE(16) - 0.4, 0.8, vien=0)
FXL.append('<div id="viento" class="viento">' + "".join(f'<i style="top:{900 + k * 70}px"></i>' for k in range(8)) + '</div>')
J('tl.set("#viento", {opacity:0}, 0);')
J(f'tl.to("#viento", {{opacity:1, duration:0.4}}, {F(16):.2f}); tl.fromTo("#viento i", {{x:-700}}, {{x:1400, duration:1.2, stagger:0.15, repeat:3, ease:"none", immediateRender:false}}, {F(16):.2f}); tl.to("#viento", {{opacity:0, duration:0.4}}, {FE(16):.2f});')
fx("whoosh", F(16))
etiqueta((0, DECK, 30), 560, 1300, "FLEXIBLE", "Se mueve varios metros", "si fuera rígido, se rompería", PL("metros") - 0.6, FE(16) + 0.2)
# 17) cierre: vuelve exactamente al plano del principio (bucle)
cam(F(17) - 0.2, (0, 90, 0), (-1, 0.76, 1), 0.66, DUR - F(17) - 0.3, "sine.inOut")
dato('<b>Colgado de dos cables</b>', P("cables", 2) - 0.6, DUR - 1.2, top=1440)
J(f'tl.fromTo("#d1", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.6, ease:"power3.out", immediateRender:false}}, {DUR - 1.0:.2f});')

# pasos de la obra: barra inferior que avanza
PASOS = [("Cimientos", F(4)), ("Torres", F(5)), ("Cable", F(6)), ("Anclajes", F(9)), ("Péndolas", F(10)), ("Tablero", F(11)), ("Luces", F(15))]
FXL.append('<div id="pasos"><div class="pbar"><i id="pfill"></i></div>' + "".join(f'<div class="paso" id="paso{k}" style="left:{40 + k * 150}px"><span class="pdot"></span><em>{n}</em></div>' for k, (n, t) in enumerate(PASOS)) + '</div>')
J(f'tl.set("#pasos", {{opacity:0, y:40}}, 0); tl.to("#pasos", {{opacity:1, y:0, duration:0.6, ease:"power3.out"}}, {F(4) - 0.2:.2f}); tl.to("#pasos", {{opacity:0, y:40, duration:0.5}}, {FE(15) + 0.8:.2f});')
J('tl.set("#pfill", {width:0}, 0);')
for k, (n, t) in enumerate(PASOS):
    J(f'tl.to("#paso{k} .pdot", {{backgroundColor:"#4ea3ff", borderColor:"#4ea3ff", scale:1.5, duration:0.35, ease:"back.out(3)"}}, {t:.2f}); tl.to("#paso{k} em", {{color:"#ffffff", duration:0.3}}, {t:.2f});')
    J(f'tl.to("#pfill", {{width:{k * 150}, duration:0.6, ease:"power2.inOut"}}, {t - 0.3:.2f});')
    if k + 1 < len(PASOS):
        J(f'tl.to("#paso{k} .pdot", {{scale:1, duration:0.3}}, {PASOS[k + 1][1]:.2f}); tl.to("#paso{k} em", {{color:"rgba(255,255,255,0.75)", duration:0.3}}, {PASOS[k + 1][1]:.2f});')
# nubes que cruzan el cielo (bucle exacto: vuelven a su sitio al final)
NUB = [(60, 560, 0.9), (640, 640, 0.75), (860, 520, 1.1), (180, 1500, 0.85), (760, 1540, 1.0)]
FXN = "".join(f'<div class="nube" id="nb{k}" style="left:{x}px;top:{y}px;transform:scale({sc})"><i></i><i></i><i></i></div>' for k, (x, y, sc) in enumerate(NUB))
for k in range(len(NUB)):
    J(f'tl.fromTo("#nb{k}", {{x:0}}, {{x:{(-1) ** k * 70}, duration:{DUR / 2:.2f}, ease:"sine.inOut", yoyo:true, repeat:1, immediateRender:false}}, 0);')

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
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;background:linear-gradient(180deg, #3f8fd2 0%, #74b6e6 38%, #b9dcf3 72%, #e4f2fb 100%);color:#fff}}
#gl{{position:absolute;inset:0}}
#fxl{{position:absolute;inset:0;z-index:58;pointer-events:none}} svg#lineas{{position:absolute;inset:0;z-index:57;pointer-events:none}}
.lab{{position:absolute;padding:16px 22px 18px;border-radius:16px;background:rgba(18,21,27,0.78);border:1px solid rgba(255,255,255,0.12);backdrop-filter:blur(6px);opacity:0}}
.lab small{{display:block;font:700 17px Inter;letter-spacing:5px;color:#4ea3ff;margin-bottom:6px}} .lab b{{display:block;font:600 42px/1.12 Inter;letter-spacing:-0.5px}}
.lab em{{display:block;font-style:normal;font:500 24px/1.3 Inter;color:rgba(255,255,255,0.68);margin-top:6px}}
.dato{{position:absolute;left:0;right:0;text-align:center}} .dato > *{{background:rgba(14,30,52,0.78)}} .dato b{{display:inline-block !important;padding:18px 42px 14px;border-radius:26px 26px 0 0}} .dato small{{display:block !important;width:max-content;margin:0 auto !important;padding:0 36px 16px;border-radius:0 0 22px 22px}}
.dato b{{font:300 104px/1 Inter;letter-spacing:-3px}} .dato small{{display:block;margin-top:12px;font:600 22px Inter;letter-spacing:8px;color:rgba(255,255,255,0.7)}}
.tacha{{position:absolute;left:0;right:0;top:820px;text-align:center;font:200 300px/1 Inter;color:#ffffff;text-shadow:0 6px 30px rgba(8,30,60,0.6)}}
.seccion{{position:absolute;left:240px;right:240px;top:560px;padding:30px 0 34px;text-align:center;background:rgba(18,21,27,0.88);border-radius:28px;border:1px solid rgba(255,255,255,0.12)}} .seccion b{{display:block;font:300 100px/1 Inter;letter-spacing:-3px;margin-top:10px;font-variant-numeric:tabular-nums}} .seccion small{{font:600 22px Inter;letter-spacing:8px;color:rgba(255,255,255,0.7)}}
.flechas{{position:absolute;left:250px;right:250px;top:1440px;padding:6px 0;border-radius:26px;background:rgba(14,30,52,0.72);display:flex;justify-content:center;gap:40px;font:300 70px Inter;color:#4ea3ff}} .flechas span:nth-child(2){{font:600 26px Inter;letter-spacing:8px;color:#fff;align-self:center}}
.viento{{position:absolute;inset:0}} .viento i{{position:absolute;left:0;width:420px;height:3px;border-radius:2px;background:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,255,255,0.7),rgba(255,255,255,0))}}
#grano{{position:absolute;inset:0;z-index:56;pointer-events:none;opacity:0.03;background:url(assets/grano.png);mix-blend-mode:overlay}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:520px;z-index:55;pointer-events:none;background:linear-gradient(rgba(16,52,92,0.55),rgba(16,52,92,0))}}
#nubes{{position:absolute;inset:0;z-index:0;pointer-events:none}} .nube{{position:absolute;width:260px;height:80px;transform-origin:center}}
.nube i{{position:absolute;bottom:0;border-radius:50%;background:#ffffff;opacity:0.92}} .nube i:nth-child(1){{left:0;width:130px;height:60px}} .nube i:nth-child(2){{left:60px;width:130px;height:90px}} .nube i:nth-child(3){{left:130px;width:120px;height:62px}}
#pasos{{position:absolute;left:20px;top:1630px;height:118px;width:1040px;border-radius:28px;background:rgba(14,30,52,0.72)}}
#pasos .pbar{{position:absolute;left:60px;top:36px;width:900px;height:4px;border-radius:2px;background:rgba(255,255,255,0.18)}} #pasos .pbar i{{position:absolute;left:0;top:0;bottom:0;border-radius:2px;background:#4ea3ff}}
#pasos .paso{{position:absolute;top:14px;width:40px;text-align:center}} #pasos .pdot{{display:block;margin:10px auto 0;width:28px;height:28px;border-radius:50%;border:4px solid rgba(255,255,255,0.35);background:#1d3350;box-sizing:border-box}}
#pasos em{{position:absolute;left:-60px;right:-60px;top:50px;font:700 21px Inter;font-style:normal;color:rgba(255,255,255,0.75);text-shadow:0 2px 8px rgba(10,30,60,0.6);letter-spacing:0.5px}}
#marca{{position:absolute;left:0;right:0;top:1820px;text-align:center;font:600 26px Inter;color:#ffffff;opacity:0.45;pointer-events:none;z-index:61}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 58px Inter;color:rgba(255,255,255,0.62);line-height:1.22;text-shadow:0 3px 14px rgba(8,30,60,0.75)}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:3px solid #4ea3ff;border-radius:6px;background:rgba(78,163,255,0.18);opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="nubes">{FXN}</div>
  <div id="gl"></div>
  <div id="topsombra"></div><div id="grano"></div>
  <svg id="lineas" width="1080" height="1920"></svg>
  <div id="fxl">{"".join(FXL)}</div>
  <div id="marca">@mundo.supuesto</div>
  <div id="subs" data-layout-allow-overlap>{"".join(SUBS)}</div>
  <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
</div>
<script src="iso.js"></script>
<script>
const E = window.ESC;
const R = {{ cim: E.resalta(E.cimientos), arc: E.hueR, anc: E.resalta(E.anclajes), pen: E.resalta(E.pendolas), cab: E.resalta(E.cables) }};
Object.values(R).forEach(r => r.set(0));
const HL = {{ cim:0, arc:0, anc:0, pen:0, cab:0 }};
const C = {{ tx:0, ty:90, tz:0, dx:-1, dy:0.76, dz:1, z:0.66 }};
const LABS = [], LV = {{}};
const SVGL = document.getElementById("lineas");
function frame() {{
  E.aplica();
  const w = 2 * Math.PI * E.st.t / {DUR:.3f}; const ddx = C.dx + 0.07 * Math.sin(4 * w); const n = Math.hypot(ddx, C.dy, C.dz) / 1500; E.pon(C.tx + ddx / n, C.ty + C.dy / n, C.tz + C.dz / n, C.tx, C.ty, C.tz, C.z * (1 + 0.035 * Math.sin(6 * w))); E.cam.updateMatrixWorld();
  const pul = 0.75 + 0.25 * Math.sin(E.st.t * 6);
  for (const k in R) R[k].set(HL[k] * pul);
  let s = "";
  for (const L of LABS) {{
    const v = LV["l" + L.i] || 0; const el = document.getElementById("lab" + L.i); el.style.opacity = v;
    if (v > 0.01) {{ const [x, y] = E.proyecta(new THREE.Vector3(L.p[0], L.p[1], L.p[2]));
      const ex = L.lx + (L.lx < 400 ? 40 : 20), ey = L.ly + 4;
      s += `<path d="M${{x}},${{y}} L${{ex}},${{ey}}" stroke="#4ea3ff" stroke-width="2" fill="none" opacity="${{v}}"/><circle cx="${{x}}" cy="${{y}}" r="7" fill="#4ea3ff" opacity="${{v}}"/><circle cx="${{x}}" cy="${{y}}" r="${{14 + 8 * pul}}" fill="none" stroke="#4ea3ff" stroke-width="2" opacity="${{v * 0.5}}"/>`; }}
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

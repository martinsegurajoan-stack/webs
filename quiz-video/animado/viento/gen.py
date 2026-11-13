#!/usr/bin/env python3
"""«¿Qué pasaría si el viento desapareciera?» — UN SOLO PLANO: playa con viento (bandera, cometa, olas, velero) → el viento
se para → la cámara viaja tierra adentro (mar espejo, molinos, ciudad con niebla tóxica, maizal, Biosfera 2, sequía) →
sube al espacio (globo: calor, polvo del Sáhara, pesca, albatros, huracanes) → vuelve a la playa con el viento (bucle).
Todo lo que se mueve depende de S.v (1 = viento, 0 = calma). Sin efectos de sonido.
  python3 gen.py → index.html + efectos.json + ambiente.json"""
import json, math, os, random, re, unicodedata

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
tl, FXL = [], []
def J(s): tl.append(s)
exec(open(os.path.join(BASE, "_rig.py"), encoding="utf-8").read())
rr = random.Random(11)

# ------------------------------------------------------------------ escenas (x del mundo; suelo en y = 0)
X_PLAYA, X_MAR, X_MOL, X_CIU, X_MAIZ, X_BIO, X_SECO = 120, -620, 1900, 3700, 5500, 7300, 9100
GLOBO = (9100, -6200, 420)                      # centro y radio del planeta en el cielo
M = []
# --- mar (a la izquierda de la playa)
M.append('<rect x="-3200" y="-2" width="3060" height="2000" fill="url(#mar)"/>')
M.append('<path id="olas" d="" fill="#4aa8d8"/><path id="espuma" d="" fill="none" stroke="#ffffff" stroke-width="5" stroke-linecap="round" opacity="0.85"/>')
M.append('<path id="brillo" d="M-2600,30 H-300" stroke="#ffffff" stroke-width="3" stroke-dasharray="40 90" opacity="0"/>')
# velero y surfista
M.append('<g id="velero"><path d="M-70,0 L70,0 L52,24 L-52,24 Z" fill="#ffffff"/><rect x="-4" y="-170" width="7" height="172" fill="#5b4636"/>'
         '<path id="vela" d="" fill="#fdf7ea" stroke="#e6dcc6" stroke-width="2"/><path d="M-6,-150 L-60,-10 L-6,-10 Z" fill="#f2b84b"/></g>')
M.append('<g id="surf"><ellipse cx="0" cy="0" rx="58" ry="7" fill="#ff7a59"/><g id="surfista"><circle cx="0" cy="-74" r="11" fill="#c98e6b"/>'
         '<path d="M-6,-62 L6,-62 L8,-30 L-8,-30 Z" fill="#2b6cb0"/><path d="M-8,-30 L-18,-2 M8,-30 L16,-2" stroke="#1d3557" stroke-width="7" stroke-linecap="round"/>'
         '<path d="M-6,-56 L-26,-44 M6,-56 L26,-44" stroke="#c98e6b" stroke-width="5" stroke-linecap="round"/></g></g>')
# --- playa
M.append('<path d="M-160,0 Q200,-14 900,-6 L900,2000 L-160,2000 Z" fill="#f1dfae"/><path d="M-160,0 Q200,-14 900,-6" stroke="#e8d197" stroke-width="6" fill="none"/>')
for k in range(26):
    x = -100 + k * 38; M.append(f'<circle cx="{x}" cy="{14 + (k * 7) % 30}" r="2.4" fill="#dcc283"/>')
M.append('<g transform="translate(470,-6)"><rect x="-3" y="-150" width="6" height="150" fill="#ffffff"/><path d="M-90,-140 Q0,-200 90,-140 Z" fill="#ef5b3b"/><path d="M-30,-140 Q0,-196 30,-140 Z" fill="#ffffff"/>'
         '<rect x="-60" y="-14" width="120" height="14" rx="6" fill="#4ea3ff"/></g>')
M.append('<g transform="translate(700,-8)"><path d="M0,0 Q-12,-160 18,-330" stroke="#8a5a3c" stroke-width="18" fill="none" stroke-linecap="round"/>'
         '<g id="palma" transform="translate(18,-330)">' + "".join(f'<path d="M0,0 Q{60 * math.cos(a)},{60 * math.sin(a) - 30} {120 * math.cos(a)},{120 * math.sin(a) + 20}" stroke="#3f8f3a" stroke-width="16" fill="none" stroke-linecap="round"/>' for a in (-2.9, -2.2, -1.5, -0.8, -0.2, 0.5)) + '</g></g>')
M.append('<g transform="translate(390,-8)"><rect x="-3" y="-260" width="6" height="260" fill="#d9dde3"/><g id="bandera"><path id="tela" d="" fill="#ef5b3b"/></g></g>')
# gaviotas (planean con viento; se posan sin él)
M.append('<g id="gaviotas">' + "".join(f'<path class="gav" d="M-14,0 q7,-8 14,0 q7,-8 14,0" stroke="#2b3440" stroke-width="3" fill="none"/>' for _ in range(3)) + '</g>')
# protagonista (rig) con cometa
PROTA = dict(piel="#e8b896", pelo="#3b2a20", camisa="#2f9e8f", pantalon="#33415c", zapato="#f4f4f4")
PR["cometa"] = dict(tor=-90, hd=-100, uaN=-35, faN=-55, uaF=86, faF=80, thN=92, shN=90, thF=88, shF=90)
PR["mira"] = dict(tor=-90, hd=-86, uaN=95, faN=85, uaF=86, faF=80, thN=92, shN=90, thF=88, shF=90)
fig = rig("P", PROTA).replace('cy="84"', 'cy="92"')
MECHAS = '<g id="mechas">' + "".join(f'<path class="mecha" d="M0,0 q6,-10 16,-12" stroke="#3b2a20" stroke-width="5" fill="none" stroke-linecap="round" transform="translate({x},{y})"/>' for x, y in ((-6, -182), (2, -186), (10, -184))) + '</g>'
M.append(f'<g transform="translate({X_PLAYA},-4)"><g transform="translate(0,-92)">{fig}</g>{MECHAS}</g>')
M.append('<path id="hilo" d="" stroke="#ffffff" stroke-width="2" fill="none" opacity="0.9"/><g id="cometa"><path d="M0,-38 L26,0 L0,46 L-26,0 Z" fill="#ffd23f"/><path d="M0,-38 L0,46 M-26,0 L26,0" stroke="#e0a800" stroke-width="2"/>'
         '<path id="cola" d="" stroke="#ef5b3b" stroke-width="3" fill="none"/></g>')
# --- campo verde general (playa → interior)
M.append('<rect x="880" y="-6" width="11000" height="2000" fill="#7cb85a"/><rect x="880" y="-6" width="11000" height="10" fill="#6aa64a"/>')
# --- molinos en colinas
M.append(f'<path d="M1000,0 Q1450,-260 1900,-120 Q2350,-300 2800,0 Z" fill="#8cc56a"/>')
for k, (x, hgt) in enumerate(((1480, 520), (1900, 440), (2330, 480))):
    y0 = -110 if k == 1 else -180
    M.append(f'<g transform="translate({x},{y0 + 120})"><path d="M-9,0 L9,0 L5,{-hgt} L-5,{-hgt} Z" fill="#f4f6f8"/><g transform="translate(0,{-hgt})"><g class="aspas">'
             + "".join(f'<path d="M0,0 L-7,-12 Q-4,-150 0,-190 Q4,-150 7,-12 Z" fill="#ffffff" stroke="#d5dbe1" stroke-width="1.5" transform="rotate({a})"/>' for a in (0, 120, 240))
             + '</g><circle r="11" fill="#e6eaee"/></g></g>')
# --- ciudad con niebla tóxica
for k in range(13):
    x = 2950 + k * 118; h = rr.choice([300, 420, 520, 640, 760]); w = rr.choice([90, 104, 112]); c = rr.choice(["#e9e2d3", "#dfe6ee", "#f3d9c4", "#d9e4d2", "#e6dcef"])
    M.append(f'<rect x="{x}" y="{-h}" width="{w}" height="{h}" fill="{c}"/>')
    for j in range(int(h / 70)):
        for i in range(2):
            M.append(f'<rect class="ven" x="{x + 16 + i * (w - 48) / 1}" y="{-h + 22 + j * 70}" width="22" height="30" fill="#9fc3dc"/>')
M.append('<rect x="2900" y="-6" width="1700" height="40" fill="#5b6270"/>' + "".join(f'<rect x="{2920 + k * 90}" y="10" width="40" height="5" fill="#f3f3f3"/>' for k in range(19)))
M.append('<g id="coches">' + "".join(f'<g class="coche"><rect x="-40" y="-22" width="80" height="22" rx="8" fill="{c}"/><rect x="-24" y="-38" width="46" height="18" rx="6" fill="{c}"/><circle cx="-24" cy="0" r="8" fill="#222"/><circle cx="24" cy="0" r="8" fill="#222"/></g>' for c in ("#d94f45", "#4ea3ff", "#f2b84b")) + '</g>')
M.append('<rect id="smog" x="2700" y="-900" width="2100" height="920" fill="url(#smogG)" opacity="0"/>')
# --- maizal
for k in range(22):
    x = 4800 + k * 64 + (k % 3) * 6; h = 200 + (k * 37) % 50
    M.append(f'<g transform="translate({x},0)"><path d="M0,0 L0,{-h}" stroke="#5c9a3e" stroke-width="7"/>'
             f'<path d="M0,{-h * 0.35} q-36,-20 -50,6 M0,{-h * 0.55} q36,-24 52,4 M0,{-h * 0.75} q-30,-20 -44,4" stroke="#6aa64a" stroke-width="7" fill="none" stroke-linecap="round"/>'
             f'<ellipse cx="9" cy="{-h * 0.5}" rx="8" ry="22" fill="#f2c94c" transform="rotate(14 9 {-h * 0.5})"/><path d="M0,{-h} l-10,-28 M0,{-h} l0,-32 M0,{-h} l10,-28" stroke="#d9b54a" stroke-width="4" stroke-linecap="round"/></g>')
M.append('<g id="polen">' + "".join('<circle class="pol" r="4" fill="#ffe27a"/>' for _ in range(40)) + '</g>')
# --- bosque + Biosfera 2
for x in (6550, 6680, 8000, 8120):
    M.append(f'<rect x="{x - 9}" y="-170" width="18" height="170" fill="#8a5a3c"/><circle cx="{x}" cy="-230" r="80" fill="#4f9a48"/><circle cx="{x + 30}" cy="-190" r="56" fill="#5aa752"/>')
M.append('<path d="M6850,0 A460,330 0 0 1 7770,0 Z" fill="#bfe4f7" opacity="0.45"/><path d="M6850,0 A460,330 0 0 1 7770,0" stroke="#ffffff" stroke-width="6" fill="none"/>')
M.append('<path d="M6930,-150 Q7310,-300 7690,-150 M7020,-250 Q7310,-340 7600,-250 M7310,-330 V0 M7080,-290 V0 M7540,-290 V0" stroke="#ffffff" stroke-width="3" fill="none" opacity="0.7"/>')
for x in (7080, 7200, 7460):
    M.append(f'<rect x="{x - 6}" y="-210" width="12" height="210" fill="#8a5a3c"/><circle cx="{x}" cy="-240" r="44" fill="#5aa752"/>')
M.append('<g id="arbolCae" transform="translate(7330,0)"><g id="arbolR"><rect x="-6" y="-230" width="12" height="230" fill="#8a5a3c"/><circle cx="0" cy="-262" r="46" fill="#67b25c"/></g></g>')
# --- llanura que se seca
M.append('<rect id="seco" x="8300" y="-6" width="3500" height="2000" fill="#c9a96b" opacity="0"/>')
M.append('<g id="grietas" opacity="0">' + "".join(f'<path d="M{8400 + k * 90},{30 + (k * 13) % 60} l20,18 l-12,22 l24,14" stroke="#8a6a3c" stroke-width="4" fill="none"/>' for k in range(30)) + '</g>')
M.append('<g transform="translate(8520,0)"><rect x="0" y="-150" width="190" height="150" fill="#e9dcc3"/><path d="M-16,-150 L95,-240 L206,-150 Z" fill="#b5543b"/><rect x="74" y="-80" width="44" height="80" fill="#7a4b32"/><rect x="22" y="-120" width="36" height="34" fill="#9fd3f0"/></g>')
M.append('<g transform="translate(8820,0)"><path d="M-30,0 L-14,-210 M30,0 L14,-210 M-22,-100 L22,-100" stroke="#6b5b4b" stroke-width="7"/><rect x="-34" y="-290" width="68" height="84" rx="6" fill="#a9b3be"/></g>')
M.append('<ellipse id="charca" cx="9330" cy="4" rx="190" ry="14" fill="#4aa8d8"/>')
for x in (9150, 9620, 9960):
    M.append(f'<g transform="translate({x},0)"><path d="M0,0 L0,-150 M0,-90 L-40,-140 M0,-110 L36,-160 M0,-140 L-20,-180" stroke="#7a5a3c" stroke-width="9" fill="none" stroke-linecap="round"/><g class="hoja"><circle cx="0" cy="-160" r="58" fill="#5aa752"/></g></g>')
M.append('<g opacity="0.95" transform="translate(8250,-760)"><ellipse rx="150" ry="46" fill="#fff"/><ellipse cx="70" cy="-34" rx="90" ry="56" fill="#fff"/><path d="M-60,40 l-10,40 M-10,40 l-10,40 M40,40 l-10,40" stroke="#9fd3f0" stroke-width="5"/></g>')
for x in (8600, 9000, 9500, 9800):
    M.append(f'<g class="arbusto" transform="translate({x},0)"><ellipse cx="0" cy="-30" rx="52" ry="34" fill="#5aa752"/><ellipse class="seco2" cx="0" cy="-30" rx="52" ry="34" fill="#a8895a" opacity="0"/></g>')
# --- planeta en el cielo
GX, GY, GR = GLOBO
def gp(px, py):          # coordenadas 0-1000 del dibujo → mundo
    return GX + (px - 500) * GR / 500, GY + (py - 500) * GR / 500
def gpath(d):
    return re.sub(r"(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)", lambda m: "{:.1f},{:.1f}".format(*gp(float(m.group(1)), float(m.group(2)))), d)
CONT = {
    "nam": "M120,180 C200,120 330,130 380,190 C400,240 360,300 330,330 C300,360 280,400 300,430 L330,470 L300,450 C240,400 180,360 150,300 C120,250 100,210 120,180 Z",
    "sam": "M330,470 C380,460 450,490 470,540 C480,600 440,660 410,720 C390,780 370,840 350,880 C340,840 330,780 320,720 C300,640 290,560 330,470 Z",
    "afr": "M560,330 C640,300 740,320 770,380 C800,430 790,470 760,500 C740,560 720,640 690,700 C670,740 640,760 620,740 C600,690 600,620 590,560 C560,520 520,480 520,430 C520,380 530,350 560,330 Z",
    "eur": "M560,300 C580,240 640,200 700,210 C740,220 770,250 735,290 C690,300 620,310 560,300 Z",
    "gro": "M400,90 C440,70 490,80 480,120 C460,150 410,150 400,90 Z",
}
G = [f'<g id="planeta" opacity="0"><circle cx="{GX}" cy="{GY}" r="{GR + 30}" fill="#8fd0ff" opacity="0.25"/><circle cx="{GX}" cy="{GY}" r="{GR}" fill="#2f7fc1"/>',
     f'<clipPath id="clipG"><circle cx="{GX}" cy="{GY}" r="{GR}"/></clipPath><g clip-path="url(#clipG)">']
for k, d in CONT.items():
    G.append(f'<path class="tierra" d="{gpath(d)}" fill="#5aa752"/>')
G.append(f'<ellipse id="sahara" cx="{gp(650, 395)[0]:.0f}" cy="{gp(650, 395)[1]:.0f}" rx="{GR * 0.2:.0f}" ry="{GR * 0.09:.0f}" fill="#e9c46a"/>')
G.append(f'<ellipse id="amazonas" cx="{gp(395, 560)[0]:.0f}" cy="{gp(395, 560)[1]:.0f}" rx="{GR * 0.12:.0f}" ry="{GR * 0.08:.0f}" fill="#2f7d32"/>')
G.append(f'<rect id="ecuadorB" x="{GX - GR}" y="{GY - GR * 0.16}" width="{2 * GR}" height="{GR * 0.32}" fill="#ff5a3c" opacity="0"/>')
G.append(f'<rect id="poloN" x="{GX - GR}" y="{GY - GR}" width="{2 * GR}" height="{GR * 0.32}" fill="#e8f6ff" opacity="0"/><rect id="poloS" x="{GX - GR}" y="{GY + GR * 0.68}" width="{2 * GR}" height="{GR * 0.32}" fill="#e8f6ff" opacity="0"/>')
G.append(f'<g id="lluviaMar" opacity="0">' + "".join(f'<g transform="translate({gp(x, y)[0]:.0f},{gp(x, y)[1]:.0f})"><ellipse rx="26" ry="12" fill="#ffffff"/><path d="M-10,12 l-4,14 M2,12 l-4,14 M14,12 l-4,14" stroke="#cfe8ff" stroke-width="3"/></g>' for x, y in ((450, 300), (470, 640), (820, 600), (260, 560), (560, 820))) + '</g>')
G.append(f'<path id="polvo" d="M{gp(640, 395)[0]:.0f},{gp(640, 395)[1]:.0f} Q{gp(530, 330)[0]:.0f},{gp(530, 330)[1]:.0f} {gp(410, 545)[0]:.0f},{gp(410, 545)[1]:.0f}" stroke="#e9c46a" stroke-width="16" stroke-dasharray="2 22" stroke-linecap="round" fill="none" opacity="0"/>')
G.append('<g id="peces" opacity="0">' + "".join(f'<path transform="translate({gp(x, y)[0]:.0f},{gp(x, y)[1]:.0f})" d="M-14,0 Q0,-9 12,0 Q0,9 -14,0 Z M12,0 l8,-6 l0,12 Z" fill="#ffd23f"/>' for x, y in ((300, 640), (290, 680), (310, 720), (280, 600))) + '</g>')
G.append('</g>')
G.append(f'<g id="huracanes">' + "".join(f'<g class="hur" transform="translate({gp(x, y)[0]:.0f},{gp(x, y)[1]:.0f})"><g class="hurR"><path d="M0,0 m-34,0 a34,34 0 1 1 34,34 M0,0 m34,0 a34,34 0 1 1 -34,-34" stroke="#ffffff" stroke-width="9" fill="none" stroke-linecap="round"/><circle r="7" fill="#ffffff"/></g></g>' for x, y in ((440, 380), (210, 370), (860, 320))) + '</g>')
G.append(f'<g id="albatros"><path d="M-26,0 q13,-12 26,0 q13,-12 26,0" stroke="#ffffff" stroke-width="5" fill="none"/></g>')
G.append('<g id="celdas" opacity="0">' + "".join(f'<path d="{gpath(d)}" stroke="#ffffff" stroke-width="7" fill="none" stroke-dasharray="26 18" class="celda" marker-end="url(#flecha)"/>' for d in (
    "M120,420 Q300,300 500,330", "M880,420 Q700,300 500,330", "M120,600 Q300,700 500,670", "M880,600 Q700,700 500,670", "M200,250 Q350,150 520,180", "M800,780 Q650,880 480,820")) + '</g>')
G.append('</g>')
M.extend(G)
WORLD = "".join(M)
DEFS = ['<linearGradient id="mar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3f9fd0"/><stop offset="1" stop-color="#14507d"/></linearGradient>',
        '<linearGradient id="smogG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b7a98c" stop-opacity="0.2"/><stop offset="0.5" stop-color="#9c8f74" stop-opacity="0.85"/><stop offset="1" stop-color="#8a7f68" stop-opacity="0.95"/></linearGradient>',
        '<marker id="flecha" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#ffffff"/></marker>']

# ------------------------------------------------------------------ helpers
def cam(t, d=1.4, ease="power2.inOut", **kv):
    J(f'tl.to(S, {{{", ".join(f"{k}:{v}" for k, v in kv.items())}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
def st(t, d=0.8, ease="power2.inOut", **kv):
    cam(t, d, ease, **kv)
NC = [0]
def card(html, t, hasta, top=640, left=40, w=380, cls=""):
    NC[0] += 1; i = NC[0]
    FXL.append(f'<div class="card {cls}" id="c{i}" style="top:{top}px;left:{left}px;width:{w}px">{html}</div>')
    J(f'tl.set("#c{i}", {{opacity:0}}, 0); tl.fromTo("#c{i}", {{opacity:0, y:24}}, {{opacity:1, y:0, duration:0.45, ease:"power3.out", immediateRender:false}}, {t:.2f}); tl.to("#c{i}", {{opacity:0, y:-16, duration:0.3}}, {hasta:.2f});')
def contador(sel, v0, v1, t, d, dec=0, suf=""):
    J(f'(() => {{ const o = {{v:{v0}}}; tl.to(o, {{v:{v1}, duration:{d:.2f}, ease:"power2.out", onUpdate:() => {{ document.querySelector("{sel}").textContent = fmt(o.v, {dec}) + "{suf}"; }}}}, {t:.2f}); }})();')
NL = [0]
def etiqueta(p, t, hasta, txt, dx=20, dy=-40):
    NL[0] += 1; i = NL[0]
    FXL.append(f'<div class="lab" id="lb{i}">{txt}</div>')
    J(f'LABS.push({{i:{i}, x:{p[0]:.1f}, y:{p[1]:.1f}, dx:{dx}, dy:{dy}}}); LV.l{i} = 0;')
    J(f'tl.to(LV, {{l{i}:1, duration:0.4}}, {t:.2f}); tl.to(LV, {{l{i}:0, duration:0.3}}, {hasta:.2f});')

# ------------------------------------------------------------------ GUION VISUAL (un solo plano)
rset(J, "P", "cometa")
# medidor de viento (gancho desde el fotograma 0; vuelve igual al final)
FXL.append('<div id="gauge" class="grande"><b><span id="kmh">20</span> km/h</b><small id="gtxt">VIENTO</small></div>')
PARA = P("desapareciera") - 0.1
st(PARA, 1.6, "power2.out", v=0)
contador("#kmh", 20, 0, PARA, 1.4)
J(f'tl.to("#gauge b", {{color:"#ff6b5e", duration:0.4}}, {PARA + 0.8:.2f}); tl.to("#gauge", {{opacity:0, y:20, duration:0.4}}, {FE(1) + 1.4:.2f});')
rpose(J, "P", "mira", PARA + 0.6, 0.8)
# 2) el día perfecto… y lo que viene
card('<small>EN UNAS SEMANAS</small><b>falta comida</b>', P("comida") - 0.4, FE(2) + 0.2, top=600)
card('<small>EN MEDIO PLANETA</small><b>no llueve</b>', P("llover") - 0.4, FE(2) + 0.2, top=800)
J(f'tl.to("#brillo", {{opacity:0.6, duration:1.0}}, {F(2):.2f});')
# 3) el mar: espejo, velero parado, surfista sentado
cam(F(3) - 0.3, 1.6, cx=X_MAR, cy=-240, z=1.4)
card('<small>LAS OLAS</small><b>las crea el viento</b><em>casi todas</em>', P("olas") - 0.2, FE(3) + 0.2)
etiqueta((X_MAR - 280, -180), P("veleros") - 0.3, FE(3) + 0.2, "velero sin viento", dx=-80, dy=-60)
# 4) molinos parados
cam(F(4) - 0.4, 1.8, cx=X_MOL, cy=-330, z=1.3)
card('<small>ENERGÍA EÓLICA</small><b>8 %</b><em>de la electricidad del mundo</em>', P("ocho") - 0.3, FE(4) + 0.2)
# 5) ciudad: niebla tóxica (Londres 1952)
cam(F(5) - 0.4, 1.8, cx=X_CIU, cy=-360, z=1.3)
J(f'tl.to("#smog", {{opacity:1, duration:3.2, ease:"power1.in"}}, {F(5) + 0.4:.2f});')
card('<small>LONDRES · 1952</small><b>5 días sin viento</b><em>miles de muertos por la niebla tóxica</em>', P("1952") - 0.3, FE(5) + 0.2)
J(f'tl.to("#smog", {{opacity:0.25, duration:1.2}}, {FE(5) + 0.4:.2f});')
# 6) maíz: el polen cae recto
cam(F(6) - 0.4, 1.8, cx=X_MAIZ, cy=-190, z=2.0)
card('<small>MAÍZ</small><b>el cereal nº 1</b><em>su polen viaja con el viento</em>', P("maiz") - 0.3, P("sin", 2) - 0.3)
card('<small>SIN VIENTO</small><b class="r">sin cosecha</b>', P("cosecha") - 0.4, FE(6) + 0.2)
J(f'tl.to(S, {{pol:1, duration:0.6}}, {F(6) + 0.6:.2f}); tl.to(S, {{pol:0, duration:0.6}}, {FE(6) + 0.6:.2f});')
# 7) Biosfera 2: el árbol se cae solo
cam(F(7) - 0.4, 1.8, cx=X_BIO, cy=-250, z=1.6)
card('<small>BIOSFERA 2 · ARIZONA</small><b>árboles sin viento</b><em>crecían débiles</em>', P("biosfera") - 0.3, FE(7) + 0.2)
J(f'tl.to("#arbolR", {{rotation:78, svgOrigin:"0 0", duration:1.3, ease:"power2.in"}}, {P("cayendose") - 0.5:.2f});')
# 8-9) sequía tierra adentro
cam(F(8) - 0.4, 1.8, cx=X_SECO, cy=-260, z=1.5)
J(f'tl.to("#seco", {{opacity:1, duration:6, ease:"power1.inOut"}}, {F(8) + 0.5:.2f}); tl.to("#grietas", {{opacity:1, duration:3}}, {F(9):.2f}); tl.to(".seco2", {{opacity:1, duration:4}}, {F(9) - 1:.2f}); tl.to(".hoja", {{opacity:0, duration:4}}, {F(9) - 1:.2f}); tl.to("#charca", {{attr:{{rx:20}}, opacity:0, duration:5}}, {F(8) + 1:.2f});')
card('<small>EL VIENTO</small><b>trae las nubes</b><em>del mar a la tierra</em>', P("nubes") - 0.4, P("sin") if False else FE(8) + 0.2)
card('<small>SIN ÉL</small><b>tierra seca</b><em>solo llueve sobre el mar</em>', F(9) + 0.2, FE(9) + 0.2)
# 10) subida al espacio: el planeta
SUBE = F(10) - 0.6
cam(SUBE, 2.6, "power2.inOut", cx=GX, cy=GY, z=1)
J(f'tl.to("#espacio", {{opacity:1, duration:2.2}}, {SUBE + 0.4:.2f}); tl.to("#planeta", {{opacity:1, duration:1.2}}, {SUBE + 1.2:.2f}); tl.to("#nubes", {{opacity:0, duration:1}}, {SUBE:.2f});')
J(f'tl.to("#ecuadorB", {{opacity:0.55, duration:1.2}}, {P("ecuador") - 0.3:.2f}); tl.to(["#poloN", "#poloS"], {{opacity:0.9, duration:1.2}}, {P("polos") - 0.3:.2f});')
etiqueta((GX + GR * 0.7, GY), P("ecuador") - 0.2, FE(10) + 0.2, "ecuador: más calor", dx=-150, dy=-20)
etiqueta((GX - GR * 0.4, GY - GR * 0.9), P("polos") - 0.2, FE(10) + 0.2, "polos: más frío", dx=-40, dy=-60)
J(f'tl.to(["#ecuadorB", "#poloN", "#poloS"], {{opacity:0.15, duration:0.8}}, {FE(10) + 0.2:.2f});')
J(f'tl.to(".tierra", {{fill:"#b99a5f", duration:3}}, {F(10):.2f}); tl.to("#lluviaMar", {{opacity:1, duration:1}}, {F(10):.2f});')
# 11) polvo del Sáhara → Amazonas (y se corta)
J(f'tl.to("#polvo", {{opacity:1, duration:0.5}}, {P("amazonas") - 0.2:.2f}); tl.fromTo("#polvo", {{strokeDashoffset:0}}, {{strokeDashoffset:-240, duration:3, ease:"none", immediateRender:false}}, {P("amazonas"):.2f});')
J(f'tl.to("#polvo", {{opacity:0, duration:1.2}}, {FE(11) - 0.4:.2f}); tl.to("#amazonas", {{fill:"#7d9a4a", duration:1.5}}, {FE(11) - 0.6:.2f});')
etiqueta((gp(560, 360)[0], gp(560, 360)[1]), P("veintisiete") - 0.3, FE(11) + 0.2, "Sáhara → Amazonas", dx=-60, dy=-70)
card('<small>CADA AÑO</small><b>27 millones de t</b><em>de polvo que abona el Amazonas</em>', P("veintisiete") - 0.3, FE(11) + 0.2, top=1420, left=150, w=780, cls="centro")
# 12) pesca
J(f'tl.to("#peces", {{opacity:1, duration:0.6}}, {F(12) + 0.3:.2f}); tl.to("#peces", {{opacity:0.15, duration:1.5}}, {P("nutrientes"):.2f});')
etiqueta((gp(300, 660)[0], gp(300, 660)[1]), P("nutrientes") - 0.4, FE(12) + 0.2, "costa de Perú", dx=-200, dy=-30)
card('<small>ZONAS DE AFLORAMIENTO</small><b>1 de cada 5</b><em>peces que se pescan en el mundo</em>', P("quinta") - 0.4, FE(12) + 0.2, top=1420, left=150, w=780, cls="centro")
# 13) albatros (vuela alrededor del planeta y cae)
J(f'tl.to(S, {{alb:1, duration:0.5}}, {F(13):.2f}); tl.to(S, {{albA:1, duration:3.2, ease:"none"}}, {F(13):.2f}); tl.to(S, {{albCae:1, duration:1.4, ease:"power2.in"}}, {P("volar") - 1.0:.2f}); tl.to(S, {{alb:0, duration:0.4}}, {FE(13) + 0.1:.2f});')
card('<small>EL ALBATROS</small><b>46 días</b><em>para dar la vuelta al mundo</em>', P("albatros") - 0.2, FE(13) + 0.2, top=1420, left=150, w=780, cls="centro")
# 14) huracanes: desaparecen
J(f'tl.set(".hur", {{opacity:0}}, 0); tl.fromTo(".hur", {{opacity:0, scale:0.4}}, {{opacity:1, scale:1, svgOrigin:"0 0", duration:0.6, stagger:0.15, immediateRender:false}}, {F(14) - 0.2:.2f}); tl.to(".hur", {{opacity:0, scale:0.2, svgOrigin:"0 0", duration:0.8, stagger:0.25}}, {P("huracan") - 0.2:.2f});')
card('<small>LO ÚNICO BUENO</small><b>0 huracanes</b>', P("bueno") - 0.2, FE(14) + 0.3, top=1420, left=240, w=600, cls="centro")
# 15) es imposible: el Sol calienta desigual → el aire vuelve a moverse
J(f'tl.to("#solG", {{opacity:1, duration:0.8}}, {P("sol") - 0.4:.2f}); tl.to("#celdas", {{opacity:1, duration:0.8}}, {P("aire") - 0.6:.2f}); tl.to("#solG", {{opacity:0, duration:0.8}}, {FE(15) + 0.3:.2f});')
J(f'tl.to(".tierra", {{fill:"#5aa752", duration:2}}, {P("aire") - 0.4:.2f}); tl.to("#amazonas", {{fill:"#2f7d32", duration:2}}, {P("aire") - 0.4:.2f}); tl.to("#lluviaMar", {{opacity:0, duration:1}}, {P("aire"):.2f});')
st(P("movera") - 0.6, 1.6, "power1.inOut", v=1)
# 16) vuelta a la playa con viento (mismo encuadre que el fotograma 0)
BAJA = F(16) - 0.4
cam(BAJA, 2.4, "power2.inOut", cx=X_PLAYA + 40, cy=-128, z=1.8)
J(f'tl.to("#espacio", {{opacity:0, duration:1.6}}, {BAJA + 0.2:.2f}); tl.to("#planeta", {{opacity:0, duration:1.2}}, {BAJA:.2f}); tl.to("#nubes", {{opacity:1, duration:1.5}}, {BAJA + 1.2:.2f}); tl.to("#celdas", {{opacity:0, duration:0.5}}, {BAJA:.2f});')
J(f'tl.set("#seco", {{opacity:0}}, {BAJA + 1:.2f}); tl.set(["#grietas", ".seco2"], {{opacity:0}}, {BAJA + 1:.2f}); tl.set(".hoja", {{opacity:1}}, {BAJA + 1:.2f}); tl.set("#charca", {{attr:{{rx:190}}, opacity:1}}, {BAJA + 1:.2f}); tl.set("#smog", {{opacity:0}}, {BAJA + 1:.2f}); tl.set("#arbolR", {{rotation:0, svgOrigin:"0 0"}}, {BAJA + 1:.2f}); tl.set(["#ecuadorB", "#poloN", "#poloS"], {{opacity:0}}, {BAJA + 1:.2f}); tl.set("#peces", {{opacity:0}}, {BAJA + 1:.2f}); tl.set("#brillo", {{opacity:0}}, {BAJA + 1:.2f});')
rpose(J, "P", "cometa", P("despeine") - 0.6, 1.0)
J(f'tl.set("#gauge b", {{color:"#ffffff"}}, {BAJA:.2f}); tl.fromTo("#gauge", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.5, immediateRender:false}}, {DUR - 2.6:.2f});')
contador("#kmh", 0, 20, DUR - 2.6, 1.4)
card('<small>EL VIENTO TRAE</small><b>lluvia, comida y aire limpio</b>', P("lluvia") - 0.4, DUR - 2.7, top=620, w=420)

# ------------------------------------------------------------------ capa de pantalla
NUB = [(60, 560, 0.9), (620, 640, 0.7), (850, 500, 1.15), (300, 820, 0.6)]
NUBES = "".join(f'<div class="nube" id="nb{k}" style="left:{x}px;top:{y}px;transform:scale({sc})"><i></i><i></i><i></i></div>' for k, (x, y, sc) in enumerate(NUB))
ESTR = "".join(f'<i style="left:{rr.randint(10, 1070)}px;top:{rr.randint(10, 1900)}px;width:{rr.choice([2, 3, 4])}px;height:{rr.choice([2, 3, 4])}px;opacity:{rr.uniform(0.4, 1):.2f}"></i>' for _ in range(140))

_S = open(os.path.join(BASE, "_subs.py"), encoding="utf-8").read()
exec(re.sub(r"CLAVE = set\(.*?\]\)", lambda m: 'CLAVE = set(norm(w) for w in ["viento", "perfecto", "comida", "llover", "olas", "espejo", "veleros", "ocho", "1952", "londres", "miles", "maiz", "polen", "cosecha", "arboles", "biosfera", "cayendose", "sequia", "nubes", "oceano", "secando", "ecuador", "polos", "amazonas", "veintisiete", "sahara", "nutrientes", "quinta", "albatros", "cuarenta", "volar", "huracan", "imposible", "sol", "aire", "despeine", "lluvia", "limpio"])', _S, count=1, flags=re.S))
html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#74b6e6}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;color:#fff;background:linear-gradient(180deg,#3f8fd2 0%,#74b6e6 40%,#b9dcf3 75%,#dff0fa 100%)}}
#espacio{{position:absolute;inset:0;opacity:0;background:radial-gradient(ellipse at 50% 55%,#13234a 0%,#070b1a 70%)}} #espacio i{{position:absolute;border-radius:50%;background:#fff}}
#sol{{position:absolute;left:820px;top:330px;width:150px;height:150px;border-radius:50%;background:radial-gradient(circle,#fff7d6 0%,#ffe48a 55%,rgba(255,228,138,0) 72%)}}
#solG{{position:absolute;left:-260px;top:620px;width:520px;height:520px;border-radius:50%;opacity:0;background:radial-gradient(circle,#fff7d6 0%,#ffd75e 35%,rgba(255,200,80,0.35) 55%,rgba(255,200,80,0) 72%)}}
#nubes{{position:absolute;inset:0;pointer-events:none}} .nube{{position:absolute;width:260px;height:80px;transform-origin:center}}
.nube i{{position:absolute;bottom:0;border-radius:50%;background:#ffffff;opacity:0.92}} .nube i:nth-child(1){{left:0;width:130px;height:60px}} .nube i:nth-child(2){{left:60px;width:130px;height:90px}} .nube i:nth-child(3){{left:130px;width:120px;height:62px}}
svg#esc{{position:absolute;left:0;top:0}}
#fxl{{position:absolute;inset:0;z-index:58;pointer-events:none}}
.card{{position:absolute;padding:18px 24px 20px;border-radius:22px;background:rgba(14,30,52,0.82);opacity:0}}
.card small{{display:block;font:700 18px Inter;letter-spacing:4px;color:#8cc4ff;margin-bottom:6px}} .card b{{display:block;font:300 56px/1.08 Inter;letter-spacing:-1.5px}}
.card em{{display:block;font-style:normal;font:500 26px/1.3 Inter;color:rgba(255,255,255,0.8);margin-top:6px}} .card .r{{color:#ff6b5e}} .card.centro{{text-align:center}}
.grande{{position:absolute;left:0;right:0;top:1430px;text-align:center}} .grande b{{display:inline-block;padding:16px 44px 10px;border-radius:28px 28px 0 0;background:rgba(14,30,52,0.84);font:300 120px/1 Inter;letter-spacing:-4px}}
.grande small{{display:block;width:max-content;margin:0 auto;padding:4px 34px 16px;border-radius:0 0 22px 22px;background:rgba(14,30,52,0.84);font:700 24px Inter;letter-spacing:8px;color:#8cc4ff}}
.lab{{position:absolute;left:0;top:0;padding:8px 16px;border-radius:12px;background:rgba(14,30,52,0.82);font:700 26px Inter;white-space:nowrap;opacity:0}}
#grano{{position:absolute;inset:0;z-index:56;pointer-events:none;opacity:0.03;background:url(assets/grano.png);mix-blend-mode:overlay}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:520px;z-index:55;pointer-events:none;background:linear-gradient(rgba(16,52,92,0.55),rgba(16,52,92,0))}}
#marca{{position:absolute;left:0;right:0;top:1820px;text-align:center;font:600 26px Inter;color:#ffffff;opacity:0.5;pointer-events:none;z-index:61}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 58px Inter;color:rgba(255,255,255,0.62);line-height:1.22;text-shadow:0 3px 14px rgba(8,30,60,0.75)}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:3px solid #4ea3ff;border-radius:6px;background:rgba(78,163,255,0.18);opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="espacio">{ESTR}</div>
  <div id="sol"></div><div id="solG"></div>
  <div id="nubes">{NUBES}</div>
  <svg id="esc" width="1080" height="1920" viewBox="0 0 1080 1920"><defs>{"".join(DEFS)}</defs><g id="world">{WORLD}</g></svg>
  <div id="topsombra"></div><div id="grano"></div>
  <div id="fxl">{"".join(FXL)}</div>
  <div id="marca">@mundo.supuesto</div>
  <div id="subs" data-layout-allow-overlap>{"".join(SUBS)}</div>
  <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
</div>
<script>
const fmt = (v, d) => {{ const s = v.toFixed(d).split("."); return s[0].replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ".") + (s[1] ? "," + s[1] : ""); }};
const S = {{ t:0, v:1, cx:{X_PLAYA + 40}, cy:-128, z:1.8, pol:0, alb:0, albA:0, albCae:0 }};
const W = document.getElementById("world");
const $ = (id) => document.getElementById(id);
const LABS = [], LV = {{}};
const POL = [...document.querySelectorAll(".pol")], GAV = [...document.querySelectorAll(".gav")], MECH = [...document.querySelectorAll(".mecha")], ASP = [...document.querySelectorAll(".aspas")], CO = [...document.querySelectorAll(".coche")], HR = [...document.querySelectorAll(".hurR")];
const NB = [0, 1, 2, 3].map(k => $("nb" + k));
let ang = 0;
function frame() {{
  const t = S.t, v = S.v;
  W.setAttribute("transform", `translate(540,1150) scale(${{S.z}}) translate(${{-S.cx}},${{-S.cy}})`);
  // olas
  let d = "M-3200,2000 L-3200,0", e = "";
  for (let x = -3200; x <= -150; x += 40) {{ const y = -Math.abs(Math.sin(x / 90 - t * 2.4)) * 22 * v - Math.sin(x / 37 + t) * 1.5; d += ` L${{x}},${{y.toFixed(1)}}`; if (v > 0.3 && (x / 40) % 6 === 0) e += `M${{x - 14}},${{(y - 2).toFixed(1)}} q14,-8 28,0 `; }}
  d += " L-150,2000 Z"; $("olas").setAttribute("d", d); $("espuma").setAttribute("d", e); $("espuma").style.opacity = v;
  // velero
  const by = Math.sin(t * 1.7) * 5 * v; $("velero").setAttribute("transform", `translate(${{-900 + 30 * Math.sin(t * 0.3) * v}},${{by - 6}}) rotate(${{3 * v * Math.sin(t * 1.3)}})`);
  const bulge = 10 + 46 * v; $("vela").setAttribute("d", `M3,-165 Q${{3 + bulge}},-90 3,-14 L70,-14 Q${{55 + bulge * 0.3}},-90 3,-165 Z`);
  // surfista: de pie sobre la ola con viento; sentado sin él
  $("surf").setAttribute("transform", `translate(-380,${{(-18 * v * Math.abs(Math.sin(-380 / 90 - t * 2.4)) - 4).toFixed(1)}})`);
  $("surfista").setAttribute("transform", `translate(0,${{(1 - v) * 30}}) scale(1,${{(0.6 + 0.4 * v).toFixed(2)}})`);
  // bandera
  let tp = "", bt = "";
  for (let i = 0; i <= 10; i++) {{ const u = i / 10;
    const wx = u * 130, wy = Math.sin(u * 5 - t * 9) * 10 * u;
    const hx = 6 + Math.sin(u * 3 + t) * 2, hy = u * 120;
    const x = wx * v + hx * (1 - v), y = wy * v + hy * (1 - v);
    tp += (i ? " L" : "M") + (x).toFixed(1) + "," + (-255 + y).toFixed(1);
    bt = ` L${{(x + (1 - v) * 0).toFixed(1)}},${{(-255 + y + 80 * v + 6 * (1 - v)).toFixed(1)}}` + bt; }}
  $("tela").setAttribute("d", tp + bt.replace(/^ L/, " L") + " Z");
  // palmera
  $("palma").setAttribute("transform", `translate(18,-330) rotate(${{(10 * v + 4 * v * Math.sin(t * 2)).toFixed(1)}})`);
  // cometa y hilo
  const hx0 = {X_PLAYA} + 46, hy0 = -228;
  const kx = hx0 + 220 * v + 120 * (1 - v), ky = (-410 + 14 * Math.sin(t * 1.9)) * v + (-20) * (1 - v);
  $("cometa").setAttribute("transform", `translate(${{kx.toFixed(1)}},${{ky.toFixed(1)}}) rotate(${{(20 * v + Math.sin(t * 2.3) * 8 * v + 80 * (1 - v)).toFixed(1)}})`);
  $("hilo").setAttribute("d", `M${{hx0}},${{hy0}} Q${{(hx0 + kx) / 2 + 30 * v}},${{((hy0 + ky) / 2 + 60 + 120 * (1 - v)).toFixed(1)}} ${{kx.toFixed(1)}},${{ky.toFixed(1)}}`);
  let c = "M0,46"; for (let i = 1; i <= 6; i++) c += ` L${{(Math.sin(i * 1.2 - t * 6) * 10 * v).toFixed(1)}},${{46 + i * 18}}`; $("cola").setAttribute("d", c);
  // pelo
  MECH.forEach((m, k) => {{ const a = v * (10 + 14 * Math.sin(t * 11 + k)); m.setAttribute("transform", m.getAttribute("transform").replace(/ rotate\\([^)]*\\)/, "") + ` rotate(${{a.toFixed(1)}})`); m.style.opacity = Math.max(0, v * 1.4 - 0.4).toFixed(2); }});
  // gaviotas
  GAV.forEach((g, k) => {{ const x = {X_PLAYA} - 200 + k * 150 + 30 * Math.sin(t * 0.5 + k) * v, y = (-330 - k * 40 + 20 * Math.sin(t + k)) * v + (-4) * (1 - v);
    g.setAttribute("transform", `translate(${{x.toFixed(1)}},${{y.toFixed(1)}}) scale(1,${{(1 - 0.6 * (1 - v)).toFixed(2)}})`); }});
  // molinos (ángulo integrado con el viento) y coches
  ASP.forEach((a, k) => a.setAttribute("transform", `rotate(${{(S.ang + k * 40).toFixed(1)}})`));
  CO.forEach((g, k) => {{ const x = 2950 + ((t * 90 + k * 560) % 1650); g.setAttribute("transform", `translate(${{x.toFixed(1)}},8)`); }});
  // polen: con viento viaja; sin viento cae recto
  POL.forEach((p, k) => {{ const x0 = 4800 + (k % 22) * 64, h = 200 + ((k % 22) * 37) % 50, ph = ((t * 0.6 + k * 0.137) % 1);
    p.setAttribute("cx", (x0 + 6 * Math.sin(k)).toFixed(1)); p.setAttribute("cy", (-h - 30 + ph * (h + 30)).toFixed(1)); p.setAttribute("opacity", (S.pol * (1 - ph)).toFixed(2)); }});
  // albatros alrededor del planeta
  const aa = S.albA * Math.PI * 2.2 - 0.6, rA = {GR} + 70 - S.albCae * 60;
  $("albatros").setAttribute("transform", `translate(${{({GX} + Math.cos(aa) * rA).toFixed(1)}},${{({GY} + Math.sin(aa) * rA * 0.35 + {GR} * 0.62 + S.albCae * 140).toFixed(1)}}) rotate(${{(S.albCae * 70).toFixed(1)}})`);
  $("albatros").style.opacity = S.alb;
  HR.forEach((h, k) => h.setAttribute("transform", `rotate(${{(-t * 90 + k * 50).toFixed(1)}})`));
  // nubes de pantalla: se mueven con el viento
  NB.forEach((n, k) => {{ n.style.transform = `translateX(${{(S.nx * (0.6 + k * 0.2)).toFixed(1)}}px) scale(${{[0.9, 0.7, 1.15, 0.6][k]}})`; }});
  for (const L of LABS) {{ const el = $("lb" + L.i); const o = LV["l" + L.i] || 0; el.style.opacity = o;
    if (o > 0.01) {{ const x = 540 + (L.x - S.cx) * S.z, y = 1150 + (L.y - S.cy) * S.z; const xx = Math.max(20, Math.min(x + L.dx, 1060 - el.offsetWidth)); el.style.transform = `translate(${{xx}}px, ${{y + L.dy}}px)`; }} }}
}}
S.ang = 0; S.nx = 0;
const tl = gsap.timeline({{ paused: true, onUpdate: frame }});
tl.to(S, {{t:{DUR:.2f}, duration:{DUR:.2f}, ease:"none"}}, 0);
tl.to(S, {{ang:150, nx:50, duration:{P("desapareciera") + 1.5:.2f}, ease:"power1.out"}}, 0);
tl.fromTo(S, {{ang:-210, nx:-50}}, {{ang:0, nx:0, duration:{DUR - (P("movera") - 0.6):.2f}, ease:"power1.in", immediateRender:false}}, {P("movera") - 0.6:.2f});
{chr(10).join(tl)}
tl.to({{}}, {{duration:0.01}}, {DUR - 0.01});
window.__timelines["main"] = tl;
tl.seek(0); frame();
</script>
</body></html>"""
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump([], open(os.path.join(BASE, "efectos.json"), "w"))
json.dump([[0, 0.0], [DUR, 0.0]], open(os.path.join(BASE, "ambiente.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones")

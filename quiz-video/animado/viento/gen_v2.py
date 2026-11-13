#!/usr/bin/env python3
"""«¿Qué pasaría si el viento desapareciera?» v2 — UN SOLO PLANO, ilustración cuidada con profundidad:
playa con viento (estelas de aire, cometa, bandera, oleaje) → calma total (mar espejo con reflejo) → viaje tierra adentro
(molinos en capas, ciudad con niebla tóxica, maizal, cúpula geodésica de Biosfera 2, tierra agrietada) → planeta real
(continentes Natural Earth, atmósfera, calor, polvo del Sáhara, afloramiento de Perú, albatros, huracanes) → vuelta a la
playa con viento (bucle). Misma locución que la v1 (tiempos.json). Sin efectos de sonido.
  python3 gen.py → index.html + efectos.json + ambiente.json"""
import json, math, os, random, re, unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(BASE, "tiempos.json"), encoding="utf-8"))
GEO = json.load(open(os.path.join(BASE, "_globo.json"), encoding="utf-8"))
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

X_PLAYA, X_MAR, X_MOL, X_CIU, X_MAIZ, X_BIO, X_SECO = 120, -640, 1900, 3700, 5500, 7300, 9100
GX, GY, GR = 9100, -6200, 420
M = []
# ================================================================== FONDO CON PARALLAX (montañas y bruma)
L = ['<g id="lejos">']
for k, (x0, w, hh, col) in enumerate(((420, 2600, 300, "#c7dbea"), (2600, 3000, 380, "#cfe1ee"), (5200, 3000, 340, "#c7dbea"), (7600, 3600, 380, "#cfe1ee"))):
    L.append(f'<path d="M{x0},0 C{x0 + w * 0.2},{-hh * 0.7} {x0 + w * 0.3},{-hh} {x0 + w * 0.45},{-hh * 0.95} C{x0 + w * 0.6},{-hh * 0.9} {x0 + w * 0.7},{-hh * 0.55} {x0 + w * 0.8},{-hh * 0.6} C{x0 + w * 0.9},{-hh * 0.62} {x0 + w * 0.95},{-hh * 0.2} {x0 + w},0 Z" fill="{col}"/>')
for k in range(10):
    x0 = 600 + k * 1000
    L.append(f'<path d="M{x0},0 Q{x0 + 300},{-260 - (k * 53) % 120} {x0 + 620},{-120 - (k * 31) % 60} Q{x0 + 820},{-200} {x0 + 1100},0 Z" fill="#a9c9b4"/>')
L.append('<rect x="-4000" y="-420" width="18000" height="430" fill="url(#bruma)"/>')
L.append('</g>')
M.extend(L)
# ================================================================== MAR Y PLAYA
M.append('<path d="M-700,140 Q-380,40 -150,6 L-150,400 L-700,400 Z" fill="#e8d29c"/>')                       # arena bajo el agua
M.append('<rect x="-3600" y="-2" width="3450" height="2200" fill="url(#mar)"/>')
M.append('<rect x="-560" y="-2" width="410" height="220" fill="url(#orilla)"/>')
M.append('<path id="olas" d="" fill="url(#ola)"/><path id="espuma" d="" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" opacity="0.9"/>')
M.append('<g id="destellos">' + "".join(f'<rect class="dst" x="{-3000 + k * 47 + (k * 29) % 31}" y="{10 + (k * 37) % 140}" width="{18 + (k % 4) * 8}" height="3" rx="1.5" fill="#ffffff"/>' for k in range(60)) + '</g>')
VEL = ('<path d="M-80,0 L80,0 L60,26 L-60,26 Z" fill="#ffffff"/><path d="M-80,0 L80,0 L76,6 L-76,6 Z" fill="#d8e2ea"/><rect x="-3" y="-190" width="6" height="192" fill="#6b5442"/>'
       '<path class="vela" d="" fill="#fbf6ea" stroke="#e6dcc6" stroke-width="2"/><path d="M-5,-172 L-66,-12 L-5,-12 Z" fill="#f2b84b"/>')
M.append(f'<g id="velero"><g id="veleroRef" opacity="0" transform="scale(1,-1) translate(0,-52)">{VEL}</g>{VEL}</g>')
M.append('<g id="surf"><path d="M-70,0 Q0,-12 70,0 Q0,8 -70,0 Z" fill="#ff7a59"/><g id="surfista"><circle cx="0" cy="-92" r="13" fill="#c98e6b"/><path d="M-12,-100 Q0,-112 12,-100 L12,-96 L-12,-96 Z" fill="#2a1a14"/>'
         '<path d="M-9,-78 L9,-78 L11,-38 L-11,-38 Z" fill="#1f6fb2"/><path d="M-10,-38 L-22,-2 M10,-38 L20,-2" stroke="#1d3557" stroke-width="9" stroke-linecap="round"/>'
         '<path d="M-8,-72 L-34,-56 M8,-72 L34,-56" stroke="#c98e6b" stroke-width="7" stroke-linecap="round"/></g></g>')
M.append('<path d="M-290,70 Q-210,10 -150,4 Q200,-14 1000,-6 L1000,2200 L-290,2200 Z" fill="url(#arena)"/><path id="mojada" d="" fill="#d4b97e" opacity="0.35"/>')
for k in range(60):
    x = -120 + k * 18 + (k * 7) % 11; M.append(f'<circle cx="{x}" cy="{12 + (k * 13) % 90}" r="{1.6 + (k % 3) * 0.6}" fill="#cdb071" opacity="0.7"/>')
M.append('<g transform="translate(-40,-2)"><ellipse cx="10" cy="4" rx="80" ry="8" fill="#000" opacity="0.12"/><rect x="-46" y="-6" width="110" height="8" rx="4" fill="#4ea3ff"/><rect x="-46" y="-6" width="110" height="3" fill="#ffffff" opacity="0.5"/>'
         '<rect x="-2" y="-170" width="5" height="168" fill="#f4f4f4"/><path d="M-96,-160 Q0,-226 96,-160 Z" fill="#ef5b3b"/><path d="M-32,-160 Q0,-222 32,-160 Z" fill="#fff"/><path d="M-96,-160 Q0,-150 96,-160" stroke="#c94a2e" stroke-width="3" fill="none"/></g>')
M.append('<g transform="translate(480,-8)"><path d="M0,0 Q-14,-180 20,-360" stroke="#7d5236" stroke-width="20" fill="none" stroke-linecap="round"/>'
         + "".join(f'<path d="M{-6 + k * 2},{-40 - k * 40} l14,-6" stroke="#6a4430" stroke-width="3"/>' for k in range(8))
         + '<g id="palma" transform="translate(20,-360)">' + "".join(f'<path d="M0,0 Q{70 * math.cos(a)},{70 * math.sin(a) - 34} {140 * math.cos(a)},{140 * math.sin(a) + 26}" stroke="{c}" stroke-width="18" fill="none" stroke-linecap="round"/>' for a, c in ((-2.9, "#2f7d32"), (-2.2, "#3f8f3a"), (-1.5, "#2f7d32"), (-0.8, "#3f8f3a"), (-0.2, "#2f7d32"), (0.5, "#3f8f3a"))) + '<circle r="10" fill="#6a4430"/></g></g>')
M.append('<g transform="translate(330,-10)"><rect x="-3" y="-300" width="6" height="300" fill="#e6e9ee"/><circle cy="-302" r="6" fill="#c9ced6"/><path id="tela" d="" fill="#ef5b3b"/><path id="telaS" d="" fill="#000" opacity="0.12"/></g>')
M.append('<g id="gaviotas">' + "".join('<g class="gav"><path d="M-24,0 Q-12,-12 0,0 Q12,-12 24,0" stroke="#3a4250" stroke-width="4" fill="none" stroke-linecap="round"/><ellipse cx="0" cy="1" rx="6" ry="3" fill="#ffffff"/></g>' for _ in range(3)) + '</g>')
PROTA = dict(piel="#e8b896", pelo="#3b2a20", camisa="#2f9e8f", pantalon="#33415c", zapato="#f4f4f4")
PR["cometa"] = dict(tor=-90, hd=-100, uaN=-35, faN=-55, uaF=86, faF=80, thN=92, shN=90, thF=88, shF=90)
PR["mira"] = dict(tor=-90, hd=-86, uaN=95, faN=85, uaF=86, faF=80, thN=92, shN=90, thF=88, shF=90)
fig = rig("P", PROTA).replace('cy="84"', 'cy="92"')
MECHAS = '<g id="mechas">' + "".join(f'<path class="mecha" d="M0,0 q7,-8 18,-9" stroke="#3b2a20" stroke-width="5" fill="none" stroke-linecap="round" transform="translate({x},{y})"/>' for x, y in ((-6, -182), (2, -186), (10, -184))) + '</g>'
M.append(f'<g transform="translate({X_PLAYA},-4)"><g transform="translate(0,-92)">{fig}</g>{MECHAS}</g>')
M.append('<path id="hilo" d="" stroke="#ffffff" stroke-width="2" fill="none" opacity="0.9"/><g id="cometa"><path d="M0,-42 L28,0 L0,50 L-28,0 Z" fill="#ffd23f"/><path d="M0,-42 L28,0 L0,0 Z" fill="#ffbe0b"/><path d="M0,0 L0,50 L-28,0 Z" fill="#ffbe0b"/>'
         '<path d="M0,-42 L0,50 M-28,0 L28,0" stroke="#d99a00" stroke-width="2"/><path id="cola" d="" stroke="#ef5b3b" stroke-width="3" fill="none"/></g>')
M.append('<g id="arenaVuela">' + "".join('<circle class="av" r="2.2" fill="#e8d29c"/>' for _ in range(24)) + '</g>')
# ================================================================== CAMPO GENERAL
M.append('<path d="M940,-6 Q3000,-30 6000,-8 Q9000,10 12500,-10 L12500,2200 L940,2200 Z" fill="url(#hierba)"/>')
for k in range(140):
    x = 1000 + k * 82 + (k * 37) % 41
    if 8200 < x < 10200: continue
    M.append(f'<path d="M{x},{2 + (k % 5) * 6} l4,-14 l4,14" fill="#5c9a3e"/>')
# ================================================================== MOLINOS EN CAPAS
M.append('<path d="M900,0 Q1350,-300 1850,-150 Q2350,-340 2900,0 Z" fill="#94c876"/><path d="M900,0 Q1350,-300 1850,-150 Q2350,-340 2900,0" stroke="#7fb862" stroke-width="6" fill="none"/>')
def molino(x, base, h, esc, col="#f6f8fa", lado="#dfe5ea"):
    return (f'<g transform="translate({x},{base}) scale({esc})"><path d="M-12,0 L12,0 L6,{-h} L-6,{-h} Z" fill="{col}"/><path d="M2,0 L12,0 L6,{-h} L2,{-h} Z" fill="{lado}"/>'
            f'<g transform="translate(0,{-h})"><rect x="-10" y="-12" width="44" height="22" rx="10" fill="{col}"/><g class="aspas">'
            + "".join(f'<path d="M0,0 L-8,-14 Q-5,-170 0,-230 Q5,-170 8,-14 Z" fill="{col}" stroke="{lado}" stroke-width="1.5" transform="rotate({a})"/>' for a in (0, 120, 240))
            + f'</g><circle r="12" fill="{lado}"/></g></g>')
for x, base, h, e in ((1200, -250, 600, 0.45), (1450, -280, 600, 0.5), (2550, -290, 600, 0.45), (2750, -200, 600, 0.4)):
    M.append(f'<g opacity="0.75">{molino(x, base, h, e, "#e9eef3", "#d2dae2")}</g>')
for x, base, h, e in ((1560, -170, 640, 0.95), (1960, -140, 640, 1.08), (2380, -210, 640, 0.95)):
    M.append(molino(x, base, h, e))
# ================================================================== CIUDAD (dos capas) + NIEBLA TÓXICA
for k in range(16):
    x = 2850 + k * 115; h = rr.choice([520, 640, 760, 880, 980]); w = rr.choice([96, 110, 124])
    M.append(f'<rect x="{x}" y="{-h}" width="{w}" height="{h}" fill="#b8c7d6" opacity="0.8"/>')
for k in range(12):
    x = 2900 + k * 132; h = rr.choice([360, 460, 560, 680, 820]); w = rr.choice([104, 118, 126]); c = rr.choice(["#f1ece2", "#e6edf3", "#f6e1cf", "#e3ebdd", "#ece4f2"])
    M.append(f'<rect x="{x}" y="{-h}" width="{w}" height="{h}" fill="{c}"/><rect x="{x + w * 0.72}" y="{-h}" width="{w * 0.28}" height="{h}" fill="#000" opacity="0.07"/><rect x="{x - 4}" y="{-h - 10}" width="{w + 8}" height="12" fill="#cfd6de"/>')
    if k % 3 == 0: M.append(f'<rect x="{x + 20}" y="{-h - 46}" width="30" height="36" fill="#9aa5b1"/><path d="M{x + w - 20},{-h - 10} V{-h - 90}" stroke="#7b8794" stroke-width="3"/>')
    for j in range(int(h / 64)):
        for i in range(3):
            M.append(f'<rect class="ven" x="{x + 14 + i * (w - 28) / 3}" y="{-h + 26 + j * 64}" width="{(w - 28) / 3 - 10:.0f}" height="30" fill="{"#ffe8a3" if (j + i + k) % 7 == 0 else "#9fc3dc"}"/>')
M.append('<rect x="2800" y="-8" width="1900" height="46" fill="#596170"/>' + "".join(f'<rect x="{2820 + k * 90}" y="12" width="44" height="5" fill="#f3f3f3"/>' for k in range(21)))
M.append('<g id="coches">' + "".join(f'<g class="coche"><rect x="-44" y="-24" width="88" height="24" rx="9" fill="{c}"/><path d="M-26,-24 L-16,-42 L22,-42 L32,-24 Z" fill="{c}"/><path d="M-20,-26 L-12,-38 L4,-38 L4,-26 Z M8,-26 L8,-38 L20,-38 L27,-26 Z" fill="#bfe4f7"/><circle cx="-26" cy="0" r="9" fill="#222"/><circle cx="26" cy="0" r="9" fill="#222"/></g>' for c in ("#d94f45", "#4ea3ff", "#f2b84b", "#5c6b7a")) + '</g>')
M.append('<g id="smog" opacity="0" filter="url(#difuso)">' + "".join(f'<ellipse cx="{2700 + k * 170}" cy="{-260 - (k * 97) % 380}" rx="{260 + (k * 41) % 140}" ry="{170 + (k * 23) % 90}" fill="#9b8c6f" opacity="0.55"/>' for k in range(14)) + '<rect x="2650" y="-560" width="2200" height="580" fill="#9b8c6f" opacity="0.6"/></g>')
# ================================================================== MAIZAL (tres filas)
def maiz(x, h, esc, tono):
    s = f'<g transform="translate({x},0) scale({esc})"><path d="M0,0 C2,{-h * 0.5} -2,{-h * 0.8} 0,{-h}" stroke="{tono[0]}" stroke-width="7" fill="none"/>'
    for j, (yy, dd) in enumerate(((0.3, -1), (0.48, 1), (0.64, -1), (0.8, 1))):
        s += f'<path d="M0,{-h * yy} C{dd * 30},{-h * yy - 30} {dd * 60},{-h * yy - 10} {dd * 74},{-h * yy + 26}" stroke="{tono[1]}" stroke-width="8" fill="none" stroke-linecap="round"/>'
    s += f'<g transform="translate(8,{-h * 0.52}) rotate(16)"><ellipse rx="9" ry="26" fill="#f2c94c"/><path d="M-9,-6 Q-14,14 -2,26 M9,-6 Q14,14 2,26" stroke="#9cc56e" stroke-width="5" fill="none"/></g>'
    s += f'<g class="espiga" transform="translate(0,{-h})"><path d="M0,0 l-14,-30 M0,0 l-4,-38 M0,0 l6,-36 M0,0 l15,-28" stroke="#d9b54a" stroke-width="4" stroke-linecap="round"/></g></g>'
    return s
for fila, (esc, tono, dy) in enumerate(((0.6, ("#8fb878", "#9cc488"), -60), (0.8, ("#6aa64a", "#7cb85a"), -30), (1.0, ("#4f8f38", "#5c9a3e"), 0))):
    M.append(f'<g transform="translate(0,{dy})">' + "".join(maiz(4760 + k * (54 if fila < 2 else 68) + fila * 20, 230 + (k * 37) % 50, esc, tono) for k in range(26 if fila < 2 else 22)) + '</g>')
M.append('<g id="polen" filter="url(#brillo)">' + "".join('<circle class="pol" r="5" fill="#ffe27a"/>' for _ in range(44)) + '</g>')
# ================================================================== BIOSFERA 2 (cúpula geodésica)
for x in (6500, 6640, 8000, 8150):
    M.append(f'<rect x="{x - 9}" y="-180" width="18" height="180" fill="#7d5236"/><path d="M{x},-420 L{x - 90},-150 L{x + 90},-150 Z" fill="#3f7f3a"/><path d="M{x},-480 L{x - 70},-260 L{x + 70},-260 Z" fill="#4c8f45"/>')
DC, DW, DH = 7310, 470, 360
dome = [f'<path d="M{DC - DW},0 A{DW},{DH} 0 0 1 {DC + DW},0 Z" fill="url(#cristal)"/>']
for x in (7020, 7140, 7470, 7560):
    dome.append(f'<rect x="{x - 7}" y="-220" width="14" height="220" fill="#7d5236"/><circle cx="{x}" cy="-250" r="{48 + (x % 3) * 6}" fill="#5aa752"/><circle cx="{x + 18}" cy="-270" r="30" fill="#67b25c"/>')
dome.append('<g id="arbolCae" transform="translate(7310,0)"><g id="arbolR"><path d="M-8,0 L-5,-260 L5,-260 L8,0 Z" fill="#7d5236"/><circle cx="0" cy="-292" r="54" fill="#67b25c"/><circle cx="22" cy="-312" r="30" fill="#79c06d"/></g></g>')
dome.append('<g id="polvoCae" opacity="0" filter="url(#difuso)"><ellipse cx="7470" cy="-10" rx="120" ry="26" fill="#d9c59a"/></g>')
for i in range(1, 6):                                   # retícula geodésica
    a = math.pi * i / 6
    dome.append(f'<path d="M{DC},{-DH} L{DC - DW * math.cos(a):.0f},{-DH * math.sin(a) if i < 6 else 0:.0f}" stroke="#ffffff" stroke-width="3" opacity="0.6"/>')
for j in (0.35, 0.65, 0.88):
    dome.append(f'<path d="M{DC - DW * math.sqrt(1 - j * j):.0f},{-DH * j:.0f} A{DW},{DH} 0 0 1 {DC + DW * math.sqrt(1 - j * j):.0f},{-DH * j:.0f}" stroke="#ffffff" stroke-width="3" fill="none" opacity="0.55"/>')
dome.append(f'<path d="M{DC - DW},0 A{DW},{DH} 0 0 1 {DC + DW},0" stroke="#ffffff" stroke-width="7" fill="none"/><path d="M{DC - DW * 0.7},{-DH * 0.55} Q{DC - DW * 0.45},{-DH * 0.88} {DC - DW * 0.1},{-DH * 0.97}" stroke="#ffffff" stroke-width="16" fill="none" opacity="0.35" stroke-linecap="round"/>')
M.extend(dome)
# ================================================================== LLANURA QUE SE SECA
M.append('<path id="seco" d="M8200,-8 Q9100,-20 10400,-8 L10400,2200 L8200,2200 Z" fill="url(#tierraSeca)" opacity="0"/>')
cel = []
for k in range(70):
    cx, cy = 8300 + (k % 14) * 150 + (k * 37) % 60, 30 + (k // 14) * 70 + (k * 13) % 30
    pts = " ".join(f"{cx + (52 + (k * j) % 18) * math.cos(j * 1.05 + k):.0f},{cy + (24 + (k * j) % 9) * math.sin(j * 1.05 + k):.0f}" for j in range(6))
    cel.append(f'<polygon points="{pts}" fill="none" stroke="#8a6a3c" stroke-width="3" opacity="0.8"/>')
M.append('<g id="grietas" opacity="0">' + "".join(cel) + '</g>')
M.append('<g transform="translate(8560,0)"><rect x="0" y="-160" width="200" height="160" fill="#efe3c9"/><path d="M-18,-160 L100,-250 L218,-160 Z" fill="#b5543b"/><rect x="78" y="-84" width="46" height="84" fill="#7a4b32"/><rect x="24" y="-126" width="38" height="36" fill="#9fd3f0"/><rect x="140" y="-126" width="38" height="36" fill="#9fd3f0"/></g>')
M.append('<g transform="translate(8860,0)"><path d="M-34,0 L-14,-240 M34,0 L14,-240 M-24,-110 L24,-110 M-18,-180 L18,-180" stroke="#6b5b4b" stroke-width="7"/><rect x="-40" y="-330" width="80" height="94" rx="8" fill="#a9b3be"/><rect x="-40" y="-330" width="80" height="20" rx="8" fill="#8e99a5"/></g>')
M.append('<ellipse id="charca" cx="9330" cy="6" rx="200" ry="16" fill="#4aa8d8"/>')
for x in (9150, 9620, 9960, 9480):
    M.append(f'<g transform="translate({x},0)"><path d="M0,0 L0,-170 M0,-100 L-46,-150 M0,-124 L40,-176 M0,-156 L-22,-198" stroke="#6e5238" stroke-width="10" fill="none" stroke-linecap="round"/><g class="hoja"><circle cx="0" cy="-175" r="66" fill="#5aa752"/><circle cx="26" cy="-196" r="40" fill="#67b25c"/></g></g>')
NM = []
for x, y, s in ((9100 - 420, -1900, 2.2), (9100 + 380, -2600, 1.8), (9100 - 300, -3500, 2.4), (9100 + 260, -4500, 2.0), (6418, -4378, 2.4), (4630, -3164, 2.6), (2842, -1950, 2.2), (5500, -3900, 1.8), (3600, -2500, 2.0)):
    NM.append(f'<g transform="translate({x},{y}) scale({s})" opacity="0.92"><ellipse cx="0" cy="0" rx="160" ry="50" fill="#ffffff"/><ellipse cx="-70" cy="-30" rx="80" ry="54" fill="#ffffff"/><ellipse cx="50" cy="-44" rx="96" ry="66" fill="#ffffff"/><ellipse cx="0" cy="18" rx="170" ry="26" fill="#e3eef7"/></g>')
M.append('<g id="nubesM">' + "".join(NM) + '</g>')
# ================================================================== PLANETA (Natural Earth 1:110m, proyección ortográfica)
def gp(x, y): return GX + x, GY + y
def tr(d): return f'<g transform="translate({GX},{GY})">{d}</g>'
G = [f'<g id="planeta" opacity="0">',
     f'<circle cx="{GX}" cy="{GY}" r="{GR + 60}" fill="url(#atmos)"/>',
     f'<clipPath id="clipG"><circle cx="{GX}" cy="{GY}" r="{GR}"/></clipPath>',
     f'<circle cx="{GX}" cy="{GY}" r="{GR}" fill="url(#oceano)"/>',
     f'<g clip-path="url(#clipG)">',
     tr(f'<path d="{GEO["grat"]}" stroke="#ffffff" stroke-width="1" fill="none" opacity="0.08"/>'),
     tr(f'<path id="tierra" d="{GEO["land"]}" fill="#5f9f4c" stroke="#3f7a35" stroke-width="1.2"/>'),
     tr(f'<path d="{GEO["land"]}" fill="url(#relieve)" opacity="0.35"/>'),
     tr(f'<path id="polos1" d="{GEO["polN"]}" fill="#f4fbff" opacity="0.9"/><path id="polos2" d="{GEO["polS"]}" fill="#f4fbff" opacity="0.9"/>'),
     tr('<g id="calor" opacity="0" filter="url(#difusoG)"><path d="M' + " L".join(f"{x},{y}" for x, y in GEO["equator"]) + '" stroke="#ff5a2c" stroke-width="150" fill="none" stroke-linecap="round" opacity="0.65"/></g>'),
     tr('<g id="frio" opacity="0" filter="url(#difusoG)"><path d="' + GEO["polN"] + '" fill="#ffffff"/><path d="' + GEO["polS"] + '" fill="#ffffff"/></g>'),
     tr('<g id="nubesG" filter="url(#difusoG)" opacity="0.85">' + "".join(f'<ellipse class="nG" cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#ffffff" opacity="0.75"/>' for x, y, rx, ry in ((-60, -200, 90, 26), (120, 160, 110, 24), (-310, 40, 80, 22), (40, 300, 100, 22), (260, -260, 70, 20), (-200, -300, 80, 20))) + '</g>'),
     tr(f'<g id="selva"><ellipse cx="{GEO["amazon"][0]}" cy="{GEO["amazon"][1]}" rx="70" ry="44" fill="#2f7d32" opacity="0.85" filter="url(#difuso)"/></g>'),
     tr(f'<ellipse cx="{GEO["sahara"][0]}" cy="{GEO["sahara"][1]}" rx="120" ry="52" fill="#e9c46a" opacity="0.85" filter="url(#difuso)"/>'),
     tr('<g id="polvoG">' + "".join('<circle class="pg" r="4.5" fill="#f2cf7a"/>' for _ in range(46)) + '</g>'),
     tr(f'<g id="aflora" opacity="0"><ellipse cx="{GEO["peru"][0] - 18}" cy="{GEO["peru"][1] + 20}" rx="34" ry="80" fill="#6ff0ff" filter="url(#difuso)" opacity="0.8"/></g>'),
     tr('<path id="albRuta" d="M' + " L".join(f"{x},{y}" for x, y in GEO["albRing"]) + '" stroke="#ffffff" stroke-width="3" stroke-dasharray="8 8" fill="none" opacity="0"/>'),
     tr('<g id="huracanes">' + "".join(f'<g class="hur" transform="translate({x},{y})"><g class="hurR" filter="url(#suave)">' + "".join(f'<path d="M0,0 Q{26 * math.cos(a)},{26 * math.sin(a)} {50 * math.cos(a + 1.2)},{50 * math.sin(a + 1.2)}" stroke="#ffffff" stroke-width="12" fill="none" stroke-linecap="round" opacity="0.9"/>' for a in (0, 2.1, 4.2)) + '<circle r="8" fill="#2f7fc1"/></g></g>' for x, y in GEO["hur"]) + '</g>'),
     f'<circle cx="{GX}" cy="{GY}" r="{GR}" fill="url(#noche)"/>',
     f'<circle cx="{GX}" cy="{GY}" r="{GR}" fill="url(#brilloG)"/>',
     '</g>',
     tr('<g id="albatros"><path d="M-30,0 Q-15,-14 0,0 Q15,-14 30,0" stroke="#ffffff" stroke-width="6" fill="none" stroke-linecap="round"/></g>'),
     tr('<g id="celdas" opacity="0">' + "".join(f'<path class="celda" d="{d}" stroke="#ffffff" stroke-width="7" fill="none" stroke-dasharray="30 22" stroke-linecap="round" marker-end="url(#flecha)"/>' for d in (
         "M-380,-80 Q-180,-220 40,-150", "M380,-80 Q180,-220 -40,-150", "M-380,110 Q-180,250 40,180", "M380,110 Q180,250 -40,180", "M-300,-300 Q-100,-400 120,-340", "M300,320 Q100,420 -120,360")) + '</g>'),
     '</g>']
M.extend(G)
WORLD = "".join(M)
DEFS = ['<linearGradient id="mar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3fa3d6"/><stop offset="0.35" stop-color="#1f74ad"/><stop offset="1" stop-color="#0c3c63"/></linearGradient>',
        '<linearGradient id="orilla" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#7fe3e0" stop-opacity="0.85"/><stop offset="1" stop-color="#7fe3e0" stop-opacity="0"/></linearGradient>',
        '<linearGradient id="ola" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5cc0e8"/><stop offset="1" stop-color="#3fa3d6"/></linearGradient>',
        '<linearGradient id="arena" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6e4b4"/><stop offset="1" stop-color="#e4c88a"/></linearGradient>',
        '<linearGradient id="hierba" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#86c064"/><stop offset="1" stop-color="#5e9b45"/></linearGradient>',
        '<linearGradient id="tierraSeca" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d8b77a"/><stop offset="1" stop-color="#b38d55"/></linearGradient>',
        '<linearGradient id="bruma" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e7f3fb" stop-opacity="0"/><stop offset="1" stop-color="#e7f3fb" stop-opacity="0.85"/></linearGradient>',
        '<linearGradient id="cristal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e8f7ff" stop-opacity="0.65"/><stop offset="1" stop-color="#a9d8f2" stop-opacity="0.35"/></linearGradient>',
        '<radialGradient id="oceano" cx="0.4" cy="0.38" r="0.7"><stop offset="0" stop-color="#3b9be0"/><stop offset="0.7" stop-color="#1c5f9e"/><stop offset="1" stop-color="#0f3a66"/></radialGradient>',
        '<radialGradient id="atmos" cx="0.5" cy="0.5" r="0.5"><stop offset="0.86" stop-color="#7fc6ff" stop-opacity="0.55"/><stop offset="1" stop-color="#7fc6ff" stop-opacity="0"/></radialGradient>',
        '<radialGradient id="noche" cx="0.28" cy="0.4" r="0.95"><stop offset="0.55" stop-color="#000814" stop-opacity="0"/><stop offset="1" stop-color="#000814" stop-opacity="0.72"/></radialGradient>',
        '<radialGradient id="brilloG" cx="0.32" cy="0.28" r="0.4"><stop offset="0" stop-color="#ffffff" stop-opacity="0.25"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>',
        '<linearGradient id="relieve" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0.3"/><stop offset="1" stop-color="#000000" stop-opacity="0.3"/></linearGradient>',
        '<filter id="difuso" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22"/></filter>',
        '<filter id="difusoG" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="16"/></filter>',
        '<filter id="suave" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.5"/></filter>',
        '<filter id="brillo" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '<marker id="flecha" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#ffffff"/></marker>']

# ================================================================== helpers
def cam(t, d=1.4, ease="power2.inOut", **kv):
    J(f'tl.to(S, {{{", ".join(f"{k}:{v}" for k, v in kv.items())}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
NC = [0]
def card(html, t, hasta, top=600, left=40, cls=""):
    NC[0] += 1; i = NC[0]
    FXL.append(f'<div class="card {cls}" id="c{i}" style="top:{top}px;left:{left}px">{html}</div>')
    J(f'tl.set("#c{i}", {{opacity:0}}, 0); tl.fromTo("#c{i}", {{opacity:0, y:26, scale:0.96}}, {{opacity:1, y:0, scale:1, duration:0.5, ease:"power3.out", immediateRender:false}}, {t:.2f}); tl.to("#c{i}", {{opacity:0, y:-14, duration:0.3}}, {hasta:.2f});')
    return f"#c{i}"
def contador(sel, v0, v1, t, d, dec=0, suf=""):
    J(f'(() => {{ const o = {{v:{v0}}}; tl.to(o, {{v:{v1}, duration:{d:.2f}, ease:"power2.out", onUpdate:() => {{ document.querySelector("{sel}").textContent = fmt(o.v, {dec}) + "{suf}"; }}}}, {t:.2f}); }})();')
NL = [0]
def etiqueta(p, t, hasta, txt, dx=20, dy=-40):
    NL[0] += 1; i = NL[0]
    FXL.append(f'<div class="lab" id="lb{i}"><i></i>{txt}</div>')
    J(f'LABS.push({{i:{i}, x:{p[0]:.1f}, y:{p[1]:.1f}, dx:{dx}, dy:{dy}}}); LV.l{i} = 0;')
    J(f'tl.to(LV, {{l{i}:1, duration:0.4}}, {t:.2f}); tl.to(LV, {{l{i}:0, duration:0.3}}, {hasta:.2f});')
def tinte(t, color, op, d=1.2):
    J(f'tl.to("#tinte", {{backgroundColor:"{color}", opacity:{op}, duration:{d}}}, {t:.2f});')
def dias(t, n, d=1.0):
    J(f'tl.to(S, {{dias:{n}, duration:{d}, ease:"power1.inOut"}}, {t:.2f});')
def punch(t, k=1.06, d=0.5):
    J(f'tl.to(S, {{zp:{k}, duration:{d * 0.4:.2f}, ease:"power2.out"}}, {t:.2f}); tl.to(S, {{zp:1, duration:{d:.2f}, ease:"power2.inOut"}}, {t + d * 0.4:.2f});')

# ================================================================== GUION VISUAL (un solo plano)
rset(J, "P", "cometa")
FXL.append('<div id="gauge"><div class="gIn"><svg viewBox="0 0 120 70" width="132" height="77"><path d="M10,62 A50,50 0 0 1 110,62" stroke="rgba(255,255,255,0.2)" stroke-width="10" fill="none" stroke-linecap="round"/>'
           '<path id="gArc" d="M10,62 A50,50 0 0 1 110,62" stroke="#4ea3ff" stroke-width="10" fill="none" stroke-linecap="round" stroke-dasharray="157" stroke-dashoffset="47"/></svg>'
           '<div><b><span id="kmh">20</span> km/h</b><small>VIENTO</small></div></div></div>')
FXL.append('<div id="dias"><small>SIN VIENTO</small><b>DÍA <span id="nd">0</span></b></div>')
PARA = P("desapareciera") - 0.1
cam(PARA, 1.6, "power2.out", v=0)
contador("#kmh", 20, 0, PARA, 1.4)
J(f'tl.to("#gArc", {{strokeDashoffset:157, stroke:"#ff6b5e", duration:1.4, ease:"power2.out"}}, {PARA:.2f}); tl.to("#gauge b", {{color:"#ff8a7e", duration:0.4}}, {PARA + 0.8:.2f}); tl.to("#gauge", {{opacity:0, y:20, duration:0.4}}, {FE(1) + 1.6:.2f});')
punch(PARA + 0.3, 1.05, 0.8)
rpose(J, "P", "mira", PARA + 0.6, 0.8)
J(f'tl.to("#dias", {{opacity:1, y:0, duration:0.5}}, {F(2) + 0.6:.2f}); tl.to("#dias", {{opacity:0, y:-10, duration:0.4}}, {F(15) + 0.3:.2f});')
dias(F(2) + 0.6, 1, 0.6)
# 2) el día perfecto… y lo que viene
card('<small>EN UNAS SEMANAS</small><b>falta comida</b>', P("comida") - 0.4, FE(2) + 0.2, top=640)
card('<small>EN MEDIO PLANETA</small><b>no llueve</b>', P("llover") - 0.4, FE(2) + 0.2, top=830)
# 3) el mar espejo
cam(F(3) - 0.3, 1.8, cx=X_MAR, cy=-200, z=1.45)
dias(F(3), 2)
card('<small>LAS OLAS</small><b>las crea el viento</b><em>casi todas</em>', P("olas") - 0.2, FE(3) + 0.2)
etiqueta((X_MAR - 290, -205), P("veleros") - 0.3, FE(3) + 0.2, "velero sin viento", dx=-70, dy=-58)
J(f'tl.to("#veleroRef", {{opacity:0.45, duration:2}}, {P("espejo") - 0.5:.2f}); tl.to("#veleroRef", {{opacity:0, duration:0.5}}, {FE(15):.2f});')
# 4) molinos parados
cam(F(4) - 0.4, 1.9, cx=X_MOL, cy=-360, z=1.25)
dias(F(4), 3)
card('<small>ENERGÍA EÓLICA</small><b><span id="n8">0</span> %</b><em>de la electricidad del mundo</em>', P("ocho") - 0.3, FE(4) + 0.2)
contador("#n8", 0, 8, P("ocho") - 0.2, 0.9)
# 5) ciudad: niebla tóxica
cam(F(5) - 0.4, 1.9, cx=X_CIU, cy=-380, z=1.25)
dias(F(5), 5, 2)
J(f'tl.to("#smog", {{opacity:1, duration:3.4, ease:"power1.in"}}, {F(5) + 0.4:.2f}); tl.to("#smog", {{opacity:0.2, duration:1.4}}, {FE(5) + 0.5:.2f});')
tinte(F(5) + 0.8, "#8a7451", 0.35, 2.5); tinte(FE(5) + 0.4, "#8a7451", 0, 1.4)
J(f'tl.to("#sol", {{scale:0.8, opacity:0.55, duration:2}}, {F(5) + 1:.2f}); tl.to("#sol", {{scale:1, opacity:1, duration:1.2}}, {FE(5) + 0.4:.2f});')
card('<small>LONDRES · 1952</small><b>5 días sin viento</b><em>la niebla tóxica mató a miles</em>', P("1952") - 0.3, FE(5) + 0.2)
# 6) maíz: el polen cae recto
cam(F(6) - 0.4, 1.9, cx=X_MAIZ, cy=-200, z=1.9)
dias(F(6), 20, 4)
tinte(F(6), "#ffcf6b", 0.12, 1.5); tinte(FE(6), "#ffcf6b", 0, 1)
card('<small>MAÍZ</small><b>el cereal nº 1</b><em>su polen viaja con el viento</em>', P("maiz") - 0.3, P("sin", 2) - 0.3)
card('<small>SIN VIENTO</small><b class="r">sin cosecha</b>', P("cosecha") - 0.4, FE(6) + 0.2)
J(f'tl.to(S, {{pol:1, duration:0.6}}, {F(6) + 0.6:.2f}); tl.to(S, {{pol:0, duration:0.6}}, {FE(6) + 0.6:.2f});')
etiqueta((X_MAIZ + 30, -330), P("polen") - 0.2, FE(6) - 0.2, "el polen cae y no llega", dx=-40, dy=-70)
# 7) Biosfera 2
cam(F(7) - 0.4, 1.9, cx=X_BIO, cy=-250, z=1.55)
dias(F(7), 40, 3)
card('<small>BIOSFERA 2 · ARIZONA</small><b>árboles sin viento</b><em>crecían débiles</em>', P("biosfera") - 0.3, FE(7) + 0.2)
J(f'tl.to("#arbolR", {{rotation:80, svgOrigin:"0 0", duration:1.3, ease:"power2.in"}}, {P("cayendose") - 0.5:.2f}); tl.fromTo("#polvoCae", {{opacity:0}}, {{opacity:0.8, duration:0.4, immediateRender:false}}, {P("cayendose") + 0.8:.2f}); tl.to("#polvoCae", {{opacity:0, duration:1.2}}, {P("cayendose") + 1.3:.2f});')
punch(P("cayendose") + 0.75, 1.04, 0.5)
# 8-9) sequía
cam(F(8) - 0.4, 1.9, cx=X_SECO, cy=-270, z=1.45)
dias(F(8), 120, 9)
J(f'tl.to("#seco", {{opacity:1, duration:6, ease:"power1.inOut"}}, {F(8) + 0.5:.2f}); tl.to("#grietas", {{opacity:1, duration:3}}, {F(9):.2f}); tl.to(".hoja", {{opacity:0, duration:4}}, {F(9) - 1:.2f}); tl.to("#charca", {{attr:{{rx:10}}, opacity:0, duration:5}}, {F(8) + 1:.2f});')
tinte(F(8) + 1, "#ff9a3c", 0.22, 6); tinte(F(10) - 0.6, "#ff9a3c", 0, 1.5)
J(f'tl.to("#sol", {{scale:1.35, duration:5}}, {F(8) + 1:.2f}); tl.to("#sol", {{scale:1, duration:1.5}}, {F(10) - 0.6:.2f});')
card('<small>EL VIENTO</small><b>trae las nubes</b><em>del mar a la tierra</em>', P("nubes") - 0.4, FE(8) + 0.2)
card('<small>SIN ÉL</small><b>tierra seca</b><em>solo llueve sobre el mar</em>', F(9) + 0.2, FE(9) + 0.2)
# 10) subida al espacio
SUBE = F(10) - 0.6
cam(SUBE, 2.6, "power2.inOut", cx=GX, cy=GY, z=1.05)
dias(F(10), 365, 22)
J(f'tl.to("#espacio", {{opacity:1, duration:2.0}}, {SUBE + 0.3:.2f}); tl.to("#planeta", {{opacity:1, duration:1.0}}, {SUBE + 0.5:.2f}); tl.to(["#nubes", "#sol"], {{opacity:0, duration:0.9}}, {SUBE:.2f});')
J(f'tl.to("#tierra", {{fill:"#b99a5f", stroke:"#8f744a", duration:3}}, {F(10):.2f}); tl.to("#selva", {{opacity:0.9, duration:1}}, {F(10):.2f});')
J(f'tl.to("#calor", {{opacity:1, duration:1.2}}, {P("ecuador") - 0.3:.2f}); tl.to("#frio", {{opacity:0.95, duration:1.2}}, {P("polos") - 0.3:.2f}); tl.to(["#calor", "#frio"], {{opacity:0.25, duration:1}}, {FE(10) + 0.3:.2f});')
etiqueta((GX + 300, GY - 40), P("ecuador") - 0.2, FE(10) + 0.2, "ecuador: más calor", dx=-210, dy=-20)
etiqueta((GX - 120, GY - 390), P("polos") - 0.2, FE(10) + 0.2, "polos: más frío", dx=-60, dy=-64)
# 11) polvo del Sáhara → Amazonas
J(f'tl.to(S, {{dust:1, duration:0.6}}, {P("amazonas") - 0.2:.2f}); tl.to(S, {{dust:0, duration:1.4}}, {FE(11) - 0.6:.2f}); tl.to("#selva", {{opacity:0.25, duration:1.6}}, {FE(11) - 0.8:.2f});')
etiqueta(gp(60, -220), P("veintisiete") - 0.3, FE(11) + 0.2, "Sáhara → Amazonas", dx=-90, dy=-74)
card('<small>CADA AÑO</small><b><span id="n27">0</span> millones de t</b><em>de polvo que abona el Amazonas</em>', P("veintisiete") - 0.3, FE(11) + 0.2, top=1440, left=0, cls="centro")
contador("#n27", 0, 27, P("veintisiete") - 0.2, 1.2)
# 12) afloramiento (Perú)
J(f'tl.to("#aflora", {{opacity:1, duration:0.6}}, {F(12) + 0.3:.2f}); tl.to("#aflora", {{opacity:0.1, duration:1.6}}, {P("nutrientes"):.2f});')
etiqueta(gp(GEO["peru"][0], GEO["peru"][1]), P("nutrientes") - 0.4, FE(12) + 0.2, "costa de Perú", dx=-40, dy=60)
card('<small>ZONAS DE AFLORAMIENTO</small><b>1 de cada 5</b><em>peces que se pescan en el mundo</em>', P("quinta") - 0.4, FE(12) + 0.2, top=1440, left=0, cls="centro")
# 13) albatros
J(f'tl.to("#albRuta", {{opacity:0.7, duration:0.5}}, {F(13):.2f}); tl.fromTo("#albRuta", {{strokeDasharray:"0 3000"}}, {{strokeDasharray:"3000 0", duration:3.2, ease:"none", immediateRender:false}}, {F(13):.2f}); tl.to("#albRuta", {{opacity:0, duration:0.6}}, {FE(13):.2f});')
J(f'tl.to(S, {{alb:1, duration:0.4}}, {F(13):.2f}); tl.to(S, {{albA:1, duration:3.2, ease:"none"}}, {F(13):.2f}); tl.to(S, {{albCae:1, duration:1.3, ease:"power2.in"}}, {P("volar") - 1.0:.2f}); tl.to(S, {{alb:0, duration:0.4}}, {FE(13) + 0.1:.2f});')
card('<small>EL ALBATROS</small><b><span id="n46">0</span> días</b><em>para dar la vuelta al mundo</em>', P("albatros") - 0.2, FE(13) + 0.2, top=1440, left=0, cls="centro")
contador("#n46", 0, 46, P("albatros"), 1.4)
# 14) huracanes
J(f'tl.set(".hur", {{opacity:0}}, 0); tl.fromTo(".hur", {{opacity:0, scale:0.5}}, {{opacity:1, scale:1, svgOrigin:"0 0", duration:0.6, stagger:0.12, immediateRender:false}}, {F(14) - 0.3:.2f}); tl.to(".hur", {{opacity:0, scale:0.2, svgOrigin:"0 0", duration:0.9, stagger:0.2}}, {P("huracan") - 0.2:.2f});')
card('<small>LO ÚNICO BUENO</small><b>0 huracanes</b>', P("bueno") - 0.2, FE(14) + 0.3, top=1440, left=0, cls="centro")
# 15) imposible: el Sol calienta desigual → el aire se mueve
J(f'tl.to("#solG", {{opacity:1, duration:0.8}}, {P("sol") - 0.4:.2f}); tl.to("#celdas", {{opacity:1, duration:0.8}}, {P("aire") - 0.6:.2f}); tl.to("#solG", {{opacity:0, duration:0.8}}, {FE(15) + 0.3:.2f});')
J(f'tl.to("#tierra", {{fill:"#5f9f4c", stroke:"#3f7a35", duration:2}}, {P("aire") - 0.4:.2f}); tl.to("#selva", {{opacity:0.9, duration:2}}, {P("aire") - 0.4:.2f}); tl.to("#aflora", {{opacity:0, duration:1}}, {P("aire"):.2f});')
cam(P("movera") - 0.6, 1.6, "power1.inOut", v=1)
# 16) vuelta a la playa
BAJA = F(16) - 0.4
cam(BAJA, 2.2, "power2.inOut", cx=X_PLAYA + 40, cy=-128, z=1.8)
J(f'tl.to("#espacio", {{opacity:0, duration:1.0}}, {BAJA + 0.5:.2f}); tl.to("#planeta", {{opacity:0, duration:0.5}}, {BAJA + 0.4:.2f}); tl.to(["#nubes", "#sol"], {{opacity:1, duration:1.2}}, {BAJA + 1.0:.2f}); tl.to("#celdas", {{opacity:0, duration:0.5}}, {BAJA:.2f});')
J(f'tl.set("#seco", {{opacity:0}}, {BAJA + 1:.2f}); tl.set(["#grietas"], {{opacity:0}}, {BAJA + 1:.2f}); tl.set(".hoja", {{opacity:1}}, {BAJA + 1:.2f}); tl.set("#charca", {{attr:{{rx:200}}, opacity:1}}, {BAJA + 1:.2f}); tl.set("#smog", {{opacity:0}}, {BAJA + 1:.2f}); tl.set("#arbolR", {{rotation:0, svgOrigin:"0 0"}}, {BAJA + 1:.2f}); tl.set(["#calor", "#frio"], {{opacity:0}}, {BAJA + 1:.2f});')
rpose(J, "P", "cometa", P("despeine") - 0.6, 1.0)
J(f'tl.set("#gauge b", {{color:"#ffffff"}}, {BAJA:.2f}); tl.set("#gArc", {{stroke:"#4ea3ff"}}, {BAJA:.2f}); tl.fromTo("#gauge", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.5, immediateRender:false}}, {DUR - 2.6:.2f}); tl.to("#gArc", {{strokeDashoffset:47, duration:1.4, ease:"power2.out"}}, {DUR - 2.6:.2f});')
contador("#kmh", 0, 20, DUR - 2.6, 1.4)
card('<small>EL VIENTO TRAE</small><b>lluvia, comida<br>y aire limpio</b>', P("lluvia") - 0.4, DUR - 2.7, top=640)

# ================================================================== capas de pantalla
NUB = [(60, 600, 0.95), (640, 690, 0.75), (860, 540, 1.15), (330, 860, 0.62)]
NUBES = "".join(f'<div class="nube" id="nb{k}" style="left:{x}px;top:{y}px"><i></i><i></i><i></i><i></i></div>' for k, (x, y, sc) in enumerate(NUB))
ESTR = "".join(f'<i style="left:{rr.randint(10, 1070)}px;top:{rr.randint(10, 1900)}px;width:{rr.choice([2, 2, 3, 4])}px;height:{rr.choice([2, 2, 3, 4])}px;opacity:{rr.uniform(0.3, 1):.2f}"></i>' for _ in range(220))
ESTELAS = "".join(f'<path class="est" d="" stroke="#ffffff" stroke-width="{rr.choice([2, 3, 3, 4])}" fill="none" stroke-linecap="round"/>' for _ in range(16))

_S = open(os.path.join(BASE, "_subs.py"), encoding="utf-8").read()
exec(re.sub(r"CLAVE = set\(.*?\]\)", lambda m: 'CLAVE = set(norm(w) for w in ["viento", "perfecto", "comida", "llover", "olas", "espejo", "veleros", "ocho", "1952", "londres", "miles", "maiz", "polen", "cosecha", "arboles", "biosfera", "cayendose", "sequia", "nubes", "oceano", "secando", "ecuador", "polos", "amazonas", "veintisiete", "sahara", "nutrientes", "quinta", "albatros", "cuarenta", "volar", "huracan", "imposible", "sol", "aire", "despeine", "lluvia", "limpio"])', _S, count=1, flags=re.S))
html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#74b6e6}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;color:#fff;background:linear-gradient(180deg,#2f7fc6 0%,#5fa8e0 32%,#a7d3f1 68%,#e3f2fb 100%)}}
#espacio{{position:absolute;inset:0;opacity:0;background:radial-gradient(ellipse at 50% 55%,#132a55 0%,#081026 55%,#03060f 100%)}} #espacio i{{position:absolute;border-radius:50%;background:#fff}}
#sol{{position:absolute;left:800px;top:540px;width:190px;height:190px;border-radius:50%;background:radial-gradient(circle,#fffbe8 0%,#fff1b0 30%,rgba(255,226,120,0.55) 48%,rgba(255,226,120,0) 70%)}}
#solG{{position:absolute;left:-300px;top:600px;width:620px;height:620px;border-radius:50%;opacity:0;background:radial-gradient(circle,#fff9e0 0%,#ffd75e 30%,rgba(255,190,70,0.4) 52%,rgba(255,190,70,0) 72%)}}
#nubes{{position:absolute;inset:0;pointer-events:none}} .nube{{position:absolute;width:280px;height:96px}}
.nube i{{position:absolute;bottom:0;border-radius:50%;background:linear-gradient(#ffffff 55%,#e3eef7)}} .nube i:nth-child(1){{left:0;width:120px;height:58px}} .nube i:nth-child(2){{left:50px;width:140px;height:96px}} .nube i:nth-child(3){{left:140px;width:110px;height:74px}} .nube i:nth-child(4){{left:20px;width:240px;height:40px;border-radius:30px}}
svg#esc,svg#aire{{position:absolute;left:0;top:0}}
#tinte{{position:absolute;inset:0;opacity:0;mix-blend-mode:multiply;pointer-events:none}}
#vineta{{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 50% 48%,rgba(0,0,0,0) 55%,rgba(5,12,25,0.38) 100%)}}
#fxl{{position:absolute;inset:0;z-index:58;pointer-events:none}}
.card{{position:absolute;padding:20px 28px 22px 32px;border-radius:24px;background:rgba(10,22,40,0.62);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.16);box-shadow:0 18px 40px rgba(0,10,30,0.25);opacity:0;width:max-content;max-width:600px}}
.card::before{{content:"";position:absolute;left:0;top:22px;bottom:22px;width:5px;border-radius:0 4px 4px 0;background:#4ea3ff}}
.card small{{display:block;font:700 19px Inter;letter-spacing:4px;color:#8cc4ff;margin-bottom:8px}} .card b{{display:block;font:600 58px/1.06 Inter;letter-spacing:-1.5px}}
.card em{{display:block;font-style:normal;font:500 27px/1.3 Inter;color:rgba(255,255,255,0.82);margin-top:8px}} .card .r{{color:#ff7a6e}}
.card.centro{{left:0 !important;right:0;margin:0 auto;text-align:center}} .card.centro::before{{display:none}}
#gauge{{position:absolute;left:0;right:0;top:1440px;text-align:center}} #gauge .gIn{{display:inline-flex;align-items:center;gap:22px;padding:22px 40px 22px 30px;border-radius:30px;background:rgba(10,22,40,0.62);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.16)}}
#gauge b{{display:block;font:300 96px/1 Inter;letter-spacing:-3px;text-align:left}} #gauge small{{display:block;font:700 22px Inter;letter-spacing:8px;color:#8cc4ff;text-align:left;margin-top:6px}}
#dias{{position:absolute;right:40px;top:520px;padding:12px 22px;border-radius:18px;background:rgba(10,22,40,0.62);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.16);opacity:0;transform:translateY(10px);text-align:right}}
#dias small{{display:block;font:700 15px Inter;letter-spacing:4px;color:#ff9a8f}} #dias b{{display:block;font:600 38px Inter;font-variant-numeric:tabular-nums}}
.lab{{position:absolute;left:0;top:0;padding:9px 18px 9px 14px;border-radius:14px;background:rgba(10,22,40,0.72);font:600 27px Inter;white-space:nowrap;opacity:0;display:flex;align-items:center;gap:10px}} .lab i{{width:10px;height:10px;border-radius:50%;background:#4ea3ff;box-shadow:0 0 0 5px rgba(78,163,255,0.3)}}
#grano{{position:absolute;inset:0;z-index:56;pointer-events:none;opacity:0.035;background:url(assets/grano.png);mix-blend-mode:overlay}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:520px;z-index:55;pointer-events:none;background:linear-gradient(rgba(10,35,70,0.5),rgba(10,35,70,0))}}
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
  <svg id="aire" width="1080" height="1920" viewBox="0 0 1080 1920">{ESTELAS}</svg>
  <div id="tinte"></div><div id="vineta"></div>
  <div id="topsombra"></div><div id="grano"></div>
  <div id="fxl">{"".join(FXL)}</div>
  <div id="marca">@mundo.supuesto</div>
  <div id="subs" data-layout-allow-overlap>{"".join(SUBS)}</div>
  <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
</div>
<script>
const fmt = (v, d) => {{ const s = v.toFixed(d).split("."); return s[0].replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ".") + (s[1] ? "," + s[1] : ""); }};
const S = {{ t:0, v:1, cx:{X_PLAYA + 40}, cy:-128, z:1.8, zp:1, pol:0, alb:0, albA:0, albCae:0, dust:0, dias:0, ang:0, nx:0 }};
const W = document.getElementById("world"), $ = (id) => document.getElementById(id);
const LABS = [], LV = {{}};
const q = (s) => [...document.querySelectorAll(s)];
const POL = q(".pol"), GAV = q(".gav"), MECH = q(".mecha"), ASP = q(".aspas"), CO = q(".coche"), HR = q(".hurR"), EST = q(".est"), AV = q(".av"), PG = q(".pg"), DST = q(".dst"), VELAS = q(".vela"), ESP = q(".espiga"), NG = q(".nG");
const NB = [0, 1, 2, 3].map(k => $("nb" + k)), NBS = [0.95, 0.75, 1.15, 0.62];
const ALB = {json.dumps(GEO["albRing"])}, SAH = {json.dumps(GEO["sahara"])}, AMA = {json.dumps(GEO["amazon"])};
function frame() {{
  const t = S.t, v = S.v, z = S.z * S.zp;
  W.setAttribute("transform", `translate(540,1150) scale(${{z}}) translate(${{-S.cx}},${{-S.cy}})`);
  $("lejos").setAttribute("transform", `translate(${{(S.cx * 0.6).toFixed(1)}},${{(S.cy * 0.3).toFixed(1)}})`);
  // oleaje
  let d = "M-3600,2200 L-3600,0", e = "";
  for (let x = -3600; x <= -150; x += 30) {{ const y = -Math.abs(Math.sin(x / 95 - t * 2.4)) * 24 * v - Math.sin(x / 41 + t * 0.8) * 1.6; d += ` L${{x}},${{y.toFixed(1)}}`; if (v > 0.25 && (x / 30) % 7 === 0) e += `M${{x - 16}},${{(y - 1).toFixed(1)}} q16,-9 32,0 `; }}
  $("olas").setAttribute("d", d + " L-150,2200 Z"); $("espuma").setAttribute("d", e); $("espuma").style.opacity = v;
  const sw = -150 + (24 + 18 * Math.sin(t * 1.3)) * v + 4;
  $("mojada").setAttribute("d", `M-230,30 Q-170,4 -150,3 Q${{(sw + 30).toFixed(1)}},-2 ${{(sw + 70).toFixed(1)}},5 Q${{(sw + 20).toFixed(1)}},14 -230,30 Z`);
  DST.forEach((r, k) => r.style.opacity = (0.15 + 0.55 * (1 - v)) * (0.5 + 0.5 * Math.sin(t * 3 + k * 1.7)));
  // velero (+ reflejo en calma) y surfista
  $("velero").setAttribute("transform", `translate(${{-940 + 26 * Math.sin(t * 0.3) * v}},${{(Math.sin(t * 1.7) * 5 * v - 6).toFixed(1)}}) rotate(${{(3 * v * Math.sin(t * 1.3)).toFixed(2)}})`);
  const bulge = 10 + 52 * v; VELAS.forEach(s => s.setAttribute("d", `M3,-185 Q${{3 + bulge}},-100 3,-14 L78,-14 Q${{60 + bulge * 0.3}},-100 3,-185 Z`));
  $("surf").setAttribute("transform", `translate(-360,${{(-18 * v * Math.abs(Math.sin(-360 / 95 - t * 2.4)) - 4).toFixed(1)}})`);
  $("surfista").setAttribute("transform", `translate(0,${{((1 - v) * 34).toFixed(1)}}) scale(1,${{(0.62 + 0.38 * v).toFixed(2)}})`);
  // bandera
  let tp = "", bt = "";
  for (let i = 0; i <= 12; i++) {{ const u = i / 12;
    const wx = u * 150, wy = Math.sin(u * 5 - t * 9) * 11 * u, hx = 6 + Math.sin(u * 3 + t) * 2, hy = u * 130;
    const x = wx * v + hx * (1 - v), y = wy * v + hy * (1 - v);
    tp += (i ? " L" : "M") + x.toFixed(1) + "," + (-295 + y).toFixed(1);
    bt = ` L${{(x + 46 * (1 - v)).toFixed(1)}},${{(-295 + y + 90 * v + 10 * (1 - v)).toFixed(1)}}` + bt; }}
  $("tela").setAttribute("d", tp + bt + " Z");
  // palmera, cometa, hilo, cola
  $("palma").setAttribute("transform", `translate(20,-360) rotate(${{(10 * v + 4 * v * Math.sin(t * 2)).toFixed(1)}})`);
  const hx0 = {X_PLAYA} + 46, hy0 = -228;
  const kx = hx0 + 220 * v + 120 * (1 - v), ky = (-410 + 14 * Math.sin(t * 1.9)) * v + (-22) * (1 - v);
  $("cometa").setAttribute("transform", `translate(${{kx.toFixed(1)}},${{ky.toFixed(1)}}) rotate(${{(20 * v + Math.sin(t * 2.3) * 8 * v + 80 * (1 - v)).toFixed(1)}})`);
  $("hilo").setAttribute("d", `M${{hx0}},${{hy0}} Q${{((hx0 + kx) / 2 + 30 * v).toFixed(1)}},${{((hy0 + ky) / 2 + 60 + 120 * (1 - v)).toFixed(1)}} ${{kx.toFixed(1)}},${{ky.toFixed(1)}}`);
  let c = "M0,50"; for (let i = 1; i <= 7; i++) c += ` L${{(Math.sin(i * 1.2 - t * 6) * 11 * v).toFixed(1)}},${{50 + i * 18}}`; $("cola").setAttribute("d", c);
  MECH.forEach((m, k) => {{ const a = v * (10 + 14 * Math.sin(t * 11 + k)); m.setAttribute("transform", m.getAttribute("transform").replace(/ rotate\\([^)]*\\)/, "") + ` rotate(${{a.toFixed(1)}})`); m.style.opacity = Math.max(0, v * 1.4 - 0.4).toFixed(2); }});
  GAV.forEach((g, k) => {{ const x = {X_PLAYA} - 220 + k * 160 + 30 * Math.sin(t * 0.5 + k) * v, y = (-340 - k * 46 + 16 * Math.sin(t + k)) * v + (-6) * (1 - v);
    const fl = 1 - 0.55 * (1 - v) + 0.15 * Math.sin(t * 6 + k) * (1 - v); g.setAttribute("transform", `translate(${{x.toFixed(1)}},${{y.toFixed(1)}}) scale(1.1,${{fl.toFixed(2)}})`); }});
  AV.forEach((p, k) => {{ const u = ((t * 0.9 + k * 0.173) % 1); p.setAttribute("cx", ({X_PLAYA} - 260 + u * 760).toFixed(1)); p.setAttribute("cy", (-6 - 30 * Math.sin(u * Math.PI) * (0.5 + (k % 3) * 0.3)).toFixed(1)); p.setAttribute("opacity", (v * 0.8).toFixed(2)); }});
  // molinos, coches, maíz
  ASP.forEach((a, k) => a.setAttribute("transform", `rotate(${{(S.ang + k * 37).toFixed(1)}})`));
  CO.forEach((g, k) => {{ const x = 2850 + ((t * 95 + k * 470) % 1800); g.setAttribute("transform", `translate(${{x.toFixed(1)}},10)`); }});
  ESP.forEach((s, k) => s.setAttribute("transform", s.getAttribute("transform").replace(/ rotate\\([^)]*\\)/, "") + ` rotate(${{(v * 10 * Math.sin(t * 3 + k)).toFixed(1)}})`));
  POL.forEach((p, k) => {{ const x0 = 4760 + (k % 22) * 68 + 40, h = 230 + ((k % 22) * 37) % 50, ph = ((t * 0.55 + k * 0.137) % 1);
    p.setAttribute("cx", (x0 + 6 * Math.sin(k + t)).toFixed(1)); p.setAttribute("cy", (-h - 30 + ph * (h + 30)).toFixed(1)); p.setAttribute("opacity", (S.pol * (1 - ph * ph)).toFixed(2)); }});
  // planeta: polvo, albatros, huracanes, nubes
  PG.forEach((p, k) => {{ const u = ((t * 0.32 + k / 46) % 1), mx = (SAH[0] + AMA[0]) / 2 - 40, my = Math.min(SAH[1], AMA[1]) - 150;
    const x = (1 - u) * (1 - u) * SAH[0] + 2 * u * (1 - u) * mx + u * u * AMA[0], y = (1 - u) * (1 - u) * SAH[1] + 2 * u * (1 - u) * my + u * u * AMA[1];
    p.setAttribute("cx", (x + 8 * Math.sin(k * 3)).toFixed(1)); p.setAttribute("cy", (y + 8 * Math.cos(k * 2)).toFixed(1)); p.setAttribute("opacity", (S.dust * Math.sin(Math.PI * u)).toFixed(2)); }});
  {{ const n = ALB.length - 1, f = Math.min(n - 0.001, S.albA * n), i = Math.floor(f), w = f - i; const a = ALB[i], b = ALB[i + 1];
    const x = a[0] + (b[0] - a[0]) * w, y = a[1] + (b[1] - a[1]) * w + S.albCae * 160;
    $("albatros").setAttribute("transform", `translate(${{({GX} + x).toFixed(1)}},${{({GY} + y).toFixed(1)}}) rotate(${{(S.albCae * 70).toFixed(1)}}) scale(${{(1 + 0.15 * Math.sin(t * 8)).toFixed(2)}},1)`); $("albatros").style.opacity = S.alb; }}
  HR.forEach((h, k) => h.setAttribute("transform", `rotate(${{(-t * 80 + k * 50).toFixed(1)}})`));
  NG.forEach((n, k) => n.setAttribute("transform", `translate(${{(Math.sin(t * 0.2 + k) * 12).toFixed(1)}},0)`));
  // estelas de viento (pantalla)
  EST.forEach((p, k) => {{ const u = ((t * (0.35 + (k % 4) * 0.08) + k * 0.137) % 1), y0 = 560 + (k * 83) % 1000, x0 = -300 + u * 1700;
    p.setAttribute("d", `M${{x0.toFixed(1)}},${{y0}} q120,${{(-18 - (k % 3) * 8)}} 240,0 t240,0`); p.style.opacity = (v * 0.55 * Math.sin(Math.PI * u) * (S.cy > -1500 ? 1 : 0)).toFixed(2); }});
  // nubes de pantalla
  NB.forEach((n, k) => {{ n.style.transform = `translateX(${{(S.nx * (0.6 + k * 0.2)).toFixed(1)}}px) scale(${{NBS[k]}})`; }});
  $("nd").textContent = Math.round(S.dias);
  for (const L of LABS) {{ const el = $("lb" + L.i); const o = LV["l" + L.i] || 0; el.style.opacity = o;
    if (o > 0.01) {{ const x = 540 + (L.x - S.cx) * z, y = 1150 + (L.y - S.cy) * z; const xx = Math.max(20, Math.min(x + L.dx, 1060 - el.offsetWidth)); el.style.transform = `translate(${{xx}}px, ${{y + L.dy}}px)`; }} }}
}}
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

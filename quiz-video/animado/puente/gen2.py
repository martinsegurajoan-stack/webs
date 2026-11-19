#!/usr/bin/env python3
"""«Cómo se construye un puente colgante» v2 — infografía animada de perfil, simple y limpia:
fondo gris muy claro, puente en pizarra oscura, un solo acento azul, líneas que se dibujan solas y zooms a cada pieza.
  python3 gen2.py → index.html + efectos.json + ambiente.json"""
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
tl, FX, FXL, DEFS = [], [], [], []
def J(s): tl.append(s)
def fx(k, t): FX.append([k, round(t, 3)])
INK, AZ, RJ, GR = "#1e2733", "#2e6bff", "#ff4d4d", "#8a94a3"
rw = random.Random(3)

# ------------------------------------------------------------------ MUNDO (perfil del puente, coordenadas en px)
W = 3000
WY, SY, RY = 1150, 1450, 1525               # superficie del agua, fondo marino, roca
TXL, TXR, TY = 850, 2150, 250               # torres y cima
DY = 820                                    # tablero
AXL, AXR, AY = 180, 2820, 1075              # anclajes
MID = (TXL + TXR) / 2
def ycable(x):
    if TXL <= x <= TXR:
        u = (x - MID) / ((TXR - TXL) / 2); return (DY - 34) + (TY + 14 - (DY - 34)) * u * u
    if x < TXL:
        u = (x - AXL) / (TXL - AXL); return AY + (TY + 14 - AY) * u
    u = (x - TXR) / (AXR - TXR); return (TY + 14) + (AY - (TY + 14)) * u
DEFS += [
    '<linearGradient id="gAgua" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#bcd6ff" stop-opacity="0.75"/><stop offset="1" stop-color="#7fa9f5" stop-opacity="0.75"/></linearGradient>',
    '<linearGradient id="gFondo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f7f8fa"/><stop offset="1" stop-color="#e9ecf1"/></linearGradient>',
    '<filter id="sombra" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="#1e2733" flood-opacity="0.12"/></filter>',
    '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
]
S = []
S.append(f'<rect x="-2000" y="-2000" width="{W + 4000}" height="6000" fill="url(#gFondo)"/>')
# roca, fondo marino y orillas (formas suaves)
S.append(f'<rect x="-500" y="{RY}" width="{W + 1000}" height="400" fill="#d9dde3"/>')
S.append(f'<rect x="-500" y="{SY}" width="{W + 1000}" height="{RY - SY}" fill="#ece7dc"/>')
S.append(f'<path d="M-500,{WY - 30} L620,{WY - 30} Q700,{WY - 20} 720,{SY} L-500,{SY} Z" fill="#e3e7ed"/>')
S.append(f'<path d="M{W + 500},{WY - 30} L2380,{WY - 30} Q2300,{WY - 20} 2280,{SY} L{W + 500},{SY} Z" fill="#e3e7ed"/>')
S.append(f'<path d="M-500,{WY - 30} L620,{WY - 30}" stroke="{INK}" stroke-width="3" opacity="0.25"/><path d="M{W + 500},{WY - 30} L2380,{WY - 30}" stroke="{INK}" stroke-width="3" opacity="0.25"/>')
# agua (transparente: se ve todo por debajo)
AGUA = f'<g id="agua"><path d="M690,{WY} L2310,{WY} L2310,{SY} L690,{SY} Z" fill="url(#gAgua)"/><path id="olaL" d="M690,{WY} ' + " ".join(f'Q{720 + i * 60},{WY - 8} {750 + i * 60},{WY}' for i in range(27)) + f'" stroke="#ffffff" stroke-width="4" fill="none" opacity="0.8"/></g>'
# corriente (chevrons)
CORR = '<g id="corr" opacity="0">' + "".join(f'<path class="chev" d="M{900 + i * 220},{WY + 140 + (i % 2) * 70} l26,22 l-26,22" stroke="#ffffff" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' for i in range(6)) + '</g>'
def dpath(cid, d, sw, color=INK, extra=""):
    return f'<path id="{cid}" d="{d}" stroke="{color}" stroke-width="{sw}" fill="none" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1 1" {extra}/>'
# cimientos (cajones)
CIM = ""
for i, x in enumerate((TXL, TXR)):
    CIM += (f'<g id="cimG{i}"><g id="cimM{i}"><rect x="{x - 75}" y="{WY - 12}" width="150" height="{RY + 70 - WY + 12}" rx="10" fill="#cfd6df"/>'
            f'<path d="M{x - 75},{WY + 60} L{x + 75},{WY + 60} M{x - 75},{WY + 180} L{x + 75},{WY + 180} M{x - 75},{WY + 300} L{x + 75},{WY + 300}" stroke="#b7c0cc" stroke-width="3"/>'
            f'<rect x="{x - 75}" y="{WY - 12}" width="150" height="{RY + 70 - WY + 12}" rx="10" fill="none" stroke="{INK}" stroke-width="4"/>'
            f'<rect id="cimH{i}" x="{x - 81}" y="{WY - 18}" width="162" height="{RY + 82 - WY + 12}" rx="14" fill="none" stroke="{AZ}" stroke-width="6" opacity="0" filter="url(#glow)"/></g></g>')
# torres (dos patas, vigas y dos arcos huecos)
def torre(i, x):
    w, h = 70, WY - 12 - TY
    patas = f'M{x - w},{WY - 12} L{x - w + 8},{TY} M{x + w},{WY - 12} L{x + w - 8},{TY}'
    out = f'<g id="torre{i}"><path d="M{x - w - 12},{WY - 12} L{x - w - 4},{TY} L{x + w + 4},{TY} L{x + w + 12},{WY - 12} Z" fill="{INK}"/>'
    for y0, y1, ww in ((DY + 30, 560, 46), (520, 330, 40)):
        out += f'<path d="M{x - ww},{y0} L{x - ww},{y1 + ww} A{ww},{ww} 0 0 1 {x + ww},{y1 + ww} L{x + ww},{y0} Z" fill="#f2f4f7"/>'
        out += f'<path class="arcoH" d="M{x - ww},{y0} L{x - ww},{y1 + ww} A{ww},{ww} 0 0 1 {x + ww},{y1 + ww} L{x + ww},{y0} Z" fill="none" stroke="{AZ}" stroke-width="7" opacity="0" filter="url(#glow)"/>'
    out += f'<rect x="{x - 30}" y="{TY - 24}" width="60" height="26" rx="6" fill="#4a5566"/></g>'
    return out
TORRES = torre(0, TXL) + torre(1, TXR)
# cable principal
pts = [(x, ycable(x)) for x in range(AXL, AXR + 1, 20)]
CABLE_D = "M" + " L".join(f"{x},{y:.1f}" for x, y in pts)
PILOTO = dpath("piloto", CABLE_D, 3, AZ, 'stroke-dasharray="0.004 0.006"')
PASAR = f'<path id="pasarela" d="{CABLE_D}" transform="translate(0,14)" stroke="{GR}" stroke-width="3" fill="none" opacity="0" stroke-dasharray="10 8"/>'
HILOS = "".join(f'<path class="hilo" d="{CABLE_D}" transform="translate(0,{(k % 5) - 2})" stroke="{INK}" stroke-width="1.2" fill="none" opacity="0" pathLength="1" stroke-dasharray="1 1"/>' for k in range(10))
CABLE = dpath("cable", CABLE_D, 9) + f'<path id="cableH" d="{CABLE_D}" stroke="{AZ}" stroke-width="16" fill="none" opacity="0" filter="url(#glow)"/>'
RUEDA = f'<g id="rueda" opacity="0"><circle r="16" fill="#ffffff" stroke="{AZ}" stroke-width="5"/><circle r="4" fill="{AZ}"/></g>'
# anclajes
ANC = ""
for i, x in enumerate((AXL, AXR)):
    ANC += (f'<g id="anc{i}"><path d="M{x - 80},{WY - 30} L{x - 60},{AY - 20} L{x + 60},{AY - 20} L{x + 80},{WY - 30} Z" fill="#9aa4b2"/>'
            f'<path id="ancH{i}" d="M{x - 86},{WY - 26} L{x - 64},{AY - 26} L{x + 64},{AY - 26} L{x + 86},{WY - 26} Z" fill="none" stroke="{AZ}" stroke-width="6" opacity="0" filter="url(#glow)"/></g>')
# péndolas
PEN, PENX = "", []
for x in list(range(TXL + 40, TXR - 20, 40)) + list(range(AXL + 120, TXL - 20, 40)) + list(range(TXR + 40, AXR - 100, 40)):
    PENX.append(x)
PENX.sort(key=lambda x: abs(x - MID))
for k, x in enumerate(PENX):
    PEN += f'<path class="pen" id="pen{k}" d="M{x},{ycable(x) + 4} L{x},{DY - 2}" stroke="{INK}" stroke-width="3" pathLength="1" stroke-dasharray="1 1" opacity="0.9"/>'
PENH = '<g id="penH" opacity="0" filter="url(#glow)">' + "".join(f'<path d="M{x},{ycable(x) + 4} L{x},{DY - 2}" stroke="{AZ}" stroke-width="6"/>' for x in PENX) + '</g>'
# tablero en tramos (del centro hacia fuera)
TRAMOS, NT = [], 0
TW = 110
xs = list(range(150, 2850, TW))
xs.sort(key=lambda x: abs(x + TW / 2 - MID))
TAB = ""
for k, x in enumerate(xs):
    TAB += (f'<g class="tramo" id="tr{k}"><g id="trM{k}"><rect x="{x + 2}" y="{DY}" width="{TW - 4}" height="26" rx="4" fill="#4a5566"/>'
            f'<rect class="asf" x="{x + 2}" y="{DY}" width="{TW - 4}" height="7" fill="{INK}" opacity="0"/></g></g>')
NT = len(xs)
LUCES = '<g id="luces" opacity="0">' + "".join(f'<circle cx="{x}" cy="{DY - 16}" r="5" fill="#ffd166"/><circle cx="{x}" cy="{DY - 16}" r="14" fill="#ffd166" opacity="0.25"/>' for x in range(200, 2820, 90)) + '</g>'
COCHES = '<g id="coches" opacity="0">' + "".join(f'<g class="coche" id="co{k}"><rect x="-22" y="{DY - 18}" width="44" height="16" rx="7" fill="{c}"/></g>' for k, c in enumerate(["#2e6bff", INK, "#9aa4b2", "#2e6bff", INK, "#9aa4b2"])) + '</g>'
BARCO = (f'<g id="barco"><g transform="translate(0,{WY})"><path d="M-170,-10 L170,-10 L140,40 L-150,40 Z" fill="{INK}"/>'
         f'<rect x="-120" y="-70" width="60" height="60" rx="6" fill="#4a5566"/>' + "".join(f'<rect x="{-50 + k * 46}" y="-48" width="40" height="38" rx="4" fill="{c}"/>' for k, c in enumerate(["#2e6bff", "#9aa4b2", "#2e6bff", "#c9d1dc"])) + '</g></g>')
BARCAZA = f'<g id="barcaza" opacity="0"><rect x="-70" y="{WY - 16}" width="140" height="26" rx="6" fill="{INK}"/><path id="izado" d="M-30,{WY - 16} L-30,{DY} M30,{WY - 16} L30,{DY}" stroke="{AZ}" stroke-width="3"/></g>'
FANT = f'<g id="fant" opacity="0"><rect x="{MID - 60}" y="{DY + 26}" width="120" height="{RY - DY - 26}" rx="10" fill="none" stroke="{RJ}" stroke-width="6" stroke-dasharray="18 12"/><path d="M{MID - 110},{(DY + RY) / 2 - 110} l220,220 M{MID + 110},{(DY + RY) / 2 - 110} l-220,220" stroke="{RJ}" stroke-width="14" stroke-linecap="round"/></g>'
# flujo de fuerzas (trazos azules que corren)
FL = []
for s, tx, ax in ((-1, TXL, AXL), (1, TXR, AXR)):
    x0 = MID + s * 260
    d = f'M{x0},{DY} L{x0},{ycable(x0)} ' + " ".join(f'L{x},{ycable(x):.0f}' for x in (range(int(x0), tx, s * 20))) + f' L{tx},{TY + 14} L{tx},{RY + 60}'
    d2 = f'M{tx},{TY + 14} ' + " ".join(f'L{x},{ycable(x):.0f}' for x in range(tx, ax, -s * 20 if s < 0 else s * 20)) + f' L{ax},{AY}'
    FL += [d, d2]
FLUJO = '<g id="flujo" opacity="0">' + "".join(f'<path class="fl" d="{d}" stroke="{AZ}" stroke-width="10" fill="none" stroke-linecap="round" stroke-dasharray="18 26" filter="url(#glow)"/>' for d in FL) + '</g>'
VIENTO = '<g id="viento" opacity="0">' + "".join(f'<path class="vi" d="M{-200 + k * 0},{560 + k * 70} q120,-20 240,0 t240,0" stroke="{GR}" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.7"/>' for k in range(6)) + '</g>'
# cotas (líneas de medida tipo plano)
def cota(cid, x0, y0, x1, y1, txt, color=INK):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    hor = abs(y1 - y0) < abs(x1 - x0)
    tx = f'<text x="{mx}" y="{my - 18 if hor else my}" text-anchor="{"middle" if hor else "start"}" dx="{0 if hor else 24}" font-family="Inter" font-weight="700" font-size="44" fill="{color}">{txt}</text>'
    tick = (f'M{x0},{y0 - 16} L{x0},{y0 + 16} M{x1},{y1 - 16} L{x1},{y1 + 16}' if hor else f'M{x0 - 16},{y0} L{x0 + 16},{y0} M{x1 - 16},{y1} L{x1 + 16},{y1}')
    return f'<g id="{cid}" opacity="0"><path d="M{x0},{y0} L{x1},{y1} {tick}" stroke="{color}" stroke-width="4" fill="none"/>{tx}</g>'
COTAS = (cota("cSpan", TXL, 1000, TXR, 1000, "1.000 m sin apoyos", AZ) + cota("cProf", 1000, WY + 20, 1000, SY - 10, "profundo", INK)
         + cota("cAlt", TXL - 160, WY - 12, TXL - 160, TY, "+200 m", AZ) + cota("cGal", 1700, DY + 40, 1700, WY - 70, "gálibo", INK)
         + cota("cVien", MID + 260, DY - 90, MID + 260, DY + 110, "varios metros", AZ))
DRON = f'<g id="dron" opacity="0"><rect x="-18" y="-8" width="36" height="16" rx="6" fill="{INK}"/><path d="M-30,-14 L-6,-14 M6,-14 L30,-14" stroke="{AZ}" stroke-width="5" stroke-linecap="round"/></g>'
svg = (f'{"".join(S)}{CIM}{AGUA}{CORR}{BARCO}{FANT}{ANC}{TORRES}{PASAR}{HILOS}{PILOTO}{CABLE}{PEN}{PENH}{TAB}{LUCES}{COCHES}{BARCAZA}{RUEDA}{DRON}{FLUJO}{VIENTO}{COTAS}')

# ------------------------------------------------------------------ herramientas
def plano(t, cx, cy, z, d=1.0, ease="power2.inOut"):
    x = 540 - cx * z; y = 960 - cy * z
    if d == 0:
        J(f'tl.set("#cam", {{x:{x:.0f}, y:{y:.0f}, scale:{z:.3f}}}, {t:.2f});'); return
    J(f'tl.to("#cam", {{x:{x:.0f}, y:{y:.0f}, scale:{z:.3f}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
    if d <= 0.9: fx("whoosh", t)
def dibuja(sel, t, d=0.8, ease="power2.inOut", desde=1):
    J(f'tl.fromTo("{sel}", {{strokeDashoffset:{desde}}}, {{strokeDashoffset:0, duration:{d:.2f}, ease:"{ease}", immediateRender:false}}, {t:.2f});')
def borra(sel, t, d=0.5):
    J(f'tl.to("{sel}", {{strokeDashoffset:1, duration:{d:.2f}, ease:"power2.in"}}, {t:.2f});')
def op(sel, v, t, d=0.4): J(f'tl.to("{sel}", {{opacity:{v}, duration:{d:.2f}}}, {t:.2f});')
def pulso(sel, t, hasta):
    J(f'tl.to("{sel}", {{opacity:1, duration:0.3}}, {t:.2f}); tl.to("{sel}", {{opacity:0.35, duration:0.45, yoyo:true, repeat:{max(1, int((hasta - t - 0.6) / 0.45))}, ease:"sine.inOut"}}, {t + 0.3:.2f}); tl.to("{sel}", {{opacity:0, duration:0.3}}, {hasta:.2f});')
NL = [0]
def rotulo(kicker, titulo, t, hasta, top=1430):
    NL[0] += 1; i = NL[0]
    FXL.append(f'<div class="ro" id="ro{i}" style="top:{top}px"><small>{kicker}</small><b>{titulo}</b></div>')
    J(f'tl.set("#ro{i}", {{opacity:0}}, 0); tl.fromTo("#ro{i}", {{opacity:0, y:24}}, {{opacity:1, y:0, duration:0.45, ease:"power3.out", immediateRender:false}}, {t:.2f}); tl.to("#ro{i}", {{opacity:0, y:-16, duration:0.3}}, {hasta:.2f});')
    fx("pop", t)
def grande(html, t, hasta, top=1400):
    NL[0] += 1; i = NL[0]
    FXL.append(f'<div class="gr" id="gr{i}" style="top:{top}px">{html}</div>')
    J(f'tl.set("#gr{i}", {{opacity:0}}, 0); tl.fromTo("#gr{i}", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.55, ease:"power3.out", immediateRender:false}}, {t:.2f}); tl.to("#gr{i}", {{opacity:0, duration:0.3}}, {hasta:.2f});')
    fx("golpe", t)
    return f"#gr{i}"

# ------------------------------------------------------------------ estado inicial (fotograma 0 = puente terminado)
J('tl.set("#piloto, .hilo", {opacity:0}, 0); tl.set("#cable, .pen", {strokeDashoffset:0}, 0); tl.set(".asf", {opacity:1}, 0); tl.set("#luces, #coches", {opacity:1}, 0);')
J(f'tl.set("#barco", {{x:{MID - 420}}}, 0);')
HERO = (MID, 900, 0.40)
plano(0, *HERO, 0)
# coches y olas todo el vídeo
for k in range(6):
    dirr = 1 if k % 2 == 0 else -1
    x0 = 200 + k * 420
    J(f'tl.fromTo("#co{k}", {{x:{x0 if dirr > 0 else x0 + 400}}}, {{x:"{"+" if dirr > 0 else "-"}=2600", duration:{DUR / 3:.1f}, repeat:2, ease:"none", immediateRender:false}}, 0);')
J(f'tl.fromTo("#olaL", {{x:0}}, {{x:-120, duration:2.4, repeat:{int(DUR / 2.4)}, ease:"none", immediateRender:false}}, 0);')
J(f'tl.fromTo(".chev", {{x:0, opacity:0}}, {{x:120, opacity:1, duration:1.2, stagger:0.1, repeat:{int(DUR / 1.2)}, yoyo:false, ease:"none", immediateRender:false}}, 0);')
J(f'tl.fromTo(".fl", {{strokeDashoffset:0}}, {{strokeDashoffset:-440, duration:2.2, repeat:{int(DUR / 2.2)}, ease:"none", immediateRender:false}}, 0);')

# ------------------------------------------------------------------ GUION VISUAL
# 1) gancho
plano(0.3, MID, 880, 0.46, FE(1) - 0.5, "sine.inOut")
op("#cSpan", 1, 0.0, 0.01); J('tl.set("#cSpan", {opacity:1}, 0);')
grande('1.000 m<small>NI UNA COLUMNA EN EL AGUA</small>', 0.0, P("coches") - 0.2)
J('tl.set("#gr1", {opacity:1, y:0}, 0);')
op("#cSpan", 0, P("coches") - 0.2)
grande('¿Cómo se aguanta?', P("aguanta") - 0.6, FE(1) + 0.2)
# 2) mar profundo, corrientes, barcos
plano(F(2) - 0.2, MID - 300, 1180, 0.85, 0.9)
op("#cProf", 1, P("profundo") - 0.2); op("#cProf", 0, P("corrientes") - 0.1)
op("#corr", 1, P("corrientes") - 0.2); op("#corr", 0, P("barcos") - 0.1)
J(f'tl.to("#barco", {{x:{MID + 520}, duration:{FE(2) - P("barcos") + 1.5:.2f}, ease:"none"}}, {P("barcos") - 0.6:.2f});')
op("#cGal", 1, P("barcos")); op("#cGal", 0, FE(2) + 0.2)
# 3) un pilar sería un estorbo → lo cuelgan
plano(F(3) - 0.2, MID, 900, 0.55, 0.9)
op("#fant", 1, P("pilar") - 0.1, 0.3); op("#fant", 0, P("estorbo") + 0.5, 0.3); fx("denegada", P("estorbo") - 0.2)
J(f'tl.set("#barco", {{x:{MID - 420}, opacity:0}}, {F(4) - 0.3:.2f}); tl.to("#barco", {{opacity:1, duration:0.6}}, {F(17):.2f});')
pulso("#cableH", P("cuelgan") - 0.4, FE(3) + 0.3)
grande('Lo cuelgan', P("cuelgan") - 0.2, FE(3) + 0.3)
# 4) se borra todo y empieza la obra: cajones de hormigón
fx("rebobina", F(4) - 0.4)
borra("#cable, .pen", F(4) - 0.4, 0.6)
op("#torre0, #torre1, #anc0, #anc1, .tramo, #luces, #coches", 0, F(4) - 0.4, 0.5)
J(f'tl.set("#cimM0, #cimM1", {{y:-480}}, {F(4):.2f}); tl.set("#cimG0, #cimG1", {{opacity:0}}, {F(4) - 0.4:.2f});')
plano(F(4) - 0.1, TXL + 120, 1300, 1.05, 1.0)
op("#cimG0, #cimG1", 1, P("hunde") - 0.4, 0.3)
J(f'tl.to("#cimM0, #cimM1", {{y:0, duration:{P("firme") - P("hunde") + 0.3:.2f}, ease:"power1.inOut"}}, {P("hunde") - 0.2:.2f});')
fx("golpe", P("firme") + 0.1)
pulso("#cimH0", P("cajon") - 0.1, FE(4) + 0.3)
rotulo("CIMENTACIÓN", "Cajón de hormigón hasta la roca", P("cajon") - 0.1, FE(4) + 0.3)
# 5) torres que suben; arcos huecos arriba
plano(F(5) - 0.2, TXL + 100, 700, 0.62, 1.0)
J(f'tl.set("#torre0, #torre1", {{opacity:1, scaleY:0, svgOrigin:"0 {WY - 12}"}}, {P("levantan") - 0.3:.2f}); tl.to("#torre0, #torre1", {{scaleY:1, svgOrigin:"0 {WY - 12}", duration:2.2, ease:"power2.out"}}, {P("levantan") - 0.3:.2f});')
op("#cAlt", 1, P("doscientos") - 0.3); op("#cAlt", 0, P("fijate") - 0.2)
plano(P("fijate") - 0.4, TXL, 470, 1.35, 1.0)
pulso("#torre0 .arcoH", P("arriba") - 0.1, FE(5) + 0.3)
op("#viento", 1, P("viento") - 0.3); op("#viento", 0, FE(5) + 0.3)
J(f'tl.fromTo(".vi", {{x:300}}, {{x:1300, duration:1.0, stagger:0.12, repeat:1, ease:"none", immediateRender:false}}, {P("viento") - 0.3:.2f});')
rotulo("LA TORRE", "Arcos huecos: menos peso y menos viento", P("arcos") - 0.3, FE(5) + 0.3)
# 6) cable piloto con un dron
plano(F(6) - 0.2, MID, 700, 0.42, 1.0)
J(f'tl.set("#piloto", {{opacity:1, strokeDashoffset:1, strokeDasharray:"1 1"}}, {P("cruzar") - 0.3:.2f});')
dibuja("#piloto", P("cruzar") - 0.2, FE(6) - P("cruzar") + 0.2, "power1.inOut")
J(f'tl.set("#dron", {{opacity:1}}, {P("cruzar") - 0.2:.2f}); tl.fromTo("#dron", {{x:{AXL}, y:{AY - 40}}}, {{keyframes:[' + ",".join(f'{{x:{x}, y:{ycable(x) - 40:.0f}, duration:{(FE(6) - P("cruzar") + 0.2) / 26:.3f}, ease:"none"}}' for x in range(AXL + 100, AXR + 1, 100)) + f'], immediateRender:false}}, {P("cruzar") - 0.2:.2f}); tl.to("#dron", {{opacity:0, duration:0.3}}, {FE(6) + 0.1:.2f});')
rotulo("CABLE PILOTO", "El primer hilo, de orilla a orilla", P("cable") - 0.1, FE(6) + 0.2)
# 7) pasarela e hilado: la rueda va y viene
op("#pasarela", 1, P("pasarela") - 0.2)
plano(P("pasarela") - 0.3, TXL + 260, 420, 1.15, 1.0)
J(f'tl.set("#rueda", {{opacity:1}}, {P("hilado") - 0.2:.2f}); tl.to("#rueda", {{opacity:0, duration:0.3}}, {F(8) + 1.0:.2f});')
idas = [(x, ycable(x)) for x in range(TXL - 200, TXL + 760, 40)]
kfs = ",".join(f'{{x:{x}, y:{y:.0f}, duration:0.06, ease:"none"}}' for x, y in idas)
vueltas = ",".join(f'{{x:{x}, y:{y:.0f}, duration:0.06, ease:"none"}}' for x, y in idas[::-1])
J(f'tl.set("#rueda", {{x:{idas[0][0]}, y:{idas[0][1]:.0f}}}, {P("hilado") - 0.2:.2f}); tl.to("#rueda", {{keyframes:[{kfs},{vueltas},{kfs},{vueltas}]}}, {P("hilado") - 0.2:.2f});')
J(f'tl.set(".hilo", {{opacity:0.8}}, {P("hilado"):.2f}); tl.fromTo(".hilo", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:1.4, stagger:0.45, ease:"none", immediateRender:false}}, {P("hilado"):.2f});')
rotulo("HILADO", "Alambres de acero de 5 mm", P("rueda") - 0.2, FE(7) + 0.2)
# 8) decenas de miles de alambres → cable de más de 1 m
FXL.append('<div id="seccion" class="seccion"><svg viewBox="0 0 400 400" width="440" height="440"><circle cx="200" cy="200" r="192" fill="#ffffff" stroke="#1e2733" stroke-width="8"/>'
           + "".join(f'<circle class="al" cx="{200 + r * math.cos(a):.1f}" cy="{200 + r * math.sin(a):.1f}" r="5.2" fill="#1e2733"/>'
                     for r, n in ((0, 1), (14, 6), (28, 12), (42, 18), (56, 24), (70, 30), (84, 36), (98, 42), (112, 48), (126, 54), (140, 60), (154, 66), (168, 72))
                     for a in [kk * 2 * math.pi / n for kk in range(n)])
           + '</svg><b id="alN">1</b><small>ALAMBRES EN UN SOLO CABLE</small></div>')
J('tl.set("#seccion", {opacity:0}, 0); tl.set(".al", {opacity:0}, 0);')
J(f'tl.fromTo("#seccion", {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.5, ease:"back.out(1.6)", immediateRender:false}}, {F(8):.2f}); tl.to(".al", {{opacity:1, duration:0.02, stagger:{2.4 / 469:.4f}}}, {F(8) + 0.2:.2f}); tl.to("#seccion", {{opacity:0, duration:0.3}}, {FE(8) + 0.2:.2f});')
J(f'const alv = {{v:1}}; tl.to(alv, {{v:36830, duration:2.6, ease:"power2.in", onUpdate:() => {{ document.getElementById("alN").textContent = String(Math.round(alv.v)).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, "."); }}}}, {F(8) + 0.2:.2f});')
fx("cuenta", F(8) + 0.2)
J(f'tl.set("#cable", {{strokeDashoffset:0}}, {P("apretados") - 0.3:.2f}); tl.fromTo("#cable", {{strokeWidth:2}}, {{strokeWidth:9, duration:1.0, immediateRender:false}}, {P("apretados") - 0.3:.2f});')
op(".hilo, #pasarela, #piloto", 0, P("apretados"), 0.6)
grande('&gt; 1 m<small>DE GROSOR</small>', P("grosor") - 0.6, FE(8) + 0.3, top=1460)
# 9) anclajes
plano(F(9) - 0.2, AXL + 200, AY - 60, 1.1, 1.0)
J(f'tl.set("#anc0, #anc1", {{opacity:1, scaleY:0, svgOrigin:"0 {WY - 30}"}}, {F(9) + 0.2:.2f}); tl.to("#anc0, #anc1", {{scaleY:1, svgOrigin:"0 {WY - 30}", duration:1.0, ease:"back.out(1.4)"}}, {F(9) + 0.2:.2f});')
pulso("#ancH0", P("anclajes") - 0.2, FE(9) + 0.3)
rotulo("ANCLAJE", "Hormigón macizo que sujeta el cable", P("anclajes") - 0.2, FE(9) + 0.3)
# 10) péndolas
plano(F(10) - 0.2, MID, 640, 0.75, 1.0)
J(f'tl.set(".pen", {{strokeDashoffset:1}}, {F(4):.2f}); tl.to(".pen", {{strokeDashoffset:0, duration:0.25, stagger:{(FE(10) - P("pendolas") + 0.3) / len(PENX):.3f}}}, {P("pendolas") - 0.3:.2f});')
pulso("#penH", P("pendolas"), FE(10) + 0.3)
rotulo("PÉNDOLAS", "Cables verticales cada pocos metros", P("pendolas") - 0.1, FE(10) + 0.3)
# 11-12) tramos del tablero: barcaza + grúa, del centro hacia fuera
plano(F(11) - 0.2, MID, 960, 0.8, 1.0)
T0, T1 = P("barcazas") - 0.4, FE(12)
dt = (T1 - T0) / NT
J(f'tl.set(".tramo", {{opacity:0}}, {F(4):.2f});')
for k, x in enumerate(xs):
    t = T0 + k * dt
    cx = x + TW / 2
    J(f'tl.set("#tr{k}", {{opacity:1}}, {t:.2f}); tl.fromTo("#trM{k}", {{y:{WY - DY - 40}}}, {{y:0, duration:{dt * 0.9:.2f}, ease:"power1.out", immediateRender:false}}, {t:.2f});')
    J(f'tl.set("#barcaza", {{x:{cx}, opacity:1}}, {t:.2f});')
J(f'tl.to("#barcaza", {{opacity:0, duration:0.3}}, {T1:.2f});')
rotulo("TABLERO", "Las barcazas traen los tramos y una grúa los sube", P("barcazas") - 0.2, FE(11) + 0.2)
plano(F(12) - 0.2, MID, 860, 0.42, 1.2)
FXL.append('<div id="flechas" class="flechas"><span>←</span><span>DESDE EL CENTRO</span><span>→</span></div>')
J(f'tl.set("#flechas", {{opacity:0}}, 0); tl.to("#flechas", {{opacity:1, duration:0.3}}, {P("centro") - 0.2:.2f}); tl.to("#flechas", {{opacity:0, duration:0.3}}, {FE(12) + 0.2:.2f});')
# 13) el truco: el recorrido del peso
plano(F(13) - 0.2, MID, 820, 0.45, 1.0)
op("#flujo", 1, F(13) + 0.2, 0.6); op("#flujo", 0, FE(14) + 0.2, 0.5)
pulso("#penH", P("pendolas", 2) - 0.2, P("cable", 4) + 0.6)
pulso("#cableH", P("cable", 4) - 0.2, P("torres", 3) + 0.4)
pulso(".arcoH", P("torres", 3) - 0.2, FE(13) + 0.4)
pulso("#ancH0, #ancH1", P("anclajes", 2) - 0.2, FE(13) + 0.4)
rotulo("EL TRUCO", "El peso viaja por los cables hasta las torres y la tierra", F(13) + 0.6, FE(13) + 0.3)
# 14) ni un kilo al mar
plano(F(14) - 0.2, MID, 1290, 0.9, 0.9)
grande('0 kg<small>SOBRE EL MAR</small>', P("kilo") - 0.2, FE(14) + 0.3, top=1460)
# 15) último tramo, asfalto, luces
plano(F(15) - 0.2, MID, 860, 0.6, 1.0)
J(f'tl.set(".asf", {{opacity:0}}, {F(4):.2f}); tl.to(".asf", {{opacity:1, duration:0.05, stagger:0.04}}, {P("asfalta") - 0.2:.2f});')
op("#luces", 1, P("luces") - 0.2, 0.6); op("#coches", 1, P("luces"), 0.6); fx("ding", P("luces"))
# 16) viento: el tablero se mueve varios metros
plano(F(16) - 0.2, MID + 200, 820, 0.8, 1.0)
op("#viento", 1, F(16)); op("#viento", 0, FE(16))
J(f'tl.fromTo(".vi", {{x:200}}, {{x:1900, duration:1.1, stagger:0.12, repeat:3, ease:"none", immediateRender:false}}, {F(16):.2f});')
J(f'tl.to(".tramo, #luces, #coches", {{y:22, duration:0.8, yoyo:true, repeat:5, ease:"sine.inOut"}}, {F(16) + 0.2:.2f}); tl.to(".tramo, #luces, #coches", {{y:0, duration:0.4}}, {FE(16):.2f});')
op("#cVien", 1, P("metros", 4) - 0.4); op("#cVien", 0, FE(16) + 0.2)
rotulo("FLEXIBLE", "Si fuera rígido, se rompería", P("rigido") - 0.4, FE(16) + 0.3)
# 17) cierre: vuelta al plano del principio
plano(F(17) - 0.2, *HERO, DUR - F(17) + 0.2, "sine.inOut")
grande('Colgado de dos cables', P("cables", 2) - 0.6, DUR - 1.2)
J(f'tl.fromTo("#gr1", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.6, ease:"power3.out", immediateRender:false}}, {DUR - 1.0:.2f}); tl.to("#cSpan", {{opacity:1, duration:0.6}}, {DUR - 1.0:.2f});')

# ------------------------------------------------------------------ montaje
_S = open(os.path.join(BASE, "_subs.py"), encoding="utf-8").read()
exec(re.sub(r"CLAVE = set\(.*?\]\)", lambda m: 'CLAVE = set(norm(w) for w in ["mil", "columna", "aguanta", "profundo", "corrientes", "barcos", "pilar", "cuelgan", "hormigon", "roca", "torres", "doscientos", "arcos", "huecos", "cable", "dron", "hilado", "cinco", "miles", "metro", "anclajes", "pendolas", "tablero", "centro", "truco", "kilo", "luces", "viento", "rigido", "colgado", "cables"])', _S, count=1, flags=re.S))
tl[:] = [x.replace('color:"#ffffff"', f'color:"{INK}"') for x in tl]
html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#f2f4f7}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;background:#f2f4f7;color:{INK}}}
#cam{{position:absolute;left:0;top:0;width:{W}px;height:1920px;transform-origin:0 0}}
#fxl{{position:absolute;inset:0;z-index:58;pointer-events:none}}
.ro{{position:absolute;left:0;right:0;margin:0 auto;width:max-content;max-width:960px;padding:20px 34px;border-radius:24px;background:rgba(247,248,250,0.94);box-shadow:0 16px 40px rgba(30,39,51,0.14);text-align:center}}
.ro small{{display:block;font:700 20px Inter;letter-spacing:7px;color:{AZ};margin-bottom:10px}} .ro b{{display:block;font:600 46px/1.18 Inter;letter-spacing:-0.5px;color:{INK}}}
.gr{{position:absolute;left:0;right:0;text-align:center;font:200 132px/1 Inter;letter-spacing:-5px;color:{INK}}}
.gr small{{display:block;margin-top:14px;font:700 22px Inter;letter-spacing:8px;color:{AZ}}}
.seccion{{position:absolute;left:0;right:0;top:600px;text-align:center}} .seccion svg{{filter:drop-shadow(0 20px 40px rgba(30,39,51,0.18))}}
.seccion b{{display:block;font:200 110px/1 Inter;letter-spacing:-4px;margin-top:20px;font-variant-numeric:tabular-nums}} .seccion small{{font:700 22px Inter;letter-spacing:7px;color:{AZ}}}
.flechas{{position:absolute;left:0;right:0;top:1440px;display:flex;justify-content:center;align-items:center;gap:36px;font:200 90px Inter;color:{AZ}}} .flechas span:nth-child(2){{font:700 24px Inter;letter-spacing:8px;color:{INK}}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:500px;z-index:55;pointer-events:none;background:linear-gradient(rgba(242,244,247,0.97) 55%, rgba(242,244,247,0))}}
#marca{{position:absolute;left:0;right:0;top:1820px;text-align:center;font:600 26px Inter;color:{INK};opacity:0.3;pointer-events:none;z-index:61}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 58px Inter;color:rgba(30,39,51,0.28);line-height:1.22}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:3px solid {AZ};border-radius:6px;background:rgba(46,107,255,0.12);opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="cam"><svg width="{W}" height="1920" viewBox="0 0 {W} 1920" style="position:absolute;left:0;top:0;overflow:visible"><defs>{"".join(DEFS)}</defs>{svg}</svg></div>
  <div id="topsombra"></div>
  <div id="fxl">{"".join(FXL)}</div>
  <div id="marca">@mundo.supuesto</div>
  <div id="subs" data-layout-allow-overlap>{"".join(SUBS)}</div>
  <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
tl.set("#cam", {{transformOrigin:"0 0"}}, 0);
{chr(10).join(tl)}
tl.to({{}}, {{duration:0.01}}, {DUR - 0.01});
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>"""
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump(FX, open(os.path.join(BASE, "efectos.json"), "w"))
json.dump([[0, 0.0], [DUR, 0.0]], open(os.path.join(BASE, "ambiente.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones")

#!/usr/bin/env python3
"""«¿Qué pasaría si te dejasen caer desde 1.000 m dentro de una burbuja?» — v5 informativa, UN SOLO PLANO CONTINUO.
La cámara sigue a la burbuja todo el rato (sin cortes ni transiciones): el mundo pasa a su alrededor (nubes, horizonte,
suelo) y los datos aparecen junto a ella. Persona con arnés dentro, luz de sol lateral, decorado completo.
  python3 gen.py → index.html + efectos.json"""
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
tl, FX, DEFS, OVR = [], [], [], []
def J(s): tl.append(s)
CY, RJ, AM, VE, TX, MU = "#4fd1ff", "#ff5a4f", "#ffc24a", "#35d987", "#eef4fb", "#9fb3c8"
BX, BY, R = 540, 860, 230                 # la burbuja SIEMPRE en el mismo sitio de la pantalla (la cámara la sigue)
SUELO = BY + R                            # altura del suelo en pantalla en el momento del impacto
rnd = random.Random(7)

# ------------------------------------------------------------------ tiempos clave
T_SUELTA = P("suelta")
T_IMPACTO = P("impacto")
T_CIEN = P("cien")
T_SUELO_VE = T_CIEN - 0.2                 # el suelo empieza a asomar
T_REVIENTA = P("reviente")
CAIDA = T_IMPACTO - T_SUELTA

def entra(sel, t, frm="opacity:0, y:24", d=0.4, ease="power3.out"):
    J(f'tl.set("{sel}", {{opacity:0}}, 0); tl.fromTo("{sel}", {{{frm}}}, {{opacity:1, x:0, y:0, scale:1, duration:{d}, ease:"{ease}", immediateRender:false}}, {t:.2f});')
def sale(sel, t, d=0.3):
    J(f'tl.to("{sel}", {{opacity:0, duration:{d}, ease:"power1.in"}}, {t:.2f});')
def dibuja(sel, t, d=0.6, ease="power2.inOut"):
    J(f'tl.set("{sel}", {{strokeDasharray:1, strokeDashoffset:1}}, 0); tl.to("{sel}", {{strokeDashoffset:0, duration:{d}, ease:"{ease}"}}, {t:.2f});')
def contador(cid, t, v0, v1, d=0.8, ease="power2.out", fmt="int"):
    o = f"c_{cid}_{len(tl)}"
    f = "String(Math.round(o.v)).replace(/\\B(?=(\\d{3})+(?!\\d))/g, '.')"
    J(f'const {o} = {{v:{v0}}}; tl.to({o}, {{v:{v1}, duration:{max(0.05, d):.2f}, ease:"{ease}", onUpdate:() => {{ document.getElementById("{cid}").textContent = {f.replace("o.", o + ".")}; }}}}, {t:.2f});')

# ------------------------------------------------------------------ degradados y luz
DEFS += [
    '<linearGradient id="cieloA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#081733"/><stop offset="0.45" stop-color="#1b4278"/><stop offset="0.8" stop-color="#4f86b8"/><stop offset="1" stop-color="#9fc3dc"/></linearGradient>',
    '<linearGradient id="cieloB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a5f96"/><stop offset="0.5" stop-color="#5f98c6"/><stop offset="1" stop-color="#d7e8f0"/></linearGradient>',
    '<radialGradient id="solG" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff6d8"/><stop offset="0.12" stop-color="#ffe7a8" stop-opacity="0.95"/><stop offset="0.35" stop-color="#ffd27a" stop-opacity="0.35"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient>',
    '<radialGradient id="vidrio" cx="0.36" cy="0.3" r="0.8"><stop offset="0" stop-color="#ffffff" stop-opacity="0.20"/><stop offset="0.5" stop-color="#bfe6ff" stop-opacity="0.07"/><stop offset="0.86" stop-color="#7cc4f2" stop-opacity="0.22"/><stop offset="1" stop-color="#e2f5ff" stop-opacity="0.62"/></radialGradient>',
    '<radialGradient id="sombraInt" cx="0.66" cy="0.72" r="0.6"><stop offset="0.55" stop-color="#0a1f3a" stop-opacity="0"/><stop offset="1" stop-color="#0a1f3a" stop-opacity="0.35"/></radialGradient>',
    '<linearGradient id="borde" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff3d6"/><stop offset="0.45" stop-color="#d6f0ff" stop-opacity="0.7"/><stop offset="1" stop-color="#6fb6e8" stop-opacity="0.6"/></linearGradient>',
    '<linearGradient id="nubeG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="0.6" stop-color="#eef4fa"/><stop offset="1" stop-color="#b9cde0"/></linearGradient>',
    '<linearGradient id="hierba" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5f9a4c"/><stop offset="0.25" stop-color="#3f7a3a"/><stop offset="1" stop-color="#1e3d22"/></linearGradient>',
    '<linearGradient id="campo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fae86"/><stop offset="1" stop-color="#4a7a48"/></linearGradient>',
    '<linearGradient id="camiseta" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#e2604a"/><stop offset="1" stop-color="#a8392b"/></linearGradient>',
    '<linearGradient id="piel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f0c7a2"/><stop offset="1" stop-color="#c68c63"/></linearGradient>',
    '<linearGradient id="heliG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3c536e"/><stop offset="1" stop-color="#121c29"/></linearGradient>',
    '<radialGradient id="haloRojo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ff5a4f" stop-opacity="0.55"/><stop offset="1" stop-color="#ff5a4f" stop-opacity="0"/></radialGradient>',
    '<radialGradient id="rx" cx="0.5" cy="0.45" r="0.6"><stop offset="0" stop-color="#0f2a44"/><stop offset="1" stop-color="#040b14"/></radialGradient>',
    '<clipPath id="lente"><circle r="225"/></clipPath>',
]

# ------------------------------------------------------------------ piezas
def nube(x, y, s, op=1.0):
    k = rnd.Random() if False else rnd
    bolas = [(-120, 10, 70), (-50, -30, 90), (40, -45, 105), (130, -10, 80), (190, 20, 55), (-180, 30, 45), (60, 15, 90)]
    c = "".join(f'<circle cx="{bx}" cy="{by}" r="{br}"/>' for bx, by, br in bolas)
    return (f'<g transform="translate({x:.0f},{y:.0f}) scale({s:.2f})" opacity="{op:.2f}">'
            f'<g fill="url(#nubeG)">{c}<rect x="-225" y="15" width="460" height="60" rx="30"/></g>'
            f'<path d="M-225,62 Q0,92 235,62 L235,75 L-225,75 Z" fill="#9fb6cc" opacity="0.5"/></g>')

def helicoptero():
    return ('<g transform="translate(540,600)"><g id="heli"><g transform="scale(0.62)">'
            '<path d="M-150,-30 L150,-30 M-110,-30 L-90,-62 M110,-30 L90,-62" stroke="#0d1520" stroke-width="10" stroke-linecap="round"/>'
            '<path d="M-200,-150 L-560,-170 L-560,-150 L-200,-110 Z" fill="url(#heliG)"/><path d="M-560,-170 L-610,-250 L-575,-250 L-540,-160 Z" fill="#22324a"/>'
            '<path d="M-180,-62 Q-235,-62 -235,-135 Q-235,-238 -100,-242 L110,-242 Q200,-236 225,-150 Q232,-70 150,-62 Z" fill="url(#heliG)"/>'
            '<path d="M-200,-200 Q-120,-236 40,-238" stroke="#ffe7b0" stroke-width="6" fill="none" opacity="0.45" stroke-linecap="round"/>'
            '<path d="M60,-226 L120,-226 Q195,-220 214,-150 L214,-118 L60,-118 Z" fill="#2c4a6b"/><path d="M80,-220 L140,-130" stroke="#ffffff" stroke-width="8" opacity="0.18"/>'
            '<rect x="-12" y="-272" width="24" height="32" fill="#0d1520"/>'
            '<ellipse class="rotor" cx="0" cy="-276" rx="470" ry="12" fill="#cfdbe8" opacity="0.35"/>'
            '<circle class="baliza" cx="-90" cy="-60" r="9" fill="#ff5a4f"/>'
            '<path d="M0,-62 L0,0" stroke="#5b6b80" stroke-width="7"/><circle id="gancho" cy="0" r="10" fill="#7b8ba0"/></g></g></g>')

def persona():
    """Adulto sentado en el arnés (rodillas flexionadas, brazos agarrando las cintas). Luz desde arriba a la izquierda."""
    return ('<g id="persona">'
            # piernas (vaqueros) y zapatillas
            '<path d="M-22,8 L-78,40 L-96,104 M22,8 L78,40 L96,104" stroke="#2c4566" stroke-width="34" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            '<path d="M-22,8 L-78,40 M22,8 L78,40" stroke="#3d5b84" stroke-width="12" fill="none" stroke-linecap="round" transform="translate(-4,-8)"/>'
            '<path d="M-112,104 L-80,104 Q-74,118 -86,120 L-114,120 Q-122,112 -112,104 Z M80,104 L112,104 Q122,112 114,120 L86,120 Q74,118 80,104 Z" fill="#f2f4f7"/>'
            '<path d="M-114,120 L-86,120 M86,120 L114,120" stroke="#9aa7b6" stroke-width="5"/>'
            # torso (camiseta) y cinturón del arnés
            '<path d="M-52,-118 Q-60,-60 -40,14 L40,14 Q60,-60 52,-118 Q0,-132 -52,-118 Z" fill="url(#camiseta)"/>'
            '<path d="M-40,-60 Q0,-48 40,-60" stroke="#8d2e22" stroke-width="3" fill="none" opacity="0.5"/>'
            '<rect x="-46" y="-2" width="92" height="16" rx="6" fill="#1b2430"/><rect x="-10" y="-2" width="20" height="16" rx="3" fill="#c9d3de"/>'
            '<path d="M-34,-118 L-28,-2 M34,-118 L28,-2" stroke="#1b2430" stroke-width="9"/>'
            # brazos (manga + antebrazo) agarrando las cintas
            '<path d="M-48,-110 L-104,-82" stroke="url(#camiseta)" stroke-width="30" stroke-linecap="round"/><path d="M48,-110 L104,-82" stroke="#a8392b" stroke-width="30" stroke-linecap="round"/>'
            '<path d="M-104,-82 L-146,-140 M104,-82 L146,-140" stroke="url(#piel)" stroke-width="22" fill="none" stroke-linecap="round"/>'
            '<circle cx="-148" cy="-144" r="15" fill="#e6b28b"/><circle cx="148" cy="-144" r="15" fill="#c68c63"/>'
            # cuello y cabeza
            '<rect x="-13" y="-148" width="26" height="30" fill="#c68c63"/>'
            '<ellipse cx="0" cy="-182" rx="33" ry="40" fill="url(#piel)"/>'
            '<path d="M-34,-190 Q-38,-232 0,-230 Q38,-232 34,-192 Q30,-212 0,-212 Q-24,-212 -34,-190 Z" fill="#3a2a20"/>'
            '<ellipse cx="-34" cy="-180" rx="6" ry="10" fill="#d89f78"/><ellipse cx="34" cy="-180" rx="6" ry="10" fill="#b87d56"/>'
            '<path d="M-20,-192 L-8,-194 M8,-194 L20,-192" stroke="#3a2a20" stroke-width="4" stroke-linecap="round"/>'
            '<ellipse cx="-13" cy="-182" rx="4" ry="5" fill="#1d1d24"/><ellipse cx="13" cy="-182" rx="4" ry="5" fill="#1d1d24"/>'
            '<path d="M0,-178 L-4,-166 L3,-166" stroke="#a87250" stroke-width="3" fill="none"/>'
            '<path id="boca" d="M-10,-155 Q0,-152 10,-155" stroke="#7a3b2c" stroke-width="4" fill="none" stroke-linecap="round"/>'
            '</g>')

def rayosx():
    """Capa de rayos X sobre el torso de la persona (se enciende por partes)."""
    return ('<g id="rxP" opacity="0">'
            '<path d="M-52,-118 Q-60,-60 -40,14 L40,14 Q60,-60 52,-118 Q0,-132 -52,-118 Z" fill="#06111d" opacity="0.85"/>'
            '<g id="rxCos">' + "".join(f'<path d="M0,{-108 + i * 15} Q-44,{-118 + i * 15} -46,{-92 + i * 15} M0,{-108 + i * 15} Q44,{-118 + i * 15} 46,{-92 + i * 15}" stroke="#e8f4ff" stroke-width="4" fill="none" stroke-linecap="round"/>' for i in range(6)) + '</g>'
            '<g id="rxCol"><path d="M0,-146 L0,12" stroke="#e8f4ff" stroke-width="7" stroke-dasharray="8 3"/></g>'
            '<g id="rxOrg"><ellipse cx="-22" cy="-78" rx="15" ry="26" fill="#ff8a8a" opacity="0.45"/><ellipse cx="22" cy="-78" rx="15" ry="26" fill="#ff8a8a" opacity="0.45"/><path d="M4,-74 C-10,-88 -22,-70 -6,-58 L4,-50 L14,-58 C28,-70 18,-88 4,-74 Z" fill="#ff5a4f" opacity="0.8"/></g>'
            '</g>')

def burbuja():
    cintas = "".join(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="#e7ecf2" stroke-width="7" stroke-linecap="round" opacity="0.9"/>'
                     for x1, y1, x2, y2 in ((-148, -144, -178, -146), (148, -144, 178, -146), (-34, -112, -120, -194), (34, -112, 120, -194),
                                            (-40, 8, -200, 70), (40, 8, 200, 70), (-96, 104, -130, 172), (96, 104, 130, 172)))
    anclas = "".join(f'<circle cx="{x}" cy="{y}" r="9" fill="#c9d3de" stroke="#7b8ba0" stroke-width="3"/>' for x, y in ((-178, -146), (178, -146), (-120, -194), (120, -194), (-200, 70), (200, 70), (-130, 172), (130, 172)))
    costuras = (f'<ellipse rx="{R - 4}" ry="{R * 0.28:.0f}" fill="none" stroke="#d6f0ff" stroke-width="2" opacity="0.35"/>'
                f'<ellipse rx="{R * 0.32:.0f}" ry="{R - 4}" fill="none" stroke="#d6f0ff" stroke-width="2" opacity="0.25"/>')
    return (f'<g transform="translate({BX},{BY})"><g id="balanceo">'
            f'<ellipse cx="0" cy="{R + 6}" rx="{R * 0.8:.0f}" ry="18" fill="#000" opacity="0" id="sombraSuelo"/>'
            f'<g id="burCuerpo">'
            f'<circle r="{R}" fill="#0b2340" opacity="0.18" id="fondoBur"/>'
            f'<g id="interior">{costuras}{cintas}{anclas}<g id="caidaP">{persona()}{rayosx()}</g></g>'
            f'<circle r="{R}" fill="url(#vidrio)"/><circle r="{R}" fill="url(#sombraInt)"/>'
            f'<circle r="{R}" fill="none" stroke="url(#borde)" stroke-width="5"/>'
            f'<path d="M{-R * 0.74:.0f},{-R * 0.36:.0f} A{R * 0.82:.0f},{R * 0.82:.0f} 0 0 1 {-R * 0.22:.0f},{-R * 0.8:.0f}" stroke="#ffffff" stroke-width="12" fill="none" stroke-linecap="round" opacity="0.55"/>'
            f'<ellipse cx="{-R * 0.48:.0f}" cy="{-R * 0.58:.0f}" rx="22" ry="11" fill="#fffbe8" opacity="0.85" transform="rotate(-38 {-R * 0.48:.0f} {-R * 0.58:.0f})"/>'
            f'<path d="M{R * 0.55:.0f},{R * 0.62:.0f} A{R * 0.85:.0f},{R * 0.85:.0f} 0 0 0 {R * 0.86:.0f},{R * 0.1:.0f}" stroke="#bfe6ff" stroke-width="5" fill="none" opacity="0.45" stroke-linecap="round"/>'
            f'<g id="grietas" opacity="0">' + "".join(f'<path d="M{dx0},{R - 4} L{dx},{dy} L{dx2},{dy2}" stroke="#ffffff" stroke-width="3" fill="none"/>' for dx0, dx, dy, dx2, dy2 in ((-40, -110, 140, -170, 90), (20, 70, 150, 150, 120), (60, 160, 120, 210, 40), (-90, -190, 100, -215, 20))) + '</g>'
            f'</g></g>'
            f'<g id="trozos" opacity="0">' + "".join(f'<g transform="translate({R * math.cos(a):.0f},{R * math.sin(a):.0f}) rotate({math.degrees(a):.0f})"><path class="trozo" d="M-34,-5 L28,-13 L40,4 L-18,12 Z" fill="#d6f0ff" fill-opacity="0.35" stroke="#eef9ff" stroke-width="3"/></g>' for a in [i * 2 * math.pi / 18 for i in range(18)]) + '</g>'
            f'</g>')

# ------------------------------------------------------------------ MUNDO (todo se mueve alrededor de la burbuja)
lejos = (  # horizonte lejano: montañas, campos y un pueblo visto desde muy arriba
    '<g id="lejos"><g transform="translate(0,1640)">'
    '<path d="M-200,0 L-60,-70 L60,-30 L200,-110 L330,-40 L470,-95 L620,-20 L760,-120 L900,-50 L1040,-100 L1280,-10 L1280,40 L-200,40 Z" fill="#6f8fb2" opacity="0.8"/>'
    '<path d="M-200,10 L0,-30 L180,5 L380,-45 L560,0 L760,-35 L980,8 L1280,-25 L1280,60 L-200,60 Z" fill="#5d7f8f"/>'
    '<rect x="-200" y="40" width="1480" height="900" fill="url(#campo)"/>'
    + "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}" opacity="0.55"/>' for x, y, w, h, c in
              [(rnd.randint(-150, 1100), rnd.randint(60, 600), rnd.randint(80, 240), rnd.randint(14, 60), rnd.choice(["#a9b86b", "#6e9a58", "#c2b27a", "#57864d"])) for _ in range(40)])
    + '<path d="M540,40 L380,900 M540,40 L760,900 M-200,220 L1280,160" stroke="#cfd6cf" stroke-width="5" opacity="0.6"/>'
    + "".join(f'<rect x="{500 + rnd.randint(-120, 160)}" y="{70 + rnd.randint(0, 90)}" width="{rnd.randint(8, 16)}" height="{rnd.randint(6, 12)}" fill="#e6e1d6"/>' for _ in range(40))
    + '</g></g>')
nubes_atras, nubes_delante = [], []
y = 1480
while y < 15000:
    nubes_atras.append(nube(rnd.uniform(-60, 1140), y, rnd.uniform(0.45, 1.1), rnd.uniform(0.7, 0.95)))
    if rnd.random() < 0.35:
        nubes_delante.append(nube(rnd.choice([rnd.uniform(-180, 200), rnd.uniform(880, 1260)]), y + rnd.uniform(-200, 200), rnd.uniform(0.8, 1.2), 0.8))
    y += rnd.uniform(420, 820)
pajaros = "".join(f'<path d="M{x},{yy} q14,-12 28,0 q14,-12 28,0" stroke="#1a2a3c" stroke-width="4" fill="none" stroke-linecap="round"/>' for x, yy in ((80, 0), (130, 30), (40, 40), (180, 55), (10, 80)))
estelas = "".join(f'<path d="M{rnd.uniform(20, 1060):.0f},{yy:.0f} l0,{rnd.uniform(90, 260):.0f}" stroke="#eaf4ff" stroke-width="{rnd.uniform(2, 4):.1f}" opacity="{rnd.uniform(0.25, 0.6):.2f}" stroke-linecap="round"/>' for yy in [rnd.uniform(0, 1920) for _ in range(40)])
cerca = (  # suelo cercano: parque con árboles, farola, valla y una casa de dos plantas al fondo
    f'<g id="cerca"><g transform="translate(0,{SUELO})">'
    '<path d="M-200,-40 L1280,-40 L1280,0 L-200,0 Z" fill="#7aa3c0" opacity="0.4"/>'
    '<g id="casa"><rect x="780" y="-330" width="230" height="330" fill="#d9d2c4"/><rect x="780" y="-330" width="40" height="330" fill="#bfb6a6"/>'
    '<path d="M760,-330 L895,-420 L1030,-330 Z" fill="#9b4a3a"/><path d="M760,-330 L895,-420 L895,-405 L780,-326 Z" fill="#b8604c"/>'
    + "".join(f'<rect x="{x}" y="{yy}" width="52" height="62" fill="#4d7090"/><rect x="{x}" y="{yy}" width="52" height="8" fill="#ffffff" opacity="0.5"/>' for x in (830, 930) for yy in (-300, -150))
    + '<rect x="880" y="-80" width="40" height="80" fill="#5a3e2e"/></g>'
    + "".join(f'<g transform="translate({x},0)"><rect x="-9" y="-{h * 0.45:.0f}" width="18" height="{h * 0.45:.0f}" fill="#5a4030"/><circle cy="-{h * 0.62:.0f}" r="{h * 0.3:.0f}" fill="#3d7a3c"/><circle cx="-{h * 0.12:.0f}" cy="-{h * 0.7:.0f}" r="{h * 0.2:.0f}" fill="#5d9a4f"/></g>' for x, h in ((80, 260), (200, 200), (690, 230), (1050, 210)))
    + '<g transform="translate(300,0)"><rect x="-5" y="-260" width="10" height="260" fill="#2d3a48"/><path d="M0,-260 Q30,-270 46,-250" stroke="#2d3a48" stroke-width="8" fill="none"/><rect x="34" y="-252" width="26" height="10" fill="#fff3c4"/></g>'
    + "".join(f'<rect x="{x}" y="-60" width="8" height="60" fill="#e9e4da"/>' for x in range(-20, 1100, 40)) + '<rect x="-20" y="-52" width="1120" height="7" fill="#e9e4da"/><rect x="-20" y="-28" width="1120" height="7" fill="#e9e4da"/>'
    + '<rect x="-200" y="0" width="1480" height="1200" fill="url(#hierba)"/>'
    + '<path d="M-200,300 Q300,230 640,260 Q900,285 1280,220 L1280,330 Q900,390 640,360 Q300,330 -200,420 Z" fill="#cbb994" opacity="0.85"/>'
    + "".join(f'<circle cx="{rnd.randint(-20, 1100)}" cy="{rnd.randint(40, 700)}" r="{rnd.randint(4, 8)}" fill="{rnd.choice(["#f4e27a", "#ffffff", "#f29bb0", "#c9a7ff"])}"/>' for _ in range(70))
    + "".join(f'<ellipse cx="{rnd.randint(-20, 1100)}" cy="{rnd.randint(60, 760)}" rx="{rnd.randint(30, 70)}" ry="{rnd.randint(8, 16)}" fill="#2f6233" opacity="0.5"/>' for _ in range(25))
    + "".join(f'<path d="M{x},2 l4,-14 l4,14" stroke="#7bb563" stroke-width="3" fill="none"/>' for x in range(-10, 1100, 26))
    + '</g></g>')

svg = (f'<rect width="1080" height="1920" fill="url(#cieloA)"/><rect id="cieloB" width="1080" height="1920" fill="url(#cieloB)" opacity="0"/>'
       f'<g id="sol"><circle cx="150" cy="330" r="330" fill="url(#solG)"/><circle cx="150" cy="330" r="46" fill="#fffaf0"/></g>'
       f'{lejos}<g id="nubesA">{"".join(nubes_atras)}</g>'
       f'<g transform="translate(-300,1500)"><g id="pajaros">{pajaros}</g></g>'
       f'{cerca}'
       f'<g id="estelas" opacity="0">{estelas}<g transform="translate(0,1920)">{estelas}</g></g>'
       f'{helicoptero()}<path id="cable" d="M540,600 L540,{BY - R}" stroke="#aebdcc" stroke-width="5"/>'
       f'{burbuja()}' + f'<g id="tumbada" opacity="0" transform="translate(0,{SUELO})">'
       '<ellipse cx="560" cy="6" rx="230" ry="14" fill="#000" opacity="0.25"/>'
       '<path d="M600,-26 L680,-58 L748,-20 M600,-18 L672,-22 L752,-12" stroke="#2c4566" stroke-width="30" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
       '<path d="M744,-36 L774,-30 Q780,-18 770,-14 L742,-14 Z M748,-26 L782,-20 Q788,-6 776,-2 L746,-4 Z" fill="#f2f4f7"/>'
       '<rect x="452" y="-62" width="156" height="58" rx="24" fill="url(#camiseta)"/><rect x="590" y="-62" width="16" height="58" fill="#1b2430"/>'
       '<path d="M478,-40 L430,-12 L384,-10" stroke="url(#piel)" stroke-width="20" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
       '<rect x="436" y="-46" width="22" height="24" fill="#c68c63"/>'
       '<ellipse cx="412" cy="-40" rx="38" ry="33" fill="url(#piel)"/><path d="M376,-46 Q380,-82 420,-74 Q404,-60 392,-30 Z" fill="#3a2a20"/>'
       '<path d="M402,-50 L414,-50 M402,-34 L414,-34" stroke="#3a2a20" stroke-width="4" stroke-linecap="round"/>'
       '</g>' + ''
       f'<g id="nubesB">{"".join(nubes_delante)}</g>'
       # guías y cotas dibujadas (aparecen con la voz)
       f'<g id="cotaD" opacity="0"><path pathLength="1" id="cotaDl" d="M{BX - R},{BY + R + 40} L{BX + R},{BY + R + 40}" stroke="{CY}" stroke-width="4"/>'
       f'<path d="M{BX - R},{BY + R + 22} L{BX - R},{BY + R + 58} M{BX + R},{BY + R + 22} L{BX + R},{BY + R + 58}" stroke="{CY}" stroke-width="4"/></g>'
       f'<g id="flechaAire" opacity="0"><path d="M{BX},{BY - R - 12} L{BX},{BY - R - 120}" stroke="{CY}" stroke-width="14" stroke-linecap="round"/><path d="M{BX - 26},{BY - R - 104} L{BX},{BY - R - 148} L{BX + 26},{BY - R - 104} Z" fill="{CY}"/></g>'
       f'<g id="giro" opacity="0"><path d="M{BX - R - 50},{BY - 60} A{R + 50},{R + 50} 0 0 1 {BX - 60},{BY - R - 50}" stroke="{AM}" stroke-width="9" fill="none" stroke-linecap="round"/><path d="M{BX - 78},{BY - R - 72} L{BX - 40},{BY - R - 50} L{BX - 80},{BY - R - 26} Z" fill="{AM}"/>'
       f'<path d="M{BX + R + 50},{BY + 60} A{R + 50},{R + 50} 0 0 1 {BX + 60},{BY + R + 50}" stroke="{AM}" stroke-width="9" fill="none" stroke-linecap="round"/><path d="M{BX + 78},{BY + R + 72} L{BX + 40},{BY + R + 50} L{BX + 80},{BY + R + 26} Z" fill="{AM}"/></g>'
       f'<g id="cota40" opacity="0"><path id="cota40l" pathLength="1" d="M{BX + 150},{BY + 104} L{BX + 150},{SUELO}" stroke="{RJ}" stroke-width="5"/><path d="M{BX + 132},{BY + 104} L{BX + 168},{BY + 104} M{BX + 132},{SUELO} L{BX + 168},{SUELO}" stroke="{RJ}" stroke-width="5"/></g>'
       f'<g id="cota6" opacity="0"><path id="cota6l" pathLength="1" d="M752,{SUELO} L752,{SUELO - 420}" stroke="{CY}" stroke-width="5"/><path d="M734,{SUELO} L770,{SUELO} M734,{SUELO - 420} L770,{SUELO - 420}" stroke="{CY}" stroke-width="5"/></g>'
       f'<g id="lineaMil" opacity="0"><path id="lineaMilL" pathLength="1" d="M{BX},{BY + R + 10} L{BX},1700" stroke="{RJ}" stroke-width="4" stroke-dasharray="14 12"/></g>'
       # lupa de rayos X unida al pecho
       f'<g id="lupa" opacity="0"><path id="lupaL" pathLength="1" d="M{BX + 20},{BY - 60} L{BX + 120},1300" stroke="{TX}" stroke-width="3" opacity="0.8"/>'
       f'<g transform="translate({BX},1520)"><circle r="232" fill="#ffffff" opacity="0.9"/><g clip-path="url(#lente)"><rect x="-240" y="-240" width="480" height="480" fill="url(#rx)"/>'
       '<g transform="translate(0,50) scale(2.2)">'
       '<path d="M-52,-118 Q-60,-60 -40,14 L40,14 Q60,-60 52,-118 Q0,-132 -52,-118 Z" fill="#9fd4ff" opacity="0.08" stroke="#9fd4ff" stroke-width="1.5"/>'
       '<g id="LxCos">' + "".join(f'<path d="M0,{-108 + i * 15} Q-44,{-118 + i * 15} -46,{-92 + i * 15} M0,{-108 + i * 15} Q44,{-118 + i * 15} 46,{-92 + i * 15}" stroke="#e8f4ff" stroke-width="3" fill="none" stroke-linecap="round"/>' for i in range(7)) + '</g>'
       '<g id="LxCol"><path d="M0,-150 L0,14" stroke="#e8f4ff" stroke-width="6" stroke-dasharray="7 2.5"/></g>'
       '<g id="LxOrg"><ellipse cx="-22" cy="-78" rx="15" ry="26" fill="#ff8a8a" opacity="0.35"/><ellipse cx="22" cy="-78" rx="15" ry="26" fill="#ff8a8a" opacity="0.35"/><path d="M4,-74 C-10,-88 -22,-70 -6,-58 L4,-50 L14,-58 C28,-70 18,-88 4,-74 Z" fill="#ff5a4f" opacity="0.7"/></g>'
       '</g></g><circle r="228" fill="none" stroke="#ffffff" stroke-width="7"/></g></g>'
       )

# ------------------------------------------------------------------ textos (HTML) junto a la burbuja
OVR.append(f'''
<div class="gran" id="hook"><b>1.000 m</b><small>SIN PARACAÍDAS</small></div>
<div class="etq" id="eDiam" style="left:0;right:0;top:{BY + R + 64}px;text-align:center"><b>Ø 1,5 m</b></div>
<div class="etq der" id="ePeso" style="left:{BX + R + 26}px;top:{BY - 60}px"><b>≈ 12 kg</b><small>BURBUJA</small></div>
<div class="etq izq" id="eArnes" style="right:{1080 - BX + R + 26}px;top:{BY + 30}px;text-align:right"><b>ARNÉS</b><small>ATADO DENTRO</small></div>
<div class="gran rojo" id="eLibre" style="top:{BY + R + 70}px"><b style="font-size:110px">CAÍDA LIBRE</b></div>
<div class="gran" id="eVel" style="top:{BY + R + 60}px"><b><span id="velN">0</span><i>km/h</i></b><small id="velL1">EN 3 SEGUNDOS</small><small id="velL2">VELOCIDAD MÁXIMA</small></div>
<div class="fila" id="eFila" style="top:{BY + R + 330}px"><div><small>ALTITUD</small><b><span id="altN">1.000</span> m</b></div><div id="filaT"><small>TIEMPO</small><b><span id="tN">0</span> s</b></div></div>
<div class="chip" id="eCor" style="left:40px;top:{BY - 220}px"><svg width="58" height="52" viewBox="-60 -60 120 110"><path id="corazon" d="M0,45 C-75,0 -50,-62 0,-30 C50,-62 75,0 0,45 Z" fill="#ff5a4f"/></svg><div><b><span id="bpmN">72</span></b><small>PULSACIONES</small></div></div>
<div class="etq" id="eAire" style="left:{BX + 30}px;top:{BY - R - 150}px"><small style="font-size:26px">RESISTENCIA DEL AIRE</small></div>
<div class="chip ama" id="eMareo" style="left:40px;top:{BY - 40}px"><div><b style="font-size:40px">MAREO</b></div></div>
<div class="chip ama" id="eNausea" style="left:40px;top:{BY + 60}px"><div><b style="font-size:40px">NÁUSEAS</b></div></div>
<div class="aviso" id="eCien" style="top:{BY + R + 70}px"><b>100 m</b><small>MENOS DE 3 SEGUNDOS</small></div>
<div class="etq rojo" id="e40" style="left:{BX + 110}px;top:{SUELO + 40}px"><b>≈ 40 cm</b><small>DE AIRE</small></div>
<div class="duo" id="eG" style="top:{SUELO + 90}px"><div id="g200"><b>≈ <span id="gN">0</span> g</b><small>EL FRENAZO</small></div><div id="g45"><b>45 g</b><small>LÍMITE HUMANO</small></div></div>
<div class="etq rojo" id="xCos" style="left:{BX + 250}px;top:1330px"><b style="font-size:40px">COSTILLAS</b></div>
<div class="etq rojo" id="xCol" style="left:{BX + 250}px;top:1490px"><b style="font-size:40px">COLUMNA</b></div>
<div class="etq rojo" id="xOrg" style="left:{BX + 250}px;top:1650px"><b style="font-size:40px">ÓRGANOS</b></div>
<div class="gran rojo" id="eRev" style="top:{SUELO + 110}px"><b style="font-size:96px">REVIENTA</b></div>
<div class="etq" id="e6" style="right:60px;top:{SUELO - 560}px;text-align:right"><b>≈ 6 m</b><small>AQUÍ SÍ PROTEGE</small></div>
<div class="cierre" id="cA" style="top:{SUELO + 120}px">NO CAMBIA EL RESULTADO.</div>
<div class="cierre fuerte" id="cB" style="top:{SUELO + 250}px">SOLO LO RETRASA.</div>
''')

# ================================================================== ANIMACIÓN
# cámara: un único plano, empuje muy lento y continuo
J(f'tl.fromTo("#cam", {{scale:1.0}}, {{scale:1.05, duration:{DUR:.2f}, ease:"none", immediateRender:false}}, 0);')
# helicóptero: rotor y baliza
J(f'tl.fromTo(".rotor", {{scaleX:1}}, {{scaleX:0.25, transformOrigin:"50% 50%", duration:0.05, yoyo:true, repeat:{int(DUR / 0.05)}, ease:"none", immediateRender:false}}, 0);')
J(f'tl.fromTo(".baliza", {{opacity:1}}, {{opacity:0.15, duration:0.45, yoyo:true, repeat:{int(DUR / 0.45)}, ease:"steps(1)", immediateRender:false}}, 0);')

# 1) GANCHO — desde el fotograma 0: la burbuja colgando, «1.000 m» enorme, y a «suelo» una línea roja hasta abajo
J(f'tl.fromTo("#balanceo", {{rotation:-3}}, {{rotation:3, svgOrigin:"0 {-R - 260}", duration:1.4, yoyo:true, repeat:{int(T_SUELTA / 1.4)}, ease:"sine.inOut", immediateRender:false}}, 0);')
J(f'tl.fromTo("#heli", {{y:0}}, {{y:-10, duration:1.1, yoyo:true, repeat:{int(T_SUELTA / 1.1)}, ease:"sine.inOut", immediateRender:false}}, 0);')
J('tl.set("#hook", {opacity:1}, 0);')
J(f'tl.set("#lineaMil", {{opacity:1}}, {P("suelo") - 0.3:.2f});'); dibuja("#lineaMilL", P("suelo") - 0.3, 0.6)
J(f'tl.fromTo("#persona", {{y:0}}, {{y:-3, duration:1.6, yoyo:true, repeat:{int((T_REVIENTA - 2) / 1.6) // 2 * 2 + 1}, ease:"sine.inOut", immediateRender:false}}, 0);')   # respira
sale("#hook", F(2) - 0.1); sale("#lineaMil", F(2) - 0.1)

# 2) LA BURBUJA: Ø 1,5 m · 12 kg · arnés
J(f'tl.set("#cotaD", {{opacity:1}}, {P("metro") - 0.3:.2f});'); dibuja("#cotaDl", P("metro") - 0.3, 0.5)
entra("#eDiam", P("metro"))
entra("#ePeso", P("doce") - 0.2, "opacity:0, x:-20")
entra("#eArnes", P("arnes") - 0.3, "opacity:0, x:20")
J(f'tl.to("#interior path[stroke=\'#e7ecf2\']", {{stroke:"{AM}", duration:0.2, yoyo:true, repeat:3}}, {P("arnes") - 0.3:.2f});')
for s_ in ("#cotaD", "#eDiam", "#ePeso", "#eArnes"):
    sale(s_, F(3) - 0.1)

# 3) SUELTA EL CABLE → caída libre. El helicóptero y el cable se quedan arriba (la cámara sigue a la burbuja)
J(f'tl.set("#cable", {{attr:{{d:"M540,600 L540,{BY - R}"}}}}, 0); tl.to("#cable", {{attr:{{d:"M540,600 L540,640"}}, duration:0.12}}, {T_SUELTA:.2f});')
J(f'tl.to("#heli, #cable", {{y:-1300, duration:3.0, ease:"power2.in"}}, {T_SUELTA + 0.1:.2f});')
J(f'tl.to("#balanceo", {{rotation:0, duration:0.4}}, {T_SUELTA:.2f});')
entra("#eLibre", P("caida") - 0.1)
sale("#eLibre", F(4) - 0.05)
FX.append(("whoosh", T_SUELTA))
# el mundo sube: nubes (dos capas), horizonte y estelas de aire; acelera ~6 s y luego velocidad constante
A1, D1 = 6.0, 1500
VEL = 2 * D1 / A1                      # px/s a velocidad máxima
resto = CAIDA - A1
for sel, fac in (("#nubesA", 1.0), ("#nubesB", 1.6)):
    J(f'tl.to("{sel}", {{y:{-D1 * fac:.0f}, duration:{A1}, ease:"power2.in"}}, {T_SUELTA:.2f}); tl.to("{sel}", {{y:{-(D1 + VEL * resto) * fac:.0f}, duration:{resto:.2f}, ease:"none"}}, {T_SUELTA + A1:.2f});')
J(f'tl.to("#lejos", {{y:-420, duration:{CAIDA:.2f}, ease:"power1.in"}}, {T_SUELTA:.2f});')
J(f'tl.to("#cieloB", {{opacity:1, duration:{CAIDA:.2f}, ease:"power1.in"}}, {T_SUELTA:.2f});')
J(f'tl.to("#sol", {{y:-260, duration:{CAIDA:.2f}, ease:"none"}}, {T_SUELTA:.2f});')
J(f'tl.to("#estelas", {{opacity:0.9, duration:{A1}, ease:"power1.in"}}, {T_SUELTA:.2f}); tl.to("#estelas", {{opacity:0, duration:0.15}}, {T_IMPACTO:.2f});')
per = 0.35
J(f'tl.fromTo("#estelas", {{y:0}}, {{y:-1920, duration:{per}, ease:"none", repeat:{int(CAIDA / per) + 1}, immediateRender:false}}, {T_SUELTA:.2f});')
J(f'tl.fromTo("#pajaros", {{x:0, y:0}}, {{x:1700, y:-2600, duration:4.5, ease:"none", immediateRender:false}}, {F(6) + 1.0:.2f});')
# suelo cercano: aparece a «cien metros» y llega justo en el impacto
J(f'tl.set("#cerca", {{y:3200}}, 0); tl.fromTo("#cerca", {{y:2900}}, {{y:0, duration:{T_IMPACTO - T_SUELO_VE:.2f}, ease:"none", immediateRender:false}}, {T_SUELO_VE:.2f});')

# lecturas: altitud y tiempo (desde que la sueltan hasta el impacto)
entra("#eFila", T_SUELTA + 0.4)
contador("altN", T_SUELTA, 1000, 900, A1, "power2.in")
contador("altN", T_SUELTA + A1, 900, 100, T_CIEN - T_SUELTA - A1, "none")
contador("altN", T_CIEN, 100, 0, T_IMPACTO - T_CIEN, "none")
contador("tN", T_SUELTA, 0, 28, CAIDA, "none")
sale("#eFila", T_IMPACTO - 0.05, 0.15)

# 4) 90 km/h en 3 s
entra("#eVel", F(4) - 0.1)
contador("velN", F(4), 0, 90, P("noventa") - F(4) + 0.2, "power1.in")
J('tl.set("#velL2", {opacity:0}, 0);')

# 5) corazón
entra("#eCor", F(5) - 0.1, "opacity:0, x:-30")
contador("bpmN", P("dispara") - 0.2, 72, 155, P("pulsaciones") - P("dispara") + 0.3, "power2.in")
J(f'tl.fromTo("#corazon", {{scale:1}}, {{scale:1.18, transformOrigin:"50% 50%", duration:0.2, yoyo:true, repeat:{int((F(7) - F(5)) / 0.2)}, ease:"power2.out", immediateRender:false}}, {F(5):.2f});')
FX.append(("latido", F(5) + 0.2))
sale("#eCor", F(7) - 0.1)

# 6) el aire frena · velocidad máxima ≈ 140
J(f'tl.set("#flechaAire", {{opacity:0}}, 0); tl.fromTo("#flechaAire", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.4, immediateRender:false}}, {P("frena") - 0.2:.2f});')
entra("#eAire", P("frena") - 0.1, "opacity:0")
J(f'tl.to("#velL1", {{opacity:0, duration:0.2}}, {P("estabiliza") - 0.2:.2f}); tl.to("#velL2", {{opacity:1, duration:0.2}}, {P("estabiliza"):.2f});')
contador("velN", F(6) + 0.3, 90, 140, P("cuarenta") - F(6), "power2.out")
sale("#flechaAire", F(7) - 0.1); sale("#eAire", F(7) - 0.1)

# 7) gira sin control: el interior (persona y cintas) gira, la luz del plástico se queda fija
GIRO0 = P("girar") - 0.4
J(f'tl.fromTo("#interior", {{rotation:0}}, {{rotation:-1080, svgOrigin:"0 0", duration:{T_IMPACTO - GIRO0:.2f}, ease:"power1.inOut", immediateRender:false}}, {GIRO0:.2f});')
J(f'tl.set("#giro", {{opacity:0}}, 0); tl.to("#giro", {{opacity:1, duration:0.3}}, {GIRO0:.2f}); tl.fromTo("#giro", {{rotation:0}}, {{rotation:-360, svgOrigin:"{BX} {BY}", duration:4, ease:"none", immediateRender:false}}, {GIRO0:.2f});')
sale("#giro", F(8) - 0.1)
entra("#eMareo", P("orientacion") - 0.3, "opacity:0, x:-30")
entra("#eNausea", P("nauseas") - 0.2, "opacity:0, x:-30")
sale("#eMareo", F(9) - 0.2); sale("#eNausea", F(9) - 0.2)

# 8) 28 segundos: se resalta el tiempo
J(f'tl.to("#filaT", {{color:"{AM}", scale:1.12, transformOrigin:"50% 50%", duration:0.3}}, {P("veintiocho") - 0.2:.2f}); tl.to("#filaT", {{scale:1, duration:0.3}}, {F(9) - 0.2:.2f});')

# 9) a 100 m: aviso rojo, aparece el suelo
sale("#eVel", T_CIEN - 0.3, 0.2)
entra("#eCien", T_CIEN - 0.1, "opacity:0, scale:1.2")
J(f'tl.to("#eFila", {{color:"{RJ}", duration:0.2}}, {T_CIEN:.2f});')
sale("#eCien", T_IMPACTO - 0.2, 0.15)

# 10) IMPACTO: aplastamiento, sacudida y 40 cm de aire
J(f'tl.to("#burCuerpo", {{scaleY:0.86, scaleX:1.1, svgOrigin:"0 {R}", duration:0.08, ease:"power2.out"}}, {T_IMPACTO:.2f}); tl.to("#burCuerpo", {{scaleY:1, scaleX:1, svgOrigin:"0 {R}", duration:0.5, ease:"elastic.out(1,0.4)"}}, {T_IMPACTO + 0.08:.2f});')
J(f'tl.fromTo("#cam", {{x:0, y:0}}, {{x:14, y:-10, duration:0.05, yoyo:true, repeat:7, ease:"none", immediateRender:false}}, {T_IMPACTO:.2f}); tl.set("#cam", {{x:0, y:0}}, {T_IMPACTO + 0.42:.2f});')
J(f'tl.set("#sombraSuelo", {{opacity:0}}, 0); tl.to("#sombraSuelo", {{opacity:0.35, duration:0.1}}, {T_IMPACTO - 0.1:.2f});')
J(f'tl.fromTo("#flash", {{opacity:0.7}}, {{opacity:0, duration:0.35, immediateRender:false}}, {T_IMPACTO:.2f}); tl.set("#flash", {{opacity:0}}, 0);')
FX.append(("golpe", T_IMPACTO))
J(f'tl.set("#cota40", {{opacity:1}}, {P("cuarenta", 2) - 0.4:.2f});'); dibuja("#cota40l", P("cuarenta", 2) - 0.4, 0.4)
entra("#e40", P("cuarenta", 2) - 0.1, "opacity:0, x:-20")
sale("#cota40", F(12) - 0.1); sale("#e40", F(12) - 0.1)

# 11-12) 200 g frente a 45 g
entra("#eG", P("doscientas") - 0.4)
J('tl.set("#g45", {opacity:0}, 0);')
contador("gN", P("doscientas") - 0.4, 0, 200, 0.9, "power3.out")
entra("#g45", P("cinco") - 0.2, "opacity:0, y:20")
J(f'tl.fromTo("#g200", {{scale:1}}, {{scale:1.08, transformOrigin:"50% 50%", duration:0.25, yoyo:true, repeat:1, immediateRender:false}}, {P("instante") - 0.2:.2f});')
sale("#eG", F(13) - 0.1)

# 13) lesiones: rayos X sobre la persona + lupa ampliada
J(f'tl.to("#rxP", {{opacity:1, duration:0.3}}, {F(13) - 0.05:.2f}); tl.to("#lupa", {{opacity:1, duration:0.3}}, {F(13) - 0.05:.2f});'); dibuja("#lupaL", F(13) - 0.05, 0.3)
for parte, lx, et, w in (("Cos", "LxCos", "xCos", "costillas"), ("Col", "LxCol", "xCol", "columna"), ("Org", "LxOrg", "xOrg", "organos")):
    J(f'tl.to("#rx{parte} *, #{lx} *", {{stroke:"{RJ}", fill:"{RJ}", fillOpacity:0.9, duration:0.15}}, {P(w) - 0.1:.2f});')
    J(f'tl.fromTo("#{lx}", {{opacity:1}}, {{opacity:0.4, duration:0.1, yoyo:true, repeat:3, immediateRender:false}}, {P(w) - 0.1:.2f});')
    entra(f"#{et}", P(w) - 0.1, "opacity:0, x:-20", 0.3)
J(f'tl.set("#rxCos *, #LxCos *, #rxOrg *, #LxOrg *", {{fillOpacity:0}}, 0);')
for s_ in ("#lupa", "#xCos", "#xCol", "#xOrg"):
    sale(s_, F(14) - 0.1)
J(f'tl.to("#rxP", {{opacity:0, duration:0.3}}, {F(14) - 0.1:.2f});')

# 14) el plástico no aguanta y revienta
J(f'tl.to("#burCuerpo", {{scaleY:0.9, scaleX:1.06, svgOrigin:"0 {R}", duration:{T_REVIENTA - P("aguante"):.2f}, ease:"power2.in"}}, {P("aguante") - 0.1:.2f});')
J(f'tl.to("#grietas", {{opacity:1, duration:0.1}}, {P("aguante") + 0.2:.2f});')
J(f'tl.set("#vidrioTodo", {{opacity:1}}, 0);')
J(f'tl.to("#burCuerpo > circle, #burCuerpo > path, #burCuerpo > ellipse, #grietas, #interior > ellipse, #interior > circle, #interior > path", {{opacity:0, duration:0.08}}, {T_REVIENTA:.2f});')
J(f'tl.set("#trozos", {{opacity:1}}, {T_REVIENTA:.2f}); tl.fromTo(".trozo", {{x:0, y:0, rotation:0}}, {{x:(i) => Math.cos(i * 0.35) * 320, y:(i) => Math.sin(i * 0.35) * 260 - 120, rotation:(i) => (i % 2 ? 1 : -1) * 160, transformOrigin:"50% 50%", opacity:0, duration:1.3, ease:"power3.out", immediateRender:false}}, {T_REVIENTA:.2f});')
J(f'tl.to("#caidaP", {{y:110, duration:0.25, ease:"power2.in"}}, {T_REVIENTA + 0.05:.2f}); tl.to("#caidaP", {{opacity:0, duration:0.2}}, {T_REVIENTA + 0.3:.2f}); tl.to("#tumbada", {{opacity:1, duration:0.2}}, {T_REVIENTA + 0.3:.2f});')
J(f'tl.fromTo("#flash", {{opacity:0.5}}, {{opacity:0, duration:0.3, immediateRender:false}}, {T_REVIENTA:.2f});')
entra("#eRev", T_REVIENTA - 0.1, "opacity:0, scale:1.15")
sale("#eRev", F(15) - 0.1)
FX.append(("rompe", T_REVIENTA))

# 15) 6 m: la casa de dos plantas del fondo
J(f'tl.set("#cota6", {{opacity:1}}, {P("seis") - 0.4:.2f});'); dibuja("#cota6l", P("seis") - 0.4, 0.5)
entra("#e6", P("seis") - 0.1, "opacity:0, x:20")
J(f'tl.to("#casa", {{opacity:1, duration:0.2}}, 0);')
sale("#cota6", F(16) - 0.1); sale("#e6", F(16) - 0.1)

# 16) cierre seco
entra("#cA", P("resultado") - 0.3, "opacity:0, y:20", 0.5)
entra("#cB", P("retrasa") - 0.2, "opacity:0, y:20", 0.5)
tfin = FE(16) + 0.55
J(f'tl.set("#negroF", {{opacity:0}}, 0); tl.to("#negroF", {{opacity:1, duration:0.45}}, {tfin:.2f});')
FX.append(("final", tfin))

# ------------------------------------------------------------------ subtítulos (arriba, palabra a palabra, recuadro azul en lo importante)
CLAVE = set(norm(w) for w in ["mil", "plastico", "suelo", "metro", "doce", "arnes", "libre", "noventa", "cincuenta", "cuarenta", "esfera", "orientacion",
                               "nauseas", "veintiocho", "cien", "impacto", "centimetros", "doscientas", "gravedad", "costillas", "columna", "organos",
                               "reviente", "seis", "resultado", "retrasa"])
DEBIL = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "y", "a", "en", "con", "que", "por", "tu", "se", "lo", "no", "solo", "esa"}
chunks, cur = [], []
for p in T["palabras"]:
    cur.append(p)
    txt = " ".join(x["w"] for x in cur)
    fin_frase = re.search(r"[.:;?!…]$", p["w"])
    if fin_frase or ((len(cur) >= 5 or len(txt) >= 28) and norm(p["w"]) not in DEBIL) or len(cur) >= 7:
        chunks.append(cur); cur = []
if cur:
    chunks.append(cur)
SUBS = []
for k, ch in enumerate(chunks):
    st = ch[0]["ini"] - 0.05
    en = chunks[k + 1][0]["ini"] - 0.05 if k + 1 < len(chunks) else min(DUR, ch[-1]["fin"] + 0.6)
    spans = []
    for j, p in enumerate(ch):
        wid = f"w{k}_{j}"
        if norm(p["w"]) in CLAVE:
            spans.append(f'<span id="{wid}" class="sw key"><i class="hl"></i>{p["w"]}</span>')
            J(f'tl.to("#{wid} .hl", {{opacity:1, duration:0.06}}, {p["ini"]:.2f});')
        else:
            spans.append(f'<span id="{wid}" class="sw">{p["w"]}</span>')
        J(f'tl.to("#{wid}", {{color:"#ffffff", duration:0.06}}, {p["ini"]:.2f});')
    SUBS.append(f'<div id="sub{k}" class="clip sub" data-start="{max(0, st):.3f}" data-duration="{max(0.2, en - max(0, st)):.3f}" data-track-index="3">{" ".join(spans)}</div>')
r3 = random.Random(3)
for s_ in range(int(DUR / 0.08)):
    J(f'tl.set("#grano", {{backgroundPosition:"{r3.randint(0, 360)}px {r3.randint(0, 360)}px"}}, {s_ * 0.08:.2f});')

html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#03060c}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;background:#03060c;color:{TX}}}
#cam{{position:absolute;inset:0;transform-origin:{BX}px {BY}px}}
.gran{{position:absolute;left:0;right:0;top:{BY + R + 50}px;text-align:center;white-space:nowrap;text-shadow:0 6px 24px rgba(0,10,25,0.55)}}
.gran b{{display:block;font:800 170px/1 Inter;letter-spacing:-6px;color:#fff;font-variant-numeric:tabular-nums}} .gran b i{{font-style:normal;font-size:64px;letter-spacing:0;margin-left:14px;color:{CY}}}
.gran small{{display:block;margin-top:10px;font:800 30px Inter;letter-spacing:7px;color:#fff}} .gran.rojo b{{color:{RJ}}}
#eVel small{{position:absolute;left:0;right:0;top:182px}}
.etq{{position:absolute;white-space:nowrap;text-shadow:0 4px 16px rgba(0,10,25,0.6)}} .etq b{{display:block;font:800 64px/1 Inter;letter-spacing:-2px;color:#fff}} .etq small{{display:block;margin-top:8px;font:800 24px Inter;letter-spacing:5px;color:{CY}}}
.etq.rojo b{{color:{RJ}}} .etq.rojo small{{color:#ffd0cb}}
.fila{{position:absolute;left:0;right:0;display:flex;justify-content:center;gap:26px}} .fila div{{min-width:250px;padding:12px 22px;border-radius:14px;background:rgba(6,14,28,0.62);border:1px solid rgba(255,255,255,0.18);text-align:center}}
.fila small{{display:block;font:800 22px Inter;letter-spacing:5px;color:#b9c9da}} .fila b{{font:800 52px Inter;font-variant-numeric:tabular-nums}}
.chip{{position:absolute;display:flex;align-items:center;gap:14px;padding:14px 22px;border-radius:16px;background:rgba(6,14,28,0.7);border:1px solid rgba(255,255,255,0.2)}}
.chip b{{display:block;font:800 56px/1 Inter;color:#fff;font-variant-numeric:tabular-nums}} .chip small{{display:block;margin-top:4px;font:800 18px Inter;letter-spacing:4px;color:#ffb3ad}}
.chip.ama{{border-left:6px solid {AM}}}
.aviso{{position:absolute;left:0;right:0;text-align:center}} .aviso b{{display:block;font:800 150px/1 Inter;letter-spacing:-5px;color:{RJ};text-shadow:0 6px 24px rgba(0,0,0,0.5)}} .aviso small{{display:block;margin-top:10px;font:800 30px Inter;letter-spacing:6px;color:#fff}}
.duo{{position:absolute;left:0;right:0;display:flex;justify-content:center;gap:70px;text-align:center}} .duo b{{display:block;font:800 120px/1 Inter;letter-spacing:-4px;font-variant-numeric:tabular-nums}} .duo small{{display:block;margin-top:10px;font:800 26px Inter;letter-spacing:5px;color:#fff}}
#g200 b{{color:{RJ}}} #g45 b{{color:{VE}}}
.cierre{{position:absolute;left:60px;right:60px;padding:12px 0;border-radius:18px;background:rgba(4,10,20,0.72);text-align:center;font:800 66px/1.1 Inter;letter-spacing:-1px;color:#fff;text-shadow:0 6px 24px rgba(0,0,0,0.6)}} .cierre.fuerte{{color:{RJ};font-size:96px}}
#flash{{position:absolute;inset:0;z-index:50;background:#fff;opacity:0;pointer-events:none}}
#negroF{{position:absolute;inset:0;z-index:69;background:#000;pointer-events:none}}
#grano{{position:absolute;inset:0;z-index:57;pointer-events:none;opacity:0.035;background:url(assets/grano.png);mix-blend-mode:overlay}}
#vineta{{position:absolute;inset:0;z-index:56;pointer-events:none;background:radial-gradient(115% 85% at 50% 48%, rgba(0,0,0,0) 58%, rgba(0,0,0,0.5))}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:560px;z-index:55;pointer-events:none;background:linear-gradient(rgba(2,6,14,0.78), rgba(2,6,14,0))}}
#marca{{position:absolute;left:0;right:0;top:1775px;text-align:center;font:700 28px Inter;color:#ffffff;opacity:0.32;pointer-events:none;z-index:61}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 62px Inter;color:rgba(255,255,255,0.42);line-height:1.22;text-shadow:0 3px 12px rgba(0,0,0,0.6)}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:3px solid #4ea3ff;border-radius:6px;background:rgba(78,163,255,0.18);opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="cam"><svg width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0;overflow:visible"><defs>{"".join(DEFS)}</defs>{svg}</svg>
  {"".join(OVR)}</div>
  <div id="flash"></div>
  <div id="topsombra"></div><div id="vineta"></div><div id="grano"></div>
  <div id="marca">@mundo.supuesto</div>
  <div id="subs" data-layout-allow-overlap>{"".join(SUBS)}</div>
  <div id="negroF"></div>
  <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tl)}
tl.to({{}}, {{duration:0.01}}, {DUR - 0.01});
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>"""
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump(FX, open(os.path.join(BASE, "efectos.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones · caída {CAIDA:.1f}s")

#!/usr/bin/env python3
"""«¿Qué pasaría si cada vez que parpadearas crecieras 0,001 mm?» v2 — UN SOLO PLANO que sigue al protagonista.
Jardín con vecino → crece día a día → se tumba y (lo más probable) muere → «imagina que no mueres»: crece durante
80 años junto a la Torre de Pisa, el Big Ben, la Torre Eiffel y el Empire State → vuelve al ojo (bucle).
La cámara se aleja a la vez que él crece: él siempre ocupa lo mismo en pantalla y el mundo se encoge. Sin efectos.
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
rr = random.Random(7)

# ------------------------------------------------------------------ personajes (189 u = 1,75 m)
U = 189 / 1.75
PROTA = dict(piel="#e8b896", pelo="#3b2a20", camisa="#3d7cc9", pantalon="#2f3640", zapato="#f4f4f4")
VECINO = dict(piel="#c98e6b", pelo="#1d1d1d", camisa="#e07a3f", pantalon="#3b4a6b", zapato="#2b2b2b")
GRIS = dict(piel="#b9c0c8", pelo="#9aa3ad", camisa="#a9b1ba", pantalon="#8e97a1", zapato="#9aa3ad")
def figura(pid, col):
    s = rig(pid, col).replace('cy="84"', 'cy="92"')
    for lado in ("N", "F"):
        s = s.replace(f'<g id="{pid}_sh{lado}">', f'<g id="{pid}_sh{lado}">' + "§SH§", 1)
    parts = s.split("§SH§"); out = parts[0]
    for p in parts[1:]:
        k = p.index('<g transform="translate(41,0)">')
        out += (p[:k] + f'<rect class="{pid}tob" x="27" y="-5.6" width="14.5" height="11.2" fill="{col["piel"]}" opacity="0"/>'
                + f'<path class="{pid}dolor" d="M2,-5 L39,-4 L39,4 L2,5 Z" fill="#ff4b3e" opacity="0"/>' + p[k:])
    return re.sub(rf'(<g id="{pid}_th[NF]">)(.*?)(<g transform="translate\(43,0\)">)',
                  lambda m: m.group(1) + m.group(2) + f'<path class="{pid}dolor" d="M2,-7 L41,-6 L41,6 L2,7 Z" fill="#ff4b3e" opacity="0"/>' + m.group(3), out, flags=re.S)

# ------------------------------------------------------------------ mundo
M = []
# montañas lejanas (solo se ven cuando él es gigante)
for x0, w, hh, col in ((-150000, 90000, 30000, "#c5dcec"), (-90000, 70000, 22000, "#bcd6e8"), (40000, 80000, 26000, "#c5dcec"), (90000, 90000, 34000, "#bcd6e8"),
                       (-60000, 50000, 14000, "#a9cbb0"), (30000, 60000, 16000, "#a9cbb0")):
    M.append(f'<path d="M{x0},0 Q{x0 + w * 0.3},{-hh} {x0 + w * 0.5},{-hh * 0.92} Q{x0 + w * 0.7},{-hh * 0.8} {x0 + w},0 Z" fill="{col}"/>')
M.append('<rect x="-300000" y="0" width="600000" height="300000" fill="#7cb85a"/>')
M.append('<rect x="-300000" y="0" width="600000" height="10" fill="#6aa64a"/>')
# ciudad: fila del fondo (edificios) y fila media (casas), lejos del jardín
COLB = ["#e9e2d3", "#dfe6ee", "#f3d9c4", "#d9e4d2", "#e6dcef"]
for k in range(140):
    lado = -1 if k % 2 else 1
    x = lado * (2600 + (k // 2) * 820 + rr.uniform(0, 400))
    hgt = rr.choice([2200, 3000, 4200, 5600, 7000]) if abs(x) > 9000 else rr.choice([1300, 1800, 2400])
    w = rr.uniform(700, 1300); c = rr.choice(COLB)
    M.append(f'<rect x="{x:.0f}" y="{-hgt}" width="{w:.0f}" height="{hgt}" fill="{c}"/>')
    for j in range(int(hgt / 420)):
        M.append(f'<rect x="{x + 110:.0f}" y="{-hgt + 160 + j * 420}" width="{w - 220:.0f}" height="150" fill="#9fc3dc" opacity="0.8"/>')
for k in range(120):
    lado = -1 if k % 2 else 1
    x = lado * (1450 + (k // 2) * 610 + rr.uniform(0, 200))
    w = rr.uniform(380, 520); hgt = rr.uniform(360, 520); c = rr.choice(["#f3ead8", "#f6efe2", "#efe3d0"]); t = rr.choice(["#c8664a", "#b5543b", "#7b8fa6"])
    M.append(f'<rect x="{x:.0f}" y="{-hgt:.0f}" width="{w:.0f}" height="{hgt:.0f}" fill="{c}"/><path d="M{x - 30:.0f},{-hgt:.0f} L{x + w / 2:.0f},{-hgt - 220:.0f} L{x + w + 30:.0f},{-hgt:.0f} Z" fill="{t}"/>'
             f'<rect x="{x + w * 0.2:.0f}" y="{-hgt * 0.7:.0f}" width="{w * 0.22:.0f}" height="{hgt * 0.28:.0f}" fill="#9fd3f0"/><rect x="{x + w * 0.58:.0f}" y="{-hgt * 0.7:.0f}" width="{w * 0.22:.0f}" height="{hgt * 0.28:.0f}" fill="#9fd3f0"/>')
    if k % 3 == 0:
        tx = x + w + 120
        M.append(f'<rect x="{tx - 18:.0f}" y="-300" width="36" height="300" fill="#8a5a3c"/><circle cx="{tx:.0f}" cy="-380" r="{rr.uniform(130, 190):.0f}" fill="{rr.choice(["#4f9a48", "#5aa752"])}"/>')
# jardín
M.append('<path d="M-60,0 L60,0 L220,3000 L-220,3000 Z" fill="#d8c9a6"/>')
for k in range(60):
    x = -1500 + k * 53 + (k * 37) % 23
    M.append(f'<path d="M{x},2 l3,-9 l3,9" fill="#5c9a3e"/>')
    if k % 4 == 1: M.append(f'<circle cx="{x + 9}" cy="-4" r="3.2" fill="{["#ffd23f", "#ff8fa3", "#ffffff"][k % 3]}"/>')
HX0, HX1, HW, HR = -620, -70, 560, 780
M.append(f'<rect x="{HX0}" y="{-HW}" width="{HX1 - HX0}" height="{HW}" fill="#f3ead8"/><rect x="{HX0}" y="{-HW}" width="{HX1 - HX0}" height="16" fill="#e2d6bd"/>')
M.append(f'<path d="M{HX0 - 40},{-HW} L{(HX0 + HX1) / 2},{-HR} L{HX1 + 40},{-HW} Z" fill="#c8664a"/><rect x="{HX0 + 330}" y="{-HR + 60}" width="50" height="120" fill="#a9553c"/>')
DX0, DX1, DH = -170, -82, 2.03 * U
M.append(f'<rect x="{DX0 - 8}" y="{-DH - 8}" width="{DX1 - DX0 + 16}" height="{DH + 8}" fill="#d9ccb1"/><rect x="{DX0}" y="{-DH}" width="{DX1 - DX0}" height="{DH}" fill="#7a4b32"/>'
         f'<rect x="{DX0 + 10}" y="{-DH + 14}" width="{DX1 - DX0 - 20}" height="70" fill="#6a3f29"/><rect x="{DX0 + 10}" y="{-DH + 98}" width="{DX1 - DX0 - 20}" height="90" fill="#6a3f29"/><circle cx="{DX1 - 14}" cy="{-DH / 2 + 6}" r="4" fill="#e9c46a"/>')
for wx, wy in ((-520, -460), (-360, -460), (-520, -250), (-360, -250)):
    M.append(f'<rect x="{wx}" y="{wy}" width="100" height="120" fill="#ffffff"/><rect x="{wx + 8}" y="{wy + 8}" width="84" height="104" fill="#9fd3f0"/><path d="M{wx + 50},{wy + 8} V{wy + 112} M{wx + 8},{wy + 60} H{wx + 92}" stroke="#ffffff" stroke-width="6"/>')
# coche aparcado (1,5 m) delante de la casa
M.append('<g transform="translate(-560,0)"><path d="M0,-40 Q0,-70 30,-74 L120,-80 Q160,-150 230,-152 L330,-150 Q380,-148 410,-86 L455,-78 Q470,-74 470,-46 L470,-24 L0,-24 Z" fill="#d94f45"/>'
         '<path d="M140,-84 Q170,-140 225,-142 L265,-142 L265,-84 Z M280,-142 L328,-140 Q362,-136 388,-84 L280,-84 Z" fill="#bfe4f7"/>'
         '<circle cx="95" cy="-24" r="32" fill="#2b2b2b"/><circle cx="95" cy="-24" r="14" fill="#c9c9c9"/><circle cx="375" cy="-24" r="32" fill="#2b2b2b"/><circle cx="375" cy="-24" r="14" fill="#c9c9c9"/></g>')
M.append('<rect x="-760" y="-430" width="10" height="430" fill="#3a4250"/><path d="M-755,-430 q0,-30 40,-30" stroke="#3a4250" stroke-width="8" fill="none"/><ellipse cx="-712" cy="-452" rx="16" ry="10" fill="#ffe7a3"/>')
for k in range(14):
    x = 560 + k * 46
    M.append(f'<rect x="{x}" y="-118" width="18" height="118" rx="3" fill="#ffffff"/><path d="M{x},-118 l9,-12 l9,12 Z" fill="#ffffff"/>')
M.append('<rect x="550" y="-92" width="660" height="12" fill="#f1f1f1"/><rect x="550" y="-46" width="660" height="12" fill="#f1f1f1"/>')
M.append('<rect x="860" y="-330" width="36" height="330" fill="#8a5a3c"/><circle cx="878" cy="-470" r="190" fill="#4f9a48"/><circle cx="770" cy="-390" r="120" fill="#5aa752"/><circle cx="990" cy="-400" r="130" fill="#5aa752"/><circle cx="900" cy="-560" r="110" fill="#67b25c"/>')
for bx in (-260, -330, 480, 1150):
    M.append(f'<ellipse cx="{bx}" cy="-24" rx="46" ry="34" fill="#4f9a48"/><ellipse cx="{bx + 28}" cy="-18" rx="34" ry="26" fill="#5aa752"/>')

# ------------------------------------------------------------------ monumentos a escala (aparecen con un fundido)
def pisa(x):
    h, w = 56 * U, 15.5 * U
    s = f'<g transform="translate({x},0) rotate(4)">'
    s += f'<rect x="{-w / 2}" y="{-h}" width="{w}" height="{h}" fill="#f1ebdd"/><rect x="{-w / 2}" y="{-h}" width="{w * 0.18}" height="{h}" fill="#000" opacity="0.06"/>'
    for k in range(1, 8):
        y = -h * k / 8.4
        s += f'<rect x="{-w / 2 - 60}" y="{y - 70}" width="{w + 120}" height="70" fill="#e2d9c4"/>'
        for a in range(6):
            ax = -w / 2 + 120 + a * (w - 240) / 5
            s += f'<path d="M{ax - 70},{y - 70} V{y - 520} Q{ax},{y - 640} {ax + 70},{y - 520} V{y - 70} Z" fill="#d6ccb4"/>'
    s += f'<rect x="{-w * 0.36}" y="{-h - 700}" width="{w * 0.72}" height="700" fill="#efe8d8"/><path d="M{-w * 0.4},{-h - 700} H{w * 0.4}" stroke="#d6ccb4" stroke-width="60"/>'
    return s + '</g>'
def bigben(x):
    h, w = 96 * U, 12 * U
    s = f'<g transform="translate({x},0)">'
    s += f'<rect x="{-w / 2}" y="{-h * 0.62}" width="{w}" height="{h * 0.62}" fill="#d9bc8c"/>'
    for k in range(10):
        s += f'<rect x="{-w / 2 + 90 + k * (w - 180) / 10}" y="{-h * 0.6}" width="40" height="{h * 0.58}" fill="#c4a473"/>'
    s += f'<rect x="{-w * 0.56}" y="{-h * 0.76}" width="{w * 1.12}" height="{h * 0.14}" fill="#d9bc8c"/><circle cx="0" cy="{-h * 0.69}" r="{w * 0.38}" fill="#fbf6e8" stroke="#3d3d3d" stroke-width="60"/>'
    s += f'<path d="M0,{-h * 0.69} l0,{-w * 0.28} M0,{-h * 0.69} l{w * 0.2},0" stroke="#222" stroke-width="70"/>'
    s += f'<rect x="{-w * 0.44}" y="{-h * 0.84}" width="{w * 0.88}" height="{h * 0.08}" fill="#c9a774"/><path d="M{-w * 0.44},{-h * 0.84} L0,{-h} L{w * 0.44},{-h * 0.84} Z" fill="#4b5d55"/>'
    return s + '</g>'
def eiffel(x):
    h, b = 330 * U, 125 * U / 2
    s = f'<g transform="translate({x},0)" fill="#9a6c45">'
    s += (f'<path d="M{-b},0 Q{-b * 0.55},{-h * 0.18} {-b * 0.42},{-h * 0.18} L{-b * 0.18},{-h * 0.36} Q{-b * 0.06},{-h * 0.62} {-b * 0.04},{-h * 0.84} L0,{-h} '
          f'L{b * 0.04},{-h * 0.84} Q{b * 0.06},{-h * 0.62} {b * 0.18},{-h * 0.36} L{b * 0.42},{-h * 0.18} Q{b * 0.55},{-h * 0.18} {b},0 '
          f'L{b * 0.62},0 Q{0},{-h * 0.2} {-b * 0.62},0 Z"/>')
    for yf, wf in ((0.17, 0.5), (0.35, 0.22), (0.835, 0.06)):
        s += f'<rect x="{-b * wf}" y="{-h * yf - 500}" width="{2 * b * wf}" height="900" fill="#7d5636"/>'
    s += f'<g stroke="#c49b70" stroke-width="160" opacity="0.5" fill="none">'
    for k in range(9):
        y0, y1 = -h * 0.02 * k * 2, -h * 0.02 * (k * 2 + 2)
        s += f'<path d="M{-b * (1 - 0.1 * k) * 0.7},{y0} L{b * (1 - 0.1 * k) * 0.25},{y1}"/>'
    return s + '</g></g>'
def empire(x):
    h = 381 * U; a = 443 * U
    s = f'<g transform="translate({x},0)">'
    for w, y0, y1 in ((60, 0, 0.18), (48, 0.18, 0.22), (38, 0.22, 0.86), (26, 0.86, 0.93), (16, 0.93, 1.0)):
        s += f'<rect x="{-w * U / 2}" y="{-h * y1}" width="{w * U}" height="{h * (y1 - y0) + 2}" fill="#b7c0ca"/><rect x="{w * U / 2 * 0.3}" y="{-h * y1}" width="{w * U / 2 * 0.7}" height="{h * (y1 - y0) + 2}" fill="#000" opacity="0.08"/>'
    for k in range(40):
        s += f'<rect x="{-16 * U}" y="{-h * 0.22 - k * h * 0.016}" width="{32 * U}" height="90" fill="#8fa3b6" opacity="0.6"/>'
    s += f'<path d="M{-5 * U},{-h} L0,{-h - 25 * U} L{5 * U},{-h} Z" fill="#c9d1da"/><rect x="-140" y="{-a}" width="280" height="{a - h - 20 * U}" fill="#c9d1da"/>'
    return s + '</g>'
MON = [("pisa", pisa(2600)), ("bigben", bigben(5600)), ("eiffel", eiffel(17000)), ("empire", empire(-15000))]
for n, svg in MON:
    M.append(f'<g id="m_{n}" opacity="0">{svg}</g>')
# nubes del mundo (a 280-350 m: le quedan por debajo de la cabeza al final)
for x, y, sc in ((-24000, -31000, 1.0), (-11000, -36000, 0.8), (18000, -33000, 1.1), (30000, -37500, 0.9)):
    M.append(f'<g opacity="0.9" transform="translate({x},{y}) scale({sc * 18})"><ellipse cx="0" cy="0" rx="130" ry="44" fill="#fff"/><ellipse cx="60" cy="-30" rx="80" ry="50" fill="#fff"/><ellipse cx="-50" cy="-18" rx="70" ry="40" fill="#fff"/></g>')
# avioneta (cruza en la parte gigante)
M.append('<g id="avion" opacity="0"><g transform="scale(16)"><path d="M-150,0 Q-140,-22 -60,-24 L120,-24 Q160,-24 170,-6 Q160,8 120,8 L-120,8 Q-150,6 -150,0 Z" fill="#ffffff"/>'
         '<path d="M-10,-6 L40,-6 L-10,60 L-40,60 Z" fill="#d7dee6"/><path d="M-130,-22 L-150,-70 L-120,-70 L-95,-24 Z" fill="#d94f45"/>'
         + "".join(f'<circle cx="{-70 + k * 26}" cy="-12" r="5" fill="#9fd3f0"/>' for k in range(7)) + '</g></g>')
# líneas de referencia
def linea(i, y, x0, x1):
    return f'<path id="ref{i}" d="M{x0},{-y} H{x1}" stroke="#ffffff" stroke-width="3" stroke-dasharray="10 8" vector-effect="non-scaling-stroke" opacity="0"/>'
M.append(linea("cama", 1.90 * U, -40, 120)); M.append(linea("puerta", DH, DX0 - 8, 120))
# Robert Wadlow (2,72 m), gris, mirando al protagonista
WAD = 2.72 / 1.75
M.append(f'<g id="wad" opacity="0"><g transform="translate(260,0) scale({-WAD:.3f},{WAD:.3f})"><g transform="translate(0,-92)">{figura("W", GRIS)}</g></g></g>')
# vecino (1,75 m) que le mira desde abajo; luego se va andando
M.append(f'<g id="vecMove"><g transform="translate(118,0)"><g id="vecFlip"><g transform="translate(0,-92)">{figura("V", VECINO)}</g></g></g></g>')

EXTRA_P = ('<g transform="translate(40,-172)"><g id="zz" opacity="0"><text x="0" y="0" font-family="Inter" font-weight="800" font-size="22" fill="#ffffff">Z</text>'
           '<text x="16" y="-20" font-family="Inter" font-weight="800" font-size="16" fill="#ffffff">z</text></g></g>'
           '<g id="lagrima" opacity="0"><path d="M30,-162 q-3,6 0,9 q3,-3 0,-9 Z" fill="#9fdcff"/></g>'
           '<ellipse id="sombraT" cx="95" cy="2" rx="100" ry="6" fill="#000" opacity="0"/>')
PROT = f'<g id="crece"><g id="tumbaT"><g id="tumba"><g id="sentar"><g transform="translate(0,-92)">{figura("P", PROTA)}</g></g></g></g>{EXTRA_P}</g>'
WORLD = "".join(M) + PROT

# ------------------------------------------------------------------ helpers
def h(t, metros, d, ease="power1.inOut"):
    J(f'tl.to(S, {{h:{metros}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
def cam(t, d=1.2, ease="power2.inOut", **kv):
    J(f'tl.to(S, {{{", ".join(f"{k}:{v}" for k, v in kv.items())}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
PARP = []; NB = [0]
def parpadeo(t, pop=False):
    PARP.append(t)
    J(f'tl.to("#P_ojo", {{scaleY:0.08, svgOrigin:"10 -24.6", duration:0.07, ease:"power1.in"}}, {t:.2f}); tl.to("#P_ojo", {{scaleY:1, svgOrigin:"10 -24.6", duration:0.09, ease:"power1.out"}}, {t + 0.09:.2f});')
    if pop:
        NB[0] += 1; i = NB[0]
        FXL.append(f'<div class="pop" id="pp{i}">+0,001 mm</div>')
        J(f'tl.set("#pp{i}", {{opacity:0}}, 0); tl.fromTo("#pp{i}", {{opacity:0, y:0}}, {{opacity:1, y:-60, duration:0.35, ease:"power2.out", immediateRender:false}}, {t + 0.05:.2f}); tl.to("#pp{i}", {{opacity:0, duration:0.4}}, {t + 0.9:.2f});')
NC = [0]
def card(html, t, hasta, top=700, left=40, w=360, cls=""):
    NC[0] += 1; i = NC[0]
    FXL.append(f'<div class="card {cls}" id="c{i}" style="top:{top}px;left:{left}px;width:{w}px">{html}</div>')
    J(f'tl.set("#c{i}", {{opacity:0}}, 0); tl.fromTo("#c{i}", {{opacity:0, x:-30}}, {{opacity:1, x:0, duration:0.45, ease:"power3.out", immediateRender:false}}, {t:.2f}); tl.to("#c{i}", {{opacity:0, x:-20, duration:0.3}}, {hasta:.2f});')
    return f"#c{i}"
def contador(sel, v0, v1, t, d, dec=0, suf=""):
    J(f'(() => {{ const o = {{v:{v0}}}; tl.to(o, {{v:{v1}, duration:{d:.2f}, ease:"power2.out", onUpdate:() => {{ document.querySelector("{sel}").textContent = fmt(o.v, {dec}) + "{suf}"; }}}}, {t:.2f}); }})();')
NL = [0]
def etiqueta(p, t, hasta, txt, dx=24, dy=-10):
    NL[0] += 1; i = NL[0]
    FXL.append(f'<div class="lab" id="lb{i}">{txt}</div>')
    J(f'LABS.push({{i:{i}, x:{p[0]:.1f}, y:{p[1]:.1f}, dx:{dx}, dy:{dy}}}); LV.l{i} = 0;')
    J(f'tl.to(LV, {{l{i}:1, duration:0.4}}, {t:.2f}); tl.to(LV, {{l{i}:0, duration:0.3}}, {hasta:.2f});')
def ref(nombre, t, hasta):
    J(f'tl.to("#ref{nombre}", {{opacity:0.9, duration:0.4}}, {t:.2f}); tl.to("#ref{nombre}", {{opacity:0, duration:0.4}}, {hasta:.2f});')
def monumento(n, t, hasta=None):
    J(f'tl.to("#m_{n}", {{opacity:1, duration:0.8}}, {t:.2f});')
def an(m):                      # altura a los «m» meses / años
    return 1.75 + 0.015 * m
YR = 0.015 * 365

# ------------------------------------------------------------------ GUION VISUAL
rset(J, "P", "pie"); rset(J, "W", "pie"); rset(J, "V", "pie")
J('tl.set("#vecFlip", {scaleX:-1, svgOrigin:"0 0"}, 0);')
# 1) gancho: el ojo + «0,001 mm»
FXL.append('<div id="gancho" class="grande"><b>0,001 mm</b><small>CADA VEZ QUE PARPADEAS</small></div>')
J(f'tl.to("#gancho", {{opacity:0, y:20, duration:0.4}}, {FE(1) - 0.1:.2f});')
parpadeo(P("parpadearas") + 0.1, pop=True)
# 2) «más alto que la Torre Eiffel… y mucho antes, te mataría»
cam(F(2) - 0.3, 2.4, "power2.inOut", ojo=0)
card('<small>ACABARÍAS MIDIENDO</small><b>330 m</b><em>más que la Torre Eiffel</em>', P("eiffel") - 0.4, P("antes") - 0.2)
card('<small>PERO MUCHO ANTES</small><b class="r">morirías</b>', P("antes") - 0.1, FE(2) + 0.4)
J(f'tl.to("#V_hd", {{rotation:-8, svgOrigin:"0 0", duration:0.6}}, {P("eiffel"):.2f});')
# 3) 15.000 parpadeos; ojos que arden
for t in (F(3) + 0.4, P("quince") - 0.1, P("dia") - 0.2):
    parpadeo(t, pop=True)
card('<small>PARPADEOS AL DÍA</small><b><span id="n15">0</span></b><em>sin darte cuenta</em>', P("quince") - 0.3, P("evitarlo"))
contador("#n15", 0, 15000, P("quince") - 0.2, 1.3)
cam(P("evitarlo") - 0.3, 1.2, ojo=0.55)
J(f'tl.to("#P_rojo", {{opacity:0.8, duration:1.0}}, {P("aguantas"):.2f}); tl.to("#P_rojo", {{opacity:0, duration:0.4}}, {FE(3) + 0.1:.2f});')
J(f'tl.fromTo("#lagrima", {{opacity:0, y:0}}, {{opacity:1, y:22, duration:1.0, ease:"power1.in", immediateRender:false}}, {P("arden") - 0.5:.2f}); tl.to("#lagrima", {{opacity:0, duration:0.2}}, {P("arden") + 0.6:.2f});')
card('<small>SIN PARPADEAR</small><b>ojos secos</b><em>arden en segundos</em>', P("aguantas") - 0.1, FE(3) + 0.2)
parpadeo(FE(3) + 0.05)
cam(FE(3) - 0.1, 1.2, ojo=0)
# 4) 1,5 cm al día; de noche no parpadeas
J(f'tl.to("#hud", {{opacity:1, y:0, duration:0.5, ease:"power3.out"}}, {F(4):.2f});')
h(F(4) + 0.3, an(1), 2.0)
card('<small>CRECES</small><b>1,5 cm</b><em>cada día</em>', P("centimetro") - 0.2, P("despierto") - 0.1)
J(f'tl.to("#noche", {{opacity:0.62, duration:0.6}}, {P("dormido") - 0.5:.2f}); tl.to("#noche", {{opacity:0, duration:0.6}}, {FE(4) + 0.1:.2f});')
J(f'tl.to("#estrellas", {{opacity:1, duration:0.6}}, {P("dormido") - 0.5:.2f}); tl.to("#estrellas", {{opacity:0, duration:0.6}}, {FE(4) + 0.1:.2f});')
J(f'tl.to("#P_ojo", {{scaleY:0.08, svgOrigin:"10 -24.6", duration:0.25}}, {P("dormido") - 0.4:.2f}); tl.to("#P_ojo", {{scaleY:1, svgOrigin:"10 -24.6", duration:0.2}}, {FE(4) + 0.1:.2f});')
J(f'tl.fromTo("#zz", {{opacity:0, y:0}}, {{opacity:1, y:-10, duration:0.6, immediateRender:false}}, {P("dormido") - 0.2:.2f}); tl.to("#zz", {{opacity:0, duration:0.3}}, {FE(4):.2f});')
card('<small>DORMIDO</small><b>0 parpadeos</b><em>no creces</em>', P("dormido") - 0.2, FE(4) + 0.1)
# 5-7) los días pasan (día/noche rápido): ropa corta, cama, puerta, 2,20 m
J(f'tl.to("#noche", {{opacity:0.32, duration:0.5, yoyo:true, repeat:{int((FE(7) - FE(4) - 0.8) / 0.5) // 2 * 2 - 1}, ease:"sine.inOut"}}, {FE(4) + 0.8:.2f});')
h(F(5), an(7), P("diez", 1) - F(5) - 0.3)
J(f'tl.to(".Ptob", {{opacity:1, duration:0.5}}, {P("ropa"):.2f});')
etiqueta((44, -6), P("ropa"), P("diez") - 0.2, "la ropa se queda corta", dx=40, dy=-80)
h(P("diez") - 0.3, an(10), FE(5) - P("diez") + 0.3)
ref("cama", P("diez") - 0.2, FE(5) + 0.5)
etiqueta((120, -1.90 * U), P("diez"), FE(5) + 0.5, "cama · 1,90 m", dx=12, dy=-44)
J(f'tl.to("#V_hd", {{rotation:-14, svgOrigin:"0 0", duration:1.5}}, {F(5) + 1:.2f});')
h(F(6), an(21), P("puerta") - F(6))
cam(F(6) - 0.2, 1.0, fx=-55)
ref("puerta", P("cabeza") - 0.4, FE(6) + 0.4)
etiqueta((120, -DH), P("cabeza") - 0.3, FE(6) + 0.4, "puerta · 2,03 m", dx=12, dy=-44)
J(f'tl.to("#P_hd", {{rotation:14, svgOrigin:"0 0", duration:0.3}}, {P("agachas") - 0.1:.2f}); tl.to("#P_hd", {{rotation:0, svgOrigin:"0 0", duration:0.4}}, {FE(6) + 0.2:.2f});')
cam(FE(6), 1.0, fx=0)
h(F(7), an(30), P("veinte") - F(7) + 0.3)
J(f'tl.to("#V_hd", {{rotation:-22, svgOrigin:"0 0", duration:1.2}}, {F(7):.2f});')
card('<small>1 MES</small><b>2,20 m</b>', P("mes") - 0.2, FE(7) + 0.2)
J(f'tl.to("#hud", {{scale:1.06, duration:0.25, yoyo:true, repeat:1}}, {P("problema") - 0.2:.2f});')
# 8) ley del cubo
CUBOS = ('<svg viewBox="0 0 300 120" width="320" height="128"><g fill="#4ea3ff" stroke="#ffffff" stroke-width="2"><rect x="10" y="70" width="40" height="40"/>'
         + "".join(f'<rect x="{110 + i * 40}" y="{30 + j * 40}" width="40" height="40" opacity="{0.55 + 0.45 * ((i + j) % 2)}"/>' for i in range(2) for j in range(2))
         + '</g><text x="200" y="65" font-family="Inter" font-weight="800" font-size="34" fill="#ffffff">→ ×8</text></svg>')
card(f'<small>SI MIDES EL DOBLE</small>{CUBOS}<div class="filas"><p id="f1">Altura <b>×2</b></p><p id="f2">Peso <b class="r">×8</b></p><p id="f3">Huesos <b>×4</b></p></div>', F(8) - 0.1, FE(8) + 0.3, top=640, w=380)
for k, w in enumerate(("duplica", "ocho", "cuatro"), 1):
    J(f'tl.set("#f{k}", {{opacity:0.25}}, 0); tl.to("#f{k}", {{opacity:1, duration:0.3}}, {P(w) - 0.15:.2f});')
J(f'tl.to(".Pdolor", {{opacity:0.35, duration:0.3, yoyo:true, repeat:1}}, {P("huesos") - 0.1:.2f});')
h(F(8), an(40), FE(8) - F(8))
# 9) Robert Wadlow
J(f'tl.to("#wad", {{opacity:0.92, duration:0.6}}, {P("wadlow") - 0.8:.2f}); tl.to("#wad", {{opacity:0, duration:0.6}}, {FE(9) + 0.3:.2f});')
h(F(9), 2.73, P("wadlow") + 0.3 - F(9)); h(P("wadlow") + 0.3, an(70), FE(9) - P("wadlow"))
cam(F(9) - 0.2, 1.4, fx=70, zm=0.82)
etiqueta((260, -2.72 * U), P("wadlow") - 0.4, FE(9) + 0.3, "Robert Wadlow · 2,72 m", dx=-120, dy=-50)
J(f'tl.to(".Wdolor", {{opacity:0.5, duration:0.4}}, {P("aparatos") - 0.2:.2f});')
J(f'tl.to("#V_hd", {{rotation:-32, svgOrigin:"0 0", duration:1.2}}, {F(9):.2f});')
cam(FE(9) + 0.1, 1.2, fx=0, zm=1)
# 10) cuatro meses: 3,55 m, +500 kg, piernas en rojo
h(F(10), an(120), P("tonelada") - F(10))
card('<small>4 MESES</small><b>3,55 m</b><em>+ de 500 kg</em>', P("cuatro", 2) - 0.2, P("ponerte") - 0.1)
J(f'tl.to(".Pdolor", {{opacity:0.55, duration:0.5}}, {P("ponerte") - 0.3:.2f}); tl.to(".Pdolor", {{opacity:0.25, duration:0.2, yoyo:true, repeat:5}}, {P("pierna") - 0.6:.2f}); tl.to(".Pdolor", {{opacity:0, duration:0.4}}, {FE(10) + 1.2:.2f});')
card('<small>CADA PASO</small><b class="r">riesgo de fractura</b>', P("ponerte") - 0.1, FE(10) + 0.2)
J(f'tl.to("#V_hd", {{rotation:-40, svgOrigin:"0 0", duration:1.2}}, {F(10):.2f});')
# 11) se tumba; el vecino se va
TB = P("tumbas") - 0.4
J(f'tl.to("#tumba", {{rotation:-90, svgOrigin:"0 0", duration:1.6, ease:"power2.inOut"}}, {TB:.2f}); tl.to("#tumbaT", {{x:189, y:-14, duration:1.6, ease:"power2.inOut"}}, {TB:.2f});')
J(f'tl.to("#P_sombra", {{opacity:0, duration:0.4}}, {TB:.2f}); tl.to("#sombraT", {{opacity:0.25, duration:0.8}}, {TB + 0.8:.2f});')
rpose(J, "P", "tumbado", TB, 1.6)
cam(TB, 1.6, lie=1)
J(f'tl.set("#vecFlip", {{scaleX:1, svgOrigin:"0 0"}}, {TB:.2f}); tl.to("#V_hd", {{rotation:0, svgOrigin:"0 0", duration:0.3}}, {TB:.2f});')
J(f'tl.to("#vecMove", {{x:1400, duration:4.5, ease:"none"}}, {TB + 0.1:.2f});')
for k in range(12):
    rpose(J, "V", "anda1" if k % 2 == 0 else "anda2", TB + 0.1 + k * 0.38, 0.38, "sine.inOut")
J(f'tl.to("#vecMove", {{opacity:0, duration:0.3}}, {TB + 4.4:.2f});')
# 12) seis meses: 4,45 m, más de una tonelada
h(F(12), an(180), FE(12) - F(12))
card('<small>6 MESES</small><b>4,45 m</b><em>+ de 1 tonelada</em>', P("seis") - 0.2, FE(12) + 0.2)
# 13-14) pulmones aplastados, como una ballena varada → lo más probable: morir antes del año
J(f'tl.to(S, {{gris:1, duration:2.2, ease:"power1.inOut"}}, {F(13):.2f});')
J(f'tl.to("#P_tor", {{scaleY:1.03, svgOrigin:"0 0", duration:1.3, yoyo:true, repeat:5, ease:"sine.inOut"}}, {F(13):.2f});')
BALLENA = ('<svg viewBox="0 0 320 120" width="320" height="120"><path d="M20,70 Q40,20 140,25 Q230,30 260,55 Q290,40 305,20 Q300,55 312,80 Q285,72 262,78 Q220,105 120,100 Q40,98 20,70 Z" fill="#8cc4ff"/>'
           '<circle cx="70" cy="58" r="5" fill="#0e1e34"/><path d="M0,104 H320" stroke="#e8d5a8" stroke-width="8"/></svg>')
card(f'<small>COMO UNA BALLENA VARADA</small>{BALLENA}<em>su propio peso le aplasta los pulmones</em>', P("ballena") - 0.5, FE(13) + 0.2, top=620, w=380)
ECG = ('<svg viewBox="0 0 340 90" width="340" height="90"><path id="ecg" d="M0,45 H60 L72,20 L84,70 L96,45 H170 L180,30 L190,58 L200,45 H340" stroke="#ff6b5e" stroke-width="5" fill="none" stroke-linejoin="round"/></svg>')
card(f'<small>LO MÁS PROBABLE</small><b>no llegarías al año</b>{ECG}', F(14) - 0.1, FE(14) + 0.5, top=620, w=380)
J(f'tl.fromTo("#ecg", {{strokeDasharray:"0 700"}}, {{strokeDasharray:"700 0", duration:2.6, ease:"none", immediateRender:false}}, {F(14):.2f});')
J(f'tl.to(S, {{gris:0, duration:1.4, ease:"power1.inOut"}}, {F(15) + 0.3:.2f});')
# 15) «imagina que no mueres»: se levanta y sigue creciendo
LV_ = P("aguanta") - 0.2
J(f'tl.to("#tumba", {{rotation:0, svgOrigin:"0 0", duration:1.6, ease:"power2.inOut"}}, {LV_:.2f}); tl.to("#tumbaT", {{x:0, y:0, duration:1.6, ease:"power2.inOut"}}, {LV_:.2f});')
rpose(J, "P", "pie", LV_, 1.6)
J(f'tl.to("#sombraT", {{opacity:0, duration:0.4}}, {LV_:.2f}); tl.to("#P_sombra", {{opacity:0.28, duration:0.6}}, {LV_ + 1.0:.2f});')
cam(LV_, 1.6, lie=0)
card('<small>SUPONGAMOS QUE</small><b>no mueres</b>', P("imagina") - 0.2, FE(15) + 0.2)
h(P("mueres") - 0.2, 1.75 + YR * 2, FE(15) - P("mueres") + 0.5)
# 16-19) años: Pisa, Big Ben, Torre Eiffel, Empire State
h(F(16), 1.75 + YR * 10, P("pisa") - F(16), "power2.inOut")
monumento("pisa", P("pisa") - 1.2)
etiqueta((2600, -56 * U - 900), P("pisa") - 0.3, FE(16) + 0.4, "Torre de Pisa · 56 m", dx=-130, dy=-50)
h(F(17), 1.75 + YR * 20, P("cuello") - F(17), "power2.inOut")
monumento("bigben", P("ben") - 1.2)
etiqueta((5600, -96 * U), P("ben") - 0.3, FE(17) + 0.4, "Big Ben · 96 m", dx=-100, dy=-50)
h(F(18), 1.75 + YR * 60, P("eiffel", 2) - F(18), "power2.inOut")
monumento("eiffel", P("eiffel", 2) - 1.4)
etiqueta((17000, -330 * U), P("eiffel", 2) - 0.3, FE(18) + 0.4, "Torre Eiffel · 330 m", dx=-130, dy=-50)
card('<small>PESARÍAS</small><b>470.000 t</b><em>más que 40 torres Eiffel</em>', P("pesarias") - 0.2, FE(18) + 0.3)
J(f'tl.fromTo("#avion", {{opacity:1, x:-36000, y:-17000}}, {{x:36000, y:-17600, duration:11, ease:"none", immediateRender:false}}, {F(18):.2f}); tl.set("#avion", {{opacity:0}}, {F(18) + 11:.2f});')
h(F(19), 1.75 + YR * 80, P("empire") - F(19), "power2.inOut")
monumento("empire", P("empire") - 1.4)
etiqueta((-15000, -443 * U), P("empire") - 0.3, FE(19) + 0.4, "Empire State · 443 m", dx=20, dy=-50)
cam(F(19) - 0.2, 2.0, fx=-20)
card('<small>80 AÑOS</small><b>440 m</b>', P("ochenta") - 0.2, FE(19) + 0.3)
J(f'tl.to("#hud", {{opacity:0, y:40, duration:0.5}}, {FE(19) + 0.3:.2f});')
# 20-22) vuelta al ojo (bucle)
cam(F(20) - 0.2, FE(20) - F(20) + 2.2, "power2.inOut", ojo=1, fx=0)
card('<small>MIENTRAS VEÍAS ESTE VÍDEO</small><b><span id="nv">0</span> parpadeos</b>', P("parpadeado") - 0.4, FE(21) + 0.2, top=1430, left=190, w=700, cls="centro")
FXL.append('<div id="final" class="grande"><b>+0,03 mm</b><small>Y ACABAS DE PARPADEAR</small></div>')
J(f'tl.set("#final", {{opacity:0}}, 0); tl.fromTo("#final", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.5, ease:"power3.out", immediateRender:false}}, {F(22) - 0.1:.2f}); tl.to("#final", {{opacity:0, duration:0.35}}, {DUR - 0.75:.2f});')
J(f'tl.fromTo("#gancho", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.35, immediateRender:false}}, {DUR - 0.5:.2f});')

# parpadeos regulares (~15/min) fuera de los tramos con ojos abiertos/cerrados a propósito
LIBRE = [(F(5) + 0.3, FE(12)), (F(13) + 1.5, FE(19))]
ult = max(PARP)
for a, b in LIBRE:
    t = max(a, ult + 3.6)
    while t < b:
        parpadeo(t); ult = t; t += 3.8
parpadeo(P("vez", 2) + 0.2)
N21 = len([t for t in PARP if t < F(21)])
contador("#nv", 0, N21, P("parpadeado") - 0.3, 1.2)
parpadeo(P("otra") - 0.1)

# ------------------------------------------------------------------ capa de pantalla: nubes y estrellas (vuelven a su sitio)
NUB = [(70, 560, 0.9), (650, 650, 0.7), (860, 500, 1.15), (300, 820, 0.6)]
NUBES = "".join(f'<div class="nube" id="nb{k}" style="left:{x}px;top:{y}px;transform:scale({sc})"><i></i><i></i><i></i></div>' for k, (x, y, sc) in enumerate(NUB))
for k in range(len(NUB)):
    J(f'tl.fromTo("#nb{k}", {{x:0}}, {{x:{(-1) ** k * 80}, duration:{DUR / 2:.2f}, ease:"sine.inOut", yoyo:true, repeat:1, immediateRender:false}}, 0);')
ESTR = "".join(f'<i style="left:{rr.randint(20, 1060)}px;top:{rr.randint(40, 1100)}px;width:{rr.choice([3, 4, 5])}px;height:{rr.choice([3, 4, 5])}px"></i>' for _ in range(60))

# ------------------------------------------------------------------ montaje
_S = open(os.path.join(BASE, "_subs.py"), encoding="utf-8").read()
exec(re.sub(r"CLAVE = set\(.*?\]\)", lambda m: 'CLAVE = set(norm(w) for w in ["parpadearas", "milesima", "eiffel", "mataria", "quince", "mil", "arden", "centimetro", "dormido", "ropa", "cama", "dos", "cabeza", "veinte", "problema", "duplica", "ocho", "cuatro", "wadlow", "historia", "aparatos", "tonelada", "pierna", "tumbas", "parpadeando", "seis", "pulmones", "ballena", "probable", "ano", "mueres", "pisa", "ben", "cuello", "trescientos", "cuarenta", "cuatrocientos", "empire", "milimetro", "treinta", "centesimas", "otra"])', _S, count=1, flags=re.S))
html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#74b6e6}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;color:#fff}}
#escena{{position:absolute;inset:0;background:linear-gradient(180deg,#3f8fd2 0%,#74b6e6 40%,#b9dcf3 75%,#dff0fa 100%)}}
#sol{{position:absolute;left:820px;top:330px;width:150px;height:150px;border-radius:50%;background:radial-gradient(circle,#fff7d6 0%,#ffe48a 55%,rgba(255,228,138,0) 72%)}}
#nubes{{position:absolute;inset:0;pointer-events:none}} .nube{{position:absolute;width:260px;height:80px;transform-origin:center}}
.nube i{{position:absolute;bottom:0;border-radius:50%;background:#ffffff;opacity:0.92}} .nube i:nth-child(1){{left:0;width:130px;height:60px}} .nube i:nth-child(2){{left:60px;width:130px;height:90px}} .nube i:nth-child(3){{left:130px;width:120px;height:62px}}
svg#esc{{position:absolute;left:0;top:0}}
#noche{{position:absolute;inset:0;background:#0f1d44;opacity:0;pointer-events:none;mix-blend-mode:multiply}}
#estrellas{{position:absolute;inset:0;opacity:0;pointer-events:none}} #estrellas i{{position:absolute;border-radius:50%;background:#fff}}
#vineta{{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 50% 50%,rgba(0,0,0,0) 45%,rgba(10,12,20,0.75) 100%);opacity:0}}
#fxl{{position:absolute;inset:0;z-index:58;pointer-events:none}}
.card{{position:absolute;padding:18px 24px 20px;border-radius:22px;background:rgba(14,30,52,0.82);opacity:0}}
.card small{{display:block;font:700 18px Inter;letter-spacing:4px;color:#8cc4ff;margin-bottom:6px}} .card b{{display:block;font:300 60px/1.05 Inter;letter-spacing:-1.5px}}
.card em{{display:block;font-style:normal;font:500 26px/1.3 Inter;color:rgba(255,255,255,0.78);margin-top:6px}} .card .r{{color:#ff6b5e}}
.card.centro{{text-align:center}} .card .filas p{{font:500 30px/1.5 Inter;color:#fff}} .card .filas b{{display:inline;font:800 34px Inter}}
.grande{{position:absolute;left:0;right:0;top:1430px;text-align:center}} .grande b{{display:inline-block;padding:16px 44px 10px;border-radius:28px 28px 0 0;background:rgba(14,30,52,0.84);font:300 120px/1 Inter;letter-spacing:-4px}}
.grande small{{display:block;width:max-content;margin:0 auto;padding:4px 34px 16px;border-radius:0 0 22px 22px;background:rgba(14,30,52,0.84);font:700 24px Inter;letter-spacing:6px;color:#8cc4ff}}
.pop{{position:absolute;left:600px;top:560px;font:800 40px Inter;color:#ffffff;text-shadow:0 3px 12px rgba(8,30,60,0.6);opacity:0}}
.lab{{position:absolute;left:0;top:0;padding:8px 16px;border-radius:12px;background:rgba(14,30,52,0.82);font:700 26px Inter;white-space:nowrap;opacity:0}}
#hud{{position:absolute;left:40px;right:40px;top:1610px;height:130px;border-radius:28px;background:rgba(14,30,52,0.82);display:flex;justify-content:space-around;align-items:center;opacity:0;transform:translateY(40px);z-index:59}}
#hud div{{text-align:center;min-width:280px}} #hud small{{display:block;font:700 18px Inter;letter-spacing:4px;color:#8cc4ff}} #hud b{{display:block;font:300 54px Inter;letter-spacing:-1px;font-variant-numeric:tabular-nums}}
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
  <div id="escena">
    <div id="sol"></div>
    <div id="nubes">{NUBES}</div>
    <svg id="esc" width="1080" height="1920" viewBox="0 0 1080 1920"><g id="world">{WORLD}</g></svg>
  </div>
  <div id="noche"></div><div id="estrellas">{ESTR}</div><div id="vineta"></div>
  <div id="topsombra"></div><div id="grano"></div>
  <div id="fxl">{"".join(FXL)}</div>
  <div id="hud"><div><small id="hT">DÍA</small><b id="hDia">0</b></div><div><small>ALTURA</small><b id="hAlt">1,75 m</b></div><div><small>PESO</small><b id="hKg">70 kg</b></div></div>
  <div id="marca">@mundo.supuesto</div>
  <div id="subs" data-layout-allow-overlap>{"".join(SUBS)}</div>
  <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
</div>
<script>
const fmt = (v, d) => {{ const s = v.toFixed(d).split("."); return s[0].replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ".") + (s[1] ? "," + s[1] : ""); }};
const S = {{ h:1.75, ojo:1, fx:0, by:0.5, lie:0, gris:0, zm:1 }};
const W = document.getElementById("world"), CR = document.getElementById("crece"), OJO = document.getElementById("P_ojo"), ESC = document.getElementById("escena"), VIN = document.getElementById("vineta");
const LABS = [], LV = {{}};
function wpt(el) {{ const b = el.getBBox(); const m = W.getCTM().inverse().multiply(el.getCTM()); return new DOMPoint(b.x + b.width / 2, b.y + b.height / 2).matrixTransform(m); }}
function frame() {{
  const s = S.h / 1.75; CR.setAttribute("transform", `scale(${{s}})`);
  W.setAttribute("transform", "");
  const H = 189 * s, e = wpt(OJO);
  const zb = 900 / H * S.zm, ze = 22 / s;
  const z = Math.exp(Math.log(zb) * (1 - S.ojo) + Math.log(ze) * S.ojo);
  const bx = (S.fx + 12) * s * (1 - S.lie) + 95 * s * S.lie, by = -H * S.by * (1 - S.lie) - 22 * s * S.lie;
  const fx = bx * (1 - S.ojo) + e.x * S.ojo, fy = by * (1 - S.ojo) + e.y * S.ojo;
  const sy = (1020 + 60 * S.lie) * (1 - S.ojo) + 930 * S.ojo;
  W.setAttribute("transform", `translate(540,${{sy}}) scale(${{z}}) translate(${{-fx}},${{-fy}})`);
  ESC.style.filter = S.gris > 0.001 ? `grayscale(${{S.gris * 0.85}}) brightness(${{1 - 0.22 * S.gris}})` : "none";
  VIN.style.opacity = S.gris;
  const dias = Math.max(0, (S.h - 1.75) / 0.015);
  if (dias < 365) {{ document.getElementById("hT").textContent = "DÍA"; document.getElementById("hDia").textContent = Math.round(dias); }}
  else {{ document.getElementById("hT").textContent = "AÑOS"; document.getElementById("hDia").textContent = fmt(dias / 365, 0); }}
  document.getElementById("hAlt").textContent = S.h < 10 ? S.h.toFixed(2).replace(".", ",") + " m" : fmt(S.h, 0) + " m";
  const kg = 70 * Math.pow(s, 3);
  document.getElementById("hKg").textContent = kg < 1000 ? fmt(kg, 0) + " kg" : (kg < 10000 ? fmt(kg / 1000, 1) + " t" : fmt(kg / 1000, 0) + " t");
  for (const L of LABS) {{ const el = document.getElementById("lb" + L.i); const v = LV["l" + L.i] || 0; el.style.opacity = v;
    if (v > 0.01) {{ const x = 540 + (L.x - fx) * z, y = sy + (L.y - fy) * z; const xx = Math.max(20, Math.min(x + L.dx, 1060 - el.offsetWidth)); el.style.transform = `translate(${{xx}}px, ${{y + L.dy}}px)`; }} }}
}}
const tl = gsap.timeline({{ paused: true, onUpdate: frame }});
{chr(10).join(tl)}
tl.to({{}}, {{duration:0.01}}, {DUR - 0.01});
window.__timelines["main"] = tl;
tl.seek(0); frame();
</script>
</body></html>"""
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump([], open(os.path.join(BASE, "efectos.json"), "w"))
json.dump([[0, 0.0], [DUR, 0.0]], open(os.path.join(BASE, "ambiente.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones · {len(PARP)} parpadeos ({N21} antes de la frase 21)")

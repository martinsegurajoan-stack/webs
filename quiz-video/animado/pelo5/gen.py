#!/usr/bin/env python3
"""Genera la composición HyperFrames (index.html) del vídeo «¿Qué pasaría si no te cortas el pelo en 5 años?»
leyendo tiempos.json (momento exacto de cada palabra). Todo va pegado a la voz con P("palabra", n).

  python3 gen.py              → index.html con subtítulos
  python3 gen.py --sin-subs   → index.html sin subtítulos
"""
import json, math, os, random, re, sys, unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(BASE, "tiempos.json"), encoding="utf-8"))
DUR = T["duracion"]
SIN_SUBS = "--sin-subs" in sys.argv
random.seed(5)

def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9ñ]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))

WORDS = [(norm(p["w"]), p["ini"], p["fin"]) for p in T["palabras"]]
FR = T["frases"]

def P(word, n=1):
    """Cuándo EMPIEZA la n-ésima vez que se dice `word`."""
    k = 0
    for w, a, b in WORDS:
        if w == norm(word):
            k += 1
            if k == n:
                return a
    raise KeyError(f"{word} #{n}")

def F(n):          # inicio de la frase n (1..25)
    return FR[n - 1]["ini"]

def FE(n):
    return FR[n - 1]["fin"]

# ------------------------------------------------------------------ paleta y mundo
TEAL1, TEAL2 = "#2f6f73", "#1f4b50"
CREAM = "#eadfc8"
WOOD1, WOOD2 = "#a2704a", "#87593a"
HAIR, HAIR_HI = "#4b3021", "#7a5038"
SKIN, SKIN_D = "#f2c4a2", "#e0a582"
SHIRT, SHIRT_D = "#e07a5f", "#c4614a"
PANTS = "#3d405b"
GOOD, BAD, KEY = "#3fbf7f", "#e5484d", "#f2b84b"
WORLD_W, WORLD_H = 10600, 1920
FLOOR_Y = 1380
ST = {"s0": 700, "s1": 2200, "s2": 3700, "s3": 5200, "s4": 6700, "s5": 8200, "s6": 9700}

tl = []    # líneas JS del timeline
def J(s):
    tl.append(s)

# ------------------------------------------------------------------ personaje (SVG)
FX, HCY = 500, 770      # centro x y centro de la cabeza (coords locales del svg 1000x1800)

def cap_path(v):
    return (f"M{395 - v},800 C{395 - v},700 {430},{640 - v} 500,{640 - v} C570,{640 - v} {605 + v},700 {605 + v},800 "
            f"L600,780 C595,725 560,700 500,705 C440,700 405,725 400,780 Z")

def fringe_path(drop):
    pts = [f"M402,722 C440,698 560,698 598,722 L598,{722 + drop}"]
    n = 10
    for i in range(n, -1, -1):
        x = 402 + 196 * i / n
        y = 722 + drop + (16 if i % 2 else 0)
        pts.append(f"L{x:.0f},{y}")
    return " ".join(pts) + " Z"

def lock_path(side, bottom, w0=64, w1=26):
    """Mechón delantero desde la sien hasta `bottom`, sobre el hombro y el pecho."""
    s = -1 if side == "L" else 1
    xt = FX + s * 96
    xs = FX + s * 140            # sobre el hombro
    xb = FX + s * 128
    mid = (760 + bottom) / 2
    o = f"M{xt - s * 10},740 C{xt + s * 40},800 {xs + s * 30},{min(mid, 960)} {xb + s * w1 / 2},{bottom - 30} "
    o += f"L{xb},{bottom + 18} L{xb - s * w1 / 2},{bottom - 30} "
    o += f"C{xs - s * w0},{min(mid, 960)} {xt - s * 30},{820} {xt - s * 60},740 Z"
    return o

def side_path(side, bottom):
    s = -1 if side == "L" else 1
    x0 = FX + s * 100
    return (f"M{x0 - s * 8},720 C{x0 + s * 30},760 {x0 + s * 26},{bottom - 30} {x0 + s * 8},{bottom} "
            f"L{x0 - s * 20},{bottom - 10} C{x0 - s * 10},{bottom - 60} {x0 - s * 8},780 {x0 - s * 30},740 Z")

def strands(path_kind, side, bottom, n=9):
    """Líneas finas de textura dentro de un mechón."""
    s = -1 if side == "L" else 1
    out = []
    for i in range(n):
        k = (i + 0.5) / n
        xt = FX + s * (70 + 40 * k)
        xb = FX + s * (110 + 30 * k)
        out.append(f'<path d="M{xt:.0f},760 C{xt + s * 40:.0f},860 {xb + s * 20:.0f},{(760 + bottom) / 2:.0f} {xb:.0f},{bottom - 20}" '
                   f'stroke="{HAIR_HI}" stroke-width="2.2" fill="none" opacity="0.45"/>')
    return "".join(out)

def personaje(pid, cm=None, bald=False, stubble=False):
    """SVG del personaje. cm = largo de pelo (None = calvo)."""
    g = []
    defs = f"""<defs>
<radialGradient id="{pid}-skin" cx="0.38" cy="0.32" r="0.8"><stop offset="0" stop-color="#f7d3b6"/><stop offset="1" stop-color="{SKIN_D}"/></radialGradient>
<linearGradient id="{pid}-shirt" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ea8d72"/><stop offset="1" stop-color="{SHIRT_D}"/></linearGradient>
<linearGradient id="{pid}-hair" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5d3c29"/><stop offset="1" stop-color="#3a2418"/></linearGradient>
</defs>"""
    g.append(defs)
    bottom = 760 + (cm or 0) * 6.3
    # sombra en el suelo
    g.append(f'<ellipse cx="500" cy="1702" rx="190" ry="26" fill="#000" opacity="0.22"/>')
    # melena de detrás (asoma por los lados)
    if cm and cm >= 25:
        g.append(f'<path d="M390,760 C370,900 360,1000 352,{bottom - 20} L648,{bottom - 20} C640,1000 630,900 610,760 Z" fill="url(#{pid}-hair)"/>')
    # piernas y zapatos
    g.append(f'<g id="{pid}-legs"><path d="M372,1250 L628,1250 L620,1300 L380,1300 Z" fill="{PANTS}"/>'
             f'<path d="M385,1290 L490,1290 L482,1680 L400,1680 Z" fill="{PANTS}"/>'
             f'<path d="M510,1290 L615,1290 L600,1680 L518,1680 Z" fill="#363955"/>'
             f'<ellipse cx="438" cy="1690" rx="58" ry="20" fill="#f4efe6"/><ellipse cx="562" cy="1690" rx="58" ry="20" fill="#f4efe6"/></g>')
    # cuerpo que respira (torso + brazos + cabeza)
    g.append(f'<g id="{pid}-up">')
    for side, sx, rot in (("L", 372, 1), ("R", 628, -1)):
        g.append(f'<g id="{pid}-arm{side}">'
                 f'<path d="M{sx - 26 * rot},975 C{sx - 48 * rot},1030 {sx - 52 * rot},1090 {sx - 46 * rot},1120 L{sx - 6 * rot},1120 C{sx - 4 * rot},1080 {sx},1030 {sx + 12 * rot},990 Z" fill="url(#{pid}-shirt)"/>'
                 f'<path d="M{sx - 42 * rot},1112 C{sx - 46 * rot},1180 {sx - 40 * rot},1240 {sx - 36 * rot},1262 L{sx - 10 * rot},1262 C{sx - 12 * rot},1230 {sx - 10 * rot},1170 {sx - 8 * rot},1112 Z" fill="{SKIN}"/>'
                 f'<circle cx="{sx - 24 * rot}" cy="1280" r="27" fill="{SKIN}"/></g>')
    g.append(f'<path d="M372,985 C372,962 402,952 440,948 L560,948 C598,952 628,962 628,985 L622,1270 L378,1270 Z" fill="url(#{pid}-shirt)"/>')
    g.append(f'<path d="M455,952 Q500,985 545,952" stroke="{SHIRT_D}" stroke-width="7" fill="none"/>')
    g.append(f'<rect x="470" y="870" width="60" height="90" rx="22" fill="{SKIN_D}"/>')
    # cabeza
    g.append(f'<g id="{pid}-head">')
    g.append(f'<ellipse cx="396" cy="775" rx="18" ry="28" fill="{SKIN_D}"/><ellipse cx="604" cy="775" rx="18" ry="28" fill="{SKIN_D}"/>')
    g.append(f'<ellipse cx="500" cy="770" rx="105" ry="128" fill="url(#{pid}-skin)"/>')
    if bald:
        g.append('<ellipse cx="465" cy="690" rx="34" ry="18" fill="#fff" opacity="0.35" transform="rotate(-20 465 690)"/>')
    g.append('<circle cx="452" cy="796" r="16" fill="#f08a7a" opacity="0.35"/><circle cx="548" cy="796" r="16" fill="#f08a7a" opacity="0.35"/>')
    g.append(f'<g id="{pid}-eyes"><ellipse cx="462" cy="742" rx="10" ry="13" fill="#2b2230"/><ellipse cx="538" cy="742" rx="10" ry="13" fill="#2b2230"/>'
             f'<circle cx="465" cy="737" r="3.5" fill="#fff"/><circle cx="541" cy="737" r="3.5" fill="#fff"/></g>')
    g.append(f'<g id="{pid}-brows"><path d="M444,712 Q462,702 480,710" stroke="#5a3b2b" stroke-width="6" fill="none" stroke-linecap="round"/>'
             f'<path d="M520,710 Q538,702 556,712" stroke="#5a3b2b" stroke-width="6" fill="none" stroke-linecap="round"/></g>')
    g.append('<path d="M498,760 Q490,784 504,789" stroke="#c98a6c" stroke-width="4" fill="none" stroke-linecap="round"/>')
    g.append(f'<path id="{pid}-mouth" d="M478,816 Q500,832 522,816" stroke="#7a3f35" stroke-width="5" fill="none" stroke-linecap="round"/>')
    g.append(f'<ellipse id="{pid}-mouthO" cx="500" cy="822" rx="9" ry="12" fill="#6b2f2a" opacity="0"/>')
    if stubble:   # pelitos que brotan (aparecen al decir «cien mil»)
        pts = []
        for i in range(260):
            a = random.uniform(math.pi * 1.05, math.pi * 1.95)
            r = random.uniform(0.55, 1.0)
            x = 500 + math.cos(a) * 104 * r
            y = 770 + math.sin(a) * 127 * r
            if y > 735:
                continue
            ang = math.atan2(y - 800, x - 500)
            pts.append(f'<line class="{pid}-stub" x1="{x:.1f}" y1="{y:.1f}" x2="{x + math.cos(ang) * 9:.1f}" y2="{y + math.sin(ang) * 9:.1f}" '
                       f'stroke="{HAIR}" stroke-width="3" stroke-linecap="round" opacity="0"/>')
        g.append(f'<path id="{pid}-capfade" d="{cap_path(0)}" fill="{HAIR}" opacity="0"/>' + "".join(pts))
    if bald:      # el pelo solitario
        g.append(f'<path id="{pid}-one" d="M500,642 C494,600 532,592 522,560 C514,538 538,528 544,516" stroke="{HAIR}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    if cm:
        v = min(4 + cm * 1.4, 22)
        if 10 <= cm < 25:
            for sd in ("L", "R"):
                g.append(f'<path d="{side_path(sd, bottom)}" fill="url(#{pid}-hair)"/>')
        g.append(f'<path d="{cap_path(v)}" fill="url(#{pid}-hair)"/>')
        g.append(f'<path d="M430,670 Q500,640 570,668" stroke="{HAIR_HI}" stroke-width="4" fill="none" opacity="0.6"/>')
        if cm < 12:
            g.append(f'<path id="{pid}-fringe" d="{fringe_path(20)}" fill="url(#{pid}-hair)"/>')
    g.append('</g>')   # head
    if cm and cm >= 25:
        for sd in ("L", "R"):
            g.append(f'<g id="{pid}-lock{sd}"><path d="{lock_path(sd, bottom)}" fill="url(#{pid}-hair)"/>{strands("lock", sd, bottom)}</g>')
    g.append('</g>')   # up
    return f'<svg class="pj" id="{pid}" viewBox="0 0 1000 1800" width="1000" height="1800" style="position:absolute;left:{{x}}px;top:0px;overflow:visible">' + "".join(g) + "</svg>"

def pj_at(pid, sx, **kw):
    return personaje(pid, **kw).replace("{x}", str(sx - 500))

def vida(pid):
    """Respira y parpadea durante todo el vídeo (nunca congelado)."""
    reps = int(DUR / 1.7)
    J(f'tl.fromTo("#{pid}-up", {{scaleY:1}}, {{scaleY:1.012, duration:0.85, ease:"sine.inOut", yoyo:true, repeat:{reps}, svgOrigin:"500 1270"}}, 0);')
    t = 0.7 + random.uniform(0, 1.2)
    while t < DUR - 0.3:
        J(f'tl.to("#{pid}-eyes", {{scaleY:0.1, duration:0.07, svgOrigin:"500 742", yoyo:true, repeat:1}}, {t:.2f});')
        t += random.uniform(2.6, 3.8)

# ------------------------------------------------------------------ piezas reutilizables (HTML)
def card(cid, x, y, top, big, color=KEY, w=380):
    return (f'<div id="{cid}" class="card" style="left:{x}px;top:{y}px;width:{w}px">'
            f'<div class="card-top">{top}</div><div class="card-big" style="color:{color}">{big}</div></div>')

def rodillo(rid, x, y, valor, size=120, color="#1d2b33"):
    """Número tipo rodillo: cada cifra es una tira 0-9 que gira hasta su valor."""
    html = [f'<div id="{rid}" class="rod" style="left:{x}px;top:{y}px;font-size:{size}px;color:{color};height:{size * 1.15}px">']
    k = 0
    for ch in valor:
        if ch.isdigit():
            strip = "".join(f"<div>{d}</div>" for d in range(10))
            html.append(f'<div class="rod-col" style="height:{size * 1.15}px"><div class="rod-strip" id="{rid}-d{k}">{strip}</div></div>')
            k += 1
        else:
            html.append(f'<div class="rod-sep">{ch}</div>')
    html.append("</div>")
    return "".join(html), k, [int(c) for c in valor if c.isdigit()], size * 1.15

def rodar(rid, n, digs, h, t, dur=1.4):
    for i, d in enumerate(digs):
        J(f'tl.fromTo("#{rid}-d{i}", {{y:0}}, {{y:{-d * h:.1f}, duration:{dur + 0.12 * (n - i):.2f}, ease:"power3.out"}}, {t:.2f});')

def pop(sel, t, s0=0.0, dur=0.45, ease="back.out(1.8)", origin=None):
    o = f', transformOrigin:"{origin}"' if origin else ""
    J(f'tl.fromTo("{sel}", {{scale:{s0}, opacity:0}}, {{scale:1, opacity:1, duration:{dur}, ease:"{ease}"{o}}}, {t:.2f});')
    FX_EV.append(("pop", t))

FX_EV = []   # efectos de sonido (tipo, tiempo)

# ------------------------------------------------------------------ cámara
CAM = []
def cam(t, x, y, z, dur=1.0, ease="power2.inOut", viaje=False):
    J(f'tl.to("#world", {{x:{540 - x * z:.1f}, y:{960 - y * z:.1f}, scale:{z}, duration:{dur}, ease:"{ease}"}}, {t:.2f});')
    J(f'tl.to("#lejos", {{x:{(540 - x * z) * 0.35:.1f}, duration:{dur}, ease:"{ease}"}}, {t:.2f});')
    if viaje:
        J(f'tl.to("#world", {{filter:"blur(5px)", duration:{dur / 2:.2f}, ease:"sine.in"}}, {t:.2f});')
        J(f'tl.to("#world", {{filter:"blur(0px)", duration:{dur / 2:.2f}, ease:"sine.out"}}, {t + dur / 2:.2f});')
        FX_EV.append(("whoosh", t))

# ------------------------------------------------------------------ construcción del mundo
H = []   # HTML del mundo
s0, s1, s2, s3, s4, s5, s6 = (ST[k] for k in ("s0", "s1", "s2", "s3", "s4", "s5", "s6"))

# camino que une las estaciones (se dibuja mientras viaja la cámara)
path_d = f"M{s0},1760 " + " ".join(f"C{a + 500},1700 {b - 500},1820 {b},1760" for a, b in zip(list(ST.values())[:-1], list(ST.values())[1:]))
H.append(f'<svg style="position:absolute;left:0;top:0" width="{WORLD_W}" height="{WORLD_H}"><path id="camino" d="{path_d}" stroke="{CREAM}" '
         f'stroke-width="10" fill="none" stroke-linecap="round" stroke-dasharray="1 0" opacity="0.85"/>'
         + "".join(f'<circle id="nodo{i}" cx="{x}" cy="1760" r="22" fill="{CREAM}" stroke="{TEAL2}" stroke-width="6"/>' for i, x in enumerate(ST.values()))
         + "</svg>")

# S0: calvo con un pelo → cien mil pelitos
H.append(pj_at("p0", s0, bald=True, stubble=True))
r_html, r_n, r_d, r_h = rodillo("rod0", s0 + 95, 1050, "100.000", size=80)
H.append(f'<div id="c0" class="card" style="left:{s0 + 60}px;top:960px;width:400px;height:200px"><div class="card-top">PELOS EN LA CABEZA</div></div>')
H.append(r_html)
H.append(f'<div id="regla0" class="regla" style="left:{s0 - 300}px;top:650px;height:420px"></div>')
H.append(f'<div id="cal0" class="card" style="left:{s0 - 470}px;top:1110px;width:300px"><div class="card-top">CRECE</div><div class="card-big" style="color:{GOOD}">≈1 cm<span style="font-size:44px">/mes</span></div></div>')

# S1: mes 6 (flequillo)
H.append(pj_at("p1", s1, cm=7))
H.append(card("c1", s1 + 170, 1130, "MES 6", "7 cm"))
H.append(f'<svg id="peine" style="position:absolute;left:{s1 - 260}px;top:600px" width="260" height="90" viewBox="0 0 260 90"><rect x="0" y="0" width="260" height="30" rx="12" fill="#e9d7b5"/>'
         + "".join(f'<rect x="{8 + i * 12}" y="26" width="6" height="56" rx="3" fill="#e9d7b5"/>' for i in range(21)) + "</svg>")
H.append(f'<div id="x1" class="badge" style="left:{s1 - 330}px;top:1150px;background:{BAD}">✕ NO AGUANTA</div>')

# S2: año 2 (nudos, secado)
H.append(pj_at("p2", s2, cm=30))
H.append(card("c2", s2 + 170, 1150, "AÑO 2", "30 cm"))
H.append(f'<svg id="cepillo" style="position:absolute;left:{s2 + 70}px;top:830px" width="150" height="260" viewBox="0 0 150 260">'
         f'<ellipse cx="75" cy="60" rx="58" ry="62" fill="#8f6656"/><ellipse cx="75" cy="60" rx="44" ry="48" fill="#3a3038"/>'
         + "".join(f'<circle cx="{45 + (i % 5) * 15}" cy="{28 + (i // 5) * 16}" r="3.5" fill="#d9d2c8"/>' for i in range(20))
         + '<rect x="62" y="115" width="26" height="140" rx="13" fill="#8f6656"/></svg>')
H.append(f'<svg id="secador" style="position:absolute;left:{s2 - 470}px;top:640px" width="300" height="260" viewBox="0 0 300 260">'
         '<rect x="20" y="40" width="190" height="90" rx="45" fill="#9fb7c9"/><rect x="190" y="58" width="60" height="54" rx="10" fill="#7f98ab"/>'
         '<rect x="70" y="118" width="46" height="120" rx="20" fill="#9fb7c9"/><circle cx="70" cy="85" r="26" fill="#c9d7e2"/>'
         + "".join(f'<path class="aire" d="M255,{70 + i * 14} q20,-8 40,0" stroke="#e8f1f7" stroke-width="5" fill="none" stroke-linecap="round" opacity="0"/>' for i in range(3))
         + "</svg>")
H.append(f'<div id="reloj" class="reloj" style="left:{s2 - 470}px;top:1060px"><div id="aguja1" class="aguja" style="height:70px"></div><div id="aguja2" class="aguja" style="height:52px;width:12px"></div></div>')

# S3: año 3 (puerta, cremallera, sopa)
H.append(f'<div id="marco" style="position:absolute;left:{s3 - 520}px;top:760px;width:270px;height:640px;background:#cdbb9c;border-radius:10px"></div>')
H.append(f'<div id="puerta" style="position:absolute;left:{s3 - 505}px;top:775px;width:240px;height:625px;background:linear-gradient(90deg,#5f7e74,#4d6a61);border-radius:6px;transform-origin:0 50%">'
         f'<div style="position:absolute;right:22px;top:300px;width:22px;height:22px;border-radius:50%;background:#e2c27a"></div></div>')
H.append(pj_at("p3", s3, cm=45))
H.append(f'<svg id="tenso" style="position:absolute;left:{s3 - 300}px;top:780px;overflow:visible" width="220" height="80"><path d="M0,40 C70,30 140,50 210,20" stroke="{HAIR}" stroke-width="16" fill="none" stroke-linecap="round"/></svg>')
H.append(card("c3", s3 + 190, 1150, "AÑO 3", "45 cm"))
H.append(f'<svg id="zip" style="position:absolute;left:{s3 - 10}px;top:960px" width="20" height="310"><line x1="10" y1="0" x2="10" y2="310" stroke="#d8c7a3" stroke-width="8" stroke-dasharray="6 5"/></svg>')
H.append(f'<div id="slider" style="position:absolute;left:{s3 - 16}px;top:1240px;width:32px;height:46px;background:#d9b456;border-radius:6px"></div>')
H.append(f'<svg id="sopa" style="position:absolute;left:{s3 + 40}px;top:1130px" width="260" height="200" viewBox="0 0 260 200">'
         '<path d="M10,80 Q130,230 250,80 Z" fill="#f0e8dc"/><ellipse cx="130" cy="80" rx="120" ry="24" fill="#d9944d"/>'
         + "".join(f'<path class="vapor" d="M{90 + i * 40},60 q-14,-25 0,-45 q14,-20 0,-45" stroke="#fff" stroke-width="6" fill="none" opacity="0"/>' for i in range(3))
         + "</svg>")

# S4: clímax (gráfica que se aplana, 2-7 años, ADN, caída y nuevo pelo)
H.append(f'<div id="graf" class="card" style="left:{s4 - 430}px;top:520px;width:860px;height:560px"><div class="card-top">CRECIMIENTO DE TU PELO</div></div>')
H.append(f'<svg id="grafsvg" style="position:absolute;left:{s4 - 400}px;top:590px" width="800" height="470" viewBox="0 0 800 470">'
         '<line x1="40" y1="430" x2="780" y2="430" stroke="#c9c2b6" stroke-width="5"/><line x1="40" y1="20" x2="40" y2="430" stroke="#c9c2b6" stroke-width="5"/>'
         + "".join(f'<text x="{40 + i * 148}" y="465" font-size="28" font-family="Inter" font-weight="700" fill="#8a8277">{i}</text>' for i in range(6))
         + f'<path id="curva" d="M40,420 C180,330 320,220 480,140 L780,140" stroke="{GOOD}" stroke-width="12" fill="none" stroke-linecap="butt" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
         + f'<g id="stop"><circle cx="480" cy="140" r="34" fill="{BAD}"/><rect x="465" y="125" width="30" height="30" rx="4" fill="#fff"/></g></svg>')
H.append(f'<div id="barra" class="card" style="left:{s4 - 430}px;top:1110px;width:860px;height:170px"><div class="card-top">CADA PELO CRECE</div>'
         f'<div style="position:absolute;left:40px;top:92px;width:780px;height:40px;border-radius:20px;background:#ece6db"></div>'
         f'<div id="barfill" style="position:absolute;left:40px;top:92px;width:780px;height:40px;border-radius:20px;background:{KEY};transform-origin:0 50%"></div>'
         f'<div style="position:absolute;right:40px;top:12px;font:900 56px Inter;color:#1d2b33">2 → 7 años</div></div>')
helix = []
for i in range(14):
    y = 20 + i * 26
    helix.append(f'<circle class="adnA" data-i="{i}" cx="70" cy="{y}" r="11" fill="{GOOD}"/><circle class="adnB" data-i="{i}" cx="70" cy="{y}" r="11" fill="{KEY}"/>')
H.append(f'<svg id="adn" style="position:absolute;left:{s4 + 300}px;top:1300px;overflow:visible" width="140" height="380">{"".join(helix)}</svg>')
H.append(f'<svg id="foliculo" style="position:absolute;left:{s4 - 430}px;top:1320px;overflow:visible" width="300" height="240" viewBox="0 0 300 240">'
         f'<rect x="0" y="150" width="300" height="90" rx="20" fill="{SKIN}"/><path d="M150,150 q-8,-30 0,-60" id="pelo-viejo" stroke="{HAIR}" stroke-width="7" fill="none" stroke-linecap="round"/>'
         f'<path id="pelo-nuevo" d="M150,150 q6,-25 0,-50" stroke="{HAIR}" stroke-width="7" fill="none" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg>')

# S5: año 5 (75 cm, cinta métrica)
H.append(pj_at("p5", s5, cm=75))
H.append(f'<div id="cinta" class="cinta" style="left:{s5 + 230}px;top:760px;height:472px"><div class="cinta-tag">75 cm</div></div>')
H.append(card("c5", s5 - 560, 1050, "AÑO 5", "75 cm", color=GOOD, w=330))

# S6: pelos perdidos + llamada a la acción
H.append(f'<div id="panel" class="card" style="left:{s6 - 430}px;top:560px;width:860px;height:430px"><div class="card-top">PELOS PERDIDOS EN 5 AÑOS</div>'
         f'<div style="position:absolute;left:0;right:0;top:170px;text-align:center;font:900 64px Inter;color:#8a8277">–</div>'
         f'<div style="position:absolute;left:0;right:0;top:330px;text-align:center;font:700 40px Inter;color:#8a8277">de 50 a 100 al día · normal</div></div>')
ra, ran, rad_, rah = rodillo("rodA", s6 - 400, 700, "90.000", size=96)
rb, rbn, rbd, rbh = rodillo("rodB", s6 + 20, 700, "180.000", size=96, color=BAD)
H.append(ra); H.append(rb)
falling = []
for i in range(26):
    x = s6 - 380 + random.uniform(0, 760)
    falling.append(f'<svg class="caen" id="caen{i}" style="position:absolute;left:{x:.0f}px;top:1000px;overflow:visible" width="60" height="60">'
                   f'<path d="M5,5 C25,15 10,35 40,50" stroke="{HAIR}" stroke-width="4" fill="none" stroke-linecap="round"/></svg>')
H.append("".join(falling))
H.append(f'<div id="btnA" class="btn" style="left:{s6 - 420}px;top:1180px;background:{GOOD}">AGUANTO</div>')
H.append(f'<div id="btnB" class="btn" style="left:{s6 + 40}px;top:1180px;background:{BAD}">CORTO</div>')
H.append(f'<svg id="cursor" style="position:absolute;left:{s6 + 250}px;top:1420px;overflow:visible" width="80" height="100" viewBox="0 0 80 100">'
         '<path d="M5,5 L5,80 L25,62 L40,95 L52,90 L38,58 L65,58 Z" fill="#fff" stroke="#1d2b33" stroke-width="5" stroke-linejoin="round"/></svg>')

# ------------------------------------------------------------------ guion → animación (todo con P())
for pid in ("p0", "p1", "p2", "p3", "p5"):
    vida(pid)

# estado inicial (y final, para el bucle)
J('tl.set("#world", {x:%.1f, y:%.1f, scale:1.55}, 0);' % (540 - s0 * 1.55, 960 - 760 * 1.55))
J('tl.set("#lejos", {x:%.1f}, 0);' % ((540 - s0 * 1.55) * 0.35))
for sel in ["#c0", "#rod0", "#regla0", "#cal0", "#c1", "#peine", "#x1", "#c2", "#cepillo", "#secador", "#reloj", "#c3", "#tenso", "#zip", "#slider",
            "#sopa", "#graf", "#grafsvg", "#barra", "#adn", "#foliculo", "#cinta", "#c5", "#panel", "#rodA", "#rodB", "#btnA", "#btnB", "#cursor", "#stop"]:
    J(f'tl.set("{sel}", {{opacity:0}}, 0);')
J('tl.set("#camino", {strokeDasharray:"0 20000"}, 0);')
J('tl.set(".caen", {opacity:0}, 0);')

# 1 · gancho: arranque potente (golpe de zoom + el pelo solitario hace «boing»)
J('tl.fromTo("#world", {scale:1.85}, {scale:1.55, duration:0.55, ease:"power3.out"}, 0);')
J('tl.fromTo("#p0-one", {rotation:-35}, {rotation:0, duration:1.4, ease:"elastic.out(1.2,0.25)", svgOrigin:"500 642"}, 0.05);')
FX_EV.append(("golpe", 0.0))
J(f'tl.to("#p0-one", {{rotation:14, duration:0.35, yoyo:true, repeat:3, ease:"sine.inOut", svgOrigin:"500 642"}}, {P("pelo", 1):.2f});')
# 2 · «un pelo» → «cien mil»
J(f'tl.fromTo("#p0-one", {{scale:1}}, {{scale:1.35, duration:0.3, yoyo:true, repeat:1, svgOrigin:"500 642"}}, {P("pelo", 2):.2f});')
J(f'tl.to("#p0-mouthO", {{opacity:1, duration:0.15}}, {P("bueno"):.2f}); tl.to("#p0-mouth", {{opacity:0, duration:0.15}}, {P("bueno"):.2f});')
tc = P("cien")
J(f'tl.to(".p0-stub", {{opacity:1, duration:0.12, stagger:{{each:0.004, from:"random"}}}}, {tc:.2f});')
J(f'tl.to("#p0-capfade", {{opacity:0.55, duration:1.0}}, {tc + 0.2:.2f});')
J(f'tl.to("#world", {{scale:1.15, x:{540 - (s0 + 60) * 1.15:.1f}, y:{960 - 900 * 1.15:.1f}, duration:0.9, ease:"power2.inOut"}}, {tc - 0.1:.2f});')
pop("#c0", tc); J(f'tl.to("#rod0", {{opacity:1, duration:0.2}}, {tc:.2f});')
rodar("rod0", r_n, r_d, r_h, tc)
FX_EV.append(("pop", tc + 0.3))
J(f'tl.to("#p0-mouthO", {{opacity:0, duration:0.15}}, {P("mil") + 0.3:.2f}); tl.to("#p0-mouth", {{opacity:1, duration:0.15}}, {P("mil") + 0.3:.2f});')
# 3 · crece ~1 cm al mes: regla + ficha; la cámara se aleja y enseña la estación entera
tcm = P("centimetro")
J(f'tl.fromTo("#regla0", {{scaleY:0, opacity:1}}, {{scaleY:1, duration:0.6, ease:"power2.out", transformOrigin:"50% 0%"}}, {P("crece"):.2f});')
FX_EV.append(("pop", P("crece")))
pop("#cal0", tcm)
cam(P("mes", 1) - 0.1, s0 - 20, 1000, 0.95, dur=0.8)

# 4 · UNO — mes 6: viaje por el camino hasta S1
t = F(5)
J(f'tl.to("#camino", {{strokeDasharray:"{s1 - s0 + 120} 20000", duration:1.0, ease:"power2.inOut"}}, {t:.2f});')
cam(t, s1, 1000, 0.95, dur=1.0, viaje=True)
pop("#c1", P("siete"))
cam(P("flequillo") - 0.35, s1, 780, 1.75, dur=0.6); J(f'tl.to("#c1", {{opacity:0, duration:0.25}}, {P("flequillo") - 0.4:.2f});')
J(f'tl.to("#p1-fringe", {{attr:{{d:"{fringe_path(78)}"}}, duration:0.7, ease:"power2.inOut"}}, {P("flequillo"):.2f});')
J(f'tl.to("#p1-mouth", {{attr:{{d:"M480,822 Q500,812 520,822"}}, duration:0.3}}, {P("ojos"):.2f});')
# 5 · ningún peinado aguanta: el peine pasa y el flequillo vuelve a caer
tp = P("peinado")
cam(tp - 0.3, s1 - 60, 820, 1.35, dur=0.5)
J(f'tl.fromTo("#peine", {{opacity:1, x:-120, y:0, rotation:-8}}, {{x:620, y:20, rotation:6, duration:0.9, ease:"power1.inOut"}}, {tp:.2f});')
J(f'tl.to("#p1-fringe", {{attr:{{d:"{fringe_path(22)}"}}, duration:0.35}}, {tp + 0.3:.2f});')
J(f'tl.to("#p1-fringe", {{attr:{{d:"{fringe_path(78)}"}}, duration:0.6, ease:"bounce.out"}}, {P("aguanta"):.2f});')
J(f'tl.to("#peine", {{opacity:0, duration:0.3}}, {tp + 1.0:.2f});')
pop("#x1", P("aguanta") + 0.1)
cam(FE(7) + 0.05, s1, 1000, 0.95, dur=0.5)

# 6 · DOS — año 2
t = F(8)
J(f'tl.to("#camino", {{strokeDasharray:"{s2 - s0 + 120} 20000", duration:1.0, ease:"power2.inOut"}}, {t:.2f});')
cam(t, s2, 1000, 0.95, dur=1.0, viaje=True)
pop("#c2", P("treinta"))
tn = P("nudos")
cam(tn - 0.3, s2 + 70, 920, 1.5, dur=0.6); J(f'tl.to("#c2", {{opacity:0, duration:0.25}}, {tn - 0.35:.2f});')
pop("#cepillo", tn, origin="50% 50%")
J(f'tl.to("#cepillo", {{rotation:12, duration:0.09, yoyo:true, repeat:15, transformOrigin:"50% 20%"}}, {tn + 0.4:.2f});')
J(f'tl.to("#p2-armR", {{rotation:-55, duration:0.4, ease:"power2.out", svgOrigin:"628 990"}}, {tn + 0.2:.2f});')
J(f'tl.to("#p2-brows", {{y:6, duration:0.2}}, {tn + 0.2:.2f}); tl.to("#p2-mouth", {{attr:{{d:"M480,824 Q500,812 520,824"}}, duration:0.2}}, {tn + 0.2:.2f});')
ts = P("secarlo")
cam(ts - 0.3, s2 - 200, 900, 1.2, dur=0.6)
pop("#secador", ts)
J(f'tl.to("#secador .aire", {{opacity:1, x:30, duration:0.25, stagger:0.08, yoyo:true, repeat:7}}, {ts + 0.2:.2f});')
pop("#reloj", P("media"))
J(f'tl.fromTo("#aguja1", {{rotation:0}}, {{rotation:1440, duration:1.6, ease:"power2.inOut"}}, {P("manana"):.2f});')
J(f'tl.fromTo("#aguja2", {{rotation:0}}, {{rotation:180, duration:1.6, ease:"power2.inOut"}}, {P("manana"):.2f});')
J(f'tl.to("#p2-armR", {{rotation:0, duration:0.5}}, {FE(10):.2f});')
cam(FE(10), s2, 1000, 0.95, dur=0.4)

# 7 · TRES — año 3: puerta, cremallera, sopa
t = F(11)
J(f'tl.to("#camino", {{strokeDasharray:"{s3 - s0 + 120} 20000", duration:1.0, ease:"power2.inOut"}}, {t:.2f});')
J(f'tl.set("#puerta", {{scaleX:0.18}}, 0);')
cam(t, s3, 1000, 0.95, dur=1.0, viaje=True)
pop("#c3", P("cuarenta"))
tq = P("puertas")
cam(tq - 0.4, s3 - 180, 950, 1.15, dur=0.5); J(f'tl.to("#c3", {{opacity:0, duration:0.25}}, {tq - 0.45:.2f});')
J(f'tl.to("#puerta", {{scaleX:1, duration:0.28, ease:"power4.in"}}, {tq:.2f});')
FX_EV.append(("portazo", tq + 0.28))
J(f'tl.to("#tenso", {{opacity:1, duration:0.05}}, {tq + 0.27:.2f});')
J(f'tl.fromTo("#p3-up", {{x:0}}, {{x:-26, duration:0.12, yoyo:true, repeat:3}}, {tq + 0.3:.2f});')
J(f'tl.to("#p3-mouth", {{attr:{{d:"M482,826 Q500,812 518,826"}}, duration:0.15}}, {tq + 0.3:.2f});')
tz = P("cremallera")
cam(tz - 0.35, s3, 1080, 1.35, dur=0.5)
J(f'tl.to(["#zip","#slider"], {{opacity:1, duration:0.2}}, {tz - 0.1:.2f});')
J(f'tl.fromTo("#slider", {{y:0}}, {{y:-250, duration:0.8, ease:"power2.inOut"}}, {tz:.2f});')
J(f'tl.to("#p3-lockR", {{x:-70, duration:0.6, ease:"power2.inOut"}}, {tz + 0.3:.2f});')
FX_EV.append(("clic", tz + 0.8))
tsop = P("sopa")
cam(tsop - 0.4, s3 + 140, 1120, 1.3, dur=0.5)
pop("#sopa", tsop - 0.2)
J(f'tl.to("#p3-lockR", {{x:-30, y:60, rotation:-6, duration:0.6, ease:"power2.inOut", svgOrigin:"600 760"}}, {tsop:.2f});')
J(f'tl.to("#sopa .vapor", {{opacity:0.8, y:-30, duration:0.7, stagger:0.15, yoyo:true, repeat:3}}, {tsop:.2f});')
cam(FE(14) + 0.05, s3, 1000, 0.95, dur=0.45)

# 8 · CUATRO — clímax: deja de crecer
t = F(15)
J(f'tl.to("#camino", {{strokeDasharray:"{s4 - s0 + 120} 20000", duration:1.1, ease:"power2.inOut"}}, {t:.2f});')
cam(t, s4, 980, 0.95, dur=1.1, viaje=True)
pop("#graf", P("aqui")); J(f'tl.to("#grafsvg", {{opacity:1, duration:0.3}}, {P("aqui"):.2f});')
cam(P("nadie"), s4, 830, 1.1, dur=1.6, ease="sine.inOut")   # zoom lento
td = P("dejar")
J(f'tl.to("#curva", {{strokeDashoffset:0, duration:{max(0.8, P("crecer", 1) - td + 0.4):.2f}, ease:"none"}}, {td - 0.3:.2f});')
J(f'tl.fromTo("#stop", {{scale:0, opacity:0}}, {{scale:1, opacity:1, duration:0.45, ease:"back.out(2)", svgOrigin:"480 140"}}, {P("crecer", 1) + 0.15:.2f});'); FX_EV.append(("pop", P("crecer", 1) + 0.15))
FX_EV.append(("golpe", P("crecer", 1) + 0.15))
J(f'tl.fromTo("#world", {{rotation:0}}, {{rotation:0.4, duration:0.06, yoyo:true, repeat:3}}, {P("crecer", 1) + 0.15:.2f});')
tb = P("dos", 3)
cam(tb - 0.4, s4, 1100, 1.0, dur=0.5)
pop("#barra", tb - 0.3)
J(f'tl.fromTo("#barfill", {{scaleX:0.28}}, {{scaleX:1, duration:{max(0.6, P("siete", 2) - tb + 0.3):.2f}, ease:"power2.inOut"}}, {tb:.2f});')
tg = P("genes")
cam(tg - 0.3, s4, 1300, 1.0, dur=0.5)
pop("#adn", tg)
J(f'tl.to(".adnA", {{attr:{{cx:(i, el) => 70 + 50 * Math.sin(i * 0.6 + 3.14)}}, duration:0.6, ease:"sine.inOut", stagger:0.02, yoyo:true, repeat:5}}, {tg:.2f});')
J(f'tl.to(".adnB", {{attr:{{cx:(i, el) => 70 + 50 * Math.sin(i * 0.6)}}, duration:0.6, ease:"sine.inOut", stagger:0.02, yoyo:true, repeat:5}}, {tg:.2f});')
J(f'tl.fromTo("#adn .adnA, #adn .adnB", {{attr:{{cx:70}}}}, {{attr:{{cx:70}}, duration:0.01}}, 0);')
pop("#foliculo", P("despues") - 0.2)
J(f'tl.to("#pelo-viejo", {{y:140, x:30, rotation:40, opacity:0, duration:0.9, ease:"power2.in", svgOrigin:"150 150"}}, {P("cae"):.2f});')
J(f'tl.to("#pelo-nuevo", {{strokeDashoffset:0, duration:0.7, ease:"power2.out"}}, {P("nace"):.2f});')
cam(P("despues") - 0.4, s4, 1300, 1.0, dur=0.5)

# 9 · año 5: 75 cm, cinta métrica, casi hasta la cintura
t = F(20)
J(f'tl.to("#camino", {{strokeDasharray:"{s5 - s0 + 120} 20000", duration:1.0, ease:"power2.inOut"}}, {t:.2f});')
cam(t, s5, 960, 1.1, dur=1.0, viaje=True)
J(f'tl.fromTo("#cinta", {{scaleY:0, opacity:1}}, {{scaleY:1, duration:1.2, ease:"power2.out", transformOrigin:"50% 0%"}}, {P("setenta"):.2f});')
FX_EV.append(("pop", P("setenta")))
pop("#c5", P("setenta") + 0.3)
cam(P("cintura") - 0.4, s5 - 60, 1050, 0.9, dur=0.8)
J(f'tl.to("#p5-mouth", {{attr:{{d:"M474,814 Q500,840 526,814"}}, duration:0.3}}, {P("cintura"):.2f});')

# 10 · pelos perdidos (números rodillo) y pelos que caen
t = F(22)
J(f'tl.to("#camino", {{strokeDasharray:"{s6 - s0 + 120} 20000", duration:1.0, ease:"power2.inOut"}}, {t:.2f});')
cam(t, s6, 980, 0.95, dur=1.0, viaje=True)
pop("#panel", P("perdido"))
tn9 = P("noventa")
J(f'tl.to("#rodA", {{opacity:1, duration:0.15}}, {tn9:.2f});'); rodar("rodA", ran, rad_, rah, tn9)
tc18 = P("ciento")
J(f'tl.to("#rodB", {{opacity:1, duration:0.15}}, {tc18:.2f});'); rodar("rodB", rbn, rbd, rbh, tc18)
FX_EV.append(("pop", tn9)); FX_EV.append(("pop", tc18))
for i in range(26):
    t0 = tn9 + i * 0.12
    J(f'tl.fromTo("#caen{i}", {{opacity:0, y:-80, rotation:0}}, {{opacity:1, y:{560 + (i % 5) * 30}, rotation:{random.choice([-1, 1]) * random.randint(60, 240)}, duration:1.6, ease:"power1.in"}}, {t0:.2f});')

# 11 · llamada a la acción: AGUANTO / CORTO con cursor
ta = P("aguantarias")
cam(ta - 0.3, s6, 1080, 1.0, dur=0.6)
pop("#btnA", ta); pop("#btnB", ta + 0.12)
J(f'tl.to("#cursor", {{opacity:1, duration:0.2}}, {P("escribe"):.2f});')
J(f'tl.to("#btnA", {{scale:1.12, duration:0.2, yoyo:true, repeat:1}}, {P("aguanto"):.2f});')
J(f'tl.to("#btnB", {{scale:1.12, duration:0.2, yoyo:true, repeat:1}}, {P("corto"):.2f});')
J(f'tl.to("#cursor", {{x:-290, y:-150, duration:0.6, ease:"power2.inOut"}}, {P("aguanto") - 0.3:.2f});')
J(f'tl.to("#cursor", {{scale:0.85, duration:0.1, yoyo:true, repeat:1}}, {P("comentarios"):.2f});')
J(f'tl.to("#btnA", {{scale:0.94, duration:0.1, yoyo:true, repeat:1}}, {P("comentarios"):.2f});')
FX_EV.append(("clic", P("comentarios")))

# 12 · BUCLE: la cámara vuelve al principio del camino (cabeza calva con un pelo = primer fotograma)
t = F(25)
back = DUR - t
J(f'tl.to(".p0-stub", {{opacity:0, duration:0.3}}, {t:.2f}); tl.to("#p0-capfade", {{opacity:0, duration:0.3}}, {t:.2f});')
J(f'tl.to(["#c0", "#rod0", "#regla0", "#cal0"], {{opacity:0, duration:0.3}}, {t:.2f});')
J(f'tl.to("#camino", {{strokeDasharray:"0 20000", duration:{back:.2f}, ease:"power2.inOut"}}, {t:.2f});')
J(f'tl.to("#world", {{x:{540 - s0 * 1.55:.1f}, y:{960 - 760 * 1.55:.1f}, scale:1.55, duration:{back:.2f}, ease:"power3.inOut"}}, {t:.2f});')
J(f'tl.to("#lejos", {{x:{(540 - s0 * 1.55) * 0.35:.1f}, duration:{back:.2f}, ease:"power3.inOut"}}, {t:.2f});')
J(f'tl.to("#world", {{filter:"blur(6px)", duration:{back / 2:.2f}, ease:"sine.in"}}, {t:.2f}); tl.to("#world", {{filter:"blur(0px)", duration:{back / 2 - 0.05:.2f}, ease:"sine.out"}}, {t + back / 2:.2f});')
J(f'tl.fromTo("#p0-one", {{rotation:-35}}, {{rotation:-35, duration:0.01}}, {DUR - 0.04:.2f});')   # mismo estado que el fotograma 0
FX_EV.append(("whoosh", t))

# fondo con paralaje y motas que flotan (nunca quieto)
LEJOS = []
for i in range(40):
    x = random.uniform(-500, WORLD_W * 0.6)
    y = random.uniform(150, 1300)
    r = random.uniform(40, 160)
    LEJOS.append(f'<div class="blob" style="left:{x:.0f}px;top:{y:.0f}px;width:{2 * r:.0f}px;height:{2 * r:.0f}px;opacity:{random.uniform(0.05, 0.13):.2f}"></div>')
MOTAS = []
for i in range(60):
    x = random.uniform(0, WORLD_W)
    y = random.uniform(200, 1350)
    MOTAS.append(f'<div class="mota" id="mota{i}" style="left:{x:.0f}px;top:{y:.0f}px"></div>')
    J(f'tl.fromTo("#mota{i}", {{y:0, opacity:0.0}}, {{y:{-random.uniform(60, 160):.0f}, opacity:0.6, duration:{random.uniform(3, 6):.1f}, ease:"sine.inOut", yoyo:true, repeat:{int(DUR / 4)}}}, {random.uniform(0, 3):.2f});')

# ------------------------------------------------------------------ subtítulos (arriba, palabra a palabra)
CLAVE = {"cinco": KEY, "pelo": KEY, "cien": KEY, "mil": KEY, "centimetro": GOOD, "seis": KEY, "siete": KEY, "flequillo": BAD, "ojos": BAD,
         "peinado": BAD, "treinta": KEY, "nudos": BAD, "manana": BAD, "cuarenta": KEY, "puertas": BAD, "cremallera": BAD, "sopa": BAD,
         "nadie": KEY, "dejar": BAD, "crecer": BAD, "genes": GOOD, "cae": BAD, "nace": GOOD, "setenta": GOOD, "cintura": GOOD,
         "noventa": BAD, "ochenta": BAD, "aguantarias": KEY, "aguanto": GOOD, "corto": BAD, "solo": KEY, "uno": KEY, "dos": KEY,
         "tres": KEY, "cuatro": KEY}
SUBS = []
if not SIN_SUBS:
    chunks, cur = [], []
    for p in T["palabras"]:
        cur.append(p)
        txt = " ".join(x["w"] for x in cur)
        if len(cur) >= 4 or len(txt) >= 20 or re.search(r"[.,:;?!…]$", p["w"]) or (len(cur) >= 2 and len(txt) >= 15):
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    for k, ch in enumerate(chunks):
        st = ch[0]["ini"]
        en = chunks[k + 1][0]["ini"] if k + 1 < len(chunks) else DUR
        if k + 1 < len(chunks) and chunks[k + 1][0]["frase"] != ch[-1]["frase"]:
            en = min(en, ch[-1]["fin"] + 0.35)
        spans = []
        for j, p in enumerate(ch):
            wid = f"w{k}_{j}"
            spans.append(f'<span id="{wid}" class="sw">{p["w"]}</span>')
            c = CLAVE.get(norm(p["w"]))
            if c:
                J(f'tl.to("#{wid}", {{backgroundColor:"{c}", color:"#10181c", duration:0.08}}, {p["ini"]:.2f});')
            else:
                J(f'tl.to("#{wid}", {{color:"#ffffff", duration:0.08}}, {p["ini"]:.2f});')
        SUBS.append(f'<div id="sub{k}" class="clip sub" data-start="{st:.3f}" data-duration="{max(0.2, en - st):.3f}" data-track-index="3">{" ".join(spans)}</div>')

# ------------------------------------------------------------------ HTML final
html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:{TEAL2}}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif}}
#fondo{{position:absolute;inset:0;background:radial-gradient(120% 70% at 50% 40%, #3b8086 0%, {TEAL1} 45%, {TEAL2} 100%)}}
#lejos{{position:absolute;left:0;top:0;width:{WORLD_W}px;height:1920px}}
.blob{{position:absolute;border-radius:50%;background:#bfe6e0;filter:blur(30px)}}
#world{{position:absolute;left:0;top:0;width:{WORLD_W}px;height:{WORLD_H}px;transform-origin:0 0}}
.pared-luz{{position:absolute;top:0;width:900px;height:{FLOOR_Y}px;background:radial-gradient(60% 55% at 50% 40%, rgba(255,240,215,0.16), rgba(255,240,215,0) 70%)}}
#rodapie{{position:absolute;left:0;top:{FLOOR_Y - 90}px;width:{WORLD_W}px;height:90px;background:linear-gradient(#efe6d2,#d9ccb2)}}
#suelo{{position:absolute;left:0;top:{FLOOR_Y}px;width:{WORLD_W}px;height:{WORLD_H - FLOOR_Y}px;
  background:repeating-linear-gradient(180deg,{WOOD1} 0 116px,#7a4f33 116px 120px),linear-gradient({WOOD1},{WOOD2})}}
#suelo:after{{content:"";position:absolute;inset:0;background:linear-gradient(rgba(0,0,0,0.25),rgba(0,0,0,0) 30%)}}
.card{{position:absolute;background:#fbf8f2;border-radius:28px;box-shadow:0 18px 40px rgba(0,0,0,0.25);padding:26px 34px}}
.card-top{{font:900 34px Inter;letter-spacing:0.08em;color:#8a8277}}
.card-big{{font:900 92px Inter;line-height:1.05}}
.badge{{position:absolute;padding:18px 30px;border-radius:22px;color:#fff;font:900 46px Inter;box-shadow:0 12px 30px rgba(0,0,0,0.25)}}
.btn{{position:absolute;width:380px;height:150px;border-radius:40px;color:#fff;font:900 64px Inter;display:flex;align-items:center;justify-content:center;box-shadow:0 18px 40px rgba(0,0,0,0.3)}}
.rod{{position:absolute;display:flex;font-family:Inter;font-weight:900;line-height:1.15;overflow:hidden}}
.rod-col{{overflow:hidden}} .rod-strip div{{height:1.15em}}
.rod-sep{{padding:0 2px}}
.regla{{position:absolute;width:70px;border-radius:12px;background:repeating-linear-gradient(180deg,#f2d27a 0 34px,#3a3324 34px 38px);box-shadow:0 10px 24px rgba(0,0,0,0.25)}}
.cinta{{position:absolute;width:90px;border-radius:10px;background:repeating-linear-gradient(180deg,#f4e3a1 0 37px,#3a3324 37px 41px);box-shadow:0 10px 24px rgba(0,0,0,0.25)}}
.cinta-tag{{position:absolute;left:110px;bottom:-30px;background:{GOOD};color:#fff;font:900 54px Inter;padding:10px 22px;border-radius:18px;white-space:nowrap}}
.reloj{{position:absolute;width:220px;height:220px;border-radius:50%;background:#fbf8f2;border:12px solid #d8cdbb;box-shadow:0 14px 30px rgba(0,0,0,0.25)}}
.aguja{{position:absolute;left:94px;bottom:98px;width:8px;border-radius:6px;background:#1d2b33;transform-origin:50% 100%}}
.mota{{position:absolute;width:10px;height:10px;border-radius:50%;background:#fff6e0}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:170px;display:flex;align-items:center;justify-content:center}}
.sub{{position:absolute;left:0;right:0;text-align:center;font:900 64px Inter;color:rgba(255,255,255,0.45);text-shadow:0 4px 14px rgba(0,0,0,0.45);line-height:1.25}}
.sw{{display:inline-block;padding:2px 12px;border-radius:14px}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="fondo"></div>
  <div id="lejos">{"".join(LEJOS)}</div>
  <div id="world" data-layout-allow-overflow data-layout-ignore>
    {"".join(f'<div class="pared-luz" style="left:{x - 450}px"></div>' for x in ST.values())}
    <div id="rodapie"></div><div id="suelo"></div>
    {"".join(MOTAS)}
    {"".join(H)}
  </div>
  <div id="subs" data-layout-allow-overlap>{"".join(SUBS)}</div>
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
json.dump(FX_EV, open(os.path.join(BASE, "efectos.json"), "w"))
print(f"index.html ({'sin' if SIN_SUBS else 'con'} subtítulos) · {DUR:.1f}s · {len(tl)} animaciones · {len(FX_EV)} efectos")

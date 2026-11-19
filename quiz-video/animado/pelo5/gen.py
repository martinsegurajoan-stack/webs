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
TEAL1, TEAL2 = "#7b7fc4", "#4c4f93"
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
    """Mechón que nace del casco POR FUERA de la cara y cae sobre el hombro hasta `bottom`."""
    s = -1 if side == "L" else 1
    X = lambda d: FX + s * d
    return (f"M{X(100)},735 C{X(112)},722 {X(124)},726 {X(132)},745 "            # sale del casco
            f"C{X(158)},780 {X(186)},900 {X(178)},{min(bottom - 40, 1000)} "    # borde exterior hasta el hombro
            f"C{X(172)},{bottom - 30} {X(158)},{bottom - 6} {X(140)},{bottom + 16} "  # punta
            f"C{X(126)},{bottom - 10} {X(122)},{bottom - 40} {X(120)},{min(bottom - 60, 980)} "
            f"C{X(118)},900 {X(114)},820 {X(108)},760 "                            # borde interior: pegado a la mejilla, sin entrar
            f"C{X(106)},740 {X(103)},738 {X(100)},735 Z")

def side_path(side, bottom):
    """Melena corta (10-25 cm) que tapa las orejas, por fuera de la cara."""
    s = -1 if side == "L" else 1
    X = lambda d: FX + s * d
    return (f"M{X(96)},680 C{X(122)},670 {X(132)},700 {X(134)},740 "
            f"C{X(138)},790 {X(132)},{bottom - 20} {X(122)},{bottom + 8} "
            f"L{X(110)},{bottom - 6} C{X(110)},{bottom - 40} {X(108)},790 {X(104)},740 "
            f"C{X(102)},710 {X(100)},690 {X(96)},680 Z")

def strands(path_kind, side, bottom, n=7):
    """Líneas finas de textura dentro del mechón."""
    s = -1 if side == "L" else 1
    out = []
    for i in range(n):
        k = (i + 0.5) / n
        xt = FX + s * (112 + 16 * k)
        xm = FX + s * (126 + 40 * k)
        xb = FX + s * (126 + 32 * k)
        out.append(f'<path d="M{xt:.0f},760 C{xm:.0f},850 {xm:.0f},{(760 + bottom) / 2:.0f} {xb:.0f},{bottom - 20}" '
                   f'stroke="{HAIR_HI}" stroke-width="2.2" fill="none" opacity="0.45"/>')
    return "".join(out)

def beard_path(L):
    """Barba que sigue la mandíbula; L = cuánto cuelga por debajo de la barbilla."""
    return (f"M404,796 C404,850 424,{884 + L * 0.4:.0f} 455,{904 + L * 0.8:.0f} C474,{918 + L} 526,{918 + L} 545,{904 + L * 0.8:.0f} "
            f"C576,{884 + L * 0.4:.0f} 596,850 596,796 C590,826 574,846 548,850 C530,842 470,842 452,850 C426,846 410,826 404,796 Z")

MUST = "M460,813 C474,796 494,800 500,807 C506,800 526,796 540,813 C523,808 509,813 500,813 C491,813 477,808 460,813 Z"
HEAD_D = "M395,765 C395,690 440,642 500,642 C560,642 605,690 605,765 C605,826 590,868 556,890 C536,903 464,903 444,890 C410,868 395,826 395,765 Z"

HEADSC = "translate(500 905) scale(0.86) translate(-500 -905)"

def personaje(pid, cm=None, bald=False, stubble=False, beard=None):
    """SVG del personaje. cm = largo de pelo (None = calvo)."""
    g = []
    defs = f"""<defs>
<radialGradient id="{pid}-skin" cx="0.38" cy="0.32" r="0.8"><stop offset="0" stop-color="#f7d3b6"/><stop offset="1" stop-color="{SKIN_D}"/></radialGradient>
<linearGradient id="{pid}-shirt" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ea8d72"/><stop offset="1" stop-color="{SHIRT_D}"/></linearGradient>
<linearGradient id="{pid}-hair" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5d3c29"/><stop offset="1" stop-color="#3a2418"/></linearGradient>
<linearGradient id="{pid}-beard" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b8693a"/><stop offset="1" stop-color="#8a4626"/></linearGradient>
</defs>"""
    g.append(defs)
    bottom = 760 + (cm or 0) * 6.3
    # sombra en el suelo
    g.append(f'<ellipse cx="500" cy="1702" rx="190" ry="26" fill="#000" opacity="0.22"/>')
    # melena de detrás (asoma por los lados)
    if cm and cm >= 25:
        g.append(f'<g transform="{HEADSC}"><path d="M390,760 C370,900 360,1000 352,{bottom - 20} L648,{bottom - 20} C640,1000 630,900 610,760 Z" fill="url(#{pid}-hair)"/></g>')
    # piernas y zapatos
    g.append(f'<g id="{pid}-legs"><path d="M372,1250 L628,1250 L620,1300 L380,1300 Z" fill="{PANTS}"/>'
             f'<g id="{pid}-legL"><path d="M385,1290 L490,1290 L482,1680 L400,1680 Z" fill="{PANTS}"/>'
             f'<path d="M470,1300 L466,1670" stroke="#2f3250" stroke-width="3" opacity="0.6"/>'
             f'<path d="M382,1694 C382,1668 410,1660 440,1662 C470,1662 496,1672 496,1694 Z" fill="#f4efe6"/><rect x="380" y="1690" width="118" height="12" rx="6" fill="#cfc6b8"/></g>'
             f'<g id="{pid}-legR"><path d="M510,1290 L615,1290 L600,1680 L518,1680 Z" fill="#363955"/>'
             f'<path d="M530,1300 L536,1670" stroke="#2a2d48" stroke-width="3" opacity="0.6"/>'
             f'<path d="M504,1694 C504,1668 532,1660 562,1662 C592,1662 618,1672 618,1694 Z" fill="#f4efe6"/><rect x="502" y="1690" width="118" height="12" rx="6" fill="#cfc6b8"/></g></g>')
    # cuerpo que respira (torso + brazos + cabeza)
    g.append(f'<g id="{pid}-up">')
    for side, sx, rot in (("L", 356, 1), ("R", 644, -1)):
        g.append(f'<g id="{pid}-arm{side}"><g id="{pid}-arm{side}g">'
                 f'<path d="M{sx - 26 * rot},975 C{sx - 48 * rot},1030 {sx - 52 * rot},1090 {sx - 46 * rot},1120 L{sx - 6 * rot},1120 C{sx - 4 * rot},1080 {sx},1030 {sx + 12 * rot},990 Z" fill="url(#{pid}-shirt)"/>'
                 f'<path d="M{sx - 42 * rot},1112 C{sx - 46 * rot},1180 {sx - 40 * rot},1240 {sx - 36 * rot},1262 L{sx - 10 * rot},1262 C{sx - 12 * rot},1230 {sx - 10 * rot},1170 {sx - 8 * rot},1112 Z" fill="{SKIN}"/>'
                 f'<circle cx="{sx - 24 * rot}" cy="1280" r="27" fill="{SKIN}"/></g></g>')
    g.append(f'<path d="M350,992 C350,960 396,950 440,946 L560,946 C604,950 650,960 650,992 L628,1270 L372,1270 Z" fill="url(#{pid}-shirt)"/>')
    g.append(f'<path d="M560,948 C604,952 650,962 650,992 L628,1270 L548,1270 C566,1150 572,1040 560,948 Z" fill="#b5553f" opacity="0.35"/>')
    g.append(f'<path d="M378,1240 L622,1240" stroke="#b5553f" stroke-width="4" opacity="0.45"/>')
    g.append(f'<path d="M455,952 Q500,985 545,952" stroke="{SHIRT_D}" stroke-width="7" fill="none"/>')
    g.append(f'<rect x="462" y="866" width="76" height="94" rx="22" fill="{SKIN_D}"/>')
    g.append(f'<ellipse cx="500" cy="906" rx="36" ry="8" fill="#c98b6c" opacity="0.3"/>')
    # cabeza (algo más pequeña: proporciones de adulto)
    g.append(f'<g transform="{HEADSC}">')
    g.append(f'<g id="{pid}-headw"><g id="{pid}-head">')
    g.append(f'<ellipse cx="396" cy="775" rx="18" ry="28" fill="{SKIN_D}"/><ellipse cx="604" cy="775" rx="18" ry="28" fill="{SKIN_D}"/>')
    g.append(f'<path d="{HEAD_D}" fill="url(#{pid}-skin)"/>')
    if bald:
        g.append('<ellipse cx="465" cy="690" rx="34" ry="18" fill="#fff" opacity="0.35" transform="rotate(-20 465 690)"/>')
    g.append('<path d="M410,800 C420,850 450,880 500,888 C550,880 580,850 590,800 C580,860 545,896 500,898 C455,896 420,860 410,800 Z" fill="#d9967a" opacity="0.35"/>')
    eye = lambda cx: (f'<ellipse cx="{cx}" cy="744" rx="17" ry="11" fill="#fbf6f0"/>'
                      f'<circle cx="{cx + 1}" cy="745" r="8.5" fill="#4a3426"/><circle cx="{cx + 1}" cy="745" r="4.2" fill="#15100e"/><circle cx="{cx + 4}" cy="741" r="2.4" fill="#fff"/>'
                      f'<path d="M{cx - 19},742 Q{cx},727 {cx + 19},742" stroke="#3a2418" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
                      f'<path d="M{cx - 14},755 Q{cx},761 {cx + 14},755" stroke="#c98a6c" stroke-width="2" fill="none" opacity="0.7"/>')
    g.append(f'<g id="{pid}-eyes">{eye(462)}{eye(538)}</g>')
    g.append(f'<g id="{pid}-brows"><path d="M440,718 Q461,707 484,713" stroke="#4a2f22" stroke-width="8" fill="none" stroke-linecap="round"/>'
             f'<path d="M516,713 Q539,707 560,718" stroke="#4a2f22" stroke-width="8" fill="none" stroke-linecap="round"/></g>')
    g.append('<path d="M500,752 C497,770 490,782 492,790 C496,796 506,796 512,791" stroke="#b97b5f" stroke-width="4" fill="none" stroke-linecap="round"/>'
             '<path d="M486,792 Q500,800 514,792" stroke="#d9967a" stroke-width="3" fill="none" opacity="0.6"/>')
    if beard is not None:
        tex = "".join(f'<path d="M{x},{858 + abs(x - 500) * 0.1:.0f} q{(x - 500) * 0.04:.1f},{14 + beard * 0.5:.0f} {(x - 500) * 0.02:.1f},{24 + beard * 0.75:.0f}" stroke="#d48a55" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.55"/>'
                      for x in range(440, 561, 20))
        g.append(f'<path id="{pid}-beard" d="{beard_path(beard)}" fill="url(#{pid}-beard)" stroke="#6e3519" stroke-width="4" stroke-linejoin="round"/>{tex}'
                 f'<path d="{MUST}" fill="#9a5230" stroke="#6e3519" stroke-width="3"/>')
    if stubble:
        g.append(f'<path id="{pid}-beardfade" d="{beard_path(0)}" fill="#a85d34" opacity="0"/>')
    g.append(f'<path id="{pid}-mouth" d="M478,816 Q500,832 522,816" stroke="#7a3f35" stroke-width="4.5" fill="none" stroke-linecap="round"/>')
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
        g.append(f'<path id="{pid}-one" d="M500,650 L500,642 C494,600 532,592 522,560 C514,538 538,528 544,516" stroke="{HAIR}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    if cm:
        v = min(4 + cm * 1.4, 22)
        if 10 <= cm < 25:
            for sd in ("L", "R"):
                g.append(f'<path d="{side_path(sd, bottom)}" fill="url(#{pid}-hair)"/>')
        g.append(f'<path d="{cap_path(v)}" fill="url(#{pid}-hair)"/>')
        g.append(f'<path d="M430,670 Q500,640 570,668" stroke="{HAIR_HI}" stroke-width="4" fill="none" opacity="0.6"/>')
        if cm < 12:
            g.append(f'<path id="{pid}-fringe" d="{fringe_path(20)}" fill="url(#{pid}-hair)"/>')
    g.append('</g></g>')   # head + headw
    if cm and cm >= 25:
        for sd in ("L", "R"):
            g.append(f'<g id="{pid}-lock{sd}"><path d="{lock_path(sd, bottom)}" fill="url(#{pid}-hair)"/>{strands("lock", sd, bottom)}</g>')
    g.append('</g>')   # escala cabeza
    g.append('</g>')   # up
    return f'<svg class="pj" id="{pid}" viewBox="0 0 1000 1800" width="1000" height="1800" style="position:absolute;left:{{x}}px;top:0px;overflow:visible">' + "".join(g) + "</svg>"

def pj_at(pid, sx, **kw):
    return personaje(pid, **kw).replace("{x}", str(sx - 500))

def vida(pid):
    """Respira y parpadea durante todo el vídeo (nunca congelado)."""
    reps = int(DUR / 1.7)
    J(f'tl.fromTo("#{pid}-up", {{scaleY:1}}, {{scaleY:1.012, duration:0.85, ease:"sine.inOut", yoyo:true, repeat:{reps}, svgOrigin:"500 1270"}}, 0);')
    for sel, amp, n, org in ((f"{pid}-up", 1.1, 13, "500 1290"), (f"{pid}-headw", 2.2, 17, "500 900"),
                             (f"{pid}-armL", 2.5, 15, "356 985"), (f"{pid}-armR", -2.5, 14, "644 985")):
        J(f'tl.to("#{sel}", {{keyframes:{{rotation:[0, {amp}, 0, {-amp}, 0], easeEach:"sine.inOut"}}, duration:{DUR / n:.4f}, ease:"none", repeat:{n - 1}, svgOrigin:"{org}"}}, 0);')
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
VIAJES = [0]
def punch(t, s=1.07, dur=0.5):
    J(f'tl.fromTo("#camB", {{scale:{s}}}, {{scale:1, duration:{dur}, ease:"power3.out", immediateRender:false}}, {t:.2f});')

def angulo(t, rot, dur=0.35, hold=None, back=0.5):
    J(f'tl.to("#camB", {{rotation:{rot}, duration:{dur}, ease:"power3.out"}}, {t:.2f});')
    if hold is not None:
        J(f'tl.to("#camB", {{rotation:0, duration:{back}, ease:"power2.inOut"}}, {t + hold:.2f});')

def cam(t, x, y, z, dur=1.0, ease="power3.inOut", viaje=False):
    J(f'tl.to("#world", {{x:{540 - x * z:.1f}, y:{960 - y * z:.1f}, scale:{z}, duration:{dur}, ease:"{ease}"}}, {t:.2f});')
    J(f'tl.to("#lejos", {{x:{(540 - x * z) * 0.35:.1f}, duration:{dur}, ease:"{ease}"}}, {t:.2f});')
    if viaje:
        J(f'tl.to("#world", {{filter:"blur(5px)", duration:{dur / 2:.2f}, ease:"sine.in"}}, {t:.2f});')
        J(f'tl.to("#world", {{filter:"blur(0px)", duration:{dur / 2:.2f}, ease:"sine.out"}}, {t + dur / 2:.2f});')
        FX_EV.append(("whoosh", t))
        VIAJES[0] += 1
        sg = 1 if VIAJES[0] % 2 else -1
        J(f'tl.to("#camB", {{rotation:{3.5 * sg}, duration:{dur / 2:.2f}, ease:"sine.in"}}, {t:.2f}); tl.to("#camB", {{rotation:0, duration:{dur / 2:.2f}, ease:"back.out(1.6)"}}, {t + dur / 2:.2f});')
        punch(t + dur * 0.92, 1.06, 0.6)

# ------------------------------------------------------------------ construcción del mundo
H = []   # HTML del mundo
s0, s1, s2, s3, s4, s5, s6 = (ST[k] for k in ("s0", "s1", "s2", "s3", "s4", "s5", "s6"))

# camino que une las estaciones (se dibuja mientras viaja la cámara)
path_d = f"M{s0},1760 " + " ".join(f"C{a + 500},1700 {b - 500},1820 {b},1760" for a, b in zip(list(ST.values())[:-1], list(ST.values())[1:]))
H.append(f'<svg style="position:absolute;left:0;top:0" width="{WORLD_W}" height="{WORLD_H}"><path id="camino" d="{path_d}" stroke="#ffe3d3" '
         f'stroke-width="10" fill="none" stroke-linecap="round" stroke-dasharray="1 0" opacity="0.85"/>'
         + "".join(f'<circle id="nodo{i}" cx="{x}" cy="1760" r="22" fill="{CREAM}" stroke="{TEAL2}" stroke-width="6"/>' for i, x in enumerate(ST.values()))
         + "</svg>")

# S0: calvo con un pelo → cien mil pelitos
H.append(pj_at("p0", s0, bald=True, stubble=True))
r_html, r_n, r_d, r_h = rodillo("rod0", s0 + 205, 1035, "100.000", size=80)
H.append(f'<div id="c0" class="card" style="left:{s0 + 165}px;top:950px;width:500px;height:215px"><div class="card-top">PELOS EN LA CABEZA</div></div>')
H.append(r_html)
H.append(f'<div id="regla0" class="regla" style="left:{s0 - 300}px;top:650px;height:420px"></div>')
H.append(f'<div id="cal0" class="card" style="left:{s0 - 450}px;top:1110px;width:300px"><div class="card-top">CRECE</div><div class="card-big" style="color:{GOOD}">≈1 cm<span style="font-size:44px">/mes</span></div></div>')

# S1: mes 6 (flequillo)
H.append(pj_at("p1", s1, cm=7, beard=0))
H.append(card("c1", s1 + 170, 1130, "MES 6", "7 cm"))
H.append(f'<svg id="peine" style="position:absolute;left:{s1 - 260}px;top:600px" width="260" height="90" viewBox="0 0 260 90"><rect x="0" y="0" width="260" height="30" rx="12" fill="#e9d7b5"/>'
         + "".join(f'<rect x="{8 + i * 12}" y="26" width="6" height="56" rx="3" fill="#e9d7b5"/>' for i in range(21)) + "</svg>")
H.append(f'<div id="x1" class="badge" style="left:{s1 - 450}px;top:550px;background:{BAD}">✕ NO AGUANTA</div>')

# S2: año 2 (nudos, secado)
H.append(pj_at("p2", s2, cm=30, beard=35))
H.append(card("c2", s2 + 170, 1150, "AÑO 2", "30 cm"))
H.append(f'<svg id="cepillo" style="position:absolute;left:{s2 + 85}px;top:790px" width="150" height="260" viewBox="0 0 150 260">'
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
H.append(f'<div id="marco" style="position:absolute;left:{s3 - 520}px;top:760px;width:270px;height:640px;background:#e9dccb;border-radius:12px;box-shadow:0 18px 40px rgba(30,20,60,0.35)"></div>')
H.append(f'<div id="hueco" style="position:absolute;left:{s3 - 505}px;top:775px;width:240px;height:625px;background:linear-gradient(90deg,#2a2440,#3d3560);border-radius:6px"></div>')
# mechón atrapado (se dibuja ANTES de la puerta: su punta queda escondida en el hueco)
LOCK_SUELTO = f"M{s3 - 165},930 C{s3 - 200},1010 {s3 - 230},1060 {s3 - 262},1075"
LOCK_TENSO = f"M{s3 - 165},930 C{s3 - 190},960 {s3 - 225},1000 {s3 - 262},1010"
H.append(f'<svg id="atrapado" style="position:absolute;left:0;top:0;overflow:visible" width="10" height="10">'
         f'<path id="atr-a" d="{LOCK_SUELTO}" stroke="#4e3122" stroke-width="34" fill="none" stroke-linecap="round"/>'
         f'<path id="atr-b" d="{LOCK_SUELTO}" stroke="#6b4530" stroke-width="18" fill="none" stroke-linecap="round" opacity="0.7"/>'
         f'<path id="atr-c" d="{LOCK_SUELTO}" stroke="{HAIR_HI}" stroke-width="3" fill="none" opacity="0.6" stroke-dasharray="30 14"/></svg>')
H.append(f'<svg id="pinza" style="position:absolute;left:{s3 - 300}px;top:950px;overflow:visible" width="10" height="10">'
         + "".join(f'<path class="pz" d="M{x},{y} l{dx},{dy}" stroke="#fff" stroke-width="6" stroke-linecap="round"/>' for x, y, dx, dy in ((70, 20, 26, -16), (78, 60, 30, 0), (70, 100, 26, 16)))
         + '</svg>')
H.append(f'<div id="puerta" style="position:absolute;left:{s3 - 505}px;top:775px;width:240px;height:625px;background:linear-gradient(90deg,#5f7e74,#4d6a61);border-radius:6px;transform-origin:0 50%">'
         f'<div style="position:absolute;right:22px;top:300px;width:22px;height:22px;border-radius:50%;background:#e2c27a"></div></div>')
H.append(pj_at("p3", s3, cm=45, beard=60))
H.append(card("c3", s3 + 165, 1150, "AÑO 3", "45 cm"))
H.append(f'<svg id="zip" style="position:absolute;left:{s3 - 10}px;top:960px" width="20" height="310"><line x1="10" y1="0" x2="10" y2="310" stroke="#d8c7a3" stroke-width="8" stroke-dasharray="6 5"/></svg>')
H.append(f'<svg id="mechonzip" style="position:absolute;left:{s3 + 12}px;top:985px;overflow:visible" width="10" height="10"><path d="M0,10 C30,0 50,30 90,20 C110,15 125,30 140,40" stroke="#4e3122" stroke-width="10" fill="none" stroke-linecap="round"/></svg>')
H.append(f'<div id="slider" style="position:absolute;left:{s3 - 16}px;top:1240px;width:32px;height:46px;background:#d9b456;border-radius:6px"></div>')
H.append(f'<svg id="mesa" style="position:absolute;left:{s3 + 22}px;top:1065px;overflow:visible" width="320" height="610">'
         '<rect x="140" y="60" width="40" height="557" rx="12" fill="#b9876a"/><ellipse cx="160" cy="623" rx="90" ry="18" fill="#a97a5f"/>'
         '<ellipse cx="160" cy="62" rx="160" ry="34" fill="#c99a7c"/><ellipse cx="160" cy="54" rx="160" ry="32" fill="#e3bb98"/></svg>')
H.append(f'<svg id="sopa" style="position:absolute;left:{s3 + 62}px;top:985px;overflow:visible" width="240" height="170" viewBox="0 0 240 170">'
         '<path d="M6,70 Q120,205 234,70 Z" fill="#f4ede2"/><path d="M30,110 Q120,170 210,110" stroke="#e07a5f" stroke-width="8" fill="none" opacity="0.6"/>'
         '<ellipse cx="120" cy="70" rx="114" ry="22" fill="#e5a24e"/><ellipse cx="96" cy="66" rx="30" ry="6" fill="#f6c477"/>'
         + "".join(f'<path class="vapor" d="M{80 + i * 40},48 q-14,-25 0,-45 q14,-20 0,-45" stroke="#fff" stroke-width="6" fill="none" opacity="0"/>' for i in range(3))
         + "".join(f'<circle class="gota" cx="{86 + i * 9}" cy="68" r="{8 - i}" fill="#f2b45f" opacity="0"/>' for i in range(5))
         + f'<path id="flota" d="M96,74 C112,64 128,82 146,70 C160,62 172,76 184,70" stroke="#4b3021" stroke-width="7" fill="none" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
         + "".join(f'<ellipse class="onda" cx="104" cy="72" rx="16" ry="4" stroke="#fbe0b0" stroke-width="3" fill="none" opacity="0"/>' for i in range(2))
         + "</svg>")

# S4: clímax (gráfica que se aplana, 2-7 años, ADN, caída y nuevo pelo)
H.append(f'<div id="graf" class="card" style="left:{s4 - 430}px;top:520px;width:860px;height:560px"><div class="card-top">CRECIMIENTO DE TU PELO</div></div>')
H.append(f'<svg id="grafsvg" style="position:absolute;left:{s4 - 400}px;top:590px" width="800" height="470" viewBox="0 0 800 470">'
         '<line x1="40" y1="430" x2="780" y2="430" stroke="#c9c2b6" stroke-width="5"/><line x1="40" y1="20" x2="40" y2="430" stroke="#c9c2b6" stroke-width="5"/>'
         + "".join(f'<text x="{40 + i * 148}" y="465" font-size="28" font-family="Inter" font-weight="700" fill="#8a8277">{i}</text>' for i in range(6))
         + f'<path id="curva" d="M40,420 C180,330 320,220 480,140" stroke="{GOOD}" stroke-width="12" fill="none" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
         + f'<path id="curva2" d="M480,140 L780,140" stroke="{BAD}" stroke-width="12" fill="none" stroke-linecap="round" stroke-dasharray="18 14" opacity="0.9"/>'
         + '<text x="54" y="44" font-size="26" font-family="Inter" font-weight="800" fill="#8a8277">cm</text><text x="700" y="412" font-size="26" font-family="Inter" font-weight="800" fill="#8a8277">años</text>'
         + f'<g id="stop"><circle cx="480" cy="140" r="34" fill="{BAD}"/><rect x="465" y="125" width="30" height="30" rx="4" fill="#fff"/></g></svg>')
H.append(f'<div id="barra" class="card" style="left:{s4 - 430}px;top:1150px;width:860px;height:170px"><div class="card-top">CADA PELO CRECE</div>'
         f'<div style="position:absolute;left:40px;top:92px;width:780px;height:40px;border-radius:20px;background:#ece6db"></div>'
         f'<div id="barfill" style="position:absolute;left:40px;top:92px;width:780px;height:40px;border-radius:20px;background:{KEY};transform-origin:0 50%"></div>'
         f'<div style="position:absolute;right:40px;top:12px;font:900 56px Inter;color:#1d2b33">2 → 7 años</div></div>')
helix = []
for i in range(14):
    y = 20 + i * 26
    xa = 70 + 50 * math.sin(i * 0.6)
    helix.append(f'<line class="adnR" x1="{xa:.1f}" y1="{y}" x2="{140 - xa:.1f}" y2="{y}" stroke="#ffffff" stroke-width="4" opacity="0.55"/>'
                 f'<circle class="adnA" cx="{xa:.1f}" cy="{y}" r="11" fill="{GOOD}"/><circle class="adnB" cx="{140 - xa:.1f}" cy="{y}" r="11" fill="{KEY}"/>')
H.append(f'<div class="plato" style="left:{s4 + 740 - 380}px;top:1625px"></div>')
H.append(pj_at("p4", s4 + 740, cm=60, beard=95))
H.append(f'<svg id="adn" style="position:absolute;left:{s4 + 300}px;top:800px;overflow:visible" width="140" height="380">{"".join(helix)}</svg>')
H.append(f'<svg id="foliculo" style="position:absolute;left:{s4 + 100}px;top:1190px;overflow:visible" width="300" height="240" viewBox="0 0 300 240">'
         f'<defs><linearGradient id="piel-cut" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f7d6bd"/><stop offset="0.25" stop-color="{SKIN}"/><stop offset="1" stop-color="#e6a98a"/></linearGradient></defs>'
         f'<rect x="0" y="150" width="300" height="100" rx="22" fill="url(#piel-cut)"/><rect x="0" y="150" width="300" height="18" rx="9" fill="#fbe1cc"/>'
         f'<path d="M20,198 q20,8 40,0 M88,212 q20,8 40,0 M200,202 q20,8 40,0 M236,226 q14,6 28,0" stroke="#e8b294" stroke-width="4" fill="none"/>'
         f'<path d="M150,158 C136,190 138,218 150,232 C162,218 164,190 150,158 Z" fill="#d99a7c"/>'
         f'<circle id="brillo" cx="150" cy="228" r="20" fill="#fff3c4" opacity="0"/>'
         f'<circle id="bulbo" cx="150" cy="228" r="12" fill="#c98468"/>'
         f'<path id="pelo-nuevo" d="M150,228 C150,200 150,175 150,152 C147,128 156,108 150,84" stroke="{HAIR}" stroke-width="7" fill="none" stroke-linecap="butt" pathLength="1" stroke-dasharray="1 2" stroke-dashoffset="1"/>'
         f'<path id="pelo-viejo" d="M150,224 C150,200 150,175 150,152 C142,126 156,110 148,88" stroke="{HAIR}" stroke-width="7" fill="none" stroke-linecap="round"/>'
         f'<text x="150" y="292" text-anchor="middle" font-size="24" font-family="Inter" font-weight="900" letter-spacing="2" fill="#fff">RAÍZ DEL PELO</text></svg>')

# S5: año 5 (75 cm, cinta métrica)
H.append(pj_at("p5", s5, cm=75, beard=120))
H.append(f'<div id="cinta" class="cinta" style="left:{s5 + 230}px;top:760px;height:472px"><div class="cinta-tag">75 cm</div></div>')
H.append(card("c5", s5 - 480, 1080, "AÑO 5", "75 cm", color=GOOD, w=260))

# S6: pelos perdidos + llamada a la acción
H.append(f'<div id="panel" class="card" style="left:{s6 - 430}px;top:560px;width:860px;height:430px"><div class="card-top">PELOS PERDIDOS EN 5 AÑOS</div>'
         f'<div id="guion6" style="position:absolute;left:368px;top:150px;font:900 56px Inter;color:#8a8277;opacity:0">–</div>'
         f'<div style="position:absolute;left:0;right:0;top:330px;text-align:center;font:700 40px Inter;color:#8a8277">de 50 a 100 al día · normal</div></div>')
ra, ran, rad_, rah = rodillo("rodA", s6 - 395, 690, "90.000", size=84)
rb, rbn, rbd, rbh = rodillo("rodB", s6 - 15, 690, "180.000", size=84, color=BAD)
H.append(ra); H.append(rb)
falling = []
for i in range(44):
    x = s6 - 420 + random.uniform(0, 840)
    falling.append(f'<svg class="caen" id="caen{i}" style="position:absolute;left:{x:.0f}px;top:1000px;overflow:visible" width="60" height="60">'
                   f'<path d="M5,5 C25,15 10,35 40,50" stroke="{HAIR}" stroke-width="7" fill="none" stroke-linecap="round"/></svg>')
H.append("".join(falling))
# ------------------------------------------------------------------ guion → animación (todo con P())
for pid in ("p0", "p1", "p2", "p3", "p4", "p5"):
    vida(pid)

# estado inicial (y final, para el bucle)
J('tl.set("#world", {x:%.1f, y:%.1f, scale:1.55}, 0);' % (540 - s0 * 1.55, 960 - 760 * 1.55))
J('tl.set("#lejos", {x:%.1f}, 0);' % ((540 - s0 * 1.55) * 0.35))
for sel in ["#c0", "#rod0", "#regla0", "#cal0", "#c1", "#peine", "#x1", "#c2", "#cepillo", "#secador", "#reloj", "#c3", "#tenso", "#zip", "#slider",
            "#sopa", "#mesa", "#graf", "#grafsvg", "#barra", "#adn", "#foliculo", "#cinta", "#c5", "#panel", "#rodA", "#rodB", "#stop"]:
    J(f'tl.set("{sel}", {{opacity:0}}, 0);')
J('tl.set("#camino", {strokeDasharray:"0 20000"}, 0);')
J('tl.set(".caen", {opacity:0}, 0);')

# 1 · gancho: arranque potente (golpe de zoom + el pelo solitario hace «boing»)
J('tl.fromTo("#world", {scale:1.85}, {scale:1.55, duration:0.55, ease:"power3.out"}, 0);')
J('tl.fromTo("#p0-one", {rotation:-28}, {rotation:0, duration:1.4, ease:"elastic.out(1.2,0.25)", svgOrigin:"500 646", immediateRender:false}, 0.05);')
FX_EV.append(("golpe", 0.0))
J(f'tl.to("#p0-one", {{rotation:14, duration:0.35, yoyo:true, repeat:3, ease:"sine.inOut", svgOrigin:"500 646"}}, {P("pelo", 1):.2f});')
# 2 · «un pelo» → «cien mil»
J(f'tl.fromTo("#p0-one", {{scale:1}}, {{scale:1.35, duration:0.3, yoyo:true, repeat:1, svgOrigin:"500 646"}}, {P("pelo", 2):.2f});')
J(f'tl.to("#p0-mouthO", {{opacity:1, duration:0.15}}, {P("bueno"):.2f}); tl.to("#p0-mouth", {{opacity:0, duration:0.15}}, {P("bueno"):.2f});')
tc = P("cien")
J(f'tl.to(".p0-stub", {{opacity:1, duration:0.12, stagger:{{each:0.004, from:"random"}}}}, {tc:.2f});')
J(f'tl.to("#p0-capfade", {{opacity:0.55, duration:1.0}}, {tc + 0.2:.2f}); tl.to("#p0-beardfade", {{opacity:0.25, duration:1.0}}, {tc + 0.2:.2f});')
J(f'tl.to("#world", {{scale:1.05, x:{540 - (s0 + 200) * 1.05:.1f}, y:{960 - 900 * 1.05:.1f}, duration:0.9, ease:"power2.inOut"}}, {tc - 0.1:.2f});')
pop("#c0", tc); J(f'tl.to("#rod0", {{opacity:1, duration:0.2}}, {tc:.2f});')
rodar("rod0", r_n, r_d, r_h, tc)
FX_EV.append(("pop", tc + 0.3))
J(f'tl.to("#p0-mouthO", {{opacity:0, duration:0.15}}, {P("mil") + 0.3:.2f}); tl.to("#p0-mouth", {{opacity:1, duration:0.15}}, {P("mil") + 0.3:.2f});')
# 3 · crece ~1 cm al mes: regla + ficha; la cámara se aleja y enseña la estación entera
tcm = P("centimetro")
cam(P("crece") - 0.45, s0 + 20, 1000, 0.8, dur=0.7)   # primero se aleja la cámara, luego aparecen la regla y la ficha
J(f'tl.fromTo("#regla0", {{scaleY:0, opacity:1}}, {{scaleY:1, duration:0.6, ease:"power2.out", transformOrigin:"50% 0%", immediateRender:false}}, {P("crece") + 0.3:.2f});')
FX_EV.append(("pop", P("crece")))
pop("#cal0", tcm)

# 4 · UNO — mes 6: viaje por el camino hasta S1
t = F(5)
J(f'tl.to("#camino", {{strokeDasharray:"{s1 - s0 + 120} 20000", duration:1.0, ease:"power2.inOut"}}, {t:.2f});')
cam(t, s1, 1000, 0.95, dur=1.0, viaje=True)
pop("#c1", P("siete"))
cam(P("flequillo") - 0.35, s1, 780, 1.75, dur=0.6); J(f'tl.to("#c1", {{opacity:0, duration:0.25}}, {P("flequillo") - 0.4:.2f});')
J(f'tl.to("#p1-fringe", {{attr:{{d:"{fringe_path(56)}"}}, duration:0.7, ease:"power2.inOut"}}, {P("flequillo"):.2f});')
J(f'tl.to("#p1-mouth", {{attr:{{d:"M480,822 Q500,812 520,822"}}, duration:0.3}}, {P("ojos"):.2f});')
# 5 · ningún peinado aguanta: el peine pasa y el flequillo vuelve a caer
tp = P("peinado")
cam(tp - 0.3, s1 - 60, 820, 1.35, dur=0.5)
J(f'tl.fromTo("#peine", {{opacity:1, x:-120, y:0, rotation:-8}}, {{x:620, y:20, rotation:6, duration:0.9, ease:"power1.inOut"}}, {tp:.2f});')
J(f'tl.to("#p1-fringe", {{attr:{{d:"{fringe_path(22)}"}}, duration:0.35}}, {tp + 0.3:.2f});')
J(f'tl.to("#p1-fringe", {{attr:{{d:"{fringe_path(56)}"}}, duration:0.6, ease:"bounce.out"}}, {P("aguanta"):.2f});')
J(f'tl.to("#peine", {{opacity:0, duration:0.3}}, {tp + 1.0:.2f});')
pop("#x1", P("aguanta") + 0.1); J(f'tl.to("#x1", {{opacity:0, duration:0.25}}, {F(8) - 0.1:.2f});')
cam(FE(7) + 0.05, s1, 1000, 0.95, dur=0.5)

# 6 · DOS — año 2
t = F(8)
J(f'tl.to("#camino", {{strokeDasharray:"{s2 - s0 + 120} 20000", duration:1.0, ease:"power2.inOut"}}, {t:.2f});')
cam(t, s2, 1000, 0.95, dur=1.0, viaje=True)
pop("#c2", P("treinta"))
tn = P("nudos")
cam(tn - 0.3, s2 + 70, 920, 1.5, dur=0.6); J(f'tl.to("#c2", {{opacity:0, duration:0.25}}, {tn - 0.35:.2f});')
pop("#cepillo", tn, origin="50% 50%")
J(f'tl.to("#cepillo", {{y:190, rotation:-8, duration:0.32, ease:"sine.inOut", yoyo:true, repeat:5, transformOrigin:"50% 20%"}}, {tn + 0.4:.2f});')
J(f'tl.to("#cepillo", {{opacity:0, duration:0.25}}, {P("secarlo") - 0.35:.2f});')

J(f'tl.to("#p2-brows", {{y:6, duration:0.2}}, {tn + 0.2:.2f}); tl.to("#p2-mouth", {{attr:{{d:"M480,824 Q500,812 520,824"}}, duration:0.2}}, {tn + 0.2:.2f});')
ts = P("secarlo")
cam(ts - 0.3, s2 - 200, 900, 1.2, dur=0.6)
pop("#secador", ts)
J(f'tl.to("#secador .aire", {{opacity:1, x:30, duration:0.25, stagger:0.08, yoyo:true, repeat:7}}, {ts + 0.2:.2f});')
pop("#reloj", P("media"))
J(f'tl.fromTo("#aguja1", {{rotation:0}}, {{rotation:1440, duration:1.6, ease:"power2.inOut"}}, {P("manana"):.2f});')
J(f'tl.fromTo("#aguja2", {{rotation:0}}, {{rotation:180, duration:1.6, ease:"power2.inOut"}}, {P("manana"):.2f});')

cam(FE(10), s2, 1000, 0.95, dur=0.4)

# 7 · TRES — año 3: puerta, cremallera, sopa
t = F(11)
J(f'tl.to("#camino", {{strokeDasharray:"{s3 - s0 + 120} 20000", duration:1.0, ease:"power2.inOut"}}, {t:.2f});')
J(f'tl.set("#puerta", {{scaleX:0.25}}, 0);')
cam(t, s3, 1000, 0.95, dur=1.0, viaje=True)
pop("#c3", P("cuarenta"))
tq = P("puertas")
cam(tq - 0.4, s3 - 180, 950, 1.15, dur=0.5); J(f'tl.to("#c3", {{opacity:0, duration:0.25}}, {tq - 0.45:.2f});')
J(f'tl.to("#puerta", {{scaleX:1, duration:0.28, ease:"power4.in"}}, {tq:.2f});')
FX_EV.append(("portazo", tq + 0.28))
J(f'tl.set("#atrapado", {{opacity:0}}, 0); tl.set("#atrapado", {{opacity:1}}, {tq + 0.2:.2f});')
for i in "abc":
    J(f'tl.to("#atr-{i}", {{attr:{{d:"{LOCK_TENSO}"}}, duration:0.12, ease:"power3.out"}}, {tq + 0.28:.2f});')
J(f'tl.fromTo("#pinza .pz", {{opacity:0, scale:0.3}}, {{opacity:1, scale:1, duration:0.18, stagger:0.04, transformOrigin:"0% 50%"}}, {tq + 0.3:.2f});')
J(f'tl.to("#pinza .pz", {{opacity:0, duration:0.3}}, {tq + 1.1:.2f});')
J(f'tl.fromTo("#p3-head", {{rotation:0}}, {{rotation:-9, duration:0.16, ease:"power3.out", svgOrigin:"500 900"}}, {tq + 0.28:.2f});')
J(f'tl.to("#p3-head", {{rotation:-5, duration:0.12, yoyo:true, repeat:3, svgOrigin:"500 900"}}, {tq + 0.45:.2f});')
J(f'tl.to("#p3-head", {{rotation:0, duration:0.4, svgOrigin:"500 900"}}, {P("cremallera") - 0.4:.2f});')
J(f'tl.fromTo("#p3-up", {{x:0}}, {{x:-22, duration:0.16, ease:"power3.out"}}, {tq + 0.28:.2f}); tl.to("#p3-up", {{x:0, duration:0.4}}, {P("cremallera") - 0.4:.2f});')
J(f'tl.fromTo("#puerta", {{x:0}}, {{x:4, duration:0.05, yoyo:true, repeat:5}}, {tq + 0.28:.2f});')
J(f'tl.to("#p3-mouth", {{attr:{{d:"M482,826 Q500,812 518,826"}}, duration:0.15}}, {tq + 0.3:.2f});')
tz = P("cremallera")
J(f'tl.to("#atrapado", {{opacity:0, duration:0.25}}, {tz - 0.5:.2f}); tl.to("#puerta", {{scaleX:0.25, duration:0.35, ease:"power2.out"}}, {tz - 0.5:.2f});')
J(f'tl.to(["#marco", "#hueco", "#puerta"], {{opacity:0, duration:0.4}}, {tz - 0.2:.2f});')
cam(tz - 0.35, s3, 1080, 1.35, dur=0.5)
J(f'tl.to(["#zip","#slider"], {{opacity:1, duration:0.2}}, {tz - 0.1:.2f}); tl.to(["#zip","#slider"], {{opacity:0, duration:0.25}}, {P("acaba") - 0.3:.2f});')
J(f'tl.fromTo("#slider", {{y:0}}, {{y:-250, duration:0.8, ease:"power2.inOut"}}, {tz:.2f});')
J(f'tl.fromTo("#mechonzip", {{opacity:0, scale:0.3}}, {{opacity:1, scale:1, duration:0.3, ease:"back.out(2)", transformOrigin:"0% 50%"}}, {tz + 0.75:.2f});')
J(f'tl.to("#mechonzip", {{opacity:0, duration:0.25}}, {P("acaba") - 0.3:.2f});')
FX_EV.append(("clic", tz + 0.8))
tsop = P("sopa")
tl0 = P("dentro") - 0.15
cam(P("acaba") - 0.3, s3 + 120, 1000, 1.25, dur=0.6)
cam(tl0 + 0.3, s3 + 120, 1000, 1.55, dur=1.2, ease="sine.inOut")
pop("#mesa", P("acaba") - 0.2, s0=0.6); pop("#sopa", P("acaba"))
J(f'tl.to("#p3-head", {{rotation:4, duration:0.7, ease:"power2.inOut", svgOrigin:"500 900"}}, {tl0:.2f});')
J(f'tl.to("#p3-lockR", {{rotation:-7, scaleY:1.16, duration:0.9, ease:"power2.inOut", svgOrigin:"616 740"}}, {tl0 + 0.1:.2f});')
J(f'tl.to("#p3-lockR", {{rotation:-4.5, duration:0.25, yoyo:true, repeat:3, ease:"sine.inOut", svgOrigin:"616 740"}}, {tl0 + 1.0:.2f});')
tsp = tl0 + 0.85
J(f'tl.fromTo("#sopa .gota", {{opacity:1, y:0, x:0}}, {{opacity:0, y:(i) => -50 - i * 12, x:(i) => (i - 2) * 22, duration:0.55, ease:"power2.out", stagger:0.03, immediateRender:false}}, {tsp:.2f});')
J(f'tl.fromTo("#sopa .onda", {{opacity:0.9, scale:0.3}}, {{opacity:0, scale:3, duration:0.9, stagger:0.3, ease:"power1.out", transformOrigin:"50% 50%", immediateRender:false}}, {tsp:.2f});')
J(f'tl.to(["#p3-up", "#p3-head", "#p3-lockR"], {{rotation:0, scaleY:1, duration:0.4, ease:"power2.inOut"}}, {FE(14) + 0.3:.2f});')
J(f'tl.to("#p3-mouth", {{attr:{{d:"M478,828 Q500,808 522,828"}}, duration:0.2}}, {tsop + 0.4:.2f});')
FX_EV.append(("pop", tsp))
J(f'tl.to("#flota", {{strokeDashoffset:0, duration:0.6, ease:"power2.out"}}, {tsp + 0.1:.2f});')
J(f'tl.to("#sopa .vapor", {{opacity:0.8, y:-30, duration:0.7, stagger:0.15, yoyo:true, repeat:3}}, {tsop:.2f});')
cam(FE(14) + 0.4, s3 + 60, 1000, 0.95, dur=0.45)

# 8 · CUATRO — clímax: deja de crecer
t = F(15)
J(f'tl.to(["#mesa", "#sopa"], {{opacity:0, duration:0.4}}, {t + 0.3:.2f});')
J(f'tl.to("#camino", {{strokeDasharray:"{s4 - s0 + 120} 20000", duration:1.1, ease:"power2.inOut"}}, {t:.2f});')
cam(t, s4, 980, 0.95, dur=1.1, viaje=True)
pop("#graf", P("aqui")); J(f'tl.to("#grafsvg", {{opacity:1, duration:0.3}}, {P("aqui"):.2f});')
cam(P("nadie"), s4, 830, 1.1, dur=1.6, ease="sine.inOut")   # zoom lento
td = P("dejar")
J(f'tl.to("#curva", {{strokeDashoffset:0, duration:{max(1.0, td - P("aqui") - 0.6):.2f}, ease:"sine.inOut"}}, {P("aqui") + 0.4:.2f});')
J('tl.set("#curva2", {scaleX:0, svgOrigin:"480 140"}, 0);')
J(f'tl.to("#curva2", {{scaleX:1, duration:0.8, ease:"power1.out", svgOrigin:"480 140"}}, {P("crecer", 1) + 0.2:.2f});')
J(f'tl.fromTo("#stop", {{scale:0, opacity:0}}, {{scale:1, opacity:1, duration:0.45, ease:"back.out(2)", svgOrigin:"480 140"}}, {P("crecer", 1) + 0.15:.2f});'); FX_EV.append(("pop", P("crecer", 1) + 0.15))
FX_EV.append(("golpe", P("crecer", 1) + 0.15))
J(f'tl.fromTo("#world", {{rotation:0}}, {{rotation:0.4, duration:0.06, yoyo:true, repeat:3}}, {P("crecer", 1) + 0.15:.2f});')
tb = P("dos", 2)
cam(tb - 0.4, s4, 1100, 1.0, dur=0.5)
pop("#barra", tb - 0.3)
J(f'tl.fromTo("#barfill", {{scaleX:0.28}}, {{scaleX:1, duration:{max(0.6, P("siete", 2) - tb + 0.3):.2f}, ease:"power2.inOut"}}, {tb:.2f});')
tg = P("genes")
cam(tg - 0.35, s4 + 540, 1020, 0.95, dur=0.7); J(f'tl.to(["#graf", "#grafsvg", "#barra"], {{opacity:0, duration:0.3}}, {tg - 0.3:.2f});')
J(f'tl.to("#p4-eyes", {{x:-7, duration:0.2}}, {tg:.2f}); tl.to("#p4-eyes", {{x:0, duration:0.3}}, {P("largo") + 0.3:.2f});')
J(f'tl.to("#p4-mouth", {{attr:{{d:"M480,824 Q500,812 520,824"}}, duration:0.25}}, {P("nunca"):.2f});')
J(f'tl.to("#p4-mouth", {{attr:{{d:"M478,816 Q500,832 522,816"}}, duration:0.25}}, {P("nace") + 0.4:.2f});')
pop("#adn", tg)


J(f'tl.fromTo("#adn", {{scaleX:1}}, {{scaleX:-1, duration:0.9, ease:"sine.inOut", yoyo:true, repeat:5, transformOrigin:"50% 50%"}}, {tg:.2f});')
pop("#foliculo", P("despues") - 0.2); J(f'tl.to("#adn", {{opacity:0, duration:0.3}}, {P("despues") - 0.4:.2f});')
tca = P("cae")
J(f'tl.to("#pelo-viejo", {{y:-95, duration:0.4, ease:"power2.out"}}, {tca - 0.05:.2f});')                    # se suelta: sale de la raíz
J(f'tl.to("#pelo-viejo", {{x:150, y:40, rotation:75, duration:1.1, ease:"power1.in", svgOrigin:"150 150"}}, {tca + 0.35:.2f});')  # y cae fuera, de lado
J(f'tl.to("#pelo-viejo", {{opacity:0, duration:0.4}}, {tca + 1.05:.2f});')
FX_EV.append(("whoosh", tca + 0.35))
tna = P("nace")
J(f'tl.fromTo("#brillo", {{opacity:0, attr:{{r:8}}}}, {{opacity:0.9, attr:{{r:30}}, duration:0.35, yoyo:true, repeat:1, immediateRender:false}}, {tna - 0.1:.2f});')
J(f'tl.to("#bulbo", {{attr:{{r:16}}, duration:0.2, yoyo:true, repeat:1}}, {tna - 0.1:.2f});')
J('tl.set("#pelo-nuevo", {opacity:0}, 0);')
J(f'tl.set("#pelo-nuevo", {{opacity:1}}, {tna:.2f}); tl.to("#pelo-nuevo", {{strokeDashoffset:0, duration:1.1, ease:"power2.out"}}, {tna:.2f});')
FX_EV.append(("pop", tna))
cam(P("despues") - 0.4, s4 + 250, 1330, 1.8, dur=0.7)

# 9 · año 5: 75 cm, cinta métrica, casi hasta la cintura
t = F(21)
J(f'tl.to("#camino", {{strokeDasharray:"{s5 - s0 + 120} 20000", duration:1.0, ease:"power2.inOut"}}, {t:.2f});')
cam(t, s5, 960, 1.0, dur=1.0, viaje=True)
J(f'tl.fromTo("#cinta", {{scaleY:0, opacity:1}}, {{scaleY:1, duration:1.2, ease:"power2.out", transformOrigin:"50% 0%"}}, {P("setenta"):.2f});')
FX_EV.append(("pop", P("setenta")))
pop("#c5", P("setenta") + 0.3)
cam(P("cintura") - 0.4, s5 - 60, 1050, 0.9, dur=0.8)
J(f'tl.to("#p5-mouth", {{attr:{{d:"M474,814 Q500,840 526,814"}}, duration:0.3}}, {P("cintura"):.2f});')

# 10 · pelos perdidos (números rodillo) y pelos que caen
t = F(23)
J(f'tl.to("#camino", {{strokeDasharray:"{s6 - s0 + 120} 20000", duration:1.0, ease:"power2.inOut"}}, {t:.2f});')
cam(t, s6, 980, 0.95, dur=1.0, viaje=True)
pop("#panel", F(23) + 0.7)
tn9 = P("noventa")
J(f'tl.to("#guion6", {{opacity:1, duration:0.2}}, {tn9 + 0.6:.2f});')
J(f'tl.to("#rodA", {{opacity:1, duration:0.15}}, {tn9:.2f});'); rodar("rodA", ran, rad_, rah, tn9)
tc18 = P("ciento")
J(f'tl.to("#rodB", {{opacity:1, duration:0.15}}, {tc18:.2f});'); rodar("rodB", rbn, rbd, rbh, tc18)
FX_EV.append(("pop", tn9)); FX_EV.append(("pop", tc18))
for i in range(44):
    t0 = tn9 + i * 0.07
    J(f'tl.fromTo("#caen{i}", {{opacity:0, y:-80, rotation:0}}, {{opacity:1, y:{600 + (i % 6) * 22}, rotation:{random.choice([-1, 1]) * random.randint(60, 240)}, duration:1.6, ease:"power1.in"}}, {t0:.2f});')

# el personaje CAMINA hasta su sitio en cada etapa y gesticula
def caminar(pid, t, desde=-420, dur=1.3):
    J(f'tl.fromTo("#{pid}", {{x:{desde}}}, {{x:0, duration:{dur}, ease:"power1.out", immediateRender:false}}, {t:.2f});')
    pasos = 4
    for k in range(pasos):
        tk = t + k * dur / pasos
        pie = "legL" if k % 2 == 0 else "legR"
        J(f'tl.to("#{pid}-{pie}", {{y:-26, duration:{dur / pasos / 2:.3f}, yoyo:true, repeat:1, ease:"sine.inOut"}}, {tk:.2f});')
        J(f'tl.to("#{pid}-up", {{y:-8, duration:{dur / pasos / 2:.3f}, yoyo:true, repeat:1, ease:"sine.inOut"}}, {tk:.2f});')
        J(f'tl.to("#{pid}-head", {{x:{6 if k % 2 == 0 else -6}, duration:{dur / pasos / 2:.3f}, yoyo:true, repeat:1, ease:"sine.inOut"}}, {tk:.2f});')

def brazo(pid, lado, rot, t, hold, ida=0.35):
    org = "356 985" if lado == "L" else "644 985"
    J(f'tl.to("#{pid}-arm{lado}g", {{rotation:{rot}, duration:{ida}, ease:"back.out(1.4)", svgOrigin:"{org}"}}, {t:.2f});')
    J(f'tl.to("#{pid}-arm{lado}g", {{rotation:0, duration:0.45, ease:"power2.inOut", svgOrigin:"{org}"}}, {t + hold:.2f});')

def encoger(pid, t, hold=0.8):
    brazo(pid, "L", 22, t, hold); brazo(pid, "R", -22, t, hold)
    J(f'tl.to("#{pid}-head", {{rotation:-5, duration:0.3, yoyo:true, repeat:1, repeatDelay:{max(0.1, hold - 0.3):.2f}, svgOrigin:"500 900"}}, {t:.2f});')

caminar("p1", F(5) - 0.1)
caminar("p2", F(8) - 0.1)
caminar("p3", F(11) - 0.1)
caminar("p5", F(21) - 0.1)
caminar("p4", P("genes") - 0.9, desde=380, dur=1.1)
# gestos
J(f'tl.to("#p0-eyes", {{y:-6, duration:0.3}}, {P("empiezas"):.2f}); tl.to("#p0-eyes", {{y:0, duration:0.3}}, {P("bueno"):.2f});')
encoger("p0", P("cien") + 0.1, hold=1.0)
tf = P("ojos") + 0.35
J(f'tl.to("#p1-mouthO", {{opacity:1, scale:0.7, duration:0.12, svgOrigin:"500 822"}}, {tf:.2f}); tl.to("#p1-mouth", {{opacity:0, duration:0.12}}, {tf:.2f});')
J(f'tl.to("#p1-fringe", {{attr:{{d:"{fringe_path(24)}"}}, duration:0.25, ease:"power2.out"}}, {tf + 0.1:.2f});')
J(f'tl.to("#p1-fringe", {{attr:{{d:"{fringe_path(56)}"}}, duration:0.5, ease:"bounce.out"}}, {tf + 0.45:.2f});')
J(f'tl.to("#p1-mouthO", {{opacity:0, duration:0.12}}, {tf + 0.5:.2f}); tl.to("#p1-mouth", {{opacity:1, duration:0.12}}, {tf + 0.5:.2f});')
encoger("p1", P("aguanta") + 0.1, hold=0.8)
for k in range(3):
    J(f'tl.to("#p2-head", {{rotation:4, duration:0.12, yoyo:true, repeat:1, ease:"power2.out", svgOrigin:"500 900"}}, {P("nudos") + 0.45 + k * 0.64:.2f});')
J(f'tl.to("#p2-head", {{rotation:6, duration:0.4, yoyo:true, repeat:1, repeatDelay:0.8, svgOrigin:"500 900"}}, {P("manana") - 0.2:.2f});')
J(f'tl.to("#p3-eyes", {{y:7, duration:0.25, yoyo:true, repeat:1, repeatDelay:0.9}}, {P("cremallera"):.2f});')
encoger("p4", P("nunca"), hold=1.0)
brazo("p5", "R", -55, P("cintura") - 0.2, 1.4)
brazo("p0", "R", -158, P("solo", 2) - 0.6, 1.0) if False else None

# las tarjetas flotan suavemente mientras están en pantalla
for sel, t0, t1 in (("#c0", P("cien"), P("mes", 1)), ("#cal0", P("centimetro"), F(5)), ("#c1", P("siete"), P("flequillo")),
                    ("#c2", P("treinta"), P("nudos")), ("#c3", P("cuarenta"), P("puertas")), ("#c5", P("setenta"), F(23)),
                    ("#panel", P("perdido"), DUR - 1), ("#reloj", P("media"), F(11))):
    reps = max(1, int((t1 - t0) / 1.2))
    J(f'tl.to("{sel}", {{y:-12, duration:0.6, ease:"sine.inOut", yoyo:true, repeat:{reps}}}, {t0 + 0.5:.2f});')

# ritmo: golpes de zoom y cambios de ángulo en las palabras fuertes
for w, n in (("seis", 1), ("treinta", 1), ("cuarenta", 1), ("setenta", 1), ("sopa", 1), ("genes", 1), ("cintura", 1), ("ochenta", 1), ("ojos", 1), ("nudos", 1)):
    punch(P(w, n) - 0.02)
punch(tq + 0.28, 1.1, 0.45); angulo(tq + 0.28, 3, dur=0.15, hold=1.1)
angulo(P("crecer", 1) + 0.1, -2.5, dur=0.2, hold=1.4); punch(P("crecer", 1) + 0.15, 1.08)
angulo(P("aguanta") + 0.05, -2, dur=0.2, hold=0.9)
angulo(P("cae"), 2, dur=0.4, hold=0.9)
angulo(P("perdido"), -1.5, dur=0.5, hold=1.6)

# 12 · BUCLE: la cámara vuelve al principio del camino (cabeza calva con un pelo = primer fotograma)
t = F(24)
back = DUR - t
J(f'tl.to(".p0-stub", {{opacity:0, duration:0.3}}, {t:.2f}); tl.to(["#p0-capfade", "#p0-beardfade"], {{opacity:0, duration:0.3}}, {t:.2f});')
J(f'tl.to(["#c0", "#rod0", "#regla0", "#cal0"], {{opacity:0, duration:0.3}}, {t:.2f});')
J(f'tl.to("#camino", {{strokeDasharray:"0 20000", duration:{back:.2f}, ease:"power2.inOut"}}, {t:.2f});')
J(f'tl.to("#world", {{x:{540 - s0 * 1.55:.1f}, y:{960 - 760 * 1.55:.1f}, scale:1.55, duration:{back:.2f}, ease:"power3.inOut"}}, {t:.2f});')
J(f'tl.to("#lejos", {{x:{(540 - s0 * 1.55) * 0.35:.1f}, duration:{back:.2f}, ease:"power3.inOut"}}, {t:.2f});')
J(f'tl.to("#world", {{filter:"blur(6px)", duration:{back / 2:.2f}, ease:"sine.in"}}, {t:.2f}); tl.to("#world", {{filter:"blur(0px)", duration:{back / 2 - 0.05:.2f}, ease:"sine.out"}}, {t + back / 2:.2f});')
J(f'tl.to("#p0-one", {{rotation:0, scale:1, duration:0.4, svgOrigin:"500 646"}}, {DUR - 0.45:.2f});')   # mismo estado que el fotograma 0
FX_EV.append(("whoosh", t))

nA = 6
J(f'tl.fromTo("#camA", {{scale:1}}, {{scale:1.035, duration:{DUR / (2 * nA):.4f}, ease:"sine.inOut", yoyo:true, repeat:{2 * nA - 1}, immediateRender:false}}, 0);')
nR = 5
J(f'tl.fromTo("#camA", {{rotation:0}}, {{rotation:0.7, duration:{DUR / (4 * nR):.4f}, ease:"sine.out", yoyo:true, repeat:1, immediateRender:false}}, 0);')
for k in range(1, nR):
    J(f'tl.to("#camA", {{rotation:{(-0.7 if k % 2 else 0.7)}, duration:{DUR / (2 * nR):.4f}, ease:"sine.inOut"}}, {DUR * (k - 0.5) / nR + DUR / (4 * nR):.3f});')
J(f'tl.to("#camA", {{rotation:0, duration:{DUR / (4 * nR):.4f}, ease:"sine.in"}}, {DUR - DUR / (4 * nR) - 0.02:.3f});')

# fondo con paralaje y motas que flotan (nunca quieto)
LEJOS = []
for i in range(40):
    x = random.uniform(-500, WORLD_W * 0.6)
    y = random.uniform(150, 1300)
    r = random.uniform(40, 160)
    LEJOS.append(f'<div class="blob" id="blob{i}" style="left:{x:.0f}px;top:{y:.0f}px;width:{2 * r:.0f}px;height:{2 * r:.0f}px;opacity:{random.uniform(0.06, 0.16):.2f}"></div>')
    n = random.choice([2, 3, 4])
    J(f'tl.fromTo("#blob{i}", {{x:0, y:0, scale:1}}, {{x:{random.uniform(-90, 90):.0f}, y:{random.uniform(-70, 70):.0f}, scale:{random.uniform(0.8, 1.3):.2f}, duration:{DUR / (2 * n):.4f}, ease:"sine.inOut", yoyo:true, repeat:{2 * n - 1}, immediateRender:false}}, 0);')
# garabatos de pelo, anillos y destellos que flotan (temáticos, muy suaves)
DOOD = ['<path d="M6,30 C18,4 30,44 42,18 C50,4 58,14 60,8" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round"/>',
        '<circle cx="30" cy="30" r="18" stroke="#fff" stroke-width="5" fill="none"/>',
        '<path d="M30,4 L36,24 L56,30 L36,36 L30,56 L24,36 L4,30 L24,24 Z" fill="#fff"/>',
        '<path d="M10,50 C10,20 50,40 50,10" stroke="#ffd9c7" stroke-width="6" fill="none" stroke-linecap="round"/>']
for i in range(46):
    x = random.uniform(-300, WORLD_W * 0.6)
    y = random.uniform(120, 1500)
    sc = random.uniform(0.7, 1.6)
    LEJOS.append(f'<svg class="dood" id="dood{i}" style="left:{x:.0f}px;top:{y:.0f}px;opacity:{random.uniform(0.05, 0.11):.2f}" width="60" height="60" viewBox="0 0 60 60" overflow="visible">'
                 f'<g transform="scale({sc:.2f})">{random.choice(DOOD)}</g></svg>')
    n = random.choice([3, 4, 5])
    J(f'tl.fromTo("#dood{i}", {{y:0, rotation:0}}, {{y:{random.uniform(-60, -20):.0f}, rotation:{random.choice([-1, 1]) * random.uniform(20, 60):.0f}, duration:{DUR / (2 * n):.4f}, ease:"sine.inOut", yoyo:true, repeat:{2 * n - 1}, immediateRender:false}}, 0);')
for k, x in enumerate(ST.values()):
    J(f'tl.fromTo("#rayos{k}", {{rotation:0}}, {{rotation:{18 if k % 2 else -18}, duration:{DUR / 2:.4f}, ease:"sine.inOut", yoyo:true, repeat:1, immediateRender:false}}, 0);')
J(f'tl.fromTo("#calido", {{opacity:0}}, {{opacity:0.55, duration:{DUR / 4:.4f}, ease:"sine.inOut", yoyo:true, repeat:3, immediateRender:false}}, 0);')
MOTAS = []
for i in range(60):
    x = random.uniform(0, WORLD_W)
    y = random.uniform(200, 1350)
    MOTAS.append(f'<div class="mota" id="mota{i}" style="left:{x:.0f}px;top:{y:.0f}px"></div>')
    J(f'tl.fromTo("#mota{i}", {{y:0, opacity:0.0}}, {{y:{-random.uniform(60, 160):.0f}, opacity:0.6, duration:{random.uniform(3, 6):.1f}, ease:"sine.inOut", yoyo:true, repeat:{int(DUR / 4)}}}, {random.uniform(0, 3):.2f});')

# ------------------------------------------------------------------ subtítulos (arriba, palabra a palabra)
CLAVE = {"cinco", "pelo", "cien", "centimetro", "seis", "flequillo", "ojos", "peinado", "dos", "treinta", "nudos",
         "manana", "tres", "cuarenta", "puertas", "cremallera", "sopa", "cuatro", "nadie", "dejar", "siete", "genes",
         "largo", "cae", "nace", "setenta", "cintura", "noventa", "ochenta", "solo"}
SUBS = []
if not SIN_SUBS:
    chunks, cur = [], []
    for p in T["palabras"]:
        cur.append(p)
        txt = " ".join(x["w"] for x in cur)
        if len(cur) >= 6 or len(txt) >= 30 or re.search(r"[.:;?!…]$", p["w"]) or (re.search(r",$", p["w"]) and len(cur) >= 3):
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    for k, ch in enumerate(chunks):
        st = ch[0]["ini"] - 0.05
        en = chunks[k + 1][0]["ini"] - 0.05 if k + 1 < len(chunks) else DUR
        spans = []
        for j, p in enumerate(ch):
            wid = f"w{k}_{j}"
            if norm(p["w"]) in CLAVE:
                spans.append(f'<span id="{wid}" class="sw key"><i class="hl"></i><b class="d1"></b><b class="d2"></b>{p["w"]}</span>')
                J(f'tl.to("#{wid} .hl, #{wid} .d1, #{wid} .d2", {{opacity:1, duration:0.06}}, {p["ini"]:.2f});')
            else:
                spans.append(f'<span id="{wid}" class="sw">{p["w"]}</span>')
            J(f'tl.to("#{wid}", {{color:"#ffffff", fontWeight:800, duration:0.06}}, {p["ini"]:.2f});')
        SUBS.append(f'<div id="sub{k}" class="clip sub" data-start="{max(0, st):.3f}" data-duration="{max(0.2, en - max(0, st)):.3f}" data-track-index="3">{" ".join(spans)}</div>')

# ------------------------------------------------------------------ HTML final
html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:{TEAL2}}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif}}
#fondo{{position:absolute;inset:0;background:radial-gradient(110% 65% at 50% 38%, #9a9ed8 0%, {TEAL1} 48%, {TEAL2} 100%)}}
#lejos{{position:absolute;left:0;top:0;width:{WORLD_W}px;height:1920px}}
#calido{{position:absolute;inset:0;background:radial-gradient(90% 55% at 30% 30%, rgba(255,170,190,0.45), rgba(255,170,190,0) 70%), radial-gradient(80% 50% at 80% 75%, rgba(120,200,230,0.35), rgba(120,200,230,0) 70%)}}
.dood{{position:absolute;overflow:visible}}
.rayos{{position:absolute;width:1600px;height:1600px;border-radius:50%;background:repeating-conic-gradient(from 0deg, rgba(255,236,225,0.05) 0deg 7deg, rgba(255,236,225,0) 7deg 20deg);
  -webkit-mask-image:radial-gradient(circle, #000 12%, rgba(0,0,0,0) 62%);mask-image:radial-gradient(circle, #000 12%, rgba(0,0,0,0) 62%)}}
.blob{{position:absolute;border-radius:50%;background:#ffd9c7;filter:blur(30px)}}
#camA,#camB{{position:absolute;left:0;top:0;width:1080px;height:1920px;transform-origin:50% 50%}}
#world{{position:absolute;left:0;top:0;width:{WORLD_W}px;height:{WORLD_H}px;transform-origin:0 0}}
.pared-luz{{position:absolute;top:0;width:900px;height:{FLOOR_Y}px;background:radial-gradient(60% 55% at 50% 45%, rgba(255,228,214,0.22), rgba(255,228,214,0) 70%)}}
.plato{{position:absolute;width:760px;height:150px;border-radius:50%;background:radial-gradient(50% 50% at 50% 45%, #a7abe3 0%, #8a8ed0 60%, rgba(138,142,208,0) 100%)}}
#rodapie{{display:none}}
#suelo{{position:absolute;left:0;top:{FLOOR_Y + 120}px;width:{WORLD_W}px;height:{WORLD_H - FLOOR_Y - 120}px;
  background:linear-gradient(rgba(60,62,130,0),rgba(60,62,130,0.55))}}
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
.cinta-tag{{position:absolute;right:-30px;bottom:-90px;background:{GOOD};color:#fff;font:900 54px Inter;padding:10px 22px;border-radius:18px;white-space:nowrap}}
.reloj{{position:absolute;width:220px;height:220px;border-radius:50%;background:#fbf8f2;border:12px solid #d8cdbb;box-shadow:0 14px 30px rgba(0,0,0,0.25)}}
.aguja{{position:absolute;left:94px;bottom:98px;width:8px;border-radius:6px;background:#1d2b33;transform-origin:50% 100%}}
.mota{{position:absolute;width:10px;height:10px;border-radius:50%;background:#fff6e0}}
#vineta{{position:absolute;inset:0;background:radial-gradient(120% 80% at 50% 45%, rgba(0,0,0,0) 55%, rgba(18,16,48,0.38) 100%);pointer-events:none}}
#grano{{position:absolute;left:0;top:0;opacity:0.05;mix-blend-mode:overlay;pointer-events:none}}
#marca{{position:absolute;left:0;right:0;top:1775px;text-align:center;font:700 28px Inter;letter-spacing:0.02em;color:#ffffff;opacity:0.32;text-shadow:0 2px 6px rgba(20,18,50,0.35);pointer-events:none}}
#subs{{position:absolute;left:70px;right:70px;top:240px;height:220px}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:500 66px Inter;color:rgba(214,216,236,0.62);
  text-shadow:0 3px 16px rgba(20,18,50,0.55);line-height:1.22;letter-spacing:-0.01em}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:4px solid #4f7dff;border-radius:6px;background:rgba(79,125,255,0.16);opacity:0}}
.key b{{position:absolute;width:16px;height:16px;border-radius:50%;background:#dfe8ff;border:4px solid #4f7dff;opacity:0}}
.key .d1{{left:-12px;top:-12px}} .key .d2{{right:-12px;bottom:-10px}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="fondo"></div><div id="calido"></div>
  <div id="camA" data-layout-allow-overflow data-layout-ignore><div id="camB" data-layout-allow-overflow data-layout-ignore>
  <div id="lejos">{"".join(LEJOS)}</div>
  <div id="world" data-layout-allow-overflow data-layout-ignore>
    {"".join(f'<div class="rayos" id="rayos{k}" style="left:{x - 800}px;top:120px"></div>' for k, x in enumerate(ST.values()))}
    {"".join(f'<div class="pared-luz" style="left:{x - 450}px"></div><div class="plato" style="left:{x - 380}px;top:1625px"></div>' for x in ST.values())}
    <div id="rodapie"></div><div id="suelo"></div>
    {"".join(MOTAS)}
    {"".join(H)}
  </div>
  </div></div>
  <div id="marca">@mundo.supuesto</div>
  <div id="vineta"></div><svg id="grano" width="1080" height="1920"><filter id="gr"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7"/><feColorMatrix values="0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0.9 0"/></filter><rect width="1080" height="1920" filter="url(#gr)"/></svg>
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

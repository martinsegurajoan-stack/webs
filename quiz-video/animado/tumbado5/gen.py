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
WORLD_W, WORLD_H = 13000, 1920
FLOOR_Y = 1380
ST = {"s0": 700, "s1": 2200, "s2": 3700, "s3": 5200, "s4": 6700, "s5": 8200, "s6": 9700}

tl = []    # líneas JS del timeline
HX = lambda y: 60 + 840 * y / 10   # posición en la línea de tiempo (años 0-10)
HXI = lambda i: 60 + 840 * i / 3   # día 1 · 1 mes · 1 año · 5 años

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
        if cm <= 15:
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
        FX_EV.append(("whoosh", t))

# ------------------------------------------------------------------ construcción del mundo (escenarios decorados)
# Seis habitaciones seguidas, como una casa de muñecas: la cámara pasa de una a otra.
H = []   # HTML del mundo
RW, FLOOR = 1500, 1700
def RL(k):
    return k * RW

def sala(k, cuerpo, fondo):
    """SVG de una habitación completa (1500x1920) con su pared/suelo y lo que lleve dentro."""
    return (f'<svg class="sala" style="position:absolute;left:{RL(k)}px;top:0;overflow:visible" width="{RW}" height="1920" '
            f'viewBox="0 0 {RW} 1920">{fondo}{cuerpo}</svg>')
H.append(f'<div style="position:absolute;left:0;top:1920px;width:9000px;height:900px;background:#6e4a33"></div>')

def pared_suelo(pid, w1, w2, f1, f2, rayas=True, zocalo="#fff3e6"):
    d = (f'<defs><linearGradient id="{pid}w" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{w1}"/><stop offset="1" stop-color="{w2}"/></linearGradient>'
         f'<linearGradient id="{pid}f" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{f1}"/><stop offset="1" stop-color="{f2}"/></linearGradient></defs>'
         f'<rect x="0" y="0" width="{RW}" height="{FLOOR}" fill="url(#{pid}w)"/>')
    if rayas:
        d += "".join(f'<rect x="{x}" y="0" width="26" height="{FLOOR}" fill="#ffffff" opacity="0.07"/>' for x in range(20, RW, 70))
    d += (f'<rect x="0" y="{FLOOR - 60}" width="{RW}" height="60" fill="{zocalo}"/>'
          f'<rect x="0" y="{FLOOR}" width="{RW}" height="{2400 - FLOOR}" fill="url(#{pid}f)"/>'
          + "".join(f'<line x1="0" y1="{FLOOR + 40 + i * 45}" x2="{RW}" y2="{FLOOR + 40 + i * 45}" stroke="#000" stroke-opacity="0.08" stroke-width="3"/>' for i in range(5)))
    d += f'<rect x="0" y="0" width="{RW}" height="1920" fill="url(#luzsala)" opacity="0.55"/>'
    return d

def ventana(x, y, w, h, noche=False, cortina="#6a8caf"):
    cielo = ("#1d2356", "#3b3f7a") if noche else ("#9fd3f5", "#e4f4ff")
    s = (f'<rect x="{x - 14}" y="{y - 14}" width="{w + 28}" height="{h + 28}" rx="10" fill="#fbf6ee"/>'
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{cielo[1]}"/><rect x="{x}" y="{y}" width="{w}" height="{h * 0.6:.0f}" fill="{cielo[0]}" opacity="0.6"/>')
    if not noche:
        s += (f'<ellipse cx="{x + w * 0.3:.0f}" cy="{y + h * 0.3:.0f}" rx="60" ry="22" fill="#fff" opacity="0.9"/>'
              f'<ellipse cx="{x + w * 0.65:.0f}" cy="{y + h * 0.45:.0f}" rx="45" ry="16" fill="#fff" opacity="0.8"/>'
              f'<rect x="{x}" y="{y + h * 0.78:.0f}" width="{w}" height="{h * 0.22:.0f}" fill="#8cc28a" opacity="0.8"/>')
    s += (f'<rect x="{x + w / 2 - 6:.0f}" y="{y}" width="12" height="{h}" fill="#fbf6ee"/><rect x="{x}" y="{y + h / 2 - 6:.0f}" width="{w}" height="12" fill="#fbf6ee"/>'
          f'<path d="M{x - 40},{y - 40} L{x + 70},{y - 40} C{x + 50},{y + h * 0.4:.0f} {x + 90},{y + h * 0.8:.0f} {x + 40},{y + h + 60} L{x - 40},{y + h + 60} Z" fill="{cortina}"/>'
          f'<path d="M{x + w + 40},{y - 40} L{x + w - 70},{y - 40} C{x + w - 50},{y + h * 0.4:.0f} {x + w - 90},{y + h * 0.8:.0f} {x + w - 40},{y + h + 60} L{x + w + 40},{y + h + 60} Z" fill="{cortina}"/>'
          f'<rect x="{x - 70}" y="{y - 52}" width="{w + 140}" height="16" rx="8" fill="#8a5a3c"/>')
    return s

def planta(x, y, seca=False):
    hoja = "#9b7b4b" if seca else "#4f9a6a"
    s = f'<path d="M{x - 45},{y} L{x + 45},{y} L{x + 34},{y + 90} L{x - 34},{y + 90} Z" fill="#c0704f"/>'
    for a in (-60, -30, 0, 30, 60):
        s += f'<path d="M{x},{y} Q{x + a * 1.3},{y - 110} {x + a * 1.8},{y - (60 if seca else 170)}" stroke="{hoja}" stroke-width="14" fill="none" stroke-linecap="round"/>'
    return s

def cuadro(x, y, w, h):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#8a5a3c"/><rect x="{x + 14}" y="{y + 14}" width="{w - 28}" height="{h - 28}" fill="#f6e7d2"/>'
            f'<path d="M{x + 14},{y + h - 14} L{x + w * 0.4:.0f},{y + h * 0.4:.0f} L{x + w * 0.6:.0f},{y + h * 0.65:.0f} L{x + w * 0.75:.0f},{y + h * 0.5:.0f} L{x + w - 14},{y + h - 14} Z" fill="#7aa38f"/>'
            f'<circle cx="{x + w * 0.72:.0f}" cy="{y + h * 0.3:.0f}" r="18" fill="#f2b84b"/>')

def reloj(cid, x, y, r=70):
    return (f'<circle cx="{x}" cy="{y}" r="{r + 10}" fill="#3d405b"/><circle cx="{x}" cy="{y}" r="{r}" fill="#fbf8f2"/>'
            + "".join(f'<line x1="{x + (r - 10) * math.cos(a * math.pi / 6):.0f}" y1="{y + (r - 10) * math.sin(a * math.pi / 6):.0f}" x2="{x + (r - 22) * math.cos(a * math.pi / 6):.0f}" y2="{y + (r - 22) * math.sin(a * math.pi / 6):.0f}" stroke="#3d405b" stroke-width="5"/>' for a in range(12))
            + f'<line id="{cid}h" x1="{x}" y1="{y}" x2="{x}" y2="{y - r * 0.5:.0f}" stroke="#1d2b33" stroke-width="9" stroke-linecap="round"/>'
            f'<line id="{cid}m" x1="{x}" y1="{y}" x2="{x + r * 0.75:.0f}" y2="{y}" stroke="#e5484d" stroke-width="6" stroke-linecap="round"/><circle cx="{x}" cy="{y}" r="8" fill="#1d2b33"/>')

def calendario(cid, x, y, txt):
    return (f'<rect x="{x}" y="{y}" width="150" height="170" rx="12" fill="#fbf8f2"/><rect x="{x}" y="{y}" width="150" height="46" rx="12" fill="#e5484d"/>'
            f'<circle cx="{x + 40}" cy="{y}" r="8" fill="#3d405b"/><circle cx="{x + 110}" cy="{y}" r="8" fill="#3d405b"/>'
            f'<text id="{cid}" x="{x + 75}" y="{y + 125}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="40" fill="#1d2b33">{txt}</text>')

def lampara_mesita(x):
    return (f'<rect x="{x}" y="1440" width="170" height="260" rx="10" fill="#b07a52"/><rect x="{x}" y="1440" width="170" height="26" rx="8" fill="#c99067"/>'
            f'<rect x="{x + 20}" y="1520" width="130" height="10" rx="5" fill="#8a5a3c"/><circle cx="{x + 85}" cy="1560" r="8" fill="#e2c27a"/>'
            f'<rect x="{x + 75}" y="1330" width="20" height="110" fill="#8a5a3c"/><path d="M{x + 25},1340 L{x + 145},1340 L{x + 115},1250 L{x + 55},1250 Z" fill="#f2d27a"/>'
            f'<ellipse cx="{x + 85}" cy="1360" rx="160" ry="120" fill="#fff1c9" opacity="0.18"/>')

# --- cama con el personaje TUMBADO (el SVG del personaje girado -90°, cabeza en la almohada)
def cama_tumbado(pid, cx, cy, s=0.62, inclin=0, **kw):
    m_top = cy + 205 * s
    pie_x = cx + 860 * s
    out = (f'<div id="{pid}-lie" style="position:absolute;left:0;top:0;width:1px;height:1px;overflow:visible">'
           f'<svg style="position:absolute;left:0;top:0;overflow:visible" width="1" height="1">'
           # cabecero y patas
           f'<rect x="{cx - 380 * s:.0f}" y="{cy - 330 * s:.0f}" width="{60 * s:.0f}" height="{FLOOR - cy + 330 * s:.0f}" rx="18" fill="#8a5a3c"/>'
           f'<rect x="{cx - 330 * s:.0f}" y="{cy - 270 * s:.0f}" width="{40 * s:.0f}" height="{(m_top - cy + 270 * s):.0f}" rx="10" fill="#a8714c"/>'
           f'<rect x="{pie_x - 10:.0f}" y="{m_top - 60:.0f}" width="{50 * s:.0f}" height="{FLOOR - m_top + 60:.0f}" rx="14" fill="#8a5a3c"/>'
           f'<rect x="{cx - 330 * s:.0f}" y="{m_top + 90 * s:.0f}" width="{pie_x - cx + 330 * s:.0f}" height="{40 * s:.0f}" fill="#7a4e33"/>'
           f'<rect x="{cx - 320 * s:.0f}" y="{m_top:.0f}" width="{pie_x - cx + 320 * s:.0f}" height="{100 * s:.0f}" rx="16" fill="#f4efe6"/>'
           f'<ellipse cx="{cx - 150 * s:.0f}" cy="{m_top - 30 * s:.0f}" rx="{175 * s:.0f}" ry="{70 * s:.0f}" fill="#ffffff"/>'
           f'<ellipse cx="{cx - 150 * s:.0f}" cy="{m_top - 10 * s:.0f}" rx="{165 * s:.0f}" ry="{40 * s:.0f}" fill="#e9e1d4"/></svg>'
           f'<div id="{pid}-rot" style="position:absolute;left:0;top:0;width:1px;height:1px;overflow:visible">'
           f'<div style="position:absolute;left:{cx - 500:.0f}px;top:{cy - 900:.0f}px;width:1000px;height:1800px;transform-origin:500px 900px;transform:rotate(-90deg) scale({s})">'
           + personaje(pid, **kw).replace("{x}", "0") +
           '</div></div>'
           # manta por encima del cuerpo (deja ver la cabeza)
           f'<svg id="{pid}-cubre" style="position:absolute;left:0;top:0;overflow:visible" width="1" height="1">'
           f'<path id="{pid}-manta" d="M{cx + 40 * s:.0f},{cy - 205 * s:.0f} C{cx + 300 * s:.0f},{cy - 245 * s:.0f} {cx + 600 * s:.0f},{cy - 225 * s:.0f} {cx + 790 * s:.0f},{cy - 175 * s:.0f} '
           f'C{cx + 860 * s:.0f},{cy - 150 * s:.0f} {cx + 880 * s:.0f},{cy - 20 * s:.0f} {pie_x + 10:.0f},{m_top + 110 * s:.0f} L{cx + 10 * s:.0f},{m_top + 110 * s:.0f} '
           f'C{cx - 20 * s:.0f},{cy + 40 * s:.0f} {cx - 10 * s:.0f},{cy - 120 * s:.0f} {cx + 40 * s:.0f},{cy - 205 * s:.0f} Z" fill="url(#manta)"/>'
           f'<path d="M{cx + 40 * s:.0f},{cy - 200 * s:.0f} C{cx + 20 * s:.0f},{cy - 80 * s:.0f} {cx + 20 * s:.0f},{cy + 80 * s:.0f} {cx + 40 * s:.0f},{m_top + 100 * s:.0f}" stroke="#fbf6ee" stroke-width="{34 * s:.0f}" fill="none" stroke-linecap="round"/>'
           + "".join(f'<path d="M{cx + (180 + i * 150) * s:.0f},{cy - (215 - i * 5) * s:.0f} q{30 * s:.0f},{150 * s:.0f} {10 * s:.0f},{330 * s:.0f}" stroke="#2f4f7a" stroke-width="5" fill="none" opacity="0.35"/>' for i in range(4))
           + '</svg></div>')
    return out

DEFS = ('<svg width="0" height="0" style="position:absolute"><defs>'
        '<radialGradient id="luzsala" cx="0.5" cy="0.35" r="0.75"><stop offset="0" stop-color="#ffffff" stop-opacity="0.35"/><stop offset="1" stop-color="#2a2550" stop-opacity="0.35"/></radialGradient>'
        '<linearGradient id="manta" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5b86c4"/><stop offset="1" stop-color="#3d5f99"/></linearGradient>'
        '</defs></svg>')
H.append(DEFS)

# ---- 0 · DORMITORIO, día 1
L0 = RL(0)
H.append(sala(0, ventana(940, 420, 330, 470) + cuadro(230, 520, 230, 230) + reloj("clk", 640, 640) + calendario("cal0", 1290, 1010, "DÍA 1")
              + lampara_mesita(40) + f'<ellipse cx="760" cy="1800" rx="560" ry="60" fill="#c56f55" opacity="0.55"/>'
              + planta(1380, 1610), pared_suelo("s0", "#f6dcc6", "#eac3a6", "#b07a52", "#8a5a3c")))
BED0 = (L0 + 470, 1330)
H.append(cama_tumbado("p0", *BED0, s=0.62, cm=7))
# mesa de cama con bandeja (entra al decir «comida»)
TRAY = f'''<svg id="bandeja" style="position:absolute;left:{L0 + 640}px;top:1010px;overflow:visible;opacity:0" width="10" height="10">
<rect x="250" y="80" width="22" height="610" fill="#9aa3b5"/><rect x="190" y="680" width="140" height="18" rx="9" fill="#7c8496"/>
<rect x="-20" y="70" width="300" height="24" rx="10" fill="#c99067"/>
<ellipse cx="80" cy="55" rx="70" ry="20" fill="#fbf8f2"/><ellipse cx="80" cy="50" rx="46" ry="12" fill="#e5a24e"/><circle cx="60" cy="44" r="10" fill="#6aa86b"/>
<rect x="170" y="10" width="34" height="58" rx="6" fill="#dff1fb" opacity="0.9"/><rect x="170" y="32" width="34" height="36" rx="4" fill="#f6a35c" opacity="0.8"/>
<circle cx="235" cy="50" r="18" fill="#e5484d"/><path d="M235,32 q4,-10 10,-12" stroke="#4f9a6a" stroke-width="5" fill="none"/></svg>'''
H.append(TRAY)
# gafas de sol (vacaciones)
H.append(f'<svg id="gafas" style="position:absolute;left:{BED0[0] - 128}px;top:{BED0[1] - 90}px;overflow:visible;opacity:0" width="10" height="10">'
         '<g transform="translate(40 90) rotate(-90) scale(0.62) translate(-40 -90)"><rect x="-30" y="70" width="58" height="40" rx="14" fill="#1d2b33"/><rect x="52" y="70" width="58" height="40" rx="14" fill="#1d2b33"/>'
         '<path d="M28,88 L52,88" stroke="#1d2b33" stroke-width="7"/><rect x="-20" y="76" width="18" height="8" rx="4" fill="#ffffff" opacity="0.5"/></g></svg>')
# flecha de «darte la vuelta» alrededor de la cama
H.append(f'<svg id="vuelta" style="position:absolute;left:{BED0[0] + 60}px;top:{BED0[1] - 330}px;overflow:visible;opacity:0" width="10" height="10">'
         f'<path id="vuelta-p" d="M40,250 C40,40 420,40 420,230" stroke="{KEY}" stroke-width="18" fill="none" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
         f'<path d="M392,200 L422,250 L455,200" stroke="{KEY}" stroke-width="18" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
         f'<text x="230" y="40" text-anchor="middle" font-family="Inter" font-weight="900" font-size="56" fill="#fbf8f2">CADA 2 H</text></svg>')
# lupa con las escaras
H.append(f'<div id="escaras" class="card" style="left:{L0 + 860}px;top:880px;width:380px;padding:22px 26px">'
         f'<div class="card-top" style="font-size:28px">ESCARAS</div>'
         f'<svg width="330" height="190" viewBox="0 0 330 190"><ellipse cx="165" cy="95" rx="150" ry="85" fill="{SKIN}"/>'
         f'<ellipse cx="120" cy="80" rx="30" ry="22" fill="#d6655a" class="llaga" opacity="0"/><ellipse cx="200" cy="110" rx="40" ry="26" fill="#c2453e" class="llaga" opacity="0"/>'
         f'<ellipse cx="170" cy="60" rx="18" ry="13" fill="#e07a6a" class="llaga" opacity="0"/></svg></div>')
# fuerza de las piernas
H.append(f'<div id="fuerza" class="card" style="left:{L0 + 860}px;top:880px;width:400px"><div class="card-top" style="font-size:28px">FUERZA EN LAS PIERNAS</div>'
         f'<div style="position:relative;height:46px;margin-top:22px;border-radius:23px;background:#ece6db"><div id="fuerza-b" style="position:absolute;left:0;top:0;bottom:0;width:100%;border-radius:23px;background:linear-gradient(90deg,{BAD},#f08a5d);transform-origin:0 50%"></div></div>'
         f'<svg width="350" height="120" viewBox="0 0 350 120" style="margin-top:14px"><path d="M20,60 C80,10 140,10 200,40 C250,62 300,50 330,40" stroke="#e8b294" stroke-width="40" fill="none" stroke-linecap="round"/>'
         f'<ellipse id="musculo" cx="120" cy="38" rx="80" ry="26" fill="#e07a6a" opacity="0.85"/></svg></div>')

# ---- 1 · BAÑO
L1 = RL(1)
azulejos = "".join(f'<line x1="0" y1="{y}" x2="{RW}" y2="{y}" stroke="#ffffff" stroke-width="5"/>' for y in range(1100, FLOOR, 90)) + \
           "".join(f'<line x1="{x}" y1="1100" x2="{x}" y2="{FLOOR}" stroke="#ffffff" stroke-width="5"/>' for x in range(0, RW, 90))
H.append(sala(1, f'<rect x="0" y="1100" width="{RW}" height="{FLOOR - 1100}" fill="#a9d9d1"/>' + azulejos
              + ventana(1080, 360, 240, 300, cortina="#f2b84b")
              + '<ellipse cx="300" cy="720" rx="130" ry="170" fill="#fbf6ee"/><ellipse cx="300" cy="720" rx="110" ry="150" fill="#cfe6f2"/><path d="M230,640 L300,560" stroke="#fff" stroke-width="10" opacity="0.6"/>'
              + '<rect x="190" y="1180" width="220" height="50" rx="20" fill="#fbf6ee"/><rect x="285" y="1225" width="30" height="470" fill="#e6e1d8"/><rect x="285" y="1140" width="10" height="45" fill="#9aa3b5"/>'
              + '<rect x="960" y="1330" width="520" height="370" rx="60" fill="#fbf6ee"/><rect x="980" y="1350" width="480" height="60" rx="30" fill="#cfe6f2"/>'
              + '<rect x="1000" y="300" width="12" height="1060" fill="#9aa3b5"/><path d="M1006,320 C1100,340 1140,700 1180,1320 L1006,1320 Z" fill="#f2b84b" opacity="0.8"/>'
              + '<rect x="560" y="900" width="180" height="16" rx="8" fill="#9aa3b5"/><rect x="590" y="916" width="120" height="220" rx="16" fill="#e07a5f"/>'
              + planta(1400, 1610), pared_suelo("s1", "#eaf6f3", "#d3ece6", "#e8e2d6", "#cbc3b4", rayas=False, zocalo="#ffffff")))
H.append(f'''<svg id="inodoro" style="position:absolute;left:{L1 + 640}px;top:1260px;overflow:visible" width="10" height="10">
<g id="ruedas" opacity="0"><circle cx="20" cy="440" r="26" fill="#3d405b"/><circle cx="210" cy="440" r="26" fill="#3d405b"/><circle cx="20" cy="440" r="9" fill="#9aa3b5"/><circle cx="210" cy="440" r="9" fill="#9aa3b5"/></g>
<rect x="150" y="0" width="140" height="210" rx="20" fill="#fbf6ee"/><rect x="170" y="-20" width="100" height="26" rx="10" fill="#e6e1d8"/>
<path d="M-20,210 L300,210 C300,330 230,360 170,370 L170,430 L60,430 L60,370 C0,350 -20,300 -20,210 Z" fill="#ffffff"/>
<ellipse cx="140" cy="212" rx="160" ry="26" fill="#e6e1d8"/></svg>''')

# ---- 2 · LABORATORIO de la agencia espacial (estudio de reposo en cama)
L2 = RL(2)
H.append(sala(2, '<rect x="700" y="640" width="560" height="120" rx="18" fill="#1d2b33"/><text x="980" y="692" text-anchor="middle" font-family="Inter" font-weight="900" font-size="36" fill="#f2b84b">AGENCIA ESPACIAL</text>'
              '<text x="980" y="738" text-anchor="middle" font-family="Inter" font-weight="700" font-size="28" fill="#fbf8f2">ESTUDIO DE REPOSO EN CAMA</text>'
              # póster de un astronauta en la pared
              '<rect x="110" y="560" width="300" height="400" rx="10" fill="#1d2356"/>' + "".join(f'<circle cx="{130 + (k * 53) % 260}" cy="{580 + (k * 97) % 360}" r="3" fill="#fff"/>' for k in range(22))
              + '<circle cx="260" cy="1000" r="170" fill="#3f7fc4" clip-path="url(#posterclip)"/><circle cx="300" cy="700" r="46" fill="#f4f6fb"/><ellipse cx="305" cy="702" rx="30" ry="26" fill="#1d2356"/>'
              '<rect x="270" y="740" width="70" height="90" rx="22" fill="#f4f6fb"/><rect x="110" y="560" width="300" height="400" rx="10" fill="none" stroke="#8a5a3c" stroke-width="14"/>'
              # monitor de constantes
              '<rect x="1230" y="900" width="200" height="140" rx="14" fill="#1d2b33"/><path id="ecg" d="M1245,970 L1290,970 L1305,930 L1320,1010 L1335,970 L1415,970" stroke="#3fbf7f" stroke-width="6" fill="none"/>'
              '<rect x="1322" y="1040" width="16" height="660" fill="#9aa3b5"/>'
              # carro con material
              '<rect x="1020" y="1450" width="170" height="20" rx="8" fill="#9aa3b5"/><rect x="1030" y="1470" width="12" height="230" fill="#7c8496"/><rect x="1170" y="1470" width="12" height="230" fill="#7c8496"/>'
              '<rect x="1050" y="1400" width="40" height="50" rx="6" fill="#e5484d"/><rect x="1100" y="1380" width="50" height="70" rx="8" fill="#dff1fb"/>'
              + planta(60, 1610), pared_suelo("s2", "#eef1f6", "#dce3ec", "#c9ced8", "#aab1bf", rayas=False, zocalo="#ffffff")))
H.append('<svg width="0" height="0" style="position:absolute"><defs><clipPath id="posterclip"><rect x="110" y="560" width="300" height="400"/></clipPath>'
         '<linearGradient id="espacioG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05071c"/><stop offset="1" stop-color="#1e2560"/></linearGradient>'
         '<linearGradient id="cieloG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0e2c"/><stop offset="0.28" stop-color="#1e2a6b"/><stop offset="0.52" stop-color="#3f7fd0"/><stop offset="0.8" stop-color="#8cc8f2"/><stop offset="1" stop-color="#d6efff"/></linearGradient>'
         '</defs></svg>')
BED2 = (L2 + 500, 1330)
H.append(cama_tumbado("p2", *BED2, s=0.62, cm=12, beard=10))
H.append(f'<div id="pago" class="badge" style="left:{L2 + 820}px;top:1060px;background:{GOOD};font-size:50px">€ TE PAGAN</div>')
H.append(f'<div id="inclina" class="badge" style="left:{L2 + 330}px;top:900px;background:#3d405b;font-size:40px">−6° CABEZA ABAJO</div>')

# ---- CIELO: columna para subir desde el tejado hasta el espacio (fuera de la casa)
SKX = 9400
nubes = "".join(f'<g opacity="0.95"><ellipse cx="{cx}" cy="{cy}" rx="150" ry="55" fill="#ffffff"/><ellipse cx="{cx - 90}" cy="{cy + 15}" rx="95" ry="45" fill="#ffffff"/><ellipse cx="{cx + 95}" cy="{cy + 20}" rx="110" ry="42" fill="#f3f8ff"/></g>'
                for cx, cy in ((260, 900), (1180, 420), (520, -200), (1250, -760), (300, -1350), (1050, -1900), (600, -2450)))
casas = "".join(f'<rect x="{x}" y="{1920 - h}" width="{w}" height="{h}" fill="{c}"/><path d="M{x - 20},{1920 - h} L{x + w / 2:.0f},{1920 - h - 120} L{x + w + 20},{1920 - h} Z" fill="#8a4e3c"/>'
                + "".join(f'<rect x="{x + 30 + k * 70}" y="{1920 - h + 60}" width="40" height="50" fill="#ffe7a6"/>' for k in range(max(1, (w - 40) // 70)))
                for x, w, h, c in ((40, 330, 330, "#e9cbb0"), (420, 420, 420, "#f2d9c2"), (900, 300, 300, "#dcbfa5"), (1240, 240, 360, "#e9cbb0")))
estrellas_cielo = "".join(f'<circle cx="{random.uniform(0, 1500):.0f}" cy="{random.uniform(-4200, -2600):.0f}" r="{random.choice([2, 2, 3])}" fill="#fff" opacity="{random.uniform(0.4, 0.9):.2f}"/>' for _ in range(90))
H.append(f'<svg style="position:absolute;left:{SKX}px;top:-4200px;overflow:visible" width="1500" height="6420" viewBox="0 -4200 1500 6420">'
         f'<rect x="0" y="-4200" width="1500" height="6120" fill="url(#cieloG)"/>{estrellas_cielo}{nubes}{casas}'
         f'<rect x="0" y="1880" width="1500" height="340" fill="#6aa86b"/></svg>')
PAJAROS = "".join(f'<path d="M{dx},{dy} q18,-16 36,0 q18,-16 36,0" stroke="#2b2f4a" stroke-width="7" fill="none" stroke-linecap="round"/>' for dx, dy in ((0, 0), (70, 40), (130, -20), (190, 30), (250, 5)))
H.append(f'<svg id="pajaros" style="position:absolute;left:{SKX - 400}px;top:700px;overflow:visible" width="10" height="10">{PAJAROS}</svg>')
H.append(f'<svg id="pajaros2" style="position:absolute;left:{SKX + 1700}px;top:-350px;overflow:visible" width="10" height="10">{PAJAROS}</svg>')
AVION = ('<path d="M-300,22 L-40,22" stroke="#ffffff" stroke-width="10" opacity="0.7" stroke-linecap="round"/>'
         '<path d="M0,10 L220,0 C250,0 262,14 250,26 L0,34 Z" fill="#f4f6fb"/><path d="M90,20 L40,-60 L80,-60 L150,18 Z" fill="#dfe5ee"/><path d="M90,26 L40,100 L80,100 L150,28 Z" fill="#cfd6e4"/>'
         '<path d="M10,12 L-20,-40 L10,-40 L40,12 Z" fill="#e5484d"/>' + "".join(f'<circle cx="{60 + k * 26}" cy="16" r="5" fill="#9fd3f5"/>' for k in range(6)))
H.append(f'<svg id="avion" style="position:absolute;left:{SKX - 500}px;top:-1150px;overflow:visible" width="10" height="10">{AVION}</svg>')
H.append(f'<svg id="avion2" style="position:absolute;left:{SKX + 1800}px;top:-2050px;overflow:visible" width="10" height="10"><g transform="scale(-0.8,0.8)">{AVION}</g></svg>')

# ---- ESPACIO: la Tierra abajo con su curva, la Luna y el astronauta
SPX = 11200
estrellas_esp = "".join(f'<circle cx="{random.uniform(-200, 1700):.0f}" cy="{random.uniform(-200, 1700):.0f}" r="{random.choice([2, 2, 3, 4])}" fill="#fff" opacity="{random.uniform(0.4, 0.95):.2f}"/>' for _ in range(160))
H.append(f'<svg style="position:absolute;left:{SPX}px;top:0;overflow:visible" width="1500" height="1920" viewBox="0 0 1500 1920">'
         f'<rect x="-200" y="-300" width="1900" height="2800" fill="url(#espacioG)"/>{estrellas_esp}'
         '<circle cx="1180" cy="420" r="110" fill="#e9dccb"/><circle cx="1150" cy="390" r="22" fill="#cbbca8"/><circle cx="1215" cy="460" r="16" fill="#cbbca8"/>'
         '<circle cx="750" cy="3700" r="2050" fill="#9fd3f5" opacity="0.35"/><circle cx="750" cy="3700" r="2000" fill="#3f7fc4"/>'
         '<path d="M-260,1820 C40,1700 260,1790 520,1720 C760,1660 1000,1760 1240,1700 C1420,1660 1600,1720 1760,1700 L1760,2600 L-260,2600 Z" fill="#5fae6e" opacity="0.9"/>'
         '<ellipse cx="420" cy="1760" rx="160" ry="30" fill="#ffffff" opacity="0.7"/><ellipse cx="1100" cy="1790" rx="200" ry="34" fill="#ffffff" opacity="0.6"/></svg>')
H.append(f'<svg id="astro" style="position:absolute;left:{SPX + 600}px;top:620px;overflow:visible" width="10" height="10">'
         '<rect x="-40" y="140" width="80" height="120" rx="20" fill="#cfd6e4"/><rect x="40" y="130" width="200" height="230" rx="70" fill="#f4f6fb"/>'
         '<circle cx="140" cy="90" r="95" fill="#f4f6fb"/><ellipse cx="150" cy="95" rx="66" ry="56" fill="#1d2356"/><ellipse cx="130" cy="75" rx="22" ry="14" fill="#9fd3f5" opacity="0.7"/>'
         '<rect x="-10" y="170" width="70" height="40" rx="20" fill="#f4f6fb" transform="rotate(-30 25 190)"/><rect x="220" y="190" width="80" height="44" rx="22" fill="#f4f6fb" transform="rotate(35 260 212)"/>'
         '<rect x="70" y="340" width="60" height="120" rx="28" fill="#f4f6fb" transform="rotate(12 100 400)"/><rect x="150" y="340" width="60" height="120" rx="28" fill="#f4f6fb" transform="rotate(-18 180 400)"/>'
         '<rect x="100" y="190" width="80" height="50" rx="10" fill="#e5484d"/></svg>')
# tarjeta de los huesos: va en la capa de gráficos (no en el mundo), así acompaña la subida
OVER = [f'<div id="hueso" class="card" style="left:60px;top:1240px;width:330px;padding:20px 24px"><div class="card-top" style="font-size:26px">TUS HUESOS</div>'
        f'<svg width="280" height="110" viewBox="0 0 250 110"><path d="M40,40 a22,22 0 1,1 20,-25 L190,15 a22,22 0 1,1 20,25 a22,22 0 1,1 -20,25 L60,65 a22,22 0 1,1 -20,-25 Z" fill="#fbf3e6" stroke="#cbbca8" stroke-width="5"/>'
        + "".join(f'<circle class="poro" cx="{70 + (i % 6) * 22}" cy="{30 + (i // 6) * 16}" r="5" fill="#cbbca8" opacity="0"/>' for i in range(18))
        + f'</svg><div style="font:900 34px Inter;color:{BAD}">− CALCIO</div></div>']

# ---- 3 · CONSULTA: corazón y riñón
L3 = RL(3)
H.append(sala(3, '<rect x="170" y="560" width="1160" height="860" rx="30" fill="#2a3346"/><rect x="190" y="580" width="1120" height="820" rx="22" fill="#eaf4ff"/>'
              '<rect x="190" y="580" width="1120" height="820" rx="22" fill="url(#luzsala)" opacity="0.4"/><line x1="750" y1="610" x2="750" y2="1370" stroke="#c9d6e6" stroke-width="6"/>'
              '<text x="470" y="660" text-anchor="middle" font-family="Inter" font-weight="900" font-size="40" fill="#5a6b85">CORAZÓN</text>'
              '<text x="1030" y="660" text-anchor="middle" font-family="Inter" font-weight="900" font-size="40" fill="#5a6b85">RIÑÓN</text>'
              '<rect x="80" y="1480" width="420" height="40" rx="10" fill="#c99067"/><rect x="100" y="1520" width="24" height="180" fill="#8a5a3c"/><rect x="456" y="1520" width="24" height="180" fill="#8a5a3c"/>'
              '<rect x="1060" y="1300" width="300" height="400" rx="20" fill="#9aa3b5"/><rect x="1080" y="1320" width="260" height="120" rx="12" fill="#c9d0dc"/>'
              + planta(1420, 1610), pared_suelo("s3", "#e4ecf3", "#cdd9e6", "#b8c4d0", "#9aa7b6", rayas=False, zocalo="#ffffff")))
H.append(f'''<svg id="corazon" style="position:absolute;left:{L3 + 470}px;top:1010px;overflow:visible" width="10" height="10">
<path d="M0,-120 C-60,-220 -230,-170 -200,-30 C-180,70 -60,140 0,220 C60,140 180,70 200,-30 C230,-170 60,-220 0,-120 Z" fill="#e5484d"/>
<path d="M-120,-150 C-150,-130 -170,-90 -160,-50" stroke="#ff9a90" stroke-width="16" fill="none" stroke-linecap="round" opacity="0.7"/>
<path d="M-40,-190 L-40,-260 M40,-180 L60,-250" stroke="#c2453e" stroke-width="30" stroke-linecap="round"/></svg>''')
H.append(f'''<svg id="rinon" style="position:absolute;left:{L3 + 1030}px;top:1010px;overflow:visible" width="10" height="10">
<path d="M-60,-220 C80,-260 190,-140 160,10 C140,140 60,230 -40,210 C-130,190 -150,90 -90,40 C-40,0 -60,-60 -110,-80 C-170,-110 -150,-200 -60,-220 Z" fill="#b5544c"/>
<path d="M-40,-150 C40,-160 100,-90 90,10" stroke="#d27a70" stroke-width="20" fill="none" stroke-linecap="round" opacity="0.6"/>
<circle class="piedra" cx="30" cy="-40" r="20" fill="#f2e6c9" opacity="0"/><circle class="piedra" cx="70" cy="40" r="15" fill="#f2e6c9" opacity="0"/>
<circle class="piedra" cx="0" cy="90" r="24" fill="#f2e6c9" opacity="0"/><circle class="piedra" cx="-30" cy="10" r="12" fill="#f2e6c9" opacity="0"/></svg>''')

# ---- 4 · DORMITORIO, 5 años después (polvo, telarañas, platos)
L4 = RL(4)
telas = ('<path d="M0,0 L220,0 M0,0 L0,220 M0,0 L170,170 M0,60 Q60,60 60,0 M0,120 Q120,120 120,0 M0,180 Q170,170 180,0" stroke="#ffffff" stroke-width="4" fill="none" opacity="0.55"/>'
         f'<path d="M{RW},0 L{RW - 220},0 M{RW},0 L{RW},220 M{RW},0 L{RW - 170},170 M{RW},70 Q{RW - 70},70 {RW - 70},0 M{RW},140 Q{RW - 140},140 {RW - 140},0" stroke="#ffffff" stroke-width="4" fill="none" opacity="0.55"/>')
platos = "".join(f'<ellipse cx="{230 - i * 4}" cy="{1690 - i * 22}" rx="80" ry="16" fill="#fbf8f2" stroke="#cbbca8" stroke-width="3"/>' for i in range(9))
H.append(sala(4, ventana(940, 420, 330, 470, cortina="#7d8aa0") + '<g transform="rotate(-8 345 635)">' + cuadro(230, 520, 230, 230) + '</g>'
              + reloj("clk4", 640, 640) + calendario("cal4", 1290, 1010, "AÑO 5") + lampara_mesita(40)
              + f'<ellipse cx="760" cy="1800" rx="560" ry="60" fill="#8f6a5c" opacity="0.55"/>' + planta(1380, 1610, seca=True) + platos + telas
              + f'<rect x="0" y="0" width="{RW}" height="1920" fill="#7a6a58" opacity="0.13"/>',
              pared_suelo("s4", "#e6cdb6", "#d2b195", "#9c6c4c", "#7a5238")))
BED4 = (L4 + 470, 1330)
H.append(cama_tumbado("p4", *BED4, s=0.62, cm=60, beard=100))
H.append(pj_at("p4s", L4 + 1090, cm=60, beard=100))
H.append(f'<div id="bocadillo" class="card" style="left:{L4 + 640}px;top:780px;width:540px;padding:24px 30px;border-radius:40px">'
         f'<div class="card-big" style="font-size:52px;color:{GOOD};line-height:1.1">¡YA PUEDES LEVANTARTE!</div></div>')
H.append(f'''<svg id="mareo" style="position:absolute;left:{L4 + 1090}px;top:640px;overflow:visible;opacity:0" width="10" height="10">
<g id="mareo-g"><ellipse id="mareo-e" cx="0" cy="0" rx="150" ry="36" fill="none" stroke="#f2b84b" stroke-width="7" stroke-dasharray="26 18"/>
<path d="M150,0 l14,-10 4,16 Z M-150,0 l-14,10 -4,-16 Z" fill="#f2b84b"/>
<text x="-120" y="-30" font-size="44" fill="#fbf8f2">★</text><text x="90" y="40" font-size="40" fill="#fbf8f2">★</text></g></svg>''')
H.append(f'''<svg id="sangre" style="position:absolute;left:{L4 + 1260}px;top:900px;overflow:visible;opacity:0" width="10" height="10">
<path id="sangre-p" d="M0,0 L0,620" stroke="{BAD}" stroke-width="22" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>
<path d="M-40,580 L0,650 L40,580" stroke="{BAD}" stroke-width="22" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="0" cy="-30" r="24" fill="{BAD}"/></svg>''')

# ---- 5 · GIMNASIO DE REHABILITACIÓN
L5 = RL(5)
H.append(sala(5, ventana(980, 380, 360, 420, cortina="#3fbf7f")
              + '<rect x="160" y="700" width="520" height="130" rx="20" fill="#3fbf7f"/><text x="420" y="785" text-anchor="middle" font-family="Inter" font-weight="900" font-size="54" fill="#fff">REHABILITACIÓN</text>'
              + '<rect x="40" y="1300" width="120" height="400" rx="12" fill="#5a6b85"/>' + "".join(f'<rect x="56" y="{1330 + i * 90}" width="88" height="22" rx="11" fill="#e5484d"/>' for i in range(4))
              + '<rect x="1200" y="1450" width="300" height="80" fill="#c99067"/><rect x="1280" y="1370" width="220" height="80" fill="#d9a77e"/><rect x="1360" y="1290" width="140" height="80" fill="#e8bb92"/>'
              + '<rect x="0" y="1760" width="1500" height="40" fill="#5b86c4" opacity="0.6"/><circle cx="1110" cy="1600" r="95" fill="#f2b84b"/>',
              pared_suelo("s5", "#dff3ea", "#c4e6d6", "#d9b38c", "#bf966e")))
H.append(f'<svg style="position:absolute;left:{L5}px;top:0;overflow:visible" width="1" height="1">'
         '<rect x="300" y="1225" width="800" height="18" rx="9" fill="#9aa3b5" opacity="0.7"/>'
         + "".join(f'<rect x="{x}" y="1225" width="22" height="475" fill="#7c8496" opacity="0.7"/>' for x in (310, 1070)) + '</svg>')
H.append(pj_at("p5", L5 + 700, cm=60, beard=100))
H.append(f'<svg style="position:absolute;left:{L5}px;top:0;overflow:visible" width="1" height="1">'
         '<rect x="280" y="1262" width="840" height="22" rx="11" fill="#c9d0dc"/>'
         + "".join(f'<rect x="{x}" y="1262" width="26" height="440" fill="#9aa3b5"/>' for x in (290, 1090)) + '</svg>')

# separadores entre habitaciones (paredes de la «casa de muñecas»)
H.append(f'<svg style="position:absolute;left:0;top:0;overflow:visible" width="1" height="1">'
         + "".join(f'<rect x="{RL(k) - 18}" y="0" width="36" height="1920" fill="#3b3552"/>' for k in range(1, 6)) + '</svg>')

# ------------------------------------------------------------------ guion → animación (todo con P())
for pid in ("p0", "p2", "p4", "p4s", "p5"):
    vida(pid)
CAMS = {"cama0": (L0 + 660, 1150, 0.95), "cara0": (BED0[0] - 70, 1260, 1.5)}
def corte(t, x, y, z):
    """Corte limpio de una escena a otra: oscurece 0,14 s, cambia de plano y vuelve."""
    J(f'tl.to("#dip", {{opacity:0.6, duration:0.14, ease:"power1.in"}}, {t - 0.14:.2f}); tl.to("#dip", {{opacity:0, duration:0.32}}, {t:.2f});')
    J(f'tl.set("#world", {{x:{540 - x * z:.1f}, y:{960 - y * z:.1f}, scale:{z}}}, {t:.2f});')
    J(f'tl.set("#lejos", {{x:{(540 - x * z) * 0.35:.1f}}}, {t:.2f});')
    FX_EV.append(("whoosh", t - 0.1))

def camk(t, nombre, dur=1.2, viaje=False):
    x, y, z = CAMS[nombre]
    cam(t, x, y, z, dur=dur, viaje=viaje)

J('tl.set("#world", {x:%.1f, y:%.1f, scale:%.2f}, 0);' % (540 - CAMS["cara0"][0] * CAMS["cara0"][2], 960 - CAMS["cara0"][1] * CAMS["cara0"][2], CAMS["cara0"][2]))
for sel in ["#escaras", "#fuerza", "#hueso", "#pago", "#inclina", "#bocadillo", "#p4s"]:
    J(f'tl.set("{sel}", {{opacity:0}}, 0);')

# 1 · gancho: cara en la almohada, la cámara se abre y enseña la cama
J(f'tl.fromTo("#p0-eyes", {{scaleY:0.15}}, {{scaleY:1, duration:0.35, svgOrigin:"500 742", immediateRender:false}}, 0.3);')
cam(P("tumbado") - 0.3, L0 + 620, 1200, 1.05, dur=1.6, ease="power2.inOut")
# 2 · te traen la comida
tco = P("comida")
J(f'tl.fromTo("#bandeja", {{opacity:0, x:260}}, {{opacity:1, x:0, duration:0.7, ease:"power3.out", immediateRender:false}}, {tco - 0.2:.2f});')
FX_EV.append(("whoosh", tco - 0.2))
J(f'tl.to("#p0-mouth", {{attr:{{d:"M474,814 Q500,840 526,814"}}, duration:0.3}}, {tco + 0.3:.2f});')
# 3 · vacaciones: gafas de sol
tva = P("vacaciones")
J(f'tl.fromTo("#gafas", {{opacity:0, y:-120}}, {{opacity:1, y:0, duration:0.45, ease:"bounce.out", immediateRender:false}}, {tva - 0.2:.2f});')
FX_EV.append(("pop", tva))
cam(tva - 0.3, BED0[0] + 40, 1250, 1.25, dur=0.8)
# 4 · cada dos horas: reloj que gira y flecha de la vuelta
tdh = P("dos")
J(f'tl.to("#gafas", {{opacity:0, duration:0.25}}, {tdh - 0.5:.2f}); tl.to("#p0-mouth", {{attr:{{d:"M478,816 Q500,832 522,816"}}, duration:0.3}}, {tdh - 0.5:.2f});')
cam(tdh - 0.5, L0 + 660, 1050, 0.95, dur=0.8)
J(f'tl.to("#clkm", {{rotation:720, duration:1.6, ease:"power2.inOut", svgOrigin:"640 640"}}, {tdh:.2f}); tl.to("#clkh", {{rotation:60, duration:1.6, ease:"power2.inOut", svgOrigin:"640 640"}}, {tdh:.2f});')
J(f'tl.to("#vuelta", {{opacity:1, duration:0.2}}, {P("vuelta") - 0.4:.2f}); tl.to("#vuelta-p", {{strokeDashoffset:0, duration:0.7, ease:"power2.out"}}, {P("vuelta") - 0.4:.2f});')
J(f'tl.to("#p0-rot", {{rotation:-5, duration:0.35, yoyo:true, repeat:3, ease:"sine.inOut", transformOrigin:"{BED0[0] + 200}px {BED0[1]}px"}}, {P("vuelta") - 0.1:.2f});')
FX_EV.append(("whoosh", P("vuelta")))
# 5 · escaras
tes = P("escaras")
J(f'tl.to("#vuelta", {{opacity:0, duration:0.3}}, {F(5) - 0.1:.2f});')
pop("#escaras", P("piel") - 0.1)
J(f'tl.to("#escaras .llaga", {{opacity:1, duration:0.3, stagger:0.2}}, {P("rompe"):.2f});')
J(f'tl.to("#p0-mouth", {{attr:{{d:"M482,826 Q500,812 518,826"}}, duration:0.25}}, {P("rompe"):.2f});')
# 6 · primer mes: fuerza de las piernas
tme = P("mes")
J(f'tl.to("#escaras", {{opacity:0, x:40, duration:0.3}}, {tme - 0.6:.2f});')
pop("#fuerza", tme - 0.2)
J(f'tl.fromTo("#fuerza-b", {{scaleX:1}}, {{scaleX:0.45, duration:1.4, ease:"power2.inOut", immediateRender:false}}, {P("piernas"):.2f});')
J(f'tl.to("#musculo", {{attr:{{rx:44, ry:14}}, duration:1.4, ease:"power2.inOut"}}, {P("piernas"):.2f});')
J(f'tl.to("#cal0", {{opacity:0, duration:0.15, yoyo:true, repeat:1}}, {tme:.2f}); tl.set("#cal0", {{textContent:"MES 1"}}, {tme + 0.15:.2f});')

# 7 · baño: el baño viene a ti
t = F(7)
J(f'tl.to("#fuerza", {{opacity:0, duration:0.3}}, {t:.2f});')
cam(t, L1 + 760, 1150, 0.95, dur=1.3, viaje=True)
tve = P("venir")
J(f'tl.to("#ruedas", {{opacity:1, duration:0.2}}, {tve - 0.6:.2f});')
J(f'tl.to("#inodoro", {{y:-30, duration:0.12, yoyo:true, repeat:1}}, {tve - 0.4:.2f});')
J(f'tl.to("#inodoro", {{x:-1060, duration:1.8, ease:"power2.inOut"}}, {tve - 0.15:.2f});')
cam(tve, L0 + 860, 1150, 0.95, dur=min(1.8, F(8) - tve - 0.3), ease="power2.inOut")
J(f'tl.to("#inodoro", {{rotation:-4, duration:0.2, yoyo:true, repeat:5, transformOrigin:"50% 100%"}}, {tve - 0.15:.2f});')
FX_EV.append(("whoosh", tve + 0.3))

# 8 · un año: SUBIMOS AL CIELO (pájaros, aviones) y llegamos al espacio
t = F(8)
corte(t, SKX + 750, 1250, 0.95)
tas = P("astronauta")
J(f'tl.to("#world", {{y:{960 - (-2950) * 0.95:.1f}, duration:{tas - 0.45 - t:.2f}, ease:"power1.inOut"}}, {t + 0.05:.2f});')
J(f'tl.fromTo("#pajaros", {{x:0}}, {{x:2300, duration:3.2, ease:"none", immediateRender:false}}, {t:.2f});')
J(f'tl.fromTo("#pajaros2", {{x:0}}, {{x:-2400, duration:3.4, ease:"none", immediateRender:false}}, {t + 0.4:.2f});')
J(f'tl.fromTo("#avion", {{x:0}}, {{x:2600, duration:3.0, ease:"none", immediateRender:false}}, {t + 0.6:.2f});')
J(f'tl.fromTo("#avion2", {{x:0}}, {{x:-2700, duration:3.0, ease:"none", immediateRender:false}}, {t + 1.0:.2f});')
FX_EV.append(("whoosh", t + 0.8))
pop("#hueso", P("huesos"))
J(f'tl.to("#hueso .poro", {{opacity:1, duration:0.2, stagger:0.08}}, {P("calcio"):.2f});')
corte(tas - 0.3, SPX + 750, 1000, 0.95)
J(f'tl.fromTo("#astro", {{y:-20, rotation:-6}}, {{y:30, rotation:6, duration:2.2, ease:"sine.inOut", yoyo:true, repeat:3, transformOrigin:"50% 50%", immediateRender:false}}, {tas - 0.3:.2f});')
cam(tas - 0.2, SPX + 750, 1100, 0.85, dur=min(2.4, F(9) - tas - 0.1), ease="sine.inOut")
# 9 · las agencias espaciales pagan a voluntarios (laboratorio, otra escena)
t = F(9)
J(f'tl.to("#hueso", {{opacity:0, x:-40, duration:0.3}}, {t - 0.2:.2f});')
corte(t, L2 + 700, 1150, 0.95)
pop("#pago", P("pagan"))
FX_EV.append(("pop", P("pagan")))
J(f'tl.to("#ecg", {{x:-30, duration:0.6, ease:"none", repeat:6, yoyo:true}}, {t:.2f});')
# 10 · lo más parecido al espacio: la cama se inclina 6° cabeza abajo (como en los estudios reales)
t = F(10)
J(f'tl.to("#p2-lie", {{rotation:-6, duration:1.0, ease:"power2.inOut", transformOrigin:"{BED2[0] + 200}px {FLOOR}px"}}, {t:.2f});')
pop("#inclina", t + 0.5)
cam(t, L2 + 700, 1180, 0.98, dur=1.4, ease="sine.inOut")

# 11 · corazón más pequeño (consulta)
t = F(11)
J(f'tl.to(["#pago", "#inclina"], {{opacity:0, duration:0.3}}, {t:.2f});')
cam(t, L3 + 750, 1060, 0.8, dur=1.3, viaje=True)
J(f'tl.fromTo("#corazon", {{scale:1}}, {{scale:1.08, duration:0.35, yoyo:true, repeat:9, ease:"sine.inOut", transformOrigin:"50% 50%", immediateRender:false}}, {t:.2f});')
J(f'tl.to("#corazon", {{scale:0.72, duration:1.0, ease:"power2.inOut", transformOrigin:"50% 50%"}}, {P("pequeno"):.2f});')
FX_EV.append(("golpe", P("pequeno")))
# 12 · piedras en el riñón
cam(P("calcio", 2) - 0.3, L3 + 950, 1040, 0.95, dur=0.9)
J(f'tl.fromTo("#rinon .piedra", {{opacity:0, scale:0}}, {{opacity:1, scale:1, duration:0.35, stagger:0.18, ease:"back.out(2)", transformOrigin:"50% 50%", immediateRender:false}}, {P("piedras"):.2f});')
FX_EV.append(("pop", P("piedras")))

# 13 · cinco años después: ¡ya puedes levantarte!
t = F(13)
cam(t, L4 + 700, 1150, 0.95, dur=1.3, viaje=True)
tle = P("levantarte")
pop("#bocadillo", P("dicen"))
FX_EV.append(("pop", P("dicen")))
J(f'tl.to("#p4-eyes", {{scaleY:1.25, duration:0.2, svgOrigin:"500 742"}}, {tle:.2f});')
# 14 · de pie… y todo da vueltas
tpi = P("pie")
J(f'tl.to("#bocadillo", {{opacity:0, duration:0.3}}, {tpi - 0.5:.2f});')
J(f'tl.to("#p4-rot", {{opacity:0, duration:0.35}}, {tpi - 0.2:.2f});')
J(f'tl.to("#p4-cubre", {{scaleY:0.45, duration:0.45, ease:"power2.out", transformOrigin:"{BED4[0]}px {BED4[1] + 200}px"}}, {tpi - 0.2:.2f});')
J(f'tl.fromTo("#p4s", {{opacity:0, y:160, x:-260}}, {{opacity:1, y:0, x:0, duration:0.6, ease:"power2.out", immediateRender:false}}, {tpi - 0.2:.2f});')
cam(tpi, L4 + 960, 1150, 1.0, dur=0.8)
J(f'tl.to("#p4s", {{rotation:4, duration:0.45, yoyo:true, repeat:7, ease:"sine.inOut", transformOrigin:"50% 94%"}}, {tpi + 0.5:.2f});')
J(f'tl.to("#mareo", {{opacity:1, duration:0.3}}, {P("vueltas") - 0.3:.2f}); tl.to("#mareo-e", {{strokeDashoffset:-440, duration:2.0, ease:"none", repeat:2}}, {P("vueltas") - 0.3:.2f});')
J(f'tl.to("#p4s-eyes", {{scaleY:0.4, duration:0.2, svgOrigin:"500 742"}}, {P("vueltas"):.2f});')
# 15 · la sangre baja a los pies
tsa = P("sangre")
J(f'tl.to("#sangre", {{opacity:1, duration:0.2}}, {tsa:.2f}); tl.to("#sangre-p", {{strokeDashoffset:0, duration:0.9, ease:"power2.in"}}, {tsa:.2f});')
tde = P("desmayarte")
J(f'tl.to("#p4s-up", {{scaleY:0.93, duration:0.4, ease:"power2.in", svgOrigin:"500 1290"}}, {tde - 0.1:.2f}); tl.to("#p4s-up", {{scaleY:1, duration:0.5, ease:"power2.out", svgOrigin:"500 1290"}}, {tde + 0.6:.2f});')
J(f'tl.to(["#mareo", "#sangre"], {{opacity:0, duration:0.4}}, {FE(15) + 0.1:.2f});')

# 16-17 · rehabilitación: volver a andar entre barras
t = F(16)
cam(t, L5 + 700, 1150, 0.95, dur=1.3, viaje=True)
J(f'tl.to("#p5-legs", {{x:6, duration:0.12, yoyo:true, repeat:9, ease:"sine.inOut"}}, {P("sostienen"):.2f});')
J(f'tl.to("#p5-mouth", {{attr:{{d:"M482,826 Q500,812 518,826"}}, duration:0.25}}, {P("sostienen"):.2f});')
tre = P("rehabilitacion")
caminar_lento = []
J(f'tl.fromTo("#p5", {{x:-260}}, {{x:120, duration:3.4, ease:"sine.inOut", immediateRender:false}}, {tre - 0.4:.2f});')
for k in range(8):
    tk = tre - 0.4 + k * 0.42
    pie = "legL" if k % 2 == 0 else "legR"
    J(f'tl.to("#p5-{pie}", {{y:-18, duration:0.21, yoyo:true, repeat:1, ease:"sine.inOut"}}, {tk:.2f});')
J(f'tl.set("#p5", {{x:-260}}, 0);')
J(f'tl.to("#p5-mouth", {{attr:{{d:"M474,814 Q500,840 526,814"}}, duration:0.3}}, {P("paso", 2):.2f});')
FX_EV.append(("pop", P("paso", 2)))

# 18 · BUCLE: corte limpio al dormitorio del día 1 (= fotograma 0)
tcut = P("con") - 0.1
J(f'tl.to("#dip", {{opacity:0.45, duration:0.12, ease:"power1.in"}}, {tcut - 0.12:.2f}); tl.to("#dip", {{opacity:0, duration:0.3}}, {tcut:.2f});')
x0, y0, z0 = CAMS["cara0"]
J(f'tl.set("#world", {{x:{540 - x0 * z0:.1f}, y:{960 - y0 * z0:.1f}, scale:{z0}}}, {tcut:.2f});')
J(f'tl.set("#inodoro", {{x:0, rotation:0}}, {tcut:.2f}); tl.set("#ruedas", {{opacity:0}}, {tcut:.2f});')
J(f'tl.set("#bandeja", {{opacity:0}}, {tcut:.2f}); tl.set("#cal0", {{textContent:"DÍA 1"}}, {tcut:.2f}); tl.set(["#clkm", "#clkh"], {{rotation:0, svgOrigin:"640 640"}}, {tcut:.2f});')
J(f'tl.set("#p0-mouth", {{attr:{{d:"M478,816 Q500,832 522,816"}}}}, {tcut:.2f}); tl.set(".llaga", {{opacity:0}}, {tcut:.2f});')
J(f'tl.set("#p0-eyes", {{scaleY:0.15, svgOrigin:"500 742"}}, {DUR - 0.05:.2f});')
FX_EV.append(("whoosh", tcut))

# --- HUD: día 1 → 1 mes → 1 año → 5 años
def hud_a(t, i, k_prev, k_new, dur=0.9):
    J(f'tl.to("#hud", {{opacity:1, y:0, duration:0.35, ease:"power3.out"}}, {t - 0.4:.2f}); tl.to("#hud", {{opacity:0, y:-20, duration:0.35, ease:"power2.in"}}, {t + 2.6:.2f});')
    x = HXI(i)
    J(f'tl.to("#hud-dot", {{x:{x - 60:.0f}, duration:{dur}, ease:"power3.inOut"}}, {t:.2f});')
    J(f'tl.to("#hud-fill", {{scaleX:{i / 3:.3f}, duration:{dur}, ease:"power3.inOut"}}, {t:.2f});')
    J(f'tl.to(".hud-pill", {{x:{min(x, 790):.0f}, duration:{dur}, ease:"power3.inOut"}}, {t:.2f});')
    if k_prev is not None:
        J(f'tl.to("#hp{k_prev}", {{opacity:0, y:-10, duration:0.2}}, {t:.2f});')
    J(f'tl.fromTo("#hp{k_new}", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:0.35, ease:"back.out(2)", immediateRender:false}}, {t + dur * 0.7:.2f});')
    FX_EV.append(("clic", t + dur * 0.9))
J(f'tl.set(".hud-pill", {{xPercent:-50, x:{HXI(0):.0f}, y:0}}, 0); tl.set("#hud-fill", {{scaleX:0}}, 0); tl.set("#hud-dot", {{x:0}}, 0);')
t_in = F(4) - 0.2
J(f'tl.fromTo("#hud", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:0.5, ease:"power3.out", immediateRender:false}}, {t_in:.2f});')
J(f'tl.fromTo("#hp0", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:0.35, immediateRender:false}}, {t_in + 0.2:.2f});')
J(f'tl.to("#hud", {{opacity:0, y:-20, duration:0.35, ease:"power2.in"}}, {t_in + 2.6:.2f});')
hud_a(P("mes") - 0.3, 1, 0, 1)
hud_a(F(8) + 0.2, 2, 1, 2)
hud_a(F(13) + 0.2, 3, 2, 3)
J(f'tl.set(".hud-pill", {{opacity:0}}, {tcut:.2f});')

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
J(f'tl.fromTo("#calido", {{opacity:0}}, {{opacity:0.55, duration:{DUR / 4:.4f}, ease:"sine.inOut", yoyo:true, repeat:3, immediateRender:false}}, 0);')
MOTAS = []
for i in range(60):
    x = random.uniform(0, WORLD_W)
    y = random.uniform(200, 1350)
    MOTAS.append(f'<div class="mota" id="mota{i}" style="left:{x:.0f}px;top:{y:.0f}px"></div>')
    J(f'tl.fromTo("#mota{i}", {{y:0, opacity:0.25}}, {{y:{-random.uniform(60, 160):.0f}, opacity:0.25, duration:{random.uniform(5, 8):.1f}, ease:"sine.inOut", yoyo:true, repeat:{int(DUR / 6)}}}, {random.uniform(0, 3):.2f});')

# ------------------------------------------------------------------ subtítulos (arriba, palabra a palabra)
CLAVE = {"cinco", "tumbado", "comida", "vacaciones", "dos", "vuelta", "escaras", "mes", "fuerza", "bano", "calcio",
         "astronauta", "pagan", "espacio", "corazon", "pequeno", "piedras", "rinon", "levantarte", "vueltas", "sangre",
         "desmayarte", "andar", "rehabilitacion", "cama"}
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


HUD = ['<div id="hud"><div class="hud-track"></div><div id="hud-fill" class="hud-fill"></div>']
for i, lab in enumerate(["día 1", "1 mes", "1 año", "5 años"]):
    HUD.append(f'<div class="hud-tick" style="left:{HXI(i) - 3:.0f}px"></div><div class="hud-lab" style="left:{HXI(i) - 50:.0f}px;width:100px">{lab}</div>')
HUD.append('<div id="hud-dot" class="hud-dot"></div>')
for k, txt in enumerate(["DÍA 1", "1 MES", "1 AÑO", "5 AÑOS"]):
    HUD.append(f'<div id="hp{k}" class="hud-pill">{txt}</div>')
HUD.append('</div>')
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
.plato{{display:none;position:absolute;width:760px;height:150px;border-radius:50%;background:radial-gradient(50% 50% at 50% 45%, #a7abe3 0%, #8a8ed0 60%, rgba(138,142,208,0) 100%)}}
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
#dip{{position:absolute;inset:0;background:#141230;opacity:0;pointer-events:none}}
#sombra-subs{{position:absolute;left:0;right:0;top:0;height:720px;background:linear-gradient(rgba(18,16,40,0.55),rgba(18,16,40,0.32) 55%,rgba(18,16,40,0));pointer-events:none}}
#vineta{{position:absolute;inset:0;background:radial-gradient(120% 80% at 50% 45%, rgba(0,0,0,0) 55%, rgba(18,16,48,0.38) 100%);pointer-events:none}}
#grano{{position:absolute;left:0;top:0;opacity:0.05;mix-blend-mode:overlay;pointer-events:none}}
#hud{{position:absolute;left:70px;width:940px;top:490px;height:130px;opacity:0;background:rgba(18,16,40,0.38);border-radius:28px}}
.hud-track{{position:absolute;left:60px;right:0;top:62px;width:840px;height:8px;border-radius:4px;background:rgba(255,255,255,0.22)}}
.hud-fill{{position:absolute;left:60px;top:62px;width:840px;height:8px;border-radius:4px;background:linear-gradient(90deg,#ffd37a,#f2b84b);transform-origin:0 50%}}
.hud-tick{{position:absolute;top:56px;width:6px;height:20px;border-radius:3px;background:rgba(255,255,255,0.55)}}
.hud-lab{{position:absolute;top:84px;width:60px;text-align:center;font:700 24px Inter;color:rgba(255,255,255,0.7)}}
.hud-unit{{position:absolute;right:-70px;top:84px;font:700 22px Inter;color:rgba(255,255,255,0.55)}}
.hud-dot{{position:absolute;left:44px;top:50px;width:32px;height:32px;border-radius:50%;background:#fff;border:7px solid #f2b84b;box-shadow:0 4px 14px rgba(0,0,0,0.3)}}
.hud-pill{{position:absolute;left:0;top:0;white-space:nowrap;padding:8px 18px;border-radius:16px;background:#fbf8f2;color:#1d2b33;font:900 30px Inter;box-shadow:0 6px 18px rgba(0,0,0,0.25);opacity:0}}
.hud-bad{{background:{BAD};color:#fff}}
.hud-stop{{position:absolute;top:40px;width:44px;height:44px;border-radius:50%;background:{BAD};color:#fff;font:900 22px/44px Inter;text-align:center;opacity:0}}
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
    {"".join(f'<div class="pared-luz" style="left:{x - 450}px"></div><div class="plato" style="left:{x - 380}px;top:1625px"></div>' for x in ST.values())}
    <div id="rodapie"></div><div id="suelo"></div>
    {"".join(MOTAS)}
    {"".join(H)}
  </div>
  </div></div>
  {"".join(HUD)}{"".join(OVER)}
  <div id="marca">@mundo.supuesto</div>
  <div id="vineta"></div><div id="sombra-subs"></div><div id="dip"></div><svg id="grano" width="1080" height="1920"><filter id="gr"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7"/><feColorMatrix values="0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0.9 0"/></filter><rect width="1080" height="1920" filter="url(#gr)"/></svg>
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

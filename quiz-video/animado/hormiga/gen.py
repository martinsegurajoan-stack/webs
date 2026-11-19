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
WORLD_W, WORLD_H = 16000, 1920
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
            g.append(f'<path id="{pid}-fringe" d="{fringe_path(2)}" fill="url(#{pid}-hair)"/>')
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

# ---------------------------------------------------------------- ESCENAS «del tamaño de una hormiga» (todo ~580 veces más grande)
ZW = 1700
OVER = []
def ZL(k):
    return k * ZW + (1800 if k >= 6 else 0)

def zona(k, cuerpo, w=ZW, h=1920, top=0):
    return (f'<svg style="position:absolute;left:{ZL(k)}px;top:{top}px;overflow:visible" width="{w}" height="{h}" viewBox="0 {top} {w} {h}">{cuerpo}</svg>')

def caminar(pid, t, desde=-420, dur=1.3, pasos=4):
    J(f'tl.fromTo("#{pid}", {{x:{desde}}}, {{x:0, duration:{dur}, ease:"power1.out", immediateRender:false}}, {t:.2f});')
    for k in range(pasos):
        tk = t + k * dur / pasos
        pie = "legL" if k % 2 == 0 else "legR"
        J(f'tl.to("#{pid}-{pie}", {{y:-26, duration:{dur / pasos / 2:.3f}, yoyo:true, repeat:1, ease:"sine.inOut"}}, {tk:.2f});')
        J(f'tl.to("#{pid}-up", {{y:-8, duration:{dur / pasos / 2:.3f}, yoyo:true, repeat:1, ease:"sine.inOut"}}, {tk:.2f});')

def brazo(pid, lado, rot, t, hold, ida=0.35):
    org = "356 985" if lado == "L" else "644 985"
    J(f'tl.to("#{pid}-arm{lado}g", {{rotation:{rot}, duration:{ida}, ease:"back.out(1.4)", svgOrigin:"{org}"}}, {t:.2f});')
    J(f'tl.to("#{pid}-arm{lado}g", {{rotation:0, duration:0.45, ease:"power2.inOut", svgOrigin:"{org}"}}, {t + hold:.2f});')

def acaro(aid, x, y, s=1.0):
    patas = "".join(f'<path d="M{dx * 40},{10 + abs(dx) * 4} q{dx * 40},-30 {dx * 70},30" stroke="#8a7a66" stroke-width="9" fill="none" stroke-linecap="round"/>'
                    for dx in (-1, -0.6, 0.6, 1))
    pelos = "".join(f'<path d="M{random.uniform(-70, 70):.0f},{random.uniform(-60, 10):.0f} l{random.uniform(-14, 14):.0f},-22" stroke="#b9a88f" stroke-width="4" stroke-linecap="round"/>' for _ in range(14))
    return (f'<svg id="{aid}" style="position:absolute;left:{x}px;top:{y}px;overflow:visible" width="10" height="10"><g transform="scale({s})">'
            f'<g class="patas">{patas}</g><ellipse cx="0" cy="-10" rx="90" ry="70" fill="#d9cbb3"/><ellipse cx="-20" cy="-35" rx="40" ry="22" fill="#efe4d0"/>{pelos}'
            f'<circle cx="-28" cy="-6" r="9" fill="#1d1b26"/><circle cx="22" cy="-6" r="9" fill="#1d1b26"/></g></svg>')

DEFS2 = ('<svg width="0" height="0" style="position:absolute"><defs>'
         '<linearGradient id="sabana" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f7fc"/><stop offset="1" stop-color="#c9d6ea"/></linearGradient>'
         '<linearGradient id="madera" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c58a5c"/><stop offset="1" stop-color="#8a5a3c"/></linearGradient>'
         '<linearGradient id="nocheG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1d2356"/><stop offset="1" stop-color="#3b3f7a"/></linearGradient>'
         '<radialGradient id="gotaG" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#ffffff" stop-opacity="0.75"/><stop offset="0.4" stop-color="#bfe6ff" stop-opacity="0.45"/><stop offset="1" stop-color="#5aa9e6" stop-opacity="0.55"/></radialGradient>'
         '<radialGradient id="migaG" cx="0.4" cy="0.35" r="0.8"><stop offset="0" stop-color="#f7d79a"/><stop offset="1" stop-color="#c58a3c"/></radialGradient>'
         '</defs></svg>')
H.append(DEFS2)
exec(open(os.path.join(BASE, 'decor_cine.py'), encoding='utf-8').read())

# ---- Z0 · SÁBANAS (despertador gigante al fondo)
dunas = "".join(f'<path d="M-100,{y} C300,{y - 90} 600,{y + 60} 900,{y - 40} C1200,{y - 120} 1500,{y + 40} 1800,{y - 30} L1800,2300 L-100,2300 Z" fill="url(#sabana)" opacity="{op}"/>'
                for y, op in ((1450, 0.7), (1600, 0.85), (1720, 1)))
H.append(zona(0, '<rect x="-100" y="0" width="1900" height="1920" fill="#f6dcc6"/>'
              '<rect x="-100" y="0" width="1900" height="1920" fill="url(#luzsala)" opacity="0.6"/>'
              # almohada gigante al fondo
              '<path d="M-150,1250 C-100,850 300,760 800,790 C1300,820 1700,900 1850,1280 Z" fill="#ffffff" opacity="0.95"/><path d="M-150,1250 C300,1180 1300,1180 1850,1280" stroke="#d9e2ef" stroke-width="18" fill="none"/>'
              # despertador gigante (las 8 de la mañana)
              '<circle cx="1330" cy="430" r="330" fill="#e5484d"/><circle cx="1330" cy="430" r="275" fill="#fbf8f2"/>'
              + "".join(f'<line x1="{1330 + 240 * math.cos(a * math.pi / 6):.0f}" y1="{430 + 240 * math.sin(a * math.pi / 6):.0f}" x2="{1330 + 210 * math.cos(a * math.pi / 6):.0f}" y2="{430 + 210 * math.sin(a * math.pi / 6):.0f}" stroke="#3d405b" stroke-width="12"/>' for a in range(12))
              + '<line x1="1330" y1="430" x2="1196" y2="507" stroke="#1d2b33" stroke-width="22" stroke-linecap="round"/><line x1="1330" y1="430" x2="1330" y2="210" stroke="#1d2b33" stroke-width="14" stroke-linecap="round"/>'
              '<circle cx="1110" cy="120" r="80" fill="#e5484d"/><circle cx="1550" cy="120" r="80" fill="#e5484d"/>' + dunas))
H.append(ZONAS_FONDO[0])
H.append(motas(0, y0=-200 if 0 == 5 else 300))
H.append(pj_at("p0", ZL(0) + 650, cm=7))
# regla gigante: 1 mm = 370 px → mides 3 mm
regla = "".join(f'<line x1="0" y1="{-k * 370:.0f}" x2="{70 if k == int(k) else 38}" y2="{-k * 370:.0f}" stroke="#3a3324" stroke-width="{7 if k == int(k) else 4}"/>' for k in [i / 2 for i in range(0, 7)])
regla += "".join(f'<text x="86" y="{-k * 370 + 14:.0f}" font-family="Inter" font-weight="900" font-size="46" fill="#3a3324">{k} mm</text>' for k in range(4))
H.append(f'<svg id="regla" style="position:absolute;left:{ZL(0) + 920}px;top:1700px;overflow:visible" width="10" height="10">'
         f'<rect x="0" y="-1180" width="230" height="1200" rx="14" fill="#f2d27a"/>{regla}</svg>')

# ---- Z1 · PASILLO (rendijas del parqué como cañones, la puerta de la cocina a lo lejos)
H.append(zona(1, '<rect x="0" y="0" width="1700" height="1920" fill="#e9d8c4"/>'
              '<rect x="0" y="0" width="1700" height="1920" fill="url(#luzsala)" opacity="0.5"/>'
              # puerta de la cocina, enorme y lejos, con luz
              '<rect x="980" y="120" width="560" height="1300" fill="#fbf6ee"/><rect x="1020" y="160" width="480" height="1260" fill="#fff4cf"/>'
              '<rect x="1060" y="200" width="400" height="300" fill="#ffe9a8" opacity="0.8"/><circle cx="1260" cy="760" r="20" fill="#e2c27a"/>'
              # suelo de parqué: tablas y rendijas
              '<rect x="0" y="1420" width="1700" height="900" fill="url(#madera)"/>'
              + "".join(f'<path d="M0,{y} L1700,{y + 30}" stroke="#5e3a26" stroke-width="{w}" opacity="0.8"/>' for y, w in ((1500, 10), (1610, 14), (1760, 26)))
              + '<path d="M300,1420 L260,1920" stroke="#5e3a26" stroke-width="12" opacity="0.6"/><path d="M1200,1420 L1260,1920" stroke="#5e3a26" stroke-width="12" opacity="0.6"/>'
              # cartel de distancia
              '<rect x="420" y="1080" width="24" height="340" fill="#8a5a3c"/><rect x="340" y="1000" width="430" height="110" rx="16" fill="#3d405b"/>'
              '<text x="555" y="1072" text-anchor="middle" font-family="Inter" font-weight="900" font-size="54" fill="#f2b84b">COCINA · 5,8 km</text>'
              # bolas de polvo
              + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 0.7:.0f}" fill="#cfc6b8" opacity="0.85"/>' for x, y, r in ((560, 1380, 120), (1420, 1460, 90), (820, 1330, 70)))))
H.append(ZONAS_FONDO[1])
H.append(motas(1, y0=-200 if 1 == 5 else 300))
H.append(pj_at("p1", ZL(1) + 650, cm=7))
H.append(acaro("acaro1", ZL(1) + 1250, 1600, 1.7))
H.append(acaro("acaro2", ZL(1) + 260, 1660, 1.3))

# ---- Z2 · LA MESA (columna vertical: encima el grano de arroz, abajo el suelo)
H.append(zona(2, '<rect x="0" y="-200" width="1700" height="4400" fill="#efe2d0"/>'
              '<rect x="0" y="-200" width="1700" height="4400" fill="url(#luzsala)" opacity="0.5"/>'
              '<rect x="0" y="1700" width="1250" height="90" fill="url(#madera)"/><rect x="0" y="1690" width="1250" height="20" fill="#d9a77e"/>'
              '<rect x="1000" y="1790" width="160" height="2010" fill="#a8714c"/><rect x="1000" y="1790" width="40" height="2010" fill="#c58a5c"/>'
              '<rect x="-100" y="3800" width="1900" height="1600" fill="#9c6c4c"/><rect x="-100" y="3800" width="1900" height="1600" fill="url(#veta)"/>'
              # terrón de azúcar
              '<rect x="80" y="1150" width="520" height="550" rx="30" fill="#ffffff"/><rect x="80" y="1150" width="520" height="80" rx="30" fill="#eef3fb"/>'
              + "".join(f'<rect x="{x}" y="{y}" width="60" height="60" fill="#e7edf7"/>' for x, y in ((150, 1300), (380, 1420), (260, 1560), (470, 1270)))
              + '', h=4400, top=-200))
H.append(ZONAS_FONDO[2])
H.append(motas(2, y0=-200 if 2 == 5 else 300))
H.append(pj_at("p2", ZL(2) + 850, cm=7))
H.append(f'<svg id="arroz" style="position:absolute;left:{ZL(2) + 850}px;top:1700px;overflow:visible" width="10" height="10">'
         '<g transform="rotate(-8 0 -150)"><path d="M-300,-150 C-300,-260 -120,-290 60,-280 C220,-270 320,-220 310,-150 C300,-80 160,-50 0,-50 C-170,-50 -300,-70 -300,-150 Z" fill="#f6efdc" stroke="#d9cba6" stroke-width="12"/>'
         '<path d="M-220,-200 C-100,-240 100,-245 230,-205" stroke="#ffffff" stroke-width="22" stroke-linecap="round" fill="none" opacity="0.9"/>'
         '<path d="M-150,-120 C-40,-100 80,-100 200,-125" stroke="#e3d6b4" stroke-width="10" stroke-linecap="round" fill="none"/>'
         '<path d="M290,-170 C320,-160 330,-140 315,-120" stroke="#cbb98d" stroke-width="10" fill="none"/></g>'
         '<text x="0" y="-330" text-anchor="middle" font-family="Inter" font-weight="900" font-size="64" fill="#3d405b" opacity="0" id="arrozT">🍚 1 grano de arroz</text></svg>')
H.append(f'<svg id="aire" style="position:absolute;left:{ZL(2) + 1350}px;top:2400px;overflow:visible;opacity:0" width="10" height="10">'
         + "".join(f'<path d="M{dx},0 L{dx},-220" stroke="#ffffff" stroke-width="10" stroke-linecap="round" stroke-dasharray="40 30" opacity="0.8"/>' for dx in (-160, -60, 60, 160)) + '</svg>')

# ---- Z3 · SUELO DE LA COCINA (miga de pan gigante, granos de azúcar)
baldosas = "".join(f'<rect x="{x}" y="1420" width="850" height="900" fill="{c}"/>' for x, c in ((0, "#f1ece2"), (850, "#e3dccd")))
H.append(zona(3, '<rect x="0" y="0" width="1700" height="1420" fill="#dfe7ee"/>'
              '<rect x="0" y="0" width="1700" height="1420" fill="url(#luzsala)" opacity="0.5"/>'
              '<rect x="0" y="980" width="1700" height="440" fill="#fbf8f2"/><rect x="0" y="980" width="1700" height="30" fill="#c9d0dc"/>'
              '<rect x="200" y="1300" width="160" height="120" rx="20" fill="#7c8496"/><rect x="1300" y="1300" width="160" height="120" rx="20" fill="#7c8496"/>'
              + baldosas + '<rect x="840" y="1420" width="20" height="900" fill="#c9bfae"/>'
              + "".join(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="10" fill="#ffffff" opacity="0.95" transform="rotate({r} {x + s / 2} {y + s / 2})"/>' for x, y, s, r in ((120, 1620, 110, 12), (1450, 1660, 90, -18), (1300, 1560, 70, 30)))))
H.append(f'<svg id="miga" style="position:absolute;left:{ZL(3) + 1060}px;top:1720px;overflow:visible" width="10" height="10">'
         '<path d="M-330,0 C-360,-260 -200,-470 20,-480 C260,-490 380,-300 350,-80 L330,0 Z" fill="url(#migaG)"/>'
         + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 0.7:.0f}" fill="#b37a34" opacity="0.6"/>' for x, y, r in ((-150, -300, 40), (60, -380, 30), (180, -200, 46), (-60, -150, 34), (-230, -90, 26), (250, -330, 22)))
         + '</svg>')
H.append(f'<svg id="vaho" style="position:absolute;left:{ZL(3) + 560}px;top:700px;overflow:visible;opacity:0" width="10" height="10">'
         + "".join(f'<circle class="vh" cx="{30 + i * 40}" cy="{-i * 35}" r="{26 + i * 8}" fill="#ffffff" opacity="0.7"/>' for i in range(3)) + '</svg>')
H.append(f'<div id="termo" class="card" style="left:{ZL(3) + 820}px;top:470px;width:300px;padding:20px 24px"><div class="card-top" style="font-size:26px">TU CUERPO</div>'
         f'<div style="display:flex;align-items:center;gap:16px;margin-top:10px"><svg width="60" height="150" viewBox="0 0 60 150"><rect x="18" y="0" width="24" height="110" rx="12" fill="#e6edf5"/>'
         f'<rect id="mercurio" x="22" y="10" width="16" height="100" rx="8" fill="{BAD}"/><circle cx="30" cy="122" r="26" fill="{BAD}"/></svg>'
         f'<div style="font:900 40px Inter;color:#5aa9e6;line-height:1.1">PIERDE<br>CALOR</div></div></div>')
H.append(ZONAS_FONDO[3])
H.append(motas(3, y0=-200 if 3 == 5 else 300))
H.append(pj_at("p3", ZL(3) + 600, cm=7))

# ---- Z4 · ENCIMERA Y GRIFO (la gota que atrapa)
H.append(zona(4, '<rect x="0" y="0" width="1700" height="1920" fill="#dfe9f0"/>'
              '<rect x="0" y="0" width="1700" height="1920" fill="url(#luzsala)" opacity="0.5"/>'
              # grifo gigante arriba
              '<rect x="560" y="-200" width="260" height="560" rx="40" fill="#b9c3cf"/><path d="M560,320 C560,520 760,560 980,560 L980,700 C700,700 420,640 420,320 Z" fill="#c9d3df"/>'
              '<rect x="940" y="520" width="120" height="200" rx="20" fill="#9aa7b6"/>'
              # encimera de mármol
              '<rect x="-100" y="1700" width="1900" height="500" fill="#f4f1ec"/>'
              + "".join(f'<path d="M{x},1720 C{x + 120},1800 {x + 60},1900 {x + 200},2000" stroke="#c9c2b6" stroke-width="5" fill="none"/>' for x in (100, 700, 1300))))
H.append(ZONAS_FONDO[4])
H.append(pj_at("p4", ZL(4) + 1000, cm=7))
H.append(f'<svg id="gota" style="position:absolute;left:{ZL(4) + 1000}px;top:700px;overflow:visible" width="10" height="10">'
         '<g id="gota-g"><path d="M0,-150 C80,-40 150,80 150,170 C150,260 80,320 0,320 C-80,320 -150,260 -150,170 C-150,80 -80,-40 0,-150 Z" fill="url(#gotaG)" stroke="#9fd3f5" stroke-width="6"/>'
         '<ellipse cx="-55" cy="120" rx="30" ry="50" fill="#ffffff" opacity="0.7"/></g></svg>')
H.append(f'<svg id="charco" style="position:absolute;left:{ZL(4) + 1000}px;top:1700px;overflow:visible;opacity:0" width="10" height="10">'
         '<path d="M-480,0 C-480,-760 -300,-1150 0,-1150 C300,-1150 480,-760 480,0 Z" fill="url(#gotaG)" stroke="#9fd3f5" stroke-width="8"/>'
         '<ellipse cx="-230" cy="-850" rx="70" ry="130" fill="#ffffff" opacity="0.6"/></svg>')

# ---- Z5 · SALÓN: alfombra, el gato gigante y el sofá
fibras = "".join(f'<path d="M{x},{1920} C{x + random.uniform(-20, 20):.0f},{1800} {x + random.uniform(-40, 40):.0f},{1700} {x + random.uniform(-30, 30):.0f},{random.uniform(1560, 1660):.0f}" stroke="{random.choice(["#b7604a", "#c56f55", "#a85540"])}" stroke-width="{random.uniform(14, 22):.0f}" fill="none" stroke-linecap="round"/>'
                 for x in range(-60, 3500, 38))
H.append(zona(5, '<rect x="0" y="-2600" width="3400" height="4600" fill="#e8d6c0"/>'
              '<rect x="0" y="-2600" width="3400" height="4600" fill="url(#luzsala)" opacity="0.4"/>'
              # bajos del sofá a la derecha: cueva oscura con flecos, moneda y pieza de construcción
              '<rect x="1900" y="400" width="1500" height="300" fill="#5b86c4"/>' + "".join(f'<rect x="{1900 + i * 50}" y="690" width="26" height="{120 + (i % 3) * 30}" fill="#4a6fa5"/>' for i in range(30))
              + '<rect x="1900" y="820" width="1500" height="1100" fill="#2a2440"/><ellipse cx="2650" cy="1700" rx="700" ry="90" fill="#1d1830"/>'
              '<circle cx="3000" cy="1440" r="250" fill="#e2c27a"/><circle cx="3000" cy="1440" r="190" fill="#d4ad5c"/><text x="3000" y="1500" text-anchor="middle" font-family="Inter" font-weight="900" font-size="170" fill="#b8913f">1</text>'
              '<rect x="2150" y="1330" width="380" height="250" rx="16" fill="#e5484d"/>' + "".join(f'<rect x="{2180 + i * 120}" y="1270" width="80" height="70" rx="12" fill="#e5484d"/>' for i in range(3))
              + '<ellipse cx="2600" cy="1560" rx="120" ry="80" fill="#8f8a9a" opacity="0.7"/>'
              + fibras, w=3400, h=4600, top=-2600))
H.append(ZONAS_FONDO[5])
H.append(motas(5, y0=-200 if 5 == 5 else 300))
H.append(pj_at("p5", ZL(5) + 700, cm=7))
# el gato: cabeza enorme asomando por arriba y pata que baja
H.append(f'''<svg id="gato" style="position:absolute;left:{ZL(5) + 500}px;top:-2300px;overflow:visible" width="10" height="10">
<path d="M-900,700 L-700,-200 L-380,300 Z M900,700 L700,-200 L380,300 Z" fill="#e8a046"/>
<path d="M-820,560 L-700,40 L-500,340 Z M820,560 L700,40 L500,340 Z" fill="#f6c1a6"/>
<ellipse cx="0" cy="900" rx="1000" ry="820" fill="#f2b05a"/>
<path d="M-300,420 C-200,520 -100,520 0,420 M300,420 C200,520 100,520 0,420" stroke="#d98b35" stroke-width="40" fill="none"/>
<ellipse cx="-360" cy="820" rx="150" ry="180" fill="#c6e36a"/><ellipse cx="360" cy="820" rx="150" ry="180" fill="#c6e36a"/>
<ellipse id="pupila1" cx="-360" cy="820" rx="34" ry="150" fill="#1d1b26"/><ellipse id="pupila2" cx="360" cy="820" rx="34" ry="150" fill="#1d1b26"/>
<path d="M-70,1060 L70,1060 L0,1130 Z" fill="#e57a8a"/>
<path d="M-120,1220 C-60,1270 0,1230 0,1170 C0,1230 60,1270 120,1220" stroke="#8a4e2c" stroke-width="18" fill="none"/>
{"".join(f'<path d="M{s * 160},{1120 + k * 50} L{s * 900},{1040 + k * 90}" stroke="#fbf8f2" stroke-width="10"/>' for s in (-1, 1) for k in range(3))}
</svg>''')
H.append(f'<svg id="pata" style="position:absolute;left:{ZL(5) + 1250}px;top:-1400px;overflow:visible" width="10" height="10">'
         '<rect x="-230" y="-1200" width="460" height="2200" rx="220" fill="#f2b05a"/><ellipse cx="0" cy="1000" rx="300" ry="200" fill="#f2b05a"/>'
         + "".join(f'<ellipse cx="{dx}" cy="1110" rx="60" ry="46" fill="#f6c1a6"/>' for dx in (-170, -55, 60, 175)) + '</svg>')
H.append(f'<div id="edificio" class="badge" style="left:{ZL(5) - 60}px;top:330px;background:#3d405b;font-size:110px;padding:30px 60px">🏢 50 PISOS</div>')

# ---- Z6 · NOCHE: el reloj de pared gigante
H.append(zona(6, '<rect x="0" y="0" width="1700" height="1920" fill="url(#nocheG)"/>'
              + "".join(f'<rect x="{x}" y="0" width="26" height="1920" fill="#ffffff" opacity="0.03"/>' for x in range(20, 1700, 70))
              + '<circle cx="850" cy="900" r="640" fill="#3d405b"/><circle cx="850" cy="900" r="580" fill="#fbf8f2"/>'
              + "".join(f'<line x1="{850 + 520 * math.cos(a * math.pi / 6):.0f}" y1="{900 + 520 * math.sin(a * math.pi / 6):.0f}" x2="{850 + 460 * math.cos(a * math.pi / 6):.0f}" y2="{900 + 460 * math.sin(a * math.pi / 6):.0f}" stroke="#3d405b" stroke-width="22"/>' for a in range(12))
              + '<text x="850" y="450" text-anchor="middle" font-family="Inter" font-weight="900" font-size="110" fill="#3d405b">12</text>'
              '<line id="rh" x1="850" y1="900" x2="850" y2="620" stroke="#1d2b33" stroke-width="40" stroke-linecap="round"/>'
              '<line id="rm" x1="850" y1="900" x2="850" y2="440" stroke="#e5484d" stroke-width="24" stroke-linecap="round"/>'
              '<circle cx="850" cy="900" r="40" fill="#1d2b33"/>'
              + "".join(f'<circle cx="{random.uniform(0, 1700):.0f}" cy="{random.uniform(0, 300):.0f}" r="3" fill="#fff" opacity="0.6"/>' for _ in range(20))))
H.append(ZONAS_FONDO[6])
H.append(motas(6, y0=-200 if 6 == 5 else 300))
H.append(f'<svg id="destello" style="position:absolute;left:{ZL(6) + 850}px;top:900px;overflow:visible;opacity:0" width="10" height="10">'
         '<defs><radialGradient id="glowR"><stop offset="0" stop-color="#fff6c9" stop-opacity="0.85"/><stop offset="0.45" stop-color="#ffe08a" stop-opacity="0.35"/><stop offset="1" stop-color="#ffe08a" stop-opacity="0"/></radialGradient></defs>'
         '<circle r="700" fill="url(#glowR)"/><circle r="560" fill="none" stroke="#fff6c9" stroke-width="10" opacity="0.5"/></svg>')

# ---- Z7 · DORMITORIO a tamaño normal (de noche) y una hormiga de verdad en el suelo
L7 = ZL(7)
H.append(f'<svg style="position:absolute;left:{L7}px;top:0;overflow:visible" width="1500" height="1920" viewBox="0 0 1500 1920">'
         + pared_suelo("s7", "#c9b3c9", "#a990ad", "#8a5a3c", "#6e4a33") + ventana(940, 420, 330, 470, noche=True, cortina="#4a5a85")
         + cuadro(230, 520, 230, 230) + reloj("clk7", 640, 640) + lampara_mesita(40) + '</svg>')
H.append(f'<svg style="position:absolute;left:{L7}px;top:0;overflow:visible" width="1" height="1">'
         '<rect x="215" y="1080" width="38" height="620" rx="18" fill="#8a5a3c"/><rect x="230" y="1450" width="760" height="70" rx="16" fill="#f4efe6"/>'
         '<rect x="230" y="1520" width="760" height="30" fill="#7a4e33"/><rect x="960" y="1400" width="34" height="300" rx="14" fill="#8a5a3c"/>'
         '<ellipse cx="330" cy="1420" rx="110" ry="44" fill="#ffffff"/><path d="M420,1400 C600,1380 800,1385 960,1410 L960,1470 L420,1470 Z" fill="url(#manta)"/></svg>')
H.append(ZONAS_FONDO[7])
H.append(pj_at("p6", L7 + 1150, cm=7))
H.append(f'<svg id="hormiga" style="position:absolute;left:{L7 + 760}px;top:1760px;overflow:visible" width="10" height="10">'
         '<ellipse cx="0" cy="0" rx="9" ry="7" fill="#1d1b26"/><ellipse cx="14" cy="-1" rx="6" ry="5" fill="#1d1b26"/><ellipse cx="-14" cy="0" rx="11" ry="8" fill="#1d1b26"/>'
         '<path d="M-6,4 l-8,9 M2,5 l0,10 M8,4 l8,9 M-6,-4 l-8,-9 M2,-5 l0,-10 M8,-4 l8,-9" stroke="#1d1b26" stroke-width="2"/></svg>')

for k in range(8):
    if ZONAS_CERCA.get(k):
        H.append(ZONAS_CERCA[k])
# ------------------------------------------------------------------ guion → animación (todo con P())
for pid in ("p0", "p1", "p2", "p3", "p4", "p5", "p6"):
    vida(pid)
COLORES_T = ["#f2b84b", "#7b7fc4", "#e07a5f", "#3fbf7f", "#5aa9e6", "#c56f55", "#f2b84b", "#7b7fc4"]
NT = [0]
def transicion(t, x, y, z):
    """Transición decorativa: un círculo de color con anillos se abre desde el centro, cambia el plano y se cierra.
    Con un whoosh suave y una campanita bajita."""
    c = COLORES_T[NT[0] % len(COLORES_T)]; NT[0] += 1
    J(f'tl.set("#iris", {{background:"radial-gradient(circle, {c} 0%, {c} 58%, #fbf8f2 59%, #fbf8f2 61%, {c} 62%, {c} 100%)"}}, {t - 0.45:.2f});')
    J(f'tl.fromTo("#iris", {{scale:0, rotation:-30}}, {{scale:1, rotation:0, duration:0.42, ease:"power2.in", immediateRender:false}}, {t - 0.42:.2f});')
    J(f'tl.set("#world", {{x:{540 - x * z:.1f}, y:{960 - y * z:.1f}, scale:{z}}}, {t:.2f}); tl.set("#lejos", {{x:{(540 - x * z) * 0.35:.1f}}}, {t:.2f});')
    J(f'tl.to("#iris", {{scale:0, rotation:30, duration:0.42, ease:"power2.out"}}, {t + 0.04:.2f});')
    FX_EV.append(("suave", t - 0.42))

# 1-3 · despiertas diminuto en la cama
J('tl.set("#iris", {scale:0}, 0); tl.set("#regla", {y:2600}, 0); tl.set("#arroz", {x:-430, y:0}, 0);')
X0, Y0, Z0 = ZL(0) + 700, 1150, 0.95
J(f'tl.set("#world", {{x:{540 - X0 * 1.2:.1f}, y:{960 - 1050 * 1.2:.1f}, scale:1.2}}, 0);')
J(f'tl.set("#p0-eyes", {{scaleY:1.3, svgOrigin:"500 742"}}, 0); tl.set("#p0-mouthO", {{opacity:1}}, 0); tl.set("#p0-mouth", {{opacity:0}}, 0);')
J(f'tl.to("#p0-eyes", {{scaleY:1, duration:0.3, svgOrigin:"500 742"}}, {FE(1):.2f}); tl.to("#p0-mouthO", {{opacity:0, duration:0.2}}, {FE(1):.2f}); tl.to("#p0-mouth", {{opacity:1, duration:0.2}}, {FE(1):.2f});')
tmm = P("milimetros")
J(f'tl.fromTo("#regla", {{y:2600}}, {{y:0, duration:0.8, ease:"power3.out", immediateRender:false}}, {P("mides") - 0.2:.2f});')
FX_EV.append(("suave", P("mides") - 0.2))
cam(P("mides") - 0.3, ZL(0) + 800, 1150, 0.9, dur=0.9)
J(f'tl.to("#p0-head", {{rotation:-8, duration:0.4, yoyo:true, repeat:1, repeatDelay:0.6, svgOrigin:"500 900"}}, {tmm:.2f});')
J(f'tl.to("#regla", {{y:1500, duration:0.5, ease:"power2.in"}}, {F(3) - 0.1:.2f});')
cam(F(3), ZL(0) + 850, 1250, 0.72, dur=1.6, ease="sine.inOut")
J(f'tl.to("#p0-eyes", {{x:-8, duration:0.3, yoyo:true, repeat:1, repeatDelay:0.5}}, {F(3) + 0.3:.2f});')

# 4-6 · el pasillo: casi 6 km y los ácaros
t = F(4)
transicion(t, ZL(1) + 850, 1150, 0.9)
caminar("p1", t, desde=-500, dur=2.6, pasos=8)
cam(t + 0.2, ZL(1) + 900, 1100, 0.82, dur=2.6, ease="sine.inOut")
tpo = P("polvo")
J(f'tl.fromTo("#acaro1", {{x:300, opacity:0}}, {{x:0, opacity:1, duration:1.4, ease:"power2.out", immediateRender:false}}, {tpo:.2f});')
J(f'tl.fromTo("#acaro2", {{x:-260, opacity:0}}, {{x:0, opacity:1, duration:1.6, ease:"power2.out", immediateRender:false}}, {tpo + 0.3:.2f});')
J(f'tl.to("#acaro1 .patas, #acaro2 .patas", {{y:-6, duration:0.12, yoyo:true, repeat:20, ease:"sine.inOut"}}, {tpo:.2f});')
J(f'tl.to("#p1-eyes", {{scaleY:1.3, duration:0.2, svgOrigin:"500 742"}}, {P("acaros"):.2f}); tl.to("#p1-mouth", {{attr:{{d:"M482,826 Q500,812 518,826"}}, duration:0.2}}, {P("acaros"):.2f});')
cam(P("acaros") - 0.2, ZL(1) + 850, 1250, 0.95, dur=0.8)

# 7-9 · eres fortísimo (grano de arroz) y caes de la mesa sin hacerte daño
t = F(7)
transicion(t, ZL(2) + 700, 1200, 0.9)
tpe = P("peso")
J(f'tl.to("#p2-armLg", {{rotation:150, duration:0.4, ease:"back.out(1.4)", svgOrigin:"356 985"}}, {tpe - 0.5:.2f}); tl.to("#p2-armRg", {{rotation:-150, duration:0.4, ease:"back.out(1.4)", svgOrigin:"644 985"}}, {tpe - 0.5:.2f});')
J(f'tl.to("#arroz", {{x:0, y:-1080, duration:0.6, ease:"back.out(1.5)"}}, {tpe - 0.5:.2f}); tl.fromTo("#arrozT", {{opacity:0}}, {{opacity:1, duration:0.3, immediateRender:false}}, {P("levantar"):.2f}); tl.to("#arrozT", {{opacity:0, duration:0.2}}, {tpe - 0.6:.2f});')
J(f'tl.to("#p2-mouth", {{attr:{{d:"M474,814 Q500,840 526,814"}}, duration:0.3}}, {tpe:.2f});')
FX_EV.append(("pop", tpe - 0.2))
tme = P("mesa")
J(f'tl.to("#arroz", {{y:0, x:-450, duration:0.5, ease:"power2.in"}}, {tme - 0.9:.2f}); tl.to(["#p2-armLg", "#p2-armRg"], {{rotation:0, duration:0.35}}, {tme - 0.9:.2f});')
J(f'tl.to("#p2", {{x:500, duration:0.6, ease:"power1.in"}}, {tme - 0.6:.2f});')
J(f'tl.to("#p2", {{y:2100, rotation:20, duration:2.4, ease:"sine.inOut", transformOrigin:"50% 70%"}}, {tme:.2f});')
J(f'tl.to("#aire", {{opacity:1, duration:0.3}}, {tme + 0.3:.2f}); tl.to("#aire", {{y:1500, duration:2.0, ease:"sine.inOut"}}, {tme + 0.2:.2f}); tl.to("#aire", {{opacity:0, duration:0.3}}, {tme + 2.3:.2f});')
cam(tme - 0.2, ZL(2) + 1250, 3000, 0.62, dur=2.6, ease="sine.inOut")
J(f'tl.to("#p2", {{rotation:0, duration:0.3}}, {tme + 2.4:.2f});')
FX_EV.append(("whoosh", tme))

# 10-12 · la cocina: miga gigante, frío y comer sin parar
t = F(10)
transicion(t, ZL(3) + 850, 1150, 0.9)
J(f'tl.fromTo("#miga", {{scale:0.6, opacity:0}}, {{scale:1, opacity:1, duration:0.6, ease:"back.out(1.6)", transformOrigin:"50% 100%", immediateRender:false}}, {P("miga") - 0.1:.2f});')
FX_EV.append(("pop", P("miga")))
tfr = P("frio")
pop("#termo", tfr)
J(f'tl.fromTo("#mercurio", {{scaleY:1}}, {{scaleY:0.35, duration:1.6, ease:"power2.inOut", transformOrigin:"50% 100%", immediateRender:false}}, {tfr + 0.3:.2f});')
J(f'tl.to("#p3", {{x:6, duration:0.06, yoyo:true, repeat:30, ease:"none"}}, {tfr:.2f});')
J(f'tl.to("#vaho", {{opacity:1, duration:0.2}}, {tfr + 0.2:.2f}); tl.fromTo("#vaho .vh", {{scale:0.3, opacity:0.9}}, {{scale:1.4, opacity:0, y:-60, duration:1.2, stagger:0.25, repeat:2, transformOrigin:"50% 50%", immediateRender:false}}, {tfr + 0.2:.2f});')
tco = P("comer")
J(f'tl.to("#termo", {{opacity:0, duration:0.3}}, {tco - 0.4:.2f}); tl.to("#vaho", {{opacity:0, duration:0.3}}, {tco - 0.4:.2f});')
J(f'tl.to("#p3", {{x:220, duration:0.6, ease:"power2.out"}}, {tco - 0.3:.2f});')
J(f'tl.to("#p3-armRg", {{rotation:-120, duration:0.25, yoyo:true, repeat:5, ease:"sine.inOut", svgOrigin:"644 985"}}, {tco + 0.3:.2f});')
J(f'tl.to("#miga", {{scale:0.8, duration:1.6, ease:"steps(5)", transformOrigin:"100% 100%"}}, {tco + 0.3:.2f});')

# 13 · la gota del grifo que atrapa como pegamento
t = F(13)
transicion(t, ZL(4) + 900, 1100, 0.85)
tgo = P("gota")
J(f'tl.fromTo("#gota", {{y:0, scaleY:1}}, {{y:780, duration:0.55, ease:"power2.in", immediateRender:false}}, {tgo:.2f});')
J(f'tl.to("#gota", {{opacity:0, duration:0.05}}, {tgo + 0.55:.2f}); tl.fromTo("#charco", {{opacity:0, scaleY:0.2}}, {{opacity:1, scaleY:1, duration:0.4, ease:"back.out(1.6)", transformOrigin:"50% 100%", immediateRender:false}}, {tgo + 0.55:.2f});')
FX_EV.append(("pop", tgo + 0.55))
J(f'tl.to("#p4-armLg", {{rotation:70, duration:0.3, yoyo:true, repeat:5, svgOrigin:"356 985"}}, {tgo + 0.9:.2f}); tl.to("#p4-armRg", {{rotation:-70, duration:0.3, yoyo:true, repeat:5, svgOrigin:"644 985"}}, {tgo + 0.9:.2f});')
J(f'tl.to("#charco", {{scaleX:1.05, scaleY:0.96, duration:0.3, yoyo:true, repeat:5, transformOrigin:"50% 100%"}}, {tgo + 1.0:.2f});')
J(f'tl.to("#p4-mouth", {{attr:{{d:"M482,826 Q500,812 518,826"}}, duration:0.2}}, {tgo + 0.6:.2f});')

# 14-16 · llega el gato (alto como un edificio) y corres bajo el sofá
t = F(14)
transicion(t, ZL(5) + 700, 1150, 0.9)
J(f'tl.fromTo("#gato", {{y:-900}}, {{y:0, duration:1.2, ease:"power2.out", immediateRender:false}}, {P("gato") - 0.3:.2f});')
cam(P("gato") - 0.1, ZL(5) + 700, -400, 0.42, dur=1.4, ease="power2.inOut")
J(f'tl.fromTo("#pata", {{y:-1200}}, {{y:0, duration:1.0, ease:"power2.in", immediateRender:false}}, {P("gato") - 0.2:.2f});')
FX_EV.append(("golpe", P("gato") + 0.8))
J(f'tl.to("#sombragato", {{opacity:1, duration:0.8}}, {P("gato") - 0.2:.2f}); tl.to("#sombragato", {{opacity:0, duration:0.6}}, {P("corres"):.2f});')
J(f'tl.to("#p5-eyes", {{scaleY:1.35, duration:0.15, svgOrigin:"500 742"}}, {P("gato") + 0.8:.2f}); tl.to("#p5-mouthO", {{opacity:1, duration:0.15}}, {P("gato") + 0.8:.2f}); tl.to("#p5-mouth", {{opacity:0, duration:0.15}}, {P("gato") + 0.8:.2f});')
ted = P("edificio")
pop("#edificio", ted)
J(f'tl.to(["#pupila1", "#pupila2"], {{attr:{{rx:70}}, duration:0.4}}, {ted:.2f});')
tso = P("sofa")
cam(P("corres") - 0.3, ZL(5) + 2300, 1150, 0.8, dur=1.2, ease="power2.inOut")
J(f'tl.to("#edificio", {{opacity:0, duration:0.3}}, {P("corres") - 0.3:.2f});')
J(f'tl.to("#p5", {{x:1700, duration:1.6, ease:"power2.in"}}, {P("corres"):.2f});')
for k in range(8):
    J(f'tl.to("#p5-{"legL" if k % 2 == 0 else "legR"}", {{y:-30, duration:0.1, yoyo:true, repeat:1}}, {P("corres") + k * 0.2:.2f});')
J(f'tl.to("#pata", {{y:200, x:600, duration:0.6, ease:"power2.in"}}, {tso:.2f});')
FX_EV.append(("whoosh", P("corres")))

# 17 · medianoche: el reloj marca las doce y vuelves a tu tamaño
t = F(17)
transicion(t, ZL(6) + 850, 950, 0.95)
tdo = P("doce")
J(f'tl.set("#rh", {{rotation:-60, svgOrigin:"850 900"}}, 0); tl.set("#rm", {{rotation:-150, svgOrigin:"850 900"}}, 0);')
J(f'tl.to("#rh", {{rotation:0, duration:{tdo - t - 0.1:.2f}, ease:"power2.inOut", svgOrigin:"850 900"}}, {t + 0.1:.2f}); tl.to("#rm", {{rotation:0, duration:{tdo - t - 0.1:.2f}, ease:"power2.inOut", svgOrigin:"850 900"}}, {t + 0.1:.2f});')
FX_EV.append(("clic", tdo))
J(f'tl.to("#destello", {{opacity:1, duration:0.3}}, {P("tamano", 2) - 0.6:.2f}); tl.fromTo("#destello", {{scale:0.5}}, {{scale:1.3, duration:1.0, ease:"sine.out", immediateRender:false}}, {P("tamano", 2) - 0.6:.2f});')
FX_EV.append(("brillo", P("tamano", 2) - 0.6))
transicion(P("tamano", 2) + 0.3, L7 + 800, 1150, 0.9)

# 18 · tamaño normal… y una hormiga de verdad en el suelo (luego, bucle)
t18 = F(18)
J(f'tl.to("#p6-eyes", {{y:8, duration:0.3}}, {P("suelo") - 0.2:.2f}); tl.to("#p6-headw", {{rotation:-8, duration:0.4, svgOrigin:"500 900"}}, {P("suelo") - 0.2:.2f});')
J(f'tl.fromTo("#hormiga", {{x:-200}}, {{x:200, duration:3.0, ease:"none", immediateRender:false}}, {t18:.2f});')
cam(P("ahi") - 0.2, L7 + 860, 1720, 3.2, dur=1.8, ease="power2.inOut")
tcut = DUR - 0.7
transicion(tcut, ZL(0) + 700, 1050, 1.2)
J(f'tl.set("#p0-eyes", {{scaleY:1.3, svgOrigin:"500 742"}}, {tcut:.2f}); tl.set("#p0-mouthO", {{opacity:1}}, {tcut:.2f}); tl.set("#p0-mouth", {{opacity:0}}, {tcut:.2f});')
J(f'tl.set("#p2", {{x:0, y:0, rotation:0}}, {tcut:.2f}); tl.set("#arroz", {{x:-430, y:0}}, {tcut:.2f});')

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
CLAVE = {"hormiga", "milimetros", "sabanas", "cocina", "kilometros", "acaros", "hamsteres", "fortisimo", "peso", "mesa",
         "frena", "miga", "roca", "frio", "calor", "comer", "gota", "pegamento", "gato", "cincuenta", "pisos", "sofa", "doce",
         "tamano", "suelo", "mundo"}
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
.motaz{{position:absolute;border-radius:50%;filter:blur(1px)}}
#iris{{position:absolute;left:-860px;top:-440px;width:2800px;height:2800px;border-radius:50%;pointer-events:none}}
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
  <div id="iris"></div><div id="vineta"></div><div id="sombra-subs"></div><div id="dip"></div><svg id="grano" width="1080" height="1920"><filter id="gr"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7"/><feColorMatrix values="0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0.9 0"/></filter><rect width="1080" height="1920" filter="url(#gr)"/></svg>
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

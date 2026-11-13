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
                 f'<g id="{pid}-fore{side}"><circle cx="{sx - 25 * rot}" cy="1116" r="18" fill="{SKIN}"/>'
                 f'<path d="M{sx - 42 * rot},1112 C{sx - 46 * rot},1180 {sx - 40 * rot},1240 {sx - 36 * rot},1262 L{sx - 10 * rot},1262 C{sx - 12 * rot},1230 {sx - 10 * rot},1170 {sx - 8 * rot},1112 Z" fill="{SKIN}"/>'
                 f'<circle cx="{sx - 24 * rot}" cy="1280" r="27" fill="{SKIN}"/></g></g></g>')
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
    g.append(f'<path id="{pid}-azul" d="{HEAD_D}" fill="#7cc8ff" opacity="0"/>')
    g.append(f'<g id="{pid}-rubor" opacity="0"><ellipse cx="438" cy="790" rx="26" ry="14" fill="#ff6b6b" opacity="0.6"/><ellipse cx="562" cy="790" rx="26" ry="14" fill="#ff6b6b" opacity="0.6"/></g>')
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
    g.append(f'<g id="{pid}-dientes" opacity="0"><rect x="478" y="810" width="44" height="20" rx="6" fill="#ffffff" stroke="#7a3f35" stroke-width="3"/><path d="M478,820 L522,820 M489,810 L489,830 M500,810 L500,830 M511,810 L511,830" stroke="#7a3f35" stroke-width="2"/></g>')
    g.append(f'<path id="{pid}-sudor" d="M606,690 C616,708 622,720 622,730 C622,742 612,748 604,748 C596,748 588,742 588,730 C588,720 596,708 606,690 Z" fill="#8fd8ff" stroke="#3a9ad9" stroke-width="3" opacity="0"/>')
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
                             (f"{pid}-armL", 4, 15, "356 985"), (f"{pid}-armR", -4, 14, "644 985"),
                             (f"{pid}-foreL", 7, 11, "331 1116"), (f"{pid}-foreR", -7, 12, "669 1116"), (f"{pid}-brows", 1.5, 9, "500 715")):
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

exec(open(os.path.join(BASE, 'escenas2.py'), encoding='utf-8').read())

nA = 6
J(f'tl.fromTo("#camA", {{scale:1}}, {{scale:1.035, duration:{DUR / (2 * nA):.4f}, ease:"sine.inOut", yoyo:true, repeat:{2 * nA - 1}, immediateRender:false}}, 0);')
nR = 5
J(f'tl.fromTo("#camA", {{rotation:0}}, {{rotation:0.7, duration:{DUR / (4 * nR):.4f}, ease:"sine.out", yoyo:true, repeat:1, immediateRender:false}}, 0);')
for k in range(1, nR):
    J(f'tl.to("#camA", {{rotation:{(-0.7 if k % 2 else 0.7)}, duration:{DUR / (2 * nR):.4f}, ease:"sine.inOut"}}, {DUR * (k - 0.5) / nR + DUR / (4 * nR):.3f});')
J(f'tl.to("#camA", {{rotation:0, duration:{DUR / (4 * nR):.4f}, ease:"sine.in"}}, {DUR - DUR / (4 * nR) - 0.02:.3f});')

LEJOS, MOTAS = [], []

# ------------------------------------------------------------------ subtítulos (arriba, palabra a palabra)
CLAVE = {"hormiga", "milimetros", "sabanas", "montana", "cocina", "kilometros", "acaros", "hamster", "fuerte", "arroz", "peso", "mesa", "centimetro", "setenta",
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
#fondo{{position:absolute;inset:0;background:linear-gradient(#3fa7ff,#8fd3ff)}}
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
#vineta{{position:absolute;inset:0;background:radial-gradient(120% 80% at 50% 45%, rgba(0,0,0,0) 55%, rgba(18,16,48,0.22) 100%);pointer-events:none}}
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
  <div id="fondo"></div>
  <div id="camA" data-layout-allow-overflow data-layout-ignore><div id="camB" data-layout-allow-overflow data-layout-ignore>
  <div id="lejos">{"".join(LEJOS)}</div>
  <div id="world" data-layout-allow-overflow data-layout-ignore>
    
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

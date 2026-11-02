#!/usr/bin/env python3
"""PLANTILLA «¿Y SI GANA <PARTIDO>?» en 60 segundos, estilo LIBRETA (profesional, para adultos).
Todo lo del partido está en partido.json (color, logo, páginas con notas y bocetos).
Voz: tiempos.json (montar_voz.py). Salida: index.html (HyperFrames) + efectos.json (mezcla.py).
  python3 gen.py
"""
import json, math, os, random, re, unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(BASE, "partido.json"), encoding="utf-8"))
T = json.load(open(os.path.join(BASE, "tiempos.json"), encoding="utf-8"))
DUR = T["duracion"]
COL, COL2 = CFG["color"], CFG["color_claro"]
rnd = random.Random(7)

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
    raise KeyError(word)
def F(n): return FR[n - 1]["ini"]
def FE(n): return FR[n - 1]["fin"]

tl, FX = [], []
def J(s): tl.append(s)

# ------------------------------------------------------------------ medidas
NBX, NBY, NBW, NBH = 60, 560, 960, 1150          # libreta en pantalla
INK, INK2, RED, GRN = "#1f3a7a", "#222222", "#c0392b", "#2e7d32"
MARG = 120

def wob(x0, y0, x1, y1, amp=4, n=6, seed=0):
    r = random.Random(seed)
    pts = [f"M{x0:.0f},{y0:.0f}"]
    for i in range(1, n + 1):
        t = i / n
        pts.append(f"L{x0 + (x1 - x0) * t + r.uniform(-amp, amp) * 0.3:.0f},{y0 + (y1 - y0) * t + r.uniform(-amp, amp):.0f}")
    return " ".join(pts)

def wob_ellipse(cx, cy, rx, ry, seed=0):
    r = random.Random(seed)
    pts = []
    for i in range(0, 38):
        a = -0.4 + i / 34 * 2 * math.pi
        k = 1 + r.uniform(-0.05, 0.05)
        pts.append(f"{'M' if i == 0 else 'L'}{cx + rx * k * math.cos(a):.0f},{cy + ry * k * math.sin(a):.0f}")
    return " ".join(pts)

# ------------------------------------------------------------------ páginas
PAGES = []      # html de cada página
HEMI = []
RECORTES = []
PEN = []        # (t0, dur, x0, y0, x1, y1) recorridos del bolígrafo en coords de página
NID = [0]
def nid(p="e"):
    NID[0] += 1
    return f"{p}{NID[0]}"

def draw_on(sel, t, dur, stagger=0.0):
    J(f'tl.fromTo("{sel}", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:{dur:.2f}, ease:"power1.inOut", stagger:{stagger}, immediateRender:false}}, {t:.2f});')
    J(f'tl.set("{sel}", {{strokeDashoffset:1}}, 0);')

def escribe(pg, x, y, txt, t, size=60, font="hand", color=INK, dur=None, peso=700):
    """Texto que se escribe solo (de izquierda a derecha) con el boli siguiéndolo."""
    i = nid("tx")
    fam = {"hand": "Caveat", "marker": "Marker", "typed": "Courier"}[font]
    cw = {"hand": 0.36, "marker": 0.62, "typed": 0.6}[font]
    w = len(txt) * size * cw
    dur = dur or max(0.45, min(1.6, len(txt) * 0.05))
    pg.append(f'<div id="{i}" class="tx" style="left:{x}px;top:{y}px;font-family:{fam};font-size:{size}px;color:{color};font-weight:{peso}">{txt}</div>')
    J(f'tl.set("#{i}", {{clipPath:"inset(-30% 100% -30% -2%)"}}, 0); tl.to("#{i}", {{clipPath:"inset(-30% -4% -30% -2%)", duration:{dur:.2f}, ease:"none"}}, {t:.2f});')
    PEN.append((t, dur, x, y + size * 0.85, x + w, y + size * 0.85))
    return w, i

def linea(pg, d, t, dur=0.35, color=INK, ancho=6, op=1.0):
    i = nid("ln")
    pg.append(f'<svg class="sk" width="960" height="1150"><path id="{i}" d="{d}" pathLength="1" stroke="{color}" stroke-width="{ancho}" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="1" opacity="{op}"/></svg>')
    draw_on(f"#{i}", t, dur)
    return i

def resalta(pg, x, y, w, h, t, color=None):
    i = nid("hl")
    pg.insert(len(pg) - 1, f'<div id="{i}" style="position:absolute;left:{x - 6}px;top:{y}px;width:{w + 12}px;height:{h}px;background:{color or COL2};border-radius:8px;transform-origin:0 50%"></div>')
    J(f'tl.set("#{i}", {{scaleX:0}}, 0); tl.to("#{i}", {{scaleX:1, duration:0.4, ease:"power2.out"}}, {t:.2f});')

def signo(pg, x, y, si, t):
    if si:
        linea(pg, f"M{x},{y + 22} L{x + 16},{y + 40} L{x + 44},{y}", t, 0.25, GRN, 8)
    else:
        linea(pg, f"M{x},{y} L{x + 36},{y + 38} M{x + 36},{y} L{x},{y + 38}", t, 0.25, RED, 8)

# ------------------------------------------------------------------ bocetos a tinta (trazos que se dibujan)
def S(paths, fills=""):
    return paths, fills

def boceto(nombre, ox, oy, t, pg):
    """Dibuja un boceto a tinta en (ox, oy) de la página. Cada trazo se dibuja seguido."""
    P_ = []      # (d, color, ancho)
    FILL = []    # rellenos suaves que aparecen después
    c = COL
    if nombre == "hemiciclo":
        filas, total = 9, 350
        radios = [120 + i * 26 for i in range(filas)]
        cuenta = [round(total * r / sum(radios)) for r in radios]
        cuenta[-1] += total - sum(cuenta)
        seats = []
        for r, n in zip(radios, cuenta):
            for j in range(n):
                a = math.pi - j / (n - 1) * math.pi
                seats.append((a, ox + 330 + r * math.cos(a), oy + 360 - r * math.sin(a)))
        seats.sort(key=lambda s_: -s_[0])
        HEMI.extend(range(len(seats)))
        for idx, (a, x, y) in enumerate(seats):
            FILL.append(f'<circle class="esc{"P" if idx < 65 else ""}" cx="{x:.0f}" cy="{y:.0f}" r="8" fill="#ffffff" stroke="{INK}" stroke-width="2"/>')
        P_.append((wob(ox + 330, oy + 100, ox + 330, oy + 370, 3), RED, 5))
        FILL.append(f'<text x="{ox + 345}" y="{oy + 120}" font-family="Caveat" font-size="44" font-weight="700" fill="{RED}">176</text>')
        FILL.append(f'<text x="{ox + 200}" y="{oy + 420}" font-family="Caveat" font-size="40" font-weight="700" fill="{c}">≈ 65 escaños (encuestas)</text>')
    elif nombre == "cartera":
        P_ += [(f"M{ox + 120},{oy + 150} L{ox + 470},{oy + 150} C{ox + 500},{oy + 150} {ox + 510},{oy + 170} {ox + 510},{oy + 200} L{ox + 510},{oy + 380} C{ox + 510},{oy + 410} {ox + 490},{oy + 420} {ox + 460},{oy + 420} L{ox + 140},{oy + 420} C{ox + 110},{oy + 420} {ox + 100},{oy + 400} {ox + 100},{oy + 370} Z", INK2, 6),
               (f"M{ox + 400},{oy + 250} L{ox + 530},{oy + 250} L{ox + 530},{oy + 320} L{ox + 400},{oy + 320} Z", INK2, 6),
               (f"M{ox + 160},{oy + 150} L{ox + 200},{oy + 70} L{ox + 420},{oy + 120} L{ox + 410},{oy + 150}", c, 6)]
        for k, (x, y) in enumerate(((ox + 600, oy + 300), (ox + 650, oy + 360), (ox + 590, oy + 400))):
            P_.append((wob_ellipse(x, y, 34, 34, k), "#c9a227", 5))
        FILL.append(f'<text x="{ox + 585}" y="{oy + 315}" font-family="Caveat" font-size="40" font-weight="700" fill="#c9a227">€</text>')
    elif nombre == "casa":
        P_ += [(f"M{ox + 150},{oy + 230} L{ox + 330},{oy + 90} L{ox + 510},{oy + 230}", INK2, 7),
               (f"M{ox + 180},{oy + 210} L{ox + 180},{oy + 420} L{ox + 480},{oy + 420} L{ox + 480},{oy + 210}", INK2, 7),
               (f"M{ox + 290},{oy + 420} L{ox + 290},{oy + 320} L{ox + 370},{oy + 320} L{ox + 370},{oy + 420}", INK2, 5),
               (f"M{ox + 210},{oy + 260} L{ox + 260},{oy + 260} L{ox + 260},{oy + 300} L{ox + 210},{oy + 300} Z M{ox + 400},{oy + 260} L{ox + 450},{oy + 260} L{ox + 450},{oy + 300} L{ox + 400},{oy + 300} Z", INK2, 5),
               (f"M{ox + 520},{oy + 130} L{ox + 680},{oy + 130} L{ox + 700},{oy + 170} L{ox + 680},{oy + 210} L{ox + 520},{oy + 210} Z", c, 6)]
        FILL.append(f'<text x="{ox + 545}" y="{oy + 188}" font-family="Marker" font-size="46" fill="{c}">IVA 0%</text>')
    elif nombre == "tarta":
        cx, cy, r = ox + 330, oy + 260, 150
        P_.append((wob_ellipse(cx, cy, r, r, 3), INK2, 6))
        a = 2 * math.pi * 0.147
        x1, y1 = cx + r * math.sin(a), cy - r * math.cos(a)
        FILL.append(f'<path d="M{cx},{cy} L{cx},{cy - r} A{r},{r} 0 0,1 {x1:.0f},{y1:.0f} Z" fill="{c}" opacity="0.8"/>')
        P_.append((f"M{cx},{cy} L{cx},{cy - r} M{cx},{cy} L{x1:.0f},{y1:.0f}", INK2, 5))
        FILL.append(f'<text x="{cx + 170}" y="{cy - 90}" font-family="Caveat" font-size="58" font-weight="700" fill="{c}">14,7 %</text>')
        FILL.append(f'<text x="{cx + 170}" y="{cy - 40}" font-family="Caveat" font-size="40" font-weight="700" fill="{INK}">3,2 millones</text>')
    elif nombre == "embarazada":
        # mujer embarazada de perfil, a línea fina con relleno suave (respetuosa, estilo ilustración editorial)
        X = lambda x: ox + 170 + x
        Y = lambda y: oy - 80 + y
        cuerpo = (f"M{X(120)},{Y(150)} C{X(105)},{Y(220)} {X(100)},{Y(300)} {X(112)},{Y(380)} C{X(118)},{Y(430)} {X(95)},{Y(500)} {X(88)},{Y(560)} "
                  f"L{X(232)},{Y(560)} C{X(226)},{Y(500)} {X(214)},{Y(450)} {X(220)},{Y(420)} C{X(262)},{Y(400)} {X(282)},{Y(350)} {X(272)},{Y(300)} "
                  f"C{X(262)},{Y(255)} {X(222)},{Y(238)} {X(196)},{Y(232)} C{X(206)},{Y(210)} {X(196)},{Y(176)} {X(172)},{Y(160)} C{X(158)},{Y(150)} {X(140)},{Y(146)} {X(120)},{Y(150)} Z")
        FILL.append(f'<path d="{cuerpo}" fill="{COL2}"/>')
        FILL.append(f'<circle cx="{X(150)}" cy="{Y(88)}" r="44" fill="#f3d9c4"/><circle cx="{X(118)}" cy="{Y(64)}" r="24" fill="#5b4636"/>'
                    f'<path d="M{X(108)},{Y(80)} C{X(110)},{Y(40)} {X(150)},{Y(30)} {X(178)},{Y(52)} C{X(160)},{Y(56)} {X(140)},{Y(70)} {X(128)},{Y(100)} Z" fill="#5b4636"/>')
        P_ += [(f"M{X(150)},{Y(44)} C{X(178)},{Y(44)} {X(196)},{Y(66)} {X(194)},{Y(92)} L{X(202)},{Y(104)} L{X(192)},{Y(110)} C{X(190)},{Y(126)} {X(176)},{Y(132)} {X(160)},{Y(130)}", INK2, 5),
               (cuerpo, INK2, 5),
               (f"M{X(150)},{Y(168)} C{X(160)},{Y(220)} {X(170)},{Y(255)} {X(178)},{Y(285)} C{X(196)},{Y(300)} {X(226)},{Y(312)} {X(246)},{Y(318)}", INK2, 5),
               (wob_ellipse(X(240), Y(318), 18, 12, 2), INK2, 4)]
    elif nombre == "mapa":
        m = json.load(open(os.path.join(BASE, "espana.json")))
        VX, VY, VW, VH = 240, -10, 380, 320            # solo la península (sin Canarias, que va aparte en el original)
        W_, H_ = 600, 505
        regs = "".join(f'<path d="{l["path"]}" fill="{COL2}" stroke="{INK2}" stroke-width="1.6"/>' for l in m["locations"] if l["id"] != "canary-islands")
        FILL.append(f'<svg x="{ox + 30}" y="{oy}" width="{W_}" height="{H_}" viewBox="{VX} {VY} {VW} {VH}" overflow="visible">{regs}</svg>')
        mp = lambda X, Y: (ox + 30 + (X - VX) * W_ / VW, oy + (Y - VY) * H_ / VH)
        mx, my = mp(372, 128)
        FILL.append(f'<circle cx="{mx:.0f}" cy="{my:.0f}" r="13" fill="{RED}"/>')
        for X, Y in ((275, 62), (332, 28), (420, 30), (556, 72), (478, 92), (470, 165), (385, 252), (300, 172), (482, 228)):
            x0, y0 = mp(X, Y)
            P_.append((f"M{x0:.0f},{y0:.0f} L{x0 + (mx - x0) * 0.82:.0f},{y0 + (my - y0) * 0.82:.0f}", RED, 5))
    elif nombre == "edificio":
        P_ += [(f"M{ox + 140},{oy + 180} L{ox + 330},{oy + 80} L{ox + 520},{oy + 180} Z", INK2, 6),
               (f"M{ox + 130},{oy + 420} L{ox + 530},{oy + 420} M{ox + 150},{oy + 400} L{ox + 510},{oy + 400}", INK2, 6)]
        for k in range(5):
            x = ox + 175 + k * 75
            P_.append((f"M{x},{oy + 195} L{x},{oy + 395} M{x + 30},{oy + 195} L{x + 30},{oy + 395}", INK2, 5))
    elif nombre == "europa":
        cx, cy = ox + 230, oy + 260
        for k in range(12):
            a = k / 12 * 2 * math.pi
            x, y = cx + 120 * math.cos(a), cy + 120 * math.sin(a)
            FILL.append(f'<path d="M{x:.0f},{y - 14:.0f} L{x + 4:.0f},{y - 4:.0f} L{x + 14:.0f},{y - 4:.0f} L{x + 6:.0f},{y + 3:.0f} L{x + 9:.0f},{y + 14:.0f} L{x:.0f},{y + 7:.0f} L{x - 9:.0f},{y + 14:.0f} L{x - 6:.0f},{y + 3:.0f} L{x - 14:.0f},{y - 4:.0f} L{x - 4:.0f},{y - 4:.0f} Z" fill="#e0b000"/>')
        P_.append((wob_ellipse(cx, cy, 160, 160, 4), "#2c4fa3", 6))
        P_ += [(f"M{ox + 420},{oy + 200} L{ox + 470},{oy + 260} L{ox + 440},{oy + 270} L{ox + 500},{oy + 340}", RED, 8)]
        P_.append((wob_ellipse(ox + 600, oy + 260, 110, 110, 6), c, 6))
        FILL.append(f'<text x="{ox + 555}" y="{oy + 280}" font-family="Marker" font-size="52" fill="{c}">ES</text>')
    elif nombre == "balanza":
        P_ += [(f"M{ox + 330},{oy + 80} L{ox + 330},{oy + 430} M{ox + 230},{oy + 430} L{ox + 430},{oy + 430}", INK2, 7),
               (f"M{ox + 110},{oy + 150} L{ox + 550},{oy + 110}", INK2, 7),
               (f"M{ox + 110},{oy + 150} L{ox + 50},{oy + 280} L{ox + 170},{oy + 280} Z", GRN, 6),
               (f"M{ox + 550},{oy + 110} L{ox + 490},{oy + 240} L{ox + 610},{oy + 240} Z", RED, 6)]
    elif nombre == "urna":
        P_ += [(f"M{ox + 160},{oy + 200} L{ox + 500},{oy + 200} L{ox + 500},{oy + 440} L{ox + 160},{oy + 440} Z", INK2, 7),
               (f"M{ox + 140},{oy + 200} L{ox + 520},{oy + 200} M{ox + 270},{oy + 200} L{ox + 390},{oy + 200}", INK2, 9),
               (f"M{ox + 290},{oy + 60} L{ox + 380},{oy + 60} L{ox + 380},{oy + 190} L{ox + 290},{oy + 190} Z", c, 6)]
        FILL.append(f'<text x="{ox + 240}" y="{oy + 345}" font-family="Marker" font-size="64" fill="{INK2}">29-N</text>')
    # html del boceto
    gid = nid("bk")
    paths = "".join(f'<path class="tz" d="{d}" pathLength="1" stroke="{col}" stroke-width="{w}" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="1"/>' for d, col, w in P_)
    pg.append(f'<svg class="sk" id="{gid}" width="960" height="1150"><g class="relleno">{"".join(FILL)}</g>{paths}</svg>')
    if P_:
        draw_on(f"#{gid} .tz", t, 0.45, stagger=0.18)
    J(f'tl.set("#{gid} .relleno", {{opacity:0}}, 0); tl.to("#{gid} .relleno", {{opacity:1, duration:0.5}}, {t + 0.3:.2f});')
    if nombre == "hemiciclo":
        J(f'tl.to("#{gid} .escP", {{attr:{{fill:"{COL}"}}, duration:0.05, stagger:0.025}}, {t + 0.5:.2f});')
    PEN.append((t, 0.45 + 0.18 * max(0, len(P_) - 1), ox + 120, oy + 120, ox + 500, oy + 380))

# ------------------------------------------------------------------ construir páginas
paginas = CFG["paginas"]
NP = len(paginas)
P_START = []
for k, pdata in enumerate(paginas):
    t0 = F(pdata["lineas"][0])
    P_START.append(t0)
    pg = []
    # papel: rayas, margen, agujeros de la espiral
    pg.append(f'<div class="papel {pdata.get("papel", "")}"></div><div class="cinta" style="left:{60 + (k * 37) % 120}px;transform:rotate(-4deg)"></div><div class="cinta" style="right:{60 + (k * 53) % 90}px;transform:rotate(5deg)"></div>')
    if pdata.get("tipo") == "portada":
        c = CFG["portada"]
        pg.append(f'<img src="{CFG["logo"]}" style="position:absolute;left:{480 - 150}px;top:110px;width:300px;opacity:0.95" id="logoP"/>')
        J('tl.set("#logoP", {opacity:0, y:20}, 0); tl.to("#logoP", {opacity:1, y:0, duration:0.5, ease:"power2.out"}, 0.05);')
        escribe(pg, MARG + 30, 330, c["linea1"], 0.1, size=110, font="marker", color=INK2, dur=0.7)
        w2, _ = escribe(pg, MARG + 30, 470, c["linea2"], 0.75, size=150, font="marker", color=COL, dur=0.5)
        linea(pg, wob(MARG + 30, 655, MARG + 60 + w2, 650, 5, 8, 3), 1.25, 0.4, COL, 10)
        escribe(pg, MARG + 40, 720, c["fecha"], P("elecciones"), size=96, font="marker", color=RED, dur=0.5)
        linea(pg, wob_ellipse(MARG + 165, 772, 170, 75, 11), P("noviembre"), 0.5, RED, 6)
        escribe(pg, MARG + 40, 900, c["sub"], P("cuento"), size=70, dur=1.0)
        linea(pg, wob(MARG + 40, 990, MARG + 640, 985, 4, 8, 5), P("sesenta"), 0.4, COL, 7)
    else:
        w, _ = escribe(pg, MARG + 10, 60, pdata["titulo"], t0 + 0.05, size=88, font="marker", color=COL, dur=0.55)
        linea(pg, wob(MARG + 10, 165, MARG + 30 + w, 160, 4, 8, k), t0 + 0.55, 0.3, COL, 8)
        y = 230
        for j, nota in enumerate(pdata.get("notas", [])):
            tn = max(P(nota["cuando"]) - 0.1, t0 + 0.6)
            size = 76 if nota.get("grande") else 60
            col = COL if nota.get("color") == "partido" else INK
            if nota.get("marca") == "resalta":
                resalta(pg, MARG + 10, y + 18, len(nota["txt"]) * size * 0.36, size * 0.8, tn)
            wn, _ = escribe(pg, MARG + 10 + (60 if nota.get("signo") else 0), y, nota["txt"], tn, size=size, color=col)
            if nota.get("signo"):
                signo(pg, MARG + 10, y + 20, nota["signo"] == "si", tn)
            if nota.get("marca") == "subraya":
                linea(pg, wob(MARG + 10, y + size + 8, MARG + 20 + wn, y + size + 4, 4, 8, j), tn + 0.5, 0.3, COL, 6)
            if nota.get("marca") == "rodea":
                linea(pg, wob_ellipse(MARG + 10 + wn / 2, y + size * 0.55, wn / 2 + 30, size * 0.75, j + 20), tn + 0.6, 0.45, RED, 5)
            if nota.get("tacha"):
                linea(pg, wob(MARG + 5, y + size * 0.55, MARG + 15 + wn, y + size * 0.5, 3, 6, j + 40), P(nota["tacha"]) - 0.1, 0.3, RED, 7)
            y += 100 if not nota.get("grande") else 120
        bt = P(pdata["boceto_cuando"]) if pdata.get("boceto_cuando") else t0 + 0.8
        boceto(pdata["boceto"], 150, max(y + 10, 560), max(bt, t0 + 0.7), pg)
        if pdata.get("posit"):
            po = pdata["posit"]; pid_ = nid("po"); rr = rnd.choice([-6, -4, 4, 6])
            fs_ = min(66, int(250 / max(1, len(po["txt"]) * 0.58)))
            pg.append(f'<div id="{pid_}" class="posit" style="left:600px;top:{max(y + 40, 590)}px"><div class="pt" style="font-size:{fs_}px">{po["txt"]}</div><div class="ps">{po["sub"]}</div></div>')
            tp = P(po["cuando"]) + 0.1
            J(f'tl.set("#{pid_}", {{opacity:0, y:-360, rotation:-28, scale:1.35}}, 0); tl.to("#{pid_}", {{opacity:1, y:0, rotation:{rr}, scale:1, duration:0.45, ease:"back.out(1.6)"}}, {tp:.2f});')
            J(f'tl.to("#cam", {{scale:"+=0.025", duration:0.12, yoyo:true, repeat:1, ease:"power2.out"}}, {tp + 0.4:.2f});')
            FX.append(("posit", tp + 0.38))
        if pdata.get("sello"):
            sid = nid("se")
            pg.append(f'<div id="{sid}" class="sello">{pdata["sello"]}</div>')
            ts_ = t0 + 0.75
            J(f'tl.set("#{sid}", {{opacity:0, scale:2.2, rotation:-14}}, 0); tl.to("#{sid}", {{opacity:0.85, scale:1, rotation:-12, duration:0.22, ease:"power3.in"}}, {ts_:.2f});')
            FX.append(("sello", ts_ + 0.2))
        if pdata.get("fuente"):
            fid = nid("fu")
            pg.append(f'<div id="{fid}" class="fuente">{pdata["fuente"]}</div>')
            J(f'tl.set("#{fid}", {{opacity:0}}, 0); tl.to("#{fid}", {{opacity:1, duration:0.4}}, {t0 + 0.8:.2f});')
    if pdata.get("recorte"):
        RECORTES.append(pdata["recorte"])
    PAGES.append(pg)

# pasar página (la de arriba se levanta hacia arriba, como una libreta de espiral)
for k in range(NP - 1):
    tf = P_START[k + 1] - 0.45
    J(f'tl.to("#pg{k}", {{x:{-1250 if k % 2 == 0 else 1250}, y:-60, rotation:{-9 if k % 2 == 0 else 9}, duration:0.5, ease:"power2.in"}}, {tf:.2f}); tl.set("#pg{k}", {{opacity:0}}, {tf + 0.5:.2f});')
    J(f'tl.fromTo("#pg{k} .sombra", {{opacity:0}}, {{opacity:0.0, duration:0.5, immediateRender:false}}, {tf:.2f});')
    FX.append(("pagina", tf))

# recortes (gráfico impreso o ficha de prensa) que entran sobre la mesa y salen
OVR = []
for i, rc in enumerate(RECORTES):
    rid = f"rc{i}"
    ta = P(rc["cuando"]) - 0.2
    if rc["tipo"] == "grafico":
        mx = max(v for _, v in rc["barras"]) * 1.25
        barras = "".join(f'<div class="rb"><div class="rl">{l}</div><div class="rbar"><i id="{rid}b{j}" style="width:{v / mx * 100:.0f}%;background:{COL if j == len(rc["barras"]) - 1 else "#9aa3ad"}"></i><span>{str(v).replace(".", ",")} %</span></div></div>' for j, (l, v) in enumerate(rc["barras"]))
        cuerpo = f'<div class="rt">{rc["titular"]}</div>{barras}<div class="rp">{rc["pie"]}</div>'
        for j in range(len(rc["barras"])):
            J(f'tl.from("#{rid}b{j}", {{scaleX:0, transformOrigin:"0 50%", duration:0.6, ease:"power2.out", immediateRender:false}}, {ta + 0.35 + j * 0.25:.2f});')
    else:
        cuerpo = (f'<div class="rs">{rc["seccion"]}</div><div class="rh">{rc["titular"]}</div><div class="rx">{rc["texto"]}</div><div class="rp">{rc["pie"]}</div>')
    OVR.append(f'<div id="{rid}" class="recorte {rc["tipo"]}">{cuerpo}</div>')
    J(f'tl.set("#{rid}", {{opacity:0, y:900, rotation:8}}, 0); tl.to("#{rid}", {{opacity:1, y:0, rotation:-3, duration:0.45, ease:"power3.out"}}, {ta:.2f});')
    J(f'tl.to("#{rid}", {{x:1200, rotation:10, duration:0.4, ease:"power2.in"}}, {ta + rc["dur"]:.2f}); tl.set("#{rid}", {{opacity:0}}, {ta + rc["dur"] + 0.4:.2f});')
    J(f'tl.to("#libreta, #espiral", {{filter:"brightness(0.93)", duration:0.3}}, {ta:.2f}); tl.to("#libreta, #espiral", {{filter:"brightness(1)", duration:0.3}}, {ta + rc["dur"]:.2f});')
    FX.append(("pagina", ta)); FX.append(("pagina", ta + rc["dur"]))

# cámara que respira: empuje lento por página
J('tl.set("#cam", {transformOrigin:"540px 1150px"}, 0);')
for k in range(NP):
    ta = P_START[k]; tb = P_START[k + 1] if k + 1 < NP else DUR
    J(f'tl.fromTo("#cam", {{scale:1.0, x:0, y:0}}, {{scale:1.06, x:{(-1) ** k * 14}, y:-20, duration:{tb - ta:.2f}, ease:"sine.inOut", immediateRender:false}}, {ta:.2f});')
# vapor del café
J(f'tl.to(".deco", {{y:"+=30", x:"+=12", duration:{DUR / 3:.2f}, yoyo:true, repeat:2, ease:"sine.inOut", stagger:0.6}}, 0);')

# boli: va a cada trazo y lo sigue
PEN.sort()
J(f'tl.set("#boli", {{x:{NBX + 700}, y:{NBY + 400}, rotation:0}}, 0);')
last_end = 0
for (t, d, x0, y0, x1, y1) in PEN:
    sx, sy, ex, ey = NBX + x0, NBY + y0, NBX + x1, NBY + y1
    ida = min(0.25, max(0.08, t - last_end))
    J(f'tl.to("#boli", {{x:{sx:.0f}, y:{sy:.0f}, duration:{ida:.2f}, ease:"power2.out"}}, {max(0, t - ida):.2f});')
    J(f'tl.to("#boli", {{x:{ex:.0f}, y:{ey:.0f}, duration:{d:.2f}, ease:"none"}}, {t:.2f});')
    J(f'tl.to("#boli", {{keyframes:{{y:["-=8", "+=8"]}}, duration:0.12, repeat:{max(0, int(d / 0.12) - 1)}, ease:"sine.inOut"}}, {t:.2f});')
    last_end = t + d
    FX.append(("lapiz", t))

# cuenta atrás de 60 s (pequeña, todo el rato)
for s in range(1, 61):
    ts = min(s * DUR / 60, DUR - 0.12)
    J(f'tl.set("#crono-n", {{innerHTML:"{60 - s}"}}, {ts:.2f});')
J(f'tl.fromTo("#crono-arc", {{strokeDashoffset:0}}, {{strokeDashoffset:1, duration:{DUR:.2f}, ease:"none", immediateRender:false}}, 0);')
J(f'tl.to("#crono", {{rotation:4, duration:0.5, yoyo:true, repeat:{int(DUR / 0.5)}, ease:"sine.inOut"}}, 0);')

# ------------------------------------------------------------------ subtítulos
CLAVE = set(norm(w) for w in CFG.get("clave", []))
SUBS = []
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
        J(f'tl.to("#{wid}", {{color:"#1d2433", fontWeight:800, duration:0.06}}, {p["ini"]:.2f});')
    SUBS.append(f'<div id="sub{k}" class="clip sub" data-start="{max(0, st):.3f}" data-duration="{max(0.2, en - max(0, st)):.3f}" data-track-index="3">{" ".join(spans)}</div>')

# ------------------------------------------------------------------ mesa (fondo) con detalles
mesa = (f'<svg width="1080" height="1920" style="position:absolute;left:0;top:0">'
        f'<defs><linearGradient id="fondoC" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fcfcf9"/><stop offset="1" stop-color="#eef3ea"/></linearGradient>'
        '<pattern id="puntos" width="38" height="38" patternUnits="userSpaceOnUse"><circle cx="19" cy="19" r="2.4" fill="#c9cfc4"/></pattern></defs>'
        '<rect width="1080" height="1920" fill="url(#fondoC)"/><rect width="1080" height="1920" fill="url(#puntos)" opacity="0.55"/>'
        f'<circle class="deco" cx="980" cy="420" r="260" fill="{COL2}"/><circle class="deco" cx="80" cy="1650" r="300" fill="{COL2}"/>'
        f'<circle class="deco" cx="120" cy="560" r="120" fill="none" stroke="{COL}" stroke-width="4" opacity="0.35"/>'
        f'<circle class="deco" cx="990" cy="1700" r="90" fill="none" stroke="{COL}" stroke-width="4" opacity="0.35"/>'
        + "".join(f'<path class="deco" d="M{x - 14},{y} L{x + 14},{y} M{x},{y - 14} L{x},{y + 14}" stroke="{c}" stroke-width="5" stroke-linecap="round"/>' for x, y, c in ((70, 470, COL), (1010, 1180, "#c0392b"), (40, 1180, "#e0b000"), (1030, 640, "#8aa0b8"), (980, 1850, COL)))
        + "".join(f'<rect x="{x}" y="1870" width="60" height="50" fill="{COL}" opacity="0.18" transform="skewX(-30)"/>' for x in range(0, 1300, 120))
        + f'<text x="540" y="1250" text-anchor="middle" font-family="Marker" font-size="560" fill="{COL}" opacity="0.05" transform="rotate(-12 540 1100)">29N</text>'
        '</svg>')

html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
@font-face{{font-family:"Caveat";src:url("assets/fonts/Caveat-700-latin.woff2") format("woff2");font-weight:700}}
@font-face{{font-family:"Marker";src:url("assets/fonts/permanent-marker-400.woff2") format("woff2")}}
@font-face{{font-family:"Courier";src:url("assets/fonts/courier-prime-700.woff2") format("woff2");font-weight:700}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#f6f7f2}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif}}
#libreta{{position:absolute;left:{NBX}px;top:{NBY}px;width:{NBW}px;height:{NBH}px;perspective:2600px}}
#trasera{{position:absolute;left:0;top:0;width:{NBW}px;height:{NBH}px;background:{COL2};border-radius:34px;transform:rotate(3deg);box-shadow:0 20px 40px rgba(40,60,30,0.12)}}
#trasera2{{position:absolute;left:0;top:0;width:{NBW}px;height:{NBH}px;background:#ffffff;border-radius:34px;transform:rotate(-2deg);box-shadow:0 20px 40px rgba(40,60,30,0.12)}}
.pg{{position:absolute;left:0;top:0;width:{NBW}px;height:{NBH}px;border-radius:34px;overflow:hidden;box-shadow:0 26px 50px rgba(40,60,30,0.16)}}
.papel{{position:absolute;inset:0;background:#ffffff}}
.papel::before{{content:"";position:absolute;left:0;right:0;top:0;height:18px;background:{COL}}}
.papel::after{{content:"";position:absolute;inset:18px 0 0 0;background:radial-gradient(circle, rgba(150,160,150,0.22) 2px, transparent 2.5px) 0 0/34px 34px}}
.papel.cuadricula::after{{background:repeating-linear-gradient(90deg, transparent 0 49px, rgba(100,171,76,0.10) 49px 50px), repeating-linear-gradient(180deg, transparent 0 49px, rgba(100,171,76,0.10) 49px 50px)}}
.cinta{{position:absolute;top:-6px;width:170px;height:52px;background:{COL};opacity:0.35}}
.posit{{position:absolute;width:300px;height:250px;background:linear-gradient(160deg,#fff6a8,#ffe76b);box-shadow:0 18px 30px rgba(0,0,0,0.28);padding:28px 22px;text-align:center;border-radius:2px}}
.posit::before{{content:"";position:absolute;left:0;right:0;top:0;height:34px;background:rgba(0,0,0,0.05)}}
.pt{{font-family:Marker;font-size:66px;color:#222;line-height:1.1;white-space:nowrap}}
.ps{{font-family:Caveat;font-weight:700;font-size:40px;color:{INK};margin-top:10px}}
.sello{{position:absolute;right:46px;top:{NBH - 132}px;padding:4px 16px;border:5px solid #c0392b;color:#c0392b;font:900 30px Courier;letter-spacing:4px;border-radius:10px}}
  .recorte{{position:absolute;left:110px;top:720px;width:860px;padding:44px 50px;background:#ffffff;box-shadow:0 30px 70px rgba(40,60,30,0.25);border-radius:28px;border-left:16px solid {COL}}}
.recorte.periodico{{background:#fbfaf6}}
.rt{{font-family:Marker;font-size:58px;color:#222;margin-bottom:26px}}
.rb{{margin:18px 0}} .rl{{font:700 34px Courier;color:#444;margin-bottom:8px}}
.rbar{{position:relative;height:70px;background:#ecebe6;border-radius:6px}} .rbar i{{position:absolute;left:0;top:0;bottom:0;border-radius:6px}}
.rbar span{{position:absolute;right:16px;top:8px;font-family:Marker;font-size:46px;color:#222}}
.rs{{font:700 30px Courier;letter-spacing:6px;color:{COL};border-bottom:3px solid #222;padding-bottom:8px;margin-bottom:18px}}
.rh{{font:900 76px Georgia, serif;line-height:1.05;color:#111;margin-bottom:20px}}
.rx{{font:400 40px Georgia, serif;line-height:1.3;color:#333}}
.rp{{font:700 24px Courier;color:#888;margin-top:24px}}
.sombra{{position:absolute;inset:0;background:#000;opacity:0;pointer-events:none}}
.tx{{position:absolute;white-space:nowrap;line-height:1.1}}
.sk{{position:absolute;left:0;top:0;overflow:visible}}
.fuente{{position:absolute;left:{MARG}px;right:300px;top:{NBH - 70}px;font:700 22px Courier;color:#777;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
#crono{{position:absolute;left:{NBX + NBW - 150}px;top:{NBY - 120}px;width:170px;height:170px}}
#boli{{position:absolute;left:0;top:0;width:10px;height:10px;overflow:visible}}
#marca{{position:absolute;left:0;right:0;top:1775px;text-align:center;font:700 28px Inter;color:#1d2433;opacity:0.35;pointer-events:none}}
#subs{{position:absolute;left:70px;right:70px;top:250px;height:220px}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:500 62px Inter;color:rgba(40,48,40,0.32);line-height:1.22}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:4px solid {COL};border-radius:6px;background:{COL}33;opacity:0}}
.key b{{position:absolute;width:16px;height:16px;border-radius:50%;background:#fff;border:4px solid {COL};opacity:0}}
.key .d1{{left:-12px;top:-12px}} .key .d2{{right:-12px;bottom:-10px}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="cam" style="position:absolute;left:0;top:0;width:1080px;height:1920px" data-layout-allow-overflow data-layout-ignore>
  {mesa}
  <div id="libreta" data-layout-allow-overflow data-layout-ignore>
    <div id="trasera"></div><div id="trasera2"></div>
    {"".join(f'<div class="pg" id="pg{k}" style="z-index:{100 - k}">{"".join(pg)}<div class="sombra"></div></div>' for k, pg in enumerate(PAGES))}
  </div>
  <svg id="crono" width="170" height="170" viewBox="0 0 170 170" data-layout-allow-overflow>
    <rect x="72" y="2" width="26" height="18" rx="4" fill="#2b2b2b"/><circle cx="85" cy="92" r="72" fill="#fbf8f0" stroke="#2b2b2b" stroke-width="7"/>
    <circle id="crono-arc" cx="85" cy="92" r="58" fill="none" stroke="{COL}" stroke-width="12" pathLength="1" stroke-dasharray="1" transform="rotate(-90 85 92)"/>
    <text id="crono-n" x="85" y="110" text-anchor="middle" font-family="Marker" font-size="50" fill="#2b2b2b">60</text>
  </svg>
  <svg id="boli" width="10" height="10" data-layout-allow-overflow><g transform="rotate(-35)"><rect x="-9" y="-260" width="18" height="230" rx="8" fill="#1b1b1b"/><rect x="-9" y="-200" width="18" height="14" fill="{COL}"/><path d="M-9,-30 L9,-30 L0,0 Z" fill="#c9c9c9"/><circle cx="0" cy="-2" r="2.5" fill="{INK}"/></g></svg>
  </div>
  {"".join(OVR)}
  <div id="marca">@mundo.supuesto</div>
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
json.dump(FX, open(os.path.join(BASE, "efectos.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones · {NP} páginas")

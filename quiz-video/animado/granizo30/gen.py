#!/usr/bin/env python3
"""«¿Y si granizara 30 días seguidos?» v2 — estilo DOCUMENTAL / informe meteorológico (serio, adulto).
Sin personaje, granizo realista en 3 capas de profundidad, diagramas técnicos limpios, mapa real de España, panel de
salidas, gráfica de precios, contador «DÍA NN/30» fijo, un movimiento de cámara por plano, cortes secos y solo 3
transiciones (cortina de granizo) en los cambios de bloque. Misma voz (tiempos.json).
  python3 gen.py → index.html + efectos.json
"""
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
tl, FX = [], []
def J(s): tl.append(s)
NID = [0]
def nid(p="e"):
    NID[0] += 1
    return f"{p}{NID[0]}"

BG, INK, MUTED = "#070c16", "#e9f1fb", "#8796ad"
ICE, ICE2, AMB, RED, GRN = "#9fdcff", "#d9f2ff", "#ffb547", "#ff5a52", "#4cd18a"

def pop(sel, t, d=0.45, frm="opacity:0, y:24", ease="power3.out"):
    J(f'tl.set("{sel}", {{opacity:0}}, 0);')
    J(f'tl.fromTo("{sel}", {{{frm}}}, {{opacity:1, x:0, y:0, scale:1, duration:{d}, ease:"{ease}", immediateRender:false}}, {t:.2f});')
def fuera(sel, t, d=0.3):
    J(f'tl.to("{sel}", {{opacity:0, duration:{d}, ease:"power2.in"}}, {t:.2f});')

ESC = []
def escena(eid, cuerpo, w=1080):
    ESC.append(f'<div class="esc" id="{eid}"><div class="cam" id="{eid}-cam"><svg width="{w}" height="1920" viewBox="0 0 {w} 1920" style="position:absolute;left:0;top:0;overflow:visible">{cuerpo}</svg></div></div>')
def mostrar(eid, t0, t1):
    J(f'tl.set("#{eid}", {{opacity:0}}, 0); tl.set("#{eid}", {{opacity:1}}, {t0:.2f}); tl.set("#{eid}", {{opacity:0}}, {t1:.2f});')
def camara(eid, t0, t1, desde, hasta, ease="sine.inOut"):
    x0, y0, s0 = desde; x1, y1, s1 = hasta
    J(f'tl.fromTo("#{eid}-cam", {{x:{x0}, y:{y0}, scale:{s0}}}, {{x:{x1}, y:{y1}, scale:{s1}, duration:{t1 - t0:.2f}, ease:"{ease}", immediateRender:false}}, {t0:.2f});')
def barrido(t):
    J(f'tl.fromTo("#cortina", {{y:-2400}}, {{y:1920, duration:0.6, ease:"power2.inOut", immediateRender:false}}, {t - 0.3:.2f});')
    FX.append(("whoosh", t - 0.3))

# ------------------------------------------------------------------ granizo realista
def piedra(x, y, r, streak=True, op=1.0):
    s = (f'<path d="M{x - r * 0.15:.1f},{y - r * 7:.1f} L{x},{y}" stroke="url(#estela)" stroke-width="{r * 1.1:.1f}" stroke-linecap="round" opacity="{0.55 * op:.2f}"/>' if streak else "")
    return s + (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="url(#hielo)" opacity="{op:.2f}"/>'
                f'<circle cx="{x - r * 0.35:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.28:.1f}" fill="#ffffff" opacity="{0.9 * op:.2f}"/>')
def capa_granizo(gid, n, rmin, rmax, op, seed, w=1080, h=1920):
    rr = random.Random(seed)
    cuerpo = "".join(piedra(rr.uniform(-60, w + 60), rr.uniform(0, h), rr.uniform(rmin, rmax), True, op) for _ in range(n))
    return f'<g class="gcapa" id="{gid}"><g class="gmov">{cuerpo}<g transform="translate(0,-{h})">{cuerpo}</g></g></g>'
def granizo(pref, seed=1, densidad=1.0):
    return (capa_granizo(f"{pref}a", int(70 * densidad), 2.5, 4.5, 0.45, seed)
            + capa_granizo(f"{pref}b", int(45 * densidad), 5, 8, 0.75, seed + 1)
            + capa_granizo(f"{pref}c", int(14 * densidad), 10, 15, 1.0, seed + 2))
def caer(pref, t0, t1):
    for suf, vel, dx in (("a", 1.6, 30), ("b", 1.0, 50), ("c", 0.65, 80)):
        n = max(1, int((t1 - t0) / vel) + 1)
        J(f'tl.fromTo("#{pref}{suf} .gmov", {{y:0, x:0}}, {{y:1920, x:{-dx}, duration:{vel}, repeat:{n}, ease:"none", immediateRender:false}}, {t0:.2f});')
    tt = t0
    while tt < t1 - 0.6:
        FX.append(("granizo", tt)); tt += 2.3

# ------------------------------------------------------------------ ciudad en silueta con volumen y luz
def ciudad(seed, y_suelo=1500, luces=0.35, tono="#111b2e", tono2="#0b1322", nieve=False, altura=1.0):
    rr = random.Random(seed)
    s = []
    x = -40
    while x < 1120:
        w, h = rr.randint(90, 170), rr.randint(380, 760) * altura
        s.append(f'<rect x="{x}" y="{y_suelo - h:.0f}" width="{w}" height="{h:.0f}" fill="{tono2}"/>')
        x += w + rr.randint(0, 12)
    x = -60
    while x < 1140:
        w, h = rr.randint(150, 260), rr.randint(520, 980) * altura
        y0 = y_suelo - h
        s.append(f'<rect x="{x}" y="{y0:.0f}" width="{w}" height="{h:.0f}" fill="{tono}"/>'
                 f'<rect x="{x + w - 18}" y="{y0:.0f}" width="18" height="{h:.0f}" fill="#000" opacity="0.25"/>'
                 f'<rect x="{x - 4}" y="{y0 - 10:.0f}" width="{w + 8}" height="12" fill="#1c2a44"/>')
        if nieve:
            s.append(f'<rect x="{x - 4}" y="{y0 - 22:.0f}" width="{w + 8}" height="14" rx="6" fill="{ICE2}" opacity="0.9"/>')
        cols, filas = max(2, w // 48), int((h - 60) // 64)
        for i in range(cols):
            for j in range(filas):
                if rr.random() < luces:
                    wx, wy = x + 16 + i * ((w - 30) / cols), y0 + 30 + j * 64
                    c = rr.choice(("#ffcf7a", "#ffd99a", "#f6b75a", "#cfe6ff"))
                    s.append(f'<rect x="{wx:.0f}" y="{wy:.0f}" width="22" height="30" fill="{c}" opacity="{rr.uniform(0.55, 0.95):.2f}"/>')
        if rr.random() < 0.5:
            s.append(f'<path d="M{x + w * 0.3:.0f},{y0 - 10:.0f} l0,-60 M{x + w * 0.3 - 14:.0f},{y0 - 50:.0f} l28,0" stroke="#1c2a44" stroke-width="5"/>')
        x += w + rr.randint(6, 24)
    return "".join(s)
def calle(y=1500, mojada=True, blanca=False):
    s = [f'<rect x="0" y="{y}" width="1080" height="{1920 - y}" fill="url(#asfalto)"/>', f'<rect x="0" y="{y}" width="1080" height="34" fill="#1d2738"/>']
    if mojada:
        s.append(f'<rect x="0" y="{y + 34}" width="1080" height="{1920 - y - 34}" fill="url(#reflejo)" opacity="0.5"/>')
    if blanca:
        s.append(f'<rect id="mantoB" x="0" y="{y - 6}" width="1080" height="{1926 - y}" fill="url(#mantoG)" opacity="0"/>')
    return "".join(s)
def coche_sil(cid, x, y, s=1.0, col="#2a3550"):
    return (f'<g id="{cid}" transform="translate({x},{y}) scale({s})"><ellipse cx="170" cy="128" rx="180" ry="12" fill="#000" opacity="0.45"/>'
            f'<path d="M8,108 L8,72 Q12,50 48,46 L96,40 L140,4 L238,4 L290,42 L318,50 Q338,56 338,82 L338,108 Z" fill="{col}"/>'
            f'<path d="M150,14 L230,14 L268,44 L112,44 Z" fill="#1a2a44"/><path d="M150,14 L190,14 L170,44 L112,44 Z" fill="#ffffff" opacity="0.08"/>'
            f'<circle cx="84" cy="110" r="28" fill="#06090f"/><circle cx="262" cy="110" r="28" fill="#06090f"/>'
            f'<rect x="306" y="62" width="26" height="12" rx="4" fill="#ffe3a0"/><rect x="10" y="66" width="18" height="12" rx="4" fill="#ff5a52"/></g>')

# ------------------------------------------------------------------ HUD fijo y rótulos
OVR = []
OVR.append('<div id="hud"><div class="hl">DÍA</div><div class="hn" id="hudn">01</div><div class="hd">/ 30</div><div class="hbar"><i id="hudb"></i></div></div>')
J('tl.set("#hud", {opacity:0}, 0);')
def dia(t, n):
    J(f'tl.set("#hudn", {{innerHTML:"{n:02d}"}}, {t:.2f}); tl.to("#hudb", {{scaleX:{n / 30:.3f}, duration:0.6, ease:"power3.out"}}, {t:.2f});')
    J(f'tl.fromTo("#hudn", {{y:-20, opacity:0}}, {{y:0, opacity:1, duration:0.35, ease:"power3.out", immediateRender:false}}, {t:.2f});')
    FX.append(("tic", t))
def chip(txt, t, t_out, x, y, color=ICE):
    i = nid("ch")
    OVR.append(f'<div class="chip" id="{i}" style="left:{x}px;top:{y}px;border-color:{color}"><b style="background:{color}"></b>{txt}</div>')
    pop(f"#{i}", t, 0.4, "opacity:0, x:-30")
    fuera(f"#{i}", t_out)
def fuente(txt, t, t_out):
    i = nid("fu")
    OVR.append(f'<div class="fuente" id="{i}">{txt}</div>')
    pop(f"#{i}", t, 0.4, "opacity:0")
    fuera(f"#{i}", t_out)
def rueda(i, valor, size, col):
    h = [f'<span class="rueda" id="{i}" style="font-size:{size}px;color:{col}">']
    k = 0
    for ch in valor:
        if ch.isdigit():
            strip = "".join(f"<span>{d}</span>" for d in list(range(10)) * 2)
            h.append(f'<span class="dg"><span class="st" id="{i}-{k}">{strip}</span></span>'); k += 1
        else:
            h.append(f'<span class="sep">{ch}</span>')
    return "".join(h) + '</span>'
def gira(i, valor, t, d=1.0):
    k, n = 0, sum(c.isdigit() for c in valor)
    for ch in valor:
        if ch.isdigit():
            J(f'tl.fromTo("#{i}-{k}", {{y:"0em"}}, {{y:"-{10 + int(ch)}em", duration:{d + 0.08 * (n - k):.2f}, ease:"power4.out", immediateRender:false}}, {t:.2f});')
            k += 1
    J(f'tl.set("#{i}", {{opacity:0}}, 0); tl.set("#{i}", {{opacity:1}}, {t:.2f});')

# ------------------------------------------------------------------ piezas nuevas v3 (nube real, chorro de granizo, coche detallado)
DEFS = []
def cumulo(cid, cx, ybase, ytop, semi, seed, luz, alto, n=150, yunque=True, sombra="#1a2234", dentro=""):
    """Cumulonimbo: muchas pompas (clipPath) + luz lateral + volumen; base plana; yunque arriba."""
    rr = random.Random(seed); pf = []
    tope = ytop + (110 if yunque else 0)
    for i in range(n):
        t = rr.random() ** 0.85
        y = ybase - 30 - t * (ybase - 70 - tope)
        s = semi * (1 - 0.3 * math.sin(t * math.pi) + 0.12 * t)
        x = cx + rr.uniform(-s, s) * 0.82
        r = rr.uniform(0.22, 0.38) * semi * (1 - 0.3 * t)
        pf.append((x, y, r, t))
    pf.sort(key=lambda p: p[3])
    an = []
    if yunque:
        for i in range(44):
            u = rr.uniform(-1, 1)
            an.append((cx + u * 1.55 * semi, ytop + 60 + rr.uniform(-12, 22) + abs(u) * 18, rr.uniform(0.16, 0.26) * semi, abs(u)))
    circ = "".join(f'<circle id="{cid}p{i}" cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}"/>' for i, (x, y, r, t) in enumerate(pf))
    circ += "".join(f'<circle id="{cid}a{i}" cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}"/>' for i, (x, y, r, u) in enumerate(an))
    if yunque:
        circ += (f'<path id="{cid}y" d="M{cx - 1.6 * semi:.0f},{ytop + 85:.0f} C{cx - 1.0 * semi:.0f},{ytop + 10:.0f} {cx + 1.0 * semi:.0f},{ytop:.0f} '
                 f'{cx + 1.75 * semi:.0f},{ytop + 75:.0f} L{cx + 1.75 * semi:.0f},{ytop + 105:.0f} L{cx - 1.6 * semi:.0f},{ytop + 112:.0f} Z"/>')
    H = ybase - ytop
    DEFS.append(f'<clipPath id="{cid}F">{circ}</clipPath><clipPath id="{cid}B"><rect x="-600" y="{ytop - 300:.0f}" width="2300" height="{H + 300:.0f}"/></clipPath>')
    x0, w0 = cx - 2.2 * semi, 4.4 * semi
    vol = "".join(f'<circle cx="{x + r * 0.28:.0f}" cy="{y - r * 0.32:.0f}" r="{r * 0.75:.0f}" fill="url(#volB)"/>' for x, y, r, t in pf[::2])
    vol += "".join(f'<circle cx="{x - r * 0.3:.0f}" cy="{y + r * 0.35:.0f}" r="{r * 0.7:.0f}" fill="url(#volS)"/>' for x, y, r, t in pf[1::3])
    body = (f'<g clip-path="url(#{cid}B)"><g clip-path="url(#{cid}F)">'
            f'<rect x="{x0:.0f}" y="{ytop - 100:.0f}" width="{w0:.0f}" height="{H + 200:.0f}" fill="url(#{luz})"/>'
            f'<rect x="{x0:.0f}" y="{ytop - 100:.0f}" width="{w0:.0f}" height="{H + 200:.0f}" fill="url(#{alto})"/>{vol}{dentro}'
            f'<rect id="{cid}flash" x="{x0:.0f}" y="{ytop - 100:.0f}" width="{w0:.0f}" height="{H + 200:.0f}" fill="#eaf2ff" opacity="0"/></g></g>')
    return body, pf, an
def chorro(sid, xa, xb, y0, y1, abre=60, seed=1, n=70):
    """Cortina de granizo bajo la base de la nube (polígono con vetas que caen)."""
    rr = random.Random(seed)
    pol = f"{xa},{y0} {xb},{y0} {xb + abre},{y1} {xa - abre},{y1}"
    DEFS.append(f'<clipPath id="{sid}C"><polygon points="{pol}"/></clipPath>')
    H = y1 - y0
    lin = "".join(f'<path d="M{x:.0f},{y:.0f} l-5,24" stroke="#ffffff" stroke-width="2.4" stroke-linecap="round" opacity="{rr.uniform(0.35, 0.8):.2f}"/>'
                  for x, y in ((rr.uniform(xa - abre, xb + abre), rr.uniform(y0, y1)) for _ in range(n)))
    return (f'<g id="{sid}" opacity="0"><polygon points="{pol}" fill="url(#chorroG)"/><g clip-path="url(#{sid}C)"><g class="{sid}m">{lin}<g transform="translate(0,-{H})">{lin}</g></g></g></g>'), H
def mover_chorro(sid, H, t0, t1, vel=0.9):
    n = max(1, int((t1 - t0) / vel) + 1)
    J(f'tl.fromTo("#{sid} .{sid}m", {{y:0}}, {{y:{H}, duration:{vel}, repeat:{n}, ease:"none", immediateRender:false}}, {t0:.2f});')
def suave(pts, k=6):
    """Catmull-Rom → lista de puntos muestreados (para mover una piedra por una curva sin tirones)."""
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(0, i - 1)], pts[i], pts[i + 1], pts[min(len(pts) - 1, i + 2)]
        for s in range(k):
            t = s / k
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    out.append(pts[-1])
    return out
def coche_det(cid):
    """Turismo de perfil, detallado (1000 px de largo, ruedas apoyadas en y=362)."""
    def rueda_(x):
        return (f'<circle cx="{x}" cy="292" r="70" fill="#0a0c10"/><circle cx="{x}" cy="292" r="66" fill="none" stroke="#1d2129" stroke-width="5"/><circle cx="{x}" cy="292" r="44" fill="url(#llanta)"/>'
                + "".join(f'<path d="M{x},292 L{x + 38 * math.cos(a):.1f},{292 + 38 * math.sin(a):.1f}" stroke="#4d5766" stroke-width="11" stroke-linecap="round"/>' for a in [k * 2 * math.pi / 5 - math.pi / 2 for k in range(5)])
                + f'<circle cx="{x}" cy="292" r="11" fill="#252a33"/>')
    return (f'<g id="{cid}"><ellipse cx="510" cy="362" rx="520" ry="20" fill="#000" opacity="0.55"/>'
            '<path d="M24,262 Q18,205 70,192 L232,168 Q318,98 400,84 L628,82 Q706,88 790,162 L936,182 Q992,192 994,240 L996,268 Q996,290 972,292 L48,292 Q24,290 24,262 Z" fill="url(#pintura)"/>'
            '<path d="M262,166 Q330,104 404,96 L496,95 L496,166 Z" fill="url(#vidrio)"/><path d="M516,95 L622,94 Q690,100 756,164 L516,166 Z" fill="url(#vidrio)"/>'
            '<path d="M300,160 L380,104 L410,104 L330,160 Z M560,160 L620,100 L640,100 L580,160 Z" fill="#ffffff" opacity="0.10"/>'
            '<path d="M70,196 C300,176 700,178 990,206" stroke="#ffffff" stroke-width="3" opacity="0.35" fill="none"/>'
            '<path d="M40,226 C300,214 700,218 992,232" stroke="#ffffff" stroke-width="6" opacity="0.18" fill="none"/>'
            '<path d="M60,266 L960,266" stroke="#000" stroke-width="16" opacity="0.28"/>'
            '<path d="M506,170 L510,290 M262,172 Q256,230 262,290 M770,176 L764,288" stroke="#000" stroke-width="3" opacity="0.5" fill="none"/>'
            '<rect x="430" y="194" width="46" height="10" rx="5" fill="#2a0709" opacity="0.7"/><rect x="690" y="196" width="46" height="10" rx="5" fill="#2a0709" opacity="0.7"/>'
            '<path d="M950,200 L992,212 L990,234 L944,226 Z" fill="#eef4fa"/><path d="M26,214 L66,206 L62,234 L24,238 Z" fill="#c0222a"/>'
            '<path d="M758,150 L798,146 L806,172 L768,174 Z" fill="#8f1f25"/>'
            '<path d="M116,292 A88,88 0 0 1 292,292 Z M712,292 A88,88 0 0 1 888,292 Z" fill="#06080b"/>'
            + rueda_(204) + rueda_(800) + '</g>')

# ================================================================== 1) GANCHO: el coche arranca y derrapa fuera; cae la piedra y ESTALLA
f1e = FE(1)
CARX, IX, IY, TI = 330, 560, 1450, 2.95       # coche aparcado · punto de impacto (centro de la piedra al tocar el suelo) · instante
rr = random.Random(41)
humo = "".join(f'<circle class="humo1" cx="{CARX + 70 + k * 58}" cy="{1508 - (k % 3) * 8}" r="46" fill="url(#humoG)" opacity="0"/>' for k in range(10))
marca = f'<path id="marca1" d="M{CARX + 60},1532 C{CARX + 300},1530 {CARX + 520},1526 {CARX + 760},1530" stroke="#030406" stroke-width="12" fill="none" opacity="0.75" pathLength="1" stroke-dasharray="1" style="stroke-dashoffset:1"/>'
coche1 = (f'<g id="car1mov"><path id="haz1" d="M{CARX + 344},1484 L{CARX + 344},1500 L{CARX + 820},1580 L{CARX + 820},1420 Z" fill="url(#hazG)" opacity="0"/>'
          + coche_sil("car1", CARX, 1420, 1.05) + f'<circle id="freno1" cx="{CARX + 22}" cy="1496" r="34" fill="url(#frenoG)" opacity="0"/></g>')
shards = []
for k in range(20):
    s = rr.uniform(9, 30); n = rr.randint(5, 7)
    pts = " ".join(f"{IX + s * rr.uniform(0.55, 1.0) * math.cos(a):.0f},{IY + 40 + s * rr.uniform(0.55, 1.0) * math.sin(a):.0f}" for a in sorted(rr.uniform(0, 6.283) for _ in range(n)))
    shards.append((f'<polygon class="ast1" id="ast1_{k}" points="{pts}" fill="url(#hielo)" stroke="#ffffff" stroke-width="1.5" opacity="0"/>', s))
polvo = "".join(f'<circle class="polvo1" cx="{IX + dx}" cy="{1505 - dy}" r="70" fill="url(#polvoG)" opacity="0"/>' for dx, dy in ((0, 10), (-70, 0), (70, 4), (-30, 40), (40, 50), (-120, -6), (120, -4)))
resto = "".join(f'<ellipse class="resto1" cx="{IX + rr.uniform(-110, 110):.0f}" cy="{1532 + rr.uniform(-3, 8):.0f}" rx="{rr.uniform(5, 14):.0f}" ry="{rr.uniform(3, 6):.0f}" fill="#eaf6ff" opacity="0"/>' for _ in range(16))
bola1 = (f'<g id="bola1"><path d="M{IX - 14},{IY - 900} L{IX},{IY}" stroke="url(#estela)" stroke-width="120" stroke-linecap="round" opacity="0.35"/>'
         f'<circle cx="{IX}" cy="{IY}" r="82" fill="url(#hielo)"/><circle cx="{IX}" cy="{IY}" r="60" fill="none" stroke="#fff" stroke-width="3" opacity="0.25"/>'
         f'<circle cx="{IX}" cy="{IY}" r="38" fill="none" stroke="#fff" stroke-width="3" opacity="0.2"/><ellipse cx="{IX - 28}" cy="{IY - 30}" rx="22" ry="16" fill="#fff" opacity="0.9"/></g>')
e1 = ['<rect width="1080" height="1920" fill="url(#cieloNoche)"/>',
      '<g>' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="url(#nubeG)" opacity="{o}"/>' for x, y, rx, ry, o in
                       ((180, 260, 420, 170, 0.9), (760, 220, 480, 190, 0.95), (520, 420, 520, 160, 0.85), (980, 470, 300, 120, 0.8), (80, 520, 280, 110, 0.8))) + '</g>',
      '<rect id="relamp1" width="1080" height="1920" fill="#cfe2ff" opacity="0"/>',
      ciudad(3, 1500, 0.4), calle(1500, True, True), marca, humo, coche1,
      f'<ellipse id="onda1" cx="{IX}" cy="1532" rx="20" ry="5" fill="none" stroke="#ffffff" stroke-width="4" opacity="0"/>',
      resto, polvo, "".join(x for x, _ in shards), bola1, granizo("g1", 1, 1.3)]
escena("e1", "".join(e1))
mostrar("e1", 0, F(2))
camara("e1", 0, F(2), (0, 60, 1.18), (0, 0, 1.04), "power2.out")
caer("g1", 0, F(2))
J(f'tl.to("#mantoB", {{opacity:0.85, duration:{f1e:.2f}}}, 0.3);')
# el coche se enciende (mini arranque), tiembla al ralentí, acelera derrapando y sale del plano
J('tl.to("#freno1", {opacity:0.9, duration:0.12}, 0.85); tl.to("#haz1", {opacity:1, duration:0.06, yoyo:true, repeat:2}, 0.95); tl.set("#haz1", {opacity:1}, 1.15);')
J('tl.fromTo("#car1mov", {y:0}, {y:-2.5, duration:0.05, yoyo:true, repeat:11, ease:"none", immediateRender:false}, 0.9);')
FX.append(("arranque", 0.85))
J(f'tl.to("#car1mov", {{rotation:-2.5, svgOrigin:"{CARX + 88} 1535", duration:0.25, ease:"power2.out"}}, 1.5); tl.to("#car1mov", {{rotation:0, svgOrigin:"{CARX + 88} 1535", duration:0.4, ease:"sine.inOut"}}, 1.85);')
J('tl.to("#car1mov", {x:960, duration:1.15, ease:"power2.in"}, 1.5);')
J('tl.fromTo("#marca1", {strokeDashoffset:1}, {strokeDashoffset:0, duration:0.9, ease:"power2.in", immediateRender:false}, 1.5);')
J('tl.fromTo(".humo1", {opacity:0, scale:0.3, transformOrigin:"50% 50%"}, {opacity:0.6, scale:1.3, duration:0.3, stagger:0.08, ease:"power2.out", immediateRender:false}, 1.5);')
J('tl.to(".humo1", {opacity:0, scale:2.8, y:-60, duration:1.2, stagger:0.08, ease:"power1.out"}, 1.8);')
FX.append(("derrape", 1.5))
# la piedra cae justo donde estaba el coche y ESTALLA: trozos con parábola, polvo de hielo, onda y restos en el asfalto
J(f'tl.set("#bola1", {{opacity:0}}, 0); tl.set("#bola1", {{opacity:1}}, {TI - 0.95:.2f}); tl.fromTo("#bola1", {{y:-1900}}, {{y:0, duration:0.95, ease:"power2.in", immediateRender:false}}, {TI - 0.95:.2f}); tl.set("#bola1", {{opacity:0}}, {TI:.2f});')
for k, (_, s) in enumerate(shards):
    dx = rr.uniform(-460, 460); up = rr.uniform(140, 460) * (1.4 - s / 30); dy = 1532 - (IY + 40) - s * 0.4 + rr.uniform(-4, 6)
    tu = 0.28 + 0.12 * rr.random()
    J(f'tl.set("#ast1_{k}", {{opacity:1}}, {TI:.2f}); tl.fromTo("#ast1_{k}", {{x:0}}, {{x:{dx:.0f}, duration:{tu * 2.6:.2f}, ease:"power1.out", immediateRender:false}}, {TI:.2f});'
      f'tl.fromTo("#ast1_{k}", {{y:0}}, {{y:{-up:.0f}, duration:{tu:.2f}, ease:"power2.out", immediateRender:false}}, {TI:.2f}); tl.to("#ast1_{k}", {{y:{dy:.0f}, duration:{tu * 1.3:.2f}, ease:"bounce.out"}}, {TI + tu:.2f});'
      f'tl.fromTo("#ast1_{k}", {{rotation:0}}, {{rotation:{rr.uniform(-420, 420):.0f}, transformOrigin:"50% 50%", duration:{tu * 2.6:.2f}, ease:"power1.out", immediateRender:false}}, {TI:.2f});')
J(f'tl.fromTo(".polvo1", {{opacity:0.85, scale:0.25, transformOrigin:"50% 50%"}}, {{opacity:0, scale:3.2, y:-70, duration:1.4, stagger:0.03, ease:"power2.out", immediateRender:false}}, {TI:.2f});')
J(f'tl.fromTo("#onda1", {{opacity:0.9, attr:{{rx:20, ry:5}}}}, {{opacity:0, attr:{{rx:330, ry:46}}, duration:0.7, ease:"power2.out", immediateRender:false}}, {TI:.2f});')
J(f'tl.to(".resto1", {{opacity:0.9, duration:0.15, stagger:0.02}}, {TI + 0.05:.2f});')
J(f'tl.to("#e1", {{x:14, y:-9, duration:0.05}}, {TI:.2f}); tl.to("#e1", {{x:-10, y:7, duration:0.05}}, {TI + 0.05:.2f}); tl.to("#e1", {{x:5, y:-3, duration:0.05}}, {TI + 0.1:.2f}); tl.to("#e1", {{x:0, y:0, duration:0.08}}, {TI + 0.15:.2f});')
FX.append(("impacto", TI))
J('tl.to("#relamp1", {opacity:0.3, duration:0.05, yoyo:true, repeat:1}, 4.3);')
OVR.append('<div id="titulo"><div class="t0">¿Y SI GRANIZARA</div><div class="t1"><span>30</span> DÍAS SEGUIDOS?</div></div>')
J('tl.fromTo("#titulo .t0", {y:16}, {y:0, duration:0.35, ease:"power3.out", immediateRender:false}, 0);')
J('tl.fromTo("#titulo .t1", {y:16}, {y:0, duration:0.35, ease:"power3.out", immediateRender:false}, 0.08);')
J(f'tl.to("#titulo", {{opacity:0, y:-40, duration:0.35, ease:"power2.in"}}, {F(2) - 0.4:.2f});')
# ================================================================== 2) CUÁNTO DURA: tormenta real sobre el campo → la cámara entra en la nube
f2 = F(2); barrido(f2)
CX2, YB2, YT2 = 560, 1130, 560
TC2 = P("cada") - 0.15                       # empuje de cámara hacia dentro de la nube
ups = "".join(f'<path class="up2" d="M{x},1125 C{x - 14},1010 {x + 14},880 {x},770" stroke="{AMB}" stroke-width="5" fill="none" stroke-linecap="round" stroke-dasharray="18 12"/>'
              f'<path d="M{x - 9},784 L{x},764 L{x + 9},784" stroke="{AMB}" stroke-width="5" fill="none" stroke-linejoin="round"/>' for x in (530, 565, 600))
dn = (f'<path class="dn2" d="M735,800 C748,900 722,1000 735,1110" stroke="#7cc4ff" stroke-width="4" fill="none" stroke-linecap="round" stroke-dasharray="14 10"/>'
      f'<path d="M727,1096 L735,1114 L743,1096" stroke="#7cc4ff" stroke-width="4" fill="none" stroke-linejoin="round"/>')
dentro2 = (f'<rect id="rx2" x="0" y="0" width="1080" height="1920" fill="#14203a" opacity="0"/>'
           f'<g id="int2" opacity="0"><path d="M300,905 L830,905" stroke="{ICE}" stroke-width="1.6" stroke-dasharray="6 5" opacity="0.8"/>'
           f'<text x="420" y="898" font-family="Inter" font-weight="800" font-size="15" fill="{ICE}">0 °C</text>{ups}{dn}</g>')
nube2, _, _ = cumulo("n2", CX2, YB2, YT2, 300, 5, "tLuz", "tAlto", sombra="#0e1422", dentro=dentro2)
ch2, H2 = chorro("cho2", 440, 720, YB2, 1500, 50, 3)
rr = random.Random(55)
campo2 = ('<path d="M-300,1500 L1380,1500 L1380,2400 L-300,2400 Z" fill="url(#sueloCampo)"/>'
          '<path d="M-300,1500 C0,1478 200,1490 420,1480 C640,1470 860,1488 1380,1478 L1380,1508 L-300,1508 Z" fill="#26341f"/>'
          + "".join(f'<circle cx="{x}" cy="{1494 - rr.randint(0, 6)}" r="{rr.randint(10, 18)}" fill="#1c2818"/>' for x in range(-200, 1300, 23))
          + "".join(f'<g><rect x="{x}" y="1470" width="26" height="18" fill="#c9c0b0"/><path d="M{x - 3},1471 L{x + 13},1460 L{x + 29},1471 Z" fill="#8a3b2a"/></g>' for x in (840, 872, 905, 950, 986))
          + "".join(f'<path d="M{-300 + i * 260},2400 L540,1505" stroke="#1d2a17" stroke-width="5" opacity="0.6"/>' for i in range(8)))
rayo2 = '<path id="rayo2" d="M800,1105 L786,1190 L812,1214 L790,1300 L820,1330 L804,1420 L826,1500" stroke="#eef4ff" stroke-width="5" fill="none" stroke-linejoin="round" opacity="0"/>'
pts2 = [(560, 1105), (565, 960), (575, 805), (650, 775), (712, 850), (722, 1000), (690, 1090), (612, 1100), (565, 965), (572, 800), (660, 780), (722, 905), (712, 1060), (705, 1140), (708, 1320)]
cur2 = suave(pts2, 6)
traza2 = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in cur2)
e2 = ['<rect width="1080" height="1920" fill="url(#cieloTorm)"/>', campo2, ch2, rayo2, nube2,
      f'<path id="traza2" d="{traza2}" stroke="{ICE}" stroke-width="2" fill="none" opacity="0.7" pathLength="1" stroke-dasharray="1" style="stroke-dashoffset:1"/>',
      '<g id="pl2"><circle r="9" fill="url(#hielo)"/><circle r="6" fill="none" stroke="#fff" stroke-width="1" opacity="0.4"/><circle cx="-3" cy="-3" r="2.5" fill="#fff" opacity="0.9"/></g>']
escena("e2", "".join(e2))
mostrar("e2", f2, F(3))
camara("e2", f2, TC2, (0, 30, 1.0), (0, 0, 1.04), "sine.out")
S2 = 2.2
J(f'tl.to("#e2-cam", {{x:{-S2 * (CX2 - 540):.0f}, y:{-S2 * (880 - 960):.0f}, scale:{S2}, duration:0.95, ease:"power3.inOut"}}, {TC2:.2f});')
FX.append(("whoosh", TC2 + 0.1))
J(f'tl.to("#cho2", {{opacity:1, duration:0.6}}, {f2 + 0.2:.2f});'); mover_chorro("cho2", H2, f2, F(3))
for tr in (f2 + 0.9, P("minutos") + 0.2):
    J(f'tl.to("#rayo2", {{opacity:1, duration:0.04, yoyo:true, repeat:3}}, {tr:.2f}); tl.to("#n2flash", {{opacity:0.45, duration:0.05, yoyo:true, repeat:3}}, {tr:.2f});')
FX.append(("trueno", f2 + 0.9))
J(f'tl.to("#rx2", {{opacity:0.62, duration:0.5}}, {TC2 + 0.4:.2f}); tl.to("#int2", {{opacity:1, duration:0.5}}, {TC2 + 0.5:.2f}); tl.set("#cho2", {{opacity:0}}, {TC2 + 0.6:.2f});')
J(f'tl.fromTo(".up2", {{strokeDashoffset:0}}, {{strokeDashoffset:-150, duration:{F(3) - TC2:.2f}, ease:"none", immediateRender:false}}, {TC2:.2f});')
J(f'tl.fromTo(".dn2", {{strokeDashoffset:0}}, {{strokeDashoffset:120, duration:{F(3) - TC2:.2f}, ease:"none", immediateRender:false}}, {TC2:.2f});')
# la piedra sube y baja por la nube, ganando capas (crece), y cae cuando pesa demasiado
t0s, t1s = P("piedra") - 0.1, P("demasiado") - 0.15
nub = len(cur2) - 7
dt = (t1s - t0s) / nub
J(f'tl.set("#pl2", {{x:{cur2[0][0]:.0f}, y:{cur2[0][1]:.0f}, scale:0.55, opacity:0}}, 0); tl.set("#pl2", {{opacity:1}}, {t0s:.2f});')
for k in range(1, len(cur2)):
    x, y = cur2[k]
    if k <= nub:
        J(f'tl.to("#pl2", {{x:{x:.0f}, y:{y:.0f}, scale:{0.55 + 1.0 * k / nub:.2f}, duration:{dt:.3f}, ease:"none"}}, {t0s + (k - 1) * dt:.3f});')
    else:
        J(f'tl.to("#pl2", {{x:{x:.0f}, y:{y:.0f}, duration:{0.09 * (1.2 - (k - nub) / 8):.3f}, ease:"none"}}, {t1s + (k - nub - 1) * 0.08:.3f});')
J(f'tl.to("#traza2", {{strokeDashoffset:{1 - nub / (len(cur2) - 1):.3f}, duration:{t1s - t0s:.2f}, ease:"none"}}, {t0s:.2f}); tl.to("#traza2", {{strokeDashoffset:0, duration:0.5, ease:"power2.in"}}, {t1s:.2f});')
FX.append(("baja", t1s))
OVR.append(f'<div id="dur2" class="panel durp"><svg width="140" height="140" viewBox="-70 -70 140 140"><circle r="62" fill="#0b1626" stroke="#4a6080" stroke-width="4"/>'
           + "".join(f'<path d="M{54 * math.cos(a):.1f},{54 * math.sin(a):.1f} L{62 * math.cos(a):.1f},{62 * math.sin(a):.1f}" stroke="#8796ad" stroke-width="3"/>' for a in [k * math.pi / 6 for k in range(12)])
           + f'<circle id="sec2" r="26" fill="none" stroke="{ICE}" stroke-width="52" opacity="0.35" pathLength="1" stroke-dasharray="1" transform="rotate(-90)" style="stroke-dashoffset:1"/>'
           f'<path id="man2" d="M0,0 L0,-48" stroke="{INK}" stroke-width="5" stroke-linecap="round"/><circle r="6" fill="{INK}"/></svg>'
           '<div><div class="pt">DURACIÓN HABITUAL</div><div class="dv">unos minutos</div><div class="ds2">en un mismo lugar</div></div></div>')
pop("#dur2", P("granizada") - 0.2, 0.4, "opacity:0, x:-30")
J(f'tl.to("#sec2", {{strokeDashoffset:0.8, duration:1.4, ease:"power2.inOut"}}, {P("dura"):.2f}); tl.fromTo("#man2", {{rotation:0}}, {{rotation:72, svgOrigin:"0 0", duration:1.4, ease:"power2.inOut", immediateRender:false}}, {P("dura"):.2f});')
fuera("#dur2", TC2)
chip("CORRIENTE ASCENDENTE", P("sube") - 0.2, F(3) - 0.1, 60, 1500, AMB)
chip("CORRIENTE DESCENDENTE", P("baja") - 0.1, F(3) - 0.1, 60, 1584, "#7cc4ff")
OVR.append('<div id="corte2" class="panel cortep"><svg width="250" height="250" viewBox="-125 -125 250 250">'
           + "".join(f'<circle class="capa2" r="{r}" fill="{c}" stroke="#ffffff" stroke-opacity="0.5" stroke-width="1.5"/>' for r, c in ((112, "#eef8ff"), (92, "#a9cfe8"), (72, "#eef8ff"), (52, "#a9cfe8"), (32, "#eef8ff"), (14, "#c7e2f4")))
           + '<ellipse cx="-38" cy="-46" rx="26" ry="16" fill="#fff" opacity="0.7"/></svg><div class="pt">CORTE DE UNA PIEDRA</div><div class="dv2">capas de hielo</div></div>')
pop("#corte2", P("capas") - 0.3, 0.45, "opacity:0, x:-30")
J(f'tl.fromTo(".capa2", {{scale:0}}, {{scale:1, svgOrigin:"0 0", duration:0.45, stagger:0.12, ease:"back.out(1.6)", immediateRender:false}}, {P("capas") - 0.2:.2f});')
fuera("#corte2", F(3) - 0.1)
fuente("Fuente: NOAA · Servicio Meteorológico de EE. UU.", P("capas"), F(3) - 0.1)
# ================================================================== 3) DÍA 1: la ciudad amanece blanca + capó abollado
f3 = F(3); barrido(f3)
J(f'tl.to("#hud", {{opacity:1, duration:0.4}}, {f3 + 0.2:.2f});'); dia(f3 + 0.25, 1)
e3 = ['<rect width="1080" height="1920" fill="url(#cieloAlba)"/>',
      '<g>' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="url(#nubeG)" opacity="0.85"/>' for x, y, rx, ry in ((200, 300, 420, 140), (820, 260, 460, 160))) + '</g>',
      ciudad(7, 1380, 0.25, "#26324a", "#1b263a", True),
      '<rect x="0" y="1380" width="1080" height="540" fill="url(#mantoG)"/>', "".join(piedra(random.Random(k).uniform(0, 1080), 1390 + random.Random(k + 99).uniform(0, 520) ** 1.0, random.Random(k + 7).uniform(4, 11), False, 0.9) for k in range(120)),
      '<g>' + "".join(f'<circle class="onda3" cx="{x}" cy="{y}" r="10" fill="none" stroke="#ffffff" stroke-width="3"/>' for x, y in ((140, 820), (420, 700), (700, 760), (960, 720), (300, 900), (860, 880))) + '</g>',
      granizo("g3", 3, 0.8)]
escena("e3", "".join(e3))
tc = P("coches")
mostrar("e3", f3, tc - 0.05)
camara("e3", f3, tc, (-40, 0, 1.06), (40, 0, 1.06))
caer("g3", f3, tc)
J(f'tl.fromTo(".onda3", {{attr:{{r:6}}, opacity:0.9}}, {{attr:{{r:70}}, opacity:0, duration:0.6, stagger:0.17, repeat:{max(1, int((tc - P("tejados")) / 1.0))}, ease:"power1.out", immediateRender:false}}, {P("tejados") - 0.2:.2f}); tl.set(".onda3", {{opacity:0}}, 0);')
OVR.append('<div id="db3" class="panel"><div class="pt">RUIDO SOBRE LOS TEJADOS</div><div class="barras">' + "".join(f'<i class="bd" style="height:{h}px"></i>' for h in (30, 50, 70, 90, 110, 130, 150, 170, 190, 210)) + '</div><div class="pv">golpes continuos, como una percusión</div></div>')
pop("#db3", P("tejados"), 0.45)
J(f'tl.fromTo("#db3 .bd", {{scaleY:0.1}}, {{scaleY:1, transformOrigin:"50% 100%", duration:0.18, stagger:0.04, yoyo:true, repeat:{max(1, int((tc - P("tejados")) / 0.5))}, ease:"power1.inOut", immediateRender:false}}, {P("tejados"):.2f});')
fuera("#db3", tc - 0.15)
rr = random.Random(9)
CXO, CYO = 40, 1060                          # coche: esquina del dibujo en la escena
fachada = ('<rect width="1080" height="1920" fill="url(#cieloGris)"/>'
           '<rect x="-300" y="380" width="1700" height="1000" fill="#262c38"/>'
           + "".join(f'<rect x="{x}" y="{y}" width="150" height="190" fill="#1a1f29"/><rect x="{x + 8}" y="{y + 8}" width="134" height="174" fill="{c}" opacity="0.85"/><rect x="{x - 10}" y="{y + 190}" width="170" height="12" fill="#3a4250"/>'
                     for x, y, c in ((-60, 470, "#3c4a60"), (200, 470, "#ffcf7a"), (460, 470, "#3c4a60"), (720, 470, "#3c4a60"), (980, 470, "#ffd99a"), (-60, 760, "#3c4a60"), (200, 760, "#3c4a60"), (460, 760, "#ffcf7a"), (720, 760, "#3c4a60"), (980, 760, "#3c4a60")))
           + '<rect x="-300" y="1040" width="1700" height="300" fill="#1e232d"/>'
           + "".join(f'<path d="M{x},1060 L{x},1330" stroke="#2c3340" stroke-width="3"/>' for x in range(-280, 1400, 22))
           + '<rect x="-300" y="1330" width="1700" height="40" fill="#3a4250"/>'
           '<rect x="-300" y="1366" width="1700" height="600" fill="url(#mantoG)"/>')
abol, rebotes, t_ab = [], [], []
sitios = [(470, 92), (560, 90), (380, 100), (860, 178), (920, 190), (820, 172), (330, 186), (420, 200), (600, 196), (700, 204), (880, 214), (240, 206), (520, 224), (660, 232), (780, 222), (150, 214)]
for k, (lx, ly) in enumerate(sitios):
    x, y, r = CXO + lx, CYO + ly, rr.randint(13, 22)
    abol.append(f'<g class="abol" id="ab{k}" opacity="0"><ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 0.62:.0f}" fill="url(#abolG)"/>'
                f'<path d="M{x - r * 0.8:.0f},{y - r * 0.1:.0f} A{r * 0.8:.0f},{r * 0.5:.0f} 0 0 1 {x + r * 0.5:.0f},{y - r * 0.45:.0f}" stroke="#ffffff" stroke-width="2.5" fill="none" opacity="0.55"/>'
                f'<ellipse cx="{x + r * 0.35:.0f}" cy="{y + r * 0.25:.0f}" rx="{r * 0.35:.0f}" ry="{r * 0.16:.0f}" fill="#ffd2d2" opacity="0.35"/></g>')
    rebotes.append(f'<g id="rb{k}" opacity="0">{piedra(x, y - 10, rr.uniform(7, 11), False)}</g>')
hielo_coche = "".join(f'<ellipse cx="{CXO + x}" cy="{CYO + y}" rx="{rr.randint(4, 9)}" ry="3" fill="#eef7ff" opacity="0.9"/>'
                      for x, y in [(rr.uniform(260, 760), 84 + rr.uniform(0, 6)) for _ in range(24)] + [(rr.uniform(800, 960), 176 + rr.uniform(0, 8)) for _ in range(12)])
e3b = [fachada, f'<g transform="translate({CXO},{CYO})">{coche_det("car3")}</g>', f'<g id="nev3" opacity="0">{hielo_coche}</g>', "".join(abol), "".join(rebotes),
       "".join(piedra(rr.uniform(-100, 1180), 1380 + rr.uniform(0, 400), rr.uniform(4, 9), False, 0.9) for _ in range(70)), granizo("g3b", 13, 0.7)]
escena("e3b", "".join(e3b))
mostrar("e3b", tc - 0.05, F(4))
PX, PY, PS = 780, 1230, 1.5                  # la cámara se acerca al capó y la puerta delantera
camara("e3b", tc - 0.05, F(4), (0, 0, 1.0), (-PS * (PX - 540), -PS * (PY - 960), PS), "power2.inOut")
caer("g3b", tc, F(4))
J(f'tl.to("#nev3", {{opacity:1, duration:1.5}}, {tc:.2f});')
orden = list(range(len(sitios))); random.Random(3).shuffle(orden)
for j, k in enumerate(orden):
    t = tc + 0.15 + j * 0.13
    J(f'tl.set("#rb{k}", {{opacity:1}}, {t - 0.2:.2f}); tl.fromTo("#rb{k}", {{y:-420, x:0}}, {{y:0, duration:0.2, ease:"power2.in", immediateRender:false}}, {t - 0.2:.2f});'
      f'tl.to("#rb{k}", {{y:{-70 - (j % 3) * 25}, x:{40 + (j % 4) * 20}, opacity:0, duration:0.35, ease:"power2.out"}}, {t:.2f}); tl.to("#ab{k}", {{opacity:1, duration:0.06}}, {t:.2f});')
    if j % 3 == 0:
        FX.append(("clic", t))
chip("COCHES APARCADOS: ABOLLADURAS", P("abolladuras") - 0.4, F(4) - 0.1, 60, 640, AMB)
# ================================================================== 4) DÍA 3: el campo + mapa de España
f4 = F(4); dia(f4 + 0.1, 3)
t25 = P("2025")
HZ = 1000                                    # horizonte del campo en perspectiva
rr = random.Random(44)
def maiz():
    g = rr.choice(("#4f8a3c", "#437c34", "#5a9644", "#3f7a36"))
    hojas = ""
    for i in range(5):
        h = 55 + i * 42; lado = -1 if (i + rr.randint(0, 1)) % 2 else 1; L = rr.uniform(95, 135) * (1 - 0.1 * i)
        hojas += (f'<path class="hj4" d="M0,{-h} C{lado * L * 0.4:.0f},{-h - 34:.0f} {lado * L * 0.8:.0f},{-h - 14:.0f} {lado * L:.0f},{-h + 26:.0f} '
                  f'C{lado * L * 0.7:.0f},{-h - 2:.0f} {lado * L * 0.35:.0f},{-h - 6:.0f} 0,{-h + 12} Z" fill="{g}"/>')
    return (f'<path class="tl4" d="M0,0 L0,-272" stroke="#3d6b2c" stroke-width="9" stroke-linecap="round"/>{hojas}'
            '<path d="M0,-272 l-14,-40 M0,-272 l0,-48 M0,-272 l14,-38" stroke="#c9b25a" stroke-width="4" stroke-linecap="round"/>')
zs, z = [], 7.0
while z > 0.33:
    zs.append(z); z /= 1.17
plantas = []
for z in zs:
    y, s = HZ + 240 / z, 0.32 / z
    for i in range(-16, 17):
        if z > 3 and i % 2:
            continue
        x = 540 + i * 0.55 * 150 / z + rr.uniform(-5, 5) * min(1, 1 / z)
        if -160 < x < 1240:
            plantas.append(f'<g transform="translate({x:.0f},{y:.0f}) scale({s:.3f})"><g class="pl4r">{maiz()}</g></g>')
surcos = "".join(f'<path class="sur4" d="M{540 + (i + 0.5) * 0.55 * 150 / 7:.0f},{HZ + 34} L{540 + (i + 0.5) * 0.55 * 150 / 0.2:.0f},{HZ + 1200}" stroke="#ffffff" stroke-width="{14}" opacity="0"/>' for i in range(-16, 16))
fondo4 = ('<rect width="1080" height="1920" fill="url(#cieloTorm)"/>'
          + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#1a2232" opacity="{o}"/>' for x, y, rx, ry, o in ((120, 640, 420, 140, 0.8), (720, 600, 520, 160, 0.85), (420, 760, 600, 110, 0.6)))
          + f'<path d="M-50,{HZ + 10} C150,{HZ - 70} 330,{HZ - 40} 500,{HZ - 20} C700,{HZ - 75} 900,{HZ - 50} 1130,{HZ - 10} L1130,{HZ + 40} L-50,{HZ + 40} Z" fill="#33452f"/>'
          + "".join(f'<ellipse cx="{x}" cy="{HZ - 6}" rx="{rx}" ry="{rx * 1.8:.0f}" fill="#22311f"/>' for x, rx in ((90, 14), (118, 12), (150, 15), (640, 13), (668, 11), (960, 16)))
          + f'<g><rect x="780" y="{HZ - 44}" width="78" height="44" fill="#cfc4b2"/><path d="M772,{HZ - 42} L819,{HZ - 72} L866,{HZ - 42} Z" fill="#8a2f22"/><rect x="866" y="{HZ - 78}" width="26" height="78" fill="#9aa3ad"/>'
          f'<ellipse cx="879" cy="{HZ - 78}" rx="13" ry="6" fill="#b9c1ca"/><rect x="806" y="{HZ - 24}" width="14" height="24" fill="#3a2a1c"/></g>'
          + "".join(f'<path d="M{x},{HZ + 20} L{x},{HZ + 20 - h}" stroke="#2a2f36" stroke-width="{w}"/>' for x, h, w in ((40, 120, 6), (230, 60, 4), (330, 38, 3)))
          + f'<path d="M40,{HZ - 92} Q140,{HZ - 30} 230,{HZ - 52} Q290,{HZ - 18} 330,{HZ - 14}" stroke="#2a2f36" stroke-width="2" fill="none"/>'
          + f'<rect x="-300" y="{HZ + 30}" width="1700" height="1000" fill="url(#sueloCampo)"/>')
trozos = "".join(f'<ellipse class="tr4" cx="{rr.uniform(60, 1020):.0f}" cy="{rr.uniform(1150, 1650):.0f}" rx="{rr.uniform(6, 14):.0f}" ry="{rr.uniform(3, 6):.0f}" fill="{rr.choice(("#4f8a3c", "#6aa04a", "#8a7a3a"))}" opacity="0"/>' for _ in range(40))
e4 = [fondo4, surcos, "".join(plantas), trozos, granizo("g4", 4, 1.0)]
escena("e4", "".join(e4))
mostrar("e4", f4, t25 - 0.05)
camara("e4", f4, t25, (0, -30, 1.0), (0, 30, 1.12))
caer("g4", f4, t25)
J(f'tl.to("#e4 .sur4", {{opacity:0.55, duration:{t25 - f4:.2f}, ease:"power1.in"}}, {f4:.2f});')
tp = P("perdido")
J(f'tl.to("#e4 .pl4r", {{rotation:(i) => ((i % 2) ? 1 : -1) * (30 + (i * 37 % 45)), svgOrigin:"0 0", duration:1.1, stagger:{{each:0.0012, from:"random"}}, ease:"power2.in"}}, {tp - 0.6:.2f});')
J(f'tl.to("#e4 .hj4", {{fill:"#8b7b3e", duration:1.0, stagger:{{each:0.0003, from:"random"}}}}, {tp - 0.4:.2f}); tl.to("#e4 .tl4", {{stroke:"#7a6a36", duration:1.0}}, {tp - 0.4:.2f});')
J(f'tl.set(".tr4", {{opacity:1}}, {tp - 0.5:.2f}); tl.to(".tr4", {{y:(i) => 120 + (i * 53 % 160), x:(i) => -40 - (i * 31 % 120), rotation:(i) => i * 47 % 360, opacity:0, duration:1.3, stagger:0.02, ease:"power1.in"}}, {tp - 0.5:.2f});')
FX.append(("baja", tp - 0.2))
m = json.load(open(os.path.join(BASE, "..", "vox29n", "espana.json")))
dan = {"castile-and-leon": 0.9, "aragon": 0.8, "castile-la-mancha": 0.85, "navarre": 0.7, "la-rioja": 0.9, "catalonia": 0.6, "valencia": 0.5, "extremadura": 0.5, "murcia": 0.4, "andalusia": 0.45}
regs = "".join(f'<path d="{l["path"]}" fill="#1a2840" stroke="#3a5070" stroke-width="1.4"/>'
               + (f'<path class="dz" d="{l["path"]}" fill="{AMB if dan[l["id"]] < 0.7 else RED}" opacity="0" data-o="{dan[l["id"]] * 0.75:.2f}"/>' if l["id"] in dan else "")
               for l in m["locations"] if l["id"] != "canary-islands")
e4b = ['<rect width="1080" height="1920" fill="url(#fondoTec)"/>', '<rect width="1080" height="1920" fill="url(#rejilla)" opacity="0.4"/>',
       f'<svg x="40" y="560" width="1000" height="887" viewBox="0 0 613 544">{regs}</svg>']
escena("e4b", "".join(e4b))
mostrar("e4b", t25 - 0.05, F(5))
camara("e4b", t25 - 0.05, F(5), (0, 30, 1.0), (0, 0, 1.06))
J(f'tl.to("#e4b .dz", {{opacity:(i, el) => +el.getAttribute("data-o"), duration:0.5, stagger:0.12, ease:"power2.out"}}, {P("danaron") - 0.1:.2f});')
OVR.append(f'<div id="ha4" class="dato"><div class="dn">{rueda("ha4n", "1.000.000", 120, INK)}</div><div class="dt">HECTÁREAS DE CULTIVO DAÑADAS</div><div class="ds">Tormentas en España · 2025</div></div>')
pop("#ha4", P("millon") - 0.5, 0.45)
gira("ha4n", "1.000.000", P("millon") - 0.4, 1.1)
for k in range(6):
    FX.append(("clic", P("millon") - 0.4 + k * 0.16))
fuera("#ha4", F(5) - 0.1)
fuente("Fuente: Agroseguro (2025) · zonas ilustrativas", P("hectareas"), F(5) - 0.1)

# ================================================================== 5) PRECIOS: gráfica + tabla
f5 = F(5)
e5 = ['<rect width="1080" height="1920" fill="url(#fondoTec)"/>', '<rect width="1080" height="1920" fill="url(#rejilla)" opacity="0.4"/>',
      '<path d="M120,1100 L960,1100 M120,1100 L120,600" stroke="#33445f" stroke-width="3"/>',
      f'<path id="curva5" d="M120,1040 C260,1036 380,1030 480,1010 C600,980 700,860 780,760 C840,690 900,640 960,610" stroke="{RED}" stroke-width="9" fill="none" stroke-linecap="round" pathLength="1" stroke-dasharray="1" style="stroke-dashoffset:1"/>',
      f'<path id="area5" d="M120,1040 C260,1036 380,1030 480,1010 C600,980 700,860 780,760 C840,690 900,640 960,610 L960,1100 L120,1100 Z" fill="url(#areaRoja)" opacity="0"/>',
      '<text x="120" y="1150" font-family="Inter" font-weight="700" font-size="26" fill="#8796ad">DÍA 1</text><text x="960" y="1150" text-anchor="end" font-family="Inter" font-weight="700" font-size="26" fill="#8796ad">DÍA 7</text>'
      '<text x="960" y="580" text-anchor="end" font-family="Inter" font-weight="800" font-size="28" fill="#c9d8ea">PRECIO DE FRUTA Y VERDURA</text>']
escena("e5", "".join(e5))
mostrar("e5", f5, F(6))
camara("e5", f5, F(6), (0, 0, 1.0), (-20, 0, 1.05))
J(f'tl.to("#curva5", {{strokeDashoffset:0, duration:2.2, ease:"power2.in"}}, {f5 + 0.3:.2f}); tl.to("#area5", {{opacity:0.5, duration:1.0}}, {f5 + 1.2:.2f});')
filas5 = (("Fruta", "1,80 €", "3,40 €"), ("Verdura", "1,20 €", "2,60 €"), ("Hortalizas", "1,50 €", "2,90 €"))
OVR.append('<div id="tab5" class="panel tabla">' + "".join(f'<div class="fila"><span>{a}</span><span class="pv5"><s>{b}</s><b>{c}</b></span><span class="flecha">▲</span></div>' for a, b, c in filas5)
           + '<div class="nota5">Precios ilustrativos · escenario hipotético</div></div>')
pop("#tab5", f5 + 0.2, 0.45)
J(f'tl.set("#tab5 b, #tab5 .flecha", {{opacity:0}}, 0); tl.to("#tab5 b, #tab5 .flecha", {{opacity:1, duration:0.2, stagger:0.12}}, {P("disparan") - 0.2:.2f}); tl.to("#tab5 s", {{opacity:0, duration:0.2, stagger:0.12}}, {P("disparan") - 0.2:.2f});')
FX.append(("sube2", P("disparan") - 0.3))
fuera("#tab5", F(6) - 0.1)

# ================================================================== 6) SEMANA: placas solares + panel de salidas
f6 = F(6); dia(f6 + 0.1, 7)
ta = P("aviones")
rr = random.Random(4)
def bil(c, u, v):
    """Punto (u,v) de la cara del tejado: c = (x0,x1 alero; xt0,xt1 cumbrera; y alero; y cumbrera)."""
    x0, x1, xt0, xt1, ya, yc = c
    xl, xr = x0 + (xt0 - x0) * v, x1 + (xt1 - x1) * v
    return xl + (xr - xl) * u, ya + (yc - ya) * v
def tejado(c, cls=""):
    x0, x1, xt0, xt1, ya, yc = c
    s = [f'<polygon points="{x0},{ya} {xt0},{yc} {xt1},{yc} {x1},{ya}" fill="url(#tejaG)"/>']
    n = 12
    for k in range(1, n):
        v = 1 - (k / n) ** 1.15
        a, b = bil(c, 0, v), bil(c, 1, v)
        s.append(f'<path d="M{a[0]:.0f},{a[1]:.0f} L{b[0]:.0f},{b[1]:.0f}" stroke="#4a1a10" stroke-width="3" opacity="0.55"/>')
        for u in [j / 16 + (0.03 if k % 2 else 0) for j in range(1, 16)]:
            p, q = bil(c, u, v), bil(c, u, v + 0.035)
            s.append(f'<path d="M{p[0]:.0f},{p[1]:.0f} L{q[0]:.0f},{q[1]:.0f}" stroke="#4a1a10" stroke-width="2" opacity="0.35"/>')
    s.append(f'<path d="M{x0},{ya} L{xt0},{yc} M{x1},{ya} L{xt1},{yc}" stroke="#5a2216" stroke-width="7"/><path d="M{xt0},{yc} L{xt1},{yc}" stroke="#5a2216" stroke-width="9"/>')
    s.append(f'<rect x="{x0 - 6}" y="{ya - 4}" width="{x1 - x0 + 12}" height="18" fill="#e8e2d6"/><rect x="{x0 - 6}" y="{ya + 14}" width="{x1 - x0 + 12}" height="8" fill="#000" opacity="0.25"/>')
    return "".join(s)
def placa(c, u0, u1, v0, v1, pid):
    q = [bil(c, u0, v0), bil(c, u1, v0), bil(c, u1, v1), bil(c, u0, v1)]
    pts = " ".join(f"{x:.0f},{y:.0f}" for x, y in q)
    s = [f'<polygon points="{" ".join(f"{x + 6:.0f},{y + 8:.0f}" for x, y in q)}" fill="#000" opacity="0.35"/>',
         f'<polygon id="{pid}" points="{pts}" fill="url(#panelG)" stroke="#c9d2dc" stroke-width="4" stroke-linejoin="round"/>']
    for k in range(1, 6):
        u = u0 + (u1 - u0) * k / 6; a, b = bil(c, u, v0), bil(c, u, v1)
        s.append(f'<path d="M{a[0]:.0f},{a[1]:.0f} L{b[0]:.0f},{b[1]:.0f}" stroke="#5f80b0" stroke-width="1.6" opacity="0.7"/>')
    for k in range(1, 4):
        v = v0 + (v1 - v0) * k / 4; a, b = bil(c, u0, v), bil(c, u1, v)
        s.append(f'<path d="M{a[0]:.0f},{a[1]:.0f} L{b[0]:.0f},{b[1]:.0f}" stroke="#5f80b0" stroke-width="1.6" opacity="0.7"/>')
    du = u1 - u0
    g = [bil(c, u0 + du * 0.55, v0), bil(c, u0 + du * 0.75, v0), bil(c, u0 + du * 0.35, v1), bil(c, u0 + du * 0.15, v1)]
    s.append(f'<polygon points="{" ".join(f"{x:.0f},{y:.0f}" for x, y in g)}" fill="#ffffff" opacity="0.13"/>')
    cx, cy = bil(c, u0 + du * rr.uniform(0.3, 0.7), v0 + (v1 - v0) * rr.uniform(0.3, 0.7))
    L = min(abs(q[1][0] - q[0][0]), abs(q[3][1] - q[0][1])) * 0.48
    ray = ""
    for a in [rr.uniform(0, 6.283) for _ in range(8)]:
        x, y, d = cx, cy, f"M{cx:.0f},{cy:.0f}"
        for st in range(3):
            a2 = a + rr.uniform(-0.35, 0.35); x += L / 3 * math.cos(a2); y += L / 3 * math.sin(a2) * 0.8; d += f" L{x:.0f},{y:.0f}"
        ray += d + " "
    s.append(f'<g class="crack6" opacity="0"><polygon points="{pts}" fill="#05080f" opacity="0.35"/><path d="{ray}" stroke="#ffffff" stroke-width="2.4" fill="none" opacity="0.95"/>'
             f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="9" fill="#ffffff" opacity="0.9"/><circle cx="{cx:.0f}" cy="{cy:.0f}" r="{L * 0.25:.0f}" fill="none" stroke="#ffffff" stroke-width="1.6" opacity="0.7"/></g>')
    return "".join(s)
def ventana(x, y, w, h, luz=False):
    return (f'<rect x="{x - 26}" y="{y}" width="24" height="{h}" fill="#3d5a3a"/><rect x="{x + w + 2}" y="{y}" width="24" height="{h}" fill="#3d5a3a"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#f2efe8"/><rect x="{x + 8}" y="{y + 8}" width="{w - 16}" height="{h - 16}" fill="{"#ffcf7a" if luz else "url(#cristalG)"}"/>'
            f'<path d="M{x + w / 2},{y + 8} L{x + w / 2},{y + h - 8} M{x + 8},{y + h / 2} L{x + w - 8},{y + h / 2}" stroke="#f2efe8" stroke-width="6"/>'
            f'<rect x="{x - 10}" y="{y + h}" width="{w + 20}" height="12" fill="#e8e2d6"/>')
YS6 = 1590
CC = (130, 950, 330, 750, 1150, 830)           # tejado de la casa central
CL = (-380, 150, -200, -30, 1230, 970)         # casa izquierda (con claraboya)
CR = (930, 1460, 1090, 1300, 1210, 930)        # casa derecha
casa_c = ('<rect x="180" y="1150" width="720" height="440" fill="url(#paredG)"/><rect x="860" y="1150" width="40" height="440" fill="#000" opacity="0.12"/>'
          + ventana(250, 1220, 150, 150, True) + ventana(680, 1220, 150, 150)
          + '<rect x="470" y="1350" width="140" height="240" fill="#5a3a24"/><rect x="480" y="1360" width="120" height="100" fill="#6b4630"/><circle cx="590" cy="1470" r="7" fill="#c9a34a"/>'
          '<rect x="450" y="1580" width="180" height="14" fill="#cfc8bb"/><rect x="884" y="1160" width="12" height="430" fill="#9aa1a8"/>'
          '<rect x="660" y="760" width="70" height="140" fill="#b9ae9e"/><rect x="652" y="752" width="86" height="16" fill="#8e8476"/>' + tejado(CC))
paneles = "".join(placa(CC, u, u + 0.2, v, v + 0.3, f"pa{i}{j}") for i, u in enumerate((0.1, 0.32, 0.54, 0.76)) for j, v in enumerate((0.1, 0.45)))
casa_l = ('<rect x="-340" y="1230" width="440" height="360" fill="url(#paredG)"/>' + ventana(-120, 1300, 130, 140) + tejado(CL))
q = [bil(CL, 0.5, 0.25), bil(CL, 0.8, 0.25), bil(CL, 0.8, 0.6), bil(CL, 0.5, 0.6)]
qp = " ".join(f"{x:.0f},{y:.0f}" for x, y in q)
mx, my = (q[0][0] + q[2][0]) / 2, (q[0][1] + q[2][1]) / 2
clara = (f'<polygon points="{qp}" fill="url(#cristalG)" stroke="#e8e2d6" stroke-width="7"/>'
         f'<g id="clara6" opacity="0"><polygon points="{qp}" fill="#0a0f18" opacity="0.65"/>'
         + "".join(f'<path d="M{mx:.0f},{my:.0f} L{mx + 70 * math.cos(a):.0f},{my + 50 * math.sin(a):.0f}" stroke="#fff" stroke-width="2.5"/>' for a in [k * 0.9 + 0.3 for k in range(7)]) + '</g>')
casa_r = ('<rect x="980" y="1210" width="440" height="380" fill="url(#paredG)"/>' + ventana(1040, 1290, 120, 140, True) + tejado(CR)
          + "".join(placa(CR, u, u + 0.24, 0.15, 0.55, f"pr{k}") for k, u in enumerate((0.1, 0.38))))
acum = "".join(f'<ellipse class="ac6" cx="{x:.0f}" cy="{y:.0f}" rx="{rr.randint(3, 7)}" ry="2.5" fill="#eef7ff" opacity="0"/>'
               for x, y in [bil(CC, rr.uniform(0.02, 0.98), rr.uniform(0, 0.95)) for _ in range(90)] + [bil(CL, rr.uniform(0, 1), rr.uniform(0, 0.9)) for _ in range(30)])
jardin = (f'<rect x="-300" y="{YS6}" width="1700" height="400" fill="#2c3a28"/><rect x="-300" y="{YS6}" width="1700" height="400" fill="url(#mantoG)" id="suelo6" opacity="0.35"/>'
          + "".join(f'<rect x="{x}" y="{YS6 - 70}" width="10" height="90" fill="#e8e2d6"/>' for x in range(-280, 1400, 60))
          + f'<rect x="-300" y="{YS6 - 60}" width="1700" height="8" fill="#e8e2d6"/><rect x="-300" y="{YS6 - 25}" width="1700" height="8" fill="#e8e2d6"/>'
          + "".join(f'<ellipse cx="{x}" cy="{YS6 - 20}" rx="{w}" ry="{w * 0.6:.0f}" fill="#2f4a2a"/>' for x, w in ((150, 80), (930, 90), (360, 50))))
e6 = ['<rect width="1080" height="1920" fill="url(#cieloTorm)"/>', casa_l, clara, casa_r, casa_c, paneles, acum, jardin, granizo("g6", 6, 0.9)]
escena("e6", "".join(e6))
mostrar("e6", f6, ta - 0.3)
camara("e6", f6, ta, (0, 40, 1.0), (-1.32 * (560 - 540), -1.32 * (990 - 960), 1.32), "power2.inOut")
caer("g6", f6, ta)
J(f'tl.to(".ac6", {{opacity:0.9, duration:0.2, stagger:0.02}}, {f6:.2f});')
J(f'tl.to("#clara6", {{opacity:1, duration:0.05}}, {P("claraboyas") - 0.1:.2f});')
FX.append(("crack", P("claraboyas") - 0.1))
J(f'tl.to("#e6 .crack6", {{opacity:1, duration:0.05, stagger:{{each:0.16, from:"random"}}}}, {P("solares") - 0.35:.2f});')
for k in range(3):
    FX.append(("crack", P("solares") - 0.35 + k * 0.4))
chip("PLACAS SOLARES Y CLARABOYAS ROTAS", P("claraboyas"), ta - 0.35, 60, 640, AMB)
vuelos = (("08:15", "MADRID", "IB 3110"), ("08:40", "PARÍS", "VY 8002"), ("09:05", "LONDRES", "BA 461"), ("09:30", "ROMA", "FR 2211"), ("09:55", "LISBOA", "TP 1023"), ("10:20", "BERLÍN", "LH 1803"))
OVR.append('<div id="fondo6" class="fondoTec"></div>')
OVR.append('<div id="sal6" class="panel salidas"><div class="sh"><span>SALIDAS</span><span>DEPARTURES</span></div>'
           + "".join(f'<div class="sf"><span>{h}</span><span>{d}</span><span>{v}</span><span class="est"><em>EN HORA</em><strong>CANCELADO</strong></span></div>' for h, d, v in vuelos) + '</div>')
for s_ in ("#fondo6", "#sal6"):
    J(f'tl.set("{s_}", {{opacity:0}}, 0); tl.set("{s_}", {{opacity:1}}, {ta - 0.3:.2f}); tl.set("{s_}", {{opacity:0}}, {F(7) - 0.03:.2f});')
J(f'tl.set("#sal6 strong", {{opacity:0}}, 0); tl.to("#sal6 strong", {{opacity:1, duration:0.05, stagger:0.15}}, {P("tierra") - 0.4:.2f}); tl.to("#sal6 em", {{opacity:0, duration:0.05, stagger:0.15}}, {P("tierra") - 0.4:.2f});')
J(f'tl.fromTo("#sal6", {{scale:1.0}}, {{scale:1.05, duration:{F(7) - ta:.2f}, ease:"sine.inOut", immediateRender:false}}, {ta - 0.3:.2f});')
for k in range(6):
    FX.append(("clic", P("tierra") - 0.4 + k * 0.15))

# ================================================================== 7) TAMAÑOS Y VELOCIDAD: la cámara viaja por la mesa de medida
f7 = F(7)
tam = (("Guisante", 0.6), ("Canica", 1.5), ("Pelota de golf", 4.3), ("Pelota de tenis", 6.7), ("Pomelo", 11))
xs = 160
e7 = ['<rect x="-400" width="2400" height="1920" fill="url(#fondoTec)"/>', '<rect x="-400" width="2400" height="1920" fill="url(#rejilla)" opacity="0.4"/>',
      '<rect x="-400" y="1240" width="2400" height="6" fill="#33445f"/>']
for i in range(0, 40):
    x = 60 + i * 60
    e7.append(f'<path d="M{x},1246 L{x},{1270 if i % 5 else 1290}" stroke="#4a6080" stroke-width="3"/>')
for k, (nom, cm) in enumerate(tam):
    r = max(8, cm * 12)
    cx = xs + r
    e7.append(f'<g class="b7"><ellipse cx="{cx:.0f}" cy="1244" rx="{r * 0.9:.0f}" ry="{max(4, r * 0.12):.0f}" fill="#000" opacity="0.5"/>{piedra(cx, 1240 - r, r, False)}'
              f'<text x="{cx:.0f}" y="{1240 - 2 * r - 50:.0f}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="32" fill="{INK}">{nom}</text>'
              f'<text x="{cx:.0f}" y="{1240 - 2 * r - 14:.0f}" text-anchor="middle" font-family="Inter" font-weight="700" font-size="28" fill="{ICE}">{str(cm).replace(".", ",")} cm</text></g>')
    xs = cx + r + (170 if cm < 2 else 110)
escena("e7", "".join(e7))
mostrar("e7", f7, F(8))
camara("e7", f7, F(8), (330, 30, 1.3), (-300, 80, 0.92), "power2.inOut")
J(f'tl.set("#e7 .b7", {{opacity:0}}, 0); tl.to("#e7 .b7", {{opacity:1, duration:0.4, stagger:0.55}}, {f7 + 0.2:.2f});')
OVR.append(f'<div id="vel7" class="panel vel"><svg width="380" height="220" viewBox="0 0 380 220">'
           + "".join(f'<path d="M{190 + 150 * math.cos(math.radians(a)):.0f},{200 + 150 * math.sin(math.radians(a)):.0f} L{190 + 170 * math.cos(math.radians(a)):.0f},{200 + 170 * math.sin(math.radians(a)):.0f}" stroke="#4a6080" stroke-width="4"/>' for a in range(180, 361, 18))
           + f'<path d="M40,200 A150,150 0 0 1 340,200" stroke="#1e2c45" stroke-width="16" fill="none"/><path id="arco7" d="M40,200 A150,150 0 0 1 340,200" stroke="{RED}" stroke-width="16" fill="none" pathLength="1" stroke-dasharray="1" style="stroke-dashoffset:1"/>'
           f'<path id="ag7" d="M190,200 L60,200" stroke="{INK}" stroke-width="7" stroke-linecap="round"/><circle cx="190" cy="200" r="12" fill="{INK}"/></svg>'
           f'<div class="vn">{rueda("v7", "160", 92, INK)}<small>km/h</small></div><div class="vt">caída de las piedras más grandes</div></div>')
pop("#vel7", P("grandes") - 0.3, 0.45)
J(f'tl.to("#arco7", {{strokeDashoffset:0.15, duration:1.1, ease:"power3.out"}}, {P("ciento") - 0.2:.2f}); tl.fromTo("#ag7", {{rotation:0}}, {{rotation:150, svgOrigin:"190 200", duration:1.1, ease:"power3.out", immediateRender:false}}, {P("ciento") - 0.2:.2f});')
gira("v7", "160", P("ciento") - 0.2, 1.0)
FX.append(("riser", P("ciento") - 0.9))
fuera("#vel7", F(8) - 0.1)
fuente("Fuente: NOAA · NSSL", P("grandes"), F(8) - 0.1)

# ================================================================== 8) RÉCORD: piedra a escala junto a un móvil
f8 = F(8)
e8 = ['<rect width="1080" height="1920" fill="url(#fondoTec)"/>', '<rect width="1080" height="1920" fill="url(#rejilla)" opacity="0.4"/>',
      f'<g id="rec8">{piedra(380, 980, 210, False)}<circle cx="380" cy="980" r="160" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.18"/><circle cx="380" cy="980" r="100" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.15"/></g>',
      '<g><rect x="720" y="800" width="160" height="330" rx="26" fill="#141c2c" stroke="#5a6e8c" stroke-width="5"/><rect x="734" y="826" width="132" height="270" rx="10" fill="#22324e"/></g>',
      '<path d="M170,1228 L590,1228" stroke="#c9d8ea" stroke-width="4"/><path d="M170,1213 L170,1243 M590,1213 L590,1243" stroke="#c9d8ea" stroke-width="4"/>',
      '<text x="380" y="1290" text-anchor="middle" font-family="Inter" font-weight="800" font-size="40" fill="#c9d8ea">20 cm</text>',
      '<text x="800" y="1180" text-anchor="middle" font-family="Inter" font-weight="700" font-size="26" fill="#8796ad">móvil · 15 cm</text>']
escena("e8", "".join(e8))
mostrar("e8", f8, F(9))
camara("e8", f8, F(9), (0, 0, 1.0), (0, -20, 1.07))
pop("#rec8", f8 + 0.1, 0.6, "opacity:0, scale:0.85")
OVR.append('<div id="rc8" class="dato" style="top:1400px"><div class="dk">RÉCORD EN EE. UU.</div><div class="dn" style="font-size:104px">20 cm · 880 g</div><div class="ds">Vivian, Dakota del Sur · 23 de julio de 2010</div></div>')
pop("#rc8", P("veinte") - 0.3, 0.45)
FX.append(("golpe", P("veinte") - 0.2))
fuera("#rc8", F(9) - 0.1)

# ================================================================== 9-10) DOS SEMANAS → DÍA 30: el hielo sube DESDE EL SUELO (sin flotar)
f9 = F(9); dia(f9 + 0.1, 14)
YS = 1560
e9 = ['<rect width="1080" height="1920" fill="url(#cieloGris)"/>', ciudad(12, YS, 0.2, "#2a3550", "#1d2840", True, 0.85),
      f'<rect x="0" y="{YS}" width="1080" height="{1920 - YS}" fill="#151d2b"/>',
      '<g>' + "".join(f'<rect x="{x}" y="{YS - 250}" width="120" height="250" fill="#3b2a1c" stroke="#5a4532" stroke-width="5"/><circle cx="{x + 100}" cy="{YS - 120}" r="7" fill="#c9a34a"/>' for x in (120, 760)) + '</g>',
      coche_sil("car9", 330, YS - 128, 0.95, "#3a4a6a"),
      f'<g id="cerr9" opacity="0"><rect x="700" y="{YS - 420}" width="300" height="80" rx="8" fill="{RED}"/><text x="850" y="{YS - 367}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="40" fill="#fff">CERRADO</text></g>',
      f'<rect id="hielo9" x="-200" y="{YS}" width="1480" height="900" fill="url(#mantoG)"/>',
      f'<path id="borde9" d="M-200,{YS} L1280,{YS}" stroke="#ffffff" stroke-width="6" opacity="0.8"/>',
      granizo("g9", 9, 0.9)]
escena("e9", "".join(e9))
mostrar("e9", f9, F(11))
camara("e9", f9, F(11), (0, 0, 1.0), (0, 60, 1.1))
caer("g9", f9, F(11))
def subir(t, alto, d):
    J(f'tl.to("#hielo9, #borde9", {{y:{-alto}, duration:{d:.2f}, ease:"power1.inOut"}}, {t:.2f});')
subir(f9 + 0.3, 120, P("guadalajara") - f9 - 0.3)
subir(P("guadalajara"), 260, FE(9) - P("guadalajara"))
subir(F(10), 330, FE(10) - F(10))
OVR.append(f'<div id="reg9" class="regla"><div class="rl"></div><div class="rt">1 m</div></div>')
J(f'tl.set("#reg9", {{opacity:0}}, 0); tl.to("#reg9", {{opacity:1, duration:0.4}}, {P("metro") - 0.4:.2f}); tl.to("#reg9", {{opacity:0, duration:0.3}}, {F(11) - 0.05:.2f});')
OVR.append('<div id="gdl9" class="dato pe"><div class="dk">GUADALAJARA (MÉXICO)</div><div class="dn" style="font-size:96px">+1 m de hielo</div><div class="ds">30 de junio de 2019 · una sola granizada</div></div>')
pop("#gdl9", P("guadalajara") - 0.2, 0.45)
fuera("#gdl9", F(10) - 0.1)
dia(P("imagina") - 0.1, 30)
for k, (txt, w) in enumerate((("PUERTAS BLOQUEADAS", "bloqueadas"), ("COLEGIOS CERRADOS", "cerrados"), ("COCHES ENTERRADOS", "enterrados"))):
    chip(txt, P(w) - 0.3, FE(10) + 0.1, 60, 640 + k * 84, RED if k == 2 else AMB)
pop("#cerr9", P("colegios") - 0.2, 0.3, "opacity:0")
fuente("Fuente: Gobierno de Jalisco y prensa (2019)", P("guadalajara"), F(10) - 0.1)

# ================================================================== 11) DESHIELO: el agua corre
f11 = F(11)
e11 = ['<rect width="1080" height="1920" fill="url(#cieloSol)"/>', '<circle cx="860" cy="560" r="120" fill="#ffd27a" opacity="0.9"/><circle cx="860" cy="560" r="230" fill="#ffd27a" opacity="0.15"/>',
       ciudad(12, YS, 0.15, "#3a3a4a", "#2a2c3a", False, 0.85),
       f'<rect x="0" y="{YS}" width="1080" height="{1920 - YS}" fill="#151d2b"/>',
       f'<g id="agua11" opacity="0"><rect x="-200" y="{YS - 110}" width="1480" height="900" fill="url(#aguaG)"/>'
       + "".join(f'<path class="cor" d="M{x},{YS - 60 + (x // 80 % 4) * 70} l160,0" stroke="#cfe8ff" stroke-width="4" stroke-linecap="round" opacity="0.6"/>' for x in range(-400, 1200, 130)) + '</g>',
       f'<rect id="hielo11" x="-200" y="{YS - 330}" width="1480" height="900" fill="url(#mantoG)"/>']
escena("e11", "".join(e11))
mostrar("e11", f11, F(12))
camara("e11", f11, F(12), (0, 40, 1.08), (0, 0, 1.0))
J(f'tl.to("#hielo11", {{y:420, opacity:0, duration:2.0, ease:"power1.in"}}, {P("derrite") - 0.4:.2f});')
J(f'tl.to("#agua11", {{opacity:1, duration:0.9}}, {P("derrite"):.2f}); tl.fromTo(".cor", {{x:0}}, {{x:600, duration:2.0, repeat:3, ease:"none", immediateRender:false}}, {P("derrite"):.2f});')
FX.append(("agua", P("derrite")))
OVR.append('<div id="tem11" class="panel tem"><div class="pt">TEMPERATURA</div><div class="tv"><span id="t11a">−2 °C</span><span id="t11b">18 °C</span></div></div>')
pop("#tem11", P("para") - 0.2, 0.4)
J(f'tl.set("#t11b", {{opacity:0}}, 0); tl.to("#t11a", {{opacity:0, duration:0.3}}, {P("derrite") - 0.3:.2f}); tl.to("#t11b", {{opacity:1, duration:0.3}}, {P("derrite") - 0.3:.2f});')
fuera("#tem11", P("rios") - 0.2)
chip("RIESGO DE INUNDACIÓN", P("rios") - 0.3, F(12) - 0.1, 60, 640, RED)

# ================================================================== 12) EL DATO: el granizo necesita calor
f12 = F(12); barrido(f12)
J(f'tl.to("#hud", {{opacity:0, duration:0.3}}, {f12:.2f});')
KM = 66.7                                   # 1 km = 66,7 px; suelo en y=1500
def yk(km): return 1500 - km * KM
CXc, YBc, YTc = 560, yk(3.4), yk(12.4)
TEMPE = P("caliente") - 0.3
dentro12 = (f'<g id="corr12" opacity="0"><path d="M{CXc},{YBc + 20:.0f} C{CXc - 30},{yk(6):.0f} {CXc + 30},{yk(9):.0f} {CXc},{yk(10.4):.0f}" stroke="{AMB}" stroke-width="70" fill="none" opacity="0.22" stroke-linecap="round"/>'
            f'<path class="corr12" d="M{CXc},{YBc + 20:.0f} C{CXc - 30},{yk(6):.0f} {CXc + 30},{yk(9):.0f} {CXc},{yk(10.4):.0f}" stroke="#ffd08a" stroke-width="12" fill="none" stroke-dasharray="46 30" stroke-linecap="round"/>'
            f'<path d="M{CXc - 34},{yk(10.0):.0f} L{CXc},{yk(10.6):.0f} L{CXc + 34},{yk(10.0):.0f}" stroke="#ffd08a" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>')
nube12, pf12, an12 = cumulo("n12", CXc, YBc, YTc, 250, 21, "cbLuz", "cbAlto", dentro=dentro12)
ch12, H12 = chorro("cho12", 470, 700, YBc, 1500, 40, 8)
burb = "".join(f'<circle class="burb12" cx="{x}" cy="1480" r="{r}" fill="url(#burbuja)"/>' for x, r in ((380, 46), (470, 34), (560, 52), (650, 38), (740, 44), (520, 30), (610, 28)))
calima = "".join(f'<path class="cal12" d="M-200,{1470 - i * 14} q60,-12 120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0" stroke="#ffcf9a" stroke-width="3" fill="none" opacity="{0.35 - i * 0.06:.2f}"/>' for i in range(5))
entra = (f'<g id="ent12" opacity="0">'
         + "".join(f'<path class="ent12" d="M{x0},1440 C{x0 + d * 120},1430 {CXc - d * 140},{YBc + 120:.0f} {CXc - d * 40},{YBc + 10:.0f}" stroke="{AMB}" stroke-width="8" fill="none" stroke-dasharray="26 18" stroke-linecap="round"/>' for x0, d in ((190, 1), (930, -1)))
         + f'<path class="ent12" d="M{CXc},1470 L{CXc},{YBc + 10:.0f}" stroke="{AMB}" stroke-width="10" fill="none" stroke-dasharray="26 18" stroke-linecap="round"/></g>')
rayo12 = f'<path id="rayo12" d="M680,{YBc:.0f} L664,{YBc + 70:.0f} L692,{YBc + 96:.0f} L668,{YBc + 160:.0f} L700,{YBc + 190:.0f} L684,1500" stroke="#f4f8ff" stroke-width="5" fill="none" stroke-linejoin="round" opacity="0"/>'
eje = ('<path d="M110,1500 L110,660" stroke="#4a6080" stroke-width="3"/>'
       + "".join(f'<path d="M104,{yk(k):.0f} L118,{yk(k):.0f}" stroke="#4a6080" stroke-width="3"/><text x="132" y="{yk(k) + 9:.0f}" font-family="Inter" font-weight="700" font-size="26" fill="#8796ad">{k} km</text>' for k in (0, 4, 8, 12))
       + f'<path d="M100,{yk(4.2):.0f} L1000,{yk(4.2):.0f}" stroke="{ICE}" stroke-width="2" stroke-dasharray="12 10" opacity="0.55"/>'
       + f'<text x="1000" y="{yk(4.2) - 14:.0f}" text-anchor="end" font-family="Inter" font-weight="800" font-size="28" fill="{ICE}">0 °C</text>'
       + f'<text x="1000" y="{yk(10) - 14:.0f}" text-anchor="end" font-family="Inter" font-weight="800" font-size="28" fill="{ICE}">−40 °C</text>'
       + f'<path d="M100,{yk(10):.0f} L1000,{yk(10):.0f}" stroke="{ICE}" stroke-width="2" stroke-dasharray="12 10" opacity="0.4"/>'
       + f'<text x="1000" y="1460" text-anchor="end" font-family="Inter" font-weight="800" font-size="28" fill="{AMB}">30 °C</text>')
paisaje = ('<path d="M-200,1500 L1280,1500 L1280,2700 L-200,2700 Z" fill="url(#sueloCal)"/>'
           '<path d="M0,1500 C200,1488 380,1494 560,1486 C760,1478 900,1492 1080,1484 L1080,1520 L0,1520 Z" fill="#8a4a26" opacity="0.7"/>'
           + "".join(f'<rect x="{x}" y="{1500 - h}" width="{w}" height="{h}" fill="#3a2418"/>' for x, w, h in ((40, 40, 60), (90, 26, 40), (840, 50, 80), (900, 34, 50), (950, 44, 70))))
sombra12 = f'<ellipse id="som12" cx="{CXc}" cy="1510" rx="420" ry="26" fill="#000" opacity="0"/>'
e12 = ['<rect width="1080" height="1920" fill="url(#cieloTarde)"/>', '<circle cx="990" cy="1430" r="60" fill="#ffd27a" opacity="0.95"/><circle cx="990" cy="1430" r="150" fill="#ffd27a" opacity="0.12"/>',
       eje, paisaje, sombra12, calima, burb, entra, ch12, rayo12, '<g id="torre12">' + nube12 + '</g>']
escena("e12", "".join(e12))
FIN12 = F(13) + 0.5
mostrar("e12", f12, FIN12)
camara("e12", f12, FIN12, (0, -420, 1.2), (0, 40, 1.0), "power1.inOut")
J(f'tl.fromTo(".cal12", {{x:0}}, {{x:-120, duration:2.0, repeat:{int((FIN12 - f12) / 2) + 1}, ease:"none", immediateRender:false}}, {f12:.2f});')
J(f'tl.fromTo(".burb12", {{y:0, opacity:0.0, scale:0.6}}, {{y:{YBc - 1480:.0f}, opacity:0.9, scale:1.2, duration:2.2, stagger:0.35, repeat:{int((FIN12 - f12) / 2.6)}, ease:"power1.in", immediateRender:false}}, {f12 + 0.2:.2f});')
J('tl.set(".burb12", {opacity:0}, 0);')
# la nube CRECE de verdad: cada pompa se hincha (de la base hacia arriba) con un pequeño rebote, y luego «hierve»
g0, g1 = f12 + 0.5, P("arriba") - 0.5
for i, (x, y, r, t) in enumerate(pf12):
    tt = g0 + (g1 - g0) * t + (i % 5) * 0.04
    J(f'tl.set("#n12p{i}", {{attr:{{r:0}}}}, 0); tl.to("#n12p{i}", {{attr:{{r:{r:.0f}}}, duration:0.9, ease:"back.out(1.4)"}}, {tt:.2f});')
    if t > 0.72:
        J(f'tl.to("#n12p{i}", {{attr:{{r:{r * 1.09:.0f}}}, duration:0.55, yoyo:true, repeat:3, ease:"sine.inOut"}}, {tt + 0.95 + (i % 3) * 0.15:.2f});')
ya0 = P("arriba") - 0.9
for i, (x, y, r, u) in enumerate(an12):
    J(f'tl.set("#n12a{i}", {{attr:{{r:0, cx:{CXc + (x - CXc) * 0.2:.0f}}}}}, 0); tl.to("#n12a{i}", {{attr:{{r:{r:.0f}, cx:{x:.0f}}}, duration:1.1, ease:"power2.out"}}, {ya0 + u * 0.5:.2f});')
J(f'tl.set("#n12y", {{scaleX:0, scaleY:0, svgOrigin:"{CXc} {YTc:.0f}"}}, 0); tl.to("#n12y", {{scaleX:1, scaleY:1, svgOrigin:"{CXc} {YTc:.0f}", duration:1.4, ease:"power2.out"}}, {ya0 + 0.2:.2f});')
J(f'tl.to("#som12", {{opacity:0.35, duration:{g1 - g0:.2f}}}, {g0:.2f});')
# el aire caliente entra por los lados y sube por el centro (la flecha solo se ve dentro de la nube y bajo su base)
J(f'tl.to("#ent12", {{opacity:1, duration:0.4}}, {TEMPE:.2f}); tl.fromTo(".ent12", {{strokeDashoffset:0}}, {{strokeDashoffset:-176, duration:{FIN12 - TEMPE:.2f}, ease:"none", immediateRender:false}}, {TEMPE:.2f});')
J(f'tl.to("#corr12", {{opacity:1, duration:0.5}}, {P("empuja") - 0.2:.2f}); tl.fromTo(".corr12", {{strokeDashoffset:0}}, {{strokeDashoffset:-304, duration:{FIN12 - P("empuja"):.2f}, ease:"none", immediateRender:false}}, {P("empuja") - 0.2:.2f});')
FX.append(("riser", P("empuja") - 0.6))
for tr in (P("tormentas", 2) - 0.1, P("arriba") + 0.3):
    J(f'tl.to("#rayo12", {{opacity:1, duration:0.04, yoyo:true, repeat:3}}, {tr:.2f}); tl.to("#n12flash", {{opacity:0.5, duration:0.05, yoyo:true, repeat:3}}, {tr:.2f});')
FX.append(("trueno", P("tormentas", 2) - 0.1))
J(f'tl.to("#cho12", {{opacity:1, duration:0.5}}, {P("arriba") + 0.1:.2f});'); mover_chorro("cho12", H12, P("arriba"), FIN12)
chip("EL AIRE CALIENTE SUBE Y FORMA LA TORMENTA", TEMPE, FIN12 - 0.1, 60, 1640, AMB)
FX.append(("brillo", P("calor")))
# ================================================================== 13) CIERRE EN BUCLE: un día de calor, una sola piedra
f13 = F(13)
e13 = ['<rect width="1080" height="1920" fill="url(#cieloSol)"/>', ciudad(3, 1500, 0.2, "#2e2a36", "#221f2a"), calle(1500, False), coche_sil("car13", 640, 1420, 1.05, "#3a3446")]
escena("e13", "".join(e13))
mostrar("e13", f13 + 0.5, DUR - 0.35)
camara("e13", f13 + 0.5, DUR - 0.35, (0, 0, 1.04), (0, 60, 1.18), "power2.in")
OVR.append('<svg id="pu13" width="200" height="200" viewBox="-100 -100 200 200" style="position:absolute;left:640px;top:-220px;overflow:visible;z-index:9">'
           '<path d="M-10,-700 L0,0" stroke="url(#estela)" stroke-width="40" stroke-linecap="round" opacity="0.4"/><circle r="40" fill="url(#hielo)"/><ellipse cx="-14" cy="-14" rx="12" ry="9" fill="#fff" opacity="0.9"/></svg>')
J(f'tl.set("#pu13", {{opacity:0}}, 0); tl.set("#pu13", {{opacity:1}}, {f13 + 0.6:.2f}); tl.fromTo("#pu13", {{y:0}}, {{y:1500, duration:{DUR - f13 - 0.9:.2f}, ease:"power2.in", immediateRender:false}}, {f13 + 0.6:.2f}); tl.set("#pu13", {{opacity:0}}, {DUR - 0.3:.2f});')
J(f'tl.set("#e1", {{opacity:1}}, {DUR - 0.35:.2f}); tl.set("#e1-cam", {{x:0, y:60, scale:1.18}}, {DUR - 0.35:.2f}); tl.set("#titulo", {{opacity:1, y:0}}, {DUR - 0.35:.2f}); tl.set("#mantoB", {{opacity:0}}, {DUR - 0.35:.2f});')
J(f'tl.set("#car1mov", {{x:0, y:0, rotation:0}}, {DUR - 0.35:.2f}); tl.set("#e1", {{x:0, y:0}}, {DUR - 0.35:.2f}); tl.set(".ast1, .polvo1, .resto1, #onda1, #bola1, .humo1, #haz1, #freno1", {{opacity:0}}, {DUR - 0.35:.2f}); tl.set("#marca1", {{strokeDashoffset:1}}, {DUR - 0.35:.2f});')

# ------------------------------------------------------------------ subtítulos
CLAVE = set(norm(w) for w in ["granizar", "treinta", "minutos", "capas", "blancas", "tambores", "abolladuras", "perdido", "millon", "hectareas",
                               "precios", "disparan", "claraboyas", "solares", "aviones", "ciento", "sesenta", "veinte", "kilo", "acumula",
                               "metro", "bloqueadas", "cerrados", "enterrados", "derrite", "rios", "calor", "caliente", "piedra"])
SUBS, chunks, cur = [], [], []
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
            spans.append(f'<span id="{wid}" class="sw key"><i class="hl"></i>{p["w"]}</span>')
            J(f'tl.to("#{wid} .hl", {{opacity:1, duration:0.06}}, {p["ini"]:.2f});')
        else:
            spans.append(f'<span id="{wid}" class="sw">{p["w"]}</span>')
        J(f'tl.to("#{wid}", {{color:"#ffffff", duration:0.06}}, {p["ini"]:.2f});')
    SUBS.append(f'<div id="sub{k}" class="clip sub" data-start="{max(0, st):.3f}" data-duration="{max(0.2, en - max(0, st)):.3f}" data-track-index="3">{" ".join(spans)}</div>')

rr = random.Random(3)
for s in range(int(DUR / 0.08)):
    J(f'tl.set("#grano", {{backgroundPosition:"{rr.randint(0, 360)}px {rr.randint(0, 360)}px"}}, {s * 0.08:.2f});')

cortina = capa_granizo("cort", 170, 4, 13, 1.0, 77, 1080, 2400)
html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:{BG}}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;background:{BG}}}
.esc{{position:absolute;inset:0;overflow:hidden}}
.cam{{position:absolute;inset:0;transform-origin:50% 50%}}
.fondoTec{{position:absolute;inset:0;background:radial-gradient(120% 80% at 50% 40%, #13213a, {BG} 70%);z-index:12}}
#hud{{position:absolute;left:60px;top:470px;width:250px;padding:12px 18px 16px;border-left:5px solid {ICE};background:rgba(7,12,22,0.62);z-index:40;color:{INK}}}
#hud .hl{{font:800 22px Inter;letter-spacing:6px;color:{MUTED}}} #hud .hn{{display:inline-block;font:900 72px Inter;line-height:1;letter-spacing:-2px}}
#hud .hd{{display:inline-block;font:800 32px Inter;color:{MUTED};margin-left:8px}}
#hud .hbar{{margin-top:10px;height:6px;background:#1e2c45}} #hud .hbar i{{display:block;height:100%;background:{ICE};transform-origin:0 50%;transform:scaleX(0.0333)}}
.chip{{position:absolute;z-index:35;display:flex;align-items:center;gap:14px;padding:14px 22px;background:rgba(7,12,22,0.8);border:2px solid;border-radius:6px;font:800 30px Inter;letter-spacing:1px;color:{INK}}}
.chip b{{width:12px;height:12px;border-radius:50%}}
.fuente{{position:absolute;left:60px;right:60px;top:1712px;z-index:35;font:600 24px Inter;color:{MUTED};letter-spacing:0.5px}}
.panel{{position:absolute;z-index:30;background:rgba(9,15,28,0.88);border:1px solid #2b3d5c;border-radius:10px;color:{INK}}}
#db3{{left:60px;top:1180px;width:560px;padding:22px 26px}} .pt{{font:800 22px Inter;letter-spacing:4px;color:{MUTED}}}
.barras{{display:flex;align-items:flex-end;gap:10px;height:220px;margin-top:14px}} .bd{{width:38px;background:linear-gradient(0deg,{ICE},{AMB} 70%,{RED});border-radius:3px}}
.pv{{margin-top:10px;font:700 26px Inter;color:#c9d8ea}}
.dato{{position:absolute;left:60px;right:60px;top:1260px;z-index:30;padding:26px 30px;background:rgba(9,15,28,0.88);border-left:6px solid {ICE};color:{INK}}}
.dato.pe{{top:860px}}
.dk{{font:800 24px Inter;letter-spacing:4px;color:{ICE}}} .dn{{font:900 120px Inter;letter-spacing:-3px;line-height:1.05}}
.dt{{font:800 30px Inter;letter-spacing:2px;color:#c9d8ea}} .ds{{font:600 26px Inter;color:{MUTED};margin-top:6px}}
.tabla{{left:60px;right:60px;top:1240px;padding:18px 26px}} .fila{{display:grid;grid-template-columns:1fr 300px 60px;align-items:center;padding:14px 0;border-bottom:1px solid #1e2c45;font:800 40px Inter}}
.pv5{{position:relative;height:50px}} .pv5 s{{position:absolute;left:0;top:0;color:#c9d8ea;text-decoration:none}} .pv5 b{{position:absolute;left:0;top:0;color:{RED}}}
.flecha{{color:{RED};font-size:34px}} .nota5{{font:600 22px Inter;color:{MUTED};margin-top:12px}}
.salidas{{left:40px;right:40px;top:720px;padding:20px 24px;background:#0b0f18;border:2px solid #2a3240;z-index:30}}
.sh{{display:flex;justify-content:space-between;font:900 40px Inter;color:{AMB};letter-spacing:4px;padding-bottom:14px;border-bottom:2px solid #2a3240}}
.sf{{display:grid;grid-template-columns:110px 1fr 160px 230px;gap:10px;padding:16px 0;border-bottom:1px solid #1a2130;font:700 33px "Courier New", monospace;color:#f3e7c4}}
.est{{position:relative}} .est em{{font-style:normal;color:{GRN}}} .est strong{{position:absolute;left:0;top:0;color:{RED}}}
.vel{{left:60px;top:560px;width:440px;padding:20px 26px}} .vn{{font:900 92px Inter;line-height:1;margin-top:-10px}} .vn small{{font:800 34px Inter;color:{MUTED};margin-left:10px}}
.vt{{font:700 24px Inter;color:{MUTED};margin-top:6px}}
.tem{{left:60px;top:1240px;width:520px;padding:20px 26px}} .tv{{position:relative;height:110px;font:900 100px Inter}} .tv span{{position:absolute;left:0;top:0}} #t11a{{color:{ICE}}} #t11b{{color:{AMB}}}
.regla{{position:absolute;left:24px;top:{YS - 420}px;width:70px;height:420px;z-index:30}}
.regla .rl{{position:absolute;inset:0;border:3px solid #c9d8ea;border-right:none;background:repeating-linear-gradient(180deg, transparent 0 40px, rgba(201,216,234,0.7) 40px 43px)}}
.regla .rt{{position:absolute;left:80px;top:-20px;white-space:nowrap;font:900 40px Inter;color:{INK};text-shadow:0 2px 8px #000}}
.rueda{{display:inline-flex;align-items:baseline;font-weight:900;font-family:Inter;letter-spacing:-3px;font-variant-numeric:tabular-nums}}
.dg{{display:inline-block;height:1em;overflow:hidden;line-height:1em}} .st{{display:grid}} .st span{{height:1em;line-height:1em}} .sep{{display:inline-block;line-height:1em}}
.durp{{left:60px;top:1470px;display:flex;align-items:center;gap:24px;padding:18px 28px 18px 18px}} .dv{{font:900 58px Inter;line-height:1.05}} .ds2{{font:600 24px Inter;color:{MUTED}}}
.cortep{{left:40px;top:960px;width:330px;padding:16px 20px 18px;text-align:center}} .dv2{{font:800 30px Inter;color:#c9d8ea}}
#titulo{{position:absolute;left:56px;right:56px;top:620px;z-index:20}}
#titulo .t0{{font:800 64px Inter;color:#c9d8ea;letter-spacing:2px}} #titulo .t1{{font:900 112px Inter;color:#ffffff;letter-spacing:-4px;line-height:1}} #titulo .t1 span{{color:{ICE}}}
#cortina{{position:absolute;left:0;top:0;width:1080px;height:2400px;z-index:58;pointer-events:none}}
#grano{{position:absolute;inset:0;z-index:57;pointer-events:none;opacity:0.07;background:url(assets/grano.png);mix-blend-mode:overlay}}
#vineta{{position:absolute;inset:0;z-index:56;pointer-events:none;background:radial-gradient(110% 80% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55))}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:560px;z-index:55;pointer-events:none;background:linear-gradient(rgba(4,8,16,0.8), rgba(4,8,16,0))}}
#marca{{position:absolute;left:0;right:0;top:1775px;text-align:center;font:700 28px Inter;color:#ffffff;opacity:0.32;pointer-events:none;z-index:61}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 62px Inter;color:rgba(255,255,255,0.4);line-height:1.22;text-shadow:0 3px 12px rgba(0,0,0,0.6)}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:3px solid #4ea3ff;border-radius:6px;background:rgba(78,163,255,0.18);opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <svg width="0" height="0" style="position:absolute"><defs>
    <radialGradient id="hielo" cx="0.38" cy="0.35" r="0.7"><stop offset="0" stop-color="#ffffff"/><stop offset="0.45" stop-color="#e3f3ff"/><stop offset="0.85" stop-color="#9cc3dd"/><stop offset="1" stop-color="#6f97b4"/></radialGradient>
    <linearGradient id="estela" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0"/><stop offset="1" stop-color="#ffffff" stop-opacity="0.9"/></linearGradient>
    <linearGradient id="cieloNoche" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05080f"/><stop offset="0.55" stop-color="#16243d"/><stop offset="1" stop-color="#2a3c5a"/></linearGradient>
    <linearGradient id="cieloAlba" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b2840"/><stop offset="0.6" stop-color="#55688a"/><stop offset="1" stop-color="#9aaecb"/></linearGradient>
    <linearGradient id="cieloGris" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#121c2e"/><stop offset="1" stop-color="#4a5a74"/></linearGradient>
    <linearGradient id="cieloSol" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a2238"/><stop offset="0.55" stop-color="#b8664a"/><stop offset="1" stop-color="#f0b06a"/></linearGradient>
    <radialGradient id="nubeG" cx="0.5" cy="0.35" r="0.6"><stop offset="0" stop-color="#5c6c88"/><stop offset="1" stop-color="#1a2438" stop-opacity="0"/></radialGradient>
    <linearGradient id="nubeTec" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dce8f6"/><stop offset="1" stop-color="#6f86a6"/></linearGradient>
    <radialGradient id="fondoTec" cx="0.5" cy="0.4" r="0.9"><stop offset="0" stop-color="#13213a"/><stop offset="1" stop-color="{BG}"/></radialGradient>
    <pattern id="rejilla" width="60" height="60" patternUnits="userSpaceOnUse"><path d="M60,0 L0,0 0,60" fill="none" stroke="#1b2a44" stroke-width="1.5"/></pattern>
    <linearGradient id="asfalto" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#121a28"/><stop offset="1" stop-color="#05080f"/></linearGradient>
    <linearGradient id="reflejo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffcf7a" stop-opacity="0.18"/><stop offset="1" stop-color="#ffcf7a" stop-opacity="0"/></linearGradient>
    <linearGradient id="mantoG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4faff"/><stop offset="0.12" stop-color="#d9e9f6"/><stop offset="1" stop-color="#9fb8cf"/></linearGradient>
    <linearGradient id="capo" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5a6678"/><stop offset="0.5" stop-color="#2c3646"/><stop offset="1" stop-color="#151b26"/></linearGradient>
    <radialGradient id="abolG" cx="0.6" cy="0.65" r="0.6"><stop offset="0" stop-color="#05080f" stop-opacity="0.7"/><stop offset="1" stop-color="#05080f" stop-opacity="0"/></radialGradient>
    <linearGradient id="panelG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2b4b7a"/><stop offset="0.5" stop-color="#14274a"/><stop offset="1" stop-color="#0c1830"/></linearGradient>
    <linearGradient id="areaRoja" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{RED}" stop-opacity="0.5"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></linearGradient>
    <linearGradient id="aguaG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4f86b8"/><stop offset="1" stop-color="#1c3550"/></linearGradient>
    <radialGradient id="puff" cx="0.45" cy="0.3" r="0.7"><stop offset="0" stop-color="#ffffff"/><stop offset="0.55" stop-color="#dfe7f2"/><stop offset="1" stop-color="#8a9bb4"/></radialGradient>
    <linearGradient id="yunqueG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f8fd"/><stop offset="1" stop-color="#a9b8cc"/></linearGradient>
    <radialGradient id="burbuja"><stop offset="0" stop-color="#ffb547" stop-opacity="0.55"/><stop offset="1" stop-color="#ff7a3a" stop-opacity="0"/></radialGradient>
    <linearGradient id="cieloTarde" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d1730"/><stop offset="0.55" stop-color="#2e4a78"/><stop offset="0.85" stop-color="#c47a52"/><stop offset="1" stop-color="#f0b06a"/></linearGradient>
    <linearGradient id="cbLuz" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#fff1dc"/><stop offset="0.45" stop-color="#d8e2ef"/><stop offset="1" stop-color="#6d7f9c"/></linearGradient>
    <linearGradient id="cbAlto" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0.35"/><stop offset="0.7" stop-color="#ffffff" stop-opacity="0"/><stop offset="1" stop-color="#2a3a58" stop-opacity="0.55"/></linearGradient>
    {''.join(DEFS)}
    <radialGradient id="volB"><stop offset="0" stop-color="#ffffff" stop-opacity="0.32"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>
    <radialGradient id="volS"><stop offset="0" stop-color="#1a2234" stop-opacity="0.22"/><stop offset="1" stop-color="#1a2234" stop-opacity="0"/></radialGradient>
    <linearGradient id="tLuz" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#eef2f7"/><stop offset="0.5" stop-color="#a6b1c2"/><stop offset="1" stop-color="#4a566c"/></linearGradient>
    <linearGradient id="tAlto" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0.3"/><stop offset="0.5" stop-color="#ffffff" stop-opacity="0"/><stop offset="1" stop-color="#121826" stop-opacity="0.85"/></linearGradient>
    <linearGradient id="cieloTorm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#151d2c"/><stop offset="0.6" stop-color="#3f4c63"/><stop offset="1" stop-color="#7d8798"/></linearGradient>
    <linearGradient id="sueloCampo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a3f26"/><stop offset="1" stop-color="#1c1d10"/></linearGradient>
    <linearGradient id="chorroG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9e3ef" stop-opacity="0.55"/><stop offset="1" stop-color="#d9e3ef" stop-opacity="0.12"/></linearGradient>
    <radialGradient id="humoG"><stop offset="0" stop-color="#c9ced6" stop-opacity="0.8"/><stop offset="1" stop-color="#c9ced6" stop-opacity="0"/></radialGradient>
    <radialGradient id="polvoG"><stop offset="0" stop-color="#f2f9ff" stop-opacity="0.95"/><stop offset="1" stop-color="#f2f9ff" stop-opacity="0"/></radialGradient>
    <radialGradient id="frenoG"><stop offset="0" stop-color="#ff4a3a" stop-opacity="0.9"/><stop offset="1" stop-color="#ff4a3a" stop-opacity="0"/></radialGradient>
    <linearGradient id="hazG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffe9b0" stop-opacity="0.6"/><stop offset="1" stop-color="#ffe9b0" stop-opacity="0"/></linearGradient>
    <linearGradient id="pintura" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9545b"/><stop offset="0.3" stop-color="#a3262d"/><stop offset="0.7" stop-color="#6a1218"/><stop offset="1" stop-color="#2a0609"/></linearGradient>
    <linearGradient id="vidrio" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3a4d66"/><stop offset="1" stop-color="#0b111a"/></linearGradient>
    <radialGradient id="llanta" cx="0.4" cy="0.35"><stop offset="0" stop-color="#dfe4ea"/><stop offset="1" stop-color="#7b8592"/></radialGradient>
    <linearGradient id="tejaG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7a3222"/><stop offset="1" stop-color="#a4523a"/></linearGradient>
    <linearGradient id="paredG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#d9d0c2"/><stop offset="1" stop-color="#b3a896"/></linearGradient>
    <linearGradient id="cristalG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#9fb6cf"/><stop offset="0.5" stop-color="#4c6684"/><stop offset="1" stop-color="#26364c"/></linearGradient>
    <linearGradient id="sueloCal" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7a3a22"/><stop offset="1" stop-color="#2a1610"/></linearGradient>
  </defs></svg>
  {"".join(ESC)}
  <div id="topsombra"></div>
  {"".join(OVR)}
  <svg id="cortina" width="1080" height="2400">{cortina}</svg>
  <div id="vineta"></div><div id="grano"></div>
  <div id="marca">@mundo.supuesto</div>
  <div id="subs" data-layout-allow-overlap>{"".join(SUBS)}</div>
  <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
tl.set("#cortina", {{y:-2400}}, 0);
{chr(10).join(tl)}
tl.to({{}}, {{duration:0.01}}, {DUR - 0.01});
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>"""
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump(FX, open(os.path.join(BASE, "efectos.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones")

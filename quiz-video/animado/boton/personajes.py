# Personajes con CARA (ilustración 2D cuidada): piel, pelo, ojos que parpadean, cejas y boca con expresiones,
# ropa con sombreado y manos con dedos. Se pega dentro de gen.py (usa J, DEFS, grad_lin, grad_rad, random).
PIELES = ("#f2c9a8", "#e0ac85", "#c68a62", "#8d5a3b", "#f6d5bd", "#a86f4c")
PELOS = ("#2a1a12", "#5a3a22", "#1a1a1a", "#b07a3a", "#d8b26a", "#6b4a3a", "#8e8e8e")
ROPAS = ("#3f7ad8", "#e2725b", "#2fa36b", "#f2c14e", "#8a5cd6", "#e9e9e9", "#2a3550", "#d94f6b", "#1f9aa8")
ESTILOS = ("corto", "largo", "mono", "rizado", "calvo", "corto", "largo")
OJOS = ("#4a3020", "#2f5a8a", "#3f6a3a", "#2a1a12")
grad_rad("sombraCara", ((0, "#000000", 0), (0.7, "#000000", 0), (1, "#000000", 0.22)), 0.38, 0.32, 0.75)
grad_lin("brilloRopa", ((0, "#ffffff", 0.18), (0.5, "#ffffff", 0), (1, "#000000", 0.25)), 0, 0, 1, 0)
def estilo(seed, **kw):
    r_ = random.Random(seed)
    e = dict(piel=r_.choice(PIELES), pelo=r_.choice(PELOS), ropa=r_.choice(ROPAS), peinado=r_.choice(ESTILOS), ojos=r_.choice(OJOS),
             barba=r_.random() < 0.22, gafas=r_.random() < 0.18)
    e.update(kw)
    return e
def oscurece(c, f=0.75):
    c = c.lstrip("#"); return "#" + "".join(f"{int(int(c[i:i + 2], 16) * f):02x}" for i in (0, 2, 4))
BOCAS = {"neutral": (-0.22, 0.58, 0, 0.62, 0.22, 0.58), "sonrisa": (-0.32, 0.5, 0, 0.84, 0.32, 0.5), "triste": (-0.24, 0.68, 0, 0.5, 0.24, 0.68),
         "nervioso": (-0.22, 0.6, 0.04, 0.53, 0.22, 0.63), "serio": (-0.2, 0.6, 0, 0.6, 0.2, 0.6)}
CEJAS = {"neutral": ((-0.56, -0.38), (-0.36, -0.5), (-0.14, -0.42)), "preocupado": ((-0.56, -0.38), (-0.36, -0.46), (-0.14, -0.56)),
         "enfado": ((-0.56, -0.5), (-0.36, -0.46), (-0.14, -0.34)), "sorpresa": ((-0.56, -0.5), (-0.36, -0.66), (-0.14, -0.56))}
def _boca_d(hx, hy, r, tipo):
    a, b, c, d, e, f = BOCAS[tipo]
    return f"M{hx + a * r:.1f},{hy + b * r:.1f} Q{hx + c * r:.1f},{hy + d * r:.1f} {hx + e * r:.1f},{hy + f * r:.1f}"
def _ceja_d(hx, hy, r, tipo, lado):
    p = CEJAS[tipo]
    return "M" + " ".join(f"{hx + lado * x * r:.1f},{hy + y * r:.1f}" if i != 1 else f"Q{hx + lado * x * r:.1f},{hy + y * r:.1f}" for i, (x, y) in enumerate(p)).replace(" Q", " Q")
CARAS = {}
def cara(pid, hx, hy, r, e, espalda=False, expr="neutral"):
    """Cabeza con pelo y cara expresiva. Devuelve SVG; registra la geometría para animar expresiones y parpadeo."""
    CARAS[pid] = (hx, hy, r)
    pelo, piel = e["pelo"], e["piel"]
    craneo = (f"M{hx - r:.1f},{hy - 0.1 * r:.1f} C{hx - r:.1f},{hy - 1.25 * r:.1f} {hx + r:.1f},{hy - 1.25 * r:.1f} {hx + r:.1f},{hy - 0.1 * r:.1f} "
              f"C{hx + r:.1f},{hy + 0.75 * r:.1f} {hx + 0.45 * r:.1f},{hy + 1.15 * r:.1f} {hx:.1f},{hy + 1.18 * r:.1f} C{hx - 0.45 * r:.1f},{hy + 1.15 * r:.1f} {hx - r:.1f},{hy + 0.75 * r:.1f} {hx - r:.1f},{hy - 0.1 * r:.1f} Z")
    s = []
    if e["peinado"] == "largo":
        s.append(f'<path d="M{hx - 1.08 * r:.1f},{hy - 0.3 * r:.1f} C{hx - 1.25 * r:.1f},{hy + 0.9 * r:.1f} {hx - 1.0 * r:.1f},{hy + 1.6 * r:.1f} {hx - 0.6 * r:.1f},{hy + 1.75 * r:.1f} L{hx + 0.6 * r:.1f},{hy + 1.75 * r:.1f} C{hx + 1.0 * r:.1f},{hy + 1.6 * r:.1f} {hx + 1.25 * r:.1f},{hy + 0.9 * r:.1f} {hx + 1.08 * r:.1f},{hy - 0.3 * r:.1f} Z" fill="{pelo}"/>')
    if e["peinado"] == "mono":
        s.append(f'<circle cx="{hx:.1f}" cy="{hy - 1.22 * r:.1f}" r="{0.38 * r:.1f}" fill="{pelo}"/>')
    s.append(f'<ellipse cx="{hx - r:.1f}" cy="{hy + 0.08 * r:.1f}" rx="{0.17 * r:.1f}" ry="{0.26 * r:.1f}" fill="{oscurece(piel, 0.9)}"/><ellipse cx="{hx + r:.1f}" cy="{hy + 0.08 * r:.1f}" rx="{0.17 * r:.1f}" ry="{0.26 * r:.1f}" fill="{oscurece(piel, 0.9)}"/>')
    s.append(f'<path d="{craneo}" fill="{piel}"/>')
    if espalda:
        s.append(f'<path d="{craneo}" fill="{pelo}"/><path d="M{hx - 0.7 * r:.1f},{hy - 0.6 * r:.1f} Q{hx:.1f},{hy - 1.0 * r:.1f} {hx + 0.6 * r:.1f},{hy - 0.5 * r:.1f}" stroke="#ffffff" stroke-width="{0.08 * r:.1f}" opacity="0.18" fill="none"/>')
        return f'<g class="cabeza" id="{pid}_cab">' + "".join(s) + '</g>'
    s.append(f'<path d="{craneo}" fill="url(#sombraCara)"/>')
    s.append(f'<ellipse cx="{hx - 0.5 * r:.1f}" cy="{hy + 0.35 * r:.1f}" rx="{0.16 * r:.1f}" ry="{0.09 * r:.1f}" fill="#ff8a7a" opacity="0.25"/><ellipse cx="{hx + 0.5 * r:.1f}" cy="{hy + 0.35 * r:.1f}" rx="{0.16 * r:.1f}" ry="{0.09 * r:.1f}" fill="#ff8a7a" opacity="0.25"/>')
    ojos = ""
    for L in (-1, 1):
        ox, oy = hx + L * 0.34 * r, hy - 0.1 * r
        ojos += (f'<ellipse cx="{ox:.1f}" cy="{oy:.1f}" rx="{0.17 * r:.1f}" ry="{0.13 * r:.1f}" fill="#ffffff"/><circle cx="{ox:.1f}" cy="{oy + 0.01 * r:.1f}" r="{0.095 * r:.1f}" fill="{e["ojos"]}"/>'
                 f'<circle cx="{ox:.1f}" cy="{oy + 0.01 * r:.1f}" r="{0.05 * r:.1f}" fill="#111"/><circle cx="{ox + 0.035 * r:.1f}" cy="{oy - 0.035 * r:.1f}" r="{0.028 * r:.1f}" fill="#ffffff"/>'
                 f'<path d="M{ox - 0.18 * r:.1f},{oy - 0.02 * r:.1f} Q{ox:.1f},{oy - 0.19 * r:.1f} {ox + 0.18 * r:.1f},{oy - 0.02 * r:.1f}" stroke="{oscurece(piel, 0.55)}" stroke-width="{0.035 * r:.1f}" fill="none"/>')
    s.append(f'<g id="{pid}_ojos" class="ojos">{ojos}</g>')
    if e["gafas"]:
        s.append("".join(f'<circle cx="{hx + L * 0.34 * r:.1f}" cy="{hy - 0.1 * r:.1f}" r="{0.24 * r:.1f}" fill="#ffffff" fill-opacity="0.08" stroke="#2a2a2a" stroke-width="{0.05 * r:.1f}"/>' for L in (-1, 1))
                 + f'<path d="M{hx - 0.1 * r:.1f},{hy - 0.12 * r:.1f} L{hx + 0.1 * r:.1f},{hy - 0.12 * r:.1f}" stroke="#2a2a2a" stroke-width="{0.05 * r:.1f}"/>')
    s.append(f'<path d="M{hx - 0.03 * r:.1f},{hy + 0.02 * r:.1f} Q{hx + 0.12 * r:.1f},{hy + 0.3 * r:.1f} {hx - 0.07 * r:.1f},{hy + 0.33 * r:.1f}" stroke="{oscurece(piel, 0.7)}" stroke-width="{0.05 * r:.1f}" fill="none" stroke-linecap="round"/>')
    if e["barba"]:
        s.append(f'<path d="M{hx - 0.9 * r:.1f},{hy + 0.3 * r:.1f} C{hx - 0.8 * r:.1f},{hy + 1.1 * r:.1f} {hx + 0.8 * r:.1f},{hy + 1.1 * r:.1f} {hx + 0.9 * r:.1f},{hy + 0.3 * r:.1f} C{hx + 0.6 * r:.1f},{hy + 0.75 * r:.1f} {hx - 0.6 * r:.1f},{hy + 0.75 * r:.1f} {hx - 0.9 * r:.1f},{hy + 0.3 * r:.1f} Z" fill="{pelo}" opacity="0.9"/>')
    s.append(f'<path id="{pid}_boca" d="{_boca_d(hx, hy, r, expr)}" stroke="#7a2e2e" stroke-width="{0.075 * r:.1f}" fill="none" stroke-linecap="round"/>'
             f'<ellipse id="{pid}_bocaO" cx="{hx:.1f}" cy="{hy + 0.62 * r:.1f}" rx="{0.13 * r:.1f}" ry="{0.17 * r:.1f}" fill="#5a1a1a" opacity="0"/>')
    for L, nm in ((-1, "cI"), (1, "cD")):
        s.append(f'<path id="{pid}_{nm}" d="{_ceja_d(hx, hy, r, "neutral", L)}" stroke="{pelo}" stroke-width="{0.1 * r:.1f}" fill="none" stroke-linecap="round"/>')
    pe = e["peinado"]
    if pe in ("corto", "largo", "mono"):
        s.append(f'<path d="M{hx - 1.04 * r:.1f},{hy - 0.02 * r:.1f} C{hx - 1.12 * r:.1f},{hy - 1.32 * r:.1f} {hx + 1.12 * r:.1f},{hy - 1.32 * r:.1f} {hx + 1.04 * r:.1f},{hy - 0.02 * r:.1f} '
                 f'C{hx + 0.86 * r:.1f},{hy - 0.62 * r:.1f} {hx + 0.25 * r:.1f},{hy - 0.8 * r:.1f} {hx - 0.25 * r:.1f},{hy - 0.6 * r:.1f} C{hx - 0.6 * r:.1f},{hy - 0.48 * r:.1f} {hx - 0.92 * r:.1f},{hy - 0.32 * r:.1f} {hx - 1.04 * r:.1f},{hy - 0.02 * r:.1f} Z" fill="{pelo}"/>'
                 f'<path d="M{hx - 0.6 * r:.1f},{hy - 0.85 * r:.1f} Q{hx:.1f},{hy - 1.08 * r:.1f} {hx + 0.55 * r:.1f},{hy - 0.85 * r:.1f}" stroke="#ffffff" stroke-width="{0.07 * r:.1f}" opacity="0.18" fill="none"/>')
    elif pe == "rizado":
        s.append("".join(f'<circle cx="{hx + 1.0 * r * math.cos(a):.1f}" cy="{hy - 0.15 * r + 0.95 * r * math.sin(a) * 1.05:.1f}" r="{0.32 * r:.1f}" fill="{pelo}"/>' for a in [math.pi + k * math.pi / 9 for k in range(10)]))
    elif pe == "calvo":
        s.append(f'<path d="M{hx - 1.0 * r:.1f},{hy - 0.05 * r:.1f} Q{hx - 0.95 * r:.1f},{hy - 0.45 * r:.1f} {hx - 0.8 * r:.1f},{hy - 0.5 * r:.1f} M{hx + 1.0 * r:.1f},{hy - 0.05 * r:.1f} Q{hx + 0.95 * r:.1f},{hy - 0.45 * r:.1f} {hx + 0.8 * r:.1f},{hy - 0.5 * r:.1f}" stroke="{pelo}" stroke-width="{0.16 * r:.1f}" fill="none"/>')
    return f'<g class="cabeza" id="{pid}_cab">' + "".join(s) + '</g>'
def expr(pid, t, boca="neutral", cejas="neutral", d=0.25, abierta=False):
    """Cambia la expresión (boca + cejas) con una transición suave."""
    if pid not in CARAS: return
    hx, hy, r = CARAS[pid]
    J(f'tl.to("#{pid}_boca", {{attr:{{d:"{_boca_d(hx, hy, r, boca)}"}}, opacity:{0 if abierta else 1}, duration:{d}, ease:"power2.out"}}, {t:.2f});')
    J(f'tl.to("#{pid}_bocaO", {{opacity:{1 if abierta else 0}, duration:{d * 0.6:.2f}}}, {t:.2f});')
    for L, nm in ((-1, "cI"), (1, "cD")):
        J(f'tl.to("#{pid}_{nm}", {{attr:{{d:"{_ceja_d(hx, hy, r, cejas, L)}"}}, duration:{d}, ease:"power2.out"}}, {t:.2f});')
def parpadeo(pid, t0, t1, seed=1):
    if pid not in CARAS: return
    hx, hy, r = CARAS[pid]
    r_ = random.Random(seed); t = t0 + r_.uniform(0.3, 1.5)
    while t < t1 - 0.3:
        J(f'tl.fromTo("#{pid}_ojos", {{scaleY:1}}, {{scaleY:0.08, svgOrigin:"{hx:.0f} {hy - 0.1 * r:.0f}", duration:0.07, yoyo:true, repeat:1, immediateRender:false}}, {t:.2f});')
        t += r_.uniform(2.2, 3.6)
def mano_svg(mid, x, y, k, piel, cls="mano"):
    """Mano apoyada (vista desde delante): palma, cuatro dedos hacia la mesa y pulgar. Grupo trasladable."""
    dedos = "".join(f'<rect x="{dx * k - 4.5 * k:.1f}" y="{4 * k:.1f}" width="{9 * k:.1f}" height="{(15 + (1 - abs(dx) / 13) * 5) * k:.1f}" rx="{4.5 * k:.1f}" fill="{piel}"/>' for dx in (-13, -4.5, 4.5, 13))
    return (f'<g id="{mid}" class="{cls}" transform="translate({x:.1f},{y:.1f})"><g class="mv">{dedos}'
            f'<ellipse cx="0" cy="{2 * k:.1f}" rx="{18 * k:.1f}" ry="{14 * k:.1f}" fill="{piel}"/>'
            f'<ellipse cx="{-17 * k:.1f}" cy="{4 * k:.1f}" rx="{6 * k:.1f}" ry="{11 * k:.1f}" fill="{piel}" transform="rotate(-25 {-17 * k:.1f} {4 * k:.1f})"/>'
            f'<path d="M{-12 * k:.1f},{-6 * k:.1f} Q0,{-10 * k:.1f} {12 * k:.1f},{-6 * k:.1f}" stroke="#000" stroke-opacity="0.12" stroke-width="{2 * k:.1f}" fill="none"/></g></g>')
def sentado(pid, cx, ytab, h=300, rim="#ffe2b0", col=None, lado_mano=1, e=None, expr0="neutral"):
    """Persona sentada tras la mesa, CON CARA: cuerpo (detrás de la mesa) y brazos/manos (delante). Devuelve (cuerpo, brazos)."""
    e = e or estilo(hash(pid) % 9973)
    k = h / 300
    ropa, piel = e["ropa"], e["piel"]
    hs = (cx + 70 * k * lado_mano, ytab - 150 * k); ho = (cx - 70 * k * lado_mano, ytab - 150 * k)
    mano = (cx + 62 * k * lado_mano, ytab + 14 * k); mano2 = (cx - 62 * k * lado_mano, ytab + 14 * k)
    SEN[pid] = (hs, mano, k)
    torso = (f'M{cx - 86 * k:.0f},{ytab + 30 * k:.0f} L{cx - 82 * k:.0f},{ytab - 130 * k:.0f} Q{cx - 80 * k:.0f},{ytab - 168 * k:.0f} {cx - 36 * k:.0f},{ytab - 172 * k:.0f} '
             f'L{cx + 36 * k:.0f},{ytab - 172 * k:.0f} Q{cx + 80 * k:.0f},{ytab - 168 * k:.0f} {cx + 82 * k:.0f},{ytab - 130 * k:.0f} L{cx + 86 * k:.0f},{ytab + 30 * k:.0f} Z')
    cuello = f'<path d="M{cx - 16 * k:.0f},{ytab - 226 * k:.0f} L{cx + 16 * k:.0f},{ytab - 226 * k:.0f} L{cx + 19 * k:.0f},{ytab - 166 * k:.0f} L{cx - 19 * k:.0f},{ytab - 166 * k:.0f} Z" fill="{oscurece(piel, 0.88)}"/>'
    escote = f'<path d="M{cx - 24 * k:.0f},{ytab - 172 * k:.0f} L{cx:.0f},{ytab - 140 * k:.0f} L{cx + 24 * k:.0f},{ytab - 172 * k:.0f} Z" fill="{oscurece(piel, 0.88)}"/><path d="M{cx - 26 * k:.0f},{ytab - 173 * k:.0f} L{cx:.0f},{ytab - 138 * k:.0f} L{cx + 26 * k:.0f},{ytab - 173 * k:.0f}" stroke="{oscurece(ropa, 0.7)}" stroke-width="{5 * k:.1f}" fill="none"/>'
    cuerpo = (f'<g id="{pid}"><g class="cuerpo"><path d="{torso}" fill="{ropa}"/><path d="{torso}" fill="url(#brilloRopa)"/>{cuello}{escote}'
              f'<path d="{torso}" fill="none" stroke="{rim}" stroke-width="{2 * k:.1f}" opacity="0.45"/>'
              f'<g class="cab">{cara(pid, cx, ytab - 257 * k, 42 * k, e, expr=expr0)}</g></g></g>')
    def brazo(a, m, i):
        ex = (a[0] + m[0]) / 2 + 38 * k * (1 if m[0] > cx else -1)
        return (f'<path id="{i}" d="M{a[0]:.0f},{a[1]:.0f} Q{ex:.0f},{(a[1] + m[1]) / 2:.0f} {m[0]:.0f},{m[1] - 8 * k:.0f}" stroke="{ropa}" stroke-width="{34 * k:.0f}" stroke-linecap="round" fill="none"/>')
    brazos = (f'<g id="{pid}_brazos">' + brazo(ho, mano2, f"{pid}_bi") + mano_svg(f"{pid}_mi", mano2[0], mano2[1], k, piel)
              + brazo(hs, mano, f"{pid}_bd") + mano_svg(f"{pid}_md", mano[0], mano[1], k, piel) + '</g>')
    return cuerpo, brazos
def mano_a(pid, t, x, y, d=0.45):
    (sx, sy), (mx, my), k = SEN[pid]
    J(f'tl.to("#{pid}_bd", {{attr:{{d:"M{sx:.0f},{sy:.0f} Q{(sx + x) / 2 + 26 * k:.0f},{(sy + y) / 2 - 24 * k:.0f} {x:.0f},{y - 8 * k:.0f}"}}, duration:{d}, ease:"power2.inOut"}}, {t:.2f});')
    J(f'tl.to("#{pid}_md .mv", {{x:{x - mx:.0f}, y:{y - my:.0f}, duration:{d}, ease:"power2.inOut"}}, {t:.2f});')
def mano_reposo(pid, t, d=0.5):
    (sx, sy), (mx, my), k = SEN[pid]
    ex = (sx + mx) / 2 + 38 * k * (1 if mx > sx - 1 else -1)
    J(f'tl.to("#{pid}_bd", {{attr:{{d:"M{sx:.0f},{sy:.0f} Q{ex:.0f},{(sy + my) / 2:.0f} {mx:.0f},{my - 8 * k:.0f}"}}, duration:{d}, ease:"power2.inOut"}}, {t:.2f}); tl.to("#{pid}_md .mv", {{x:0, y:0, duration:{d}, ease:"power2.inOut"}}, {t:.2f});')
def pulsar_con(pid, bid, t, sube=0.5, fuerte=False):
    cx, ytop, s, base = BOT[bid]
    mano_a(pid, t - sube, cx, ytop - 4 * s, sube - 0.05)
    J(f'tl.to("#{pid}_md, #{pid}_bd", {{y:{14 * s:.0f}, duration:0.07, yoyo:true, repeat:1}}, {t:.2f});')
    pulsa(bid, t, fuerte=fuerte)
def persona(x, suelo, h=300, col=None, rim=None, brazo=0, cls="", pid="", pose="pie", lado=1, e=None, espalda=False, expr0="neutral"):
    """Persona de pie, CON CARA (o de espaldas): pelo, cara, ropa, pantalón, zapatos y brazo «brazo» animable."""
    pid = pid or f"pp{int(x)}_{int(suelo)}_{int(h)}"
    e = e or estilo(int(x * 7 + suelo * 3 + h) % 9973)
    k = h / 300
    ropa, piel = e["ropa"], e["piel"]
    pant = random.Random(int(x + h)).choice(("#2a3550", "#3a3f48", "#5a4632", "#1f2a3a", "#6b6f78"))
    sy = suelo
    torso = f'M{x - 34 * k:.0f},{sy - 120 * k:.0f} L{x - 38 * k:.0f},{sy - 222 * k:.0f} Q{x - 36 * k:.0f},{sy - 240 * k:.0f} {x - 14 * k:.0f},{sy - 242 * k:.0f} L{x + 14 * k:.0f},{sy - 242 * k:.0f} Q{x + 36 * k:.0f},{sy - 240 * k:.0f} {x + 38 * k:.0f},{sy - 222 * k:.0f} L{x + 34 * k:.0f},{sy - 120 * k:.0f} Z'
    piernas = (f'<path d="M{x - 30 * k:.0f},{sy - 124 * k:.0f} L{x - 26 * k:.0f},{sy - 8 * k:.0f} L{x - 6 * k:.0f},{sy - 8 * k:.0f} L{x - 2 * k:.0f},{sy - 100 * k:.0f} L{x + 2 * k:.0f},{sy - 100 * k:.0f} L{x + 6 * k:.0f},{sy - 8 * k:.0f} L{x + 26 * k:.0f},{sy - 8 * k:.0f} L{x + 30 * k:.0f},{sy - 124 * k:.0f} Z" fill="{pant}"/>'
               f'<ellipse cx="{x - 16 * k:.0f}" cy="{sy - 4 * k:.0f}" rx="{14 * k:.0f}" ry="{6 * k:.0f}" fill="#1a1a1a"/><ellipse cx="{x + 16 * k:.0f}" cy="{sy - 4 * k:.0f}" rx="{14 * k:.0f}" ry="{6 * k:.0f}" fill="#1a1a1a"/>')
    br = lambda L, c: f'<path d="M{x + L * 34 * k:.0f},{sy - 228 * k:.0f} Q{x + L * 46 * k:.0f},{sy - 180 * k:.0f} {x + L * 42 * k:.0f},{sy - 130 * k:.0f}" stroke="{ropa}" stroke-width="{17 * k:.0f}" stroke-linecap="round" fill="none"/><circle cx="{x + L * 42 * k:.0f}" cy="{sy - 122 * k:.0f}" r="{8.5 * k:.0f}" fill="{piel}"/>'
    brazo_g = f'<g class="brazo" transform="rotate({brazo * lado} {x + 34 * k * lado:.0f} {sy - 228 * k:.0f})">{br(lado, ropa)}</g>'
    sombra = f'<ellipse cx="{x:.0f}" cy="{sy:.0f}" rx="{44 * k:.0f}" ry="{7 * k:.0f}" fill="#000" opacity="0.25"/>'
    rim_s = f'<path d="{torso}" fill="none" stroke="{rim}" stroke-width="{1.8 * k:.1f}" opacity="0.4"/>' if rim else ""
    return (f'<g class="{cls}" id="{pid}">{sombra}{piernas}{br(-lado, ropa)}<path d="{torso}" fill="{ropa}"/><path d="{torso}" fill="url(#brilloRopa)"/>{rim_s}'
            f'<rect x="{x - 8 * k:.0f}" y="{sy - 276 * k:.0f}" width="{16 * k:.0f}" height="{38 * k:.0f}" fill="{oscurece(piel, 0.88)}"/>'
            f'{cara(pid, x, sy - 296 * k, 22 * k, e, espalda=espalda, expr=expr0)}{brazo_g}</g>')

def movil(mid, x, y, s=1.0, texto="", color="#ffffff"):
    """Móvil con la app del banco (cabecera, saldo grande, movimientos) y avisos verde/rojo que se encienden."""
    s *= 1.35
    col = {"#ffffff": "#1b2230", "#7CFFB0": "#1a9a55"}.get(color, color)
    w, h = 124 * s, 200 * s
    x0, y0 = x - w / 2, y - h / 2
    filas = "".join(f'<circle cx="{x0 + 18 * s:.0f}" cy="{y0 + (128 + i * 18) * s:.0f}" r="{5 * s:.1f}" fill="{c}"/><rect x="{x0 + 28 * s:.0f}" y="{y0 + (125 + i * 18) * s:.0f}" width="{48 * s:.0f}" height="{5 * s:.1f}" rx="{2.5 * s:.1f}" fill="#c9d1dc"/>'
                    f'<rect x="{x0 + 86 * s:.0f}" y="{y0 + (125 + i * 18) * s:.0f}" width="{24 * s:.0f}" height="{5 * s:.1f}" rx="{2.5 * s:.1f}" fill="#9aa6b6"/>' for i, c in enumerate(("#f2c14e", "#5fa8d3", "#e2725b")))
    return (f'<g id="{mid}"><rect x="{x0 - 5 * s:.0f}" y="{y0 - 5 * s:.0f}" width="{w + 10 * s:.0f}" height="{h + 10 * s:.0f}" rx="{18 * s:.0f}" fill="#111317"/>'
            f'<rect class="pant" x="{x0:.0f}" y="{y0:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{12 * s:.0f}" fill="#f4f6fa"/>'
            f'<path d="M{x0:.0f},{y0 + 12 * s:.0f} Q{x0:.0f},{y0:.0f} {x0 + 12 * s:.0f},{y0:.0f} L{x0 + w - 12 * s:.0f},{y0:.0f} Q{x0 + w:.0f},{y0:.0f} {x0 + w:.0f},{y0 + 12 * s:.0f} L{x0 + w:.0f},{y0 + 34 * s:.0f} L{x0:.0f},{y0 + 34 * s:.0f} Z" fill="#1f5fa8"/>'
            f'<text x="{x:.0f}" y="{y0 + 22 * s:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="{10 * s:.1f}" fill="#ffffff" letter-spacing="1.5">MI BANCO</text>'
            f'<text x="{x0 + 12 * s:.0f}" y="{y0 + 56 * s:.0f}" font-family="Inter" font-weight="600" font-size="{7.5 * s:.1f}" fill="#7a8696">Saldo disponible</text>'
            f'<text class="saldo" x="{x0 + 12 * s:.0f}" y="{y0 + 80 * s:.0f}" font-family="Inter" font-weight="900" font-size="{15 * s:.1f}" fill="{col}">{texto}</text>'
            f'<rect x="{x0 + 12 * s:.0f}" y="{y0 + 92 * s:.0f}" width="{w - 24 * s:.0f}" height="{1.5 * s:.1f}" fill="#dfe4ea"/>'
            f'<text x="{x0 + 12 * s:.0f}" y="{y0 + 110 * s:.0f}" font-family="Inter" font-weight="700" font-size="{7 * s:.1f}" fill="#7a8696">Últimos movimientos</text>{filas}'
            f'<g class="ok" opacity="0"><rect x="{x0 + 6 * s:.0f}" y="{y0 + h - 34 * s:.0f}" width="{w - 12 * s:.0f}" height="{26 * s:.0f}" rx="{8 * s:.0f}" fill="#1a9a55"/>'
            f'<text x="{x:.0f}" y="{y0 + h - 17 * s:.0f}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="{7.5 * s:.1f}" fill="#ffffff">Ingreso recibido ✓</text></g>'
            f'<g class="aviso" opacity="0"><rect x="{x0 + 6 * s:.0f}" y="{y0 + h - 34 * s:.0f}" width="{w - 12 * s:.0f}" height="{26 * s:.0f}" rx="{8 * s:.0f}" fill="#d8261a"/>'
            f'<text x="{x:.0f}" y="{y0 + h - 17 * s:.0f}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="{7 * s:.1f}" fill="#ffffff">Cuenta vaciada ⚠</text></g></g>')

TELAS = {"humilde": "#c8553d", "moderno": "#9fc7c4", "elegante": "#7a1f2b", "industrial": "#3a5a6a", "cocina": "#f2e6c8", "rosa": "#ffffff", "noche": "#2a3550"}
def decor(tipo, seed, ytab, x0=0, w=1080):
    """Vida en la pared: cortinas que se mecen, cuadros, estante con libros y planta, reloj de pared."""
    r_ = random.Random(seed * 13)
    cx = x0 + w / 2
    vw, vh = w * 0.5, 1920 * 0.3
    vx, vy = cx - vw / 2, ytab - 620 - vh * 0.5
    tela = TELAS[tipo]
    s = []
    for L in (-1, 1):
        bx = vx - 40 if L < 0 else vx + vw - 70
        s.append(f'<g class="cortina"><path d="M{bx},{vy - 40:.0f} L{bx + 110},{vy - 40:.0f} C{bx + 100},{vy + vh * 0.5:.0f} {bx + 120},{vy + vh:.0f} {bx + 105 - L * 20},{vy + vh + 120:.0f} L{bx + 5 + L * 10},{vy + vh + 120:.0f} C{bx - 5},{vy + vh:.0f} {bx + 10},{vy + vh * 0.5:.0f} {bx},{vy - 40:.0f} Z" fill="{tela}"/>'
                 + "".join(f'<path d="M{bx + 18 + i * 24},{vy - 40:.0f} C{bx + 14 + i * 24},{vy + vh * 0.5:.0f} {bx + 26 + i * 24},{vy + vh:.0f} {bx + 20 + i * 24},{vy + vh + 120:.0f}" stroke="#000" stroke-opacity="0.12" stroke-width="5" fill="none"/>' for i in range(4)) + '</g>')
    s.append(f'<rect x="{vx - 70:.0f}" y="{vy - 52:.0f}" width="{vw + 140:.0f}" height="12" rx="6" fill="#5a4632"/>')
    # cuadros
    for k_, (fx, fy, fw, fh) in enumerate(((x0 + w * 0.05, vy + 40, 130, 170), (x0 + w * 0.82, vy + 20, 150, 110))):
        c1, c2 = r_.choice((("#f2c14e", "#e2725b"), ("#5fa8d3", "#2f6f9a"), ("#7cc47f", "#2f8a3a"), ("#c78bff", "#7a3fd0")))
        s.append(f'<rect x="{fx:.0f}" y="{fy:.0f}" width="{fw}" height="{fh}" fill="#5a3a22"/><rect x="{fx + 10:.0f}" y="{fy + 10:.0f}" width="{fw - 20}" height="{fh - 20}" fill="{c1}"/>'
                 f'<circle cx="{fx + fw * 0.62:.0f}" cy="{fy + fh * 0.38:.0f}" r="{fw * 0.14:.0f}" fill="#fff6d8" opacity="0.85"/><path d="M{fx + 10:.0f},{fy + fh - 10:.0f} L{fx + fw * 0.4:.0f},{fy + fh * 0.5:.0f} L{fx + fw * 0.65:.0f},{fy + fh * 0.72:.0f} L{fx + fw - 10:.0f},{fy + fh * 0.45:.0f} L{fx + fw - 10:.0f},{fy + fh - 10:.0f} Z" fill="{c2}"/>')
    # estante con libros y planta colgante
    ex, ey = x0 + w * 0.04, ytab - 150
    s.append(f'<rect x="{ex:.0f}" y="{ey:.0f}" width="190" height="12" fill="#6b4a2a"/>'
             + "".join(f'<rect x="{ex + 8 + i * 24:.0f}" y="{ey - h_:.0f}" width="20" height="{h_}" rx="2" fill="{c}"/>' for i, (h_, c) in enumerate(((70, "#e2725b"), (84, "#2f6f9a"), (62, "#f2c14e"), (78, "#7cc47f"), (66, "#8a5cd6"))))
             + f'<path d="M{ex + 150:.0f},{ey:.0f} Q{ex + 140:.0f},{ey - 40:.0f} {ex + 162:.0f},{ey - 46:.0f} L{ex + 180:.0f},{ey - 46:.0f} Q{ex + 190:.0f},{ey - 40:.0f} {ex + 182:.0f},{ey:.0f} Z" fill="#c65b46"/>'
             + "".join(f'<path class="hoja" d="M{ex + 166:.0f},{ey - 44:.0f} q{a},{-30 - i * 6} {b},{-8 - i * 4}" stroke="#3f9a5a" stroke-width="9" fill="none" stroke-linecap="round"/>' for i, (a, b) in enumerate(((-30, -50), (25, 46), (-8, -18), (14, 30)))))
    # reloj
    rx_, ry_ = x0 + w * 0.88, ytab - 330
    s.append(f'<circle cx="{rx_:.0f}" cy="{ry_:.0f}" r="44" fill="#ffffff" stroke="#3a2a1a" stroke-width="7"/>'
             + "".join(f'<path d="M{rx_ + 36 * math.cos(a):.0f},{ry_ + 36 * math.sin(a):.0f} L{rx_ + 30 * math.cos(a):.0f},{ry_ + 30 * math.sin(a):.0f}" stroke="#3a2a1a" stroke-width="3"/>' for a in [i * math.pi / 6 for i in range(12)])
             + f'<path d="M{rx_:.0f},{ry_:.0f} L{rx_:.0f},{ry_ - 24:.0f}" stroke="#3a2a1a" stroke-width="5" stroke-linecap="round"/><path class="aguja" d="M{rx_:.0f},{ry_:.0f} L{rx_ + 30:.0f},{ry_:.0f}" stroke="#d8261a" stroke-width="3" stroke-linecap="round"/>')
    return "".join(s)
def mesa_objs(cx, ytab, seed, lado=1):
    """Objetos sobre la mesa: taza humeante y libreta con boli (al lado contrario del botón)."""
    r_ = random.Random(seed * 7)
    tx = cx - lado * 330
    taza = r_.choice(("#ffffff", "#f2c14e", "#5fa8d3", "#e2725b"))
    return (f'<g><ellipse cx="{tx}" cy="{ytab + 8}" rx="46" ry="12" fill="#000" opacity="0.2"/><path d="M{tx - 38},{ytab - 62} L{tx + 38},{ytab - 62} L{tx + 32},{ytab + 4} Q{tx},{ytab + 14} {tx - 32},{ytab + 4} Z" fill="{taza}"/>'
            f'<path d="M{tx + 36},{ytab - 48} q30,6 22,30 q-6,14 -26,10" stroke="{taza}" stroke-width="9" fill="none"/><ellipse cx="{tx}" cy="{ytab - 62}" rx="38" ry="9" fill="#5a3a22"/>'
            + "".join(f'<path class="vapor" d="M{tx - 14 + i * 14},{ytab - 72} q-12,-24 0,-48 q12,-24 0,-48" stroke="#ffffff" stroke-width="6" fill="none" opacity="0.5" stroke-linecap="round"/>' for i in range(3))
            + f'<g transform="rotate({-8 * lado} {cx + lado * 330} {ytab})"><rect x="{cx + lado * 330 - 70}" y="{ytab - 22}" width="140" height="44" rx="4" fill="#f4efe4" transform="skewX(-25)"/>'
            f'<rect x="{cx + lado * 330 - 40}" y="{ytab - 8}" width="110" height="6" rx="3" fill="#1f5fa8"/></g></g>')
def vida_global(dur):
    """Animaciones de ambiente que dan vida a todos los planos (cortinas, plantas, vapor, agujas del reloj)."""
    n = int(dur / 2.4) + 1
    J(f'tl.fromTo(".cortina", {{skewX:0}}, {{skewX:1.6, transformOrigin:"50% 0%", duration:1.2, yoyo:true, repeat:{n * 2}, ease:"sine.inOut", immediateRender:false}}, 0);')
    J(f'tl.fromTo(".hoja", {{rotation:-4}}, {{rotation:4, transformOrigin:"0% 100%", duration:1.4, yoyo:true, repeat:{n * 2}, ease:"sine.inOut", immediateRender:false}}, 0);')
    J(f'tl.fromTo(".vapor", {{y:0, opacity:0.55}}, {{y:-60, opacity:0, duration:1.8, stagger:0.6, repeat:{n * 2}, ease:"sine.out", immediateRender:false}}, 0);')
    J(f'tl.fromTo(".aguja", {{rotation:0}}, {{rotation:{int(dur) * 6}, transformOrigin:"0% 50%", duration:{dur:.2f}, ease:"steps({int(dur)})", immediateRender:false}}, 0);')

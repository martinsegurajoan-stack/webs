#!/usr/bin/env python3
"""«¿Y si todo el mundo tuviera un botón para ganar un millón?» — animado (HyperFrames + GSAP), misma identidad que «puertas»
documental/thriller serio: noche, haces de luz, niebla, partículas, siluetas sin caras. Misma voz y subtítulos de siempre.
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
tl, FX, OVR, ESC, DEFS = [], [], [], [], []
def J(s): tl.append(s)
NID = [0]
def nid(p="e"):
    NID[0] += 1
    return f"{p}{NID[0]}"
BG, INK, MUTED = "#04060b", "#eef3fa", "#8796ad"
AMB, ORO, CAL, RED, TEAL, ICE = "#ffb85c", "#ffd27a", "#fff1d6", "#ff3b2f", "#2bb3c0", "#9fdcff"
SIL = "#05070c"                                     # siluetas: negro azulado, sin caras

def pop(sel, t, d=0.45, frm="opacity:0, y:24", ease="power3.out"):
    J(f'tl.set("{sel}", {{opacity:0}}, 0);')
    J(f'tl.fromTo("{sel}", {{{frm}}}, {{opacity:1, x:0, y:0, scale:1, duration:{d}, ease:"{ease}", immediateRender:false}}, {t:.2f});')
def fuera(sel, t, d=0.3):
    J(f'tl.to("{sel}", {{opacity:0, duration:{d}, ease:"power2.in"}}, {t:.2f});')
def escena(eid, cuerpo, w=1080):
    ESC.append(f'<div class="esc" id="{eid}"><div class="cam" id="{eid}-cam"><svg width="{w}" height="1920" viewBox="0 0 {w} 1920" style="position:absolute;left:0;top:0;overflow:visible">{cuerpo}</svg></div></div>')
def mostrar(eid, t0, t1):
    J(f'tl.set("#{eid}", {{opacity:0}}, 0); tl.set("#{eid}", {{opacity:1}}, {t0:.2f}); tl.set("#{eid}", {{opacity:0}}, {t1:.2f});')
def camara(eid, t0, t1, desde, hasta, ease="sine.inOut"):
    x0, y0, s0 = desde; x1, y1, s1 = hasta
    J(f'tl.fromTo("#{eid}-cam", {{x:{x0}, y:{y0}, scale:{s0}}}, {{x:{x1}, y:{y1}, scale:{s1}, duration:{t1 - t0:.2f}, ease:"{ease}", immediateRender:false}}, {t0:.2f});')
def enfoca(px, py, s):
    """Cámara (transform-origin en el centro 540,960) que deja el punto (px,py) en el centro con zoom s."""
    return (round(-s * (px - 540)), round(-s * (py - 960)), s)
def nota(txt, t, t_out, x, y, color=AMB, sub=""):
    """Nota COMPACTA (píldora pequeña) que entra deslizándose y se va sola en ~2,6 s. Nunca sobre personajes."""
    i = nid("nt")
    OVR.append(f'<div class="nota" id="{i}" style="left:{x}px;top:{y}px;--c:{color}"><b></b><span class="ct">{txt}</span>' + (f'<span class="cs">{sub}</span>' if sub else "") + '</div>')
    J(f'tl.set("#{i}", {{opacity:0}}, 0); tl.fromTo("#{i}", {{opacity:0, x:-24, filter:"blur(6px)"}}, {{opacity:1, x:0, filter:"blur(0px)", duration:0.35, ease:"power3.out", immediateRender:false}}, {t:.2f});')
    J(f'tl.to("#{i}", {{opacity:0, x:12, filter:"blur(4px)", duration:0.3, ease:"power2.in"}}, {min(t_out, t + 2.6):.2f});')
    return i
def luz(t, col="#ffe2b0", d=0.55):
    """Transición de luz cálida (la luz de la puerta lo llena todo y se abre al siguiente plano)."""
    J(f'tl.set("#luz", {{background:"radial-gradient(60% 45% at 50% 50%, #ffffff, {col} 45%, rgba(255,190,110,0.6))"}}, {t - d:.2f});')
    J(f'tl.fromTo("#luz", {{opacity:0}}, {{opacity:1, duration:{d:.2f}, ease:"power2.in", immediateRender:false}}, {t - d:.2f}); tl.to("#luz", {{opacity:0, duration:{d + 0.2:.2f}, ease:"power2.out"}}, {t:.2f});')
def negro(t, d=0.35):
    J(f'tl.fromTo("#negro", {{opacity:0}}, {{opacity:1, duration:{d}, ease:"power2.in", immediateRender:false}}, {t - d:.2f}); tl.to("#negro", {{opacity:0, duration:{d + 0.15}, ease:"power2.out"}}, {t:.2f});')

# ------------------------------------------------------------------ piezas de dibujo
rr = random.Random(7)
def grad_lin(gid, stops, x1=0, y1=0, x2=0, y2=1):
    DEFS.append(f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">' + "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops) + '</linearGradient>')
def grad_rad(gid, stops, cx=0.5, cy=0.5, r=0.5):
    DEFS.append(f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}">' + "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops) + '</radialGradient>')
PAL = {"oro": ("#fff6e0", "#ffd27a", "#ff9a3c"), "frio": ("#ffffff", "#bfeaff", "#4fa8d8"), "rojo": ("#ffd0c0", "#ff5a3c", "#a3120a"),
       "verde": ("#f0fff4", "#9ff2c0", "#2fa36b"), "lila": ("#fbefff", "#d6a8ff", "#7a3fd0"), "cian": ("#ffffff", "#a8f4ff", "#1fb6c9")}
for k, (a, b, c) in PAL.items():
    grad_lin(f"hueco_{k}", ((0, a, 1), (0.55, b, 1), (1, c, 1)))
    grad_rad(f"halo_{k}", ((0, b, 0.55), (0.45, c, 0.22), (1, c, 0)))
    grad_lin(f"cono_{k}", ((0, b, 0.55), (1, c, 0)))
def puerta(pid, cx, suelo, w, h, pal="oro", abre=0.0, marco="#0d1016", hoja="#141821", haz=1.0, num="", interior="", en_hoja=""):
    """Puerta exenta y realista (el MISMO modelo en todo el vídeo): halo, cono de luz, marco con bisel, hueco luminoso
    (o lo que hay al otro lado: interior) y hoja. abre>0 → hoja entreabierta en perspectiva (gira hacia cámara).
    Para animar la apertura se usa abre=0 y se tweenea .hoja con scaleX (transformOrigin 0% 0%)."""
    x0, y0 = cx - w / 2, suelo - h
    fr = max(10, w * 0.07)
    hx, hy, hw, hh = x0 + fr, y0 + fr, w - 2 * fr, h - fr
    s = [f'<g id="{pid}">',
         f'<ellipse class="halo" cx="{cx}" cy="{suelo - h * 0.45:.0f}" rx="{w * 2.3:.0f}" ry="{h * 1.05:.0f}" fill="url(#halo_{pal})" opacity="{haz:.2f}"/>',
         f'<path class="cono" d="M{hx:.0f},{suelo} L{hx + hw:.0f},{suelo} L{cx + w * 2.6:.0f},{suelo + h * 0.55:.0f} L{cx - w * 2.6:.0f},{suelo + h * 0.55:.0f} Z" fill="url(#cono_{pal})" opacity="{0.85 * haz:.2f}"/>',
         f'<rect x="{x0 - 4:.0f}" y="{y0 - 4:.0f}" width="{w + 8:.0f}" height="{h + 4:.0f}" fill="#000" opacity="0.5"/>',
         f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{marco}"/>',
         f'<path d="M{x0:.0f},{y0:.0f} L{x0 + w:.0f},{y0:.0f} L{x0 + w - fr:.0f},{y0 + fr:.0f} L{x0 + fr:.0f},{y0 + fr:.0f} Z" fill="#ffffff" opacity="0.07"/>',
         f'<path d="M{x0 + w:.0f},{y0:.0f} L{x0 + w:.0f},{suelo} L{x0 + w - fr:.0f},{suelo} L{x0 + w - fr:.0f},{y0 + fr:.0f} Z" fill="#000" opacity="0.25"/>',
         f'<rect class="hueco" x="{hx:.0f}" y="{hy:.0f}" width="{hw:.0f}" height="{hh:.0f}" fill="url(#hueco_{pal})"/>']
    if interior:
        DEFS.append(f'<clipPath id="{pid}_c"><rect x="{hx:.0f}" y="{hy:.0f}" width="{hw:.0f}" height="{hh:.0f}"/></clipPath>')
        s.append(f'<g clip-path="url(#{pid}_c)">{interior}</g>')
    pan = lambda X, Y, W, H: f'<rect x="{X:.0f}" y="{Y:.0f}" width="{W:.0f}" height="{H:.0f}" fill="none" stroke="#ffffff" stroke-opacity="0.07" stroke-width="3"/><rect x="{X + 3:.0f}" y="{Y + 3:.0f}" width="{W - 6:.0f}" height="{H - 6:.0f}" fill="none" stroke="#000" stroke-opacity="0.35" stroke-width="2"/>'
    if abre > 0:                                     # hoja entreabierta en perspectiva: el canto libre se acerca a cámara
        th = math.radians(abre * 78)
        xf = hx + hw * math.cos(th)
        e = h * 0.07 * math.sin(th)
        ty = lambda u: (hy - e * u, suelo + e * 0.6 * u)
        P = lambda u, v: (hx + (xf - hx) * u, ty(u)[0] + (ty(u)[1] - ty(u)[0]) * v)
        quad = lambda u0, u1, v0, v1: " ".join(f"{x:.0f},{y:.0f}" for x, y in (P(u0, v0), P(u1, v0), P(u1, v1), P(u0, v1)))
        s.append(f'<g class="hoja"><polygon points="{quad(0, 1, 0, 1)}" fill="{hoja}"/><polygon points="{quad(0, 1, 0, 1)}" fill="url(#hojaSombra)"/>'
                 f'<polygon points="{quad(0.14, 0.86, 0.07, 0.43)}" fill="none" stroke="#ffffff" stroke-opacity="0.07" stroke-width="3"/>'
                 f'<polygon points="{quad(0.14, 0.86, 0.5, 0.88)}" fill="none" stroke="#ffffff" stroke-opacity="0.07" stroke-width="3"/>'
                 f'<circle cx="{P(0.88, 0.55)[0]:.0f}" cy="{P(0.88, 0.55)[1]:.0f}" r="{max(3, w * 0.03):.1f}" fill="#c9a24a"/>'
                 f'<polygon points="{xf:.0f},{ty(1)[0]:.0f} {xf + max(6, w * 0.035):.0f},{ty(1)[0] + 4:.0f} {xf + max(6, w * 0.035):.0f},{ty(1)[1] - 2:.0f} {xf:.0f},{ty(1)[1]:.0f}" fill="url(#hueco_{pal})" opacity="0.95"/></g>')
    else:
        s.append(f'<g class="hoja"><rect x="{hx:.0f}" y="{hy:.0f}" width="{hw:.0f}" height="{hh:.0f}" fill="{hoja}"/>'
                 + pan(hx + hw * 0.14, hy + h * 0.07, hw * 0.72, h * 0.36) + pan(hx + hw * 0.14, hy + h * 0.5, hw * 0.72, h * 0.38)
                 + f'<circle cx="{hx + hw * 0.88:.0f}" cy="{y0 + h * 0.55:.0f}" r="{max(3, w * 0.025):.1f}" fill="#c9a24a"/>'
                 + (f'<text x="{cx:.0f}" y="{y0 + h * 0.22:.0f}" text-anchor="middle" font-family="Georgia" font-size="{w * 0.12:.0f}" fill="#c9a24a">{num}</text>' if num else "")
                 + en_hoja + f'<rect class="filo" x="{hx + hw - 4:.0f}" y="{hy:.0f}" width="4" height="{hh:.0f}" fill="url(#hueco_{pal})" opacity="0.9"/></g>')
    s.append(f'<rect x="{hx:.0f}" y="{suelo - 3:.0f}" width="{hw:.0f}" height="3" fill="url(#hueco_{pal})"/></g>')
    return "".join(s)
grad_lin("hojaSombra", ((0, "#000000", 0.55), (1, "#000000", 0.0)), 0, 0, 1, 0)
def persona(x, suelo, h=300, col=SIL, rim=None, brazo=0, cls="", pid="", pose="pie", lado=1):
    """Silueta humana sin rasgos (de espaldas o de perfil), con borde de luz opcional."""
    k = h / 300
    def P_(px, py): return f"{x + px * k * lado:.1f},{suelo - py * k:.1f}"
    cuerpo = (f'M{P_(-26, 0)} L{P_(-20, 120)} L{P_(-30, 125)} L{P_(-34, 230)} C{P_(-30, 250)} {P_(-14, 256)} {P_(0, 256)} C{P_(14, 256)} {P_(30, 250)} {P_(34, 230)} '
              f'L{P_(30, 125)} L{P_(20, 120)} L{P_(26, 0)} L{P_(8, 0)} L{P_(2, 112)} L{P_(-2, 112)} L{P_(-8, 0)} Z')
    cab = f'<ellipse cx="{x:.1f}" cy="{suelo - 278 * k:.1f}" rx="{19 * k:.1f}" ry="{23 * k:.1f}" fill="{col}"/>'
    cuello = f'<rect x="{x - 8 * k:.1f}" y="{suelo - 262 * k:.1f}" width="{16 * k:.1f}" height="{12 * k:.1f}" fill="{col}"/>'
    bra = (f'<g class="brazo" style="transform-origin:{x + 30 * k * lado:.0f}px {suelo - 232 * k:.0f}px;transform:rotate({brazo * lado}deg)">'
           f'<path d="M{P_(26, 236)} L{P_(40, 236)} L{P_(46, 140)} L{P_(36, 138)} Z" fill="{col}"/></g>'
           f'<path d="M{P_(-26, 236)} L{P_(-40, 236)} L{P_(-46, 140)} L{P_(-36, 138)} Z" fill="{col}"/>')
    rim_s = (f'<path d="{cuerpo}" fill="none" stroke="{rim}" stroke-width="{min(2.6, 1.3 * k):.1f}" opacity="0.42"/>'
             f'<ellipse cx="{x:.1f}" cy="{suelo - 278 * k:.1f}" rx="{19 * k:.1f}" ry="{23 * k:.1f}" fill="none" stroke="{rim}" stroke-width="{min(2.6, 1.3 * k):.1f}" opacity="0.42"/>') if rim else ""
    return f'<g class="{cls}" id="{pid}"><ellipse cx="{x:.1f}" cy="{suelo:.1f}" rx="{42 * k:.1f}" ry="{6 * k:.1f}" fill="#000" opacity="0.5"/><path d="{cuerpo}" fill="{col}"/>{cuello}{cab}{bra}{rim_s}</g>'
def polvo(pid, n, x0, x1, y0, y1, col="#ffe2b0", seed=3, rmax=3.2):
    r_ = random.Random(seed)
    return f'<g id="{pid}" class="polvo">' + "".join(f'<circle cx="{r_.uniform(x0, x1):.0f}" cy="{r_.uniform(y0, y1):.0f}" r="{r_.uniform(0.8, rmax):.1f}" fill="{col}" opacity="{r_.uniform(0.25, 0.85):.2f}"/>' for _ in range(n)) + '</g>'
def mover_polvo(pid, t0, t1, dy=-120, dx=30):
    J(f'tl.fromTo("#{pid}", {{x:0, y:0}}, {{x:{dx}, y:{dy}, duration:{t1 - t0:.2f}, ease:"none", immediateRender:false}}, {t0:.2f});')
def niebla(y, h, col="#9fc7d6", op=0.12, w=1080, x=0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#niebla)" opacity="{op}" style="mix-blend-mode:screen"/>'
grad_lin("niebla", ((0, "#cfe6f0", 0), (0.5, "#cfe6f0", 1), (1, "#cfe6f0", 0)))
grad_lin("noche", ((0, "#03050a", 1), (0.55, "#0a1520", 1), (1, "#10232c", 1)))
grad_lin("suelo", ((0, "#0c141b", 1), (1, "#020305", 1)))
grad_lin("muro", ((0, "#0b1016", 1), (1, "#06080c", 1)))
def skyline(seed, base, alto=1.0, col="#070b11", col2="#0a1018", luces=0.18, w=1080, x0=-60):
    r_ = random.Random(seed); s = []
    x = x0
    while x < w + 60:
        bw, bh = r_.randint(90, 180), r_.randint(300, 760) * alto
        s.append(f'<rect x="{x}" y="{base - bh:.0f}" width="{bw}" height="{bh:.0f}" fill="{col2}"/>')
        x += bw + r_.randint(4, 20)
    x = x0 - 30
    while x < w + 90:
        bw, bh = r_.randint(140, 240), r_.randint(420, 1000) * alto
        y0 = base - bh
        s.append(f'<rect x="{x}" y="{y0:.0f}" width="{bw}" height="{bh:.0f}" fill="{col}"/>')
        for i in range(max(2, bw // 46)):
            for j in range(int((bh - 40) // 58)):
                if r_.random() < luces:
                    s.append(f'<rect x="{x + 14 + i * 44}" y="{y0 + 26 + j * 58:.0f}" width="20" height="28" fill="{r_.choice(("#ffcf7a", "#ffe0a8", "#9fd6ff", "#f2b468"))}" opacity="{r_.uniform(0.35, 0.85):.2f}"/>')
        x += bw + r_.randint(8, 26)
    return "".join(s)


# ================================================================== PIEZAS DEL BOTÓN (mismo diseño en todo el vídeo)
grad_rad("domoG", ((0, "#ff8a7a", 1), (0.45, "#e8261a", 1), (1, "#7a0a06", 1)), 0.38, 0.3, 0.75)
grad_lin("baseG", ((0, "#4a505a", 1), (0.5, "#2a2e35", 1), (1, "#16181c", 1)))
grad_rad("brilloRojo", ((0, "#ff5a40", 0.75), (0.5, "#ff3020", 0.25), (1, "#ff3020", 0)))
grad_rad("brilloOro", ((0, "#ffe7a0", 0.8), (0.5, "#ffc040", 0.25), (1, "#ffc040", 0)))
def boton(bid, cx, cy, s=1.0):
    """Botón rojo: base de metal grafito + cúpula roja brillante. cy = altura de la superficie de la mesa."""
    w, hb, rx, ry = 230 * s, 46 * s, 84 * s, 66 * s
    top = cy - hb
    return (f'<g id="{bid}"><ellipse cx="{cx}" cy="{cy + 6 * s:.0f}" rx="{w * 0.62:.0f}" ry="{18 * s:.0f}" fill="#000" opacity="0.28"/>'
            f'<ellipse class="glow" cx="{cx}" cy="{top - ry * 0.4:.0f}" rx="{w * 1.4:.0f}" ry="{w:.0f}" fill="url(#brilloRojo)" opacity="0.35"/>'
            f'<path d="M{cx - w / 2:.0f},{top:.0f} L{cx - w / 2:.0f},{cy - 6 * s:.0f} Q{cx - w / 2:.0f},{cy:.0f} {cx - w / 2 + 12 * s:.0f},{cy:.0f} L{cx + w / 2 - 12 * s:.0f},{cy:.0f} Q{cx + w / 2:.0f},{cy:.0f} {cx + w / 2:.0f},{cy - 6 * s:.0f} L{cx + w / 2:.0f},{top:.0f} Z" fill="url(#baseG)"/>'
            f'<ellipse cx="{cx}" cy="{top:.0f}" rx="{w / 2:.0f}" ry="{20 * s:.0f}" fill="#3a3f48"/><ellipse cx="{cx}" cy="{top:.0f}" rx="{w / 2 - 10 * s:.0f}" ry="{15 * s:.0f}" fill="#1a1c20"/>'
            f'<ellipse cx="{cx}" cy="{top:.0f}" rx="{rx + 8 * s:.0f}" ry="{12 * s:.0f}" fill="#c9ccd2"/>'
            f'<g class="domo"><path d="M{cx - rx:.0f},{top:.0f} C{cx - rx:.0f},{top - ry * 1.3:.0f} {cx + rx:.0f},{top - ry * 1.3:.0f} {cx + rx:.0f},{top:.0f} A{rx:.0f},{11 * s:.0f} 0 0 1 {cx - rx:.0f},{top:.0f} Z" fill="url(#domoG)"/>'
            f'<ellipse cx="{cx - rx * 0.32:.0f}" cy="{top - ry * 0.62:.0f}" rx="{rx * 0.32:.0f}" ry="{ry * 0.18:.0f}" fill="#ffffff" opacity="0.75" transform="rotate(-18 {cx - rx * 0.32:.0f} {top - ry * 0.62:.0f})"/></g></g>')
BOT = {}                                              # posición de cada botón (para que la mano llegue justo encima)
def pon_boton(bid, cx, cy, s=1.0):
    BOT[bid] = (cx, cy - 46 * s - 66 * s * 0.95, s, cy - 46 * s)
    return boton(bid, cx, cy, s)
def pulsa(bid, t, fx=True, fuerte=False):
    cx, ytop, s, base = BOT[bid]
    J(f'tl.fromTo("#{bid} .domo", {{scaleY:1, svgOrigin:"{cx} {base:.0f}"}}, {{scaleY:0.55, svgOrigin:"{cx} {base:.0f}", duration:0.07, yoyo:true, repeat:1, ease:"power2.in", immediateRender:false}}, {t:.2f});')
    J(f'tl.fromTo("#{bid} .glow", {{opacity:0.35}}, {{opacity:1, scale:1.25, svgOrigin:"{cx} {ytop:.0f}", duration:0.12, yoyo:true, repeat:1, immediateRender:false}}, {t:.2f});')
    if fx:
        FX.append(("clic2" if fuerte else "clic", t))
SEN = {}
def sentado(pid, cx, ytab, h=300, rim="#ffe2b0", col="#1b2230", lado_mano=1):
    """Persona sentada tras la mesa (silueta a contraluz, sin rasgos). Brazo «bd» con mano que puede ir al botón."""
    k = h / 300
    hs = (cx + 62 * k * lado_mano, ytab - 168 * k)                 # hombro de la mano activa
    ho = (cx - 62 * k * lado_mano, ytab - 168 * k)
    mano = (cx + 70 * k * lado_mano, ytab + 18 * k); mano2 = (cx - 70 * k * lado_mano, ytab + 18 * k)
    SEN[pid] = (hs, mano, k)
    brazo = lambda a, m, i: f'<path id="{i}" d="M{a[0]:.0f},{a[1]:.0f} Q{(a[0] + m[0]) / 2 + 30 * k * (1 if m[0] > cx else -1):.0f},{(a[1] + m[1]) / 2:.0f} {m[0]:.0f},{m[1]:.0f}" stroke="{col}" stroke-width="{30 * k:.0f}" stroke-linecap="round" fill="none"/>'
    torso = (f'M{cx - 80 * k:.0f},{ytab + 20 * k:.0f} L{cx - 74 * k:.0f},{ytab - 150 * k:.0f} Q{cx - 70 * k:.0f},{ytab - 182 * k:.0f} {cx - 30 * k:.0f},{ytab - 186 * k:.0f} '
             f'L{cx + 30 * k:.0f},{ytab - 186 * k:.0f} Q{cx + 70 * k:.0f},{ytab - 182 * k:.0f} {cx + 74 * k:.0f},{ytab - 150 * k:.0f} L{cx + 80 * k:.0f},{ytab + 20 * k:.0f} Z')
    return (f'<g id="{pid}"><g class="cuerpo"><path d="{torso}" fill="{col}"/><path d="{torso}" fill="none" stroke="{rim}" stroke-width="{2.2 * k:.1f}" opacity="0.55"/>'
            f'<g class="cab"><rect x="{cx - 12 * k:.0f}" y="{ytab - 204 * k:.0f}" width="{24 * k:.0f}" height="{22 * k:.0f}" fill="{col}"/>'
            f'<ellipse cx="{cx}" cy="{ytab - 238 * k:.0f}" rx="{30 * k:.0f}" ry="{37 * k:.0f}" fill="{col}"/><ellipse cx="{cx}" cy="{ytab - 238 * k:.0f}" rx="{30 * k:.0f}" ry="{37 * k:.0f}" fill="none" stroke="{rim}" stroke-width="{2.2 * k:.1f}" opacity="0.6"/></g></g></g>',
            f'<g id="{pid}_brazos">' + brazo(ho, mano2, f"{pid}_bi") + f'<circle cx="{mano2[0]:.0f}" cy="{mano2[1]:.0f}" r="{17 * k:.0f}" fill="{col}"/>'
            + brazo(hs, mano, f"{pid}_bd") + f'<circle id="{pid}_md" cx="{mano[0]:.0f}" cy="{mano[1]:.0f}" r="{17 * k:.0f}" fill="{col}"/></g>')
def mano_a(pid, t, x, y, d=0.45):
    """Mueve la mano activa a (x,y) con el brazo curvándose de forma natural."""
    (sx, sy), _, k = SEN[pid]
    J(f'tl.to("#{pid}_bd", {{attr:{{d:"M{sx:.0f},{sy:.0f} Q{(sx + x) / 2 + 20 * k:.0f},{(sy + y) / 2 - 30 * k:.0f} {x:.0f},{y:.0f}"}}, duration:{d}, ease:"power2.inOut"}}, {t:.2f}); tl.to("#{pid}_md", {{attr:{{cx:{x:.0f}, cy:{y:.0f}}}, duration:{d}, ease:"power2.inOut"}}, {t:.2f});')
def mano_reposo(pid, t, d=0.5):
    (sx, sy), (mx, my), k = SEN[pid]
    J(f'tl.to("#{pid}_bd", {{attr:{{d:"M{sx:.0f},{sy:.0f} Q{(sx + mx) / 2 + 30 * k * (1 if mx > sx - 1 else -1):.0f},{(sy + my) / 2:.0f} {mx:.0f},{my:.0f}"}}, duration:{d}, ease:"power2.inOut"}}, {t:.2f}); tl.to("#{pid}_md", {{attr:{{cx:{mx:.0f}, cy:{my:.0f}}}, duration:{d}, ease:"power2.inOut"}}, {t:.2f});')
def pulsar_con(pid, bid, t, sube=0.5, fuerte=False):
    """La mano va al botón, lo pulsa (t) y vuelve."""
    cx, ytop, s, base = BOT[bid]
    mano_a(pid, t - sube, cx, ytop - 8 * s, sube - 0.05)
    J(f'tl.to("#{pid}_md, #{pid}_bd", {{y:{14 * s:.0f}, duration:0.07, yoyo:true, repeat:1}}, {t:.2f});')
    pulsa(bid, t, fuerte=fuerte)
def respira(pid, t0, t1):
    J(f'tl.fromTo("#{pid} .cuerpo", {{y:0}}, {{y:-4, duration:1.1, yoyo:true, repeat:{max(1, int((t1 - t0) / 1.1))}, ease:"sine.inOut", immediateRender:false}}, {t0:.2f});')
def cabeza(pid, t, rot, d=0.5):
    J(f'tl.to("#{pid} .cab", {{rotation:{rot}, transformOrigin:"50% 100%", duration:{d}, ease:"sine.inOut"}}, {t:.2f});')

# ------------------------------------------------------------------ habitaciones luminosas (cada una con personalidad)
grad_lin("cieloDia", ((0, "#5fb2ec", 1), (1, "#d6f0ff", 1)))
grad_lin("cieloTarde", ((0, "#3a5fa8", 1), (0.6, "#f2a26a", 1), (1, "#ffd59a", 1)))
grad_lin("cieloNoche", ((0, "#0b1430", 1), (1, "#28406e", 1)))
grad_lin("rayoLuz", ((0, "#fff6d8", 0.55), (1, "#fff6d8", 0)))
grad_lin("maderaM", ((0, "#b7814e", 1), (1, "#7d4f2a", 1)))
grad_lin("maderaF", ((0, "#6b3f20", 1), (1, "#3d220f", 1)))
grad_lin("blancoM", ((0, "#f4f4f2", 1), (1, "#cfd3d6", 1)))
grad_lin("metalM", ((0, "#9aa3ad", 1), (1, "#5b636d", 1)))
TIPOS = {
    "humilde": dict(pared=("#f1cf93", "#d9a35f"), cielo="cieloDia", mesa="maderaM", rim="#fff1c8", suelo="#a8754a"),
    "moderno": dict(pared=("#eef5f4", "#c9dedd"), cielo="cieloDia", mesa="blancoM", rim="#ffffff", suelo="#c9c2b6"),
    "elegante": dict(pared=("#3f8a6c", "#235241"), cielo="cieloTarde", mesa="maderaF", rim="#ffd9a0", suelo="#5a3a24"),
    "industrial": dict(pared=("#c4683f", "#8e4127"), cielo="cieloDia", mesa="metalM", rim="#fff1d6", suelo="#5b5f66"),
    "cocina": dict(pared=("#a9d4ee", "#6fa8cf"), cielo="cieloDia", mesa="maderaM", rim="#ffffff", suelo="#d8cdbb"),
    "rosa": dict(pared=("#f6c9cf", "#e29aa6"), cielo="cieloTarde", mesa="blancoM", rim="#fff0e0", suelo="#c99a86"),
    "noche": dict(pared=("#33466e", "#1d2846"), cielo="cieloNoche", mesa="maderaF", rim="#9fc8ff", suelo="#2a2a36"),
}
for n_, t_ in TIPOS.items():
    grad_lin(f"pared_{n_}", ((0, t_["pared"][0], 1), (1, t_["pared"][1], 1)))
def habitacion(tipo, x0=0, w=1080, h=1920, ytab=1260, seed=1, detalle=True):
    """Fondo de habitación: pared, ventana con cielo detrás de la persona (contraluz), rayos de luz, suelo y objetos."""
    T_ = TIPOS[tipo]; r_ = random.Random(seed)
    cx = x0 + w / 2
    vw, vh = w * 0.5, h * 0.3
    vx, vy = cx - vw / 2, ytab - 620 * h / 1920 - vh * 0.5
    s = [f'<rect x="{x0}" y="0" width="{w}" height="{h}" fill="url(#pared_{tipo})"/>']
    if tipo == "industrial":
        s.append("".join(f'<rect x="{x0 + (i * 70 + (j % 2) * 35) % w:.0f}" y="{j * 34}" width="64" height="28" fill="#000" opacity="0.08"/>' for j in range(int(h / 34)) for i in range(int(w / 70) + 1)))
    if tipo == "cocina":
        s.append("".join(f'<rect x="{x0 + i * 60}" y="{j * 60}" width="58" height="58" fill="#ffffff" opacity="0.12"/>' for j in range(int(h / 60)) for i in range(int(w / 60))))
    if tipo == "elegante":
        s.append("".join(f'<path d="M{x0 + i * 90 + 45},{j * 120} l18,30 l-18,30 l-18,-30 Z" fill="#d8b46a" opacity="0.15"/>' for j in range(int(h / 120)) for i in range(int(w / 90))))
    s.append(f'<rect x="{vx - 18:.0f}" y="{vy - 18:.0f}" width="{vw + 36:.0f}" height="{vh + 36:.0f}" fill="#ffffff" opacity="0.85"/>'
             f'<rect x="{vx:.0f}" y="{vy:.0f}" width="{vw:.0f}" height="{vh:.0f}" fill="url(#{T_["cielo"]})"/>')
    if T_["cielo"] != "cieloNoche":
        s.append(f'<circle cx="{vx + vw * 0.75:.0f}" cy="{vy + vh * 0.3:.0f}" r="{vw * 0.09:.0f}" fill="#fff6d8"/>')
    s.append(skyline(seed + 3, vy + vh, 0.18 * h / 1920, "#7fa6c8" if T_["cielo"] != "cieloNoche" else "#152340", "#9cbcd8" if T_["cielo"] != "cieloNoche" else "#1c2c4c", 0.1 if T_["cielo"] != "cieloNoche" else 0.4, vw, vx).replace("<rect", f'<rect clip-path="url(#cv_{seed})"'))
    DEFS.append(f'<clipPath id="cv_{seed}"><rect x="{vx:.0f}" y="{vy:.0f}" width="{vw:.0f}" height="{vh:.0f}"/></clipPath>')
    s.append(f'<path d="M{vx + vw / 2:.0f},{vy - 18:.0f} L{vx + vw / 2:.0f},{vy + vh + 18:.0f} M{vx - 18:.0f},{vy + vh / 2:.0f} L{vx + vw + 18:.0f},{vy + vh / 2:.0f}" stroke="#ffffff" stroke-width="12" opacity="0.85"/>')
    if T_["cielo"] != "cieloNoche":
        s.append(f'<path class="rayos" d="M{vx:.0f},{vy:.0f} L{vx + vw:.0f},{vy:.0f} L{cx + w * 0.55:.0f},{h:.0f} L{cx - w * 0.55:.0f},{h:.0f} Z" fill="url(#rayoLuz)" opacity="0.5" style="mix-blend-mode:screen"/>')
    s.append(f'<rect x="{x0}" y="{ytab + 140 * h / 1920:.0f}" width="{w}" height="{h:.0f}" fill="{T_["suelo"]}"/>')
    if detalle:
        if tipo in ("humilde", "cocina"):
            s.append(f'<path d="M{x0 + w * 0.15:.0f},0 L{x0 + w * 0.15:.0f},{h * 0.14:.0f}" stroke="#3a2a1a" stroke-width="3"/><circle cx="{x0 + w * 0.15:.0f}" cy="{h * 0.15:.0f}" r="{w * 0.025:.0f}" fill="#fff3c0"/><circle cx="{x0 + w * 0.15:.0f}" cy="{h * 0.15:.0f}" r="{w * 0.1:.0f}" fill="url(#brilloOro)"/>')
            s.append(f'<rect x="{x0 + w * 0.76:.0f}" y="{h * 0.36:.0f}" width="{w * 0.2:.0f}" height="10" fill="#7d4f2a"/>' + "".join(f'<rect x="{x0 + w * (0.77 + i * 0.05):.0f}" y="{h * 0.36 - 40 - (i % 2) * 14:.0f}" width="{w * 0.035:.0f}" height="{40 + (i % 2) * 14}" rx="4" fill="{c}"/>' for i, c in enumerate(("#e2725b", "#f2c14e", "#5fa8d3", "#7cc47f"))))
        if tipo in ("moderno", "rosa"):
            s.append(f'<path d="M{x0 + w * 0.86:.0f},{ytab + 140 * h / 1920:.0f} L{x0 + w * 0.86:.0f},{ytab - 250 * h / 1920:.0f}" stroke="#2a2a2a" stroke-width="5"/><path d="M{x0 + w * 0.8:.0f},{ytab - 250 * h / 1920:.0f} L{x0 + w * 0.92:.0f},{ytab - 250 * h / 1920:.0f} L{x0 + w * 0.89:.0f},{ytab - 300 * h / 1920:.0f} L{x0 + w * 0.83:.0f},{ytab - 300 * h / 1920:.0f} Z" fill="#f2efe6"/>')
            s.append(f'<rect x="{x0 + w * 0.05:.0f}" y="{ytab - 40 * h / 1920:.0f}" width="{w * 0.1:.0f}" height="{180 * h / 1920:.0f}" fill="#e9e3d6"/>' + "".join(f'<ellipse cx="{x0 + w * (0.1 + r_.uniform(-0.06, 0.06)):.0f}" cy="{ytab - (80 + r_.uniform(0, 160)) * h / 1920:.0f}" rx="{w * 0.04:.0f}" ry="{w * 0.015:.0f}" fill="#3f9a5a" transform="rotate({r_.uniform(-60, 60):.0f} {x0 + w * 0.1:.0f} {ytab - 60 * h / 1920:.0f})"/>' for _ in range(9)))
        if tipo == "elegante":
            s.append(f'<path d="M{cx:.0f},0 L{cx:.0f},{h * 0.08:.0f}" stroke="#c9a24a" stroke-width="4"/><circle cx="{cx:.0f}" cy="{h * 0.1:.0f}" r="{w * 0.18:.0f}" fill="url(#brilloOro)"/>' + "".join(f'<path d="M{cx + dx:.0f},{h * 0.08:.0f} l0,{h * 0.035:.0f}" stroke="#fff3c0" stroke-width="5"/>' for dx in (-60, -30, 0, 30, 60)))
            s.append(f'<rect x="{x0 + w * 0.04:.0f}" y="{h * 0.28:.0f}" width="{w * 0.18:.0f}" height="{h * 0.16:.0f}" fill="#c9a24a"/><rect x="{x0 + w * 0.055:.0f}" y="{h * 0.29:.0f}" width="{w * 0.15:.0f}" height="{h * 0.14:.0f}" fill="#7a4a3a"/>')
        if tipo == "industrial":
            s.append("".join(f'<path d="M{x0 + w * x:.0f},0 L{x0 + w * x:.0f},{h * 0.16:.0f}" stroke="#1d1d1d" stroke-width="4"/><path d="M{x0 + w * x - 40:.0f},{h * 0.16:.0f} L{x0 + w * x + 40:.0f},{h * 0.16:.0f} L{x0 + w * x + 26:.0f},{h * 0.14:.0f} L{x0 + w * x - 26:.0f},{h * 0.14:.0f} Z" fill="#2f3a3f"/><ellipse cx="{x0 + w * x:.0f}" cy="{h * 0.22:.0f}" rx="{w * 0.12:.0f}" ry="{h * 0.06:.0f}" fill="url(#brilloOro)"/>' for x in (0.2, 0.8)))
    return "".join(s)
def mesa(x0, x1, ytab, fill="maderaM", grosor=40):
    return (f'<polygon points="{x0 + 40},{ytab - 30} {x1 - 40},{ytab - 30} {x1},{ytab + 30} {x0},{ytab + 30}" fill="url(#{fill})"/>'
            f'<polygon points="{x0 + 40},{ytab - 30} {x1 - 40},{ytab - 30} {x1},{ytab + 30} {x0},{ytab + 30}" fill="#ffffff" opacity="0.12"/>'
            f'<rect x="{x0}" y="{ytab + 30}" width="{x1 - x0}" height="{grosor}" fill="url(#{fill})"/><rect x="{x0}" y="{ytab + 30}" width="{x1 - x0}" height="{grosor}" fill="#000" opacity="0.25"/>')
def movil(mid, x, y, s=1.0, texto="", color="#ffffff"):
    s *= 1.35
    return (f'<g id="{mid}"><rect x="{x - 62 * s:.0f}" y="{y - 100 * s:.0f}" width="{124 * s:.0f}" height="{200 * s:.0f}" rx="{16 * s:.0f}" fill="#111317"/>'
            f'<rect class="pant" x="{x - 55 * s:.0f}" y="{y - 92 * s:.0f}" width="{110 * s:.0f}" height="{184 * s:.0f}" rx="{10 * s:.0f}" fill="#1b2a3a"/>'
            f'<text x="{x:.0f}" y="{y - 30 * s:.0f}" text-anchor="middle" font-family="Inter" font-weight="700" font-size="{10 * s:.0f}" fill="#9fb3cf" letter-spacing="2">MI CUENTA</text>'
            f'<text class="saldo" x="{x:.0f}" y="{y + 8 * s:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="{14 * s:.0f}" fill="{color}">{texto}</text></g>')
def escena_hab(eid, tipo, pid, bid, seed, ytab=1300, h=300, lado=1, extra="", bx=None, mov=None):
    """Plano completo: habitación + persona sentada + mesa + botón (+ móvil opcional)."""
    bx = bx if bx is not None else 540 + 200 * lado
    cuerpo, brazos = sentado(pid, 540, ytab, h, TIPOS[tipo]["rim"], lado_mano=lado, e=estilo(seed * 31 + 7))
    c = [habitacion(tipo, seed=seed, ytab=ytab), decor(tipo, seed, ytab), polvo(f"pv_{eid}", 70, 200, 880, 300, ytab, "#fff6d8", seed, 2.2), cuerpo, mesa(-60, 1140, ytab, TIPOS[tipo]["mesa"], 640),
         mesa_objs(540, ytab, seed, 1 if bx > 540 else -1), pon_boton(bid, bx, ytab + 10, 1.0), extra, brazos]
    if mov:
        c.insert(4, movil(*mov))
    escena(eid, "".join(c))

# ------------------------------------------------------------------ personajes con cara, móvil con app y decoración (personajes.py)
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
    cuello = f'<path d="M{cx - 15 * k:.0f},{ytab - 205 * k:.0f} L{cx + 15 * k:.0f},{ytab - 205 * k:.0f} L{cx + 17 * k:.0f},{ytab - 166 * k:.0f} L{cx - 17 * k:.0f},{ytab - 166 * k:.0f} Z" fill="{oscurece(piel, 0.88)}"/>'
    escote = f'<path d="M{cx - 24 * k:.0f},{ytab - 172 * k:.0f} L{cx:.0f},{ytab - 140 * k:.0f} L{cx + 24 * k:.0f},{ytab - 172 * k:.0f} Z" fill="{oscurece(piel, 0.88)}"/><path d="M{cx - 26 * k:.0f},{ytab - 173 * k:.0f} L{cx:.0f},{ytab - 138 * k:.0f} L{cx + 26 * k:.0f},{ytab - 173 * k:.0f}" stroke="{oscurece(ropa, 0.7)}" stroke-width="{5 * k:.1f}" fill="none"/>'
    cuerpo = (f'<g id="{pid}"><g class="cuerpo"><path d="{torso}" fill="{ropa}"/><path d="{torso}" fill="url(#brilloRopa)"/>{cuello}{escote}'
              f'<path d="{torso}" fill="none" stroke="{rim}" stroke-width="{2 * k:.1f}" opacity="0.45"/>'
              f'<g class="cab">{cara(pid, cx, ytab - 245 * k, 42 * k, e, expr=expr0)}</g></g></g>')
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
            f'<rect x="{x - 7 * k:.0f}" y="{sy - 256 * k:.0f}" width="{14 * k:.0f}" height="{16 * k:.0f}" fill="{oscurece(piel, 0.88)}"/>'
            f'{cara(pid, x, sy - 278 * k, 22 * k, e, espalda=espalda, expr=expr0)}{brazo_g}</g>')

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
    tx = cx - lado * 400
    taza = r_.choice(("#ffffff", "#f2c14e", "#5fa8d3", "#e2725b"))
    return (f'<g><ellipse cx="{tx}" cy="{ytab + 8}" rx="46" ry="12" fill="#000" opacity="0.2"/><path d="M{tx - 38},{ytab - 62} L{tx + 38},{ytab - 62} L{tx + 32},{ytab + 4} Q{tx},{ytab + 14} {tx - 32},{ytab + 4} Z" fill="{taza}"/>'
            f'<path d="M{tx + 36},{ytab - 48} q30,6 22,30 q-6,14 -26,10" stroke="{taza}" stroke-width="9" fill="none"/><ellipse cx="{tx}" cy="{ytab - 62}" rx="38" ry="9" fill="#5a3a22"/>'
            + "".join(f'<path class="vapor" d="M{tx - 14 + i * 14},{ytab - 72} q-12,-24 0,-48 q12,-24 0,-48" stroke="#ffffff" stroke-width="6" fill="none" opacity="0.5" stroke-linecap="round"/>' for i in range(3))
            + '</g>')
def vida_global(dur):
    """Animaciones de ambiente que dan vida a todos los planos (cortinas, plantas, vapor, agujas del reloj)."""
    n = int(dur / 2.4) + 1
    J(f'tl.fromTo(".cortina", {{skewX:0}}, {{skewX:1.6, transformOrigin:"50% 0%", duration:1.2, yoyo:true, repeat:{n * 2}, ease:"sine.inOut", immediateRender:false}}, 0);')
    J(f'tl.fromTo(".hoja", {{rotation:-4}}, {{rotation:4, transformOrigin:"0% 100%", duration:1.4, yoyo:true, repeat:{n * 2}, ease:"sine.inOut", immediateRender:false}}, 0);')
    J(f'tl.fromTo(".vapor", {{y:0, opacity:0.55}}, {{y:-60, opacity:0, duration:1.8, stagger:0.6, repeat:{n * 2}, ease:"sine.out", immediateRender:false}}, 0);')
    J(f'tl.fromTo(".aguja", {{rotation:0}}, {{rotation:{int(dur) * 6}, transformOrigin:"0% 50%", duration:{dur:.2f}, ease:"steps({int(dur)})", immediateRender:false}}, 0);')

# ================================================================== 1) GANCHO: el botón en primer plano en una habitación luminosa; la cámara se abre
e1 = "h1"
escena_hab("e1", "humilde", "p1", "b1", 1, mov=("m1", 330, 1290, 1.0, "", "#7CFFB0"))
mostrar("e1", 0, F(3))
camara("e1", 0, P("pulsas") - 0.3, enfoca(650, 1150, 1.7), enfoca(580, 1150, 1.25), "power2.inOut")
J(f'tl.to("#e1-cam", {{x:{enfoca(420, 1250, 1.9)[0]}, y:{enfoca(420, 1250, 1.9)[1]}, scale:1.9, duration:{F(3) - P("millon") + 0.4:.2f}, ease:"power2.inOut"}}, {P("millon") - 0.4:.2f});')
respira("p1", 0, F(3))
cabeza("p1", 0.6, -6); cabeza("p1", 1.8, 3); parpadeo("p1", 0, F(3), 1); expr("p1", 0.5, "nervioso", "preocupado"); expr("p1", P("millon"), "sonrisa", "sorpresa")
pulsar_con("p1", "b1", P("pulsas"), 0.55, True)
mano_reposo("p1", P("pulsas") + 0.35)
J(f'tl.set("#m1 .saldo", {{innerHTML:"<tspan>+1.000.000 €</tspan>"}}, {P("millon") - 0.1:.2f}); tl.fromTo("#m1 .ok", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:0.3, immediateRender:false}}, {P("millon") - 0.1:.2f});')
J(f'tl.fromTo("#m1", {{rotation:0}}, {{rotation:3, svgOrigin:"330 1290", duration:0.05, yoyo:true, repeat:7, immediateRender:false}}, {P("millon") - 0.1:.2f});')
OVR.append('<div id="gancho"><div class="g1">1.000.000 €</div><div class="g2">POR PULSAR UN BOTÓN</div></div>')
J('tl.fromTo("#gancho", {scale:1.1}, {scale:1, duration:0.6, ease:"power3.out", immediateRender:false}, 0);')
J(f'tl.to("#gancho", {{opacity:0, y:-30, duration:0.35, ease:"power2.in"}}, {P("pulsas") - 0.15:.2f});')
FX.append(("vibra", P("millon") - 0.1)); FX.append(("caja", P("millon") + 0.1))

# ================================================================== 2) EL PRECIO: en otra parte del mundo, alguien se queda sin nada (montaje paralelo)
escena_hab("e3", "noche", "p3", "b3", 3, mov=("m3", 790, 1270, 1.25, "<tspan>12.480 €</tspan>", "#ffffff"), bx=330, lado=-1)
mostrar("e3", F(3), F(4))
camara("e3", F(3), F(4), enfoca(620, 1150, 1.15), enfoca(700, 1220, 1.7), "power1.inOut")
respira("p3", F(3), F(4))
J(f'tl.set("#m3 .saldo", {{innerHTML:"<tspan>0,00 €</tspan>", fill:"#d8261a"}}, {P("ahorros") - 0.2:.2f}); tl.fromTo("#m3 .aviso", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:0.25, immediateRender:false}}, {P("ahorros") - 0.2:.2f});')
mano_a("p3", P("ahorros") + 0.1, 470, 1050, 0.5)
cabeza("p3", P("ahorros"), 8, 0.6); parpadeo("p3", F(3), F(4), 3); expr("p3", P("ahorros") - 0.1, "neutral", "sorpresa", abierta=True); expr("p3", P("ahorros") + 0.7, "triste", "preocupado")
FX.append(("perdida", P("ahorros") - 0.2))

# ================================================================== 3) NO ERES EL ÚNICO: la cámara sale de una habitación y descubre un edificio entero… y una ciudad
COLS, FILAS, CW, CH = 9, 15, 320, 330
r3 = random.Random(9)
tipos = list(TIPOS)
celdas = []
for j_ in range(FILAS):
    for i_ in range(COLS):
        t_ = r3.choice(tipos[:-1]) if r3.random() > 0.15 else "noche"
        x0, y0 = i_ * CW, j_ * CH
        T_ = TIPOS[t_]
        cel = (f'<g class="celda" id="c{j_}_{i_}"><rect x="{x0}" y="{y0}" width="{CW}" height="{CH}" fill="url(#pared_{t_})"/>'
               f'<rect x="{x0 + CW * 0.3:.0f}" y="{y0 + CH * 0.12:.0f}" width="{CW * 0.4:.0f}" height="{CH * 0.3:.0f}" fill="url(#{T_["cielo"]})"/>'
               f'<rect x="{x0}" y="{y0 + CH * 0.72:.0f}" width="{CW}" height="{CH * 0.28:.0f}" fill="{T_["suelo"]}"/>'
               f'<ellipse cx="{x0 + CW / 2:.0f}" cy="{y0 + CH * 0.37:.0f}" rx="{CW * 0.06:.0f}" ry="{CH * 0.07:.0f}" fill="{r3.choice(PIELES)}"/><circle cx="{x0 + CW * 0.48:.0f}" cy="{y0 + CH * 0.37:.0f}" r="2.6" fill="#222"/><circle cx="{x0 + CW * 0.52:.0f}" cy="{y0 + CH * 0.37:.0f}" r="2.6" fill="#222"/><path d="M{x0 + CW * 0.48:.0f},{y0 + CH * 0.405:.0f} q{CW * 0.02:.1f},4 {CW * 0.04:.1f},0" stroke="#7a2e2e" stroke-width="2" fill="none"/><path d="M{x0 + CW * 0.44:.0f},{y0 + CH * 0.36:.0f} Q{x0 + CW / 2:.0f},{y0 + CH * 0.26:.0f} {x0 + CW * 0.56:.0f},{y0 + CH * 0.36:.0f} Z" fill="{r3.choice(PELOS)}"/>'
               f'<path d="M{x0 + CW * 0.36:.0f},{y0 + CH * 0.72:.0f} L{x0 + CW * 0.38:.0f},{y0 + CH * 0.5:.0f} Q{x0 + CW / 2:.0f},{y0 + CH * 0.43:.0f} {x0 + CW * 0.62:.0f},{y0 + CH * 0.5:.0f} L{x0 + CW * 0.64:.0f},{y0 + CH * 0.72:.0f} Z" fill="{r3.choice(ROPAS)}"/>'
               f'<rect x="{x0 + CW * 0.12:.0f}" y="{y0 + CH * 0.66:.0f}" width="{CW * 0.76:.0f}" height="{CH * 0.09:.0f}" fill="url(#{T_["mesa"]})"/>'
               f'<ellipse class="bt" cx="{x0 + CW * 0.6:.0f}" cy="{y0 + CH * 0.645:.0f}" rx="{CW * 0.05:.0f}" ry="{CH * 0.035:.0f}" fill="#e8261a"/>'
               f'<circle class="fl" cx="{x0 + CW * 0.6:.0f}" cy="{y0 + CH * 0.64:.0f}" r="{CW * 0.22:.0f}" fill="url(#brilloRojo)" opacity="0"/>'
               f'<rect class="apaga" x="{x0}" y="{y0}" width="{CW}" height="{CH}" fill="#05070c" opacity="0"/>'
               f'<rect x="{x0}" y="{y0}" width="{CW}" height="{CH}" fill="none" stroke="#2a2f38" stroke-width="14"/></g>')
        celdas.append(cel)
EW, EH = COLS * CW, FILAS * CH
edif = f'<g id="edif">{"".join(celdas)}</g>'
e4 = [f'<rect x="-6000" y="-6000" width="14000" height="14000" fill="url(#cieloTarde)"/>',
      "".join(f'<g transform="translate({dx},{dy}) scale({sc})" opacity="0.92"><use href="#edif"/></g>' for dx, dy, sc in ((-3300, 900, 0.8), (EW + 400, 600, 0.85), (-6200, 2200, 0.6), (EW + 3200, 2000, 0.65))),
      edif]
escena("e4", "".join(e4), EW)
mostrar("e4", F(4), F(6))
cx4, cy4 = 4 * CW + CW / 2, 7 * CH + CH * 0.55
J(f'tl.fromTo("#e4-cam", {{x:{-(cx4 - 540) * 3.2 - (540 - 540):.0f}, y:{-3.2 * (cy4 - 960):.0f}, scale:3.2, transformOrigin:"540px 960px"}}, {{x:{-(EW / 2 - 540) * 0.16:.0f}, y:{-0.16 * (EH / 2 - 960):.0f}, scale:0.16, duration:{F(6) - F(4) - 0.2:.2f}, ease:"power3.inOut", immediateRender:false}}, {F(4):.2f});')
J(f'tl.to("#e4 .fl", {{opacity:0.9, duration:0.1, yoyo:true, repeat:1, stagger:{{each:0.012, from:"random"}}}}, {P("mismo") - 0.3:.2f});')
FX.append(("whoosh", F(4) + 0.2)); FX.append(("coro", P("mismo") - 0.3))

# ================================================================== 4) TANTAS VECES COMO QUIERAS · MILLONARIO EN UN SEGUNDO: pulsaciones rápidas
escena_hab("e6", "moderno", "p6", "b6", 6, mov=("m6", 330, 1290, 1.0, "<tspan>1.000.000 €</tspan>", "#7CFFB0"))
mostrar("e6", F(6), F(8))
camara("e6", F(6), F(8), enfoca(540, 1150, 1.2), enfoca(600, 1260, 1.7), "sine.inOut")
respira("p6", F(6), F(8)); parpadeo("p6", F(6), F(8), 6); expr("p6", F(6), "sonrisa", "neutral"); expr("p6", P("millonario"), "sonrisa", "sorpresa")
for k_, w_ in enumerate(("pulsarlo", "veces", "quieras", "millonario", "segundo")):
    t_ = P(w_)
    pulsar_con("p6", "b6", t_, 0.28)
    J(f'tl.set("#m6 .saldo", {{innerHTML:"<tspan>{k_ + 2}.000.000 €</tspan>"}}, {t_ + 0.05:.2f});')
    J(f'tl.fromTo("#m6", {{scale:1}}, {{scale:1.08, svgOrigin:"330 1290", duration:0.08, yoyo:true, repeat:1, immediateRender:false}}, {t_ + 0.05:.2f});')
mano_reposo("p6", P("segundo") + 0.3)
J('tl.set("#m6 .saldo", {innerHTML:"<tspan>1.000.000 €</tspan>"}, 0);')
nota("PULSACIONES ILIMITADAS", P("veces") - 0.2, F(8) - 0.2, 60, 500, "#ff5a40")

# ================================================================== 5) NUNCA SABRÁS A QUIÉN ARRUINAS: pantalla partida (gana arriba, pierde abajo)
f8 = F(8)
escena_hab("e8a", "elegante", "p8", "b8", 8)
escena_hab("e8b", "cocina", "p8b", "b8b", 18, mov=("m8", 700, 1290, 1.25, "<tspan>3.240 €</tspan>", "#ffffff"), bx=330, lado=-1)
for e_, top in (("e8a", 0), ("e8b", 1)):
    J(f'tl.set("#{e_}", {{clipPath:"inset({0 if top == 0 else 50}% 0% {50 if top == 0 else 0}% 0%)"}}, 0);')
    mostrar(e_, f8, F(9))
camara("e8a", f8, F(9), enfoca(560, 1250, 1.0), enfoca(560, 1250, 1.05))
J(f'tl.fromTo("#e8a-cam", {{y:-430}}, {{y:-460, duration:{F(9) - f8:.2f}, ease:"none", immediateRender:false}}, {f8:.2f});')
J(f'tl.fromTo("#e8b-cam", {{y:420, scale:1.0}}, {{y:390, scale:1.05, duration:{F(9) - f8:.2f}, ease:"none", immediateRender:false}}, {f8:.2f});')
OVR.append('<div id="split8"></div>'); J(f'tl.set("#split8", {{opacity:0}}, 0); tl.set("#split8", {{opacity:1}}, {f8:.2f}); tl.set("#split8", {{opacity:0}}, {F(9):.2f});')
pulsar_con("p8", "b8", P("arruinando") - 0.3, 0.4)
J(f'tl.set("#m8 .saldo", {{innerHTML:"<tspan>0,00 €</tspan>", fill:"#d8261a"}}, {P("arruinando") - 0.2:.2f}); tl.fromTo("#m8 .aviso", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:0.25, immediateRender:false}}, {P("arruinando") - 0.2:.2f});')
cabeza("p8b", P("arruinando"), -8, 0.5); expr("p8", F(8), "sonrisa", "enfado"); expr("p8b", P("arruinando") - 0.1, "neutral", "sorpresa", abierta=True); parpadeo("p8", F(8), F(9), 8); parpadeo("p8b", F(8), F(9), 9)
FX.append(("perdida", P("arruinando") - 0.2))

# ================================================================== 6) MILLONES PULSAN: travelling rápido por muchas habitaciones; casas, coches y viajes
f9 = F(9)
TIRA = ("industrial", "rosa", "humilde", "elegante", "cocina", "moderno", "noche", "industrial", "rosa", "humilde")
tira = []
for k_, t_ in enumerate(TIRA):
    x0 = k_ * 1080
    cuerpo, brazos = sentado(f"t{k_}", x0 + 540, 1300, 300, TIPOS[t_]["rim"], lado_mano=1 if k_ % 2 else -1)
    tira.append(habitacion(t_, x0=x0, seed=30 + k_, ytab=1300) + cuerpo + mesa(x0 - 10, x0 + 1090, 1300, TIPOS[t_]["mesa"], 640)
                + pon_boton(f"bt{k_}", x0 + 540 + (200 if k_ % 2 else -200), 1310, 1.0) + brazos
                + f'<rect x="{x0 + 1070}" y="0" width="20" height="1920" fill="#2a2f38"/>')
escena("e9", "".join(tira), 1080 * len(TIRA))
mostrar("e9", f9, F(10))
J(f'tl.fromTo("#e9-cam", {{x:0, y:-60, scale:1.1}}, {{x:{-1080 * (len(TIRA) - 1) * 1.1:.0f}, y:-60, scale:1.1, duration:{F(10) - f9:.2f}, ease:"power1.inOut", immediateRender:false}}, {f9:.2f});')
for k_ in range(len(TIRA)):
    tk = f9 + (F(10) - f9) * (k_ / (len(TIRA) - 1)) * 0.96 + 0.05
    pulsar_con(f"t{k_}", f"bt{k_}", tk + 0.12, 0.3); expr(f"t{k_}", tk - 0.3, ("sonrisa", "nervioso")[k_ % 2], ("neutral", "preocupado")[k_ % 2])
FX.append(("whoosh", f9))
# casas, coches y viajes: tres viñetas en un mismo barrido
f10 = F(10)
def nubes(x0, y, n=4, seed=1):
    r_ = random.Random(seed)
    return "".join(f'<g class="nube" transform="translate({x0 + r_.uniform(0, 1000):.0f},{y + r_.uniform(0, 260):.0f})">' + "".join(f'<ellipse cx="{dx}" cy="0" rx="{rx}" ry="{rx * 0.6:.0f}" fill="#ffffff" opacity="0.92"/>' for dx, rx in ((-60, 50), (0, 70), (60, 50), (20, 45))) + '</g>' for _ in range(n))
def arbol(x, y, s=1.0, c="#3f9a5a"):
    return f'<rect x="{x - 9 * s:.0f}" y="{y - 120 * s:.0f}" width="{18 * s:.0f}" height="{120 * s:.0f}" fill="#6b4a2a"/><circle cx="{x}" cy="{y - 150 * s:.0f}" r="{70 * s:.0f}" fill="{c}"/><circle cx="{x - 40 * s:.0f}" cy="{y - 120 * s:.0f}" r="{48 * s:.0f}" fill="{c}"/><circle cx="{x + 42 * s:.0f}" cy="{y - 122 * s:.0f}" r="{50 * s:.0f}" fill="{c}"/><circle cx="{x - 20 * s:.0f}" cy="{y - 175 * s:.0f}" r="{30 * s:.0f}" fill="#ffffff" opacity="0.12"/>'
def casa(x0):
    """Barrio soleado: casas, árboles, valla; la familia sonríe con las llaves de su casa nueva."""
    vecinas = "".join(f'<rect x="{x0 + vx}" y="{1060}" width="220" height="200" fill="{c}"/><polygon points="{x0 + vx - 20},{1060} {x0 + vx + 110},{960} {x0 + vx + 240},{1060}" fill="#8a3a2a"/><rect x="{x0 + vx + 30}" y="{1110}" width="50" height="50" fill="#8fc8ea"/><rect x="{x0 + vx + 140}" y="{1110}" width="50" height="50" fill="#8fc8ea"/>' for vx, c in ((-160, "#e9dcc2"), (900, "#d8e6ef")))
    return (f'<rect x="{x0}" y="0" width="1080" height="1920" fill="url(#cieloDia)"/>' + nubes(x0, 220, 4, 3) + vecinas
            + f'<rect x="{x0}" y="1260" width="1080" height="660" fill="#7cc47f"/><rect x="{x0}" y="1500" width="1080" height="80" fill="#cfc8bc"/>'
            + arbol(x0 + 110, 1290, 1.2) + arbol(x0 + 980, 1290, 1.1, "#2f8a3a")
            + f'<rect x="{x0 + 240}" y="860" width="600" height="420" fill="#f4efe4"/><rect x="{x0 + 820}" y="860" width="20" height="420" fill="#000" opacity="0.06"/><polygon points="{x0 + 200},{860} {x0 + 540},{600} {x0 + 880},{860}" fill="#c65b46"/>'
            + f'<rect x="{x0 + 470}" y="1060" width="140" height="220" fill="#7d4f2a"/><circle cx="{x0 + 590}" cy="1170" r="7" fill="#f2c14e"/><rect x="{x0 + 290}" y="940" width="140" height="120" fill="#8fc8ea" stroke="#ffffff" stroke-width="10"/><rect x="{x0 + 650}" y="940" width="140" height="120" fill="#8fc8ea" stroke="#ffffff" stroke-width="10"/>'
            + "".join(f'<rect x="{x0 + i * 60}" y="1440" width="14" height="80" fill="#ffffff"/>' for i in range(19)) + f'<rect x="{x0}" y="1456" width="1080" height="10" fill="#ffffff"/><rect x="{x0}" y="1490" width="1080" height="10" fill="#ffffff"/>'
            + f'<rect x="{x0 + 860}" y="1180" width="10" height="240" fill="#5a3a22"/><rect x="{x0 + 800}" y="1180" width="140" height="74" rx="6" fill="#ffffff"/><text x="{x0 + 870}" y="1228" text-anchor="middle" font-family="Inter" font-weight="900" font-size="28" fill="#e8261a">VENDIDA</text>'
            + persona(x0 + 360, 1640, 420, rim="#fff1c8", pid="cas1", expr0="sonrisa", e=estilo(41, ropa="#3f7ad8")) + persona(x0 + 470, 1650, 380, rim="#fff1c8", pid="cas2", expr0="sonrisa", e=estilo(42, ropa="#f2c14e", peinado="largo"))
            + f'<g id="llaves"><circle cx="{x0 + 420}" cy="1300" r="14" fill="none" stroke="#f2c14e" stroke-width="6"/><rect x="{x0 + 414}" y="1312" width="12" height="40" fill="#f2c14e"/></g>')
def coche(x0):
    """Calle de ciudad al atardecer: edificios, farolas, árboles; el deportivo nuevo brilla."""
    return (f'<rect x="{x0}" y="0" width="1080" height="1920" fill="url(#cieloTarde)"/>' + nubes(x0, 240, 3, 5)
            + skyline(70, 1300, 1.0, "#5a5f8a", "#7a7fa8", 0.25, 1080, x0)
            + f'<rect x="{x0}" y="1300" width="1080" height="90" fill="#b9b2a6"/><rect x="{x0}" y="1390" width="1080" height="530" fill="#3a3f48"/><rect x="{x0}" y="1386" width="1080" height="8" fill="#e9e3d6"/>'
            + "".join(f'<rect x="{x0 + i * 160 + 40}" y="1640" width="90" height="12" fill="#f2f2f2" opacity="0.8"/>' for i in range(7))
            + "".join(f'<rect x="{x0 + fx}" y="980" width="10" height="330" fill="#2a2f38"/><path d="M{x0 + fx + 5},985 q40,-10 60,10" stroke="#2a2f38" stroke-width="8" fill="none"/><circle cx="{x0 + fx + 66}" cy="1000" r="14" fill="#ffe7a0"/><circle cx="{x0 + fx + 66}" cy="1000" r="60" fill="url(#brilloOro)"/>' for fx in (60, 760))
            + arbol(x0 + 380, 1310, 0.9) + arbol(x0 + 960, 1310, 0.8, "#2f8a3a")
            + f'<g transform="translate({x0 + 70},1250) scale(0.9)"><ellipse cx="410" cy="215" rx="440" ry="24" fill="#000" opacity="0.35"/><path d="M0,200 L0,140 Q10,110 60,100 L200,80 L300,20 L540,20 L660,90 L780,110 Q820,120 820,170 L820,200 Z" fill="#e8261a"/>'
            + '<path d="M320,36 L520,36 L620,96 L250,96 Z" fill="#9fd6ff"/><path d="M330,40 L420,40 L360,92 L270,92 Z" fill="#ffffff" opacity="0.35"/><path d="M30,150 L790,160" stroke="#ffffff" stroke-width="6" opacity="0.45"/>'
            + '<circle cx="170" cy="205" r="62" fill="#111"/><circle cx="650" cy="205" r="62" fill="#111"/><circle cx="170" cy="205" r="30" fill="#c9ccd2"/><circle cx="650" cy="205" r="30" fill="#c9ccd2"/><rect x="790" y="130" width="30" height="18" rx="4" fill="#fff3c0"/><rect x="0" y="132" width="20" height="16" rx="4" fill="#ff5a3c"/></g>'
            + persona(x0 + 950, 1660, 400, rim="#ffd59a", pid="coc1", expr0="sonrisa", lado=-1, e=estilo(51, ropa="#2a3550", gafas=True)))
def viaje(x0):
    """Playa de vacaciones: mar, sombrillas, palmera, avión en el cielo; brindan con un cóctel."""
    return (f'<rect x="{x0}" y="0" width="1080" height="1920" fill="url(#cieloDia)"/>' + nubes(x0, 260, 3, 7) + f'<circle cx="{x0 + 820}" cy="460" r="90" fill="#fff6d8"/><circle cx="{x0 + 820}" cy="460" r="200" fill="#fff6d8" opacity="0.25"/>'
            + f'<rect x="{x0}" y="1150" width="1080" height="270" fill="#2f8fc8"/><rect x="{x0}" y="1150" width="1080" height="12" fill="#bfe8ff"/>' + "".join(f'<path d="M{x0 + i * 120},{1220 + (i % 3) * 50} q30,-12 60,0" stroke="#bfe8ff" stroke-width="6" fill="none" opacity="0.7"/>' for i in range(9))
            + f'<rect x="{x0}" y="1420" width="1080" height="500" fill="#efdcb4"/>'
            + "".join(f'<path d="M{x0 + sx},1560 L{x0 + sx},1380" stroke="#ffffff" stroke-width="8"/><path d="M{x0 + sx - 110},1390 Q{x0 + sx},1300 {x0 + sx + 110},1390 Z" fill="{c}"/><path d="M{x0 + sx - 40},1390 Q{x0 + sx},1300 {x0 + sx + 40},1390" fill="#ffffff" opacity="0.5"/>' for sx, c in ((180, "#e2725b"), (900, "#f2c14e")))
            + f'<g transform="translate({x0 + 300},420) rotate(-8)"><path d="M0,0 L260,0 Q300,0 300,20 Q300,40 260,40 L0,40 Z" fill="#ffffff"/><path d="M120,20 L60,-70 L100,-70 L190,20 Z M120,20 L60,110 L100,110 L190,20 Z" fill="#e9eef5"/><path d="M10,20 L-20,-30 L10,-30 L40,20 Z" fill="#e2725b"/>'
            + "".join(f'<circle cx="{60 + i * 30}" cy="16" r="5" fill="#5fa8d3"/>' for i in range(7)) + '</g>'
            + f'<path d="M{x0 + 640},1440 C{x0 + 630},1300 {x0 + 620},1200 {x0 + 640},1080" stroke="#6b4a2a" stroke-width="18" fill="none"/>'
            + "".join(f'<path class="hoja" d="M{x0 + 640},1080 q{a},-24 {b},{c}" stroke="#2f8a3a" stroke-width="20" fill="none" stroke-linecap="round"/>' for a, b, c in ((-80, -150, 40), (80, 150, 40), (-20, -110, -60), (30, 120, -50)))
            + persona(x0 + 330, 1700, 430, rim="#fff6d8", pid="via1", expr0="sonrisa", e=estilo(61, ropa="#f2c14e", peinado="rizado"))
            + f'<g><path d="M{x0 + 400},1340 L{x0 + 430},1340 L{x0 + 418},1380 L{x0 + 412},1380 Z" fill="#ff8a5c"/><rect x="{x0 + 413}" y="1380" width="4" height="30" fill="#ffffff"/><circle cx="{x0 + 428}" cy="1336" r="8" fill="#7cc47f"/></g>')
escena("e10", casa(0) + coche(1080) + viaje(2160), 3240)
mostrar("e10", f10, F(11))
J(f'tl.fromTo("#e10-cam", {{x:0, scale:1.05}}, {{x:0, scale:1.05, duration:0.01, immediateRender:false}}, {f10:.2f});')
J(f'tl.to("#e10-cam", {{x:-1134, duration:0.35, ease:"power3.inOut"}}, {P("coches") - 0.3:.2f}); tl.to("#e10-cam", {{x:-2268, duration:0.35, ease:"power3.inOut"}}, {P("viajes") - 0.3:.2f});')
FX.append(("whoosh", P("coches") - 0.3)); FX.append(("whoosh", P("viajes") - 0.3))

# ================================================================== 7) LAS VÍCTIMAS: cajero en la calle (saldo 0) · sin explicación · sin aviso
f11 = F(11)
cajero = ('<rect width="1080" height="1920" fill="url(#cieloDia)"/>' + skyline(61, 1500, 1.0, "#c9d6e2", "#dfe8f0", 0.0) +
          '<rect x="0" y="1500" width="1080" height="420" fill="#cfc8bc"/><rect x="180" y="560" width="720" height="940" fill="#e9e3d6"/><rect x="180" y="560" width="720" height="110" fill="#1f5fa8"/>'
          '<text x="540" y="635" text-anchor="middle" font-family="Inter" font-weight="900" font-size="54" fill="#ffffff" letter-spacing="8">BANCO</text>'
          '<rect x="360" y="760" width="360" height="560" rx="16" fill="#3a3f48"/><rect id="pant11" x="400" y="800" width="280" height="200" rx="8" fill="#1b2a3a"/>'
          '<text id="sal11" x="540" y="880" text-anchor="middle" font-family="Inter" font-weight="800" font-size="30" fill="#9fdcff">SALDO</text>'
          '<text id="num11" x="540" y="945" text-anchor="middle" font-family="Inter" font-weight="900" font-size="48" fill="#ffffff"><tspan>41.230 €</tspan></text>'
          '<rect x="430" y="1040" width="220" height="16" rx="8" fill="#111"/><rect x="420" y="1100" width="240" height="160" rx="10" fill="#4a505a"/>')
escena("e11", cajero + persona(560, 1780, 720, rim="#ffffff", pid="v11", espalda=True, e=estilo(111, ropa="#d94f6b", peinado="largo", pelo="#5a3a22")))
mostrar("e11", f11, F(13))
camara("e11", f11, F(13), enfoca(540, 1000, 1.0), enfoca(540, 920, 1.25), "sine.inOut")
J(f'tl.set("#num11", {{innerHTML:"<tspan>0,00 €</tspan>", fill:"#d8261a"}}, {P("vacias") - 0.2:.2f}); tl.to("#pant11", {{fill:"#3a0f12", duration:0.2}}, {P("vacias") - 0.2:.2f});')
J(f'tl.fromTo("#v11 .brazo", {{rotation:0}}, {{rotation:-150, svgOrigin:"642 1233", duration:0.5, ease:"power2.out", immediateRender:false}}, {P("explicacion") - 0.2:.2f});')
J(f'tl.fromTo("#e11-cam", {{rotation:0}}, {{rotation:0.8, duration:0.05, yoyo:true, repeat:3, immediateRender:false}}, {P("aviso") - 0.05:.2f});')
FX.append(("perdida", P("vacias") - 0.2)); FX.append(("golpe", P("explicacion") - 0.05)); FX.append(("golpe", P("aviso") - 0.05))

# ================================================================== 8) BANCOS · FAMILIAS · COMERCIOS (tres planos encadenados con un mismo barrido)
f13 = F(13)
banco = ('<rect x="0" y="0" width="1080" height="1920" fill="url(#cieloDia)"/><rect x="0" y="1480" width="1080" height="440" fill="#d8d0c2"/>'
         '<polygon points="120,620 540,420 960,620" fill="#efe9dd"/><rect x="140" y="620" width="800" height="60" fill="#e2dccf"/>'
         + "".join(f'<rect x="{180 + i * 150}" y="690" width="70" height="700" fill="#f4efe4"/><rect x="{170 + i * 150}" y="680" width="90" height="20" fill="#e2dccf"/>' for i in range(6))
         + '<rect x="120" y="1390" width="840" height="90" fill="#e2dccf"/><text x="540" y="560" text-anchor="middle" font-family="Georgia" font-weight="700" font-size="56" fill="#7a6a50" letter-spacing="10">BANCO</text>'
         + "".join(persona(80 + i * 95, 1720 + (i % 2) * 20, 330 + (i % 3) * 20, rim="#ffffff", lado=1, pid=f"cola{i}", expr0=("triste", "nervioso", "serio")[i % 3]) for i in range(11))
         + '<g id="papeles13">' + "".join(f'<rect class="pap13" x="{random.Random(i).uniform(100, 980):.0f}" y="{random.Random(i + 9).uniform(900, 1300):.0f}" width="44" height="58" fill="#ffffff" stroke="#c9c2b6"/>' for i in range(16)) + '</g>')
cocina14 = (habitacion("cocina", seed=14, ytab=1300) + persona(380, 1300, 520, rim="#ffffff", pid="fa1", expr0="triste") + persona(700, 1300, 500, rim="#ffffff", lado=-1, pid="fa2", expr0="triste")
            + mesa(-60, 1140, 1300, "maderaM", 640)
            + '<g id="hucha"><ellipse cx="540" cy="1250" rx="110" ry="80" fill="#f2a0b4"/><ellipse cx="640" cy="1240" rx="30" ry="24" fill="#f2a0b4"/><rect x="480" y="1316" width="22" height="20" fill="#e28aa0"/><rect x="580" y="1316" width="22" height="20" fill="#e28aa0"/><rect x="520" y="1172" width="44" height="8" rx="4" fill="#7a3a4a"/></g>'
            + '<g id="trozos" opacity="0">' + "".join(f'<path d="M{540 + dx},{1250 + dy} l{20 + abs(dx) % 15},-12 l8,24 Z" fill="#f2a0b4"/>' for dx, dy in ((-80, -10), (-40, 20), (0, -30), (40, 10), (80, -20), (-60, 30), (60, 30))) + '</g>')
tienda = (habitacion("rosa", seed=15, ytab=1300, detalle=False) + '<rect x="0" y="700" width="1080" height="420" fill="#ffffff" opacity="0.4"/>'
          + "".join(f'<rect x="{60 + i * 120}" y="{720 + j * 130}" width="90" height="100" rx="8" fill="{c}"/>' for j in range(3) for i, c in enumerate(("#f2c14e", "#e2725b", "#5fa8d3", "#7cc47f", "#c78bff", "#f2c14e", "#e2725b", "#5fa8d3")))
          + persona(300, 1300, 520, rim="#ffffff", pid="tend", expr0="neutral") + mesa(-60, 1140, 1300, "blancoM", 640)
          + '<rect x="600" y="1150" width="170" height="250" rx="16" fill="#2a2e35"/><rect id="tpv" x="620" y="1170" width="130" height="90" rx="6" fill="#1b2a3a"/>'
          + '<text id="tpvt" x="685" y="1225" text-anchor="middle" font-family="Inter" font-weight="900" font-size="22" fill="#7CFFB0"><tspan>PAGAR</tspan></text>')
escena("e13", banco + f'<g transform="translate(1080,0)">{cocina14}</g>' + f'<g transform="translate(2160,0)">{tienda}</g>', 3240)
mostrar("e13", f13, F(16))
J(f'tl.fromTo("#e13-cam", {{x:0, scale:1.0}}, {{x:0, scale:1.04, duration:{F(14) - f13:.2f}, ease:"none", immediateRender:false}}, {f13:.2f});')
J(f'tl.to("#e13-cam", {{x:-1080, scale:1.0, duration:0.4, ease:"power3.inOut"}}, {F(14) - 0.25:.2f}); tl.to("#e13-cam", {{x:-2160, duration:0.4, ease:"power3.inOut"}}, {F(15) - 0.25:.2f});')
J(f'tl.fromTo(".pap13", {{y:0, rotation:0}}, {{y:-500, rotation:(i) => (i % 2 ? 1 : -1) * 200, duration:2.4, stagger:0.08, ease:"power1.out", immediateRender:false}}, {f13 + 0.2:.2f});')
J(f'tl.to("#hucha", {{opacity:0, duration:0.1}}, {P("vida") - 0.1:.2f}); tl.to("#trozos", {{opacity:1, duration:0.05}}, {P("vida") - 0.1:.2f}); tl.fromTo("#trozos path", {{x:0, y:0}}, {{x:(i) => (i - 3) * 30, y:(i) => 40 + (i % 3) * 20, rotation:(i) => i * 50, duration:0.6, ease:"power2.out", immediateRender:false}}, {P("vida") - 0.1:.2f});')
J(f'tl.set("#tpvt", {{innerHTML:"<tspan>DENEGADA</tspan>", fill:"#ff5a52"}}, {P("cobrar") - 0.2:.2f}); tl.to("#tpv", {{fill:"#3a0f12", duration:0.15}}, {P("cobrar") - 0.2:.2f});')
FX.append(("murmullo", f13)); expr("tend", P("cobrar") - 0.2, "neutral", "sorpresa", abierta=True); parpadeo("fa1", F(14), F(15), 4); parpadeo("fa2", F(14), F(15), 5); FX.append(("rompe", P("vida") - 0.1)); FX.append(("denegada", P("cobrar") - 0.2))

# ================================================================== 9) CADA PULSACIÓN = ALGUIEN LO PIERDE TODO: el edificio, en paralelo (destello rojo ↔ habitación que se apaga)
f16 = F(16)
edif2 = edif.replace('id="edif"', 'id="edif2"').replace('id="c', 'id="d')
escena("e16", f'<rect x="-3000" y="-3000" width="9000" height="9000" fill="url(#cieloTarde)"/>{edif2}', EW)
mostrar("e16", f16, F(18))
J(f'tl.fromTo("#e16-cam", {{x:{-(EW / 2 - 540) * 0.5:.0f}, y:{-0.5 * (EH / 2 - 960):.0f}, scale:0.5}}, {{x:{-(EW / 2 - 540) * 0.62:.0f}, y:{-0.62 * (EH / 2 - 960):.0f}, scale:0.62, duration:{F(18) - f16:.2f}, ease:"sine.inOut", immediateRender:false}}, {f16:.2f});')
r9 = random.Random(4)
tt, gap = f16 + 0.25, 0.75
while tt < P("siguiente") - 0.3:
    a = (r9.randint(4, 10), r9.randint(2, 6)); b = (r9.randint(4, 10), r9.randint(2, 6))
    if a == b: continue
    J(f'tl.fromTo("#d{a[0]}_{a[1]} .fl", {{opacity:0}}, {{opacity:1, duration:0.08, yoyo:true, repeat:1, immediateRender:false}}, {tt:.2f});')
    J(f'tl.to("#d{b[0]}_{b[1]} .apaga", {{opacity:0.82, duration:0.25}}, {tt + 0.12:.2f});')
    FX.append(("clic", tt)); FX.append(("apagon", tt + 0.12))
    tt += gap; gap = max(0.28, gap * 0.82)
FX.append(("latido", P("siguiente") - 0.4))

# ================================================================== 10) LOS GOBIERNOS: parlamento · botón en una urna con sello de PROHIBIDO · ventanas anónimas
f18 = F(18)
parl = ('<rect width="1080" height="1920" fill="url(#cieloDia)"/><rect x="0" y="1460" width="1080" height="460" fill="#d8d0c2"/>'
        '<path d="M300,700 Q540,420 780,700 Z" fill="#e9e3d6"/><rect x="140" y="700" width="800" height="60" fill="#e2dccf"/>'
        + "".join(f'<rect x="{180 + i * 115}" y="770" width="54" height="600" fill="#f4efe4"/>' for i in range(7))
        + '<rect x="120" y="1370" width="840" height="90" fill="#e2dccf"/>'
        + "".join(f'<path d="M{x},700 L{x},540" stroke="#8a8a8a" stroke-width="5"/><rect x="{x}" y="540" width="90" height="56" fill="{c}"/>' for x, c in ((200, "#c60b1e"), (860, "#1f4fa8")))
        + '<rect x="400" y="1300" width="280" height="300" fill="#7d4f2a"/><rect x="380" y="1290" width="320" height="24" fill="#5a3a22"/>'
        + '<path d="M500,1290 l-20,-60 M580,1290 l20,-60" stroke="#222" stroke-width="5"/><circle cx="480" cy="1226" r="10" fill="#222"/><circle cx="600" cy="1226" r="10" fill="#222"/>'
        + persona(540, 1320, 420, rim="#ffffff", pid="pres", expr0="serio", e=estilo(81, ropa="#2a3550", peinado="calvo", pelo="#8e8e8e")))
escena("e18", parl)
mostrar("e18", f18, F(19))
camara("e18", f18, F(19), enfoca(540, 1000, 1.0), enfoca(540, 1150, 1.25), "sine.inOut")
FX.append(("murmullo", f18))
f19 = F(19)
urna = (habitacion("moderno", seed=19, ytab=1300, detalle=False) + mesa(-60, 1140, 1300, "blancoM", 640) + pon_boton("b19", 540, 1310, 1.4)
        + '<rect x="330" y="980" width="420" height="340" fill="#cfeaff" opacity="0.18" stroke="#ffffff" stroke-width="6"/><path d="M340,990 L420,1300" stroke="#ffffff" stroke-width="10" opacity="0.35"/>'
        + '<g id="sello19" opacity="0"><rect x="300" y="1075" width="480" height="124" rx="12" fill="none" stroke="#d8261a" stroke-width="12"/><text x="540" y="1164" text-anchor="middle" font-family="Inter" font-weight="900" font-size="70" fill="#d8261a" letter-spacing="5">PROHIBIDO</text></g>')
escena("e19", urna)
mostrar("e19", f19, F(20))
camara("e19", f19, F(20), enfoca(540, 1150, 1.3), enfoca(540, 1150, 1.45), "sine.inOut")
J(f'tl.fromTo("#sello19", {{opacity:0, scale:1.8, rotation:-14}}, {{opacity:0.92, scale:1, rotation:-8, svgOrigin:"540 1135", duration:0.25, ease:"power4.in", immediateRender:false}}, {P("prohibir") - 0.05:.2f});')
FX.append(("sello", P("prohibir") + 0.2))
f20 = F(20)
r20 = random.Random(20)
ventanas = "".join(f'<g class="vn"><rect x="{40 + i * 205}" y="{140 + j * 230}" width="170" height="190" fill="#ffcf7a" opacity="{r20.uniform(0.55, 0.95):.2f}"/>'
                   f'<path d="M{88 + i * 205},{330 + j * 230} Q{125 + i * 205},{270 + j * 230} {162 + i * 205},{330 + j * 230} Z" fill="{r20.choice(ROPAS)}"/><ellipse cx="{125 + i * 205}" cy="{240 + j * 230}" rx="22" ry="27" fill="{r20.choice(PIELES)}"/><circle cx="{117 + i * 205}" cy="{242 + j * 230}" r="3" fill="#222"/><circle cx="{133 + i * 205}" cy="{242 + j * 230}" r="3" fill="#222"/><path d="M{117 + i * 205},{254 + j * 230} q8,{(i + j) % 3 - 1} 16,0" stroke="#7a2e2e" stroke-width="2.4" fill="none"/><path d="M{102 + i * 205},{236 + j * 230} Q{125 + i * 205},{200 + j * 230} {148 + i * 205},{236 + j * 230} Z" fill="{r20.choice(PELOS)}"/>'
                   f'<circle class="rj" cx="{125 + i * 205}" cy="{315 + j * 230}" r="70" fill="url(#brilloRojo)" opacity="0"/></g>' for i in range(5) for j in range(8))
escena("e20", f'<rect width="1080" height="1920" fill="#20283a"/>{ventanas}')
mostrar("e20", f20, F(21))
camara("e20", f20, F(21), enfoca(540, 1000, 1.25), enfoca(540, 1000, 1.0), "sine.inOut")
J(f'tl.to("#e20 .rj", {{opacity:1, duration:0.12, yoyo:true, repeat:1, stagger:{{each:0.09, from:"random"}}}}, {P("demostrar") - 0.3:.2f});')
nota("NADIE PUEDE DEMOSTRARLO", P("demostrar") - 0.2, F(21) - 0.1, 60, 500, "#9fdcff")

# ================================================================== 11) «SI NO LO HAGO YO, LO HARÁ OTRO»: cortes rápidos de manos sobre botones
f21 = F(21)
cortes = ("industrial", "elegante", "rosa", "humilde")
dur = (F(22) - f21) / len(cortes)
for k_, t_ in enumerate(cortes):
    e_ = f"e21{k_}"
    escena_hab(e_, t_, f"q{k_}", f"bq{k_}", 50 + k_, lado=1 if k_ % 2 == 0 else -1)
    a, b = f21 + k_ * dur, f21 + (k_ + 1) * dur
    mostrar(e_, a, b)
    bx_, by_ = BOT[f"bq{k_}"][0], BOT[f"bq{k_}"][1]
    camara(e_, a, b, enfoca(bx_, by_ + 40, 1.9), enfoca(bx_, by_ + 40, 2.2), "sine.in")
    pulsar_con(f"q{k_}", f"bq{k_}", b - 0.25, 0.7, True); expr(f"q{k_}", a, "nervioso", "preocupado"); expr(f"q{k_}", b - 0.25, "serio", "enfado")

# ================================================================== 12) PASA ALGO QUE NADIE HABÍA PREVISTO: silencio, una pulsación a cámara lenta
f22 = F(22)
escena_hab("e22", "noche", "p22", "b22", 22)
mostrar("e22", f22, F(24))
camara("e22", f22, F(24), enfoca(700, 1150, 1.4), enfoca(700, 1180, 2.4), "power1.in")
mano_a("p22", P("alguien", 2) - 0.2, BOT["b22"][0], BOT["b22"][1] - 40, 1.4)
pulsar_con("p22", "b22", P("boton", 3) - 0.1, 0.3, True); expr("p22", F(22), "serio", "preocupado"); parpadeo("p22", F(22), F(24), 22)
J(f'tl.fromTo("#flash22", {{opacity:0}}, {{opacity:1, duration:0.12, yoyo:true, repeat:1, immediateRender:false}}, {P("boton", 3) - 0.05:.2f});')
OVR.append('<div id="flash22"></div>')

def mano_pov(mid, x, y, lado, piel="#e0ac85", manga="#2a3550"):
    """Tu mano vista desde arriba (primera persona): manga, muñeca y mano de piel con dedos hacia el botón."""
    L = lado; sk = oscurece(piel, 0.82)
    dedos = "".join(f'<path d="M{x + dx * L - 15:.0f},{y - 40} L{x + dx * L - 13:.0f},{y - 40 - h_} Q{x + dx * L:.0f},{y - 54 - h_} {x + dx * L + 13:.0f},{y - 40 - h_} L{x + dx * L + 15:.0f},{y - 40} Z" fill="{piel}"/>'
                    f'<path d="M{x + dx * L - 8:.0f},{y - 30 - h_ * 0.55:.0f} q8,4 16,0" stroke="{sk}" stroke-width="3" fill="none"/>' for dx, h_ in ((-36, 70), (-12, 88), (12, 84), (34, 66)))
    return (f'<g id="{mid}"><path d="M{x - 80},2000 C{x - 76},1900 {x - 64},{y + 150} {x - 58},{y + 70} L{x + 60},{y + 70} C{x + 66},{y + 150} {x + 76},1900 {x + 80},2000 Z" fill="{manga}"/>'
            f'<path d="M{x - 66},{y + 74} L{x + 66},{y + 74}" stroke="{oscurece(manga, 0.7)}" stroke-width="12"/>'
            f'<path d="M{x - 58},{y + 70} C{x - 64},{y + 10} {x - 54},{y - 40} {x - 50},{y - 44} L{x + 50},{y - 44} C{x + 56},{y - 40} {x + 64},{y + 10} {x + 58},{y + 70} Z" fill="{piel}"/>{dedos}'
            f'<path d="M{x - 52 * L},{y + 20} C{x - 86 * L},{y} {x - 100 * L},{y - 30} {x - 92 * L},{y - 50} C{x - 82 * L},{y - 62} {x - 64 * L},{y - 40} {x - 46 * L},{y - 14} Z" fill="{piel}"/>'
            f'<path d="M{x - 30},{y - 20} Q{x},{y - 30} {x + 30},{y - 20}" stroke="{sk}" stroke-width="4" fill="none" opacity="0.6"/></g>')

# ================================================================== 13) ERES TÚ: tu habitación (vista subjetiva); el móvil se queda a cero; la luz se apaga
f24 = F(24)
grad_lin("mesaPOV", ((0, "#c08a55", 1), (1, "#6b4426", 1)))
pov = (habitacion("rosa", seed=24, ytab=820, detalle=True)
       + '<polygon points="-200,1000 1280,1000 2100,2700 -1020,2700" fill="url(#mesaPOV)"/><polygon points="-200,1000 1280,1000 2100,2700 -1020,2700" fill="#ffffff" opacity="0.08"/>'
       + pon_boton("btu", 540, 1360, 1.9) + movil("mtu", 900, 1420, 1.45, "<tspan>18.350 €</tspan>", "#ffffff")
       + mano_pov("manoI", 250, 1700, -1) + mano_pov("manoD", 650, 1700, 1)
       + '<rect id="oscuro24" width="1080" height="1920" fill="#0a0408" opacity="0"/><rect id="rojo24" width="1080" height="1920" fill="url(#brilloRojo)" opacity="0"/>')
escena("e24", pov)
mostrar("e24", f24, DUR)
camara("e24", f24, F(26), enfoca(540, 1180, 1.0), enfoca(650, 1350, 1.35), "sine.inOut")
J(f'tl.set("#mtu .saldo", {{innerHTML:"<tspan>0,00 €</tspan>", fill:"#d8261a"}}, {P("tu", 2) - 0.1:.2f}); tl.fromTo("#mtu .aviso", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:0.25, immediateRender:false}}, {P("tu", 2) - 0.1:.2f});')
J(f'tl.fromTo("#mtu", {{rotation:0}}, {{rotation:2.5, svgOrigin:"900 1420", duration:0.05, yoyo:true, repeat:9, immediateRender:false}}, {P("tu", 2) - 0.1:.2f});')
J(f'tl.to("#oscuro24", {{opacity:0.55, duration:1.6}}, {P("cero") - 0.2:.2f}); tl.to("#e24 .rayos", {{opacity:0, duration:1.2}}, {P("cero") - 0.2:.2f});')
FX.append(("vibra", P("tu", 2) - 0.1)); FX.append(("perdida", P("cero") - 0.2))
# el botón delante: la cámara se acerca; tu mano avanza… y se queda a un centímetro
J(f'tl.to("#e24-cam", {{x:{enfoca(540, 1250, 1.7)[0]}, y:{enfoca(540, 1250, 1.7)[1]}, scale:1.7, duration:{DUR - F(26) - 1.5:.2f}, ease:"sine.inOut"}}, {F(26):.2f});')
J(f'tl.to("#rojo24", {{opacity:0.55, duration:2.0, yoyo:true, repeat:1}}, {F(26):.2f}); tl.to("#btu .glow", {{opacity:0.9, duration:0.6, yoyo:true, repeat:5, ease:"sine.inOut"}}, {F(26):.2f});')
J(f'tl.to("#manoD", {{x:-80, y:-300, scale:0.8, svgOrigin:"650 1920", duration:{P("precio") - P("recuperar"):.2f}, ease:"power1.inOut"}}, {P("recuperar"):.2f});')
FX.append(("latido", F(26))); FX.append(("latido", P("precio") - 0.6))
tc = P("precio") + 0.75
J(f'tl.set("#negroF", {{opacity:1}}, {tc:.2f}); tl.set("#negroF", {{opacity:0}}, 0);')
OVR.append('<div id="negroF"></div>')
FX.append(("final", tc))

vida_global(DUR)
J(f'tl.fromTo(".nube", {{x:0}}, {{x:60, duration:{DUR:.2f}, ease:"none", immediateRender:false}}, 0);')

# ------------------------------------------------------------------ subtítulos habituales (arriba, palabra a palabra, recuadro azul en lo importante)
CLAVE = set(norm(w) for w in ["boton", "millon", "euros", "ahorros", "unico", "mismo", "veces", "millonario", "arruinando", "millones", "casas", "coches", "viajes",
                               "vacias", "explicacion", "aviso", "reclamaciones", "vida", "cobrar", "todo", "siguiente", "prohibir", "demostrar", "otro",
                               "previsto", "tu", "cero", "delante", "recuperar", "precio"])
SUBS, chunks, cur = [], [], []
for p in T["palabras"]:
    cur.append(p)
    txt = " ".join(x["w"] for x in cur)
    if len(cur) >= 6 or len(txt) >= 30 or re.search(r"[.:;?!…»]$", p["w"]) or (re.search(r",$", p["w"]) and len(cur) >= 3):
        chunks.append(cur); cur = []
if cur:
    chunks.append(cur)
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
@font-face{{font-family:'Grabado';src:url(assets/fonts/grabado.ttf) format('truetype');font-weight:700}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:{BG}}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;background:{BG}}}
.esc{{position:absolute;inset:0;overflow:hidden}}
.cam{{position:absolute;inset:0;transform-origin:540px 960px}}
#gancho{{position:absolute;left:0;right:0;top:1330px;text-align:center;z-index:20}}
#gancho .g1{{font:900 150px Inter;letter-spacing:-5px;color:#ffe08a;text-shadow:0 0 50px rgba(255,200,90,0.6), 0 8px 30px rgba(0,0,0,0.45)}}
#gancho .g2{{font:800 44px Inter;letter-spacing:8px;color:#ffffff;text-shadow:0 4px 20px rgba(0,0,0,0.6)}}
#split8{{position:absolute;left:0;right:0;top:956px;height:8px;background:#ffffff;z-index:30;box-shadow:0 0 20px rgba(0,0,0,0.5)}}
#flash22{{position:absolute;inset:0;background:#ffffff;z-index:58;opacity:0;pointer-events:none}}
#reloj{{position:absolute;left:0;right:0;top:600px;text-align:center;z-index:20;color:#fff;text-shadow:0 6px 30px rgba(0,0,0,0.6)}}
#reloj .rk{{font:800 46px Inter;letter-spacing:12px;color:rgba(255,255,255,0.75)}}
#reloj .rn{{font:300 170px Inter;letter-spacing:-4px;font-variant-numeric:tabular-nums;line-height:1}}
.nota{{position:absolute;z-index:32;display:flex;align-items:center;gap:12px;padding:9px 18px 10px 14px;border-radius:40px;color:#fff;background:linear-gradient(135deg, rgba(14,20,34,0.55), rgba(14,20,34,0.3));backdrop-filter:blur(14px) saturate(1.4);-webkit-backdrop-filter:blur(14px) saturate(1.4);border:1px solid rgba(255,255,255,0.22);box-shadow:0 8px 30px rgba(0,0,0,0.25);text-shadow:0 2px 8px rgba(0,0,0,0.4);white-space:nowrap}}
.nota b{{width:12px;height:12px;border-radius:50%;background:var(--c);box-shadow:0 0 12px var(--c);flex:none}} .nota .ct{{font:800 28px Inter;letter-spacing:2px}} .nota .cs{{font:600 20px Inter;color:rgba(255,255,255,0.7);letter-spacing:1px}}
.nota .cn{{font:900 44px Inter;letter-spacing:-2px;font-variant-numeric:tabular-nums;line-height:1.05;color:var(--c)}}
.barra{{height:16px;border-radius:8px;background:rgba(255,255,255,0.15);margin-top:10px;overflow:hidden}} .barra i{{display:block;height:100%;background:linear-gradient(90deg,#ff8a6a,{RED});transform-origin:0 50%}}
#luz{{position:absolute;inset:-100px;z-index:58;opacity:0;pointer-events:none}}
#negro{{position:absolute;inset:0;z-index:58;opacity:0;background:#000;pointer-events:none}}
#negroF{{position:absolute;inset:0;z-index:59;background:#000;pointer-events:none}}
#grano{{position:absolute;inset:0;z-index:57;pointer-events:none;opacity:0.08;background:url(assets/grano.png);mix-blend-mode:overlay}}
#vineta{{position:absolute;inset:0;z-index:56;pointer-events:none;background:radial-gradient(110% 80% at 50% 50%, rgba(0,0,0,0) 50%, rgba(0,0,0,0.6))}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:560px;z-index:55;pointer-events:none;background:linear-gradient(rgba(2,3,6,0.78), rgba(2,3,6,0))}}
#marca{{position:absolute;left:0;right:0;top:1775px;text-align:center;font:700 28px Inter;color:#ffffff;opacity:0.32;pointer-events:none;z-index:61}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 62px Inter;color:rgba(255,255,255,0.4);line-height:1.22;text-shadow:0 3px 12px rgba(0,0,0,0.6)}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:3px solid #4ea3ff;border-radius:6px;background:rgba(78,163,255,0.18);opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <svg width="0" height="0" style="position:absolute"><defs>{"".join(DEFS)}</defs></svg>
  {"".join(ESC)}
  <div id="topsombra"></div>
  {"".join(OVR)}
  <div id="vineta"></div><div id="grano"></div><div id="luz"></div><div id="negro"></div>
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
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones")

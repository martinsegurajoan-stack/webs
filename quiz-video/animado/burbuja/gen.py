#!/usr/bin/env python3
"""«¿Qué pasaría si te sueltan en una burbuja de fútbol desde un helicóptero?» (piezas del botón y del váter)
«¿Y si todo el mundo tuviera un botón para ganar un millón?» — animado (HyperFrames + GSAP), misma identidad que «puertas»
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


# ======================================================================================================
#  ¿QUÉ PASARÍA SI TE SUELTAN EN UNA BURBUJA DE FÚTBOL DESDE UN HELICÓPTERO?  — un solo mundo vertical
#  (del campo de fútbol a 1.000 m) y una cámara que sigue a la burbuja. Casi sin transiciones.
# ======================================================================================================
def nubes(x0, y, n=4, seed=1, w=1000, h=260, s=1.0, op=0.92):
    r_ = random.Random(seed)
    return "".join(f'<g class="nube" transform="translate({x0 + r_.uniform(0, w):.0f},{y + r_.uniform(0, h):.0f}) scale({s * r_.uniform(0.7, 1.3):.2f})">' + "".join(f'<ellipse cx="{dx}" cy="{dy}" rx="{rx}" ry="{rx * 0.62:.0f}" fill="#ffffff" opacity="{op}"/>' for dx, dy, rx in ((-70, 6, 52), (0, -10, 74), (66, 4, 54), (22, 14, 60), (-30, 18, 50))) + '<ellipse cx="0" cy="30" rx="120" ry="16" fill="#cfe3f5" opacity="0.6"/></g>' for _ in range(n))
def destello(cx, cy, r, col="#ffffff", cls="chispa"):
    return f'<path class="{cls}" d="M{cx},{cy - r} Q{cx + r * 0.18},{cy - r * 0.18} {cx + r},{cy} Q{cx + r * 0.18},{cy + r * 0.18} {cx},{cy + r} Q{cx - r * 0.18},{cy + r * 0.18} {cx - r},{cy} Q{cx - r * 0.18},{cy - r * 0.18} {cx},{cy - r} Z" fill="{col}"/>'
grad_lin("cieloV", ((0, "#0f3c8f", 1), (0.35, "#2f7de0", 1), (0.8, "#7cc2ff", 1), (1, "#cdeaff", 1)))
grad_rad("burbG", ((0, "#ffffff", 0.06), (0.75, "#bfefff", 0.16), (0.95, "#8fdcff", 0.42), (1, "#ffffff", 0.7)))
grad_lin("cesped", ((0, "#4fb35a", 1), (1, "#2f7d3a", 1)))
grad_lin("gradas", ((0, "#3a4258", 1), (1, "#262c3d", 1)))
grad_lin("rojoH", ((0, "#ff5a4a", 1), (1, "#c41f2a", 1)))
YO = estilo(5, piel="#e0ac85", pelo="#2a1a12", ropa="#f2c14e", peinado="corto", barba=False, gafas=False, ojos="#4a3020")
PANT = "#2a3550"
R = 200                       # radio de la burbuja
YG = 15000                    # suelo (césped)
PXM = 12                      # píxeles por metro de altura
YC0 = YG - 380                # centro de la burbuja con los pies en el suelo
L = 520                       # cuerda: del gancho del helicóptero a lo alto de la burbuja
HOOK0 = YC0 - R - L           # gancho cuando la burbuja está en el suelo
def y_alt(a): return YC0 - a * PXM

def burbuja(pid, cuerda=0):
    """Burbuja de fútbol (bubble football): tú dentro (cabeza y pecho, con correas), piernas fuera por abajo."""
    e = YO
    s = []
    if cuerda:
        s.append(f'<path class="cuerdaB" d="M0,{-R} C30,{-R - cuerda * 0.3} -30,{-R - cuerda * 0.6} 10,{-R - cuerda}" stroke="#c9a46a" stroke-width="9" fill="none" stroke-linecap="round"/>')
    for L_, sid in ((-1, "pi"), (1, "pd")):
        x = L_ * 42
        s.append(f'<g id="{pid}_{sid}"><path d="M{x - 26},150 L{x + 26},150 L{x + 22},350 L{x - 22},350 Z" fill="{PANT}"/>'
                 f'<path d="M{x - 24},342 L{x + 24},342 L{x + 22 + L_ * 18},372 L{x - 22 + L_ * 6},378 Z" fill="#f4f4f4"/><rect x="{x - 26 + min(0, L_ * 6)}" y="370" width="{52 + 18}" height="10" rx="5" fill="#d8261a"/></g>')
    s.append(f'<circle r="{R}" fill="url(#burbG)"/>')
    s.append(f'<clipPath id="{pid}_clip"><circle r="{R - 4}"/></clipPath><g clip-path="url(#{pid}_clip)"><rect x="{-R}" y="{R * 0.48:.0f}" width="{2 * R}" height="{R}" fill="#ff5a4a" opacity="0.55"/></g>')
    s.append(f'<ellipse cx="0" cy="{R * 0.8:.0f}" rx="{R * 0.42:.0f}" ry="{R * 0.12:.0f}" fill="#1a2030" opacity="0.55"/>')
    # tú dentro: torso con correas, cuello, cabeza con cara, gorra y móvil (que flotarán al caer)
    s.append(f'<g id="{pid}_cuerpo"><path d="M-74,150 L-70,20 Q-66,-6 -30,-10 L30,-10 Q66,-6 70,20 L74,150 Z" fill="{e["ropa"]}"/><path d="M-74,150 L-70,20 Q-66,-6 -30,-10 L30,-10 Q66,-6 70,20 L74,150 Z" fill="url(#brilloRopa)"/>'
             f'<path class="correa" d="M-60,0 L40,150 M60,0 L-40,150" stroke="#1d2433" stroke-width="13"/><rect x="-14" y="64" width="28" height="22" rx="5" fill="#c9ccd2"/>'
             f'<path d="M-14,-46 L14,-46 L18,-8 L-18,-8 Z" fill="{oscurece(e["piel"], 0.88)}"/>'
             f'<g class="cab" id="{pid}_cabG">{cara(pid, 0, -78, 46, e, expr="nervioso")}'
             f'<g id="{pid}_gorra"><path d="M-48,-112 Q0,-160 48,-112 Z" fill="#2f5fbf"/><rect x="-6" y="-116" width="70" height="10" rx="5" fill="#2f5fbf"/></g></g>'
             f'<g id="{pid}_movil"><rect x="20" y="96" width="34" height="56" rx="6" fill="#1a1d22"/><rect x="24" y="101" width="26" height="44" rx="3" fill="#7fe0ff"/></g>'
             + "".join(f'<path d="M{L_ * 62},12 Q{L_ * 120},20 {L_ * 136},-24" stroke="{e["ropa"]}" stroke-width="30" fill="none" stroke-linecap="round"/><circle cx="{L_ * 138}" cy="-30" r="17" fill="{e["piel"]}"/>'
                       f'<path d="M{L_ * 120},-56 Q{L_ * 160},-34 {L_ * 150},-4" stroke="#1d2433" stroke-width="9" fill="none"/>' for L_ in (-1, 1)) + '</g>')
    s.append(f'<g id="{pid}_grito" opacity="0">' + "".join(f'<path d="M{-30 - i * 16},{-30 + i * 2} Q0,{-6 + i * 14} {30 + i * 16},{-30 + i * 2}" stroke="#ffffff" stroke-width="4" fill="none" opacity="{0.8 - i * 0.2:.1f}" transform="translate(0,{30 + i * 14})"/>' for i in range(3)) + '</g>')
    # superficie: brillo grande, costuras y escarcha
    s.append(f'<circle r="{R}" fill="none" stroke="#ffffff" stroke-width="6" opacity="0.85"/>'
             f'<path d="M{-R * 0.72:.0f},{-R * 0.35:.0f} A{R * 0.8:.0f},{R * 0.8:.0f} 0 0 1 {-R * 0.2:.0f},{-R * 0.8:.0f}" stroke="#ffffff" stroke-width="22" fill="none" stroke-linecap="round" opacity="0.55"/>'
             f'<ellipse cx="{R * 0.42:.0f}" cy="{-R * 0.55:.0f}" rx="22" ry="12" fill="#ffffff" opacity="0.7" transform="rotate(35 {R * 0.42:.0f} {-R * 0.55:.0f})"/>'
             f'<ellipse rx="{R}" ry="{R * 0.32:.0f}" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.25"/><ellipse rx="{R * 0.32:.0f}" ry="{R}" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.2"/>'
             f'<circle cy="{-R}" r="12" fill="none" stroke="#9aa3ad" stroke-width="6"/>')
    s.append(f'<g id="{pid}_hielo" opacity="0"><circle r="{R - 3}" fill="none" stroke="#e8fbff" stroke-width="14" stroke-dasharray="18 10"/>'
             + "".join(destello(x, y, rr, "#e8fbff") for x, y, rr in ((-140, -80, 22), (120, -120, 18), (150, 60, 16), (-120, 110, 20), (0, -170, 14))) + '</g>')
    return "".join(s)

def helicoptero(hid):
    """Helicóptero rojo (morro a la derecha). El gancho está en (0,0); el cuerpo encima."""
    s = [f'<g id="{hid}">',
         '<path d="M0,-70 L0,0" stroke="#5b636d" stroke-width="8"/><circle cy="0" r="10" fill="#5b636d"/>',
         '<path d="M-150,-30 L150,-30 M-110,-30 L-90,-62 M110,-30 L90,-62" stroke="#3a3f48" stroke-width="10" stroke-linecap="round"/>',
         '<path d="M-200,-150 L-560,-170 L-560,-150 L-200,-110 Z" fill="url(#rojoH)"/><path d="M-560,-170 L-610,-250 L-575,-250 L-540,-160 Z" fill="#c41f2a"/>',
         '<g id="' + hid + '_cola"><circle cx="-580" cy="-160" r="46" fill="none" stroke="#3a3f48" stroke-width="5" opacity="0.5"/><path d="M-580,-206 L-580,-114" stroke="#3a3f48" stroke-width="8"/></g>',
         '<path d="M-180,-62 Q-235,-62 -235,-135 Q-235,-238 -100,-242 L110,-242 Q200,-236 225,-150 Q232,-70 150,-62 Z" fill="url(#rojoH)"/>',
         '<path d="M60,-226 L120,-226 Q195,-220 214,-150 L214,-118 L60,-118 Z" fill="#9fd6ff"/><path d="M80,-220 L140,-130" stroke="#ffffff" stroke-width="10" opacity="0.4"/>',
         '<rect x="-160" y="-216" width="120" height="120" rx="10" fill="#1a1d22"/>',
         '<rect x="-12" y="-272" width="24" height="32" fill="#3a3f48"/>',
         '<g id="' + hid + '_rotor"><ellipse cx="0" cy="-276" rx="460" ry="10" fill="#2a2e35" opacity="0.85"/></g>',
         '<path d="M-235,-120 L225,-120" stroke="#ffffff" stroke-width="8" opacity="0.6"/>']
    s.append(f'<g>{cara("pil", 140, -176, 30, estilo(81, piel="#c68a62", pelo="#1a1a1a", peinado="corto", gafas=True, barba=True), expr="neutral")}</g>')
    s.append('<g id="pilMovil"><rect x="88" y="-150" width="30" height="46" rx="5" fill="#1a1d22"/><rect x="92" y="-146" width="22" height="36" rx="3" fill="#7fe0ff"/></g>')
    # copiloto asomado por la puerta con unas tijeras gigantes (aparece en el momento)
    s.append('<g id="copi" opacity="0">' + cara("cop", -100, -170, 34, estilo(83, piel="#f2c9a8", pelo="#b07a3a", peinado="corto"), expr="sonrisa")
             + '<path d="M-110,-120 Q-150,-20 -120,60" stroke="#2fa36b" stroke-width="26" fill="none" stroke-linecap="round"/><circle cx="-118" cy="62" r="16" fill="#f2c9a8"/>'
             + '<g transform="translate(-110,70)"><g id="tije">'
             + '<g id="tijAbierta"><path d="M0,0 L130,-30 L128,-16 Z" fill="#dfe5ec" stroke="#7d8894" stroke-width="3"/><path d="M0,0 L130,30 L128,16 Z" fill="#c9d1d9" stroke="#7d8894" stroke-width="3"/></g>'
             + '<g id="tijCerrada" opacity="0"><path d="M0,-3 L140,-4 L138,6 Z" fill="#dfe5ec" stroke="#7d8894" stroke-width="3"/><path d="M0,3 L140,4 L138,-6 Z" fill="#c9d1d9" stroke="#7d8894" stroke-width="3"/></g>'
             + '<circle cx="-26" cy="-18" r="18" fill="none" stroke="#e8261a" stroke-width="8"/><circle cx="-26" cy="18" r="18" fill="none" stroke="#e8261a" stroke-width="8"/><circle r="7" fill="#3a3f48"/></g></g></g>')
    s.append('</g>')
    return "".join(s)

def jugador(jid, x, ropa, h=300, portero=False, lado=1):
    e = estilo(hash(jid) % 997, ropa=ropa)
    extra = f'<circle cx="{x - 46 * h / 300:.0f}" cy="{YG - 125 * h / 300:.0f}" r="{12 * h / 300:.0f}" fill="#ffffff"/><circle cx="{x + 46 * h / 300:.0f}" cy="{YG - 125 * h / 300:.0f}" r="{12 * h / 300:.0f}" fill="#ffffff"/>' if portero else ""
    return f'<g id="{jid}">{persona(x, YG + 6, h, pid=jid + "p", e=e, lado=lado, expr0="neutral")}{extra}</g>'

# ------------------------------------------------------------------ el mundo: cielo, nubes, regla de altura, estadio
W0, W1 = -9000, 10000
mundo = [f'<rect x="{W0}" y="-2000" width="{W1 - W0}" height="{YG + 2000}" fill="url(#cieloV)"/>']
for a_, seed in ((980, 1), (900, 2), (760, 3), (620, 4), (480, 5), (330, 6), (190, 7)):
    mundo.append(nubes(-900, y_alt(a_) - 120, 5, seed, 2600, 260, 1.8, 0.88) + nubes(-7000, y_alt(a_) - 300, 8, seed + 40, 15000, 500, 3.5, 0.8))
# regla de altura (para el plano general)
for m in range(0, 1001, 100):
    y = y_alt(m) + 380
    mundo.append(f'<path d="M1500,{y} L1640,{y}" stroke="#ffffff" stroke-width="10" opacity="0.8"/><text x="1660" y="{y + 26}" font-family="Inter" font-weight="900" font-size="80" fill="#ffffff" opacity="0.9">{m} m</text>')
mundo.append(f'<path d="M1500,{y_alt(1000) + 380} L1500,{YG}" stroke="#ffffff" stroke-width="8" opacity="0.6"/>')
# pájaros (~560 m) y avioneta (~470 m)
for i, (dx, dy) in enumerate(((180, -60), (300, 20), (820, -30), (900, 60), (760, 120))):
    bx, by_ = dx, y_alt(560) + dy
    mundo.append(f'<g class="pajaro" transform="translate({bx},{by_})"><g class="pj"><path class="ala" d="M0,0 Q-40,-30 -80,-6 Q-40,-14 0,8 Q40,-14 80,-6 Q40,-30 0,0 Z" fill="#2a2e35"/>'
                 f'<ellipse cx="0" cy="6" rx="22" ry="14" fill="#2a2e35"/><g class="cabP"><circle cx="16" cy="-4" r="11" fill="#2a2e35"/><circle cx="20" cy="-6" r="5" fill="#ffffff"/><circle cx="21" cy="-6" r="2.4" fill="#111"/><path d="M26,-2 L38,0 L26,4 Z" fill="#f2c14e"/></g></g></g>')
mundo.append(f'<g id="avioneta" transform="translate(1500,{y_alt(470)})"><g id="avI"><path d="M-160,0 Q-150,-30 -60,-34 L120,-30 Q170,-24 170,0 Q170,22 120,26 L-60,28 Q-150,26 -160,0 Z" fill="#ffffff"/>'
             '<path d="M-20,-4 L40,-150 L80,-150 L60,-4 Z M-20,4 L40,150 L80,150 L60,4 Z" fill="#e8261a"/><path d="M-140,-6 L-180,-70 L-150,-70 L-110,-8 Z" fill="#e8261a"/>'
             '<path d="M90,-24 Q140,-22 152,-2 L90,-2 Z" fill="#9fd6ff"/><rect x="168" y="-50" width="8" height="100" rx="4" fill="#3a3f48"/>'
             + cara("avp", 112, -36, 16, estilo(91, peinado="corto", gafas=True), expr="neutral") + '</g></g>')
# estadio: gradas con público, focos, césped con rayas, porterías y jugadores
r9 = random.Random(9)
mundo.append(f'<rect x="{W0}" y="{YG - 640}" width="{W1 - W0}" height="560" fill="url(#gradas)"/>'
             + "".join(f'<rect x="{W0}" y="{YG - 640 + i * 90}" width="{W1 - W0}" height="8" fill="#4a5470"/>' for i in range(6))
             + "".join((lambda x, y, c, p: f'<rect x="{x - 11:.0f}" y="{y:.0f}" width="22" height="30" rx="8" fill="{c}"/><circle cx="{x:.0f}" cy="{y - 9:.0f}" r="9" fill="{p}"/>')(r9.uniform(W0, W1), YG - 590 + r9.randint(0, 5) * 90 + r9.uniform(20, 40), r9.choice(("#f2c14e", "#e2725b", "#3f7ad8", "#ffffff", "#2fa36b", "#d94f6b")), r9.choice(PIELES)) for _ in range(2600))
             + "".join(f'<rect x="{x - 12}" y="{YG - 1500}" width="24" height="900" fill="#9aa3ad"/><rect x="{x - 90}" y="{YG - 1580}" width="180" height="90" rx="10" fill="#dfe5ec"/><ellipse class="foco" cx="{x}" cy="{YG - 1535}" rx="200" ry="120" fill="url(#brilloOro)" opacity="0.6"/>' for x in (-500, 1580)))
mundo.append(f'<rect x="{W0}" y="{YG - 80}" width="{W1 - W0}" height="2600" fill="url(#cesped)"/>' + "".join(f'<rect x="{W0 + i * 260}" y="{YG - 80}" width="130" height="2600" fill="#ffffff" opacity="0.06"/>' for i in range(80))
             + f'<path d="M{W0},{YG + 30} L{W1},{YG + 30}" stroke="#ffffff" stroke-width="8" opacity="0.7"/><ellipse cx="540" cy="{YG + 120}" rx="420" ry="60" fill="none" stroke="#ffffff" stroke-width="8" opacity="0.6"/>')
for gx, s_ in ((-180, 1), (1260, -1)):
    mundo.append(f'<path d="M{gx},{YG + 10} L{gx},{YG - 240} L{gx + s_ * 150},{YG - 240} L{gx + s_ * 150},{YG + 10}" stroke="#ffffff" stroke-width="14" fill="none"/>'
                 + "".join(f'<path d="M{gx + s_ * k * 30},{YG - 240} L{gx + s_ * k * 30},{YG + 10}" stroke="#ffffff" stroke-width="3" opacity="0.5"/>' for k in range(1, 5)))
JUG = [("j1", 120, "#3f7ad8", 1), ("j2", 330, "#e2725b", 1), ("j3", 780, "#3f7ad8", -1), ("j4", 980, "#e2725b", -1)]
for jid, x, ropa, lado in JUG:
    mundo.append(jugador(jid, x, ropa, 330, lado=lado))
mundo.append(jugador("port", 1180, "#2fa36b", 330, portero=True, lado=-1))
mundo.append(f'<g id="amigo" opacity="0">{persona(250, YG + 6, 400, pid="amg", e=estilo(33, ropa="#2fa36b", peinado="rizado"), expr0="sonrisa")}</g>')
mundo.append(f'<ellipse id="sombra" cx="540" cy="{YG + 10}" rx="140" ry="22" fill="#000" opacity="0.0"/>')
mundo.append(f'<g id="polvo" opacity="0">' + "".join(f'<circle cx="{540 + dx}" cy="{YG - 20}" r="{60 + abs(dx) % 40}" fill="#cfe6c0" opacity="0.7"/>' for dx in (-300, -180, -60, 60, 180, 300)) + '</g>')
# helicóptero con la burbuja colgando (péndulo) y la burbuja que cae suelta
mundo.append(f'<g transform="translate(540,{HOOK0})"><g id="heliG">{helicoptero("heli")}'
             f'<g id="pend"><path id="cuerdaA" d="M0,0 L0,{L}" stroke="#c9a46a" stroke-width="9"/><g transform="translate(0,{L + R})"><g id="bubA">{burbuja("ba")}</g></g></g>'
             f'<path id="cuerdaCorta" d="M0,0 L0,70" stroke="#c9a46a" stroke-width="9" opacity="0"/></g></g>')
mundo.append(f'<g transform="translate(540,{y_alt(1000)})"><g id="bubB" opacity="0"><g id="bubBr">{burbuja("bb", cuerda=380)}</g></g></g>')
# explosión final (trozos de plástico)
mundo.append(f'<g transform="translate(540,{YC0})"><g id="boom" opacity="0"><circle r="420" fill="url(#brilloBlanco)"/>' + "".join(
    f'<path class="trozo" d="M0,0 l{30 + i % 3 * 12},{-16 - i % 2 * 10} l{-14},{30 + i % 4 * 6} Z" fill="#bfefff" stroke="#ffffff" stroke-width="3"/>' for i in range(16)) + '</g></g>')

ESC.append(f'<div class="esc" id="mundo"><div class="cam" id="zoom"><div id="follow" style="position:absolute;left:0;top:0;width:1080px;height:1920px">'
           f'<svg width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0;overflow:visible">{"".join(mundo)}</svg></div></div></div>')

# ------------------------------------------------------------------ cámara: foco (punto del mundo en el centro) y zoom
def foco(t, F_, S_, d, ease="power2.inOut"):
    J(f'tl.to("#follow", {{y:{960 - F_:.0f}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f}); tl.to("#zoom", {{scale:{S_}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
def foco_set(t, F_, S_):
    J(f'tl.set("#follow", {{y:{960 - F_:.0f}}}, {t:.2f}); tl.set("#zoom", {{scale:{S_}}}, {t:.2f});')
ALT = []
def altura(t, a, d=0.0, ease="none"):
    """Altímetro: el número que se ve arriba a la izquierda."""
    J(f'tl.to(ALT, {{v:{a}, duration:{max(0.01, d):.2f}, ease:"{ease}", onUpdate:pintaAlt}}, {t:.2f});')
J('const ALT = {v:1000}; const pintaAlt = () => { const e = document.getElementById("altN"); if (e) e.textContent = Math.round(ALT.v).toLocaleString("es-ES"); };')
OVR.append('<div id="altim"><small>ALTURA</small><b><span id="altN">1.000</span> m</b></div>')
J('tl.set("#mundo", {opacity:1}, 0);')
# rotor y cola giran siempre; foco del estadio late; nubes se mueven
J(f'tl.fromTo("#heli_rotor", {{scaleX:1}}, {{scaleX:0.15, svgOrigin:"0 -276", duration:0.06, yoyo:true, repeat:{int(DUR / 0.06)}, ease:"none", immediateRender:false}}, 0);')
J(f'tl.fromTo("#heli_cola", {{rotation:0}}, {{rotation:{int(DUR * 900)}, svgOrigin:"-580 -160", duration:{DUR:.2f}, ease:"none", immediateRender:false}}, 0);')
J(f'tl.fromTo(".nube", {{x:0}}, {{x:-260, duration:{DUR:.2f}, ease:"none", immediateRender:false}}, 0);')
J(f'tl.fromTo(".pj .ala", {{scaleY:1}}, {{scaleY:-0.6, transformOrigin:"50% 50%", duration:0.18, yoyo:true, repeat:{int(DUR / 0.18)}, ease:"sine.inOut", immediateRender:false}}, 0);')
parpadeo("ba", 0, DUR, 2); parpadeo("bb", 0, DUR, 3); parpadeo("pil", 0, DUR, 4)
FX.append(("helice", 0.0))

# ================================================================== 1) GANCHO: a 1.000 m, colgando del helicóptero… plano general de toda la caída… y cortan
f1, f2 = 0.0, F(2)
J(f'tl.set("#heliG", {{y:{-1000 * PXM}}}, 0);')
foco_set(0, y_alt(1000) - 260, 0.8)
J(f'tl.fromTo("#pend", {{rotation:-6}}, {{rotation:6, svgOrigin:"0 0", duration:1.1, yoyo:true, repeat:5, ease:"sine.inOut", immediateRender:false}}, 0);')
J(f'tl.fromTo("#bubA", {{rotation:-20}}, {{rotation:20, svgOrigin:"0 0", duration:0.9, yoyo:true, repeat:7, ease:"sine.inOut", immediateRender:false}}, 0);')
expr("ba", 0.0, "nervioso", "preocupado")
J('tl.fromTo("#zoom", {scale:0.95}, {scale:0.8, duration:0.6, ease:"power3.out", immediateRender:false}, 0);')
OVR.append('<div id="gancho"><div class="g1">1.000 METROS</div><div class="g2">SIN PARACAÍDAS</div></div>')
J(f'tl.fromTo("#gancho", {{opacity:1, scale:1.2}}, {{scale:1, duration:0.4, ease:"back.out(2)", immediateRender:false}}, 0); tl.to("#gancho", {{opacity:0, duration:0.25}}, {P("mil") - 0.2:.2f});')
# plano general de toda la columna: del helicóptero al estadio
foco(P("mil") - 0.4, (y_alt(1000) + YG) / 2 - 300, 0.105, 0.7, "power3.inOut")
foco(P("cortan") - 0.45, y_alt(1000) - 200, 0.85, 0.4, "power3.inOut")
# tijeretazo en el gancho
J(f'tl.set("#copi", {{opacity:1}}, {P("cortan") - 0.5:.2f}); tl.fromTo("#copi", {{x:-60}}, {{x:0, duration:0.25, ease:"back.out(2)", immediateRender:false}}, {P("cortan") - 0.5:.2f});')
tcut1 = P("cortan") + 0.15
J(f'tl.set("#tijAbierta", {{opacity:0}}, {P("cortan"):.2f}); tl.set("#tijCerrada", {{opacity:1}}, {P("cortan"):.2f}); tl.set("#tijAbierta", {{opacity:1}}, {f2 + 0.35:.2f}); tl.set("#tijCerrada", {{opacity:0}}, {f2 + 0.35:.2f});')
J(f'tl.set("#pend", {{opacity:0}}, {tcut1:.2f}); tl.set("#cuerdaCorta", {{opacity:1}}, {tcut1:.2f}); tl.set("#bubB", {{opacity:1, y:0}}, {tcut1:.2f}); tl.set("#bubBr", {{rotation:0}}, {tcut1:.2f});')
J(f'tl.to("#bubB", {{y:520, duration:{f2 - tcut1:.2f}, ease:"power2.in"}}, {tcut1:.2f}); tl.to("#bubBr", {{rotation:-30, svgOrigin:"0 0", duration:{f2 - tcut1:.2f}}}, {tcut1:.2f});')
expr("bb", tcut1, "nervioso", "sorpresa", abierta=True)
FX.append(("snip", P("cortan"))); FX.append(("whoosh", tcut1))

# ================================================================== 2) PRIMERO TE ATAN DENTRO (en el césped del estadio)
# «rebobinado»: la cámara baja de golpe de 1.000 m al campo y todo vuelve a su sitio
J(f'tl.set("#bubB", {{opacity:0}}, {f2 + 0.35:.2f}); tl.set("#pend", {{opacity:1}}, {f2 + 0.35:.2f}); tl.set("#cuerdaCorta, #copi", {{opacity:0}}, {f2 + 0.35:.2f}); tl.set("#heliG", {{y:0}}, {f2 + 0.35:.2f});')
J(f'tl.set("#pend, #bubA", {{rotation:0}}, {f2 + 0.35:.2f});')
OVR.append('<div id="rebob"><i></i><i></i> ANTES</div>')
J(f'tl.set("#rebob", {{opacity:0}}, 0); tl.set("#rebob", {{opacity:1}}, {f2:.2f}); tl.set("#rebob", {{opacity:0}}, {f2 + 1.0:.2f});')
foco(f2, YC0 - 120, 1.0, 0.85, "power3.inOut")
altura(f2, 0, 0.85, "power3.inOut")
J(f'tl.set("#amigo", {{opacity:1}}, {f2:.2f}); tl.to("#amg .brazo", {{rotation:-70, svgOrigin:"{250 + 34 * 400 / 300:.0f} {YG + 6 - 228 * 400 / 300:.0f}", duration:0.3, yoyo:true, repeat:5}}, {P("atan"):.2f});')
J(f'tl.fromTo("#ba_cuerpo .correa", {{stroke:"#1d2433"}}, {{stroke:"#ffcf3a", duration:0.15, yoyo:true, repeat:3, immediateRender:false}}, {P("atan"):.2f});')
expr("ba", f2, "sonrisa", "neutral")
nota("CABEZA Y PECHO DENTRO", P("cabeza") - 0.1, P("piernas") - 0.1, 40, 640, "#7fe0ff")
nota("PIERNAS FUERA", P("piernas") - 0.1, F(3), 40, 640, "#ffcf3a")
J(f'tl.fromTo("#ba_pi, #ba_pd", {{x:0}}, {{x:8, duration:0.12, yoyo:true, repeat:5, immediateRender:false}}, {P("piernas"):.2f});')
J(f'tl.to("#j1, #j2, #j3, #j4, #port", {{y:-12, duration:0.2, yoyo:true, repeat:3, stagger:0.08}}, {f2 + 0.8:.2f});')

# ================================================================== 3) DESPEGA: los pies dejan el césped
t3 = P("despega")
J(f'tl.to("#amigo", {{x:-260, duration:0.8, ease:"power2.in"}}, {t3:.2f});')
J(f'tl.fromTo("#polvo", {{opacity:0, scale:0.6}}, {{opacity:0.8, scale:1.4, svgOrigin:"540 {YG}", duration:0.6, immediateRender:false}}, {t3:.2f}); tl.to("#polvo", {{opacity:0, duration:0.8}}, {t3 + 0.9:.2f});')
J(f'tl.to("#heliG", {{y:-30, duration:0.5, ease:"power1.out"}}, {t3 + 0.1:.2f});')
J(f'tl.to("#heliG", {{y:{-100 * PXM}, duration:{F(4) + 0.4 - (P("pies") + 0.2):.2f}, ease:"power2.in"}}, {P("pies") + 0.2:.2f});')
foco(P("pies") + 0.2, y_alt(100) - 150, 0.85, F(4) + 0.4 - (P("pies") + 0.2), "power2.in")
altura(P("pies") + 0.2, 100, F(4) + 0.4 - (P("pies") + 0.2), "power2.in")
J(f'tl.fromTo("#ba_pi", {{rotation:-10}}, {{rotation:12, svgOrigin:"-42 150", duration:0.25, yoyo:true, repeat:7, immediateRender:false}}, {P("pies"):.2f}); tl.fromTo("#ba_pd", {{rotation:10}}, {{rotation:-12, svgOrigin:"42 150", duration:0.25, yoyo:true, repeat:7, immediateRender:false}}, {P("pies"):.2f});')
expr("ba", P("pies"), "nervioso", "sorpresa", abierta=True)
J(f'tl.to("#j1, #j2, #j3, #j4", {{y:-30, duration:0.25, yoyo:true, repeat:1, stagger:0.05}}, {P("pies"):.2f});')
FX.append(("helice", t3)); FX.append(("whoosh", P("pies")))

# ================================================================== 4) A 100 m GIRA COMO UNA PEONZA · 5) A 500 m: FRÍO, PIERNAS CONGELADAS, EL PILOTO NI TE MIRA
J(f'tl.fromTo("#bubA", {{rotation:0}}, {{rotation:1080, svgOrigin:"0 0", duration:{F(5) - P("girar") + 0.3:.2f}, ease:"sine.inOut", immediateRender:false}}, {P("girar") - 0.3:.2f});')
J(f'tl.fromTo("#pend", {{rotation:-10}}, {{rotation:10, svgOrigin:"0 0", duration:0.7, yoyo:true, repeat:{int((F(6) - F(4)) / 0.7)}, ease:"sine.inOut", immediateRender:false}}, {F(4):.2f});')
expr("ba", P("girar"), "nervioso", "preocupado", abierta=True)
nota("GIRA COMO UNA PEONZA", P("peonza") - 0.4, F(5), 40, 640, "#ff5a4a")
# sube a 500 m (las nubes pasan a toda velocidad)
t5a, t5b = F(4) + 0.6, P("quinientos") + 0.1
J(f'tl.to("#heliG", {{y:{-500 * PXM}, duration:{t5b - t5a:.2f}, ease:"power1.inOut"}}, {t5a:.2f});')
foco(t5a, y_alt(500) - 150, 0.85, t5b - t5a, "power1.inOut")
altura(t5a, 500, t5b - t5a, "power1.inOut")
J(f'tl.to("#ba_hielo", {{opacity:1, duration:1.0}}, {P("congela") - 0.5:.2f});')
J(f'tl.fromTo("#ba_pi, #ba_pd", {{x:-5}}, {{x:5, duration:0.05, yoyo:true, repeat:{int((F(6) - P("congela")) / 0.05)}, immediateRender:false}}, {P("congela"):.2f});')
J(f'tl.set("#ba_bocaO", {{opacity:0}}, {P("congela"):.2f}); tl.to("#ba_boca", {{opacity:1}}, {P("congela"):.2f});')
expr("ba", P("congela") - 0.1, "nervioso", "preocupado")
OVR.append('<div id="viento">' + "".join(f'<i style="top:{560 + i * 150}px;left:{(i * 280) % 1000}px"></i>' for i in range(8)) + '</div>')
J(f'tl.set("#viento", {{opacity:0}}, 0); tl.to("#viento", {{opacity:1, duration:0.3}}, {P("viento") - 0.2:.2f}); tl.to("#viento", {{opacity:0, duration:0.3}}, {F(6):.2f});')
J(f'tl.fromTo("#viento i", {{x:600}}, {{x:-900, duration:0.45, repeat:{int((F(6) - P("viento")) / 0.45)}, stagger:0.07, ease:"none", immediateRender:false}}, {P("viento") - 0.2:.2f});')
FX.append(("viento", P("viento") - 0.2))
# el piloto ni te mira: la cámara sube a la cabina (está con el móvil)
tp = P("piloto") - 0.35
foco(tp, y_alt(500) - R - L - 170, 1.55, 0.45, "power3.inOut")
J(f'tl.to("#pilMovil", {{y:-8, duration:0.2, yoyo:true, repeat:3}}, {tp + 0.4:.2f});')
expr("pil", tp, "sonrisa", "neutral")
t6a, t6b = F(6) - 0.4, P("silencio") - 0.2
J(f'tl.to("#heliG", {{y:{-1000 * PXM}, duration:{t6b - t6a:.2f}, ease:"power2.inOut"}}, {t6a:.2f});')
foco(t6a, y_alt(1000) - 260, 0.9, t6b - t6a, "power2.inOut")
altura(t6a, 1000, t6b - t6a, "power2.inOut")
J(f'tl.to("#pend", {{rotation:0, svgOrigin:"0 0", duration:0.8}}, {P("silencio") - 0.2:.2f}); tl.to("#bubA", {{rotation:0, svgOrigin:"0 0", duration:0.8}}, {P("silencio") - 0.2:.2f});')
expr("ba", P("silencio"), "triste", "preocupado")
J(f'tl.set("#copi", {{opacity:1}}, {P("alguien") - 0.1:.2f}); tl.fromTo("#copi", {{x:-80}}, {{x:0, duration:0.35, ease:"back.out(2)", immediateRender:false}}, {P("alguien") - 0.1:.2f});')
J(f'tl.fromTo("#tije", {{opacity:0}}, {{opacity:1, duration:0.15, immediateRender:false}}, {P("tijeras") - 0.2:.2f});')
for k_ in range(3):
    J(f'tl.set("#tijAbierta", {{opacity:0}}, {P("tijeras") + k_ * 0.25:.2f}); tl.set("#tijCerrada", {{opacity:1}}, {P("tijeras") + k_ * 0.25:.2f}); tl.set("#tijAbierta", {{opacity:1}}, {P("tijeras") + k_ * 0.25 + 0.12:.2f}); tl.set("#tijCerrada", {{opacity:0}}, {P("tijeras") + k_ * 0.25 + 0.12:.2f});')
foco(P("tijeras") - 0.2, y_alt(1000) - R - L + 40, 1.6, 0.5, "power3.inOut")
expr("ba", P("tijeras"), "nervioso", "sorpresa", abierta=True)
tc = P("cortan", 2) + 0.05
J(f'tl.set("#tijAbierta", {{opacity:0}}, {tc:.2f}); tl.set("#tijCerrada", {{opacity:1}}, {tc:.2f});')
J(f'tl.set("#pend", {{opacity:0}}, {tc + 0.08:.2f}); tl.set("#cuerdaCorta", {{opacity:1}}, {tc + 0.08:.2f}); tl.set("#bubB", {{opacity:1, y:0, x:0}}, {tc + 0.08:.2f}); tl.set("#bubBr", {{rotation:0}}, {tc + 0.08:.2f});')
J(f'tl.fromTo("#flashB", {{opacity:0.8}}, {{opacity:0, duration:0.25, immediateRender:false}}, {tc + 0.08:.2f});')
foco(tc + 0.1, y_alt(1000) - 60, 0.95, 0.5, "power2.out")
FX.append(("snip", tc)); FX.append(("golpe", tc + 0.1))

# ================================================================== 8-15) LA CAÍDA: la cámara sigue a la burbuja
CAI = [(tc + 0.15, 1000), (F(9), 975), (F(10), 940), (F(11), 880), (F(12), 800), (F(13), 650), (P("abajo") - 0.2, 470), (F(14), 330), (F(15), 230), (P("cien", 3) - 0.1, 100),
       (P("cincuenta") - 0.05, 50), (P("diez") - 0.05, 10), (P("explota") + 0.02, 0)]
for (ta, aa), (tb, ab) in zip(CAI, CAI[1:]):
    ease = "power2.in" if aa == 1000 else "none"
    J(f'tl.to("#bubB", {{y:{(1000 - ab) * PXM}, duration:{tb - ta:.2f}, ease:"{ease}"}}, {ta:.2f});')
    altura(ta, ab, tb - ta, ease)
def sigue(ta, tb, ab, off, S_, ease="none"):
    foco(ta, y_alt(ab) - off, S_, tb - ta, ease)
# 8) el estómago se queda arriba: la gorra y el móvil flotan dentro de la burbuja
sigue(CAI[0][0], F(9), 975, 0, 1.25, "power2.in")
J(f'tl.to("#bb_gorra", {{y:-60, rotation:-25, svgOrigin:"0 -120", duration:0.6, ease:"power2.out"}}, {P("estomago") - 0.2:.2f}); tl.to("#bb_movil", {{y:-150, x:-40, rotation:60, svgOrigin:"37 124", duration:0.8, ease:"power2.out"}}, {P("estomago") - 0.1:.2f});')
J(f'tl.to("#bb_cuerpo", {{y:-14, duration:0.3, yoyo:true, repeat:1}}, {P("estomago"):.2f});')
expr("bb", P("estomago") - 0.2, "nervioso", "sorpresa", abierta=True)
nota("TU ESTÓMAGO SE QUEDA ARRIBA", P("estomago") - 0.2, F(9), 40, 640, "#ffcf3a")
# 9) casi 100 km/h al tercer segundo (velocímetro)
OVR.append('<div id="velo"><div class="esfera"><div class="aguja2" id="agV"></div><div class="centro"></div></div><b><span id="velN">0</span> km/h</b></div>')
J('const VEL = {v:0}; const pintaVel = () => { document.getElementById("velN").textContent = Math.round(VEL.v); document.getElementById("agV").style.transform = "rotate(" + (-120 + VEL.v * 1.6) + "deg)"; };')
J(f'tl.set("#velo", {{opacity:0}}, 0); tl.fromTo("#velo", {{opacity:0, scale:0.5}}, {{opacity:1, scale:1, duration:0.3, ease:"back.out(2)", immediateRender:false}}, {F(9):.2f}); tl.to("#velo", {{opacity:0, duration:0.3}}, {F(13) - 0.1:.2f});')
J(f'tl.to(VEL, {{v:90, duration:{P("cien", 2) - F(9) + 0.2:.2f}, ease:"power1.out", onUpdate:pintaVel}}, {F(9):.2f});')
sigue(F(9), F(10), 940, 0, 1.0)
J(f'tl.fromTo("#bubBr", {{rotation:0}}, {{rotation:-160, svgOrigin:"0 0", duration:{F(10) - F(9):.2f}, ease:"sine.inOut", immediateRender:false}}, {F(9):.2f});')
expr("bb", F(9), "nervioso", "sorpresa", abierta=True)
FX.append(("viento", F(9)))
# 10) el aire frena… pero mucho menos de lo que crees (flechas de fuerzas)
OVR.append('<div id="fuerzas"><div class="fl arriba" id="flA"><i></i><span>AIRE</span></div><div class="fl abajo"><i></i><span>TU PESO</span></div></div>')
J(f'tl.set("#fuerzas", {{opacity:0}}, 0); tl.to("#fuerzas", {{opacity:1, duration:0.2}}, {P("aire") - 0.2:.2f}); tl.to("#fuerzas", {{opacity:0, duration:0.25}}, {F(11) + 0.6:.2f});')
J(f'tl.fromTo("#flA", {{scaleY:0.2}}, {{scaleY:0.55, transformOrigin:"50% 100%", duration:0.6, ease:"power2.out", immediateRender:false}}, {P("frena") - 0.1:.2f});')
J(f'tl.fromTo("#flA", {{scaleY:0.55}}, {{scaleY:0.42, transformOrigin:"50% 100%", duration:0.3, immediateRender:false}}, {P("menos") - 0.1:.2f});')
J(f'tl.to(VEL, {{v:118, duration:{F(11) - F(10):.2f}, ease:"none", onUpdate:pintaVel}}, {F(10):.2f});')
sigue(F(10), F(11), 880, 0, 1.0)
J(f'tl.to("#bubBr", {{rotation:-330, svgOrigin:"0 0", duration:{F(11) - F(10):.2f}, ease:"sine.inOut"}}, {F(10):.2f});')
# 11) 140 km/h y de ahí ya no pasas (la burbuja se aplasta un poco con el aire)
J(f'tl.to(VEL, {{v:140, duration:{P("cuarenta") - F(11) + 0.2:.2f}, ease:"power2.out", onUpdate:pintaVel}}, {F(11):.2f});')
J(f'tl.fromTo("#velo", {{boxShadow:"0 0 0 0 rgba(255,59,47,0)"}}, {{boxShadow:"0 0 50px 10px rgba(255,59,47,0.8)", duration:0.25, yoyo:true, repeat:5, immediateRender:false}}, {P("cuarenta"):.2f});')
nota("VELOCIDAD MÁXIMA", P("cuarenta"), F(12), 40, 640, "#ff5a4a")
J(f'tl.fromTo("#bubBr", {{scaleY:1, scaleX:1}}, {{scaleY:0.9, scaleX:1.06, svgOrigin:"0 0", duration:0.15, yoyo:true, repeat:7, immediateRender:false}}, {P("pasas") - 0.6:.2f});')
sigue(F(11), F(12), 800, 0, 0.95)
J(f'tl.to("#bubBr", {{rotation:-520, svgOrigin:"0 0", duration:{F(12) - F(11):.2f}, ease:"sine.inOut"}}, {F(11):.2f});')
# 12) casi medio minuto dando vueltas y gritando (cronómetro)
OVR.append('<div id="crono"><small>CAYENDO</small><b>0:<span id="croN">00</span></b></div>')
J('const CR = {v:0}; const pintaCr = () => { document.getElementById("croN").textContent = String(Math.round(CR.v)).padStart(2, "0"); };')
J(f'tl.set("#crono", {{opacity:0}}, 0); tl.fromTo("#crono", {{opacity:0, x:200}}, {{opacity:1, x:0, duration:0.3, immediateRender:false}}, {P("minuto") - 0.4:.2f}); tl.to("#crono", {{opacity:0, duration:0.3}}, {F(14) - 0.1:.2f});')
J(f'tl.to(CR, {{v:28, duration:{F(14) - P("minuto"):.2f}, ease:"none", onUpdate:pintaCr}}, {P("minuto") - 0.3:.2f});')
J(f'tl.to("#bubBr", {{rotation:-1600, svgOrigin:"0 0", duration:{F(13) - F(12):.2f}, ease:"none"}}, {F(12):.2f});')
J(f'tl.set("#bb_grito", {{opacity:1}}, {P("gritando") - 0.2:.2f}); tl.fromTo("#bb_grito path", {{scale:0.6, opacity:0}}, {{scale:1.3, opacity:0.9, svgOrigin:"0 -40", duration:0.3, stagger:0.1, repeat:5, immediateRender:false}}, {P("gritando") - 0.2:.2f}); tl.set("#bb_grito", {{opacity:0}}, {F(13) + 0.4:.2f});')
expr("bb", P("gritando") - 0.2, "nervioso", "sorpresa", abierta=True)
sigue(F(12), F(13), 650, 0, 0.9)
FX.append(("grito", P("gritando") - 0.1))
# 13) los pájaros te miran · una avioneta te esquiva · abajo el campo se hace enorme
J(f'tl.to("#bubBr", {{rotation:-1800, svgOrigin:"0 0", duration:{P("abajo") - F(13):.2f}, ease:"sine.out"}}, {F(13):.2f});')
sigue(F(13), P("abajo") - 0.2, 470, 0, 0.75)
J(f'tl.to(".pajaro .cabP", {{rotation:40, svgOrigin:"16 -4", duration:0.25, stagger:0.06}}, {P("pajaros") - 0.1:.2f}); tl.to(".pajaro", {{y:"-=40", duration:0.6, stagger:0.05, ease:"power2.out"}}, {P("miran"):.2f});')
expr("bb", P("pajaros"), "nervioso", "preocupado")
J(f'tl.fromTo("#avI", {{x:0, y:0, rotation:0}}, {{x:-2600, y:-120, rotation:-28, svgOrigin:"0 0", duration:1.6, ease:"power1.inOut", immediateRender:false}}, {P("avioneta") - 0.5:.2f});')
expr("avp", P("esquiva") - 0.2, "nervioso", "sorpresa", abierta=True)
FX.append(("avioneta", P("avioneta") - 0.5))
# el campo se hace enorme: plano que mira hacia abajo, con el estadio ya a la vista
sigue(P("abajo") - 0.2, F(14), 330, -2300, 0.32, "power1.inOut")
J(f'tl.to(".foco", {{opacity:1, duration:0.3, yoyo:true, repeat:5}}, {P("abajo"):.2f});')
J(f'tl.to("#bubBr", {{rotation:-1980, svgOrigin:"0 0", duration:{F(14) - P("abajo") + 0.2:.2f}, ease:"none"}}, {P("abajo") - 0.2:.2f});')
# 14-15) la burbuja solo salva de caídas pequeñas (un 2.º piso) · desde 1.000 m = un muro a toda velocidad
CASA = ('<svg viewBox="0 0 420 420" width="420" height="420"><rect width="420" height="420" rx="30" fill="#bfe3ff"/><rect y="340" width="420" height="80" fill="#4fb35a"/>'
        '<rect x="40" y="120" width="190" height="220" fill="#f4e2c8"/><polygon points="25,120 135,50 245,120" fill="#c65b46"/><rect x="70" y="150" width="50" height="50" fill="#9fd6ff"/><rect x="150" y="150" width="50" height="50" fill="#9fd6ff"/><rect x="110" y="260" width="50" height="80" fill="#7d4f2a"/>'
        '<path d="M250,120 L250,340" stroke="#ffffff" stroke-width="4" stroke-dasharray="10 8"/><text x="262" y="236" font-family="Inter" font-weight="900" font-size="34" fill="#1d2433">6-8 m</text>'
        '<g id="miniB"><circle cx="330" cy="300" r="34" fill="#bfefff" stroke="#ffffff" stroke-width="5" opacity="0.9"/><circle cx="330" cy="290" r="11" fill="#e0ac85"/></g>'
        '<circle cx="360" cy="70" r="40" fill="#2fd27a"/><path d="M342,70 L356,84 L382,56" stroke="#fff" stroke-width="10" fill="none" stroke-linecap="round"/></svg>')
MURO = ('<svg viewBox="0 0 420 420" width="420" height="420"><rect width="420" height="420" rx="30" fill="#ffd9c8"/><rect y="340" width="420" height="80" fill="#9aa0a6"/>'
        + "".join(f'<rect x="{260 + (j % 2) * 30 + i * 0}" y="{60 + j * 40}" width="60" height="36" fill="#b8442f" stroke="#ffd9c8" stroke-width="4"/><rect x="{320 + (j % 2) * 30}" y="{60 + j * 40}" width="60" height="36" fill="#b8442f" stroke="#ffd9c8" stroke-width="4"/>' for j in range(7) for i in range(1))
        + '<g id="miniM"><circle cx="200" cy="230" r="40" fill="#bfefff" stroke="#ffffff" stroke-width="5"/><circle cx="200" cy="220" r="12" fill="#e0ac85"/></g>'
        '<path d="M40,230 L150,230 M60,200 L140,200 M60,260 L140,260" stroke="#ffffff" stroke-width="8" stroke-linecap="round" opacity="0.8"/>'
        '<text x="30" y="70" font-family="Inter" font-weight="900" font-size="40" fill="#1d2433">140 km/h</text>'
        '<circle cx="80" cy="140" r="40" fill="#ff3b2f"/><path d="M60,120 L100,160 M100,120 L60,160" stroke="#fff" stroke-width="10" stroke-linecap="round"/></svg>')
OVR.append(f'<div class="cmp" id="cmpA">{CASA}<b>CAÍDAS PEQUEÑAS</b></div><div class="cmp" id="cmpB">{MURO}<b>DESDE 1.000 m</b></div>')
J(f'tl.set("#cmpA, #cmpB", {{opacity:0}}, 0); tl.fromTo("#cmpA", {{opacity:0, x:-500, rotation:-8}}, {{opacity:1, x:0, rotation:-3, duration:0.4, ease:"back.out(1.6)", immediateRender:false}}, {F(14):.2f});')
J(f'tl.fromTo("#miniB", {{y:-200}}, {{y:0, duration:0.45, ease:"bounce.out", repeat:3, repeatDelay:0.3, immediateRender:false}}, {F(14) + 0.3:.2f});')
J(f'tl.to("#cmpA", {{opacity:0, x:-500, duration:0.3, ease:"power2.in"}}, {F(15) - 0.1:.2f}); tl.fromTo("#cmpB", {{opacity:0, x:500, rotation:8}}, {{opacity:1, x:0, rotation:3, duration:0.4, ease:"back.out(1.6)", immediateRender:false}}, {F(15):.2f});')
J(f'tl.fromTo("#miniM", {{x:-120}}, {{x:60, duration:0.35, ease:"power3.in", immediateRender:false}}, {P("estamparte") - 0.2:.2f}); tl.to("#miniM", {{scaleX:0.4, svgOrigin:"260 230", duration:0.08}}, {P("estamparte") + 0.15:.2f});')
J(f'tl.fromTo("#cmpB", {{x:0}}, {{x:16, duration:0.05, yoyo:true, repeat:7, immediateRender:false}}, {P("estamparte") + 0.15:.2f}); tl.to("#cmpB", {{opacity:0, duration:0.3}}, {F(16) - 0.1:.2f});')
FX.append(("boing", F(14) + 0.75)); FX.append(("golpe", P("estamparte") + 0.15))
sigue(F(14), F(15), 230, -250, 0.85)
J(f'tl.to("#bubBr", {{rotation:-2160, svgOrigin:"0 0", duration:{F(16) - F(14):.2f}, ease:"none"}}, {F(14):.2f});')
sigue(F(15), P("cien", 3) - 0.1, 100, -250, 0.85)

# ================================================================== 16-19) QUEDAN 100 m · LOS JUGADORES MIRAN ARRIBA · EL PORTERO HUYE · DIEZ… · EXPLOTA
t16 = P("cien", 3) - 0.1
sigue(t16, P("cincuenta") - 0.05, 50, -950, 0.42, "power1.inOut")
for jid, x, ropa, lado in JUG + [("port", 1180, "", -1)]:
    expr(jid + "p", P("jugadores") - 0.1, "nervioso", "sorpresa", abierta=True)
J(f'tl.to("#j1, #j2, #j3, #j4, #port", {{y:-24, duration:0.2, yoyo:true, repeat:1, stagger:0.06}}, {P("levantan") - 0.1:.2f});')
J(f'tl.to("#sombra", {{opacity:0.35, rx:240, duration:{P("explota") - t16:.2f}, ease:"power2.in"}}, {t16:.2f});')
J(f'tl.to("#bubBr", {{rotation:-2340, svgOrigin:"0 0", duration:{P("diez") - F(16):.2f}, ease:"power1.out"}}, {F(16):.2f});')
# el portero sale corriendo (con saltitos)
J(f'tl.to("#port", {{x:900, duration:1.6, ease:"power2.in"}}, {P("portero") - 0.1:.2f}); tl.to("#port", {{y:-30, duration:0.12, yoyo:true, repeat:13}}, {P("portero") - 0.1:.2f});')
J(f'tl.to("#j1, #j2", {{x:-700, duration:1.4, ease:"power2.in", stagger:0.1}}, {P("corriendo"):.2f}); tl.to("#j3, #j4", {{x:700, duration:1.4, ease:"power2.in", stagger:0.1}}, {P("corriendo"):.2f});')
FX.append(("silba", P("cincuenta")))
sigue(P("cincuenta") - 0.05, P("diez") - 0.05, 10, -380, 0.62, "power1.in")
expr("bb", P("diez") - 0.3, "nervioso", "preocupado")
J(f'tl.set("#bb_ojos", {{scaleY:0.1, svgOrigin:"0 -82"}}, {P("diez"):.2f});')
J(f'tl.to("#bubBr", {{rotation:-2520, svgOrigin:"0 0", duration:{P("explota") - P("diez"):.2f}, ease:"power1.in"}}, {P("diez"):.2f});')
sigue(P("diez") - 0.05, P("explota") + 0.02, 0, -180, 0.8, "power1.in")
te = P("explota") + 0.02
J(f'tl.set("#bubB", {{opacity:0}}, {te + 0.03:.2f}); tl.set("#boom", {{opacity:1}}, {te:.2f});')
J(f'tl.fromTo("#boom .trozo", {{x:0, y:0, rotation:0}}, {{x:(i) => Math.cos(i * 0.39) * 900, y:(i) => Math.sin(i * 0.39) * 700 - 200, rotation:(i) => i * 70, svgOrigin:"0 0", duration:0.5, ease:"power3.out", immediateRender:false}}, {te:.2f});')
J(f'tl.fromTo("#flashB", {{opacity:1}}, {{opacity:0.6, duration:0.12, immediateRender:false}}, {te:.2f});')
tfin = te + 0.14                                           # CORTE EN SECO
J(f'tl.set("#negroF", {{opacity:0}}, 0); tl.set("#negroF", {{opacity:1}}, {tfin:.2f});')
OVR.append('<div id="flashB"></div><div id="negroF"></div>')
FX.append(("explota", te)); FX.append(("final", tfin))

# ------------------------------------------------------------------ subtítulos habituales (arriba, palabra a palabra, recuadro azul en lo importante)
CLAVE = set(norm(w) for w in ["burbuja", "helicoptero", "mil", "cortan", "atan", "piernas", "despega", "cesped", "girar", "peonza", "congela", "piloto",
                               "silencio", "tijeras", "estomago", "cien", "frena", "menos", "cuarenta", "minuto", "gritando", "pajaros", "avioneta",
                               "enorme", "pequenas", "piso", "muro", "velocidad", "jugadores", "portero", "diez", "explota"])
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
#gancho{{position:absolute;left:0;right:0;top:1560px;text-align:center;z-index:20}}
#gancho .g1{{font:900 112px Inter;letter-spacing:-4px;color:#ffe08a;text-shadow:0 0 50px rgba(255,200,90,0.6), 0 8px 30px rgba(0,0,0,0.45)}}
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
#negroF{{position:absolute;inset:0;z-index:69;background:#000;pointer-events:none}}
#altim{{position:absolute;left:40px;top:500px;z-index:40;padding:10px 20px;border-radius:18px;background:rgba(10,20,40,0.55);backdrop-filter:blur(8px);border:2px solid rgba(255,255,255,0.5);color:#fff}}
#altim small{{display:block;font:800 18px Inter;letter-spacing:4px;color:#9fdcff}} #altim b{{font:900 46px Inter;font-variant-numeric:tabular-nums}}
#velo{{position:absolute;right:40px;top:500px;z-index:40;width:250px;padding:14px;border-radius:24px;background:rgba(10,20,40,0.6);border:2px solid rgba(255,255,255,0.5);color:#fff;text-align:center}}
#velo .esfera{{position:relative;width:200px;height:110px;margin:0 auto;border-radius:110px 110px 0 0;background:conic-gradient(from -90deg at 50% 100%, #2fd27a 0deg, #ffcf3a 90deg, #ff3b2f 180deg, transparent 180deg)}}
#velo .esfera::after{{content:"";position:absolute;left:22px;right:22px;top:22px;bottom:0;border-radius:90px 90px 0 0;background:#14203a}}
#velo .aguja2{{position:absolute;left:97px;bottom:0;width:6px;height:96px;background:#fff;border-radius:3px;transform-origin:50% 100%;transform:rotate(-90deg);z-index:2}}
#velo .centro{{position:absolute;left:88px;bottom:-12px;width:24px;height:24px;border-radius:50%;background:#fff;z-index:3}} #velo b{{display:block;margin-top:14px;font:900 46px Inter;font-variant-numeric:tabular-nums}}
#crono{{position:absolute;right:40px;top:760px;z-index:40;padding:10px 22px;border-radius:18px;background:#ff3b2f;color:#fff;text-align:center}} #crono small{{display:block;font:800 18px Inter;letter-spacing:4px}} #crono b{{font:900 54px Inter;font-variant-numeric:tabular-nums}}
#fuerzas{{position:absolute;left:0;right:0;top:0;bottom:0;z-index:35;pointer-events:none}}
#fuerzas .fl{{position:absolute;left:840px;width:120px;text-align:center;font:900 26px Inter;color:#fff;letter-spacing:2px}}
#fuerzas .fl i{{display:block;margin:0 auto;width:40px;background:currentColor}}
#fuerzas .arriba{{top:560px;height:330px;color:#7fe0ff}} #fuerzas .arriba i{{height:260px;clip-path:polygon(50% 0,100% 18%,70% 18%,70% 100%,30% 100%,30% 18%,0 18%)}}
#fuerzas .abajo{{top:1040px;height:430px;color:#ff5a4a}} #fuerzas .abajo i{{height:380px;width:60px;clip-path:polygon(30% 0,70% 0,70% 82%,100% 82%,50% 100%,0 82%,30% 82%)}}
#fuerzas .fl span{{display:block;margin-top:8px}}
#viento{{position:absolute;inset:0;z-index:34;pointer-events:none}} #viento i{{position:absolute;width:300px;height:6px;border-radius:3px;background:rgba(255,255,255,0.75)}}
.cmp{{position:absolute;left:330px;top:1180px;z-index:36;padding:16px;border-radius:30px;background:#ffffff;box-shadow:0 20px 50px rgba(0,0,0,0.35);text-align:center}}
.cmp svg{{display:block;width:380px;height:380px}} .cmp b{{display:block;margin-top:8px;font:900 34px Inter;color:#1d2433;letter-spacing:1px}}
#rebob{{position:absolute;left:0;right:0;top:880px;z-index:45;text-align:center;font:900 110px Inter;color:#fff;letter-spacing:6px;text-shadow:0 8px 30px rgba(0,0,0,0.5)}}
#rebob i{{display:inline-block;width:0;height:0;border-top:50px solid transparent;border-bottom:50px solid transparent;border-right:70px solid #fff;margin-right:-10px;vertical-align:middle}}
#flashB{{position:absolute;inset:0;z-index:58;background:#ffffff;opacity:0;pointer-events:none}}

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

#!/usr/bin/env python3
"""«¿Cómo funciona el váter de un avión?» (reutiliza piezas del vídeo del botón)
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
#  ¿CÓMO FUNCIONA EL VÁTER DE UN AVIÓN?  — escenas
# ======================================================================================================
def nubes(x0, y, n=4, seed=1, w=1000, h=260, s=1.0, op=0.92):
    r_ = random.Random(seed)
    return "".join(f'<g class="nube" transform="translate({x0 + r_.uniform(0, w):.0f},{y + r_.uniform(0, h):.0f}) scale({s * r_.uniform(0.7, 1.3):.2f})">' + "".join(f'<ellipse cx="{dx}" cy="{dy}" rx="{rx}" ry="{rx * 0.62:.0f}" fill="#ffffff" opacity="{op}"/>' for dx, dy, rx in ((-70, 6, 52), (0, -10, 74), (66, 4, 54), (22, 14, 60), (-30, 18, 50))) + '<ellipse cx="0" cy="30" rx="120" ry="16" fill="#cfe3f5" opacity="0.6"/></g>' for _ in range(n))
def arbol(x, y, s=1.0, c="#3f9a5a"):
    return (f'<rect x="{x - 9 * s:.0f}" y="{y - 120 * s:.0f}" width="{18 * s:.0f}" height="{120 * s:.0f}" fill="#6b4a2a"/><circle cx="{x}" cy="{y - 150 * s:.0f}" r="{70 * s:.0f}" fill="{c}"/>'
            f'<circle cx="{x - 40 * s:.0f}" cy="{y - 120 * s:.0f}" r="{48 * s:.0f}" fill="{c}"/><circle cx="{x + 42 * s:.0f}" cy="{y - 122 * s:.0f}" r="{50 * s:.0f}" fill="{c}"/><circle cx="{x - 20 * s:.0f}" cy="{y - 172 * s:.0f}" r="{30 * s:.0f}" fill="#ffffff" opacity="0.12"/>')
grad_lin("cieloAlto", ((0, "#1f5fbf", 1), (0.55, "#4f9be8", 1), (1, "#bfe3ff", 1)))
grad_lin("cieloOcaso", ((0, "#2a2a6e", 1), (0.5, "#a14f9a", 1), (1, "#ff9f6a", 1)))
grad_lin("piel_avion", ((0, "#ffffff", 1), (0.6, "#eef2f6", 1), (1, "#c3ccd6", 1)))
grad_lin("inox", ((0, "#f4f7fa", 1), (0.45, "#c9d1d9", 1), (1, "#8a95a1", 1)), 0, 0, 1, 0)
grad_lin("inoxV", ((0, "#f4f7fa", 1), (0.5, "#c9d1d9", 1), (1, "#7d8894", 1)))
grad_lin("cabina", ((0, "#fbf6ec", 1), (1, "#efe4cf", 1)))
grad_lin("bodega", ((0, "#d9ccb4", 1), (1, "#bfae92", 1)))
grad_lin("pared_lav", ((0, "#eef2f4", 1), (1, "#d5dde2", 1)), 0, 0, 1, 0)
grad_lin("suelo_lav", ((0, "#5b636d", 1), (1, "#3a4048", 1)))
grad_lin("hielo", ((0, "#e8fbff", 1), (0.5, "#8fd8ff", 1), (1, "#2f8fd8", 1)), 0, 0, 1, 1)
grad_lin("azulQ", ((0, "#6fd0ff", 1), (1, "#1f6fd8", 1)))
grad_lin("tierra", ((0, "#7cb86a", 1), (1, "#4f8a45", 1)))
grad_rad("brilloAzul", ((0, "#bff0ff", 0.85), (0.5, "#5fc8ff", 0.25), (1, "#5fc8ff", 0)))
grad_rad("brilloBlanco", ((0, "#ffffff", 0.95), (0.5, "#ffffff", 0.3), (1, "#ffffff", 0)))
YO = estilo(5, piel="#e0ac85", pelo="#2a1a12", ropa="#f2c14e", peinado="corto", barba=False, gafas=False, ojos="#4a3020")
PANT_YO = "#2a3550"

def caca(cid, x, y, s=1.0):
    """Mojón de dibujo (tres roscas marrones con brillo). El grupo interior #cid es el que se anima."""
    return (f'<g transform="translate({x:.0f},{y:.0f}) scale({s:.2f})"><g id="{cid}">'
            '<ellipse cx="0" cy="4" rx="30" ry="9" fill="#000" opacity="0.18"/>'
            '<ellipse cx="0" cy="-4" rx="28" ry="13" fill="#7a4a24"/><ellipse cx="1" cy="-17" rx="21" ry="11" fill="#8f5a2e"/>'
            '<ellipse cx="3" cy="-28" rx="13" ry="8" fill="#a46a38"/><path d="M3,-34 Q10,-46 2,-50 Q6,-40 -2,-35 Z" fill="#a46a38"/>'
            '<ellipse cx="-9" cy="-20" rx="7" ry="3" fill="#ffffff" opacity="0.35"/><ellipse cx="-12" cy="-7" rx="8" ry="3" fill="#ffffff" opacity="0.25"/></g></g>')
def estela(eid, x, y, largo=160, col="#ffffff", s=1.0):
    """Líneas de velocidad detrás de algo que va hacia la izquierda (nacen a su derecha)."""
    return f'<g transform="translate({x:.0f},{y:.0f}) scale({s:.2f})"><g id="{eid}" opacity="0">' + "".join(f'<path d="M{20 + i * 6},{dy} L{20 + largo - i * 25},{dy}" stroke="{col}" stroke-width="{5 - i}" stroke-linecap="round" opacity="{0.8 - i * 0.15:.2f}"/>' for i, dy in enumerate((-22, -8, 6, -34))) + '</g></g>'
def bloque_hielo(x, y, s=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})">'
            '<path d="M-80,0 L75,0 L98,42 L86,118 L42,150 L-24,146 L-82,108 L-102,48 Z" fill="url(#hielo)" stroke="#ffffff" stroke-width="5"/>'
            '<path d="M-80,0 L-30,56 L42,40 L75,0 M-30,56 L-24,146 M42,40 L86,118 M-30,56 L-102,48" stroke="#ffffff" stroke-width="3" opacity="0.55" fill="none"/>'
            '<path d="M-50,18 L-20,30" stroke="#ffffff" stroke-width="8" stroke-linecap="round" opacity="0.7"/>'
            '<path d="M-60,108 L-54,140 L-48,112 M10,146 L16,182 L24,146 M60,132 L66,160 L72,128" fill="#bff0ff" stroke="#ffffff" stroke-width="2"/></g>')
def destello(cx, cy, r, col="#ffffff", cls="chispa"):
    return f'<path class="{cls}" d="M{cx},{cy - r} Q{cx + r * 0.18},{cy - r * 0.18} {cx + r},{cy} Q{cx + r * 0.18},{cy + r * 0.18} {cx},{cy + r} Q{cx - r * 0.18},{cy + r * 0.18} {cx - r},{cy} Q{cx - r * 0.18},{cy - r * 0.18} {cx},{cy - r} Z" fill="{col}"/>'

# ------------------------------------------------------------------ EL AVIÓN (mismo modelo en todo el vídeo; morro a la derecha, cola a la izquierda)
FUS = "M430,830 L2700,830 C2880,830 3000,900 3025,1005 C3000,1110 2880,1180 2700,1180 L760,1180 C600,1180 440,1070 300,905 L300,870 C320,846 380,830 430,830 Z"
LAV_X, TANK = 2595, (600, 1098, 770, 1170)          # váter (delantero) y depósito (en la cola, bajo el suelo)
def avion(pid, corte=True, ocaso=False, tren=False):
    r_ = random.Random(11)
    s = [f'<g id="{pid}">']
    # ala del otro lado + motor (detrás del fuselaje)
    s.append('<path d="M1820,1060 L1460,1060 L1080,1290 L1180,1300 Z" fill="#c9d2dc"/><path d="M1180,1300 L1080,1290 L1060,1310 L1150,1316 Z" fill="#9aa6b6"/>'
             '<rect x="1420" y="1150" width="320" height="120" rx="58" fill="url(#inoxV)"/><ellipse cx="1740" cy="1210" rx="22" ry="58" fill="#3a3f48"/><ellipse cx="1736" cy="1210" rx="12" ry="44" fill="#1a1d22"/>'
             '<rect x="1500" y="1170" width="160" height="10" rx="5" fill="#ffffff" opacity="0.5"/>')
    # estabilizador vertical (cola) con la franja de la marca
    s.append('<path d="M640,832 L440,520 L330,520 L330,880 Z" fill="url(#piel_avion)"/><path d="M600,770 L470,560 L405,560 L470,700 Z" fill="#ff6a4d"/><path d="M560,706 L470,560 L440,560 L520,690 Z" fill="#ffb24d"/>'
             '<path d="M520,900 L230,860 L210,890 L500,930 Z" fill="#dfe5ec"/>')
    if corte:
        DEFS.append(f'<clipPath id="{pid}_clip"><path d="{FUS}"/></clipPath>')
        c = [f'<rect x="250" y="800" width="2800" height="290" fill="url(#cabina)"/>',
             '<rect x="250" y="836" width="2800" height="50" fill="#e1d7c3"/>' + "".join(f'<rect x="{x}" y="838" width="4" height="46" fill="#c9bea8"/>' for x in range(420, 2560, 160)),
             "".join(f'<ellipse cx="{x}" cy="930" rx="15" ry="21" fill="#9fd6ff" stroke="#d9cdb6" stroke-width="5"/>' for x in range(560, 2520, 95)),
             '<rect x="250" y="1080" width="2800" height="16" fill="#8a7a66"/>',
             '<rect x="250" y="1096" width="2800" height="100" fill="url(#bodega)"/>']
        # maletas en la bodega
        for x in range(820, 2500, 130):
            c.append(f'<rect x="{x + r_.randint(-10, 10)}" y="{1132 + r_.randint(-6, 6)}" width="{r_.randint(70, 100)}" height="{r_.randint(30, 40)}" rx="8" fill="{r_.choice(("#d94f6b", "#3f7ad8", "#2fa36b", "#f2c14e", "#8a5cd6", "#2a3550"))}" opacity="0.85"/>')
        # asientos de perfil + pasajeros (cabeza con cuello y pelo)
        for i, x in enumerate(range(800, 2480, 84)):
            c.append(f'<path d="M{x},{1078} L{x - 8},{960} Q{x - 6},{946} {x + 8},{948} L{x + 18},{1040} L{x + 58},{1040} Q{x + 66},{1046} {x + 60},{1062} L{x + 22},{1066} L{x + 22},{1078} Z" fill="#2f5fb3"/><rect x="{x - 6}" y="{950}" width="14" height="20" rx="4" fill="#ffffff" opacity="0.85"/>')
            if r_.random() < 0.82:
                e_ = estilo(200 + i)
                hx, hy = x + 26, 984 + r_.randint(-3, 3)
                c.append(f'<g class="pax"><path d="M{x + 8},{1042} L{x + 12},{1004} Q{x + 26},{994} {x + 42},{1004} L{x + 46},{1042} Z" fill="{e_["ropa"]}"/><rect x="{hx - 6}" y="{hy + 10}" width="12" height="14" fill="{oscurece(e_["piel"], 0.88)}"/>'
                         f'<circle cx="{hx}" cy="{hy}" r="17" fill="{e_["piel"]}"/><path d="M{hx - 18},{hy - 2} Q{hx - 4},{hy - 26} {hx + 14},{hy - 12} L{hx + 6},{hy - 6} Q{hx - 6},{hy - 12} {hx - 12},{hy + 6} Z" fill="{e_["pelo"]}"/>'
                         f'<circle cx="{hx + 9}" cy="{hy - 2}" r="2.6" fill="#222"/></g>')
        # el que come un bocadillo y la niña con la tableta (para el viaje bajo sus pies)
        c.append('<g id="bocata"><rect x="1716" y="1004" width="34" height="18" rx="8" fill="#e8b26a"/><rect x="1716" y="1010" width="34" height="5" fill="#5fae4a"/></g>'
                 '<rect x="1300" y="1000" width="26" height="20" rx="3" fill="#1a1d22"/><rect x="1302" y="1002" width="22" height="16" fill="#7fe0ff" opacity="0.9"/>')
        # aseo delantero con su váter
        c.append(f'<rect x="{LAV_X - 70}" y="844" width="150" height="236" fill="url(#pared_lav)"/><rect x="{LAV_X - 70}" y="844" width="6" height="236" fill="#b7c1c9"/><rect x="{LAV_X + 74}" y="844" width="6" height="236" fill="#b7c1c9"/>'
                 f'<rect x="{LAV_X - 30}" y="870" width="60" height="22" rx="4" fill="#2a3550"/><text x="{LAV_X}" y="887" text-anchor="middle" font-family="Inter" font-weight="900" font-size="16" fill="#ffffff">WC</text>'
                 f'<path d="M{LAV_X - 34},1020 L{LAV_X + 30},1020 Q{LAV_X + 34},1050 {LAV_X + 10},1060 L{LAV_X + 4},1080 L{LAV_X - 22},1080 L{LAV_X - 24},1060 Q{LAV_X - 38},1048 {LAV_X - 34},1020 Z" fill="url(#inox)"/>'
                 f'<rect x="{LAV_X - 44}" y="1012" width="88" height="10" rx="5" fill="#2a2e35"/><rect x="{LAV_X - 50}" y="960" width="14" height="56" rx="5" fill="#2a2e35"/>')
        # cabina de pilotos
        c.append('<rect x="2700" y="844" width="330" height="236" fill="#2a3550" opacity="0.9"/><rect x="2760" y="980" width="160" height="40" rx="6" fill="#1a1d22"/>' + "".join(f'<circle cx="{2780 + i * 26}" cy="1000" r="5" fill="{col}"/>' for i, col in enumerate(("#7CFFB0", "#ffcf4d", "#ff6a4d", "#7fe0ff", "#7CFFB0", "#ffcf4d"))))
        # TUBERÍA: váter → bajo el suelo → depósito en la cola → respiradero al exterior
        tubo = f"M{LAV_X - 6},1080 L{LAV_X - 6},1124 L{TANK[2]},1124"
        c.append(f'<path d="{tubo}" stroke="#6f7884" stroke-width="20" fill="none" stroke-linejoin="round"/><path d="{tubo}" stroke="#aeb7c2" stroke-width="12" fill="none" stroke-linejoin="round"/>'
                 f'<path d="{tubo}" stroke="#ffffff" stroke-width="3" fill="none" opacity="0.5" transform="translate(0,-3)"/>'
                 f'<path id="{pid}_flujo" d="{tubo}" stroke="#7fe0ff" stroke-width="5" fill="none" stroke-dasharray="26 34" opacity="0"/>')
        x0, y0, x1, y1 = TANK
        DEFS.append(f'<clipPath id="{pid}_tq"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="22"/></clipPath>')
        c.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="22" fill="#f4f7fa" stroke="#7d8894" stroke-width="5"/>'
                 f'<g clip-path="url(#{pid}_tq)"><rect id="{pid}_nivel" x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#8a5a2e" transform="translate(0,{(y1 - y0) * 0.85:.0f})"/></g>'
                 f'<rect x="{x0 + 10}" y="{y0 + 8}" width="{x1 - x0 - 20}" height="8" rx="4" fill="#ffffff" opacity="0.6"/>'
                 f'<path d="M{x0 + 30},{y0} L{x0 + 30},{y0 - 10} L{x0 - 30},{y0 - 10} L{x0 - 30},1182" stroke="#6f7884" stroke-width="9" fill="none"/>'
                 f'<path id="{pid}_resp" d="M{x0 + 30},{y0} L{x0 + 30},{y0 - 10} L{x0 - 30},{y0 - 10} L{x0 - 30},1190" stroke="#7fe0ff" stroke-width="4" fill="none" stroke-dasharray="14 18" opacity="0"/>')
        s.append(f'<path d="{FUS}" fill="#ffffff"/><g clip-path="url(#{pid}_clip)">' + "".join(c) + '</g>')
        s.append(f'<path d="{FUS}" fill="none" stroke="#ffffff" stroke-width="12"/><path d="{FUS}" fill="none" stroke="#9aa6b6" stroke-width="3"/>')
    else:
        s.append(f'<path d="{FUS}" fill="url(#piel_avion)"/>'
                 + "".join(f'<ellipse cx="{x}" cy="935" rx="14" ry="20" fill="#2a3a55"/><ellipse cx="{x - 4}" cy="929" rx="5" ry="7" fill="#ffffff" opacity="0.35"/>' for x in range(560, 2620, 64))
                 + '<path d="M420,1060 L2900,1060 L2930,1080 L470,1090 Z" fill="#ff6a4d" opacity="0.9"/><path d="M450,1092 L2880,1084 L2860,1100 L520,1110 Z" fill="#ffb24d" opacity="0.9"/>'
                 + '<rect x="2560" y="880" width="56" height="150" rx="12" fill="none" stroke="#9aa6b6" stroke-width="4"/><rect x="740" y="880" width="50" height="140" rx="12" fill="none" stroke="#9aa6b6" stroke-width="4"/>'
                 + '<path d="M2905,905 L2960,905 L2990,940 L2920,945 Z" fill="#1d2a40"/><path d="M2850,905 L2895,905 L2905,945 L2852,945 Z" fill="#1d2a40"/>'
                 + f'<path d="{FUS}" fill="none" stroke="#9aa6b6" stroke-width="3"/>'
                 # panel de servicio de aguas residuales (bajo la cola)
                 + f'<g id="{pid}_panel"><rect x="690" y="1150" width="70" height="26" rx="5" fill="#d5dde2" stroke="#7d8894" stroke-width="3"/><circle cx="725" cy="1163" r="8" fill="#5b636d"/>'
                 + f'<rect id="{pid}_palanca" x="722" y="1150" width="6" height="22" rx="3" fill="#ffcf4d"/></g>')
    if tren:
        s.append("".join(f'<rect x="{x - 8}" y="1170" width="16" height="130" fill="#9aa3ad"/><circle cx="{x - 22}" cy="1310" r="34" fill="#1a1d22"/><circle cx="{x + 22}" cy="1310" r="34" fill="#1a1d22"/><circle cx="{x - 22}" cy="1310" r="13" fill="#9aa3ad"/><circle cx="{x + 22}" cy="1310" r="13" fill="#9aa3ad"/>' for x in (1620, 2720)))
    # ala cercana (solo por debajo)
    s.append('<path d="M1700,1150 L1500,1150 L1260,1330 L1330,1338 Z" fill="#dfe5ec"/><path d="M1330,1338 L1260,1330 L1250,1352 L1320,1356 Z" fill="#ff6a4d"/>')
    s.append('</g>')
    return "".join(s)

def relleno(eid, abajo, izq=None, der=None):
    for i, s_ in enumerate(ESC):
        if f'id="{eid}"' in s_:
            extra = f'<rect x="-1500" y="1915" width="4600" height="1500" fill="{abajo}"/>'
            if izq: extra += f'<rect x="-1500" y="-1500" width="1502" height="4500" fill="{izq}"/>'
            if der: extra += f'<rect x="1078" y="-1500" width="1500" height="4500" fill="{der}"/>'
            ESC[i] = s_.replace("</svg></div></div>", extra + "</svg></div></div>")
# ================================================================== 1) GANCHO: corte del avión; tu caca sale disparada por el tubo hasta la cola… a 10.000 m
f1 = 0.0
cielo1 = (f'<rect x="-3000" y="-3500" width="9500" height="6000" fill="url(#cieloAlto)"/>'
          f'<rect x="-3000" y="2500" width="9500" height="3000" fill="url(#tierra)"/>'
          + "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}" opacity="0.8"/>' for x, y, w, h, c in ((-800, 2560, 900, 300, "#9ccf6a"), (300, 2620, 700, 260, "#d9c97a"), (1200, 2540, 800, 380, "#8ac060"), (2200, 2600, 900, 300, "#c9b86a"), (3300, 2560, 800, 340, "#9ccf6a"), (4300, 2620, 700, 260, "#d9c97a")))
          + '<path d="M-1000,2900 C200,2700 900,3100 1800,2850 C2600,2650 3400,3000 4600,2800" stroke="#5fb2ec" stroke-width="60" fill="none" opacity="0.9"/>'
          + nubes(-1500, 1500, 9, 4, 6000, 700, 3.2, 0.9) + nubes(-1500, -900, 6, 8, 6000, 900, 2.6, 0.85))
escena("e1", cielo1 + avion("av1") + caca("k1", LAV_X - 6, 1050, 1.5) + estela("st1", LAV_X - 6, 1050, 140, "#ffffff"), 3200)
mostrar("e1", 0, F(2))
# la caca baja por el váter y sale disparada por el tubo; la cámara la persigue
tb, tv = 0.0, 0.35
t_tubo = 2.3
J(f'tl.fromTo("#k1", {{x:0, y:0}}, {{y:74, duration:{tv}, ease:"power2.in", immediateRender:false}}, {tb:.2f});')
J(f'tl.to("#k1", {{x:{TANK[2] - LAV_X + 6 - 20}, duration:{t_tubo - tv:.2f}, ease:"power2.in"}}, {tv:.2f});')
J(f'tl.to("#k1", {{y:96, x:{TANK[2] - LAV_X + 6 - 90}, scale:0.6, opacity:0, duration:0.2, ease:"power2.in"}}, {t_tubo:.2f});')
J(f'tl.set("#st1", {{opacity:1}}, {tv:.2f}); tl.fromTo("#st1", {{x:0, y:74}}, {{x:{TANK[2] - LAV_X + 6 - 20}, y:74, duration:{t_tubo - tv:.2f}, ease:"power2.in", immediateRender:false}}, {tv:.2f}); tl.set("#st1", {{opacity:0}}, {t_tubo:.2f});')
J(f'tl.set("#av1_flujo", {{opacity:0.9}}, 0); tl.fromTo("#av1_flujo", {{strokeDashoffset:0}}, {{strokeDashoffset:-900, duration:{t_tubo + 0.2:.2f}, ease:"none", immediateRender:false}}, 0); tl.to("#av1_flujo", {{opacity:0, duration:0.3}}, {t_tubo + 0.1:.2f});')
J(f'tl.fromTo("#av1_nivel", {{y:{(TANK[3] - TANK[1]) * 0.85:.0f}}}, {{y:{(TANK[3] - TANK[1]) * 0.7:.0f}, duration:0.35, ease:"back.out(2)", immediateRender:false}}, {t_tubo + 0.05:.2f});')
c0 = enfoca(LAV_X - 6, 1060, 2.6)
J(f'tl.fromTo("#e1-cam", {{x:{c0[0]}, y:{c0[1]}, scale:2.6}}, {{x:{enfoca(LAV_X - 6, 1110, 2.6)[0]}, y:{enfoca(LAV_X - 6, 1110, 2.6)[1]}, duration:{tv}, ease:"power2.in", immediateRender:false}}, 0);')
J(f'tl.to("#e1-cam", {{x:{enfoca(TANK[2] - 10, 1110, 2.6)[0]}, duration:{t_tubo - tv:.2f}, ease:"power2.in"}}, {tv:.2f});')
J(f'tl.fromTo("#e1-cam", {{rotation:0}}, {{rotation:0.6, duration:0.06, yoyo:true, repeat:13, immediateRender:false}}, {tv:.2f});')
cz = enfoca(1660, 1180, 0.34)
J(f'tl.to("#e1-cam", {{x:{cz[0]}, y:{cz[1]}, scale:0.34, rotation:0, duration:1.6, ease:"power3.inOut"}}, {t_tubo + 0.35:.2f});')
J(f'tl.to("#e1-cam", {{x:{cz[0] - 30}, duration:{F(2) - t_tubo - 1.95:.2f}, ease:"none"}}, {t_tubo + 1.95:.2f});')
J(f'tl.fromTo("#e1 .nube", {{x:0}}, {{x:-900, duration:{F(2):.2f}, ease:"none", immediateRender:false}}, 0);')
OVR.append('<div id="gancho"><div class="g1">10.000 METROS</div><div class="g2">Y TIRAS DE LA CADENA</div></div>')
J(f'tl.fromTo("#gancho", {{opacity:1, scale:1.0, y:330}}, {{scale:1, y:330, duration:0.35, ease:"back.out(2)"}}, 0); tl.to("#gancho", {{y:0, duration:1.6, ease:"power3.inOut"}}, {t_tubo + 0.35:.2f}); tl.fromTo("#gancho .g1", {{scale:1}}, {{scale:1.08, duration:0.25, yoyo:true, repeat:1, immediateRender:false}}, {P("diez") - 0.1:.2f}); tl.to("#gancho", {{opacity:0, duration:0.2}}, {F(2) - 0.15:.2f});')
FX.append(("aspira", 0.05)); FX.append(("chof", t_tubo + 0.05)); FX.append(("whoosh", t_tubo + 0.4))

# ================================================================== 2) ASIENTO 32 · LLEVAS UNA HORA AGUANTANDO · 3) SALTAS POR ENCIMA DE DOS SEÑORES DORMIDOS
def piernas_sentado(x, ytab, k, pant, zap="#2a2a2a", cid=""):
    """Muslos (en escorzo) y espinillas de alguien sentado, vistos de frente."""
    s = []
    for L in (-1, 1):
        kx = x + L * 34 * k
        s.append(f'<path d="M{kx - 26 * k:.0f},{ytab + 20 * k:.0f} L{kx + 26 * k:.0f},{ytab + 20 * k:.0f} L{kx + 24 * k:.0f},{ytab + 70 * k:.0f} L{kx - 24 * k:.0f},{ytab + 70 * k:.0f} Z" fill="{pant}"/>'
                 f'<ellipse cx="{kx:.0f}" cy="{ytab + 70 * k:.0f}" rx="{25 * k:.0f}" ry="{12 * k:.0f}" fill="{oscurece(pant, 0.85)}"/>'
                 f'<path d="M{kx - 21 * k:.0f},{ytab + 72 * k:.0f} L{kx + 21 * k:.0f},{ytab + 72 * k:.0f} L{kx + 18 * k:.0f},{ytab + 190 * k:.0f} L{kx - 18 * k:.0f},{ytab + 190 * k:.0f} Z" fill="{oscurece(pant, 0.92)}"/>'
                 f'<ellipse cx="{kx + L * 6 * k:.0f}" cy="{ytab + 196 * k:.0f}" rx="{30 * k:.0f}" ry="{13 * k:.0f}" fill="{zap}"/>')
    return f'<g class="piernas" id="{cid}">' + "".join(s) + '</g>'
def asiento(x, ytop, ybase, w=230, col="#2f5fb3"):
    return (f'<rect x="{x - w / 2:.0f}" y="{ytop}" width="{w}" height="{ybase - ytop}" rx="34" fill="{col}"/><rect x="{x - w / 2:.0f}" y="{ytop}" width="{w}" height="{ybase - ytop}" rx="34" fill="url(#brilloRopa)"/>'
            f'<rect x="{x - w * 0.38:.0f}" y="{ytop + 14}" width="{w * 0.76:.0f}" height="70" rx="16" fill="#f6f2ea"/>')
def reposabrazos(x, y):
    return f'<rect x="{x - 16}" y="{y}" width="32" height="150" rx="12" fill="#3a3f48"/><rect x="{x - 22}" y="{y - 8}" width="44" height="24" rx="10" fill="#4a505a"/>'
YTAB = 1290
fila = ['<rect width="1300" height="1920" fill="#e9e2d4"/>',
        # ventanilla ovalada con nubes que pasan (lado izquierdo)
        '<rect x="0" y="560" width="150" height="1360" fill="#ddd3c0"/><ellipse cx="80" cy="900" rx="62" ry="96" fill="#cfc4ae"/>',
        '<clipPath id="vent2"><ellipse cx="80" cy="900" rx="48" ry="80"/></clipPath><g clip-path="url(#vent2)"><rect x="0" y="800" width="200" height="200" fill="url(#cieloAlto)"/><g id="nubV">' + nubes(-200, 860, 4, 9, 600, 60, 0.6) + '</g></g>',
        # maleteros con el número de fila integrado
        '<path d="M0,420 L1300,420 L1300,620 Q650,660 0,620 Z" fill="#f4efe6"/><path d="M0,612 Q650,652 1300,612 L1300,640 Q650,680 0,640 Z" fill="#d9cfbc"/>'
        + "".join(f'<rect x="{x}" y="440" width="6" height="170" fill="#ddd3c0"/>' for x in (420, 860)) +
        '<rect x="180" y="650" width="200" height="56" rx="10" fill="#2a3550"/><text x="280" y="690" text-anchor="middle" font-family="Inter" font-weight="900" font-size="34" fill="#ffffff">32 · A B C</text>'
        + "".join(f'<circle cx="{x}" cy="680" r="12" fill="#fff6d8"/><circle cx="{x}" cy="680" r="30" fill="url(#brilloOro)" opacity="0.6"/>' for x in (520, 640, 760)),
        # pasillo a la derecha con filas que se alejan
        '<polygon points="1000,1920 1300,1920 1300,700 1120,760" fill="#c9bfae"/>' + "".join(f'<rect x="{1150 + i * 26}" y="{780 + i * 10}" width="{60 - i * 6}" height="{120 - i * 14}" rx="10" fill="#2f5fb3" opacity="{0.9 - i * 0.12:.2f}"/>' for i in range(4)),
        asiento(300, 800, 1330), asiento(540, 800, 1330), asiento(780, 800, 1330)]
yo_c, yo_b = sentado("yo", 300, YTAB, 300, "#fff1d6", lado_mano=-1, e=YO, expr0="nervioso")
d1_c, d1_b = sentado("d1", 540, YTAB, 300, "#fff1d6", e=estilo(61, ropa="#3f7ad8", peinado="calvo", pelo="#6b4a3a", barba=True), expr0="neutral")
d2_c, d2_b = sentado("d2", 780, YTAB, 300, "#fff1d6", e=estilo(62, ropa="#2fa36b", peinado="corto", pelo="#8e8e8e", gafas=True), expr0="neutral")
fila += [f'<g id="yoSent">{yo_c}</g>', d1_c, d2_c,
         reposabrazos(420, 1280), reposabrazos(660, 1280),
         '<rect x="0" y="1330" width="1300" height="40" fill="#24467f"/>',
         f'<g id="yoPiernas">{piernas_sentado(300, YTAB + 40, 1.0, PANT_YO)}</g>', piernas_sentado(540, YTAB + 40, 1.0, "#3a3f48"), piernas_sentado(780, YTAB + 40, 1.0, "#5a4632"),
         f'<g id="yoBraz">{yo_b}</g>', d1_b, d2_b,
         # burbujas de dormir en la nariz de los señores
         '<circle id="bur1" cx="566" cy="1055" r="14" fill="#cfefff" opacity="0.75" stroke="#ffffff" stroke-width="2"/><circle id="bur2" cx="806" cy="1055" r="12" fill="#cfefff" opacity="0.75" stroke="#ffffff" stroke-width="2"/>',
         # gotas de sudor del protagonista
         '<g id="sudor"><path d="M346,970 q8,14 0,20 q-8,-6 0,-20 Z" fill="#8fd8ff"/><path d="M256,990 q7,12 0,17 q-7,-5 0,-17 Z" fill="#8fd8ff"/></g>',
         # el protagonista de pie (para saltar por encima)
         f'<g id="yoPie" opacity="0">{persona(300, 1620, 520, pid="yop", e=YO, expr0="nervioso")}</g>']
escena("e2", "".join(fila), 1300)
f2, f3, f4 = F(2), F(3), F(4)
mostrar("e2", f2, f4)
camara("e2", f2, f3, enfoca(420, 1060, 1.35), enfoca(380, 1080, 1.5), "sine.inOut")
for pid in ("d1", "d2"):
    hx, hy, r = CARAS[pid]
    J(f'tl.set("#{pid}_ojos", {{scaleY:0.08, svgOrigin:"{hx:.0f} {hy - 0.1 * r:.0f}"}}, {f2:.2f});')
    expr(pid, f2, "neutral", "neutral", abierta=True)
J(f'tl.fromTo("#d1 .cab", {{rotation:-10}}, {{rotation:-16, transformOrigin:"50% 100%", duration:1.4, yoyo:true, repeat:4, ease:"sine.inOut", immediateRender:false}}, {f2:.2f});')
J(f'tl.fromTo("#d2 .cab", {{rotation:12}}, {{rotation:18, transformOrigin:"50% 100%", duration:1.6, yoyo:true, repeat:3, ease:"sine.inOut", immediateRender:false}}, {f2:.2f});')
J(f'tl.fromTo("#bur1", {{scale:0.3}}, {{scale:1.2, svgOrigin:"556 1060", duration:1.1, yoyo:true, repeat:5, ease:"sine.inOut", immediateRender:false}}, {f2:.2f});')
J(f'tl.fromTo("#bur2", {{scale:1.1}}, {{scale:0.3, svgOrigin:"796 1060", duration:1.3, yoyo:true, repeat:4, ease:"sine.inOut", immediateRender:false}}, {f2:.2f});')
expr("yo", f2, "nervioso", "preocupado")
J(f'tl.fromTo("#yoPiernas", {{y:0}}, {{y:-7, duration:0.12, yoyo:true, repeat:{int((f3 - f2) / 0.12)}, ease:"sine.inOut", immediateRender:false}}, {f2:.2f});')
J(f'tl.fromTo("#yoSent .cuerpo", {{x:-3}}, {{x:3, duration:0.18, yoyo:true, repeat:{int((f3 - f2) / 0.18)}, ease:"sine.inOut", immediateRender:false}}, {f2:.2f});')
J(f'tl.fromTo("#sudor path", {{y:0, opacity:0}}, {{y:40, opacity:1, duration:0.9, stagger:0.4, repeat:3, ease:"power1.in", immediateRender:false}}, {f2 + 0.3:.2f});')
J(f'tl.fromTo("#nubV", {{x:0}}, {{x:-420, duration:{f4 - f2:.2f}, ease:"none", immediateRender:false}}, {f2:.2f});')
J(f'tl.to("#yo .cab", {{rotation:-14, transformOrigin:"50% 100%", duration:0.25, yoyo:true, repeat:1}}, {P("hora") - 0.2:.2f});')
# 3) de pie y salta por encima de los dos dormidos
J(f'tl.set("#yoSent, #yoPiernas, #yoBraz, #sudor", {{opacity:0}}, {f3:.2f}); tl.set("#yoPie", {{opacity:1}}, {f3:.2f});')
J(f'tl.fromTo("#yoPie", {{x:0, y:40}}, {{y:0, duration:0.2, ease:"back.out(2)", immediateRender:false}}, {f3:.2f});')
for i, (dx, t) in enumerate(((240, f3 + 0.5), (480, f3 + 1.15), (760, f3 + 1.8))):
    J(f'tl.to("#yoPie", {{x:{dx}, duration:0.55, ease:"power1.inOut"}}, {t:.2f}); tl.to("#yoPie", {{y:-170, duration:0.27, ease:"power2.out", yoyo:true, repeat:1}}, {t:.2f});')
    J(f'tl.to("#yoPie", {{rotation:{(-8 if i % 2 else 8)}, transformOrigin:"50% 100%", duration:0.27, yoyo:true, repeat:1}}, {t:.2f});')
J(f'tl.to("#yop .brazo", {{rotation:-140, svgOrigin:"{300 + 34 * 520 / 300:.0f} {1620 - 228 * 520 / 300:.0f}", duration:0.3, yoyo:true, repeat:5}}, {f3 + 0.5:.2f});')
camara("e2", f3, f4, enfoca(540, 960, 1.0), enfoca(760, 1000, 1.05), "power1.inOut")
FX.append(("boing", f3 + 0.5)); FX.append(("boing", f3 + 1.15)); FX.append(("boing", f3 + 1.8))

# ================================================================== 4) HAY COLA · SE ENCIENDE LA LUZ DE LOS CINTURONES (pasillo hacia el aseo)
pas = ['<rect width="1080" height="1920" fill="#e9e2d4"/>',
       '<polygon points="0,0 1080,0 760,700 320,700" fill="#f4efe6"/><polygon points="0,0 320,700 320,1340 0,1920" fill="#ddd3c0"/><polygon points="1080,0 760,700 760,1340 1080,1920" fill="#ddd3c0"/>',
       '<polygon points="320,1340 760,1340 1080,1920 0,1920" fill="#8a5c4a"/>' + "".join(f'<path d="M{540 + (x - 540) * 0.4:.0f},1340 L{x},1920" stroke="#7a4e3e" stroke-width="3"/>' for x in range(0, 1081, 120)),
       # asientos a los lados en perspectiva
       "".join(f'<rect x="{320 - 330 * (1 - t):.0f}" y="{700 + 640 * (1 - t) * 0.3:.0f}" width="{40 + 230 * (1 - t):.0f}" height="{240 + 380 * (1 - t):.0f}" rx="{10 + 20 * (1 - t):.0f}" fill="#2f5fb3" opacity="0.95"/>'
               f'<rect x="{760 + 330 * (1 - t) - (40 + 230 * (1 - t)):.0f}" y="{700 + 640 * (1 - t) * 0.3:.0f}" width="{40 + 230 * (1 - t):.0f}" height="{240 + 380 * (1 - t):.0f}" rx="{10 + 20 * (1 - t):.0f}" fill="#2f5fb3" opacity="0.95"/>' for t in (0.9, 0.7, 0.45)),
       # puerta del aseo al fondo con el indicador OCUPADO integrado
       '<rect x="380" y="760" width="320" height="580" rx="8" fill="#dfe8ee" stroke="#b7c1c9" stroke-width="8"/><rect x="430" y="820" width="220" height="70" rx="8" fill="#2a3550"/>'
       '<text x="540" y="868" text-anchor="middle" font-family="Inter" font-weight="900" font-size="34" fill="#ffffff">WC</text>'
       '<rect x="470" y="1010" width="140" height="44" rx="8" fill="#1a1d22"/><text id="ocup4" x="540" y="1041" text-anchor="middle" font-family="Inter" font-weight="900" font-size="24" fill="#ff5a4a">OCUPADO</text>'
       '<rect x="640" y="1080" width="16" height="70" rx="6" fill="#9aa3ad"/>',
       # panel de señales del techo (cinturón)
       '<rect x="380" y="560" width="320" height="110" rx="20" fill="#d9cfbc"/><rect x="400" y="576" width="130" height="78" rx="14" fill="#3a3f48"/><rect x="550" y="576" width="130" height="78" rx="14" fill="#3a3f48"/>'
       '<g id="cint4" opacity="0.25"><rect x="400" y="576" width="130" height="78" rx="14" fill="#ffb84d"/><path d="M432,630 L498,630 M440,614 Q465,594 490,614" stroke="#3a2a10" stroke-width="7" fill="none" stroke-linecap="round"/><rect x="456" y="622" width="18" height="16" rx="3" fill="#3a2a10"/></g>'
       '<circle id="halo4" cx="465" cy="615" r="160" fill="url(#brilloOro)" opacity="0"/>'
       '<path d="M590,600 L640,640 M640,600 L590,640" stroke="#ff8a7a" stroke-width="7" opacity="0.5"/>']
cola = [(540, 1380, 300, 71), (510, 1470, 360, 72), (580, 1590, 430, 73)]
for i, (x, s_, h, sd) in enumerate(cola):
    pas.append(f'<g class="col4">{persona(x, s_, h, pid=f"c4_{i}", espalda=True, e=estilo(sd))}</g>')
pas.append(f'<g id="yo4">{persona(520, 1800, 560, pid="yo4p", espalda=True, e=YO)}</g>')
escena("e4", "".join(pas))
mostrar("e4", f4, F(5))
camara("e4", f4, F(5), enfoca(540, 1150, 1.0), enfoca(540, 1110, 1.12), "sine.inOut")
J(f'tl.fromTo("#yo4", {{x:-12, rotation:-2}}, {{x:12, rotation:2, transformOrigin:"50% 100%", duration:0.16, yoyo:true, repeat:{int((F(5) - f4) / 0.16)}, ease:"sine.inOut", immediateRender:false}}, {f4:.2f});')
J(f'tl.to("#cint4", {{opacity:1, duration:0.05}}, {P("luz") - 0.05:.2f}); tl.fromTo("#halo4", {{opacity:0}}, {{opacity:0.9, duration:0.1, yoyo:true, repeat:5, immediateRender:false}}, {P("luz") - 0.05:.2f});')
J(f'tl.to(".col4 .cabeza", {{y:-6, duration:0.2, ease:"back.out(3)"}}, {P("luz") + 0.1:.2f});')
J(f'tl.fromTo("#ocup4", {{opacity:1}}, {{opacity:0.35, duration:0.3, yoyo:true, repeat:5, immediateRender:false}}, {f4:.2f});')
FX.append(("ding", P("luz") - 0.05))

# ================================================================== 5-11) EL ASEO: tamaño armario · pestillo · turbulencias · botón · trampilla · rugido · limpio
def vater_frente(cx, ytaza, s=1.0):
    """Váter de avión de acero visto de frente: respaldo, asiento negro, tapa levantada, taza y pie."""
    k = s
    return (f'<rect x="{cx - 110 * k:.0f}" y="{ytaza - 230 * k:.0f}" width="{220 * k:.0f}" height="{190 * k:.0f}" rx="{22 * k:.0f}" fill="url(#inoxV)"/>'
            f'<rect x="{cx - 92 * k:.0f}" y="{ytaza - 214 * k:.0f}" width="{184 * k:.0f}" height="{150 * k:.0f}" rx="{30 * k:.0f}" fill="#2a2e35"/>'
            f'<path d="M{cx - 128 * k:.0f},{ytaza:.0f} C{cx - 128 * k:.0f},{ytaza + 120 * k:.0f} {cx - 60 * k:.0f},{ytaza + 160 * k:.0f} {cx - 50 * k:.0f},{ytaza + 230 * k:.0f} L{cx + 50 * k:.0f},{ytaza + 230 * k:.0f} C{cx + 60 * k:.0f},{ytaza + 160 * k:.0f} {cx + 128 * k:.0f},{ytaza + 120 * k:.0f} {cx + 128 * k:.0f},{ytaza:.0f} Z" fill="url(#inox)"/>'
            f'<ellipse cx="{cx}" cy="{ytaza:.0f}" rx="{130 * k:.0f}" ry="{36 * k:.0f}" fill="#1f2328"/><ellipse cx="{cx}" cy="{ytaza:.0f}" rx="{92 * k:.0f}" ry="{20 * k:.0f}" fill="#8a95a1"/>'
            f'<ellipse cx="{cx}" cy="{ytaza + 4 * k:.0f}" rx="{60 * k:.0f}" ry="{11 * k:.0f}" fill="#5b636d"/>'
            f'<rect x="{cx - 70 * k:.0f}" y="{ytaza + 230 * k:.0f}" width="{140 * k:.0f}" height="{20 * k:.0f}" rx="{8 * k:.0f}" fill="#7d8894"/>')
lav = ['<rect width="1080" height="1920" fill="url(#pared_lav)"/>',
       "".join(f'<rect x="{x}" y="0" width="3" height="1560" fill="#c7d0d6"/>' for x in (300, 780)),
       '<rect x="0" y="470" width="1080" height="70" fill="#cfd8de"/><rect x="380" y="490" width="320" height="26" rx="13" fill="#fff6d8"/><ellipse id="lamp5" cx="540" cy="503" rx="300" ry="90" fill="url(#brilloOro)" opacity="0.4"/>',
       # espejo con reflejo, señal de no fumar y rejilla
       '<rect x="330" y="600" width="420" height="300" rx="16" fill="#b9d7e6" stroke="#9aa6b6" stroke-width="10"/><path d="M380,880 L520,620 M440,880 L580,620" stroke="#ffffff" stroke-width="18" opacity="0.35"/>',
       '<circle cx="880" cy="640" r="40" fill="#ffffff" stroke="#d8261a" stroke-width="8"/><rect x="852" y="634" width="56" height="12" rx="3" fill="#3a3f48"/><path d="M852,668 L908,612" stroke="#d8261a" stroke-width="8"/>',
       '<rect x="150" y="610" width="110" height="70" rx="10" fill="#c7d0d6"/>' + "".join(f'<rect x="164" y="{622 + i * 12}" width="82" height="5" rx="2" fill="#9aa6b6"/>' for i in range(4)),
       # lavabo a la derecha con grifo y jabón
       '<rect x="760" y="1030" width="320" height="70" rx="10" fill="#f4f7fa" stroke="#c7d0d6" stroke-width="4"/><ellipse cx="900" cy="1046" rx="80" ry="16" fill="#c9d1d9"/>'
       '<path d="M900,990 L900,960 L940,960" stroke="#9aa3ad" stroke-width="12" fill="none" stroke-linecap="round"/>'
       '<g id="jabon"><rect x="990" y="960" width="44" height="72" rx="10" fill="#7fd0ff"/><rect x="1004" y="944" width="16" height="18" fill="#3a3f48"/></g>',
       # papel higiénico y papelera con trampilla
       '<rect x="180" y="1140" width="90" height="16" rx="6" fill="#9aa3ad"/><circle cx="225" cy="1186" r="40" fill="#ffffff" stroke="#ddd" stroke-width="3"/><circle cx="225" cy="1186" r="12" fill="#c9d1d9"/>'
       '<path id="papel5" d="M200,1214 L200,1260 L250,1260 L250,1214" fill="#ffffff"/>',
       '<rect x="150" y="1360" width="160" height="110" rx="8" fill="#c7d0d6"/><rect x="170" y="1380" width="120" height="30" rx="6" fill="#9aa6b6"/>',
       # pulsador de la cisterna integrado en una placa
       '<rect x="690" y="1140" width="110" height="110" rx="14" fill="#c9d1d9" stroke="#9aa6b6" stroke-width="5"/><circle id="puls5" cx="745" cy="1185" r="32" fill="#e9eef2" stroke="#7d8894" stroke-width="5"/>'
       '<circle id="pulsLuz" cx="745" cy="1185" r="70" fill="url(#brilloAzul)" opacity="0"/><text x="745" y="1236" text-anchor="middle" font-family="Inter" font-weight="900" font-size="15" fill="#5b636d" letter-spacing="1">DESCARGA</text>',
       '<rect x="0" y="1540" width="1080" height="380" fill="url(#suelo_lav)"/>' + "".join(f'<circle cx="{x}" cy="{y}" r="4" fill="#6f7884"/>' for x in range(30, 1080, 60) for y in range(1580, 1920, 60)),
       vater_frente(540, 1330, 1.0)]
paredI = '<g id="parI"><polygon points="-400,0 150,0 150,1560 -400,1920" fill="#c7d0d6"/><polygon points="150,0 170,0 170,1550 150,1560" fill="#aeb8c0"/><rect x="60" y="900" width="18" height="320" rx="9" fill="#9aa3ad"/></g>'
paredD = '<g id="parD"><polygon points="1480,0 930,0 930,1560 1480,1920" fill="#c7d0d6"/><polygon points="930,0 910,0 910,1550 930,1560" fill="#aeb8c0"/></g>'
yp_ = persona(540, 1660, 560, pid="yo5", e=YO, expr0="nervioso")
ys_c, ys_b = sentado("yo6", 540, 1310, 330, "#ffffff", lado_mano=1, e=YO, expr0="neutral")
lav += [f'<g id="yoDePie">{yp_}</g>',
        f'<g id="yoSentado" opacity="0">{ys_c}{piernas_sentado(540, 1350, 1.1, PANT_YO)}<rect x="440" y="1540" width="200" height="34" rx="14" fill="{PANT_YO}"/>{ys_b}</g>',
        '<g id="viento5" opacity="0">' + "".join(f'<path d="M{540 + dx},{900 + i * 40} Q{540 + dx * 0.6},{1150} {540 + dx * 0.1},{1330}" stroke="#ffffff" stroke-width="6" fill="none" stroke-linecap="round" stroke-dasharray="40 50" opacity="0.8"/>' for i, dx in enumerate((-260, -180, -90, 90, 180, 260))) + '</g>',
        paredI, paredD, '<rect id="osc5" width="1080" height="1920" fill="#0a0f18" opacity="0.38"/>']
escena("e5", "".join(lav))
f5, f6, f7, f8 = F(5), F(6), F(7), F(8)
p_sienta = P("sientas")
mostrar("e5", f5, f6); mostrar("e5", p_sienta - 0.15, f8)
camara("e5", f5, f6, enfoca(540, 1180, 1.25), enfoca(540, 1180, 1.05), "power2.out")
J(f'tl.fromTo("#parI", {{x:-140}}, {{x:120, duration:0.5, ease:"back.out(1.6)", immediateRender:false}}, {P("tamano") - 0.1:.2f}); tl.fromTo("#parD", {{x:140}}, {{x:-120, duration:0.5, ease:"back.out(1.6)", immediateRender:false}}, {P("tamano") - 0.1:.2f});')
J(f'tl.fromTo("#yo5", {{scaleX:1}}, {{scaleX:0.9, svgOrigin:"540 1660", duration:0.25, yoyo:true, repeat:1, immediateRender:false}}, {P("armario") - 0.1:.2f});')
expr("yo5", P("armario") - 0.1, "nervioso", "sorpresa")
FX.append(("golpe", P("armario") - 0.05))
# 6) pestillo (inserto): LIBRE → OCUPADO y se enciende la luz
pest = ('<rect width="1080" height="1920" fill="#dfe8ee"/>' + "".join(f'<rect x="0" y="{y}" width="1080" height="4" fill="#c7d0d6"/>' for y in range(200, 1920, 160))
        + '<rect x="240" y="760" width="600" height="400" rx="40" fill="#c9d1d9" stroke="#9aa6b6" stroke-width="10"/><rect x="300" y="830" width="480" height="130" rx="16" fill="#1a1d22"/>'
        + '<g id="libre6"><rect x="310" y="840" width="460" height="110" rx="12" fill="#1f8f4e"/><text x="540" y="918" text-anchor="middle" font-family="Inter" font-weight="900" font-size="70" fill="#ffffff" letter-spacing="4">LIBRE</text></g>'
        + '<g id="ocup6" opacity="0"><rect x="310" y="840" width="460" height="110" rx="12" fill="#d8261a"/><text x="540" y="918" text-anchor="middle" font-family="Inter" font-weight="900" font-size="64" fill="#ffffff" letter-spacing="3">OCUPADO</text></g>'
        + '<rect x="320" y="1010" width="440" height="60" rx="30" fill="#9aa6b6"/><g id="pomo6"><rect x="330" y="996" width="150" height="88" rx="30" fill="#e9eef2" stroke="#7d8894" stroke-width="6"/><path d="M375,1040 L435,1040" stroke="#7d8894" stroke-width="8" stroke-linecap="round"/></g>'
        + mano_svg("mano6", 400, 1110, 3.2, YO["piel"]))
escena("e6", pest)
mostrar("e6", f6, p_sienta - 0.15)
camara("e6", f6, p_sienta - 0.15, enfoca(540, 960, 1.0), enfoca(540, 960, 1.12), "sine.out")
tp = P("pestillo")
J(f'tl.fromTo("#pomo6, #mano6 .mv", {{x:0}}, {{x:270, duration:0.3, ease:"power3.inOut", immediateRender:false}}, {tp:.2f});')
J(f'tl.set("#libre6", {{opacity:0}}, {tp + 0.28:.2f}); tl.set("#ocup6", {{opacity:1}}, {tp + 0.28:.2f}); tl.to("#osc5", {{opacity:0, duration:0.25}}, {tp + 0.28:.2f}); tl.to("#lamp5", {{opacity:1, duration:0.25}}, {tp + 0.28:.2f});')
FX.append(("clic2", tp + 0.28))
# sentado + turbulencias
J(f'tl.set("#yoDePie", {{opacity:0}}, {p_sienta - 0.15:.2f}); tl.set("#yoSentado", {{opacity:1}}, {p_sienta - 0.15:.2f});')
camara("e5", p_sienta - 0.15, P("boton") - 0.3, enfoca(540, 1200, 1.15), enfoca(540, 1200, 1.22), "sine.inOut")
expr("yo6", p_sienta, "sonrisa", "neutral")
tt_ = P("turbulencias")
J(f'tl.fromTo("#e5", {{x:0, y:0, rotation:0}}, {{x:"random(-16,16)", y:"random(-12,12)", rotation:"random(-1.2,1.2)", duration:0.07, repeat:22, yoyo:true, ease:"none", immediateRender:false}}, {tt_ - 0.1:.2f}); tl.to("#e5", {{x:0, y:0, rotation:0, duration:0.1}}, {tt_ + 1.55:.2f});')
J(f'tl.fromTo("#jabon", {{rotation:0}}, {{rotation:-24, svgOrigin:"990 1032", duration:0.15, yoyo:true, repeat:9, immediateRender:false}}, {tt_:.2f});')
J(f'tl.fromTo("#papel5", {{scaleY:1}}, {{scaleY:4, svgOrigin:"225 1214", duration:0.8, ease:"bounce.out", immediateRender:false}}, {tt_ + 0.1:.2f});')
expr("yo6", tt_ - 0.1, "nervioso", "sorpresa", abierta=True)
mano_a("yo6", tt_ - 0.05, 920, 1060, 0.25)
FX.append(("turbu", tt_ - 0.1))
# 7) termina (cara de alivio) y pulsa el botón
expr("yo6", f7 + 0.1, "sonrisa", "neutral")
tb7 = P("boton") + 0.1
mano_a("yo6", tb7 - 0.45, 745, 1190, 0.4)
J(f'tl.fromTo("#puls5", {{scale:1}}, {{scale:0.86, svgOrigin:"745 1185", duration:0.08, yoyo:true, repeat:1, immediateRender:false}}, {tb7:.2f}); tl.fromTo("#pulsLuz", {{opacity:0}}, {{opacity:1, duration:0.12, yoyo:true, repeat:1, immediateRender:false}}, {tb7:.2f});')
J(f'tl.to("#e5-cam", {{x:{enfoca(700, 1190, 1.9)[0]}, y:{enfoca(700, 1190, 1.9)[1]}, scale:1.9, duration:0.5, ease:"power3.out"}}, {tb7 - 0.35:.2f});')
FX.append(("clic", tb7))

# ================================================================== 8-9) CORTE DE LA TAZA: se abre la trampilla · rugido · no es agua, es aire
sec = ['<rect width="1080" height="1920" fill="url(#pared_lav)"/>', '<rect x="0" y="1560" width="1080" height="360" fill="url(#suelo_lav)"/>',
       # taza en corte: acero por fuera, hueco por dentro, salida por abajo con la trampilla
       '<path d="M200,900 L880,900 C880,1150 760,1250 620,1290 L620,1360 L460,1360 L460,1290 C320,1250 200,1150 200,900 Z" fill="url(#inox)"/>',
       '<path d="M250,920 L830,920 C830,1120 720,1210 600,1250 L600,1300 L480,1300 L480,1250 C360,1210 250,1120 250,920 Z" fill="#59626d"/>',
       '<path d="M250,920 L830,920 C830,1120 720,1210 600,1250 L600,1300 L480,1300 L480,1250 C360,1210 250,1120 250,920 Z" fill="url(#inoxV)" opacity="0.35"/>',
       '<rect x="180" y="880" width="720" height="34" rx="16" fill="#1f2328"/>',
       # tubo que baja y se va hacia la cola
       '<path d="M540,1300 L540,1600 Q540,1700 440,1700 L-200,1700" stroke="#6f7884" stroke-width="150" fill="none"/><path d="M540,1300 L540,1600 Q540,1700 440,1700 L-200,1700" stroke="#3a4048" stroke-width="110" fill="none"/>',
       '<path id="flujo8" d="M540,1300 L540,1600 Q540,1700 440,1700 L-200,1700" stroke="#cfefff" stroke-width="14" fill="none" stroke-dasharray="60 70" opacity="0"/>',
       # trampilla (bisagra a la izquierda)
       '<g id="flap8"><rect x="480" y="1292" width="120" height="20" rx="8" fill="#2a2e35"/><rect x="480" y="1292" width="120" height="6" rx="3" fill="#8a95a1"/></g><circle cx="484" cy="1302" r="12" fill="#9aa3ad"/>',
       caca("k8", 540, 1282, 2.6),
       '<g id="aire8" opacity="0">' + "".join(f'<path d="M{x},{860 - (i % 2) * 60} C{x},1080 {540 + (x - 540) * 0.3:.0f},1180 540,1290" stroke="#ffffff" stroke-width="10" fill="none" stroke-linecap="round" stroke-dasharray="50 60" opacity="0.9"/>' for i, x in enumerate((180, 300, 420, 660, 780, 900))) + '</g>',
       '<g transform="translate(560,330) scale(0.5)"><g id="gota9" opacity="0"><path d="M540,560 C580,630 610,680 610,720 C610,770 575,800 540,800 C505,800 470,770 470,720 C470,680 500,630 540,560 Z" fill="url(#azulQ)"/><path d="M450,560 L630,800 M630,560 L450,800" stroke="#d8261a" stroke-width="22" stroke-linecap="round"/></g></g>',
       '<g id="limpio11" opacity="0">' + "".join(destello(x, y, r) for x, y, r in ((360, 980, 30), (700, 1010, 40), (560, 1150, 26), (430, 1120, 20), (780, 940, 22))) + '</g>',
       '<g id="chorro11" opacity="0"><path d="M250,930 Q380,1080 520,1250" stroke="#4fb8ff" stroke-width="12" fill="none" stroke-linecap="round"/><path d="M830,930 Q700,1080 560,1250" stroke="#4fb8ff" stroke-width="12" fill="none" stroke-linecap="round"/></g>']
escena("e8", "".join(sec))
p_tr = P("trampilla")
mostrar("e8", f8, P("rugido") - 0.1); mostrar("e8", F(9), F(10)); mostrar("e8", F(11), F(12))
camara("e8", f8, P("rugido") - 0.1, enfoca(540, 1150, 1.05), enfoca(540, 1220, 1.25), "sine.inOut")
J(f'tl.to("#flap8", {{rotation:80, svgOrigin:"484 1302", duration:0.25, ease:"power3.in"}}, {p_tr:.2f});')
J(f'tl.to("#k8", {{y:420, x:0, scale:0.5, duration:0.35, ease:"power3.in"}}, {p_tr + 0.18:.2f}); tl.set("#k8", {{opacity:0}}, {p_tr + 0.55:.2f});')
J(f'tl.set("#aire8", {{opacity:1}}, {p_tr + 0.1:.2f}); tl.fromTo("#aire8 path", {{strokeDashoffset:0}}, {{strokeDashoffset:-330, duration:0.6, repeat:5, ease:"none", immediateRender:false}}, {p_tr + 0.1:.2f});')
J(f'tl.set("#flujo8", {{opacity:0.85}}, {p_tr + 0.15:.2f}); tl.fromTo("#flujo8", {{strokeDashoffset:0}}, {{strokeDashoffset:-520, duration:0.5, repeat:9, ease:"none", immediateRender:false}}, {p_tr + 0.15:.2f});')
FX.append(("aspira", p_tr + 0.1))
# rugido: vuelve al pasajero, despeinado y asustado
J(f'tl.set("#e5-cam", {{x:{enfoca(540, 1150, 1.3)[0]}, y:{enfoca(540, 1150, 1.3)[1]}, scale:1.3}}, {P("rugido") - 0.1:.2f});')
mostrar("e5", P("rugido") - 0.1, F(9))
J(f'tl.set("#viento5", {{opacity:1}}, {P("rugido") - 0.1:.2f}); tl.fromTo("#viento5 path", {{strokeDashoffset:0}}, {{strokeDashoffset:-360, duration:0.5, repeat:4, ease:"none", immediateRender:false}}, {P("rugido") - 0.1:.2f}); tl.set("#viento5", {{opacity:0}}, {F(9):.2f});')
J(f'tl.fromTo("#e5-cam", {{rotation:0}}, {{rotation:0.8, duration:0.05, yoyo:true, repeat:25, immediateRender:false}}, {P("rugido") - 0.1:.2f});')
J(f'tl.fromTo("#yo6 .cab", {{y:0}}, {{y:16, duration:0.06, yoyo:true, repeat:19, immediateRender:false}}, {P("rugido") - 0.1:.2f});')
expr("yo6", P("rugido") - 0.1, "nervioso", "sorpresa", abierta=True)
mano_reposo("yo6", P("rugido"), 0.2)
FX.append(("rugido", P("rugido") - 0.15))
# 9) no es agua: es aire
camara("e8", F(9), F(10), enfoca(540, 1050, 1.0), enfoca(540, 1080, 1.08), "sine.inOut")
J(f'tl.set("#flap8", {{rotation:80, svgOrigin:"484 1302"}}, {F(9):.2f}); tl.set("#k8", {{opacity:0}}, {F(9):.2f});')
J(f'tl.fromTo("#gota9", {{opacity:0, scale:0.4}}, {{opacity:1, scale:1, svgOrigin:"540 700", duration:0.3, ease:"back.out(2)", immediateRender:false}}, {P("agua") - 0.15:.2f}); tl.to("#gota9", {{opacity:0, duration:0.2}}, {P("aire") - 0.2:.2f});')
J(f'tl.fromTo("#aire8", {{scale:1}}, {{scale:1.12, svgOrigin:"540 1290", duration:0.3, yoyo:true, repeat:3, immediateRender:false}}, {P("aire") - 0.1:.2f}); tl.set("#aire8", {{opacity:0}}, {F(10):.2f});')
FX.append(("whoosh", P("aire") - 0.15))

# ================================================================== 10) LA PRESIÓN: dentro mucha, fuera poca → el tubo aspira (aspiradora gigante)
# 12-13) por el tubo bajo los pasajeros hasta el depósito de la cola; ahí se queda todo el vuelo
r10 = random.Random(10)
aire_dentro = '<g id="pd10" opacity="0">' + "".join(f'<circle cx="{r10.uniform(820, 2680):.0f}" cy="{r10.uniform(850, 1070):.0f}" r="{r10.uniform(4, 7):.1f}" fill="#4f9be8" opacity="0.7"/>' for _ in range(240)) + '</g>'
aire_fuera = '<g id="pf10" opacity="0">' + "".join(f'<circle cx="{r10.uniform(-200, 3300):.0f}" cy="{r10.choice((r10.uniform(300, 760), r10.uniform(1250, 1800))):.0f}" r="{r10.uniform(4, 7):.1f}" fill="#ffffff" opacity="0.8"/>' for _ in range(40)) + '</g>'
aspiradora = ('<g id="asp10" opacity="0"><g transform="translate(330,1500) scale(1.5)">'
              '<path d="M-160,40 C-160,-60 -60,-110 60,-100 C160,-90 200,-30 200,40 Z" fill="#e8261a"/><path d="M-150,30 C-140,-40 -60,-90 40,-86" stroke="#ffffff" stroke-width="10" opacity="0.4" fill="none"/>'
              '<rect x="-170" y="30" width="380" height="40" rx="18" fill="#2a2e35"/><circle cx="-120" cy="80" r="30" fill="#1a1d22"/><circle cx="160" cy="80" r="30" fill="#1a1d22"/>'
              '<circle cx="-120" cy="80" r="11" fill="#9aa3ad"/><circle cx="160" cy="80" r="11" fill="#9aa3ad"/><rect x="-30" y="-60" width="90" height="34" rx="10" fill="#ffcf4d"/></g>'
              '<path d="M520,1400 C560,1300 560,1240 570,1190" stroke="#2a2e35" stroke-width="36" fill="none" stroke-linecap="round"/></g>')
cuerpo10 = (f'<rect x="-3000" y="-3500" width="9500" height="7000" fill="url(#cieloAlto)"/><rect id="ocaso10" x="-3000" y="-3500" width="9500" height="7000" fill="url(#cieloOcaso)" opacity="0"/>'
            + nubes(-1500, 1300, 8, 21, 6000, 600, 2.4, 0.85) + nubes(-1500, 200, 5, 22, 6000, 500, 2.0, 0.8) + aire_fuera + aspiradora + avion("av2")
            + aire_dentro + caca("k12", LAV_X - 6, 1050, 1.0) + estela("st12", LAV_X - 6, 1050, 120, "#ffffff"))
escena("e10", cuerpo10, 3200)
f10, f11, f12, f13, f14 = F(10), F(11), F(12), F(13), F(14)
mostrar("e10", f10, f11); mostrar("e10", f12, f14)
camara("e10", f10, P("aspiradora") - 0.3, enfoca(1660, 1030, 0.42), enfoca(1560, 1060, 0.46), "sine.inOut")
J(f'tl.to("#e10-cam", {{x:{enfoca(900, 1180, 0.8)[0]}, y:{enfoca(900, 1180, 0.8)[1]}, scale:0.8, duration:0.6, ease:"power3.inOut"}}, {P("aspiradora") - 0.3:.2f});')
J(f'tl.fromTo("#pd10", {{opacity:0}}, {{opacity:1, duration:0.4, immediateRender:false}}, {P("dentro") - 0.6:.2f}); tl.fromTo("#pd10 circle", {{x:-3}}, {{x:3, duration:0.12, yoyo:true, repeat:30, stagger:{{each:0.002, from:"random"}}, immediateRender:false}}, {P("dentro") - 0.6:.2f});')
J(f'tl.fromTo("#pf10", {{opacity:0}}, {{opacity:1, duration:0.4, immediateRender:false}}, {P("presion") - 0.1:.2f});')
J(f'tl.to("#pd10, #pf10", {{opacity:0, duration:0.3}}, {f11 - 0.3:.2f});')
nota("DENTRO · PRESIÓN ALTA", P("dentro") - 0.3, P("tubo") - 0.1, 560, 1140, "#4f9be8")
nota("FUERA · PRESIÓN MUY BAJA", P("presion") - 0.1, P("dentro") + 0.4, 120, 760, "#ffffff")
J(f'tl.set("#av2_flujo, #av2_resp", {{opacity:0.95}}, {P("tubo") - 0.1:.2f}); tl.fromTo("#av2_flujo, #av2_resp", {{strokeDashoffset:0}}, {{strokeDashoffset:-1400, duration:{f11 - P("tubo"):.2f}, ease:"none", immediateRender:false}}, {P("tubo") - 0.1:.2f}); tl.set("#av2_flujo, #av2_resp", {{opacity:0}}, {f11:.2f});')
J(f'tl.fromTo("#asp10", {{opacity:0, scale:0.3}}, {{opacity:1, scale:1, svgOrigin:"330 1500", duration:0.4, ease:"back.out(2)", immediateRender:false}}, {P("aspiradora") - 0.15:.2f});')
J(f'tl.fromTo("#asp10", {{x:-6}}, {{x:6, duration:0.05, yoyo:true, repeat:30, immediateRender:false}}, {P("aspiradora") + 0.3:.2f});')
FX.append(("whoosh", P("tubo") - 0.2)); FX.append(("aspira", P("aspiradora")))
# 11) en un segundo, limpia (en el corte de la taza: trampilla cerrada, chorrito azul, brillos)
camara("e8", f11, f12, enfoca(540, 1080, 1.05), enfoca(540, 1080, 1.15), "sine.out")
J(f'tl.set("#flap8", {{rotation:0, svgOrigin:"484 1302"}}, {f11:.2f}); tl.set("#k8, #aire8, #gota9, #flujo8", {{opacity:0}}, {f11:.2f});')
J(f'tl.fromTo("#chorro11", {{opacity:0}}, {{opacity:1, duration:0.15, yoyo:true, repeat:1, immediateRender:false}}, {f11 + 0.2:.2f});')
J(f'tl.fromTo("#limpio11", {{opacity:0}}, {{opacity:1, duration:0.2, immediateRender:false}}, {P("limpia") - 0.3:.2f}); tl.fromTo("#limpio11 .chispa", {{scale:0, rotation:0}}, {{scale:1, rotation:45, transformOrigin:"50% 50%", duration:0.4, stagger:0.08, yoyo:true, repeat:3, ease:"back.out(2)", immediateRender:false}}, {P("limpia") - 0.3:.2f});')
nota("1 SEGUNDO", P("segundo") - 0.1, f12 - 0.1, 400, 560, "#7fe0ff")
FX.append(("brillo", P("limpia") - 0.3))
# 12) bajo los pasajeros (el del bocadillo ni se entera)
t12a, t12b = f12 + 0.2, P("deposito")
J(f'tl.set("#k12", {{opacity:0}}, 0); tl.set("#k12", {{x:0, y:74, opacity:1}}, {f12:.2f}); tl.set("#st12", {{opacity:1, x:0, y:74}}, {f12:.2f});')
J(f'tl.to("#k12, #st12", {{x:{TANK[2] - LAV_X + 6 - 20}, duration:{t12b - t12a:.2f}, ease:"sine.inOut"}}, {t12a:.2f});')
J(f'tl.to("#k12", {{y:96, x:{TANK[2] - LAV_X + 6 - 90}, scale:0.6, opacity:0, duration:0.25, ease:"power2.in"}}, {t12b:.2f}); tl.set("#st12", {{opacity:0}}, {t12b:.2f});')
J(f'tl.set("#e10-cam", {{x:{enfoca(LAV_X - 6, 1040, 1.6)[0]}, y:{enfoca(LAV_X - 6, 1040, 1.6)[1]}, scale:1.6}}, {f12:.2f});')
J(f'tl.to("#e10-cam", {{x:{enfoca(TANK[2] - 10, 1040, 1.6)[0]}, duration:{t12b - t12a:.2f}, ease:"sine.inOut"}}, {t12a:.2f});')
J(f'tl.fromTo("#bocata", {{y:0, rotation:0}}, {{y:-10, rotation:-12, svgOrigin:"1733 1013", duration:0.35, yoyo:true, repeat:9, ease:"sine.inOut", immediateRender:false}}, {f12:.2f});')
J(f'tl.fromTo("#e10 .pax", {{y:0}}, {{y:-3, duration:0.6, yoyo:true, repeat:10, stagger:{{each:0.03, from:"random"}}, ease:"sine.inOut", immediateRender:false}}, {f12:.2f});')
nota("BAJO TUS PIES", P("pasajeros") - 0.4, P("deposito") - 0.2, 560, 1280, "#ffcf4d")
# 13) el depósito se va llenando todo el vuelo; atardece
J(f'tl.to("#e10-cam", {{x:{enfoca(700, 1120, 2.2)[0]}, y:{enfoca(700, 1120, 2.2)[1]}, scale:2.2, duration:0.5, ease:"power2.inOut"}}, {t12b:.2f});')
J(f'tl.to("#av2_nivel", {{y:{(TANK[3] - TANK[1]) * 0.15:.0f}, duration:{f14 - P("queda", 2):.2f}, ease:"steps(7)"}}, {P("queda", 2):.2f});')
J(f'tl.to("#e10-cam", {{x:{enfoca(1500, 1100, 0.5)[0]}, y:{enfoca(1500, 1100, 0.5)[1]}, scale:0.5, duration:1.2, ease:"power2.inOut"}}, {P("queda", 2) - 0.2:.2f});')
J(f'tl.to("#ocaso10", {{opacity:1, duration:{f14 - P("queda", 2):.2f}, ease:"none"}}, {P("queda", 2):.2f}); tl.fromTo("#e10 .nube", {{x:0}}, {{x:-1500, duration:{f14 - P("queda", 2):.2f}, ease:"none", immediateRender:false}}, {P("queda", 2):.2f});')
nota("DEPÓSITO", P("deposito") + 0.3, P("queda", 2) - 0.2, 420, 1180, "#ffcf4d")
FX.append(("chof", t12b + 0.05)); FX.append(("whoosh", f12 + 0.1))

# ================================================================== 14-16) EN TIERRA: llega el camión, manguera, válvula, se vacía; agua y desinfectante azul; despega
def camion(cid):
    """Camión de aguas residuales (cisterna con el rótulo pintado, cabina, rotativo, ruedas). Origen: rueda trasera en (0,0)."""
    return (f'<g id="{cid}">'
            '<ellipse cx="160" cy="44" rx="300" ry="16" fill="#000" opacity="0.25"/>'
            '<rect x="-90" y="-60" width="420" height="40" rx="8" fill="#3a3f48"/>'
            '<rect x="-80" y="-250" width="330" height="190" rx="70" fill="#f4f7fa" stroke="#9aa6b6" stroke-width="5"/><rect x="-80" y="-180" width="330" height="40" fill="#1f6fd8"/>'
            '<text x="85" y="-152" text-anchor="middle" font-family="Inter" font-weight="900" font-size="25" fill="#ffffff" letter-spacing="1">AGUAS RESIDUALES</text>'
            '<rect x="200" y="-232" width="22" height="150" rx="8" fill="#dfe5ec" stroke="#7d8894" stroke-width="3"/><rect id="ccNivel" x="203" y="-110" width="16" height="25" fill="#8a5a2e"/>'
            '<rect x="-100" y="-120" width="30" height="40" rx="6" fill="#7d8894"/><circle cx="-85" cy="-100" r="10" fill="#ffcf4d"/>'
            '<path d="M260,-60 L260,-220 Q260,-240 280,-240 L370,-240 Q410,-240 420,-200 L440,-120 L440,-60 Z" fill="#1f6fd8"/><path d="M290,-225 L370,-225 Q395,-225 402,-200 L415,-140 L290,-140 Z" fill="#9fd6ff"/>'
            '<rect x="300" y="-262" width="40" height="22" rx="6" fill="#ffb84d"/><circle class="rotat" cx="320" cy="-262" r="40" fill="url(#brilloOro)" opacity="0.7"/>'
            + "".join(f'<g class="rueda" transform="translate({x},0)"><circle r="44" fill="#1a1d22"/><circle r="20" fill="#9aa3ad"/><rect x="-4" y="-20" width="8" height="40" fill="#5b636d"/></g>' for x in (0, 90, 370))
            + '</g>')
def terminal():
    s = ['<rect width="1080" height="1920" fill="url(#cieloTarde)"/>', nubes(-200, 280, 4, 14, 1300, 200, 1.4),
         '<rect x="-100" y="900" width="1300" height="380" fill="#dfe5ec"/><rect x="-100" y="900" width="1300" height="40" fill="#9aa6b6"/>'
         + "".join(f'<rect x="{x}" y="960" width="70" height="250" fill="#7fb3d8" opacity="0.85"/><rect x="{x}" y="960" width="70" height="250" fill="url(#rayoLuz)" opacity="0.3"/>' for x in range(-80, 1200, 90)),
         '<rect x="830" y="560" width="70" height="380" fill="#c9d1d9"/><path d="M790,560 L940,560 L920,470 L810,470 Z" fill="#2a3a55"/><rect x="800" y="530" width="130" height="30" fill="#9fd6ff"/>',
         '<rect x="-100" y="1280" width="1300" height="640" fill="#9aa0a6"/>' + "".join(f'<rect x="{x}" y="1290" width="60" height="1" fill="#000"/>' for x in range(0, 1080, 200)),
         '<path d="M-100,1700 L1200,1640" stroke="#ffcf4d" stroke-width="14"/><path d="M-100,1560 L1200,1520" stroke="#ffffff" stroke-width="6" stroke-dasharray="60 40" opacity="0.7"/>',
         "".join(f'<path d="M{x - 18},1640 L{x},1590 L{x + 18},1640 Z" fill="#ff8a1a"/><rect x="{x - 12}" y="1608" width="24" height="7" fill="#ffffff"/>' for x in (120, 960))]
    return "".join(s)
cuerpo14 = (terminal() + '<g transform="translate(-250,260) scale(0.9)">' + avion("av3", corte=False, tren=True) + '</g>'
            # ventana de corte sobre el depósito (dentro del fuselaje)
            + '<clipPath id="ins14"><rect x="300" y="1205" width="200" height="98" rx="18"/></clipPath>'
            + '<g id="ins14g" opacity="0"><rect x="294" y="1199" width="212" height="110" rx="22" fill="#2a2e35"/><g clip-path="url(#ins14)"><rect x="300" y="1205" width="200" height="98" fill="#f4f7fa"/>'
            + '<rect id="nivel14" x="300" y="1205" width="200" height="98" fill="#8a5a2e" transform="translate(0,20)"/><rect id="azul16" x="300" y="1205" width="200" height="98" fill="url(#azulQ)" transform="translate(0,98)"/></g></g>'
            + '<path id="mang14" d="M385,1445 C440,1580 300,1560 300,1440 C300,1380 330,1340 393,1322" stroke="#2a2e35" stroke-width="24" fill="none" stroke-linecap="round" stroke-dasharray="700" stroke-dashoffset="700"/>'
            + '<path id="flu14" d="M393,1322 C330,1340 300,1380 300,1440 C300,1560 440,1580 385,1445" stroke="#c99a6a" stroke-width="8" fill="none" stroke-dasharray="20 26" opacity="0"/>'
            + '<g transform="translate(470,1560)">' + camion("cam14") + '</g>'
            + f'<g id="oper14">{persona(250, 1790, 520, pid="op14", e=estilo(91, ropa="#ff8a1a", peinado="corto", pelo="#1a1a1a"), expr0="serio")}'
            + '<rect x="196" y="1420" width="108" height="14" fill="#f4f7fa" opacity="0.9"/><rect x="196" y="1470" width="108" height="14" fill="#f4f7fa" opacity="0.9"/></g>')
escena("e14", cuerpo14)
f15, f16, f17 = F(15), F(16), F(17)
mostrar("e14", f14, P("vuelo", 3) - 0.25 if False else P("listo") + 0.1)
camara("e14", f14, P("listo") + 0.1, enfoca(540, 960, 1.0), enfoca(470, 1050, 1.18), "sine.inOut")
J(f'tl.fromTo("#cam14", {{x:900}}, {{x:0, duration:1.8, ease:"power2.out", immediateRender:false}}, {f14:.2f});')
J(f'tl.fromTo("#cam14 .rueda", {{rotation:0}}, {{rotation:-720, duration:1.8, ease:"power2.out", immediateRender:false}}, {f14:.2f});')
J(f'tl.fromTo("#cam14 .rotat", {{opacity:0.2}}, {{opacity:0.9, duration:0.25, yoyo:true, repeat:{int((P("listo") - f14) / 0.25)}, immediateRender:false}}, {f14:.2f});')
J(f'tl.fromTo("#oper14", {{x:-260}}, {{x:0, duration:1.0, ease:"power1.out", immediateRender:false}}, {f14 + 0.6:.2f}); tl.fromTo("#oper14", {{y:0}}, {{y:-10, duration:0.2, yoyo:true, repeat:4, immediateRender:false}}, {f14 + 0.6:.2f});')
J(f'tl.to("#mang14", {{strokeDashoffset:0, duration:0.8, ease:"power2.inOut"}}, {P("manguera") - 0.3:.2f});')
J(f'tl.to("#op14 .brazo", {{rotation:-120, svgOrigin:"{250 + 34 * 520 / 300:.0f} {1790 - 228 * 520 / 300:.0f}", duration:0.35, yoyo:true, repeat:3}}, {P("manguera") - 0.3:.2f});')
J(f'tl.to("#av3_palanca", {{rotation:90, svgOrigin:"725 1163", duration:0.3, ease:"back.out(2)"}}, {P("valvula") - 0.1:.2f});')
J(f'tl.set("#ins14g", {{opacity:1}}, {P("valvula") - 0.1:.2f}); tl.set("#flu14", {{opacity:0.95}}, {P("valvula"):.2f}); tl.fromTo("#flu14", {{strokeDashoffset:0}}, {{strokeDashoffset:-600, duration:{f16 - P("valvula"):.2f}, ease:"none", immediateRender:false}}, {P("valvula"):.2f});')
J(f'tl.to("#nivel14", {{y:98, duration:{f16 - P("valvula") - 0.2:.2f}, ease:"power1.inOut"}}, {P("valvula") + 0.1:.2f}); tl.to("#ccNivel", {{attr:{{y:-200, height:115}}, duration:{f16 - P("valvula") - 0.2:.2f}, ease:"power1.inOut"}}, {P("valvula") + 0.1:.2f});')
nota("EN MINUTOS", P("minutos") - 0.3, f16 - 0.1, 600, 1700, "#ffcf4d")
FX.append(("camion", f14)); FX.append(("clic2", P("valvula") - 0.1)); FX.append(("aspira", P("valvula") + 0.1))
# 16) agua + desinfectante azul
J(f'tl.to("#flu14", {{stroke:"#4fb8ff", duration:0.1}}, {f16:.2f}); tl.to("#azul16", {{y:30, duration:1.5, ease:"power1.out"}}, {f16 + 0.1:.2f});')
J(f'tl.fromTo("#flu14", {{strokeDashoffset:0}}, {{strokeDashoffset:600, duration:{P("listo") - f16:.2f}, ease:"none", immediateRender:false}}, {f16:.2f});')
nota("AGUA + DESINFECTANTE AZUL", P("agua", 2) - 0.2, P("listo") - 0.1, 160, 1700, "#4fb8ff")
FX.append(("brillo", P("azul") - 0.2))
# «listo para otro vuelo»: despega
desp = ('<rect width="1080" height="1920" fill="url(#cieloTarde)"/>' + nubes(-300, 300, 5, 31, 1500, 300, 1.6)
        + '<rect x="-200" y="1380" width="1500" height="560" fill="#7a8088"/><rect x="-200" y="1360" width="1500" height="30" fill="#5fae4a"/>'
        + '<path d="M-200,1600 L1300,1600" stroke="#ffffff" stroke-width="12" stroke-dasharray="90 70"/>'
        + '<g id="av4g"><g transform="translate(40,1060) scale(0.33)">' + avion("av4", corte=False, tren=True) + '</g></g>')
escena("e16", desp)
mostrar("e16", P("listo") + 0.1, f17)
J(f'tl.fromTo("#av4g", {{x:-300, y:0, rotation:0}}, {{x:500, y:-120, rotation:-9, svgOrigin:"600 1400", duration:{f17 - P("listo") - 0.1:.2f}, ease:"power2.in", immediateRender:false}}, {P("listo") + 0.1:.2f});')
camara("e16", P("listo") + 0.1, f17, enfoca(540, 1200, 1.0), enfoca(560, 1100, 1.1), "power1.in")
FX.append(("despegue", P("listo")))

# ================================================================== 17-19) EL PROBLEMA: la válvula gotea, se congela… y se suelta encima de un tejado
fuga = ('<rect x="-2000" y="0" width="5000" height="4600" fill="url(#cieloOcaso)"/>' + nubes(-800, 2750, 7, 41, 2600, 700, 2.0, 0.8) + nubes(-800, 1500, 5, 42, 2600, 400, 1.6, 0.7)
        + '<g transform="translate(-1300,-300) scale(2.4)">' + avion("av5", corte=False) + '</g>'
        + '<g id="gotas17">' + "".join(f'<path class="gota" d="M{430 + i * 0},{2490} q10,16 0,24 q-10,-8 0,-24 Z" fill="#7fd0ff"/>' for i in range(3)) + '</g>'
        + '<g id="hielo18">' + bloque_hielo(440, 2520, 0.9) + '</g>'
        + '<g id="escarcha18" opacity="0">' + "".join(destello(x, y, r, "#e8fbff") for x, y, r in ((300, 2470, 20), (500, 2500, 14), (260, 2600, 16), (520, 2620, 18))) + '</g>'
        + '<g id="viento17">' + "".join(f'<path d="M{1100 + i * 40},{2300 + i * 70} L{700 + i * 40},{2300 + i * 70}" stroke="#ffffff" stroke-width="5" stroke-linecap="round" opacity="0.6"/>' for i in range(6)) + '</g>')
escena("e17", fuga)
f18, f19 = F(18), F(19)
mostrar("e17", f17, f19)
# panel en pantalla: (725,1176) del avión → (-1300+725*2.4, -300+1176*2.4) = (440, 2522)
camara("e17", f17, f19, enfoca(480, 2450, 0.9), enfoca(430, 2540, 1.25), "sine.inOut")
J(f'tl.fromTo("#gotas17 .gota", {{x:0, y:0, opacity:1, scaleY:1}}, {{x:-160, y:260, opacity:0, scaleY:2.2, transformOrigin:"50% 0%", duration:0.7, stagger:0.45, repeat:2, ease:"power2.in", immediateRender:false}}, {P("gotea") - 0.4:.2f});')
J(f'tl.fromTo("#viento17 path", {{x:0}}, {{x:-500, duration:0.5, repeat:{int((f19 - f17) / 0.5)}, stagger:0.08, ease:"none", immediateRender:false}}, {f17:.2f});')
J(f'tl.fromTo("#e17 .nube", {{x:0}}, {{x:-1200, duration:{f19 - f17:.2f}, ease:"none", immediateRender:false}}, {f17:.2f});')
J(f'tl.set("#hielo18", {{scale:0, svgOrigin:"440 2512"}}, 0); tl.to("#hielo18", {{scale:1, svgOrigin:"440 2512", duration:{P("azul", 2) - P("congela") + 0.2:.2f}, ease:"steps(6)"}}, {P("congela") - 0.1:.2f});')
J(f'tl.set("#escarcha18", {{opacity:1}}, {P("congela"):.2f}); tl.fromTo("#escarcha18 .chispa", {{scale:0}}, {{scale:1, transformOrigin:"50% 50%", duration:0.3, stagger:0.15, yoyo:true, repeat:3, immediateRender:false}}, {P("congela"):.2f});')
nota("FUERA: −50 °C", P("congela") - 0.2, f19 - 0.1, 120, 600, "#9fdcff")
FX.append(("gota", P("gotea") - 0.1)); FX.append(("gota", P("gotea") + 0.35)); FX.append(("cristal", P("congela"))); FX.append(("cristal", P("hielo")))
# 19) baja sobre un barrio… se suelta… directo a un tejado → CORTE SECO
def casita(x, suelo, w, h, pared, teja, seed):
    r_ = random.Random(seed)
    return (f'<rect x="{x}" y="{suelo - h}" width="{w}" height="{h}" fill="{pared}"/><polygon points="{x - 20},{suelo - h} {x + w / 2:.0f},{suelo - h - w * 0.45:.0f} {x + w + 20},{suelo - h}" fill="{teja}"/>'
            + "".join(f'<path d="M{x - 10 + i * 0},{suelo - h - 10 * i}" />' for i in range(0))
            + f'<rect x="{x + w * 0.15:.0f}" y="{suelo - h * 0.7:.0f}" width="{w * 0.25:.0f}" height="{h * 0.3:.0f}" fill="#9fd6ff" stroke="#ffffff" stroke-width="5"/><rect x="{x + w * 0.6:.0f}" y="{suelo - h * 0.7:.0f}" width="{w * 0.25:.0f}" height="{h * 0.3:.0f}" fill="#ffe7a0" stroke="#ffffff" stroke-width="5"/>'
            f'<rect x="{x + w * 0.42:.0f}" y="{suelo - h * 0.35:.0f}" width="{w * 0.16:.0f}" height="{h * 0.35:.0f}" fill="#7d4f2a"/>')
barrio = ['<rect x="-500" y="-2000" width="2100" height="5000" fill="url(#cieloOcaso)"/>', nubes(-400, -1600, 5, 51, 1800, 600, 1.6, 0.7),
          '<rect x="-500" y="1500" width="2100" height="1500" fill="#6fae5a"/>']
for i, (x, w, h, p_, t_) in enumerate(((-120, 260, 200, "#f4e2c8", "#c65b46"), (180, 240, 230, "#dfe8ee", "#8a3a2a"), (650, 260, 200, "#f6d7b0", "#b8442f"), (930, 240, 220, "#e8f0d8", "#c65b46"))):
    barrio.append(casita(x, 1520, w, h, p_, t_, i))
barrio.append(arbol(560, 1530, 0.9) + arbol(-140, 1540, 0.8, "#2f8a3a") + arbol(1180, 1530, 0.9, "#2f8a3a"))
barrio.append('<g id="casaX">' + casita(360, 1560, 300, 260, "#fbefd8", "#d8442f", 9) + '<rect x="560" y="1170" width="40" height="80" fill="#8a3a2a"/></g>')
barrio.append('<g id="gato19"><ellipse cx="460" cy="1270" rx="30" ry="18" fill="#2a2a2a"/><circle cx="488" cy="1252" r="15" fill="#2a2a2a"/><path d="M478,1240 L482,1226 L490,1238 Z M492,1238 L500,1226 L502,1242 Z" fill="#2a2a2a"/><path d="M432,1270 Q412,1250 420,1232" stroke="#2a2a2a" stroke-width="7" fill="none"/><circle cx="494" cy="1252" r="3" fill="#ffcf4d"/></g>')
barrio.append('<g id="av6g"><g transform="translate(-260,-1500) scale(0.42)">' + avion("av6", corte=False) + '</g></g>')
barrio.append('<g id="bloque19" opacity="0">' + bloque_hielo(44, -1006, 0.55) + '</g>')
barrio.append('<g id="impacto19" opacity="0">' + "".join(f'<rect class="teja" x="{480 + dx}" y="{1190 + dy}" width="40" height="22" fill="#d8442f" transform="rotate({dx} {500 + dx} {1200 + dy})"/>' for dx, dy in ((-60, 0), (-20, -20), (20, -10), (60, 10), (0, 20))) + '<circle cx="510" cy="1200" r="160" fill="url(#brilloBlanco)"/></g>')
escena("e19", "".join(barrio))
mostrar("e19", f19, DUR)
ts = P("suelta"); tt9 = P("tejado")
J(f'tl.fromTo("#av6g", {{x:-200, y:0, rotation:0}}, {{x:700, y:260, rotation:4, svgOrigin:"300 -1100", duration:{tt9 - f19 + 0.4:.2f}, ease:"none", immediateRender:false}}, {f19:.2f});')
J(f'tl.set("#bloque19", {{opacity:1, x:0, y:0}}, {f19:.2f}); tl.fromTo("#bloque19", {{x:-200, y:0}}, {{x:{-200 + 900 * (ts - f19) / (tt9 - f19 + 0.4):.0f}, y:{260 * (ts - f19) / (tt9 - f19 + 0.4):.0f}, duration:{ts - f19:.2f}, ease:"none", immediateRender:false}}, {f19:.2f});')
J(f'tl.to("#bloque19", {{x:466, y:2190, rotation:200, svgOrigin:"44 -960", duration:{tt9 - ts + 0.05:.2f}, ease:"power2.in"}}, {ts:.2f});')
camara("e19", f19, ts, enfoca(300, -700, 0.85), enfoca(420, -600, 0.85), "sine.inOut")
J(f'tl.to("#e19-cam", {{x:{enfoca(510, 1150, 1.05)[0]}, y:{enfoca(510, 1150, 1.05)[1]}, scale:1.05, duration:{tt9 - ts + 0.05:.2f}, ease:"power2.in"}}, {ts:.2f});')
J(f'tl.to("#gato19", {{y:-40, duration:0.2, ease:"power2.out"}}, {tt9 - 0.25:.2f});')
ti = tt9 + 0.05                                          # el bloque toca el tejado
tc = ti + 0.3                                            # … y CORTE EN SECO a negro
J(f'tl.set("#impacto19", {{opacity:1}}, {ti:.2f}); tl.set("#bloque19", {{opacity:0}}, {ti + 0.04:.2f});')
J(f'tl.fromTo("#impacto19 .teja", {{x:0, y:0, rotation:0}}, {{x:(i) => (i - 2) * 90, y:(i) => -120 - (i % 2) * 80, rotation:(i) => (i - 2) * 160, transformOrigin:"50% 50%", duration:0.3, ease:"power2.out", immediateRender:false}}, {ti:.2f});')
J(f'tl.fromTo("#e19", {{x:0, y:0}}, {{x:"random(-24,24)", y:"random(-24,24)", duration:0.05, yoyo:true, repeat:5, ease:"none", immediateRender:false}}, {ti:.2f});')
J(f'tl.set("#negroF", {{opacity:0}}, 0); tl.set("#negroF", {{opacity:1}}, {tc:.2f});')
OVR.append('<div id="negroF"></div>')
FX.append(("silba", ts)); FX.append(("final", tc - 0.05))

vida_global(DUR)

for eid_, ab_, iz_, de_ in (("e2", "#e9e2d4", "#ddd3c0", "#c9bfae"), ("e4", "#8a5c4a", None, None), ("e5", "#3a4048", None, None), ("e6", "#dfe8ee", None, None),
                            ("e8", "#3a4048", None, None), ("e14", "#9aa0a6", "#9aa0a6", None), ("e16", "#7a8088", None, None)):
    relleno(eid_, ab_, iz_, de_)
# ------------------------------------------------------------------ subtítulos habituales (arriba, palabra a palabra, recuadro azul en lo importante)
CLAVE = set(norm(w) for w in ["caca", "cadena", "metros", "treinta", "aguantando", "dormidos", "cola", "cinturones", "armario", "pestillo", "turbulencias",
                               "boton", "trampilla", "rugido", "aire", "presion", "aspiradora", "segundo", "limpia", "tuberias", "pasajeros", "deposito",
                               "camion", "manguera", "valvula", "minutos", "azul", "gotea", "congela", "hielo", "suelta", "tejado"])
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
#gancho{{position:absolute;left:0;right:0;top:1150px;text-align:center;z-index:20}}
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

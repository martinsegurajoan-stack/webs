#!/usr/bin/env python3
"""«¿Y si mañana apareciera una puerta delante de cada persona?» — animado por código (HyperFrames + GSAP), estilo
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

# ================================================================== 1) GANCHO: 08:59:58 → 09:00 y la puerta aparece en mitad de la calle
SU = 1500                                            # suelo de la calle
TAP = P("aparecera")
e1 = ['<rect width="1080" height="1920" fill="url(#noche)"/>',
      polvo("st1", 90, 0, 1080, 0, 700, "#cfe0ff", 11, 1.6),
      skyline(5, SU, 1.0, "#060a10", "#09101a", 0.16),
      niebla(1050, 520, op=0.16),
      f'<rect x="-200" y="{SU}" width="1480" height="700" fill="url(#suelo)"/>',
      f'<path d="M540,{SU} L-400,1920 M540,{SU} L1480,1920" stroke="#1a2430" stroke-width="5"/>'
      + "".join(f'<path d="M{540 - 18 * k},{SU + 20 + k * k * 9} L{540 - 22 * k},{SU + 40 + k * k * 11}" stroke="#c9a24a" stroke-opacity="0.45" stroke-width="{2 + k}"/>' for k in range(1, 10)),
      '<g id="aparece1" opacity="0">' + puerta("p1", 540, SU, 200, 420, "oro", abre=0.18) + '</g>',
      '<rect id="raya1" x="538" y="1080" width="4" height="420" fill="#fff6e0" opacity="0"/>',
      '<g id="refl1" opacity="0"><path d="M470,1505 L610,1505 L700,1920 L380,1920 Z" fill="url(#cono_oro)" opacity="0.6"/></g>',
      persona(250, SU + 40, 230, rim="#ffd27a", pid="tr1"), persona(830, SU + 70, 260, rim="#ffd27a", pid="tr2", lado=-1),
      polvo("pv1", 70, 380, 700, 1050, 1520, "#ffe2b0", 4)]
# más puertas que se encienden por toda la ciudad al decir «planeta»
r_ = random.Random(21)
mini = ""
for k in range(34):
    y = r_.uniform(1330, 1490); s = 0.05 + (y - 1330) / 160 * 0.12
    x = r_.uniform(-40, 1120)
    if abs(x - 540) < 140: x += 300 if x > 540 else -300
    mini += f'<g class="mini1" transform="translate({x:.0f},{y:.0f}) scale({s:.2f})">' + puerta(f"m1_{k}", 0, 0, 200, 420, r_.choice(("oro", "oro", "frio", "cian")), haz=0.5) + '</g>'
e1.insert(4, f'<g id="minis1">{mini}</g>')
escena("e1", "".join(e1))
mostrar("e1", 0, F(2))
camara("e1", 0, F(2), (0, -40, 1.12), (0, 30, 1.0), "sine.inOut")
OVR.append('<div id="reloj"><div class="rk">MAÑANA</div><div class="rn"><span id="rh">08:59:</span><span id="rs">58</span></div></div>')
J('tl.fromTo("#reloj", {scale:1.08, opacity:1}, {scale:1, duration:0.5, ease:"power3.out", immediateRender:false}, 0);')
J(f'tl.set("#rs", {{innerHTML:"<b>59</b>"}}, 0.85); tl.set("#rs", {{innerHTML:"<b>58</b>"}}, 0); tl.set("#rh", {{innerHTML:"<b>09:00:</b>"}}, {TAP - 0.1:.2f}); tl.set("#rs", {{innerHTML:"<b>00</b>"}}, {TAP - 0.1:.2f}); tl.set("#rh", {{innerHTML:"<b>08:59:</b>"}}, 0);')
J(f'tl.fromTo("#reloj .rn", {{color:"#ffffff"}}, {{color:"{ORO}", textShadow:"0 0 40px {ORO}", duration:0.3, immediateRender:false}}, {TAP - 0.1:.2f});')
J(f'tl.to("#reloj", {{opacity:0, y:-30, duration:0.4, ease:"power2.in"}}, {P("planeta") - 0.2:.2f});')
J(f'tl.fromTo("#raya1", {{opacity:0, scaleY:0}}, {{opacity:1, scaleY:1, transformOrigin:"50% 100%", duration:0.35, ease:"power3.out", immediateRender:false}}, {TAP - 0.2:.2f}); tl.to("#raya1", {{opacity:0, scaleX:40, duration:0.4, ease:"power2.in"}}, {TAP + 0.15:.2f});')
J(f'tl.fromTo("#aparece1", {{opacity:0, scaleX:0.05, svgOrigin:"540 1500"}}, {{opacity:1, scaleX:1, svgOrigin:"540 1500", duration:0.55, ease:"expo.out", immediateRender:false}}, {TAP + 0.2:.2f}); tl.to("#refl1", {{opacity:1, duration:0.6}}, {TAP + 0.3:.2f});')
J(f'tl.fromTo("#e1-cam", {{x:0}}, {{x:10, duration:0.06, yoyo:true, repeat:5, ease:"none", immediateRender:false}}, {TAP + 0.2:.2f});')
J(f'tl.set(".mini1", {{opacity:0}}, 0); tl.to(".mini1", {{opacity:1, duration:0.12, stagger:{{each:0.05, from:"random"}}}}, {P("cada") - 0.2:.2f});')
J(f'tl.to("#tr1", {{x:-30, duration:2.5, ease:"sine.inOut"}}, {TAP:.2f}); tl.to("#tr2", {{x:25, duration:2.5, ease:"sine.inOut"}}, {TAP:.2f});')
mover_polvo("pv1", 0, F(2), -140, 20)
FX.append(("tic", 0.0)); FX.append(("tic", 0.85)); FX.append(("aparece", TAP - 0.25))

# ================================================================== 2) CASA · TRABAJO · CALLE: un único travelling por un corte de edificio (sin cortes)
W2 = 3240
def salon(x0):
    return (f'<rect x="{x0}" y="560" width="1080" height="1100" fill="#0a0f15"/>'
            f'<rect x="{x0 + 90}" y="700" width="300" height="380" fill="#0d2232"/><path d="M{x0 + 240},700 L{x0 + 240},1080 M{x0 + 90},890 L{x0 + 390},890" stroke="#05080c" stroke-width="10"/>'
            + '<g clip-path="url(#vent2)">' + skyline(31, 1080, 0.32, "#081520", "#0a1a28", 0.3, 300, x0 + 90) + '</g>'
            + f'<rect x="{x0 + 60}" y="1360" width="420" height="120" rx="20" fill="#121a24"/><rect x="{x0 + 60}" y="1300" width="420" height="80" rx="18" fill="#17212d"/>'
            f'<rect x="{x0 + 560}" y="1100" width="140" height="10" fill="#1a2430"/><path d="M{x0 + 630},1110 L{x0 + 630},1480" stroke="#1a2430" stroke-width="8"/>'
            f'<ellipse cx="{x0 + 630}" cy="1090" rx="60" ry="20" fill="#ffcf7a" opacity="0.25"/>'
            + persona(x0 + 270, 1400, 210, rim="#ffd27a", lado=-1)
            + puerta(f"p2a", x0 + 860, 1480, 190, 400, "oro"))
def oficina(x0):
    mesas = "".join(f'<g><rect x="{x0 + 80 + i * 300}" y="{1230 - j * 120}" width="220" height="16" fill="#1a2430"/><rect x="{x0 + 120 + i * 300}" y="{1150 - j * 120}" width="120" height="78" rx="4" fill="#0f2a3a"/>'
                    f'<rect x="{x0 + 126 + i * 300}" y="{1156 - j * 120}" width="108" height="66" fill="#3a9bd0" opacity="0.35"/></g>' for i in range(3) for j in range(2))
    return (f'<rect x="{x0}" y="560" width="1080" height="1100" fill="#091017"/>'
            + "".join(f'<rect x="{x0 + 40 + k * 260}" y="600" width="200" height="12" fill="#cfe6ff" opacity="0.18"/>' for k in range(4))
            + mesas + persona(x0 + 330, 1480, 250, rim="#9fdcff") + puerta("p2b", x0 + 760, 1480, 200, 420, "frio"))
def calle2(x0):
    return (f'<rect x="{x0}" y="0" width="1080" height="1920" fill="url(#noche)"/>' + skyline(41, 1480, 0.9, "#060a10", "#09101a", 0.18, 1080, x0)
            + f'<rect x="{x0}" y="1480" width="1080" height="440" fill="url(#suelo)"/>'
            + f'<rect x="{x0 + 120}" y="1080" width="14" height="400" fill="#1a2430"/><rect x="{x0 + 98}" y="1030" width="58" height="140" rx="10" fill="#10161e"/><circle id="sem2" cx="{x0 + 127}" cy="1060" r="16" fill="#ff3b2f"/>'
            + persona(x0 + 350, 1500, 240, rim="#ffd27a") + puerta("p2c", x0 + 640, 1480, 210, 440, "oro"))
DEFS.append('<clipPath id="vent2"><rect x="90" y="700" width="300" height="380"/></clipPath>')
e2 = [f'<rect width="{W2}" height="1920" fill="#030409"/>', salon(0), oficina(1080), calle2(2160),
      f'<rect x="1068" y="520" width="24" height="1180" fill="#1b232d"/><rect x="2148" y="520" width="24" height="1180" fill="#1b232d"/>',
      f'<rect x="0" y="520" width="2160" height="40" fill="#1b232d"/><rect x="0" y="1660" width="2160" height="60" fill="#1b232d"/>',
      polvo("pv2", 200, 0, W2, 600, 1600, "#ffe2b0", 8, 2.2)]
escena("e2", "".join(e2), W2)
mostrar("e2", F(2), F(5))
J(f'tl.fromTo("#e2-cam", {{x:0, scale:1.0}}, {{x:0, scale:1.0, duration:0.1, immediateRender:false}}, {F(2):.2f});')
J(f'tl.to("#e2-cam", {{x:-1080, duration:0.85, ease:"power3.inOut"}}, {P("trabajo") - 0.45:.2f}); tl.to("#e2-cam", {{x:-2160, duration:0.85, ease:"power3.inOut"}}, {P("calle") - 0.5:.2f});')
J(f'tl.fromTo("#e2-cam", {{y:0}}, {{y:-20, duration:{F(4) - F(2):.2f}, ease:"none", immediateRender:false}}, {F(2):.2f});')
for k, w in (("casa", "casa"), ("trabajo", "trabajo"), ("calle", "calle")):
    FX.append(("paso", P(w) - 0.4))
mover_polvo("pv2", F(2), F(5), -100, 40)
# 3) «Y detrás de ella…»: la cámara se acerca a la puerta de la calle hasta que la luz lo llena todo
J(f'tl.to("#e2-cam", {{x:{-2160 * 3.4 - 3.4 * (640 - 540):.0f}, y:{-3.4 * (1270 - 960):.0f}, scale:3.4, duration:{F(5) - P("detras") - 0.1:.2f}, ease:"power2.in"}}, {P("detras"):.2f});')
J(f'tl.to("#p2c .hoja", {{scaleX:0.18, transformOrigin:"0% 0%", duration:2.2, ease:"power2.inOut"}}, {P("encontraras"):.2f});')
FX.append(("riser", F(5) - 1.6))
luz(F(5))

# ================================================================== 4) NADIE ENTIENDE: pasillo 307, alguien intenta abrir, luces de policía
f4 = F(5)
VP = (540, 1020)                                      # punto de fuga del pasillo
def q(*pts): return " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)
e4 = ['<rect width="1080" height="1920" fill="#040508"/>',
      f'<polygon points="{q((0, 0), (1080, 0), (640, 930), (440, 930))}" fill="#07090d"/>',
      f'<polygon points="{q((0, 0), (440, 930), (440, 1110), (0, 1920))}" fill="url(#pared4)"/>',
      f'<polygon points="{q((1080, 0), (640, 930), (640, 1110), (1080, 1920))}" fill="url(#pared4b)"/>',
      f'<polygon points="{q((0, 1920), (440, 1110), (640, 1110), (1080, 1920))}" fill="url(#moqueta)"/>',
      f'<rect x="440" y="930" width="200" height="180" fill="#0b0d12"/><rect x="505" y="975" width="70" height="135" fill="#120f0c"/>',
      '<ellipse cx="540" cy="945" rx="30" ry="8" fill="#ffe6b0" opacity="0.8"/><path d="M500,950 L580,950 L640,1110 L440,1110 Z" fill="#ffe6b0" opacity="0.05"/>',
      "".join(f'<path d="M{x1:.0f},{y1:.0f} L{x2:.0f},{y2:.0f}" stroke="#2a2016" stroke-width="5" opacity="0.6"/>' for x1, y1, x2, y2 in ((0, 1180, 440, 1050), (1080, 1180, 640, 1050))),
      # puerta 307 en primer plano a la derecha (en perspectiva) con luz por debajo y por el canto
      '<polygon points="760,610 1000,470 1000,1520 760,1340" fill="#1a120c"/><polygon points="772,628 988,500 988,1500 772,1330" fill="#24180f"/>',
      '<polygon id="rend4" points="1000,470 1012,466 1012,1528 1000,1520" fill="#ffb14a"/>',
      '<polygon id="bajo4" points="760,1340 1000,1520 1080,1600 1080,1920 600,1920" fill="url(#luzBajo)" opacity="0.9"/>',
      '<text x="880" y="700" text-anchor="middle" font-family="Georgia" font-size="46" fill="#c9a24a" transform="skewY(-30) translate(0,505)">307</text>',
      '<g id="pomo4"><rect x="800" y="1010" width="40" height="12" rx="6" fill="#c9a24a"/><circle cx="800" cy="1016" r="12" fill="#c9a24a"/></g>',
      persona(560, 1700, 520, rim="#ffb14a", pid="hom4", brazo=-62, lado=1),
      '<rect id="sirR" width="1080" height="1920" fill="url(#sirenaR)" opacity="0"/><rect id="sirA" width="1080" height="1920" fill="url(#sirenaA)" opacity="0"/>',
      '<g id="movil4" opacity="0"><rect x="456" y="1270" width="46" height="84" rx="8" fill="#9fdcff"/><rect x="456" y="1270" width="46" height="84" rx="8" fill="#ffffff" opacity="0.4"/></g>',
      polvo("pv4", 60, 600, 1080, 900, 1700, "#ffcf8a", 5, 1.8)]
grad_lin("pared4", ((0, "#120d0a", 1), (1, "#07060a", 1)), 0, 0, 1, 0)
grad_lin("pared4b", ((0, "#07060a", 1), (1, "#140e0a", 1)), 0, 0, 1, 0)
grad_lin("moqueta", ((0, "#0d0907", 1), (1, "#2a1a10", 1)))
grad_rad("luzBajo", ((0, "#ffb14a", 0.85), (0.6, "#ff8a2a", 0.25), (1, "#ff8a2a", 0)), 0.75, 0.15, 0.7)
grad_rad("sirenaR", ((0, "#ff2a2a", 0.55), (1, "#ff2a2a", 0)), 0.1, 0.3, 0.8)
grad_rad("sirenaA", ((0, "#2a6bff", 0.55), (1, "#2a6bff", 0)), 0.9, 0.3, 0.8)
escena("e4", "".join(e4))
mostrar("e4", f4, F(8))
camara("e4", f4, F(8), (60, 30, 1.12), (-30, -10, 1.02), "sine.inOut")
J(f'tl.fromTo("#hom4", {{x:-340}}, {{x:0, duration:1.6, ease:"power2.out", immediateRender:false}}, {f4:.2f});')
J(f'tl.to("#hom4 .brazo", {{rotation:-80, duration:0.35, ease:"power2.out"}}, {P("abrirla") - 0.6:.2f});')
J(f'tl.fromTo("#pomo4", {{rotation:0}}, {{rotation:-28, svgOrigin:"800 1016", duration:0.12, yoyo:true, repeat:5, ease:"sine.inOut", immediateRender:false}}, {P("abrirla") - 0.3:.2f});')
J(f'tl.fromTo("#rend4, #bajo4", {{opacity:0.9}}, {{opacity:0.55, duration:0.16, yoyo:true, repeat:{int((F(8) - f4) / 0.3)}, ease:"sine.inOut", immediateRender:false}}, {f4:.2f});')
J(f'tl.to("#movil4", {{opacity:1, duration:0.3}}, {P("llaman") - 0.2:.2f}); tl.to("#hom4 .brazo", {{rotation:-20, duration:0.3}}, {P("llaman") - 0.3:.2f});')
J(f'tl.to("#sirR", {{opacity:1, duration:0.25, yoyo:true, repeat:5, ease:"sine.inOut"}}, {P("policia") - 0.2:.2f}); tl.to("#sirA", {{opacity:1, duration:0.25, yoyo:true, repeat:5, ease:"sine.inOut"}}, {P("policia") + 0.05:.2f});')
mover_polvo("pv4", f4, F(8), -90, -20)
FX.append(("pomo", P("abrirla") - 0.3)); FX.append(("sirena", P("policia") - 0.3))

# ================================================================== 5) CADA PUERTA ES DIFERENTE: galería infinita de puertas de colores (travelling lateral)
f5 = F(8)
cols = ("oro", "frio", "verde", "rojo", "lila", "cian", "oro", "frio", "verde")
e5 = ['<rect width="2600" height="1920" fill="#030508"/>', '<rect x="0" y="1480" width="2600" height="440" fill="url(#suelo)"/>', niebla(1100, 500, op=0.12, w=2600)]
for k, c in enumerate(cols):
    x = 220 + k * 280
    e5.append(puerta(f"p5_{k}", x, 1480, 170, 380, c, abre=0.0, haz=0.85))
    if k % 2 == 0:
        e5.append(persona(x - 10, 1560, 200, rim=PAL[c][1], lado=1))
e5.append(polvo("pv5", 160, 0, 2600, 900, 1600, "#ffffff", 9, 1.6))
escena("e5", "".join(e5), 2600)
mostrar("e5", f5, F(9))
camara("e5", f5, F(9), (-100, -260, 1.3), (-1700, -300, 1.36), "sine.inOut")
J(f'tl.to("#e5 .hoja", {{scaleX:0.2, transformOrigin:"0% 0%", duration:0.6, stagger:0.12, ease:"power2.inOut"}}, {P("diferente") - 0.7:.2f});')
FX.append(("puertas", P("diferente") - 0.7))

# ================================================================== 6) DINERO: LA MISMA puerta se abre y al otro lado hay una sala llena de dinero
f6 = F(9)
C6, S6, W6, H6 = 540, 1460, 380, 820
hx6, hy6, hw6 = C6 - W6 / 2 + W6 * 0.07, S6 - H6 + W6 * 0.07, W6 * 0.86
r6 = random.Random(61)
def fajo(x, y, s=1.0):
    return (f'<g transform="translate({x:.0f},{y:.0f}) scale({s:.2f})"><rect x="-30" y="-9" width="60" height="18" rx="2" fill="#cfd5ad"/><rect x="-30" y="-9" width="60" height="5" fill="#e7ecc6"/>'
            f'<rect x="-30" y="-9" width="60" height="18" rx="2" fill="none" stroke="#8b9168" stroke-width="1.5"/><rect x="-6" y="-9" width="12" height="18" fill="#d8a84a"/></g>')
pilas = ""
for j_ in range(7):                                   # pilas ordenadas de fajos, de fondo a primer plano
    y = S6 - 300 + j_ * 46; sc = 0.55 + j_ * 0.12
    for i_ in range(-4, 5):
        x = C6 + i_ * 70 * sc + r6.uniform(-6, 6)
        for k_ in range(r6.randint(2, 5)):
            pilas += fajo(x, y - k_ * 13 * sc, sc)
monedas6 = "".join(f'<ellipse cx="{r6.uniform(hx6, hx6 + hw6):.0f}" cy="{S6 - r6.uniform(0, 70):.0f}" rx="9" ry="4" fill="#ffcf5a" stroke="#b88a22" stroke-width="1.5"/>' for _ in range(90))
volando6 = "".join(f'<g class="bill6" transform="translate({r6.uniform(hx6, hx6 + hw6):.0f},{r6.uniform(hy6, S6 - 400):.0f})"><rect x="-22" y="-8" width="44" height="16" rx="2" fill="#dfe3bd" opacity="0.92"/></g>' for _ in range(18))
interior6 = (f'<rect x="{hx6:.0f}" y="{hy6:.0f}" width="{hw6:.0f}" height="{H6:.0f}" fill="url(#oroFondo)"/>'
             f'<path d="M{C6},{hy6:.0f} L{hx6 - 60:.0f},{S6} L{hx6 + hw6 + 60:.0f},{S6} Z" fill="url(#rayos6)" opacity="0.45"/>'
             f'<rect x="{hx6:.0f}" y="{S6 - 330:.0f}" width="{hw6:.0f}" height="330" fill="#b7782a" opacity="0.35"/>' + pilas + monedas6 + volando6)
e6 = ['<rect width="1080" height="1920" fill="#06080c"/>', '<rect x="0" y="1460" width="1080" height="460" fill="url(#suelo)"/>',
      '<rect x="0" y="0" width="1080" height="1460" fill="url(#muro)"/>',
      puerta("p6", C6, S6, W6, H6, "oro", interior=interior6),
      persona(540, 1760, 560, rim="#ffd27a", pid="hom6"), polvo("pv6", 120, 250, 830, 600, 1600, "#fff1c0", 6, 2.4)]
grad_lin("oroFondo", ((0, "#fff3d0", 1), (0.45, "#ffc65a", 1), (1, "#a8620e", 1)))
grad_lin("rayos6", ((0, "#ffffff", 0.9), (1, "#ffffff", 0)))
escena("e6", "".join(e6))
mostrar("e6", f6, F(10))
camara("e6", f6, F(10), enfoca(540, 1150, 1.0), enfoca(540, 1110, 1.2), "sine.inOut")
J(f'tl.fromTo("#p6 .hoja", {{scaleX:1}}, {{scaleX:0.14, transformOrigin:"0% 0%", duration:1.2, ease:"power3.inOut", immediateRender:false}}, {f6 + 0.05:.2f});')
J(f'tl.fromTo("#p6 .halo, #p6 .cono", {{opacity:0.25}}, {{opacity:1, duration:1.2, immediateRender:false}}, {f6 + 0.05:.2f});')
J(f'tl.fromTo(".bill6", {{y:-120, rotation:0}}, {{y:420, rotation:(i) => (i % 2 ? 1 : -1) * (90 + i * 11), duration:2.8, stagger:0.08, ease:"none", immediateRender:false}}, {f6 + 0.6:.2f});')
J(f'tl.fromTo("#hom6", {{y:0, scale:1}}, {{y:-70, scale:0.86, svgOrigin:"540 1760", duration:{F(10) - f6 - 0.6:.2f}, ease:"power1.inOut", immediateRender:false}}, {f6 + 0.6:.2f});')
mover_polvo("pv6", f6, F(10), -160, 10)
FX.append(("puertaAbre", f6 + 0.05)); FX.append(("monedas", P("dinero") - 0.2))

# ================================================================== 7) REENCUENTRO: abrazo bien construido en el umbral (sin solaparse)
f7 = F(10)
e7 = ['<rect width="1080" height="1920" fill="#06080c"/>', '<rect x="0" y="0" width="1080" height="1460" fill="url(#muro)"/>', '<rect x="0" y="1460" width="1080" height="460" fill="url(#suelo)"/>',
      puerta("p7", 540, 1460, 420, 900, "oro", abre=0.7),
      persona(470, 1500, 560, rim="#ffd27a", pid="a7"), persona(612, 1495, 590, rim="#fff1d6", pid="b7", lado=-1),
      polvo("pv7", 140, 200, 880, 500, 1500, "#ffe2b0", 12, 2.2)]
escena("e7", "".join(e7))
mostrar("e7", f7, F(11))
camara("e7", f7, F(11), enfoca(540, 1150, 1.05), enfoca(545, 1130, 1.22), "sine.inOut")
J(f'tl.fromTo("#b7", {{x:110, opacity:0}}, {{x:0, opacity:1, duration:1.0, ease:"power2.out", immediateRender:false}}, {f7 + 0.05:.2f});')
J(f'tl.to("#a7 .brazo, #b7 .brazo", {{rotation:-58, duration:0.55, ease:"power2.out"}}, {f7 + 0.95:.2f}); tl.set("#a7 .brazo, #b7 .brazo", {{rotation:0}}, 0);')
mover_polvo("pv7", f7, F(11), -120, 15)

# ================================================================== 8) LA VIDA SOÑADA: la puerta se abre y al otro lado hay sol, mar y una villa
f8 = F(11)
vista = ('<rect x="330" y="560" width="420" height="900" fill="url(#cieloDia)"/><circle cx="640" cy="760" r="60" fill="#fff4d0"/><circle cx="640" cy="760" r="130" fill="#fff4d0" opacity="0.25"/>'
         '<rect x="330" y="1020" width="420" height="160" fill="#2f8fc8"/><rect x="330" y="1020" width="420" height="8" fill="#bfe8ff" opacity="0.8"/>'
         '<rect x="380" y="900" width="230" height="120" fill="#f4f1ea"/><rect x="420" y="930" width="60" height="50" fill="#7fc3e0"/><rect x="510" y="930" width="60" height="50" fill="#7fc3e0"/><rect x="370" y="890" width="250" height="14" fill="#e2ddd2"/>'
         '<rect x="330" y="1180" width="420" height="280" fill="#e9dcc2"/><rect x="380" y="1210" width="300" height="90" rx="10" fill="#36b6e0"/><rect x="380" y="1210" width="300" height="12" fill="#bdf0ff"/>'
         '<path d="M700,1180 C700,1060 690,980 705,900" stroke="#5a3a22" stroke-width="12" fill="none"/>'
         + "".join(f'<path d="M705,900 q{a},-20 {b},{c}" stroke="#2f8a3a" stroke-width="14" fill="none" stroke-linecap="round"/>' for a, b, c in ((-60, -110, 30), (60, 110, 30), (-20, -80, -40), (30, 90, -30))))
DEFS.append('<clipPath id="hueco8"><rect x="330" y="560" width="420" height="900"/></clipPath>')
hoja8 = ('<g id="hoja8"><rect x="330" y="560" width="420" height="900" fill="#141821"/>'
         '<rect x="389" y="623" width="302" height="324" fill="none" stroke="#ffffff" stroke-opacity="0.07" stroke-width="3"/><rect x="389" y="1010" width="302" height="342" fill="none" stroke="#ffffff" stroke-opacity="0.07" stroke-width="3"/>'
         '<circle cx="700" cy="1055" r="9" fill="#c9a24a"/><rect x="746" y="560" width="4" height="900" fill="#fff4d0" opacity="0.9"/></g>')
e8 = ['<rect width="1080" height="1920" fill="#05090d"/>', '<polygon points="0,0 330,560 330,1460 0,1920" fill="#081016"/><polygon points="1080,0 750,560 750,1460 1080,1920" fill="#091218"/>',
      '<polygon points="0,1920 330,1460 750,1460 1080,1920" fill="#0b1218"/>',
      f'<g clip-path="url(#hueco8)">{vista}{hoja8}</g>', '<rect x="310" y="540" width="460" height="920" fill="none" stroke="#10161e" stroke-width="40"/>',
      '<polygon id="luz8" points="330,1460 750,1460 1080,1920 0,1920" fill="url(#luzDia)" opacity="0"/>',
      persona(300, 1880, 760, rim="#fff1c0", pid="jov8", lado=1)]
grad_lin("cieloDia", ((0, "#4aa6e8", 1), (1, "#cfeeff", 1)))
grad_lin("luzDia", ((0, "#fff4d0", 0.8), (1, "#fff4d0", 0)))
escena("e8", "".join(e8))
mostrar("e8", f8, F(12))
camara("e8", f8, F(12), enfoca(540, 1100, 1.15), enfoca(540, 1010, 1.0), "sine.out")
J(f'tl.fromTo("#hoja8", {{scaleX:1}}, {{scaleX:0.1, transformOrigin:"0% 0%", duration:1.4, ease:"power3.inOut", immediateRender:false}}, {f8 + 0.15:.2f}); tl.to("#luz8", {{opacity:0.6, duration:1.2}}, {f8 + 0.3:.2f});')
J(f'tl.fromTo("#jov8", {{x:-120}}, {{x:0, duration:2.2, ease:"power2.out", immediateRender:false}}, {f8:.2f});')
FX.append(("puertaAbre", f8 + 0.15)); FX.append(("olas", f8 + 0.8))

# ================================================================== 9) LA REGLA: la luz se vuelve roja; quien cruza desaparece
f9 = F(12)
e9 = ['<rect width="1080" height="1920" fill="#030305"/>', '<rect x="0" y="1460" width="1080" height="460" fill="url(#suelo)"/>',
      '<g id="dor9">' + puerta("p9o", 540, 1460, 300, 660, "oro", abre=0.75) + '</g>',
      '<g id="roj9" opacity="0">' + puerta("p9r", 540, 1460, 300, 660, "rojo", abre=0.75) + '</g>',
      persona(540, 1640, 430, rim="#ffd27a", pid="cru9"), polvo("pv9", 120, 250, 830, 700, 1600, "#ffb0a0", 13, 2.0)]
escena("e9", "".join(e9))
mostrar("e9", f9, F(15))
camara("e9", f9, F(15), enfoca(540, 1150, 1.0), enfoca(540, 1130, 1.35), "sine.inOut")
J(f'tl.to("#roj9", {{opacity:1, duration:0.8, ease:"power2.inOut"}}, {P("condicion") - 0.3:.2f}); tl.to("#dor9", {{opacity:0, duration:0.8}}, {P("condicion") - 0.3:.2f});')
J(f'tl.fromTo("#cru9", {{y:0, scale:1, opacity:1}}, {{y:-140, scale:0.62, svgOrigin:"540 1640", duration:1.6, ease:"power1.inOut", immediateRender:false}}, {P("saberlo") - 0.2:.2f}); tl.to("#cru9", {{opacity:0, duration:0.25}}, {P("cruzas"):.2f});')
J(f'tl.to("#p9r .halo", {{opacity:1, scale:1.2, svgOrigin:"540 1160", duration:0.2, yoyo:true, repeat:1}}, {P("cruzas"):.2f});')
mover_polvo("pv9", f9, F(15), -110, -10)
nota("LO QUE MÁS DESEAS", P("conseguir") - 0.2, F(15) - 0.2, 60, 500, ORO)
nota("A CAMBIO DE ALGO", P("cambio") - 0.4, F(15) - 0.2, 60, 600, RED, "no eliges qué · no lo sabes hasta cruzar")
FX.append(("golpe", P("condicion") - 0.25)); FX.append(("golpe2", P("cruzas") + 0.05))
negro(F(15))

# ================================================================== 10) MILLONES CRUZAN: la ciudad desde arriba, colas de gente hacia las puertas
f10 = F(15)
r_ = random.Random(5)
manz = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{r_.choice(("#0b1219", "#0d151d", "#09101a"))}" stroke="#141f2a" stroke-width="3"/>'
               + "".join(f'<rect x="{x + 8 + i * 18}" y="{y + 8 + j * 18}" width="8" height="8" fill="#ffcf7a" opacity="{r_.uniform(0.1, 0.6):.2f}"/>' for i in range(max(1, (w - 10) // 18)) for j in range(max(1, (h - 10) // 18)) if r_.random() < 0.12)
               for x in range(-300, 1400, 170) for y in range(200, 2100, 170) for w, h in [(r_.randint(110, 150), r_.randint(110, 150))])
calles = "".join(f'<path d="M{x},150 L{x},2150" stroke="#1d2a36" stroke-width="16"/>' for x in range(-150, 1400, 170)) + "".join(f'<path d="M-350,{y} L1450,{y}" stroke="#1d2a36" stroke-width="16"/>' for y in range(350, 2150, 170))
pts10 = [(-150 + 170 * i, 350 + 170 * j) for i in range(10) for j in range(11)]
r_.shuffle(pts10)
pts10 = pts10[:60]
pu10 = "".join(f'<g class="pu10"><circle cx="{x}" cy="{y}" r="58" fill="url(#halo_{c})"/><rect x="{x - 5}" y="{y - 10}" width="10" height="20" fill="{PAL[c][1]}"/></g>' for (x, y), c in zip(pts10, [r_.choice(("oro", "oro", "frio", "rojo", "verde")) for _ in pts10]))
gente10 = "".join(f'<circle class="ge10" cx="{x + r_.uniform(-60, 60):.0f}" cy="{y + r_.uniform(-60, 60):.0f}" r="4.5" fill="#e9eef5" data-x="{x}" data-y="{y}"/>' for x, y in pts10 for _ in range(5))
e10 = ['<rect x="-400" y="0" width="1880" height="2300" fill="#05080c"/>', calles, manz, pu10, gente10, niebla(0, 1920, op=0.1)]
escena("e10", "".join(e10))
mostrar("e10", f10, F(19))
camara("e10", f10, F(19), (0, 0, 1.0), (0, -60, 1.25), "sine.inOut")
J(f'tl.set(".pu10", {{opacity:0}}, 0); tl.to(".pu10", {{opacity:1, duration:0.2, stagger:{{each:0.03, from:"random"}}}}, {f10 + 0.2:.2f});')
J(f'tl.to(".ge10", {{attr:{{cx:(i, el) => el.dataset.x, cy:(i, el) => el.dataset.y}}, opacity:0, duration:2.2, stagger:{{each:0.02, from:"random"}}, ease:"power1.in"}}, {P("cruzar") - 0.6:.2f});')
OVR.append(f'<div id="cnt10" class="nota" style="left:60px;top:500px;--c:{ORO}"><b></b><span class="cs">HAN CRUZADO</span><span class="cn" id="cntn">0</span></div>')
pop("#cnt10", P("millones") - 0.3, 0.4, "opacity:0, x:-30"); fuera("#cnt10", F(19) - 0.15)
J(f'tl.fromTo(window.__cnt = {{v:0}}, {{v:0}}, {{v:48200000, duration:{F(19) - P("millones"):.2f}, ease:"power2.in", immediateRender:false, onUpdate:() => document.getElementById("cntn").textContent = Math.round(window.__cnt.v).toString().replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ".")}}, {P("millones"):.2f});')
nota("MILLONARIOS", P("millonarios") - 0.3, F(17) + 1.6, 60, 650, ORO)
nota("REENCUENTROS", P("recuperan") - 0.2, F(19) - 0.15, 60, 750, "#ffb0a0")
nota("PRIMERAS CONSECUENCIAS", P("consecuencias") - 0.4, F(19) - 0.15, 60, 850, RED)
FX.append(("pulso", f10)); FX.append(("golpe", P("consecuencias") - 0.3))

# ================================================================== 11) EL PRECIO I: un salón de lujo con el dinero… y ya no reconoce a su familia (cálido → frío)
f11 = F(19); tp11 = P("pero", 5)
r11 = random.Random(11)
DEFS.append('<clipPath id="ven11"><rect x="560" y="430" width="440" height="860"/></clipPath>')
mesa = '<rect x="300" y="1430" width="480" height="22" rx="4" fill="#2a1c10"/><rect x="330" y="1452" width="16" height="120" fill="#1a1109"/><rect x="734" y="1452" width="16" height="120" fill="#1a1109"/>'
pilas11 = "".join(fajo(340 + i_ * 70, 1420 - k_ * 13, 1.0) for i_ in range(7) for k_ in range(r11.randint(3, 6)))
e11 = ['<rect width="1080" height="1920" fill="url(#salon11)"/>',
       '<g clip-path="url(#ven11)"><rect x="560" y="430" width="440" height="860" fill="url(#noche)"/>' + skyline(19, 1290, 0.75, "#081018", "#0b1520", 0.3, 440, 560) + '</g>',
       '<rect x="560" y="430" width="440" height="860" fill="none" stroke="#2a1d12" stroke-width="18"/><path d="M780,430 L780,1290 M560,860 L1000,860" stroke="#2a1d12" stroke-width="10"/>',
       '<circle cx="280" cy="470" r="150" fill="url(#halo_oro)" opacity="0.8"/><path d="M280,300 L280,420" stroke="#3a2a18" stroke-width="4"/>'
       + "".join(f'<path d="M{280 + dx},430 l0,{L}" stroke="#ffe7b0" stroke-width="3" opacity="0.8"/>' for dx, L in ((-40, 50), (-20, 70), (0, 80), (20, 70), (40, 50))),
       '<rect x="40" y="1200" width="400" height="160" rx="26" fill="#1c140c"/><rect x="40" y="1150" width="400" height="80" rx="24" fill="#22180e"/>',
       '<rect x="0" y="1560" width="1080" height="360" fill="#0f0a06"/><rect x="0" y="1560" width="1080" height="360" fill="url(#reflejo11)"/>',
       mesa, f'<g id="pila11">{pilas11}</g>',
       '<rect id="frio11" width="1080" height="1920" fill="#06101a" opacity="0" style="mix-blend-mode:color"/>',
       '<rect id="frio11b" width="1080" height="1920" fill="#0a1a2a" opacity="0"/>',
       '<g id="fam11">' + persona(170, 1720, 560, rim="#ffd27a", pid="mu11", lado=1) + persona(300, 1730, 340, rim="#ffd27a", pid="ni11", lado=1) + '</g>',
       persona(880, 1740, 620, rim="#ffd27a", pid="ho11", lado=-1)]
grad_lin("salon11", ((0, "#1a1209", 1), (1, "#0a0704", 1)))
grad_lin("reflejo11", ((0, "#ffcf7a", 0.12), (1, "#ffcf7a", 0)))
escena("e11", "".join(e11))
mostrar("e11", f11, F(20))
camara("e11", f11, F(20), enfoca(540, 1250, 1.0), enfoca(600, 1230, 1.12), "sine.inOut")
J(f'tl.to("#frio11", {{opacity:0.75, duration:1.0, ease:"power2.inOut"}}, {tp11:.2f}); tl.to("#frio11b", {{opacity:0.45, duration:1.0}}, {tp11:.2f}); tl.to("#pila11", {{opacity:0.35, duration:1.0}}, {tp11:.2f});')
J(f'tl.to("#fam11", {{opacity:0.4, filter:"blur(7px)", duration:1.4, ease:"power2.inOut"}}, {P("reconocer") - 0.3:.2f});')
J(f'tl.to("#ho11", {{x:30, duration:1.2, ease:"sine.inOut"}}, {P("reconocer") - 0.2:.2f});')
nota("YA NO RECONOCE A SU FAMILIA", P("reconocer") - 0.2, F(20) - 0.4, 60, 500, ICE)
FX.append(("golpe2", tp11))

# ================================================================== 12) EL PRECIO II: recupera a su pareja… y olvida los recuerdos (las fotos se borran)
f12 = F(20)
fotos = ""
for k, (x, y, a) in enumerate(((150, 640, -6), (430, 600, 4), (720, 650, -3), (260, 930, 5), (560, 900, -5), (820, 960, 6))):
    escena_f = ['<rect x="-90" y="-80" width="180" height="140" fill="#f0b46a"/><circle cx="40" cy="-40" r="22" fill="#fff1c0"/><rect x="-90" y="20" width="180" height="40" fill="#2f6f9a"/>',
                '<rect x="-90" y="-80" width="180" height="140" fill="#4a6a8a"/><rect x="-90" y="10" width="180" height="50" fill="#e9eef5"/>',
                '<rect x="-90" y="-80" width="180" height="140" fill="#2a1a2a"/><circle cx="-40" cy="-30" r="5" fill="#ffd27a"/><circle cx="10" cy="-50" r="4" fill="#ffd27a"/><circle cx="50" cy="-20" r="5" fill="#ffd27a"/>'][k % 3]
    fotos += (f'<g class="foto12" transform="translate({x},{y}) rotate({a})"><rect x="-110" y="-100" width="220" height="230" fill="#f4f1ea"/>{escena_f}'
              f'{persona(-22, 60, 110, col="#14181f")}{persona(22, 60, 104, col="#14181f", lado=-1)}<rect class="borra12" x="-90" y="-80" width="180" height="140" fill="#f4f1ea" opacity="0"/></g>')
e12 = ['<rect width="1080" height="1920" fill="#0b0d12"/>', '<rect id="frio12" width="1080" height="1920" fill="#08121c" opacity="0"/>',
       '<path d="M60,520 Q540,600 1020,520" stroke="#3a3328" stroke-width="3" fill="none"/>' + "".join(f'<circle cx="{x}" cy="{520 + 80 * (1 - ((x - 540) / 480) ** 2) * 0.5:.0f}" r="7" fill="#ffd27a" opacity="0.8"/>' for x in range(100, 1000, 75)),
       fotos, '<rect x="0" y="1480" width="1080" height="440" fill="#07090d"/>',
       persona(330, 1780, 560, rim="#ffd27a", pid="el12", lado=1), persona(760, 1780, 540, rim="#bfeaff", pid="ella12", lado=-1)]
escena("e12", "".join(e12))
mostrar("e12", f12, F(21))
camara("e12", f12, F(21), enfoca(540, 1000, 1.08), enfoca(540, 1060, 1.0), "sine.inOut")
J(f'tl.to(".borra12", {{opacity:1, duration:0.5, stagger:0.28, ease:"power2.in"}}, {P("olvida") - 0.1:.2f}); tl.to("#frio12", {{opacity:0.9, duration:1.0}}, {P("pero", 6) - 0.1:.2f});')
J(f'tl.to("#ella12", {{x:90, duration:1.6, ease:"sine.inOut"}}, {P("olvida"):.2f});')
nota("OLVIDA TODOS SUS RECUERDOS", P("recuerdos") - 0.3, F(21) - 0.1, 60, 1110, ICE)
FX.append(("borrar", P("olvida")))

# ================================================================== 13) LOS GOBIERNOS: cordón policial, focos… y la puerta no se rompe
f13 = F(21); tg = P("destruirlas")
cinta = "".join(f'<rect x="{x}" y="0" width="34" height="34" fill="#111" transform="skewX(-30)"/>' for x in range(0, 1400, 68))
e13 = ['<rect width="1080" height="1920" fill="url(#noche)"/>', skyline(77, 1380, 0.8, "#060a10", "#09101a", 0.12),
       '<rect x="-200" y="1380" width="1480" height="700" fill="url(#suelo)"/>',
       '<path id="foco13" d="M900,0 L380,1460 L700,1460 Z" fill="url(#focoG)" opacity="0.55"/>',
       puerta("p13", 540, 1380, 220, 480, "frio"),
       '<g id="chispas13" opacity="0">' + "".join(f'<path d="M560,1080 l{120 * math.cos(a):.0f},{120 * math.sin(a):.0f}" stroke="#ffd27a" stroke-width="5" stroke-linecap="round"/>' for a in [k * 0.45 - 2.4 for k in range(10)]) + '<circle cx="560" cy="1080" r="40" fill="#fff6d0" opacity="0.9"/></g>',
       '<g id="maza13"><path d="M650,1040 L1500,700 L1500,760 L660,1068 Z" fill="#1a1f27"/><rect x="1180" y="790" width="60" height="120" rx="6" fill="#2a313c" transform="rotate(-22 1210 850)"/><rect x="600" y="1010" width="70" height="90" rx="10" fill="#2a313c"/></g>',
       '<g transform="translate(-60,1500) rotate(-4)"><rect width="1300" height="34" fill="#f2c20f"/><g transform="translate(0,0)">' + cinta + '</g><text x="200" y="26" font-family="Inter" font-weight="900" font-size="24" fill="#111">PROHIBIDO EL PASO · PROHIBIDO EL PASO · PROHIBIDO EL PASO · PROHIBIDO EL PASO</text></g>',
       "".join(persona(x, 1640 + (k % 2) * 30, 300 + (k % 3) * 20, col="#04060a", rim="#9fdcff") for k, x in enumerate(range(80, 1080, 150))),
       '<rect id="sir13a" width="1080" height="1920" fill="url(#sirenaR)" opacity="0"/><rect id="sir13b" width="1080" height="1920" fill="url(#sirenaA)" opacity="0"/>']
grad_lin("focoG", ((0, "#e9f4ff", 0.0), (0.4, "#e9f4ff", 0.35), (1, "#e9f4ff", 0.05)))
escena("e13", "".join(e13))
mostrar("e13", f13, F(24))
camara("e13", f13, F(24), enfoca(540, 1200, 1.0), enfoca(540, 1150, 1.15), "sine.inOut")
J(f'tl.fromTo("#foco13", {{rotation:-8}}, {{rotation:10, svgOrigin:"900 0", duration:{F(24) - f13:.2f}, ease:"sine.inOut", immediateRender:false}}, {f13:.2f});')
J(f'tl.to("#sir13a", {{opacity:0.8, duration:0.3, yoyo:true, repeat:{int((F(24) - f13) / 0.6)}, ease:"sine.inOut"}}, {f13:.2f}); tl.to("#sir13b", {{opacity:0.8, duration:0.3, yoyo:true, repeat:{int((F(24) - f13) / 0.6)}, ease:"sine.inOut"}}, {f13 + 0.3:.2f});')
J(f'tl.fromTo("#maza13", {{x:260, rotation:0}}, {{x:0, duration:0.18, ease:"power3.in", immediateRender:false}}, {tg - 0.15:.2f}); tl.to("#maza13", {{x:160, rotation:6, svgOrigin:"640 1050", duration:0.4, ease:"power2.out"}}, {tg + 0.05:.2f});')
J(f'tl.fromTo("#chispas13", {{opacity:1, scale:0.4}}, {{opacity:0, scale:1.6, svgOrigin:"560 1080", duration:0.5, ease:"power2.out", immediateRender:false}}, {tg + 0.03:.2f});')
J(f'tl.fromTo("#e13-cam", {{rotation:0}}, {{rotation:0.6, duration:0.05, yoyo:true, repeat:5, ease:"none", immediateRender:false}}, {tg + 0.03:.2f});')
nota("PROHIBIDAS", P("prohibir") - 0.3, F(24) - 0.1, 60, 500, RED)
nota("INDESTRUCTIBLES", tg - 0.1, F(24) - 0.1, 60, 600, ICE)
FX.append(("sirena", f13)); FX.append(("metal", tg + 0.02))

# ================================================================== 14) LO PEOR: alguien cruza una y otra vez; el precio sube
f14 = F(24)
e14 = ['<rect width="1080" height="1920" fill="#030305"/>', '<rect id="osc14" width="1080" height="1920" fill="#200404" opacity="0"/>',
       '<rect x="0" y="1460" width="1080" height="460" fill="url(#suelo)"/>', puerta("p14", 540, 1460, 300, 660, "rojo", abre=0.75),
       persona(540, 1600, 380, rim="#ff8a6a", pid="rep14"), polvo("pv14", 90, 250, 830, 700, 1600, "#ff9a80", 21, 1.8)]
escena("e14", "".join(e14))
mostrar("e14", f14, F(26))
camara("e14", f14, F(26), enfoca(540, 1150, 1.0), enfoca(540, 1100, 1.4), "power1.in")
veces = P("varias") - 1.6
for k in range(4):
    t0 = f14 + 0.4 + k * 1.75
    J(f'tl.fromTo("#rep14", {{y:0, scale:1, opacity:1}}, {{y:-120, scale:0.7, opacity:0, svgOrigin:"540 1600", duration:0.75, ease:"power2.in", immediateRender:false}}, {t0:.2f});'
      f'tl.fromTo("#rep14", {{y:-120, scale:0.7, opacity:0}}, {{y:0, scale:1, opacity:1, duration:0.6, ease:"power2.out", immediateRender:false}}, {t0 + 0.9:.2f});')
    FX.append(("cruce", t0 + 0.6))
J(f'tl.to("#osc14", {{opacity:0.85, duration:{F(26) - f14:.2f}, ease:"power1.in"}}, {f14:.2f});')
OVR.append(f'<div id="pre14" class="nota" style="left:60px;top:500px;--c:{RED}"><b></b><span class="ct">CRUCE <span id="cr14">1</span></span><span class="cs">PRECIO</span><div class="barra" style="width:200px;margin:0"><i id="br14"></i></div></div>')
pop("#pre14", f14 + 0.3, 0.4, "opacity:0, x:-30"); fuera("#pre14", F(26) - 0.1)
for k in range(4):
    t0 = f14 + 0.4 + k * 1.75 + 0.75
    J(f'tl.set("#cr14", {{innerHTML:"{k + 2}"}}, {t0:.2f}); tl.to("#br14", {{scaleX:{0.25 + 0.25 * k:.2f}, duration:0.4, ease:"power3.out"}}, {t0:.2f});')
J('tl.set("#cr14", {innerHTML:"1"}, 0); tl.set("#br14", {scaleX:0.1}, 0);')
FX.append(("golpe", P("precio") - 0.2))
negro(F(26), 0.5)

# ================================================================== 15) AL DÍA SIGUIENTE: las puertas se apagan… todas menos una
f15 = F(26)
e15 = ['<rect x="-400" y="0" width="1880" height="2300" fill="#04070b"/>', calles, manz,
       "".join(f'<g class="pu15" data-k="{k}"><circle cx="{x}" cy="{y}" r="58" fill="url(#halo_oro)"/><rect x="{x - 5}" y="{y - 10}" width="10" height="20" fill="{ORO}"/></g>' for k, (x, y) in enumerate(pts10)),
       '<g id="ult15"><circle cx="540" cy="1190" r="80" fill="url(#halo_oro)"/><rect x="530" y="1170" width="20" height="40" fill="#fff1c0"/></g>']
escena("e15", "".join(e15))
mostrar("e15", f15, F(28))
J(f'tl.to(".pu15", {{opacity:0, duration:0.15, stagger:{{each:0.025, from:"random"}}}}, {P("desaparecen") - 0.1:.2f});')
camara("e15", f15, P("tuya") - 0.2, (0, 0, 1.0), (0, 0, 1.1), "sine.inOut")
J(f'tl.to("#e15-cam", {{scale:9, y:{-9 * (1190 - 960)}, x:0, duration:{F(28) - P("tuya") + 0.2:.2f}, ease:"power3.in"}}, {P("tuya") - 0.2:.2f});')
FX.append(("apagado", P("desaparecen") - 0.1)); FX.append(("whoosh", F(28) - 0.6))
luz(F(28), "#ffe2b0", 0.4)

# ================================================================== 16-18) LA TUYA: delante de ti; zoom a la puerta y el mensaje se graba en la madera; se abre… y negro
f16 = F(28); tmsg = P("ella", 2); ta = P("abre")
DX, DY, DW, DH = 540, 1500, 420, 960
mensaje = ("Puedes recuperar", "todo lo que", "has perdido…", "pero tendrás", "que entregar algo", "que todavía", "conservas.")
mensaje = ("PUEDES RECUPERAR", "TODO LO QUE", "HAS PERDIDO…", "PERO TENDRÁS", "QUE ENTREGAR ALGO", "QUE TODAVÍA", "CONSERVAS")
def talla(k, t):
    """Letras TALLADAS en la madera: borde iluminado abajo-derecha, surco oscuro, y brasa que brilla al grabarse y se apaga."""
    y = 690 + k * 44
    base = f'x="{DX}" text-anchor="middle" font-family="Grabado" font-size="21" letter-spacing="1.4"'
    return (f'<g class="lin16" id="ln{k}"><text {base} y="{y + 1.6:.1f}" dx="1.3" fill="#6e5a40" opacity="0.85">{t}</text>'
            f'<text {base} y="{y:.1f}" fill="#070504">{t}</text>'
            f'<text class="emb16" {base} y="{y:.1f}" fill="url(#brasa)" filter="url(#brillo)" opacity="0">{t}</text></g>')
r16 = random.Random(16)
vetas = "".join(f'<path d="M{x:.0f},569 C{x + r16.uniform(-6, 6):.0f},800 {x + r16.uniform(-8, 8):.0f},1200 {x + r16.uniform(-5, 5):.0f},1500" stroke="{r16.choice(("#2a1f15", "#0f0a07", "#24190f"))}" stroke-width="{r16.uniform(1, 3.5):.1f}" fill="none" opacity="{r16.uniform(0.25, 0.6):.2f}"/>' for x in [r16.uniform(362, 718) for _ in range(46)])
grabado = vetas + "".join(talla(k, t) for k, t in enumerate(mensaje))
grad_lin("brasa", ((0, "#ffe2a8", 1), (0.5, "#ff9a3c", 1), (1, "#d2541c", 1)))
e16 = ['<rect width="1080" height="1920" fill="#030406"/>', '<rect x="0" y="0" width="1080" height="1500" fill="url(#muro)"/>', '<polygon points="0,1500 1080,1500 1080,1920 0,1920" fill="#06080b"/>',
       '<rect id="haz16" x="0" y="1500" width="1080" height="420" fill="url(#haz16g)" opacity="0.25"/>',
       '<g id="pu16">' + puerta("p16", DX, DY, DW, DH, "oro", haz=0.55, marco="#0c0d10", hoja="#17130f", en_hoja=grabado) + '</g>',
       persona(300, 1980, 900, col="#020304", rim="#ffb14a", pid="tu16"), polvo("pv16", 90, 200, 900, 600, 1700, "#ffe2b0", 31, 1.8)]
grad_lin("haz16g", ((0, "#ffd27a", 0.7), (1, "#ffd27a", 0)))
DEFS.append('<filter id="brillo" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
escena("e16", "".join(e16))
mostrar("e16", f16, DUR)
camara("e16", f16, tmsg - 0.4, enfoca(540, 1160, 0.92), enfoca(540, 1120, 1.0), "sine.out")
J(f'tl.to("#e16-cam", {{x:{enfoca(540, 818, 2.45)[0]}, y:{enfoca(540, 818, 2.45)[1]}, scale:2.45, duration:1.3, ease:"power2.inOut"}}, {tmsg - 0.4:.2f});')
J(f'tl.to("#e16-cam", {{x:{enfoca(540, 812, 2.6)[0]}, y:{enfoca(540, 812, 2.6)[1]}, scale:2.6, duration:{ta - 0.9 - tmsg - 0.9:.2f}, ease:"none"}}, {tmsg + 0.9:.2f});')
J(f'tl.to("#e16-cam", {{x:{enfoca(540, 1090, 1.12)[0]}, y:{enfoca(540, 1090, 1.12)[1]}, scale:1.12, duration:1.5, ease:"power2.inOut"}}, {ta - 0.9:.2f});')
J(f'tl.fromTo("#tu16", {{x:-40}}, {{x:0, duration:{tmsg - f16:.2f}, ease:"sine.out", immediateRender:false}}, {f16:.2f});')
J(f'tl.fromTo("#p16 .filo, #p16 .hueco", {{opacity:0.6}}, {{opacity:1, duration:0.3, yoyo:true, repeat:{int((tmsg - f16) / 0.6)}, ease:"sine.inOut", immediateRender:false}}, {f16:.2f});')
J('tl.set(".lin16", {clipPath:"inset(0% 100% 0% 0%)"}, 0); tl.set(".emb16", {opacity:0}, 0);')
for k, w in enumerate(("puedes", "todo", "perdido", "pero", "entregar", "todavia", "conservas")):
    tw = P(w, {"pero": 8, "todo": 2, "entregar": 2, "puedes": 3, "todavia": 2, "perdido": 2}.get(w, 1))
    J(f'tl.to("#ln{k}", {{clipPath:"inset(0% 0% 0% 0%)", duration:0.7, ease:"none"}}, {tw - 0.2:.2f});')
    J(f'tl.fromTo("#ln{k} .emb16", {{opacity:0.95}}, {{opacity:0.38, duration:1.6, ease:"power2.out", immediateRender:false}}, {tw - 0.2:.2f});')
FX.append(("grabado", tmsg + 0.4))
J(f'tl.to("#p16 .hoja", {{scaleX:0.16, transformOrigin:"0% 0%", duration:{P("detras", 2) - ta + 0.3:.2f}, ease:"power1.in"}}, {ta:.2f}); tl.to("#haz16", {{opacity:1, duration:{P("detras", 2) - ta:.2f}, ease:"power1.in"}}, {ta:.2f});')
FX.append(("chirrido", ta - 0.1))
tc = P("detras", 2) + 0.45
J(f'tl.set("#negroF", {{opacity:1}}, {tc:.2f});')
FX.append(("final", tc))
OVR.append('<div id="negroF"></div>')
J('tl.set("#negroF", {opacity:0}, 0);')

# ------------------------------------------------------------------ subtítulos habituales (arriba, palabra a palabra, recuadro azul en lo importante)
CLAVE = set(norm(w) for w in ["puerta", "planeta", "casa", "trabajo", "calle", "deseas", "policia", "diferente", "dinero", "perdido", "sonado",
                               "condicion", "cambio", "elegir", "cruzas", "millones", "millonarios", "consecuencias", "familia", "recuerdos",
                               "prohibir", "inutil", "destruirlas", "veces", "precio", "desaparecen", "tuya", "mensaje", "conservas", "detras"])
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
#e10-cam svg, #e15-cam svg{{transform:perspective(1500px) rotateX(48deg) scale(1.55);transform-origin:50% 62%}}
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

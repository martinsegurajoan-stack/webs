#!/usr/bin/env python3
"""«¿Y si Marruecos invadiera España?» en 60 s (@mundo.supuesto). Estilo INFOGRAFÍA ANIMADA (ni libreta ni 2D):
mapa del Estrecho con cámara que viaja, paneles VS con iconos y contadores, notitas con cada dato y su fuente.
Voz: tiempos.json (montar_voz.py). Salida: index.html (HyperFrames) + efectos.json (mezcla.py).
  python3 gen.py
"""
import json, math, os, re, unicodedata

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
    raise KeyError(word)
def F(n): return FR[n - 1]["ini"]
def FE(n): return FR[n - 1]["fin"]

tl, FX = [], []
def J(s): tl.append(s)
NID = [0]
def nid(p="e"):
    NID[0] += 1
    return f"{p}{NID[0]}"

# ------------------------------------------------------------------ colores
ES, MA = "#e0a422", "#d0453a"          # España (oro), Marruecos (rojo)
NAVY, INK = "#1d2433", "#24304a"
GRN, RED = "#2e9d57", "#d0453a"
SEA1, SEA2 = "#9ad8f0", "#5bb4de"

# ------------------------------------------------------------------ mapa (lon/lat → mundo)
K = 200.0
CX = 0.79
def W(lon, lat):
    return ((lon + 14) * K * CX, (45 - lat) * K)
def poly(pts):
    return "M" + " L".join(f"{W(a, b)[0]:.0f},{W(a, b)[1]:.0f}" for a, b in pts) + " Z"

N_ES = [(-1.78, 43.37), (-1.98, 43.32), (-2.95, 43.40), (-3.80, 43.47), (-4.6, 43.42), (-5.66, 43.55), (-5.85, 43.66), (-7.04, 43.54),
        (-7.69, 43.79), (-8.40, 43.37), (-9.0, 43.2), (-9.27, 42.88), (-8.9, 42.5), (-8.75, 42.23), (-8.87, 41.87)]
BORDER_PT = [(-8.87, 41.87), (-8.2, 42.1), (-7.4, 41.85), (-6.6, 41.95), (-6.2, 41.6), (-6.9, 41.0), (-6.8, 40.3), (-7.0, 39.7),
             (-7.5, 39.6), (-7.0, 39.0), (-7.3, 38.4), (-7.0, 38.0), (-7.5, 37.5), (-7.40, 37.17)]
S_ES = [(-7.40, 37.17), (-6.95, 37.20), (-6.40, 36.80), (-6.29, 36.53), (-6.0, 36.2), (-5.61, 36.01), (-5.35, 36.13), (-4.9, 36.5),
        (-4.42, 36.72), (-3.5, 36.72), (-2.46, 36.83), (-2.19, 36.72), (-1.6, 37.3), (-0.98, 37.60), (-0.69, 37.63), (-0.48, 38.35),
        (0.23, 38.73), (-0.33, 39.47), (-0.03, 39.98), (0.87, 40.72), (1.25, 41.12), (2.17, 41.39), (3.0, 41.8), (3.32, 42.32), (3.16, 42.43)]
PIRINEO = [(3.16, 42.43), (2.5, 42.35), (1.7, 42.5), (0.7, 42.8), (-0.3, 42.8), (-1.4, 43.05), (-1.78, 43.37)]
SPAIN = N_ES + BORDER_PT[1:] + S_ES[1:] + PIRINEO[1:]
PORTUGAL = [(-8.87, 41.87), (-8.67, 41.15), (-8.75, 40.64), (-9.0, 40.0), (-9.38, 39.36), (-9.50, 38.78), (-9.15, 38.70), (-8.9, 38.5),
            (-8.87, 37.95), (-8.80, 37.4), (-8.99, 37.02), (-7.93, 37.01), (-7.40, 37.17)] + BORDER_PT[::-1][1:]
FRANCIA = PIRINEO[::-1] + [(-1.45, 43.6), (-1.2, 44.6), (-1.3, 46.5), (4.5, 46.5), (4.5, 43.4), (3.05, 42.6), (3.16, 42.43)]
MARRUECOS = [(-2.22, 35.09), (-2.97, 35.44), (-2.94, 35.29), (-3.4, 35.2), (-3.93, 35.25), (-4.67, 35.21), (-5.10, 35.45), (-5.30, 35.68),
             (-5.31, 35.89), (-5.50, 35.89), (-5.80, 35.79), (-5.92, 35.79), (-6.03, 35.47), (-6.15, 35.19), (-6.65, 34.30), (-6.84, 34.02),
             (-7.62, 33.60), (-8.50, 33.25), (-9.24, 32.30), (-9.77, 31.51), (-9.89, 30.63), (-9.60, 30.42), (-10.17, 29.38), (-11.1, 28.5),
             (-11.6, 27.9), (-11.6, 27.2), (-8.67, 27.2), (-8.67, 28.7), (-6.5, 29.5), (-5.0, 29.9), (-3.6, 30.6), (-2.5, 31.5), (-1.2, 32.1),
             (-1.5, 32.8), (-1.7, 33.7), (-1.75, 34.7)]
ARGELIA = [(-2.22, 35.09), (-1.3, 35.3), (-0.64, 35.70), (0.5, 36.2), (1.5, 36.55), (3.5, 36.8), (5.0, 36.9), (5.0, 27.2), (-8.67, 27.2),
           (-8.67, 28.7), (-6.5, 29.5), (-5.0, 29.9), (-3.6, 30.6), (-2.5, 31.5), (-1.2, 32.1), (-1.5, 32.8), (-1.7, 33.7), (-1.75, 34.7)]
def isla(lon, lat, rx, ry, rot=0):
    x, y = W(lon, lat)
    return f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rx * K * CX:.0f}" ry="{ry * K:.0f}" transform="rotate({rot} {x:.0f} {y:.0f})"/>'

CIUD = {"Madrid": (-3.70, 40.42), "Rabat": (-6.84, 34.02), "Tarifa": (-5.61, 36.01), "Tánger": (-5.80, 35.77), "Ceuta": (-5.31, 35.89),
        "Melilla": (-2.94, 35.29)}

MAPA = [f'<rect x="-4000" y="-4000" width="12000" height="12000" fill="url(#mar)"/>',
        f'<rect x="-4000" y="-4000" width="12000" height="12000" fill="url(#olas)" opacity="0.5" id="olas"/>']
for pts, fill in ((FRANCIA, "#ece6da"), (ARGELIA, "#ece6da"), (PORTUGAL, "#ece6da"), (MARRUECOS, "#f2b7ae"), (SPAIN, "#f6d98a")):
    MAPA.append(f'<path d="{poly(pts)}" fill="{fill}" stroke="#ffffff" stroke-width="7" stroke-linejoin="round"/>')
MAPA.append(f'<g fill="#f6d98a" stroke="#ffffff" stroke-width="5">{isla(2.95, 39.62, 0.42, 0.24, -20)}{isla(4.10, 39.97, 0.2, 0.08, -10)}{isla(1.42, 38.98, 0.17, 0.12)}{isla(1.45, 38.70, 0.07, 0.05)}</g>')
# relieve suave (sombras de sierra) para que no se vea plano
for lon, lat, rx, ry in ((-4.0, 40.6, 1.6, 0.25), (-3.2, 37.1, 1.3, 0.2), (-5.0, 31.6, 2.6, 0.35), (-4.4, 34.9, 1.2, 0.2), (-0.8, 42.7, 1.8, 0.18)):
    x, y = W(lon, lat)
    MAPA.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rx * K * CX:.0f}" ry="{ry * K:.0f}" fill="#000" opacity="0.05" transform="rotate(-12 {x:.0f} {y:.0f})"/>')
# etiquetas de país
for txt, lon, lat, col in (("ESPAÑA", -4.0, 39.3, "#a87808"), ("MARRUECOS", -7.0, 31.9, "#a3352c"), ("PORTUGAL", -8.2, 39.6, "#b9b2a4"), ("ARGELIA", 1.0, 33.0, "#b9b2a4")):
    x, y = W(lon, lat)
    MAPA.append(f'<text class="pais" x="{x:.0f}" y="{y:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="{110 if col in ("#a87808", "#a3352c") else 70}" letter-spacing="14" fill="{col}" opacity="0.85">{txt}</text>')
for nom, (lon, lat) in CIUD.items():
    x, y = W(lon, lat)
    if nom in ("Ceuta", "Melilla"):
        continue
    dy = -26 if nom not in ("Tánger", "Rabat") else 52
    MAPA.append(f'<g class="ciudad"><circle cx="{x:.0f}" cy="{y:.0f}" r="11" fill="{NAVY}" stroke="#fff" stroke-width="5"/>'
                f'<text x="{x + 18:.0f}" y="{y + dy:.0f}" font-family="Inter" font-weight="800" font-size="34" fill="{NAVY}">{nom}</text></g>')
# Ceuta y Melilla: marcadores que laten
for nom in ("Ceuta", "Melilla"):
    x, y = W(*CIUD[nom])
    MAPA.append(f'<g id="m-{norm(nom)}"><circle class="pulso" cx="{x:.0f}" cy="{y:.0f}" r="18" fill="none" stroke="{ES}" stroke-width="6"/>'
                f'<circle cx="{x:.0f}" cy="{y:.0f}" r="14" fill="{ES}" stroke="#fff" stroke-width="6"/>'
                f'<g class="etq" opacity="0"><rect x="{x - 95:.0f}" y="{y - 92:.0f}" width="190" height="56" rx="16" fill="{NAVY}"/>'
                f'<text x="{x:.0f}" y="{y - 52:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="34" fill="#fff">{nom.upper()}</text></g></g>')
# chinchetas con bandera en las capitales
def bandera_es(w=120, h=80):
    return (f'<rect width="{w}" height="{h}" rx="8" fill="#c60b1e"/><rect y="{h / 4}" width="{w}" height="{h / 2}" fill="#ffc400"/>')
def bandera_ma(w=120, h=80):
    cx, cy, r = w / 2, h / 2, h * 0.3
    pts = [(cx + r * math.sin(i * 4 * math.pi / 5), cy - r * math.cos(i * 4 * math.pi / 5)) for i in range(5)]
    d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + " Z"
    return (f'<rect width="{w}" height="{h}" rx="8" fill="#c1272d"/><path d="{d}" fill="none" stroke="#006233" stroke-width="{h * 0.06:.1f}" stroke-linejoin="round"/>')
for nom, fn in (("Madrid", bandera_es), ("Rabat", bandera_ma)):
    x, y = W(*CIUD[nom])
    MAPA.append(f'<g class="pin" id="pin-{norm(nom)}" transform="translate({x - 60:.0f},{y - 175:.0f})"><path d="M60,80 L60,170" stroke="{NAVY}" stroke-width="7"/>'
                f'<g filter="url(#sombra)">{fn()}</g></g>')

# ------------------------------------------------------------------ iconos (viewBox 0 0 100 100, color = currentColor)
ICON = {
    "soldado": '<circle cx="50" cy="24" r="13"/><path d="M33,22 Q50,2 67,22 L67,26 L33,26 Z"/><path d="M30,44 Q50,34 70,44 L70,70 L62,70 L60,96 L53,96 L50,72 L47,96 L40,96 L38,70 L30,70 Z"/>',
    "tanque": '<rect x="8" y="58" width="84" height="22" rx="11"/><rect x="18" y="42" width="54" height="18" rx="5"/><rect x="34" y="30" width="28" height="16" rx="6"/><rect x="60" y="34" width="36" height="6" rx="3"/><g fill="#fff" opacity="0.6"><circle cx="20" cy="69" r="5"/><circle cx="35" cy="69" r="5"/><circle cx="50" cy="69" r="5"/><circle cx="65" cy="69" r="5"/><circle cx="80" cy="69" r="5"/></g>',
    "caza": '<path d="M50,4 L56,30 L92,58 L92,66 L56,56 L55,80 L68,90 L68,95 L50,90 L32,95 L32,90 L45,80 L44,56 L8,66 L8,58 L44,30 Z"/>',
    "submarino": '<rect x="6" y="46" width="88" height="26" rx="13"/><rect x="38" y="30" width="20" height="20" rx="4"/><rect x="46" y="18" width="4" height="14"/><path d="M90,59 L99,48 L99,70 Z"/>',
    "barco": '<path d="M4,60 L96,60 L84,80 L16,80 Z"/><rect x="34" y="40" width="30" height="20"/><rect x="44" y="26" width="10" height="14"/><rect x="62" y="48" width="18" height="12"/><rect x="48" y="12" width="2" height="16"/>',
    "lancha": '<path d="M10,58 L90,58 L78,74 L22,74 Z"/><rect x="40" y="46" width="22" height="12" rx="3"/>',
    "portaaviones": '<path d="M2,56 L98,50 L94,62 L86,74 L10,74 Z"/><rect x="62" y="34" width="12" height="18"/><rect x="66" y="24" width="4" height="12"/><g fill="#fff" opacity="0.7"><rect x="8" y="53" width="40" height="2"/></g>',
    "contenedor": '<rect x="8" y="30" width="84" height="44" rx="4"/><g fill="#fff" opacity="0.45"><rect x="18" y="36" width="5" height="32"/><rect x="32" y="36" width="5" height="32"/><rect x="46" y="36" width="5" height="32"/><rect x="60" y="36" width="5" height="32"/><rect x="74" y="36" width="5" height="32"/></g>',
}
SYMS = "".join(f'<symbol id="i-{k}" viewBox="0 0 100 100">{v}</symbol>' for k, v in ICON.items())
def ico(k, x, y, s, col, cls="", extra=""):
    return f'<svg class="ic {cls}" style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{s}px;height:{s}px;color:{col}" viewBox="0 0 100 100" {extra}><use href="#i-{k}" fill="currentColor"/></svg>'

# ------------------------------------------------------------------ cámara del mapa
VIEW_Y = 820      # dónde queda el centro de la cámara en pantalla
def cam(lon, lat, z, t, dur=1.2, ease="power2.inOut", vy=VIEW_Y):
    x, y = W(lon, lat)
    J(f'tl.to("#mundo", {{x:{540 - x * z:.0f}, y:{vy - y * z:.0f}, scale:{z}, duration:{dur:.2f}, ease:"{ease}"}}, {t:.2f});')
def cam_set(lon, lat, z, vy=VIEW_Y):
    x, y = W(lon, lat)
    J(f'tl.set("#mundo", {{transformOrigin:"0 0", x:{540 - x * z:.0f}, y:{vy - y * z:.0f}, scale:{z}}}, 0);')

OVR = []   # capas en pantalla (sobre el mapa)
MOV = []   # cosas que se mueven por el mapa (en coords del mundo)

def pop(sel, t, d=0.4, frm="scale:0.4, opacity:0", ease="back.out(2)"):
    J(f'tl.fromTo("{sel}", {{{frm}}}, {{scale:1, opacity:1, x:0, y:0, rotation:0, duration:{d}, ease:"{ease}", immediateRender:false}}, {t:.2f});')
    J(f'tl.set("{sel}", {{opacity:0}}, 0);')
def fuera(sel, t, d=0.3):
    J(f'tl.to("{sel}", {{opacity:0, scale:0.9, duration:{d}}}, {t:.2f});')

NOTAS = []
def nota(txt, sub, t, t_out, x=40, y=842, rot=-4, w=380):
    i = nid("nt")
    OVR.append(f'<div id="{i}" class="nota" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({rot}deg)"><div class="nt">{txt}</div><div class="ns">{sub}</div></div>')
    J(f'tl.set("#{i}", {{opacity:0}}, 0); tl.fromTo("#{i}", {{y:-60, opacity:0, rotation:{rot - 8}}}, {{y:0, opacity:1, rotation:{rot}, duration:0.45, ease:"back.out(2)", immediateRender:false}}, {t:.2f});')
    J(f'tl.to("#{i}", {{opacity:0, y:-30, duration:0.3}}, {t_out:.2f});')
    FX.append(("posit", t + 0.2))

# ================================================================== GANCHO (frase 1): el Estrecho, 14 km, lanchas que cruzan
f1, f1e = F(1), FE(1)
cam_set(-5.5, 35.98, 1.6)
cam(-5.5, 35.98, 1.35, 0, f1e, "sine.inOut")
# regla de 14 km entre Tarifa y Punta Cires
xa, ya = W(-5.61, 36.01); xb, yb = W(-5.42, 35.915)
MAPA.append(f'<g id="regla"><path id="regla-l" d="M{xa:.0f},{ya:.0f} L{xb:.0f},{yb:.0f}" stroke="{NAVY}" stroke-width="7" stroke-dasharray="1" pathLength="1" fill="none"/>'
            f'<circle cx="{xa:.0f}" cy="{ya:.0f}" r="10" fill="{NAVY}"/><circle cx="{xb:.0f}" cy="{yb:.0f}" r="10" fill="{NAVY}"/>'
            f'<g id="regla-t"><rect x="{(xa + xb) / 2 - 20:.0f}" y="{(ya + yb) / 2 - 30:.0f}" width="150" height="60" rx="14" fill="#fff" stroke="{NAVY}" stroke-width="5"/>'
            f'<text x="{(xa + xb) / 2 + 55:.0f}" y="{(ya + yb) / 2 + 14:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="40" fill="{NAVY}">14 km</text></g></g>')
J('tl.fromTo("#regla-l", {strokeDasharray:"0 1"}, {strokeDasharray:"1 0", duration:0.6, ease:"power2.out", immediateRender:false}, 0.15);')
J('tl.set("#regla-l", {strokeDasharray:"0 1"}, 0);')
pop("#regla-t", P("catorce"), 0.4)
FX.append(("pop", P("catorce")))
# lanchas marroquíes que salen de la costa (desde el fotograma 0)
LAN = []
for k, (lon, lat) in enumerate(((-6.35, 35.86), (-6.05, 35.84), (-5.80, 35.86), (-5.05, 35.95), (-4.75, 35.97))):
    x, y = W(lon, lat)
    i = f"lan{k}"
    LAN.append(i)
    MOV.append(f'<g id="{i}" transform="translate({x:.0f},{y:.0f})"><g class="lanw"><g transform="scale(0.6)">'
               f'<path d="M-9,40 L-30,120 M9,40 L30,120" stroke="#ffffff" stroke-width="7" stroke-linecap="round" opacity="0.8"/>'
               f'<path d="M0,-44 C16,-22 15,28 11,40 L-11,40 C-15,28 -16,-22 0,-44 Z" fill="{MA}" stroke="#fff" stroke-width="5"/>'
               f'<rect x="-6" y="-6" width="12" height="18" rx="3" fill="#fff" opacity="0.8"/></g></g></g>')
    J(f'tl.fromTo("#{i}", {{y:"+=0"}}, {{y:"-=45", duration:{max(1, P("cruzarlos") - 0.2):.2f}, ease:"sine.inOut", immediateRender:false}}, 0);')
J(f'tl.to(".lanw", {{rotation:4, transformOrigin:"0px 0px", duration:0.4, yoyo:true, repeat:{int(f1e / 0.4)}, ease:"sine.inOut"}}, 0);')
# radar en la costa española
xr, yr = W(-5.55, 36.06)
MAPA.append(f'<g id="radar">' + "".join(f'<circle class="rad" cx="{xr:.0f}" cy="{yr:.0f}" r="20" fill="none" stroke="{ES}" stroke-width="4"/>' for _ in range(3)) + '</g>')
J(f'tl.fromTo(".rad", {{attr:{{r:20}}, opacity:0.9}}, {{attr:{{r:160}}, opacity:0, duration:1.4, stagger:0.47, repeat:{int(f1e / 1.4) + 1}, ease:"none", immediateRender:false}}, 0);')
# signo de interrogación al decir «cruzarlos»
xq, yq = W(-5.50, 35.95)
MAPA.append(f'<g id="preg"><circle cx="{xq:.0f}" cy="{yq:.0f}" r="42" fill="{MA}" stroke="#fff" stroke-width="6"/><text x="{xq:.0f}" y="{yq + 20:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="58" fill="#fff">?</text></g>')
pop("#preg", P("cruzarlos"), 0.4)
FX.append(("golpe", P("cruzarlos")))
# título gancho (visible desde el fotograma 0)
OVR.append(f'<div id="titulo"><div class="t1">¿Y SI MARRUECOS</div><div class="t2">INVADIERA ESPAÑA?</div>'
           f'<div class="t3"><span class="fl">{"<svg width=60 height=40 viewBox=\'0 0 120 80\'>" + bandera_ma() + "</svg>"}</span> VS <span class="fl">{"<svg width=60 height=40 viewBox=\'0 0 120 80\'>" + bandera_es() + "</svg>"}</span></div></div>')
J('tl.fromTo("#titulo", {scale:1.18}, {scale:1, duration:0.45, ease:"back.out(1.6)", immediateRender:false}, 0);')
J('tl.fromTo("#titulo .t2", {x:-30}, {x:0, duration:0.35, ease:"power3.out", immediateRender:false}, 0.05);')
J(f'tl.to("#titulo", {{y:-12, duration:0.9, yoyo:true, repeat:{int(f1e / 0.9)}, ease:"sine.inOut"}}, 0.45);')
FX.append(("golpe", 0.0))
J(f'tl.to("#titulo", {{opacity:0, y:120, scale:0.8, duration:0.45, ease:"power2.in"}}, {F(2) + 0.6:.2f});')
J(f'tl.to("#{",#".join(LAN)}, #preg, #regla", {{opacity:0, duration:0.5}}, {F(2) + 0.4:.2f});')

# ================================================================== frase 2: vista general + «60 segundos»
cam(-4.6, 36.8, 0.40, F(2), 1.4)
FX.append(("whoosh", F(2)))
pop("#pin-madrid", F(2) + 0.7, 0.45, "scale:0, opacity:0, y:40")
pop("#pin-rabat", F(2) + 0.9, 0.45, "scale:0, opacity:0, y:40")
FX.append(("pop", F(2) + 0.7)); FX.append(("pop", F(2) + 0.9))
OVR.append('<div id="sesenta"><span>60</span> segundos · datos reales</div>')
pop("#sesenta", P("sesenta"), 0.4)
fuera("#sesenta", FE(2) + 0.1)

# ================================================================== PANEL VS (soldados, tanques, cazas, submarinos, ranking)
PANEL = []
def fmt(n):
    return f"{n:,}".replace(",", "<span>.</span>")
def contador(i, n, t, d=0.9, pre=""):
    pasos = 18
    for s in range(pasos + 1):
        v = round(n * (s / pasos) ** 0.6)
        J(f'tl.set("#{i}", {{innerHTML:"{pre}{fmt(v)}"}}, {t + d * s / pasos:.2f});')
    J(f'tl.set("#{i}", {{innerHTML:"{pre}0"}}, 0);')

def slide_vs(nombre, titulo, t_in, t_out, izq, der, gana, nota_txt, nota_sub):
    """izq/der = dict(n, txt, icono, cada, cuando, cols)"""
    sid = f"vs-{nombre}"
    h = [f'<div class="vs" id="{sid}"><div class="vt">{titulo}</div><div class="vbadge">VS</div>']
    for lado, d, x0 in (("es", izq, 40), ("ma", der, 520)):
        col = ES if lado == "es" else MA
        flag = bandera_es() if lado == "es" else bandera_ma()
        nom = "ESPAÑA" if lado == "es" else "MARRUECOS"
        cid = f"{sid}-{lado}-n"
        h.append(f'<div class="col" style="left:{x0}px"><div class="cab"><svg width="78" height="52" viewBox="0 0 120 80">{flag}</svg><span>{nom}</span></div>'
                 f'<div class="num" id="{cid}" style="color:{col}">0</div><div class="txt">{d.get("txt", "")}</div></div>')
        n_ic = d["iconos"]
        cols = d.get("cols", 6)
        s = d.get("tam", 66)
        ids = []
        for k in range(n_ic):
            r_, c_ = divmod(k, cols)
            iid = f"{sid}-{lado}-i{k}"
            ids.append(iid)
            h.append(ico(d["icono"], x0 + 10 + c_ * (s + 8), 380 + r_ * (s + 6), s, col, "", f'id="{iid}"'))
        if n_ic == 0:
            h.append(f'<div class="cero" id="{sid}-{lado}-cero" style="left:{x0 + 20}px">NINGUNO</div>')
            pop(f"#{sid}-{lado}-cero", d["cuando"] + 0.2, 0.4)
        else:
            J(f'tl.fromTo("#{",#".join(ids)}", {{scale:0, opacity:0}}, {{scale:1, opacity:1, duration:0.25, ease:"back.out(3)", stagger:{min(0.06, 0.9 / n_ic):.3f}, immediateRender:false}}, {d["cuando"]:.2f});')
            J(f'tl.set("#{",#".join(ids)}", {{opacity:0}}, 0);')
        contador(cid, d["n"], d["cuando"], 0.8, d.get("pre", ""))
        FX.append(("clic", d["cuando"]))
    if gana:
        x0 = 40 if gana == "es" else 520
        h.append(f'<div class="gana" id="{sid}-gana" style="left:{x0 + 268}px">VENTAJA</div>')
        tg = (izq if gana == "es" else der)["cuando"] + 0.9
        pop(f"#{sid}-gana", tg, 0.35, "scale:2, opacity:0, rotation:-20")
        FX.append(("sello", tg))
    if izq.get("pie") or der.get("pie"):
        h.append(f'<div class="pie">{izq.get("pie") or der.get("pie")}</div>')
    h.append('</div>')
    PANEL.append("".join(h))
    J(f'tl.set("#{sid}", {{opacity:0}}, 0); tl.fromTo("#{sid}", {{opacity:0, x:80}}, {{opacity:1, x:0, duration:0.35, ease:"power2.out", immediateRender:false}}, {t_in:.2f});')
    J(f'tl.to("#{sid}", {{opacity:0, x:-80, duration:0.3}}, {t_out:.2f});')
    nota(nota_txt, nota_sub, t_in + 0.3, t_out)

def panel_in(t):
    J(f'tl.to("#panel", {{y:0, duration:0.55, ease:"power3.out"}}, {t:.2f});')
    J(f'tl.to("#velo", {{opacity:1, duration:0.4}}, {t:.2f});')
    FX.append(("whoosh", t))
def panel_out(t):
    J(f'tl.to("#panel", {{y:1000, duration:0.5, ease:"power3.in"}}, {t:.2f});')
    J(f'tl.to("#velo", {{opacity:0, duration:0.4}}, {t:.2f});')
    FX.append(("whoosh", t))

# --- frase 3: soldados
cam(-5.3, 36.3, 0.9, F(3) - 0.2, 1.0, vy=560)
panel_in(F(3))
slide_vs("sold", "SOLDADOS EN ACTIVO", F(3) + 0.1, FE(3) + 0.05,
         dict(n=120000, txt="unos 120.000", icono="soldado", iconos=12, cuando=P("ciento")),
         dict(n=200000, txt="unos 200.000", icono="soldado", iconos=20, cuando=P("doscientos")),
         "ma", "1 muñeco = 10.000", "Fuente: IISS y Euronews (2026)")
# --- frase 4: tanques
slide_vs("tanq", "CARROS DE COMBATE", F(4), FE(4) + 0.05,
         dict(n=298, txt="menos de 300", icono="tanque", iconos=3, cuando=P("frente"), tam=96, cols=4),
         dict(n=1346, txt="más de 1.300", icono="tanque", iconos=13, cuando=P("trescientos"), tam=96, cols=4),
         "ma", "1 tanque = 100", "Fuente: Global Firepower 2026")
panel_out(FE(4) + 0.1)

# ================================================================== frase 5: el mar y el aire (escena en el mapa)
f5 = F(5)
cam(-5.5, 36.0, 1.9, f5 - 0.1, 1.2)
BAR = []
for k, lon in enumerate((-6.25, -5.95, -5.65, -5.35, -5.05, -4.75)):
    x, y = W(lon, 36.06 if k % 2 else 35.99)
    i = f"bar{k}"
    BAR.append(i)
    MOV.append(f'<g id="{i}" style="opacity:0" transform="translate({x - 36:.0f},{y - 36:.0f})"><svg width="72" height="72" viewBox="0 0 100 100" style="color:#2f4f8a"><use href="#i-barco" fill="currentColor"/></svg></g>')
J(f'tl.fromTo("#{",#".join(BAR)}", {{opacity:0, y:"-=60"}}, {{opacity:1, y:"+=60", duration:0.5, stagger:0.12, ease:"back.out(2)", immediateRender:false}}, {P("mar", 2) - 0.1:.2f});')
J(f'tl.set("#{",#".join(BAR)}", {{opacity:0}}, 0);')
FX.append(("whoosh", P("mar", 2)))
CAZ = []
for k, lon in enumerate((-6.0, -5.5, -5.0)):
    x, y = W(lon, 36.5)
    i = f"caz{k}"
    CAZ.append(i)
    MOV.append(f'<g id="{i}" style="opacity:0" transform="translate({x - 40:.0f},{y - 40:.0f})"><path d="M40,80 L40,240" stroke="#ffffff" stroke-width="6" opacity="0.7"/>'
               f'<svg width="80" height="80" viewBox="0 0 100 100" style="color:{NAVY}"><g transform="rotate(180 50 50)"><use href="#i-caza" fill="currentColor"/></g></svg></g>')
J(f'tl.fromTo("#{",#".join(CAZ)}", {{opacity:1, y:-500}}, {{y:420, duration:1.6, stagger:0.25, ease:"none", immediateRender:false}}, {P("aire") - 0.4:.2f});')
J(f'tl.set("#{",#".join(CAZ)}", {{opacity:0}}, 0); tl.set("#{",#".join(CAZ)}", {{opacity:1}}, {P("aire") - 0.4:.2f}); tl.to("#{",#".join(CAZ)}", {{opacity:0, duration:0.2}}, {P("aire") + 1.6:.2f});')
FX.append(("whoosh", P("aire") - 0.2)); FX.append(("whoosh", P("aire") + 0.3))
OVR.append(f'<div id="manda" class="cartel">MAR Y AIRE: <b style="color:{ES}">ESPAÑA</b></div>')
pop("#manda", P("manda"), 0.4, "scale:1.6, opacity:0")
FX.append(("sello", P("manda")))
fuera("#manda", FE(5))
nota("Para invadir hay que", "cruzar el mar (14 km)", f5 + 0.2, FE(5), x=60, y=1300, rot=3)

# ================================================================== frases 6-8: panel otra vez
cam(-5.3, 36.3, 0.9, F(6) - 0.3, 1.0, vy=560)
J(f'tl.to("#{",#".join(BAR)}", {{opacity:0, duration:0.4}}, {F(6) - 0.3:.2f});')
panel_in(F(6) - 0.1)
slide_vs("cazas", "AVIONES DE CAZA", F(6), FE(6) + 0.05,
         dict(n=136, txt="cazas", icono="caza", iconos=14, cuando=P("treinta"), cols=5, tam=70),
         dict(n=84, txt="cazas", icono="caza", iconos=8, cuando=P("ochenta"), cols=5, tam=70),
         "es", "1 avión = 10 cazas", "Fuente: Global Firepower 2026")
slide_vs("subs", "SUBMARINOS", F(7), P("portaaviones") - 0.1,
         dict(n=2, txt="submarinos", icono="submarino", iconos=2, cuando=P("dos"), cols=2, tam=150),
         dict(n=0, txt="submarinos", icono="submarino", iconos=0, cuando=P("ninguno")),
         "es", "España: 2 en servicio", "Fuente: GFP 2026 y Armada")
# portaaviones
sid = "vs-port"
PANEL.append(f'<div class="vs" id="{sid}"><div class="vt">PORTAAVIONES</div>'
             f'<div class="col" style="left:40px"><div class="cab"><svg width="78" height="52" viewBox="0 0 120 80">{bandera_es()}</svg><span>ESPAÑA</span></div></div>'
             f'<div class="col" style="left:520px"><div class="cab"><svg width="78" height="52" viewBox="0 0 120 80">{bandera_ma()}</svg><span>MARRUECOS</span></div></div>'
             + ico("portaaviones", 40, 220, 420, ES, "", 'id="port-es"')
             + f'<div class="nomb" style="left:60px" id="port-nom">«Juan Carlos I»</div>'
             + f'<div class="hueco" id="port-ma">✕</div><div class="cero" style="left:560px;top:560px" id="port-cero">NO TIENE</div></div>')
J(f'tl.set("#{sid}", {{opacity:0}}, 0); tl.fromTo("#{sid}", {{opacity:0, x:80}}, {{opacity:1, x:0, duration:0.35, immediateRender:false}}, {P("portaaviones") - 0.1:.2f}); tl.to("#{sid}", {{opacity:0, x:-80, duration:0.3}}, {FE(7) + 0.05:.2f});')
J(f'tl.fromTo("#port-es", {{x:-500}}, {{x:0, duration:0.7, ease:"power3.out", immediateRender:false}}, {P("portaaviones"):.2f});')
pop("#port-nom", P("portaaviones") + 0.5, 0.35)
pop("#port-ma", P("solo", 1) if False else P("portaaviones") + 0.7, 0.35, "scale:2, opacity:0")
pop("#port-cero", P("portaaviones") + 0.8, 0.35)
FX.append(("whoosh", P("portaaviones"))); FX.append(("sello", P("portaaviones") + 0.7))
# ranking
sid = "vs-rank"
def mk(lado, pos, col, flag):
    x = 90 + 820 * (pos - 1) / 144
    return (f'<div class="rk" id="rk-{lado}" style="left:{x - 70:.0f}px;border-color:{col}"><svg width="60" height="40" viewBox="0 0 120 80">{flag}</svg><b style="color:{col}">#{pos}</b></div>'
            f'<div class="rkp" id="rkp-{lado}" style="left:{x - 5:.0f}px;background:{col}"></div>')
PANEL.append(f'<div class="vs" id="{sid}"><div class="vt">RANKING MILITAR MUNDIAL</div>'
             f'<div class="rkbar"><i id="rkfill"></i></div><div class="rk1">1.º</div><div class="rk145">145.º</div>'
             + mk("es", 18, ES, bandera_es()) + mk("ma", 56, MA, bandera_ma())
             + f'<div class="rkn" style="left:60px">ESPAÑA <b style="color:{ES}">18.ª</b></div><div class="rkn" style="left:540px">MARRUECOS <b style="color:{MA}">56.ª</b></div></div>')
J(f'tl.set("#{sid}", {{opacity:0}}, 0); tl.fromTo("#{sid}", {{opacity:0, x:80}}, {{opacity:1, x:0, duration:0.35, immediateRender:false}}, {F(8):.2f}); tl.to("#{sid}", {{opacity:0, x:-80, duration:0.3}}, {FE(8) + 0.05:.2f});')
J(f'tl.fromTo("#rkfill", {{scaleX:0}}, {{scaleX:1, duration:0.8, ease:"power2.out", immediateRender:false}}, {F(8) + 0.2:.2f});')
for lado, w in (("es", "dieciocho"), ("ma", "cincuenta")):
    pop(f"#rk-{lado}", P(w), 0.45, "scale:0.3, opacity:0, y:-60")
    pop(f"#rkp-{lado}", P(w), 0.3, "scale:0, opacity:0")
    FX.append(("pop", P(w)))
nota("Global Firepower 2026", "145 países analizados", F(8) + 0.3, FE(8))
panel_out(FE(8) + 0.1)

# ================================================================== frases 9-10: Ceuta y Melilla, OTAN y UE
f9 = F(9)
cam(-4.15, 35.75, 1.9, f9 - 0.1, 1.3)
for nom in ("ceuta", "melilla"):
    J(f'tl.fromTo("#m-{nom} .etq", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.35, ease:"back.out(2)", immediateRender:false}}, {P(nom):.2f});')
    FX.append(("pop", P(nom)))
J(f'tl.fromTo(".pulso", {{attr:{{r:18}}, opacity:1}}, {{attr:{{r:70}}, opacity:0, duration:1.1, repeat:{int((DUR - f9) / 1.1)}, ease:"none", immediateRender:false}}, {f9:.2f});')
# paraguas OTAN: línea discontinua que cubre la península pero se corta en el mar
xo1, yo1 = W(-6.6, 36.45); xo2, yo2 = W(-1.6, 36.75)
MAPA.append(f'<g id="otan" opacity="0"><path d="M{xo1:.0f},{yo1:.0f} Q{(xo1 + xo2) / 2:.0f},{yo1 - 120:.0f} {xo2:.0f},{yo2:.0f}" stroke="#2f4f8a" stroke-width="9" stroke-dasharray="26 18" fill="none"/>'
            f'<rect x="{(xo1 + xo2) / 2 - 160:.0f}" y="{yo1 - 200:.0f}" width="320" height="78" rx="20" fill="#2f4f8a"/>'
            f'<text x="{(xo1 + xo2) / 2:.0f}" y="{yo1 - 147:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="44" fill="#fff">OTAN · art. 5</text></g>')
J(f'tl.to("#otan", {{opacity:1, duration:0.5}}, {P("otan") - 0.1:.2f});')
for nom in ("Ceuta", "Melilla"):
    x, y = W(*CIUD[nom])
    MAPA.append(f'<g class="nox" opacity="0"><circle cx="{x + 70:.0f}" cy="{y + 70:.0f}" r="34" fill="{RED}" stroke="#fff" stroke-width="6"/><path d="M{x + 56:.0f},{y + 56:.0f} L{x + 84:.0f},{y + 84:.0f} M{x + 84:.0f},{y + 56:.0f} L{x + 56:.0f},{y + 84:.0f}" stroke="#fff" stroke-width="8" stroke-linecap="round"/></g>'
                f'<g class="sie" opacity="0"><circle cx="{x + 70:.0f}" cy="{y + 70:.0f}" r="34" fill="{GRN}" stroke="#fff" stroke-width="6"/><path d="M{x + 54:.0f},{y + 70:.0f} L{x + 66:.0f},{y + 82:.0f} L{x + 88:.0f},{y + 58:.0f}" stroke="#fff" stroke-width="8" fill="none" stroke-linecap="round"/></g>'
                + "".join(f'<path class="eu" d="{(lambda cx, cy: "M" + " L".join(f"{cx + (9 if i % 2 == 0 else 4) * math.sin(i * math.pi / 5):.1f},{cy - (9 if i % 2 == 0 else 4) * math.cos(i * math.pi / 5):.1f}" for i in range(10)) + " Z")(x + 62 * math.cos(a), y + 62 * math.sin(a))}" fill="#ffcc00" opacity="0"/>' for a in [j * math.pi / 6 for j in range(12)]))
J(f'tl.to(".nox", {{opacity:1, duration:0.3, stagger:0.15}}, {P("automaticamente"):.2f});')
FX.append(("sello", P("automaticamente")))
nota("OTAN: el art. 5 solo cubre", "Europa y Norteamérica (art. 6)", P("otan"), FE(9) + 0.2, x=50, y=1330, rot=-3, w=420)
f10 = F(10)
J(f'tl.to(".nox, #otan", {{opacity:0, duration:0.3}}, {f10:.2f});')
J(f'tl.to(".eu", {{opacity:1, duration:0.2, stagger:0.04}}, {f10 + 0.1:.2f});')
J(f'tl.to(".sie", {{opacity:1, duration:0.3, stagger:0.15}}, {P("ayudar"):.2f});')
FX.append(("brillo", f10 + 0.1)); FX.append(("sello", P("ayudar")))
nota("UE: art. 42.7 = ayuda", "obligatoria a un socio atacado", f10 + 0.2, FE(10) + 0.2, x=560, y=1330, rot=3, w=440)

# ================================================================== frase 11: conclusión (flechas tachadas)
f11 = F(11)
cam(-5.0, 36.0, 1.0, f11 - 0.1, 1.2)
J(f'tl.to(".eu, .sie", {{opacity:0, duration:0.4}}, {f11:.2f});')
FLE = []
for k, (a, b) in enumerate((((-6.0, 35.3), (-5.9, 36.5)), ((-4.6, 35.2), (-4.4, 36.6)))):
    x1, y1 = W(*a); x2, y2 = W(*b)
    i = f"fle{k}"
    FLE.append(i)
    MAPA.append(f'<path id="{i}" style="opacity:0" d="M{x1:.0f},{y1:.0f} Q{(x1 + x2) / 2 + 60:.0f},{(y1 + y2) / 2:.0f} {x2:.0f},{y2:.0f}" stroke="{MA}" stroke-width="16" fill="none" stroke-linecap="round" pathLength="1" stroke-dasharray="0 1" marker-end="url(#punta)"/>')
J(f'tl.set("#{",#".join(FLE)}", {{opacity:1}}, {P("estrecho") - 0.4:.2f});')
J(f'tl.to("#{",#".join(FLE)}", {{strokeDasharray:"1 0", duration:0.7, stagger:0.2, ease:"power2.out"}}, {P("estrecho") - 0.4:.2f});')
OVR.append(f'<div id="imposible" class="sello2">CASI IMPOSIBLE</div>')
pop("#imposible", P("imposible"), 0.4, "scale:2.2, opacity:0, rotation:-25")
FX.append(("sello", P("imposible")))
J(f'tl.to("#imposible", {{opacity:0, duration:0.3}}, {P("tension") - 0.1:.2f});')
J(f'tl.to("#{",#".join(FLE)}", {{opacity:0, duration:0.3}}, {P("tension") - 0.1:.2f});')
J(f'tl.fromTo("#m-ceuta, #m-melilla", {{scale:1}}, {{scale:1.6, transformOrigin:"50% 50%", duration:0.35, yoyo:true, repeat:3, ease:"sine.inOut", immediateRender:false}}, {P("tension"):.2f});')
nota("Según los análisis:", "cruzar el Estrecho, casi imposible", f11 + 0.3, FE(11) + 0.1, x=60, y=1320, rot=-3, w=440)

# ================================================================== frase 12: economía (contenedores que van y vienen)
f12 = F(12)
CON = []
for k in range(6):
    ida = k % 2 == 0
    a = W(-5.62 + 0.08 * k, 35.82) if ida else W(-5.5 + 0.08 * k, 36.1)
    i = f"con{k}"
    CON.append(i)
    MOV.append(f'<g id="{i}" transform="translate({a[0] - 30:.0f},{a[1] - 30:.0f})" opacity="0"><svg width="60" height="60" viewBox="0 0 100 100" style="color:{ES if ida else MA}"><use href="#i-contenedor" fill="currentColor"/></svg></g>')
    J(f'tl.fromTo("#{i}", {{opacity:1, y:0}}, {{y:{-90 if ida else 90}, duration:1.6, repeat:1, ease:"sine.inOut", immediateRender:false}}, {f12 + 0.15 * k:.2f});')
    J(f'tl.to("#{i}", {{opacity:0, duration:0.3}}, {FE(12) + 0.3:.2f});')
OVR.append(f'<div id="nadie" class="cartel">UNA GUERRA ASÍ <b style="color:{RED}">NO LA GANA NADIE</b></div>')
pop("#nadie", P("nadie"), 0.4, "scale:1.5, opacity:0")
fuera("#nadie", FE(12) + 0.1)
nota("España: 1.er socio", "comercial de Marruecos", P("socio") - 0.2, FE(12) + 0.2, x=560, y=1320, rot=3, w=420)
FX.append(("brillo", P("socio")))

# ================================================================== frase 13: pregunta final
f13 = F(13)
cam(-4.6, 36.8, 0.42, f13 - 0.1, 1.3)
OVR.append(f'<div id="final"><div class="f1">¿TÚ QUÉ CREES</div><div class="f2">QUE PASARÍA?</div>'
           f'<div class="f3"><svg width="70" height="62" viewBox="0 0 100 90"><path d="M10,8 L90,8 Q96,8 96,14 L96,60 Q96,66 90,66 L40,66 L20,86 L22,66 L10,66 Q4,66 4,60 L4,14 Q4,8 10,8 Z" fill="{NAVY}"/>'
           f'<circle cx="30" cy="37" r="6" fill="#fff"/><circle cx="50" cy="37" r="6" fill="#fff"/><circle cx="70" cy="37" r="6" fill="#fff"/></svg>Te leo en comentarios</div></div>')
pop("#final", f13, 0.5, "scale:0.6, opacity:0")
J(f'tl.fromTo("#final .f3", {{y:30, opacity:0}}, {{y:0, opacity:1, duration:0.4, immediateRender:false}}, {P("leo"):.2f}); tl.set("#final .f3", {{opacity:0}}, 0);')
FX.append(("brillo", f13))

# respiración suave del mapa y del oleaje
J(f'tl.to("#olas", {{x:-160, duration:{DUR:.2f}, ease:"none"}}, 0);')
J(f'tl.to(".pin", {{y:"-=14", duration:0.8, yoyo:true, repeat:{int(DUR / 0.8)}, ease:"sine.inOut"}}, 0);')

# ------------------------------------------------------------------ cuenta atrás de 60 s
for s in range(1, 61):
    ts = min(s * DUR / 60, DUR - 0.12)
    J(f'tl.set("#crono-n", {{innerHTML:"{60 - s}"}}, {ts:.2f});')
    if s < 60:
        FX.append(("tic2" if 60 - s <= 5 else "tic", ts))
        if 60 - s <= 5:
            J(f'tl.fromTo("#crono", {{scale:1.12}}, {{scale:1, duration:0.3, ease:"power2.out", immediateRender:false}}, {ts:.2f});')
J(f'tl.fromTo("#crono-arc", {{strokeDashoffset:0}}, {{strokeDashoffset:1, duration:{DUR:.2f}, ease:"none", immediateRender:false}}, 0);')

# ------------------------------------------------------------------ subtítulos
CLAVE = set(norm(w) for w in ["catorce", "invadir", "marruecos", "cruzarlos", "sesenta", "doscientos", "ciento", "tanques", "mil", "mar", "aire",
                               "españa", "cazas", "dos", "ninguno", "portaaviones", "dieciocho", "cincuenta", "ceuta", "melilla", "otan",
                               "union", "ayudar", "imposible", "tension", "nadie", "socio", "comentarios"])
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

# ------------------------------------------------------------------ html
html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
@font-face{{font-family:"Caveat";src:url("assets/fonts/Caveat-700-latin.woff2") format("woff2");font-weight:700}}
@font-face{{font-family:"Marker";src:url("assets/fonts/permanent-marker-400.woff2") format("woff2")}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:{SEA1}}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif}}
#mundo{{position:absolute;left:0;top:0;width:10px;height:10px;overflow:visible}}
#cielo{{position:absolute;left:0;right:0;top:0;height:520px;background:linear-gradient(#fbfbf8 55%, rgba(251,251,248,0));pointer-events:none}}
#suelo{{position:absolute;left:0;right:0;bottom:0;height:560px;background:linear-gradient(rgba(244,241,234,0), #f4f1ea 70%);pointer-events:none}}
#velo{{position:absolute;inset:0;background:rgba(250,250,246,0.45);opacity:0;pointer-events:none}}
#panel{{position:absolute;left:36px;top:1010px;width:1008px;height:700px;background:#ffffff;border-radius:44px;box-shadow:0 30px 70px rgba(20,40,70,0.28);overflow:hidden}}
#panel::before{{content:"";position:absolute;left:0;right:0;top:0;height:16px;background:linear-gradient(90deg,{ES} 0 50%,{MA} 50% 100%)}}
.vs{{position:absolute;inset:0}}
.vt{{position:absolute;left:0;right:0;top:44px;text-align:center;font:900 52px Inter;color:{NAVY};letter-spacing:2px}}
.vbadge{{position:absolute;left:469px;top:225px;width:70px;height:70px;font-size:28px !important;border-radius:50%;background:{NAVY};color:#fff;font:900 40px Inter;display:flex;align-items:center;justify-content:center;box-shadow:0 8px 20px rgba(0,0,0,0.2)}}
.col{{position:absolute;top:130px;width:450px}}
.cab{{display:flex;align-items:center;gap:14px;font:900 34px Inter;color:{NAVY}}} .cab svg{{border-radius:6px;box-shadow:0 3px 8px rgba(0,0,0,0.2)}}
.num{{font:900 96px Inter;letter-spacing:-3px;line-height:1.1;margin-top:8px}}
.txt{{font:700 30px Inter;color:#6b7385;margin-top:-4px}}
.ic{{overflow:visible;filter:drop-shadow(0 4px 6px rgba(0,0,0,0.15))}}
.cero{{position:absolute;top:430px;font:900 64px Inter;color:#b6bcc8;border:6px dashed #c9ced8;border-radius:24px;padding:20px 30px}}
.gana{{position:absolute;top:120px;padding:8px 18px;border-radius:14px;background:{GRN};color:#fff;font:900 30px Inter;letter-spacing:2px;transform:rotate(-6deg)}}
.pie{{position:absolute;left:0;right:0;bottom:26px;text-align:center;font:700 24px Inter;color:#98a0b0}}
.nomb{{position:absolute;top:600px;font:800 italic 40px Inter;color:{NAVY}}}
.hueco{{position:absolute;left:640px;top:300px;width:220px;height:220px;border:8px dashed #d5d9e0;border-radius:30px;font:900 130px Inter;color:{RED};display:flex;align-items:center;justify-content:center}}
.rkbar{{position:absolute;left:90px;top:330px;width:820px;height:34px;border-radius:17px;background:#eef0f4;overflow:hidden}}
.rkbar i{{position:absolute;inset:0;background:linear-gradient(90deg,{GRN},#e8c547,{RED});transform-origin:0 50%;opacity:0.85}}
.rk1,.rk145{{position:absolute;top:380px;font:800 30px Inter;color:#8a92a3}} .rk1{{left:80px}} .rk145{{left:860px}}
.rk{{position:absolute;top:190px;width:140px;height:110px;border:6px solid;border-radius:22px;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 10px 20px rgba(0,0,0,0.15)}}
.rk b{{font:900 46px Inter;line-height:1}}
.rkp{{position:absolute;top:322px;width:10px;height:50px;border-radius:5px}}
.rkn{{position:absolute;top:480px;font:900 50px Inter;color:{NAVY}}} .rkn b{{font-size:84px}}
.nota{{position:absolute;padding:24px 26px 22px;background:linear-gradient(160deg,#fff6a8,#ffe76b);box-shadow:0 18px 30px rgba(0,0,0,0.25);border-radius:4px;z-index:30}}
.nota::before{{content:"";position:absolute;left:38%;top:-16px;width:110px;height:34px;background:rgba(255,255,255,0.55);transform:rotate(-3deg)}}
.nt{{font:700 46px Caveat;color:#1f2a44;line-height:1.05}} .ns{{font:700 38px Caveat;color:#4a5570;line-height:1.05;margin-top:4px}}
#titulo{{position:absolute;left:40px;right:40px;top:1120px;text-align:center;z-index:20}}
#titulo .t1,#titulo .t2{{display:inline-block;padding:6px 30px;font:900 104px Inter;letter-spacing:-2px;line-height:1.1;background:#fff;border-radius:22px;box-shadow:0 16px 40px rgba(0,0,0,0.25)}}
#titulo .t1{{color:{NAVY}}} #titulo .t2{{color:#fff;background:{MA};margin-top:14px}}
#titulo .t3{{margin-top:22px;font:900 54px Inter;color:{NAVY};display:flex;justify-content:center;align-items:center;gap:20px}}
#titulo .fl svg{{border-radius:6px;box-shadow:0 4px 10px rgba(0,0,0,0.25);vertical-align:middle}}
#sesenta{{position:absolute;left:0;right:0;top:1300px;margin:0 auto;width:760px;text-align:center;padding:22px;background:#fff;border-radius:30px;font:800 46px Inter;color:{NAVY};box-shadow:0 16px 40px rgba(0,0,0,0.2)}}
#sesenta span{{font:900 70px Inter;color:{MA}}}
.cartel{{position:absolute;left:60px;right:60px;top:1500px;text-align:center;padding:24px;background:#fff;border-radius:30px;font:900 56px Inter;color:{NAVY};box-shadow:0 16px 40px rgba(0,0,0,0.22);z-index:20}}
.sello2{{position:absolute;left:190px;top:1020px;padding:14px 40px;border:10px solid {RED};border-radius:24px;color:{RED};font:900 80px Inter;letter-spacing:4px;background:rgba(255,255,255,0.85);transform:rotate(-8deg);z-index:20}}
#final{{position:absolute;left:60px;right:60px;top:1100px;text-align:center;padding:50px 30px;background:#fff;border-radius:44px;box-shadow:0 30px 70px rgba(20,40,70,0.3);z-index:20}}
#final .f1{{font:900 96px Inter;color:{NAVY};line-height:1}} #final .f2{{font:900 96px Inter;color:{MA};line-height:1.1}}
#final .f3{{margin-top:26px;font:800 50px Inter;color:#4a5570;display:flex;align-items:center;justify-content:center;gap:18px}}
#crono{{position:absolute;left:845px;top:470px;width:200px;height:200px;filter:drop-shadow(0 10px 18px rgba(20,40,70,0.25));z-index:25}}
#marca{{position:absolute;left:0;right:0;top:1775px;text-align:center;font:700 28px Inter;color:#1d2433;opacity:0.4;pointer-events:none;z-index:40}}
#subs{{position:absolute;left:70px;right:70px;top:250px;height:220px;z-index:40}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:500 62px Inter;color:rgba(40,48,40,0.32);line-height:1.22}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:4px solid {MA};border-radius:6px;background:{MA}22;opacity:0}}
.key b{{position:absolute;width:16px;height:16px;border-radius:50%;background:#fff;border:4px solid {MA};opacity:0}}
.key .d1{{left:-12px;top:-12px}} .key .d2{{right:-12px;bottom:-10px}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <svg width="0" height="0" style="position:absolute"><defs>{SYMS}
    <linearGradient id="mar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SEA1}"/><stop offset="1" stop-color="{SEA2}"/></linearGradient>
    <pattern id="olas" width="160" height="60" patternUnits="userSpaceOnUse"><path d="M0,30 Q20,18 40,30 T80,30 T120,30 T160,30" stroke="#ffffff" stroke-width="3" fill="none" opacity="0.6"/></pattern>
    <filter id="sombra" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="6" stdDeviation="6" flood-opacity="0.3"/></filter>
    <marker id="punta" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="3" markerHeight="3" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="{MA}"/></marker>
  </defs></svg>
  <svg id="mundo" width="10" height="10" data-layout-allow-overflow data-layout-ignore>{"".join(MAPA)}{"".join(MOV)}</svg>
  <div id="cielo"></div><div id="suelo"></div>
  <div id="velo"></div>
  <div id="panel" data-layout-allow-overflow>{"".join(PANEL)}</div>
  {"".join(OVR)}
  <svg id="crono" width="200" height="200" viewBox="0 0 170 170" data-layout-allow-overflow>
    <rect x="72" y="2" width="26" height="18" rx="4" fill="#2b2b2b"/><circle cx="85" cy="92" r="72" fill="#ffffff" stroke="#2b2b2b" stroke-width="6"/>
    <circle id="crono-arc" cx="85" cy="92" r="58" fill="none" stroke="{MA}" stroke-width="14" pathLength="1" stroke-dasharray="1" transform="rotate(-90 85 92)"/>
    <text id="crono-n" x="85" y="110" text-anchor="middle" font-family="Marker" font-size="50" fill="#2b2b2b">60</text>
  </svg>
  <div id="marca">@mundo.supuesto</div>
  <div id="subs" data-layout-allow-overlap>{"".join(SUBS)}</div>
  <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
tl.set("#panel", {{y:1000}}, 0);
{chr(10).join(tl)}
tl.to({{}}, {{duration:0.01}}, {DUR - 0.01});
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>"""
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump(FX, open(os.path.join(BASE, "efectos.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones")

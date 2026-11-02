#!/usr/bin/env python3
"""«¿Y si Marruecos invadiera España?» v2 (misma voz que v1, 0 créditos). Mejoras (MEJORA_CONTINUA.md):
mapa en 3D inclinado tipo mesa de guerra con nubes en parallax, entrada de cine (picado al Estrecho + sacudida +
destello), transiciones con barrido (whip) y sonido, cartas VS a pantalla completa con números que RUEDAN, iconos que
entran marchando, sellos con sacudida, ranking que se desplaza, grano de película, viñeta, destellos de luz,
subtítulos tipo karaoke con píldora y diseño de sonido (subida antes de cada dato, golpe al revelar).
  python3 gen.py → index.html + efectos.json
"""
import json, math, os, re, unicodedata, random
from geo import W, poly, isla, SPAIN, PORTUGAL, FRANCIA, MARRUECOS, ARGELIA, CIUD, K, CX

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
rnd = random.Random(5)

ES, ES2, MA, MA2 = "#f2b630", "#d98e0b", "#e0483c", "#a8261d"
NAVY, GRN = "#16203a", "#25a35a"
SEA1, SEA2 = "#7fd0f2", "#3fa6d8"

# ------------------------------------------------------------------ mapa (mundo SVG)
MAPA = ['<rect x="-6000" y="-6000" width="16000" height="16000" fill="url(#mar)"/>',
        '<rect id="olas" x="-6000" y="-6000" width="16000" height="16000" fill="url(#olasp)" opacity="0.45"/>']
for pts, fill, sh in ((FRANCIA, "#ece4d4", 1), (ARGELIA, "#ece4d4", 1), (PORTUGAL, "#ece4d4", 1), (MARRUECOS, "#f0a99f", 1), (SPAIN, "#f7d27a", 1)):
    d = poly(pts)
    MAPA.append(f'<path d="{d}" fill="#000" opacity="0.18" transform="translate(10,16)"/>')       # sombra (relieve)
    MAPA.append(f'<path d="{d}" fill="{fill}" stroke="#ffffff" stroke-width="8" stroke-linejoin="round"/>')
MAPA.append(f'<g fill="#f7d27a" stroke="#ffffff" stroke-width="5">{isla(2.95, 39.62, 0.42, 0.24, -20)}{isla(4.10, 39.97, 0.2, 0.08, -10)}{isla(1.42, 38.98, 0.17, 0.12)}</g>')
# relieve: sierras y ríos sutiles para que no sea plano
for lon, lat, rx, ry, rot in ((-4.0, 40.6, 1.6, 0.22, -10), (-3.2, 37.1, 1.4, 0.18, -8), (-5.0, 31.6, 2.6, 0.32, -25), (-4.4, 34.95, 1.3, 0.16, 5), (-0.8, 42.7, 1.8, 0.15, -6)):
    x, y = W(lon, lat)
    MAPA.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rx * K * CX:.0f}" ry="{ry * K:.0f}" fill="#7a4b1c" opacity="0.10" transform="rotate({rot} {x:.0f} {y:.0f})"/>')
for txt, lon, lat, col, fs in (("ESPAÑA", -4.0, 39.3, "#a87808", 120), ("MARRUECOS", -7.0, 31.9, "#a3352c", 120), ("PORTUGAL", -8.2, 39.6, "#b4ab99", 70), ("ARGELIA", 1.0, 33.0, "#b4ab99", 70)):
    x, y = W(lon, lat)
    MAPA.append(f'<text class="pais" x="{x:.0f}" y="{y:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="{fs}" letter-spacing="16" fill="{col}" opacity="0.8">{txt}</text>')
for nom in ("Madrid", "Rabat", "Tarifa", "Tánger"):
    x, y = W(*CIUD[nom])
    dy = -26 if nom in ("Madrid", "Tarifa") else 56
    MAPA.append(f'<g><circle cx="{x:.0f}" cy="{y:.0f}" r="11" fill="{NAVY}" stroke="#fff" stroke-width="5"/>'
                f'<text x="{x + 18:.0f}" y="{y + dy:.0f}" font-family="Inter" font-weight="800" font-size="34" fill="{NAVY}" stroke="#ffffff" stroke-width="7" paint-order="stroke">{nom}</text></g>')
def bandera_es(w=120, h=80):
    return f'<rect width="{w}" height="{h}" rx="8" fill="#c60b1e"/><rect y="{h / 4}" width="{w}" height="{h / 2}" fill="#ffc400"/>'
def bandera_ma(w=120, h=80):
    cx, cy, r = w / 2, h / 2, h * 0.3
    pts = [(cx + r * math.sin(i * 4 * math.pi / 5), cy - r * math.cos(i * 4 * math.pi / 5)) for i in range(5)]
    d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + " Z"
    return f'<rect width="{w}" height="{h}" rx="8" fill="#c1272d"/><path d="{d}" fill="none" stroke="#006233" stroke-width="{h * 0.06:.1f}" stroke-linejoin="round"/>'
for nom, fn in (("Madrid", bandera_es), ("Rabat", bandera_ma)):
    x, y = W(*CIUD[nom])
    MAPA.append(f'<g class="pin" id="pin-{norm(nom)}" style="opacity:0" transform="translate({x - 60:.0f},{y - 175:.0f})"><path d="M60,80 L60,170" stroke="{NAVY}" stroke-width="7"/><g filter="url(#sombra)">{fn()}</g></g>')
for nom in ("Ceuta", "Melilla"):
    x, y = W(*CIUD[nom])
    MAPA.append(f'<g id="m-{norm(nom)}"><circle class="pulso" cx="{x:.0f}" cy="{y:.0f}" r="18" fill="none" stroke="{ES2}" stroke-width="6" style="opacity:0"/>'
                f'<circle cx="{x:.0f}" cy="{y:.0f}" r="14" fill="{ES}" stroke="#fff" stroke-width="6"/>'
                f'<g class="etq" style="opacity:0"><rect x="{x - 110:.0f}" y="{y - 104:.0f}" width="220" height="64" rx="18" fill="{NAVY}"/>'
                f'<text x="{x:.0f}" y="{y - 59:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="38" fill="#fff">{nom.upper()}</text></g></g>')

ICON = {
    "soldado": '<circle cx="50" cy="22" r="13"/><path d="M33,20 Q50,0 67,20 L67,24 L33,24 Z"/><path d="M30,42 Q50,32 70,42 L70,68 L62,68 L60,96 L53,96 L50,70 L47,96 L40,96 L38,68 L30,68 Z"/>',
    "tanque": '<rect x="6" y="58" width="88" height="24" rx="12"/><rect x="16" y="42" width="58" height="18" rx="5"/><rect x="32" y="28" width="30" height="17" rx="6"/><rect x="60" y="32" width="38" height="6" rx="3"/><g fill="#000" opacity="0.25"><circle cx="20" cy="70" r="6"/><circle cx="36" cy="70" r="6"/><circle cx="52" cy="70" r="6"/><circle cx="68" cy="70" r="6"/><circle cx="84" cy="70" r="6"/></g>',
    "caza": '<path d="M50,4 L56,30 L92,58 L92,66 L56,56 L55,80 L68,90 L68,95 L50,90 L32,95 L32,90 L45,80 L44,56 L8,66 L8,58 L44,30 Z"/>',
    "submarino": '<rect x="6" y="46" width="88" height="26" rx="13"/><rect x="38" y="30" width="20" height="20" rx="4"/><rect x="46" y="18" width="4" height="14"/><path d="M90,59 L99,48 L99,70 Z"/>',
    "barco": '<path d="M4,60 L96,60 L84,80 L16,80 Z"/><rect x="34" y="40" width="30" height="20"/><rect x="44" y="26" width="10" height="14"/><rect x="62" y="48" width="18" height="12"/><rect x="48" y="12" width="2" height="16"/>',
    "portaaviones": '<path d="M2,56 L98,50 L94,62 L86,74 L10,74 Z"/><rect x="62" y="34" width="12" height="18"/><rect x="66" y="24" width="4" height="12"/>',
    "contenedor": '<path d="M6,62 L94,62 L84,82 L16,82 Z"/><rect x="18" y="40" width="18" height="20"/><rect x="38" y="40" width="18" height="20"/><rect x="58" y="40" width="18" height="20"/><rect x="28" y="22" width="18" height="17"/><rect x="48" y="22" width="18" height="17"/>',
}
SYMS = "".join(f'<symbol id="i-{k}" viewBox="0 0 100 100">{v}</symbol>' for k, v in ICON.items())
def svgico(k, col, s, extra=""):
    return f'<svg width="{s}" height="{s}" viewBox="0 0 100 100" style="color:{col};overflow:visible" {extra}><use href="#i-{k}" fill="currentColor"/></svg>'

# ------------------------------------------------------------------ utilidades de animación
VIEW_Y = 1060
def cam(lon, lat, z, t, dur=1.2, ease="power3.inOut", tilt=None):
    x, y = W(lon, lat)
    J(f'tl.to("#mundo", {{x:{540 - x * z:.0f}, y:{VIEW_Y - y * z:.0f}, scale:{z}, duration:{dur:.2f}, ease:"{ease}"}}, {t:.2f});')
    if tilt is not None:
        J(f'tl.to("#mesa", {{rotationX:{tilt}, duration:{dur:.2f}, ease:"{ease}"}}, {t:.2f});')
def cam_set(lon, lat, z, tilt=0):
    x, y = W(lon, lat)
    J(f'tl.set("#mundo", {{transformOrigin:"0 0", x:{540 - x * z:.0f}, y:{VIEW_Y - y * z:.0f}, scale:{z}}}, 0); tl.set("#mesa", {{rotationX:{tilt}}}, 0);')
def pop(sel, t, d=0.45, frm="scale:0.3, opacity:0", ease="back.out(2.2)"):
    J(f'tl.set("{sel}", {{opacity:0}}, 0);')
    J(f'tl.fromTo("{sel}", {{{frm}}}, {{scale:1, opacity:1, x:0, y:0, rotation:0, duration:{d}, ease:"{ease}", immediateRender:false}}, {t:.2f});')
def fuera(sel, t, d=0.3):
    J(f'tl.to("{sel}", {{opacity:0, duration:{d}}}, {t:.2f});')
def sacude(t, f=16):
    J(f'tl.fromTo("#todo", {{x:{f}, y:{-f * 0.6:.0f}}}, {{x:0, y:0, duration:0.45, ease:"elastic.out(1.2,0.25)", immediateRender:false}}, {t:.2f});')
def punch(t, s=1.05):
    J(f'tl.fromTo("#todo", {{scale:{s}}}, {{scale:1, duration:0.5, ease:"power3.out", immediateRender:false}}, {t:.2f});')
def leak(t, d=1.1):
    J(f'tl.fromTo("#leak", {{opacity:0, x:-200}}, {{opacity:0.75, x:0, duration:{d * 0.4:.2f}, ease:"power2.out", immediateRender:false}}, {t:.2f}); tl.to("#leak", {{opacity:0, x:200, duration:{d * 0.6:.2f}, ease:"power2.in"}}, {t + d * 0.4:.2f});')
def flash(t, o=0.85):
    J(f'tl.fromTo("#flash", {{opacity:{o}}}, {{opacity:0, duration:0.5, ease:"power2.out", immediateRender:false}}, {t:.2f});')
def whip(t, dirx=1):
    """Barrido rápido entre escenas (rayas + destello + whoosh)."""
    J(f'tl.fromTo("#whip", {{x:{-1500 * dirx}, opacity:1}}, {{x:{1500 * dirx}, duration:0.42, ease:"power2.inOut", immediateRender:false}}, {t - 0.21:.2f}); tl.set("#whip", {{opacity:0}}, {t + 0.22:.2f});')
    FX.append(("whoosh", t - 0.25))
def riser(t_hit, d=1.0):
    FX.append(("riser", max(0, t_hit - d)))

OVR, MOV, CARDS = [], [], []
def nota(txt, sub, t, t_out, x=56, y=1590, rot=-4, w=420):
    i = nid("nt")
    OVR.append(f'<div id="{i}" class="nota" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({rot}deg)"><div class="nt">{txt}</div><div class="ns">{sub}</div></div>')
    J(f'tl.set("#{i}", {{opacity:0}}, 0); tl.fromTo("#{i}", {{y:80, opacity:0, rotation:{rot + 10}}}, {{y:0, opacity:1, rotation:{rot}, duration:0.5, ease:"back.out(2)", immediateRender:false}}, {t:.2f});')
    J(f'tl.to("#{i}", {{opacity:0, y:40, duration:0.25}}, {t_out:.2f});')
    FX.append(("posit", t + 0.2))

def rueda(i, valor, size, col):
    """Número con columnas de dígitos que ruedan (number-wheel del kit, generado en Python)."""
    h = [f'<span class="rueda" id="{i}" style="font-size:{size}px;color:{col}">']
    k = 0
    for ch in valor:
        if ch.isdigit():
            strip = "".join(f"<span>{d}</span>" for d in list(range(10)) * 2)
            h.append(f'<span class="dg"><span class="st" id="{i}-{k}" data-d="{ch}">{strip}</span></span>')
            k += 1
        else:
            h.append(f'<span class="sep">{ch}</span>')
    h.append('</span>')
    return "".join(h), k
def gira(i, valor, n, t, d=1.1):
    if valor.strip("0") == "":      # un «0» solo aparece; si rueda parece que pasa por 6, 7…
        return
    k = 0
    for ch in valor:
        if ch.isdigit():
            J(f'tl.fromTo("#{i}-{k}", {{y:"0em"}}, {{y:"-{10 + int(ch)}em", duration:{d + 0.12 * (n - k):.2f}, ease:"power4.out", immediateRender:false}}, {t:.2f});')
            k += 1
    for s in range(int((d + 0.3) / 0.07)):
        if s % 2 == 0:
            FX.append(("clic", t + s * 0.07))

TJ_X, TJ_Y, TJ_W, TJ_H = 70, 690, 940, 800
def entra_sale(cid, t_in, t_out, entra, sale):
    J(f'tl.set("#{cid}", {{opacity:0}}, 0); tl.set("#{cid}", {{opacity:1}}, {t_in:.2f}); tl.set("#{cid}", {{opacity:0}}, {t_out + 0.5:.2f});')
    if entra == "arriba":
        J(f'tl.fromTo("#{cid}", {{y:1100, rotation:4}}, {{y:0, rotation:0, duration:0.6, ease:"back.out(1.3)", immediateRender:false}}, {t_in:.2f});')
    else:
        J(f'tl.fromTo("#{cid}", {{x:1150, rotation:3}}, {{x:0, rotation:0, duration:0.5, ease:"power3.out", immediateRender:false}}, {t_in:.2f});')
    if sale == "izq":
        J(f'tl.to("#{cid}", {{x:-1150, rotation:-3, duration:0.45, ease:"power3.in"}}, {t_out:.2f});')
    else:
        J(f'tl.to("#{cid}", {{y:1150, rotation:-4, duration:0.5, ease:"power3.in"}}, {t_out:.2f});')
    FX.append(("whoosh", t_in)); FX.append(("whoosh", t_out))

def cabecera(cid, lado):
    flag, nom = (bandera_es(), "ESPAÑA") if lado == "es" else (bandera_ma(), "MARRUECOS")
    return f'<div class="tjcab"><svg width="78" height="52" viewBox="0 0 120 80">{flag}</svg><span>{nom}</span></div>'

def carta(cid, titulo, t_in, t_out, es, ma, gana, unidad="", entra="arriba", sale="izq"):
    """Tarjeta VS COMPACTA (no ocupa la pantalla): dos columnas claras, VS pequeño entre los nombres, número que
    rueda solo cuando se dice, iconos del mismo tamaño en las dos columnas y la que gana se ilumina."""
    h = [f'<div class="tj" id="{cid}"><div class="tjbar"></div><div class="tjt">{titulo}</div><div class="tjvs">VS</div>']
    for lado, d, x0 in (("es", es, 20), ("ma", ma, 520)):
        col = ES2 if lado == "es" else MA
        rid = f"{cid}-{lado}-n"
        r_html, nd = rueda(rid, d["valor"], d.get("num", 88), col)
        h.append(f'<div class="tjc" id="{cid}-{lado}" style="left:{x0}px"><div class="tjfx"></div>{cabecera(cid, lado)}'
                 f'<div class="tjn" id="{cid}-{lado}-num">{r_html}</div><div class="tjx">{d.get("txt", "")}</div>')
        n_ic, cols, sz = d["iconos"], d.get("cols", 5), d.get("tam", 62)
        ancho = cols * (sz + 8) - 8
        ids = []
        for k in range(n_ic):
            r_, c_ = divmod(k, cols)
            iid = f"{cid}-{lado}-i{k}"; ids.append("#" + iid)
            h.append(f'<div class="vic" id="{iid}" style="left:{(400 - ancho) / 2 + c_ * (sz + 8):.0f}px;top:{300 + r_ * (sz + 6)}px">{svgico(d["icono"], col, sz)}</div>')
        if n_ic == 0:
            h.append(f'<div class="tjcero" id="{cid}-{lado}-cero">NINGUNO</div>')
            pop(f"#{cid}-{lado}-cero", d["cuando"] + 0.1, 0.4, "scale:1.8, opacity:0, rotation:-10")
            FX.append(("golpe", d["cuando"] + 0.1))
        else:
            J(f'tl.set("{",".join(ids)}", {{opacity:0}}, 0);')
            J(f'tl.fromTo("{",".join(ids)}", {{opacity:0, scale:0, y:30}}, {{opacity:1, scale:1, y:0, duration:0.35, stagger:{min(0.06, 0.9 / n_ic):.3f}, ease:"back.out(2.5)", immediateRender:false}}, {d["cuando"]:.2f});')
            FX.append(("pop", d["cuando"]))
        h.append('</div>')
        J(f'tl.set("#{cid}-{lado}-num", {{opacity:0}}, 0); tl.to("#{cid}-{lado}-num", {{opacity:1, duration:0.15}}, {d["cuando"]:.2f});')
        gira(rid, d["valor"], nd, d["cuando"], 0.9)
    if unidad:
        h.append(f'<div class="tju">{unidad}</div>')
    if gana:
        pierde = "ma" if gana == "es" else "es"
        tg = max(es["cuando"], ma["cuando"]) + 0.5
        h.append(f'<div class="tjg" id="{cid}-g" style="left:{20 if gana == "es" else 520}px">VENTAJA</div>')
        pop(f"#{cid}-g", tg, 0.35, "scale:2.2, opacity:0, rotation:-15", "back.out(3)")
        J(f'tl.set("#{cid}-{gana} .tjfx", {{opacity:0}}, 0); tl.to("#{cid}-{gana} .tjfx", {{opacity:1, duration:0.3}}, {tg:.2f}); tl.to("#{cid}-{pierde}", {{opacity:0.45, duration:0.3}}, {tg:.2f});')
        FX.append(("sello", tg))
    h.append('</div>')
    CARDS.append("".join(h))
    J(f'tl.fromTo("#{cid} .tjvs", {{scale:0, rotation:-120}}, {{scale:1, rotation:0, duration:0.5, ease:"back.out(2.5)", immediateRender:false}}, {t_in + 0.3:.2f});')
    entra_sale(cid, t_in, t_out, entra, sale)

# ================================================================== 1) GANCHO: picado al Estrecho
cam_set(-4.5, 36.5, 0.42, 0)
cam(-5.5, 35.98, 1.45, 0.0, 1.25, "power3.inOut", tilt=34)
cam(-5.5, 35.98, 1.25, 1.25, FE(1) - 1.25, "sine.inOut")
J('tl.fromTo("#todo", {rotation:-2}, {rotation:0, duration:1.25, ease:"power3.inOut", immediateRender:false}, 0);')
sacude(1.2, 18); leak(0.05, 1.4)
FX.append(("boom", 0.0)); FX.append(("whoosh", 0.05)); FX.append(("golpe", 1.2))
# regla de 14 km
xa, ya = W(-5.61, 36.01); xb, yb = W(-5.42, 35.915)
MAPA.append(f'<g id="regla"><path id="regla-l" d="M{xa:.0f},{ya:.0f} L{xb:.0f},{yb:.0f}" stroke="{NAVY}" stroke-width="8" stroke-dasharray="1" pathLength="1" fill="none" style="stroke-dashoffset:1"/>'
            f'<g id="regla-t" style="opacity:0"><rect x="{(xa + xb) / 2 - 40:.0f}" y="{(ya + yb) / 2 - 36:.0f}" width="170" height="70" rx="16" fill="#fff" stroke="{NAVY}" stroke-width="6"/>'
            f'<text x="{(xa + xb) / 2 + 45:.0f}" y="{(ya + yb) / 2 + 14:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="44" fill="{NAVY}">14 km</text></g></g>')
J(f'tl.to("#regla-l", {{strokeDashoffset:0, duration:0.5, ease:"power2.out"}}, {P("catorce") - 0.35:.2f});')
pop("#regla-t", P("catorce"), 0.45, "scale:2, opacity:0")
FX.append(("pop", P("catorce")))
LAN = []
for k, (lon, lat) in enumerate(((-6.35, 35.86), (-6.05, 35.84), (-5.80, 35.86), (-4.55, 35.98), (-4.25, 36.0))):
    x, y = W(lon, lat)
    i = f"lan{k}"; LAN.append("#" + i)
    MOV.append(f'<g id="{i}" transform="translate({x:.0f},{y:.0f})"><g transform="scale(0.6)">'
               f'<path d="M-9,40 L-34,130 M9,40 L34,130" stroke="#ffffff" stroke-width="8" stroke-linecap="round" opacity="0.85"/>'
               f'<path d="M0,-44 C16,-22 15,28 11,40 L-11,40 C-15,28 -16,-22 0,-44 Z" fill="{MA}" stroke="#fff" stroke-width="5"/></g></g>')
J(f'tl.to("{",".join(LAN)}", {{y:"-=50", duration:{P("cruzarlos"):.2f}, ease:"sine.inOut"}}, 0);')
xr, yr = W(-5.55, 36.06)
MAPA.append("".join(f'<circle class="rad" cx="{xr:.0f}" cy="{yr:.0f}" r="20" fill="none" stroke="{ES2}" stroke-width="5"/>' for _ in range(3)))
J(f'tl.fromTo(".rad", {{attr:{{r:20}}, opacity:0.9}}, {{attr:{{r:170}}, opacity:0, duration:1.3, stagger:0.43, repeat:{int(FE(1) / 1.3) + 1}, ease:"none", immediateRender:false}}, 0);')
xq, yq = W(-5.50, 35.96)
MAPA.append(f'<g id="preg" style="opacity:0"><circle cx="{xq:.0f}" cy="{yq:.0f}" r="48" fill="{MA}" stroke="#fff" stroke-width="7"/><text x="{xq:.0f}" y="{yq + 22:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="64" fill="#fff">?</text></g>')
pop("#preg", P("cruzarlos"), 0.4, "scale:3, opacity:0")
FX.append(("golpe", P("cruzarlos"))); sacude(P("cruzarlos"), 10)
OVR.append('<div id="titulo"><div class="t1">¿Y SI <span>MARRUECOS</span></div><div class="t2">INVADIERA ESPAÑA?</div></div>')
J('tl.fromTo("#titulo .t1", {scale:1.22, y:-20}, {scale:1, y:0, duration:0.38, ease:"power4.out", immediateRender:false}, 0);')
J('tl.fromTo("#titulo .t2", {scale:1.22, y:20}, {scale:1, y:0, duration:0.38, ease:"power4.out", immediateRender:false}, 0.0);')
J(f'tl.to("#titulo", {{y:-10, duration:0.8, yoyo:true, repeat:{int(F(2) / 0.8)}, ease:"sine.inOut"}}, 0.5);')
FX.append(("golpe", 0.12))
J(f'tl.to("#titulo", {{opacity:0, y:-200, scale:0.85, duration:0.4, ease:"power3.in"}}, {F(2) + 0.3:.2f});')
J(f'tl.to("{",".join(LAN)}, #preg, #regla, .rad", {{opacity:0, duration:0.4}}, {F(2) + 0.2:.2f});')

# ================================================================== 2) vista general + «60 segundos»
cam(-4.6, 36.8, 0.42, F(2), 1.3, tilt=18)
FX.append(("whoosh", F(2)))
for k, nom in enumerate(("madrid", "rabat")):
    pop(f"#pin-{nom}", F(2) + 0.7 + 0.2 * k, 0.5, "scale:0, opacity:0, y:-140", "bounce.out")
    FX.append(("pop", F(2) + 0.9 + 0.2 * k))
OVR.append(f'<div id="sesenta"><b>60</b><span>SEGUNDOS<br>DATOS REALES</span></div>')
pop("#sesenta", P("sesenta") - 0.05, 0.45, "scale:0, opacity:0, rotation:-20")
FX.append(("sello", P("sesenta")))
fuera("#sesenta", FE(2) + 0.05)
J(f'tl.fromTo("#crono", {{scale:0, rotation:-90}}, {{scale:1, rotation:0, duration:0.6, ease:"back.out(2.5)", immediateRender:false}}, {P("sesenta"):.2f}); tl.set("#crono", {{scale:0}}, 0);')

# ================================================================== 3-4) tarjetas: soldados y tanques
J(f'tl.to("#velo", {{opacity:1, duration:0.4}}, {F(3) - 0.1:.2f}); tl.to("#velo", {{opacity:0, duration:0.4}}, {FE(4) + 0.2:.2f});')
riser(P("doscientos"), 0.9)
carta("c-sold", "SOLDADOS EN ACTIVO", F(3), F(4) - 0.05, dict(valor="120.000", txt="soldados", icono="soldado", iconos=12, cuando=P("ciento")),
      dict(valor="200.000", txt="soldados", icono="soldado", iconos=20, cuando=P("doscientos")), "ma", "1 muñeco = 10.000 soldados")
nota("Fuente: IISS y", "Euronews (2026)", F(3) + 0.7, F(4) - 0.05, x=60, y=1530, rot=-3, w=360)
riser(P("trescientos"), 0.9)
carta("c-tanq", "TANQUES", F(4), FE(4) + 0.05, dict(valor="298", txt="carros de combate", icono="tanque", iconos=3, cuando=P("frente"), tam=70),
      dict(valor="1.346", txt="carros de combate", icono="tanque", iconos=13, cuando=P("trescientos"), tam=70), "ma", "1 tanque = 100 tanques", entra="der", sale="abajo")
nota("Fuente: Global", "Firepower 2026", F(4) + 0.6, FE(4) + 0.05, x=640, y=1530, rot=3, w=360)

# ================================================================== 5) el mar y el aire (mapa 3D)
f5 = F(5)
whip(f5)
cam(-5.5, 36.02, 1.7, f5 - 0.15, 0.9, tilt=40)
BAR = []
for k, lon in enumerate((-6.25, -5.95, -5.65, -5.35, -5.05, -4.75)):
    x, y = W(lon, 36.06 if k % 2 else 36.0)
    i = f"bar{k}"; BAR.append("#" + i)
    MOV.append(f'<g id="{i}" style="opacity:0" transform="translate({x - 40:.0f},{y - 40:.0f})"><ellipse cx="40" cy="70" rx="34" ry="8" fill="#000" opacity="0.25"/>{svgico("barco", "#24407a", 80)}</g>')
J(f'tl.fromTo("{",".join(BAR)}", {{opacity:0, y:"-=90"}}, {{opacity:1, y:"+=90", duration:0.55, stagger:0.1, ease:"bounce.out", immediateRender:false}}, {P("mar", 2) - 0.1:.2f});')
FX.append(("whoosh", P("mar", 2)))
CAZ = []
for k, (x0, y0) in enumerate(((150, -300), (430, -420), (710, -330))):
    i = f"caz{k}"; CAZ.append("#" + i)
    OVR.append(f'<div class="cazav" id="{i}" style="left:{x0}px;top:0px"><div class="estela"></div>{svgico("caza", NAVY, 150, "class=cz")}</div>')
ta = P("aire") - 0.5
J(f'tl.set("{",".join(CAZ)}", {{opacity:0}}, 0); tl.set("{",".join(CAZ)}", {{opacity:1}}, {ta:.2f});')
J(f'tl.fromTo("{",".join(CAZ)}", {{y:-500, rotation:180}}, {{y:2300, rotation:180, duration:1.3, stagger:0.18, ease:"power1.in", immediateRender:false}}, {ta:.2f});')
FX.append(("whoosh", ta + 0.2)); FX.append(("whoosh", ta + 0.5)); sacude(ta + 0.6, 10)
OVR.append(f'<div id="manda" class="cartel">MAR Y AIRE: <b style="color:{ES2}">ESPAÑA</b></div>')
pop("#manda", P("manda"), 0.4, "scale:2, opacity:0")
FX.append(("sello", P("manda"))); punch(P("manda"))
fuera("#manda", FE(5))
nota("Para invadir hay que", "cruzar 14 km de mar", f5 + 0.3, FE(5), x=60, y=1580, rot=-3)
J(f'tl.to("{",".join(BAR)}", {{opacity:0, duration:0.3}}, {FE(5) + 0.05:.2f});')

# ================================================================== 6-8) tarjetas: cazas, submarinos, portaaviones, ranking
J(f'tl.to("#velo", {{opacity:1, duration:0.4}}, {F(6) - 0.1:.2f}); tl.to("#velo", {{opacity:0, duration:0.4}}, {FE(8) + 0.3:.2f});')
riser(P("treinta"), 0.8)
carta("c-caz", "AVIONES DE CAZA", F(6), F(7) - 0.05, dict(valor="136", txt="cazas", icono="caza", iconos=14, cuando=P("treinta")),
      dict(valor="84", txt="cazas", icono="caza", iconos=8, cuando=P("ochenta")), "es", "1 avión = 10 cazas")
nota("Fuente: Global", "Firepower 2026", F(6) + 0.5, FE(8) + 0.05, x=640, y=1530, rot=3, w=360)
tp = P("portaaviones") - 0.15
carta("c-sub", "SUBMARINOS", F(7), tp, dict(valor="2", txt="en servicio", icono="submarino", iconos=2, cuando=P("dos"), cols=2, tam=150),
      dict(valor="0", txt="submarinos", icono="submarino", iconos=0, cuando=P("ninguno")), "es", "Fuente: Armada y GFP 2026", entra="der", sale="izq")
# portaaviones (tarjeta compacta propia)
CARDS.append(f'<div class="tj" id="c-port"><div class="tjbar"></div><div class="tjt">PORTAAVIONES</div><div class="tjvs">VS</div>'
             f'<div class="tjc" id="c-port-es" style="left:20px"><div class="tjfx"></div>{cabecera("c-port", "es")}<div class="tjn" style="color:{ES2}">1</div><div class="tjx">«Juan Carlos I»</div>'
             f'<div id="port-b" style="position:absolute;left:40px;top:290px">{svgico("portaaviones", ES2, 320)}</div></div>'
             f'<div class="tjc" id="c-port-ma" style="left:520px">{cabecera("c-port", "ma")}<div class="tjn" style="color:{MA}">0</div><div class="tjx">no tiene</div>'
             f'<div class="tjcero" id="port-x">✕</div></div><div class="tjg" id="port-g" style="left:20px">VENTAJA</div></div>')
J(f'tl.fromTo("#port-b", {{x:-420}}, {{x:0, duration:0.9, ease:"power3.out", immediateRender:false}}, {tp + 0.2:.2f}); tl.to("#port-b", {{y:-10, duration:0.6, yoyo:true, repeat:4, ease:"sine.inOut"}}, {tp + 1.1:.2f});')
pop("#port-x", P("solo") - 0.05, 0.35, "scale:2.2, opacity:0, rotation:-15")
pop("#port-g", P("solo") + 0.3, 0.35, "scale:2.2, opacity:0, rotation:-15", "back.out(3)")
J(f'tl.set("#c-port-es .tjfx", {{opacity:0}}, 0); tl.to("#c-port-es .tjfx", {{opacity:1, duration:0.3}}, {P("solo") + 0.3:.2f}); tl.to("#c-port-ma", {{opacity:0.45, duration:0.3}}, {P("solo") + 0.3:.2f});')
J(f'tl.fromTo("#c-port .tjvs", {{scale:0}}, {{scale:1, duration:0.5, ease:"back.out(2.5)", immediateRender:false}}, {tp + 0.3:.2f});')
FX.append(("sello", P("solo")))
entra_sale("c-port", tp, FE(7) + 0.05, "der", "izq")
# ranking (tarjeta compacta: ventana de 5 filas que se desplaza)
f8 = F(8)
filas = []
for n in range(1, 66):
    cls = " es" if n == 18 else (" ma" if n == 56 else "")
    lab = "ESPAÑA" if n == 18 else ("MARRUECOS" if n == 56 else "")
    filas.append(f'<div class="fila{cls}"><b>{n}.º</b><span>{lab}</span></div>')
CARDS.append(f'<div class="tj" id="c-rank"><div class="tjbar"></div><div class="tjt">RANKING MILITAR MUNDIAL</div>'
             f'<div class="rkvent"><div class="rkstrip" id="rkstrip">{"".join(filas)}</div></div><div class="rkmarco"></div>'
             f'<div class="tju">Global Firepower 2026 · 145 países</div></div>')
ROW = 96
def fila_y(n): return -(n - 1) * ROW + 2 * ROW
J(f'tl.fromTo("#rkstrip", {{y:{fila_y(1)}}}, {{y:{fila_y(18)}, duration:{P("dieciocho") - f8:.2f}, ease:"power2.inOut", immediateRender:false}}, {f8:.2f});')
J(f'tl.to("#rkstrip", {{y:{fila_y(56)}, duration:0.9, ease:"power3.inOut"}}, {P("cincuenta") - 0.9:.2f});')
for w_ in ("dieciocho", "cincuenta"):
    FX.append(("golpe", P(w_)))
for s_ in range(int((FE(8) - f8) / 0.12)):
    FX.append(("clic", f8 + s_ * 0.12))
entra_sale("c-rank", f8, FE(8) + 0.05, "der", "abajo")

# ================================================================== 9-10) Ceuta y Melilla, OTAN y UE
f9 = F(9)
whip(f9, -1)
cam(-4.15, 35.7, 1.75, f9 - 0.15, 1.2, tilt=36)
for nom in ("ceuta", "melilla"):
    J(f'tl.fromTo("#m-{nom} .etq", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.4, ease:"back.out(2.5)", immediateRender:false}}, {P(nom):.2f});')
    FX.append(("pop", P(nom)))
J(f'tl.set(".pulso", {{opacity:1}}, {f9:.2f}); tl.fromTo(".pulso", {{attr:{{r:18}}, opacity:1}}, {{attr:{{r:80}}, opacity:0, duration:1.1, repeat:{int((DUR - f9) / 1.1)}, ease:"none", immediateRender:false}}, {f9:.2f});')
xo1, yo1 = W(-6.6, 36.45); xo2, yo2 = W(-1.6, 36.75)
MAPA.append(f'<g id="otan" style="opacity:0"><path d="M{xo1:.0f},{yo1:.0f} Q{(xo1 + xo2) / 2:.0f},{yo1 - 140:.0f} {xo2:.0f},{yo2:.0f}" stroke="#2f4f8a" stroke-width="10" stroke-dasharray="28 18" fill="none"/>'
            f'<rect x="{(xo1 + xo2) / 2 - 180:.0f}" y="{yo1 - 230:.0f}" width="360" height="86" rx="22" fill="#2f4f8a"/>'
            f'<text x="{(xo1 + xo2) / 2:.0f}" y="{yo1 - 172:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="48" fill="#fff">OTAN · art. 5</text></g>')
J(f'tl.to("#otan", {{opacity:1, duration:0.5}}, {P("otan") - 0.1:.2f});')
for nom in ("Ceuta", "Melilla"):
    x, y = W(*CIUD[nom])
    MAPA.append(f'<g class="nox" style="opacity:0"><circle cx="{x + 75:.0f}" cy="{y + 75:.0f}" r="38" fill="{MA}" stroke="#fff" stroke-width="7"/><path d="M{x + 60:.0f},{y + 60:.0f} L{x + 90:.0f},{y + 90:.0f} M{x + 90:.0f},{y + 60:.0f} L{x + 60:.0f},{y + 90:.0f}" stroke="#fff" stroke-width="9" stroke-linecap="round"/></g>'
                f'<g class="sie" style="opacity:0"><circle cx="{x + 75:.0f}" cy="{y + 75:.0f}" r="38" fill="{GRN}" stroke="#fff" stroke-width="7"/><path d="M{x + 58:.0f},{y + 75:.0f} L{x + 70:.0f},{y + 88:.0f} L{x + 94:.0f},{y + 62:.0f}" stroke="#fff" stroke-width="9" fill="none" stroke-linecap="round"/></g>'
                f'<g class="eur" style="opacity:0;transform-origin:{x:.0f}px {y:.0f}px">'
                + "".join(f'<path d="{(lambda cx, cy: "M" + " L".join(f"{cx + (10 if i % 2 == 0 else 4.5) * math.sin(i * math.pi / 5):.1f},{cy - (10 if i % 2 == 0 else 4.5) * math.cos(i * math.pi / 5):.1f}" for i in range(10)) + " Z")(x + 66 * math.cos(a), y + 66 * math.sin(a))}" fill="#ffcc00"/>' for a in [j * math.pi / 6 for j in range(12)]) + '</g>')
pop(".nox", P("automaticamente"), 0.35, "scale:2.5, opacity:0")
FX.append(("sello", P("automaticamente"))); sacude(P("automaticamente"), 10)
nota("OTAN: el art. 5 solo cubre", "Europa y Norteamérica (art. 6)", P("otan"), FE(9) + 0.2, x=50, y=1560, rot=-3, w=440)
f10 = F(10)
J(f'tl.to(".nox, #otan", {{opacity:0, duration:0.3}}, {f10:.2f});')
J(f'tl.fromTo(".eur", {{opacity:0, scale:0.3, rotation:-90}}, {{opacity:1, scale:1, rotation:0, duration:0.7, ease:"back.out(1.8)", immediateRender:false}}, {f10 + 0.1:.2f});')
J(f'tl.to(".eur", {{rotation:60, duration:{FE(10) - f10:.2f}, ease:"none"}}, {f10 + 0.8:.2f});')
pop(".sie", P("ayudar"), 0.35, "scale:2.5, opacity:0")
FX.append(("brillo", f10 + 0.1)); FX.append(("sello", P("ayudar"))); leak(f10, 1.2)
nota("UE: art. 42.7 = ayuda", "obligatoria a un socio atacado", f10 + 0.2, FE(10) + 0.2, x=560, y=1560, rot=3, w=440)

# ================================================================== 11) conclusión: flechas que se rompen
f11 = F(11)
cam(-5.0, 36.0, 0.95, f11 - 0.1, 1.2, tilt=26)
J(f'tl.to(".eur, .sie", {{opacity:0, duration:0.4}}, {f11:.2f});')
FLE = []
for k, (a, b) in enumerate((((-6.2, 35.2), (-6.0, 36.6)), ((-4.5, 35.1), (-4.3, 36.7)), ((-3.2, 35.2), (-3.0, 36.75)))):
    x1, y1 = W(*a); x2, y2 = W(*b)
    i = f"fle{k}"; FLE.append("#" + i)
    MAPA.append(f'<path id="{i}" style="opacity:0" d="M{x1:.0f},{y1:.0f} Q{(x1 + x2) / 2 + 70:.0f},{(y1 + y2) / 2:.0f} {x2:.0f},{y2:.0f}" stroke="{MA}" stroke-width="18" fill="none" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" marker-end="url(#punta)"/>')
te = P("estrecho") - 0.5
J(f'tl.set("{",".join(FLE)}", {{opacity:1}}, {te:.2f}); tl.to("{",".join(FLE)}", {{strokeDashoffset:0, duration:0.6, stagger:0.15, ease:"power2.out"}}, {te:.2f});')
OVR.append('<div id="imposible" class="sello2">CASI IMPOSIBLE</div>')
pop("#imposible", P("imposible"), 0.35, "scale:3, opacity:0, rotation:-30", "power4.out")
FX.append(("boom", P("imposible"))); sacude(P("imposible"), 22); flash(P("imposible"), 0.5)
J(f'tl.to("{",".join(FLE)}", {{opacity:0, duration:0.25}}, {P("imposible") + 0.05:.2f});')
J(f'tl.to("#imposible", {{opacity:0, duration:0.3}}, {P("tension") - 0.1:.2f});')
J(f'tl.fromTo("#m-ceuta, #m-melilla", {{scale:1}}, {{scale:1.6, transformOrigin:"50% 50%", duration:0.35, yoyo:true, repeat:3, ease:"sine.inOut", immediateRender:false}}, {P("tension"):.2f});')
nota("Según los análisis:", "cruzar el Estrecho, casi imposible", f11 + 0.3, FE(11) + 0.1, x=60, y=1580, rot=-3, w=440)

# ================================================================== 12) economía
f12 = F(12)
cam(-5.5, 36.0, 1.35, f12 - 0.1, 1.0, tilt=38)
CON = []
for k in range(6):
    ida = k % 2 == 0
    lon = -6.3 + 0.32 * k
    a = W(lon, 35.86) if ida else W(lon, 36.1)
    i = f"con{k}"; CON.append("#" + i)
    MOV.append(f'<g id="{i}" style="opacity:0" transform="translate({a[0] - 36:.0f},{a[1] - 36:.0f})"><ellipse cx="36" cy="64" rx="30" ry="7" fill="#000" opacity="0.25"/>{svgico("contenedor", ES2 if ida else MA, 72)}</g>')
    J(f'tl.set("#{i}", {{opacity:1}}, {f12 + 0.12 * k:.2f}); tl.to("#{i}", {{y:"{'-=' if ida else '+='}80", duration:{FE(12) - f12:.2f}, ease:"sine.inOut"}}, {f12 + 0.12 * k:.2f});')
J(f'tl.to("{",".join(CON)}", {{opacity:0, duration:0.3}}, {FE(12) + 0.2:.2f});')
OVR.append(f'<div id="nadie" class="cartel grande">NO LA GANA <b style="color:{MA}">NADIE</b></div>')
pop("#nadie", P("nadie") - 0.05, 0.4, "scale:2.2, opacity:0")
FX.append(("golpe", P("nadie"))); punch(P("nadie"))
fuera("#nadie", FE(12) + 0.1)
nota("España: 1.er socio", "comercial de Marruecos", P("socio") - 0.2, FE(12) + 0.2, x=560, y=1580, rot=3, w=420)
FX.append(("brillo", P("socio")))

# ================================================================== 13) final
f13 = F(13)
cam(-4.6, 36.8, 0.42, f13 - 0.1, 1.3, tilt=12)
OVR.append(f'<div id="final"><div class="f1">¿TÚ QUÉ CREES</div><div class="f2">QUE PASARÍA?</div>'
           f'<div class="f3">Te leo en comentarios <span class="dedo">👇</span></div></div>')
pop("#final", f13, 0.55, "scale:0.5, opacity:0, rotation:-6")
J(f'tl.to("#final .dedo", {{y:14, duration:0.35, yoyo:true, repeat:{max(1, int((DUR - f13) / 0.35) - 1)}, ease:"sine.inOut"}}, {f13 + 0.4:.2f});')
FX.append(("brillo", f13)); leak(f13, 1.4)

# nombres de país solo en los planos generales (en los cercanos asomaban por arriba, bajo los subtítulos)
J(f'tl.to(".pais", {{opacity:0, duration:0.3}}, 0.7); tl.to(".pais", {{opacity:0.8, duration:0.4}}, {F(2) + 0.6:.2f}); tl.to(".pais, .pin", {{opacity:0, duration:0.3}}, {F(3):.2f}); tl.to(".pin", {{opacity:1, duration:0.4}}, {F(13) + 0.6:.2f}); tl.to(".pais", {{opacity:0.8, duration:0.5}}, {F(13):.2f});')
# Ceuta y Melilla: fuera las etiquetas en la escena del comercio (tapaban los barcos y Melilla salía cortada)
J(f'tl.to("#m-ceuta .etq, #m-melilla .etq", {{opacity:0, duration:0.3}}, {F(12) - 0.1:.2f});')
# vida: nubes en parallax, oleaje, grano que parpadea, chinchetas
J(f'tl.to("#nubes", {{x:-420, duration:{DUR:.2f}, ease:"none"}}, 0);')
J(f'tl.to("#olas", {{x:-200, duration:{DUR:.2f}, ease:"none"}}, 0);')
for s in range(int(DUR / 0.08)):
    J(f'tl.set("#grano", {{backgroundPosition:"{rnd.randint(0, 360)}px {rnd.randint(0, 360)}px"}}, {s * 0.08:.2f});')
J(f'tl.to(".pin", {{y:"-=14", duration:0.8, yoyo:true, repeat:{int(DUR / 0.8)}, ease:"sine.inOut"}}, 0);')
# las nubes solo sobre el mapa (se esconden con las cartas)
for (a, b) in ((F(3) - 0.2, FE(4) + 0.1), (F(6) - 0.2, FE(8) + 0.1)):
    J(f'tl.to("#nubes", {{opacity:0, duration:0.2}}, {a:.2f}); tl.to("#nubes", {{opacity:1, duration:0.4}}, {b:.2f});')

# ------------------------------------------------------------------ cuenta atrás de 60 s
for s in range(1, 61):
    ts = min(s * DUR / 60, DUR - 0.12)
    J(f'tl.set("#crono-n", {{innerHTML:"{60 - s}"}}, {ts:.2f});')
    if s < 60:
        FX.append(("tic2" if 60 - s <= 5 else "tic", ts))
        if 60 - s <= 5:
            J(f'tl.fromTo("#crono", {{scale:1.15}}, {{scale:1, duration:0.3, ease:"power2.out", immediateRender:false}}, {ts:.2f});')
J(f'tl.fromTo("#crono-arc", {{strokeDashoffset:0}}, {{strokeDashoffset:1, duration:{DUR:.2f}, ease:"none", immediateRender:false}}, 0);')

# ------------------------------------------------------------------ subtítulos karaoke (píldora en la palabra que suena)
CLAVE = set(norm(w) for w in ["catorce", "marruecos", "cruzarlos", "sesenta", "doscientos", "ciento", "tanques", "mil", "mar", "aire",
                               "españa", "cazas", "dos", "ninguno", "portaaviones", "dieciocho", "cincuenta", "ceuta", "melilla", "otan",
                               "union", "ayudar", "imposible", "tension", "nadie", "socio", "comentarios"])
SUBS = []
chunks, cur = [], []
for p in T["palabras"]:
    cur.append(p)
    txt = " ".join(x["w"] for x in cur)
    if len(cur) >= 5 or len(txt) >= 26 or re.search(r"[.:;?!…]$", p["w"]) or (re.search(r",$", p["w"]) and len(cur) >= 3):
        chunks.append(cur); cur = []
if cur:
    chunks.append(cur)
for k, ch in enumerate(chunks):
    st = ch[0]["ini"] - 0.05
    en = chunks[k + 1][0]["ini"] - 0.05 if k + 1 < len(chunks) else DUR
    spans = []
    for j, p in enumerate(ch):
        wid = f"w{k}_{j}"
        clave = norm(p["w"]) in CLAVE
        spans.append(f'<span id="{wid}" class="sw{" key" if clave else ""}">{p["w"]}</span>')
        fin = ch[j + 1]["ini"] if j + 1 < len(ch) else en
        J(f'tl.to("#{wid}", {{backgroundColor:"{MA if clave else NAVY}", color:"#ffffff", scale:1.1, duration:0.07}}, {p["ini"]:.2f});')
        J(f'tl.to("#{wid}", {{backgroundColor:"rgba(0,0,0,0)", color:"{MA2 if clave else NAVY}", scale:1, duration:0.1}}, {max(p["ini"] + 0.08, fin - 0.02):.2f});')
    SUBS.append(f'<div id="sub{k}" class="clip sub" data-start="{max(0, st):.3f}" data-duration="{max(0.2, en - max(0, st)):.3f}" data-track-index="3">{" ".join(spans)}</div>')
    J(f'tl.fromTo("#sub{k}", {{y:24, opacity:0}}, {{y:0, opacity:1, duration:0.18, ease:"power2.out", immediateRender:false}}, {max(0, st):.2f});')

nubes = "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#ffffff" opacity="{o}"/>' for x, y, rx, ry, o in
                ((200, 720, 260, 60, 0.5), (300, 700, 160, 70, 0.55), (900, 1350, 300, 70, 0.4), (1000, 1320, 170, 80, 0.45),
                 (1500, 900, 280, 60, 0.45), (1600, 870, 150, 70, 0.5), (500, 1650, 240, 55, 0.35), (1300, 1720, 220, 60, 0.35)))
html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
@font-face{{font-family:"Caveat";src:url("assets/fonts/Caveat-700-latin.woff2") format("woff2");font-weight:700}}
@font-face{{font-family:"Marker";src:url("assets/fonts/permanent-marker-400.woff2") format("woff2")}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#f8f4ea}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;background:linear-gradient(#fff8ea, #f1e6cf 45%, #d9eef8 46%, #bfe3f4)}}
#todo{{position:absolute;inset:0;transform-origin:50% 50%}}
#escena{{position:absolute;inset:0;perspective:1700px;perspective-origin:50% 22%}}
#mesa{{position:absolute;inset:0;transform-origin:50% 60%;transform-style:preserve-3d}}
#mundo{{position:absolute;left:0;top:0;width:10px;height:10px;overflow:visible}}
#nubes{{position:absolute;left:0;top:0;overflow:visible;pointer-events:none}}
#cielo{{position:absolute;left:0;right:0;top:0;height:560px;background:linear-gradient(#fdf8ee 58%, rgba(253,248,238,0));pointer-events:none}}
.vsc{{position:absolute;inset:0;overflow:hidden;z-index:12;background:#fff}}
.tj{{position:absolute;left:{TJ_X}px;top:{TJ_Y}px;width:{TJ_W}px;height:{TJ_H}px;background:#ffffff;border-radius:40px;box-shadow:0 30px 70px rgba(20,30,60,0.35);overflow:hidden;z-index:14}}
.tjbar{{position:absolute;left:0;right:0;top:0;height:14px;background:linear-gradient(90deg,{ES} 0 50%,{MA} 50% 100%)}}
.tjt{{position:absolute;left:0;right:0;top:40px;text-align:center;font:900 54px Inter;color:{NAVY};letter-spacing:1px}}
.tjvs{{position:absolute;left:{TJ_W / 2 - 38:.0f}px;top:140px;width:76px;height:76px;border-radius:50%;background:{NAVY};color:#fff;font:900 30px Inter;display:flex;align-items:center;justify-content:center;z-index:3}}
.tjc{{position:absolute;top:140px;width:400px;height:{TJ_H - 212}px;text-align:center}}
.tjfx{{position:absolute;inset:-6px;border-radius:30px;background:rgba(46,170,90,0.10);border:5px solid {GRN};opacity:0}}
.tjcab{{position:relative;display:flex;align-items:center;justify-content:center;gap:12px;height:110px;font:900 34px Inter;color:{NAVY}}}
.tjcab svg{{border-radius:6px;box-shadow:0 4px 10px rgba(0,0,0,0.2)}}
.tjn{{position:relative;font:900 88px Inter;letter-spacing:-3px;line-height:1;height:92px}}
.tjx{{position:relative;margin-top:8px;font:800 28px Inter;color:#7a8296}}
.tjcero{{position:absolute;left:60px;right:60px;top:320px;padding:18px;border:6px dashed #c9ced8;border-radius:26px;font:900 54px Inter;color:#b0b6c4}}
.tjg{{position:absolute;top:118px;width:400px;text-align:left;padding-left:26px;font:900 26px Inter;color:#fff;letter-spacing:2px;z-index:4;transform:rotate(-6deg);transform-origin:20% 50%}}
.tjg::before{{content:"";position:absolute;left:10px;width:178px;top:-6px;bottom:-6px;border-radius:12px;background:{GRN};z-index:-1;box-shadow:0 6px 0 rgba(0,0,0,0.15)}}
.tju{{position:absolute;left:0;right:0;bottom:22px;text-align:center;font:700 26px Inter;color:#98a0b0}}
#velo{{position:absolute;inset:0;background:rgba(250,246,236,0.5);opacity:0;pointer-events:none;z-index:11}}
.mitad{{position:absolute;top:0;bottom:0;left:0;width:100%}}
.mitad.izq{{background:linear-gradient(160deg,{ES},{ES2});clip-path:polygon(0 0,57.5% 0,41.5% 100%,0 100%)}}
.mitad.der{{background:linear-gradient(200deg,{MA},{MA2});clip-path:polygon(58.5% 0,100% 0,100% 100%,42.5% 100%)}}
.rayasf{{position:absolute;inset:0 -200px 0 0;background:repeating-linear-gradient(-60deg, rgba(255,255,255,0.08) 0 26px, transparent 26px 70px)}}
.agua{{position:absolute;left:0;right:0;top:1330px;bottom:0;background:linear-gradient(rgba(20,60,110,0.0), rgba(20,60,110,0.35))}}
.vtit{{position:absolute;left:0;right:220px;top:520px;text-align:center}}
.vtit span{{display:inline-block;font:900 96px Inter;color:#fff;letter-spacing:-1px;text-shadow:0 8px 0 rgba(0,0,0,0.18), 0 0 40px rgba(0,0,0,0.15)}}
.vsb{{position:absolute;left:475px;top:655px;width:130px;height:130px;border-radius:50%;background:#fff;color:{NAVY};font:900 60px Inter;display:flex;align-items:center;justify-content:center;box-shadow:0 14px 40px rgba(0,0,0,0.3);z-index:3}}
.vcol{{position:absolute;top:690px;width:470px;color:#fff;z-index:2}}
.vcab{{display:flex;align-items:center;gap:16px;font:900 42px Inter;text-shadow:0 4px 0 rgba(0,0,0,0.15)}} .vcab svg{{border-radius:8px;box-shadow:0 6px 14px rgba(0,0,0,0.3)}}
.vnum{{margin-top:70px;font:900 104px Inter;letter-spacing:-4px;line-height:1;color:#fff;text-shadow:0 10px 0 rgba(0,0,0,0.18)}}
.vtxt{{font:800 34px Inter;color:rgba(255,255,255,0.85);margin-top:10px}}
.rueda{{display:inline-flex;align-items:baseline;font-variant-numeric:tabular-nums}}
.dg{{display:inline-block;height:1em;overflow:hidden;line-height:1em}} .st{{display:grid}} .st span{{height:1em;line-height:1em}}
.sep{{display:inline-block;line-height:1em}}
.vic{{position:absolute;filter:drop-shadow(0 8px 0 rgba(0,0,0,0.18))}}
.vcero{{position:absolute;top:1250px;padding:22px 34px;border:8px dashed rgba(255,255,255,0.8);border-radius:28px;font:900 66px Inter;color:#fff}}
.vgana{{position:absolute;top:1060px;padding:10px 22px;border-radius:16px;background:{GRN};color:#fff;font:900 38px Inter;letter-spacing:3px;transform:rotate(-8deg);box-shadow:0 8px 0 rgba(0,0,0,0.2);z-index:4}}
.vsc.rk{{background:linear-gradient(#22345f,{NAVY})}}
.rktop{{position:absolute;left:0;right:0;top:0;height:500px;background:linear-gradient(#fdf8ee 70%, rgba(253,248,238,0))}}
.rkfondo{{position:absolute;inset:0;background:repeating-linear-gradient(90deg, rgba(255,255,255,0.04) 0 2px, transparent 2px 90px)}}
.rkvent{{position:absolute;left:40px;right:40px;top:150px;height:{5 * 96}px;overflow:hidden;-webkit-mask:linear-gradient(transparent, #000 25%, #000 75%, transparent)}}
.fila{{height:96px;display:flex;align-items:center;gap:40px;padding:0 40px;font:900 52px Inter;color:#c3c8d3;border-bottom:2px solid #eef0f4}}
.fila b{{width:200px}} .fila.es{{color:#fff;background:linear-gradient(90deg,{ES},{ES2});border-radius:24px}} .fila.ma{{color:#fff;background:linear-gradient(90deg,{MA},{MA2});border-radius:24px}}
.rkmarco{{position:absolute;left:24px;right:24px;top:{150 + 2 * 96 - 8}px;height:112px;border:6px solid {NAVY};border-radius:26px}}
.rkfuente{{position:absolute;left:0;right:0;top:1460px;text-align:center;font:800 34px Inter;color:#9fb0d6}}
.nota{{position:absolute;padding:22px 26px 20px;background:linear-gradient(160deg,#fff6a8,#ffe76b);box-shadow:0 18px 34px rgba(0,0,0,0.3);border-radius:4px;z-index:30}}
.nota::before{{content:"";position:absolute;left:38%;top:-16px;width:110px;height:34px;background:rgba(255,255,255,0.55);transform:rotate(-3deg)}}
.nt{{font:700 46px Caveat;color:#1f2a44;line-height:1.05}} .ns{{font:700 36px Caveat;color:#4a5570;line-height:1.05;margin-top:4px}}
#titulo{{position:absolute;left:30px;right:30px;top:1180px;text-align:center;z-index:20}}
#titulo .t1,#titulo .t2{{display:inline-block;padding:4px 30px 10px;font:900 98px Inter;letter-spacing:-3px;line-height:1.08;border-radius:24px;box-shadow:0 18px 50px rgba(0,0,0,0.3)}}
#titulo .t1{{background:#fff;color:{NAVY}}} #titulo .t1 span{{color:{MA}}} #titulo .t2{{background:{MA};color:#fff;margin-top:16px}}
#sesenta{{position:absolute;left:250px;top:1280px;display:flex;align-items:center;gap:22px;padding:18px 36px;background:#fff;border-radius:34px;box-shadow:0 18px 40px rgba(0,0,0,0.25);z-index:20}}
#sesenta b{{font:900 130px Inter;color:{MA};letter-spacing:-6px;line-height:1}} #sesenta span{{font:900 40px Inter;color:{NAVY};line-height:1.1}}
.cazav{{position:absolute;z-index:18;width:150px}} .estela{{position:absolute;left:68px;top:-420px;width:14px;height:440px;background:linear-gradient(rgba(255,255,255,0),rgba(255,255,255,0.9));border-radius:7px}}
.cartel{{position:absolute;left:60px;right:60px;top:1420px;text-align:center;padding:26px;background:#fff;border-radius:32px;font:900 60px Inter;color:{NAVY};box-shadow:0 18px 50px rgba(0,0,0,0.28);z-index:20}}
.cartel.grande{{font-size:76px;top:1380px}}
.sello2{{position:absolute;left:140px;top:1060px;padding:16px 44px;border:12px solid {MA};border-radius:28px;color:{MA};font:900 86px Inter;letter-spacing:4px;background:rgba(255,255,255,0.9);transform:rotate(-8deg);z-index:20}}
#final{{position:absolute;left:50px;right:50px;top:1120px;text-align:center;padding:50px 30px;background:#fff;border-radius:48px;box-shadow:0 30px 80px rgba(20,40,70,0.35);z-index:20}}
#final .f1{{font:900 100px Inter;color:{NAVY};line-height:1;letter-spacing:-2px}} #final .f2{{font:900 100px Inter;color:{MA};line-height:1.1;letter-spacing:-2px}}
#final .f3{{margin-top:24px;font:800 52px Inter;color:#4a5570}} .dedo{{display:inline-block}}
#whip{{position:absolute;top:-200px;left:-300px;width:1700px;height:2400px;z-index:60;pointer-events:none;opacity:0;
  background:linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.95) 42%, #ffffff 50%, rgba(255,255,255,0.95) 58%, rgba(255,255,255,0) 100%), repeating-linear-gradient(0deg, rgba(0,0,0,0.05) 0 6px, transparent 6px 22px);transform:skewX(-14deg)}}
#leak{{position:absolute;inset:-200px;z-index:55;pointer-events:none;opacity:0;mix-blend-mode:screen;
  background:radial-gradient(40% 30% at 15% 20%, rgba(255,150,60,0.75), rgba(255,150,60,0) 70%), radial-gradient(35% 28% at 85% 70%, rgba(255,80,120,0.55), rgba(255,80,120,0) 70%)}}
#flash{{position:absolute;inset:0;background:#fff;z-index:58;opacity:0;pointer-events:none}}
#grano{{position:absolute;inset:0;z-index:57;pointer-events:none;opacity:0.07;background:url(assets/grano.png);mix-blend-mode:multiply}}
#vineta{{position:absolute;inset:0;z-index:56;pointer-events:none;background:radial-gradient(110% 80% at 50% 50%, rgba(0,0,0,0) 62%, rgba(40,20,0,0.32))}}
#crono{{position:absolute;left:845px;top:480px;width:200px;height:200px;filter:drop-shadow(0 10px 18px rgba(20,40,70,0.3));z-index:40}}
#marca{{position:absolute;left:0;right:0;top:1775px;text-align:center;font:700 28px Inter;color:#ffffff;opacity:0.6;text-shadow:0 1px 4px rgba(0,0,0,0.55);pointer-events:none;z-index:61}}
#subs{{position:absolute;left:50px;right:50px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:800 66px Inter;color:{NAVY};line-height:1.3;text-shadow:0 2px 0 #fff, 0 0 18px rgba(255,255,255,0.9)}}
.sw{{display:inline-block;position:relative;padding:0 12px;margin:2px 0;border-radius:16px;text-shadow:none}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <svg width="0" height="0" style="position:absolute"><defs>{SYMS}
    <linearGradient id="mar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SEA1}"/><stop offset="1" stop-color="{SEA2}"/></linearGradient>
    <pattern id="olasp" width="160" height="60" patternUnits="userSpaceOnUse"><path d="M0,30 Q20,18 40,30 T80,30 T120,30 T160,30" stroke="#ffffff" stroke-width="3" fill="none" opacity="0.6"/></pattern>
    <filter id="sombra" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="6" stdDeviation="6" flood-opacity="0.3"/></filter>
    <marker id="punta" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="3" markerHeight="3" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="{MA}"/></marker>
  </defs></svg>
  <div id="todo" data-layout-allow-overflow data-layout-ignore>
    <div id="escena"><div id="mesa"><svg id="mundo" width="10" height="10" data-layout-allow-overflow data-layout-ignore>{"".join(MAPA)}{"".join(MOV)}</svg></div></div>
    <svg id="nubes" width="2200" height="1920">{nubes}</svg>
    <div id="cielo"></div><div id="velo"></div>
    {"".join(CARDS)}
    {"".join(OVR)}
  </div>
  <div id="whip"></div><div id="leak"></div><div id="flash"></div><div id="vineta"></div><div id="grano"></div>
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
{chr(10).join(tl)}
tl.to({{}}, {{duration:0.01}}, {DUR - 0.01});
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>"""
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump(FX, open(os.path.join(BASE, "efectos.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones · {len(FX)} efectos")

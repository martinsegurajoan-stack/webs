#!/usr/bin/env python3
"""«¿Qué pasaría si nunca más te cortaras las uñas?» — UN SOLO PLANO: una mano grande en un estudio oscuro con luz cálida.
Las uñas crecen al ritmo real (3,5 mm/mes) y a partir de ~12 cm se retuercen en espiral. Cada frase añade algo:
regla, móvil que no responde, botón/cremallera/moneda, lupa con bacterias, pie con uña en cuerno, rotura al dormir,
récord de Shridhar Chillal (pulgar 1,98 m), dedos deformados, queratina (pelo, garra, cuerno de rinoceronte) y cortaúñas
que devuelve la mano al fotograma 0 (bucle). Sin efectos de sonido.
  python3 gen.py → index.html + efectos.json + ambiente.json"""
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
tl, FXL = [], []
def J(s): tl.append(s)

def st(t, d=1.0, ease="power2.inOut", **kv):
    J(f'tl.to(S, {{{", ".join(f"{k}:{v}" for k, v in kv.items())}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
NC = [0]
def dato(kicker, grande, t, hasta, sub="", top=1480):
    NC[0] += 1; i = NC[0]
    FXL.append(f'<div class="dato" id="d{i}" style="top:{top}px"><small>{kicker}</small><b>{grande}</b>{f"<em>{sub}</em>" if sub else ""}</div>')
    J(f'tl.set("#d{i}", {{opacity:0}}, 0); tl.fromTo("#d{i}", {{opacity:0, x:-24}}, {{opacity:1, x:0, duration:0.5, ease:"power3.out", immediateRender:false}}, {t:.2f}); tl.to("#d{i}", {{opacity:0, x:12, duration:0.35}}, {hasta:.2f});')
def contador(sel, v0, v1, t, d, dec=0, suf=""):
    J(f'(() => {{ const o = {{v:{v0}}}; tl.to(o, {{v:{v1}, duration:{d:.2f}, ease:"power2.out", onUpdate:() => {{ document.querySelector("{sel}").textContent = fmt(o.v, {dec}) + "{suf}"; }}}}, {t:.2f}); }})();')
NO = [0]
def panel(html, t, hasta, x=540, y=760, w=600, entra="up"):
    """Panel gráfico (SVG/HTML) centrado en (x, y) de pantalla."""
    NO[0] += 1; i = NO[0]
    FXL.append(f'<div class="pan" id="p{i}" style="left:{x - w / 2}px;top:{y}px;width:{w}px">{html}</div>')
    J(f'tl.set("#p{i}", {{opacity:0}}, 0); tl.fromTo("#p{i}", {{opacity:0, y:40, scale:0.94}}, {{opacity:1, y:0, scale:1, duration:0.55, ease:"power3.out", immediateRender:false}}, {t:.2f}); tl.to("#p{i}", {{opacity:0, y:-20, duration:0.35}}, {hasta:.2f});')
    return f"#p{i}"
LN = 'fill="none" stroke="#f3e9dc" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"'
RD = 'fill="none" stroke="#ff6f61" stroke-width="7" stroke-linecap="round"'


# ================================================================== ESCENA CON EL MUÑECO (problemas del día a día)
exec(open(os.path.join(BASE, "_rig.py"), encoding="utf-8").read())
PROTA = dict(piel="#e3b08c", pelo="#2e2019", camisa="#3e6fa8", pantalon="#2c3442", zapato="#e3b08c")
PR["abrocha"] = dict(tor=-90, hd=-70, uaN=72, faN=-118, uaF=76, faF=-112, thN=92, shN=90, thF=88, shF=90)
PR["abrocha2"] = dict(tor=-90, hd=-70, uaN=76, faN=-108, uaF=72, faF=-122, thN=92, shN=90, thF=88, shF=90)
PR["agacha"] = dict(tor=-40, hd=-20, uaN=96, faN=92, uaF=100, faF=96, thN=-35, shN=100, thF=-25, shF=95)
PR["sentMovilT"] = dict(tor=-80, hd=-40, uaN=72, faN=-40, uaF=76, faF=-26, thN=2, shN=92, thF=6, shF=94)
PR["pieZ"] = dict(tor=-82, hd=-50, uaN=60, faN=40, uaF=64, faF=46, thN=-10, shN=20, thF=6, shF=94)
import math as _m
def espiral(total=150, recto=26, sgn=1, ang0=0.0):
    pts, x, y, a, s = [(0.0, 0.0)], 0.0, 0.0, ang0, 0.0
    while s < total:
        s += 1.5
        if s > recto: a += sgn * min(0.16, 0.012 + (s - recto) * 0.0022)
        x += _m.cos(a) * 1.5; y += _m.sin(a) * 1.5; pts.append((x, y))
    d = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    return d, s
NAILS_LEN = 150
def unasMano(cls):
    out = ""
    for k, (dy, ang, sg) in enumerate(((-2.6, -0.10, -1), (-0.9, -0.03, 1), (0.9, 0.04, 1), (2.6, 0.12, 1))):
        d, L = espiral(NAILS_LEN, 22 + k * 3, sg, ang)
        out += (f'<g transform="translate(5,{dy})"><path class="{cls} nb" d="{d}" pathLength="100" stroke="#7a6146" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-dasharray="100 200" stroke-dashoffset="100"/>'
                f'<path class="{cls} nf" d="{d}" pathLength="100" stroke="#f0e2c6" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-dasharray="100 200" stroke-dashoffset="100"/></g>')
    return out
MOVIL = ('<g transform="rotate(-70)"><rect x="-7" y="-13" width="14" height="24" rx="3" fill="#15171c"/><rect x="-5.6" y="-11.2" width="11.2" height="20.4" rx="2" fill="#8fd8ff"/>'
         '<circle id="ripU" cx="0" cy="-2" r="2" fill="none" stroke="#ff5a4f" stroke-width="1.2" opacity="0"/><circle id="ripN" cx="0" cy="-2" r="2" fill="none" stroke="#ffffff" stroke-width="1.2" opacity="0"/></g>')
fig = rig("P", PROTA)
fig = fig.replace('<g id="P_manoN"></g>', f'<g id="P_manoN"><g id="movilG" opacity="0">{MOVIL}</g>{unasMano("un1")}</g>').replace('<g id="P_manoF"></g>', f'<g id="P_manoF">{unasMano("un2")}</g>')
# pies descalzos con uña del dedo gordo que se curva hacia abajo
dP, LP = espiral(70, 6, 1, 0.25)
fig = fig.replace('<path d="M-6,6 L21,6 L21,8 L-6,8 Z" fill="#ffffff" opacity="0.25"/>',
                  f'<g transform="translate(20,3)"><path class="pieU nb" d="{dP}" pathLength="100" stroke="#7a6146" stroke-width="3.4" fill="none" stroke-linecap="round" stroke-dasharray="100 200" stroke-dashoffset="100"/><path class="pieU nf" d="{dP}" pathLength="100" stroke="#f0e2c6" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-dasharray="100 200" stroke-dashoffset="100"/></g>')
E = []
E.append('<rect x="-2000" y="-700" width="5000" height="700" fill="#4a3f36"/><rect x="-2000" y="-700" width="5000" height="700" fill="url(#papel)"/>')
E.append('<rect x="-2000" y="0" width="5000" height="600" fill="#6b4c36"/>' + "".join(f'<rect x="{-2000 + k * 90}" y="0" width="2" height="600" fill="#5a3e2c"/>' for k in range(56)))
E.append('<rect x="-2000" y="-14" width="5000" height="14" fill="#d9cdbd"/>')
# salón: ventana, lámpara, sofá, mesa
E.append('<g transform="translate(-180,-330)"><rect width="190" height="230" fill="#1c2a3f"/><rect width="190" height="230" fill="url(#noche)"/><path d="M95,0 V230 M0,115 H190" stroke="#d9cdbd" stroke-width="8"/><rect x="-10" y="-10" width="210" height="250" fill="none" stroke="#d9cdbd" stroke-width="10"/></g>')
E.append('<g transform="translate(330,0)"><rect x="-3" y="-260" width="6" height="260" fill="#2a2a2a"/><path d="M-40,-260 L40,-260 L26,-310 L-26,-310 Z" fill="#f1d9a7"/><ellipse cx="0" cy="-220" rx="130" ry="90" fill="#ffd38a" opacity="0.12"/></g>')
E.append('<g transform="translate(-40,0)"><rect x="-10" y="-110" width="230" height="70" rx="18" fill="#8a4f3d"/><rect x="0" y="-62" width="210" height="34" rx="10" fill="#9c5a46"/><rect x="-20" y="-80" width="30" height="72" rx="12" fill="#7c4535"/><rect x="200" y="-80" width="30" height="72" rx="12" fill="#7c4535"/><rect x="0" y="-28" width="10" height="28" fill="#3a2a22"/><rect x="200" y="-28" width="10" height="28" fill="#3a2a22"/></g>')
E.append('<g transform="translate(220,0)"><rect x="0" y="-48" width="90" height="8" fill="#c79a6e"/><rect x="8" y="-40" width="6" height="40" fill="#a57b55"/><rect x="76" y="-40" width="6" height="40" fill="#a57b55"/><rect x="30" y="-56" width="30" height="8" rx="2" fill="#e8e2d8"/></g>')
# pasillo: espejo y moneda
E.append('<g transform="translate(660,-260)"><rect width="120" height="210" rx="60" fill="#9fb6c9" opacity="0.55"/><rect width="120" height="210" rx="60" fill="none" stroke="#c9a46a" stroke-width="8"/><path d="M30,40 L50,20 M30,80 L70,40" stroke="#ffffff" stroke-width="4" opacity="0.4"/></g>')
E.append('<g id="moneda"><ellipse cx="900" cy="-3" rx="8" ry="3" fill="#e2b84a"/><ellipse cx="900" cy="-4" rx="8" ry="3" fill="#f6d06a"/></g>')
# dormitorio: cama, mesilla, zapato
E.append('<g transform="translate(1180,0)"><rect x="0" y="-100" width="12" height="100" fill="#5a3b2a"/><rect x="0" y="-62" width="320" height="34" rx="8" fill="#e8e2d8"/><rect x="0" y="-70" width="320" height="12" rx="6" fill="#ffffff"/><rect x="10" y="-82" width="70" height="20" rx="10" fill="#f6f2ea"/><rect x="120" y="-66" width="200" height="10" rx="5" fill="#4f7cab"/><rect x="0" y="-28" width="320" height="10" fill="#5a3b2a"/><rect x="300" y="-60" width="12" height="60" fill="#5a3b2a"/></g>')
E.append('<g transform="translate(1100,0)"><rect x="-40" y="-60" width="60" height="60" fill="#6e4a33"/><rect x="-32" y="-90" width="10" height="30" fill="#ddd"/><path d="M-36,-100 L-18,-100 L-22,-90 L-32,-90 Z" fill="#f1d9a7"/></g>')
E.append('<g id="zapato" transform="translate(1330,0)"><path d="M0,-4 C0,-14 6,-20 16,-20 L30,-22 C40,-22 46,-14 48,-4 L48,0 L0,0 Z" fill="#3a3a3a"/><path d="M4,-2 H46" stroke="#eee" stroke-width="2"/></g>')
E.append('')
SCN = ''.join(E) + f'<g id="pos"><g id="tumba"><g id="sentar"><g transform="translate(0,-92)">{fig}</g></g></g></g><g id="trozo" opacity="0"><path d="M0,0 C10,-6 22,-4 28,6 C32,14 26,22 18,20" stroke="#f0e2c6" stroke-width="2" fill="none"/></g>'
SDEFS = ('<pattern id="papel" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M0,0 V40" stroke="#3f352d" stroke-width="2"/></pattern>'
         '<linearGradient id="noche" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a3d5c"/><stop offset="1" stop-color="#0f1726"/></linearGradient>')
def esc(t, d=0.6, **kv): st(t, d, "power2.inOut", **kv)

# ------------------------------------------------------------------ GUION VISUAL
INI = dict(cx=0, cy=-250, z=2.05)
FXL.append('<div class="dato" id="hook" style="top:1480px;opacity:1"><small>SIN CORTARLAS</small><b>nunca más</b></div>')
J('tl.set("#hook", {opacity:1}, 0);')
# 1) gancho: la mano con uñas normales; empiezan a crecer en «nunca»
st(P("nunca", 2), FE(1) - P("nunca", 2) + 0.3, "power1.in", L=0.6)
J(f'tl.to("#hook", {{opacity:0, duration:0.4}}, {F(2) - 0.1:.2f}); tl.to("#hook", {{opacity:1, duration:0.4}}, {DUR - 0.6:.2f});')
# 2) 3,5 mm al mes → 4 cm al año; la mano dominante, más rápido
st(F(2), FE(2) - F(2), "none", L=4.2)
st(F(2), 1.4, cy=-330, z=1.7)
J(f'tl.to(S, {{regla:1, duration:0.5}}, {F(2) + 0.3:.2f}); tl.to(S, {{regla:0, duration:0.4}}, {FE(2) + 0.1:.2f});')
dato("CRECEN", "<span id=\"nmm\">0</span> mm al mes", F(2) + 0.2, P("ano") - 0.4)
contador("#nmm", 0, 3.5, F(2) + 0.3, 1.2, 1)
dato("EN UN AÑO", "≈ 4 cm", P("ano") - 0.4, P("escribes") - 0.4)
dato("LA MANO CON LA QUE ESCRIBES", "crece más rápido", P("escribes") - 0.4, FE(2) + 0.2)
# 3) el móvil: el muñeco en el sofá; la uña toca la pantalla y no pasa nada; con el nudillo, sí
J(f'tl.to(S, {{vista:1, duration:0.6}}, {F(3) - 0.3:.2f});')
J(f'tl.set(S, {{px:60, py:30, sx:70, sy:-60, sz:4.4}}, {F(3) - 0.3:.2f});')
rset(J, "P", "sentMovil", 0); J(f'tl.set("#P_sombra", {{opacity:0}}, {F(3) - 0.3:.2f}); tl.set("#P_sombra", {{opacity:0.28}}, {F(4) - 0.2:.2f}); tl.set("#P_sombra", {{opacity:0}}, {P("moneda") - 0.5:.2f});'); J(f'tl.set("#movilG", {{opacity:1}}, {F(3) - 0.3:.2f});')
st(F(3), FE(3) - F(3), "none", L=4.6)
for k in range(3):
    rpose(J, "P", "sentMovilT", P("pantalla") - 0.2 + k * 0.5, 0.18); rpose(J, "P", "sentMovil", P("pantalla") + 0.0 + k * 0.5, 0.18)
J(f'tl.fromTo("#ripU", {{opacity:1, attr:{{r:1}}}}, {{opacity:0, attr:{{r:7}}, duration:0.5, repeat:2, immediateRender:false}}, {P("pantalla") - 0.1:.2f});')
J(f'tl.fromTo("#ripN", {{opacity:1, attr:{{r:1}}}}, {{opacity:0, attr:{{r:8}}, duration:0.5, repeat:2, immediateRender:false}}, {P("nudillos") - 0.2:.2f});')
esc(F(3) + 0.5, 2.5, sx=90, sy=-90, sz=6.0)
dato("LA UÑA NO CONDUCE", "la pantalla no responde", P("pantalla") - 0.4, P("nudillos") - 0.5)
dato("SOLUCIÓN", "escribir con los nudillos", P("nudillos") - 0.4, FE(3) + 0.2)
# 4) botón frente al espejo + moneda del suelo
J(f'tl.set("#movilG", {{opacity:0}}, {F(4) - 0.2:.2f}); tl.set(S, {{px:610, py:0, sx:640, sy:-110, sz:4.6}}, {F(4) - 0.2:.2f});')
rset(J, "P", "abrocha", F(4) - 0.2)
for k in range(6):
    rpose(J, "P", "abrocha2" if k % 2 == 0 else "abrocha", F(4) + k * 0.32, 0.3, "sine.inOut")
st(F(4), FE(4) - F(4), "none", L=5.4)
J(f'tl.set(S, {{px:860, sx:880, sy:-70, sz:4.6}}, {P("moneda") - 0.5:.2f}); tl.set("#sentar", {{y:62}}, {P("moneda") - 0.5:.2f});')
rset(J, "P", "agacha", P("moneda") - 0.5)
J(f'tl.to("#moneda", {{x:14, duration:0.25, yoyo:true, repeat:5, ease:"sine.inOut"}}, {P("moneda"):.2f});')
dato("ABROCHARSE UN BOTÓN", "imposible", P("boton") - 0.3, P("moneda") - 0.6)
dato("COGER UNA MONEDA", "imposible", P("moneda") - 0.5, FE(4) + 0.2)
J(f'tl.to(S, {{vista:0, duration:0.6}}, {FE(4) - 0.2:.2f}); tl.set("#sentar", {{y:0}}, {FE(4) + 0.5:.2f});')
# 5) bacterias bajo la uña
BAC = "".join(f'<g class="bac" transform="translate({140 + 120 * math.cos(k * 2.39) * (0.3 + 0.7 * ((k * 37) % 10) / 10):.0f},{140 + 120 * math.sin(k * 2.39) * (0.3 + 0.7 * ((k * 53) % 10) / 10):.0f}) rotate({(k * 47) % 180})"><rect x="-14" y="-5" width="28" height="10" rx="5" fill="{["#7ed957", "#5ac8a8", "#b6e36b"][k % 3]}" opacity="0.9"/></g>' for k in range(34))
LUPA = (f'<svg viewBox="0 0 280 280" width="460" height="460"><defs><clipPath id="clL"><circle cx="140" cy="140" r="126"/></clipPath><radialGradient id="gL" cx="0.5" cy="0.45" r="0.6"><stop offset="0" stop-color="#3a2f22"/><stop offset="1" stop-color="#16110c"/></radialGradient></defs>'
        f'<circle cx="140" cy="140" r="126" fill="url(#gL)"/><g clip-path="url(#clL)">{BAC}</g><circle cx="140" cy="140" r="126" fill="none" stroke="#f3e9dc" stroke-width="6"/></svg>')
panel(LUPA, F(5) - 0.1, FE(5) + 0.2, x=540, y=430, w=460)
J(f'tl.fromTo(".bac", {{scale:0.2, opacity:0}}, {{scale:1, opacity:1, duration:0.3, stagger:0.04, ease:"back.out(2)", immediateRender:false}}, {P("bacterias") - 0.5:.2f});')
J(f'tl.to(".bac", {{rotation:"+=40", x:"+=6", duration:0.5, yoyo:true, repeat:9, ease:"sine.inOut", stagger:{{each:0.03, from:"random"}}}}, {P("bacterias"):.2f});')
st(F(5) - 0.2, 1.2, cy=-600, z=1.4)
J(f'tl.to(S, {{L:5.8, duration:{FE(5) - F(5):.2f}, ease:"none"}}, {F(5):.2f}); tl.to(S, {{sucio:1, duration:0.8}}, {P("bacterias") - 0.3:.2f}); tl.to(S, {{sucio:0, duration:0.5}}, {FE(5) + 0.2:.2f});')
dato("BAJO UNA UÑA LARGA", "millones de bacterias", P("bacterias") - 0.3, FE(5) + 0.2)
# 6) el pie: sentado en la cama, la uña del pie se curva; el zapato no entra
J(f'tl.to(S, {{vista:1, duration:0.6}}, {F(6) - 0.3:.2f}); tl.set(S, {{px:1240, py:22, sx:1270, sy:-60, sz:4.8}}, {F(6) - 0.3:.2f});')
rset(J, "P", "sentado", F(6) - 0.3); J(f'tl.set("#zapato", {{x:1330, y:0}}, {F(6) - 0.3:.2f});')
st(F(6), FE(6) - F(6), "power1.inOut", Lp=1)
esc(P("zapato") - 0.6, 1.4, sx=1290, sy=-30, sz=6.5)
J(f'tl.to("#zapato", {{x:1292, duration:0.6, ease:"power2.out"}}, {P("zapato") - 0.4:.2f}); tl.to("#zapato", {{x:1340, rotation:-20, duration:0.5, ease:"back.out(2)"}}, {P("cabria") - 0.1:.2f});')
dato("NINGÚN ZAPATO", "te cabría", P("zapato") - 0.4, P("curvan") - 0.6)
dato("LAS DE LOS PIES", "se curvan como un cuerno", P("curvan") - 0.5, FE(6) + 0.2)
J(f'tl.to(S, {{vista:0, duration:0.6}}, {FE(6) - 0.1:.2f});')
# 7) espiral pasados 20 cm
st(F(7) - 0.3, 1.6, cx=0, cy=-560, z=0.95)
st(F(7), FE(7) - F(7), "power1.inOut", L=34)
dato("A PARTIR DE", "<span id=\"ncm\">0</span> cm", P("veinte") - 0.4, P("espiral") - 0.4)
contador("#ncm", 0, 20, P("veinte") - 0.3, 0.9)
dato("SE RETUERCEN", "en espiral", P("espiral") - 0.4, FE(7) + 0.2, "cada lado crece a distinto ritmo")
# 8) dormir: en la cama, un giro y la uña se parte (el muñeco con uñas larguísimas)
J(f'tl.to(S, {{vista:1, duration:0.6}}, {F(8) - 0.3:.2f}); tl.set(S, {{px:1422, py:-80, sx:1340, sy:-110, sz:3.6, Lp:0}}, {F(8) - 0.3:.2f});')
rset(J, "P", "tumbado", F(8) - 0.3); J(f'tl.set("#tumba", {{rotation:-90, svgOrigin:"0 0"}}, {F(8) - 0.3:.2f}); tl.set("#zapato", {{opacity:0}}, {F(8) - 0.3:.2f});')
J(f'tl.to("#tumba", {{rotation:-80, svgOrigin:"0 0", duration:0.35, yoyo:true, repeat:1, ease:"power2.inOut"}}, {P("giro") - 0.2:.2f});')
J(f'tl.set("#trozo", {{opacity:1, x:1280, y:-120}}, {P("parte") - 0.1:.2f}); tl.to("#trozo", {{y:0, x:1400, rotation:200, duration:0.9, ease:"power2.in"}}, {P("parte") - 0.1:.2f}); tl.to("#trozo", {{opacity:0, duration:0.3}}, {FE(8) + 0.2:.2f});')
J(f'tl.to(S, {{rotP:1, duration:0.1}}, {P("parte") - 0.1:.2f});')
dato("DORMIR", "un giro y se parte", P("giro") - 0.3, FE(8) + 0.2, "años de crecimiento, perdidos")
J(f'tl.to(S, {{vista:0, duration:0.6}}, {FE(8) - 0.1:.2f}); tl.set("#tumba", {{rotation:0}}, {FE(8) + 0.6:.2f});')
# 9) Shridhar Chillal: 66 años, pulgar de casi 2 m
st(F(9) - 0.2, FE(9) - F(9) + 0.4, "power2.inOut", L=180, z=0.36, cy=-1150)
dato("SHRIDHAR CHILLAL · INDIA", "<span id=\"nan\">0</span> años sin cortarlas", P("sesenta") - 0.4, P("pulgar") - 0.3)
contador("#nan", 0, 66, P("sesenta") - 0.3, 1.4)
BARRAS = ('<svg viewBox="0 0 420 520" width="420" height="520"><path d="M20,480 H400" stroke="#6b5c4c" stroke-width="3"/>'
          '<rect id="bP" x="70" y="480" width="110" height="0" rx="8" fill="#e8d8b8"/><rect id="bH" x="250" y="480" width="110" height="0" rx="8" fill="#5f6f82"/>'
          '<text x="125" y="512" font-family="Inter" font-size="22" font-weight="600" text-anchor="middle" fill="#f3e9dc">su pulgar</text><text x="305" y="512" font-family="Inter" font-size="22" font-weight="600" text-anchor="middle" fill="#f3e9dc">una persona</text>'
          '<text id="tP" x="125" y="40" font-family="Inter" font-size="34" font-weight="300" text-anchor="middle" fill="#ffffff" opacity="0">1,98 m</text><text id="tH" x="305" y="80" font-family="Inter" font-size="34" font-weight="300" text-anchor="middle" fill="#ffffff" opacity="0">1,75 m</text></svg>')
panel(BARRAS, P("pulgar") - 0.4, FE(9) + 0.3, x=800, y=520, w=420)
J(f'tl.to("#bP", {{attr:{{y:66, height:414}}, duration:1.4, ease:"power2.out"}}, {P("pulgar") - 0.2:.2f}); tl.to("#bH", {{attr:{{y:114, height:366}}, duration:1.4, ease:"power2.out"}}, {P("pulgar"):.2f}); tl.to(["#tP", "#tH"], {{opacity:1, duration:0.4}}, {P("pulgar") + 1.0:.2f});')
dato("SU PULGAR", "1,98 m", P("pulgar") - 0.3, FE(9) + 0.3, "récord Guinness, 2016")
# 10) dedos deformados; la mano no vuelve a abrirse
J(f'tl.to(S, {{deforma:1, duration:2.2, ease:"power2.inOut"}}, {F(10) + 0.2:.2f}); tl.to(S, {{deforma:0, duration:0.8}}, {FE(10) + 0.4:.2f});')
st(F(10) - 0.2, 1.6, z=0.6, cy=-750)
dato("EL PRECIO", "dedos deformados", F(10) + 0.2, P("abrirse") - 0.5)
dato("ESA MANO", "nunca volvió a abrirse", P("abrirse") - 0.5, FE(10) + 0.3)
# 11) queratina: pelo, garra, cuerno de rinoceronte
QK = {
    "pelo": f'<path d="M40,110 C30,80 60,60 50,30 C44,14 54,6 62,4" {LN}/><path d="M64,112 C56,84 84,64 76,34 C72,20 80,10 88,8" {LN}/><path d="M86,110 C82,84 104,66 98,40" {LN}/>',
    "garra": f'<path d="M20,100 C30,60 60,30 104,20 C84,40 74,70 72,104 Z" {LN}/><path d="M36,92 C46,66 64,48 88,36" {LN} stroke-width="3"/>',
    "cuerno": f'<path d="M14,108 C30,70 50,40 96,10 C82,50 78,80 84,108 Z" {LN}/><path d="M30,98 C44,72 60,52 80,36" {LN} stroke-width="3"/>',
}
for k, (n, w) in enumerate((("pelo", "pelo"), ("garra", "garras"), ("cuerno", "rinoceronte"))):
    panel(f'<svg viewBox="0 0 120 120" width="190" height="190">{QK[n]}</svg><div class="cap">{["pelo", "garras", "cuerno de rinoceronte"][k]}</div>', P(w) - 0.4, FE(11) + 0.2, x=200 + k * 340, y=540, w=300)
st(F(11) - 0.2, 1.8, L=6, z=1.6, cy=-330)
dato("LAS UÑAS SON", "queratina", P("queratina") - 0.4, FE(11) + 0.2)
# 12) cortaúñas → la mano vuelve al fotograma 0 (bucle)
CLIP = (f'<svg viewBox="0 0 300 120" width="300" height="120"><path d="M20,60 L250,38 C270,36 284,46 284,60 C284,74 270,84 250,82 Z" fill="#c9ced6"/><path d="M20,60 L250,82" stroke="#8e96a2" stroke-width="4"/>'
        f'<path d="M60,40 C120,10 200,8 250,30" stroke="#aab2bd" stroke-width="10" fill="none" stroke-linecap="round"/><circle cx="250" cy="60" r="8" fill="#8e96a2"/></svg>')
panel(CLIP, F(12) - 0.1, P("cuerno", 3) + 0.2, x=540, y=560, w=300)
st(P("cortas") - 0.2, 0.9, "power3.in", L=0.6)
J(f'tl.to(S, {{flash:1, duration:0.12, yoyo:true, repeat:1}}, {P("cortas") + 0.6:.2f});')
dato("CADA VEZ QUE TE CORTAS LAS UÑAS", "te quitas un pequeño cuerno", P("cuerno", 3) - 0.6, DUR - 2.4)
st(FE(12) - 2.0, DUR - FE(12) + 1.9, "power2.inOut", cx=INI["cx"], cy=INI["cy"], z=INI["z"], L=0.3)

# ------------------------------------------------------------------ montaje
_S = open(os.path.join(BASE, "_subs.py"), encoding="utf-8").read()
exec(re.sub(r"CLAVE = set\(.*?\]\)", lambda m: 'CLAVE = set(norm(w) for w in ["nunca", "unas", "tres", "cuatro", "escribes", "movil", "pantalla", "nudillos", "boton", "cremallera", "moneda", "imposible", "bacterias", "sucios", "zapato", "cuerno", "veinte", "espiral", "parte", "chillal", "sesenta", "pulgar", "metros", "deformaron", "abrirse", "queratina", "pelo", "garras", "rinoceronte", "cortas"])', _S, count=1, flags=re.S))
html = open(os.path.join(BASE, "_plantilla.html"), encoding="utf-8").read()
for k, v in (("%%DURX%%", f"{DUR:.3f}"), ("%%DUREND%%", f"{DUR - 0.01:.3f}"), ("%%DUR%%", f"{DUR}"), ("%%FXL%%", "".join(FXL)), ("%%SUBS%%", "".join(SUBS)),
             ("%%TL%%", chr(10).join(tl)), ("%%INI%%", json.dumps(INI)), ("%%SCN%%", SCN), ("%%SDEFS%%", SDEFS)):
    html = html.replace(k, v)
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump([], open(os.path.join(BASE, "efectos.json"), "w"))
json.dump([[0, 0.0], [DUR, 0.0]], open(os.path.join(BASE, "ambiente.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones")

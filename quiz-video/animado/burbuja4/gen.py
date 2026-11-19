#!/usr/bin/env python3
"""«¿Qué pasaría si te dejasen caer desde 1.000 m dentro de una burbuja?» — versión INFORMATIVA (documental, tono neutro).
Infografía profesional: fondo oscuro de cine, dibujos técnicos, gráficas y paneles de datos; cortes secos; cámara con empuje suave.
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
tl, FX, ESC, OVR, DEFS = [], [], [], [], []
def J(s): tl.append(s)

CY, RJ, AM, TX, MU, LN = "#4fd1ff", "#ff5a4f", "#ffc24a", "#e8f0fa", "#7f93ad", "#1d2c44"

# ------------------------------------------------------------------ utilidades
def escena(eid, svg, t0, t1, z0=1.0, z1=1.045, html=""):
    """Plano con corte seco. Empuje de cámara muy suave y continuo (nunca zoom de ida y vuelta)."""
    ESC.append(f'<div class="esc" id="{eid}"><div class="cam" id="{eid}-cam"><svg width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0;overflow:visible">{svg}</svg>{html}</div></div>')
    J(f'tl.set("#{eid}", {{opacity:0}}, 0); tl.set("#{eid}", {{opacity:1}}, {t0:.2f}); tl.set("#{eid}", {{opacity:0}}, {t1:.2f});')
    J(f'tl.fromTo("#{eid}-cam", {{scale:{z0}}}, {{scale:{z1}, duration:{t1 - t0:.2f}, ease:"none", immediateRender:false}}, {t0:.2f});')
def entra(sel, t, frm="opacity:0, y:30", d=0.45, ease="power3.out"):
    J(f'tl.set("{sel}", {{opacity:0}}, 0); tl.fromTo("{sel}", {{{frm}}}, {{opacity:1, x:0, y:0, duration:{d}, ease:"{ease}", immediateRender:false}}, {t:.2f});')
def dibuja(sel, t, d=0.8, ease="power2.inOut"):
    """Traza una línea/curva (stroke-dasharray) — los elementos llevan pathLength=1."""
    J(f'tl.set("{sel}", {{strokeDasharray:1, strokeDashoffset:1}}, 0); tl.to("{sel}", {{strokeDashoffset:0, duration:{d}, ease:"{ease}"}}, {t:.2f});')
def contador(cid, t, v0, v1, d=0.8, fmt="int", ease="power2.out"):
    o = cid.replace("-", "_") + f"_{len(tl)}"
    f = {"int": "Math.round(o.v).toLocaleString('es-ES')", "dec": "o.v.toFixed(1).replace('.', ',')"}[fmt].replace("o.", f"{o}.")
    J(f'const {o} = {{v:{v0}}}; tl.to({o}, {{v:{v1}, duration:{d:.2f}, ease:"{ease}", onUpdate:() => {{ const e = document.getElementById("{cid}"); if (e) e.textContent = {f}; }}}}, {t:.2f});')
def etiqueta(x, y, txt, col=CY, size=30, anchor="start", cls="", eid=""):
    return f'<text {f"id={chr(34)}{eid}{chr(34)}" if eid else ""} class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}" font-family="Inter" font-weight="800" font-size="{size}" fill="{col}" letter-spacing="{size * 0.12:.1f}">{txt}</text>'
def fondo(variante=0):
    s = ['<rect width="1080" height="1920" fill="url(#fondoG)"/>']
    s.append("".join(f'<path d="M{x},0 L{x},1920" stroke="#ffffff" stroke-width="1" opacity="0.035"/>' for x in range(0, 1081, 60))
             + "".join(f'<path d="M0,{y} L1080,{y}" stroke="#ffffff" stroke-width="1" opacity="0.035"/>' for y in range(0, 1921, 60)))
    return "".join(s)
DEFS.append('<radialGradient id="fondoG" cx="0.5" cy="0.45" r="0.8"><stop offset="0" stop-color="#11223a"/><stop offset="0.6" stop-color="#08111f"/><stop offset="1" stop-color="#03060c"/></radialGradient>')
DEFS.append('<linearGradient id="cieloG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#07101e"/><stop offset="0.55" stop-color="#173253"/><stop offset="0.85" stop-color="#3f6f8f"/><stop offset="1" stop-color="#a7c4cf"/></linearGradient>')
DEFS.append('<radialGradient id="burG" cx="0.38" cy="0.32" r="0.75"><stop offset="0" stop-color="#e6f6ff" stop-opacity="0.22"/><stop offset="0.55" stop-color="#8fcfff" stop-opacity="0.10"/><stop offset="0.9" stop-color="#5fb2ec" stop-opacity="0.28"/><stop offset="1" stop-color="#cdeeff" stop-opacity="0.55"/></radialGradient>')
DEFS.append('<linearGradient id="heliG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a4d66"/><stop offset="1" stop-color="#16212f"/></linearGradient>')
DEFS.append('<linearGradient id="sueloG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2c4a3a"/><stop offset="1" stop-color="#0d1a14"/></linearGradient>')
DEFS.append('<radialGradient id="haloC" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#4fd1ff" stop-opacity="0.35"/><stop offset="1" stop-color="#4fd1ff" stop-opacity="0"/></radialGradient>')
DEFS.append('<radialGradient id="haloR" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ff5a4f" stop-opacity="0.45"/><stop offset="1" stop-color="#ff5a4f" stop-opacity="0"/></radialGradient>')

def maniqui(r, col="#9fb3c8", cls="maniqui"):
    """Silueta humana técnica (maniquí), proporcional al radio de la burbuja, sujeta con arnés."""
    k = r / 300
    return (f'<g class="{cls}" stroke="{col}" stroke-linecap="round" fill="none">'
            f'<path d="M0,{-40 * k:.0f} L{-150 * k:.0f},{-150 * k:.0f} M0,{-40 * k:.0f} L{150 * k:.0f},{-150 * k:.0f} M{-10 * k:.0f},{60 * k:.0f} L{-120 * k:.0f},{170 * k:.0f} M{10 * k:.0f},{60 * k:.0f} L{120 * k:.0f},{170 * k:.0f}" stroke-width="{3 * k:.1f}" opacity="0.55" stroke-dasharray="{8 * k:.0f} {6 * k:.0f}"/>'
            f'<path d="M0,{-55 * k:.0f} L0,{55 * k:.0f}" stroke-width="{46 * k:.0f}"/>'
            f'<path d="M{-20 * k:.0f},{-40 * k:.0f} L{-95 * k:.0f},{-120 * k:.0f} M{20 * k:.0f},{-40 * k:.0f} L{95 * k:.0f},{-120 * k:.0f}" stroke-width="{18 * k:.0f}"/>'
            f'<path d="M{-14 * k:.0f},{55 * k:.0f} L{-60 * k:.0f},{170 * k:.0f} M{14 * k:.0f},{55 * k:.0f} L{60 * k:.0f},{170 * k:.0f}" stroke-width="{22 * k:.0f}"/>'
            f'<circle cy="{-100 * k:.0f}" r="{27 * k:.0f}" fill="{col}" stroke="none"/></g>')
def burbuja(r, figura=True, eid=""):
    s = [f'<g {f"id={chr(34)}{eid}{chr(34)}" if eid else ""}>', f'<circle r="{r}" fill="url(#burG)"/>']
    if figura:
        s.append(maniqui(r))
    s.append(f'<circle r="{r}" fill="none" stroke="#cdeeff" stroke-width="{max(2, r / 70):.1f}" opacity="0.85"/>'
             f'<path d="M{-r * 0.7:.0f},{-r * 0.38:.0f} A{r * 0.8:.0f},{r * 0.8:.0f} 0 0 1 {-r * 0.2:.0f},{-r * 0.8:.0f}" stroke="#ffffff" stroke-width="{r / 22:.1f}" fill="none" stroke-linecap="round" opacity="0.5"/>'
             f'<ellipse cx="{r * 0.42:.0f}" cy="{-r * 0.55:.0f}" rx="{r * 0.09:.0f}" ry="{r * 0.045:.0f}" fill="#ffffff" opacity="0.7" transform="rotate(35 {r * 0.42:.0f} {-r * 0.55:.0f})"/>'
             f'<ellipse rx="{r}" ry="{r * 0.3:.0f}" fill="none" stroke="#cdeeff" stroke-width="1.5" opacity="0.25"/></g>')
    return "".join(s)
def helicoptero(s=1.0, eid="heli"):
    return (f'<g id="{eid}" transform="scale({s})">'
            '<path d="M-150,-30 L150,-30 M-110,-30 L-90,-62 M110,-30 L90,-62" stroke="#0d1520" stroke-width="10" stroke-linecap="round"/>'
            '<path d="M-200,-150 L-560,-170 L-560,-150 L-200,-110 Z" fill="url(#heliG)"/><path d="M-560,-170 L-610,-250 L-575,-250 L-540,-160 Z" fill="#22324a"/>'
            '<path d="M-180,-62 Q-235,-62 -235,-135 Q-235,-238 -100,-242 L110,-242 Q200,-236 225,-150 Q232,-70 150,-62 Z" fill="url(#heliG)"/>'
            '<path d="M60,-226 L120,-226 Q195,-220 214,-150 L214,-118 L60,-118 Z" fill="#2c4a6b"/><path d="M80,-220 L140,-130" stroke="#ffffff" stroke-width="8" opacity="0.15"/>'
            '<path d="M-235,-128 L225,-128" stroke="#4fd1ff" stroke-width="3" opacity="0.35"/>'
            '<rect x="-12" y="-272" width="24" height="32" fill="#0d1520"/>'
            f'<ellipse class="rotor" cx="0" cy="-276" rx="470" ry="12" fill="#9fb3c8" opacity="0.35"/>'
            '<circle class="baliza" cx="-90" cy="-60" r="9" fill="#ff5a4f"/>'
            '<path d="M0,-62 L0,0" stroke="#5b6b80" stroke-width="7"/><circle cy="0" r="9" fill="#5b6b80"/></g>')
def regla(x, y0, y1, labels=(0, 200, 400, 600, 800, 1000), eid="regla"):
    s = [f'<g id="{eid}"><path d="M{x},{y0} L{x},{y1}" stroke="{MU}" stroke-width="3" opacity="0.6"/>']
    for m in range(0, 1001, 50):
        y = y1 - (y1 - y0) * m / 1000
        big = m in labels
        s.append(f'<path class="tick" d="M{x},{y:.0f} L{x + (36 if big else 16)},{y:.0f}" stroke="{TX if big else MU}" stroke-width="{3 if big else 2}" opacity="{0.9 if big else 0.5}"/>')
        if big:
            s.append(etiqueta(x + 48, y + 10, f"{m} m", TX if m else MU, 26))
    s.append('</g>')
    return "".join(s)
def suelo(y, estadio=True):
    s = [f'<rect x="-200" y="{y}" width="1480" height="{1920 - y + 200}" fill="url(#sueloG)"/>', f'<path d="M-200,{y} L1280,{y}" stroke="#7fbf9a" stroke-width="3" opacity="0.6"/>']
    if estadio:
        s.append(f'<path d="M120,{y} L160,{y - 70} L920,{y - 70} L960,{y} Z" fill="#132232"/>' + "".join(f'<path d="M{x},{y - 70} L{x},{y - 190}" stroke="#2a3c54" stroke-width="6"/><rect x="{x - 26}" y="{y - 206}" width="52" height="18" rx="4" fill="#cfe0ef" opacity="0.8"/>' for x in (180, 900)))
    return "".join(s)
def hud_alt():
    OVR.append('<div class="hud" id="hudA"><small>ALTITUD</small><b><span id="altN">1.000</span> m</b></div><div class="hud der" id="hudV"><small>VELOCIDAD</small><b><span id="velN">0</span> km/h</b></div>')

# ================================================================== 1) GANCHO: 1.000 m de altura, dentro de una burbuja de plástico
f1, f2 = 0.0, F(2)
s1 = (f'<rect width="1080" height="1920" fill="url(#cieloG)"/>' + "".join(f'<circle cx="{random.Random(i).uniform(0, 1080):.0f}" cy="{random.Random(i + 50).uniform(0, 700):.0f}" r="{random.Random(i + 9).uniform(0.8, 2):.1f}" fill="#ffffff" opacity="{random.Random(i + 3).uniform(0.2, 0.6):.2f}"/>' for i in range(60))
      + suelo(1660, False)
      + '<g transform="translate(540,700)">' + helicoptero(0.62) + '</g>'
      + '<path id="cable1" d="M540,700 L540,870" stroke="#9fb3c8" stroke-width="4"/>'
      + '<g transform="translate(540,1010)"><g id="bur1">' + burbuja(140) + '</g></g>'
)
escena("e1", s1, f1, f2, 1.0, 1.06,
       '<div class="titulo" id="tit1"><b>1.000 m</b><small>DE CAÍDA · SIN PARACAÍDAS</small></div>')
J('tl.fromTo("#tit1", {opacity:1, y:0}, {opacity:1, duration:0.01}, 0);')
dibuja("#e1 .tick", 0.0, 0.6)
J(f'tl.fromTo("#bur1", {{rotation:-4}}, {{rotation:4, svgOrigin:"0 -140", duration:1.6, yoyo:true, repeat:3, ease:"sine.inOut", immediateRender:false}}, 0);')
J(f'tl.to("#e1 .maniqui", {{stroke:"{CY}", duration:0.3}}, {P("cuerpo") - 0.4:.2f});')
J(f'tl.fromTo("#e1 .maniqui", {{opacity:1}}, {{opacity:0.5, duration:0.3, yoyo:true, repeat:3, immediateRender:false}}, {P("cuerpo") - 0.4:.2f});')

# ================================================================== 2) LA BURBUJA: metro y medio · unos 12 kg
s2 = (fondo() + '<g transform="translate(540,1040)"><circle r="380" fill="url(#haloC)"/>' + burbuja(300) + '</g>'
      + f'<path id="cota" pathLength="1" d="M240,1410 L840,1410" stroke="{CY}" stroke-width="4"/><path d="M240,1390 L240,1430 M840,1390 L840,1430" stroke="{CY}" stroke-width="4"/>'
      + f'<path id="cotaV1" pathLength="1" d="M240,1040 L240,1390" stroke="{CY}" stroke-width="2" stroke-dasharray="6 8" opacity="0.6"/><path id="cotaV2" pathLength="1" d="M840,1040 L840,1390" stroke="{CY}" stroke-width="2" stroke-dasharray="6 8" opacity="0.6"/>')
escena("e2", s2, F(2), F(3), 1.0, 1.04,
       '<div class="dato" id="d2a" style="left:0;right:0;top:1440px;text-align:center"><b>Ø 1,5 m</b><small>DIÁMETRO</small></div>'
       '<div class="dato" id="d2b" style="right:70px;top:620px;text-align:right"><b>≈ 12 kg</b><small>PESO DE LA BURBUJA</small></div>'
       '')
dibuja("#cota", P("metro") - 0.2, 0.6)
entra("#d2a", P("metro"), "opacity:0, y:20")
entra("#d2b", P("doce") - 0.2, "opacity:0, x:40")

# ================================================================== 3) EL HELICÓPTERO LA SUELTA: empieza la caída libre
s3 = (f'<rect width="1080" height="1920" fill="url(#cieloG)"/>' + suelo(1660, False)
      + '<g transform="translate(540,660)">' + helicoptero(0.62, "heli3") + '</g>'
      + '<path id="cable3" d="M540,660 L540,830" stroke="#9fb3c8" stroke-width="4"/>'
      + '<g transform="translate(540,970)"><g id="bur3">' + burbuja(140) + '</g></g>')
escena("e3", s3, F(3), F(4), 1.0, 1.03, '<div class="grande" id="t3b" style="top:1380px"><b style="font-size:110px;letter-spacing:-3px">CAÍDA LIBRE</b></div>')
J(f'tl.to("#cable3", {{attr:{{d:"M540,660 L540,700"}}, duration:0.15}}, {P("suelta"):.2f});')
J(f'tl.fromTo("#bur3", {{y:0}}, {{y:420, duration:{F(4) - P("suelta"):.2f}, ease:"power2.in", immediateRender:false}}, {P("suelta"):.2f});')
entra("#t3b", P("caida") - 0.1, "opacity:0, y:30")
FX.append(("whoosh", P("suelta")))

# ---- plano de caída: la burbuja en el centro y el aire pasando hacia arriba (sensación de velocidad)
def caida(eid, t0, t1, extra_svg="", html="", vel=1.0):
    r_ = random.Random(eid)
    lineas = "".join(f'<path d="M{r_.uniform(40, 1040):.0f},{y:.0f} l0,{r_.uniform(80, 220):.0f}" stroke="#cfe6ff" stroke-width="{r_.uniform(2, 4):.1f}" opacity="{r_.uniform(0.15, 0.45):.2f}" stroke-linecap="round"/>' for y in [r_.uniform(0, 1920) for _ in range(34)])
    svg = (f'<rect width="1080" height="1920" fill="url(#cieloG)"/><g id="{eid}-aire">{lineas}<g transform="translate(0,1920)">{lineas}</g></g>'
           + '<g transform="translate(540,880)"><circle r="300" fill="url(#haloC)"/><g id="' + eid + '-bur">' + burbuja(210) + '</g></g>' + extra_svg)
    escena(eid, svg, t0, t1, 1.0, 1.03, html)
    per = 0.9 / vel
    J(f'tl.fromTo("#{eid}-aire", {{y:0}}, {{y:-1920, duration:{per:.2f}, ease:"none", repeat:{int((t1 - t0) / per) + 1}, immediateRender:false}}, {t0:.2f});')
    J(f'tl.fromTo("#{eid}-bur", {{rotation:-6}}, {{rotation:6, svgOrigin:"0 0", duration:0.7, yoyo:true, repeat:{int((t1 - t0) / 0.7) + 1}, ease:"sine.inOut", immediateRender:false}}, {t0:.2f});')

# ================================================================== 4) 90 km/h EN 3 SEGUNDOS
caida("e4", F(4), F(5), html='<div class="grande" id="d4" style="top:1260px"><b><span id="v4">0</span><i class="ud">km/h</i></b><small>EN SOLO 3 SEGUNDOS</small></div>', vel=0.8)
contador("v4", F(4) + 0.1, 0, 90, P("noventa") - F(4) + 0.1, ease="power1.in")
entra("#d4", F(4), "opacity:0, y:30")

# ================================================================== 5) EL CORAZÓN: más de 150 pulsaciones
s5 = (fondo() + '<g transform="translate(540,900)"><circle r="330" fill="url(#haloR)"/><g id="corazon"><path d="M0,150 C-280,-20 -180,-250 0,-115 C180,-250 280,-20 0,150 Z" fill="#ff5a4f"/><path d="M0,150 C-280,-20 -180,-250 0,-115" stroke="#ffffff" stroke-width="6" fill="none" opacity="0.25"/></g></g>')
escena("e5", s5, F(5), F(6), 1.0, 1.03,
       '<div class="grande" id="bpmW" style="top:1260px"><b><span id="bpmN">72</span></b><small>PULSACIONES POR MINUTO</small></div>')
J(f'tl.fromTo("#corazon", {{scale:1}}, {{scale:1.1, svgOrigin:"0 0", duration:0.2, yoyo:true, repeat:{int((F(6) - F(5)) / 0.2)}, ease:"power2.out", immediateRender:false}}, {F(5):.2f});')
contador("bpmN", P("supera") - 0.2, 72, 155, P("pulsaciones") - P("supera") + 0.2, ease="power2.in")
entra("#bpmW", F(5), "opacity:0, y:30")
FX.append(("latido", F(5) + 0.2))

# ================================================================== 6) EL AIRE LA FRENA: velocidad máxima ≈ 140 km/h
flecha = (f'<g transform="translate(540,880)"><g id="fAire"><path d="M0,-240 L0,-400" stroke="{CY}" stroke-width="16" stroke-linecap="round"/><path d="M-30,-380 L0,-430 L30,-380 Z" fill="{CY}"/></g></g>'
          + etiqueta(580, 500, "EL AIRE FRENA", CY, 30))
caida("e6", F(6), F(7), extra_svg=flecha, html='<div class="grande" id="d6" style="top:1260px"><b><span id="v6">90</span><i class="ud">km/h</i></b><small>VELOCIDAD MÁXIMA</small></div>', vel=1.3)
contador("v6", F(6) + 0.3, 90, 140, P("cuarenta") - F(6), ease="power2.out")
entra("#fAire", P("frena") - 0.2, "opacity:0, y:30")
entra("#e6 text", P("frena") - 0.1, "opacity:0")
entra("#d6", F(6), "opacity:0, y:30")

# ================================================================== 7) UNA ESFERA GIRA SIN CONTROL: desorientación y náuseas
s7 = (fondo() + '<g transform="translate(540,960)"><circle r="380" fill="url(#haloC)"/><g id="bur7">' + burbuja(260) + '</g>'
      + f'<path d="M-340,-60 A340,340 0 0 1 -60,-340" stroke="{AM}" stroke-width="10" fill="none" stroke-linecap="round"/><path d="M-80,-362 L-40,-338 L-82,-312 Z" fill="{AM}"/>'
      + f'<path d="M340,60 A340,340 0 0 1 60,340" stroke="{AM}" stroke-width="10" fill="none" stroke-linecap="round"/><path d="M80,362 L40,338 L82,312 Z" fill="{AM}"/></g>')
escena("e7", s7, F(7), F(8), 1.0, 1.04,
       '<div class="grande" style="top:1420px"><b id="l7b" style="font-size:84px;letter-spacing:-2px">MAREO</b><b id="l7c" style="font-size:84px;letter-spacing:-2px;color:#ffc24a">Y NÁUSEAS</b></div>')
J(f'tl.fromTo("#bur7", {{rotation:0}}, {{rotation:-1080, svgOrigin:"0 0", duration:{F(8) - F(7):.2f}, ease:"none", immediateRender:false}}, {F(7):.2f});')
entra("#l7b", P("orientacion") - 0.3, "opacity:0, y:30")
entra("#l7c", P("nauseas") - 0.15, "opacity:0, y:30")

# ================================================================== 8) LA CAÍDA DURA UNOS 28 SEGUNDOS
s8 = (fondo() + f'<rect x="140" y="1250" width="800" height="30" rx="15" fill="{LN}"/><rect id="barra8" x="140" y="1250" width="800" height="30" rx="15" fill="{AM}" style="transform-origin:140px 1265px"/>')
escena("e8", s8, F(8), F(9), 1.0, 1.03, '<div class="grande" id="g8" style="top:860px"><b><span id="segN">0</span> s</b><small>DURA LA CAÍDA</small></div>')
J(f'tl.fromTo("#barra8", {{scaleX:0}}, {{scaleX:1, duration:{P("veintiocho") - F(8) + 0.3:.2f}, ease:"power1.out", immediateRender:false}}, {F(8):.2f});')
contador("segN", F(8), 0, 28, P("veintiocho") - F(8) + 0.3, ease="power1.out")
entra("#g8", F(8), "opacity:0, y:30")

# ================================================================== 9) EL PROBLEMA ES EL FINAL: solo unos 40 cm de aire
s9 = (fondo() + suelo(1500, False) + '<g transform="translate(540,1170)"><g transform="rotate(90)">' + burbuja(330) + '</g></g>'
      + f'<path id="cota9" pathLength="1" d="M760,1350 L760,1500" stroke="{RJ}" stroke-width="5"/><path d="M740,1350 L780,1350 M740,1500 L780,1500" stroke="{RJ}" stroke-width="5"/>')
escena("e9", s9, F(9), F(10), 1.0, 1.04,
       '<div class="tag rojo" id="t9" style="left:70px;top:600px">EL PROBLEMA: EL IMPACTO</div><div class="dato rojo" id="d9" style="left:600px;top:1530px"><b>≈ 40 cm</b><small>DE AIRE</small></div>')
entra("#t9", P("problema") - 0.1, "opacity:0, x:-40")
dibuja("#cota9", P("cuarenta", 2) - 0.3, 0.5)
entra("#d9", P("cuarenta", 2), "opacity:0, x:-20")

# ================================================================== 10-11) LA DECELERACIÓN: unas 200 g · el cuerpo tolera unas 45
BX, BY, BH = 240, 1560, 760
def bh(g): return BH * g / 220
s10 = (fondo() + f'<path d="M150,{BY} L930,{BY}" stroke="{TX}" stroke-width="3"/>'
       + f'<rect x="{BX}" y="{BY - BH}" width="220" height="{BH}" rx="12" fill="{LN}"/><rect id="barG" x="{BX}" y="{BY - bh(200):.0f}" width="220" height="{bh(200):.0f}" rx="12" fill="{RJ}" style="transform-origin:{BX + 110}px {BY}px"/>'
       + f'<rect x="{BX + 380}" y="{BY - BH}" width="220" height="{BH}" rx="12" fill="{LN}"/><rect id="barH" x="{BX + 380}" y="{BY - bh(45):.0f}" width="220" height="{bh(45):.0f}" rx="12" fill="#2fd27a" style="transform-origin:{BX + 490}px {BY}px"/>'
       + f'<path id="lim45" pathLength="1" d="M150,{BY - bh(45):.0f} L930,{BY - bh(45):.0f}" stroke="#2fd27a" stroke-width="3" stroke-dasharray="10 8"/>'
       + etiqueta(BX + 110, BY + 50, "EL IMPACTO", RJ, 26, "middle") + etiqueta(BX + 490, BY + 50, "LO QUE TOLERAS", "#2fd27a", 26, "middle"))
escena("e10", s10, F(10), F(12), 1.0, 1.04,
       f'<div class="numbar" id="nG" style="left:{BX}px;top:{BY - bh(200) - 110:.0f}px">≈ <span id="gN">0</span> g</div>'
       f'<div class="numbar verde" id="nH" style="left:{BX + 380}px;top:{BY - bh(45) - 110:.0f}px">≈ 45 g</div>'
       '')
J(f'tl.fromTo("#barG", {{scaleY:0}}, {{scaleY:1, duration:0.9, ease:"power3.out", immediateRender:false}}, {P("doscientas") - 0.3:.2f}); tl.set("#barG", {{scaleY:0}}, 0);')
contador("gN", P("doscientas") - 0.3, 0, 200, 0.9, ease="power3.out")
entra("#nG", P("doscientas") - 0.3, "opacity:0, y:20")
J(f'tl.fromTo("#barH", {{scaleY:0}}, {{scaleY:1, duration:0.7, ease:"power3.out", immediateRender:false}}, {P("cinco") - 0.3:.2f}); tl.set("#barH", {{scaleY:0}}, 0);')
entra("#nH", P("cinco") - 0.2, "opacity:0, y:20")
dibuja("#lim45", P("instante") - 0.4, 0.6)
FX.append(("golpe", P("doscientas") - 0.2))

# ================================================================== 12) LAS LESIONES: costillas, columna, órganos (vista de rayos X)
rx = ['<g transform="translate(540,1080)">',
      '<path d="M-60,-430 Q0,-470 60,-430 Q80,-380 60,-340 L40,-310 L-40,-310 L-60,-340 Q-80,-380 -60,-430 Z" fill="none" stroke="#bfe3ff" stroke-width="5" opacity="0.8"/>',
      '<path d="M-170,-270 Q0,-310 170,-270 L200,200 Q0,250 -200,200 Z" fill="#4fd1ff" opacity="0.05" stroke="#4fd1ff" stroke-width="3"/>',
      '<g id="rxCol"><path d="M0,-300 L0,200" stroke="#e8f4ff" stroke-width="14" stroke-dasharray="20 7" stroke-linecap="butt"/></g>',
      '<g id="rxCos">' + "".join(f'<path d="M0,{-240 + i * 42} Q{-130 - i * 4},{-262 + i * 42} {-150 + i * 2},{-180 + i * 42} M0,{-240 + i * 42} Q{130 + i * 4},{-262 + i * 42} {150 - i * 2},{-180 + i * 42}" stroke="#e8f4ff" stroke-width="8" fill="none" stroke-linecap="round"/>' for i in range(7)) + '</g>',
      '<g id="rxOrg"><path d="M-110,-200 C-150,-120 -140,0 -70,20 C-40,-40 -40,-150 -60,-210 Z" fill="#ff8a8a" opacity="0.35"/><path d="M110,-200 C150,-120 140,0 70,20 C40,-40 40,-150 60,-210 Z" fill="#ff8a8a" opacity="0.35"/>'
      '<path d="M10,-110 C-40,-150 -70,-90 -20,-50 L10,-20 L40,-50 C80,-90 50,-150 10,-110 Z" fill="#ff5a4f" opacity="0.6"/></g>',
      '<path d="M-150,200 Q0,260 150,200 L120,290 Q0,320 -120,290 Z" fill="none" stroke="#e8f4ff" stroke-width="7"/>',
      '</g>']
s12 = (fondo() + '<rect width="1080" height="1920" fill="#02060d" opacity="0.6"/>' + "".join(rx)
       + f'<path id="ln1" pathLength="1" d="M700,840 L860,760" stroke="{RJ}" stroke-width="3"/><path id="ln2" pathLength="1" d="M545,1150 L860,1230" stroke="{RJ}" stroke-width="3"/><path id="ln3" pathLength="1" d="M520,960 L220,1380" stroke="{RJ}" stroke-width="3"/>')
escena("e12", s12, F(12), F(13), 1.0, 1.04,
       '<div class="tag rojo" id="t12a" style="left:760px;top:700px">COSTILLAS</div><div class="tag rojo" id="t12b" style="left:760px;top:1240px">COLUMNA</div><div class="tag rojo" id="t12c" style="left:70px;top:1390px">ÓRGANOS INTERNOS</div>'
       '<div class="nota12" id="n12">Lesiones incompatibles con la vida</div>')
for sel, ln, tg, w in (("#rxCos path", "#ln1", "#t12a", "costillas"), ("#rxCol path", "#ln2", "#t12b", "columna"), ("#rxOrg path", "#ln3", "#t12c", "organos")):
    J(f'tl.to("{sel}", {{stroke:"{RJ}", duration:0.15}}, {P(w) - 0.1:.2f}); tl.fromTo("{sel}", {{opacity:1}}, {{opacity:0.35, duration:0.12, yoyo:true, repeat:3, immediateRender:false}}, {P(w) - 0.1:.2f});')
    dibuja(ln, P(w) - 0.2, 0.35)
    entra(tg, P(w) - 0.05, "opacity:0, x:20", 0.3)
J(f'tl.to("#rxOrg path", {{fill:"{RJ}", opacity:0.85, duration:0.2}}, {P("organos") - 0.1:.2f}); tl.fromTo("#rxOrg", {{x:-8}}, {{x:8, duration:0.06, yoyo:true, repeat:7, immediateRender:false}}, {P("organos"):.2f});')
entra("#n12", P("esqueleto") - 0.1, "opacity:0, y:20")
J(f'tl.fromTo("#e12-cam", {{x:0}}, {{x:10, duration:0.05, yoyo:true, repeat:5, immediateRender:false}}, {P("costillas"):.2f});')

# ================================================================== 13) EL PLÁSTICO NO RESISTE: la burbuja revienta
frag = "".join(f'<g transform="translate({280 * math.cos(a):.0f},{280 * math.sin(a):.0f}) rotate({math.degrees(a):.0f})"><path class="frag" d="M-38,-6 L30,-14 L42,4 L-20,12 Z" fill="#cdeeff" fill-opacity="0.35" stroke="#e6f6ff" stroke-width="3"/></g>' for a in [i * 0.4 for i in range(16)])
s13 = (fondo() + suelo(1500, False) + '<g transform="translate(540,1220)"><g transform="rotate(90)">' + maniqui(280) + '</g><g id="bur13">' + burbuja(280, False) + '</g>'
       + '<g id="grietas" opacity="0">' + "".join(f'<path d="M0,280 L{dx},{dy} L{dx * 1.3:.0f},{dy * 0.6:.0f}" stroke="#ffffff" stroke-width="4" fill="none"/>' for dx, dy in ((-120, 120), (80, 160), (160, 60), (-200, 40))) + '</g>'
       + f'<g id="frags" opacity="0">{frag}</g><circle id="flash13" r="300" fill="url(#haloC)" opacity="0"/></g>')
escena("e13", s13, F(13), F(14), 1.0, 1.04, '<div class="grande" id="t13" style="top:620px"><b style="font-size:84px;letter-spacing:-2px;color:#ff5a4f">LA BURBUJA REVIENTA</b></div>')
entra("#t13", P("reviente") - 0.1, "opacity:0, y:20")
J(f'tl.to("#bur13", {{scaleY:0.82, scaleX:1.12, svgOrigin:"0 280", duration:0.5, ease:"power2.in"}}, {P("resista") - 0.3:.2f}); tl.to("#grietas", {{opacity:1, duration:0.1}}, {P("resista"):.2f});')
J(f'tl.set("#bur13, #grietas", {{opacity:0}}, {P("reviente"):.2f}); tl.set("#frags", {{opacity:1}}, {P("reviente"):.2f}); tl.fromTo("#flash13", {{opacity:1}}, {{opacity:0, duration:0.4, immediateRender:false}}, {P("reviente"):.2f});')
J(f'tl.fromTo("#frags .frag", {{x:0, y:0, rotation:0}}, {{x:(i) => Math.cos(i * 0.4 + 0.2) * 260, y:(i) => Math.sin(i * 0.4 + 0.2) * 260 - 60, rotation:(i) => (i % 2 ? 1 : -1) * 120, transformOrigin:"50% 50%", opacity:0, duration:1.2, ease:"power3.out", immediateRender:false}}, {P("reviente"):.2f});')
FX.append(("rompe", P("reviente")))

# ================================================================== 14) SOLO PROTEGE DESDE ~6 m (un segundo piso)
s14 = (fondo() + suelo(1560, False)
       + '<g id="casa14"><rect x="170" y="1190" width="300" height="370" fill="#1d2c44" stroke="#9fb3c8" stroke-width="4"/><path d="M150,1190 L320,1080 L490,1190 Z" fill="#26364f" stroke="#9fb3c8" stroke-width="4"/>'
       + "".join(f'<rect x="{x}" y="{y}" width="70" height="80" fill="#3f6f8f" opacity="0.7"/>' for x in (210, 360) for y in (1230, 1400)) + '</g>'
       + f'<path d="M520,1190 L520,1560" stroke="{CY}" stroke-width="4"/><path d="M500,1190 L540,1190 M500,1560 L540,1560" stroke="{CY}" stroke-width="4"/>'
       + '<g transform="translate(95,1130)"><g id="mini14">' + burbuja(60, False) + '</g></g>'
       + f'<path d="M830,650 L830,1560" stroke="{RJ}" stroke-width="4" stroke-dasharray="12 10"/><path d="M810,650 L850,650" stroke="{RJ}" stroke-width="4"/>')
escena("e14", s14, F(14), F(15), 1.0, 1.04,
       '<div class="dato" id="d14a" style="left:550px;top:1310px"><b>≈ 6 m</b><small>PROTEGE</small></div>'
       '<div class="dato rojo" id="d14b" style="right:60px;top:530px;text-align:right"><b>1.000 m</b><small>NO PROTEGE</small></div>')
J(f'tl.fromTo("#mini14", {{y:0}}, {{y:370, duration:0.6, ease:"power2.in", immediateRender:false}}, {P("caida", 3) - 0.2:.2f}); tl.to("#mini14", {{y:330, duration:0.35, ease:"power2.out", yoyo:true, repeat:1}}, {P("caida", 3) + 0.4:.2f});')
entra("#d14a", P("seis") - 0.1, "opacity:0, x:-20")
entra("#d14b", P("piso") - 0.2, "opacity:0, x:-20")

# ================================================================== 15) DESDE 1.000 m NO CAMBIA EL RESULTADO. SOLO LO RETRASA.
s15 = (f'<rect width="1080" height="1920" fill="url(#cieloG)"/>' + suelo(1660, False)
       + '<g transform="translate(540,700)">' + helicoptero(0.62, "heli15") + '</g>'
       + f'<path d="M470,780 L470,1200" stroke="{RJ}" stroke-width="3" stroke-dasharray="10 12" opacity="0.7"/>')
escena("e15", s15, F(15), DUR, 1.06, 1.0,
       '<div class="cierre" id="c15a">NO CAMBIA EL RESULTADO.</div><div class="cierre fuerte" id="c15b">SOLO LO RETRASA.</div>')
entra("#c15a", P("resultado") - 0.3, "opacity:0, y:20", 0.6)
entra("#c15b", P("retrasa") - 0.2, "opacity:0, y:20", 0.6)
tfin = FE(15) + 0.6
J(f'tl.set("#negroF", {{opacity:0}}, 0); tl.to("#negroF", {{opacity:1, duration:0.5}}, {tfin:.2f});')
OVR.append('<div id="negroF"></div>')
FX.append(("final", tfin))

# rotores y balizas siempre en marcha
J(f'tl.fromTo(".rotor", {{scaleX:1}}, {{scaleX:0.2, transformOrigin:"50% 50%", duration:0.05, yoyo:true, repeat:{int(DUR / 0.05)}, ease:"none", immediateRender:false}}, 0);')
J(f'tl.fromTo(".baliza", {{opacity:1}}, {{opacity:0.15, duration:0.45, yoyo:true, repeat:{int(DUR / 0.45)}, ease:"steps(1)", immediateRender:false}}, 0);')

# ------------------------------------------------------------------ subtítulos de siempre (arriba, palabra a palabra, recuadro azul en lo importante)
CLAVE = set(norm(w) for w in ["mil", "plastico", "cuerpo", "metro", "doce", "suelta", "libre", "noventa", "cincuenta", "cuarenta", "esfera", "orientacion",
                               "nauseas", "veintiocho", "final", "centimetros", "doscientas", "gravedad", "humano", "costillas", "columna", "organos",
                               "reviente", "seis", "piso", "resultado", "retrasa"])
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
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#03060c}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;background:#03060c;color:{TX}}}
.esc{{position:absolute;inset:0;overflow:hidden}}
.cam{{position:absolute;inset:0;transform-origin:540px 1080px}}
.titulo{{position:absolute;left:0;right:0;top:1330px;text-align:center}} .titulo b{{display:block;font:800 150px/1 Inter;letter-spacing:-5px;color:#fff}} .titulo small{{display:block;margin-top:14px;font:700 30px Inter;letter-spacing:6px;color:{CY}}}
.dato{{position:absolute;white-space:nowrap}} .dato b{{display:block;font:800 76px/1 Inter;letter-spacing:-2px;color:#fff}} .dato small{{display:block;margin-top:8px;font:700 26px Inter;letter-spacing:5px;color:{CY}}}
.dato.rojo b{{color:{RJ}}} .dato.rojo small{{color:#ffb3ad}}
.ficha{{position:absolute;left:70px;right:70px;top:1560px;display:flex;gap:16px}} .ficha div{{flex:1;padding:14px 18px;border:1px solid rgba(79,209,255,0.35);border-radius:10px;background:rgba(8,17,31,0.75)}}
.ficha span{{display:block;font:700 22px Inter;letter-spacing:4px;color:{MU}}} .ficha b{{display:block;margin-top:6px;font:800 32px Inter;color:#fff}}
.tag{{position:absolute;padding:10px 20px;border-left:5px solid {CY};background:rgba(8,17,31,0.8);font:800 30px Inter;letter-spacing:4px;color:#fff}} .tag.rojo{{border-left-color:{RJ}}}
.hud{{position:absolute;left:60px;top:480px;z-index:40;padding:10px 18px;border:1px solid rgba(255,255,255,0.25);border-radius:10px;background:rgba(5,10,20,0.7)}} .hud.der{{left:auto;right:60px;text-align:right}}
.hud small{{display:block;font:700 22px Inter;letter-spacing:4px;color:{MU}}} .hud b{{font:800 44px Inter;font-variant-numeric:tabular-nums;color:#fff}}
.grande{{position:absolute;left:0;right:0;top:1300px;text-align:center}} .grande b{{display:block;font:800 200px/1 Inter;letter-spacing:-6px;color:#fff;font-variant-numeric:tabular-nums}} .grande .ud{{font-style:normal;font-size:70px;letter-spacing:0;margin-left:16px;color:{CY}}} .grande small{{display:block;margin-top:10px;font:700 26px Inter;letter-spacing:6px;color:{CY}}}
.lista{{position:absolute;left:70px;top:1480px}} .lista div{{margin-bottom:14px;padding:10px 20px;border-left:5px solid {AM};background:rgba(8,17,31,0.8);font:800 34px Inter;letter-spacing:3px;color:#fff}}
.numbar{{position:absolute;width:220px;white-space:nowrap;text-align:center;font:800 60px Inter;color:{RJ};font-variant-numeric:tabular-nums}} .numbar.verde{{color:#2fd27a}}
.formula{{position:absolute;left:70px;right:70px;top:1660px;text-align:center;font:600 26px Inter;color:{MU};letter-spacing:1px}}
.nota12{{position:absolute;left:0;right:0;top:1640px;text-align:center;font:800 36px Inter;letter-spacing:2px;color:#ffb3ad}}
.cierre{{position:absolute;left:70px;right:70px;top:1260px;text-align:center;font:800 64px/1.1 Inter;letter-spacing:-1px;color:#fff}} .cierre.fuerte{{top:1370px;color:{RJ};font-size:88px}}
#negroF{{position:absolute;inset:0;z-index:69;background:#000;pointer-events:none}}
#grano{{position:absolute;inset:0;z-index:57;pointer-events:none;opacity:0.04;background:url(assets/grano.png);mix-blend-mode:overlay}}
#vineta{{position:absolute;inset:0;z-index:56;pointer-events:none;background:radial-gradient(110% 80% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.6))}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:520px;z-index:55;pointer-events:none;background:linear-gradient(rgba(2,4,8,0.85), rgba(2,4,8,0))}}
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
  <div id="vineta"></div><div id="grano"></div>
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

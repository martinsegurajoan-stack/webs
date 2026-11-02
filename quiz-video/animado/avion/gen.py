#!/usr/bin/env python3
"""«¿Qué pasa si un avión pierde los dos motores?» — documental: planos 3D (Three.js, assets/motor3d.js) + esquemas 2D
(SVG) + subtítulos habituales de @mundo.supuesto. Todo sincronizado con la voz (tiempos.json).
  python3 gen.py → index.html + efectos.json"""
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
    raise KeyError(f"{word} {n}")
def F(n): return FR[n - 1]["ini"]
tl, FX, OVR, ESC = [], [], [], []
def J(s): tl.append(s)
NID = [0]
def nid(p="e"):
    NID[0] += 1
    return f"{p}{NID[0]}"
BG, INK, MUTED = "#070c16", "#e9f1fb", "#8796ad"
ICE, AMB, RED, GRN = "#9fdcff", "#ffb547", "#ff5a52", "#4cd18a"
def pop(sel, t, d=0.45, frm="opacity:0, y:24", ease="power3.out"):
    J(f'tl.set("{sel}", {{opacity:0}}, 0);')
    J(f'tl.fromTo("{sel}", {{{frm}}}, {{opacity:1, x:0, y:0, scale:1, duration:{d}, ease:"{ease}", immediateRender:false}}, {t:.2f});')
def fuera(sel, t, d=0.3):
    J(f'tl.to("{sel}", {{opacity:0, duration:{d}, ease:"power2.in"}}, {t:.2f});')
def escena(eid, cuerpo):
    ESC.append(f'<div class="esc" id="{eid}"><div class="cam" id="{eid}-cam"><svg width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0;overflow:visible">{cuerpo}</svg></div></div>')
def mostrar(eid, t0, t1):
    J(f'tl.set("#{eid}", {{opacity:0}}, 0); tl.set("#{eid}", {{opacity:1}}, {t0:.2f}); tl.set("#{eid}", {{opacity:0}}, {t1:.2f});')
def camara(eid, t0, t1, desde, hasta, ease="sine.inOut"):
    x0, y0, s0 = desde; x1, y1, s1 = hasta
    J(f'tl.fromTo("#{eid}-cam", {{x:{x0}, y:{y0}, scale:{s0}}}, {{x:{x1}, y:{y1}, scale:{s1}, duration:{t1 - t0:.2f}, ease:"{ease}", immediateRender:false}}, {t0:.2f});')
def chip(txt, t, t_out, x, y, color=ICE):
    i = nid("ch")
    OVR.append(f'<div class="chip" id="{i}" style="left:{x}px;top:{y}px;border-color:{color}"><b style="background:{color}"></b>{txt}</div>')
    pop(f"#{i}", t, 0.4, "opacity:0, x:-30"); fuera(f"#{i}", t_out)
def fuente(txt, t, t_out):
    i = nid("fu")
    OVR.append(f'<div class="fuente" id="{i}">{txt}</div>')
    pop(f"#{i}", t, 0.4, "opacity:0"); fuera(f"#{i}", t_out)
def niebla(t):
    """Transición «a través de la nube» (solo 3 en todo el vídeo)."""
    J(f'tl.fromTo("#niebla", {{opacity:0, scale:1.25}}, {{opacity:1, scale:1, duration:0.32, ease:"power2.in", immediateRender:false}}, {t - 0.32:.2f}); tl.to("#niebla", {{opacity:0, scale:0.9, duration:0.45, ease:"power2.out"}}, {t + 0.02:.2f});')
    FX.append(("whoosh", t - 0.35))
FONDO = '<rect width="1080" height="1920" fill="url(#fondoTec)"/><rect width="1080" height="1920" fill="url(#rejilla)" opacity="0.45"/>'

# tiempos clave para el motor 3D
K = {f"p{i}": F(i) for i in range(1, 14)}
K.update(fin=DUR, apagado=P("motores") + 0.2, piedra=P("piedra"), morro=P("morro"), rat=P("aparece"), gira=P("aeropuerto"), toma=P("aterrizo"), amera=P("amerizo"))
# altímetro del HUD (solo en los planos 3D de crucero): pares (t, metros)
ALT = [(0, 11000), (K["apagado"], 11000), (F(3), 10850), (F(4), 10850), (F(5), 10300), (F(8), 7400), (F(9), 7100)]

# ================================================================== 1) GANCHO (3D) — rótulo grande desde el fotograma 0
OVR.append('<div id="gancho"><div class="g0">A</div><div class="g1">11.000 m</div><div class="g2">DE ALTURA</div></div>')
J('tl.fromTo("#gancho", {scale:1.12}, {scale:1, duration:0.6, ease:"power3.out", immediateRender:false}, 0);')
J(f'tl.to("#gancho", {{opacity:0, y:-30, duration:0.35, ease:"power2.in"}}, {P("ahora") - 0.1:.2f});')
OVR.append('<div id="ecam" class="panel"><div class="et">AVISO</div>'
           '<div class="er" id="er1"><i></i>MOTOR 1 <span>APAGADO</span></div><div class="er" id="er2"><i></i>MOTOR 2 <span>APAGADO</span></div></div>')
pop("#ecam", P("apagarse") - 0.3, 0.3, "opacity:0, x:-30")
J(f'tl.set("#er1, #er2", {{opacity:0}}, 0); tl.set("#er1", {{opacity:1}}, {P("apagarse") - 0.2:.2f}); tl.set("#er2", {{opacity:1}}, {P("apagarse") + 0.1:.2f});')
J(f'tl.fromTo("#ecam .er i", {{opacity:1}}, {{opacity:0.25, duration:0.25, yoyo:true, repeat:9, ease:"none", immediateRender:false}}, {P("apagarse"):.2f});')
fuera("#ecam", F(2) - 0.05)
FX.append(("apagado", K["apagado"])); FX.append(("aviso", P("apagarse") - 0.2))
OVR.append(f'<div id="cuenta" class="panel"><div class="ct">CADA SEGUNDO CUENTA</div></div>')
pop("#cuenta", P("segundo") - 0.1, 0.3, "opacity:0, scale:1.15"); fuera("#cuenta", F(2) - 0.05)

# HUD de altitud (planos 3D 2, 4 y 8)
OVR.append('<div id="hud"><div class="hl">ALTITUD</div><div class="hn"><span id="hudn">11.000</span><small> m</small></div><div class="hs">SIN MOTORES</div></div>')
J('tl.set("#hud", {opacity:0}, 0);')
for a, b in ((F(2), F(3)), (F(4), F(5)), (F(8), F(9))):
    J(f'tl.set("#hud", {{opacity:1}}, {a:.2f}); tl.set("#hud", {{opacity:0}}, {b:.2f});')

# ================================================================== 2) NO CAE COMO UNA PIEDRA (3D)
chip("TRAYECTORIA DE PLANEO", P("planeador") - 0.9, F(3) - 0.1, 60, 1360, ICE)
chip("UNA PIEDRA CAERÍA RECTA", P("piedra") - 0.2, F(3) - 0.1, 60, 1444, RED)
FX.append(("caida", P("piedra")))

# ================================================================== 3) SUSTENTACIÓN: corte del ala con flujo de aire (2D)
f3 = F(3); niebla(f3)
perfil = "M160,1050 C210,940 430,900 610,930 C770,958 880,1018 930,1052 C860,1064 610,1084 410,1080 C260,1076 185,1066 160,1050 Z"
lineas = []
for k in (-4, -3, -2, -1, 1, 2, 3, 4):
    y0 = 1050 + k * 92
    if k < 0:
        A = 150 / abs(k) ** 0.7
        d = f"M-200,{y0} L120,{y0} C330,{y0 - A} 760,{y0 - A * 0.75} 980,{y0} L1300,{y0}"
        lineas.append(f'<path class="fl3a" d="{d}" stroke="{ICE}" stroke-width="5" fill="none" stroke-dasharray="46 34" opacity="{0.95 - 0.12 * abs(k):.2f}"/>')
    else:
        A = 44 / k
        d = f"M-200,{y0} L120,{y0} C330,{y0 + A} 760,{y0 + A} 980,{y0} L1300,{y0}"
        lineas.append(f'<path class="fl3b" d="{d}" stroke="#7aa6cc" stroke-width="5" fill="none" stroke-dasharray="46 34" opacity="{0.9 - 0.12 * k:.2f}"/>')
e3 = [FONDO, "".join(lineas),
      f'<g transform="rotate(-6 545 1050)"><path d="{perfil}" fill="url(#alaG)" stroke="#e9f1fb" stroke-width="4"/><path d="M200,1040 C400,960 700,960 900,1046" stroke="#ffffff" stroke-width="3" opacity="0.25" fill="none"/></g>',
      f'<g id="sus3"><path d="M545,1000 L545,560" stroke="{GRN}" stroke-width="22" stroke-linecap="round"/><path d="M490,610 L545,520 L600,610 Z" fill="{GRN}"/></g>',
      f'<text id="sust3" x="580" y="600" font-family="Inter" font-weight="900" font-size="46" fill="{GRN}">SUSTENTACIÓN</text>',
      f'<g id="pr3a" opacity="0"><text x="830" y="790" text-anchor="end" font-family="Inter" font-weight="800" font-size="32" fill="{ICE}">aire más rápido</text><text x="830" y="830" text-anchor="end" font-family="Inter" font-weight="700" font-size="28" fill="{MUTED}">menos presión</text></g>',
      f'<g id="pr3b" opacity="0"><text x="830" y="1310" text-anchor="end" font-family="Inter" font-weight="800" font-size="32" fill="#7aa6cc">aire más lento</text><text x="830" y="1350" text-anchor="end" font-family="Inter" font-weight="700" font-size="28" fill="{MUTED}">más presión</text></g>']
escena("e3", "".join(e3))
mostrar("e3", f3, F(4))
camara("e3", f3, F(4), (0, 0, 1.0), (0, -20, 1.06))
J(f'tl.fromTo(".fl3a", {{strokeDashoffset:0}}, {{strokeDashoffset:-1600, duration:{F(4) - f3:.2f}, ease:"none", immediateRender:false}}, {f3:.2f});')
J(f'tl.fromTo(".fl3b", {{strokeDashoffset:0}}, {{strokeDashoffset:-900, duration:{F(4) - f3:.2f}, ease:"none", immediateRender:false}}, {f3:.2f});')
J(f'tl.to("#pr3a", {{opacity:1, duration:0.4}}, {P("alas") - 0.2:.2f}); tl.to("#pr3b", {{opacity:1, duration:0.4}}, {P("alas") + 0.3:.2f});')
J(f'tl.set("#sus3, #sust3", {{opacity:0}}, 0); tl.fromTo("#sus3", {{opacity:1, scaleY:0}}, {{scaleY:1, svgOrigin:"545 1000", duration:0.8, ease:"back.out(1.5)", immediateRender:false}}, {P("generando") - 0.2:.2f}); tl.to("#sust3", {{opacity:1, duration:0.3}}, {P("sustentacion") - 0.1:.2f});')
FX.append(("sube", P("generando") - 0.2))
OVR.append(f'<div id="vel3" class="panel vel"><div class="pt">VELOCIDAD</div><div class="vb"><i id="vb3"></i></div><div class="vs">suficiente → el ala sustenta</div></div>')
pop("#vel3", P("velocidad") - 0.3, 0.4, "opacity:0, x:-30")
J(f'tl.fromTo("#vb3", {{scaleX:0}}, {{scaleX:0.78, transformOrigin:"0 50%", duration:1.0, ease:"power3.out", immediateRender:false}}, {P("velocidad"):.2f});')
fuera("#vel3", F(4) - 0.1)

# ================================================================== 4) EL MORRO BAJA (3D)
chip("EL MORRO BAJA PARA NO PERDER VELOCIDAD", P("morro") - 0.3, F(5) - 0.1, 60, 1360, AMB)
chip("SE CAMBIA ALTURA POR VELOCIDAD", P("precio") - 0.2, F(5) - 0.1, 60, 1444, ICE)

# ================================================================== 5) FINURA: 1 km de bajada = más de 15 km de avance (2D)
f5 = F(5)
avion2d = '<path d="M0,0 L-70,-6 L-84,-30 L-74,-30 L-52,-8 L-10,-8 L-34,-40 L-18,-40 L22,-8 L60,-6 Q78,0 60,6 L-70,6 Z" fill="#e9f1fb"/>'
regla = "".join(f'<path d="M{100 + i * 60},1000 L{100 + i * 60},{1016 if i % 5 else 1030}" stroke="#4a6080" stroke-width="3"/>' for i in range(16))
regla += "".join(f'<text x="{100 + i * 60}" y="1070" text-anchor="middle" font-family="Inter" font-weight="800" font-size="28" fill="{MUTED}">{i} km</text>' for i in (0, 5, 10, 15))
e5 = [FONDO, '<path d="M60,1000 L1040,1000" stroke="#4a6080" stroke-width="3"/>', regla,
      f'<path id="glide5" d="M100,880 L1000,940" stroke="{ICE}" stroke-width="6" stroke-dasharray="1" pathLength="1" style="stroke-dashoffset:1"/>',
      f'<g id="av5" transform="translate(100,880) rotate(4)">{avion2d}</g>',
      f'<g id="km5" opacity="0"><path d="M1030,880 L1030,940 M1018,880 L1042,880 M1018,940 L1042,940" stroke="{AMB}" stroke-width="5"/><text x="1010" y="860" text-anchor="end" font-family="Inter" font-weight="900" font-size="40" fill="{AMB}">1 km ↓</text></g>',
      f'<g id="mapa5" opacity="0"><circle cx="540" cy="1420" r="250" fill="#0e1a2e" stroke="#2b3d5c" stroke-width="3"/>'
      f'<circle id="alc5" cx="540" cy="1420" r="230" fill="{ICE}" fill-opacity="0.10" stroke="{ICE}" stroke-width="4" stroke-dasharray="14 10"/>'
      f'<g transform="translate(540,1420) rotate(-90) scale(0.55)">{avion2d}</g>'
      + "".join(f'<g><circle cx="{x}" cy="{y}" r="11" fill="{GRN}"/><path d="M{x - 18},{y} L{x + 18},{y}" stroke="#0e1a2e" stroke-width="4"/></g>' for x, y in ((420, 1300), (690, 1510), (610, 1260)))
      + f'<text x="540" y="1710" text-anchor="middle" font-family="Inter" font-weight="800" font-size="30" fill="#c9d8ea">alcance planeando</text></g>']
escena("e5", "".join(e5))
mostrar("e5", f5, F(6))
camara("e5", f5, F(6), (0, 30, 1.0), (0, -10, 1.04))
J(f'tl.to("#glide5", {{strokeDashoffset:0, duration:2.6, ease:"power1.inOut"}}, {P("avanzar") - 0.3:.2f}); tl.to("#av5", {{x:900, y:60, duration:2.6, ease:"power1.inOut"}}, {P("avanzar") - 0.3:.2f});')
J(f'tl.to("#km5", {{opacity:1, duration:0.3}}, {P("kilometro") - 0.3:.2f});')
OVR.append('<div id="fin5" class="dato"><div class="dk">FINURA DE PLANEO</div><div class="dn"><span>+15 km</span><small> por cada km de altura</small></div><div class="ds">Orientativo: depende del modelo, el peso y el viento</div></div>')
pop("#fin5", P("quince") - 0.3, 0.45)
FX.append(("golpe", P("quince") - 0.1))
J(f'tl.fromTo("#mapa5", {{opacity:0, scale:0.85}}, {{opacity:1, scale:1, svgOrigin:"540 1420", duration:0.5, ease:"power3.out", immediateRender:false}}, {P("baja", 2) - 0.2:.2f}); tl.fromTo("#alc5", {{scale:0}}, {{scale:1, svgOrigin:"540 1420", duration:1.0, ease:"power2.out", immediateRender:false}}, {P("baja", 2):.2f});')
J(f'tl.to("#fin5", {{y:-760, duration:0.5, ease:"power2.inOut"}}, {P("baja", 2) - 0.3:.2f});')
fuera("#fin5", F(6) - 0.1)

# ================================================================== 6) CABINA: velocidad de planeo, MAYDAY, buscar dónde (2D)
f6 = F(6); niebla(f6)
nub6 = "".join(f'<ellipse class="nb6" cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#ffe4d2" opacity="{o}"/>' for x, y, rx, ry, o in
               ((100, 760, 260, 40, 0.55), (520, 790, 320, 46, 0.6), (930, 770, 280, 40, 0.5), (300, 820, 360, 50, 0.7), (800, 830, 340, 52, 0.7), (1300, 800, 300, 44, 0.55)))
pfd = (f'<g transform="translate(70,1180)"><rect width="440" height="420" rx="10" fill="#05070b" stroke="#2a3240" stroke-width="5"/>'
       f'<clipPath id="pfdC"><rect x="10" y="10" width="420" height="400" rx="6"/></clipPath><g clip-path="url(#pfdC)"><g id="hor6"><rect x="-200" y="-300" width="840" height="510" fill="#2c6fb8"/><rect x="-200" y="210" width="840" height="510" fill="#7a4a24"/><path d="M-200,210 L640,210" stroke="#fff" stroke-width="3"/></g>'
       f'<path d="M150,210 L200,210 M240,210 L290,210" stroke="{AMB}" stroke-width="8"/><circle cx="220" cy="210" r="6" fill="{AMB}"/>'
       f'<rect x="10" y="10" width="78" height="400" fill="#000" opacity="0.55"/><rect x="352" y="10" width="78" height="400" fill="#000" opacity="0.55"/>'
       f'<text x="48" y="218" text-anchor="middle" font-family="Courier New" font-weight="700" font-size="26" fill="{GRN}">VEL</text>'
       f'<text id="alt6" x="391" y="218" text-anchor="middle" font-family="Courier New" font-weight="700" font-size="24" fill="#fff">8600</text>'
       f'<path d="M352,195 L430,195 L430,230 L352,230 Z" fill="none" stroke="#fff" stroke-width="2"/></g>'
       f'<text x="220" y="450" text-anchor="middle" font-family="Inter" font-weight="800" font-size="24" fill="{MUTED}">VELOCIDAD DE MEJOR PLANEO</text></g>')
nd = (f'<g transform="translate(570,1180)"><rect width="440" height="420" rx="10" fill="#05070b" stroke="#2a3240" stroke-width="5"/>'
      + "".join(f'<path d="M{220 - r},{380} A{r},{r} 0 0 1 {220 + r},380" stroke="#3a4a60" stroke-width="2" fill="none"/>' for r in (110, 220, 330))
      + f'<path d="M220,380 L220,60" stroke="{GRN}" stroke-width="2" stroke-dasharray="8 6"/><path d="M205,385 L220,350 L235,385 Z" fill="#fff"/>'
      + "".join(f'<g class="apt6"><circle cx="{x}" cy="{y}" r="13" fill="none" stroke="#c78bff" stroke-width="4"/><text x="{x + 20}" y="{y + 8}" font-family="Courier New" font-weight="700" font-size="22" fill="#c78bff">{n}</text></g>' for x, y, n in ((120, 170, "APT1"), (330, 120, "APT2"), (300, 260, "APT3")))
      + f'<text x="220" y="450" text-anchor="middle" font-family="Inter" font-weight="800" font-size="24" fill="{MUTED}">MAPA: AEROPUERTOS CERCANOS</text></g>')
e6 = ['<rect width="1080" height="1920" fill="#0b0e14"/>', '<rect x="0" y="300" width="1080" height="640" fill="url(#cieloCab)"/>',
      '<g id="mundo6">' + nub6 + '</g>',
      '<path d="M0,300 L1080,300 L1080,380 L760,360 L540,420 L320,360 L0,380 Z" fill="#1a1f28"/><path d="M520,420 L560,420 L600,940 L480,940 Z" fill="#1a1f28"/>'
      '<path d="M0,380 L320,360 L480,940 L0,940 Z" fill="none" stroke="#2a313d" stroke-width="18"/><path d="M1080,380 L760,360 L600,940 L1080,940 Z" fill="none" stroke="#2a313d" stroke-width="18"/>',
      '<rect x="0" y="930" width="1080" height="150" fill="#1d222b"/><rect x="0" y="930" width="1080" height="10" fill="#2b313c"/>',
      f'<g id="mc6"><rect x="80" y="975" width="170" height="70" rx="8" fill="#3a2a10"/><text x="165" y="1020" text-anchor="middle" font-family="Inter" font-weight="900" font-size="22" fill="#5a4318">AVISO</text></g>',
      f'<g id="mw6"><rect x="830" y="975" width="170" height="70" rx="8" fill="#3a1414"/><text x="915" y="1020" text-anchor="middle" font-family="Inter" font-weight="900" font-size="22" fill="#5a2020">ALARMA</text></g>',
      f'<rect id="mcl6" x="80" y="975" width="170" height="70" rx="8" fill="{AMB}" opacity="0"/><rect id="mwl6" x="830" y="975" width="170" height="70" rx="8" fill="{RED}" opacity="0"/>',
      '<rect x="0" y="1080" width="1080" height="840" fill="#232933"/>', pfd, nd,
      f'<g transform="translate(330,1650)"><rect width="420" height="110" rx="10" fill="#05070b" stroke="#2a3240" stroke-width="5"/><text x="30" y="70" font-family="Courier New" font-weight="700" font-size="28" fill="{MUTED}">TRANSPONDEDOR</text>'
      f'<text id="sq6" x="390" y="72" text-anchor="end" font-family="Courier New" font-weight="700" font-size="44" fill="{GRN}">2000</text><text id="sq6b" x="390" y="72" text-anchor="end" font-family="Courier New" font-weight="700" font-size="44" fill="{AMB}" opacity="0">7700</text></g>']
escena("e6", "".join(e6))
mostrar("e6", f6, F(7))
camara("e6", f6, F(7), (0, 0, 1.0), (0, -60, 1.1))
J(f'tl.fromTo("#mundo6", {{x:0, rotation:0}}, {{x:-420, rotation:-3, svgOrigin:"540 800", duration:{F(7) - f6:.2f}, ease:"none", immediateRender:false}}, {f6:.2f});')
J(f'tl.fromTo("#hor6", {{y:0, rotation:0}}, {{y:28, rotation:3, svgOrigin:"220 210", duration:{F(7) - f6:.2f}, ease:"sine.inOut", immediateRender:false}}, {f6:.2f});')
J(f'tl.to("#mcl6", {{opacity:0.9, duration:0.3, yoyo:true, repeat:{int((F(7) - f6) / 0.6)}, ease:"none"}}, {f6:.2f}); tl.to("#mwl6", {{opacity:0.85, duration:0.3, yoyo:true, repeat:5, ease:"none"}}, {f6 + 0.15:.2f});')
J(f'tl.set("#sq6", {{opacity:0}}, {P("emergencia") - 0.2:.2f}); tl.set("#sq6b", {{opacity:1}}, {P("emergencia") - 0.2:.2f});')
J(f'tl.fromTo(".apt6", {{opacity:0.25}}, {{opacity:1, duration:0.2, stagger:0.2, immediateRender:false}}, {P("buscan") - 0.1:.2f}); tl.set(".apt6", {{opacity:0.25}}, 0);')
OVR.append(f'<div id="may6" class="panel radio"><div class="pt">RADIO</div><div class="rm">MAYDAY · MAYDAY · MAYDAY</div><div class="rs">emergencia declarada · código 7700</div></div>')
pop("#may6", P("declaran") - 0.3, 0.35, "opacity:0, x:-30"); fuera("#may6", F(7) - 0.1)
FX.append(("radio", P("declaran") - 0.3)); FX.append(("aviso", f6 + 0.1))
chip("1 · VELOCIDAD DE MEJOR PLANEO", P("fijan") - 0.2, F(7) - 0.1, 60, 470, GRN)

# ================================================================== 7) LISTA DE EMERGENCIA + INTENTO DE REENCENDIDO (2D)
f7 = F(7); tm = P("con") - 0.2
items = (("VELOCIDAD DE MEJOR PLANEO", P("vez")), ("EMERGENCIA DECLARADA", P("siguen", 2) + 0.2), ("REENCENDIDO MOTOR 1", P("intentar")), ("REENCENDIDO MOTOR 2", P("encender")))
e7 = [FONDO, '<rect x="70" y="560" width="940" height="760" rx="16" fill="#f4efe2"/><rect x="70" y="560" width="940" height="110" rx="16" fill="#c0392b"/><rect x="70" y="640" width="940" height="30" fill="#c0392b"/>',
      '<text x="110" y="632" font-family="Inter" font-weight="900" font-size="40" fill="#fff">FALLO DE LOS DOS MOTORES</text>']
for k, (txt, t) in enumerate(items):
    y = 760 + k * 130
    e7.append(f'<g><text x="120" y="{y}" font-family="Courier New" font-weight="700" font-size="38" fill="#1a1a1a">{k + 1}. {txt}</text>'
              f'<path d="M120,{y + 30} L960,{y + 30}" stroke="#c9c1ad" stroke-width="2" stroke-dasharray="6 6"/>'
              f'<path id="ok7_{k}" d="M900,{y - 22} L920,{y} L960,{y - 44}" stroke="{"#1e9e5a" if k < 2 else "#c97a10"}" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" style="stroke-dashoffset:1"/></g>')
e7.append('<text x="120" y="1290" font-family="Inter" font-weight="700" font-size="26" fill="#6a6252">Lista orientativa · cada fabricante tiene la suya</text>')
escena("e7", "".join(e7))
mostrar("e7", f7, tm)
camara("e7", f7, tm, (0, 20, 1.0), (0, -10, 1.04))
for k, (txt, t) in enumerate(items):
    J(f'tl.to("#ok7_{k}", {{strokeDashoffset:0, duration:0.3, ease:"power2.out"}}, {t:.2f});'); FX.append(("clic", t))
# corte del motor: el aire lo hace girar (molinete) o arranque con la APU; chispa que no prende
aspas = "".join(f'<path d="M0,0 L{230 * math.cos(math.radians(a)):.0f},{230 * math.sin(math.radians(a)):.0f}" stroke="#9fb3cf" stroke-width="22" stroke-linecap="round"/>' for a in range(0, 360, 20))
e7b = [FONDO,
       f'<g transform="translate(540,920)"><circle r="290" fill="#0c1424" stroke="#c9d8ea" stroke-width="10"/><circle r="262" fill="none" stroke="#2b3d5c" stroke-width="4"/>'
       f'<g id="fan7">{aspas}</g><circle r="70" fill="#c9d8ea"/><circle r="70" fill="url(#brillo)"/></g>',
       "".join(f'<path class="aire7" d="M{-60},{720 + k * 80} L170,{720 + k * 80}" stroke="{ICE}" stroke-width="7" stroke-dasharray="30 22" stroke-linecap="round"/>' for k in range(6)),
       f'<g id="apu7" opacity="0"><rect x="640" y="1300" width="360" height="130" rx="12" fill="#13213a" stroke="{AMB}" stroke-width="4"/><text x="820" y="1355" text-anchor="middle" font-family="Inter" font-weight="900" font-size="34" fill="{AMB}">APU</text>'
       f'<text x="820" y="1400" text-anchor="middle" font-family="Inter" font-weight="700" font-size="26" fill="#c9d8ea">unidad auxiliar</text><path id="apuL7" d="M820,1300 C820,1230 700,1230 650,1180" stroke="{AMB}" stroke-width="7" fill="none" stroke-dasharray="20 14"/></g>',
       f'<g id="chis7" opacity="0"><path d="M540,920 l-30,-50 l20,0 l-20,-50 l45,65 l-22,0 l30,40 Z" fill="#ffe27a"/></g>']
escena("e7b", "".join(e7b))
mostrar("e7b", tm, F(8))
camara("e7b", tm, F(8), (0, 0, 1.06), (0, 0, 1.0))
J(f'tl.fromTo("#fan7", {{rotation:0}}, {{rotation:540, svgOrigin:"0 0", duration:{F(8) - tm:.2f}, ease:"none", immediateRender:false}}, {tm:.2f});')
J(f'tl.fromTo(".aire7", {{strokeDashoffset:0}}, {{strokeDashoffset:-260, duration:{F(8) - tm:.2f}, ease:"none", immediateRender:false}}, {tm:.2f});')
J(f'tl.to("#apu7", {{opacity:1, duration:0.35}}, {P("unidad") - 0.2:.2f}); tl.fromTo("#apuL7", {{strokeDashoffset:0}}, {{strokeDashoffset:-170, duration:2, ease:"none", immediateRender:false}}, {P("unidad"):.2f});')
J(f'tl.to("#chis7", {{opacity:1, duration:0.05, yoyo:true, repeat:5}}, {P("disponible") - 0.2:.2f});')
chip("① EL AIRE HACE GIRAR EL MOTOR", P("aire", 2) - 0.3, F(8) - 0.1, 60, 470, ICE)
chip("② ARRANQUE CON LA APU, SI ESTÁ DISPONIBLE", P("unidad") - 0.2, F(8) - 0.1, 60, 1540, AMB)
FX.append(("intento", P("disponible") - 0.3))

# ================================================================== 8) LA RAT (3D, desde abajo)
chip("RAT · TURBINA DE EMERGENCIA", P("rat") - 0.2, F(9) - 0.1, 60, 1360, AMB)
FX.append(("clunk", P("aparece") + 0.05)); FX.append(("helice", P("aparece") + 0.6))

# ================================================================== 9) QUÉ HACE LA RAT (2D)
f9 = F(9)
sil = ('<path d="M540,480 C565,480 575,520 575,560 L575,1440 L540,1520 L505,1440 L505,560 C505,520 515,480 540,480 Z" fill="#c9d8ea"/>'
       '<path d="M505,900 L90,1160 L90,1210 L505,1060 Z M575,900 L990,1160 L990,1210 L575,1060 Z" fill="#c9d8ea"/>'
       '<path d="M505,1380 L380,1470 L380,1500 L505,1460 Z M575,1380 L700,1470 L700,1500 L575,1460 Z" fill="#c9d8ea"/>'
       '<rect x="300" y="1000" width="44" height="120" rx="18" fill="#8796ad"/><rect x="736" y="1000" width="44" height="120" rx="18" fill="#8796ad"/>')
e9 = [FONDO, sil,
      f'<g id="ratp9"><circle cx="600" cy="1080" r="20" fill="{AMB}"/><path id="hel9" d="M600,1050 L600,1110" stroke="#fff" stroke-width="6" stroke-linecap="round"/></g>',
      f'<path class="en9" d="M600,1080 C620,1300 380,1400 230,1560" stroke="{AMB}" stroke-width="8" fill="none" stroke-dasharray="22 16"/>',
      f'<path class="en9" d="M600,1080 C680,1300 760,1400 850,1560" stroke="{AMB}" stroke-width="8" fill="none" stroke-dasharray="22 16"/>',
      f'<g id="no9" opacity="0"><path d="M600,1080 C520,1060 420,1060 344,1060" stroke="{RED}" stroke-width="7" fill="none" stroke-dasharray="14 10"/><path d="M600,1080 C660,1060 700,1060 736,1060" stroke="{RED}" stroke-width="7" fill="none" stroke-dasharray="14 10"/>'
      f'<path d="M296,1000 L348,1052 M348,1000 L296,1052 M732,1000 L784,1052 M784,1000 L732,1052" stroke="{RED}" stroke-width="12" stroke-linecap="round"/></g>']
escena("e9", "".join(e9))
mostrar("e9", f9, F(10))
camara("e9", f9, F(10), (0, -20, 1.0), (0, 10, 1.05))
J(f'tl.fromTo("#hel9", {{rotation:0}}, {{rotation:{int((F(10) - f9) * 900)}, svgOrigin:"600 1080", duration:{F(10) - f9:.2f}, ease:"none", immediateRender:false}}, {f9:.2f});')
J(f'tl.set(".en9", {{opacity:0}}, 0); tl.to(".en9", {{opacity:1, duration:0.3, stagger:0.4}}, {P("energia", 2) - 0.2:.2f}); tl.fromTo(".en9", {{strokeDashoffset:0}}, {{strokeDashoffset:-380, duration:{F(10) - f9:.2f}, ease:"none", immediateRender:false}}, {f9:.2f});')
OVR.append(f'<div id="bx9a" class="panel caja" style="left:60px;top:1540px;border-color:{AMB}"><div class="cn">MANDOS DE VUELO</div><div class="cs">presión hidráulica</div></div>')
OVR.append(f'<div id="bx9b" class="panel caja" style="left:600px;top:1540px;border-color:{AMB}"><div class="cn">INSTRUMENTOS</div><div class="cs">electricidad esencial</div></div>')
pop("#bx9a", P("mandos") - 0.2, 0.35); pop("#bx9b", P("instrumentos") - 0.2, 0.35)
fuera("#bx9a", F(10) - 0.1); fuera("#bx9b", F(10) - 0.1)
J(f'tl.to("#no9", {{opacity:1, duration:0.3}}, {P("arranca") - 0.3:.2f});')
chip("NO ARRANCA LOS MOTORES", P("arranca") - 0.3, F(10) - 0.1, 60, 470, RED)
fuente("Varía según el modelo de avión", P("muchos"), F(10) - 0.1)
FX.append(("golpe", P("arranca") - 0.2))

# ================================================================== 10) DÓNDE ATERRIZAR (3D, mapa desde arriba)
f10 = F(10); niebla(f10)
for k, (txt, wd, pos, col) in enumerate((("AEROPUERTO", "aeropuerto", (-700, 0, -1500), GRN), ("CAMPO", "campo", (-300, 0, 1600), AMB), ("AGUA", "agua", (2100, 0, 200), ICE))):
    OVR.append(f'<div class="marca3d" id="mk{k}" data-p="{pos[0]},{pos[1]},{pos[2]}" style="border-color:{col};color:{col}"><i style="border-color:{col}"></i><span>{txt}</span></div>')
    J(f'tl.set("#mk{k}", {{opacity:0}}, 0); tl.fromTo("#mk{k}", {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.35, ease:"back.out(2)", immediateRender:false}}, {P(wd) - 0.15:.2f}); tl.set("#mk{k}", {{opacity:0}}, {F(11):.2f});')
    FX.append(("tic", P(wd) - 0.15))
chip("UNA SOLA OPORTUNIDAD", P("oportunidad") - 0.3, F(11) - 0.1, 60, 470, RED)

# ================================================================== 11) AZORES 2001 (3D)
OVR.append('<div id="az11" class="dato"><div class="dk">VUELO 236 DE AIR TRANSAT · 2001</div><div class="dn" style="font-size:84px">≈19 min planeando</div>'
           '<div class="ds">Airbus A330 · Azores (Portugal) · 306 a bordo: sobrevivieron todos</div></div>')
pop("#az11", P("airbus") - 0.2, 0.45); fuera("#az11", F(12) - 0.1)
fuente("Fuente: GPIAA, informe oficial del accidente (Portugal)", P("airbus"), F(12) - 0.1)
FX.append(("toma", K["toma"]))
# ================================================================== 12) HUDSON 2009 (3D)
OVR.append('<div id="hu12" class="dato"><div class="dk">VUELO 1549 DE US AIRWAYS · 2009</div><div class="dn" style="font-size:84px">155 de 155</div>'
           '<div class="ds">Airbus A320 · río Hudson (Nueva York) · sobrevivieron todos</div></div>')
pop("#hu12", P("hudson") - 0.2, 0.45); fuera("#hu12", F(13) - 0.1)
fuente("Fuente: NTSB, informe oficial del accidente (EE. UU.)", P("hudson"), F(13) - 0.1)
FX.append(("splash", K["amera"]))
# ================================================================== 13) CIERRE EN BUCLE (3D): vuelve al encuadre del principio
J(f'tl.set("#gancho", {{opacity:1, y:0, scale:1}}, {DUR - 0.3:.2f});')

# ------------------------------------------------------------------ subtítulos habituales (arriba, palabra a palabra, recuadro azul)
CLAVE = set(norm(w) for w in ["once", "motores", "apagarse", "segundo", "piedra", "planeador", "velocidad", "sustentacion", "altura", "morro", "quince",
                               "kilometros", "emergencia", "aterrizar", "encender", "auxiliar", "rat", "turbina", "mandos", "instrumentos", "arranca",
                               "oportunidad", "aeropuerto", "campo", "agua", "diecinueve", "azores", "sobrevivieron", "hudson", "cuenta"])
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

import random
rr = random.Random(3)
for s in range(int(DUR / 0.08)):
    J(f'tl.set("#grano", {{backgroundPosition:"{rr.randint(0, 360)}px {rr.randint(0, 360)}px"}}, {s * 0.08:.2f});')

html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<script src="assets/three.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:{BG}}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;background:{BG}}}
#gl{{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:1}}
.esc{{position:absolute;inset:0;overflow:hidden;z-index:5;background:{BG}}}
.cam{{position:absolute;inset:0;transform-origin:50% 50%}}
#gancho{{position:absolute;left:0;right:0;top:640px;text-align:center;z-index:20;color:#fff;text-shadow:0 6px 30px rgba(0,0,0,0.55)}}
#gancho .g0{{font:800 54px Inter;letter-spacing:6px;color:#e6edf6}} #gancho .g1{{font:900 190px Inter;letter-spacing:-8px;line-height:0.95}} #gancho .g2{{font:800 54px Inter;letter-spacing:8px;color:#e6edf6}}
#ecam{{left:60px;top:1330px;width:520px;padding:18px 24px;border-left:6px solid {RED}}}
#ecam .et{{font:800 22px Inter;letter-spacing:5px;color:{MUTED};margin-bottom:6px}}
.er{{display:flex;align-items:center;gap:14px;font:800 40px "Courier New", monospace;color:#fff;padding:6px 0}} .er span{{color:{RED};margin-left:auto}} .er i{{width:18px;height:18px;border-radius:50%;background:{RED};box-shadow:0 0 18px {RED}}}
#cuenta{{left:60px;top:1560px;padding:14px 22px;border-left:6px solid {AMB}}} #cuenta .ct{{font:900 40px Inter;letter-spacing:2px;color:{AMB}}}
#hud{{position:absolute;left:60px;top:470px;width:300px;padding:12px 18px 14px;border-left:5px solid {ICE};background:rgba(7,12,22,0.62);z-index:40;color:{INK}}}
#hud .hl{{font:800 22px Inter;letter-spacing:6px;color:{MUTED}}} #hud .hn{{font:900 64px Inter;line-height:1;letter-spacing:-2px;font-variant-numeric:tabular-nums}} #hud .hn small{{font:800 30px Inter;color:{MUTED}}}
#hud .hs{{margin-top:6px;font:800 20px Inter;letter-spacing:4px;color:{RED}}}
.chip{{position:absolute;z-index:35;display:flex;align-items:center;gap:14px;padding:14px 22px;background:rgba(7,12,22,0.82);border:2px solid;border-radius:6px;font:800 30px Inter;letter-spacing:1px;color:{INK}}}
.chip b{{width:12px;height:12px;border-radius:50%}}
.fuente{{position:absolute;left:60px;right:60px;top:1712px;z-index:35;font:600 24px Inter;color:{MUTED};letter-spacing:0.5px}}
.panel{{position:absolute;z-index:30;background:rgba(9,15,28,0.88);border:1px solid #2b3d5c;border-radius:10px;color:{INK}}}
.pt{{font:800 22px Inter;letter-spacing:4px;color:{MUTED}}}
.vel{{left:60px;top:1500px;width:520px;padding:18px 24px}} .vb{{height:22px;background:#1e2c45;border-radius:4px;margin:12px 0 8px}} .vb i{{display:block;height:100%;border-radius:4px;background:linear-gradient(90deg,{ICE},{GRN})}}
.vs{{font:700 26px Inter;color:#c9d8ea}}
.dato{{position:absolute;left:60px;right:60px;top:1300px;z-index:30;padding:26px 30px;background:rgba(9,15,28,0.88);border-left:6px solid {ICE};color:{INK}}}
.dk{{font:800 24px Inter;letter-spacing:4px;color:{ICE}}} .dn{{font:900 100px Inter;letter-spacing:-3px;line-height:1.05}} .dn small{{font:800 32px Inter;letter-spacing:0;color:#c9d8ea}}
.ds{{font:600 26px Inter;color:{MUTED};margin-top:6px}}
.radio{{left:60px;top:560px;width:620px;padding:18px 24px;border-left:6px solid {RED}}} .rm{{font:900 42px "Courier New", monospace;color:#fff;margin-top:6px}} .rs{{font:700 24px Inter;color:{MUTED};margin-top:4px}}
.caja{{width:420px;padding:18px 22px;border:3px solid}} .cn{{font:900 34px Inter}} .cs{{font:700 24px Inter;color:{MUTED}}}
.marca3d{{position:absolute;left:0;top:0;z-index:30;display:flex;align-items:center;gap:12px;font:900 32px Inter;letter-spacing:2px;transform-origin:0 50%;white-space:nowrap}}
.marca3d i{{display:block;width:60px;height:60px;border-radius:50%;border:5px solid;margin-left:-30px;box-shadow:0 0 22px rgba(255,255,255,0.25)}}
.marca3d span{{background:rgba(7,12,22,0.8);padding:6px 14px;border-radius:6px}}
#niebla{{position:absolute;inset:-200px;z-index:58;opacity:0;pointer-events:none;background:radial-gradient(50% 40% at 30% 40%, #ffffff, rgba(255,255,255,0.85) 60%, rgba(230,236,244,0.95)), #f0f4f8}}
#grano{{position:absolute;inset:0;z-index:57;pointer-events:none;opacity:0.06;background:url(assets/grano.png);mix-blend-mode:overlay}}
#vineta{{position:absolute;inset:0;z-index:56;pointer-events:none;background:radial-gradient(110% 80% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.5))}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:560px;z-index:55;pointer-events:none;background:linear-gradient(rgba(4,8,16,0.75), rgba(4,8,16,0))}}
#marca{{position:absolute;left:0;right:0;top:1775px;text-align:center;font:700 28px Inter;color:#ffffff;opacity:0.32;pointer-events:none;z-index:61}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 62px Inter;color:rgba(255,255,255,0.4);line-height:1.22;text-shadow:0 3px 12px rgba(0,0,0,0.6)}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:3px solid #4ea3ff;border-radius:6px;background:rgba(78,163,255,0.18);opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <svg width="0" height="0" style="position:absolute"><defs>
    <radialGradient id="fondoTec" cx="0.5" cy="0.4" r="0.9"><stop offset="0" stop-color="#13213a"/><stop offset="1" stop-color="{BG}"/></radialGradient>
    <pattern id="rejilla" width="60" height="60" patternUnits="userSpaceOnUse"><path d="M60,0 L0,0 0,60" fill="none" stroke="#1b2a44" stroke-width="1.5"/></pattern>
    <linearGradient id="alaG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dfe7f2"/><stop offset="1" stop-color="#7d8ea8"/></linearGradient>
    <linearGradient id="cieloCab" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b2f5a"/><stop offset="0.7" stop-color="#e79c6a"/><stop offset="1" stop-color="#f3c39a"/></linearGradient>
    <radialGradient id="brillo" cx="0.35" cy="0.35" r="0.7"><stop offset="0" stop-color="#ffffff" stop-opacity="0.7"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>
  </defs></svg>
  <canvas id="gl" width="1080" height="1920"></canvas>
  {"".join(ESC)}
  <div id="topsombra"></div>
  {"".join(OVR)}
  <div id="vineta"></div><div id="grano"></div><div id="niebla"></div>
  <div id="marca">@mundo.supuesto</div>
  <div id="subs" data-layout-allow-overlap>{"".join(SUBS)}</div>
  <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
</div>
<script>window.K = {json.dumps(K)};</script>
<script src="assets/motor3d.js"></script>
<script>
const ALT = {json.dumps(ALT)};
const hudn = document.getElementById("hudn");
const marcas = [...document.querySelectorAll(".marca3d")];
function altura(t) {{ for (let i = 1; i < ALT.length; i++) if (t <= ALT[i][0]) {{ const [a, va] = ALT[i - 1], [b, vb] = ALT[i]; return va + (vb - va) * (t - a) / Math.max(1e-6, b - a); }} return ALT[ALT.length - 1][1]; }}
function frame(t) {{
  window.render3d(t);
  hudn.textContent = String(Math.round(altura(t) / 10) * 10).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ".");
  for (const m of marcas) {{ const [x, y, z] = m.dataset.p.split(",").map(Number); const [sx, sy] = window.proyecta(x, y, z); m.style.left = sx + "px"; m.style.top = (sy - 30) + "px"; }}
}}
const tl = gsap.timeline({{ paused: true, onUpdate: () => frame(tl.time()) }});
tl.set("#niebla", {{opacity:0}}, 0);
{chr(10).join(tl)}
tl.to({{}}, {{duration:0.01}}, {DUR - 0.01});
window.__timelines["main"] = tl;
window.addEventListener("hf-seek", e => frame(e.detail && e.detail.time != null ? e.detail.time : tl.time()));
tl.seek(0); frame(0);
</script>
</body></html>"""
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump(FX, open(os.path.join(BASE, "efectos.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones")

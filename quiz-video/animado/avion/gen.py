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
    OVR.append(f'<div class="chip" id="{i}" style="left:{x}px;top:{y}px;border-left:6px solid {color}"><b style="background:{color};color:{color}"></b>{txt}</div>')
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
K.update(fin=DUR, apagado=P("motores") + 0.2, piedra=P("piedra"), morro=P("morro"), intento1=P("encender") + 0.2, intento2=P("vuelven") + 0.2,
         rat=P("aparece"), tren=P("tren"), toca=P("tocan") + 0.1)
ALT = [(0, 11000), (K["apagado"], 11000), (F(3), 10900), (F(4), 10800), (F(5), 10300), (F(8), 6400), (F(9), 6200), (F(10), 2600), (F(11), 1500)]
CIELO = '<rect width="1080" height="1920" fill="url(#cieloOc)"/>'

# ================================================================== 1) GANCHO (3D): rótulo grande desde el fotograma 0
OVR.append('<div id="gancho"><div class="g0">A</div><div class="g1">11.000 m</div><div class="g2">DE ALTURA</div></div>')
J('tl.fromTo("#gancho", {scale:1.12}, {scale:1, duration:0.6, ease:"power3.out", immediateRender:false}, 0);')
J(f'tl.to("#gancho", {{opacity:0, y:-30, duration:0.35, ease:"power2.in"}}, {P("ahora") - 0.1:.2f});')
OVR.append(f'<div id="ecam" class="nota" style="left:60px;top:1330px;width:540px;--c:{RED}"><div class="nt">AVISO</div>'
           '<div class="er" id="er1"><i></i>MOTOR 1 <span>APAGADO</span></div><div class="er" id="er2"><i></i>MOTOR 2 <span>APAGADO</span></div></div>')
pop("#ecam", P("apagarse") - 0.3, 0.3, "opacity:0, x:-30")
J(f'tl.set("#er1, #er2", {{opacity:0}}, 0); tl.set("#er1", {{opacity:1}}, {P("apagarse") - 0.2:.2f}); tl.set("#er2", {{opacity:1}}, {P("apagarse") + 0.1:.2f});')
J(f'tl.fromTo("#ecam .er i", {{opacity:1}}, {{opacity:0.25, duration:0.25, yoyo:true, repeat:9, ease:"none", immediateRender:false}}, {P("apagarse"):.2f});')
fuera("#ecam", F(2) - 0.05)
FX.append(("apagado", K["apagado"]))
OVR.append(f'<div id="cuenta" class="nota" style="left:60px;top:1560px;--c:{AMB}"><div class="ct">CADA SEGUNDO CUENTA</div></div>')
pop("#cuenta", P("segundo") - 0.1, 0.3, "opacity:0, scale:1.15"); fuera("#cuenta", F(2) - 0.05)
OVR.append('<div id="hud" class="nota" style="--c:#9fdcff"><div class="nt">ALTITUD</div><div class="hn"><span id="hudn">11.000</span><small> m</small></div><div class="hs">SIN MOTORES</div></div>')
J('tl.set("#hud", {opacity:0}, 0);')
for a, b in ((F(2), F(3)), (F(4), F(5)), (F(8), F(9)), (F(10), F(11))):
    J(f'tl.set("#hud", {{opacity:1}}, {a:.2f}); tl.set("#hud", {{opacity:0}}, {b:.2f});')

# ================================================================== 2) ALARMAS + NO CAE (3D)
OVR.append('<div id="alarma"></div>')
J(f'tl.set("#alarma", {{opacity:0}}, 0); tl.to("#alarma", {{opacity:1, duration:0.18, yoyo:true, repeat:5, ease:"sine.inOut"}}, {P("alarmas") - 0.6:.2f});')
FX.append(("aviso", P("alarmas") - 0.6))
chip("UNA PIEDRA CAERÍA RECTA", P("piedra") - 0.3, F(3) - 0.1, 60, 1380, RED)
chip("EL AVIÓN PLANEA", P("planeador") - 0.3, F(3) - 0.1, 60, 1470, ICE)

# ================================================================== 3) SOBRE EL ALA (3D, líneas de flujo)
chip("AIRE RÁPIDO SOBRE EL ALA", P("rapido") - 0.3, F(4) - 0.1, 60, 1380, ICE)
chip("= SUSTENTACIÓN", P("volando") - 0.3, F(4) - 0.1, 60, 1470, GRN)

# ================================================================== 4) EL MORRO BAJA (3D)
chip("EL MORRO BAJA PARA NO PERDER VELOCIDAD", P("morro") - 0.3, F(5) - 0.1, 60, 1380, AMB)
chip("EL SUELO SE ACERCA", P("suelo") - 0.2, F(5) - 0.1, 60, 1470, RED)

# ================================================================== 5) EL MARGEN: 1 km de altura ≈ +15 km de vuelo (2D cinematográfico)
f5 = F(5); niebla(f5)
avion2d = ('<path d="M-90,0 C-90,-8 -80,-12 -60,-12 L70,-12 C88,-12 98,-6 102,0 C98,6 88,9 70,9 L-60,9 C-78,9 -86,5 -90,0 Z" fill="url(#fusG)"/>'
           '<path d="M-66,-12 L-92,-48 L-78,-48 L-48,-12 Z" fill="#1d3a6e"/><path d="M-82,-2 L-104,-2 L-100,4 L-80,4 Z" fill="#cfd6df"/>'
           '<path d="M18,3 L-16,18 L-2,18 L34,3 Z" fill="#cfd6df"/><rect x="0" y="9" width="26" height="9" rx="4.5" fill="#e9eef4"/>'
           + "".join(f'<circle cx="{x}" cy="-4" r="1.6" fill="#1a2230"/>' for x in range(-50, 66, 7)) + '<path d="M80,-7 L90,-7 L93,-3 L82,-3 Z" fill="#1a2230"/>')
montes = ('<path d="M0,1250 L120,1180 L220,1220 L340,1150 L470,1215 L600,1160 L720,1225 L860,1170 L1000,1230 L1080,1200 L1080,1920 L0,1920 Z" fill="#3a2a3c"/>'
          '<path d="M0,1300 L160,1260 L300,1290 L460,1250 L640,1300 L800,1262 L960,1295 L1080,1270 L1080,1920 L0,1920 Z" fill="#251c2a"/>')
regla = "".join(f'<path d="M{100 + i * 58},1330 L{100 + i * 58},{1346 if i % 5 else 1362}" stroke="#ffffff" stroke-opacity="0.7" stroke-width="3"/>' for i in range(16))
regla += "".join(f'<text x="{100 + i * 58}" y="1400" text-anchor="middle" font-family="Inter" font-weight="800" font-size="28" fill="#ffffff" fill-opacity="0.8">{i} km</text>' for i in (0, 5, 10, 15))
e5 = [CIELO, '<circle cx="860" cy="1150" r="70" fill="#ffd9a8" opacity="0.9"/><circle cx="860" cy="1150" r="190" fill="#ffd9a8" opacity="0.15"/>',
      "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#ffe1cf" opacity="{o}"/>' for x, y, rx, ry, o in ((160, 980, 220, 26, 0.35), (700, 1040, 300, 30, 0.3), (420, 1110, 260, 22, 0.25))),
      montes, '<path d="M70,1330 L1010,1330" stroke="#ffffff" stroke-opacity="0.6" stroke-width="3"/>', regla,
      f'<path d="M100,740 L970,800" stroke="{ICE}" stroke-width="14" opacity="0.25" stroke-linecap="round"/>',
      f'<path id="glide5" d="M100,740 L970,800" stroke="#ffffff" stroke-width="5" stroke-dasharray="1" pathLength="1" style="stroke-dashoffset:1"/>',
      f'<g id="av5" transform="translate(100,740) rotate(4) scale(1.3)">{avion2d}</g>',
      f'<g id="km5" opacity="0"><path d="M1010,740 L1010,800 M996,740 L1024,740 M996,800 L1024,800" stroke="{AMB}" stroke-width="5"/><text x="990" y="716" text-anchor="end" font-family="Inter" font-weight="900" font-size="42" fill="{AMB}">1 km de altura</text></g>',
      f'<rect x="100" y="1300" width="870" height="12" rx="6" fill="#ffffff" opacity="0.15"/><rect id="mar5" x="100" y="1300" width="870" height="12" rx="6" fill="{AMB}"/>']
escena("e5", "".join(e5))
mostrar("e5", f5, F(6))
camara("e5", f5, F(6), (0, 30, 1.0), (0, -10, 1.04))
J(f'tl.to("#km5", {{opacity:1, duration:0.3}}, {P("altura") - 0.3:.2f});')
J(f'tl.to("#glide5", {{strokeDashoffset:0, duration:2.4, ease:"power1.inOut"}}, {P("quince") - 0.6:.2f}); tl.to("#av5", {{x:870, y:60, duration:2.4, ease:"power1.inOut"}}, {P("quince") - 0.6:.2f});')
J(f'tl.fromTo("#mar5", {{scaleX:0}}, {{scaleX:1, transformOrigin:"0 50%", duration:2.4, ease:"power1.inOut", immediateRender:false}}, {P("quince") - 0.6:.2f}); tl.to("#mar5", {{fill:"{RED}", duration:0.5}}, {P("margen") - 0.2:.2f});')
OVR.append(f'<div id="fin5" class="nota" style="left:60px;right:60px;top:1470px;--c:{ICE}"><div class="nt">SEGÚN EL AVIÓN</div><div class="dn">+15 km <small>por cada km de altura</small></div></div>')
pop("#fin5", P("quince") - 0.3, 0.45)
OVR.append(f'<div id="mg5" class="nota" style="left:60px;top:560px;--c:{RED}"><div class="ct" style="color:#fff">TODO SU MARGEN</div></div>')
pop("#mg5", P("margen") - 0.3, 0.35, "opacity:0, x:-30")
fuera("#fin5", F(6) - 0.1); fuera("#mg5", F(6) - 0.1)

# ================================================================== 6) CABINA (3D fuera + panel 2D encima)
f6 = F(6); niebla(f6)
def pantalla(x, y, w, h, cuerpo, rot=""):
    return (f'<g transform="translate({x},{y})"><rect x="-16" y="-16" width="{w + 32}" height="{h + 32}" rx="14" fill="#15181d" stroke="#3a414c" stroke-width="2"/>'
            + "".join(f'<circle cx="{cx}" cy="{cy}" r="4" fill="#4a525e"/>' for cx, cy in ((-6, -6), (w + 6, -6), (-6, h + 6), (w + 6, h + 6)))
            + f'<clipPath id="c{x}{y}"><rect width="{w}" height="{h}" rx="6"/></clipPath><g clip-path="url(#c{x}{y})"><rect width="{w}" height="{h}" fill="#04060a"/>{cuerpo}</g>'
            f'<rect width="{w}" height="{h}" rx="6" fill="url(#vidrioP)"/></g>')
cinta_v = "".join(f'<text x="58" y="{230 - k * 44}" text-anchor="end" font-family="Courier New" font-weight="700" font-size="26" fill="#e6f0ff">{220 + k * 10}</text>' for k in range(-6, 7))
cinta_a = "".join(f'<text x="386" y="{230 - k * 44}" text-anchor="end" font-family="Courier New" font-weight="700" font-size="24" fill="#e6f0ff">{8000 + k * 100}</text>' for k in range(-30, 31))
pfd = (f'<g id="hor6"><rect x="-300" y="-400" width="1040" height="620" fill="url(#pfdCielo)"/><rect x="-300" y="220" width="1040" height="620" fill="url(#pfdTierra)"/><path d="M-300,220 L740,220" stroke="#fff" stroke-width="3"/>'
       + "".join(f'<path d="M{220 - w},{220 - k * 40} L{220 + w},{220 - k * 40}" stroke="#fff" stroke-width="2" opacity="0.8"/>' for k, w in ((1, 30), (2, 55), (3, 30), (-1, 30), (-2, 55))) + '</g>'
       f'<path d="M150,220 L196,220 L196,232 M290,220 L244,220 L244,232" stroke="{AMB}" stroke-width="7" fill="none"/><rect x="214" y="214" width="12" height="12" fill="{AMB}"/>'
       f'<rect x="0" y="0" width="76" height="440" fill="#1b2230" opacity="0.85"/><g id="cv6">{cinta_v}</g><rect x="0" y="204" width="76" height="36" fill="none" stroke="#fff" stroke-width="2"/>'
       f'<path id="bug6" d="M76,206 L92,222 L76,238 Z" fill="#ff4fd8"/>'
       f'<rect x="324" y="0" width="76" height="440" fill="#1b2230" opacity="0.85"/><g id="ca6">{cinta_a}</g><rect x="318" y="204" width="82" height="36" fill="#04060a" stroke="#fff" stroke-width="2"/>')
nd = ("".join(f'<path d="M{220 - r},400 A{r},{r} 0 0 1 {220 + r},400" stroke="#56657c" stroke-width="2" fill="none" stroke-dasharray="6 6"/>' for r in (120, 240, 360))
      + '<path d="M60,90 A230,230 0 0 1 380,90" stroke="#e6f0ff" stroke-width="2" fill="none"/>'
      + "".join(f'<path d="M{220 + 230 * math.sin(math.radians(a)):.0f},{320 - 230 * math.cos(math.radians(a)):.0f} L{220 + 244 * math.sin(math.radians(a)):.0f},{320 - 244 * math.cos(math.radians(a)):.0f}" stroke="#e6f0ff" stroke-width="2"/>' for a in range(-40, 41, 10))
      + f'<path d="M220,400 L220,60" stroke="{GRN}" stroke-width="2" stroke-dasharray="8 6"/><path d="M204,410 L220,372 L236,410 Z" fill="#ffd34a"/>'
      + "".join(f'<g class="apt6"><circle cx="{x}" cy="{y}" r="12" fill="none" stroke="#ff4fd8" stroke-width="4"/><text x="{x + 18}" y="{y + 8}" font-family="Courier New" font-weight="700" font-size="20" fill="#ff4fd8">{n}</text></g>' for x, y, n in ((110, 180, "LPLA"), (330, 130, "LPPD"), (300, 270, "LPHR")))
      + '<text x="16" y="32" font-family="Courier New" font-weight="700" font-size="20" fill="#e6f0ff">GS 230  TAS 240</text>')
ecam = (f'<text x="24" y="46" font-family="Courier New" font-weight="700" font-size="30" fill="{AMB}">MOTOR 1 APAGADO</text><text x="24" y="90" font-family="Courier New" font-weight="700" font-size="30" fill="{AMB}">MOTOR 2 APAGADO</text>'
        f'<text x="24" y="140" font-family="Courier New" font-weight="700" font-size="24" fill="#7fd6ff">- VELOCIDAD DE PLANEO</text><text x="24" y="176" font-family="Courier New" font-weight="700" font-size="24" fill="#7fd6ff">- REENCENDIDO ..........</text>')
e6 = ['<path d="M0,0 L1080,0 L1080,240 L0,240 Z" fill="#14171c"/>',
      '<path d="M0,240 L470,268 L520,860 L0,860 Z M610,860 L560,268 L1080,240 L1080,860 Z" fill="url(#vidrioC)"/>',
      '<path d="M0,0 L1080,0 L1080,240 L560,268 L520,268 L0,240 Z" fill="#191c22"/><path d="M470,268 L520,268 L560,860 L520,860 Z M520,268 L560,268 L610,860 L560,860 Z" fill="#1d2128"/>',
      '<path d="M0,240 L470,268 L520,860" stroke="#2b3038" stroke-width="22" fill="none"/><path d="M1080,240 L560,268 L560,860" stroke="#2b3038" stroke-width="22" fill="none"/>',
      '<path d="M0,860 C300,820 780,820 1080,860 L1080,1000 L0,1000 Z" fill="#20242b"/><path d="M0,862 C300,822 780,822 1080,862" stroke="#3a414c" stroke-width="4" fill="none"/>',
      '<rect x="300" y="890" width="480" height="70" rx="8" fill="#15181d" stroke="#3a414c" stroke-width="2"/>'
      + "".join(f'<text x="{340 + k * 120}" y="937" font-family="Courier New" font-weight="700" font-size="26" fill="#ffb547">{v}</text>' for k, v in enumerate(("SPD", "HDG", "ALT", "V/S"))),
      f'<rect id="mcl6" x="70" y="895" width="170" height="60" rx="8" fill="#3a2a10"/><text x="155" y="934" text-anchor="middle" font-family="Inter" font-weight="900" font-size="22" fill="#1d1408">CAUTION</text>',
      f'<rect id="mwl6" x="840" y="895" width="170" height="60" rx="8" fill="#3a1414"/><text x="925" y="934" text-anchor="middle" font-family="Inter" font-weight="900" font-size="22" fill="#1d0a0a">WARNING</text>',
      '<rect x="0" y="1000" width="1080" height="920" fill="url(#panelG)"/>',
      pantalla(50, 1060, 440, 440, pfd), pantalla(590, 1060, 440, 440, nd), pantalla(240, 1580, 600, 200, ecam)]
escena("e6", "".join(e6))
mostrar("e6", f6, F(7))
J(f'tl.fromTo("#hor6", {{y:0, rotation:0}}, {{y:34, rotation:2.5, svgOrigin:"220 220", duration:{F(7) - f6:.2f}, ease:"sine.inOut", immediateRender:false}}, {f6:.2f});')
J(f'tl.fromTo("#ca6", {{y:0}}, {{y:{44 * 9}, duration:{F(7) - f6:.2f}, ease:"none", immediateRender:false}}, {f6:.2f});')
J(f'tl.fromTo("#cv6", {{y:0}}, {{y:8, duration:0.8, yoyo:true, repeat:{int((F(7) - f6) / 0.8)}, ease:"sine.inOut", immediateRender:false}}, {f6:.2f});')
J(f'tl.to("#mcl6", {{fill:"{AMB}", duration:0.3, yoyo:true, repeat:{int((F(7) - f6) / 0.6)}, ease:"none"}}, {f6:.2f}); tl.to("#mwl6", {{fill:"{RED}", duration:0.3, yoyo:true, repeat:7, ease:"none"}}, {f6 + 0.15:.2f});')
J(f'tl.fromTo("#bug6", {{scale:1}}, {{scale:1.6, svgOrigin:"80 222", duration:0.25, yoyo:true, repeat:3, immediateRender:false}}, {P("velocidad", 2) - 0.1:.2f});')
J(f'tl.fromTo(".apt6", {{opacity:0.25}}, {{opacity:1, duration:0.2, stagger:0.2, immediateRender:false}}, {P("buscar") - 0.1:.2f}); tl.set(".apt6", {{opacity:0.25}}, 0);')
chip("VELOCIDAD DE PLANEO", P("velocidad", 2) - 0.2, F(7) - 0.1, 40, 560, GRN)
OVR.append(f'<div id="may6" class="nota" style="left:40px;top:650px;--c:{RED}"><div class="nt">RADIO</div><div class="rm">MAYDAY MAYDAY</div><div class="rs">emergencia · 7700</div></div>')
pop("#may6", P("llamada") - 0.2, 0.35, "opacity:0, x:-30"); fuera("#may6", F(7) - 0.1)
FX.append(("radio", P("llamada") - 0.2))

# ================================================================== 7) INTENTOS DE ENCENDIDO (3D, el motor por detrás)
OVR.append(f'<div id="re7" class="nota" style="left:60px;top:1380px;width:760px;--c:{AMB}"><div class="nt">REENCENDIDO</div>'
           f'<div class="er" id="r71"><i style="background:{AMB}"></i>INTENTO 1 <span id="r71s">…</span></div><div class="er" id="r72"><i style="background:{AMB}"></i>INTENTO 2 <span id="r72s">…</span></div></div>')
pop("#re7", P("encender") - 0.3, 0.35, "opacity:0, x:-30"); fuera("#re7", F(8) - 0.1)
J(f'tl.set("#r72", {{opacity:0}}, 0); tl.set("#r72", {{opacity:1}}, {K["intento2"] - 0.2:.2f});')
J(f'tl.set("#r71s", {{innerHTML:"SIN RESPUESTA"}}, {P("nada") - 0.1:.2f}); tl.set("#r71s", {{innerHTML:"…"}}, 0); tl.set("#r72s", {{innerHTML:"SIN RESPUESTA"}}, {F(8) - 0.5:.2f}); tl.set("#r72s", {{innerHTML:"…"}}, 0);')
FX.append(("intento", K["intento1"])); FX.append(("intento", K["intento2"]))

# ================================================================== 8) LA RAT (3D)
chip("RAT · TURBINA DE EMERGENCIA", P("rat") - 0.3, F(9) - 0.1, 60, 1380, AMB)
FX.append(("clunk", P("aparece") + 0.05)); FX.append(("helice", P("aparece") + 0.6))

# ================================================================== 9) QUÉ HACE LA RAT (2D, plano técnico)
f9 = F(9)
sil = ('<path d="M540,470 C566,470 580,520 580,580 L580,1430 C580,1470 560,1520 540,1540 C520,1520 500,1470 500,1430 L500,580 C500,520 514,470 540,470 Z" fill="url(#fusT)"/>'
       '<path d="M500,880 L110,1150 L110,1196 L500,1050 Z M580,880 L970,1150 L970,1196 L580,1050 Z" fill="url(#alaT)"/>'
       '<path d="M500,1400 L370,1490 L370,1516 L500,1470 Z M580,1400 L710,1490 L710,1516 L580,1470 Z" fill="url(#alaT)"/>'
       '<rect x="306" y="980" width="46" height="130" rx="20" fill="#9aa8ba"/><rect x="728" y="980" width="46" height="130" rx="20" fill="#9aa8ba"/>'
       '<path d="M528,500 L552,500 L556,520 L524,520 Z" fill="#1a2230"/>')
e9 = ['<rect width="1080" height="1920" fill="url(#cieloAz)"/>', '<rect width="1080" height="1920" fill="url(#rejilla)" opacity="0.35"/>', sil,
      f'<circle cx="610" cy="1090" r="46" fill="{AMB}" opacity="0.25"/><circle cx="610" cy="1090" r="20" fill="{AMB}"/><path id="hel9" d="M610,1058 L610,1122" stroke="#fff" stroke-width="7" stroke-linecap="round"/>',
      f'<path class="en9" d="M610,1090 C640,900 580,700 548,540" stroke="{AMB}" stroke-width="18" opacity="0.25" fill="none"/>',
      f'<path class="en9 en9b" d="M610,1090 C640,900 580,700 548,540" stroke="#ffd690" stroke-width="7" fill="none" stroke-dasharray="20 16"/>',
      f'<g id="no9" opacity="0"><path d="M610,1090 L352,1045 M610,1090 L728,1045" stroke="{RED}" stroke-width="6" stroke-dasharray="12 10"/>'
      f'<path d="M300,1020 L358,1078 M358,1020 L300,1078 M722,1020 L780,1078 M780,1020 L722,1078" stroke="{RED}" stroke-width="12" stroke-linecap="round"/></g>']
escena("e9", "".join(e9))
mostrar("e9", f9, F(10))
camara("e9", f9, F(10), (0, -20, 1.0), (0, 10, 1.05))
J(f'tl.fromTo("#hel9", {{rotation:0}}, {{rotation:{int((F(10) - f9) * 900)}, svgOrigin:"610 1090", duration:{F(10) - f9:.2f}, ease:"none", immediateRender:false}}, {f9:.2f});')
J(f'tl.set(".en9", {{opacity:0}}, 0); tl.to(".en9", {{opacity:1, duration:0.4}}, {P("mantiene") - 0.2:.2f}); tl.fromTo(".en9b", {{strokeDashoffset:0}}, {{strokeDashoffset:-400, duration:{F(10) - f9:.2f}, ease:"none", immediateRender:false}}, {f9:.2f});')
OVR.append(f'<div id="bx9a" class="nota" style="left:620px;top:470px;--c:{AMB}"><div class="ct" style="color:#fff">MANDOS</div></div>')
OVR.append(f'<div id="bx9b" class="nota" style="left:620px;top:560px;--c:{AMB}"><div class="ct" style="color:#fff">PANTALLAS</div></div>')
pop("#bx9a", P("mandos") - 0.2, 0.35, "opacity:0, x:30"); pop("#bx9b", P("pantallas") - 0.2, 0.35, "opacity:0, x:30")
fuera("#bx9a", F(10) - 0.1); fuera("#bx9b", F(10) - 0.1)
J(f'tl.to("#no9", {{opacity:1, duration:0.3}}, {P("arrancar") - 0.3:.2f});')
chip("NO PUEDE ARRANCAR LOS MOTORES", P("arrancar") - 0.3, F(10) - 0.1, 60, 1590, RED)
fuente("Varía según el modelo de avión", P("gira"), F(10) - 0.1)

# ================================================================== 10) DESCENSO ENTRE NUBES (3D)
chip("SIN SEGUNDA OPORTUNIDAD", P("oportunidad") - 0.3, F(11) - 0.1, 60, 1380, RED)

# ================================================================== 11) PISTA, CAMPO O AGUA (3D, mapa)
f11 = F(11); niebla(f11)
for k, (txt, wd, pos, col) in enumerate((("PISTA", "pista", (-700, 0, -1500), GRN), ("CAMPO", "campo", (-300, 0, 1600), AMB), ("AGUA", "agua", (2100, 0, 200), ICE))):
    OVR.append(f'<div class="marca3d" id="mk{k}" data-p="{pos[0]},{pos[1]},{pos[2]}" style="--c:{col}"><i></i><span>{txt}</span></div>')
    J(f'tl.set("#mk{k}", {{opacity:0}}, 0); tl.fromTo("#mk{k}", {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.35, ease:"back.out(2)", immediateRender:false}}, {P(wd) - 0.15:.2f}); tl.set("#mk{k}", {{opacity:0}}, {F(12):.2f});')

# ================================================================== 12) ATERRIZAJE (3D)
chip("EL TREN CAE POR SU PROPIO PESO", P("tren") - 0.3, F(13) - 0.1, 60, 1380, ICE)
FX.append(("toma", K["toca"]))
# ================================================================== 13) CIERRE EN BUCLE (3D)
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
.nota{{position:absolute;z-index:32;padding:14px 22px 16px;border-radius:12px;color:#fff;background:linear-gradient(135deg, rgba(14,20,34,0.58), rgba(14,20,34,0.32));backdrop-filter:blur(16px) saturate(1.5);-webkit-backdrop-filter:blur(16px) saturate(1.5);border:1px solid rgba(255,255,255,0.35);border-left:6px solid var(--c);box-shadow:0 10px 40px rgba(0,0,0,0.22);text-shadow:0 2px 10px rgba(0,0,0,0.35)}}
.nota .nt{{font:800 22px Inter;letter-spacing:5px;color:rgba(255,255,255,0.75);margin-bottom:4px}} .nota .ct{{font:900 40px Inter;letter-spacing:2px;color:var(--c)}}
.nota .dn{{font:900 96px Inter;letter-spacing:-3px;line-height:1.02}} .nota .dn small{{font:800 32px Inter;letter-spacing:0;opacity:0.85}}
.nota .rm{{font:900 40px "Courier New", monospace;margin-top:4px}} .nota .rs{{font:700 24px Inter;opacity:0.8;margin-top:2px}}
.er{{display:flex;align-items:center;gap:14px;font:800 38px "Courier New", monospace;color:#fff;padding:4px 0}} .er span{{color:var(--c);margin-left:auto}} .er i{{width:16px;height:16px;border-radius:50%;background:{RED};box-shadow:0 0 16px {RED}}}
#hud{{left:60px;top:470px;width:300px}} #hud .hn{{font:900 64px Inter;line-height:1;letter-spacing:-2px;font-variant-numeric:tabular-nums}} #hud .hn small{{font:800 30px Inter;opacity:0.7}} #hud .hs{{margin-top:6px;font:800 20px Inter;letter-spacing:4px;color:#ffb0aa}}
#alarma{{position:absolute;inset:0;z-index:54;pointer-events:none;background:radial-gradient(90% 70% at 50% 50%, rgba(255,40,30,0) 50%, rgba(255,40,30,0.55))}}
#e6{{background:transparent}}
#gancho{{position:absolute;left:0;right:0;top:640px;text-align:center;z-index:20;color:#fff;text-shadow:0 6px 30px rgba(0,0,0,0.55)}}
#gancho .g0{{font:800 54px Inter;letter-spacing:6px;color:#e6edf6}} #gancho .g1{{font:900 190px Inter;letter-spacing:-8px;line-height:0.95}} #gancho .g2{{font:800 54px Inter;letter-spacing:8px;color:#e6edf6}}
#ecam{{left:60px;top:1330px;width:520px;padding:18px 24px;border-left:6px solid {RED}}}
#ecam .et{{font:800 22px Inter;letter-spacing:5px;color:{MUTED};margin-bottom:6px}}
.er{{display:flex;align-items:center;gap:14px;font:800 40px "Courier New", monospace;color:#fff;padding:6px 0}} .er span{{color:{RED};margin-left:auto}} .er i{{width:18px;height:18px;border-radius:50%;background:{RED};box-shadow:0 0 18px {RED}}}
#cuenta{{left:60px;top:1560px;padding:14px 22px;border-left:6px solid {AMB}}} #cuenta .ct{{font:900 40px Inter;letter-spacing:2px;color:{AMB}}}
#hud{{position:absolute;left:60px;top:470px;width:300px;padding:12px 18px 14px;border-left:5px solid {ICE};background:rgba(7,12,22,0.62);z-index:40;color:{INK}}}
#hud .hl{{font:800 22px Inter;letter-spacing:6px;color:{MUTED}}} #hud .hn{{font:900 64px Inter;line-height:1;letter-spacing:-2px;font-variant-numeric:tabular-nums}} #hud .hn small{{font:800 30px Inter;color:{MUTED}}}
#hud .hs{{margin-top:6px;font:800 20px Inter;letter-spacing:4px;color:{RED}}}
.chip{{position:absolute;z-index:35;display:flex;align-items:center;gap:14px;padding:13px 22px;border-radius:12px;font:800 30px Inter;letter-spacing:1px;color:#fff;background:linear-gradient(135deg, rgba(14,20,34,0.58), rgba(14,20,34,0.32));backdrop-filter:blur(16px) saturate(1.5);-webkit-backdrop-filter:blur(16px) saturate(1.5);border:1px solid rgba(255,255,255,0.35);box-shadow:0 10px 40px rgba(0,0,0,0.2);text-shadow:0 2px 10px rgba(0,0,0,0.35)}}
.chip b{{width:14px;height:14px;border-radius:50%;box-shadow:0 0 12px currentColor}}
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
.marca3d{{position:absolute;left:0;top:0;z-index:30;display:flex;align-items:center;gap:14px;font:900 32px Inter;letter-spacing:3px;color:#fff;white-space:nowrap;text-shadow:0 2px 10px rgba(0,0,0,0.5)}}
.marca3d i{{display:block;width:64px;height:64px;border-radius:50%;border:5px solid var(--c);margin-left:-32px;box-shadow:0 0 0 8px rgba(255,255,255,0.12), 0 0 30px var(--c)}}
.marca3d span{{padding:8px 16px;border-radius:10px;background:linear-gradient(135deg, rgba(255,255,255,0.22), rgba(255,255,255,0.08));backdrop-filter:blur(14px);border:1px solid rgba(255,255,255,0.35);border-left:6px solid var(--c)}}
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
    <linearGradient id="cieloOc" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b2f5a"/><stop offset="0.55" stop-color="#c46a52"/><stop offset="0.72" stop-color="#f0a46c"/><stop offset="1" stop-color="#f6c79e"/></linearGradient>
    <linearGradient id="cieloAz" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d1a33"/><stop offset="1" stop-color="#22385e"/></linearGradient>
    <linearGradient id="fusG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#b8c2ce"/></linearGradient>
    <linearGradient id="fusT" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9fb0c4"/><stop offset="0.5" stop-color="#f2f6fa"/><stop offset="1" stop-color="#9fb0c4"/></linearGradient>
    <linearGradient id="alaT" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e6edf5"/><stop offset="1" stop-color="#a9b8ca"/></linearGradient>
    <linearGradient id="vidrioP" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0.10"/><stop offset="0.4" stop-color="#ffffff" stop-opacity="0"/></linearGradient>
    <linearGradient id="vidrioC" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0.08"/><stop offset="0.5" stop-color="#ffffff" stop-opacity="0"/><stop offset="1" stop-color="#ffffff" stop-opacity="0.05"/></linearGradient>
    <linearGradient id="pfdCielo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1f5fb0"/><stop offset="1" stop-color="#4c93e0"/></linearGradient>
    <linearGradient id="pfdTierra" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9a5a2a"/><stop offset="1" stop-color="#5a3216"/></linearGradient>
    <linearGradient id="panelG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2e333b"/><stop offset="1" stop-color="#181b20"/></linearGradient>
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

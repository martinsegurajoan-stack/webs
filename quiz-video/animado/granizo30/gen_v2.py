#!/usr/bin/env python3
"""«¿Y si granizara 30 días seguidos?» v2 — estilo DOCUMENTAL / informe meteorológico (serio, adulto).
Sin personaje, granizo realista en 3 capas de profundidad, diagramas técnicos limpios, mapa real de España, panel de
salidas, gráfica de precios, contador «DÍA NN/30» fijo, un movimiento de cámara por plano, cortes secos y solo 3
transiciones (cortina de granizo) en los cambios de bloque. Misma voz (tiempos.json).
  python3 gen.py → index.html + efectos.json
"""
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
tl, FX = [], []
def J(s): tl.append(s)
NID = [0]
def nid(p="e"):
    NID[0] += 1
    return f"{p}{NID[0]}"

BG, INK, MUTED = "#070c16", "#e9f1fb", "#8796ad"
ICE, ICE2, AMB, RED, GRN = "#9fdcff", "#d9f2ff", "#ffb547", "#ff5a52", "#4cd18a"

def pop(sel, t, d=0.45, frm="opacity:0, y:24", ease="power3.out"):
    J(f'tl.set("{sel}", {{opacity:0}}, 0);')
    J(f'tl.fromTo("{sel}", {{{frm}}}, {{opacity:1, x:0, y:0, scale:1, duration:{d}, ease:"{ease}", immediateRender:false}}, {t:.2f});')
def fuera(sel, t, d=0.3):
    J(f'tl.to("{sel}", {{opacity:0, duration:{d}, ease:"power2.in"}}, {t:.2f});')

ESC = []
def escena(eid, cuerpo, w=1080):
    ESC.append(f'<div class="esc" id="{eid}"><div class="cam" id="{eid}-cam"><svg width="{w}" height="1920" viewBox="0 0 {w} 1920" style="position:absolute;left:0;top:0;overflow:visible">{cuerpo}</svg></div></div>')
def mostrar(eid, t0, t1):
    J(f'tl.set("#{eid}", {{opacity:0}}, 0); tl.set("#{eid}", {{opacity:1}}, {t0:.2f}); tl.set("#{eid}", {{opacity:0}}, {t1:.2f});')
def camara(eid, t0, t1, desde, hasta, ease="sine.inOut"):
    x0, y0, s0 = desde; x1, y1, s1 = hasta
    J(f'tl.fromTo("#{eid}-cam", {{x:{x0}, y:{y0}, scale:{s0}}}, {{x:{x1}, y:{y1}, scale:{s1}, duration:{t1 - t0:.2f}, ease:"{ease}", immediateRender:false}}, {t0:.2f});')
def barrido(t):
    J(f'tl.fromTo("#cortina", {{y:-2400}}, {{y:1920, duration:0.6, ease:"power2.inOut", immediateRender:false}}, {t - 0.3:.2f});')
    FX.append(("whoosh", t - 0.3))

# ------------------------------------------------------------------ granizo realista
def piedra(x, y, r, streak=True, op=1.0):
    s = (f'<path d="M{x - r * 0.15:.1f},{y - r * 7:.1f} L{x},{y}" stroke="url(#estela)" stroke-width="{r * 1.1:.1f}" stroke-linecap="round" opacity="{0.55 * op:.2f}"/>' if streak else "")
    return s + (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="url(#hielo)" opacity="{op:.2f}"/>'
                f'<circle cx="{x - r * 0.35:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.28:.1f}" fill="#ffffff" opacity="{0.9 * op:.2f}"/>')
def capa_granizo(gid, n, rmin, rmax, op, seed, w=1080, h=1920):
    rr = random.Random(seed)
    cuerpo = "".join(piedra(rr.uniform(-60, w + 60), rr.uniform(0, h), rr.uniform(rmin, rmax), True, op) for _ in range(n))
    return f'<g class="gcapa" id="{gid}"><g class="gmov">{cuerpo}<g transform="translate(0,-{h})">{cuerpo}</g></g></g>'
def granizo(pref, seed=1, densidad=1.0):
    return (capa_granizo(f"{pref}a", int(70 * densidad), 2.5, 4.5, 0.45, seed)
            + capa_granizo(f"{pref}b", int(45 * densidad), 5, 8, 0.75, seed + 1)
            + capa_granizo(f"{pref}c", int(14 * densidad), 10, 15, 1.0, seed + 2))
def caer(pref, t0, t1):
    for suf, vel, dx in (("a", 1.6, 30), ("b", 1.0, 50), ("c", 0.65, 80)):
        n = max(1, int((t1 - t0) / vel) + 1)
        J(f'tl.fromTo("#{pref}{suf} .gmov", {{y:0, x:0}}, {{y:1920, x:{-dx}, duration:{vel}, repeat:{n}, ease:"none", immediateRender:false}}, {t0:.2f});')
    tt = t0
    while tt < t1 - 0.6:
        FX.append(("granizo", tt)); tt += 2.3

# ------------------------------------------------------------------ ciudad en silueta con volumen y luz
def ciudad(seed, y_suelo=1500, luces=0.35, tono="#111b2e", tono2="#0b1322", nieve=False, altura=1.0):
    rr = random.Random(seed)
    s = []
    x = -40
    while x < 1120:
        w, h = rr.randint(90, 170), rr.randint(380, 760) * altura
        s.append(f'<rect x="{x}" y="{y_suelo - h:.0f}" width="{w}" height="{h:.0f}" fill="{tono2}"/>')
        x += w + rr.randint(0, 12)
    x = -60
    while x < 1140:
        w, h = rr.randint(150, 260), rr.randint(520, 980) * altura
        y0 = y_suelo - h
        s.append(f'<rect x="{x}" y="{y0:.0f}" width="{w}" height="{h:.0f}" fill="{tono}"/>'
                 f'<rect x="{x + w - 18}" y="{y0:.0f}" width="18" height="{h:.0f}" fill="#000" opacity="0.25"/>'
                 f'<rect x="{x - 4}" y="{y0 - 10:.0f}" width="{w + 8}" height="12" fill="#1c2a44"/>')
        if nieve:
            s.append(f'<rect x="{x - 4}" y="{y0 - 22:.0f}" width="{w + 8}" height="14" rx="6" fill="{ICE2}" opacity="0.9"/>')
        cols, filas = max(2, w // 48), int((h - 60) // 64)
        for i in range(cols):
            for j in range(filas):
                if rr.random() < luces:
                    wx, wy = x + 16 + i * ((w - 30) / cols), y0 + 30 + j * 64
                    c = rr.choice(("#ffcf7a", "#ffd99a", "#f6b75a", "#cfe6ff"))
                    s.append(f'<rect x="{wx:.0f}" y="{wy:.0f}" width="22" height="30" fill="{c}" opacity="{rr.uniform(0.55, 0.95):.2f}"/>')
        if rr.random() < 0.5:
            s.append(f'<path d="M{x + w * 0.3:.0f},{y0 - 10:.0f} l0,-60 M{x + w * 0.3 - 14:.0f},{y0 - 50:.0f} l28,0" stroke="#1c2a44" stroke-width="5"/>')
        x += w + rr.randint(6, 24)
    return "".join(s)
def calle(y=1500, mojada=True, blanca=False):
    s = [f'<rect x="0" y="{y}" width="1080" height="{1920 - y}" fill="url(#asfalto)"/>', f'<rect x="0" y="{y}" width="1080" height="34" fill="#1d2738"/>']
    if mojada:
        s.append(f'<rect x="0" y="{y + 34}" width="1080" height="{1920 - y - 34}" fill="url(#reflejo)" opacity="0.5"/>')
    if blanca:
        s.append(f'<rect id="mantoB" x="0" y="{y - 6}" width="1080" height="{1926 - y}" fill="url(#mantoG)" opacity="0"/>')
    return "".join(s)
def coche_sil(cid, x, y, s=1.0, col="#2a3550"):
    return (f'<g id="{cid}" transform="translate({x},{y}) scale({s})"><ellipse cx="170" cy="128" rx="180" ry="12" fill="#000" opacity="0.45"/>'
            f'<path d="M8,108 L8,72 Q12,50 48,46 L96,40 L140,4 L238,4 L290,42 L318,50 Q338,56 338,82 L338,108 Z" fill="{col}"/>'
            f'<path d="M150,14 L230,14 L268,44 L112,44 Z" fill="#1a2a44"/><path d="M150,14 L190,14 L170,44 L112,44 Z" fill="#ffffff" opacity="0.08"/>'
            f'<circle cx="84" cy="110" r="28" fill="#06090f"/><circle cx="262" cy="110" r="28" fill="#06090f"/>'
            f'<rect x="306" y="62" width="26" height="12" rx="4" fill="#ffe3a0"/><rect x="10" y="66" width="18" height="12" rx="4" fill="#ff5a52"/></g>')

# ------------------------------------------------------------------ HUD fijo y rótulos
OVR = []
OVR.append('<div id="hud"><div class="hl">DÍA</div><div class="hn" id="hudn">01</div><div class="hd">/ 30</div><div class="hbar"><i id="hudb"></i></div></div>')
J('tl.set("#hud", {opacity:0}, 0);')
def dia(t, n):
    J(f'tl.set("#hudn", {{innerHTML:"{n:02d}"}}, {t:.2f}); tl.to("#hudb", {{scaleX:{n / 30:.3f}, duration:0.6, ease:"power3.out"}}, {t:.2f});')
    J(f'tl.fromTo("#hudn", {{y:-20, opacity:0}}, {{y:0, opacity:1, duration:0.35, ease:"power3.out", immediateRender:false}}, {t:.2f});')
    FX.append(("tic", t))
def chip(txt, t, t_out, x, y, color=ICE):
    i = nid("ch")
    OVR.append(f'<div class="chip" id="{i}" style="left:{x}px;top:{y}px;border-color:{color}"><b style="background:{color}"></b>{txt}</div>')
    pop(f"#{i}", t, 0.4, "opacity:0, x:-30")
    fuera(f"#{i}", t_out)
def fuente(txt, t, t_out):
    i = nid("fu")
    OVR.append(f'<div class="fuente" id="{i}">{txt}</div>')
    pop(f"#{i}", t, 0.4, "opacity:0")
    fuera(f"#{i}", t_out)
def rueda(i, valor, size, col):
    h = [f'<span class="rueda" id="{i}" style="font-size:{size}px;color:{col}">']
    k = 0
    for ch in valor:
        if ch.isdigit():
            strip = "".join(f"<span>{d}</span>" for d in list(range(10)) * 2)
            h.append(f'<span class="dg"><span class="st" id="{i}-{k}">{strip}</span></span>'); k += 1
        else:
            h.append(f'<span class="sep">{ch}</span>')
    return "".join(h) + '</span>'
def gira(i, valor, t, d=1.0):
    k, n = 0, sum(c.isdigit() for c in valor)
    for ch in valor:
        if ch.isdigit():
            J(f'tl.fromTo("#{i}-{k}", {{y:"0em"}}, {{y:"-{10 + int(ch)}em", duration:{d + 0.08 * (n - k):.2f}, ease:"power4.out", immediateRender:false}}, {t:.2f});')
            k += 1
    J(f'tl.set("#{i}", {{opacity:0}}, 0); tl.set("#{i}", {{opacity:1}}, {t:.2f});')

# ================================================================== 1) GANCHO: tormenta de noche
f1e = FE(1)
e1 = ['<rect width="1080" height="1920" fill="url(#cieloNoche)"/>',
      '<g>' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="url(#nubeG)" opacity="{o}"/>' for x, y, rx, ry, o in
                       ((180, 260, 420, 170, 0.9), (760, 220, 480, 190, 0.95), (520, 420, 520, 160, 0.85), (980, 470, 300, 120, 0.8), (80, 520, 280, 110, 0.8))) + '</g>',
      '<rect id="relamp1" width="1080" height="1920" fill="#cfe2ff" opacity="0"/>',
      ciudad(3, 1500, 0.4), calle(1500, True, True), coche_sil("car1", 640, 1420, 1.05), granizo("g1", 1, 1.3)]
escena("e1", "".join(e1))
mostrar("e1", 0, F(2))
camara("e1", 0, F(2), (0, 60, 1.18), (0, 0, 1.04), "power2.out")
caer("g1", 0, F(2))
J('tl.to("#relamp1", {opacity:0.45, duration:0.05, yoyo:true, repeat:1}, 1.6); tl.to("#relamp1", {opacity:0.25, duration:0.05, yoyo:true, repeat:1}, 1.85);')
FX.append(("trueno", 1.55))
J(f'tl.to("#mantoB", {{opacity:0.85, duration:{f1e:.2f}}}, 0.3);')
OVR.append('<svg id="pg" width="300" height="300" viewBox="-150 -150 300 300" style="position:absolute;left:560px;top:-320px;overflow:visible;z-index:9">'
           '<path d="M-20,-900 L0,0" stroke="url(#estela)" stroke-width="90" stroke-linecap="round" opacity="0.35"/>'
           '<circle r="110" fill="url(#hielo)"/><circle r="80" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.25"/><circle r="52" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.2"/>'
           '<ellipse cx="-38" cy="-42" rx="30" ry="22" fill="#ffffff" opacity="0.9"/></svg>')
J(f'tl.fromTo("#pg", {{y:0, rotation:0}}, {{y:2400, rotation:40, duration:{f1e + 0.3:.2f}, ease:"power1.in", immediateRender:false}}, 0); tl.set("#pg", {{opacity:0}}, {F(2):.2f});')
OVR.append('<div id="titulo"><div class="t0">¿Y SI GRANIZARA</div><div class="t1"><span>30</span> DÍAS SEGUIDOS?</div></div>')
J('tl.fromTo("#titulo .t0", {y:16}, {y:0, duration:0.35, ease:"power3.out", immediateRender:false}, 0);')
J('tl.fromTo("#titulo .t1", {y:16}, {y:0, duration:0.35, ease:"power3.out", immediateRender:false}, 0.08);')
J(f'tl.to("#titulo", {{opacity:0, y:-40, duration:0.35, ease:"power2.in"}}, {F(2) - 0.4:.2f});')

# ================================================================== 2) LA NUBE POR DENTRO: diagrama técnico
f2 = F(2); barrido(f2)
cb_cloud = ('<path d="M220,1160 C180,1080 220,980 300,960 C300,860 380,780 470,800 C500,640 640,600 700,720 C800,700 860,800 840,880 C930,900 960,1000 900,1080 C940,1120 900,1170 860,1160 Z" fill="url(#nubeTec)"/>'
            '<path d="M330,700 C430,560 650,540 900,620 C760,600 620,620 560,700 Z" fill="url(#nubeTec)" opacity="0.9"/>'
            '<path d="M220,1160 L860,1160" stroke="#9fb3cf" stroke-width="3" stroke-dasharray="10 10" opacity="0.6"/>')
lazo = "M520,1150 C620,1000 640,820 560,760 C470,700 450,900 540,960 C630,1020 640,860 570,820 C500,790 500,940 560,1170"
e2 = ['<rect width="1080" height="1920" fill="url(#fondoTec)"/>', '<rect width="1080" height="1920" fill="url(#rejilla)" opacity="0.5"/>', cb_cloud,
      '<path d="M0,1340 L1080,1340" stroke="#1e2c45" stroke-width="2"/>'
      '<g font-family="Inter" font-size="26" font-weight="700" fill="#8796ad"><text x="40" y="1346">0 km</text><text x="40" y="1012">6 km</text><text x="40" y="682">12 km</text></g>'
      '<path d="M150,1340 L150,640" stroke="#33445f" stroke-width="3"/>' + "".join(f'<path d="M146,{y} L158,{y}" stroke="#33445f" stroke-width="3"/>' for y in (1340, 1170, 1006, 840, 676)),
      '<g>' + "".join(f'<path class="up" d="M{x},1320 C{x - 20},1200 {x + 20},1080 {x},960" stroke="{AMB}" stroke-width="10" fill="none" stroke-linecap="round" stroke-dasharray="40 30" opacity="0.85"/>' for x in (420, 520, 620)) + '</g>',
      f'<path id="lazo2" d="{lazo}" stroke="{ICE}" stroke-width="4" fill="none" stroke-dasharray="1" pathLength="1" style="stroke-dashoffset:1" opacity="0.8"/>',
      '<g id="pl2">' + piedra(0, 0, 14, False) + '</g>',
      '<g id="corte2" opacity="0"><circle cx="820" cy="1470" r="170" fill="#0b1626" stroke="#2b4466" stroke-width="3"/>'
      + "".join(f'<circle class="capa2" cx="820" cy="1470" r="{r}" fill="{c}" opacity="0.9"/>' for r, c in ((150, "#e9f6ff"), (124, "#b9dcf2"), (98, "#e9f6ff"), (72, "#b9dcf2"), (46, "#e9f6ff"), (22, "#cfe8f8")))
      + '<text x="820" y="1680" text-anchor="middle" font-family="Inter" font-weight="800" font-size="30" fill="#c9d8ea">CAPAS DE HIELO</text></g>']
escena("e2", "".join(e2))
mostrar("e2", f2, F(3))
camara("e2", f2, F(3), (0, 120, 1.0), (0, -40, 1.08))
J(f'tl.to("#lazo2", {{strokeDashoffset:0, duration:{FE(2) - f2 - 1.2:.2f}, ease:"none"}}, {f2 + 0.4:.2f});')
pts = [(520, 1150), (610, 1000), (630, 860), (560, 760), (470, 780), (470, 900), (540, 960), (630, 940), (610, 840), (530, 820), (510, 940), (560, 1170)]
seg = (FE(2) - f2 - 1.2) / (len(pts) - 1)
J(f'tl.set("#pl2", {{x:{pts[0][0]}, y:{pts[0][1]}, scale:0.6}}, 0);')
for k, (x, y) in enumerate(pts[1:]):
    J(f'tl.to("#pl2", {{x:{x}, y:{y}, scale:{0.6 + 0.08 * k:.2f}, duration:{seg:.2f}, ease:"sine.inOut"}}, {f2 + 0.4 + k * seg:.2f});')
J(f'tl.fromTo(".up", {{strokeDashoffset:0}}, {{strokeDashoffset:-140, duration:{F(3) - f2:.2f}, ease:"none", immediateRender:false}}, {f2:.2f});')
chip("DURACIÓN HABITUAL: UNOS MINUTOS", P("minutos") - 0.3, F(3) - 0.1, 200, 500, ICE)
chip("CORRIENTE ASCENDENTE", P("sube") - 0.2, F(3) - 0.1, 200, 584, AMB)
pop("#corte2", P("capas") - 0.2, 0.5, "opacity:0, scale:0.8")
J(f'tl.fromTo(".capa2", {{scale:0}}, {{scale:1, svgOrigin:"820 1470", duration:0.45, stagger:0.12, ease:"power3.out", immediateRender:false}}, {P("capas"):.2f});')
fuente("Fuente: NOAA · Servicio Meteorológico de EE. UU.", P("capas"), F(3) - 0.1)

# ================================================================== 3) DÍA 1: la ciudad amanece blanca + capó abollado
f3 = F(3); barrido(f3)
J(f'tl.to("#hud", {{opacity:1, duration:0.4}}, {f3 + 0.2:.2f});'); dia(f3 + 0.25, 1)
e3 = ['<rect width="1080" height="1920" fill="url(#cieloAlba)"/>',
      '<g>' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="url(#nubeG)" opacity="0.85"/>' for x, y, rx, ry in ((200, 300, 420, 140), (820, 260, 460, 160))) + '</g>',
      ciudad(7, 1380, 0.25, "#26324a", "#1b263a", True),
      '<rect x="0" y="1380" width="1080" height="540" fill="url(#mantoG)"/>', "".join(piedra(random.Random(k).uniform(0, 1080), 1390 + random.Random(k + 99).uniform(0, 520) ** 1.0, random.Random(k + 7).uniform(4, 11), False, 0.9) for k in range(120)),
      '<g>' + "".join(f'<circle class="onda3" cx="{x}" cy="{y}" r="10" fill="none" stroke="#ffffff" stroke-width="3"/>' for x, y in ((140, 820), (420, 700), (700, 760), (960, 720), (300, 900), (860, 880))) + '</g>',
      granizo("g3", 3, 0.8)]
escena("e3", "".join(e3))
tc = P("coches")
mostrar("e3", f3, tc - 0.05)
camara("e3", f3, tc, (-40, 0, 1.06), (40, 0, 1.06))
caer("g3", f3, tc)
J(f'tl.fromTo(".onda3", {{attr:{{r:6}}, opacity:0.9}}, {{attr:{{r:70}}, opacity:0, duration:0.6, stagger:0.17, repeat:{max(1, int((tc - P("tejados")) / 1.0))}, ease:"power1.out", immediateRender:false}}, {P("tejados") - 0.2:.2f}); tl.set(".onda3", {{opacity:0}}, 0);')
OVR.append('<div id="db3" class="panel"><div class="pt">RUIDO SOBRE LOS TEJADOS</div><div class="barras">' + "".join(f'<i class="bd" style="height:{h}px"></i>' for h in (30, 50, 70, 90, 110, 130, 150, 170, 190, 210)) + '</div><div class="pv">golpes continuos, como una percusión</div></div>')
pop("#db3", P("tejados"), 0.45)
J(f'tl.fromTo("#db3 .bd", {{scaleY:0.1}}, {{scaleY:1, transformOrigin:"50% 100%", duration:0.18, stagger:0.04, yoyo:true, repeat:{max(1, int((tc - P("tejados")) / 0.5))}, ease:"power1.inOut", immediateRender:false}}, {P("tejados"):.2f});')
fuera("#db3", tc - 0.15)
e3b = ['<rect width="1080" height="1920" fill="url(#capo)"/>', '<path d="M0,620 C360,560 720,560 1080,620" stroke="#ffffff" stroke-width="40" opacity="0.06" fill="none"/>']
rr = random.Random(9)
for k in range(26):
    x, y, r = rr.randint(80, 1000), rr.randint(620, 1600), rr.randint(14, 34)
    e3b.append(f'<g class="abol" opacity="0"><ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 0.7:.0f}" fill="url(#abolG)"/><ellipse cx="{x - r * 0.3:.0f}" cy="{y - r * 0.25:.0f}" rx="{r * 0.35:.0f}" ry="{r * 0.18:.0f}" fill="#ffffff" opacity="0.35"/></g>')
e3b.append(granizo("g3b", 13, 0.6))
escena("e3b", "".join(e3b))
mostrar("e3b", tc - 0.05, F(4))
camara("e3b", tc - 0.05, F(4), (0, 0, 1.12), (0, -30, 1.0), "power2.out")
caer("g3b", tc, F(4))
J(f'tl.to("#e3b .abol", {{opacity:1, duration:0.12, stagger:0.09}}, {tc + 0.1:.2f});')
for k in range(5):
    FX.append(("clic", tc + 0.2 + k * 0.45))
chip("COCHES APARCADOS: ABOLLADURAS", P("abolladuras") - 0.4, F(4) - 0.1, 60, 640, AMB)

# ================================================================== 4) DÍA 3: el campo + mapa de España
f4 = F(4); dia(f4 + 0.1, 3)
t25 = P("2025")
filas = []
for j in range(18):
    y = 980 + j * 52
    esc = 0.35 + j * 0.06
    for i in range(int(1080 / (70 * esc)) + 2):
        x = (i * 70 * esc) + (j % 2) * 35 * esc - 20
        filas.append(f'<g class="pl4" transform="translate({x:.0f},{y}) scale({esc:.2f})"><g class="pl4r"><path d="M0,0 C-6,-40 -24,-60 -30,-80 M0,0 C4,-46 18,-66 26,-90 M0,0 L0,-100" stroke="#4a8f4e" stroke-width="6" fill="none" stroke-linecap="round"/></g></g>')
e4 = ['<rect width="1080" height="1920" fill="url(#cieloGris)"/>',
      '<path d="M0,960 C300,930 760,940 1080,920 L1080,1920 L0,1920 Z" fill="#33502f"/>',
      '<path d="M0,960 C300,930 760,940 1080,920 L1080,1000 L0,1040 Z" fill="#46663f"/>', "".join(filas), granizo("g4", 4, 0.9)]
escena("e4", "".join(e4))
mostrar("e4", f4, t25 - 0.05)
camara("e4", f4, t25, (0, -60, 1.0), (0, 40, 1.12))
caer("g4", f4, t25)
J(f'tl.to("#e4 .pl4r", {{rotation:70, transformOrigin:"0 0", duration:1.4, stagger:0.002, ease:"power2.in"}}, {P("perdido") - 0.6:.2f});')
J(f'tl.to("#e4 .pl4r path", {{stroke:"#8a7a44", duration:1.2}}, {P("perdido") - 0.4:.2f});')
FX.append(("baja", P("perdido") - 0.2))
m = json.load(open(os.path.join(BASE, "..", "vox29n", "espana.json")))
dan = {"castile-and-leon": 0.9, "aragon": 0.8, "castile-la-mancha": 0.85, "navarre": 0.7, "la-rioja": 0.9, "catalonia": 0.6, "valencia": 0.5, "extremadura": 0.5, "murcia": 0.4, "andalusia": 0.45}
regs = "".join(f'<path d="{l["path"]}" fill="#1a2840" stroke="#3a5070" stroke-width="1.4"/>'
               + (f'<path class="dz" d="{l["path"]}" fill="{AMB if dan[l["id"]] < 0.7 else RED}" opacity="0" data-o="{dan[l["id"]] * 0.75:.2f}"/>' if l["id"] in dan else "")
               for l in m["locations"] if l["id"] != "canary-islands")
e4b = ['<rect width="1080" height="1920" fill="url(#fondoTec)"/>', '<rect width="1080" height="1920" fill="url(#rejilla)" opacity="0.4"/>',
       f'<svg x="40" y="560" width="1000" height="887" viewBox="0 0 613 544">{regs}</svg>']
escena("e4b", "".join(e4b))
mostrar("e4b", t25 - 0.05, F(5))
camara("e4b", t25 - 0.05, F(5), (0, 30, 1.0), (0, 0, 1.06))
J(f'tl.to("#e4b .dz", {{opacity:(i, el) => +el.getAttribute("data-o"), duration:0.5, stagger:0.12, ease:"power2.out"}}, {P("danaron") - 0.1:.2f});')
OVR.append(f'<div id="ha4" class="dato"><div class="dn">{rueda("ha4n", "1.000.000", 120, INK)}</div><div class="dt">HECTÁREAS DE CULTIVO DAÑADAS</div><div class="ds">Tormentas en España · 2025</div></div>')
pop("#ha4", P("millon") - 0.5, 0.45)
gira("ha4n", "1.000.000", P("millon") - 0.4, 1.1)
for k in range(6):
    FX.append(("clic", P("millon") - 0.4 + k * 0.16))
fuera("#ha4", F(5) - 0.1)
fuente("Fuente: Agroseguro (2025) · zonas ilustrativas", P("hectareas"), F(5) - 0.1)

# ================================================================== 5) PRECIOS: gráfica + tabla
f5 = F(5)
e5 = ['<rect width="1080" height="1920" fill="url(#fondoTec)"/>', '<rect width="1080" height="1920" fill="url(#rejilla)" opacity="0.4"/>',
      '<path d="M120,1100 L960,1100 M120,1100 L120,600" stroke="#33445f" stroke-width="3"/>',
      f'<path id="curva5" d="M120,1040 C260,1036 380,1030 480,1010 C600,980 700,860 780,760 C840,690 900,640 960,610" stroke="{RED}" stroke-width="9" fill="none" stroke-linecap="round" pathLength="1" stroke-dasharray="1" style="stroke-dashoffset:1"/>',
      f'<path id="area5" d="M120,1040 C260,1036 380,1030 480,1010 C600,980 700,860 780,760 C840,690 900,640 960,610 L960,1100 L120,1100 Z" fill="url(#areaRoja)" opacity="0"/>',
      '<text x="120" y="1150" font-family="Inter" font-weight="700" font-size="26" fill="#8796ad">DÍA 1</text><text x="960" y="1150" text-anchor="end" font-family="Inter" font-weight="700" font-size="26" fill="#8796ad">DÍA 7</text>'
      '<text x="960" y="580" text-anchor="end" font-family="Inter" font-weight="800" font-size="28" fill="#c9d8ea">PRECIO DE FRUTA Y VERDURA</text>']
escena("e5", "".join(e5))
mostrar("e5", f5, F(6))
camara("e5", f5, F(6), (0, 0, 1.0), (-20, 0, 1.05))
J(f'tl.to("#curva5", {{strokeDashoffset:0, duration:2.2, ease:"power2.in"}}, {f5 + 0.3:.2f}); tl.to("#area5", {{opacity:0.5, duration:1.0}}, {f5 + 1.2:.2f});')
filas5 = (("Fruta", "1,80 €", "3,40 €"), ("Verdura", "1,20 €", "2,60 €"), ("Hortalizas", "1,50 €", "2,90 €"))
OVR.append('<div id="tab5" class="panel tabla">' + "".join(f'<div class="fila"><span>{a}</span><span class="pv5"><s>{b}</s><b>{c}</b></span><span class="flecha">▲</span></div>' for a, b, c in filas5)
           + '<div class="nota5">Precios ilustrativos · escenario hipotético</div></div>')
pop("#tab5", f5 + 0.2, 0.45)
J(f'tl.set("#tab5 b, #tab5 .flecha", {{opacity:0}}, 0); tl.to("#tab5 b, #tab5 .flecha", {{opacity:1, duration:0.2, stagger:0.12}}, {P("disparan") - 0.2:.2f}); tl.to("#tab5 s", {{opacity:0, duration:0.2, stagger:0.12}}, {P("disparan") - 0.2:.2f});')
FX.append(("sube2", P("disparan") - 0.3))
fuera("#tab5", F(6) - 0.1)

# ================================================================== 6) SEMANA: placas solares + panel de salidas
f6 = F(6); dia(f6 + 0.1, 7)
ta = P("aviones")
pan = ['<rect width="1080" height="1920" fill="url(#cieloGris)"/>']
for i in range(4):
    for j in range(5):
        x, y = 70 + i * 240, 420 + j * 230
        pan.append(f'<g><rect x="{x}" y="{y}" width="220" height="210" fill="url(#panelG)" stroke="#9fb3cf" stroke-width="4"/>'
                   + "".join(f'<path d="M{x + 55 * c},{y} L{x + 55 * c},{y + 210}" stroke="#5a7ba3" stroke-width="2" opacity="0.6"/>' for c in (1, 2, 3))
                   + "".join(f'<path d="M{x},{y + 52 * c} L{x + 220},{y + 52 * c}" stroke="#5a7ba3" stroke-width="2" opacity="0.6"/>' for c in (1, 2, 3)) + '</g>')
rr = random.Random(4)
for k in range(9):
    cx, cy = rr.randint(120, 960), rr.randint(480, 1520)
    rays = "".join(f'M{cx},{cy} l{rr.randint(-90, 90)},{rr.randint(-90, 90)} ' for _ in range(6))
    pan.append(f'<path class="grieta6" d="{rays}" stroke="#ffffff" stroke-width="3" fill="none" opacity="0"/>')
pan.append(granizo("g6", 6, 0.8))
escena("e6", "".join(pan))
mostrar("e6", f6, ta - 0.3)
camara("e6", f6, ta, (0, 0, 1.12), (0, 0, 1.0), "power2.out")
caer("g6", f6, ta)
J(f'tl.to(".grieta6", {{opacity:0.9, duration:0.05, stagger:0.14}}, {P("claraboyas") - 0.2:.2f});')
for k in range(4):
    FX.append(("crack", P("claraboyas") - 0.2 + k * 0.3))
chip("PLACAS SOLARES Y CLARABOYAS ROTAS", P("claraboyas"), ta - 0.35, 60, 640, AMB)
vuelos = (("08:15", "MADRID", "IB 3110"), ("08:40", "PARÍS", "VY 8002"), ("09:05", "LONDRES", "BA 461"), ("09:30", "ROMA", "FR 2211"), ("09:55", "LISBOA", "TP 1023"), ("10:20", "BERLÍN", "LH 1803"))
OVR.append('<div id="fondo6" class="fondoTec"></div>')
OVR.append('<div id="sal6" class="panel salidas"><div class="sh"><span>SALIDAS</span><span>DEPARTURES</span></div>'
           + "".join(f'<div class="sf"><span>{h}</span><span>{d}</span><span>{v}</span><span class="est"><em>EN HORA</em><strong>CANCELADO</strong></span></div>' for h, d, v in vuelos) + '</div>')
for s_ in ("#fondo6", "#sal6"):
    J(f'tl.set("{s_}", {{opacity:0}}, 0); tl.set("{s_}", {{opacity:1}}, {ta - 0.3:.2f}); tl.set("{s_}", {{opacity:0}}, {F(7) - 0.03:.2f});')
J(f'tl.set("#sal6 strong", {{opacity:0}}, 0); tl.to("#sal6 strong", {{opacity:1, duration:0.05, stagger:0.15}}, {P("tierra") - 0.4:.2f}); tl.to("#sal6 em", {{opacity:0, duration:0.05, stagger:0.15}}, {P("tierra") - 0.4:.2f});')
J(f'tl.fromTo("#sal6", {{scale:1.0}}, {{scale:1.05, duration:{F(7) - ta:.2f}, ease:"sine.inOut", immediateRender:false}}, {ta - 0.3:.2f});')
for k in range(6):
    FX.append(("clic", P("tierra") - 0.4 + k * 0.15))

# ================================================================== 7) TAMAÑOS Y VELOCIDAD: la cámara viaja por la mesa de medida
f7 = F(7)
tam = (("Guisante", 0.6), ("Canica", 1.5), ("Pelota de golf", 4.3), ("Pelota de tenis", 6.7), ("Pomelo", 11))
xs = 160
e7 = ['<rect x="-400" width="2400" height="1920" fill="url(#fondoTec)"/>', '<rect x="-400" width="2400" height="1920" fill="url(#rejilla)" opacity="0.4"/>',
      '<rect x="-400" y="1240" width="2400" height="6" fill="#33445f"/>']
for i in range(0, 40):
    x = 60 + i * 60
    e7.append(f'<path d="M{x},1246 L{x},{1270 if i % 5 else 1290}" stroke="#4a6080" stroke-width="3"/>')
for k, (nom, cm) in enumerate(tam):
    r = max(8, cm * 12)
    cx = xs + r
    e7.append(f'<g class="b7"><ellipse cx="{cx:.0f}" cy="1244" rx="{r * 0.9:.0f}" ry="{max(4, r * 0.12):.0f}" fill="#000" opacity="0.5"/>{piedra(cx, 1240 - r, r, False)}'
              f'<text x="{cx:.0f}" y="{1240 - 2 * r - 50:.0f}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="32" fill="{INK}">{nom}</text>'
              f'<text x="{cx:.0f}" y="{1240 - 2 * r - 14:.0f}" text-anchor="middle" font-family="Inter" font-weight="700" font-size="28" fill="{ICE}">{str(cm).replace(".", ",")} cm</text></g>')
    xs = cx + r + (170 if cm < 2 else 110)
escena("e7", "".join(e7))
mostrar("e7", f7, F(8))
camara("e7", f7, F(8), (330, 30, 1.3), (-300, 80, 0.92), "power2.inOut")
J(f'tl.set("#e7 .b7", {{opacity:0}}, 0); tl.to("#e7 .b7", {{opacity:1, duration:0.4, stagger:0.55}}, {f7 + 0.2:.2f});')
OVR.append(f'<div id="vel7" class="panel vel"><svg width="380" height="220" viewBox="0 0 380 220">'
           + "".join(f'<path d="M{190 + 150 * math.cos(math.radians(a)):.0f},{200 + 150 * math.sin(math.radians(a)):.0f} L{190 + 170 * math.cos(math.radians(a)):.0f},{200 + 170 * math.sin(math.radians(a)):.0f}" stroke="#4a6080" stroke-width="4"/>' for a in range(180, 361, 18))
           + f'<path d="M40,200 A150,150 0 0 1 340,200" stroke="#1e2c45" stroke-width="16" fill="none"/><path id="arco7" d="M40,200 A150,150 0 0 1 340,200" stroke="{RED}" stroke-width="16" fill="none" pathLength="1" stroke-dasharray="1" style="stroke-dashoffset:1"/>'
           f'<path id="ag7" d="M190,200 L60,200" stroke="{INK}" stroke-width="7" stroke-linecap="round"/><circle cx="190" cy="200" r="12" fill="{INK}"/></svg>'
           f'<div class="vn">{rueda("v7", "160", 92, INK)}<small>km/h</small></div><div class="vt">caída de las piedras más grandes</div></div>')
pop("#vel7", P("grandes") - 0.3, 0.45)
J(f'tl.to("#arco7", {{strokeDashoffset:0.15, duration:1.1, ease:"power3.out"}}, {P("ciento") - 0.2:.2f}); tl.fromTo("#ag7", {{rotation:0}}, {{rotation:150, svgOrigin:"190 200", duration:1.1, ease:"power3.out", immediateRender:false}}, {P("ciento") - 0.2:.2f});')
gira("v7", "160", P("ciento") - 0.2, 1.0)
FX.append(("riser", P("ciento") - 0.9))
fuera("#vel7", F(8) - 0.1)
fuente("Fuente: NOAA · NSSL", P("grandes"), F(8) - 0.1)

# ================================================================== 8) RÉCORD: piedra a escala junto a un móvil
f8 = F(8)
e8 = ['<rect width="1080" height="1920" fill="url(#fondoTec)"/>', '<rect width="1080" height="1920" fill="url(#rejilla)" opacity="0.4"/>',
      f'<g id="rec8">{piedra(380, 980, 210, False)}<circle cx="380" cy="980" r="160" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.18"/><circle cx="380" cy="980" r="100" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.15"/></g>',
      '<g><rect x="720" y="800" width="160" height="330" rx="26" fill="#141c2c" stroke="#5a6e8c" stroke-width="5"/><rect x="734" y="826" width="132" height="270" rx="10" fill="#22324e"/></g>',
      '<path d="M170,1228 L590,1228" stroke="#c9d8ea" stroke-width="4"/><path d="M170,1213 L170,1243 M590,1213 L590,1243" stroke="#c9d8ea" stroke-width="4"/>',
      '<text x="380" y="1290" text-anchor="middle" font-family="Inter" font-weight="800" font-size="40" fill="#c9d8ea">20 cm</text>',
      '<text x="800" y="1180" text-anchor="middle" font-family="Inter" font-weight="700" font-size="26" fill="#8796ad">móvil · 15 cm</text>']
escena("e8", "".join(e8))
mostrar("e8", f8, F(9))
camara("e8", f8, F(9), (0, 0, 1.0), (0, -20, 1.07))
pop("#rec8", f8 + 0.1, 0.6, "opacity:0, scale:0.85")
OVR.append('<div id="rc8" class="dato" style="top:1400px"><div class="dk">RÉCORD EN EE. UU.</div><div class="dn" style="font-size:104px">20 cm · 880 g</div><div class="ds">Vivian, Dakota del Sur · 23 de julio de 2010</div></div>')
pop("#rc8", P("veinte") - 0.3, 0.45)
FX.append(("golpe", P("veinte") - 0.2))
fuera("#rc8", F(9) - 0.1)

# ================================================================== 9-10) DOS SEMANAS → DÍA 30: el hielo sube DESDE EL SUELO (sin flotar)
f9 = F(9); dia(f9 + 0.1, 14)
YS = 1560
e9 = ['<rect width="1080" height="1920" fill="url(#cieloGris)"/>', ciudad(12, YS, 0.2, "#2a3550", "#1d2840", True, 0.85),
      f'<rect x="0" y="{YS}" width="1080" height="{1920 - YS}" fill="#151d2b"/>',
      '<g>' + "".join(f'<rect x="{x}" y="{YS - 250}" width="120" height="250" fill="#3b2a1c" stroke="#5a4532" stroke-width="5"/><circle cx="{x + 100}" cy="{YS - 120}" r="7" fill="#c9a34a"/>' for x in (120, 760)) + '</g>',
      coche_sil("car9", 330, YS - 128, 0.95, "#3a4a6a"),
      f'<g id="cerr9" opacity="0"><rect x="700" y="{YS - 420}" width="300" height="80" rx="8" fill="{RED}"/><text x="850" y="{YS - 367}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="40" fill="#fff">CERRADO</text></g>',
      f'<rect id="hielo9" x="-200" y="{YS}" width="1480" height="900" fill="url(#mantoG)"/>',
      f'<path id="borde9" d="M-200,{YS} L1280,{YS}" stroke="#ffffff" stroke-width="6" opacity="0.8"/>',
      granizo("g9", 9, 0.9)]
escena("e9", "".join(e9))
mostrar("e9", f9, F(11))
camara("e9", f9, F(11), (0, 0, 1.0), (0, 60, 1.1))
caer("g9", f9, F(11))
def subir(t, alto, d):
    J(f'tl.to("#hielo9, #borde9", {{y:{-alto}, duration:{d:.2f}, ease:"power1.inOut"}}, {t:.2f});')
subir(f9 + 0.3, 120, P("guadalajara") - f9 - 0.3)
subir(P("guadalajara"), 260, FE(9) - P("guadalajara"))
subir(F(10), 330, FE(10) - F(10))
OVR.append(f'<div id="reg9" class="regla"><div class="rl"></div><div class="rt">1 m</div></div>')
J(f'tl.set("#reg9", {{opacity:0}}, 0); tl.to("#reg9", {{opacity:1, duration:0.4}}, {P("metro") - 0.4:.2f}); tl.to("#reg9", {{opacity:0, duration:0.3}}, {F(11) - 0.05:.2f});')
OVR.append('<div id="gdl9" class="dato pe"><div class="dk">GUADALAJARA (MÉXICO)</div><div class="dn" style="font-size:96px">+1 m de hielo</div><div class="ds">30 de junio de 2019 · una sola granizada</div></div>')
pop("#gdl9", P("guadalajara") - 0.2, 0.45)
fuera("#gdl9", F(10) - 0.1)
dia(P("imagina") - 0.1, 30)
for k, (txt, w) in enumerate((("PUERTAS BLOQUEADAS", "bloqueadas"), ("COLEGIOS CERRADOS", "cerrados"), ("COCHES ENTERRADOS", "enterrados"))):
    chip(txt, P(w) - 0.3, FE(10) + 0.1, 60, 640 + k * 84, RED if k == 2 else AMB)
pop("#cerr9", P("colegios") - 0.2, 0.3, "opacity:0")
fuente("Fuente: Gobierno de Jalisco y prensa (2019)", P("guadalajara"), F(10) - 0.1)

# ================================================================== 11) DESHIELO: el agua corre
f11 = F(11)
e11 = ['<rect width="1080" height="1920" fill="url(#cieloSol)"/>', '<circle cx="860" cy="560" r="120" fill="#ffd27a" opacity="0.9"/><circle cx="860" cy="560" r="230" fill="#ffd27a" opacity="0.15"/>',
       ciudad(12, YS, 0.15, "#3a3a4a", "#2a2c3a", False, 0.85),
       f'<rect x="0" y="{YS}" width="1080" height="{1920 - YS}" fill="#151d2b"/>',
       f'<g id="agua11" opacity="0"><rect x="-200" y="{YS - 110}" width="1480" height="900" fill="url(#aguaG)"/>'
       + "".join(f'<path class="cor" d="M{x},{YS - 60 + (x // 80 % 4) * 70} l160,0" stroke="#cfe8ff" stroke-width="4" stroke-linecap="round" opacity="0.6"/>' for x in range(-400, 1200, 130)) + '</g>',
       f'<rect id="hielo11" x="-200" y="{YS - 330}" width="1480" height="900" fill="url(#mantoG)"/>']
escena("e11", "".join(e11))
mostrar("e11", f11, F(12))
camara("e11", f11, F(12), (0, 40, 1.08), (0, 0, 1.0))
J(f'tl.to("#hielo11", {{y:420, opacity:0, duration:2.0, ease:"power1.in"}}, {P("derrite") - 0.4:.2f});')
J(f'tl.to("#agua11", {{opacity:1, duration:0.9}}, {P("derrite"):.2f}); tl.fromTo(".cor", {{x:0}}, {{x:600, duration:2.0, repeat:3, ease:"none", immediateRender:false}}, {P("derrite"):.2f});')
FX.append(("agua", P("derrite")))
OVR.append('<div id="tem11" class="panel tem"><div class="pt">TEMPERATURA</div><div class="tv"><span id="t11a">−2 °C</span><span id="t11b">18 °C</span></div></div>')
pop("#tem11", P("para") - 0.2, 0.4)
J(f'tl.set("#t11b", {{opacity:0}}, 0); tl.to("#t11a", {{opacity:0, duration:0.3}}, {P("derrite") - 0.3:.2f}); tl.to("#t11b", {{opacity:1, duration:0.3}}, {P("derrite") - 0.3:.2f});')
fuera("#tem11", P("rios") - 0.2)
chip("RIESGO DE INUNDACIÓN", P("rios") - 0.3, F(12) - 0.1, 60, 640, RED)

# ================================================================== 12) EL DATO: el granizo necesita calor
f12 = F(12); barrido(f12)
J(f'tl.to("#hud", {{opacity:0, duration:0.3}}, {f12:.2f});')
KM = 66.7                                   # 1 km = 66,7 px; suelo en y=1500
def yk(km): return 1500 - km * KM
rr = random.Random(21)
pf = []
# torre: muchas pompas solapadas, base ancha que se estrecha un poco y se abre arriba en yunque
for i in range(140):
    km = rr.uniform(3.5, 11.3)
    t = (km - 3.5) / 7.8
    semi = 250 - 70 * math.sin(t * math.pi) + 40 * t
    x = 560 + rr.uniform(-semi, semi) * 0.85
    r = rr.uniform(60, 110) * (1.0 - 0.25 * t)
    pf.append((x, yk(km), r))
for i in range(40):                         # yunque: capa aplanada a 11-12,4 km que se extiende a los lados
    x = 560 + rr.uniform(-400, 400)
    pf.append((x, yk(rr.uniform(11.4, 12.0)), rr.uniform(50, 80)))
forma = "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}"/>' for x, y, r in pf)
forma += f'<path d="M{560 - 430},{yk(11.7):.0f} C{560 - 280},{yk(12.5):.0f} {560 + 280},{yk(12.6):.0f} {560 + 440},{yk(11.8):.0f} L{560 + 440},{yk(11.3):.0f} L{560 - 430},{yk(11.3):.0f} Z"/>'
DEFS12 = (f'<clipPath id="cbForma">{forma}</clipPath>'
          f'<linearGradient id="fundeArriba" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000"/><stop offset="0.16" stop-color="#fff"/><stop offset="1" stop-color="#fff"/></linearGradient>'
          f'<mask id="cbRevela" maskUnits="userSpaceOnUse" x="-300" y="0" width="1700" height="1920"><rect id="revela12" x="-300" y="{yk(3.3):.0f}" width="1700" height="900" fill="url(#fundeArriba)"/></mask>')
nube12 = (f'<g mask="url(#cbRevela)"><g clip-path="url(#cbForma)">'
          f'<rect x="0" y="{yk(13):.0f}" width="1080" height="{yk(3) - yk(13):.0f}" fill="url(#cbLuz)"/>'
          f'<rect x="0" y="{yk(13):.0f}" width="1080" height="{yk(3) - yk(13):.0f}" fill="url(#cbAlto)"/>'
          + "".join(f'<circle cx="{x + r * 0.25:.0f}" cy="{y - r * 0.3:.0f}" r="{r * 0.55:.0f}" fill="#ffffff" opacity="0.18"/>' for x, y, r in pf[::3])
          + '</g></g>')
base12 = f'<path d="M{560 - 230},{yk(3.4):.0f} C{560 - 120},{yk(3.25):.0f} {560 + 120},{yk(3.25):.0f} {560 + 230},{yk(3.4):.0f}" stroke="#5f7393" stroke-width="10" fill="none" opacity="0.8"/>'
burb = "".join(f'<circle class="burb12" cx="{x}" cy="1480" r="{r}" fill="url(#burbuja)"/>' for x, r in ((380, 46), (470, 34), (560, 52), (650, 38), (740, 44), (520, 30), (610, 28)))
calima = "".join(f'<path class="cal12" d="M{-200 + i * 0},{1470 - i * 14} q60,-12 120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0" stroke="#ffcf9a" stroke-width="3" fill="none" opacity="{0.35 - i * 0.06:.2f}"/>' for i in range(5))
eje = ('<path d="M110,1500 L110,660" stroke="#4a6080" stroke-width="3"/>'
       + "".join(f'<path d="M104,{yk(k):.0f} L118,{yk(k):.0f}" stroke="#4a6080" stroke-width="3"/><text x="132" y="{yk(k) + 9:.0f}" font-family="Inter" font-weight="700" font-size="26" fill="#8796ad">{k} km</text>' for k in (0, 4, 8, 12))
       + f'<path d="M100,{yk(4.2):.0f} L1000,{yk(4.2):.0f}" stroke="{ICE}" stroke-width="2" stroke-dasharray="12 10" opacity="0.55"/>'
       + f'<text x="1000" y="{yk(4.2) - 14:.0f}" text-anchor="end" font-family="Inter" font-weight="800" font-size="28" fill="{ICE}">0 °C</text>'
       + f'<text x="1000" y="{yk(10) - 14:.0f}" text-anchor="end" font-family="Inter" font-weight="800" font-size="28" fill="{ICE}">−40 °C</text>'
       + f'<path d="M100,{yk(10):.0f} L1000,{yk(10):.0f}" stroke="{ICE}" stroke-width="2" stroke-dasharray="12 10" opacity="0.4"/>'
       + f'<text x="1000" y="1460" text-anchor="end" font-family="Inter" font-weight="800" font-size="28" fill="{AMB}">30 °C</text>')
paisaje = ('<path d="M-200,1500 L1280,1500 L1280,2700 L-200,2700 Z" fill="url(#sueloCal)"/>'
           '<path d="M0,1500 C200,1488 380,1494 560,1486 C760,1478 900,1492 1080,1484 L1080,1520 L0,1520 Z" fill="#8a4a26" opacity="0.7"/>'
           + "".join(f'<rect x="{x}" y="{1500 - h}" width="{w}" height="{h}" fill="#3a2418"/>' for x, w, h in ((40, 40, 60), (90, 26, 40), (840, 50, 80), (900, 34, 50), (950, 44, 70))))
e12 = ['<rect width="1080" height="1920" fill="url(#cieloTarde)"/>', '<circle cx="990" cy="1430" r="60" fill="#ffd27a" opacity="0.95"/><circle cx="990" cy="1430" r="150" fill="#ffd27a" opacity="0.12"/>',
       eje, paisaje, calima, burb, base12, '<g id="torre12">' + nube12 + '</g>']
escena("e12", "".join(e12))
mostrar("e12", f12, F(13) + 0.5)
camara("e12", f12, F(13) + 0.5, (0, -420, 1.2), (0, 60, 0.97), "power1.inOut")
J(f'tl.fromTo(".cal12", {{x:0}}, {{x:-120, duration:2.0, repeat:{int((F(13) + 0.5 - f12) / 2) + 1}, ease:"none", immediateRender:false}}, {f12:.2f});')
J(f'tl.fromTo(".burb12", {{y:0, opacity:0.0, scale:0.6}}, {{y:{yk(3.4) - 1480:.0f}, opacity:0.9, scale:1.2, duration:2.2, stagger:0.35, repeat:{int((F(13) + 0.5 - f12) / 2.6)}, ease:"power1.in", immediateRender:false}}, {f12 + 0.2:.2f});')
J('tl.set(".burb12", {opacity:0}, 0);')
dur_c = max(2.5, FE(12) - f12 - 0.6)
J(f'tl.set("#revela12", {{attr:{{y:{yk(3.1):.0f}, height:{1920 - yk(3.1) + 200:.0f}}}}}, 0); tl.to("#revela12", {{attr:{{y:{yk(13.6):.0f}, height:{1920 - yk(13.6) + 200:.0f}}}, duration:{dur_c:.2f}, ease:"power1.inOut"}}, {f12 + 0.4:.2f});')
chip("EL AIRE CALIENTE SUBE Y FORMA LA TORMENTA", P("caliente") - 0.3, F(13) + 0.4, 60, 1640, AMB)
FX.append(("brillo", P("calor")))

# ================================================================== 13) CIERRE EN BUCLE: un día de calor, una sola piedra
f13 = F(13)
e13 = ['<rect width="1080" height="1920" fill="url(#cieloSol)"/>', ciudad(3, 1500, 0.2, "#2e2a36", "#221f2a"), calle(1500, False), coche_sil("car13", 640, 1420, 1.05, "#3a3446")]
escena("e13", "".join(e13))
mostrar("e13", f13 + 0.5, DUR - 0.35)
camara("e13", f13 + 0.5, DUR - 0.35, (0, 0, 1.04), (0, 60, 1.18), "power2.in")
OVR.append('<svg id="pu13" width="200" height="200" viewBox="-100 -100 200 200" style="position:absolute;left:640px;top:-220px;overflow:visible;z-index:9">'
           '<path d="M-10,-700 L0,0" stroke="url(#estela)" stroke-width="40" stroke-linecap="round" opacity="0.4"/><circle r="40" fill="url(#hielo)"/><ellipse cx="-14" cy="-14" rx="12" ry="9" fill="#fff" opacity="0.9"/></svg>')
J(f'tl.set("#pu13", {{opacity:0}}, 0); tl.set("#pu13", {{opacity:1}}, {f13 + 0.6:.2f}); tl.fromTo("#pu13", {{y:0}}, {{y:1500, duration:{DUR - f13 - 0.9:.2f}, ease:"power2.in", immediateRender:false}}, {f13 + 0.6:.2f}); tl.set("#pu13", {{opacity:0}}, {DUR - 0.3:.2f});')
J(f'tl.set("#e1", {{opacity:1}}, {DUR - 0.35:.2f}); tl.set("#e1-cam", {{x:0, y:60, scale:1.18}}, {DUR - 0.35:.2f}); tl.set("#titulo", {{opacity:1, y:0}}, {DUR - 0.35:.2f}); tl.set("#mantoB", {{opacity:0}}, {DUR - 0.35:.2f});')

# ------------------------------------------------------------------ subtítulos
CLAVE = set(norm(w) for w in ["granizar", "treinta", "minutos", "capas", "blancas", "tambores", "abolladuras", "perdido", "millon", "hectareas",
                               "precios", "disparan", "claraboyas", "solares", "aviones", "ciento", "sesenta", "veinte", "kilo", "acumula",
                               "metro", "bloqueadas", "cerrados", "enterrados", "derrite", "rios", "calor", "caliente", "piedra"])
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

rr = random.Random(3)
for s in range(int(DUR / 0.08)):
    J(f'tl.set("#grano", {{backgroundPosition:"{rr.randint(0, 360)}px {rr.randint(0, 360)}px"}}, {s * 0.08:.2f});')

cortina = capa_granizo("cort", 170, 4, 13, 1.0, 77, 1080, 2400)
html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:{BG}}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;background:{BG}}}
.esc{{position:absolute;inset:0;overflow:hidden}}
.cam{{position:absolute;inset:0;transform-origin:50% 50%}}
.fondoTec{{position:absolute;inset:0;background:radial-gradient(120% 80% at 50% 40%, #13213a, {BG} 70%);z-index:12}}
#hud{{position:absolute;left:60px;top:470px;width:250px;padding:12px 18px 16px;border-left:5px solid {ICE};background:rgba(7,12,22,0.62);z-index:40;color:{INK}}}
#hud .hl{{font:800 22px Inter;letter-spacing:6px;color:{MUTED}}} #hud .hn{{display:inline-block;font:900 72px Inter;line-height:1;letter-spacing:-2px}}
#hud .hd{{display:inline-block;font:800 32px Inter;color:{MUTED};margin-left:8px}}
#hud .hbar{{margin-top:10px;height:6px;background:#1e2c45}} #hud .hbar i{{display:block;height:100%;background:{ICE};transform-origin:0 50%;transform:scaleX(0.0333)}}
.chip{{position:absolute;z-index:35;display:flex;align-items:center;gap:14px;padding:14px 22px;background:rgba(7,12,22,0.8);border:2px solid;border-radius:6px;font:800 30px Inter;letter-spacing:1px;color:{INK}}}
.chip b{{width:12px;height:12px;border-radius:50%}}
.fuente{{position:absolute;left:60px;right:60px;top:1712px;z-index:35;font:600 24px Inter;color:{MUTED};letter-spacing:0.5px}}
.panel{{position:absolute;z-index:30;background:rgba(9,15,28,0.88);border:1px solid #2b3d5c;border-radius:10px;color:{INK}}}
#db3{{left:60px;top:1180px;width:560px;padding:22px 26px}} .pt{{font:800 22px Inter;letter-spacing:4px;color:{MUTED}}}
.barras{{display:flex;align-items:flex-end;gap:10px;height:220px;margin-top:14px}} .bd{{width:38px;background:linear-gradient(0deg,{ICE},{AMB} 70%,{RED});border-radius:3px}}
.pv{{margin-top:10px;font:700 26px Inter;color:#c9d8ea}}
.dato{{position:absolute;left:60px;right:60px;top:1260px;z-index:30;padding:26px 30px;background:rgba(9,15,28,0.88);border-left:6px solid {ICE};color:{INK}}}
.dato.pe{{top:860px}}
.dk{{font:800 24px Inter;letter-spacing:4px;color:{ICE}}} .dn{{font:900 120px Inter;letter-spacing:-3px;line-height:1.05}}
.dt{{font:800 30px Inter;letter-spacing:2px;color:#c9d8ea}} .ds{{font:600 26px Inter;color:{MUTED};margin-top:6px}}
.tabla{{left:60px;right:60px;top:1240px;padding:18px 26px}} .fila{{display:grid;grid-template-columns:1fr 300px 60px;align-items:center;padding:14px 0;border-bottom:1px solid #1e2c45;font:800 40px Inter}}
.pv5{{position:relative;height:50px}} .pv5 s{{position:absolute;left:0;top:0;color:#c9d8ea;text-decoration:none}} .pv5 b{{position:absolute;left:0;top:0;color:{RED}}}
.flecha{{color:{RED};font-size:34px}} .nota5{{font:600 22px Inter;color:{MUTED};margin-top:12px}}
.salidas{{left:40px;right:40px;top:720px;padding:20px 24px;background:#0b0f18;border:2px solid #2a3240;z-index:30}}
.sh{{display:flex;justify-content:space-between;font:900 40px Inter;color:{AMB};letter-spacing:4px;padding-bottom:14px;border-bottom:2px solid #2a3240}}
.sf{{display:grid;grid-template-columns:110px 1fr 160px 230px;gap:10px;padding:16px 0;border-bottom:1px solid #1a2130;font:700 33px "Courier New", monospace;color:#f3e7c4}}
.est{{position:relative}} .est em{{font-style:normal;color:{GRN}}} .est strong{{position:absolute;left:0;top:0;color:{RED}}}
.vel{{left:60px;top:560px;width:440px;padding:20px 26px}} .vn{{font:900 92px Inter;line-height:1;margin-top:-10px}} .vn small{{font:800 34px Inter;color:{MUTED};margin-left:10px}}
.vt{{font:700 24px Inter;color:{MUTED};margin-top:6px}}
.tem{{left:60px;top:1240px;width:520px;padding:20px 26px}} .tv{{position:relative;height:110px;font:900 100px Inter}} .tv span{{position:absolute;left:0;top:0}} #t11a{{color:{ICE}}} #t11b{{color:{AMB}}}
.regla{{position:absolute;left:24px;top:{YS - 420}px;width:70px;height:420px;z-index:30}}
.regla .rl{{position:absolute;inset:0;border:3px solid #c9d8ea;border-right:none;background:repeating-linear-gradient(180deg, transparent 0 40px, rgba(201,216,234,0.7) 40px 43px)}}
.regla .rt{{position:absolute;left:80px;top:-20px;white-space:nowrap;font:900 40px Inter;color:{INK};text-shadow:0 2px 8px #000}}
.rueda{{display:inline-flex;align-items:baseline;font-weight:900;font-family:Inter;letter-spacing:-3px;font-variant-numeric:tabular-nums}}
.dg{{display:inline-block;height:1em;overflow:hidden;line-height:1em}} .st{{display:grid}} .st span{{height:1em;line-height:1em}} .sep{{display:inline-block;line-height:1em}}
#titulo{{position:absolute;left:56px;right:56px;top:620px;z-index:20}}
#titulo .t0{{font:800 64px Inter;color:#c9d8ea;letter-spacing:2px}} #titulo .t1{{font:900 112px Inter;color:#ffffff;letter-spacing:-4px;line-height:1}} #titulo .t1 span{{color:{ICE}}}
#cortina{{position:absolute;left:0;top:0;width:1080px;height:2400px;z-index:58;pointer-events:none}}
#grano{{position:absolute;inset:0;z-index:57;pointer-events:none;opacity:0.07;background:url(assets/grano.png);mix-blend-mode:overlay}}
#vineta{{position:absolute;inset:0;z-index:56;pointer-events:none;background:radial-gradient(110% 80% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55))}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:560px;z-index:55;pointer-events:none;background:linear-gradient(rgba(4,8,16,0.8), rgba(4,8,16,0))}}
#marca{{position:absolute;left:0;right:0;top:1775px;text-align:center;font:700 28px Inter;color:#ffffff;opacity:0.32;pointer-events:none;z-index:61}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 62px Inter;color:rgba(255,255,255,0.4);line-height:1.22;text-shadow:0 3px 12px rgba(0,0,0,0.6)}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:3px solid #4ea3ff;border-radius:6px;background:rgba(78,163,255,0.18);opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <svg width="0" height="0" style="position:absolute"><defs>
    <radialGradient id="hielo" cx="0.38" cy="0.35" r="0.7"><stop offset="0" stop-color="#ffffff"/><stop offset="0.45" stop-color="#e3f3ff"/><stop offset="0.85" stop-color="#9cc3dd"/><stop offset="1" stop-color="#6f97b4"/></radialGradient>
    <linearGradient id="estela" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0"/><stop offset="1" stop-color="#ffffff" stop-opacity="0.9"/></linearGradient>
    <linearGradient id="cieloNoche" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05080f"/><stop offset="0.55" stop-color="#16243d"/><stop offset="1" stop-color="#2a3c5a"/></linearGradient>
    <linearGradient id="cieloAlba" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b2840"/><stop offset="0.6" stop-color="#55688a"/><stop offset="1" stop-color="#9aaecb"/></linearGradient>
    <linearGradient id="cieloGris" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#121c2e"/><stop offset="1" stop-color="#4a5a74"/></linearGradient>
    <linearGradient id="cieloSol" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a2238"/><stop offset="0.55" stop-color="#b8664a"/><stop offset="1" stop-color="#f0b06a"/></linearGradient>
    <radialGradient id="nubeG" cx="0.5" cy="0.35" r="0.6"><stop offset="0" stop-color="#5c6c88"/><stop offset="1" stop-color="#1a2438" stop-opacity="0"/></radialGradient>
    <linearGradient id="nubeTec" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dce8f6"/><stop offset="1" stop-color="#6f86a6"/></linearGradient>
    <radialGradient id="fondoTec" cx="0.5" cy="0.4" r="0.9"><stop offset="0" stop-color="#13213a"/><stop offset="1" stop-color="{BG}"/></radialGradient>
    <pattern id="rejilla" width="60" height="60" patternUnits="userSpaceOnUse"><path d="M60,0 L0,0 0,60" fill="none" stroke="#1b2a44" stroke-width="1.5"/></pattern>
    <linearGradient id="asfalto" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#121a28"/><stop offset="1" stop-color="#05080f"/></linearGradient>
    <linearGradient id="reflejo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffcf7a" stop-opacity="0.18"/><stop offset="1" stop-color="#ffcf7a" stop-opacity="0"/></linearGradient>
    <linearGradient id="mantoG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4faff"/><stop offset="0.12" stop-color="#d9e9f6"/><stop offset="1" stop-color="#9fb8cf"/></linearGradient>
    <linearGradient id="capo" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5a6678"/><stop offset="0.5" stop-color="#2c3646"/><stop offset="1" stop-color="#151b26"/></linearGradient>
    <radialGradient id="abolG" cx="0.6" cy="0.65" r="0.6"><stop offset="0" stop-color="#05080f" stop-opacity="0.7"/><stop offset="1" stop-color="#05080f" stop-opacity="0"/></radialGradient>
    <linearGradient id="panelG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2b4b7a"/><stop offset="0.5" stop-color="#14274a"/><stop offset="1" stop-color="#0c1830"/></linearGradient>
    <linearGradient id="areaRoja" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{RED}" stop-opacity="0.5"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></linearGradient>
    <linearGradient id="aguaG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4f86b8"/><stop offset="1" stop-color="#1c3550"/></linearGradient>
    <radialGradient id="puff" cx="0.45" cy="0.3" r="0.7"><stop offset="0" stop-color="#ffffff"/><stop offset="0.55" stop-color="#dfe7f2"/><stop offset="1" stop-color="#8a9bb4"/></radialGradient>
    <linearGradient id="yunqueG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f8fd"/><stop offset="1" stop-color="#a9b8cc"/></linearGradient>
    <radialGradient id="burbuja"><stop offset="0" stop-color="#ffb547" stop-opacity="0.55"/><stop offset="1" stop-color="#ff7a3a" stop-opacity="0"/></radialGradient>
    <linearGradient id="cieloTarde" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d1730"/><stop offset="0.55" stop-color="#2e4a78"/><stop offset="0.85" stop-color="#c47a52"/><stop offset="1" stop-color="#f0b06a"/></linearGradient>
    <linearGradient id="cbLuz" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#fff1dc"/><stop offset="0.45" stop-color="#d8e2ef"/><stop offset="1" stop-color="#6d7f9c"/></linearGradient>
    <linearGradient id="cbAlto" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0.35"/><stop offset="0.7" stop-color="#ffffff" stop-opacity="0"/><stop offset="1" stop-color="#2a3a58" stop-opacity="0.55"/></linearGradient>
    {DEFS12}
    <linearGradient id="sueloCal" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7a3a22"/><stop offset="1" stop-color="#2a1610"/></linearGradient>
  </defs></svg>
  {"".join(ESC)}
  <div id="topsombra"></div>
  {"".join(OVR)}
  <svg id="cortina" width="1080" height="2400">{cortina}</svg>
  <div id="vineta"></div><div id="grano"></div>
  <div id="marca">@mundo.supuesto</div>
  <div id="subs" data-layout-allow-overlap>{"".join(SUBS)}</div>
  <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
tl.set("#cortina", {{y:-2400}}, 0);
{chr(10).join(tl)}
tl.to({{}}, {{duration:0.01}}, {DUR - 0.01});
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>"""
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump(FX, open(os.path.join(BASE, "efectos.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones")

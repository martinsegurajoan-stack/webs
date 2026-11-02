#!/usr/bin/env python3
"""«¿Y si granizara 30 días seguidos?» (@mundo.supuesto, 70-90 s). Animación 2D estilo Netflix: escenarios distintos por
etapa (calle con tormenta, nube por dentro, tejados y coches, campo, supermercado, aeropuerto, tamaños del granizo,
calle enterrada, riada, aire caliente), personaje articulado, granizo que cae y rebota, calendario que arranca hojas,
números que ruedan, notas con fuente, barridos de color, grano, viñeta y final en bucle.
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
R = random.Random(30)
NID = [0]
def nid(p="e"):
    NID[0] += 1
    return f"{p}{NID[0]}"

NAVY, ICE, ICE2, BLUE = "#1b2340", "#f4fbff", "#bfe3f7", "#2f7de1"
RED, YEL, GRN, ORA = "#ef4a4a", "#ffc93c", "#33b864", "#ff8a3c"

# ------------------------------------------------------------------ utilidades
def pop(sel, t, d=0.45, frm="scale:0.3, opacity:0", ease="back.out(2.2)"):
    J(f'tl.set("{sel}", {{opacity:0}}, 0);')
    J(f'tl.fromTo("{sel}", {{{frm}}}, {{scale:1, opacity:1, x:0, y:0, rotation:0, duration:{d}, ease:"{ease}", immediateRender:false}}, {t:.2f});')
def fuera(sel, t, d=0.3):
    J(f'tl.to("{sel}", {{opacity:0, duration:{d}}}, {t:.2f});')
def punch(sel, t, s=1.06):
    J(f'tl.fromTo("{sel}", {{scale:{s}}}, {{scale:1, duration:0.5, ease:"power3.out", immediateRender:false}}, {t:.2f});')

def granizo(gid, n=90, w=1080, h=1920, rmin=6, rmax=13, slant=60, seed=1):
    """Capa de granizo: dos copias apiladas que bajan en bucle (determinista)."""
    rr = random.Random(seed)
    piedras = []
    for _ in range(n):
        x, y, r = rr.uniform(-80, w + 40), rr.uniform(0, h), rr.uniform(rmin, rmax)
        piedras.append(f'<g transform="translate({x:.0f},{y:.0f})"><path d="M{-r * 0.5:.1f},{-r * 5:.1f} L0,0" stroke="#ffffff" stroke-width="{r * 0.6:.1f}" opacity="0.35" stroke-linecap="round"/>'
                       f'<circle r="{r:.1f}" fill="{ICE}"/><circle cx="{-r * 0.3:.1f}" cy="{-r * 0.3:.1f}" r="{r * 0.35:.1f}" fill="#ffffff"/><circle r="{r:.1f}" fill="none" stroke="#9fd2ee" stroke-width="2"/></g>')
    capa = "".join(piedras)
    return (f'<svg class="gran" id="{gid}" width="{w}" height="{h}" style="position:absolute;left:0;top:0;overflow:hidden;pointer-events:none">'
            f'<g class="granmov">{capa}<g transform="translate(0,-{h})">{capa}</g></g></svg>')
def caer(gid, t0, t1, vel=1.1, slant=60):
    n = max(1, int((t1 - t0) / vel))
    J(f'tl.fromTo("#{gid} .granmov", {{y:0, x:0}}, {{y:1920, x:{-slant}, duration:{vel}, repeat:{n}, ease:"none", immediateRender:false}}, {t0:.2f});')

# ------------------------------------------------------------------ personaje (hombre adulto, de frente, articulado)
SK, SKD, HAIR, JACK, JACKD, PANT = "#f2c49b", "#d99e74", "#3b2a20", "#2f6fd6", "#2456a8", "#2b3048"
def persona(pid, paraguas=False, s=1.0):
    """Cuerpo de 1000x1800 (pies en y=1700). Grupos con pivote: brazos (hombro/codo), cabeza, cara."""
    brazoI = (f'<g id="{pid}-aL"><path d="M392,1000 C380,980 410,960 430,975 L420,1150 L380,1150 Z" fill="{JACKD}"/>'
              f'<g id="{pid}-fL"><path d="M380,1140 L420,1140 L410,1290 L376,1290 Z" fill="{JACKD}"/><circle cx="393" cy="1305" r="26" fill="{SK}"/></g></g>')
    paraguas_svg = (f'<g id="{pid}-umb"><path d="M607,1300 L607,700" stroke="#3a2a1a" stroke-width="10"/>'
                    f'<path d="M607,1300 q0,40 -30,40" stroke="#3a2a1a" stroke-width="10" fill="none"/>'
                    f'<path d="M300,720 Q607,380 914,720 Q850,690 800,720 Q760,690 710,720 Q660,690 607,720 Q555,690 505,720 Q455,690 405,720 Q355,690 300,720 Z" fill="{RED}"/>'
                    f'<path d="M607,720 Q607,500 607,410 M405,720 Q470,520 607,410 M810,720 Q745,520 607,410" stroke="#b83030" stroke-width="5" fill="none"/>'
                    f'<g id="{pid}-agujeros" opacity="0"><ellipse cx="470" cy="620" rx="22" ry="14" fill="#1b2340"/><ellipse cx="700" cy="580" rx="18" ry="12" fill="#1b2340"/><ellipse cx="560" cy="510" rx="14" ry="10" fill="#1b2340"/></g></g>') if paraguas else ""
    brazoD = (f'<g id="{pid}-aR"><path d="M570,975 C590,960 620,980 608,1000 L620,1150 L580,1150 Z" fill="{JACK}"/>'
              f'<g id="{pid}-fR"><path d="M580,1140 L620,1140 L624,1290 L590,1290 Z" fill="{JACK}"/><circle cx="607" cy="1305" r="26" fill="{SK}"/></g></g>')
    cabeza = (f'<g id="{pid}-head"><rect x="472" y="880" width="56" height="90" rx="20" fill="{SKD}"/>'
              f'<path d="M410,740 C410,650 460,610 500,610 C540,610 590,650 590,740 C590,830 550,885 500,885 C450,885 410,830 410,740 Z" fill="{SK}"/>'
              f'<ellipse cx="410" cy="760" rx="16" ry="26" fill="{SKD}"/><ellipse cx="590" cy="760" rx="16" ry="26" fill="{SKD}"/>'
              f'<path d="M402,730 C396,640 450,590 505,592 C570,594 606,640 598,724 C580,690 540,672 500,676 C470,672 440,690 420,740 Z" fill="{HAIR}"/>'
              f'<g id="{pid}-ojos"><ellipse cx="465" cy="748" rx="16" ry="18" fill="#ffffff"/><ellipse cx="535" cy="748" rx="16" ry="18" fill="#ffffff"/>'
              f'<circle class="pup" cx="467" cy="752" r="8" fill="#2a1d16"/><circle class="pup" cx="537" cy="752" r="8" fill="#2a1d16"/>'
              f'<rect class="parpado" x="446" y="728" width="38" height="0" fill="{SK}"/><rect class="parpado" x="516" y="728" width="38" height="0" fill="{SK}"/></g>'
              f'<path d="M444,720 Q465,708 486,718 M514,718 Q535,708 556,720" stroke="{HAIR}" stroke-width="8" fill="none" stroke-linecap="round" id="{pid}-cejas"/>'
              f'<path d="M500,760 Q492,800 506,806" stroke="{SKD}" stroke-width="6" fill="none" stroke-linecap="round"/>'
              f'<path id="{pid}-boca" d="M472,830 Q500,846 528,830" stroke="#8a3d33" stroke-width="7" fill="none" stroke-linecap="round"/>'
              f'<ellipse id="{pid}-bocaO" cx="500" cy="836" rx="16" ry="20" fill="#7a2f28" opacity="0"/></g>')
    cuerpo = (f'<path d="M420,980 C430,950 570,950 580,980 L600,1330 L400,1330 Z" fill="{JACK}"/>'
              f'<path d="M500,960 L500,1330" stroke="{JACKD}" stroke-width="5"/>'
              f'<path d="M420,1320 L580,1320 L572,1700 L515,1700 L500,1420 L485,1700 L428,1700 Z" fill="{PANT}"/>'
              f'<path d="M420,1690 L488,1690 L490,1712 L404,1712 Z M512,1690 L580,1690 L596,1712 L510,1712 Z" fill="#1d1d24"/>')
    return (f'<svg class="pj" id="{pid}" viewBox="0 0 1000 1800" width="{1000 * s:.0f}" height="{1800 * s:.0f}" style="overflow:visible;position:absolute">'
            f'<ellipse cx="500" cy="1712" rx="170" ry="22" fill="#000" opacity="0.2"/><g id="{pid}-cuerpo">{brazoI}{cuerpo}{cabeza}{brazoD}{paraguas_svg}</g></svg>')
def vida(pid, t0, t1):
    n = max(1, int((t1 - t0) / 1.6))
    J(f'tl.to("#{pid}-cuerpo", {{y:-8, duration:0.8, yoyo:true, repeat:{n * 2 - 1}, ease:"sine.inOut", svgOrigin:"500 1700"}}, {t0:.2f});')
    J(f'tl.to("#{pid}-head", {{rotation:3, duration:1.1, yoyo:true, repeat:{max(1, int((t1 - t0) / 1.1)) - 1}, ease:"sine.inOut", svgOrigin:"500 900"}}, {t0:.2f});')
    for k in range(int((t1 - t0) / 3.2)):
        tb = t0 + 1.2 + k * 3.2
        J(f'tl.to("#{pid} .parpado", {{attr:{{height:40}}, duration:0.07, yoyo:true, repeat:1}}, {tb:.2f});')
def brazo(pid, lado, t, hombro, codo, d=0.4):
    o = "400 1000" if lado == "L" else "600 1000"
    oc = "400 1145" if lado == "L" else "600 1145"
    J(f'tl.to("#{pid}-a{lado}", {{rotation:{hombro}, duration:{d}, ease:"back.out(1.5)", svgOrigin:"{o}"}}, {t:.2f}); tl.to("#{pid}-f{lado}", {{rotation:{codo}, duration:{d}, ease:"back.out(1.5)", svgOrigin:"{oc}"}}, {t:.2f});')
def cara(pid, t, tipo):
    bocas = {"normal": "M472,830 Q500,846 528,830", "triste": "M472,840 Q500,824 528,840", "feliz": "M466,822 Q500,862 534,822", "plano": "M476,834 L524,834"}
    if tipo == "sorpresa":
        J(f'tl.to("#{pid}-bocaO", {{opacity:1, duration:0.1}}, {t:.2f}); tl.to("#{pid}-boca", {{opacity:0, duration:0.1}}, {t:.2f}); tl.to("#{pid}-cejas", {{y:-12, duration:0.2}}, {t:.2f});')
    else:
        J(f'tl.to("#{pid}-bocaO", {{opacity:0, duration:0.1}}, {t:.2f}); tl.to("#{pid}-boca", {{opacity:1, attr:{{d:"{bocas[tipo]}"}}, duration:0.2}}, {t:.2f}); tl.to("#{pid}-cejas", {{y:{6 if tipo == "triste" else 0}, duration:0.2}}, {t:.2f});')

# ------------------------------------------------------------------ escenarios
ESC = []          # (id, html)
def escena(eid, cuerpo, fondo="#000"):
    ESC.append(f'<div class="esc" id="{eid}" style="background:{fondo}"><div class="cam" id="{eid}-cam"><svg width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0;overflow:visible">{cuerpo}</svg></div></div>')
def mostrar(eid, t0, t1, zoom=1.07):
    J(f'tl.set("#{eid}", {{opacity:0}}, 0); tl.set("#{eid}", {{opacity:1}}, {t0:.2f}); tl.set("#{eid}", {{opacity:0}}, {t1:.2f});')
    if zoom is None:
        return
    J(f'tl.fromTo("#{eid}-cam", {{scale:1}}, {{scale:{zoom}, duration:{t1 - t0:.2f}, ease:"sine.inOut", immediateRender:false}}, {t0:.2f});')

def edificio(x, y, w, h, col, techo="#c0533a", seed=0, toldo=None, rotulo=None, nieve=False):
    rr = random.Random(seed)
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{col}"/>',
         f'<rect x="{x - 10}" y="{y - 26}" width="{w + 20}" height="30" fill="{techo}"/>']
    cols, filas = max(2, w // 110), max(2, (h - 200) // 150)
    for i in range(cols):
        for j in range(filas):
            wx, wy = x + 30 + i * ((w - 60) / cols), y + 40 + j * 150
            luz = rr.random() < 0.45
            s.append(f'<rect x="{wx:.0f}" y="{wy:.0f}" width="60" height="90" rx="6" fill="{"#ffd98a" if luz else "#3f5f8c"}"/>'
                     f'<rect x="{wx - 8:.0f}" y="{wy + 88:.0f}" width="76" height="10" fill="#ffffff" opacity="0.8"/>'
                     f'<path d="M{wx - 6:.0f},{wy + 98:.0f} l0,26 M{wx + 66:.0f},{wy + 98:.0f} l0,26 M{wx - 6:.0f},{wy + 124:.0f} l72,0" stroke="#1b2340" stroke-width="4" fill="none"/>')
            if rr.random() < 0.35:
                s.append(f'<ellipse cx="{wx + 14:.0f}" cy="{wy + 92:.0f}" rx="16" ry="12" fill="{GRN}"/><circle cx="{wx + 6:.0f}" cy="{wy + 86:.0f}" r="5" fill="{RED}"/>')
    if toldo:
        s.append(f'<path d="M{x + 20},{y + h - 210} L{x + w - 20},{y + h - 210} L{x + w},{y + h - 150} L{x},{y + h - 150} Z" fill="{toldo}"/>'
                 + "".join(f'<rect x="{x + 20 + k * 40}" y="{y + h - 210}" width="20" height="60" fill="#ffffff" opacity="0.45"/>' for k in range((w - 40) // 40)))
        s.append(f'<rect x="{x + 40}" y="{y + h - 140}" width="{w - 80}" height="140" fill="#2a3a5a"/><rect x="{x + 52}" y="{y + h - 128}" width="{w - 104}" height="120" fill="#ffe7a8" opacity="0.6"/>')
    if rotulo:
        s.append(f'<rect x="{x + w / 2 - 110:.0f}" y="{y + h - 270}" width="220" height="50" rx="10" fill="#ffffff"/><text x="{x + w / 2:.0f}" y="{y + h - 233}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="30" fill="{NAVY}">{rotulo}</text>')
    if nieve:
        s.append(f'<path d="M{x - 10},{y - 26} q{(w + 20) / 4:.0f},-24 {(w + 20) / 2:.0f},0 q{(w + 20) / 4:.0f},-20 {(w + 20) / 2:.0f},0 l0,12 l-{w + 20},0 Z" fill="{ICE}"/>')
    return "".join(s)

def coche(cid, x, y, col, s=1.0):
    return (f'<g id="{cid}" transform="translate({x},{y}) scale({s})"><ellipse cx="160" cy="132" rx="170" ry="14" fill="#000" opacity="0.25"/>'
            f'<path d="M10,110 L10,70 Q14,48 50,44 L90,40 L130,0 L230,0 L280,40 L310,48 Q330,54 330,80 L330,110 Z" fill="{col}"/>'
            f'<path d="M140,12 L222,12 L262,42 L104,42 Z" fill="#bfe3f7"/><path d="M183,12 L183,42" stroke="{col}" stroke-width="8"/>'
            f'<circle cx="80" cy="112" r="28" fill="#1b1b22"/><circle cx="80" cy="112" r="12" fill="#c9c9d1"/><circle cx="255" cy="112" r="28" fill="#1b1b22"/><circle cx="255" cy="112" r="12" fill="#c9c9d1"/>'
            f'<rect x="300" y="64" width="24" height="12" rx="4" fill="#fff4b0"/><rect x="12" y="66" width="18" height="12" rx="4" fill="#ff6b6b"/>'
            f'<g class="abolla" opacity="0">' + "".join(f'<ellipse cx="{dx}" cy="{dy}" rx="10" ry="6" fill="#000" opacity="0.25"/>' for dx, dy in ((60, 60), (110, 50), (200, 70), (270, 62), (160, 88), (40, 90))) + '</g>'
            f'<g class="grieta" opacity="0"><path d="M190,20 l-12,10 l14,6 l-20,8 M190,20 l18,8 l-6,12 M190,20 l4,-8" stroke="#ffffff" stroke-width="3" fill="none"/></g></g>')

def farola(x, y):
    return (f'<rect x="{x}" y="{y - 420}" width="14" height="420" fill="#2b3048"/><path d="M{x + 7},{y - 420} q0,-40 60,-40" stroke="#2b3048" stroke-width="12" fill="none"/>'
            f'<path d="M{x + 50},{y - 470} l40,0 l10,24 l-60,0 Z" fill="#2b3048"/><ellipse cx="{x + 70}" cy="{y - 440}" rx="26" ry="12" fill="#ffe08a"/>')
def arbol(x, y, s=1.0, col="#3cb371"):
    return (f'<g transform="translate({x},{y}) scale({s})"><rect x="-14" y="-160" width="28" height="160" fill="#7a4b2a"/>'
            f'<circle cx="0" cy="-200" r="90" fill="{col}"/><circle cx="-60" cy="-160" r="60" fill="{col}"/><circle cx="60" cy="-160" r="60" fill="{col}"/><circle cx="-20" cy="-240" r="50" fill="#5fd18b" opacity="0.6"/></g>')
def nube(x, y, s=1.0, col="#5a5f86", op=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})" opacity="{op}"><ellipse cx="0" cy="0" rx="200" ry="90" fill="{col}"/><ellipse cx="-150" cy="30" rx="130" ry="70" fill="{col}"/>'
            f'<ellipse cx="160" cy="30" rx="140" ry="70" fill="{col}"/><ellipse cx="-40" cy="-60" rx="120" ry="80" fill="{col}"/><ellipse cx="70" cy="-50" rx="110" ry="70" fill="{col}"/></g>')

OVR = []
def nota(txt, sub, t, t_out, x=60, y=1520, rot=-3, w=420):
    i = nid("nt")
    OVR.append(f'<div id="{i}" class="nota" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({rot}deg)"><div class="nt">{txt}</div><div class="ns">{sub}</div></div>')
    J(f'tl.set("#{i}", {{opacity:0}}, 0); tl.fromTo("#{i}", {{y:80, opacity:0, rotation:{rot + 10}}}, {{y:0, opacity:1, rotation:{rot}, duration:0.5, ease:"back.out(2)", immediateRender:false}}, {t:.2f});')
    J(f'tl.to("#{i}", {{opacity:0, y:40, duration:0.25}}, {t_out:.2f});')
    FX.append(("posit", t + 0.2))

def rueda(i, valor, size, col):
    h = [f'<span class="rueda" id="{i}" style="font-size:{size}px;color:{col}">']
    k = 0
    for ch in valor:
        if ch.isdigit():
            strip = "".join(f"<span>{d}</span>" for d in list(range(10)) * 2)
            h.append(f'<span class="dg"><span class="st" id="{i}-{k}">{strip}</span></span>'); k += 1
        else:
            h.append(f'<span class="sep">{ch}</span>')
    return "".join(h) + '</span>', k
def gira(i, valor, t, d=1.0):
    k = 0
    n = sum(c.isdigit() for c in valor)
    for ch in valor:
        if ch.isdigit():
            J(f'tl.fromTo("#{i}-{k}", {{y:"0em"}}, {{y:"-{10 + int(ch)}em", duration:{d + 0.1 * (n - k):.2f}, ease:"power4.out", immediateRender:false}}, {t:.2f});')
            k += 1
    for s in range(int(d / 0.08)):
        if s % 2 == 0:
            FX.append(("clic", t + s * 0.08))

# --- transición: barrido diagonal con 3 franjas de color (con sonido bajito)
def barrido(t):
    J(f'tl.fromTo("#barr", {{x:-2600}}, {{x:2600, duration:0.8, ease:"power2.inOut", immediateRender:false}}, {t - 0.4:.2f});')
    FX.append(("suave", t - 0.4))
# --- calendario que arranca hojas
CAL = []
def calendario(t, dia, t_out):
    cid = nid("cal")
    OVR.append(f'<div class="cal" id="{cid}"><div class="calt">DÍA</div><div class="caln">{dia}</div><div class="cald">de 30</div><div class="hoja" id="{cid}-h"><div class="calt">DÍA</div><div class="caln">{dia - 1 if dia > 1 else "0"}</div></div></div>')
    J(f'tl.set("#{cid}", {{opacity:0}}, 0); tl.fromTo("#{cid}", {{y:-260, opacity:1, rotation:-8}}, {{y:0, rotation:-4, duration:0.5, ease:"back.out(1.8)", immediateRender:false}}, {t:.2f});')
    J(f'tl.fromTo("#{cid}-h", {{rotation:0, y:0, opacity:1}}, {{rotation:-35, y:520, x:-160, opacity:0, duration:0.7, ease:"power2.in", immediateRender:false}}, {t + 0.45:.2f});')
    J(f'tl.to("#{cid}", {{y:-300, opacity:0, duration:0.4, ease:"power2.in"}}, {t_out:.2f});')
    FX.append(("pagina", t + 0.45))

# ================================================================== E1: GANCHO — calle con tormenta, granizo desde el fotograma 0
f1e = FE(1)
calle = [
    '<rect x="0" y="0" width="1080" height="1920" fill="url(#cieloTorm)"/>',
    nube(240, 360, 1.5, "#4b4f7a"), nube(820, 300, 1.7, "#3f4370"), nube(560, 470, 1.3, "#5a5f8f"),
    '<path id="rayo1" d="M700,380 l-60,160 l50,0 l-70,190" stroke="#fff7c2" stroke-width="10" fill="none" opacity="0"/>',
    edificio(-40, 760, 360, 820, "#ff8a65", seed=1, toldo="#2fa36b", rotulo="PANADERÍA"),
    edificio(330, 640, 420, 940, "#ffd36e", "#b5543a", seed=2, toldo="#ef4a4a", rotulo="FARMACIA"),
    edificio(760, 720, 360, 860, "#7cc6e8", "#8b3b6b", seed=3),
    '<rect x="0" y="1580" width="1080" height="80" fill="#c9c4d6"/><rect x="0" y="1660" width="1080" height="260" fill="#4a4f66"/>',
    '<path d="M0,1780 L1080,1780" stroke="#ffffff" stroke-width="10" stroke-dasharray="70 50" opacity="0.6"/>',
    farola(60, 1600), farola(980, 1600), arbol(1000, 1600, 0.9),
    '<g id="suelo1" opacity="0"><path d="M0,1600 q270,-30 540,0 q270,-30 540,0 l0,60 l-1080,0 Z" fill="#ffffff"/></g>',
    coche("coche1", 610, 1530, RED, 1.25),
    f'<g id="p1w" transform="translate(150,1060) scale(0.34)">{persona("p1", paraguas=True)}</g>',
    '<g id="rebotes1">' + "".join(f'<circle class="reb" cx="{R.randint(20, 1060)}" cy="{R.randint(1590, 1700)}" r="{R.randint(5, 9)}" fill="{ICE}"/>' for _ in range(26)) + '</g>',
    granizo("g1", 110, seed=2),
]
escena("e1", "".join(calle))
mostrar("e1", 0, F(2) - 0.05, None)
caer("g1", 0, F(2), 0.9, 80)
J(f'tl.fromTo("#e1-cam", {{scale:1.6}}, {{scale:1.0, duration:1.6, ease:"power3.inOut", immediateRender:false}}, 0.5); tl.to("#e1-cam", {{scale:1.08, duration:{F(2) - 2.1:.2f}, ease:"sine.inOut"}}, 2.1);')
J('tl.set("#e1-cam", {transformOrigin:"760px 1500px", scale:1.6}, 0);')
FX.append(("golpe", 0.0)); FX.append(("granizo", 0.0))
# la primera piedra GIGANTE rompe el parabrisas en el fotograma 0
OVR.append('<svg id="piedraG" width="200" height="200" style="position:absolute;left:770px;top:-200px;overflow:visible;z-index:9"><circle cx="100" cy="100" r="70" fill="#f4fbff" stroke="#9fd2ee" stroke-width="6"/><circle cx="76" cy="76" r="22" fill="#fff"/><path d="M60,120 q40,20 80,-10" stroke="#cfe9f7" stroke-width="6" fill="none"/></svg>')
J('tl.fromTo("#piedraG", {y:-60}, {y:1580, duration:0.35, ease:"power2.in", immediateRender:false}, 0); tl.to("#piedraG", {y:1420, x:220, rotation:180, duration:0.45, ease:"power2.out"}, 0.35); tl.to("#piedraG", {opacity:0, duration:0.2}, 0.8);')
J('tl.set("#coche1 .grieta, #coche1 .abolla", {opacity:0}, 0); tl.to("#coche1 .grieta", {opacity:1, duration:0.05}, 0.33); tl.to("#coche1 .abolla", {opacity:1, duration:0.6}, 1.0);')
J('tl.fromTo("#e1-cam", {x:14}, {x:0, duration:0.4, ease:"elastic.out(1,0.3)", immediateRender:false}, 0.34);')
FX.append(("crack", 0.33))
J(f'tl.to("#suelo1", {{opacity:1, duration:{f1e:.2f}}}, 0.2);')
J(f'tl.fromTo(".reb", {{y:0}}, {{y:-26, duration:0.22, yoyo:true, repeat:{int(f1e / 0.22)}, stagger:0.05, ease:"power1.out", immediateRender:false}}, 0);')
J('tl.to("#rayo1", {opacity:1, duration:0.06, yoyo:true, repeat:3}, 2.2);'); FX.append(("trueno", 2.2))
vida("p1", 0, f1e)
brazo("p1", "R", 0.0, -8, -10)
J(f'tl.to("#p1-agujeros", {{opacity:1, duration:0.1}}, {P("seguidos") - 0.2:.2f});'); cara("p1", P("seguidos") - 0.2, "sorpresa"); FX.append(("pop", P("seguidos") - 0.2))
OVR.append('<div id="titulo"><div class="t1">¿Y SI GRANIZARA</div><div class="t2"><span>30</span> DÍAS SEGUIDOS?</div></div>')
J('tl.fromTo("#titulo .t1", {scale:1.25, y:-20}, {scale:1, y:0, duration:0.4, ease:"back.out(2)", immediateRender:false}, 0); tl.fromTo("#titulo .t2", {scale:1.25, y:20}, {scale:1, y:0, duration:0.4, ease:"back.out(2)", immediateRender:false}, 0.08);')
J(f'tl.to("#titulo", {{y:-8, duration:0.9, yoyo:true, repeat:{int(f1e / 0.9)}, ease:"sine.inOut"}}, 0.5); tl.to("#titulo", {{opacity:0, y:-120, duration:0.35}}, {F(2) - 0.4:.2f});')
punch("#titulo .t2 span", P("treinta"), 1.3)

# ================================================================== E2: la nube por dentro (frase 2)
f2 = F(2); barrido(f2)
loop_path = "M540,1350 C700,1150 700,800 560,640 C420,520 380,800 520,1000 C640,1160 640,820 540,700 C460,620 440,860 540,1150"
nube_body = (
    '<rect width="1080" height="1920" fill="url(#cieloAzul)"/>'
    '<path d="M60,1500 C40,1250 140,1080 260,1040 C240,860 380,720 520,740 C560,560 760,560 820,720 C980,720 1040,900 980,1040 C1080,1120 1080,1400 980,1500 Z" fill="#eef2fb"/>'
    '<path d="M120,560 L960,560 C900,520 760,500 540,500 C320,500 180,520 120,560 Z" fill="#dfe6f6"/>'
    '<path d="M260,560 C300,700 260,900 300,1040 M820,560 C780,700 820,900 780,1040" stroke="#c6d1ea" stroke-width="10" fill="none"/>'
    '<rect x="0" y="1500" width="1080" height="420" fill="#7ccf6a"/>'
    + "".join(edificio(x, 1680 - h, 90, h, c, seed=x) for x, h, c in ((80, 160, "#ff8a65"), (200, 220, "#ffd36e"), (320, 140, "#7cc6e8"), (760, 200, "#ff8a65"), (880, 170, "#c79bf2")))
    + f'<path id="lazo" d="{loop_path}" stroke="#2f7de1" stroke-width="8" fill="none" stroke-dasharray="20 16" opacity="0.65"/>'
    '<g id="flechasA">' + "".join(f'<path d="M{x},{y} l0,-120 l-26,30 M{x},{y - 120} l26,30" stroke="{RED}" stroke-width="14" fill="none" stroke-linecap="round"/>' for x, y in ((380, 1300), (700, 1250), (540, 1000))) + '</g>'
    '<text x="540" y="1440" text-anchor="middle" font-family="Inter" font-weight="900" font-size="44" fill="#d23c3c">AIRE CALIENTE QUE SUBE</text>'
    '<g id="piedraL"><circle id="pl1" r="16" fill="#ffffff" stroke="#9fd2ee" stroke-width="4"/><circle id="pl2" r="10" fill="none" stroke="#bfe3f7" stroke-width="3"/></g>'
    '<g id="corte" opacity="0"><circle cx="830" cy="980" r="150" fill="#ffffff" stroke="#1b2340" stroke-width="8"/>'
    + "".join(f'<circle cx="830" cy="980" r="{r}" fill="none" stroke="{c}" stroke-width="16"/>' for r, c in ((130, "#e8f5ff"), (104, "#cbe7fa"), (78, "#e8f5ff"), (52, "#cbe7fa"), (26, "#e8f5ff")))
    + '<text x="830" y="1170" text-anchor="middle" font-family="Inter" font-weight="900" font-size="38" fill="#1b2340">CAPAS DE HIELO</text></g>'
    '<g id="reloj2" opacity="0"><circle cx="200" cy="760" r="90" fill="#ffffff" stroke="#1b2340" stroke-width="10"/><path id="aguja2" d="M200,760 L200,690" stroke="#ef4a4a" stroke-width="10" stroke-linecap="round"/>'
    '<text x="200" y="900" text-anchor="middle" font-family="Inter" font-weight="900" font-size="40" fill="#1b2340">MINUTOS</text></g>')
escena("e2", nube_body, "#9ad3ff")
mostrar("e2", f2, F(3), 1.06)
J(f'tl.set("#piedraL", {{opacity:1}}, {f2:.2f}); tl.fromTo("#piedraL", {{motionPath:{{path:"#lazo", align:"#lazo", alignOrigin:[0.5,0.5]}}}}, {{duration:0.01}}, {f2:.2f});') if False else None
# la piedra recorre el lazo (posiciones calculadas a mano)
pts = [(540, 1350), (660, 1100), (600, 720), (450, 700), (500, 980), (610, 1060), (590, 780), (500, 760), (540, 1150), (540, 1700)]
seg = (FE(2) - f2 - 0.6) / (len(pts) - 1)
J(f'tl.set("#piedraL", {{x:{pts[0][0]}, y:{pts[0][1]}, scale:0.6}}, 0);')
for k, (x, y) in enumerate(pts[1:]):
    J(f'tl.to("#piedraL", {{x:{x}, y:{y}, scale:{0.6 + 0.25 * k:.2f}, duration:{seg:.2f}, ease:"sine.inOut"}}, {f2 + 0.3 + k * seg:.2f});')
J(f'tl.fromTo("#flechasA path", {{y:30, opacity:0.3}}, {{y:-30, opacity:1, duration:0.9, repeat:{int((FE(2) - f2) / 0.9)}, stagger:0.25, ease:"none", immediateRender:false}}, {f2:.2f});')
pop("#reloj2", P("minutos") - 0.2, 0.4)
J(f'tl.to("#aguja2", {{rotation:360, svgOrigin:"200 760", duration:1.4, ease:"power2.inOut"}}, {P("minutos"):.2f});')
pop("#corte", P("capas") - 0.1, 0.45); FX.append(("pop", P("capas")))
J(f'tl.fromTo("#corte circle", {{scale:0}}, {{scale:1, svgOrigin:"830 980", duration:0.5, stagger:0.08, ease:"back.out(2)", immediateRender:false}}, {P("capas"):.2f});')
FX.append(("baja", P("demasiado")))

# ================================================================== E3: día 1 — tejados que suenan y coches abollados
f3 = F(3); barrido(f3); calendario(f3 + 0.15, 1, P("amanecen") + 0.6)
fila_coches = "".join(coche(f"c3{k}", 40 + k * 260, 1580, c, 0.7) for k, c in enumerate((RED, YEL, BLUE, GRN)))
e3 = ('<rect width="1080" height="1920" fill="url(#cieloGris)"/>'
      + nube(300, 260, 1.4, "#8a90b4") + nube(860, 320, 1.6, "#7a80a8")
      + edificio(-20, 820, 340, 760, "#ff9f6e", seed=5, nieve=True) + edificio(330, 700, 400, 880, "#f7d36e", "#b5543a", seed=6, nieve=True)
      + edificio(740, 780, 360, 800, "#9ad0ea", "#8b3b6b", seed=7, nieve=True)
      + '<g id="notas3">' + "".join(f'<text class="tum" x="{x}" y="{y}" font-family="Inter" font-weight="900" font-size="42" fill="#ffffff" stroke="#1b2340" stroke-width="6" paint-order="stroke">TUM</text>' for x, y in ((120, 760), (480, 640), (860, 720), (300, 700))) + '</g>'
      + '<rect x="0" y="1580" width="1080" height="340" fill="#f4fbff"/><path d="M0,1580 q270,-26 540,0 q270,-26 540,0" fill="#ffffff"/>'
      + fila_coches + granizo("g3", 80, seed=3)
      + f'<g transform="translate(580,1180) scale(0.22)">{persona("p3")}</g>')
escena("e3", e3, "#b8c4dc")
mostrar("e3", f3, F(4), 1.08)
caer("g3", f3, F(4), 1.0, 50)
J(f'tl.fromTo(".tum", {{scale:0.4, opacity:0}}, {{scale:1.2, opacity:1, transformOrigin:"50% 50%", duration:0.25, yoyo:true, repeat:{int((FE(3) - f3) / 0.5)}, stagger:0.17, ease:"power2.out", immediateRender:false}}, {P("tambores") - 0.4:.2f}); tl.set(".tum", {{opacity:0}}, 0);')
for k in range(4):
    J(f'tl.set("#c3{k} .abolla", {{opacity:0}}, 0); tl.to("#c3{k} .abolla", {{opacity:1, duration:0.6}}, {P("abolladuras") - 0.6 + k * 0.15:.2f});')
    FX.append(("clic", P("abolladuras") - 0.5 + k * 0.15))
for k in range(6):
    FX.append(("tambor", P("tambores") - 0.3 + k * 0.32))
vida("p3", f3, F(4)); cara("p3", P("abolladuras"), "triste")

# ================================================================== E4: día 3 — el campo perdido
f4 = F(4); barrido(f4); calendario(f4 + 0.15, 3, P("perdido") + 0.6)
campo = ['<rect width="1080" height="1920" fill="url(#cieloGris)"/>', nube(200, 300, 1.4, "#7a80a8"), nube(800, 260, 1.6, "#6d7399"),
         '<path d="M0,900 C300,860 700,880 1080,840 L1080,1920 L0,1920 Z" fill="#7fbf5a"/>',
         '<path d="M0,1100 C300,1060 700,1080 1080,1040 L1080,1920 L0,1920 Z" fill="#5ea844"/>']
for fila in range(5):
    y = 1000 + fila * 170
    for k in range(7):
        x = 60 + k * 150 + (fila % 2) * 60
        campo.append(f'<g class="planta" transform="translate({x},{y}) scale({0.5 + fila * 0.12:.2f})"><rect x="-6" y="-80" width="12" height="80" fill="#6b4a2a"/>'
                     f'<circle class="hoja" cx="0" cy="-100" r="46" fill="#2f9e4f"/><circle class="hoja" cx="-34" cy="-80" r="30" fill="#36b35a"/><circle class="hoja" cx="34" cy="-80" r="30" fill="#36b35a"/>'
                     f'<circle class="fruta" cx="-14" cy="-94" r="10" fill="{RED}"/><circle class="fruta" cx="18" cy="-76" r="10" fill="{ORA}"/></g>')
campo.append('<g transform="translate(760,1180) scale(0.6)"><rect x="0" y="40" width="220" height="90" rx="12" fill="#ef4a4a"/><rect x="120" y="-20" width="90" height="70" rx="8" fill="#bfe3f7" stroke="#ef4a4a" stroke-width="10"/><circle cx="50" cy="140" r="45" fill="#1b1b22"/><circle cx="190" cy="140" r="30" fill="#1b1b22"/></g>')
campo.append(granizo("g4", 90, seed=4))
campo.append('<g id="ha4" opacity="0"><rect x="140" y="560" width="800" height="300" rx="36" fill="#ffffff" stroke="#1b2340" stroke-width="6"/>'
             '<foreignObject x="140" y="590" width="800" height="150"><div xmlns="http://www.w3.org/1999/xhtml" class="hanum">' + rueda("ha4n", "1.000.000", 110, NAVY)[0] + '</div></foreignObject>'
             '<text x="540" y="810" text-anchor="middle" font-family="Inter" font-weight="900" font-size="44" fill="#2f9e4f">HECTÁREAS DE CULTIVO</text></g>')
escena("e4", "".join(campo), "#9fb5c9")
mostrar("e4", f4, F(5), 1.06)
caer("g4", f4, F(5), 1.0, 50)
J(f'tl.to("#e4 .hoja", {{y:60, opacity:0.2, fill:"#8a7b3a", duration:1.2, stagger:0.01, ease:"power2.in"}}, {P("perdido") - 0.3:.2f});')
J(f'tl.to("#e4 .fruta", {{y:120, opacity:0, duration:0.8, stagger:0.01, ease:"bounce.out"}}, {P("perdido") - 0.1:.2f});')
FX.append(("baja", P("perdido")))
pop("#ha4", P("millon") - 0.4, 0.45)
gira("ha4n", "1.000.000", P("millon") - 0.3, 1.1)
nota("Fuente: Agroseguro", "tormentas en 2025", P("hectareas"), F(5) - 0.05, x=560, y=1520, rot=3, w=400)

# ================================================================== E5: supermercado — los precios se disparan
f5 = F(5); barrido(f5)
estante = ['<rect width="1080" height="1920" fill="#fff6e6"/>', '<rect x="0" y="0" width="1080" height="160" fill="#2fa36b"/>',
           '<text x="540" y="110" text-anchor="middle" font-family="Inter" font-weight="900" font-size="70" fill="#ffffff">FRUTA Y VERDURA</text>']
frutas = [RED, ORA, YEL, GRN, "#9b59b6"]
for fila in range(3):
    y = 520 + fila * 330
    estante.append(f'<rect x="40" y="{y + 150}" width="1000" height="26" fill="#c98a4b"/>')
    for k in range(4):
        x = 70 + k * 245
        estante.append(f'<g class="caja"><rect x="{x}" y="{y + 40}" width="210" height="110" rx="8" fill="#e0a868"/>'
                       + "".join(f'<circle class="fr" cx="{x + 30 + i * 38}" cy="{y + 40 - (i % 2) * 14}" r="22" fill="{frutas[(k + fila) % 5]}"/>' for i in range(5)) + '</g>')
        precio_id = f"pr{fila}{k}"
        estante.append(f'<g id="{precio_id}"><rect x="{x + 50}" y="{y + 186}" width="120" height="56" rx="8" fill="#ffe14a"/><text class="ptxt" x="{x + 110}" y="{y + 226}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="32" fill="#1b2340">1,20€</text></g>')
estante.append('<g id="flechaP" opacity="0"><path d="M880,1540 L880,1300 M820,1360 L880,1300 L940,1360" stroke="#ef4a4a" stroke-width="30" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>')
estante.append(f'<g transform="translate(120,1290) scale(0.26)">{persona("p5")}</g>')
estante.append('<g transform="translate(330,1640)"><path d="M0,0 L40,0 L80,150 L300,150 L340,40 L60,40" stroke="#5a6070" stroke-width="12" fill="none"/><circle cx="110" cy="180" r="20" fill="#2b3048"/><circle cx="280" cy="180" r="20" fill="#2b3048"/></g>')
escena("e5", "".join(estante), "#fff6e6")
mostrar("e5", f5, F(6), 1.07)
J(f'tl.to("#e5 .fr", {{opacity:0, scale:0, transformOrigin:"50% 50%", duration:0.3, stagger:0.02}}, {f5 + 0.4:.2f});')
precios = ["2,90€", "3,50€", "4,10€", "3,90€"]
for fila in range(3):
    for k in range(4):
        J(f'tl.to("#pr{fila}{k} .ptxt", {{textContent:"{precios[(fila + k) % 4]}", duration:0.01}}, {P("disparan") - 0.2 + 0.05 * (fila * 4 + k):.2f});') if False else None
        J(f'tl.set("#pr{fila}{k} text", {{attr:{{fill:"#ef4a4a"}}}}, {P("disparan") - 0.2 + 0.05 * (fila * 4 + k):.2f});')
        J(f'tl.fromTo("#pr{fila}{k}", {{scale:1.3}}, {{scale:1, transformOrigin:"50% 50%", duration:0.35, ease:"back.out(3)", immediateRender:false}}, {P("disparan") - 0.2 + 0.05 * (fila * 4 + k):.2f});')
pop("#flechaP", P("disparan") - 0.1, 0.4, "scale:0.3, opacity:0, y:120")
FX.append(("sube2", P("disparan") - 0.2))
vida("p5", f5, F(6)); cara("p5", P("precios"), "sorpresa")

# ================================================================== E6: una semana — claraboyas, placas solares y aviones en tierra
f6 = F(6); barrido(f6); calendario(f6 + 0.15, 7, P("claraboyas") + 0.2)
e6 = ['<rect width="1080" height="1920" fill="url(#cieloGris)"/>', nube(300, 220, 1.5, "#7a80a8"), nube(850, 260, 1.6, "#6d7399"),
      '<path d="M-20,900 L540,600 L1100,900 Z" fill="#c0533a"/><rect x="0" y="900" width="1080" height="420" fill="#ffcf7a"/>' + "".join(f'<rect x="{x}" y="960" width="120" height="140" rx="8" fill="#3f5f8c" stroke="#ffffff" stroke-width="10"/><rect x="{x - 10}" y="1100" width="140" height="16" fill="#ffffff"/><ellipse cx="{x + 30}" cy="1098" rx="26" ry="14" fill="#33b864"/>' for x in (80, 300, 700, 900)) + '<rect x="470" y="1080" width="140" height="240" rx="10" fill="#7a4b2a"/><circle cx="590" cy="1200" r="9" fill="#ffd34d"/>']
for k in range(5):
    x = 120 + k * 120 - (k * 4)
    e6.append(f'<g transform="translate({x},{820 - k * 55}) rotate(-28)"><rect width="110" height="70" fill="#1e3a6e" stroke="#c9d4e6" stroke-width="5"/>'
              f'<path d="M36,0 L36,70 M73,0 L73,70 M0,35 L110,35" stroke="#c9d4e6" stroke-width="3"/><path class="grietaS" d="M20,10 l20,20 l-8,10 l26,14 M55,8 l-10,24 l24,6" stroke="#ffffff" stroke-width="4" fill="none" opacity="0"/></g>')
e6.append('<g transform="translate(700,700) rotate(28)"><rect width="150" height="90" fill="#bfe3f7" stroke="#ffffff" stroke-width="8"/><path class="grietaS" d="M75,45 l-40,-30 M75,45 l40,-26 M75,45 l-30,40 M75,45 l46,30" stroke="#1b2340" stroke-width="4" fill="none" opacity="0"/></g>')
e6.append('<rect x="0" y="1320" width="1080" height="600" fill="#3b4256"/><path d="M0,1500 L1080,1500" stroke="#ffd34d" stroke-width="12" stroke-dasharray="80 60"/>')
e6.append('<g transform="translate(120,1380) scale(1.3)"><path d="M0,60 L420,60 Q470,60 470,80 Q470,100 420,100 L0,100 Q-20,80 0,60 Z" fill="#ffffff"/><path d="M200,70 L120,0 L170,0 L270,70 Z M200,90 L120,170 L170,170 L270,90 Z" fill="#dfe6f6"/><path d="M20,70 L0,20 L30,20 L60,70 Z" fill="#2f7de1"/>'
          + "".join(f'<circle cx="{60 + i * 34}" cy="74" r="7" fill="#9fc9ee"/>' for i in range(10)) + '</g>')
e6.append('<g id="panel6" opacity="0"><rect x="560" y="1560" width="470" height="300" rx="20" fill="#14182a" stroke="#ffd34d" stroke-width="6"/>'
          '<text x="795" y="1615" text-anchor="middle" font-family="Inter" font-weight="900" font-size="34" fill="#ffd34d">SALIDAS</text>'
          + "".join(f'<text x="590" y="{1675 + i * 58}" font-family="Courier" font-weight="700" font-size="30" fill="#ffffff">{c}</text><text class="canc" x="1000" y="{1675 + i * 58}" text-anchor="end" font-family="Inter" font-weight="900" font-size="28" fill="#ef4a4a">CANCELADO</text>' for i, c in enumerate(("MADRID", "PARÍS", "LONDRES", "ROMA"))) + '</g>')
e6.append(granizo("g6", 90, seed=6))
escena("e6", "".join(e6), "#9fb5c9")
mostrar("e6", f6, F(7), 1.06)
caer("g6", f6, F(7), 1.0, 50)
J(f'tl.to("#e6 .grietaS", {{opacity:1, duration:0.05, stagger:0.12}}, {P("claraboyas") - 0.1:.2f});')
for k in range(4):
    FX.append(("crack", P("claraboyas") - 0.1 + k * 0.2))
pop("#panel6", P("aviones") - 0.3, 0.4)
J(f'tl.fromTo("#e6 .canc", {{opacity:0, scaleY:0}}, {{opacity:1, scaleY:1, transformOrigin:"50% 50%", duration:0.2, stagger:0.12, immediateRender:false}}, {P("tierra") - 0.3:.2f}); tl.set("#e6 .canc", {{opacity:0}}, 0);')

# ================================================================== E7: tamaños y velocidad (frases 7 y 8)
f7 = F(7); barrido(f7)
tam = [("guisante", 0.6, "#7cc96a"), ("canica", 1.5, "#4aa3df"), ("golf", 4.3, "#ffffff"), ("tenis", 6.7, "#d7f04a"), ("pomelo", 11, "#ff9f5a"), ("récord", 20, ICE)]
e7 = ['<rect width="1080" height="1920" fill="url(#cieloAzul)"/>', '<rect x="0" y="1260" width="1080" height="660" fill="#f0e2c8"/>',
      '<rect x="60" y="1300" width="960" height="50" rx="8" fill="#ffd34d" stroke="#1b2340" stroke-width="4"/>'
      + "".join(f'<path d="M{80 + i * 44},{1300} l0,{24 if i % 5 else 40}" stroke="#1b2340" stroke-width="4"/>' for i in range(22))]
xcur = 90
for k, (nom, cm, col) in enumerate(tam):
    r = max(10, cm * 8.3)
    cx = xcur + r
    e7.append(f'<g class="bola" id="bola{k}"><circle cx="{cx:.0f}" cy="{1250 - r:.0f}" r="{r:.0f}" fill="{col}" stroke="#1b2340" stroke-width="4"/>'
              + (f'<circle cx="{cx - r * 0.3:.0f}" cy="{1250 - r * 1.3:.0f}" r="{r * 0.3:.0f}" fill="#ffffff" opacity="0.7"/>' if nom == "récord" else "")
              + f'<text x="{cx:.0f}" y="{1250 - 2 * r - 22 - (70 if k < 3 and k % 2 else 0):.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="30" fill="#1b2340" stroke="#ffffff" stroke-width="7" paint-order="stroke">{nom}</text>'
              f'<text x="{cx:.0f}" y="{1250 - 2 * r + 8 - (70 if k < 3 and k % 2 else 0):.0f}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="26" fill="#2f7de1" stroke="#ffffff" stroke-width="6" paint-order="stroke">{str(cm).replace(".", ",")} cm</text></g>')
    xcur = cx + r + (60 if cm < 5 else 26)
e7.append('<g id="velo7" opacity="0"><circle cx="540" cy="760" r="230" fill="#ffffff" stroke="#1b2340" stroke-width="12"/>'
          + "".join(f'<path d="M{540 + 190 * math.cos(math.radians(a)):.0f},{760 + 190 * math.sin(math.radians(a)):.0f} L{540 + 215 * math.cos(math.radians(a)):.0f},{760 + 215 * math.sin(math.radians(a)):.0f}" stroke="#1b2340" stroke-width="6"/>' for a in range(150, 391, 24))
          + '<path d="M370,890 A230,230 0 0 1 760,640" stroke="#ef4a4a" stroke-width="22" fill="none" opacity="0.85"/>'
          '<path id="aguja7" d="M540,760 L380,760" stroke="#1b2340" stroke-width="14" stroke-linecap="round"/><circle cx="540" cy="760" r="20" fill="#1b2340"/>'
          '<foreignObject x="300" y="800" width="480" height="140"><div xmlns="http://www.w3.org/1999/xhtml" class="velnum">' + rueda("vel7", "160", 100, RED)[0] + '<span class="kmh">km/h</span></div></foreignObject></g>')
e7.append('<g id="rec7" opacity="0"><rect x="120" y="560" width="840" height="300" rx="34" fill="#ffffff" stroke="#1b2340" stroke-width="6"/>'
          '<text x="540" y="640" text-anchor="middle" font-family="Inter" font-weight="900" font-size="46" fill="#2f7de1">RÉCORD · DAKOTA DEL SUR (2010)</text>'
          '<text x="540" y="760" text-anchor="middle" font-family="Inter" font-weight="900" font-size="110" fill="#1b2340">20 cm · 880 g</text>'
          '<text x="540" y="830" text-anchor="middle" font-family="Inter" font-weight="700" font-size="34" fill="#6b7385">casi un kilo de hielo</text></g>')
e7.append(f'<g transform="translate(860,980) scale(0.15)">{persona("p7")}</g>')
escena("e7", "".join(e7), "#9ad3ff")
mostrar("e7", f7, F(9), 1.05)
J(f'tl.fromTo("#e7 .bola", {{y:-900, opacity:1}}, {{y:0, duration:0.55, stagger:{max(0.25, (P("cambia") - f7) / 6):.2f}, ease:"bounce.out", immediateRender:false}}, {f7 + 0.2:.2f}); tl.set("#e7 .bola", {{opacity:0}}, 0);')
for k in range(6):
    FX.append(("golpe", f7 + 0.5 + k * max(0.25, (P("cambia") - f7) / 6)))
pop("#velo7", P("grandes") - 0.2, 0.45)
J(f'tl.fromTo("#aguja7", {{rotation:0}}, {{rotation:150, svgOrigin:"540 760", duration:1.2, ease:"power3.out", immediateRender:false}}, {P("ciento") - 0.2:.2f});')
gira("vel7", "160", P("ciento") - 0.2, 1.0)
J(f'tl.set(".velnum", {{opacity:0}}, 0); tl.set(".velnum", {{opacity:1}}, {P("ciento") - 0.2:.2f});')
FX.append(("riser", P("ciento") - 1.0))
J(f'tl.to("#velo7", {{opacity:0, y:-60, duration:0.3}}, {F(8) - 0.1:.2f});')
pop("#rec7", F(8), 0.45, "scale:1.6, opacity:0")
FX.append(("sello", F(8) + 0.1))
J(f'tl.fromTo("#bola5", {{scale:1}}, {{scale:1.15, transformOrigin:"50% 100%", duration:0.4, yoyo:true, repeat:3, ease:"sine.inOut", immediateRender:false}}, {P("veinte"):.2f});')
vida("p7", f7, F(9)); cara("p7", P("veinte"), "sorpresa")
nota("Fuente: NOAA (velocidad)", "y Servicio Meteorológico de EE. UU.", P("grandes"), F(9) - 0.05, x=60, y=1540, rot=-3, w=470)

# ================================================================== E8: dos semanas — el hielo se acumula y entierra la calle (frases 9 y 10)
f9 = F(9); barrido(f9); calendario(f9 + 0.15, 14, P("acumula") + 0.6)
e8 = ['<rect width="1080" height="1920" fill="url(#cieloGris)"/>', nube(300, 260, 1.5, "#7a80a8"), nube(860, 300, 1.6, "#6d7399"),
      edificio(-20, 700, 520, 1100, "#ff9f6e", seed=11, nieve=True),
      '<rect x="120" y="1500" width="160" height="300" rx="10" fill="#7a4b2a"/><circle cx="250" cy="1660" r="10" fill="#ffd34d"/>',
      edificio(520, 760, 580, 1040, "#9ad0ea", "#8b3b6b", seed=12, nieve=True),
      '<rect x="600" y="1060" width="360" height="70" rx="10" fill="#ffffff"/><text x="780" y="1108" text-anchor="middle" font-family="Inter" font-weight="900" font-size="40" fill="#1b2340">COLEGIO</text>',
      '<g id="cerrado" opacity="0"><rect x="640" y="1150" width="280" height="80" rx="12" fill="#ef4a4a" transform="rotate(-6 780 1190)"/><text x="780" y="1205" text-anchor="middle" font-family="Inter" font-weight="900" font-size="46" fill="#ffffff" transform="rotate(-6 780 1190)">CERRADO</text></g>',
      coche("c8", 560, 1640, YEL, 0.9),
      f'<g id="p8w" transform="translate(330,1188) scale(0.34)">{persona("p8")}</g>',
      '<g id="hielo8"><rect x="-20" y="1800" width="1120" height="400" fill="#f4fbff"/>'
      + "".join(f'<circle cx="{x}" cy="1800" r="{R.randint(18, 34)}" fill="#ffffff" stroke="#cfe9f7" stroke-width="3"/>' for x in range(0, 1100, 40)) + '</g>',
      '<g id="cinta8"><rect x="40" y="1250" width="60" height="560" fill="#ffd34d" stroke="#1b2340" stroke-width="4"/>'
      + "".join(f'<path d="M40,{1810 - i * 56} l{30 if i % 5 else 50},0" stroke="#1b2340" stroke-width="4"/>' for i in range(11))
      + '<text x="120" y="1250" font-family="Inter" font-weight="900" font-size="54" fill="#1b2340" stroke="#ffffff" stroke-width="8" paint-order="stroke">1 m</text></g>',
      granizo("g8", 90, seed=8)]
escena("e8", "".join(e8), "#9fb5c9")
mostrar("e8", f9, F(11), 1.06)
caer("g8", f9, F(11), 1.0, 50)
J(f'tl.to("#hielo8", {{y:-420, duration:{P("metro") - f9:.2f}, ease:"power1.inOut"}}, {f9 + 0.3:.2f});')
J(f'tl.to("#hielo8", {{y:-560, duration:{FE(10) - P("metro"):.2f}, ease:"power1.inOut"}}, {P("metro"):.2f});')
J(f'tl.to("#p8w", {{y:"-=370", duration:{P("metro") - f9:.2f}, ease:"power1.inOut"}}, {f9 + 0.3:.2f}); tl.to("#p8w", {{y:"-=150", duration:{FE(10) - P("metro"):.2f}, ease:"power1.inOut"}}, {P("metro"):.2f});')
J(f'tl.set("#cinta8", {{opacity:0}}, 0); tl.fromTo("#cinta8", {{opacity:0, y:120}}, {{opacity:1, y:0, duration:0.5, ease:"back.out(2)", immediateRender:false}}, {P("metro") - 0.4:.2f});')
FX.append(("sube", P("metro") - 0.3))
nota("Guadalajara (México),", "30 de junio de 2019", P("guadalajara"), F(10) - 0.05, x=560, y=1480, rot=3, w=420)
pop("#cerrado", P("colegios"), 0.4, "scale:2, opacity:0, rotation:-20"); FX.append(("sello", P("colegios")))
calendario(P("imagina") - 0.2, 30, P("bloqueadas"))
vida("p8", f9, F(11)); cara("p8", P("acumula"), "triste"); brazo("p8", "L", P("bloqueadas"), 40, -60); brazo("p8", "R", P("bloqueadas"), -40, 60)
FX.append(("golpe", P("enterrados")))

# ================================================================== E9: deshielo — las calles se convierten en ríos (frase 11)
f11 = F(11); barrido(f11)
e9 = ['<rect width="1080" height="1920" fill="url(#cieloSol)"/>', '<circle id="sol9" cx="880" cy="640" r="110" fill="#ffd34d"/>',
      edificio(-20, 700, 360, 1000, "#ff9f6e", seed=21), edificio(340, 620, 420, 1080, "#f7d36e", "#b5543a", seed=22), edificio(760, 700, 360, 1000, "#9ad0ea", "#8b3b6b", seed=23),
      '<g id="hielo9"><rect x="0" y="1360" width="1080" height="600" fill="#f4fbff"/></g>',
      '<g id="agua9" opacity="0"><rect x="0" y="1460" width="1080" height="500" fill="#3f9ad8"/>'
      + "".join(f'<path class="ola" d="M{x},{1480 + (x // 90 % 3) * 70} q30,-18 60,0 q30,18 60,0" stroke="#bfe3f7" stroke-width="6" fill="none"/>' for x in range(-60, 1100, 140)) + '</g>',
      f'<g id="coche9">{coche("c9", 300, 1430, RED, 0.9)}</g>',
      f'<g transform="translate(560,980) scale(0.26)">{persona("p9")}</g>',
      '<rect x="540" y="1440" width="300" height="20" fill="#5a3b26"/>']
escena("e9", "".join(e9), "#ffe2a8")
mostrar("e9", f11, F(12), 1.06)
J(f'tl.fromTo("#sol9", {{y:200, scale:0.6}}, {{y:0, scale:1, transformOrigin:"50% 50%", duration:1.0, ease:"power2.out", immediateRender:false}}, {P("para") - 0.4:.2f});')
J(f'tl.to("#hielo9", {{y:200, opacity:0, duration:1.4, ease:"power1.in"}}, {P("derrite") - 0.3:.2f});')
J(f'tl.to("#agua9", {{opacity:1, duration:0.8}}, {P("derrite"):.2f}); tl.fromTo(".ola", {{x:0}}, {{x:120, duration:{FE(11) - P("derrite") + 0.5:.2f}, ease:"none", immediateRender:false}}, {P("derrite"):.2f});')
J(f'tl.to("#coche9", {{x:340, y:-30, rotation:6, duration:{FE(11) - P("derrite") + 0.5:.2f}, ease:"sine.inOut"}}, {P("rios") - 0.6:.2f});')
FX.append(("agua", P("derrite")))
vida("p9", f11, F(12)); cara("p9", P("rios"), "sorpresa")

# ================================================================== E10: el dato final — hace falta calor (frase 12) y vuelta al principio (13)
f12 = F(12); barrido(f12)
e10 = ['<rect width="1080" height="1920" fill="url(#cieloSol)"/>', '<circle cx="160" cy="720" r="100" fill="#ffd34d"/>' + "".join(f'<path d="M{160 + 130 * math.cos(a):.0f},{720 + 130 * math.sin(a):.0f} L{160 + 170 * math.cos(a):.0f},{720 + 170 * math.sin(a):.0f}" stroke="#ffd34d" stroke-width="12" stroke-linecap="round"/>' for a in [i * math.pi / 6 for i in range(12)]),
       '<path d="M0,1500 C300,1460 700,1480 1080,1440 L1080,1920 L0,1920 Z" fill="#8fd16a"/>',
       '<g id="torre"><path d="M250,690 C330,620 470,600 600,600 C730,600 870,620 950,690 C870,680 760,700 700,720 L500,720 C440,700 330,680 250,690 Z" fill="#e6ecf8"/>'
       + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for x, y, r, c in ((600, 760, 110, "#f4f7fd"), (540, 880, 120, "#eef2fb"), (680, 900, 110, "#f4f7fd"), (470, 1020, 130, "#eef2fb"), (620, 1040, 140, "#f7f9fe"), (760, 1060, 110, "#eef2fb"), (420, 1170, 120, "#f4f7fd"), (560, 1200, 150, "#eef2fb"), (720, 1210, 140, "#f4f7fd"), (840, 1200, 100, "#eef2fb")))
       + '<path d="M360,1300 C400,1240 800,1240 860,1300 Z" fill="#c9d3ea"/></g>',
       '<g id="flechas10">' + "".join(f'<path d="M{x},1480 C{x - 20},1380 {x + 20},1300 {x},1220" stroke="{ORA}" stroke-width="18" fill="none" stroke-linecap="round"/><path d="M{x - 30},1250 L{x},1210 L{x + 30},1250" stroke="{ORA}" stroke-width="18" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' for x in (420, 580, 740)) + '</g>',
       '<g id="termo"><rect x="900" y="1000" width="60" height="380" rx="30" fill="#ffffff" stroke="#1b2340" stroke-width="6"/><rect id="mercurio" x="915" y="1360" width="30" height="0" rx="15" fill="#ef4a4a"/><circle cx="930" cy="1400" r="50" fill="#ef4a4a" stroke="#1b2340" stroke-width="6"/></g>',
       f'<g transform="translate(90,1170) scale(0.24)">{persona("p10")}</g>']
escena("e10", "".join(e10), "#ffe2a8")
mostrar("e10", f12, F(13) + 0.6, 1.06)
J(f'tl.to("#mercurio", {{attr:{{y:1040, height:340}}, duration:1.2, ease:"power2.out"}}, {P("calor") - 0.3:.2f});')
J(f'tl.fromTo("#flechas10 path", {{y:40, opacity:0.2}}, {{y:-60, opacity:1, duration:0.9, stagger:0.15, repeat:{int((FE(12) - f12) / 0.9)}, ease:"none", immediateRender:false}}, {P("caliente") - 0.3:.2f});')
J(f'tl.fromTo("#torre", {{scale:0.7}}, {{scale:1.15, transformOrigin:"600px 1300px", duration:{FE(12) - P("caliente"):.2f}, ease:"power2.out", immediateRender:false}}, {P("caliente"):.2f});')
FX.append(("sube2", P("caliente") - 0.2)); FX.append(("brillo", P("calor")))
vida("p10", f12, F(13) + 0.6); cara("p10", P("sabe"), "sorpresa")
# frase 13: vuelve la calle del principio (bucle) — la misma composición del fotograma 0
f13 = F(13)
J(f'tl.set("#e1", {{opacity:1}}, {f13 + 0.6:.2f}); tl.set("#e1-cam", {{scale:1.6, x:0}}, {f13 + 0.6:.2f});')
barrido(f13 + 0.6)
J(f'tl.set("#coche1 .grieta, #coche1 .abolla, #p1-agujeros, #suelo1", {{opacity:0}}, {f13 + 0.6:.2f}); tl.set("#p1-bocaO", {{opacity:0}}, {f13 + 0.6:.2f}); tl.set("#p1-boca", {{opacity:1}}, {f13 + 0.6:.2f});')
J(f'tl.set("#g1", {{opacity:0}}, {f13 + 0.6:.2f}); tl.set("#g1", {{opacity:1}}, {DUR - 0.25:.2f});')
J(f'tl.fromTo("#piedraG", {{y:-260, x:0, rotation:0, opacity:1}}, {{y:-60, duration:{DUR - f13 - 0.7:.2f}, ease:"power2.in", immediateRender:false}}, {f13 + 0.7:.2f});')
J(f'tl.to("#e1-cam", {{scale:1.6, duration:0.2}}, {f13 + 0.6:.2f});')
J(f'tl.set("#titulo", {{opacity:1, y:0}}, {DUR - 0.3:.2f});')

# ------------------------------------------------------------------ subtítulos (gris → blanco; lo importante con recuadro azul)
CLAVE = set(norm(w) for w in ["granizar", "treinta", "minutos", "capas", "blancas", "tambores", "abolladuras", "perdido", "millon", "hectareas",
                               "precios", "disparan", "claraboyas", "solares", "aviones", "ciento", "sesenta", "veinte", "kilo", "acumula",
                               "metro", "bloqueadas", "cerrados", "enterrados", "derrite", "rios", "calor", "caliente", "piedra"])
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
        J(f'tl.to("#{wid}", {{color:"#ffffff", fontWeight:800, duration:0.06}}, {p["ini"]:.2f});')
    SUBS.append(f'<div id="sub{k}" class="clip sub" data-start="{max(0, st):.3f}" data-duration="{max(0.2, en - max(0, st)):.3f}" data-track-index="3">{" ".join(spans)}</div>')

# grano
rr = random.Random(3)
for s in range(int(DUR / 0.08)):
    J(f'tl.set("#grano", {{backgroundPosition:"{rr.randint(0, 360)}px {rr.randint(0, 360)}px"}}, {s * 0.08:.2f});')

html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
@font-face{{font-family:"Caveat";src:url("assets/fonts/Caveat-700-latin.woff2") format("woff2");font-weight:700}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#1b2340}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif}}
.esc{{position:absolute;inset:0;overflow:hidden}}
.cam{{position:absolute;inset:0;transform-origin:50% 55%}}
.cam > svg, .esc svg.base{{position:absolute;left:0;top:0}}
.nota{{position:absolute;padding:22px 26px 20px;background:linear-gradient(160deg,#fff6a8,#ffe76b);box-shadow:0 18px 34px rgba(0,0,0,0.3);border-radius:4px;z-index:30}}
.nota::before{{content:"";position:absolute;left:38%;top:-16px;width:110px;height:34px;background:rgba(255,255,255,0.55);transform:rotate(-3deg)}}
.nt{{font:700 46px Caveat;color:#1f2a44;line-height:1.05}} .ns{{font:700 36px Caveat;color:#4a5570;line-height:1.05;margin-top:4px}}
.cal{{position:absolute;left:740px;top:520px;width:250px;height:250px;background:#ffffff;border-radius:22px;box-shadow:0 18px 40px rgba(0,0,0,0.35);text-align:center;z-index:25;overflow:visible}}
.cal::before{{content:"";position:absolute;left:0;right:0;top:0;height:64px;background:#ef4a4a;border-radius:22px 22px 0 0}}
.calt{{position:relative;margin-top:12px;font:900 34px Inter;color:#ffffff;letter-spacing:4px}}
.caln{{font:900 120px Inter;color:#1b2340;line-height:1.05}} .cald{{font:800 26px Inter;color:#8a90a4;margin-top:-8px}}
.hoja{{position:absolute;inset:0;background:#ffffff;border-radius:22px;transform-origin:50% 0}}
.hoja::before{{content:"";position:absolute;left:0;right:0;top:0;height:64px;background:#ef4a4a;border-radius:22px 22px 0 0}}
.hoja .calt{{position:relative}}
#titulo{{position:absolute;left:30px;right:30px;top:520px;text-align:center;z-index:20}}
#titulo .t1,#titulo .t2{{display:inline-block;padding:6px 28px 12px;font:900 92px Inter;letter-spacing:-3px;line-height:1.05;border-radius:24px;box-shadow:0 16px 40px rgba(0,0,0,0.35)}}
#titulo .t1{{background:#ffffff;color:#1b2340}} #titulo .t2{{background:#2f7de1;color:#ffffff;margin-top:14px}}
#titulo .t2 span{{display:inline-block;color:#ffd34d}}
.rueda{{display:inline-flex;align-items:baseline;font-weight:900;font-family:Inter;letter-spacing:-3px;font-variant-numeric:tabular-nums}}
.dg{{display:inline-block;height:1em;overflow:hidden;line-height:1em}} .st{{display:grid}} .st span{{height:1em;line-height:1em}} .sep{{display:inline-block;line-height:1em}}
.hanum{{text-align:center;line-height:1}} .velnum{{text-align:center;line-height:1}} .kmh{{font:900 44px Inter;color:#1b2340;margin-left:12px}}
#barr{{position:absolute;top:-400px;left:-600px;width:2000px;height:2800px;z-index:60;pointer-events:none;transform:skewX(-18deg);
  background:linear-gradient(90deg, transparent 0 18%, #2f7de1 18% 40%, #ffd34d 40% 60%, #ef4a4a 60% 82%, transparent 82%)}}
#grano{{position:absolute;inset:0;z-index:57;pointer-events:none;opacity:0.06;background:url(assets/grano.png);mix-blend-mode:multiply}}
#vineta{{position:absolute;inset:0;z-index:56;pointer-events:none;background:radial-gradient(110% 80% at 50% 50%, rgba(0,0,0,0) 60%, rgba(10,10,30,0.35))}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:560px;z-index:55;pointer-events:none;background:linear-gradient(rgba(12,16,34,0.72), rgba(12,16,34,0))}}
#marca{{position:absolute;left:0;right:0;top:1775px;text-align:center;font:700 28px Inter;color:#ffffff;opacity:0.32;pointer-events:none;z-index:61}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 64px Inter;color:rgba(255,255,255,0.45);line-height:1.22;text-shadow:0 3px 10px rgba(0,0,0,0.45)}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:4px solid #4ea3ff;border-radius:6px;background:rgba(78,163,255,0.2);opacity:0}}
.key b{{position:absolute;width:16px;height:16px;border-radius:50%;background:#fff;border:4px solid #4ea3ff;opacity:0}}
.key .d1{{left:-12px;top:-12px}} .key .d2{{right:-12px;bottom:-10px}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <svg width="0" height="0" style="position:absolute"><defs>
    <linearGradient id="cieloTorm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b2f5a"/><stop offset="0.6" stop-color="#5b5f9a"/><stop offset="1" stop-color="#8a8fc2"/></linearGradient>
    <linearGradient id="cieloGris" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#46507a"/><stop offset="1" stop-color="#a9b6d4"/></linearGradient>
    <linearGradient id="cieloAzul" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3f8ee8"/><stop offset="1" stop-color="#a8dcff"/></linearGradient>
    <linearGradient id="cieloSol" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff9f5a"/><stop offset="0.5" stop-color="#ffd38a"/><stop offset="1" stop-color="#fff1c8"/></linearGradient>
  </defs></svg>
  {"".join(f'<svg class="base" width="1080" height="1920" viewBox="0 0 1080 1920" style="display:none"></svg>' for _ in range(0))}
  {"".join(ESC).replace('<div class="cam"', '<div class="cam"').replace('"><svg', '"><svg')}
  <div id="topsombra"></div>
  {"".join(OVR)}
  <div id="barr"></div><div id="vineta"></div><div id="grano"></div>
  <div id="marca">@mundo.supuesto</div>
  <div id="subs" data-layout-allow-overlap>{"".join(SUBS)}</div>
  <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
tl.set("#barr", {{x:-2600}}, 0);
{chr(10).join(t for t in tl if t)}
tl.to({{}}, {{duration:0.01}}, {DUR - 0.01});
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>"""
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump(FX, open(os.path.join(BASE, "efectos.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones")

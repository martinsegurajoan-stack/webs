#!/usr/bin/env python3
"""«El efecto placebo del alcohol en una fiesta» — informativo, UN SOLO PLANO que sigue al protagonista por la fiesta
(barra del «bar de mentira» → pista de baile → salón). Personas de palo con tronco grueso (las del vídeo del tenis).
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
tl, FX, DEFS, OVR = [], [], [], []
def J(s): tl.append(s)
def fx(k, t): FX.append([k, round(t, 3)])
CY_, RJ, AM, VE, TX = "#4fd1ff", "#ff5a4f", "#ffc24a", "#35d987", "#eef4fb"
def cansancio(t): return 0.0
def entra(sel, t, frm="opacity:0, y:24", d=0.4, ease="power3.out"):
    J(f'tl.set("{sel}", {{opacity:0}}, 0); tl.fromTo("{sel}", {{{frm}}}, {{opacity:1, x:0, y:0, scale:1, duration:{d}, ease:"{ease}", immediateRender:false}}, {t:.2f});')
def sale(sel, t, d=0.3):
    J(f'tl.to("{sel}", {{opacity:0, duration:{d}, ease:"power1.in"}}, {t:.2f});')
exec(open(os.path.join(BASE, "_figuras.py"), encoding="utf-8").read())

# ------------------------------------------------------------------ posturas nuevas (de frente)
def Pz(**k):
    base = dict(head=(0, -91), neck=(0, -80), hip=(0, -48), eR=(12, -62), hR=(10, -50), eL=(-12, -62), hL=(-10, -50), tip=(10, -50),
                kR=(7, -24), fR=(9, 0), kL=(-7, -24), fL=(-9, 0))
    base.update(k); base["tip"] = base["hR"]; return base
POSES.update({
    "baile1": Pz(head=(0, -90), neck=(0, -79), hip=(0, -46), eR=(17, -92), hR=(22, -110), eL=(-15, -84), hL=(-18, -98), kR=(10, -23), fR=(14, 0), kL=(-8, -25), fL=(-12, 0)),
    "baile2": Pz(head=(5, -89), neck=(3, -79), hip=(2, -45), eR=(19, -70), hR=(12, -60), eL=(-16, -76), hL=(-22, -92), kR=(14, -21), fR=(16, 0), kL=(-6, -23), fL=(-12, 0)),
    "baile3": Pz(head=(-4, -89), neck=(-3, -79), hip=(-2, -45), eR=(14, -84), hR=(6, -96), eL=(-18, -70), hL=(-24, -80), kR=(8, -23), fR=(12, 0), kL=(-14, -21), fL=(-16, 0)),
    "hablar": Pz(eR=(17, -66), hR=(28, -76), eL=(-12, -66), hL=(-8, -76)),
    "reir": Pz(head=(2, -93), eR=(14, -60), hR=(6, -54), eL=(-12, -66), hL=(-8, -76)),
    "sorpresa": Pz(eR=(15, -88), hR=(8, -100), eL=(-15, -88), hL=(-8, -100)),
    "espejo": Pz(eR=(17, -60), hR=(8, -50), eL=(-14, -76), hL=(-6, -98)),
    "soplar": Pz(eR=(12, -72), hR=(3, -86), eL=(-12, -66), hL=(-8, -76)),
    "brazos": Pz(eR=(22, -76), hR=(40, -78), eL=(-22, -76), hL=(-40, -78)),
    "atrapar": Pz(eR=(16, -70), hR=(24, -84), eL=(-12, -66), hL=(-8, -76)),
    "pensar": Pz(eR=(12, -70), hR=(4, -84), eL=(-12, -66), hL=(-8, -76)),
    "beber2": Pz(eR=(12, -62), hR=(10, -50), eL=(-12, -76), hL=(-3, -92)),
    "servir": Pz(eR=(18, -76), hR=(30, -84), eL=(-12, -66), hL=(-16, -76)),
    "mostrar": Pz(eR=(18, -80), hR=(30, -96), eL=(-12, -62), hL=(-10, -50)),
    "nota": Pz(eR=(14, -84), hR=(18, -108), eL=(-12, -62), hL=(-10, -50)),
})
MANO_OBJ = {}                                   # objetos que siguen a una mano: pid -> [(id, mano)]
def pz(pid, nombre, t, d=0.2, ease="power2.out", solo=None):
    pose(pid, nombre, t, d, ease, slouch=0.0, solo=solo)
    if pid in MANO_OBJ and not solo:
        j = joints(POSES[nombre])
        for oid, mano in MANO_OBJ[pid]:
            J(f'tl.to("#{oid}", {{x:{j[mano][0]:.1f}, y:{j[mano][1]:.1f}, duration:{d}, ease:"{ease}"}}, {t:.3f});')
POS = {}
def coloca(pid, x, y, s, t=None, d=0.0, ease="power2.inOut"):
    if t is None:
        J(f'tl.set("#{pid}", {{svgOrigin:"0 0", x:{x:.1f}, y:{y:.1f}, scale:{s:.3f}}}, 0);')
    else:
        J(f'tl.to("#{pid}", {{x:{x:.1f}, y:{y:.1f}, scale:{s:.3f}, duration:{d:.3f}, ease:"{ease}"}}, {t:.3f});')
    POS[pid] = (x, y, s)
def anda(pid, x, t, d, y=None):
    x0, y0, s = POS[pid]
    y = y0 if y is None else y
    J(f'tl.to("#{pid}", {{x:{x:.1f}, y:{y:.1f}, duration:{d:.3f}, ease:"sine.inOut"}}, {t:.3f});')
    k, tt = 0, t
    while tt < t + d - 0.15:
        pz(pid, f"andar{1 + k % 2}", tt, 0.2, "sine.inOut")
        tt += 0.24; k += 1
    POS[pid] = (x, y, s)
BEAT = 60 / 124.0
def bailar(pid, t0, t1, cada=2, poses=("baile1", "baile2", "baile3", "baile2"), bote=True):
    k, t = 0, t0
    while t < t1 - 0.05:
        pz(pid, poses[k % len(poses)], t, BEAT * 0.6, "power2.out")
        t += BEAT * cada; k += 1
    if bote:
        n = max(1, int((t1 - t0) / BEAT))
        J(f'tl.fromTo("#{pid}_m", {{y:0}}, {{y:-5, duration:{BEAT / 2:.3f}, yoyo:true, repeat:{2 * n - 1}, ease:"sine.inOut", immediateRender:false}}, {t0:.3f});')
        J(f'tl.set("#{pid}_m", {{y:0}}, {t1:.3f});')

# ------------------------------------------------------------------ MUNDO (lateral; la cámara se mueve en horizontal)
W, SUELO = 2700, 1430
DEFS += [
    '<linearGradient id="pared" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a1d4a"/><stop offset="1" stop-color="#3d2a63"/></linearGradient>',
    '<linearGradient id="suelo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a2f2a"/><stop offset="1" stop-color="#2a1a18"/></linearGradient>',
    '<linearGradient id="barra" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8a5a36"/><stop offset="1" stop-color="#4e3020"/></linearGradient>',
    '<linearGradient id="cieloN" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a1230"/><stop offset="1" stop-color="#2a2f6a"/></linearGradient>',
    '<radialGradient id="glowM" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ff5ad8" stop-opacity="0.55"/><stop offset="1" stop-color="#ff5ad8" stop-opacity="0"/></radialGradient>',
    '<radialGradient id="glowC" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#4fd1ff" stop-opacity="0.5"/><stop offset="1" stop-color="#4fd1ff" stop-opacity="0"/></radialGradient>',
    '<radialGradient id="glowA" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffc24a" stop-opacity="0.6"/><stop offset="1" stop-color="#ffc24a" stop-opacity="0"/></radialGradient>',
    '<linearGradient id="cono" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0.35"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>',
    '<linearGradient id="espejoG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#bcd7ee"/><stop offset="0.5" stop-color="#7fa3c4"/><stop offset="1" stop-color="#c9e2f5"/></linearGradient>',
    '<linearGradient id="tonica" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eaf8ff" stop-opacity="0.8"/><stop offset="1" stop-color="#bfe6ff" stop-opacity="0.9"/></linearGradient>',
]
rw = random.Random(8)
mundo = []
mundo.append(f'<rect x="0" y="0" width="{W}" height="{SUELO}" fill="url(#pared)"/>')
# zócalo y tablas del suelo
mundo.append(f'<rect x="0" y="{SUELO}" width="{W}" height="{1920 - SUELO}" fill="url(#suelo)"/>')
for i in range(0, W, 120):
    mundo.append(f'<path d="M{i},{SUELO} L{i - 90},1920" stroke="#1d1110" stroke-width="2" opacity="0.5"/>')
for yy in (1500, 1600, 1730, 1880):
    mundo.append(f'<path d="M0,{yy} L{W},{yy}" stroke="#1d1110" stroke-width="2" opacity="0.35"/>')
mundo.append(f'<rect x="0" y="{SUELO - 16}" width="{W}" height="16" fill="#1d1430"/>')
# techo con viga y guirnalda de bombillas
mundo.append(f'<rect x="0" y="440" width="{W}" height="40" fill="#1a1230"/>')
gx = list(range(-20, W + 40, 70))
path = " ".join(f'{"M" if i == 0 else "L"}{x},{500 + 26 * math.sin(i * 0.9) ** 2:.0f}' for i, x in enumerate(gx))
mundo.append(f'<path d="{path}" stroke="#141020" stroke-width="3" fill="none"/>')
for i, x in enumerate(gx):
    y = 500 + 26 * math.sin(i * 0.9) ** 2
    c = ["#ffc24a", "#ff5ad8", "#4fd1ff", "#35d987"][i % 4]
    mundo.append(f'<circle class="bomb{i % 3}" cx="{x}" cy="{y + 10:.0f}" r="7" fill="{c}"/><circle class="bomb{i % 3}" cx="{x}" cy="{y + 10:.0f}" r="20" fill="{c}" opacity="0.25"/>')
# --- BARRA (izquierda): estanterías con botellas, neón, barra de madera
mundo.append('<rect x="110" y="760" width="680" height="400" rx="8" fill="#1d1430"/>')
for yy in (900, 1040):
    mundo.append(f'<rect x="120" y="{yy}" width="660" height="10" fill="#6b4a2e"/>')
botellas = []
for i, x in enumerate(range(150, 770, 52)):
    for fila, yy in enumerate((900, 1040)):
        tipo = rw.choice(["v", "v", "t", "g", "r"])
        col = {"v": "#dfeef8", "t": "#9fe0c0", "g": "#3fa66b", "r": "#b8202a"}[tipo]
        h = rw.randint(80, 108)
        botellas.append(f'<g transform="translate({x},{yy})"><rect x="-13" y="{-h}" width="26" height="{h}" rx="7" fill="{col}" opacity="0.88"/>'
                        f'<rect x="-6" y="{-h - 24}" width="12" height="26" rx="3" fill="{col}" opacity="0.88"/><rect x="-11" y="{-h * 0.62:.0f}" width="22" height="20" fill="#ffffff" opacity="0.75"/></g>')
mundo += botellas
mundo.append('<g transform="translate(450,690)"><rect x="-130" y="-48" width="260" height="96" rx="20" fill="none" stroke="#ff5ad8" stroke-width="7"/>'
             '<text x="0" y="22" text-anchor="middle" font-family="Inter" font-weight="900" font-size="62" fill="#ffd6f6" letter-spacing="8">BAR</text></g>')
mundo.append('<circle cx="450" cy="690" r="220" fill="url(#glowM)"/>')
# --- PISTA (centro): cabina del DJ, altavoces, bola de discoteca
mundo.append('<g transform="translate(1350,0)">'
             '<rect x="-170" y="1190" width="340" height="240" rx="10" fill="#141020"/><rect x="-170" y="1190" width="340" height="24" fill="#4fd1ff" opacity="0.7"/>'
             '<rect x="-120" y="1150" width="90" height="40" rx="6" fill="#2c3e5e"/><circle cx="-75" cy="1170" r="14" fill="#0b0f1a"/>'
             '<rect x="30" y="1150" width="90" height="40" rx="6" fill="#2c3e5e"/><circle cx="75" cy="1170" r="14" fill="#0b0f1a"/>'
             '<text x="0" y="1320" text-anchor="middle" font-family="Inter" font-weight="900" font-size="34" fill="#4fd1ff" letter-spacing="6">DJ</text></g>')
for x in (1120, 1580):
    mundo.append(f'<g transform="translate({x},{SUELO})"><rect x="-70" y="-300" width="140" height="300" rx="10" fill="#0e0b18"/>'
                 f'<circle class="alta" cx="0" cy="-200" r="46" fill="#1d1730" stroke="#3a3260" stroke-width="6"/><circle cx="0" cy="-90" r="34" fill="#1d1730" stroke="#3a3260" stroke-width="6"/></g>')
mundo.append('<path d="M1350,480 L1350,540" stroke="#141020" stroke-width="3"/>')
bola = "".join(f'<rect x="{-50 + c * 12}" y="{-50 + r * 12}" width="10" height="10" fill="{rw.choice(["#e6eef8", "#b9c9da", "#ffffff", "#8fa3c0"])}"/>' for r in range(9) for c in range(9) if (c - 4) ** 2 + (r - 4) ** 2 <= 18)
mundo.append(f'<g transform="translate(1350,592)"><g id="bolaD">{bola}</g><circle r="54" fill="none" stroke="#ffffff" stroke-width="2" opacity="0.4"/></g>')
for i, (x, c) in enumerate(((1000, "#ff5ad8"), (1350, "#4fd1ff"), (1700, "#ffc24a"))):
    mundo.append(f'<g transform="translate({x},480)"><g id="foco{i}"><path d="M0,0 L-170,950 L170,950 Z" fill="{c}" opacity="0.13"/></g><rect x="-22" y="-6" width="44" height="26" rx="5" fill="#141020"/></g>')
# baldosas iluminadas de la pista
for i in range(8):
    for j in range(3):
        x0 = 950 + i * 100 - j * 18
        mundo.append(f'<path class="bald{(i + j) % 3}" d="M{x0},{SUELO + 30 + j * 70} l92,0 l-12,62 l-92,0 Z" fill="{["#ff5ad8", "#4fd1ff", "#ffc24a"][(i + j) % 3]}" opacity="0.10"/>')
# --- SALÓN (derecha): ventana con ciudad, espejo, sofá, lámpara, planta
mundo.append('<rect x="1960" y="640" width="420" height="500" rx="10" fill="url(#cieloN)" stroke="#1a1230" stroke-width="14"/>')
for i in range(14):
    bx, bh = 1975 + i * 30, rw.randint(120, 330)
    mundo.append(f'<rect x="{bx}" y="{1140 - bh}" width="26" height="{bh}" fill="#141a3a"/>')
    for k in range(bh // 30):
        if rw.random() < 0.45:
            mundo.append(f'<rect x="{bx + 6}" y="{1140 - bh + 10 + k * 30}" width="6" height="8" fill="#ffd27a" opacity="0.8"/>')
mundo.append('<circle cx="2310" cy="720" r="30" fill="#f4f1e2"/><path d="M2170,640 L2170,1140 M1960,890 L2380,890" stroke="#1a1230" stroke-width="10"/>')
mundo.append('<g transform="translate(2540,960)"><ellipse rx="95" ry="170" fill="#c9a25a"/><ellipse rx="80" ry="155" fill="url(#espejoG)"/>'
             '<path d="M-40,-110 L20,-150 M-55,-60 L40,-120" stroke="#ffffff" stroke-width="6" opacity="0.5"/></g>')
mundo.append(f'<g transform="translate(2160,{SUELO})"><rect x="-230" y="-150" width="460" height="110" rx="30" fill="#7a3b6b"/><rect x="-250" y="-90" width="500" height="80" rx="24" fill="#93467f"/>'
             '<rect x="-270" y="-150" width="50" height="140" rx="20" fill="#7a3b6b"/><rect x="220" y="-150" width="50" height="140" rx="20" fill="#7a3b6b"/>'
             '<rect x="-230" y="-10" width="16" height="12" fill="#1d1430"/><rect x="214" y="-10" width="16" height="12" fill="#1d1430"/></g>')
mundo.append(f'<g transform="translate(1880,{SUELO})"><path d="M0,0 L0,-420" stroke="#c9b28a" stroke-width="6"/><path d="M-50,-420 L50,-420 L30,-490 L-30,-490 Z" fill="#ffd27a"/><circle cx="0" cy="-440" r="130" fill="url(#glowA)"/></g>')
mundo.append(f'<g transform="translate(2660,{SUELO})"><rect x="-34" y="-70" width="68" height="70" rx="8" fill="#6b4a2e"/>'
             + "".join(f'<path d="M0,-70 Q{dx},{-150 - abs(dx)} {dx * 1.6},{-200 + abs(dx) * 0.5}" stroke="#3fa66b" stroke-width="14" fill="none" stroke-linecap="round"/>' for dx in (-40, -15, 15, 40)) + '</g>')
# cinta en el suelo para la prueba de equilibrio (aparece luego)
mundo.append('<g id="cinta" opacity="0"><path d="M1960,1700 L2560,1700" stroke="#ffc24a" stroke-width="10" stroke-dasharray="40 14"/></g>')

# ------------------------------------------------------------------ PERSONAS
ROPA = ["#e2604a", "#35a3d9", "#7a5bd6", "#3fa66b", "#f08aa0", "#ffc24a", "#f2f4f7", "#1d1d24"]
PIEL = ["#f0c7a2", "#c68c63", "#8a5a3c", "#e6b28b"]
def traje(cam, short="#1d2433", piel=None, pelo="#1d1d24", cinta=None, zap="#f2f4f7"):
    return dict(piel=piel or rw.choice(PIEL), pelo=pelo, cam=cam, short=short, zap=zap, raq="none", cinta=cinta or pelo)
gente = []
# protagonista
PROTA = traje("#18c2a4", short="#1d2433", piel="#e6b28b", pelo="#3a2a20", zap="#ffc24a")
vaso = ('<g id="P_vaso"><g transform="translate(0,-6)"><path d="M-7,-14 L7,-14 L5.5,6 L-5.5,6 Z" fill="url(#tonica)" stroke="#ffffff" stroke-width="1.4"/>'
        '<circle cx="3" cy="-12" r="4" fill="#9be15d" stroke="#5a9a2a" stroke-width="1"/><circle cx="-2" cy="-4" r="1.2" fill="#fff"/><circle cx="1" cy="0" r="1" fill="#fff"/></g></g>')
gente.append(("P", figura("P", PROTA, "baile1", sudor=False, extra=vaso)))
MANO_OBJ["P"] = [("P_vaso", "hL")]
# investigador camarero (detrás de la barra) e investigadora (bata) que se mueve por la fiesta
gente.append(("R1", figura("R1", traje("#1d1d24", short="#1d1d24", pelo="#5a3a20"), "firme", sudor=False,
                           extra='<g id="R1_bot"><rect x="-7" y="-46" width="14" height="40" rx="5" fill="#dfeef8"/><rect x="-3" y="-60" width="6" height="16" fill="#dfeef8"/><rect x="-6" y="-34" width="12" height="10" fill="#ffffff"/></g>')))
MANO_OBJ["R1"] = [("R1_bot", "hR")]
gente.append(("R2", figura("R2", traje("#f4f8fc", short="#2c4566", piel="#c68c63", pelo="#1d1d24"), "firme", sudor=False,
                           extra='<g id="R2_obj"><g id="R2_alco" opacity="0"><rect x="-6" y="-22" width="12" height="22" rx="3" fill="#2c3e5e"/><rect x="-4" y="-18" width="8" height="6" fill="#35d987"/></g>'
                                 '<g id="R2_bot" opacity="0"><rect x="-7" y="-46" width="14" height="40" rx="5" fill="#dfeef8"/><rect x="-3" y="-60" width="6" height="16" fill="#dfeef8"/><rect x="-6" y="-34" width="12" height="10" fill="#ffffff"/></g>'
                                 '<g id="R2_regla" opacity="0"><rect x="-3" y="0" width="6" height="60" fill="#ffd27a" stroke="#8a6a2a" stroke-width="1"/></g></g>')))
MANO_OBJ["R2"] = [("R2_obj", "hR")]
# bailarines y gente de la fiesta
BAIL = []
for i, (x, y, s) in enumerate(((1000, 1560, 2.5), (1180, 1520, 2.35), (1500, 1530, 2.4), (1680, 1570, 2.55), (1420, 1600, 2.6), (880, 1520, 2.3))):
    pid = f"D{i}"
    gente.append((pid, figura(pid, traje(ROPA[i % len(ROPA)], short=rw.choice(["#1d2433", "#2c4566", "#3a2a20"]), pelo=rw.choice(["#1d1d24", "#3a2a20", "#7a4a2a", "#c9a25a"])), "baile1", sudor=False)))
    BAIL.append((pid, x, y, s))
gente.append(("C1", figura("C1", traje("#f08aa0", pelo="#7a4a2a"), "hablar", sudor=False)))
gente.append(("C2", figura("C2", traje("#3fa66b", pelo="#1d1d24"), "reir", sudor=False)))
gente.append(("S1", figura("S1", traje("#35a3d9", pelo="#c9a25a"), "sentado", sudor=False,
                           extra='<g id="S1_nota" opacity="0" transform="translate(18,-108)"><rect x="-14" y="-20" width="28" height="22" rx="3" fill="#fff"/><text x="0" y="-3" text-anchor="middle" font-family="Inter" font-weight="900" font-size="15" fill="#1d1d24">6</text></g>')))
gente.append(("S2", figura("S2", traje("#7a5bd6", pelo="#3a2a20"), "sentado", sudor=False,
                           extra='<g id="S2_nota" opacity="0" transform="translate(18,-108)"><rect x="-14" y="-20" width="28" height="22" rx="3" fill="#fff"/><text x="0" y="-3" text-anchor="middle" font-family="Inter" font-weight="900" font-size="15" fill="#1d1d24">6</text></g>')))

coloca("R1", 470, 1420, 2.5); pz("R1", "firme", 0, 0.01)
coloca("R2", 640, 1600, 2.7); pz("R2", "firme", 0, 0.01)
coloca("C1", 230, 1560, 2.45); coloca("C2", 330, 1580, 2.5)
J('tl.set("#C2_m", {svgOrigin:"0 0", scaleX:-1}, 0);')
coloca("S1", 2060, 1400, 2.3); coloca("S2", 2250, 1400, 2.3)
for pid, x, y, s in BAIL:
    coloca(pid, x, y, s)
PX0 = 1250
coloca("P", PX0, 1650, 3.1)

# ------------------------------------------------------------------ LUCES QUE SE MUEVEN (suaves, sin destellos)
J(f'tl.to("#bolaD", {{rotation:360, svgOrigin:"0 0", duration:{DUR:.2f}, ease:"none"}}, 0);')
for i in range(3):
    J(f'tl.fromTo("#foco{i}", {{rotation:{-14 + i * 6}, svgOrigin:"0 0"}}, {{rotation:{14 - i * 6}, svgOrigin:"0 0", duration:{2.6 + i * 0.7:.2f}, yoyo:true, repeat:{int(DUR / (2.6 + i * 0.7))}, ease:"sine.inOut", immediateRender:false}}, 0);')
for k in range(3):
    J(f'tl.fromTo(".bald{k}", {{opacity:0.08}}, {{opacity:0.32, duration:{BEAT * 2:.3f}, yoyo:true, repeat:{int(DUR / (BEAT * 2))}, ease:"sine.inOut", immediateRender:false}}, {k * BEAT * 0.66:.3f});')
    J(f'tl.fromTo(".bomb{k}", {{opacity:0.55}}, {{opacity:1, duration:{BEAT * 3:.3f}, yoyo:true, repeat:{int(DUR / (BEAT * 3))}, ease:"sine.inOut", immediateRender:false}}, {k * BEAT:.3f});')
J(f'tl.fromTo(".alta", {{scale:1, transformOrigin:"50% 50%"}}, {{scale:1.06, transformOrigin:"50% 50%", duration:{BEAT / 2:.3f}, yoyo:true, repeat:{int(DUR / (BEAT / 2))}, ease:"sine.inOut", immediateRender:false}}, 0);')

# la fiesta: bailarines y conversación de fondo, todo el vídeo
for i, (pid, x, y, s) in enumerate(BAIL):
    bailar(pid, i * 0.11, DUR, cada=4, poses=(["baile1", "baile2", "baile3", "baile2"][i % 4:] + ["baile1", "baile2", "baile3", "baile2"][:i % 4]))
for i, pid in enumerate(("C1", "C2")):
    t = i * 0.7
    while t < DUR - 1:
        pz(pid, ["hablar", "reir", "beber2", "firme"][int(t * 3 + i) % 4], t, 0.4, "sine.inOut")
        t += 2.4

# ------------------------------------------------------------------ GUION VISUAL (el protagonista P y la cámara)
CAM = []                                        # (t, x del centro) — la cámara sigue al protagonista
def cam(t, x, d=1.6):
    CAM.append((t, max(540, min(W - 540, x)), d))
cam(0, PX0, 0)
# 1-2) gancho: baila con el vaso, con 0,00 de alcohol
bailar("P", 0.0, F(3) - 0.3, cada=1)
# 3) camina a la barra (bar de mentira)
anda("P", 700, F(3) - 0.2, 2.6)
cam(F(3) - 0.2, 620, 2.6)
pz("P", "firme", F(3) + 2.5, 0.3)
# el camarero (investigador) coge la botella de «vodka» y sirve
pz("R1", "servir", P("botellas") - 0.3, 0.4)
pz("R1", "firme", FE(3), 0.4)
# 4) el borde del vaso y las gotas (lupa), y el primer trago
pz("P", "beber2", P("trago") - 0.2, 0.35)
pz("P", "firme", P("alcohol", 3) + 0.4, 0.4)
# 5) «estáis bebiendo vodka con tónica»
pz("R1", "hablar", F(5), 0.3); pz("R1", "firme", FE(5) + 0.2, 0.3)
# 6) vuelve a la pista: habla alto, se suelta, se ríe
anda("P", 1150, F(6) - 0.1, 2.2)
cam(F(6) - 0.1, 1150, 2.2)
pz("P", "hablar", P("alto", 2) - 0.2, 0.3)
bailar("P", P("sueltan") - 0.1, P("rien") - 0.1, cada=1)
pz("P", "reir", P("rien") - 0.1, 0.3)
J(f'tl.to("#P_h", {{rotation:-10, svgOrigin:"0 -91", duration:0.25, yoyo:true, repeat:5, ease:"sine.inOut"}}, {P("rien"):.2f});')
# 7) se mira al espejo (se ve más guapo); los «jueces» del sofá sacan un 6
anda("P", 2440, F(7) - 0.1, 3.0)
cam(F(7) - 0.1, 2160, 3.0)
pz("P", "espejo", P("atractivos") - 0.4, 0.4)
J(f'tl.to("#S1_nota, #S2_nota", {{opacity:1, duration:0.3}}, {P("jueces") - 0.1:.2f}); tl.to("#S1_nota, #S2_nota", {{opacity:0, duration:0.3}}, {FE(7) + 0.4:.2f});')
pz("S1", "nota", P("jueces") - 0.2, 0.3); pz("S2", "nota", P("jueces") - 0.1, 0.3)
pz("S1", "sentado", FE(7) + 0.3, 0.3); pz("S2", "sentado", FE(7) + 0.4, 0.3)
# 8) recuerdos falsos: piensa (bocadillo con las fotos del robo)
anda("P", 2260, F(8) - 0.1, 1.2)
pz("P", "pensar", F(8) + 1.2, 0.4)
# la investigadora cruza la fiesta por detrás hasta el salón
anda("R2", 2060, F(8), 6.5, y=1600)
# 9) alcoholímetro: sopla y marca 0,00
J(f'tl.to("#R2_alco", {{opacity:1, duration:0.2}}, {F(9) - 0.2:.2f}); tl.to("#R2_alco", {{opacity:0, duration:0.2}}, {FE(9) + 0.3:.2f});')
pz("R2", "dar", F(9) - 0.2, 0.3)
pz("P", "soplar", F(9) + 0.2, 0.3)
pz("P", "firme", FE(9) - 0.2, 0.3); pz("R2", "firme", FE(9) + 0.2, 0.3)
# 10-12) por qué pasa: expectativas, olor-música-vaso, excusa
pz("P", "pensar", F(10), 0.4)
bailar("P", F(11) + 0.2, FE(11), cada=2)
pz("P", "hablar", F(12), 0.3)
pz("P", "reir", P("permiso") - 0.1, 0.3)
pz("P", "firme", FE(12), 0.3)
# 13-14) reflejos: camina por la cinta y atrapa la regla
J(f'tl.to("#cinta", {{opacity:1, duration:0.4}}, {F(13):.2f}); tl.to("#cinta", {{opacity:0, duration:0.4}}, {FE(14) + 0.3:.2f});')
coloca("P", 1980, 1700, 3.1, F(13) - 0.1, 0.8)
pz("P", "brazos", F(13) + 0.6, 0.4)
J(f'tl.to("#P", {{x:2500, duration:3.0, ease:"none"}}, {F(13) + 1.0:.2f});')
k, tt = 0, F(13) + 1.0
while tt < F(13) + 3.9:
    pz("P", f"andar{1 + k % 2}", tt, 0.22, "sine.inOut", solo=PIERNAS); tt += 0.3; k += 1
POS["P"] = (2500, 1700, 3.1)
cam(F(13) - 0.1, 2240, 1.2)
# la regla: la investigadora la suelta y él la atrapa
coloca("R2", 2380, 1600, 2.7, F(14) - 0.6, 0.6)
pz("R2", "mostrar", F(14), 0.3)
J(f'tl.to("#R2_regla", {{opacity:1, duration:0.15}}, {F(14) + 0.2:.2f});')
pz("P", "atrapar", P("reaccion") - 0.1, 0.15, "power3.out")
J(f'tl.to("#R2_regla", {{y:"+=26", duration:0.12, ease:"power2.in"}}, {P("reaccion") - 0.2:.2f}); tl.to("#R2_regla", {{opacity:0, duration:0.2}}, {FE(14):.2f});')
pz("P", "firme", P("empeoran") + 0.2, 0.3)
pz("R2", "firme", P("empeoran") + 0.3, 0.3)
# 15) la verdad: la investigadora enseña la botella (solo tónica); él se lleva las manos a la cabeza
J(f'tl.to("#R2_bot", {{opacity:1, duration:0.2}}, {F(15) - 0.1:.2f}); tl.to("#R2_bot", {{opacity:0, duration:0.2}}, {FE(15) + 0.4:.2f});')
pz("R2", "mostrar", F(15), 0.3)
pz("P", "sorpresa", P("creerlo") - 0.5, 0.35)
pz("R2", "firme", FE(15) + 0.3, 0.3)
# 16-17) vuelve a la pista y sigue bailando (igual que en el fotograma 0)
coloca("P", 2500, 1650, 3.1, F(16) - 0.3, 0.4)
anda("P", PX0, F(16) + 0.1, 4.2, y=1650)
cam(F(16) + 0.1, PX0, 4.2)
bailar("P", F(16) + 4.4, DUR - 0.25, cada=1)
pz("P", "baile1", DUR - 0.25, 0.2)
# cámara
J(f'tl.set("#cam", {{x:{-(PX0 - 540)}}}, 0);')
for t, x, d in CAM[1:]:
    J(f'tl.to("#cam", {{x:{-(x - 540):.0f}, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.2f});')

# ------------------------------------------------------------------ MEDIDORES (lo que siente / alcohol en sangre)
SIENTE = [(0, 82), (F(3) - 0.2, 82), (F(3) + 0.8, 0), (P("trago"), 0), (P("trago") + 1.0, 18), (F(6), 25), (P("rien"), 70), (FE(8), 78),
          (F(9), 78), (FE(15) - 1.0, 78), (P("creerlo"), 35), (F(16) + 1.5, 45), (DUR - 2.0, 82), (DUR, 82)]
kf = [f'{{v:{b[1]}, duration:{max(0.01, b[0] - a[0]):.3f}, ease:"sine.inOut"}}' for a, b in zip(SIENTE, SIENTE[1:])]
J('const sv = {v:82};')
J(f'tl.to(sv, {{keyframes:[{",".join(kf)}], onUpdate:() => {{ document.getElementById("barS").style.width = sv.v + "%"; document.getElementById("numS").textContent = Math.round(sv.v) + "%"; }}}}, 0);')
J('document.getElementById("barS").style.width = "82%";')
J(f'tl.fromTo("#medA", {{boxShadow:"0 0 0px rgba(53,217,135,0)"}}, {{boxShadow:"0 0 26px rgba(53,217,135,0.9)", duration:0.4, yoyo:true, repeat:3, immediateRender:false}}, {P("cero") - 0.2:.2f});')

# ------------------------------------------------------------------ DATOS JUNTO AL PROTAGONISTA (coordenadas del mundo)
def chip(cid, x, y, html, t, hasta, cls="chip", desde="opacity:0, y:16"):
    OVR.append(f'<div id="{cid}" class="{cls}" style="left:{x}px;top:{y}px">{html}</div>')
    entra(f"#{cid}", t, desde)
    sale(f"#{cid}", hasta)
HOOK = f'<div id="hook" class="gran" style="left:{PX0 - 540}px"><b>0,00<i>g/L</i></b><small>DE ALCOHOL EN SU VASO</small></div>'
OVR.append(HOOK)
J('tl.set("#hook", {opacity:1}, 0);')
J(f'tl.to("#hook", {{opacity:0, scale:0.92, transformOrigin:"50% 50%", duration:0.35}}, {P("placebo") - 0.6:.2f});')
J(f'tl.fromTo("#hook", {{opacity:0, scale:1.06}}, {{opacity:1, scale:1, transformOrigin:"50% 50%", duration:0.6, ease:"power2.out", immediateRender:false}}, {DUR - 1.2:.2f});')
chip("cBorr", PX0 + 40, 1020, '<b>«VOY BORRACHO»</b>', P("jura") - 0.2, FE(1) + 0.1, cls="chip lite ama")
chip("cPlac", PX0 - 300, 1060, '<b>EFECTO PLACEBO</b><small>MEDIDO EN LABORATORIO</small>', P("placebo") - 0.2, FE(2) + 0.2)
chip("cBar", 170, 1180, '<b>BAR DE MENTIRA</b><small>MÚSICA · LUCES · BOTELLAS</small>', P("mentira") - 0.3, P("tonica") - 0.2)
chip("cTon", 560, 1100, '<b>«VODKA» = <span class="az">TÓNICA</span></b>', P("tonica") - 0.2, FE(3) + 0.3)
# lupa con el vaso: borde untado y gotas flotando
OVR.append('<div id="lupa" class="lupa" style="left:770px;top:880px"><svg viewBox="0 0 300 300" width="300" height="300">'
           '<circle cx="150" cy="150" r="140" fill="#140f24" stroke="#ffffff" stroke-width="6"/>'
           '<path d="M90,90 L210,90 L196,250 L104,250 Z" fill="url(#tonica)" stroke="#ffffff" stroke-width="4"/>'
           '<path id="lupaBorde" d="M90,90 L210,90" stroke="#ffc24a" stroke-width="9" stroke-linecap="round" opacity="0"/>'
           '<g id="lupaGotas" opacity="0"><ellipse cx="130" cy="104" rx="9" ry="4" fill="#fff4c2"/><ellipse cx="165" cy="108" rx="7" ry="3" fill="#fff4c2"/><ellipse cx="150" cy="100" rx="6" ry="3" fill="#fff4c2"/></g>'
           '<circle cx="182" cy="96" r="22" fill="#9be15d" stroke="#5a9a2a" stroke-width="3"/></svg>'
           '<small id="lupaT1">BORDE CON VODKA</small><small id="lupaT2">GOTAS ENCIMA</small></div>')
entra("#lupa", P("olfato") - 0.3, "opacity:0, scale:0.7")
J(f'tl.set("#lupaBorde, #lupaGotas, #lupaT1, #lupaT2", {{opacity:0}}, 0);')
J(f'tl.to("#lupaBorde, #lupaT1", {{opacity:1, duration:0.3}}, {P("borde") - 0.1:.2f}); tl.to("#lupaGotas, #lupaT2", {{opacity:1, duration:0.3}}, {P("gotas") - 0.1:.2f});')
sale("#lupa", P("trago") + 0.3)
chip("cHuele", 560, 1060, '<b>HUELE Y SABE A ALCOHOL</b>', P("huele") - 0.2, FE(4) + 0.2, cls="chip lite")
chip("cDicen", 170, 1180, '<b>«ESTÁIS BEBIENDO VODKA»</b>', P("mismo") - 0.2, FE(5) + 0.2, cls="chip lite ama")
chip("cNotan", 840, 1060, '<b>«YA LO NOTO»</b>', P("notan") - 0.3, FE(6), cls="chip lite ama")
chip("cAlto", 1250, 1180, '<b>+ VOLUMEN · + RISAS</b>', P("alto", 2) - 0.1, FE(6) + 0.2, cls="chip lite")
OVR.append('<div id="cGuapo" class="comp" style="left:1650px;top:1040px;width:760px">'
           '<div class="fila2"><small>ÉL SE PUNTÚA</small><div class="barra"><i id="barG1"></i></div><b class="az">★★★★★</b></div>'
           '<div class="fila2"><small>LOS JUECES</small><div class="barra"><i id="barG2" class="gris"></i></div><b>IGUAL</b></div></div>')
entra("#cGuapo", P("atractivos") - 0.5)
J(f'tl.fromTo("#barG1", {{width:"0%"}}, {{width:"92%", duration:0.8, ease:"power2.out", immediateRender:false}}, {P("atractivos") - 0.3:.2f});')
J(f'tl.fromTo("#barG2", {{width:"0%"}}, {{width:"55%", duration:0.8, ease:"power2.out", immediateRender:false}}, {P("jueces"):.2f});')
sale("#cGuapo", FE(7) + 0.2)
chip("cFrancia", 1700, 960, '<b>ESTUDIO EN FRANCIA</b>', P("francia") - 0.2, P("atractivos") - 0.6, cls="chip lite")
# bocadillo de pensamiento con las fotos del robo y el dato falso
OVR.append('<div id="bocata" class="bocata" style="left:1900px;top:880px">'
           '<div class="fotos"><i class="f1">👤💼</i><i class="f2">🏃</i><i id="fFalso" class="f3">🧢</i></div>'
           '<small id="falsoT">DATO FALSO</small></div>')
entra("#bocata", P("fotos") - 0.3, "opacity:0, scale:0.8")
J(f'tl.set("#fFalso, #falsoT", {{opacity:0}}, 0); tl.to("#fFalso, #falsoT", {{opacity:1, duration:0.3}}, {P("falsos") - 0.2:.2f});')
sale("#bocata", FE(8) + 0.1)
chip("cFalsos", 1820, 1180, '<b class="rojo">MÁS RECUERDOS FALSOS</b><small>Y MÁS SEGUROS DE ELLOS</small>', P("creyeron") - 0.3, FE(8) + 0.2)
OVR.append(f'<div id="cCero" class="gran2" style="left:1700px;top:1020px"><b>0,00</b><small>ALCOHOLÍMETRO</small></div>')
entra("#cCero", P("cero") - 0.3, "opacity:0, scale:0.8")
sale("#cCero", FE(9) + 0.4)
chip("cExp", 1760, 1060, '<b>EXPECTATIVA → EFECTO</b><small>EL CEREBRO PREDICE</small>', P("espera") - 0.6, FE(10) + 0.2)
chip("cOlor", 1700, 1060, '<b>👃 OLOR + 🎵 MÚSICA + 🥃 VASO</b><small>= SOLTARSE</small>', P("olor") - 0.3, FE(11) + 0.2)
chip("cExc", 1760, 1060, '<b>EXCUSA PERFECTA</b><small>«HA SIDO EL ALCOHOL»</small>', P("excusa") - 0.3, P("permiso") - 0.2)
chip("cPerm", 1760, 1060, '<b class="az">PERMISO PARA SOLTARSE</b>', P("permiso") - 0.2, FE(12) + 0.2)
chip("cRefl", 1950, 1060, '<b>LOS REFLEJOS</b><small>NO SE PUEDEN FINGIR</small>', P("reflejos") - 0.3, F(14) + 0.3, cls="chip ama")
OVR.append('<div id="cComp" class="comp" style="left:1720px;top:1020px;width:800px">'
           '<div class="fila2"><small>SOLO CREE QUE BEBE</small><div class="barra"><i id="barC1" class="verde"></i></div><b class="verde2">CASI IGUAL</b></div>'
           '<div class="fila2"><small>ALCOHOL DE VERDAD</small><div class="barra"><i id="barC2" class="rojo"></i></div><b class="rojo">MÁS LENTO</b></div></div>')
entra("#cComp", P("empeoran") - 0.6)
J(f'tl.fromTo("#barC1", {{width:"0%"}}, {{width:"90%", duration:0.8, ease:"power2.out", immediateRender:false}}, {P("empeoran") - 0.4:.2f});')
J(f'tl.fromTo("#barC2", {{width:"0%"}}, {{width:"48%", duration:0.8, ease:"power2.out", immediateRender:false}}, {P("frena") - 0.2:.2f});')
sale("#cComp", FE(14) + 0.3)
chip("cVerdad", 1900, 1060, '<b>SOLO ERA TÓNICA</b><small>A MUCHOS LES CUESTA CREERLO</small>', P("verdad", 2) - 0.2, FE(15) + 0.3, cls="chip ama")
chip("cCabeza", 1480, 1060, '<b>NO SALE DEL VASO</b><small class="am">SALE DE TU CABEZA</small>', P("vaso", 4) - 0.6, FE(16) + 0.3)

# ------------------------------------------------------------------ ensamblar SVG
svg_gente = "".join(g for pid, g in sorted(gente, key=lambda g: POS.get(g[0], (0, 0, 0))[1]))
# el camarero va detrás de la barra (se dibuja antes que la barra)
r1 = [g for pid, g in gente if pid == "R1"][0]
svg_gente = svg_gente.replace(r1, "")
barra = (f'<rect x="120" y="1240" width="700" height="{SUELO - 1240 + 30}" rx="8" fill="url(#barra)"/><rect x="100" y="1222" width="740" height="30" rx="6" fill="#a8744a"/>'
         + "".join(f'<rect x="{x}" y="1260" width="6" height="{SUELO - 1260}" fill="#3a2418" opacity="0.5"/>' for x in range(170, 800, 80))
         + '<g transform="translate(300,1222)"><path d="M-10,-30 L10,-30 L8,0 L-8,0 Z" fill="url(#tonica)" stroke="#fff" stroke-width="1.5"/></g>'
         + '<g transform="translate(560,1222)"><rect x="-12" y="-64" width="24" height="64" rx="7" fill="#dfeef8"/><rect x="-5" y="-84" width="10" height="22" fill="#dfeef8"/><rect x="-10" y="-44" width="20" height="16" fill="#fff"/><text x="0" y="-32" text-anchor="middle" font-family="Inter" font-weight="900" font-size="7" fill="#1d1d24">VODKA</text></g>'
         + '<g transform="translate(650,1222)"><path d="M-14,-10 Q0,-26 14,-10 Z" fill="#9be15d"/></g>')
svg = f'<g id="mundo">{"".join(mundo)}{r1}{barra}{svg_gente}</g>'

_S = open(os.path.join(BASE, "_subs.py"), encoding="utf-8").read()
exec(re.sub(r"CLAVE = set\(.*?\]\)", lambda m: 'CLAVE = set(norm(w) for w in ["borracho", "gota", "placebo", "laboratorio", "mentira", "vodka", "tonica", "olfato", "borde", "gotas", "huele", "sabe", "notan", "alto", "rien", "francia", "atractivos", "jueces", "robo", "falsos", "seguridad", "cero", "sangre", "espera", "olor", "musica", "vaso", "soltarse", "excusa", "permiso", "reflejos", "equilibrio", "reaccion", "empeoran", "frena", "verdad", "creerlo", "cabeza", "bailando"])', _S, count=1, flags=re.S))

html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#0a0716}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;background:#0a0716;color:{TX}}}
#cam{{position:absolute;left:0;top:0;width:{W}px;height:1920px}}
.gran{{position:absolute;width:1080px;top:1060px;text-align:center;white-space:nowrap;text-shadow:0 6px 24px rgba(0,0,0,0.7)}}
.gran b{{display:block;font:900 190px/1 Inter;letter-spacing:-6px;color:#fff;font-variant-numeric:tabular-nums}} .gran b i{{font-style:normal;font-size:64px;letter-spacing:0;margin-left:14px;color:{VE}}}
.gran small{{display:inline-block;margin-top:12px;padding:8px 20px;border-radius:12px;background:rgba(10,6,22,0.7);font:800 32px Inter;letter-spacing:6px;color:#fff}}
.gran2{{position:absolute;text-align:center;padding:16px 30px;border-radius:20px;background:rgba(10,6,22,0.8);border:2px solid {VE}}} .gran2 b{{display:block;font:900 140px/1 Inter;color:{VE};font-variant-numeric:tabular-nums}} .gran2 small{{font:800 22px Inter;letter-spacing:5px;color:#d9f7e8}}
.chip{{position:absolute;display:flex;align-items:center;gap:14px;padding:12px 20px;border-radius:16px;background:rgba(10,6,22,0.8);border:1px solid rgba(255,255,255,0.22);white-space:nowrap;box-shadow:0 8px 24px rgba(0,0,0,0.35)}}
.chip b{{display:block;font:800 48px/1 Inter;color:#fff}} .chip small{{display:block;margin-top:5px;font:800 18px Inter;letter-spacing:4px;color:#c9b9e6}}
.chip.ama{{border-left:6px solid {AM}}} .chip.lite b{{font-size:34px}} .chip small.am{{color:{AM};font-size:26px}}
.rojo{{color:{RJ} !important}} .az{{color:{CY_} !important}} .verde2{{color:{VE} !important}}
.comp{{position:absolute;padding:18px 24px;border-radius:18px;background:rgba(10,6,22,0.82);border:1px solid rgba(255,255,255,0.2)}}
.fila2{{display:grid;grid-template-columns:250px 1fr 240px;align-items:center;gap:14px;margin:8px 0}} .fila2 small{{font:800 18px Inter;letter-spacing:3px;color:#c9b9e6}} .fila2 b{{font:900 32px Inter;color:#fff;text-align:right}}
.barra{{height:22px;border-radius:11px;background:rgba(255,255,255,0.12);overflow:hidden}} .barra i{{display:block;height:100%;width:0;background:{CY_};border-radius:11px}} .barra i.rojo{{background:{RJ}}} .barra i.gris{{background:#9fb3c8}} .barra i.verde{{background:{VE}}}
.lupa{{position:absolute;width:300px;text-align:center}} .lupa small{{display:block;margin-top:6px;font:800 22px Inter;letter-spacing:3px;color:{AM}}}
.bocata{{position:absolute;padding:20px 26px;border-radius:40px;background:rgba(255,255,255,0.94);text-align:center;box-shadow:0 10px 30px rgba(0,0,0,0.4)}}
.bocata:after{{content:"";position:absolute;left:170px;bottom:-34px;width:30px;height:30px;border-radius:50%;background:rgba(255,255,255,0.94)}}
.fotos{{display:flex;gap:14px}} .fotos i{{display:block;font-style:normal;font-size:52px;width:110px;height:100px;line-height:100px;background:#e9e2cf;border:6px solid #fff;box-shadow:0 4px 10px rgba(0,0,0,0.3)}}
.fotos i.f3{{outline:5px solid {RJ}}} .bocata small{{display:block;margin-top:10px;font:900 24px Inter;letter-spacing:4px;color:{RJ}}}
#meds{{position:absolute;right:36px;top:500px;z-index:60;width:430px;padding:12px 16px;border-radius:14px;background:rgba(10,6,22,0.85);border:1px solid rgba(255,255,255,0.18)}}
#meds small{{display:flex;justify-content:space-between;font:800 15px Inter;letter-spacing:3px;color:#c9b9e6}} #meds small b{{font:900 20px Inter;color:#fff;letter-spacing:0}}
.med{{height:16px;border-radius:8px;background:rgba(255,255,255,0.12);overflow:hidden;margin:6px 0 10px}} #barS{{height:100%;width:82%;background:linear-gradient(90deg,{AM},{RJ});border-radius:8px}}
#medA{{border-radius:8px}} #medA b{{color:{VE} !important}}
#grano{{position:absolute;inset:0;z-index:57;pointer-events:none;opacity:0.035;background:url(assets/grano.png);mix-blend-mode:overlay}}
#vineta{{position:absolute;inset:0;z-index:56;pointer-events:none;background:radial-gradient(115% 85% at 50% 58%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.5))}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:520px;z-index:55;pointer-events:none;background:linear-gradient(rgba(6,3,14,0.85), rgba(6,3,14,0))}}
#marca{{position:absolute;left:0;right:0;top:1775px;text-align:center;font:700 28px Inter;color:#ffffff;opacity:0.32;pointer-events:none;z-index:61}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 62px Inter;color:rgba(255,255,255,0.42);line-height:1.22;text-shadow:0 3px 12px rgba(0,0,0,0.6)}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:3px solid #4ea3ff;border-radius:6px;background:rgba(78,163,255,0.18);opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="cam"><svg width="{W}" height="1920" viewBox="0 0 {W} 1920" style="position:absolute;left:0;top:0;overflow:visible"><defs>{"".join(DEFS)}</defs>{svg}</svg>
  {"".join(OVR)}</div>
  <div id="topsombra"></div><div id="vineta"></div><div id="grano"></div>
  <div id="meds"><small>LO QUE SIENTE <b id="numS">82%</b></small><div class="med"><div id="barS"></div></div>
    <div id="medA"><small>ALCOHOL EN SANGRE <b>0,00 g/L</b></small></div></div>
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
json.dump([[0, 0.45], [DUR, 0.45]], open(os.path.join(BASE, "ambiente.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones")

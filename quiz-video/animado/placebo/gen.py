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
mundo.append('<g id="cinta" opacity="0"><path d="M1960,1700 L2230,1700" stroke="#35d987" stroke-width="10" stroke-dasharray="40 14"/></g>')

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

# ------------------------------------------------------------------ v2: EDICIÓN DINÁMICA (zooms, barridos, textos que golpean)
FXL = []                                        # capa de efectos en pantalla (fuera de la cámara)
def slam(cid, html, t, hasta, y=1000, cls="slam", rot=-3, son="golpe"):
    FXL.append(f'<div id="{cid}" class="{cls}" style="top:{y}px">{html}</div>')
    J(f'tl.set("#{cid}", {{opacity:0}}, 0); tl.fromTo("#{cid}", {{opacity:0, scale:2.3, rotation:{rot * 2}}}, {{opacity:1, scale:1, rotation:{rot}, duration:0.32, ease:"back.out(2.2)", immediateRender:false}}, {t:.2f});')
    J(f'tl.to("#{cid}", {{opacity:0, scale:1.25, duration:0.22, ease:"power2.in"}}, {hasta:.2f});')
    if son:
        fx(son, t)
def burbuja(cid, html, t, hasta, x, y, cola="izq"):
    FXL.append(f'<div id="{cid}" class="bubble {cola}" style="left:{x}px;top:{y}px">{html}</div>')
    J(f'tl.set("#{cid}", {{opacity:0}}, 0); tl.fromTo("#{cid}", {{opacity:0, scale:0.4, y:30}}, {{opacity:1, scale:1, y:0, duration:0.35, ease:"back.out(2)", immediateRender:false}}, {t:.2f});')
    J(f'tl.to("#{cid}", {{opacity:0, scale:0.8, duration:0.2}}, {hasta:.2f});')
    fx("pop", t)
CAMS = []
def plano(t, cx, cy, z, d=0.55, ease="power3.inOut", barrido=False):
    z = max(1.0, z)
    x = min(0, max(1080 - W * z, 540 - cx * z)); y = min(0, max(1920 - 1920 * z, 960 - cy * z))
    if d == 0:
        J(f'tl.set("#cam", {{x:{x:.0f}, y:{y:.0f}, scale:{z:.3f}}}, {t:.2f});')
    else:
        J(f'tl.to("#cam", {{x:{x:.0f}, y:{y:.0f}, scale:{z:.3f}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
    if barrido:
        J(f'tl.to("#shake", {{filter:"blur(14px)", duration:{d * 0.45:.2f}, ease:"power2.in"}}, {t:.2f}); tl.to("#shake", {{filter:"blur(0px)", duration:{d * 0.55:.2f}, ease:"power2.out"}}, {t + d * 0.45:.2f});')
        fx("whoosh", t)
def golpe_cam(t, f=14):
    J(f'tl.fromTo("#imp", {{x:0, y:0}}, {{keyframes:[{{x:{f}, y:{-f * 0.6:.0f}, duration:0.05}}, {{x:{-f * 0.8:.0f}, y:{f * 0.5:.0f}, duration:0.05}}, {{x:{f * 0.5:.0f}, y:{f * 0.3:.0f}, duration:0.05}}, {{x:0, y:0, duration:0.08}}], immediateRender:false}}, {t:.2f});')
def boca(t, tipo):
    for m in ("son", "ris", "o", "pla"):
        J(f'tl.set("#P_{m}", {{opacity:{1 if m == tipo else 0}}}, {t:.2f});')
def teleporta(pid, x, y, s, t):
    J(f'tl.set("#{pid}", {{x:{x}, y:{y}, scale:{s}}}, {t:.2f});'); POS[pid] = (x, y, s)
HEADY = 1650 - 3.1 * 90
def face(x): return (x, HEADY + 40, 2.3)

# cara del protagonista (ojos y bocas que cambian)
CARA = ('<circle cx="-3.2" cy="-90.6" r="1.15" fill="#1d1d24"/><circle cx="3.2" cy="-90.6" r="1.15" fill="#1d1d24"/>'
        '<path id="P_son" d="M-3.6,-86.6 Q0,-83.4 3.6,-86.6" stroke="#5a1d1d" stroke-width="1.3" fill="none" stroke-linecap="round"/>'
        '<path id="P_ris" d="M-4,-87.2 Q0,-80.6 4,-87.2 Z" fill="#5a1d1d" opacity="0"/>'
        '<ellipse id="P_o" cx="0" cy="-85.6" rx="1.8" ry="2.5" fill="#5a1d1d" opacity="0"/>'
        '<path id="P_pla" d="M-3,-86 L3,-86" stroke="#5a1d1d" stroke-width="1.3" opacity="0"/>'
        '<g id="P_esp" opacity="0">' + "".join(f'<path d="M{12 * math.cos(a):.1f},{-104 + 4 * math.sin(a):.1f} q2,-3 4,0" stroke="#ffc24a" stroke-width="1.2" fill="none"/>' for a in (0, 2.1, 4.2)) +
        '<g id="P_espiral"><path d="M0,-108 m-6,0 a6,4 0 1,1 12,0 a4.5,3 0 1,1 -9,0 a3,2 0 1,1 6,0" stroke="#ffc24a" stroke-width="1.4" fill="none"/></g></g>')

# fantasma «con alcohol de verdad» para la comparación de reflejos
GHOST = dict(PROTA); GHOST["cam"] = "#ff5a4f"
gente.append(("G", figura("G", GHOST, "brazos", sudor=False)))
coloca("G", 2330, 1700, 3.1)
J('tl.set("#G", {opacity:0}, 0);')
mundo.append('<g id="cinta2" opacity="0"><path d="M2310,1700 L2600,1700" stroke="#ff5a4f" stroke-width="10" stroke-dasharray="40 14"/></g>')

# ------------------------------------------------------------------ GUION VISUAL
R2X = 2380
x0, y0, z0 = face(PX0)
plano(0, x0, y0, z0, 0)
boca(0, "ris")
# 1) gancho: primer plano bailando; «¿borracho?»; golpe al vaso con 0,00
bailar("P", 0.0, F(3) - 0.2, cada=1)
slam("sBorr", "¿BORRACHO?", 0.0, P("convencido") + 0.9, y=980, son=None)
J('tl.set("#sBorr", {opacity:1, scale:1, rotation:-3}, 0);')
plano(P("baila") - 0.1, PX0, 1460, 1.7, 0.5)
boca(P("grita"), "o"); boca(P("rie") , "ris")
J(f'tl.to("#P_h", {{rotation:-12, svgOrigin:"0 -91", duration:0.18, yoyo:true, repeat:3, ease:"sine.inOut"}}, {P("rie"):.2f});')
plano(P("gota") - 0.25, PX0 - 56, 1340, 2.9, 0.35, "power4.out")
slam("s000", '0,00<small>GOTAS DE ALCOHOL</small>', P("gota") - 0.05, FE(1) + 0.15, y=980, cls="slam verde")
golpe_cam(P("gota"))
# 2) se abre: toda la fiesta
plano(F(2) - 0.05, 1300, 960, 1.0, 0.9, "power2.inOut")
slam("sCient", 'CIENTOS<small>DE PERSONAS</small>', P("cientos") - 0.05, P("raro") - 0.3, y=1040, cls="slam")
plano(P("raro") - 0.2, PX0, 1460, 1.5, 0.6)
slam("sRaro", 'MUY RARO', P("raro") - 0.05, FE(2) + 0.2, y=1100, cls="slam rojo", son="latido")
# 3) barrido a la barra: el truco
teleporta("P", 720, 1650, 3.1, F(3) + 0.05)
pz("P", "firme", F(3) + 0.1, 0.2)
boca(F(3) + 0.1, "son")
plano(F(3) - 0.05, 560, 1180, 1.35, 0.5, barrido=True)
slam("sFalso", 'BAR FALSO', P("falso") - 0.05, P("musica") - 0.1, y=1120, cls="slam ama")
slam("sMus", '🎵 MÚSICA', P("musica") - 0.05, P("luces") - 0.1, y=1120, cls="slam", son="pop")
J(f'tl.fromTo(".bomb0, .bomb1, .bomb2", {{scale:1, transformOrigin:"50% 50%"}}, {{scale:1.6, transformOrigin:"50% 50%", duration:0.2, yoyo:true, repeat:1}}, {P("luces"):.2f});')
slam("sLuz", '💡 LUCES', P("luces") - 0.05, P("botellas") - 0.1, y=1120, cls="slam", son="pop")
plano(P("botellas") - 0.1, 450, 980, 2.1, 0.5)
slam("sTon", '<s>VODKA</s> TÓNICA', P("tonica") - 0.05, FE(3) + 0.2, y=1150, cls="slam az", son="rasca")
golpe_cam(P("tonica"), 10)
# 4) la lupa: borde untado, gotas; hueles/saboreas/no hay
plano(F(4) - 0.05, 720, 1460, 1.6, 0.6)
FXL.append('<div id="lupa" class="lupa2"><svg viewBox="0 0 400 400" width="560" height="560">'
           '<circle cx="200" cy="200" r="190" fill="#140f24" stroke="#ffffff" stroke-width="8"/>'
           '<path d="M110,110 L290,110 L270,330 L130,330 Z" fill="url(#tonica)" stroke="#ffffff" stroke-width="5"/>'
           '<path id="lupaBorde" d="M110,110 L290,110" stroke="#ffc24a" stroke-width="12" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/>'
           '<g id="dedo"><path d="M80,40 q30,-10 40,40 l-8,40 q-20,6 -30,-10 Z" fill="#e6b28b" stroke="#a87250" stroke-width="3"/></g>'
           '<g id="lupaGotas">' + "".join(f'<g id="gt{i}"><ellipse cx="{150 + i * 35}" cy="60" rx="8" ry="11" fill="#fff4c2"/></g>' for i in range(3)) + '</g>'
           '<circle cx="250" cy="120" r="30" fill="#9be15d" stroke="#5a9a2a" stroke-width="4"/></svg></div>')
J('tl.set("#lupa", {opacity:0}, 0); tl.set("#gt0, #gt1, #gt2", {opacity:0}, 0);')
J(f'tl.fromTo("#lupa", {{opacity:0, scale:0.3, rotation:-20}}, {{opacity:1, scale:1, rotation:0, duration:0.45, ease:"back.out(1.8)", immediateRender:false}}, {P("sospeche") - 0.3:.2f});')
fx("whoosh", P("sospeche") - 0.3)
J(f'tl.fromTo("#dedo", {{x:0}}, {{x:200, duration:0.5, yoyo:true, repeat:2, ease:"sine.inOut", immediateRender:false}}, {P("borde") - 0.1:.2f});')
J(f'tl.to("#lupaBorde", {{strokeDashoffset:0, duration:1.4, ease:"none"}}, {P("borde") - 0.1:.2f});')
for i in range(3):
    J(f'tl.fromTo("#gt{i}", {{opacity:1, y:-40}}, {{opacity:1, y:58, duration:0.45, ease:"bounce.out", immediateRender:false}}, {P("vodka", 2) + i * 0.18:.2f});')
J(f'tl.to("#dedo", {{opacity:0, duration:0.2}}, {P("vodka", 2):.2f});')
J(f'tl.to("#lupa", {{opacity:0, scale:0.6, duration:0.25}}, {P("hueles") - 0.25:.2f});')
pz("P", "beber2", P("hueles") - 0.1, 0.3)
slam("sHue", 'HUELE ✓', P("hueles") - 0.05, P("saboreas") - 0.05, y=980, cls="slam verde", son="clic")
slam("sSab", 'SABE ✓', P("saboreas") - 0.05, P("pero") - 0.05, y=1100, cls="slam verde", son="clic")
slam("sNo", 'ALCOHOL ✗', P("pero") + 0.3, FE(4) + 0.2, y=1220, cls="slam rojo", son="denegada")
pz("P", "firme", FE(4), 0.3)
# 5) el investigador: «estáis bebiendo vodka» (P vuelve a la pista fuera de plano)
plano(F(5) - 0.05, 470, 1180, 1.9, 0.5, barrido=True)
pz("R1", "hablar", F(5) + 0.1, 0.3); pz("R1", "firme", FE(5) + 0.2, 0.3)
burbuja("bVodka", '«ESTÁIS BEBIENDO VODKA» 😉', P("estais") - 0.2, P("bueno") - 0.4, 120, 760)
teleporta("P", 1150, 1650, 3.1, F(5) + 0.4)
slam("sBueno", 'AQUÍ EMPIEZA<br>LO BUENO', P("bueno") - 0.3, FE(5) + 0.25, y=1020, cls="slam ama", son="riser")
plano(P("bueno") - 0.3, 470, 1180, 2.3, 0.8, "power2.in")
# 6) montaje en la pista: se suelta, habla alto, se ríe, mareos
plano(F(6) - 0.05, 1150, 1460, 1.55, 0.5, barrido=True)
bailar("P", F(6), P("habla") - 0.1, cada=1)
boca(F(6), "ris")
plano(P("habla") - 0.1, 1150, HEADY + 40, 2.4, 0.3, "power4.out")
pz("P", "hablar", P("habla") - 0.1, 0.25); boca(P("habla"), "o")
FXL.append('<div id="ondas" class="ondas"><i></i><i></i><i></i></div>')
J('tl.set("#ondas", {opacity:0}, 0);')
J(f'tl.set("#ondas", {{opacity:1}}, {P("habla"):.2f}); tl.fromTo("#ondas i", {{scale:0.2, opacity:1}}, {{scale:2.2, opacity:0, duration:0.7, stagger:0.18, repeat:1, ease:"power1.out", immediateRender:false}}, {P("habla"):.2f}); tl.set("#ondas", {{opacity:0}}, {P("cualquier") - 0.2:.2f});')
slam("sVol", '🔊 + VOLUMEN', P("habla"), P("rie", 2) - 0.1, y=1160, cls="slam", son="pop")
plano(P("rie", 2) - 0.1, 1150, 1460, 1.7, 0.35)
pz("P", "reir", P("rie", 2) - 0.1, 0.25); boca(P("rie", 2), "ris")
J(f'tl.to("#P_h", {{rotation:-12, svgOrigin:"0 -91", duration:0.16, yoyo:true, repeat:5, ease:"sine.inOut"}}, {P("rie", 2):.2f});')
slam("sRie", 'SE RÍE<br>DE TODO', P("rie", 2), P("mareados") - 0.1, y=1060, cls="slam ama", son="pop")
plano(P("mareados") - 0.2, 1150, HEADY + 30, 2.2, 0.5)
J(f'tl.to("#P_esp", {{opacity:1, duration:0.2}}, {P("mareados"):.2f}); tl.to("#P_espiral", {{rotation:720, svgOrigin:"0 -108", duration:2.2, ease:"none"}}, {P("mareados"):.2f}); tl.to("#P_esp", {{opacity:0, duration:0.2}}, {FE(7) + 0.1:.2f});')
J(f'tl.to("#shake", {{rotation:3, duration:0.6, yoyo:true, repeat:1, ease:"sine.inOut"}}, {P("mareados"):.2f});')
pz("P", "firme", P("mareados") - 0.1, 0.3); boca(P("mareados"), "pla")
J(f'tl.to("#P", {{rotation:4, duration:0.5, yoyo:true, repeat:3, ease:"sine.inOut"}}, {P("mareados"):.2f});')
# 7) congelado: ¿con tónica?
J(f'tl.to("#cam", {{filter:"grayscale(1) contrast(1.15) brightness(0.8)", duration:0.12}}, {F(7) - 0.05:.2f}); tl.to("#cam", {{filter:"grayscale(0) contrast(1) brightness(1)", duration:0.25}}, {FE(7) + 0.1:.2f});')
fx("rasca", F(7) - 0.05)
plano(F(7) - 0.05, 1150, HEADY + 40, 2.7, 0.2, "power4.out")
slam("sTon2", '¿CON TÓNICA?', P("tonica", 2) - 0.1, FE(7) + 0.1, y=1080, cls="slam az", son=None)
# 8) barrido al salón: espejo y jueces
teleporta("P", 2420, 1650, 3.1, F(8))
pz("P", "espejo", F(8) + 0.1, 0.3); boca(F(8) + 0.1, "son")
plano(F(8) - 0.1, 2300, 1300, 1.3, 0.5, barrido=True)
slam("sFra", '🇫🇷 FRANCIA', P("francia") - 0.05, P("creian") - 0.1, y=1000, cls="slam", son="pop")
plano(P("guapos") - 0.4, 2480, 1250, 2.0, 0.5)
FXL.append('<div id="brillos" class="brillos">✨<span>✨</span><em>✨</em></div>')
J('tl.set("#brillos", {opacity:0}, 0);')
J(f'tl.to("#brillos", {{opacity:1, duration:0.2}}, {P("guapos") - 0.1:.2f}); tl.fromTo("#brillos", {{scale:0.6, rotation:-10}}, {{scale:1.15, rotation:10, duration:0.5, yoyo:true, repeat:2, ease:"sine.inOut", immediateRender:false}}, {P("guapos") - 0.1:.2f}); tl.to("#brillos", {{opacity:0, duration:0.2}}, {P("demas") - 0.2:.2f});')
slam("sGuapo", '★★★★★<small>ÉL SE VE ASÍ</small>', P("guapos"), P("demas") - 0.2, y=1480, cls="slam ama", son="ding")
plano(P("demas") - 0.2, 2150, 1300, 1.9, 0.5)
J(f'tl.to("#S1_nota, #S2_nota", {{opacity:1, duration:0.2}}, {P("demas"):.2f}); tl.to("#S1_nota, #S2_nota", {{opacity:0, duration:0.3}}, {FE(8) + 0.3:.2f});')
pz("S1", "nota", P("demas") - 0.1, 0.3); pz("S2", "nota", P("demas"), 0.3)
pz("S1", "sentado", FE(8) + 0.3, 0.3); pz("S2", "sentado", FE(8) + 0.4, 0.3)
slam("sDif", 'NADIE MÁS<br>LO NOTABA', P("diferencia") - 0.3, FE(8) + 0.2, y=1080, cls="slam", son="golpe")
# 9) recuerdos falsos
pz("P", "pensar", F(9) + 0.2, 0.3); boca(F(9), "pla")
plano(F(9) - 0.05, 2420, 1380, 1.6, 0.6)
slam("sInq", 'INQUIETANTE', P("inquietante") - 0.1, P("ensenaron") - 0.1, y=1150, cls="slam rojo", son="latido")
FXL.append('<div id="bocata" class="bocata2"><div class="fotos"><i>👤💼</i><i>🏃</i><i id="fFalso" class="f3">🧢</i></div><small id="falsoT">DETALLE FALSO</small></div>')
J('tl.set("#bocata", {opacity:0}, 0); tl.set("#fFalso, #falsoT", {opacity:0}, 0);')
J(f'tl.fromTo("#bocata", {{opacity:0, scale:0.5, y:40}}, {{opacity:1, scale:1, y:0, duration:0.4, ease:"back.out(2)", immediateRender:false}}, {P("fotos") - 0.3:.2f});')
J(f'tl.fromTo("#fFalso", {{opacity:0, scale:2.5, rotation:-25}}, {{opacity:1, scale:1, rotation:0, duration:0.3, ease:"back.out(2)", immediateRender:false}}, {P("colaron") - 0.1:.2f}); tl.to("#falsoT", {{opacity:1, duration:0.2}}, {P("colaron"):.2f});')
fx("sello", P("colaron"))
J(f'tl.to("#bocata", {{opacity:0, duration:0.25}}, {P("tragaron") - 0.3:.2f});')
slam("sTrag", 'SE LO TRAGARON', P("tragaron") - 0.2, P("convencidisimos") - 0.1, y=1080, cls="slam rojo")
slam("s100", '100%<small>SEGUROS</small>', P("convencidisimos") - 0.1, FE(9) + 0.2, y=1080, cls="slam ama", son="pop")
anda("R2", R2X - 260, F(8), 5.0, y=1600)
# 10) el alcoholímetro: cero
anda("R2", R2X - 140, F(10) - 0.6, 0.6)
J(f'tl.to("#R2_alco", {{opacity:1, duration:0.2}}, {F(10) - 0.1:.2f}); tl.to("#R2_alco", {{opacity:0, duration:0.2}}, {FE(10) + 0.3:.2f});')
pz("R2", "dar", F(10) - 0.1, 0.3)
pz("P", "soplar", F(10) + 0.3, 0.25); boca(F(10) + 0.3, "o")
plano(F(10) - 0.05, 2330, 1400, 1.9, 0.45)
FXL.append('<div id="alcN" class="slam verde" style="top:960px"><b id="alcV">0,37</b><small>ALCOHOLÍMETRO</small></div>')
J('tl.set("#alcN", {opacity:0}, 0);')
J(f'tl.fromTo("#alcN", {{opacity:0, scale:0.5}}, {{opacity:1, scale:1, duration:0.3, ease:"back.out(2)", immediateRender:false}}, {P("alcoholimetro"):.2f});')
J(f'const alv = {{v:0.9}}; tl.to(alv, {{v:0, duration:{max(0.3, P("cero") - P("alcoholimetro") - 0.1):.2f}, ease:"power2.in", onUpdate:() => {{ document.getElementById("alcV").textContent = alv.v.toFixed(2).replace(".", ","); }}}}, {P("alcoholimetro") + 0.1:.2f});')
J(f'tl.fromTo("#alcN", {{scale:1.5}}, {{scale:1, duration:0.3, ease:"back.out(3)", immediateRender:false}}, {P("cero") - 0.05:.2f});')
golpe_cam(P("cero"), 20); fx("golpe", P("cero"))
J(f'tl.fromTo("#medA", {{boxShadow:"0 0 0px rgba(53,217,135,0)"}}, {{boxShadow:"0 0 30px rgba(53,217,135,1)", duration:0.25, yoyo:true, repeat:3, immediateRender:false}}, {P("cero"):.2f});')
J(f'tl.to("#alcN", {{opacity:0, duration:0.25}}, {FE(10) + 0.2:.2f});')
pz("P", "firme", P("nada"), 0.3); pz("R2", "firme", FE(10) + 0.3, 0.3)
# 11-12) el cerebro se adelanta y activa el modo fiesta
plano(F(11) - 0.05, 2420, HEADY + 40, 2.5, 0.5)
boca(F(11), "son")
FXL.append('<div id="cerebro" class="cerebro"><svg viewBox="0 0 300 220" width="520" height="380">'
           '<path d="M150,30 C90,0 30,30 35,90 C10,120 30,180 90,185 C110,215 145,205 150,190 C155,205 190,215 210,185 C270,180 290,120 265,90 C270,30 210,0 150,30 Z" fill="#ff9ec7" stroke="#ffffff" stroke-width="6"/>'
           '<path d="M150,35 L150,185 M80,80 q30,20 10,50 M220,80 q-30,20 -10,50 M100,150 q25,-10 40,10 M200,150 q-25,-10 -40,10" stroke="#d1608f" stroke-width="7" fill="none" stroke-linecap="round"/></svg>'
           '<div id="iconos"><i id="ic1">👃</i><i id="ic2">🎵</i><i id="ic3">🥃</i></div>'
           '<div id="sw" class="sw2"><span>MODO FIESTA</span><b><i id="swk"></i></b></div></div>')
J('tl.set("#cerebro", {opacity:0}, 0); tl.set("#ic1, #ic2, #ic3", {opacity:0}, 0);')
J(f'tl.fromTo("#cerebro", {{opacity:0, scale:0.4}}, {{opacity:1, scale:1, duration:0.45, ease:"back.out(1.8)", immediateRender:false}}, {P("cerebro") - 0.2:.2f});')
fx("whoosh", P("cerebro") - 0.2)
slam("sAdel", '⏩ SE ADELANTA', P("adelanta") - 0.1, FE(11) + 0.2, y=1420, cls="slam ama", son="riser")
for i, (w, dx) in enumerate((("huele", -420), ("oye", 420), ("vaso", -420))):
    tw = P(w, 3) if w == "vaso" else P(w)
    J(f'tl.fromTo("#ic{i + 1}", {{opacity:1, x:{dx}, y:{-120 + i * 90}, scale:1.6}}, {{opacity:1, x:0, y:0, scale:0.9, duration:0.45, ease:"power3.in", immediateRender:false}}, {tw - 0.15:.2f});')
    fx("pop", tw + 0.3)
J(f'tl.to("#swk", {{x:62, background:"#35d987", duration:0.2, ease:"back.out(3)"}}, {P("fiesta") - 0.05:.2f}); tl.to("#sw b", {{background:"rgba(53,217,135,0.35)", duration:0.2}}, {P("fiesta") - 0.05:.2f});')
fx("ding", P("fiesta"))
# confeti al activar el modo fiesta
rc = random.Random(12)
conf = "".join(f'<i class="cf" style="left:{rc.randint(0, 1060)}px;background:{rc.choice(["#ff5ad8", "#4fd1ff", "#ffc24a", "#35d987", "#ffffff"])}"></i>' for _ in range(70))
FXL.append(f'<div id="confeti">{conf}</div>')
J('tl.set("#confeti", {opacity:0}, 0);')
J(f'tl.set("#confeti", {{opacity:1}}, {P("fiesta"):.2f}); tl.fromTo("#confeti .cf", {{y:-80, rotation:0}}, {{y:2000, rotation:540, duration:2.4, stagger:0.025, ease:"power1.in", immediateRender:false}}, {P("fiesta"):.2f}); tl.set("#confeti", {{opacity:0}}, {P("fiesta") + 4.2:.2f});')
J(f'tl.to("#cerebro", {{opacity:0, scale:0.6, duration:0.3}}, {FE(12) - 0.1:.2f});')
bailar("P", P("fiesta"), FE(12) + 0.1, cada=1); boca(P("fiesta"), "ris")
plano(P("fiesta") - 0.05, 2250, 1250, 1.25, 0.6)
# 13) la excusa perfecta
pz("P", "sorpresa", F(13) + 0.1, 0.2)
pz("P", "hablar", P("yo") - 0.2, 0.25); boca(F(13), "son")
plano(F(13) - 0.05, 2420, 1400, 1.9, 0.5)
slam("sExc", 'LA EXCUSA<br>PERFECTA', P("excusa") - 0.1, P("yo") - 0.35, y=1000, cls="slam ama")
burbuja("bYo", '«NO ERA YO,<br>ERA EL ALCOHOL» 🤷', P("yo") - 0.3, FE(13) + 0.3, 520, 800, cola="der")
# 14) silencio: los reflejos (luces bajan, foco sobre él)
J(f'tl.to("#oscuro", {{opacity:0.62, duration:0.5}}, {F(14) - 0.1:.2f}); tl.to("#oscuro", {{opacity:0, duration:0.5}}, {P("fallarias") - 0.6:.2f});')
teleporta("P", 1980, 1700, 3.1, F(14) - 0.05)
pz("P", "firme", F(14), 0.2); boca(F(14), "pla")
plano(F(14) - 0.1, 2000, 1500, 1.6, 0.6, barrido=True)
slam("sRefl", 'LOS REFLEJOS', P("reflejos") - 0.1, FE(14) + 0.2, y=1060, cls="slam az", son="latido")
# 15) comparación: placebo recto / alcohol real torcido
J(f'tl.to("#cinta, #cinta2", {{opacity:1, duration:0.3}}, {F(15) - 0.3:.2f}); tl.to("#cinta, #cinta2", {{opacity:0, duration:0.3}}, {FE(15) + 0.4:.2f});')
J(f'tl.to("#G", {{opacity:0.75, duration:0.3}}, {F(15) - 0.3:.2f}); tl.to("#G", {{opacity:0, duration:0.3}}, {FE(15) + 0.3:.2f});')
plano(F(15) - 0.2, 2268, 1500, 1.25, 0.5)
pz("P", "brazos", F(15), 0.3); pz("G", "brazos", F(15), 0.3)
J(f'tl.to("#P", {{x:2210, duration:2.0, ease:"none"}}, {F(15) + 0.2:.2f});')
J(f'tl.to("#G", {{keyframes:[{{x:2390, y:1685, rotation:-9, duration:0.5}}, {{x:2440, y:1720, rotation:10, duration:0.5}}, {{x:2510, y:1680, rotation:-12, duration:0.5}}, {{x:2560, y:1725, rotation:12, duration:0.5}}], ease:"sine.inOut"}}, {F(15) + 0.2:.2f});')
k, tt = 0, F(15) + 0.2
while tt < F(15) + 2.1:
    pz("P", f"andar{1 + k % 2}", tt, 0.22, "sine.inOut", solo=PIERNAS); pz("G", f"andar{1 + k % 2}", tt, 0.22, "sine.inOut", solo=PIERNAS); tt += 0.3; k += 1
POS["P"] = (2210, 1700, 3.1)
FXL.append('<div id="etqs" class="etqs"><span class="v">PLACEBO</span><span class="r">ALCOHOL REAL</span></div>')
J('tl.set("#etqs", {opacity:0}, 0);'); J(f'tl.to("#etqs", {{opacity:1, duration:0.3}}, {F(15):.2f}); tl.to("#etqs", {{opacity:0, duration:0.3}}, {FE(15) + 0.3:.2f});')
coloca("R2", 2080, 1590, 2.7, F(15) + 0.2, 0.8)
pz("R2", "mostrar", P("regla") - 0.5, 0.3)
J(f'tl.to("#R2_regla", {{opacity:1, duration:0.15}}, {P("regla") - 0.4:.2f}); tl.to("#R2_regla", {{y:"+=26", duration:0.12, ease:"power2.in"}}, {P("regla"):.2f}); tl.to("#R2_regla", {{opacity:0, duration:0.2}}, {FE(15):.2f});')
pz("P", "atrapar", P("regla") + 0.05, 0.12, "power3.out"); fx("clic2", P("regla") + 0.1)
slam("sPerf", 'PLACEBO: ✓', P("perfecto") - 0.15, P("fallarias") - 0.3, y=1000, cls="slam verde", son="ding")
slam("sFall", 'ALCOHOL: ✗', P("fallarias") - 0.2, FE(15) + 0.2, y=1120, cls="slam rojo", son="denegada")
pz("P", "firme", FE(15), 0.3); pz("R2", "firme", FE(15), 0.3)
# 16) la verdad: enseñan la botella; no se lo creen
J(f'tl.to("#R2_bot", {{opacity:1, duration:0.2}}, {F(16) - 0.1:.2f}); tl.to("#R2_bot", {{opacity:0, duration:0.2}}, {FE(16) + 0.3:.2f});')
pz("R2", "mostrar", F(16), 0.3)
plano(F(16) - 0.05, 2150, 1380, 1.7, 0.5)
pz("P", "sorpresa", P("creen") - 0.5, 0.25); boca(P("creen") - 0.5, "o")
plano(P("creen") - 0.5, 2210, HEADY + 90, 2.6, 0.3, "power4.out")
slam("sCreen", '¿SOLO TÓNICA?', P("verdad", 2) + 0.2, FE(16) + 0.2, y=1060, cls="slam az", son="rasca")
pz("R2", "firme", FE(16) + 0.3, 0.3)
# 17) vuelve a la pista y sigue bailando → mismo plano que el fotograma 0
teleporta("P", PX0, 1650, 3.1, F(17) - 0.05)
plano(F(17) - 0.1, 1300, 960, 1.0, 0.55, barrido=True)
bailar("P", F(17), DUR - 0.25, cada=1); boca(F(17), "ris")
slam("sCopa", 'UNA SOLA COPA…', P("copa") - 0.2, P("chico", 2) - 0.4, y=1040, cls="slam ama", son="pop")
plano(P("copa") + 0.4, x0, y0, z0, max(0.6, DUR - 1.4 - P("copa") - 0.4), "sine.inOut")
pz("P", "baile1", DUR - 0.25, 0.2)
J(f'tl.fromTo("#sBorr", {{opacity:0, scale:1.6, rotation:-6}}, {{opacity:1, scale:1, rotation:-3, duration:0.4, ease:"back.out(2)", immediateRender:false}}, {DUR - 1.0:.2f});')

# ------------------------------------------------------------------ MEDIDORES
SIENTE = [(0, 82), (F(3) - 0.2, 82), (F(3) + 0.6, 0), (P("hueles"), 0), (P("saboreas") + 0.6, 20), (F(6), 30), (P("rie", 2), 70), (P("mareados") + 0.5, 80),
          (FE(15) - 1.0, 80), (P("creen"), 35), (F(17) + 1.5, 55), (DUR - 2.0, 82), (DUR, 82)]
kf = [f'{{v:{b[1]}, duration:{max(0.01, b[0] - a[0]):.3f}, ease:"sine.inOut"}}' for a, b in zip(SIENTE, SIENTE[1:])]
J('const sv = {v:82};')
J(f'tl.to(sv, {{keyframes:[{",".join(kf)}], onUpdate:() => {{ document.getElementById("barS").style.width = sv.v + "%"; document.getElementById("numS").textContent = Math.round(sv.v) + "%"; }}}}, 0);')
J('document.getElementById("barS").style.width = "82%";')
# pulso sutil a ritmo y cámara en mano
J(f'tl.fromTo("#shake", {{x:-5, y:3}}, {{x:5, y:-3, duration:2.7, yoyo:true, repeat:{int(DUR / 2.7)}, ease:"sine.inOut", immediateRender:false}}, 0);')
J(f'tl.fromTo("#pulso", {{scale:1, transformOrigin:"50% 50%"}}, {{scale:1.012, transformOrigin:"50% 50%", duration:{BEAT / 2:.3f}, yoyo:true, repeat:{int(DUR / (BEAT / 2))}, ease:"sine.inOut", immediateRender:false}}, 0);')

# ------------------------------------------------------------------ insertar la cara en la figura del protagonista
for i, (pid, g) in enumerate(gente):
    if pid == "P":
        a = g.index('<g id="P_h" >'); b = g.index('</g></g>', a)
        gente[i] = (pid, g[:b] + CARA + g[b:])
OVR = []

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
svg = f'<g id="mundo">{"".join(mundo)}{r1}{barra}<rect id="oscuro" x="0" y="0" width="{W}" height="1920" fill="#05030c" opacity="0"/>{svg_gente}</g>'

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
#imp,#shake,#pulso{{position:absolute;inset:0}} #cam{{position:absolute;left:0;top:0;width:{W}px;height:1920px;transform-origin:0 0}}
#fxl{{position:absolute;inset:0;z-index:58;pointer-events:none}}
.slam{{position:absolute;left:0;right:0;margin:0 auto;width:max-content;max-width:1000px;padding:10px 30px;border-radius:18px;background:rgba(10,6,22,0.82);border:3px solid #fff;text-align:center;font:900 92px/1.02 Inter;letter-spacing:-2px;color:#fff;text-shadow:0 6px 20px rgba(0,0,0,0.5);box-shadow:0 14px 40px rgba(0,0,0,0.45)}}
.slam small{{display:block;margin-top:6px;font:800 26px Inter;letter-spacing:6px;color:#e6dcff}} .slam s{{color:#9fb3c8;font-size:70px}}
.slam.verde{{border-color:{VE};color:{VE}}} .slam.rojo{{border-color:{RJ};color:{RJ}}} .slam.ama{{border-color:{AM};color:{AM}}} .slam.az{{border-color:{CY_};color:{CY_}}}
.slam.verde b{{font:900 150px/1 Inter;font-variant-numeric:tabular-nums}}
.bubble{{position:absolute;padding:20px 28px;border-radius:30px;background:#fff;color:#1d1430;font:900 50px/1.1 Inter;box-shadow:0 10px 30px rgba(0,0,0,0.4)}}
.bubble:after{{content:"";position:absolute;bottom:-26px;left:70px;border:16px solid transparent;border-top:20px solid #fff}} .bubble.der:after{{left:auto;right:90px}}
.lupa2{{position:absolute;left:260px;top:700px;width:560px}}
.ondas{{position:absolute;left:540px;top:900px}} .ondas i{{position:absolute;left:-90px;top:-90px;width:180px;height:180px;border-radius:50%;border:8px solid {AM}}}
.brillos{{position:absolute;left:640px;top:760px;font-size:90px}} .brillos span{{position:absolute;left:-200px;top:180px;font-size:60px}} .brillos em{{position:absolute;left:60px;top:260px;font-size:50px;font-style:normal}}
.bocata2{{position:absolute;left:120px;top:640px;width:840px;padding:24px;border-radius:50px;background:rgba(255,255,255,0.95);text-align:center;box-shadow:0 10px 30px rgba(0,0,0,0.4)}}
.bocata2 .fotos{{display:flex;gap:20px;justify-content:center}} .bocata2 .fotos i{{display:block;font-style:normal;font-size:80px;width:200px;height:170px;line-height:170px;background:#e9e2cf;border:8px solid #fff;box-shadow:0 4px 10px rgba(0,0,0,0.3)}}
.bocata2 .fotos i.f3{{outline:7px solid {RJ}}} .bocata2 small{{display:block;margin-top:14px;font:900 34px Inter;letter-spacing:5px;color:{RJ}}}
.cerebro{{position:absolute;left:280px;top:700px;width:520px;text-align:center}} #iconos{{position:absolute;left:0;right:0;top:120px}} #iconos i{{position:absolute;left:220px;top:0;font-size:80px;font-style:normal}}
.sw2{{display:inline-flex;align-items:center;gap:16px;margin-top:6px;padding:12px 22px;border-radius:40px;background:rgba(10,6,22,0.85);font:900 34px Inter;color:#fff;letter-spacing:3px}}
.sw2 b{{position:relative;width:120px;height:56px;border-radius:28px;background:rgba(255,255,255,0.2)}} .sw2 b i{{position:absolute;left:4px;top:4px;width:48px;height:48px;border-radius:50%;background:#9fb3c8}}
#confeti{{position:absolute;inset:0;overflow:hidden}} .cf{{position:absolute;top:0;width:16px;height:26px;border-radius:3px}}
.etqs{{position:absolute;left:0;right:0;top:1300px;display:flex;justify-content:space-around;font:900 40px Inter;letter-spacing:3px}} .etqs .v{{color:{VE}}} .etqs .r{{color:{RJ}}}
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
  <div id="imp"><div id="shake"><div id="pulso"><div id="cam"><svg width="{W}" height="1920" viewBox="0 0 {W} 1920" style="position:absolute;left:0;top:0;overflow:visible"><defs>{"".join(DEFS)}</defs>{svg}</svg>
  {"".join(OVR)}</div></div></div></div>
  <div id="fxl">{"".join(FXL)}</div>
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

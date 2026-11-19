#!/usr/bin/env python3
"""«100 horas pegado a una pantalla» v2 — ilustración plana cuidada: personaje de perfil articulado (_rig.py),
escenarios a escala real (dormitorio, autobús, oficina, baño) con luz y sombras, cámara de cine y rótulos limpios.
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
def PL(word): return [a for w, a, b in WORDS if w == norm(word)][-1]
def F(n): return FR[n - 1]["ini"]
def FE(n): return FR[n - 1]["fin"]
tl, FX, DEFS, FXL = [], [], [], []
def J(s): tl.append(s)
def fx(k, t): FX.append([k, round(t, 3)])
CY_, RJ, AM, VE, TX, LI = "#4fd1ff", "#ff5a4f", "#ffc24a", "#35d987", "#eef4fb", "#b98cff"
exec(open(os.path.join(BASE, "_rig.py"), encoding="utf-8").read())
rw = random.Random(5)
S = 3.6                                         # píxeles por cm
SUELO = 1560
def cm(v): return v * S
W = 4300

# ------------------------------------------------------------------ HORAS DE PANTALLA
R0 = F(2) + 0.1; R1 = R0 + 1.4
ANCH = [(0, 100), (R0, 100), (R1, 0), (F(3), 0.5), (F(5), 1.5), (F(7), 9), (F(8), 13), (FE(8), 18), (F(9) + 1.0, 40), (F(12), 60),
        (F(15), 100), (DUR, 100)]
def H(t):
    for (a, va), (b, vb) in zip(ANCH, ANCH[1:]):
        if a <= t <= b:
            return va + (vb - va) * (t - a) / max(1e-6, b - a)
    return 100.0
TS = sorted(set([round(i * 0.2, 2) for i in range(int(DUR / 0.2) + 1)] + [round(R0 + i * 0.05, 2) for i in range(30)] + [DUR]))

# ------------------------------------------------------------------ DEGRADADOS
DEFS += [
    '<linearGradient id="gDorm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b1f3d"/><stop offset="1" stop-color="#2b3060"/></linearGradient>',
    '<linearGradient id="gNoche" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05091f"/><stop offset="1" stop-color="#1d2a5e"/></linearGradient>',
    '<linearGradient id="gDia" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6fb0e8"/><stop offset="1" stop-color="#d6ecf8"/></linearGradient>',
    '<linearGradient id="gBus" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9edf2"/><stop offset="1" stop-color="#c3cbd6"/></linearGradient>',
    '<linearGradient id="gOfi" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e7ebf0"/><stop offset="1" stop-color="#c9d1db"/></linearGradient>',
    '<linearGradient id="gBan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e3f1f2"/><stop offset="1" stop-color="#bcd8db"/></linearGradient>',
    '<linearGradient id="gSuelo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7a5a42"/><stop offset="1" stop-color="#4e3626"/></linearGradient>',
    '<linearGradient id="gSueloB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a505c"/><stop offset="1" stop-color="#2c3038"/></linearGradient>',
    '<linearGradient id="gMadera" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a87a52"/><stop offset="1" stop-color="#7a5236"/></linearGradient>',
    '<linearGradient id="gPant" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#bfe8ff"/><stop offset="0.6" stop-color="#5aa8e8"/><stop offset="1" stop-color="#2c6ab0"/></linearGradient>',
    '<linearGradient id="gAsiento" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a62c9"/><stop offset="1" stop-color="#26449a"/></linearGradient>',
    '<linearGradient id="gCuerpoBus" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f2b33a"/><stop offset="1" stop-color="#d9922a"/></linearGradient>',
    '<radialGradient id="glowP" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#8fd8ff" stop-opacity="0.85"/><stop offset="1" stop-color="#8fd8ff" stop-opacity="0"/></radialGradient>',
    '<radialGradient id="glowM" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#9fdcff" stop-opacity="0.55"/><stop offset="1" stop-color="#9fdcff" stop-opacity="0"/></radialGradient>',
    '<radialGradient id="glowL" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffe2a0" stop-opacity="0.7"/><stop offset="1" stop-color="#ffe2a0" stop-opacity="0"/></radialGradient>',
    '<radialGradient id="glowT" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffffff" stop-opacity="0.6"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>',
    '<linearGradient id="haz" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0.35"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>',
    '<linearGradient id="gAzulejo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#e2ecef"/></linearGradient>',
]
M = []
def sombra_suelo(x0, x1, op=0.25):
    M.append(f'<ellipse cx="{(x0 + x1) / 2}" cy="{SUELO + 6}" rx="{(x1 - x0) / 2}" ry="14" fill="#000" opacity="{op}"/>')
TECHO = SUELO - cm(265)
# ================= DORMITORIO (0-1050)
M.append(f'<rect x="0" y="0" width="1060" height="{SUELO}" fill="url(#gDorm)"/>')
M.append(f'<rect x="0" y="{TECHO - 30}" width="1060" height="30" fill="#151830"/>')
M.append('<g transform="translate(140,760)"><rect width="420" height="420" rx="6" fill="url(#gNoche)"/>'
         + "".join(f'<rect x="{10 + i * 38}" y="{420 - rw.randint(140, 330)}" width="34" height="400" fill="{rw.choice(["#141a3a", "#1a2148", "#10162e"])}"/>' for i in range(11))
         + "".join(f'<rect x="{rw.randint(16, 400)}" y="{rw.randint(160, 400)}" width="5" height="7" fill="#ffd27a" opacity="{rw.uniform(0.4, 0.9):.2f}"/>' for _ in range(45))
         + '<circle cx="330" cy="80" r="30" fill="#f4f1e2"/><circle cx="330" cy="80" r="70" fill="url(#glowT)" opacity="0.4"/>'
         + '<rect width="420" height="420" rx="6" fill="none" stroke="#e9e2cf" stroke-width="16"/><path d="M210,0 L210,420 M0,210 L420,210" stroke="#e9e2cf" stroke-width="10"/>'
         + '<path d="M-40,-30 Q-10,200 -50,450 L-20,450 Q30,200 0,-30 Z" fill="#7a3b6b"/><path d="M460,-30 Q430,200 470,450 L440,450 Q390,200 420,-30 Z" fill="#7a3b6b"/></g>')
M.append('<g transform="translate(640,820)"><rect x="0" y="0" width="200" height="260" rx="4" fill="#e9e2cf"/><rect x="14" y="14" width="172" height="232" fill="#c75b5b"/><circle cx="100" cy="110" r="50" fill="#ffc24a"/><rect x="14" y="200" width="172" height="46" fill="#2c3e5e"/></g>')
M.append(f'<rect x="0" y="{SUELO}" width="1060" height="{1920 - SUELO}" fill="url(#gSuelo)"/>' + "".join(f'<path d="M{i},{SUELO} L{i - 80},1920" stroke="#3a281c" stroke-width="3" opacity="0.6"/>' for i in range(0, 1060, 120)))
CAMA_X0, CAMA_X1, COLCHON = 80, 900, SUELO - cm(52)
sombra_suelo(CAMA_X0, CAMA_X1 + 40, 0.35)
M.append(f'<rect x="{CAMA_X0}" y="{SUELO - cm(110)}" width="40" height="{cm(110)}" rx="10" fill="url(#gMadera)"/>'
         f'<rect x="{CAMA_X0 + 30}" y="{COLCHON + 40}" width="{CAMA_X1 - CAMA_X0 - 30}" height="{SUELO - COLCHON - 40}" rx="8" fill="url(#gMadera)"/>'
         f'<rect x="{CAMA_X0 + 34}" y="{COLCHON}" width="{CAMA_X1 - CAMA_X0 - 40}" height="50" rx="16" fill="#f2efe6"/>')
CAMA_TOP = []                                       # sábana y almohada (delante del personaje cuando duerme)
CAMA_TOP.append(f'<path d="M{CAMA_X0 + 380},{COLCHON - 34} L{CAMA_X1 - 6},{COLCHON - 30} Q{CAMA_X1 + 10},{COLCHON + 10} {CAMA_X1 - 6},{COLCHON + 60} L{CAMA_X0 + 370},{COLCHON + 60} Q{CAMA_X0 + 350},{COLCHON + 10} {CAMA_X0 + 380},{COLCHON - 34} Z" fill="#4f6fc9"/>'
                f'<path d="M{CAMA_X0 + 380},{COLCHON - 34} L{CAMA_X1 - 6},{COLCHON - 30}" stroke="#7a95e0" stroke-width="8"/>')
ALMOH = f'<rect x="{CAMA_X0 + 50}" y="{COLCHON - 46}" width="150" height="56" rx="26" fill="#ffffff"/><rect x="{CAMA_X0 + 50}" y="{COLCHON - 10}" width="150" height="20" rx="10" fill="#dfe4ea"/>'
M.append(ALMOH)
MESILLA = SUELO - cm(55)
sombra_suelo(920, 1040)
M.append(f'<rect x="915" y="{MESILLA}" width="130" height="{SUELO - MESILLA}" rx="6" fill="url(#gMadera)"/><rect x="930" y="{MESILLA + 30}" width="100" height="6" fill="#4e3020"/>'
         f'<g transform="translate(975,{MESILLA})"><rect x="-44" y="-56" width="88" height="56" rx="10" fill="#1d1d24"/><text id="despN" x="0" y="-18" text-anchor="middle" font-family="Inter" font-weight="900" font-size="30" fill="#ff5a4f">06:30</text></g>'
         f'<circle cx="975" cy="{MESILLA - 40}" r="110" fill="url(#glowL)" opacity="0.0" id="luzMes"/>')
# ================= AUTOBÚS (1060-2260)
BX0, BX1 = 1060, 2260
M.append(f'<rect x="{BX0}" y="0" width="{BX1 - BX0}" height="{SUELO}" fill="url(#gBus)"/>')
VEN_Y0, VEN_Y1 = SUELO - cm(205), SUELO - cm(115)
M.append(f'<clipPath id="clipVen"><rect x="{BX0 + 40}" y="{VEN_Y0}" width="{BX1 - BX0 - 80}" height="{VEN_Y1 - VEN_Y0}" rx="20"/></clipPath>')
DEFS.append(f'<clipPath id="clipVen2"><rect x="{BX0 + 40}" y="{VEN_Y0}" width="{BX1 - BX0 - 80}" height="{VEN_Y1 - VEN_Y0}" rx="20"/></clipPath>')
lej = "".join(f'<rect x="{BX0 + i * 90}" y="{VEN_Y0 + rw.randint(10, 120)}" width="84" height="420" fill="{rw.choice(["#9fb7d6", "#b3c6de", "#8fa8ca"])}"/>' for i in range(40))
cer = "".join(f'<g><rect x="{BX0 + i * 160}" y="{VEN_Y0 + rw.randint(60, 160)}" width="150" height="420" fill="{rw.choice(["#5a6f9a", "#4a5f8a", "#6a7faa"])}"/>'
              + "".join(f'<rect x="{BX0 + i * 160 + 18 + k * 44}" y="{VEN_Y0 + 200 + r * 50}" width="26" height="30" fill="#e8f0ff" opacity="0.6"/>' for k in range(3) for r in range(3)) + '</g>' for i in range(30))
farolas = "".join(f'<g transform="translate({BX0 + i * 420},{VEN_Y1})"><rect x="-4" y="-260" width="8" height="260" fill="#2c3038"/><rect x="-30" y="-266" width="40" height="10" rx="4" fill="#2c3038"/></g>' for i in range(14))
M.append(f'<g clip-path="url(#clipVen2)"><rect x="{BX0}" y="{VEN_Y0}" width="{BX1 - BX0}" height="{VEN_Y1 - VEN_Y0}" fill="url(#gDia)"/>'
         f'<g id="vLej">{lej}</g><g id="vCer">{cer}</g><g id="vFar">{farolas}</g></g>')
for x in range(BX0 + 40, BX1 - 40, 280):
    M.append(f'<rect x="{x - 6}" y="{VEN_Y0}" width="12" height="{VEN_Y1 - VEN_Y0}" fill="#c3cbd6"/>')
M.append(f'<rect x="{BX0 + 40}" y="{VEN_Y0}" width="{BX1 - BX0 - 80}" height="{VEN_Y1 - VEN_Y0}" rx="20" fill="none" stroke="#9aa6b6" stroke-width="10"/>'
         f'<rect x="{BX0 + 40}" y="{VEN_Y0 - 120}" width="{BX1 - BX0 - 80}" height="90" rx="10" fill="#ffffff"/>'
         + "".join(f'<rect x="{BX0 + 60 + i * 290}" y="{VEN_Y0 - 110}" width="270" height="70" rx="6" fill="{c}"/>' for i, c in enumerate(("#ff5a4f", "#35a3d9", "#ffc24a", "#7a5bd6")))
         + f'<path d="M{BX0},{TECHO + 40} L{BX1},{TECHO + 40}" stroke="#9aa6b6" stroke-width="12"/>' + "".join(f'<path d="M{x},{TECHO + 40} L{x},{SUELO}" stroke="#ffc24a" stroke-width="14"/>' for x in (BX0 + 520, BX0 + 1020))
         + "".join(f'<g transform="translate({BX0 + 200 + i * 260},{TECHO + 40})"><path d="M0,0 L0,40" stroke="#9aa6b6" stroke-width="5"/><circle cy="58" r="18" fill="none" stroke="#2c3038" stroke-width="7"/></g>' for i in range(4))
         + f'<rect x="{BX0}" y="{TECHO}" width="{BX1 - BX0}" height="40" fill="#ffffff"/><rect x="{BX0 + 30}" y="{TECHO + 10}" width="{BX1 - BX0 - 60}" height="14" rx="6" fill="#fff8e0"/>')
M.append(f'<rect x="{BX0}" y="{SUELO}" width="{BX1 - BX0}" height="{1920 - SUELO}" fill="url(#gSueloB)"/>' + "".join(f'<path d="M{BX0},{SUELO + 30 + k * 40} L{BX1},{SUELO + 30 + k * 40}" stroke="#5a606c" stroke-width="3"/>' for k in range(9)))
ASIENTO_Y = SUELO - cm(45)
def asiento(x):
    return (f'<g transform="translate({x},{ASIENTO_Y})"><rect x="-70" y="-6" width="170" height="40" rx="16" fill="url(#gAsiento)"/>'
            f'<path d="M-76,-200 Q-90,-80 -70,0 L-40,0 Q-56,-80 -46,-200 Z" fill="url(#gAsiento)"/><rect x="-82" y="-216" width="44" height="30" rx="12" fill="#2a4aa8"/>'
            f'<rect x="-10" y="34" width="14" height="{SUELO - ASIENTO_Y - 34}" fill="#5a606c"/></g>')
for x in (1300, 1640, 1980):
    sombra_suelo(x - 90, x + 110, 0.3)
    M.append(asiento(x))
# ================= OFICINA (2260-3420)
OX0, OX1 = 2260, 3420
M.append(f'<rect x="{OX0}" y="0" width="{OX1 - OX0}" height="{SUELO}" fill="url(#gOfi)"/>')
M.append(f'<rect x="{OX0}" y="{TECHO - 30}" width="{OX1 - OX0}" height="30" fill="#b9c2ce"/>')
M.append(f'<g transform="translate({OX0 + 60},{SUELO - cm(230)})"><rect width="520" height="{cm(150)}" rx="6" fill="url(#gDia)"/>'
         + "".join(f'<rect x="{12 + i * 52}" y="{cm(150) - rw.randint(120, 380)}" width="46" height="400" fill="{rw.choice(["#9fb7d6", "#b3c6de", "#8fa8ca"])}"/>' for i in range(10))
         + f'<rect width="520" height="{cm(150)}" rx="6" fill="none" stroke="#8a96a8" stroke-width="16"/><path d="M260,0 L260,{cm(150)}" stroke="#8a96a8" stroke-width="10"/>'
         + f'<path d="M30,20 L200,{cm(150) - 20} L320,{cm(150) - 20} L150,20 Z" fill="url(#haz)" opacity="0.5"/></g>')
M.append(f'<g transform="translate({OX0 + 760},{SUELO - cm(215)})"><circle r="50" fill="#fff" stroke="#3a3f4b" stroke-width="8"/>'
         + "".join(f'<path d="M{40 * math.cos(a):.0f},{40 * math.sin(a):.0f} L{46 * math.cos(a):.0f},{46 * math.sin(a):.0f}" stroke="#3a3f4b" stroke-width="3"/>' for a in [i * math.pi / 6 for i in range(12)])
         + '<g id="agujaO"><path d="M0,0 L0,-34" stroke="#1d1d24" stroke-width="6" stroke-linecap="round"/></g><path d="M0,0 L20,0" stroke="#1d1d24" stroke-width="6" stroke-linecap="round"/></g>')
M.append(f'<g transform="translate({OX0 + 900},{SUELO - cm(240)})"><rect width="230" height="{cm(70)}" rx="4" fill="#2c3e5e"/><text x="115" y="{cm(35) + 4}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="34" fill="#ffc24a">KPI ↑</text></g>')
for i, x in enumerate((OX0 + 330, OX0 + 640, OX0 + 950)):
    M.append(f'<g transform="translate({x},{TECHO})"><path d="M0,0 L0,90" stroke="#3a3f4b" stroke-width="4"/><path d="M-60,90 L60,90 L40,130 L-40,130 Z" fill="#3a3f4b"/><ellipse cx="0" cy="170" rx="160" ry="120" fill="url(#glowL)" opacity="0.55"/></g>')
M.append(f'<rect x="{OX0}" y="{SUELO}" width="{OX1 - OX0}" height="{1920 - SUELO}" fill="#8a96a8"/>' + "".join(f'<path d="M{x},{SUELO} L{x - 70},1920" stroke="#7a8698" stroke-width="3"/>' for x in range(OX0, OX1, 110)))
# compañero al fondo, en su mesa (más pequeño y apagado)
M.append(f'<g opacity="0.75"><rect x="{OX0 + 120}" y="{SUELO - cm(70) + 40}" width="320" height="16" fill="#8a7a6a"/><rect x="{OX0 + 300}" y="{SUELO - cm(70) - 90}" width="120" height="80" rx="6" fill="#2c3e5e"/><rect x="{OX0 + 308}" y="{SUELO - cm(70) - 82}" width="104" height="64" fill="#7fc0ec"/></g>')
MESA_Y = SUELO - cm(75)
MX = 3060
sombra_suelo(MX - 240, MX + 240, 0.3)
MESA_FONDO = (f'<rect x="{MX - 230}" y="{MESA_Y + 16}" width="20" height="{SUELO - MESA_Y - 16}" fill="#5a3e2a"/>'
              f'<g transform="translate({MX + 90},{MESA_Y})"><rect x="-10" y="-70" width="20" height="70" fill="#3a3f4b"/><rect x="-60" y="-8" width="120" height="10" rx="4" fill="#3a3f4b"/>'
              f'<path d="M-10,-250 L40,-270 L40,-70 L-10,-80 Z" fill="#1d1d24"/><path d="M-120,-240 L-10,-250 L-10,-80 L-120,-90 Z" fill="#2c3038"/>'
              f'<path id="pantOfi" d="M-112,-232 L-16,-241 L-16,-88 L-112,-97 Z" fill="url(#gPant)"/>'
              f'<g id="pantCont"><rect x="-104" y="-224" width="70" height="8" fill="#ffffff" opacity="0.8"/><rect x="-104" y="-208" width="50" height="6" fill="#ffffff" opacity="0.6"/>'
              + "".join(f'<rect x="-104" y="{-196 + k * 14}" width="{rw.randint(40, 80)}" height="5" fill="#ffffff" opacity="0.45"/>' for k in range(6)) + '</g>'
              f'<ellipse cx="-130" cy="-150" rx="220" ry="180" fill="url(#glowM)" id="luzPant"/></g>')
MESA_FRENTE = (f'<rect x="{MX - 250}" y="{MESA_Y}" width="500" height="24" rx="6" fill="url(#gMadera)"/>'
               f'<rect x="{MX + 220}" y="{MESA_Y + 16}" width="22" height="{SUELO - MESA_Y - 16}" fill="#7a5236"/>'
               f'<rect x="{MX - 170}" y="{MESA_Y - 12}" width="150" height="14" rx="4" fill="#2c3038"/>'
               f'<g transform="translate({MX + 190},{MESA_Y})"><rect x="-22" y="-56" width="44" height="56" rx="8" fill="#ffffff"/><path d="M22,-44 q20,8 0,26" stroke="#ffffff" stroke-width="7" fill="none"/>'
               f'<path class="vapor" d="M-6,-64 q-8,-16 4,-30 q10,-14 -2,-30" stroke="#ffffff" stroke-width="4" fill="none" opacity="0.5"/></g>'
               f'<g id="papeles">' + "".join(f'<rect class="pap" x="{MX - 20}" y="{MESA_Y - 8 - i * 7}" width="80" height="6" fill="#f4f8fc" stroke="#cfd6e0"/>' for i in range(16)) + '</g>')
SILLA_Y = SUELO - cm(48)
CX = MX - 330
SILLA = (f'<g transform="translate({CX},{SILLA_Y})"><rect x="-60" y="-4" width="150" height="30" rx="12" fill="#2c3038"/><path d="M-70,-230 Q-90,-110 -60,0 L-34,0 Q-56,-110 -44,-230 Z" fill="#2c3038"/>'
         f'<rect x="10" y="26" width="14" height="{SUELO - SILLA_Y - 50}" fill="#5a606c"/><path d="M-50,{SUELO - SILLA_Y - 20} L80,{SUELO - SILLA_Y - 20}" stroke="#5a606c" stroke-width="10" stroke-linecap="round"/></g>')
sombra_suelo(CX - 70, CX + 100, 0.3)
# ================= BAÑO (3420-4300)
ZX0 = 3420
M.append(f'<rect x="{ZX0}" y="0" width="{W - ZX0}" height="{SUELO}" fill="url(#gBan)"/>')
for y in range(int(TECHO) + 400, SUELO, 72):
    for x in range(ZX0, W, 72):
        M.append(f'<rect x="{x + 2}" y="{y + 2}" width="68" height="68" rx="3" fill="url(#gAzulejo)" opacity="0.9"/>')
M.append(f'<g transform="translate({ZX0 + 640},{SUELO - cm(180)})"><rect x="-130" y="-160" width="260" height="300" rx="20" fill="#cfe6f5" stroke="#9fb3c8" stroke-width="10"/><path d="M-90,-110 L30,-150 M-100,-50 L60,-120" stroke="#ffffff" stroke-width="10" opacity="0.6"/></g>'
         f'<g transform="translate({ZX0 + 640},{SUELO - cm(85)})"><rect x="-140" y="-20" width="280" height="40" rx="14" fill="#f4f8fc"/><rect x="-22" y="20" width="44" height="{cm(85) - 20}" fill="#e2e8ee"/><path d="M-10,-20 L-10,-60 Q-10,-70 10,-70 L30,-70" stroke="#9fb3c8" stroke-width="10" fill="none"/></g>'
         f'<g transform="translate({ZX0 + 150},{SUELO - cm(80)})"><rect x="-30" y="-30" width="60" height="16" rx="6" fill="#9fb3c8"/><rect x="-40" y="-14" width="80" height="56" rx="24" fill="#ffffff"/></g>')
M.append(f'<rect x="{ZX0}" y="{SUELO}" width="{W - ZX0}" height="{1920 - SUELO}" fill="#9fb3c8"/>' + "".join(f'<path d="M{x},{SUELO} L{x - 70},1920" stroke="#8aa0b6" stroke-width="3"/>' for x in range(ZX0, W, 90)))
VX = ZX0 + 330
VATER_Y = SUELO - cm(42)
sombra_suelo(VX - 120, VX + 140, 0.3)
VATER = (f'<g transform="translate({VX},{SUELO})"><rect x="-150" y="-{cm(80)}" width="70" height="{cm(42)}" rx="12" fill="#f4f8fc" stroke="#cfd6e0" stroke-width="4"/>'
         f'<path d="M-90,-{cm(42)} L130,-{cm(42)} Q140,-{cm(30)} 110,-{cm(22)} L40,-{cm(18)} L50,0 L-40,0 L-30,-{cm(18)} Q-90,-{cm(22)} -90,-{cm(42)} Z" fill="#ffffff" stroke="#cfd6e0" stroke-width="4"/>'
         f'<rect x="-94" y="-{cm(42) + 8}" width="236" height="14" rx="7" fill="#e9eef3"/></g>')

# ------------------------------------------------------------------ PERSONAJES
PROTA = dict(piel="#e8b48c", pelo="#2a1c14", camisa="#eef2f7", pantalon="#2c3e5e", zapato="#1d1d24")
OTRO1 = dict(piel="#8a5a3c", pelo="#141418", camisa="#7a5bd6", pantalon="#1d2433", zapato="#f2f4f7")
OTRO2 = dict(piel="#f0c7a2", pelo="#9a6a3a", camisa="#3fa66b", pantalon="#3a3f4b", zapato="#3a2a20")
movil = ('<g id="P_mov"><g transform="rotate(-70)"><rect x="-7" y="-13" width="14" height="24" rx="3" fill="#1d1d24"/><rect id="P_movP" x="-5.6" y="-11.2" width="11.2" height="20.4" rx="2" fill="#8fd8ff"/></g></g>')
figP = rig("P", PROTA).replace('<g id="P_manoN"></g>', f'<g id="P_manoN">{movil}</g>')
figO1 = rig("O1", OTRO1).replace('<g id="O1_manoN"></g>', '<g id="O1_manoN"><g transform="rotate(-70)"><rect x="-7" y="-13" width="14" height="24" rx="3" fill="#1d1d24"/><rect x="-5.6" y="-11.2" width="11.2" height="20.4" rx="2" fill="#8fd8ff"/></g></g>')
figO2 = rig("O2", OTRO2).replace('<g id="O2_manoN"></g>', '<g id="O2_manoN"><g transform="rotate(-70)"><rect x="-7" y="-13" width="14" height="24" rx="3" fill="#1d1d24"/><rect x="-5.6" y="-11.2" width="11.2" height="20.4" rx="2" fill="#8fd8ff"/></g></g>')
CADERA_PIE = cm(RL["TH"] + RL["SH"]) - 4
LUG = {"cama": (CAMA_X0 + 330, COLCHON - 18, -90), "camaSent": (CAMA_X0 + 600, COLCHON - 6, 0), "bus": (1300, ASIENTO_Y - 10, 0),
       "ofi": (CX + 10, SILLA_Y - 8, 0), "ban": (VX - 20, VATER_Y - 6, 0)}
def lugar(t, k, pose_=None, d=0):
    x, y, r = LUG[k]
    if d:
        J(f'tl.to("#P", {{x:{x}, y:{y}, rotation:{r}, duration:{d}, ease:"power2.inOut"}}, {t:.2f});')
    else:
        J(f'tl.set("#P", {{x:{x}, y:{y}, rotation:{r}}}, {t:.2f});')
    if pose_:
        rpose(J, "P", pose_, t, 0.01 if not d else d)
J(f'tl.set("#P", {{svgOrigin:"0 0", scale:{S:.2f}}}, 0); tl.set("#O1", {{svgOrigin:"0 0", x:1980, y:{ASIENTO_Y - 10}, scale:{S * 0.97:.2f}}}, 0); tl.set("#O2", {{svgOrigin:"0 0", x:1650, y:{SUELO - CADERA_PIE * 0.95:.0f}, scale:{S * 0.95:.2f}}}, 0);')
rset(J, "O1", "sentMovil2"); rset(J, "O2", "movilPie")
J('tl.set("#O1_glow, #O2_glow", {opacity:0.6}, 0);')
def boca(t, tipo):
    J(f'tl.set("#P_boca", {{opacity:{1 if tipo == "son" else 0}}}, {t:.2f}); tl.set("#P_bocaT", {{opacity:{1 if tipo == "tri" else 0}}}, {t:.2f});')
def movil_vis(t, v): J(f'tl.set("#P_mov", {{opacity:{v}}}, {t:.2f});')
def glow(t, v, d=0.3): J(f'tl.to("#P_glow", {{opacity:{v}, duration:{d}}}, {t:.2f});')
def cansado(t, v, d=0.6):
    J(f'tl.to("#P_ojera", {{opacity:{v}, duration:{d}}}, {t:.2f}); tl.to("#P_rojo", {{opacity:{v * 0.9:.2f}, duration:{d}}}, {t:.2f}); tl.to("#P_par", {{scaleY:{1 + v * 0.9:.2f}, transformOrigin:"50% 0%", duration:{d}}}, {t:.2f});')
def parpadeo(t):
    J(f'tl.to("#P_par", {{scaleY:3.2, transformOrigin:"50% 0%", duration:0.06, yoyo:true, repeat:1}}, {t:.2f});')
for k in range(int(DUR / 3.7)):
    parpadeo(1.3 + k * 3.7)

# ------------------------------------------------------------------ CÁMARA Y RÓTULOS
def plano(t, cx, cy, z, d=0.6, ease="power3.inOut", barrido=False):
    x = min(0, max(1080 - W * z, 540 - cx * z)); y = min(0, max(1920 - 1920 * z, 960 - cy * z))
    if d == 0:
        J(f'tl.set("#cam", {{x:{x:.0f}, y:{y:.0f}, scale:{z:.3f}}}, {t:.2f});'); return
    J(f'tl.to("#cam", {{x:{x:.0f}, y:{y:.0f}, scale:{z:.3f}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
    if barrido:
        J(f'tl.to("#shake", {{filter:"blur(12px)", duration:{d * 0.4:.2f}}}, {t:.2f}); tl.to("#shake", {{filter:"blur(0px)", duration:{d * 0.6:.2f}}}, {t + d * 0.4:.2f});')
        fx("whoosh", t)
def deriva(t, d, dz=0.06):
    J(f'tl.to("#cam", {{scale:"+={dz}", x:"-={540 * dz:.0f}", y:"-={960 * dz:.0f}", duration:{d:.2f}, ease:"none"}}, {t:.2f});')
def golpe_cam(t, f=10):
    J(f'tl.fromTo("#imp", {{x:0, y:0}}, {{keyframes:[{{x:{f}, y:{-f * 0.6:.0f}, duration:0.05}}, {{x:{-f * 0.8:.0f}, y:{f * 0.5:.0f}, duration:0.05}}, {{x:0, y:0, duration:0.08}}], immediateRender:false}}, {t:.2f});')
ICO = {
    "ojo": '<path d="M2,12 Q12,2 22,12 Q12,22 2,12 Z" fill="none" stroke="currentColor" stroke-width="2.4"/><circle cx="12" cy="12" r="3.6" fill="currentColor"/>',
    "reloj": '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M12,7 L12,12 L16,14" stroke="currentColor" stroke-width="2.4" fill="none" stroke-linecap="round"/>',
    "luna": '<path d="M15,3 A9,9 0 1 0 21,15 A7,7 0 1 1 15,3 Z" fill="currentColor"/>',
    "movil": '<rect x="7" y="2" width="10" height="20" rx="2.5" fill="none" stroke="currentColor" stroke-width="2.4"/><circle cx="12" cy="18" r="1.3" fill="currentColor"/>',
    "alerta": '<path d="M12,3 L22,20 L2,20 Z" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"/><path d="M12,9 L12,14" stroke="currentColor" stroke-width="2.4"/><circle cx="12" cy="17" r="1.3" fill="currentColor"/>',
    "cerebro": '<path d="M12,5 C8,2 3,5 4,10 C2,13 4,18 9,18 C10,21 12,20 12,19 C12,20 14,21 15,18 C20,18 22,13 20,10 C21,5 16,2 12,5 Z" fill="none" stroke="currentColor" stroke-width="2.2"/>',
    "cuello": '<circle cx="14" cy="6" r="4" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M12,10 L8,22" stroke="currentColor" stroke-width="2.4"/>',
    "ok": '<path d="M4,12 L10,18 L20,6" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
    "corazon": '<path d="M12,20 L4,12 C1,8 4,3 8,4 C10,4 11,6 12,7 C13,6 14,4 16,4 C20,3 23,8 20,12 Z" fill="none" stroke="currentColor" stroke-width="2.2"/>',
    "bus": '<rect x="3" y="4" width="18" height="14" rx="3" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M3,11 L21,11" stroke="currentColor" stroke-width="2.4"/><circle cx="8" cy="20" r="1.6" fill="currentColor"/><circle cx="16" cy="20" r="1.6" fill="currentColor"/>',
}
def ico(n, color): return f'<svg viewBox="0 0 24 24" width="46" height="46" style="color:{color}">{ICO[n]}</svg>'
NC = [0]
def rotulo(texto, t, hasta, y=1520, color=CY_, kicker="", icono=None, grande=False, son="pop"):
    NC[0] += 1; cid = f"ro{NC[0]}"
    ic = ico(icono, color) if icono else ""
    k = f'<small style="color:{color}">{kicker}</small>' if kicker else ""
    FXL.append(f'<div id="{cid}" class="ro{" gr" if grande else ""}" style="top:{y}px;--c:{color}">{ic}<div>{k}<b>{texto}</b></div></div>')
    J(f'tl.set("#{cid}", {{opacity:0}}, 0); tl.fromTo("#{cid}", {{opacity:0, y:30, clipPath:"inset(0 100% 0 0 round 22px)"}}, {{opacity:1, y:0, clipPath:"inset(0 0% 0 0 round 22px)", duration:0.45, ease:"power3.out", immediateRender:false}}, {t:.2f});')
    J(f'tl.to("#{cid}", {{opacity:0, y:-20, duration:0.25, ease:"power2.in"}}, {hasta:.2f});')
    if son: fx(son, t)
def panel(cid, html, t, hasta, top=640):
    FXL.append(f'<div id="{cid}" class="pan" style="top:{top}px">{html}</div>')
    J(f'tl.set("#{cid}", {{opacity:0}}, 0); tl.fromTo("#{cid}", {{opacity:0, scale:0.85, y:40}}, {{opacity:1, scale:1, y:0, duration:0.45, ease:"power3.out", immediateRender:false}}, {t:.2f}); tl.to("#{cid}", {{opacity:0, scale:0.95, duration:0.25}}, {hasta:.2f});')
    fx("whoosh", t)
def titular(cid, html, t, hasta, top=1000):
    FXL.append(f'<div id="{cid}" class="tit" style="top:{top}px">{html}</div>')
    J(f'tl.set("#{cid}", {{opacity:0}}, 0); tl.fromTo("#{cid} .l", {{yPercent:110}}, {{yPercent:0, duration:0.55, stagger:0.08, ease:"power4.out", immediateRender:false}}, {t:.2f}); tl.set("#{cid}", {{opacity:1}}, {t:.2f}); tl.to("#{cid}", {{opacity:0, duration:0.25}}, {hasta:.2f});')
    fx("golpe", t)
def cabeza_xy(k):
    x, y, r = LUG[k]
    return x + 40, y - cm(RL["T"] + 26)

# ------------------------------------------------------------------ GUION VISUAL
J('tl.set("#cam", {x:0, y:0, scale:1, transformOrigin:"0 0"}, 0);')
hx, hy = cabeza_xy("ofi")
FACE0 = (hx + 90, hy + 80, 2.0)
# 1) gancho: oficina, hora 100, cara azul de la pantalla; mini-montaje
lugar(0, "ofi", "zombi"); movil_vis(0, 0); J('tl.set("#P_glow", {opacity:0.95}, 0);'); cansado(0, 1, 0.01); boca(0, "tri")
plano(0, *FACE0, 0)
deriva(0.05, P("autobus") - 0.4, 0.08)
FXL.append('<div id="tHook" class="tit" style="top:1180px"><span class="m"><span class="l">100 HORAS</span></span><span class="m"><span class="l s">PEGADO A UNA PANTALLA</span></span></div>')
J(f'tl.set("#tHook", {{opacity:1}}, 0); tl.to("#tHook", {{opacity:0, duration:0.25}}, {P("dormir") - 0.1:.2f});')
rotulo("Solo 6 h de sueño", P("dormir") - 0.4, P("autobus") - 0.3, y=1500, color=LI, kicker="CADA NOCHE", icono="luna")
lugar(P("autobus") - 0.15, "bus", "sentMovil"); movil_vis(P("autobus") - 0.15, 1); boca(P("autobus"), "son")
bx_, by_ = cabeza_xy("bus"); plano(P("autobus") - 0.35, bx_ + 120, by_ + 160, 1.6, 0.45, barrido=True)
lugar(P("bano") - 0.15, "ban", "sentMovil")
zx_, zy_ = cabeza_xy("ban"); plano(P("bano") - 0.35, zx_ + 120, zy_ + 160, 1.6, 0.45, barrido=True)
lugar(FE(1) - 1.6, "ofi", "zombi"); movil_vis(FE(1) - 1.6, 0)
plano(FE(1) - 1.8, hx + 150, hy + 260, 1.35, 0.45, barrido=True)
titular("tCuerpo", '<span class="m"><span class="l">¿QUÉ LE PASA</span></span><span class="m"><span class="l">A TU CUERPO?</span></span>', P("cuerpo") - 0.6, FE(1) + 0.2, top=1380)
# 2) rebobinado: hora 0, la cama, el despertador, el móvil
FXL.append('<div id="rebob" class="rebob"><span>◀◀</span> HORA 0</div>')
J(f'tl.set("#rebob", {{opacity:0}}, 0); tl.to("#rebob", {{opacity:1, duration:0.15}}, {R0:.2f}); tl.to("#rebob", {{opacity:0, duration:0.3}}, {R1:.2f});')
J(f'tl.to("#cam", {{filter:"saturate(0.3) contrast(1.2)", duration:0.15}}, {R0:.2f}); tl.to("#cam", {{filter:"saturate(1) contrast(1)", duration:0.3}}, {R1 - 0.1:.2f});')
fx("rebobina", R0)
cansado(R1 - 0.3, 0, 0.3); boca(R1, "son"); glow(R1, 0)
lugar(R0 + 0.5, "cama", "tumbado"); movil_vis(R0 + 0.5, 0)
J(f'tl.set("#mantas", {{opacity:1}}, {R0 + 0.5:.2f}); tl.set("#mantas", {{opacity:0}}, {P("movil") - 0.9:.2f});')
plano(R0 + 0.45, CAMA_X0 + 520, COLCHON - 120, 1.3, 0.55, barrido=True)
J(f'tl.fromTo("#despN", {{scale:1, transformOrigin:"50% 50%"}}, {{scale:1.3, transformOrigin:"50% 50%", duration:0.12, yoyo:true, repeat:9, immediateRender:false}}, {P("alarma") - 0.1:.2f});')
fx("alarma", P("alarma"))
rotulo("06:30", P("seis", 2) - 0.1, P("alarma") + 0.8, y=1500, color=AM, icono="reloj", grande=True, son=None)
lugar(P("movil") - 0.9, "camaSent", "sentMovil", d=0.6)
movil_vis(P("movil") - 0.4, 1); glow(P("movil") - 0.3, 0.9)
plano(P("movil") - 0.6, LUG["camaSent"][0] + 160, LUG["camaSent"][1] - 230, 2.2, 0.6)
rotulo("Lo primero: el móvil", P("movil") - 0.1, FE(2) + 0.2, y=1520, color=CY_, icono="movil")
# 3) autobús: cuello doblado
lugar(F(3) - 0.1, "bus", "sentMovil"); boca(F(3), "son")
plano(F(3) - 0.3, bx_ + 130, by_ + 200, 1.45, 0.5, barrido=True)
for g, dist in (("vLej", 1200), ("vCer", 2600), ("vFar", 4200)):
    J(f'tl.fromTo("#{g}", {{x:0}}, {{x:{-dist}, duration:{FE(4) - F(3) + 0.6:.2f}, ease:"none", immediateRender:false}}, {F(3) - 0.1:.2f});')
J(f'tl.fromTo("#P_fl, #O1_fl, #O2_fl", {{y:0}}, {{y:-1.2, duration:0.17, yoyo:true, repeat:{int((FE(4) - F(3)) / 0.17)}, ease:"sine.inOut", immediateRender:false}}, {F(3):.2f});')
panel("pCuello", '<svg viewBox="0 0 520 360" width="760" height="526"><rect width="520" height="360" rx="26" fill="#0d0b1a" opacity="0.92"/>'
      + "".join(f'<g transform="translate({70 + i * 120},270)"><path d="M0,0 L0,-70" stroke="#e8f4ff" stroke-width="10" stroke-linecap="round"/>'
                f'<g transform="rotate({a}) "><circle cx="0" cy="-102" r="32" fill="#e8b48c"/><path d="M-20,-128 Q0,-142 22,-124 Q8,-122 -2,-112 Z" fill="#2a1c14"/></g>'
                f'<text x="0" y="40" text-anchor="middle" font-family="Inter" font-weight="900" font-size="34" fill="{c}">{kg} kg</text>'
                f'<text x="0" y="74" text-anchor="middle" font-family="Inter" font-weight="800" font-size="20" fill="#9fb3c8">{a}°</text></g>'
                for i, (a, kg, c) in enumerate(((0, 5, "#35d987"), (15, 12, "#ffc24a"), (30, 18, "#ff9a5a"), (60, 27, "#ff5a4f"))))
      + '</svg>', P("cuello") - 0.4, FE(3) + 0.3, top=620)
rotulo("Más de 20 kg en el cuello", P("veinte") - 0.2, FE(3) + 0.2, y=1520, color=RJ, kicker="CABEZA AGACHADA", icono="cuello")
# 4) mareo
plano(F(4) - 0.1, bx_ + 60, by_ + 60, 2.2, 0.6)
rotulo("Los ojos, quietos", P("ojos") - 0.1, P("cuerpo", 2) - 0.1, y=1480, color=CY_, icono="ojo")
rotulo("El cuerpo, en movimiento", P("cuerpo", 2) - 0.1, P("mareo") - 0.2, y=1600, color=AM, icono="bus")
J(f'tl.to("#shake", {{rotation:2.2, duration:0.55, yoyo:true, repeat:3, ease:"sine.inOut"}}, {P("mareo") - 0.3:.2f});')
J(f'tl.to("#cam", {{filter:"hue-rotate(25deg) saturate(1.3)", duration:0.4, yoyo:true, repeat:1}}, {P("mareo") - 0.2:.2f});')
boca(P("mareo"), "tri"); cansado(P("mareo"), 0.4)
titular("tMareo", '<span class="m"><span class="l r">MAREO</span></span>', P("mareo") - 0.15, FE(4) + 0.3, top=1420)
# 5) oficina: parpadeos
lugar(F(5) - 0.1, "ofi", "teclea"); movil_vis(F(5) - 0.1, 0); cansado(F(5) - 0.1, 0, 0.01); glow(F(5), 0.75); boca(F(5), "son")
plano(F(5) - 0.3, MX - 160, SUELO - 520, 1.15, 0.6, barrido=True)
k, tt = 0, F(5)
while tt < FE(6) - 0.1:
    rpose(J, "P", "teclea" if k % 2 == 0 else "teclea2", tt, 0.14, "sine.inOut", solo={"uaN", "faN", "uaF", "faF"}); tt += 0.26; k += 1
J(f'tl.to("#agujaO", {{rotation:720, svgOrigin:"0 0", duration:{FE(6) - F(5):.2f}, ease:"none"}}, {F(5):.2f});')
J(f'tl.fromTo("#pantCont", {{y:0}}, {{y:-90, duration:{FE(6) - F(5):.2f}, ease:"none", immediateRender:false}}, {F(5):.2f});')
rotulo("12 h delante del ordenador", P("doce") - 0.1, P("normalmente") - 0.2, y=1520, color=CY_, icono="reloj")
panel("pOjo", '<svg viewBox="0 0 420 250" width="700" height="417"><defs><radialGradient id="iris" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#2a1a14"/><stop offset="0.35" stop-color="#5a3a1c"/><stop offset="0.8" stop-color="#8a5a2c"/><stop offset="1" stop-color="#3a2410"/></radialGradient>'
      '<clipPath id="cOjo"><path d="M20,125 Q210,-20 400,125 Q210,270 20,125 Z"/></clipPath></defs>'
      '<rect width="420" height="250" rx="26" fill="#0d0b1a" opacity="0.92"/>'
      '<g clip-path="url(#cOjo)"><rect width="420" height="250" fill="#fbf6f2"/><g id="venas" opacity="0">'
      + "".join(f'<path d="M{x0},{y0} q{dx},{dy} {dx * 2},{dy * 0.4}" stroke="#e0464a" stroke-width="2.5" fill="none" opacity="0.8"/>' for x0, y0, dx, dy in ((30, 120, 40, -14), (40, 150, 36, 10), (390, 120, -40, -12), (380, 150, -34, 12), (60, 95, 30, 16), (360, 95, -30, 16)))
      + '<rect width="420" height="250" fill="#ff6a6a" opacity="0.25"/></g><circle cx="210" cy="125" r="70" fill="url(#iris)"/><circle cx="210" cy="125" r="28" fill="#0b0b10"/><circle cx="188" cy="102" r="12" fill="#fff" opacity="0.9"/>'
      '<g id="parpado"><rect x="0" y="-260" width="420" height="260" fill="#e8b48c"/><path d="M0,0 L420,0" stroke="#2a1c14" stroke-width="6"/></g></g>'
      '<path d="M20,125 Q210,-20 400,125" stroke="#2a1c14" stroke-width="6" fill="none"/></svg>'
      '<div class="cnt"><b id="parpN">15</b><small>PARPADEOS POR MINUTO</small></div>', P("parpadeas") - 0.3, FE(6) + 0.3, top=600)
J(f'tl.set("#parpado", {{y:0}}, 0);')
k, tk = 0, P("parpadeas") + 0.2
while tk < FE(6):
    J(f'tl.to("#parpado", {{y:250, duration:0.07, yoyo:true, repeat:1, ease:"power2.in"}}, {tk:.2f});'); tk += 0.45 if tk < P("cinco") else 1.4
J(f'const pb = {{v:15}}; tl.to(pb, {{v:5, duration:1.2, ease:"power2.inOut", onUpdate:() => {{ const e = document.getElementById("parpN"); e.textContent = Math.round(pb.v); e.style.color = pb.v < 9 ? "#ff5a4f" : "#fff"; }}}}, {P("cinco") - 0.6:.2f});')
fx("cuenta", P("cinco") - 0.6)
# 6) ojo seco y borroso
J(f'tl.to("#venas", {{opacity:1, duration:1.0}}, {P("seca") - 0.2:.2f});'); cansado(P("rojo") - 0.2, 0.8)
J(f'tl.to("#cam", {{filter:"blur(6px)", duration:0.5}}, {P("borroso") - 0.3:.2f}); tl.to("#cam", {{filter:"blur(0px)", duration:0.5}}, {FE(6) + 0.2:.2f});')
rotulo("Seco · escuece · rojo", P("seca") - 0.1, P("borroso") - 0.4, y=1520, color=RJ, icono="ojo")
titular("tBorr", '<span class="m"><span class="l">BORROSO</span></span>', P("borroso") - 0.3, FE(6) + 0.2, top=1440)
# 7) baño con el móvil
lugar(F(7) - 0.1, "ban", "sentMovil"); movil_vis(F(7) - 0.1, 1); glow(F(7), 0.9); cansado(F(7) - 0.1, 0.2, 0.01); boca(F(7), "son")
plano(F(7) - 0.3, zx_ + 140, zy_ + 220, 1.4, 0.5, barrido=True)
deriva(F(7) + 0.3, FE(7) - F(7) - 0.4, 0.12)
rotulo("Estudio de 2025", P("estudio") - 0.1, P("cuarenta") - 0.2, y=1480, color=CY_, icono="alerta")
titular("t46", '<span class="m"><span class="l r">+46 %</span></span><span class="m"><span class="l s">RIESGO DE HEMORROIDES</span></span>', P("cuarenta") - 0.2, FE(7) + 0.2, top=1380)
# 8) noche: melatonina, 6 h, vuelta a empezar
lugar(F(8) - 0.1, "camaSent", "sentMovil"); movil_vis(F(8) - 0.1, 1); glow(F(8), 0.95)
J(f'tl.to("#luzMes", {{opacity:0.0}}, {F(8):.2f});')
plano(F(8) - 0.3, LUG["camaSent"][0] + 160, LUG["camaSent"][1] - 230, 1.9, 0.5, barrido=True)
panel("pMel", '<b>MELATONINA</b><div class="barraM"><i id="melB"></i></div><small>LA HORMONA QUE TE DICE «A DORMIR»</small>', P("melatonina") - 0.3, P("tarde", 2) + 0.3, top=640)
J(f'tl.fromTo("#melB", {{width:"90%"}}, {{width:"22%", duration:1.4, ease:"power2.inOut", immediateRender:false}}, {P("melatonina") + 0.3:.2f});')
lugar(P("tarde", 2) - 0.2, "cama", "tumbado", d=0.5); movil_vis(P("tarde", 2) + 0.2, 0); glow(P("tarde", 2), 0)
J(f'tl.set("#mantas", {{opacity:1}}, {P("tarde", 2) + 0.2:.2f});')
plano(P("tarde", 2) - 0.2, CAMA_X0 + 520, COLCHON - 120, 1.3, 0.6)
J(f'tl.to("#noche", {{opacity:0.55, duration:0.4}}, {P("seis", 4) - 0.3:.2f}); tl.to("#noche", {{opacity:0, duration:0.3}}, {P("vuelta") - 0.1:.2f});')
rotulo("6 horas", P("seis", 4) - 0.2, P("vuelta") - 0.1, y=1500, color=LI, icono="luna", grande=True, son=None)
J(f'tl.fromTo("#despN", {{scale:1, transformOrigin:"50% 50%"}}, {{scale:1.3, transformOrigin:"50% 50%", duration:0.12, yoyo:true, repeat:5, immediateRender:false}}, {P("vuelta") - 0.1:.2f});'); fx("alarma", P("vuelta"))
titular("tVuelta", '<span class="m"><span class="l a">Y VUELTA A EMPEZAR</span></span>', P("vuelta") - 0.1, FE(8) + 0.25, top=1420)
J(f'tl.set("#mantas", {{opacity:0}}, {FE(8) + 0.3:.2f});')
# 9) día 3: irritable, olvidos, errores
lugar(F(9) - 0.1, "ofi", "zombi"); movil_vis(F(9) - 0.1, 0); glow(F(9), 0.95); cansado(F(9), 0.7, 0.4); boca(F(9), "tri")
J(f'tl.to(".pap", {{opacity:1, duration:0.01, stagger:0.12}}, {F(9):.2f});')
plano(F(9) - 0.3, MX - 160, SUELO - 520, 1.15, 0.5, barrido=True)
titular("tD3", '<span class="m"><span class="l a">DÍA 3</span></span>', P("dia") - 0.15, P("irritable") - 0.1, top=1420)
J(f'tl.to("#P_ceja", {{attr:{{d:"M6.5,-27.4 Q10,-29.8 13.6,-29.6"}}, duration:0.2}}, {P("irritable") - 0.1:.2f});')
k, tt = 0, P("irritable")
while tt < FE(9) - 0.1:
    rpose(J, "P", "teclea" if k % 2 == 0 else "teclea2", tt, 0.12, "sine.inOut", solo={"uaN", "faN", "uaF", "faF"}); tt += 0.2; k += 1
panel("pErr", '<div class="err">Error al guardar</div><div class="err q">¿Qué iba a hacer?</div><div class="err">Error en la fórmula</div>', P("errores") - 0.9, FE(9) + 0.2, top=640)
rotulo("Irritable · olvidos · errores", P("irritable") - 0.1, P("peor") - 0.2, y=1520, color=RJ, icono="alerta")
rotulo("Y casi no lo notas", P("peor") - 0.2, FE(9) + 0.2, y=1520, color=AM, icono="cerebro")
# 10) 6 h × 14 noches = 1 noche sin dormir
plano(F(10) - 0.1, hx + 120, hy + 120, 1.8, 0.6)
panel("pSue", '<div class="noches">' + "".join(f'<i id="n{k}">{ICO["luna"].replace("currentColor", "#b98cff").join(["<svg viewBox=\"0 0 24 24\" width=\"64\" height=\"64\">", "</svg>"])}</i>' for k in range(14)) + '</div><b>6 h × 14 noches</b><small>= UNA NOCHE ENTERA SIN DORMIR</small>', F(10) + 0.2, FE(10) + 0.3, top=640)
J(f'tl.fromTo("#pSue i", {{opacity:0.12}}, {{opacity:1, duration:0.05, stagger:0.12, immediateRender:false}}, {F(10) + 0.4:.2f});'); fx("cuenta", F(10) + 0.4)
# 11) vibración fantasma
rpose(J, "P", "bolsillo", P("vibra") - 0.2, 0.3)
plano(P("vibra") - 0.3, CX + 120, SILLA_Y - 60, 2.2, 0.45)
FXL.append('<div id="vibIco" class="vibIco"><i></i><i></i><i></i></div>')
J(f'tl.set("#vibIco", {{opacity:0}}, 0); tl.set("#vibIco", {{opacity:1}}, {P("vibra"):.2f}); tl.fromTo("#vibIco i", {{scale:0.4, opacity:1}}, {{scale:1.8, opacity:0, duration:0.5, stagger:0.15, repeat:2, immediateRender:false}}, {P("vibra"):.2f}); tl.set("#vibIco", {{opacity:0}}, {P("nada") + 0.2:.2f});')
fx("vibra", P("vibra"))
titular("tNada", '<span class="m"><span class="l">NADA.</span></span>', P("nada") - 0.05, P("fantasma") - 0.3, top=1420)
rotulo("Vibración fantasma", P("fantasma") - 0.3, FE(11) + 0.25, y=1520, color=LI, icono="movil")
rpose(J, "P", "zombi", FE(11), 0.3)
# 12) hora 60: espalda y cuello
plano(F(12) - 0.1, CX + 60, SILLA_Y - 200, 1.5, 0.6)
rpose(J, "P", "cuello", P("cuello", 2) - 0.2, 0.35); boca(P("cuello", 2), "tri")
FXL.append('<div id="dolor" class="dolor"><i class="d1"></i><i class="d2"></i></div>')
J(f'tl.set("#dolor", {{opacity:0}}, 0); tl.to("#dolor", {{opacity:1, duration:0.2}}, {P("espalda") - 0.1:.2f}); tl.fromTo("#dolor i", {{scale:0.6, opacity:0.9}}, {{scale:1.5, opacity:0.2, duration:0.6, repeat:5, immediateRender:false}}, {P("espalda") - 0.1:.2f}); tl.to("#dolor", {{opacity:0, duration:0.2}}, {FE(12) + 0.2:.2f});')
titular("tH60", '<span class="m"><span class="l a">HORA 60</span></span>', P("sesenta") - 0.15, P("espalda") - 0.1, top=1420)
rotulo("16 h al día sentado", P("dieciseis") - 0.2, FE(12) + 0.2, y=1520, color=RJ, icono="reloj")
# 13) más horas no es más trabajo
rpose(J, "P", "zombi", F(13), 0.3)
plano(F(13) - 0.1, MX - 160, SUELO - 520, 1.15, 0.6)
panel("pGraf", '<svg viewBox="0 0 420 270" width="720" height="463"><rect width="420" height="270" rx="24" fill="#0d0b1a" opacity="0.92"/><path d="M50,225 L390,225 M50,225 L50,25" stroke="#5a6a80" stroke-width="3"/>'
      + "".join(f'<path d="M50,{225 - k * 40} L390,{225 - k * 40}" stroke="#2a3040" stroke-width="1"/>' for k in range(1, 5))
      + '<path id="curva" d="M50,220 L200,95 C240,66 300,60 390,57" stroke="#35d987" stroke-width="7" fill="none" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" stroke-linecap="round"/>'
      '<path d="M200,225 L200,35" stroke="#ffc24a" stroke-width="3" stroke-dasharray="8 6"/><text x="208" y="48" font-family="Inter" font-weight="900" font-size="20" fill="#ffc24a">50 h / semana</text>'
      '<text x="330" y="252" font-family="Inter" font-weight="800" font-size="15" fill="#9fb3c8">HORAS</text><text x="58" y="40" font-family="Inter" font-weight="800" font-size="15" fill="#9fb3c8">LO QUE RINDES</text></svg>', F(13) + 0.5, FE(13) + 0.3, top=620)
J(f'tl.to("#curva", {{strokeDashoffset:0, duration:2.2, ease:"power1.inOut"}}, {F(13) + 0.7:.2f});')
rotulo("Más horas ≠ más trabajo", P("menos") - 0.4, FE(13) + 0.2, y=1520, color=AM, icono="alerta")
# 14) OMS: +35 % ictus
plano(F(14) - 0.1, hx + 120, hy + 120, 1.9, 0.6)
rotulo("OMS", P("oms") - 0.1, P("treinta") - 0.3, y=1520, color=CY_, kicker="ORGANIZACIÓN MUNDIAL DE LA SALUD", icono="corazon")
panel("pIctus", '<svg viewBox="0 0 300 220" width="380" height="279"><path d="M150,30 C90,0 30,30 35,90 C10,120 30,180 90,185 C110,215 145,205 150,190 C155,205 190,215 210,185 C270,180 290,120 265,90 C270,30 210,0 150,30 Z" fill="#ff9ec7" stroke="#fff" stroke-width="5"/>'
      '<path d="M150,35 L150,185 M80,80 q30,20 10,50 M220,80 q-30,20 -10,50" stroke="#d1608f" stroke-width="6" fill="none" stroke-linecap="round"/>'
      '<path id="rayo" d="M175,55 L135,118 L165,118 L125,180" stroke="#ff5a4f" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'
      '<b class="r">+35 % riesgo de ictus</b><small>TRABAJANDO 55 H O MÁS A LA SEMANA, DURANTE AÑOS</small>', P("treinta") - 0.3, FE(14) + 0.3, top=620)
golpe_cam(P("treinta") + 0.3, 12); fx("golpe", P("treinta") + 0.3)
# 15) hora 100
plano(F(15) - 0.1, *FACE0, 0.6)
cansado(F(15), 1, 0.6); rpose(J, "P", "cabeza", P("cabeza", 3) - 0.2, 0.35)
titular("tH100", '<span class="m"><span class="l a">HORA 100</span></span>', P("cien", 2) - 0.15, P("rojos") - 0.1, top=1180)
for i, (w, txt, ic) in enumerate((("rojos", "Ojos rojos", "ojo"), ("cabeza3", "Dolor de cabeza", "cerebro"), ("destrozado", "Cuello destrozado", "cuello"), ("cansancio", "Cansancio que no se va", "alerta"))):
    tw = P("cabeza", 3) if w == "cabeza3" else P(w)
    rotulo(txt, tw - 0.15, FE(15) + 0.25, y=1060 + i * 128, color=RJ, icono=ic)
rpose(J, "P", "zombi", FE(15) + 0.1, 0.4)
# 16) la buena noticia: 20-20-20 (mira por la ventana)
rpose(J, "P", "arriba", F(16) + 0.2, 0.6); cansado(F(16), 0, 1.5); boca(F(16) + 0.3, "son"); glow(F(16), 0.3)
J(f'tl.set("#P_ceja", {{attr:{{d:"M6.5,-28.4 Q10,-29.6 13.6,-28.2"}}}}, {F(16):.2f});')
plano(F(16) - 0.1, MX - 300, SUELO - 620, 1.0, 1.0)
rotulo("Casi todo se recupera descansando", P("buena") - 0.1, PL("cada") - 0.2, y=1520, color=VE, icono="ok")
panel("p20", '<b class="v">20 · 20 · 20</b><small>CADA 20 MINUTOS, MIRA ALGO LEJANO DURANTE 20 SEGUNDOS</small>', PL("cada") - 0.2, FE(16) + 0.3, top=700)
# 17) cierre: levanta la vista; vuelve al plano del principio
plano(F(17) - 0.1, *FACE0, 0.8)
rpose(J, "P", "zombi", F(17) + 0.1, 0.4); glow(F(17), 0.95); boca(F(17), "tri")
rpose(J, "P", "arriba", P("levantar") - 0.1, 0.5, "power2.out"); boca(P("levantar"), "son")
rpose(J, "P", "zombi", DUR - 1.3, 0.6); cansado(DUR - 1.3, 1, 0.6); boca(DUR - 1.2, "tri")
J(f'tl.set("#tHook .l", {{yPercent:110}}, {DUR - 1.2:.2f}); tl.set("#tHook", {{opacity:1}}, {DUR - 1.2:.2f}); tl.to("#tHook .l", {{yPercent:0, duration:0.5, stagger:0.08, ease:"power4.out"}}, {DUR - 1.1:.2f});')
J(f'tl.fromTo("#shake", {{x:-3, y:2}}, {{x:3, y:-2, duration:2.8, yoyo:true, repeat:{int(DUR / 2.8)}, ease:"sine.inOut", immediateRender:false}}, 0);')
J(f'tl.fromTo(".vapor", {{y:0, opacity:0.5}}, {{y:-20, opacity:0, duration:1.6, repeat:{int(DUR / 1.6)}, ease:"none", immediateRender:false}}, 0);')
J(f'tl.fromTo("#luzPant", {{opacity:0.75}}, {{opacity:1, duration:0.9, yoyo:true, repeat:{int(DUR / 0.9)}, ease:"sine.inOut", immediateRender:false}}, 0);')

# ------------------------------------------------------------------ HUD
J('const hv = {v:100};')
kf = [f'{{v:{H(tb):.3f}, duration:{tb - ta:.3f}, ease:"none"}}' for ta, tb in zip(TS, TS[1:])]
J('''function pinta(h){
  document.getElementById("hN").textContent = Math.round(h); document.getElementById("hB").style.width = h + "%";
  document.getElementById("dN").textContent = Math.min(6, Math.floor(h / 18) + 1);
  document.getElementById("sN").textContent = "−" + Math.min(10, Math.floor(h / 18) * 2) + " h";
}''')
J(f'tl.to(hv, {{keyframes:[{",".join(kf)}], onUpdate:() => pinta(hv.v)}}, 0);')
J('pinta(100);')
HUD = ('<div id="hud"><div class="c1"><small>HORAS DE PANTALLA</small><b><span id="hN">100</span><em>/100</em></b><div class="barra"><i id="hB"></i></div></div>'
       '<div class="c2"><small>DÍA</small><b id="dN">6</b></div><div class="c2"><small>SUEÑO PERDIDO</small><b id="sN" class="rojo">−10 h</b></div></div>')

# ------------------------------------------------------------------ montaje
MANTAS = f'<g id="mantas" opacity="0">{"".join(CAMA_TOP)}</g>'
svg = (f'<g id="mundo">{"".join(M)}{MESA_FONDO}{SILLA}{asiento(1300).replace(asiento(1300), "")}{figO1}{figO2}{VATER}{figP}{MANTAS}{MESA_FRENTE}'
       f'<rect id="noche" x="0" y="0" width="{W}" height="1920" fill="#02040e" opacity="0"/></g>')
_S = open(os.path.join(BASE, "_subs.py"), encoding="utf-8").read()
exec(re.sub(r"CLAVE = set\(.*?\]\)", lambda m: 'CLAVE = set(norm(w) for w in ["cien", "pantalla", "seis", "dormir", "cuerpo", "movil", "cuello", "veinte", "kilos", "mareo", "doce", "quince", "cinco", "seca", "rojo", "borroso", "cuarenta", "hemorroides", "melatonina", "tres", "irritable", "errores", "noche", "fantasma", "sesenta", "dieciseis", "menos", "oms", "treinta", "ictus", "rojos", "cabeza", "destrozado", "cansancio", "recupera", "lejano", "vista"])', _S, count=1, flags=re.S))

html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#0a0716}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;background:#0a0716;color:{TX}}}
#imp,#shake{{position:absolute;inset:0}} #cam{{position:absolute;left:0;top:0;width:{W}px;height:1920px;transform-origin:0 0}}
#fxl{{position:absolute;inset:0;z-index:58;pointer-events:none}}
.ro{{position:absolute;left:60px;right:60px;display:flex;align-items:center;gap:20px;padding:20px 26px;border-radius:22px;background:rgba(12,10,24,0.82);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.14);box-shadow:0 20px 50px rgba(0,0,0,0.4), inset 6px 0 0 var(--c)}}
.ro small{{display:block;font:800 18px Inter;letter-spacing:4px;margin-bottom:4px}} .ro b{{display:block;font:800 50px/1.08 Inter;letter-spacing:-1px;color:#fff}}
.ro.gr b{{font-size:96px;letter-spacing:-3px;font-variant-numeric:tabular-nums}}
.tit{{position:absolute;left:0;right:0;text-align:center;pointer-events:none}} .tit .m{{display:block;overflow:hidden;line-height:1.02;padding:0 0 12px}}
.tit .l{{display:inline-block;font:900 128px/1.02 Inter;letter-spacing:-5px;color:#fff;text-shadow:0 10px 40px rgba(0,0,0,0.55)}}
.tit .l.s{{font-size:44px;letter-spacing:6px;font-weight:800;color:#d9e6f5}} .tit .l.r{{color:{RJ}}} .tit .l.a{{color:{AM}}}
.pan{{position:absolute;left:0;right:0;margin:0 auto;width:max-content;max-width:1000px;padding:22px 26px;border-radius:28px;background:rgba(12,10,24,0.86);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.14);text-align:center;box-shadow:0 30px 60px rgba(0,0,0,0.45)}}
.pan b{{display:block;font:900 56px Inter;letter-spacing:-1px;color:#fff;margin-top:8px}} .pan b.r{{color:{RJ}}} .pan b.v{{color:{VE};font-size:110px;letter-spacing:-3px}}
.pan small{{display:block;font:800 20px Inter;letter-spacing:4px;color:#b9c0d6;margin-top:6px}}
.cnt b{{font:900 120px/1 Inter;font-variant-numeric:tabular-nums;color:#fff}}
.barraM{{width:640px;height:30px;border-radius:15px;background:rgba(255,255,255,0.12);overflow:hidden;margin:14px auto}} .barraM i{{display:block;height:100%;background:linear-gradient(90deg,{LI},#7a5bd6);border-radius:15px}}
.err{{margin:12px 0;padding:16px 26px;border-radius:16px;background:rgba(255,90,79,0.14);border:2px solid {RJ};font:800 40px Inter;color:#fff;text-align:left}} .err.q{{border-color:{AM};background:rgba(255,194,74,0.12)}}
.noches{{display:grid;grid-template-columns:repeat(7,1fr);gap:10px;margin-bottom:6px}}
.vibIco{{position:absolute;left:540px;top:1080px}} .vibIco i{{position:absolute;left:-70px;top:-70px;width:140px;height:140px;border-radius:50%;border:6px solid {LI}}}
.dolor{{position:absolute;inset:0}} .dolor i{{position:absolute;width:150px;height:150px;border-radius:50%;background:radial-gradient(circle, rgba(255,90,79,0.65), rgba(255,90,79,0) 70%)}} .dolor .d1{{left:470px;top:620px}} .dolor .d2{{left:400px;top:900px}}
.rebob{{position:absolute;left:0;right:0;top:1080px;text-align:center;font:900 120px Inter;letter-spacing:-4px;color:#fff;text-shadow:0 8px 30px rgba(0,0,0,0.7)}} .rebob span{{color:{AM}}}
#hud{{position:absolute;left:40px;right:40px;top:488px;z-index:60;display:flex;gap:12px}}
#hud > div{{padding:12px 18px;border-radius:18px;background:rgba(12,10,24,0.8);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.14)}}
#hud .c1{{flex:1}} #hud small{{display:block;font:800 15px Inter;letter-spacing:3px;color:#9aa6c0}} #hud b{{font:900 40px/1.1 Inter;color:#fff;font-variant-numeric:tabular-nums}} #hud em{{font-style:normal;font-size:24px;color:#6a7690}}
#hud .barra{{height:8px;border-radius:4px;background:rgba(255,255,255,0.12);overflow:hidden;margin-top:6px}} #hud .barra i{{display:block;height:100%;background:linear-gradient(90deg,{CY_},{RJ})}}
#hud .c2{{text-align:center;min-width:150px}} #hud .rojo{{color:{RJ}}}
#grano{{position:absolute;inset:0;z-index:57;pointer-events:none;opacity:0.045;background:url(assets/grano.png);mix-blend-mode:overlay}}
#vineta{{position:absolute;inset:0;z-index:56;pointer-events:none;background:radial-gradient(120% 80% at 50% 60%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.5))}}
#tono{{position:absolute;inset:0;z-index:55;pointer-events:none;background:linear-gradient(180deg, rgba(40,20,80,0.18), rgba(0,0,0,0) 40%, rgba(255,140,60,0.06));mix-blend-mode:soft-light}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:560px;z-index:55;pointer-events:none;background:linear-gradient(rgba(6,4,14,0.94) 45%, rgba(6,4,14,0))}}
#marca{{position:absolute;left:0;right:0;top:1820px;text-align:center;font:700 28px Inter;color:#ffffff;opacity:0.32;pointer-events:none;z-index:61}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 62px Inter;color:rgba(255,255,255,0.42);line-height:1.22;text-shadow:0 3px 12px rgba(0,0,0,0.6)}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:3px solid #4ea3ff;border-radius:6px;background:rgba(78,163,255,0.18);opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="imp"><div id="shake"><div id="cam"><svg width="{W}" height="1920" viewBox="0 0 {W} 1920" style="position:absolute;left:0;top:0"><defs>{"".join(DEFS)}</defs>{svg}</svg></div></div></div>
  <div id="tono"></div><div id="topsombra"></div><div id="vineta"></div><div id="grano"></div>
  <div id="fxl">{"".join(FXL)}</div>
  {HUD}
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
json.dump([[0, 0.12], [DUR, 0.12]], open(os.path.join(BASE, "ambiente.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones")

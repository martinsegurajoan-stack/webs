#!/usr/bin/env python3
"""«¿Qué pasaría si un partido de tenis dura más de 20 horas?» (el tie-break no acaba nunca) — informativo, UN SOLO PLANO.
Cámara de televisión fija detrás del fondo de pista (pista dura azul tipo US Open). El tiempo pasa alrededor: el cielo,
los focos, el público que se va, el cansancio de los jugadores, el marcador y el reloj.
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
tl, FX, DEFS, OVR = [], [], [], []
def J(s): tl.append(s)
def fx(k, t): FX.append([k, round(t, 3)])
rnd = random.Random(11)
CY_, RJ, AM, VE, TX = "#4fd1ff", "#ff5a4f", "#ffc24a", "#35d987", "#eef4fb"

# ------------------------------------------------------------------ cámara (perspectiva de TV detrás del fondo)
HC, ZC, TH, FOC, CYP = 16.0, -26.0, math.radians(38), 1700.0, 1202.4
_S, _C = math.sin(TH), math.cos(TH)
def PR(X, Y, Z):
    dy, dz = Y - HC, Z - ZC
    dep = -dy * _S + dz * _C
    up = dy * _C + dz * _S
    return 540 + FOC * X / dep, CYP - FOC * up / dep, FOC / dep
def pt(X, Y, Z):
    x, y, _ = PR(X, Y, Z)
    return f"{x:.1f},{y:.1f}"
def poly(pts, extra=""):
    return f'<path d="M{" L".join(pt(*p) for p in pts)} Z" {extra}/>'
def suelo_rect(x0, x1, z0, z1, extra):
    return poly([(x0, 0, z0), (x1, 0, z0), (x1, 0, z1), (x0, 0, z1)], extra)
SC = 0.0195                                   # escala de las personas (algo más grandes que la realidad para que se lean)
def esc(Z, X=0.0): return PR(X, 0, Z)[2] * SC

# ------------------------------------------------------------------ el tiempo de la historia (horas de tie-break)
R0 = F(2) + 0.15                              # rebobinado: de las 20 h al inicio (13:00)
R1 = R0 + 1.7
T_FOCOS = P("focos")
ANCH = [(0, 20.0), (R0, 20.0), (R1, 0.0), (F(8), 3.0), (F(10), 6.0), (T_FOCOS, 6.3), (F(14), 11.0), (F(16), 14.0),
        (F(22), 17.5), (DUR, 20.0)]
def H(t):
    for (a, va), (b, vb) in zip(ANCH, ANCH[1:]):
        if a <= t <= b:
            return va + (vb - va) * (t - a) / max(1e-6, b - a)
    return ANCH[-1][1]
def lerpf(pts, x):
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if a <= x <= b:
            return va + (vb - va) * (x - a) / max(1e-6, b - a)
    return pts[-1][1] if x > pts[-1][0] else pts[0][1]
def LH(t): return (13 + H(t)) % 24
def luzdia(t): return lerpf([(0, 0), (5.2, 0), (6.4, 0.4), (7.6, 1), (18.2, 1), (19.6, 0.3), (20.6, 0), (24, 0)], LH(t))
def ocaso(t): return lerpf([(0, 0), (17.6, 0), (18.9, 1), (19.9, 0.6), (20.7, 0), (24, 0)], LH(t))
def alba(t): return lerpf([(0, 0), (4.9, 0), (6.1, 1), (7.3, 0.5), (8.4, 0), (24, 0)], LH(t))
def focos(t, d=0.0): return 1.0 if 6.3 + d <= H(t) <= 18.6 else 0.0
def publico(t): return 1.0 if H(t) <= 11 else max(0.12, 1 - 0.88 * (H(t) - 11) / 6.5)
def cansancio(t): return min(1.0, H(t) / 20.0)
TS = sorted(set([round(i * 0.25, 2) for i in range(int(DUR / 0.25) + 1)] + [round(R0 + i * 0.05, 2) for i in range(int((R1 - R0) / 0.05) + 2)] + [DUR]))
def pista(sel, fn, prop="opacity", dec=3):
    """Una animación con fotogramas clave muestreados de una función del tiempo (cielo, focos, público…)."""
    vals = [(t, round(fn(t), dec)) for t in TS]
    kf, last, acc = [], vals[0][1], 0.0
    for (ta, va), (tb, vb) in zip(vals, vals[1:]):
        acc += tb - ta
        if vb != last:
            kf.append(f'{{{prop}:{vb}, duration:{acc:.3f}, ease:"none"}}'); last = vb; acc = 0.0
    if acc > 0:
        kf.append(f'{{{prop}:{last}, duration:{acc:.3f}, ease:"none"}}')
    J(f'tl.set("{sel}", {{{prop}:{vals[0][1]}}}, 0); tl.to("{sel}", {{keyframes:[{",".join(kf)}]}}, 0);')

def entra(sel, t, frm="opacity:0, y:24", d=0.4, ease="power3.out"):
    J(f'tl.set("{sel}", {{opacity:0}}, 0); tl.fromTo("{sel}", {{{frm}}}, {{opacity:1, x:0, y:0, scale:1, duration:{d}, ease:"{ease}", immediateRender:false}}, {t:.2f});')
def sale(sel, t, d=0.3):
    J(f'tl.to("{sel}", {{opacity:0, duration:{d}, ease:"power1.in"}}, {t:.2f});')

# ------------------------------------------------------------------ degradados
DEFS += [
    '<linearGradient id="skyDia" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2f7fd0"/><stop offset="1" stop-color="#9fd0f2"/></linearGradient>',
    '<linearGradient id="skyOcaso" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3b3f8f"/><stop offset="0.55" stop-color="#d9607a"/><stop offset="1" stop-color="#ffb35c"/></linearGradient>',
    '<linearGradient id="skyAlba" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4b6fb8"/><stop offset="0.6" stop-color="#f2a0a8"/><stop offset="1" stop-color="#ffe0b0"/></linearGradient>',
    '<linearGradient id="skyNoche" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#050a1c"/><stop offset="1" stop-color="#16244a"/></linearGradient>',
    '<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffffff" stop-opacity="0.95"/><stop offset="0.25" stop-color="#fff4d6" stop-opacity="0.5"/><stop offset="1" stop-color="#fff4d6" stop-opacity="0"/></radialGradient>',
    '<radialGradient id="luzPista" cx="0.5" cy="0.55" r="0.55"><stop offset="0" stop-color="#e8f3ff" stop-opacity="0.32"/><stop offset="1" stop-color="#e8f3ff" stop-opacity="0"/></radialGradient>',
    '<radialGradient id="solG" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fffbe8"/><stop offset="0.2" stop-color="#ffe9a8" stop-opacity="0.9"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient>',
    '<pattern id="red" width="7" height="7" patternUnits="userSpaceOnUse"><path d="M0,0 L7,7 M7,0 L0,7" stroke="#0b1220" stroke-width="1.1" opacity="0.9"/></pattern>',
    '<linearGradient id="muro" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16264a"/><stop offset="1" stop-color="#0c1730"/></linearGradient>',
    '<radialGradient id="bolaG" cx="0.35" cy="0.35" r="0.7"><stop offset="0" stop-color="#f9ff9a"/><stop offset="0.6" stop-color="#dbe83a"/><stop offset="1" stop-color="#9aa81c"/></radialGradient>',
]

# ------------------------------------------------------------------ CIELO (franja de arriba, por encima del estadio)
rs = random.Random(5)
estrellas = "".join(f'<circle cx="{rs.uniform(0, 1080):.0f}" cy="{rs.uniform(0, 330):.0f}" r="{rs.uniform(0.8, 2.2):.1f}" fill="#fff" opacity="{rs.uniform(0.4, 1):.2f}"/>' for _ in range(90))
svg_cielo = ('<rect x="-200" y="-200" width="1480" height="700" fill="url(#skyNoche)"/>'
             f'<g id="estrellas">{estrellas}<circle cx="840" cy="120" r="34" fill="#f4f1e2"/><circle cx="828" cy="112" r="34" fill="#0b1430" opacity="0.0"/></g>'
             '<rect id="cAlba" x="-200" y="-200" width="1480" height="700" fill="url(#skyAlba)"/>'
             '<rect id="cOcaso" x="-200" y="-200" width="1480" height="700" fill="url(#skyOcaso)"/>'
             '<rect id="cDia" x="-200" y="-200" width="1480" height="700" fill="url(#skyDia)"/>'
             '<g id="sol"><circle cx="0" cy="0" r="120" fill="url(#solG)"/><circle r="30" fill="#fff8dc"/></g>'
             '<g id="nubes" opacity="0.85">' + "".join(
                 f'<g transform="translate({x},{y}) scale({s})"><ellipse cx="0" cy="0" rx="90" ry="22" fill="#ffffff" opacity="0.8"/><ellipse cx="-30" cy="-12" rx="45" ry="22" fill="#ffffff" opacity="0.8"/><ellipse cx="30" cy="-14" rx="50" ry="26" fill="#ffffff" opacity="0.8"/></g>'
                 for x, y, s in ((160, 120, 1.0), (520, 70, 0.8), (930, 150, 1.1), (1250, 90, 0.9))) + '</g>')

# ------------------------------------------------------------------ GRADAS con público (personas de palo, por grupos que se van)
NFILAS = 13
PAL_ROPA = ["#e2604a", "#f2f4f7", "#2c4566", "#ffc24a", "#35a3d9", "#1d1d24", "#7a5bd6", "#3fa66b", "#f08aa0", "#c9d3de"]
PIELES = ["#f0c7a2", "#c68c63", "#8a5a3c", "#e6b28b"]
NGR = 14
gr_ropa = {(g, c): [] for g in range(NGR) for c in range(len(PAL_ROPA))}
gr_piel = {(g, c): [] for g in range(NGR) for c in range(len(PIELES))}
bandas = []
def fila(k):
    xs, zb, y = 9.7 + 0.9 * k, 19.2 + 0.9 * k, 1.3 + 0.45 * k
    return xs, zb, y
ZNEAR = -22.0
for k in range(NFILAS):
    xs, zb, y = fila(k)
    xs2, zb2, y2 = fila(k + 1)
    col = "#1f3563" if k % 2 == 0 else "#243d70"
    if k in (8, 9, 16, 17):
        col = "#2b2f3a"                       # pasillos
    front = [(-xs, y, ZNEAR), (-xs, y, zb), (xs, y, zb), (xs, y, ZNEAR)]
    back = [(-xs2, y2, ZNEAR), (-xs2, y2, zb2), (xs2, y2, zb2), (xs2, y2, ZNEAR)]
    bandas.append(poly(front + back[::-1], f'fill="{col}"'))
    bandas.append(f'<path d="M{pt(-xs, y, ZNEAR)} L{pt(-xs, y, zb)} L{pt(xs, y, zb)} L{pt(xs, y, ZNEAR)}" fill="none" stroke="#3a5794" stroke-width="1.2" opacity="0.7"/>')
    if k in (8, 9, 16, 17):
        continue
    # personas sentadas: a lo largo del fondo y de los laterales
    yy = y + 0.05
    sitios = [(x, zb + 0.35) for x in [-xs + 0.45 + i * 0.82 for i in range(int(2 * xs / 0.82))]]
    sitios += [(s * (xs + 0.35), z) for s in (-1, 1) for z in [zb - 0.6 - i * 0.82 for i in range(40)] if z > ZNEAR + 2]
    for (X, Z) in sitios:
        x0, y0, kk = PR(X, yy, Z)
        if not (-30 < x0 < 1110 and -30 < y0 < 1950):
            continue
        u = kk * 0.36                          # tamaño de una persona sentada
        g = rnd.randrange(NGR)
        tw, th_ = u * 0.55, u * 0.95
        gr_ropa[(g, rnd.randrange(len(PAL_ROPA)))].append(
            f"M{x0 - tw / 2:.1f},{y0:.1f} L{x0 - tw / 2:.1f},{y0 - th_ + tw * 0.3:.1f} Q{x0 - tw / 2:.1f},{y0 - th_:.1f} {x0:.1f},{y0 - th_:.1f} Q{x0 + tw / 2:.1f},{y0 - th_:.1f} {x0 + tw / 2:.1f},{y0 - th_ + tw * 0.3:.1f} L{x0 + tw / 2:.1f},{y0:.1f} Z")
        hr = u * 0.24
        hy = y0 - th_ - hr * 0.9
        gr_piel[(g, rnd.randrange(len(PIELES)))].append(f"M{x0 - hr:.1f},{hy:.1f} a{hr:.1f},{hr:.1f} 0 1 0 {2 * hr:.1f},0 a{hr:.1f},{hr:.1f} 0 1 0 {-2 * hr:.1f},0 Z")
svg_publico = ""
for g in range(NGR):
    inner = "".join(f'<path d="{" ".join(v)}" fill="{PAL_ROPA[c]}"/>' for (gg, c), v in gr_ropa.items() if gg == g and v)
    inner += "".join(f'<path d="{" ".join(v)}" fill="{PIELES[c]}"/>' for (gg, c), v in gr_piel.items() if gg == g and v)
    svg_publico += f'<g id="pub{g}">{inner}</g>'
# el público se va por grupos según avanza la noche (y vuelve en el rebobinado)
UMB = [0.12 + 0.88 * (g + 0.5) / NGR for g in range(NGR)]
UMB[0] = 0.0                                  # un grupo se queda siempre (los pocos cientos del amanecer)
for g in range(NGR):
    pista(f"#pub{g}", lambda t, g=g: 1.0 if publico(t) >= UMB[g] else 0.0)

# aro superior del estadio con los focos
xs, zb, y = fila(NFILAS)
aro_in = [(-xs, y, ZNEAR), (-xs, y, zb), (xs, y, zb), (xs, y, ZNEAR)]
aro_out = [(-xs - 3, y + 2.4, ZNEAR), (-xs - 3, y + 2.4, zb + 3), (xs + 3, y + 2.4, zb + 3), (xs + 3, y + 2.4, ZNEAR)]
svg_aro = poly(aro_in + aro_out[::-1], 'fill="#0c1424"') + f'<path d="M{" L".join(pt(*p) for p in aro_in)}" fill="none" stroke="#5b6b80" stroke-width="3"/>'
lamparas, halos = [], []
nb = 0
for i in range(-9, 10):
    X = i * (xs / 9.5)
    x0, y0, kk = PR(X, y + 1.2, zb + 1.5)
    lamparas.append(f'<rect x="{x0 - 9:.0f}" y="{y0 - 5:.0f}" width="18" height="10" rx="2" fill="#2a3446"/><rect class="lamp" id="lamp{nb}" x="{x0 - 7:.0f}" y="{y0 - 3:.0f}" width="14" height="6" rx="2" fill="#fffbe6" opacity="0"/>')
    halos.append(f'<circle id="halo{nb}" cx="{x0:.0f}" cy="{y0:.0f}" r="46" fill="url(#glow)" opacity="0"/>')
    nb += 1
for s in (-1, 1):
    for z in (14, 6, -2, -10):
        x0, y0, kk = PR(s * (xs + 1.5), y + 1.2, z)
        if -40 < x0 < 1120:
            lamparas.append(f'<rect x="{x0 - 9:.0f}" y="{y0 - 5:.0f}" width="18" height="10" rx="2" fill="#2a3446"/><rect class="lamp" id="lamp{nb}" x="{x0 - 7:.0f}" y="{y0 - 3:.0f}" width="14" height="6" rx="2" fill="#fffbe6" opacity="0"/>')
            halos.append(f'<circle id="halo{nb}" cx="{x0:.0f}" cy="{y0:.0f}" r="56" fill="url(#glow)" opacity="0"/>')
            nb += 1
for i in range(nb):
    d = (i % 7) * 0.03 + (i // 7) * 0.012      # se encienden por bancos, uno tras otro
    pista(f"#lamp{i}", lambda t, d=d: focos(t, d))
    pista(f"#halo{i}", lambda t, d=d: 0.9 * focos(t, d))

# ------------------------------------------------------------------ MUROS con publicidad (marcas inventadas)
ZW, XW, YW = 18.3, 9.0, 1.15
muros = poly([(-XW, 0, ZW), (XW, 0, ZW), (XW, YW, ZW), (-XW, YW, ZW)], 'fill="url(#muro)"')
muros += poly([(-XW, 0, ZNEAR), (-XW, 0, ZW), (-XW, YW, ZW), (-XW, YW, ZNEAR)], 'fill="#13234a"')
muros += poly([(XW, 0, ZNEAR), (XW, 0, ZW), (XW, YW, ZW), (XW, YW, ZNEAR)], 'fill="#13234a"')
def cartel_fondo(x0, x1, fondo, texto, col, peso=900, extra=""):
    a, b = PR(x0, 0.15, ZW), PR(x1, YW - 0.12, ZW)
    w, h = b[0] - a[0], a[1] - b[1]
    cx = (a[0] + b[0]) / 2
    return (f'<rect x="{a[0]:.1f}" y="{b[1]:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fondo}"/>'
            f'<text x="{cx:.1f}" y="{b[1] + h * 0.72:.1f}" text-anchor="middle" font-family="Inter" font-weight="{peso}" font-size="{h * 0.62:.1f}" fill="{col}" letter-spacing="1" {extra}>{texto}</text>')
muros += cartel_fondo(-8.7, -5.6, "#0e5a3c", "ORVEX", "#e9d58a")
muros += cartel_fondo(-5.4, -2.0, "#10203f", "NORDA AIR", "#ffffff")
muros += cartel_fondo(2.0, 5.4, "#10203f", "VOLTA", "#4fd1ff")
muros += cartel_fondo(5.6, 8.7, "#b8202a", "AQUAPURA", "#ffffff")
# marcador de velocidad del saque en el centro del fondo
a, b = PR(-1.8, 0.12, ZW), PR(1.8, YW - 0.1, ZW)
muros += (f'<rect x="{a[0]:.1f}" y="{b[1]:.1f}" width="{b[0] - a[0]:.1f}" height="{a[1] - b[1]:.1f}" rx="3" fill="#05080f" stroke="#2c3e5e" stroke-width="2"/>'
          f'<text x="540" y="{b[1] + 12:.1f}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="9" fill="#8fa3c0" letter-spacing="2">SERVE SPEED</text>'
          f'<g id="vel0"><text x="540" y="{a[1] - 6:.1f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="20" fill="#ffc24a">NEW YORK</text></g>'
          f'<g id="vel1" opacity="0"><text x="540" y="{a[1] - 6:.1f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="21" fill="#35d987">210 KM/H</text></g>'
          f'<g id="vel2" opacity="0"><text x="540" y="{a[1] - 6:.1f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="21" fill="#ff8a80">180 KM/H</text></g>')
def cartel_lado(s, z0, z1, fondo, texto, col):
    """Cartel en un muro lateral (en perspectiva): transform afín a partir de 3 puntos proyectados."""
    X = s * XW
    o, u, v = PR(X, 0.15, z0), PR(X, 0.15, z1), PR(X, YW - 0.12, z0)
    L = 100.0
    a_, b_ = (u[0] - o[0]) / L, (u[1] - o[1]) / L
    c_, d_ = (v[0] - o[0]) / -20.0, (v[1] - o[1]) / -20.0
    return (f'<g transform="matrix({a_:.4f},{b_:.4f},{c_:.4f},{d_:.4f},{o[0]:.1f},{o[1]:.1f})">'
            f'<rect x="0" y="-20" width="100" height="20" fill="{fondo}"/><text x="50" y="-5" text-anchor="middle" font-family="Inter" font-weight="900" font-size="12" fill="{col}">{texto}</text></g>')
for s in (-1, 1):
    muros += cartel_lado(s, 17.5, 10.5, "#0e5a3c", "ORVEX", "#e9d58a")
    muros += cartel_lado(s, 9.5, 2.5, "#10203f", "MERIDIAN BANK", "#ffffff")
    muros += cartel_lado(s, -2.5, -9.5, "#e9e2cf", "KITE", "#10203f")
    muros += cartel_lado(s, -10.5, -17.5, "#b8202a", "AQUAPURA", "#ffffff")
# ------------------------------------------------------------------ PISTA (verde fuera, azul dentro, líneas blancas)
pista_svg = suelo_rect(-XW, XW, ZNEAR, ZW, 'fill="#3d7a5c"')
pista_svg += suelo_rect(-6.9, 6.9, -16.0, 16.0, 'fill="#3f8a66" opacity="0.35"')
pista_svg += suelo_rect(-5.485, 5.485, -11.885, 11.885, 'fill="#3768b0"')
LW = 0.06
lineas = [(-5.485 - LW, 5.485 + LW, -11.885 - 0.1, -11.885), (-5.485 - LW, 5.485 + LW, 11.885, 11.885 + 0.1),
          (-5.485 - LW, -5.485, -11.885, 11.885), (5.485, 5.485 + LW, -11.885, 11.885),
          (-4.115 - LW, -4.115, -11.885, 11.885), (4.115, 4.115 + LW, -11.885, 11.885),
          (-4.115, 4.115, -6.40 - LW, -6.40), (-4.115, 4.115, 6.40, 6.40 + LW),
          (-LW / 2, LW / 2, -6.40, 6.40), (-LW / 2, LW / 2, -11.885, -11.585), (-LW / 2, LW / 2, 11.585, 11.885)]
pista_svg += "".join(suelo_rect(a, b, c, d, 'fill="#f4f8fc"') for a, b, c, d in lineas)
pista_svg += '<g id="luzP" opacity="0">' + suelo_rect(-8, 8, -15, 15, 'fill="url(#luzPista)"') + '</g>'
pista_svg += suelo_rect(-6.4, 6.4, 0.0, 0.55, 'fill="#000" opacity="0.18"')        # sombra de la red

# ------------------------------------------------------------------ RED
XP = 6.4
red_svg = poly([(-XP, 0, 0), (XP, 0, 0), (XP, 1.0, 0), (0, 0.88, 0), (-XP, 1.0, 0)], 'fill="url(#red)" opacity="0.85"')
red_svg += f'<path d="M{pt(-XP, 1.07, 0)} L{pt(0, 0.914, 0)} L{pt(XP, 1.07, 0)}" stroke="#f4f8fc" stroke-width="5" fill="none"/>'
red_svg += f'<path d="M{pt(0, 0, 0)} L{pt(0, 0.914, 0)}" stroke="#f4f8fc" stroke-width="4"/>'
for s in (-1, 1):
    red_svg += f'<path d="M{pt(s * XP, 0, 0)} L{pt(s * XP, 1.07, 0)}" stroke="#1d2b44" stroke-width="7" stroke-linecap="round"/>'
    red_svg += f'<path d="M{pt(s * 5.0, 0, 0)} L{pt(s * 5.0, 1.07, 0)}" stroke="#f4f8fc" stroke-width="2.5"/>'
a, b = PR(-2.2, 0.75, 0), PR(2.2, 0.75, 0)
red_svg += f'<text x="540" y="{a[1] + 5:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="15" fill="#ffffff" opacity="0.85" letter-spacing="3">ORVEX</text>'

# ------------------------------------------------------------------ PERSONAS DE PALO (tronco grueso, articulaciones)
POSES = {
    "listo": dict(head=(0, -91), neck=(0, -80), hip=(0, -47), eR=(13, -62), hR=(8, -52), eL=(-12, -62), hL=(-2, -54), tip=(18, -78),
                  kR=(10, -25), fR=(13, 0), kL=(-10, -25), fL=(-13, 0)),
    "drAtras": dict(head=(3, -90), neck=(2, -80), hip=(0, -47), eR=(21, -66), hR=(29, -58), eL=(-13, -68), hL=(-8, -64), tip=(52, -66),
                    kR=(12, -25), fR=(16, 0), kL=(-11, -24), fL=(-16, 0)),
    "drFinal": dict(head=(-2, -91), neck=(-1, -80), hip=(0, -47), eR=(-7, -74), hR=(-15, -80), eL=(-15, -58), hL=(-10, -48), tip=(-6, -106),
                    kR=(9, -25), fR=(14, 0), kL=(-11, -26), fL=(-14, 0)),
    "revAtras": dict(head=(-3, -90), neck=(-2, -80), hip=(0, -47), eR=(-12, -66), hR=(-22, -60), eL=(-16, -62), hL=(-20, -58), tip=(-46, -68),
                     kR=(11, -24), fR=(16, 0), kL=(-12, -25), fL=(-16, 0)),
    "revFinal": dict(head=(2, -91), neck=(1, -80), hip=(0, -47), eR=(13, -76), hR=(18, -84), eL=(10, -74), hL=(15, -82), tip=(8, -110),
                     kR=(11, -25), fR=(14, 0), kL=(-10, -26), fL=(-14, 0)),
    "saqueA": dict(head=(0, -92), neck=(0, -81), hip=(0, -48), eR=(17, -72), hR=(23, -62), eL=(-9, -94), hL=(-11, -112), tip=(30, -40),
                   kR=(9, -24), fR=(12, 0), kL=(-8, -25), fL=(-12, 0)),
    "saqueB": dict(head=(2, -97), neck=(2, -86), hip=(0, -50), eR=(8, -108), hR=(10, -126), eL=(-10, -74), hL=(-6, -60), tip=(14, -154),
                   kR=(5, -25), fR=(6, -2), kL=(-6, -25), fL=(-8, 0)),
    "correr1": dict(head=(0, -91), neck=(0, -80), hip=(0, -47), eR=(14, -64), hR=(10, -54), eL=(-13, -64), hL=(-4, -56), tip=(20, -80),
                    kR=(14, -27), fR=(20, -5), kL=(-6, -21), fL=(-14, 0)),
    "correr2": dict(head=(0, -91), neck=(0, -80), hip=(0, -47), eR=(14, -64), hR=(10, -54), eL=(-13, -64), hL=(-4, -56), tip=(20, -80),
                    kR=(6, -21), fR=(14, 0), kL=(-14, -27), fL=(-20, -5)),
    "toalla": dict(head=(0, -89), neck=(0, -79), hip=(0, -47), eR=(12, -80), hR=(4, -90), eL=(-12, -80), hL=(-4, -90), tip=(26, -60),
                   kR=(8, -25), fR=(10, 0), kL=(-8, -25), fL=(-10, 0)),
    "beber": dict(head=(1, -89), neck=(0, -79), hip=(0, -47), eR=(12, -60), hR=(14, -44), eL=(-12, -76), hL=(-3, -92), tip=(20, -22),
                  kR=(8, -25), fR=(10, 0), kL=(-8, -25), fL=(-10, 0)),
    "comer": dict(head=(1, -89), neck=(0, -79), hip=(0, -47), eR=(12, -60), hR=(14, -44), eL=(-11, -74), hL=(-3, -86), tip=(20, -22),
                  kR=(8, -25), fR=(10, 0), kL=(-8, -25), fL=(-10, 0)),
    "calambre": dict(head=(-10, -66), neck=(-8, -56), hip=(0, -30), eR=(4, -36), hR=(12, -14), eL=(-16, -40), hL=(-18, -20), tip=(-34, -4),
                     kR=(14, -16), fR=(8, 0), kL=(-14, -14), fL=(-26, 0)),
    "cansado": dict(head=(2, -86), neck=(1, -77), hip=(0, -46), eR=(12, -58), hR=(14, -42), eL=(-11, -60), hL=(-12, -44), tip=(22, -18),
                    kR=(8, -24), fR=(11, 0), kL=(-8, -24), fL=(-11, 0)),
    "andar1": dict(head=(0, -92), neck=(0, -81), hip=(0, -48), eR=(10, -62), hR=(14, -46), eL=(-10, -62), hL=(-14, -48), tip=(24, -28),
                   kR=(9, -25), fR=(15, -2), kL=(-7, -24), fL=(-11, 0)),
    "andar2": dict(head=(0, -92), neck=(0, -81), hip=(0, -48), eR=(10, -62), hR=(12, -48), eL=(-10, -62), hL=(-10, -48), tip=(22, -30),
                   kR=(7, -24), fR=(11, 0), kL=(-9, -25), fL=(-15, -2)),
    "bote": dict(head=(1, -90), neck=(0, -80), hip=(0, -47), eR=(14, -64), hR=(22, -56), eL=(-10, -64), hL=(-8, -48), tip=(36, -40),
                 kR=(9, -25), fR=(12, 0), kL=(-9, -25), fL=(-12, 0)),
}
def joints(p):
    j = dict(p)
    nx, ny = p["neck"]; hx, hy = p["hip"]
    j["sR"], j["sL"] = (nx + 8, ny + 3), (nx - 8, ny + 3)
    j["pR"], j["pL"] = (hx + 5, hy), (hx - 5, hy)
    hr, tp = p["hR"], p["tip"]
    j["thr"] = (hr[0] + 0.38 * (tp[0] - hr[0]), hr[1] + 0.38 * (tp[1] - hr[1]))
    j["mR"] = ((j["pR"][0] + p["kR"][0]) / 2, (j["pR"][1] + p["kR"][1]) / 2)
    j["mL"] = ((j["pL"][0] + p["kL"][0]) / 2, (j["pL"][1] + p["kL"][1]) / 2)
    j["zR"] = (p["fR"][0] + 5, p["fR"][1]); j["zL"] = (p["fL"][0] - 5, p["fL"][1])
    j["cR"] = (j["sR"][0] + 0.45 * (p["eR"][0] - j["sR"][0]), j["sR"][1] + 0.45 * (p["eR"][1] - j["sR"][1]))
    j["cL"] = (j["sL"][0] + 0.45 * (p["eL"][0] - j["sL"][0]), j["sL"][1] + 0.45 * (p["eL"][1] - j["sL"][1]))
    return j
# (nombre, desde, hasta, grosor, color)  — el orden es el de dibujo
def segs(c):
    return [("muL", "pL", "kL", 8, c["piel"]), ("piL", "kL", "fL", 7, c["piel"]), ("zaL", "fL", "zL", 6, c["zap"]),
            ("muR", "pR", "kR", 8, c["piel"]), ("piR", "kR", "fR", 7, c["piel"]), ("zaR", "fR", "zR", 6, c["zap"]),
            ("shL", "pL", "mL", 11, c["short"]), ("shR", "pR", "mR", 11, c["short"]), ("cad", "pL", "pR", 11, c["short"]),
            ("tor", "neck", "hip", 19, c["cam"]),
            ("brL", "sL", "eL", 7, c["piel"]), ("anL", "eL", "hL", 6, c["piel"]), ("mgL", "sL", "cL", 9, c["cam"]),
            ("brR", "sR", "eR", 7, c["piel"]), ("anR", "eR", "hR", 6, c["piel"]), ("mgR", "sR", "cR", 9, c["cam"]),
            ("mng", "hR", "thr", 3, "#1b1f27"), ("rq", "thr", "tip", 10, c["raq"]), ("cu", "thr", "tip", 5, "#dfe9f2")]
ESTADO = {}
def figura(pid, c, pose="listo", sudor=True, extra=""):
    j = joints(POSES[pose])
    out = [f'<g id="{pid}"><g id="{pid}_m">',
           f'<ellipse cx="0" cy="1" rx="17" ry="5" fill="#000" opacity="0.32"/>']
    for nm, a, b, w, col in segs(c):
        if c["raq"] == "none" and nm in ("mng", "rq", "cu"):
            continue
        op = ' opacity="0.8"' if nm == "cu" else ""
        out.append(f'<line id="{pid}_{nm}" x1="{j[a][0]}" y1="{j[a][1]}" x2="{j[b][0]}" y2="{j[b][1]}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"{op}/>')
        if nm == "tor" and sudor:
            out.append(f'<line id="{pid}_sud" x1="{j[a][0]}" y1="{j[a][1] + 6}" x2="{j[b][0]}" y2="{j[b][1] - 4}" stroke="#000" stroke-width="11" stroke-linecap="round" opacity="0"/>')
    hx, hy = j["head"]
    out.append(f'<g id="{pid}_hd" transform="translate(0,0)"><g id="{pid}_h" ><circle cx="{hx}" cy="{hy}" r="9" fill="{c["piel"]}"/>'
               f'<path d="M{hx - 9.2},{hy - 1} A9.2,9.2 0 0 1 {hx + 9.2},{hy - 1} Q{hx},{hy - 5} {hx - 9.2},{hy - 1} Z" fill="{c["pelo"]}"/>'
               f'<path d="M{hx - 9},{hy - 3.5} Q{hx},{hy - 6.5} {hx + 9},{hy - 3.5}" stroke="{c.get("cinta", "#ffffff")}" stroke-width="2.6" fill="none"/></g></g>')
    out.append(extra + '</g></g>')
    ESTADO[pid] = dict(pose=pose, c=c)
    return "".join(out)
HEAD0 = {}
def pose(pid, nombre, t, d=0.18, ease="power2.out", slouch=None, solo=None):
    """Lleva la persona a una postura (mueve los extremos de cada palo)."""
    p = {k: list(v) for k, v in POSES[nombre].items()}
    f = cansancio(t) if slouch is None else slouch
    if nombre not in ("calambre",):
        p["head"][0] += 3 * f; p["head"][1] += 6 * f; p["neck"][1] += 4 * f; p["neck"][0] += 1.5 * f
    j = joints({k: tuple(v) for k, v in p.items()})
    for nm, a, b, w, col in segs(ESTADO[pid]["c"]):
        if ESTADO[pid]["c"]["raq"] == "none" and nm in ("mng", "rq", "cu"):
            continue
        if solo and nm not in solo:
            continue
        J(f'tl.to("#{pid}_{nm}", {{attr:{{x1:{j[a][0]:.1f}, y1:{j[a][1]:.1f}, x2:{j[b][0]:.1f}, y2:{j[b][1]:.1f}}}, duration:{d}, ease:"{ease}"}}, {t:.3f});')
        if nm == "tor" and (not solo):
            J(f'tl.to("#{pid}_sud", {{attr:{{x1:{j[a][0]:.1f}, y1:{j[a][1] + 6:.1f}, x2:{j[b][0]:.1f}, y2:{j[b][1] - 4:.1f}}}, duration:{d}, ease:"{ease}"}}, {t:.3f});')
    if not solo:
        h0 = POSES["listo"]["head"]
        J(f'tl.to("#{pid}_h", {{x:{j["head"][0] - h0[0]:.1f}, y:{j["head"][1] - h0[1]:.1f}, duration:{d}, ease:"{ease}"}}, {t:.3f});')
    ESTADO[pid]["pose"] = nombre
PIERNAS = {"muL", "piL", "zaL", "muR", "piR", "zaR", "shL", "shR", "cad"}

# ------------------------------------------------------------------ JUGADORES, colocación y movimiento
JUG = {"A": dict(piel="#e6b28b", pelo="#3a2a20", cam="#e2604a", short="#1d2433", zap="#f2f4f7", raq="#1b1f27", cinta="#ffffff"),
       "B": dict(piel="#c68c63", pelo="#1d1d24", cam="#f2f4f7", short="#2c4566", zap="#ffc24a", raq="#c0392b", cinta="#35a3d9")}
POS = {}
def coloca(pid, X, Z, t=None, d=0.0, ease="power2.inOut", espejo=None):
    x, y, k = PR(X, 0, Z)
    s = k * SC
    if t is None:
        J(f'tl.set("#{pid}", {{svgOrigin:"0 0", x:{x:.1f}, y:{y:.1f}, scale:{s:.3f}}}, 0);')
    else:
        J(f'tl.to("#{pid}", {{x:{x:.1f}, y:{y:.1f}, scale:{s:.3f}, duration:{d:.3f}, ease:"{ease}"}}, {t:.3f});')
    if espejo is not None:
        if t is None:
            J(f'tl.set("#{pid}_m", {{svgOrigin:"0 0", scaleX:{espejo}}}, 0);')
        else:
            J(f'tl.to("#{pid}_m", {{scaleX:{espejo}, duration:0.25, ease:"power1.inOut"}}, {t + d / 2 - 0.12:.3f});')
    POS[pid] = (X, Z)
def camino(pid, pts, t, d, piernas="andar", espejo=None):
    """Camina por una lista de puntos (X,Z) de la pista: posición, escala y piernas alternando."""
    L = [0.0]
    for (a, b), (c, e) in zip(pts, pts[1:]):
        L.append(L[-1] + math.hypot(c - a, e - b))
    kf, n = [], max(2, int(d / 0.12))
    for i in range(1, n + 1):
        u = i / n * L[-1]
        for q in range(len(pts) - 1):
            if L[q] <= u <= L[q + 1] + 1e-9:
                w = (u - L[q]) / max(1e-6, L[q + 1] - L[q])
                X = pts[q][0] + w * (pts[q + 1][0] - pts[q][0]); Z = pts[q][1] + w * (pts[q + 1][1] - pts[q][1])
                break
        x, y, k = PR(X, 0, Z)
        kf.append(f'{{x:{x:.1f}, y:{y:.1f}, scale:{k * SC:.3f}, duration:{d / n:.3f}, ease:"none"}}')
    J(f'tl.to("#{pid}", {{keyframes:[{",".join(kf)}]}}, {t:.3f});')
    paso = 0.2 if piernas == "andar" else 0.14
    k = 0
    tt = t
    while tt < t + d - 0.1:
        pose(pid, f"{piernas}{1 + k % 2}" if piernas == "andar" else f"correr{1 + k % 2}", tt, paso * 0.9, "sine.inOut", solo=None if piernas == "andar" else PIERNAS)
        tt += paso; k += 1
    if espejo is not None:
        J(f'tl.to("#{pid}_m", {{scaleX:{espejo}, duration:0.3, ease:"power1.inOut"}}, {t + d * 0.5:.3f});')
    POS[pid] = pts[-1]

# ------------------------------------------------------------------ JUEZ DE SILLA, BANQUILLOS, JUECES DE LÍNEA, RECOGEPELOTAS
def silla_juez():
    X, Z, YS = 7.1, 0.0, 2.0
    s = ""
    for dx in (-0.35, 0.35):
        for dz in (-0.35, 0.35):
            s += f'<path d="M{pt(X + dx, 0, Z + dz)} L{pt(X + dx * 0.8, YS, Z + dz * 0.8)}" stroke="#c9d3de" stroke-width="4"/>'
    s += f'<path d="M{pt(X - 0.2, 0.7, Z - 0.5)} L{pt(X - 0.2, YS, Z - 0.5)}" stroke="#8fa3c0" stroke-width="3"/>'
    for yy in (0.6, 1.2):
        s += f'<path d="M{pt(X - 0.5, yy, Z - 0.48)} L{pt(X - 0.1, yy, Z - 0.48)}" stroke="#8fa3c0" stroke-width="3"/>'
    s += poly([(X - 0.45, YS, Z - 0.45), (X + 0.45, YS, Z - 0.45), (X + 0.45, YS, Z + 0.45), (X - 0.45, YS, Z + 0.45)], 'fill="#1d2b44"')
    s += poly([(X - 0.55, YS + 0.05, -0.5), (X - 0.55, YS + 0.05, 0.5), (X - 0.55, YS + 0.7, 0.5), (X - 0.55, YS + 0.7, -0.5)], 'fill="#0e5a3c"')
    x0, y0, k = PR(X - 0.55, YS + 0.38, 0)
    s += f'<text x="{x0 - 2:.0f}" y="{y0 + 4:.0f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="9" fill="#e9d58a">ORVEX</text>'
    s += poly([(X + 0.3, YS, -0.45), (X + 0.3, YS, 0.45), (X + 0.3, YS + 1.0, 0.45), (X + 0.3, YS + 1.0, -0.45)], 'fill="#16264a"')
    return s
def banquillo(Z):
    X = 8.5
    s = poly([(X - 0.35, 0, Z - 0.9), (X + 0.35, 0, Z - 0.9), (X + 0.35, 0, Z + 0.9), (X - 0.35, 0, Z + 0.9)], 'fill="#000" opacity="0.25"')
    s += poly([(X - 0.35, 0.45, Z - 0.9), (X + 0.35, 0.45, Z - 0.9), (X + 0.35, 0.45, Z + 0.9), (X - 0.35, 0.45, Z + 0.9)], 'fill="#0e5a3c"')
    s += poly([(X - 0.35, 0, Z - 0.9), (X - 0.35, 0.45, Z - 0.9), (X - 0.35, 0.45, Z + 0.9), (X - 0.35, 0, Z + 0.9)], 'fill="#0a4430"')
    s += poly([(X + 0.35, 0.45, Z - 0.9), (X + 0.35, 1.0, Z - 0.9), (X + 0.35, 1.0, Z + 0.9), (X + 0.35, 0.45, Z + 0.9)], 'fill="#12704b"')
    s += poly([(X - 0.2, 0.46, Z - 0.6), (X + 0.2, 0.46, Z - 0.6), (X + 0.2, 0.46, Z - 0.05), (X - 0.2, 0.46, Z - 0.05)], 'fill="#f4f8fc"')   # toalla
    s += poly([(X - 0.25, 0, Z + 1.0), (X + 0.25, 0, Z + 1.0), (X + 0.25, 0.5, Z + 1.0), (X - 0.25, 0.5, Z + 1.0)], 'fill="#1b1f27"')        # bolsa
    for i in range(3):
        x0, y0, k = PR(X - 0.15, 0.46, Z + 0.15 + i * 0.22)
        s += f'<rect x="{x0 - 2.5:.1f}" y="{y0 - 11:.1f}" width="5" height="11" rx="1.5" fill="{["#4fd1ff", "#ff5a4f", "#f2f4f7"][i]}"/>'
    return s
STAFF = {"juez": dict(piel="#e6b28b", pelo="#5a5a5a", cam="#1d2b44", short="#1d2b44", zap="#1b1f27", raq="none", cinta="#1d2b44"),
         "linea": dict(piel="#c68c63", pelo="#1d1d24", cam="#24356b", short="#d9d4c6", zap="#f2f4f7", raq="none", cinta="#24356b"),
         "linea2": dict(piel="#f0c7a2", pelo="#7a4a2a", cam="#24356b", short="#d9d4c6", zap="#f2f4f7", raq="none", cinta="#24356b"),
         "bk": dict(piel="#e6b28b", pelo="#3a2a20", cam="#3b4fd0", short="#3b4fd0", zap="#f2f4f7", raq="none", cinta="#3b4fd0"),
         "bk2": dict(piel="#8a5a3c", pelo="#1d1d24", cam="#3b4fd0", short="#3b4fd0", zap="#f2f4f7", raq="none", cinta="#3b4fd0")}
POSES["sentado"] = dict(head=(0, -64), neck=(0, -54), hip=(0, -24), eR=(10, -40), hR=(14, -28), eL=(-10, -40), hL=(-14, -28), tip=(14, -28),
                        kR=(6, -22), fR=(7, 0), kL=(-6, -22), fL=(-7, 0))
POSES["agachado"] = dict(head=(0, -60), neck=(0, -50), hip=(0, -22), eR=(10, -38), hR=(9, -26), eL=(-10, -38), hL=(-9, -26), tip=(9, -26),
                         kR=(11, -14), fR=(6, 0), kL=(-11, -14), fL=(-6, 0))
POSES["firme"] = dict(head=(0, -92), neck=(0, -81), hip=(0, -48), eR=(9, -64), hR=(6, -50), eL=(-9, -64), hL=(-6, -50), tip=(6, -50),
                      kR=(5, -24), fR=(6, 0), kL=(-5, -24), fL=(-6, 0))
POSES["dar"] = dict(head=(0, -92), neck=(0, -81), hip=(0, -48), eR=(14, -68), hR=(26, -66), eL=(-9, -64), hL=(-6, -50), tip=(26, -66),
                    kR=(5, -24), fR=(6, 0), kL=(-5, -24), fL=(-6, 0))
for nm in ("sentado", "agachado", "firme", "dar"):
    pass
personas_staff = []
def staff(pid, tipo, X, Z, pose_="firme", espejo=1, Y=0.0):
    personas_staff.append(figura(pid, STAFF[tipo], pose_, sudor=False))
    x, y, k = PR(X, Y, Z)
    J(f'tl.set("#{pid}", {{svgOrigin:"0 0", x:{x:.1f}, y:{y:.1f}, scale:{k * SC * 0.92:.3f}}}, 0); tl.set("#{pid}_m", {{svgOrigin:"0 0", scaleX:{espejo}}}, 0);')
    POS[pid] = (X, Z)
# juez de silla (sentado arriba)
staff("juez", "juez", 7.05, 0.0, "sentado", -1, Y=2.0)
# jueces de línea sentados (laterales) y de pie (detrás del fondo)
staff("lj1", "linea", 8.0, 6.4, "sentado", -1)
staff("lj2", "linea2", -8.0, 11.9, "sentado", 1)
staff("lj3", "linea", -8.0, -6.4, "sentado", 1)
staff("lj4", "linea2", 8.0, -11.9, "sentado", -1)
staff("lj5", "linea", 2.2, 16.2, "firme", 1)
staff("lj6", "linea2", -2.4, -16.0, "firme", 1)
# recogepelotas: dos agachados en la red y cuatro en las esquinas
staff("bk1", "bk", 5.9, 0.7, "agachado", -1)
staff("bk2", "bk2", -5.9, -0.7, "agachado", 1)
staff("bk3", "bk2", 4.8, 16.0, "firme", 1)
staff("bk4", "bk", -4.8, 16.0, "firme", 1)
staff("bk5", "bk", 4.6, -15.8, "firme", 1)
staff("bk6", "bk2", -4.6, -15.8, "firme", 1)
# relevos (entran después): esperan fuera de plano
staff("bk7", "bk2", 9.6, -15.0, "firme", -1)
staff("lj7", "linea2", 9.8, -11.9, "firme", -1)
J('tl.set("#bk7, #lj7", {opacity:0}, 0);')

# ------------------------------------------------------------------ BOLA
bola_svg = ('<g id="bsom"><ellipse rx="1.3" ry="0.5" fill="#000" opacity="0.35"/></g>'
            '<g id="bg2" opacity="0"><circle r="1" fill="#e6f05a" opacity="0.25"/></g><g id="bg1" opacity="0"><circle r="1" fill="#e6f05a" opacity="0.45"/></g>'
            '<g id="bola"><circle r="1" fill="url(#bolaG)"/><path d="M-0.7,-0.5 Q0,0 -0.7,0.5 M0.7,-0.5 Q0,0 0.7,0.5" stroke="#ffffff" stroke-width="0.12" fill="none" opacity="0.8"/></g>')
J('tl.set("#bola, #bg1, #bg2, #bsom", {svgOrigin:"0 0", opacity:0}, 0);')
def RB(Z): return PR(0, 0, Z)[2] * 0.067 * 1.15
def bola_vuelo(t, tramos, sombra=True, fantasmas=True):
    """tramos: lista de (puntos3D muestreados, duración). Mueve la bola (y su sombra) por la trayectoria."""
    kb, ks = [], []
    for pts, d in tramos:
        n = len(pts) - 1
        for (X, Y, Z) in pts[1:]:
            x, y, k = PR(X, Y, Z); gx, gy, _ = PR(X, 0, Z)
            kb.append(f'{{x:{x:.1f}, y:{y:.1f}, scale:{RB(Z):.2f}, duration:{d / n:.3f}, ease:"none"}}')
            ks.append(f'{{x:{gx:.1f}, y:{gy:.1f}, scale:{RB(Z):.2f}, duration:{d / n:.3f}, ease:"none"}}')
    X, Y, Z = tramos[0][0][0]
    x, y, k = PR(X, Y, Z); gx, gy, _ = PR(X, 0, Z)
    J(f'tl.set("#bola", {{x:{x:.1f}, y:{y:.1f}, scale:{RB(Z):.2f}, opacity:1}}, {t:.3f}); tl.to("#bola", {{keyframes:[{",".join(kb)}]}}, {t:.3f});')
    if sombra:
        J(f'tl.set("#bsom", {{x:{gx:.1f}, y:{gy:.1f}, scale:{RB(Z):.2f}, opacity:1}}, {t:.3f}); tl.to("#bsom", {{keyframes:[{",".join(ks)}]}}, {t:.3f});')
    if fantasmas:
        for i, g in ((1, "#bg1"), (2, "#bg2")):
            J(f'tl.set("{g}", {{x:{x:.1f}, y:{y:.1f}, scale:{RB(Z):.2f}, opacity:1}}, {t + 0.035 * i:.3f}); tl.to("{g}", {{keyframes:[{",".join(kb)}]}}, {t + 0.035 * i:.3f});')
def arco(a, b, alto, n=7):
    out = []
    for i in range(n + 1):
        u = i / n
        out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u + alto * 4 * u * (1 - u), a[2] + (b[2] - a[2]) * u))
    return out
def oculta_bola(t):
    J(f'tl.set("#bola, #bg1, #bg2, #bsom", {{opacity:0}}, {t:.3f});')
def contacto(pid, derecha):
    X, Z = POS[pid]
    lado = 1 if Z < 0 else -1                 # el de abajo se ve de espaldas (raqueta a la derecha de la pantalla)
    off = 0.62 if derecha else -0.62
    return (X + off * lado, 1.25, Z + (0.4 if Z < 0 else -0.4))

# ------------------------------------------------------------------ PELOTEOS
LADO = {"A": -1, "B": 1}                      # -1 = abajo (cerca de cámara), 1 = arriba (fondo)
def golpe(pid, t, derecha, fuerte=False):
    a, b = ("drAtras", "drFinal") if derecha else ("revAtras", "revFinal")
    pose(pid, a, t - 0.26, 0.2, "power2.out")
    pose(pid, b, t - 0.02, 0.16, "power3.out")
    pose(pid, "listo", t + 0.32, 0.35, "power1.inOut")
    fx("bola", t)
def peloteo(t0, t1, saca=None, botes=1.15, lento=1.0, final="ganador", rng=None):
    """Intercambio de golpes de t0 a t1. Devuelve el instante en que muere el punto."""
    r = rng or rnd
    quien = saca
    t = t0
    otro = lambda p: "B" if p == "A" else "A"
    if saca:
        # saque: botar, lanzar y golpear
        X, Z = POS[saca]
        lz = LADO_ACT[saca]
        pose(saca, "saqueA", t, 0.45, "power1.inOut")
        x0, y0, z0 = X - 0.35 * (-lz), 1.0, Z
        alto = (X - 0.25 * (-lz), 3.1, Z + 0.25 * -lz)
        bola_vuelo(t + 0.05, [(arco((x0, y0, z0), alto, 0.0, 4), 0.42)], sombra=False, fantasmas=False)
        pose(saca, "saqueB", t + 0.42, 0.12, "power3.out")
        th = t + 0.5
        fx("bola", th)
        rec = otro(saca)
        Xr, Zr = POS[rec]
        xb = -X * 0.9 + r.uniform(-0.6, 0.6)
        zb = -lz * r.uniform(4.0, 6.0) * -1
        zb = 5.0 * (1 if LADO_ACT[rec] > 0 else -1) * r.uniform(0.8, 1.15)
        dvu = 0.62 * lento
        Xr2 = max(-4.8, min(4.8, xb + r.uniform(-0.6, 0.6)))
        der = r.random() < 0.6
        coloca(rec, Xr2 - (0.62 if der else -0.62) * (1 if LADO_ACT[rec] < 0 else -1), Zr, th + 0.05, dvu * 0.85)
        POS[rec] = (Xr2 - (0.62 if der else -0.62) * (1 if LADO_ACT[rec] < 0 else -1), Zr)
        c2 = contacto(rec, der)
        bnc = (xb, 0.0, zb)
        bola_vuelo(th, [(arco(alto, bnc, 0.0, 4), dvu * 0.62), (arco(bnc, c2, botes * 0.55, 5), dvu * 0.38)])
        fx("bote", th + dvu * 0.62)
        pose(saca, "listo", th + 0.3, 0.4)
        t = th + dvu
        quien = rec
        siguiente_der = der
    else:
        siguiente_der = True
        if quien is None:
            quien = "A"
    while True:
        h = H(t)
        dur = (1.02 + 0.28 * min(1, h / 20)) * lento
        if t + dur > t1:
            break
        rec = otro(quien)
        der_h = siguiente_der
        golpe(quien, t, der_h)
        c1 = contacto(quien, der_h)
        lr = LADO_ACT[rec]
        xb = r.uniform(-3.4, 3.4)
        zb = lr * r.uniform(7.0, 10.8)
        Xr, Zr = POS[rec]
        der = r.random() < 0.6
        lado_vista = 1 if lr < 0 else -1
        xr = max(-4.9, min(4.9, xb + r.uniform(-0.4, 0.4) - (0.62 if der else -0.62) * lado_vista))
        dist = abs(xr - Xr)
        zr = lr * r.uniform(12.2, 13.2)
        if dist > 0.7:
            camino(rec, [(Xr, Zr), (xr, zr)], t + 0.12, dur * 0.72, piernas="correr")
        else:
            coloca(rec, xr, zr, t + 0.12, dur * 0.72)
        POS[rec] = (xr, zr)
        c2 = contacto(rec, der)
        bnc = (xb, 0.0, zb)
        alto1 = 1.5 if botes > 1 else 1.1
        bola_vuelo(t, [(arco(c1, bnc, alto1, 6), dur * 0.62), (arco(bnc, c2, botes * 0.6, 5), dur * 0.38)])
        fx("bote", t + dur * 0.62)
        # el que golpea vuelve hacia el centro
        Xq, Zq = POS[quien]
        coloca(quien, Xq * 0.4, Zq, t + 0.35, dur * 0.55)
        t += dur
        quien = rec
        siguiente_der = der
    # el último golpe es un ganador: la bola pasa al otro y sigue hasta el fondo
    rec = otro(quien)
    golpe(quien, t, siguiente_der)
    c1 = contacto(quien, siguiente_der)
    lr = LADO_ACT[rec]
    Xr, Zr = POS[rec]
    xb = Xr + (2.6 if Xr < 0 else -2.6)
    bnc = (xb, 0.0, lr * 9.5)
    fin = (xb + (xb - c1[0]) * 0.35, 0.9, lr * 17.8)
    dur = 1.05 * lento
    camino(rec, [(Xr, Zr), (Xr + (xb - Xr) * 0.45, Zr)], t + 0.2, 0.6, piernas="correr")
    bola_vuelo(t, [(arco(c1, bnc, 1.3, 6), dur * 0.55), (arco(bnc, fin, 0.8, 5), dur * 0.45)])
    fx("bote", t + dur * 0.55)
    J(f'tl.to("#bola, #bg1, #bg2, #bsom", {{opacity:0, duration:0.25}}, {t + dur + 0.05:.3f});')
    pose(rec, "listo", t + 0.9, 0.35)
    pose(quien, "listo", t + 0.4, 0.35)
    return t + dur

# ------------------------------------------------------------------ COLOCACIÓN INICIAL (fotograma 0 = estado a las 20 h)
LADO_ACT = {"A": 1, "B": -1}                  # a las 20 h: B abajo (de espaldas), A arriba
jug_svg = figura("A", JUG["A"]) + figura("B", JUG["B"])
coloca("A", 0.3, 12.6, espejo=-1)
coloca("B", 0.8, -12.7, espejo=1)
pose("A", "listo", 0, 0.01, slouch=1.0)
pose("B", "bote", 0, 0.01, slouch=1.0)
J('tl.set("#A_sud, #B_sud", {opacity:0.28}, 0);')
pista("#A_sud", lambda t: round(0.28 * cansancio(t), 2), dec=2)
pista("#B_sud", lambda t: round(0.28 * cansancio(t), 2), dec=2)

# la bola en la mano del que saca (bota antes de sacar) — igual al principio y al final (bucle)
def bote_previo(t, pid="B", n=2):
    X, Z = POS[pid]
    lz = LADO_ACT[pid]
    mano = (X + 0.4 * (1 if lz < 0 else -1), 0.95, Z + 0.3 * (1 if lz < 0 else -1))
    suelo = (mano[0], 0.0, mano[2] + 0.05)
    for i in range(n):
        tt = t + i * 0.62
        bola_vuelo(tt, [(arco(mano, suelo, 0.0, 3), 0.3), (arco(suelo, mano, 0.0, 3), 0.3)], fantasmas=False)
        pose(pid, "bote", tt, 0.2, "sine.inOut", solo={"brR", "anR", "mgR"})
        fx("bote", tt + 0.3)

# ------------------------------------------------------------------ GUION VISUAL
rv = random.Random(4)
# 1) gancho: a las 20 h, B bota la bola y saca; peloteo lento y cansado
bote_previo(0.15, "B", 1)
POS["B"] = (0.8, -12.7)
fin1 = peloteo(0.85, R0 - 0.8, saca="B", lento=1.15, rng=rv)
# 2) rebobinado: todo vuelve a las 13:00 (cielo, público, cansancio, marcador)
pose("A", "listo", R0 + 0.2, 0.8, slouch=0.0)
pose("B", "listo", R0 + 0.2, 0.8, slouch=0.0)
coloca("A", 0.0, 12.5, R0 + 0.2, 1.2)
coloca("B", 0.0, -12.5, R0 + 0.2, 1.2)
fx("rebobina", R0)
t_ = peloteo(R1 + 0.2, F(4) + 0.6, saca="A", rng=rv)
# 4) fin del punto: el recogepelotas de la red corre a por la bola
camino("bk2", [(-5.9, -0.7), (-3.0, -0.9), (-5.9, -0.7)], t_ + 0.2, 1.6, piernas="correr")
pose("bk2", "agachado", t_ + 1.85, 0.25)
# 5) cambio de lado SIN banquillo (A baja, B sube), pasando junto a la silla del juez
T_CAMBIO = P("cambian") - 0.6
pose("A", "listo", T_CAMBIO - 0.3, 0.3)
camino("A", [POS["A"], (5.4, 3.5), (5.6, -1.2), (4.0, -8.0), (2.6, -13.6)], T_CAMBIO, 4.2, espejo=1)
camino("B", [POS["B"], (5.2, -3.5), (5.1, 1.2), (3.0, 8.0), (1.2, 12.6)], T_CAMBIO + 0.15, 4.2, espejo=-1)
LADO_ACT = {"A": -1, "B": 1}
# 6) los 25 segundos: toalla (del recogepelotas), agua y plátano en la esquina
T_TOA = P("toalla")
pose("bk5", "dar", T_TOA - 0.5, 0.3)
camino("A", [POS["A"], (4.0, -14.9)], T_CAMBIO + 4.3, 0.9)
pose("A", "toalla", T_TOA, 0.35)
pose("A", "beber", P("trago"), 0.35)
pose("A", "comer", P("platano"), 0.35)
pose("bk5", "firme", P("trago"), 0.3)
camino("A", [(4.0, -14.9), (0.6, -12.7)], FE(6) - 0.2, 1.0)
pose("A", "listo", FE(6) + 0.85, 0.3)
# toalla / botella / plátano en la mano de A
# 7-8) se reanuda, con el marcador corriendo
t_ = peloteo(F(7) + 0.4, P("doscientos") - 1.0, saca="A", rng=rv)
# 9) saque a 210 y luego a 180 km/h (marcador del fondo)
POS["A"] = (0.6, -12.7)
coloca("A", 0.6, -12.7, P("doscientos") - 1.0, 0.4)
peloteo(P("doscientos") - 0.6, P("doscientos") + 1.2, saca="A", rng=rv)
J(f'tl.set("#vel0", {{opacity:0}}, {P("doscientos") - 0.1:.2f}); tl.set("#vel1", {{opacity:1}}, {P("doscientos") - 0.1:.2f});')
coloca("A", -0.6, -12.7, P("ochenta") - 1.2, 0.4)
POS["A"] = (-0.6, -12.7)
peloteo(P("ochenta") - 0.8, F(10) + 2.5, saca="A", lento=1.05, rng=rv)
J(f'tl.set("#vel1", {{opacity:0}}, {P("ochenta") - 0.3:.2f}); tl.set("#vel2", {{opacity:1}}, {P("ochenta") - 0.3:.2f});')
J(f'tl.set("#vel2", {{opacity:0}}, {F(11):.2f}); tl.set("#vel0", {{opacity:1}}, {F(11):.2f});')
# 10-11) sol que se pone, focos, sudor y mareos
t_ = peloteo(F(10) + 2.7, P("mareos") - 0.2, saca="B", rng=rv)
J(f'tl.to("#A_h", {{rotation:8, svgOrigin:"0 -80", duration:0.5, yoyo:true, repeat:3, ease:"sine.inOut"}}, {P("mareos"):.2f});')
J(f'tl.to("#A", {{rotation:3, duration:0.6, yoyo:true, repeat:3, ease:"sine.inOut"}}, {P("mareos"):.2f});')
# 12) calambre: A se agacha y se agarra el gemelo; luego sigue
T_CAL = P("calambres")
pose("A", "calambre", T_CAL + 0.1, 0.45, "power2.out")
pose("A", "listo", P("seguir") - 0.1, 0.6, "power1.inOut")
# 13) relevo de recogepelotas y jueces de línea (los jugadores siguen)
T_REL = P("relevan") - 0.6
camino("bk5", [(4.6, -15.8), (9.6, -15.4)], T_REL, 1.8, espejo=-1)
J(f'tl.set("#bk7", {{opacity:1}}, {T_REL:.2f});')
camino("bk7", [(9.6, -15.0), (4.6, -15.8)], T_REL + 0.3, 1.8, espejo=1)
camino("lj4", [(8.0, -11.9), (9.9, -12.6)], T_REL + 0.2, 1.4)
J(f'tl.to("#lj4", {{opacity:0, duration:0.3}}, {T_REL + 1.5:.2f});')
J(f'tl.set("#lj7", {{opacity:1}}, {T_REL + 0.4:.2f});')
camino("lj7", [(9.8, -11.6), (8.0, -11.9)], T_REL + 0.5, 1.4)
pose("lj7", "sentado", T_REL + 1.95, 0.3)
pose("bk7", "firme", T_REL + 2.2, 0.3)
t_ = peloteo(F(13) + 0.3, F(14) - 0.2, saca="B", rng=rv)
# 14) medianoche: segundo cambio de lado (cada seis puntos), B vuelve abajo
T_C2 = F(14) + 0.1
camino("A", [POS["A"], (5.3, -3.5), (5.4, 1.2), (3.0, 8.0), (0.3, 12.6)], T_C2, 3.6, espejo=-1)
camino("B", [POS["B"], (5.0, 3.5), (5.0, -1.2), (3.0, -8.0), (0.8, -12.7)], T_C2 + 0.1, 3.6, espejo=1)
LADO_ACT = {"A": 1, "B": -1}
# 15-21) la noche: peloteos cada vez más lentos
t_ = peloteo(F(15) + 0.2, F(19) - 0.3, saca="B", lento=1.1, rng=rv)
# 19) saque a 180 de A (arriba): B llega tarde, la bola le pasa
POS["A"] = (0.5, 12.6)
peloteo(F(19) + 0.6, F(19) + 1.6, saca="A", lento=1.0, rng=rv)
t_ = peloteo(P("tarde", 3) + 0.6, F(20) - 0.1, saca="A", lento=1.15, rng=rv)
# 20) pelotas viejas: botan menos
t_ = peloteo(F(20) + 0.2, F(22) - 0.2, saca="B", botes=0.65, lento=1.15, rng=rv)
t_ = peloteo(F(22) + 0.1, F(24) + 0.6, saca="A", botes=0.7, lento=1.2, rng=rv)
# 24) ampollas: gesto de dolor (se mira la mano)
pose("B", "cansado", P("ampollas"), 0.4)
t_ = peloteo(P("golpe") - 0.2, F(26) - 0.2, saca="A", botes=0.7, lento=1.2, rng=rv)
# 26) el final vuelve al fotograma 0: B a la posición de saque, A lista, bola en la mano
coloca("A", 0.3, 12.6, F(26), 1.2)
coloca("B", 0.8, -12.7, F(26), 1.2)
pose("A", "listo", F(26) + 0.4, 0.6, slouch=1.0)
pose("B", "listo", F(26) + 0.4, 0.6, slouch=1.0)
bote_previo(DUR - 2.0, "B", 2)
pose("B", "bote", DUR - 0.75, 0.5, slouch=1.0)

# ------------------------------------------------------------------ OBJETOS EN LA MANO (toalla, botella, plátano)
mano_obj = ('<g id="toaA" opacity="0"><rect x="-10" y="-98" width="20" height="14" rx="3" fill="#f4f8fc"/></g>'
            '<g id="botA" opacity="0"><rect x="-6" y="-104" width="7" height="16" rx="2" fill="#4fd1ff"/></g>'
            '<g id="plaA" opacity="0"><path d="M-8,-96 Q-2,-84 4,-94" stroke="#ffd84a" stroke-width="5" fill="none" stroke-linecap="round"/></g>')
for sel, a, b in (("#toaA", P("toalla"), P("trago") - 0.1), ("#botA", P("trago"), P("platano") - 0.1), ("#plaA", P("platano"), FE(6) - 0.2)):
    J(f'tl.to("{sel}", {{opacity:1, duration:0.2}}, {a + 0.15:.2f}); tl.to("{sel}", {{opacity:0, duration:0.2}}, {b:.2f});')

# ------------------------------------------------------------------ CIELO, LUZ Y RELOJES
pista("#cDia", luzdia, dec=3)
pista("#cOcaso", ocaso, dec=3)
pista("#cAlba", alba, dec=3)
pista("#nubes", lambda t: round(0.85 * max(luzdia(t), ocaso(t) * 0.6), 2), dec=2)
def sol_xy(t):
    lh = LH(t)
    u = (lh - 6.0) / 13.6                        # 6:00 sale por la izquierda, 19:36 se pone por la derecha
    return 80 + 920 * u, 300 - 260 * math.sin(math.pi * max(0, min(1, u)))
pista("#sol", lambda t: round(sol_xy(t)[0], 0), prop="x", dec=0)
pista("#sol", lambda t: round(sol_xy(t)[1], 0), prop="y", dec=0)
pista("#sol", lambda t: 1.0 if 5.8 < LH(t) < 19.9 else 0.0)
pista("#oscuro", lambda t: round(0.62 * (1 - luzdia(t)) * (1 - 0.35 * focos(t)), 3))
pista("#oscuroP", lambda t: round(0.55 * (1 - luzdia(t)) * (1 - 0.75 * focos(t)), 3))
pista("#tinteOcaso", lambda t: round(0.22 * max(ocaso(t), alba(t) * 0.7), 3))
pista("#luzP", lambda t: round(focos(t) * (1 - luzdia(t)), 2), dec=2)
# reloj del partido, hora local y marcador (todo sale de las horas de tie-break)
hv = "hv"
J(f'const {hv} = {{v:20}};')
kf = []
last = None
for (ta, _), tb in zip([(t, 0) for t in TS], TS[1:]):
    kf.append(f'{{v:{H(tb):.4f}, duration:{tb - ta:.3f}, ease:"none"}}')
J('''function pintaReloj(h){
  const s = Math.max(0, Math.round(h * 3600)); const hh = Math.floor(s / 3600), mm = Math.floor(s % 3600 / 60), ss = s % 60;
  const p = n => String(n).padStart(2, "0");
  document.getElementById("crono").textContent = p(hh) + ":" + p(mm) + ":" + p(ss);
  const lm = Math.round((13 * 60 + h * 60)) % 1440;
  const hl = p(Math.floor(lm / 60)) + ":" + p(lm % 60);
  document.getElementById("horaLocal").textContent = hl;
  const n = Math.max(0, Math.round(h * 110)); const a = Math.ceil(n / 2), b = Math.floor(n / 2);
  const f = x => String(x).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ".");
  document.getElementById("ptsA").textContent = f(b); document.getElementById("ptsB").textContent = f(a);
  const noche = (lm < 6 * 60 + 30 || lm > 20 * 60); document.getElementById("icoSol").style.opacity = noche ? 0 : 1; document.getElementById("icoLuna").style.opacity = noche ? 1 : 0;
}''')
J(f'tl.to({hv}, {{keyframes:[{",".join(kf)}], onUpdate:() => pintaReloj({hv}.v)}}, 0);')
J(f'pintaReloj(20);')

# ------------------------------------------------------------------ DATOS JUNTO A LOS PROTAGONISTAS (HTML)
def chip(cid, x, y, html, t, hasta, cls="chip", desde="opacity:0, y:16"):
    OVR.append(f'<div id="{cid}" class="{cls}" style="left:{x}px;top:{y}px">{html}</div>')
    entra(f"#{cid}", t, desde)
    sale(f"#{cid}", hasta)
# gancho (y bucle: vuelve al final)
OVR.append('<div id="hook" class="gran"><b>20<i>HORAS</i></b><small>EL MISMO TIE-BREAK</small></div>')
J('tl.set("#hook", {opacity:1}, 0);')
J(f'tl.to("#hook", {{opacity:0, scale:0.92, transformOrigin:"50% 50%", duration:0.35}}, {R0 - 0.1:.2f});')
J(f'tl.fromTo("#hook", {{opacity:0, scale:1.06}}, {{opacity:1, scale:1, transformOrigin:"50% 50%", duration:0.6, ease:"power2.out", immediateRender:false}}, {DUR - 1.1:.2f});')
OVR.append('<div id="rebob" class="rebob">◀◀ 13:00</div>')
J(f'tl.set("#rebob", {{opacity:0}}, 0); tl.to("#rebob", {{opacity:1, duration:0.15}}, {R0:.2f}); tl.to("#rebob", {{opacity:0, duration:0.3}}, {R1 + 0.2:.2f});')
chip("cQuinto", 300, 760, '<b>6 – 6</b><small>QUINTO SET</small>', P("quinto"), F(3) + 0.2)
chip("cPista", 60, 1080, '<b>PISTA DURA</b><small>COMO EN NUEVA YORK</small>', P("dura"), P("quinto") - 0.1, cls="chip ama")
chip("cDiez", 330, 1110, '<b>A 10 PUNTOS</b><small>GANAR POR 2</small>', P("diez"), F(4) - 0.2)
chip("cNunca", 330, 1240, '<b class="rojo">+2 NUNCA LLEGA</b>', P("nunca"), F(4) - 0.2, cls="chip lite")
# 25 segundos: anillo que se vacía
OVR.append('<div id="c25" class="anillo" style="left:260px;top:930px"><svg width="170" height="170" viewBox="0 0 170 170"><circle cx="85" cy="85" r="72" stroke="rgba(255,255,255,0.18)" stroke-width="12" fill="rgba(4,10,20,0.55)"/><circle id="c25arco" cx="85" cy="85" r="72" stroke="#ffc24a" stroke-width="12" fill="none" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" transform="rotate(-90 85 85)"/></svg><b id="c25n">25</b><small>SEGUNDOS</small></div>')
entra("#c25", P("veinticinco") - 0.1, "opacity:0, scale:0.8")
J(f'tl.fromTo("#c25arco", {{attr:{{"stroke-dashoffset":0}}}}, {{attr:{{"stroke-dashoffset":1}}, duration:{FE(6) - P("veinticinco"):.2f}, ease:"none", immediateRender:false}}, {P("veinticinco"):.2f});')
J(f'const c25 = {{v:25}}; tl.to(c25, {{v:0, duration:{FE(6) - P("veinticinco"):.2f}, ease:"none", onUpdate:() => {{ document.getElementById("c25n").textContent = Math.ceil(c25.v); }}}}, {P("veinticinco"):.2f});')
sale("#c25", FE(6) + 0.2)
chip("cBanq", 60, 760, '<b class="rojo">✕ BANQUILLO</b><small>CADA 6 PUNTOS, DE PIE</small>', P("descanso"), FE(5))
chip("cToa", 470, 1310, '<b>TOALLA</b>', P("toalla"), FE(6) + 0.1, cls="chip lite")
chip("cAgua", 470, 1230, '<b>AGUA</b>', P("trago"), FE(6) + 0.1, cls="chip lite")
chip("cPla", 470, 1150, '<b>PLÁTANO</b>', P("platano"), FE(6) + 0.1, cls="chip lite")
chip("c35", 60, 1150, '<b>≈35 s</b><small>CADA PUNTO</small>', P("treinta"), FE(7))
chip("c100", 640, 1150, '<b>+100</b><small>PUNTOS POR HORA</small>', P("cien"), FE(7))
# glucógeno: batería que se vacía
OVR.append('<div id="cGlu" class="chip" style="left:640px;top:1200px"><div class="bat"><i id="batN"></i></div><div><b id="gluN">100%</b><small>GLUCÓGENO</small></div></div>')
entra("#cGlu", P("glucogeno") - 0.6)
J(f'tl.fromTo("#batN", {{width:"100%", background:"#35d987"}}, {{width:"12%", background:"#ff5a4f", duration:2.4, ease:"power1.in", immediateRender:false}}, {P("glucogeno") - 0.4:.2f});')
J(f'const glu = {{v:100}}; tl.to(glu, {{v:12, duration:2.4, ease:"power1.in", onUpdate:() => {{ document.getElementById("gluN").textContent = Math.round(glu.v) + "%"; }}}}, {P("glucogeno") - 0.4:.2f});')
sale("#cGlu", FE(8))
chip("cVel", 330, 1150, '<b><span class="tach">210</span> → <span class="rojo">180</span></b><small>KM/H DE SAQUE</small>', P("ochenta") - 0.2, FE(9) + 0.3)
chip("c6h", 340, 880, '<b>19:00</b><small>SE PONE EL SOL</small>', P("seis", 3) - 0.1, FE(10))
chip("cSudor", 640, 1180, '<b>+6 L</b><small>DE SUDOR</small>', P("litros") - 0.3, P("mareos") + 1.4)
chip("cSodio", 60, 1180, '<b class="rojo">SODIO ↓</b><small>MAREOS</small>', P("sodio") - 0.1, FE(11) + 0.2)
chip("cCal", 300, 1180, '<b class="rojo">CALAMBRE</b><small>SIN ATENCIÓN MÉDICA</small>', P("calambre") - 0.2, FE(12))
chip("cRel", 640, 1640, '<b>RELEVO</b><small>CADA TURNO</small>', P("relevan") - 0.2, FE(13), cls="chip lite")
chip("cJugNo", 330, 1180, '<b class="rojo">LOS JUGADORES, NO</b>', P("jugadores") - 0.2, FE(13) + 0.2, cls="chip lite")
chip("c00", 380, 880, '<b>00:00</b><small>EL PÚBLICO SE VA</small>', P("medianoche") - 0.1, FE(14) + 0.2)
chip("cLim", 300, 860, '<b>SIN HORA LÍMITE</b>', P("limite") - 0.3, P("partido") - 0.1, cls="chip ama")
chip("cRec1", 300, 860, '<b>02:50</b><small>EL FINAL MÁS TARDÍO DEL TORNEO</small>', P("madrugada") - 0.8, FE(15) + 0.3)
chip("c14", 330, 1150, '<b>14 HORAS</b><small>DE TIE-BREAK</small>', P("catorce") - 0.1, FE(16) + 0.2)
OVR.append('<div id="cKcal" class="chip" style="left:300px;top:1150px"><div><b id="kcalN">0</b><small>KCAL CADA UNO</small></div></div>')
entra("#cKcal", P("quemado") - 0.2)
J(f'const kc = {{v:0}}; tl.to(kc, {{v:9000, duration:1.6, ease:"power2.out", onUpdate:() => {{ document.getElementById("kcalN").textContent = String(Math.round(kc.v / 50) * 50).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, "."); }}}}, {P("quemado"):.2f});')
sale("#cKcal", FE(17))
chip("c4d", 330, 1260, '<b>= 4 DÍAS</b><small>DE COMIDA NORMAL</small>', P("cuatro", 1) - 0.3, FE(17), cls="chip lite")
chip("cDesp", 60, 1150, '<b>20 h</b><small>DESPIERTOS</small>', P("despiertos") - 0.3, FE(18))
chip("cAlc", 600, 1150, '<b class="rojo">REFLEJOS</b><small>COMO CON ALCOHOL</small>', P("alcohol") - 0.5, FE(18) + 0.2)
chip("cMedio", 600, 1180, '<b>0,5 s</b><small>PARA REACCIONAR</small>', P("medio") - 0.2, FE(19))
chip("cTarde", 160, 1180, '<b class="rojo">LLEGA TARDE</b>', P("tarde", 3) - 0.2, FE(19) + 0.2, cls="chip lite")
chip("cBola", 300, 1150, '<b>LA MISMA PELOTA</b><small>HACE HORAS</small>', P("pelotas") - 0.1, P("pierden") - 0.1)
chip("cBota", 300, 1150, '<b class="rojo">BOTA MENOS</b><small>PIERDE PRESIÓN</small>', P("pierden"), FE(20) + 0.2)
OVR.append('<div id="cKm" class="chip" style="left:330px;top:1150px"><div><b id="kmN">0 km</b><small>CORRIENDO A SPRINTS</small></div></div>')
entra("#cKm", P("corrido") - 0.2)
J(f'const km = {{v:0}}; tl.to(km, {{v:40, duration:1.4, ease:"power2.out", onUpdate:() => {{ document.getElementById("kmN").textContent = Math.round(km.v) + " km"; }}}}, {P("corrido"):.2f});')
sale("#cKm", FE(21))
chip("cMar", 330, 1260, '<b>≈ MARATÓN</b><small>42 KM</small>', P("maraton") - 0.2, FE(21), cls="chip lite")
chip("cAma", 340, 880, '<b>06:30</b><small>QUEDAN UNOS CIENTOS</small>', P("amanece") - 0.1, FE(22) + 0.2)
chip("cMil", 330, 1150, '<b>+1.000</b><small>PUNTOS CADA UNO</small>', P("mil", 2) - 0.3, FE(23) + 0.2)
chip("cAmp", 330, 1250, '<b class="rojo">AMPOLLAS</b><small>MANOS Y PIES</small>', P("ampollas") - 0.2, FE(24))
# récord real frente a este partido: dos barras
OVR.append('<div id="cRec" class="comp" style="left:90px;top:1120px">'
           '<div class="fila2"><small>RÉCORD REAL · 3 DÍAS</small><div class="barra"><i id="barR"></i></div><b>11 h 05</b></div>'
           '<div class="fila2"><small>ESTE PARTIDO · SIN PARAR</small><div class="barra"><i id="barE" class="rojo"></i></div><b class="rojo">20 h</b></div></div>')
entra("#cRec", P("record") - 0.2)
J(f'tl.fromTo("#barR", {{width:"0%"}}, {{width:"55%", duration:0.9, ease:"power2.out", immediateRender:false}}, {P("once"):.2f});')
J(f'tl.fromTo("#barE", {{width:"0%"}}, {{width:"100%", duration:1.0, ease:"power2.out", immediateRender:false}}, {P("dias", 2):.2f});')
sale("#cRec", F(26) + 1.2)
chip("cEmp", 360, 1150, '<b>EMPATE</b><small>OTRA VEZ</small>', P("empate") - 0.2, DUR - 1.3)

# marcas de ampollas y calambre sobre B / A (círculos que laten en la figura)
J('tl.set("#A_cal, #B_amp1, #B_amp2", {opacity:0}, 0);')
J(f'tl.to("#A_cal", {{opacity:1, duration:0.2}}, {T_CAL + 0.3:.2f}); tl.to("#A_cal", {{scale:1.4, svgOrigin:"12 -14", duration:0.4, yoyo:true, repeat:5}}, {T_CAL + 0.3:.2f}); tl.to("#A_cal", {{opacity:0, duration:0.3}}, {P("seguir") - 0.1:.2f});')
J(f'tl.to("#B_amp1, #B_amp2", {{opacity:1, duration:0.3}}, {P("ampollas") + 0.2:.2f}); tl.to("#B_amp1, #B_amp2", {{opacity:0, duration:0.3}}, {FE(24) + 0.3:.2f});')

# ------------------------------------------------------------------ cámara: casi quieta, se acerca suave en 2 momentos
J('tl.set("#cam", {transformOrigin:"540px 1300px", scale:1, x:0, y:0}, 0);')
J(f'tl.to("#cam", {{scale:1.28, x:-140, y:-150, duration:2.2, ease:"sine.inOut"}}, {T_TOA - 1.6:.2f}); tl.to("#cam", {{scale:1, x:0, y:0, duration:2.2, ease:"sine.inOut"}}, {FE(6) + 0.4:.2f});')
J(f'tl.to("#cam", {{scale:1.25, x:0, y:-130, duration:2.0, ease:"sine.inOut"}}, {T_CAL - 0.9:.2f}); tl.to("#cam", {{scale:1, x:0, y:0, duration:2.2, ease:"sine.inOut"}}, {P("seguir") + 0.4:.2f});')

# ------------------------------------------------------------------ ensamblar SVG
# marcas sobre las figuras: van dentro de su grupo (coordenadas locales)
jug_svg = jug_svg.replace('<g id="A_hd"', '<circle id="A_cal" cx="12" cy="-14" r="7" fill="none" stroke="#ff5a4f" stroke-width="3"/><g id="A_hd"')
jug_svg = jug_svg.replace('<g id="B_hd"', '<circle id="B_amp1" cx="8" cy="-50" r="4" fill="#ff5a4f" opacity="0.9"/><circle id="B_amp2" cx="13" cy="0" r="4" fill="#ff5a4f" opacity="0.9"/><g id="B_hd"')
jug_svg = jug_svg.replace('<g id="A_hd"', mano_obj + '<g id="A_hd"', 1)
fondo_staff = "".join(p for p in personas_staff)
svg = (f'<g id="cielo">{svg_cielo}</g>'
       f'<g id="gradas">{"".join(bandas)}{svg_publico}</g>'
       f'{svg_aro}<rect id="oscuro" x="-200" y="-200" width="1480" height="2400" fill="#050b1e" opacity="0"/>'
       f'<rect id="tinteOcaso" x="-200" y="-200" width="1480" height="2400" fill="#ff8a4a" opacity="0" style="mix-blend-mode:soft-light"/>'
       f'{"".join(lamparas)}'
       f'<g id="muros">{muros}</g>'
       f'<g id="suelo">{pista_svg}</g>'
       f'<rect id="oscuroP" x="-200" y="560" width="1480" height="1600" fill="#050b1e" opacity="0"/>'
       f'<g id="mobiliario">{banquillo(-2.6)}{banquillo(2.6)}{silla_juez()}</g>'
       f'{fondo_staff}{red_svg}{bola_svg}{jug_svg}'
       f'<g id="halos" style="mix-blend-mode:screen">{"".join(halos)}</g>')
# los de la mitad de abajo se dibujan delante de la red: reordenar figuras por profundidad no hace falta (la red es transparente)

# ------------------------------------------------------------------ subtítulos
CLAVE = set(norm(w) for w in ["veinte", "horas", "tiebreak", "nadie", "una", "dura", "diez", "dos", "nunca", "veinticinco", "sentado", "seis",
                               "toalla", "agua", "platano", "treinta", "cien", "glucogeno", "doscientos", "ochenta", "sol", "focos", "litros",
                               "sodio", "mareos", "calambres", "calambre", "relevan", "no", "medianoche", "limite", "madrugada", "catorce",
                               "nueve", "cuatro", "despiertos", "alcohol", "medio", "tarde", "cambian", "presion", "cuarenta", "maraton",
                               "amanece", "cientos", "mil", "ampollas", "duele", "once", "cinco", "tres", "pausa", "empate"])
DEBIL = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "y", "a", "en", "con", "que", "por", "tu", "se", "lo", "no", "solo", "esa", "esos", "su"}
chunks, cur = [], []
for p in T["palabras"]:
    cur.append(p)
    txt = " ".join(x["w"] for x in cur)
    fin_frase = re.search(r"[.:;?!…]$", p["w"])
    if fin_frase or ((len(cur) >= 5 or len(txt) >= 28) and norm(p["w"]) not in DEBIL) or len(cur) >= 7:
        chunks.append(cur); cur = []
if cur:
    chunks.append(cur)
SUBS = []
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
#cam{{position:absolute;inset:0}}
.gran{{position:absolute;left:0;right:0;top:1060px;text-align:center;white-space:nowrap;text-shadow:0 6px 24px rgba(0,10,25,0.7)}}
.gran b{{display:block;font:900 200px/1 Inter;letter-spacing:-8px;color:#fff;font-variant-numeric:tabular-nums}} .gran b i{{font-style:normal;font-size:70px;letter-spacing:0;margin-left:16px;color:{AM}}}
.gran small{{display:inline-block;margin-top:14px;padding:8px 20px;border-radius:12px;background:rgba(4,10,20,0.6);font:800 34px Inter;letter-spacing:7px;color:#fff}}
.rebob{{position:absolute;left:0;right:0;top:1100px;text-align:center;font:900 120px Inter;letter-spacing:-3px;color:#fff;text-shadow:0 6px 24px rgba(0,0,0,0.6)}}
.chip{{position:absolute;display:flex;align-items:center;gap:14px;padding:12px 20px;border-radius:16px;background:rgba(6,14,28,0.78);border:1px solid rgba(255,255,255,0.22);white-space:nowrap;box-shadow:0 8px 24px rgba(0,0,0,0.35)}}
.chip b{{display:block;font:800 50px/1 Inter;color:#fff;font-variant-numeric:tabular-nums}} .chip small{{display:block;margin-top:5px;font:800 18px Inter;letter-spacing:4px;color:#b9c9da}}
.chip.ama{{border-left:6px solid {AM}}} .chip.lite b{{font-size:34px}}
.rojo{{color:{RJ} !important}} .tach{{text-decoration:line-through;color:#9fb3c8}}
.anillo{{position:absolute;width:170px;height:170px;text-align:center}} .anillo svg{{position:absolute;left:0;top:0}}
.anillo b{{position:absolute;left:0;right:0;top:44px;font:900 64px/1 Inter;color:#fff}} .anillo small{{position:absolute;left:0;right:0;top:110px;font:800 14px Inter;letter-spacing:3px;color:#ffe2a8}}
.bat{{width:70px;height:34px;border:4px solid #fff;border-radius:6px;padding:3px;position:relative}} .bat:after{{content:"";position:absolute;right:-10px;top:8px;width:6px;height:12px;background:#fff;border-radius:2px}}
.bat i{{display:block;height:100%;width:100%;background:{VE};border-radius:2px}}
.comp{{position:absolute;width:900px;padding:18px 24px;border-radius:18px;background:rgba(6,14,28,0.8);border:1px solid rgba(255,255,255,0.2)}}
.fila2{{display:grid;grid-template-columns:330px 1fr 130px;align-items:center;gap:14px;margin:8px 0}} .fila2 small{{font:800 18px Inter;letter-spacing:3px;color:#b9c9da}} .fila2 b{{font:900 36px Inter;color:#fff;text-align:right}}
.barra{{height:22px;border-radius:11px;background:rgba(255,255,255,0.12);overflow:hidden}} .barra i{{display:block;height:100%;width:0;background:{CY_};border-radius:11px}} .barra i.rojo{{background:{RJ}}}
#hud{{position:absolute;left:36px;top:500px;z-index:60;display:flex;gap:10px;align-items:stretch;font-family:Inter}}
.sb{{background:rgba(6,12,24,0.86);border-radius:12px;overflow:hidden;border:1px solid rgba(255,255,255,0.18)}}
.sb .tit{{background:#0e5a3c;color:#e9d58a;font:800 15px Inter;letter-spacing:3px;padding:5px 12px}}
.sb .row{{display:grid;grid-template-columns:22px 110px 38px 38px 120px;align-items:center;padding:5px 12px;font:800 24px Inter;color:#fff}}
.sb .row i{{width:12px;height:12px;border-radius:50%;display:block}} .sb .row span{{text-align:center;color:#b9c9da}} .sb .row b{{text-align:right;color:{AM};font-variant-numeric:tabular-nums}}
#relojes{{position:absolute;right:36px;top:500px;z-index:60;text-align:right;background:rgba(6,12,24,0.86);border-radius:12px;padding:8px 16px;border:1px solid rgba(255,255,255,0.18)}}
#relojes small{{display:block;font:800 14px Inter;letter-spacing:3px;color:#b9c9da}} #crono{{display:block;font:900 40px/1.1 Inter;color:#fff;font-variant-numeric:tabular-nums}}
#horaL{{display:flex;justify-content:flex-end;align-items:center;gap:8px;margin-top:4px;font:800 26px Inter;color:#ffe2a8;font-variant-numeric:tabular-nums}}
#horaL span.ic{{position:relative;width:24px;height:24px}} #icoSol,#icoLuna{{position:absolute;inset:0}}
#flash{{position:absolute;inset:0;z-index:50;background:#fff;opacity:0;pointer-events:none}}
#grano{{position:absolute;inset:0;z-index:57;pointer-events:none;opacity:0.035;background:url(assets/grano.png);mix-blend-mode:overlay}}
#vineta{{position:absolute;inset:0;z-index:56;pointer-events:none;background:radial-gradient(115% 85% at 50% 55%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.45))}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:520px;z-index:55;pointer-events:none;background:linear-gradient(rgba(2,6,14,0.72), rgba(2,6,14,0))}}
#marca{{position:absolute;left:0;right:0;top:1775px;text-align:center;font:700 28px Inter;color:#ffffff;opacity:0.32;pointer-events:none;z-index:61}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 62px Inter;color:rgba(255,255,255,0.42);line-height:1.22;text-shadow:0 3px 12px rgba(0,0,0,0.6)}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:3px solid #4ea3ff;border-radius:6px;background:rgba(78,163,255,0.18);opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="cam"><svg width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0;overflow:visible"><defs>{"".join(DEFS)}</defs>{svg}</svg>
  {"".join(OVR)}</div>
  <div id="flash"></div>
  <div id="topsombra"></div><div id="vineta"></div><div id="grano"></div>
  <div id="hud"><div class="sb"><div class="tit">QUINTO SET · TIE-BREAK</div>
    <div class="row"><i style="background:{JUG["A"]["cam"]}"></i>RIVAS<span>2</span><span>6</span><b id="ptsA">1.100</b></div>
    <div class="row"><i style="background:{JUG["B"]["cam"]}"></i>LANG<span>2</span><span>6</span><b id="ptsB">1.100</b></div></div></div>
  <div id="relojes"><small>TIEMPO DE TIE-BREAK</small><b id="crono">20:00:00</b>
    <div id="horaL"><span class="ic"><svg id="icoSol" viewBox="0 0 24 24"><circle cx="12" cy="12" r="6" fill="#ffd27a"/></svg><svg id="icoLuna" viewBox="0 0 24 24" style="opacity:0"><path d="M15,3 A9,9 0 1 0 21,15 A7,7 0 1 1 15,3 Z" fill="#e9eefc"/></svg></span><span id="horaLocal">09:00</span></div></div>
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
json.dump([[round(t, 2), round(publico(t), 3)] for t in TS], open(os.path.join(BASE, "ambiente.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones · {sum(len(v) for v in gr_ropa.values())} espectadores")

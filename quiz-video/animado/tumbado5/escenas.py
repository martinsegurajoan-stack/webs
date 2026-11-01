# ------------------------------------------------------------------ construcción del mundo (escenarios decorados)
# Seis habitaciones seguidas, como una casa de muñecas: la cámara pasa de una a otra.
H = []   # HTML del mundo
RW, FLOOR = 1500, 1700
def RL(k):
    return k * RW

def sala(k, cuerpo, fondo):
    """SVG de una habitación completa (1500x1920) con su pared/suelo y lo que lleve dentro."""
    return (f'<svg class="sala" style="position:absolute;left:{RL(k)}px;top:0;overflow:visible" width="{RW}" height="1920" '
            f'viewBox="0 0 {RW} 1920">{fondo}{cuerpo}</svg>')

def pared_suelo(pid, w1, w2, f1, f2, rayas=True, zocalo="#fff3e6"):
    d = (f'<defs><linearGradient id="{pid}w" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{w1}"/><stop offset="1" stop-color="{w2}"/></linearGradient>'
         f'<linearGradient id="{pid}f" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{f1}"/><stop offset="1" stop-color="{f2}"/></linearGradient></defs>'
         f'<rect x="0" y="0" width="{RW}" height="{FLOOR}" fill="url(#{pid}w)"/>')
    if rayas:
        d += "".join(f'<rect x="{x}" y="0" width="26" height="{FLOOR}" fill="#ffffff" opacity="0.07"/>' for x in range(20, RW, 70))
    d += (f'<rect x="0" y="{FLOOR - 60}" width="{RW}" height="60" fill="{zocalo}"/>'
          f'<rect x="0" y="{FLOOR}" width="{RW}" height="{1920 - FLOOR}" fill="url(#{pid}f)"/>'
          + "".join(f'<line x1="0" y1="{FLOOR + 40 + i * 45}" x2="{RW}" y2="{FLOOR + 40 + i * 45}" stroke="#000" stroke-opacity="0.08" stroke-width="3"/>' for i in range(5)))
    d += f'<rect x="0" y="0" width="{RW}" height="1920" fill="url(#luzsala)" opacity="0.55"/>'
    return d

def ventana(x, y, w, h, noche=False, cortina="#6a8caf"):
    cielo = ("#1d2356", "#3b3f7a") if noche else ("#9fd3f5", "#e4f4ff")
    s = (f'<rect x="{x - 14}" y="{y - 14}" width="{w + 28}" height="{h + 28}" rx="10" fill="#fbf6ee"/>'
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{cielo[1]}"/><rect x="{x}" y="{y}" width="{w}" height="{h * 0.6:.0f}" fill="{cielo[0]}" opacity="0.6"/>')
    if not noche:
        s += (f'<ellipse cx="{x + w * 0.3:.0f}" cy="{y + h * 0.3:.0f}" rx="60" ry="22" fill="#fff" opacity="0.9"/>'
              f'<ellipse cx="{x + w * 0.65:.0f}" cy="{y + h * 0.45:.0f}" rx="45" ry="16" fill="#fff" opacity="0.8"/>'
              f'<rect x="{x}" y="{y + h * 0.78:.0f}" width="{w}" height="{h * 0.22:.0f}" fill="#8cc28a" opacity="0.8"/>')
    s += (f'<rect x="{x + w / 2 - 6:.0f}" y="{y}" width="12" height="{h}" fill="#fbf6ee"/><rect x="{x}" y="{y + h / 2 - 6:.0f}" width="{w}" height="12" fill="#fbf6ee"/>'
          f'<path d="M{x - 40},{y - 40} L{x + 70},{y - 40} C{x + 50},{y + h * 0.4:.0f} {x + 90},{y + h * 0.8:.0f} {x + 40},{y + h + 60} L{x - 40},{y + h + 60} Z" fill="{cortina}"/>'
          f'<path d="M{x + w + 40},{y - 40} L{x + w - 70},{y - 40} C{x + w - 50},{y + h * 0.4:.0f} {x + w - 90},{y + h * 0.8:.0f} {x + w - 40},{y + h + 60} L{x + w + 40},{y + h + 60} Z" fill="{cortina}"/>'
          f'<rect x="{x - 70}" y="{y - 52}" width="{w + 140}" height="16" rx="8" fill="#8a5a3c"/>')
    return s

def planta(x, y, seca=False):
    hoja = "#9b7b4b" if seca else "#4f9a6a"
    s = f'<path d="M{x - 45},{y} L{x + 45},{y} L{x + 34},{y + 90} L{x - 34},{y + 90} Z" fill="#c0704f"/>'
    for a in (-60, -30, 0, 30, 60):
        s += f'<path d="M{x},{y} Q{x + a * 1.3},{y - 110} {x + a * 1.8},{y - (60 if seca else 170)}" stroke="{hoja}" stroke-width="14" fill="none" stroke-linecap="round"/>'
    return s

def cuadro(x, y, w, h):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#8a5a3c"/><rect x="{x + 14}" y="{y + 14}" width="{w - 28}" height="{h - 28}" fill="#f6e7d2"/>'
            f'<path d="M{x + 14},{y + h - 14} L{x + w * 0.4:.0f},{y + h * 0.4:.0f} L{x + w * 0.6:.0f},{y + h * 0.65:.0f} L{x + w * 0.75:.0f},{y + h * 0.5:.0f} L{x + w - 14},{y + h - 14} Z" fill="#7aa38f"/>'
            f'<circle cx="{x + w * 0.72:.0f}" cy="{y + h * 0.3:.0f}" r="18" fill="#f2b84b"/>')

def reloj(cid, x, y, r=70):
    return (f'<circle cx="{x}" cy="{y}" r="{r + 10}" fill="#3d405b"/><circle cx="{x}" cy="{y}" r="{r}" fill="#fbf8f2"/>'
            + "".join(f'<line x1="{x + (r - 10) * math.cos(a * math.pi / 6):.0f}" y1="{y + (r - 10) * math.sin(a * math.pi / 6):.0f}" x2="{x + (r - 22) * math.cos(a * math.pi / 6):.0f}" y2="{y + (r - 22) * math.sin(a * math.pi / 6):.0f}" stroke="#3d405b" stroke-width="5"/>' for a in range(12))
            + f'<line id="{cid}h" x1="{x}" y1="{y}" x2="{x}" y2="{y - r * 0.5:.0f}" stroke="#1d2b33" stroke-width="9" stroke-linecap="round"/>'
            f'<line id="{cid}m" x1="{x}" y1="{y}" x2="{x + r * 0.75:.0f}" y2="{y}" stroke="#e5484d" stroke-width="6" stroke-linecap="round"/><circle cx="{x}" cy="{y}" r="8" fill="#1d2b33"/>')

def calendario(cid, x, y, txt):
    return (f'<rect x="{x}" y="{y}" width="150" height="170" rx="12" fill="#fbf8f2"/><rect x="{x}" y="{y}" width="150" height="46" rx="12" fill="#e5484d"/>'
            f'<circle cx="{x + 40}" cy="{y}" r="8" fill="#3d405b"/><circle cx="{x + 110}" cy="{y}" r="8" fill="#3d405b"/>'
            f'<text id="{cid}" x="{x + 75}" y="{y + 125}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="40" fill="#1d2b33">{txt}</text>')

def lampara_mesita(x):
    return (f'<rect x="{x}" y="1440" width="170" height="260" rx="10" fill="#b07a52"/><rect x="{x}" y="1440" width="170" height="26" rx="8" fill="#c99067"/>'
            f'<rect x="{x + 20}" y="1520" width="130" height="10" rx="5" fill="#8a5a3c"/><circle cx="{x + 85}" cy="1560" r="8" fill="#e2c27a"/>'
            f'<rect x="{x + 75}" y="1330" width="20" height="110" fill="#8a5a3c"/><path d="M{x + 25},1340 L{x + 145},1340 L{x + 115},1250 L{x + 55},1250 Z" fill="#f2d27a"/>'
            f'<ellipse cx="{x + 85}" cy="1360" rx="160" ry="120" fill="#fff1c9" opacity="0.18"/>')

# --- cama con el personaje TUMBADO (el SVG del personaje girado -90°, cabeza en la almohada)
def cama_tumbado(pid, cx, cy, s=0.62, inclin=0, **kw):
    m_top = cy + 205 * s
    pie_x = cx + 860 * s
    out = (f'<div id="{pid}-lie" style="position:absolute;left:0;top:0;width:1px;height:1px;overflow:visible">'
           f'<svg style="position:absolute;left:0;top:0;overflow:visible" width="1" height="1">'
           # cabecero y patas
           f'<rect x="{cx - 380 * s:.0f}" y="{cy - 330 * s:.0f}" width="{60 * s:.0f}" height="{FLOOR - cy + 330 * s:.0f}" rx="18" fill="#8a5a3c"/>'
           f'<rect x="{cx - 330 * s:.0f}" y="{cy - 270 * s:.0f}" width="{40 * s:.0f}" height="{(m_top - cy + 270 * s):.0f}" rx="10" fill="#a8714c"/>'
           f'<rect x="{pie_x - 10:.0f}" y="{m_top - 60:.0f}" width="{50 * s:.0f}" height="{FLOOR - m_top + 60:.0f}" rx="14" fill="#8a5a3c"/>'
           f'<rect x="{cx - 330 * s:.0f}" y="{m_top + 90 * s:.0f}" width="{pie_x - cx + 330 * s:.0f}" height="{40 * s:.0f}" fill="#7a4e33"/>'
           f'<rect x="{cx - 320 * s:.0f}" y="{m_top:.0f}" width="{pie_x - cx + 320 * s:.0f}" height="{100 * s:.0f}" rx="16" fill="#f4efe6"/>'
           f'<ellipse cx="{cx - 150 * s:.0f}" cy="{m_top - 30 * s:.0f}" rx="{175 * s:.0f}" ry="{70 * s:.0f}" fill="#ffffff"/>'
           f'<ellipse cx="{cx - 150 * s:.0f}" cy="{m_top - 10 * s:.0f}" rx="{165 * s:.0f}" ry="{40 * s:.0f}" fill="#e9e1d4"/></svg>'
           f'<div id="{pid}-rot" style="position:absolute;left:0;top:0;width:1px;height:1px;overflow:visible">'
           f'<div style="position:absolute;left:{cx - 500:.0f}px;top:{cy - 900:.0f}px;width:1000px;height:1800px;transform-origin:500px 900px;transform:rotate(-90deg) scale({s})">'
           + personaje(pid, **kw).replace("{x}", "0") +
           '</div></div>'
           # manta por encima del cuerpo (deja ver la cabeza)
           f'<svg style="position:absolute;left:0;top:0;overflow:visible" width="1" height="1">'
           f'<path id="{pid}-manta" d="M{cx + 40 * s:.0f},{cy - 205 * s:.0f} C{cx + 300 * s:.0f},{cy - 245 * s:.0f} {cx + 600 * s:.0f},{cy - 225 * s:.0f} {cx + 790 * s:.0f},{cy - 175 * s:.0f} '
           f'C{cx + 860 * s:.0f},{cy - 150 * s:.0f} {cx + 880 * s:.0f},{cy - 20 * s:.0f} {pie_x + 10:.0f},{m_top + 110 * s:.0f} L{cx + 10 * s:.0f},{m_top + 110 * s:.0f} '
           f'C{cx - 20 * s:.0f},{cy + 40 * s:.0f} {cx - 10 * s:.0f},{cy - 120 * s:.0f} {cx + 40 * s:.0f},{cy - 205 * s:.0f} Z" fill="url(#manta)"/>'
           f'<path d="M{cx + 40 * s:.0f},{cy - 200 * s:.0f} C{cx + 20 * s:.0f},{cy - 80 * s:.0f} {cx + 20 * s:.0f},{cy + 80 * s:.0f} {cx + 40 * s:.0f},{m_top + 100 * s:.0f}" stroke="#fbf6ee" stroke-width="{34 * s:.0f}" fill="none" stroke-linecap="round"/>'
           + "".join(f'<path d="M{cx + (180 + i * 150) * s:.0f},{cy - (215 - i * 5) * s:.0f} q{30 * s:.0f},{150 * s:.0f} {10 * s:.0f},{330 * s:.0f}" stroke="#2f4f7a" stroke-width="5" fill="none" opacity="0.35"/>' for i in range(4))
           + '</svg></div>')
    return out

DEFS = ('<svg width="0" height="0" style="position:absolute"><defs>'
        '<radialGradient id="luzsala" cx="0.5" cy="0.35" r="0.75"><stop offset="0" stop-color="#ffffff" stop-opacity="0.35"/><stop offset="1" stop-color="#2a2550" stop-opacity="0.35"/></radialGradient>'
        '<linearGradient id="manta" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5b86c4"/><stop offset="1" stop-color="#3d5f99"/></linearGradient>'
        '</defs></svg>')
H.append(DEFS)

# ---- 0 · DORMITORIO, día 1
L0 = RL(0)
H.append(sala(0, ventana(940, 420, 330, 470) + cuadro(230, 520, 230, 230) + reloj("clk", 640, 640) + calendario("cal0", 1290, 1010, "DÍA 1")
              + lampara_mesita(40) + f'<ellipse cx="760" cy="1800" rx="560" ry="60" fill="#c56f55" opacity="0.55"/>'
              + planta(1380, 1610), pared_suelo("s0", "#f6dcc6", "#eac3a6", "#b07a52", "#8a5a3c")))
BED0 = (L0 + 470, 1330)
H.append(cama_tumbado("p0", *BED0, s=0.62, cm=7))
# mesa de cama con bandeja (entra al decir «comida»)
TRAY = f'''<svg id="bandeja" style="position:absolute;left:{L0 + 640}px;top:1010px;overflow:visible;opacity:0" width="10" height="10">
<rect x="250" y="80" width="22" height="610" fill="#9aa3b5"/><rect x="190" y="680" width="140" height="18" rx="9" fill="#7c8496"/>
<rect x="-20" y="70" width="300" height="24" rx="10" fill="#c99067"/>
<ellipse cx="80" cy="55" rx="70" ry="20" fill="#fbf8f2"/><ellipse cx="80" cy="50" rx="46" ry="12" fill="#e5a24e"/><circle cx="60" cy="44" r="10" fill="#6aa86b"/>
<rect x="170" y="10" width="34" height="58" rx="6" fill="#dff1fb" opacity="0.9"/><rect x="170" y="32" width="34" height="36" rx="4" fill="#f6a35c" opacity="0.8"/>
<circle cx="235" cy="50" r="18" fill="#e5484d"/><path d="M235,32 q4,-10 10,-12" stroke="#4f9a6a" stroke-width="5" fill="none"/></svg>'''
H.append(TRAY)
# gafas de sol (vacaciones)
H.append(f'<svg id="gafas" style="position:absolute;left:{BED0[0] - 128}px;top:{BED0[1] - 90}px;overflow:visible;opacity:0" width="10" height="10">'
         '<g transform="rotate(-90 40 90)"><rect x="-30" y="70" width="58" height="40" rx="14" fill="#1d2b33"/><rect x="52" y="70" width="58" height="40" rx="14" fill="#1d2b33"/>'
         '<path d="M28,88 L52,88" stroke="#1d2b33" stroke-width="7"/><rect x="-20" y="76" width="18" height="8" rx="4" fill="#ffffff" opacity="0.5"/></g></svg>')
# flecha de «darte la vuelta» alrededor de la cama
H.append(f'<svg id="vuelta" style="position:absolute;left:{BED0[0] + 60}px;top:{BED0[1] - 330}px;overflow:visible;opacity:0" width="10" height="10">'
         f'<path id="vuelta-p" d="M40,250 C40,40 420,40 420,230" stroke="{KEY}" stroke-width="18" fill="none" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
         f'<path d="M392,200 L422,250 L455,200" stroke="{KEY}" stroke-width="18" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
         f'<text x="230" y="40" text-anchor="middle" font-family="Inter" font-weight="900" font-size="56" fill="#fbf8f2">CADA 2 H</text></svg>')
# lupa con las escaras
H.append(f'<div id="escaras" class="card" style="left:{L0 + 860}px;top:880px;width:380px;padding:22px 26px">'
         f'<div class="card-top" style="font-size:28px">ESCARAS</div>'
         f'<svg width="330" height="190" viewBox="0 0 330 190"><ellipse cx="165" cy="95" rx="150" ry="85" fill="{SKIN}"/>'
         f'<ellipse cx="120" cy="80" rx="30" ry="22" fill="#d6655a" class="llaga" opacity="0"/><ellipse cx="200" cy="110" rx="40" ry="26" fill="#c2453e" class="llaga" opacity="0"/>'
         f'<ellipse cx="170" cy="60" rx="18" ry="13" fill="#e07a6a" class="llaga" opacity="0"/></svg></div>')
# fuerza de las piernas
H.append(f'<div id="fuerza" class="card" style="left:{L0 + 860}px;top:880px;width:400px"><div class="card-top" style="font-size:28px">FUERZA EN LAS PIERNAS</div>'
         f'<div style="position:relative;height:46px;margin-top:22px;border-radius:23px;background:#ece6db"><div id="fuerza-b" style="position:absolute;left:0;top:0;bottom:0;width:100%;border-radius:23px;background:linear-gradient(90deg,{BAD},#f08a5d);transform-origin:0 50%"></div></div>'
         f'<svg width="350" height="120" viewBox="0 0 350 120" style="margin-top:14px"><path d="M20,60 C80,10 140,10 200,40 C250,62 300,50 330,40" stroke="#e8b294" stroke-width="40" fill="none" stroke-linecap="round"/>'
         f'<ellipse id="musculo" cx="120" cy="38" rx="80" ry="26" fill="#e07a6a" opacity="0.85"/></svg></div>')

# ---- 1 · BAÑO
L1 = RL(1)
azulejos = "".join(f'<line x1="0" y1="{y}" x2="{RW}" y2="{y}" stroke="#ffffff" stroke-width="5"/>' for y in range(1100, FLOOR, 90)) + \
           "".join(f'<line x1="{x}" y1="1100" x2="{x}" y2="{FLOOR}" stroke="#ffffff" stroke-width="5"/>' for x in range(0, RW, 90))
H.append(sala(1, f'<rect x="0" y="1100" width="{RW}" height="{FLOOR - 1100}" fill="#a9d9d1"/>' + azulejos
              + ventana(1080, 360, 240, 300, cortina="#f2b84b")
              + '<ellipse cx="300" cy="720" rx="130" ry="170" fill="#fbf6ee"/><ellipse cx="300" cy="720" rx="110" ry="150" fill="#cfe6f2"/><path d="M230,640 L300,560" stroke="#fff" stroke-width="10" opacity="0.6"/>'
              + '<rect x="190" y="1180" width="220" height="50" rx="20" fill="#fbf6ee"/><rect x="285" y="1225" width="30" height="470" fill="#e6e1d8"/><rect x="285" y="1140" width="10" height="45" fill="#9aa3b5"/>'
              + '<rect x="960" y="1330" width="520" height="370" rx="60" fill="#fbf6ee"/><rect x="980" y="1350" width="480" height="60" rx="30" fill="#cfe6f2"/>'
              + '<rect x="1000" y="300" width="12" height="1060" fill="#9aa3b5"/><path d="M1006,320 C1100,340 1140,700 1180,1320 L1006,1320 Z" fill="#f2b84b" opacity="0.8"/>'
              + '<rect x="560" y="900" width="180" height="16" rx="8" fill="#9aa3b5"/><rect x="590" y="916" width="120" height="220" rx="16" fill="#e07a5f"/>'
              + planta(1400, 1610), pared_suelo("s1", "#eaf6f3", "#d3ece6", "#e8e2d6", "#cbc3b4", rayas=False, zocalo="#ffffff")))
H.append(f'''<svg id="inodoro" style="position:absolute;left:{L1 + 640}px;top:1260px;overflow:visible" width="10" height="10">
<g id="ruedas" opacity="0"><circle cx="20" cy="440" r="26" fill="#3d405b"/><circle cx="210" cy="440" r="26" fill="#3d405b"/><circle cx="20" cy="440" r="9" fill="#9aa3b5"/><circle cx="210" cy="440" r="9" fill="#9aa3b5"/></g>
<rect x="150" y="0" width="140" height="210" rx="20" fill="#fbf6ee"/><rect x="170" y="-20" width="100" height="26" rx="10" fill="#e6e1d8"/>
<path d="M-20,210 L300,210 C300,330 230,360 170,370 L170,430 L60,430 L60,370 C0,350 -20,300 -20,210 Z" fill="#ffffff"/>
<ellipse cx="140" cy="212" rx="160" ry="26" fill="#e6e1d8"/></svg>''')

# ---- 2 · ESPACIO + LABORATORIO de la agencia espacial
L2 = RL(2)
estrellas = "".join(f'<circle cx="{random.uniform(10, 740):.0f}" cy="{random.uniform(20, 1900):.0f}" r="{random.choice([2, 2, 3, 4])}" fill="#fff" opacity="{random.uniform(0.4, 0.95):.2f}"/>' for _ in range(120))
espacio = (f'<rect x="0" y="0" width="750" height="1920" fill="url(#espacioG)"/>{estrellas}'
           '<circle cx="120" cy="1650" r="330" fill="#3f7fc4"/><path d="M-120,1520 C0,1450 120,1560 220,1480 C300,1420 380,1500 440,1560 L440,1980 L-120,1980 Z" fill="#5fae6e" opacity="0.85"/>'
           '<circle cx="120" cy="1650" r="330" fill="none" stroke="#9fd3f5" stroke-width="18" opacity="0.4"/>'
           '<circle cx="600" cy="300" r="70" fill="#e9dccb"/><circle cx="580" cy="280" r="14" fill="#cbbca8"/><circle cx="625" cy="320" r="10" fill="#cbbca8"/>')
lab = (f'<rect x="750" y="0" width="750" height="{FLOOR}" fill="#eef1f6"/><rect x="750" y="{FLOOR}" width="750" height="{1920 - FLOOR}" fill="#c9ced8"/>'
       f'<rect x="750" y="{FLOOR - 50}" width="750" height="50" fill="#ffffff"/><rect x="742" y="0" width="16" height="1920" fill="#3d405b"/>'
       '<rect x="860" y="430" width="560" height="120" rx="18" fill="#1d2b33"/><text x="1140" y="482" text-anchor="middle" font-family="Inter" font-weight="900" font-size="36" fill="#f2b84b">LABORATORIO</text>'
       '<text x="1140" y="528" text-anchor="middle" font-family="Inter" font-weight="700" font-size="28" fill="#fbf8f2">ESTUDIO DE REPOSO EN CAMA</text>'
       '<rect x="1230" y="760" width="200" height="140" rx="14" fill="#1d2b33"/><path id="ecg" d="M1245,830 L1290,830 L1305,790 L1320,870 L1335,830 L1415,830" stroke="#3fbf7f" stroke-width="6" fill="none"/>'
       '<rect x="1322" y="900" width="16" height="800" fill="#9aa3b5"/>')
H.append(f'<svg width="0" height="0" style="position:absolute"><defs><linearGradient id="espacioG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0e2c"/><stop offset="1" stop-color="#232a66"/></linearGradient></defs></svg>')
H.append(sala(2, espacio + lab, ""))
ASTRO = f'''<svg id="astro" style="position:absolute;left:{L2 + 280}px;top:640px;overflow:visible" width="10" height="10">
<rect x="-40" y="140" width="80" height="120" rx="20" fill="#cfd6e4"/><rect x="40" y="130" width="200" height="230" rx="70" fill="#f4f6fb"/>
<circle cx="140" cy="90" r="95" fill="#f4f6fb"/><ellipse cx="150" cy="95" rx="66" ry="56" fill="#1d2356"/><ellipse cx="130" cy="75" rx="22" ry="14" fill="#9fd3f5" opacity="0.7"/>
<rect x="-10" y="170" width="70" height="40" rx="20" fill="#f4f6fb" transform="rotate(-30 25 190)"/><rect x="220" y="190" width="80" height="44" rx="22" fill="#f4f6fb" transform="rotate(35 260 212)"/>
<rect x="70" y="340" width="60" height="120" rx="28" fill="#f4f6fb" transform="rotate(12 100 400)"/><rect x="150" y="340" width="60" height="120" rx="28" fill="#f4f6fb" transform="rotate(-18 180 400)"/>
<rect x="100" y="190" width="80" height="50" rx="10" fill="#e5484d"/></svg>'''
H.append(ASTRO)
H.append(f'<div id="hueso" class="card" style="left:{L2 + 60}px;top:1120px;width:300px;padding:20px 24px"><div class="card-top" style="font-size:26px">TUS HUESOS</div>'
         f'<svg width="250" height="110" viewBox="0 0 250 110"><path d="M40,40 a22,22 0 1,1 20,-25 L190,15 a22,22 0 1,1 20,25 a22,22 0 1,1 -20,25 L60,65 a22,22 0 1,1 -20,-25 Z" fill="#fbf3e6" stroke="#cbbca8" stroke-width="5"/>'
         + "".join(f'<circle class="poro" cx="{70 + (i % 6) * 22}" cy="{30 + (i // 6) * 16}" r="5" fill="#cbbca8" opacity="0"/>' for i in range(18))
         + f'</svg><div style="font:900 34px Inter;color:{BAD}">− CALCIO</div></div>')
H.append(cama_tumbado("p2", L2 + 1000, 1300, s=0.5, cm=12, beard=10))
H.append(f'<div id="pago" class="badge" style="left:{L2 + 900}px;top:860px;background:{GOOD};font-size:50px">€ TE PAGAN</div>')

# ---- 3 · CONSULTA: corazón y riñón
L3 = RL(3)
H.append(sala(3, '<rect x="170" y="420" width="1160" height="860" rx="30" fill="#2a3346"/><rect x="190" y="440" width="1120" height="820" rx="22" fill="#eaf4ff"/>'
              '<rect x="190" y="440" width="1120" height="820" rx="22" fill="url(#luzsala)" opacity="0.4"/><line x1="750" y1="470" x2="750" y2="1230" stroke="#c9d6e6" stroke-width="6"/>'
              '<text x="470" y="520" text-anchor="middle" font-family="Inter" font-weight="900" font-size="40" fill="#5a6b85">CORAZÓN</text>'
              '<text x="1030" y="520" text-anchor="middle" font-family="Inter" font-weight="900" font-size="40" fill="#5a6b85">RIÑÓN</text>'
              '<rect x="80" y="1380" width="420" height="40" rx="10" fill="#c99067"/><rect x="100" y="1420" width="24" height="280" fill="#8a5a3c"/><rect x="456" y="1420" width="24" height="280" fill="#8a5a3c"/>'
              '<rect x="1060" y="1300" width="300" height="400" rx="20" fill="#9aa3b5"/><rect x="1080" y="1320" width="260" height="120" rx="12" fill="#c9d0dc"/>'
              + planta(1420, 1610), pared_suelo("s3", "#e4ecf3", "#cdd9e6", "#b8c4d0", "#9aa7b6", rayas=False, zocalo="#ffffff")))
H.append(f'''<svg id="corazon" style="position:absolute;left:{L3 + 470}px;top:860px;overflow:visible" width="10" height="10">
<path d="M0,-120 C-60,-220 -230,-170 -200,-30 C-180,70 -60,140 0,220 C60,140 180,70 200,-30 C230,-170 60,-220 0,-120 Z" fill="#e5484d"/>
<path d="M-120,-150 C-150,-130 -170,-90 -160,-50" stroke="#ff9a90" stroke-width="16" fill="none" stroke-linecap="round" opacity="0.7"/>
<path d="M-40,-190 L-40,-260 M40,-180 L60,-250" stroke="#c2453e" stroke-width="30" stroke-linecap="round"/></svg>''')
H.append(f'''<svg id="rinon" style="position:absolute;left:{L3 + 1030}px;top:860px;overflow:visible" width="10" height="10">
<path d="M-60,-220 C80,-260 190,-140 160,10 C140,140 60,230 -40,210 C-130,190 -150,90 -90,40 C-40,0 -60,-60 -110,-80 C-170,-110 -150,-200 -60,-220 Z" fill="#b5544c"/>
<path d="M-40,-150 C40,-160 100,-90 90,10" stroke="#d27a70" stroke-width="20" fill="none" stroke-linecap="round" opacity="0.6"/>
<circle class="piedra" cx="30" cy="-40" r="20" fill="#f2e6c9" opacity="0"/><circle class="piedra" cx="70" cy="40" r="15" fill="#f2e6c9" opacity="0"/>
<circle class="piedra" cx="0" cy="90" r="24" fill="#f2e6c9" opacity="0"/><circle class="piedra" cx="-30" cy="10" r="12" fill="#f2e6c9" opacity="0"/></svg>''')

# ---- 4 · DORMITORIO, 5 años después (polvo, telarañas, platos)
L4 = RL(4)
telas = ('<path d="M0,0 L220,0 M0,0 L0,220 M0,0 L170,170 M0,60 Q60,60 60,0 M0,120 Q120,120 120,0 M0,180 Q170,170 180,0" stroke="#ffffff" stroke-width="4" fill="none" opacity="0.55"/>'
         f'<path d="M{RW},0 L{RW - 220},0 M{RW},0 L{RW},220 M{RW},0 L{RW - 170},170 M{RW},70 Q{RW - 70},70 {RW - 70},0 M{RW},140 Q{RW - 140},140 {RW - 140},0" stroke="#ffffff" stroke-width="4" fill="none" opacity="0.55"/>')
platos = "".join(f'<ellipse cx="{230 - i * 4}" cy="{1690 - i * 22}" rx="80" ry="16" fill="#fbf8f2" stroke="#cbbca8" stroke-width="3"/>' for i in range(9))
H.append(sala(4, ventana(940, 420, 330, 470, cortina="#7d8aa0") + '<g transform="rotate(-8 345 635)">' + cuadro(230, 520, 230, 230) + '</g>'
              + reloj("clk4", 640, 640) + calendario("cal4", 1290, 1010, "AÑO 5") + lampara_mesita(40)
              + f'<ellipse cx="760" cy="1800" rx="560" ry="60" fill="#8f6a5c" opacity="0.55"/>' + planta(1380, 1610, seca=True) + platos + telas
              + f'<rect x="0" y="0" width="{RW}" height="1920" fill="#7a6a58" opacity="0.13"/>',
              pared_suelo("s4", "#e6cdb6", "#d2b195", "#9c6c4c", "#7a5238")))
BED4 = (L4 + 470, 1330)
H.append(cama_tumbado("p4", *BED4, s=0.62, cm=60, beard=100))
H.append(pj_at("p4s", L4 + 1170, cm=60, beard=100))
H.append(f'<div id="bocadillo" class="card" style="left:{L4 + 760}px;top:780px;width:560px;padding:24px 30px;border-radius:40px">'
         f'<div class="card-big" style="font-size:52px;color:{GOOD};line-height:1.1">¡YA PUEDES LEVANTARTE!</div></div>')
H.append(f'''<svg id="mareo" style="position:absolute;left:{L4 + 1170}px;top:700px;overflow:visible;opacity:0" width="10" height="10">
<g id="mareo-g"><ellipse cx="0" cy="0" rx="150" ry="36" fill="none" stroke="#f2b84b" stroke-width="7" stroke-dasharray="26 18"/>
<path d="M150,0 l14,-10 4,16 Z M-150,0 l-14,10 -4,-16 Z" fill="#f2b84b"/>
<text x="-120" y="-30" font-size="44" fill="#fbf8f2">★</text><text x="90" y="40" font-size="40" fill="#fbf8f2">★</text></g></svg>''')
H.append(f'''<svg id="sangre" style="position:absolute;left:{L4 + 1330}px;top:900px;overflow:visible;opacity:0" width="10" height="10">
<path id="sangre-p" d="M0,0 L0,620" stroke="{BAD}" stroke-width="22" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>
<path d="M-40,580 L0,650 L40,580" stroke="{BAD}" stroke-width="22" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="0" cy="-30" r="24" fill="{BAD}"/></svg>''')

# ---- 5 · GIMNASIO DE REHABILITACIÓN
L5 = RL(5)
H.append(sala(5, ventana(980, 380, 360, 420, cortina="#3fbf7f")
              + '<rect x="160" y="420" width="520" height="130" rx="20" fill="#3fbf7f"/><text x="420" y="505" text-anchor="middle" font-family="Inter" font-weight="900" font-size="54" fill="#fff">REHABILITACIÓN</text>'
              + '<rect x="40" y="1300" width="120" height="400" rx="12" fill="#5a6b85"/>' + "".join(f'<rect x="56" y="{1330 + i * 90}" width="88" height="22" rx="11" fill="#e5484d"/>' for i in range(4))
              + '<rect x="1200" y="1450" width="300" height="80" fill="#c99067"/><rect x="1280" y="1370" width="220" height="80" fill="#d9a77e"/><rect x="1360" y="1290" width="140" height="80" fill="#e8bb92"/>'
              + '<rect x="0" y="1760" width="1500" height="40" fill="#5b86c4" opacity="0.6"/><circle cx="1110" cy="1600" r="95" fill="#f2b84b"/>',
              pared_suelo("s5", "#dff3ea", "#c4e6d6", "#d9b38c", "#bf966e")))
H.append(f'<svg style="position:absolute;left:{L5}px;top:0;overflow:visible" width="1" height="1">'
         '<rect x="300" y="1225" width="800" height="18" rx="9" fill="#9aa3b5" opacity="0.7"/>'
         + "".join(f'<rect x="{x}" y="1225" width="22" height="475" fill="#7c8496" opacity="0.7"/>' for x in (310, 1070)) + '</svg>')
H.append(pj_at("p5", L5 + 700, cm=60, beard=100))
H.append(f'<svg style="position:absolute;left:{L5}px;top:0;overflow:visible" width="1" height="1">'
         '<rect x="280" y="1262" width="840" height="22" rx="11" fill="#c9d0dc"/>'
         + "".join(f'<rect x="{x}" y="1262" width="26" height="440" fill="#9aa3b5"/>' for x in (290, 1090)) + '</svg>')

# separadores entre habitaciones (paredes de la «casa de muñecas»)
H.append(f'<svg style="position:absolute;left:0;top:0;overflow:visible" width="1" height="1">'
         + "".join(f'<rect x="{RL(k) - 18}" y="0" width="36" height="1920" fill="#3b3552"/>' for k in range(1, 6)) + '</svg>')

# ------------------------------------------------------------------ guion → animación (todo con P())
for pid in ("p0", "p2", "p4", "p4s", "p5"):
    vida(pid)
CAMS = {"cama0": (L0 + 660, 1150, 0.95), "cara0": (BED0[0] - 70, 1260, 1.5)}
def camk(t, nombre, dur=1.2, viaje=False):
    x, y, z = CAMS[nombre]
    cam(t, x, y, z, dur=dur, viaje=viaje)

J('tl.set("#world", {x:%.1f, y:%.1f, scale:%.2f}, 0);' % (540 - CAMS["cara0"][0] * CAMS["cara0"][2], 960 - CAMS["cara0"][1] * CAMS["cara0"][2], CAMS["cara0"][2]))
for sel in ["#escaras", "#fuerza", "#hueso", "#pago", "#bocadillo", "#p4s"]:
    J(f'tl.set("{sel}", {{opacity:0}}, 0);')

# 1 · gancho: cara en la almohada, la cámara se abre y enseña la cama
J(f'tl.fromTo("#p0-eyes", {{scaleY:0.15}}, {{scaleY:1, duration:0.35, svgOrigin:"500 742", immediateRender:false}}, 0.3);')
cam(P("tumbado") - 0.3, L0 + 620, 1200, 1.05, dur=1.6, ease="power2.inOut")
# 2 · te traen la comida
tco = P("comida")
J(f'tl.fromTo("#bandeja", {{opacity:0, x:260}}, {{opacity:1, x:0, duration:0.7, ease:"power3.out", immediateRender:false}}, {tco - 0.2:.2f});')
FX_EV.append(("whoosh", tco - 0.2))
J(f'tl.to("#p0-mouth", {{attr:{{d:"M474,814 Q500,840 526,814"}}, duration:0.3}}, {tco + 0.3:.2f});')
# 3 · vacaciones: gafas de sol
tva = P("vacaciones")
J(f'tl.fromTo("#gafas", {{opacity:0, y:-120}}, {{opacity:1, y:0, duration:0.45, ease:"bounce.out", immediateRender:false}}, {tva - 0.2:.2f});')
FX_EV.append(("pop", tva))
cam(tva - 0.3, BED0[0] + 40, 1250, 1.25, dur=0.8)
# 4 · cada dos horas: reloj que gira y flecha de la vuelta
tdh = P("dos")
J(f'tl.to("#gafas", {{opacity:0, duration:0.25}}, {tdh - 0.5:.2f}); tl.to("#p0-mouth", {{attr:{{d:"M478,816 Q500,832 522,816"}}, duration:0.3}}, {tdh - 0.5:.2f});')
cam(tdh - 0.5, L0 + 660, 1050, 0.95, dur=0.8)
J(f'tl.to("#clkm", {{rotation:720, duration:1.6, ease:"power2.inOut", svgOrigin:"640 640"}}, {tdh:.2f}); tl.to("#clkh", {{rotation:60, duration:1.6, ease:"power2.inOut", svgOrigin:"640 640"}}, {tdh:.2f});')
J(f'tl.to("#vuelta", {{opacity:1, duration:0.2}}, {P("vuelta") - 0.4:.2f}); tl.to("#vuelta-p", {{strokeDashoffset:0, duration:0.7, ease:"power2.out"}}, {P("vuelta") - 0.4:.2f});')
J(f'tl.to("#p0-rot", {{rotation:-5, duration:0.35, yoyo:true, repeat:3, ease:"sine.inOut", transformOrigin:"{BED0[0] + 200}px {BED0[1]}px"}}, {P("vuelta") - 0.1:.2f});')
FX_EV.append(("whoosh", P("vuelta")))
# 5 · escaras
tes = P("escaras")
J(f'tl.to("#vuelta", {{opacity:0, duration:0.3}}, {F(5) - 0.1:.2f});')
pop("#escaras", P("piel") - 0.1)
J(f'tl.to("#escaras .llaga", {{opacity:1, duration:0.3, stagger:0.2}}, {P("rompe"):.2f});')
J(f'tl.to("#p0-mouth", {{attr:{{d:"M482,826 Q500,812 518,826"}}, duration:0.25}}, {P("rompe"):.2f});')
# 6 · primer mes: fuerza de las piernas
tme = P("mes")
J(f'tl.to("#escaras", {{opacity:0, x:40, duration:0.3}}, {tme - 0.6:.2f});')
pop("#fuerza", tme - 0.2)
J(f'tl.fromTo("#fuerza-b", {{scaleX:1}}, {{scaleX:0.45, duration:1.4, ease:"power2.inOut", immediateRender:false}}, {P("piernas"):.2f});')
J(f'tl.to("#musculo", {{attr:{{rx:44, ry:14}}, duration:1.4, ease:"power2.inOut"}}, {P("piernas"):.2f});')
J(f'tl.to("#cal0", {{opacity:0, duration:0.15, yoyo:true, repeat:1}}, {tme:.2f}); tl.set("#cal0", {{textContent:"MES 1"}}, {tme + 0.15:.2f});')

# 7 · baño: el baño viene a ti
t = F(7)
J(f'tl.to("#fuerza", {{opacity:0, duration:0.3}}, {t:.2f});')
cam(t, L1 + 760, 1150, 0.95, dur=1.3, viaje=True)
tve = P("venir")
J(f'tl.to("#ruedas", {{opacity:1, duration:0.2}}, {tve - 0.6:.2f});')
J(f'tl.to("#inodoro", {{y:-30, duration:0.12, yoyo:true, repeat:1}}, {tve - 0.4:.2f});')
J(f'tl.to("#inodoro", {{x:-1500, duration:1.6, ease:"power2.in"}}, {tve - 0.15:.2f});')
J(f'tl.to("#inodoro", {{rotation:-4, duration:0.2, yoyo:true, repeat:5, transformOrigin:"50% 100%"}}, {tve - 0.15:.2f});')
FX_EV.append(("whoosh", tve + 0.3))

# 8 · un año: huesos como los de un astronauta (espacio)
t = F(8)
cam(t, L2 + 380, 1050, 0.95, dur=1.3, viaje=True)
J(f'tl.fromTo("#astro", {{y:-20, rotation:-6}}, {{y:30, rotation:6, duration:2.2, ease:"sine.inOut", yoyo:true, repeat:5, transformOrigin:"50% 50%", immediateRender:false}}, {t:.2f});')
pop("#hueso", P("huesos"))
J(f'tl.to("#hueso .poro", {{opacity:1, duration:0.2, stagger:0.08}}, {P("calcio"):.2f});')
# 9 · las agencias espaciales pagan a voluntarios (laboratorio)
tag = P("agencias")
cam(tag - 0.3, L2 + 1120, 1150, 0.95, dur=1.0)
pop("#pago", P("pagan"))
FX_EV.append(("pop", P("pagan")))
J(f'tl.to("#ecg", {{x:-30, duration:0.6, ease:"none", repeat:6, yoyo:true}}, {tag:.2f});')
# 10 · lo más parecido al espacio: se ven las dos mitades
cam(F(10) - 0.1, L2 + 760, 1000, 0.72, dur=1.4, ease="power2.inOut")

# 11 · corazón más pequeño (consulta)
t = F(11)
J(f'tl.to(["#hueso", "#pago"], {{opacity:0, duration:0.3}}, {t:.2f});')
cam(t, L3 + 480, 1000, 1.0, dur=1.3, viaje=True)
J(f'tl.fromTo("#corazon", {{scale:1}}, {{scale:1.08, duration:0.35, yoyo:true, repeat:9, ease:"sine.inOut", transformOrigin:"50% 50%", immediateRender:false}}, {t:.2f});')
J(f'tl.to("#corazon", {{scale:0.72, duration:1.0, ease:"power2.inOut", transformOrigin:"50% 50%"}}, {P("pequeno"):.2f});')
FX_EV.append(("golpe", P("pequeno")))
# 12 · piedras en el riñón
cam(P("calcio", 2) - 0.3, L3 + 1000, 1000, 1.0, dur=0.9)
J(f'tl.fromTo("#rinon .piedra", {{opacity:0, scale:0}}, {{opacity:1, scale:1, duration:0.35, stagger:0.18, ease:"back.out(2)", transformOrigin:"50% 50%", immediateRender:false}}, {P("piedras"):.2f});')
FX_EV.append(("pop", P("piedras")))

# 13 · cinco años después: ¡ya puedes levantarte!
t = F(13)
cam(t, L4 + 700, 1150, 0.95, dur=1.3, viaje=True)
tle = P("levantarte")
pop("#bocadillo", P("dicen"))
FX_EV.append(("pop", P("dicen")))
J(f'tl.to("#p4-eyes", {{scaleY:1.25, duration:0.2, svgOrigin:"500 742"}}, {tle:.2f});')
# 14 · de pie… y todo da vueltas
tpi = P("pie")
J(f'tl.to("#bocadillo", {{opacity:0, duration:0.3}}, {tpi - 0.5:.2f});')
J(f'tl.to("#p4-rot", {{opacity:0, duration:0.35}}, {tpi - 0.2:.2f});')
J(f'tl.fromTo("#p4s", {{opacity:0, y:160, x:-260}}, {{opacity:1, y:0, x:0, duration:0.6, ease:"power2.out", immediateRender:false}}, {tpi - 0.2:.2f});')
cam(tpi, L4 + 1000, 1150, 1.0, dur=0.8)
J(f'tl.to("#p4s", {{rotation:4, duration:0.45, yoyo:true, repeat:7, ease:"sine.inOut", transformOrigin:"50% 94%"}}, {tpi + 0.5:.2f});')
J(f'tl.to("#mareo", {{opacity:1, duration:0.3}}, {P("vueltas") - 0.3:.2f}); tl.to("#mareo-g", {{rotation:360, duration:2.0, ease:"none", repeat:2, transformOrigin:"0 0"}}, {P("vueltas") - 0.3:.2f});')
J(f'tl.to("#p4s-eyes", {{scaleY:0.4, duration:0.2, svgOrigin:"500 742"}}, {P("vueltas"):.2f});')
# 15 · la sangre baja a los pies
tsa = P("sangre")
J(f'tl.to("#sangre", {{opacity:1, duration:0.2}}, {tsa:.2f}); tl.to("#sangre-p", {{strokeDashoffset:0, duration:0.9, ease:"power2.in"}}, {tsa:.2f});')
tde = P("desmayarte")
J(f'tl.to("#p4s-up", {{scaleY:0.93, duration:0.4, ease:"power2.in", svgOrigin:"500 1290"}}, {tde - 0.1:.2f}); tl.to("#p4s-up", {{scaleY:1, duration:0.5, ease:"power2.out", svgOrigin:"500 1290"}}, {tde + 0.6:.2f});')
J(f'tl.to(["#mareo", "#sangre"], {{opacity:0, duration:0.4}}, {FE(15) + 0.1:.2f});')

# 16-17 · rehabilitación: volver a andar entre barras
t = F(16)
cam(t, L5 + 700, 1150, 0.95, dur=1.3, viaje=True)
J(f'tl.to("#p5-legs", {{x:6, duration:0.12, yoyo:true, repeat:9, ease:"sine.inOut"}}, {P("sostienen"):.2f});')
J(f'tl.to("#p5-mouth", {{attr:{{d:"M482,826 Q500,812 518,826"}}, duration:0.25}}, {P("sostienen"):.2f});')
tre = P("rehabilitacion")
caminar_lento = []
J(f'tl.fromTo("#p5", {{x:-260}}, {{x:120, duration:3.4, ease:"sine.inOut", immediateRender:false}}, {tre - 0.4:.2f});')
for k in range(8):
    tk = tre - 0.4 + k * 0.42
    pie = "legL" if k % 2 == 0 else "legR"
    J(f'tl.to("#p5-{pie}", {{y:-18, duration:0.21, yoyo:true, repeat:1, ease:"sine.inOut"}}, {tk:.2f});')
J(f'tl.set("#p5", {{x:-260}}, 0);')
J(f'tl.to("#p5-mouth", {{attr:{{d:"M474,814 Q500,840 526,814"}}, duration:0.3}}, {P("paso", 2):.2f});')
FX_EV.append(("pop", P("paso", 2)))

# 18 · BUCLE: corte limpio al dormitorio del día 1 (= fotograma 0)
tcut = P("con") - 0.1
J(f'tl.to("#dip", {{opacity:0.45, duration:0.12, ease:"power1.in"}}, {tcut - 0.12:.2f}); tl.to("#dip", {{opacity:0, duration:0.3}}, {tcut:.2f});')
x0, y0, z0 = CAMS["cara0"]
J(f'tl.set("#world", {{x:{540 - x0 * z0:.1f}, y:{960 - y0 * z0:.1f}, scale:{z0}}}, {tcut:.2f});')
J(f'tl.set("#bandeja", {{opacity:0}}, {tcut:.2f}); tl.set("#cal0", {{textContent:"DÍA 1"}}, {tcut:.2f}); tl.set(["#clkm", "#clkh"], {{rotation:0, svgOrigin:"640 640"}}, {tcut:.2f});')
J(f'tl.set("#p0-mouth", {{attr:{{d:"M478,816 Q500,832 522,816"}}}}, {tcut:.2f}); tl.set(".llaga", {{opacity:0}}, {tcut:.2f});')
J(f'tl.set("#p0-eyes", {{scaleY:0.15, svgOrigin:"500 742"}}, {DUR - 0.05:.2f});')
FX_EV.append(("whoosh", tcut))

# --- HUD: día 1 → 1 mes → 1 año → 5 años
def hud_a(t, i, k_prev, k_new, dur=0.9):
    x = HXI(i)
    J(f'tl.to("#hud-dot", {{x:{x - 60:.0f}, duration:{dur}, ease:"power3.inOut"}}, {t:.2f});')
    J(f'tl.to("#hud-fill", {{scaleX:{i / 3:.3f}, duration:{dur}, ease:"power3.inOut"}}, {t:.2f});')
    J(f'tl.to(".hud-pill", {{x:{min(x, 790):.0f}, duration:{dur}, ease:"power3.inOut"}}, {t:.2f});')
    if k_prev is not None:
        J(f'tl.to("#hp{k_prev}", {{opacity:0, y:-10, duration:0.2}}, {t:.2f});')
    J(f'tl.fromTo("#hp{k_new}", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:0.35, ease:"back.out(2)", immediateRender:false}}, {t + dur * 0.7:.2f});')
    FX_EV.append(("clic", t + dur * 0.9))
J(f'tl.set(".hud-pill", {{xPercent:-50, x:{HXI(0):.0f}, y:0}}, 0); tl.set("#hud-fill", {{scaleX:0}}, 0); tl.set("#hud-dot", {{x:0}}, 0);')
t_in = F(4) - 0.2
J(f'tl.fromTo("#hud", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:0.5, ease:"power3.out", immediateRender:false}}, {t_in:.2f});')
J(f'tl.fromTo("#hp0", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:0.35, immediateRender:false}}, {t_in + 0.2:.2f});')
hud_a(P("mes") - 0.3, 1, 0, 1)
hud_a(F(8) + 0.2, 2, 1, 2)
hud_a(F(13) + 0.2, 3, 2, 3)
J(f'tl.to("#hud", {{opacity:0, y:-30, duration:0.35, ease:"power2.in"}}, {tcut - 0.4:.2f});')
J(f'tl.set(".hud-pill", {{opacity:0}}, {tcut:.2f});')

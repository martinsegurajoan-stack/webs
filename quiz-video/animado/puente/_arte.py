# Ilustración a tinta del puente colgante (perfil). Coordenadas en px del «mundo».
import math, random
INK, PAPEL, ACENTO, TENUE = "#23201c", "#f2ede4", "#b0543a", "#8c857a"
W = 3000
WY, SY = 1160, 1470            # línea del agua, fondo marino (en el centro)
TXL, TXR, TY = 830, 2170, 300  # torres y cima
DY = 860                       # cara superior del tablero
AXL, AXR, AY = 170, 2830, 1090
MID = (TXL + TXR) / 2
rr = random.Random(21)
def ycable(x):
    if TXL <= x <= TXR:
        u = (x - MID) / ((TXR - TXL) / 2); return (DY - 22) + (TY + 18 - (DY - 22)) * u * u
    if x < TXL:
        u = (x - AXL) / (TXL - AXL); return AY + (TY + 18 - AY) * (u ** 1.15)
    u = (x - TXR) / (AXR - TXR); return (TY + 18) + (AY - (TY + 18)) * (1 - (1 - u) ** 1.15)
def ysea(x):                    # perfil del fondo marino (más hondo en el centro)
    if x < 640 or x > 2360: return WY - 30
    u = (x - MID) / (MID - 640)
    return WY + (SY - WY) * (1 - u * u) ** 0.6 + 18 * math.sin(x / 70)
DEFS = [
    '<filter id="tinta" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="4" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="2.6" xChannelSelector="R" yChannelSelector="G"/></filter>',
    f'<pattern id="rayado" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><path d="M0,0 L0,9" stroke="{INK}" stroke-width="1.6" opacity="0.55"/></pattern>',
    f'<pattern id="rayadoF" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><path d="M0,0 L0,7" stroke="{INK}" stroke-width="1.3" opacity="0.35"/></pattern>',
    f'<pattern id="cruzado" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><path d="M0,0 L0,10 M0,0 L10,0" stroke="{INK}" stroke-width="1.2" opacity="0.4"/></pattern>',
    f'<pattern id="puntos" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="3" cy="4" r="1.3" fill="{INK}" opacity="0.45"/><circle cx="10" cy="11" r="1" fill="{INK}" opacity="0.35"/></pattern>',
]
def L(d, sw=3, op=1, extra="", color=INK):
    return f'<path d="{d}" stroke="{color}" stroke-width="{sw}" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="{op}" {extra}/>'
# ---------------------------------------------------------------- terreno y mar
def orillas():
    out = []
    for s in (-1, 1):
        x0 = 0 if s < 0 else W
        edge = 640 if s < 0 else 2360
        top = WY - 30
        d = (f"M{x0 - s * 600},{top - 40} L{edge - s * 120},{top - 40} Q{edge - s * 40},{top - 36} {edge},{top} "
             f"Q{edge + s * 30},{WY + 60} {edge + s * 70},{ysea(edge + s * 70)} L{edge + s * 70},2000 L{x0 - s * 600},2000 Z")
        out.append(f'<path d="{d}" fill="{PAPEL}"/><path d="{d}" fill="url(#cruzado)" opacity="0.55"/>')
        out.append(L(f"M{x0 - s * 600},{top - 40} L{edge - s * 120},{top - 40} Q{edge - s * 40},{top - 36} {edge},{top} Q{edge + s * 30},{WY + 60} {edge + s * 70},{ysea(edge + s * 70)}", 3.4))
        # hierba y piedras en el borde
        for k in range(26):
            x = (edge - s * 140) - s * k * 22
            out.append(L(f"M{x},{top - 40} l{rr.uniform(-4, 4):.1f},{-rr.uniform(8, 18):.1f}", 1.6, 0.7))
    return "".join(out)
def fondo_marino():
    pts = [(x, ysea(x)) for x in range(600, 2401, 20)]
    d = "M" + " L".join(f"{x},{y:.1f}" for x, y in pts)
    area = d + " L2400,2000 L600,2000 Z"
    return f'<path d="{area}" fill="{PAPEL}"/><path d="{area}" fill="url(#puntos)"/>' + L(d, 3.2)
def agua():
    """Sin bloque de color: línea de agua + trazos horizontales que se espacian con la profundidad."""
    out = [L(f"M640,{WY} " + " ".join(f"Q{655 + i * 30},{WY - 5} {670 + i * 30},{WY}" for i in range(57)), 2.6)]
    g = []
    for k in range(70):
        y = WY + 14 + (k / 70) ** 1.6 * (SY - WY - 40)
        x = rr.uniform(700, 2280); ln = rr.uniform(40, 160) * (1 - k / 110)
        if ysea(x) - 12 > y and ysea(x + ln) - 12 > y:
            g.append(L(f"M{x:.0f},{y:.0f} l{ln:.0f},0", 2, 0.55 - k * 0.005))
    out.append(f'<g id="olas">{"".join(g)}</g>')
    return "".join(out)
def reflejos():
    out = []
    for x in (TXL, TXR):
        for k in range(14):
            y = WY + 10 + k * 13; w = 40 - k * 2
            out.append(L(f"M{x - w + rr.uniform(-6, 6):.0f},{y} l{2 * w * rr.uniform(0.4, 0.9):.0f},0", 2.2, 0.5 - k * 0.03))
    return f'<g id="reflejos">{"".join(out)}</g>'
# ---------------------------------------------------------------- piezas del puente
def cimiento(i, x):
    top, bot = WY - 8, ysea(x) + 90
    d = f"M{x - 78},{top} L{x + 78},{top} L{x + 84},{bot} L{x - 84},{bot} Z"
    return (f'<g id="cim{i}"><g id="cimM{i}"><path d="{d}" fill="{PAPEL}"/><path d="{d}" fill="url(#rayadoF)"/>{L(d, 3.4)}'
            + "".join(L(f"M{x - 80},{y} L{x + 80},{y}", 1.6, 0.5) for y in range(int(top) + 50, int(bot), 50)) + '</g></g>')
def torre(i, x):
    base, top = WY - 8, TY
    h = base - top
    def leg(cx):
        wb, wt = 26, 17
        d = f"M{cx - wb},{base} L{cx - wt},{top} L{cx + wt},{top} L{cx + wb},{base} Z"
        sh = f"M{cx + 2},{base} L{cx + 2},{top} L{cx + wt},{top} L{cx + wb},{base} Z"
        return (f'<path d="{d}" fill="{PAPEL}"/><path d="{sh}" fill="url(#rayado)"/>{L(d, 3.4)}'
                + "".join(L(f"M{cx - 12},{y} L{cx + 12},{y}", 1.4, 0.45) for y in range(int(top) + 40, int(base), 70)))
    out = f'<g id="torre{i}">' + leg(x - 62) + leg(x + 62)
    # travesaños (portales con arco suave)
    struts = [(top + 18, 44), (top + 150, 34), (top + 290, 30), (DY + 70, 34)]
    for k, (y, hh) in enumerate(struts):
        d = f"M{x - 44},{y} L{x + 44},{y} L{x + 44},{y + hh} Q{x},{y + hh - 14} {x - 44},{y + hh} Z"
        out += f'<g class="trav{i}"><path d="{d}" fill="{PAPEL}"/><path d="{d}" fill="url(#rayadoF)"/>{L(d, 3)}</g>'
        if k < 3:
            out += f'<path class="hueco{i}" d="M{x - 44},{y + hh} Q{x},{y + hh - 14} {x + 44},{y + hh} L{x + 44},{struts[k + 1][0]} L{x - 44},{struts[k + 1][0]} Z" fill="none" stroke="{ACENTO}" stroke-width="6" opacity="0"/>'
    out += f'<path d="M{x - 24},{top - 22} L{x + 24},{top - 22} L{x + 30},{top} L{x - 30},{top} Z" fill="{INK}"/>' + L(f"M{x - 90},{top} L{x + 90},{top}", 4)
    out += '</g>'
    return out
def cable_d():
    return "M" + " L".join(f"{x},{ycable(x):.1f}" for x in range(AXL, AXR + 1, 15))
def pendolas():
    xs = list(range(TXL + 36, TXR - 20, 36)) + list(range(AXL + 170, TXL - 20, 36)) + list(range(TXR + 36, AXR - 150, 36))
    xs.sort(key=lambda x: abs(x - MID))
    return xs
def tablero_tramo(x0, w):
    """Tramo de tablero: viga de celosía (cordones + diagonales)."""
    y0, y1 = DY, DY + 38
    d = L(f"M{x0},{y0} L{x0 + w},{y0} M{x0},{y1} L{x0 + w},{y1}", 3.2)
    diag = " ".join(f"M{x0 + k * 19},{y1} L{x0 + k * 19 + 9.5},{y0} L{x0 + k * 19 + 19},{y1}" for k in range(int(w / 19)))
    return (f'<rect x="{x0}" y="{y0}" width="{w}" height="38" fill="{PAPEL}"/>' + d + L(diag, 1.6, 0.8)
            + f'<rect class="asf" x="{x0}" y="{y0 - 5}" width="{w}" height="5" fill="{INK}" opacity="0"/>')
def anclaje(i, x):
    top = AY - 30
    d = f"M{x - 95},{WY - 70} L{x - 70},{top} L{x + 70},{top} L{x + 95},{WY - 70} Z"
    return f'<g id="anc{i}"><path d="{d}" fill="{PAPEL}"/><path d="{d}" fill="url(#rayado)"/>{L(d, 3.4)}</g>'
def barco(color=INK):
    hull = "M-190,-14 L190,-14 Q178,30 150,44 L-160,44 Q-182,28 -190,-14 Z"
    out = f'<path d="{hull}" fill="{PAPEL}"/><path d="{hull}" fill="url(#rayado)"/>' + L(hull, 3)
    out += L("M-130,-14 L-130,-86 L-70,-86 L-70,-14 M-120,-70 L-80,-70", 2.6)
    for k in range(5):
        cx = -50 + k * 44
        out += f'<rect x="{cx}" y="-52" width="38" height="38" fill="{PAPEL}"/>' + L(f"M{cx},-52 l38,0 l0,38 l-38,0 Z M{cx + 10},-52 l0,38 M{cx + 20},-52 l0,38 M{cx + 29},-52 l0,38", 2, 0.85)
    out += L("M-100,-86 L-100,-118", 2.4)
    return out
def gaviota(x, y, s=1):
    return L(f"M{x - 14 * s},{y} q{7 * s},{-8 * s} {14 * s},0 q{7 * s},{-8 * s} {14 * s},0", 2.2, 0.85)
def nube(x, y, s=1):
    return L(f"M{x},{y} q{20 * s},{-26 * s} {48 * s},{-8 * s} q{18 * s},{-30 * s} {54 * s},{-4 * s} q{28 * s},{-6 * s} {30 * s},{12 * s} L{x},{y}", 2, 0.55)

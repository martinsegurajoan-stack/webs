"""Escenarios ilustrados (SVG 1080x1920, sin personajes) para el vídeo del vago.
Cada función devuelve un <svg> completo; los elementos con id se animan desde gen.py."""
import random

def _svg(sid, body, defs=""):
    return (f'<svg class="set" id="{sid}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920" '
            f'preserveAspectRatio="xMidYMid slice"><defs>{defs}</defs>{body}</svg>')

def _lg(i, stops, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{i}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'

def _rg(i, c, o=0.8):
    return f'<radialGradient id="{i}"><stop offset="0" stop-color="{c}" stop-opacity="{o}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'

def sofa(p, c1, c2, c3, y0=1170):
    """Sofá de frente (x 100-980). c1 tela, c2 sombra, c3 cojines."""
    d = y0 - 1170
    return f'''<g id="{p}sofa" transform="translate(0,{d})">
 <ellipse cx="540" cy="1590" rx="500" ry="34" fill="#000" opacity="0.45"/>
 <rect x="150" y="1170" width="780" height="270" rx="56" fill="{c1}"/>
 <rect x="178" y="1196" width="352" height="214" rx="44" fill="{c3}"/><rect x="550" y="1196" width="352" height="214" rx="44" fill="{c3}"/>
 <path d="M200,1220 q150,-18 300,0" stroke="#fff" stroke-opacity="0.12" stroke-width="10" fill="none" stroke-linecap="round"/>
 <path d="M572,1220 q150,-18 300,0" stroke="#fff" stroke-opacity="0.12" stroke-width="10" fill="none" stroke-linecap="round"/>
 <rect x="130" y="1400" width="820" height="130" rx="34" fill="{c1}"/>
 <rect x="160" y="1362" width="378" height="96" rx="30" fill="{c3}"/><rect x="542" y="1362" width="378" height="96" rx="30" fill="{c3}"/>
 <ellipse id="{p}hueco" cx="350" cy="1398" rx="140" ry="30" fill="{c2}" opacity="0.85"/>
 <ellipse cx="350" cy="1300" rx="120" ry="70" fill="{c2}" opacity="0.35"/>
 <rect x="92" y="1290" width="122" height="262" rx="50" fill="{c1}"/><rect x="866" y="1290" width="122" height="262" rx="50" fill="{c1}"/>
 <rect x="92" y="1290" width="122" height="40" rx="20" fill="#fff" opacity="0.08"/><rect x="866" y="1290" width="122" height="40" rx="20" fill="#fff" opacity="0.08"/>
 <rect x="130" y="1500" width="820" height="56" rx="22" fill="{c2}"/>
 <rect x="170" y="1552" width="26" height="34" rx="6" fill="#1a1410"/><rect x="884" y="1552" width="26" height="34" rx="6" fill="#1a1410"/>
</g>'''

def props_sofa(p, y0=1170):
    """Bolsa de patatas, mando, latas, manta: la «guarida»."""
    d = y0 - 1170
    return f'''<g transform="translate(0,{d})">
 <g transform="translate(700,1300) rotate(-14)"><path d="M0,0 h96 l-8,120 h-80 z" fill="#f4c430"/><path d="M0,0 h96 l-4,22 h-88 z" fill="#d62828"/>
   <circle cx="48" cy="70" r="22" fill="#d62828"/><path d="M10,-6 l12,-14 l14,10 l14,-12 l16,12 l14,-10 l16,14" stroke="#e8b10f" stroke-width="6" fill="none"/></g>
 <g transform="translate(110,1262) rotate(-8)"><rect x="0" y="0" width="120" height="58" rx="28" fill="#1c1c22"/><circle cx="30" cy="29" r="10" fill="#444"/>
   <circle cx="90" cy="20" r="7" fill="#3ddc84"/><circle cx="104" cy="34" r="7" fill="#ff3b4e"/><circle cx="78" cy="36" r="7" fill="#4ea8ff"/></g>
 <path d="M866,1290 q60,-10 122,0 v190 q-30,40 -70,10 q-30,-30 -52,-40 z" fill="#b55d4c"/>
 <path d="M880,1320 h100 M880,1360 h100 M880,1400 h96" stroke="#8c3f32" stroke-width="8"/>
 <g transform="translate(560,1340)"><path d="M0,0 q40,-40 90,-10 q30,20 80,0" stroke="#e9e3d0" stroke-width="10" fill="none" opacity="0.6"/></g>
</g>'''

def suelo_basura(p, extra=False):
    cans = "".join(f'<g transform="translate({x},{y}) rotate({r})"><rect width="38" height="70" rx="8" fill="{c}"/><rect y="6" width="38" height="8" fill="#fff" opacity="0.5"/></g>'
                   for x, y, r, c in ((250, 1640, 80, "#c1121f"), (330, 1670, 0, "#2a9d8f"), (820, 1650, -70, "#c1121f"), (760, 1690, 20, "#ffb703")))
    pizza = '<g transform="translate(470,1650) rotate(-4)"><rect width="220" height="34" rx="4" fill="#e6c79c"/><rect y="0" width="220" height="8" fill="#c9a679"/><text x="110" y="27" font-family="Inter" font-weight="900" font-size="20" fill="#c1121f" text-anchor="middle">PIZZA</text></g>'
    calc = '<path d="M140,1720 q30,-30 70,-6 q20,14 40,-6" stroke="#f1f1f1" stroke-width="16" fill="none" stroke-linecap="round" opacity="0.7"/>'
    return f'<g id="{p}basura">{pizza}{cans}{calc}</g>'

def salon(sid="set_salon"):
    """Salón de tus padres, de noche: ventana, cuadro, reloj, lámpara y EL sofá."""
    p = sid + "_"
    defs = (_lg(p + "pared", [(0, "#2d2440"), (1, "#3c2e4f")]) + _lg(p + "suelo", [(0, "#4a3426"), (1, "#2a1d15")]) +
            _lg(p + "noche", [(0, "#0b1430"), (1, "#24305a")]) + _rg(p + "luz", "#ffcf7a", 0.55) + _rg(p + "tv", "#5fa8ff", 0.5))
    estrellas = "".join(f'<circle class="estrella" cx="{random.Random(k).randint(115, 395)}" cy="{random.Random(k + 50).randint(560, 860)}" r="{random.Random(k + 9).choice([1.5, 2, 2.5])}" fill="#fff"/>' for k in range(22))
    rayas = "".join(f'<rect x="{x}" y="0" width="3" height="1560" fill="#fff" opacity="0.025"/>' for x in range(0, 1080, 60))
    tablas = "".join(f'<rect x="0" y="{y}" width="1080" height="3" fill="#000" opacity="0.25"/>' for y in range(1600, 1920, 60))
    polvo = "".join(f'<circle class="polvo" cx="{random.Random(k).randint(80, 1000)}" cy="{random.Random(k + 7).randint(600, 1500)}" r="{random.Random(k + 3).choice([2, 3, 4])}" fill="#ffe7b0" opacity="0.5"/>' for k in range(26))
    telas = "".join(f'<path d="M{x0},{y0} l{dx},0" stroke="#ffffff" stroke-opacity="0.55" stroke-width="2"/>' for x0, y0, dx in ())
    arana = ('<g id="' + p + 'telarana" opacity="0.85" stroke="#e8e8f0" stroke-width="2.4" fill="none">'
             + "".join(f'<path pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="M100,1290 L{100 + 150 * c},{1290 + 150 * s}"/>'
                       for c, s in ((1, 0), (0.92, 0.38), (0.7, 0.7), (0.38, 0.92), (0, 1)))
             + "".join(f'<path pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="M{100 + r},1290 Q{100 + r * 0.8},{1290 + r * 0.3} {100 + r * 0.7},{1290 + r * 0.7} Q{100 + r * 0.3},{1290 + r * 0.8} 100,{1290 + r}"/>'
                       for r in (40, 75, 110, 140)) + '</g>')
    body = f'''<rect width="1080" height="1600" fill="url(#{p}pared)"/>{rayas}
<rect y="1560" width="1080" height="360" fill="url(#{p}suelo)"/>{tablas}
<rect y="1550" width="1080" height="18" fill="#1d1520"/>
<g><rect x="90" y="530" width="330" height="360" rx="10" fill="#1b1424"/><rect x="108" y="548" width="294" height="324" fill="url(#{p}noche)"/>{estrellas}
 <circle cx="330" cy="620" r="34" fill="#fff6d8"/><circle cx="316" cy="610" r="34" fill="#202a52"/>
 <rect x="252" y="548" width="6" height="324" fill="#1b1424"/><rect x="108" y="706" width="294" height="6" fill="#1b1424"/>
 <path d="M70,510 h80 q-20,200 10,400 h-80 z" fill="#7a3b4b"/><path d="M360,510 h80 v400 h-80 q30,-200 0,-400z" fill="#7a3b4b"/><rect x="60" y="500" width="390" height="16" rx="8" fill="#a0715a"/></g>
<g transform="translate(600,900)"><rect width="200" height="150" rx="6" fill="#a0715a"/><rect x="14" y="14" width="172" height="122" fill="#6fa8a0"/>
 <path d="M14,136 l50,-60 l40,40 l30,-30 l52,50 z" fill="#3f6b63"/><circle cx="150" cy="44" r="14" fill="#ffe7a0"/></g>
<text x="700" y="1095" font-family="Inter" font-weight="700" font-size="22" fill="#fff" opacity="0.35" text-anchor="middle">HOGAR, DULCE HOGAR</text>
<g transform="translate(910,640)"><circle r="64" fill="#efe6d8"/><circle r="64" fill="none" stroke="#a0715a" stroke-width="10"/>
 <rect id="{p}aguja1" x="-3" y="-44" width="6" height="44" rx="3" fill="#222"/><rect id="{p}aguja2" x="-2" y="-30" width="5" height="30" rx="3" fill="#c1121f"/><circle r="6" fill="#222"/></g>
<g><rect x="1000" y="900" width="10" height="660" fill="#2b2230"/><ellipse cx="1005" cy="1560" rx="50" ry="10" fill="#2b2230"/>
 <path d="M940,820 h130 l-24,90 h-82 z" fill="#f2d8a7"/><circle id="{p}lampara" cx="1005" cy="900" r="300" fill="url(#{p}luz)"/></g>
<rect id="{p}tvluz" x="0" y="0" width="1080" height="1920" fill="url(#{p}tv)" opacity="0.4"/>
<g transform="translate(540,1780)"><rect x="-300" y="-60" width="600" height="34" rx="10" fill="#5a3b2a"/><rect x="-270" y="-30" width="20" height="90" fill="#3b261a"/><rect x="250" y="-30" width="20" height="90" fill="#3b261a"/>
 <rect x="-120" y="-84" width="90" height="26" rx="8" fill="#1c1c22"/><rect x="40" y="-112" width="40" height="54" rx="8" fill="#c1121f"/><rect x="100" y="-106" width="40" height="48" rx="8" fill="#2a9d8f"/></g>
{sofa(p, "#3f6b63", "#26443f", "#4f8077")}{props_sofa(p)}{suelo_basura(p)}{arana}{polvo}'''
    return _svg(sid, body, defs)

def oficina(sid="set_oficina"):
    p = sid + "_"
    defs = (_lg(p + "cielo", [(0, "#7cb8f5"), (1, "#d6ecff")]) + _lg(p + "pared", [(0, "#cfd9e4"), (1, "#aebccb")]) +
            _lg(p + "mesa", [(0, "#d9b48a"), (1, "#b88f63")]) + _rg(p + "sol", "#ffffff", 0.8))
    r = random.Random(5); edif = ""
    for k in range(14):
        x = k * 80 - 20; h = r.randint(260, 640); c = r.choice(["#5f86b3", "#4d7299", "#7099c4", "#3f6188"])
        edif += f'<rect x="{x}" y="{1200 - h}" width="{r.randint(70, 110)}" height="{h}" fill="{c}"/>'
        for yy in range(1200 - h + 24, 1180, 40):
            for xx in range(x + 12, x + 66, 22):
                if r.random() < 0.7:
                    edif += f'<rect x="{xx}" y="{yy}" width="10" height="16" fill="#cfe6ff" opacity="0.7"/>'
    nubes = "".join(f'<g class="nube" transform="translate({x},{y})"><ellipse rx="90" ry="30" fill="#fff" opacity="0.85"/><ellipse cx="40" cy="-18" rx="56" ry="30" fill="#fff" opacity="0.85"/></g>' for x, y in ((220, 520), (760, 600), (1000, 470)))
    body = f'''<rect width="1080" height="1920" fill="url(#{p}pared)"/>
<rect x="40" y="380" width="1000" height="840" fill="url(#{p}cielo)"/><circle cx="820" cy="520" r="200" fill="url(#{p}sol)"/>{nubes}{edif}
<g fill="#e9eef3"><rect x="30" y="370" width="1020" height="22"/><rect x="30" y="1210" width="1020" height="26"/><rect x="30" y="370" width="22" height="860"/><rect x="1028" y="370" width="22" height="860"/>
 <rect x="364" y="380" width="14" height="840"/><rect x="702" y="380" width="14" height="840"/></g>
<rect x="0" y="0" width="1080" height="70" fill="#9aa9b8"/><rect x="200" y="70" width="680" height="16" rx="8" fill="#fff" opacity="0.9"/>
<g transform="translate(110,1060)"><rect x="10" y="120" width="90" height="100" rx="12" fill="#c8693f"/>
 <path d="M55,120 q-60,-80 -40,-150 q30,50 40,150 M55,120 q10,-110 50,-160 q10,80 -50,160 M55,120 q-90,-30 -90,-90 q50,20 90,90" fill="#3a8f5c"/></g>
<rect x="0" y="1380" width="1080" height="44" fill="url(#{p}mesa)"/><rect x="0" y="1424" width="1080" height="496" fill="#8a6a49"/><rect x="0" y="1424" width="1080" height="16" fill="#000" opacity="0.2"/>
<g transform="translate(330,1040)"><rect width="420" height="270" rx="16" fill="#1d2430"/><rect x="14" y="14" width="392" height="226" rx="6" fill="#0f1720"/>
 <rect x="40" y="170" width="40" height="50" fill="#3ddc84"/><rect x="100" y="140" width="40" height="80" fill="#3ddc84"/><rect x="160" y="110" width="40" height="110" fill="#3ddc84"/><rect x="220" y="80" width="40" height="140" fill="#3ddc84"/>
 <path d="M300,190 l30,-40 l30,20 l30,-60" stroke="#4ea8ff" stroke-width="6" fill="none"/><rect x="185" y="270" width="50" height="70" fill="#2a3240"/><rect x="130" y="336" width="160" height="16" rx="8" fill="#2a3240"/></g>
<rect x="330" y="1394" width="420" height="22" rx="8" fill="#e7ecf2"/>
<g transform="translate(830,1290)"><rect width="90" height="100" rx="14" fill="#fff"/><path d="M90,25 q40,0 40,30 q0,30 -40,30" stroke="#fff" stroke-width="12" fill="none"/>
 <path class="vapor" d="M25,-20 q-14,-30 0,-60 q14,-30 0,-60" stroke="#fff" stroke-width="6" fill="none" opacity="0.6"/><path class="vapor" d="M60,-20 q-14,-30 0,-60 q14,-30 0,-60" stroke="#fff" stroke-width="6" fill="none" opacity="0.6"/></g>
<g><rect x="60" y="1470" width="300" height="400" rx="10" fill="#7a5b3d"/><rect x="720" y="1470" width="300" height="400" rx="10" fill="#7a5b3d"/>
 {"".join(f'<rect x="{x}" y="{y}" width="260" height="110" rx="8" fill="#8f6c49"/><rect x="{x + 100}" y="{y + 48}" width="60" height="12" rx="6" fill="#e0c9a6"/>' for x in (80, 740) for y in (1490, 1620, 1750))}
 <rect x="360" y="1440" width="360" height="480" fill="#000" opacity="0.18"/></g>
<g transform="translate(560,1360) rotate(4)"><rect width="150" height="22" rx="4" fill="#fff"/></g>
<g transform="translate(120,1300) rotate(-6)"><rect width="170" height="80" rx="4" fill="#fffef6"/><text x="85" y="30" font-family="Inter" font-weight="900" font-size="20" fill="#222" text-anchor="middle">CONTRATO</text><path d="M30,60 q20,-20 40,0 t40,0 t30,-6" stroke="#1d4ed8" stroke-width="4" fill="none"/></g>
<g transform="translate(110,1330)"><rect width="190" height="52" rx="6" fill="#283447"/><text x="95" y="34" font-family="Inter" font-size="22" font-weight="800" fill="#fff" text-anchor="middle">TU PUESTO</text></g>
<g id="{p}globos">{"".join(f'<g transform="translate({x},{y})"><ellipse rx="44" ry="54" fill="{c}"/><path d="M0,54 q-10,60 6,140" stroke="#fff" stroke-width="2" fill="none" opacity="0.7"/></g>' for x, y, c in ((90, 760, "#ef476f"), (170, 700, "#ffd166"), (950, 740, "#06d6a0"), (1010, 800, "#4ea8ff")))}</g>'''
    return _svg(sid, body, defs)

def calle(sid="set_calle"):
    p = sid + "_"
    defs = _lg(p + "cielo", [(0, "#2b2350"), (0.55, "#9b4f8a"), (1, "#ff9a5a")]) + _rg(p + "sol", "#ffd27a", 0.9) + _rg(p + "freno", "#ff2a2a", 0.9)
    r = random.Random(8); edif = ""
    for capa, (base, col, win) in enumerate((("1200", "#3a2d5c", "#ffcf7a"), ("1300", "#241c3d", "#ffd98f"))):
        x = -30
        while x < 1100:
            w = r.randint(90, 160); h = r.randint(300, 700) - capa * 120
            edif += f'<rect x="{x}" y="{int(base) - h}" width="{w}" height="{h + 10}" fill="{col}"/>'
            for yy in range(int(base) - h + 30, int(base) - 20, 46):
                for xx in range(x + 14, x + w - 20, 30):
                    if r.random() < 0.35:
                        edif += f'<rect x="{xx}" y="{yy}" width="12" height="18" fill="{win}" opacity="0.8"/>'
            x += w + r.randint(4, 20)
    def coche(x, y, s, c):
        return (f'<g class="auto" transform="translate({x},{y}) scale({s})"><ellipse cx="110" cy="92" rx="120" ry="12" fill="#000" opacity="0.4"/>'
                f'<path d="M0,60 q0,-24 26,-26 l40,-30 h90 l40,30 q30,2 30,26 v22 h-226 z" fill="{c}"/><path d="M72,10 h36 v26 h-58 z M114,10 h34 l28,26 h-62 z" fill="#a9d6ff" opacity="0.8"/>'
                f'<circle cx="52" cy="84" r="22" fill="#111"/><circle cx="52" cy="84" r="9" fill="#777"/><circle cx="176" cy="84" r="22" fill="#111"/><circle cx="176" cy="84" r="9" fill="#777"/>'
                f'<rect x="-4" y="50" width="14" height="14" rx="4" fill="#ff2a2a"/><circle class="freno" cx="2" cy="57" r="40" fill="url(#{p}freno)"/></g>')
    autos = ""
    for fila, (y, s, cols) in enumerate(((1330, 0.7, ["#e63946", "#457b9d", "#f1faee", "#ffb703", "#8d99ae", "#2a9d8f"]), (1500, 0.95, ["#ffb703", "#e76f51", "#264653", "#e9c46a", "#e63946"]), (1720, 1.25, ["#3a86ff", "#f1faee", "#e63946", "#8338ec"]))):
        for k, c in enumerate(cols):
            autos += coche(-60 + k * int(240 * s) + fila * 40, y - 90 * s, s, c)
    body = f'''<rect width="1080" height="1300" fill="url(#{p}cielo)"/><circle cx="540" cy="1150" r="420" fill="url(#{p}sol)"/><circle cx="540" cy="1180" r="120" fill="#ffd27a"/>{edif}
<rect y="1290" width="1080" height="630" fill="#2b2b33"/><rect y="1290" width="1080" height="14" fill="#55556a"/>
{"".join(f'<rect x="{x}" y="{y}" width="70" height="8" fill="#e9e9f0" opacity="0.6"/>' for y in (1420, 1610) for x in range(20, 1080, 140))}
<g transform="translate(980,760)"><rect x="-8" y="140" width="16" height="560" fill="#1c1c22"/><rect x="-36" y="0" width="72" height="170" rx="16" fill="#1c1c22"/>
 <circle cx="0" cy="34" r="22" fill="#ff2a2a"/><circle cx="0" cy="34" r="60" fill="url(#{p}freno)"/><circle cx="0" cy="86" r="22" fill="#4a3a1a"/><circle cx="0" cy="138" r="22" fill="#1a3a22"/></g>
<g id="{p}autos">{autos}</g>'''
    return _svg(sid, body, defs)

def piso(sid="set_piso"):
    p = sid + "_"
    defs = (_lg(p + "pared", [(0, "#1f3346"), (1, "#28435a")]) + _lg(p + "cielo", [(0, "#ffb38a"), (0.6, "#ff7e8a"), (1, "#7a5ca8")]) +
            _lg(p + "suelo", [(0, "#a07a54"), (1, "#5c4128")]) + _rg(p + "luz", "#ffdca8", 0.5))
    r = random.Random(11); sky = ""
    x = 130
    while x < 960:
        w = r.randint(50, 110); h = r.randint(120, 380)
        sky += f'<rect x="{x}" y="{1120 - h}" width="{w}" height="{h}" fill="#3b2e5a" opacity="0.85"/>'
        x += w + 6
    libros = "".join(f'<rect x="{830 + k * 26}" y="{y - h}" width="22" height="{h}" fill="{c}"/>' for y in (900, 1060) for k, (h, c) in enumerate(((90, "#e76f51"), (110, "#2a9d8f"), (80, "#e9c46a"), (100, "#f4a261"), (96, "#457b9d"))))
    body = f'''<rect width="1080" height="1920" fill="url(#{p}pared)"/>
<rect x="110" y="420" width="660" height="720" rx="8" fill="url(#{p}cielo)"/><circle cx="560" cy="980" r="90" fill="#ffe0a0"/>{sky}
<g fill="#e7ecf2"><rect x="100" y="410" width="680" height="18"/><rect x="100" y="1132" width="680" height="22"/><rect x="100" y="410" width="18" height="740"/><rect x="762" y="410" width="18" height="740"/><rect x="432" y="420" width="12" height="720"/></g>
<g><rect x="810" y="780" width="170" height="14" fill="#c9a26e"/><rect x="810" y="940" width="170" height="14" fill="#c9a26e"/>{libros}</g>
<rect y="1500" width="1080" height="420" fill="url(#{p}suelo)"/><rect y="1490" width="1080" height="16" fill="#e7ecf2"/>
<g transform="translate(70,1160)"><rect x="20" y="230" width="110" height="120" rx="14" fill="#e7ecf2"/>
 <path d="M75,230 q-100,-120 -60,-260 q40,90 60,260 M75,230 q0,-200 80,-280 q20,140 -80,280 M75,230 q-140,-60 -130,-170 q80,40 130,170" fill="#2f9e64"/></g>
<g transform="translate(980,1000)"><rect x="-6" y="0" width="12" height="500" fill="#d8dde3"/><path d="M-70,-10 h140 l-30,-80 h-80 z" fill="#f6e3c0"/><circle cx="0" cy="-20" r="320" fill="url(#{p}luz)"/></g>
<g transform="translate(420,1560)"><rect width="260" height="110" rx="10" fill="#f4f4f4"/><rect width="260" height="26" rx="6" fill="#ff6b35"/><text x="130" y="80" font-family="Inter" font-weight="900" font-size="34" fill="#222" text-anchor="middle">NUEVAS</text></g>
<g transform="translate(860,620)"><rect x="-4" width="110" height="10" rx="5" fill="#c9a26e"/><path d="M20,10 v24 M50,10 v24 M80,10 v24" stroke="#888" stroke-width="4"/>
 <g transform="translate(18,40)"><circle r="12" fill="none" stroke="#ffd166" stroke-width="5"/><rect x="-4" y="10" width="8" height="34" fill="#ffd166"/></g>
 <g transform="translate(48,40)"><circle r="12" fill="none" stroke="#c0c6cc" stroke-width="5"/><rect x="-4" y="10" width="8" height="30" fill="#c0c6cc"/></g></g>
<text x="921" y="700" font-family="Inter" font-weight="800" font-size="20" fill="#fff" opacity="0.6" text-anchor="middle">TUS LLAVES</text>'''
    return _svg(sid, body, defs)

def guarida(sid="set_guarida"):
    """Vuelta al sofá: vista desde detrás del sofá hacia la tele gigante, luces LED, latas y pizzas que se acumulan."""
    p = sid + "_"
    defs = (_lg(p + "pared", [(0, "#140a24"), (1, "#22103a")]) + _rg(p + "led", "#ff2e88", 0.7) + _rg(p + "led2", "#2ee6ff", 0.5) +
            _lg(p + "pant", [(0, "#ff2e88"), (0.5, "#ff7a00"), (0.51, "#2b0a3d"), (1, "#12001f")]) + _lg(p + "sofa", [(0, "#3a2050"), (1, "#160b22")]))
    pilas = "".join(f'<g transform="translate(850,{1360 - k * 36}) rotate({(-1) ** k * 3})"><g class="caja"><rect width="200" height="36" rx="4" fill="#e6c79c"/><rect width="200" height="8" fill="#c9a679"/><text x="100" y="29" font-family="Inter" font-weight="900" font-size="18" fill="#c1121f" text-anchor="middle">PIZZA</text></g></g>' for k in range(7))
    latas = "".join(f'<g transform="translate({70 + (k % 5) * 46},{1325 - (k // 5) * 72})"><g class="lata"><rect width="38" height="70" rx="8" fill="{c}"/><rect y="6" width="38" height="8" fill="#fff" opacity="0.5"/></g></g>' for k, c in enumerate(["#c1121f", "#2ee6ff", "#c1121f", "#9bff3a", "#c1121f", "#2ee6ff", "#c1121f", "#9bff3a", "#c1121f", "#2ee6ff"]))
    grid = "".join(f'<path d="M{540 + (x - 540) * 0.3},850 L{x},1090" stroke="#ff2e88" stroke-width="2" opacity="0.6"/>' for x in range(100, 1000, 70))
    grid += "".join(f'<rect x="110" y="{y}" width="860" height="2" fill="#ff2e88" opacity="0.6"/>' for y in (880, 920, 970, 1030))
    body = f'''<rect width="1080" height="1920" fill="url(#{p}pared)"/>
<circle cx="540" cy="830" r="640" fill="url(#{p}led)"/><circle cx="150" cy="1300" r="380" fill="url(#{p}led2)"/>
<rect x="80" y="560" width="920" height="560" rx="18" fill="#050507"/>
<g id="{p}pantalla"><rect x="110" y="590" width="860" height="500" fill="url(#{p}pant)"/>
 {"".join(f'<rect x="{540 - w}" y="{y}" width="{2 * w}" height="16" fill="#ffe066"/>' for y, w in ((640, 70), (668, 120), (696, 150), (724, 168), (752, 176), (780, 180), (808, 176), (836, 168)))}{grid}</g>
<rect id="{p}brillo" x="110" y="590" width="860" height="500" fill="#fff" opacity="0"/>
<rect x="400" y="1120" width="280" height="22" rx="10" fill="#0a0a0d"/>
<rect x="60" y="1150" width="960" height="46" rx="8" fill="#2a1a36"/><rect x="60" y="1150" width="960" height="6" fill="#ff2e88" opacity="0.8"/>
<g transform="translate(120,1090)"><rect width="140" height="60" rx="8" fill="#0d0d12"/><rect x="10" y="20" width="120" height="6" rx="3" fill="#2ee6ff"/></g>
<g transform="translate(820,1080)"><rect width="70" height="70" rx="8" fill="#0d0d12"/><circle cx="35" cy="35" r="16" fill="#9bff3a" opacity="0.8"/></g>
{latas}{pilas}
<rect x="0" y="1395" width="1080" height="30" fill="#ff2e88" opacity="0.12"/>
<path d="M-60,1520 q0,-110 120,-110 h300 q60,0 80,40 q20,-40 80,-40 h80 q60,0 80,40 q20,-40 80,-40 h300 q120,0 120,110 v400 h-1240 z" fill="url(#{p}sofa)"/>
<path d="M60,1412 h300 q60,0 80,40 q20,-40 80,-40 h80 q60,0 80,40 q20,-40 80,-40 h300" stroke="#ff2e88" stroke-width="5" fill="none" opacity="0.8"/>
<path d="M440,1460 v460 M640,1460 v460" stroke="#0b0512" stroke-width="6" opacity="0.7"/>
<path d="M700,1440 q120,-20 260,10 l-20,200 q-120,30 -230,-10 z" fill="#5b2b6e" opacity="0.9"/><path d="M720,1490 h220 M716,1540 h220 M712,1590 h220" stroke="#3a1748" stroke-width="8"/>

<g transform="translate(470,1420) rotate(-6)"><rect width="150" height="70" rx="34" fill="#141418"/><circle cx="40" cy="35" r="12" fill="#333"/><circle cx="110" cy="24" r="8" fill="#9bff3a"/><circle cx="126" cy="42" r="8" fill="#ff2e88"/><circle cx="96" cy="44" r="8" fill="#2ee6ff"/></g>
<g transform="translate(1200,1600)"><g id="{p}plato"><ellipse cx="0" cy="40" rx="130" ry="36" fill="#f4f4f4"/><ellipse cx="0" cy="30" rx="90" ry="24" fill="#e9c46a"/><path d="M-60,26 q30,-26 60,-6 q30,-26 60,0" stroke="#c1121f" stroke-width="10" fill="none"/><text x="0" y="-30" font-family="Inter" font-weight="800" font-size="28" fill="#fff" text-anchor="middle">de mamá ❤</text></g></g>'''
    return _svg(sid, body, defs)

def ciudad(sid="set_ciudad"):
    p = sid + "_"
    defs = _lg(p + "cielo", [(0, "#060a1e"), (1, "#1c2550")]) + _rg(p + "halo", "#ffcf7a", 0.35)
    r = random.Random(21); edif = ""; x = -20
    while x < 1100:
        w = r.randint(70, 150); h = r.randint(500, 1150)
        edif += f'<rect x="{x}" y="{1600 - h}" width="{w}" height="{h + 400}" fill="{r.choice(["#121a36", "#18224a", "#0f1630"])}"/>'
        for yy in range(1600 - h + 26, 1580, 34):
            for xx in range(x + 10, x + w - 14, 22):
                if r.random() < 0.42:
                    edif += f'<rect class="ven" x="{xx}" y="{yy}" width="10" height="16" fill="{r.choice(["#ffcf7a", "#ffe6a8", "#9fd8ff"])}" opacity="{r.choice([0.5, 0.8, 1])}"/>'
        x += w + r.randint(2, 14)
    est = "".join(f'<circle class="estrella" cx="{r.randint(0, 1080)}" cy="{r.randint(0, 600)}" r="{r.choice([1.5, 2, 2.5])}" fill="#fff"/>' for _ in range(60))
    body = f'''<rect width="1080" height="1920" fill="url(#{p}cielo)"/>{est}<circle cx="800" cy="380" r="60" fill="#fff6d8"/><circle cx="800" cy="380" r="200" fill="url(#{p}halo)"/>
{edif}<rect y="1600" width="1080" height="320" fill="#070b18"/>'''
    return _svg(sid, body, defs)

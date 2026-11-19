# ---------------------------------------------------------------- ESCENAS «del tamaño de una hormiga» (todo ~580 veces más grande)
ZW = 1700
def ZL(k):
    return k * ZW

def zona(k, cuerpo, w=ZW, h=1920, top=0):
    return (f'<svg style="position:absolute;left:{ZL(k)}px;top:{top}px;overflow:visible" width="{w}" height="{h}" viewBox="0 {top} {w} {h}">{cuerpo}</svg>')

def caminar(pid, t, desde=-420, dur=1.3, pasos=4):
    J(f'tl.fromTo("#{pid}", {{x:{desde}}}, {{x:0, duration:{dur}, ease:"power1.out", immediateRender:false}}, {t:.2f});')
    for k in range(pasos):
        tk = t + k * dur / pasos
        pie = "legL" if k % 2 == 0 else "legR"
        J(f'tl.to("#{pid}-{pie}", {{y:-26, duration:{dur / pasos / 2:.3f}, yoyo:true, repeat:1, ease:"sine.inOut"}}, {tk:.2f});')
        J(f'tl.to("#{pid}-up", {{y:-8, duration:{dur / pasos / 2:.3f}, yoyo:true, repeat:1, ease:"sine.inOut"}}, {tk:.2f});')

def brazo(pid, lado, rot, t, hold, ida=0.35):
    org = "356 985" if lado == "L" else "644 985"
    J(f'tl.to("#{pid}-arm{lado}g", {{rotation:{rot}, duration:{ida}, ease:"back.out(1.4)", svgOrigin:"{org}"}}, {t:.2f});')
    J(f'tl.to("#{pid}-arm{lado}g", {{rotation:0, duration:0.45, ease:"power2.inOut", svgOrigin:"{org}"}}, {t + hold:.2f});')

def acaro(aid, x, y, s=1.0):
    patas = "".join(f'<path d="M{dx * 40},{10 + abs(dx) * 4} q{dx * 40},-30 {dx * 70},30" stroke="#8a7a66" stroke-width="9" fill="none" stroke-linecap="round"/>'
                    for dx in (-1, -0.6, 0.6, 1))
    pelos = "".join(f'<path d="M{random.uniform(-70, 70):.0f},{random.uniform(-60, 10):.0f} l{random.uniform(-14, 14):.0f},-22" stroke="#b9a88f" stroke-width="4" stroke-linecap="round"/>' for _ in range(14))
    return (f'<svg id="{aid}" style="position:absolute;left:{x}px;top:{y}px;overflow:visible" width="10" height="10"><g transform="scale({s})">'
            f'<g class="patas">{patas}</g><ellipse cx="0" cy="-10" rx="90" ry="70" fill="#d9cbb3"/><ellipse cx="-20" cy="-35" rx="40" ry="22" fill="#efe4d0"/>{pelos}'
            f'<circle cx="-28" cy="-6" r="9" fill="#1d1b26"/><circle cx="22" cy="-6" r="9" fill="#1d1b26"/></g></svg>')

DEFS2 = ('<svg width="0" height="0" style="position:absolute"><defs>'
         '<linearGradient id="sabana" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f7fc"/><stop offset="1" stop-color="#c9d6ea"/></linearGradient>'
         '<linearGradient id="madera" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c58a5c"/><stop offset="1" stop-color="#8a5a3c"/></linearGradient>'
         '<linearGradient id="nocheG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1d2356"/><stop offset="1" stop-color="#3b3f7a"/></linearGradient>'
         '<radialGradient id="gotaG" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#ffffff" stop-opacity="0.75"/><stop offset="0.4" stop-color="#bfe6ff" stop-opacity="0.45"/><stop offset="1" stop-color="#5aa9e6" stop-opacity="0.55"/></radialGradient>'
         '<radialGradient id="migaG" cx="0.4" cy="0.35" r="0.8"><stop offset="0" stop-color="#f7d79a"/><stop offset="1" stop-color="#c58a3c"/></radialGradient>'
         '</defs></svg>')
H.append(DEFS2)

# ---- Z0 · SÁBANAS (despertador gigante al fondo)
dunas = "".join(f'<path d="M-100,{y} C300,{y - 90} 600,{y + 60} 900,{y - 40} C1200,{y - 120} 1500,{y + 40} 1800,{y - 30} L1800,2300 L-100,2300 Z" fill="url(#sabana)" opacity="{op}"/>'
                for y, op in ((1450, 0.7), (1600, 0.85), (1720, 1)))
H.append(zona(0, '<rect x="-100" y="0" width="1900" height="1920" fill="#f6dcc6"/>'
              '<rect x="-100" y="0" width="1900" height="1920" fill="url(#luzsala)" opacity="0.6"/>'
              # almohada gigante al fondo
              '<path d="M-150,1250 C-100,850 300,760 800,790 C1300,820 1700,900 1850,1280 Z" fill="#ffffff" opacity="0.95"/><path d="M-150,1250 C300,1180 1300,1180 1850,1280" stroke="#d9e2ef" stroke-width="18" fill="none"/>'
              # despertador gigante (las 8 de la mañana)
              '<circle cx="1330" cy="430" r="330" fill="#e5484d"/><circle cx="1330" cy="430" r="275" fill="#fbf8f2"/>'
              + "".join(f'<line x1="{1330 + 240 * math.cos(a * math.pi / 6):.0f}" y1="{430 + 240 * math.sin(a * math.pi / 6):.0f}" x2="{1330 + 210 * math.cos(a * math.pi / 6):.0f}" y2="{430 + 210 * math.sin(a * math.pi / 6):.0f}" stroke="#3d405b" stroke-width="12"/>' for a in range(12))
              + '<line x1="1330" y1="430" x2="1196" y2="507" stroke="#1d2b33" stroke-width="22" stroke-linecap="round"/><line x1="1330" y1="430" x2="1330" y2="210" stroke="#1d2b33" stroke-width="14" stroke-linecap="round"/>'
              '<circle cx="1110" cy="120" r="80" fill="#e5484d"/><circle cx="1550" cy="120" r="80" fill="#e5484d"/>' + dunas))
H.append(pj_at("p0", ZL(0) + 650, cm=7))
# regla gigante: 1 mm = 370 px → mides 3 mm
regla = "".join(f'<line x1="0" y1="{-k * 370:.0f}" x2="{70 if k == int(k) else 38}" y2="{-k * 370:.0f}" stroke="#3a3324" stroke-width="{7 if k == int(k) else 4}"/>' for k in [i / 2 for i in range(0, 7)])
regla += "".join(f'<text x="86" y="{-k * 370 + 14:.0f}" font-family="Inter" font-weight="900" font-size="46" fill="#3a3324">{k} mm</text>' for k in range(4))
H.append(f'<svg id="regla" style="position:absolute;left:{ZL(0) + 920}px;top:1700px;overflow:visible" width="10" height="10">'
         f'<rect x="0" y="-1180" width="230" height="1200" rx="14" fill="#f2d27a"/>{regla}</svg>')

# ---- Z1 · PASILLO (rendijas del parqué como cañones, la puerta de la cocina a lo lejos)
H.append(zona(1, '<rect x="0" y="0" width="1700" height="1920" fill="#e9d8c4"/>'
              '<rect x="0" y="0" width="1700" height="1920" fill="url(#luzsala)" opacity="0.5"/>'
              # puerta de la cocina, enorme y lejos, con luz
              '<rect x="980" y="120" width="560" height="1300" fill="#fbf6ee"/><rect x="1020" y="160" width="480" height="1260" fill="#fff4cf"/>'
              '<rect x="1060" y="200" width="400" height="300" fill="#ffe9a8" opacity="0.8"/><circle cx="1260" cy="760" r="20" fill="#e2c27a"/>'
              # suelo de parqué: tablas y rendijas
              '<rect x="0" y="1420" width="1700" height="900" fill="url(#madera)"/>'
              + "".join(f'<path d="M0,{y} L1700,{y + 30}" stroke="#5e3a26" stroke-width="{w}" opacity="0.8"/>' for y, w in ((1500, 10), (1610, 14), (1760, 26)))
              + '<path d="M300,1420 L260,1920" stroke="#5e3a26" stroke-width="12" opacity="0.6"/><path d="M1200,1420 L1260,1920" stroke="#5e3a26" stroke-width="12" opacity="0.6"/>'
              # cartel de distancia
              '<rect x="120" y="1080" width="24" height="340" fill="#8a5a3c"/><rect x="40" y="1000" width="430" height="110" rx="16" fill="#3d405b"/>'
              '<text x="255" y="1072" text-anchor="middle" font-family="Inter" font-weight="900" font-size="54" fill="#f2b84b">COCINA · 5,8 km</text>'
              # bolas de polvo
              + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 0.7:.0f}" fill="#cfc6b8" opacity="0.85"/>' for x, y, r in ((560, 1380, 120), (1420, 1460, 90), (820, 1330, 70)))))
H.append(pj_at("p1", ZL(1) + 650, cm=7))
H.append(acaro("acaro1", ZL(1) + 1250, 1600, 1.2))
H.append(acaro("acaro2", ZL(1) + 300, 1640, 0.9))

# ---- Z2 · LA MESA (columna vertical: encima el grano de arroz, abajo el suelo)
H.append(zona(2, '<rect x="0" y="-200" width="1700" height="4400" fill="#efe2d0"/>'
              '<rect x="0" y="-200" width="1700" height="4400" fill="url(#luzsala)" opacity="0.5"/>'
              '<rect x="0" y="1700" width="1250" height="90" fill="url(#madera)"/><rect x="0" y="1690" width="1250" height="20" fill="#d9a77e"/>'
              '<rect x="1000" y="1790" width="160" height="2010" fill="#a8714c"/><rect x="1000" y="1790" width="40" height="2010" fill="#c58a5c"/>'
              '<rect x="-100" y="3800" width="1900" height="400" fill="#9c6c4c"/>'
              # terrón de azúcar
              '<rect x="80" y="1150" width="520" height="550" rx="30" fill="#ffffff"/><rect x="80" y="1150" width="520" height="80" rx="30" fill="#eef3fb"/>'
              + "".join(f'<rect x="{x}" y="{y}" width="60" height="60" fill="#e7edf7"/>' for x, y in ((150, 1300), (380, 1420), (260, 1560), (470, 1270)))
              + '', h=4400, top=-200))
H.append(pj_at("p2", ZL(2) + 850, cm=7))
H.append(f'<svg id="arroz" style="position:absolute;left:{ZL(2) + 850}px;top:1700px;overflow:visible" width="10" height="10">'
         '<ellipse cx="0" cy="-180" rx="330" ry="110" fill="#fbf8f0"/><ellipse cx="-60" cy="-215" rx="200" ry="40" fill="#ffffff"/><path d="M-300,-170 C-150,-140 150,-140 300,-170" stroke="#e8e0cc" stroke-width="10" fill="none"/></svg>')
H.append(f'<svg id="aire" style="position:absolute;left:{ZL(2) + 1350}px;top:2400px;overflow:visible;opacity:0" width="10" height="10">'
         + "".join(f'<path d="M{dx},0 L{dx},-220" stroke="#ffffff" stroke-width="10" stroke-linecap="round" stroke-dasharray="40 30" opacity="0.8"/>' for dx in (-160, -60, 60, 160)) + '</svg>')

# ---- Z3 · SUELO DE LA COCINA (miga de pan gigante, granos de azúcar)
baldosas = "".join(f'<rect x="{x}" y="1420" width="850" height="900" fill="{c}"/>' for x, c in ((0, "#f1ece2"), (850, "#e3dccd")))
H.append(zona(3, '<rect x="0" y="0" width="1700" height="1420" fill="#dfe7ee"/>'
              '<rect x="0" y="0" width="1700" height="1420" fill="url(#luzsala)" opacity="0.5"/>'
              '<rect x="0" y="980" width="1700" height="440" fill="#fbf8f2"/><rect x="0" y="980" width="1700" height="30" fill="#c9d0dc"/>'
              '<rect x="200" y="1300" width="160" height="120" rx="20" fill="#7c8496"/><rect x="1300" y="1300" width="160" height="120" rx="20" fill="#7c8496"/>'
              + baldosas + '<rect x="840" y="1420" width="20" height="900" fill="#c9bfae"/>'
              + "".join(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="10" fill="#ffffff" opacity="0.95" transform="rotate({r} {x + s / 2} {y + s / 2})"/>' for x, y, s, r in ((120, 1620, 110, 12), (1450, 1660, 90, -18), (1300, 1560, 70, 30)))))
H.append(f'<svg id="miga" style="position:absolute;left:{ZL(3) + 1060}px;top:1720px;overflow:visible" width="10" height="10">'
         '<path d="M-330,0 C-360,-260 -200,-470 20,-480 C260,-490 380,-300 350,-80 L330,0 Z" fill="url(#migaG)"/>'
         + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 0.7:.0f}" fill="#b37a34" opacity="0.6"/>' for x, y, r in ((-150, -300, 40), (60, -380, 30), (180, -200, 46), (-60, -150, 34), (-230, -90, 26), (250, -330, 22)))
         + '</svg>')
H.append(f'<svg id="vaho" style="position:absolute;left:{ZL(3) + 560}px;top:700px;overflow:visible;opacity:0" width="10" height="10">'
         + "".join(f'<circle class="vh" cx="{30 + i * 40}" cy="{-i * 35}" r="{26 + i * 8}" fill="#ffffff" opacity="0.7"/>' for i in range(3)) + '</svg>')
H.append(f'<div id="termo" class="card" style="left:{ZL(3) + 80}px;top:760px;width:300px;padding:20px 24px"><div class="card-top" style="font-size:26px">TU CUERPO</div>'
         f'<div style="display:flex;align-items:center;gap:16px;margin-top:10px"><svg width="60" height="150" viewBox="0 0 60 150"><rect x="18" y="0" width="24" height="110" rx="12" fill="#e6edf5"/>'
         f'<rect id="mercurio" x="22" y="10" width="16" height="100" rx="8" fill="{BAD}"/><circle cx="30" cy="122" r="26" fill="{BAD}"/></svg>'
         f'<div style="font:900 40px Inter;color:#5aa9e6;line-height:1.1">PIERDE<br>CALOR</div></div></div>')
H.append(pj_at("p3", ZL(3) + 600, cm=7))

# ---- Z4 · ENCIMERA Y GRIFO (la gota que atrapa)
H.append(zona(4, '<rect x="0" y="0" width="1700" height="1920" fill="#dfe9f0"/>'
              '<rect x="0" y="0" width="1700" height="1920" fill="url(#luzsala)" opacity="0.5"/>'
              # grifo gigante arriba
              '<rect x="560" y="-200" width="260" height="560" rx="40" fill="#b9c3cf"/><path d="M560,320 C560,520 760,560 980,560 L980,700 C700,700 420,640 420,320 Z" fill="#c9d3df"/>'
              '<rect x="940" y="520" width="120" height="200" rx="20" fill="#9aa7b6"/>'
              # encimera de mármol
              '<rect x="-100" y="1700" width="1900" height="500" fill="#f4f1ec"/>'
              + "".join(f'<path d="M{x},1720 C{x + 120},1800 {x + 60},1900 {x + 200},2000" stroke="#c9c2b6" stroke-width="5" fill="none"/>' for x in (100, 700, 1300))))
H.append(pj_at("p4", ZL(4) + 1000, cm=7))
H.append(f'<svg id="gota" style="position:absolute;left:{ZL(4) + 1000}px;top:700px;overflow:visible" width="10" height="10">'
         '<g id="gota-g"><path d="M0,-150 C80,-40 150,80 150,170 C150,260 80,320 0,320 C-80,320 -150,260 -150,170 C-150,80 -80,-40 0,-150 Z" fill="url(#gotaG)" stroke="#9fd3f5" stroke-width="6"/>'
         '<ellipse cx="-55" cy="120" rx="30" ry="50" fill="#ffffff" opacity="0.7"/></g></svg>')
H.append(f'<svg id="charco" style="position:absolute;left:{ZL(4) + 1000}px;top:1700px;overflow:visible;opacity:0" width="10" height="10">'
         '<path d="M-480,0 C-480,-760 -300,-1150 0,-1150 C300,-1150 480,-760 480,0 Z" fill="url(#gotaG)" stroke="#9fd3f5" stroke-width="8"/>'
         '<ellipse cx="-230" cy="-850" rx="70" ry="130" fill="#ffffff" opacity="0.6"/></svg>')

# ---- Z5 · SALÓN: alfombra, el gato gigante y el sofá
fibras = "".join(f'<path d="M{x},{1920} C{x + random.uniform(-20, 20):.0f},{1800} {x + random.uniform(-40, 40):.0f},{1700} {x + random.uniform(-30, 30):.0f},{random.uniform(1560, 1660):.0f}" stroke="{random.choice(["#b7604a", "#c56f55", "#a85540"])}" stroke-width="{random.uniform(14, 22):.0f}" fill="none" stroke-linecap="round"/>'
                 for x in range(-60, 3500, 38))
H.append(zona(5, '<rect x="0" y="-2600" width="3400" height="4600" fill="#e8d6c0"/>'
              '<rect x="0" y="-2600" width="3400" height="4600" fill="url(#luzsala)" opacity="0.4"/>'
              # bajos del sofá a la derecha: cueva oscura con flecos, moneda y pieza de construcción
              '<rect x="1900" y="400" width="1500" height="300" fill="#5b86c4"/>' + "".join(f'<rect x="{1900 + i * 50}" y="690" width="26" height="{120 + (i % 3) * 30}" fill="#4a6fa5"/>' for i in range(30))
              + '<rect x="1900" y="820" width="1500" height="1100" fill="#2a2440"/><ellipse cx="2650" cy="1700" rx="700" ry="90" fill="#1d1830"/>'
              '<circle cx="3000" cy="1440" r="250" fill="#e2c27a"/><circle cx="3000" cy="1440" r="190" fill="#d4ad5c"/><text x="3000" y="1500" text-anchor="middle" font-family="Inter" font-weight="900" font-size="170" fill="#b8913f">1</text>'
              '<rect x="2150" y="1330" width="380" height="250" rx="16" fill="#e5484d"/>' + "".join(f'<rect x="{2180 + i * 120}" y="1270" width="80" height="70" rx="12" fill="#e5484d"/>' for i in range(3))
              + '<ellipse cx="2600" cy="1560" rx="120" ry="80" fill="#8f8a9a" opacity="0.7"/>'
              + fibras, w=3400, h=4600, top=-2600))
H.append(pj_at("p5", ZL(5) + 700, cm=7))
# el gato: cabeza enorme asomando por arriba y pata que baja
H.append(f'''<svg id="gato" style="position:absolute;left:{ZL(5) + 500}px;top:-2300px;overflow:visible" width="10" height="10">
<path d="M-900,700 L-700,-200 L-380,300 Z M900,700 L700,-200 L380,300 Z" fill="#e8a046"/>
<path d="M-820,560 L-700,40 L-500,340 Z M820,560 L700,40 L500,340 Z" fill="#f6c1a6"/>
<ellipse cx="0" cy="900" rx="1000" ry="820" fill="#f2b05a"/>
<path d="M-300,420 C-200,520 -100,520 0,420 M300,420 C200,520 100,520 0,420" stroke="#d98b35" stroke-width="40" fill="none"/>
<ellipse cx="-360" cy="820" rx="150" ry="180" fill="#c6e36a"/><ellipse cx="360" cy="820" rx="150" ry="180" fill="#c6e36a"/>
<ellipse id="pupila1" cx="-360" cy="820" rx="34" ry="150" fill="#1d1b26"/><ellipse id="pupila2" cx="360" cy="820" rx="34" ry="150" fill="#1d1b26"/>
<path d="M-70,1060 L70,1060 L0,1130 Z" fill="#e57a8a"/>
<path d="M-120,1220 C-60,1270 0,1230 0,1170 C0,1230 60,1270 120,1220" stroke="#8a4e2c" stroke-width="18" fill="none"/>
{"".join(f'<path d="M{s * 160},{1120 + k * 50} L{s * 900},{1040 + k * 90}" stroke="#fbf8f2" stroke-width="10"/>' for s in (-1, 1) for k in range(3))}
</svg>''')
H.append(f'<svg id="pata" style="position:absolute;left:{ZL(5) + 1250}px;top:-1400px;overflow:visible" width="10" height="10">'
         '<rect x="-230" y="-1200" width="460" height="2200" rx="220" fill="#f2b05a"/><ellipse cx="0" cy="1000" rx="300" ry="200" fill="#f2b05a"/>'
         + "".join(f'<ellipse cx="{dx}" cy="1110" rx="60" ry="46" fill="#f6c1a6"/>' for dx in (-170, -55, 60, 175)) + '</svg>')
H.append(f'<div id="edificio" class="badge" style="left:{ZL(5) + 80}px;top:-120px;background:#3d405b;font-size:48px">🏢 50 PISOS</div>')

# ---- Z6 · NOCHE: el reloj de pared gigante
H.append(zona(6, '<rect x="0" y="0" width="1700" height="1920" fill="url(#nocheG)"/>'
              + "".join(f'<rect x="{x}" y="0" width="26" height="1920" fill="#ffffff" opacity="0.03"/>' for x in range(20, 1700, 70))
              + '<circle cx="850" cy="900" r="640" fill="#3d405b"/><circle cx="850" cy="900" r="580" fill="#fbf8f2"/>'
              + "".join(f'<line x1="{850 + 520 * math.cos(a * math.pi / 6):.0f}" y1="{900 + 520 * math.sin(a * math.pi / 6):.0f}" x2="{850 + 460 * math.cos(a * math.pi / 6):.0f}" y2="{900 + 460 * math.sin(a * math.pi / 6):.0f}" stroke="#3d405b" stroke-width="22"/>' for a in range(12))
              + '<text x="850" y="450" text-anchor="middle" font-family="Inter" font-weight="900" font-size="110" fill="#3d405b">12</text>'
              '<line id="rh" x1="850" y1="900" x2="850" y2="620" stroke="#1d2b33" stroke-width="40" stroke-linecap="round" transform="rotate(-60 850 900)"/>'
              '<line id="rm" x1="850" y1="900" x2="850" y2="440" stroke="#e5484d" stroke-width="24" stroke-linecap="round" transform="rotate(-150 850 900)"/>'
              '<circle cx="850" cy="900" r="40" fill="#1d2b33"/>'
              + "".join(f'<circle cx="{random.uniform(0, 1700):.0f}" cy="{random.uniform(0, 300):.0f}" r="3" fill="#fff" opacity="0.6"/>' for _ in range(20))))
H.append(f'<svg id="destello" style="position:absolute;left:{ZL(6) + 850}px;top:1500px;overflow:visible;opacity:0" width="10" height="10">'
         + "".join(f'<path d="M0,-{r} L{r * 0.18:.0f},-{r * 0.18:.0f} L{r},0 L{r * 0.18:.0f},{r * 0.18:.0f} L0,{r} L-{r * 0.18:.0f},{r * 0.18:.0f} L-{r},0 L-{r * 0.18:.0f},-{r * 0.18:.0f} Z" fill="#fff6c9" opacity="{op}" transform="rotate({rot})"/>' for r, op, rot in ((360, 0.9, 0), (240, 0.8, 45)))
         + '</svg>')

# ---- Z7 · DORMITORIO a tamaño normal (de noche) y una hormiga de verdad en el suelo
L7 = ZL(7)
H.append(f'<svg style="position:absolute;left:{L7}px;top:0;overflow:visible" width="1500" height="1920" viewBox="0 0 1500 1920">'
         + pared_suelo("s7", "#c9b3c9", "#a990ad", "#8a5a3c", "#6e4a33") + ventana(940, 420, 330, 470, noche=True, cortina="#4a5a85")
         + cuadro(230, 520, 230, 230) + reloj("clk7", 640, 640) + lampara_mesita(40) + '</svg>')
H.append(f'<svg style="position:absolute;left:{L7}px;top:0;overflow:visible" width="1" height="1">'
         '<rect x="215" y="1080" width="38" height="620" rx="18" fill="#8a5a3c"/><rect x="230" y="1450" width="760" height="70" rx="16" fill="#f4efe6"/>'
         '<rect x="230" y="1520" width="760" height="30" fill="#7a4e33"/><rect x="960" y="1400" width="34" height="300" rx="14" fill="#8a5a3c"/>'
         '<ellipse cx="330" cy="1420" rx="110" ry="44" fill="#ffffff"/><path d="M420,1400 C600,1380 800,1385 960,1410 L960,1470 L420,1470 Z" fill="url(#manta)"/></svg>')
H.append(pj_at("p6", L7 + 1150, cm=7))
H.append(f'<svg id="hormiga" style="position:absolute;left:{L7 + 760}px;top:1760px;overflow:visible" width="10" height="10">'
         '<ellipse cx="0" cy="0" rx="9" ry="7" fill="#1d1b26"/><ellipse cx="14" cy="-1" rx="6" ry="5" fill="#1d1b26"/><ellipse cx="-14" cy="0" rx="11" ry="8" fill="#1d1b26"/>'
         '<path d="M-6,4 l-8,9 M2,5 l0,10 M8,4 l8,9 M-6,-4 l-8,-9 M2,-5 l0,-10 M8,-4 l8,-9" stroke="#1d1b26" stroke-width="2"/></svg>')

# ------------------------------------------------------------------ guion → animación (todo con P())
for pid in ("p0", "p1", "p2", "p3", "p4", "p5", "p6"):
    vida(pid)
COLORES_T = ["#f2b84b", "#7b7fc4", "#e07a5f", "#3fbf7f", "#5aa9e6", "#c56f55", "#f2b84b", "#7b7fc4"]
NT = [0]
def transicion(t, x, y, z):
    """Transición decorativa: un círculo de color con anillos se abre desde el centro, cambia el plano y se cierra.
    Con un whoosh suave y una campanita bajita."""
    c = COLORES_T[NT[0] % len(COLORES_T)]; NT[0] += 1
    J(f'tl.set("#iris", {{background:"radial-gradient(circle, {c} 0%, {c} 58%, #fbf8f2 59%, #fbf8f2 61%, {c} 62%, {c} 100%)"}}, {t - 0.45:.2f});')
    J(f'tl.fromTo("#iris", {{scale:0, rotation:-30}}, {{scale:1, rotation:0, duration:0.42, ease:"power2.in", immediateRender:false}}, {t - 0.42:.2f});')
    J(f'tl.set("#world", {{x:{540 - x * z:.1f}, y:{960 - y * z:.1f}, scale:{z}}}, {t:.2f}); tl.set("#lejos", {{x:{(540 - x * z) * 0.35:.1f}}}, {t:.2f});')
    J(f'tl.to("#iris", {{scale:0, rotation:30, duration:0.5, ease:"power2.out"}}, {t + 0.04:.2f});')
    FX_EV.append(("suave", t - 0.42))

# 1-3 · despiertas diminuto en la cama
X0, Y0, Z0 = ZL(0) + 700, 1150, 0.95
J(f'tl.set("#world", {{x:{540 - X0 * 1.2:.1f}, y:{960 - 1050 * 1.2:.1f}, scale:1.2}}, 0);')
J(f'tl.set("#p0-eyes", {{scaleY:1.3, svgOrigin:"500 742"}}, 0); tl.set("#p0-mouthO", {{opacity:1}}, 0); tl.set("#p0-mouth", {{opacity:0}}, 0);')
J(f'tl.to("#p0-eyes", {{scaleY:1, duration:0.3, svgOrigin:"500 742"}}, {FE(1):.2f}); tl.to("#p0-mouthO", {{opacity:0, duration:0.2}}, {FE(1):.2f}); tl.to("#p0-mouth", {{opacity:1, duration:0.2}}, {FE(1):.2f});')
tmm = P("milimetros")
J(f'tl.fromTo("#regla", {{y:1300}}, {{y:0, duration:0.8, ease:"power3.out", immediateRender:false}}, {P("mides") - 0.2:.2f});')
FX_EV.append(("suave", P("mides") - 0.2))
cam(P("mides") - 0.3, ZL(0) + 800, 1150, 0.9, dur=0.9)
J(f'tl.to("#p0-head", {{rotation:-8, duration:0.4, yoyo:true, repeat:1, repeatDelay:0.6, svgOrigin:"500 900"}}, {tmm:.2f});')
J(f'tl.to("#regla", {{y:1300, duration:0.5, ease:"power2.in"}}, {F(3) - 0.1:.2f});')
cam(F(3), ZL(0) + 850, 1250, 0.72, dur=1.6, ease="sine.inOut")
J(f'tl.to("#p0-eyes", {{x:-8, duration:0.3, yoyo:true, repeat:1, repeatDelay:0.5}}, {F(3) + 0.3:.2f});')

# 4-6 · el pasillo: casi 6 km y los ácaros
t = F(4)
transicion(t, ZL(1) + 850, 1150, 0.9)
caminar("p1", t, desde=-500, dur=2.6, pasos=8)
cam(t + 0.2, ZL(1) + 900, 1100, 0.82, dur=2.6, ease="sine.inOut")
tpo = P("polvo")
J(f'tl.fromTo("#acaro1", {{x:300, opacity:0}}, {{x:0, opacity:1, duration:1.4, ease:"power2.out", immediateRender:false}}, {tpo:.2f});')
J(f'tl.fromTo("#acaro2", {{x:-260, opacity:0}}, {{x:0, opacity:1, duration:1.6, ease:"power2.out", immediateRender:false}}, {tpo + 0.3:.2f});')
J(f'tl.to("#acaro1 .patas, #acaro2 .patas", {{y:-6, duration:0.12, yoyo:true, repeat:20, ease:"sine.inOut"}}, {tpo:.2f});')
J(f'tl.to("#p1-eyes", {{scaleY:1.3, duration:0.2, svgOrigin:"500 742"}}, {P("acaros"):.2f}); tl.to("#p1-mouth", {{attr:{{d:"M482,826 Q500,812 518,826"}}, duration:0.2}}, {P("acaros"):.2f});')
cam(P("acaros") - 0.2, ZL(1) + 850, 1250, 0.95, dur=0.8)

# 7-9 · eres fortísimo (grano de arroz) y caes de la mesa sin hacerte daño
t = F(7)
transicion(t, ZL(2) + 700, 1200, 0.9)
J('tl.set("#arroz", {y:0}, 0);')
tpe = P("peso")
J(f'tl.to("#p2-armLg", {{rotation:150, duration:0.4, ease:"back.out(1.4)", svgOrigin:"356 985"}}, {tpe - 0.5:.2f}); tl.to("#p2-armRg", {{rotation:-150, duration:0.4, ease:"back.out(1.4)", svgOrigin:"644 985"}}, {tpe - 0.5:.2f});')
J(f'tl.to("#arroz", {{y:-1080, duration:0.5, ease:"back.out(1.5)"}}, {tpe - 0.45:.2f});')
J(f'tl.to("#p2-mouth", {{attr:{{d:"M474,814 Q500,840 526,814"}}, duration:0.3}}, {tpe:.2f});')
FX_EV.append(("pop", tpe - 0.2))
tme = P("mesa")
J(f'tl.to("#arroz", {{y:0, x:-450, duration:0.5, ease:"power2.in"}}, {tme - 0.9:.2f}); tl.to(["#p2-armLg", "#p2-armRg"], {{rotation:0, duration:0.35}}, {tme - 0.9:.2f});')
J(f'tl.to("#p2", {{x:500, duration:0.6, ease:"power1.in"}}, {tme - 0.6:.2f});')
J(f'tl.to("#p2", {{y:2100, rotation:20, duration:2.4, ease:"sine.inOut", transformOrigin:"50% 70%"}}, {tme:.2f});')
J(f'tl.to("#aire", {{opacity:1, duration:0.3}}, {tme + 0.3:.2f}); tl.to("#aire", {{y:1500, duration:2.0, ease:"sine.inOut"}}, {tme + 0.2:.2f}); tl.to("#aire", {{opacity:0, duration:0.3}}, {tme + 2.3:.2f});')
cam(tme - 0.2, ZL(2) + 1250, 3000, 0.62, dur=2.6, ease="sine.inOut")
J(f'tl.to("#p2", {{rotation:0, duration:0.3}}, {tme + 2.4:.2f});')
FX_EV.append(("whoosh", tme))

# 10-12 · la cocina: miga gigante, frío y comer sin parar
t = F(10)
transicion(t, ZL(3) + 850, 1150, 0.9)
J(f'tl.fromTo("#miga", {{scale:0.6, opacity:0}}, {{scale:1, opacity:1, duration:0.6, ease:"back.out(1.6)", transformOrigin:"50% 100%", immediateRender:false}}, {P("miga") - 0.1:.2f});')
FX_EV.append(("pop", P("miga")))
tfr = P("frio")
pop("#termo", tfr)
J(f'tl.fromTo("#mercurio", {{scaleY:1}}, {{scaleY:0.35, duration:1.6, ease:"power2.inOut", transformOrigin:"50% 100%", immediateRender:false}}, {tfr + 0.3:.2f});')
J(f'tl.to("#p3", {{x:6, duration:0.06, yoyo:true, repeat:30, ease:"none"}}, {tfr:.2f});')
J(f'tl.to("#vaho", {{opacity:1, duration:0.2}}, {tfr + 0.2:.2f}); tl.fromTo("#vaho .vh", {{scale:0.3, opacity:0.9}}, {{scale:1.4, opacity:0, y:-60, duration:1.2, stagger:0.25, repeat:2, transformOrigin:"50% 50%", immediateRender:false}}, {tfr + 0.2:.2f});')
tco = P("comer")
J(f'tl.to("#termo", {{opacity:0, duration:0.3}}, {tco - 0.4:.2f}); tl.to("#vaho", {{opacity:0, duration:0.3}}, {tco - 0.4:.2f});')
J(f'tl.to("#p3", {{x:220, duration:0.6, ease:"power2.out"}}, {tco - 0.3:.2f});')
J(f'tl.to("#p3-armRg", {{rotation:-120, duration:0.25, yoyo:true, repeat:5, ease:"sine.inOut", svgOrigin:"644 985"}}, {tco + 0.3:.2f});')
J(f'tl.to("#miga", {{scale:0.8, duration:1.6, ease:"steps(5)", transformOrigin:"100% 100%"}}, {tco + 0.3:.2f});')

# 13 · la gota del grifo que atrapa como pegamento
t = F(13)
transicion(t, ZL(4) + 900, 1100, 0.85)
tgo = P("gota")
J(f'tl.fromTo("#gota", {{y:0, scaleY:1}}, {{y:780, duration:0.55, ease:"power2.in", immediateRender:false}}, {tgo:.2f});')
J(f'tl.to("#gota", {{opacity:0, duration:0.05}}, {tgo + 0.55:.2f}); tl.fromTo("#charco", {{opacity:0, scaleY:0.2}}, {{opacity:1, scaleY:1, duration:0.4, ease:"back.out(1.6)", transformOrigin:"50% 100%", immediateRender:false}}, {tgo + 0.55:.2f});')
FX_EV.append(("pop", tgo + 0.55))
J(f'tl.to("#p4-armLg", {{rotation:70, duration:0.3, yoyo:true, repeat:5, svgOrigin:"356 985"}}, {tgo + 0.9:.2f}); tl.to("#p4-armRg", {{rotation:-70, duration:0.3, yoyo:true, repeat:5, svgOrigin:"644 985"}}, {tgo + 0.9:.2f});')
J(f'tl.to("#charco", {{scaleX:1.05, scaleY:0.96, duration:0.3, yoyo:true, repeat:5, transformOrigin:"50% 100%"}}, {tgo + 1.0:.2f});')
J(f'tl.to("#p4-mouth", {{attr:{{d:"M482,826 Q500,812 518,826"}}, duration:0.2}}, {tgo + 0.6:.2f});')

# 14-16 · llega el gato (alto como un edificio) y corres bajo el sofá
t = F(14)
transicion(t, ZL(5) + 700, 1150, 0.9)
J(f'tl.fromTo("#pata", {{y:-1200}}, {{y:0, duration:1.0, ease:"power2.in", immediateRender:false}}, {P("gato") - 0.2:.2f});')
FX_EV.append(("golpe", P("gato") + 0.8))
J(f'tl.to("#p5-eyes", {{scaleY:1.35, duration:0.15, svgOrigin:"500 742"}}, {P("gato") + 0.8:.2f}); tl.to("#p5-mouthO", {{opacity:1, duration:0.15}}, {P("gato") + 0.8:.2f}); tl.to("#p5-mouth", {{opacity:0, duration:0.15}}, {P("gato") + 0.8:.2f});')
ted = P("edificio")
cam(ted - 0.6, ZL(5) + 700, -400, 0.42, dur=1.6, ease="power2.inOut")
pop("#edificio", ted)
J(f'tl.to(["#pupila1", "#pupila2"], {{attr:{{rx:70}}, duration:0.4}}, {ted:.2f});')
tso = P("sofa")
cam(P("corres") - 0.3, ZL(5) + 1700, 1150, 0.8, dur=1.2, ease="power2.inOut")
J(f'tl.to("#edificio", {{opacity:0, duration:0.3}}, {P("corres") - 0.3:.2f});')
J(f'tl.to("#p5", {{x:1700, duration:1.6, ease:"power2.in"}}, {P("corres"):.2f});')
for k in range(8):
    J(f'tl.to("#p5-{"legL" if k % 2 == 0 else "legR"}", {{y:-30, duration:0.1, yoyo:true, repeat:1}}, {P("corres") + k * 0.2:.2f});')
J(f'tl.to("#pata", {{y:200, x:600, duration:0.6, ease:"power2.in"}}, {tso:.2f});')
FX_EV.append(("whoosh", P("corres")))

# 17 · medianoche: el reloj marca las doce y vuelves a tu tamaño
t = F(17)
transicion(t, ZL(6) + 850, 950, 0.95)
tdo = P("doce")
J(f'tl.to("#rh", {{rotation:60, duration:1.4, ease:"power2.inOut", svgOrigin:"850 900"}}, {t + 0.2:.2f}); tl.to("#rm", {{rotation:150, duration:1.4, ease:"power2.inOut", svgOrigin:"850 900"}}, {t + 0.2:.2f});')
FX_EV.append(("clic", t + 1.6))
J(f'tl.to("#destello", {{opacity:1, duration:0.3}}, {P("tamano", 2) - 0.6:.2f}); tl.fromTo("#destello", {{scale:0.2, rotation:0}}, {{scale:3, rotation:90, duration:0.9, ease:"power2.out", immediateRender:false}}, {P("tamano", 2) - 0.6:.2f});')
FX_EV.append(("brillo", P("tamano", 2) - 0.6))
transicion(P("tamano", 2) + 0.3, L7 + 800, 1150, 0.9)

# 18 · tamaño normal… y una hormiga de verdad en el suelo (luego, bucle)
t18 = F(18)
J(f'tl.to("#p6-eyes", {{y:8, duration:0.3}}, {P("suelo") - 0.2:.2f}); tl.to("#p6-headw", {{rotation:-8, duration:0.4, svgOrigin:"500 900"}}, {P("suelo") - 0.2:.2f});')
J(f'tl.fromTo("#hormiga", {{x:-200}}, {{x:200, duration:3.0, ease:"none", immediateRender:false}}, {t18:.2f});')
cam(P("ahi") - 0.2, L7 + 860, 1720, 3.2, dur=1.8, ease="power2.inOut")
tcut = DUR - 0.5
transicion(tcut, ZL(0) + 700, 1050, 1.2)
J(f'tl.set("#p0-eyes", {{scaleY:1.3, svgOrigin:"500 742"}}, {tcut:.2f}); tl.set("#p0-mouthO", {{opacity:1}}, {tcut:.2f}); tl.set("#p0-mouth", {{opacity:0}}, {tcut:.2f});')
J(f'tl.set("#p2", {{x:0, y:0, rotation:0}}, {tcut:.2f}); tl.set("#arroz", {{x:0, y:0}}, {tcut:.2f});')

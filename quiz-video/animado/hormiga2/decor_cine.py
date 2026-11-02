# ---------------------------------------------------------------- DECORADO DE CINE: profundidad, luz y detalle
# Fondo desenfocado (lejos), rayos de luz suaves, polvo en suspensión y primer plano desenfocado.
H.append('<svg width="0" height="0" style="position:absolute"><defs>'
         '<filter id="lejos1" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="10"/></filter>'
         '<filter id="lejos2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="22"/></filter>'
         '<filter id="cerca" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="28"/></filter>'
         '<linearGradient id="rayo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3d6" stop-opacity="0.55"/><stop offset="1" stop-color="#fff3d6" stop-opacity="0"/></linearGradient>'
         '<linearGradient id="rayoFrio" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9ecff" stop-opacity="0.5"/><stop offset="1" stop-color="#d9ecff" stop-opacity="0"/></linearGradient>'
         '<radialGradient id="bokeh" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff1c9" stop-opacity="0.9"/><stop offset="0.7" stop-color="#ffd27a" stop-opacity="0.35"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient>'
         '<pattern id="tela" width="16" height="16" patternUnits="userSpaceOnUse"><path d="M0,8 L16,8 M8,0 L8,16" stroke="#c9d6ea" stroke-width="1.4" opacity="0.6"/></pattern>'
         '<pattern id="veta" width="400" height="60" patternUnits="userSpaceOnUse"><path d="M0,20 C100,10 200,34 400,18 M0,44 C140,52 260,30 400,46" stroke="#7a4a2e" stroke-width="3" fill="none" opacity="0.35"/></pattern>'
         '<pattern id="marmol" width="500" height="300" patternUnits="userSpaceOnUse"><path d="M0,60 C120,30 220,140 500,90 M0,220 C160,180 300,280 500,230" stroke="#cfc7ba" stroke-width="4" fill="none" opacity="0.7"/></pattern>'
         '</defs></svg>')

def capa(k, cuerpo, w=ZW, top=-400, h=2700):
    return f'<svg style="position:absolute;left:{ZL(k)}px;top:{top}px;overflow:visible" width="{w}" height="{h}" viewBox="0 {top} {w} {h}">{cuerpo}</svg>'

def rayos_luz(x, y, ang=18, n=4, frio=False, largo=1700):
    g = "rayoFrio" if frio else "rayo"
    return "".join(f'<path d="M{x + i * 110},{y} L{x + i * 110 + 90},{y} L{x + i * 110 + 90 + largo * math.tan(math.radians(ang)):.0f},{y + largo} L{x + i * 110 - 60 + largo * math.tan(math.radians(ang)):.0f},{y + largo} Z" fill="url(#{g})" opacity="{0.55 - i * 0.08:.2f}"/>' for i in range(n))

def bokehs(pts):
    return "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#bokeh)" opacity="{o}"/>' for x, y, r, o in pts)

def motas(k, n=26, y0=300, y1=1600, color="#fff6e0"):
    out = []
    for i in range(n):
        mid = f"mz{k}_{i}"
        x = ZL(k) + random.uniform(80, ZW - 80); y = random.uniform(y0, y1)
        out.append(f'<div class="motaz" id="{mid}" style="left:{x:.0f}px;top:{y:.0f}px;width:{random.choice([6, 8, 10])}px;height:{random.choice([6, 8, 10])}px;background:{color};opacity:{random.uniform(0.3, 0.7):.2f}"></div>')
        J(f'tl.fromTo("#{mid}", {{x:0, y:0}}, {{x:{random.uniform(-60, 60):.0f}, y:{random.uniform(-120, -40):.0f}, duration:{random.uniform(6, 10):.1f}, ease:"sine.inOut", yoyo:true, repeat:{int(DUR / 12) + 1}, immediateRender:false}}, 0);')
    return "".join(out)

ZONAS_FONDO = {}
ZONAS_CERCA = {}

# Z0 · cama por la mañana: dormitorio gigante desenfocado detrás, rayos de sol, sábana con textura
ZONAS_FONDO[0] = capa(0,
    f'<g filter="url(#lejos2)" opacity="0.9">'
    '<rect x="-200" y="-400" width="700" height="1300" fill="#9fd3f5"/><rect x="-200" y="-400" width="700" height="1300" fill="none" stroke="#fbf6ee" stroke-width="60"/>'
    '<path d="M-220,-420 L60,-420 C20,100 120,500 30,960 L-220,960 Z" fill="#6a8caf"/>'
    '<rect x="1520" y="200" width="300" height="900" rx="30" fill="#b07a52"/><path d="M1540,200 L1800,200 L1720,-60 L1620,-60 Z" fill="#f2d27a"/>'
    '</g>' + bokehs(((1650, 120, 230, 0.8), (1500, 300, 120, 0.5), (200, 700, 160, 0.35)))
    + rayos_luz(-60, -300, ang=22, n=5, largo=2100)
    + '<rect x="-100" y="1350" width="1900" height="900" fill="url(#tela)" opacity="0.5"/>')
ZONAS_CERCA[0] = capa(0, '<g filter="url(#cerca)"><path d="M-200,1820 C200,1640 500,1880 900,1760 L900,2300 L-200,2300 Z" fill="#e8eef8"/>'
                         '<path d="M1300,1900 C1500,1700 1800,1780 1900,1700 L1900,2300 L1300,2300 Z" fill="#dfe7f3"/>'
                         '<path d="M1500,-300 C1600,0 1550,300 1700,600" stroke="#4b3021" stroke-width="60" fill="none" stroke-linecap="round"/></g>')

# Z1 · pasillo: zapatilla y calcetín gigantes al fondo, luz de la cocina sobre el suelo
ZONAS_FONDO[1] = capa(1,
    '<g filter="url(#lejos1)">'
    '<path d="M-120,1430 C-80,1180 180,1100 420,1180 C560,1230 700,1260 760,1340 L760,1430 Z" fill="#f4efe6"/><path d="M-120,1430 L760,1430 L760,1470 L-120,1470 Z" fill="#c9c2b6"/>'
    '<path d="M60,1220 L380,1190" stroke="#e5484d" stroke-width="26" stroke-linecap="round"/><path d="M120,1180 L150,1260 M200,1172 L230,1252 M280,1166 L310,1246" stroke="#3d405b" stroke-width="10"/>'
    '<path d="M1440,1430 C1430,1300 1520,1240 1640,1260 C1720,1270 1760,1330 1760,1430 Z" fill="#7aa38f"/>'
    '</g>'
    '<path d="M1020,1420 L1500,1420 L1800,2300 L700,2300 Z" fill="#fff4cf" opacity="0.28"/>'
    + bokehs(((1260, 330, 200, 0.55), (1400, 650, 120, 0.4)))
    + '<rect x="0" y="1420" width="1700" height="900" fill="url(#veta)"/>')
ZONAS_CERCA[1] = capa(1, '<g filter="url(#cerca)"><ellipse cx="80" cy="1900" rx="300" ry="190" fill="#cfc6b8"/><ellipse cx="1650" cy="1850" rx="260" ry="160" fill="#d8cfc2"/></g>')

# Z2 · mesa: cuchara y taza gigantes, ventana de la cocina al fondo, migas
ZONAS_FONDO[2] = capa(2,
    '<g filter="url(#lejos2)" opacity="0.85">'
    '<rect x="1150" y="-200" width="500" height="900" fill="#bfe3f7"/><rect x="1150" y="-200" width="500" height="900" fill="none" stroke="#fbf6ee" stroke-width="50"/>'
    '<rect x="-100" y="300" width="900" height="60" fill="#c99067"/>' + "".join(f'<rect x="{x}" y="{170}" width="110" height="130" rx="14" fill="{c}"/>' for x, c in ((-50, "#e5484d"), (90, "#f2b84b"), (230, "#3fbf7f"), (380, "#5aa9e6")))
    + '</g>' + rayos_luz(1150, -100, ang=-20, n=4, largo=1900)
    + '<path d="M700,1700 L760,1450 C770,1400 840,1400 850,1450 L900,1700 Z" fill="#c9d0dc" opacity="0" />'
    + '<g><rect x="1230" y="1530" width="420" height="170" rx="16" fill="#9aa3b5"/><ellipse cx="1440" cy="1530" rx="210" ry="40" fill="#c9d0dc"/><path d="M1230,1600 C1100,1600 1100,1680 1230,1680" stroke="#9aa3b5" stroke-width="24" fill="none"/></g>'
    + '<rect x="0" y="1700" width="1250" height="90" fill="url(#veta)"/>'
    + "".join(f'<ellipse cx="{x}" cy="{1700}" rx="{r}" ry="{r * 0.6:.0f}" fill="#d9a35c"/>' for x, r in ((680, 26), (720, 16), (1150, 20))), h=4600)
ZONAS_CERCA[2] = capa(2, '<g filter="url(#cerca)"><path d="M-200,1650 L500,1690 C560,1692 560,1730 500,1732 L-200,1760 Z" fill="#c9d0dc"/>'
                         '<ellipse cx="-80" cy="1700" rx="170" ry="110" fill="#b9c3cf"/></g>', h=4600)

# Z3 · suelo de la cocina: nevera con luz fría, zapato, granos de azúcar brillantes
ZONAS_FONDO[3] = capa(3,
    '<g filter="url(#lejos1)">'
    '<rect x="1150" y="-300" width="650" height="1300" rx="30" fill="#eef3f8"/><rect x="1150" y="560" width="650" height="16" fill="#c9d0dc"/><rect x="1190" y="300" width="20" height="220" rx="10" fill="#9aa3b5"/>'
    '<path d="M-120,1420 C-110,1240 60,1170 260,1230 C360,1260 420,1320 430,1420 Z" fill="#3d405b"/><path d="M-120,1420 L430,1420 L430,1450 L-120,1450 Z" fill="#1d1b26"/>'
    '</g>' + rayos_luz(1150, 980, ang=-12, n=3, frio=True, largo=900)
    + "".join(f'<path d="M{x},{y} l14,-14 14,14 -14,14 Z" fill="#ffffff" opacity="0.9"/>' for x, y in ((160, 1600), (1490, 1640), (1330, 1540))))
ZONAS_CERCA[3] = capa(3, '<g filter="url(#cerca)"><rect x="-200" y="1780" width="520" height="400" rx="40" fill="#fbfbfb" transform="rotate(14 60 1980)"/><ellipse cx="1700" cy="1900" rx="300" ry="160" fill="#d9a35c"/></g>')

# Z4 · encimera: esponja, burbujas de jabón, gotitas y reflejos
ZONAS_FONDO[4] = capa(4,
    '<g filter="url(#lejos1)"><rect x="-100" y="1050" width="560" height="650" rx="30" fill="#f2b84b"/><rect x="-100" y="1050" width="560" height="200" rx="30" fill="#3fbf7f"/>'
    '<rect x="1300" y="700" width="260" height="1000" rx="60" fill="#5aa9e6"/><rect x="1360" y="560" width="140" height="160" rx="20" fill="#e5484d"/></g>'
    + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffffff" fill-opacity="0.18" stroke="#ffffff" stroke-opacity="0.75" stroke-width="5"/><ellipse cx="{x - r * 0.35:.0f}" cy="{y - r * 0.4:.0f}" rx="{r * 0.25:.0f}" ry="{r * 0.15:.0f}" fill="#ffffff" opacity="0.7"/>' for x, y, r in ((240, 900, 80), (360, 760, 50), (1450, 420, 70), (1250, 1180, 40)))
    + '<rect x="-100" y="1700" width="1900" height="500" fill="url(#marmol)"/>'
    + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 0.55:.0f}" fill="#bfe6ff" opacity="0.7" stroke="#ffffff" stroke-width="3"/>' for x, y, r in ((250, 1760, 40), (1500, 1800, 55), (600, 1850, 24))))
ZONAS_CERCA[4] = capa(4, '<g filter="url(#cerca)"><circle cx="1600" cy="1600" r="220" fill="#ffffff" fill-opacity="0.15" stroke="#ffffff" stroke-opacity="0.6" stroke-width="16"/></g>')

# Z5 · salón: tele encendida, planta y lámpara de pie desenfocadas al fondo; sombra del gato
ZONAS_FONDO[5] = capa(5,
    '<g filter="url(#lejos2)" opacity="0.9">'
    '<rect x="-150" y="-200" width="900" height="560" rx="20" fill="#1d1b26"/><rect x="-120" y="-170" width="840" height="500" rx="10" fill="#5aa9e6"/><rect x="-120" y="-170" width="840" height="200" fill="#9fd3f5" opacity="0.6"/>'
    '<path d="M1300,600 C1250,300 1500,200 1550,-100 M1400,600 C1450,300 1300,100 1400,-200" stroke="#4f9a6a" stroke-width="60" fill="none"/>'
    '</g>' + bokehs(((300, 50, 260, 0.45), (2600, 200, 220, 0.6), (3200, 500, 160, 0.4))), w=3400, top=-2600, h=4600)
ZONAS_CERCA[5] = capa(5, '<g filter="url(#cerca)">' + "".join(f'<path d="M{x},1920 C{x + 10},1800 {x - 20},1700 {x + 15},1600" stroke="#a85540" stroke-width="60" fill="none" stroke-linecap="round"/>' for x in (40, 140, 1600, 3300)) + '</g>', w=3400, top=-2600, h=4600)
H.append(f'<div id="sombragato" style="position:absolute;left:{ZL(5) - 200}px;top:-2600px;width:3800px;height:4600px;background:radial-gradient(60% 50% at 30% 30%, rgba(20,16,40,0.55), rgba(20,16,40,0) 70%);opacity:0;pointer-events:none"></div>')

# Z6 · noche: luz de luna por la ventana sobre el reloj
ZONAS_FONDO[6] = capa(6, rayos_luz(-100, -300, ang=25, n=4, frio=True, largo=2300)
                         + bokehs(((1500, 200, 140, 0.35), (200, 1500, 120, 0.25))))
ZONAS_CERCA[6] = ""

# Z7 · dormitorio de noche (tamaño normal): luz cálida de la lámpara
ZONAS_FONDO[7] = capa(7, bokehs(((125, 1290, 260, 0.6),)) + rayos_luz(940, 420, ang=-8, n=3, frio=True, largo=1300))
ZONAS_CERCA[7] = ""

# ESCENAS v2 — una CASA DE VERDAD en corte (como una casa de muñecas), colores vivos, nada desenfocado.
# Escala de la casa: una persona mide ~1000 px. «Tú» (hormiga) mides ~90 px (licencia de dibujo animado).
# Se ejecuta dentro de gen.py (usa J, cam, pop, personaje, vida, P, F, FE, DUR, FX_EV, H, OVER).
H.clear()
OVER = []
exec(open(os.path.join(BASE, 'perfil.py'), encoding='utf-8').read())
exec(open(os.path.join(BASE, 'gato2.py'), encoding='utf-8').read())
FL = 1745                  # línea de los pies en el suelo
S_MINI = 0.085             # tamaño del personaje diminuto
WORLD_W = 13400
R = {"bed": (0, 2600), "hall": (2600, 4800), "din": (4800, 7000), "kit": (7000, 9800), "liv": (9800, 12900)}
rnd = random.Random(9)

def svg(cuerpo, idd=""):
    i = f' id="{idd}"' if idd else ""
    return f'<svg{i} style="position:absolute;left:0;top:0;overflow:visible" width="1" height="1">{cuerpo}</svg>'

DEF = ('<svg width="0" height="0" style="position:absolute"><defs>'
       '<linearGradient id="cielo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3fa7ff"/><stop offset="0.6" stop-color="#8fd3ff"/><stop offset="1" stop-color="#ffe1a8"/></linearGradient>'
       '<linearGradient id="amanecer" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff7eb3"/><stop offset="0.55" stop-color="#ffb36b"/><stop offset="1" stop-color="#ffe08a"/></linearGradient>'
       '<linearGradient id="cieloDia" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2e9bff"/><stop offset="1" stop-color="#bfe8ff"/></linearGradient>'
       '<linearGradient id="cieloNoche" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b1046"/><stop offset="1" stop-color="#3a2a8a"/></linearGradient>'
       '<linearGradient id="pBed" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff8c7a"/><stop offset="1" stop-color="#ff6f61"/></linearGradient>'
       '<linearGradient id="pHall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#38b6ff"/><stop offset="1" stop-color="#1e8fe0"/></linearGradient>'
       '<linearGradient id="pDin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd23f"/><stop offset="1" stop-color="#ffb627"/></linearGradient>'
       '<linearGradient id="pKit" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5ee2b8"/><stop offset="1" stop-color="#27c79a"/></linearGradient>'
       '<linearGradient id="pLiv" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9d6bff"/><stop offset="1" stop-color="#7a45f0"/></linearGradient>'
       '<linearGradient id="suelo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d98a4e"/><stop offset="1" stop-color="#b8682f"/></linearGradient>'
       '<linearGradient id="madera2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c97b45"/><stop offset="1" stop-color="#9a5a2c"/></linearGradient>'
       '<linearGradient id="metal" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9fb3c8"/><stop offset="0.45" stop-color="#f4f8ff"/><stop offset="1" stop-color="#8aa0b8"/></linearGradient>'
       '<radialGradient id="gotaG2" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#ffffff" stop-opacity="0.9"/><stop offset="0.45" stop-color="#9fdcff" stop-opacity="0.55"/><stop offset="1" stop-color="#2f9bff" stop-opacity="0.65"/></radialGradient>'
       '<radialGradient id="migaG2" cx="0.4" cy="0.35" r="0.8"><stop offset="0" stop-color="#ffe2a6"/><stop offset="1" stop-color="#d98b3a"/></radialGradient>'
       '<radialGradient id="lampG" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff3b0" stop-opacity="0.75"/><stop offset="1" stop-color="#fff3b0" stop-opacity="0"/></radialGradient>'
       '<pattern id="papelBed" width="90" height="90" patternUnits="userSpaceOnUse"><circle cx="20" cy="20" r="7" fill="#ffd6cc"/><path d="M65,55 l6,12 l13,2 l-10,9 l3,13 l-12,-7 l-12,7 l3,-13 l-10,-9 l13,-2 Z" fill="#ffb3a6" transform="scale(0.6) translate(40 30)"/></pattern>'
       '<pattern id="papelHall" width="120" height="120" patternUnits="userSpaceOnUse"><path d="M0,60 L60,0 L120,60 L60,120 Z" fill="none" stroke="#7fd0ff" stroke-width="5"/></pattern>'
       '<pattern id="papelDin" width="80" height="80" patternUnits="userSpaceOnUse"><circle cx="40" cy="40" r="10" fill="#ffe680"/><circle cx="0" cy="0" r="6" fill="#ffc84a"/></pattern>'
       '<pattern id="papelLiv" width="140" height="140" patternUnits="userSpaceOnUse"><path d="M70,20 C100,50 100,90 70,120 C40,90 40,50 70,20 Z" fill="#b48cff"/></pattern>'
       '<pattern id="azulejo" width="70" height="70" patternUnits="userSpaceOnUse"><rect width="70" height="70" fill="#ffffff"/><rect x="3" y="3" width="64" height="64" rx="6" fill="#e8fbff"/><circle cx="35" cy="35" r="9" fill="#5ac8fa"/></pattern>'
       '<pattern id="damero" width="160" height="160" patternUnits="userSpaceOnUse"><rect width="160" height="160" fill="#fff6e8"/><rect width="80" height="80" fill="#1fb5a5"/><rect x="80" y="80" width="80" height="80" fill="#1fb5a5"/></pattern>'
       '<pattern id="tablas" width="260" height="60" patternUnits="userSpaceOnUse"><rect width="260" height="60" fill="none" stroke="#8e4f22" stroke-width="4" opacity="0.55"/><path d="M130,0 L130,60" stroke="#8e4f22" stroke-width="3" opacity="0.4"/><path d="M20,30 C60,24 90,36 120,30" stroke="#f0a96b" stroke-width="3" fill="none" opacity="0.6"/></pattern>'
       '<pattern id="rayasManta" width="60" height="60" patternUnits="userSpaceOnUse"><rect width="60" height="60" fill="#2ec4b6"/><rect width="30" height="60" fill="#3ddcce"/></pattern>'
       '<pattern id="alfombraP" width="80" height="40" patternUnits="userSpaceOnUse"><rect width="80" height="40" fill="#ff5d8f"/><path d="M0,20 L20,0 L40,20 L60,0 L80,20 L60,40 L40,20 L20,40 Z" fill="#ffd23f"/></pattern>'
       '</defs></svg>')
H.append(DEF)

# ------------------------------------------------------------------ exterior: cielo, tejado y terreno (se ven en los planos abiertos)
H.append(svg('<rect x="-3000" y="-6000" width="19400" height="5950" fill="url(#cielo)"/>'
             + "".join(f'<g opacity="0.95"><ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 0.42:.0f}" fill="#ffffff"/><ellipse cx="{x + r * 0.5:.0f}" cy="{y - r * 0.2:.0f}" rx="{r * 0.6:.0f}" ry="{r * 0.4:.0f}" fill="#ffffff"/></g>'
                       for x, y, r in ((-800, -1500, 380), (1800, -2300, 300), (4200, -1700, 420), (7600, -2400, 340), (10400, -1600, 400), (13600, -2200, 360), (900, -3300, 260), (9000, -3400, 300)))
             + '<circle cx="12000" cy="-2900" r="320" fill="#ffe066"/><circle cx="12000" cy="-2900" r="420" fill="#ffe066" opacity="0.25"/>'
             # tejado de tejas
             + '<path d="M-260,-40 L6450,-1250 L13160,-40 Z" fill="#e2483d"/><path d="M-260,-40 L6450,-1250 L13160,-40" stroke="#b5302a" stroke-width="40" fill="none"/>'
             + "".join(f'<path d="M{-260 + i * 270},-40 L{6450 + (i * 270 - 6710) * 0.15:.0f},{-1250 + abs(i * 270 - 6710) * 0.0}" stroke="#c93a31" stroke-width="10" opacity="0.0"/>' for i in range(0))
             + "".join(f'<path d="M{6450 - (6710) * k:.0f},{-1250 + 1210 * k:.0f} L{6450 + 6710 * k:.0f},{-1250 + 1210 * k:.0f}" stroke="#ff6b5b" stroke-width="12" opacity="0.6"/>' for k in (0.2, 0.4, 0.6, 0.8))
             + '<rect x="9300" y="-1000" width="300" height="560" fill="#b5302a"/><rect x="9270" y="-1040" width="360" height="70" fill="#8e2420"/>'
             # forjado del techo y del suelo
             + '<rect x="-260" y="-60" width="13420" height="60" fill="#fff1dc"/><rect x="-260" y="1880" width="13420" height="90" fill="#efe0c8"/>'
             + '<rect x="-3000" y="1970" width="19400" height="4000" fill="#7a4b2a"/><rect x="-3000" y="1970" width="19400" height="60" fill="#4fc36b"/>'
             + "".join(f'<ellipse cx="{x}" cy="{2200 + (x * 7) % 400}" rx="{40 + x % 50}" ry="22" fill="#5e391f"/>' for x in range(-2600, 16000, 420))
             # paredes exteriores
             + '<rect x="-260" y="-60" width="260" height="2030" fill="#fff1dc"/><rect x="12900" y="-60" width="260" height="2030" fill="#fff1dc"/>'))

# ------------------------------------------------------------------ piezas
def habitacion(k, grad, papel, papel_op=0.55):
    x0, x1 = R[k]
    w = x1 - x0
    return (f'<rect x="{x0}" y="0" width="{w}" height="1700" fill="url(#{grad})"/>'
            f'<rect x="{x0}" y="0" width="{w}" height="1700" fill="url(#{papel})" opacity="{papel_op}"/>'
            f'<rect x="{x0}" y="0" width="{w}" height="34" fill="#fff6ea"/><rect x="{x0}" y="34" width="{w}" height="10" fill="#000" opacity="0.08"/>'
            f'<rect x="{x0}" y="1652" width="{w}" height="48" fill="#fff6ea"/><rect x="{x0}" y="1644" width="{w}" height="8" fill="#000" opacity="0.06"/>')

def suelo_madera(x0, x1):
    return (f'<rect x="{x0}" y="1700" width="{x1 - x0}" height="180" fill="url(#suelo)"/><rect x="{x0}" y="1700" width="{x1 - x0}" height="180" fill="url(#tablas)"/>'
            f'<rect x="{x0}" y="1700" width="{x1 - x0}" height="10" fill="#000" opacity="0.12"/>')

def tabique(x):
    """Pared entre habitaciones con hueco de puerta."""
    return (f'<rect x="{x - 40}" y="0" width="80" height="700" fill="#fff1dc"/><rect x="{x - 40}" y="680" width="80" height="20" fill="#e2cfb3"/>'
            f'<rect x="{x - 56}" y="700" width="16" height="1000" fill="#fbe8cf"/><rect x="{x + 40}" y="700" width="16" height="1000" fill="#fbe8cf"/>')

def ventana2(x, y, w, h, cielo="cieloDia", cortina="#ffd23f", vista=True, idd=""):
    i = f' id="{idd}"' if idd else ""
    s = (f'<rect x="{x - 22}" y="{y - 22}" width="{w + 44}" height="{h + 44}" rx="10" fill="#ffffff"/>'
         f'<rect{i} x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{cielo})"/>')
    if vista:
        s += (f'<circle cx="{x + w * 0.75:.0f}" cy="{y + h * 0.28:.0f}" r="{w * 0.1:.0f}" fill="#fff4b0"/>'
              f'<ellipse cx="{x + w * 0.3:.0f}" cy="{y + h * 0.25:.0f}" rx="{w * 0.16:.0f}" ry="{h * 0.05:.0f}" fill="#fff"/>'
              + "".join(f'<rect x="{x + w * a:.0f}" y="{y + h * (1 - b):.0f}" width="{w * 0.13:.0f}" height="{h * b:.0f}" fill="{c}"/>'
                        for a, b, c in ((0.02, 0.35, "#6c5ce7"), (0.16, 0.5, "#fd79a8"), (0.31, 0.28, "#00b894"), (0.45, 0.6, "#0984e3"), (0.6, 0.38, "#e17055"), (0.75, 0.46, "#a29bfe"), (0.88, 0.3, "#fdcb6e")))
              + "".join(f'<rect x="{x + w * a + 10:.0f}" y="{y + h * (1 - b) + 14 + j * 34:.0f}" width="14" height="16" fill="#fff6b0" opacity="0.9"/>'
                        for a, b in ((0.16, 0.5), (0.45, 0.6), (0.75, 0.46)) for j in range(3)))
    s += (f'<rect x="{x + w / 2 - 8:.0f}" y="{y}" width="16" height="{h}" fill="#ffffff"/><rect x="{x}" y="{y + h * 0.45:.0f}" width="{w}" height="16" fill="#ffffff"/>'
          f'<rect x="{x - 60}" y="{y + h + 22}" width="{w + 120}" height="26" rx="8" fill="#ffffff"/>'
          f'<path d="M{x - 90},{y - 60} L{x + 60},{y - 60} C{x + 30},{y + h * 0.4:.0f} {x + 70},{y + h * 0.8:.0f} {x + 20},{y + h + 40} L{x - 90},{y + h + 40} Z" fill="{cortina}"/>'
          f'<path d="M{x + w + 90},{y - 60} L{x + w - 60},{y - 60} C{x + w - 30},{y + h * 0.4:.0f} {x + w - 70},{y + h * 0.8:.0f} {x + w - 20},{y + h + 40} L{x + w + 90},{y + h + 40} Z" fill="{cortina}"/>'
          f'<path d="M{x - 70},{y - 40} L{x - 70},{y + h + 30}" stroke="#000" stroke-opacity="0.1" stroke-width="16"/>'
          f'<rect x="{x - 130}" y="{y - 78}" width="{w + 260}" height="22" rx="11" fill="#7a4b2a"/>')
    return s

def rayos(x, y, ang, largo, n=3, op=0.13):
    s = ""
    for i in range(n):
        dx = i * 90
        a = math.radians(ang)
        s += (f'<path d="M{x + dx},{y} L{x + dx + 60},{y} L{x + dx + 60 + largo * math.sin(a) + 160:.0f},{y + largo * math.cos(a):.0f} '
              f'L{x + dx + largo * math.sin(a) - 40:.0f},{y + largo * math.cos(a):.0f} Z" fill="#fff8d6" opacity="{op}"/>')
    return s

def marco(x, y, w, h, dibujo, c="#ffffff"):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{c}"/><rect x="{x + 14}" y="{y + 14}" width="{w - 28}" height="{h - 28}" fill="#fffaf0"/>' + dibujo

def montes(x, y, w, h):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#7ad7ff"/><circle cx="{x + w * 0.75:.0f}" cy="{y + h * 0.3:.0f}" r="{h * 0.12:.0f}" fill="#ffd23f"/>'
            f'<path d="M{x},{y + h} L{x + w * 0.35:.0f},{y + h * 0.35:.0f} L{x + w * 0.55:.0f},{y + h * 0.65:.0f} L{x + w * 0.72:.0f},{y + h * 0.45:.0f} L{x + w},{y + h} Z" fill="#2ec4b6"/>'
            f'<path d="M{x + w * 0.35:.0f},{y + h * 0.35:.0f} L{x + w * 0.29:.0f},{y + h * 0.47:.0f} L{x + w * 0.41:.0f},{y + h * 0.47:.0f} Z" fill="#fff"/>')

def libros(x, y, n, alto=110, seed=0):
    r2 = random.Random(seed)
    cols = ["#ff5d8f", "#ffd23f", "#2ec4b6", "#3a86ff", "#ff9f1c", "#8338ec", "#06d6a0", "#ef476f"]
    s, cx = "", x
    for i in range(n):
        w = r2.randint(22, 40); h = alto - r2.randint(0, 30)
        s += f'<rect x="{cx}" y="{y - h}" width="{w}" height="{h}" rx="3" fill="{r2.choice(cols)}"/><rect x="{cx + 4}" y="{y - h + 14}" width="{w - 8}" height="6" fill="#fff" opacity="0.6"/>'
        cx += w + 3
    return s

def maceta(x, y, s=1.0, c="#ff7f50"):
    hojas = "".join(f'<path d="M{x},{y - 10 * s:.0f} C{x + a * s * 0.6:.0f},{y - 110 * s:.0f} {x + a * s:.0f},{y - 160 * s:.0f} {x + a * s * 1.3:.0f},{y - 190 * s:.0f} '
                    f'C{x + a * s * 0.9:.0f},{y - 140 * s:.0f} {x + a * s * 0.3:.0f},{y - 80 * s:.0f} {x},{y - 10 * s:.0f} Z" fill="{g}"/>'
                    for a, g in ((-90, "#1f9d55"), (-40, "#2ecc71"), (10, "#27ae60"), (60, "#2ecc71"), (100, "#1f9d55")))
    return hojas + f'<path d="M{x - 60 * s:.0f},{y} L{x + 60 * s:.0f},{y} L{x + 46 * s:.0f},{y + 110 * s:.0f} L{x - 46 * s:.0f},{y + 110 * s:.0f} Z" fill="{c}"/><rect x="{x - 66 * s:.0f}" y="{y - 6}" width="{132 * s:.0f}" height="{22 * s:.0f}" rx="6" fill="{c}"/>'

def guirnalda(x0, x1, y):
    cols = ["#ff5d8f", "#ffd23f", "#2ec4b6", "#3a86ff", "#ff9f1c"]
    s = f'<path d="M{x0},{y} Q{(x0 + x1) / 2:.0f},{y + 120} {x1},{y}" stroke="#3b2f2f" stroke-width="5" fill="none"/>'
    for i in range(1, 14):
        t = i / 14
        px = x0 + (x1 - x0) * t
        py = (1 - t) ** 2 * y + 2 * (1 - t) * t * (y + 120) + t * t * y
        s += f'<circle class="bombilla" cx="{px:.0f}" cy="{py + 22:.0f}" r="16" fill="{cols[i % 5]}"/><circle cx="{px:.0f}" cy="{py + 22:.0f}" r="30" fill="{cols[i % 5]}" opacity="0.25"/>'
    return s

def lampara_techo(x, c="#ffd23f", largo=260):
    return (f'<rect x="{x - 3}" y="40" width="6" height="{largo}" fill="#3b2f2f"/><path d="M{x - 110},{40 + largo + 110} L{x + 110},{40 + largo + 110} L{x + 60},{40 + largo} L{x - 60},{40 + largo} Z" fill="{c}"/>'
            f'<ellipse cx="{x}" cy="{40 + largo + 112}" rx="70" ry="16" fill="#fff8c4"/>')

def zapatilla(x, y, s=1.0, c="#ff3b5c"):
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M0,0 L0,-60 C0,-110 60,-120 110,-100 C150,-80 180,-50 260,-40 C320,-30 340,-10 340,0 Z" fill="{c}"/>'
            f'<rect x="-6" y="-10" width="352" height="22" rx="10" fill="#ffffff"/><path d="M60,-95 L150,-55 M80,-105 L170,-62 M100,-110 L190,-68" stroke="#ffffff" stroke-width="8" stroke-linecap="round"/>'
            f'<path d="M20,-40 L300,-30" stroke="#ffd23f" stroke-width="10" stroke-linecap="round"/></g>')

def enchufe(x, y):
    return (f'<rect x="{x}" y="{y}" width="70" height="70" rx="12" fill="#ffffff"/><circle cx="{x + 35}" cy="{y + 35}" r="22" fill="#eee"/>'
            f'<circle cx="{x + 27}" cy="{y + 35}" r="5" fill="#555"/><circle cx="{x + 43}" cy="{y + 35}" r="5" fill="#555"/>')

# ================================================================== DORMITORIO (0-2600)
x0, x1 = R["bed"]
b = habitacion("bed", "pBed", "papelBed") + suelo_madera(x0, x1)
b += guirnalda(200, 1500, 150)
b += ventana2(1950, 330, 470, 640, cielo="amanecer", cortina="#ffd23f")
b += rayos(1960, 420, -38, 1500, n=3, op=0.14)
# estantería con libros, planta y trofeo
b += '<rect x="160" y="520" width="560" height="26" rx="6" fill="#7a4b2a"/>' + libros(180, 520, 11, seed=1) + maceta(640, 470, 0.45, "#3a86ff")
b += marco(820, 430, 300, 380, montes(834, 444, 272, 352), "#ffd23f")
b += marco(1180, 480, 220, 280, '<rect x="1194" y="494" width="192" height="252" fill="#2b2d6e"/>' + "".join(f'<circle cx="{1210 + (i * 53) % 170}" cy="{510 + (i * 37) % 220}" r="{3 + i % 3}" fill="#fff"/>' for i in range(14)) + '<path d="M1290,560 l14,28 l30,4 l-22,21 l6,30 l-28,-15 l-28,15 l6,-30 l-22,-21 l30,-4 Z" fill="#ffd23f"/>', "#ffffff")
# armario a la izquierda
b += '<rect x="20" y="760" width="300" height="940" rx="10" fill="#ffb4a2"/><rect x="40" y="790" width="125" height="880" rx="8" fill="#ffc9bd"/><rect x="175" y="790" width="125" height="880" rx="8" fill="#ffc9bd"/>'
b += '<circle cx="150" cy="1220" r="12" fill="#7a4b2a"/><circle cx="190" cy="1220" r="12" fill="#7a4b2a"/>'
# cama: cabecero a la derecha, almohada, sábana (el «desierto») y edredón doblado a los pies
b += '<rect x="1430" y="820" width="90" height="925" rx="22" fill="#7a4b2a"/><rect x="1446" y="850" width="58" height="420" rx="16" fill="#9a5f36"/>'
b += '<rect x="380" y="1300" width="40" height="445" rx="12" fill="#7a4b2a"/>'
b += '<rect x="380" y="1325" width="1060" height="110" rx="10" fill="#9a5f36"/><rect x="380" y="1325" width="1060" height="20" fill="#7a4b2a"/>'
b += '<rect x="390" y="1185" width="1050" height="150" rx="26" fill="#ffffff"/><rect x="390" y="1290" width="1050" height="45" rx="16" fill="#e9eef8"/>'
b += "".join(f'<path d="M{x},1190 C{x + 40},1176 {x + 90},1200 {x + 140},1186" stroke="#d5deee" stroke-width="7" fill="none" stroke-linecap="round"/>' for x in (700, 860, 1000))
b += '<path d="M1120,1190 C1120,1110 1200,1080 1290,1086 C1380,1092 1430,1120 1430,1190 Z" fill="#ffffff"/><path d="M1130,1186 C1220,1170 1340,1170 1428,1186" stroke="#cfe0ff" stroke-width="10" fill="none"/>'
b += '<path d="M1150,1130 L1410,1130 M1145,1155 L1420,1155" stroke="#7ab8ff" stroke-width="10" opacity="0.6"/>'
b += '<path d="M380,1170 C450,1150 600,1150 690,1175 C720,1190 730,1250 720,1340 L700,1520 L380,1520 Z" fill="url(#rayasManta)"/><path d="M690,1175 C720,1190 730,1250 720,1340" stroke="#1d8f85" stroke-width="10" fill="none"/>'
# mesilla con lámpara, libros, vaso y móvil
b += '<rect x="1560" y="1300" width="300" height="445" rx="12" fill="#ffd23f"/><rect x="1560" y="1300" width="300" height="30" rx="10" fill="#ffe680"/>'
b += '<rect x="1585" y="1370" width="250" height="140" rx="10" fill="#ffb627"/><circle cx="1710" cy="1440" r="14" fill="#7a4b2a"/><rect x="1585" y="1540" width="250" height="140" rx="10" fill="#ffb627"/><circle cx="1710" cy="1610" r="14" fill="#7a4b2a"/>'
b += '<rect x="1760" y="1130" width="12" height="170" fill="#3b2f2f"/><path d="M1690,1150 L1840,1150 L1810,1040 L1720,1040 Z" fill="#2ec4b6"/><ellipse cx="1766" cy="1210" rx="200" ry="150" fill="url(#lampG)"/>'
b += '<rect x="1590" y="1255" width="120" height="22" rx="4" fill="#3a86ff"/><rect x="1598" y="1235" width="105" height="22" rx="4" fill="#ff5d8f"/><rect x="1680" y="1200" width="40" height="55" rx="6" fill="#bfe8ff" opacity="0.85"/>'
b += '<rect x="1585" y="1286" width="70" height="14" rx="4" fill="#222"/>'
# alfombra, zapatillas, mochila, guitarra y planta grande
b += '<ellipse cx="1150" cy="1790" rx="620" ry="70" fill="url(#alfombraP)"/><ellipse cx="1150" cy="1790" rx="620" ry="70" fill="none" stroke="#ffffff" stroke-width="12" stroke-dasharray="20 14"/>'
b += zapatilla(1880, 1770, 0.42, "#3a86ff") + zapatilla(2030, 1785, 0.42, "#3a86ff")
b += '<path d="M2210,1745 C2190,1600 2230,1500 2330,1490 C2430,1500 2460,1600 2450,1745 Z" fill="#8338ec"/><rect x="2260" y="1580" width="140" height="90" rx="20" fill="#a66bff"/><path d="M2280,1500 C2290,1440 2380,1440 2390,1500" stroke="#5a22b8" stroke-width="16" fill="none"/>'
b += maceta(2520, 1620, 0.9, "#ff5d8f")
# DESPERTADOR GIGANTE encima de la cama (el gancho): rojo, campanas, cara y agujas
DESP = ('<g id="despG"><rect x="1166" y="1150" width="20" height="40" fill="#3b2f2f" transform="rotate(20 1176 1170)"/><rect x="1314" y="1150" width="20" height="40" fill="#3b2f2f" transform="rotate(-20 1324 1170)"/>'
        '<circle cx="1250" cy="1060" r="112" fill="#ff3b3b"/><circle cx="1250" cy="1060" r="92" fill="#fffaf0"/>'
        + "".join(f'<line x1="{1250 + 80 * math.cos(a * math.pi / 6):.1f}" y1="{1060 + 80 * math.sin(a * math.pi / 6):.1f}" x2="{1250 + 70 * math.cos(a * math.pi / 6):.1f}" y2="{1060 + 70 * math.sin(a * math.pi / 6):.1f}" stroke="#2b2d42" stroke-width="5" stroke-linecap="round"/>' for a in range(12))
        + '<line x1="1250" y1="1060" x2="1250" y2="1002" stroke="#2b2d42" stroke-width="8" stroke-linecap="round"/><line x1="1250" y1="1060" x2="1205" y2="1086" stroke="#2b2d42" stroke-width="10" stroke-linecap="round"/><circle cx="1250" cy="1060" r="9" fill="#ff3b3b"/>'
        '<g id="campL"><path d="M1150,975 C1150,925 1195,915 1215,945 Z" fill="#ffd23f"/><rect x="1165" y="955" width="12" height="30" fill="#3b2f2f" transform="rotate(-35 1171 970)"/></g>'
        '<g id="campR"><path d="M1350,975 C1350,925 1305,915 1285,945 Z" fill="#ffd23f"/><rect x="1323" y="955" width="12" height="30" fill="#3b2f2f" transform="rotate(35 1329 970)"/></g>'
        '<rect x="1240" y="930" width="20" height="22" rx="4" fill="#3b2f2f"/></g>')
H.append(svg(b))
H.append(svg(DESP, "desp"))
H.append(svg('<g id="ring" opacity="0">' + "".join(f'<path d="M{1250 + 140 * math.cos(math.radians(a))},{1040 + 140 * math.sin(math.radians(a))} L{1250 + 175 * math.cos(math.radians(a))},{1040 + 175 * math.sin(math.radians(a))}" stroke="#ffd23f" stroke-width="10" stroke-linecap="round"/>'
                                                for a in (-150, -120, -60, -30, 200, -20 + 360, 160)) + '</g>'))

# ================================================================== PASILLO (2600-4800)
x0, x1 = R["hall"]
h = habitacion("hall", "pHall", "papelHall", 0.5) + suelo_madera(x0, x1)
h += f'<rect x="{x0}" y="1150" width="{x1 - x0}" height="502" fill="#ffffff"/>' + "".join(f'<rect x="{x}" y="1190" width="300" height="420" rx="10" fill="none" stroke="#d6ecff" stroke-width="10"/>' for x in range(x0 + 60, x1 - 200, 360))
h += f'<rect x="{x0}" y="1140" width="{x1 - x0}" height="20" fill="#e3f2ff"/>'
h += lampara_techo(3200, "#ff5d8f") + lampara_techo(4300, "#ffd23f")
h += marco(2780, 480, 240, 300, montes(2794, 494, 212, 272), "#ffd23f") + marco(3080, 420, 200, 200, '<circle cx="3180" cy="520" r="60" fill="#ff5d8f"/><circle cx="3180" cy="520" r="30" fill="#ffd23f"/>', "#ffffff") + marco(3080, 660, 200, 160, '<rect x="3094" y="674" width="172" height="132" fill="#06d6a0"/><path d="M3094,806 L3180,700 L3266,806 Z" fill="#118ab2"/>', "#ff9f1c")
# espejo y perchero con abrigos
h += '<ellipse cx="3560" cy="700" rx="150" ry="230" fill="#ffd23f"/><ellipse cx="3560" cy="700" rx="125" ry="205" fill="#c9f0ff"/><path d="M3480,560 L3540,520 M3470,620 L3580,540" stroke="#ffffff" stroke-width="16" stroke-linecap="round" opacity="0.8"/>'
h += '<rect x="3870" y="420" width="420" height="30" rx="10" fill="#7a4b2a"/>' + "".join(f'<circle cx="{x}" cy="470" r="14" fill="#3b2f2f"/>' for x in (3930, 4080, 4230))
h += '<path d="M3880,470 C3840,600 3850,860 3880,1000 L4000,1000 C4010,860 4000,600 3980,470 Z" fill="#ef476f"/><path d="M4040,470 C4000,620 4010,880 4040,1060 L4140,1060 C4160,880 4150,620 4120,470 Z" fill="#118ab2"/>'
h += '<path d="M4190,470 C4170,560 4180,720 4210,800 L4290,800 C4300,700 4290,560 4270,470 Z" fill="#ffd23f"/><ellipse cx="4230" cy="430" rx="80" ry="30" fill="#06d6a0"/><path d="M4170,430 C4180,370 4280,370 4290,430 Z" fill="#06d6a0"/>'
# mueble zapatero con zapatos, paraguas, planta, enchufe con cable, alfombra
h += '<rect x="3250" y="1380" width="520" height="365" rx="12" fill="#ff9f1c"/><rect x="3250" y="1380" width="520" height="28" rx="8" fill="#ffbf5a"/>' + "".join(f'<rect x="{x}" y="1430" width="230" height="290" rx="10" fill="#ffb347"/><circle cx="{x + 200}" cy="1575" r="10" fill="#7a4b2a"/>' for x in (3270, 3520))
h += zapatilla(3300, 1380, 0.55, "#06d6a0") + zapatilla(3520, 1380, 0.5, "#8338ec")
h += '<rect x="4420" y="1450" width="130" height="295" rx="16" fill="#8338ec"/><path d="M4460,1450 L4440,1100 M4510,1450 L4540,1130" stroke="#ff5d8f" stroke-width="14" stroke-linecap="round"/><path d="M4400,1130 C4420,1060 4490,1060 4500,1110" stroke="#ff5d8f" stroke-width="12" fill="none"/>'
h += maceta(4660, 1600, 0.8, "#3a86ff")
h += enchufe(3840, 1560) + '<path d="M3875,1630 C3870,1700 3950,1730 4100,1740" stroke="#ffffff" stroke-width="12" fill="none" stroke-linecap="round"/>'
h += f'<rect x="{x0 + 40}" y="1750" width="{x1 - x0 - 80}" height="70" rx="10" fill="#ef476f"/><rect x="{x0 + 40}" y="1750" width="{x1 - x0 - 80}" height="70" rx="10" fill="none" stroke="#ffd23f" stroke-width="10" stroke-dasharray="30 20"/>'
# ZAPATILLA GIGANTE junto al camino (para la escala) y el cartelito «COCINA 5,8 km»
h += zapatilla(3010, 1800, 0.95, "#ff3b5c")
h += ('<rect x="2905" y="1665" width="8" height="85" fill="#7a4b2a"/><rect x="2860" y="1640" width="150" height="42" rx="8" fill="#2b2d42"/>'
      '<text x="2935" y="1670" text-anchor="middle" font-family="Inter" font-weight="900" font-size="22" fill="#ffd23f">COCINA ➜</text>'
      '<rect x="2878" y="1688" width="114" height="26" rx="6" fill="#ffd23f"/><text x="2935" y="1708" text-anchor="middle" font-family="Inter" font-weight="900" font-size="19" fill="#2b2d42">5,8 km</text>')
# bolas de polvo (se convierten en ácaros)
h += "".join(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 0.7:.0f}" fill="#cfc4b8" opacity="0.9"/>' for x, y, r in ((3600, 1772, 26), (3800, 1790, 18)))
H.append(svg(h))

# ================================================================== COMEDOR (4800-7000)
x0, x1 = R["din"]
d = habitacion("din", "pDin", "papelDin") + suelo_madera(x0, x1)
d += ventana2(5050, 330, 520, 620, cortina="#ef476f")
d += rayos(5070, 420, -30, 1300, n=3, op=0.12)
d += marco(6000, 420, 380, 260, '<rect x="6014" y="434" width="352" height="232" fill="#ff5d8f"/><circle cx="6120" cy="550" r="70" fill="#ffd23f"/><circle cx="6260" cy="520" r="50" fill="#06d6a0"/>', "#3a86ff")
d += '<rect x="6480" y="560" width="400" height="24" rx="6" fill="#7a4b2a"/>' + "".join(f'<circle cx="{x}" cy="510" r="48" fill="#ffffff" stroke="{c}" stroke-width="10"/>' for x, c in ((6540, "#3a86ff"), (6650, "#ff5d8f"), (6760, "#06d6a0")))
d += lampara_techo(5950, "#ef476f", 420)
# mesa: tablero a y=1050, patas, mantel de camino de mesa
d += '<rect x="5300" y="1050" width="1320" height="44" rx="10" fill="url(#madera2)"/><rect x="5300" y="1050" width="1320" height="12" rx="6" fill="#e39a62"/>'
d += '<rect x="5360" y="1094" width="44" height="651" fill="#9a5a2c"/><rect x="6516" y="1094" width="44" height="651" fill="#9a5a2c"/><rect x="5420" y="1094" width="1080" height="40" fill="#8a4f24"/>'
d += '<rect x="5650" y="1040" width="620" height="16" fill="#3a86ff"/><rect x="5650" y="1040" width="620" height="16" fill="url(#papelHall)" opacity="0.5"/>'
# sillas
for cx, s_ in ((5150, 1), (6760, -1)):
    d += f'<rect x="{cx - 120}" y="1260" width="240" height="34" rx="10" fill="#06d6a0"/><rect x="{cx - 110}" y="1294" width="22" height="451" fill="#7a4b2a"/><rect x="{cx + 88}" y="1294" width="22" height="451" fill="#7a4b2a"/>'
    d += f'<rect x="{cx - 120 * s_ - 11}" y="800" width="22" height="470" fill="#7a4b2a"/><rect x="{min(cx - 120 * s_, cx - 120 * s_ + 20 * s_) - (0 if s_ > 0 else 0)}" y="820" width="22" height="0" fill="none"/>'
# en la mesa: plato con tostada, frutero, jarrón con flores, azucarero, salero, taza, granos de arroz
d += '<ellipse cx="5480" cy="1046" rx="130" ry="18" fill="#ffffff"/><rect x="5420" y="1006" width="120" height="34" rx="10" fill="#e8a54b"/><rect x="5420" y="1006" width="120" height="10" rx="5" fill="#c97b2f"/>'
d += '<path d="M5640,1046 L5840,1046 C5830,980 5650,980 5640,1046 Z" fill="#ff5d8f"/><circle cx="5690" cy="985" r="38" fill="#ef233c"/><circle cx="5760" cy="975" r="40" fill="#8ac926"/><path d="M5700,960 C5740,900 5820,920 5830,980" stroke="#ffd23f" stroke-width="26" fill="none" stroke-linecap="round"/>'
d += '<path d="M5935,1046 L6005,1046 L6015,930 L5925,930 Z" fill="#3a86ff"/>' + "".join(f'<path d="M5970,930 C{5970 + a},860 {5970 + a * 1.4},800 {5970 + a * 1.5},760" stroke="#2ecc71" stroke-width="7" fill="none"/><circle cx="{5970 + a * 1.5}" cy="760" r="26" fill="{c}"/><circle cx="{5970 + a * 1.5}" cy="760" r="10" fill="#ffd23f"/>'
                                                                                         for a, c in ((-50, "#ff5d8f"), (0, "#ff9f1c"), (45, "#8338ec"), (-20, "#ef476f")))
d += '<rect x="6080" y="975" width="100" height="72" rx="20" fill="#ffffff"/><rect x="6070" y="960" width="120" height="22" rx="8" fill="#06d6a0"/><rect x="6118" y="944" width="24" height="18" rx="6" fill="#06d6a0"/>'
d += '<rect x="6210" y="985" width="34" height="62" rx="10" fill="#ffffff"/><rect x="6210" y="985" width="34" height="16" rx="6" fill="#bbb"/><rect x="6250" y="985" width="34" height="62" rx="10" fill="#2b2d42"/>'
d += '<rect x="6300" y="990" width="70" height="56" rx="10" fill="#ef476f"/><path d="M6370,1000 C6400,1000 6400,1035 6370,1035" stroke="#ef476f" stroke-width="10" fill="none"/>'
d += "".join(f'<ellipse cx="{x}" cy="1044" rx="12" ry="6" fill="#fffaf0" stroke="#e0d3b0" stroke-width="2" transform="rotate({a} {x} 1044)"/>' for x, a in ((6400, 10), (6420, -15), (6585, 25)))
d += '<ellipse cx="6000" cy="1800" rx="800" ry="65" fill="#118ab2"/><ellipse cx="6000" cy="1800" rx="800" ry="65" fill="none" stroke="#ffd23f" stroke-width="10"/>'
d += maceta(4950, 1600, 0.85, "#ffd23f")
H.append(svg(d))
H.append(svg('<g id="arroz2"><ellipse cx="0" cy="0" rx="44" ry="17" fill="#fffaf0" stroke="#d9c79a" stroke-width="4"/><path d="M-30,-6 C-10,-12 10,-12 30,-6" stroke="#ffffff" stroke-width="6" fill="none" stroke-linecap="round"/></g>', "arroz"))
H.append(svg('<g id="aire2" opacity="0">' + "".join(f'<path d="M{dx},0 L{dx},-90" stroke="#ffffff" stroke-width="7" stroke-linecap="round" stroke-dasharray="20 14"/>' for dx in (-60, -20, 20, 60)) + '</g>', "aire"))

# ================================================================== COCINA (7000-9800)
x0, x1 = R["kit"]
k = habitacion("kit", "pKit", "papelDin", 0.0)
k += f'<rect x="{x0}" y="1700" width="{x1 - x0}" height="180" fill="url(#damero)"/><rect x="{x0}" y="1700" width="{x1 - x0}" height="10" fill="#000" opacity="0.12"/>'
k += '<rect x="7620" y="660" width="2140" height="440" fill="url(#azulejo)"/>'
k += ventana2(8720, 250, 460, 360, cortina="#ff9f1c")
k += rayos(8730, 320, -25, 900, n=2, op=0.12)
# muebles altos con tarros
k += '<rect x="7640" y="200" width="900" height="380" rx="10" fill="#ff9f1c"/>' + "".join(f'<rect x="{x}" y="220" width="200" height="340" rx="8" fill="#ffb347"/><rect x="{x + 85}" y="510" width="30" height="12" rx="6" fill="#7a4b2a"/>' for x in (7660, 7880, 8100, 8320))
k += '<rect x="9300" y="560" width="440" height="22" rx="6" fill="#7a4b2a"/>' + "".join(f'<rect x="{x}" y="{560 - hh}" width="70" height="{hh}" rx="12" fill="{c}" opacity="0.95"/><rect x="{x - 4}" y="{560 - hh - 14}" width="78" height="20" rx="6" fill="#7a4b2a"/>'
                                                                                  for x, hh, c in ((9320, 120, "#ffd23f"), (9410, 150, "#ef476f"), (9500, 110, "#8ac926"), (9590, 140, "#3a86ff")))
# nevera con imanes y dibujo
k += '<rect x="7060" y="420" width="500" height="1325" rx="30" fill="#bde0fe"/><rect x="7060" y="900" width="500" height="14" fill="#8fbfe6"/><rect x="7500" y="560" width="22" height="260" rx="10" fill="#ffffff"/><rect x="7500" y="980" width="22" height="300" rx="10" fill="#ffffff"/>'
k += '<rect x="7120" y="500" width="190" height="230" fill="#ffffff" transform="rotate(-6 7215 615)"/><circle cx="7190" cy="590" r="40" fill="#ffd23f"/><path d="M7140,700 L7200,640 L7260,700 Z" fill="#06d6a0" transform="rotate(-6 7215 615)"/>'
k += "".join(f'<circle cx="{x}" cy="{y}" r="22" fill="{c}"/>' for x, y, c in ((7350, 520, "#ef476f"), (7420, 620, "#8338ec"), (7340, 700, "#ffd23f"), (7180, 1050, "#06d6a0"), (7400, 1120, "#ff9f1c")))
k += '<rect x="7300" y="980" width="150" height="110" fill="#fffaf0" transform="rotate(5 7375 1035)"/><path d="M7320,1010 L7430,1010 M7320,1040 L7410,1040 M7320,1070 L7420,1070" stroke="#3a86ff" stroke-width="6"/>'
# encimera, horno, fregadero y grifo
k += '<rect x="7600" y="1100" width="2180" height="44" rx="8" fill="#f1f3f8"/><rect x="7600" y="1100" width="2180" height="12" rx="6" fill="#ffffff"/>'
k += '<rect x="7610" y="1144" width="2160" height="560" fill="#ef476f"/>' + "".join(f'<rect x="{x}" y="1170" width="250" height="500" rx="10" fill="#ff6b8a"/><rect x="{x + 100}" y="1200" width="50" height="14" rx="7" fill="#ffd23f"/>' for x in (8240, 8510, 9050, 9320))
k += '<rect x="7640" y="1170" width="560" height="500" rx="12" fill="#2b2d42"/><rect x="7680" y="1260" width="480" height="300" rx="16" fill="#ff9f1c" opacity="0.85"/><rect x="7680" y="1260" width="480" height="300" rx="16" fill="none" stroke="#c0c6d6" stroke-width="10"/><rect x="7700" y="1190" width="440" height="22" rx="10" fill="#c0c6d6"/>'
k += '<rect x="7610" y="1704" width="2160" height="41" fill="#1d1e2c"/>'
k += '<rect x="8740" y="1096" width="420" height="20" rx="8" fill="#b9c3d4"/>'
k += '<path d="M9080,1100 L9080,880 C9080,800 8960,790 8930,850 L8930,880" stroke="url(#metal)" stroke-width="38" fill="none" stroke-linecap="round"/><rect x="9040" y="1060" width="80" height="44" rx="10" fill="#c0c6d6"/><rect x="9118" y="1000" width="70" height="20" rx="8" fill="#c0c6d6"/>'
k += '<rect x="8908" y="872" width="44" height="22" rx="6" fill="#9fb3c8"/>'
# cosas encima: tostadora, tabla con pan, frutero, jabón, esponja, plantas
k += '<rect x="8230" y="960" width="200" height="140" rx="40" fill="#ef233c"/><rect x="8260" y="940" width="40" height="30" rx="8" fill="#2b2d42"/><rect x="8340" y="940" width="40" height="30" rx="8" fill="#2b2d42"/><rect x="8430" y="1020" width="26" height="40" rx="8" fill="#2b2d42"/>'
k += '<rect x="8480" y="1080" width="230" height="20" rx="8" fill="#c97b45"/><path d="M8500,1080 C8500,990 8560,960 8600,960 C8650,960 8700,990 8700,1080 Z" fill="#e8a54b"/><path d="M8540,1000 L8560,1040 M8600,990 L8620,1040 M8650,1000 L8665,1040" stroke="#c97b2f" stroke-width="10" stroke-linecap="round"/>'
k += '<rect x="9240" y="990" width="70" height="110" rx="18" fill="#3a86ff"/><rect x="9258" y="960" width="34" height="34" rx="6" fill="#ffffff"/><rect x="9320" y="1070" width="90" height="30" rx="8" fill="#ffd23f"/><rect x="9320" y="1060" width="90" height="12" rx="6" fill="#06d6a0"/>'
k += maceta(9560, 1010, 0.6, "#ffd23f") + maceta(9690, 1010, 0.5, "#3a86ff")
k += lampara_techo(8200, "#2b2d42", 120)
H.append(svg(k))
# migas en el suelo y LA MIGA-ROCA
H.append(svg('<g id="miga2"><path d="M-110,0 C-120,-90 -60,-170 10,-165 C90,-160 130,-90 120,0 Z" fill="url(#migaG2)"/>'
             + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 0.7:.0f}" fill="#c97b2f" opacity="0.7"/>' for x, y, r in ((-50, -110, 14), (30, -80, 18), (-20, -40, 12), (70, -40, 10), (0, -140, 8)))
             + '<path d="M-90,-60 C-80,-120 -30,-150 10,-150" stroke="#fff3d6" stroke-width="10" fill="none" stroke-linecap="round" opacity="0.8"/></g>', "miga"))
H.append(svg("".join(f'<ellipse cx="{x}" cy="{1750 + (x % 3) * 6}" rx="{8 + x % 7}" ry="6" fill="#e8a54b"/>' for x in (7640, 7700, 7960, 8040, 8120))))
H.append(svg('<g id="gota2"><path d="M0,-70 C24,-30 40,-5 40,18 C40,42 22,58 0,58 C-22,58 -40,42 -40,18 C-40,-5 -24,-30 0,-70 Z" fill="url(#gotaG2)" stroke="#5ab8ff" stroke-width="3"/><ellipse cx="-12" cy="10" rx="8" ry="14" fill="#fff" opacity="0.8"/></g>', "gota"))
H.append(svg('<g id="charco2" opacity="0"><path d="M-95,0 C-100,-120 -60,-170 0,-170 C60,-170 100,-120 95,0 Z" fill="url(#gotaG2)" stroke="#5ab8ff" stroke-width="4"/><ellipse cx="-45" cy="-110" rx="16" ry="30" fill="#fff" opacity="0.75"/></g>', "charco"))
H.append(svg('<g id="vaho2" opacity="0">' + "".join(f'<circle cx="{i * 14}" cy="{-i * 10}" r="{6 + i * 3}" fill="#ffffff" opacity="{0.8 - i * 0.12:.2f}"/>' for i in range(5)) + '</g>', "vaho"))

# ================================================================== SALÓN (9800-12900)
x0, x1 = R["liv"]
l = habitacion("liv", "pLiv", "papelLiv", 0.45) + suelo_madera(x0, x1)
l += ventana2(12230, 300, 460, 760, cortina="#ffd23f", idd="ventLiv")
l += f'<g id="ventNoche" opacity="0"><rect x="12230" y="300" width="460" height="760" fill="url(#cieloNoche)"/>' + "".join(f'<circle cx="{12250 + (i * 71) % 420}" cy="{320 + (i * 53) % 400}" r="{2 + i % 3}" fill="#fff"/>' for i in range(22)) + '<circle cx="12560" cy="420" r="50" fill="#fff6c9"/><circle cx="12580" cy="405" r="44" fill="#0b1046"/>' + "".join(f'<rect x="{12230 + int(460 * a)}" y="{300 + int(760 * (1 - bb))}" width="{int(460 * 0.13)}" height="{int(760 * bb)}" fill="#1b1f5e"/>' for a, bb in ((0.02, 0.35), (0.16, 0.5), (0.31, 0.28), (0.45, 0.6), (0.6, 0.38), (0.75, 0.46), (0.88, 0.3))) + '<rect x="12238" y="300" width="0" height="0"/></g>'
l += '<rect x="12441" y="300" width="16" height="760" fill="#ffffff"/><rect x="12230" y="636" width="460" height="16" fill="#ffffff"/>'
# estantería llena (izquierda)
l += '<rect x="9880" y="420" width="520" height="1325" rx="10" fill="#7a4b2a"/>' + "".join(f'<rect x="9900" y="{y}" width="480" height="20" fill="#5e391f"/>' for y in (700, 980, 1260, 1540))
l += libros(9910, 700, 12, seed=3) + libros(9910, 980, 12, seed=4) + libros(9910, 1260, 7, seed=5) + maceta(10300, 1180, 0.5, "#ffd23f") + libros(9910, 1540, 12, seed=6)
l += '<circle cx="10050" cy="590" r="70" fill="#3a86ff"/><path d="M10010,560 C10040,520 10090,530 10100,580" stroke="#8ac926" stroke-width="22" fill="none"/>'
# cuadros
l += marco(10560, 380, 340, 260, '<rect x="10574" y="394" width="312" height="232" fill="#06d6a0"/><path d="M10574,626 C10660,520 10760,580 10886,470 L10886,626 Z" fill="#118ab2"/><circle cx="10640" cy="460" r="30" fill="#ffd23f"/>', "#ffffff")
l += marco(10560, 700, 160, 200, '<rect x="10574" y="714" width="132" height="172" fill="#ff5d8f"/>', "#ffd23f") + marco(10740, 700, 160, 200, '<rect x="10754" y="714" width="132" height="172" fill="#ffd23f"/><circle cx="10820" cy="800" r="40" fill="#ef476f"/>', "#ff5d8f")
# RELOJ DE PARED grande encima del sofá
l += ('<circle cx="11600" cy="640" r="190" fill="#ffd23f"/><circle cx="11600" cy="640" r="160" fill="#fffaf0"/>'
      + "".join(f'<line x1="{11600 + 140 * math.cos(a * math.pi / 6):.1f}" y1="{640 + 140 * math.sin(a * math.pi / 6):.1f}" x2="{11600 + 118 * math.cos(a * math.pi / 6):.1f}" y2="{640 + 118 * math.sin(a * math.pi / 6):.1f}" stroke="#2b2d42" stroke-width="10" stroke-linecap="round"/>' for a in range(12))
      + '<text x="11600" y="545" text-anchor="middle" font-family="Inter" font-weight="900" font-size="54" fill="#2b2d42">12</text>')
# sofá, cojines, manta
l += '<rect x="11000" y="1080" width="1180" height="330" rx="60" fill="#ff5d8f"/><rect x="10960" y="1250" width="140" height="350" rx="50" fill="#ef476f"/><rect x="12080" y="1250" width="140" height="350" rx="50" fill="#ef476f"/>'
l += '<rect x="11080" y="1360" width="1020" height="140" rx="40" fill="#ff7aa5"/><rect x="11000" y="1490" width="1180" height="110" rx="20" fill="#ef476f"/>'
l += '<rect x="11120" y="1180" width="220" height="190" rx="40" fill="#ffd23f" transform="rotate(-8 11230 1275)"/><rect x="11820" y="1180" width="220" height="190" rx="40" fill="#06d6a0" transform="rotate(8 11930 1275)"/>'
l += '<path d="M11500,1100 L11720,1100 L11760,1500 L11470,1500 Z" fill="url(#rayasManta)" opacity="0.95"/>'
l += '<rect x="11030" y="1600" width="26" height="145" fill="#3b2f2f"/><rect x="12120" y="1600" width="26" height="145" fill="#3b2f2f"/>'
l += '<rect x="11056" y="1600" width="1064" height="145" fill="#1c1240"/>'
# bajos del sofá: moneda, pieza de LEGO, calcetín perdido, pelusa
l += '<ellipse cx="11520" cy="1736" rx="42" ry="12" fill="#c0c6d6"/><ellipse cx="11520" cy="1730" rx="42" ry="12" fill="#e6ebf5"/>'
l += '<rect x="11700" y="1700" width="80" height="45" rx="6" fill="#ef233c"/>' + "".join(f'<rect x="{11706 + i * 26}" y="1688" width="18" height="14" rx="4" fill="#ef233c"/>' for i in range(3))
l += '<path d="M11850,1745 L11850,1690 C11850,1670 11880,1670 11880,1690 L11880,1720 L11950,1720 C11970,1720 11970,1745 11950,1745 Z" fill="#06d6a0"/>'
l += '<ellipse cx="11980" cy="1735" rx="40" ry="16" fill="#9a8fb3"/>'
# lámpara de pie, mesa baja con taza y mando, alfombra y planta grande
l += '<rect x="12260" y="1100" width="16" height="645" fill="#2b2d42"/><ellipse cx="12268" cy="1745" rx="70" ry="14" fill="#2b2d42"/><path d="M12180,1110 L12360,1110 L12320,980 L12220,980 Z" fill="#ffd23f"/>'
l += '<ellipse id="luzLamp" cx="12268" cy="1200" rx="300" ry="260" fill="url(#lampG)" opacity="0"/>'
l += '<ellipse cx="11450" cy="1810" rx="900" ry="70" fill="url(#alfombraP)"/>'
l += maceta(12780, 1580, 1.1, "#3a86ff")
H.append(svg(l))
H.append(f'<div id="noche" style="position:absolute;left:{x0 - 60}px;top:-80px;width:{x1 - x0 + 120}px;height:2000px;background:#120c4a;opacity:0;mix-blend-mode:multiply"></div>')
H.append(svg('<g id="aguH"><line x1="11600" y1="640" x2="11600" y2="560" stroke="#2b2d42" stroke-width="18" stroke-linecap="round"/></g><g id="aguM"><line x1="11600" y1="640" x2="11600" y2="510" stroke="#ef233c" stroke-width="10" stroke-linecap="round"/></g><circle cx="11600" cy="640" r="16" fill="#2b2d42"/>'))

# tabiques entre habitaciones (encima de todo lo de cada sala)
H.append(svg("".join(tabique(R[k][1]) for k in ("bed", "hall", "din", "kit"))))

# ------------------------------------------------------------------ personajes diminutos
def mini(pid, x, yf, s=S_MINI):
    J(f'tl.set("#{pid}-w", {{scale:{s}, transformOrigin:"500px 1702px"}}, 0);')
    return f'<div id="{pid}-w" style="position:absolute;left:{x - 500}px;top:{yf - 1702}px;width:1000px;height:1800px">' + personaje(pid, cm=7).replace("{x}", "0") + perfil(pid) + '</div>'

# ácaros (bolas de polvo con patas)
def acaro2(aid, x, y, s=1.0):
    patas = "".join(f'<path d="M{dx * 40},{10 + abs(dx) * 4} q{dx * 40},-30 {dx * 70},30" stroke="#8a7a66" stroke-width="9" fill="none" stroke-linecap="round"/>' for dx in (-1, -0.6, 0.6, 1))
    pelos = "".join(f'<path d="M{rnd.uniform(-70, 70):.0f},{rnd.uniform(-60, 10):.0f} l{rnd.uniform(-14, 14):.0f},-22" stroke="#b9a88f" stroke-width="4" stroke-linecap="round"/>' for _ in range(14))
    return (f'<svg id="{aid}" style="position:absolute;left:{x}px;top:{y}px;overflow:visible" width="10" height="10"><g transform="scale({s})">'
            f'<g class="patas">{patas}</g><ellipse cx="0" cy="-10" rx="90" ry="70" fill="#d9cbb3"/><ellipse cx="-20" cy="-35" rx="40" ry="22" fill="#efe4d0"/>{pelos}'
            f'<circle cx="-28" cy="-6" r="11" fill="#1d1b26"/><circle cx="22" cy="-6" r="11" fill="#1d1b26"/><circle cx="-25" cy="-9" r="4" fill="#fff"/><circle cx="25" cy="-9" r="4" fill="#fff"/></g></svg>')

# gato (de frente, sentado) y su pata
GATO = ('<svg id="gato" style="position:absolute;left:0;top:0;overflow:visible" width="1" height="1"><g transform="translate(10380 0)"><g id="gatoG">'
        '<path id="cola" d="M150,1700 C320,1690 360,1560 300,1440" stroke="#ff9f1c" stroke-width="50" fill="none" stroke-linecap="round"/>'
        '<ellipse cx="0" cy="1500" rx="220" ry="250" fill="#ff9f1c"/><ellipse cx="0" cy="1540" rx="120" ry="170" fill="#ffe0b3"/>'
        '<ellipse cx="-110" cy="1720" rx="80" ry="40" fill="#ff9f1c"/><ellipse cx="110" cy="1720" rx="80" ry="40" fill="#ff9f1c"/>'
        + "".join(f'<path d="M{s * 80},{1240 + k * 30} L{s * 150},{1260 + k * 40}" stroke="#e07b00" stroke-width="16" stroke-linecap="round"/>' for s in (-1, 1) for k in range(3))
        + '<path d="M-170,1110 L-150,900 L-50,1010 Z M170,1110 L150,900 L50,1010 Z" fill="#ff9f1c"/><path d="M-150,1080 L-140,950 L-80,1020 Z M150,1080 L140,950 L80,1020 Z" fill="#ffb3c6"/>'
        '<ellipse cx="0" cy="1140" rx="200" ry="170" fill="#ffad33"/>'
        '<ellipse cx="-75" cy="1120" rx="42" ry="50" fill="#c6f432"/><ellipse cx="75" cy="1120" rx="42" ry="50" fill="#c6f432"/>'
        '<ellipse class="pup" cx="-75" cy="1120" rx="12" ry="42" fill="#1d1b26"/><ellipse class="pup" cx="75" cy="1120" rx="12" ry="42" fill="#1d1b26"/>'
        '<circle cx="-85" cy="1100" r="8" fill="#fff"/><circle cx="65" cy="1100" r="8" fill="#fff"/>'
        '<path d="M-18,1190 L18,1190 L0,1210 Z" fill="#ff6b8a"/><path d="M-36,1228 C-18,1244 0,1232 0,1212 C0,1232 18,1244 36,1228" stroke="#7a3b10" stroke-width="7" fill="none" stroke-linecap="round"/>'
        + "".join(f'<path d="M{s * 40},{1205 + k * 16} L{s * 230},{1180 + k * 34}" stroke="#ffffff" stroke-width="5"/>' for s in (-1, 1) for k in range(3))
        + '<path d="M-60,1000 L-40,1050 M0,990 L0,1045 M60,1000 L40,1050" stroke="#e07b00" stroke-width="14" stroke-linecap="round"/>'
        '</g></g></svg>')

# EDIFICIO DE 50 PISOS (bien estructurado: 50 plantas contadas, ventanas, portal, azotea y antena)
def edificio(x, ybase, alto, ancho=200):
    pl = alto / 52.0
    s = f'<rect x="{x - 14}" y="{ybase - alto - 14}" width="{ancho + 28}" height="{alto + 28}" rx="16" fill="#ffffff" opacity="0.92"/>'
    s += f'<rect x="{x}" y="{ybase - alto + pl * 2:.1f}" width="{ancho}" height="{alto - pl * 2:.1f}" fill="#2b4c8c"/>'
    for i in range(50):
        y = ybase - pl * (i + 1)
        s += f'<rect x="{x}" y="{y:.1f}" width="{ancho}" height="{pl * 0.12:.2f}" fill="#1b3366"/>'
        for j in range(6):
            lit = ((i * 7 + j * 3) % 5) < 2
            s += f'<rect x="{x + 10 + j * (ancho - 20) / 6:.1f}" y="{y + pl * 0.22:.1f}" width="{(ancho - 20) / 6 - 6:.1f}" height="{pl * 0.6:.1f}" fill="{"#ffe066" if lit else "#9fd3ff"}"/>'
    s += f'<rect x="{x + ancho * 0.35:.0f}" y="{ybase - pl * 1.6:.1f}" width="{ancho * 0.3:.0f}" height="{pl * 1.6:.1f}" fill="#ffd23f"/>'
    s += f'<rect x="{x - 8}" y="{ybase - alto + pl * 1.2:.1f}" width="{ancho + 16}" height="{pl:.1f}" fill="#1b3366"/><rect x="{x + ancho / 2 - 3:.0f}" y="{ybase - alto - pl * 3:.1f}" width="6" height="{pl * 4:.1f}" fill="#ff3b3b"/><circle cx="{x + ancho / 2:.0f}" cy="{ybase - alto - pl * 3:.1f}" r="7" fill="#ff3b3b"/>'
    for n in (10, 20, 30, 40, 50):
        y = ybase - pl * n
        s += f'<path d="M{x + ancho + 6},{y + pl * 0.5:.1f} L{x + ancho + 26},{y + pl * 0.5:.1f}" stroke="#ffffff" stroke-width="3"/><text x="{x + ancho + 30}" y="{y + pl * 0.5 + 9:.1f}" font-family="Inter" font-weight="900" font-size="26" fill="#ffffff" stroke="#2b2d42" stroke-width="5" paint-order="stroke">{n}</text>'
    s += f'<rect x="{x - 10}" y="{ybase - alto - pl * 9:.1f}" width="{ancho + 20}" height="{pl * 4.5:.1f}" rx="10" fill="#ffd23f"/><text x="{x + ancho / 2:.0f}" y="{ybase - alto - pl * 5.8:.1f}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="34" fill="#2b2d42">50 PISOS</text>'
    return s

# --- colocación de personajes y objetos que se animan (orden = profundidad)
YB = 1188         # sábana de la cama
YT = 1050         # tablero de la mesa
YC = 1100         # encimera
H.append(mini("p0", 1080, YB))
H.append(acaro2("acaro1", 3470, 1790, 0.42)); H.append(acaro2("acaro2", 3530, 1800, 0.34))
H.append(mini("p1", 3250, FL))
H.append(mini("p2", 6480, YT))
H.append(mini("p3", 7700, FL))
H.append(mini("p4", 8930, YC))
H.append(gato_svg())
H.append(mini("p5", 10800, FL))
H.append(svg(edificio(11000, FL, 780, 160), "edif"))
# cinta métrica (crecer) y hormiga real
cm_px = 1000 / 175.0
cinta = (f'<rect x="-46" y="-1060" width="92" height="1060" rx="10" fill="#ffd23f"/><rect x="-46" y="-1060" width="14" height="1060" fill="#ffb627"/>'
         + "".join(f'<line x1="{-46 + (0 if c % 10 else 0)}" y1="{-c * cm_px:.1f}" x2="{-46 + (40 if c % 10 == 0 else (26 if c % 5 == 0 else 14))}" y2="{-c * cm_px:.1f}" stroke="#2b2d42" stroke-width="{4 if c % 10 == 0 else 2}"/>' for c in range(0, 181))
)
H.append(f'<svg id="cinta" style="position:absolute;left:11330px;top:{FL}px;overflow:visible" width="1" height="1"><g id="cintaG">{cinta}</g></svg>')

H.append(f'<svg id="hormiga" style="position:absolute;left:11760px;top:{FL + 4}px;overflow:visible" width="10" height="10">'
         '<ellipse cx="0" cy="0" rx="9" ry="7" fill="#1d1b26"/><ellipse cx="14" cy="-1" rx="6" ry="5" fill="#1d1b26"/><ellipse cx="-14" cy="0" rx="11" ry="8" fill="#1d1b26"/>'
         '<path d="M-6,4 l-8,9 M2,5 l0,10 M8,4 l8,9 M-6,-4 l-8,-9 M2,-5 l0,-10 M8,-4 l8,-9 M18,-4 l8,-10 M18,-4 l10,-4" stroke="#1d1b26" stroke-width="2"/></svg>')
# regla para «mides 3 mm» (1 mm = 30 px a esta escala)
regla2 = (f'<rect x="0" y="-110" width="60" height="120" rx="6" fill="#ffd23f"/>'
          + "".join(f'<line x1="0" y1="{-k * 30:.0f}" x2="{26 if k % 1 == 0 else 14}" y2="{-k * 30:.0f}" stroke="#2b2d42" stroke-width="{3 if k % 1 == 0 else 1.5}"/>' for k in [i / 2 for i in range(0, 8)])
          + "".join(f'<text x="30" y="{-k * 30 + 5:.0f}" font-family="Inter" font-weight="900" font-size="13" fill="#2b2d42">{k}mm</text>' for k in range(1, 4)))
H.append(f'<svg id="regla" style="position:absolute;left:1132px;top:{YB}px;overflow:visible;opacity:0" width="1" height="1">{regla2}</svg>')
# etiqueta «TÚ» con flecha (en el plano abierto del principio)
H.append(f'<div id="tuTag" style="position:absolute;left:{1080 - 160}px;top:{YB - 470}px;width:320px;opacity:0;text-align:center">'
         '<div style="display:inline-block;background:#ffd23f;color:#2b2d42;font:900 84px Inter;padding:10px 34px;border-radius:30px;box-shadow:0 12px 0 #2b2d42">TÚ</div>'
         '<svg width="320" height="230" style="display:block;overflow:visible"><path d="M160,20 L160,200" stroke="#ffd23f" stroke-width="22" stroke-linecap="round"/><path d="M110,150 L160,210 L210,150" stroke="#ffd23f" stroke-width="22" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></div>')

# tarjetas (en el mundo, nítidas)
H.append(f'<div id="termo" class="card" style="left:7820px;top:1430px;width:300px;padding:18px 22px;opacity:0"><div class="card-top" style="font-size:24px">TU CUERPO</div>'
         '<div style="display:flex;align-items:center;gap:14px"><svg width="40" height="110" viewBox="0 0 40 110"><rect x="12" y="4" width="16" height="80" rx="8" fill="#e3e8f0"/><rect id="mercurio" x="15" y="44" width="10" height="40" rx="5" fill="#ef233c"/><circle cx="20" cy="92" r="16" fill="#ef233c"/></svg>'
         '<div class="card-big" style="font-size:46px;color:#3a86ff">PIERDE<br>CALOR</div></div></div>')

for pid in ("p0", "p1", "p2", "p3", "p4", "p5"):
    vida(pid)

# ------------------------------------------------------------------ helpers de cámara
def C(x, yf, z=6.0):
    return (x, yf - 45 - 190 / z, z)

def camC(t, x, yf, z=6.0, dur=1.0, ease="power3.inOut"):
    cx, cy, cz = C(x, yf, z)
    cam(t, cx, cy, cz, dur=dur, ease=ease)

def camset(t, x, y, z):
    J(f'tl.set("#world", {{x:{540 - x * z:.1f}, y:{960 - y * z:.1f}, scale:{z}}}, {t:.2f});')

def viaje(t, wide, dest, d1=0.9, hold=0.35, d2=1.0):
    """Viaje por la casa: se abre el plano (se ve la casa) y se acerca al nuevo sitio."""
    cam(t, *wide, dur=d1, ease="power2.inOut")
    cam(t + d1 + hold, *dest, dur=d2, ease="power2.inOut")
    FX_EV.append(("suave", t + 0.1))

def barrido(t, dest):
    """Transición: tres franjas de colores en diagonal cruzan la pantalla con una hormiguita corriendo.
    El cambio de plano ocurre cuando la franja grande tapa todo."""
    J(f'tl.fromTo("#wipe", {{x:1900}}, {{x:-4300, duration:1.0, ease:"sine.inOut", immediateRender:false}}, {t - 0.5:.2f});')
    camset(t, *dest)
    FX_EV.append(("suave", t - 0.5))

def andar(pid, t, dx, dur, pasos):
    J(f'tl.to("#{pid}-w", {{x:"+={dx}", duration:{dur}, ease:"none"}}, {t:.2f});')
    for k in range(pasos):
        tk = t + k * dur / pasos
        pie = "legL" if k % 2 == 0 else "legR"
        J(f'tl.to("#{pid}-{pie}", {{y:-30, duration:{dur / pasos / 2:.3f}, yoyo:true, repeat:1, ease:"sine.inOut"}}, {tk:.2f});')
        J(f'tl.to("#{pid}-up", {{y:-8, duration:{dur / pasos / 2:.3f}, yoyo:true, repeat:1, ease:"sine.inOut"}}, {tk:.2f});')

def brazos(pid, t, rotL, rotR, hold, ida=0.35):
    J(f'tl.to("#{pid}-armLg", {{rotation:{rotL}, duration:{ida}, ease:"back.out(1.4)", svgOrigin:"356 985"}}, {t:.2f}); tl.to("#{pid}-armRg", {{rotation:{rotR}, duration:{ida}, ease:"back.out(1.4)", svgOrigin:"644 985"}}, {t:.2f});')
    if hold:
        J(f'tl.to(["#{pid}-armLg", "#{pid}-armRg"], {{rotation:0, duration:0.4, ease:"power2.inOut"}}, {t + hold:.2f});')

def sorpresa(pid, t, hold=None):
    J(f'tl.to("#{pid}-eyes", {{scaleY:1.35, duration:0.15, svgOrigin:"500 742"}}, {t:.2f}); tl.to("#{pid}-mouthO", {{opacity:1, duration:0.15}}, {t:.2f}); tl.to("#{pid}-mouth", {{opacity:0, duration:0.15}}, {t:.2f});')
    if hold:
        J(f'tl.to("#{pid}-eyes", {{scaleY:1, duration:0.2, svgOrigin:"500 742"}}, {t + hold:.2f}); tl.to("#{pid}-mouthO", {{opacity:0, duration:0.2}}, {t + hold:.2f}); tl.to("#{pid}-mouth", {{opacity:1, duration:0.2}}, {t + hold:.2f});')

def sonrisa(pid, t):
    J(f'tl.to("#{pid}-mouth", {{attr:{{d:"M474,814 Q500,842 526,814"}}, duration:0.25}}, {t:.2f});')

exec(open(os.path.join(BASE, 'guion_anim.py'), encoding='utf-8').read())

# franjas de la transición (fuera del mundo, en pantalla)
OVER.append('<div id="wipe" style="position:absolute;left:0;top:-300px;width:3200px;height:2600px;pointer-events:none">'
            '<div style="position:absolute;left:0;top:0;width:3200px;height:2600px;transform:skewX(-18deg)">'
            '<div style="position:absolute;left:0;top:0;width:150px;height:2600px;background:#06d6a0"></div>'
            '<div style="position:absolute;left:150px;top:0;width:150px;height:2600px;background:#ffd23f"></div>'
            '<div style="position:absolute;left:300px;top:0;width:2600px;height:2600px;background:#ff5d8f;box-shadow:0 0 0 14px #ffffff inset"></div>'
            '<div style="position:absolute;left:2900px;top:0;width:150px;height:2600px;background:#ffd23f"></div>'
            '<div style="position:absolute;left:3050px;top:0;width:150px;height:2600px;background:#06d6a0"></div></div>'
            '<div style="position:absolute;left:1450px;top:1150px;font:900 120px Inter;color:#ffffff">🐜</div></div>')
J('tl.set("#wipe", {x:1900}, 0);')

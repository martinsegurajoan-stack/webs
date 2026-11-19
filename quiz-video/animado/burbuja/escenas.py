# ======================================================================================================
#  ¿QUÉ PASARÍA SI TE SUELTAN EN UNA BURBUJA DE FÚTBOL DESDE UN HELICÓPTERO?  — un solo mundo vertical
#  (del campo de fútbol a 1.000 m) y una cámara que sigue a la burbuja. Casi sin transiciones.
# ======================================================================================================
def nubes(x0, y, n=4, seed=1, w=1000, h=260, s=1.0, op=0.92):
    r_ = random.Random(seed)
    return "".join(f'<g class="nube" transform="translate({x0 + r_.uniform(0, w):.0f},{y + r_.uniform(0, h):.0f}) scale({s * r_.uniform(0.7, 1.3):.2f})">' + "".join(f'<ellipse cx="{dx}" cy="{dy}" rx="{rx}" ry="{rx * 0.62:.0f}" fill="#ffffff" opacity="{op}"/>' for dx, dy, rx in ((-70, 6, 52), (0, -10, 74), (66, 4, 54), (22, 14, 60), (-30, 18, 50))) + '<ellipse cx="0" cy="30" rx="120" ry="16" fill="#cfe3f5" opacity="0.6"/></g>' for _ in range(n))
def destello(cx, cy, r, col="#ffffff", cls="chispa"):
    return f'<path class="{cls}" d="M{cx},{cy - r} Q{cx + r * 0.18},{cy - r * 0.18} {cx + r},{cy} Q{cx + r * 0.18},{cy + r * 0.18} {cx},{cy + r} Q{cx - r * 0.18},{cy + r * 0.18} {cx - r},{cy} Q{cx - r * 0.18},{cy - r * 0.18} {cx},{cy - r} Z" fill="{col}"/>'
grad_lin("cieloV", ((0, "#0f3c8f", 1), (0.35, "#2f7de0", 1), (0.8, "#7cc2ff", 1), (1, "#cdeaff", 1)))
grad_rad("burbG", ((0, "#ffffff", 0.06), (0.75, "#bfefff", 0.16), (0.95, "#8fdcff", 0.42), (1, "#ffffff", 0.7)))
grad_lin("cesped", ((0, "#4fb35a", 1), (1, "#2f7d3a", 1)))
grad_lin("gradas", ((0, "#3a4258", 1), (1, "#262c3d", 1)))
grad_lin("rojoH", ((0, "#ff5a4a", 1), (1, "#c41f2a", 1)))
YO = estilo(5, piel="#e0ac85", pelo="#2a1a12", ropa="#f2c14e", peinado="corto", barba=False, gafas=False, ojos="#4a3020")
PANT = "#2a3550"
R = 200                       # radio de la burbuja
YG = 15000                    # suelo (césped)
PXM = 12                      # píxeles por metro de altura
YC0 = YG - 380                # centro de la burbuja con los pies en el suelo
L = 520                       # cuerda: del gancho del helicóptero a lo alto de la burbuja
HOOK0 = YC0 - R - L           # gancho cuando la burbuja está en el suelo
def y_alt(a): return YC0 - a * PXM

def burbuja(pid, cuerda=0):
    """Burbuja de fútbol (bubble football): tú dentro (cabeza y pecho, con correas), piernas fuera por abajo."""
    e = YO
    s = []
    if cuerda:
        s.append(f'<path class="cuerdaB" d="M0,{-R} C30,{-R - cuerda * 0.3} -30,{-R - cuerda * 0.6} 10,{-R - cuerda}" stroke="#c9a46a" stroke-width="9" fill="none" stroke-linecap="round"/>')
    for L_, sid in ((-1, "pi"), (1, "pd")):
        x = L_ * 42
        s.append(f'<g id="{pid}_{sid}"><path d="M{x - 26},150 L{x + 26},150 L{x + 22},350 L{x - 22},350 Z" fill="{PANT}"/>'
                 f'<path d="M{x - 24},342 L{x + 24},342 L{x + 22 + L_ * 18},372 L{x - 22 + L_ * 6},378 Z" fill="#f4f4f4"/><rect x="{x - 26 + min(0, L_ * 6)}" y="370" width="{52 + 18}" height="10" rx="5" fill="#d8261a"/></g>')
    s.append(f'<circle r="{R}" fill="url(#burbG)"/>')
    s.append(f'<clipPath id="{pid}_clip"><circle r="{R - 4}"/></clipPath><g clip-path="url(#{pid}_clip)"><rect x="{-R}" y="{R * 0.48:.0f}" width="{2 * R}" height="{R}" fill="#ff5a4a" opacity="0.55"/></g>')
    s.append(f'<ellipse cx="0" cy="{R * 0.8:.0f}" rx="{R * 0.42:.0f}" ry="{R * 0.12:.0f}" fill="#1a2030" opacity="0.55"/>')
    # tú dentro: torso con correas, cuello, cabeza con cara, gorra y móvil (que flotarán al caer)
    s.append(f'<g id="{pid}_cuerpo"><path d="M-74,150 L-70,20 Q-66,-6 -30,-10 L30,-10 Q66,-6 70,20 L74,150 Z" fill="{e["ropa"]}"/><path d="M-74,150 L-70,20 Q-66,-6 -30,-10 L30,-10 Q66,-6 70,20 L74,150 Z" fill="url(#brilloRopa)"/>'
             f'<path class="correa" d="M-60,0 L40,150 M60,0 L-40,150" stroke="#1d2433" stroke-width="13"/><rect x="-14" y="64" width="28" height="22" rx="5" fill="#c9ccd2"/>'
             f'<path d="M-14,-46 L14,-46 L18,-8 L-18,-8 Z" fill="{oscurece(e["piel"], 0.88)}"/>'
             f'<g class="cab" id="{pid}_cabG">{cara(pid, 0, -78, 46, e, expr="nervioso")}'
             f'<g id="{pid}_gorra"><path d="M-48,-112 Q0,-160 48,-112 Z" fill="#2f5fbf"/><rect x="-6" y="-116" width="70" height="10" rx="5" fill="#2f5fbf"/></g></g>'
             f'<g id="{pid}_movil"><rect x="20" y="96" width="34" height="56" rx="6" fill="#1a1d22"/><rect x="24" y="101" width="26" height="44" rx="3" fill="#7fe0ff"/></g>'
             + "".join(f'<path d="M{L_ * 62},12 Q{L_ * 120},20 {L_ * 136},-24" stroke="{e["ropa"]}" stroke-width="30" fill="none" stroke-linecap="round"/><circle cx="{L_ * 138}" cy="-30" r="17" fill="{e["piel"]}"/>'
                       f'<path d="M{L_ * 120},-56 Q{L_ * 160},-34 {L_ * 150},-4" stroke="#1d2433" stroke-width="9" fill="none"/>' for L_ in (-1, 1)) + '</g>')
    s.append(f'<g id="{pid}_grito" opacity="0">' + "".join(f'<path d="M{-30 - i * 16},{-30 + i * 2} Q0,{-6 + i * 14} {30 + i * 16},{-30 + i * 2}" stroke="#ffffff" stroke-width="4" fill="none" opacity="{0.8 - i * 0.2:.1f}" transform="translate(0,{30 + i * 14})"/>' for i in range(3)) + '</g>')
    # superficie: brillo grande, costuras y escarcha
    s.append(f'<circle r="{R}" fill="none" stroke="#ffffff" stroke-width="6" opacity="0.85"/>'
             f'<path d="M{-R * 0.72:.0f},{-R * 0.35:.0f} A{R * 0.8:.0f},{R * 0.8:.0f} 0 0 1 {-R * 0.2:.0f},{-R * 0.8:.0f}" stroke="#ffffff" stroke-width="22" fill="none" stroke-linecap="round" opacity="0.55"/>'
             f'<ellipse cx="{R * 0.42:.0f}" cy="{-R * 0.55:.0f}" rx="22" ry="12" fill="#ffffff" opacity="0.7" transform="rotate(35 {R * 0.42:.0f} {-R * 0.55:.0f})"/>'
             f'<ellipse rx="{R}" ry="{R * 0.32:.0f}" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.25"/><ellipse rx="{R * 0.32:.0f}" ry="{R}" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.2"/>'
             f'<circle cy="{-R}" r="12" fill="none" stroke="#9aa3ad" stroke-width="6"/>')
    s.append(f'<g id="{pid}_hielo" opacity="0"><circle r="{R - 3}" fill="none" stroke="#e8fbff" stroke-width="14" stroke-dasharray="18 10"/>'
             + "".join(destello(x, y, rr, "#e8fbff") for x, y, rr in ((-140, -80, 22), (120, -120, 18), (150, 60, 16), (-120, 110, 20), (0, -170, 14))) + '</g>')
    return "".join(s)

def helicoptero(hid):
    """Helicóptero rojo (morro a la derecha). El gancho está en (0,0); el cuerpo encima."""
    s = [f'<g id="{hid}">',
         '<path d="M0,-70 L0,0" stroke="#5b636d" stroke-width="8"/><circle cy="0" r="10" fill="#5b636d"/>',
         '<path d="M-150,-30 L150,-30 M-110,-30 L-90,-62 M110,-30 L90,-62" stroke="#3a3f48" stroke-width="10" stroke-linecap="round"/>',
         '<path d="M-200,-150 L-560,-170 L-560,-150 L-200,-110 Z" fill="url(#rojoH)"/><path d="M-560,-170 L-610,-250 L-575,-250 L-540,-160 Z" fill="#c41f2a"/>',
         '<g id="' + hid + '_cola"><circle cx="-580" cy="-160" r="46" fill="none" stroke="#3a3f48" stroke-width="5" opacity="0.5"/><path d="M-580,-206 L-580,-114" stroke="#3a3f48" stroke-width="8"/></g>',
         '<path d="M-180,-62 Q-235,-62 -235,-135 Q-235,-238 -100,-242 L110,-242 Q200,-236 225,-150 Q232,-70 150,-62 Z" fill="url(#rojoH)"/>',
         '<path d="M60,-226 L120,-226 Q195,-220 214,-150 L214,-118 L60,-118 Z" fill="#9fd6ff"/><path d="M80,-220 L140,-130" stroke="#ffffff" stroke-width="10" opacity="0.4"/>',
         '<rect x="-160" y="-216" width="120" height="120" rx="10" fill="#1a1d22"/>',
         '<rect x="-12" y="-272" width="24" height="32" fill="#3a3f48"/>',
         '<g id="' + hid + '_rotor"><ellipse cx="0" cy="-276" rx="460" ry="10" fill="#2a2e35" opacity="0.85"/></g>',
         '<path d="M-235,-120 L225,-120" stroke="#ffffff" stroke-width="8" opacity="0.6"/>']
    s.append(f'<g>{cara("pil", 140, -176, 30, estilo(81, piel="#c68a62", pelo="#1a1a1a", peinado="corto", gafas=True, barba=True), expr="neutral")}</g>')
    s.append('<g id="pilMovil"><rect x="88" y="-150" width="30" height="46" rx="5" fill="#1a1d22"/><rect x="92" y="-146" width="22" height="36" rx="3" fill="#7fe0ff"/></g>')
    # copiloto asomado por la puerta con unas tijeras gigantes (aparece en el momento)
    s.append('<g id="copi" opacity="0">' + cara("cop", -100, -170, 34, estilo(83, piel="#f2c9a8", pelo="#b07a3a", peinado="corto"), expr="sonrisa")
             + '<g id="tije" transform="translate(-60,-60)"><g id="tijA"><path d="M0,0 L120,90 L110,100 Z" fill="#c9d1d9" stroke="#7d8894" stroke-width="3"/><circle cx="-24" cy="-14" r="20" fill="none" stroke="#e8261a" stroke-width="9"/></g>'
             '<g id="tijB"><path d="M0,0 L130,70 L122,82 Z" fill="#dfe5ec" stroke="#7d8894" stroke-width="3"/><circle cx="-18" cy="22" r="20" fill="none" stroke="#e8261a" stroke-width="9"/></g><circle r="7" fill="#3a3f48"/></g></g>')
    s.append('</g>')
    return "".join(s)

def jugador(jid, x, ropa, h=300, portero=False, lado=1):
    e = estilo(hash(jid) % 997, ropa=ropa)
    extra = f'<circle cx="{x - 46 * h / 300:.0f}" cy="{YG - 125 * h / 300:.0f}" r="{12 * h / 300:.0f}" fill="#ffffff"/><circle cx="{x + 46 * h / 300:.0f}" cy="{YG - 125 * h / 300:.0f}" r="{12 * h / 300:.0f}" fill="#ffffff"/>' if portero else ""
    return f'<g id="{jid}">{persona(x, YG + 6, h, pid=jid + "p", e=e, lado=lado, expr0="neutral")}{extra}</g>'

# ------------------------------------------------------------------ el mundo: cielo, nubes, regla de altura, estadio
W0, W1 = -1200, 2300
mundo = [f'<rect x="{W0}" y="-2000" width="{W1 - W0}" height="{YG + 2000}" fill="url(#cieloV)"/>']
for a_, seed in ((980, 1), (900, 2), (760, 3), (620, 4), (480, 5), (330, 6), (190, 7)):
    mundo.append(nubes(-900, y_alt(a_) - 120, 5, seed, 2600, 260, 1.8, 0.88))
# regla de altura (para el plano general)
for m in range(0, 1001, 100):
    y = y_alt(m) + 380
    mundo.append(f'<path d="M1500,{y} L1640,{y}" stroke="#ffffff" stroke-width="10" opacity="0.8"/><text x="1660" y="{y + 26}" font-family="Inter" font-weight="900" font-size="80" fill="#ffffff" opacity="0.9">{m} m</text>')
mundo.append(f'<path d="M1500,{y_alt(1000) + 380} L1500,{YG}" stroke="#ffffff" stroke-width="8" opacity="0.6"/>')
# pájaros (~560 m) y avioneta (~470 m)
for i, (dx, dy) in enumerate(((180, -60), (300, 20), (820, -30), (900, 60), (760, 120))):
    bx, by_ = dx, y_alt(560) + dy
    mundo.append(f'<g class="pajaro" transform="translate({bx},{by_})"><g class="pj"><path class="ala" d="M0,0 Q-40,-30 -80,-6 Q-40,-14 0,8 Q40,-14 80,-6 Q40,-30 0,0 Z" fill="#2a2e35"/>'
                 f'<ellipse cx="0" cy="6" rx="22" ry="14" fill="#2a2e35"/><g class="cabP"><circle cx="16" cy="-4" r="11" fill="#2a2e35"/><circle cx="20" cy="-6" r="5" fill="#ffffff"/><circle cx="21" cy="-6" r="2.4" fill="#111"/><path d="M26,-2 L38,0 L26,4 Z" fill="#f2c14e"/></g></g></g>')
mundo.append(f'<g id="avioneta" transform="translate(1500,{y_alt(470)})"><g id="avI"><path d="M-160,0 Q-150,-30 -60,-34 L120,-30 Q170,-24 170,0 Q170,22 120,26 L-60,28 Q-150,26 -160,0 Z" fill="#ffffff"/>'
             '<path d="M-20,-4 L40,-150 L80,-150 L60,-4 Z M-20,4 L40,150 L80,150 L60,4 Z" fill="#e8261a"/><path d="M-140,-6 L-180,-70 L-150,-70 L-110,-8 Z" fill="#e8261a"/>'
             '<path d="M90,-24 Q140,-22 152,-2 L90,-2 Z" fill="#9fd6ff"/><rect x="168" y="-50" width="8" height="100" rx="4" fill="#3a3f48"/>'
             + cara("avp", 112, -36, 16, estilo(91, peinado="corto", gafas=True), expr="neutral") + '</g></g>')
# estadio: gradas con público, focos, césped con rayas, porterías y jugadores
r9 = random.Random(9)
mundo.append(f'<rect x="{W0}" y="{YG - 640}" width="{W1 - W0}" height="560" fill="url(#gradas)"/>'
             + "".join(f'<rect x="{W0}" y="{YG - 640 + i * 90}" width="{W1 - W0}" height="8" fill="#4a5470"/>' for i in range(6))
             + "".join(f'<circle cx="{r9.uniform(W0, W1):.0f}" cy="{YG - 600 + r9.randint(0, 5) * 90 + r9.uniform(10, 60):.0f}" r="14" fill="{r9.choice(("#f2c14e", "#e2725b", "#3f7ad8", "#ffffff", "#2fa36b", "#d94f6b"))}"/>' for _ in range(420))
             + "".join(f'<rect x="{x - 12}" y="{YG - 1500}" width="24" height="900" fill="#9aa3ad"/><rect x="{x - 90}" y="{YG - 1580}" width="180" height="90" rx="10" fill="#dfe5ec"/><ellipse class="foco" cx="{x}" cy="{YG - 1535}" rx="200" ry="120" fill="url(#brilloOro)" opacity="0.6"/>' for x in (-500, 1580)))
mundo.append(f'<rect x="{W0}" y="{YG - 80}" width="{W1 - W0}" height="2600" fill="url(#cesped)"/>' + "".join(f'<rect x="{W0 + i * 260}" y="{YG - 80}" width="130" height="2600" fill="#ffffff" opacity="0.06"/>' for i in range(14))
             + f'<path d="M{W0},{YG + 30} L{W1},{YG + 30}" stroke="#ffffff" stroke-width="8" opacity="0.7"/><ellipse cx="540" cy="{YG + 120}" rx="420" ry="60" fill="none" stroke="#ffffff" stroke-width="8" opacity="0.6"/>')
for gx, s_ in ((-180, 1), (1260, -1)):
    mundo.append(f'<path d="M{gx},{YG + 10} L{gx},{YG - 240} L{gx + s_ * 150},{YG - 240} L{gx + s_ * 150},{YG + 10}" stroke="#ffffff" stroke-width="14" fill="none"/>'
                 + "".join(f'<path d="M{gx + s_ * k * 30},{YG - 240} L{gx + s_ * k * 30},{YG + 10}" stroke="#ffffff" stroke-width="3" opacity="0.5"/>' for k in range(1, 5)))
JUG = [("j1", 120, "#3f7ad8", 1), ("j2", 330, "#e2725b", 1), ("j3", 780, "#3f7ad8", -1), ("j4", 980, "#e2725b", -1)]
for jid, x, ropa, lado in JUG:
    mundo.append(jugador(jid, x, ropa, 330, lado=lado))
mundo.append(jugador("port", 1180, "#2fa36b", 330, portero=True, lado=-1))
mundo.append(f'<g id="amigo" opacity="0">{persona(250, YG + 6, 400, pid="amg", e=estilo(33, ropa="#2fa36b", peinado="rizado"), expr0="sonrisa")}</g>')
mundo.append(f'<ellipse id="sombra" cx="540" cy="{YG + 10}" rx="140" ry="22" fill="#000" opacity="0.0"/>')
mundo.append(f'<g id="polvo" opacity="0">' + "".join(f'<circle cx="{540 + dx}" cy="{YG - 20}" r="{60 + abs(dx) % 40}" fill="#cfe6c0" opacity="0.7"/>' for dx in (-300, -180, -60, 60, 180, 300)) + '</g>')
# helicóptero con la burbuja colgando (péndulo) y la burbuja que cae suelta
mundo.append(f'<g transform="translate(540,{HOOK0})"><g id="heliG">{helicoptero("heli")}'
             f'<g id="pend"><path id="cuerdaA" d="M0,0 L0,{L}" stroke="#c9a46a" stroke-width="9"/><g transform="translate(0,{L + R})"><g id="bubA">{burbuja("ba")}</g></g></g>'
             f'<path id="cuerdaCorta" d="M0,0 L0,70" stroke="#c9a46a" stroke-width="9" opacity="0"/></g></g>')
mundo.append(f'<g transform="translate(540,{y_alt(1000)})"><g id="bubB" opacity="0">{burbuja("bb", cuerda=380)}</g></g>')
# explosión final (trozos de plástico)
mundo.append(f'<g transform="translate(540,{YC0})"><g id="boom" opacity="0"><circle r="420" fill="url(#brilloBlanco)"/>' + "".join(
    f'<path class="trozo" d="M0,0 l{30 + i % 3 * 12},{-16 - i % 2 * 10} l{-14},{30 + i % 4 * 6} Z" fill="#bfefff" stroke="#ffffff" stroke-width="3"/>' for i in range(16)) + '</g></g>')

ESC.append(f'<div class="esc" id="mundo"><div class="cam" id="zoom"><div id="follow" style="position:absolute;left:0;top:0;width:1080px;height:1920px">'
           f'<svg width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0;overflow:visible">{"".join(mundo)}</svg></div></div></div>')

# ------------------------------------------------------------------ cámara: foco (punto del mundo en el centro) y zoom
def foco(t, F_, S_, d, ease="power2.inOut"):
    J(f'tl.to("#follow", {{y:{960 - F_:.0f}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f}); tl.to("#zoom", {{scale:{S_}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
def foco_set(t, F_, S_):
    J(f'tl.set("#follow", {{y:{960 - F_:.0f}}}, {t:.2f}); tl.set("#zoom", {{scale:{S_}}}, {t:.2f});')
ALT = []
def altura(t, a, d=0.0, ease="none"):
    """Altímetro: el número que se ve arriba a la izquierda."""
    J(f'tl.to(ALT, {{v:{a}, duration:{max(0.01, d):.2f}, ease:"{ease}", onUpdate:pintaAlt}}, {t:.2f});')
J('const ALT = {v:1000}; const pintaAlt = () => { const e = document.getElementById("altN"); if (e) e.textContent = Math.round(ALT.v).toLocaleString("es-ES"); };')
OVR.append('<div id="altim"><small>ALTURA</small><b><span id="altN">1.000</span> m</b></div>')
J('tl.set("#mundo", {opacity:1}, 0);')
# rotor y cola giran siempre; foco del estadio late; nubes se mueven
J(f'tl.fromTo("#heli_rotor", {{scaleX:1}}, {{scaleX:0.15, svgOrigin:"0 -276", duration:0.06, yoyo:true, repeat:{int(DUR / 0.06)}, ease:"none", immediateRender:false}}, 0);')
J(f'tl.fromTo("#heli_cola", {{rotation:0}}, {{rotation:{int(DUR * 900)}, svgOrigin:"-580 -160", duration:{DUR:.2f}, ease:"none", immediateRender:false}}, 0);')
J(f'tl.fromTo(".nube", {{x:0}}, {{x:-260, duration:{DUR:.2f}, ease:"none", immediateRender:false}}, 0);')
J(f'tl.fromTo(".pj .ala", {{scaleY:1}}, {{scaleY:-0.6, transformOrigin:"50% 50%", duration:0.18, yoyo:true, repeat:{int(DUR / 0.18)}, ease:"sine.inOut", immediateRender:false}}, 0);')
parpadeo("ba", 0, DUR, 2); parpadeo("bb", 0, DUR, 3); parpadeo("pil", 0, DUR, 4)
FX.append(("helice", 0.0))

# ================================================================== 1) GANCHO: a 1.000 m, colgando del helicóptero… plano general de toda la caída… y cortan
f1, f2 = 0.0, F(2)
J(f'tl.set("#heliG", {{y:{-1000 * PXM}}}, 0);')
foco_set(0, y_alt(1000) - 260, 0.8)
J(f'tl.fromTo("#pend", {{rotation:-6}}, {{rotation:6, svgOrigin:"0 0", duration:1.1, yoyo:true, repeat:5, ease:"sine.inOut", immediateRender:false}}, 0);')
J(f'tl.fromTo("#bubA", {{rotation:-20}}, {{rotation:20, svgOrigin:"0 0", duration:0.9, yoyo:true, repeat:7, ease:"sine.inOut", immediateRender:false}}, 0);')
expr("ba", 0.0, "nervioso", "preocupado")
J('tl.fromTo("#zoom", {scale:0.95}, {scale:0.8, duration:0.6, ease:"power3.out", immediateRender:false}, 0);')
OVR.append('<div id="gancho"><div class="g1">1.000 METROS</div><div class="g2">SIN PARACAÍDAS</div></div>')
J(f'tl.fromTo("#gancho", {{opacity:1, scale:1.2}}, {{scale:1, duration:0.4, ease:"back.out(2)", immediateRender:false}}, 0); tl.to("#gancho", {{opacity:0, duration:0.25}}, {P("mil") - 0.2:.2f});')
# plano general de toda la columna: del helicóptero al estadio
foco(P("mil") - 0.15, (y_alt(1000) + YG) / 2 - 300, 0.105, 0.9, "power3.inOut")
foco(P("cortan") - 0.55, y_alt(1000) - 200, 0.85, 0.5, "power3.inOut")
# tijeretazo en el gancho
J(f'tl.set("#copi", {{opacity:1}}, {P("cortan") - 0.5:.2f}); tl.fromTo("#copi", {{x:-60}}, {{x:0, duration:0.25, ease:"back.out(2)", immediateRender:false}}, {P("cortan") - 0.5:.2f});')
J(f'tl.to("#tijA", {{rotation:14, svgOrigin:"0 0", duration:0.1, yoyo:true, repeat:1}}, {P("cortan"):.2f}); tl.to("#tijB", {{rotation:-14, svgOrigin:"0 0", duration:0.1, yoyo:true, repeat:1}}, {P("cortan"):.2f});')
tcut1 = P("cortan") + 0.15
J(f'tl.set("#pend", {{opacity:0}}, {tcut1:.2f}); tl.set("#cuerdaCorta", {{opacity:1}}, {tcut1:.2f}); tl.set("#bubB", {{opacity:1, y:0, rotation:0}}, {tcut1:.2f});')
J(f'tl.to("#bubB", {{y:520, rotation:-30, svgOrigin:"0 0", duration:{f2 - tcut1:.2f}, ease:"power2.in"}}, {tcut1:.2f});')
expr("bb", tcut1, "nervioso", "sorpresa", abierta=True)
FX.append(("snip", P("cortan"))); FX.append(("whoosh", tcut1))

# ================================================================== 2) PRIMERO TE ATAN DENTRO (en el césped del estadio)
# «rebobinado»: la cámara baja de golpe de 1.000 m al campo y todo vuelve a su sitio
J(f'tl.set("#bubB", {{opacity:0}}, {f2 + 0.35:.2f}); tl.set("#pend", {{opacity:1}}, {f2 + 0.35:.2f}); tl.set("#cuerdaCorta, #copi", {{opacity:0}}, {f2 + 0.35:.2f}); tl.set("#heliG", {{y:0}}, {f2 + 0.35:.2f});')
J(f'tl.set("#pend, #bubA", {{rotation:0}}, {f2 + 0.35:.2f});')
OVR.append('<div id="rebob"><i></i><i></i> ANTES</div>')
J(f'tl.set("#rebob", {{opacity:0}}, 0); tl.set("#rebob", {{opacity:1}}, {f2:.2f}); tl.set("#rebob", {{opacity:0}}, {f2 + 1.0:.2f});')
foco(f2, YC0 - 120, 1.0, 0.85, "power3.inOut")
altura(f2, 0, 0.85, "power3.inOut")
J(f'tl.set("#amigo", {{opacity:1}}, {f2:.2f}); tl.to("#amg .brazo", {{rotation:-70, svgOrigin:"{250 + 34 * 400 / 300:.0f} {YG + 6 - 228 * 400 / 300:.0f}", duration:0.3, yoyo:true, repeat:5}}, {P("atan"):.2f});')
J(f'tl.fromTo("#ba_cuerpo .correa", {{stroke:"#1d2433"}}, {{stroke:"#ffcf3a", duration:0.15, yoyo:true, repeat:3, immediateRender:false}}, {P("atan"):.2f});')
expr("ba", f2, "sonrisa", "neutral")
nota("CABEZA Y PECHO DENTRO", P("cabeza") - 0.1, P("piernas") - 0.1, 60, 500, "#7fe0ff")
nota("PIERNAS FUERA", P("piernas") - 0.1, F(3), 60, 500, "#ffcf3a")
J(f'tl.fromTo("#ba_pi, #ba_pd", {{x:0}}, {{x:8, duration:0.12, yoyo:true, repeat:5, immediateRender:false}}, {P("piernas"):.2f});')
J(f'tl.to("#j1, #j2, #j3, #j4, #port", {{y:-12, duration:0.2, yoyo:true, repeat:3, stagger:0.08}}, {f2 + 0.8:.2f});')

# ================================================================== 3) DESPEGA: los pies dejan el césped
t3 = P("despega")
J(f'tl.to("#amigo", {{x:-260, duration:0.8, ease:"power2.in"}}, {t3:.2f});')
J(f'tl.fromTo("#polvo", {{opacity:0, scale:0.6}}, {{opacity:0.8, scale:1.4, svgOrigin:"540 {YG}", duration:0.6, immediateRender:false}}, {t3:.2f}); tl.to("#polvo", {{opacity:0, duration:0.8}}, {t3 + 0.9:.2f});')
J(f'tl.to("#heliG", {{y:-30, duration:0.5, ease:"power1.out"}}, {t3 + 0.1:.2f});')
J(f'tl.to("#heliG", {{y:{-100 * PXM}, duration:{F(4) + 0.4 - (P("pies") + 0.2):.2f}, ease:"power2.in"}}, {P("pies") + 0.2:.2f});')
foco(P("pies") + 0.2, y_alt(100) - 150, 0.85, F(4) + 0.4 - (P("pies") + 0.2), "power2.in")
altura(P("pies") + 0.2, 100, F(4) + 0.4 - (P("pies") + 0.2), "power2.in")
J(f'tl.fromTo("#ba_pi", {{rotation:-10}}, {{rotation:12, svgOrigin:"-42 150", duration:0.25, yoyo:true, repeat:7, immediateRender:false}}, {P("pies"):.2f}); tl.fromTo("#ba_pd", {{rotation:10}}, {{rotation:-12, svgOrigin:"42 150", duration:0.25, yoyo:true, repeat:7, immediateRender:false}}, {P("pies"):.2f});')
expr("ba", P("pies"), "nervioso", "sorpresa", abierta=True)
J(f'tl.to("#j1, #j2, #j3, #j4", {{y:-30, duration:0.25, yoyo:true, repeat:1, stagger:0.05}}, {P("pies"):.2f});')
FX.append(("helice", t3)); FX.append(("whoosh", P("pies")))

# ================================================================== 4) A 100 m GIRA COMO UNA PEONZA · 5) A 500 m: FRÍO, PIERNAS CONGELADAS, EL PILOTO NI TE MIRA
J(f'tl.fromTo("#bubA", {{rotation:0}}, {{rotation:1080, svgOrigin:"0 0", duration:{F(5) - P("girar") + 0.3:.2f}, ease:"sine.inOut", immediateRender:false}}, {P("girar") - 0.3:.2f});')
J(f'tl.fromTo("#pend", {{rotation:-10}}, {{rotation:10, svgOrigin:"0 0", duration:0.7, yoyo:true, repeat:{int((F(6) - F(4)) / 0.7)}, ease:"sine.inOut", immediateRender:false}}, {F(4):.2f});')
expr("ba", P("girar"), "nervioso", "preocupado", abierta=True)
nota("GIRA COMO UNA PEONZA", P("peonza") - 0.4, F(5), 60, 500, "#ff5a4a")
# sube a 500 m (las nubes pasan a toda velocidad)
t5a, t5b = F(4) + 0.6, P("quinientos") + 0.1
J(f'tl.to("#heliG", {{y:{-500 * PXM}, duration:{t5b - t5a:.2f}, ease:"power1.inOut"}}, {t5a:.2f});')
foco(t5a, y_alt(500) - 150, 0.85, t5b - t5a, "power1.inOut")
altura(t5a, 500, t5b - t5a, "power1.inOut")
J(f'tl.to("#ba_hielo", {{opacity:1, duration:1.0}}, {P("congela") - 0.5:.2f});')
J(f'tl.fromTo("#ba_pi, #ba_pd", {{x:-5}}, {{x:5, duration:0.05, yoyo:true, repeat:{int((F(6) - P("congela")) / 0.05)}, immediateRender:false}}, {P("congela"):.2f});')
J(f'tl.set("#ba_bocaO", {{opacity:0}}, {P("congela"):.2f}); tl.to("#ba_boca", {{opacity:1}}, {P("congela"):.2f});')
expr("ba", P("congela") - 0.1, "nervioso", "preocupado")
OVR.append('<div id="viento">' + "".join(f'<i style="top:{560 + i * 150}px;left:{(i * 280) % 1000}px"></i>' for i in range(8)) + '</div>')
J(f'tl.set("#viento", {{opacity:0}}, 0); tl.to("#viento", {{opacity:1, duration:0.3}}, {P("viento") - 0.2:.2f}); tl.to("#viento", {{opacity:0, duration:0.3}}, {F(6):.2f});')
J(f'tl.fromTo("#viento i", {{x:600}}, {{x:-900, duration:0.45, repeat:{int((F(6) - P("viento")) / 0.45)}, stagger:0.07, ease:"none", immediateRender:false}}, {P("viento") - 0.2:.2f});')
FX.append(("viento", P("viento") - 0.2))
# el piloto ni te mira: la cámara sube a la cabina (está con el móvil)
tp = P("piloto") - 0.35
foco(tp, y_alt(500) - R - L - 170, 1.55, 0.45, "power3.inOut")
J(f'tl.to("#pilMovil", {{y:-8, duration:0.2, yoyo:true, repeat:3}}, {tp + 0.4:.2f});')
expr("pil", tp, "sonrisa", "neutral")
foco(F(6) - 0.05, y_alt(500) - 200, 0.85, 0.4, "power3.inOut")

# ================================================================== 6) A 1.000 m: SILENCIO · ALGUIEN SACA UNAS TIJERAS · 7) Y CORTAN
t6a, t6b = F(6) + 0.3, P("mil", 2) + 0.2
J(f'tl.to("#heliG", {{y:{-1000 * PXM}, duration:{t6b - t6a:.2f}, ease:"power2.inOut"}}, {t6a:.2f});')
foco(t6a, y_alt(1000) - 260, 0.9, t6b - t6a, "power2.inOut")
altura(t6a, 1000, t6b - t6a, "power2.inOut")
J(f'tl.to("#pend", {{rotation:0, svgOrigin:"0 0", duration:0.8}}, {P("silencio") - 0.2:.2f}); tl.to("#bubA", {{rotation:0, svgOrigin:"0 0", duration:0.8}}, {P("silencio") - 0.2:.2f});')
expr("ba", P("silencio"), "triste", "preocupado")
J(f'tl.set("#copi", {{opacity:1}}, {P("alguien") - 0.1:.2f}); tl.fromTo("#copi", {{x:-80}}, {{x:0, duration:0.35, ease:"back.out(2)", immediateRender:false}}, {P("alguien") - 0.1:.2f});')
J(f'tl.fromTo("#tije", {{scale:0.2}}, {{scale:1.4, svgOrigin:"0 0", duration:0.3, ease:"back.out(2)", immediateRender:false}}, {P("tijeras") - 0.2:.2f});')
J(f'tl.to("#tijA", {{rotation:14, svgOrigin:"0 0", duration:0.15, yoyo:true, repeat:3}}, {P("tijeras"):.2f}); tl.to("#tijB", {{rotation:-14, svgOrigin:"0 0", duration:0.15, yoyo:true, repeat:3}}, {P("tijeras"):.2f});')
foco(P("tijeras") - 0.2, y_alt(1000) - R - L + 40, 1.6, 0.5, "power3.inOut")
expr("ba", P("tijeras"), "nervioso", "sorpresa", abierta=True)
tc = P("cortan", 2) + 0.05
J(f'tl.to("#tijA", {{rotation:20, svgOrigin:"0 0", duration:0.08}}, {tc:.2f}); tl.to("#tijB", {{rotation:-20, svgOrigin:"0 0", duration:0.08}}, {tc:.2f});')
J(f'tl.set("#pend", {{opacity:0}}, {tc + 0.08:.2f}); tl.set("#cuerdaCorta", {{opacity:1}}, {tc + 0.08:.2f}); tl.set("#bubB", {{opacity:1, y:0, x:0, rotation:0}}, {tc + 0.08:.2f});')
J(f'tl.fromTo("#flashB", {{opacity:0.8}}, {{opacity:0, duration:0.25, immediateRender:false}}, {tc + 0.08:.2f});')
foco(tc + 0.1, y_alt(1000) - 60, 0.95, 0.5, "power2.out")
FX.append(("snip", tc)); FX.append(("golpe", tc + 0.1))

# ================================================================== 8-15) LA CAÍDA: la cámara sigue a la burbuja
CAI = [(tc + 0.15, 1000), (F(9), 975), (F(10), 940), (F(11), 880), (F(12), 800), (F(13), 650), (P("abajo") - 0.2, 470), (F(14), 330), (F(15), 230), (P("cien", 3) - 0.1, 100),
       (P("cincuenta") - 0.05, 50), (P("diez") - 0.05, 10), (P("explota") + 0.02, 0)]
for (ta, aa), (tb, ab) in zip(CAI, CAI[1:]):
    ease = "power2.in" if aa == 1000 else "none"
    J(f'tl.to("#bubB", {{y:{(1000 - ab) * PXM}, duration:{tb - ta:.2f}, ease:"{ease}"}}, {ta:.2f});')
    altura(ta, ab, tb - ta, ease)
def sigue(ta, tb, ab, off, S_, ease="none"):
    foco(ta, y_alt(ab) - off, S_, tb - ta, ease)
# 8) el estómago se queda arriba: la gorra y el móvil flotan dentro de la burbuja
sigue(CAI[0][0], F(9), 975, 0, 1.25, "power2.in")
J(f'tl.to("#bb_gorra", {{y:-60, rotation:-25, svgOrigin:"0 -120", duration:0.6, ease:"power2.out"}}, {P("estomago") - 0.2:.2f}); tl.to("#bb_movil", {{y:-150, x:-40, rotation:60, svgOrigin:"37 124", duration:0.8, ease:"power2.out"}}, {P("estomago") - 0.1:.2f});')
J(f'tl.to("#bb_cuerpo", {{y:-14, duration:0.3, yoyo:true, repeat:1}}, {P("estomago"):.2f});')
expr("bb", P("estomago") - 0.2, "nervioso", "sorpresa", abierta=True)
nota("TU ESTÓMAGO SE QUEDA ARRIBA", P("estomago") - 0.2, F(9), 60, 500, "#ffcf3a")
# 9) casi 100 km/h al tercer segundo (velocímetro)
OVR.append('<div id="velo"><div class="esfera"><div class="aguja2" id="agV"></div><div class="centro"></div></div><b><span id="velN">0</span> km/h</b></div>')
J('const VEL = {v:0}; const pintaVel = () => { document.getElementById("velN").textContent = Math.round(VEL.v); document.getElementById("agV").style.transform = "rotate(" + (-120 + VEL.v * 1.6) + "deg)"; };')
J(f'tl.set("#velo", {{opacity:0}}, 0); tl.fromTo("#velo", {{opacity:0, scale:0.5}}, {{opacity:1, scale:1, duration:0.3, ease:"back.out(2)", immediateRender:false}}, {F(9):.2f}); tl.to("#velo", {{opacity:0, duration:0.3}}, {F(13) - 0.1:.2f});')
J(f'tl.to(VEL, {{v:90, duration:{P("cien") - F(9) + 0.2:.2f}, ease:"power1.out", onUpdate:pintaVel}}, {F(9):.2f});')
sigue(F(9), F(10), 940, 0, 1.0)
J(f'tl.fromTo("#bubB", {{rotation:0}}, {{rotation:-160, svgOrigin:"0 0", duration:{F(10) - F(9):.2f}, ease:"sine.inOut", immediateRender:false}}, {F(9):.2f});')
expr("bb", F(9), "nervioso", "sorpresa", abierta=True)
FX.append(("viento", F(9)))
# 10) el aire frena… pero mucho menos de lo que crees (flechas de fuerzas)
OVR.append('<div id="fuerzas"><div class="fl arriba" id="flA"><i></i><span>AIRE</span></div><div class="fl abajo"><i></i><span>TU PESO</span></div></div>')
J(f'tl.set("#fuerzas", {{opacity:0}}, 0); tl.to("#fuerzas", {{opacity:1, duration:0.2}}, {P("aire") - 0.2:.2f}); tl.to("#fuerzas", {{opacity:0, duration:0.25}}, {F(11) + 0.6:.2f});')
J(f'tl.fromTo("#flA", {{scaleY:0.2}}, {{scaleY:0.55, transformOrigin:"50% 100%", duration:0.6, ease:"power2.out", immediateRender:false}}, {P("frena") - 0.1:.2f});')
J(f'tl.fromTo("#flA", {{scaleY:0.55}}, {{scaleY:0.42, transformOrigin:"50% 100%", duration:0.3, immediateRender:false}}, {P("menos") - 0.1:.2f});')
J(f'tl.to(VEL, {{v:118, duration:{F(11) - F(10):.2f}, ease:"none", onUpdate:pintaVel}}, {F(10):.2f});')
sigue(F(10), F(11), 880, 0, 1.0)
J(f'tl.to("#bubB", {{rotation:-330, svgOrigin:"0 0", duration:{F(11) - F(10):.2f}, ease:"sine.inOut"}}, {F(10):.2f});')
# 11) 140 km/h y de ahí ya no pasas (la burbuja se aplasta un poco con el aire)
J(f'tl.to(VEL, {{v:140, duration:{P("cuarenta") - F(11) + 0.2:.2f}, ease:"power2.out", onUpdate:pintaVel}}, {F(11):.2f});')
J(f'tl.fromTo("#velo", {{boxShadow:"0 0 0 0 rgba(255,59,47,0)"}}, {{boxShadow:"0 0 50px 10px rgba(255,59,47,0.8)", duration:0.25, yoyo:true, repeat:5, immediateRender:false}}, {P("cuarenta"):.2f});')
nota("VELOCIDAD MÁXIMA", P("cuarenta"), F(12), 60, 500, "#ff5a4a")
J(f'tl.fromTo("#bubB", {{scaleY:1, scaleX:1}}, {{scaleY:0.9, scaleX:1.06, svgOrigin:"0 0", duration:0.15, yoyo:true, repeat:7, immediateRender:false}}, {P("pasas") - 0.6:.2f});')
sigue(F(11), F(12), 800, 0, 0.95)
J(f'tl.to("#bubB", {{rotation:-520, svgOrigin:"0 0", duration:{F(12) - F(11):.2f}, ease:"sine.inOut"}}, {F(11):.2f});')
# 12) casi medio minuto dando vueltas y gritando (cronómetro)
OVR.append('<div id="crono"><small>CAYENDO</small><b>0:<span id="croN">00</span></b></div>')
J('const CR = {v:0}; const pintaCr = () => { document.getElementById("croN").textContent = String(Math.round(CR.v)).padStart(2, "0"); };')
J(f'tl.set("#crono", {{opacity:0}}, 0); tl.fromTo("#crono", {{opacity:0, x:200}}, {{opacity:1, x:0, duration:0.3, immediateRender:false}}, {P("minuto") - 0.4:.2f}); tl.to("#crono", {{opacity:0, duration:0.3}}, {F(14) - 0.1:.2f});')
J(f'tl.to(CR, {{v:28, duration:{F(14) - P("minuto"):.2f}, ease:"none", onUpdate:pintaCr}}, {P("minuto") - 0.3:.2f});')
J(f'tl.to("#bubB", {{rotation:-1600, svgOrigin:"0 0", duration:{F(13) - F(12):.2f}, ease:"none"}}, {F(12):.2f});')
J(f'tl.set("#bb_grito", {{opacity:1}}, {P("gritando") - 0.2:.2f}); tl.fromTo("#bb_grito path", {{scale:0.6, opacity:0}}, {{scale:1.3, opacity:0.9, svgOrigin:"0 -40", duration:0.3, stagger:0.1, repeat:5, immediateRender:false}}, {P("gritando") - 0.2:.2f}); tl.set("#bb_grito", {{opacity:0}}, {F(13) + 0.4:.2f});')
expr("bb", P("gritando") - 0.2, "nervioso", "sorpresa", abierta=True)
sigue(F(12), F(13), 650, 0, 0.9)
FX.append(("grito", P("gritando") - 0.1))
# 13) los pájaros te miran · una avioneta te esquiva · abajo el campo se hace enorme
J(f'tl.to("#bubB", {{rotation:-1800, svgOrigin:"0 0", duration:{P("abajo") - F(13):.2f}, ease:"sine.out"}}, {F(13):.2f});')
sigue(F(13), P("abajo") - 0.2, 470, 0, 0.75)
J(f'tl.to(".pajaro .cabP", {{rotation:40, svgOrigin:"16 -4", duration:0.25, stagger:0.06}}, {P("pajaros") - 0.1:.2f}); tl.to(".pajaro", {{y:"-=40", duration:0.6, stagger:0.05, ease:"power2.out"}}, {P("miran"):.2f});')
expr("bb", P("pajaros"), "nervioso", "preocupado")
J(f'tl.fromTo("#avI", {{x:0, y:0, rotation:0}}, {{x:-2600, y:-120, rotation:-28, svgOrigin:"0 0", duration:1.6, ease:"power1.inOut", immediateRender:false}}, {P("avioneta") - 0.5:.2f});')
expr("avp", P("esquiva") - 0.2, "nervioso", "sorpresa", abierta=True)
FX.append(("avioneta", P("avioneta") - 0.5))
# el campo se hace enorme: plano que mira hacia abajo, con el estadio ya a la vista
sigue(P("abajo") - 0.2, F(14), 330, -2300, 0.32, "power1.inOut")
J(f'tl.to(".foco", {{opacity:1, duration:0.3, yoyo:true, repeat:5}}, {P("abajo"):.2f});')
J(f'tl.to("#bubB", {{rotation:-1980, svgOrigin:"0 0", duration:{F(14) - P("abajo") + 0.2:.2f}, ease:"none"}}, {P("abajo") - 0.2:.2f});')
# 14-15) la burbuja solo salva de caídas pequeñas (un 2.º piso) · desde 1.000 m = un muro a toda velocidad
CASA = ('<svg viewBox="0 0 420 420" width="420" height="420"><rect width="420" height="420" rx="30" fill="#bfe3ff"/><rect y="340" width="420" height="80" fill="#4fb35a"/>'
        '<rect x="40" y="120" width="190" height="220" fill="#f4e2c8"/><polygon points="25,120 135,50 245,120" fill="#c65b46"/><rect x="70" y="150" width="50" height="50" fill="#9fd6ff"/><rect x="150" y="150" width="50" height="50" fill="#9fd6ff"/><rect x="110" y="260" width="50" height="80" fill="#7d4f2a"/>'
        '<path d="M250,120 L250,340" stroke="#ffffff" stroke-width="4" stroke-dasharray="10 8"/><text x="262" y="236" font-family="Inter" font-weight="900" font-size="34" fill="#1d2433">6-8 m</text>'
        '<g id="miniB"><circle cx="330" cy="300" r="34" fill="#bfefff" stroke="#ffffff" stroke-width="5" opacity="0.9"/><circle cx="330" cy="290" r="11" fill="#e0ac85"/></g>'
        '<circle cx="360" cy="70" r="40" fill="#2fd27a"/><path d="M342,70 L356,84 L382,56" stroke="#fff" stroke-width="10" fill="none" stroke-linecap="round"/></svg>')
MURO = ('<svg viewBox="0 0 420 420" width="420" height="420"><rect width="420" height="420" rx="30" fill="#ffd9c8"/><rect y="340" width="420" height="80" fill="#9aa0a6"/>'
        + "".join(f'<rect x="{260 + (j % 2) * 30 + i * 0}" y="{60 + j * 40}" width="60" height="36" fill="#b8442f" stroke="#ffd9c8" stroke-width="4"/><rect x="{320 + (j % 2) * 30}" y="{60 + j * 40}" width="60" height="36" fill="#b8442f" stroke="#ffd9c8" stroke-width="4"/>' for j in range(7) for i in range(1))
        + '<g id="miniM"><circle cx="200" cy="230" r="40" fill="#bfefff" stroke="#ffffff" stroke-width="5"/><circle cx="200" cy="220" r="12" fill="#e0ac85"/></g>'
        '<path d="M40,230 L150,230 M60,200 L140,200 M60,260 L140,260" stroke="#ffffff" stroke-width="8" stroke-linecap="round" opacity="0.8"/>'
        '<text x="30" y="70" font-family="Inter" font-weight="900" font-size="40" fill="#1d2433">140 km/h</text>'
        '<circle cx="80" cy="140" r="40" fill="#ff3b2f"/><path d="M60,120 L100,160 M100,120 L60,160" stroke="#fff" stroke-width="10" stroke-linecap="round"/></svg>')
OVR.append(f'<div class="cmp" id="cmpA">{CASA}<b>CAÍDAS PEQUEÑAS</b></div><div class="cmp" id="cmpB">{MURO}<b>DESDE 1.000 m</b></div>')
J(f'tl.set("#cmpA, #cmpB", {{opacity:0}}, 0); tl.fromTo("#cmpA", {{opacity:0, x:-500, rotation:-8}}, {{opacity:1, x:0, rotation:-3, duration:0.4, ease:"back.out(1.6)", immediateRender:false}}, {F(14):.2f});')
J(f'tl.fromTo("#miniB", {{y:-200}}, {{y:0, duration:0.45, ease:"bounce.out", repeat:3, repeatDelay:0.3, immediateRender:false}}, {F(14) + 0.3:.2f});')
J(f'tl.to("#cmpA", {{opacity:0, x:-500, duration:0.3, ease:"power2.in"}}, {F(15) - 0.1:.2f}); tl.fromTo("#cmpB", {{opacity:0, x:500, rotation:8}}, {{opacity:1, x:0, rotation:3, duration:0.4, ease:"back.out(1.6)", immediateRender:false}}, {F(15):.2f});')
J(f'tl.fromTo("#miniM", {{x:-120}}, {{x:60, duration:0.35, ease:"power3.in", immediateRender:false}}, {P("estamparte") - 0.2:.2f}); tl.to("#miniM", {{scaleX:0.4, svgOrigin:"260 230", duration:0.08}}, {P("estamparte") + 0.15:.2f});')
J(f'tl.fromTo("#cmpB", {{x:0}}, {{x:16, duration:0.05, yoyo:true, repeat:7, immediateRender:false}}, {P("estamparte") + 0.15:.2f}); tl.to("#cmpB", {{opacity:0, duration:0.3}}, {F(16) - 0.1:.2f});')
FX.append(("boing", F(14) + 0.75)); FX.append(("golpe", P("estamparte") + 0.15))
sigue(F(14), F(15), 230, -250, 0.85)
J(f'tl.to("#bubB", {{rotation:-2160, svgOrigin:"0 0", duration:{F(16) - F(14):.2f}, ease:"none"}}, {F(14):.2f});')
sigue(F(15), P("cien", 3) - 0.1, 100, -250, 0.85)

# ================================================================== 16-19) QUEDAN 100 m · LOS JUGADORES MIRAN ARRIBA · EL PORTERO HUYE · DIEZ… · EXPLOTA
t16 = P("cien", 3) - 0.1
sigue(t16, P("cincuenta") - 0.05, 50, -950, 0.42, "power1.inOut")
for jid, x, ropa, lado in JUG + [("port", 1180, "", -1)]:
    expr(jid + "p", P("jugadores") - 0.1, "nervioso", "sorpresa", abierta=True)
J(f'tl.to("#j1, #j2, #j3, #j4, #port", {{y:-24, duration:0.2, yoyo:true, repeat:1, stagger:0.06}}, {P("levantan") - 0.1:.2f});')
J(f'tl.to("#sombra", {{opacity:0.35, rx:240, duration:{P("explota") - t16:.2f}, ease:"power2.in"}}, {t16:.2f});')
J(f'tl.to("#bubB", {{rotation:-2340, svgOrigin:"0 0", duration:{P("diez") - F(16):.2f}, ease:"power1.out"}}, {F(16):.2f});')
# el portero sale corriendo (con saltitos)
J(f'tl.to("#port", {{x:900, duration:1.6, ease:"power2.in"}}, {P("portero") - 0.1:.2f}); tl.to("#port", {{y:-30, duration:0.12, yoyo:true, repeat:13}}, {P("portero") - 0.1:.2f});')
J(f'tl.to("#j1, #j2", {{x:-700, duration:1.4, ease:"power2.in", stagger:0.1}}, {P("corriendo"):.2f}); tl.to("#j3, #j4", {{x:700, duration:1.4, ease:"power2.in", stagger:0.1}}, {P("corriendo"):.2f});')
FX.append(("silba", P("cincuenta")))
sigue(P("cincuenta") - 0.05, P("diez") - 0.05, 10, -380, 0.62, "power1.in")
expr("bb", P("diez") - 0.3, "nervioso", "preocupado")
J(f'tl.set("#bb_ojos", {{scaleY:0.1, svgOrigin:"0 -82"}}, {P("diez"):.2f});')
J(f'tl.to("#bubB", {{rotation:-2520, svgOrigin:"0 0", duration:{P("explota") - P("diez"):.2f}, ease:"power1.in"}}, {P("diez"):.2f});')
sigue(P("diez") - 0.05, P("explota") + 0.02, 0, -180, 0.8, "power1.in")
te = P("explota") + 0.02
J(f'tl.set("#bubB", {{opacity:0}}, {te + 0.03:.2f}); tl.set("#boom", {{opacity:1}}, {te:.2f});')
J(f'tl.fromTo("#boom .trozo", {{x:0, y:0, rotation:0}}, {{x:(i) => Math.cos(i * 0.39) * 900, y:(i) => Math.sin(i * 0.39) * 700 - 200, rotation:(i) => i * 70, svgOrigin:"0 0", duration:0.5, ease:"power3.out", immediateRender:false}}, {te:.2f});')
J(f'tl.fromTo("#flashB", {{opacity:1}}, {{opacity:0.6, duration:0.12, immediateRender:false}}, {te:.2f});')
tfin = te + 0.14                                           # CORTE EN SECO
J(f'tl.set("#negroF", {{opacity:0}}, 0); tl.set("#negroF", {{opacity:1}}, {tfin:.2f});')
OVR.append('<div id="flashB"></div><div id="negroF"></div>')
FX.append(("explota", te)); FX.append(("final", tfin))

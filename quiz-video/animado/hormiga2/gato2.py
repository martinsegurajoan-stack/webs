# GATO de perfil (mira a la derecha), bonito y articulado: 4 patas con ciclo de paso, cola, cabeza que mira,
# párpados que parpadean, pupilas que se dilatan, collar con cascabel. Origen = suelo bajo el centro del cuerpo.
GX = 10300
def gato_svg():
    def pata(idd, x, col, calcetin):
        return (f'<g id="{idd}"><path d="M{x - 46},-380 C{x - 50},-250 {x - 40},-120 {x - 36},-30 L{x + 36},-30 C{x + 40},-120 {x + 50},-250 {x + 46},-380 Z" fill="{col}"/>'
                f'<ellipse cx="{x + 8}" cy="-18" rx="58" ry="30" fill="{calcetin}"/>'
                f'<path d="M{x - 16},-26 L{x - 16},-8 M{x + 8},-28 L{x + 8},-6 M{x + 32},-26 L{x + 32},-8" stroke="#e8d9c8" stroke-width="5" stroke-linecap="round"/></g>')
    rayas = "".join(f'<path d="M{x},-585 C{x + 20},-530 {x + 10},-480 {x - 10},-440" stroke="#e0761a" stroke-width="26" fill="none" stroke-linecap="round"/>' for x in (-220, -120, -20, 80))
    bigotes = "".join(f'<path d="M560,{-612 + k * 16} L{690 + k * 10},{-640 + k * 26}" stroke="#ffffff" stroke-width="5" stroke-linecap="round"/>' for k in range(3))
    bigotes += "".join(f'<path d="M520,{-612 + k * 16} L{400 - k * 6},{-650 + k * 30}" stroke="#ffffff" stroke-width="4" stroke-linecap="round" opacity="0.85"/>' for k in range(3))
    s = (f'<svg id="gato" style="position:absolute;left:0;top:0;overflow:visible;opacity:0" width="1" height="1"><g transform="translate({GX} {FL})"><g id="gatoG">'
         '<defs><linearGradient id="gPelo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffb347"/><stop offset="1" stop-color="#ff8c1a"/></linearGradient>'
         '<radialGradient id="gOjo" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#e8ff7a"/><stop offset="1" stop-color="#7cc414"/></radialGradient></defs>'
         '<ellipse cx="40" cy="0" rx="430" ry="34" fill="#000" opacity="0.18"/>'
         # cola
         '<g id="gCola"><path d="M-300,-470 C-430,-480 -500,-600 -470,-740 C-460,-790 -420,-800 -400,-770" stroke="url(#gPelo)" stroke-width="64" fill="none" stroke-linecap="round"/>'
         '<path d="M-440,-540 L-470,-560 M-470,-640 L-500,-650 M-450,-720 L-490,-715" stroke="#e0761a" stroke-width="20" stroke-linecap="round"/>'
         '<circle cx="-400" cy="-770" r="34" fill="#fff3e0"/></g>'
         # patas de detrás (lejanas, más oscuras)
         + pata("gPF1", -210, "#e98a1f", "#f5e6d3") + pata("gPF2", 210, "#e98a1f", "#f5e6d3") +
         # cuerpo con barriga, rayas y pecho
         '<g id="gCuerpo"><path d="M-340,-430 C-350,-580 -170,-630 40,-620 C230,-612 350,-560 360,-450 C370,-330 260,-280 60,-280 C-160,-280 -330,-300 -340,-430 Z" fill="url(#gPelo)"/>'
         '<path d="M-260,-330 C-120,-300 120,-300 300,-340 C290,-300 220,-282 60,-282 C-120,-282 -230,-295 -260,-330 Z" fill="#ffe2bf"/>'
         + rayas + '</g>'
         # patas de delante (cercanas) con calcetines blancos
         + pata("gPN1", -190, "#ffa63d", "#ffffff") + pata("gPN2", 230, "#ffa63d", "#ffffff") +
         # cabeza
         '<g id="gCab"><path d="M250,-520 C260,-600 330,-640 400,-640 L420,-500 Z" fill="url(#gPelo)"/>'
         '<rect x="250" y="-540" width="190" height="34" rx="16" fill="#ef233c" transform="rotate(-18 345 -523)"/><circle cx="372" cy="-500" r="24" fill="#ffd23f" stroke="#c99a00" stroke-width="4"/><path d="M360,-498 L384,-498" stroke="#8a6a00" stroke-width="4"/>'
         '<path d="M330,-760 L360,-900 L440,-790 Z" fill="#ff9f1c"/><path d="M350,-780 L365,-860 L415,-795 Z" fill="#ffb3c6"/>'
         '<path d="M455,-790 L520,-910 L570,-770 Z" fill="#ffa63d"/><path d="M475,-795 L518,-870 L550,-780 Z" fill="#ffb3c6"/>'
         '<ellipse cx="450" cy="-650" rx="185" ry="160" fill="url(#gPelo)"/>'
         '<path d="M290,-600 L262,-575 L292,-565 L266,-540 L300,-535 L285,-505 L330,-520 Z" fill="#ffb347"/>'
         '<ellipse cx="545" cy="-590" rx="78" ry="56" fill="#fff3e0"/>'
         '<path d="M400,-780 C410,-740 405,-720 395,-700 M450,-795 C455,-750 452,-730 446,-710 M500,-790 C500,-750 498,-735 494,-715" stroke="#e0761a" stroke-width="14" fill="none" stroke-linecap="round"/>'
         # ojos (el cercano grande, el lejano más pequeño) con pupilas que se dilatan
         '<g id="gOjos"><ellipse cx="455" cy="-660" rx="44" ry="52" fill="url(#gOjo)" stroke="#3b2f2f" stroke-width="5"/>'
         '<ellipse class="gPup" cx="465" cy="-656" rx="12" ry="40" fill="#1d1b26"/><circle cx="448" cy="-680" r="11" fill="#fff"/><circle cx="476" cy="-640" r="5" fill="#fff"/>'
         '<ellipse cx="580" cy="-664" rx="30" ry="46" fill="url(#gOjo)" stroke="#3b2f2f" stroke-width="5"/>'
         '<ellipse class="gPup" cx="588" cy="-660" rx="9" ry="34" fill="#1d1b26"/><circle cx="576" cy="-680" r="8" fill="#fff"/></g>'
         '<g id="gPar" opacity="0"><ellipse cx="455" cy="-660" rx="47" ry="55" fill="#ff9f1c"/><ellipse cx="580" cy="-664" rx="33" ry="49" fill="#ff9f1c"/>'
         '<path d="M412,-660 Q455,-640 498,-660 M552,-664 Q580,-646 608,-664" stroke="#3b2f2f" stroke-width="6" fill="none"/></g>'
         '<path d="M600,-612 L640,-612 L620,-588 Z" fill="#ff6b8a"/><path d="M620,-588 L620,-572 M590,-562 C600,-552 612,-556 620,-572 C628,-556 640,-552 650,-562" stroke="#7a3b10" stroke-width="6" fill="none" stroke-linecap="round"/>'
         + bigotes + '</g>'
         '</g></g></svg>')
    return s

def gato_andar(t, dx, dur, pasos):
    """Camina de perfil: patas en diagonal (como los gatos de verdad), lomo que sube y baja, cola que se mece."""
    J(f'tl.to("#gatoG", {{x:"+={dx}", duration:{dur}, ease:"none"}}, {t:.2f});')
    ciclos = max(1, round(pasos / 2)); c = dur / ciclos
    for idd, ox, s in (("gPN1", -190, 1), ("gPF2", 210, 1), ("gPF1", -210, -1), ("gPN2", 230, -1)):
        J(f'tl.to("#{idd}", {{keyframes:{{rotation:[{-22 * s}, {22 * s}, {-22 * s}], easeEach:"sine.inOut"}}, duration:{c:.3f}, repeat:{ciclos - 1}, ease:"none", svgOrigin:"{ox} -380"}}, {t:.2f});')
    J(f'tl.to(["#gCuerpo", "#gCab"], {{keyframes:{{y:[0, -12, 0, -12, 0]}}, duration:{c:.3f}, repeat:{ciclos - 1}, ease:"none"}}, {t:.2f});')
    J(f'tl.set(["#gPN1", "#gPN2", "#gPF1", "#gPF2"], {{rotation:0}}, {t + dur:.2f});')

def gato_vida(t0, t1):
    """Cola que se mece, parpadeos y respiración."""
    n = max(1, int((t1 - t0) / 1.8))
    J(f'tl.to("#gCola", {{keyframes:{{rotation:[0, 9, 0, -7, 0]}}, duration:1.8, repeat:{n - 1}, ease:"none", svgOrigin:"-300 -470"}}, {t0:.2f});')
    J(f'tl.to("#gCuerpo", {{scaleY:1.025, duration:0.9, yoyo:true, repeat:{2 * n - 1}, ease:"sine.inOut", svgOrigin:"0 -280"}}, {t0:.2f});')
    t = t0 + 0.9
    while t < t1:
        J(f'tl.to("#gPar", {{opacity:1, duration:0.06, yoyo:true, repeat:1}}, {t:.2f});')
        t += 2.3

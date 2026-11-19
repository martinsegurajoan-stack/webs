# Personaje de PERFIL (mirando a la derecha) con articulaciones reales: cada parte es un grupo que gira en su articulación.
# Medidas en «cm» (persona de ~178 cm). La raíz está en la cadera. Ángulos ABSOLUTOS en grados (0 = derecha, 90 = abajo, -90 = arriba).
import math as _m
RL = dict(T=58, N=7, UA=29, FA=26, TH=43, SH=41)
def _osc(c, k):
    c = c.lstrip("#"); r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    return "#%02x%02x%02x" % (int(r * k), int(g * k), int(b * k))
def _cap(L, w0, w1, fill, rid):
    return (f'<path d="M0,{-w0 / 2:.1f} L{L},{-w1 / 2:.1f} A{w1 / 2:.1f},{w1 / 2:.1f} 0 0 1 {L},{w1 / 2:.1f} L0,{w0 / 2:.1f} A{w0 / 2:.1f},{w0 / 2:.1f} 0 0 1 0,{-w0 / 2:.1f} Z" fill="{fill}"/>'
            f'<path d="M0,{w0 / 6:.1f} L{L},{w1 / 6:.1f} L{L},{w1 / 2:.1f} L0,{w0 / 2:.1f} Z" fill="#000" opacity="0.13"/>')
GRADS = []
def rig(pid, c):
    """c: piel, pelo, camisa, pantalon, zapato. Devuelve el SVG (raíz en la cadera, mira a la derecha)."""
    p, s, t, z = c["piel"], c["camisa"], c["pantalon"], c["zapato"]
    pf, sf, tf = _osc(p, 0.82), _osc(s, 0.78), _osc(t, 0.78)
    def brazo(lado, sc, pc):
        return (f'<g id="{pid}_ua{lado}">{_cap(RL["UA"], 11, 9.5, sc, "")}'
                f'<g transform="translate({RL["UA"]},0)"><g id="{pid}_fa{lado}">{_cap(RL["FA"], 9, 7.5, sc, "")}'
                f'<path d="M{RL["FA"] - 6},-4.2 L{RL["FA"]},-3.6 L{RL["FA"]},3.6 L{RL["FA"] - 6},4.2 Z" fill="{pc}"/>'
                f'<g transform="translate({RL["FA"] + 3},0)"><ellipse rx="5.2" ry="4.3" fill="{pc}"/><ellipse cx="1.5" cy="-3.6" rx="2.4" ry="1.6" fill="{pc}"/>'
                f'<g id="{pid}_mano{lado}"></g></g></g></g></g>')
    def pierna(lado, tc, zc):
        return (f'<g id="{pid}_th{lado}">{_cap(RL["TH"], 16, 13, tc, "")}'
                f'<g transform="translate({RL["TH"]},0)"><g id="{pid}_sh{lado}">{_cap(RL["SH"], 12.5, 10, tc, "")}'
                f'<g transform="translate({RL["SH"]},0)"><g transform="rotate(-90)"><path d="M-6,-3 L-6,4 Q-6,8 0,8 L17,8 Q21,8 21,4 Q21,0 14,-1 L6,-3 Z" fill="{zc}"/>'
                f'<path d="M-6,6 L21,6 L21,8 L-6,8 Z" fill="#ffffff" opacity="0.25"/></g></g></g></g></g>')
    torso = (f'<path d="M-2,-12 L{RL["T"] - 6},-11 Q{RL["T"] + 2},-10 {RL["T"] + 2},-1 L{RL["T"] + 1},9 Q{RL["T"] - 8},15 {RL["T"] - 20},14 L6,13 Q-3,12 -3,0 Z" fill="{s}"/>'
             f'<path d="M-2,-12 L{RL["T"] - 6},-11 Q{RL["T"] + 2},-10 {RL["T"] + 2},-1 L{RL["T"] - 4},-1 L0,-4 Z" fill="#000" opacity="0.12"/>'
             f'<path d="M{RL["T"] - 2},2 L{RL["T"] - 10},8 M{RL["T"] - 2},2 L{RL["T"] - 8},-4" stroke="{sf}" stroke-width="1.6" fill="none"/>'
             f'<path d="M4,13 L{RL["T"] - 30},13.5" stroke="{sf}" stroke-width="1.4"/>'
             f'<rect x="-5" y="-12.5" width="11" height="26" rx="5" fill="{t}"/><rect x="5" y="-12.5" width="2.6" height="26" fill="#1d1d24" opacity="0.5"/>')
    cabeza = (f'<g transform="rotate(90)">'
              f'<path d="M-4,0 L-4,-9 L4,-9 L4,0 Z" fill="{pf}"/>'
              f'<path d="M-9,-20 Q-10,-35 3,-36 Q15,-36 15,-24 L16.5,-20 Q17.5,-18 15,-17.5 L15,-13 Q15,-9.5 11,-9.5 L6,-9.5 Q2,-6 -4,-8 Q-9,-11 -9,-20 Z" fill="{p}"/>'
              f'<path d="M-9,-20 Q-9,-12 -4,-8 Q0,-7 3,-8 Q-3,-12 -4,-20 Z" fill="#000" opacity="0.1"/>'
              f'<path id="{pid}_pelo" d="M-10.5,-19 Q-13,-38 4,-39 Q17,-39 16.5,-28 Q13,-31 8,-30 Q4,-29 1,-27 Q0,-23 -2,-21 L-3,-15 Q-8,-14 -10.5,-19 Z" fill="{c["pelo"]}"/>'
              f'<ellipse cx="-2" cy="-20" rx="3.2" ry="4.4" fill="{pf}"/><path d="M-2.5,-22 q2,2 0,4" stroke="{_osc(p, 0.65)}" stroke-width="1" fill="none"/>'
              f'<g id="{pid}_ojo"><path d="M7,-24.6 Q10,-26.6 13,-24.6 Q10,-22.4 7,-24.6 Z" fill="#ffffff"/><g id="{pid}_rojo" opacity="0"><path d="M7,-24.6 Q10,-26.6 13,-24.6 Q10,-22.4 7,-24.6 Z" fill="#ff8a8a"/></g>'
              f'<circle cx="11.2" cy="-24.6" r="1.35" fill="#2a1a14"/><path id="{pid}_par" d="M6.6,-24.8 Q10,-27.4 13.4,-24.8 L13.4,-26.8 L6.6,-26.8 Z" fill="{p}"/>'
              f'<path d="M6.5,-24.6 Q10,-27 13.4,-24.8" stroke="#2a1a14" stroke-width="0.9" fill="none"/></g>'
              f'<path id="{pid}_ceja" d="M6.5,-28.4 Q10,-29.6 13.6,-28.2" stroke="{c["pelo"]}" stroke-width="1.5" fill="none" stroke-linecap="round"/>'
              f'<g id="{pid}_ojera" opacity="0"><path d="M7.5,-22.2 Q10,-21 12.6,-22.2" stroke="#7a5a8a" stroke-width="1" fill="none"/></g>'
              f'<path d="M14.6,-17.6 L12.4,-17.2" stroke="{_osc(p, 0.7)}" stroke-width="0.9"/>'
              f'<path id="{pid}_boca" d="M10.6,-12.8 Q12.6,-12 14,-13" stroke="#7a3b2c" stroke-width="1.2" fill="none" stroke-linecap="round"/>'
              f'<path id="{pid}_bocaT" d="M10.6,-12.2 Q12.6,-13.6 14,-12.4" stroke="#7a3b2c" stroke-width="1.2" fill="none" stroke-linecap="round" opacity="0"/>'
              f'<circle id="{pid}_glow" cx="12" cy="-22" r="24" fill="url(#glowP)" opacity="0"/></g>')
    return (f'<g id="{pid}"><g id="{pid}_fl">'
            f'<ellipse id="{pid}_sombra" cx="0" cy="84" rx="30" ry="5" fill="#000" opacity="0.28"/>'
            f'{pierna("F", tf, _osc(z, 0.8))}'
            f'<g id="{pid}_tor"><g transform="translate({RL["T"] - 5},1)">{brazo("F", sf, pf)}</g>{torso}'
            f'<g transform="translate({RL["T"]},0)"><g id="{pid}_hd">{cabeza}</g></g>'
            f'<g transform="translate({RL["T"] - 5},1)">{brazo("N", s, p)}</g></g>'
            f'{pierna("N", t, z)}</g></g>')
PR = {
    "pie":      dict(tor=-90, hd=-90, uaN=95, faN=85, uaF=86, faF=80, thN=92, shN=90, thF=88, shF=90),
    "anda1":    dict(tor=-88, hd=-90, uaN=70, faN=50, uaF=110, faF=100, thN=65, shN=95, thF=112, shF=120),
    "anda2":    dict(tor=-88, hd=-90, uaN=110, faN=100, uaF=70, faF=50, thN=112, shN=120, thF=65, shF=95),
    "movilPie": dict(tor=-88, hd=-55, uaN=80, faN=-40, uaF=82, faF=-30, thN=92, shN=90, thF=88, shF=90),
    "sentMovil":dict(tor=-80, hd=-40, uaN=72, faN=-32, uaF=76, faF=-26, thN=2, shN=92, thF=6, shF=94),
    "sentMovil2":dict(tor=-78, hd=-36, uaN=74, faN=-28, uaF=78, faF=-22, thN=2, shN=92, thF=6, shF=94),
    "teclea":   dict(tor=-86, hd=-74, uaN=68, faN=4, uaF=64, faF=-2, thN=0, shN=92, thF=4, shF=94),
    "teclea2":  dict(tor=-86, hd=-74, uaN=66, faN=-2, uaF=66, faF=4, thN=0, shN=92, thF=4, shF=94),
    "zombi":    dict(tor=-74, hd=-50, uaN=74, faN=10, uaF=70, faF=6, thN=0, shN=92, thF=4, shF=94),
    "cuello":   dict(tor=-80, hd=-62, uaN=-120, faN=40, uaF=70, faF=6, thN=0, shN=92, thF=4, shF=94),
    "cabeza":   dict(tor=-78, hd=-70, uaN=-35, faN=-150, uaF=70, faF=6, thN=0, shN=92, thF=4, shF=94),
    "arriba":   dict(tor=-94, hd=-108, uaN=72, faN=8, uaF=68, faF=4, thN=0, shN=92, thF=4, shF=94),
    "bolsillo": dict(tor=-86, hd=-60, uaN=100, faN=40, uaF=70, faF=6, thN=0, shN=92, thF=4, shF=94),
    "tumbado":  dict(tor=-90, hd=-90, uaN=92, faN=88, uaF=88, faF=84, thN=90, shN=90, thF=90, shF=90),
    "tumbMovil":dict(tor=-90, hd=-70, uaN=10, faN=-80, uaF=88, faF=84, thN=90, shN=90, thF=90, shF=90),
    "sentado":  dict(tor=-88, hd=-88, uaN=86, faN=30, uaF=82, faF=24, thN=2, shN=92, thF=6, shF=94),
}
PADRE = dict(hd="tor", uaN="tor", faN="uaN", uaF="tor", faF="uaF", shN="thN", shF="thF", tor=None, thN=None, thF=None)
def rpose(J, pid, nombre, t, d=0.3, ease="power2.inOut", solo=None):
    a = PR[nombre]
    for k, par in PADRE.items():
        if solo and k not in solo:
            continue
        rel = a[k] - (a[par] if par else 0)
        J(f'tl.to("#{pid}_{k}", {{rotation:{rel:.1f}, svgOrigin:"0 0", duration:{d}, ease:"{ease}"}}, {t:.3f});')
def rset(J, pid, nombre, t=0):
    a = PR[nombre]
    for k, par in PADRE.items():
        rel = a[k] - (a[par] if par else 0)
        J(f'tl.set("#{pid}_{k}", {{rotation:{rel:.1f}, svgOrigin:"0 0"}}, {t:.3f});')

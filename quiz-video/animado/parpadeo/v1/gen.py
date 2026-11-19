#!/usr/bin/env python3
"""«¿Qué pasaría si cada vez que parpadeas crecieras 0,001 mm?» — UN SOLO PLANO que sigue al protagonista (rig de perfil)
mientras crece en su jardín. La cámara se aleja a la vez que él crece (siempre ocupa lo mismo en pantalla) y el mundo
(puerta, canasta, Robert Wadlow…) se encoge a su lado. Sin efectos de sonido. Bucle: empieza y acaba en primer plano del ojo.
  python3 gen.py → index.html + efectos.json + ambiente.json"""
import json, os, random, re, unicodedata

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
tl, FXL = [], []
def J(s): tl.append(s)
exec(open(os.path.join(BASE, "_rig.py"), encoding="utf-8").read())

# ------------------------------------------------------------------ mundo (unidades del rig: 189 u = 1,75 m)
U = 189 / 1.75                     # unidades por metro
PIEL, PELO = "#e8b896", "#3b2a20"
PROTA = dict(piel=PIEL, pelo=PELO, camisa="#3d7cc9", pantalon="#2f3640", zapato="#f4f4f4")
GRIS = dict(piel="#b9c0c8", pelo="#9aa3ad", camisa="#a9b1ba", pantalon="#8e97a1", zapato="#9aa3ad")
PR["suelo"] = dict(tor=-90, hd=-90, uaN=118, faN=104, uaF=112, faF=98, thN=0, shN=0, thF=-3, shF=-3)

def figura(pid, col):
    s = rig(pid, col).replace('cy="84"', 'cy="92"')
    # tobillos (piel bajo el pantalón que se queda corto) y piernas en rojo (presión en los huesos)
    for lado in ("N", "F"):
        s = s.replace(f'<g id="{pid}_sh{lado}">', f'<g id="{pid}_sh{lado}">' + "§SH§", 1)
    parts = s.split("§SH§")
    out = parts[0]
    for p in parts[1:]:
        k = p.index('<g transform="translate(41,0)">')
        out += (p[:k] + f'<rect class="{pid}tob" x="27" y="-5.6" width="14.5" height="11.2" fill="{col["piel"]}" opacity="0"/>'
                + f'<path class="{pid}dolor" d="M2,-5 L39,-4 L39,4 L2,5 Z" fill="#ff4b3e" opacity="0"/>' + p[k:])
    out = re.sub(rf'(<g id="{pid}_th[NF]">)(.*?)(<g transform="translate\(43,0\)">)',
                 lambda m: m.group(1) + m.group(2) + f'<path class="{pid}dolor" d="M2,-7 L41,-6 L41,6 L2,7 Z" fill="#ff4b3e" opacity="0"/>' + m.group(3), out, flags=re.S)
    return out

M = []
M.append('<rect x="-4000" y="0" width="8000" height="3000" fill="#7cb85a"/>')
M.append('<rect x="-4000" y="0" width="8000" height="10" fill="#6aa64a"/>')
M.append('<path d="M-4000,-40 Q-3200,-420 -2300,-60 Q-1700,-330 -1000,-40 L-1000,0 L-4000,0 Z" fill="#a9cf8e"/>')
M.append('<path d="M900,-30 Q1700,-480 2600,-40 Q3200,-300 4000,-60 L4000,0 L900,0 Z" fill="#a9cf8e"/>')
M.append('<path d="M-60,0 L60,0 L220,3000 L-220,3000 Z" fill="#d8c9a6"/>')   # camino hacia la cámara
for k in range(60):                                                          # hierba y flores
    x = -1500 + k * 53 + (k * 37) % 23
    M.append(f'<path d="M{x},2 l3,-9 l3,9" fill="#5c9a3e"/>')
    if k % 4 == 1: M.append(f'<circle cx="{x + 9}" cy="-4" r="3.2" fill="{["#ffd23f", "#ff8fa3", "#ffffff"][k % 3]}"/>')
# casa (fachada lateral a la izquierda, puerta de 2,03 m junto al protagonista)
HX0, HX1 = -620, -70
HW, HR = 560, 780
M.append(f'<rect x="{HX0}" y="{-HW}" width="{HX1 - HX0}" height="{HW}" fill="#f3ead8"/>')
M.append(f'<rect x="{HX0}" y="{-HW}" width="{HX1 - HX0}" height="16" fill="#e2d6bd"/>')
M.append(f'<path d="M{HX0 - 40},{-HW} L{(HX0 + HX1) / 2},{-HR} L{HX1 + 40},{-HW} Z" fill="#c8664a"/>')
M.append(f'<path d="M{HX0 - 40},{-HW} L{(HX0 + HX1) / 2},{-HR} L{(HX0 + HX1) / 2},{-HR + 14} L{HX0 - 22},{-HW} Z" fill="#000" opacity="0.08"/>')
DX0, DX1, DH = -170, -82, 2.03 * U
M.append(f'<rect x="{DX0 - 8}" y="{-DH - 8}" width="{DX1 - DX0 + 16}" height="{DH + 8}" fill="#d9ccb1"/>')
M.append(f'<rect id="puerta" x="{DX0}" y="{-DH}" width="{DX1 - DX0}" height="{DH}" fill="#7a4b32"/>')
M.append(f'<rect x="{DX0 + 10}" y="{-DH + 14}" width="{DX1 - DX0 - 20}" height="70" fill="#6a3f29"/><rect x="{DX0 + 10}" y="{-DH + 98}" width="{DX1 - DX0 - 20}" height="90" fill="#6a3f29"/>')
M.append(f'<circle cx="{DX1 - 14}" cy="{-DH / 2 + 6}" r="4" fill="#e9c46a"/>')
for wx, wy in ((-520, -460), (-360, -460), (-520, -250), (-360, -250)):
    M.append(f'<rect x="{wx}" y="{wy}" width="100" height="120" fill="#ffffff"/><rect x="{wx + 8}" y="{wy + 8}" width="84" height="104" fill="#9fd3f0"/>'
             f'<path d="M{wx + 50},{wy + 8} V{wy + 112} M{wx + 8},{wy + 60} H{wx + 92}" stroke="#ffffff" stroke-width="6"/>')
M.append(f'<rect x="{HX0 + 330}" y="{-HR + 60}" width="50" height="120" fill="#a9553c"/>')   # chimenea
# farola, valla, árbol, arbustos
M.append('<rect x="-760" y="-430" width="10" height="430" fill="#3a4250"/><path d="M-755,-430 q0,-30 40,-30" stroke="#3a4250" stroke-width="8" fill="none"/><ellipse cx="-712" cy="-452" rx="16" ry="10" fill="#ffe7a3"/>')
for k in range(16):
    x = 330 + k * 46
    M.append(f'<rect x="{x}" y="-118" width="18" height="118" rx="3" fill="#ffffff"/><path d="M{x},-118 l9,-12 l9,12 Z" fill="#ffffff"/>')
M.append('<rect x="320" y="-92" width="760" height="12" fill="#f1f1f1"/><rect x="320" y="-46" width="760" height="12" fill="#f1f1f1"/>')
M.append('<rect x="560" y="-330" width="36" height="330" fill="#8a5a3c"/><circle cx="578" cy="-470" r="190" fill="#4f9a48"/><circle cx="470" cy="-390" r="120" fill="#5aa752"/><circle cx="690" cy="-400" r="130" fill="#5aa752"/><circle cx="600" cy="-560" r="110" fill="#67b25c"/>')
for bx in (-260, -330, 250, 1050):
    M.append(f'<ellipse cx="{bx}" cy="-24" rx="46" ry="34" fill="#4f9a48"/><ellipse cx="{bx + 28}" cy="-18" rx="34" ry="26" fill="#5aa752"/>')
# canasta de baloncesto (aro a 3,05 m)
AR = 3.05 * U
M.append(f'<rect x="232" y="{-AR - 70}" width="14" height="{AR + 70}" fill="#3a4250"/><path d="M239,{-AR - 40} L205,{-AR - 40}" stroke="#3a4250" stroke-width="10"/>'
         f'<rect x="196" y="{-AR - 92}" width="10" height="104" fill="#ffffff" stroke="#c9d1da" stroke-width="2"/><rect x="198" y="{-AR - 50}" width="6" height="34" fill="none" stroke="#ef5b3b" stroke-width="2"/>'
         f'<path d="M196,{-AR} L150,{-AR}" stroke="#ef5b3b" stroke-width="6" stroke-linecap="round"/><path d="M152,{-AR} l6,30 l26,0 l8,-30" stroke="#ffffff" stroke-width="2" fill="none" opacity="0.9"/>')
# líneas de referencia (discontinuas, grosor fijo en pantalla)
def linea(i, y, x0, x1):
    return f'<path id="ref{i}" d="M{x0},{-y} H{x1}" stroke="#ffffff" stroke-width="3" stroke-dasharray="10 8" vector-effect="non-scaling-stroke" opacity="0"/>'
M.append(linea("cama", 1.90 * U, -40, 120))
M.append(linea("puerta", DH, DX0 - 8, 120))
M.append(linea("aro", AR, 60, 196))
# Robert Wadlow (2,72 m) en gris, mirando al protagonista
WAD = 2.72 / 1.75
M.append(f'<g id="wad" opacity="0"><g transform="translate(140,0) scale({-WAD:.3f},{WAD:.3f})"><g transform="translate(0,-92)">{figura("W", GRIS)}</g></g></g>')

# protagonista: #crece (escala desde los pies) > #sentar (altura de la cadera) > rig
EXTRA_P = ('<g transform="translate(40,-172)"><g id="zz" opacity="0"><text x="0" y="0" font-family="Inter" font-weight="800" font-size="22" fill="#ffffff">Z</text>'
           '<text x="16" y="-20" font-family="Inter" font-weight="800" font-size="16" fill="#ffffff">z</text></g></g>'
           '<g id="corazon" opacity="0"><path d="M24,-138 L24,-170" stroke="#ff4b3e" stroke-width="2.4" stroke-dasharray="4 3" fill="none"/>'
           '<path d="M19,-168 L24,-176 L29,-168" stroke="#ff4b3e" stroke-width="2.4" fill="none" stroke-linejoin="round"/>'
           '<g transform="translate(24,-128)"><g id="lat"><path d="M0,6 C-12,-3 -10,-13 -4,-13 C-1,-13 0,-10 0,-9 C0,-10 1,-13 4,-13 C10,-13 12,-3 0,6 Z" fill="#ff4b3e" stroke="#ffffff" stroke-width="1.6"/></g></g></g>'
           '<g id="lagrima" opacity="0"><path d="M30,-162 q-3,6 0,9 q3,-3 0,-9 Z" fill="#9fdcff"/></g>')
PROT = f'<g id="crece"><g id="sentar"><g transform="translate(0,-92)">{figura("P", PROTA)}</g></g>{EXTRA_P}</g>'
WORLD = "".join(M) + PROT

# ------------------------------------------------------------------ helpers de animación
def h(t, metros, d, ease="power1.inOut"):
    J(f'tl.to(S, {{h:{metros}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
def cam(t, d=1.2, ease="power2.inOut", **kv):
    J(f'tl.to(S, {{{", ".join(f"{k}:{v}" for k, v in kv.items())}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
NB = [0]
PARP = []
def parpadeo(t, pop=False):
    PARP.append(t)
    J(f'tl.to("#P_ojo", {{scaleY:0.08, svgOrigin:"10 -24.6", duration:0.07, ease:"power1.in"}}, {t:.2f}); tl.to("#P_ojo", {{scaleY:1, svgOrigin:"10 -24.6", duration:0.09, ease:"power1.out"}}, {t + 0.09:.2f});')
    if pop:
        NB[0] += 1; i = NB[0]
        FXL.append(f'<div class="pop" id="pp{i}">+0,001 mm</div>')
        J(f'tl.set("#pp{i}", {{opacity:0}}, 0); tl.fromTo("#pp{i}", {{opacity:0, y:0}}, {{opacity:1, y:-60, duration:0.35, ease:"power2.out", immediateRender:false}}, {t + 0.05:.2f}); tl.to("#pp{i}", {{opacity:0, duration:0.4}}, {t + 0.9:.2f});')
NC = [0]
def card(html, t, hasta, top=700, left=40, w=360, cls=""):
    NC[0] += 1; i = NC[0]
    FXL.append(f'<div class="card {cls}" id="c{i}" style="top:{top}px;left:{left}px;width:{w}px">{html}</div>')
    J(f'tl.set("#c{i}", {{opacity:0}}, 0); tl.fromTo("#c{i}", {{opacity:0, x:-30}}, {{opacity:1, x:0, duration:0.45, ease:"power3.out", immediateRender:false}}, {t:.2f}); tl.to("#c{i}", {{opacity:0, x:-20, duration:0.3}}, {hasta:.2f});')
    return f"#c{i}"
def contador(sel, v0, v1, t, d, dec=0, suf=""):
    NC[0] += 1
    J(f'(() => {{ const o = {{v:{v0}}}; tl.to(o, {{v:{v1}, duration:{d:.2f}, ease:"power2.out", onUpdate:() => {{ document.querySelector("{sel}").textContent = fmt(o.v, {dec}) + "{suf}"; }}}}, {t:.2f}); }})();')
NL = [0]
def etiqueta(p, t, hasta, txt, dx=24, dy=-10):
    NL[0] += 1; i = NL[0]
    FXL.append(f'<div class="lab" id="lb{i}">{txt}</div>')
    J(f'LABS.push({{i:{i}, x:{p[0]:.1f}, y:{p[1]:.1f}, dx:{dx}, dy:{dy}}}); LV.l{i} = 0;')
    J(f'tl.to(LV, {{l{i}:1, duration:0.4}}, {t:.2f}); tl.to(LV, {{l{i}:0, duration:0.3}}, {hasta:.2f});')
def ref(nombre, t, hasta):
    J(f'tl.to("#ref{nombre}", {{opacity:0.9, duration:0.4}}, {t:.2f}); tl.to("#ref{nombre}", {{opacity:0, duration:0.4}}, {hasta:.2f});')

# ------------------------------------------------------------------ GUION VISUAL (un solo plano)
rset(J, "P", "pie"); rset(J, "W", "pie")
# 1) gancho: primer plano del ojo + «0,001 mm»; parpadea y la cámara se abre al cuerpo entero
FXL.append('<div id="gancho" class="grande"><b>0,001 mm</b><small>CADA VEZ QUE PARPADEAS</small></div>')
J(f'tl.to("#gancho", {{opacity:0, y:20, duration:0.4}}, {FE(1) - 0.2:.2f});')
parpadeo(P("parpadeas") + 0.1, pop=True)
cam(FE(1) - 0.4, 2.2, "power2.inOut", ojo=0)
# 2) 15.000 veces al día
for k, t in enumerate((F(2) + 0.6, P("quince") - 0.2, P("dia") - 0.3)):
    parpadeo(t, pop=True)
card('<small>PARPADEOS AL DÍA</small><b><span id="n15">0</span></b><em>solo despierto</em>', P("quince") - 0.3, FE(2) + 0.3)
contador("#n15", 0, 15000, P("quince") - 0.2, 1.3)
# 3) no puedes evitarlo: ojos rojos, lágrima, sin parpadear
J(f'tl.to("#P_rojo", {{opacity:0.75, duration:1.2}}, {P("aguantas"):.2f}); tl.to("#P_rojo", {{opacity:0, duration:0.4}}, {FE(3) + 0.1:.2f});')
J(f'tl.fromTo("#lagrima", {{opacity:0, y:0}}, {{opacity:1, y:22, duration:1.2, ease:"power1.in", immediateRender:false}}, {P("arden") - 0.4:.2f}); tl.to("#lagrima", {{opacity:0, duration:0.2}}, {P("arden") + 0.8:.2f});')
cam(P("aguantas") - 0.2, 1.4, ojo=0.55)
card('<small>SIN PARPADEAR</small><b>ojos secos</b><em>arden en segundos</em>', P("secan") - 0.3, FE(3) + 0.2)
parpadeo(FE(3) + 0.05)
cam(FE(3) - 0.1, 1.2, ojo=0)
# 4) 1,5 cm al día; de noche no parpadeas
J(f'tl.to("#hud", {{opacity:1, y:0, duration:0.5, ease:"power3.out"}}, {F(4):.2f});')
h(F(4) + 0.3, 1.765, 2.2)
card('<small>CRECES</small><b>1,5 cm</b><em>cada día</em>', P("centimetro") - 0.2, P("despierto") - 0.1)
J(f'tl.to("#noche", {{opacity:0.62, duration:0.6}}, {P("duermes") - 0.5:.2f}); tl.to("#noche", {{opacity:0, duration:0.6}}, {FE(4) + 0.1:.2f});')
J(f'tl.to("#P_ojo", {{scaleY:0.08, svgOrigin:"10 -24.6", duration:0.25}}, {P("duermes") - 0.4:.2f}); tl.to("#P_ojo", {{scaleY:1, svgOrigin:"10 -24.6", duration:0.2}}, {FE(4) + 0.1:.2f});')
J(f'tl.fromTo("#zz", {{opacity:0, y:0}}, {{opacity:1, y:-10, duration:0.6, immediateRender:false}}, {P("duermes") - 0.2:.2f}); tl.to("#zz", {{opacity:0, duration:0.3}}, {FE(4):.2f});')
card('<small>DORMIDO</small><b>0 parpadeos</b><em>no creces</em>', P("duermes") - 0.2, FE(4) + 0.1)
# 5) una semana: +10 cm, pantalones cortos
h(F(5), 1.855, P("tobillo") - F(5))
J(f'tl.to(".Ptob", {{opacity:1, duration:0.5}}, {P("pantalones"):.2f});')
etiqueta((44, -6), P("pantalones"), FE(5) + 0.2, "pantalones cortos", dx=30, dy=-60)
card('<small>1 SEMANA</small><b>+10 cm</b>', P("semana") - 0.2, FE(5) + 0.2)
# 6) diez días: 1,90 m, la cama
h(F(6), 1.90, FE(6) - F(6))
ref("cama", P("diez", 2) - 0.2, FE(6) + 0.4)
etiqueta((120, -1.90 * U), P("diez", 2), FE(6) + 0.4, "cama · 1,90 m", dx=12, dy=-44)
# 7) tres semanas: pasa los 2 m, la puerta
h(F(7), 2.065, P("marco") - F(7))
cam(F(7) - 0.2, 1.0, fx=-55)
ref("puerta", P("marco") - 0.6, FE(7) + 0.4)
etiqueta((120, -DH), P("marco") - 0.5, FE(7) + 0.4, "puerta · 2,03 m", dx=12, dy=-44)
J(f'tl.to("#P_hd", {{rotation:12, svgOrigin:"0 0", duration:0.25, ease:"power2.out"}}, {P("marco") - 0.1:.2f}); tl.to("#P_hd", {{rotation:0, svgOrigin:"0 0", duration:0.4}}, {P("puerta") + 0.3:.2f});')
cam(FE(7), 1.0, fx=0)
# 8) un mes: 2,20 m
h(F(8), 2.20, P("veinte") - F(8) + 0.3)
card('<small>1 MES</small><b>2,20 m</b>', P("mes") - 0.2, FE(8) + 0.2)
J(f'tl.to("#hud", {{scale:1.06, duration:0.25, yoyo:true, repeat:1}}, {P("problema") - 0.2:.2f});')
# 9) ley del cubo: altura ×2, peso ×8, huesos ×4
CUBOS = ('<svg viewBox="0 0 300 120" width="320" height="128"><g fill="#4ea3ff" stroke="#ffffff" stroke-width="2">'
         '<rect x="10" y="70" width="40" height="40"/>'
         + "".join(f'<rect x="{110 + i * 40}" y="{30 + j * 40}" width="40" height="40" opacity="{0.55 + 0.45 * ((i + j) % 2)}"/>' for i in range(2) for j in range(2))
         + '</g><text x="200" y="65" font-family="Inter" font-weight="800" font-size="34" fill="#ffffff">→ ×8</text></svg>')
card(f'<small>SI MIDES EL DOBLE</small>{CUBOS}<div class="filas"><p id="f1">Altura <b>×2</b></p><p id="f2">Peso <b class="r">×8</b></p><p id="f3">Huesos <b>×4</b></p></div>', F(9) - 0.1, FE(9) + 0.3, top=640, w=380)
for k, (w, n) in enumerate((("duplica", 1), ("ocho", 1), ("cuatro", 1)), 1):
    J(f'tl.set("#f{k}", {{opacity:0.25}}, 0); tl.to("#f{k}", {{opacity:1, duration:0.3}}, {P(w, n) - 0.15:.2f});')
J(f'tl.to(".Pdolor", {{opacity:0.35, duration:0.3, yoyo:true, repeat:1}}, {P("huesos") - 0.1:.2f});')
# 10) 140 kg sin engordar
card('<small>PESAS</small><b><span id="kg140">70</span> kg</b><em>el doble, sin engordar</em>', P("pesas") - 0.3, FE(10) + 0.2)
contador("#kg140", 70, 140, P("pesas") - 0.2, 1.4)
# 11) supera a Robert Wadlow (2,72 m)
J(f'tl.to("#wad", {{opacity:0.9, duration:0.6}}, {P("wadlow") - 0.6:.2f}); tl.to("#wad", {{opacity:0, duration:0.6}}, {FE(11) + 0.4:.2f});')
h(F(11), 2.73, P("wadlow") + 0.3 - F(11)); h(P("wadlow") + 0.3, 2.76, FE(11) - P("wadlow"))
cam(F(11) - 0.2, 1.4, fx=60)
etiqueta((140, -2.72 * U), P("wadlow") - 0.3, FE(11) + 0.3, "Robert Wadlow · 2,72 m", dx=14, dy=-46)
cam(FE(11) + 0.1, 1.2, fx=0)
# 12) el corazón
h(F(12), 2.90, FE(12) - F(12))
J(f'tl.to("#corazon", {{opacity:1, duration:0.4}}, {P("corazon") - 0.2:.2f}); tl.to("#corazon", {{opacity:0, duration:0.4}}, {FE(12) + 0.2:.2f});')
J(f'tl.to("#lat", {{scale:1.3, svgOrigin:"0 0", duration:0.18, yoyo:true, repeat:13, ease:"power1.inOut"}}, {P("corazon"):.2f});')
card('<small>EL CORAZÓN</small><b>más altura</b><em>que bombear cada día</em>', P("sangre") - 0.3, FE(12) + 0.2)
# 13) tres meses: 3,10 m, 389 kg; la canasta
h(F(13), 3.10, FE(13) - F(13))
ref("aro", P("tres", 2) - 0.2, FE(13) + 0.4)
etiqueta((196, -AR), P("tres", 2), FE(13) + 0.4, "canasta · 3,05 m", dx=12, dy=-44)
card('<small>3 MESES</small><b>3,10 m</b><em><span id="kg389">140</span> kg</em>', P("meses", 2) - 0.2, FE(13) + 0.2)
contador("#kg389", 140, 389, P("cuatrocientos") - 0.8, 1.2)
# 14) cuatro meses: 3,55 m, más de media tonelada
h(F(14), 3.55, FE(14) - F(14))
card('<small>4 MESES</small><b>3,55 m</b><em>+ de 500 kg</em>', P("cuatro", 2) - 0.2, FE(14) + 0.2)
# 15) presión en los huesos ×2 — piernas en rojo
h(F(15), 3.58, FE(15) - F(15))
J(f'tl.to(".Pdolor", {{opacity:0.55, duration:0.5}}, {P("huesos", 2) - 0.2:.2f}); tl.to(".Pdolor", {{opacity:0, duration:0.4}}, {FE(15) + 0.1:.2f});')
J(f'tl.to(".Pdolor", {{opacity:0.3, duration:0.2, yoyo:true, repeat:5}}, {P("pierna") - 0.6:.2f});')
card('<small>PRESIÓN EN LOS HUESOS</small><b class="r">×2</b><em>riesgo de fractura</em>', P("presion") - 0.3, FE(15) + 0.2)
# 16) tendría que vivir sentado… y sigue creciendo
rpose(J, "P", "suelo", P("sentado") - 0.6, 1.1, "power2.inOut")
J(f'tl.to("#sentar", {{y:78, duration:1.1, ease:"power2.inOut"}}, {P("sentado") - 0.6:.2f});')
J(f'tl.to("#P_sombra", {{y:-78, rx:60, duration:1.1, ease:"power2.inOut"}}, {P("sentado") - 0.6:.2f});')
cam(P("sentado") - 0.6, 1.1, by=0.33)
h(F(16) + 0.6, 3.64, FE(16) - F(16))
card('<small>SENTADO</small><b>y sigue creciendo</b>', P("creciendo") - 0.3, FE(16) + 0.2)
J(f'tl.to("#hud", {{opacity:0, y:40, duration:0.5}}, {FE(16) + 0.3:.2f});')
# 17-18) los parpadeos de este vídeo; vuelta al ojo (bucle)
cam(F(17) - 0.1, 2.6, "power2.inOut", ojo=1)
card('<small>MIENTRAS VEÍAS ESTE VÍDEO</small><b><span id="nv">0</span> parpadeos</b>', P("parpadeado") - 0.4, FE(17) + 0.2, top=1430, left=190, w=700, cls="centro")
FXL.append('<div id="final" class="grande"><b>+0,02 mm</b><small>SOLO POR PARPADEAR</small></div>')
J(f'tl.set("#final", {{opacity:0}}, 0); tl.fromTo("#final", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.5, ease:"power3.out", immediateRender:false}}, {F(18) - 0.1:.2f}); tl.to("#final", {{opacity:0, duration:0.35}}, {DUR - 0.75:.2f});')
J(f'tl.fromTo("#gancho", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.35, immediateRender:false}}, {DUR - 0.5:.2f});')

# parpadeos regulares (≈ 15 por minuto) fuera de los tramos con ojos abiertos/cerrados a propósito
LIBRE = [(F(5) + 0.3, P("tobillo") - 0.4), (F(6) + 0.2, FE(6)), (F(7) + 0.3, P("marco") - 0.6), (F(8) + 0.4, FE(8)), (F(9) + 0.5, FE(9)),
         (F(10) + 0.3, FE(10)), (F(11) + 0.3, FE(11)), (F(12) + 0.3, FE(12)), (F(13) + 0.3, FE(13)), (F(14) + 0.3, FE(14)),
         (F(15) + 0.3, FE(15)), (F(16) + 0.3, FE(16))]
ult = max(PARP)
for a, b in LIBRE:
    t = max(a, ult + 3.6)
    while t < b:
        parpadeo(t); ult = t; t += 3.9
N17 = len([t for t in PARP if t < F(17)])
contador("#nv", 0, N17, P("parpadeado") - 0.3, 1.2)
for t in (P("veces", 2) + 0.3, F(18) + 1.6):
    parpadeo(t)

# ------------------------------------------------------------------ nubes, pájaros (capa de pantalla; vuelven a su sitio al final)
NUB = [(70, 560, 0.9), (650, 650, 0.7), (860, 500, 1.15), (300, 820, 0.6)]
NUBES = "".join(f'<div class="nube" id="nb{k}" style="left:{x}px;top:{y}px;transform:scale({sc})"><i></i><i></i><i></i></div>' for k, (x, y, sc) in enumerate(NUB))
for k in range(len(NUB)):
    J(f'tl.fromTo("#nb{k}", {{x:0}}, {{x:{(-1) ** k * 80}, duration:{DUR / 2:.2f}, ease:"sine.inOut", yoyo:true, repeat:1, immediateRender:false}}, 0);')
PAJ = "".join(f'<svg class="pajaro" id="pj{k}" width="40" height="20" viewBox="0 0 40 20" style="top:{600 + k * 70}px"><path d="M2,12 Q10,2 20,12 Q30,2 38,12" stroke="#2b3440" stroke-width="3" fill="none"/></svg>' for k in range(3))
PAJ = ''

# ------------------------------------------------------------------ montaje
_S = open(os.path.join(BASE, "_subs.py"), encoding="utf-8").read()
exec(re.sub(r"CLAVE = set\(.*?\]\)", lambda m: 'CLAVE = set(norm(w) for w in ["parpadeas", "milesima", "quince", "mil", "secan", "arden", "centimetro", "duermes", "semana", "diez", "tobillo", "cama", "dos", "puerta", "mes", "veinte", "problema", "duplica", "ocho", "cuatro", "doble", "cuarenta", "wadlow", "corazon", "sangre", "tres", "cuatrocientos", "tonelada", "huesos", "presion", "pierna", "sentado", "creciendo", "parpadeado", "centesimas", "parpadear"])', _S, count=1, flags=re.S))
html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#74b6e6}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;color:#fff;background:linear-gradient(180deg,#3f8fd2 0%,#74b6e6 40%,#b9dcf3 75%,#dff0fa 100%)}}
#sol{{position:absolute;left:820px;top:330px;width:150px;height:150px;border-radius:50%;background:radial-gradient(circle,#fff7d6 0%,#ffe48a 55%,rgba(255,228,138,0) 72%)}}
#nubes,#aves{{position:absolute;inset:0;pointer-events:none}} .nube{{position:absolute;width:260px;height:80px;transform-origin:center}}
.nube i{{position:absolute;bottom:0;border-radius:50%;background:#ffffff;opacity:0.92}} .nube i:nth-child(1){{left:0;width:130px;height:60px}} .nube i:nth-child(2){{left:60px;width:130px;height:90px}} .nube i:nth-child(3){{left:130px;width:120px;height:62px}}
.pajaro{{position:absolute;left:0}}
svg#esc{{position:absolute;left:0;top:0}}
#noche{{position:absolute;inset:0;background:#0f1d44;opacity:0;pointer-events:none;mix-blend-mode:multiply}}
#fxl{{position:absolute;inset:0;z-index:58;pointer-events:none}}
.card{{position:absolute;padding:18px 24px 20px;border-radius:22px;background:rgba(14,30,52,0.8);opacity:0}}
.card small{{display:block;font:700 18px Inter;letter-spacing:4px;color:#8cc4ff;margin-bottom:6px}} .card b{{display:block;font:300 64px/1.05 Inter;letter-spacing:-1.5px}}
.card em{{display:block;font-style:normal;font:500 26px/1.3 Inter;color:rgba(255,255,255,0.75);margin-top:6px}} .card .r{{color:#ff6b5e}}
.card.centro{{text-align:center}} .card .filas p{{font:500 30px/1.5 Inter;color:#fff}} .card .filas b{{display:inline;font:800 34px Inter}}
.grande{{position:absolute;left:0;right:0;top:1430px;text-align:center}} .grande b{{display:inline-block;padding:16px 44px 10px;border-radius:28px 28px 0 0;background:rgba(14,30,52,0.82);font:300 120px/1 Inter;letter-spacing:-4px}}
.grande small{{display:block;width:max-content;margin:0 auto;padding:4px 34px 16px;border-radius:0 0 22px 22px;background:rgba(14,30,52,0.82);font:700 24px Inter;letter-spacing:6px;color:#8cc4ff}}
.pop{{position:absolute;left:600px;top:560px;font:800 40px Inter;color:#ffffff;text-shadow:0 3px 12px rgba(8,30,60,0.6);opacity:0}}
.lab{{position:absolute;left:0;top:0;padding:8px 16px;border-radius:12px;background:rgba(14,30,52,0.8);font:700 26px Inter;white-space:nowrap;opacity:0}}
#hud{{position:absolute;left:40px;right:40px;top:1610px;height:130px;border-radius:28px;background:rgba(14,30,52,0.8);display:flex;justify-content:space-around;align-items:center;opacity:0;transform:translateY(40px);z-index:59}}
#hud div{{text-align:center}} #hud small{{display:block;font:700 18px Inter;letter-spacing:4px;color:#8cc4ff}} #hud b{{display:block;font:300 54px Inter;letter-spacing:-1px;font-variant-numeric:tabular-nums}}
#grano{{position:absolute;inset:0;z-index:56;pointer-events:none;opacity:0.03;background:url(assets/grano.png);mix-blend-mode:overlay}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:520px;z-index:55;pointer-events:none;background:linear-gradient(rgba(16,52,92,0.55),rgba(16,52,92,0))}}
#marca{{position:absolute;left:0;right:0;top:1820px;text-align:center;font:600 26px Inter;color:#ffffff;opacity:0.5;pointer-events:none;z-index:61}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 58px Inter;color:rgba(255,255,255,0.62);line-height:1.22;text-shadow:0 3px 14px rgba(8,30,60,0.75)}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:3px solid #4ea3ff;border-radius:6px;background:rgba(78,163,255,0.18);opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="sol"></div>
  <div id="nubes">{NUBES}</div>
  <svg id="esc" width="1080" height="1920" viewBox="0 0 1080 1920"><g id="world">{WORLD}</g></svg>
  <div id="aves">{PAJ}</div>
  <div id="noche"></div>
  <div id="topsombra"></div><div id="grano"></div>
  <div id="fxl">{"".join(FXL)}</div>
  <div id="hud"><div><small>DÍA</small><b id="hDia">0</b></div><div><small>ALTURA</small><b id="hAlt">1,75 m</b></div><div><small>PESO</small><b id="hKg">70 kg</b></div></div>
  <div id="marca">@mundo.supuesto</div>
  <div id="subs" data-layout-allow-overlap>{"".join(SUBS)}</div>
  <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
</div>
<script>
const fmt = (v, d) => {{ const s = v.toFixed(d).split("."); return s[0].replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ".") + (s[1] ? "," + s[1] : ""); }};
const S = {{ h:1.75, ojo:1, fx:0, by:0.5 }};
const W = document.getElementById("world"), CR = document.getElementById("crece"), OJO = document.getElementById("P_ojo");
const LABS = [], LV = {{}};
function wpt(el) {{ const b = el.getBBox(); const m = W.getCTM().inverse().multiply(el.getCTM()); const p = new DOMPoint(b.x + b.width / 2, b.y + b.height / 2).matrixTransform(m); return p; }}
function frame() {{
  const s = S.h / 1.75; CR.setAttribute("transform", `scale(${{s}})`);
  W.setAttribute("transform", "");
  const H = 189 * s;
  const e = wpt(OJO);
  const zb = 900 / H, ze = 22 / s;
  const z = Math.exp(Math.log(zb) * (1 - S.ojo) + Math.log(ze) * S.ojo);
  const fx = (S.fx + 12) * s * (1 - S.ojo) + e.x * S.ojo, fy = -H * S.by * (1 - S.ojo) + e.y * S.ojo;
  const sy = 1020 * (1 - S.ojo) + 930 * S.ojo;
  W.setAttribute("transform", `translate(540,${{sy}}) scale(${{z}}) translate(${{-fx}},${{-fy}})`);
  const dia = Math.max(0, (S.h - 1.75) / 0.015);
  document.getElementById("hDia").textContent = Math.round(dia);
  document.getElementById("hAlt").textContent = S.h.toFixed(2).replace(".", ",") + " m";
  document.getElementById("hKg").textContent = fmt(70 * Math.pow(s, 3), 0) + " kg";
  for (const L of LABS) {{ const el = document.getElementById("lb" + L.i); const v = LV["l" + L.i] || 0; el.style.opacity = v;
    if (v > 0.01) {{ const x = 540 + (L.x - fx) * z, y = sy + (L.y - fy) * z; const xx = Math.min(x + L.dx, 1060 - el.offsetWidth); el.style.transform = `translate(${{xx}}px, ${{y + L.dy}}px)`; }} }}
}}
const tl = gsap.timeline({{ paused: true, onUpdate: frame }});
{chr(10).join(tl)}
tl.to({{}}, {{duration:0.01}}, {DUR - 0.01});
window.__timelines["main"] = tl;
tl.seek(0); frame();
</script>
</body></html>"""
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump([], open(os.path.join(BASE, "efectos.json"), "w"))
json.dump([[0, 0.0], [DUR, 0.0]], open(os.path.join(BASE, "ambiente.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones · {len(PARP)} parpadeos ({N17} antes de la frase 17)")

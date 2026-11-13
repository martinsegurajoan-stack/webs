#!/usr/bin/env python3
"""«¿Qué pasaría si todo el mundo fuese calvo?» (basado en unas/gen.py)
« — UN SOLO PLANO: una mano grande en un estudio oscuro con luz cálida.
Las uñas crecen al ritmo real (3,5 mm/mes) y a partir de ~12 cm se retuercen en espiral. Cada frase añade algo:
regla, móvil que no responde, botón/cremallera/moneda, lupa con bacterias, pie con uña en cuerno, rotura al dormir,
récord de Shridhar Chillal (pulgar 1,98 m), dedos deformados, queratina (pelo, garra, cuerno de rinoceronte) y cortaúñas
que devuelve la mano al fotograma 0 (bucle). Sin efectos de sonido.
  python3 gen.py → index.html + efectos.json + ambiente.json"""
import json, math, os, random, re, unicodedata

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

def st(t, d=1.0, ease="power2.inOut", **kv):
    J(f'tl.to(S, {{{", ".join(f"{k}:{v}" for k, v in kv.items())}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
NC = [0]
def dato(kicker, grande, t, hasta, sub="", top=1480):
    NC[0] += 1; i = NC[0]
    FXL.append(f'<div class="dato" id="d{i}" style="top:{top}px"><small>{kicker}</small><b>{grande}</b>{f"<em>{sub}</em>" if sub else ""}</div>')
    J(f'tl.set("#d{i}", {{opacity:0}}, 0); tl.fromTo("#d{i}", {{opacity:0, x:-24}}, {{opacity:1, x:0, duration:0.5, ease:"power3.out", immediateRender:false}}, {t:.2f}); tl.to("#d{i}", {{opacity:0, x:12, duration:0.35}}, {hasta:.2f});')
def contador(sel, v0, v1, t, d, dec=0, suf=""):
    J(f'(() => {{ const o = {{v:{v0}}}; tl.to(o, {{v:{v1}, duration:{d:.2f}, ease:"power2.out", onUpdate:() => {{ document.querySelector("{sel}").textContent = fmt(o.v, {dec}) + "{suf}"; }}}}, {t:.2f}); }})();')
NO = [0]
def panel(html, t, hasta, x=540, y=760, w=600, entra="up"):
    """Panel gráfico (SVG/HTML) centrado en (x, y) de pantalla."""
    NO[0] += 1; i = NO[0]
    FXL.append(f'<div class="pan" id="p{i}" style="left:{x - w / 2}px;top:{y}px;width:{w}px">{html}</div>')
    J(f'tl.set("#p{i}", {{opacity:0}}, 0); tl.fromTo("#p{i}", {{opacity:0, y:40, scale:0.94}}, {{opacity:1, y:0, scale:1, duration:0.55, ease:"power3.out", immediateRender:false}}, {t:.2f}); tl.to("#p{i}", {{opacity:0, y:-20, duration:0.35}}, {hasta:.2f});')
    return f"#p{i}"
LN = 'fill="none" stroke="#f3e9dc" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"'
RD = 'fill="none" stroke="#ff6f61" stroke-width="7" stroke-linecap="round"'

# ------------------------------------------------------------------ GUION VISUAL
INI = dict(cx=0, cy=-470, z=1.7)
LN = 'fill="none" stroke="#e8f3ff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"'
RD = 'fill="none" stroke="#ff6f61" stroke-width="7" stroke-linecap="round"'
FXL.append('<div class="dato" id="hook" style="top:1640px;opacity:1"><small>MAÑANA · TODO EL MUNDO</small><b>sin un solo pelo</b></div>')
J('tl.set("#hook", {opacity:1}, 0);')
J(f'tl.to("#hook", {{opacity:0, duration:0.4}}, {F(2) - 0.2:.2f});')
for tb in [1.2, 4.0] + [x * 3.7 + 6 for x in range(19)]:
    J(f'tl.to(S, {{parp:1, duration:0.07}}, {tb:.2f}); tl.to(S, {{parp:0, duration:0.1}}, {tb + 0.1:.2f});')
J(f'tl.to(S, {{mira:-0.6, duration:0.4}}, {F(2) + 1:.2f}); tl.to(S, {{mira:0.6, duration:0.5}}, {F(2) + 2.2:.2f}); tl.to(S, {{mira:0, duration:0.4}}, {F(2) + 3.4:.2f});')
# 1) se despierta calvo: el pelo cae, luego cejas y pestañas
J(f'tl.to(S, {{caida:1, duration:1.4, ease:"power1.in"}}, {P("pelo") - 0.2:.2f}); tl.to(S, {{pelo:0, duration:1.6, ease:"power2.in"}}, {P("pelo"):.2f}); tl.to(S, {{brillo:1, duration:0.4, yoyo:true, repeat:1}}, {P("pelo") + 1.6:.2f}); tl.to(S, {{barba:0, duration:0.8}}, {P("barba") - 0.2:.2f});')
J(f'tl.to(S, {{flash:1, duration:0.1, yoyo:true, repeat:1}}, {P("nunca") - 0.1:.2f});')
st(P("pelo") - 0.3, 2.0, z=1.85, cy=-500)
# 2) reconocer a la gente
J(f'tl.to(S, {{scan:1, duration:0.5}}, {P("reconocer") - 0.3:.2f}); tl.to(S, {{scan:0, duration:0.4}}, {FE(2) + 0.1:.2f});')
CARAS = '<svg viewBox="0 0 600 220" width="600" height="220">' + "".join(
    f'<g transform="translate({100 + k * 200},110)"><ellipse rx="70" ry="92" fill="{c}"/><ellipse cx="-24" cy="-8" rx="10" ry="6" fill="#fff"/><ellipse cx="24" cy="-8" rx="10" ry="6" fill="#fff"/><circle cx="-24" cy="-8" r="4" fill="#222"/><circle cx="24" cy="-8" r="4" fill="#222"/><path d="M-20,40 Q0,48 20,40" stroke="#8a4a3c" stroke-width="5" fill="none"/><ellipse cx="-20" cy="-60" rx="26" ry="14" fill="#fff" opacity="0.25"/></g>'
    for k, c in enumerate(("#e2ad8a", "#e6b391", "#dea684"))) + '</svg><div class="cap">¿quién es quién?</div>'
panel(CARAS, P("cara") - 0.5, FE(2) + 0.2, x=540, y=520, w=760)
st(P("reconocer") - 0.4, 1.2, cy=-640, z=1.15)
dato("TU CEREBRO", "reconoce caras por el pelo", P("cerebro") - 0.4, FE(2) + 0.2, top=1660)
# 3) sudor y lluvia a los ojos
st(F(3) - 0.2, 1.4, cy=-470, z=2.1)
J(f'tl.to(S, {{gotas:1, duration:0.5}}, {P("sudor") - 0.3:.2f}); tl.to(S, {{gotas:0, duration:0.4}}, {FE(3) + 0.1:.2f});')
dato("SIN CEJAS", "el sudor cae a los ojos", P("sudor") - 0.2, FE(3) + 0.2, top=1660)
# 4) pestañas: polvo y ojos secos (zoom al ojo)
st(F(4) - 0.3, 1.4, cx=-62, cy=-440, z=4.6)
J(f'tl.to(S, {{polvo:1, duration:0.6}}, {P("polvo") - 0.6:.2f}); tl.to(S, {{rojo:1, duration:2.5}}, {F(4) + 0.5:.2f}); tl.to(S, {{polvo:0, duration:0.5}}, {FE(4) + 0.1:.2f}); tl.to(S, {{rojo:0, duration:1}}, {FE(4) + 0.3:.2f});')
dato("SIN PESTAÑAS", "más polvo y ojos secos", P("polvo") - 0.4, FE(4) + 0.2, top=1660)
# 5) nariz: polen
st(F(5) - 0.3, 1.4, cx=0, cy=-370, z=3.6)
J(f'tl.to(S, {{polen:1, duration:0.6}}, {P("polen") - 0.5:.2f}); tl.to(S, {{polen:0, duration:0.5}}, {FE(5) + 0.1:.2f});')
dato("SIN FILTRO", "más alergias", P("alergias") - 0.6, FE(5) + 0.2, top=1660)
# panels del resto: cabeza abajo
st(F(6) - 0.4, 1.4, cx=0, cy=-640, z=1.0)
# 6) mosquito: los pelos del brazo son sensores
BRAZO = ('<svg viewBox="0 0 600 300" width="600" height="300"><defs><linearGradient id="gb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#efc09d"/><stop offset="1" stop-color="#c88a68"/></linearGradient></defs>'
         '<path d="M0,170 C150,150 450,150 600,170 L600,300 L0,300 Z" fill="url(#gb)"/>'
         '<g id="vellos">' + "".join(f'<path class="vello" d="M{30 + k * 38},{164 - (k % 3)} q4,-22 14,-30" stroke="#5a3a2a" stroke-width="3" fill="none" stroke-linecap="round"/>' for k in range(15)) + '</g>'
         '<path id="nervio" d="M300,170 V290" stroke="#9fdcff" stroke-width="5" stroke-dasharray="10 8" opacity="0"/>'
         '<g id="mosq"><g transform="translate(560,40)"><ellipse cx="0" cy="0" rx="18" ry="7" fill="#2b2b2b"/><circle cx="-18" cy="-2" r="7" fill="#2b2b2b"/><path d="M-24,0 l-18,6" stroke="#2b2b2b" stroke-width="3"/>'
         '<ellipse class="ala" cx="4" cy="-14" rx="16" ry="7" fill="#cfe8ff" opacity="0.7"/><path d="M-6,6 l-10,18 M4,6 l0,20 M14,6 l10,18" stroke="#2b2b2b" stroke-width="2.5"/></g></g></svg>')
panel(BRAZO + '<div class="cap" id="capB">cada pelo avisa a un nervio</div>', F(6) - 0.2, FE(6) + 0.2, x=540, y=500, w=760)
J(f'tl.to("#mosq", {{x:-250, y:110, duration:1.6, ease:"power2.out"}}, {P("mosquito") - 0.3:.2f}); tl.to(".ala", {{scaleY:0.2, duration:0.06, yoyo:true, repeat:25, transformOrigin:"50% 50%"}}, {P("mosquito") - 0.3:.2f});')
J(f'tl.to(".vello", {{rotation:-25, svgOrigin:"300 165", duration:0.3, stagger:0.02}}, {P("sensor") - 0.4:.2f}); tl.to("#nervio", {{opacity:1, strokeDashoffset:-60, duration:1.2}}, {P("nervio") - 0.3:.2f});')
dato("CADA PELO", "es un sensor", P("sensor") - 0.3, FE(6) + 0.2, top=1660)
# 7) el piojo humano se extinguiría
PIOJO = ('<svg viewBox="0 0 300 300" width="300" height="300"><ellipse cx="150" cy="170" rx="58" ry="80" fill="#c9b79a"/><ellipse cx="150" cy="80" rx="30" ry="26" fill="#bba989"/>'
         + "".join(f'<path d="M{150 + s * 50},{130 + k * 34} q{s * 40},-10 {s * 70},{20 + k * 4}" stroke="#a8977a" stroke-width="8" fill="none" stroke-linecap="round"/>' for s in (-1, 1) for k in range(3))
         + '<path d="M136,58 l-14,-28 M164,58 l14,-28" stroke="#a8977a" stroke-width="5"/>'
         '<g id="sello" opacity="0" transform="rotate(-14 150 160)"><rect x="20" y="126" width="260" height="70" rx="10" fill="none" stroke="#ff6f61" stroke-width="8"/><text x="150" y="176" font-family="Inter" font-weight="800" font-size="42" text-anchor="middle" fill="#ff6f61">EXTINTO</text></g></svg>')
panel(PIOJO + '<div class="cap">solo vive en el pelo humano</div>', F(7) - 0.1, FE(7) + 0.2, x=540, y=470, w=520)
J(f'tl.fromTo("#sello", {{opacity:0, scale:1.6}}, {{opacity:1, scale:1, svgOrigin:"150 160", duration:0.35, ease:"back.out(2)", immediateRender:false}}, {P("extinguiria") + 0.2:.2f});')
dato("UNA ESPECIE", "desaparecería", P("piojo") - 0.4, FE(7) + 0.2, top=1660)
# 8) industria
IND = ('<svg viewBox="0 0 600 260" width="600" height="260">' + "".join(
    f'<g transform="translate({90 + k * 210},40)" class="prod">{p}</g>' for k, p in enumerate((
        f'<rect x="-34" y="40" width="68" height="150" rx="22" {LN}/><rect x="-18" y="10" width="36" height="30" rx="6" {LN}/>',
        f'<path d="M-40,190 V90 C-40,60 40,60 40,90 V190 Z" {LN}/><path d="M-20,60 V20 H20 V60" {LN}/>',
        f'<circle cx="-22" cy="160" r="22" {LN}/><circle cx="26" cy="160" r="22" {LN}/><path d="M-10,140 L30,20 M14,140 L-26,20" {LN}/>'))) + '</svg>')
panel(IND, F(8) - 0.1, FE(8) + 0.2, x=540, y=500, w=760)
J(f'tl.to(".prod", {{opacity:0.15, y:30, duration:0.8, stagger:0.2}}, {P("peluquerias") - 0.2:.2f});')
dato("UNA INDUSTRIA DE", "<span id=\"nmil\">0</span> millones $", P("cien") - 0.5, FE(8) + 0.2, "al año · champús, tintes, peluquerías", top=1640)
contador("#nmil", 0, 100000, P("cien") - 0.4, 1.6)
# 9) templo de Tirumala
TEMP = ('<svg viewBox="0 0 600 300" width="600" height="300"><path d="M200,260 V140 L300,40 L400,140 V260 Z" fill="none" stroke="#f2c76b" stroke-width="6"/>'
        '<path d="M230,140 H370 M250,170 H350 M270,200 H330" stroke="#f2c76b" stroke-width="4"/><path d="M300,40 V10" stroke="#f2c76b" stroke-width="6"/>'
        '<g id="pilaPelo">' + "".join(f'<path d="M{430 + (k % 6) * 22},{260 - (k // 6) * 16} q10,-14 20,0" stroke="#2f2018" stroke-width="7" fill="none"/>' for k in range(30)) + '</g>'
        '<text x="300" y="296" font-family="Inter" font-size="22" font-weight="600" text-anchor="middle" fill="#e8f3ff">Tirumala, India</text></svg>')
panel(TEMP, F(9) - 0.1, FE(9) + 0.2, x=540, y=480, w=760)
J(f'tl.fromTo("#pilaPelo path", {{opacity:0}}, {{opacity:1, duration:0.1, stagger:0.08, immediateRender:false}}, {P("rapan") - 0.3:.2f});')
dato("SU PELO DONADO", "se vende para pelucas", P("pelucas") - 0.8, FE(9) + 0.2, top=1660)
# 10) policía: un pelo guarda meses
MESES = ('<svg viewBox="0 0 600 160" width="600" height="160">' + "".join(f'<rect class="mes" x="{40 + k * 130}" y="60" width="124" height="22" rx="11" fill="{c}"/><text x="{102 + k * 130}" y="120" font-family="Inter" font-size="22" text-anchor="middle" fill="#e8f3ff">mes {k + 1}</text>' for k, c in enumerate(("#5b6b80", "#ff6f61", "#5b6b80", "#ff6f61")))
         + '<circle cx="34" cy="71" r="14" fill="#e8f3ff"/></svg><div class="cap">un pelo crece ~1 cm al mes y guarda lo que tomaste</div>')
panel(MESES, F(10) - 0.1, FE(10) + 0.2, x=540, y=560, w=760)
J(f'tl.fromTo(".mes", {{scaleX:0}}, {{scaleX:1, svgOrigin:"40 71", duration:0.5, stagger:0.35, immediateRender:false}}, {P("pelo", 6) - 0.3:.2f});')
dato("UN SOLO PELO", "revela meses de drogas", P("drogas") - 0.6, FE(10) + 0.2, top=1660)
# 11) tantos pelos como un chimpancé
CHIMP = ('<svg viewBox="0 0 600 300" width="600" height="300">'
         '<g transform="translate(160,150)"><circle r="90" fill="#3b2a20"/><ellipse cx="0" cy="20" rx="58" ry="50" fill="#c79a78"/><circle cx="-22" cy="0" r="7" fill="#111"/><circle cx="22" cy="0" r="7" fill="#111"/><ellipse cx="0" cy="40" rx="24" ry="10" fill="#8f6a50"/><circle cx="-94" cy="0" r="26" fill="#3b2a20"/><circle cx="94" cy="0" r="26" fill="#3b2a20"/></g>'
         '<g transform="translate(440,150)"><ellipse rx="74" ry="92" fill="#e2ad8a"/><circle cx="-24" cy="-4" r="6" fill="#111"/><circle cx="24" cy="-4" r="6" fill="#111"/><path d="M-18,44 Q0,52 18,44" stroke="#8a4a3c" stroke-width="5" fill="none"/>'
         + "".join(f'<circle class="fino" cx="{-60 + (k % 10) * 13}" cy="{-80 + (k // 10) * 18}" r="1.6" fill="#7a5040" opacity="0"/>' for k in range(90)) + '</g>'
         '<text x="160" y="290" font-family="Inter" font-size="26" font-weight="600" text-anchor="middle" fill="#e8f3ff">≈ 5 millones</text><text x="440" y="290" font-family="Inter" font-size="26" font-weight="600" text-anchor="middle" fill="#e8f3ff">≈ 5 millones</text></svg>')
panel(CHIMP, F(11) - 0.1, P("finos") - 0.6, x=540, y=500, w=760)
J(f'tl.to(".fino", {{opacity:0.8, duration:0.1, stagger:0.015}}, {P("finos") - 0.4:.2f});')
dato("FOLÍCULOS PILOSOS", "como un chimpancé", P("chimpance") - 0.4, P("finos") - 0.6, top=1660)
# cierre: primer plano de la piel con los pelos finísimos que no ves (sin preguntas ni «imagina»)
st(P("finos") - 0.6, 2.4, cx=0, cy=-500, z=2.9)
J(f'tl.to(S, {{vello:1, duration:1.6}}, {P("finos") - 0.2:.2f});')
dato("NO LOS VES", "pero están ahí", P("ves") - 0.2, DUR - 0.2, top=1660)

# ------------------------------------------------------------------ montaje
_S = open(os.path.join(BASE, "_subs.py"), encoding="utf-8").read()
exec(re.sub(r"CLAVE = set\(.*?\]\)", lambda m: 'CLAVE = set(norm(w) for w in ["calvo", "pelo", "cejas", "pestanas", "reconocer", "sudor", "ojos", "polvo", "nariz", "alergias", "mosquito", "sensor", "piojo", "extinguiria", "cien", "templo", "pelucas", "drogas", "petroleo", "absorbe", "chimpance", "cinco", "millones", "golpe", "manana"])', _S, count=1, flags=re.S))
html = open(os.path.join(BASE, "_plantilla.html"), encoding="utf-8").read()
for k, v in (("%%DURX%%", f"{DUR:.3f}"), ("%%DUREND%%", f"{DUR - 0.01:.3f}"), ("%%DUR%%", f"{DUR}"), ("%%FXL%%", "".join(FXL)), ("%%SUBS%%", "".join(SUBS)),
             ("%%TL%%", chr(10).join(tl)), ("%%INI%%", json.dumps(INI))):
    html = html.replace(k, v)
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump([], open(os.path.join(BASE, "efectos.json"), "w"))
json.dump([[0, 0.0], [DUR, 0.0]], open(os.path.join(BASE, "ambiente.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones")

#!/usr/bin/env python3
"""«¿Qué pasaría si nunca más te cortaras las uñas?» — UN SOLO PLANO: una mano grande en un estudio oscuro con luz cálida.
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
INI = dict(cx=0, cy=-250, z=2.05)
FXL.append('<div class="dato" id="hook" style="top:1480px;opacity:1"><small>SIN CORTARLAS</small><b>nunca más</b></div>')
J('tl.set("#hook", {opacity:1}, 0);')
# 1) gancho: la mano con uñas normales; empiezan a crecer en «nunca»
st(P("nunca", 2), FE(1) - P("nunca", 2) + 0.3, "power1.in", L=0.6)
J(f'tl.to("#hook", {{opacity:0, duration:0.4}}, {F(2) - 0.1:.2f}); tl.to("#hook", {{opacity:1, duration:0.4}}, {DUR - 0.6:.2f});')
# 2) 3,5 mm al mes → 4 cm al año; la mano dominante, más rápido
st(F(2), FE(2) - F(2), "none", L=4.2)
st(F(2), 1.4, cy=-330, z=1.7)
J(f'tl.to(S, {{regla:1, duration:0.5}}, {F(2) + 0.3:.2f}); tl.to(S, {{regla:0, duration:0.4}}, {FE(2) + 0.1:.2f});')
dato("CRECEN", "<span id=\"nmm\">0</span> mm al mes", F(2) + 0.2, P("ano") - 0.4)
contador("#nmm", 0, 3.5, F(2) + 0.3, 1.2, 1)
dato("EN UN AÑO", "≈ 4 cm", P("ano") - 0.4, P("escribes") - 0.4)
dato("LA MANO CON LA QUE ESCRIBES", "crece más rápido", P("escribes") - 0.4, FE(2) + 0.2)
# 3) el móvil no detecta la uña
MOVIL = (f'<svg viewBox="0 0 300 560" width="300" height="560"><rect x="20" y="10" width="260" height="540" rx="42" fill="#15171c" stroke="#3a3f4a" stroke-width="6"/>'
         f'<rect x="38" y="60" width="224" height="440" rx="14" fill="#1f2a3a"/><rect x="110" y="26" width="80" height="16" rx="8" fill="#000"/>'
         + "".join(f'<rect x="{58 + (k % 4) * 52}" y="{90 + (k // 4) * 64}" width="38" height="38" rx="10" fill="{c}"/>' for k, c in enumerate(["#4ea3ff", "#ff9f43", "#2ecc71", "#a66cff", "#ff6b81", "#f1c40f", "#1abc9c", "#e67e22", "#5dade2", "#ec7063", "#58d68d", "#af7ac5"]))
         + f'<circle id="tapU" cx="150" cy="380" r="34" fill="none" stroke="#ff6f61" stroke-width="5" opacity="0"/><path id="tapX" d="M128,358 L172,402 M172,358 L128,402" {RD} opacity="0"/>'
         f'<circle id="tapN" cx="150" cy="380" r="34" fill="none" stroke="#4ea3ff" stroke-width="5" opacity="0"/></svg>')
panel(MOVIL + '<div class="cap" id="capM">la uña no conduce: <b class="r">la pantalla no responde</b></div>', F(3) - 0.2, FE(3) + 0.2, x=780, y=560, w=400)
J(f'tl.to(S, {{L:4.6, duration:{FE(3) - F(3):.2f}, ease:"none"}}, {F(3):.2f}); tl.to(S, {{cx:200, cy:-230, duration:1.2}}, {F(3) - 0.2:.2f});')
J(f'tl.fromTo("#tapU", {{opacity:0.9, attr:{{r:12}}}}, {{opacity:0, attr:{{r:60}}, duration:0.6, repeat:1, immediateRender:false}}, {P("pantalla") - 0.2:.2f}); tl.to("#tapX", {{opacity:1, duration:0.2}}, {P("piel") - 0.3:.2f}); tl.to("#tapX", {{opacity:0, duration:0.2}}, {P("nudillos") - 0.5:.2f});')
J(f'tl.fromTo("#tapN", {{opacity:0.9, attr:{{r:12}}}}, {{opacity:0, attr:{{r:70}}, duration:0.6, repeat:2, immediateRender:false}}, {P("nudillos") - 0.3:.2f});')
J(f'tl.to("#capM", {{opacity:0, duration:0.2}}, {P("nudillos") - 0.5:.2f}); tl.call(() => {{}}, null, 0);')
dato("SOLUCIÓN", "escribir con los nudillos", P("nudillos") - 0.4, FE(3) + 0.2)
# 4) botón, cremallera, moneda
ICON = {
    "boton": f'<circle cx="60" cy="60" r="44" {LN}/><circle cx="46" cy="48" r="6" fill="#f3e9dc"/><circle cx="74" cy="48" r="6" fill="#f3e9dc"/><circle cx="46" cy="74" r="6" fill="#f3e9dc"/><circle cx="74" cy="74" r="6" fill="#f3e9dc"/>',
    "cremallera": f'<path d="M60,6 V114" {LN}/>' + "".join(f'<path d="M{48 if k % 2 else 60},{14 + k * 9} h12" {LN} stroke-width="4"/>' for k in range(9)) + f'<rect x="44" y="72" width="32" height="40" rx="8" {LN}/>',
    "moneda": f'<ellipse cx="60" cy="80" rx="46" ry="18" {LN}/><path d="M14,80 V66 M106,80 V66" {LN}/><ellipse cx="60" cy="66" rx="46" ry="18" {LN}/><text x="60" y="73" font-family="Inter" font-weight="700" font-size="22" text-anchor="middle" fill="#f3e9dc">€</text>',
}
for k, (n, w) in enumerate((("boton", "boton"), ("cremallera", "cremallera"), ("moneda", "moneda"))):
    t0 = P(w) - 0.35
    panel(f'<svg viewBox="0 0 120 120" width="200" height="200">{ICON[n]}<path class="tacha{k}" d="M14,14 L106,106" {RD} opacity="0"/></svg>', t0, FE(4) + 0.2, x=220 + k * 320, y=520, w=220)
    J(f'tl.to(".tacha{k}", {{opacity:1, duration:0.25}}, {t0 + 0.5:.2f});')
st(F(4) - 0.2, 1.2, cx=0, cy=-600, z=1.4)
J(f'tl.to(S, {{L:5.2, duration:{FE(4) - F(4):.2f}, ease:"none"}}, {F(4):.2f});')
dato("TAREAS DE 2 SEGUNDOS", "casi imposibles", P("imposible") - 0.6, FE(4) + 0.2)
# 5) bacterias bajo la uña
BAC = "".join(f'<g class="bac" transform="translate({140 + 120 * math.cos(k * 2.39) * (0.3 + 0.7 * ((k * 37) % 10) / 10):.0f},{140 + 120 * math.sin(k * 2.39) * (0.3 + 0.7 * ((k * 53) % 10) / 10):.0f}) rotate({(k * 47) % 180})"><rect x="-14" y="-5" width="28" height="10" rx="5" fill="{["#7ed957", "#5ac8a8", "#b6e36b"][k % 3]}" opacity="0.9"/></g>' for k in range(34))
LUPA = (f'<svg viewBox="0 0 280 280" width="460" height="460"><defs><clipPath id="clL"><circle cx="140" cy="140" r="126"/></clipPath><radialGradient id="gL" cx="0.5" cy="0.45" r="0.6"><stop offset="0" stop-color="#3a2f22"/><stop offset="1" stop-color="#16110c"/></radialGradient></defs>'
        f'<circle cx="140" cy="140" r="126" fill="url(#gL)"/><g clip-path="url(#clL)">{BAC}</g><circle cx="140" cy="140" r="126" fill="none" stroke="#f3e9dc" stroke-width="6"/></svg>')
panel(LUPA, F(5) - 0.1, FE(5) + 0.2, x=540, y=430, w=460)
J(f'tl.fromTo(".bac", {{scale:0.2, opacity:0}}, {{scale:1, opacity:1, duration:0.3, stagger:0.04, ease:"back.out(2)", immediateRender:false}}, {P("bacterias") - 0.5:.2f});')
J(f'tl.to(".bac", {{rotation:"+=40", x:"+=6", duration:0.5, yoyo:true, repeat:9, ease:"sine.inOut", stagger:{{each:0.03, from:"random"}}}}, {P("bacterias"):.2f});')
st(F(5) - 0.2, 1.2, cy=-600, z=1.4)
J(f'tl.to(S, {{L:5.8, duration:{FE(5) - F(5):.2f}, ease:"none"}}, {F(5):.2f}); tl.to(S, {{sucio:1, duration:0.8}}, {P("bacterias") - 0.3:.2f}); tl.to(S, {{sucio:0, duration:0.5}}, {FE(5) + 0.2:.2f});')
dato("BAJO UNA UÑA LARGA", "millones de bacterias", P("bacterias") - 0.3, FE(5) + 0.2)
# 6) el pie: la uña se curva hacia abajo como un cuerno; el zapato no entra
PIE = ('<svg viewBox="0 0 640 380" width="640" height="380"><defs><linearGradient id="gP" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eec1a0"/><stop offset="1" stop-color="#cf9a78"/></linearGradient></defs>'
       '<path d="M30,330 C40,250 60,200 120,180 L380,150 C450,142 500,160 520,200 C536,232 530,270 500,290 L60,330 Z" fill="url(#gP)"/>'
       '<path d="M450,170 C470,166 490,168 500,182" stroke="#b9876a" stroke-width="4" fill="none"/><path d="M480,190 C500,184 520,190 524,210" fill="#f6d9c8" stroke="#c99a80" stroke-width="3"/>'
       '<path id="cuerno" d="M522,200 C580,196 612,232 606,282 C600,320 566,336 548,318" stroke="#e8d8b8" stroke-width="20" fill="none" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
       '<path d="M0,334 H640" stroke="#5a4c3e" stroke-width="4"/>'
       '<g id="zapato" opacity="0"><path d="M10,330 C20,260 90,214 170,206 L360,190 C440,184 520,210 560,270 C580,300 576,330 560,334 L10,334 Z" fill="none" stroke="#9fd3ff" stroke-width="6" stroke-dasharray="14 10"/></g></svg>')
panel(PIE, F(6) - 0.2, FE(6) + 0.2, x=540, y=520, w=640)
J(f'tl.to("#zapato", {{opacity:1, duration:0.4}}, {P("zapato") - 0.6:.2f}); tl.to("#zapato", {{x:-120, opacity:0, duration:0.8, ease:"power2.in"}}, {P("cabria"):.2f});')
J(f'tl.to("#cuerno", {{strokeDashoffset:0, duration:{FE(6) - P("meses") + 0.2:.2f}, ease:"power1.inOut"}}, {P("meses") - 0.4:.2f});')
st(F(6) - 0.2, 1.2, cy=-640, z=1.3)
dato("LAS DE LOS PIES", "se curvan como un cuerno", P("curvan") - 0.4, FE(6) + 0.2)
# 7) espiral pasados 20 cm
st(F(7) - 0.3, 1.6, cx=0, cy=-560, z=0.95)
st(F(7), FE(7) - F(7), "power1.inOut", L=34)
dato("A PARTIR DE", "<span id=\"ncm\">0</span> cm", P("veinte") - 0.4, P("espiral") - 0.4)
contador("#ncm", 0, 20, P("veinte") - 0.3, 0.9)
dato("SE RETUERCEN", "en espiral", P("espiral") - 0.4, FE(7) + 0.2, "cada lado crece a distinto ritmo")
# 8) dormir: un mal giro y la uña se parte
J(f'tl.to(S, {{rotura:1, duration:0.9, ease:"power2.in"}}, {P("parte") - 0.3:.2f});')
J(f'tl.to(S, {{gira:1, duration:0.35, yoyo:true, repeat:1, ease:"power2.inOut"}}, {P("giro") - 0.2:.2f});')
st(F(8), FE(8) - F(8), "none", L=38)
dato("DORMIR", "un mal giro y se parte", P("giro") - 0.3, FE(8) + 0.2, "años de crecimiento, perdidos")
# 9) Shridhar Chillal: 66 años, pulgar de casi 2 m
st(F(9) - 0.2, FE(9) - F(9) + 0.4, "power2.inOut", L=180, z=0.36, cy=-1400)
J(f'tl.to(S, {{rotura:0, duration:0.01}}, {F(9):.2f});')
dato("SHRIDHAR CHILLAL · INDIA", "<span id=\"nan\">0</span> años sin cortarlas", P("sesenta") - 0.4, P("pulgar") - 0.3)
contador("#nan", 0, 66, P("sesenta") - 0.3, 1.4)
BARRAS = ('<svg viewBox="0 0 420 520" width="420" height="520"><path d="M20,480 H400" stroke="#6b5c4c" stroke-width="3"/>'
          '<rect id="bP" x="70" y="480" width="110" height="0" rx="8" fill="#e8d8b8"/><rect id="bH" x="250" y="480" width="110" height="0" rx="8" fill="#5f6f82"/>'
          '<text x="125" y="512" font-family="Inter" font-size="22" font-weight="600" text-anchor="middle" fill="#f3e9dc">su pulgar</text><text x="305" y="512" font-family="Inter" font-size="22" font-weight="600" text-anchor="middle" fill="#f3e9dc">una persona</text>'
          '<text id="tP" x="125" y="40" font-family="Inter" font-size="34" font-weight="300" text-anchor="middle" fill="#ffffff" opacity="0">1,98 m</text><text id="tH" x="305" y="80" font-family="Inter" font-size="34" font-weight="300" text-anchor="middle" fill="#ffffff" opacity="0">1,75 m</text></svg>')
panel(BARRAS, P("pulgar") - 0.4, FE(9) + 0.3, x=800, y=520, w=420)
J(f'tl.to("#bP", {{attr:{{y:66, height:414}}, duration:1.4, ease:"power2.out"}}, {P("pulgar") - 0.2:.2f}); tl.to("#bH", {{attr:{{y:114, height:366}}, duration:1.4, ease:"power2.out"}}, {P("pulgar"):.2f}); tl.to(["#tP", "#tH"], {{opacity:1, duration:0.4}}, {P("pulgar") + 1.0:.2f});')
dato("SU PULGAR", "1,98 m", P("pulgar") - 0.3, FE(9) + 0.3, "récord Guinness, 2016")
# 10) dedos deformados; la mano no vuelve a abrirse
J(f'tl.to(S, {{deforma:1, duration:2.2, ease:"power2.inOut"}}, {F(10) + 0.2:.2f}); tl.to(S, {{deforma:0, duration:0.8}}, {FE(10) + 0.4:.2f});')
st(F(10) - 0.2, 1.6, z=0.6, cy=-900)
dato("EL PRECIO", "dedos deformados", F(10) + 0.2, P("abrirse") - 0.5)
dato("ESA MANO", "nunca volvió a abrirse", P("abrirse") - 0.5, FE(10) + 0.3)
# 11) queratina: pelo, garra, cuerno de rinoceronte
QK = {
    "pelo": f'<path d="M40,110 C30,80 60,60 50,30 C44,14 54,6 62,4" {LN}/><path d="M64,112 C56,84 84,64 76,34 C72,20 80,10 88,8" {LN}/><path d="M86,110 C82,84 104,66 98,40" {LN}/>',
    "garra": f'<path d="M20,100 C30,60 60,30 104,20 C84,40 74,70 72,104 Z" {LN}/><path d="M36,92 C46,66 64,48 88,36" {LN} stroke-width="3"/>',
    "cuerno": f'<path d="M14,108 C30,70 50,40 96,10 C82,50 78,80 84,108 Z" {LN}/><path d="M30,98 C44,72 60,52 80,36" {LN} stroke-width="3"/>',
}
for k, (n, w) in enumerate((("pelo", "pelo"), ("garra", "garras"), ("cuerno", "rinoceronte"))):
    panel(f'<svg viewBox="0 0 120 120" width="190" height="190">{QK[n]}</svg><div class="cap">{["pelo", "garras", "cuerno de rinoceronte"][k]}</div>', P(w) - 0.4, FE(11) + 0.2, x=200 + k * 340, y=540, w=300)
st(F(11) - 0.2, 1.8, L=6, z=1.6, cy=-330)
dato("LAS UÑAS SON", "queratina", P("queratina") - 0.4, FE(11) + 0.2)
# 12) cortaúñas → la mano vuelve al fotograma 0 (bucle)
CLIP = (f'<svg viewBox="0 0 300 120" width="300" height="120"><path d="M20,60 L250,38 C270,36 284,46 284,60 C284,74 270,84 250,82 Z" fill="#c9ced6"/><path d="M20,60 L250,82" stroke="#8e96a2" stroke-width="4"/>'
        f'<path d="M60,40 C120,10 200,8 250,30" stroke="#aab2bd" stroke-width="10" fill="none" stroke-linecap="round"/><circle cx="250" cy="60" r="8" fill="#8e96a2"/></svg>')
panel(CLIP, F(12) - 0.1, P("cuerno", 3) + 0.2, x=540, y=560, w=300)
st(P("cortas") - 0.2, 0.9, "power3.in", L=0.6)
J(f'tl.to(S, {{flash:1, duration:0.12, yoyo:true, repeat:1}}, {P("cortas") + 0.6:.2f});')
dato("CADA VEZ QUE TE CORTAS LAS UÑAS", "te quitas un pequeño cuerno", P("cuerno", 3) - 0.6, DUR - 2.4)
st(FE(12) - 2.0, DUR - FE(12) + 1.9, "power2.inOut", cx=INI["cx"], cy=INI["cy"], z=INI["z"], L=0.3)

# ------------------------------------------------------------------ montaje
_S = open(os.path.join(BASE, "_subs.py"), encoding="utf-8").read()
exec(re.sub(r"CLAVE = set\(.*?\]\)", lambda m: 'CLAVE = set(norm(w) for w in ["nunca", "unas", "tres", "cuatro", "escribes", "movil", "pantalla", "nudillos", "boton", "cremallera", "moneda", "imposible", "bacterias", "sucios", "zapato", "cuerno", "veinte", "espiral", "parte", "chillal", "sesenta", "pulgar", "metros", "deformaron", "abrirse", "queratina", "pelo", "garras", "rinoceronte", "cortas"])', _S, count=1, flags=re.S))
html = open(os.path.join(BASE, "_plantilla.html"), encoding="utf-8").read()
for k, v in (("%%DURX%%", f"{DUR:.3f}"), ("%%DUREND%%", f"{DUR - 0.01:.3f}"), ("%%DUR%%", f"{DUR}"), ("%%FXL%%", "".join(FXL)), ("%%SUBS%%", "".join(SUBS)),
             ("%%TL%%", chr(10).join(tl)), ("%%INI%%", json.dumps(INI))):
    html = html.replace(k, v)
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump([], open(os.path.join(BASE, "efectos.json"), "w"))
json.dump([[0, 0.0], [DUR, 0.0]], open(os.path.join(BASE, "ambiente.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones")

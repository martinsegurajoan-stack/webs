#!/usr/bin/env python3
"""«¿Qué pasaría si el viento se detuviera en todo el planeta?» v3 — DOCUMENTAL DE DATOS, sin dibujos:
planeta real (Natural Earth 1:50m, proyección ortográfica en canvas) con miles de partículas de viento siguiendo la
circulación general (alisios, vientos del oeste, polares). El viento se para (las partículas se congelan) y la cámara
recorre el mundo con datos sobre el mapa: oleaje Antártida→Alaska, olores, vuelos NY↔Londres, maíz, niebla de Londres 1952,
Londres vs Nueva York, desertización, polvo del Bodélé al Amazonas, Biosfera 2, huracanes → el Sol calienta desigual y
el viento vuelve (bucle: último fotograma = primero). Rótulos mínimos sin cajas. Sin efectos de sonido.
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
rr = random.Random(5)

CUR = {"sc": 440}
def cam(t, d=2.0, ease="power2.inOut", **kv):
    """Vuelo de cámara: si se entra o se sale de un zoom grande, primero se aleja, gira y luego se acerca."""
    sc = kv.pop("sc", None)
    if kv:
        J(f'tl.to(S, {{{", ".join(f"{k}:{v}" for k, v in kv.items())}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
    if sc is None:
        return
    if (sc > 1200 or CUR["sc"] > 1200) and ("lon" in kv or "lat" in kv):
        mid = 640
        J(f'tl.to(S, {{sc:{mid}, duration:{d * 0.45:.2f}, ease:"power2.inOut"}}, {t:.2f}); tl.to(S, {{sc:{sc}, duration:{d * 0.55:.2f}, ease:"power2.inOut"}}, {t + d * 0.45:.2f});')
    else:
        J(f'tl.to(S, {{sc:{sc}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
    CUR["sc"] = sc
NL = [0]
def lab(lon, lat, t, hasta, titulo, kicker="", lado="d", dy=0):
    NL[0] += 1; i = NL[0]
    FXL.append(f'<div class="lab {lado}" id="lb{i}">{f"<small>{kicker}</small>" if kicker else ""}<b>{titulo}</b></div>')
    J(f'LABS.push({{i:{i}, lon:{lon}, lat:{lat}, lado:"{lado}", dy:{dy}}}); LV.l{i} = 0;')
    J(f'tl.to(LV, {{l{i}:1, duration:0.5}}, {t:.2f}); tl.to(LV, {{l{i}:0, duration:0.35}}, {hasta:.2f});')
NC = [0]
def dato(kicker, grande, t, hasta, sub=""):
    NC[0] += 1; i = NC[0]
    FXL.append(f'<div class="dato" id="d{i}"><small>{kicker}</small><b>{grande}</b>{f"<em>{sub}</em>" if sub else ""}</div>')
    J(f'tl.set("#d{i}", {{opacity:0}}, 0); tl.fromTo("#d{i}", {{opacity:0, x:-24}}, {{opacity:1, x:0, duration:0.5, ease:"power3.out", immediateRender:false}}, {t:.2f}); tl.to("#d{i}", {{opacity:0, x:12, duration:0.35}}, {hasta:.2f});')
def contador(sel, v0, v1, t, d, dec=0, suf=""):
    J(f'(() => {{ const o = {{v:{v0}}}; tl.to(o, {{v:{v1}, duration:{d:.2f}, ease:"power2.out", onUpdate:() => {{ document.querySelector("{sel}").textContent = fmt(o.v, {dec}) + "{suf}"; }}}}, {t:.2f}); }})();')
def capa(nombre, t, op, d=0.8):
    J(f'tl.to(S, {{{nombre}:{op}, duration:{d}, ease:"power1.inOut"}}, {t:.2f});')

# ------------------------------------------------------------------ tiempo del viento (W): se congela y vuelve; bucle exacto
L_VIDA = 3.0
PARA = P("detuviera") - 0.2
VUELVE = P("moverse") - 1.2
W1 = PARA
W2 = W1 + 0.9
W_FIN = math.ceil((W2 + (DUR - VUELVE) * 0.85) / L_VIDA) * L_VIDA
J(f'tl.to(S, {{W:{W1:.3f}, duration:{W1:.3f}, ease:"none"}}, 0); tl.to(S, {{W:{W2:.3f}, duration:1.8, ease:"power2.out"}}, {W1:.3f});')
J(f'tl.to(S, {{W:{W_FIN:.3f}, duration:{DUR - VUELVE:.3f}, ease:"power1.in"}}, {VUELVE:.3f});')
J(f'tl.to(S, {{va:0.13, duration:1.8, ease:"power2.out"}}, {PARA:.2f}); tl.to(S, {{va:1, duration:2.2, ease:"power1.inOut"}}, {VUELVE:.2f});')

# ------------------------------------------------------------------ GUION VISUAL
INI = dict(lon=-28, lat=18, sc=440)
J(f'tl.to(S, {{lon:-22, duration:{F(2):.2f}, ease:"none"}}, 0);')
FXL.append('<div id="kmh"><small>VIENTO MEDIO EN SUPERFICIE</small><b><span id="nk">12</span> km/h</b></div>')
contador("#nk", 12, 0, PARA, 1.6)
J(f'tl.to("#kmh b", {{color:"#ff8a7e", duration:0.5}}, {PARA + 1:.2f}); tl.to("#kmh", {{opacity:0, duration:0.5}}, {FE(1) + 1.2:.2f});')
# 2) silencio; mar espejo
cam(P("mar") - 0.5, 2.4, lon=-150, lat=-12, sc=620)
capa("olas", P("mar") + 1.2, 1, 0.8); capa("olas", P("espejo") - 0.2, 0, 2.2)
dato("CASI TODAS LAS OLAS", "las crea el viento", P("olas") - 0.3, FE(2) + 0.2)
# 3) oleaje de la Antártida a Alaska
cam(F(3) - 0.3, 2.2, lon=-155, lat=6, sc=480)
J(f'tl.fromTo(S, {{swell:0}}, {{swell:1, duration:{FE(3) - P("olas", 2) + 0.4:.2f}, ease:"none", immediateRender:false}}, {P("olas", 2) - 0.2:.2f}); tl.to(S, {{swellA:1, duration:0.4}}, {P("olas", 2) - 0.2:.2f}); tl.to(S, {{swellA:0, duration:0.6}}, {FE(3) + 0.4:.2f});')
lab(-165, -55, P("antartida") - 0.3, FE(3) + 0.3, "tormenta", "ANTÁRTIDA", "i")
lab(-152, 59, P("alaska") - 0.5, FE(3) + 0.3, "1 semana después", "ALASKA", "d")
dato("RECORRIDO DE UNA OLA", "≈ 10.000 km", P("semana") - 0.5, FE(3) + 0.2)
# 4) olores (Madrid)
cam(F(4) - 0.3, 2.4, lon=-3.7, lat=40.4, sc=5200)
capa("olor", F(4) + 2.0, 1, 0.8); capa("olorV", P("pan") - 0.2, 0, 1.6); capa("olor", FE(4) + 0.2, 0, 0.6)
lab(-3.7, 40.4, P("pan") - 0.3, FE(4) + 0.2, "una panadería", "MADRID", "d")
dato("EL OLOR A PAN, CON VIENTO", "cientos de metros", P("pan") - 0.2, P("panaderia") - 0.1)
dato("SIN VIENTO", "unos pocos metros", P("panaderia") - 0.1, FE(4) + 0.2)
# 5) vuelos Nueva York ↔ Londres
cam(F(5) - 0.3, 2.4, lon=-38, lat=47, sc=820)
J(f'tl.fromTo(S, {{vueloA:0}}, {{vueloA:1, duration:2.6, ease:"power1.inOut", immediateRender:false}}, {P("york") - 0.3:.2f}); tl.fromTo(S, {{vueloB:0}}, {{vueloB:1, duration:3.2, ease:"power1.inOut", immediateRender:false}}, {P("volver") - 0.6:.2f});')
capa("vuelos", P("york") - 0.4, 1, 0.5); capa("vuelos", FE(5) + 0.4, 0, 0.6); capa("chorro", P("york") - 0.4, 1, 0.8); capa("chorro", FE(5) + 0.4, 0, 0.6)
lab(-74, 40.7, P("york") - 0.3, FE(5) + 0.3, "Nueva York", "", "i")
lab(-0.1, 51.5, P("londres") - 0.3, FE(5) + 0.3, "Londres", "", "d")
dato("NUEVA YORK → LONDRES", "≈ 7 h", P("york") - 0.2, P("volver") - 0.3, "corriente en chorro a favor")
dato("LONDRES → NUEVA YORK", "≈ 8 h", P("volver") - 0.3, FE(5) + 0.2, "viento en contra")
# 6) maíz
cam(F(6) - 0.3, 2.4, lon=-75, lat=12, sc=560)
capa("maiz", F(6) + 0.5, 1, 0.8); capa("maizG", P("mazorca") - 0.3, 1, 1.6); capa("maiz", FE(6) + 0.3, 0, 0.6)
dato("MAÍZ · EL CEREAL Nº 1", "1.200 millones de t", P("maiz") - 0.2, P("polen") - 0.4, "al año en todo el mundo")
dato("SIN VIENTO", "el polen no llega", P("polen") - 0.4, FE(6) + 0.2, "ni una mazorca")
# 7) Londres 1952
cam(F(7) - 0.3, 2.4, lon=-1.5, lat=52.5, sc=5600)
capa("smog", P("humo") - 0.3, 1, 3.5); capa("smog", FE(7) + 0.3, 0, 1.0)
lab(-0.1, 51.5, P("1952") - 0.4, FE(7) + 0.2, "Londres", "DICIEMBRE 1952", "d")
dato("5 DÍAS SIN VIENTO", "miles de muertos", P("1952") - 0.2, FE(7) + 0.2, "por la niebla tóxica")
# 8) Londres más al norte que Nueva York, pero más templada
cam(F(8) - 0.3, 2.4, lon=-38, lat=46, sc=780)
capa("latl", P("norte") - 0.6, 1, 0.8); capa("latl", FE(8) + 0.3, 0, 0.6); capa("oeste", P("atlantico") - 0.6, 1, 0.8); capa("oeste", FE(8) + 0.3, 0, 0.6)
lab(-0.1, 51.5, P("norte") - 0.4, FE(8) + 0.2, "5 °C en enero", "LONDRES · 51° N", "d")
lab(-74, 40.7, P("york", 2) - 0.2, FE(8) + 0.2, "1 °C en enero", "NUEVA YORK · 41° N", "i")
dato("LA CALIENTA", "el viento del Atlántico", P("atlantico") - 0.5, FE(8) + 0.2)
# 9) desertización
cam(F(9) - 0.3, 2.6, lon=25, lat=20, sc=470)
capa("seco", F(9) + 0.5, 1, 5.5)
capa("humedad", F(9) + 0.2, 1, 0.6); capa("humedad", P("desierto") - 0.6, 0, 1.2)
dato("SIN VIENTO", "la lluvia no entra", F(9) + 0.3, P("desierto") - 0.5, "en los continentes")
dato("EL INTERIOR", "se vuelve desierto", P("desierto") - 0.5, FE(9) + 0.2)
# 10-11) polvo del Sáhara (Bodélé) al Amazonas
cam(F(10) - 0.3, 2.6, lon=-22, lat=4, sc=600)
capa("seco", F(10) + 0.5, 0.25, 2.0)
capa("polvo", P("amazonas") - 0.2, 1, 0.8); capa("polvo", FE(11) + 0.3, 0, 0.8)
lab(-62, -3, P("amazonas") - 0.3, FE(10) + 0.3, "Amazonas", "", "i")
dato("CADA AÑO", "<span id=\"ncam\">0</span> camiones", P("millon") - 0.8, FE(10) + 0.2, "de polvo del Sáhara · 27 millones de t")
contador("#ncam", 0, 1000000, P("millon") - 0.7, 1.4)
cam(F(11) - 0.2, 1.6, lon=0, lat=12, sc=900)
capa("bodele", F(11) + 0.2, 1, 0.6); capa("bodele", FE(11) + 0.4, 0, 0.5)
lab(18, 17, F(11) + 0.3, FE(11) + 0.3, "lago seco del Bodélé", "CHAD", "d")
dato("MÁS DE LA MITAD", "sale de un solo sitio", F(11) + 0.2, FE(11) + 0.2)
# 12) Biosfera 2
cam(F(12) - 0.3, 2.6, lon=-111, lat=33, sc=2400)
capa("seco", F(12), 0, 1.6)
capa("bio", P("biosfera") - 0.4, 1, 0.6); capa("bio", FE(12) + 0.3, 0, 0.5)
lab(-110.85, 32.58, P("biosfera") - 0.3, FE(12) + 0.2, "Biosfera 2", "ARIZONA", "d")
dato("ÁRBOLES SIN VIENTO", "crecían débiles", P("biosfera") - 0.1, P("partian") - 0.4)
dato("Y ACABABAN", "partiéndose solos", P("partian") - 0.4, FE(12) + 0.2)
# 13) huracanes
cam(F(13) - 0.3, 2.0, lon=-62, lat=20, sc=820)
capa("hur", F(13) - 0.1, 1, 0.6); capa("hur", P("huracan") - 0.1, 0, 1.4)
dato("LO ÚNICO BUENO", "0 huracanes", P("bueno") - 0.2, FE(13) + 0.3)
# 14) el Sol calienta desigual → el viento vuelve
cam(F(14) - 0.4, 3.0, lon=-34, lat=INI["lat"], sc=INI["sc"])
capa("solar", P("sol") - 0.5, 1, 1.0); capa("solar", FE(14) + 0.6, 0, 1.0)
dato("EL SOL", "calienta más el ecuador", P("sol") - 0.3, P("moverse") - 0.4)
dato("Y EL AIRE", "vuelve a moverse", P("moverse") - 0.4, FE(14) + 0.3)
# 15) final: rotación lenta hasta el encuadre del fotograma 0
J(f'tl.fromTo(S, {{lon:-34}}, {{lon:{INI["lon"]}, duration:{DUR - FE(14) - 0.3:.2f}, ease:"none", immediateRender:false}}, {FE(14) + 0.3:.2f});')
J(f'tl.set("#kmh b", {{color:"#ffffff"}}, {F(15):.2f}); tl.fromTo("#kmh", {{opacity:0}}, {{opacity:1, duration:0.6, immediateRender:false}}, {DUR - 2.8:.2f});')
contador("#nk", 0, 12, DUR - 2.8, 1.6)
dato("EL VIENTO TE TRAE", "lluvia, comida y aire", P("lluvia") - 0.4, DUR - 3.0)


# ================================================================== ICONOS ANIMADOS (uno por frase)
NI = [0]
def icono(svg, t, hasta, lon=None, lat=None, x=540, y=760, dx=0, dy=0, w=240):
    NI[0] += 1; i = NI[0]
    FXL.append(f'<div class="ico" id="ic{i}" style="width:{w}px;height:{w}px"><svg viewBox="0 0 240 240" width="{w}" height="{w}">{svg}</svg></div>')
    J(f'ICS.push({{i:{i}, lon:{"null" if lon is None else lon}, lat:{"null" if lat is None else lat}, x:{x}, y:{y}, dx:{dx}, dy:{dy}, w:{w}}}); IV.v{i} = 0;')
    J(f'tl.to(IV, {{v{i}:1, duration:0.45, ease:"power2.out"}}, {t:.2f}); tl.to(IV, {{v{i}:0, duration:0.35}}, {hasta:.2f});')
    return i
ST = 'fill="none" stroke="#ffffff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"'
AC = 'fill="none" stroke="#7fd3ff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"'
# 1b) parón: onda expansiva en el borde del planeta
J(f'tl.fromTo(S, {{pulso:0}}, {{pulso:1, duration:1.6, ease:"power2.out", immediateRender:false}}, {PARA:.2f});')
# 2a) silencio: una onda de sonido que se aplana
i = icono(f'<g id="sil"><path d="M20,120 C40,40 60,200 80,120 S120,40 140,120 S180,200 200,120 S220,80 230,120" {AC}/></g>', P("silencio") - 0.5, P("hoja") - 0.4, x=540, y=1040, w=300)
J(f'tl.to("#sil", {{scaleY:0.03, svgOrigin:"120 120", duration:1.2, ease:"power2.inOut"}}, {P("silencio") - 0.1:.2f});')
# 2b) hojas que se mecen… y se quedan quietas
HOJA = lambda x, y, r: f'<g transform="translate({x},{y}) rotate({r})"><path d="M0,0 C20,-30 60,-34 80,-10 C56,14 20,16 0,0 Z" {ST}/><path d="M6,-2 L66,-12" {ST} stroke-width="3"/></g>'
i = icono(f'<g id="rama"><path d="M30,210 C70,170 110,120 150,40" {ST}/>{HOJA(70, 168, -40)}{HOJA(100, 128, 10)}{HOJA(124, 92, -60)}{HOJA(140, 60, 20)}</g>', P("hoja") - 0.4, P("mar") - 0.3, lon=12, lat=50, dx=150, dy=-60)
J(f'tl.fromTo("#rama", {{rotation:-7}}, {{rotation:7, svgOrigin:"30 210", duration:0.38, yoyo:true, repeat:3, ease:"sine.inOut", immediateRender:false}}, {P("hoja") - 0.4:.2f}); tl.to("#rama", {{rotation:0, svgOrigin:"30 210", duration:0.6, ease:"power2.out"}}, {P("moviendose") + 0.1:.2f});')
# 2c) el mar: una línea de oleaje que se queda plana como un espejo
i = icono(f'<g id="mar"><path d="M10,120 C30,80 50,80 70,120 S110,160 130,120 S170,80 190,120 S220,150 235,120" {AC}/><path d="M10,170 H230" stroke="#7fd3ff" stroke-width="2" opacity="0.4"/></g>', P("mar") + 0.6, FE(2) + 0.5, x=540, y=640, w=300)
J(f'tl.to("#mar", {{scaleY:0.04, svgOrigin:"120 120", duration:1.6, ease:"power2.inOut"}}, {P("espejo") - 0.4:.2f});')
capa("espejo", P("espejo") - 0.4, 1, 1.4); capa("espejo", FE(2) + 0.6, 0, 1.0)
# 4) pan: el olor se encoge hasta quedarse junto a la panadería
i = icono(f'<g><path d="M40,170 C30,120 70,96 120,96 C170,96 210,120 200,170 Z" {ST}/><path d="M80,120 l12,20 M118,112 l12,22 M156,120 l12,20" {ST} stroke-width="4"/></g>'
          f'<g id="aroma"><path d="M90,80 c-14,-14 14,-24 0,-40 M120,76 c-14,-14 14,-26 0,-44 M150,80 c-14,-14 14,-24 0,-40" stroke="#ffd28a" stroke-width="5" fill="none" stroke-linecap="round"/></g>', F(4) + 2.0, FE(4) + 0.2, lon=-3.7, lat=40.4, dx=0, dy=-190)
J(f'tl.fromTo("#aroma", {{y:0, opacity:1}}, {{y:-14, opacity:0.6, duration:0.7, yoyo:true, repeat:3, ease:"sine.inOut", immediateRender:false}}, {F(4) + 2.0:.2f}); tl.to("#aroma", {{scale:0.25, opacity:0, svgOrigin:"120 90", duration:1.2}}, {P("apenas") - 0.2:.2f});')
# 6) maíz: planta con el polen cayendo recto
POL = "".join(f'<circle class="pmz" cx="{150 + (k % 3) * 9}" cy="{40 + (k // 3) * 6}" r="4" fill="#ffd23f"/>' for k in range(9))
i = icono(f'<g><path d="M120,230 L120,40" {ST}/><path d="M120,160 C90,140 70,150 56,170 M120,120 C150,100 170,110 184,130 M120,90 C96,72 80,78 70,92" {ST}/>'
          f'<g transform="translate(138,140) rotate(18)"><ellipse rx="13" ry="34" {ST} stroke="#ffd23f"/></g><path d="M120,40 l-16,-30 M120,40 l0,-34 M120,40 l16,-30" {ST} stroke="#ffd23f"/>{POL}</g>', F(6) + 1.6, FE(6) + 0.2, lon=-92, lat=41.5, dx=-60, dy=-200, w=300)
J(f'tl.fromTo(".pmz", {{y:0, opacity:1}}, {{y:170, opacity:0, duration:1.6, stagger:0.15, repeat:2, ease:"power1.in", immediateRender:false}}, {P("polen") - 0.6:.2f});')
# 7) Londres 1952: perfil de la ciudad que se hunde en el humo
i = icono(f'<g><path d="M20,200 V140 H50 V110 H70 V150 H96 V70 H104 V50 H112 V70 H120 V150 H150 V120 H180 V160 H200 V130 H222 V200 Z" {ST}/></g>'
          "".join(f'<path class="humo" d="M10,{y} C60,{y - 16} 100,{y + 16} 150,{y} S210,{y - 14} 232,{y}" stroke="#b9a888" stroke-width="18" fill="none" stroke-linecap="round" opacity="0"/>' for y in (196, 170, 144, 118, 92, 66)), P("humo") - 0.6, FE(7) + 0.2, lon=-0.1, lat=51.5, dx=200, dy=-170)
J(f'tl.to(".humo", {{opacity:0.85, duration:0.7, stagger:0.45}}, {P("humo") - 0.4:.2f});')
# 8) Londres congelada: escarcha + termómetro que baja
i = icono(f'<g><rect x="104" y="30" width="32" height="150" rx="16" {ST}/><circle cx="120" cy="190" r="26" {ST}/><rect id="merc" x="113" y="60" width="14" height="130" rx="7" fill="#ff8a7e"/>'
          f'<path d="M150,60 h20 M150,90 h14 M150,120 h20 M150,150 h14" {ST} stroke-width="3"/></g>', F(8) - 0.1, P("norte") - 0.5, lon=-0.1, lat=51.5, dx=180, dy=-120)
J(f'tl.to("#merc", {{scaleY:0.18, fill:"#7fd3ff", svgOrigin:"120 190", duration:1.4, ease:"power2.in"}}, {F(8) + 0.3:.2f});')
capa("hielo", F(8) + 0.2, 1, 1.4); capa("hielo", P("suaves") - 0.4, 0, 1.0)
# 9) nubes de lluvia que se paran en la costa
NUBE = f'<path d="M50,140 C30,140 30,104 58,104 C62,74 108,70 116,96 C130,80 168,86 166,114 C190,116 188,142 166,142 Z" {ST}/>'
i = icono(f'<g id="nubeG">{NUBE}<g id="lluvia"><path d="M80,160 l-8,22 M110,160 l-8,22 M140,160 l-8,22" {AC}/></g></g>', F(9) - 0.1, FE(9) - 0.5, lon=-12, lat=12, dx=-60, dy=-80)
J(f'tl.fromTo("#nubeG", {{x:-60}}, {{x:30, duration:2.4, ease:"power2.out", immediateRender:false}}, {F(9):.2f}); tl.to("#lluvia", {{opacity:0, duration:0.8}}, {P("tierra") if False else F(9) + 2.4:.2f});')
# 10) Amazonas resaltado entero + camión de polvo
capa("amaz", P("amazonas") - 0.3, 1, 0.8); capa("amazF", P("abono") - 0.2, 1, 2.0); capa("amaz", FE(11) + 0.2, 0, 0.8)
i = icono(f'<g><rect x="30" y="100" width="110" height="70" rx="6" {ST}/><path d="M140,120 H180 L206,146 V170 H140 Z" {ST}/><circle cx="70" cy="182" r="16" {ST}/><circle cx="176" cy="182" r="16" {ST}/>'
          f'<path d="M40,96 C60,70 100,70 120,96" stroke="#f0be6e" stroke-width="6" fill="none" stroke-linecap="round"/></g>', P("camiones") - 1.0, FE(10) + 0.2, lon=-28, lat=10, dx=0, dy=-150)
# 11) Bodélé: la cuenca resaltada y el polvo que sube
capa("bodP", F(11) + 0.2, 1, 0.6); capa("bodP", FE(11) + 0.4, 0, 0.5)
# 12) Biosfera 2: cúpula con un árbol que se parte
i = icono(f'<g><path d="M20,200 A100,100 0 0 1 220,200 Z" {AC}/><path d="M60,200 A60,100 0 0 1 180,200 M20,200 H220" stroke="#7fd3ff" stroke-width="3" fill="none" opacity="0.6"/>'
          f'<g id="arbol"><path d="M120,200 V120" {ST}/><circle cx="120" cy="104" r="26" {ST}/></g></g>', P("biosfera") - 0.3, FE(12) + 0.2, lon=-110.85, lat=32.58, dx=-230, dy=-200)
J(f'tl.to("#arbol", {{rotation:72, svgOrigin:"120 172", duration:0.9, ease:"power2.in"}}, {P("partian") - 0.2:.2f});')
# 14) el Sol
i = icono(f'<g id="solI"><circle cx="120" cy="120" r="40" stroke="#ffd28a" stroke-width="6" fill="none"/>' + "".join(f'<path d="M{120 + 60 * math.cos(a):.0f},{120 + 60 * math.sin(a):.0f} L{120 + 90 * math.cos(a):.0f},{120 + 90 * math.sin(a):.0f}" stroke="#ffd28a" stroke-width="6" stroke-linecap="round"/>' for a in [k * math.pi / 4 for k in range(8)]) + '</g>',
          P("sol") - 0.4, FE(14) + 0.3, x=170, y=700, w=220)
J(f'tl.fromTo("#solI", {{rotation:0}}, {{rotation:90, svgOrigin:"120 120", duration:{FE(14) - P("sol") + 0.7:.2f}, ease:"none", immediateRender:false}}, {P("sol") - 0.4:.2f});')
capa("celdas", P("aire") - 0.5, 1, 0.8); capa("celdas", FE(14) + 0.6, 0, 0.8)
# ------------------------------------------------------------------ montaje
ESTR = "".join(f'<i style="left:{rr.randint(0, 1078)}px;top:{rr.randint(0, 1918)}px;width:{rr.choice([1, 2, 2, 3])}px;height:{rr.choice([1, 2, 2, 3])}px;opacity:{rr.uniform(0.25, 0.9):.2f}"></i>' for _ in range(260))
_S = open(os.path.join(BASE, "_subs.py"), encoding="utf-8").read()
exec(re.sub(r"CLAVE = set\(.*?\]\)", lambda m: 'CLAVE = set(norm(w) for w in ["detuviera", "silencio", "espejo", "olas", "antartida", "alaska", "olores", "pan", "hora", "maiz", "mazorca", "humo", "1952", "miles", "congelaria", "norte", "suaves", "atlantico", "desierto", "amazonas", "millon", "chad", "biosfera", "partian", "huracan", "imposible", "sol", "moverse", "lluvia", "comida", "respiras"])', _S, count=1, flags=re.S))
html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script><script src="assets/d3-array.min.js"></script><script src="assets/d3-geo.min.js"></script><script src="assets/mundo.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#02050b}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;color:#fff;background:radial-gradient(ellipse at 50% 52%,#0c1a33 0%,#050b18 55%,#02050b 100%)}}
#estrellas{{position:absolute;inset:0}} #estrellas i{{position:absolute;border-radius:50%;background:#cfe3ff}}
canvas{{position:absolute;left:0;top:0}}
#vineta{{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 50% 50%,rgba(0,0,0,0) 58%,rgba(0,0,0,0.55) 100%)}}
#bajo{{position:absolute;left:0;right:0;bottom:0;height:720px;pointer-events:none;background:linear-gradient(rgba(2,5,11,0),rgba(2,5,11,0.78))}}
#fxl{{position:absolute;inset:0;z-index:58;pointer-events:none}}
.lab{{position:absolute;left:0;top:0;opacity:0;white-space:nowrap;text-shadow:0 2px 10px rgba(0,0,0,0.9)}}
.lab small{{display:block;font:700 17px Inter;letter-spacing:4px;color:#7fd3ff;margin-bottom:2px}} .lab b{{display:block;font:500 34px Inter;letter-spacing:-0.3px}}
.dato{{position:absolute;left:64px;top:1450px;opacity:0;max-width:900px;text-shadow:0 2px 14px rgba(0,0,0,0.8)}}
.dato small{{display:flex;align-items:center;gap:14px;font:700 20px Inter;letter-spacing:5px;color:#7fd3ff;margin-bottom:10px}} .dato small::before{{content:"";width:38px;height:2px;background:#7fd3ff}}
.dato b{{display:block;font:300 74px/1.04 Inter;letter-spacing:-2px}} .dato em{{display:block;font-style:normal;font:400 28px Inter;color:rgba(255,255,255,0.7);margin-top:10px}}
#kmh{{position:absolute;left:64px;top:1450px;text-shadow:0 2px 14px rgba(0,0,0,0.8)}} #kmh small{{display:flex;align-items:center;gap:14px;font:700 20px Inter;letter-spacing:5px;color:#7fd3ff;margin-bottom:10px}} #kmh small::before{{content:"";width:38px;height:2px;background:#7fd3ff}}
#kmh b{{display:block;font:200 120px/1 Inter;letter-spacing:-4px;font-variant-numeric:tabular-nums}}

.ico{{position:absolute;left:0;top:0;opacity:0;filter:drop-shadow(0 4px 14px rgba(0,0,0,0.85))}}
#grano{{position:absolute;inset:0;z-index:56;pointer-events:none;opacity:0.035;background:url(assets/grano.png);mix-blend-mode:overlay}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:520px;z-index:55;pointer-events:none;background:linear-gradient(rgba(2,5,11,0.7),rgba(2,5,11,0))}}
#marca{{position:absolute;left:0;right:0;top:1820px;text-align:center;font:600 26px Inter;color:#ffffff;opacity:0.45;pointer-events:none;z-index:61}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 56px Inter;color:rgba(255,255,255,0.55);line-height:1.22;text-shadow:0 3px 14px rgba(0,0,0,0.8)}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:2px solid #7fd3ff;border-radius:6px;background:rgba(127,211,255,0.14);opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="estrellas">{ESTR}</div>
  <canvas id="cv" width="1080" height="1920"></canvas>
  <div id="vineta"></div><div id="bajo"></div>
  <div id="topsombra"></div><div id="grano"></div>
  <div id="fxl">{"".join(FXL)}</div>
  <div id="marca">@mundo.supuesto</div>
  <div id="subs" data-layout-allow-overlap>{"".join(SUBS)}</div>
  <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
</div>
<script>
const fmt = (v, d) => {{ const s = v.toFixed(d).split("."); return s[0].replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ".") + (s[1] ? "," + s[1] : ""); }};
const S = {{ t:0, W:0, va:1, lon:{INI["lon"]}, lat:{INI["lat"]}, sc:{INI["sc"]}, olas:0, swell:0, swellA:0, olor:0, olorV:1, vuelos:0, vueloA:0, vueloB:0, chorro:0, maiz:0, maizG:0, smog:0, latl:0, oeste:0, seco:0, humedad:0, polvo:0, bodele:0, bio:0, hur:0, solar:0, espejo:0, pulso:0, hielo:0, amaz:0, amazF:0, bodP:0, celdas:0 }};
const cv = document.getElementById("cv"), g = cv.getContext("2d");
const proj = d3.geoOrthographic().clipAngle(90).precision(0.4);
const path = d3.geoPath(proj, g);
const GRAT = d3.geoGraticule10(), SPH = {{type:"Sphere"}};
const LABS = [], LV = {{}}, ICS = [], IV = {{}};
function rnd(i) {{ const x = Math.sin(i * 12.9898) * 43758.5453; return x - Math.floor(x); }}
const N = 2600, SEED = [];
for (let i = 0; i < N; i++) {{ const u = rnd(i + 1), v = rnd(i + 7.3); SEED.push([u * 360 - 180, Math.asin(2 * v - 1) * 180 / Math.PI, rnd(i + 3.1) * {L_VIDA}]); }}
function campo(lon, lat) {{
  const p = lat * Math.PI / 180, l = lon * Math.PI / 180;
  const u = -7.5 * Math.cos(6 * p) * (0.75 + 0.25 * Math.cos(p)) + 2.6 * Math.sin(3 * l + 2 * p) + 1.6 * Math.cos(5 * l - 3 * p);
  const v = 2.4 * Math.sin(6 * p) * Math.cos(2 * l) + 2.2 * Math.sin(4 * l + p * 3) - 1.2 * Math.cos(3 * l - 2 * p);
  return [u / Math.max(0.25, Math.cos(p)), v];
}}
function particulas(vis) {{
  const dt = 0.1; g.lineCap = "round"; g.lineWidth = 1.6;
  for (let i = 0; i < N; i++) {{
    const sd = SEED[i]; const age = ((S.W + sd[2]) % {L_VIDA} + {L_VIDA}) % {L_VIDA};
    let lon = sd[0], lat = sd[1]; const n = Math.floor(age / dt); const tr = [];
    for (let k = 0; k < n; k++) {{ const f = campo(lon, lat); lon += f[0] * dt; lat = Math.max(-85, Math.min(85, lat + f[1] * dt)); if (k >= n - 6) tr.push([lon, lat]); }}
    if (tr.length < 2) continue;
    const vida = Math.sin(Math.PI * age / {L_VIDA});
    g.beginPath(); let ok = 0;
    for (const q of tr) {{ if (!vis(q)) {{ ok = 0; continue; }} const s = proj(q); if (ok) g.lineTo(s[0], s[1]); else g.moveTo(s[0], s[1]); ok = 1; }}
    const sp = Math.hypot(...campo(lon, lat));
    g.strokeStyle = `rgba(${{Math.round(150 + Math.min(105, sp * 10))}},${{Math.round(215 + Math.min(40, sp * 4))}},255,${{(0.75 * vida * S.va).toFixed(3)}})`; g.stroke();
  }}
}}
const NY = [-74, 40.7], LON = [-0.1, 51.5], BOD = [18, 17], AMA = [-62, -3], STORM = [-165, -55], BIO = [-110.85, 32.58], MAD = [-3.7, 40.4];
const MAIZ = [[-92, 41.5, 6], [-97, 38, 4], [-52, -20, 4], [-61, -33, 3.5], [-100, 20, 3]];
const HUR = [[-60, 18], [-78, 25], [-45, 15]];
function poli(c) {{ let p = {{type:"Polygon", coordinates:[c]}}; if (d3.geoArea(p) > 2 * Math.PI) p = {{type:"Polygon", coordinates:[c.slice().reverse()]}}; return p; }}
const AMZ = poli([[-79,-2],[-77,2],[-72,3],[-67,4],[-62,4],[-58,3],[-54,1],[-50,-1],[-49,-4],[-52,-8],[-55,-12],[-60,-14],[-65,-15],[-69,-14],[-72,-12],[-75,-9],[-77,-6],[-79,-2]]);
const BODP = poli([[16,16.2],[17.2,15.6],[18.7,16.2],[19.2,17.3],[18.1,18.2],[16.5,17.8],[16,16.2]]);
const CELDAS = [[[-60,5],[-20,22],[20,28]], [[60,-5],[20,-22],[-20,-28]], [[-80,35],[-40,48],[0,58]], [[80,-35],[40,-48],[0,-58]]];
function glow(x, y, r, col, a) {{ if (a <= 0.001) return; const gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, col.replace("A", a)); gr.addColorStop(1, col.replace("A", 0)); g.fillStyle = gr; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); }}
function linea(a, b, col, w) {{ g.strokeStyle = col; g.lineWidth = w; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); }}
function frame() {{
  const t = S.t, R = S.sc, cy = 1040;
  const wv = 2 * Math.PI * t / {DUR:.3f};
  const Rr = R * (1 + 0.025 * Math.sin(4 * wv)); proj.scale(Rr).translate([540, cy]).rotate([-(S.lon + 1.6 * Math.sin(3 * wv)), -(S.lat + 0.8 * Math.sin(2 * wv))]);
  const centro = [S.lon + 1.6 * Math.sin(3 * wv), S.lat + 0.8 * Math.sin(2 * wv)];
  const vis = (q) => d3.geoDistance(q, centro) < Math.PI / 2 - 0.01;
  g.clearRect(0, 0, 1080, 1920);
  glow(540, cy, R * 1.18, "rgba(80,170,255,A)", 0.28);
  let gr = g.createRadialGradient(540 - R * 0.35, cy - R * 0.35, R * 0.1, 540, cy, R);
  gr.addColorStop(0, "#14406b"); gr.addColorStop(0.7, "#0a2747"); gr.addColorStop(1, "#061a31");
  g.fillStyle = gr; g.beginPath(); path(SPH); g.fill();
  const sec = S.seco;
  g.fillStyle = `rgb(${{Math.round(38 + 92 * sec)}},${{Math.round(58 + 40 * sec)}},${{Math.round(46 + 12 * sec)}})`;
  g.beginPath(); path(LAND); g.fill();
  g.strokeStyle = "rgba(150,210,255,0.35)"; g.lineWidth = 1.1; g.beginPath(); path(LAND); g.stroke();
  g.strokeStyle = "rgba(255,255,255,0.10)"; g.lineWidth = 0.8; g.beginPath(); path(BORDERS); g.stroke();
  g.strokeStyle = "rgba(255,255,255,0.05)"; g.lineWidth = 1; g.beginPath(); path(GRAT); g.stroke();
  if (S.humedad > 0.01) for (let k = 0; k < 40; k++) {{ const lat0 = -30 + (k % 10) * 7, lon0 = -40 + Math.floor(k / 10) * 4 + ((t * 3 + k) % 14);
      const a = [lon0, lat0], b = [lon0 + 6, lat0 + 1]; if (!vis(a) || !vis(b)) continue; linea(proj(a), proj(b), `rgba(120,200,255,${{0.6 * S.humedad}})`, 3); }}
  particulas(vis);
  if (S.olas > 0.01) for (let k = 0; k < 14; k++) {{ const r = ((t * 0.9 + k * 1.3) % 18) + 2; const c = d3.geoCircle().center([-150 + (k % 3) * 25 - 25, -30 + (k % 4) * 9]).radius(r)();
      g.strokeStyle = `rgba(190,230,255,${{(0.35 * S.olas * (1 - r / 20)).toFixed(3)}})`; g.lineWidth = 2; g.beginPath(); path(c); g.stroke(); }}
  if (S.swellA > 0.01) {{ for (let k = 0; k < 6; k++) {{ const r = Math.max(0.5, S.swell * 118 - k * 7); const c = d3.geoCircle().center(STORM).radius(r)();
      g.strokeStyle = `rgba(160,225,255,${{(0.55 * S.swellA * (1 - k / 6)).toFixed(3)}})`; g.lineWidth = 3; g.beginPath(); path(c); g.stroke(); }}
    if (vis(STORM)) {{ const ps = proj(STORM); glow(ps[0], ps[1], 60, "rgba(220,240,255,A)", 0.6 * S.swellA); }} }}
  if (S.olor > 0.01 && vis(MAD)) {{ const p = proj(MAD);
      g.save(); g.translate(p[0], p[1]); g.globalAlpha = S.olor;
      const L = 420 * S.olorV + 40 * (1 - S.olorV), Wd = 70 * S.olorV + 40 * (1 - S.olorV);
      const gg = g.createRadialGradient(0, 0, 0, L * 0.5, 0, L); gg.addColorStop(0, "rgba(255,200,120,0.75)"); gg.addColorStop(1, "rgba(255,200,120,0)");
      g.fillStyle = gg; g.beginPath(); g.ellipse(L * 0.45 * S.olorV, 0, L * 0.55 + 20, Wd, 0, 0, 7); g.fill();
      g.fillStyle = "#ffd28a"; g.beginPath(); g.arc(0, 0, 7, 0, 7); g.fill(); g.restore(); }}
  if (S.chorro > 0.01) for (let k = 0; k < 60; k++) {{ const u = ((t * 0.25 + k / 60) % 1), lo = -80 + u * 85, la = 44 + 6 * Math.sin(u * 5 + k) + (k % 5) - 2; const a = [lo, la], b = [lo + 4, la + 0.4];
      if (!vis(a) || !vis(b)) continue; linea(proj(a), proj(b), `rgba(255,190,90,${{(0.5 * S.chorro * Math.sin(Math.PI * u)).toFixed(3)}})`, 2.5); }}
  if (S.vuelos > 0.01) {{ const ruta = {{type:"LineString", coordinates:[NY, LON]}};
      g.setLineDash([8, 10]); g.strokeStyle = `rgba(255,255,255,${{0.55 * S.vuelos}})`; g.lineWidth = 2.5; g.beginPath(); path(ruta); g.stroke(); g.setLineDash([]);
      const ip = d3.geoInterpolate(NY, LON); let f = null;
      if (S.vueloB > 0) f = 1 - S.vueloB; else if (S.vueloA > 0) f = S.vueloA;
      if (f !== null) {{ const q = ip(f); if (vis(q)) {{ const p = proj(q), q2 = ip(Math.min(1, f + 0.01)), p2 = proj(q2); let an = Math.atan2(p2[1] - p[1], p2[0] - p[0]); if (S.vueloB > 0) an += Math.PI;
          glow(p[0], p[1], 36, "rgba(255,255,255,A)", 0.5 * S.vuelos); g.save(); g.translate(p[0], p[1]); g.rotate(an); g.fillStyle = "#ffffff"; g.beginPath();
          g.moveTo(22, 0); g.lineTo(10, -3); g.lineTo(-2, -20); g.lineTo(-8, -20); g.lineTo(0, -3); g.lineTo(-14, -3); g.lineTo(-20, -10); g.lineTo(-24, -10); g.lineTo(-20, 0); g.lineTo(-24, 10); g.lineTo(-20, 10); g.lineTo(-14, 3); g.lineTo(0, 3); g.lineTo(-8, 20); g.lineTo(-2, 20); g.lineTo(10, 3); g.closePath(); g.fill(); g.restore(); }} }} }}
  if (S.maiz > 0.01) for (const [lo, la, r] of MAIZ) {{ const c = d3.geoCircle().center([lo, la]).radius(r)();
      g.fillStyle = `rgba(${{Math.round(255 - 140 * S.maizG)}},${{Math.round(205 - 90 * S.maizG)}},${{Math.round(80 + 30 * S.maizG)}},${{(0.55 * S.maiz).toFixed(3)}})`; g.beginPath(); path(c); g.fill(); }}
  if (S.smog > 0.01 && vis(LON)) {{ const p = proj(LON); for (let k = 0; k < 7; k++) glow(p[0] + 60 * Math.sin(k * 2.1 + t * 0.2), p[1] + 40 * Math.cos(k * 1.7), 140 + 70 * S.smog + k * 18, "rgba(170,150,110,A)", 0.45 * S.smog); }}
  if (S.latl > 0.01) for (const [la, col] of [[51.5, "255,200,120"], [40.7, "127,211,255"]]) {{ const c = {{type:"LineString", coordinates:d3.range(-90, 31, 2).map(lo => [lo, la])}};
      g.setLineDash([4, 8]); g.strokeStyle = `rgba(${{col}},${{0.7 * S.latl}})`; g.lineWidth = 2; g.beginPath(); path(c); g.stroke(); g.setLineDash([]); }}
  if (S.oeste > 0.01) for (let k = 0; k < 40; k++) {{ const u = ((t * 0.3 + k / 40) % 1), lo = -45 + u * 45, la = 46 + (k % 8) * 1.4; const a = [lo, la], b = [lo + 3, la + 0.3];
      if (!vis(a) || !vis(b)) continue; linea(proj(a), proj(b), `rgba(255,170,90,${{(0.7 * S.oeste * Math.sin(Math.PI * u)).toFixed(3)}})`, 3); }}
  if (S.polvo > 0.01) {{ const ip = d3.geoInterpolate(BOD, AMA);
      for (let k = 0; k < 220; k++) {{ const u = ((t * 0.18 + k / 220) % 1), q = ip(u); const off = 3.5 * Math.sin(k * 7.3) * Math.sin(Math.PI * u); const qq = [q[0] + off, q[1] + off * 0.6 + 6 * Math.sin(Math.PI * u)];
        if (!vis(qq)) continue; const p = proj(qq); g.fillStyle = `rgba(240,190,110,${{(0.85 * S.polvo * Math.sin(Math.PI * u)).toFixed(3)}})`; g.beginPath(); g.arc(p[0], p[1], 2.6, 0, 7); g.fill(); }}
      if (vis(BOD)) {{ const p = proj(BOD); glow(p[0], p[1], 70, "rgba(240,190,110,A)", 0.6 * S.polvo); }} }}
  if (S.bodele > 0.01 && vis(BOD)) {{ const p = proj(BOD); glow(p[0], p[1], 90, "rgba(255,210,140,A)", 0.7 * S.bodele); }}
  if (S.bio > 0.01 && vis(BIO)) {{ const p = proj(BIO); glow(p[0], p[1], 50 + 10 * Math.sin(t * 4), "rgba(140,255,190,A)", 0.7 * S.bio); }}
  if (S.hur > 0.01) for (const [lo, la] of HUR) {{ if (!vis([lo, la])) continue; const p = proj([lo, la]);
      for (let k = 0; k < 90; k++) {{ const a = k * 0.35 + t * 1.6, r = 4 + k * 1.15; g.fillStyle = `rgba(255,255,255,${{(0.55 * S.hur * (1 - k / 95)).toFixed(3)}})`; g.beginPath(); g.arc(p[0] + Math.cos(a) * r, p[1] + Math.sin(a) * r * 0.9, 3.4, 0, 7); g.fill(); }} }}
  if (S.amaz > 0.01) {{ const a = S.amaz; g.fillStyle = `rgba(${{Math.round(60 + 150 * S.amazF)}},${{Math.round(200 - 40 * S.amazF)}},${{Math.round(110 - 50 * S.amazF)}},${{(0.45 * a).toFixed(3)}})`; g.beginPath(); path(AMZ); g.fill();
      g.strokeStyle = `rgba(160,255,190,${{(0.9 * a * (1 - 0.5 * S.amazF)).toFixed(3)}})`; g.lineWidth = 3; g.setLineDash([10, 8]); g.lineDashOffset = -t * 30; g.beginPath(); path(AMZ); g.stroke(); g.setLineDash([]); }}
  if (S.bodP > 0.01) {{ g.fillStyle = `rgba(240,190,110,${{(0.55 * S.bodP).toFixed(3)}})`; g.beginPath(); path(BODP); g.fill(); g.strokeStyle = `rgba(255,220,160,${{S.bodP}})`; g.lineWidth = 3; g.beginPath(); path(BODP); g.stroke();
      if (vis(BOD)) {{ const p = proj(BOD); for (let k = 0; k < 40; k++) {{ const u = ((t * 0.5 + k / 40) % 1); g.fillStyle = `rgba(240,190,110,${{(S.bodP * (1 - u)).toFixed(3)}})`; g.beginPath(); g.arc(p[0] + 30 * Math.sin(k * 3.7) - u * 160, p[1] - u * 140 + 20 * Math.cos(k), 3 + u * 4, 0, 7); g.fill(); }} }} }}
  if (S.hielo > 0.01) {{ g.fillStyle = `rgba(225,242,255,${{(0.75 * S.hielo).toFixed(3)}})`; g.beginPath(); path(UKIE); g.fill(); g.strokeStyle = `rgba(255,255,255,${{S.hielo}})`; g.lineWidth = 3; g.beginPath(); path(UKIE); g.stroke();
      g.save(); g.beginPath(); path(UKIE); g.clip(); g.strokeStyle = `rgba(140,200,255,${{(0.8 * S.hielo).toFixed(3)}})`; g.lineWidth = 1.6;
      for (let k = 0; k < 160; k++) {{ const q = [-11 + (k * 37 % 140) / 10, 49.5 + (k * 53 % 110) / 10]; if (!vis(q)) continue; const p = proj(q), s = 5 + (k % 4) * 3; g.beginPath();
        for (let j = 0; j < 3; j++) {{ const an = j * Math.PI / 3 + k; g.moveTo(p[0] - Math.cos(an) * s, p[1] - Math.sin(an) * s); g.lineTo(p[0] + Math.cos(an) * s, p[1] + Math.sin(an) * s); }} g.stroke(); }} g.restore(); }}
  if (S.celdas > 0.01) for (const c of CELDAS) {{ const ln = {{type:"LineString", coordinates:c}}; g.setLineDash([22, 16]); g.lineDashOffset = -t * 60; g.strokeStyle = `rgba(255,255,255,${{(0.75 * S.celdas).toFixed(3)}})`; g.lineWidth = 4; g.beginPath(); path(ln); g.stroke(); g.setLineDash([]);
      const e = c[c.length - 1], b = c[c.length - 2]; if (vis(e) && vis(b)) {{ const pe = proj(e), pb = proj(b), an = Math.atan2(pe[1] - pb[1], pe[0] - pb[0]); g.fillStyle = `rgba(255,255,255,${{S.celdas}})`; g.beginPath(); g.moveTo(pe[0] + Math.cos(an) * 16, pe[1] + Math.sin(an) * 16); g.lineTo(pe[0] + Math.cos(an + 2.5) * 14, pe[1] + Math.sin(an + 2.5) * 14); g.lineTo(pe[0] + Math.cos(an - 2.5) * 14, pe[1] + Math.sin(an - 2.5) * 14); g.fill(); }} }}
  if (S.espejo > 0.01) {{ glow(540 - R * 0.18, cy - R * 0.22, R * 0.55, "rgba(255,250,235,A)", 0.45 * S.espejo); glow(540 - R * 0.18, cy - R * 0.22, R * 0.14, "rgba(255,255,255,A)", 0.85 * S.espejo); }}
  if (S.pulso > 0.01 && S.pulso < 0.999) {{ g.strokeStyle = `rgba(127,211,255,${{(0.8 * (1 - S.pulso)).toFixed(3)}})`; g.lineWidth = 4; g.beginPath(); g.arc(540, cy, R * (1 + 0.6 * S.pulso), 0, 7); g.stroke(); }}
  gr = g.createRadialGradient(540 - R * 0.55, cy - R * 0.3, R * 0.2, 540 - R * 0.2, cy, R * 1.25);
  gr.addColorStop(0, "rgba(0,0,0,0)"); gr.addColorStop(0.62, "rgba(0,0,0,0)"); gr.addColorStop(1, "rgba(0,4,12,0.72)");
  g.fillStyle = gr; g.beginPath(); path(SPH); g.fill();
  if (S.solar > 0.01) {{ const eq = {{type:"LineString", coordinates:d3.range(-180, 181, 3).map(lo => [lo, 0])}};
      g.save(); g.beginPath(); path(SPH); g.clip(); g.filter = "blur(18px)"; g.strokeStyle = `rgba(255,120,60,${{0.5 * S.solar}})`; g.lineWidth = R * 0.32; g.beginPath(); path(eq); g.stroke(); g.restore();
      glow(540 - R * 1.25, cy - R * 0.2, R * 0.9, "rgba(255,225,150,A)", 0.55 * S.solar); }}
  glow(540 - R * 0.38, cy - R * 0.42, R * 0.5, "rgba(255,255,255,A)", 0.08);
  for (const L of LABS) {{ const el = document.getElementById("lb" + L.i); const o = LV["l" + L.i] || 0; el.style.opacity = o;
    if (o > 0.01) {{ const q = [L.lon, L.lat]; if (!vis(q)) {{ el.style.opacity = 0; continue; }} const p = proj(q);
      const dx = L.lado === "i" ? -70 : 70; linea(p, [p[0] + dx, p[1] - 60 + L.dy], `rgba(127,211,255,${{o}})`, 2);
      g.fillStyle = `rgba(255,255,255,${{o}})`; g.beginPath(); g.arc(p[0], p[1], 6, 0, 7); g.fill(); glow(p[0], p[1], 22, "rgba(127,211,255,A)", 0.5 * o);
      const w = el.offsetWidth; let x = L.lado === "i" ? p[0] + dx - w - 10 : p[0] + dx + 10; x = Math.max(24, Math.min(1056 - w, x));
      el.style.transform = `translate(${{x}}px, ${{p[1] - 60 + L.dy - el.offsetHeight / 2}}px)`; }} }}
  for (const I of ICS) {{ const el = document.getElementById("ic" + I.i); const o = IV["v" + I.i] || 0; el.style.opacity = o; if (o < 0.01) continue;
    let x = I.x, y = I.y; if (I.lon !== null) {{ const q = [I.lon, I.lat]; if (!vis(q)) {{ el.style.opacity = 0; continue; }} const p = proj(q); x = p[0] + I.dx; y = p[1] + I.dy; }}
    x = Math.max(I.w / 2 + 10, Math.min(1070 - I.w / 2, x)); el.style.transform = `translate(${{x - I.w / 2}}px, ${{y - I.w / 2}}px) scale(${{(0.85 + 0.15 * o).toFixed(3)}})`; }}
}}
const tl = gsap.timeline({{ paused: true, onUpdate: frame }});
tl.to(S, {{t:{DUR:.2f}, duration:{DUR:.2f}, ease:"none"}}, 0);
{chr(10).join(tl)}
tl.to({{}}, {{duration:0.01}}, {DUR - 0.01});
window.__timelines["main"] = tl;
tl.seek(0); frame();
</script>
</body></html>"""
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump([], open(os.path.join(BASE, "efectos.json"), "w"))
json.dump([[0, 0.0], [DUR, 0.0]], open(os.path.join(BASE, "ambiente.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones · W_fin {W_FIN}")

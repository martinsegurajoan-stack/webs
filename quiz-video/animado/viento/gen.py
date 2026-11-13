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


# ================================================================== CAPAS EXTRA (efectos sobre el planeta)
J(f'tl.fromTo(S, {{pulso:0}}, {{pulso:1, duration:1.6, ease:"power2.out", immediateRender:false}}, {PARA:.2f});')
capa("hoja", P("hoja") - 0.4, 1, 0.5); capa("hoja", P("mar") - 0.3, 0, 0.5)
capa("espejo", P("espejo") - 0.6, 1, 1.6); capa("espejo", FE(2) + 0.6, 0, 1.0)
capa("pol", P("polen") - 0.6, 1, 0.5); capa("pol", FE(6) + 0.3, 0, 0.5)
capa("hielo", F(8) + 0.2, 1, 1.6); capa("hielo", P("suaves") - 0.4, 0.15, 1.0); capa("hielo", FE(8) + 0.3, 0, 0.5)
capa("lluviaS", F(9) - 0.1, 1, 0.6); capa("lluviaS", P("desierto") - 0.4, 0, 1.0)
capa("amaz", P("amazonas") - 0.3, 1, 0.8); capa("amazF", P("abono") - 0.2, 1, 2.0); capa("amaz", FE(11) + 0.2, 0, 0.8)
capa("bodP", F(11) + 0.2, 1, 0.6); capa("bodP", FE(11) + 0.4, 0, 0.5)
capa("celdas", P("aire") - 0.5, 1, 0.8); capa("celdas", FE(14) + 0.6, 0, 0.8)
J(f'tl.fromTo(S, {{arbol:0}}, {{arbol:1, duration:0.9, ease:"power2.in", immediateRender:false}}, {P("partian") - 0.2:.2f});')
# iluminación por escena (ángulo del Sol respecto a la cámara: 0 = de frente, 90 = lado, 170 = noche)
for t, ang, d in ((P("mar") - 0.5, -25, 2.4), (F(4) - 0.3, -35, 2.4), (F(5) - 0.3, 150, 2.6), (F(6) - 0.3, -30, 2.4), (F(7) - 0.3, 168, 2.4),
                  (F(8) - 0.3, 35, 2.4), (F(9) - 0.3, -30, 2.4), (F(13) - 0.3, -20, 2.0), (P("sol") - 0.6, -60, 2.2), (FE(14) + 0.2, 55, 4.0)):
    J(f'tl.to(S, {{sol:{ang}, duration:{d}, ease:"power2.inOut"}}, {t:.2f});')
# ------------------------------------------------------------------ montaje
ESTR = "".join(f'<i style="left:{rr.randint(0, 1078)}px;top:{rr.randint(0, 1918)}px;width:{rr.choice([1, 2, 2, 3])}px;height:{rr.choice([1, 2, 2, 3])}px;opacity:{rr.uniform(0.25, 0.9):.2f}"></i>' for _ in range(260))
_S = open(os.path.join(BASE, "_subs.py"), encoding="utf-8").read()
exec(re.sub(r"CLAVE = set\(.*?\]\)", lambda m: 'CLAVE = set(norm(w) for w in ["detuviera", "silencio", "espejo", "olas", "antartida", "alaska", "olores", "pan", "hora", "maiz", "mazorca", "humo", "1952", "miles", "congelaria", "norte", "suaves", "atlantico", "desierto", "amazonas", "millon", "chad", "biosfera", "partian", "huracan", "imposible", "sol", "moverse", "lluvia", "comida", "respiras"])', _S, count=1, flags=re.S))
import base64
def b64(f): return "data:image/jpeg;base64," + base64.b64encode(open(os.path.join(BASE, "assets", "tierra", f), "rb").read()).decode()
html = open(os.path.join(BASE, "_plantilla.html"), encoding="utf-8").read()
for k, v in (("%%DURX%%", f"{DUR:.3f}"), ("%%DUREND%%", f"{DUR - 0.01:.3f}"), ("%%DUR%%", f"{DUR}"), ("%%FXL%%", "".join(FXL)), ("%%SUBS%%", "".join(SUBS)),
             ("%%TL%%", chr(10).join(tl)), ("%%TDIA%%", b64("dia_q.jpg")), ("%%TNOCHE%%", b64("noche.jpg")), ("%%TNUBES%%", b64("nubes2k.jpg")), ("%%TMAR%%", b64("mar.jpg")), ("%%LV%%", f"{L_VIDA}"), ("%%HOJA%%", f"{P('moviendose'):.2f}")):
    html = html.replace(k, v)
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump([], open(os.path.join(BASE, "efectos.json"), "w"))
json.dump([[0, 0.0], [DUR, 0.0]], open(os.path.join(BASE, "ambiente.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones · W_fin {W_FIN}")

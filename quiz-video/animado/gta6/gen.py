#!/usr/bin/env python3
"""«Lo que NUNCA harías el día que salga GTA 6» — vídeo visual (fotos reales + grafismo, sin dibujos), HyperFrames + GSAP.
Cortes secos entre frases y una decoración distinta en cada frase. python3 gen.py → index.html + efectos.json"""
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
tl, FX, ESC, OVR = [], [], [], []
def J(s): tl.append(s)
NID = [0]
def nid(p="x"):
    NID[0] += 1
    return f"{p}{NID[0]}"

# ------------------------------------------------------------------ utilidades de animación
def escena(eid, html, t0, t1, z0=1.0, z1=1.06):
    """Una escena = un plano con corte seco. La cámara empuja muy despacio (nunca quieta)."""
    ESC.append(f'<div class="esc" id="{eid}"><div class="cam" id="{eid}-cam">{html}</div></div>')
    J(f'tl.set("#{eid}", {{opacity:0}}, 0); tl.set("#{eid}", {{opacity:1}}, {t0:.2f}); tl.set("#{eid}", {{opacity:0}}, {t1:.2f});')
    J(f'tl.fromTo("#{eid}-cam", {{scale:{z0}}}, {{scale:{z1}, duration:{t1 - t0:.2f}, ease:"sine.inOut", immediateRender:false}}, {t0:.2f});')
ROT = {}
def entra(sel, t, frm="opacity:0, y:60, scale:0.9", d=0.35, ease="back.out(1.8)"):
    rot = ROT.get(sel.lstrip("#"), 0) if "," not in sel else 0
    J(f'tl.set("{sel}", {{opacity:0}}, 0); tl.fromTo("{sel}", {{{frm}}}, {{opacity:1, x:0, y:0, scale:1, rotation:{rot}, duration:{d}, ease:"{ease}", immediateRender:false}}, {t:.2f});')
def golpe(sel, t, fx=True, desde=2.4):
    """Texto/sello que cae de golpe (slam) con sacudida de cámara."""
    J(f'tl.set("{sel}", {{opacity:0}}, 0); tl.fromTo("{sel}", {{opacity:0, scale:{desde}}}, {{opacity:1, scale:1, duration:0.22, ease:"power4.in", immediateRender:false}}, {t - 0.22:.2f});')
    J(f'tl.fromTo("#root-shake", {{x:0, y:0}}, {{x:"random(-14,14)", y:"random(-14,14)", duration:0.04, yoyo:true, repeat:5, ease:"none", immediateRender:false}}, {t:.2f}); tl.set("#root-shake", {{x:0, y:0}}, {t + 0.26:.2f});')
    if fx:
        FX.append(("golpe", t))
def sale(sel, t, d=0.2):
    J(f'tl.to("{sel}", {{opacity:0, scale:0.9, duration:{d}, ease:"power2.in"}}, {t:.2f});')
def flash(t, col="#ffffff"):
    J(f'tl.set("#flash", {{background:"{col}"}}, {t:.2f}); tl.fromTo("#flash", {{opacity:0.75}}, {{opacity:0, duration:0.3, ease:"power2.out", immediateRender:false}}, {t:.2f});')
def tarjeta(cid, src, x, y, w, h, rot=0, pos="50% 50%", borde="#ff4fa3", extra=""):
    """Foto en tarjeta con borde neón y sombra (las fotos de la portada son pequeñas: así se ven nítidas)."""
    ROT[cid] = rot
    return (f'<div class="card" id="{cid}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;transform:rotate({rot}deg);--b:{borde}">'
            f'<div class="ph" style="background-image:url(assets/fotos/{src});background-position:{pos}"></div>{extra}</div>')
def medalla(mid, n, color):
    c = {"bronce": ("#ffd1a3", "#c8743a", "#7a3a14"), "plata": ("#ffffff", "#c9d1dc", "#6b7684"), "oro": ("#fff6c2", "#ffc83a", "#a86a00")}[color]
    return (f'<div class="medal" id="{mid}" style="--a:{c[0]};--m:{c[1]};--o:{c[2]}"><div class="cinta"></div><div class="disco"><span>{n}</span></div></div>')
def chip(cid, txt, x, y, bg="#ff2f6d", col="#ffffff", size=40, extra_style=""):
    return f'<div class="chip" id="{cid}" style="left:{x}px;top:{y}px;background:{bg};color:{col};font-size:{size}px;{extra_style}">{txt}</div>'
def numero(nid_, n, x, y):
    return f'<div class="numero" id="{nid_}" style="left:{x}px;top:{y}px">{n}</div>'

# ================================================================== 1) GANCHO: la portada de GTA 6 (PS5) desde el fotograma 0
f1, f2 = 0.0, F(2)
h1 = (f'<div class="portada" id="port1"><img src="assets/fotos/portada_ps5.jpg"/></div>'
      '<div class="cruz" id="cruz1"><i></i><i></i></div>'
      '<div class="nohagas" id="noh1"><span class="x">✕</span> NO HAGAS ESTO</div>')
escena("e1", h1, f1, f2, 1.0, 1.05)
J('tl.fromTo("#port1", {scale:1.12, rotation:-2}, {scale:1, rotation:0, duration:0.6, ease:"power3.out", immediateRender:false}, 0);')
J('tl.fromTo("#noh1", {scale:1.25}, {scale:1, duration:0.4, ease:"back.out(2)", immediateRender:false}, 0);')
J(f'tl.fromTo("#noh1", {{scale:1}}, {{scale:1.06, duration:0.35, yoyo:true, repeat:5, ease:"sine.inOut", immediateRender:false}}, 0.6);')
J(f'tl.fromTo("#port1", {{boxShadow:"0 0 40px rgba(255,79,163,0.5)"}}, {{boxShadow:"0 0 90px rgba(255,79,163,0.95)", duration:0.6, yoyo:true, repeat:7, ease:"sine.inOut", immediateRender:false}}, 0);')
golpe("#cruz1", P("errores"))
J(f'tl.to("#port1 img", {{filter:"grayscale(0.7) brightness(0.7)", duration:0.2}}, {P("errores"):.2f});')
FX.append(("whoosh", 0.05))

# ================================================================== 2) NI LOCO (medalla de bronce)
h2 = (medalla("med2", 3, "bronce") + '<div class="tier" id="tier2"><small>LO QUE NO HARÍA</small>NI LOCO</div>'
      + tarjeta("c2", "rapero.jpg", 700, 1310, 300, 400, 6, borde="#ff8a3a"))
escena("e2", h2, f2, F(3))
entra("#med2", f2, "opacity:0, scale:0.2, rotation:-200", 0.5, "back.out(1.6)")
J(f'tl.fromTo("#med2 .disco", {{rotationY:0}}, {{rotationY:360, duration:0.8, ease:"power2.out", immediateRender:false}}, {f2:.2f});')
golpe("#tier2", P("loco"))
entra("#c2", P("loco") + 0.1, "opacity:0, x:300, rotation:20", 0.35)
FX.append(("whoosh", f2))

# ================================================================== 3) IR DIRECTO AL ONLINE (moto + carga de GTA Online)
h3 = (tarjeta("c3", "moto.jpg", 170, 560, 740, 885, -3, borde="#7a5cff")
      + '<div class="carga" id="carga3"><b>GTA ONLINE</b><div class="barra"><i id="bar3"></i></div><span>CARGANDO…</span></div>'
      + chip("d3", "DÍA 1", 120, 600, "#ffcf3a", "#1a0a2a", 46))
escena("e3", h3, F(3), F(4))
entra("#c3", F(3), "opacity:0, x:500, rotation:8", 0.35)
entra("#carga3", F(3) + 0.25, "opacity:0, y:120", 0.3)
J(f'tl.fromTo("#bar3", {{scaleX:0}}, {{scaleX:1, duration:{F(4) - F(3) - 0.3:.2f}, ease:"power1.in", immediateRender:false}}, {F(3) + 0.3:.2f});')
entra("#d3", P("directo"), "opacity:0, scale:2.2, rotation:-20", 0.25)

# ================================================================== 4) 13 AÑOS… Y UN NIÑO TE REVIENTA (contador + WASTED)
h4 = (tarjeta("c4", "pistolero.jpg", 120, 560, 840, 600, 2, borde="#ff4f4f")
      + '<div class="contador" id="cont4"><span id="n4">0</span><small>AÑOS ESPERANDO</small></div>'
      + '<div class="wasted" id="was4">WASTED</div>'
      + '<div class="killfeed" id="kf4"><b>xX_Niño2014_Xx</b> te ha eliminado</div>')
escena("e4", h4, F(4), F(5))
entra("#c4", F(4), "opacity:0, y:-300, rotation:-6", 0.35)
entra("#cont4", P("trece") - 0.15, "opacity:0, scale:0.4", 0.3)
J(f'tl.fromTo("#n4", {{innerText:0}}, {{innerText:13, snap:{{innerText:1}}, duration:0.7, ease:"power2.out", immediateRender:false}}, {P("trece") - 0.1:.2f});')
J(f'tl.to("#c4 .ph", {{filter:"grayscale(1) brightness(0.6)", duration:0.15}}, {P("reviente"):.2f});')
golpe("#was4", P("reviente") + 0.05)
entra("#kf4", P("reviente") + 0.3, "opacity:0, x:400", 0.3, "power3.out")
FX.append(("caja", P("trece")))

# ================================================================== 5-6) TIKTOK / YOUTUBE: un clip de 30 s te cuenta el final (SPOILER)
h5 = ('<div class="movil" id="mov5"><div class="pantalla" style="background-image:url(assets/fotos/lucia_jason.jpg)"></div>'
      '<div class="iconos"><i></i><i></i><i></i></div><div class="prog"><i id="prog5"></i></div>'
      '<div class="reloj" id="rel5">0:<span id="seg5">30</span></div><div class="oscurece" id="osc5"></div></div>'
      + chip("tk5", "TikTok", 60, 760, "#111111", "#ffffff", 48, "box-shadow:-5px 0 0 #25f4ee, 5px 0 0 #fe2c55")
      + chip("yt5", "YouTube", 700, 1040, "#ff0033", "#ffffff", 48)
      + '<div class="vs" id="vs6"><div><b>+10 AÑOS</b><small>DE ESPERA</small></div><em>VS</em><div><b>30 SEG</b><small>DE CLIP</small></div></div>'
      + '<div class="spoiler" id="sp6">SPOILER</div>')
escena("e5", h5, F(5), F(7))
entra("#mov5", F(5), "opacity:0, y:700, rotation:10", 0.4)
entra("#tk5", P("tiktok"), "opacity:0, x:-300, rotation:-15", 0.3)
entra("#yt5", P("youtube"), "opacity:0, x:300, rotation:15", 0.3)
J(f'tl.fromTo("#mov5 .pantalla", {{backgroundPosition:"62% 50%"}}, {{backgroundPosition:"40% 50%", duration:{F(7) - F(5):.2f}, ease:"none", immediateRender:false}}, {F(5):.2f});')
J(f'tl.fromTo("#prog5", {{scaleX:0}}, {{scaleX:1, duration:{P("final") - F(5):.2f}, ease:"none", immediateRender:false}}, {F(5):.2f});')
sale("#tk5, #yt5", F(6) - 0.1)
entra("#vs6", P("decada") - 0.1, "opacity:0, y:200", 0.35)
entra("#rel5", P("treinta") - 0.1, "opacity:0, scale:2", 0.25)
J(f'const o5 = {{v:30}}; tl.fromTo(o5, {{v:30}}, {{v:0, duration:{P("final") - P("treinta"):.2f}, ease:"none", immediateRender:false, onUpdate:() => {{ document.getElementById("seg5").textContent = String(Math.round(o5.v)).padStart(2, "0"); }}}}, {P("treinta"):.2f});')
J(f'tl.to("#osc5", {{opacity:0.6, duration:0.15}}, {P("final"):.2f});')
golpe("#sp6", P("final") + 0.05)
FX.append(("vibra", F(5) + 0.1))

# ================================================================== 7) ME LO PENSARÍA (medalla de plata)
h7 = (medalla("med7", 2, "plata") + '<div class="tier" id="tier7" style="font-size:112px"><small>LO QUE</small>ME LO PENSARÍA</div>'
      + tarjeta("c7", "heli.jpg", 700, 1330, 320, 340, 6, borde="#9fd6ff"))
escena("e7", h7, F(7), F(8))
entra("#med7", F(7), "opacity:0, scale:0.2, rotation:200", 0.5, "back.out(1.6)")
J(f'tl.fromTo("#med7 .disco", {{rotationY:0}}, {{rotationY:360, duration:0.8, ease:"power2.out", immediateRender:false}}, {F(7):.2f});')
golpe("#tier7", P("pensaria"))
entra("#c7", P("pensaria") + 0.1, "opacity:0, x:-300, rotation:-20", 0.35)
FX.append(("whoosh", F(7)))

# ================================================================== 8-9) LA EDICIÓN MÁS CARA: un coche dorado que consigues en una semana
dias = "".join(f'<div class="dia" id="dd{i}"><small>{d}</small><b>✓</b></div>' for i, d in enumerate("LMXJVSD"))
h8 = (tarjeta("c8", "coche.jpg", 300, 560, 480, 830, -2, borde="#ffc83a", extra='<div class="dorado" id="oro8"></div><div class="brillo" id="bri8"></div>')
      + '<div class="precio" id="pre8"><span>€€€</span><small>EDICIÓN MÁS CARA</small></div>'
      + f'<div class="semana" id="sem8">{dias}</div><div class="unaSem" id="us8">EN 1 SEMANA</div>')
escena("e8", h8, F(8), F(10))
entra("#c8", F(8), "opacity:0, y:500, rotation:6", 0.35)
entra("#pre8", P("cara") - 0.25, "opacity:0, scale:0.3, rotation:-40", 0.35)
J(f'tl.fromTo("#pre8", {{rotation:-6}}, {{rotation:6, duration:0.5, yoyo:true, repeat:5, ease:"sine.inOut", immediateRender:false}}, {P("cara") + 0.1:.2f});')
J(f'tl.to("#oro8", {{opacity:0.55, duration:0.3}}, {P("dorado") - 0.1:.2f}); tl.fromTo("#bri8", {{x:-700}}, {{x:700, duration:0.7, ease:"power2.inOut", immediateRender:false}}, {P("dorado"):.2f});')
FX.append(("brillo", P("dorado")))
entra("#sem8", P("consigues") - 0.1, "opacity:0, y:150", 0.3)
for i in range(7):
    t_ = P("consigues") + 0.15 + i * (P("semana") - P("consigues") - 0.1) / 7
    J(f'tl.to("#dd{i}", {{background:"#2fd27a", duration:0.08}}, {t_:.2f}); tl.fromTo("#dd{i} b", {{opacity:0, scale:2}}, {{opacity:1, scale:1, duration:0.15, immediateRender:false}}, {t_:.2f});')
golpe("#us8", P("semana") + 0.1, fx=False)
FX.append(("caja", P("semana") + 0.1))

# ================================================================== 10-11) PEDIR VACACIONES: tres días de gloria… ojeras y sin un euro
h10 = ('<div class="calendario" id="cal10"><div class="cab">VACACIONES</div><div class="rej">'
       + "".join(f'<div class="cd" id="cd{i}">{i + 18}</div>' for i in range(7)) + '</div></div>'
       + tarjeta("c11", "mujer.jpg", 80, 560, 520, 900, -3, pos="50% 30%", borde="#2fd27a")
       + '<div class="bateria" id="bat11"><div class="llena" id="niv11"></div><span><em id="pct11">100</em>%</span></div>'
       + '<div class="cartera" id="car11"><small>SALDO</small><b><span id="eur11">1.240</span> €</b></div>')
escena("e10", h10, F(10), F(12))
entra("#cal10", F(10), "opacity:0, y:-500, rotation:-8", 0.35)
for i in range(3):
    J(f'tl.to("#cd{i}", {{background:"#ff2f6d", color:"#ffffff", scale:1.12, duration:0.12}}, {P("vacaciones") + 0.15 + i * 0.18:.2f});')
J(f'tl.to("#cal10", {{x:300, y:-80, scale:0.62, rotation:6, duration:0.3, ease:"power3.inOut"}}, {F(11) - 0.15:.2f});')
entra("#c11", F(11), "opacity:0, x:-500, rotation:-12", 0.35)
J(f'tl.fromTo("#c11 .ph", {{scale:1}}, {{scale:1.08, duration:0.4, yoyo:true, repeat:3, ease:"sine.inOut", immediateRender:false}}, {F(11):.2f});')
entra("#bat11", P("trabajo") - 0.2, "opacity:0, x:300", 0.3)
J(f'tl.fromTo("#niv11", {{scaleX:1, background:"#2fd27a"}}, {{scaleX:0.06, background:"#ff3b2f", duration:0.8, ease:"power2.in", immediateRender:false}}, {P("ojeras") - 0.3:.2f});')
J(f'tl.fromTo("#pct11", {{innerText:100}}, {{innerText:3, snap:{{innerText:1}}, duration:0.8, ease:"power2.in", immediateRender:false}}, {P("ojeras") - 0.3:.2f});')
J(f'tl.to("#c11 .ph", {{filter:"grayscale(0.85) brightness(0.65)", duration:0.4}}, {P("ojeras") - 0.2:.2f});')
entra("#car11", P("sin", 1) if False else P("euro") - 0.6, "opacity:0, y:200", 0.25)
J(f'tl.fromTo("#eur11", {{innerText:1240}}, {{innerText:0, snap:{{innerText:1}}, duration:0.5, ease:"power3.in", immediateRender:false}}, {P("euro") - 0.35:.2f}); tl.to("#car11 b", {{color:"#ff3b2f", duration:0.1}}, {P("euro") + 0.15:.2f});')
J(f'tl.fromTo("#car11", {{x:0}}, {{x:14, duration:0.05, yoyo:true, repeat:5, immediateRender:false}}, {P("euro") + 0.15:.2f});')
FX.append(("perdida", P("euro") + 0.1))

# ================================================================== 12) LO QUE SÍ HARÍA (medalla de oro)
h12 = ('<div class="fondoFoto" id="ff12" style="background-image:url(assets/fotos/lucia_jason.jpg);background-position:60% 50%"></div><div class="velo"></div>'
       + medalla("med12", 1, "oro") + '<div class="tier oro" id="tier12"><small>Y AHORA…</small>LO QUE SÍ HARÍA</div>'
       + '<div class="rayo" id="ray12"></div>')
escena("e12", h12, F(12), F(13))
entra("#med12", F(12), "opacity:0, scale:0.2, rotation:-200", 0.5, "back.out(1.6)")
J(f'tl.fromTo("#med12 .disco", {{rotationY:0}}, {{rotationY:360, duration:0.8, ease:"power2.out", immediateRender:false}}, {F(12):.2f});')
golpe("#tier12", P("haria", 2))
J(f'tl.fromTo("#ray12", {{x:-900}}, {{x:900, duration:0.8, ease:"power2.inOut", immediateRender:false}}, {P("haria", 2) + 0.1:.2f});')
FX.append(("brillo", P("haria", 2)))

# ================================================================== 13) UNO: LA HISTORIA SIN PRISA (Lucía y Jason a pantalla completa)
h13 = ('<div class="fondoFoto" id="ff13" style="background-image:url(assets/fotos/lucia_jason.jpg);background-position:62% 50%"></div><div class="veloAbajo"></div>'
       + numero("num13", 1, 60, 1180) + chip("ch13", "MODO HISTORIA", 300, 1300, "#ffcf3a", "#1a0a2a", 44)
       + chip("sp13", "SIN PRISA", 300, 1390, "rgba(255,255,255,0.15)", "#ffffff", 40, "border:3px solid #fff")
       + '<div class="sello" id="se13">NO SE REPITE</div>')
escena("e13", h13, F(13), F(14), 1.0, 1.1)
golpe("#num13", P("uno") + 0.02, desde=3)
entra("#ch13", P("historia") - 0.1, "opacity:0, x:-400", 0.3, "power3.out")
entra("#sp13", P("prisa") - 0.1, "opacity:0, x:-400", 0.3, "power3.out")
golpe("#se13", P("repite") + 0.05, fx=False)
FX.append(("sello", P("repite") + 0.05))

# ================================================================== 14) DOS: VICE CITY DE NOCHE, CON LA RADIO Y SIN MAPA
barras = "".join(f'<i style="animation-delay:{i * 0.07:.2f}s"></i>' for i in range(14))
h14 = ('<div class="fondoFoto" id="ff14" style="background-image:url(assets/fotos/lucia_jason.jpg);background-position:12% 50%"></div>'
       '<div class="noche" id="noc14"></div>'
       + numero("num14", 2, 60, 1180)
       + '<div class="radio" id="rad14"><small>RADIO</small><b>VICE FM</b><div class="eq" id="eq14">' + "".join(f'<i class="eqb"></i>' for _ in range(14)) + '</div></div>'
       + '<div class="mapa" id="map14"><div class="punto"></div><div class="tacha" id="tac14"></div></div>'
       + chip("sm14", "SIN MISIONES", 300, 1300, "#7a5cff", "#ffffff", 44))
escena("e14", h14, F(14), F(15), 1.0, 1.08)
J(f'tl.fromTo("#ff14", {{x:0}}, {{x:-80, duration:{F(15) - F(14):.2f}, ease:"none", immediateRender:false}}, {F(14):.2f});')
golpe("#num14", P("dos") + 0.02, desde=3)
entra("#sm14", P("misiones") - 0.1, "opacity:0, x:-400", 0.3, "power3.out")
J(f'tl.set("#noc14", {{opacity:0}}, 0); tl.to("#noc14", {{opacity:1, duration:0.5}}, {P("noche") - 0.2:.2f});')
entra("#rad14", P("radio") - 0.15, "opacity:0, y:250", 0.35)
J(f'tl.fromTo("#eq14 .eqb", {{scaleY:0.2}}, {{scaleY:1, duration:0.18, yoyo:true, repeat:{int((F(15) - P("radio")) / 0.18)}, stagger:{{each:0.04, from:"random"}}, ease:"sine.inOut", immediateRender:false}}, {P("radio"):.2f});')
entra("#map14", P("mirar") - 0.4, "opacity:0, scale:0.3", 0.3)
J(f'tl.fromTo("#tac14", {{scaleX:0}}, {{scaleX:1, duration:0.2, ease:"power3.out", immediateRender:false}}, {P("mapa"):.2f}); tl.to("#map14", {{opacity:0.25, duration:0.3}}, {P("mapa") + 0.3:.2f});')
FX.append(("radio", P("radio")))

# ================================================================== 15) AHÍ ES DONDE GTA SE VUELVE GTA (logo + palabras que saltan)
h15 = (tarjeta("c15", "logo6.jpg", 90, 560, 900, 700, 0, borde="#ff4fa3")
       + '<div class="frase15">' + "".join(f'<span class="pw" id="pw{i}">{w}</span>' for i, w in enumerate(("GTA", "SE", "VUELVE", "GTA"))) + '</div>')
escena("e15", h15, F(15), F(16), 1.0, 1.06)
entra("#c15", F(15), "opacity:0, scale:1.4", 0.3, "power3.out")
for i, w in enumerate(("gta", "se", "vuelve", "gta")):
    t_ = P(w, 2 if (w == "gta" and i == 0) else (3 if w == "gta" else 1)) if w != "se" else P("se", 2)
    entra(f"#pw{i}", t_ - 0.05, "opacity:0, y:120, scale:1.6", 0.25)
golpe("#pw3", P("gta", 3), fx=True, desde=2)

# ================================================================== 16) TRES: SILENCIAR LAS REDES (GTA, Lucía, Jason)
filas = "".join(f'<div class="fila" id="fl{i}"><b>{w}</b><span class="mute"></span><div class="tg" id="sw{i}"><i></i></div></div>' for i, w in enumerate(("GTA", "Lucía", "Jason")))
h16 = (tarjeta("c16", "pareja.jpg", 130, 560, 820, 580, -2, borde="#9fd6ff")
       + numero("num16", 3, 830, 1440)
       + f'<div class="ajustes" id="aj16"><div class="ti">PALABRAS SILENCIADAS</div>{filas}</div>')
escena("e16", h16, F(16), F(17))
entra("#c16", F(16), "opacity:0, y:-300", 0.3)
golpe("#num16", P("tres", 2) + 0.02, desde=3)
J(f'tl.to("#c16", {{opacity:0.35, scale:0.92, duration:0.3}}, {P("redes") - 0.1:.2f});')
entra("#aj16", P("redes") - 0.1, "opacity:0, y:400", 0.35)
for i, w in enumerate(("gta", "lucia", "jason")):
    t_ = P(w, 4) if w == "gta" else P(w)
    J(f'tl.to("#sw{i}", {{background:"#2fd27a", duration:0.1}}, {t_:.2f}); tl.to("#sw{i} i", {{x:52, duration:0.15, ease:"back.out(2)"}}, {t_:.2f}); tl.to("#fl{i} b", {{opacity:0.35, textDecoration:"line-through", duration:0.1}}, {t_:.2f});')
    FX.append(("clic", t_))

# ================================================================== 17) CUATRO: LIBERAR ESPACIO (barra de almacenamiento) · borrar juegos a las 00:00
juegos = "".join(f'<div class="juego" id="jg{i}"><span>JUEGO {i + 1}</span><em>✕</em></div>' for i in range(4))
h17 = ('<div class="almac" id="al17"><div class="ti">ALMACENAMIENTO</div><div class="barraA"><i id="ba17"></i></div><div class="pc"><span id="pc17">97</span>% ocupado</div></div>'
       + numero("num17", 4, 60, 1180)
       + f'<div class="juegos" id="jgs17">{juegos}</div><div class="hora" id="ho17">00:00</div>')
escena("e17", h17, F(17), F(18))
golpe("#num17", P("cuatro") + 0.02, desde=3)
entra("#al17", F(17) + 0.1, "opacity:0, y:-300", 0.35)
J(f'tl.fromTo("#ba17", {{scaleX:0.97, background:"#ff3b2f"}}, {{scaleX:0.38, background:"#2fd27a", duration:1.2, ease:"power2.inOut", immediateRender:false}}, {P("espacio"):.2f});')
J(f'tl.fromTo("#pc17", {{innerText:97}}, {{innerText:38, snap:{{innerText:1}}, duration:1.2, ease:"power2.inOut", immediateRender:false}}, {P("espacio"):.2f});')
entra("#jgs17", P("nadie") - 0.1, "opacity:0, y:200", 0.3)
for i in range(4):
    t_ = P("borrar") + i * 0.22
    J(f'tl.to("#jg{i} em", {{opacity:1, scale:1, duration:0.1}}, {t_:.2f}); tl.to("#jg{i}", {{opacity:0.25, scale:0.85, duration:0.2}}, {t_ + 0.1:.2f});')
    FX.append(("clic", t_))
golpe("#ho17", P("doce"), fx=False)
FX.append(("reloj", P("doce")))

# ================================================================== 18) CINCO, LA SORPRESA: VICE CITY (2002) con efecto VHS
h18 = ('<div class="vhs" id="vhs18"><img id="vc18" src="assets/fotos/vicecity_logo.png"/><div class="lineas"></div><div class="rec">▶ PLAY</div></div>'
       + numero("num18", 5, 60, 1180) + chip("sor18", "LA SORPRESA", 300, 1300, "#ff4fa3", "#ffffff", 44)
       + '<div class="anyo" id="an18">2002</div>')
escena("e18", h18, F(18), F(19))
golpe("#num18", P("cinco") + 0.02, desde=3)
entra("#sor18", P("sorpresa") - 0.1, "opacity:0, x:-400", 0.3, "power3.out")
entra("#vhs18", P("vuelta") - 0.3, "opacity:0, scaleY:0.02", 0.3, "power3.out")
J(f'tl.fromTo("#vc18", {{x:-8, filter:"drop-shadow(6px 0 0 #ff2f6d) drop-shadow(-6px 0 0 #25f4ee)"}}, {{x:8, duration:0.06, yoyo:true, repeat:{int((F(19) - P("vuelta")) / 0.06)}, ease:"none", immediateRender:false}}, {P("vuelta"):.2f});')
golpe("#an18", P("2002"), fx=False)
FX.append(("vhs", P("vuelta") - 0.3))

# ================================================================== 19) DE DÓNDE VENIMOS → LA NUEVA CIUDAD PEGA EL DOBLE
h19 = (tarjeta("c19a", "vicecity_logo.png", 70, 640, 400, 440, -4, pos="50% 50%", borde="#ff4fa3")
       + tarjeta("c19b", "logo6.jpg", 590, 640, 420, 440, 4, pos="50% 50%", borde="#ffcf3a")
       + '<div class="flecha" id="fle19">➜</div><div class="lab" id="la19a" style="left:150px">2002</div><div class="lab" id="la19b" style="left:690px">2026</div>'
       + '<div class="x2" id="x2_19">×2</div>')
escena("e19", h19, F(19), F(20))
entra("#c19a, #la19a", F(19), "opacity:0, x:-400", 0.3)
entra("#fle19", P("venimos"), "opacity:0, x:-100", 0.3)
entra("#c19b, #la19b", P("nueva") - 0.2, "opacity:0, x:400", 0.3)
golpe("#x2_19", P("doble"))

# ================================================================== 20) LA PRIMERA SEMANA NO VUELVE… y CORTE SECO
h20 = ('<div class="portada" id="port20"><img src="assets/fotos/portada_ps5.jpg"/></div>'
       '<div class="final" id="fin20"><small>LA PRIMERA SEMANA</small>NO VUELVE</div>')
escena("e20", h20, F(20), DUR, 1.0, 1.12)
J(f'tl.fromTo("#port20", {{scale:1.15}}, {{scale:1, duration:0.4, ease:"power3.out", immediateRender:false}}, {F(20):.2f});')
golpe("#fin20", P("vuelve", 2))
J(f'tl.to("#port20 img", {{filter:"brightness(0.55)", duration:1.2}}, {P("desperdicia"):.2f});')
tc = FE(20) + 0.1
J(f'tl.set("#negroF", {{opacity:0}}, 0); tl.set("#negroF", {{opacity:1}}, {tc:.2f});')
FX.append(("final", tc - 0.05))

# ------------------------------------------------------------------ chip de nivel persistente (bajo los subtítulos)
NIV = (("NI LOCO", "#c8743a", F(3), F(7)), ("ME LO PENSARÍA", "#9aa6b6", F(8), F(12)), ("LO QUE SÍ HARÍA", "#e8a800", F(13), F(20)))
for i, (txt, col, a, b) in enumerate(NIV):
    OVR.append(f'<div class="nivel" id="niv{i}" style="--c:{col}"><i></i>{txt}</div>')
    J(f'tl.set("#niv{i}", {{opacity:0}}, 0); tl.fromTo("#niv{i}", {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:0.25, immediateRender:false}}, {a:.2f}); tl.to("#niv{i}", {{opacity:0, duration:0.15}}, {b - 0.05:.2f});')

# ------------------------------------------------------------------ subtítulos de siempre (arriba, palabra a palabra, recuadro azul en lo importante)
CLAVE = set(norm(w) for w in ["gta", "errores", "loco", "online", "trece", "reviente", "tiktok", "youtube", "final", "pensaria", "cara", "dorado",
                               "semana", "vacaciones", "euro", "si", "historia", "prisa", "noche", "radio", "mapa", "silenciar", "lucia", "jason",
                               "espacio", "doce", "sorpresa", "2002", "doble", "vuelve", "recupera"])
SUBS, chunks, cur = [], [], []
for p in T["palabras"]:
    cur.append(p)
    txt = " ".join(x["w"] for x in cur)
    if len(cur) >= 6 or len(txt) >= 30 or re.search(r"[.:;?!…»]$", p["w"]) or (re.search(r",$", p["w"]) and len(cur) >= 3):
        chunks.append(cur); cur = []
if cur:
    chunks.append(cur)
for k, ch in enumerate(chunks):
    st = ch[0]["ini"] - 0.05
    en = chunks[k + 1][0]["ini"] - 0.05 if k + 1 < len(chunks) else min(DUR, ch[-1]["fin"] + 0.6)
    spans = []
    for j, p in enumerate(ch):
        wid = f"w{k}_{j}"
        if norm(p["w"]) in CLAVE:
            spans.append(f'<span id="{wid}" class="sw key"><i class="hl"></i>{p["w"]}</span>')
            J(f'tl.to("#{wid} .hl", {{opacity:1, duration:0.06}}, {p["ini"]:.2f});')
        else:
            spans.append(f'<span id="{wid}" class="sw">{p["w"]}</span>')
        J(f'tl.to("#{wid}", {{color:"#ffffff", duration:0.06}}, {p["ini"]:.2f});')
    SUBS.append(f'<div id="sub{k}" class="clip sub" data-start="{max(0, st):.3f}" data-duration="{max(0.2, en - max(0, st)):.3f}" data-track-index="3">{" ".join(spans)}</div>')
# fondo vivo: rejilla synthwave que avanza y estrellas que titilan
J(f'tl.fromTo("#rejilla", {{backgroundPosition:"0px 0px"}}, {{backgroundPosition:"0px {int(DUR * 90)}px", duration:{DUR:.2f}, ease:"none", immediateRender:false}}, 0);')
J(f'tl.fromTo("#sol", {{scale:1}}, {{scale:1.06, duration:2.4, yoyo:true, repeat:{int(DUR / 2.4)}, ease:"sine.inOut", immediateRender:false}}, 0);')
r3 = random.Random(3)
for s_ in range(int(DUR / 0.08)):
    J(f'tl.set("#grano", {{backgroundPosition:"{r3.randint(0, 360)}px {r3.randint(0, 360)}px"}}, {s_ * 0.08:.2f});')

html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#0d0418}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;background:#0d0418}}
#root-shake{{position:absolute;inset:0}}
#fondo{{position:absolute;inset:0;background:linear-gradient(#0d0418 0%, #2a0b3d 38%, #7a1f63 60%, #ff6a4d 72%, #1a0628 72.2%, #12041f 100%)}}
#sol{{position:absolute;left:290px;top:820px;width:500px;height:500px;border-radius:50%;background:linear-gradient(#ffe36b, #ff8a3a 45%, #ff2f6d);opacity:0.55;
      -webkit-mask:repeating-linear-gradient(#000 0 34px, transparent 34px 46px);mask:repeating-linear-gradient(#000 0 34px, transparent 34px 46px)}}
#rejilla{{position:absolute;left:-600px;right:-600px;top:1386px;height:900px;transform:perspective(500px) rotateX(62deg);transform-origin:50% 0;
      background-image:linear-gradient(rgba(255,79,163,0.7) 2px, transparent 2px), linear-gradient(90deg, rgba(255,79,163,0.7) 2px, transparent 2px);background-size:90px 90px}}
#estrellas{{position:absolute;inset:0 0 50% 0;background-image:radial-gradient(2px 2px at 120px 160px,#fff,transparent),radial-gradient(2px 2px at 820px 260px,#fff,transparent),radial-gradient(1.5px 1.5px at 420px 620px,#fff,transparent),radial-gradient(2px 2px at 960px 700px,#fff,transparent),radial-gradient(1.5px 1.5px at 260px 900px,#fff,transparent),radial-gradient(2px 2px at 640px 120px,#fff,transparent);opacity:0.7}}
.esc{{position:absolute;inset:0;overflow:hidden}}
.cam{{position:absolute;inset:0;transform-origin:540px 1000px}}
.portada{{position:absolute;left:150px;top:540px;width:780px;height:972px;border:8px solid #fff;border-radius:18px;overflow:hidden;box-shadow:0 0 60px rgba(255,79,163,0.7)}}
.portada img{{width:100%;height:100%;object-fit:cover;display:block}}
.cruz{{position:absolute;left:340px;top:820px;width:400px;height:400px}}
.cruz i{{position:absolute;left:-40px;top:170px;width:480px;height:60px;background:#ff1f3d;border-radius:30px;box-shadow:0 0 40px rgba(255,31,61,0.9), 0 6px 0 #8a0014;transform:rotate(45deg)}}
.cruz i+i{{transform:rotate(-45deg)}}
.nohagas{{position:absolute;left:0;right:0;top:1560px;text-align:center;font:900 92px Inter;letter-spacing:-2px;color:#fff;text-shadow:0 6px 0 #8a0014, 0 0 40px rgba(255,31,61,0.8)}}
.nohagas .x{{display:inline-block;width:100px;height:100px;line-height:96px;border-radius:50%;background:#ff1f3d;font-size:70px;vertical-align:middle;margin-right:10px;text-shadow:none;box-shadow:0 0 30px rgba(255,31,61,0.9)}}
.card{{position:absolute;border:7px solid #fff;border-radius:18px;overflow:hidden;box-shadow:0 0 0 4px var(--b), 0 0 50px var(--b), 0 30px 60px rgba(0,0,0,0.55);background:#000}}
.card .ph{{position:absolute;inset:0;background-size:cover}}
.medal{{position:absolute;left:390px;top:600px;width:300px;height:420px}}
.medal .cinta{{position:absolute;left:95px;top:0;width:110px;height:190px;background:linear-gradient(90deg,#ff2f6d 0 30%,#7a1f63 30% 70%,#ff2f6d 70%);clip-path:polygon(0 0,100% 0,100% 100%,50% 85%,0 100%)}}
.medal .disco{{position:absolute;left:0;top:120px;width:300px;height:300px;border-radius:50%;background:radial-gradient(circle at 35% 30%, var(--a), var(--m) 55%, var(--o));
      box-shadow:0 0 0 12px rgba(255,255,255,0.25), 0 20px 50px rgba(0,0,0,0.5), inset 0 -12px 24px rgba(0,0,0,0.25);display:flex;align-items:center;justify-content:center}}
.medal .disco span{{font:900 190px Inter;color:#fff;text-shadow:0 6px 0 var(--o), 0 0 20px rgba(0,0,0,0.25)}}
.tier{{position:absolute;left:0;right:0;top:1060px;text-align:center;font:900 140px/1 Inter;letter-spacing:-5px;color:#fff;text-shadow:0 8px 0 #7a1f63, 0 0 50px rgba(255,79,163,0.8)}}
.tier small{{display:block;font:800 44px Inter;letter-spacing:10px;color:#ffcf3a;text-shadow:none;margin-bottom:14px}}
.tier.oro{{color:#ffe36b;text-shadow:0 8px 0 #a86a00, 0 0 60px rgba(255,200,58,0.9)}}
.chip{{position:absolute;padding:12px 28px;border-radius:50px;font-weight:900;letter-spacing:1px;white-space:nowrap;box-shadow:0 10px 30px rgba(0,0,0,0.4)}}
.carga{{position:absolute;left:150px;right:150px;top:1490px;padding:24px 34px;border-radius:24px;background:rgba(12,6,24,0.85);border:3px solid #7a5cff;color:#fff}}
.carga b{{font:900 52px Inter;letter-spacing:2px}} .carga span{{font:700 28px Inter;color:#b9a8ff;letter-spacing:4px}}
.barra{{height:26px;border-radius:13px;background:rgba(255,255,255,0.15);margin:14px 0 10px;overflow:hidden}} .barra i{{display:block;height:100%;background:linear-gradient(90deg,#7a5cff,#ff4fa3);transform-origin:0 50%}}
.contador{{position:absolute;left:0;right:0;top:1210px;text-align:center;color:#fff}}
.contador span{{font:900 230px/1 Inter;letter-spacing:-8px;color:#ffcf3a;text-shadow:0 10px 0 #a86a00}} .contador small{{display:block;font:800 46px Inter;letter-spacing:8px}}
.wasted{{position:absolute;left:0;right:0;top:770px;text-align:center;font:900 170px Inter;letter-spacing:4px;color:#ff2f2f;text-shadow:0 6px 0 #000, 0 0 40px rgba(0,0,0,0.8);transform:rotate(-4deg)}}
.killfeed{{position:absolute;right:60px;top:1500px;padding:12px 22px;border-radius:12px;background:rgba(0,0,0,0.75);border-left:8px solid #ff2f2f;color:#fff;font:600 30px Inter}} .killfeed b{{color:#ff6a6a}}
.movil{{position:absolute;left:290px;top:540px;width:500px;height:1000px;border-radius:60px;background:#0b0b10;border:14px solid #1d1d26;box-shadow:0 0 0 4px #ff4fa3, 0 0 60px rgba(255,79,163,0.6), 0 40px 80px rgba(0,0,0,0.6);overflow:hidden}}
.movil .pantalla{{position:absolute;inset:0;background-size:auto 100%}}
.movil .iconos{{position:absolute;right:22px;top:480px;display:flex;flex-direction:column;gap:30px}} .movil .iconos i{{width:70px;height:70px;border-radius:50%;background:rgba(255,255,255,0.85)}}
.movil .prog{{position:absolute;left:30px;right:30px;bottom:40px;height:10px;border-radius:5px;background:rgba(255,255,255,0.3);overflow:hidden}} .movil .prog i{{display:block;height:100%;background:#fff;transform-origin:0 50%}}
.movil .reloj{{position:absolute;left:30px;top:40px;padding:8px 20px;border-radius:30px;background:#ff2f6d;color:#fff;font:900 46px Inter;font-variant-numeric:tabular-nums}}
.movil .oscurece{{position:absolute;inset:0;background:#000;opacity:0}}
.vs{{position:absolute;left:40px;right:40px;top:1560px;display:flex;align-items:center;justify-content:center;gap:24px;color:#fff;text-align:center}}
.vs div{{padding:14px 26px;border-radius:20px;background:rgba(12,6,24,0.85);border:3px solid #ffcf3a}} .vs b{{display:block;font:900 54px Inter}} .vs small{{font:700 24px Inter;letter-spacing:3px;color:#ffcf3a}}
.vs em{{font:900 italic 60px Inter;color:#ff4fa3}}
.spoiler{{position:absolute;left:0;right:0;top:960px;text-align:center;font:900 150px Inter;color:#fff;letter-spacing:4px}}
.spoiler{{-webkit-text-stroke:0;transform:rotate(-12deg)}} .spoiler::before{{content:"";position:absolute;left:120px;right:120px;top:10px;bottom:10px;background:#ff1f3d;z-index:-1;border-radius:20px;box-shadow:0 0 50px rgba(255,31,61,0.9)}}
.precio{{position:absolute;left:640px;top:600px;padding:22px 30px;border-radius:20px;background:#ffcf3a;color:#1a0a2a;text-align:center;box-shadow:0 20px 40px rgba(0,0,0,0.45);transform-origin:50% 0}}
.precio span{{display:block;font:900 96px/1 Inter}} .precio small{{font:900 22px Inter;letter-spacing:2px}}
.dorado{{position:absolute;inset:0;background:linear-gradient(135deg,#ffe36b,#c8901a);mix-blend-mode:color;opacity:0}}
.brillo,.rayo{{position:absolute;top:-200px;bottom:-200px;width:180px;left:50%;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.75),transparent);transform:rotate(20deg)}}
.semana{{position:absolute;left:90px;right:90px;top:1440px;display:flex;gap:12px;justify-content:center}}
.dia{{width:118px;height:130px;border-radius:18px;background:rgba(255,255,255,0.12);border:3px solid rgba(255,255,255,0.6);color:#fff;text-align:center;padding-top:8px}}
.dia small{{display:block;font:800 30px Inter}} .dia b{{display:block;font:900 54px Inter;opacity:0}}
.unaSem{{position:absolute;left:0;right:0;top:1610px;text-align:center;font:900 76px Inter;color:#2fd27a;text-shadow:0 6px 0 #0a5a2e}}
.calendario{{position:absolute;left:190px;top:600px;width:700px;border-radius:28px;background:#fff;overflow:hidden;box-shadow:0 30px 60px rgba(0,0,0,0.5)}}
.calendario .cab{{background:#ff2f6d;color:#fff;font:900 60px Inter;text-align:center;padding:20px;letter-spacing:4px}}
.calendario .rej{{display:flex;gap:12px;padding:30px;justify-content:center}} .cd{{width:80px;height:80px;border-radius:14px;background:#f1eef6;color:#3a2a4a;font:900 40px/80px Inter;text-align:center}}
.bateria{{position:absolute;left:650px;top:1120px;width:320px;height:140px;border:10px solid #fff;border-radius:26px;padding:10px}} .bateria::after{{content:"";position:absolute;right:-30px;top:36px;width:18px;height:50px;background:#fff;border-radius:0 8px 8px 0}}
.bateria .llena{{height:100%;border-radius:10px;background:#2fd27a;transform-origin:0 50%}} .bateria span em{{font-style:normal}} .bateria span{{position:absolute;left:0;right:0;top:120px;text-align:center;font:900 50px Inter;color:#fff}}
.cartera{{position:absolute;left:620px;top:1380px;width:380px;padding:20px;border-radius:24px;background:rgba(12,6,24,0.88);border:3px solid #ff4fa3;text-align:center;color:#fff}}
.cartera small{{font:800 26px Inter;letter-spacing:6px;color:#ff9ac8}} .cartera b{{display:block;font:900 82px Inter;font-variant-numeric:tabular-nums}}
.fondoFoto{{position:absolute;inset:-40px;background-size:cover}}
.velo{{position:absolute;inset:0;background:linear-gradient(rgba(13,4,24,0.55), rgba(13,4,24,0.75))}}
.veloAbajo{{position:absolute;inset:0;background:linear-gradient(rgba(13,4,24,0.35) 0%, rgba(13,4,24,0) 35%, rgba(13,4,24,0) 55%, rgba(13,4,24,0.85) 85%)}}
.noche{{position:absolute;inset:0;background:linear-gradient(rgba(10,10,60,0.75), rgba(40,10,80,0.55));mix-blend-mode:multiply}}
.numero{{position:absolute;font:900 300px/1 Inter;color:transparent;-webkit-text-stroke:8px #ffcf3a;text-shadow:0 0 40px rgba(255,200,58,0.6)}}
.sello{{position:absolute;left:250px;top:1500px;padding:16px 34px;border:8px solid #ff2f6d;border-radius:16px;color:#ff2f6d;font:900 70px Inter;letter-spacing:3px;transform:rotate(-8deg);background:rgba(255,255,255,0.92)}}
.radio{{position:absolute;left:130px;right:130px;top:1460px;padding:22px 30px;border-radius:26px;background:rgba(12,6,24,0.85);border:3px solid #25f4ee;color:#fff;display:flex;align-items:center;gap:24px}}
.radio small{{font:800 24px Inter;letter-spacing:4px;color:#25f4ee}} .radio b{{font:900 46px Inter}}
.eq{{display:flex;gap:6px;align-items:flex-end;height:80px;margin-left:auto}} .eq i{{width:12px;height:80px;background:linear-gradient(#ff4fa3,#25f4ee);border-radius:4px;transform-origin:50% 100%}}
.mapa{{position:absolute;right:60px;top:560px;width:220px;height:220px;border-radius:50%;border:8px solid #fff;background:radial-gradient(#3f7a5a,#1f3a2e);box-shadow:0 0 30px rgba(0,0,0,0.5);overflow:hidden}}
.mapa .punto{{position:absolute;left:96px;top:96px;width:28px;height:28px;border-radius:50%;background:#ffcf3a;box-shadow:0 0 12px #ffcf3a}}
.mapa .tacha{{position:absolute;left:-20px;top:96px;width:260px;height:26px;background:#ff1f3d;transform:rotate(-45deg);transform-origin:50% 50%}}
.frase15{{position:absolute;left:30px;right:30px;top:1330px;text-align:center}} .pw{{display:inline-block;margin:0 10px;font:900 120px Inter;letter-spacing:-3px;color:#fff;text-shadow:0 8px 0 #7a1f63}}
#pw3{{color:#ffcf3a;text-shadow:0 8px 0 #a86a00, 0 0 40px rgba(255,200,58,0.8)}}
.ajustes{{position:absolute;left:110px;right:110px;top:1000px;padding:30px;border-radius:30px;background:#ffffff;box-shadow:0 30px 60px rgba(0,0,0,0.5)}}
.ajustes .ti{{font:900 34px Inter;letter-spacing:3px;color:#7a5cff;margin-bottom:16px}}
.fila{{display:flex;align-items:center;gap:20px;padding:16px 0;border-top:2px solid #eee}} .fila b{{font:900 56px Inter;color:#1a0a2a;flex:1}}
.fila .mute{{width:44px;height:44px;border-radius:50%;background:#ff2f6d}}
.tg{{width:110px;height:58px;border-radius:29px;background:#cfcfd8;position:relative}} .tg i{{position:absolute;left:5px;top:5px;width:48px;height:48px;border-radius:50%;background:#fff;box-shadow:0 2px 6px rgba(0,0,0,0.3)}}
.almac{{position:absolute;left:110px;right:110px;top:600px;padding:34px;border-radius:30px;background:rgba(12,6,24,0.9);border:3px solid #25f4ee;color:#fff}}
.almac .ti{{font:900 40px Inter;letter-spacing:4px;color:#25f4ee}} .barraA{{height:60px;border-radius:30px;background:rgba(255,255,255,0.15);margin:22px 0;overflow:hidden}} .barraA i{{display:block;height:100%;border-radius:30px;transform-origin:0 50%}}
.almac .pc{{font:900 64px Inter}}
.juegos{{position:absolute;left:300px;right:80px;top:1220px;display:grid;grid-template-columns:1fr 1fr;gap:18px}}
.juego{{position:relative;height:140px;border-radius:20px;background:linear-gradient(135deg,#3a2a6a,#7a5cff);color:#fff;font:900 34px Inter;display:flex;align-items:center;justify-content:center}}
.juego em{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font:900 110px Inter;font-style:normal;color:#ff1f3d;opacity:0;transform:scale(2)}}
.hora{{position:absolute;left:0;right:0;top:1580px;text-align:center;font:900 130px Inter;color:#ff2f6d;font-variant-numeric:tabular-nums;text-shadow:0 0 40px rgba(255,47,109,0.8)}}
.vhs{{position:absolute;left:140px;top:560px;width:800px;height:640px;border-radius:24px;background:#0b0b18;border:8px solid #fff;overflow:hidden;box-shadow:0 0 60px rgba(255,79,163,0.6);display:flex;align-items:center;justify-content:center}}
.vhs img{{height:560px}} .vhs .lineas{{position:absolute;inset:0;background:repeating-linear-gradient(rgba(0,0,0,0.25) 0 3px, transparent 3px 7px)}}
.vhs .rec{{position:absolute;left:24px;top:20px;font:900 34px Inter;color:#fff;letter-spacing:2px}}
.anyo{{position:absolute;left:0;right:0;top:1440px;text-align:center;font:900 italic 210px Inter;letter-spacing:-6px;background:linear-gradient(#ffffff,#ff9ac8 45%,#7a1f63 50%,#ff4fa3);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 8px 0 #2a0b3d)}}
.flecha{{position:absolute;left:470px;top:780px;font:900 130px Inter;color:#ffcf3a}}
.lab{{position:absolute;top:1120px;width:240px;text-align:center;font:900 80px Inter;color:#fff}}
.x2{{position:absolute;left:0;right:0;top:1310px;text-align:center;font:900 260px Inter;color:#ffcf3a;text-shadow:0 12px 0 #a86a00, 0 0 60px rgba(255,200,58,0.8)}}
.final{{position:absolute;left:0;right:0;top:1500px;text-align:center;font:900 132px/1 Inter;letter-spacing:-4px;color:#fff;text-shadow:0 8px 0 #8a0014, 0 0 50px rgba(255,31,61,0.8)}}
.final small{{display:block;font:800 50px Inter;letter-spacing:8px;color:#ffcf3a;text-shadow:0 4px 0 #000;margin-bottom:10px}}
.nivel{{position:absolute;left:0;right:0;top:478px;text-align:center;z-index:40;font:900 30px Inter;letter-spacing:4px;color:#fff}}
.nivel{{display:flex;justify-content:center;align-items:center;gap:12px}} .nivel i{{width:26px;height:26px;border-radius:50%;background:var(--c);box-shadow:0 0 12px var(--c)}}
#flash{{position:absolute;inset:0;z-index:58;opacity:0;pointer-events:none}}
#negroF{{position:absolute;inset:0;z-index:70;background:#000;pointer-events:none}}
#grano{{position:absolute;inset:0;z-index:57;pointer-events:none;opacity:0.06;background:url(assets/grano.png);mix-blend-mode:overlay}}
#vineta{{position:absolute;inset:0;z-index:56;pointer-events:none;background:radial-gradient(110% 80% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55))}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:540px;z-index:55;pointer-events:none;background:linear-gradient(rgba(6,2,12,0.85), rgba(6,2,12,0))}}
#marca{{position:absolute;left:0;right:0;top:1775px;text-align:center;font:700 28px Inter;color:#ffffff;opacity:0.32;pointer-events:none;z-index:61}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 62px Inter;color:rgba(255,255,255,0.4);line-height:1.22;text-shadow:0 3px 12px rgba(0,0,0,0.6)}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:3px solid #4ea3ff;border-radius:6px;background:rgba(78,163,255,0.18);opacity:0}}
@keyframes nada{{}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
 <div id="root-shake">
  <div id="fondo"></div><div id="estrellas"></div><div id="sol"></div><div id="rejilla"></div>
  {"".join(ESC)}
 </div>
  <div id="topsombra"></div>
  {"".join(OVR)}
  <div id="vineta"></div><div id="grano"></div><div id="flash"></div><div id="negroF"></div>
  <div id="marca">@mundo.supuesto</div>
  <div id="subs" data-layout-allow-overlap>{"".join(SUBS)}</div>
  <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tl)}
tl.to({{}}, {{duration:0.01}}, {DUR - 0.01});
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>"""
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump(FX, open(os.path.join(BASE, "efectos.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones")

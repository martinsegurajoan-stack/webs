#!/usr/bin/env python3
"""«¿Y si dejaras de hacer el vago y te pusieras a trabajar?» — tipografía cinética + interfaces animadas (sin personajes).
Cada frase es una escena que entra y sale con barrido rápido (whip), una sola familia de easing (expo), cámara con
punch-in en los momentos clave y sacudida en los golpes. Insultos censurados con pitido (bip.py) y «#@%!» en pantalla.
  python3 gen.py → index.html (+ censura.json para bip.py)"""
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
def PF(word, n=1):
    k = 0
    for w, a, b in WORDS:
        if w == norm(word):
            k += 1
            if k == n:
                return b
    raise KeyError(word)
def F(n): return FR[n - 1]["ini"]
def FE(n): return FR[n - 1]["fin"]
tl, SC = [], []
def J(s): tl.append(s)
rr = random.Random(4)

# ------------------------------------------------------------------ censura (pitido + «#@%!» en subtítulos)
CENS = ["gilipollas", "puto", "mierda"]
cens = []
for p in T["palabras"]:
    if norm(p["w"]) in CENS:
        cens.append([p["ini"] - 0.03, p["fin"] + 0.04])
        p["w"] = re.sub(r"[A-Za-zÁÉÍÓÚáéíóúñÑ]+", "#@%!", p["w"])
json.dump(cens, open(os.path.join(BASE, "censura.json"), "w"))

# ------------------------------------------------------------------ helpers de escena y cámara
EASE_IN, EASE_OUT = "expo.out", "expo.in"
def escena(sid, html, t0, t1, dentro="x", fuera="x", cls=""):
    """Escena a pantalla completa: entra y sale con barrido (whip) + desenfoque."""
    SC.append(f'<div class="sc {cls}" id="{sid}">{html}</div>')
    if dentro == "n":
        J(f'tl.set("#{sid}", {{autoAlpha:1}}, 0);')
        J(f'tl.to("#{sid}", {{x:-900, filter:"blur(18px)", duration:0.28, ease:"{EASE_OUT}"}}, {t1 - 0.28:.2f}); tl.set("#{sid}", {{autoAlpha:0}}, {t1:.2f});')
        return
    d0 = {"x": "x:900", "y": "y:1400", "z": "scale:1.6", "f": "opacity:0"}[dentro]
    d1 = {"x": "x:-900", "y": "y:-1400", "z": "scale:0.6", "f": "opacity:0"}[fuera]
    J(f'tl.set("#{sid}", {{autoAlpha:0}}, 0);')
    J(f'tl.fromTo("#{sid}", {{autoAlpha:1, {d0}, filter:"blur(18px)"}}, {{x:0, y:0, scale:1, opacity:1, filter:"blur(0px)", duration:0.38, ease:"{EASE_IN}", immediateRender:false}}, {t0:.2f});')
    J(f'tl.to("#{sid}", {{{d1}, filter:"blur(18px)", duration:0.28, ease:"{EASE_OUT}"}}, {t1 - 0.28:.2f}); tl.set("#{sid}", {{autoAlpha:0}}, {t1:.2f});')
def at(sel, t, d=0.45, ease=EASE_IN, desde=None, **kv):
    props = ", ".join(f"{k}:{v}" for k, v in kv.items())
    if desde:
        J(f'tl.fromTo("{sel}", {{{desde}}}, {{{props}, duration:{d}, ease:"{ease}", immediateRender:false}}, {t:.2f});')
    else:
        J(f'tl.to("{sel}", {{{props}, duration:{d}, ease:"{ease}"}}, {t:.2f});')
def pop(sel, t, d=0.45):
    J(f'tl.set("{sel}", {{autoAlpha:0}}, 0); tl.fromTo("{sel}", {{autoAlpha:1, scale:0.3, rotation:-6}}, {{scale:1, rotation:0, duration:{d}, ease:"back.out(2.2)", immediateRender:false}}, {t:.2f});')
def slam(sel, t, d=0.32):
    J(f'tl.set("{sel}", {{autoAlpha:0}}, 0); tl.fromTo("{sel}", {{autoAlpha:1, scale:2.6, filter:"blur(10px)"}}, {{scale:1, filter:"blur(0px)", duration:{d}, ease:"expo.out", immediateRender:false}}, {t:.2f});')
    shake(t + d * 0.6, 22)
def tacha(sel, t):
    J(f'tl.set("{sel}", {{scaleX:0, transformOrigin:"0% 50%"}}, 0); tl.to("{sel}", {{scaleX:1, duration:0.25, ease:"expo.out"}}, {t:.2f});')
def shake(t, amp=16):
    seq = [(amp, -amp * 0.6), (-amp * 0.8, amp * 0.5), (amp * 0.5, amp * 0.4), (-amp * 0.3, -amp * 0.2), (0, 0)]
    for k, (x, y) in enumerate(seq):
        J(f'tl.to("#shake", {{x:{x:.1f}, y:{y:.1f}, duration:0.045, ease:"none"}}, {t + k * 0.045:.3f});')
def punch(t, k=1.12, hold=0.9):
    J(f'tl.to("#cam", {{scale:{k}, duration:0.35, ease:"expo.out"}}, {t:.2f}); tl.to("#cam", {{scale:1, duration:0.5, ease:"expo.inOut"}}, {t + hold:.2f});')
def contador(sel, v0, v1, t, d, dec=0, suf="", pre=""):
    J(f'(() => {{ const o = {{v:{v0}}}; tl.to(o, {{v:{v1}, duration:{d:.2f}, ease:"expo.out", onUpdate:() => {{ document.querySelector("{sel}").textContent = "{pre}" + fmt(o.v, {dec}) + "{suf}"; }}}}, {t:.2f}); }})();')
def fondo(t, c1, c2, d=0.6):
    J(f'tl.to("#b1", {{backgroundColor:"{c1}", duration:{d}}}, {t:.2f}); tl.to("#b2", {{backgroundColor:"{c2}", duration:{d}}}, {t:.2f});')
CENSOR = '<div class="cens"><span>#@%!</span></div>'

# ================================================================== 1) GANCHO (frame 0 ya con texto)
h = ('<div class="mega" id="h1">TÚ.</div>'
     '<div class="stamp red" id="h2">VAGO</div>'
     '<div class="dedo" id="h3">👉</div>'
     '<div class="card glass" id="h4"><small>TIEMPO EN EL SOFÁ DE TUS PADRES</small><b><span id="n25">0</span> años</b>'
     '<div class="bar"><i id="barra"></i></div><em><span id="nh">0</span> horas</em></div>')
escena("s1", h, 0, F(2) + 0.1, "n")
J('tl.set("#h1", {autoAlpha:1, scale:1}, 0);')
at("#h1", 0.0, 0.6, "expo.out", desde="scale:1.35, opacity:1", scale=1)
at("#h1", P("vago") - 0.2, 0.3, y=-260, scale=0.55)
slam("#h2", P("vago") - 0.05); punch(P("vago") - 0.05, 1.1, 0.7)
pop("#h3", P("tu") - 0.1); at("#h3", P("tu"), 0.5, "expo.out", x=-40, yoyo="true", repeat=3)
J(f'tl.to(["#h2", "#h3"], {{autoAlpha:0, duration:0.25}}, {P("veinticinco") - 0.4:.2f});')
pop("#h4", P("veinticinco") - 0.3)
contador("#n25", 0, 25, P("veinticinco") - 0.2, 1.2)
contador("#nh", 0, 219000, P("veinticinco"), 2.0)
at("#barra", P("sofa") - 0.4, 1.6, "expo.out", desde="width:'0%'", width="'100%'")
fondo(0, "#3a2b5c", "#1f2a44")

# ================================================================== 2) LinkedIn: un currículum… y te llaman
FEED = "".join(f'<div class="oferta"><i style="background:{c}"></i><div><b>{t}</b><small>{e} · {l}</small></div><span class="sol" id="sol{k}">Solicitar<em>Enviada ✓</em></span></div>'
               for k, (t, e, l, c) in enumerate((("Auxiliar administrativo", "Grupo Norte", "Madrid", "#0a66c2"), ("Dependiente/a", "Moda Urbana", "Valencia", "#e85d75"),
                                                 ("Mozo de almacén", "LogiExpress", "Sevilla", "#f4a261"), ("Teleoperador/a", "CallPlus", "Remoto", "#2a9d8f"))))
TEL = (f'<div class="movil" id="mv"><div class="notch"></div><div class="app"><div class="apphead"><b>in</b><span>Empleos</span></div><div id="feed">{FEED}</div>'
       '<div class="toast" id="toastCV">✓ Solicitud enviada <b>(1)</b></div></div>'
       '<div class="llamada" id="call"><small>LLAMADA ENTRANTE</small><b>Recursos Humanos</b><em>Grupo Norte</em><div class="btns"><i class="no"></i><i class="si" id="si"></i></div></div></div>')
escena("s2", TEL + '<div class="kick" id="k2">UN MARTES CUALQUIERA</div>', F(2) - 0.1, F(3) + 0.05)
at("#k2", F(2) + 0.1, 0.4, desde="opacity:0, y:30", opacity=1, y=0)
at("#feed", P("linkedin") + 0.2, 1.4, "power2.inOut", y=-190)
J(f'tl.to("#sol0", {{scale:0.85, duration:0.12, yoyo:true, repeat:1}}, {P("curriculum") + 0.1:.2f}); tl.to("#sol0 em", {{opacity:1, duration:0.15}}, {P("curriculum") + 0.3:.2f});')
pop("#toastCV", P("uno") - 0.1)
J(f'tl.set("#call", {{autoAlpha:0}}, 0); tl.fromTo("#call", {{autoAlpha:1, y:900}}, {{y:0, duration:0.4, ease:"expo.out", immediateRender:false}}, {P("llaman") - 0.3:.2f});')
J(f'tl.to("#mv", {{rotation:2.5, duration:0.05, yoyo:true, repeat:13, ease:"none"}}, {P("llaman"):.2f});')
J(f'tl.to("#si", {{scale:1.25, duration:0.25, yoyo:true, repeat:5, ease:"sine.inOut"}}, {P("llaman"):.2f});')
fondo(F(2), "#0a3d73", "#0b1f3a")

# ================================================================== 3) Te han cogido… gilipollas
CONF = "".join(f'<i class="cf" style="left:{rr.randint(80, 1000)}px;background:{rr.choice(["#ffd166", "#06d6a0", "#ef476f", "#118ab2", "#ffffff"])};width:{rr.randint(10, 18)}px;height:{rr.randint(18, 30)}px"></i>' for _ in range(70))
s3 = (f'<div class="confeti">{CONF}</div><div class="mail" id="mail"><small>Asunto: Oferta de empleo</small><b>¡Enhorabuena!</b><em>Has sido seleccionado para el puesto.</em></div>'
      '<div class="mega green" id="cog">TE HAN COGIDO</div><div class="mid" id="ati">A TI.</div>'
      '<div class="lav" id="lav"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 220" width="300" height="330"><rect x="10" y="10" width="180" height="200" rx="18" fill="none" stroke="#fff" stroke-width="8"/><path d="M10,52 H190" stroke="#fff" stroke-width="6"/><circle cx="100" cy="132" r="54" fill="none" stroke="#fff" stroke-width="8"/><circle class="tambor" cx="100" cy="132" r="34" fill="none" stroke="#7fd3ff" stroke-width="6" stroke-dasharray="20 14"/><circle cx="40" cy="31" r="7" fill="#fff"/><circle cx="62" cy="31" r="7" fill="#fff"/></svg><div class="q">???</div></div>'
      + CENSOR.replace('class="cens"', 'class="cens" id="c3"'))
escena("s3", s3, F(3) - 0.05, F(4) + 0.05, "z")
pop("#mail", F(3) - 0.05)
J(f'tl.fromTo(".cf", {{y:-200, rotation:0}}, {{y:2200, rotation:720, duration:2.6, ease:"power1.in", stagger:{{each:0.01, from:"random"}}, immediateRender:false}}, {F(3):.2f});')
J(f'tl.to("#mail", {{autoAlpha:0, scale:0.8, duration:0.25}}, {P("ti") - 0.4:.2f});')
slam("#cog", F(3) + 0.1)
J(f'tl.to("#cog", {{y:-380, scale:0.6, duration:0.4, ease:"expo.inOut"}}, {P("ti") - 0.3:.2f});')
slam("#ati", P("ti") - 0.15)
J(f'tl.to("#ati", {{autoAlpha:0, duration:0.2}}, {P("lavadora") - 0.6:.2f});')
pop("#lav", P("lavadora") - 0.5)
J(f'tl.to(".tambor", {{rotation:360, svgOrigin:"100 132", duration:1.2, ease:"none", repeat:1}}, {P("lavadora") - 0.4:.2f});')
slam("#c3", P("gilipollas") - 0.05, 0.22); punch(P("gilipollas") - 0.05, 1.15, 0.6)
fondo(F(3), "#0f5132", "#0b2a1c")

# ================================================================== 4) 25 años para lo que otros hacen a los 18… enhorabuena, campeón
s4 = ('<div class="kick">EDAD DEL PRIMER TRABAJO</div><div class="barras"><div class="br"><b>Otros</b><div class="tr"><i id="b18"></i></div><span>18</span></div>'
      '<div class="br tu"><b>Tú</b><div class="tr"><i id="b25"></i></div><span id="n25b">18</span></div></div>'
      '<div class="clap" id="clap">👏</div><div class="mid gold" id="camp">«CAMPEÓN»</div>')
escena("s4", s4, F(4) - 0.05, F(5) + 0.05)
at("#b18", F(4) + 0.3, 0.9, "expo.out", desde="width:'0%'", width="'62%'")
at("#b25", P("dieciocho"), 1.0, "expo.out", desde="width:'0%'", width="'100%'")
contador("#n25b", 18, 25, P("dieciocho"), 1.0)
pop("#clap", P("enhorabuena") - 0.2)
J(f'tl.to("#clap", {{scale:1.25, duration:0.12, yoyo:true, repeat:9, ease:"sine.inOut"}}, {P("enhorabuena"):.2f});')
slam("#camp", P("campeon") - 0.1)
fondo(F(4), "#5c4b16", "#2a2410")

# ================================================================== 5) el primer mes: madrugar, tráfico, jefe… nómina
COCHES = "".join(f'<div class="coche" style="top:{k * 70}px;left:{(k * 137) % 300}px;background:{c}"><i></i><i></i></div>'
                 for k, c in enumerate(["#e63946", "#457b9d", "#f1faee", "#ffb703", "#8d99ae", "#e76f51"]))
s5 = ('<div class="alarma" id="alarma"><b>06:30</b><small>Despertador</small></div>'
      f'<div class="atasco" id="atasco"><div class="carril">{COCHES}</div><div class="cap">Atasco · +45 min</div></div>'
      '<div class="chat" id="jefe"><small>Jefe</small><p>¿Otra vez tarde? 🙄</p></div>'
      '<div class="cal" id="cal"><small>NOVIEMBRE</small><b>1</b></div>'
      '<div class="nomina" id="nom"><small>NÓMINA</small><b><span id="nsal">0</span> €</b><em>Líquido a percibir</em><div class="st">INGRESADO</div></div>'
      '<div class="kick" id="k5">EL PRIMER MES DUELE</div>')
escena("s5", s5, F(5) - 0.05, F(6) + 0.05)
at("#k5", F(5), 0.4, desde="opacity:0, y:30", opacity=1, y=0)
pop("#alarma", P("madrugar") - 0.3)
J(f'tl.to("#alarma", {{rotation:6, duration:0.04, yoyo:true, repeat:15, ease:"none"}}, {P("madrugar"):.2f}); tl.to("#alarma", {{autoAlpha:0, y:-60, duration:0.25}}, {P("trafico") - 0.3:.2f});')
pop("#atasco", P("trafico") - 0.3)
J(f'tl.to(".coche", {{x:"+=18", duration:0.9, ease:"power1.inOut", stagger:0.05}}, {P("trafico"):.2f}); tl.to("#atasco", {{autoAlpha:0, y:-60, duration:0.25}}, {P("jefe") - 0.3:.2f});')
pop("#jefe", P("jefe") - 0.25)
J(f'tl.to(["#jefe", "#k5"], {{autoAlpha:0, duration:0.25}}, {P("uno", 2) - 0.6:.2f});')
J(f'tl.set("#cal", {{autoAlpha:0}}, 0); tl.fromTo("#cal", {{autoAlpha:1, rotationX:-90, transformPerspective:800}}, {{rotationX:0, duration:0.5, ease:"expo.out", immediateRender:false}}, {P("uno", 2) - 0.5:.2f});')
J(f'tl.to("#cal", {{autoAlpha:0, scale:0.7, duration:0.25}}, {P("nomina") - 0.5:.2f});')
pop("#nom", P("nomina") - 0.4)
contador("#nsal", 0, 1350, P("nomina") - 0.2, 1.4, 0)
slam("#nom .st", P("nomina") + 1.0)
fondo(F(5), "#1e3a5f", "#0d1b2a")

# ================================================================== 6) el dinero no aparece por arte de magia
s6 = ('<div class="banco"><div class="cta" id="ctaP"><small>Cuenta de papá y mamá</small><b>— transferencias a tu nombre: 0</b></div>'
      '<div class="flujo"><div class="emp">🏢 Tu empresa</div><div class="mon" id="mon">€</div></div>'
      '<div class="cta yo" id="ctaY"><small>TU cuenta</small><b><span id="nyo">0,00</span> €</b></div></div>'
      '<div class="magia" id="mag">✨ MAGIA ✨<i class="lin"></i></div>')
escena("s6", s6, F(6) - 0.05, F(7) + 0.05)
pop("#ctaY", F(6) + 0.1)
J(f'tl.fromTo("#mon", {{y:-120, opacity:0}}, {{y:220, opacity:1, duration:0.6, ease:"expo.in", repeat:2, immediateRender:false}}, {F(6) + 0.4:.2f});')
contador("#nyo", 0, 1350, F(6) + 0.9, 1.6, 2)
pop("#mag", P("magia") - 0.6); tacha("#mag .lin", P("magia") + 0.1)
fondo(F(6), "#14532d", "#052e16")

# ================================================================== 7) zapatillas, cenas, alquiler… ya no pides 20 € a tu madre
ITEMS = (("👟", "Zapatillas", "119,99 €", "zapatillas"), ("🍝", "Cena fuera", "42,50 €", "cenas"), ("🏠", "Tu alquiler", "650,00 €", "alquiler"))
s7 = '<div class="carrito">' + "".join(f'<div class="item" id="it{k}"><i>{e}</i><b>{n}</b><span>{p}</span><em class="ok">✓</em></div>' for k, (e, n, p, w) in enumerate(ITEMS)) + '</div>'
s7 += '<div class="bizum" id="biz"><small>Bizum a Mamá</small><b>Pedir 20 €</b><i class="lin"></i><div class="st2">YA NO HACE FALTA</div></div>'
escena("s7", s7, F(7) - 0.05, F(8) + 0.05)
for k, (e, n, p, w) in enumerate(ITEMS):
    pop(f"#it{k}", P(w) - 0.3)
    J(f'tl.set("#it{k} .ok", {{autoAlpha:0}}, 0); tl.fromTo("#it{k} .ok", {{autoAlpha:1, scale:0}}, {{scale:1, duration:0.3, ease:"back.out(3)", immediateRender:false}}, {P(w) + 0.25:.2f});')
J(f'tl.to(".carrito", {{y:-90, scale:0.82, duration:0.5, ease:"expo.inOut"}}, {P("veinte") - 0.9:.2f});')
pop("#biz", P("veinte") - 0.6); tacha("#biz .lin", P("veinte") + 0.3); slam("#biz .st2", FE(7) - 0.6)
fondo(F(7), "#4c1d95", "#1e1b4b")

# ================================================================== 8) no eres un puto parásito. Eres un adulto. Casi.
s8 = ('<div class="mid" id="noeres">NO ERES UN</div><div class="mega red" id="par">PARÁSITO<i class="lin"></i></div>'
      + CENSOR.replace('class="cens"', 'class="cens" id="c8"') +
      '<div class="stamp green" id="adulto">ADULTO ✓</div><div class="casi" id="casi">casi.</div>')
escena("s8", s8, F(8) - 0.05, F(9) + 0.02, "x", "f")
pop("#noeres", F(8) + 0.4)
slam("#c8", P("puto") - 0.05, 0.22)
slam("#par", P("parasito") - 0.1); tacha("#par .lin", P("parasito") + 0.6)
J(f'tl.to(["#noeres", "#par", "#c8"], {{autoAlpha:0, y:-80, duration:0.25}}, {P("adulto") - 0.4:.2f});')
slam("#adulto", P("adulto") - 0.15); punch(P("adulto") - 0.15, 1.1, 0.6)
J(f'tl.set("#casi", {{autoAlpha:0}}, 0); tl.fromTo("#casi", {{autoAlpha:1, y:-300, rotation:-30}}, {{y:0, rotation:-8, duration:0.6, ease:"bounce.out", immediateRender:false}}, {P("casi") - 0.15:.2f}); tl.to("#adulto", {{rotation:-6, y:20, duration:0.4}}, {P("casi"):.2f});')
fondo(F(8), "#7f1d1d", "#2b0a0a")

# ================================================================== 9) Y entonces… sale el GTA 6  (apagón + neón)
s9 = ('<div class="neon" id="gta"><small>YA DISPONIBLE</small><b>GTA VI</b><div class="sol"></div><div class="palmeras"></div></div>'
      '<div class="glitch" id="gl"></div>')
J(f'tl.to("#negro", {{autoAlpha:1, duration:0.15}}, {F(9) + 0.05:.2f}); tl.to("#negro", {{autoAlpha:0, duration:0.05}}, {P("gta") - 0.08:.2f});')
escena("s9", s9, P("gta") - 0.08, F(10) + 0.05, "f", "x", "noir")
slam("#gta", P("gta") - 0.08, 0.4); shake(P("gta") + 0.05, 34); punch(P("gta"), 1.14, 1.4)
J(f'tl.fromTo("#gl", {{opacity:0.9, x:-40}}, {{opacity:0, x:40, duration:0.12, repeat:4, yoyo:true, immediateRender:false}}, {P("gta") - 0.08:.2f});')
fondo(P("gta") - 0.1, "#9d174d", "#4c1d95", 0.2)

# ================================================================== 10) lo dejas todo: trabajo, gimnasio, ducha
s10 = ('<div class="kick" id="k10">LO ÚNICO QUE SE TE DA BIEN</div><div class="mega" id="dej">DEJARLO TODO</div><div class="mid" id="nada">APRENDIDO: <span class="red">NADA</span></div>'
       '<div class="lista">' + "".join(f'<div class="li" id="li{k}"><i>{e}</i><b>{n}</b><i class="lin"></i><span>✗</span></div>' for k, (e, n) in enumerate((("💼", "Trabajo"), ("🏋️", "Gimnasio"), ("🚿", "Ducha")))) + '</div>')
escena("s10", s10, F(10) - 0.05, F(11) + 0.05)
pop("#k10", P("unico") - 0.2 if "unico" in [w for w, a, b in WORDS] else F(10) + 1.5)
slam("#dej", P("dejarlo") - 0.1)
J(f'tl.to("#k10", {{autoAlpha:0, duration:0.2}}, {P("dejarlo") - 0.3:.2f}); tl.to("#nada", {{autoAlpha:0, duration:0.2}}, {P("dejarlo") - 0.3:.2f}); tl.to("#dej", {{y:-230, scale:0.7, duration:0.4, ease:"expo.inOut"}}, {P("trabajo") - 0.5:.2f});')
slam("#nada", P("nada") - 0.1)
for k, w in enumerate(("trabajo", "gimnasio", "ducha")):
    pop(f"#li{k}", P(w) - 0.25); tacha(f"#li{k} .lin", P(w) + 0.25)
shake(P("ducha") + 0.3, 12)
fondo(F(10), "#3b0764", "#1a0333")

# ================================================================== 11) dimisión por WhatsApp… trozo de mierda
s11 = ('<div class="wa"><div class="wahead"><i>J</i><div><b>Jefe</b><small>en línea</small></div></div><div class="wabody">'
       '<div class="burb yo" id="w1">Lo dejo.<span>✓✓</span></div><div class="burb yo" id="w2">🎮🎮🎮<span>✓✓</span></div><div class="burb el" id="w3">¿¿¿Perdona???</div>'
       '<div class="escr" id="w4">Jefe está escribiendo…</div></div></div>' + CENSOR.replace('class="cens"', 'class="cens" id="c11"')
       + '<div class="mid" id="trozo">COMO EL TROZO DE</div>')
escena("s11", s11, F(11) - 0.05, F(12) + 0.05)
pop("#w1", P("whatsapp") - 0.3); pop("#w2", P("whatsapp") + 0.3)
J(f'tl.to("#w1 span, #w2 span", {{color:"#34b7f1", duration:0.1}}, {P("whatsapp") + 0.9:.2f});')
pop("#w3", P("whatsapp") + 1.0)
pop("#trozo", P("trozo") - 0.15)
slam("#c11", P("mierda") - 0.05, 0.22); punch(P("mierda") - 0.05, 1.15, 0.7)
fondo(F(11), "#064e3b", "#022c22")

# ================================================================== 12) 24 h jugando; mamá deja la comida en la puerta
s12 = ('<div class="reloj" id="rel"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="440" height="440"><circle cx="150" cy="150" r="130" fill="none" stroke="#2a2f3a" stroke-width="22"/>'
       '<circle id="arco" cx="150" cy="150" r="130" fill="none" stroke="#ff2e88" stroke-width="22" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" transform="rotate(-90 150 150)"/></svg>'
       '<div class="hrs"><b><span id="nhoras">0</span> h</b><small>JUGANDO HOY</small></div></div>'
       '<div class="noti" id="noti"><i>👩</i><div><b>Mamá</b><p>Te dejo la comida en la puerta 🍝</p></div></div>'
       '<div class="kick" id="k12">DE VUELTA AL SOFÁ DE PAPÁ Y MAMÁ</div>')
escena("s12", s12, F(12) - 0.05, F(13) + 0.05)
pop("#k12", F(12) + 0.1)
pop("#rel", P("veinticuatro") - 0.4)
at("#arco", P("veinticuatro") - 0.2, 2.6, "power2.inOut", strokeDashoffset=0)
contador("#nhoras", 0, 24, P("veinticuatro") - 0.2, 2.6)
J(f'tl.set("#noti", {{autoAlpha:0}}, 0); tl.fromTo("#noti", {{autoAlpha:1, y:-300}}, {{y:0, duration:0.45, ease:"back.out(1.6)", immediateRender:false}}, {P("comida") - 0.8:.2f});')
fondo(F(12), "#701a75", "#2e1065")

# ================================================================== 13) en el juego: millones; en la vida: 4 € y una deuda
s13 = ('<div class="split"><div class="mitad juego"><small>EN EL JUEGO</small><b>$<span id="nmill">0</span></b><div class="iconos" id="icj"><i>🏰</i><i>🏎️</i><i>🛥️</i><i>🚁</i></div></div>'
       '<div class="mitad real"><small>EN LA VIDA REAL</small><b><span id="ncuatro">1.350</span> €</b><div class="deuda" id="deuda">Debes 50 € a tu hermano</div></div></div>')
escena("s13", s13, F(13) - 0.05, F(14) + 0.05, "y")
contador("#nmill", 0, 48000000, P("mansiones") - 0.3, 2.6)
J(f'tl.fromTo("#icj i", {{scale:0, autoAlpha:0}}, {{scale:1, autoAlpha:1, duration:0.35, stagger:0.25, ease:"back.out(3)", immediateRender:false}}, {P("mansiones") - 0.2:.2f});')
contador("#ncuatro", 1350, 4, P("vida", 2) - 0.6, 1.4, 2)
pop("#deuda", P("hermano") - 0.5); shake(P("cuatro") + 0.1, 10)
fondo(F(13), "#1e1b4b", "#3f0d12")

# ================================================================== 14-15) unos se hacen ricos… tú decides lo que eres, muertazo
s14 = ('<div class="frase" id="u1">Unos se hacen ricos<br><b>en el juego.</b></div><div class="frase big" id="u2">Otros,<br><b>en la vida.</b></div>')
escena("s14", s14, F(14) - 0.05, F(15) + 0.05, "f", "f")
J(f'tl.set(["#u1", "#u2"], {{autoAlpha:0}}, 0); tl.fromTo("#u1", {{autoAlpha:1, y:40, opacity:0}}, {{y:0, opacity:1, duration:0.5, ease:"expo.out", immediateRender:false}}, {F(14):.2f}); tl.to("#u1", {{opacity:0.35, duration:0.3}}, {P("otros", 2) - 0.2:.2f});')
J(f'tl.fromTo("#u2", {{autoAlpha:1, y:40, opacity:0}}, {{y:0, opacity:1, duration:0.5, ease:"expo.out", immediateRender:false}}, {P("otros", 2) - 0.1:.2f});')
s15 = '<div class="mid" id="dec">TÚ DECIDES LO QUE ERES</div><div class="mega red final" id="muert">MUERTAZO.</div>'
escena("s15", s15, F(15) - 0.05, DUR + 1, "f", "f")
J(f'tl.set("#dec", {{autoAlpha:0}}, 0); tl.fromTo("#dec", {{autoAlpha:1, opacity:0, letterSpacing:"20px"}}, {{opacity:1, letterSpacing:"2px", duration:0.7, ease:"expo.out", immediateRender:false}}, {F(15):.2f});')
slam("#muert", P("muertazo") - 0.05, 0.3); punch(P("muertazo"), 1.08, 3.0)
fondo(F(14), "#111827", "#030712"); fondo(P("muertazo") - 0.1, "#7f1d1d", "#000000", 0.2)

# ------------------------------------------------------------------ montaje
_S = open(os.path.join(BASE, "_subs.py"), encoding="utf-8").read()
exec(re.sub(r"CLAVE = set\(.*?\]\)", lambda m: 'CLAVE = set(norm(w) for w in ["vago", "tu", "veinticinco", "linkedin", "llaman", "cogido", "dieciocho", "campeon", "nomina", "magia", "zapatillas", "alquiler", "veinte", "adulto", "gta", "6", "dejarlo", "trabajo", "gimnasio", "ducha", "whatsapp", "veinticuatro", "millones", "cuatro", "hermano", "juego", "vida", "decides", "muertazo"])', _S, count=1, flags=re.S))
CSS = open(os.path.join(BASE, "estilo.css"), encoding="utf-8").read()
html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>{CSS.replace("%%", "")}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="bg"><i id="b1"></i><i id="b2"></i></div>
  <div id="shake"><div id="cam">{"".join(SC)}</div></div>
  <div id="negro"></div>
  <div id="vineta"></div><div id="grano"></div>
  <div id="marca">@mundo.supuesto</div>
  <div id="subs" data-layout-allow-overlap>{"".join(SUBS)}</div>
  <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{DUR}" data-track-index="5" data-volume="1"></audio>
</div>
<script>
const fmt = (v, d) => {{ const s = v.toFixed(d).split("."); return s[0].replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ".") + (s[1] ? "," + s[1] : ""); }};
const tl = gsap.timeline({{ paused: true }});
tl.fromTo("#b1", {{x:-120, y:-80}}, {{x:120, y:80, duration:{DUR / 2:.2f}, yoyo:true, repeat:1, ease:"sine.inOut"}}, 0);
tl.fromTo("#b2", {{x:100, y:120}}, {{x:-100, y:-60, duration:{DUR / 2:.2f}, yoyo:true, repeat:1, ease:"sine.inOut"}}, 0);
{chr(10).join(tl)}
tl.to({{}}, {{duration:0.01}}, {DUR - 0.01});
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>"""
open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(html)
json.dump([], open(os.path.join(BASE, "efectos.json"), "w"))
json.dump([[0, 0.0], [DUR, 0.0]], open(os.path.join(BASE, "ambiente.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones · censuras {len(cens)}")

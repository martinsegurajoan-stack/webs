#!/usr/bin/env python3
"""«2 cachimbas al día vs 1 paquete de tabaco durante 10 años» — pantalla partida (arriba cachimba, abajo tabaco),
edición dinámica (zooms, textos que golpean, contadores), personas de palo adultas.
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
def PL(word):
    return [a for w, a, b in WORDS if w == norm(word)][-1]
def F(n): return FR[n - 1]["ini"]
def FE(n): return FR[n - 1]["fin"]
tl, FX, DEFS, FXL = [], [], [], []
def J(s): tl.append(s)
def fx(k, t): FX.append([k, round(t, 3)])
CY_, RJ, AM, VE, TX, LI = "#4fd1ff", "#ff5a4f", "#ffc24a", "#35d987", "#eef4fb", "#b98cff"
def cansancio(t): return 0.0
exec(open(os.path.join(BASE, "_figuras.py"), encoding="utf-8").read())
rw = random.Random(9)

# ------------------------------------------------------------------ AÑOS (todo depende de ellos)
R0 = F(19) + 0.1                                 # rebobinado final al año 0 (bucle)
R1 = R0 + 1.6
ANCH = [(0, 0), (F(6) - 1.3, 0), (P("tres"), 3), (P("cinco") - 1.0, 3.3), (P("cinco"), 5), (F(8) - 1.0, 5.4),
        (P("diez", 2), 10), (R0, 10), (R1, 0), (DUR, 0)]
def Y(t):
    for (a, va), (b, vb) in zip(ANCH, ANCH[1:]):
        if a <= t <= b:
            return va + (vb - va) * (t - a) / max(1e-6, b - a)
    return 0.0
TS = sorted(set([round(i * 0.2, 2) for i in range(int(DUR / 0.2) + 1)] + [DUR]))

# ------------------------------------------------------------------ posturas
def Pz(**k):
    base = dict(head=(0, -91), neck=(0, -80), hip=(0, -48), eR=(12, -62), hR=(10, -50), eL=(-12, -62), hL=(-10, -50), tip=(10, -50),
                kR=(7, -24), fR=(9, 0), kL=(-7, -24), fL=(-9, 0))
    base.update(k); base["tip"] = base["hR"]; return base
def Sz(**k):
    base = dict(head=(0, -64), neck=(0, -54), hip=(0, -24), eR=(12, -40), hR=(16, -28), eL=(-12, -40), hL=(-16, -28), tip=(16, -28),
                kR=(8, -24), fR=(9, 0), kL=(-8, -24), fL=(-9, 0))
    base.update(k); base["tip"] = base["hR"]; return base
POSES.update({
    "s_calada": Sz(eR=(12, -44), hR=(4, -58)),
    "s_relax": Sz(eR=(14, -38), hR=(18, -26), head=(2, -63)),
    "s_tos": Sz(head=(-2, -60), neck=(-1, -51), eR=(10, -46), hR=(2, -56), eL=(-10, -42), hL=(-6, -34)),
    "s_cansado": Sz(head=(3, -60), neck=(2, -52), hip=(0, -24), eR=(12, -38), hR=(14, -26)),
    "p_calada": Pz(eR=(12, -70), hR=(4, -86), eL=(-12, -64), hL=(4, -60)),
    "p_fuma": Pz(eR=(14, -64), hR=(20, -70), eL=(-12, -64), hL=(4, -60)),
    "p_tos": Pz(head=(-3, -86), neck=(-2, -77), hip=(0, -47), eR=(10, -70), hR=(2, -82), eL=(-12, -62), hL=(-8, -50), kR=(8, -23), kL=(-8, -23)),
    "p_ahogo": Pz(head=(6, -78), neck=(5, -70), hip=(0, -44), eR=(14, -48), hR=(12, -28), eL=(-8, -50), hL=(-6, -28), kR=(10, -22), kL=(-6, -22)),
    "p_mano": Pz(eR=(16, -70), hR=(24, -84), eL=(-12, -64), hL=(4, -60)),
})
def pz(pid, nombre, t, d=0.25, ease="power2.out", solo=None):
    pose(pid, nombre, t, d, ease, slouch=0.0, solo=solo)
    for oid, mano in OBJ.get(pid, []):
        j = joints(POSES[nombre])
        J(f'tl.to("#{oid}", {{x:{j[mano][0]:.1f}, y:{j[mano][1]:.1f}, duration:{d}, ease:"{ease}"}}, {t:.3f});')
OBJ = {}

# ------------------------------------------------------------------ ESCENARIO (pantalla partida)
AY0, AY1 = 520, 1130                             # panel de arriba: cachimba
BY0, BY1 = 1180, 1800                            # panel de abajo: tabaco
DEFS += [
    f'<clipPath id="clipA"><rect x="0" y="{AY0}" width="1080" height="{AY1 - AY0}"/></clipPath>',
    f'<clipPath id="clipB"><rect x="0" y="{BY0}" width="1080" height="{BY1 - BY0}"/></clipPath>',
    '<linearGradient id="paredA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a1630"/><stop offset="1" stop-color="#5a2340"/></linearGradient>',
    '<linearGradient id="cieloB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a1230"/><stop offset="1" stop-color="#2c3a78"/></linearGradient>',
    '<radialGradient id="lampA" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffb35c" stop-opacity="0.65"/><stop offset="1" stop-color="#ffb35c" stop-opacity="0"/></radialGradient>',
    '<radialGradient id="brasa" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffd27a"/><stop offset="0.4" stop-color="#ff7a2a"/><stop offset="1" stop-color="#ff3a1a" stop-opacity="0"/></radialGradient>',
    '<linearGradient id="vidrioA" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7a4ad6" stop-opacity="0.75"/><stop offset="0.5" stop-color="#c9a8ff" stop-opacity="0.55"/><stop offset="1" stop-color="#5a2ab0" stop-opacity="0.8"/></linearGradient>',
    '<radialGradient id="humo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#e9e6f2" stop-opacity="0.55"/><stop offset="1" stop-color="#e9e6f2" stop-opacity="0"/></radialGradient>',
    '<linearGradient id="pulmonG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff9ec7"/><stop offset="1" stop-color="#e86a9e"/></linearGradient>',
]
A, B = [], []
# --- PANEL A: local de cachimbas
A.append(f'<rect x="0" y="{AY0}" width="1080" height="{AY1 - AY0}" fill="url(#paredA)"/>')
for i in range(9):                                # celosía árabe en la pared
    x = 40 + i * 120
    A.append(f'<path d="M{x},{AY0 + 40} q50,-40 100,0 v180 h-100 Z" fill="none" stroke="#7a3a5a" stroke-width="4" opacity="0.6"/>')
A.append(f'<rect x="0" y="{AY1 - 120}" width="1080" height="120" fill="#2a0f22"/>')
A.append(f'<g transform="translate(200,{AY0})"><path d="M0,0 L0,70" stroke="#c9a25a" stroke-width="3"/><path d="M-30,70 L30,70 L20,120 L-20,120 Z" fill="#c9a25a"/><circle cx="0" cy="110" r="150" fill="url(#lampA)"/></g>')
A.append(f'<g transform="translate(880,{AY0})"><path d="M0,0 L0,50" stroke="#c9a25a" stroke-width="3"/><path d="M-26,50 L26,50 L18,96 L-18,96 Z" fill="#c9a25a"/><circle cx="0" cy="86" r="130" fill="url(#lampA)"/></g>')
A.append(f'<g transform="translate(330,{AY1 - 120})"><rect x="-250" y="-130" width="500" height="110" rx="26" fill="#6b1f3a"/><rect x="-270" y="-70" width="540" height="70" rx="22" fill="#8a2a4c"/>'
         + "".join(f'<rect x="{-220 + i * 150}" y="-120" width="120" height="60" rx="18" fill="{c}"/>' for i, c in enumerate(("#c9a25a", "#3a8a7a", "#c9a25a"))) + '</g>')
A.append(f'<rect x="560" y="{AY1 - 170}" width="200" height="16" rx="6" fill="#4a2a18"/><rect x="580" y="{AY1 - 156}" width="12" height="36" fill="#4a2a18"/><rect x="728" y="{AY1 - 156}" width="12" height="36" fill="#4a2a18"/>')
# la cachimba (base de vidrio, tubo, cazoleta con carbón, manguera)
HX, HB = 680, AY1 - 170                           # centro y apoyo de la base
A.append(f'<g id="cachimba"><path d="M{HX - 46},{HB} Q{HX - 70},{HB - 70} {HX - 22},{HB - 120} L{HX + 22},{HB - 120} Q{HX + 70},{HB - 70} {HX + 46},{HB} Z" fill="url(#vidrioA)" stroke="#e6d6ff" stroke-width="3"/>'
         f'<path id="aguaA" d="M{HX - 52},{HB - 50} Q{HX},{HB - 58} {HX + 52},{HB - 50} Q{HX + 50},{HB - 6} {HX + 44},{HB - 2} L{HX - 44},{HB - 2} Q{HX - 50},{HB - 6} {HX - 52},{HB - 50} Z" fill="#8fd3ff" opacity="0.45"/>'
         f'<rect x="{HX - 8}" y="{HB - 330}" width="16" height="215" fill="#c9a25a"/><rect x="{HX - 30}" y="{HB - 250}" width="60" height="14" rx="5" fill="#c9a25a"/>'
         f'<path d="M{HX - 40},{HB - 330} L{HX + 40},{HB - 330} L{HX + 22},{HB - 380} L{HX - 22},{HB - 380} Z" fill="#8a3a2a"/>'
         f'<rect x="{HX - 30}" y="{HB - 392}" width="60" height="14" rx="4" fill="#9fb3c8"/>'
         + "".join(f'<rect x="{HX - 24 + i * 17}" y="{HB - 404}" width="14" height="12" rx="2" fill="#2a1a18"/>' for i in range(3))
         + f'<circle id="brasaA" cx="{HX}" cy="{HB - 398}" r="46" fill="url(#brasa)" opacity="0.8"/>'
         + f'<g id="burbujas">' + "".join(f'<circle class="burb" cx="{HX - 30 + i * 12}" cy="{HB - 12}" r="{3 + (i % 3)}" fill="#e6f6ff" opacity="0.8"/>' for i in range(6)) + '</g></g>')
# --- PANEL B: balcón de noche
B.append(f'<rect x="0" y="{BY0}" width="1080" height="{BY1 - BY0}" fill="url(#cieloB)"/>')
for i in range(22):
    bx, bh = i * 52 - 10, rw.randint(120, 380)
    B.append(f'<rect x="{bx}" y="{BY1 - 140 - bh}" width="48" height="{bh}" fill="#141a3a"/>')
    for k in range(bh // 34):
        if rw.random() < 0.4:
            B.append(f'<rect x="{bx + 10 + (k % 2) * 16}" y="{BY1 - 140 - bh + 12 + k * 34}" width="8" height="10" fill="#ffd27a" opacity="0.75"/>')
B.append(f'<circle cx="900" cy="{BY0 + 90}" r="34" fill="#f4f1e2"/>')
B.append(f'<rect x="0" y="{BY1 - 140}" width="1080" height="140" fill="#3a3a4a"/><rect x="0" y="{BY1 - 140}" width="1080" height="10" fill="#5a5a6a"/>')
B.append(f'<path d="M0,{BY1 - 250} L1080,{BY1 - 250}" stroke="#9fb3c8" stroke-width="10"/>' + "".join(f'<rect x="{x}" y="{BY1 - 250}" width="8" height="110" fill="#9fb3c8"/>' for x in range(20, 1080, 46)))
B.append(f'<g transform="translate(780,{BY1 - 250})"><path d="M-40,0 Q0,-24 40,0 Z" fill="#6b6b7a"/><g id="colillas"></g></g>')
B.append(f'<rect x="120" y="{BY1 - 130}" width="12" height="130" fill="#2a2a3a"/>')

# ------------------------------------------------------------------ PERSONAS
JA = dict(piel="#e6b28b", pelo="#2a1a14", cam="#7a5bd6", short="#1d2433", zap="#f2f4f7", raq="none", cinta="#2a1a14")
JB = dict(piel="#c68c63", pelo="#1d1d24", cam="#e2804a", short="#2c4566", zap="#1d1d24", raq="none", cinta="#1d1d24")
POSES["sentadoA"] = POSES["s_relax"]
manguera = '<g id="A_boq"><rect x="-3" y="-8" width="6" height="12" rx="2" fill="#c9a25a"/></g>'
cig = ('<g id="B_cig"><rect x="-1.4" y="-9" width="2.8" height="12" fill="#f4f1e2"/><rect x="-1.4" y="-9" width="2.8" height="3" fill="#ffb35c"/>'
       '<circle id="B_ascua" cx="0" cy="-9" r="2.4" fill="#ff5a1a"/></g>')
def cara(pid):
    return (f'<circle cx="-3.2" cy="-90.6" r="1.1" fill="#1d1d24"/><circle cx="3.2" cy="-90.6" r="1.1" fill="#1d1d24"/>'
            f'<path d="M-5.2,-93.4 l3.4,-0.6 M5.2,-93.4 l-3.4,-0.6" stroke="#2a1a14" stroke-width="1.1" stroke-linecap="round"/>'
            f'<g id="{pid}_oj" opacity="0"><path d="M-4.6,-88.6 q1.4,1 2.8,0 M1.8,-88.6 q1.4,1 2.8,0" stroke="#6b4a7a" stroke-width="0.9" fill="none"/></g>'
            f'<path id="{pid}_son" d="M-3.4,-86.4 Q0,-84 3.4,-86.4" stroke="#5a1d1d" stroke-width="1.2" fill="none" stroke-linecap="round"/>'
            f'<ellipse id="{pid}_o" cx="0" cy="-85.6" rx="1.7" ry="2.3" fill="#5a1d1d" opacity="0"/>'
            f'<g id="{pid}_die" opacity="0"><path d="M-3.6,-86.8 L3.6,-86.8 Q3,-83.6 0,-83.4 Q-3,-83.6 -3.6,-86.8 Z" fill="#5a1d1d"/><rect id="{pid}_dt" x="-3" y="-86.8" width="6" height="1.6" fill="#ffffff"/></g>')
def con_cara(pid, g):
    a = g.index(f'<g id="{pid}_h" >'); b = g.index('</g></g>', a)
    return g[:b] + cara(pid) + g[b:]
figA = con_cara("A", figura("A", JA, "s_relax", sudor=False, extra=manguera))
figB = con_cara("B", figura("B", JB, "p_fuma", sudor=False, extra=cig))
OBJ["A"] = [("A_boq", "hR")]; OBJ["B"] = [("B_cig", "hR")]
AX, AYp, AS = 360, AY1 - 128, 3.3                # A sentado en el sofá
BX, BYp, BS = 450, BY1 - 40, 3.2                 # B de pie en el balcón
J(f'tl.set("#A", {{svgOrigin:"0 0", x:{AX}, y:{AYp}, scale:{AS}}}, 0); tl.set("#B", {{svgOrigin:"0 0", x:{BX}, y:{BYp}, scale:{BS}}}, 0);')
pz("A", "s_relax", 0, 0.01); pz("B", "p_fuma", 0, 0.01)
# manguera: de la cachimba a la mano de A (se redibuja siguiendo la mano con un trazo fijo aproximado)
A.append(f'<path id="manguera" d="M{HX - 30},{HB - 250} C{HX - 120},{HB - 120} {AX + 140},{AYp - 40} {AX + 60},{AYp - 92}" stroke="#2a6a8a" stroke-width="9" fill="none" stroke-linecap="round"/>')

# humo continuo en los dos paneles (bocanadas que suben y se deshacen)
def humo(pref, x, y, n, t0=0.0):
    out = []
    for i in range(n):
        cid = f"{pref}{i}"
        out.append(f'<g transform="translate({x},{y})"><g id="{cid}"><circle r="26" fill="url(#humo)"/></g></g>')
        per = 3.2 + (i % 3) * 0.5
        J(f'tl.fromTo("#{cid}", {{x:0, y:0, scale:0.4, opacity:0.0}}, {{keyframes:[{{x:{(i % 2) * 30 - 15}, y:-60, scale:1.0, opacity:0.8, duration:{per * 0.35:.2f}}}, {{x:{(i % 3) * 25 - 25}, y:-170, scale:2.2, opacity:0, duration:{per * 0.65:.2f}}}], repeat:{int(DUR / per)}, immediateRender:false, ease:"none"}}, {t0 + i * per / n:.2f});')
    return out
A += humo("hA", AX + 30, AYp - 230, 6)
A += humo("hC", HX, HB - 420, 3, 0.5)
B += humo("hB", BX + 70, BYp - 330, 5)
J(f'tl.fromTo(".burb", {{y:0, opacity:0.9}}, {{y:-42, opacity:0, duration:0.6, stagger:0.1, repeat:{int(DUR / 0.6)}, ease:"power1.out", immediateRender:false}}, 0);')
J(f'tl.fromTo("#brasaA", {{opacity:0.6}}, {{opacity:1, duration:1.1, yoyo:true, repeat:{int(DUR / 1.1)}, ease:"sine.inOut", immediateRender:false}}, 0);')
J(f'tl.fromTo("#B_ascua", {{opacity:0.6}}, {{opacity:1, duration:0.8, yoyo:true, repeat:{int(DUR / 0.8)}, ease:"sine.inOut", immediateRender:false}}, 0);')
# caladas periódicas (vida constante)
def caladas(pid, pa, pb, t0, t1, cada):
    t = t0
    while t < t1 - 1.0:
        pz(pid, pa, t, 0.35, "sine.inOut"); pz(pid, pb, t + 0.9, 0.4, "sine.inOut"); t += cada
CALM = [(0, F(6) - 0.3), (FE(7) + 0.2, F(14)), (F(16) + 0.3, DUR)]
for a, b in CALM:
    caladas("A", "s_calada", "s_relax", a + 0.4, b, 3.4)
    caladas("B", "p_calada", "p_fuma", a + 1.2, b, 2.9)

# ------------------------------------------------------------------ indicadores fijos de cada panel (pulmón, aliento, contadores)
def panel_ui(pref, y0, color, titulo):
    return (f'<div class="ptag" style="top:{y0 + 14}px;border-color:{color}">{titulo}</div>'
            f'<div class="pcont" style="top:{y0 + 70}px"><b id="{pref}_n">0</b><small id="{pref}_nl"></small><b id="{pref}_e" class="eur">0 €</b></div>'
            f'<div class="pulm" style="top:{y0 + 14}px"><svg viewBox="0 0 120 110" width="120" height="110"><path d="M60,8 L60,40" stroke="#e9e2cf" stroke-width="6"/>'
            f'<path id="{pref}_pl" d="M54,36 C30,30 10,55 14,88 C18,104 44,104 52,92 Z M66,36 C90,30 110,55 106,88 C102,104 76,104 68,92 Z" fill="#ff9ec7"/>'
            f'<g id="{pref}_man" opacity="0">' + "".join(f'<circle cx="{rx}" cy="{ry}" r="{rr}" fill="#3a2a2a"/>' for rx, ry, rr in ((32, 66, 6), (88, 70, 5), (40, 84, 4), (80, 54, 4), (26, 50, 3))) + '</g></svg>'
            f'<small>ALIENTO</small><div class="al"><i id="{pref}_al"></i></div></div>')
UI = panel_ui("ua", AY0, LI, "2 CACHIMBAS / DÍA") + panel_ui("ub", BY0, "#ff9a5a", "1 PAQUETE / DÍA")
UI += ('<div id="anio"><small>AÑO</small><b id="anioN">0</b><div class="barra"><i id="anioB"></i></div></div>')
J('const yv = {v:0};')
kf = [f'{{v:{Y(tb):.4f}, duration:{tb - ta:.3f}, ease:"none"}}' for ta, tb in zip(TS, TS[1:])]
J('''function pinta(y){
  const f = x => String(Math.round(x)).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ".");
  document.getElementById("anioN").textContent = Math.floor(y + 0.001); document.getElementById("anioB").style.width = (y * 10) + "%";
  document.getElementById("ua_n").textContent = f(730 * y); document.getElementById("ua_nl").textContent = " sesiones";
  document.getElementById("ub_n").textContent = f(7300 * y); document.getElementById("ub_nl").textContent = " cigarrillos";
  document.getElementById("ua_e").textContent = f(8760 * y) + " €"; document.getElementById("ub_e").textContent = f(2007.5 * y) + " €";
  const mix = (a, b, k) => "rgb(" + a.map((c, i) => Math.round(c + (b[i] - c) * k)).join(",") + ")";
  document.getElementById("ua_pl").setAttribute("fill", mix([255,158,199], [122,96,104], Math.min(1, y / 10)));
  document.getElementById("ub_pl").setAttribute("fill", mix([255,158,199], [110,90,90], Math.min(1, y / 10)));
  document.getElementById("ua_man").style.opacity = Math.min(1, y / 9); document.getElementById("ub_man").style.opacity = Math.min(1, y / 8);
  document.getElementById("ua_al").style.width = (100 - 3.4 * y) + "%"; document.getElementById("ub_al").style.width = (100 - 3.6 * y) + "%";
  document.getElementById("A_oj").style.opacity = Math.min(1, y / 7); document.getElementById("B_oj").style.opacity = Math.min(1, y / 7);
  document.getElementById("B_dt").setAttribute("fill", mix([255,255,255], [222,190,90], Math.min(1, y / 5)));
}''')
J(f'tl.to(yv, {{keyframes:[{",".join(kf)}], onUpdate:() => pinta(yv.v)}}, 0);')
J('pinta(0);')
# colillas que se acumulan en el cenicero
col = "".join(f'<rect class="col" x="{-34 + (i % 9) * 8}" y="{-6 - (i // 9) * 5}" width="7" height="3" rx="1" fill="{["#f4f1e2", "#ffb35c"][i % 2]}" transform="rotate({rw.randint(-30, 30)})"/>' for i in range(36))
B = [b.replace('<g id="colillas"></g>', f'<g id="colillas">{col}</g>') for b in B]
J('tl.set(".col", {opacity:0}, 0);')
J(f'tl.to(".col", {{opacity:1, duration:0.05, stagger:{(P("diez", 2) - F(6)) / 36:.3f}}}, {F(6):.2f}); tl.set(".col", {{opacity:0}}, {R0 + 0.8:.2f});')

# ------------------------------------------------------------------ herramientas de edición
def slam(cid, html, t, hasta, y=1100, cls="slam", rot=-3, son="golpe"):
    FXL.append(f'<div id="{cid}" class="{cls}" style="top:{y}px">{html}</div>')
    J(f'tl.set("#{cid}", {{opacity:0}}, 0); tl.fromTo("#{cid}", {{opacity:0, scale:2.2, rotation:{rot * 2}}}, {{opacity:1, scale:1, rotation:{rot}, duration:0.3, ease:"back.out(2.2)", immediateRender:false}}, {t:.2f});')
    J(f'tl.to("#{cid}", {{opacity:0, scale:1.2, duration:0.2, ease:"power2.in"}}, {hasta:.2f});')
    if son:
        fx(son, t)
def plano(t, cx, cy, z, d=0.5, ease="power3.inOut"):
    x = min(0, max(1080 - 1080 * z, 540 - cx * z)); y = min(0, max(1920 - 1920 * z, 960 - cy * z))
    J(f'tl.to("#cam", {{x:{x:.0f}, y:{y:.0f}, scale:{z:.3f}, duration:{d:.2f}, ease:"{ease}"}}, {t:.2f});')
    fx("whoosh", t) if d <= 0.5 and z != 1 else None
def ancho(t, d=0.5): plano(t, 540, 960, 1.0, d)
def golpe_cam(t, f=12):
    J(f'tl.fromTo("#imp", {{x:0, y:0}}, {{keyframes:[{{x:{f}, y:{-f * 0.6:.0f}, duration:0.05}}, {{x:{-f * 0.8:.0f}, y:{f * 0.5:.0f}, duration:0.05}}, {{x:0, y:0, duration:0.08}}], immediateRender:false}}, {t:.2f});')
def boca(pid, t, tipo):
    for m in ("son", "o", "die"):
        J(f'tl.set("#{pid}_{m}", {{opacity:{1 if m == tipo else 0}}}, {t:.2f});')
def tos(pid, t, sentado):
    pz(pid, "s_tos" if sentado else "p_tos", t, 0.2); boca(pid, t, "o")
    J(f'tl.fromTo("#{pid}_m", {{y:0}}, {{y:-6, duration:0.12, yoyo:true, repeat:5, ease:"sine.inOut", immediateRender:false}}, {t:.2f});')
    fx("tos", t)
CA, CB = (540, (AY0 + AY1) / 2), (540, (BY0 + BY1) / 2)

# ------------------------------------------------------------------ GUION VISUAL
J('tl.set("#cam", {x:0, y:0, scale:1, transformOrigin:"0 0"}, 0);')
# 1) gancho
slam("sQuien", '¿QUIÉN ACABA PEOR?', 0.0, P("cachimbas") - 0.2, y=960, cls="slam", son=None)
J('tl.set("#sQuien", {opacity:1, scale:1, rotation:-3}, 0);')
plano(P("cachimbas") - 0.2, 540, CA[1] + 40, 1.35, 0.45)
plano(P("paquete") - 0.2, 540, CB[1] + 40, 1.35, 0.45)
ancho(P("diez") - 0.2, 0.45)
slam("s10", '10 AÑOS', P("diez") - 0.05, P("peor") - 0.1, y=1105, cls="slam ama")
slam("sQuien2", '¿QUIÉN ACABA PEOR?', P("peor") - 0.1, FE(1) + 0.2, y=1105, cls="slam")
# 2) mitos
slam("sSuave", '«ES MÁS SUAVE»', P("suave") - 0.4, P("filtra") - 0.6, y=760, cls="slam lila", son="pop")
slam("sFiltra", '«EL AGUA LO FILTRA»', P("filtra") - 0.6, P("spoiler") - 0.1, y=900, cls="slam lila", son="pop")
slam("sNo", 'SPOILER: NO', P("spoiler"), FE(2) + 0.25, y=1105, cls="slam rojo", son="rasca")
golpe_cam(P("spoiler") + 0.4)
# 3) OMS: una sesión = 100+ cigarrillos de humo (cuadrícula de 100 cigarrillos)
plano(F(3) - 0.1, 540, CA[1], 1.2, 0.45)
slam("sOms", 'OMS', P("oms") - 0.1, P("cien") - 0.3, y=640, cls="slam az", son="pop")
cien = "".join(f'<i style="left:{(k % 10) * 86}px;top:{(k // 10) * 42}px"></i>' for k in range(100))
FXL.append(f'<div id="cien" class="cien">{cien}<b>1 SESIÓN ≈ 100+ CIGARRILLOS DE HUMO</b></div>')
J('tl.set("#cien", {opacity:0}, 0);')
J(f'tl.set("#cien", {{opacity:1}}, {P("cien") - 0.3:.2f}); tl.fromTo("#cien i", {{scale:0, opacity:0}}, {{scale:1, opacity:1, duration:0.12, stagger:0.012, ease:"back.out(2)", immediateRender:false}}, {P("cien") - 0.3:.2f}); tl.to("#cien", {{opacity:0, duration:0.25}}, {FE(3) + 0.3:.2f});')
fx("riser", P("cien") - 0.3)
# 4) el agua no filtra: zoom a la base, tóxicos que atraviesan el agua
plano(F(4) - 0.1, HX, HB - 60, 2.6, 0.5)
tox = "".join(f'<circle class="tox" cx="{HX - 20 + (k % 5) * 10}" cy="{HB - 20}" r="4" fill="#ff5a4f"/>' for k in range(10))
A.append(f'<g id="toxG">{tox}</g>')
J('tl.set(".tox", {opacity:0}, 0);')
J(f'tl.fromTo(".tox", {{opacity:1, y:0, x:0}}, {{keyframes:[{{y:-55, duration:0.6}}, {{y:-130, x:-40, duration:0.6}}], stagger:0.12, repeat:2, ease:"none", immediateRender:false}}, {P("enfria"):.2f}); tl.set(".tox", {{opacity:0}}, {FE(4):.2f});')
slam("sTox", 'NO FILTRA LOS TÓXICOS', P("toxicos") - 0.1, P("hondo") - 0.4, y=1350, cls="slam rojo")
plano(P("hondo") - 0.4, AX, AYp - 140, 2.0, 0.6)
pz("A", "s_calada", P("hondo") - 0.4, 0.4)
slam("sHondo", 'MÁS HONDO', P("hondo") - 0.1, FE(4) + 0.2, y=1350, cls="slam ama")
J(f'tl.fromTo(".pulm", {{scale:1}}, {{scale:1.25, duration:0.25, yoyo:true, repeat:3, immediateRender:false}}, {P("hondo"):.2f});')
# 5) carbón y monóxido; urgencias
plano(F(5) - 0.1, HX, HB - 390, 2.6, 0.5)
J(f'tl.to("#brasaA", {{scale:1.5, svgOrigin:"{HX} {HB - 398}", duration:0.4, yoyo:true, repeat:1}}, {P("carbon"):.2f});')
co = "".join(f'<text class="co" x="{HX - 40 + k * 22}" y="{HB - 430}" font-family="Inter" font-weight="900" font-size="18" fill="#ffd27a">CO</text>' for k in range(5))
A.append(co)
J('tl.set(".co", {opacity:0}, 0);')
J(f'tl.fromTo(".co", {{opacity:1, y:0}}, {{opacity:0, y:-120, duration:1.6, stagger:0.25, ease:"power1.out", immediateRender:false}}, {P("monoxido") - 0.2:.2f});')
slam("sCO", 'MONÓXIDO DE CARBONO', P("monoxido") - 0.1, P("urgencias") - 0.5, y=1350, cls="slam ama")
FXL.append('<div id="sirena"></div>')
J('tl.set("#sirena", {opacity:0}, 0);')
J(f'tl.to("#sirena", {{opacity:1, duration:0.15}}, {P("urgencias") - 0.2:.2f}); tl.to("#sirena", {{backgroundPosition:"100% 0", duration:0.5, repeat:4, yoyo:true, ease:"sine.inOut"}}, {P("urgencias") - 0.2:.2f}); tl.to("#sirena", {{opacity:0, duration:0.3}}, {FE(5) + 0.2:.2f});')
ancho(P("urgencias") - 0.4, 0.5)
slam("sUrg", '🚑 URGENCIAS', P("urgencias") - 0.1, FE(5) + 0.2, y=1105, cls="slam rojo", son="sirena")
# 6) año 3: tos y ahogo
slam("sA3", 'AÑO 3', P("tres") - 0.1, P("tosen") - 0.1, y=1105, cls="slam ama", son="clic2")
tos("A", P("tosen"), True); tos("B", P("tosen") + 0.15, False)
pz("A", "s_cansado", P("escaleras") - 0.2, 0.4); pz("B", "p_ahogo", P("escaleras") - 0.2, 0.4)
boca("A", FE(6), "son"); boca("B", FE(6), "son")
slam("sAh", 'SIN ALIENTO', P("escaleras") - 0.1, FE(6) + 0.2, y=1105, cls="slam rojo")
J(f'tl.fromTo(".al", {{boxShadow:"0 0 0px #ff5a4f"}}, {{boxShadow:"0 0 18px #ff5a4f", duration:0.3, yoyo:true, repeat:3, immediateRender:false}}, {P("escaleras"):.2f});')
# 7) año 5: dientes y dedos amarillos (B), encías (los dos)
slam("sA5", 'AÑO 5', P("cinco") - 0.1, P("dientes") - 0.1, y=1105, cls="slam ama", son="clic2")
pz("B", "p_mano", P("dientes") - 0.3, 0.3)
plano(P("dientes") - 0.3, BX + 30, BYp - 260, 2.6, 0.5)
boca("B", P("dientes") - 0.1, "die")
slam("sDie", 'DIENTES Y DEDOS AMARILLOS', P("dientes"), P("encias") - 0.2, y=1520, cls="slam ama")
plano(P("encias") - 0.2, AX, AYp - 190, 2.6, 0.5)
boca("A", P("encias") - 0.1, "die")
J(f'tl.set("#A_dt", {{attr:{{fill:"#ff7a8a"}}}}, {P("encias"):.2f}); tl.set("#A_dt", {{attr:{{fill:"#ffffff"}}}}, {FE(7) + 0.3:.2f});')
slam("sEnc", 'ENCÍAS QUE SANGRAN', P("encias"), FE(7) + 0.2, y=640, cls="slam rojo")
boca("A", FE(7) + 0.3, "son"); boca("B", FE(7) + 0.3, "son"); pz("B", "p_fuma", FE(7) + 0.3, 0.3)
ancho(FE(7) + 0.1, 0.5)
# 8) año 10: hagamos cuentas
slam("sA10", 'AÑO 10', P("diez", 2) - 0.1, P("cuentas") - 0.2, y=1105, cls="slam ama", son="clic2")
slam("sCuen", '🧮 HAGAMOS CUENTAS', P("cuentas") - 0.2, FE(8) + 0.2, y=1105, cls="slam", son="pop")
# 9) totales del tabaco (panel de abajo)
plano(F(9) - 0.1, 540, CB[1] - 20, 1.25, 0.5)
FXL.append('<div id="totB" class="tot" style="top:1240px"><div><b id="tbCig">0</b><small>CIGARRILLOS</small></div><div><b id="tbPaq">0</b><small>PAQUETES</small></div><div><b id="tbEur" class="eurb">0 €</b><small>EN 10 AÑOS</small></div></div>')
J('tl.set("#totB", {opacity:0}, 0);')
J(f'tl.fromTo("#totB", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.35, ease:"back.out(1.8)", immediateRender:false}}, {P("setenta") - 0.3:.2f}); tl.to("#totB", {{opacity:0, duration:0.25}}, {FE(9) + 0.4:.2f});')
def cuenta(eid, v, t, d=1.0, suf=""):
    o = f"c{len(tl)}"
    J(f'const {o} = {{v:0}}; tl.to({o}, {{v:{v}, duration:{d}, ease:"power2.out", onUpdate:() => {{ document.getElementById("{eid}").textContent = String(Math.round({o}.v)).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ".") + "{suf}"; }}}}, {t:.2f});')
    fx("cuenta", t)
cuenta("tbCig", 73000, P("setenta") - 0.1)
cuenta("tbPaq", 3650, P("paquetes") - 0.5)
cuenta("tbEur", 20075, P("veinte") - 0.3, 1.0, " €")
golpe_cam(P("veinte") + 0.7, 8)
# 10) totales de la cachimba (panel de arriba)
plano(F(10) - 0.1, 540, CA[1] + 20, 1.25, 0.5)
FXL.append('<div id="totA" class="tot" style="top:600px"><div><b id="taSes">0</b><small>SESIONES</small></div><div><b id="taEur" class="eurb">0 €</b><small>EN UN LOCAL</small></div></div>')
J('tl.set("#totA", {opacity:0}, 0);')
J(f'tl.fromTo("#totA", {{opacity:0, y:-40}}, {{opacity:1, y:0, duration:0.35, ease:"back.out(1.8)", immediateRender:false}}, {P("sesiones") - 0.6:.2f}); tl.to("#totA", {{opacity:0, duration:0.25}}, {FE(10) + 0.3:.2f});')
cuenta("taSes", 7300, P("sesiones") - 0.5)
cuenta("taEur", 87600, P("ochenta") - 0.4, 1.2, " €")
golpe_cam(P("ochenta") + 0.9, 14)
slam("sX4", 'x4 MÁS DINERO', P("cuatro") - 0.1, FE(10) + 0.25, y=1105, cls="slam rojo", son="golpe")
# 11) el tiempo: 7.300 horas ≈ 10 meses
ancho(F(11) - 0.1, 0.5)
slam("sHoras", '7.300 HORAS', P("horas", 2) - 0.1, P("meses") - 0.2, y=760, cls="slam lila")
slam("sMeses", '≈ 10 MESES SIN PARAR', P("meses") - 0.2, FE(11) + 0.2, y=880, cls="slam ama")
# 12) volumen de humo: 730.000 cigarrillos
plano(F(12) - 0.1, 540, CA[1], 1.3, 0.5)
J(f'tl.to(".hA, #hA0, #hA1, #hA2, #hA3, #hA4, #hA5", {{scale:"+=1.2", duration:0.6}}, {P("volumen"):.2f});')
FXL.append('<div id="sHumo" class="slam lila" style="top:700px">≈ <b id="humoN">0</b><small>CIGARRILLOS DE HUMO</small></div>')
J('tl.set("#sHumo", {opacity:0}, 0);')
J(f'tl.fromTo("#sHumo", {{opacity:0, scale:2}}, {{opacity:1, scale:1, duration:0.3, ease:"back.out(2)", immediateRender:false}}, {P("setecientos") - 0.4:.2f}); tl.to("#sHumo", {{opacity:0, duration:0.2}}, {FE(12) + 0.25:.2f});')
cuenta("humoN", 730000, P("setecientos") - 0.3, 1.1)
# 13) estudio 2024: -20 min por cigarrillo → -2,5 años (panel de abajo)
plano(F(13) - 0.1, 540, CB[1], 1.3, 0.5)
slam("s20", '−20 MIN<small>POR CIGARRILLO (ESTUDIO 2024)</small>', P("minutos") - 0.3, P("tabaco", 4) - 0.1, y=1250, cls="slam az", son="tic")
FXL.append('<div id="reloj" class="reloj"><svg viewBox="0 0 100 100" width="150" height="150"><circle cx="50" cy="50" r="44" fill="#140f24" stroke="#fff" stroke-width="5"/><g id="aguja"><path d="M50,50 L50,14" stroke="#ff5a4f" stroke-width="5" stroke-linecap="round"/></g></svg></div>')
J('tl.set("#reloj", {opacity:0}, 0);')
J(f'tl.to("#reloj", {{opacity:1, duration:0.2}}, {P("minutos") - 0.3:.2f}); tl.to("#aguja", {{rotation:-1440, svgOrigin:"50 50", duration:3.0, ease:"power2.in"}}, {P("minutos") - 0.3:.2f}); tl.to("#reloj", {{opacity:0, duration:0.2}}, {FE(13) + 0.2:.2f});')
slam("s25", '−2,5 AÑOS DE VIDA', P("tabaco", 4) - 0.1, FE(13) + 0.25, y=1450, cls="slam rojo", son="golpe")
# 14) la cachimba: rayos X con pulmón, boca y corazón
plano(F(14) - 0.1, AX, AYp - 140, 1.9, 0.5)
FXL.append('<div id="rx" class="rx"><svg viewBox="0 0 300 360" width="360" height="430"><rect width="300" height="360" rx="20" fill="#06111d" opacity="0.9"/>'
           '<circle cx="150" cy="60" r="34" fill="none" stroke="#e8f4ff" stroke-width="4"/><path id="rxBoca" d="M134,72 Q150,82 166,72" stroke="#ff5a4f" stroke-width="6" fill="none"/>'
           '<path d="M150,94 L150,140" stroke="#e8f4ff" stroke-width="6"/><path id="rxPul" d="M142,140 C100,130 70,180 76,250 C82,290 130,290 140,262 Z M158,140 C200,130 230,180 224,250 C218,290 170,290 160,262 Z" fill="#6b5a62" stroke="#e8f4ff" stroke-width="3"/>'
           '<path id="rxCor" d="M160,220 C150,205 132,214 140,230 L160,250 L180,230 C188,214 170,205 160,220 Z" fill="#ff5a4f"/></svg>'
           '<small id="rx1">PULMÓN</small><small id="rx2">BOCA</small><small id="rx3">CORAZÓN</small></div>')
J('tl.set("#rx, #rx1, #rx2, #rx3", {opacity:0}, 0);')
J(f'tl.fromTo("#rx", {{opacity:0, x:200}}, {{opacity:1, x:0, duration:0.4, ease:"power3.out", immediateRender:false}}, {F(14) + 0.3:.2f}); tl.to("#rx", {{opacity:0, duration:0.25}}, {FE(14) + 0.3:.2f});')
for i, w in enumerate(("pulmon", "boca", "corazon")):
    J(f'tl.to("#rx{i + 1}", {{opacity:1, duration:0.2}}, {P(w) - 0.1:.2f});')
    fx("pop", P(w))
J(f'tl.fromTo("#rxCor", {{scale:1, svgOrigin:"160 230"}}, {{scale:1.25, svgOrigin:"160 230", duration:0.25, yoyo:true, repeat:5, immediateRender:false}}, {P("corazon"):.2f});')
# 15-17) comparativa final: lo peor de cada uno
ancho(F(15) - 0.1, 0.5)
def lista(cid, titulo, items, y, color, t0, palabras, hasta):
    lis = "".join(f'<li id="{cid}{i}">✗ {it}</li>' for i, it in enumerate(items))
    FXL.append(f'<div id="{cid}" class="lista" style="top:{y}px;border-color:{color}"><b style="color:{color}">{titulo}</b><ul>{lis}</ul></div>')
    J(f'tl.set("#{cid}", {{opacity:0}}, 0); tl.fromTo("#{cid}", {{opacity:0, x:-120}}, {{opacity:1, x:0, duration:0.35, ease:"power3.out", immediateRender:false}}, {t0:.2f}); tl.to("#{cid}", {{opacity:0, duration:0.3}}, {hasta:.2f});')
    for i, w in enumerate(palabras):
        J(f'tl.set("#{cid}{i}", {{opacity:0}}, 0); tl.fromTo("#{cid}{i}", {{opacity:0, x:40}}, {{opacity:1, x:0, duration:0.25, ease:"back.out(2)", immediateRender:false}}, {w - 0.1:.2f});')
        fx("pop", w)
lista("lB", "LO PEOR DEL TABACO", ["Muchos más cigarrillos", "Dientes y dedos amarillos", "Riesgos de cáncer más estudiados"], 1240, "#ff9a5a", F(15) - 0.1,
      [P("cigarrillos", 4), P("amarillos", 2), P("estudiados")], F(18) + 0.2)
lista("lA", "LO PEOR DE LA CACHIMBA", ["Muchísimo más humo", "Monóxido de carbono", "Boquillas compartidas", "La cartera vacía"], 600, LI, F(16) - 0.1,
      [P("muchisimo"), P("monoxido", 2), P("boquillas"), P("cartera")], F(18) + 0.2)
# 17) nicotina: cadena que une a los dos
FXL.append('<div id="cadena" class="cadena">⛓️ NICOTINA ⛓️<small>LOS DOS SON ADICTOS</small></div>')
J('tl.set("#cadena", {opacity:0}, 0);')
J(f'tl.fromTo("#cadena", {{opacity:0, scaleX:0.2}}, {{opacity:1, scaleX:1, duration:0.4, ease:"back.out(1.6)", immediateRender:false}}, {P("nicotina") - 0.2:.2f}); tl.to("#cadena", {{opacity:0, duration:0.25}}, {F(18) + 0.2:.2f});')
fx("golpe", P("nicotina"))
# 18) ninguno gana: balanza
FXL.append('<div id="balanza" class="balanza"><svg viewBox="0 0 400 220" width="640" height="352"><path d="M200,40 L200,200 M150,200 L250,200" stroke="#e9e2cf" stroke-width="8" stroke-linecap="round"/>'
           '<g id="brazo"><path d="M60,50 L340,50" stroke="#e9e2cf" stroke-width="8" stroke-linecap="round"/><path d="M60,50 L30,120 L90,120 Z M340,50 L310,120 L370,120 Z" fill="none" stroke="#e9e2cf" stroke-width="4"/>'
           '<rect x="22" y="120" width="76" height="12" rx="4" fill="#ff9a5a"/><rect x="302" y="120" width="76" height="12" rx="4" fill="#b98cff"/>'
           '<text x="60" y="160" text-anchor="middle" font-family="Inter" font-weight="900" font-size="20" fill="#ff9a5a">TABACO</text><text x="340" y="160" text-anchor="middle" font-family="Inter" font-weight="900" font-size="20" fill="#b98cff">CACHIMBA</text></g></svg></div>')
J('tl.set("#balanza", {opacity:0}, 0);')
J(f'tl.to("#balanza", {{opacity:1, duration:0.3}}, {F(18) + 0.2:.2f}); tl.fromTo("#brazo", {{rotation:-12, svgOrigin:"200 50"}}, {{keyframes:[{{rotation:10, duration:0.6}}, {{rotation:-6, duration:0.5}}, {{rotation:0, duration:0.5}}], ease:"sine.inOut", immediateRender:false}}, {F(18) + 0.2:.2f}); tl.to("#balanza", {{opacity:0, duration:0.3}}, {PL("suave") - 0.3:.2f});')
slam("sNing", 'NINGUNO GANA', P("ninguno") - 0.1, PL("suave") - 0.3, y=1320, cls="slam ama")
slam("sOtra", 'NO ES LA OPCIÓN SUAVE<small>ES OTRA FORMA DE FUMAR</small>', PL("suave") - 0.3, FE(18) + 0.25, y=1060, cls="slam rojo")
# 19) cierre y rebobinado al año 0 (el último fotograma = el primero)
FXL.append('<div id="rebob" class="rebob">◀◀ AÑO 0</div>')
J(f'tl.set("#rebob", {{opacity:0}}, 0); tl.to("#rebob", {{opacity:1, duration:0.15}}, {R0:.2f}); tl.to("#rebob", {{opacity:0, duration:0.3}}, {R1:.2f});')
fx("rebobina", R0)
slam("sSolo", '«SOLO ES UNA CACHIMBA»', P("solo", 2) - 0.2, P("amigos", 2) - 0.3, y=1105, cls="slam lila", son="pop") if False else None
J(f'tl.fromTo("#sQuien", {{opacity:0, scale:1.6, rotation:-6}}, {{opacity:1, scale:1, rotation:-3, duration:0.4, ease:"back.out(2)", immediateRender:false}}, {DUR - 1.0:.2f});')
# pulso y cámara en mano
J(f'tl.fromTo("#shake", {{x:-4, y:3}}, {{x:4, y:-3, duration:2.6, yoyo:true, repeat:{int(DUR / 2.6)}, ease:"sine.inOut", immediateRender:false}}, 0);')

# ------------------------------------------------------------------ montaje
svg = (f'<g clip-path="url(#clipA)">{"".join(A)}{figA}</g>'
       f'<g clip-path="url(#clipB)">{"".join(B)}{figB}</g>'
       f'<rect x="0" y="{AY1}" width="1080" height="{BY0 - AY1}" fill="#0a0716"/>')
_S = open(os.path.join(BASE, "_subs.py"), encoding="utf-8").read()
exec(re.sub(r"CLAVE = set\(.*?\]\)", lambda m: 'CLAVE = set(norm(w) for w in ["cachimbas", "paquete", "diez", "peor", "suave", "filtra", "spoiler", "oms", "cien", "toxicos", "hondo", "monoxido", "urgencias", "tres", "tosen", "escaleras", "cinco", "dientes", "amarillos", "encias", "cuentas", "setenta", "paquetes", "veinte", "sesiones", "ochenta", "cuatro", "horas", "meses", "volumen", "setecientos", "minutos", "medio", "pulmon", "boca", "corazon", "estudiados", "muchisimo", "boquillas", "cartera", "nicotina", "adictos", "ninguno", "fumar", "cachimba"])', _S, count=1, flags=re.S))

html = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#0a0716}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter, sans-serif;background:#0a0716;color:{TX}}}
#imp,#shake{{position:absolute;inset:0}} #cam{{position:absolute;left:0;top:0;width:1080px;height:1920px;transform-origin:0 0}}
#fxl{{position:absolute;inset:0;z-index:58;pointer-events:none}}
.ptag{{position:absolute;left:24px;padding:8px 16px;border-radius:12px;background:rgba(10,6,22,0.8);border-left:6px solid;font:900 30px Inter;letter-spacing:1px;color:#fff}}
.pcont{{position:absolute;left:24px;padding:8px 14px;border-radius:12px;background:rgba(10,6,22,0.7);font:800 26px Inter;color:#fff;font-variant-numeric:tabular-nums}}
.pcont small{{font:700 18px Inter;color:#c9b9e6;margin-right:12px}} .pcont .eur{{color:{AM}}}
.pulm{{position:absolute;right:20px;width:150px;padding:8px;border-radius:14px;background:rgba(10,6,22,0.7);text-align:center}}
.pulm small{{display:block;font:800 14px Inter;letter-spacing:3px;color:#c9b9e6}} .al{{height:10px;border-radius:5px;background:rgba(255,255,255,0.15);overflow:hidden;margin-top:4px}} .al i{{display:block;height:100%;width:100%;background:{VE}}}
#anio{{position:absolute;left:340px;right:340px;top:1132px;height:46px;display:flex;align-items:center;gap:12px;z-index:5}} #anio small{{font:800 18px Inter;letter-spacing:4px;color:#c9b9e6}}
#anio b{{font:900 36px Inter;color:{AM};width:46px;text-align:center}} #anio .barra{{flex:1;height:12px;border-radius:6px;background:rgba(255,255,255,0.15);overflow:hidden}} #anio .barra i{{display:block;height:100%;width:0;background:{AM}}}
.slam{{position:absolute;left:0;right:0;margin:0 auto;width:max-content;max-width:1000px;padding:10px 28px;border-radius:18px;background:rgba(10,6,22,0.85);border:3px solid #fff;text-align:center;font:900 76px/1.04 Inter;letter-spacing:-2px;color:#fff;box-shadow:0 14px 40px rgba(0,0,0,0.45)}}
.slam small{{display:block;margin-top:6px;font:800 24px Inter;letter-spacing:5px;color:#e6dcff}} .slam b{{font-variant-numeric:tabular-nums}}
.slam.rojo{{border-color:{RJ};color:{RJ}}} .slam.ama{{border-color:{AM};color:{AM}}} .slam.az{{border-color:{CY_};color:{CY_}}} .slam.lila{{border-color:{LI};color:{LI}}}
.cien{{position:absolute;left:110px;top:640px;width:860px;height:520px;padding:14px;border-radius:20px;background:rgba(10,6,22,0.85)}}
.cien i{{position:absolute;width:70px;height:16px;margin:16px 0 0 18px;border-radius:4px;background:linear-gradient(90deg,#f4f1e2 72%,#ffb35c 72%)}}
.cien b{{position:absolute;left:0;right:0;bottom:16px;text-align:center;font:900 40px Inter;color:{LI}}}
#sirena{{position:absolute;inset:0;background:linear-gradient(90deg, rgba(255,40,40,0.35), rgba(0,0,0,0) 30%, rgba(0,0,0,0) 70%, rgba(40,90,255,0.35));background-size:200% 100%;mix-blend-mode:screen}}
.tot{{position:absolute;left:40px;right:40px;display:flex;justify-content:space-around;padding:18px;border-radius:20px;background:rgba(10,6,22,0.88);border:3px solid {AM}}}
.tot div{{text-align:center}} .tot b{{display:block;font:900 64px Inter;color:#fff;font-variant-numeric:tabular-nums}} .tot .eurb{{color:{AM}}} .tot small{{font:800 20px Inter;letter-spacing:4px;color:#c9b9e6}}
.reloj{{position:absolute;right:60px;top:1220px}}
.rx{{position:absolute;right:30px;top:560px;width:360px;text-align:center}} .rx small{{display:inline-block;margin:6px 6px 0;padding:4px 10px;border-radius:8px;background:{RJ};font:900 20px Inter;color:#fff}}
.lista{{position:absolute;left:40px;right:40px;padding:16px 24px;border-radius:20px;background:rgba(10,6,22,0.9);border:3px solid}} .lista b{{display:block;font:900 40px Inter;margin-bottom:8px}}
.lista ul{{list-style:none}} .lista li{{font:800 36px/1.35 Inter;color:#fff}}
.cadena{{position:absolute;left:0;right:0;top:1060px;margin:0 auto;width:max-content;padding:12px 30px;border-radius:20px;background:rgba(10,6,22,0.92);border:3px solid {RJ};font:900 64px Inter;color:#fff;text-align:center}} .cadena small{{display:block;font:800 22px Inter;letter-spacing:5px;color:{RJ}}}
.balanza{{position:absolute;left:220px;top:700px}}
.rebob{{position:absolute;left:0;right:0;top:1060px;text-align:center;font:900 110px Inter;color:#fff;text-shadow:0 6px 24px rgba(0,0,0,0.7)}}
#grano{{position:absolute;inset:0;z-index:57;pointer-events:none;opacity:0.035;background:url(assets/grano.png);mix-blend-mode:overlay}}
#vineta{{position:absolute;inset:0;z-index:56;pointer-events:none;background:radial-gradient(115% 85% at 50% 58%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.45))}}
#topsombra{{position:absolute;left:0;right:0;top:0;height:520px;z-index:55;pointer-events:none;background:linear-gradient(rgba(6,3,14,0.92), rgba(6,3,14,0.5))}}
#marca{{position:absolute;left:0;right:0;top:1820px;text-align:center;font:700 28px Inter;color:#ffffff;opacity:0.32;pointer-events:none;z-index:61}}
#subs{{position:absolute;left:60px;right:60px;top:250px;height:220px;z-index:62}}
.sub{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 62px Inter;color:rgba(255,255,255,0.42);line-height:1.22;text-shadow:0 3px 12px rgba(0,0,0,0.6)}}
.sw{{display:inline-block;position:relative;padding:0 6px;margin:0 1px}}
.key .hl{{position:absolute;inset:-4px -2px -2px -2px;border:3px solid #4ea3ff;border-radius:6px;background:rgba(78,163,255,0.18);opacity:0}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <div id="imp"><div id="shake"><div id="cam"><svg width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0"><defs>{"".join(DEFS)}</defs>{svg}</svg>
  {UI}</div></div></div>
  <div id="fxl">{"".join(FXL)}</div>
  <div id="topsombra"></div><div id="vineta"></div><div id="grano"></div>
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
json.dump([[0, 0.2], [DUR, 0.2]], open(os.path.join(BASE, "ambiente.json"), "w"))
print(f"index.html · {DUR:.1f}s · {len(tl)} animaciones")

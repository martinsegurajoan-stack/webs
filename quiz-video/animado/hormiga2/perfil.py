# Personaje DE PERFIL (mira a la derecha) con caderas, rodillas, hombros y codos: para caminar y correr.
# Mismo sistema de coordenadas que el de frente (svg 1000x1800, pies en y=1702, centro x=500).
def perfil(pid):
    sk, skd = SKIN, SKIN_D
    def pierna(n, col, zap):
        return (f'<g id="{pid}-pT{n}"><path d="M468,1262 L536,1262 L530,1488 L476,1488 Z" fill="{col}"/>'
                f'<g id="{pid}-pS{n}"><circle cx="503" cy="1484" r="27" fill="{col}"/><path d="M478,1480 L528,1480 L522,1684 L484,1684 Z" fill="{col}"/>'
                f'<path d="M474,1676 L548,1676 C584,1676 600,1692 596,1702 L470,1702 Z" fill="{zap}"/><rect x="468" y="1696" width="132" height="10" rx="5" fill="#cfc6b8"/></g></g>')
    def brazo(n, manga, piel):
        return (f'<g id="{pid}-pA{n}"><path d="M482,972 C482,952 530,950 532,972 L528,1122 L486,1122 Z" fill="{manga}"/>'
                f'<g id="{pid}-pF{n}"><circle cx="507" cy="1120" r="20" fill="{piel}"/><path d="M490,1118 L526,1118 L520,1256 L494,1256 Z" fill="{piel}"/>'
                f'<circle cx="507" cy="1272" r="26" fill="{piel}"/></g></g>')
    s = [f'<svg class="pj" id="{pid}-perf" viewBox="0 0 1000 1800" width="1000" height="1800" style="position:absolute;left:0;top:0;overflow:visible;opacity:0">',
         f'<g id="{pid}-perfG"><ellipse cx="510" cy="1702" rx="150" ry="22" fill="#000" opacity="0.22"/><g id="{pid}-perfUp">',
         pierna("F", "#2f3250", "#dcd5c8"), brazo("F", SHIRT_D, skd),
         f'<path d="M444,968 C444,944 560,938 572,964 L582,1272 L438,1272 Z" fill="url(#{pid}-shirt)"/>',
         f'<path d="M548,950 C566,955 572,960 572,964 L582,1272 L548,1272 Z" fill="#b5553f" opacity="0.3"/>',
         f'<path d="M438,1250 L582,1250 L580,1300 L440,1300 Z" fill="{PANTS}"/>',
         pierna("N", PANTS, "#f4efe6"),
         f'<rect x="482" y="868" width="50" height="96" rx="18" fill="{skd}"/>',
         f'<g id="{pid}-pHead"><g transform="{HEADSC}">',
         f'<path d="M420,770 C420,690 470,650 530,650 C595,650 625,700 625,760 L642,788 C646,798 636,802 626,802 C622,842 600,880 560,892 C520,900 470,886 450,860 C430,835 420,805 420,770 Z" fill="url(#{pid}-skin)"/>',
         f'<path id="{pid}-pAzul" d="M420,770 C420,690 470,650 530,650 C595,650 625,700 625,760 L642,788 C646,798 636,802 626,802 C622,842 600,880 560,892 C520,900 470,886 450,860 C430,835 420,805 420,770 Z" fill="#7cc8ff" opacity="0"/>',
         f'<ellipse cx="486" cy="778" rx="16" ry="24" fill="{skd}"/>',
         f'<g id="{pid}-pEye"><ellipse cx="574" cy="746" rx="12" ry="12" fill="#fbf6f0"/><circle cx="579" cy="747" r="6.5" fill="#2a1d16"/><circle cx="581" cy="744" r="2" fill="#fff"/></g>',
         f'<path d="M558,724 Q577,714 597,722" stroke="#4a2f22" stroke-width="7" fill="none" stroke-linecap="round"/>',
         f'<path id="{pid}-pMouth" d="M588,826 Q602,834 614,824" stroke="#7a3f35" stroke-width="4.5" fill="none" stroke-linecap="round"/>',
         f'<path d="M416,772 C408,690 458,636 530,636 C592,636 628,668 630,714 C602,700 572,704 548,712 C524,700 502,708 494,732 C474,742 460,760 456,802 C440,802 422,792 416,772 Z" fill="url(#{pid}-hair)"/>',
         f'<path id="{pid}-pSudor" d="M612,690 C622,708 628,720 628,730 C628,742 618,748 610,748 C602,748 594,742 594,730 C594,720 602,708 612,690 Z" fill="#8fd8ff" stroke="#3a9ad9" stroke-width="3" opacity="0"/>',
         '</g></g>', brazo("N", "url(#" + pid + "-shirt)", sk), '</g></g></svg>']
    return "".join(s)

def a_perfil(pid, t, izquierda=False):
    J(f'tl.set("#{pid}", {{opacity:0}}, {t:.2f}); tl.set("#{pid}-perf", {{opacity:1}}, {t:.2f}); tl.set("#{pid}-perfG", {{scaleX:{-1 if izquierda else 1}, svgOrigin:"500 0"}}, {t:.2f});')

def a_frente(pid, t):
    J(f'tl.set("#{pid}", {{opacity:1}}, {t:.2f}); tl.set("#{pid}-perf", {{opacity:0}}, {t:.2f});')

def caminar_perfil(pid, t, dx, dur, pasos, correr=False, volver=True):
    """Camina (o corre) DE PERFIL: caderas, rodillas, brazos y codos con ciclo de paso real."""
    a_perfil(pid, t, izquierda=dx < 0)
    J(f'tl.to("#{pid}-w", {{x:"+={dx}", duration:{dur}, ease:"none"}}, {t:.2f});')
    ciclos = max(1, round(pasos / 2))
    c = dur / ciclos
    amp, rod, br = (34, 70, 45) if correr else (24, 42, 26)
    for n, s in (("N", 1), ("F", -1)):
        J(f'tl.to("#{pid}-pT{n}", {{keyframes:{{rotation:[{-amp * s}, {amp * s}, {-amp * s}], easeEach:"sine.inOut"}}, duration:{c:.3f}, repeat:{ciclos - 1}, ease:"none", svgOrigin:"502 1268"}}, {t:.2f});')
        J(f'tl.to("#{pid}-pS{n}", {{keyframes:{{rotation:[{5 if s > 0 else rod}, {rod if s > 0 else 5}, {5 if s > 0 else rod}], easeEach:"sine.inOut"}}, duration:{c:.3f}, repeat:{ciclos - 1}, ease:"none", svgOrigin:"503 1484"}}, {t:.2f});')
        J(f'tl.to("#{pid}-pA{n}", {{keyframes:{{rotation:[{br * s}, {-br * s}, {br * s}], easeEach:"sine.inOut"}}, duration:{c:.3f}, repeat:{ciclos - 1}, ease:"none", svgOrigin:"507 975"}}, {t:.2f});')
        J(f'tl.to("#{pid}-pF{n}", {{keyframes:{{rotation:[-20, {-50 if correr else -35}, -20], easeEach:"sine.inOut"}}, duration:{c:.3f}, repeat:{ciclos - 1}, ease:"none", svgOrigin:"507 1120"}}, {t:.2f});')
    J(f'tl.to("#{pid}-perfUp", {{keyframes:{{y:[0, -14, 0, -14, 0]}}, rotation:{8 if correr else 2}, duration:{c:.3f}, repeat:{ciclos - 1}, ease:"none", svgOrigin:"500 1290"}}, {t:.2f});')
    J(f'tl.to("#{pid}-pHead", {{keyframes:{{rotation:[0, 3, 0, -3, 0]}}, duration:{c:.3f}, repeat:{ciclos - 1}, ease:"none", svgOrigin:"505 880"}}, {t:.2f});')
    if volver:
        J(f'tl.set(["#{pid}-pTN", "#{pid}-pTF", "#{pid}-pSN", "#{pid}-pSF", "#{pid}-pAN", "#{pid}-pAF", "#{pid}-pFN", "#{pid}-pFF", "#{pid}-perfUp"], {{rotation:0, y:0}}, {t + dur:.2f});')
        a_frente(pid, t + dur)

# ---------------- expresiones (cara de frente)
def cara(pid, t, tipo, hold=None):
    """Cambia la expresión: sorpresa, miedo, feliz, frio, esfuerzo, normal."""
    out = []
    if tipo in ("sorpresa", "miedo"):
        out += [f'tl.to("#{pid}-eyes", {{scaleY:1.4, duration:0.15, svgOrigin:"500 742"}}, {t:.2f})', f'tl.to("#{pid}-mouthO", {{opacity:1, duration:0.12}}, {t:.2f})',
                f'tl.to("#{pid}-mouth", {{opacity:0, duration:0.12}}, {t:.2f})', f'tl.to("#{pid}-brows", {{y:-16, duration:0.18}}, {t:.2f})']
        if tipo == "miedo":
            out += [f'tl.fromTo("#{pid}-sudor", {{opacity:0, y:-10}}, {{opacity:1, y:30, duration:0.9, immediateRender:false}}, {t + 0.1:.2f})',
                    f'tl.to("#{pid}-legs", {{x:3, duration:0.05, yoyo:true, repeat:15}}, {t:.2f})']
    if tipo == "feliz":
        out += [f'tl.to("#{pid}-mouth", {{attr:{{d:"M472,812 Q500,846 528,812"}}, duration:0.25}}, {t:.2f})', f'tl.to("#{pid}-rubor", {{opacity:1, duration:0.3}}, {t:.2f})',
                f'tl.to("#{pid}-eyes", {{scaleY:0.75, duration:0.2, svgOrigin:"500 742"}}, {t:.2f})', f'tl.to("#{pid}-brows", {{y:-8, duration:0.2}}, {t:.2f})']
    if tipo == "esfuerzo":
        out += [f'tl.to("#{pid}-dientes", {{opacity:1, duration:0.15}}, {t:.2f})', f'tl.to("#{pid}-mouth", {{opacity:0, duration:0.1}}, {t:.2f})',
                f'tl.to("#{pid}-rubor", {{opacity:1, duration:0.3}}, {t:.2f})', f'tl.to("#{pid}-brows", {{y:6, duration:0.2}}, {t:.2f})']
    if tipo == "frio":
        out += [f'tl.to("#{pid}-azul", {{opacity:0.75, duration:0.6}}, {t:.2f})', f'tl.to("#{pid}-dientes", {{opacity:1, duration:0.15}}, {t:.2f})',
                f'tl.to("#{pid}-mouth", {{opacity:0, duration:0.1}}, {t:.2f})', f'tl.to("#{pid}-dientes", {{y:3, duration:0.06, yoyo:true, repeat:40}}, {t:.2f})',
                f'tl.to("#{pid}-brows", {{y:-6, rotation:4, duration:0.2, svgOrigin:"500 715"}}, {t:.2f})']
    for s in out:
        J(s + ";")
    if hold is not None:
        normal(pid, t + hold)

def normal(pid, t):
    J(f'tl.to("#{pid}-eyes", {{scaleY:1, duration:0.2, svgOrigin:"500 742"}}, {t:.2f}); tl.to("#{pid}-mouthO", {{opacity:0, duration:0.15}}, {t:.2f}); tl.to("#{pid}-mouth", {{opacity:1, attr:{{d:"M478,816 Q500,832 522,816"}}, duration:0.2}}, {t:.2f});')
    J(f'tl.to(["#{pid}-dientes", "#{pid}-sudor", "#{pid}-rubor", "#{pid}-azul"], {{opacity:0, duration:0.3}}, {t:.2f}); tl.to("#{pid}-brows", {{y:0, rotation:0, duration:0.2, svgOrigin:"500 715"}}, {t:.2f});')

def pose(pid, t, armL=0, armR=0, foreL=0, foreR=0, dur=0.35, ease="back.out(1.4)"):
    J(f'tl.to("#{pid}-armLg", {{rotation:{armL}, duration:{dur}, ease:"{ease}", svgOrigin:"356 985"}}, {t:.2f}); tl.to("#{pid}-armRg", {{rotation:{armR}, duration:{dur}, ease:"{ease}", svgOrigin:"644 985"}}, {t:.2f});')
    J(f'tl.to("#{pid}-foreL", {{rotation:{foreL}, duration:{dur}, ease:"{ease}", svgOrigin:"331 1116"}}, {t:.2f}); tl.to("#{pid}-foreR", {{rotation:{foreR}, duration:{dur}, ease:"{ease}", svgOrigin:"669 1116"}}, {t:.2f});')

def cabeza(pid, t, rot, dur=0.35):
    J(f'tl.to("#{pid}-headw", {{rotation:{rot}, duration:{dur}, ease:"power2.inOut", svgOrigin:"500 900"}}, {t:.2f});')

def salto(pid, t, h=60, dur=0.45):
    J(f'tl.to("#{pid}-w", {{y:"-={h * 0.085:.1f}", duration:{dur / 2:.2f}, ease:"power2.out", yoyo:true, repeat:1}}, {t:.2f});')

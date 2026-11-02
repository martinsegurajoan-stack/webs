# CASA COMPLETA para los planos abiertos: planta de arriba (5 habitaciones), BUHARDILLA con tejado de tejas,
# chimenea con humo, SÓTANO (garaje, trastero, lavadero, sala de ping-pong) y JARDINES a los lados.
# Escala: una persona ~1000 px. Planta de arriba: suelo (pies) en y=-230, techo en -1800. Sótano: pies en 3480.
UF, UT = -230, -1800          # suelo y techo de la planta de arriba
BF, BT = 3480, 1970           # suelo y techo del sótano
rx = random.Random(21)

DEFX = ('<svg width="0" height="0" style="position:absolute"><defs>'
        '<linearGradient id="uBano" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a8ecff"/><stop offset="1" stop-color="#5cc8f0"/></linearGradient>'
        '<linearGradient id="uNino" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd6e8"/><stop offset="1" stop-color="#ff9fc8"/></linearGradient>'
        '<linearGradient id="uOfi" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c8f7c5"/><stop offset="1" stop-color="#7ddc7a"/></linearGradient>'
        '<linearGradient id="uMus" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd49e"/><stop offset="1" stop-color="#ffa94d"/></linearGradient>'
        '<linearGradient id="uJue" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a2f8f"/><stop offset="1" stop-color="#1d1652"/></linearGradient>'
        '<linearGradient id="bSot" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9fb0c8"/><stop offset="1" stop-color="#76869e"/></linearGradient>'
        '<linearGradient id="buh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e8b884"/><stop offset="1" stop-color="#c98f58"/></linearGradient>'
        '<pattern id="tejas" width="140" height="70" patternUnits="userSpaceOnUse"><rect width="140" height="70" fill="#e2483d"/><path d="M0,70 Q35,20 70,70 Q105,20 140,70" fill="#c93a31"/><path d="M0,70 Q35,30 70,70" stroke="#ff7a6b" stroke-width="5" fill="none" opacity="0.6"/></pattern>'
        '<pattern id="ladrillo" width="160" height="80" patternUnits="userSpaceOnUse"><rect width="160" height="80" fill="none"/><path d="M0,40 L160,40 M0,80 L160,80 M80,0 L80,40 M0,40 L0,80 M160,40 L160,80" stroke="#ffffff" stroke-width="4" opacity="0.18"/></pattern>'
        '<pattern id="tablon" width="300" height="1" patternUnits="userSpaceOnUse"><rect width="300" height="1" fill="none"/><rect x="0" width="4" height="1" fill="#9a6a3c" opacity="0.5"/></pattern>'
        '</defs></svg>')
H.append(DEFX)

def sala_up(x0, x1, grad, papel=None, op=0.4, suelo="url(#suelo)"):
    w = x1 - x0
    s = f'<rect x="{x0}" y="{UT}" width="{w}" height="{UF - UT}" fill="url(#{grad})"/>'
    if papel:
        s += f'<rect x="{x0}" y="{UT}" width="{w}" height="{UF - UT}" fill="url(#{papel})" opacity="{op}"/>'
    s += (f'<rect x="{x0}" y="{UT}" width="{w}" height="30" fill="#fff6ea"/><rect x="{x0}" y="{UF - 44}" width="{w}" height="44" fill="#fff6ea"/>'
          f'<rect x="{x0}" y="{UF}" width="{w}" height="170" fill="{suelo}"/><rect x="{x0}" y="{UF}" width="{w}" height="170" fill="url(#tablas)" opacity="0.8"/>'
          f'<rect x="{x0}" y="{UF}" width="{w}" height="8" fill="#000" opacity="0.12"/>')
    return s

def tabique_up(x):
    return (f'<rect x="{x - 40}" y="{UT}" width="80" height="560" fill="#fff1dc"/><rect x="{x - 56}" y="{UT + 560}" width="16" height="{UF - UT - 560}" fill="#fbe8cf"/>'
            f'<rect x="{x + 40}" y="{UT + 560}" width="16" height="{UF - UT - 560}" fill="#fbe8cf"/>')

def ventana_up(x, y, w, h, cort="#ffd23f"):
    return ventana2(x, y, w, h, cielo="cieloDia", cortina=cort)

up = ""
# ---------------- BAÑO (0-2600)
up += sala_up(0, 2600, "uBano")
up += f'<rect x="0" y="-900" width="2600" height="{UF - 44 + 900}" fill="url(#azulejo)" opacity="0.9"/>'
up += ventana_up(620, -1560, 420, 440, "#06d6a0")
up += ('<path d="M300,-700 L1300,-700 L1300,-560 C1300,-380 1180,-330 1020,-330 L580,-330 C420,-330 300,-380 300,-560 Z" fill="#ffffff"/>'
       '<rect x="280" y="-720" width="1040" height="40" rx="20" fill="#f0f4fa"/><path d="M420,-330 L390,-240 M1180,-330 L1210,-240" stroke="#ffd23f" stroke-width="30" stroke-linecap="round"/>'
       '<path d="M1300,-700 L1300,-1000 C1300,-1060 1220,-1070 1200,-1020" stroke="url(#metal)" stroke-width="22" fill="none" stroke-linecap="round"/>')
up += "".join(f'<circle class="burbuja" cx="{x}" cy="{y}" r="{r}" fill="#ffffff" stroke="#bfe8ff" stroke-width="4"/>' for x, y, r in ((420, -760, 50), (520, -790, 70), (650, -760, 45), (760, -800, 60), (880, -770, 40), (1000, -790, 66), (1120, -760, 48), (1220, -780, 40)))
up += '<g id="pato"><ellipse cx="900" cy="-820" rx="60" ry="40" fill="#ffd23f"/><circle cx="950" cy="-870" r="34" fill="#ffd23f"/><path d="M980,-868 L1010,-860 L980,-852 Z" fill="#ff9f1c"/><circle cx="958" cy="-878" r="6" fill="#2b2d42"/></g>'
up += ('<rect x="1500" y="-900" width="200" height="230" rx="20" fill="#ffffff"/><ellipse cx="1610" cy="-560" rx="170" ry="60" fill="#ffffff"/><path d="M1460,-560 C1470,-430 1520,-380 1600,-380 L1640,-230 L1560,-230 L1560,-380" fill="#f0f4fa"/>'
       '<rect x="1520" y="-940" width="160" height="40" rx="10" fill="#e3e8f0"/>')
up += ('<rect x="2050" y="-640" width="300" height="60" rx="20" fill="#ffffff"/><rect x="2160" y="-580" width="80" height="350" fill="#f0f4fa"/><path d="M2200,-640 L2200,-720 L2250,-720" stroke="url(#metal)" stroke-width="16" fill="none"/>'
       '<ellipse cx="2200" cy="-1050" rx="170" ry="230" fill="#ffd23f"/><ellipse cx="2200" cy="-1050" rx="145" ry="205" fill="#d9f6ff"/><path d="M2120,-1160 L2180,-1200 M2110,-1100 L2230,-1180" stroke="#ffffff" stroke-width="14" stroke-linecap="round"/>')
up += '<rect x="1380" y="-1320" width="320" height="16" rx="8" fill="#9fb3c8"/>' + "".join(f'<rect x="{x}" y="-1305" width="90" height="300" rx="14" fill="{c}"/><rect x="{x}" y="-1250" width="90" height="16" fill="#ffffff" opacity="0.6"/>' for x, c in ((1390, "#ff5d8f"), (1490, "#3a86ff"), (1590, "#ffd23f")))
up += maceta(2480, -340, 0.8, "#ff5d8f") + '<rect x="1450" y="-250" width="400" height="30" rx="14" fill="#ff5d8f"/>'

# ---------------- HABITACIÓN INFANTIL (2600-4800)
up += sala_up(2600, 4800, "uNino", "papelBed", 0.35)
up += ventana_up(4180, -1560, 420, 460, "#3a86ff")
up += ('<rect x="2760" y="-1300" width="40" height="1070" fill="#7a4b2a"/><rect x="3640" y="-1300" width="40" height="1070" fill="#7a4b2a"/>'
       '<rect x="2780" y="-1040" width="880" height="90" rx="14" fill="#ffffff"/><rect x="2900" y="-1080" width="760" height="80" rx="20" fill="#3a86ff"/><ellipse cx="2880" cy="-1070" rx="90" ry="36" fill="#ffffff"/>'
       '<rect x="2780" y="-520" width="880" height="90" rx="14" fill="#ffffff"/><rect x="2900" y="-560" width="760" height="80" rx="20" fill="#ff5d8f"/><ellipse cx="2880" cy="-550" rx="90" ry="36" fill="#ffffff"/>'
       '<rect x="2780" y="-430" width="880" height="40" fill="#7a4b2a"/><rect x="2780" y="-950" width="880" height="34" fill="#7a4b2a"/>'
       '<path d="M3600,-960 L3600,-430 M3520,-960 L3520,-430" stroke="#c97b45" stroke-width="14"/>' + "".join(f'<path d="M3520,{y} L3600,{y}" stroke="#c97b45" stroke-width="12"/>' for y in (-880, -790, -700, -610, -520)))
up += marco(2760, -1650, 280, 220, '<rect x="2774" y="-1636" width="252" height="192" fill="#2b2d6e"/><circle cx="2860" cy="-1560" r="40" fill="#ffd23f"/><circle cx="2960" cy="-1500" r="22" fill="#ff5d8f"/>', "#06d6a0")
up += '<g id="movil">' + '<path d="M3900,-1770 L3900,-1600 M3760,-1600 L4040,-1600" stroke="#3b2f2f" stroke-width="6"/>' + "".join(f'<path d="M{x},-1600 L{x},{y}" stroke="#3b2f2f" stroke-width="4"/><circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for x, y, r, c in ((3770, -1450, 40, "#ffd23f"), (3900, -1400, 55, "#ff5d8f"), (4030, -1470, 35, "#06d6a0"))) + '</g>'
up += ('<rect x="3820" y="-560" width="380" height="330" rx="20" fill="#ff9f1c"/><rect x="3820" y="-560" width="380" height="50" rx="20" fill="#ffbf5a"/>'
       '<circle cx="3900" cy="-620" r="70" fill="#ef233c"/><path d="M3840,-640 C3880,-600 3930,-600 3960,-640" stroke="#ffffff" stroke-width="10" fill="none"/>'
       '<circle cx="4090" cy="-640" r="60" fill="#c97b45"/><circle cx="4050" cy="-700" r="26" fill="#c97b45"/><circle cx="4130" cy="-700" r="26" fill="#c97b45"/><circle cx="4070" cy="-650" r="6" fill="#2b2d42"/><circle cx="4110" cy="-650" r="6" fill="#2b2d42"/>'
       '<ellipse cx="3700" cy="-180" rx="420" ry="40" fill="#8ac926"/>'
       '<path d="M4500,-230 L4500,-500 L4560,-560 L4620,-500 L4620,-230 Z" fill="#ffffff"/><path d="M4500,-500 L4560,-620 L4620,-500 Z" fill="#ef233c"/><circle cx="4560" cy="-420" r="22" fill="#5ac8fa"/>')

# ---------------- DESPACHO (4800-7000)
up += sala_up(4800, 7000, "uOfi", "papelHall", 0.35)
up += ('<rect x="5000" y="-1520" width="560" height="380" rx="10" fill="#c97b45"/><rect x="5016" y="-1504" width="528" height="348" fill="#e8b884"/>'
       + "".join(f'<rect x="{x}" y="{y}" width="110" height="90" fill="{c}" transform="rotate({a} {x + 55} {y + 45})"/>' for x, y, c, a in ((5050, -1480, "#ffd23f", -4), (5200, -1460, "#ff5d8f", 5), (5360, -1470, "#06d6a0", -3), (5110, -1330, "#3a86ff", 3), (5300, -1320, "#ffffff", -5)))
       + '<rect x="5200" y="-720" width="1000" height="40" rx="10" fill="#7a4b2a"/><rect x="5230" y="-680" width="30" height="450" fill="#5e391f"/><rect x="6140" y="-680" width="30" height="450" fill="#5e391f"/>'
       '<rect x="5480" y="-1100" width="460" height="300" rx="16" fill="#2b2d42"/><rect x="5500" y="-1080" width="420" height="260" rx="8" fill="#1d3557"/>'
       + "".join(f'<rect x="{5520 + (i % 3) * 30}" y="{-1060 + i * 22}" width="{90 + (i * 37) % 160}" height="10" rx="5" fill="{["#ffd23f", "#06d6a0", "#ff5d8f", "#3a86ff"][i % 4]}"/>' for i in range(11))
       + '<rect x="5690" y="-800" width="40" height="80" fill="#2b2d42"/><rect x="5620" y="-725" width="180" height="14" rx="6" fill="#2b2d42"/><rect x="5520" y="-740" width="300" height="20" rx="6" fill="#e3e8f0"/>'
       '<rect x="6000" y="-790" width="60" height="70" rx="10" fill="#ef476f"/><path d="M6060,-770 C6090,-770 6090,-740 6060,-740" stroke="#ef476f" stroke-width="10" fill="none"/>'
       '<path d="M5300,-720 L5260,-880 L5340,-940" stroke="#2b2d42" stroke-width="12" fill="none"/><path d="M5310,-950 L5400,-950 L5370,-900 Z" fill="#ffd23f"/>'
       '<rect x="5560" y="-560" width="300" height="60" rx="20" fill="#ff5d8f"/><rect x="5580" y="-860" width="260" height="300" rx="40" fill="#ff7aa5"/><rect x="5690" y="-500" width="40" height="200" fill="#2b2d42"/><path d="M5600,-300 L5820,-300 M5710,-300 L5710,-250" stroke="#2b2d42" stroke-width="16" stroke-linecap="round"/>'
       '<rect x="6400" y="-1500" width="500" height="1270" rx="10" fill="#7a4b2a"/>' + "".join(f'<rect x="6420" y="{y}" width="460" height="18" fill="#5e391f"/>' for y in (-1200, -900, -600))
       + libros(6430, -1200, 11, seed=11) + libros(6430, -900, 11, seed=12) + libros(6430, -600, 8, seed=13)
       + '<circle cx="6560" cy="-1290" r="70" fill="#3a86ff"/><path d="M6510,-1320 C6540,-1360 6600,-1340 6610,-1290" stroke="#8ac926" stroke-width="22" fill="none"/><rect x="6550" y="-1220" width="20" height="20" fill="#7a4b2a"/>'
       + maceta(6800, -1340, 0.5, "#ffd23f") + maceta(4960, -340, 0.8, "#3a86ff"))

# ---------------- SALA DE MÚSICA (7000-9800)
up += sala_up(7000, 9800, "uMus", "papelDin", 0.3)
up += ventana_up(8100, -1600, 400, 420, "#8338ec")
up += ('<rect x="7150" y="-950" width="820" height="720" rx="14" fill="#2b2d42"/><rect x="7150" y="-950" width="820" height="60" rx="14" fill="#3d405b"/>'
       '<rect x="7170" y="-620" width="780" height="90" fill="#ffffff"/>' + "".join(f'<rect x="{7170 + i * 39}" y="-620" width="3" height="90" fill="#bbb"/>' for i in range(20))
       + "".join(f'<rect x="{7195 + i * 39}" y="-620" width="22" height="55" fill="#1d1e2c"/>' for i in range(19) if i % 7 not in (2, 6))
       + '<rect x="7250" y="-1150" width="200" height="200" rx="10" fill="#fffaf0"/><path d="M7280,-1110 L7420,-1110 M7280,-1080 L7420,-1080 M7280,-1050 L7420,-1050 M7280,-1020 L7420,-1020" stroke="#2b2d42" stroke-width="3"/><circle cx="7320" cy="-1080" r="12" fill="#2b2d42"/><circle cx="7380" cy="-1050" r="12" fill="#2b2d42"/>'
       '<rect x="7400" y="-450" width="320" height="50" rx="16" fill="#7a4b2a"/><rect x="7420" y="-400" width="30" height="170" fill="#5e391f"/><rect x="7670" y="-400" width="30" height="170" fill="#5e391f"/>'
       # batería
       '<circle cx="8750" cy="-450" r="200" fill="#ef233c"/><circle cx="8750" cy="-450" r="160" fill="#ffffff"/><text x="8750" y="-430" text-anchor="middle" font-family="Inter" font-weight="900" font-size="64" fill="#ef233c">ROCK</text>'
       '<rect x="8420" y="-700" width="200" height="110" rx="20" fill="#ef233c"/><ellipse cx="8520" cy="-700" rx="100" ry="24" fill="#ffffff"/><rect x="8880" y="-760" width="180" height="120" rx="20" fill="#ef233c"/><ellipse cx="8970" cy="-760" rx="90" ry="22" fill="#ffffff"/>'
       '<path d="M8350,-230 L8350,-900 M9150,-230 L9150,-950" stroke="#c0c6d6" stroke-width="14"/><ellipse cx="8350" cy="-900" rx="130" ry="20" fill="#ffd23f"/><ellipse cx="9150" cy="-950" rx="140" ry="22" fill="#ffd23f"/>'
       # guitarras y discos
       + "".join(f'<g transform="translate({x} -1100) rotate({a})"><rect x="-14" y="-420" width="28" height="360" fill="#7a4b2a"/><rect x="-26" y="-470" width="52" height="70" rx="10" fill="#3b2f2f"/><path d="M0,-80 C-110,-80 -120,40 -70,90 C-110,170 -60,240 0,240 C60,240 110,170 70,90 C120,40 110,-80 0,-80 Z" fill="{c}"/><circle cx="0" cy="40" r="30" fill="#3b2f2f"/></g>' for x, a, c in ((9350, -8, "#06d6a0"), (9620, 6, "#ff9f1c")))
       + "".join(f'<circle cx="{x}" cy="-1550" r="80" fill="#1d1e2c"/><circle cx="{x}" cy="-1550" r="28" fill="{c}"/>' for x, c in ((7300, "#ff5d8f"), (7500, "#ffd23f"), (7700, "#06d6a0"))))

# ---------------- SALA DE JUEGOS (9800-12900)
up += sala_up(9800, 12900, "uJue", None, 0, suelo="#3a2f8f")
up += ('<rect x="9950" y="-1700" width="2800" height="16" rx="8" fill="#ff5d8f"/><rect x="9950" y="-1660" width="2800" height="10" rx="5" fill="#06d6a0" opacity="0.8"/>'
       '<rect x="10500" y="-1330" width="1200" height="660" rx="24" fill="#111"/><rect x="10530" y="-1300" width="1140" height="600" rx="10" fill="#4cc9f0"/>'
       '<rect x="10530" y="-860" width="1140" height="160" fill="#8ac926"/><rect x="10530" y="-880" width="1140" height="30" fill="#5a9216"/>'
       + "".join(f'<rect x="{x}" y="{y}" width="80" height="80" fill="#ff9f1c" stroke="#7a3b10" stroke-width="6"/>' for x, y in ((10800, -1080), (10880, -1080), (11300, -1150)))
       + '<rect x="10960" y="-1080" width="80" height="80" fill="#ffd23f" stroke="#7a3b10" stroke-width="6"/><text x="11000" y="-1018" text-anchor="middle" font-family="Inter" font-weight="900" font-size="54" fill="#7a3b10">?</text>'
       '<g id="heroe"><rect x="10700" y="-980" width="60" height="80" rx="10" fill="#ef233c"/><circle cx="10730" cy="-1000" r="30" fill="#ffd6b0"/><rect x="10700" y="-1040" width="66" height="22" rx="8" fill="#ef233c"/></g>'
       '<ellipse cx="11450" cy="-1200" rx="90" ry="40" fill="#ffffff"/><ellipse cx="10650" cy="-1230" rx="70" ry="30" fill="#ffffff"/>'
       '<rect x="10950" y="-670" width="300" height="30" rx="10" fill="#2b2d42"/><rect x="10700" y="-640" width="800" height="200" rx="16" fill="#3d405b"/><rect x="10760" y="-600" width="160" height="50" rx="10" fill="#111"/>'
       '<path d="M10380,-230 C10300,-230 10280,-420 10420,-450 C10560,-470 10640,-420 10640,-300 C10640,-240 10560,-230 10380,-230 Z" fill="#ff5d8f"/>'
       '<path d="M11780,-230 C11700,-230 11690,-420 11830,-450 C11970,-470 12050,-420 12050,-300 C12050,-240 11970,-230 11780,-230 Z" fill="#ffd23f"/>'
       '<path d="M10900,-330 C10980,-300 11080,-300 11150,-330 L11160,-250 C11080,-230 10980,-230 10890,-250 Z" fill="#ffffff"/><rect x="10990" y="-340" width="70" height="40" rx="10" fill="#2b2d42"/>'
       # máquina recreativa
       '<path d="M12250,-230 L12250,-1250 L12700,-1250 L12700,-230 Z" fill="#8338ec"/><rect x="12250" y="-1300" width="450" height="110" rx="14" fill="#ff5d8f"/><text x="12475" y="-1222" text-anchor="middle" font-family="Inter" font-weight="900" font-size="64" fill="#ffffff">ARCADE</text>'
       '<rect x="12300" y="-1150" width="350" height="300" rx="10" fill="#111"/><circle cx="12475" cy="-1000" r="60" fill="#ffd23f"/><path d="M12475,-1000 L12540,-1040 L12540,-960 Z" fill="#111"/>'
       '<rect x="12290" y="-820" width="370" height="90" fill="#3d405b"/><circle cx="12360" cy="-775" r="22" fill="#ef233c"/><circle cx="12440" cy="-775" r="22" fill="#06d6a0"/><rect x="12540" y="-800" width="14" height="40" fill="#111"/><circle cx="12547" cy="-805" r="18" fill="#ef233c"/>'
       '<rect x="9950" y="-1250" width="420" height="20" fill="#06d6a0"/>' + libros(9960, -1250, 10, seed=21) + '<rect x="9950" y="-900" width="420" height="20" fill="#ff5d8f"/>' + libros(9960, -900, 10, seed=22))
up += "".join(tabique_up(R[k][1]) for k in ("bed", "hall", "din", "kit"))
up += '<rect x="-260" y="-1860" width="13420" height="60" fill="#fff1dc"/>'

# ---------------- BUHARDILLA bajo el tejado (sección): vigas, ventana redonda, baúl, cajas, caballito…
def techo_y(x):
    return -1860 - 1660 * max(0.0, 1 - abs(x - 6450) / 6600)
buh = ('<path d="M-500,-1830 L6450,-3720 L13400,-1830 Z" fill="url(#tejas)"/><path d="M-500,-1830 L6450,-3720 L13400,-1830" stroke="#9e2a22" stroke-width="46" fill="none" stroke-linejoin="round"/>'
       '<path d="M-150,-1860 L6450,-3520 L13050,-1860 Z" fill="url(#buh)"/>'
       + "".join(f'<path d="M{6450 + k * 700},{techo_y(6450 + k * 700):.0f} L{6450 + k * 700},-1860" stroke="#a8713f" stroke-width="34"/>' for k in range(-8, 9))
       + '<path d="M-150,-1860 L6450,-3520 L13050,-1860" stroke="#8e5a2c" stroke-width="40" fill="none"/>'
       '<rect x="-150" y="-1900" width="13200" height="40" fill="#a8713f"/>'
       # ventana redonda (ojo de buey) con cielo
       '<circle cx="6450" cy="-2780" r="250" fill="#ffffff"/><circle cx="6450" cy="-2780" r="220" fill="url(#cieloDia)"/><path d="M6230,-2780 L6670,-2780 M6450,-3000 L6450,-2560" stroke="#ffffff" stroke-width="18"/>'
       '<ellipse cx="6380" cy="-2850" rx="70" ry="24" fill="#ffffff"/>'
       # bombilla colgando
       '<path d="M6450,-3510 L6450,-3140" stroke="#3b2f2f" stroke-width="6"/><circle cx="6450" cy="-3110" r="36" fill="#fff3b0"/><circle cx="6450" cy="-3110" r="110" fill="#fff3b0" opacity="0.25"/>'
       # guirnalda por las vigas
       + guirnalda(2800, 10100, techo_y(2800) + 140)
       # cajas apiladas, baúl, caballito, maleta, telescopio, espejo, caja de Navidad, lámpara vieja
       + "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{hh}" rx="8" fill="#c98f58" stroke="#8e5a2c" stroke-width="6"/><path d="M{x},{y + 30} L{x + w},{y + 30}" stroke="#8e5a2c" stroke-width="5"/><text x="{x + w / 2}" y="{y + hh / 2 + 22}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="38" fill="#7a3b10">{t}</text>'
                 for x, y, w, hh, t in ((3600, -2160, 360, 300, "FOTOS"), (3980, -2160, 300, 300, "LIBROS"), (3720, -2420, 320, 260, "VARIOS")))
       + '<rect x="4500" y="-2180" width="560" height="320" rx="30" fill="#7a3b10"/><path d="M4500,-2100 C4500,-2260 5060,-2260 5060,-2100 Z" fill="#9a4f1a"/><rect x="4500" y="-2120" width="560" height="26" fill="#ffd23f"/><rect x="4760" y="-2080" width="40" height="60" rx="6" fill="#ffd23f"/>'
       '<path d="M5300,-1860 C5350,-1920 5700,-1920 5760,-1860" stroke="#ef233c" stroke-width="22" fill="none"/><rect x="5380" y="-2100" width="260" height="140" rx="40" fill="#ffffff" stroke="#ef233c" stroke-width="10"/><circle cx="5660" cy="-2200" r="70" fill="#ffffff" stroke="#ef233c" stroke-width="10"/><path d="M5690,-2270 L5720,-2330 L5740,-2260" fill="#ffd23f"/><circle cx="5680" cy="-2210" r="9" fill="#2b2d42"/><path d="M5420,-1960 L5400,-1880 M5600,-1960 L5620,-1880" stroke="#ef233c" stroke-width="16"/>'
       '<rect x="7000" y="-2120" width="420" height="260" rx="24" fill="#06d6a0"/><rect x="7150" y="-2160" width="120" height="50" rx="16" fill="none" stroke="#04a37a" stroke-width="14"/><rect x="7000" y="-2010" width="420" height="20" fill="#04a37a"/>'
       '<path d="M7700,-1860 L7800,-2160 M7900,-1860 L7800,-2160 M7800,-1860 L7800,-2160" stroke="#3b2f2f" stroke-width="10"/><rect x="7700" y="-2340" width="320" height="80" rx="36" fill="#3a86ff" transform="rotate(-25 7860 -2300)"/>'
       '<rect x="8300" y="-2400" width="260" height="540" rx="20" fill="#c97b45"/><rect x="8325" y="-2375" width="210" height="490" rx="12" fill="#d9f6ff"/><path d="M8360,-2300 L8440,-2340 M8350,-2230 L8480,-2310" stroke="#ffffff" stroke-width="12" stroke-linecap="round"/>'
       '<rect x="8800" y="-2160" width="460" height="300" rx="10" fill="#ef233c"/><rect x="8800" y="-2160" width="460" height="300" rx="10" fill="none" stroke="#06d6a0" stroke-width="14" stroke-dasharray="40 30"/><text x="9030" y="-1990" text-anchor="middle" font-family="Inter" font-weight="900" font-size="44" fill="#ffffff">NAVIDAD</text>'
       '<path d="M9600,-1860 L9640,-2300 M9680,-1860 L9640,-2300" stroke="#3b2f2f" stroke-width="10"/><path d="M9540,-2300 L9740,-2300 L9700,-2420 L9580,-2420 Z" fill="#ffd23f"/>')
H.append(svg(buh))
# chimenea con humo
H.append(svg('<rect x="10150" y="-3150" width="260" height="700" fill="#b5302a"/><rect x="10150" y="-3150" width="260" height="700" fill="url(#ladrillo)"/><rect x="10110" y="-3210" width="340" height="80" rx="10" fill="#8e2420"/>'
             '<g id="humo">' + "".join(f'<circle class="humo" cx="{10280 + k * 30}" cy="{-3260 - k * 90}" r="{60 + k * 18}" fill="#ffffff" opacity="0.8"/>' for k in range(4)) + '</g>'))
H.append(svg(up))

# ---------------- SÓTANO (garaje, trastero, lavadero, ping-pong)
sot = (f'<rect x="-260" y="{BT}" width="13420" height="{BF + 160 - BT}" fill="#5e6b82"/>'
       f'<rect x="0" y="{BT + 40}" width="12900" height="{BF - BT - 40}" fill="url(#bSot)"/><rect x="0" y="{BT + 40}" width="12900" height="{BF - BT - 40}" fill="url(#ladrillo)"/>'
       f'<rect x="0" y="{BF}" width="12900" height="80" fill="#9aa5b8"/><rect x="0" y="{BF}" width="12900" height="8" fill="#000" opacity="0.15"/>'
       + "".join(f'<rect x="{x - 40}" y="{BT + 40}" width="80" height="{BF - BT - 40}" fill="#5e6b82"/>' for x in (3600, 7000, 9800))
       + "".join(f'<path d="M{x},{BT + 40} L{x},{BT + 160}" stroke="#3b2f2f" stroke-width="5"/><circle cx="{x}" cy="{BT + 180}" r="26" fill="#fff3b0"/><circle cx="{x}" cy="{BT + 180}" r="90" fill="#fff3b0" opacity="0.22"/>' for x in (1800, 5300, 8400, 11350)))
# garaje: coche, bici, herramientas
sot += ('<g id="coche"><path d="M500,3380 C500,3250 560,3200 700,3190 L900,3040 C960,2990 1040,2980 1500,2980 C1700,2980 1800,3000 1900,3070 L2100,3190 C2300,3200 2400,3250 2400,3380 Z" fill="#ef233c"/>'
        '<path d="M960,3060 L1180,3060 L1180,3180 L860,3180 Z M1240,3060 L1600,3060 C1700,3060 1760,3090 1820,3180 L1240,3180 Z" fill="#bde0fe"/>'
        '<rect x="2320" y="3260" width="80" height="40" rx="10" fill="#ffd23f"/><rect x="500" y="3260" width="60" height="40" rx="10" fill="#ff9f1c"/>'
        '<circle cx="900" cy="3390" r="110" fill="#1d1e2c"/><circle cx="900" cy="3390" r="50" fill="#c0c6d6"/><circle cx="2000" cy="3390" r="110" fill="#1d1e2c"/><circle cx="2000" cy="3390" r="50" fill="#c0c6d6"/></g>'
        '<circle cx="2700" cy="3400" r="80" fill="none" stroke="#2b2d42" stroke-width="14"/><circle cx="3100" cy="3400" r="80" fill="none" stroke="#2b2d42" stroke-width="14"/><path d="M2700,3400 L2850,3260 L3050,3260 L3100,3400 M2850,3260 L2900,3400 L3050,3260 M2840,3230 L2900,3230 M3040,3260 L3060,3210" stroke="#06d6a0" stroke-width="14" fill="none" stroke-linecap="round"/>'
        '<rect x="960" y="2280" width="900" height="600" rx="12" fill="#c98f58"/>' + "".join(f'<circle cx="{1000 + (i % 12) * 72}" cy="{2320 + (i // 12) * 70}" r="6" fill="#8e5a2c"/>' for i in range(96))
        + '<path d="M1050,2420 L1050,2650 M1020,2420 L1080,2420" stroke="#3a86ff" stroke-width="20" stroke-linecap="round"/><path d="M1200,2400 L1200,2700" stroke="#ef233c" stroke-width="18"/><rect x="1170" y="2380" width="60" height="70" rx="10" fill="#2b2d42"/>'
        '<path d="M1350,2450 C1400,2400 1460,2420 1460,2480 L1400,2700" stroke="#2b2d42" stroke-width="18" fill="none"/><rect x="1550" y="2420" width="220" height="60" rx="20" fill="#ffd23f"/><rect x="1640" y="2470" width="40" height="220" fill="#7a4b2a"/>'
        '<rect x="100" y="2400" width="300" height="20" fill="#7a4b2a"/>' + "".join(f'<rect x="{x}" y="2300" width="70" height="100" rx="10" fill="{c}"/>' for x, c in ((120, "#3a86ff"), (210, "#ff5d8f"), (300, "#06d6a0"))))
# trastero
sot += ('<rect x="3800" y="2300" width="1500" height="1180" fill="none" stroke="#c0c6d6" stroke-width="24"/>' + "".join(f'<rect x="3800" y="{y}" width="1500" height="22" fill="#c0c6d6"/>' for y in (2650, 3050))
        + "".join(f'<rect x="{x}" y="{y - hh}" width="{w}" height="{hh}" rx="6" fill="#d9a066" stroke="#8e5a2c" stroke-width="5"/><text x="{x + w / 2}" y="{y - hh / 2 + 12}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="30" fill="#7a3b10">{t}</text>'
                  for x, y, w, hh, t in ((3840, 2650, 300, 220, "JUGUETES"), (4170, 2650, 260, 200, "ROPA"), (4460, 2650, 380, 240, "NAVIDAD"), (3860, 3050, 420, 260, "FOTOS"), (4320, 3050, 300, 200, "CABLES"), (4660, 3050, 420, 300, "PLAYA")))
        + '<path d="M5500,3480 L5620,2600 M5560,3480 L5680,2600" stroke="#3a86ff" stroke-width="22" stroke-linecap="round"/><path d="M5600,2620 L5640,2560 M5660,2620 L5700,2560" stroke="#ef233c" stroke-width="16"/>'
        '<rect x="5900" y="3060" width="500" height="420" rx="30" fill="#8338ec"/><rect x="5900" y="3060" width="500" height="80" rx="30" fill="#a66bff"/><circle cx="6550" cy="3380" r="100" fill="#ffffff" stroke="#2b2d42" stroke-width="8"/><path d="M6480,3330 L6620,3430 M6620,3330 L6480,3430" stroke="#2b2d42" stroke-width="6"/>'
        '<rect x="6200" y="2700" width="560" height="320" rx="20" fill="#ff9f1c"/><circle cx="6300" cy="3020" r="30" fill="#2b2d42"/><circle cx="6660" cy="3020" r="30" fill="#2b2d42"/>')
# lavadero
sot += ('<rect x="7250" y="2900" width="560" height="580" rx="24" fill="#ffffff"/><rect x="7250" y="2900" width="560" height="110" rx="24" fill="#e3e8f0"/><circle cx="7330" cy="2955" r="20" fill="#06d6a0"/><rect x="7600" y="2940" width="160" height="30" rx="10" fill="#2b2d42"/>'
        '<circle cx="7530" cy="3250" r="190" fill="#c0c6d6"/><circle cx="7530" cy="3250" r="160" fill="#4cc9f0"/>'
        '<g id="tambor">' + "".join(f'<path d="M7530,3250 L{7530 + 140 * math.cos(a * math.pi / 3):.0f},{3250 + 140 * math.sin(a * math.pi / 3):.0f} A140,140 0 0,1 {7530 + 140 * math.cos((a + 1) * math.pi / 3):.0f},{3250 + 140 * math.sin((a + 1) * math.pi / 3):.0f} Z" fill="{c}" opacity="0.85"/>'
                                 for a, c in ((0, "#ff5d8f"), (2, "#ffd23f"), (4, "#8ac926"))) + '</g>'
        '<circle cx="7470" cy="3190" r="40" fill="#ffffff" opacity="0.5"/>'
        '<rect x="7900" y="2900" width="560" height="580" rx="24" fill="#f0f4fa"/><rect x="7900" y="2900" width="560" height="110" rx="24" fill="#e3e8f0"/><circle cx="8180" cy="3250" r="170" fill="#c0c6d6"/><circle cx="8180" cy="3250" r="140" fill="#3d405b"/><circle cx="8130" cy="3200" r="30" fill="#ffffff" opacity="0.3"/>'
        '<path d="M8550,3480 L8600,3280 L8900,3280 L8950,3480 Z" fill="#ffd23f"/><path d="M8600,3280 C8650,3200 8700,3240 8750,3200 C8800,3240 8850,3200 8900,3280" fill="#ff5d8f"/>'
        '<path d="M8600,2400 C8900,2470 9300,2470 9650,2400" stroke="#ffffff" stroke-width="6" fill="none"/>'
        + "".join(f'<path d="M{x},2445 L{x - 30},2620 L{x + 10},2640 L{x + 30},2460 Z" fill="{c}"/><rect x="{x - 6}" y="2425" width="14" height="40" fill="#ffd23f"/>' for x, c in ((8720, "#ef233c"), (8900, "#3a86ff"), (9080, "#06d6a0"), (9260, "#ff9f1c"), (9440, "#8338ec")))
        + '<rect x="7250" y="2500" width="1200" height="22" fill="#7a4b2a"/>' + "".join(f'<rect x="{x}" y="{2500 - hh}" width="90" height="{hh}" rx="14" fill="{c}"/>' for x, hh, c in ((7300, 150, "#3a86ff"), (7420, 120, "#ff5d8f"), (7540, 170, "#06d6a0"), (7680, 130, "#ffd23f"))))
# sala de ping-pong
sot += ('<rect x="10100" y="2960" width="1500" height="50" rx="10" fill="#118ab2"/><path d="M10850,2960 L10850,3010" stroke="#ffffff" stroke-width="8"/><path d="M10100,2985 L11600,2985" stroke="#ffffff" stroke-width="4"/>'
        '<rect x="10850" y="2880" width="10" height="80" fill="#2b2d42"/><rect x="10840" y="2880" width="30" height="80" fill="none" stroke="#ffffff" stroke-width="3"/>'
        '<path d="M10200,3010 L10180,3480 M11500,3010 L11520,3480" stroke="#2b2d42" stroke-width="22"/>'
        '<circle cx="10500" cy="2880" r="16" fill="#ffffff"/><ellipse cx="10350" cy="2930" rx="50" ry="60" fill="#ef233c" transform="rotate(-30 10350 2930)"/><rect x="10380" y="2960" width="16" height="70" fill="#7a4b2a" transform="rotate(-30 10350 2930)"/>'
        '<circle cx="12100" cy="2550" r="200" fill="#1d1e2c"/>' + "".join(f'<circle cx="12100" cy="2550" r="{r}" fill="{c}"/>' for r, c in ((170, "#ef233c"), (130, "#ffffff"), (90, "#06d6a0"), (50, "#ffffff"), (20, "#ef233c")))
        + '<path d="M12060,2520 L12000,2460" stroke="#ffd23f" stroke-width="10"/>'
        '<rect x="11950" y="3150" width="850" height="250" rx="60" fill="#06d6a0"/><rect x="11900" y="3050" width="140" height="350" rx="50" fill="#04a37a"/><rect x="12720" y="3050" width="140" height="350" rx="50" fill="#04a37a"/><rect x="11950" y="3050" width="850" height="140" rx="60" fill="#06d6a0"/>'
        '<path d="M12000,3400 L12000,3480 M12750,3400 L12750,3480" stroke="#3b2f2f" stroke-width="20"/>')
# escalera que baja del pasillo al sótano
sot += "".join(f'<rect x="{2600 + i * 62}" y="{BT + 60 + i * 110}" width="240" height="30" fill="#c97b45"/>' for i in range(12))
H.append(svg(sot))
# paredes exteriores de toda la casa (con ventanitas a los lados)
H.append(svg('<rect x="-260" y="-1860" width="260" height="5420" fill="#fff1dc"/><rect x="12900" y="-1860" width="260" height="5420" fill="#fff1dc"/>'
             '<rect x="-260" y="3560" width="13420" height="90" fill="#4a3a33"/>'))

# ---------------- JARDINES a los dos lados y cielo con vida
def arbol(x, s=1.0, c="#2ecc71"):
    return (f'<rect x="{x - 40 * s:.0f}" y="{1970 - 700 * s:.0f}" width="{80 * s:.0f}" height="{700 * s:.0f}" fill="#7a4b2a"/>'
            + "".join(f'<circle cx="{x + dx * s:.0f}" cy="{1970 + dy * s:.0f}" r="{r * s:.0f}" fill="{cc}"/>' for dx, dy, r, cc in ((0, -900, 320, c), (-230, -760, 230, "#27ae60"), (230, -760, 240, "#27ae60"), (0, -1150, 220, "#58d68d")))
            + "".join(f'<circle cx="{x + dx * s:.0f}" cy="{1970 + dy * s:.0f}" r="{22 * s:.0f}" fill="#ef233c"/>' for dx, dy in ((-120, -900), (80, -1000), (180, -820), (-60, -760))))
jard = ('<rect x="-4200" y="1940" width="3940" height="80" fill="#4fc36b"/><rect x="13160" y="1940" width="4200" height="80" fill="#4fc36b"/>'
        + "".join(f'<path d="M{x},1950 l10,-40 l10,40" fill="#3fae5c"/>' for x in list(range(-4100, -300, 60)) + list(range(13200, 17300, 60)))
        + arbol(-1700, 1.2) + arbol(-3400, 0.9, "#58d68d") + arbol(14600, 1.25) + arbol(16400, 0.85, "#58d68d")
        + "".join(f'<rect x="{x}" y="1680" width="40" height="290" rx="10" fill="#ffffff"/><path d="M{x},1690 L{x + 20},1650 L{x + 40},1690 Z" fill="#ffffff"/>' for x in list(range(-4100, -400, 110)))
        + '<rect x="-4100" y="1760" width="3700" height="20" fill="#ffffff"/><rect x="-4100" y="1860" width="3700" height="20" fill="#ffffff"/>'
        + "".join(f'<path d="M{x},1970 L{x},1870" stroke="#2ecc71" stroke-width="8"/><circle cx="{x}" cy="1860" r="26" fill="{c}"/><circle cx="{x}" cy="1860" r="10" fill="#ffd23f"/>' for x, c in ((-3800, "#ff5d8f"), (-3600, "#8338ec"), (-2900, "#ef233c"), (-1100, "#ff9f1c"), (-800, "#ff5d8f"), (13600, "#8338ec"), (13800, "#ef233c"), (15400, "#ff5d8f"), (15700, "#ffd23f"), (17000, "#3a86ff")))
        + '<rect x="-620" y="1600" width="30" height="370" fill="#7a4b2a"/><rect x="-720" y="1500" width="230" height="140" rx="60" fill="#3a86ff"/><rect x="-520" y="1460" width="12" height="80" fill="#ef233c"/><rect x="-520" y="1460" width="60" height="36" fill="#ef233c"/>'
        '<path d="M-2700,1970 L-2700,1700 L-2500,1560 L-2300,1700 L-2300,1970 Z" fill="#ff9f1c"/><path d="M-2740,1720 L-2500,1530 L-2260,1720" stroke="#ef233c" stroke-width="40" fill="none"/><path d="M-2580,1970 C-2580,1820 -2420,1820 -2420,1970 Z" fill="#3b2f2f"/><text x="-2500" y="1680" text-anchor="middle" font-family="Inter" font-weight="900" font-size="44" fill="#ffffff">TOBY</text>'
        # columpio en el árbol de la derecha
        '<path d="M14380,1050 L14380,1700 M14620,1050 L14620,1700" stroke="#3b2f2f" stroke-width="10"/><rect id="columpio" x="14340" y="1700" width="320" height="40" rx="12" fill="#ef233c"/>'
        '<rect x="15700" y="1550" width="500" height="420" rx="30" fill="#8ac926"/><circle cx="15800" cy="1560" r="70" fill="#8ac926"/><circle cx="16080" cy="1540" r="90" fill="#8ac926"/>')
H.append(svg(jard))
cielo_vida = ('<g id="globo"><path d="M-1500,-4200 C-1820,-4200 -1900,-3800 -1650,-3500 L-1350,-3500 C-1100,-3800 -1180,-4200 -1500,-4200 Z" fill="#ff5d8f"/>'
              '<path d="M-1500,-4200 C-1620,-4200 -1640,-3800 -1560,-3500 L-1440,-3500 C-1360,-3800 -1380,-4200 -1500,-4200 Z" fill="#ffd23f"/>'
              '<path d="M-1650,-3500 L-1580,-3300 M-1350,-3500 L-1420,-3300" stroke="#3b2f2f" stroke-width="8"/><rect x="-1590" y="-3300" width="180" height="130" rx="16" fill="#c97b45"/></g>'
              + "".join(f'<g class="pajaro" transform="translate({x} {y})"><path class="ala" d="M-50,0 Q-25,-30 0,0 Q25,-30 50,0" stroke="#2b2d42" stroke-width="10" fill="none" stroke-linecap="round"/></g>' for x, y in ((1500, -2600), (1650, -2700), (1820, -2580), (8200, -3900), (8380, -3980), (12200, -4100))))
H.append(svg(cielo_vida, "cieloVida"))

# animaciones del entorno (lentas, nada de destellos)
J(f'tl.to(".humo", {{y:-260, scale:1.6, opacity:0, duration:3.2, stagger:{{each:0.8, repeat:{int(DUR / 3.2)}}}, ease:"sine.out"}}, 0);')
J(f'tl.to("#globo", {{y:-120, x:200, duration:{DUR / 2:.2f}, yoyo:true, repeat:1, ease:"sine.inOut"}}, 0);')
J(f'tl.to(".pajaro", {{x:"+=900", duration:{DUR:.2f}, ease:"none"}}, 0);')
J(f'tl.to(".ala", {{scaleY:-0.6, duration:0.3, yoyo:true, repeat:{int(DUR / 0.3)}, ease:"sine.inOut", transformOrigin:"50% 100%"}}, 0);')
J(f'tl.to("#tambor", {{rotation:360 * {int(DUR / 2)}, duration:{DUR:.2f}, ease:"none", svgOrigin:"7530 3250"}}, 0);')
J(f'tl.to(".burbuja", {{y:-40, duration:1.6, yoyo:true, repeat:{int(DUR / 1.6)}, ease:"sine.inOut", stagger:0.2}}, 0);')
J(f'tl.to("#pato", {{rotation:8, duration:1.2, yoyo:true, repeat:{int(DUR / 1.2)}, ease:"sine.inOut", svgOrigin:"900 -800"}}, 0);')
J(f'tl.to("#movil", {{rotation:6, duration:2.0, yoyo:true, repeat:{int(DUR / 2.0)}, ease:"sine.inOut", svgOrigin:"3900 -1770"}}, 0);')
J(f'tl.to("#columpio", {{x:60, duration:1.4, yoyo:true, repeat:{int(DUR / 1.4)}, ease:"sine.inOut"}}, 0);')
J(f'tl.to("#heroe", {{x:220, y:-60, duration:1.0, yoyo:true, repeat:{int(DUR / 1.0)}, ease:"sine.inOut"}}, 0);')

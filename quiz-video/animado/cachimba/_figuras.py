POSES = {
    "listo": dict(head=(0, -91), neck=(0, -80), hip=(0, -47), eR=(13, -62), hR=(8, -52), eL=(-12, -62), hL=(-2, -54), tip=(18, -78),
                  kR=(10, -25), fR=(13, 0), kL=(-10, -25), fL=(-13, 0)),
    "drAtras": dict(head=(3, -90), neck=(2, -80), hip=(0, -47), eR=(21, -66), hR=(29, -58), eL=(-13, -68), hL=(-8, -64), tip=(52, -66),
                    kR=(12, -25), fR=(16, 0), kL=(-11, -24), fL=(-16, 0)),
    "drFinal": dict(head=(-2, -91), neck=(-1, -80), hip=(0, -47), eR=(-7, -74), hR=(-15, -80), eL=(-15, -58), hL=(-10, -48), tip=(-6, -106),
                    kR=(9, -25), fR=(14, 0), kL=(-11, -26), fL=(-14, 0)),
    "revAtras": dict(head=(-3, -90), neck=(-2, -80), hip=(0, -47), eR=(-12, -66), hR=(-22, -60), eL=(-16, -62), hL=(-20, -58), tip=(-46, -68),
                     kR=(11, -24), fR=(16, 0), kL=(-12, -25), fL=(-16, 0)),
    "revFinal": dict(head=(2, -91), neck=(1, -80), hip=(0, -47), eR=(13, -76), hR=(18, -84), eL=(10, -74), hL=(15, -82), tip=(8, -110),
                     kR=(11, -25), fR=(14, 0), kL=(-10, -26), fL=(-14, 0)),
    "saqueA": dict(head=(0, -92), neck=(0, -81), hip=(0, -48), eR=(17, -72), hR=(23, -62), eL=(-9, -94), hL=(-11, -112), tip=(30, -40),
                   kR=(9, -24), fR=(12, 0), kL=(-8, -25), fL=(-12, 0)),
    "saqueB": dict(head=(2, -97), neck=(2, -86), hip=(0, -50), eR=(8, -108), hR=(10, -126), eL=(-10, -74), hL=(-6, -60), tip=(14, -154),
                   kR=(5, -25), fR=(6, -2), kL=(-6, -25), fL=(-8, 0)),
    "correr1": dict(head=(0, -91), neck=(0, -80), hip=(0, -47), eR=(14, -64), hR=(10, -54), eL=(-13, -64), hL=(-4, -56), tip=(20, -80),
                    kR=(14, -27), fR=(20, -5), kL=(-6, -21), fL=(-14, 0)),
    "correr2": dict(head=(0, -91), neck=(0, -80), hip=(0, -47), eR=(14, -64), hR=(10, -54), eL=(-13, -64), hL=(-4, -56), tip=(20, -80),
                    kR=(6, -21), fR=(14, 0), kL=(-14, -27), fL=(-20, -5)),
    "toalla": dict(head=(0, -89), neck=(0, -79), hip=(0, -47), eR=(12, -80), hR=(4, -90), eL=(-12, -80), hL=(-4, -90), tip=(26, -60),
                   kR=(8, -25), fR=(10, 0), kL=(-8, -25), fL=(-10, 0)),
    "beber": dict(head=(1, -89), neck=(0, -79), hip=(0, -47), eR=(12, -60), hR=(14, -44), eL=(-12, -76), hL=(-3, -92), tip=(20, -22),
                  kR=(8, -25), fR=(10, 0), kL=(-8, -25), fL=(-10, 0)),
    "comer": dict(head=(1, -89), neck=(0, -79), hip=(0, -47), eR=(12, -60), hR=(14, -44), eL=(-11, -74), hL=(-3, -86), tip=(20, -22),
                  kR=(8, -25), fR=(10, 0), kL=(-8, -25), fL=(-10, 0)),
    "calambre": dict(head=(-10, -66), neck=(-8, -56), hip=(0, -30), eR=(4, -36), hR=(12, -14), eL=(-16, -40), hL=(-18, -20), tip=(-34, -4),
                     kR=(14, -16), fR=(8, 0), kL=(-14, -14), fL=(-26, 0)),
    "cansado": dict(head=(2, -86), neck=(1, -77), hip=(0, -46), eR=(12, -58), hR=(14, -42), eL=(-11, -60), hL=(-12, -44), tip=(22, -18),
                    kR=(8, -24), fR=(11, 0), kL=(-8, -24), fL=(-11, 0)),
    "andar1": dict(head=(0, -92), neck=(0, -81), hip=(0, -48), eR=(10, -62), hR=(14, -46), eL=(-10, -62), hL=(-14, -48), tip=(24, -28),
                   kR=(9, -25), fR=(15, -2), kL=(-7, -24), fL=(-11, 0)),
    "andar2": dict(head=(0, -92), neck=(0, -81), hip=(0, -48), eR=(10, -62), hR=(12, -48), eL=(-10, -62), hL=(-10, -48), tip=(22, -30),
                   kR=(7, -24), fR=(11, 0), kL=(-9, -25), fL=(-15, -2)),
    "bote": dict(head=(1, -90), neck=(0, -80), hip=(0, -47), eR=(14, -64), hR=(22, -56), eL=(-10, -64), hL=(-8, -48), tip=(36, -40),
                 kR=(9, -25), fR=(12, 0), kL=(-9, -25), fL=(-12, 0)),
}
def joints(p):
    j = dict(p)
    nx, ny = p["neck"]; hx, hy = p["hip"]
    j["sR"], j["sL"] = (nx + 8, ny + 3), (nx - 8, ny + 3)
    j["pR"], j["pL"] = (hx + 5, hy), (hx - 5, hy)
    hr, tp = p["hR"], p["tip"]
    j["thr"] = (hr[0] + 0.38 * (tp[0] - hr[0]), hr[1] + 0.38 * (tp[1] - hr[1]))
    j["mR"] = ((j["pR"][0] + p["kR"][0]) / 2, (j["pR"][1] + p["kR"][1]) / 2)
    j["mL"] = ((j["pL"][0] + p["kL"][0]) / 2, (j["pL"][1] + p["kL"][1]) / 2)
    j["zR"] = (p["fR"][0] + 5, p["fR"][1]); j["zL"] = (p["fL"][0] - 5, p["fL"][1])
    j["cR"] = (j["sR"][0] + 0.45 * (p["eR"][0] - j["sR"][0]), j["sR"][1] + 0.45 * (p["eR"][1] - j["sR"][1]))
    j["cL"] = (j["sL"][0] + 0.45 * (p["eL"][0] - j["sL"][0]), j["sL"][1] + 0.45 * (p["eL"][1] - j["sL"][1]))
    return j
# (nombre, desde, hasta, grosor, color)  — el orden es el de dibujo
def segs(c):
    return [("muL", "pL", "kL", 8, c["piel"]), ("piL", "kL", "fL", 7, c["piel"]), ("zaL", "fL", "zL", 6, c["zap"]),
            ("muR", "pR", "kR", 8, c["piel"]), ("piR", "kR", "fR", 7, c["piel"]), ("zaR", "fR", "zR", 6, c["zap"]),
            ("shL", "pL", "mL", 11, c["short"]), ("shR", "pR", "mR", 11, c["short"]), ("cad", "pL", "pR", 11, c["short"]),
            ("tor", "neck", "hip", 19, c["cam"]),
            ("brL", "sL", "eL", 7, c["piel"]), ("anL", "eL", "hL", 6, c["piel"]), ("mgL", "sL", "cL", 9, c["cam"]),
            ("brR", "sR", "eR", 7, c["piel"]), ("anR", "eR", "hR", 6, c["piel"]), ("mgR", "sR", "cR", 9, c["cam"]),
            ("mng", "hR", "thr", 3, "#1b1f27"), ("rq", "thr", "tip", 10, c["raq"]), ("cu", "thr", "tip", 5, "#dfe9f2")]
ESTADO = {}
def figura(pid, c, pose="listo", sudor=True, extra=""):
    j = joints(POSES[pose])
    out = [f'<g id="{pid}"><g id="{pid}_m">',
           f'<ellipse cx="0" cy="1" rx="17" ry="5" fill="#000" opacity="0.32"/>']
    for nm, a, b, w, col in segs(c):
        if c["raq"] == "none" and nm in ("mng", "rq", "cu"):
            continue
        op = ' opacity="0.8"' if nm == "cu" else ""
        out.append(f'<line id="{pid}_{nm}" x1="{j[a][0]}" y1="{j[a][1]}" x2="{j[b][0]}" y2="{j[b][1]}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"{op}/>')
        if nm == "tor" and sudor:
            out.append(f'<line id="{pid}_sud" x1="{j[a][0]}" y1="{j[a][1] + 6}" x2="{j[b][0]}" y2="{j[b][1] - 4}" stroke="#000" stroke-width="11" stroke-linecap="round" opacity="0"/>')
    hx, hy = j["head"]
    out.append(f'<g id="{pid}_hd" transform="translate(0,0)"><g id="{pid}_h" ><circle cx="{hx}" cy="{hy}" r="9" fill="{c["piel"]}"/>'
               f'<path d="M{hx - 9.2},{hy - 1} A9.2,9.2 0 0 1 {hx + 9.2},{hy - 1} Q{hx},{hy - 5} {hx - 9.2},{hy - 1} Z" fill="{c["pelo"]}"/>'
               f'<path d="M{hx - 9},{hy - 3.5} Q{hx},{hy - 6.5} {hx + 9},{hy - 3.5}" stroke="{c.get("cinta", "#ffffff")}" stroke-width="2.6" fill="none"/></g></g>')
    out.append(extra + '</g></g>')
    ESTADO[pid] = dict(pose=pose, c=c)
    return "".join(out)
HEAD0 = {}
def pose(pid, nombre, t, d=0.18, ease="power2.out", slouch=None, solo=None):
    """Lleva la persona a una postura (mueve los extremos de cada palo)."""
    p = {k: list(v) for k, v in POSES[nombre].items()}
    f = cansancio(t) if slouch is None else slouch
    if nombre not in ("calambre",):
        p["head"][0] += 3 * f; p["head"][1] += 6 * f; p["neck"][1] += 4 * f; p["neck"][0] += 1.5 * f
    j = joints({k: tuple(v) for k, v in p.items()})
    for nm, a, b, w, col in segs(ESTADO[pid]["c"]):
        if ESTADO[pid]["c"]["raq"] == "none" and nm in ("mng", "rq", "cu"):
            continue
        if solo and nm not in solo:
            continue
        J(f'tl.to("#{pid}_{nm}", {{attr:{{x1:{j[a][0]:.1f}, y1:{j[a][1]:.1f}, x2:{j[b][0]:.1f}, y2:{j[b][1]:.1f}}}, duration:{d}, ease:"{ease}"}}, {t:.3f});')
        if nm == "tor" and (not solo):
            J(f'tl.to("#{pid}_sud", {{attr:{{x1:{j[a][0]:.1f}, y1:{j[a][1] + 6:.1f}, x2:{j[b][0]:.1f}, y2:{j[b][1] - 4:.1f}}}, duration:{d}, ease:"{ease}"}}, {t:.3f});')
    if not solo:
        h0 = POSES["listo"]["head"]
        J(f'tl.to("#{pid}_h", {{x:{j["head"][0] - h0[0]:.1f}, y:{j["head"][1] - h0[1]:.1f}, duration:{d}, ease:"{ease}"}}, {t:.3f});')
    ESTADO[pid]["pose"] = nombre
PIERNAS = {"muL", "piL", "zaL", "muR", "piR", "zaR", "shL", "shR", "cad"}
POSES["sentado"] = dict(head=(0, -64), neck=(0, -54), hip=(0, -24), eR=(10, -40), hR=(14, -28), eL=(-10, -40), hL=(-14, -28), tip=(14, -28),
                        kR=(6, -22), fR=(7, 0), kL=(-6, -22), fL=(-7, 0))
POSES["agachado"] = dict(head=(0, -60), neck=(0, -50), hip=(0, -22), eR=(10, -38), hR=(9, -26), eL=(-10, -38), hL=(-9, -26), tip=(9, -26),
                         kR=(11, -14), fR=(6, 0), kL=(-11, -14), fL=(-6, 0))
POSES["firme"] = dict(head=(0, -92), neck=(0, -81), hip=(0, -48), eR=(9, -64), hR=(6, -50), eL=(-9, -64), hL=(-6, -50), tip=(6, -50),
                      kR=(5, -24), fR=(6, 0), kL=(-5, -24), fL=(-6, 0))
POSES["dar"] = dict(head=(0, -92), neck=(0, -81), hip=(0, -48), eR=(14, -68), hR=(26, -66), eL=(-9, -64), hL=(-6, -50), tip=(26, -66),
                    kR=(5, -24), fR=(6, 0), kL=(-5, -24), fL=(-6, 0))

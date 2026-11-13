# ------------------------------------------------------------------ subtítulos
CLAVE = set(norm(w) for w in ["veinte", "horas", "tiebreak", "nadie", "una", "dura", "diez", "dos", "nunca", "veinticinco", "sentado", "seis",
                               "toalla", "agua", "platano", "treinta", "cien", "glucogeno", "doscientos", "ochenta", "sol", "focos", "litros",
                               "sodio", "mareos", "calambres", "calambre", "relevan", "no", "medianoche", "limite", "madrugada", "catorce",
                               "nueve", "cuatro", "despiertos", "alcohol", "medio", "tarde", "cambian", "presion", "cuarenta", "maraton",
                               "amanece", "cientos", "mil", "ampollas", "duele", "once", "cinco", "tres", "pausa", "empate"])
DEBIL = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "y", "a", "en", "con", "que", "por", "tu", "se", "lo", "no", "solo", "esa", "esos", "su"}
chunks, cur = [], []
for p in T["palabras"]:
    cur.append(p)
    txt = " ".join(x["w"] for x in cur)
    fin_frase = re.search(r"[.:;?!…]$", p["w"])
    if fin_frase or ((len(cur) >= 5 or len(txt) >= 28) and norm(p["w"]) not in DEBIL) or len(cur) >= 7:
        chunks.append(cur); cur = []
if cur:
    chunks.append(cur)
SUBS = []
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
r3 = random.Random(3)
for s_ in range(int(DUR / 0.08)):
    J(f'tl.set("#grano", {{backgroundPosition:"{r3.randint(0, 360)}px {r3.randint(0, 360)}px"}}, {s_ * 0.08:.2f});')


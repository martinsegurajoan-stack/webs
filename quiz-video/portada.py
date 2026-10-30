"""Portadas (miniaturas) para TikTok, Instagram, YouTube Shorts y Facebook.

Uso:  python3 portada.py quizzes/pareja_01.json
Crea en portadas/:  <video>_9x16.png (1080x1920, Reels/Shorts/Facebook/TikTok)
                    <video>_3x4.png  (1080x1440, recorte central para la portada de TikTok)
Todo lo importante queda dentro de la franja central 3:4 (y 240-1680), que es lo que se ve en
la cuadrícula del perfil. Las opciones NUNCA marcan la respuesta correcta.
"""

import json
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

from quizvideo import themes
from quizvideo.render import _heart, _shape, fit, font, tfont, with_alpha

W, H = 1080, 1920
BASE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(BASE, "assets")
USUARIO = "@hora.delquiz"

# Textos de cada portada: gancho grande + pregunta de muestra + pegatina.
# Vídeos NUEVOS: pon este mismo bloque como clave "portada" dentro del JSON del quiz (sin "paleta":
# se elige sola según el modo). Campos: arriba, titulo [(texto, "w"|"a")], tam (opcional),
# pregunta (índice), emoji, emoji2 (nombres de assets/portada/), estilo clasica|sello|cartel,
# pegatina (clasica/cartel) o sello (2 líneas, estilo sello), sub ("|" = salto de línea en sello).
PORTADAS = {
    "pareja_01": {
        "paleta": lambda: themes.paleta_romantica(themes.elegir_tono("pareja_01")),
        "arriba": "QUIZ DE PAREJAS",
        "titulo": [("¿CUÁNTO CONOCES", "w"), ("A TU PAREJA?", "a")],
        "pregunta": 3,
        "emoji": "sonrojado", "emoji2": "corazon_flecha",
        "pegatina": "¡ETIQUETA A TU PAREJA!",
        "sub": "Si fallas… duermes en el sofá",
    },
    "hora_del_quiz_02": {
        "paleta": lambda: themes.paleta_desde_tono(themes.elegir_tono("hora_del_quiz_02")),
        "arriba": "SOLO PARA LISTOS",
        "titulo": [("PREGUNTAS", "w"), ("TRAMPA", "a")],
        "tam": 140,
        "pregunta": 0,
        "emoji": "mente_explota", "emoji2": "cerebro",
        "estilo": "sello",
        "sello": ("¿LLEGAS", "AL 6/6?"),
        "sub": "La 1ª ya la falla|casi todo el mundo",
    },
    "hora_del_quiz_03": {
        "paleta": lambda: themes.paleta_halloween(themes.elegir_tono("hora_del_quiz_03")),
        "arriba": "ESPECIAL HALLOWEEN",
        "titulo": [("¿CUÁNTO SABES", "w"), ("DE HALLOWEEN?", "a")],
        "pregunta": 0,
        "emoji": "calavera", "emoji2": "calabaza",
        "estilo": "cartel",
        "pegatina": "¿TE ATREVES?",
        "sub": "Solo los valientes llegan al final",
    },
}


def img(path, size):
    im = Image.open(path).convert("RGBA")
    k = size / max(im.size)
    return im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)


def con_sombra(im, off=18, blur=16, alpha=110):
    """Devuelve la imagen con una sombra suave debajo (lienzo algo mayor)."""
    pad = blur * 2 + off
    out = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    mask = im.getchannel("A").point(lambda a: a * alpha // 255)
    sh.paste((0, 0, 0, 255), (pad, pad + off), mask)
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    out.alpha_composite(im, (pad, pad))
    return out


def pegar(base, im, cx, cy, ang=0):
    if ang:
        im = im.rotate(ang, Image.BICUBIC, expand=True)
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def fondo(th, halloween):
    top, bot, mid = th["bg_top"], th["bg_bottom"], th.get("bg_mid", th["bg_top"])
    bg = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    # brillo central detrás del titular
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((-200, 250, W + 200, 1350), fill=with_alpha(mid, 0.75))
    bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
    # rayos de concurso
    rays = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rays)
    cx, cy, R = 540, 760, 2400
    for k in range(20):
        a0 = k * 2 * math.pi / 20 + 0.1
        a1 = a0 + math.pi / 20
        rd.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                    (cx + R * math.cos(a1), cy + R * math.sin(a1))],
                   fill=(255, 255, 255, 22 if halloween else 34))
    bg.alpha_composite(rays)
    # formas de fondo
    rnd = random.Random(7)
    fl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fl)
    cols = th["options"] + [th["accent"]]
    if not halloween:
        for _ in range(26):
            x, y = rnd.uniform(0, W), rnd.uniform(0, H)
            s = rnd.uniform(18, 46)
            col = with_alpha(rnd.choice(cols), 0.6)
            if th.get("formas") == "corazones":
                _heart(fd, x, y, s * 1.3, rnd.uniform(-0.5, 0.5), col)
            else:
                _shape(fd, rnd.choice([0, 1, 2, 3]), x, y, s, rnd.uniform(0, 6.28), col)
    bg.alpha_composite(fl)
    if halloween:
        decor_halloween(bg)
    # viñeta para que el centro destaque
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for i in range(40):
        vd.rectangle((i * 6, i * 6, W - i * 6, H - i * 6), outline=(0, 0, 0, int(5 * (40 - i) / 40 * 2.2)), width=6)
    bg.alpha_composite(vig)
    return bg


def decor_halloween(bg):
    D = os.path.join(A, "decor_halloween")
    luna = img(os.path.join(D, "luna.png"), 330)
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse((700, 60, 1140, 500), fill=(255, 230, 160, 90))
    bg.alpha_composite(halo.filter(ImageFilter.GaussianBlur(60)))
    pegar(bg, luna, 900, 260)
    pegar(bg, img(os.path.join(D, "telarana.png"), 360), 120, 150, 0)
    for x, y, s, a in [(260, 330, 150, -15), (760, 470, 120, 12), (980, 600, 90, -8), (140, 1500, 110, 10),
                       (960, 1380, 130, -12)]:
        pegar(bg, img(os.path.join(D, "murcielago.png"), s), x, y, a)
    pegar(bg, img(os.path.join(D, "fantasma.png"), 170), 110, 1180, 8)
    pegar(bg, img(os.path.join(D, "calabaza.png"), 220), 960, 1760, -6)
    pegar(bg, img(os.path.join(D, "calavera.png"), 160), 130, 1790, 10)


def titular(lineas, th, ang=-4, tam=None):
    """Titular gigante con contorno grueso, sombra y ligera inclinación."""
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    maxw = 960
    sizes = []
    lineas = [tuple(l) for l in lineas]
    for txt, _ in lineas:
        s = 200
        while tmp.textlength(txt, font=tfont(s)) > maxw and s > 60:
            s -= 4
        sizes.append(min(s, tam or (150 if len(lineas) > 2 else 175)))
    hgt = sum(int(s * 1.0) for s in sizes) + 60
    layer = Image.new("RGBA", (W + 200, hgt + 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y = 40
    dark = th["text_dark"]
    for (txt, c), s in zip(lineas, sizes):
        f = tfont(s)
        fill = th["accent"] if c == "a" else (255, 255, 255)
        cx = layer.width / 2
        d.text((cx + 10, y + s / 2 + 14), txt, font=f, anchor="mm", fill=with_alpha(dark, 0.55),
               stroke_width=18, stroke_fill=with_alpha(dark, 0.55))
        d.text((cx, y + s / 2), txt, font=f, anchor="mm", fill=fill, stroke_width=16, stroke_fill=dark)
        y += int(s * 1.0)
    return layer.rotate(ang, Image.BICUBIC, expand=True)


def tarjeta(q, th, ancho=880, hueco="der"):
    """Tarjeta con una pregunta real del vídeo y sus 4 opciones (2x2), sin marcar ninguna."""
    pad = 32
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    hl, hr = {"der": (0, 175), "izq": (175, 0), "ambos": (130, 130)}[hueco]  # hueco para los emojis
    qw = ancho - 2 * pad - hl - hr
    fq, lq, lhq = fit(tmp, q["pregunta"], qw, 130, 56, minimum=38)
    alto_q = int(len(lq) * lhq) + 2 * pad
    opt_h, gap = 92, 16
    alto = alto_q + 2 * (opt_h + gap) + pad - gap + 8
    card = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, ancho - 1, alto - 1), 46, fill=th["card"])
    y = pad
    for line in lq:
        d.text((pad + hl + qw / 2 + (20 if hueco == "der" else -20 if hueco == "izq" else 0), y + lhq / 2), line, font=fq, fill=th["text_dark"], anchor="mm")
        y += lhq
    ow = (ancho - 2 * pad - gap) / 2
    for i, o in enumerate(q["opciones"]):
        col = th["options"][i % len(th["options"])]
        x0 = pad + (i % 2) * (ow + gap)
        y0 = alto_q + (i // 2) * (opt_h + gap)
        box = (x0, y0, x0 + ow, y0 + opt_h)
        d.rounded_rectangle((box[0], box[1] + 7, box[2], box[3] + 7), 28, fill=tuple(int(c * 0.72) for c in col))
        d.rounded_rectangle(box, 28, fill=col)
        cx, cy = box[0] + 40, (box[1] + box[3]) / 2
        d.ellipse((cx - 26, cy - 26, cx + 26, cy + 26), fill=(255, 255, 255))
        d.text((cx, cy + 2), "ABCD"[i], font=tfont(36), fill=col, anchor="mm")
        fo, lo, lho = fit(d, o, ow - 92, opt_h - 12, 38, minimum=22, spacing=1.0)
        yy = cy - lho * len(lo) / 2 + lho / 2 + 2
        for l in lo:
            d.text(((box[0] + 72 + box[2]) / 2, yy), l, font=fo, fill=(255, 255, 255), anchor="mm")
            yy += lho
    return con_sombra(card, off=22, blur=22, alpha=120)


def pegatina(texto, bg, fg, ang=6, size=86):
    f = tfont(size)
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    w = d0.textlength(texto, font=f)
    while w > 860 and size > 50:
        size -= 4
        f = tfont(size)
        w = d0.textlength(texto, font=f)
    pw, ph = int(w + 110), int(size + 70)
    st = Image.new("RGBA", (pw + 20, ph + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    d.rounded_rectangle((4, 4, pw + 14, ph + 14), 34, fill=(255, 255, 255))
    d.rounded_rectangle((14, 14, pw + 4, ph + 4), 28, fill=bg)
    hl = Image.new("RGBA", st.size, (0, 0, 0, 0))
    ImageDraw.Draw(hl).rounded_rectangle((24, 20, pw - 6, 14 + ph * 0.42), 20, fill=(255, 255, 255, 40))
    st.alpha_composite(hl)
    d.text(((pw + 18) / 2, (ph + 18) / 2 + 4), texto, font=f, fill=fg, anchor="mm",
           stroke_width=4, stroke_fill=tuple(int(c * 0.6) for c in bg))
    return con_sombra(st, off=14, blur=12, alpha=120).rotate(ang, Image.BICUBIC, expand=True)


def sello(arriba, abajo, bg, fg, r=170, ang=12):
    """Sello en forma de estallido con dos líneas de texto."""
    size = 2 * r + 80
    st = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    c = size / 2
    for rad, col in [(r + 16, (255, 255, 255)), (r, bg)]:
        pts = []
        for k in range(36):
            rr = rad if k % 2 == 0 else rad * 0.86
            a = k * math.pi / 18
            pts.append((c + rr * math.cos(a), c + rr * math.sin(a)))
        d.polygon(pts, fill=col)
    hl = Image.new("RGBA", st.size, (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse((c - r * 0.7, c - r * 0.78, c + r * 0.7, c - r * 0.1), fill=(255, 255, 255, 38))
    st.alpha_composite(hl)
    sombra = tuple(int(v * 0.55) for v in bg)
    d.text((c, c - r * 0.27), arriba, font=tfont(int(r * 0.27)), fill=(255, 255, 255), anchor="mm",
           stroke_width=4, stroke_fill=sombra)
    d.text((c, c + r * 0.17), abajo, font=tfont(int(r * 0.43)), fill=fg, anchor="mm",
           stroke_width=6, stroke_fill=sombra)
    return con_sombra(st, off=14, blur=12, alpha=120).rotate(ang, Image.BICUBIC, expand=True)


def flecha(base, p0, p1, p2, col=(255, 40, 60), w=22):
    """Flecha curva estilo rotulador (curva de Bézier) que apunta a p2."""
    d = ImageDraw.Draw(base)
    pts = []
    for k in range(41):
        t = k / 40
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    for c, ww in [((255, 255, 255), w + 14), (col, w)]:
        d.line(pts, fill=c, width=ww, joint="curve")
        ang = math.atan2(pts[-1][1] - pts[-4][1], pts[-1][0] - pts[-4][0])
        L = 62 + (ww - w) / 2
        for s in (2.5, -2.5):
            d.line([p2, (p2[0] - L * math.cos(ang + s * 0.25), p2[1] - L * math.sin(ang + s * 0.25))],
                   fill=c, width=ww)
        r = ww / 2
        for p in [pts[0], p2]:
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=c)


def pill(base, cx, cy, texto, size, bg, fg):
    d = ImageDraw.Draw(base)
    f = tfont(size)
    w = d.textlength(texto, font=f)
    box = (cx - w / 2 - 40, cy - size / 2 - 20, cx + w / 2 + 40, cy + size / 2 + 20)
    d.rounded_rectangle((box[0], box[1] + 8, box[2], box[3] + 8), (box[3] - box[1]) / 2, fill=(0, 0, 0, 70))
    d.rounded_rectangle(box, (box[3] - box[1]) / 2, fill=bg)
    d.text((cx, cy + 3), texto, font=f, fill=fg, anchor="mm")


def paleta_para(video, quiz, cfg):
    """Misma paleta que el vídeo (el tono ya está en el registro tras renderizar)."""
    if "paleta" in cfg:
        return cfg["paleta"]()
    h = themes.elegir_tono(video)
    modo = quiz.get("modo", "trivial")
    if modo == "pareja":
        return themes.paleta_romantica(h)
    if modo == "halloween":
        return themes.paleta_halloween(h)
    if modo == "mascota":
        return themes.paleta_mascota(h)
    if modo == "personalidad":  # colores de marca del test: amarillo, turquesa, morado y negro
        th = themes.paleta_desde_tono(h)
        th.update({"bg_top": (96, 30, 190), "bg_bottom": (14, 8, 26), "bg_mid": (150, 70, 255),
                   "blob": (0, 222, 205), "accent": (255, 212, 0), "text_dark": (36, 10, 80),
                   "options": [(230, 160, 0), (0, 165, 155), (138, 58, 255), (255, 64, 160)]})
        return th
    if modo == "gamer":
        return themes.paleta_gamer(h)
    return themes.paleta_desde_tono(h)


def crear(quiz_path, out_dir):
    video = os.path.splitext(os.path.basename(quiz_path))[0]
    quiz = json.load(open(quiz_path, encoding="utf-8"))
    video = quiz.get("video", video)  # nombre del vídeo si el JSON lo indica
    cfg = quiz.get("portada") or PORTADAS[video]
    th = paleta_para(video, quiz, cfg)
    hall = th.get("formas") == "halloween"
    base = fondo(th, hall)
    E = os.path.join(A, "portada")
    dark = th["text_dark"]

    q = quiz["preguntas"][cfg["pregunta"]]
    e1 = con_sombra(img(os.path.join(E, cfg["emoji"] + ".png"), 250), off=16, blur=14)
    e2 = con_sombra(img(os.path.join(E, cfg["emoji2"] + ".png"), 170), off=12, blur=12)
    logo = con_sombra(img(os.path.join(A, "logo.png"), 170), off=10, blur=10, alpha=90)
    peg_col = (230, 30, 50) if not hall else (255, 120, 0)
    d = ImageDraw.Draw(base)
    estilo = cfg.get("estilo", "clasica")

    def subtitulo(y):
        d.text((540, y), cfg["sub"], font=font(46), fill=(255, 255, 255), anchor="mm",
               stroke_width=7, stroke_fill=dark)

    if estilo == "clasica":
        # logo izq + etiqueta, titular inclinado a la izquierda, flecha desde la izquierda,
        # emoji arriba a la derecha y pegatina alargada debajo
        pegar(base, logo, 175, 340, 6)
        pill(base, 620, 330, cfg["arriba"], 54, th["accent"], dark)
        t = titular(cfg["titulo"], th, ang=-4, tam=cfg.get("tam"))
        pegar(base, t, 540, 420 + t.height / 2 - 40)
        y_tit = 420 + t.height - 40
        card = tarjeta(q, th, 860, "der")
        cy = y_tit + card.height / 2 - 60
        pegar(base, card, 540, cy, 2)
        top = cy - card.height / 2 + 40
        pegar(base, e1, 905, top + 30, -10)
        pegar(base, e2, 95, cy + card.height / 2 - 70, 12)
        flecha(base, (70, top - 110), (20, top + 20), (150, top + 75))
        y_peg = cy + card.height / 2 + 15
        pegar(base, pegatina(cfg["pegatina"], peg_col, (255, 255, 255), size=80), 540, y_peg, 4)
        subtitulo(y_peg + 150)

    elif estilo == "sello":
        # espejo: etiqueta izq + logo dcha, titular inclinado a la derecha, emoji a la izquierda,
        # flecha desde la derecha y sello redondo sobre la esquina de la tarjeta
        pill(base, 450, 330, cfg["arriba"], 54, th["accent"], dark)
        pegar(base, logo, 900, 340, -6)
        t = titular(cfg["titulo"], th, ang=4, tam=cfg.get("tam"))
        pegar(base, t, 540, 420 + t.height / 2 - 40)
        y_tit = 420 + t.height - 40
        card = tarjeta(q, th, 860, "izq")
        cy = y_tit + card.height / 2 - 60
        pegar(base, card, 540, cy, -2.5)
        top = cy - card.height / 2 + 40
        pegar(base, e1, 170, top + 30, 10)
        flecha(base, (1010, top - 110), (1065, top + 20), (935, top + 70))
        bot = cy + card.height / 2 - 40
        a1, a2 = cfg["sello"]
        pegar(base, sello(a1, a2, peg_col, th["accent"], r=180, ang=10), 830, bot + 130, 10)
        pegar(base, e2, 150, bot + 320, -12)
        for i, linea in enumerate(cfg["sub"].split("|")):
            d.text((360, bot + 150 + i * 62), linea, font=font(50), fill=(255, 255, 255), anchor="mm",
                   stroke_width=7, stroke_fill=dark)

    else:  # "cartel": todo centrado y recto, pegatina arriba, emojis a ambos lados de la pregunta
        pegar(base, logo, 540, 300, 0)
        pegar(base, pegatina(cfg["pegatina"], peg_col, (255, 255, 255), size=74), 540, 470, -5)
        t = titular(cfg["titulo"], th, ang=0, tam=cfg.get("tam"))
        pegar(base, t, 540, 540 + t.height / 2 - 30)
        y_tit = 540 + t.height - 30
        card = tarjeta(q, th, 900, "ambos")
        cy = y_tit + card.height / 2 - 20
        pegar(base, card, 540, cy, 0)
        top = cy - card.height / 2 + 40
        pegar(base, con_sombra(img(os.path.join(E, cfg["emoji2"] + ".png"), 210), off=14, blur=12),
              105, top + 20, -12)
        pegar(base, con_sombra(img(os.path.join(E, cfg["emoji"] + ".png"), 220), off=14, blur=12),
              975, top + 20, 12)
        bot = cy + card.height / 2 - 40
        subtitulo(bot + 85)
        pill(base, 540, bot + 185, cfg["arriba"], 50, th["accent"], dark)

    # usuario abajo del todo
    fu = font(44)
    w = d.textlength(USUARIO, font=fu)
    d.rounded_rectangle((540 - w / 2 - 34, 1735, 540 + w / 2 + 34, 1805), 35, fill=(0, 0, 0, 120))
    d.text((540, 1772), USUARIO, font=fu, fill=(255, 255, 255), anchor="mm")

    os.makedirs(out_dir, exist_ok=True)
    rgb = base.convert("RGB")
    p916 = os.path.join(out_dir, f"{video}_9x16.png")
    p34 = os.path.join(out_dir, f"{video}_3x4.png")
    rgb.save(p916, optimize=True)
    rgb.crop((0, 240, W, 1680)).save(p34, optimize=True)
    return p916, p34


if __name__ == "__main__":
    for q in sys.argv[1:]:
        print(*crear(q, os.path.join(BASE, "portadas")))

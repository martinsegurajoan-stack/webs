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

# Textos de cada portada: gancho grande + pregunta de muestra + pegatina
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
        "titulo": [("6 ACERTIJOS", "w"), ("TRAMPA", "a")],
        "tam": 140,
        "pregunta": 0,
        "emoji": "mente_explota", "emoji2": "cerebro",
        "pegatina": "¿LLEGAS AL 6/6?",
        "sub": "La 1ª ya la falla casi todo el mundo",
    },
    "hora_del_quiz_03": {
        "paleta": lambda: themes.paleta_halloween(themes.elegir_tono("hora_del_quiz_03")),
        "arriba": "ESPECIAL HALLOWEEN",
        "titulo": [("¿CUÁNTO SABES", "w"), ("DE HALLOWEEN?", "a")],
        "pregunta": 0,
        "emoji": "calavera", "emoji2": "calabaza",
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


def tarjeta(q, th, ancho=880):
    """Tarjeta con una pregunta real del vídeo y sus 4 opciones (2x2), sin marcar ninguna."""
    pad = 32
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    qw = ancho - 2 * pad - 175  # hueco a la derecha para el emoji
    fq, lq, lhq = fit(tmp, q["pregunta"], qw, 130, 56, minimum=38)
    alto_q = int(len(lq) * lhq) + 2 * pad
    opt_h, gap = 92, 16
    alto = alto_q + 2 * (opt_h + gap) + pad - gap + 8
    card = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, ancho - 1, alto - 1), 46, fill=th["card"])
    y = pad
    for line in lq:
        d.text((pad + qw / 2 + 20, y + lhq / 2), line, font=fq, fill=th["text_dark"], anchor="mm")
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
    d.rounded_rectangle((24, 20, pw - 6, 14 + ph * 0.42), 20, fill=(255, 255, 255, 40))
    d.text(((pw + 18) / 2, (ph + 18) / 2 + 4), texto, font=f, fill=fg, anchor="mm",
           stroke_width=4, stroke_fill=tuple(int(c * 0.6) for c in bg))
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


def crear(quiz_path, out_dir):
    video = os.path.splitext(os.path.basename(quiz_path))[0]
    cfg = PORTADAS[video]
    quiz = json.load(open(quiz_path, encoding="utf-8"))
    th = cfg["paleta"]()
    hall = th.get("formas") == "halloween"
    base = fondo(th, hall)
    E = os.path.join(A, "portada")
    dark = th["text_dark"]

    # cabecera: logo + etiqueta
    logo = con_sombra(img(os.path.join(A, "logo.png"), 170), off=10, blur=10, alpha=90)
    pegar(base, logo, 175, 340, 6)
    pill(base, 620, 330, cfg["arriba"], 54, th["accent"], dark)

    # titular gigante
    t = titular(cfg["titulo"], th, tam=cfg.get("tam"))
    pegar(base, t, 540, 420 + t.height / 2 - 40)
    y_tit = 420 + t.height - 40

    # tarjeta con pregunta real (sin respuesta marcada), un poco girada
    card = tarjeta(quiz["preguntas"][cfg["pregunta"]], th, 860)
    cy_card = y_tit + card.height / 2 - 60
    pegar(base, card, 540, cy_card, 2)
    top_card = cy_card - card.height / 2 + 40  # +40: margen de la sombra

    # emoji 3D gigante en la esquina (hueco reservado en la tarjeta) + secundario
    e1 = con_sombra(img(os.path.join(E, cfg["emoji"] + ".png"), 250), off=16, blur=14)
    pegar(base, e1, 905, top_card + 30, -10)
    e2 = con_sombra(img(os.path.join(E, cfg["emoji2"] + ".png"), 170), off=12, blur=12)
    pegar(base, e2, 95, cy_card + card.height / 2 - 70, 12)

    # flecha roja señalando la pregunta
    flecha(base, (70, top_card - 110), (20, top_card + 20), (150, top_card + 75))

    # pegatina gancho
    y_peg = cy_card + card.height / 2 + 15
    peg_col = (230, 30, 50) if not hall else (255, 120, 0)
    pegar(base, pegatina(cfg["pegatina"], peg_col, (255, 255, 255), size=80), 540, y_peg, 4)

    # subtítulo debajo de la pegatina + usuario abajo del todo
    d = ImageDraw.Draw(base)
    y_sub = min(y_peg + 150, 1640)
    d.text((540, y_sub), cfg["sub"], font=font(46), fill=(255, 255, 255), anchor="mm",
           stroke_width=7, stroke_fill=dark)
    pill(base, 540, min(y_sub + 90, 1665), "5 PREGUNTAS + 1 EXTRA", 40, (255, 255, 255), dark)
    fu = font(44)
    w = d.textlength(USUARIO, font=fu)
    d.rounded_rectangle((540 - w / 2 - 34, 1735, 540 + w / 2 + 34, 1805), 35, fill=(0, 0, 0, 120))
    d.text((540, 1772), USUARIO, font=fu, fill=(255, 255, 255), anchor="mm")
    print(video, "pegatina y =", int(y_peg), "sub y =", int(y_sub))

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

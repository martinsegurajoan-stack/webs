#!/usr/bin/env python3
"""Portadas de HISTORIAS DESTACADAS de Instagram (1080x1080, todo lo importante dentro del círculo).

  python3 destacadas.py  → portadas/destacadas/<nombre>.png + hoja de muestra del perfil
Mismo concepto en todas (fondo radial, aros, destellos, dibujo 3D grande, rayo de marca); cambia el color.
"""
import colorsys
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
EMOJI = os.environ.get("EMOJI_DIR", os.path.join(BASE, "assets", "destacadas"))
OUT = os.path.join(BASE, "portadas", "destacadas")
S = 1080
C = S // 2

# nombre, tono, emoji principal, detalle
CATS = [
    ("quiz", 46, "1f9e0", "pregunta"),
    ("parejas", 335, "1f49e", "corazones"),
    ("retos", 0, "1f3af", "niveles"),
    ("streamers", 268, "1f3ae", "live"),
    ("fiesta", 182, "1f37b", "confeti"),
    ("mascotas", 118, "1f436", "huellas"),
    ("personalidad", 222, "1f3ad", "letras"),
]


def hsv(h, s, v, a=255):
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360, s, v)
    return (int(r * 255), int(g * 255), int(b * 255), a)


def emoji(code, size):
    im = Image.open(os.path.join(EMOJI, code + ".png")).convert("RGBA")
    return im.resize((size, size), Image.LANCZOS)


def paste_c(img, spr, cx, cy, angle=0, shadow=True):
    if angle:
        spr = spr.rotate(angle, resample=Image.BICUBIC, expand=True)
    x, y = int(cx - spr.width / 2), int(cy - spr.height / 2)
    if shadow:
        sh = Image.new("RGBA", spr.size, (0, 0, 0, 0))
        sh.putalpha(spr.getchannel("A").point(lambda a: int(a * 0.35)))
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        img.alpha_composite(sh, (x + 8, y + 22))
    img.alpha_composite(spr, (x, y))


def star(d, x, y, r, col):
    pts = []
    for k in range(8):
        a = k * math.pi / 4 - math.pi / 2
        rr = r if k % 2 == 0 else r * 0.28
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    d.polygon(pts, fill=col)


def portada(nombre, h, code, detalle):
    img = Image.new("RGBA", (S, S))
    # fondo radial
    px = img.load()
    c0, c1 = hsv(h, 0.45, 1.0), hsv(h - (8 if nombre == "quiz" else 0), 0.95, {"retos": 0.5, "quiz": 0.85}.get(nombre, 0.62))
    for y in range(S):
        for x in range(S):
            k = min(1.0, math.hypot(x - C, y - C * 0.92) / (S * 0.72))
            k = k ** 1.2
            px[x, y] = tuple(int(c0[i] + (c1[i] - c0[i]) * k) for i in range(3)) + (255,)
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    # rayos suaves
    for k in range(16):
        a0 = k * 2 * math.pi / 16
        d.polygon([(C, C), (C + math.cos(a0) * 900, C + math.sin(a0) * 900),
                   (C + math.cos(a0 + 0.17) * 900, C + math.sin(a0 + 0.17) * 900)], fill=(255, 255, 255, 22))
    # bokeh
    r = random.Random(h)
    for _ in range(26):
        x, y, rad = r.uniform(0, S), r.uniform(0, S), r.uniform(8, 34)
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(255, 255, 255, r.randint(18, 50)))
    img.alpha_composite(lay)
    d = ImageDraw.Draw(img)
    # aros
    d.ellipse((C - 452, C - 452, C + 452, C + 452), outline=(255, 255, 255, 120), width=4)
    for k in range(60):  # aro punteado
        a = k * 2 * math.pi / 60
        x, y = C + math.cos(a) * 420, C + math.sin(a) * 420
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 255, 255, 170))
    # disco interior con brillo
    disc = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dd = ImageDraw.Draw(disc)
    dd.ellipse((C - 372, C - 372 + 16, C + 372, C + 372 + 16), fill=hsv(h, 0.9, 0.35, 120))
    dd.ellipse((C - 372, C - 372, C + 372, C + 372), fill=hsv(h, 0.3, 1.0, 255), outline=(255, 255, 255, 255), width=12)
    img.alpha_composite(disc.filter(ImageFilter.GaussianBlur(0.6)))
    hl = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse((C - 260, C - 330, C + 200, C - 120), fill=(255, 255, 255, 90))
    img.alpha_composite(hl.filter(ImageFilter.GaussianBlur(40)))
    d = ImageDraw.Draw(img)
    # detalle propio de cada categoría (todo dentro del círculo)
    if detalle == "niveles":  # 6 niveles: 5 verdes/amarillos/naranja/rojo y el imposible
        cols = [(60, 200, 90), (250, 210, 40), (255, 150, 30), (240, 70, 50), (150, 60, 200), (20, 20, 25)]
        for i, col in enumerate(cols):
            a = math.radians(-150 + i * 24)
            x, y = C + math.cos(a) * 420, C + math.sin(a) * 420
            d.ellipse((x - 30, y - 30, x + 30, y + 30), fill=col + (255,), outline=(255, 255, 255, 255), width=6)
        paste_c(img, emoji("1f480", 120), C + math.cos(math.radians(-30)) * 420, C + math.sin(math.radians(-30)) * 420 - 4)
    if detalle == "letras":  # chips A-D del test de personalidad sobre el aro
        from PIL import ImageFont
        fl = ImageFont.truetype(os.path.join(BASE, "fuentes", "titulo.ttf"), 46)
        cols = [((255, 212, 0), (20, 14, 30)), ((0, 222, 205), (20, 14, 30)), ((138, 58, 255), (255, 255, 255)),
                ((26, 18, 44), (255, 255, 255))]
        for i, (bg, fg) in enumerate(cols):
            a = math.radians(-168 + i * 30)
            x, y = C + math.cos(a) * 420, C + math.sin(a) * 420
            d.ellipse((x - 38, y - 38, x + 38, y + 38), fill=bg + (255,), outline=(255, 255, 255, 255), width=6)
            d.text((x, y + 2), "ABCD"[i], font=fl, fill=fg + (255,), anchor="mm")
    paste_c(img, emoji(code, 590), C, C - 15)
    d = ImageDraw.Draw(img)
    if detalle == "pregunta":
        paste_c(img, emoji("2753", 170), C + 250, C - 235, angle=-14)
    elif detalle == "corazones":
        paste_c(img, emoji("1f495", 150), C + 255, C - 230, angle=-12)
    elif detalle == "live":
        x0, y0 = C + 150, C - 300
        d.rounded_rectangle((x0, y0, x0 + 200, y0 + 78), 39, fill=(235, 25, 60, 255), outline=(255, 255, 255, 255), width=6)
        d.ellipse((x0 + 26, y0 + 25, x0 + 54, y0 + 53), fill=(255, 255, 255, 255))
        try:
            from PIL import ImageFont
            f = ImageFont.truetype(os.path.join(BASE, "fuentes", "titulo.ttf"), 44)
            d.text((x0 + 125, y0 + 41), "LIVE", font=f, fill=(255, 255, 255, 255), anchor="mm")
        except OSError:
            pass
    elif detalle == "confeti":
        paste_c(img, emoji("1f973", 160), C + 250, C - 230, angle=-12)
        for k in range(18):
            a = r.uniform(0, 2 * math.pi)
            rad = r.uniform(250, 360)
            x, y = C + math.cos(a) * rad, C + math.sin(a) * rad
            col = hsv(r.choice([46, 335, 200, 120, 25]), 0.8, 1.0)
            d.rounded_rectangle((x - 9, y - 5, x + 9, y + 5), 3, fill=col)
    elif detalle == "letras":
        paste_c(img, emoji("1f52e", 160), C + 255, C - 225, angle=-12)
    elif detalle == "huellas":
        paste_c(img, emoji("1f43e", 160), C + 250, C - 230, angle=-14)
    # destellos
    for (x, y, rr) in [(C - 300, C - 230, 34), (C - 250, C + 260, 24), (C + 300, C + 200, 30), (C - 340, C + 40, 18)]:
        star(d, x, y, rr, (255, 255, 255, 235))
    # rayo de marca abajo
    d.ellipse((C - 62, C + 300, C + 62, C + 424), fill=(255, 214, 0, 255), outline=(255, 255, 255, 255), width=8)
    paste_c(img, emoji("26a1", 84), C, C + 362, shadow=False)
    out = os.path.join(OUT, f"destacada_{nombre}.png")
    img.convert("RGB").save(out)
    return out


def hoja(paths):
    """Simula la fila de destacadas del perfil para comprobar que el conjunto queda estético."""
    w = len(paths) * 190 + 40
    im = Image.new("RGB", (w, 260), (255, 255, 255))
    d = ImageDraw.Draw(im)
    from PIL import ImageFont
    f = ImageFont.truetype(os.path.join(BASE, "fuentes", "texto.ttf"), 26)
    for i, p in enumerate(paths):
        x = 20 + i * 190 + 15
        a = Image.open(p).resize((150, 150), Image.LANCZOS)
        m = Image.new("L", (150, 150), 0)
        ImageDraw.Draw(m).ellipse((0, 0, 149, 149), fill=255)
        d.ellipse((x - 6, 24, x + 156, 186), outline=(200, 200, 200), width=3)
        im.paste(a, (x, 30), m)
        d.text((x + 75, 220), CATS[i][0].capitalize(), font=f, fill=(20, 20, 20), anchor="mm")
    return im


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    paths = [portada(*c) for c in CATS]
    print("\n".join(paths))
    if len(sys.argv) > 1:
        hoja(paths).save(sys.argv[1])

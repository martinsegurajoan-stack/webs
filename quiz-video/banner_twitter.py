#!/usr/bin/env python3
"""Banner de cabecera para Twitter/X: 1500x500 (3:1). La foto de perfil tapa la esquina inferior izquierda
(~450x250 px), así que lo importante va a la derecha de x=470 y dentro de la franja central (y 70-430)."""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from quizvideo.render import font, tfont  # noqa: E402

W, H = 1500, 500
A = os.path.join(BASE, "assets")
YEL, TURQ, MOR, DARK, WHITE = (255, 212, 0), (0, 222, 205), (138, 58, 255), (24, 8, 46), (255, 255, 255)


def spr(path, size, ang=0):
    im = Image.open(os.path.join(A, path)).convert("RGBA").resize((size, size), Image.LANCZOS)
    return im.rotate(ang, Image.BICUBIC, expand=True) if ang else im


def paste(img, im, cx, cy, shadow=True):
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        sh.putalpha(im.getchannel("A").point(lambda v: int(v * 0.35)))
        sh = sh.filter(ImageFilter.GaussianBlur(8))
        img.paste(sh, (int(cx - im.width / 2 + 6), int(cy - im.height / 2 + 10)), sh)
    img.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)


def text(d, xy, s, f, fill, stroke, sfill, anchor="mm"):
    d.text((xy[0] + 5, xy[1] + 8), s, font=f, fill=(0, 0, 0, 90), anchor=anchor, stroke_width=stroke,
           stroke_fill=(0, 0, 0, 90))
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sfill)


def pill(d, cx, cy, s, size, bg, fg, pad=(28, 12)):
    f = tfont(size)
    w = d.textlength(s, font=f)
    box = (cx - w / 2 - pad[0], cy - size / 2 - pad[1], cx + w / 2 + pad[0], cy + size / 2 + pad[1])
    r = (box[3] - box[1]) / 2
    d.rounded_rectangle((box[0] + 4, box[1] + 7, box[2] + 4, box[3] + 7), r, fill=(0, 0, 0, 70))
    d.rounded_rectangle(box, r, fill=bg)
    d.text((cx, cy + 2), s, font=f, fill=fg, anchor="mm")


def main():
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    top, bot = np.array((96, 30, 190)), np.array((18, 8, 40))
    k = np.clip(0.75 * y + 0.35 * (1 - x), 0, 1)[..., None]
    arr = top * (1 - k) + bot * k
    g = np.exp(-(((x - 0.62) / 0.28) ** 2 + ((y - 0.5) / 0.6) ** 2))[..., None]
    arr = arr + g * np.array((60, 40, 120))
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy = 930, 250
    for i in range(28):
        a0 = i * math.pi / 14
        d.polygon([(cx, cy), (cx + 1800 * math.cos(a0), cy + 1800 * math.sin(a0)),
                   (cx + 1800 * math.cos(a0 + math.pi / 28), cy + 1800 * math.sin(a0 + math.pi / 28))],
                  fill=(255, 255, 255, 22))
    rs = random.Random(3)
    cols = [YEL, TURQ, (255, 64, 160), WHITE]
    for _ in range(46):  # confeti y destellos
        px, py, s = rs.uniform(0, W), rs.uniform(0, H), rs.uniform(5, 12)
        c = rs.choice(cols)
        if rs.random() < 0.5:
            d.polygon([(px, py - s * 2.4), (px + s * 0.7, py), (px, py + s * 2.4), (px - s * 0.7, py)], fill=c + (170,))
        else:
            ang = rs.uniform(0, 6.28)
            d.polygon([(px + s * math.cos(ang + j * math.pi / 2) * (1 if j % 2 else 0.45),
                        py + s * math.sin(ang + j * math.pi / 2) * (1 if j % 2 else 0.45)) for j in range(4)],
                      fill=c + (150,))
    # emojis 3D alrededor (fuera de la zona de la foto de perfil)
    for path, size, px, py, ang in [("niveles2/cerebro.png", 120, 560, 105, -14), ("fiesta/mando.png" if os.path.exists(os.path.join(A, "fiesta/mando.png")) else "decor_gamer/mando.png", 110, 1395, 400, 12),
                                    ("portada/interrogacion.png", 110, 1430, 95, 14), ("fiesta/bomba.png", 96, 520, 400, -10),
                                    ("imagenes/trofeo_3d.png", 100, 1300, 130, 8), ("imagenes/calavera_3d.png", 80, 1180, 430, -8),
                                    ("fiesta/confeti.png", 100, 120, 110, -12), ("fiesta/rayo.png", 90, 330, 70, 10)]:
        paste(img, spr(path, size, ang), px, py)
    d = ImageDraw.Draw(img, "RGBA")
    pill(d, 930, 88, "QUIZZES · RETOS · JUEGOS CON AMIGOS", 30, WHITE, (70, 20, 140))
    text(d, (900, 196), "¡ES HORA", tfont(118), WHITE, 11, DARK)
    text(d, (930, 305), "DEL QUIZ!", tfont(134), YEL, 12, DARK)
    paste(img, spr("fiesta/rayo.png", 120, -12), 1262, 290)
    d = ImageDraw.Draw(img, "RGBA")
    pill(d, 930, 400, "¿LLEGAS AL ÚLTIMO NIVEL?", 34, (239, 45, 70), WHITE, pad=(30, 13))
    logo = Image.open(os.path.join(A, "logo.png")).convert("RGBA").resize((150, 150), Image.LANCZOS)
    m = Image.new("L", logo.size, 0)
    ImageDraw.Draw(m).ellipse((0, 0, 149, 149), fill=255)
    logo.putalpha(m)
    paste(img, logo, 1385, 250)
    out = os.path.join(BASE, "portadas", "twitter_banner_1500x500.png")
    img.convert("RGB").save(out, optimize=True)
    print(out, os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    main()

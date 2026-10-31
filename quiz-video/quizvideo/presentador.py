"""DON QUIZÁS — presentador fijo de Hora del Quiz ⚡ (dibujado por código, siempre idéntico).

Rasgos FIJOS (no cambiar nunca): cabeza grande y redonda, tupé amarillo eléctrico con forma de
rayo, bigotón castaño rizado, nariz redonda, cejas gruesas, mejillas sonrosadas, diente separado.
Lo que cambia en cada vídeo: el traje (TRAJES) y el plató (PLATOS).

    from quizvideo.presentador import presentador, plato
    img = presentador("clasico", "feliz", boca=0.6)   # RGBA 600x900
"""

import math
import os

from PIL import Image, ImageDraw, ImageFilter

K = 2  # se dibuja al doble y se reduce (bordes suaves)
W0, H0 = 600, 900

SKIN = (255, 206, 165)
SKIN_D = (232, 170, 130)
HAIR = (255, 212, 0)
HAIR_D = (215, 160, 0)
STACHE = (88, 50, 28)
STACHE_D = (60, 32, 18)
INK = (30, 18, 40)

TRAJES = {
    # chaqueta, solapa, camisa, pajarita/corbata, extra
    "clasico": {"chaqueta": (128, 52, 235), "solapa": (255, 212, 0), "camisa": (255, 255, 255),
                "pajarita": (255, 212, 0), "extra": "lentejuelas"},
    "personalidad": {"chaqueta": (0, 200, 190), "solapa": (255, 212, 0), "camisa": (30, 18, 40),
                     "pajarita": (255, 64, 160), "extra": None},
    "halloween": {"chaqueta": (25, 18, 35), "solapa": (120, 20, 40), "camisa": (255, 255, 255),
                  "pajarita": (255, 130, 0), "extra": "capa"},
    "parejas": {"chaqueta": (225, 40, 90), "solapa": (255, 170, 200), "camisa": (255, 255, 255),
                "pajarita": (180, 0, 50), "extra": "rosa"},
    "trivial": {"chaqueta": (30, 120, 255), "solapa": (20, 60, 160), "camisa": (255, 255, 255),
                "pajarita": (255, 90, 60), "extra": "lentejuelas"},
}

EXPRESIONES = ["feliz", "sorprendido", "picaro", "riendo", "sospecha"]


def _p(pts):
    return [(x * K, y * K) for x, y in pts]


def _box(x0, y0, x1, y1):
    return (x0 * K, y0 * K, x1 * K, y1 * K)


def _heart(d, cx, cy, s, col):
    pts = []
    for k in range(40):
        u = k / 40 * 2 * math.pi
        x = 16 * math.sin(u) ** 3
        y = -(13 * math.cos(u) - 5 * math.cos(2 * u) - 2 * math.cos(3 * u) - math.cos(4 * u))
        pts.append((cx + x * s / 17, cy + y * s / 17))
    d.polygon(_p(pts), fill=col)


def _bolt(d, cx, cy, s, col, outline=None):
    pts = [(0.15, -1), (-0.55, 0.12), (-0.05, 0.12), (-0.25, 1), (0.55, -0.2), (0.05, -0.2), (0.35, -1)]
    d.polygon(_p([(cx + x * s, cy + y * s) for x, y in pts]), fill=col, outline=outline,
              width=3 * K if outline else 0)


def _cuerpo(d, img, traje, gesto):
    t = TRAJES[traje]
    ch, so, ca, pa = t["chaqueta"], t["solapa"], t["camisa"], t["pajarita"]
    dark = tuple(int(c * 0.72) for c in ch)
    if t["extra"] == "capa":  # capa de vampiro detrás
        d.polygon(_p([(150, 470), (450, 470), (560, 900), (40, 900)]), fill=(20, 10, 25))
        d.polygon(_p([(170, 490), (430, 490), (520, 900), (80, 900)]), fill=(150, 15, 40))
        d.polygon(_p([(150, 470), (95, 380), (205, 455)]), fill=(20, 10, 25))
        d.polygon(_p([(450, 470), (505, 380), (395, 455)]), fill=(20, 10, 25))
    # cuello
    d.rectangle(_box(262, 440, 338, 480), fill=SKIN_D)
    # brazo derecho: dedo arriba ("¿quizás?") o abierto
    if gesto == "dedo":
        d.polygon(_p([(425, 525), (482, 520), (520, 420), (470, 400)]), fill=dark)
        d.ellipse(_box(462, 335, 542, 425), fill=SKIN)
        d.rounded_rectangle(_box(494, 255, 524, 360), 15 * K, fill=SKIN)
        d.ellipse(_box(498, 262, 518, 282), fill=(255, 225, 200))
    else:
        d.polygon(_p([(425, 525), (482, 520), (560, 600), (520, 640)]), fill=dark)
        d.ellipse(_box(515, 570, 595, 650), fill=SKIN)
    # chaqueta
    d.polygon(_p([(110, 520), (250, 470), (350, 470), (490, 520), (520, 900), (80, 900)]), fill=ch)
    # camisa en V
    d.polygon(_p([(250, 470), (350, 470), (300, 650)]), fill=ca)
    # solapas
    d.polygon(_p([(250, 470), (300, 650), (265, 680), (215, 520)]), fill=so)
    d.polygon(_p([(350, 470), (300, 650), (335, 680), (385, 520)]), fill=so)
    # botones
    for y in (700, 770):
        d.ellipse(_box(290, y, 310, y + 20), fill=so)
    # lentejuelas / rosa / corazones
    if t["extra"] == "lentejuelas":
        import random
        r = random.Random(3)
        for _ in range(70):
            x, y = r.uniform(110, 490), r.uniform(530, 890)
            if abs(x - 300) < 70 and y < 690:
                continue
            s = r.uniform(3, 6)
            d.ellipse(_box(x - s, y - s, x + s, y + s), fill=(255, 255, 255, 140))
    if t["extra"] == "rosa":
        d.ellipse(_box(380, 540, 420, 580), fill=(200, 0, 40))
        d.ellipse(_box(388, 548, 412, 572), fill=(255, 60, 90))
        d.line(_p([(400, 578), (392, 615)]), fill=(40, 140, 60), width=5 * K)
        for x, y in [(160, 760), (440, 820), (200, 860)]:
            _heart(d, x, y, 20, (255, 170, 200))
    # brazo izquierdo con el micro (delante de la chaqueta)
    d.polygon(_p([(108, 522), (168, 528), (212, 640), (160, 668)]), fill=dark)
    d.rounded_rectangle(_box(178, 520, 206, 640), 12 * K, fill=(45, 45, 55))
    d.rounded_rectangle(_box(170, 560, 214, 600), 8 * K, fill=(255, 212, 0))
    _bolt(d, 192, 580, 15, INK)
    d.ellipse(_box(160, 470, 224, 534), fill=(75, 75, 90))
    d.ellipse(_box(168, 478, 216, 526), fill=(120, 120, 135))
    for k in range(3):
        d.line(_p([(178 + k * 14, 482), (178 + k * 14, 522)]), fill=(85, 85, 100), width=2 * K)
    d.ellipse(_box(158, 610, 228, 680), fill=SKIN)
    d.ellipse(_box(198, 600, 232, 640), fill=SKIN)
    # pajarita
    d.polygon(_p([(300, 492), (250, 470), (250, 520)]), fill=pa)
    d.polygon(_p([(300, 492), (350, 470), (350, 520)]), fill=pa)
    d.ellipse(_box(286, 480, 314, 506), fill=tuple(int(c * 0.8) for c in pa))


def _cabeza(d, expr, boca, parpadeo, mirada):
    # orejas
    for x in (150, 450):
        d.ellipse(_box(x - 28, 280, x + 28, 350), fill=SKIN_D)
        d.ellipse(_box(x - 16, 293, x + 16, 337), fill=SKIN)
    # cara
    d.ellipse(_box(148, 130, 452, 470), fill=SKIN)
    # patillas
    for x0 in (152, 418):
        d.rounded_rectangle(_box(x0, 205, x0 + 30, 300), 14 * K, fill=HAIR_D)
    # tupé-rayo: gran ola amarilla con un rayo que sale hacia arriba
    d.ellipse(_box(150, 95, 455, 255), fill=HAIR_D)
    d.ellipse(_box(158, 85, 448, 240), fill=HAIR)
    d.polygon(_p([(300, 110), (250, 10), (330, 70), (318, 0), (400, 105)]), fill=HAIR_D)
    d.polygon(_p([(305, 112), (262, 30), (330, 80), (325, 18), (390, 108)]), fill=HAIR)
    d.ellipse(_box(165, 175, 300, 245), fill=HAIR)  # flequillo
    d.arc(_box(185, 120, 330, 230), 200, 330, fill=HAIR_D, width=5 * K)
    d.arc(_box(260, 110, 430, 220), 210, 320, fill=HAIR_D, width=5 * K)
    # cejas
    cej = {"feliz": (-8, 8, 0), "sorprendido": (-14, 14, -18), "picaro": (12, -18, -6),
           "riendo": (-6, 6, 4), "sospecha": (14, -14, 6)}[expr]
    for side, ang in ((-1, cej[0]), (1, cej[1])):
        cx, cy = 300 + side * 58, 255 + cej[2] + (12 if (expr == "picaro" and side == -1) else 0)
        br = Image.new("RGBA", (90 * K, 30 * K), (0, 0, 0, 0))
        ImageDraw.Draw(br).rounded_rectangle((0, 0, 90 * K - 1, 26 * K), 13 * K, fill=STACHE)
        br = br.rotate(ang * side * -1, Image.BICUBIC, expand=True)
        d._image.alpha_composite(br, (int(cx * K - br.width / 2), int(cy * K - br.height / 2)))
    # ojos
    for side in (-1, 1):
        cx, cy = 300 + side * 55, 290
        ry = {"sorprendido": 48, "sospecha": 20}.get(expr, 40)
        if parpadeo or expr == "riendo":
            d.arc(_box(cx - 34, cy - 20, cx + 34, cy + 24), 200, 340, fill=INK, width=7 * K)
            continue
        if expr == "picaro" and side == 1:
            ry = 26
        d.ellipse(_box(cx - 36, cy - ry, cx + 36, cy + ry), fill=(255, 255, 255), outline=INK, width=4 * K)
        px, py = cx + mirada[0] * 12, cy + mirada[1] * 10
        pr = 18 if expr != "sorprendido" else 14
        d.ellipse(_box(px - pr, py - pr, px + pr, py + pr), fill=INK)
        d.ellipse(_box(px - pr * 0.6 + 6, py - pr * 0.6, px - pr * 0.6 + 14, py - pr * 0.6 + 8),
                  fill=(255, 255, 255))
    # mejillas
    for x in (200, 400):
        d.ellipse(_box(x - 28, 330, x + 28, 360), fill=(255, 140, 140, 110))
    # boca (debajo del bigote)
    o = max(boca, {"sorprendido": 0.8, "riendo": 1.0}.get(expr, 0.0))
    if o > 0.05:
        h = 12 + 30 * o
        d.chord(_box(256, 388 - h, 344, 388 + h), 0, 180, fill=(120, 20, 40))
        d.ellipse(_box(278, 388 + h * 0.35, 322, 388 + h * 0.92), fill=(255, 110, 130))
        d.rectangle(_box(264, 386, 296, 399), fill=(255, 255, 255))  # dientes con hueco
        d.rectangle(_box(304, 386, 336, 399), fill=(255, 255, 255))
    elif expr == "picaro":
        d.arc(_box(258, 362, 360, 420), 10, 150, fill=(120, 20, 40), width=6 * K)
    else:
        d.arc(_box(255, 362, 345, 420), 20, 160, fill=(120, 20, 40), width=6 * K)
    # nariz
    d.ellipse(_box(268, 298, 332, 352), fill=(240, 150, 120))
    d.ellipse(_box(282, 308, 300, 322), fill=(255, 200, 180))
    # bigotón rizado
    for side in (-1, 1):
        d.chord(_box(300 - (115 if side < 0 else -10) - (0 if side < 0 else 105), 334,
                     300 + (10 if side < 0 else 115), 394), 180, 360, fill=STACHE)
        d.ellipse(_box(300 + side * 100 - 22, 324, 300 + side * 100 + 22, 368), fill=STACHE)
        d.ellipse(_box(300 + side * 100 - 9 + side * 4, 334, 300 + side * 100 + 9 + side * 4, 352),
                  fill=SKIN)
        d.ellipse(_box(300 + side * 112 - 13, 312, 300 + side * 112 + 13, 338), fill=STACHE)
    d.ellipse(_box(255, 332, 345, 374), fill=STACHE)
    d.arc(_box(262, 338, 338, 370), 200, 340, fill=STACHE_D, width=4 * K)


def presentador(traje="clasico", expresion="feliz", boca=0.0, parpadeo=False, mirada=(0, 0),
                gesto="dedo", escala=1.0):
    """Devuelve a Don Quizás (RGBA 600x900 × escala)."""
    img = Image.new("RGBA", (W0 * K, H0 * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _cuerpo(d, img, traje, gesto)
    _cabeza(d, expresion, boca, parpadeo, mirada)
    if traje == "halloween":  # colmillos de vampiro de broma
        d.polygon(_p([(268, 380), (282, 380), (275, 410)]), fill=(255, 255, 255))
        d.polygon(_p([(318, 380), (332, 380), (325, 410)]), fill=(255, 255, 255))
    out = img.resize((int(W0 * escala), int(H0 * escala)), Image.LANCZOS)
    return out


# ---------------------------------------------------------------- platós

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")


def _grad(w, h, top, bot):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return im.convert("RGBA")


PLATOS = {
    "clasico": {"top": (70, 20, 150), "bot": (15, 5, 35), "foco": (255, 230, 120), "suelo": (255, 212, 0),
                "nombre": "Plató concurso"},
    "personalidad": {"top": (40, 10, 90), "bot": (5, 5, 20), "foco": (0, 222, 205), "suelo": (0, 222, 205),
                     "nombre": "Plató neón"},
    "halloween": {"top": (40, 15, 70), "bot": (8, 4, 18), "foco": (255, 140, 30), "suelo": (255, 120, 0),
                  "nombre": "Plató encantado"},
    "parejas": {"top": (255, 110, 160), "bot": (120, 20, 70), "foco": (255, 220, 235), "suelo": (255, 170, 200),
                "nombre": "Plató romántico"},
    "trivial": {"top": (20, 90, 220), "bot": (5, 20, 60), "foco": (255, 255, 255), "suelo": (0, 200, 255),
                "nombre": "Plató trivial"},
}


def plato(nombre, w=1080, h=1920):
    p = PLATOS[nombre]
    bg = _grad(w, h, p["top"], p["bot"])
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    # focos que bajan del techo
    for k, x in enumerate([w * 0.12, w * 0.5, w * 0.88]):
        d.polygon([(x - 30, 0), (x + 30, 0), (x + w * 0.28, h * 0.82), (x - w * 0.28, h * 0.82)],
                  fill=p["foco"] + (38,))
    # suelo de plató con rejilla en perspectiva
    hy = int(h * 0.7)
    d.rectangle((0, hy, w, h), fill=(0, 0, 0, 90))
    for k in range(-10, 11):
        d.line([(w / 2 + k * 40, hy), (w / 2 + k * w * 0.2, h)], fill=p["suelo"] + (70,), width=3)
    for k in range(8):
        y = hy + (h - hy) * (k / 8) ** 1.6
        d.line([(0, y), (w, y)], fill=p["suelo"] + (60,), width=3)
    # bombillas de concurso en el arco
    for k in range(18):
        a = math.pi * (k / 17)
        x, y = w / 2 - math.cos(a) * w * 0.46, h * 0.45 - math.sin(a) * h * 0.3
        d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=p["suelo"] + (230,))
        d.ellipse((x - 26, y - 26, x + 26, y + 26), outline=p["suelo"] + (70,), width=4)
    bg.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1)))
    deco = ImageDraw.Draw(bg)
    if nombre == "halloween":
        for f, x, y, s in [("luna", 0.8, 0.12, 0.22), ("calabaza", 0.12, 0.78, 0.18), ("calabaza", 0.88, 0.8, 0.15),
                           ("murcielago", 0.2, 0.18, 0.12), ("murcielago", 0.62, 0.25, 0.09)]:
            pth = os.path.join(ASSETS, "decor_halloween", f + ".png")
            if os.path.exists(pth):
                im = Image.open(pth).convert("RGBA")
                sz = int(w * s)
                im = im.resize((sz, sz), Image.LANCZOS)
                bg.alpha_composite(im, (int(w * x - sz / 2), int(h * y - sz / 2)))
    if nombre == "parejas":
        import random
        r = random.Random(5)
        for _ in range(26):
            x, y, s = r.uniform(0, w), r.uniform(0, h * 0.7), r.uniform(w * 0.02, w * 0.05)
            pts = []
            for k in range(30):
                u = k / 30 * 2 * math.pi
                pts.append((x + 16 * math.sin(u) ** 3 * s / 17,
                            y - (13 * math.cos(u) - 5 * math.cos(2 * u) - 2 * math.cos(3 * u) - math.cos(4 * u)) * s / 17))
            deco.polygon(pts, fill=(255, 220, 235))
    if nombre in ("personalidad", "clasico", "trivial"):
        for k, (x, y) in enumerate([(0.14, 0.2), (0.86, 0.26), (0.5, 0.08)]):
            s = w * 0.06
            pts = [(0.15, -1), (-0.55, 0.12), (-0.05, 0.12), (-0.25, 1), (0.55, -0.2), (0.05, -0.2), (0.35, -1)]
            deco.polygon([(w * x + a * s, h * y + b * s) for a, b in pts], fill=(255, 212, 0))
    # atril del concurso
    aw, ah = w * 0.56, h * 0.16
    ax, ay = w / 2 - aw / 2, h * 0.84
    deco.polygon([(ax, ay), (ax + aw, ay), (ax + aw * 0.9, ay + ah), (ax + aw * 0.1, ay + ah)], fill=(20, 12, 30))
    deco.rectangle((ax, ay, ax + aw, ay + h * 0.02), fill=p["suelo"])
    return bg

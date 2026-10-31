"""Piezas del quiz de MÉXICO: bandera que ondea, papel picado y franja de sarape (todo dibujado por código).

Se usan en el vídeo (`render.py`, modo "mexico") y en la portada (`portada.py`).
"""

import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
DECOR = os.path.join(ASSETS, "decor_mexico")

VERDE, BLANCO, ROJO = (0, 104, 71), (255, 255, 255), (206, 17, 38)
# colores del papel picado y del sarape
FIESTA = [(228, 0, 124), (255, 128, 0), (255, 205, 0), (0, 178, 190), (130, 50, 200), (60, 180, 75), (230, 30, 50)]


def sprite(name, size):
    im = Image.open(os.path.join(DECOR, name + ".png")).convert("RGBA")
    k = size / max(im.size)
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)


def _escudo(size):
    """Escudo simplificado: águila sobre un nopal, con corona de laurel verde y lazo tricolor."""
    s = size
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    # corona de laurel: hojas a lo largo de un arco por debajo del águila
    R = s * 0.40
    for side in (-1, 1):
        for k in range(9):
            th = math.radians(100 + k * 10.5)  # desde abajo hacia arriba por cada lado
            x = c + side * R * math.cos(th - math.pi / 2) * -1
            y = c + 0.05 * s + R * math.sin(th - math.pi / 2) * -1
            x = c - side * R * math.sin(th)
            y = c + 0.05 * s - R * math.cos(th)
            r = s * 0.05
            leaf = Image.new("RGBA", (int(r * 3.4), int(r * 2)), (0, 0, 0, 0))
            ImageDraw.Draw(leaf).ellipse((1, 1, leaf.width - 2, leaf.height - 2), fill=(46, 130, 56),
                                         outline=(22, 84, 34), width=2)
            leaf = leaf.rotate(-side * (k * 10.5 + 10) + 90 * side, resample=Image.BICUBIC, expand=True)
            im.alpha_composite(leaf, (int(x - leaf.width / 2), int(y - leaf.height / 2)))
    # lazo tricolor abajo
    for i, col in enumerate((VERDE, BLANCO, ROJO)):
        d.rectangle((c - s * 0.15 + i * s * 0.1, c + s * 0.40, c - s * 0.05 + i * s * 0.1, c + s * 0.47), fill=col)
    # nopal y águila (dibujos 3D)
    nop = sprite("cactus", int(s * 0.46))
    im.alpha_composite(nop, (int(c - nop.width / 2), int(c + s * 0.38 - nop.height)))
    ag = sprite("aguila", int(s * 0.56))
    im.alpha_composite(ag, (int(c - ag.width / 2), int(c - s * 0.36)))
    return im


def bandera_plana(w, h):
    """Bandera de México (proporción 4:7) sin ondear."""
    im = Image.new("RGBA", (w, h), BLANCO + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w // 3, h), fill=VERDE)
    d.rectangle((2 * w // 3, 0, w, h), fill=ROJO)
    esc = _escudo(int(min(w / 3 * 0.98, h * 0.62)))
    im.alpha_composite(esc, (int(w / 2 - esc.width / 2), int(h / 2 - esc.height / 2)))
    return im


class BanderaOndeando:
    """Bandera con mástil que ondea: `frame(t)` devuelve una imagen RGBA."""

    def __init__(self, w, h, amp=None, mastil=True):
        self.w, self.h = w, h
        self.amp = amp if amp is not None else h * 0.07
        self.flag = np.asarray(bandera_plana(w, h), dtype=np.float32)
        self.mastil = mastil
        self.pad = int(self.amp + 4)

    def frame(self, t, fuerza=1.0):
        w, h, pad = self.w, self.h, self.pad
        xs = np.arange(w) / w
        ph = 2 * math.pi * (1.25 * xs) - t * 5.0
        amp = self.amp * fuerza * (0.15 + 0.85 * xs ** 0.8)  # junto al mástil casi no se mueve
        off = amp * np.sin(ph)
        slope = np.gradient(off)
        shade = np.clip(1.0 + slope * 0.9, 0.62, 1.22)
        H2 = h + 2 * pad
        yy = np.arange(H2)[:, None] - pad - off[None, :]
        src = np.clip(np.round(yy).astype(int), 0, h - 1)
        inside = (yy >= 0) & (yy <= h - 1)
        out = self.flag[src, np.arange(w)[None, :]]
        out[..., :3] *= shade[None, :, None]
        out[..., 3] *= inside
        img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
        if not self.mastil:
            return img
        full = Image.new("RGBA", (w + 40, H2 + 60), (0, 0, 0, 0))
        d = ImageDraw.Draw(full)
        d.rounded_rectangle((6, 0, 26, H2 + 60), 8, fill=(150, 110, 40))
        d.rounded_rectangle((10, 0, 18, H2 + 60), 4, fill=(230, 190, 90))
        d.ellipse((0, -6, 32, 26), fill=(255, 205, 0), outline=(170, 120, 20), width=3)
        full.alpha_composite(img, (24, 14))
        return full


def _picado(w, h, col, seed):
    """Una bandera de papel picado con agujeros (rombos, círculos, flor) y borde inferior en zigzag."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    zig = []
    n = 7
    for k in range(n * 2 + 1):
        zig.append((k * w / (n * 2), h - (0 if k % 2 == 0 else h * 0.08)))
    d.polygon([(0, 0), (w, 0)] + zig[::-1], fill=col + (235,))
    hole = (0, 0, 0, 0)
    r = random.Random(seed)
    cx, cy = w / 2, h * 0.47
    # flor central
    for k in range(8):
        a = k * math.pi / 4
        d.ellipse((cx + math.cos(a) * w * 0.15 - w * 0.07, cy + math.sin(a) * w * 0.15 - w * 0.07,
                   cx + math.cos(a) * w * 0.15 + w * 0.07, cy + math.sin(a) * w * 0.15 + w * 0.07), fill=hole)
    d.ellipse((cx - w * 0.06, cy - w * 0.06, cx + w * 0.06, cy + w * 0.06), fill=hole)
    # rombos en fila arriba y abajo
    for row_y in (h * 0.12, h * 0.82):
        for k in range(5):
            x = w * (0.14 + k * 0.18)
            s = w * 0.045
            d.polygon([(x, row_y - s), (x + s, row_y), (x, row_y + s), (x - s, row_y)], fill=hole)
    # puntitos laterales
    for k in range(4):
        for x in (w * 0.1, w * 0.9):
            y = h * (0.28 + k * 0.13)
            s = w * 0.025 * r.uniform(0.8, 1.2)
            d.ellipse((x - s, y - s, x + s, y + s), fill=hole)
    return im


class PapelPicado:
    """Guirnalda de papel picado colgando de una cuerda que cruza la pantalla."""

    def __init__(self, ancho=1080, n=9, fw=104, fh=128, y0=4, caida=46, seed=3, desfase=0):
        self.ancho, self.n, self.y0, self.caida = ancho, n, y0, caida
        self.flags = [_picado(fw, fh, FIESTA[(k + desfase) % len(FIESTA)], seed + k) for k in range(n)]
        self.fw, self.fh = fw, fh
        self.fases = [random.Random(seed * 31 + k).uniform(0, 6.28) for k in range(n)]

    def _y(self, x):
        u = x / self.ancho
        return self.y0 + self.caida * 4 * u * (1 - u)

    def draw(self, img, t, dy=0):
        d = ImageDraw.Draw(img)
        pts = [(x, self._y(x) + dy) for x in range(-20, self.ancho + 21, 20)]
        d.line(pts, fill=(250, 245, 230, 230), width=4)
        step = self.ancho / self.n
        for k, fl in enumerate(self.flags):
            x = step * (k + 0.5)
            y = self._y(x) + dy
            ang = 7 * math.sin(t * 2.1 + self.fases[k])
            im = fl.rotate(ang, resample=Image.BICUBIC, expand=True, center=(self.fw / 2, 0))
            img.alpha_composite(im, (int(x - im.width / 2), int(y - 4)))


def sarape(w, h, seed=2):
    """Franja de sarape (rayas de colores vivos con hilos finos)."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = random.Random(seed)
    y = 0
    k = 0
    while y < h:
        bh = r.choice((10, 14, 22, 30))
        col = FIESTA[k % len(FIESTA)]
        d.rectangle((0, y, w, y + bh), fill=col + (255,))
        if bh >= 22:
            d.rectangle((0, y + bh / 2 - 2, w, y + bh / 2 + 2), fill=(255, 255, 255, 200))
        y += bh
        d.rectangle((0, y, w, y + 3), fill=(30, 20, 40, 255))
        y += 3
        k += r.choice((1, 2, 3))
    return im


def sombra(im, off=12, blur=12, alpha=110, col=(0, 0, 0)):
    pad = blur * 2 + off
    out = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    sh.paste(col + (255,), (pad, pad + off), im.getchannel("A").point(lambda a: a * alpha // 255))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    out.alpha_composite(im, (pad, pad))
    return out


def talavera(s):
    """Azulejo de Talavera (azul cobalto, blanco y amarillo) con flor central."""
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    azul, ama = (24, 70, 170), (250, 190, 30)
    d.rounded_rectangle((0, 0, s - 1, s - 1), s * 0.12, fill=(250, 248, 238), outline=azul, width=max(2, s // 18))
    c = s / 2
    for k in range(8):
        a = k * math.pi / 4
        r = s * 0.26
        x, y = c + math.cos(a) * r, c + math.sin(a) * r
        pr = s * 0.11
        d.ellipse((x - pr, y - pr, x + pr, y + pr), fill=azul)
    d.ellipse((c - s * 0.15, c - s * 0.15, c + s * 0.15, c + s * 0.15), fill=ama, outline=azul, width=2)
    for (x, y) in ((0, 0), (s, 0), (0, s), (s, s)):
        d.pieslice((x - s * 0.22, y - s * 0.22, x + s * 0.22, y + s * 0.22), 0, 360, fill=azul)
    return im

import math, random, sys
sys.path.insert(0, ".")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from quizvideo.render import tfont
D = "assets/preferirias/"
Wd, Hd = 1200, 800
yy, xx = np.mgrid[0:Hd, 0:Wd]
r = np.sqrt(((xx - Wd / 2) / Wd) ** 2 + ((yy - Hd * 0.45) / Hd) ** 2)
c1, c2 = np.array([150, 60, 230.]), np.array([20, 6, 45.])
k = np.clip(r / 0.75, 0, 1)[..., None]
img = Image.fromarray((c1 * (1 - k) + c2 * k).astype(np.uint8), "RGB").convert("RGBA")
lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
for j in range(16):  # rayos suaves
    a0 = j * math.pi / 8; a1 = a0 + math.pi / 16
    d.polygon([(600, 380), (600 + 1500 * math.cos(a0), 380 + 1500 * math.sin(a0)), (600 + 1500 * math.cos(a1), 380 + 1500 * math.sin(a1))], fill=(255, 255, 255, 18))
img.alpha_composite(lay)
# luna/halo detrás de la calavera
g = Image.new("RGBA", img.size, (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((380, 140, 820, 580), fill=(255, 200, 255, 150))
img.alpha_composite(g.filter(ImageFilter.GaussianBlur(40)))
ImageDraw.Draw(img).ellipse((430, 190, 770, 530), fill=(205, 140, 255))
rnd = random.Random(4); d = ImageDraw.Draw(img)
for _ in range(60):
    x, y, s = rnd.uniform(0, Wd), rnd.uniform(0, Hd), rnd.uniform(1.5, 4)
    d.ellipse((x - s, y - s, x + s, y + s), fill=(255, 255, 255, 200))
def put(name, size, cx, cy, ang=0, sh=True):
    im = Image.open(D + name + ".png").convert("RGBA").resize((size, size), Image.LANCZOS).rotate(ang, resample=Image.BICUBIC, expand=True)
    if sh:
        s = Image.new("RGBA", img.size, (0, 0, 0, 0))
        s.paste((20, 0, 40, 160), (int(cx - im.width / 2) + 10, int(cy - im.height / 2) + 22), im.getchannel("A"))
        img.alpha_composite(s.filter(ImageFilter.GaussianBlur(14)))
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
put("calavera", 330, 600, 370)
put("calendario", 250, 215, 450, 12)
put("reloj_arena", 250, 990, 440, -12)
put("ataud", 190, 860, 650, 8)
d = ImageDraw.Draw(img)
for (x, y, s, a) in ((300, 230, 120, 14), (900, 210, 110, -12), (130, 640, 90, -8), (560, 680, 80, 6), (1100, 680, 90, 10)):
    t = Image.new("RGBA", (220, 220), (0, 0, 0, 0)); td = ImageDraw.Draw(t)
    td.text((110, 110), "?", font=tfont(s), fill=(255, 214, 0), anchor="mm", stroke_width=8, stroke_fill=(90, 0, 120))
    t = t.rotate(a, resample=Image.BICUBIC); img.alpha_composite(t, (x - 110, y - 110))
img.convert("RGB").save(D + "foto_muerte_dibujo.png")

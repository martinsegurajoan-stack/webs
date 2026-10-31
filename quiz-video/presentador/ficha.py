"""Genera la ficha de personaje de DON QUIZÁS: python3 presentador/ficha.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PIL import Image, ImageDraw
from quizvideo.presentador import presentador, plato, PLATOS, EXPRESIONES
from quizvideo.render import tfont, font

W, H = 2400, 1560
YEL, TURQ, WHITE, INK = (255, 212, 0), (0, 222, 205), (255, 255, 255), (30, 18, 40)
img = Image.new("RGBA", (W, H))
d = ImageDraw.Draw(img)
for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)], fill=(int(48 - 30 * t), int(18 - 10 * t), int(100 - 70 * t)))

def txt(x, y, s, size, fill, anchor="la", title=True, stroke=0):
    d.text((x, y), s, font=(tfont if title else font)(size), fill=fill, anchor=anchor,
           stroke_width=stroke, stroke_fill=INK)

def panel(nombre, traje, expr, x, y, w, boca=0.0, label=True):
    h = int(w * 16 / 9)
    bg = plato(nombre, 1080, 1920)
    p = presentador(traje, expr, boca=boca, escala=1.55)
    bg.alpha_composite(p, ((1080 - p.width) // 2, 1920 - p.height - 40))
    bg = bg.resize((w, h), Image.LANCZOS)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 28, fill=255)
    img.paste(bg, (x, y), m)
    d.rounded_rectangle((x, y, x + w, y + h), 28, outline=WHITE, width=5)
    if label:
        txt(x + w / 2, y + h + 18, f"{PLATOS[nombre]['nombre'].upper()}", 36, YEL, "ma")
    return h

# cabecera
txt(60, 40, "DON QUIZÁS", 120, YEL, stroke=8)
txt(60, 170, "El presentador oficial de HORA DEL QUIZ · @hora.delquiz", 40, WHITE, title=False)
txt(W - 60, 70, "«¿Quizás sí… o quizás no?»", 64, TURQ, "ra", stroke=5)
txt(W - 60, 150, "Muletilla y saludo: «¡Bienvenidos a la Hora del Quiz!»", 32, WHITE, "ra", title=False)

# personaje principal
panel("clasico", "clasico", "feliz", 60, 250, 640, boca=0.45, label=False)
txt(380, 1395, "PLATÓ CONCURSO · traje clásico", 34, YEL, "ma")

# expresiones
txt(780, 250, "EXPRESIONES", 46, YEL)
for i, e in enumerate(EXPRESIONES):
    p = presentador("clasico", e, gesto="abierto")
    head = p.crop((120, 0, 480, 470)).resize((250, 326), Image.LANCZOS)
    x = 780 + i * 312
    d.rounded_rectangle((x, 310, x + 280, 680), 30, fill=(78, 48, 140), outline=(150, 120, 210), width=3)
    img.alpha_composite(head, (x + 15, 318))
    txt(x + 140, 650, e.upper(), 30, WHITE, "mm")

# trajes y platós
txt(780, 715, "TRAJE Y PLATÓ SEGÚN EL VÍDEO", 46, YEL)
for i, (n, t, e) in enumerate([("personalidad", "personalidad", "picaro"), ("halloween", "halloween", "sospecha"),
                                ("parejas", "parejas", "riendo"), ("trivial", "trivial", "sorprendido")]):
    panel(n, t, e, 780 + i * 395, 780, 330)

# rasgos fijos
txt(W / 2, 1500, "SIEMPRE IGUAL: tupé amarillo en forma de rayo · bigotón rizado · nariz redonda · "
    "cejas gruesas · diente separado · micro con rayo", 30, WHITE, "ma", title=False)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "don_quizas_ficha.png")
img.convert("RGB").save(out, optimize=True)
print(out)

#!/usr/bin/env python3
"""Vídeo de MISTERIO CRIMINAL de Hora del Quiz.

  python3 generar_misterio.py quizzes/misterio_01.json --faltan        # voces que faltan (sin gastar)
  python3 generar_misterio.py quizzes/misterio_01.json --preview 1,20 -o /tmp/p
  python3 generar_misterio.py quizzes/misterio_01.json                 # monta salida/<video>.mp4 + portadas
"""
import argparse, json, os, subprocess, sys
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance  # noqa: E402
from quizvideo import misterio  # noqa: E402
from quizvideo.misterio import F, YEL, TURQ, WHITE  # noqa: E402


def portadas(c):
    """Miniatura cinematográfica: biblioteca + los tres sospechosos + titular."""
    W, H = 1080, 1920
    src = Image.open(os.path.join(BASE, c["imagenes"], c["portada"]["fondo"] + ".jpg")).convert("RGB")
    ch = src.height
    cw = ch * W // H
    bg = src.crop((1500 - cw // 2, 0, 1500 + cw // 2, ch)).resize((W, H), Image.LANCZOS)
    bg = ImageEnhance.Brightness(bg).enhance(0.95).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for y in range(H):  # oscurece arriba (titular) y abajo, deja ver la biblioteca en medio
        a = int(150 * max(0, 1 - y / 760) + 215 * max(0, (y - 1250) / 670))
        od.line([(0, y), (W, y)], fill=(4, 2, 10, min(235, a)))
    bg.alpha_composite(ov)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    misterio._text_shadow(lay, (W / 2, 270), c["portada"]["titulo"][0], F("titulo", 230), WHITE, "ma", blur=16)
    misterio._text_shadow(lay, (W / 2, 470), c["portada"]["titulo"][1], F("titulo", 230), YEL, "ma", blur=16)
    misterio._text_shadow(lay, (W / 2, 720), "EL ASESINATO EN LA MANSIÓN", F("semi", 46), TURQ, "ma")
    bg.alpha_composite(lay)
    # tres sospechosos
    items = [("clara", "CLARA"), ("roberto", "ROBERTO"), ("sofia", "SOFÍA")]
    cwid, chei = 310, 430
    for k, (n, nom) in enumerate(items):
        im = Image.open(os.path.join(BASE, c["imagenes"], n + ".jpg")).convert("RGB")
        fx, fy = c["focos"][n]
        hh = 1000
        ww = hh * cwid // chei
        face = im.crop((fx - ww // 2, max(0, fy - hh // 2 + 60), fx + ww // 2, max(0, fy - hh // 2 + 60) + hh))
        face = face.resize((cwid, chei), Image.LANCZOS).convert("RGBA")
        m = Image.new("L", (cwid, chei), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, cwid - 1, chei - 1), 24, fill=255)
        x = 45 + k * (cwid + 20)
        y = 850
        bg.paste(face, (x, y), m)
        ImageDraw.Draw(bg).rounded_rectangle((x, y, x + cwid, y + chei), 24, outline=(255, 255, 255, 120), width=4)
        ImageDraw.Draw(bg).text((x + cwid / 2, y + chei + 22), nom, font=F("titulo", 70), fill=WHITE, anchor="ma")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    misterio._text_shadow(lay, (W / 2, 1420), c["portada"]["sub"].upper(), F("titulo", 104), YEL, "ma", blur=12)
    ImageDraw.Draw(lay).rectangle((W / 2 - 160, 1545, W / 2 + 160, 1550), fill=TURQ)
    bg.alpha_composite(lay)
    logo = Image.open(os.path.join(BASE, "assets", "logo.png")).convert("RGBA").resize((110, 110), Image.LANCZOS)
    bg.alpha_composite(logo, (W // 2 - 55, 120))
    ImageDraw.Draw(bg).text((W / 2, 1700), "@hora.delquiz", font=F("semi", 36), fill=(255, 255, 255, 190), anchor="mm")
    rgb = bg.convert("RGB")
    os.makedirs(os.path.join(BASE, "portadas"), exist_ok=True)
    p1 = os.path.join(BASE, "portadas", f"{c['video']}_9x16.png")
    p2 = os.path.join(BASE, "portadas", f"{c['video']}_3x4.png")
    rgb.save(p1, optimize=True)
    rgb.crop((0, 240, W, 1680)).save(p2, optimize=True)
    return p1, p2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("-o", "--salida")
    ap.add_argument("--faltan", action="store_true")
    ap.add_argument("--preview")
    ap.add_argument("--solo-portadas", action="store_true")
    a = ap.parse_args()
    c = json.load(open(a.json, encoding="utf-8"))
    out = a.salida or os.path.join(BASE, "salida", c["video"] + ".mp4")
    if a.faltan:
        print(json.dumps(misterio.faltan(c), ensure_ascii=False, indent=2))
        return
    if a.solo_portadas:
        print(*portadas(c))
        return
    if a.preview:
        tl, outs = misterio.render(c, out, preview=[float(x) for x in a.preview.split(",")])
        print(f"total {tl['total']:.1f}s tempo {tl['tempo']:.3f}")
        print("\n".join(outs))
        return
    if misterio.faltan(c):
        raise SystemExit("Faltan voces: ejecuta con --faltan")
    if os.path.exists(out):
        raise SystemExit(f"Ya existe {out}: no lo sobrescribo.")
    tl, _ = misterio.render(c, out)
    j = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                                            "stream=codec_type,codec_name,width,height:format=duration",
                                            "-of", "json", out]))
    v = [s for s in j["streams"] if s["codec_type"] == "video"][0]
    au = [s for s in j["streams"] if s["codec_type"] == "audio"]
    dur = float(j["format"]["duration"])
    ok = au and v["width"] == 1080 and v["height"] == 1920 and dur <= 90
    print(("OK" if ok else "ERROR") + f": {out} · {v['width']}x{v['height']} · audio {'sí' if au else 'NO'} · "
          f"{dur:.1f}s · voz x{tl['tempo']:.3f}")
    print(*portadas(c))


if __name__ == "__main__":
    main()

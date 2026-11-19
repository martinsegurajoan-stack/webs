"""Formato "NO DIGAS LO MISMO QUE YO" (evita decir lo mismo que el narrador o quedas fuera).

El juego EMPIEZA EN EL FOTOGRAMA 0 (petición del usuario: «que empiece el juego nada más comenzar el vídeo»):
la ronda 1 hace de gancho. Cada ronda: categoría → «¡PIENSA UNA!» con cuenta atrás de 3 s → «YO HE DICHO:»
+ palabra → sello «¿TAMBIÉN? ¡FUERA!». La última ronda es la RONDA FINAL (oscura, rayos, calaveras).
Cierre: «¿En qué ronda te han eliminado?» + «¿Qué categoría quieres para la próxima?» + seguir/apoyar.
"""

import math
import os
import random
import subprocess
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from . import audio
from .fiesta import sfx_airhorn, vsay
from .niveles import paste_c, pill, pop, rr, text, username
from .personalidad import sfx_boing, sfx_impact
from .render import FPS, W, H, ease_in, ease_out, ease_out_back, font, tfont

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
DECOR = os.path.join(ASSETS, "evita")
WHITE, YEL, DARK, RED, GREEN = (255, 255, 255), (255, 214, 0), (24, 12, 40), (238, 40, 66), (40, 200, 110)
CD = 3  # segundos para pensar
# color de fondo de cada ronda (muy vivos y distintos entre sí)
COLS = [(255, 70, 140), (0, 170, 255), (255, 140, 0), (120, 200, 30), (150, 70, 255), (0, 200, 170),
        (255, 60, 60), (255, 190, 0), (60, 110, 255), (230, 60, 200)]
CONF = [YEL, (0, 230, 210), (255, 70, 170), WHITE, (160, 90, 255), (60, 220, 120), (255, 120, 40)]


def mix(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


# ------------------------------------------------------------------ audio

def build_audio(events, total, path):
    m = audio.Mixer(total)
    fx = {"whoosh": audio.sfx_whoosh(), "pop": audio.sfx_pop(), "tick": audio.sfx_tick(),
          "tick_high": audio.sfx_tick(True), "tock": audio.sfx_tock(), "heart": audio.sfx_heartbeat(),
          "riser": audio.sfx_riser(4), "impact": sfx_impact(), "boing": sfx_boing(),
          "buzz": audio.sfx_buzz_end(), "correct": audio.sfx_correct(), "applause": audio.sfx_applause(),
          "airhorn": sfx_airhorn()}
    gains = {"whoosh": 0.5, "pop": 0.6, "tick": 1.0, "tick_high": 1.3, "tock": 0.9, "heart": 0.9,
             "riser": 0.5, "impact": 0.75, "boing": 0.8, "buzz": 0.9, "correct": 0.7, "applause": 0.8,
             "airhorn": 0.7}
    boosts = [(a, b) for kind, a, b in events if kind == "music_boost"]
    for kind, what, at in events:
        if kind == "music_boost":
            continue
        if kind == "fx":
            m.add_fx(fx[what], at, gains[what])
        elif what is not None:
            m.add_voice(what, at, 1.0)
    music = audio.music_pop(total, bpm=126, seed=23)
    audio.write_wav(path, m.render(music, music_gain=0.36, boosts=boosts))


# ------------------------------------------------------------------ línea de tiempo

def build_timeline(c, voice):
    scenes, ev = [], []
    t = 0.0
    n = len(c["rondas"])
    for k, r in enumerate(c["rondas"]):
        if c.get("cta_voz") and k == int(c.get("cta_antes", n - 2)):
            # «Si has llegado hasta aquí… ¡sígueme y apoya el vídeo!» antes de la penúltima ronda
            sig, d = vsay(voice, c["cta_voz"])
            ev += [("fx", "whoosh", t), ("fx", "pop", t + 0.2), ("voice", sig, t + 0.15), ("fx", "correct", t + 0.15 + d * 0.6)]
            dur = max(2.8, 0.15 + d + 0.35)
            scenes.append({"kind": "cta", "start": t, "dur": dur, "k": k, "n": n})
            t += dur
        st = t
        final = k == n - 1
        cd = r.get("segundos", 4 if final else CD)
        v0 = 0.0 if k == 0 else 0.15  # la ronda 1 suena desde el fotograma 0
        sig, d = vsay(voice, r["voz"])
        ev.append(("voice", sig, st + v0))
        ev += [("fx", "impact" if k == 0 or final else "whoosh", st), ("fx", "pop", st + 0.25)]
        if k == 0:
            ev.append(("fx", "airhorn", st + 0.05))
        T = {"cd": float(r["cd_inicio"]) if r.get("cd_inicio") else v0 + d + 0.15, "cdn": cd}
        ev += [("fx", "riser", st + T["cd"]), ("music_boost", st + T["cd"], st + T["cd"] + cd)]
        for s in range(cd):
            ts = st + T["cd"] + s
            ev += [("fx", "heart", ts), ("fx", "tick_high" if s >= cd - 1 else "tick", ts), ("fx", "tock", ts + 0.5)]
        T["rv"] = max(T["cd"] + cd, v0 + d + 0.1)
        ev += [("fx", "impact", st + T["rv"]), ("fx", "boing", st + T["rv"] + 0.05)]
        sig, d2 = vsay(voice, r["revela_voz"])
        ev.append(("voice", sig, st + T["rv"] + 0.15))
        T["stamp"] = T["rv"] + 0.15 + d2 * float(r.get("sello_en", 0.55))
        ev += [("fx", "buzz", st + T["stamp"]), ("fx", "impact", st + T["stamp"])]
        if final:
            ev += [("fx", "applause", st + T["stamp"] + 0.2), ("fx", "airhorn", st + T["stamp"])]
        dur = T["rv"] + 0.15 + d2 + 0.55
        scenes.append({"kind": "ronda", "start": st, "dur": dur, "k": k, "n": n, "r": r, "T": T, "final": final})
        t += dur
    sig, d = vsay(voice, c["cierre_voz"])
    shout_at = 0.3 + d + 0.1
    sig2, d2 = voice.say("¡Sígueme para más!", shout=True)
    dur = max(4.0, shout_at + d2 + 1.0)
    ev += [("fx", "whoosh", t), ("voice", sig, t + 0.3), ("voice", sig2, t + shout_at), ("fx", "applause", t + shout_at)]
    scenes.append({"kind": "outro", "start": t, "dur": dur, "shout_at": shout_at})
    return scenes, ev, t + dur


# ------------------------------------------------------------------ recursos

_S = {}


def spr(name, size):
    key = (name, size)
    if key not in _S["spr"]:
        im = Image.open(os.path.join(DECOR, name + ".png")).convert("RGBA")
        k = size / max(im.size)
        _S["spr"][key] = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    return _S["spr"][key]


def _gradient(top, bot, glow):
    yy = np.linspace(0, 1, H)[:, None, None]
    xx = np.linspace(-1, 1, W)[None, :, None]
    g = np.array(top, float) * (1 - yy) + np.array(bot, float) * yy
    r = np.sqrt(xx ** 2 + ((yy - 0.48) * 1.6) ** 2)
    g = g + np.array(glow, float) * np.clip(1 - r, 0, 1)[..., :] ** 2 * 0.5
    g = np.broadcast_to(g, (H, W, 3))
    return Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def _init(state):
    _S.clear()
    _S.update(state)
    _S["spr"] = {}
    c = state["c"]
    _S["bg"] = {}
    n = len(c["rondas"])
    for k in range(n):
        if k == n - 1:
            _S["bg"][k] = _gradient((60, 0, 30), (8, 0, 14), (220, 20, 60))
        else:
            col = COLS[k % len(COLS)]
            _S["bg"][k] = _gradient(mix(col, WHITE, 0.15), mix(col, (10, 0, 30), 0.65), mix(col, WHITE, 0.5))
    _S["bg"]["outro"] = _gradient((255, 90, 170), (120, 30, 200), (255, 220, 80))
    rnd = random.Random(4)
    _S["conf"] = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.choice(CONF), rnd.uniform(7, 14), rnd.uniform(60, 150),
                   rnd.uniform(0, 6.28)) for _ in range(46)]
    _S["flo"] = [(rnd.uniform(60, W - 60), rnd.uniform(0, H), rnd.choice((70, 90, 110)), rnd.uniform(35, 80),
                  rnd.uniform(0, 6.28)) for _ in range(9)]
    _S["burst"] = [(rnd.uniform(-1, 1), rnd.uniform(-1.5, -0.4), rnd.choice(CONF), rnd.uniform(10, 22),
                    rnd.uniform(0, 6.28)) for _ in range(60)]
    _S["logo"] = Image.open(os.path.join(ASSETS, "logo.png")).convert("RGBA")


# ------------------------------------------------------------------ fondo

def background(sc, lt, t):
    key = sc["k"] if sc["kind"] in ("ronda", "cta") else "outro"
    img = _S["bg"][key].copy()
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    final = sc.get("final")
    # rayos que giran
    cx, cy, R = 540, 960, 2300
    base = math.radians(t * 16)
    for j in range(16):
        a0 = base + j * 2 * math.pi / 16
        a1 = a0 + math.pi / 16
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                   (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=(255, 255, 255, 22 if not final else 14))
    # confeti cayendo
    for x0, y0, col, s, sp, ph in _S["conf"]:
        y = (y0 + sp * t) % (H + 40) - 20
        x = x0 + 30 * math.sin(t * 1.3 + ph)
        if final:
            col = (255, 80, 80) if col != YEL else YEL
        d.rectangle((x - s, y - s * 0.45, x + s, y + s * 0.45), fill=col + (150,))
    img.alpha_composite(lay)
    # dibujos de la categoría flotando (en la final: calaveras y rayos)
    if sc["kind"] in ("ronda", "cta"):
        r_ = sc.get("r") or _S["c"]["rondas"][sc["k"]]
        names = ["calavera", "rayo", "fuego"] if final else r_.get("flotan", [r_["icono"]])
        for j, (x0, y0, sz, sp, ph) in enumerate(_S["flo"]):
            im = spr(names[j % len(names)], sz)
            y = (y0 - sp * t) % (H + 200) - 100
            x = x0 + 40 * math.sin(t * 0.7 + ph)
            a = 0.55
            im2 = im.rotate(18 * math.sin(t * 1.4 + ph), resample=Image.BICUBIC, expand=True)
            im2.putalpha(im2.getchannel("A").point(lambda v, a_=a: int(v * a_)))
            img.alpha_composite(im2, (int(x - im2.width / 2), int(y - im2.height / 2)))
    if final and sc["kind"] == "ronda":
        # relámpagos de vez en cuando
        ph = (t * 0.7) % 1
        if ph < 0.06:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(70 * (1 - ph / 0.06)))))
    return img


# ------------------------------------------------------------------ piezas

def title(img, d, sc, lt):
    """«¡NO DIGAS LO MISMO QUE YO!» fijo arriba; en la ronda 1 entra de golpe desde el fotograma 0."""
    k = sc["k"]
    s = 1.0
    if k == 0:
        s = 1.07 - 0.07 * ease_out_back(min(1, lt / 0.3))
    sh = math.sin(lt * 55) * 12 * max(0, 1 - lt / 0.35) if k == 0 else 0
    text(d, (540 + sh, 215), "¡NO DIGAS LO MISMO", tfont(int(76 * s)), WHITE, 11, DARK, sh=8)
    text(d, (540 - sh, 300), "QUE YO!", tfont(int(96 * s)), YEL, 12, DARK, sh=9)


def progress(img, d, sc, lt):
    n, k = sc["n"], sc["k"]
    sp = min(96, 900 / max(1, n - 1))
    xs = [540 + (i - (n - 1) / 2) * sp for i in range(n)]
    y = 112
    d.line([(xs[0], y), (xs[-1], y)], fill=(255, 255, 255, 80), width=6)
    for i, x in enumerate(xs):
        last = i == n - 1
        if i < k:
            d.ellipse((x - 20, y - 20, x + 20, y + 20), fill=WHITE)
            d.line([(x - 9, y), (x - 2, y + 8), (x + 10, y - 8)], fill=GREEN, width=6)
        elif i == k:
            r_ = 28 + 3 * math.sin(lt * 8)
            d.ellipse((x - r_, y - r_, x + r_, y + r_), fill=RED if last else YEL, outline=WHITE, width=5)
            d.text((x, y + 2), "☠" if False else ("!" if last else str(i + 1)), font=tfont(32),
                   fill=WHITE if last else DARK, anchor="mm")
        else:
            d.ellipse((x - 20, y - 20, x + 20, y + 20), fill=(0, 0, 0, 90), outline=(255, 255, 255, 120), width=3)
            if last:
                paste_c(img, spr("calavera", 30), x, y, 1.0)


def category(img, d, sc, lt):
    r, k = sc["r"], sc["k"]
    a = pop(lt, 0.0 if k == 0 else 0.1, 0.35)
    if k == 0:
        a = max(a, 0.85 + 0.15 * a)
    if a <= 0:
        return
    final = sc["final"]
    lab = "RONDA FINAL · IMPOSIBLE" if final else f"RONDA {k + 1} DE {sc['n']}"
    pill(d, 540, 395 - (1 - a) * 60, lab, 44, RED if final else WHITE, WHITE if final else DARK, pad=(30, 12))
    y0 = 455 + (1 - a) * 200
    box = (80, y0, 1000, y0 + 230)
    rr(d, (box[0] + 8, box[1] + 14, box[2] + 8, box[3] + 14), 44, (0, 0, 0, 70))
    rr(d, box, 44, WHITE, outline=RED if final else YEL, width=10)
    d.text((540, y0 + 52), r.get("pre", "DI UN…"), font=tfont(46), fill=(120, 110, 140), anchor="mm")
    f = tfont(110)
    cat = r["categoria"]
    while d.textlength(cat, font=f) > 840 and f.size > 50:
        f = tfont(f.size - 4)
    d.text((540, y0 + 145), cat, font=f, fill=DARK, anchor="mm")


def think(img, d, sc, lt):
    """Antes de revelar: dibujo grande de la categoría; durante la cuenta atrás, anillo + número + «¡PIENSA UNA!»."""
    r, T = sc["r"], sc["T"]
    cx, cy = 540, 990
    if lt >= T["rv"]:
        return
    a = pop(lt, 0.0 if sc["k"] == 0 else 0.15, 0.4)
    if sc["k"] == 0:
        a = max(a, 0.75 + 0.25 * a)
    if a <= 0:
        return
    col = COLS[sc["k"] % len(COLS)] if not sc["final"] else RED
    g = 0.5 + 0.5 * math.sin(lt * 6)
    R = 250 * a
    d.ellipse((cx - R - 26, cy - R - 26, cx + R + 26, cy + R + 26), fill=WHITE + (int(50 + 50 * g),))
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=mix(col, WHITE, 0.75))
    bob = 12 * math.sin(lt * 3)
    paste_c(img, spr(r["icono"], 330), cx, cy + bob, a, angle=6 * math.sin(lt * 2))
    if sc["k"] == 0 and lt < T["cd"] - 0.2:
        # GANCHO: pegatina de la regla mientras habla la voz
        pz = 1 + 0.05 * math.sin(lt * 9)
        f = tfont(int(56 * pz))
        txt = "SI COINCIDES CONMIGO… ¡FUERA!"
        tw = d.textlength(txt, font=f)
        lay = Image.new("RGBA", (int(tw + 100), int(f.size + 70)), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((6, 6, lay.width - 6, lay.height - 6), 24, fill=RED, outline=WHITE, width=8)
        ld.text((lay.width / 2, lay.height / 2 + 3), txt, font=f, fill=WHITE, anchor="mm")
        lay = lay.rotate(-4, resample=Image.BICUBIC, expand=True)
        img.alpha_composite(lay, (int(540 - lay.width / 2), int(1345 - lay.height / 2)))
        for j, xx in enumerate((170, 910)):
            paste_c(img, spr("cruz", 120), xx, 1470 + 10 * math.sin(lt * 6 + j), 1.0, angle=15 * math.sin(lt * 4 + j))
    if lt >= T["cd"] - 0.2:
        frac = min(1.0, max(0.0, (lt - T["cd"]) / T["cdn"]))
        d.arc((cx - R - 16, cy - R - 16, cx + R + 16, cy + R + 16), -90, -90 + 360 * (1 - frac),
              fill=YEL if frac < 0.66 else RED, width=22)
        n = max(1, T["cdn"] - int(lt - T["cd"])) if lt >= T["cd"] else T["cdn"]
        pz = 1 + 0.25 * math.exp(-((lt - T["cd"]) % 1) * 6) if lt >= T["cd"] else 1
        bx, by = cx + 220, cy + 210
        d.ellipse((bx - 80 * pz, by - 80 * pz, bx + 80 * pz, by + 80 * pz), fill=RED, outline=WHITE, width=8)
        d.text((bx, by + 6), str(n), font=tfont(int(110 * pz)), fill=WHITE, anchor="mm")
        # pensativo que se asoma
        paste_c(img, spr("pensativo", 190), cx - 250, cy + 220 + 8 * math.sin(lt * 5), 1.0, angle=-8)
        e = pop(lt, T["cd"] - 0.2, 0.3)
        pulse = 1 + 0.06 * math.sin(lt * 10)
        text(d, (540, 1345), "¡PIENSA UNA!", tfont(int(100 * e * pulse)), YEL, 12, DARK, sh=9)


def reveal(img, d, sc, lt):
    r, T = sc["r"], sc["T"]
    if lt < T["rv"]:
        return
    rl = lt - T["rv"]
    a = ease_out_back(min(1, rl / 0.35))
    cx, cy = 540, 990
    flip = min(1, rl / 0.25)
    w = 900 * max(0.05, abs(math.cos((1 - flip) * math.pi / 2)))
    hgt = 470
    box = (cx - w / 2, cy - hgt / 2, cx + w / 2, cy + hgt / 2)
    rr(d, (box[0] + 10, box[1] + 16, box[2] + 10, box[3] + 16), 50, (0, 0, 0, 90))
    rr(d, box, 50, YEL if not sc["final"] else (255, 230, 120), outline=WHITE, width=12)
    if flip >= 0.9:
        d.text((cx, cy - 165), "YO HE DICHO:", font=tfont(52), fill=DARK, anchor="mm")
        words = r["respuesta"]
        f = tfont(130 if len(words) <= 9 else 104)
        while d.textlength(words, font=f) > 820 and f.size > 50:
            f = tfont(f.size - 4)
        sz = 1 + 0.06 * math.sin(rl * 7)
        f2 = tfont(int(f.size * sz * a))
        text(d, (cx, cy - 40), words, f2, WHITE, 14, DARK, sh=10)
        icons = r.get("iconos_resp", [])
        for j, ic in enumerate(icons):
            xx = cx + (j - (len(icons) - 1) / 2) * 230
            paste_c(img, spr(ic, 170), xx, cy + 120 + 8 * math.sin(rl * 5 + j), a, angle=8 * math.sin(rl * 3 + j))
    # sello «¿TAMBIÉN? ¡FUERA!»
    if lt >= T["stamp"]:
        sl = lt - T["stamp"]
        k = ease_out(min(1, sl / 0.15))
        s = 1.8 - 0.8 * k
        st_txt = r.get("sello", "¿TAMBIÉN? ¡FUERA!")
        f = tfont(int(88 * s))
        tw = d.textlength(st_txt, font=f)
        lay = Image.new("RGBA", (int(tw + 120), int(f.size + 90)), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((6, 6, lay.width - 6, lay.height - 6), 26, fill=RED + (235,), outline=WHITE, width=10)
        ld.text((lay.width / 2, lay.height / 2 + 4), st_txt, font=f, fill=WHITE, anchor="mm")
        lay = lay.rotate(-6, resample=Image.BICUBIC, expand=True)
        img.alpha_composite(lay, (int(540 - lay.width / 2), int(1345 - lay.height / 2)))
        # cruces que salen
        for j, (vx, vy, col, sz_, ph) in enumerate(_S["burst"][:10]):
            x = 540 + vx * 700 * min(sl, 1.2)
            y = 1345 + vy * 500 * min(sl, 1.2) + 600 * min(sl, 1.2) ** 2
            if sl < 1.2:
                paste_c(img, spr("cruz", 70), x, y, 1.0, max(0, 1 - sl / 1.2), angle=ph * 50)
        if sl < 0.12:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 30, 50, int(110 * (1 - sl / 0.12)))))
        if sc["final"]:
            for j, (vx, vy, col, sz_, ph) in enumerate(_S["burst"]):
                x = 540 + vx * 900 * sl
                y = 990 + vy * 1000 * sl + 1200 * sl * sl
                d.rectangle((x - sz_, y - sz_ * 0.5, x + sz_, y + sz_ * 0.5), fill=col + (230,))


def draw_ronda(img, d, sc, lt):
    progress(img, d, sc, lt)
    title(img, d, sc, lt)
    category(img, d, sc, lt)
    think(img, d, sc, lt)
    reveal(img, d, sc, lt)


def draw_outro(img, d, sc, lt):
    # FIESTA: lluvia de confeti, globos que suben, estrellas y trofeo
    for j, (vx, vy, col, sz_, ph) in enumerate(_S["burst"]):
        x = (vx + 1) / 2 * W + 40 * math.sin(lt * 2 + ph)
        y = ((lt * (200 + sz_ * 12) + j * 97) % (H + 100)) - 50
        ang = lt * 4 + ph
        w_ = sz_ * abs(math.cos(ang))
        d.rectangle((x - w_, y - sz_ * 0.45, x + w_, y + sz_ * 0.45), fill=col + (235,))
    for j in range(6):
        x = 120 + j * 170 + 20 * math.sin(lt * 2 + j)
        y = H + 120 - ((lt * 230 + j * 260) % (H + 300))
        paste_c(img, spr("globo", 130), x, y, 1.0, 0.95, angle=8 * math.sin(lt * 2 + j))
    a = pop(lt, 0.0, 0.4)
    y = 230 + (1 - a) * -500
    box = (70, y, 1010, y + 420)
    rr(d, (box[0] + 8, box[1] + 14, box[2] + 8, box[3] + 14), 50, (0, 0, 0, 80))
    rr(d, box, 50, WHITE, outline=YEL, width=10)
    paste_c(img, spr("fiesta", 170), 140, y - 10 + 10 * math.sin(lt * 5), a, angle=-12)
    paste_c(img, spr("trofeo", 160), 945, y - 10 + 10 * math.sin(lt * 5 + 1), a, angle=10)
    d.text((540, y + 120), "¿EN QUÉ RONDA", font=tfont(96), fill=DARK, anchor="mm")
    d.text((540, y + 235), "TE HAN ELIMINADO?", font=tfont(84), fill=RED, anchor="mm")
    # chips de las rondas botando
    n = len(_S["c"]["rondas"])
    sp = min(110, 900 / max(1, n - 1))
    for i in range(n):
        x = 540 + (i - (n - 1) / 2) * sp
        b = pop(lt, 0.3 + 0.07 * i, 0.3)
        yy = y + 340 - 14 * abs(math.sin(lt * 5 + i))
        if b > 0:
            col = COLS[i % len(COLS)] if i < n - 1 else RED
            d.ellipse((x - 40 * b, yy - 40 * b, x + 40 * b, yy + 40 * b), fill=col, outline=WHITE, width=5)
            d.text((x, yy + 3), str(i + 1) if i < n - 1 else "!", font=tfont(int(44 * b)), fill=WHITE, anchor="mm")
    e = pop(lt, 0.8, 0.4)
    if e > 0:
        pulse = 1 + 0.05 * math.sin(lt * 8)
        pill(d, 540, 790 + (1 - e) * 200, "¿QUÉ CATEGORÍA QUIERES AHORA?", int(50 * pulse * e), YEL, DARK, pad=(34, 16))
        pill(d, 540, 905 + (1 - e) * 200, "¡COMÉNTALO Y APOYA EL VÍDEO!", int(48 * e), RED, WHITE, pad=(34, 16))
        paste_c(img, spr("bocadillo", 150), 150, 980 + 10 * math.sin(lt * 4), e, angle=-10)
        paste_c(img, spr("corazon", 120), 935, 985 + 10 * math.sin(lt * 4 + 1), e * (1 + 0.15 * abs(math.sin(lt * 6))))
    b = pop(lt, sc["shout_at"] - 0.1, 0.4)
    if b > 0:
        pulse = 1 + 0.07 * math.sin(lt * 9)
        pill(d, 540, 1070 + (1 - b) * 300, "¡SÍGUEME PARA MÁS!", int(62 * pulse * b), WHITE, DARK, pad=(40, 18))
        lg = _S["logo"].resize((int(330 * b), int(330 * b)), Image.LANCZOS)
        img.alpha_composite(lg, (540 - lg.width // 2, 1340 - lg.height // 2))
    for j, (vx, vy, col, sz_, ph) in enumerate(_S["burst"]):
        sl = lt - sc["shout_at"]
        if 0 < sl < 2:
            x = 540 + vx * 800 * sl
            y = 1100 + vy * 900 * sl + 1100 * sl * sl
            d.rectangle((x - sz_, y - sz_ * 0.5, x + sz_, y + sz_ * 0.5), fill=col + (230,))


def draw_cta(img, d, sc, lt):
    """Pausa DENTRO del juego, limpia y bonita: sello «✓ RONDA N SUPERADA», logo gigante que late con botón «+»,
    corazones que suben, «¡SÍGUEME!» y las 2 rondas que quedan bloqueadas (sin más texto)."""
    progress(img, d, sc, lt)
    title(img, d, sc, lt)
    k, n = sc["k"], sc["n"]
    # corazones subiendo detrás
    for j, (vx, vy, col, sz_, ph) in enumerate(_S["burst"][:18]):
        x = 540 + vx * 470 + 30 * math.sin(lt * 3 + ph)
        y = 1350 - ((lt * 300 + j * 75) % 1000)
        paste_c(img, spr("corazon", max(4, int(40 + sz_ * 2))), x, y, 1.0, 0.75)
    # sello verde
    a = ease_out(min(1, lt / 0.18))
    s_ = 1.6 - 0.6 * a
    lay = Image.new("RGBA", (700, 120), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle((6, 6, 694, 114), 30, fill=GREEN, outline=WHITE, width=8)
    ld.line([(70, 60), (95, 85), (135, 38)], fill=WHITE, width=12)
    ld.text((395, 62), f"RONDA {k} SUPERADA", font=tfont(56), fill=WHITE, anchor="mm")
    lay = lay.resize((int(700 * s_), int(120 * s_)), Image.BILINEAR).rotate(-4, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(lay, (540 - lay.width // 2, 440 - lay.height // 2))
    # logo gigante con halo y botón +
    c = ease_out_back(min(1, max(0, (lt - 0.15) / 0.4)))
    if c > 0.03:
        pulse = 1 + 0.04 * math.sin(lt * 6)
        R = 230 * c * pulse
        g = 0.5 + 0.5 * math.sin(lt * 5)
        d.ellipse((540 - R - 30, 840 - R - 30, 540 + R + 30, 840 + R + 30), fill=(255, 255, 255, int(60 + 50 * g)))
        d.ellipse((540 - R - 12, 840 - R - 12, 540 + R + 12, 840 + R + 12), fill=YEL)
        lg = _S["logo"].resize((max(2, int(2 * R)), max(2, int(2 * R))), Image.LANCZOS)
        img.alpha_composite(lg, (int(540 - R), int(840 - R)))
        pz = 1 + 0.15 * abs(math.sin(lt * 5))
        bx, by = 540 + R * 0.72, 840 + R * 0.72
        d.ellipse((bx - 55 * pz, by - 55 * pz, bx + 55 * pz, by + 55 * pz), fill=RED, outline=WHITE, width=8)
        d.line([(bx - 26 * pz, by), (bx + 26 * pz, by)], fill=WHITE, width=11)
        d.line([(bx, by - 26 * pz), (bx, by + 26 * pz)], fill=WHITE, width=11)
        paste_c(img, spr("dedo", 180), 540 - R - 70 + 16 * math.sin(lt * 7), 860, c)
    e = ease_out_back(min(1, max(0, (lt - 0.45) / 0.35)))
    if e > 0:
        pulse = 1 + 0.06 * math.sin(lt * 9)
        pill(d, 540, 1170, "¡SÍGUEME!", int(84 * pulse * e), WHITE, RED, pad=(54, 22))
    # las 2 rondas que quedan, bloqueadas (sin texto)
    f_ = pop(lt, 0.7, 0.35)
    if f_ > 0:
        for q in range(n - k):
            x = 540 + (q - (n - k - 1) / 2) * 190
            y = 1360 + 10 * math.sin(lt * 4 + q)
            last = q == n - k - 1
            col = (150, 20, 40) if last else (60, 110, 255)
            r_ = 70 * f_
            d.ellipse((x - r_, y - r_, x + r_, y + r_), fill=col, outline=WHITE, width=6)
            if last:
                paste_c(img, spr("calavera", max(4, int(80 * f_))), x, y - 6, 1.0)
            else:
                d.text((x, y), str(k + 1 + q), font=tfont(int(70 * f_)), fill=WHITE, anchor="mm")
            cx_, cy_ = x + 45 * f_, y + 45 * f_
            d.arc((cx_ - 14, cy_ - 32, cx_ + 14, cy_ - 4), 180, 360, fill=YEL, width=7)
            d.rounded_rectangle((cx_ - 20, cy_ - 16, cx_ + 20, cy_ + 18), 6, fill=YEL)


DRAW = {"ronda": draw_ronda, "outro": draw_outro, "cta": draw_cta}


def shake(sc, lt):
    if sc["kind"] != "ronda":
        return 0, 0
    T = sc["T"]
    amp = 0.0
    for t0, a in ((0.0, 1.0 if sc["k"] == 0 else 0.4), (T["rv"], 0.5), (T["stamp"], 1.0 if sc["final"] else 0.8)):
        if 0 <= lt - t0 < 0.35:
            amp = max(amp, a * (1 - (lt - t0) / 0.35))
    if amp <= 0:
        return 0, 0
    return int(math.sin(lt * 80) * 16 * amp), int(math.cos(lt * 67) * 12 * amp)


def render_frame(i):
    t = i / FPS
    scenes = _S["scenes"]
    sc = scenes[-1]
    for s in scenes:
        if s["start"] <= t < s["start"] + s["dur"]:
            sc = s
            break
    lt = t - sc["start"]
    bg = background(sc, lt, t)
    img = bg.copy()
    d = ImageDraw.Draw(img, "RGBA")
    DRAW[sc["kind"]](img, d, sc, lt)
    dx, dy = shake(sc, lt)
    if dx or dy:
        img = ImageChops.offset(img, dx, dy)
    out_t = sc["dur"] - lt
    if out_t < 0.15 and sc is not scenes[-1]:
        img = Image.blend(bg, img, max(0.0, out_t / 0.15))
    username(img)
    return img.convert("RGB").tobytes()


# ------------------------------------------------------------------ portada

def portada(c, state, out_dir):
    _init(state)
    r = c["rondas"][0]
    sc = {"kind": "ronda", "k": 0, "n": len(c["rondas"]), "r": r, "final": False,
          "T": {"cd": 0.0, "cdn": 3, "rv": 99, "stamp": 99}}
    img = background(sc, 0, 1.3)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (540, 330), "¡NO DIGAS LO MISMO", tfont(92), WHITE, 13, DARK, sh=10)
    text(d, (540, 440), "QUE YO!", tfont(140), YEL, 15, DARK, sh=12)
    box = (90, 560, 990, 790)
    rr(d, (box[0] + 8, box[1] + 14, box[2] + 8, box[3] + 14), 44, (0, 0, 0, 70))
    rr(d, box, 44, WHITE, outline=YEL, width=10)
    d.text((540, 612), r.get("pre", "DI UN…"), font=tfont(46), fill=(120, 110, 140), anchor="mm")
    d.text((540, 710), r["categoria"], font=tfont(110), fill=DARK, anchor="mm")
    d.ellipse((540 - 230, 1060 - 230, 540 + 230, 1060 + 230), fill=WHITE + (90,))
    paste_c(img, spr(r["icono"], 300), 540, 1050, 1.0, angle=-6)
    paste_c(img, spr("pensativo", 200), 260, 1240, 1.0, angle=-10)
    paste_c(img, spr("sorpresa", 190), 830, 900, 1.0, angle=10)
    lay = Image.new("RGBA", (900, 200), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle((6, 6, 894, 194), 30, fill=RED, outline=WHITE, width=10)
    ld.text((450, 104), c.get("portada", {}).get("pegatina", "SI COINCIDES… ¡FUERA!"), font=tfont(80), fill=WHITE, anchor="mm")
    lay = lay.rotate(-5, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(lay, (540 - lay.width // 2, 1420 - lay.height // 2))
    d.text((540, 1580), c.get("portada", {}).get("sub", "¿Aguantas hasta la ronda final?"), font=font(50), fill=WHITE,
           anchor="mm", stroke_width=7, stroke_fill=DARK)
    username(img)
    os.makedirs(out_dir, exist_ok=True)
    rgb = img.convert("RGB")
    p916 = os.path.join(out_dir, f"{c['video']}_9x16.png")
    p34 = os.path.join(out_dir, f"{c['video']}_3x4.png")
    rgb.save(p916, optimize=True)
    rgb.crop((0, 240, W, 1680)).save(p34, optimize=True)
    return p916, p34


# ------------------------------------------------------------------ exportación

def render_video(c, voice, out_path, preview=None, workers=None):
    scenes, events, total = build_timeline(c, voice)
    state = {"scenes": scenes, "c": c}
    if preview is not None:
        _init(state)
        outs = []
        for s in preview:
            p = f"{out_path}_{s:05.1f}.png"
            Image.frombytes("RGB", (W, H), render_frame(int(s * FPS))).save(p)
            outs.append(p)
        return total, outs
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    wav = out_path + ".audio.wav"
    build_audio(events, total, wav)
    frames = int(total * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "23",
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1", "-c:a", "aac", "-b:a", "192k",
           "-ar", "44100", "-shortest", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers or os.cpu_count(), initializer=_init, initargs=(state,)) as pool:
        for k, fr in enumerate(pool.imap(render_frame, range(frames), chunksize=6)):
            proc.stdin.write(fr)
            if k % (FPS * 10) == 0:
                print(f"  fotograma {k}/{frames}", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg falló al exportar el vídeo.")
    os.remove(wav)
    return total, [out_path]

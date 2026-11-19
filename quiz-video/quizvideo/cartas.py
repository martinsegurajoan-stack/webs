"""Formato "ELIGE UNA CARTA" (juego para beber con amigos).

Gancho → instrucciones → rondas (3 cartas boca abajo, cuenta atrás para elegir/pausar, se giran
una a una con su prueba) → cierre. Reutiliza voz, efectos y exportación del proyecto.
"""

import math
import os
import random
import subprocess
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import audio, themes
from .niveles import check, paste_c, pill, pop, rr, text, username
from .personalidad import sfx_boing, sfx_impact
from .render import FPS, W, H, ease_in, ease_out, font, tfont

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
COUNTDOWN = 5
WHITE = (255, 255, 255)
YEL = (255, 212, 0)
DARK = (34, 18, 56)
CW, CH = 270, 410
CARD_X = [225, 525, 825]
CARD_Y = 960

# color de cada ronda: arriba, abajo (fondo) y dorso de la carta
ROUND_COLORS = [
    ((46, 214, 196), (8, 104, 136)),     # turquesa
    ((255, 156, 64), (214, 60, 34)),     # naranja
    ((255, 96, 176), (166, 20, 112)),    # rosa
    ((88, 156, 255), (42, 40, 184)),     # azul
    ((176, 104, 255), (78, 20, 168)),    # morado
    ((255, 206, 72), (196, 104, 8)),     # dorado
]
TAGS = {
    "BEBE": (239, 55, 70), "SALVADO": (22, 186, 96), "SALVADO?": (22, 186, 96), "REPARTE": (36, 118, 255),
    "MANDAS TÚ": (36, 118, 255), "BRINDIS": (138, 58, 255), "TODOS": (138, 58, 255),
    "FIESTA": (255, 64, 160), "TRAMPA": (40, 24, 56), "MALDICIÓN": (40, 24, 56), "CAOS": (255, 120, 20),
    "VECINO": (0, 170, 190), "DORADA": (224, 150, 0),
}


# ------------------------------------------------------------------ audio

def sfx_clink():
    t = np.arange(int(0.9 * audio.SR)) / audio.SR
    s = (np.sin(2 * np.pi * 2637 * t) + 0.6 * np.sin(2 * np.pi * 3951 * t) + 0.3 * np.sin(2 * np.pi * 5274 * t))
    s2 = np.zeros_like(s)
    d = int(0.07 * audio.SR)
    s2[d:] = s[:-d] * 0.7
    return 0.32 * (s + s2) * np.exp(-t * 7)


def sfx_flip():
    n = int(0.18 * audio.SR)
    t = np.arange(n) / audio.SR
    noise = np.random.default_rng(4).standard_normal(n)
    return 0.5 * noise * np.exp(-t * 28) * np.sin(np.pi * t / 0.18)


def build_audio(events, total, path):
    mix = audio.Mixer(total)
    fx = {"whoosh": audio.sfx_whoosh(), "pop": audio.sfx_pop(), "tick": audio.sfx_tick(),
          "tick_high": audio.sfx_tick(True), "tock": audio.sfx_tock(), "heart": audio.sfx_heartbeat(),
          "riser": audio.sfx_riser(COUNTDOWN), "flip": sfx_flip(), "impact": sfx_impact(),
          "boing": sfx_boing(), "clink": sfx_clink(), "applause": audio.sfx_applause(),
          "correct": audio.sfx_correct()}
    gains = {"whoosh": 0.5, "pop": 0.6, "tick": 1.3, "tick_high": 1.45, "tock": 0.95, "heart": 0.8,
             "riser": 0.5, "flip": 0.9, "impact": 0.7, "boing": 0.8, "clink": 1.0, "applause": 0.8,
             "correct": 0.6}
    boosts = [(a, b) for kind, a, b in events if kind == "music_boost"]
    for kind, what, at in events:
        if kind == "music_boost":
            continue
        if kind == "fx":
            mix.add_fx(fx[what], at, gains[what])
        elif what is not None:
            mix.add_voice(what, at, 1.0)
    audio.write_wav(path, mix.render(audio.music_pop(total, bpm=124, seed=3), music_gain=0.36, boosts=boosts))


# ------------------------------------------------------------------ línea de tiempo

def build_timeline(c, voice):
    scenes, ev = [], []
    sig, d = voice.say(c["gancho"]["voz"])
    ev += [("voice", sig, 0.05), ("fx", "impact", 0.0), ("fx", "whoosh", 0.05)]
    for i in range(3):
        ev.append(("fx", "flip", 0.25 + 0.12 * i))
    dur = max(3.2, d + 0.4)
    scenes.append({"kind": "hook", "start": 0.0, "dur": dur, "lv": -1})
    t = dur

    sig, d = voice.say(c["instrucciones"]["voz"])
    ev += [("fx", "whoosh", t), ("voice", sig, t + 0.2)]
    for i in range(3):
        ev.append(("fx", "pop", t + 0.5 + 0.35 * i))
    dur = max(3.5, 0.2 + d + 0.15)
    scenes.append({"kind": "instr", "start": t, "dur": dur, "lv": -1})
    t += dur

    reac = c.get("reacciones", ["¡Salud!"])
    n = len(c["rondas"])
    for k, r in enumerate(c["rondas"]):
        st, loc = t, 0.0
        ev.append(("fx", "whoosh", st))
        for i in range(3):
            ev.append(("fx", "flip", st + 0.25 + 0.1 * i))
        sig, d = voice.say(r["anuncio"])
        ev.append(("voice", sig, st + 0.15))
        loc = 0.15 + d
        cd = loc
        ev += [("fx", "riser", st + cd), ("music_boost", st + cd, st + cd + COUNTDOWN)]
        for s in range(COUNTDOWN):
            ts = st + cd + s
            ev += [("fx", "heart", ts), ("fx", "tick_high" if s >= COUNTDOWN - 2 else "tick", ts),
                   ("fx", "tock", ts + 0.5)]
            if s >= COUNTDOWN - 2:
                ev += [("fx", "tick_high", ts + 0.25), ("fx", "tick_high", ts + 0.75)]
        loc = cd + COUNTDOWN + 0.05
        order = r.get("orden", [0, 1, 2])
        flips = {}
        for j, i in enumerate(order):
            card = r["cartas"][i]
            flips[i] = loc
            ev += [("fx", "flip", st + loc), ("fx", "impact" if j == 0 else "pop", st + loc + 0.05)]
            if card["tag"] in ("SALVADO", "DORADA"):
                ev.append(("fx", "correct", st + loc + 0.2))
            if card["tag"] in ("TRAMPA", "SALVADO?", "MALDICIÓN"):
                ev.append(("fx", "boing", st + loc + 0.25))
            sig, d = voice.say(card["voz"])
            ev.append(("voice", sig, st + loc + 0.12))
            loc += 0.12 + d + 0.02
        last = k == n - 1
        cheer_t = None
        if not last:
            # brindis visual con choque de copas (sin voz, para mantener el ritmo)
            cheer_t = loc
            ev += [("fx", "clink", st + loc), ("fx", "pop", st + loc + 0.05)]
            loc += 1.0
        else:
            cheer_t = loc - 0.2
            ev += [("fx", "clink", st + cheer_t), ("fx", "applause", st + cheer_t)]
            loc += 0.9
        scenes.append({"kind": "round", "start": st, "dur": loc, "k": k, "r": r, "lv": k, "cd": cd,
                       "flips": flips, "cheer": cheer_t, "cheer_txt": reac[k % len(reac)] if not last else None,
                       "n": n})
        t += loc

    sig, d = voice.say(c["cierre_voz"])
    shout_at = 0.3 + d + 0.1
    sig2, d2 = voice.say("¡Sígueme para más!", shout=True)
    dur = max(3.6, shout_at + d2 + 1.0)
    ev += [("fx", "whoosh", t), ("voice", sig, t + 0.3), ("voice", sig2, t + shout_at),
           ("fx", "applause", t + shout_at)]
    scenes.append({"kind": "outro", "start": t, "dur": dur, "shout_at": shout_at, "lv": -1})
    return scenes, ev, t + dur


# ------------------------------------------------------------------ recursos

_S = {}


def _spr(name, size):
    key = (name, size)
    if key not in _S["spr"]:
        im = Image.open(os.path.join(ASSETS, name)).convert("RGBA")
        _S["spr"][key] = im.resize((size, size), Image.LANCZOS)
    return _S["spr"][key]


def _gradient(top, bot, w=W, h=H, glow=True):
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(-1, 1, w)[None, :]
    k = np.clip(y * 0.9 + x * 0.06 + 0.02, 0, 1)
    arr = np.zeros((h, w, 3))
    for ch in range(3):
        arr[..., ch] = top[ch] + (bot[ch] - top[ch]) * k
    if glow:
        arr += (np.exp(-((x * 0.9) ** 2 + ((y - 0.45) / 0.4) ** 2)) * 30)[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def _fit_t(d, s, maxw, maxh, start, minimum=24):
    size = start
    while size >= minimum:
        f = tfont(size)
        words, lines, cur = s.split(), [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if d.textlength(test, font=f) <= maxw or not cur:
                cur = test
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        lh = size * 1.05
        if len(lines) * lh <= maxh and all(d.textlength(l, font=f) <= maxw for l in lines):
            return f, lines, lh
        size -= 2
    return tfont(minimum), [s], minimum * 1.05


def _mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    return m


def card_back(k, num, gold=False):
    top, bot = ROUND_COLORS[k] if k >= 0 else ((150, 70, 255), (70, 20, 160))
    if gold:
        top, bot = (255, 222, 110), (210, 130, 10)
    g = _gradient(mix(top, WHITE, 0.1), mix(bot, (0, 0, 0), 0.15), CW, CH, glow=False).convert("RGBA")
    d = ImageDraw.Draw(g, "RGBA")
    for yy in range(-20, CH + 40, 34):
        for xx in range(-20, CW + 40, 34):
            off = 17 if (yy // 34) % 2 else 0
            cx, cy = xx + off, yy
            d.polygon([(cx, cy - 9), (cx + 9, cy), (cx, cy + 9), (cx - 9, cy)], fill=(255, 255, 255, 34))
    d.rounded_rectangle((12, 12, CW - 13, CH - 13), 22, outline=(255, 255, 255, 230), width=6)
    d.ellipse((CW / 2 - 78, CH / 2 - 78, CW / 2 + 78, CH / 2 + 78), fill=(0, 0, 0, 50))
    d.ellipse((CW / 2 - 72, CH / 2 - 76, CW / 2 + 72, CH / 2 + 68), fill=WHITE)
    d.text((CW / 2, CH / 2 - 2), str(num), font=tfont(108), fill=bot if not gold else (170, 100, 0), anchor="mm")
    if gold:
        for (sx, sy, ss) in [(52, 60, 16), (214, 92, 11), (60, 330, 12), (210, 345, 17), (135, 52, 9)]:
            d.polygon([(sx, sy - ss), (sx + ss * 0.3, sy - ss * 0.3), (sx + ss, sy), (sx + ss * 0.3, sy + ss * 0.3),
                       (sx, sy + ss), (sx - ss * 0.3, sy + ss * 0.3), (sx - ss, sy), (sx - ss * 0.3, sy - ss * 0.3)],
                      fill=WHITE)
    d.text((CW / 2, CH - 44), "HORA DEL QUIZ", font=tfont(24), fill=(255, 255, 255, 200), anchor="mm")
    g.putalpha(_mask(CW, CH, 28))
    return g


def card_face(item, num, k):
    col = TAGS.get(item["tag"], (138, 58, 255))
    gold = item["tag"] == "DORADA"
    base = (255, 248, 222) if gold else (255, 252, 246)
    g = Image.new("RGBA", (CW, CH), base + (255,))
    d = ImageDraw.Draw(g, "RGBA")
    d.rounded_rectangle((6, 6, CW - 7, CH - 7), 24, outline=col, width=9)
    d.text((32, 38), str(num), font=tfont(42), fill=col, anchor="mm")
    em = _spr(os.path.join("cartas", item["emoji"] + ".png"), 112)
    g.alpha_composite(em, (CW // 2 - 56, 40))
    f, lines, lh = _fit_t(d, item["texto"], CW - 40, 172, 52, 30)
    yy = 248 - lh * len(lines) / 2 + lh / 2
    for ln in lines:
        d.text((CW / 2, yy), ln, font=f, fill=DARK, anchor="mm")
        yy += lh
    d.rounded_rectangle((22, CH - 74, CW - 22, CH - 22), 26, fill=col)
    ft = tfont(34)
    while d.textlength(item["tag"], font=ft) > CW - 70:
        ft = tfont(ft.size - 2)
    d.text((CW / 2, CH - 47), item["tag"], font=ft, fill=WHITE, anchor="mm")
    g.putalpha(Image.fromarray(np.minimum(np.array(g.getchannel("A")), np.array(_mask(CW, CH, 28)))))
    return g


def mix(c1, c2, k):
    return tuple(int(a + (b - a) * k) for a, b in zip(c1, c2))


def _init(state):
    _S.clear()
    _S.update(state)
    _S["spr"] = {}
    h = state["tono"]
    _S["bg"] = {-1: _gradient(themes._hsv(h, 0.8, 0.62), themes._hsv(h + 20, 0.95, 0.16))}
    for k, (top, bot) in enumerate(ROUND_COLORS):
        _S["bg"][k] = _gradient(top, bot)
    blob = Image.new("L", (640, 640), 0)
    ImageDraw.Draw(blob).ellipse((120, 120, 520, 520), fill=255)
    blob = blob.filter(ImageFilter.GaussianBlur(70))
    spr = Image.new("RGBA", blob.size, (255, 255, 255, 0))
    spr.putalpha(blob.point(lambda v: int(v * 0.16)))
    _S["blob"] = spr
    rnd = random.Random(8)
    cols = [YEL, (0, 230, 210), (255, 70, 170), WHITE, (160, 90, 255), (60, 220, 120)]
    _S["confeti"] = [(rnd.random() * W, rnd.random() * H, rnd.choice(cols), rnd.uniform(8, 16),
                      rnd.uniform(0.4, 1.0), rnd.random() * 6.28) for _ in range(46)]
    rb = random.Random(3)
    _S["burst"] = [(rb.uniform(-1, 1), rb.uniform(-1.5, -0.4), rb.choice(cols), rb.uniform(10, 22),
                    rb.uniform(0, 6.28)) for _ in range(50)]
    _S["logo"] = Image.open(os.path.join(ASSETS, "logo.png")).convert("RGBA")
    _S["backs"], _S["faces"] = {}, {}
    c = state["c"]
    for k, r in enumerate(c["rondas"]):
        for i, it in enumerate(r["cartas"]):
            _S["backs"][(k, i)] = card_back(k, i + 1, bool(r.get("dorada")))
            _S["faces"][(k, i)] = card_face(it, i + 1, k)
    for i in range(3):
        _S["backs"][(-1, i)] = card_back(-1, i + 1)


# ------------------------------------------------------------------ fondo

def _bg_frame(lv, t):
    img = _S["bg"][lv].copy()
    for i, (bx, by, sp) in enumerate([(160, 380, 0.25), (930, 900, 0.2), (380, 1500, 0.16)]):
        x = bx + math.sin(t * sp + i) * 110
        y = by + math.cos(t * sp * 1.3 + i * 2) * 80
        img.paste(_S["blob"], (int(x - 320), int(y - 320)), _S["blob"])
    d = ImageDraw.Draw(img, "RGBA")
    # focos de fiesta que barren desde arriba
    for j, (x0, ph) in enumerate([(160, 0.0), (540, 2.1), (920, 4.2)]):
        ang = math.sin(t * 0.9 + ph) * 0.45 + math.pi / 2
        L = 2100
        a1, a2 = ang - 0.09, ang + 0.09
        d.polygon([(x0, -20), (x0 + L * math.cos(a1), -20 + L * math.sin(a1)),
                   (x0 + L * math.cos(a2), -20 + L * math.sin(a2))], fill=(255, 255, 255, 18))
    # confeti cayendo
    for (x0, y0, col, s, sp, ph) in _S["confeti"]:
        y = (y0 + t * 120 * sp) % (H + 60) - 30
        x = x0 + math.sin(t * 1.5 * sp + ph) * 30
        ang = ph + t * 3 * sp
        pts = [(x + s * math.cos(ang + q * math.pi / 2) * (1 if q % 2 else 0.45),
                y + s * math.sin(ang + q * math.pi / 2) * (1 if q % 2 else 0.45)) for q in range(4)]
        d.polygon(pts, fill=col + (150,))
    return img


def background(sc, lt, t):
    img = _bg_frame(sc["lv"], t)
    if sc["kind"] in ("round", "outro") and lt < 0.5:
        prev = -1 if sc["kind"] == "round" and sc["k"] == 0 else (sc["k"] - 1 if sc["kind"] == "round" else
                                                                  len(_S["c"]["rondas"]) - 1)
        old = _bg_frame(prev, t)
        r = ease_in(lt / 0.5) * 1400 + 10
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).ellipse((540 - r, CARD_Y - r, 540 + r, CARD_Y + r), fill=255)
        img = Image.composite(img, old, mask)
    return img


# ------------------------------------------------------------------ piezas

def draw_card(img, spr, cx, cy, scale=1.0, flipx=1.0, angle=0.0, shadow=True):
    if scale <= 0.02:
        return
    w = max(2, int(CW * scale * abs(flipx)))
    h = max(2, int(CH * scale))
    if shadow:
        sh = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((20, 26, w + 20, h + 26), 26, fill=(0, 0, 0, 80))
        sh = sh.filter(ImageFilter.GaussianBlur(8))
        if angle:
            sh = sh.rotate(angle, resample=Image.BICUBIC, expand=True)
        img.paste(sh, (int(cx - sh.width / 2 + 6), int(cy - sh.height / 2 + 10)), sh)
    s = spr.resize((w, h), Image.BILINEAR)
    if angle:
        s = s.rotate(angle, resample=Image.BICUBIC, expand=True)
    img.paste(s, (int(cx - s.width / 2), int(cy - s.height / 2)), s)


def pause_pill(d, cx, cy, s, size, bg, fg):
    f = tfont(size)
    w = d.textlength(s, font=f) + size * 1.1
    box = (cx - w / 2 - 30, cy - size / 2 - 16, cx + w / 2 + 30, cy + size / 2 + 16)
    rr(d, (box[0] + 4, box[1] + 8, box[2] + 4, box[3] + 8), (box[3] - box[1]) / 2, (0, 0, 0, 60))
    rr(d, box, (box[3] - box[1]) / 2, bg)
    ix = box[0] + 30
    bw, bh = size * 0.22, size * 0.8
    d.rounded_rectangle((ix, cy - bh / 2, ix + bw, cy + bh / 2), 4, fill=fg)
    d.rounded_rectangle((ix + bw * 1.9, cy - bh / 2, ix + bw * 2.9, cy + bh / 2), 4, fill=fg)
    d.text((ix + size * 0.85 + (w - size * 1.1) / 2, cy + 2), s, font=f, fill=fg, anchor="mm")


def burst(d, lt, cx, cy, dur=1.6, power=1.0):
    if not 0 <= lt < dur:
        return
    for (vx, vy, col, sz, ph) in _S["burst"]:
        x = cx + vx * 640 * lt * power
        y = cy + vy * 760 * lt * power + 950 * lt * lt
        ang = ph + lt * 8
        pts = [(x + sz * math.cos(ang + j * math.pi / 2) * (1 if j % 2 else 0.5),
                y + sz * math.sin(ang + j * math.pi / 2) * (1 if j % 2 else 0.5)) for j in range(4)]
        d.polygon(pts, fill=col + (int(255 * max(0, 1 - lt / dur)),))


def title2(d, l1, l2, y1, y2, s1, s2, scale=1.0, sh=0.0):
    text(d, (540 + sh, y1), l1, tfont(int(s1 * scale)), WHITE, 13, DARK, sh=10)
    text(d, (540 - sh, y2), l2, tfont(int(s2 * scale)), YEL, 14, DARK, sh=10)


# ------------------------------------------------------------------ escenas

def draw_hook(img, d, sc, lt):
    c = _S["c"]
    l1, l2 = c["gancho"]["texto"]
    p = ease_out(lt / 0.28)
    sh = math.sin(lt * 50) * 10 * max(0, 1 - lt / 0.35)
    # cartas que salen del mazo girando
    for i in range(3):
        t0 = 0.12 + 0.12 * i
        a = ease_out((lt - t0) / 0.5) if lt > t0 else 0
        x = 525 + (CARD_X[i] - 525) * a
        y = CARD_Y + 40 + (1 - a) * 260 + math.sin(lt * 3 + i) * 10 * a
        ang = (1 - a) * (200 - 140 * i) + math.sin(lt * 2.5 + i) * 4 * a
        draw_card(img, _S["backs"][(-1, i)], x, y, 0.75 + 0.25 * a, 1.0, ang)
    title2(d, l1, l2, 360, 520, 150, 150, 1.14 - 0.14 * p, sh)
    for j, (x, y) in enumerate([(125, 660), (955, 650)]):
        a = pop(lt, 0.3 + 0.15 * j, 0.4)
        paste_c(img, _spr("cartas/brindis.png" if j == 0 else "cartas/party.png", 150), x,
                y + math.sin(lt * 4 + j) * 12, a, angle=(-12 if j == 0 else 12))
    b = pop(lt, 0.55, 0.4)
    if b > 0:
        pill(d, 540, 1310 + (1 - b) * 120, c["gancho"]["pegatina"], int(60 * max(b, 0.1)), YEL, DARK,
             pad=(40, 22))
    burst(d, lt - 0.05, 540, 700, 1.4, 1.1)
    if lt < 0.18:
        img.paste(WHITE, (0, 0), Image.new("L", (W, H), int(200 * (1 - lt / 0.18))))


def draw_instr(img, d, sc, lt):
    c = _S["c"]
    pause_pill(d, 540, 330, "PAUSA PARA ELEGIR", 54, WHITE, DARK)
    d.text((540, 470), "¿CÓMO SE JUEGA?", font=tfont(78), fill=WHITE, anchor="mm", stroke_width=10,
           stroke_fill=DARK)
    for i in range(3):
        a = pop(lt, 0.4 + 0.35 * i, 0.4)
        y = 860 + (1 - a) * 80 + math.sin(lt * 3 + i) * 8
        draw_card(img, _S["backs"][(-1, i)], CARD_X[i], y, 0.62 + 0.18 * a if a > 0 else 0.0, 1.0,
                  math.sin(lt * 2 + i) * 3)
    a = pop(lt, 0.3, 0.45)
    if a > 0:
        y0 = 1130 + (1 - a) * 200
        box = (90, y0, 990, y0 + 340)
        rr(d, (box[0] + 6, box[1] + 12, box[2] + 6, box[3] + 12), 40, (0, 0, 0, 70))
        rr(d, box, 40, WHITE)
        for i, s in enumerate(c["instrucciones"]["pasos"]):
            yy = y0 + 62 + i * 84
            d.ellipse((140, yy - 30, 200, yy + 30), fill=ROUND_COLORS[i * 2][1])
            d.text((170, yy + 2), str(i + 1), font=tfont(40), fill=WHITE, anchor="mm")
            d.text((228, yy + 2), s, font=tfont(48), fill=DARK, anchor="lm")
        d.text((540, y0 + 305), c["instrucciones"]["nota"], font=font(34), fill=(130, 110, 150), anchor="mm")


def round_header(d, sc, lt):
    k, r, n = sc["k"], sc["r"], sc["n"]
    a = pop(lt, 0.15, 0.4)
    # puntos de progreso
    for i in range(n):
        x = 540 + (i - (n - 1) / 2) * 62
        col = ROUND_COLORS[i][0]
        if i < k:
            d.ellipse((x - 18, 200 - 18, x + 18, 200 + 18), fill=WHITE)
            check(d, x, 202, 18, ROUND_COLORS[i][1], 6)
        elif i == k:
            rad = 24 + 3 * math.sin(lt * 6)
            d.ellipse((x - rad, 200 - rad, x + rad, 200 + rad), fill=WHITE, outline=col, width=6)
            d.text((x, 203), str(i + 1), font=tfont(30), fill=ROUND_COLORS[i][1], anchor="mm")
        else:
            d.ellipse((x - 16, 200 - 16, x + 16, 200 + 16), fill=(255, 255, 255, 80))
    if a > 0:
        d.text((540, 300), f"RONDA {k + 1}" if not r.get("dorada") else "ÚLTIMA RONDA", font=tfont(int(54 * a)),
               fill=(255, 255, 255, 235), anchor="mm", stroke_width=7, stroke_fill=DARK)
        text(d, (540, 410), r["nombre"], tfont(int(112 * a)), YEL if r.get("dorada") else WHITE, 13, DARK, sh=10)


def draw_round(img, d, sc, lt):
    k, r = sc["k"], sc["r"]
    round_header(d, sc, lt)
    cd = sc["cd"]
    gold = bool(r.get("dorada"))
    for i in range(3):
        t0 = 0.2 + 0.1 * i
        a = ease_out((lt - t0) / 0.45) if lt > t0 else 0
        if a <= 0:
            continue
        x = 525 + (CARD_X[i] - 525) * a
        ft = sc["flips"][i]
        float_y = math.sin(lt * 3 + i * 1.3) * 9
        if lt < ft:
            # boca abajo, flotando; durante la cuenta atrás tiemblan un poco
            ang = (1 - a) * (150 - 120 * i) + math.sin(lt * 2.2 + i) * 3
            if cd <= lt < cd + COUNTDOWN:
                ang += math.sin(lt * 30 + i) * 1.5
            y = CARD_Y + (1 - a) * 400 + float_y
            draw_card(img, _S["backs"][(k, i)], x, y, 0.8 + 0.2 * a, 1.0, ang)
            if gold:
                g = 0.5 + 0.5 * math.sin(lt * 5 + i)
                d.text((x, y - 240), "?", font=tfont(int(60 + 8 * g)), fill=YEL, anchor="mm", stroke_width=6,
                       stroke_fill=DARK)
        else:
            q = min(1.0, (lt - ft) / 0.42)
            fx = math.cos(math.pi * q)
            lift = -40 * math.sin(math.pi * q)
            sc_ = 1.0 + 0.12 * math.sin(math.pi * q) + (0.04 * math.sin((lt - ft) * 7) if q >= 1 and
                                                       r["cartas"][i]["tag"] in ("DORADA",) else 0)
            y = CARD_Y + lift + float_y * (1 if q >= 1 else 0)
            spr = _S["backs"][(k, i)] if fx > 0 else _S["faces"][(k, i)]
            if r["cartas"][i]["tag"] == "DORADA" and q >= 1:
                gl = 0.5 + 0.5 * math.sin(lt * 6)
                d.ellipse((x - 220, y - 290, x + 220, y + 290), fill=(255, 220, 90, int(50 + 60 * gl)))
            draw_card(img, spr, x, y, sc_, fx)
            if q < 1 and q > 0.45:
                d.ellipse((x - 160, y - 220, x + 160, y + 220), outline=(255, 255, 255, int(150 * (1 - q))), width=8)
    # cuenta atrás + pausa
    if cd - 0.3 <= lt < cd + COUNTDOWN + 0.3:
        a = pop(lt, cd - 0.3, 0.35) if lt < cd + COUNTDOWN else 1 - ease_in((lt - cd - COUNTDOWN) / 0.3)
        rem = max(0.0, cd + COUNTDOWN - lt)
        n = min(COUNTDOWN, int(math.ceil(rem))) if lt >= cd else COUNTDOWN
        urgent = lt >= cd and rem <= 2
        col = (239, 55, 70) if urgent else ROUND_COLORS[k][1]
        beat = 1 + (0.09 * max(0, math.cos((lt - cd) * 2 * math.pi)) if urgent else 0)
        R = 72 * a * beat
        cx, cy = 525, 1330
        if R > 18:
            d.ellipse((cx - R + 4, cy - R + 10, cx + R + 4, cy + R + 10), fill=(0, 0, 0, 60))
            d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=WHITE)
            frac = rem / COUNTDOWN if lt >= cd else 1.0
            d.arc((cx - R + 7, cy - R + 7, cx + R - 7, cy + R - 7), -90, -90 + 360 * frac, fill=col,
                  width=max(1, int(13 * a)))
            if n > 0:
                d.text((cx, cy + 4), str(n), font=tfont(int(80 * a * beat)), fill=col if urgent else DARK,
                       anchor="mm")
        if a > 0.3:
            pulse = 1 + 0.05 * math.sin(lt * 8)
            pause_pill(d, 525, 1475, "¡PAUSA Y ELEGID!", int(48 * pulse), YEL, DARK)
        if lt < cd + 1.2 and a > 0.3:
            d.text((540, 560), "1, 2 o 3", font=tfont(70), fill=WHITE, anchor="mm", stroke_width=9,
                   stroke_fill=DARK)
    # brindis al final
    ch = sc["cheer"]
    if ch is not None and lt >= ch:
        lt2 = lt - ch
        b = pop(lt, ch, 0.35)
        txt = sc["cheer_txt"] or "¡A BEBER!"
        pill(d, 525, 1360 + (1 - b) * 120, txt.upper(), int(70 * max(b, 0.1)), WHITE, ROUND_COLORS[k][1],
             pad=(44, 24))
        for j, (x, ang) in enumerate([(200, -18), (850, 18)]):
            paste_c(img, _spr("cartas/copas.png", 150), x + math.sin(lt2 * 10) * 6 * (1 if j else -1), 1350,
                    b, angle=ang + math.sin(lt2 * 12) * 6)
        burst(d, lt2, 525, 950, 1.6)


def draw_outro(img, d, sc, lt):
    a = pop(lt, 0.1, 0.45)
    y = 330 + (1 - a) * -600
    box = (80, y, 1000, y + 400)
    rr(d, (box[0] + 6, box[1] + 14, box[2] + 6, box[3] + 14), 48, (0, 0, 0, 70))
    rr(d, box, 48, WHITE)
    f = tfont(96)
    d.text((540, y + 120), "¿QUIÉN HA", font=f, fill=DARK, anchor="mm")
    d.text((540, y + 225), "BEBIDO MÁS?", font=f, fill=(214, 40, 110), anchor="mm")
    d.text((540, y + 330), "¡Etiquétalo en comentarios!", font=font(52), fill=(120, 60, 200), anchor="mm")
    for i in range(3):
        t0 = 0.25 + 0.1 * i
        b = pop(lt, t0, 0.4)
        if b > 0:
            draw_card(img, _S["faces"][(i, i)], 330 + i * 210, 960 + math.sin(lt * 4 + i) * 12, 0.55 * b, 1.0,
                      (i - 1) * 12)
    c2 = pop(lt, sc["shout_at"] - 0.15, 0.4)
    if c2 > 0:
        pulse = 1 + 0.07 * math.sin(lt * 9)
        pill(d, 540, 1210 + (1 - c2) * 700, "¡SÍGUEME PARA MÁS!", int(64 * pulse), YEL, DARK)
    c3 = pop(lt, sc["shout_at"] + 0.2, 0.6)
    if c3 > 0:
        size = 300 * c3 * (1 + 0.025 * math.sin(lt * 4))
        d.ellipse((540 - size / 2, 1440 - size / 2 + 14, 540 + size / 2, 1440 + size / 2 + 14), fill=(0, 0, 0, 70))
        paste_c(img, _S["logo"], 540, 1440, size / _S["logo"].width)
    burst(d, lt - sc["shout_at"], 540, 1000, 1.8, 1.2)


DRAW = {"hook": draw_hook, "instr": draw_instr, "round": draw_round, "outro": draw_outro}


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
    out_t = sc["dur"] - lt
    if out_t < 0.2 and sc is not scenes[-1]:
        img = Image.blend(bg, img, max(0.0, out_t / 0.2))
    username(img)
    return img.tobytes()


# ------------------------------------------------------------------ portada

def portada(c, state, out_dir):
    _init(state)
    img = _bg_frame(-1, 1.3)
    d = ImageDraw.Draw(img, "RGBA")
    l1, l2 = c["portada"]["titulo"]
    title2(d, l1, l2, 400, 560, 160, 160)
    draw_card(img, _S["backs"][(0, 0)], 290, 1010, 1.0, 1.0, 12)
    draw_card(img, _S["backs"][(len(c["rondas"]) - 1, 2)], 790, 1010, 1.0, 1.0, -12)
    draw_card(img, _S["faces"][(1, 0)], 540, 960, 1.08, 1.0, 0)
    paste_c(img, _spr("cartas/brindis.png", 170), 175, 400, 1.0, angle=-14)
    paste_c(img, _spr("cartas/party.png", 170), 905, 395, 1.0, angle=14)
    st = Image.new("RGBA", (920, 150), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    rr(sd, (8, 16, 912, 146), 60, (0, 0, 0, 80))
    rr(sd, (0, 4, 904, 134), 60, YEL, outline=WHITE, width=7)
    f = tfont(64)
    while sd.textlength(c["portada"]["pegatina"], font=f) > 820:
        f = tfont(f.size - 3)
    sd.text((452, 72), c["portada"]["pegatina"], font=f, fill=DARK, anchor="mm")
    paste_c(img, st, 540, 1440, 1.0, angle=-3)
    username(img, 1616)
    p916 = os.path.join(out_dir, f"{c['video']}_9x16.png")
    p34 = os.path.join(out_dir, f"{c['video']}_3x4.png")
    img.save(p916)
    img.crop((0, 240, 1080, 1680)).save(p34)
    return p916, p34


# ------------------------------------------------------------------ exportación

def render_video(c, voice, out_path, tono, workers=None, preview=None):
    scenes, events, total = build_timeline(c, voice)
    state = {"scenes": scenes, "c": c, "tono": tono}
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
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-level", "4.1", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
           "-shortest", "-movflags", "+faststart", out_path]
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

"""Monta el vídeo: calcula la línea de tiempo, dibuja los fotogramas y exporta a MP4."""

import math
import os
import random
import subprocess
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from . import audio

W, H = 1080, 1920
FPS = 30
LETTERS = "ABCD"

FONT_DIRS = [os.path.join(os.path.dirname(__file__), "..", "fuentes")]
FONT_FALLBACKS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]

# Zona segura de TikTok: evitamos ~150 px arriba, ~370 px abajo y ~120 px a la derecha.
CARD_Y, CARD_H = 290, 420
TIMER_C, TIMER_R = (540, 835), 92
OPT_Y, OPT_H, OPT_GAP = 970, 128, 22
OPT_X0, OPT_X1 = 70, 1010

DIFICULTAD = {"facil": "FÁCIL", "fácil": "FÁCIL", "media": "MEDIA", "dificil": "DIFÍCIL", "difícil": "DIFÍCIL"}


# ------------------------------------------------------------------ utilidades

def ease_out_back(x):
    x = min(max(x, 0.0), 1.0)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = min(max(x, 0.0), 1.0)
    return x ** 3


def _font_path():
    for d in FONT_DIRS:
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.lower().endswith((".ttf", ".otf")):
                    return os.path.join(d, f)
    for f in FONT_FALLBACKS:
        if os.path.exists(f):
            return f
    raise SystemExit("No encuentro ninguna fuente TTF.")


_FONT_CACHE = {}


def font(size):
    size = max(8, int(size))
    if size not in _FONT_CACHE:
        _FONT_CACHE[size] = ImageFont.truetype(_font_path(), size)
    return _FONT_CACHE[size]


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=fnt) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, max_w, max_h, start, minimum=28, spacing=1.12):
    size = start
    while size >= minimum:
        f = font(size)
        lines = wrap(draw, text, f, max_w)
        lh = size * spacing
        if len(lines) * lh <= max_h and all(draw.textlength(l, font=f) <= max_w for l in lines):
            return f, lines, lh
        size -= 3
    f = font(minimum)
    return f, wrap(draw, text, f, max_w), minimum * spacing


def draw_lines(draw, lines, fnt, lh, cx, cy, fill, stroke=0, stroke_fill=None):
    total = lh * len(lines)
    y = cy - total / 2 + lh / 2
    for line in lines:
        draw.text((cx, y), line, font=fnt, fill=fill, anchor="mm",
                  stroke_width=stroke, stroke_fill=stroke_fill)
        y += lh


def with_alpha(c, a):
    return (c[0], c[1], c[2], int(max(0, min(1, a)) * 255))


def shadow_box(draw, box, radius, alpha=0.28, off=12):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle((x0, y0 + off, x1, y1 + off), radius, fill=(0, 0, 0, int(255 * alpha)))


# ------------------------------------------------------------------ línea de tiempo

def build_timeline(quiz, voice, countdown=5):
    """Devuelve (escenas, eventos_de_audio, duración_total)."""
    scenes, events = [], []
    t = 0.0
    n = len(quiz["preguntas"])
    tema = quiz["tema"]

    def say(text):
        sig, dur = voice.say(text)
        return sig, dur

    # Intro
    intro_text = quiz.get("titulo") or f"¿Cuánto sabes de {tema}?"
    sig, d = say(f"{intro_text} Tienes {countdown} segundos por pregunta.")
    dur = max(2.8, 0.35 + d + 0.35)
    events += [("fx", "whoosh", t), ("voice", sig, t + 0.35)]
    scenes.append({"kind": "intro", "start": t, "dur": dur, "title": intro_text})
    t += dur

    for qi, q in enumerate(quiz["preguntas"]):
        st = t
        loc = 0.5
        sig, dq = say(q["pregunta"])
        events += [("fx", "whoosh", st), ("voice", sig, st + loc)]
        loc += dq + 0.25
        opt_times = []
        for k, o in enumerate(q["opciones"]):
            sig, do = say(f"{LETTERS[k]}: {o}." if voice.name != "sin voz" else o)
            if voice.name == "sin voz":
                do = 0.35
            opt_times.append(loc)
            events += [("fx", "pop", st + loc), ("voice", sig, st + loc + 0.05)]
            loc += do + 0.12
        cd_start = loc + 0.25
        for s in range(countdown):
            events.append(("fx", "tick_high" if s >= countdown - 2 else "tick", st + cd_start + s))
        rv = cd_start + countdown
        ci = LETTERS.index(q["correcta"].upper())
        sig, dv = say(f"¡La correcta es la {LETTERS[ci]}! {q['opciones'][ci]}.")
        events += [("fx", "buzz", st + rv), ("fx", "correct", st + rv + 0.15), ("voice", sig, st + rv + 0.55)]
        rdur = max(2.2, 0.55 + dv + 0.45)
        dur = rv + rdur
        scenes.append({"kind": "question", "start": st, "dur": dur, "q": q, "index": qi, "total": n,
                       "opt_times": opt_times, "cd_start": cd_start, "countdown": countdown,
                       "reveal": rv, "correct": ci})
        t += dur

    sig, d = say("¿Cuántas has acertado? Déjalo en comentarios y sígueme para más quizzes.")
    dur = max(3.2, 0.4 + d + 0.8)
    events += [("fx", "whoosh", t), ("voice", sig, t + 0.4)]
    scenes.append({"kind": "outro", "start": t, "dur": dur})
    t += dur
    return scenes, events, t


def build_audio(events, total, path, music_on=True):
    mix = audio.Mixer(total)
    fx = {
        "whoosh": audio.sfx_whoosh(), "pop": audio.sfx_pop(), "tick": audio.sfx_tick(),
        "tick_high": audio.sfx_tick(True), "buzz": audio.sfx_buzz_end(), "correct": audio.sfx_correct(),
    }
    gains = {"whoosh": 0.5, "pop": 0.6, "tick": 0.9, "tick_high": 1.0, "buzz": 0.6, "correct": 0.9}
    for kind, what, at in events:
        if kind == "fx":
            mix.add_fx(fx[what], at, gains[what])
        elif what is not None:
            mix.add_voice(what, at, 1.0)
    music = audio.music(total) if music_on else np.zeros(int(total * audio.SR))
    audio.write_wav(path, mix.render(music))


# ------------------------------------------------------------------ dibujo

_STATE = {}


def _init(state):
    _STATE.update(state)
    th = state["theme"]
    top, bot = np.array(th["bg_top"], float), np.array(th["bg_bottom"], float)
    yy = np.linspace(0, 1, H)[:, None, None]
    xx = np.linspace(0, 1, W)[None, :, None]
    g = top * (1 - (0.75 * yy + 0.25 * xx)) + bot * (0.75 * yy + 0.25 * xx)
    _STATE["bg"] = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    rnd = random.Random(11)
    _STATE["bubbles"] = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(30, 150), rnd.uniform(25, 90),
                          rnd.uniform(0.08, 0.2), rnd.uniform(0, 6.28)) for _ in range(16)]
    _STATE["confetti"] = [(rnd.uniform(-1, 1), rnd.uniform(-1.4, -0.4), rnd.randint(0, 4),
                           rnd.uniform(12, 26), rnd.uniform(0, 6.28)) for _ in range(70)]


def _background(t):
    th = _STATE["theme"]
    img = _STATE["bg"].copy()
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x0, y0, r, sp, a, ph in _STATE["bubbles"]:
        y = (y0 - sp * t) % (H + 2 * r) - r
        x = x0 + 30 * math.sin(t * 0.7 + ph)
        d.ellipse((x - r, y - r, x + r, y + r), fill=with_alpha(th["blob"], a))
    # franjas diagonales sutiles
    off = (t * 40) % 160
    for k in range(-4, 20):
        x = k * 160 + off
        d.polygon([(x, 0), (x + 50, 0), (x + 50 - 700, H), (x - 700, H)], fill=(255, 255, 255, 10))
    img.alpha_composite(layer)
    return img


def _pill(d, cx, cy, text, size, bg, fg, pad=(34, 16)):
    f = font(size)
    w = d.textlength(text, font=f)
    box = (cx - w / 2 - pad[0], cy - size / 2 - pad[1], cx + w / 2 + pad[0], cy + size / 2 + pad[1])
    shadow_box(d, box, (box[3] - box[1]) / 2, 0.25, 7)
    d.rounded_rectangle(box, (box[3] - box[1]) / 2, fill=bg)
    d.text((cx, cy), text, font=f, fill=fg, anchor="mm")


def _check(d, cx, cy, s, color, width=10):
    d.line([(cx - s * 0.5, cy), (cx - s * 0.12, cy + s * 0.4), (cx + s * 0.55, cy - s * 0.45)],
           fill=color, width=width, joint="curve")


def _draw_intro(layer, sc, lt):
    th = _STATE["theme"]
    d = ImageDraw.Draw(layer)
    quiz = _STATE["quiz"]
    # "QUIZ" que rebota
    p = ease_out_back(lt / 0.6)
    size = 60 + 190 * p + 8 * math.sin(lt * 5)
    d.text((540, 470), "QUIZ", font=font(size), fill=th["accent"], anchor="mm",
           stroke_width=14, stroke_fill=th["text_dark"])
    # tarjeta con el título
    a = ease_out_back((lt - 0.25) / 0.5)
    y = 620 + (1 - a) * 900
    box = (80, y, 1000, y + 470)
    shadow_box(d, box, 50)
    d.rounded_rectangle(box, 50, fill=th["card"])
    f, lines, lh = fit(d, sc["title"], 820, 380, 86)
    draw_lines(d, lines, f, lh, 540, y + 235, th["text_dark"])
    # etiquetas
    b = ease_out_back((lt - 0.55) / 0.45)
    if b > 0:
        dif = DIFICULTAD.get(str(quiz.get("dificultad", "media")).lower(), str(quiz.get("dificultad", "")).upper())
        _pill(d, 540 - (1 - b) * 1200, 1210, f"NIVEL: {dif}", 50, th["accent2"], th["text_light"])
        n = len(quiz["preguntas"])
        _pill(d, 540 + (1 - b) * 1200, 1340,
              f"{n} PREGUNTAS · {_STATE['countdown']} SEGUNDOS", 44, th["accent"], th["text_dark"])


def _draw_outro(layer, sc, lt):
    th = _STATE["theme"]
    d = ImageDraw.Draw(layer)
    a = ease_out_back(lt / 0.5)
    y = 380 + (1 - a) * -800
    box = (80, y, 1000, y + 520)
    shadow_box(d, box, 50)
    d.rounded_rectangle(box, 50, fill=th["card"])
    f, lines, lh = fit(d, "¿Cuántas has acertado?", 820, 300, 110)
    draw_lines(d, lines, f, lh, 540, y + 200, th["text_dark"])
    d.text((540, y + 420), "¡Escríbelo en comentarios!", font=font(54), fill=th["accent2"], anchor="mm")
    b = ease_out_back((lt - 0.5) / 0.5)
    if b > 0:
        pulse = 1 + 0.05 * math.sin(lt * 7)
        _pill(d, 540, 1150 + (1 - b) * 900, "¡SÍGUEME PARA MÁS!", int(64 * pulse), th["accent"], th["text_dark"])


def _draw_question(layer, sc, lt):
    th = _STATE["theme"]
    d = ImageDraw.Draw(layer)
    q = sc["q"]
    revealed = lt >= sc["reveal"]
    rlt = lt - sc["reveal"]

    # cabecera: pregunta X/N + puntos de progreso
    a = ease_out_back(lt / 0.45)
    _pill(d, 540, 175 - (1 - a) * 300, f"PREGUNTA {sc['index'] + 1}/{sc['total']}", 46,
          th["accent"], th["text_dark"])

    # tarjeta de la pregunta
    a = ease_out_back((lt - 0.05) / 0.5)
    y = CARD_Y + (1 - a) * -700
    box = (OPT_X0, y, OPT_X1, y + CARD_H)
    shadow_box(d, box, 44)
    d.rounded_rectangle(box, 44, fill=th["card"])
    f, lines, lh = fit(d, q["pregunta"], 840, CARD_H - 70, 78, 40)
    draw_lines(d, lines, f, lh, 540, y + CARD_H / 2, th["text_dark"])

    # cronómetro
    cs, n = sc["cd_start"], sc["countdown"]
    if lt >= cs - 0.3:
        ap = ease_out_back((lt - cs + 0.3) / 0.35)
        cx, cy = TIMER_C
        r = TIMER_R * ap
        remaining = max(0.0, n - (lt - cs)) if lt >= cs else n
        frac = remaining / n
        col = th["correct"] if frac > 0.6 else ((255, 190, 0) if frac > 0.3 else (255, 60, 60))
        if revealed:
            col = th["accent2"]
        shake = 6 * math.sin(lt * 60) if (0 < remaining <= 2 and not revealed) else 0
        cx += shake
        d.ellipse((cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8), fill=(0, 0, 0, 60))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, 255))
        if r > 10:
            d.arc((cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6), -90, -90 + 360 * frac, fill=col, width=18)
        if revealed:
            _check(d, cx, cy, r * 0.9, th["correct"], 16)
        else:
            num = math.ceil(remaining) if lt >= cs else n
            beat = (lt - cs) % 1 if lt >= cs else 1
            pop = 1 + 0.35 * (1 - ease_out(beat / 0.25)) if lt >= cs else 1
            d.text((cx, cy + 4), str(max(1, num)), font=font(96 * pop * ap), fill=th["text_dark"], anchor="mm")

    # opciones
    for k, opt in enumerate(q["opciones"]):
        ot = sc["opt_times"][k]
        if lt < ot:
            continue
        p = ease_out_back((lt - ot) / 0.4)
        yy = OPT_Y + k * (OPT_H + OPT_GAP)
        xoff = (1 - p) * 1100
        x0, x1 = OPT_X0 + xoff, OPT_X1 + xoff
        is_ok = k == sc["correct"]
        fill, txt, badge, btxt = th["card"], th["text_dark"], th["options"][k], th["text_light"]
        grow = 0
        if revealed:
            rp = ease_out(rlt / 0.35)
            if is_ok:
                fill, txt, badge, btxt = th["correct"], th["text_light"], th["text_light"], th["correct"]
                grow = 14 * ease_out_back(rlt / 0.4) + 4 * math.sin(rlt * 8) * (rlt > 0.4)
            else:
                g = th["wrong"]
                fill = tuple(int(th["card"][i] * (1 - rp) + g[i] * rp) for i in range(3))
                txt = tuple(int(th["text_dark"][i] * (1 - rp) + 235 * rp) for i in range(3))
                badge = tuple(int(th["options"][k][i] * (1 - rp) + 150 * rp) for i in range(3))
        b = (x0 - grow, yy - grow / 2, x1 + grow, yy + OPT_H + grow / 2)
        shadow_box(d, b, 36, 0.25, 9)
        d.rounded_rectangle(b, 36, fill=fill)
        bc = (x0 + 70 - grow, yy + OPT_H / 2)
        d.ellipse((bc[0] - 46, bc[1] - 46, bc[0] + 46, bc[1] + 46), fill=badge)
        if revealed and is_ok:
            _check(d, bc[0], bc[1], 52, btxt, 11)
        else:
            d.text(bc, LETTERS[k], font=font(56), fill=btxt, anchor="mm")
        f, lines, lh = fit(d, opt, x1 - x0 - 190, OPT_H - 24, 54, 30)
        draw_lines(d, lines, f, lh, (x0 + 140 + x1) / 2, yy + OPT_H / 2, txt)

    # confeti en la revelación
    if revealed and rlt < 2.5:
        yy = OPT_Y + sc["correct"] * (OPT_H + OPT_GAP) + OPT_H / 2
        cols = th["options"] + [th["accent"]]
        for vx, vy, ci, s, ph in _STATE["confetti"]:
            tt = rlt
            x = 540 + vx * 900 * tt
            y = yy + vy * 1300 * tt + 1400 * tt * tt
            ang = ph + tt * 8
            dx, dy = math.cos(ang) * s, math.sin(ang) * s * 0.5
            alpha = 1 - max(0, (tt - 1.6) / 0.9)
            d.polygon([(x - dx, y - dy), (x + dy, y - dx), (x + dx, y + dy), (x - dy, y + dx)],
                      fill=with_alpha(cols[ci], alpha))


def render_frame(i):
    t = i / FPS
    scenes = _STATE["scenes"]
    img = _background(t)
    for sc in scenes:
        lt = t - sc["start"]
        if 0 <= lt < sc["dur"]:
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            {"intro": _draw_intro, "question": _draw_question, "outro": _draw_outro}[sc["kind"]](layer, sc, lt)
            out_t = sc["dur"] - lt
            if out_t < 0.3 and sc is not scenes[-1]:
                # transición de salida: desliza hacia la izquierda
                shift = int(-ease_in(1 - out_t / 0.3) * W)
                moved = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                moved.paste(layer, (shift, 0))
                layer = moved
            img.alpha_composite(layer)
            break
    return img.convert("RGB").tobytes()


# ------------------------------------------------------------------ exportación

def render_video(quiz, theme, voice, out_path, countdown=5, workers=None, music_on=True, preview=None):
    scenes, events, total = build_timeline(quiz, voice, countdown)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    wav = out_path + ".audio.wav"
    build_audio(events, total, wav, music_on)
    frames = int(total * FPS)
    state = {"scenes": scenes, "theme": theme, "quiz": quiz, "countdown": countdown}

    if preview is not None:  # solo un fotograma PNG para revisar el diseño
        _init(state)
        Image.frombytes("RGB", (W, H), render_frame(int(preview * FPS))).save(out_path)
        os.remove(wav)
        return total

    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav,
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-level", "4.1",
           "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
           "-shortest", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers or os.cpu_count(), initializer=_init, initargs=(state,)) as pool:
        for k, fr in enumerate(pool.imap(render_frame, range(frames), chunksize=8)):
            proc.stdin.write(fr)
            if k % (FPS * 5) == 0:
                print(f"  fotograma {k}/{frames}", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg falló al exportar el vídeo.")
    os.remove(wav)
    return total

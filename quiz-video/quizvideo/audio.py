"""Música de fondo y efectos de sonido sintetizados con numpy (sin archivos externos)."""

import wave

import numpy as np

SR = 44100


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def _env(n, attack=0.005, decay=0.2):
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-t / max(decay, 1e-4))


def _note(freq, dur, wave_kind="saw", decay=0.25, attack=0.004):
    t = _t(dur)
    if wave_kind == "sine":
        w = np.sin(2 * np.pi * freq * t)
    elif wave_kind == "square":
        w = np.sign(np.sin(2 * np.pi * freq * t)) * 0.6
    elif wave_kind == "tri":
        w = 2 * np.abs(2 * ((freq * t) % 1) - 1) - 1
    else:  # saw suavizada (dos osciladores desafinados)
        w = 0.5 * (2 * ((freq * t) % 1) - 1) + 0.5 * (2 * ((freq * 1.006 * t) % 1) - 1)
    return w * _env(len(t), attack, decay)


def _lowpass(x, alpha):
    """Filtro paso bajo de un polo (alpha entre 0 y 1; menor = más oscuro)."""
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += alpha * (v - acc)
        y[i] = acc
    return y


def _midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# ---------------------------------------------------------------- efectos

def sfx_tick(high=False):
    """Tic de reloj tipo bloque de madera (más agudo en los últimos segundos)."""
    f = 2100 if high else 1500
    t = _t(0.06)
    body = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.7 * t)
    click = np.random.default_rng(1).standard_normal(len(t)) * np.exp(-t * 900) * 0.6
    return 0.6 * (body * np.exp(-t * 70) + click)


def sfx_tock():
    t = _t(0.07)
    body = np.sin(2 * np.pi * 950 * t) + 0.4 * np.sin(2 * np.pi * 2300 * t)
    return 0.45 * body * np.exp(-t * 60)


def sfx_heartbeat():
    """Latido grave doble (lub-dub)."""
    out = np.zeros(int(0.5 * SR))
    for off, g in ((0.0, 1.0), (0.17, 0.7)):
        t = _t(0.18)
        f = 48 + 30 * np.exp(-t * 20)
        th = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.004, 0.07)
        s = int(off * SR)
        out[s:s + len(th)] += g * th
    return 0.9 * out


def sfx_riser(dur=5.0):
    """Subida de tensión: sierra filtrada cuyo tono y volumen crecen durante la cuenta atrás."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 110 * 2 ** (t / dur * 2.0)  # dos octavas
    ph = np.cumsum(f) / SR
    saw = 2 * (ph % 1) - 1 + 0.5 * (2 * ((ph * 1.01) % 1) - 1)
    noise = np.random.default_rng(4).standard_normal(n) * 0.15
    sig = _lowpass(saw + noise, 0.08) 
    env = (t / dur) ** 2
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * (4 + 8 * t / dur) * t)
    return 0.5 * sig * env * trem


def sfx_pop():
    t = _t(0.12)
    f = 500 + 900 * np.exp(-t * 30)
    return 0.5 * np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.002, 0.05)


def sfx_whoosh(dur=0.45):
    rng = np.random.default_rng(3)
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    # barrido: paso bajo cuyo corte sube y baja
    out = np.empty(n)
    acc = 0.0
    for i in range(n):
        p = i / n
        alpha = 0.02 + 0.35 * np.sin(np.pi * p) ** 2
        acc += alpha * (noise[i] - acc)
        out[i] = acc
    return 0.6 * out * np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5


def sfx_correct():
    """Arpegio brillante tipo 'ta-da'."""
    out = np.zeros(int(1.3 * SR))
    for k, m in enumerate([72, 76, 79, 84]):
        s = _note(_midi(m), 1.0, "tri", decay=0.35) + 0.4 * _note(_midi(m + 12), 1.0, "sine", decay=0.25)
        st = int(k * 0.07 * SR)
        out[st:st + len(s)] += 0.32 * s[: len(out) - st]
    return out


def sfx_buzz_end():
    """Gong corto al acabar el tiempo."""
    t = _t(0.5)
    w = np.sin(2 * np.pi * 220 * t) + 0.5 * np.sin(2 * np.pi * 331 * t)
    return 0.35 * w * _env(len(t), 0.003, 0.18)


def sfx_applause(dur=2.5, seed=5):
    """Aplausos y vítores sintetizados (muchas palmadas aleatorias)."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    out = np.zeros(n)
    clap = rng.standard_normal(int(0.03 * SR))
    clap = (clap - _lowpass(clap, 0.2)) * _env(len(clap), 0.0005, 0.008)
    for _ in range(int(dur * 90)):
        s = int(rng.uniform(0, n - len(clap)))
        out[s:s + len(clap)] += clap * rng.uniform(0.3, 1.0)
    shape = np.minimum(1, np.linspace(0, 6, n)) * np.minimum(1, np.linspace(3, 0, n))
    return 0.35 * out * shape


# ---------------------------------------------------------------- música

def music(duration, bpm=118, seed=7, style="pop"):
    if style == "romantica":
        return music_romantica(duration)
    if style == "halloween":
        return music_halloween(duration)
    return music_pop(duration, bpm, seed)


def music_halloween(duration, bpm=104, seed=13):
    """Música de Halloween divertida y misteriosa: La menor armónica (Am–F–Dm–E), órgano con vibrato,
    clavecín en arpegio, bajo pizzicato, campanitas y melodía tipo theremin."""
    beat = 60.0 / bpm
    bar = 4 * beat
    n = int(duration * SR) + SR
    out = np.zeros(n)
    rng = np.random.default_rng(seed)

    def add(sig, start, gain=1.0):
        st = int(start * SR)
        if st >= n:
            return
        e = min(n, st + len(sig))
        out[st:e] += gain * sig[: e - st]

    def organ(m, dur):
        t = _t(dur)
        f = _midi(m) * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * t))
        ph = np.cumsum(f) / SR
        w = np.sign(np.sin(2 * np.pi * ph)) * 0.4 + np.sin(2 * np.pi * 2 * ph) * 0.3 + np.sin(2 * np.pi * 3 * ph) * 0.2
        env = np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.1)
        return w * env

    def theremin(m, dur):
        t = _t(dur)
        f = _midi(m) * (1 + 0.012 * np.sin(2 * np.pi * 6 * t))
        w = np.sin(2 * np.pi * np.cumsum(f) / SR)
        env = np.minimum(1, t / 0.08) * np.minimum(1, (dur - t) / 0.12)
        return w * env

    kick = _t(0.2)
    kick = np.sin(2 * np.pi * np.cumsum(45 + 80 * np.exp(-kick * 25)) / SR) * _env(len(kick), 0.002, 0.1)
    snare = rng.standard_normal(int(0.12 * SR))
    snare = (snare - _lowpass(snare, 0.15)) * _env(len(snare), 0.001, 0.04) * 0.35
    chords = [[57, 60, 64], [53, 57, 60], [50, 53, 57], [52, 56, 59]]   # Am F Dm E
    bass = [45, 41, 38, 40]
    arp = [0, 2, 1, 2, 0, 2, 1, 2]
    melody = [  # (nota, inicio en tiempos, duración en tiempos) para 4 compases
        (76, 0, 1), (81, 1, 1), (84, 2, 1.5), (83, 3.5, 0.5),
        (81, 4, 1), (76, 5, 1), (77, 6, 1.5), (76, 7.5, 0.5),
        (74, 8, 1), (77, 9, 1), (81, 10, 1.5), (80, 11.5, 0.5),
        (76, 12, 1), (80, 13, 1), (83, 14, 1), (88, 15, 1),
    ]
    t, bi = 0.0, 0
    while t < duration + bar:
        k = bi % 4
        ch = chords[k]
        for b in range(4):
            bt = t + b * beat
            add(kick, bt, 0.6 if b in (0, 2) else 0.0)
            if b in (1, 3):
                add(snare, bt, 0.55)
            # bajo pizzicato saltarín
            add(_note(_midi(bass[k]), beat * 0.4, "tri", decay=0.12), bt, 0.5)
            add(_note(_midi(bass[k] + 7), beat * 0.3, "tri", decay=0.08), bt + beat / 2, 0.3)
        for j, pi_ in enumerate(arp):  # clavecín
            m = ch[pi_] + 12
            add(_note(_midi(m), beat * 0.5, "saw", decay=0.09), t + j * beat / 2, 0.08)
        for m in ch:  # órgano de fondo
            add(organ(m, bar * 0.98), t, 0.045)
        if bi % 8 >= 4:  # la melodía entra cada dos frases para no cansar
            for m, st_, du in melody[(k * 4):(k * 4 + 4)]:
                add(theremin(m, du * beat * 0.95), t + (st_ - k * 4) * beat, 0.09)
        else:  # campanitas tétricas
            add(_note(_midi(ch[0] + 24), beat, "sine", decay=0.5), t + 3.5 * beat, 0.08)
        t += bar
        bi += 1
    out = out[: int(duration * SR)]
    f = int(0.6 * SR)
    out[:f] *= np.linspace(0, 1, f)
    out[-int(1.5 * SR):] *= np.linspace(1, 0, int(1.5 * SR))
    return out


def music_romantica(duration, bpm=92, seed=9):
    """Pop suave y romántico: I–vi–IV–V, arpegio de campanitas, bajo redondo y percusión ligera."""
    beat = 60.0 / bpm
    bar = 4 * beat
    n = int(duration * SR) + SR
    out = np.zeros(n)
    rng = np.random.default_rng(seed)
    kick = _t(0.22)
    kick = np.sin(2 * np.pi * np.cumsum(45 + 70 * np.exp(-kick * 25)) / SR) * _env(len(kick), 0.002, 0.12)
    shaker = rng.standard_normal(int(0.06 * SR))
    shaker = (shaker - _lowpass(shaker, 0.35)) * _env(len(shaker), 0.01, 0.02) * 0.18
    snap = rng.standard_normal(int(0.08 * SR))
    snap = (snap - _lowpass(snap, 0.2)) * _env(len(snap), 0.001, 0.03) * 0.25
    chords = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]
    bass = [36, 33, 41, 43]
    arp = [0, 1, 2, 1, 0, 1, 2, 1]

    def add(sig, start, gain=1.0):
        st = int(start * SR)
        if st >= n:
            return
        e = min(n, st + len(sig))
        out[st:e] += gain * sig[: e - st]

    t, bi = 0.0, 0
    while t < duration + bar:
        ch = chords[bi % 4]
        for b in range(4):
            bt = t + b * beat
            if b in (0, 2):
                add(kick, bt, 0.55)
            if b in (1, 3):
                add(snap, bt, 0.5)
            add(shaker, bt + beat / 2, 1.0)
        add(_note(_midi(bass[bi % 4]), bar * 0.95, "sine", decay=bar * 0.5, attack=0.01), t, 0.45)
        for k, pidx in enumerate(arp):
            m = ch[pidx] + 24
            add(_note(_midi(m), beat, "sine", decay=0.35) + 0.3 * _note(_midi(m + 12), beat, "sine", decay=0.15),
                t + k * beat / 2, 0.09)
        for m in ch:
            add(_note(_midi(m), bar, "tri", decay=bar * 0.8, attack=0.25), t, 0.07)
        t += bar
        bi += 1
    out = out[: int(duration * SR)]
    f = int(0.6 * SR)
    out[:f] *= np.linspace(0, 1, f)
    out[-int(1.5 * SR):] *= np.linspace(1, 0, int(1.5 * SR))
    return out


def music_pop(duration, bpm=118, seed=7):
    """Bucle pop alegre: I–V–vi–IV en Do mayor, con bombo, palmas, hi-hats y bajo."""
    beat = 60.0 / bpm
    bar = 4 * beat
    n = int(duration * SR) + SR
    out = np.zeros(n)
    rng = np.random.default_rng(seed)

    kick = _t(0.25)
    kick = np.sin(2 * np.pi * np.cumsum(50 + 110 * np.exp(-kick * 28)) / SR) * _env(len(kick), 0.001, 0.12)
    hat = rng.standard_normal(int(0.05 * SR))
    hat = (hat - _lowpass(hat, 0.3)) * _env(len(hat), 0.001, 0.015) * 0.35
    clap = rng.standard_normal(int(0.15 * SR))
    clap = (clap - _lowpass(clap, 0.12)) * _env(len(clap), 0.001, 0.05) * 0.4

    chords = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
    bass = [36, 43, 45, 41]
    # patrón de pluck en corcheas
    pattern = [0, 1, 2, 1, 0, 2, 1, 2]

    def add(sig, start, gain=1.0):
        s = int(start * SR)
        if s >= n:
            return
        e = min(n, s + len(sig))
        out[s:e] += gain * sig[: e - s]

    t = 0.0
    bar_i = 0
    while t < duration + bar:
        ch = chords[bar_i % 4]
        for b in range(4):
            bt = t + b * beat
            add(kick, bt, 0.9)
            if b in (1, 3):
                add(clap, bt, 0.55)
            add(hat, bt + beat / 2, 1.0)
            add(hat, bt + beat * 0.75, 0.5)
            add(_note(_midi(bass[bar_i % 4]), beat * 0.9, "tri", decay=0.3), bt, 0.42)
        for k, p in enumerate(pattern):
            m = ch[p] + 12
            add(_note(_midi(m), beat * 0.5, "saw", decay=0.12), t + k * beat / 2, 0.11)
        # colchón suave
        for m in ch:
            add(_note(_midi(m), bar, "sine", decay=bar * 0.6, attack=0.08), t, 0.06)
        t += bar
        bar_i += 1
    out = out[: int(duration * SR)]
    # fundido de entrada/salida
    f = int(0.4 * SR)
    out[:f] *= np.linspace(0, 1, f)
    out[-int(1.2 * SR):] *= np.linspace(1, 0, int(1.2 * SR))
    return out


# ---------------------------------------------------------------- mezcla

class Mixer:
    def __init__(self, duration):
        self.n = int(duration * SR)
        self.fx = np.zeros(self.n)
        self.voice = np.zeros(self.n)

    def _add(self, buf, sig, start, gain):
        s = int(start * SR)
        if s >= self.n or sig is None:
            return
        e = min(self.n, s + len(sig))
        buf[s:e] += gain * sig[: e - s]

    def add_fx(self, sig, start, gain=1.0):
        self._add(self.fx, sig, start, gain)

    def add_voice(self, sig, start, gain=1.0):
        self._add(self.voice, sig, start, gain)

    def render(self, music_sig, music_gain=0.32, boosts=(), boost=1.25):
        m = np.zeros(self.n)
        m[: min(self.n, len(music_sig))] = music_sig[: self.n]
        # durante la cuenta atrás la música sube un poco (rampa suave de 0,25 s)
        g = np.ones(self.n)
        for a, b in boosts:
            g[int(a * SR):int(b * SR)] = boost
        ramp = int(0.25 * SR)
        g = np.convolve(g, np.ones(ramp) / ramp, mode="same")
        m *= g
        # ducking: baja la música mientras habla la voz
        env = np.abs(self.voice)
        win = int(0.05 * SR)
        env = np.convolve(env, np.ones(win) / win, mode="same")
        env = np.clip(env * 12, 0, 1)
        env = np.convolve(env, np.ones(win * 4) / (win * 4), mode="same")
        duck = 1.0 - 0.6 * env
        mix = music_gain * m * duck + self.fx + self.voice
        peak = np.max(np.abs(mix)) or 1.0
        if peak > 0.95:
            mix = mix * (0.95 / peak)
        return mix


def write_wav(path, mono):
    data = (np.clip(mono, -1, 1) * 32767).astype(np.int16)
    stereo = np.repeat(data[:, None], 2, axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(stereo.tobytes())


def resample(sig, sr_from):
    if sr_from == SR:
        return sig
    x_old = np.arange(len(sig)) / sr_from
    x_new = np.arange(int(len(sig) * SR / sr_from)) / SR
    return np.interp(x_new, x_old, sig)


def presenter_fx(sig, drive=2.2):
    """Voz de concurso: realce de presencia, compresión suave y normalización."""
    low = _lowpass_fast(sig, 0.08)
    bright = sig + 0.35 * (sig - low)  # más brillo y presencia
    # compresión suave
    comp = np.tanh(bright * drive) / np.tanh(drive)
    peak = np.max(np.abs(comp)) or 1.0
    return 0.85 * comp / peak


def _lowpass_fast(x, alpha):
    return _lowpass(x, alpha)

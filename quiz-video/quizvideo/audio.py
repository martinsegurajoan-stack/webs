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
    f = 1800 if high else 1250
    return 0.55 * _note(f, 0.07, "sine", decay=0.02, attack=0.001)


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
    return music_pop(duration, bpm, seed)


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

    def render(self, music_sig, music_gain=0.32, boosts=(), boost=1.45):
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

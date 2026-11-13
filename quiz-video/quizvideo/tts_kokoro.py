"""Voz Kokoro-82M (Apache-2.0), local y gratuita. Modelo y voces en modelos/ (ver instalar_voz.sh).

Para que suene más alegre y humana se exagera la melodía (entonación) con WORLD (pyworld):
las subidas y bajadas de tono se amplían y el tono general se sube un poco.
"""

import os

import numpy as np

from . import audio

MODELS = os.path.join(os.path.dirname(__file__), "..", "modelos")
PERFIL = os.path.join(os.path.dirname(__file__), "..", "assets", "voz_ref", "perfil.npz")

# Ajustes de la voz de la plantilla
EXPAND = 1.6        # 1.0 = entonación original; más = más expresiva
PITCH = 1.5         # semitonos de subida general
SHOUT_EXPAND = 2.0  # para el grito final
SHOUT_PITCH = 3.5


def _load_profile():
    if os.path.exists(PERFIL):
        p = np.load(PERFIL)
        return {k: p[k] for k in p.files}
    return None


def _expressive(x, sr, expand, shift, profile=None):
    """Exagera la entonación y, si hay perfil de referencia, adapta tono y timbre a esa voz."""
    import pyworld as pw

    f0, sp, ap = pw.wav2world(x, sr, frame_period=5.0)
    v = f0 > 0
    if v.sum() < 3:
        return x
    lf = np.log2(f0[v])
    m = np.median(lf)
    if profile is not None:
        target = np.log2(float(profile["f0_target"]))
        f0[v] = np.clip(2 ** (target + float(profile["expand"]) * expand * (lf - m) + shift / 12), 110, 600)
        n = sp.shape[1]
        src = np.clip(np.arange(n) / float(profile["warp"]), 0, n - 1)
        lo = np.floor(src).astype(int)
        hi = np.minimum(lo + 1, n - 1)
        fr = src - lo
        sp = (sp[:, lo] * (1 - fr) + sp[:, hi] * fr) * np.exp(profile["eq"])[None, :]
    else:
        f0[v] = 2 ** (m + expand * (lf - m) + shift / 12)
    return pw.synthesize(f0, np.ascontiguousarray(sp), ap, sr, frame_period=5.0)


class KokoroVoice:
    def __init__(self, voice_id="ef_dora", speed=1.0):
        from kokoro_onnx import Kokoro

        self.k = Kokoro(os.path.join(MODELS, "kokoro-q8.onnx"), os.path.join(MODELS, "voices-es.npz"))
        self.voice_id, self.speed = voice_id, speed
        self.name = f"kokoro:{voice_id}"
        self.cache = {}
        self.profile = _load_profile()
        if self.profile is not None:
            self.name += " (adaptada a la voz de referencia)"

    def say(self, text, shout=False):
        key = (text, shout)
        if key not in self.cache:
            from .tts import trim_silence

            sig, sr = self.k.create(text, voice=self.voice_id, speed=self.speed * (1.05 if shout else 1), lang="es")
            x = trim_silence(np.asarray(sig, dtype=np.float64))
            if self.profile is not None:
                # con perfil: entonación de la referencia; el grito sube 2 semitonos y algo más de energía
                x = _expressive(x, sr, 1.1 if shout else 1.0, 2.0 if shout else 0.0, self.profile)
            else:
                x = _expressive(x, sr, SHOUT_EXPAND if shout else EXPAND, SHOUT_PITCH if shout else PITCH)
            x = audio.presenter_fx(audio.resample(x, sr), drive=4.0 if shout else 2.2)
            self.cache[key] = x * (1.0 if shout else 0.72)
        sig = self.cache[key]
        return sig, len(sig) / audio.SR

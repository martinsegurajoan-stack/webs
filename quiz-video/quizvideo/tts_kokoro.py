"""Voz Kokoro-82M (Apache-2.0), local y gratuita. Modelo y voces en modelos/ (ver README)."""

import os

import numpy as np

from . import audio

MODELS = os.path.join(os.path.dirname(__file__), "..", "modelos")


class KokoroVoice:
    def __init__(self, voice_id="em_santa", speed=1.0, pitch=2.0):
        from kokoro_onnx import Kokoro

        self.k = Kokoro(os.path.join(MODELS, "kokoro-q8.onnx"), os.path.join(MODELS, "voices-es.npz"))
        self.voice_id, self.speed = voice_id, speed
        self.ratio = 2 ** (pitch / 12)  # subir el tono da una voz más alegre
        self.name = f"kokoro:{voice_id}"
        self.cache = {}

    def say(self, text):
        if text not in self.cache:
            from .tts import trim_silence

            # al subir el tono por remuestreo también se acelera; compensamos la velocidad
            sig, sr = self.k.create(text, voice=self.voice_id, speed=self.speed / self.ratio, lang="es")
            sig = audio.resample(trim_silence(np.asarray(sig, dtype=np.float64)), sr * self.ratio)
            sig = audio.presenter_fx(sig)
            self.cache[text] = sig
        sig = self.cache[text]
        return sig, len(sig) / audio.SR

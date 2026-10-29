"""Voz de ElevenLabs "QUIZ" (cuenta del usuario).

Los audios los genera Claude con el conector de ElevenLabs y los guarda en
assets/voz_eleven/cache/<clave>.mp3. Este módulo solo los lee; si falta alguno, lo apunta
para que `generar.py --frases-pendientes` diga cuáles hay que generar.
"""

import hashlib
import json
import os
import subprocess

import numpy as np

from . import audio

VOICE_ID = "7Jak8XD0XjFEAyIV8XkL"  # voz "QUIZ" de la cuenta de ElevenLabs del usuario
MODEL = "eleven_v4"
CACHE = os.path.join(os.path.dirname(__file__), "..", "assets", "voz_eleven", "cache")


def prompt_for(text, shout=False):
    """Texto que se envía a ElevenLabs (el grito lleva etiqueta de dirección)."""
    return f"[shouting excitedly] {text}" if shout else text


def key_for(text, shout=False):
    raw = f"{VOICE_ID}|{MODEL}|{prompt_for(text, shout)}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def path_for(text, shout=False):
    return os.path.join(CACHE, key_for(text, shout) + ".mp3")


class ElevenVoice:
    name = "elevenlabs:QUIZ"

    def __init__(self):
        self.missing = {}

    def say(self, text, shout=False):
        p = path_for(text, shout)
        if not os.path.exists(p):
            self.missing[os.path.basename(p)] = prompt_for(text, shout)
            return None, max(0.8, len(text) / 15.0)
        raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", p, "-ac", "1",
                                       "-ar", str(audio.SR), "-f", "s16le", "-"])
        from .tts import trim_silence

        sig = trim_silence(np.frombuffer(raw, np.int16).astype(np.float64) / 32768)
        peak = np.max(np.abs(sig)) or 1.0
        sig = sig / peak * (0.98 if shout else 0.75)
        return sig, len(sig) / audio.SR

    def pending_json(self):
        return json.dumps([{"archivo": f"assets/voz_eleven/cache/{k}", "texto": v}
                           for k, v in self.missing.items()], ensure_ascii=False, indent=2)

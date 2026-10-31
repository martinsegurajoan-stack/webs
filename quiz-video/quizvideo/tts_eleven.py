"""Voz de ElevenLabs "QUIZ" (cuenta del usuario).

Los audios los genera Claude con el conector de ElevenLabs y los guarda en
assets/voz_eleven/cache/<clave>.mp3. Este módulo solo los lee; si falta alguno, lo apunta
para que `generar.py --frases-pendientes` diga cuáles hay que generar (con el texto EXACTO
que hay que enviar a ElevenLabs, etiquetas de tono incluidas).
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


def cache_path(prompt):
    key = hashlib.sha1(f"{VOICE_ID}|{MODEL}|{prompt}".encode("utf-8")).hexdigest()[:16]
    return os.path.join(CACHE, key + ".mp3")


class ElevenVoice:
    name = "elevenlabs:QUIZ"

    def __init__(self):
        self.missing = {}
        self.style = ""                         # etiqueta de tono para todas las frases
        self.final_tag = "[shouting excitedly]"  # etiqueta de la frase final
        self.tempo = 1.15                       # acelera sin cambiar el tono

    def configure(self, style="", final_tag="[shouting excitedly]", tempo=1.15):
        self.style, self.final_tag, self.tempo = style, final_tag, tempo

    def prompt_for(self, text, shout=False):
        if shout:
            return f"{self.final_tag} {text}"
        return f"{self.style} {text}" if self.style else text

    def say(self, text, shout=False):
        prompt = self.prompt_for(text, shout)
        p = cache_path(prompt)
        if not os.path.exists(p):
            self.missing[os.path.basename(p)] = prompt
            return None, max(0.8, len(text) / 15.0)
        raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", p, "-af", f"atempo={self.tempo}",
                                       "-ac", "1", "-ar", str(audio.SR), "-f", "s16le", "-"])
        from .tts import trim_silence

        sig = trim_silence(np.frombuffer(raw, np.int16).astype(np.float64) / 32768)
        peak = np.max(np.abs(sig)) or 1.0
        sig = sig / peak * (0.98 if shout else 0.75)
        return sig, len(sig) / audio.SR

    def pending_json(self):
        return json.dumps([{"archivo": f"assets/voz_eleven/cache/{k}", "texto": v}
                           for k, v in self.missing.items()], ensure_ascii=False, indent=2)

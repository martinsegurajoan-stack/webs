"""Voz en off. Cada motor devuelve audio mono float (a 44.1 kHz) o None si no hay voz."""

import numpy as np

from . import audio


class SilentVoice:
    """Sin voz: solo estima cuánto tardaría en leerse el texto para el ritmo del vídeo."""

    name = "sin voz"

    def say(self, text):
        return None, max(0.6, len(text) / 17.0)


def get_voice(name: str, speed: float = 1.0):
    if name in ("ninguna", "none", ""):
        return SilentVoice()
    if name.startswith("kokoro"):
        from .tts_kokoro import KokoroVoice

        voice_id = name.split(":", 1)[1] if ":" in name else "em_santa"
        return KokoroVoice(voice_id, speed)
    raise SystemExit(f"Voz '{name}' desconocida. Usa 'ninguna' o 'kokoro:ef_dora'.")


def trim_silence(sig, thr=0.01):
    idx = np.where(np.abs(sig) > thr)[0]
    if len(idx) == 0:
        return sig
    a = max(0, idx[0] - int(0.02 * audio.SR))
    b = min(len(sig), idx[-1] + int(0.06 * audio.SR))
    return sig[a:b]

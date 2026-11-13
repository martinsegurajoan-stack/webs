#!/usr/bin/env python3
"""Crea un perfil para que la voz Kokoro se parezca a una grabación de referencia.

Mide en la referencia: tono medio, cuánto sube y baja la entonación y el timbre (envolvente
espectral media). Luego calcula los ajustes para la voz base. No clona la voz: la aproxima.

Uso: python3 crear_perfil_voz.py assets/voz_ref/referencia.wav [--voz ef_dora]
"""

import argparse
import os
import subprocess
import sys

import numpy as np
import pyworld as pw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SR = 24000
FRASES = [
    "¡Hola! ¿Qué tal estás? Hoy vamos a jugar a un quiz muy divertido.",
    "¿En qué ciudad se encuentra la Casa Blanca? ¡Piénsalo bien!",
    "¡Pregunta dos! ¿Cuántas comunidades autónomas tiene España?",
    "¡Muy bien! La respuesta correcta era la B. ¡Sígueme para más!",
]


def load(path):
    raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", str(SR),
                                   "-f", "s16le", "-"])
    return np.frombuffer(raw, np.int16).astype(np.float64) / 32768


def analyze(x):
    f0, sp, ap = pw.wav2world(x, SR, frame_period=5.0)
    v = f0 > 0
    lf = np.log2(f0[v])
    env = np.log(sp[v] + 1e-12)
    # pondera por energía para que pesen los tramos con voz clara
    e = np.exp(env).sum(1)
    env_mean = (env * (e / e.sum())[:, None]).sum(0)
    return 2 ** np.median(lf), 12 * np.std(lf - np.median(lf)), env_mean


def warp_env(env, alpha):
    n = len(env)
    src = np.clip(np.arange(n) / alpha, 0, n - 1)
    return np.interp(src, np.arange(n), env)


def smooth(v, k=15):
    return np.convolve(np.pad(v, k, mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), mode="same")[k:-k]


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("referencia")
    ap_.add_argument("--voz", default="ef_dora")
    ap_.add_argument("--salida", default="assets/voz_ref/perfil.npz")
    a = ap_.parse_args()

    from kokoro_onnx import Kokoro

    k = Kokoro("modelos/kokoro-q8.onnx", "modelos/voices-es.npz")
    base = np.concatenate([np.asarray(k.create(f, voice=a.voz, speed=1.1, lang="es")[0], np.float64)
                           for f in FRASES])
    ref = load(a.referencia)
    f0_ref, var_ref, env_ref = analyze(ref)
    f0_b, var_b, env_b = analyze(base)

    # desplazamiento de formantes que mejor iguala el timbre medio
    best = min(np.arange(0.94, 1.151, 0.01),
               key=lambda al: np.mean((smooth(warp_env(env_b, al)) - smooth(env_ref))[20:400] ** 2))
    # ecualización residual suave (limitada a ±6 dB)
    diff = smooth(env_ref) - smooth(warp_env(env_b, best))
    diff -= np.median(diff)
    eq = np.clip(smooth(diff, 25), -0.69, 0.69)  # ln(2) ~ 6 dB en potencia

    perfil = dict(f0_target=f0_ref, f0_base=f0_b, expand=float(np.clip(var_ref / var_b, 1.0, 2.4)),
                  warp=float(best), eq=eq)
    np.savez(a.salida, **perfil)
    print(f"Referencia: tono {f0_ref:.0f} Hz, entonación {var_ref:.1f} st")
    print(f"Voz base {a.voz}: tono {f0_b:.0f} Hz, entonación {var_b:.1f} st")
    print(f"Ajustes: tono x{f0_ref / f0_b:.2f} ({12 * np.log2(f0_ref / f0_b):+.1f} st), "
          f"expresividad x{perfil['expand']:.2f}, formantes x{best:.2f}")
    print(f"Guardado en {a.salida}")


if __name__ == "__main__":
    main()

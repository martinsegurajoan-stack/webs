#!/usr/bin/env python3
"""Voz GRATIS y local: Piper TTS (voz es_ES «davefx», castellano) frase a frase, con ritmo propio por frase
y un toque de estudio (algo más grave, cuerpo, presencia y compresión). Sin créditos ni APIs.

  pip install piper-tts
  modelo: https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-es_ES-davefx-medium.tar.bz2
          (descomprimir en /root/tts/ o cambiar MODELO)
  python3 voz_libre.py   → voz/lN.wav (luego: python3 montar_voz.py)
"""
import os, subprocess, wave
from piper import PiperVoice, SynthesisConfig

BASE = os.path.dirname(os.path.abspath(__file__))
MODELO = os.environ.get("PIPER_MODELO", "/root/tts/vits-piper-es_ES-davefx-medium/es_ES-davefx-medium.onnx")
# (texto que se LEE, length_scale): >1 más pausado (suspense), <1 más vivo (sorpresa). El texto de pantalla sale de guion.txt
LECTURA = [
    ("¿Qué pasaría si no te cortas el pelo en diez años?", 1.06),
    ("Empiezas con un pelo.", 1.08),
    ("Bueno... con cien mil.", 1.14),
    ("Y cada uno crece algo más de un centímetro al mes.", 1.05),
    ("Al primer año, ya tienes quince centímetros.", 1.02),
    ("El flequillo te tapa los ojos.", 1.06),
    ("¡A los tres años, cuarenta y cinco centímetros!", 0.98),
    ("Se te engancha en las puertas.", 1.04),
    ("Y acaba... dentro de la sopa.", 1.10),
    ("A los cinco años, ya te llega casi a la cintura.", 1.04),
    ("Y aquí viene, lo que casi nadie sabe.", 1.18),
    ("Tu pelo, no crece para siempre.", 1.16),
    ("Cada pelo vive solo de dos a siete años.", 1.08),
    ("Después se cae... y nace otro nuevo.", 1.10),
    ("Así que a los diez años, tu melena se queda en un metro, como mucho.", 1.05),
    ("Salvo que tengas unos genes únicos...", 1.14),
    ("como Shie Chiupin, ¡que lo tiene de más de cinco metros!", 1.00),
    ("Y por el camino, habrás perdido unos trescientos mil pelos.", 1.06),
    ("Porque todo empezó... con un solo pelo.", 1.16),
]
RITMO = 1.12   # ritmo general: un poco más pausado que el de serie
ESTUDIO = ("rubberband=pitch=0.93:formant=preserved:pitchq=quality,highpass=f=70,"
           "equalizer=f=120:t=q:w=1.0:g=2.5,equalizer=f=420:t=q:w=1.2:g=-2,equalizer=f=3500:t=q:w=1.4:g=2,"
           "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2")

voz = PiperVoice.load(MODELO, config_path=MODELO + ".json")
os.makedirs(os.path.join(BASE, "voz"), exist_ok=True)
for i, (txt, ls) in enumerate(LECTURA, 1):
    crudo = os.path.join(BASE, "voz", f"l{i}_crudo.wav")
    with wave.open(crudo, "wb") as w:
        voz.synthesize_wav(txt, w, syn_config=SynthesisConfig(length_scale=ls * RITMO, noise_scale=0.72, noise_w_scale=0.9))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", crudo, "-af", ESTUDIO, "-ar", "44100", "-ac", "1",
                    os.path.join(BASE, "voz", f"l{i}.wav")], check=True)
    os.remove(crudo)
    print(i, txt)

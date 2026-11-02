"""Parte la locución completa de ElevenLabs (voz_el/narrador.wav) en voz/lN.wav, una por línea de guion.txt.
Elige los cortes entre silencios para que el tiempo HABLADO de cada trozo encaje con su número de letras."""
import subprocess, re, soundfile as sf
lines = open('guion.txt').read().splitlines()
out = subprocess.run(['ffmpeg', '-i', 'voz_el/narrador.wav', '-af', 'silencedetect=noise=-38dB:d=0.18', '-f', 'null', '-'], capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r'silence_start: ([0-9.]+)', out)]; en = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', out)]
x, sr = sf.read('voz_el/narrador.wav'); T = len(x) / sr
gaps = [(a, b) for a, b in zip(st, en) if a > 0.2 and b < T - 0.3]
N = len(lines)
import json, os
FORZAR = json.load(open('voz_el/cortes.json')) if os.path.exists('voz_el/cortes.json') else {}   # {"línea": segundo donde acaba}
def _hablado(l):   # las cifras se dicen con muchas más letras de las que ocupan («29» = veintinueve)
    l = re.sub(r'\b(19|20)\d\d\b', 'dosmilveintitres', l)
    l = re.sub(r'\d+', lambda m: 'x' * (5 * len(m.group())), l)
    return l
ch = [len(re.sub(r'[^\wáéíóúñü]', '', _hablado(l))) for l in lines]
cuts = [0.0] + [(a + b) / 2 for a, b in gaps] + [T]
glen = [0] + [b - a for a, b in gaps] + [0]
K = len(cuts)
def habla(p, j):   # tiempo hablado entre el corte p y el j (sin silencios internos ni medias pausas de los bordes)
    return (cuts[j] - cuts[p]) - sum(glen[p + 1:j]) - glen[p] / 2 - glen[j] / 2
rate = sum(habla(k, k + 1) for k in range(K - 1)) / sum(ch)
INF = 1e18
dp = [[INF] * K for _ in range(N + 1)]; bk = [[-1] * K for _ in range(N + 1)]; dp[0][0] = 0
for i in range(1, N + 1):
    for j in range(1, K):
        if (i == N) != (j == K - 1): continue
        for p in range(j):
            if dp[i - 1][p] >= INF: continue
            e = rate * ch[i - 1]
            c = dp[i - 1][p] + ((habla(p, j) - e) / e) ** 2 - 1.5 * glen[j]
            if str(i) in FORZAR and abs(cuts[j] - FORZAR[str(i)]) > 0.3: c += 1e6   # corte fijado a mano
            if c < dp[i][j]: dp[i][j] = c; bk[i][j] = p
j = K - 1; seq = []
for i in range(N, 0, -1):
    p = bk[i][j]; seq.append((cuts[p], cuts[j])); j = p
for i, (a, b) in enumerate(seq[::-1], 1):
    print(i, f"{a:6.2f}-{b:6.2f}", lines[i - 1][:55])
    sf.write(f'voz/l{i}.wav', x[int(a * sr):int(b * sr)], sr)

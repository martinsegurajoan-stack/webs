"""Acorta los silencios internos largos de cada voz/lN.wav (> 0,3 s → 0,22 s) para que el vídeo no pase de 75 s."""
import glob, numpy as np, soundfile as sf
for f in sorted(glob.glob('voz/l*.wav')):
    x, sr = sf.read(f)
    if x.ndim > 1: x = x.mean(1)
    win = int(0.02 * sr); e = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, 'same'))
    quiet = e < 10 ** (-38 / 20)
    out, i, n = [], 0, len(x)
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]: j += 1
            seg = x[i:j]
            if (j - i) / sr > 0.3 and i > 0 and j < n:
                k = int(0.11 * sr); seg = np.concatenate([x[i:i + k], x[j - k:j]])
            out.append(seg); i = j
        else:
            j = i
            while j < n and not quiet[j]: j += 1
            out.append(x[i:j]); i = j
    y = np.concatenate(out); sf.write(f, y, sr); print(f, round(n / sr, 2), '→', round(len(y) / sr, 2))

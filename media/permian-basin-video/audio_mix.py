import numpy as np, soundfile as sf, json
from scipy.signal import resample_poly, butter, sosfilt

SR = 44100
TOTAL = 84.75
N = int(TOTAL * SR)
SCENE_STARTS = [0.00, 9.09, 19.16, 30.75, 42.13, 53.06, 65.29, 74.64]
VO_OFFSET = 0.65

rng = np.random.default_rng(7)
t = np.arange(N) / SR

# ---------------- voiceover track ----------------
vo = np.zeros(N)
meta = json.load(open('vo_meta.json'))
for m in meta:
    data, sr0 = sf.read(m['file'])
    if data.ndim > 1: data = data.mean(axis=1)
    data = resample_poly(data, SR, sr0)
    start = int((SCENE_STARTS[m['scene'] - 1] + VO_OFFSET) * SR)
    end = min(start + len(data), N)
    vo[start:end] += data[:end - start]
peak = np.abs(vo).max()
vo *= 0.82 / peak

# ---------------- ambient bed ----------------
# chord per scene (frequencies in Hz)
CHORDS = [
    [73.42, 110.00, 146.83, 174.61, 220.00],   # Dm
    [116.54, 146.83, 174.61, 233.08],          # Bb
    [73.42, 110.00, 146.83, 174.61],           # Dm low
    [87.31, 130.81, 174.61, 220.00],           # F
    [110.00, 164.81, 220.00, 261.63],          # Am
    [116.54, 174.61, 233.08, 293.66],          # Bb add9-ish
    [130.81, 196.00, 261.63, 329.63],          # C
    [73.42, 110.00, 146.83, 185.00, 220.00],   # D major (resolution)
]
bed_L = np.zeros(N); bed_R = np.zeros(N)
bounds = SCENE_STARTS + [TOTAL]
for i, chord in enumerate(CHORDS):
    s, e = bounds[i], bounds[i + 1]
    i0, i1 = int(s * SR), int(e * SR)
    # chord envelope with 2s attack / 2.5s release crossing boundaries
    a0 = max(0, i0 - int(1.2 * SR)); a1 = min(N, i1 + int(1.4 * SR))
    seg_n = a1 - a0
    env = np.ones(seg_n)
    atk = int(2.0 * SR); rel = int(2.5 * SR)
    env[:atk] = np.linspace(0, 1, atk) ** 2
    env[-rel:] *= np.linspace(1, 0, rel) ** 1.5
    tt = t[a0:a1]
    for j, f in enumerate(chord):
        amp = 0.16 / len(chord) * (1.25 if j == 0 else 1.0)
        trem = 1 + 0.22 * np.sin(2 * np.pi * (0.11 + 0.031 * j) * tt + j * 1.7)
        ph = rng.uniform(0, 6.28)
        wl = np.sin(2 * np.pi * f * 0.9985 * tt + ph)
        wr = np.sin(2 * np.pi * f * 1.0015 * tt + ph + 0.8)
        # soften with a 2nd harmonic whisper
        wl += 0.25 * np.sin(2 * np.pi * 2 * f * 0.999 * tt + ph * 2)
        wr += 0.25 * np.sin(2 * np.pi * 2 * f * 1.001 * tt + ph * 2 + 0.5)
        bed_L[a0:a1] += amp * trem * env * wl
        bed_R[a0:a1] += amp * trem * env * wr

# soft noise air (very quiet, bandpassed)
noise = rng.standard_normal(N) * 0.003
sos = butter(2, [400, 1800], btype='band', fs=SR, output='sos')
air = sosfilt(sos, noise)
swell = np.zeros(N)
for s in SCENE_STARTS[1:]:
    i0 = int((s - 1.4) * SR); i1 = int((s + 0.4) * SR)
    if i0 < 0: continue
    n = i1 - i0
    swell[i0:i1] = np.maximum(swell[i0:i1], np.hanning(n * 2)[:n] * 1.0)
air *= (0.35 + 2.2 * swell)
bed_L += air; bed_R += air

# sub thump at scene starts
for s in SCENE_STARTS:
    i0 = int(s * SR); n = int(0.55 * SR)
    if i0 + n > N: n = N - i0
    tt = np.arange(n) / SR
    th = np.sin(2 * np.pi * (52 - 14 * tt) * tt) * np.exp(-tt * 7.5) * 0.11
    bed_L[i0:i0 + n] += th; bed_R[i0:i0 + n] += th

# ---------------- duck bed under voice ----------------
env_v = np.abs(vo)
k = int(0.18 * SR)
kernel = np.ones(k) / k
env_s = np.convolve(env_v, kernel, mode='same')
duck = 1.0 - 0.5 * np.clip(env_s / 0.06, 0, 1)
bed_L *= duck; bed_R *= duck

# master
L = bed_L + vo
R = bed_R + vo
mx = max(np.abs(L).max(), np.abs(R).max())
if mx > 0.97:
    L *= 0.97 / mx; R *= 0.97 / mx
# gentle fade in/out on the master
fi = int(0.4 * SR); fo = int(1.6 * SR)
for ch in (L, R):
    ch[:fi] *= np.linspace(0, 1, fi)
    ch[-fo:] *= np.linspace(1, 0, fo) ** 1.2

sf.write('mix.wav', np.stack([L, R], axis=1), SR)
print('mix.wav written', N / SR, 's')

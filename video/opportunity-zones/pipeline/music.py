#!/usr/bin/env python3
"""Subtle cinematic corporate music bed — layered soft pads, slow chord
progression, gentle sub root and light shimmer. Rendered to stereo 44.1k WAV."""
import numpy as np, wave, os

SR = 44100
DUR = 108.0
N = int(SR * DUR)
t = np.arange(N) / SR

# chord progression (frequencies, Hz) — Dm9 / Bbmaj7 / Fmaj9 / Cadd9 feel
def notes(*ns): return [440.0 * 2 ** ((n - 69) / 12) for n in ns]
CHORDS = [
    notes(50, 57, 62, 65, 69),   # D2 A2 D3 F3 A3  (Dm)
    notes(46, 58, 62, 65, 70),   # Bb1 Bb2 D3 F3 Bb3 (Bbmaj)
    notes(41, 57, 60, 65, 69),   # F2 A2 C3 F3 A3   (F)
    notes(48, 55, 62, 64, 67),   # C2 G2 D3 E3 G3   (Cadd9)
]
CHORD_LEN = 9.0  # seconds per chord

def chord_at(i):
    return CHORDS[i % len(CHORDS)]

mix = np.zeros(N)

# pads: for each chord segment, synth detuned partials with slow attack/release
seg = int(CHORD_LEN * SR)
n_seg = int(np.ceil(DUR / CHORD_LEN))
rng = np.random.RandomState(7)
for s in range(n_seg):
    i0 = s * seg
    i1 = min(N, i0 + seg + int(2.5 * SR))  # overlap tails for legato
    seg_n = i1 - i0
    tt = np.arange(seg_n) / SR
    env = np.minimum(tt / 3.0, 1.0) * np.minimum((seg_n / SR - tt) / 3.0, 1.0)
    env = np.clip(env, 0, 1) ** 1.4
    segmix = np.zeros(seg_n)
    for f in chord_at(s):
        for det, amp in ((0.9985, .5), (1.0, 1.0), (1.0018, .5)):
            ph = rng.uniform(0, 2 * np.pi)
            vib = 1 + 0.0006 * np.sin(2 * np.pi * 0.13 * tt + ph)
            w = np.sin(2 * np.pi * f * det * vib * tt + ph)
            # soften with a second harmonic whisper
            w += 0.18 * np.sin(2 * np.pi * f * det * 2 * tt + ph * 1.7)
            segmix += amp * w / len(chord_at(s))
    mix[i0:i1] += segmix * env * 0.16

# gentle sub root (sine, one octave below chord root)
for s in range(n_seg):
    i0 = s * seg
    i1 = min(N, i0 + seg + int(1.5 * SR))
    seg_n = i1 - i0
    tt = np.arange(seg_n) / SR
    env = np.minimum(tt / 2.0, 1.0) * np.minimum((seg_n / SR - tt) / 2.5, 1.0)
    env = np.clip(env, 0, 1)
    root = chord_at(s)[0] / 2
    mix[i0:i1] += 0.10 * np.sin(2 * np.pi * root * tt) * env

# light shimmer: slow, sparse high sine blips (deterministic)
for k in range(60):
    at = 1.5 + k * 1.77
    if at > DUR - 4: break
    f = [880, 1174.7, 987.8, 1318.5][k % 4]
    i0 = int(at * SR); ln = int(2.8 * SR); i1 = min(N, i0 + ln)
    tt = np.arange(i1 - i0) / SR
    env = np.exp(-tt * 1.8) * np.minimum(tt / 0.4, 1)
    mix[i0:i1] += 0.014 * np.sin(2 * np.pi * f * tt) * env

# global swell in/out
master = np.minimum(t / 6.0, 1.0) * np.clip((DUR - t) / 7.0, 0, 1.0)
mix *= master

# gentle lowpass (spectral) to keep it dark/warm
F = np.fft.rfft(mix)
freqs = np.fft.rfftfreq(len(mix), 1 / SR)
H = 1.0 / (1.0 + (freqs / 2200.0) ** 2)
out = np.fft.irfft(F * H, n=len(mix))

# stereo width via short haas offset
off = int(0.011 * SR)
L = out
R = np.concatenate([np.zeros(off), out[:-off]]) * 0.96 + out * 0.04

peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak * 0.72, R / peak * 0.72
stereo = np.stack([L, R], axis=1)
pcm = (stereo * 32767).astype(np.int16)

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio", "music.wav")
with wave.open(out_path, "w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("music written:", out_path, DUR, "s")

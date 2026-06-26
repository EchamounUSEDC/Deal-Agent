#!/usr/bin/env python3
"""Synthesize a simple Wild-West background loop (offline, no downloads).

Karplus-Strong plucked strings (banjo/guitar timbre) play a I-IV-V-I progression
in G major with a banjo roll + a root bass. Written to music.wav, long enough to
sit under the whole video.
"""
import os, numpy as np, wave
HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
TEMPO = 100
BEAT = 60.0 / TEMPO
TOTAL = 90.0      # seconds

def pluck(freq, dur, decay=0.995, gain=1.0):
    N = max(2, int(SR / freq))
    buf = np.random.uniform(-1, 1, N)
    total = int(SR * dur)
    out = np.empty(total, dtype=np.float64)
    idx = 0
    for i in range(total):
        out[i] = buf[idx]
        nxt = (idx + 1) % N
        buf[idx] = decay * 0.5 * (buf[idx] + buf[nxt])
        idx = nxt
    # amplitude envelope (quick attack, gentle decay)
    env = np.exp(-np.linspace(0, 3.2, total))
    return out * env * gain

NOTE = {'G2':98.0,'D3':146.83,'G3':196.0,'B3':246.94,'C4':261.63,'D4':293.66,
        'E4':329.63,'G4':392.0,'A4':440.0,'B4':493.88,'C5':523.25,'D5':587.33,
        'C3':130.81,'E3':164.81,'F#4':369.99,'A3':220.0}

# one bar per chord: (bass root, [roll notes])
BARS = [
    ('G2', ['G3','B3','D4','G4','D4','B3','G3','B3']),
    ('C3', ['C4','E4','G4','C5','G4','E4','C4','E4']),
    ('D3', ['D4','F#4','A4','D5','A4','F#4','D4','A3']),
    ('G2', ['G3','B3','D4','G4','B4','G4','D4','B3']),
]

def build():
    bar_dur = 4 * BEAT
    loop_len = int(SR * bar_dur * len(BARS))
    loop = np.zeros(loop_len)
    eighth = BEAT / 2
    for bi, (bass, roll) in enumerate(BARS):
        bar0 = int(bi * bar_dur * SR)
        # bass on beats 1 and 3
        for beat in (0, 2):
            s = bass; n = pluck(NOTE[s], BEAT*2*0.9, decay=0.996, gain=0.6)
            p = bar0 + int(beat * BEAT * SR)
            loop[p:p+len(n)] += n[:max(0, loop_len-p)] if p+len(n) > loop_len else n
        # banjo roll: eighth notes
        for j, nm in enumerate(roll):
            n = pluck(NOTE[nm], eighth*1.6, decay=0.994, gain=0.4)
            p = bar0 + int(j * eighth * SR)
            end = min(loop_len, p+len(n))
            loop[p:end] += n[:end-p]
    # tile to TOTAL
    reps = int(np.ceil(TOTAL * SR / loop_len))
    full = np.tile(loop, reps)[:int(TOTAL*SR)]
    # gentle low-pass-ish smoothing + normalize
    full = np.convolve(full, np.ones(3)/3, mode='same')
    full /= (np.max(np.abs(full)) + 1e-6)
    full *= 0.85
    stereo = np.stack([full, full], axis=1)
    data = (stereo * 32767).astype('<i2')
    out = os.path.join(HERE, 'music.wav')
    with wave.open(out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(data.tobytes())
    print('wrote', out, round(len(full)/SR,1), 's')

if __name__ == '__main__':
    build()

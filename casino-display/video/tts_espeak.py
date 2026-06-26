#!/usr/bin/env python3
"""Offline TTS using espeak-ng via ctypes (no network/models needed).

Usage: python3 tts_espeak.py "text to speak" out.wav [pitch] [rate] [voice]
Produces a 16-bit mono WAV. espeak is robotic; we tune pitch/rate/range to be
friendlier, and callers can post-process (e.g. slight pitch shift) with ffmpeg.
"""
import sys, os, ctypes, wave, struct

import espeakng_loader

LIB = espeakng_loader.get_library_path()
DATA = espeakng_loader.get_data_path()
# espeak_Initialize wants the directory CONTAINING 'espeak-ng-data'
if os.path.basename(DATA.rstrip('/')) == 'espeak-ng-data':
    DATA_PARENT = os.path.dirname(DATA.rstrip('/'))
else:
    DATA_PARENT = DATA

AUDIO_OUTPUT_RETRIEVAL = 1
espeakCHARS_UTF8 = 1
espeakRATE, espeakVOLUME, espeakPITCH, espeakRANGE = 1, 2, 3, 4

e = ctypes.CDLL(LIB)
e.espeak_Initialize.restype = ctypes.c_int
e.espeak_Initialize.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]

SYNTH_CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_short),
                            ctypes.c_int, ctypes.c_void_p)
e.espeak_SetSynthCallback.argtypes = [SYNTH_CB]
e.espeak_SetVoiceByName.argtypes = [ctypes.c_char_p]
e.espeak_SetParameter.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
e.espeak_Synth.restype = ctypes.c_int
e.espeak_Synth.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint,
                           ctypes.c_int, ctypes.c_uint, ctypes.c_uint,
                           ctypes.POINTER(ctypes.c_uint), ctypes.c_void_p]


def synth(text, out_wav, pitch=65, rate=160, voice='en-us+m3', rng=70):
    rate_hz = e.espeak_Initialize(AUDIO_OUTPUT_RETRIEVAL, 0, DATA_PARENT.encode(), 0)
    if rate_hz < 0:
        raise RuntimeError('espeak_Initialize failed')

    samples = bytearray()

    @SYNTH_CB
    def cb(wav, numsamples, events):
        if numsamples > 0:
            samples.extend(ctypes.string_at(wav, numsamples * 2))
        return 0

    e.espeak_SetSynthCallback(cb)
    if e.espeak_SetVoiceByName(voice.encode()) != 0:
        e.espeak_SetVoiceByName(b'en-us')
    e.espeak_SetParameter(espeakPITCH, int(pitch), 0)
    e.espeak_SetParameter(espeakRATE, int(rate), 0)
    e.espeak_SetParameter(espeakRANGE, int(rng), 0)
    e.espeak_SetParameter(espeakVOLUME, 200, 0)

    b = text.encode('utf-8')
    e.espeak_Synth(b, len(b) + 1, 0, 0, 0, espeakCHARS_UTF8, None, None)
    e.espeak_Synchronize()

    with wave.open(out_wav, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate_hz)
        w.writeframes(bytes(samples))
    return rate_hz, len(samples) // 2 / rate_hz


if __name__ == '__main__':
    text = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else 'out.wav'
    pitch = int(sys.argv[3]) if len(sys.argv) > 3 else 65
    rate = int(sys.argv[4]) if len(sys.argv) > 4 else 160
    voice = sys.argv[5] if len(sys.argv) > 5 else 'en-us+m3'
    sr, dur = synth(text, out, pitch, rate, voice)
    print(f'wrote {out}  sr={sr}  dur={dur:.2f}s')

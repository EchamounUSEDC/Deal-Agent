import json, soundfile as sf
from kokoro_onnx import Kokoro

LINES = [
    "Beneath West Texas and southeastern New Mexico lies the most productive oil field on earth: the Permian Basin.",
    "Its story began nearly three hundred million years ago, when an ancient inland sea laid down thick layers of organic-rich sediment.",
    "Early failures earned it the name petroleum graveyard. Then, in May of nineteen twenty-three, the Santa Rita Number One gusher changed everything.",
    "Boomtowns like Midland and Odessa rose from the plains, while royalties from university lands built one of the largest endowments in America.",
    "Conventional output peaked above two million barrels a day in the early seventies, then declined for three decades as the easy oil ran dry.",
    "The shale revolution rewrote the story. Horizontal drilling and hydraulic fracturing unlocked stacked pay zones like the Wolfcamp, Spraberry, and Bone Spring.",
    "Today, the Permian delivers roughly six and a half million barrels of crude every day, nearly half of all American production.",
    "A century after the first gusher, the basin once written off as a graveyard remains the heartbeat of American energy.",
]

k = Kokoro('kokoro-v1.0.onnx', 'voices-v1.0.bin')
meta = []
for i, line in enumerate(LINES, 1):
    samples, sr = k.create(line, voice='am_michael', speed=0.96)
    fn = f'vo_{i:02d}.wav'
    sf.write(fn, samples, sr)
    dur = len(samples) / sr
    meta.append({'scene': i, 'file': fn, 'dur': round(dur, 3), 'text': line})
    print(f'scene {i}: {dur:.2f}s')

json.dump(meta, open('vo_meta.json', 'w'), indent=1)
total = sum(m['dur'] for m in meta)
print('total narration:', round(total, 1), 's')

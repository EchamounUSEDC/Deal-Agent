#!/usr/bin/env bash
# Turn an N-second clip into an (N-1)-second SEAMLESS loop by crossfading the
# last 1s into the first 1s. Works great for the falling-stream (static camera,
# chaotic particles → the 1s dissolve is invisible, and the loop point matches).
set -e
IN="${1:-wylde_4k_raw.mp4}"
OUT="${2:-wylde_4k_loop.mp4}"
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")

# probe duration
L=$("$FF" -v error -show_entries format=duration -of csv=p=0 -i "$IN" 2>/dev/null || echo 11)
L=${L%.*}
D=1                    # crossfade overlap (seconds)
MID_END=$((L-1))       # end of middle section = L - d

"$FF" -y -hide_banner -loglevel error -i "$IN" -filter_complex "\
[0:v]trim=0:${D},setpts=PTS-STARTPTS[begin];\
[0:v]trim=${MID_END}:${L},setpts=PTS-STARTPTS[end];\
[end][begin]blend=all_expr='A*(1-(T/${D}))+B*(T/${D})'[xf];\
[0:v]trim=${D}:${MID_END},setpts=PTS-STARTPTS[mid];\
[xf][mid]concat=n=2:v=1[v]" \
  -map "[v]" -r 30 \
  -c:v libx264 -profile:v high -level 5.1 -pix_fmt yuv420p -crf 18 -preset medium \
  -movflags +faststart -an "$OUT"

echo "loop -> $OUT"
"$FF" -hide_banner -i "$OUT" 2>&1 | grep -E 'Duration|Stream'

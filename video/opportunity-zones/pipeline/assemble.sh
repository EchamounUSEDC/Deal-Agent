#!/bin/bash
# Final assembly: scene encodes -> xfade chain -> audio mix -> deliverable MP4
set -e
cd "$(dirname "$0")"
mkdir -p out

V="-c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -r 30"

echo "== graphics scenes from frames =="
ffmpeg -y -v error -framerate 30 -i frames/scene1/f%05d.png  $V out/sc1.mp4
ffmpeg -y -v error -framerate 30 -i frames/scene3/f%05d.png  $V out/sc3.mp4
ffmpeg -y -v error -framerate 30 -i frames/scene4/f%05d.png  $V out/sc4.mp4
ffmpeg -y -v error -framerate 30 -i frames/endcard/f%05d.png $V out/sc_end.mp4

echo "== footage + overlays =="
ffmpeg -y -v error -i out/seg_fw_a.mp4  -framerate 30 -i frames/ov2a/f%05d.png -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p" $V out/sc2a.mp4
ffmpeg -y -v error -i out/seg_rig_b.mp4 -framerate 30 -i frames/ov2b/f%05d.png -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p" $V out/sc2b.mp4
ffmpeg -y -v error -t 8.0 -i out/seg_rig_c.mp4 -framerate 30 -i frames/ov5a/f%05d.png -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p" $V out/sc5a.mp4
ffmpeg -y -v error -i out/seg_fw_d.mp4  -framerate 30 -i frames/ov5b/f%05d.png -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p" $V out/sc5b.mp4

echo "== xfade chain =="
# lens: 16.0 10.5 9.0 29.0 24.0 8.0 6.0 7.5 ; fade 0.5
# offsets: 15.5 25.5 34.0 62.5 86.0 93.5 99.0 ; total 106.5
ffmpeg -y -v error \
 -i out/sc1.mp4 -i out/sc2a.mp4 -i out/sc2b.mp4 -i out/sc3.mp4 \
 -i out/sc4.mp4 -i out/sc5a.mp4 -i out/sc5b.mp4 -i out/sc_end.mp4 \
 -filter_complex "\
 [0:v][1:v]xfade=transition=fade:duration=0.5:offset=15.5[v1];\
 [v1][2:v]xfade=transition=fade:duration=0.5:offset=25.5[v2];\
 [v2][3:v]xfade=transition=fade:duration=0.5:offset=34.0[v3];\
 [v3][4:v]xfade=transition=fade:duration=0.5:offset=62.5[v4];\
 [v4][5:v]xfade=transition=fade:duration=0.5:offset=86.0[v5];\
 [v5][6:v]xfade=transition=fade:duration=0.5:offset=93.5[v6];\
 [v6][7:v]xfade=transition=fade:duration=0.5:offset=99.0,format=yuv420p[vout]" \
 -map "[vout]" $V out/video_only.mp4

echo "== audio mix =="
# VO: tempo 1.06, gentle EQ + compression; placed at absolute times (ms)
# VO1@0.8 VO2a@16.2 VO2b@25.9 VO3@34.6 VO4@63.1 VO5@86.5
VOF="atempo=1.06,highpass=f=85,equalizer=f=240:t=q:w=1.2:g=-1.5,equalizer=f=3200:t=q:w=1.4:g=1.2,acompressor=threshold=-19dB:ratio=2.6:attack=8:release=140:makeup=3dB,aformat=sample_rates=48000:channel_layouts=stereo"
ffmpeg -y -v error \
 -i vo/s1_opening.wav -i vo/s2a_usedc_hq.wav -i vo/s2b_usedc_ops.wav \
 -i vo/s3_timeline.wav -i vo/s4_tax.wav -i vo/s5_closing.wav \
 -i audio/music.wav \
 -filter_complex "\
 [0:a]$VOF,adelay=800|800[a0];\
 [1:a]$VOF,adelay=16200|16200[a1];\
 [2:a]$VOF,adelay=25900|25900[a2];\
 [3:a]$VOF,adelay=34600|34600[a3];\
 [4:a]$VOF,adelay=63100|63100[a4];\
 [5:a]$VOF,adelay=86500|86500[a5];\
 [a0][a1][a2][a3][a4][a5]amix=inputs=6:normalize=0[vo];\
 [6:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.34,atrim=0:106.5,afade=t=out:st=101.5:d=5[mus];\
 [vo][mus]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=9[aout]" \
 -map "[aout]" -ar 48000 out/audio_mix.wav

echo "== mux =="
ffmpeg -y -v error -i out/video_only.mp4 -i out/audio_mix.wav \
 -c:v copy -c:a aac -b:a 192k -movflags +faststart -shortest \
 out/USEDC_Opportunity_Zones_Explainer_1080p.mp4
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 out/USEDC_Opportunity_Zones_Explainer_1080p.mp4
echo ASSEMBLY_DONE

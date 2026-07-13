#!/bin/bash
set -e
cd "$(dirname "$0")"
UP=/root/.claude/uploads/36108824-8941-5da2-af75-c438086bdb28
FW="$UP/cc3476fb-ft_worth_texas_v1_1080p.mp4"
RIG="$UP/45bf16a0-u.s._energy_rig_in_pecos_tx_v1_1080p.mp4"
GRADE="eq=contrast=1.07:saturation=0.9:brightness=-0.02,colorbalance=rs=-.04:bs=.06:rm=.02:bm=-.02:rh=.05:bh=-.06,unsharp=5:5:0.35,vignette=PI/4.6"
GRADE_DARK="eq=contrast=1.09:saturation=0.82:brightness=-0.05,colorbalance=rs=-.05:bs=.08:rh=.04:bh=-.06,unsharp=5:5:0.3,vignette=PI/4.2"

zoom_seg () { # src start dur zexpr grade out
  ffmpeg -y -v error -ss "$2" -t "$3" -i "$1" -an -filter_complex \
   "[0:v]fps=30,scale=3840:2160:flags=lanczos,zoompan=z='$4':d=1:x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':s=1920x1080:fps=30,$5,format=yuv420p" \
   -c:v libx264 -preset medium -crf 16 "$6"
}

# S2a: Ft Worth 0-10.5, zoom in 1.0 -> 1.07 (315 frames)
zoom_seg "$FW" 0 10.5 "1+0.07*on/315" "$GRADE" out/seg_fw_a.mp4
# S2b: Pecos 0-9.0, zoom out 1.08 -> 1.0 (270 frames)
zoom_seg "$RIG" 0 9.0 "1.08-0.08*on/270" "$GRADE" out/seg_rig_b.mp4
# S5a: Pecos 9.0-17.0 (8s), zoom in 1.0 -> 1.06 (240 frames)
zoom_seg "$RIG" 9.0 8.0 "1+0.06*on/240" "$GRADE" out/seg_rig_c.mp4
# S5b: Ft Worth 6.0-12.0 (6s), zoom 1.05 -> 1.12, darker (180 frames)
zoom_seg "$FW" 6.0 6.0 "1.05+0.07*on/180" "$GRADE_DARK" out/seg_fw_d.mp4
echo FOOTAGE_DONE

#!/bin/bash
set -e
cd "$(dirname "$0")"
node render.mjs overlays/ov2a.html 10.5 30 frames/ov2a alpha
node render.mjs overlays/ov2b.html 9.0 30 frames/ov2b alpha
node render.mjs overlays/ov5a.html 8.0 30 frames/ov5a alpha
node render.mjs overlays/ov5b.html 6.0 30 frames/ov5b alpha
echo OVL_DONE

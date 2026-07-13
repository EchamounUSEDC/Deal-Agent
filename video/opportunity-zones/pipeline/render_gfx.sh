#!/bin/bash
set -e
cd "$(dirname "$0")"
node render.mjs scenes/scene3.html 29.0 30 frames/scene3
node render.mjs scenes/scene4.html 24.0 30 frames/scene4
node render.mjs scenes/endcard.html 7.5 30 frames/endcard
echo GFX_DONE

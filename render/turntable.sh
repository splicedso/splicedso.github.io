#!/bin/sh
# Render the package turntable, composite each frame on the page grey, encode a web loop.
cd "$(dirname "$0")/.."
B="$HOME/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender"
NAME=${1:-package}
rm -f render/frames-turn/*
EXTRA=${2:-}
"$B" -b -P render/$NAME.py -- "$PWD/render/frames-turn/" 1600x900 --turntable 240 $EXTRA >/dev/null 2>&1
uv run --with pillow python -I -c "
import glob
from PIL import Image
for f in sorted(glob.glob('render/frames-turn/*.png')):
    im = Image.open(f); bg = Image.new('RGBA', im.size, (238, 238, 238, 255)); bg.alpha_composite(im)
    bg.convert('RGB').save(f.replace('.png', '.jpg'), quality=94)
"
ffmpeg -y -loglevel error -framerate 30 -i render/frames-turn/%04d.jpg -c:v libx264 -pix_fmt yuv420p -crf 22 -preset slow -movflags +faststart -an assets/${OUTNAME:-$NAME}-turn.mp4
ffmpeg -y -loglevel error -framerate 30 -i render/frames-turn/%04d.jpg -c:v libvpx-vp9 -b:v 0 -crf 34 -an assets/${OUTNAME:-$NAME}-turn.webm
cp render/frames-turn/0001.jpg assets/${OUTNAME:-$NAME}-turn-poster.jpg
ls -la assets/${OUTNAME:-$NAME}-turn.*

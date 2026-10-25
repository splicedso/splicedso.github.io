#!/bin/sh
# The hero fall first (the lid text now falls with the chip), then the textured re-renders. One Blender at a time.
cd "$(dirname "$0")/.."
B="/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender"
"$B" -b -P render/tray.py -- "$PWD/render/tray-hero.png" 2800x1600 >render/log/tray.log 2>&1
"$B" -b -P render/gpu.py -- "$PWD/render/gpu.png" 2800x1600 >render/log/gpu.log 2>&1
"$B" -b -P render/gpu.py -- "$PWD/render/hgx.png" 2800x1600 --board >render/log/hgx.log 2>&1
"$B" -b -P render/card.py -- "$PWD/render/card-hero.png" 2800x1600 >render/log/card.log 2>&1
"$B" -b -P render/package.py -- "$PWD/render/package-hero.png" 2800x1600 >render/log/package.log 2>&1
"$B" -b -P render/package.py -- "$PWD/render/package-top.png" 1600x1600 --angle top >render/log/package-top.log 2>&1
"$B" -b -P render/wafer.py -- "$PWD/render/wafer-stand.png" 2000x2400 --stand >render/log/wafer-stand.log 2>&1
echo done >render/log/queue.done

#!/bin/sh
# Resume the 72-frame hero fall at frame 55, then the textured re-renders. One Blender at a time.
cd "$(dirname "$0")/.."
B="$HOME/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender"
"$B" -b -P render/package.py -- "$PWD/render/frames-fall/" 1280x800 --fall 72 --from 55 >render/log/fall.log 2>&1
"$B" -b -P render/tray.py -- "$PWD/render/tray-hero.png" 2800x1600 >render/log/tray.log 2>&1
"$B" -b -P render/gpu.py -- "$PWD/render/gpu.png" 2800x1600 >render/log/gpu.log 2>&1
"$B" -b -P render/gpu.py -- "$PWD/render/hgx.png" 2800x1600 --board >render/log/hgx.log 2>&1
echo done >render/log/queue.done

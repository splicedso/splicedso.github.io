#!/bin/sh
# Render every product shot, then finish them for the web. Waits for any energy measurement
# on this machine to finish first, so the renders don't disturb it.
cd "$(dirname "$0")/.."
while pgrep -f "experiments/quality.py" >/dev/null; do sleep 20; done
B="$HOME/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender"
"$B" -b -P render/package.py -- "$PWD/render/package-hero.png" 2800x1600 >/dev/null 2>&1
"$B" -b -P render/package.py -- "$PWD/render/package-top.png" 1600x1600 --angle top >/dev/null 2>&1
"$B" -b -P render/tray.py -- "$PWD/render/tray-hero.png" 2800x1600 >/dev/null 2>&1
"$B" -b -P render/card.py -- "$PWD/render/card-hero.png" 2800x1600 >/dev/null 2>&1
for n in package-hero:package package-top:package-top tray-hero:tray card-hero:card; do
  uv run --with pillow --with numpy python render/finish.py "render/${n%%:*}.png" "assets/img/${n##*:}.webp"
done

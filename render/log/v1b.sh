cd "/Users/martinmuskov/Docs/GitHub/spliced/site"
while [ ! -f render/log/v1.done ]; do sleep 15; done
"/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender" -b -P render/v1.py -- "$PWD/render/v1-sled.png" 2400x1400 --sled >render/log/v1-sled.log 2>&1
grep -q "Blender quit" render/log/v1-sled.log && { uv run --with pillow --with numpy python render/finish.py render/v1-sled.png assets/img/v1-sled.webp 60 64 0.6 && echo ok >render/log/v1b.done; } || echo crashed >render/log/v1b.done

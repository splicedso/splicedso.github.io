cd "/Users/martinmuskov/Docs/GitHub/spliced/site"
B="/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender"
"$B" -b -P render/decode.py -- "$PWD/render/decode.png" 2800x1600 >render/log/decode.log 2>&1
grep -q "Blender quit" render/log/decode.log || { echo crashed >render/log/designs.done; exit 1; }
"$B" -b -P render/decode.py -- "$PWD/render/sled.png" 2800x1600 --sled >render/log/sled.log 2>&1
grep -q "Blender quit" render/log/sled.log || { echo crashed >render/log/designs.done; exit 1; }
uv run --with pillow --with numpy python render/finish.py render/decode.png assets/img/decode.webp 60 64
uv run --with pillow --with numpy python render/finish.py render/sled.png assets/img/sled.webp 60 64
echo ok >render/log/designs.done

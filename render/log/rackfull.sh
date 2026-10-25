cd "/Users/martinmuskov/Docs/GitHub/spliced/site"
while [ ! -f render/log/realism.done ]; do sleep 15; done
"/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender" -b -P render/rack.py -- "$PWD/render/rack.png" 2000x2600 >render/log/rack.log 2>&1
grep -q "Blender quit" render/log/rack.log && { uv run --with pillow --with numpy python render/finish.py render/rack.png assets/img/rack.webp 60 64 0.6 && echo ok >render/log/rack.done; } || echo crashed >render/log/rack.done

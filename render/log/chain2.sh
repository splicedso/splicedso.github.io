cd "/Users/martinmuskov/Docs/GitHub/spliced/site"
"/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender" -b -P render/rack.py -- "$PWD/render/rack.png" 1500x1950 >render/log/rack.log 2>&1
grep -q "Blender quit" render/log/rack.log && { uv run --with pillow --with numpy python render/finish.py render/rack.png assets/img/rack.webp 60 64 0.6 && echo ok >render/log/rack.done; } || echo crashed >render/log/rack.done
"/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender" -b -P render/cell.py -- "$PWD/render/log/cell-test.png" 1200x700 >render/log/cell-test.log 2>&1
grep -q "Blender quit" render/log/cell-test.log && echo ok >render/log/cell-test.done || echo crashed >render/log/cell-test.done

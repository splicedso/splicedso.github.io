cd "/Users/martinmuskov/Docs/GitHub/spliced/site"
"/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender" -b -P render/cell.py -- "$PWD/render/cell.png" 2800x1600 >render/log/cell.log 2>&1
grep -q "Blender quit" render/log/cell.log || { echo crashed >render/log/cell.done; exit 1; }
"/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender" -b -P render/cell.py -- "$PWD/render/cell-row.png" 2800x1400 --row >render/log/cell-row.log 2>&1
grep -q "Blender quit" render/log/cell-row.log || { echo crashed >render/log/cell.done; exit 1; }
uv run --with pillow --with numpy python render/finish.py render/cell.png assets/img/cell.webp 60 64 0.6
uv run --with pillow --with numpy python render/finish.py render/cell-row.png assets/img/cell-row.webp 60 64 0.6
echo ok >render/log/cell.done

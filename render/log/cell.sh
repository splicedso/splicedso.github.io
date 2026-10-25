cd "/Users/martinmuskov/Docs/GitHub/spliced/site"
while [ ! -f render/log/rack.done ]; do sleep 15; done
"/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender" -b -P render/cell.py -- "$PWD/render/log/cell-test.png" 1200x700 >render/log/cell-test.log 2>&1
grep -q "Blender quit" render/log/cell-test.log && echo ok >render/log/cell-test.done || echo crashed >render/log/cell-test.done

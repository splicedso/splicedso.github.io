#!/bin/sh
# Re-render every page image that carries the Spliced mark (new mark, 27 Oct 2026), then finish for the web.
cd "$(dirname "$0")/.."
B="$HOME/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender"
r() { name=$1; shift; "$B" -b -P "$@" >render/log/$name.log 2>&1; grep -q "Blender quit" render/log/$name.log && echo "ok $name $(date +%H:%M:%S)" || { echo "crashed $name"; return 1; }; }
f() { uv run -q --with pillow --with numpy python render/finish.py render/$1.png assets/img/$1.webp $2; }
r decode render/decode.py -- "$PWD/render/decode.png" 2800x1600 && f decode "60 64"
r desk-open render/desk.py -- "$PWD/render/desk-open.png" 2800x1600 --open && f desk-open "60 64 0.6"
r cell-open render/cell.py -- "$PWD/render/cell-open.png" 2800x1700 --open && f cell-open "60 64 0.6"
r cell-row render/cell.py -- "$PWD/render/cell-row.png" 2800x1400 --row && f cell-row "60 64 0.6"
r node-open render/node.py -- "$PWD/render/node-open.png" 2400x1400 --open && f node-open "60 64 0.6"
r node-grid render/node.py -- "$PWD/render/node-grid.png" 2400x1400 --grid && f node-grid "60 64 0.6"
r node-tray render/node.py -- "$PWD/render/node-tray.png" 2400x1400 --tray && f node-tray "60 64 0.6"
r node-rack render/node.py -- "$PWD/render/node-rack.png" 1500x1950 --rack && f node-rack "60 64 0.6"
r node-row render/node.py -- "$PWD/render/node-row.png" 2200x1100 --row && f node-row "40 64 0.5"
r lineup render/lineup.py -- "$PWD/render/lineup.png" 2400x1200 && f lineup "40 64 0.5"
echo done $(date +%H:%M:%S)

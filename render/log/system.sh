cd "/Users/martinmuskov/Docs/GitHub/spliced/site"
B="/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender"
r() { name=$1; shift; "$B" -b -P "$@" >render/log/$name.log 2>&1; grep -q "Blender quit" render/log/$name.log || { echo "crashed $name" >>render/log/system.done; exit 1; }; }
r lineup render/lineup.py -- "$PWD/render/lineup.png" 2400x1200
r desk render/desk.py -- "$PWD/render/desk.png" 2800x1600
r desk-open render/desk.py -- "$PWD/render/desk-open.png" 2800x1600 --open
r cell render/cell.py -- "$PWD/render/cell.png" 2800x1600
r cell-open render/cell.py -- "$PWD/render/cell-open.png" 2800x1700 --open
r cell-row render/cell.py -- "$PWD/render/cell-row.png" 2800x1400 --row
r decode render/decode.py -- "$PWD/render/decode.png" 2800x1600
r sled render/decode.py -- "$PWD/render/sled.png" 2800x1600 --sled
r rack render/rack.py -- "$PWD/render/rack.png" 1500x1950
uv run --with pillow --with numpy python render/finish.py render/lineup.png assets/img/lineup.webp 40 64 0.5
uv run --with pillow --with numpy python render/finish.py render/desk.png assets/img/desk.webp 60 64 0.6
uv run --with pillow --with numpy python render/finish.py render/desk-open.png assets/img/desk-open.webp 60 64 0.6
uv run --with pillow --with numpy python render/finish.py render/cell.png assets/img/cell.webp 60 64 0.6
uv run --with pillow --with numpy python render/finish.py render/cell-open.png assets/img/cell-open.webp 60 64 0.6
uv run --with pillow --with numpy python render/finish.py render/cell-row.png assets/img/cell-row.webp 60 64 0.6
uv run --with pillow --with numpy python render/finish.py render/decode.png assets/img/decode.webp 60 64
uv run --with pillow --with numpy python render/finish.py render/sled.png assets/img/sled.webp 60 64
uv run --with pillow --with numpy python render/finish.py render/rack.png assets/img/rack.webp 60 64 0.6
echo ok >>render/log/system.done

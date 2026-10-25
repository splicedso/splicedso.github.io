cd "/Users/martinmuskov/Docs/GitHub/spliced/site"
B="/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender"
r() { name=$1; shift; "$B" -b -P "$@" >render/log/$name.log 2>&1; grep -q "Blender quit" render/log/$name.log || { echo "crashed $name" >>render/log/marks.done; exit 1; }; }
r decode render/decode.py -- "$PWD/render/decode.png" 2800x1600
r sled render/decode.py -- "$PWD/render/sled.png" 2800x1600 --sled
r rack render/rack.py -- "$PWD/render/rack.png" 1500x1950
r cell render/cell.py -- "$PWD/render/cell.png" 2800x1600
r cell-row render/cell.py -- "$PWD/render/cell-row.png" 2800x1400 --row
uv run --with pillow --with numpy python render/finish.py render/decode.png assets/img/decode.webp 60 64
uv run --with pillow --with numpy python render/finish.py render/sled.png assets/img/sled.webp 60 64
uv run --with pillow --with numpy python render/finish.py render/rack.png assets/img/rack.webp 60 64 0.6
uv run --with pillow --with numpy python render/finish.py render/cell.png assets/img/cell.webp 60 64 0.6
uv run --with pillow --with numpy python render/finish.py render/cell-row.png assets/img/cell-row.webp 60 64 0.6
echo ok >>render/log/marks.done

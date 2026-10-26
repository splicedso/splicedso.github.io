cd "/Users/martinmuskov/Docs/GitHub/spliced/site"
B="/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender"
while ! grep -q "Blender quit" render/log/lineup-test.log 2>/dev/null; do sleep 15; done
r() { name=$1; shift; "$B" -b -P "$@" >render/log/$name.log 2>&1; grep -q "Blender quit" render/log/$name.log || { echo "crashed $name" >>render/log/family.done; exit 1; }; }
r node render/node.py -- "$PWD/render/node.png" 2400x1400
r node-open render/node.py -- "$PWD/render/node-open.png" 2400x1400 --open
r node-grid render/node.py -- "$PWD/render/node-grid.png" 2400x1400 --grid
r node-tray render/node.py -- "$PWD/render/node-tray.png" 2400x1400 --tray
r node-rack render/node.py -- "$PWD/render/node-rack.png" 1500x1950 --rack
r node-row render/node.py -- "$PWD/render/node-row.png" 2200x1100 --row
r lineup render/lineup.py -- "$PWD/render/lineup.png" 2400x1200
for n in node node-open node-grid node-tray; do uv run --with pillow --with numpy python render/finish.py render/$n.png assets/img/$n.webp 60 64 0.6; done
uv run --with pillow --with numpy python render/finish.py render/node-rack.png assets/img/node-rack.webp 60 64 0.6
uv run --with pillow --with numpy python render/finish.py render/node-row.png assets/img/node-row.webp 40 64 0.5
uv run --with pillow --with numpy python render/finish.py render/lineup.png assets/img/lineup.webp 40 64 0.5
echo ok >>render/log/family.done

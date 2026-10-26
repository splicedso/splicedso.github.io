cd "/Users/martinmuskov/Docs/GitHub/spliced/site"
B="/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender"
while [ ! -f render/log/system.done ]; do sleep 20; done
r() { name=$1; shift; "$B" -b -P "$@" >render/log/$name.log 2>&1; grep -q "Blender quit" render/log/$name.log || { echo "crashed $name" >>render/log/v1.done; exit 1; }; }
r v1-sled render/v1.py -- "$PWD/render/v1-sled.png" 2800x1600 --sled
r v1-sled-open render/v1.py -- "$PWD/render/v1-sled-open.png" 2800x1600 --sled-open
r v1-pod render/v1.py -- "$PWD/render/v1-pod.png" 1500x1950 --pod
r v1-row render/v1.py -- "$PWD/render/v1-row.png" 2400x1200 --row
uv run --with pillow --with numpy python render/finish.py render/v1-sled.png assets/img/v1-sled.webp 60 64 0.6
uv run --with pillow --with numpy python render/finish.py render/v1-sled-open.png assets/img/v1-sled-open.webp 60 64 0.6
uv run --with pillow --with numpy python render/finish.py render/v1-pod.png assets/img/v1-pod.webp 60 64 0.6
uv run --with pillow --with numpy python render/finish.py render/v1-row.png assets/img/v1-row.webp 40 64 0.5
echo ok >>render/log/v1.done

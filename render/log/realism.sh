cd "/Users/martinmuskov/Docs/GitHub/spliced/site"
B="/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender"
while [ ! -f render/log/rack-test.done ]; do sleep 10; done
r() { name=$1; shift; "$B" -b -P "$@" >render/log/$name.log 2>&1; grep -q "Blender quit" render/log/$name.log || { echo "crashed $name" >>render/log/realism.done; }; }
r gpu render/gpu.py -- "$PWD/render/gpu.png" 2800x1600
r hgx render/gpu.py -- "$PWD/render/hgx.png" 2800x1600 --board
r decode render/decode.py -- "$PWD/render/decode.png" 2800x1600
r sled render/decode.py -- "$PWD/render/sled.png" 2800x1600 --sled
r card render/card.py -- "$PWD/render/card-hero.png" 2800x1600
for pair in gpu:gpu hgx:hgx decode:decode sled:sled card-hero:card; do uv run --with pillow --with numpy python render/finish.py render/${pair%%:*}.png assets/img/${pair##*:}.webp 60 64; done
echo ok >>render/log/realism.done

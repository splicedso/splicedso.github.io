cd "/Users/martinmuskov/Docs/GitHub/spliced/site"
while [ ! -f render/log/queue.done ]; do sleep 15; done
"/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender" -b -P render/tray.py -- "/Users/martinmuskov/Docs/GitHub/spliced/site/render/tray-hero.png" 2800x1600 >render/log/tray.log 2>&1
echo done >render/log/after.done

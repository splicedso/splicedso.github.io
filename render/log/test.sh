cd "/Users/martinmuskov/Docs/GitHub/spliced/site"
"/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender" -b -P render/tray.py -- "/Users/martinmuskov/Docs/GitHub/spliced/site/render/log/tray-test.png" 1400x800 >render/log/tray-test.log 2>&1
"/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender" -b -P render/gpu.py -- "/Users/martinmuskov/Docs/GitHub/spliced/site/render/log/gpu-test.png" 1400x800 >render/log/gpu-test.log 2>&1
echo done >render/log/test.done

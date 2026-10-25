cd "/Users/martinmuskov/Docs/GitHub/spliced/site"
while [ ! -f render/log/after.done ]; do sleep 10; done
"/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender" -b -P render/wafer.py -- "/Users/martinmuskov/Docs/GitHub/spliced/site/render/log/wafer-test.png" 1000x1200 --stand >render/log/wafer-test.log 2>&1
echo done >render/log/after2.done

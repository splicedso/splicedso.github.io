#!/bin/sh
# Re-render the package without its made-up part number: the two stills, then the 72 hero frames.
cd "$(dirname "$0")/.."
B="/Users/martinmuskov/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender"
"$B" -b -P render/package.py -- "$PWD/render/package-hero.png" 2800x1600 >render/log/package.log 2>&1
"$B" -b -P render/package.py -- "$PWD/render/package-top.png" 1600x1600 --angle top >render/log/package-top.log 2>&1
echo stills >render/log/stills.done
rm -f render/frames-fall/*.png
"$B" -b -P render/package.py -- "$PWD/render/frames-fall/" 1280x800 --fall 72 >render/log/fall.log 2>&1
echo done >render/log/unbranded.done

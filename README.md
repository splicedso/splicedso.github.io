# splicedso.github.io

The Spliced site. Static HTML, no build step.

- `index.html`: the page. The hero trace replays `assets/trace.json`, a real recording made with [joule](https://github.com/splicedso/joule).
- `brand/`: the mark in every variant, generated from one geometry by `brand/build.py`, plus the LinkedIn banner.
- `render/`: the Blender scenes behind the two films. Rebuild with Blender 5.2 and ffmpeg:

```bash
blender --background --factory-startup --python render/mark.py -- "$PWD/render/frames-mark/"
ffmpeg -framerate 30 -i render/frames-mark/%04d.png -c:v libx264 -pix_fmt yuv420p -crf 20 assets/hero.mp4
```

Preview locally with `python3 -m http.server`.

"""Composite the hero fall frames on page grey and write them as the site's scrubbed JPEG sequence.

    uv run --with pillow python render/fallframes.py render/frames-fall assets/fall
"""
import sys
from pathlib import Path
from PIL import Image

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
dst.mkdir(parents=True, exist_ok=True)
for old in dst.glob("*.jpg"):
    old.unlink()
frames = sorted(src.glob("*.png"))
for i, f in enumerate(frames, 1):
    im = Image.open(f).convert("RGBA")
    bg = Image.new("RGBA", im.size, (238, 238, 238, 255))
    bg.alpha_composite(im)
    bg.convert("RGB").save(dst / f"{i:04d}.jpg", quality=82, optimize=True, progressive=False)
print(len(frames), "frames", im.size)

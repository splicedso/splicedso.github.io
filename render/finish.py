"""Finish a transparent render for the web: crop to the object and its shadow, add fine film grain, export WebP.

    python render/finish.py in.png out.webp [pad] [cut]

cut (0 to 255) drops the faint haze a shadow catcher leaves across the whole floor: alpha below
cut goes to nothing and ramps up to full over the next 96 levels, so the real shadow stays.
"""
import sys
import numpy as np
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
pad = int(sys.argv[3]) if len(sys.argv) > 3 else 60
cut = int(sys.argv[4]) if len(sys.argv) > 4 else 0
im = Image.open(src).convert("RGBA")
if cut:
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < cut else min(255, int(255 * (v - cut) / 96))))
# crop to the object, not its faint floor shadow: bounding box of fairly opaque pixels
bb = im.getchannel("A").point(lambda v: 255 if v > 200 else 0).getbbox()
# keep the whole soft shadow around the object, then fade it to nothing at the borders,
# so the render sits on the page instead of looking like a pasted rectangle
sb = im.getchannel("A").point(lambda v: 255 if v > 6 else 0).getbbox()
m = 3 * pad
box = (max(0, min(bb[0] - m, sb[0])), max(0, min(bb[1] - m, sb[1])), min(im.width, max(bb[2] + m, sb[2])), min(im.height, max(bb[3] + m, sb[3])))
im = im.crop(box)
a = np.asarray(im).astype(np.float32)
# no border fade: it read as white fog around every object. Each scene frames its object whole,
# and the shadow catcher's shadow already fades to nothing on its own.
rng = np.random.default_rng(7)
grain = rng.normal(0, 3.2, a.shape[:2])[..., None]
a[..., :3] = np.clip(a[..., :3] + grain, 0, 255)
Image.fromarray(a.astype(np.uint8), "RGBA").save(dst, quality=88, method=6)
print(dst, im.size)

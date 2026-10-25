"""Finish a transparent render for the web: crop to the object, add fine film grain, export WebP.

    python render/finish.py in.png out.webp [pad]
"""
import sys
import numpy as np
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
pad = int(sys.argv[3]) if len(sys.argv) > 3 else 60
im = Image.open(src).convert("RGBA")
# crop to the object, not its faint floor shadow: bounding box of fairly opaque pixels
bb = im.getchannel("A").point(lambda v: 255 if v > 200 else 0).getbbox()
# keep the whole soft shadow around the object, then fade it to nothing at the borders,
# so the render sits on the page instead of looking like a pasted rectangle
sb = im.getchannel("A").point(lambda v: 255 if v > 6 else 0).getbbox()
m = 3 * pad
box = (max(0, min(bb[0] - m, sb[0])), max(0, min(bb[1] - m, sb[1])), min(im.width, max(bb[2] + m, sb[2])), min(im.height, max(bb[3] + m, sb[3])))
im = im.crop(box)
a = np.asarray(im).astype(np.float32)
h, w = a.shape[:2]
fx = np.clip(np.minimum(np.arange(w), np.arange(w)[::-1]) / (0.14 * w), 0, 1)
fy = np.clip(np.minimum(np.arange(h), np.arange(h)[::-1]) / (0.16 * h), 0, 1)
ramp = np.outer(fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx))
a[..., 3] *= ramp
rng = np.random.default_rng(7)
grain = rng.normal(0, 3.2, a.shape[:2])[..., None]
a[..., :3] = np.clip(a[..., :3] + grain, 0, 255)
Image.fromarray(a.astype(np.uint8), "RGBA").save(dst, quality=88, method=6)
print(dst, im.size)

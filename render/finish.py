"""Finish a transparent render for the web: crop to the object, add fine film grain, export WebP.

    python render/finish.py in.png out.webp [pad]
"""
import sys
import numpy as np
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
pad = int(sys.argv[3]) if len(sys.argv) > 3 else 60
im = Image.open(src).convert("RGBA")
bb = im.getbbox()
im = im.crop((max(0, bb[0] - pad), max(0, bb[1] - pad), min(im.width, bb[2] + pad), min(im.height, bb[3] + pad)))
a = np.asarray(im).astype(np.float32)
rng = np.random.default_rng(7)
grain = rng.normal(0, 3.2, a.shape[:2])[..., None]
a[..., :3] = np.clip(a[..., :3] + grain, 0, 255)
Image.fromarray(a.astype(np.uint8), "RGBA").save(dst, quality=88, method=6)
print(dst, im.size)

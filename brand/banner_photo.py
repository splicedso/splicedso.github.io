"""LinkedIn banners, black and white variants, from our own eight-GPU baseboard render.

The lockup sits on the right, inside the band LinkedIn keeps on phones (the sides crop) and away from
where the profile photo covers on desktop (lower left).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

HERE = Path(__file__).parent
FONT = "/System/Library/Fonts/HelveticaNeue.ttc"
W, H = 3168, 792


def lockup(img, fg, x=480, y=150, sub="Efficient inference."):
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype(FONT, 132, index=10)  # Helvetica Neue Medium
    small = ImageFont.truetype(FONT, 40, index=0)
    k = 150 / 1059  # the mark, 150 px tall
    pts = [(639, 0), (941, 0), (301, 1059), (0, 1059)]
    d.polygon([(x + px * k, y + py * k) for px, py in pts], fill=fg)
    tx = x + 941 * k + 40
    d.text((tx, y - 14), "Spliced", font=big, fill=fg)
    d.text((tx + 4, y + 150 + 6), sub, font=small, fill=fg)
    return img


def shade(img, color, right=False):
    """A soft fade behind the lockup so it reads over the photograph."""
    fade = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(fade)
    if right:  # a clean white field on the right, fading into the photograph
        for i in range(W):
            a = int(205 * (1 if i < 700 else max(0, 1 - (i - 700) / 1300) ** 1.4))
            d.line([(W - 1 - i, 0), (W - 1 - i, H)], fill=a)
    else:
        for i in range(1500):
            d.line([(i, 0), (i, H)], fill=int(245 * max(0, 1 - i / 1500) ** 1.1))
    return Image.composite(Image.new("RGB", (W, H), color), img, fade)


def band(path, focus, contrast, bright):
    im = ImageOps.grayscale(Image.open(path))
    im = ImageEnhance.Brightness(ImageEnhance.Contrast(im).enhance(contrast)).enhance(bright)
    w, h = im.size
    ch = int(w * H / W)
    top = max(0, min(h - ch, int(h * focus - ch / 2)))
    return im.crop((0, top, w, top + ch)).resize((W, H), Image.LANCZOS).convert("RGB")


def render_band(path, bg, focus, contrast, bright, zoom=1.0):
    """A band through one of our own renders (transparent PNG) on a flat background, graded."""
    src = Image.open(path).convert("RGBA")
    base = Image.new("RGBA", src.size, (*bg, 255)); base.alpha_composite(src)
    im = ImageOps.grayscale(base.convert("RGB"))
    im = ImageEnhance.Brightness(ImageEnhance.Contrast(im).enhance(contrast)).enhance(bright)
    w, h = im.size
    cw = int(w / zoom); ch = int(cw * H / W)
    left = (w - cw) // 2
    top = max(0, min(h - ch, int(h * focus - ch / 2)))
    return im.crop((left, top, left + cw, top + ch)).resize((W, H), Image.LANCZOS).convert("RGB")


def lede(img, fg, x, y, text):
    d = ImageDraw.Draw(img)
    d.text((x, y), text, font=ImageFont.truetype(FONT, 34, index=0), fill=fg)
    return img


def object_band(path, bg, height=480, right=1900, grade=(1.0, 1.0)):
    """One of our own renders (transparent PNG), cropped to the object plus a margin for its floor shadow, placed left
    of the lockup. Only the faint shadow is faded toward the crop's edges; the object itself is never faded."""
    from PIL import ImageChops
    src = Image.open(path).convert("RGBA")
    a = src.getchannel("A")
    solid = a.point(lambda v: 255 if v > 200 else 0).getbbox()        # the object
    mw, mh = int((solid[2] - solid[0]) * 0.12), int((solid[3] - solid[1]) * 0.25)
    box = (max(0, solid[0] - mw), max(0, solid[1] - mh), min(src.width, solid[2] + mw), min(src.height, solid[3] + mh))
    obj = src.crop(box); a = obj.getchannel("A"); w, h = a.size
    ramp = int(min(mw, mh) * 0.9) or 1
    fade = Image.new("L", (w, h), 0); d = ImageDraw.Draw(fade)
    for k in range(ramp):
        d.rectangle([k, k, w - 1 - k, h - 1 - k], outline=int(255 * (k / ramp) ** 1.5))
    d.rectangle([ramp, ramp, w - 1 - ramp, h - 1 - ramp], fill=255)
    keep = a.point(lambda v: 255 if v > 200 else 0)                    # solid pixels keep full alpha
    obj.putalpha(ImageChops.lighter(ImageChops.multiply(a, fade), ImageChops.multiply(a, keep)))
    k = height / (solid[3] - solid[1])
    obj = obj.resize((int(w * k), int(h * k)), Image.LANCZOS)
    canvas = Image.new("RGBA", (W, H), (*bg, 255))
    canvas.alpha_composite(obj, (right - obj.width, (H - obj.height) // 2 + 10))
    rgb = canvas.convert("RGB")
    return ImageEnhance.Brightness(ImageEnhance.Contrast(rgb).enhance(grade[0])).enhance(grade[1])


# Both banners (2026-10-26): our own package render with the Spliced mark, the home page's object, on the left;
# the lockup on the right: the mark, the name and the tagline, nothing else (Martin, 26 Oct). Says only what Spliced is today: research on what AI
# costs to run, and models. The eight-GPU baseboard banner (2026-10-25) is retired with the datacenter hardware.
SUB = "Efficient inference systems"
PKG = HERE.parent / "render" / "package-hero.png"
light = object_band(PKG, (238, 238, 238))
lockup(light, (0, 0, 0), x=1960, y=280, sub=SUB).save(HERE / "linkedin-banner-white.png")
dark = object_band(PKG, (12, 12, 12), grade=(1.05, 1.15))
lockup(dark, (255, 255, 255), x=1960, y=280, sub=SUB).save(HERE / "linkedin-banner-black.png")
print("ok")

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


# Both banners: our own eight-GPU baseboard render (render/hgx.png), no photograph, no third-party credit.
SUB = "Efficient inference systems"
dark = render_band(HERE.parent / "render" / "hgx.png", (0, 0, 0), 0.52, 1.25, 0.8, zoom=1.15)
lockup(shade(dark, (0, 0, 0), right=True), (255, 255, 255), x=1960, y=280, sub=SUB).save(HERE / "linkedin-banner-black.png")
light = render_band(HERE.parent / "render" / "hgx.png", (238, 238, 238), 0.52, 1.1, 1.05, zoom=1.15)
lockup(shade(light, (255, 255, 255), right=True), (0, 0, 0), x=1960, y=280, sub=SUB).save(HERE / "linkedin-banner-white.png")
print("ok")

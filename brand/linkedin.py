"""LinkedIn banners (black, white, Meta blue) and the white LinkedIn post poster.

Both draw the mark from brand/mark-*.svg, so its corners are exact.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
FONT = "/System/Library/Fonts/HelveticaNeue.ttc"
W, H = 3168, 792


def lockup(img, fg, x=480, y=150, sub="Efficient inference."):
    """The mark (rendered from brand/mark-*.svg, so its corners are exact), the name and the tagline.
    The mark stands 1.6 cap heights tall, centred on the capitals, as in brand/build.py."""
    import subprocess, tempfile
    d = ImageDraw.Draw(img)
    size = 132
    big = ImageFont.truetype(FONT, size, index=10)  # Helvetica Neue Medium
    small = ImageFont.truetype(FONT, 38, index=0)
    mh = round(size * 0.714 * 1.6)
    src = HERE / ("mark-white.svg" if fg == (255, 255, 255) else "mark-black.svg")
    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        subprocess.run(["rsvg-convert", "-h", str(mh), "-o", f.name, str(src)], check=True)
        m = Image.open(f.name).convert("RGBA")
    m = m.crop(m.getchannel("A").getbbox())
    img.paste(Image.new("RGB", m.size, fg), (x, y), m)
    base = y + mh / 2 + size * 0.714 / 2
    tx = x + m.width + round(size * 0.42)
    d.text((tx, base), "Spliced", font=big, fill=fg, anchor="ls")
    d.text((tx + 3, base + size * 0.55), sub, font=small, fill=fg, anchor="ls")
    return img


# Banners (2026-10-27, Martin: "no need the background"): a plain ground and the lockup, nothing else.
# The lockup is centred and sits a little above the middle, inside the band LinkedIn keeps on phones
# and clear of the profile photo, which covers the lower left on desktop.
SUB = "Efficient inference systems"
PKG = HERE.parent / "render" / "package-hero.png"


def plain_banner(bg, fg, out):
    img = Image.new("RGB", (W, H), bg)
    size, mh = 132, round(132 * 0.714 * 1.6)
    name_w = ImageDraw.Draw(img).textlength("Spliced", font=ImageFont.truetype(FONT, size, index=10))
    lock_w = mh * 250 / 739 + round(size * 0.42) + name_w
    lockup(img, fg, x=round((W - lock_w) / 2), y=round(H * 0.42 - mh / 2), sub=SUB).save(out)


plain_banner((255, 255, 255), (0, 0, 0), HERE / "linkedin-banner-white.png")
plain_banner((0, 0, 0), (255, 255, 255), HERE / "linkedin-banner-black.png")
plain_banner((0, 100, 224), (255, 255, 255), HERE / "linkedin-banner-meta.png")  # Meta blue, #0064E0

def poster(bg, fg, sub_fill, out, w=2160, h=2700):
    """A LinkedIn post (4:5, the feed's largest shape, at twice 1080 x 1350): the lockup centred at the
    top, the tagline under it, our package render below, the address at the foot."""
    import subprocess, tempfile
    img = Image.new("RGBA", (w, h), (*bg, 255))
    src = Image.open(PKG).convert("RGBA")
    a = src.getchannel("A")
    solid = a.point(lambda v: 255 if v > 200 else 0).getbbox()
    mw, mh_ = int((solid[2] - solid[0]) * 0.1), int((solid[3] - solid[1]) * 0.3)
    obj = src.crop((max(0, solid[0] - mw), max(0, solid[1] - mh_), min(src.width, solid[2] + mw), min(src.height, solid[3] + mh_)))
    k = 2000 / obj.width
    obj = obj.resize((int(obj.width * k), int(obj.height * k)), Image.LANCZOS)
    img.alpha_composite(obj, ((w - obj.width) // 2, 1180))
    img = img.convert("RGB")
    d = ImageDraw.Draw(img)
    size = 250
    big = ImageFont.truetype(FONT, size, index=10)
    mh = round(size * 0.714 * 1.6)
    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        subprocess.run(["rsvg-convert", "-h", str(mh), "-o", f.name,
                        str(HERE / ("mark-white.svg" if fg == (255, 255, 255) else "mark-black.svg"))], check=True)
        m = Image.open(f.name).convert("RGBA")
    m = m.crop(m.getchannel("A").getbbox())
    gap = round(size * 0.42)
    name_w = d.textlength("Spliced", font=big)
    x = round((w - (m.width + gap + name_w)) / 2); y = 420
    img.paste(Image.new("RGB", m.size, fg), (x, y), m)
    base = y + mh / 2 + size * 0.714 / 2
    d.text((x + m.width + gap, base), "Spliced", font=big, fill=fg, anchor="ls")
    d.text((w / 2, base + 190), "Efficient inference systems", font=ImageFont.truetype(FONT, 76, index=0), fill=sub_fill, anchor="ms")
    d.text((w / 2, h - 200), "splicedso.github.io", font=ImageFont.truetype(FONT, 54, index=0), fill=sub_fill, anchor="ms")
    img.save(out)


poster((255, 255, 255), (0, 0, 0), (90, 90, 90), HERE / "linkedin-poster-white.png")
print("ok")

"""Generate the Spliced mark in every variant from one geometry.

    uv run --with fonttools --with uharfbuzz python brand/build.py

The mark (2026-10-27) is an upright bar with pointed ends: 250 wide, 750 tall, the points 85 deep,
every corner rounded at 26. Traced from Martin's master artwork (1254 px; fit within 0.6% of its pixels).
Three schemes: black, white, and Meta blue (#0082FB to #0064E0, ink #1C2B33). Every asset comes in
the reverse too. PNGs are rendered with rsvg-convert. The wordmark is Helvetica Neue Medium, set with
HarfBuzz and written as outlines, so no SVG here needs the font installed.
"""
import json
import math
import subprocess
from pathlib import Path

OUT = Path(__file__).parent
ASSETS = OUT.parent / "assets"
FONT = "/System/Library/Fonts/HelveticaNeue.ttc"
MEDIUM, REGULAR = 10, 0

POINTS = [(125, 0), (250, 85), (250, 665), (125, 750), (0, 665), (0, 85)]
R = 26
W, H = 250, 750

BLACK, WHITE = "#000", "#fff"
META_LIGHT, META, META_INK = "#0082FB", "#0064E0", "#1C2B33"
GRAD = "url(#spliced-blue)"


def corners():
    """Each corner as (start tangent point, end tangent point) on the sharp outline."""
    out = []
    for i, p in enumerate(POINTS):
        a, b = POINTS[i - 1], POINTS[(i + 1) % len(POINTS)]
        u = (a[0] - p[0], a[1] - p[1]); lu = math.hypot(*u)
        v = (b[0] - p[0], b[1] - p[1]); lv = math.hypot(*v)
        th = math.acos((u[0] * v[0] + u[1] * v[1]) / (lu * lv))
        t = R / math.tan(th / 2)
        out.append(((p[0] + u[0] / lu * t, p[1] + u[1] / lu * t), (p[0] + v[0] / lv * t, p[1] + v[1] / lv * t)))
    return out


def top_inset():
    """How far the rounded point sits inside the sharp one (the outline's true top and bottom)."""
    (x0, y0), (x1, y1) = (125, 0), (250, 85)
    th = 2 * math.atan2(x1 - x0, y1 - y0)  # the angle at the point
    return R / math.sin(th / 2) - R


INSET = top_inset()
BOX = (0, INSET, W, H - 2 * INSET)  # the outline's bounding box: x, y, w, h


def path(k=1.0, dx=0.0, dy=0.0):
    f = lambda q: f"{q[0] * k + dx:.2f} {q[1] * k + dy:.2f}"
    c = corners()
    d = f"M{f(c[0][1])}"
    for i in range(1, len(c) + 1):
        start, end = c[i % len(c)]
        d += f" L{f(start)} A{R * k:.2f} {R * k:.2f} 0 0 1 {f(end)}"
    return d + " Z"


def grad(x, y, w, h):
    return (f'<defs><linearGradient id="spliced-blue" gradientUnits="userSpaceOnUse" x1="{x:.1f}" y1="{y:.1f}" '
            f'x2="{x + w * 0.35:.1f}" y2="{y + h:.1f}"><stop offset="0" stop-color="{META_LIGHT}"/>'
            f'<stop offset="1" stop-color="{META}"/></linearGradient></defs>')


def shape(fill, height, x, y):
    """The mark `height` tall with its outline's top-left corner at (x, y)."""
    k = height / BOX[3]
    return f'<path fill="{fill}" d="{path(k, x, y - INSET * k)}"/>', (x, y, W * k, height)


def svg(w, h, body, bg=None, radius=0, defs=""):
    rx = f' rx="{radius}"' if radius else ""
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"{rx}/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" width="{w:g}" height="{h:g}">{defs}{rect}{body}</svg>\n'


# ---- wordmark as outlines -------------------------------------------------------------------------
_fonts = {}


def words(text, size, x, baseline, fill, index=MEDIUM, tracking=-0.02):
    """`text` set in Helvetica Neue at `size`, left edge at x, as one path. Returns (svg, advance)."""
    import uharfbuzz as hb
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTCollection
    if index not in _fonts:
        blob = hb.Blob.from_file_path(FONT)
        _fonts[index] = (hb.Font(hb.Face(blob, index)), TTCollection(FONT).fonts[index])
    hbf, tt = _fonts[index]
    upem = tt["head"].unitsPerEm
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(hbf, buf, {"kern": True, "liga": True})
    gs, order = tt.getGlyphSet(), tt.getGlyphOrder()
    s = size / upem
    pen = SVGPathPen(gs)
    pen_x = 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        gs[order[info.codepoint]].draw(TransformPen(pen, (s, 0, 0, -s, x + (pen_x + pos.x_offset) * s, baseline)))
        pen_x += pos.x_advance + tracking * upem
    return f'<path fill="{fill}" d="{pen.getCommands()}"/>', (pen_x - tracking * upem) * s


CAP = 0.714  # Helvetica Neue cap height, as a share of the font size


def lockup(ink, mark_fill, size, x, y, tag=None, tag_fill=None):
    """Mark and name side by side. `size` is the name's font size; (x, y) is the mark's top left.
    The mark stands 1.6 cap heights tall, centred on the capitals."""
    mh = size * CAP * 1.6
    m, (mx, my, mw, _) = shape(mark_fill, mh, x, y)
    base = y + mh / 2 + size * CAP / 2
    name, adv = words("Spliced", size, mx + mw + size * 0.42, base, ink)
    body = m + name
    width = mw + size * 0.42 + adv
    if tag:
        t, tadv = words(tag, size * 0.29, mx + mw + size * 0.44, base + size * 0.55, tag_fill or ink, REGULAR, 0)
        body += t
        width = max(width, mw + size * 0.44 + tadv)
    return body, width, mh


SCHEMES = {  # name: (background, ink, mark fill)
    "black": (WHITE, BLACK, BLACK),          # black on white
    "white": (BLACK, WHITE, WHITE),          # white on black
    "meta": (WHITE, META_INK, GRAD),         # the blue mark, dark ink, on white
    "meta-reverse": (META, WHITE, WHITE),    # white on Meta blue
}


def mark_file(fill):
    pad = 20
    m, _ = shape(fill, BOX[3], pad, pad)
    w, h = W + 2 * pad, BOX[3] + 2 * pad
    return svg(w, h, m, defs=grad(pad, pad, W, BOX[3]) if fill == GRAD else "")


def tile(fg, bg, size=1024, scale=0.6, radius=0):
    mh = size * scale; mw = mh * W / BOX[3]
    x, y = (size - mw) / 2, (size - mh) / 2
    m, _ = shape(fg, mh, x, y)
    defs = grad(x, y, mw, mh) if fg == GRAD else grad(0, 0, size * 0.6, size) if bg == GRAD else ""
    return svg(size, size, m, bg=bg, radius=radius, defs=defs)


def lockup_file(ink, mark_fill, bg=None, tag=None):
    size, pad = 200, 60
    body, w, mh = lockup(ink, mark_fill, size, pad, pad, tag)
    h = mh + 2 * pad + (size * 0.25 if tag else 0)
    defs = grad(pad, pad, mh * W / BOX[3], mh) if mark_fill == GRAD else ""
    return svg(math.ceil(w + 2 * pad), math.ceil(h), body, bg=bg, defs=defs)


def trace_path(w, h, base, top):
    trace = json.loads((ASSETS / "trace.json").read_text())
    samples, T = trace["samples"], trace["samples"][-1][0]
    px = lambda t: t / T * w
    py = lambda p: base - p / 45 * (base - top)
    return " ".join(f"{'M' if i == 0 else 'L'}{px(t):.1f} {py(c):.1f}" for i, (t, c, _) in enumerate(samples))


def og(bg, ink, mark_fill, tag_fill, line_opacity):
    """The share image, 1200 x 630: lockup above the chip power trace of Qwen2.5 1.5B on an M5 Pro."""
    w, h = 1200, 630
    body, lw, mh = lockup(ink, mark_fill, 86, 0, 0, "Efficient inference systems", tag_fill)
    x, y = (w - lw) / 2, 74
    body, _, _ = lockup(ink, mark_fill, 86, x, y, "Efficient inference systems", tag_fill)
    line = (f'<path d="{trace_path(w, h, h - 40, h * 0.42)}" fill="none" stroke="{ink}" stroke-width="1.6" '
            f'stroke-linejoin="round" opacity="{line_opacity}"/>')
    defs = grad(x, y, mh * W / BOX[3], mh)
    return svg(w, h, line + body, bg=bg, defs=defs)


def png(name, height=None, width=None):
    src, dst = OUT / name, OUT / name.replace(".svg", ".png")
    size = ["-h", str(height)] if height else ["-w", str(width)] if width else []
    subprocess.run(["rsvg-convert", *size, "-o", str(dst), str(src)], check=True)


files = {
    # the mark alone, transparent
    "mark-black.svg": mark_file(BLACK),
    "mark-white.svg": mark_file(WHITE),
    "mark-meta.svg": mark_file(GRAD),
    # mark and name, transparent
    "lockup-black.svg": lockup_file(BLACK, BLACK),
    "lockup-white.svg": lockup_file(WHITE, WHITE),
    "lockup-meta.svg": lockup_file(META_INK, GRAD),
    "lockup-meta-reverse.svg": lockup_file(WHITE, WHITE, bg=META),
    # square tiles (profile pictures), both ways round in each scheme
    "tile-white-on-black.svg": tile(WHITE, BLACK),
    "tile-black-on-white.svg": tile(BLACK, WHITE),
    "tile-white-on-meta.svg": tile(WHITE, GRAD),
    "tile-meta-on-white.svg": tile(GRAD, WHITE),
    # app icons, rounded
    "icon-white-on-black.svg": tile(WHITE, BLACK, radius=230),
    "icon-black-on-white.svg": tile(BLACK, WHITE, radius=230),
    "icon-white-on-meta.svg": tile(WHITE, GRAD, radius=230),
    "foundry-icon.svg": tile(WHITE, BLACK, radius=230),
    "favicon.svg": tile(WHITE, BLACK, size=64, scale=0.78, radius=14),
    "apple-touch-icon.svg": tile(WHITE, BLACK, size=180, scale=0.6),
    # share images
    "og-black.svg": og(BLACK, WHITE, WHITE, "#999", 0.16),
    "og-white.svg": og(WHITE, BLACK, BLACK, "#666", 0.12),
    "og-meta.svg": og(META, WHITE, WHITE, "#d6e7ff", 0.22),
}
for name, text in files.items():
    (OUT / name).write_text(text)

for name in files:
    if name.startswith(("mark-",)):
        png(name, height=2048)
    elif name.startswith(("tile-", "icon-")):
        png(name, width=2048)
    elif name.startswith("lockup-"):
        png(name, height=600)
    elif name in ("foundry-icon.svg",):
        png(name, width=1024)
    elif name == "apple-touch-icon.svg":
        png(name, width=180)
    elif name.startswith("og-"):
        png(name, width=1200)

(ASSETS / "favicon.svg").write_text(files["favicon.svg"])
(ASSETS / "mark-black.svg").write_text(files["mark-black.svg"])
(ASSETS / "mark-white.svg").write_text(files["mark-white.svg"])
(ASSETS / "mark-meta.svg").write_text(files["mark-meta.svg"])
subprocess.run(["rsvg-convert", "-w", "32", "-o", str(ASSETS / "favicon-32.png"), str(OUT / "favicon.svg")], check=True)
for name in ("apple-touch-icon.png",):
    (ASSETS / name).write_bytes((OUT / name).read_bytes())
(ASSETS / "og.png").write_bytes((OUT / "og-black.png").read_bytes())

# for site/src/base.html: the nav and footer mark, drawn in currentColor
(OUT / "inline-mark.txt").write_text(
    f'<svg viewBox="{BOX[0]} {BOX[1]:.2f} {BOX[2]} {BOX[3]:.2f}" aria-hidden="true"><path fill="currentColor" d="{path()}"/></svg>\n')
print("\n".join(files))

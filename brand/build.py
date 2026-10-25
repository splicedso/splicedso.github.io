"""Generate the Spliced mark in every variant from one geometry.

The mark is a single slanted bar, traced from the master artwork (1500 px): corners at
(932, 232), (1235, 232), (594, 1291) and (294, 1291), with slightly rounded corners. Drawn
here as a vector, so every size is exact.
"""
from pathlib import Path

A = [(639, 0), (941, 0), (301, 1059), (0, 1059)]
W, H = 941, 1059
ROUND = 0.012  # corner rounding, as a share of the mark's height
OUT = Path(__file__).parent


def path(points, dx=0, dy=0, k=1.0):
    return "M" + " L".join(f"{x * k + dx:.1f} {y * k + dy:.1f}" for x, y in points) + " Z"


def shape(fill, dx=0, dy=0, k=1.0):
    r = ROUND * H * k
    return (f'<path fill="{fill}" stroke="{fill}" stroke-width="{r:.1f}" stroke-linejoin="round" '
            f'd="{path(A, dx, dy, k)}"/>')


def mark(fill):
    pad = ROUND * H
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad:.0f} {-pad:.0f} {W + 2 * pad:.0f} {H + 2 * pad:.0f}">'
            f'{shape(fill)}</svg>\n')


def tile(fg, bg, size=1024, scale=0.52, radius=0):
    k = size * scale / H
    dx, dy = (size - W * k) / 2, (size - H * k) / 2
    rx = f' rx="{radius}"' if radius else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">'
            f'<rect width="{size}" height="{size}" fill="{bg}"{rx}/>{shape(fg, dx, dy, k)}</svg>\n')


def banner(fg, bg, w=1584, h=396):
    """LinkedIn banner, safe on every screen.

    LinkedIn crops the sides on phones and puts the profile photo over the lower left on
    desktop and lower centre-left on mobile. So the lockup sits in a centred safe zone above
    the middle, and the trace (the real chip power trace of Qwen2.5 1.5B on an M5 Pro) runs
    full width behind it as texture that any crop can lose.
    """
    import json
    trace = json.loads((OUT.parent / "assets" / "trace.json").read_text())
    samples, T = trace["samples"], trace["samples"][-1][0]
    base, top = h - 40, h * 0.42
    px = lambda t: t / T * w
    py = lambda p: base - p / 45 * (base - top)
    line = " ".join(f"{'M' if i == 0 else 'L'}{px(t):.1f} {py(c):.1f}" for i, (t, c, _) in enumerate(samples))
    mh = 110
    k = mh / H
    lock_w = mh * W / H + 28 + 300
    mx, my = (w - lock_w) / 2 + 40, 66
    tx = mx + mh * W / H + 28
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<rect width="{w}" height="{h}" fill="{bg}"/>'
            f'<path d="{line}" fill="none" stroke="{fg}" stroke-width="1.6" stroke-linejoin="round" opacity=".16"/>'
            f'{shape(fg, mx, my, k)}'
            f'<text x="{tx:.1f}" y="{my + 70}" font-family="Helvetica Neue" font-weight="600" '
            f'font-size="66" letter-spacing="-2.4" fill="{fg}">Spliced</text>'
            f'<text x="{tx + 3:.1f}" y="{my + 104}" font-family="Helvetica Neue" '
            f'font-size="19" fill="{fg}" opacity=".6">Efficient inference systems.</text>'
            f'</svg>\n')


files = {
    "linkedin-banner-black.svg": banner("#fff", "#000"),
    "linkedin-banner-white.svg": banner("#000", "#fff"),
    "mark-black.svg": mark("#000"),
    "mark-white.svg": mark("#fff"),
    "tile-white-on-black.svg": tile("#fff", "#000"),
    "tile-black-on-white.svg": tile("#000", "#fff"),
    "icon-white-on-black.svg": tile("#fff", "#000", scale=0.6, radius=224),
    "favicon.svg": tile("#fff", "#000", size=64, scale=0.66, radius=14),
}
for name, svg in files.items():
    (OUT / name).write_text(svg)
(OUT.parent / "assets" / "favicon.svg").write_text(files["favicon.svg"])
print("\n".join(files))

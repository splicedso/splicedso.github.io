"""Generate the Spliced mark in every variant from one geometry."""
from pathlib import Path

A = [(0, 192), (418, 0), (418, 205), (145, 331), (145, 449), (0, 516)]
B = [(197, 385), (500, 246), (500, 520), (197, 659)]
W, H = 500, 659
OUT = Path(__file__).parent


def path(points, dx=0, dy=0, k=1.0):
    return "M" + " L".join(f"{x * k + dx:.1f} {y * k + dy:.1f}" for x, y in points) + " Z"


def mark(fill):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">'
            f'<path fill="{fill}" d="{path(A)} {path(B)}"/></svg>\n')


def tile(fg, bg, size=1024, scale=0.52, radius=0):
    k = size * scale / H
    dx, dy = (size - W * k) / 2, (size - H * k) / 2
    rx = f' rx="{radius}"' if radius else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">'
            f'<rect width="{size}" height="{size}" fill="{bg}"{rx}/>'
            f'<path fill="{fg}" d="{path(A, dx, dy, k)} {path(B, dx, dy, k)}"/></svg>\n')


BLUE, DEEP = "#0866FF", "#0143B5"


def banner(fg, bg, w=1584, h=396):
    """LinkedIn banner, safe on every screen.

    LinkedIn crops the sides on phones and puts the profile photo over the lower left on
    desktop and lower centre-left on mobile. So the lockup sits in a centred safe zone above
    the middle, and the trace (the real chip power trace of Qwen2.5 1.5B on an M5 Pro) runs
    full width behind it as texture that any crop can lose. bg is a colour, or "blue" for
    the brand gradient.
    """
    import json
    trace = json.loads((OUT.parent / "assets" / "trace.json").read_text())
    samples, T = trace["samples"], trace["samples"][-1][0]
    base, top = h - 40, h * 0.42
    px = lambda t: t / T * w
    py = lambda p: base - p / 45 * (base - top)
    line = " ".join(f"{'M' if i == 0 else 'L'}{px(t):.1f} {py(c):.1f}" for i, (t, c, _) in enumerate(samples))
    k = 104 / H
    lock_w = 104 * W / H + 24 + 300
    mx, my = (w - lock_w) / 2 + 60, 72
    if bg == "blue":
        defs = (f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
                f'<stop offset="0" stop-color="{BLUE}"/><stop offset="1" stop-color="{DEEP}"/></linearGradient></defs>')
        fill, trace_op, text = "url(#g)", ".22", fg
    else:
        defs, fill, trace_op, text = "", bg, ".18", "#1C2B33"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{defs}'
            f'<rect width="{w}" height="{h}" fill="{fill}"/>'
            f'<path d="{line}" fill="none" stroke="{fg}" stroke-width="1.6" stroke-linejoin="round" opacity="{trace_op}"/>'
            f'<path fill="{fg}" d="{path(A, mx, my, k)} {path(B, mx, my, k)}"/>'
            f'<text x="{mx + 104 * W / H + 24}" y="{my + 66}" font-family="Helvetica Neue" font-weight="600" '
            f'font-size="64" letter-spacing="-2.2" fill="{text}">Spliced</text>'
            f'<text x="{mx + 104 * W / H + 27}" y="{my + 98}" font-family="Helvetica Neue" '
            f'font-size="19" fill="{text}" opacity=".7">Efficient inference.</text>'
            f'</svg>\n')


files = {
    "linkedin-banner-white.svg": banner(BLUE, "#fff"),
    "linkedin-banner-blue.svg": banner("#fff", "blue"),
    "mark-blue.svg": mark(BLUE),
    "tile-blue-on-white.svg": tile(BLUE, "#fff"),
    "tile-white-on-blue.svg": tile("#fff", BLUE),
    "icon-white-on-blue.svg": tile("#fff", BLUE, scale=0.62, radius=224),
    "mark-black.svg": mark("#000"),
    "mark-white.svg": mark("#fff"),
    "tile-white-on-black.svg": tile("#fff", "#000"),
    "tile-black-on-white.svg": tile("#000", "#fff"),
    "icon-white-on-black.svg": tile("#fff", "#000", scale=0.62, radius=224),
    "favicon.svg": tile("#fff", BLUE, size=64, scale=0.66, radius=14),
}
for name, svg in files.items():
    (OUT / name).write_text(svg)
(OUT.parent / "assets" / "favicon.svg").write_text(files["favicon.svg"])
print("\n".join(files))

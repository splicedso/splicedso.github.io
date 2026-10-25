"""The Foundry app mark: a cast ingot (a trapezoid, wider at the base) with the Spliced slash
cut through it. White on black, on a rounded square. Writes foundry-icon.svg/.png and the
mark alone (foundry-mark-white.svg)."""
from pathlib import Path
OUT = Path(__file__).parent


def ingot_paths(cx, cy, s):
    # ingot: top width 0.62s, bottom width 1.0s, height 0.56s; the slash is a gap 0.11s wide
    tw, bw, h, g = 0.62 * s, 1.0 * s, 0.56 * s, 0.11 * s
    top, bot = cy - h / 2, cy + h / 2
    # the slash runs from upper right to lower left, splitting the ingot into two pieces
    sx_top, sx_bot = cx + 0.12 * s, cx - 0.12 * s
    left = [(cx - tw / 2, top), (sx_top - g / 2, top), (sx_bot - g / 2, bot), (cx - bw / 2, bot)]
    right = [(sx_top + g / 2, top), (cx + tw / 2, top), (cx + bw / 2, bot), (sx_bot + g / 2, bot)]
    d = lambda pts: "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    return d(left) + " " + d(right)


def icon(size=1024):
    r = size * 0.225
    p = ingot_paths(size / 2, size / 2 + size * 0.02, size * 0.62)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">'
            f'<rect width="{size}" height="{size}" rx="{r:.0f}" fill="#000"/>'
            f'<path fill="#fff" stroke="#fff" stroke-width="{size*0.012:.1f}" stroke-linejoin="round" d="{p}"/></svg>\n')


(OUT / "foundry-icon.svg").write_text(icon())
p = ingot_paths(500, 300, 1000)
(OUT / "foundry-mark-white.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 6 1000 588"><path fill="#fff" d="{p}"/></svg>\n')
(OUT / "foundry-mark-black.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 6 1000 588"><path fill="#000" d="{p}"/></svg>\n')
print("ok")

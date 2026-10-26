"""Schematic drawings of the cell: plan, front and side elevations, and an exploded view, as SVG with
dimensions in millimetres, generated from the same numbers render/cell.py builds from.

    python render/cell_drawings.py assets/img/cell-drawings.svg
"""
import sys

OUT = sys.argv[1]
MM = 25.0                                   # 1 scene unit = 25 mm
CW, CD, CH, SK = 24.0, 120.0, 48.0, 4.0     # scene units
Y_FAN0, Y_FAN1, Y_BAY0, Y_BAY1 = 5, 11, 14, 100   # from the front face, scene units
PX = 3.4                                    # px per scene unit on the page

ink, mute, hair = "#0d0d0d", "#6b6b6b", "#b8b8b8"
font = "font-family='JetBrains Mono, ui-monospace, Menlo, monospace' font-size='11'"
out = []


def rect(x, y, w, h, stroke=ink, sw=1.2, fill="none", dash=""):
    out.append(f"<rect x='{x:.1f}' y='{y:.1f}' width='{w:.1f}' height='{h:.1f}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}' {('stroke-dasharray=' + chr(39) + dash + chr(39)) if dash else ''}/>")


def line(x1, y1, x2, y2, stroke=ink, sw=1.0):
    out.append(f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{stroke}' stroke-width='{sw}'/>")


def text(x, y, s, anchor="middle", fill=ink, size=11):
    out.append(f"<text x='{x:.1f}' y='{y:.1f}' text-anchor='{anchor}' fill='{fill}' {font.replace('11', str(size))}>{s}</text>")


def dim(x1, y1, x2, y2, label, offset=14, vertical=False):
    """A dimension line with ticks and a centred label, offset from the edge it measures."""
    if vertical:
        x = x1 + offset
        line(x, y1, x, y2, mute, 0.8); line(x - 4, y1, x + 4, y1, mute, 0.8); line(x - 4, y2, x + 4, y2, mute, 0.8)
        out.append(f"<text x='{x + 6:.1f}' y='{(y1 + y2) / 2 + 4:.1f}' fill='{mute}' {font} text-anchor='start'>{label}</text>")
    else:
        y = y1 + offset
        line(x1, y, x2, y, mute, 0.8); line(x1, y - 4, x1, y + 4, mute, 0.8); line(x2, y - 4, x2, y + 4, mute, 0.8)
        out.append(f"<text x='{(x1 + x2) / 2:.1f}' y='{y + 14:.1f}' fill='{mute}' {font} text-anchor='middle'>{label}</text>")


def label(x, y, s, anchor="start"):
    text(x, y, s, anchor, ink, 11)


# ---- plan view (from above): depth along x, width along y
X0, Y0 = 60, 90
w, d = CW * PX, CD * PX
text(X0, Y0 - 74, "PLAN  (dimensions in mm)", "start", ink, 12)
rect(X0, Y0, d, w)
for yy in (Y_FAN0, Y_FAN1, Y_BAY0, Y_BAY1):                          # bulkheads
    line(X0 + yy * PX, Y0, X0 + yy * PX, Y0 + w, hair, 0.8)
# fans 2 x 4 seen from above: 2 across the width
for i in range(2):
    cx = X0 + (Y_FAN0 + 3) * PX; cy = Y0 + (CW / 4 + i * CW / 2) * PX
    rect(cx - 2.8 * PX, cy - 4.6 * PX, 5.6 * PX, 9.2 * PX, ink, 0.8)
# carriers: 2 columns across the width, 3 along the depth
for col_i in range(2):
    for row_i in range(3):
        cx = X0 + (Y_BAY0 + 13 + row_i * 24) * PX; cy = Y0 + (CW / 2 + (-5.6 if col_i == 0 else 5.6)) * PX
        rect(cx - 11 * PX, cy - 5.3 * PX, 22 * PX, 10.6 * PX, ink, 0.9)
        text(cx, cy + 4, f"C{col_i * 3 + row_i} / C{col_i * 3 + row_i + 6}", "middle", mute, 9)
# prefill, host and switch at the back
rect(X0 + (Y_BAY1 - 17) * PX, Y0 + 2 * PX, 16 * PX, 20 * PX, ink, 0.9, dash="2,2"); text(X0 + (Y_BAY1 - 9) * PX, Y0 + 12 * PX + 4, "PREFILL", "middle", mute, 10)
rect(X0 + (Y_BAY1 + 2) * PX, Y0 + 2 * PX, 12 * PX, 8 * PX, ink, 0.8, dash="3,2"); text(X0 + (Y_BAY1 + 8) * PX, Y0 + 6 * PX + 4, "HOST", "middle", mute, 9)
rect(X0 + (Y_BAY1 + 2) * PX, Y0 + 14 * PX, 12 * PX, 8 * PX, ink, 0.8, dash="3,2"); text(X0 + (Y_BAY1 + 8) * PX, Y0 + 18 * PX + 4, "SWITCH", "middle", mute, 9)
# airflow arrows
for i in range(4):
    yy = Y0 + (3 + i * 6) * PX
    line(X0 - 52, yy, X0 - 6, yy, mute, 1.0); out.append(f"<path d='M{X0 - 10:.1f} {yy - 3:.1f} L{X0 - 4:.1f} {yy:.1f} L{X0 - 10:.1f} {yy + 3:.1f}' fill='none' stroke='{mute}'/>")
    line(X0 + d + 6, yy, X0 + d + 52, yy, mute, 1.0); out.append(f"<path d='M{X0 + d + 46:.1f} {yy - 3:.1f} L{X0 + d + 52:.1f} {yy:.1f} L{X0 + d + 46:.1f} {yy + 3:.1f}' fill='none' stroke='{mute}'/>")
text(X0 - 36, Y0 - 8, "AIR IN", "middle", mute, 9); text(X0 + d + 36, Y0 - 8, "AIR OUT", "middle", mute, 9)
# dock on the near long side
rect(X0 + (CD / 2 + CD / 4 - 15) * PX, Y0 + w - 2, 30 * PX, 4, ink, 0.8); text(X0 + (CD / 2 + CD / 4) * PX, Y0 + w + 14, "DOCK (coolant x2, fibre, busbar)", "middle", mute, 9)
dim(X0, Y0 + w, X0 + d, Y0 + w, f"{CD * MM:.0f}", 30)
dim(X0 + d, Y0, X0 + d, Y0 + w, f"{CW * MM:.0f}", 64, vertical=True)
dim(X0, Y0, X0 + Y_FAN1 * PX, Y0, f"{Y_FAN1 * MM:.0f} intake, filter, fans", -34)
dim(X0 + Y_BAY0 * PX, Y0, X0 + Y_BAY1 * PX, Y0, f"{(Y_BAY1 - Y_BAY0) * MM:.0f} module bay", -34)

# ---- side elevation (long side, from the left): depth along x, height along y
Y1 = Y0 + w + 110 + (CH + SK) * PX
text(X0, Y1 - CH * PX - 20, "SIDE ELEVATION", "start", ink, 12)
h = (CH + SK) * PX
rect(X0, Y1, d, SK * PX, ink, 1.0)                                      # skid
for yy in (-40, 0, 40):
    rect(X0 + (CD / 2 + yy - 3) * PX, Y1 + 0.9 * PX, 6 * PX, 2.2 * PX, ink, 0.8)
rect(X0, Y1 - CH * PX, d, CH * PX, ink, 1.2)                            # body
for yy in (Y_FAN0, Y_FAN1, Y_BAY0, Y_BAY1):
    line(X0 + yy * PX, Y1 - CH * PX, X0 + yy * PX, Y1, hair, 0.8)
for tier in range(2):
    zb = Y1 - (3 + tier * 20) * PX
    for row_i in range(3):
        cx = X0 + (Y_BAY0 + 13 + row_i * 24) * PX
        rect(cx - 11 * PX, zb - 16.5 * PX, 22 * PX, 16.5 * PX, ink, 0.9)
rect(X0 + (Y_BAY1 - 17) * PX, Y1 - 40 * PX, 16 * PX, 37 * PX, ink, 0.9, dash="2,2")
rect(X0 + (CD / 4 + CD / 2 - 15) * PX, Y1 - 29 * PX, 30 * PX, 22 * PX, hair, 1.4, dash="4,3"); text(X0 + (CD / 4 + CD / 2) * PX, Y1 - 31 * PX, "DOCK (on the side panel)", "middle", mute, 9)
dim(X0 + d, Y1 - CH * PX, X0 + d, Y1 + SK * PX, f"{(CH + SK) * MM:.0f}", 44, vertical=True)
dim(X0, Y1 + SK * PX, X0 + d, Y1 + SK * PX, f"{CD * MM:.0f}", 30)

# ---- front elevation: width along x, height along y
X2 = X0 + d + 170 + 470
text(X2, Y1 - CH * PX - 20, "FRONT", "start", ink, 12)
rect(X2, Y1, w, SK * PX, ink, 1.0); rect(X2, Y1 - CH * PX, w, CH * PX, ink, 1.2)
rect(X2 + 3 * PX, Y1 - (CH - 5) * PX, (CW - 6) * PX, (CH - 10) * PX, ink, 0.8)      # grille
for i in range(2):
    for j in range(4):
        cx = X2 + (CW / 4 + i * CW / 2) * PX; cy = Y1 - (6 + j * (CH - 12) / 3) * PX
        out.append(f"<circle cx='{cx:.1f}' cy='{cy:.1f}' r='{4.6 * PX:.1f}' fill='none' stroke='{hair}' stroke-width='0.8' stroke-dasharray='3,2'/>")
dim(X2, Y1 + SK * PX, X2 + w, Y1 + SK * PX, f"{CW * MM:.0f}", 30)

# ---- parts list
X3, Y3 = X0 + d + 170, Y0 - 36
text(X3, Y3 - 24, "PARTS (one cell)", "start", ink, 12)
parts = [("skid", "galvanised steel, forklift pockets x3", 1), ("frame", "steel rails and bulkheads", 1), ("side panel with dock", "sheet, couplers x2, fibre, busbar", 2),
         ("top, floor", "sheet", 2), ("front door", "filtered intake grille, handle, mark", 1), ("rear door", "exhaust grille", 1), ("fan wall", "8 x 230 mm fans in a plate", 1),
         ("tier shelf", "steel", 1), ("decode carrier", "tray, duct, board, package, vapour chamber, fins, handle", 12), ("prefill module", "board, package, fin stack", 1),
         ("host shelf", "host board, switch", 1), ("power", "busbar tap, DC stage", 1)]
for i, (name, desc, n) in enumerate(parts):
    yy = Y3 + 12 + i * 26
    text(X3, yy, f"{n:>2} x", "start", ink, 10); text(X3 + 34, yy, name, "start", ink, 10); text(X3 + 34, yy + 11, desc, "start", mute, 8)
text(X3, Y3 + 12 + len(parts) * 26 + 10, "STL for every part at 1 : 10 in render/parts/cell (2.5 mm per 25 mm).", "start", mute, 9)
text(X3, Y3 + 12 + len(parts) * 26 + 26, "A design, not a product. Air cooled: intake front, fan wall, ducted lanes over the fins, exhaust rear.", "start", mute, 9)

page_w = X0 + d + 170 + 470 + w + 80; page_h = Y1 + SK * PX + 90
svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {page_w:.0f} {page_h:.0f}' width='{page_w:.0f}' height='{page_h:.0f}'>"
       f"<rect width='100%' height='100%' fill='#eeeeee'/>" + "".join(out) + "</svg>\n")
open(OUT, "w").write(svg)
print(OUT, f"{page_w:.0f}x{page_h:.0f}")

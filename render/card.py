"""A photo-real datacenter PCIe accelerator card, dual slot, standing on its edge, studio-lit.

Board along x, thickness along y (shroud on -y, backplate on +y), height along z. The bracket is at
-x facing the camera; the power connector sits at the top-rear corner.

    Blender -b -P render/card.py -- out.png [WxH] [--turntable N]
"""
import math, sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).parent))
import studio as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
W, H = (int(v) for v in (args[1] if len(args) > 1 and "x" in args[1] else "2800x1600").split("x"))

sc = S.setup(W, H)
S.floor(0.0)

shroud = S.scuffed("shroud", (0.035, 0.036, 0.04), metal=0.85, rough=0.48)
rib = S.mat("rib", (0.05, 0.05, 0.055), metal=0.85, rough=0.36, micro=0.08)
fin = S.mat("fin", (0.7, 0.7, 0.68), metal=1.0, rough=0.3, micro=0.06)
pcb = S.pcb_mat("pcb", (0.008, 0.02, 0.012), scale=9.0)   # traces and vias under the mask
gold = S.mat("gold", (0.95, 0.72, 0.38), metal=1.0, rough=0.2)
steel = S.scuffed("steel", (0.6, 0.6, 0.58), metal=1.0, rough=0.34)
black = S.mat("black", (0.01, 0.01, 0.01), rough=0.6)
hole = S.mat("hole", (0.0, 0.0, 0.0), rough=1.0)
nylon = S.mat("nylon", (0.02, 0.02, 0.02), rough=0.45)
mark_m = S.mat("markm", (0.8, 0.8, 0.78), metal=1.0, rough=0.22)
laser = S.mat("laser", (0.2, 0.2, 0.2), metal=0.4, rough=0.75)
screw_m = S.mat("screw", (0.3, 0.3, 0.3), metal=1.0, rough=0.3)

L, Hc, z0 = 10.6, 4.1, 0.42      # board length, board height, board bottom
x0, x1 = -L / 2, L / 2
top = z0 + Hc
cz = z0 + Hc / 2

# Board: visible as a thin green edge between shroud and backplate, and below the shroud.
S.box((L, 0.065, Hc), (0, 0, cz), pcb, 0.008)

# PCIe x16 edge connector with the key notch, pads on both faces, fingers below the board.
fx0 = x0 + 1.55
S.box((5.6, 0.065, 0.32), (fx0 + 2.8, 0, z0 - 0.16), pcb, 0.004)
for i in range(82):
    x = fx0 + 0.08 + i * 0.066
    if 10 <= i <= 11:
        continue
    for y in (-0.036, 0.036):
        S.box((0.042, 0.008, 0.27), (x, y, z0 - 0.17), gold, 0.002, 1)
S.box((0.14, 0.1, 0.34), (fx0 + 0.08 + 10.5 * 0.066, 0, z0 - 0.16), hole)   # key notch shadow

# Shroud: x from sx0 to sx1, depth y from -0.06 to -sd, z from sz0 to sz1.
sx0, sx1 = x0 + 0.12, x1 - 0.05
sd, sz0, sz1 = 1.32, z0 + 0.22, top + 0.02
sl = sx1 - sx0
sxc = (sx0 + sx1) / 2
S.box((sl, 0.06, sz1 - sz0), (sxc, -0.1, (sz0 + sz1) / 2), black)            # inner wall
for xe in (sx0 + 0.11, sx1 - 0.11):                                         # end caps, chamfered
    S.box((0.22, sd - 0.06, sz1 - sz0), (xe, -(sd + 0.06) / 2, (sz0 + sz1) / 2), shroud, 0.05, 1)

# Long fin array, visible through the open top and the front grille.
fz0, fz1 = sz0 + 0.1, sz1 - 0.06
n = 128
for i in range(n):
    x = sx0 + 0.3 + i * (sl - 0.6) / (n - 1)
    S.box((0.018, sd - 0.28, fz1 - fz0), (x, -(sd + 0.06) / 2 + 0.05, (fz0 + fz1) / 2), fin, 0.002, 1)
for z in (fz0 + 0.5, fz1 - 0.6):                                            # heat pipes through the stack
    for y in (-0.45, -0.85):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=sl - 0.5, location=(sxc, y, z), rotation=(0, math.pi / 2, 0))
        bpy.ops.object.shade_smooth(); bpy.context.object.data.materials.append(S.mat("cu", (0.85, 0.52, 0.36), metal=1.0, rough=0.25))

# Front skin: a solid lower panel, a grille band of slats above it, a lip along the top edge.
fy = -sd + 0.05
gz0 = sz0 + 1.75                    # grille band from gz0 to gz1
gz1 = sz1 - 0.2
px0, px1 = sx0 + 0.2, sx1 - 0.2
S.box((px1 - px0 + 0.04, 0.12, gz0 - sz0), ((px0 + px1) / 2, fy, (sz0 + gz0) / 2), shroud, 0.045, 1)
S.box((px1 - px0 + 0.04, 0.12, 0.2), ((px0 + px1) / 2, fy, sz1 - 0.1), shroud, 0.04, 1)      # top lip
S.box((sl, 0.05, 0.06), (sxc, -0.2, sz1 - 0.03), shroud, 0.01)                             # rear lip
k = 0
z = gz0 + 0.11
while z < gz1 - 0.05:
    S.box((px1 - px0, 0.09, 0.055), ((px0 + px1) / 2, fy + 0.01, z), shroud, 0.018, 2)
    z += 0.13
for xm in (sxc - 1.7, sxc + 1.7):                                           # slat supports
    S.box((0.07, 0.11, gz1 - gz0), (xm, fy + 0.015, (gz0 + gz1) / 2), shroud, 0.02, 1)

# Panel break: a recessed groove across the lower panel, fine ribbing on the rear section.
S.box((0.03, 0.02, gz0 - sz0 - 0.1), (sxc + 1.2, fy - 0.058, (sz0 + gz0) / 2), hole)
for i in range(46):
    x = sxc + 1.35 + i * 0.07
    if x > px1 - 0.1:
        break
    S.box((0.03, 0.025, gz0 - sz0 - 0.36), (x, fy - 0.068, (sz0 + gz0) / 2), rib, 0.008, 2)
S.box((px1 - px0, 0.02, 0.025), ((px0 + px1) / 2, fy - 0.058, gz0 - 0.03), hole)           # seam under grille

# Our mark and the laser-etched model line, small, on the front panel.
for x in (px0 + 0.12, px1 - 0.12):
    for z in (sz0 + 0.14, gz0 - 0.16):
        S.screw((x, fy - 0.07, z), screw_m, 0.04, axis="y")

# Bracket: steel plate at -x with perforation, L-shaped mounting tab at the top, tongue below.
bx = x0 - 0.03
by0, by1 = -1.42, 0.12
S.box((0.04, by1 - by0, Hc + 0.35), (bx, (by0 + by1) / 2, cz + 0.1), steel, 0.006, 2)
S.box((0.5, by1 - by0, 0.04), (bx - 0.23, (by0 + by1) / 2, top + 0.27), steel, 0.006, 2)
S.box((0.04, 0.3, 0.5), (bx, by0 + 0.35, z0 - 0.3), steel, 0.006, 2)
for r in range(15):
    for c in range(6):
        y = by0 + 0.2 + c * 0.2 + (0.1 if r % 2 else 0)
        if y > by1 - 0.12:
            continue
        z = z0 + 0.35 + r * 0.24
        bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.06, location=(bx, y, z), rotation=(0, math.pi / 2, 0), vertices=6)
        bpy.context.object.data.materials.append(hole)
S.screw((bx - 0.23, by0 + 0.45, top + 0.3), screw_m, 0.06)

# 12V-2x6 auxiliary power connector at the top-rear edge, with a latch.
cx = x1 - 0.75
S.box((0.95, 0.42, 0.34), (cx, -0.3, top + 0.12), nylon, 0.02, 2)
for i in range(6):
    for j in range(2):
        S.box((0.11, 0.11, 0.02), (cx - 0.33 + i * 0.132, -0.38 + j * 0.16, top + 0.29), hole, 0.01, 1)
for i in range(4):
    S.box((0.05, 0.04, 0.02), (cx - 0.2 + i * 0.13, -0.15, top + 0.29), hole)
S.box((0.22, 0.08, 0.14), (cx, -0.54, top + 0.2), nylon, 0.015, 2)

# NVLink-style bridge fingers on the top edge, three short strips.
for b in range(3):
    nx = x0 + 3.6 + b * 1.15
    S.box((0.85, 0.065, 0.14), (nx, 0, top + 0.07), pcb, 0.004)
    for i in range(16):
        for y in (-0.036, 0.036):
            S.box((0.032, 0.008, 0.1), (nx - 0.38 + i * 0.05, y, top + 0.07), gold, 0.002, 1)

# Backplate with screws.
S.box((L - 0.25, 0.07, Hc - 0.08), (0.05, 0.09, cz), shroud, 0.025, 2)
for x in (x0 + 0.4, -1.5, 1.5, x1 - 0.4):
    for z in (z0 + 0.25, top - 0.25):
        S.screw((x + 0.05, 0.135, z), screw_m, 0.045, axis="y")

S.area((-9, -9, 11), 900, 9, (0, 0, cz))
S.area((-12, 2, 4), 350, 5, (0, 0, cz))
S.area((8, -6, 5), 500, 6, (0, 0, cz))
S.area((2, 8, 9), 350, 8, (0, 0, cz))
S.camera((-14.5, -30.0, 8.0), (0.1, -0.4, cz - 0.15), lens=90, fstop=5.0)
if "--turntable" in args:
    S.turntable(OUT, int(args[args.index("--turntable") + 1]), sway=16)
else:
    S.render(OUT)

"""A design concept: the desk unit. One decode carrier, the same part that fills a cell, in a small
air-cooled enclosure for local hosting: intake grille at the front, the carrier's own ducted fin stack,
two fans at the back, a host board under the carrier, power and network at the rear. Proportions of a
small subwoofer: 0.32 m wide, 0.28 m tall, 0.62 m deep. Unbranded except the mark. A concept.

    Blender -b -P render/desk.py -- out.png [WxH] [--open]
"""
import math, random, sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).parent))
import studio as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
W, H = (int(v) for v in (args[1] if len(args) > 1 and "x" in args[1] else "2800x1600").split("x"))
OPEN = "--open" in args
random.seed(61)
sc = S.setup(W, H, hdri_strength=0.6)
S.floor(0.0)

shell = S.scuffed("shell", (0.04, 0.04, 0.042), metal=0.5, rough=0.55)
panel = S.scuffed("panel", (0.06, 0.06, 0.063), metal=0.5, rough=0.5)
steel = S.scuffed("steel", (0.6, 0.6, 0.58), metal=1.0, rough=0.35)
galv = S.scuffed("galv", (0.5, 0.5, 0.5), metal=1.0, rough=0.5)
dark = S.mat("dark", (0.0, 0.0, 0.0), rough=0.9)
cu = S.mat("cu", (0.86, 0.52, 0.34), metal=1.0, rough=0.3)
fin = S.mat("fin", (0.72, 0.72, 0.7), metal=1.0, rough=0.4)
pcb = S.pcb_mat("pcb", (0.008, 0.022, 0.014))
mesh = S.mat("mesh", (0.08, 0.08, 0.085), metal=0.6, rough=0.7)
inset = S.mat("inset", (0.75, 0.75, 0.74), metal=1.0, rough=0.35)
rubber = S.mat("rubber", (0.03, 0.03, 0.03), rough=0.8)
led = bpy.data.materials.new("led"); led.use_nodes = True
e = led.node_tree.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (0.6, 1.0, 0.7, 1); e.inputs["Strength"].default_value = 5
led.node_tree.links.new(e.outputs[0], led.node_tree.nodes["Material Output"].inputs[0])

# 1 unit = 25 mm
UW, UD, UH = 12.8, 24.8, 11.2
# shell: a folded sheet with a seam on top, on four rubber feet
S.box((UW, UD, UH), (0, 0, UH / 2 + 0.4), shell, 0.35, 6)
S.box((UW + 0.1, 0.2, UH + 0.1), (0, 2.0, UH / 2 + 0.4), dark)
for x, y in ((-5, -10), (5, -10), (-5, 10), (5, 10)):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=0.4, location=(x, y, 0.2), vertices=24)
    bpy.context.object.data.materials.append(rubber)
if OPEN:
    # top and the near side off: the carrier visible on its rails, the host board beneath
    pass
# front: a recessed grille the full face, the mark inset top left, a status light
S.box((UW - 1.6, 0.4, UH - 1.6), (0, -UD / 2 - 0.1, UH / 2 + 0.4), mesh, 0.1)
for i in range(int((UH - 2.4) / 0.9)):
    S.box((UW - 2.0, 0.15, 0.3), (0, -UD / 2 - 0.25, 1.6 + i * 0.9), panel)
S.badge((-3.0, -UD / 2 - 0.45, UH - 1.1), 0.9, panel, inset, rot=(math.pi / 2, 0, 0), depth=0.12)
bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.2, location=(4.8, -UD / 2 - 0.35, UH - 1.0), rotation=(math.pi / 2, 0, 0), vertices=12)
bpy.context.object.data.materials.append(led)
# rear: two fans behind grilles, the power inlet, two network ports, one USB-C for setup
for cx in (-3.2, 3.2):
    bpy.ops.mesh.primitive_cylinder_add(radius=2.6, depth=0.6, location=(cx, UD / 2 + 0.1, UH / 2 + 0.6), rotation=(math.pi / 2, 0, 0), vertices=36)
    bpy.context.object.data.materials.append(dark)
    for k in range(7):
        a = k * 2 * math.pi / 7
        S.box((2.2, 0.2, 0.8), (cx + 1.3 * math.cos(a), UD / 2 + 0.25, UH / 2 + 0.6 + 1.3 * math.sin(a)), panel, 0.03, rot=(0, -a, 0.5))
    for r in (1.2, 2.0, 2.7):
        bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.08, location=(cx, UD / 2 + 0.45, UH / 2 + 0.6), rotation=(math.pi / 2, 0, 0))
        bpy.context.object.data.materials.append(steel)
S.box((1.4, 0.3, 1.0), (-5.2, UD / 2 + 0.2, 1.6), dark, 0.05)                  # power inlet
for i in range(2):
    S.box((0.7, 0.3, 0.6), (-2.6 + i * 1.0, UD / 2 + 0.2, 1.6), dark, 0.03)     # network
S.box((0.5, 0.3, 0.25), (0.2, UD / 2 + 0.2, 1.6), dark, 0.02)                  # USB-C
if OPEN:
    # cut the top and the near side by shrinking the shell: redraw as an open frame with the carrier visible
    for o in list(sc.objects):
        if o.type == "MESH" and o.data.materials and o.data.materials[0].name == "shell":
            bpy.data.objects.remove(o)
    for x in (-UW / 2 + 0.4, UW / 2 - 0.4):
        for z in (0.8, UH):
            S.box((0.8, UD, 0.8), (x, 0, z), steel, 0.05)
    for y in (-UD / 2 + 0.4, UD / 2 - 0.4):
        for x in (-UW / 2 + 0.4, UW / 2 - 0.4):
            S.box((0.8, 0.8, UH - 0.8), (x, y, UH / 2 + 0.4), steel, 0.05)
    S.box((UW - 1.0, UD - 1.0, 0.3), (0, 0, 0.55), galv, 0.05)                 # floor
    S.box((UW - 1.0, UD - 1.0, 0.3), (0, 0, 3.4), galv, 0.05)                  # mid shelf: carrier above, host below
    S.box((9.4, 12.0, 0.4), (0, 2, 1.0), pcb, 0.05)                            # host board
    S.silkscreen(0, 2, 1.21, 9, 11, n=30, seed=4)
    # the carrier, the same part as the cell's: tray, duct walls, board, package, vapour chamber, fins, handle
    cx, cy, cz = 0, -1.5, 3.6
    S.box((10.6, 18.0, 0.5), (cx, cy, cz), galv, 0.05)
    for sx in (-5.2, 5.2):
        S.box((0.4, 18.0, 6.4), (cx + sx, cy, cz + 3.2), galv, 0.05)
    S.box((9.4, 16.0, 0.4), (cx, cy, cz + 0.7), pcb, 0.05)
    S.box((5.0, 5.0, 0.9), (cx, cy - 3, cz + 1.4), S.mat("pkg", (0.02, 0.025, 0.02), rough=0.35, coat=0.3), 0.05)
    S.box((8.4, 16.0, 1.0), (cx, cy, cz + 2.4), cu, 0.05)
    for k in range(26):
        S.box((0.12, 16.0, 3.4), (cx - 3.9 + k * 0.31, cy, cz + 4.6), fin, 0.01)
    S.box((2.4, 0.5, 1.6), (cx, cy - 10.3, cz + 2.2), steel, 0.1)
    S.silkscreen(cx, cy + 5, cz + 0.91, 8.6, 5, n=12, seed=9)
    S.camera((-38, -60, 26), (0, 0, 4.5), lens=60, fstop=9)
else:
    S.camera((-36, -58, 24), (0, 0, 5.0), lens=60, fstop=9)
S.area((-20, -28, 32), 26000, 14, (0, 0, 5))
S.area((26, -12, 20), 11000, 10, (0, 0, 5))
S.area((0, 26, 24), 8000, 14, (0, 0, 5))
S.render(OUT)

"""A design concept: a portable datacenter cell. One rack of decode sleds in a sealed, pallet-sized
enclosure with its own heat rejection on top, a blind-mate dock on each side (coolant, fibre, busbar),
forklift pockets below and lifting eyes above. Alone it is one unit; docked end to end, hundreds make a
row that shares power and cooling trunks. --row renders eight docked. Unbranded. A concept, not a product.

    Blender -b -P render/cell.py -- out.png [WxH] [--row]
"""
import math, random, sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).parent))
import studio as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
W, H = (int(v) for v in (args[1] if len(args) > 1 and "x" in args[1] else "2800x1600").split("x"))
ROW = "--row" in args
random.seed(51)
sc = S.setup(W, H, hdri_strength=0.6)
S.floor(0.0)

shell = S.scuffed("shell", (0.04, 0.04, 0.042), metal=0.5, rough=0.55)
panel = S.scuffed("panel", (0.06, 0.06, 0.063), metal=0.5, rough=0.5)
steel = S.scuffed("steel", (0.6, 0.6, 0.58), metal=1.0, rough=0.35)
galv = S.scuffed("galv", (0.5, 0.5, 0.5), metal=1.0, rough=0.5)
dark = S.mat("dark", (0.0, 0.0, 0.0), rough=0.9)
collar = S.mat("collar", (0.85, 0.45, 0.1), rough=0.5)
cu = S.mat("cu", (0.86, 0.52, 0.34), metal=1.0, rough=0.3)
fin = S.mat("fin", (0.72, 0.72, 0.7), metal=1.0, rough=0.4)
led = bpy.data.materials.new("led"); led.use_nodes = True
e = led.node_tree.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (0.6, 1.0, 0.7, 1); e.inputs["Strength"].default_value = 5
led.node_tree.links.new(e.outputs[0], led.node_tree.nodes["Material Output"].inputs[0])

# 1 unit = 25 mm. A cell: 1.2 m wide, 1.0 m deep, 2.2 m tall, on a 0.15 m skid.
CW, CD, CH, SK = 36.0, 18.0, 96.0, 4.0


def cell(ox, docked_left=False, docked_right=False):
    # skid with forklift pockets
    S.box((CW, CD, SK), (ox, 0, SK / 2), galv, 0.3)
    for px in (-9, 9):
        S.box((6.0, CD + 0.2, 2.2), (ox + px, 0, 1.6), dark)
    # body, with two horizontal seams on each side where the panels meet
    S.box((CW, CD, CH), (ox, 0, SK + CH / 2), shell, 0.5, 6)
    for sz in (SK + 32, SK + 64):
        S.box((CW + 0.1, CD + 0.1, 0.25), (ox, 0, sz), dark)
    # front door: a recessed panel with a vertical handle, a status window and a lock
    S.box((CW - 5, 0.8, CH - 7), (ox, -CD / 2 - 0.2, SK + CH / 2), panel, 0.3)
    S.box((1.0, 1.3, 30), (ox + CW / 2 - 5, -CD / 2 - 1.2, SK + CH / 2), steel, 0.3)
    S.box((9, 0.3, 5), (ox - 7, -CD / 2 - 0.65, SK + CH - 10), dark, 0.2)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.2, location=(ox - 10.5, -CD / 2 - 0.75, SK + CH - 10), rotation=(math.pi / 2, 0, 0), vertices=12)
    bpy.context.object.data.materials.append(led)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=0.4, location=(ox + CW / 2 - 5, -CD / 2 - 0.8, SK + CH / 2 - 20), rotation=(math.pi / 2, 0, 0), vertices=24)
    bpy.context.object.data.materials.append(steel)
    # heat rejection: a louvred band across the upper third of the back face, fins behind it, exhaust up and out
    S.box((CW - 6, 1.2, 28), (ox, CD / 2 + 0.2, SK + CH - 20), dark, 0.2)
    for i in range(14):
        S.box((CW - 8, 0.6, 0.5), (ox, CD / 2 + 0.7, SK + CH - 33 + i * 2.0), panel, 0.1)
    for i in range(24):
        S.box((0.3, 2.0, 26), (ox - CW / 2 + 4.5 + i * (CW - 9) / 23, CD / 2 - 0.8, SK + CH - 20), fin, 0.03)
    # a recessed top with two lifting points, flush, so the top stays flat
    S.box((CW - 2, CD - 2, 0.6), (ox, 0, SK + CH + 0.3), panel, 0.2)
    for ex in (-CW / 2 + 6, CW / 2 - 6):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.9, minor_radius=0.25, location=(ox + ex, 0, SK + CH + 0.9), rotation=(math.pi / 2, 0, 0))
        bpy.context.object.data.materials.append(steel)
    # side docks: a plate with two coolant couplers, a fibre plate and a busbar cover; blind-mate when cells butt together
    for side, docked in ((-1, docked_left), (1, docked_right)):
        x = ox + side * (CW / 2 + 0.3)
        S.box((0.6, 10, 34), (x, 0, SK + 34), panel, 0.2)
        if docked:
            continue
        for cy in (-2.5, 0.5):
            bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=1.6, location=(x + side * 0.8, cy, SK + 22), rotation=(0, math.pi / 2, 0), vertices=24)
            bpy.context.object.data.materials.append(steel)
            bpy.ops.mesh.primitive_cylinder_add(radius=1.25, depth=0.5, location=(x + side * 1.5, cy, SK + 22), rotation=(0, math.pi / 2, 0), vertices=24)
            bpy.context.object.data.materials.append(collar)
        S.box((0.4, 4, 3), (x + side * 0.4, 3.5, SK + 22), dark, 0.1)
        for i in range(3):
            S.box((0.3, 0.9, 0.9), (x + side * 0.5, 2.3 + i * 1.2, SK + 22), steel, 0.05)
        S.box((0.5, 8, 4), (x + side * 0.4, 0, SK + 44), dark, 0.2)
        for by in (-2.0, 2.0):
            S.box((0.6, 1.8, 2.4), (x + side * 0.5, by, SK + 44), cu, 0.1)


if ROW:
    N = 8
    for i in range(N):
        cell(-(N - 1) * (CW + 0.6) / 2 + i * (CW + 0.6), docked_left=i > 0, docked_right=i < N - 1)
    S.area((-200, -260, 260), 1.6e6, 120, (0, 0, 50))
    S.area((220, -120, 160), 7e5, 80, (0, 0, 50))
    S.area((0, 200, 220), 5e5, 120, (0, 0, 50))
    S.camera((-300, -520, 150), (-10, 0, 44), lens=45, fstop=10)
else:
    cell(0)
    S.area((-90, -120, 150), 5e5, 60, (0, 0, 50))
    S.area((120, -60, 90), 2.2e5, 40, (0, 0, 50))
    S.area((0, 110, 120), 1.5e5, 60, (0, 0, 50))
    S.camera((-140, -215, 95), (0, 0, 50), lens=55, fstop=10)
S.render(OUT)

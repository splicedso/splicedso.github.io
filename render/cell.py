"""A design concept: a portable datacenter cell. A low, narrow, deep block, the proportions of an
accelerator card lying flat: 0.6 m wide, 1.2 m tall, 3.0 m deep. Sleds load from the front in one column;
heat leaves through a louvred band along the top; a blind-mate dock on each long side (coolant, fibre,
busbar) so cells butt together side by side into a row that shares trunks; forklift pockets along the
skid. Alone it is one unit; hundreds make a row. --row renders eight docked. Unbranded. A concept.

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
CW, CD, CH, SK = 24.0, 120.0, 48.0, 4.0


def cell(ox, docked_left=False, docked_right=False):
    # skid with forklift pockets
    S.box((CW, CD, SK), (ox, 0, SK / 2), galv, 0.3)
    for py in (-40, 0, 40):
        S.box((CW + 0.2, 6.0, 2.2), (ox, py, 1.6), dark)
    # body, with two horizontal seams on each side where the panels meet
    S.box((CW, CD, CH), (ox, 0, SK + CH / 2), shell, 0.5, 6)
    for sy in (-CD / 6, CD / 6):
        S.box((CW + 0.1, 0.25, CH + 0.1), (ox, sy, SK + CH / 2), dark)
        for side in (-1, 1):                                                        # a row of panel screws beside each seam
            for sz in range(6, int(CH) - 4, 7):
                S.screw((ox + side * (CW / 2 + 0.02), sy + 1.2, SK + sz), steel, 0.35, axis="x")
    for side in (-1, 1):                                                            # screws along the top and bottom edges of each side
        for sy in range(-int(CD / 2) + 8, int(CD / 2) - 6, 10):
            S.screw((ox + side * (CW / 2 + 0.02), sy, SK + 2.5), steel, 0.35, axis="x")
            S.screw((ox + side * (CW / 2 + 0.02), sy, SK + CH - 2.5), steel, 0.35, axis="x")
    # the mark, inset in the door above the status window
    S.mark((ox - 5, -CD / 2 - 1.02, SK + CH - 3), 2.4, S.mat("inset", (0.75, 0.75, 0.74), metal=1.0, rough=0.35), rot=(math.pi / 2, 0, 0), depth=0.15)
    # a blank rating-plate recess on the front door, low, and a drain at the rear of the skid
    S.box((7, 0.3, 3.2), (ox - 2, -CD / 2 - 0.65, SK + 8), steel, 0.1)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=1.0, location=(ox + 6, CD / 2 + 0.4, 1.0), rotation=(math.pi / 2, 0, 0), vertices=16)
    bpy.context.object.data.materials.append(steel)
    # front door: a recessed panel with a vertical handle, a status window and a lock
    S.box((CW - 4, 0.8, CH - 5), (ox, -CD / 2 - 0.2, SK + CH / 2), panel, 0.3)
    S.box((1.0, 1.3, 18), (ox + CW / 2 - 4, -CD / 2 - 1.2, SK + CH / 2), steel, 0.3)
    S.box((8, 0.3, 4), (ox - 5, -CD / 2 - 0.65, SK + CH - 7), dark, 0.2)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.2, location=(ox - 8, -CD / 2 - 0.75, SK + CH - 7), rotation=(math.pi / 2, 0, 0), vertices=12)
    bpy.context.object.data.materials.append(led)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=0.4, location=(ox + CW / 2 - 4, -CD / 2 - 0.8, SK + CH / 2 - 14), rotation=(math.pi / 2, 0, 0), vertices=24)
    bpy.context.object.data.materials.append(steel)
    # heat rejection: a louvred band the full depth of the top, fins beneath, exhaust straight up
    S.box((CW - 6, CD - 12, 1.2), (ox, 0, SK + CH + 0.2), dark, 0.2)
    for i in range(int((CD - 14) / 2.4)):
        S.box((CW - 8, 0.6, 0.5), (ox, -CD / 2 + 7 + i * 2.4, SK + CH + 0.9), panel, 0.1)
    for i in range(10):
        S.box((0.3, CD - 14, 6), (ox - CW / 2 + 4 + i * (CW - 8) / 9, 0, SK + CH - 3), fin, 0.03)
    for ey in (-CD / 2 + 8, CD / 2 - 8):                                             # lifting points at each end of the top
        for ex in (-CW / 2 + 4, CW / 2 - 4):
            bpy.ops.mesh.primitive_torus_add(major_radius=0.8, minor_radius=0.22, location=(ox + ex, ey, SK + CH + 0.9), rotation=(math.pi / 2, 0, 0))
            bpy.context.object.data.materials.append(steel)
    # side docks: a plate with two coolant couplers, a fibre plate and a busbar cover; blind-mate when cells butt together
    for side, docked in ((-1, docked_left), (1, docked_right)):
        x = ox + side * (CW / 2 + 0.3)
        S.box((0.6, 30, 22), (x, CD / 4, SK + 18), panel, 0.2)
        if docked:
            continue
        for cy in (CD / 4 - 8, CD / 4 - 4):
            bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=1.6, location=(x + side * 0.8, cy, SK + 12), rotation=(0, math.pi / 2, 0), vertices=24)
            bpy.context.object.data.materials.append(steel)
            bpy.ops.mesh.primitive_cylinder_add(radius=1.25, depth=0.5, location=(x + side * 1.5, cy, SK + 12), rotation=(0, math.pi / 2, 0), vertices=24)
            bpy.context.object.data.materials.append(collar)
        S.box((0.4, 6, 3), (x + side * 0.4, CD / 4 + 4, SK + 12), dark, 0.1)
        for i in range(4):
            S.box((0.3, 0.9, 0.9), (x + side * 0.5, CD / 4 + 1.8 + i * 1.4, SK + 12), steel, 0.05)
        S.box((0.5, 10, 4), (x + side * 0.4, CD / 4 + 10, SK + 24), dark, 0.2)
        for by in (CD / 4 + 7.5, CD / 4 + 12.5):
            S.box((0.6, 1.8, 2.4), (x + side * 0.5, by, SK + 24), cu, 0.1)


if ROW:
    N = 8
    for i in range(N):
        cell(-(N - 1) * (CW + 0.6) / 2 + i * (CW + 0.6), docked_left=i > 0, docked_right=i < N - 1)
    S.area((-200, -260, 260), 1.6e6, 120, (0, 0, 50))
    S.area((220, -120, 160), 7e5, 80, (0, 0, 50))
    S.area((0, 200, 220), 5e5, 120, (0, 0, 50))
    S.camera((-230, -300, 120), (0, -30, 26), lens=45, fstop=10)
else:
    cell(0)
    S.area((-90, -120, 150), 5e5, 60, (0, 0, 50))
    S.area((120, -60, 90), 2.2e5, 40, (0, 0, 50))
    S.area((0, 110, 120), 1.5e5, 60, (0, 0, 50))
    S.camera((-120, -190, 70), (0, -10, 26), lens=55, fstop=10)
S.render(OUT)

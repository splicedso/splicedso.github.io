"""A design concept: a liquid-cooled rack of decode sleds. Front three-quarter view, doors off.

Twelve 1U sleds (the decode sled from render/decode.py, seen from the front), a 4U coolant
distribution unit at the bottom with two supply and return hoses, blanking panels above, a
vertical busbar at the rear, and quick-disconnect coolant couplers on every sled face. Unbranded.
A concept, not a product.

    Blender -b -P render/rack.py -- out.png [WxH]
"""
import math, random, sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).parent))
import studio as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
W, H = (int(v) for v in (args[1] if len(args) > 1 and "x" in args[1] else "2000x2600").split("x"))
random.seed(41)
sc = S.setup(W, H, samples=224, hdri_strength=0.5)
S.floor(0.0)

frame = S.scuffed("frame", (0.03, 0.03, 0.032), metal=0.7, rough=0.5)
face = S.scuffed("face", (0.05, 0.05, 0.052), metal=0.6, rough=0.45)
steel = S.scuffed("steel", (0.6, 0.6, 0.58), metal=1.0, rough=0.35)
dark = S.mat("dark", (0.0, 0.0, 0.0), rough=0.9)
cu = S.mat("cu", (0.86, 0.52, 0.34), metal=1.0, rough=0.3)
hose = S.mat("hose", (0.02, 0.02, 0.022), rough=0.75)
collar = S.mat("collar", (0.85, 0.45, 0.1), rough=0.5)
blank = S.scuffed("blank", (0.04, 0.04, 0.042), metal=0.6, rough=0.55)
led = bpy.data.materials.new("led"); led.use_nodes = True
e = led.node_tree.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (0.6, 1.0, 0.7, 1); e.inputs["Strength"].default_value = 5
led.node_tree.links.new(e.outputs[0], led.node_tree.nodes["Material Output"].inputs[0])

# 1 unit = 25 mm. A 42U cabinet: 600 wide, 1200 deep, 2000 tall.
RW, RD, RH, U = 24.0, 48.0, 80.0, 1.75
# frame: four posts, top and bottom, rails
for x in (-RW / 2, RW / 2):
    for y in (-RD / 2, RD / 2):
        S.box((1.2, 1.2, RH), (x, y, RH / 2), frame, 0.06)
S.box((RW + 1.2, RD + 1.2, 1.0), (0, 0, RH + 0.5), frame, 0.06)
S.box((RW + 1.2, RD + 1.2, 1.6), (0, 0, 0.8), frame, 0.06)
S.box((RW, 1.0, RH), (0, RD / 2, RH / 2), frame, 0.04)        # rear panel
for x in (-RW / 2 - 0.3, RW / 2 + 0.3):                        # side panels, so the cabinet reads as a closed box
    S.box((0.6, RD, RH - 2.0), (x, 0, RH / 2), face, 0.04)
for x in (-RW / 2 + 0.9, RW / 2 - 0.9):                        # front mounting rails with holes
    S.box((0.6, 0.6, RH - 2.0), (x, -RD / 2 + 0.3, RH / 2), steel, 0.02)
    for i in range(0, 126, 6):
        S.box((0.3, 0.3, 0.3), (x, -RD / 2 + 0.0, 1.6 + i * 0.58), dark)
# busbar at the rear, vertical, two copper bars behind a clear-ish cover (drawn as bars only)
for bx in (-1.2, 1.2):
    S.box((0.5, 0.15, RH - 6), (bx, RD / 2 - 1.5, RH / 2), cu, 0.02)
    S.box((0.7, 0.3, 0.6), (bx, RD / 2 - 1.5, RH - 4), dark)
# the coolant distribution unit: 4U at the bottom, with a front grille, a display window and two couplers
CDU_Z = 1.6
S.box((RW - 2.0, RD - 4, 4 * U), (0, 0, CDU_Z + 2 * U), face, 0.08)
S.box((RW - 2.4, 0.1, 4 * U - 0.6), (0, -RD / 2 + 2.02, CDU_Z + 2 * U), dark)
for i in range(30):
    for j in range(4):
        S.box((0.36, 0.1, 0.9), (-RW / 2 + 1.7 + i * 0.72, -RD / 2 + 1.98, CDU_Z + 1.0 + j * 1.5), face)
for k, x in enumerate((-RW / 2 + 3.0, -RW / 2 + 5.2)):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=1.2, location=(x, -RD / 2 + 1.4, CDU_Z + 1.2), rotation=(math.pi / 2, 0, 0), vertices=32)
    bpy.context.object.data.materials.append(steel)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.62, depth=0.35, location=(x, -RD / 2 + 0.9, CDU_Z + 1.2), rotation=(math.pi / 2, 0, 0), vertices=32)
    bpy.context.object.data.materials.append(collar)
S.badge((RW / 2 - 5.5, -RD / 2 + 1.9, CDU_Z + 4 * U - 1.6), 1.1, steel, dark, rot=(math.pi / 2, 0, 0), depth=0.12)       # nameplate on the CDU
# supply and return hoses from the CDU up the inside of the left post to each sled (two vertical runs)
for hx in (-RW / 2 + 1.9, -RW / 2 + 2.6):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=RH - 10, location=(hx, -RD / 2 + 2.6, (RH - 10) / 2 + 6), vertices=24)
    bpy.context.object.data.materials.append(hose)


def sled_face(z):
    """One 1U sled seen from the front: faceplate, grille, two couplers, a handle, a status LED."""
    S.box((RW - 2.4, RD - 4, U - 0.1), (0, 0, z + U / 2), face, 0.05)
    S.box((RW - 2.8, 0.08, U - 0.5), (0, -RD / 2 + 2.0, z + U / 2), dark)
    for i in range(26):
        S.box((0.32, 0.08, 1.1), (-RW / 2 + 4.8 + i * 0.6, -RD / 2 + 1.97, z + U / 2), face)
    for k, x in enumerate((-RW / 2 + 1.9, -RW / 2 + 2.6)):                        # coupler stubs feeding the hoses
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.8, location=(x, -RD / 2 + 2.2, z + U / 2), rotation=(math.pi / 2, 0, 0), vertices=20)
        bpy.context.object.data.materials.append(steel)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.26, depth=0.2, location=(x, -RD / 2 + 1.85, z + U / 2), rotation=(math.pi / 2, 0, 0), vertices=20)
        bpy.context.object.data.materials.append(collar)
    S.box((0.5, 0.3, 0.9), (RW / 2 - 2.2, -RD / 2 + 1.85, z + U / 2), steel, 0.05)  # pull handle
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.05, location=(RW / 2 - 3.6, -RD / 2 + 1.96, z + U / 2), rotation=(math.pi / 2, 0, 0), vertices=12)
    bpy.context.object.data.materials.append(led)


z = CDU_Z + 4 * U + 0.4
for i in range(24):
    sled_face(z + i * (U + 0.1))
z_top = z + 24 * (U + 0.1)
# a top-of-rack switch: 1U, a row of 32 cage ports and two status lights
S.box((RW - 2.4, RD - 4, U - 0.1), (0, 0, z_top + 0.4 + U / 2), face, 0.05)
for i in range(32):
    S.box((0.42, 0.1, 0.5), (-RW / 2 + 2.2 + i * 0.6, -RD / 2 + 1.98, z_top + 0.4 + U / 2), dark, 0.02)
    S.box((0.36, 0.06, 0.44), (-RW / 2 + 2.2 + i * 0.6, -RD / 2 + 1.96, z_top + 0.4 + U / 2), steel, 0.01)
for k in range(2):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.05, location=(RW / 2 - 1.6 - k * 0.3, -RD / 2 + 1.96, z_top + 0.4 + U / 2), rotation=(math.pi / 2, 0, 0), vertices=12)
    bpy.context.object.data.materials.append(led)
z_top = z_top + 0.4 + U + 0.3
for i in range(2):                                                                  # blanking panels above
    S.box((RW - 2.4, 0.3, 2 * U - 0.2), (0, -RD / 2 + 1.9, z_top + 1.0 + i * (2 * U + 0.1) + U - 0.1), blank, 0.04)
    for j in range(20):
        S.box((0.3, 0.1, 0.3), (-RW / 2 + 2.4 + j * 1.0, -RD / 2 + 1.75, z_top + 1.0 + i * (2 * U + 0.1) + U - 0.1), dark)

S.area((-50, -70, 80), 140000, 36, (0, 0, 40))
S.area((45, -30, 40), 40000, 20, (0, 0, 40))
S.area((0, 50, 60), 30000, 30, (0, 0, 40))
S.camera((-52, -120, 58), (0, -8, 40), lens=50, fstop=9)
S.render(OUT)

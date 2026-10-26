"""V1, the cluster someone could build: a 2U sled (two carriers, a fan cage, host and power at the
rear), a 42U pod of sixteen sleds plus a prefill sled, a switch and a power shelf, and a row of pods
in hot-aisle containment. Standard rack width, front-to-back air. Badged. A concept, not a product.

    Blender -b -P render/v1.py -- out.png [WxH] [--sled | --sled-open | --pod | --row]
"""
import math, random, sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).parent))
import studio as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
W, H = (int(v) for v in (args[1] if len(args) > 1 and "x" in args[1] else "2800x1600").split("x"))
MODE = next((a[2:] for a in args if a in ("--sled", "--sled-open", "--pod", "--row")), "sled")
random.seed(71)
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
led = bpy.data.materials.new("led"); led.use_nodes = True
e = led.node_tree.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (0.6, 1.0, 0.7, 1); e.inputs["Strength"].default_value = 5
led.node_tree.links.new(e.outputs[0], led.node_tree.nodes["Material Output"].inputs[0])

# 1 unit = 25 mm. 19-inch sled: 17.7 wide (443 mm), 2U = 3.5 tall (88 mm), 32 deep (800 mm).
SW, SH, SD = 17.7, 3.5, 32.0


def carrier(cx, cy, cz, open_top=True):
    """The one part: tray, duct walls, board, package, vapour chamber, fins front to back, handle, badge."""
    S.box((8.4, 20.0, 0.3), (cx, cy, cz + 0.15), galv, 0.03)
    for sx in (-4.1, 4.1):
        S.box((0.3, 20.0, 2.9), (cx + sx, cy, cz + 1.6), galv, 0.03)
    S.box((7.6, 18.0, 0.3), (cx, cy, cz + 0.5), pcb, 0.03)
    S.box((4.0, 4.0, 0.6), (cx, cy - 3, cz + 0.95), S.mat("pkg", (0.02, 0.025, 0.02), rough=0.35, coat=0.3), 0.03)
    S.box((7.0, 18.0, 0.5), (cx, cy, cz + 1.5), cu, 0.03)
    for k in range(24):
        S.box((0.1, 18.0, 1.4), (cx - 3.3 + k * 0.29, cy, cz + 2.45), fin, 0.005)
    S.box((2.0, 0.4, 1.2), (cx, cy - 10.2, cz + 1.5), steel, 0.08)
    S.badge((cx - 2.0, cy - 10.05, cz + 2.6), 0.32, galv, dark, rot=(math.pi / 2, 0, 0), depth=0.04)


def fan_cage(cx, cy, cz):
    """Four 80 mm fans in a 2U hot-swap cage, blowing front to back."""
    S.box((SW - 1.2, 3.4, SH - 0.2), (cx, cy, cz + SH / 2), panel, 0.05)
    for i in range(4):
        fx = cx - (SW - 1.2) / 2 + 2.2 + i * 4.1
        bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=3.2, location=(fx, cy, cz + SH / 2), rotation=(math.pi / 2, 0, 0), vertices=32)
        bpy.context.object.data.materials.append(dark)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=3.3, location=(fx, cy, cz + SH / 2), rotation=(math.pi / 2, 0, 0), vertices=16)
        bpy.context.object.data.materials.append(panel)
        for k in range(7):
            a = k * 2 * math.pi / 7
            S.box((1.3, 0.12, 0.45), (fx + 0.85 * math.cos(a), cy, cz + SH / 2 + 0.85 * math.sin(a)), panel, 0.02, rot=(0, -a, 0.5))


def sled(ox, oy, oz, lid=True, ears=True, open_top=False):
    """A 2U sled: two carriers side by side, the fan cage behind, host and power stage at the rear."""
    S.box((SW, SD, 0.2), (ox, oy, oz + 0.1), galv, 0.03)                                   # chassis floor
    for sx in (-SW / 2 + 0.1, SW / 2 - 0.1):
        S.box((0.2, SD, SH), (ox + sx, oy, oz + SH / 2), galv, 0.03)                       # side walls
    if ears:
        for sx in (-SW / 2 - 0.9, SW / 2 + 0.9):
            S.box((1.8, 0.2, SH), (ox + sx, oy - SD / 2 + 0.1, oz + SH / 2), steel, 0.03)   # rack ears
            for z in (0.7, SH - 0.7):
                S.screw((ox + sx, oy - SD / 2 - 0.02, oz + z), steel, 0.22, axis="y")
    # front face: a full-width grille, the badge, the status light, two carrier handles poking through
    S.box((SW - 0.4, 0.25, SH - 0.3), (ox, oy - SD / 2 + 0.12, oz + SH / 2), mesh, 0.03)
    for i in range(int((SH - 0.8) / 0.45)):
        S.box((SW - 1.0, 0.1, 0.18), (ox, oy - SD / 2 + 0.02, oz + 0.6 + i * 0.45), panel)
    S.badge((ox - SW / 2 + 2.6, oy - SD / 2 - 0.05, oz + SH - 0.9), 0.42, panel, inset, rot=(math.pi / 2, 0, 0), depth=0.06)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.1, location=(ox + SW / 2 - 1.2, oy - SD / 2 - 0.05, oz + SH - 0.9), rotation=(math.pi / 2, 0, 0), vertices=12)
    bpy.context.object.data.materials.append(led)
    # inside
    for cx in (ox - 4.6, ox + 4.6):
        carrier(cx, oy - SD / 2 + 11.5, oz + 0.2)
    fan_cage(ox, oy - SD / 2 + 23.6, oz + 0.2)
    S.box((7.0, 5.0, 0.3), (ox + 4.4, oy + SD / 2 - 3.2, oz + 0.5), pcb, 0.03)              # host board
    S.silkscreen(ox + 4.4, oy + SD / 2 - 3.2, oz + 0.66, 6.5, 4.5, n=20, seed=3)
    S.box((6.0, 4.0, 1.6), (ox - 4.6, oy + SD / 2 - 3.0, oz + 1.0), panel, 0.08)           # power stage
    # rear face: two network cages, management port, power inlet, exhaust grille
    S.box((SW - 0.4, 0.25, SH - 0.3), (ox, oy + SD / 2 - 0.12, oz + SH / 2), mesh, 0.03)
    for i in range(2):
        S.box((0.6, 0.3, 0.5), (ox + 2.0 + i * 1.0, oy + SD / 2 + 0.05, oz + 1.2), dark, 0.02)
    S.box((0.5, 0.3, 0.4), (ox + 5.2, oy + SD / 2 + 0.05, oz + 1.2), dark, 0.02)
    S.box((1.2, 0.3, 0.8), (ox - 6.5, oy + SD / 2 + 0.05, oz + 1.4), dark, 0.03)
    if lid and not open_top:
        S.box((SW, SD, 0.2), (ox, oy, oz + SH - 0.1), galv, 0.03)
        S.box((SW + 0.1, 0.25, 0.3), (ox, oy - 2, oz + SH - 0.1), dark)                     # lid seam


def pod(ox, oy):
    """A 42U rack: power shelf at the bottom, 16 sleds, a prefill sled, blanking, a switch at the top."""
    RW, RD, RH, U = 24.0, 48.0, 80.0, 1.75
    for x in (-RW / 2, RW / 2):
        for y in (-RD / 2, RD / 2):
            S.box((1.2, 1.2, RH), (ox + x, oy + y, RH / 2), shell, 0.06)
    S.box((RW + 1.2, RD + 1.2, 1.0), (ox, oy, RH + 0.5), shell, 0.06)
    S.box((RW + 1.2, RD + 1.2, 1.6), (ox, oy, 0.8), shell, 0.06)
    for x in (-RW / 2 - 0.3, RW / 2 + 0.3):
        S.box((0.6, RD, RH - 2.0), (ox + x, oy, RH / 2), panel, 0.04)
    for x in (-RW / 2 + 0.9, RW / 2 - 0.9):
        S.box((0.6, 0.6, RH - 2.0), (ox + x, oy - RD / 2 + 0.3, RH / 2), steel, 0.02)
    z = 1.6
    S.box((RW - 2.4, RD - 4, 2 * U - 0.1), (ox, oy, z + U), panel, 0.05)                   # power shelf
    for i in range(6):
        S.box((2.2, 0.3, 1.2), (ox - 8 + i * 3.2, oy - RD / 2 + 1.95, z + U), dark, 0.05)
    z += 2 * U + 0.2
    for i in range(16):                                                                    # sleds
        sled(ox, oy, z + i * (2 * U + 0.05), lid=True, ears=True)
    z += 16 * (2 * U + 0.05) + 0.2
    S.box((RW - 2.4, RD - 4, 2 * U - 0.1), (ox, oy, z + U), panel, 0.05)                   # prefill sled
    S.box((RW - 2.8, 0.25, 2 * U - 0.6), (ox, oy - RD / 2 + 2.0, z + U), mesh, 0.03)
    S.badge((ox - RW / 2 + 3.5, oy - RD / 2 + 1.85, z + 2 * U - 1.0), 0.42, panel, inset, rot=(math.pi / 2, 0, 0), depth=0.06)
    z += 2 * U + 0.2
    S.box((RW - 2.4, RD - 4, U - 0.1), (ox, oy, z + U / 2), panel, 0.05)                   # switch
    for i in range(32):
        S.box((0.42, 0.1, 0.5), (ox - RW / 2 + 2.2 + i * 0.6, oy - RD / 2 + 1.98, z + U / 2), dark, 0.02)
    z += U + 0.2
    while z < RH - 2.5:                                                                    # blanking
        S.box((RW - 2.4, 0.3, 2 * U - 0.2), (ox, oy - RD / 2 + 1.9, z + U), panel, 0.04)
        z += 2 * U + 0.1


if MODE == "sled":
    sled(0, 0, 0, lid=True, ears=False)
    S.camera((-34, -54, 22), (0, 0, 1.4), lens=55, fstop=9)
    S.area((-24, -34, 36), 26000, 16, (0, 0, 2)); S.area((30, -16, 22), 11000, 12, (0, 0, 2)); S.area((0, 30, 26), 8000, 16, (0, 0, 2))
elif MODE == "sled-open":
    sled(0, 0, 0, lid=False, ears=False, open_top=True)
    S.camera((-26, -36, 24), (0, 0, 1.2), lens=55, fstop=10)
    S.area((-24, -34, 36), 26000, 16, (0, 0, 2)); S.area((30, -16, 22), 11000, 12, (0, 0, 2)); S.area((0, 30, 26), 8000, 16, (0, 0, 2))
elif MODE == "pod":
    pod(0, 0)
    S.camera((-52, -120, 58), (0, -8, 40), lens=50, fstop=9)
    S.area((-50, -70, 80), 140000, 36, (0, 0, 40)); S.area((45, -30, 40), 40000, 20, (0, 0, 40)); S.area((0, 50, 60), 30000, 30, (0, 0, 40))
else:
    for i in range(6):
        pod(-5 * 26.0 / 2 + i * 26.0, 0)
    # containment: a hot-aisle roof and end door behind the row, drawn as a frame
    S.box((6 * 26.0 + 4, 30, 1.0), (0, 24 + 15, 86), panel, 0.1)
    S.camera((-150, -240, 100), (0, 0, 40), lens=45, fstop=10)
    S.area((-200, -260, 260), 1.6e6, 120, (0, 0, 40)); S.area((220, -120, 160), 7e5, 80, (0, 0, 40)); S.area((0, 200, 220), 5e5, 120, (0, 0, 40))
S.render(OUT)

"""A design concept: a decode-first inference module, and a 1U sled of them with one prefill module.

The module puts a small compute die in the middle of a ring of eight memory stacks on a wide
interposer: decode is bound by reading weights and cache, so the design spends its silicon on
memory and its power budget on bandwidth, and runs the die at a capped clock under a flat cold
plate instead of a tall fin stack. The sled (--sled) holds six of them behind one compute-dense
prefill module with a tall heat sink, and a switch chip between. Unbranded. A concept, not a product.

    Blender -b -P render/decode.py -- out.png [WxH] [--sled]
"""
import math, random, sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).parent))
import studio as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
W, H = (int(v) for v in (args[1] if len(args) > 1 and "x" in args[1] else "2800x1600").split("x"))
SLED = "--sled" in args
random.seed(33)
sc = S.setup(W, H)
S.floor(0.0)

pcb = S.pcb_mat("pcb", (0.008, 0.022, 0.014))
interposer = S.mat("interposer", (0.25, 0.26, 0.3), metal=1.0, rough=0.18)
die = S.mat("die", (0.08, 0.08, 0.1), metal=0.6, rough=0.12)
hbm = S.mat("hbm", (0.05, 0.05, 0.06), metal=0.4, rough=0.3)
frame = S.scuffed("frame", (0.62, 0.62, 0.6), metal=1.0, rough=0.32)
cap = S.mat("cap", (0.36, 0.32, 0.26), rough=0.45)
choke = S.mat("choke", (0.02, 0.02, 0.02), rough=0.6)
gold = S.mat("gold", (0.95, 0.72, 0.38), metal=1.0, rough=0.22)
fin = S.mat("fin", (0.78, 0.78, 0.76), metal=1.0, rough=0.28, micro=0.05)
cu = S.mat("cu", (0.86, 0.52, 0.34), metal=1.0, rough=0.25)
plate = S.scuffed("plate", (0.7, 0.7, 0.69), metal=1.0, rough=0.22)
black = S.mat("black", (0.015, 0.015, 0.015), rough=0.55)
sub = S.mat("sub", (0.02, 0.025, 0.02), rough=0.35, coat=0.3)


def decode_module(ox, oy, z=0.0, plate_on=False):
    """The decode module: 4.6 x 3.4 units. A small die ringed by eight memory stacks."""
    S.box((4.6, 3.4, 0.08), (ox, oy, z + 0.04), pcb, 0.02)
    for hx in (-2.1, 2.1):
        for hy in (-1.5, 1.5):
            bpy.ops.mesh.primitive_torus_add(major_radius=0.08, minor_radius=0.025, location=(ox + hx, oy + hy, z + 0.085))
            bpy.context.object.data.materials.append(gold)
    for dx, dy, sx, sy in ((0, 1.3, 3.0, 0.12), (0, -1.3, 3.0, 0.12), (1.45, 0, 0.12, 2.7), (-1.45, 0, 0.12, 2.7)):
        S.box((sx, sy, 0.12), (ox + dx, oy + dy, z + 0.14), frame, 0.02)
    S.box((2.6, 2.3, 0.06), (ox, oy, z + 0.11), sub, 0.01)
    S.box((2.3, 2.0, 0.03), (ox, oy, z + 0.155), interposer, 0.005)
    if plate_on:
        # a flat vapour-chamber cold plate the size of the package, with two heat pipes running off the back
        S.box((2.5, 2.2, 0.16), (ox, oy, z + 0.26), plate, 0.03, 4)
        for py in (-0.5, 0.5):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=1.6, location=(ox + 1.5, oy + py, z + 0.3), rotation=(0, math.pi / 2, 0), vertices=24)
            bpy.context.object.data.materials.append(cu)
        # the pipes run into a finned copper condenser at the module's edge, in the sled's airflow
        S.box((0.5, 1.7, 0.4), (ox + 2.35, oy, z + 0.32), cu, 0.02)
        for i in range(14):
            S.box((0.42, 0.03, 0.55), (ox + 2.35, oy - 0.78 + i * 0.12, z + 0.6), fin, 0.003, 2)
        for hx in (-1.15, 1.15):
            for hy in (-1.0, 1.0):
                S.screw((ox + hx, oy + hy, z + 0.36), frame, 0.06)
        S.mark((ox - 0.75, oy - 0.65, z + 0.341), 0.34, S.mat("etch", (0.3, 0.3, 0.3), metal=1.0, rough=0.6))   # laser-etched into the plate
    else:
        S.box((0.6, 0.6, 0.04), (ox, oy, z + 0.19), die, 0.006)                       # the small compute die
        for k in (-1, 1):                                                              # eight memory stacks, a ring
            for j in (-0.72, 0, 0.72):
                S.box((0.34, 0.5, 0.05), (ox + k * 0.78, oy + j, z + 0.195), hbm, 0.006)
            S.box((0.5, 0.34, 0.05), (ox, oy + k * 0.72, z + 0.195), hbm, 0.006)
    S.silkscreen(ox, oy, z + 0.082, 4.4, 3.2, n=70, seed=int(ox * 7 + oy * 3) & 0xFFFF, keep_out=(ox - 1.6, oy - 1.45, ox + 1.6, oy + 1.45))
    for i in range(150):
        x = ox + random.uniform(-2.2, 2.2); y = oy + random.uniform(-1.6, 1.6)
        if abs(x - ox) < 1.55 and abs(y - oy) < 1.4:
            continue
        S.box((0.05, 0.025, 0.025), (x, y, z + 0.093), cap, 0.003, 2)
    S.mark((ox + 1.95, oy + 1.35, z + 0.083), 0.22, S.mat("silkmark", (0.9, 0.9, 0.87), rough=0.7))             # silk mark in the board's corner
    for i in range(6):                                                                  # a short power stage row: low power
        S.box((0.22, 0.22, 0.12), (ox - 1.1 + i * 0.44, oy - 1.62, z + 0.14), choke, 0.02)


def prefill_module(ox, oy, z=0.0):
    """The prefill module: compute dense, a big die with two stacks, a tall fin stack."""
    S.box((4.6, 3.4, 0.08), (ox, oy, z + 0.04), pcb, 0.02)
    S.box((2.6, 2.4, 0.25), (ox, oy, z + 0.2), cu, 0.02)
    for i in range(34):
        S.box((0.035, 2.3, 1.6), (ox - 1.25 + i * 0.075, oy, z + 1.15), fin, 0.004, 2)
    S.box((2.6, 0.08, 1.6), (ox, oy - 1.2, z + 1.15), frame, 0.01)
    S.box((2.6, 0.08, 1.6), (ox, oy + 1.2, z + 1.15), frame, 0.01)
    for i in range(14):
        S.box((0.22, 0.22, 0.12), (ox - 2.1, oy - 1.5 + i * 0.23, z + 0.14), choke, 0.02)


if SLED:
    # a 1U sled: six decode modules in two rows behind one prefill module and a switch, power at the back
    S.box((20.0, 8.6, 0.12), (0, 0, 0.06), pcb, 0.03)
    S.silkscreen(0, 0, 0.122, 19.0, 8.0, n=140, seed=9)
    S.box((20.4, 9.0, 0.3), (0, 0, -0.12), S.mat("tray", (0.03, 0.03, 0.032), metal=0.7, rough=0.5, micro=0.1), 0.03)
    for r, y in enumerate((-2.2, 2.2)):
        for c in range(3):
            decode_module(-6.4 + c * 5.0, y, z=0.12, plate_on=True)
    prefill_module(6.6, 1.6, z=0.12)
    S.box((1.2, 0.9, 0.12), (6.6, -2.2, 0.2), cu, 0.02)                                 # the switch
    for i in range(12):
        S.box((0.03, 0.85, 0.4), (6.6 - 0.5 + i * 0.09, -2.2, 0.44), fin, 0.003, 2)
    for i in range(4):                                                                  # power connectors at the back
        S.box((0.9, 0.5, 0.45), (-8.5 + i * 1.6, 3.9, 0.35), black, 0.04)
    for i in range(110):                                                                # edge fingers at the front
        S.box((0.06, 0.2, 0.02), (-9.6 + i * 0.12, -4.2, 0.13), gold, 0.002, 2)
    S.area((-12, -14, 16), 1600, 14, (0, 0, 1))
    S.area((14, -8, 8), 900, 8, (0, 0, 1))
    S.area((0, 14, 10), 600, 14, (0, 0, 1))
    S.camera((16.0, -27.0, 20.0), (0, 0, 0.6), lens=52, fstop=8)
else:
    decode_module(0, 0)
    S.area((-5, -6, 7), 600, 6)
    S.area((6, -2, 3), 400, 4)
    S.area((0, 7, 6), 300, 7)
    S.camera((7.8, -12.6, 9.0), (0, 0, 0.1), lens=85, fstop=8)
S.render(OUT)

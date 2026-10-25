"""A photo-real datacenter GPU module (SXM-style), and an 8-GPU baseboard built from it.

Module: a dark-green high-layer-count board, a large GPU die on a silicon interposer ringed by
six HBM stacks, a stiffener frame, dense decoupling capacitors, power stages along one edge,
mounting holes with plated rings. Baseboard (--board): eight modules under tall fin-stack heat
sinks in two rows of four, four switch chips with low heat sinks, power connectors and a
mezzanine edge, on a large board.

    Blender -b -P render/gpu.py -- out.png [WxH] [--board] [--turntable N]
"""
import math, random, sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).parent))
import studio as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
W, H = (int(v) for v in (args[1] if len(args) > 1 and "x" in args[1] else "2800x1600").split("x"))
BOARD = "--board" in args
random.seed(21)
sc = S.setup(W, H)
S.floor(0.0)

pcb = S.mat("pcb", (0.008, 0.022, 0.014), rough=0.5, coat=0.15, micro=0.05)
interposer = S.mat("interposer", (0.25, 0.26, 0.3), metal=1.0, rough=0.18)
die = S.mat("die", (0.08, 0.08, 0.1), metal=0.6, rough=0.12)
hbm = S.mat("hbm", (0.05, 0.05, 0.06), metal=0.4, rough=0.3)
frame = S.mat("frame", (0.62, 0.62, 0.6), metal=1.0, rough=0.32, micro=0.08)
cap = S.mat("cap", (0.36, 0.32, 0.26), rough=0.45)
choke = S.mat("choke", (0.02, 0.02, 0.02), rough=0.6)
gold = S.mat("gold", (0.95, 0.72, 0.38), metal=1.0, rough=0.22)
fin = S.mat("fin", (0.78, 0.78, 0.76), metal=1.0, rough=0.28, micro=0.05)
cu = S.mat("cu", (0.86, 0.52, 0.34), metal=1.0, rough=0.25)
black = S.mat("black", (0.015, 0.015, 0.015), rough=0.55)
silk = S.mat("silk", (0.85, 0.85, 0.82), rough=0.6)


def module(ox, oy, z=0.0, heatsink=False):
    """One GPU module, about 4.5 x 3 units, centred at (ox, oy)."""
    S.box((4.6, 3.0, 0.08), (ox, oy, z + 0.04), pcb, 0.02)
    # mounting holes with plated rings
    for hx in (-2.1, 2.1):
        for hy in (-1.3, 1.3):
            bpy.ops.mesh.primitive_torus_add(major_radius=0.08, minor_radius=0.025, location=(ox + hx, oy + hy, z + 0.085))
            bpy.context.object.data.materials.append(gold)
    if heatsink:
        # cold plate base and a tall fin stack over the package
        S.box((2.6, 2.4, 0.25), (ox, oy, z + 0.2), cu, 0.02)
        for i in range(34):
            S.box((0.035, 2.3, 1.6), (ox - 1.25 + i * 0.075, oy, z + 1.15), fin, 0.004, 2)
        S.box((2.6, 0.08, 1.6), (ox, oy - 1.2, z + 1.15), frame, 0.01)
        S.box((2.6, 0.08, 1.6), (ox, oy + 1.2, z + 1.15), frame, 0.01)
        for hx in (-1.15, 1.15):
            for hy in (-1.05, 1.05):
                S.screw((ox + hx, oy + hy, z + 0.34), frame, 0.06)
        return
    # stiffener frame around the package
    for dx, dy, sx, sy in ((0, 1.05, 2.6, 0.12), (0, -1.05, 2.6, 0.12), (1.25, 0, 0.12, 2.2), (-1.25, 0, 0.12, 2.2)):
        S.box((sx, sy, 0.12), (ox + dx, oy + dy, z + 0.14), frame, 0.02)
    # package substrate, interposer, die, HBM stacks
    S.box((2.2, 1.8, 0.06), (ox, oy, z + 0.11), S.mat("sub", (0.02, 0.025, 0.02), rough=0.35, coat=0.3), 0.01)
    S.box((1.9, 1.4, 0.03), (ox, oy, z + 0.155), interposer, 0.005)
    S.box((0.85, 1.1, 0.04), (ox, oy, z + 0.19), die, 0.006)
    for side in (-1, 1):
        for k in (-1, 0, 1):
            S.box((0.32, 0.36, 0.05), (ox + side * 0.67, oy + k * 0.4, z + 0.195), hbm, 0.006)
    # decoupling capacitors and power stages
    for i in range(140):
        x = ox + random.uniform(-2.2, 2.2); y = oy + random.uniform(-1.4, 1.4)
        if abs(x - ox) < 1.35 and abs(y - oy) < 1.15:
            continue
        S.box((0.05, 0.025, 0.025), (x, y, z + 0.093), cap, 0.003, 2)
    for i in range(10):
        S.box((0.22, 0.22, 0.12), (ox - 2.0 + i * 0.44, oy - 1.45 + 0.0, z + 0.14), choke, 0.02)
    S.text("SPL-G1", (ox + 1.6, oy + 1.3, z + 0.081), 0.09, silk)


if BOARD:
    S.box((22.0, 9.6, 0.12), (0, 0, 0.06), pcb, 0.03)                      # baseboard
    for r, y in enumerate((-2.4, 2.4)):
        for c in range(4):
            module(-7.5 + c * 5.0, y, z=0.12, heatsink=True)
    for c in range(4):                                                     # switch chips, low heat sinks
        x = -7.5 + c * 5.0
        S.box((1.0, 0.7, 0.12), (x, 0, 0.2), cu, 0.02)
        for i in range(10):
            S.box((0.03, 0.65, 0.35), (x - 0.4 + i * 0.09, 0, 0.42), fin, 0.003, 2)
    for i in range(6):                                                     # power connectors
        S.box((0.9, 0.5, 0.45), (10.4, -3.8 + i * 1.5, 0.35), black, 0.04)
    for i in range(120):                                                   # mezzanine edge fingers
        S.box((0.06, 0.2, 0.02), (-10.6 + i * 0.12, -4.7, 0.13), gold, 0.002, 2)
    S.area((-12, -14, 16), 1600, 14, (0, 0, 1))
    S.area((14, -8, 8), 900, 8, (0, 0, 1))
    S.area((0, 14, 10), 600, 14, (0, 0, 1))
    S.camera((17.0, -30.0, 22.0), (0, 0, 0.8), lens=52, fstop=8)
else:
    module(0, 0)
    S.area((-5, -6, 7), 600, 6)
    S.area((6, -2, 3), 400, 4)
    S.area((0, 7, 6), 300, 7)
    S.camera((7.8, -12.6, 9.0), (0, 0, 0.1), lens=85, fstop=8)

if "--turntable" in args:
    S.turntable(OUT, int(args[args.index("--turntable") + 1]), sway=18)
else:
    S.render(OUT)

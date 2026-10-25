"""A photo-real DDR5 server memory module (RDIMM), studio-lit on a shadow-catcher floor.

Black solder-mask PCB with ten DRAM packages, a PMIC, an SPD hub and RCD, gold contacts with
the key notch, and passive components between the packages.

    Blender -b -P render/dimm.py -- out.png [WxH]
"""
import math, random, sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).parent))
import studio as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
W, H = (int(v) for v in (args[1] if len(args) > 1 and "x" in args[1] else "2800x1600").split("x"))
random.seed(9)
sc = S.setup(W, H)
S.floor(0.0)

pcb = S.mat("pcb", (0.006, 0.008, 0.007), rough=0.5, coat=0.18, micro=0.06)
pkg = S.mat("pkg", (0.008, 0.008, 0.008), rough=0.72, micro=0.05)
gold = S.mat("gold", (0.95, 0.72, 0.38), metal=1.0, rough=0.2)
laser = S.mat("laser", (0.3, 0.3, 0.3), rough=0.6)
cap = S.mat("cap", (0.36, 0.32, 0.26), rough=0.45)
silk = S.mat("silk", (0.85, 0.85, 0.82), rough=0.6)

L, Hh, T = 13.3, 3.1, 0.06      # 133.35 x 31.25 mm, scaled
z0 = 0.05
# The module stands on its contact edge, as in a slot.
S.box((L, T, Hh), (0, 0, z0 + Hh / 2), pcb, 0.01)
for i in range(144):
    x = -L / 2 + 0.35 + i * 0.087
    if 70 <= i <= 72:
        continue  # key notch
    for side in (-1, 1):
        S.box((0.06, 0.004, 0.32), (x, side * (T / 2 + 0.002), z0 + 0.2), gold, 0.002, 2)

# ten DRAM packages in a row, two banks of five around the RCD
xs = [-5.5, -4.25, -3.0, -1.75, -0.5, 1.75, 3.0, 4.25, 5.5, 6.45]
for k, x in enumerate([-5.55, -4.4, -3.25, -2.1, -0.95, 1.55, 2.7, 3.85, 5.0, 6.15]):
    S.box((0.98, 0.09, 1.1), (x, -T / 2 - 0.045, z0 + 1.65), pkg, 0.02)
    S.text("D5", (x, -T / 2 - 0.0905, z0 + 1.85), 0.16, laser, rot=(math.pi / 2, 0, 0))
    S.text("16Gb 4800", (x, -T / 2 - 0.0905, z0 + 1.55), 0.09, laser, rot=(math.pi / 2, 0, 0))
# RCD in the middle, PMIC at one end, SPD hub
S.box((0.7, 0.08, 0.7), (0.3, -T / 2 - 0.04, z0 + 1.65), pkg, 0.02)
S.box((0.55, 0.07, 0.55), (-6.2, -T / 2 - 0.035, z0 + 2.55), pkg, 0.015)
S.box((0.3, 0.06, 0.25), (6.3, -T / 2 - 0.03, z0 + 2.65), pkg, 0.01)
# passives
for i in range(60):
    x = random.uniform(-6.3, 6.3); z = random.choice([0.75, 0.85, 2.55, 2.65]) + z0
    if abs(x + 6.2) < 0.45 and z > 2:
        continue
    S.box((0.06, 0.03, 0.03), (x, -T / 2 - 0.016, z), cap, 0.004, 2)
# silkscreen label strip and the mark
S.box((1.6, 0.003, 0.32), (-3.6, -T / 2 - 0.0016, z0 + 2.75), silk)
S.mark((4.5, -T / 2 - 0.002, z0 + 2.72), 0.32, silk, rot=(math.pi / 2, 0, 0))

S.area((-6, -8, 7), 700, 8)
S.area((7, -3, 3), 450, 4)
S.area((0, 7, 5), 300, 8)
S.camera((14.5, -26.0, 9.0), (0.3, 0, 1.4), lens=85, fstop=5.6)
S.render(OUT)

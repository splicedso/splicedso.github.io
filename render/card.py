"""A photo-real inference accelerator card on its edge, studio-lit, on a shadow-catcher floor.

    Blender -b -P render/card.py -- out.png [WxH]
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

shroud = S.mat("shroud", (0.05, 0.05, 0.052), metal=0.75, rough=0.5, micro=0.12)
fin = S.mat("fin", (0.72, 0.72, 0.7), metal=1.0, rough=0.3, micro=0.05)
pcb = S.mat("pcb", (0.01, 0.016, 0.013), rough=0.4, coat=0.5)
gold = S.mat("gold", (0.95, 0.72, 0.38), metal=1.0, rough=0.22)
steel = S.mat("steel", (0.62, 0.62, 0.6), metal=1.0, rough=0.32, micro=0.08)
black = S.mat("black", (0.012, 0.012, 0.012), rough=0.55)
mark_m = S.mat("markm", (0.85, 0.85, 0.83), metal=1.0, rough=0.25)
laser = S.mat("laser", (0.28, 0.28, 0.28), metal=0.6, rough=0.6)
copper = S.mat("copper", (0.85, 0.5, 0.33), metal=1.0, rough=0.3)

L, Hc, z0 = 10.4, 4.0, 0.18  # card length and height (scene units), lift off the floor
cz = z0 + Hc / 2

# Board, with gold fingers along the bottom edge.
S.box((L, 0.07, Hc), (0, 0, cz), pcb, 0.01)
for i in range(70):
    x = -2.6 + i * 0.07
    if 22 <= i <= 24:
        continue  # the key notch
    S.box((0.045, 0.075, 0.32), (x, 0, z0 + 0.12), gold, 0.004, 2)

# Shroud on the front face, with a chamfered window showing the fin stack.
sh = Hc - 0.35          # shroud height; it spans x -5.05..4.85
wz = 1.35               # half-height of the fin window, which spans x 1.8..4.6
S.box((6.85, 0.9, sh), (-1.625, -0.5, cz + 0.08), shroud, 0.09, 6)
S.box((0.25, 0.9, sh), (4.725, -0.5, cz + 0.08), shroud, 0.05, 4)
rail = (sh / 2 - wz)
for sgn in (1, -1):
    S.box((2.8, 0.9, rail), (3.2, -0.5, cz + 0.08 + sgn * (wz + rail / 2)), shroud, 0.05, 4)
S.box((2.8, 0.05, 2 * wz), (3.2, -0.12, cz + 0.08), black)   # dark backing behind the fins
for i in range(36):
    S.box((0.024, 0.72, 2 * wz - 0.04), (1.86 + i * 0.077, -0.58, cz + 0.08), fin, 0.003, 2)
# fins also visible at the open end
for i in range(16):
    S.box((0.06, 0.8, 0.03), (L / 2 - 0.15, -0.5, z0 + 0.5 + i * 0.2), fin, 0.003, 2)

# Mark and laser-etched model line on the shroud.
S.mark((-2.7, -0.958, cz + 0.25), 1.15, mark_m, rot=(math.pi / 2, 0, 0), depth=0.012)
S.text("SPLICED  TRACE-1", (-2.7, -0.957, cz - 0.62), 0.14, laser, rot=(math.pi / 2, 0, 0))
for x in (-4.85, 4.65):
    for z in (z0 + 0.35, z0 + Hc - 0.2):
        S.screw((x, -0.97, z), steel, 0.05, axis="y")

# Bracket at the I/O end: a steel plate with vent slots and a mounting tab.
S.box((0.05, 1.3, Hc + 0.5), (-L / 2 - 0.05, -0.35, cz + 0.2), steel, 0.01)
for i in range(9):
    S.box((0.06, 0.95, 0.16), (-L / 2 - 0.08, -0.35, z0 + 0.7 + i * 0.36), black, 0.02, 2)
S.box((0.5, 1.3, 0.05), (-L / 2 + 0.2, -0.35, cz + Hc / 2 + 0.45), steel, 0.01)

# Power connector and a copper strip on the top edge.
S.box((0.85, 0.5, 0.38), (3.9, -0.3, z0 + Hc + 0.15), black, 0.03)
for i in range(6):
    S.box((0.08, 0.06, 0.1), (3.6 + i * 0.12, -0.3, z0 + Hc + 0.34), gold, 0.005, 2)
S.box((L - 1.4, 0.06, 0.04), (-0.4, 0.05, z0 + Hc - 0.02), copper, 0.005)

# Backplate.
S.box((L - 0.6, 0.06, Hc - 0.4), (0, 0.08, cz), shroud, 0.03)

S.area((-7, -9, 9), 900, 9)
S.area((8, -4, 4), 600, 5)
S.area((0, 8, 6), 400, 8)
S.camera((11.5, -21.0, 7.2), (0.2, 0, cz - 0.2), lens=55, fstop=9)
S.render(OUT)

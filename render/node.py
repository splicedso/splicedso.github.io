"""The node: a tiny complete computer in a Spliced shell: the same board and memory as the box we
measure (AMD RAH-001 class), in a narrow, deep, tall enclosure, 60 x 240 x 120 mm, so it breathes
front to back and stands six across in a tray. Intake grille on the narrow front, fins front to back,
two fans at the rear, ports at the rear; a badge on the front. The unit of every size:
alone on a desk, eight in a 2U tray, a hundred and forty in a rack. Badged. A concept.

    Blender -b -P render/node.py -- out.png [WxH] [--open | --tray | --rack | --row]
"""
import math, random, sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).parent))
import studio as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
W, H = (int(v) for v in (args[1] if len(args) > 1 and "x" in args[1] else "2400x1400").split("x"))
MODE = next((a[2:] for a in args if a in ("--open", "--grid", "--tray", "--rack", "--row")), "node")
random.seed(81)
sc = S.setup(W, H, hdri_strength=0.6)
S.floor(0.0)

from nodeparts import node, tray, rack, grid  # noqa: E402

if MODE == "node":
    node(0, 0, 0.15)
    S.camera((-14, -20, 9), (0, -1, 2.2), lens=65, fstop=8)
    S.area((-9, -12, 14), 2600, 7, (0, 0, 1)); S.area((11, -5, 8), 1100, 5, (0, 0, 1)); S.area((0, 11, 10), 800, 7, (0, 0, 1))
elif MODE == "open":
    node(0, 0, 0.15, open_top=True)
    S.camera((-13, -16, 9), (0, -0.5, 2.2), lens=60, fstop=9)
    S.area((-9, -12, 14), 2600, 7, (0, 0, 1)); S.area((11, -5, 8), 1100, 5, (0, 0, 1)); S.area((0, 11, 10), 800, 7, (0, 0, 1))
elif MODE == "grid":
    grid(0, 0, 0.15)
    S.camera((-22, -32, 15), (0, -1, 4.8), lens=60, fstop=9)
    S.area((-9, -12, 14), 2600, 7, (0, 0, 4)); S.area((11, -5, 8), 1100, 5, (0, 0, 4)); S.area((0, 11, 10), 800, 7, (0, 0, 4))
elif MODE == "tray":
    tray(0, 0, 0, ears=False)
    S.camera((-20, -32, 15), (0, -1, 2.4), lens=60, fstop=9)
    S.area((-24, -34, 36), 26000, 16, (0, 0, 2)); S.area((30, -16, 22), 11000, 12, (0, 0, 2)); S.area((0, 30, 26), 8000, 16, (0, 0, 2))
elif MODE == "rack":
    rack(0, 0)
    S.camera((-60, -140, 70), (0, -8, 40), lens=50, fstop=9)
    S.area((-50, -70, 80), 140000, 36, (0, 0, 40)); S.area((45, -30, 40), 40000, 20, (0, 0, 40)); S.area((0, 50, 60), 30000, 30, (0, 0, 40))
else:
    for i in range(6):
        rack(-5 * 26.0 / 2 + i * 26.0, 0, simple=True)
    S.camera((-150, -240, 100), (0, 0, 40), lens=45, fstop=10)
    S.area((-200, -260, 260), 1.6e6, 120, (0, 0, 40)); S.area((220, -120, 160), 7e5, 80, (0, 0, 40)); S.area((0, 200, 220), 5e5, 120, (0, 0, 40))
S.render(OUT)

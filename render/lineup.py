"""The family in one frame at relative scale, as Etched shows theirs: the package, the node, the tray
of six, the rack of eighty-four. One floor, one light, a long lens from the front.

    Blender -b -P render/lineup.py -- out.png [WxH]
"""
import math, sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).parent))
import studio as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
W, H = (int(v) for v in (args[1] if len(args) > 1 and "x" in args[1] else "2400x1200").split("x"))
sc = S.setup(W, H, samples=160, hdri_strength=0.6)
S.floor(0.0)
from nodeparts import node, tray, rack  # noqa: E402

lid = S.mat("lid", (0.66, 0.66, 0.64), metal=1.0, rough=0.2)
sub = S.pcb_mat("substrate", (0.012, 0.016, 0.014), scale=14.0)


def package(ox, k=5.0):
    # the package at k times its 32 mm, so it reads at all; the caption says so
    S.box((3.2 * k * 0.4, 3.2 * k * 0.4, 0.12 * k * 0.4), (ox, 0, 0.06 * k * 0.4), sub, 0.02)
    S.box((2.3 * k * 0.4, 2.3 * k * 0.4, 0.16 * k * 0.4), (ox, 0, 0.2 * k * 0.4), lid, 0.03, 6)
    S.mark((ox - 0.25 * k * 0.4, 0.15 * k * 0.4, 0.2805 * k * 0.4), 1.0 * k * 0.4, S.mat("etch", (0.03, 0.03, 0.03), metal=0.3, rough=0.5))


package(-84, k=7.0); node(-62, 0, 0.15); tray(-34, 0, 0, ears=False); rack(22, 0, simple=True)
S.area((-120, -200, 160), 1.4e6, 80, (-20, 0, 20))
S.area((120, -90, 90), 5e5, 50, (-20, 0, 20))
S.area((0, 120, 110), 2e5, 60, (-20, 0, 20))
S.camera((-32, -390, 74), (-28, 0, 40), lens=70, fstop=11)
S.render(OUT)

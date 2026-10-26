"""The family in one frame at relative scale, as Etched shows theirs: the package, the decode carrier,
the desk unit, the cell. Each is built by its own scene script's geometry; here they are placed on one
floor, scaled to true relative size, lit once, and shot from the front with a long lens.

    Blender -b -P render/lineup.py -- out.png [WxH]
"""
import math, sys, runpy
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).parent))
import studio as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
W, H = (int(v) for v in (args[1] if len(args) > 1 and "x" in args[1] else "2400x1200").split("x"))
sc = S.setup(W, H, samples=192, hdri_strength=0.6)
S.floor(0.0)

# Units: 1 = 25 mm for the desk and the cell; the carrier is the same part; the package is 1 unit = 1 mm in its
# own script, so a 32 mm package is 1.28 of these units: too small to see, so the lineup shows it at 4x with a note.
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
lid = S.mat("lid", (0.66, 0.66, 0.64), metal=1.0, rough=0.2)
sub = S.pcb_mat("substrate", (0.012, 0.016, 0.014), scale=14.0)


def package(ox, k=4.0):
    # the decode package at 4x: substrate, lid with the mark
    S.box((3.2 * k * 0.4, 3.2 * k * 0.4, 0.12 * k * 0.4), (ox, 0, 0.06 * k * 0.4), sub, 0.02)
    S.box((2.3 * k * 0.4, 2.3 * k * 0.4, 0.16 * k * 0.4), (ox, 0, 0.2 * k * 0.4), lid, 0.03, 6)
    S.mark((ox - 0.25 * k * 0.4, 0.15 * k * 0.4, 0.2805 * k * 0.4), 1.0 * k * 0.4, S.mat("etch", (0.03, 0.03, 0.03), metal=0.3, rough=0.5))


def carrier(ox):
    cx, cy, cz = ox, 0, 0
    S.box((10.6, 24.0, 0.5), (cx, cy, cz + 0.25), galv, 0.05)
    for sx in (-5.2, 5.2):
        S.box((0.4, 24.0, 16.0), (cx + sx, cy, cz + 8.2), galv, 0.05)
    S.box((9.4, 20.0, 0.4), (cx, cy, cz + 0.9), pcb, 0.05)
    S.box((5.0, 5.0, 0.9), (cx, cy - 4, cz + 1.6), S.mat("pkg", (0.02, 0.025, 0.02), rough=0.35, coat=0.3), 0.05)
    S.box((8.4, 20.0, 1.0), (cx, cy, cz + 2.6), cu, 0.05)
    for k in range(26):
        S.box((0.12, 20.0, 13.0), (cx - 3.9 + k * 0.31, cy, cz + 9.6), fin, 0.01)
    S.box((2.4, 0.5, 2.0), (cx, cy - 12.3, cz + 2.7), steel, 0.1)
    S.badge((cx - 2.2, cy - 12.1, cz + 5.0), 0.5, galv, dark, rot=(math.pi / 2, 0, 0), depth=0.06)


def desk(ox):
    UW, UD, UH = 12.8, 24.8, 11.2
    S.box((UW, UD, UH), (ox, 0, UH / 2 + 0.4), shell, 0.35, 6)
    S.box((UW - 1.6, 0.4, UH - 1.6), (ox, -UD / 2 - 0.1, UH / 2 + 0.4), mesh, 0.1)
    for i in range(int((UH - 2.4) / 0.9)):
        S.box((UW - 2.0, 0.15, 0.3), (ox, -UD / 2 - 0.25, 1.6 + i * 0.9), panel)
    S.badge((ox - 3.0, -UD / 2 - 0.45, UH - 1.1), 0.9, panel, inset, rot=(math.pi / 2, 0, 0), depth=0.12)


def cell(ox):
    CW, CD, CH, SK = 24.0, 120.0, 48.0, 4.0
    S.box((CW, CD, SK), (ox, 0, SK / 2), galv, 0.3)
    S.box((CW, CD, CH), (ox, 0, SK + CH / 2), shell, 0.5, 6)
    S.box((CW - 2, 1.2, CH - 2), (ox, -CD / 2 - 0.4, SK + CH / 2), panel, 0.3)
    S.box((CW - 6, 0.3, CH - 10), (ox, -CD / 2 - 1.05, SK + CH / 2 - 1), mesh, 0.1)
    for i in range(int((CH - 12) / 1.6)):
        S.box((CW - 7, 0.15, 0.35), (ox, -CD / 2 - 1.15, SK + 6 + i * 1.6), panel)
    S.box((1.0, 1.3, 14), (ox + CW / 2 - 3.2, -CD / 2 - 1.5, SK + CH / 2), steel, 0.3)
    S.badge((ox - 3.5, -CD / 2 - 1.35, SK + CH - 3.4), 1.6, panel, inset, rot=(math.pi / 2, 0, 0), depth=0.2)
    for sy in (-CD / 6, CD / 6):
        S.box((CW + 0.1, 0.25, CH + 0.1), (ox, sy, SK + CH / 2), dark)


# positions left to right, feet on the floor, fronts toward the camera
package(-92, k=6.0); carrier(-70); desk(-44); cell(10)
S.area((-120, -200, 160), 1.4e6, 80, (-40, 0, 20))
S.area((120, -90, 90), 5e5, 50, (-40, 0, 20))
S.area((0, 120, 110), 2e5, 60, (0, 0, 20))
S.camera((-40, -420, 70), (-40, 0, 24), lens=85, fstop=11)
S.render(OUT)

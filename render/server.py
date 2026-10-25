"""A photo-real 2U rack server, three-quarter view, studio-lit on a shadow-catcher floor.

Front: twelve 3.5-inch drive caddies (handle, two LEDs, honeycomb vent), rack ears with a
power button, status LEDs and USB ports, the Spliced mark on the bezel. Top: a lid with
panel seams and a service label.

    Blender -b -P render/server.py -- out.png [WxH]
"""
import math, random, sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).parent))
import studio as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
W, H = (int(v) for v in (args[1] if len(args) > 1 and "x" in args[1] else "2800x1600").split("x"))
random.seed(5)

sc = S.setup(W, H)
S.floor(0.0)

body = S.mat("body", (0.045, 0.045, 0.048), metal=0.7, rough=0.48, micro=0.1)
lid = S.mat("lid", (0.06, 0.06, 0.064), metal=0.75, rough=0.55, micro=0.14)
caddy = S.mat("caddy", (0.03, 0.03, 0.032), rough=0.45, micro=0.06)
handle = S.mat("handle", (0.55, 0.55, 0.55), metal=1.0, rough=0.3)
hole = S.mat("hole", (0.0, 0.0, 0.0), rough=0.9)
label = S.mat("label", (0.85, 0.85, 0.83), rough=0.6)
ink = S.mat("ink", (0.02, 0.02, 0.02), rough=0.5)
port = S.mat("port", (0.6, 0.6, 0.6), metal=1.0, rough=0.25)


def emit(name, color, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True
    e = m.node_tree.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (*color, 1); e.inputs["Strength"].default_value = strength
    m.node_tree.links.new(e.outputs[0], m.node_tree.nodes["Material Output"].inputs[0])
    return m


led_w = emit("led_w", (1, 1, 1), 8)
led_g = emit("led_g", (0.75, 1, 0.8), 5)

Wd, Dp, Hh = 8.0, 6.5, 1.48     # width, depth, height (2U, 19-inch proportions)
fy = -Dp / 2                     # front face
S.box((Wd, Dp, Hh), (0, 0, Hh / 2 + 0.01), body, 0.02)
# lid on top, with two seams and a service label
S.box((Wd - 0.06, Dp - 0.04, 0.03), (0, 0.0, Hh + 0.02), lid, 0.01)
for y in (-0.8, 1.6):
    S.box((Wd - 0.1, 0.012, 0.012), (0, y, Hh + 0.036), hole)
S.box((1.4, 0.9, 0.004), (2.2, 1.6 + 0.8, Hh + 0.037), label)
for i in range(5):
    S.box((1.1 - (i % 2) * 0.35, 0.05, 0.002), (2.1 - (i % 2) * 0.17, 2.75 - i * 0.14, Hh + 0.04), ink)

# rack ears
for side in (-1, 1):
    S.box((0.45, 0.12, Hh), (side * (Wd / 2 + 0.2), fy - 0.02, Hh / 2 + 0.01), body, 0.015)
    for z in (0.32, Hh - 0.32):
        S.screw((side * (Wd / 2 + 0.2), fy - 0.1, z), handle, 0.05, axis="y")
# left ear: power button and status LEDs; right ear: two USB ports
bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.04, location=(-Wd / 2 - 0.2, fy - 0.1, Hh / 2 + 0.15), rotation=(math.pi / 2, 0, 0), vertices=32)
bpy.context.object.data.materials.append(handle)
for k in range(3):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=0.02, location=(-Wd / 2 - 0.2, fy - 0.09, Hh / 2 - 0.12 - k * 0.1), rotation=(math.pi / 2, 0, 0), vertices=16)
    bpy.context.object.data.materials.append(led_g if k == 0 else hole)
for k in range(2):
    S.box((0.16, 0.05, 0.07), (Wd / 2 + 0.2, fy - 0.085, Hh / 2 + 0.12 - k * 0.16), port, 0.005)
    S.box((0.12, 0.06, 0.03), (Wd / 2 + 0.2, fy - 0.09, Hh / 2 + 0.12 - k * 0.16), hole)

# twelve drive caddies, 4 columns by 3 rows
cw, ch, gap = 1.88, 0.42, 0.05
for col in range(4):
    for row in range(3):
        x = -Wd / 2 + 0.12 + cw / 2 + col * (cw + gap)
        z = 0.14 + ch / 2 + row * (ch + gap)
        S.box((cw, 0.08, ch), (x, fy - 0.04, z), caddy, 0.012)
        S.box((cw * 0.62, 0.05, ch * 0.5), (x - cw * 0.12, fy - 0.075, z), hole, 0.004)   # vent field
        for v in range(10):
            for u in range(3):
                bpy.ops.mesh.primitive_cylinder_add(radius=0.028, depth=0.02, vertices=6,
                    location=(x - cw * 0.12 - cw * 0.27 + v * 0.06 + (0.03 if u % 2 else 0), fy - 0.1, z - 0.07 + u * 0.07),
                    rotation=(math.pi / 2, 0, 0))
                bpy.context.object.data.materials.append(caddy)
        S.box((0.42, 0.06, ch * 0.72), (x + cw * 0.36, fy - 0.1, z), handle, 0.015)        # release latch
        for k, m in enumerate((led_w if random.random() < 0.7 else hole, led_g)):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.016, depth=0.02, location=(x + cw * 0.36 + 0.24, fy - 0.11, z + 0.08 - k * 0.1), rotation=(math.pi / 2, 0, 0), vertices=12)
            bpy.context.object.data.materials.append(m)

# the mark, top right of the bezel
S.mark((Wd / 2 - 0.55, fy - 0.081, Hh - 0.07), 0.12, label, rot=(math.pi / 2, 0, 0))

S.area((-7, -9, 9), 800, 9, (0, 0, 0.6))
S.area((9, -5, 4), 500, 5, (0, 0, 0.6))
S.area((0, 9, 7), 350, 8, (0, 0, 0.6))
S.camera((-17.5, -27.5, 12.0), (0.3, -0.4, 0.5), lens=100, fstop=4.5)
if "--turntable" in args:
    S.turntable(OUT, int(args[args.index("--turntable") + 1]), sway=28)
else:
    S.render(OUT)

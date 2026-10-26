"""A design concept, v2: the portable datacenter cell, air cooled, drawn as parts.

Proportions of an accelerator card lying flat: 0.6 m wide, 1.2 m tall, 3.0 m deep, on a skid. Air
enters through the whole front face (a filtered intake grille), passes a fan wall, flows front to
back over six decode modules on cold plates and one prefill module, and leaves through the rear
face; the long sides carry the docks and are closed. Every part is a named object in its own
collection, so the same script exports STL per part at 1:10 (--parts) and draws the schematic
views (render/cell_drawings.py). Unbranded except the mark. A concept, not a product.

    Blender -b -P render/cell.py -- out.png [WxH] [--row] [--open] [--parts DIR]
"""
import math, random, sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).parent))
import studio as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
W, H = (int(v) for v in (args[1] if len(args) > 1 and "x" in args[1] else "2800x1600").split("x"))
ROW = "--row" in args
OPEN = "--open" in args                     # doors and the near side panel removed, internals visible
PARTS = args[args.index("--parts") + 1] if "--parts" in args else None
random.seed(51)
sc = S.setup(W, H, hdri_strength=0.6)
S.floor(0.0)

shell = S.scuffed("shell", (0.04, 0.04, 0.042), metal=0.5, rough=0.55)
panel = S.scuffed("panel", (0.06, 0.06, 0.063), metal=0.5, rough=0.5)
steel = S.scuffed("steel", (0.6, 0.6, 0.58), metal=1.0, rough=0.35)
galv = S.scuffed("galv", (0.5, 0.5, 0.5), metal=1.0, rough=0.5)
dark = S.mat("dark", (0.0, 0.0, 0.0), rough=0.9)
collar = S.mat("collar", (0.85, 0.45, 0.1), rough=0.5)
cu = S.mat("cu", (0.86, 0.52, 0.34), metal=1.0, rough=0.3)
fin = S.mat("fin", (0.72, 0.72, 0.7), metal=1.0, rough=0.4)
pcb = S.pcb_mat("pcb", (0.008, 0.022, 0.014))
mesh = S.mat("mesh", (0.08, 0.08, 0.085), metal=0.6, rough=0.7)
inset = S.mat("inset", (0.75, 0.75, 0.74), metal=1.0, rough=0.35)
led = bpy.data.materials.new("led"); led.use_nodes = True
e = led.node_tree.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (0.6, 1.0, 0.7, 1); e.inputs["Strength"].default_value = 5
led.node_tree.links.new(e.outputs[0], led.node_tree.nodes["Material Output"].inputs[0])

# 1 unit = 25 mm. Width 0.6 m, depth 3.0 m, height 1.2 m above a 0.1 m skid.
CW, CD, CH, SK = 24.0, 120.0, 48.0, 4.0
# the air path, front (y = -CD/2) to back (y = +CD/2):
#   intake grille 0 to 3 | filter 3 to 5 | fan wall 5 to 11 | plenum | module bay 14 to 100 | exhaust 100 to 120
Y_FAN0, Y_FAN1, Y_BAY0, Y_BAY1 = -CD / 2 + 5, -CD / 2 + 11, -CD / 2 + 14, -CD / 2 + 100


def part(name):
    """Put every object created after this call into a collection named `name` (one part for the STL export)."""
    col = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if col.name not in [c.name for c in sc.collection.children]:
        sc.collection.children.link(col)
    before = set(o.name for o in sc.objects)
    def done():
        for o in sc.objects:
            if o.name not in before and o.type == "MESH" and col not in o.users_collection:
                for c in o.users_collection:
                    c.objects.unlink(o)
                col.objects.link(o)
    return done


def cell(ox, docked_left=False, docked_right=False, open_side=False):
    # --- skid
    d = part("skid")
    S.box((CW, CD, SK), (ox, 0, SK / 2), galv, 0.3)
    for py in (-40, 0, 40):
        S.box((CW + 0.2, 6.0, 2.2), (ox, py, 1.6), dark)
    d()
    # --- frame: four longitudinal rails and cross members, the structure every panel bolts to
    d = part("frame")
    for x in (-CW / 2 + 0.8, CW / 2 - 0.8):
        for z in (SK + 0.8, SK + CH - 0.8):
            S.box((1.6, CD - 2, 1.6), (ox + x, 0, z), steel, 0.1)
    for y in (-CD / 2 + 1, Y_FAN0, Y_FAN1, Y_BAY0, Y_BAY1, CD / 2 - 1):
        for z in (SK + 0.8, SK + CH - 0.8):
            S.box((CW - 1.6, 1.6, 1.6), (ox, y, z), steel, 0.1)
        for x in (-CW / 2 + 0.8, CW / 2 - 0.8):
            S.box((1.6, 1.6, CH - 3.2), (ox + x, y, SK + CH / 2), steel, 0.1)
    d()
    # --- side panels: closed, with the docks; the near one is left off when open_side
    for side, docked in ((-1, docked_left), (1, docked_right)):
        if open_side and side == -1:
            continue
        d = part(f"side-{'left' if side < 0 else 'right'}")
        x = ox + side * (CW / 2 + 0.3)
        S.box((0.6, CD - 2, CH - 2), (x, 0, SK + CH / 2), shell, 0.2)
        for sy in (-CD / 6, CD / 6):
            S.box((0.7, 0.25, CH - 2), (x, sy, SK + CH / 2), dark)
        for sy in range(-int(CD / 2) + 8, int(CD / 2) - 6, 10):
            for sz in (SK + 2.5, SK + CH - 2.5):
                S.screw((ox + side * (CW / 2 + 0.62), sy, sz), steel, 0.35, axis="x")
        S.box((0.6, 30, 22), (x + side * 0.3, CD / 4, SK + 18), panel, 0.2)          # dock plate
        if not docked:
            for cy in (CD / 4 - 8, CD / 4 - 4):
                bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=1.6, location=(x + side * 1.1, cy, SK + 12), rotation=(0, math.pi / 2, 0), vertices=24)
                bpy.context.object.data.materials.append(steel)
                bpy.ops.mesh.primitive_cylinder_add(radius=1.25, depth=0.5, location=(x + side * 1.8, cy, SK + 12), rotation=(0, math.pi / 2, 0), vertices=24)
                bpy.context.object.data.materials.append(collar)
            S.box((0.4, 6, 3), (x + side * 0.7, CD / 4 + 4, SK + 12), dark, 0.1)
            for i in range(4):
                S.box((0.3, 0.9, 0.9), (x + side * 0.8, CD / 4 + 1.8 + i * 1.4, SK + 12), steel, 0.05)
            S.box((0.5, 10, 4), (x + side * 0.7, CD / 4 + 10, SK + 24), dark, 0.2)
            for by in (CD / 4 + 7.5, CD / 4 + 12.5):
                S.box((0.6, 1.8, 2.4), (x + side * 0.8, by, SK + 24), cu, 0.1)
        d()
    # --- top and bottom skins
    d = part("top")
    S.box((CW + 0.6, CD, 0.6), (ox, 0, SK + CH + 0.3), shell, 0.2)
    for ey in (-CD / 2 + 8, CD / 2 - 8):
        for ex in (-CW / 2 + 4, CW / 2 - 4):
            bpy.ops.mesh.primitive_torus_add(major_radius=0.8, minor_radius=0.22, location=(ox + ex, ey, SK + CH + 0.9), rotation=(math.pi / 2, 0, 0))
            bpy.context.object.data.materials.append(steel)
    d()
    d = part("floor"); S.box((CW, CD - 2, 0.6), (ox, 0, SK + 0.3), galv, 0.1); d()
    # --- front: the intake door, a full-face filtered grille with a hinged frame, the mark above the handle
    if not OPEN:
        d = part("door-front")
        S.box((CW - 2, 1.2, CH - 2), (ox, -CD / 2 - 0.4, SK + CH / 2), panel, 0.3)
        S.box((CW - 6, 0.3, CH - 10), (ox, -CD / 2 - 1.05, SK + CH / 2 - 1), mesh, 0.1)        # the grille
        for i in range(int((CH - 12) / 1.6)):
            S.box((CW - 7, 0.15, 0.35), (ox, -CD / 2 - 1.15, SK + 6 + i * 1.6), panel)        # louvres
        S.box((1.0, 1.3, 14), (ox + CW / 2 - 3.2, -CD / 2 - 1.5, SK + CH / 2), steel, 0.3)   # handle
        S.badge((ox - 3.5, -CD / 2 - 1.35, SK + CH - 3.4), 1.6, panel, inset, rot=(math.pi / 2, 0, 0), depth=0.2)
        S.box((6, 0.3, 3.2), (ox + 6, -CD / 2 - 1.2, SK + CH - 3.2), dark, 0.1)                # status window
        bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.2, location=(ox + 4, -CD / 2 - 1.35, SK + CH - 3.2), rotation=(math.pi / 2, 0, 0), vertices=12)
        bpy.context.object.data.materials.append(led)
        d()
    # --- fan wall: 2 x 4 fans in a plate, between the filter and the plenum
    d = part("fan-wall")
    S.box((CW - 2, 0.6, CH - 2), (ox, Y_FAN0 + 3, SK + CH / 2), panel, 0.1)
    for i in range(2):
        for j in range(4):
            cx, cz = ox - CW / 4 + i * CW / 2, SK + 6 + j * (CH - 12) / 3
            bpy.ops.mesh.primitive_cylinder_add(radius=4.6, depth=5.5, location=(cx, Y_FAN0 + 3, cz), rotation=(math.pi / 2, 0, 0), vertices=40)
            bpy.context.object.data.materials.append(dark)
            bpy.ops.mesh.primitive_cylinder_add(radius=1.6, depth=5.6, location=(cx, Y_FAN0 + 3, cz), rotation=(math.pi / 2, 0, 0), vertices=24)
            bpy.context.object.data.materials.append(panel)
            for k in range(7):                                                               # blades
                a = k * 2 * math.pi / 7
                S.box((4.0, 0.25, 1.4), (cx + 2.4 * math.cos(a), Y_FAN0 + 3, cz + 2.4 * math.sin(a)), panel, 0.05, rot=(0, -a, 0.5))
    d()
    # --- module bay: decode modules in pull-out carriers, two columns by three rows by two tiers (12),
    # each carrier a tray with the board, a ducted fin stack running front to back, and a pull handle;
    # the tiers are a shelf so the upper six sit in the same airflow lanes as the lower six
    carriers = 0
    for tier in range(2):
        cz = SK + 3 + tier * 20
        if tier:
            d = part("tier-shelf"); S.box((CW - 3, Y_BAY1 - Y_BAY0 - 2, 0.6), (ox, (Y_BAY0 + Y_BAY1) / 2, cz - 1.2), steel, 0.1); d()
        for col_i, cx in enumerate((ox - 5.6, ox + 5.6)):
            for row_i in range(3):
                d = part(f"carrier-{carriers}"); carriers += 1
                cy = Y_BAY0 + 14 + row_i * 27
                S.box((10.6, 24.0, 0.5), (cx, cy, cz), galv, 0.05)                                  # tray
                for sx in (-5.2, 5.2):
                    S.box((0.4, 24.0, 16.0), (cx + sx, cy, cz + 8), galv, 0.05)                      # duct walls: air stays over the fins
                S.box((9.4, 20.0, 0.4), (cx, cy, cz + 0.7), pcb, 0.05)                              # module board
                S.box((5.0, 5.0, 0.9), (cx, cy - 4, cz + 1.4), S.mat("pkg", (0.02, 0.025, 0.02), rough=0.35, coat=0.3), 0.05)
                S.box((8.4, 20.0, 1.0), (cx, cy, cz + 2.4), cu, 0.05)                               # vapour chamber the length of the tray
                for k in range(26):
                    S.box((0.12, 20.0, 13.0), (cx - 3.9 + k * 0.31, cy, cz + 9.4), fin, 0.01)       # fins front to back, full length
                S.box((2.4, 0.5, 2.0), (cx, cy - 12.3, cz + 2.5), steel, 0.1)                       # pull handle on the front edge
                S.badge((cx - 2.2, cy - 12.1, cz + 5.0), 0.5, galv, dark, rot=(math.pi / 2, 0, 0), depth=0.06)
                bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.2, location=(cx + 4, cy - 12.1, cz + 1.5), rotation=(math.pi / 2, 0, 0), vertices=10)
                bpy.context.object.data.materials.append(led)
                S.silkscreen(cx, cy + 6, cz + 0.91, 8.6, 6, n=14, seed=carriers, keep_out=None)
                d()
    # --- prefill module: one tall fin stack at the back of the bay, full width, own carrier
    d = part("prefill")
    cy = Y_BAY1 - 9; cz = SK + 3
    S.box((20.0, 16.0, 0.5), (ox, cy, cz), galv, 0.05)
    S.box((19.0, 15.0, 0.4), (ox, cy, cz + 0.7), pcb, 0.05)
    S.box((7.0, 6.0, 1.0), (ox, cy - 2, cz + 1.4), S.mat("pkg2", (0.02, 0.025, 0.02), rough=0.35, coat=0.3), 0.05)
    S.box((14.0, 13.0, 1.2), (ox, cy, cz + 2.5), cu, 0.05)
    for k in range(46):
        S.box((0.12, 13.0, 36.0), (ox - 6.9 + k * 0.3, cy, cz + 21), fin, 0.01)
    S.silkscreen(ox, cy + 6, cz + 0.91, 18, 3, n=24, seed=77, keep_out=None)
    d()
    # --- host and switch: a shelf on the left wall above the bay, in the exhaust stream
    d = part("host-shelf")
    S.box((CW - 4, 14.0, 0.6), (ox, Y_BAY1 + 8, SK + CH - 4.5), steel, 0.1)                  # shelf across the exhaust plenum
    S.box((8.0, 12.0, 3.2), (ox - 5.5, Y_BAY1 + 8, SK + CH - 2.5), panel, 0.2)                  # host
    S.box((8.0, 12.0, 3.2), (ox + 5.5, Y_BAY1 + 8, SK + CH - 2.5), panel, 0.2)                  # switch
    for k in range(16):
        S.box((0.42, 0.1, 0.5), (ox + 2.0 + k * 0.45, Y_BAY1 + 1.9, SK + CH - 2.3), dark, 0.02)
    d()
    # --- busbar tap and DC stage: right wall, rear
    d = part("power")
    S.box((3.0, 20.0, 8.0), (ox + CW / 2 - 3, Y_BAY1 - 14, SK + CH - 8), panel, 0.2)
    for by in (Y_BAY1 - 20, Y_BAY1 - 8):
        S.box((0.8, 2.0, 2.4), (ox + CW / 2 - 0.8, by, SK + 24), cu, 0.1)
    d()
    # --- rear: exhaust face, a grille the full height, the drain below
    d = part("door-rear")
    if not OPEN:
        S.box((CW - 2, 1.2, CH - 2), (ox, CD / 2 + 0.4, SK + CH / 2), panel, 0.3)
        S.box((CW - 5, 0.3, CH - 8), (ox, CD / 2 + 1.05, SK + CH / 2), mesh, 0.1)
        for i in range(int((CH - 10) / 1.6)):
            S.box((CW - 6, 0.15, 0.35), (ox, CD / 2 + 1.15, SK + 5 + i * 1.6), panel)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=1.0, location=(ox + 6, CD / 2 + 0.4, 1.0), rotation=(math.pi / 2, 0, 0), vertices=16)
    bpy.context.object.data.materials.append(steel)
    d()


if PARTS:
    cell(0)
    import os
    os.makedirs(PARTS, exist_ok=True)
    for col in sc.collection.children:
        bpy.ops.object.select_all(action="DESELECT")
        for o in col.objects:
            o.select_set(True)
        if not col.objects:
            continue
        bpy.ops.wm.stl_export(filepath=os.path.join(PARTS, f"{col.name}.stl"), export_selected_objects=True, global_scale=2.5)   # 1 unit = 25 mm; at 1:10, 2.5 mm
    print("exported", len(sc.collection.children), "parts to", PARTS)
    sys.exit(0)

if ROW:
    N = 8
    for i in range(N):
        cell(-(N - 1) * (CW + 0.6) / 2 + i * (CW + 0.6), docked_left=i > 0, docked_right=i < N - 1)
    S.area((-200, -260, 260), 1.6e6, 120, (0, 0, 50))
    S.area((220, -120, 160), 7e5, 80, (0, 0, 50))
    S.area((0, 200, 220), 5e5, 120, (0, 0, 50))
    S.camera((-230, -300, 120), (0, -30, 26), lens=45, fstop=10)
else:
    cell(0, open_side=OPEN)
    S.area((-90, -120, 150), 5e5, 60, (0, 0, 50))
    S.area((120, -60, 90), 2.2e5, 40, (0, 0, 50))
    S.area((0, 110, 120), 1.5e5, 60, (0, 0, 50))
    if OPEN:
        S.camera((-150, -150, 90), (0, -5, 24), lens=50, fstop=11)
    else:
        S.camera((-120, -190, 70), (0, -10, 26), lens=55, fstop=10)
S.render(OUT)

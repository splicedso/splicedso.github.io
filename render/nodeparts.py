"""The node family's geometry, shared by render/node.py and render/lineup.py: materials, the node,
the 3U tray of six, the 42U rack of fourteen trays. Import after studio.setup() has made a scene."""
import math
import bpy
import studio as S

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
rubber = S.mat("rubber", (0.03, 0.03, 0.03), rough=0.8)
led = bpy.data.materials.new("led"); led.use_nodes = True
e = led.node_tree.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (0.6, 1.0, 0.7, 1); e.inputs["Strength"].default_value = 5
led.node_tree.links.new(e.outputs[0], led.node_tree.nodes["Material Output"].inputs[0])

# 1 unit = 25 mm. Node: 2.4 wide x 9.6 deep x 4.8 tall (60 x 240 x 120 mm).
NW, ND, NH = 2.4, 9.6, 4.8


def node(ox, oy, oz, open_top=False, feet=True, badge=True):
    """One node: a narrow deep tall shell; front intake, fins front to back, two rear fans, rear ports."""
    if not open_top:
        S.box((NW, ND, NH), (ox, oy, oz + NH / 2), shell, 0.16, 6)
        S.box((NW + 0.05, 0.1, NH + 0.05), (ox, oy + ND / 2 - 2.6, oz + NH / 2), dark)             # a seam where the rear cap meets the shell
    else:
        # the near side wall off: floor, far wall, front and rear caps, and the internals
        S.box((NW, ND, 0.12), (ox, oy, oz + 0.06), shell, 0.04)
        S.box((0.12, ND, NH), (ox + NW / 2 - 0.06, oy, oz + NH / 2), shell, 0.04)
        S.box((NW, 0.12, NH), (ox, oy - ND / 2 + 0.06, oz + NH / 2), shell, 0.04)
        S.box((NW, 0.12, NH), (ox, oy + ND / 2 - 0.06, oz + NH / 2), shell, 0.04)
        # board stands on edge against the far wall; package and heatsink face the open side, fins run front to back
        S.box((0.12, 8.0, 4.0), (ox + NW / 2 - 0.3, oy - 0.2, oz + NH / 2), pcb, 0.02)
        S.box((0.3, 1.6, 1.6), (ox + NW / 2 - 0.5, oy - 1.5, oz + NH / 2), S.mat("pkg", (0.02, 0.025, 0.02), rough=0.35, coat=0.3), 0.02)
        S.box((0.25, 6.0, 3.6), (ox + NW / 2 - 0.78, oy - 0.6, oz + NH / 2), cu, 0.02)
        for k in range(16):
            S.box((1.0, 6.0, 0.05), (ox + NW / 2 - 1.4, oy - 0.6, oz + 0.7 + k * 0.23), fin, 0.003)   # fins: horizontal plates, air flows along them front to back
        S.box((0.08, 1.6, 0.6), (ox + NW / 2 - 0.2, oy + 3.0, oz + 1.2), dark, 0.01)               # NVMe
        for k in range(2):                                                                         # memory
            S.box((0.08, 0.7, 1.4), (ox + NW / 2 - 0.2, oy - 3.6 + k * 0.9, oz + NH / 2), dark, 0.01)
        for fz in (NH * 0.3, NH * 0.7):                                                            # two rear fans, stacked
            bpy.ops.mesh.primitive_cylinder_add(radius=0.95, depth=0.5, location=(ox, oy + ND / 2 - 0.5, oz + fz), rotation=(math.pi / 2, 0, 0), vertices=32)
            bpy.context.object.data.materials.append(dark)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.55, location=(ox, oy + ND / 2 - 0.5, oz + fz), rotation=(math.pi / 2, 0, 0), vertices=16)
            bpy.context.object.data.materials.append(panel)
            for k in range(7):
                a = k * 2 * math.pi / 7
                S.box((0.75, 0.08, 0.28), (ox + 0.55 * math.cos(a), oy + ND / 2 - 0.5, oz + fz + 0.55 * math.sin(a)), panel, 0.01, rot=(0, -a, 0.5))
    # front: a grille the full narrow face with the badge above it, the light at the top
    S.box((NW - 0.5, 0.08, NH - 1.6), (ox, oy - ND / 2 - 0.02, oz + NH / 2 - 0.5), mesh, 0.02)
    for i in range(int((NH - 2.0) / 0.26)):
        S.box((NW - 0.7, 0.05, 0.1), (ox, oy - ND / 2 - 0.06, oz + 0.5 + i * 0.26), panel)
    if badge:
        S.badge((ox, oy - ND / 2 - 0.05, oz + NH - 0.75), 0.24, panel, inset, rot=(math.pi / 2, 0, 0), depth=0.04, wordmark=False)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.08, location=(ox + NW / 2 - 0.35, oy - ND / 2 - 0.03, oz + NH - 0.3), rotation=(math.pi / 2, 0, 0), vertices=12)
    bpy.context.object.data.materials.append(led)
    # rear: exhaust grille over the fans, ports in a column beside it
    S.box((NW - 0.5, 0.08, NH - 0.6), (ox, oy + ND / 2 + 0.02, oz + NH / 2), mesh, 0.02)
    for i in range(int((NH - 0.9) / 0.26)):
        S.box((NW - 1.2, 0.05, 0.1), (ox - 0.3, oy + ND / 2 + 0.06, oz + 0.45 + i * 0.26), panel)
    for i, (w, h) in enumerate(((0.34, 0.14), (0.34, 0.14), (0.34, 0.14), (0.34, 0.14), (0.6, 0.45), (0.6, 0.2))):   # four USB-C, 10GbE, HDMI
        S.box((w, 0.1, h), (ox + NW / 2 - 0.45, oy + ND / 2 + 0.03, oz + 0.5 + i * 0.7), dark, 0.01)
    # docks: a recessed blind-mate connector with two alignment pins on each side face and on the top and
    # bottom, so nodes join side by side and stacked into a 2 x 2 grid (or a 2 x 1, or 1 x 2) without a cable;
    # power passes through, the link is a 10GbE pair. They sit on closed faces, so the air path is untouched.
    for side in (-1, 1):
        x = ox + side * (NW / 2 + 0.01)
        S.box((0.08, 1.6, 0.8), (x, oy + 1.0, oz + NH / 2), dark, 0.02)
        S.box((0.05, 1.2, 0.4), (x + side * 0.03, oy + 1.0, oz + NH / 2), S.mat("gold", (0.95, 0.72, 0.38), metal=1.0, rough=0.25), 0.01)
        for py in (-1.2, 3.2):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.08, location=(x + side * 0.02, oy + py, oz + NH / 2), rotation=(0, math.pi / 2, 0), vertices=12)
            bpy.context.object.data.materials.append(steel)
    for top in (0, 1):
        z = oz + (NH + 0.01 if top else -0.01)
        S.box((1.0, 1.6, 0.08), (ox, oy + 1.0, z), dark, 0.02)
        for py in (-1.2, 3.2):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.08, location=(ox, oy + py, z), vertices=12)
            bpy.context.object.data.materials.append(steel)
    if feet:
        for x, y in ((-0.8, -3.6), (0.8, -3.6), (-0.8, 3.6), (0.8, 3.6)):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.12, location=(ox + x, oy + y, oz - 0.06), vertices=16)
            bpy.context.object.data.materials.append(rubber)


# 19-inch 3U tray (133 mm) holds the 120 mm node standing; six across at 60 mm with 12 mm gaps in the 443 mm width,
# one row deep. Every node breathes front to back on its own; a fan plate at the rear pulls the plenum out. 14 trays,
# 84 nodes, in a 42U rack.
TW, TH, TD = 17.7, 5.25, 12.0


def tray(ox, oy, oz, ears=True):
    S.box((TW, TD, 0.15), (ox, oy, oz + 0.08), galv, 0.03)
    for sx in (-TW / 2 + 0.08, TW / 2 - 0.08):
        S.box((0.15, TD, TH), (ox + sx, oy, oz + TH / 2), galv, 0.03)
    if ears:
        for sx in (-TW / 2 - 0.9, TW / 2 + 0.9):
            S.box((1.8, 0.2, TH), (ox + sx, oy - TD / 2 + 0.1, oz + TH / 2), steel, 0.03)
            for z in (0.7, TH - 0.7):
                S.screw((ox + sx, oy - TD / 2 - 0.02, oz + z), steel, 0.22, axis="y")
    # the nodes, fronts toward the camera, in two rows: the rear row is reached by sliding the tray out
    for c in range(6):
        node(ox - TW / 2 + 0.55 + NW / 2 + c * (NW + 0.5), oy - TD / 2 + 0.8 + ND / 2, oz + 0.2, feet=False)
    # a fan plate at the rear, the full height of the tray, three 60 mm fans in it, pulling the plenum out
    S.box((TW - 0.4, 0.3, TH - 0.3), (ox, oy + TD / 2 - 0.5, oz + TH / 2), panel, 0.03)
    for i in range(3):
        fx = ox - 5.4 + i * 5.4
        bpy.ops.mesh.primitive_cylinder_add(radius=1.9, depth=0.9, location=(fx, oy + TD / 2 - 0.5, oz + TH / 2), rotation=(math.pi / 2, 0, 0), vertices=32)
        bpy.context.object.data.materials.append(dark)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.95, location=(fx, oy + TD / 2 - 0.5, oz + TH / 2), rotation=(math.pi / 2, 0, 0), vertices=16)
        bpy.context.object.data.materials.append(panel)
        for k in range(7):
            a = k * 2 * math.pi / 7
            S.box((1.0, 0.1, 0.35), (fx + 0.7 * math.cos(a), oy + TD / 2 - 0.5, oz + TH / 2 + 0.7 * math.sin(a)), panel, 0.02, rot=(0, -a, 0.5))
    # power distribution at the rear left corner, cables to each node implied; the tray badge low on the front left side wall
    S.badge((ox - TW / 2 + 0.2, oy - TD / 2 + 1.0, oz + 1.0), 0.22, galv, dark, rot=(math.pi / 2, 0, math.pi / 2), depth=0.03)


def node_simple(ox, oy, oz):
    """A far-view node: the shell, a grille and a light, nothing that needs text or many parts."""
    S.box((NW, ND, NH), (ox, oy, oz + NH / 2), shell, 0.16, 3)
    S.box((NW - 0.5, 0.08, NH - 1.6), (ox, oy - ND / 2 - 0.02, oz + NH / 2 - 0.5), mesh, 0.02)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.08, location=(ox + NW / 2 - 0.35, oy - ND / 2 - 0.03, oz + NH - 0.3), rotation=(math.pi / 2, 0, 0), vertices=8)
    bpy.context.object.data.materials.append(led)


def tray_simple(ox, oy, oz):
    S.box((TW, TD, 0.15), (ox, oy, oz + 0.08), galv, 0.03)
    for sx in (-TW / 2 + 0.08, TW / 2 - 0.08):
        S.box((0.15, TD, TH), (ox + sx, oy, oz + TH / 2), galv, 0.03)
    for sx in (-TW / 2 - 0.9, TW / 2 + 0.9):
        S.box((1.8, 0.2, TH), (ox + sx, oy - TD / 2 + 0.1, oz + TH / 2), steel, 0.03)
    for c in range(6):
        node_simple(ox - TW / 2 + 0.55 + NW / 2 + c * (NW + 0.5), oy - TD / 2 + 0.8 + ND / 2, oz + 0.2)


def rack(ox, oy, trays=14, simple=False):
    RW, RD, RH, U = 24.0, 48.0, 80.0, 1.75
    for x in (-RW / 2, RW / 2):
        for y in (-RD / 2, RD / 2):
            S.box((1.2, 1.2, RH), (ox + x, oy + y, RH / 2), shell, 0.06)
    S.box((RW + 1.2, RD + 1.2, 1.0), (ox, oy, RH + 0.5), shell, 0.06)
    S.box((RW + 1.2, RD + 1.2, 1.6), (ox, oy, 0.8), shell, 0.06)
    for x in (-RW / 2 - 0.3, RW / 2 + 0.3):
        S.box((0.6, RD, RH - 2.0), (ox + x, oy, RH / 2), panel, 0.04)
    z = 1.6
    S.box((RW - 2.4, RD - 4, 2 * U - 0.1), (ox, oy, z + U), panel, 0.05)                           # power shelf
    z += 2 * U + 0.2
    for i in range(trays):
        (tray_simple if simple else tray)(ox, oy - RD / 2 + TD / 2 + 2, z + i * (3 * U + 0.05)) if simple else tray(ox, oy - RD / 2 + TD / 2 + 2, z + i * (3 * U + 0.05), ears=True)
    z += trays * (3 * U + 0.05) + 0.2
    S.box((RW - 2.4, RD - 4, U - 0.1), (ox, oy, z + U / 2), panel, 0.05)                           # switch
    for i in range(32):
        S.box((0.42, 0.1, 0.5), (ox - RW / 2 + 2.2 + i * 0.6, oy - RD / 2 + 1.98, z + U / 2), dark, 0.02)
    z += U + 0.2
    while z < RH - 2.5:
        S.box((RW - 2.4, 0.3, 2 * U - 0.2), (ox, oy - RD / 2 + 1.9, z + U), panel, 0.04); z += 2 * U + 0.1




def grid(ox, oy, oz, cols=2, rows=2):
    """Nodes docked into a cols x rows grid: side by side on their docks, stacked on their top docks."""
    for r in range(rows):
        for c in range(cols):
            node(ox - (cols - 1) * (NW + 0.02) / 2 + c * (NW + 0.02), oy, oz + r * (NH + 0.02), feet=(r == 0))

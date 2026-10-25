"""A photo-real inference server tray with braided cables, isolated (Cycles, transparent film).

A 2U chassis in bead-blasted dark metal, a perforated front grille, a nameplate with the
Spliced mark, and a row of braided cables looping down out of the bottom.

    Blender -b -P render/tray.py -- out.png [WxH]
"""
import math, random, sys
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
W, H = (int(v) for v in (args[1] if len(args) > 1 and "x" in args[1] else "2800x1600").split("x"))
random.seed(11)

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import studio as S  # noqa: E402
sc = S.setup(W, H, hdri_strength=0.3)

def principled(name, color, metal=0.0, rough=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metal; p.inputs["Roughness"].default_value = rough
    return m, p


# Bead-blasted metal: fine noise in roughness and a little in the bump.
chassis, p = principled("chassis", (0.018, 0.018, 0.02), metal=0.6, rough=0.55)
nt = chassis.node_tree
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900; nz.inputs["Detail"].default_value = 2
bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08
nt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])

# Braided sleeve: a woven pattern from two crossed wave textures along the cable's length.
braid, p = principled("braid", (0.03, 0.03, 0.032), rough=0.72)
p.inputs["Sheen Weight"].default_value = 0.08; p.inputs["Sheen Roughness"].default_value = 0.6
nt = braid.node_tree
tc = nt.nodes.new("ShaderNodeTexCoord")
# Woven PET sleeve: two sets of fine diagonal strands in object space, crossed, with fibre noise.
waves = []
for rot in (0.75, -0.75):
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (rot, 0, 0); mp.inputs["Scale"].default_value = (1, 1, 1)
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 55; wv.wave_type = "BANDS"; wv.bands_direction = "Z"
    wv.inputs["Distortion"].default_value = 0.6
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], wv.inputs["Vector"])
    waves.append(wv)
mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MAXIMUM"
nt.links.new(waves[0].outputs["Fac"], mul.inputs[0]); nt.links.new(waves[1].outputs["Fac"], mul.inputs[1])
fib = nt.nodes.new("ShaderNodeTexNoise"); fib.inputs["Scale"].default_value = 400; fib.inputs["Detail"].default_value = 8
nt.links.new(tc.outputs["Object"], fib.inputs["Vector"])
h = nt.nodes.new("ShaderNodeMath"); h.operation = "MULTIPLY_ADD"; h.inputs[2].default_value = 0.0
nt.links.new(fib.outputs["Fac"], h.inputs[0]); h.inputs[1].default_value = 0.25
hs = nt.nodes.new("ShaderNodeMath"); hs.operation = "ADD"
nt.links.new(mul.outputs[0], hs.inputs[0]); nt.links.new(h.outputs[0], hs.inputs[1])
col = nt.nodes.new("ShaderNodeMix"); col.data_type = "RGBA"
col.inputs["A"].default_value = (0.003, 0.003, 0.0035, 1); col.inputs["B"].default_value = (0.03, 0.03, 0.032, 1)
nt.links.new(hs.outputs[0], col.inputs["Factor"]); nt.links.new(col.outputs["Result"], p.inputs["Base Color"])
bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.7; bump.inputs["Distance"].default_value = 0.01
nt.links.new(hs.outputs[0], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])

steel, _ = principled("steel", (0.6, 0.6, 0.6), metal=1.0, rough=0.28)
plate, _ = principled("plate", (0.82, 0.82, 0.8), metal=1.0, rough=0.35)
ink, _ = principled("ink", (0.02, 0.02, 0.02), rough=0.4)
dark, _ = principled("dark", (0.02, 0.02, 0.02), rough=0.7)


def box(size, loc, m, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 5
        o.modifiers.new("w", "WEIGHTED_NORMAL")
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return o


# Chassis: two stacked 1U trays, the top one set slightly back, like a pulled-out unit.
box((8.0, 4.0, 0.9), (0, 0, 1.5), chassis, 0.03)
box((8.0, 4.0, 0.9), (0, -0.25, 0.55), chassis, 0.03)
box((0.35, 4.3, 2.6), (-4.2, 0, 0.9), chassis, 0.03)   # rack ears / rails
box((0.35, 4.3, 2.6), (4.2, 0, 0.9), chassis, 0.03)
box((8.0, 0.05, 0.75), (0, -2.28, 0.55), dark)          # grille backing
# perforated grille: an array of small holes as dark discs on a steel face
box((7.6, 0.04, 0.62), (0, -2.3, 0.55), steel, 0.005)
for i in range(64):
    for j in range(5):
        x = -3.6 + i * 0.115 + (0.057 if j % 2 else 0)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.034, depth=0.05, location=(x, -2.33, 0.33 + j * 0.11), rotation=(math.pi / 2, 0, 0), vertices=10)
        bpy.context.object.data.materials.append(dark)
# nameplate with the mark
box((0.5, 0.03, 0.42), (2.6, -2.36, 0.55), plate, 0.01)
A = [(639, 0), (941, 0), (301, 1059), (0, 1059)]
k = 0.3 / 1059
v = [((x - 470) * k + 2.6, -2.378, -(y - 530) * k + 0.55) for x, y in A]
me = bpy.data.meshes.new("mark"); me.from_pydata(v, [], [[0, 1, 2, 3]]); me.update()
o = bpy.data.objects.new("mark", me); sc.collection.objects.link(o); o.data.materials.append(ink)

# Cabling, as on photographs of cabled inference servers: thick braided cables leave a port cage
# on the upper unit's front, hang in one long even service loop under the chassis, and come back
# up into the lower unit's port cage. Every cable the same, a slight sway each, nothing loose or cut off.
NC = 28
pitch = 0.24
cx0 = -(NC - 1) * pitch / 2
cage, _ = principled("cage", (0.45, 0.45, 0.46), metal=1.0, rough=0.4)
for zc in (1.5, 0.55):                                                        # port cages across both units' fronts
    box((NC * pitch + 0.3, 0.12, 0.34), (0, -2.33, zc), cage, 0.01)
    for i in range(NC):
        S.box((0.17, 0.14, 0.24), (cx0 + i * pitch, -2.36, zc), dark)           # the port openings
        S.box((0.19, 0.3, 0.2), (cx0 + i * pitch, -2.48, zc), steel, 0.01)     # the plug shells
for i in range(NC):
    x = cx0 + i * pitch
    sway = random.uniform(-0.035, 0.035)
    drop = random.uniform(-0.06, 0.06)
    cu = bpy.data.curves.new("c", "CURVE"); cu.dimensions = "3D"
    cu.bevel_depth = 0.075; cu.bevel_resolution = 10; cu.use_fill_caps = True; cu.resolution_u = 36
    sp = cu.splines.new("BEZIER"); sp.bezier_points.add(5)
    # shorter loops: the slack hangs just under the chassis, not far below it
    pts = [(x, -2.55, 1.5), (x, -3.1, 1.35), (x + sway, -3.35, 0.2), (x + sway, -3.3, -1.0 + drop * 0.5),
           (x + sway * 0.5, -3.05, -0.1), (x, -2.6, 0.55)]
    for bp, co in zip(sp.bezier_points, pts):
        bp.co = co; bp.handle_left_type = bp.handle_right_type = "AUTO"
    # the cable leaves and re-enters its plug straight on
    for k, y in ((0, -2.9), (-1, -2.95)):
        bp = sp.bezier_points[k]; bp.handle_left_type = bp.handle_right_type = "ALIGNED"
        z = pts[k][2]
        bp.handle_left = (x, -2.3 if k == 0 else y, z); bp.handle_right = (x, y if k == 0 else -2.3, z)
    ob = bpy.data.objects.new("cable", cu); sc.collection.objects.link(ob)
    cu.materials.append(braid)

# Screws on the rack ears, pull handles and two status lights.
for x in (-4.2, 4.2):
    for z in (0.15, 0.85, 1.55):
        S.screw((x, -2.18, z), steel, 0.07, axis="y")
    bpy.ops.mesh.primitive_torus_add(major_radius=0.32, minor_radius=0.05, location=(x * 0.93, -2.5, 0.9), rotation=(0, math.pi / 2, 0))
    bpy.ops.object.shade_smooth(); bpy.context.object.data.materials.append(steel)
led = bpy.data.materials.new("led"); led.use_nodes = True
e = led.node_tree.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (1, 1, 1, 1); e.inputs["Strength"].default_value = 6
led.node_tree.links.new(e.outputs[0], led.node_tree.nodes["Material Output"].inputs[0])
for k, x in enumerate((3.15, 3.3)):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.028, depth=0.02, location=(x, -2.385, 0.36), rotation=(math.pi / 2, 0, 0), vertices=16)
    bpy.context.object.data.materials.append(led if k == 0 else dark)


def area(loc, energy, size):
    l = bpy.data.lights.new("a", "AREA"); l.energy = energy; l.size = size
    ob = bpy.data.objects.new("a", l); ob.location = loc; sc.collection.objects.link(ob)
    ob.rotation_euler = (Vector((0, 0, 0.5)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


area((-7, -9, 7), 1000, 7)        # key: high, front left
area((8, -4, 1), 350, 4)           # soft fill from the right
area((5, 6, 4), 1200, 5)           # rim from behind right: edge light on every cable
area((0, -9, -4), 160, 8)          # faint lift from below

cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 80
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (-6.5, -22.0, -0.4)                     # low front three-quarter, the whole unit and its loops in frame
target = Vector((0.2, -1.5, 0.2))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
cam_d.dof.use_dof = True; cam_d.dof.focus_distance = (target - cam.location).length; cam_d.dof.aperture_fstop = 7.0

S.render(OUT)

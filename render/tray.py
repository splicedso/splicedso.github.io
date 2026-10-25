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

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
prefs = bpy.context.preferences.addons["cycles"].preferences
try:
    prefs.compute_device_type = "METAL"; prefs.get_devices()
    for d in prefs.devices: d.use = True
    sc.cycles.device = "GPU"
except Exception:
    pass
sc.cycles.samples = 192; sc.cycles.use_denoising = True
sc.render.film_transparent = True
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.85, 0.85, 0.85, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.3


def principled(name, color, metal=0.0, rough=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metal; p.inputs["Roughness"].default_value = rough
    return m, p


# Bead-blasted metal: fine noise in roughness and a little in the bump.
chassis, p = principled("chassis", (0.035, 0.035, 0.037), metal=0.7, rough=0.62)
nt = chassis.node_tree
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900; nz.inputs["Detail"].default_value = 2
bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08
nt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])

# Braided sleeve: a woven pattern from two crossed wave textures along the cable's length.
braid, p = principled("braid", (0.035, 0.035, 0.035), rough=0.55)
nt = braid.node_tree
tc = nt.nodes.new("ShaderNodeTexCoord")
waves = []
for rot in (0.6, -0.6):
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0, 0, rot); mp.inputs["Scale"].default_value = (40, 40, 40)
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 3
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], wv.inputs["Vector"])
    waves.append(wv)
mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
nt.links.new(waves[0].outputs["Fac"], mul.inputs[0]); nt.links.new(waves[1].outputs["Fac"], mul.inputs[1])
bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.6
nt.links.new(mul.outputs[0], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])

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

# Braided cables: loops out of the bottom face, hanging under gravity, each slightly different.
for i in range(26):
    x = -3.5 + i * 0.28 + random.uniform(-0.03, 0.03)
    drop = 2.2 + random.uniform(-0.25, 0.35)
    cu = bpy.data.curves.new("c", "CURVE"); cu.dimensions = "3D"
    cu.bevel_depth = 0.075; cu.bevel_resolution = 6; cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER"); sp.bezier_points.add(2)
    pts = [(x, -1.2, 0.1), (x + random.uniform(-0.05, 0.05), -1.55, 0.1 - drop), (x, -0.4, 0.1)]
    for bp, co in zip(sp.bezier_points, pts):
        bp.co = co; bp.handle_left_type = bp.handle_right_type = "AUTO"
    ob = bpy.data.objects.new("cable", cu); sc.collection.objects.link(ob)
    cu.materials.append(braid)
    # metal ferrule where each cable leaves the chassis
    bpy.ops.mesh.primitive_cylinder_add(radius=0.095, depth=0.16, location=(x, -1.2, 0.05), vertices=24)
    bpy.context.object.data.materials.append(steel)


def area(loc, energy, size):
    l = bpy.data.lights.new("a", "AREA"); l.energy = energy; l.size = size
    ob = bpy.data.objects.new("a", l); ob.location = loc; sc.collection.objects.link(ob)
    ob.rotation_euler = (Vector((0, 0, 0.5)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


area((-6, -8, 7), 1800, 8)
area((7, -5, 3), 1400, 5)
area((0, 6, 6), 900, 8)
area((0, -9, -2), 500, 8)

cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 60
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (0.0, -21.5, 3.0)
cam.rotation_euler = (Vector((0, 0, -0.55)) - cam.location).to_track_quat("-Z", "Y").to_euler()

r = sc.render; r.image_settings.file_format = "PNG"; r.image_settings.color_mode = "RGBA"; r.filepath = OUT
bpy.ops.render.render(write_still=True)

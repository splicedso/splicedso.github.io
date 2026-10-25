"""A photo-real processor package, isolated on a transparent background (Cycles).

Substrate with solder balls and surface capacitors, a machined metal lid with the Spliced mark
engraved, studio lighting. The film is transparent, so the object is already cut out and can
sit on any page colour.

    Blender -b -P render/package.py -- out.png [WxH] [--angle low|top]
"""
import math, random, sys
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
W, H = (int(v) for v in (args[1] if len(args) > 1 and "x" in args[1] else "2400x1600").split("x"))
ANGLE = args[args.index("--angle") + 1] if "--angle" in args else "low"
random.seed(4)

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
sc.cycles.samples = 160; sc.cycles.use_denoising = True
sc.render.film_transparent = True
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.8, 0.8, 0.8, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.25


def mat(name, color, metal=0.0, rough=0.5, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metal; p.inputs["Roughness"].default_value = rough
    if coat:
        p.inputs["Coat Weight"].default_value = coat
    return m


def box(size, loc, m, bevel=0.0, segs=4):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = segs
        o.modifiers.new("w", "WEIGHTED_NORMAL")
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return o


# Brushed metal for the lid: anisotropic-looking roughness from a stretched noise.
lid = bpy.data.materials.new("lid"); lid.use_nodes = True
nt = lid.node_tree; p = nt.nodes["Principled BSDF"]
p.inputs["Base Color"].default_value = (0.62, 0.62, 0.6, 1); p.inputs["Metallic"].default_value = 1.0
tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1, 160, 1)
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 30; nz.inputs["Detail"].default_value = 8
rmp = nt.nodes.new("ShaderNodeMapRange"); rmp.inputs["To Min"].default_value = 0.16; rmp.inputs["To Max"].default_value = 0.3
nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
nt.links.new(nz.outputs["Fac"], rmp.inputs["Value"]); nt.links.new(rmp.outputs["Result"], p.inputs["Roughness"])

substrate = mat("substrate", (0.025, 0.03, 0.028), rough=0.35, coat=0.6)
gold = mat("gold", (0.75, 0.75, 0.72), metal=1.0, rough=0.25)
cap = mat("cap", (0.32, 0.3, 0.27), rough=0.45)
capend = mat("capend", (0.8, 0.8, 0.78), metal=1.0, rough=0.2)
etch = mat("etch", (0.18, 0.18, 0.18), metal=1.0, rough=0.55)
ball = mat("ball", (0.7, 0.7, 0.7), metal=1.0, rough=0.15)

box((3.2, 3.2, 0.12), (0, 0, 0.06), substrate, 0.04)
box((2.3, 2.3, 0.16), (0, 0, 0.2), lid, 0.06, 6)
# a thin sealant ring under the lid
box((2.36, 2.36, 0.025), (0, 0, 0.126), mat("seal", (0.08, 0.08, 0.08), rough=0.6), 0.01)

# Surface capacitors in rows around the lid.
for side in range(4):
    for i in range(14):
        t = -1.35 + i * 0.2 + random.uniform(-0.01, 0.01)
        if random.random() < 0.18:
            continue
        x, y = (t, 1.38) if side == 0 else (t, -1.38) if side == 1 else (1.38, t) if side == 2 else (-1.38, t)
        rot = side >= 2
        body = box((0.05, 0.1, 0.05) if rot else (0.1, 0.05, 0.05), (x, y, 0.145), cap, 0.006, 2)
        for s in (-1, 1):
            ox, oy = (0, s * 0.045) if rot else (s * 0.045, 0)
            box((0.054, 0.02, 0.054) if rot else (0.02, 0.054, 0.054), (x + ox, y + oy, 0.146), capend, 0.004, 2)

# Solder balls under the substrate, seen at the low angle.
for i in range(30):
    for j in range(30):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(-1.48 + i * 0.102, -1.48 + j * 0.102, -0.02), segments=10, ring_count=6)
        bpy.context.object.data.materials.append(ball)

# The mark, engraved: a shallow inset slab of darker metal on the lid.
A = [(639, 0), (941, 0), (301, 1059), (0, 1059)]
k = 1.0 / 1059
v = [((x - 470) * k, -(y - 530) * k, 0.2802) for x, y in A]
me = bpy.data.meshes.new("mark"); me.from_pydata(v, [], [list(range(4))]); me.update()
o = bpy.data.objects.new("mark", me); sc.collection.objects.link(o); o.data.materials.append(etch)


def area(loc, energy, size, color=(1, 1, 1)):
    l = bpy.data.lights.new("a", "AREA"); l.energy = energy; l.size = size; l.color = color
    ob = bpy.data.objects.new("a", l); ob.location = loc; sc.collection.objects.link(ob)
    ob.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


area((-4, -3, 6), 900, 5)          # key, soft
area((5, 2, 2.5), 700, 3)          # rim, picks the lid edge
area((0, 6, 4), 300, 6)            # back fill
area((0, -6, 0.6), 120, 4)         # low front kicker for the balls

cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 85
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (5.6, -8.8, 3.0) if ANGLE == "low" else (0.0, -5.2, 9.5)
cam.rotation_euler = (Vector((0, 0, 0.1)) - cam.location).to_track_quat("-Z", "Y").to_euler()
cam_d.dof.use_dof = True; cam_d.dof.focus_distance = (cam.location - Vector((0, 0, 0.1))).length; cam_d.dof.aperture_fstop = 8

r = sc.render; r.image_settings.file_format = "PNG"; r.image_settings.color_mode = "RGBA"; r.filepath = OUT
bpy.ops.render.render(write_still=True)

"""Hero film: the Spliced mark assembles in a dark studio. Blender, Eevee, H.264."""
import math, sys
import bpy
from mathutils import Vector

OUT = sys.argv[sys.argv.index("--") + 1]
A = [(0, 192), (418, 0), (418, 205), (145, 331), (145, 449), (0, 516)]
B = [(197, 385), (500, 246), (500, 520), (197, 659)]
S = 1 / 120

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.fps = 30
sc.frame_start, sc.frame_end = 1, 210
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - High Contrast" if "AgX - High Contrast" in [l.identifier for l in sc.view_settings.bl_rna.properties["look"].enum_items_static] else "None"
try:
    sc.eevee.use_raytracing = True
except Exception:
    pass

world = bpy.data.worlds.new("w"); sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.004, 0.004, 0.004, 1)


def prism(name, pts, depth):
    verts = [((x - 250) * S, 0, -(y - 330) * S + 2.76) for x, y in pts]
    n = len(verts)
    verts += [(x, depth, z) for x, _, z in verts]
    faces = [list(range(n)), list(range(n, 2 * n))[::-1]]
    faces += [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob)
    bev = ob.modifiers.new("b", "BEVEL"); bev.width = 0.012; bev.segments = 3
    return ob


mat = bpy.data.materials.new("anodised"); mat.use_nodes = True
p = mat.node_tree.nodes["Principled BSDF"]
p.inputs["Base Color"].default_value = (0.82, 0.82, 0.8, 1)
p.inputs["Metallic"].default_value = 1.0
p.inputs["Roughness"].default_value = 0.32
a = prism("A", A, 0.45); b = prism("B", B, 0.45)
for ob in (a, b):
    ob.data.materials.append(mat)

floor_m = bpy.data.materials.new("floor"); floor_m.use_nodes = True
fp = floor_m.node_tree.nodes["Principled BSDF"]
fp.inputs["Base Color"].default_value = (0.01, 0.01, 0.01, 1)
fp.inputs["Roughness"].default_value = 0.42
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.01))
bpy.context.object.data.materials.append(floor_m)

# Assembly: the halves arrive along the mark's own diagonal and meet.
d = Vector((1.6, 0, -0.75))
for ob, sgn in ((a, -1), (b, 1)):
    ob.location = d * sgn + Vector((0, -0.6, 0.4)); ob.rotation_euler = (0, sgn * 0.12, sgn * 0.35)
    ob.keyframe_insert("location", frame=1); ob.keyframe_insert("rotation_euler", frame=1)
    ob.location = (0, 0, 0); ob.rotation_euler = (0, 0, 0)
    ob.keyframe_insert("location", frame=75); ob.keyframe_insert("rotation_euler", frame=75)

def area(name, loc, energy, size, color=(1, 1, 1)):
    l = bpy.data.lights.new(name, "AREA"); l.energy = energy; l.size = size; l.color = color
    o = bpy.data.objects.new(name, l); o.location = loc; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 0.3)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o

area("key", (-5, -6, 7), 1400, 4)
area("rim", (5, 5, 5), 900, 6, (0.85, 0.9, 1))
sweep = area("sweep", (-8, -6, 3), 450, 1.5)
sweep.location = (-8, -6, 3); sweep.keyframe_insert("location", frame=60)
sweep.location = (8, -6, 3); sweep.keyframe_insert("location", frame=200)

cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 60
cam_d.dof.use_dof = True; cam_d.dof.aperture_fstop = 2.8
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
tgt = bpy.data.objects.new("tgt", None); sc.collection.objects.link(tgt); tgt.location = (0.1, 0.2, 2.75)
cam_d.dof.focus_object = tgt
tc = cam.constraints.new("TRACK_TO"); tc.target = tgt
for f, ang in ((1, -0.42), (210, -0.12)):
    cam.location = (20 * math.sin(ang), -20 * math.cos(ang), 3.6)
    cam.keyframe_insert("location", frame=f)

for ob in bpy.data.objects:
    if ob.animation_data and ob.animation_data.action:
        try:
            for fc in ob.animation_data.action.fcurves:
                for k in fc.keyframe_points:
                    k.interpolation = "BEZIER"; k.easing = "EASE_IN_OUT"
        except AttributeError:
            pass

r = sc.render
r.image_settings.file_format = "PNG"
r.filepath = OUT
if "--still" in sys.argv:
    sc.frame_set(int(sys.argv[sys.argv.index("--still") + 1]))
    r.filepath = OUT + "still.png"
    bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)

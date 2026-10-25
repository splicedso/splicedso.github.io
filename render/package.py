"""A photo-real processor package, studio-lit on a shadow-catcher floor.

Substrate with solder balls and capacitors, a machined lid with the Spliced mark and a
laser-etched model line, and the sealant bead where lid meets substrate.

    Blender -b -P render/package.py -- out.png [WxH] [--angle low|top]
"""
import math, random, sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).parent))
import studio as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
W, H = (int(v) for v in (args[1] if len(args) > 1 and "x" in args[1] else "2400x1600").split("x"))
ANGLE = args[args.index("--angle") + 1] if "--angle" in args else "low"
random.seed(4)

sc = S.setup(W, H)
S.floor(-0.06)

# Brushed lid: roughness from noise stretched along one axis.
lid = bpy.data.materials.new("lid"); lid.use_nodes = True
nt = lid.node_tree; p = nt.nodes["Principled BSDF"]
p.inputs["Base Color"].default_value = (0.66, 0.66, 0.64, 1); p.inputs["Metallic"].default_value = 1.0
tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1, 220, 1)
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 30; nz.inputs["Detail"].default_value = 10
rmp = nt.nodes.new("ShaderNodeMapRange"); rmp.inputs["To Min"].default_value = 0.14; rmp.inputs["To Max"].default_value = 0.3
nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
nt.links.new(nz.outputs["Fac"], rmp.inputs["Value"]); nt.links.new(rmp.outputs["Result"], p.inputs["Roughness"])

substrate = S.pcb_mat("substrate", (0.012, 0.016, 0.014), scale=14.0)   # a fine-pitch package substrate: traces and vias
cap = S.mat("cap", (0.33, 0.3, 0.26), rough=0.45)
capend = S.mat("capend", (0.82, 0.82, 0.8), metal=1.0, rough=0.2)
etch = S.mat("etch", (0.03, 0.03, 0.03), metal=0.3, rough=0.5)
laser = S.mat("laser", (0.36, 0.36, 0.35), metal=0.7, rough=0.55)
ball = S.mat("ball", (0.72, 0.72, 0.72), metal=1.0, rough=0.15)
seal = S.mat("seal", (0.05, 0.05, 0.05), rough=0.35, coat=0.6)

S.box((3.2, 3.2, 0.12), (0, 0, 0.06), substrate, 0.04)
S.box((2.36, 2.36, 0.028), (0, 0, 0.128), seal, 0.012)
S.box((2.3, 2.3, 0.16), (0, 0, 0.2), lid, 0.06, 6)

for side in range(4):
    for i in range(14):
        t = -1.35 + i * 0.2 + random.uniform(-0.01, 0.01)
        if random.random() < 0.18:
            continue
        x, y = (t, 1.38) if side == 0 else (t, -1.38) if side == 1 else (1.38, t) if side == 2 else (-1.38, t)
        rot = side >= 2
        S.box((0.05, 0.1, 0.05) if rot else (0.1, 0.05, 0.05), (x, y, 0.145), cap, 0.006, 2)
        for s in (-1, 1):
            ox, oy = (0, s * 0.045) if rot else (s * 0.045, 0)
            S.box((0.054, 0.02, 0.054) if rot else (0.02, 0.054, 0.054), (x + ox, y + oy, 0.146), capend, 0.004, 2)

for i in range(30):
    for j in range(30):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(-1.48 + i * 0.102, -1.48 + j * 0.102, -0.02), segments=12, ring_count=8)
        bpy.ops.object.shade_smooth(); bpy.context.object.data.materials.append(ball)

S.mark((-0.25, 0.15, 0.2805), 1.0, etch)
# pin-1 marker
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.002, location=(-0.98, -0.98, 0.2806), vertices=24)
bpy.context.object.data.materials.append(laser)

S.area((-4, -3, 6), 600, 5)
S.area((5, 2, 2.5), 450, 3)
if ANGLE == "low":
    S.camera((7.4, -11.4, 4.4), (0, 0, 0.1), lens=85, fstop=8)
else:
    S.camera((0.0, -3.2, 12.0), (0, 0, 0.1), lens=85, fstop=11)
if "--fall" in args:
    # the package stands facing the camera, then falls flat onto the floor (scrubbed by scroll on the site)
    from mathutils import Vector, Quaternion
    frames = int(args[args.index("--fall") + 1])
    sc.cycles.samples = 20
    # --from N resumes an interrupted render at frame N (the keyframes are the same either way)
    sc.frame_start = int(args[args.index("--from") + 1]) if "--from" in args else 1
    sc.frame_end = frames
    pivot = bpy.data.objects.new("pivot", None); sc.collection.objects.link(pivot)
    for o in list(sc.objects):
        # everything on the package falls with it, the lid's laser text (FONT objects) included
        if o.type in ("MESH", "FONT", "CURVE") and o.name != "floor" and o.parent is None and o.location.z > -0.05:
            o.parent = pivot
    sc.camera.data.lens = 50
    sc.camera.data.dof.use_dof = False
    sc.cycles.use_denoising = True
    d = (sc.camera.location - Vector((0, 0, 0.1))).normalized()
    axis = Vector((0, 0, 1)).cross(d).normalized()
    yaw = Quaternion((0, 0, 1), math.atan2(d.y, d.x) + math.pi / 2)
    up = Quaternion(axis, Vector((0, 0, 1)).angle(d)) @ yaw
    pivot.rotation_mode = "QUATERNION"
    for f in range(1, frames + 1):
        t = (f - 1) / (frames - 1)
        e = t * t * (3 - 2 * t)
        pivot.rotation_quaternion = up.slerp(yaw, e)
        pivot.location = (0, 0, 1.7 * (1 - e))
        pivot.keyframe_insert("rotation_quaternion", frame=f); pivot.keyframe_insert("location", frame=f)
    r = sc.render
    r.image_settings.file_format = "PNG"; r.image_settings.color_mode = "RGBA"; r.filepath = OUT
    bpy.ops.render.render(animation=True)
elif "--turntable" in args:
    # a seamless orbit: the camera circles the package once over the loop
    frames = int(args[args.index("--turntable") + 1])
    sc.cycles.samples = 96
    sc.frame_start, sc.frame_end = 1, frames
    sc.render.fps = 30
    cam = sc.camera
    pivot = bpy.data.objects.new("pivot", None); sc.collection.objects.link(pivot)
    cam.parent = pivot
    pivot.rotation_euler = (0, 0, 0); pivot.keyframe_insert("rotation_euler", index=2, frame=1)
    pivot.rotation_euler = (0, 0, 2 * math.pi); pivot.keyframe_insert("rotation_euler", index=2, frame=frames + 1)
    for fc in (pivot.animation_data.action.fcurves if hasattr(pivot.animation_data.action, "fcurves") else
               [c for l in pivot.animation_data.action.layers for st in l.strips for bag in st.channelbags for c in bag.fcurves]):
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"
    r = sc.render
    r.image_settings.file_format = "PNG"; r.image_settings.color_mode = "RGBA"; r.filepath = OUT
    bpy.ops.render.render(animation=True)
else:
    S.render(OUT)

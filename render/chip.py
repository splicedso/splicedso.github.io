"""Loop: power flowing into a chip along its board traces. Blender, Eevee, seamless 6 s loop."""
import math, random, sys
import bpy

OUT = sys.argv[sys.argv.index("--") + 1]
FRAMES = 180
random.seed(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.fps = 30
sc.frame_start, sc.frame_end = 1, FRAMES
sc.view_settings.view_transform = "AgX"
sc.eevee.use_raytracing = True
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.003, 0.003, 0.003, 1)


def mat(name, color, metal=0.0, rough=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metal; p.inputs["Roughness"].default_value = rough
    return m


def box(name, size, loc, m, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 4
    o.data.materials.append(m)
    return o


board = mat("board", (0.012, 0.012, 0.012), rough=0.6)
copper = mat("copper", (0.55, 0.55, 0.52), metal=1.0, rough=0.35)
lid = mat("lid", (0.7, 0.7, 0.68), metal=1.0, rough=0.22)
subst = mat("substrate", (0.03, 0.03, 0.03), rough=0.4)

box("board", (16, 10, 0.1), (0, 0, -0.05), board)
box("substrate", (2.6, 2.6, 0.08), (0, 0, 0.04), subst, 0.02)
box("lid", (1.9, 1.9, 0.12), (0, 0, 0.14), lid, 0.05)
A = [(639, 0), (941, 0), (301, 1059), (0, 1059)]  # the Spliced mark, as in brand/build.py
etch = mat("etch", (0.08, 0.08, 0.08), metal=1.0, rough=0.7)
for pts in (A,):
    k = 1.0 / 1059
    v = [((x - 470) * k, -(y - 530) * k, 0.201) for x, y in pts]
    me = bpy.data.meshes.new("m"); me.from_pydata(v, [], [list(range(len(v)))]); me.update()
    o = bpy.data.objects.new("mark", me); sc.collection.objects.link(o); o.data.materials.append(etch)

# Pulse material: wave bands along the trace's own length, phase keyframed over exactly one
# period so the loop closes.
pulse = bpy.data.materials.new("pulse"); pulse.use_nodes = True
nt = pulse.node_tree; nt.nodes.clear()
tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "X"
wv.inputs["Scale"].default_value = 1.0; wv.inputs["Distortion"].default_value = 0
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.955; ramp.color_ramp.elements[1].position = 0.999
em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 9
mix = nt.nodes.new("ShaderNodeMixShader"); bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Base Color"].default_value = (0.5, 0.5, 0.48, 1); bsdf.inputs["Metallic"].default_value = 1; bsdf.inputs["Roughness"].default_value = 0.35
out = nt.nodes.new("ShaderNodeOutputMaterial")
L = nt.links.new
oi = nt.nodes.new("ShaderNodeObjectInfo"); add = nt.nodes.new("ShaderNodeVectorMath"); add.operation = "ADD"
cmb = nt.nodes.new("ShaderNodeCombineXYZ")
L(oi.outputs["Random"], cmb.inputs["X"])
L(tc.outputs["UV"], add.inputs[0]); L(cmb.outputs[0], add.inputs[1])
L(add.outputs[0], mp.inputs["Vector"]); L(mp.outputs["Vector"], wv.inputs["Vector"])
L(wv.outputs["Fac"], ramp.inputs["Fac"]); L(ramp.outputs["Color"], mix.inputs["Fac"])
L(bsdf.outputs[0], mix.inputs[1]); L(em.outputs[0], mix.inputs[2]); L(mix.outputs[0], out.inputs[0])
loc = mp.inputs["Location"]
for f, v in ((1, 0.0), (FRAMES + 1, -1.0)):
    loc.default_value[0] = v; loc.keyframe_insert("default_value", index=0, frame=f)
fc = pulse.node_tree.animation_data.action
try:
    curves = fc.fcurves
except AttributeError:
    curves = [c for layer in fc.layers for strip in layer.strips for bag in strip.channelbags for c in bag.fcurves]
for c in curves:
    for k in c.keyframe_points:
        k.interpolation = "LINEAR"


def trace(points, width=0.035, m=None):
    """A flat trace along a polyline, UV u running 0..1 from the board edge to the chip."""
    import bmesh
    me = bpy.data.meshes.new("t"); bm = bmesh.new()
    total = sum(math.dist(points[i], points[i + 1]) for i in range(len(points) - 1))
    acc = 0.0; prev = None
    uv = bm.loops.layers.uv.new()
    for i in range(len(points) - 1):
        (x0, y0), (x1, y1) = points[i], points[i + 1]
        seg = math.dist(points[i], points[i + 1]); dx, dy = (x1 - x0) / seg, (y1 - y0) / seg
        nx, ny = -dy * width / 2, dx * width / 2
        v = [bm.verts.new((x0 + nx, y0 + ny, 0.005)), bm.verts.new((x0 - nx, y0 - ny, 0.005)),
             bm.verts.new((x1 - nx, y1 - ny, 0.005)), bm.verts.new((x1 + nx, y1 + ny, 0.005))]
        face = bm.faces.new(v)
        u0, u1 = acc / total * total / 3, (acc + seg) / total * total / 3
        for lp, (u, w) in zip(face.loops, ((u0, 0), (u0, 1), (u1, 1), (u1, 0))):
            lp[uv].uv = (u, w)
        acc += seg
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("trace", me); sc.collection.objects.link(o); o.data.materials.append(m)


# Bus fan-out on four sides: straight run from the board edge, one 45 degree jog, into the package.
for side in range(4):
    ang = side * math.pi / 2
    for k in range(-9, 10):
        off = k * 0.12
        start = (8.5, off * 2.4 + random.uniform(-0.05, 0.05)); jog = (3.2 + abs(k) * 0.06, off * 2.4); end = (1.3, off)
        mid = (jog[0] - abs(jog[1] - end[1]), end[1])
        pts = [start, (jog[0], start[1]), mid, end]
        c, s = math.cos(ang), math.sin(ang)
        pts = [(x * c - y * s, x * s + y * c) for x, y in pts]
        trace(pts, 0.03 if k % 3 else 0.05, pulse if random.random() < 0.45 else copper)

def area(name, loc, energy, size):
    l = bpy.data.lights.new(name, "AREA"); l.energy = energy; l.size = size
    o = bpy.data.objects.new(name, l); o.location = loc; sc.collection.objects.link(o)
    from mathutils import Vector
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()

area("key", (-3, -4, 6), 500, 3); area("rim", (5, 3, 3), 300, 4)

cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 50
cam_d.dof.use_dof = True; cam_d.dof.aperture_fstop = 1.8; cam_d.dof.focus_distance = 8.6
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (2.2, -6.2, 5.6)
from mathutils import Vector
cam.rotation_euler = (Vector((0.2, 0.3, 0)) - cam.location).to_track_quat("-Z", "Y").to_euler()

if "--wide" in sys.argv:  # a low, wide shot for the LinkedIn banner
    sc.render.resolution_x, sc.render.resolution_y = 3168, 792
    cam_d.lens = 40
    cam.location = (0.0, -7.4, 2.6)
    cam.rotation_euler = (Vector((0, 0.4, 0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_d.dof.focus_distance = 7.8
if "--size" in sys.argv:
    w, h = sys.argv[sys.argv.index("--size") + 1].split("x")
    sc.render.resolution_x, sc.render.resolution_y = int(w), int(h)
r = sc.render; r.image_settings.file_format = "PNG"; r.filepath = OUT
if "--still" in sys.argv:
    sc.frame_set(int(sys.argv[sys.argv.index("--still") + 1])); r.filepath = OUT + "still.png"
    bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)

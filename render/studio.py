"""Shared studio for the product renders: Cycles on the GPU, a real HDRI for reflections, a
shadow-catcher floor so the object sits on something, and a camera with depth of field.

The HDRI is Poly Haven's studio_small_09 (CC0), in render/hdri/.
"""
import math
from pathlib import Path
import bpy
from mathutils import Vector

HDRI = Path(__file__).parent / "hdri" / "studio.exr"


def setup(width, height, samples=384, hdri_rot=120, hdri_strength=1.0):
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
    sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 12; sc.cycles.glossy_bounces = 8
    sc.render.film_transparent = True
    sc.render.resolution_x, sc.render.resolution_y = width, height
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
    world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
    nt = world.node_tree; bg = nt.nodes["Background"]
    env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(str(HDRI))
    mp = nt.nodes.new("ShaderNodeMapping"); tc = nt.nodes.new("ShaderNodeTexCoord")
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(hdri_rot))
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = hdri_strength
    return sc


def floor(z=0.0, size=60):
    """A shadow catcher: invisible itself, it keeps only the shadows and reflections cast on it."""
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
    o = bpy.context.object; o.is_shadow_catcher = True
    return o


def mat(name, color, metal=0.0, rough=0.5, coat=0.0, micro=0.0):
    """Principled material; micro adds fine roughness variation, as on handled metal."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metal; p.inputs["Roughness"].default_value = rough
    if coat:
        p.inputs["Coat Weight"].default_value = coat
    if micro:
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 220; nz.inputs["Detail"].default_value = 10
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["To Min"].default_value = max(0.0, rough - micro); mr.inputs["To Max"].default_value = min(1.0, rough + micro)
        nt.links.new(nz.outputs["Fac"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], p.inputs["Roughness"])
        bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.04
        nt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def box(size, loc, m, bevel=0.0, segs=4, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = segs; b.limit_method = "ANGLE"
        o.modifiers.new("w", "WEIGHTED_NORMAL")
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return o


def screw(loc, m, r=0.05, axis="z"):
    """A Torx-style screw head: a domed cylinder with a dark star recess."""
    rot = {"z": (0, 0, 0), "y": (math.pi / 2, 0, 0), "x": (0, math.pi / 2, 0)}[axis]
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=r * 0.5, location=loc, rotation=rot, vertices=32)
    o = bpy.context.object
    b = o.modifiers.new("b", "BEVEL"); b.width = r * 0.35; b.segments = 5
    bpy.ops.object.shade_smooth(); o.data.materials.append(m)
    return o


def text(body, loc, size, m, rot=(0, 0, 0), extrude=0.0, font="/System/Library/Fonts/Supplemental/Arial.ttf"):
    cu = bpy.data.curves.new("t", "FONT"); cu.body = body; cu.size = size; cu.extrude = extrude
    cu.align_x = "CENTER"; cu.align_y = "CENTER"
    try:
        cu.font = bpy.data.fonts.load(font)
    except Exception:
        pass
    o = bpy.data.objects.new("t", cu); o.location = loc; o.rotation_euler = rot
    bpy.context.scene.collection.objects.link(o); cu.materials.append(m)
    return o


def mark(loc, height, m, rot=(0, 0, 0), depth=0.0):
    """The Spliced mark as a flat or slightly raised plate."""
    A = [(639, 0), (941, 0), (301, 1059), (0, 1059)]
    k = height / 1059
    v = [((x - 470) * k, -(y - 530) * k, 0) for x, y in A]
    me = bpy.data.meshes.new("mark"); me.from_pydata(v, [], [[0, 1, 2, 3]]); me.update()
    o = bpy.data.objects.new("mark", me); o.location = loc; o.rotation_euler = rot
    bpy.context.scene.collection.objects.link(o); o.data.materials.append(m)
    if depth:
        s = o.modifiers.new("s", "SOLIDIFY"); s.thickness = depth
    return o


def area(loc, energy, size, target=(0, 0, 0)):
    l = bpy.data.lights.new("a", "AREA"); l.energy = energy; l.size = size
    ob = bpy.data.objects.new("a", l); ob.location = loc; bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return ob


def camera(loc, target, lens=85, fstop=5.6):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("cam"); cd.lens = lens
    cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cd.dof.use_dof = True; cd.dof.focus_distance = (Vector(loc) - Vector(target)).length; cd.dof.aperture_fstop = fstop
    return cam


def render(out):
    r = bpy.context.scene.render
    r.image_settings.file_format = "PNG"; r.image_settings.color_mode = "RGBA"; r.image_settings.color_depth = "16"
    r.filepath = out
    bpy.ops.render.render(write_still=True)


def turntable(out, frames, samples=96):
    """Orbit the camera once around the origin over `frames` and render PNG frames to `out`."""
    sc = bpy.context.scene
    sc.cycles.samples = samples
    sc.frame_start, sc.frame_end = 1, frames
    sc.render.fps = 30
    pivot = bpy.data.objects.new("pivot", None); sc.collection.objects.link(pivot)
    sc.camera.parent = pivot
    pivot.rotation_euler = (0, 0, 0); pivot.keyframe_insert("rotation_euler", index=2, frame=1)
    pivot.rotation_euler = (0, 0, 2 * math.pi); pivot.keyframe_insert("rotation_euler", index=2, frame=frames + 1)
    act = pivot.animation_data.action
    curves = getattr(act, "fcurves", None) or [c for l in act.layers for st in l.strips for bag in st.channelbags for c in bag.fcurves]
    for fc in curves:
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"
    r = sc.render
    r.image_settings.file_format = "PNG"; r.image_settings.color_mode = "RGBA"; r.filepath = out
    bpy.ops.render.render(animation=True)

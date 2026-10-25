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


def pcb_mat(name, color=(0.012, 0.03, 0.018), scale=6.0):
    """Solder-masked board: copper traces under the mask (lighter, slightly raised), vias, and
    fine mask texture. Traces are Manhattan runs: thin stripes along x and y, broken up by noise."""
    m = mat(name, color, rough=0.38, coat=0.35)
    nt = m.node_tree; N = nt.nodes; L = nt.links; p = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])

    def stripes(axis, freq):
        sep = N.new("ShaderNodeSeparateXYZ"); L.new(mp.outputs["Vector"], sep.inputs["Vector"])
        mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = freq
        L.new(sep.outputs[axis], mul.inputs[0])
        fr = N.new("ShaderNodeMath"); fr.operation = "FRACT"; L.new(mul.outputs[0], fr.inputs[0])
        lt = N.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = 0.22
        L.new(fr.outputs[0], lt.inputs[0])
        nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.2; nz.inputs["Detail"].default_value = 0
        L.new(mp.outputs["Vector"], nz.inputs["Vector"])
        gt = N.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.52
        L.new(nz.outputs["Fac"], gt.inputs[0])
        both = N.new("ShaderNodeMath"); both.operation = "MULTIPLY"
        L.new(lt.outputs[0], both.inputs[0]); L.new(gt.outputs[0], both.inputs[1])
        return both
    a = stripes("X", 9.0); b = stripes("Y", 11.0)
    tr = N.new("ShaderNodeMath"); tr.operation = "MAXIMUM"; L.new(a.outputs[0], tr.inputs[0]); L.new(b.outputs[0], tr.inputs[1])
    vo = N.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 14
    L.new(mp.outputs["Vector"], vo.inputs["Vector"])
    via = N.new("ShaderNodeMath"); via.operation = "LESS_THAN"; via.inputs[1].default_value = 0.07
    L.new(vo.outputs["Distance"], via.inputs[0])
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*color, 1)
    mix.inputs["B"].default_value = (color[0] * 2.4 + 0.01, color[1] * 2.6 + 0.02, color[2] * 2.2 + 0.01, 1)
    L.new(tr.outputs[0], mix.inputs["Factor"]); L.new(mix.outputs["Result"], p.inputs["Base Color"])
    viac = N.new("ShaderNodeMix"); viac.data_type = "RGBA"; viac.inputs["B"].default_value = (0.75, 0.6, 0.35, 1)
    L.new(mix.outputs["Result"], viac.inputs["A"]); L.new(via.outputs[0], viac.inputs["Factor"])
    L.new(viac.outputs["Result"], p.inputs["Base Color"])
    vm = N.new("ShaderNodeMath"); vm.operation = "MULTIPLY_ADD"; vm.inputs[1].default_value = 0.65; vm.inputs[2].default_value = 0.0
    L.new(via.outputs[0], vm.inputs[0])
    met = N.new("ShaderNodeMath"); met.operation = "MAXIMUM"; met.inputs[1].default_value = 0.0
    L.new(vm.outputs[0], met.inputs[0]); L.new(met.outputs[0], p.inputs["Metallic"])
    h = N.new("ShaderNodeMath"); h.operation = "ADD"; L.new(tr.outputs[0], h.inputs[0]); L.new(via.outputs[0], h.inputs[1])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25; bump.inputs["Distance"].default_value = 0.002
    L.new(h.outputs[0], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
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


def turntable(out, frames, samples=96, sway=None):
    """Orbit the camera once around the origin over `frames`, or with sway=degrees swing it gently
    back and forth across the front (for objects whose back is not modelled). Renders PNG frames."""
    sc = bpy.context.scene
    sc.cycles.samples = samples
    sc.frame_start, sc.frame_end = 1, frames
    sc.render.fps = 30
    pivot = bpy.data.objects.new("pivot", None); sc.collection.objects.link(pivot)
    sc.camera.parent = pivot
    if sway:
        a = math.radians(sway)
        for f, z in ((1, -a), (frames // 2 + 1, a), (frames + 1, -a)):
            pivot.rotation_euler = (0, 0, z); pivot.keyframe_insert("rotation_euler", index=2, frame=f)
        act = pivot.animation_data.action
    else:
        pivot.rotation_euler = (0, 0, 0); pivot.keyframe_insert("rotation_euler", index=2, frame=1)
        pivot.rotation_euler = (0, 0, 2 * math.pi); pivot.keyframe_insert("rotation_euler", index=2, frame=frames + 1)
        act = pivot.animation_data.action
    curves = getattr(act, "fcurves", None) or [c for l in act.layers for st in l.strips for bag in st.channelbags for c in bag.fcurves]
    for fc in curves:
        for k in fc.keyframe_points:
            k.interpolation = "SINE" if sway else "LINEAR"
            if sway:
                k.easing = "EASE_IN_OUT"
    r = sc.render
    r.image_settings.file_format = "PNG"; r.image_settings.color_mode = "RGBA"; r.filepath = out
    bpy.ops.render.render(animation=True)

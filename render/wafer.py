"""A photo-real 300 mm silicon wafer with a die grid, studio-lit on a shadow-catcher floor.

Polished silicon with a thin-film interference coat (the rainbow sheen), dies separated by
scribe streets, an edge exclusion ring and the orientation notch.

    Blender -b -P render/wafer.py -- out.png [WxH]
"""
import math, sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).parent))
import studio as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
W, H = (int(v) for v in (args[1] if len(args) > 1 and "x" in args[1] else "2800x1600").split("x"))
sc = S.setup(W, H, samples=448, hdri_rot=200, hdri_strength=0.12)
S.floor(0.0)


def silicon(name, film, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.36, 0.37, 0.4, 1)
    p.inputs["Metallic"].default_value = 1.0; p.inputs["Roughness"].default_value = rough
    if "Thin Film Thickness" in p.inputs:
        p.inputs["Thin Film Thickness"].default_value = film
        p.inputs["Thin Film IOR"].default_value = 1.46
    return m


R = 3.0
# One material for the whole face: a fine square grid of dies (brick texture with no offset),
# scribe streets as the mortar, and an edge-exclusion ring of bare silicon.
wafer = bpy.data.materials.new("wafer"); wafer.use_nodes = True
nt = wafer.node_tree; p = nt.nodes["Principled BSDF"]
p.inputs["Metallic"].default_value = 1.0
if "Thin Film Thickness" in p.inputs:
    p.inputs["Thin Film IOR"].default_value = 1.46
tc = nt.nodes.new("ShaderNodeTexCoord")
br = nt.nodes.new("ShaderNodeTexBrick")
br.offset = 0.0; br.squash = 1.0
br.inputs["Scale"].default_value = 1.0
br.inputs["Brick Width"].default_value = 0.16; br.inputs["Row Height"].default_value = 0.16
br.inputs["Mortar Size"].default_value = 0.008; br.inputs["Mortar Smooth"].default_value = 0.0
br.inputs["Color1"].default_value = (1, 1, 1, 1); br.inputs["Color2"].default_value = (0.9, 0.9, 0.9, 1)
br.inputs["Mortar"].default_value = (0, 0, 0, 1)
nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
# radial mask: 1 inside the die area, 0 in the outer ring
ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"
nt.links.new(tc.outputs["Object"], ln.inputs[0])
ring = nt.nodes.new("ShaderNodeMath"); ring.operation = "LESS_THAN"; ring.inputs[1].default_value = R - 0.12
nt.links.new(ln.outputs["Value"], ring.inputs[0])
diem = nt.nodes.new("ShaderNodeMath"); diem.operation = "MULTIPLY"
nt.links.new(br.outputs["Fac"], diem.inputs[0]); nt.links.new(ring.outputs[0], diem.inputs[1])
# circuit blocks inside each die: a finer brick grid that modulates colour and roughness
br2 = nt.nodes.new("ShaderNodeTexBrick"); br2.offset = 0.5; br2.squash = 1.0
br2.inputs["Scale"].default_value = 1.0
br2.inputs["Brick Width"].default_value = 0.032; br2.inputs["Row Height"].default_value = 0.018
br2.inputs["Mortar Size"].default_value = 0.003
br2.inputs["Color1"].default_value = (1, 1, 1, 1); br2.inputs["Color2"].default_value = (0.55, 0.55, 0.55, 1)
br2.inputs["Mortar"].default_value = (0.2, 0.2, 0.2, 1)
nt.links.new(tc.outputs["Object"], br2.inputs["Vector"])
# film thickness drifts slowly across the wafer, as on real ones: the rainbow bands
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.6; nz.inputs["Detail"].default_value = 2
nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
# dies: darker, slightly rougher, thicker film; streets and ring: bright polished silicon
mix_c = nt.nodes.new("ShaderNodeMix"); mix_c.data_type = "RGBA"
mix_c.inputs["A"].default_value = (0.62, 0.63, 0.66, 1); mix_c.inputs["B"].default_value = (0.3, 0.31, 0.36, 1)
nt.links.new(diem.outputs[0], mix_c.inputs["Factor"])
tint = nt.nodes.new("ShaderNodeMix"); tint.data_type = "RGBA"; tint.blend_type = "MULTIPLY"
nt.links.new(diem.outputs[0], tint.inputs["Factor"]); nt.links.new(mix_c.outputs["Result"], tint.inputs["A"]); nt.links.new(br2.outputs["Color"], tint.inputs["B"])
nt.links.new(tint.outputs["Result"], p.inputs["Base Color"])
rough = nt.nodes.new("ShaderNodeMapRange"); rough.inputs["To Min"].default_value = 0.1; rough.inputs["To Max"].default_value = 0.3
nt.links.new(diem.outputs[0], rough.inputs["Value"]); nt.links.new(rough.outputs["Result"], p.inputs["Roughness"])
if "Thin Film Thickness" in p.inputs:
    film = nt.nodes.new("ShaderNodeMapRange"); film.inputs["To Min"].default_value = 300; film.inputs["To Max"].default_value = 620
    film.inputs["To Min"].default_value = 250; film.inputs["To Max"].default_value = 900
    if "--stand" in args:
        # on edge the whole face is one reflection, so the drift reads as blotches; instead each die gets
        # its own thickness, a little off its neighbours, as a processed wafer looks up close
        cell = nt.nodes.new("ShaderNodeTexBrick"); cell.offset = 0.0; cell.squash = 1.0
        cell.inputs["Scale"].default_value = 1.0
        cell.inputs["Brick Width"].default_value = 0.16; cell.inputs["Row Height"].default_value = 0.16
        cell.inputs["Mortar Size"].default_value = 0.0; cell.inputs["Bias"].default_value = 0.0
        cell.inputs["Color1"].default_value = (0, 0, 0, 1); cell.inputs["Color2"].default_value = (1, 1, 1, 1)
        nt.links.new(tc.outputs["Object"], cell.inputs["Vector"])
        film.inputs["To Min"].default_value = 430; film.inputs["To Max"].default_value = 520
        nt.links.new(cell.outputs["Color"], film.inputs["Value"])
    nt.links.new(nz.outputs["Fac"], film.inputs["Value"]); nt.links.new(film.outputs["Result"], p.inputs["Thin Film Thickness"])

bpy.ops.mesh.primitive_cylinder_add(radius=R, depth=0.03, location=(0, 0, 0.015), vertices=256)
disk = bpy.context.object; disk.data.materials.append(wafer)
b = disk.modifiers.new("b", "BEVEL"); b.width = 0.01; b.segments = 3
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.1, location=(0, -R, 0.015), vertices=24)
notch = bpy.context.object
m = disk.modifiers.new("n", "BOOLEAN"); m.object = notch; m.operation = "DIFFERENCE"
notch.hide_render = True

if "--stand" in args:
    # the wafer stands on its edge facing the camera, as if held in a carrier
    pivot = bpy.data.objects.new("pivot", None); bpy.context.scene.collection.objects.link(pivot)
    for o in list(bpy.context.scene.objects):
        if o.type == "MESH" and o.name != "Plane" and o.parent is None:
            o.parent = pivot
    # --face: square to the camera, as if held up to the viewer; otherwise yawed a little, as if in a carrier
    yaw = 0 if "--face" in args else 28
    pivot.rotation_euler = (math.radians(78), 0, math.radians(yaw)); pivot.location = (0, 0, R * math.sin(math.radians(78)) + 0.03)
    # The face is a mirror, so what the camera sees on it is whatever sits along the reflected ray.
    # One very large softbox placed on that ray, so its reflection spans the whole face as one smooth
    # gradient (no hotspot), a weak fill from the other side, and a brighter HDRI so the rest is not black.
    # dimmer, and set off the mirror ray so its reflection grades across the face from bright to dark,
    # the way a polished wafer photographs: a dark disc with one soft window of light in it
    # most of the face stays dark silicon; one narrow soft window of light crosses it, as in a product shot
    if "--face" in args:
        # square on, the face mirrors what is in front of it: a soft window high and to one side, a weak fill
        S.area((5.0, -12.0, R + 8.0), 760, 14, target=(0, 0, R))
        S.area((-10.0, -9.0, R - 1.0), 50, 8, target=(0, 0, R))
    else:
        S.area((11.0, -8.0, R + 7.0), 420, 7, target=(0, 0, R))
        S.area((-9.0, -7.0, R + 1.0), 60, 8, target=(0, 0, R))
    sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.08
    for m in bpy.data.materials:
        if m.name == "wafer":
            mx = next(n for n in m.node_tree.nodes if n.type == "MIX" and n.inputs["A"].default_value[0] > 0.6)
            mx.inputs["A"].default_value = (0.3, 0.31, 0.34, 1); mx.inputs["B"].default_value = (0.12, 0.125, 0.15, 1)
    sc.cycles.samples = 640
    cam_x = 0.0 if "--face" in args else 3.0
    S.camera((cam_x, -16.0, R + 2.4), (0, 0, R * 0.95), lens=70, fstop=11)
else:
    S.area((-3, 5, 5), 260, 3)
    S.area((5, 3, 2.5), 160, 2)
    S.area((-6, -2, 2), 90, 2)
    S.camera((7.5, -13.5, 6.4), (0, 0.3, 0), lens=70, fstop=6.3)
if "--turntable" in args:
    S.turntable(OUT, int(args[args.index("--turntable") + 1]))
else:
    S.render(OUT)

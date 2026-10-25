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
    nt.links.new(nz.outputs["Fac"], film.inputs["Value"]); nt.links.new(film.outputs["Result"], p.inputs["Thin Film Thickness"])

bpy.ops.mesh.primitive_cylinder_add(radius=R, depth=0.03, location=(0, 0, 0.015), vertices=256)
disk = bpy.context.object; disk.data.materials.append(wafer)
b = disk.modifiers.new("b", "BEVEL"); b.width = 0.01; b.segments = 3
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.1, location=(0, -R, 0.015), vertices=24)
notch = bpy.context.object
m = disk.modifiers.new("n", "BOOLEAN"); m.object = notch; m.operation = "DIFFERENCE"
notch.hide_render = True

S.area((-3, 5, 5), 260, 3)
S.area((5, 3, 2.5), 160, 2)
S.area((-6, -2, 2), 90, 2)
S.camera((7.5, -13.5, 6.4), (0, 0.3, 0), lens=70, fstop=6.3)
S.render(OUT)

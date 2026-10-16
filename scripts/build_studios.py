"""TrackMesh film with two separate studios: a warm closed studio (A) and a cool night loft by a window (B).
blender --background --factory-startup --python-exit-code 1 --python scripts/build_studios.py
The rooms are 40 m apart and never share a frame; the link shots are split screens assembled in the edit.
Screens: the real VST3 editor and the current desktop source, both with synthetic status (assets/screens/v4).
v04: one-click share (auto share off, the default) with a cursor, the DAW-closed question before Get, a 1.6 GB
project where only 44 MB travels, and a calmer Berlin skyline.
Each run saves the next unused scenes/versions/trackmesh-studios-vNN.blend; nothing older is touched.
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
SCREENS = ROOT / 'assets/screens'
number = 1
while (ROOT / f'scenes/versions/trackmesh-studios-v{number:02d}.blend').exists(): number += 1
tag = f'studios-v{number:02d}'

FPS, END = 24, 720
B_X = 40.0  # Studio B's origin; far enough that neither room lights or reflects the other
SHOTS = [('S1 / Studio A', 1, 'A wide'), ('S2 / Save in the DAW', 97, 'A close'), ('S3 / Studio B', 229, 'B wide'),
         ('S4 / Get when ready', 325, 'B close'), ('S5 / PC to PC', 457, 'split'), ('S6 / Outro', 601, 'split outro')]
PLUGIN = [('idle', 1), ('saved', 128), ('sharing', 166), ('shared', 190)]  # a DAW save, then one press on Share
CLICK = 163  # the cursor presses Share current version
APP = [('idle', 1), ('new', 292), ('ask', 350), ('get97', 388), ('get98', 480), ('get99', 525), ('done', 560)]

scene = bpy.context.scene
for obj in list(scene.objects): bpy.data.objects.remove(obj, do_unlink=True)
collections = {}
def collection(name):
    if name not in collections:
        col = bpy.data.collections.new(name); scene.collection.children.link(col); collections[name] = col
    return collections[name]
current = collection('A_Studio')

def put(obj):
    for col in list(obj.users_collection): col.objects.unlink(obj)
    current.objects.link(obj); return obj

# ---------- materials ----------
def material(name, color, rough=.5, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; m.diffuse_color = (*color, 1)
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*color, 1); p.inputs['Roughness'].default_value = rough; p.inputs['Metallic'].default_value = metal
    return m

def textured(name, dark, light, scale, stretch, rough, bump=.08):
    m = material(name, dark, rough); n = m.node_tree.nodes; l = m.node_tree.links; p = n['Principled BSDF']
    coords = n.new('ShaderNodeTexCoord'); mult = n.new('ShaderNodeVectorMath'); mult.operation = 'MULTIPLY'; mult.inputs[1].default_value = stretch
    noise = n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = scale; noise.inputs['Detail'].default_value = 3
    ramp = n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = (*dark, 1); ramp.color_ramp.elements[1].color = (*light, 1)
    height = n.new('ShaderNodeBump'); height.inputs['Strength'].default_value = bump; height.inputs['Distance'].default_value = .0015
    l.new(coords.outputs['Generated'], mult.inputs[0]); l.new(mult.outputs['Vector'], noise.inputs['Vector'])
    l.new(noise.outputs['Fac'], ramp.inputs[0]); l.new(ramp.outputs[0], p.inputs['Base Color'])
    l.new(noise.outputs['Fac'], height.inputs['Height']); l.new(height.outputs[0], p.inputs['Normal'])
    return m

def glow(name, color, strength):
    m = material(name, color, .4); p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Emission Color'].default_value = (*color, 1); p.inputs['Emission Strength'].default_value = strength
    return m

def emission(name, color, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True; n = m.node_tree.nodes; n.clear()
    e = n.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*color, 1); e.inputs['Strength'].default_value = strength
    out = n.new('ShaderNodeOutputMaterial'); m.node_tree.links.new(e.outputs[0], out.inputs['Surface'])
    return m, e

graphite = material('Powder coated graphite', (.023, .027, .031), .44, .4)
metal = material('Brushed charcoal aluminum', (.12, .135, .145), .33, .8)
black = material('Soft black polymer', (.008, .01, .012), .6)
keycaps = material('Graphite keycaps', (.09, .105, .115), .54)
rubber = material('Rubber feet', (.006, .007, .008), .86)
diode = glow('Muted power LED', (.35, .6, .62), .45)
# Studio A: warm, closed, wood and felt.
plaster = textured('A graphite plaster', (.014, .016, .018), (.032, .034, .037), 45, (1, 1, 1), .89, .05)
felt = textured('A acoustic felt', (.016, .016, .017), (.046, .044, .043), 170, (1, 1, 1), .95, .12)
concrete = textured('A dark concrete floor', (.023, .025, .028), (.046, .049, .053), 24, (1, 1, 1), .44, .13)
walnut = textured('A smoked walnut', (.028, .013, .007), (.13, .060, .024), 6, (.7, 23, 8), .43, .14)
oak_slat = textured('A smoked oak slats', (.065, .031, .012), (.19, .10, .043), 5, (18, 12, .45), .53, .08)
rug_a = textured('A rust wool rug', (.045, .02, .013), (.09, .045, .028), 90, (1, 1, 1), .97, .2)
amber = glow('A amber diffuser', (1, .46, .14), 4)
# Studio B: cool, open, pale concrete and light oak by a big window.
concrete_b = textured('B pale concrete wall', (.09, .095, .10), (.15, .155, .16), 18, (1, 1, 1), .82, .06)
oak_floor = textured('B light oak floor', (.11, .075, .045), (.24, .17, .11), 4, (.6, 30, 1), .5, .06)
black_oak = textured('B black oak desk', (.010, .010, .011), (.035, .033, .032), 6, (.7, 23, 8), .38, .1)
rug_b = textured('B grey wool rug', (.05, .055, .06), (.10, .11, .115), 90, (1, 1, 1), .97, .2)
teal = glow('B teal LED strip', (.16, .75, .70), 6)
leaf = material('B plant leaves', (.02, .06, .03), .55)
pot = material('B ceramic pot', (.55, .55, .53), .35)

# ---------- geometry helpers ----------
def box(name, loc, dim, mat, bevel=.008, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = put(bpy.context.object); o.name = name; o.dimensions = dim
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat: o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Edge bevel', 'BEVEL'); b.width = bevel; b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat, rot=(0, 0, 0), top=None):
    if top is None: bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=radius, depth=depth, location=loc, rotation=rot)
    else: bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=radius, radius2=top, depth=depth, location=loc, rotation=rot)
    o = put(bpy.context.object); o.name = name; o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth = True
    return o

def cable(name, points, radius=.003):
    c = bpy.data.curves.new(name, 'CURVE'); c.dimensions = '3D'; c.bevel_depth = radius; c.bevel_resolution = 2
    s = c.splines.new('BEZIER'); s.bezier_points.add(len(points) - 1)
    for p, co in zip(s.bezier_points, points): p.co = co; p.handle_left_type = p.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, c); current.objects.link(o); c.materials.append(rubber)
    return o

def area(name, loc, target, power, color, size, size_y=None):
    d = bpy.data.lights.new(name, 'AREA'); d.energy = power; d.color = color
    d.shape = 'RECTANGLE' if size_y else 'DISK'; d.size = size
    if size_y: d.size_y = size_y
    o = bpy.data.objects.new(name, d); current.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()
    return o

def point(name, loc, power, color, radius=.05):
    d = bpy.data.lights.new(name, 'POINT'); d.energy = power; d.color = color; d.shadow_soft_size = radius
    o = bpy.data.objects.new(name, d); current.objects.link(o); o.location = loc
    return o

def show_between(obj, start, end):
    """Visible on [start, end] only; hide flags step with constant interpolation."""
    keys = {1: start > 1, start: False, end + 1: True}
    if start > 1: keys[start - 1] = True
    for frame, hidden in sorted(keys.items()):
        if frame > END + 1: continue
        obj.hide_render = hidden; obj.hide_viewport = hidden
        obj.keyframe_insert('hide_render', frame=frame); obj.keyframe_insert('hide_viewport', frame=frame)

# A lit screen: emission a little above the old 0.8, so the panel reads as a light source and blooms softly.
SCREEN_GLOW = 1.9
def screen_material(label, file):
    m = bpy.data.materials.new(label); m.use_nodes = True; n = m.node_tree.nodes; n.clear()
    img = n.new('ShaderNodeTexImage'); img.image = bpy.data.images.load(str(file), check_existing=True); img.image.pack(); img.interpolation = 'Linear'
    e = n.new('ShaderNodeEmission'); e.inputs['Strength'].default_value = SCREEN_GLOW
    out = n.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(img.outputs['Color'], e.inputs['Color']); m.node_tree.links.new(e.outputs[0], out.inputs['Surface'])
    return m

def plane(name, centre, w, h, mat):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)], [], [(0, 1, 2, 3)]); mesh.update()
    uv = mesh.uv_layers.new(name='UV')
    for loop, co in zip(uv.data, [(0, 0), (1, 0), (1, 1), (0, 1)]): loop.uv = co
    o = bpy.data.objects.new(name, mesh); current.objects.link(o); o.location = centre; mesh.materials.append(mat)
    return o

def speaker(label, x, y):
    box(label + ' speaker', (x, y + .20, .874), (.135, .135, .23), graphite, .014)
    cylinder(label + ' woofer', (x, y + .127, .849), .043, .010, rubber, (math.pi / 2, 0, 0))
    cylinder(label + ' tweeter', (x, y + .124, .938), .014, .006, metal, (math.pi / 2, 0, 0))

def workstation(label, x, y, desk):
    """Desk, monitor, keyboard, speakers, interface and PC. Returns the screen centre and size."""
    box(label + ' desktop', (x, y, .715), (1.8, .82, .05), desk, .018)
    box(label + ' apron', (x, y + .04, .666), (1.64, .64, .042), graphite, .008)
    for dx in (-.76, .76):
        for dy in (-.29, .29): box(label + ' leg', (x + dx, y + dy, .335), (.035, .035, .65), graphite, .004)
        box(label + ' cross foot', (x + dx, y, .03), (.046, .69, .034), graphite, .004)
    box(label + ' monitor housing', (x, y + .235, 1.205), (.802, .047, .468), graphite, .014)
    box(label + ' bezel', (x, y + .208, 1.208), (.784, .010, .449), black, .008)
    box(label + ' stand neck', (x, y + .244, .869), (.044, .034, .248), metal, .006)
    box(label + ' stand base', (x, y + .17, .755), (.28, .21, .025), metal, .009)
    box(label + ' power LED', (x + .353, y + .198, .984), (.004, .003, .002), diode, .001)
    box(label + ' keyboard', (x - .08, y - .238, .759), (.425, .138, .028), graphite, .009)
    for row in range(5):
        for k in range(15):
            if row == 4 and 3 <= k <= 10: continue
            box(label + ' key', (x - .274 + k * .027, y - .29 + row * .025, .778), (.023, .021, .010), keycaps, .003)
    box(label + ' spacebar', (x - .08, y - .19, .779), (.192, .021, .010), keycaps, .003)
    box(label + ' mouse', (x + .34, y - .235, .765), (.056, .105, .035), graphite, .017)
    for dx in (-.62, .62): speaker(label, x + dx, y)
    box(label + ' PC', (x + .51, y + .10, .27), (.19, .34, .50), graphite, .017)
    box(label + ' PC front', (x + .51, y - .075, .28), (.166, .007, .455), black, .009)
    box(label + ' audio interface', (x - .53, y - .20, .781), (.18, .135, .073), metal, .008)
    cable(label + ' monitor cable', [(x, y + .267, 1.09), (x + .07, y + .34, .88), (x + .08, y + .41, .68), (x + .50, y + .31, .51)])
    centre = (x, y + .201, 1.21)
    # The screen lights the desk and keyboard in front of it, as a real panel does in a dark room.
    glow_light = area(label + ' screen spill', (x, y + .19, 1.21), (x, y - 1.5, .95), 9, (.80, .88, 1.0), .76, .43)
    glow_light.data.use_shadow = False
    return centre, .760, .4275

def screen_states(label, centre, w, h, states, prefix, depth=.0004):
    for i, (state, start) in enumerate(states):
        end = states[i + 1][1] - 1 if i + 1 < len(states) else END
        o = plane(f'{label} / {state}', (centre[0], centre[1] - depth * (i + 1), centre[2]), w, h,
                  screen_material(f'{label} / {state}', SCREENS / 'v4' / f'{prefix}-{state}.png'))
        o['provenance'] = 'Synthetic status; ' + ('real VST3 in the SDK editor host.' if prefix == 'vst3' else 'current desktop source.')
        show_between(o, start, end)

# ======================= Studio A: warm closed studio =======================
current = collection('A_Studio')
box('A floor', (0, -.6, -.065), (6.6, 6.4, .13), concrete, .015)
box('A rear wall', (0, 1.6, 1.5), (6.6, .18, 3), plaster, .012)
box('A left wall', (-3.2, -.6, 1.5), (.15, 6.4, 3), plaster)
box('A right wall', (3.2, -.6, 1.5), (.15, 6.4, 3), plaster)
box('A ceiling', (0, -.6, 3.05), (6.6, 6.4, .1), graphite, 0)
box('A rug', (0, -.2, .006), (2.6, 2.0, .012), rug_a, .004)
for x in (-1.95, 1.95):
    box('A felt panel mount', (x, 1.47, 1.75), (1.0, .08, 1.45), black, .014)
    box('A felt panel', (x, 1.42, 1.75), (.94, .07, 1.39), felt, .025)
for i in range(18):  # oak slat diffuser behind the desk
    box('A oak slat', (-.68 + i * .08, 1.47, 1.82), (.032, .06, 1.3), oak_slat, .003)
for x in (-3.08, 3.08):
    box('A corner LED', (x, 1.45, 1.5), (.012, .025, 2.6), amber, .003)
# Floor lamp with a warm shade, and a shelf of record sleeves: a lived-in studio.
cylinder('A lamp base', (-2.35, .75, .015), .16, .03, metal)
cylinder('A lamp pole', (-2.35, .75, .8), .012, 1.56, metal)
cylinder('A lamp shade', (-2.35, .75, 1.66), .22, .3, glow('A lamp shade glow', (1, .55, .25), 2.5), top=.15)
point('A lamp bulb', (-2.35, .75, 1.6), 55, (1, .58, .3), .1)
box('A record shelf', (2.62, .9, .45), (.9, .36, .9), walnut, .01)
for i in range(16):
    tint = [(.30, .07, .04), (.05, .10, .16), (.25, .18, .05), (.07, .07, .08)][i % 4]
    box('A record sleeve', (2.26 + i * .048, .9, .62), (.012, .31, .31), material(f'A sleeve {i}', tint, .6), .002)
centre_a, sw, sh = workstation('Studio A', 0, 0, walnut)
area('A soft key', (0, -2.4, 2.9), (0, 0, .95), 45, (.84, .89, 1), 3.5, 1.8)
area('A warm left key', (-2.6, -.6, 2.2), (0, .1, 1.0), 85, (1, .48, .19), 1.4, 1.8)
area('A warm wall wash', (-1.9, .9, 2.8), (-1.9, 1.45, 1.6), 22, (1, .55, .25), 1.0, .3)
area('A warm wall wash right', (1.9, .9, 2.8), (1.9, 1.45, 1.6), 14, (1, .6, .32), 1.0, .3)
for x in (-2.95, 2.95): area('A corner bounce', (x, 1.25, 1.45), (x * .6, .2, 1), 10, (1, .49, .18), .04, 2)
# The DAW fills the monitor; the real VST3 editor floats over it, one plane per plugin state.
plane('Studio A DAW', (centre_a[0], centre_a[1], centre_a[2]), sw, sh, screen_material('Studio A DAW', SCREENS / 'daw.png'))
pw = .44; ph = pw * 440 / 580
screen_states('Studio A plugin', (centre_a[0], centre_a[1] - .002, centre_a[2] + .01), pw, ph, PLUGIN, 'vst3')
box('A plugin window border', (centre_a[0], centre_a[1] + .002, centre_a[2] + .01), (pw + .006, .004, ph + .006), black, .001)

# A Windows arrow cursor glides onto Share current version and presses it once.
def cursor_image():
    size = 64; img = bpy.data.images.new('Cursor arrow', size, size, alpha=True)
    outline = [(0, 0), (0, 46), (11, 35), (19, 53), (26, 50), (18, 33), (33, 33)]  # tip at top left, in pixels from the tip
    def inside(px, py, poly):
        hit = False
        for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
            if (y1 > py) != (y2 > py) and px < x1 + (py - y1) * (x2 - x1) / (y2 - y1): hit = not hit
        return hit
    pixels = []
    for row in range(size):
        for col in range(size):
            x, y = col * 56 / size, (size - 1 - row) * 56 / size  # image rows run bottom-up
            core = inside(x - 2, y - 2, outline) if x >= 2 and y >= 2 else False
            edge = any(inside(x - 2 + dx, y - 2 + dy, outline) for dx in (-1.6, 0, 1.6) for dy in (-1.6, 0, 1.6))
            inner = all(inside(x - 2 + dx, y - 2 + dy, outline) for dx in (-1.3, 1.3) for dy in (-1.3, 1.3))
            pixels += (1, 1, 1, 1) if inner else (0, 0, 0, 1) if edge or core else (0, 0, 0, 0)
    img.pixels = pixels; img.pack(); return img
cursor_mat = bpy.data.materials.new('Cursor'); cursor_mat.use_nodes = True; n = cursor_mat.node_tree.nodes; n.clear()
tex = n.new('ShaderNodeTexImage'); tex.image = cursor_image(); tex.interpolation = 'Linear'
cursor_light = n.new('ShaderNodeEmission'); cursor_light.inputs['Strength'].default_value = SCREEN_GLOW
clear = n.new('ShaderNodeBsdfTransparent'); mix = n.new('ShaderNodeMixShader'); out = n.new('ShaderNodeOutputMaterial')
links = cursor_mat.node_tree.links
links.new(tex.outputs['Color'], cursor_light.inputs['Color']); links.new(tex.outputs['Alpha'], mix.inputs['Fac'])
links.new(clear.outputs[0], mix.inputs[1]); links.new(cursor_light.outputs[0], mix.inputs[2]); links.new(mix.outputs[0], out.inputs['Surface'])
cursor_mat.surface_render_method = 'BLENDED'
cs = .022  # about 29 px of the 580 px plugin
cursor = plane('Studio A cursor', (0, 0, 0), cs, cs, cursor_mat)
for v in cursor.data.vertices: v.co.x += cs / 2; v.co.z -= cs / 2  # origin at the arrow tip
def plugin_point(u, v):
    """A point on the plugin window from its pixel position (580x440 capture), just in front of it."""
    return (centre_a[0] + (u / 580 - .5) * pw, centre_a[1] - .008, centre_a[2] + .01 + (.5 - v / 440) * ph)
share_button = plugin_point(150, 262)
for frame, spot in [(1, plugin_point(470, 330)), (140, plugin_point(470, 330)), (CLICK - 3, share_button), (230, share_button)]:
    cursor.location = spot; cursor.keyframe_insert('location', frame=frame)
for frame, scale in [(CLICK - 1, 1), (CLICK + 1, .82), (CLICK + 4, 1)]:
    cursor.scale = (scale, scale, scale); cursor.keyframe_insert('scale', frame=frame)
show_between(cursor, 97, 228)

# ======================= Studio B: night loft with a city window =======================
current = collection('B_Studio')
bx = B_X
box('B floor', (bx, -.6, -.065), (6.4, 6.4, .13), oak_floor, .01)
# Rear wall with a large window opening (x -1.75..1.75, z .85..2.65).
box('B wall below window', (bx, 1.9, .425), (6.4, .2, .85), concrete_b, .01)
box('B wall above window', (bx, 1.9, 2.825), (6.4, .2, .35), concrete_b, .01)
for side in (-1, 1): box('B wall beside window', (bx + side * 2.425, 1.9, 1.75), (1.35, .2, 1.8), concrete_b, .01)
box('B left wall', (bx - 3.1, -.6, 1.5), (.15, 6.4, 3), concrete_b)
box('B right wall', (bx + 3.1, -.6, 1.5), (.15, 6.4, 3), concrete_b)
box('B ceiling', (bx, -.6, 3.05), (6.4, 6.4, .1), concrete_b, 0)
frame_mat = material('B black window frame', (.01, .011, .012), .4, .6)
for x in (-1.75, -.583, .583, 1.75): box('B window mullion', (bx + x, 1.86, 1.75), (.05, .08, 1.84), frame_mat, .004)
for z in (.85, 2.65): box('B window rail', (bx, 1.86, z), (3.55, .08, .05), frame_mat, .004)
box('B window sill', (bx, 1.74, .84), (3.7, .3, .04), concrete_b, .006)
box('B rug', (bx, .5, .006), (2.8, 2.2, .012), rug_b, .004)
# Floating shelf on the right wall with a teal LED strip under it, plants on top.
box('B floating shelf', (bx + 2.85, .2, 1.55), (.3, 1.6, .04), black_oak, .006)
box('B shelf LED', (bx + 2.82, .2, 1.525), (.03, 1.5, .008), teal, .002)
for i, y in enumerate((-.3, .25, .7)):
    cylinder('B shelf pot', (bx + 2.85, y, 1.65), .07, .16, pot)
    for k in range(12):
        a = k * 2.39996 + i
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.06, location=(bx + 2.85 + .06 * math.cos(a), y + .06 * math.sin(a), 1.76 + .015 * (k % 4)))
        o = put(bpy.context.object); o.name = 'B shelf leaf'; o.scale = (1.0, .5, .14); o.rotation_euler = (0, -.6, a); o.data.materials.append(leaf)
cylinder('B floor plant pot', (bx - 2.4, 1.3, .22), .2, .44, pot, top=.16)
cylinder('B plant stem', (bx - 2.4, 1.3, 1.0), .015, 1.2, leaf)
for k in range(44):
    a = k * 2.39996; z = .62 + (k / 44) * .95; r = .10 + .14 * math.sin(math.pi * k / 44)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.11, location=(bx - 2.4 + r * math.cos(a), 1.3 + r * math.sin(a), z))
    o = put(bpy.context.object); o.name = 'B plant leaf'; o.scale = (1.0, .55, .12)
    o.rotation_euler = (0, -.55, a); o.data.materials.append(leaf)
area('B shelf LED light', (bx + 2.8, .2, 1.51), (bx + 2.6, .2, .4), 30, (.2, .8, .74), 1.5, .04)
centre_b, _, _ = workstation('Studio B', bx, .95, black_oak)
screen_states('Studio B app', centre_b, sw, sh, APP, 'app')

# The city outside: lit buildings in front of a dusk sky, far enough for real parallax.
def windows_material(name, seed):
    m = bpy.data.materials.new(name); m.use_nodes = True; n = m.node_tree.nodes; l = m.node_tree.links; n.clear()
    coords = n.new('ShaderNodeTexCoord')
    bricks = n.new('ShaderNodeTexBrick'); bricks.offset = 0; bricks.inputs['Scale'].default_value = 1
    bricks.inputs['Mortar Size'].default_value = .35; bricks.inputs['Brick Width'].default_value = .9; bricks.inputs['Row Height'].default_value = 1.4
    # v04: calmer city. Fewer lit windows, each with its own warmth and brightness, so the facades stop reading
    # as a uniform grid and stay behind the screen.
    bricks.inputs['Color1'].default_value = (1, 1, 1, 1); bricks.inputs['Color2'].default_value = (1, 1, 1, 1)
    bricks.inputs['Mortar'].default_value = (0, 0, 0, 1)
    noise = n.new('ShaderNodeTexWhiteNoise'); noise.noise_dimensions = '3D'
    snap = n.new('ShaderNodeVectorMath'); snap.operation = 'SNAP'; snap.inputs[1].default_value = (.9, .9, 1.4)
    cut = n.new('ShaderNodeMath'); cut.operation = 'GREATER_THAN'; cut.inputs[1].default_value = .79
    channels = n.new('ShaderNodeSeparateColor')
    warmth = n.new('ShaderNodeValToRGB'); r = warmth.color_ramp.elements
    r[0].color = (1, .52, .22, 1); r[0].position = 0; r[1].color = (.62, .76, 1, 1); r[1].position = 1
    middle = r.new(.65); middle.color = (1, .80, .58, 1)
    level = n.new('ShaderNodeMath'); level.operation = 'MULTIPLY_ADD'; level.inputs[1].default_value = .75; level.inputs[2].default_value = .25
    dim = n.new('ShaderNodeMath'); dim.operation = 'MULTIPLY'
    tint = n.new('ShaderNodeMixRGB'); tint.blend_type = 'MULTIPLY'; tint.inputs['Fac'].default_value = 1
    lit = n.new('ShaderNodeMixRGB'); lit.blend_type = 'MULTIPLY'; lit.inputs['Fac'].default_value = 1
    e = n.new('ShaderNodeEmission'); e.inputs['Strength'].default_value = 1.3
    # A faint blue floor so the facades read as buildings against the sky, not black cut-outs.
    facade_glow = n.new('ShaderNodeMixRGB'); facade_glow.blend_type = 'ADD'; facade_glow.inputs['Fac'].default_value = 1
    facade_glow.inputs['Color2'].default_value = (.010, .014, .024, 1)
    body = n.new('ShaderNodeBsdfPrincipled'); body.inputs['Base Color'].default_value = (.02, .025, .035, 1); body.inputs['Roughness'].default_value = .7
    add = n.new('ShaderNodeAddShader'); out = n.new('ShaderNodeOutputMaterial')
    shift = n.new('ShaderNodeVectorMath'); shift.operation = 'ADD'; shift.inputs[1].default_value = (seed, seed * 2, 0)
    # The brick pattern is 2D in X/Y; a facade faces -Y, so feed it X and Z.
    split = n.new('ShaderNodeSeparateXYZ'); facade = n.new('ShaderNodeCombineXYZ')
    l.new(coords.outputs['Object'], split.inputs[0])
    l.new(split.outputs['X'], facade.inputs['X']); l.new(split.outputs['Z'], facade.inputs['Y']); l.new(split.outputs['Y'], facade.inputs['Z'])
    l.new(facade.outputs[0], bricks.inputs['Vector']); l.new(facade.outputs[0], snap.inputs[0])
    l.new(snap.outputs['Vector'], shift.inputs[0]); l.new(shift.outputs['Vector'], noise.inputs['Vector'])
    l.new(noise.outputs['Value'], cut.inputs[0])
    l.new(noise.outputs['Color'], channels.inputs[0])
    l.new(channels.outputs['Red'], warmth.inputs[0]); l.new(channels.outputs['Green'], level.inputs[0])
    l.new(level.outputs[0], dim.inputs[0]); l.new(cut.outputs['Value'], dim.inputs[1])
    l.new(bricks.outputs['Color'], tint.inputs['Color1']); l.new(warmth.outputs['Color'], tint.inputs['Color2'])
    l.new(tint.outputs['Color'], lit.inputs['Color1']); l.new(dim.outputs[0], lit.inputs['Color2'])
    l.new(lit.outputs['Color'], facade_glow.inputs['Color1']); l.new(facade_glow.outputs['Color'], e.inputs['Color'])
    l.new(body.outputs[0], add.inputs[0]); l.new(e.outputs[0], add.inputs[1]); l.new(add.outputs[0], out.inputs['Surface'])
    return m
for i, (x, y, w, h) in enumerate([(-38, 70, 16, 26), (-18, 90, 20, 44), (2, 64, 14, 20), (20, 84, 18, 36), (40, 72, 16, 28),
                                  (-55, 110, 24, 52), (58, 116, 24, 46), (-4, 128, 22, 60), (30, 136, 26, 54), (-28, 140, 20, 40)]):
    # The loft is a few floors up: facades run 40 m below the window line, so no ground or sky shows beneath them.
    box(f'B city building {i + 1}', (bx + x, y, (h - 40) / 2), (w, 8, h + 40), windows_material(f'B building windows {i + 1}', i * 3.7), 0)
sky = bpy.data.materials.new('B dusk sky'); sky.use_nodes = True; n = sky.node_tree.nodes; l = sky.node_tree.links; n.clear()
coords = n.new('ShaderNodeTexCoord'); sep = n.new('ShaderNodeSeparateXYZ'); ramp = n.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color = (.30, .17, .20, 1); ramp.color_ramp.elements[0].position = .0
ramp.color_ramp.elements[1].color = (.012, .018, .045, 1); ramp.color_ramp.elements[1].position = .42
mid = ramp.color_ramp.elements.new(.1); mid.color = (.08, .10, .22, 1)
e = n.new('ShaderNodeEmission'); e.inputs['Strength'].default_value = 1.0; out = n.new('ShaderNodeOutputMaterial')
l.new(coords.outputs['Generated'], sep.inputs[0]); l.new(sep.outputs['Z'], ramp.inputs[0]); l.new(ramp.outputs[0], e.inputs['Color']); l.new(e.outputs[0], out.inputs['Surface'])
box('B sky', (bx, 170, 60), (520, .5, 140), sky, 0)  # z -10..130: the warm band sits on the horizon
# Cool moonlight and city glow through the window; the room stays dark so the screen leads.
area('B window light', (bx, 2.4, 2.0), (bx, -.5, .9), 70, (.55, .68, 1.0), 3.4, 1.7)
area('B soft fill', (bx, -2.6, 2.8), (bx, .5, 1.0), 14, (.75, .82, 1), 3, 1.6)
area('B left rim', (bx - 2.7, 1.2, 2.2), (bx, .9, 1.1), 25, (.35, .55, .9), 1, 1.6)

# ---------- the direct link: a teal arc drawn between the screens in the split-screen edit ----------
# (2D overlay in the edit, since the rooms are apart; nothing to model here.)

# ---------- cameras ----------
current = collection('Cameras')
def camera(name, keys, focus=None, fstop=4.0):
    cam = bpy.data.objects.new(name, bpy.data.cameras.new(name)); current.objects.link(cam)
    cam.data.sensor_width = 36; cam.data.clip_start = .05; cam.data.clip_end = 200
    if focus:
        cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = fstop
    for frame, location, target, lens in keys:
        cam.location = location
        cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
        cam.data.lens = lens
        if focus: cam.data.dof.focus_distance = (Vector(focus) - Vector(location)).length; cam.data.dof.keyframe_insert('focus_distance', frame=frame)
        cam.keyframe_insert('location', frame=frame); cam.keyframe_insert('rotation_euler', frame=frame); cam.data.keyframe_insert('lens', frame=frame)
    return cam
A = lambda x, y, z: (x, y, z)
B = lambda x, y, z: (bx + x, y, z)
sa = centre_a; sb = centre_b
cams = {
    'A wide': camera('A wide', [(1, A(2.3, -5.2, 2.05), A(0, .35, 1.25), 30), (96, A(1.95, -4.55, 1.98), A(0, .35, 1.25), 31)]),
    'A close': camera('A close', [(97, A(-.40, -1.10, 1.36), sa, 46), (228, A(-.28, -.92, 1.33), sa, 48)], focus=sa, fstop=2.8),
    # Focus on the desk, so the city behind the window softens and the screen leads.
    'B wide': camera('B wide', [(229, B(-2.2, -4.1, 1.75), B(0, 1.2, 1.45), 26), (324, B(-1.85, -3.55, 1.7), B(0, 1.2, 1.45), 27)],
                     focus=sb, fstop=2.0),
    # f/4 keeps the whole angled screen sharp (the DAW question sits left of centre); the city still softens.
    'B close': camera('B close', [(325, B(.42, -.08, 1.36), sb, 46), (456, B(.30, .10, 1.33), sb, 48)], focus=sb, fstop=4.0),
}
# Split-screen halves (960x1080 each); the render script renders both for frames 457–720.
SPLIT = {
    'A split': camera('A split', [(457, A(0, -2.05, 1.40), A(0, .2, 1.18), 24), (600, A(0, -2.3, 1.42), A(0, .2, 1.18), 24),
                                  (601, A(0, -2.3, 1.42), A(0, .2, 1.18), 24), (720, A(0, -4.4, 1.75), A(0, .3, 1.2), 22)]),
    'B split': camera('B split', [(457, B(0, -1.15, 1.40), B(0, 1.15, 1.18), 24), (600, B(0, -1.4, 1.42), B(0, 1.15, 1.18), 24),
                                  (601, B(0, -1.4, 1.42), B(0, 1.15, 1.18), 24), (720, B(0, -3.5, 1.75), B(0, 1.3, 1.25), 22)]),
}
for cam in SPLIT.values(): cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24
for marker in list(scene.timeline_markers): scene.timeline_markers.remove(marker)
for name, frame, key in SHOTS:
    scene.timeline_markers.new(name, frame=frame).camera = cams.get(key) or SPLIT['A split']

# ---------- render settings and a gentle bloom on the lit screens ----------
world = bpy.data.worlds.new('Dark ambience'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (.05, .06, .08, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = .05
scene.frame_start, scene.frame_end = 1, END
scene.render.fps, scene.render.fps_base = FPS, 1
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1920, 1080, 100
scene.render.engine = 'BLENDER_EEVEE'; scene.eevee.taa_render_samples = 48; scene.eevee.use_raytracing = True
scene.view_settings.view_transform = 'AgX'; scene.view_settings.look = 'AgX - Medium High Contrast'; scene.view_settings.exposure = .25
scene.render.image_settings.file_format = 'PNG'
tree = bpy.data.node_groups.new('Screen bloom', 'CompositorNodeTree')
tree.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
layers = tree.nodes.new('CompositorNodeRLayers'); bloom = tree.nodes.new('CompositorNodeGlare'); output = tree.nodes.new('NodeGroupOutput')
bloom.inputs['Type'].default_value = 'Bloom'; bloom.inputs['Quality'].default_value = 'High'
bloom.inputs['Threshold'].default_value = .55; bloom.inputs['Strength'].default_value = .45; bloom.inputs['Size'].default_value = .62
tree.links.new(layers.outputs['Image'], bloom.inputs['Image']); tree.links.new(bloom.outputs['Image'], output.inputs[0])
scene.compositing_node_group = tree
scene['scene_version'] = tag
scene['split_cameras'] = json.dumps({'A': 'A split', 'B': 'B split', 'from': 457})
scene['screen_centres'] = json.dumps({'A': list(centre_a), 'B': list(centre_b)})
scene['technical_honesty'] = ('Concept film. Screens: the real VST3 and the current desktop source with synthetic status. '
                              'No real save, share, transfer or peer connection was performed.')
scene.camera = cams['A wide']; scene.frame_set(1)
bpy.ops.file.pack_all()
output_path = ROOT / f'scenes/versions/trackmesh-{tag}.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
manifest = {'version': tag, 'blend': str(output_path), 'fps': FPS, 'frames': END, 'shots': SHOTS, 'plugin_states': PLUGIN, 'app_states': APP,
            'meshes': sum(o.type == 'MESH' for o in scene.objects)}
(ROOT / f'logs/{tag}.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print('TRACKMESH_STUDIOS ' + json.dumps(manifest))

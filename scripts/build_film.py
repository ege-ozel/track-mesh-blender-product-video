"""30-second TrackMesh concept film, built from the approved v02 studio.
Run: blender --background --factory-startup --python-exit-code 1 --python scripts/build_film.py
Screens use captures of the current desktop source and the real VST3 with synthetic status only.
Captions are added later in the edit (scripts/edit_film.py), so wording can change without re-rendering.
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
SCREENS = ROOT / 'assets/screens/v2'
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'scenes/versions/trackmesh-v02.blend'))
scene = bpy.context.scene
number = 1
while (ROOT / f'scenes/versions/trackmesh-film-v{number:02d}.blend').exists(): number += 1
tag = f'film-v{number:02d}'

FPS, END = 24, 720
# Shot boundaries (first frame of each shot) and what each one shows.
SHOTS = [('S1 / Two studios', 1), ('S2 / Save in the DAW', 97), ('S3 / Collaborator sees it', 229),
         ('S4 / Get when ready', 337), ('S5 / PC to PC', 469), ('S6 / Outro', 581)]
PLUGIN = [('idle', 1), ('saving', 141), ('shared', 181)]
APP = [('idle', 1), ('new', 292), ('getting', 441), ('done', 556)]

col = bpy.data.collections.new('09_Film'); scene.collection.children.link(col)

def show_between(obj, start, end):
    """Visible on [start, end] only; booleans use constant interpolation."""
    keys = {1: start > 1, start: False, end + 1: True}
    if start > 1: keys[start - 1] = True
    for frame, hidden in sorted(keys.items()):
        if frame > END + 1: continue
        obj.hide_render = hidden; obj.hide_viewport = hidden
        obj.keyframe_insert('hide_render', frame=frame); obj.keyframe_insert('hide_viewport', frame=frame)

def image(name):
    img = bpy.data.images.load(str(SCREENS / f'{name}.png'), check_existing=True); img.pack(); return img

def screen_material(base, img, label):
    mat = base.copy(); mat.name = label
    node = next(n for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE'); node.image = img; node.interpolation = 'Linear'
    return mat

# Studio B: one LCD copy per app state, each a hair in front of the last.
lcd_b = bpy.data.objects['Studio B independent LCD mesh']
base_b = lcd_b.data.materials[0]
for i, (state, start) in enumerate(APP):
    end = APP[i + 1][1] - 1 if i + 1 < len(APP) else END
    obj = lcd_b.copy(); obj.data = lcd_b.data.copy(); obj.name = f'Studio B app / {state}'
    col.objects.link(obj); obj.location.y -= .0004 * (i + 1)
    obj.data.materials.clear(); obj.data.materials.append(screen_material(base_b, image(f'app-{state}'), f'Studio B app / {state}'))
    show_between(obj, start, end)
lcd_b.hide_render = True; lcd_b.hide_viewport = True

# Studio A: the real VST3 editor floats over the DAW, one plane per plugin state.
base_a = bpy.data.objects['Studio A independent LCD mesh'].data.materials[0]
w = .46; h = w * 440 / 580; centre = (-1.25, .189, 1.236)
for i, (state, start) in enumerate(PLUGIN):
    end = PLUGIN[i + 1][1] - 1 if i + 1 < len(PLUGIN) else END
    mesh = bpy.data.meshes.new(f'VST3 {state}')
    mesh.from_pydata([(-w/2, 0, -h/2), (w/2, 0, -h/2), (w/2, 0, h/2), (-w/2, 0, h/2)], [], [(0, 1, 2, 3)]); mesh.update()
    uv = mesh.uv_layers.new(name='UV')
    for loop, co in zip(uv.data, [(0, 0), (1, 0), (1, 1), (0, 1)]): loop.uv = co
    obj = bpy.data.objects.new(f'Real VST3 editor / {state}', mesh); col.objects.link(obj)
    obj.location = (centre[0], centre[1] - .0004 * i, centre[2])
    mesh.materials.append(screen_material(base_a, image(f'vst3-{state}'), f'Real VST3 editor / {state}'))
    obj['provenance'] = 'Unmodified TrackMesh VST3 in the Steinberg SDK editor host; synthetic status.'
    show_between(obj, start, end)
bpy.ops.mesh.primitive_cube_add(size=1, location=(centre[0], .195, centre[2]))
border = bpy.context.object; border.name = 'VST3 window border'
for old in list(border.users_collection): old.objects.unlink(border)
col.objects.link(border); border.dimensions = (w + .006, .010, h + .006)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
border.data.materials.append(bpy.data.materials['Soft black polymer'])
border.modifiers.new('Corners', 'BEVEL').width = .002

def emission(name, rgb, strength):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    nodes = mat.node_tree.nodes; nodes.clear()
    em = nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*rgb, 1); em.inputs['Strength'].default_value = strength
    out = nodes.new('ShaderNodeOutputMaterial'); mat.node_tree.links.new(em.outputs[0], out.inputs['Surface'])
    return mat, em

# The direct link: a thin teal arc from monitor A to monitor B that draws itself in shot 3.
curve = bpy.data.curves.new('Direct link', 'CURVE'); curve.dimensions = '3D'
curve.bevel_depth = .0045; curve.bevel_resolution = 4; curve.resolution_u = 48
spline = curve.splines.new('BEZIER'); spline.bezier_points.add(2)
for point, co in zip(spline.bezier_points, [(-1.25, .27, 1.452), (0, .34, 1.93), (1.25, .27, 1.452)]):
    point.co = co; point.handle_left_type = point.handle_right_type = 'AUTO'
link = bpy.data.objects.new('Direct link arc', curve); col.objects.link(link)
link_mat, link_em = emission('Direct link / teal', (.06, .72, .58), 2.2)
curve.materials.append(link_mat)
link.visible_shadow = False
# A drawn concept line, not a cable: leave it out of the Studio B close-up.
for frame, hidden in [(1, False), (336, False), (337, True), (468, True), (469, False)]:
    link.hide_render = hidden; link.keyframe_insert('hide_render', frame=frame)
curve.bevel_factor_end = 0; curve.keyframe_insert('bevel_factor_end', frame=236)
curve.bevel_factor_end = 1; curve.keyframe_insert('bevel_factor_end', frame=266)
# Dim between moments, brighter while something travels.
for frame, value in [(236, 2.6), (300, 2.6), (316, 1.4), (469, 1.4), (480, 3.2), (560, 3.2), (590, 1.8)]:
    link_em.inputs['Strength'].default_value = value
    link_em.inputs['Strength'].keyframe_insert('default_value', frame=frame)

def traveller(name, size, start, length, material):
    bpy.ops.mesh.primitive_cube_add(size=size)
    obj = bpy.context.object; obj.name = name
    for old in list(obj.users_collection): old.objects.unlink(obj)
    col.objects.link(obj); obj.data.materials.append(material); obj.visible_shadow = False
    bevel = obj.modifiers.new('Round', 'BEVEL'); bevel.width = size * .25; bevel.segments = 3
    follow = obj.constraints.new('FOLLOW_PATH'); follow.target = link; follow.use_fixed_location = True; follow.use_curve_follow = True
    follow.forward_axis = 'FORWARD_X'; follow.up_axis = 'UP_Z'
    follow.offset_factor = 0; follow.keyframe_insert('offset_factor', frame=start)
    follow.offset_factor = 1; follow.keyframe_insert('offset_factor', frame=start + length)
    show_between(obj, start, start + length)
    return obj

# Shot 3: one small pulse, the new-version notice. Files do not move until Studio B presses Get.
pulse_mat, _ = emission('Notice pulse / white', (.7, 1, .9), 9)
traveller('Version notice pulse', .022, 262, 30, pulse_mat)
# Shot 5: after Get, project data travels PC to PC.
packet_mat, _ = emission('Project packets / teal', (.12, .9, .7), 5)
for i in range(12):
    traveller(f'Project packet {i + 1:02d}', .03, 472 + i * 7, 34, packet_mat)

# One camera per shot, each with its own slow move.
def camera(name, keys):
    cam = bpy.data.objects.new(name, bpy.data.cameras.new(name)); col.objects.link(cam)
    cam.data.sensor_width = 36
    for frame, location, target, lens in keys:
        cam.location = location
        cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
        cam.data.lens = lens
        cam.keyframe_insert('location', frame=frame); cam.keyframe_insert('rotation_euler', frame=frame)
        cam.data.keyframe_insert('lens', frame=frame)
    return cam

cameras = [
    camera('Film S1 wide', [(1, (2.6, -6.6, 2.28), (0, .26, 1.26), 43), (96, (2.42, -6.05, 2.2), (0, .26, 1.26), 44)]),
    camera('Film S2 DAW', [(97, (-1.66, -2.02, 1.48), (-1.25, .20, 1.22), 60), (228, (-1.52, -1.74, 1.44), (-1.25, .20, 1.22), 63)]),
    camera('Film S3 link', [(229, (-.35, -4.7, 1.98), (0, .25, 1.55), 31), (336, (.25, -4.3, 1.92), (0, .25, 1.55), 32)]),
    camera('Film S4 TrackMesh', [(337, (1.66, -2.02, 1.48), (1.25, .20, 1.21), 60), (468, (1.53, -1.74, 1.44), (1.25, .20, 1.21), 63)]),
    camera('Film S5 PC to PC', [(469, (-.2, -2.75, 1.78), (.65, .26, 1.45), 27), (580, (.15, -2.5, 1.72), (.75, .26, 1.43), 28)]),
    camera('Film S6 outro', [(581, (0, -4.5, 1.92), (0, .3, 1.45), 33), (720, (0, -6.9, 2.3), (0, .3, 1.38), 36)]),
]
for marker in list(scene.timeline_markers): scene.timeline_markers.remove(marker)
for (name, frame), cam in zip(SHOTS, cameras):
    scene.timeline_markers.new(name, frame=frame).camera = cam

scene.frame_start, scene.frame_end = 1, END
scene.render.fps, scene.render.fps_base = FPS, 1
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1920, 1080, 100
# EEVEE matched the Cycles look in side-by-side stills at about a tenth of the time.
scene.render.engine = 'BLENDER_EEVEE'; scene.eevee.taa_render_samples = 32; scene.eevee.use_raytracing = True
scene.render.use_motion_blur = False
scene.render.use_persistent_data = True
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(ROOT / f'renders/frames/{tag}/frame_')
scene['scene_version'] = tag
scene['technical_honesty'] = ('Concept film. Screens: current desktop source and the real VST3 with synthetic status. '
                              'No real save, share, transfer or peer connection was performed.')
scene.camera = cameras[0]; scene.frame_set(1)
bpy.ops.file.pack_all()
output = ROOT / f'scenes/versions/trackmesh-{tag}.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(output))
manifest = {'version': tag, 'blend': str(output), 'fps': FPS, 'frames': END, 'shots': SHOTS, 'plugin_states': PLUGIN, 'app_states': APP}
(ROOT / f'logs/{tag}.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print('TRACKMESH_FILM ' + json.dumps(manifest))

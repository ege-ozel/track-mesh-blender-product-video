"""Track Mesh procedural Blender 5.2 starter. Runs with --background --python build_scene.py [-- --preview].
Creates an editable .blend scene; only renders a 960x540 preview if --preview is given.
Existing .blend files are NOT overwritten unless directly running this script (the setup script skips existing files).
No private Track Mesh repo data or real DAW projects are accessed.
"""
import bpy
import math
import os
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(os.environ.get('TRACKMESH_VIDEO_PROJECT', str(Path.home() / 'TrackMeshVideo')))
SCENES = ROOT / 'scenes'
RENDERS = ROOT / 'renders' / 'previews'
SCREENS = ROOT / 'assets' / 'screens'
BACKGROUNDS = ROOT / 'assets' / 'backgrounds'
for folder in (SCENES, RENDERS):
    folder.mkdir(parents=True, exist_ok=True)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for material in list(bpy.data.materials):
    if material.users == 0:
        bpy.data.materials.remove(material)


def mat(name, rgb, metallic=0.0, roughness=0.5, emission=0.0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*rgb, 1.0)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*rgb, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    if emission > 0:
        bsdf.inputs['Emission Color'].default_value = (*rgb, 1.0)
        bsdf.inputs['Emission Strength'].default_value = emission
    return material


def image_material(name, path):
    if not path.exists():
        return None
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.node_tree.nodes.clear()
    nodes = material.node_tree.nodes
    image_node = nodes.new('ShaderNodeTexImage')
    image_node.image = bpy.data.images.load(str(path), check_existing=True)
    emission = nodes.new('ShaderNodeEmission')
    output = nodes.new('ShaderNodeOutputMaterial')
    material.node_tree.links.new(image_node.outputs['Color'], emission.inputs['Color'])
    material.node_tree.links.new(emission.outputs[0], output.inputs['Surface'])
    return material


def cube(name, location, scale, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        ob.data.materials.append(material)
    if bevel:
        mod = ob.modifiers.new('Soft machined edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        ob.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return ob


def surface(name, location, size, material):
    bpy.ops.mesh.primitive_plane_add(size=1, location=location, rotation=(math.pi / 2, 0, 0))
    ob = bpy.context.object
    ob.name = name
    ob.scale = (size[0], size[1], 1)
    if material:
        ob.data.materials.append(material)
    return ob


def curve_line(name, points, material, radius=0.012):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions = '3D'
    c.bevel_depth = radius
    c.bevel_resolution = 3
    poly = c.splines.new('POLY')
    poly.points.add(len(points) - 1)
    for point, xyz in zip(poly.points, points):
        point.co = (*xyz, 1)
    obj = bpy.data.objects.new(name, c)
    bpy.context.collection.objects.link(obj)
    c.materials.append(material)
    return obj


def area(name, location, power, rgb, shape, size):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = power
    data.color = rgb
    data.shape = shape
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    direction = Vector((0, 0, 1.5)) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def look_at(ob, xyz):
    direction = Vector(xyz) - ob.location
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

black = mat('Powder-black aluminum', (0.013, 0.021, 0.035), metallic=0.5, roughness=0.35)
frame = mat('Anodized steel', (0.07, 0.10, 0.15), metallic=0.7, roughness=0.23)
wood = mat('Desaturated charcoal desk', (0.05, 0.055, 0.065), metallic=0.15, roughness=0.48)
ground = mat('Midnight stage', (0.008, 0.012, 0.018), roughness=0.74)
left_glow = mat('Amber DAW interface', (0.85, 0.21, 0.06), emission=1.9)
right_glow = mat('Teal Track Mesh interface', (0.0, 0.68, 0.61), emission=2.0)
left_screen = mat('Left screen dark fill', (0.015, 0.024, 0.035), emission=0.7)
right_screen = mat('Right screen dark fill', (0.012, 0.028, 0.039), emission=0.7)
metal_light = mat('Tiny keyboard keys', (0.15, 0.18, 0.24), metallic=0.25)

cube('Stage floor', (0, 0.9, -0.13), (16, 13, 0.18), ground, .06)
cube('Desktop plank', (0, 0.20, 1.05), (9.5, 2.25, 0.15), wood, .08)
for legx in (-4.0, 4.0):
    cube('Desk leg', (legx, .82, .48), (.16, .17, .96), black, .035)


def workstation(label, x, filename, screen_mat, highlight):
    cube(f'{label} monitor housing', (x, .28, 2.25), (3.12, .20, 1.86), black, .085)
    cube(f'{label} screen frame', (x, .16, 2.27), (2.92, .06, 1.65), frame, .033)
    screen = image_material(f'{label} provided PNG screen', SCREENS / filename)
    surface(f'{label} screen display', (x, .105, 2.28), (2.78, 1.51), screen or screen_mat)
    cube(f'{label} stand neck', (x, .3, 1.30), (.16, .27, .66), frame, .026)
    cube(f'{label} stand base', (x, -.08, 1.14), (1.00, .67, .065), frame, .027)
    cube(f'{label} keyboard', (x, -.62, 1.16), (1.55, .38, .075), black, .035)
    for row in range(3):
        for col in range(14):
            cube(f'{label} key {row}:{col}', (x - .68 + col * .102, -.77 + row * .11, 1.207), (.075, .07, .012), metal_light, .003)
    if screen is None:
        # Stylized, deliberately fictitious placeholders (not the real Ableton/Track Mesh UI).
        for i in range(10):
            cube(f'{label} mock UI track {i}',
                 (x - 1.15 + i*.249, .061, 2.25 + .20*math.sin(i*.7)),
                 (.17, .008, .25 + .08*(i%3)), highlight, .005)
        cube(f'{label} UI top bar', (x, .055, 2.88), (2.6, .008, .05), highlight)
    cube(f'{label} status diode', (x+1.47, .02, 1.44), (.035, .035, .035), highlight, .01)

workstation('DAW computer / A', -2.42, 'daw.png', left_screen, left_glow)
workstation('Track Mesh computer / B', 2.42, 'trackmesh.png', right_screen, right_glow)

points = [(-.65, -.18, 2.11), (-.45, -.4, 2.45), (0, -.65, 2.68), (.45, -.4, 2.45), (.65, -.18, 2.11)]
curve_line('Direct P2P cable-of-light (symbolic)', points, right_glow, .018)
for j in range(9):
    obj = cube(f'Encrypted packet {j+1:02d}', (-.6, -.35, 2.3), (.038, .038, .038), right_glow, .008)
    start = 1 + j*8
    end = start+35
    for frame_num, frac in ((start,0),(end,1)):
        x = -.6+1.2*frac
        obj.location = (x, -.43 - .17*math.sin(math.pi*frac), 2.28+.45*math.sin(math.pi*frac))
        obj.keyframe_insert(data_path='location', frame=frame_num)
    obj.hide_render = False

background = image_material('User background image', BACKGROUNDS / 'studio.png')
if background:
    surface('Background image plane', (0, 3.4, 3.2), (14.5, 8.5), background)

world = bpy.context.scene.world
world.color = (0.012, .017, .027)
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (.012,.017,.027,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = .25
area('Soft key light', (-3.2, -3.0, 7.2), 1100, (.72,.82,1), 'DISK', 6)
area('Teal edge light', (4.5, 1.5, 4.9), 850, (.09, 1.0, .84), 'DISK', 4)
area('Amber accent light', (-5, 1, 3.7), 350, (1.0, .33, .14), 'DISK', 2.8)

cam_data = bpy.data.cameras.new('Animated product camera')
cam = bpy.data.objects.new('Animated product camera', cam_data)
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam
cam.location = (8.1, -12.9, 5.2)
look_at(cam, (0, 0, 1.65))
cam.keyframe_insert(data_path='location', frame=1)
cam.location = (6.1, -11.1, 4.3)
look_at(cam, (0, 0, 1.7))
cam.keyframe_insert(data_path='location', frame=120)
cam.data.type = 'PERSP'
cam.data.lens = 40

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 18
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.frame_start = 1
scene.frame_end = 120
scene.render.fps = 24
scene.frame_set(48)
scene.view_settings.view_transform = 'AgX'
scene.render.filepath = str(RENDERS / 'trackmesh-proof-of-concept.png')
scene.camera.data.dof.use_dof = False
scene.render.image_settings.color_mode = 'RGBA'
bpy.ops.wm.save_as_mainfile(filepath=str(SCENES / 'trackmesh-starter.blend'))
print('TRACKMESH: saved', SCENES / 'trackmesh-starter.blend')
if '--preview' in sys.argv:
    bpy.ops.render.render(write_still=True)
    print('TRACKMESH: preview', scene.render.filepath)

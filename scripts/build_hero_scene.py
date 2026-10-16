"""Editable, static Track Mesh hero studio. Blender --python build_hero_scene.py.
No animation, user preferences, addon installation, external assets or source changes.
Existing outputs are preserved: re-running creates the next numbered scene version.
"""
import bpy, math, json, argparse, sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--preview', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
versions = ROOT/'scenes/versions'
versions.mkdir(parents=True, exist_ok=True)
version = 1
while (versions/f'trackmesh-v{version:02d}.blend').exists(): version += 1
tag = f'v{version:02d}'

# This is a new process with factory startup; no existing user scene is loaded.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
collections = {}
for name in ('01_Architecture','02_Acoustic_Wall','03_Studio_A_DAW','04_Studio_B_TrackMesh','05_Lighting','06_Cameras'):
    col = bpy.data.collections.new(name)
    scene.collection.children.link(col)
    collections[name] = col
current = collections['01_Architecture']

def link(obj):
    for col in list(obj.users_collection): col.objects.unlink(obj)
    current.objects.link(obj)
    return obj

def material(name, color, rough=.5, metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    m.diffuse_color=(*color,1)
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metal
    return m

def texture_material(name, dark, light, scale, stretch, rough, bump_strength=.08):
    m=material(name,dark,rough)
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
    tex=n.new('ShaderNodeTexCoord')
    mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=stretch
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=3
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*dark,1);ramp.color_ramp.elements[1].color=(*light,1)
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=bump_strength;bump.inputs['Distance'].default_value=.0015
    l.new(tex.outputs['Generated'],mapping.inputs[0]);l.new(mapping.outputs['Vector'],noise.inputs['Vector'])
    l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
    l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    return m

def glow(name, color, strength):
    m=material(name,color,.4)
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=strength
    return m

graphite=material('Powder coated graphite',(.023,.027,.031),.44,.4)
metal=material('Brushed charcoal aluminum',(.12,.135,.145),.33,.8)
black=material('Soft black polymer',(.008,.01,.012),.6)
keys=material('Graphite keycaps',(.09,.105,.115),.54)
rubber=material('Rubber feet',(.006,.007,.008),.86)
wall=texture_material('Graphite plaster',(.012,.015,.018),(.027,.032,.037),45,(1,1,1),.89,.05)
felt=texture_material('Acoustic felt weave',(.015,.017,.019),(.043,.046,.048),170,(1,1,1),.95,.12)
floor=texture_material('Honed dark concrete',(.023,.027,.032),(.046,.053,.061),24,(1,1,1),.44,.13)
wood=texture_material('Natural smoked walnut',(.028,.013,.007),(.13,.060,.024),6,(.7,23,8),.43,.14)
slatwood=texture_material('Vertical smoked oak',(.065,.031,.012),(.19,.10,.043),5,(18,12,.45),.53,.08)
amber=glow('Warm practical diffuser',(1,.46,.14),3)
teal=glow('Cool practical diffuser',(.16,.65,.67),2.2)
diode=glow('Muted power LED',(.35,.6,.62),.45)

def box(name, loc, dim, mat, bevel=.008):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=link(bpy.context.object);o.name=name;o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if mat:o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new('Physical edge bevel','BEVEL');b.width=bevel;b.segments=3
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=loc,rotation=rotation)
    o=link(bpy.context.object);o.name=name;o.data.materials.append(mat)
    b=o.modifiers.new('Edge radius','BEVEL');b.width=.002;b.segments=2
    for p in o.data.polygons:p.use_smooth=True
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cable(name, points, radius=.003):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=radius;c.bevel_resolution=2
    s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c);current.objects.link(o);c.materials.append(rubber)
    return o

box('Continuous concrete floor',(0,-.8,-.065),(8,8,.13),floor,.015)
box('Solid rear studio wall',(0,1.55,1.5),(7.4,.18,3),wall,.012)
box('Left return wall',(-3.62,-.25,1.5),(.15,3.7,3),wall)
box('Right return wall',(3.62,-.25,1.5),(.15,3.7,3),wall)
box('Dark ceiling soffit',(0,1.28,2.92),(7.3,.58,.16),graphite)
box('Rear skirting',(0,1.438,.065),(7.22,.025,.13),graphite,.003)
for x in (-3.22,3.22):
    box('Corner pilaster',(x,1.40,1.47),(.12,.12,2.85),graphite)
    box('Recessed vertical diffuser',(x + (.09 if x<0 else -.09),1.405,1.52),(.012,.025,2.5),amber if x<0 else teal,.003)
current=collections['02_Acoustic_Wall']
for x in (-2.45,-.98,.98,2.45):
    box('Acoustic panel shadow mount',(x,1.408,1.86),(.94,.09,1.36),black,.014)
    box('Acoustic panel thick felt',(x,1.352,1.86),(.88,.07,1.30),felt,.025)
    if abs(x)<1.1:
        for i in range(12):
            box('Oak diffuser slat',(x-.41+i*.074,1.28,1.86),(.027,.06,1.29),slatwood,.003)
for side in (-1,1):
    for i in range(11):
        box('Corner wood batten',(side*(3.32+i*.025),1.295,1.46),(.013,.09,2.69),slatwood,.002)

def screen_material(label, filename):
    file=ROOT/'assets/screens'/filename
    if not file.exists():raise RuntimeError(f'Required screen texture missing: {file}')
    m=bpy.data.materials.new(label+' / packed real screen');m.use_nodes=True
    n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
    img=n.new('ShaderNodeTexImage');img.image=bpy.data.images.load(str(file),check_existing=True);img.image.pack();img.interpolation='Linear'
    emission=n.new('ShaderNodeEmission');emission.inputs['Strength'].default_value=.8
    output=n.new('ShaderNodeOutputMaterial');l.new(img.outputs['Color'],emission.inputs['Color']);l.new(emission.outputs[0],output.inputs['Surface'])
    return m

def screen_mesh(name, x, y, z, w, h, mat):
    mesh=bpy.data.meshes.new(name+' UV mesh')
    mesh.from_pydata([(-w/2,0,-h/2),(w/2,0,-h/2),(w/2,0,h/2),(-w/2,0,h/2)],[],[(0,1,2,3)])
    mesh.update();uv=mesh.uv_layers.new(name='ScreenUV')
    for loop,co in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=co
    o=bpy.data.objects.new(name,mesh);current.objects.link(o);o.location=(x,y,z);mesh.materials.append(mat)
    o['screen_source']=mat.name;o['physical_diagonal_inches']=34.33
    return o

def speaker(label,x):
    box(label+' nearfield speaker',(x,.20,.874),(.135,.135,.23),graphite,.014)
    cylinder(label+' woofer surround',(x,.127,.849),.043,.010,rubber,(math.pi/2,0,0))
    cylinder(label+' woofer',(x,.119,.849),.032,.006,black,(math.pi/2,0,0))
    cylinder(label+' tweeter',(x,.118,.938),.014,.006,metal,(math.pi/2,0,0))

def workstation(label, x, filename, col):
    global current
    current=collections[col]
    # Two separate 1.8m desks at standard 74cm working height.
    box(label+' walnut desktop',(x,0,.715),(1.8,.82,.05),wood,.018)
    box(label+' inset steel apron',(x,.04,.666),(1.64,.64,.042),graphite,.008)
    for dx in (-.76,.76):
        for dy in (-.29,.29):
            box(label+' steel leg',(x+dx,dy,.335),(.035,.035,.65),graphite,.004)
            box(label+' rubber foot',(x+dx,dy,.010),(.044,.044,.02),rubber,.004)
        box(label+' floor cross foot',(x+dx,0,.03),(.046,.69,.034),graphite,.004)
    box(label+' monitor housing',(x,.235,1.205),(.802,.047,.468),graphite,.014)
    box(label+' inset black bezel',(x,.208,1.208),(.784,.010,.449),black,.008)
    screen_mesh(label+' independent LCD mesh',x,.201,1.21,.760,.4275,screen_material(label,filename))
    box(label+' metal stand neck',(x,.244,.869),(.044,.034,.248),metal,.006)
    box(label+' weighted stand base',(x,.17,.755),(.28,.21,.025),metal,.009)
    box(label+' power indicator',(x+.353,.198,.984),(.004,.003,.002),diode,.001)
    box(label+' keyboard shell',(x-.08,-.238,.759),(.425,.138,.028),graphite,.009)
    for row in range(5):
        for k in range(15):
            if row==4 and 3<=k<=10:continue
            box(label+f' key {row:02d}-{k:02d}',(x-.274+k*.027,-.29+row*.025,.778),(.023,.021,.010),keys,.003)
    box(label+' spacebar',(x-.08,-.19,.779),(.192,.021,.010),keys,.003)
    box(label+' desk mat',(x+.34,-.235,.744),(.25,.22,.005),felt,.018)
    mouse=box(label+' mouse',(x+.34,-.235,.765),(.056,.105,.035),graphite,.017)
    box(label+' mouse wheel',(x+.34,-.265,.784),(.004,.014,.005),rubber,.002)
    for dx in (-.62,.62):speaker(label,x+dx)
    # Quiet small-form-factor PC under each desk, no neon components.
    box(label+' computer tower',(x+.51,.10,.27),(.19,.34,.50),graphite,.017)
    box(label+' PC front panel',(x+.51,-.075,.28),(.166,.007,.455),black,.009)
    for i in range(9):box(label+' PC vent',(x+.51,-.081,.18+i*.013),(.115,.003,.002),metal,.001)
    cylinder(label+' PC power button',(x+.51,-.082,.447),.006,.002,metal,(math.pi/2,0,0))
    cable(label+' monitor power cable',[(x,.267,1.09),(x+.07,.34,.88),(x+.08,.41,.68),(x+.50,.31,.51)])
    cable(label+' keyboard cable',[(x-.08,-.17,.76),(x-.26,.03,.745),(x-.30,.35,.745)])
    # Small restrained desktop audio interface, aluminum + two controls.
    box(label+' audio interface',(x-.53,-.20,.781),(.18,.135,.073),metal,.008)
    for dx in (-.046,.046):cylinder(label+' interface control',(x-.53+dx,-.270,.782),.014,.010,graphite,(math.pi/2,0,0))

workstation('Studio A',-1.25,'daw.png','03_Studio_A_DAW')
workstation('Studio B',1.25,'trackmesh.png','04_Studio_B_TrackMesh')

current=collections['05_Lighting']
def area(name,loc,target,power,color,size,size_y=None):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.color=color
    data.shape='RECTANGLE' if size_y else 'DISK';data.size=size
    if size_y:data.size_y=size_y
    o=bpy.data.objects.new(name,data);current.objects.link(o);o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    return o
area('Large soft studio key',(0,-2.1,3.25),(0,0,.95),60,(.84,.89,1),4,2)
area('Warm left key',(-2.8,-.45,2.25),(-1.25,.15,1.0),90,(1,.48,.19),1.5,2)
area('Soft teal right rim',(3.0,.4,2.3),(1.25,.10,1.1),70,(.21,.65,.69),1.0,1.7)
area('Warm wall wash',(-2.35,.90,2.72),(-2.3,1.42,1.5),18,(1,.55,.25),.7,.25)
area('Cool wall wash',(2.25,.90,2.72),(2.3,1.42,1.5),12,(.26,.67,.72),.7,.25)
for x in (-3.14,3.14):
    area('Recess glow bounce',(x,1.18,1.42),(x*.65,.2,1),12,(1,.49,.18) if x<0 else (.17,.63,.67),.04,2)
world=bpy.data.worlds.new('Controlled studio ambience');scene.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.065,.075,.09,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.08

current=collections['06_Cameras']
camera_specs=[
    ('A_Establishing',(2.6,-6.6,2.28),(0,.26,1.26),43),
    ('B_DAW',(-1.69,-1.84,1.46),(-1.25,.20,1.21),64),
    ('C_TrackMesh',(1.57,-1.78,1.45),(1.25,.20,1.21),66)
]
cameras=[]
for name,loc,target,lens in camera_specs:
    d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_start=.05;d.clip_end=100
    d.dof.use_dof=False
    o=bpy.data.objects.new(name,d);current.objects.link(o);o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();cameras.append(o)
    o['purpose']='Static hero composition; no camera animation.'
scene.camera=cameras[0]
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.cycles.max_bounces=6;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3
scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.035
scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
scene.render.film_transparent=False;scene.render.fps=24;scene.frame_start=1;scene.frame_end=1
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.1
scene['production_stage']='Hero only. Awaiting visual approval; no animation or product operation.'
scene['technical_honesty']='TrackMesh screenshot = real React UI + synthetic fixture; DIRECT is a demo status, not WAN validation.'
scene['studio_reference']='assets/backgrounds/studio.png is reference only; no image backdrop plane.'
scene['scene_version']=tag
# Runtime device discovery; never save user preferences or infer GPU readiness.
probe_path=ROOT/'logs/environment-blender.json'
backend=json.loads(probe_path.read_text())['selection'] if probe_path.exists() else 'CPU'
prefs=bpy.context.preferences.addons['cycles'].preferences
if backend!='CPU':
    try:
        prefs.compute_device_type=backend;prefs.get_devices()
        for d in prefs.devices:d.use=d.type==backend
        scene.cycles.device='GPU'
    except Exception:scene.cycles.device='CPU';backend='CPU'
else:scene.cycles.device='CPU'
scene['render_backend']=backend
scene.render.filepath=str(ROOT/'renders/previews'/f'hero-{tag}-A.png')
# Show the complete studio immediately when opened interactively.
for screen in bpy.data.screens:
    for area_ui in screen.areas:
        if area_ui.type=='VIEW_3D':
            space=area_ui.spaces.active;space.region_3d.view_perspective='CAMERA'
            space.shading.type='MATERIAL';space.shading.use_scene_lights=True;space.shading.use_scene_world=True
            space.overlay.show_overlays=False
bpy.ops.file.pack_all()
output=versions/f'trackmesh-{tag}.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(output))
manifest={'blend':str(output),'version':tag,'backend':backend,'cameras':[o.name for o in cameras],
  'mesh_count':sum(o.type=='MESH' for o in scene.objects),'animated_objects':sum(bool(o.animation_data) for o in scene.objects),
  'image_assets':[{'name':img.name,'packed':bool(img.packed_file)} for img in bpy.data.images if img.source=='FILE'],
  'settings':{'engine':'CYCLES','width':960,'height':540,'samples':24,'denoising':True}}
(ROOT/'logs'/f'scene-{tag}.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('TRACKMESH_SCENE '+json.dumps(manifest))
if args.preview:
    for camera in cameras:
        scene.camera=camera;scene.render.filepath=str(ROOT/'renders/previews'/f'hero-{tag}-{camera.name[0]}.png')
        bpy.ops.render.render(write_still=True)

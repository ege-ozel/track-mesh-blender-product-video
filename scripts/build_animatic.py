"""Three-second A+B timing study, derived read-only from the approved v02.
Run using project Blender: --background --factory-startup --python build_animatic.py.
No actual DAW save, snapshot creation, native API call, transfer or source change.
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'scenes/versions/trackmesh-v02.blend'
bpy.ops.wm.open_mainfile(filepath=str(base))
scene=bpy.context.scene
number=3
while (ROOT/f'scenes/versions/trackmesh-v{number:02d}.blend').exists():number+=1
tag=f'v{number:02d}'
output=ROOT/f'scenes/versions/trackmesh-{tag}.blend'
graphics=bpy.data.collections.new('07_Animatic_Concept_Titles')
scene.collection.children.link(graphics)
camera_a=bpy.data.objects['A_Establishing'];camera_b=bpy.data.objects['B_DAW']

def pose(camera,frame,location,target,lens):
    camera.location=location
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.lens=lens
    camera.keyframe_insert(data_path='location',frame=frame)
    camera.keyframe_insert(data_path='rotation_euler',frame=frame)
    camera.data.keyframe_insert(data_path='lens',frame=frame)

pose(camera_a,1,(2.6,-6.6,2.28),(0,.26,1.26),43)
pose(camera_a,24,(2.54,-6.36,2.25),(0,.26,1.26),43.4)
pose(camera_b,25,(-1.65,-2.0,1.48),(-1.25,.20,1.21),61)
pose(camera_b,72,(-1.56,-1.84,1.45),(-1.25,.20,1.21),64)
camera_a['purpose']='Shot A / slow establishing dolly, frames 1-24'
camera_b['purpose']='Shot B / DAW close-up dolly, frames 25-72'

for marker in list(scene.timeline_markers):scene.timeline_markers.remove(marker)
for name,frame,camera in [('A / ESTABLISH',1,camera_a),('B / DAW CLOSE',25,camera_b)]:
    marker=scene.timeline_markers.new(name,frame=frame);marker.camera=camera
for name,frame in [('CONCEPT / SAVE OBSERVED',31),('CONCEPT / SETTLING',41),('CONCEPT / SNAPSHOT READY',57)]:
    scene.timeline_markers.new(name,frame=frame)

def emission(name,rgb,strength=1):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    nodes=mat.node_tree.nodes;nodes.clear()
    shader=nodes.new('ShaderNodeEmission');shader.inputs['Color'].default_value=(*rgb,1);shader.inputs['Strength'].default_value=strength
    out=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(shader.outputs[0],out.inputs['Surface'])
    return mat
ink=emission('Concept caption / soft white',(.64,.71,.72),.8)
amber=emission('Concept save caption / warm',(.82,.45,.13),.9)
mint=emission('Concept ready caption / muted mint',(.35,.65,.50),.9)
muted=emission('Concept caption / secondary',(.26,.32,.36),.9)
panel=emission('Concept caption / dark panel',(.009,.014,.020),.65)

def plane(name,w,h,location,material,parent=None):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([(-w/2,-h/2,0),(w/2,-h/2,0),(w/2,h/2,0),(-w/2,h/2,0)],[],[(0,1,2,3)])
    mesh.update();obj=bpy.data.objects.new(name,mesh);graphics.objects.link(obj)
    obj.data.materials.append(material);obj.parent=parent;obj.location=location
    obj.visible_shadow=False;obj.visible_diffuse=False;obj.visible_glossy=False
    return obj

def text(name,body,location,size,material,parent=None,rotation=(0,0,0)):
    curve=bpy.data.curves.new(name,'FONT');curve.body=body;curve.size=size;curve.align_y='CENTER';curve.space_character=1.05
    obj=bpy.data.objects.new(name,curve);graphics.objects.link(obj)
    obj.parent=parent;obj.location=location;obj.rotation_euler=rotation
    curve.materials.append(material);obj.visible_shadow=False;obj.visible_diffuse=False;obj.visible_glossy=False
    return obj

def visible_between(objects,start,end):
    for obj in objects:
        # Boolean keyframes use constant interpolation.
        for frame,hidden in [(1,start>1),(max(1,start-1),start>1),(start,False),(end,False),(end+1,True)]:
            obj.hide_render=hidden;obj.hide_viewport=hidden
            obj.keyframe_insert(data_path='hide_render',frame=frame)
            obj.keyframe_insert(data_path='hide_viewport',frame=frame)

# A quiet camera-space editorial tag, separate from the actual product screen.
for camera,start,end in [(camera_a,1,24),(camera_b,25,72)]:
    # Different focal lengths have different 1m camera-space frustums.
    # Lens stored in mm; plane is 1m from lens.
    half_width=36/(2*(43 if camera==camera_a else 64))
    half_height=half_width*9/16
    width=half_width*.46;height=half_width*.064
    center_x=half_width*.68;center_y=half_height*.88
    p=plane(camera.name+' concept tag backing',width,height,(center_x,center_y,-1),panel,camera)
    label=text(camera.name+' permanent concept label','Concept Visualization',
      (center_x-width*.44,center_y,-.998),half_width*.028,ink,camera)
    visible_between([p,label],start,end)

# Screen-local concept toast is actual editable geometry in front of the DAW LCD.
# It is NOT represented as a real Track Mesh UI control or verified automation.
rotation=(math.pi/2,0,0)
for label,title,subtitle,start,end,color in [
    ('01_Save','Save observed','Concept: DAW save trigger',31,40,amber),
    ('02_Settle','Waiting for files to settle','Concept: local preparation',41,56,ink),
    ('03_Ready','Snapshot ready','Local snapshot only',57,72,mint)
]:
    backing=plane(label+' toast backing',.388,.066,(-1.07,.193,1.051),panel)
    backing.rotation_euler=rotation
    title_obj=text(label+' title',title,(-1.25,.191,1.061),.014,color,rotation=rotation)
    subtitle_obj=text(label+' subtitle',subtitle,(-1.25,.190,1.039),.009,muted,rotation=rotation)
    visible_between([backing,title_obj,subtitle_obj],start,end)

scene.frame_start=1;scene.frame_end=72;scene.render.fps=24;scene.render.fps_base=1
scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.cycles.adaptive_threshold=.05
scene.render.use_motion_blur=False
scene['scene_version']=tag
scene['approved_base']='trackmesh-v02.blend'
scene['production_stage']='A+B concept animatic only / 72 frames at 24fps / 3 seconds. Awaiting motion approval.'
scene['technical_honesty']='Save-triggered preparation is an unverified concept. Screen toast is illustrative, not real UI. No transfer or actual save occurs.'
scene.camera=camera_a;scene.frame_set(1)
scene.render.filepath=str(ROOT/f'renders/frames/animatic-{tag}/frame_')
bpy.ops.wm.save_as_mainfile(filepath=str(output))
manifest={
  'version':tag,'base':str(base),'blend':str(output),'fps':24,'frames':72,'duration_seconds':3,
  'resolution':[960,540],'engine':'CYCLES','samples':16,'denoising':True,
  'stills':{'A':13,'B':64},
  'shots':[{'name':'A','range':[1,24],'camera':camera_a.name},{'name':'B','range':[25,72],'camera':camera_b.name}],
  'concept_states':[{'label':'Save observed','range':[31,40]},{'label':'Waiting for files to settle','range':[41,56]},{'label':'Snapshot ready','range':[57,72]}],
  'concept_label':'Concept Visualization / visible throughout',
  'no_actual_save_or_transfer':True
}
(ROOT/f'logs/animatic-{tag}.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('TRACKMESH_ANIMATIC '+json.dumps(manifest))

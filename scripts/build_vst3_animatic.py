"""Keep approved v04 timing; show the captured genuine native VST3 in shot B."""
import bpy,json,shutil,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'scenes/versions/trackmesh-v04.blend'
bpy.ops.wm.open_mainfile(filepath=str(base));scene=bpy.context.scene
number=5
while (ROOT/f'scenes/versions/trackmesh-v{number:02d}.blend').exists():number+=1
tag=f'v{number:02d}'
capture=ROOT/'assets/screens/trackmesh-vst3-native.png'
if not capture.exists():raise RuntimeError('Capture the actual native VST3 before building this revision.')
col=bpy.data.collections.new('08_Real_VST3_Captured_Editor');scene.collection.children.link(col)
mat=bpy.data.materials.new('Actual native VST3 / packed unmodified UI capture');mat.use_nodes=True
nodes=mat.node_tree.nodes;links=mat.node_tree.links;nodes.clear()
texture=nodes.new('ShaderNodeTexImage');texture.image=bpy.data.images.load(str(capture),check_existing=True);texture.image.pack()
texture.interpolation='Linear'
emission=nodes.new('ShaderNodeEmission');emission.inputs['Strength'].default_value=.8
out=nodes.new('ShaderNodeOutputMaterial');links.new(texture.outputs['Color'],emission.inputs['Color']);links.new(emission.outputs[0],out.inputs['Surface'])
w=.46;h=w*400/580
mesh=bpy.data.meshes.new('Native VST3 window UV mesh')
mesh.from_pydata([(-w/2,0,-h/2),(w/2,0,-h/2),(w/2,0,h/2),(-w/2,0,h/2)],[],[(0,1,2,3)])
mesh.update();uv=mesh.uv_layers.new(name='NativeEditorUV')
for loop,co in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=co
editor=bpy.data.objects.new('Actual TRACKMESH VST3 editor image',mesh);col.objects.link(editor)
editor.location=(-1.25,.189,1.252);mesh.materials.append(mat)
editor['provenance']='Actual unmodified VST3, SDK editor host, PrintWindow capture. Synthetic status only.'
bpy.ops.mesh.primitive_cube_add(size=1,location=(-1.25,.195,1.252))
border=bpy.context.object;border.name='VST3 floating window border'
for old in list(border.users_collection):old.objects.unlink(border)
col.objects.link(border);border.dimensions=(w+.006,.010,h+.006)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
border.data.materials.append(bpy.data.materials['Soft black polymer'])
bevel=border.modifiers.new('Window corner radius','BEVEL');bevel.width=.002;bevel.segments=3
border.modifiers.new('Window normals','WEIGHTED_NORMAL')
for obj in (editor,border):
    for frame,hidden in [(1,True),(24,True),(25,False),(72,False)]:
        obj.hide_render=hidden;obj.hide_viewport=hidden
        obj.keyframe_insert(data_path='hide_render',frame=frame);obj.keyframe_insert(data_path='hide_viewport',frame=frame)
scene['scene_version']=tag
scene['approved_motion_base']='trackmesh-v04.blend'
scene['production_stage']='A+B animatic / actual native VST3 capture / approved tempo unchanged'
scene['technical_honesty']='Native editor from a real, unmodified TrackMesh VST3; status is synthetic. SDK host capture is not real DAW Save or transfer validation.'
scene.render.filepath=str(ROOT/f'renders/frames/animatic-{tag}/frame_')
scene.frame_set(1);bpy.ops.file.pack_all()
output=ROOT/f'scenes/versions/trackmesh-{tag}.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(output))
manifest=json.loads((ROOT/'logs/animatic-v04.json').read_text())
manifest.update({'version':tag,'base':str(base),'blend':str(output),'native_vst3':str(capture),
  'native_vst3_visible_frames':[25,72],'motion_identical_to_v04':True,'reuse_shot_A_from':'v04'})
(ROOT/f'logs/animatic-{tag}.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
frames=ROOT/f'renders/frames/animatic-{tag}';frames.mkdir(parents=True,exist_ok=True)
# Shot A is pixel-identical: native editor is deliberately revealed at the cut.
for frame in range(1,25):
    source=ROOT/f'renders/frames/animatic-v04/frame_{frame:04d}.png';dest=frames/f'frame_{frame:04d}.png'
    if source.exists() and not dest.exists():shutil.copy2(source,dest)
print('TRACKMESH_NATIVE_VST3_SCENE '+json.dumps(manifest))

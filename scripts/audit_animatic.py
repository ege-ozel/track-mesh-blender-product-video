"""Scene inspection: camera cuts, state visibility and screen framing across 72 frames."""
import bpy,json
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene;tag=scene['scene_version']
lcd=bpy.data.objects['Studio A independent LCD mesh']
rows=[]
for frame in range(1,73):
    scene.frame_set(frame)
    expected_camera='A_Establishing' if frame<=24 else 'B_DAW'
    assert scene.camera.name==expected_camera,(frame,scene.camera.name)
    tags=[o.name for o in scene.objects if o.name.endswith('permanent concept label') and not o.hide_render]
    assert len(tags)==1,(frame,tags)
    states=[o.data.body for o in scene.objects if o.type=='FONT' and o.name.endswith(' title') and not o.hide_render]
    expected=[] if frame<31 else ['Save observed'] if frame<=40 else ['Waiting for files to settle'] if frame<=56 else ['Snapshot ready']
    assert states==expected,(frame,states,expected)
    row={'frame':frame,'camera':scene.camera.name,'concept_label':tags[0],'visible_state':states}
    native=bpy.data.objects.get('Actual TRACKMESH VST3 editor image')
    if native:
        assert native.hide_render==(frame<25),(frame,'native VST3 visibility')
        row['native_vst3_visible']=not native.hide_render
        if frame>=25:
            projected=[world_to_camera_view(scene,scene.camera,native.matrix_world@v.co) for v in native.data.vertices]
            assert all(0<p.x<1 and 0<p.y<1 and p.z>0 for p in projected),(frame,'native editor clipped')
    if frame>=25:
        points=[world_to_camera_view(scene,scene.camera,lcd.matrix_world@v.co) for v in lcd.data.vertices]
        bounds={'min_x':min(p.x for p in points),'max_x':max(p.x for p in points),'min_y':min(p.y for p in points),'max_y':max(p.y for p in points),'min_depth':min(p.z for p in points)}
        assert bounds['min_x']>0 and bounds['max_x']<1 and bounds['min_y']>0 and bounds['max_y']<1 and bounds['min_depth']>0,(frame,bounds)
        row['lcd_projection']=bounds
    rows.append(row)
result={'blend':bpy.data.filepath,'frames_checked':72,'camera_cut_frame':25,
  'concept_label_visible_every_frame':True,'state_sequence_exact':True,'daw_screen_not_clipped':True,'frames':rows}
if bpy.data.objects.get('Actual TRACKMESH VST3 editor image'):
    result['native_vst3_visibility_and_framing']=True
(ROOT/f'logs/animatic-audit-{tag}.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('TRACKMESH_AUDIT 72 frames: camera cuts, concept label, state sequence and LCD projection PASS')

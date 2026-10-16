"""Compare approved camera poses/lenses at every frame without modifying files."""
import bpy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
target=Path(bpy.data.filepath)
def samples():
    rows=[]
    for frame in range(1,73):
        bpy.context.scene.frame_set(frame);camera=bpy.context.scene.camera
        rows.append({'frame':frame,'camera':camera.name,'location':list(camera.location),'rotation':list(camera.rotation_euler),'lens':camera.data.lens})
    return rows
actual=samples()
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scenes/versions/trackmesh-v04.blend'))
approved=samples()
assert actual==approved,'Camera motion differs from approved v04'
result={'target':str(target),'approved_base':'trackmesh-v04.blend','frames':72,'camera_pose_and_lens_identical':True}
(ROOT/f'logs/native-motion-{target.stem}.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('TRACKMESH_NATIVE_MOTION 72 frames: camera transforms, lens and cut identical to approved v04 PASS')

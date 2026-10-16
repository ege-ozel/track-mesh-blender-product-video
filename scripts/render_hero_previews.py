"""Render three static cameras from a saved blend; do not modify the blend."""
import bpy, json, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
backend=scene.get('render_backend','CPU')
if backend!='CPU':
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type=backend;prefs.get_devices()
    for d in prefs.devices:d.use=d.type==backend
    scene.cycles.device='GPU'
result=[]
tag=scene['scene_version']
for letter in 'ABC':
    camera=next(o for o in scene.objects if o.type=='CAMERA' and o.name.startswith(letter+'_'))
    scene.camera=camera
    target=ROOT/'renders/previews'/f'hero-{tag}-{letter}.png'
    if target.exists():raise RuntimeError(f'Preserving existing preview: {target}')
    scene.render.filepath=str(target)
    start=time.time()
    try:bpy.ops.render.render(write_still=True)
    except RuntimeError:
        if scene.cycles.device!='GPU':raise
        print('GPU render failed; retrying this still on CPU.')
        scene.cycles.device='CPU';bpy.ops.render.render(write_still=True)
    result.append({'camera':camera.name,'file':str(target),'seconds':round(time.time()-start,2),'device':scene.cycles.device})
    print('TRACKMESH_RENDER '+json.dumps(result[-1]))
(ROOT/'logs'/f'renders-{tag}.json').write_text(json.dumps(result,indent=2),encoding='utf-8')

"""Render stills first or the approved three-second timing study. Resumable frames."""
import bpy,json,time,argparse,sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--stills-only',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
scene=bpy.context.scene;tag=scene['scene_version']
backend=scene.get('render_backend','CPU')
if backend!='CPU':
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type=backend;prefs.get_devices()
    for device in prefs.devices:device.use=device.type==backend
    scene.cycles.device='GPU'
manifest=json.loads((ROOT/f'logs/animatic-{tag}.json').read_text())
frames_dir=ROOT/f'renders/frames/animatic-{tag}';frames_dir.mkdir(parents=True,exist_ok=True)
entries=[]
if args.stills_only:
    jobs=[(frame,ROOT/f'renders/previews/animatic-{tag}-{name}.png') for name,frame in manifest['stills'].items()]
else:
    # Previously reviewed stills are identical frames; reuse their pixels.
    for name,frame in manifest['stills'].items():
        source=ROOT/f'renders/previews/animatic-{tag}-{name}.png';dest=frames_dir/f'frame_{frame:04d}.png'
        if source.exists() and not dest.exists():shutil.copy2(source,dest)
    jobs=[(frame,frames_dir/f'frame_{frame:04d}.png') for frame in range(1,73)]
for frame,path in jobs:
    if path.exists():
        print(f'TRACKMESH_PRESERVED {frame} {path}',flush=True);continue
    scene.frame_set(frame);scene.render.filepath=str(path)
    started=time.time()
    try:bpy.ops.render.render(write_still=True)
    except RuntimeError:
        if scene.cycles.device!='GPU':raise
        scene.cycles.device='CPU';bpy.ops.render.render(write_still=True)
    item={'frame':frame,'camera':scene.camera.name,'file':str(path),'seconds':round(time.time()-started,2),'device':scene.cycles.device}
    entries.append(item);print('TRACKMESH_ANIMATIC_RENDER '+json.dumps(item),flush=True)
    mode='stills' if args.stills_only else 'frames'
    (ROOT/f'logs/animatic-render-{tag}-{mode}.json').write_text(json.dumps(entries,indent=2),encoding='utf-8')

"""Render frames of a studios-vNN scene. Split-screen frames render both halves (A and B cameras, half width)
and record where each screen centre lands, so the edit can draw the link between the rooms.
blender --background scenes/versions/trackmesh-studios-vNN.blend --python scripts/render_studios.py -- [--stills 50,160] [--percent 50]
Existing images are kept, so runs resume.
"""
import bpy, json, time, argparse, sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--stills', default='')
parser.add_argument('--percent', type=int, default=100)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
scene = bpy.context.scene; tag = scene['scene_version']
split = json.loads(scene['split_cameras']); centres = json.loads(scene['screen_centres'])
scene.render.resolution_percentage = args.percent
if args.stills:
    frames = [int(f) for f in args.stills.split(',')]
    folder = ROOT / f'renders/previews/{tag}-{args.percent}'
else:
    frames = list(range(scene.frame_start, scene.frame_end + 1))
    folder = ROOT / f'renders/frames/{tag}'
folder.mkdir(parents=True, exist_ok=True)
log = ROOT / f'logs/render-{tag}-{"stills" if args.stills else "frames"}.jsonl'
points = folder / 'split-points.json'
projected = json.loads(points.read_text()) if points.exists() else {}

def render(path, camera=None, width=1920):
    if path.exists(): return None
    if camera:
        # Markers decide the render camera, so point the marker in force at this half's camera
        # (in this process only; the .blend is not saved).
        active = max((m for m in scene.timeline_markers if m.frame <= scene.frame_current), key=lambda m: m.frame)
        active.camera = scene.camera = bpy.data.objects[camera]
    scene.render.resolution_x = width; scene.render.filepath = str(path)
    started = time.time(); bpy.ops.render.render(write_still=True)
    return round(time.time() - started, 2)

for frame in frames:
    scene.frame_set(frame)
    if frame < split['from']:
        jobs = [(folder / f'frame_{frame:04d}.png', None, 1920)]
    else:
        jobs = [(folder / f'frame_{frame:04d}_{side}.png', split[side], 960) for side in ('A', 'B')]
    for path, camera, width in jobs:
        seconds = render(path, camera, width)
        if camera:
            # Normalised (0..1, origin bottom-left) screen centre inside this half.
            scene.render.resolution_x = width
            spot = world_to_camera_view(scene, bpy.data.objects[camera], Vector(centres[path.stem[-1]]))
            projected[path.name] = [round(spot.x, 4), round(spot.y, 4)]
        if seconds is not None:
            item = {'frame': frame, 'camera': scene.camera.name, 'file': path.name, 'seconds': seconds, 'percent': args.percent}
            with log.open('a', encoding='utf-8') as f: f.write(json.dumps(item) + '\n')
            print('TRACKMESH_STUDIOS_RENDER ' + json.dumps(item), flush=True)
points.write_text(json.dumps(projected, indent=2), encoding='utf-8')

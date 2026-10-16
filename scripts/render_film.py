"""Render film stills or the full frame sequence (EEVEE, or Cycles on OptiX). Existing frames are kept, so runs resume.
blender --background scenes/versions/trackmesh-film-vNN.blend --python scripts/render_film.py -- [--stills 50,160,...] [--percent 50]
"""
import bpy, json, time, argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--stills', default='')
parser.add_argument('--percent', type=int, default=100)
parser.add_argument('--samples', type=int, default=0)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
scene = bpy.context.scene; tag = scene['scene_version']
if scene.render.engine == 'CYCLES':
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'; prefs.get_devices()
    for device in prefs.devices: device.use = device.type == 'OPTIX'
    scene.cycles.device = 'GPU'
scene.render.resolution_percentage = args.percent
if args.samples: scene.cycles.samples = args.samples
if args.stills:
    jobs = [(int(f), ROOT / f'renders/previews/{tag}-f{int(f):04d}-{args.percent}.png') for f in args.stills.split(',')]
else:
    frames = ROOT / f'renders/frames/{tag}'; frames.mkdir(parents=True, exist_ok=True)
    jobs = [(f, frames / f'frame_{f:04d}.png') for f in range(scene.frame_start, scene.frame_end + 1)]
log = ROOT / f'logs/render-{tag}-{"stills" if args.stills else "frames"}.jsonl'
for frame, path in jobs:
    if path.exists(): continue
    scene.frame_set(frame); scene.render.filepath = str(path)
    started = time.time()
    bpy.ops.render.render(write_still=True)
    item = {'frame': frame, 'camera': scene.camera.name, 'seconds': round(time.time() - started, 2), 'percent': args.percent}
    with log.open('a', encoding='utf-8') as f: f.write(json.dumps(item) + '\n')
    print('TRACKMESH_FILM_RENDER ' + json.dumps(item), flush=True)

"""Inspect a saved studio scene over all 720 frames without rendering or product actions."""
import bpy
import json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
tag = scene['scene_version']
split = json.loads(scene['split_cameras'])
centres = json.loads(scene['screen_centres'])
failures = []
def check(condition, message):
    if not condition:
        failures.append(message)

check((scene.render.resolution_x, scene.render.resolution_y, scene.render.fps) == (1920, 1080, 24), 'Output format differs from 1080p / 24 fps')
check((scene.frame_start, scene.frame_end) == (1, 720), 'Timeline differs from 30 seconds')
check(len(scene.timeline_markers) == 6, 'Expected six shot markers')
images = []
for img in bpy.data.images:
    if img.source == 'FILE':
        images.append({'name': img.name, 'packed': bool(img.packed_file), 'size': list(img.size)})
        check(bool(img.packed_file), f'Unpacked image: {img.name}')
        check(all(img.size), f'Invalid image: {img.name}')

markers = sorted(scene.timeline_markers, key=lambda m: m.frame)
groups = {prefix: [o for o in scene.objects if o.name.startswith(prefix + ' / ')]
          for prefix in ('Studio A plugin', 'Studio B app')}
minimum_margin = {'A': 1, 'B': 1}
for frame in range(1, 721):
    scene.frame_set(frame)
    for prefix, objects in groups.items():
        visible = [o.name for o in objects if not o.hide_render]
        check(len(visible) == 1, f'Frame {frame}: {prefix} visible states {visible}')
    active = max((m for m in markers if m.frame <= frame), key=lambda m: m.frame)
    if frame < split['from']:
        side = 'A' if frame < 229 else 'B'
        cameras = [(side, active.camera, 1920)]
    else:
        cameras = [(side, bpy.data.objects[split[side]], 960) for side in 'AB']
    for side, camera, width in cameras:
        scene.render.resolution_x = width
        p = world_to_camera_view(scene, camera, Vector(centres[side]))
        check(p.z > camera.data.clip_start and p.z < camera.data.clip_end, f'Frame {frame}: {camera.name} screen clipped in depth')
        check(0 < p.x < 1 and 0 < p.y < 1, f'Frame {frame}: {camera.name} screen centre outside view')
        minimum_margin[side] = min(minimum_margin[side], p.x, 1-p.x, p.y, 1-p.y)
        # All four screen corners must stay inside the image, including moving closeups.
        for dx in (-.380, .380):
            for dz in (-.21375, .21375):
                corner = world_to_camera_view(scene, camera, Vector(centres[side]) + Vector((dx, 0, dz)))
                check(0 <= corner.x <= 1 and 0 <= corner.y <= 1, f'Frame {frame}: {camera.name} crops screen corner')

scene.render.resolution_x = 1920
scene.frame_set(1)
report = {'scene': bpy.data.filepath, 'tag': tag, 'frames_checked': 720,
          'images': images, 'minimum_screen_centre_margin': minimum_margin,
          'failures': failures, 'passed': not failures,
          'limits': ['Does not validate product behavior, audio, DPI or real internet reachability.',
                     'Does not prove absence of arbitrary mesh intersections or native dialog appearance.',
                     'Caption/lighting legibility requires visual review of composed previews.']}
output = ROOT / f'logs/audit-{tag}.json'
output.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'report': str(output), 'passed': not failures, 'failures': failures[:12], 'count': len(failures)}))
if failures:
    raise RuntimeError(f'{len(failures)} scene audit failures; see {output}')

"""Encode already-composed 1080p PNGs with Blender's bundled H.264 encoder.
No additional titles, sound, product access, or external encoder installation.
blender --background --factory-startup --python-exit-code 1 --python scripts/encode_studios.py -- studios-v09
"""
import bpy
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
tag = args[0] if args else 'studios-v09'
if not tag.startswith('studios-v') or not tag[9:].isdigit():
    raise ValueError('Expected a studios-vNN version')
folder = ROOT / f'renders/frames/{tag}/edit'
files = [folder / f'frame_{frame:04d}.png' for frame in range(1, 721)]
for file in files:
    with file.open('rb') as source:
        header = source.read(24)
    if header[:8] != b'\x89PNG\r\n\x1a\n' or struct.unpack('>II', header[16:24]) != (1920, 1080):
        raise RuntimeError(f'Missing or invalid full-resolution frame: {file}')

output = ROOT / 'renders/film'
output.mkdir(parents=True, exist_ok=True)
cut = 1
while True:
    name = f'trackmesh-{tag}-review-cut{cut:02d}'
    movie = output / f'{name}.mp4'
    edit = ROOT / f'scenes/versions/{name}.blend'
    log = ROOT / f'logs/encode-{name}.json'
    if not any(p.exists() for p in (movie, edit, log)):
        break
    cut += 1

scene = bpy.context.scene
scene.frame_start, scene.frame_end = 1, 720
scene.render.fps, scene.render.fps_base = 24, 1
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1920, 1080, 100
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure, scene.view_settings.gamma = 0, 1
scene.render.use_sequencer = True
strips = scene.sequence_editor_create().strips
footage = strips.new_image('Composed final frames', str(files[0]), 1, 1, fit_method='FIT')
for file in files[1:]:
    footage.elements.append(file.name)
scene.render.image_settings.media_type = 'VIDEO'
scene.render.image_settings.file_format = 'FFMPEG'
ff = scene.render.ffmpeg
ff.format, ff.codec = 'MPEG4', 'H264'
ff.constant_rate_factor, ff.ffmpeg_preset = 'HIGH', 'GOOD'
ff.gopsize = 24
ff.audio_codec = 'NONE'
scene.render.filepath = str(movie)
scene['review_status'] = 'Motion review only; not approved for publication.'
scene['source_frames'] = str(folder)
bpy.ops.wm.save_as_mainfile(filepath=str(edit))
bpy.ops.render.render(animation=True)
if not movie.is_file() or not movie.stat().st_size:
    raise RuntimeError(f'Encoder did not produce {movie}')
metadata = {'movie': str(movie), 'edit_blend': str(edit), 'source_frames': str(folder),
            'frames': 720, 'fps': 24, 'duration_seconds': 30, 'resolution': [1920, 1080],
            'codec_requested': 'H264', 'audio_requested': 'NONE', 'bytes': movie.stat().st_size,
            'publication_approved': False, 'verification': 'Requires independent MP4 inspection and playback.'}
log.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
print('TRACKMESH_STUDIOS_MOVIE ' + json.dumps(metadata), flush=True)

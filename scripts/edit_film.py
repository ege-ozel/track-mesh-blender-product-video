"""Cut the rendered film frames with captions and encode an H.264 MP4 in Blender's sequencer.
blender --background --factory-startup --python scripts/edit_film.py -- film-v03
Captions live here, so their wording can change without re-rendering the 3D frames.
"""
import bpy, sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
tag = args[0] if args else 'film-v03'
# '--stills 60,150' renders those edited frames as PNG previews instead of encoding the movie.
stills = [int(f) for f in args[args.index('--stills') + 1].split(',')] if '--stills' in args else []
frames = ROOT / f'renders/frames/{tag}'
files = [frames / f'frame_{f:04d}.png' for f in range(1, 721)]
missing = [f for f in files if not f.exists()]
if missing and (not stills or any(not files[f - 1].exists() for f in stills)):
    raise RuntimeError(f'{len(missing)} frames missing in {frames}')
first = next(f for f in files if f.exists())
out_dir = ROOT / 'renders/film'; out_dir.mkdir(parents=True, exist_ok=True)
number = 1
while (out_dir / f'trackmesh-{tag}-cut{number:02d}.mp4').exists(): number += 1
movie = out_dir / f'trackmesh-{tag}-cut{number:02d}.mp4'

scene = bpy.context.scene
scene.frame_start, scene.frame_end = 1, 720
scene.render.fps, scene.render.fps_base = 24, 1
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1920, 1080, 100
# The frames are already display-referred; pass them through untouched.
scene.view_settings.view_transform = 'Standard'; scene.view_settings.look = 'None'
scene.view_settings.exposure = 0; scene.view_settings.gamma = 1
strips = scene.sequence_editor_create().strips

footage = strips.new_image('Film frames', str(first if not files[0].exists() else files[0]), 1, 1, fit_method='FIT')
for file in files[1:]: footage.elements.append(file.name if file.exists() else first.name)

regular = bpy.data.fonts.load('C:/Windows/Fonts/segoeui.ttf')
semibold = bpy.data.fonts.load('C:/Windows/Fonts/seguisb.ttf')
bold = bpy.data.fonts.load('C:/Windows/Fonts/segoeuib.ttf')
WHITE = (.96, .97, .97, 1); GREY = (.70, .76, .78, 1); TEAL = (.43, .85, .76, 1)

def fade(strip, start, end, length=10, peak=1.0):
    for frame, alpha in [(start, 0), (start + length, peak), (end - length, peak), (end, 0)]:
        strip.blend_alpha = alpha; strip.keyframe_insert('blend_alpha', frame=frame)

def text(name, body, start, end, channel, font, size, color, location, align='LEFT', anchor_y='BOTTOM', peak=1.0):
    strip = strips.new_effect(name, 'TEXT', channel, start, length=end - start)
    strip.text = body; strip.font = font; strip.font_size = size; strip.color = color
    strip.location = location; strip.alignment_x = align; strip.anchor_x = align; strip.anchor_y = anchor_y
    strip.use_shadow = True; strip.shadow_color = (0, 0, 0, .55); strip.shadow_blur = .4; strip.shadow_offset = .03
    strip.blend_type = 'ALPHA_OVER'
    fade(strip, start, end, peak=peak)
    return strip

# Lower-left captions, one pair per shot.
CAPTIONS = [
    (12, 90, 'Two studios. One project.', 'Meet TrackMesh.'),
    (104, 222, 'Save in your DAW.', 'The TrackMesh plugin shares the new version.'),
    (236, 330, 'Your collaborator sees it.', 'A direct, peer-to-peer link between your PCs.'),
    (344, 462, "Get it when you're ready.", 'Close the project in your DAW, then press Get.'),
    (476, 574, 'PC to PC.', 'No cloud copy of your project files.'),
]
for i, (start, end, title, subtitle) in enumerate(CAPTIONS):
    text(f'Caption {i + 1} title', title, start, end, 3, semibold, 64, WHITE, (.065, .155))
    text(f'Caption {i + 1} subtitle', subtitle, start + 4, end, 4, regular, 36, GREY, (.065, .1))

# Outro title over the wide pull-back, then a fade to black.
text('Outro name', 'TrackMesh', 596, 708, 3, bold, 120, WHITE, (.5, .2), align='CENTER')
text('Outro line', 'Share DAW projects, PC to PC.', 606, 708, 4, regular, 42, TEAL, (.5, .135), align='CENTER')
text('Concept label', 'Concept visualization', 1, 712, 5, regular, 26, GREY, (.955, .935), align='RIGHT', anchor_y='TOP', peak=.8)
black = strips.new_effect('Fade to black', 'COLOR', 6, 700, length=21)
black.color = (0, 0, 0); black.blend_type = 'ALPHA_OVER'
for frame, alpha in [(700, 0), (716, 1)]:
    black.blend_alpha = alpha; black.keyframe_insert('blend_alpha', frame=frame)

if stills:
    scene.render.image_settings.file_format = 'PNG'
    for frame in stills:
        scene.frame_set(frame); scene.render.filepath = str(ROOT / f'renders/previews/{tag}-edit-f{frame:04d}.png')
        bpy.ops.render.render(write_still=True)
    sys.exit(0)
scene.render.image_settings.media_type = 'VIDEO'
scene.render.image_settings.file_format = 'FFMPEG'
ff = scene.render.ffmpeg
ff.format = 'MPEG4'; ff.codec = 'H264'; ff.constant_rate_factor = 'HIGH'; ff.ffmpeg_preset = 'GOOD'
ff.gopsize = 24; ff.audio_codec = 'NONE'
scene.render.filepath = str(movie)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / f'scenes/versions/trackmesh-{tag}-edit-cut{number:02d}.blend'))
bpy.ops.render.render(animation=True)
print('TRACKMESH_FILM_MOVIE ' + json.dumps({'movie': str(movie), 'bytes': movie.stat().st_size, 'captions': CAPTIONS}))

"""Encode existing short-trial PNGs only; no scene rendering."""
import bpy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
tag=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'studios-v09-mobile-get-trial02'
assert tag.startswith('studios-v09-mobile-') and '/' not in tag and '\\' not in tag
folder=ROOT/'renders/previews'/tag
meta=json.loads((folder/'manifest.json').read_text())
movie=ROOT/'renders/film'/f'trackmesh-{tag}.mp4'
assert not movie.exists(),'Preserving existing output'
scene=bpy.context.scene
scene.frame_start,scene.frame_end=1,meta['frames']
scene.render.resolution_x,scene.render.resolution_y=meta['resolution']
scene.render.resolution_percentage=100
scene.render.fps,scene.render.fps_base=24,1
scene.view_settings.view_transform='Standard'
scene.view_settings.look='None'
scene.render.use_sequencer=True
strip=scene.sequence_editor_create().strips.new_image('Mobile Get editorial trial',str(folder/'frames/frame_0001.png'),1,1)
for n in range(2,meta['frames']+1):strip.elements.append(f'frame_{n:04d}.png')
scene.render.image_settings.media_type='VIDEO'
scene.render.image_settings.file_format='FFMPEG'
ff=scene.render.ffmpeg
ff.format,ff.codec,ff.audio_codec='MPEG4','H264','NONE'
ff.constant_rate_factor,ff.ffmpeg_preset,ff.gopsize='HIGH','GOOD',24
scene.render.filepath=str(movie)
bpy.ops.render.render(animation=True)
print(json.dumps({'movie':str(movie),'bytes':movie.stat().st_size,**meta},indent=2))

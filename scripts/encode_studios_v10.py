"""Encode an existing v10 frame sequence with the bundled H.264 encoder, silent."""
import bpy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
aspect=sys.argv[sys.argv.index('--')+1]
assert aspect in ('16x9','9x16')
suffix=sys.argv[sys.argv.index('--')+2:] 
assert suffix in ([],['polish01'])
folder=ROOT/'renders/frames'/(f'studios-v10-final-{aspect}'+('-polish01' if suffix else ''))
meta=json.loads((folder/'manifest.json').read_text())
movie=Path(meta['movie']);assert not movie.exists(),'Preserve existing final movie'
for n in range(1,meta['frames']+1):assert (folder/f'frames/frame_{n:04d}.png').is_file()
s=bpy.context.scene;s.frame_start=1;s.frame_end=meta['frames'];s.render.fps=24;s.render.fps_base=1
s.render.resolution_x,s.render.resolution_y=meta['resolution'];s.render.resolution_percentage=100
s.view_settings.view_transform='Standard';s.view_settings.look='None'
s.render.use_sequencer=True
strip=s.sequence_editor_create().strips.new_image('Final composed frames',str(folder/'frames/frame_0001.png'),1,1)
for n in range(2,meta['frames']+1):strip.elements.append(f'frame_{n:04d}.png')
s.render.image_settings.media_type='VIDEO';s.render.image_settings.file_format='FFMPEG'
ff=s.render.ffmpeg;ff.format='MPEG4';ff.codec='H264';ff.audio_codec='NONE'
ff.constant_rate_factor='HIGH';ff.ffmpeg_preset='GOOD';ff.gopsize=24;s.render.filepath=str(movie)
bpy.ops.render.render(animation=True)
print('V10_ENCODE_COMPLETE '+json.dumps({'movie':str(movie),'bytes':movie.stat().st_size,'frames':meta['frames']}))

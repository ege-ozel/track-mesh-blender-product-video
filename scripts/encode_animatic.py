"""Encode 72 rendered frames using existing Playwright VP8 FFmpeg + Pillow.
No package installation. WebM is the native preview; GIF is an inline fallback.
"""
import argparse,json,subprocess,sys,io
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--version',required=True)
parser.add_argument('--ffmpeg',default='C:/Users/4D/AppData/Local/ms-playwright/ffmpeg-1011/ffmpeg-win64.exe')
args=parser.parse_args();tag=args.version
frames=ROOT/f'renders/frames/animatic-{tag}'
paths=[frames/f'frame_{n:04d}.png' for n in range(1,73)]
for path in paths:
    if not path.exists():raise RuntimeError(f'Missing frame: {path}')
    with Image.open(path) as im:
        if im.size!=(960,540):raise RuntimeError(f'Unexpected frame dimensions: {path}')
video=ROOT/f'renders/previews/animatic-{tag}-3s.webm'
gif=ROOT/f'renders/previews/animatic-{tag}-3s.gif'
if video.exists() or gif.exists():raise RuntimeError('Preserving existing encoded preview. Choose a new version.')
command=[args.ffmpeg,'-hide_banner','-n','-f','image2pipe','-c:v','mjpeg','-framerate','24','-i','pipe:0',
  '-frames:v','72','-c:v','libvpx','-b:v','1800k','-crf','12','-pix_fmt','yuv420p','-an',str(video)]
# Playwright's small FFmpeg includes MJPEG image2pipe input, not PNG sequences.
# Convert only the in-memory encode feed; keep all original PNGs unchanged.
stream=io.BytesIO()
for path in paths:
    with Image.open(path) as im:im.convert('RGB').save(stream,format='JPEG',quality=97,subsampling=0)
run=subprocess.run(command,input=stream.getvalue(),capture_output=True)
diagnostics=(run.stdout+run.stderr).decode('utf-8',errors='replace')
(ROOT/f'logs/encode-{tag}.log').write_text(diagnostics,encoding='utf-8')
if run.returncode:raise RuntimeError(diagnostics)
# A 640px inline GIF of the same frames, using a stable global palette.
images=[]
for path in paths:
    with Image.open(path) as im:images.append(im.convert('RGB').resize((640,360),Image.Resampling.LANCZOS))
sheet=Image.new('RGB',(640,360*6))
for index,n in enumerate((0,12,24,35,47,63)):sheet.paste(images[n],(0,360*index))
palette=sheet.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
indexed=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in images]
# GIF duration has 10ms granularity: 5x40ms + 1x50ms per 6 frames = 250ms.
durations=[50 if (n+1)%6==0 else 40 for n in range(72)]
indexed[0].save(gif,save_all=True,append_images=indexed[1:],duration=durations,loop=0,disposal=2,optimize=False)
with Image.open(gif) as im:
    duration=0
    for frame in range(im.n_frames):im.seek(frame);duration+=im.info.get('duration',0)
    gif_frames=im.n_frames
metadata={'version':tag,'frames':72,'fps':24,'seconds':3,'dimensions':[960,540],
  'webm':str(video),'codec':'VP8','webm_bytes':video.stat().st_size,
  'gif':str(gif),'gif_dimensions':[640,360],'gif_input_frames':72,'gif_frames':gif_frames,'gif_duration_ms':duration,
  'ffmpeg_command':command,'encode_input':'MJPEG pipe, quality 97, original PNGs preserved','no_audio':True}
if gif_frames<2 or duration!=3000:raise RuntimeError(f'GIF timing mismatch: {metadata}')
(ROOT/f'logs/encoded-{tag}.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
print(json.dumps(metadata,indent=2))

"""Update only the Shared GIF moment and its adjacent dissolves; retain all other decoded pixels."""
import hashlib,io,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'renders/readme'
old=OUT/'trackmesh-flow-v06.gif';new=OUT/'trackmesh-flow-v07.gif';assert not new.exists()
frames=[];durations=[]
with Image.open(old) as gif:
 assert gif.size==(800,450) and gif.info.get('loop')==0
 for n in range(gif.n_frames):gif.seek(n);frames.append(gif.convert('RGB'));durations.append(gif.info['duration'])
assert len(frames)==31
reference=[f.copy() for f in frames]
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',n)
def disclosure(im):
 im=im.copy();d=ImageDraw.Draw(im);d.rectangle((0,414,800,450),fill='#070e15')
 d.text((400,427),'Concept visualization · Example data',font=font(14),fill='#d6e0e4',anchor='mt');return im
source=ROOT/'logs/trackmesh-studios-v10-final-16x9-polish01-decoded/frame_0198.png'
shared=disclosure(Image.open(source).convert('RGB').resize((800,450),Image.Resampling.LANCZOS))
frames[4]=shared
for i,a in enumerate((.25,.5,.75),1):frames[i]=disclosure(Image.blend(reference[0],shared,a))
for i,a in enumerate((.25,.5,.75),5):frames[i]=disclosure(Image.blend(shared,reference[8],a))
changed=set(range(1,8));quant=[]
for i,im in enumerate(frames):
 if i not in changed:
  assert im.getcolors(256) is not None
  q=im.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
 else:
  pal=im.quantize(colors=256,method=Image.Quantize.MEDIANCUT);clean=im.quantize(palette=pal,dither=Image.Dither.NONE)
  q=im.quantize(palette=pal,dither=Image.Dither.FLOYDSTEINBERG);q.paste(clean.crop((0,414,800,450)),(0,414))
  if i==4:q.paste(clean.crop((0,345,800,414)),(0,345))
 quant.append(q)
buf=io.BytesIO();quant[0].save(buf,format='GIF',save_all=True,append_images=quant[1:],duration=durations,loop=0,optimize=True,disposal=1)
assert len(buf.getvalue())<5_000_000
with new.open('xb') as f:f.write(buf.getvalue())
verified=[]
with Image.open(new) as gif:
 assert gif.n_frames==31 and gif.info.get('loop')==0
 for i in range(31):
  gif.seek(i);assert gif.info['duration']==durations[i]
  if i not in changed:
   assert ImageChops.difference(reference[i],gif.convert('RGB')).getbbox() is None
   verified.append(i)
 gif.seek(4);gif.convert('RGB').save(OUT/'trackmesh-flow-v07-shared.png')
report={'output':str(new),'bytes':new.stat().st_size,'sha256':hashlib.sha256(new.read_bytes()).hexdigest(),
 'previous':str(old),'previous_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'resolution':[800,450],
 'duration_seconds':sum(durations)/1000,'frames':31,'changed_frame_indices':sorted(changed),
 'unchanged_frame_indices_pixel_verified':verified,'scope':'Shared hold and the three-frame dissolves immediately before/after it only. All other decoded pixels and durations match v06.',
 'publication_approved':False}
(OUT/'trackmesh-flow-v07.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))

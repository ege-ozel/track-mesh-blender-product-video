"""Colour-only label patch; lossless YUV encode and exhaustive decoded-pixel audit."""
import sys,subprocess,json,hashlib,io
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/video-python'))
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe();OUT=ROOT/'renders/previews/label-polish02'
OUT.mkdir(exist_ok=True)
ORANGE=np.array([232,170,110.]);TEAL=np.array([110,217,194.])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fontmask(w,h):
 im=Image.new('L',(w,h));ImageDraw.Draw(im).text((60,65),'STUDIO A',font=ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',30),fill=255);return im

def yuv(c):return np.array([16+.182586*c[0]+.614231*c[1]+.062007*c[2],128-.100644*c[0]-.338572*c[1]+.439216*c[2],128+.439216*c[0]-.398942*c[1]-.040274*c[2]])
def reader(p,pix='yuv420p'):
 return subprocess.Popen([FF,'-v','error','-threads','1','-i',str(p),'-f','rawvideo','-pix_fmt',pix,'-'],stdout=subprocess.PIPE)
def readexact(pipe,n):
 data=bytearray()
 while len(data)<n:
  b=pipe.read(n-len(data))
  if not b:break
  data.extend(b)
 return data

def video(aspect):
 w,h=(1920,1080) if aspect=='16x9' else (1080,1920)
 src=ROOT/f'renders/film/trackmesh-studios-v10-final-{aspect}-polish01.mp4';dst=src.with_name(src.name.replace('polish01','polish02'));assert not dst.exists()
 meta=json.loads((ROOT/f'renders/frames/studios-v10-final-{aspect}-polish01/manifest.json').read_text());total=meta['frames'];last=96 if aspect=='16x9' else 30
 protected=sha(src);nbytes=w*h*3//2
 alpha=np.asarray(fontmask(w,h),dtype=float)/255
 # Preserve the existing antialias coverage, placement and shape, shifting only colour.
 delta=yuv(ORANGE)-yuv(TEAL)
 a2=alpha.reshape(h//2,2,w//2,2).mean(axis=(1,3))
 dec=reader(src)
 enc=subprocess.Popen([FF,'-v','error','-n','-f','rawvideo','-pix_fmt','yuv420p','-s',f'{w}x{h}','-r','24','-color_range','tv','-colorspace','bt709','-i','-','-an','-c:v','libx264','-qp','0','-preset','medium','-g','24','-color_range','tv','-colorspace','bt709','-movflags','+faststart',str(dst)],stdin=subprocess.PIPE)
 for n in range(1,total+1):
  raw=readexact(dec.stdout,nbytes);assert len(raw)==nbytes
  if n<=last:
   arr=np.frombuffer(raw,dtype=np.uint8).copy();offset=0
   for size,shape,am,dv in [(w*h,(h,w),alpha,delta[0]),(w*h//4,(h//2,w//2),a2,delta[1]),(w*h//4,(h//2,w//2),a2,delta[2])]:
    plane=arr[offset:offset+size].reshape(shape);np.copyto(plane,np.clip(np.rint(plane.astype(float)+am*dv),0,255).astype('uint8'));offset+=size
   raw=arr.tobytes()
  enc.stdin.write(raw)
 enc.stdin.close();assert enc.wait()==0 and dec.wait()==0
 # Compare every output frame to the actual specified MP4, with the same RGB decoder.
 before=reader(src,'rgb24');after=reader(dst,'rgb24');changed=[];outside=0;union=None
 roi=(45,50,271,121)
 for n in range(1,total+1):
  aa=np.frombuffer(readexact(before.stdout,w*h*3),dtype=np.uint8).reshape(h,w,3);bb=np.frombuffer(readexact(after.stdout,w*h*3),dtype=np.uint8).reshape(h,w,3)
  diff=np.any(aa!=bb,axis=2);ys,xs=np.where(diff)
  if len(xs):
   bounds=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)];changed.append({'frame':n,'pixels':int(diff.sum()),'bbox':bounds})
   union=bounds if union is None else [min(union[0],bounds[0]),min(union[1],bounds[1]),max(union[2],bounds[2]),max(union[3],bounds[3])]
   diff[roi[1]:roi[3],roi[0]:roi[2]]=False;outside+=int(diff.sum())
  if n in ([48,264,582] if aspect=='16x9' else [15,140,408]):
   Image.fromarray(bb).save(OUT/f'after-{aspect}-{n}.png')
  if n%120==0:print(f'VERIFY {aspect} {n}/{total}',flush=True)
 assert before.wait()==0 and after.wait()==0 and outside==0 and len(changed)==last
 assert sha(src)==protected
 report={'source':str(src),'source_sha256':protected,'output':str(dst),'sha256':sha(dst),'bytes':dst.stat().st_size,'resolution':[w,h],'frames':total,'fps':24,'duration_seconds':total/24,'audio':False,'encoder':'H.264 lossless, original YUV420 samples preserved except label glyph colour','changed_frames':changed,'changed_bounds_union':union,'allowed_chip_region':roi,'changed_pixels_outside_chip':outside,'entirely_pixel_identical_frames':total-last,'all_frames_compared':True,'note':'Studio B already matches teal, and PC to PC Studio A already matches orange; those pixels are preserved.'}
 (ROOT/f'logs/label-polish02-{aspect}.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='changed_frames'}),flush=True)

def gif():
 src=ROOT/'renders/readme/trackmesh-flow-v07.gif';dst=src.with_name('trackmesh-flow-v08.gif');assert not dst.exists();protected=sha(src)
 frames=[];times=[]
 with Image.open(src) as g:
  loop=g.info['loop']
  for i in range(g.n_frames):g.seek(i);frames.append(g.convert('RGB'));times.append(g.info['duration'])
 # Only the opening A chip participates in these holds / dissolves. Every other chip already has the specified colour.
 fades={0:1,1:.75,2:.5,3:.25,28:.25,29:.5,30:.75}
 mask=fontmask(1920,1080).resize((800,450),Image.Resampling.LANCZOS)
 alpha=np.asarray(mask,dtype=float)/255
 # Original GIF text is desaturated by its existing palette; estimate its core from the opening hold.
 first=np.asarray(frames[0]);core=np.median(first[alpha>.9],axis=0)
 updated=[];records=[];roi=(18,20,114,51)
 for i,im in enumerate(frames):
  arr=np.asarray(im);target=arr.copy();weight=fades.get(i,0)
  if weight:
   target=np.clip(np.rint(arr.astype(float)+alpha[:,:,None]*weight*(ORANGE-core)),0,255).astype('uint8')
  # Preserve every exterior RGB exactly, including original dithering and Shared band.
  # Reserve its exact colours first, then use free palette slots for the recoloured glyph.
  x0,y0,x1,y1=roi
  outside=np.ones((450,800),dtype=bool);outside[y0:y1,x0:x1]=False
  colors,inverse=np.unique(arr[outside if weight else np.ones_like(outside)].reshape(-1,3),axis=0,return_inverse=True)
  assert len(colors)<=256
  desired=Image.fromarray(target[y0:y1,x0:x1])
  slots=256-len(colors)
  extra=[]
  if slots:
   sample=desired.quantize(colors=slots,method=Image.Quantize.MEDIANCUT).convert('RGB');extra=np.unique(np.asarray(sample).reshape(-1,3),axis=0).tolist()
  palette=np.vstack([colors,np.array(extra,dtype=np.uint8).reshape(-1,3)]) if extra else colors
  pal=Image.new('P',(1,1));plist=palette.flatten().tolist();pal.putpalette(plist+[0]*(768-len(plist)))
  # Exact mapping outside: no dither. Region is independently quantized to this palette.
  if weight:
   indexes=np.zeros((450,800),dtype=np.uint8);indexes[outside]=inverse
   pixels=np.asarray(desired).astype(float).reshape(-1,3)
   distances=((pixels[:,None,:]-palette.astype(float)[None,:,:])**2).sum(axis=2)
   indexes[y0:y1,x0:x1]=distances.argmin(axis=1).reshape(y1-y0,x1-x0)
  else:indexes=inverse.reshape(450,800).astype('uint8')
  q=Image.fromarray(indexes,'P');q.putpalette(plist+[0]*(768-len(plist)))
  assert np.array_equal(np.asarray(q.convert('RGB'))[outside],arr[outside])
  updated.append(q)
 buf=io.BytesIO();updated[0].save(buf,format='GIF',save_all=True,append_images=updated[1:],duration=times,loop=loop,optimize=False,disposal=1)
 assert len(buf.getvalue())<5_000_000
 with dst.open('xb') as f:f.write(buf.getvalue())
 with Image.open(dst) as g:
  assert g.n_frames==len(frames) and g.info['loop']==loop
  for i,old in enumerate(frames):
   g.seek(i);assert times[i]==g.info['duration'];a=np.asarray(old);b=np.asarray(g.convert('RGB'));diff=np.any(a!=b,axis=2);ys,xs=np.where(diff)
   bounds=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None
   if len(xs):assert i in fades
   diff[y0:y1,x0:x1]=False;assert not diff.any()
   records.append({'frame':i,'changed_pixels':int(np.any(a!=b,axis=2).sum()),'bbox':bounds,'duration_ms':times[i]})
   if i in [0,4,8,20]:g.convert('RGB').save(OUT/f'gif-v08-{i:02d}.png')
 assert sha(src)==protected
 report={'source':str(src),'source_sha256':protected,'output':str(dst),'sha256':sha(dst),'bytes':dst.stat().st_size,'frames':len(frames),'duration_seconds':sum(times)/1000,'resolution':[800,450],'allowed_chip_region':roi,'changed_pixels_outside_chip':0,'shared_hold_and_band_exactly_preserved':records[4]['changed_pixels']==0,'frames_audit':records,'palette':'Exterior colours reserved exactly; available local palette entries used for orange glyphs. Existing palette used in full 256-colour dissolves.'}
 (ROOT/'logs/label-polish02-gif.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='gif':gif()
 else:video(sys.argv[1])

"""Motion-normalized consecutive UI crops; diagnostics only, no product writes."""
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'renders/previews/studios-v09-flicker-diagnostic01'
out.mkdir(exist_ok=False)
data=json.loads((ROOT/'logs/studios-v09-temporal-geometry.json').read_text())
report={}
for name,frames in [('share',range(140,152)),('desktop',range(300,312))]:
    obj='Studio A plugin / saved' if name=='share' else 'Studio B app / new'
    rects=[]
    for f in frames:
        pts=data['frames'][str(f)][obj]
        quad=tuple(v for i in [3,0,1,2] for v in pts[i])
        im=Image.open(ROOT/f'renders/frames/studios-v09/frame_{f:04d}.png').convert('RGB')
        im=im.transform((580,384) if name=='share' else (960,540),Image.Transform.QUAD,quad,Image.Resampling.BICUBIC)
        im.save(out/f'{name}-{f:04d}.png')
        rects.append(np.asarray(im).astype(float))
    delta=[float(np.abs(b-a).mean()) for a,b in zip(rects,rects[1:])]
    report[name]={'frames':[min(frames),max(frames)],'mean_absolute_adjacent_pixel_deltas_0_255':delta,
      'interpretation':'Nonzero changes remain after quadrilateral alignment in a fixed source state. Camera sampling, lighting and interpolation contribute; this is not a product UI flicker measurement.'}
    sheet=Image.new('RGB',(1160,4*(384+34)),(11,18,27));d=ImageDraw.Draw(sheet)
    for i,f in enumerate(list(frames)[:8]):
        im=Image.open(out/f'{name}-{f:04d}.png');im.thumbnail((580,384))
        x=(i%2)*580;y=(i//2)*418
        d.text((x+10,y+8),f'Original raw render · frame {f}',font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20),fill='white')
        sheet.paste(im,(x,y+34))
    sheet.save(out/f'{name}-consecutive.png')
report['geometry_finding']='DAW screen y=0.201000005; plugin border front y=0.200999990: effectively coplanar. Depth competition is a plausible border shimmer source, not independently isolated by a rerender.'
(out/'analysis.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))

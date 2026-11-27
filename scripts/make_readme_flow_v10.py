"""README GIF from decoded frames of the horizontal v10 final, preserving older GIFs."""
import hashlib,io,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'renders/readme'
TARGET=OUT/'trackmesh-flow-v06.gif'
assert not TARGET.exists(),'Preserve existing output'
SOURCE=ROOT/'logs/trackmesh-studios-v10-final-16x9-decoded'
font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/'+('seguisb.ttf' if b else 'segoeui.ttf'),n)
shots=[(48,1500,'Studio A'),(198,1800,'Shared'),(264,1500,'Studio B'),(390,2300,'Get confirmation'),
       (510,2600,'Got version / Example 44 MB'),(582,1800,'PC to PC'),(672,1600,'Closing card')]
def disclosure(im):
    im=im.copy();d=ImageDraw.Draw(im)
    d.rectangle((0,414,800,450),fill='#070e15')
    d.text((400,427),'Concept visualization · Example data',font=font(14),fill='#d6e0e4',anchor='mt')
    return im
panels=[Image.open(SOURCE/f'frame_{n:04d}.png').convert('RGB').resize((800,450),Image.Resampling.LANCZOS) for n,_,_ in shots]
images=[];durations=[];holds=[];timeline=[];elapsed=0
for i,(n,hold,story) in enumerate(shots):
    holds.append(len(images));images.append(disclosure(panels[i]));durations.append(hold)
    transition=300 if i<6 else 600
    timeline.append({'final_film_frame':n,'source_time_seconds':(n-1)/24,'hold_ms':hold,'story':story,'gif_start_ms':elapsed,'transition_ms':transition});elapsed+=hold
    if i<6:transition_images=[Image.blend(panels[i],panels[i+1],a) for a in (.25,.5,.75)]
    else:
        black=Image.new('RGB',(800,450),'black')
        transition_images=[Image.blend(panels[i],black,a) for a in (1/3,2/3,1)]+[Image.blend(black,panels[0],a) for a in (.25,.5,.75)]
    for im in transition_images:images.append(disclosure(im));durations.append(100);elapsed+=100
for colors in (256,240,224,208,192):
    quant=[]
    for i,im in enumerate(images):
        pal=im.quantize(colors=colors,method=Image.Quantize.MEDIANCUT)
        clean=im.quantize(palette=pal,dither=Image.Dither.NONE)
        q=im.quantize(palette=pal,dither=Image.Dither.FLOYDSTEINBERG)
        q.paste(clean.crop((0,414,800,450)),(0,414))
        if i in holds:q.paste(clean.crop((0,345,800,414)),(0,345))
        if i==holds[-1]:q=clean
        quant.append(q)
    data=io.BytesIO();quant[0].save(data,format='GIF',save_all=True,append_images=quant[1:],duration=durations,loop=0,optimize=True,disposal=1)
    payload=data.getvalue()
    if len(payload)<5_000_000:break
assert len(payload)<5_000_000
with TARGET.open('xb') as f:f.write(payload)
decoded=[];actual=[]
with Image.open(TARGET) as gif:
    assert gif.size==(800,450) and gif.info.get('loop')==0
    for n in range(gif.n_frames):gif.seek(n);decoded.append(gif.convert('RGB'));actual.append(gif.info['duration'])
assert actual==durations and len(decoded)==31
sheet=Image.new('RGB',(1600,1960),'#0b121b');d=ImageDraw.Draw(sheet)
for i,(n,hold,story) in enumerate(shots):
    x=i%2*800;y=i//2*490;sheet.paste(decoded[holds[i]],(x,y));d.text((x+15,y+460),f'{n} / {hold/1000:.1f}s / {story}',font=font(17),fill='white')
sheet.save(OUT/'trackmesh-flow-v06-storyboard.png')
report={'movie':str(ROOT/'renders/film/trackmesh-studios-v10-final-16x9.mp4'),'output':str(TARGET),'bytes':len(payload),'resolution':[800,450],'duration_seconds':sum(actual)/1000,'frames':len(decoded),'holds':7,'colors':colors,'timeline':timeline,'requested_name_collision':'trackmesh-flow-v04.gif exists and was preserved; next unused version v06 selected.','palette_policy':'Per-frame palette and dithering reduce banding where practical; clean lettering prioritized. GIF color limits remain.','publication_approved':False}
(OUT/'trackmesh-flow-v06.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))

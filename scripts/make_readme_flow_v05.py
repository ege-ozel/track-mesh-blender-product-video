"""Seven editorial moments from existing v09 frames; no new 3D render or product writes."""
import hashlib, io, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'renders/readme'; OUT.mkdir(exist_ok=True)
TARGET=OUT/'trackmesh-flow-v05.gif'
assert not any((OUT/f'trackmesh-flow-v05{s}').exists() for s in ('.gif','.json','-storyboard.png')), 'Preserve existing v05 artifacts'
protected=list(OUT.glob('*.gif'))+[Path('D:/CodeSpace/track-mesh/docs/media/trackmesh-flow.gif')]
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
RAW=ROOT/'renders/frames/studios-v09'
EDIT=RAW/'edit'
font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/'+('seguisb.ttf' if b else 'segoeui.ttf'),n)
WHITE,GREY,TEAL='#f5f7f7','#b2c2c7','#6ed9c2'
shots=[(60,1500,'Studio A'),(208,1800,'Saved and shared'),(300,1500,'Studio B sees it'),
       (368,2300,'Get confirmation'),(430,2600,'Transfer detail'),(528,1800,'PC to PC'),(688,1600,'Closing card')]

def resized(p):return Image.open(p).convert('RGB').resize((800,450),Image.Resampling.LANCZOS)
def caption(im,title,subtitle):
    # A single two-line caption block on a gentle dark gradient.
    layer=Image.new('RGBA',(800,450));d=ImageDraw.Draw(layer)
    for y in range(315,450):
        a=round(215*min(1,(y-315)/35));d.line((0,y,800,y),fill=(5,10,16,a))
    d.text((28,350),title,font=font(27,True),fill=WHITE)
    d.text((28,389),subtitle,font=font(19),fill=GREY)
    return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')

panels=[]
for frame,hold,story in shots:
    if frame in (60,300):
        im=resized(EDIT/f'frame_{frame:04d}.png')
    elif frame==208:
        original=Image.open(RAW/'frame_0208.png').convert('RGB')
        im=original.resize((800,450),Image.Resampling.LANCZOS)
        # Existing source pixels: enlarge the completed-share status, not retype it.
        detail=original.crop((525,680,1235,742)).resize((740,65),Image.Resampling.LANCZOS)
        im.paste(detail,(30,262))
        im=caption(im,'Save in your DAW.','One click shares the new version.')
    elif frame==368:
        im=resized(EDIT/'frame_0368.png');d=ImageDraw.Draw(im)
        d.rectangle((8,8,340,34),fill='#0b121b')
        d.text((17,11),'Reconstructed confirmation · Example data',font=font(14),fill=GREY)
    elif frame==430:
        original=Image.open(RAW/'frame_0430.png').convert('RGB')
        im=ImageEnhance.Brightness(original.resize((800,450),Image.Resampling.LANCZOS)).enhance(.25)
        d=ImageDraw.Draw(im);d.rounded_rectangle((20,90,780,286),radius=10,fill='#111e2b',outline='#304452',width=2)
        # Magnified crops from this frame: status, percentage, complete progress bar,
        # and Stop. Preserve the actual source values and bar length.
        left=original.crop((445,575,760,605)).resize((470,45),Image.Resampling.LANCZOS)
        right=original.crop((1530,575,1720,605)).resize((218,35),Image.Resampling.LANCZOS)
        bar=original.crop((438,603,1730,627)).resize((730,28),Image.Resampling.LANCZOS)
        stop=original.crop((438,619,530,684)).resize((112,79),Image.Resampling.LANCZOS)
        im.paste(left,(35,115));im.paste(right,(545,122));im.paste(bar,(35,164));im.paste(stop,(35,196))
        im=caption(im,'Only the changed parts travel.','Example: 44 MB new in a 1.6 GB project.')
    elif frame==528:
        im=resized(EDIT/'frame_0528.png') # Only its original PC-to-PC caption.
    else:
        im=ImageEnhance.Brightness(resized(EDIT/'frame_0688.png').filter(ImageFilter.GaussianBlur(22))).enhance(.12)
        d=ImageDraw.Draw(im)
        d.text((400,139),'TrackMesh',font=font(65,True),fill=WHITE,anchor='mt')
        d.text((400,236),'Share DAW projects, PC to PC.',font=font(28),fill=TEAL,anchor='mt')
        d.text((400,292),'For Windows',font=font(20),fill=GREY,anchor='mt')
    panels.append(im)

def disclosure(im):
    im=im.copy();d=ImageDraw.Draw(im);f=font(15);label='Concept visualization'
    width=d.textlength(label,font=f)
    d.rectangle((800-width-22,418,800,450),fill='#070e15')
    d.text((788,426),label,font=f,fill='#d6e0e4',anchor='rt')
    return im

images=[];durations=[];timeline=[];elapsed=0;holds=[]
for i,(frame,hold,story) in enumerate(shots):
    holds.append(len(images));images.append(disclosure(panels[i]));durations.append(hold)
    transition=300 if i<6 else 600
    timeline.append({'film_frame':frame,'source_time_seconds':(frame-1)/24,'hold_ms':hold,
                     'gif_start_ms':elapsed,'transition_after_ms':transition,'story':story,
                     'gif_frame_index':holds[-1]})
    elapsed+=hold
    if i<6:
        transitions=[Image.blend(panels[i],panels[i+1],a) for a in (.25,.5,.75)]
    else:
        black=Image.new('RGB',(800,450),'black')
        transitions=[Image.blend(panels[i],black,a) for a in (1/3,2/3,1)]
        transitions += [Image.blend(black,panels[0],a) for a in (.25,.5,.75)]
    for im in transitions:images.append(disclosure(im));durations.append(100);elapsed+=100

# Quantize in memory; never overwrite an earlier artifact when optimizing size.
for colors in (256,240,224,208):
    quant=[]
    for i,im in enumerate(images):
        pal=im.quantize(colors=colors,method=Image.Quantize.MEDIANCUT)
        clean=im.quantize(palette=pal,dither=Image.Dither.NONE)
        q=im.quantize(palette=pal,dither=Image.Dither.FLOYDSTEINBERG)
        q.paste(clean.crop((590,418,800,450)),(590,418))
        # Keep editorial text and the closing card clean, dither room gradients.
        if i in holds:
            q.paste(clean.crop((0,340,800,418)),(0,340))
        if i==holds[4]:q.paste(clean.crop((20,90,780,286)),(20,90))
        if i==holds[-1]:q=clean
        quant.append(q)
    encoded=io.BytesIO()
    quant[0].save(encoded,format='GIF',save_all=True,append_images=quant[1:],duration=durations,loop=0,optimize=True,disposal=1)
    payload=encoded.getvalue()
    if len(payload)<5_000_000:break
assert len(payload)<5_000_000, 'GIF exceeds size limit'
assert 13000<=sum(durations)<=16000
with TARGET.open('xb') as f:f.write(payload)
decoded=[];actual=[]
with Image.open(TARGET) as gif:
    assert gif.size==(800,450) and gif.info.get('loop')==0
    for n in range(gif.n_frames):
        gif.seek(n);decoded.append(gif.convert('RGB'));actual.append(gif.info['duration'])
assert len(decoded)==len(images) and actual==durations
assert len(decoded)==31
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items())
sheet=Image.new('RGB',(1600,4*490),'#0b121b');d=ImageDraw.Draw(sheet)
for i,(frame,hold,story) in enumerate(shots):
    x=(i%2)*800;y=(i//2)*490
    sheet.paste(decoded[holds[i]],(x,y))
    d.text((x+12,y+458),f'{frame} / {hold/1000:.1f}s / {story}',font=font(18),fill=WHITE)
sheet.save(OUT/'trackmesh-flow-v05-storyboard.png')
# Export actual decoded detail and loop frames for review.
for name,index in [('share',holds[1]),('transfer',holds[4]),('loop-black',holds[-1]+3)]:
    decoded[index].save(OUT/f'trackmesh-flow-v05-{name}.png')
report={'output':str(TARGET),'bytes':len(payload),'size':[800,450],'duration_ms':sum(actual),
        'encoded_frames':len(decoded),'story_moments':len(shots),'colors':colors,'loop':0,'timeline':timeline,
        'transition':'Six 3-frame crossfades (300 ms); closing-to-black 3 frames then black-to-opening 3 frames (600 ms)',
        'caption_policy':'One editorial caption block per hold; UI statuses and Concept visualization retained',
        'transfer_detail':'Existing frame 430; expanded progress and Stop crops preserve both bar endcaps and full button border with surrounding padding; transfer detail quantized without dithering; values unchanged',
        'share_detail':'Existing frame 208 completed-share status pixels magnified',
        'new_claims':False,'new_3d_render':False,'product_repo_modified':False,'publication_approved':False,
        'protected_sha256':hashes,'checks':'All 31 frames decoded; dimensions, exact durations, loop, file size and protected hashes passed. Visual review pending.'}
(OUT/'trackmesh-flow-v05.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))

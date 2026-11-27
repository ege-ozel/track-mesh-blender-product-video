"""Make a new README GIF from existing v09 composed stills; never modify the product repo."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'renders/readme'
OUT.mkdir(exist_ok=True)
version = 1
while any((OUT / f'trackmesh-flow-v{version:02d}{suffix}').exists()
          for suffix in ('.gif', '.json', '-storyboard.png')):
    version += 1
stem = f'trackmesh-flow-v{version:02d}'
movie = OUT / f'{stem}.gif'
source = ROOT / 'renders/frames/studios-v09/edit'
W,H = 800,450
font = lambda size, bold=False: ImageFont.truetype('C:/Windows/Fonts/' + ('seguisb.ttf' if bold else 'segoeui.ttf'), size)
WHITE, GREY, TEAL = '#f5f7f7', '#b2c2c7', '#6ed9c2'
shots = [
    (60,1300,'Studio A','A wide'),
    (176,1800,'Save in your DAW / One click shares the new version','A close; one moment only'),
    (300,1300,'Your collaborator sees it','B wide'),
    (368,2300,'Get confirmation','B close; reconstructed native confirmation'),
    (528,2600,'Changed parts arrive / PC to PC','Split screen; both story beats share one moment'),
    (688,1600,'Closing card','Standalone graphic card using the existing closing frame and wording'),
]
panels=[]
for frame,hold,beat,view in shots:
    im=Image.open(source / f'frame_{frame:04d}.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
    if frame==368:
        # Clarify the reconstruction; do not pass it off as a native Windows recording.
        d=ImageDraw.Draw(im)
        d.rectangle((8,8,340,34),fill='#0b121b')
        d.text((17,11),'Reconstructed confirmation · Example data',font=font(14),fill=GREY)
    elif frame==528:
        # Preserve the approved example wording while retaining PC-to-PC below.
        layer=Image.new('RGBA',im.size)
        d=ImageDraw.Draw(layer)
        d.rectangle((0,0,W,101),fill=(6,12,18,237))
        d.text((28,12),'Only the changed parts travel.',font=font(27,True),fill=WHITE)
        d.text((28,55),'Example: 44 MB new in a 1.6 GB project.',font=font(20),fill=GREY)
        im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
    elif frame==688:
        # An explicit end card, rather than another still from the same split cameras.
        im=ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(22))).enhance(.16)
        d=ImageDraw.Draw(im)
        d.text((400,139),'TrackMesh',font=font(65,True),fill=WHITE,anchor='mt')
        d.text((400,236),'Share DAW projects, PC to PC.',font=font(28),fill=TEAL,anchor='mt')
        d.text((400,292),'For Windows',font=font(20),fill=GREY,anchor='mt')
    panels.append(im)

def disclosure(im):
    im=im.copy();d=ImageDraw.Draw(im)
    label='Concept visualization';f=font(15)
    width=d.textlength(label,font=f)
    d.rectangle((W-width-22,418,W,450),fill='#070e15')
    d.text((W-12,426),label,font=f,fill='#d6e0e4',anchor='rt')
    return im

images=[];durations=[];timeline=[];elapsed=0
for i,(frame,hold,beat,view) in enumerate(shots):
    images.append(disclosure(panels[i]));durations.append(hold)
    timeline.append({'source_frame':frame,'source_time_seconds':(frame-1)/24,
                     'hold_ms':hold,'transition_after_ms':300,'gif_start_ms':elapsed,
                     'story':beat,'view':view})
    elapsed+=hold
    for weight in (.25,.5,.75):
        images.append(disclosure(Image.blend(panels[i],panels[(i+1)%len(panels)],weight)))
        durations.append(100);elapsed+=100

# Per-frame palettes retain warm/cool gradients better than one palette shared
# across both rooms. Dithering is retained in imagery, disabled over disclosures
# and the standalone end card so the small lettering stays clean.
quantized=[]
for i,im in enumerate(images):
    palette=im.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
    clean=im.quantize(palette=palette,dither=Image.Dither.NONE)
    q=im.quantize(palette=palette,dither=Image.Dither.FLOYDSTEINBERG)
    q.paste(clean.crop((590,418,800,450)),(590,418))
    if i==20:q=clean
    quantized.append(q)
quantized[0].save(movie,save_all=True,append_images=quantized[1:],duration=durations,
                  loop=0,optimize=True,disposal=1)

with Image.open(movie) as gif:
    assert gif.size==(800,450) and gif.info.get('loop')==0
    decoded=[];actual=[]
    for i in range(gif.n_frames):
        gif.seek(i);decoded.append(gif.convert('RGB'));actual.append(gif.info['duration'])
assert len(decoded)==len(images) and actual==durations
assert movie.stat().st_size<5_000_000
sheet=Image.new('RGB',(1600,3*490),'#0b121b');d=ImageDraw.Draw(sheet)
for i,(frame,hold,beat,view) in enumerate(shots):
    x=(i%2)*800;y=(i//2)*490
    sheet.paste(decoded[i*4],(x,y))
    d.text((x+12,y+458),f'{frame} / {hold/1000:.1f}s / {beat}',font=font(16),fill=WHITE)
sheet.save(OUT/f'{stem}-storyboard.png')
old=Path('D:/CodeSpace/track-mesh/docs/media/trackmesh-flow.gif')
report={'output':str(movie),'bytes':movie.stat().st_size,'size':[W,H],
        'duration_ms':sum(actual),'encoded_frames':len(decoded),'loop':0,
        'transition':'300 ms crossfade after every hold, including end-to-start',
        'timeline':timeline,'source':'Existing studios-v09 composed PNG frames, matching review-cut01 edit',
        'omitted_frame':208,'omission_reason':'Same A-close shot as 176; no repeated moment from that shot',
        'combined_beats':'Changed-parts example and PC-to-PC share one split-screen moment; no repeated B-close or split-camera jump cut',
        'new_3d_render':False,'product_repo_modified':False,'publication_approved':False,
        'product_gif_readonly_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),
        'checks':'Decoded every GIF frame; validated size, dimensions, loop and all frame durations. Visual storyboard review required.'}
(OUT/f'{stem}.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))

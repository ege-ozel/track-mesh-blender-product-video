"""Short companion to the Get trial: static native VST3 captures avoid 3D screen sampling."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'renders/previews/studios-v09-mobile-share-trial01'
OUT.mkdir(exist_ok=False);(OUT/'frames').mkdir()
font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/'+('seguisb.ttf' if b else 'segoeui.ttf'),n)
for n in range(1,133):
    original=n+96
    state='idle' if original<128 else 'saved' if original<166 else 'sharing' if original<190 else 'shared'
    im=Image.new('RGB',(1080,1920),'#0b121b');d=ImageDraw.Draw(im)
    d.text((60,100),'Save in your DAW.',font=font(60,True),fill='#f5f7f7')
    d.text((60,190),'VST3 host capture · Synthetic state',font=font(34),fill='#6ed9c2')
    src=Image.open(ROOT/f'assets/screens/v5/vst3-{state}.png').convert('RGB')
    if n<=18:
        daw=Image.open(ROOT/'assets/screens/daw.png').convert('RGB');daw.thumbnail((960,950))
        im.paste(daw,((1080-daw.width)//2,430))
        small=src.resize((580,384),Image.Resampling.LANCZOS);im.paste(small,(250,600))
        d.text((60,1430),'DAW backdrop: concept',font=font(32),fill='#b2c2c7')
    else:
        src=src.resize((960,636),Image.Resampling.LANCZOS);im.paste(src,(60,500))
        if 150<=original<=165:
            x,y=308,844
            if original>=163:d.ellipse((x-42,y-42,x+42,y+42),outline='#6ed9c2',width=6)
            d.polygon([(x,y),(x,y+42),(x+11,y+32),(x+22,y+51),(x+31,y+46),(x+20,y+28),(x+37,y+28)],fill='white',outline='#17202b',width=3)
    d.text((60,1280),'One click shares the new version.',font=font(46),fill='#f5f7f7')
    d.text((60,1510),'Timing edited · Not a speed test',font=font(30),fill='#b2c2c7')
    d.text((60,1790),'Concept visualization',font=font(36),fill='#b2c2c7')
    d.text((60,1845),'Example data · Editorial trial',font=font(29),fill='#b2c2c7')
    im.save(OUT/f'frames/frame_{n:04d}.png',compress_level=1)
meta={'frames':132,'fps':24,'duration_seconds':5.5,'resolution':[1080,1920],
 'source_frame_range':[97,228],'source_interval_seconds':[4,9.5],
 'source':'Existing v5 native VST3 SDK-host captures with synthetic status; conceptual DAW backdrop',
 'audio':False,'new_3d_render':False,'full_movie_modified':False,'publication_approved':False,
 'limitation':'580x384 native source enlarged to 960x636. Static UI avoids temporal sampling, but cannot restore finer detail or prove operation inside a DAW.'}
(OUT/'manifest.json').write_text(json.dumps(meta,indent=2))
print(OUT)

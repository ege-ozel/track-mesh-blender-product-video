"""A short editorial trial using existing v09 frames and labelled synthetic UI inserts."""
import argparse, hashlib, json, shutil, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('stage', choices=['prepare', 'compose'])
parser.add_argument('--trial', default='studios-v09-mobile-get-trial02')
args = parser.parse_args()
assert args.trial.startswith('studios-v09-mobile-get-trial') and args.trial.removeprefix('studios-v09-mobile-get-trial').isdigit()
OUT = ROOT / 'renders/previews' / args.trial
W, H = 1080, 1920
BG, WHITE, GREY, TEAL = '#0b121b', '#f5f7f7', '#b2c2c7', '#6ed9c2'
def face(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/' + ('seguisb.ttf' if bold else 'segoeui.ttf'), size)
def base(title, subtitle=''):
    im = Image.new('RGB', (W,H), BG)
    d = ImageDraw.Draw(im)
    d.text((60,100), title, font=face(55,True), fill=WHITE)
    if subtitle: d.text((60,185), subtitle, font=face(32), fill=TEAL)
    d.text((60,1790), 'Concept visualization', font=face(36), fill=GREY)
    d.text((60,1845), 'Example data · Editorial trial', font=face(29), fill=GREY)
    return im
def paste_fit(im, source, box):
    scale = min((box[2]-box[0])/source.width,(box[3]-box[1])/source.height)
    source = source.resize((round(source.width*scale),round(source.height*scale)),Image.Resampling.LANCZOS)
    im.paste(source, (box[0]+(box[2]-box[0]-source.width)//2,box[1]+(box[3]-box[1]-source.height)//2))
def cursor(im, x, y, pressed=False):
    d = ImageDraw.Draw(im)
    if pressed: d.ellipse((x-42,y-42,x+42,y+42),outline=TEAL,width=6)
    d.polygon([(x,y),(x,y+42),(x+11,y+32),(x+22,y+51),(x+31,y+46),(x+20,y+28),(x+37,y+28)],fill='white',outline='#17202b',width=3)
def save(im, n): im.save(OUT / 'frames' / f'frame_{n:04d}.png',compress_level=1)

if args.stage == 'prepare':
    OUT.mkdir(parents=True,exist_ok=False)
    current = Path('D:/CodeSpace/track-mesh/apps/desktop/src-tauri/src/receive.rs').read_bytes()
    copied = (ROOT/'demo-ui-v5/receive.rs.txt').read_bytes()
    assert current == copied, 'Current receive.rs differs; re-review dialog before use'
    # Extract the existing exact synthetic dialog, rather than inventing product wording.
    script = (ROOT/'scripts/capture_demo_ui_v5.cjs').read_text(encoding='utf-8')
    dialog = json.loads(script.split('const DIALOG = ',1)[1].split(';\nfunction drawDialog',1)[0])
    import html
    message = html.escape(dialog['message'])
    page = f'''<!doctype html><meta charset="utf-8"><style>
    *{{box-sizing:border-box}}body{{margin:0;background:{BG};font-family:'Segoe UI',sans-serif;color:{WHITE};width:1080px;height:1920px}}
    h1{{margin:0;position:absolute;top:92px;left:60px;font-size:55px;font-weight:600}}
    .note{{position:absolute;top:186px;left:60px;font-size:30px;color:{TEAL}}}
    .dialog{{position:absolute;left:60px;top:300px;width:960px;border:2px solid #aaa;border-radius:10px;overflow:hidden;background:#fff;color:#1a1a1a}}
    .title{{background:#f1f1f1;padding:22px 26px;font-size:36px;border-bottom:1px solid #ccc}}
    .body{{padding:30px;font-size:34px;line-height:1.42;white-space:pre-line}}
    .buttons{{display:flex;justify-content:flex-end;gap:18px;padding:24px;background:#f0f0f0;border-top:1px solid #ddd}}
    button{{font-family:inherit;font-size:36px;min-width:200px;padding:14px 24px;border:2px solid #bbb;border-radius:5px;background:#fafafa}}
    #get{{border:3px solid #0067c0}}
    .footer{{position:absolute;left:60px;top:1790px;font-size:36px;color:{GREY}}}
    .data{{position:absolute;left:60px;top:1845px;font-size:29px;color:{GREY}}}
    </style><h1>Get it when you're ready.</h1><div class="note">Reconstructed confirmation · Not a screen recording</div>
    <section class="dialog"><div class="title">{html.escape(dialog['title'])}</div><div class="body">{message}</div>
    <div class="buttons"><button id="get">Get</button><button>Cancel</button></div></section>
    <div class="footer">Concept visualization</div><div class="data">Example data · Editorial trial</div>'''
    (OUT/'confirmation.html').write_text(page,encoding='utf-8')
    meta = {'source_movie':str(ROOT/'renders/film/trackmesh-studios-v09-review-cut01.mp4'),
      'source_frame_range':[300,560], 'source_interval_seconds':[299/24,560/24],
      'frames':261,'fps':24,'duration_seconds':261/24,'resolution':[1080,1920],
      'edit':[{'frames':[1,18],'view':'Existing Studio B overview'},
              {'frames':[19,42],'view':'Synthetic source UI Get button; illustrative click'},
              {'frames':[43,198],'view':'Reflowed reconstructed confirmation; illustrative Get click at end'},
              {'frames':[199,228],'view':'Synthetic transfer states; 97% held only 6 frames; edited timing, not a speed test'},
              {'frames':[229,261],'view':'Synthetic completed state'}],
      'receive_sha256':hashlib.sha256(current).hexdigest(), 'receive_matches_v5':True,
      'native_confirmation_capture_available':False,'new_3d_render':False,'audio':False,
      'publication_approved':False,'full_movie_modified':False}
    (OUT/'manifest.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print(OUT)
else:
    (OUT/'frames').mkdir(exist_ok=True)
    asset = ROOT/'assets/screens/v5'
    dialog = Image.open(OUT/'confirmation.png').convert('RGB')
    button = json.loads((OUT/'button.json').read_text())
    getx,gety = button['x']+button['width']/2,button['y']+button['height']/2
    # Decode screenshot of the actual MP4 for the crop quality comparison.
    original = Image.open(ROOT/'logs/trackmesh-studios-v09-review-cut01-decoded/frame_0370.png').convert('RGB')
    crop = original.crop((520,265,1410,815)).resize((1020,630),Image.Resampling.LANCZOS)
    proof = base('1080p crop quality check','Existing encoded frame 370 · enlarged dialog')
    proof.paste(crop,(30,490)); proof.save(OUT/'encoded-crop-quality.png')
    for n in range(1,262):
        if n <= 18:
            im = base('Get it when you\'re ready.','STUDIO B')
            raw = Image.open(ROOT/f'renders/frames/studios-v09/frame_{299+n:04d}.png').convert('RGB')
            # Crop for the portrait canvas, never exceed the original image height.
            paste_fit(im,raw.crop((670,0,1278,1080)),(60,300,1020,1670))
        elif n <= 42:
            im = base('Get it when you\'re ready.','Source UI · Synthetic state')
            src = Image.open(asset/'app-new.png').convert('RGB')
            paste_fit(im,src.crop((1080,425,1825,680)),(60,440,1020,1090))
            d=ImageDraw.Draw(im);d.text((60,1260),'Get Studio A\'s version',font=face(51,True),fill=WHITE)
            # Button crop mapped into its fitted display rectangle (960 × 329).
            cursor(im,253,720,pressed=n>=37)
        elif n <= 198:
            im=dialog.copy()
            if n>=183: cursor(im,round(getx),round(gety),pressed=n>=193)
        else:
            done=n>=229
            state='done' if done else ('get97' if n<205 else 'get98' if n<217 else 'get99')
            im=base('Version received.' if done else 'Getting Studio A\'s version…','Source UI · Synthetic state')
            src=Image.open(asset/f'app-{state}.png').convert('RGB')
            paste_fit(im,src.crop((345,225,1835,690)),(45,360,1035,1010))
            ImageDraw.Draw(im).text((60,1570),'Timing edited · Not a speed test',font=face(30),fill=GREY)
            if not done:
                # Two labelled detail crops retain the exact original status pixels/values.
                paste_fit(im,src.crop((375,578,850,625)),(60,930,1020,1030))
                paste_fit(im,src.crop((1560,578,1810,625)),(60,1040,1020,1130))
                d=ImageDraw.Draw(im)
                lines=['Only the changed parts travel.','Example: 44 MB new','in a 1.6 GB project.']
                for i,line in enumerate(lines): d.text((60,1190+i*76),line,font=face(46,i==0),fill=WHITE if i==0 else GREY)
        save(im,n)
    # Phone-size evidence; no sharpening or super-resolution claims.
    for n in (25,120,195,220,255):
        im=Image.open(OUT/f'frames/frame_{n:04d}.png')
        im.resize((390,693),Image.Resampling.LANCZOS).save(OUT/f'phone-{n:04d}.png')
    print('Composed 261 frames; no Blender scene render was performed.')

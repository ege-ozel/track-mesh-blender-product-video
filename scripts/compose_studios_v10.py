"""Compose independent 30s landscape and 20s portrait edits from existing v09 sources."""
import argparse, hashlib, json, math, os, textwrap, shutil
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('aspect',choices=['16x9','9x16']);p.add_argument('--stills',action='store_true');p.add_argument('--refresh-transfer99',action='store_true');p.add_argument('--refresh-layout',action='store_true');p.add_argument('--refresh-pc',action='store_true');p.add_argument('--polish',action='store_true');args=p.parse_args()
M=args.aspect=='9x16';W,H=(1080,1920) if M else (1920,1080)
ORIGINAL_TAG=f'studios-v10-final-{args.aspect}'
TAG=ORIGINAL_TAG+('-polish01' if args.polish else '')
OUT=ROOT/'renders/frames'/TAG;OUT.mkdir(exist_ok=True)
FRAMES=OUT/'frames';FRAMES.mkdir(exist_ok=True)
CACHE=OUT/'cache';CACHE.mkdir(exist_ok=True)
RAW=ROOT/'renders/frames/studios-v09';UI=ROOT/'assets/screens/v10-edit'
ui=json.loads((UI/'manifest.json').read_text())
WHITE,GREY,TEAL='#f5f7f7','#b2c2c7','#6ed9c2'
font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/'+('seguisb.ttf' if b else 'segoeui.ttf'),n)
if M:
    phases=[('a',1,30),('save',31,48),('share',49,72),('sharing',73,90),('shared',91,126),
      ('b',127,156),('get',157,180),('dialog',181,300),('transfer',301,324),('done',325,384),('pc',385,432),('end',433,480)]
else:
    phases=[('a',1,96),('save',97,114),('share',115,144),('sharing',145,168),('shared',169,228),
      ('b',229,300),('get',301,324),('dialog',325,456),('transfer',457,480),('done',481,540),('pc',541,624),('end',625,720)]

@lru_cache(maxsize=32)
def load(path):return Image.open(path).convert('RGB')
def base():return Image.new('RGB',(W,H),'#0b121b')
def wrap(s,f,width):
    lines=[];line=''
    for word in s.split():
        trial=(line+' '+word).strip()
        if f.getlength(trial)>width and line:lines.append(line);line=word
        else:line=trial
    if line:lines.append(line)
    return lines
def words(im,xy,text,size,colour=WHITE,bold=False,width=None,gap=1.35):
    d=ImageDraw.Draw(im);f=font(size,bold)
    lines=wrap(text,f,width or W-xy[0]*2)
    for i,line in enumerate(lines):d.text((xy[0],xy[1]+round(i*size*gap)),line,font=f,fill=colour)
    return len(lines)*size*gap
def footer(im):
    d=ImageDraw.Draw(im);size=30 if M else 26;body='Concept visualization · Example data';f=font(size)
    d.rounded_rectangle((40 if M else 55,H-82,W-40 if M else W-55,H-24),radius=8,fill=(7,14,21))
    d.text((W//2,H-72),body,font=f,fill=GREY,anchor='mt')
    return im
def cursor(im,x,y,pressed=False):
    d=ImageDraw.Draw(im);scale=1.25 if M else 1.1
    if pressed:
        r=36*scale;d.ellipse((x-r,y-r,x+r,y+r),outline=TEAL,width=5)
    pts=[(x,y),(x,y+42*scale),(x+11*scale,y+32*scale),(x+22*scale,y+51*scale),(x+31*scale,y+46*scale),(x+20*scale,y+28*scale),(x+37*scale,y+28*scale)]
    d.polygon(pts,fill='white',outline='#17202b',width=3)
def example(im):
    x=60 if M else 190;y=1320 if M else 872
    words(im,(x,y),'Only the changed parts travel.',44 if M else 48,bold=True)
    words(im,(x,y+(76 if M else 70)),'Example: 44 MB new in a 1.6 GB project.',40 if M else 38,colour=GREY,width=W-x*2)

def share(im,state,phase):
    # The conceptual DAW backdrop and native SDK-host capture are flat inserts;
    # no moving 3D panel edges and no unsupported native-resolution claim.
    daw=load(str(ROOT/'assets/screens/daw.png'))
    if M:
        bg=ImageOps.fit(daw,(W,1050),Image.Resampling.LANCZOS,centering=(.5,.4))
        bg=ImageEnhance.Brightness(bg).enhance(.36);im.paste(bg,(0,280))
        x,y,width=60,415,960
    else:
        bg=ImageOps.fit(daw,(W,H),Image.Resampling.LANCZOS)
        im.paste(ImageEnhance.Brightness(bg).enhance(.33),(0,0));x,y,width=500,220,920
    pic=load(str(ROOT/f'assets/screens/v5/vst3-{state}.png'))
    height=round(width*pic.height/pic.width)
    im.paste(pic.resize((width,height),Image.Resampling.LANCZOS),(x,y))
    titles={'save':'Save in your DAW.','share':'Share current version','sharing':'Sharing…','shared':'Shared.'}
    words(im,(60 if M else 130,80 if M else 65),titles[phase],58 if M else 64,bold=True)
    if phase=='save': message=''
    elif phase=='share':message='Saved. Press Share current version to send it.'
    elif phase=='sharing':message='Sharing… waiting for the DAW to finish saving.'
    else:message='Shared. Your collaborator can get this version while TrackMesh is open.'
    if message:
        yy=1170 if M else 900
        if args.polish:
            xx=60 if M else 190;size=38 if M else 36
            line_count=len(wrap(message,font(size),W-(120 if M else 380)))
            text_height=math.ceil(line_count*size*1.35)
            box=(xx-32,yy-20,W-xx+32,min(H-92,yy+text_height+24))
            shade=Image.new('RGBA',(W,H));sd=ImageDraw.Draw(shade)
            sd.rounded_rectangle((xx-8,yy-6,W-xx+8,yy+text_height+8),radius=10,fill=(5,10,16,165))
            shade=shade.filter(ImageFilter.GaussianBlur(12))
            clipped=Image.new('RGBA',(W,H));clipped.paste(shade.crop(box),(box[0],box[1]))
            im.paste(Image.alpha_composite(im.convert('RGBA'),clipped).convert('RGB'))
        words(im,(60 if M else 190,yy),message,38 if M else 36,colour=GREY,width=W-(120 if M else 380))
    return (x+150*width/580,y+208*height/384)

@lru_cache(maxsize=4)
def split():
    left=load(str(RAW/'frame_0600_A.png'));right=load(str(RAW/'frame_0600_B.png'))
    im=base();d=ImageDraw.Draw(im)
    if M:
        im.paste(left.crop((0,140,960,900)).resize((W,855),Image.Resampling.LANCZOS),(0,0))
        im.paste(right.crop((0,140,960,900)).resize((W,855),Image.Resampling.LANCZOS),(0,855))
        d=ImageDraw.Draw(im);d.rectangle((0,851,W,859),fill='#070e15')
        for y,label,c in [(45,'STUDIO A','#e8aa6e'),(900,'STUDIO B',TEAL)]:
            d.rounded_rectangle((40,y-10,245,y+48),radius=8,fill='#0b121b');d.text((55,y),label,font=font(29,True),fill=c)
        layer=Image.new('RGBA',(W,H));ld=ImageDraw.Draw(layer);ld.rectangle((0,1560,W,H),fill=(0,0,0,180))
        im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
        words(im,(60,1595),'PC to PC.',60,bold=True)
        words(im,(60,1680),'A direct link. No cloud copy of your project files.',36,colour=GREY,width=960)
        d=ImageDraw.Draw(im);d.line((1010,450,1010,1320),fill=TEAL,width=4)
        for y in (450,1320):d.ellipse((1001,y-9,1019,y+9),fill=TEAL)
    else:
        im.paste(left,(0,0));im.paste(right,(960,0));d=ImageDraw.Draw(im)
        d.rectangle((956,0,964,H),fill='#070e15')
        for x,label,c in [(60,'STUDIO A','#e8aa6e'),(1020,'STUDIO B',TEAL)]:
            d.rounded_rectangle((x-15,45,x+210,110),radius=8,fill='#0b121b');d.text((x,55),label,font=font(30,True),fill=c)
        pts=[]
        for i in range(81):
            t=i/80;pts.append((480+960*t,410-240*math.sin(math.pi*t)))
        d.line(pts,fill=TEAL,width=4)
        layer=Image.new('RGBA',(W,H));ld=ImageDraw.Draw(layer);ld.rectangle((0,845,W,H),fill=(0,0,0,170))
        im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
        words(im,(125,850),'PC to PC.',64,bold=True)
        words(im,(125,935),'A direct link. No cloud copy of your project files.',36,colour=GREY)
    return im

@lru_cache(maxsize=2)
def endcard():
    # Freeze and soften the background: no outro camera shimmer on keys/windows.
    im=split().filter(ImageFilter.GaussianBlur(36));im=ImageEnhance.Brightness(im).enhance(.22)
    d=ImageDraw.Draw(im);cy=H//2
    d.text((W//2,cy-150),'TrackMesh',font=font(116 if M else 140,True),fill=WHITE,anchor='mt')
    d.text((W//2,cy+30),'Share DAW projects, PC to PC.',font=font(42 if M else 50),fill=TEAL,anchor='mt')
    d.text((W//2,cy+125),'For Windows',font=font(34 if M else 38),fill=GREY,anchor='mt')
    return im

def render(phase,n,first,last):
    im=base();point=None;local=n-first;length=last-first+1
    if phase in ('a','b'):
        if phase=='a':f=1+round(local*95/max(1,length-1))
        else:f=229+round(local*71/max(1,length-1))
        raw=load(str(RAW/f'frame_{f:04d}.png'))
        im=ImageOps.fit(raw,(W,H),Image.Resampling.LANCZOS,centering=(.5,.5))
        layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
        d.rectangle((0,H-(400 if M else 260),W,H),fill=(0,0,0,145))
        im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
        yy=1450 if M else 835
        words(im,(60 if M else 125,yy),'Two studios. One project.' if phase=='a' else 'Your collaborator sees it.',52 if M else 64,bold=True)
        words(im,(60 if M else 125,yy+90),'Meet TrackMesh.' if phase=='a' else 'Another studio.',40 if M else 38,colour=GREY)
        d=ImageDraw.Draw(im);d.rounded_rectangle((45,50,270,120),radius=10,fill='#0b121b')
        d.text((60,65),'STUDIO A' if phase=='a' else 'STUDIO B',font=font(30,True),fill=TEAL)
    elif phase in ('save','share','sharing','shared'):
        state={'save':'idle','share':'saved','sharing':'sharing','shared':'shared'}[phase]
        point=share(im,state,phase)
        if phase!='share':point=None
    elif phase in ('get','dialog','transfer','done'):
        if phase=='transfer':
            state='transfer97' if local<6 else 'transfer98' if local<15 else 'transfer99'
        else:state=phase
        im=load(str(UI/f'{args.aspect}-{state}.png')).copy()
        if phase=='dialog' and not M:
            original=im;im=base()
            im.paste(original.crop((0,0,W,200)),(0,0))
            im.paste(original.crop((260,215,1660,1017)),(260,195))
        # Completion appears once, as the actual large status in the panel.
        if phase=='done':ImageDraw.Draw(im).rectangle((0,0,W,240),fill='#0b121b')
        if phase in ('transfer','done'):example(im)
        if phase in ('get','dialog'):
            key='card-get' if phase=='get' else 'confirm-get';r=ui['assets'][f'{args.aspect}-{state}']['buttons'][key]
            point=(r['x']+r['width']/2,r['y']+r['height']/2)
            if phase=='dialog' and not M:point=(point[0],point[1]-20)
    elif phase=='pc':im=split().copy()
    elif phase=='end':
        im=endcard().copy()
        alpha=min(1,(local+1)/8,(length-local)/12)
        if alpha<1:im=Image.blend(base(),im,max(0,alpha))
    if point and local>=length-14:
        off=max(0,(length-6-local))*3
        cursor(im,point[0]+off,point[1]+off,pressed=local>=length-6)
    return footer(im)

review=[]
for phase,first,last in phases:review.extend([first,min(first+8,last),(first+last)//2,max(first,last-6),last])
review=sorted(set(review))
total=phases[-1][2]
manifest={'tag':TAG,'frames':total,'fps':24,'duration_seconds':total/24,'resolution':[W,H],
 'movie':str(ROOT/'renders/film'/f'trackmesh-{TAG}.mp4'),'phases':[{'name':p,'first':a,'last':b,'duration_seconds':(b-a+1)/24} for p,a,b in phases],
 'review_frames':review,'example_frames':next((a for p,a,b in phases if p=='transfer')), 'example_last':next((b for p,a,b in phases if p=='done')),
 'example_duration_seconds':3.5,'audio':False,'publication_approved':False,
 'notes':'Synthetic editorial UI; conceptual DAW backdrop. Native VST3 bitmap remains 580x384; scaling does not add detail. No actual transfer timing or real DAW verification. Percentages start near 100 only in this example because data is reused.'}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
selection=review if args.stills else range(1,total+1)
if args.refresh_transfer99:
    start,end=next((a,b) for p,a,b in phases if p=='transfer');selection=range(start+15,end+1)
if args.refresh_layout:
    assert not M,'Layout patch applies to landscape only'
    selection=[n for p,a,b in phases if p in ('pc','dialog','end') for n in range(a,b+1)]
if args.refresh_pc:
    assert not M
    selection=[n for p,a,b in phases if p=='pc' for n in range(a,b+1)]
for n in selection:
    target=FRAMES/f'frame_{n:04d}.png'
    if target.exists() and not (args.refresh_transfer99 or args.refresh_layout or args.refresh_pc):continue
    phase,first,last=next(p for p in phases if p[1]<=n<=p[2])
    if args.polish and phase not in ('share','sharing','shared'):
        shutil.copyfile(ROOT/'renders/frames'/ORIGINAL_TAG/f'frames/frame_{n:04d}.png',target)
        continue
    # Static phases are cached; moving source footage and illustrative clicks get
    # distinct keys. Hardlinks keep the full image sequence without extra copies.
    click=phase in ('share','get','dialog') and n>=last-13
    dynamic=phase in ('a','b','end') or click
    key=f'{phase}-{n if dynamic else 0}'
    if phase=='transfer':key+=('-97' if n-first<6 else '-98' if n-first<15 else '-99')
    cached=CACHE/f'{key}.png'
    if not cached.exists() or args.refresh_transfer99 or args.refresh_layout or args.refresh_pc:render(phase,n,first,last).save(cached,compress_level=1)
    if args.refresh_transfer99 or args.refresh_layout or args.refresh_pc:shutil.copyfile(cached,target)
    else:
        try:os.link(cached,target)
        except PermissionError:shutil.copyfile(cached,target)
    if n in review:
        small=load(str(target)).copy()
        if M:small=small.resize((390,693),Image.Resampling.LANCZOS)
        else:small=small.resize((960,540),Image.Resampling.LANCZOS)
        small.save(OUT/f'review-{n:04d}.png')
    if n%24==0 or n==total:print(json.dumps({'aspect':args.aspect,'frame':n,'total':total,'phase':phase}),flush=True)
print('V10_COMPOSE_COMPLETE '+str(OUT),flush=True)

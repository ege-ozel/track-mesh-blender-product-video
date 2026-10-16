"""Edit a studios-vNN render folder into finished frames: split screens, the link arc, captions and place tags.
python scripts/compose_studios.py studios-v03 [--percent 50] [--frames 60,160]
Reads renders/previews/<tag>-<percent>/ (stills) or renders/frames/<tag>/ (--percent 100 --sequence);
writes <folder>/edit/frame_NNNN.png. Wording lives here, so it can change without re-rendering.
"""
import argparse, json, math, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('tag'); parser.add_argument('--percent', type=int, default=50)
parser.add_argument('--frames', default=''); parser.add_argument('--sequence', action='store_true')
args = parser.parse_args()
folder = ROOT / (f'renders/frames/{args.tag}' if args.sequence else f'renders/previews/{args.tag}-{args.percent}')
out = folder / 'edit'; out.mkdir(exist_ok=True)
points = json.loads((folder / 'split-points.json').read_text()) if (folder / 'split-points.json').exists() else {}
W, H = 1920 * args.percent // 100, 1080 * args.percent // 100
k = W / 1920
font = lambda name, size: ImageFont.truetype(f'C:/Windows/Fonts/{name}', round(size * k))
REGULAR, SEMI, BOLD = 'segoeui.ttf', 'seguisb.ttf', 'segoeuib.ttf'
WHITE, GREY, TEAL = (245, 247, 247), (178, 194, 199), (110, 217, 194)
SPLIT_FROM, END = 457, 720
PLACE_A, PLACE_B = 'STUDIO A  ·  ISTANBUL', 'STUDIO B  ·  BERLIN'
# (first, last, title, subtitle, place tag) — the place tag says which room we are in.
CAPTIONS = [
    (12, 90, 'Two studios. One project.', 'Meet TrackMesh.', PLACE_A),
    (104, 222, 'Save in your DAW.', 'One click shares the new version.', None),  # close-ups: no tag over the screen
    (236, 318, 'Your collaborator sees it.', 'Another studio, another city.', PLACE_B),
    # The subtitle follows the screen: the DAW question first, then the Get that starts near 97 %.
    (332, 450, "Get it when you're ready.", [(332, 386, 'Close the project in your DAW first.'),
                                             (390, 450, 'Only what changed travels: 44 MB of a 1.6 GB project.')], None),
    (470, 590, 'PC to PC.', 'A direct link. No cloud copy of your project files.', None),
]

def fade(frame, first, last, length=10):
    return max(0.0, min(1.0, (frame - first) / length, (last - frame) / length))

def text(layer, xy, body, face, colour, alpha, anchor='ls', spacing=0):
    draw = ImageDraw.Draw(layer)
    if spacing:  # letter-spaced small caps for place tags, on a soft dark patch so they read over bright windows
        x, y = xy
        width = sum(face.getlength(ch) + spacing * k for ch in body)
        patch = Image.new('RGBA', layer.size)
        ImageDraw.Draw(patch).rounded_rectangle((x - 14 * k, y - face.size - 10 * k, x + width + 10 * k, y + 12 * k), 12 * k, fill=(4, 6, 10, round(210 * alpha)))
        layer.alpha_composite(patch.filter(ImageFilter.GaussianBlur(4 * k)))
        for ch in body:
            draw.text((x, y), ch, font=face, fill=(*colour, round(255 * alpha)), anchor=anchor); x += face.getlength(ch) + spacing * k
        return
    shadow = Image.new('RGBA', layer.size); ImageDraw.Draw(shadow).text((xy[0] + 2 * k, xy[1] + 2 * k), body, font=face, fill=(0, 0, 0, round(150 * alpha)), anchor=anchor)
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(3 * k)))
    draw.text(xy, body, font=face, fill=(*colour, round(255 * alpha)), anchor=anchor)

def link(layer, a, b, frame):
    """Teal arc from screen A to screen B with a soft glow; project packets travel it once Get starts."""
    mid = ((a[0] + b[0]) / 2, min(a[1], b[1]) - 230 * k)
    curve = [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * mid[0] + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * mid[1] + t * t * b[1])
             for t in (i / 80 for i in range(81))]
    drawn = max(0.0, min(1.0, (frame - SPLIT_FROM) / 24))  # draws itself over the first second
    visible = curve[:max(2, round(len(curve) * drawn))]
    glow = Image.new('RGBA', layer.size); ImageDraw.Draw(glow).line(visible, fill=(*TEAL, 150), width=round(14 * k), joint='curve')
    layer.alpha_composite(glow.filter(ImageFilter.GaussianBlur(9 * k)))
    ImageDraw.Draw(layer).line(visible, fill=(*TEAL, 235), width=max(2, round(3.5 * k)), joint='curve')
    if 470 <= frame <= 590:
        for i in range(8):
            t = ((frame - 470) / 34 - i * .22) % 1.6
            if t > 1: continue
            x, y = curve[round(t * 80)]
            dot = Image.new('RGBA', layer.size); r = 7 * k
            ImageDraw.Draw(dot).ellipse((x - r * 2, y - r * 2, x + r * 2, y + r * 2), fill=(*TEAL, 120))
            layer.alpha_composite(dot.filter(ImageFilter.GaussianBlur(5 * k)))
            ImageDraw.Draw(layer).ellipse((x - r * .6, y - r * .6, x + r * .6, y + r * .6), fill=(230, 255, 248, 255))

def compose(frame):
    single = folder / f'frame_{frame:04d}.png'
    if single.exists():
        image = Image.open(single).convert('RGBA'); a_point = b_point = None
    else:
        left, right = (Image.open(folder / f'frame_{frame:04d}_{s}.png').convert('RGBA') for s in 'AB')
        image = Image.new('RGBA', (W, H), (0, 0, 0, 255)); image.paste(left, (0, 0)); image.paste(right, (W // 2, 0))
        ImageDraw.Draw(image).rectangle((W // 2 - max(1, round(2 * k)), 0, W // 2 + max(1, round(2 * k)), H), fill=(6, 8, 11, 255))
        pa, pb = points[f'frame_{frame:04d}_A.png'], points[f'frame_{frame:04d}_B.png']
        a_point = (pa[0] * W / 2, (1 - pa[1]) * H - 120 * k); b_point = (W / 2 + pb[0] * W / 2, (1 - pb[1]) * H - 120 * k)
    layer = Image.new('RGBA', image.size)
    if a_point: link(layer, a_point, b_point, frame)
    for first, last, title, subtitle, place in CAPTIONS:
        alpha = fade(frame, first, last)
        if alpha <= 0: continue
        text(layer, (125 * k, H - 167 * k), title, font(SEMI, 64), WHITE, alpha)
        for start, end, line in subtitle if isinstance(subtitle, list) else [(first + 4, last, subtitle)]:
            if fade(frame, start, end) > 0: text(layer, (125 * k, H - 108 * k), line, font(REGULAR, 36), GREY, min(alpha, fade(frame, start, end, 6)))
        if place: text(layer, (125 * k, 104 * k), place, font(SEMI, 24), TEAL, alpha * .9, spacing=3)
    if frame >= SPLIT_FROM:  # one place tag per half while split
        alpha = fade(frame, SPLIT_FROM + 6, 712)
        text(layer, (60 * k, 104 * k), PLACE_A, font(SEMI, 22), (232, 170, 110), alpha * .9, spacing=3)
        text(layer, (W / 2 + 60 * k, 104 * k), PLACE_B, font(SEMI, 22), TEAL, alpha * .9, spacing=3)
    if frame >= 606:
        alpha = fade(frame, 606, 712)
        backdrop = Image.new('RGBA', image.size); ImageDraw.Draw(backdrop).rectangle((0, H * .62, W, H), fill=(0, 0, 0, round(120 * alpha)))
        layer.alpha_composite(backdrop.filter(ImageFilter.GaussianBlur(40 * k)))
        text(layer, (W / 2, H - 215 * k), 'TrackMesh', font(BOLD, 120), WHITE, alpha, anchor='ms')
        text(layer, (W / 2, H - 140 * k), 'Share DAW projects, PC to PC.', font(REGULAR, 42), TEAL, fade(frame, 616, 712), anchor='ms')
    # Bottom right: clear of the place tags and the bright city window.
    text(layer, (W - 60 * k, H - 50 * k), 'Concept visualization', font(REGULAR, 24), GREY, .75, anchor='rs')
    image.alpha_composite(layer)
    if frame > 700:  # fade to black
        image.alpha_composite(Image.new('RGBA', image.size, (0, 0, 0, round(255 * min(1, (frame - 700) / 16)))))
    image.convert('RGB').save(out / f'frame_{frame:04d}.png')

frames = sorted({int(m.group(1)) for p in folder.glob('frame_*.png') if (m := re.match(r'frame_(\d{4})', p.name))})
if args.frames: frames = [int(f) for f in args.frames.split(',')]
for frame in frames: compose(frame)
print(f'Composed {len(frames)} frames into {out}')

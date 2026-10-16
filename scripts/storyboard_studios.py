"""Lay out composed preview frames of a studios-vNN version as one storyboard page.
python scripts/storyboard_studios.py studios-v04
Reads renders/previews/<tag>-50/edit/, writes renders/previews/<tag>-storyboard.png.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[1]
tag = sys.argv[1]
PANELS = [(60, 'S1 · Studio A, İstanbul — kuruluş planı'), (135, 'S2 · Kaydedildi — imleç Paylaş düğmesine gidiyor'),
          (175, 'S2 · Tek tık: Paylaşılıyor…'), (210, 'S2 · Paylaşıldı'), (300, 'S3 · Studio B, Berlin — sakin şehir, yeni sürüm'),
          (370, "S4 · Al → “Proje DAW'da kapalı mı?”"), (430, "S4 · İndirme %97'den başlıyor (1,6 GB'ın 44 MB'ı)"),
          (530, 'S5 · PC to PC — bölünmüş ekran'), (690, 'S6 · Kapanış — TrackMesh')]
label = ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf', 26); title = ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf', 34)
rows = (len(PANELS) + 1) // 2
page = Image.new('RGB', (2 * 960 + 3 * 24, 80 + rows * 600), (11, 15, 22)); draw = ImageDraw.Draw(page)
draw.text((24, 22), f'TrackMesh — İki stüdyo · storyboard ({tag}, 960×540 önizleme)', font=title, fill=(235, 240, 242))
for i, (frame, text) in enumerate(PANELS):
    x = 24 + (i % 2) * 984; y = 80 + (i // 2) * 600
    draw.text((x, y + 8), f'{text}  ·  kare {frame}', font=label, fill=(200, 212, 216))
    page.paste(Image.open(ROOT / f'renders/previews/{tag}-50/edit/frame_{frame:04d}.png'), (x, y + 50))
out = ROOT / f'renders/previews/{tag}-storyboard.png'; page.save(out); print(out)

"""Archive superseded videos after final verification; preserve bytes and relative paths."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RENDERS=(ROOT/'renders').resolve()
KEEP={
 (RENDERS/'film/trackmesh-studios-v10-final-16x9.mp4').resolve(),
 (RENDERS/'film/trackmesh-studios-v10-final-9x16.mp4').resolve(),
}
for p in KEEP:
 assert p.is_file()
 aspect='16x9' if '16x9' in p.name else '9x16'
 verification=json.loads((ROOT/f'logs/trackmesh-studios-v10-final-{aspect}-decoded/verification.json').read_text())
 assert verification['playback']['ended'] and not verification['playback']['error']
 assert verification['normalSpeedReview']['playbackRate']==1
assert (RENDERS/'readme/trackmesh-flow-v06.gif').is_file()
target=RENDERS/'archive/2026-10-22-pre-v10'
suffix=2
while target.exists():target=RENDERS/f'archive/2026-10-22-pre-v10-{suffix:02d}';suffix+=1
assert target.resolve().is_relative_to(RENDERS)
items=[]
for p in sorted(RENDERS.rglob('*')):
 if not p.is_file() or p.suffix.lower() not in ('.mp4','.webm','.mov','.avi'):continue
 src=p.resolve();relative=src.relative_to(RENDERS)
 if relative.parts[0]=='archive' or src in KEEP:continue
 dst=(target/relative).resolve()
 # Check absolute source and destination containment before any move.
 assert src.is_relative_to(RENDERS) and dst.is_relative_to(target.resolve())
 assert not dst.exists()
 items.append({'source':str(src),'archive':str(dst),'bytes':src.stat().st_size,'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
assert items,'No superseded videos found'
target.mkdir(parents=True,exist_ok=False)
manifest={'archive':str(target),'reason':'User requested archiving older videos after v10 final completion. No files deleted.','kept_final_movies':[str(p) for p in sorted(KEEP)],'items':items}
(target/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
for item in items:
 src=Path(item['source']);dst=Path(item['archive'])
 assert src.resolve().is_relative_to(RENDERS) and dst.resolve().is_relative_to(target.resolve())
 dst.parent.mkdir(parents=True,exist_ok=True);src.rename(dst)
 assert dst.stat().st_size==item['bytes'] and hashlib.sha256(dst.read_bytes()).hexdigest()==item['sha256']
manifest['verified_after_move']=True
(target/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'archive':str(target),'videos':len(items),'bytes':sum(i['bytes'] for i in items),'verified':True},indent=2))

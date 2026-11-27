"""Freeze read-only product source and prepare the v5 concept capture pipeline.
Does not build or change the product, use its profile, or contact peers.
Run once per review; refuses to replace an existing source snapshot.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('D:/CodeSpace/track-mesh')
TARGET = ROOT / 'demo-ui-v5'
if TARGET.exists():
    raise SystemExit('demo-ui-v5 already exists; keep this review snapshot immutable.')
TARGET.mkdir()
for name in ('index.html', 'main.tsx', 'mock-core.ts'):
    shutil.copy2(ROOT / 'demo-ui-v4' / name, TARGET / name)
shutil.copytree(SOURCE / 'apps/desktop/src', TARGET / 'source')
receive = SOURCE / 'apps/desktop/src-tauri/src/receive.rs'
shutil.copy2(receive, TARGET / 'receive.rs.txt')
hashes = {str(p.relative_to(TARGET)): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in (TARGET / 'source').rglob('*') if p.is_file()}
hashes['receive.rs.txt'] = hashlib.sha256(receive.read_bytes()).hexdigest()
manifest = {'source': str(SOURCE), 'head': subprocess.check_output(
    ['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip(),
    'source_status': subprocess.check_output(['git', '-C', str(SOURCE), 'status', '--short'], text=True),
    'hashes': hashes, 'synthetic_only': True,
    'dialog': 'Browser reconstruction of the native dialog; exact source wording, synthetic filenames and sizes.'}
(ROOT / 'logs/review-source-v5.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
build = (ROOT / 'scripts/build_demo_ui_v4.mjs').read_text(encoding='utf-8').replace('demo-ui-v4', 'demo-ui-v5')
build = build.replace("replacement: path.join(source, 'src')", "replacement: path.join(root, 'demo-ui-v5/source')")
(ROOT / 'scripts/build_demo_ui_v5.mjs').write_text(build, encoding='utf-8')
mock = (TARGET / 'mock-core.ts').read_text(encoding='utf-8')
mock = mock.replace("history: [],", "head: ahead || got ? newer : older, head_fetched: true, fetched_head: (ahead || got ? newer : older).snapshot_id, history: [],")
mock = mock.replace('requests: [] }', 'requests: [], offers: [] }')
mock = mock.replace('presence: {},', 'removed_projects: [], joined_projects: [project], offerable_devices: {}, head_pull_errors: [], presence: {},')
mock = mock.replace('pending_publications: 0, mailbox_enabled: false,', '')
mock = mock.replace('2026-10-14', '2026-10-21')
(TARGET / 'mock-core.ts').write_text(mock, encoding='utf-8')
capture = (ROOT / 'scripts/capture_demo_ui_v4.cjs').read_text(encoding='utf-8').replace('demo-ui-v4', 'demo-ui-v5').replace('screens/v4', 'screens/v5').replace('ui-capture-v4', 'ui-capture-v5')
start = capture.index('const DIALOG = ')
end = capture.index('function drawDialog', start)
dialog = {'title': "Get Studio A's version?", 'message': 'Added: 1 · Changed: 2 · Removed: 1\n+ Samples/Audio/new-layer.wav\n~ Neon Forest.als\n~ Samples/Audio/pad.wav\n− Samples/Audio/old-layer.wav\n\nNew data: about 44.0 MB · free on this drive: 128.0 GB\nClose this project in your DAW first. TrackMesh keeps a backup of the files it replaces; Open my previous files opens them.\n\nGet this version?', 'ok': 'Get', 'cancel': 'Cancel'}
capture = capture[:start] + 'const DIALOG = ' + json.dumps(dialog, ensure_ascii=False) + ';\n' + capture[end:]
capture = capture.replace('transform:scale(1.5);width:470px', 'transform:scale(1.35);width:600px')
capture = capture.replace('line-height:1.45;background:#fff', 'line-height:1.45;white-space:pre-line;background:#fff')
capture = capture.replace('const errors = [];', 'const errors = [];')
capture = capture.replace("log[state] = {file, errors, body:", "log[state] = {file, errors, dialogReconstruction: state === 'ask', body:")
(ROOT / 'scripts/capture_demo_ui_v5.cjs').write_text(capture, encoding='utf-8')
native = (ROOT / 'scripts/capture_real_vst3_v4.py').read_text(encoding='utf-8').replace('screens/v4', 'screens/v5').replace('video-vst3-v4', 'video-vst3-v5').replace('native-vst3-capture-v4', 'native-vst3-capture-v5').replace('2026-10-14', '2026-10-21')
(ROOT / 'scripts/capture_real_vst3_v5.py').write_text(native, encoding='utf-8')
print(json.dumps({'head': manifest['head'], 'snapshot': str(TARGET), 'files': len(hashes)}, indent=2))

"""Capture every TrackMesh VST3 state, in English and Turkish, from the real plugin in the official SDK editor host.
python scripts/capture_vst3_phases.py
A synthetic Named Pipe fixture answers as the agent; the words are the ones crates/core/src/ipc/status.rs and
presence.rs send. Screens are grabbed from the desktop (PrintWindow can miss owner-drawn buttons).
No production profile, project, peer or action is used. Writes assets/screens/phases/<lang>-<state>.png.
"""
import os, json, time, threading, struct, subprocess
from pathlib import Path
import win32api, win32con, win32gui, win32process, win32security, win32pipe, win32file, pywintypes
from PIL import ImageGrab, Image
import ctypes, win32ui
ROOT = Path(__file__).resolve().parents[1]
binary = Path('D:/CodeSpace/track-mesh/.build/vst3/VST3/Release/TrackMesh.vst3/Contents/x86_64-win/TrackMesh.vst3')
host = ROOT / 'tools/vst3-editorhost/bin/editorhost.exe'
out = ROOT / 'assets/screens/phases'; out.mkdir(parents=True, exist_ok=True)
token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), win32con.TOKEN_QUERY)
sid = win32security.ConvertSidToStringSid(win32security.GetTokenInformation(token, win32security.TokenUser)[0])
SHARE = 1
OLD, NEW = '4c1e' + '0' * 60, '7f31' + '0' * 60
PROJECTS = [{'project_id': '11111111-2222-4333-8444-555555555555', 'name': 'Neon Forest', 'folder_name': 'Neon Forest'},
            {'project_id': '22222222-3333-4444-8555-666666666666', 'name': 'Beat Tape', 'folder_name': 'Beat Tape'}]
MANY = PROJECTS + [{'project_id': f'3333333{i}-4444-4555-8666-77777777777{i}', 'name': n, 'folder_name': n}
                   for i, n in enumerate(['Night Drive', 'Track 07', 'Remix Ideas', 'Live Set', 'Vocal Takes'])]

def base(lang):
    tr = lang == 'tr'
    return {'ok': True, 'project_name': 'Neon Forest', 'local_snapshot': OLD, 'remote_snapshot': OLD, 'author': 'Studio B',
            'created_at': '2026-10-14T13:05:00Z', 'peer_online': True, 'connection': 'DIRECT', 'state': 'UP_TO_DATE', 'message': '',
            'projects': [], 'projects_more': False, 'picker_supported': True, 'desktop_available': True,
            'status_line': "Studio B'un son sürümü sende ✓" if tr else "You have Studio B's latest version ✓",
            'share_enabled': True, 'get_enabled': False, 'pending_publications': 0, 'auto_share_supported': True, 'auto_share': False,
            'presence_warning': '', 'share_confirmation': '', 'presence_danger': False, 'presence_since': 0, 'presence_get_line': '',
            'language': lang, 'get_label': "Studio B'un sürümünü al" if tr else "Get Studio B's version"}

def phases(lang):
    tr = lang == 'tr'
    w = lambda en, t: t if tr else en
    working = w('Studio B is working on this project now', 'Studio B şu an bu projede çalışıyor')
    return [
        ('unreachable', w('TrackMesh is not running', "TrackMesh çalışmıyor"), None),
        ('picker', w('Choose the project', 'Proje seçimi'), {'project_name': '', 'projects': PROJECTS}),
        ('picker-one', w('Choose the project: only one', 'Proje seçimi: tek proje'), {'project_name': '', 'projects': PROJECTS[:1]}),
        ('picker-many', w('Choose the project: seven, scrolls', 'Proje seçimi: yedi proje, kayar'), {'project_name': '', 'projects': MANY}),
        ('no-projects', w('No projects in TrackMesh yet', "TrackMesh'te henüz proje yok"), {'project_name': '', 'projects': []}),
        ('no-collaborator', w('No collaborator yet', 'Henüz iş arkadaşı yok'),
         {'author': '', 'peer_online': False, 'state': 'LAST_KNOWN', 'created_at': '', 'status_line': w('Invite a collaborator in TrackMesh.', "TrackMesh'te bir iş arkadaşını davet et."),
          'get_label': w("Get collaborator's version", 'İş arkadaşının sürümünü al')}),
        ('up-to-date', w('Up to date', 'Güncel'), {}),
        ('saved', w('Saved in the DAW (auto share off)', "DAW'da kaydedildi (otomatik paylaşım kapalı)"),
         {'message': w('Saved. Press Share current version to send it.', "Kaydedildi. Göndermek için Güncel sürümü paylaş'a bas.")}),
        ('sharing', w('Sharing', 'Paylaşılıyor'), {'message': w('Sharing… waiting for the DAW to finish saving.', "Paylaşılıyor… DAW'ın kaydetmeyi bitirmesi bekleniyor.")}),
        ('shared', w('Shared', 'Paylaşıldı'),
         {'state': 'LOCAL_AHEAD', 'local_snapshot': NEW, 'status_line': w("Your version is newer than Studio B's", "Senin sürümün Studio B'un sürümünden daha yeni"),
          'message': w('Shared. Your collaborator can get this version while TrackMesh is open.', 'Paylaşıldı. TrackMesh açıkken iş arkadaşın bu sürümü alabilir.')}),
        ('auto-share', w('Share when I save: on', 'Kaydedince paylaş: açık'),
         {'auto_share': True, 'message': w('Every DAW save is now shared.', 'Artık her DAW kaydı paylaşılıyor.')}),
        ('new-version', w('New version from the collaborator', 'İş arkadaşından yeni sürüm'),
         {'state': 'REMOTE_AHEAD', 'remote_snapshot': NEW, 'created_at': '2026-10-14T16:31:00Z', 'get_enabled': True,
          'status_line': w('Studio B shared a new version', 'Studio B yeni bir sürüm paylaştı')}),
        ('get-handoff', w('After Get: TrackMesh opened', 'Al sonrası: TrackMesh açıldı'),
         {'state': 'REMOTE_AHEAD', 'remote_snapshot': NEW, 'created_at': '2026-10-14T16:31:00Z', 'get_enabled': True,
          'status_line': w('Studio B shared a new version', 'Studio B yeni bir sürüm paylaştı'),
          'message': w('TrackMesh is open on this project. Save and close the project in your DAW, then press Get there.',
                       "TrackMesh bu projede açıldı. Projeyi DAW'da kaydedip kapat, sonra orada Al'a bas.")}),
        ('getting', w('Getting a version', 'Sürüm alınıyor'),
         {'state': 'RECEIVING', 'remote_snapshot': NEW, 'created_at': '2026-10-14T16:31:00Z', 'share_enabled': False,
          'status_line': w("Getting Studio B's version… 97 %", "Studio B'un sürümü alınıyor… %97")}),
        ('offline', w('Collaborator not connected', 'İş arkadaşı bağlı değil'),
         {'peer_online': False, 'state': 'OFFLINE', 'status_line': w("Studio B is not connected. You can get their version when they are.", 'Studio B bağlı değil. Bağlanınca sürümü alınabilir.')}),
        ('presence', w('Collaborator is working on it', 'İş arkadaşı üzerinde çalışıyor'),
         {'presence_warning': working, 'presence_since': 1792141200,
          'share_confirmation': w('Studio B is working on this project now. Share anyway?', 'Studio B şu an bu projede çalışıyor. Yine de paylaşılsın mı?')}),
        ('share-anyway', w('Share while they work: confirm', 'O çalışırken paylaş: onay'),
         {'presence_warning': working, 'presence_since': 1792141200,
          'share_confirmation': w('Studio B is working on this project now. Share anyway?', 'Studio B şu an bu projede çalışıyor. Yine de paylaşılsın mı?'), 'click': SHARE}),
        ('both-working', w('Both working: versions may split', 'İkiniz de çalışıyorsunuz: sürümler ayrılabilir'),
         {'presence_danger': True, 'presence_warning': w('Studio B is also working on this project. If you both save changes, your versions will split.',
                                                          'Studio B de bu projede çalışıyor. İkiniz de kaydederseniz sürümleriniz ayrılır.')}),
        ('diverged', w('Versions split', 'Sürümler ayrıldı'),
         {'state': 'DIVERGED', 'status_line': w('You and Studio B both changed the project. Choose which version to keep in TrackMesh.',
                                                "Senin sürümün de Studio B'un sürümü de değişti. Hangisinin kalacağını TrackMesh'te seç.")}),
        ('recovery', w('Last Get did not finish', 'Son alma işlemi bitmedi'),
         {'state': 'RECOVERY_REQUIRED', 'share_enabled': False, 'status_line': w('The last Get did not finish. Close the project in your DAW and press Recover in TrackMesh.',
                                                                                "Son alma işlemi bitmedi. Projeyi DAW'da kapat ve TrackMesh'te Kurtar'a bas.")}),
        ('refused', w('Action refused', 'İşlem reddedildi'),
         {'ok': False, 'state': '', 'status_line': '', 'message': w("Sharing isn't possible yet. Open TrackMesh to see what it needs.", 'Paylaşım henüz mümkün değil. Neye ihtiyaç olduğunu görmek için TrackMesh\'i aç.')}),
    ]

def capture(lang, name, overrides):
    output = out / f'{lang}-{name}.png'
    suffix = f'tm-{os.getpid()}-{int(time.time() * 1000) % 100000}'  # the plugin accepts at most 32 characters
    events, errors, finished = [], [], threading.Event()
    click = (overrides or {}).pop('click', None) if overrides is not None else None
    pipe = None
    if overrides is not None:
        security = pywintypes.SECURITY_ATTRIBUTES()
        security.SECURITY_DESCRIPTOR = win32security.ConvertStringSecurityDescriptorToSecurityDescriptor('D:P(A;;GA;;;' + sid + ')', 1)
        pipe = win32pipe.CreateNamedPipe('\\\\.\\pipe\\TrackMesh-v1-' + sid + '-' + suffix, win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_READMODE_BYTE | win32pipe.PIPE_WAIT | 8, 1, 65536, 65536, 1000, security)
        def read_exact(size):
            data = b''
            while len(data) < size:
                _, part = win32file.ReadFile(pipe, size - len(data))
                if not part: raise RuntimeError('Pipe disconnected')
                data += part
            return data
        def serve():
            try:
                try: win32pipe.ConnectNamedPipe(pipe, None)
                except pywintypes.error as exc:
                    if exc.winerror != 535: raise
                while not finished.is_set():
                    size = struct.unpack('<I', read_exact(4))[0]
                    if size > 65536: raise RuntimeError('Oversized IPC frame')
                    request = json.loads(read_exact(size)); events.append(request.get('event', ''))
                    reply = {**base(lang), **overrides, 'project_id': request['project_id']}
                    payload = json.dumps(reply).encode('utf-8')
                    win32file.WriteFile(pipe, struct.pack('<I', len(payload)) + payload)
            except Exception as exc:
                if not finished.is_set(): errors.append(str(exc))
        threading.Thread(target=serve, daemon=True).start()
    env = os.environ.copy(); env['TRACKMESH_IPC_SUFFIX'] = suffix
    env['TRACKMESH_DATA_DIR'] = str(ROOT / 'demo-vst3/unused-isolated-profile')
    env['TRACKMESH_AGENT_PATH'] = str(ROOT / 'demo-vst3/disabled-owner-not-installed.exe')
    process = subprocess.Popen([str(host), str(binary)], env=env, cwd=str(ROOT))
    child = top = None
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and child is None:
            found = []
            def inspect_window(hwnd, _):
                if win32process.GetWindowThreadProcessId(hwnd)[1] != process.pid: return
                def inspect_child(ch, _):
                    if win32gui.GetClassName(ch) == 'TrackMeshVST3View-v1': found.append((hwnd, ch))
                win32gui.EnumChildWindows(hwnd, inspect_child, None)
            win32gui.EnumWindows(inspect_window, None)
            if found:
                top, child = found[0]
                win32gui.SetWindowPos(top, 0, -6000, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE)
                break
            if process.poll() is not None: raise RuntimeError(f'Editor host exited: {process.returncode}')
            time.sleep(.1)
        if child is None: raise RuntimeError('Native VST3 window not created')
        if pipe:
            while time.monotonic() < deadline and not events: time.sleep(.1)
            if not events: raise RuntimeError('Plugin did not connect to the fixture pipe')
        time.sleep(4 if pipe is None else 1.5)
        if click:
            button = win32gui.GetDlgItem(child, click)
            win32gui.SendMessage(button, win32con.BM_CLICK, 0, 0); time.sleep(.6)
        # Quiet capture: the host window sits off-screen and never takes focus; DWM renders it for PrintWindow.
        l, t, r, b = win32gui.GetClientRect(child); width, height = r - l, b - t
        src = win32gui.GetWindowDC(child); dc = win32ui.CreateDCFromHandle(src); mem = dc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap(); bmp.CreateCompatibleBitmap(dc, width, height); mem.SelectObject(bmp)
        ctypes.windll.user32.PrintWindow(child, mem.GetSafeHdc(), 3)
        info = bmp.GetInfo(); Image.frombuffer('RGB', (info['bmWidth'], info['bmHeight']), bmp.GetBitmapBits(True), 'raw', 'BGRX', 0, 1).save(output)
        win32gui.DeleteObject(bmp.GetHandle()); mem.DeleteDC(); dc.DeleteDC(); win32gui.ReleaseDC(child, src)
        return {'file': output.name, 'events': sorted(set(events)), 'errors': errors}
    finally:
        finished.set()
        if top and process.poll() is None: win32gui.PostMessage(top, win32con.WM_CLOSE, 0, 0)
        try: process.wait(timeout=6)
        except subprocess.TimeoutExpired: process.terminate(); process.wait(timeout=3)
        # The pipe is not closed here: closing a handle while the server thread still blocks on it can hang.
        # Each state runs in its own process (below), so the handle goes away with it.

import sys
if len(sys.argv) == 4 and sys.argv[1] == '--one':
    lang, name = sys.argv[2], sys.argv[3]
    overrides = next(o for n, _, o in phases(lang) if n == name)
    print('RESULT ' + json.dumps(capture(lang, name, None if overrides is None else dict(overrides))), flush=True)
    os._exit(0)

index = {}
for lang in ('en', 'tr'):
    for name, label, _ in phases(lang):
        result = {'file': None, 'errors': ['timed out']}
        for attempt in range(2):
            try:
                run = subprocess.run([sys.executable, __file__, '--one', lang, name], capture_output=True, text=True, timeout=45)
                line = next((l for l in run.stdout.splitlines() if l.startswith('RESULT ')), None)
                if line: result = json.loads(line[7:]); break
                result = {'file': None, 'errors': [run.stderr.strip()[-300:]]}
            except subprocess.TimeoutExpired:
                subprocess.run(['taskkill', '/F', '/IM', 'editorhost.exe'], capture_output=True)
        index.setdefault(name, {})[lang] = {'label': label, **result}
        print(lang, name, result.get('file'), result.get('errors'), flush=True)
(out / 'index.json').write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')

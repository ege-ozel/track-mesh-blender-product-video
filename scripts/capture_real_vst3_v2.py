"""Load the unmodified current TrackMesh VST3 in the official SDK editor host, once per state.
Each run serves synthetic Studio A status through a unique current-user pipe and captures only the
plugin's native child window with PrintWindow. No production profile, project, peer or action is used.
"""
import os,json,time,threading,struct,subprocess,hashlib,ctypes
from pathlib import Path
import win32api,win32con,win32gui,win32ui,win32process,win32security,win32pipe,win32file,pywintypes
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
binary=Path('D:/CodeSpace/track-mesh/.build/vst3/VST3/Release/TrackMesh.vst3/Contents/x86_64-win/TrackMesh.vst3')
host=ROOT/'tools/vst3-editorhost/bin/editorhost.exe'
out=ROOT/'assets/screens/v2';out.mkdir(parents=True,exist_ok=True)
token=win32security.OpenProcessToken(win32api.GetCurrentProcess(),win32con.TOKEN_QUERY)
sid=win32security.ConvertSidToStringSid(win32security.GetTokenInformation(token,win32security.TokenUser)[0])

base={'ok':True,'project_name':'Neon Forest','local_snapshot':'4c1e'+'0'*60,'remote_snapshot':'4c1e'+'0'*60,
  'author':'Studio B','created_at':'2026-10-14T13:05:00Z','peer_online':True,'connection':'DIRECT','state':'UP_TO_DATE',
  'message':'','projects':[],'projects_more':False,'picker_supported':True,'desktop_available':True,
  'status_line':"You have Studio B's latest version \u2713",'share_enabled':True,'get_enabled':False,'pending_publications':0,
  'auto_share_supported':True,'auto_share':True,'presence_warning':'','share_confirmation':'','presence_danger':False,
  'presence_since':0,'presence_get_line':'','language':'en','get_label':"Get Studio B's version"}
# Same wording as crates/core/src/ipc/status.rs (saving(), Notice::Committed, LOCAL_AHEAD line).
states={
  'idle':{},
  'saving':{'message':'Saved. Sharing once the DAW finishes writing files\u2026'},
  'shared':{'state':'LOCAL_AHEAD','local_snapshot':'7f31'+'0'*60,'status_line':"Your version is newer than Studio B's",
    'message':'Shared. Your collaborator can get this version while TrackMesh is open.'},
}

def capture(name,overrides):
    output=out/f'vst3-{name}.png'
    suffix=f'video-vst3-v2-{name}-{os.getpid()}'
    pipe_name='\\\\.\\pipe\\TrackMesh-v1-'+sid+'-'+suffix
    security=pywintypes.SECURITY_ATTRIBUTES()
    security.SECURITY_DESCRIPTOR=win32security.ConvertStringSecurityDescriptorToSecurityDescriptor('D:P(A;;GA;;;'+sid+')',1)
    pipe=win32pipe.CreateNamedPipe(pipe_name,win32pipe.PIPE_ACCESS_DUPLEX,
      win32pipe.PIPE_TYPE_BYTE|win32pipe.PIPE_READMODE_BYTE|win32pipe.PIPE_WAIT|8,1,65536,65536,1000,security)
    events=[];errors=[];finished=threading.Event()
    def read_exact(size):
        data=b''
        while len(data)<size:
            _,part=win32file.ReadFile(pipe,size-len(data))
            if not part:raise RuntimeError('Pipe disconnected')
            data+=part
        return data
    def serve():
        try:
            try:win32pipe.ConnectNamedPipe(pipe,None)
            except pywintypes.error as exc:
                if exc.winerror!=535:raise
            while not finished.is_set():
                size=struct.unpack('<I',read_exact(4))[0]
                if size>65536:raise RuntimeError('Oversized IPC frame')
                request=json.loads(read_exact(size))
                event=request.get('event','');events.append(event)
                reply={**base,**overrides,'project_id':request['project_id']}
                if event not in ('PLUGIN_CONNECTED','GET_STATUS','PROJECT_ID','SESSION_ENDING','SAVE_OBSERVED'):
                    reply['ok']=False;reply['message']='Static demo capture: actions disabled.'
                payload=json.dumps(reply).encode('utf-8')
                win32file.WriteFile(pipe,struct.pack('<I',len(payload))+payload)
        except Exception as exc:
            if not finished.is_set():errors.append(str(exc))
    threading.Thread(target=serve,daemon=True).start()
    env=os.environ.copy();env['TRACKMESH_IPC_SUFFIX']=suffix
    env['TRACKMESH_DATA_DIR']=str(ROOT/'demo-vst3/unused-isolated-profile')
    env['TRACKMESH_AGENT_PATH']=str(ROOT/'demo-vst3/disabled-owner-not-installed.exe')
    process=subprocess.Popen([str(host),str(binary)],env=env,cwd=str(ROOT))
    child=None;top=None
    try:
        deadline=time.monotonic()+20
        while time.monotonic()<deadline and child is None:
            found=[]
            def inspect_window(hwnd,_):
                if win32process.GetWindowThreadProcessId(hwnd)[1]!=process.pid:return
                def inspect_child(ch,_):
                    if win32gui.GetClassName(ch)=='TrackMeshVST3View-v1':found.append((hwnd,ch))
                win32gui.EnumChildWindows(hwnd,inspect_child,None)
            win32gui.EnumWindows(inspect_window,None)
            if found:top,child=found[0];break
            if process.poll() is not None:raise RuntimeError(f'Editor host exited: {process.returncode}')
            time.sleep(.1)
        if child is None:raise RuntimeError('Native VST3 window not created')
        while time.monotonic()<deadline and not events:time.sleep(.1)
        if not events:raise RuntimeError('Native plugin did not connect to isolated fixture pipe')
        time.sleep(1.5)
        win32gui.RedrawWindow(child,None,None,win32con.RDW_INVALIDATE|win32con.RDW_UPDATENOW|win32con.RDW_ALLCHILDREN)
        time.sleep(.2)
        left,top_px,right,bottom=win32gui.GetClientRect(child);width=right-left;height=bottom-top_px
        native_dc=win32gui.GetWindowDC(child);source_dc=win32ui.CreateDCFromHandle(native_dc)
        capture_dc=source_dc.CreateCompatibleDC();bitmap=win32ui.CreateBitmap();bitmap.CreateCompatibleBitmap(source_dc,width,height)
        capture_dc.SelectObject(bitmap)
        if not ctypes.windll.user32.PrintWindow(child,capture_dc.GetSafeHdc(),1):raise RuntimeError('PrintWindow failed')
        info=bitmap.GetInfo();pixels=bitmap.GetBitmapBits(True)
        Image.frombuffer('RGB',(info['bmWidth'],info['bmHeight']),pixels,'raw','BGRX',0,1).save(output)
        win32gui.DeleteObject(bitmap.GetHandle());capture_dc.DeleteDC();source_dc.DeleteDC();win32gui.ReleaseDC(child,native_dc)
        return {'capture':str(output),'dimensions':[width,height],'events':sorted(set(events)),'errors':errors}
    finally:
        finished.set()
        if top and process.poll() is None:win32gui.PostMessage(top,win32con.WM_CLOSE,0,0)
        try:process.wait(timeout=6)
        except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=3)
        win32file.CloseHandle(pipe)

result={'plugin_binary':str(binary),'plugin_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
  'status_source':'synthetic local Named Pipe fixture','no_actual_snapshot_or_transfer':True,
  'captures':{name:capture(name,overrides) for name,overrides in states.items()}}
(ROOT/'logs/native-vst3-capture-v2.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))

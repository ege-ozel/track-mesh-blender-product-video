import bpy, json, platform, sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
prefs = bpy.context.preferences.addons['cycles'].preferences
result = {'version': bpy.app.version_string, 'binary': bpy.app.binary_path, 'platform': platform.platform(), 'initial_engine': bpy.context.scene.render.engine, 'initial_cycles_device': bpy.context.scene.cycles.device, 'initial_compute_type': prefs.compute_device_type, 'accelerators': {}, 'selection': 'CPU'}
for backend in ('OPTIX','CUDA','HIP','ONEAPI','METAL'):
    try:
        prefs.compute_device_type = backend
        prefs.get_devices()
        devices = [{'name':d.name,'type':d.type,'id':d.id} for d in prefs.devices if d.type == backend]
        result['accelerators'][backend] = {'available':bool(devices), 'devices':devices}
        if result['selection'] == 'CPU' and any(d['type'] == backend for d in devices):
            result['selection'] = backend
    except Exception as exc:
        result['accelerators'][backend] = {'unavailable':str(exc)}
(root/'logs/environment-blender.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('TRACKMESH_PROBE '+json.dumps(result))

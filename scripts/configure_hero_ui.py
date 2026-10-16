"""Configure this visible Blender process only; never save user preferences."""
import bpy
scene=bpy.context.scene
backend=scene.get('render_backend','CPU')
if backend!='CPU':
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type=backend;prefs.get_devices()
    for device in prefs.devices:device.use=device.type==backend
    scene.cycles.device='GPU'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.overlay.show_overlays=False
            area.spaces.active.region_3d.view_perspective='CAMERA'
print('TRACKMESH: visible review configured; preferences not saved.')

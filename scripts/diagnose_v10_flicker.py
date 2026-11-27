"""Small fixed-camera diagnostic only; do not save or alter the original blend."""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'renders/previews/studios-v10-flicker-diagnostic'
OUT.mkdir(exist_ok=False)
s=bpy.context.scene;s.frame_set(140)
cam=bpy.data.objects['A close'];cam.animation_data_clear();cam.data.animation_data_clear()
fixed=cam.matrix_world.copy();s.camera=cam
for m in s.timeline_markers:m.camera=cam
cursor=bpy.data.objects.get('Studio A cursor')
if cursor:cursor.animation_data_clear();cursor.hide_render=True
s.render.resolution_percentage=100;s.render.resolution_x=1920;s.render.resolution_y=1080
border=bpy.data.objects['A plugin window border'];original_y=border.location.y
report={'fixed_camera':True,'resolution':[1920,1080],'states':[],'original_border_y':original_y,
        'samples':s.eevee.taa_render_samples,'original_blend_saved':False}
for variant in ('baseline','border-separated'):
    border.location.y=original_y+(0.004 if variant=='border-separated' else 0)
    for f in (140,141,142):
        s.frame_set(f);cam.matrix_world=fixed;s.camera=cam
        s.render.filepath=str(OUT/f'{variant}-{f}.png')
        bpy.ops.render.render(write_still=True)
        report['states'].append({'variant':variant,'frame':f,'border_y':border.location.y})
(OUT/'manifest.json').write_text(json.dumps(report,indent=2))
print('V10_FIXED_CAMERA_DIAGNOSTIC_COMPLETE')

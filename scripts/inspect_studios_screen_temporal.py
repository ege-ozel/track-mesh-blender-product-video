"""Read-only geometry/camera inspection; never render or save the source blend."""
import bpy,json
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
names=['Studio A DAW','A plugin window border','Studio A plugin / idle','Studio A plugin / saved','Studio A plugin / sharing','Studio A plugin / shared','Studio B app / new']
report={'objects':{},'frames':{}}
for name in names:
    o=bpy.data.objects.get(name)
    if not o: continue
    coords=[o.matrix_world@v.co for v in o.data.vertices]
    report['objects'][name]={'y_range':[min(v.y for v in coords),max(v.y for v in coords)],'images':[n.image.name for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]}
for f in list(range(130,191))+list(range(292,318)):
    scene.frame_set(f)
    report['frames'][str(f)]={}
    for name in ['Studio A DAW','Studio A plugin / saved','Studio B app / new']:
        o=bpy.data.objects.get(name)
        if not o: continue
        pts=[world_to_camera_view(scene,scene.camera,o.matrix_world@v.co) for v in o.data.vertices]
        report['frames'][str(f)][name]=[[p.x*1920,(1-p.y)*1080] for p in pts]
(ROOT/'logs/studios-v09-temporal-geometry.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report['objects'],indent=2))

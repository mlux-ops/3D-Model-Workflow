"""Package static browser viewer with self-contained frozen-picks data."""
from pathlib import Path
import json,base64,re
P=Path(__file__).resolve().parents[1]
out=P/'deliverables/viewer3d'
payload=json.loads((out/'picks.json').read_text(encoding='utf-8'))
# The finished viewer is a single offline HTML file opened through file://.
# Chrome taints 2D canvases sourced from neighboring file:// JPGs, preventing
# physically source-backed typed-pixel PBR textures. Embed ONLY existing
# authorised viewer product photos as image DATA URIs in the HTML payload.
# The generated picks.json retains unchanged relative asset paths/receipts.
# This is not a tile selection or image retouch.
photo_cache={}
for room in payload['rooms']:
    for entry in list(room.get('products') or [])+list((room.get('alternative') or {}).get('products') or []):
        photo=entry.get('image')
        if not photo or photo.startswith('data:'):continue
        path=(out/photo).resolve()
        assert path.is_relative_to(out.resolve()), 'IMAGE OUTSIDE VIEWER ASSETS'
        if not path.is_file():continue
        if path not in photo_cache:
            suffix=path.suffix.lower()
            assert suffix in ('.jpg','.jpeg','.png','.webp')
            mime={'.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.webp':'image/webp'}[suffix]
            photo_cache[path]='data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode('ascii')
        entry['image']=photo_cache[path]
# R068: retain primary bathing-product records independently of frozen
# viewer picks/program. The current plumbing schedule lists a bathtub for
# EACH primary, while the selected physical WALK-IN program and 48in LINEAR
# shower drain retain their existing truth. No tub source coordinates or
# manufacturer solid exists. Embed short frozen row metadata for inspectors
# only; NEVER upgrade a schedule line to a placed or approved 3D fixture.
primary_sheet_tubs={}
for room_id,sku in [('PH-PRIMARY','700337000000090'),('TX-PRIMARY','TER-N-SW-OF')]:
    rows=json.loads((P/'rooms'/room_id/'plumbing.json').read_text(encoding='utf-8'))['fixtures']
    matches=[x for x in rows if x.get('model_or_sku')==sku]
    assert len(matches)==1, 'Primary sheet bathtub source mismatch: '+room_id
    item=matches[0]
    primary_sheet_tubs[room_id]={k:item.get(k) for k in (
        'description','manufacturer','model_or_sku','source_row_id','source',
        'status','qty_per_unit','finish','deck_reference')}
    primary_sheet_tubs[room_id].update(
        spatial_status='3D UNLOCATED; no native tub family/room insertion',
        program_selection_unchanged=True,not_installed_fixture=True)
assert len(payload['rooms'])==13
assert payload.get('phase')=='v4_native_wall_face_architecture_r043', 'Run native wall-face architectural registration after drawing envelope enrichment'
assert sum(len(room.get('physical_instances',[])) for room in payload['rooms'])==26
assert next(r for r in payload['rooms'] if r['id']=='PH-BATH4')['champion_id']=='round-036-B'
assert not next(r for r in payload['rooms'] if r['id']=='TX-POWDER')['has_pick']
template=(P/'scratch/viewer3d_index_template.html').read_text(encoding='utf-8')
assert template.count('__VIEWER_JSON__')==1
assert template.count('__IMPORT_MAP__')==1
assert len(re.findall(r'<script type="module">.*?</script>',template,re.S))==1
scene_script=(P/'scratch/viewer3d_scene_v2.js').read_text(encoding='utf-8')
completion=(P/'scratch/viewer3d_completion.js').read_text(encoding='utf-8')
native_module=(P/'scratch/native_room_geometry.js').read_text(encoding='utf-8')
scene_script=scene_script.replace('const ROOMS=DATA.rooms;',
    'const NATIVE_AUDIT=await loadNativeAudit();\nconst ROOMS=buildAuditedRooms(DATA.rooms,NATIVE_AUDIT);',1)
startup='try{\n if(!loadInstanceAddress(location.hash))'
assert scene_script.count(startup)==1, 'Viewer startup hook changed'
scene_script=scene_script.replace(startup,native_module+'\n'+completion+'\ninstallViewerCompletion();\ninstallNativeAudit();\n'+startup,1)
assert scene_script.count("import * as THREE from 'three'")==1
assert "window.__viewerDebug" in scene_script
template=re.sub(r'<script type="module">.*?</script>',
                lambda m:'<script type="module">\n'+scene_script+'\n</script>',
                template, count=1, flags=re.S)
vendor=out/'vendor'
def dataurl(name):
    return 'data:text/javascript;base64,'+base64.b64encode((vendor/name).read_bytes()).decode('ascii')
imports={'imports':{'three':dataurl('three.module.js'),'orbit-controls':dataurl('OrbitControls.js')}}
rendered=(template.replace('__VIEWER_JSON__',json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'))
                  .replace('__IMPORT_MAP__',json.dumps(imports,separators=(',',':'))))
primary_blob='<script id="r068-primary-plumbing" type="application/json">'+json.dumps(
    primary_sheet_tubs,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+'</script>\n'
assert rendered.count('<script type="module">')==1
rendered=rendered.replace('<script type="module">',primary_blob+'<script type="module">',1)
native_blob='<script id="native-geometry" type="application/octet-stream">'+base64.b64encode(
    (out/'native_geometry.json.gz').read_bytes()).decode('ascii')+'</script>\n'
rendered=rendered.replace('<script type="module">',native_blob+'<script type="module">',1)
(out/'index.html').write_text(rendered,encoding='utf-8')
print('PASS HTML viewer',out/'index.html',len(rendered),'chars',len(payload['rooms']),'rooms')

import json
import native_query as native
from apply_casing import run

snapshot=json.loads((native.TASK/'native_panel_inspection.json').read_text())['result']['targets'][0]
face=next(f for f in snapshot['solids'][0]['faces'] if f['normal'][1]<-.999)
depth=max(p['start'][1] for f in snapshot['solids'][0]['faces'] for loop in f['loops'] for p in loop)-min(p['start'][1] for f in snapshot['solids'][0]['faces'] for loop in f['loops'] for p in loop)
point=[37.33999190966225,-55.69033126642166,37.666666666666664]
rails=[]
for side,(xmin,xmax) in [('Left',(-1.5-1/24,-1.5)),('Right',(1.5,1.5+1/24))]:
    probe=point[0]+(xmin+xmax)/2
    intervals=[]
    for loop in face['loops']:
        xs=[c['start'][0] for c in loop];zs=[c['start'][2] for c in loop]
        if min(xs)<probe<max(xs) and min(zs)>38.34 and max(zs)<46.74:
            intervals.append((min(zs)-point[2],max(zs)-point[2]))
    for index,(zmin,zmax) in enumerate(sorted(set(intervals))):
        rails.append({'name':side+' panel border '+str(index+1),'profile':[[xmin,-depth,zmin],[xmax,-depth,zmin],[xmax,-depth,zmax],[xmin,-depth,zmax]]})
assert len(rails)==4,rails
arguments={'depth':depth,'rails':rails}
(native.TASK/'cut_family_arguments.json').write_text(json.dumps(arguments,indent=2))
created=run('cut_family_create','family.create',{'template':'C:/ProgramData/Autodesk/RVT 2025/Family Templates/English-Imperial/Generic Model.rft'},document={},preconditions={})
document={'session_id':created['session_id']}
(native.TASK/'cut_family_document.json').write_text(json.dumps(document))
preconditions={'is_family':True,'allow_existing_document':True}
built=run('cut_family_build','compiled.modify',{'assembly':'C:/ProgramData/CodexNativeRevit/plugins/belmont_window_trim/BelmontWindowTrimCut.dll','type':'BuildWindowTrimCut','purpose':'Author native editable void and panel-border extrusions in the new task family','expected_changes':['Only the new family: one editable void, four editable molding extrusions, height/thickness/material parameters'],'arguments':arguments},document=document,preconditions=preconditions)
print(json.dumps({'native_build':built['data']}))

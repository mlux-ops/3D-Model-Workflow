"""READ-ONLY native Revit discovery for the HTML 3D viewer; no Revit writes."""
from pathlib import Path
import json,subprocess,sys,collections,datetime
P=Path(__file__).resolve().parents[1]
SCR=P/'scratch'
R=P/'state/revit_receipts'
T='25-006 1527 N Wieland'
OUT=SCR/'viewer3d_revit_sources.json'
categories={
 'walls':('OST_Walls',1000),
 'plumbing':('OST_PlumbingFixtures',500),
 'room_tags':('OST_RoomTags',500),
 'doors':('OST_Doors',1000),
 'windows':('OST_Windows',1000),
 'floors':('OST_Floors',1000),
 'ceilings':('OST_Ceilings',1000),
 'casework':('OST_Casework',500),
 'generic_models':('OST_GenericModel',1000),
}
cached={'walls':'11fe1ae7-dd61-4a81-9b56-4bd3af4b8194','plumbing':'06086028-6c51-4b90-9158-84403650e1f1'}
data={'model_title':T,'read_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'categories':{},'errors':[]}
for key,(category,limit) in categories.items():
 try:
  receipt=R/(cached[key]+'.json') if key in cached else None
  if receipt is None or not receipt.is_file():
   q=SCR/('viewer3d_revit_req_'+key+'.json')
   q.write_text(json.dumps({'category':category,'limit':limit}),encoding='utf-8')
   cmd=[sys.executable,str(P/'tools/revit_read.py'),'elements.query','--title',T,'--args-file',str(q)]
   proc=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
   if proc.returncode: raise RuntimeError(proc.stderr.strip()[:500])
   payload=json.loads(proc.stdout)
   receipt=R/(payload['operation_id']+'.json')
  raw=json.loads(receipt.read_text(encoding='utf-8'))
  if raw.get('status')!='completed': raise RuntimeError(str(raw.get('error')))
  res=raw['result']
  items=res.get('items',[]) if isinstance(res,dict) else []
  data['categories'][key]={'receipt_id':raw['operation_id'],'count':len(items),'next_offset':res.get('next_offset'),'items':items}
  coordinates=[]
  for item in items:
   box=item.get('bounds')
   if box and box.get('min') and box.get('max'): coordinates.append((box['min'],box['max']))
  ranges={a:[round(min(v[a][k] for v in coordinates),2),round(max(v[a][k+0] for v in coordinates),2)] for a,k in []} if False else {}
  if coordinates:
   for axis in range(3):
    ranges['xyz'[axis]]=[round(min(v[0][axis] for v in coordinates),2),round(max(v[1][axis] for v in coordinates),2)]
  print(key,'receipt',raw['operation_id'],'count',len(items),'next',res.get('next_offset'),'extents',ranges,flush=True)
  if key in ('room_tags','doors','windows','casework'):
   print('  samples',[(i.get('id'),str(i.get('name'))[:48],i.get('location')) for i in items[:3]],flush=True)
 except Exception as exc:
  data['errors'].append({'category':key,'error':str(exc)})
  print('ERROR',key,str(exc)[:300],flush=True)
 OUT.write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
print('SAVED',OUT,'error_count',len(data['errors']),flush=True)

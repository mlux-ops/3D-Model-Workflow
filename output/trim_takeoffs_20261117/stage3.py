exec(open('output/trim_takeoffs_20261117/inventory.py',encoding='utf-8-sig').read().split('for i,d in enumerate(docs):')[0].replace("print(label,json.dumps(r),flush=True)","print(label,r['status'],flush=True); return r"))
jobs=[]
def submit(d,label,op,args):
 r=c.submit(op,{'session_id':d['session_id'],'path':d['path']},args,{'expected_title':d['title'],'is_family':False,'allow_existing_document':True}); jobs.append((label,r['operation_id']))
for i,d in enumerate(docs):
 prefix=['belmont','wieland'][i]
 for kind in ['project_info','revisions']:
  for e in json.loads((out/(prefix+'_'+kind+'.json')).read_text())['result']['items']: submit(d,prefix+'_params_'+str(e['id']),'parameters.query',{'element':e['unique_id']})
 if i==0:
  for e in json.loads((out/'belmont_sweeps.json').read_text())['result']['items']:
   if e['name']=='Baseboard' or 'Crown' in e['name']:
    submit(d,prefix+'_params_'+str(e['id']),'parameters.query',{'element':e['unique_id']})
  for e in json.loads((out/'belmont_casework.json').read_text())['result']['items']:
   if e['name'].startswith('Casework') or 'Crown' in e['name'] or 'trim' in e['name'].lower():
    submit(d,prefix+'_params_'+str(e['id']),'parameters.query',{'element':e['unique_id']})
    submit(d,prefix+'_inspect_'+str(e['id']),'elements.inspect',{'element':e['unique_id'],'geometry':True})
 else:
  for label,args in [('generic',{'category':'OST_GenericModel','limit':500}),('walls',{'class':'Wall','limit':500}),('sheets',{'class':'ViewSheet','limit':500}),('types_trim',{'types':True,'name_contains':'trim','limit':500}),('types_crown',{'types':True,'name_contains':'crown','limit':500}),('types_base',{'types':True,'name_contains':'baseboard','limit':500})]: submit(d,prefix+'_'+label,'elements.query',args)
for n,(label,oid) in enumerate(jobs):
 r=c.wait(oid,30); (out/(label+'.json')).write_text(json.dumps(r,indent=2))
 if r['status']!='completed': print(label,r['status'],r.get('error'),flush=True)
 if n%50==0: print('Collected',n,'of',len(jobs),flush=True)
(out/'stage3_jobs.json').write_text(json.dumps(jobs,indent=2));print('DONE',len(jobs))

exec(open('output/trim_takeoffs_20261117/inventory.py',encoding='utf-8-sig').read().split('for i,d in enumerate(docs):')[0].replace("print(label,json.dumps(r),flush=True)","print(label,r['status'],r.get('error'),flush=True); return r"))
for i,d in enumerate(docs):
 prefix=['belmont','wieland'][i]
 for label,op,args in [('levels','elements.query',{'class':'Level','limit':500}),('phases','elements.query',{'class':'Phase','limit':500}),('revisions','elements.query',{'class':'Revision','limit':500}),('project_info','elements.query',{'class':'ProjectInfo','limit':10}),('links','links.query',{}),('base_named','elements.query',{'name_contains':'baseboard','limit':500}),('crown_named','elements.query',{'name_contains':'crown','limit':500}),('panel_named','elements.query',{'name_contains':'panel','limit':500}),('room_api','api.lookup',{'type':'Autodesk.Revit.DB.Architecture.Room'})]:
  query(d,prefix+'_'+label,op,args)
 if i==0:
  sweeps=json.loads((out/(prefix+'_sweeps.json')).read_text())['result']['items']
  for name in ['Baseboard','Codex Crown - selected 3in x 3-4in - 20261014']:
   e=next(e for e in sweeps if e['name']==name);query(d,prefix+'_sample_'+str(e['id']),'parameters.query',{'element':e['unique_id']});query(d,prefix+'_inspect_'+str(e['id']),'elements.inspect',{'element':e['unique_id'],'geometry':True})

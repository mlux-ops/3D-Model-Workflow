exec(open('output/trim_takeoffs_20261117/inventory.py',encoding='utf-8-sig').read().split('for i,d in enumerate(docs):')[0].replace("print(label,json.dumps(r),flush=True)","print(label,r['status'],r.get('error'),flush=True); return r"))
for label,oid in json.loads((out/'stage3_jobs.json').read_text()):
 f=out/(label+'.json');r=json.loads(f.read_text())
 if r['status']=='unknown_completion':
  rr=c.job(oid);f.write_text(json.dumps(rr,indent=2));print('RECONCILED',label,rr['status'])
for i,d in enumerate(docs):
 prefix=['belmont','wieland'][i]
 for cl in ['Sweep','Extrusion','Family']:
  query(d,prefix+'_'+cl.lower(),'elements.query',{'class':cl,'limit':500})
for id in [13053460,13681858]:query(docs[0],'belmont_profile_'+str(id),'parameters.query',{'element':str(id)})
for e in json.loads((out/'belmont_trim.json').read_text())['result']['items']:
 if e['category']=='Sheets':
  query(docs[0],'belmont_sheet_'+str(e['id']),'sheet.inspect',{'sheet':e['unique_id']})
  query(docs[0],'belmont_export_'+str(e['id']),'capture.export',{'view':e['unique_id'],'path_prefix':str((out/('sheet_'+str(e['id']))).resolve()),'pixels':3200})

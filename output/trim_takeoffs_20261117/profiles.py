exec(open('output/trim_takeoffs_20261117/inventory.py',encoding='utf-8-sig').read().split('for i,d in enumerate(docs):')[0].replace("print(label,json.dumps(r),flush=True)","print(label,r['status'],r.get('error'),flush=True); return r"))
for word in ['Baseboard','Selected 3in']:
 r=query(docs[0],'belmont_profile_types_'+word.split()[0],'elements.query',{'types':True,'name_contains':word,'limit':50})
 for e in (r.get('result') or {}).get('items',[]):
  if e['category']=='Profiles':query(docs[0],'belmont_verified_profile_'+str(e['id']),'parameters.query',{'element':e['unique_id']})

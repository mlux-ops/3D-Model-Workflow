exec(open('output/trim_takeoffs_20261117/inventory.py',encoding='utf-8-sig').read().split('for i,d in enumerate(docs):')[0].replace("print(label,json.dumps(r),flush=True)","print(label,r['status'],r.get('error'),flush=True); return r"))
for id in [13053460,13681858]:query(docs[0],'belmont_profile_resolved_'+str(id),'parameters.query',{'element':id})
for i,d in enumerate(docs):query(d,['belmont','wieland'][i]+'_final_context','context.query',{})

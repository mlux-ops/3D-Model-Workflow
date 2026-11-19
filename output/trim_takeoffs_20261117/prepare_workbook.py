
import json,collections,math
from pathlib import Path
p=Path('output/trim_takeoffs_20261117')
def read(n):return json.loads((p/(n+'.json')).read_text())
def params(n):return {x['name']:x for x in (read(n).get('result') or {}).get('instance',[])}
levels=read('belmont_levels')['result']['items']; level={x['id']:x for x in levels}
bands=sorted([(x['elevation'],x['name']) for x in levels if x['name'] in ['BASEMENT','1ST FLOOR','2ND FLOOR','3RD FLOOR','4TH FLOOR','T/ ROOF.']])
rows=[];tot=collections.defaultdict(float)
for e in read('belmont_sweeps')['result']['items']:
 if not(e['name']=='Baseboard' or 'Crown' in e['name']):continue
 r=read('belmont_params_'+str(e['id']));ps={x['name']:x for x in r['result']['instance']};tp={x['name']:x for x in r['result']['type']}
 cat='Baseboard' if e['name']=='Baseboard' else 'Crown'
 zlo=e['bounds']['min'][2];zhi=e['bounds']['max'][2]
 floor=next((name for z,name in reversed(bands) if zlo>=z-0.01),'Below basement')
 phase=ps['Phase Created']['formatted'];demo=ps['Phase Demolished']['formatted']
 qty=ps['Length']['value']
 row=[str(e['id']),cat,ps['Level']['formatted'],floor,'Unallocated',qty,zlo,zhi,tp['Profile']['formatted'],tp['Material']['formatted'],phase,demo,ps['Design Option']['formatted'],e['unique_id'],r['operation_id'],'Raw Length parameter; opening/void deductions NOT verified']
 rows.append(row);tot[cat]+=qty
rows.sort(key=lambda r:(r[1],r[6],int(r[0])))
summary={};summary['totals']=dict(tot);summary['counts']=dict(collections.Counter(x[1] for x in rows));summary['rows']=rows
summary['bands']=[(name, sum(r[5] for r in rows if r[1]=='Baseboard' and r[3]==name),sum(r[5] for r in rows if r[1]=='Crown' and r[3]==name)) for z,name in bands]
summary['models']=read('documents')['result']
summary['revisions']=[]
for proj in ['belmont','wieland']:
 for e in read(proj+'_revisions')['result']['items']:
  ps=params(proj+'_params_'+str(e['id']))
  summary['revisions'].append([proj,e['name'],ps.get('Revision Date',{}).get('value'),ps.get('Revision Description',{}).get('value'),'Not flagged issued' if not ps.get('Issued',{}).get('value') else 'Issued',str(e['id'])])
summary['preserved']=all(not read(proj+'_final_context')['result']['document']['is_modified'] for proj in ['belmont','wieland'])
summary['phase_counts']=dict(collections.Counter((r[10]+' / '+r[11]+' / '+r[12]) for r in rows))
(p/'workbook_data.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k not in ['rows','models','revisions']},indent=2))


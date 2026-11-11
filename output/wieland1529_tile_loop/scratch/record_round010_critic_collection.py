from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
s=json.loads((R/'state/ROUND010_SUBMISSION.json').read_text(encoding='utf-8'))
assert s['phase']=='2-board' and s['all_critic_scores'] is None
rooms=['PH-PRIMARY','PH-BATH2','PH-BATH4']
seats=['market','design','build','cost']
out={'round':10,'event':'12 original independently dispatched reports physically collected; formal rubric arithmetic and weighted score next distinct turn','source_receipt':'state/ROUND010_SUBMISSION.json','phase':'2-board','weighted_scoring_complete':False,'all_critic_scores':None,'report_files':{}}
for rid in rooms:
 out['report_files'][rid]={}
 for seat in seats:
  p=R/'rooms'/rid/'board/round-010'/('critic-'+seat+'.md')
  assert p.is_file() and p.stat().st_size>1000,(rid,seat)
  b=p.read_bytes()
  out['report_files'][rid][seat]={'file':str(p.relative_to(R)).replace('\\','/'),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
assert sum(map(len,out['report_files'].values()))==12
p=R/'state/ROUND010_CRITIC_COLLECTION.json'
assert not p.exists(),'Collection receipt already exists; do not silently overwrite'
p.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print('PASS 12 actual independent files fingerprinted, 3 rooms x 4 seats; original score NULL; next-turn weighted scoring only')

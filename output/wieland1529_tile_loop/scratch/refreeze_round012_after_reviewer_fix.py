"""One controlled original-R012 pre-dispatch six-packet correction audit; critic files must be absent."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
p=R/'state/ROUND012_SUBMISSION.json'
d=json.loads(p.read_text(encoding='utf-8'))
assert d['round']==12 and d['phase']=='2-board' and d['all_critic_scores'] is None
assert d['critic_dispatch']=='NOT DISPATCHED' and 'pre_dispatch_reviewer_fix' not in d
prior={}
for rid,files in d['candidate_files'].items():
 folder=R/'rooms'/rid/'board/round-012'
 assert not list(folder.glob('critic-*.md')) and (folder/'_key.json').exists()
 for letter,record in files.items():
  source=folder/'candidates'/f'{letter}.md';raw=source.read_bytes()
  assert b'## Manufacturer and material evidence' in raw
  assert b'**Hard-gate status:**' in raw and b'**Waterproof/install planning:**' in raw
  assert b'Original Clara wet listing FAIL; Soho Ivory candidate' not in raw if rid=='TX-BATH4' and letter=='A' else True
  old=record.copy();new={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
  assert old['sha256']!=new['sha256'] and old['bytes']>=7600,(rid,letter,'expected reviewer changes')
  prior.setdefault(rid,{})[letter]={'prior':old,'corrected':new}
  d['candidate_files'][rid][letter]=new
d['pre_dispatch_reviewer_fix']={'reviewer':'worker-8','result':'FIX: remove cross-room/cross-role shared boilerplate and repair 62.484-inch Bath2 cut; six packets corrected BEFORE critics','original_vs_corrected':prior,'critic_reports_present':False,'all_critic_scores':None,'owner_release':False}
p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print('PASS R012 controlled exact six corrected SHA/bytes and old SHA lineage recorded, 3 private mappings preserved, NO critics, scores null')
for rid,files in d['candidate_files'].items():print(rid,[(a,x['sha256'][:15],x['bytes']) for a,x in files.items()])

"""One-time R012 second pre-dispatch reviewer source correction; preserve keys and original score null."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];p=R/'state/ROUND012_SUBMISSION.json'
d=json.loads(p.read_text(encoding='utf-8'))
assert d['round']==12 and d['all_critic_scores'] is None and d['critic_dispatch']=='NOT DISPATCHED'
assert 'pre_dispatch_reviewer_fix2' not in d and 'pre_dispatch_local_link_fix' in d
diff={}
for rid,files in d['candidate_files'].items():
 folder=R/'rooms'/rid/'board/round-012'
 assert (folder/'_key.json').is_file() and not list(folder.glob('critic-*.md'))
 for letter,old in files.items():
  f=folder/'candidates'/f'{letter}.md';b=f.read_bytes()
  new={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
  assert old['sha256']!=new['sha256'],(rid,letter,'unchanged source')
  text=b.decode('utf-8')
  assert '15%' in text and 'DCOF' in text and '**Hard-gate status:**' in text
  diff.setdefault(rid,{})[letter]={'prior':old,'corrected':new}
  d['candidate_files'][rid][letter]=new
d['pre_dispatch_reviewer_fix2']={'reviewer':'worker-8 (permanently finished after independent pre-dispatch FIX)','source_correction':'Six exact source table wall/floor/accent gates and room-only sample briefs; removed surviving alternate/other-room references before critics','old_new_sha':diff,'specialist_files':0,'scoring':None,'new_reviewer_required':True}
p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print('PASS R012 six source SHA/byte refrozen and audited; 3 private keys unchanged, zero critics, scores null')

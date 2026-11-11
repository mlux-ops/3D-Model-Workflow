"""Final precise R012 pre-dispatch source-room text correction; preserve prior audits and keys."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];p=R/'state/ROUND012_SUBMISSION.json'
d=json.loads(p.read_text(encoding='utf-8'))
assert d['round']==12 and d['phase']=='2-board' and d['all_critic_scores'] is None and d['critic_dispatch']=='NOT DISPATCHED'
assert 'pre_dispatch_reviewer_fix2' in d and 'pre_dispatch_new_reviewer_fix' not in d
diff={}
for rid,files in d['candidate_files'].items():
 folder=R/'rooms'/rid/'board/round-012'
 assert (folder/'_key.json').exists() and not list(folder.glob('critic-*.md'))
 for letter,old in files.items():
  f=folder/'candidates'/f'{letter}.md';raw=f.read_bytes();t=raw.decode('utf-8')
  assert '15%' in t and '**Hard-gate status:**' in t and 'DCOF' in t
  new={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
  assert old['sha256']!=new['sha256'],(rid,letter,'expected source correction')
  diff.setdefault(rid,{})[letter]={'old':old,'new':new}
  d['candidate_files'][rid][letter]=new
d['pre_dispatch_new_reviewer_fix']={'reviewer':'worker-11 non-Pro','source_changes':'Six candidate-specific W geometry/tub-waste, wet niche/sample and owner-release text fixes, preserving private keys','prior_and_corrected_sha':diff,'critics_dispatched':False,'all_critic_scores':None}
p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print('PASS R012 six corrected source SHA re-frozen with prior SHA audit, 3 private keys untouched, 0 critics, scores null')

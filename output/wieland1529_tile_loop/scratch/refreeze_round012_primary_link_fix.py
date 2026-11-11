"""Second targeted R012 pre-dispatch controlled link correction; no critique may exist."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];p=R/'state/ROUND012_SUBMISSION.json'
d=json.loads(p.read_text(encoding='utf-8'))
assert d['all_critic_scores'] is None and d['critic_dispatch']=='NOT DISPATCHED'
assert 'pre_dispatch_reviewer_fix' in d and 'pre_dispatch_local_link_fix' not in d
folder=R/'rooms/TX-PRIMARY/board/round-012'
assert not list(folder.glob('critic-*.md'))
diff={}
for letter in ('B','C'):
 f=folder/'candidates'/f'{letter}.md';raw=f.read_bytes()
 assert b'](../../../plumbing.json)' in raw and b'](../../plumbing.json)' not in raw
 old=d['candidate_files']['TX-PRIMARY'][letter]
 new={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
 assert old['sha256']!=new['sha256']
 diff[letter]={'prior':old,'corrected':new}
 d['candidate_files']['TX-PRIMARY'][letter]=new
d['pre_dispatch_local_link_fix']={'reason':'Two primary source packet relative plumbing.md citations fixed prior to dispatch','audited_sha':diff,'critics_dispatched':False,'scores':None}
p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print('PASS controlled R012 source link SHA correction for 2 TX Primary files; other 4 SHA/private keys untouched')

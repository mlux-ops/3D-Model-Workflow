from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
p=R/'state/ROUND010_SUBMISSION.json'
d=json.loads(p.read_text(encoding='utf-8'))
assert d['all_critic_scores'] is None and d['phase']=='2-board'
for rid,cs in d['candidate_files'].items():
 assert not list((R/'rooms'/rid/'board/round-010').glob('critic-*.md'))
 for letter in cs:
  b=(R/'rooms'/rid/'board/round-010/candidates'/(letter+'.md')).read_bytes()
  cs[letter]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
d['pre_dispatch_fix']='Independent R010 reviewer FIX: historical-role headings neutralized, source floor and wall corrected, room-specific tub/linear/point drain and metal, dry powders N/A, WC inherited floor. Re-frozen BEFORE critic dispatch.'
p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print('PASS controlled refreeze six R010 SHA/bytes, zero critic files, scores null')

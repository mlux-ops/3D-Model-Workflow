from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[1]
rp=R/'state/ROUND009_SUBMISSION.json'
data=json.loads(rp.read_text(encoding='utf-8'))
assert data['all_critic_scores'] is None
for room,candidates in data['candidate_files'].items():
 for letter in candidates:
  f=R/'rooms'/room/'board/round-009/candidates'/(letter+'.md')
  b=f.read_bytes()
  candidates[letter]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
data['pre_dispatch_reviewer_fixed']='Removed shorthand R02 prior-critic leak, disallowed prior steam mention, generic tub/linear and other-room boilerplate; corrected individual tub Chrome/Matte White/Brizo fixtures; labeled excluded Primary niche rate/extension null and nonorderable. All six candidate SHA refreshed prior to first critic dispatch.'
rp.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print('PASS R009 reviewer FIX refreeze: six actual SHA/byte fingerprints, no scores, no critic files modified')

"""Fingerprint genuine R012 independent three-room/four-seat reports, without weighting scores."""
from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1]
sp=R/'state/ROUND012_SUBMISSION.json';dp=R/'state/ROUND012_CRITIC_DISPATCH.json'
s=json.loads(sp.read_text(encoding='utf-8'));d=json.loads(dp.read_text(encoding='utf-8'))
assert s['round']==d['round']==12 and s['all_critic_scores'] is d['all_critic_scores'] is None
assert s['phase']==d['phase']=='2-board' and d['scoring_deferred_to_next_distinct_turn']
assert d['source_submission_sha256']==hashlib.sha256(sp.read_bytes()).hexdigest()
result={'round':12,'phase':'2-board','event':'12 original independent blind reports collected for scoring in NEXT DISTINCT turn','source_submission_sha256':hashlib.sha256(sp.read_bytes()).hexdigest(),'source_dispatch_sha256':hashlib.sha256(dp.read_bytes()).hexdigest(),'critic_worker_seats':d['critic_worker_seats'],'all_critic_scores':None,'weighted_scoring_complete':False,'report_files':{},'local_links':0,'role_language_for_reviewer':[]}
for rid,candidates in s['candidate_files'].items():
 folder=R/'rooms'/rid/'board/round-012'
 for letter,src in candidates.items():
  raw=(folder/'candidates'/f'{letter}.md').read_bytes()
  assert src['sha256']==hashlib.sha256(raw).hexdigest() and src['bytes']==len(raw)
 result['report_files'][rid]={}
 for seat in ('market','design','build','cost'):
  p=folder/f'critic-{seat}.md';assert p.is_file() and p.stat().st_size>=1200,(rid,seat,'missing critic')
  b=p.read_bytes();t=b.decode('utf-8')
  assert all(k.lower() in t.lower() for k in ('top_fix','gate_flags','confidence'))
  assert not re.search(r'(?i)_key\.json|state/ROOMS\.json|state/LEDGER\.md',t),(rid,seat,'forbidden private file reference')
  # Natural-language denials such as 'no incumbent identification' are not
  # private key access; keep possible source-role wording for Reviewer judgment.
  flagged=[line[:320] for line in t.splitlines() if re.search(r'(?i)\bincumbent\b|\bchampion\b|historical source reference|\bsteam\b',line)]
  if flagged:result['role_language_for_reviewer'].append({'room':rid,'seat':seat,'text':flagged})
  for letter in candidates:
   assert re.search(r'(?im)^#{1,3}\s+candidate\s+'+letter+r'\b',t),(rid,seat,letter,'missing section')
  for link in re.findall(r'\]\(([^)]+)\)',t):
   if link.startswith(('https://','http://','#','mailto:')):continue
   assert (folder/link.split('#')[0]).exists(),(rid,seat,'broken link',link)
   result['local_links']+=1
  result['report_files'][rid][seat]={'file':str(p.relative_to(R)).replace('\\','/'),'worker':d['critic_worker_seats'][f'critic-{seat}'],'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
assert sum(map(len,result['report_files'].values()))==12
dst=R/'state/ROUND012_CRITIC_COLLECTION.json'
assert not dst.exists(),'Do not silently overwrite original critique collection'
dst.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('PASS R012 12 original reports SHA/byte fingerprinted;',result['local_links'],'local links; scores NULL deferred to distinct scoring turn')

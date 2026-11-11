"""After explicit independent Reviewer clearance, one-time R012 blind critic dispatch receipt."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
source=R/'state/ROUND012_SUBMISSION.json';d=json.loads(source.read_text(encoding='utf-8'))
out=R/'state/ROUND012_CRITIC_DISPATCH.json'
assert not out.exists()
assert d['round']==12 and d['phase']=='2-board' and d['all_critic_scores'] is None and d['critic_dispatch']=='NOT DISPATCHED'
assert d.get('pre_dispatch_reviewer_fix') and d.get('pre_dispatch_local_link_fix')
registry=R/'state/ROOMS.json';rooms=json.loads(registry.read_text(encoding='utf-8'))
for rid,files in d['candidate_files'].items():
 for letter,src in files.items():
  b=(R/'rooms'/rid/'board/round-012/candidates'/f'{letter}.md').read_bytes()
  assert hashlib.sha256(b).hexdigest()==src['sha256'] and len(b)==src['bytes']
 item=next(x for x in rooms['rooms'] if x['id']==rid)
 assert item['status']=='blocked' and item['champion_id'] is None and item['round_012_submission']['scores'] is None
 item['round_012_submission']['status']='reviewer_cleared_critics_dispatched_pending_scores'
 item['round_012_submission']['preflight_completed']=True
 item['round_012_submission']['reviewer_clearance']='worker-11 independent non-Pro DONE FOR R012 FOUR-SEAT DISPATCH after worker-8 source FIX'
data={'round':12,'phase':'2-board','as_of':'2026-11-06','source_submission':'state/ROUND012_SUBMISSION.json','source_submission_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidate_files':d['candidate_files'],'independent_reviewer':'worker-11','preflight':'DONE FOR R012 FOUR-SEAT DISPATCH','critic_worker_seats':{'critic-market':'worker-3','critic-design':'worker-9','critic-build':'worker-10','critic-cost':'worker-12'},'source_roles_unavailable_to_critics':True,'scoring_deferred_to_next_distinct_turn':True,'all_critic_scores':None,'owner_approved':False,'procurement_release':False}
out.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
registry.write_text(json.dumps(rooms,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS R012 four authentic assigned blind seats, 6 frozen SHA, all scores null; 3 blocked rooms unchanged; no release')

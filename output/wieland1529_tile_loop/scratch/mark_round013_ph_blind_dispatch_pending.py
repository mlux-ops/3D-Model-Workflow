"""One-time pending PH R013 room register, retaining all scored R010 decisions."""
from pathlib import Path
import json,hashlib

ROOT=Path(__file__).resolve().parents[1]
roomfile=ROOT/'state/ROOMS.json'
source=ROOT/'state/ROUND013_SUBMISSION.json'
dispatch=ROOT/'state/ROUND013_CRITIC_DISPATCH.json'
assert dispatch.exists()
sub=json.loads(source.read_text(encoding='utf-8'))
des=json.loads(dispatch.read_text(encoding='utf-8'))
assert des['source_submission_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
assert sub['all_critic_scores'] is None and des['all_critic_scores'] is None
b=roomfile.read_bytes()
rooms=json.loads(b)
assert len(rooms['rooms'])==13
assert b==(json.dumps(rooms,indent=2,ensure_ascii=False)+'\n').replace('\n','\r\n').encode('utf-8')
prev=hashlib.sha256(b).hexdigest()
for item in rooms['rooms']:
 rid=item['id']
 if rid not in sub['candidate_files']:
  continue
 assert item['last_round']==10 and item['status']=='blocked' and item['champion_id'] is None and item['champion_score'] is None
 assert 'board_round_013' not in item
 assert item['board_round_010']['status']=='blocked'
 item['last_round']=13
 item['board_round_013']={
  'round':13,'phase':'2-board','status':'pending_blind_four_seat_critic_reports_unscored',
  'source_submission_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
  'critic_dispatch_sha256':hashlib.sha256(dispatch.read_bytes()).hexdigest(),
  'candidate_source_sha256':sub['candidate_files'][rid],
  'seat_workers':des['critic_worker_seats'],
  'critic_files_complete':0,
  'all_critic_scores':None,'weighted_score':None,
  'previous_scored_round':10,'previous_scored_outcome':'blocked',
  'source_role_key_private':True,
  'gates':'exact maker SKU wet measured numeric FLOOR/PAN DCOF, actual verified 1529 model, current Chicago lot/price and signed owner holds',
  'owner_approved':False,'procurement_release':False,
 }
assert [x['id'] for x in rooms['rooms'] if x['last_round']==13]==list(sub['candidate_files'])
new=(json.dumps(rooms,indent=2,ensure_ascii=False)+'\n').replace('\n','\r\n').encode('utf-8')
roomfile.write_bytes(new)
evidence={
 'as_of':'2026-11-06','old_sha256':prev,
 'new_sha256':hashlib.sha256(new).hexdigest(),
 'updated_rooms':list(sub['candidate_files']),
 'prior_scored_R010_outcomes_retained':True,
 'critics_scoring_unscored_in_submission_turn':True,
 'unchanged_other_10_rooms':True,'owner_approved':False,'procurement_release':False,
}
receipt=ROOT/'state/ROUND013_ROOMS_PENDING_SYNC.json'
assert not receipt.exists()
receipt.write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS R013 PH pending dispatch 3/13 rooms, all prior scored R010 preserved; old/new ROOMS SHA',prev,evidence['new_sha256'])

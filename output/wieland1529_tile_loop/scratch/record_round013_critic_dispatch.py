"""One-time immutable PH R013 critic dispatch fingerprint; no scores, no critique edits."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
dest=root/'state/ROUND013_CRITIC_DISPATCH.json'
assert not dest.exists(), 'Never recreate authentic dispatch history'
source=root/'state/ROUND013_SUBMISSION.json'
data=json.loads(source.read_bytes())
source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert source_sha=='55836b04247b2286d9f5e4dca2160b05dd567a094d0f391f6aa25c13ad8235d9'
assert data['all_critic_scores'] is None and data['critic_dispatch']=='NOT DISPATCHED'
assert data['owner_approval'] is False and data['procurement_release'] is False
for rid,letters in data['candidate_files'].items():
 for letter,fp in letters.items():
  b=(root/f'rooms/{rid}/board/round-013/candidates/{letter}.md').read_bytes()
  assert hashlib.sha256(b).hexdigest()==fp['sha256'] and len(b)==fp['bytes']
critic_assign={
 'critic-market':'worker-13',
 'critic-design':'worker-9',
 'critic-build':'worker-10',
 'critic-cost':'worker-12',
}
assert len(set(critic_assign.values()))==4
for rid in data['candidate_files']:
 for seat in critic_assign:
  assert not (root/f'rooms/{rid}/board/round-013/{seat}.md').exists(),(rid,seat)
receipt={
 'as_of':'2026-11-06','round':13,'phase':'2-board','source_submission':'state/ROUND013_SUBMISSION.json',
 'source_submission_sha256':source_sha,
 'candidate_files':data['candidate_files'],
 'source_preflight_reviewer':'worker-11',
 'independent_preflight':'CONTINUE - DONE FOR R013 FOUR-SEAT BLIND CRITIC DISPATCH ONLY, not globally DONE',
 'original_preflight_reviewer_fix':'state/ROUND013_PREDISPATCH_REVIEWER_FIX1.json',
 'reviewer_verified_local_links':32,
 'critic_worker_seats':critic_assign,
 'reused_sleeping':['worker-9','worker-10','worker-12'],
 'replacement_market_reason':'Original market worker-3 permanently finished; no revival or duplicate reviewer',
 'four_authentic_seat_dispatch_messages_delivered':True,
 'source_roles_unavailable_to_critics':True,
 'original_source_receipt_score_fields_preserved_null':True,
 'scoring_deferred_to_next_distinct_prime_turn':True,
 'all_critic_scores':None,'weighted_scoring':None,
 'owner_approved':False,'procurement_release':False,
 'revit_1529_verified':False,
}
dest.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS R013 four authentic blind seats DISPATCHED, source SHA',source_sha,'receipt SHA',hashlib.sha256(dest.read_bytes()).hexdigest())

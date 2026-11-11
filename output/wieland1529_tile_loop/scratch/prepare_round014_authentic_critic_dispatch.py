"""After real standing Reviewer CONTINUE: preserve frozen R014, record four-seat dispatch, mark PH/TX Bath3 pending unscored."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
clear=R/'state/ROUND014_PREDISPATCH_REVIEWER_CLEARANCE.json'
source=R/'state/ROUND014_SUBMISSION.json'
dispatch=R/'state/ROUND014_CRITIC_DISPATCH.json'
roomsp=R/'state/ROOMS.json'
assert clear.exists(), 'No actual independent Reviewer CONTINUE receipt. Never dispatch yet.'
assert not dispatch.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads(clear.read_text(encoding='utf-8'))
s=json.loads(source.read_text(encoding='utf-8'))
assert c['standing_reviewer']=='worker-14' and c['verdict']=='CONTINUE'
assert c['source_submission_sha256']==sha(source)
assert c['scope']=='R014 two-Bath3 neutral blind pre-dispatch only; R16 separate owner package technical audit'
assert s['round']==14 and s['critic_dispatch']=='NOT DISPATCHED'
assert s['all_critic_scores'] is None and s['weighted_scoring'] is None
assert set(s['candidate_files'])=={'PH-BATH3','TX-BATH3'}
before=sha(roomsp)
rooms=json.loads(roomsp.read_text(encoding='utf-8'))
assert len(rooms['rooms'])==13
for rid in s['rooms']:
    r=next(v for v in rooms['rooms'] if v['id']==rid)
    assert r['status']=='blocked' and r['owner_status'] is None
    assert r['last_round']==11 and r['champion_id'] is None and r['champion_score'] is None
    assert 'board_round_014' not in r
    assert r['board_round_011']['status']=='blocked'
    room=R/'rooms'/rid/'board/round-014'
    assert not list(room.glob('critic-*.md'))
    for letter,rec in s['candidate_files'][rid].items():
        p=R/rec['file']
        assert sha(p)==rec['sha256'] and len(p.read_bytes())==rec['bytes']
    r['board_round_014']={
      'round':14,'phase':'2-board','status':'pending_four_authentic_blind_critic_reports_unscored',
      'source_submission_sha256':sha(source),'four_critic_scores':None,
      'weights':{'market':0.30,'design':0.25,'build':0.25,'cost':0.20},
      'source_previous_scored_round':11,'source_status_retained':'blocked',
      'owner_approved':False,'procurement_release':False,'selected_tub_or_walkin':None,
      'verified_1529_native_geometry':False}
    r['last_round']=14
    r['open_gaps']=list(dict.fromkeys(r.get('open_gaps',[])+[
       'R014: four authentic neutral maker-specific PH/TX Bath3 blind critiques pending; NO scoring/selection; owner tub-versus-walk-in unresolved, exact raw wet LEVEL and conditional POINT PAN DCOF missing, live native 1529 model not verified.']))
changed={rid:next(r for r in rooms['rooms'] if r['id']==rid)['board_round_014'] for rid in s['rooms']}
other={r['id']:r for r in rooms['rooms'] if r['id'] not in s['rooms']}
dp={
 'round':14,'as_of':'2026-11-06','phase':'2-board',
 'reviewer_clearance':'worker-14 CONTINUE on FIX2 source SHA and R16 relevant maker gate corrections',
 'reviewer_clearance_sha256':sha(clear),
 'source_submission_sha256':sha(source),
 'source_research_sha256':s.get('maker_research_sha256'),
 'room_ids':['PH-BATH3','TX-BATH3'],
 'worker_seats':{'critic-market':'worker-13','critic-design':'worker-9','critic-build':'worker-10','critic-cost':'worker-12'},
 'weights':{'market':.30,'design':.25,'build':.25,'cost':.20},
 'true_worker_reports_dispatched':True,
 'independent_reports_collected':False,
 'all_critic_scores':None,'weighted_scoring':None,
 'formal_weighted_scoring_only_next_distinct_prime_turn':True,
 'source_previous_scored_round_011_unchanged':True,
 'owner_approval':False,'procurement_release':False,'actual_1529_geometry_verified':False}
dispatch.write_text(json.dumps(dp,indent=2)+'\n',encoding='utf-8')
roomsp.write_text(json.dumps(rooms,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
receipt=R/'state/ROUND014_ROOMS_PENDING_SYNC.json'
assert not receipt.exists()
receipt.write_text(json.dumps({'round':14,'old_rooms_sha256':before,'new_rooms_sha256':sha(roomsp),'changed_only_two_rooms':list(changed),'old_scored_round011_preserved':True,'other_room_count_unchanged':11,'source_sha256':sha(source),'dispatch_sha256':sha(dispatch),'all_critic_scores':None,'owner_approval':False,'procurement_release':False},indent=2)+'\n',encoding='utf-8')
assert len([r for r in rooms['rooms'] if r['id'] in other])==11
print('PASS R014 four independent original workers dispatch receipt, 2 R014 pending room records, original R011 scored preserved, scores null')
print('SOURCE',sha(source),'DISPATCH',sha(dispatch),'ROOMS',sha(roomsp))

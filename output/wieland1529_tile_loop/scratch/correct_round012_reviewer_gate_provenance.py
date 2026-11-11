"""Precisely repair Reviewer's R012 scored source-vs-revised gate provenance FIX.
Does NOT alter critic/candidate/source/dispatch/collection; preserves all weights and outcomes.
Creates separate old/new SHA correction receipt, resynchronizes 13-room register and R12 signed release index.
"""
from pathlib import Path
import hashlib,json,csv
R=Path(__file__).resolve().parents[1]
scoredpath=R/'state/ROUND012_SCORING.json'
roompath=R/'state/ROOMS.json'
receiptpath=R/'state/ROUND012_POST_SCORE_REVIEWER_FIX.json'
r12dir=R/'deliverables/integrated-r12'
manifestpath=r12dir/'MANIFEST.json'
releasepath=r12dir/'R12_13_ROOM_OWNER_DECISION_TO_PURCHASABLE_RELEASE_REGISTER.csv'
assert not receiptpath.exists()
scored=json.loads(scoredpath.read_text(encoding='utf-8'))
rooms=json.loads(roompath.read_text(encoding='utf-8'))
manifest=json.loads(manifestpath.read_text(encoding='utf-8'))
assert len(rooms['rooms'])==13 and len(manifest['outputs'])==6
assert scored['verification']=={'frozen_candidates':6,'original_critics':12,'criteria':114,'recalculated_seat_means':24,'local_links':380,'valid':True}
oldsha=hashlib.sha256(scoredpath.read_bytes()).hexdigest()
oldcsvsha=hashlib.sha256(releasepath.read_bytes()).hexdigest()
oldmanifsha=hashlib.sha256(manifestpath.read_bytes()).hexdigest()
assert manifest['outputs'][releasepath.name]['sha256']==oldcsvsha
old_common='FAIL: exact manufacturer SKU/finish raw numeric measured wet DCOF on LEVEL bath floor absent; published Emser >=0.60 is only a lower bound, not an exact lab certificate.'
oldpan='FAIL: exact independently tested and slope-compatible LINEAR PAN mosaic wet DCOF absent; Daltile Prime RL21 brochure TARGET not raw test.'
oldinterface='HOLD: selected Brizo BT0734816-BNX 48-in Black Onyx LINEAR and separate BR73480 rough installation, 7–18mm frame versus nominal Prime 6.35mm mosaic finished build-up/liner and flood-tested section unverified.'
newfirst={
 'TX-PRIMARY': 'FAIL: original Cortar Clay Soft LEVEL exact manufacturer SKU/finish raw numeric measured wet DCOF certificate absent. No Emser alternative laboratory result transfers to this source floor.',
 'TX-BATH2':'FAIL: original Cortar Clay Soft LEVEL exact manufacturer SKU/finish raw numeric measured wet DCOF certificate absent. No Emser alternative laboratory result transfers to this source floor.',
 'TX-BATH4':'FAIL: original Cortar Bone Soft LEVEL exact manufacturer SKU/finish raw numeric measured wet DCOF certificate absent. No Emser alternative laboratory result transfers to this source floor.'
}
newrev='FAIL: revised Emser Capisco Trosa F08CAPITR1224M LEVEL tile published maker wet DCOF >=0.60 is only a lower bound, NOT the individual exact raw numerical laboratory result.'
new_hist_pan='FAIL: original Cortar Clay Anti-Slip 12x24 LINEAR PAN wet DCOF exact raw numerical manufacturer test absent; actual pan geometry/slope and compatibility unverified.'
new_hist_interface='HOLD: selected Brizo BT0734816-BNX 48-in Black Onyx LINEAR and separate BR73480 rough need original Clay Anti-Slip pan/liner/flood-tested shop section; Prime RL21 is NOT part of this historical option.'
new_rev_pan='FAIL: proposed separate Daltile Prime RL21 hex mosaic LINEAR PAN has brochure TARGET only, no exact product raw measured wet DCOF certificate.'
new_rev_interface='HOLD: revised proposed Prime RL21 nominal 6.35mm tile vs selected Brizo adjustable frame 7–18mm = 0.65mm nominal stack-up coordination, NOT proven incompatibility; require manufacturer-approved full carrier/setting/liner/rough/flood section.'
oldweights={}
for rid,rr in scored['room_results'].items():
 assert rr['status']=='blocked' and rr['champion_id'] is None and rr['owner_approved'] is False
 h=rr['historical_letter'];r=rr['revised_letter']
 for letter,first in ((h,newfirst[rid]),(r,newrev)):
  x=rr['candidates'][letter]
  oldweights[(rid,letter)]=(x['weighted_score'],x['minimum_critic_score'],x['individual_critic_scores'].copy(),x['frozen_candidate_sha256'])
  assert x['gate_reasons'][0]==old_common
  x['gate_reasons'][0]=first
  if rid=='TX-PRIMARY':
   assert x['gate_reasons'][1:3]==[oldpan,oldinterface]
   x['gate_reasons'][1:3]=[new_hist_pan,new_hist_interface] if letter==h else [new_rev_pan,new_rev_interface]
# Re-create only scored-origin room reports, not specialist-owned original critiques.
for rid,rr in scored['room_results'].items():
 h=rr['historical_letter'];rev=rr['revised_letter']
 a=rr['candidates'][h];b=rr['candidates'][rev]
 folder=R/'rooms'/rid
 report=folder/'board/round-012/ROUND_REPORT.md'
 old=report.read_text(encoding='utf-8')
 assert old.count('### Candidate ')==2
 intro=old.split('### Candidate ')[0]
 # preserve shared introduction, chart, scoring/margins and historical original-source footer
 footer=old.split('**Technical visual study only',1)[1]
 blocks=[]
 for letter in (h,rev):
  x=rr['candidates'][letter]
  blocks.append('### Candidate '+letter+' — '+x['role']+'\n\n'+'; '.join(x['gate_reasons'])+'\n\n')
 report.write_text(intro+''.join(blocks)+'**Technical visual study only'+footer,encoding='utf-8')
 # Champion's latest governing section contains only revised conditional reasons.
 champ=folder/'champion.md';ct=champ.read_text(encoding='utf-8')
 anchor='## Round012 governing scored board\n\n**BLOCKED.** '
 assert ct.count(anchor)==1
 prefix=ct.split(anchor)[0]
 champ.write_text(prefix+anchor+'; '.join(b['gate_reasons'])+'\n\nSee board/round-012/ROUND_REPORT.md.\n',encoding='utf-8')
 entry=next(x for x in rooms['rooms'] if x['id']==rid)
 assert entry['status']=='blocked' and entry['champion_id'] is None
 assert entry['round_012_submission']['scores']=={k:v['weighted_score'] for k,v in rr['candidates'].items()}
 entry['board_round_012']=rr
 entry['round_012_evidence_priority']='; '.join(b['gate_reasons'])
 entry['open_gaps']=list(dict.fromkeys(entry.get('open_gaps',[])+['R012 scored source-vs-revised product gate attribution corrected: original manufacturer Soft/AntiSlip tests held separately from revised Emser/Prime testing.']))
for rid,rr in scored['room_results'].items():
 for letter,x in rr['candidates'].items():
  assert oldweights[(rid,letter)]==(x['weighted_score'],x['minimum_critic_score'],x['individual_critic_scores'],x['frozen_candidate_sha256'])
 # all mathematical/decision conditions remain intact
 assert rr['challenger_acceptance_pass'] is False and rr['champion_id'] is None
scored['post_scoring_reviewer_source_fix']='Corrected 6 candidate-specific wet floor/pan test and frame interface gates in response to independent worker-11 precise FIX; arithmetic/blocked results unchanged. Separate signed old/new scored receipt.'
scoredpath.write_text(json.dumps(scored,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
roompath.write_text(json.dumps(rooms,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
# Synchronize only sixth signed R12 owner release register, keep five previous fingerprints unchanged.
with releasepath.open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f);fieldnames=reader.fieldnames;rows=list(reader)
assert len(rows)==13
for row in rows:
 if row['room'] not in scored['room_results']:continue
 rr=scored['room_results'][row['room']];h=rr['historical_letter'];r=rr['revised_letter']
 row['round012_scores_status']='SCORED BLOCKED: historic %s %.2f, revised %s %.2f, margin %+.2f; minimum revised %.1f; no gate-qualified champion'%(h,rr['candidates'][h]['weighted_score'],r,rr['candidates'][r]['weighted_score'],rr['challenger_margin'],rr['candidates'][r]['minimum_critic_score'])
 assert row['purchase_authorized']=='False' and row['room_signed_owner_approval']=='False'
with releasepath.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fieldnames);w.writeheader();w.writerows(rows)
manifest['outputs'][releasepath.name]={'sha256':hashlib.sha256(releasepath.read_bytes()).hexdigest(),'bytes':len(releasepath.read_bytes())}
manifest['round012_weighted_scoring_deferred']=False
manifest['round012_scoring_sha256']=hashlib.sha256(scoredpath.read_bytes()).hexdigest()
manifest['round012_post_score_reviewer_fix_receipt']='state/ROUND012_POST_SCORE_REVIEWER_FIX.json'
for filename,item in manifest['outputs'].items():
 file=r12dir/filename;raw=file.read_bytes()
 assert item['sha256']==hashlib.sha256(raw).hexdigest() and item['bytes']==len(raw)
manifestpath.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
receipt={'round':12,'as_of':'2026-11-06','reviewer':'worker-11','verdict':'FIX exact source-vs-revised product wet-test gate attribution','only_changed_scored_gate_provenance':True,
 'scoring_sha256_before':oldsha,'scoring_sha256_after':hashlib.sha256(scoredpath.read_bytes()).hexdigest(),
 'r12_sixth_output_sha256_before':oldcsvsha,'r12_sixth_output_sha256_after':hashlib.sha256(releasepath.read_bytes()).hexdigest(),
 'r12_manifest_sha256_before':oldmanifsha,'r12_manifest_sha256_after':hashlib.sha256(manifestpath.read_bytes()).hexdigest(),
 'source_candidates_or_critics_modified':False,'original_submission_dispatch_collection_modified':False,
 'all_weighted_scores_margins_and_blocked_decisions_preserved':True,'owner_approved':False,'procurement_release':False,
 'current_scorer_corrected':'scratch/score_round012.py'}
receiptpath.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS independently requested exact 6 R012 source/revised gate attribution FIX, 3 scored rooms, unchanged weighted results and original evidence. Scored old/new SHA audited; sixth R12 owner register & manifest correctly re-signed.')

"""Factual one-time existing independent Reviewer-14 R014 FIX2 CONTINUE receipt."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
out=R/'state/ROUND014_PREDISPATCH_REVIEWER_CLEARANCE.json'
assert not out.exists()
sub=R/'state/ROUND014_SUBMISSION.json'
maker=R/'research/products/R14_BATH3_MAKER_BRANCH_AND_POINT_PAN_20261106.md'
r16=R/'deliverables/integrated-r16/MANIFEST.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads(sub.read_text(encoding='utf-8'))
assert sha(sub)=='946b3eda0a097961e28e76823607fd7d52b82209156e5bb59cdeb9c36450c8ed'
assert sha(maker)=='52ce52ec97c0bbc4e01790fb80ffc655aad35a772b180910835fc6960cf3e982'
assert sha(r16)=='ace730571e3b51695c77d4e54270b6e177ebedf3c7d3e9b0e13b0be869320f41'
assert s['all_critic_scores'] is None and s['critic_dispatch']=='NOT DISPATCHED'
assert all(not list((R/'rooms'/rid/'board/round-014').glob('critic-*.md')) for rid in s['rooms'])
receipt={
 'round':14,'as_of':'2026-11-06','standing_reviewer':'worker-14',
 'verdict':'CONTINUE',
 'scope':'R014 two-Bath3 neutral blind pre-dispatch only; R16 separate owner package technical audit',
 'actual_independent_result':'Independent non-Pro worker-14 read-only CONTINUE SAME-R014 FIX2; four authentic critics may be dispatched, NOT scored in source submission turn. Separately R16 book exact narrow FIX required, does not block critic dispatch.',
 'source_submission_sha256':sha(sub),'source_research_sha256':sha(maker),
 'source_fix1_receipt_sha256':sha(R/'state/ROUND014_PREDISPATCH_REVIEWER_FIX1.json'),
 'source_fix2_receipt_sha256':sha(R/'state/ROUND014_R16_REVIEWER_FIX2.json'),
 'verified_frozen_candidates':4,'valid_local_candidate_links':32,'external_research_links':12,
 'original_source_per_copy':{'PH-BATH3':930.42,'TX-BATH3':958.88},
 'historic_15pct_source_gross_already_included':True,'owner_tub_or_walkin_selected':False,
 'ph_basin_selected':False,'native_1529_verified':False,
 'r16_current_manifest_sha256':sha(r16),
 'r16_owner_book_fix_open':"TX3 omit PH basin; PH/TX primaries 48in LINEAR only and no niche; PH4 square POINT only. Re-sign owner book and manifest, do not expose to blind critics.",
 'all_critic_scores':None,'weighted_scoring':None,
 'formal_scoring_only_distinct_next_prime_turn':True,
 'owner_approved':False,'procurement_release':False,'global_13_room_done':False}
out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print('PASS actual independent R014 pre-dispatch CONTINUE worker-14 SHA',sha(out),'no score/release')

"""One-time independent R013 collection and corrected R14 clearance receipt, no scoring."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
P=R/'state/ROUND013_COLLECTION_REVIEWER_CLEARANCE.json'
assert not P.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
src=R/'state/ROUND013_SUBMISSION.json'
dis=R/'state/ROUND013_CRITIC_DISPATCH.json'
col=R/'state/ROUND013_CRITIC_COLLECTION.json'
r14=R/'deliverables/integrated-r14/MANIFEST.json'
fix=R/'state/ROUND013_R14_REVIEWER_SOURCE_IDENTITY_FIX.json'
assert not (R/'state/ROUND013_SCORING.json').exists()
assert sha(src)=='55836b04247b2286d9f5e4dca2160b05dd567a094d0f391f6aa25c13ad8235d9'
assert sha(col)=='4f0bbc757bd4d71cd029ca452141b0c77bea91e848d3d6c9e4d02368e20ca172'
assert sha(r14)=='e7fcc86fa76e373e5d4663d25a3e7be65cc6616b6be98ba49da891116a1df4d2'
assert json.loads(fix.read_bytes())['manifest_after']['sha256']==sha(r14)
c=json.loads(col.read_bytes())
assert c['all_critic_scores'] is None and c['weighted_scoring'] is None
assert c['individual_criteria']==114 and c['independent_unweighted_arithmetic_means']==24 and c['local_links']==333
data={
 'as_of':'2026-11-06',
 'round':13,
 'standing_reviewer':'worker-14',
 'reviewer_succession_reason':'previous standing non-Pro worker-11 finished for good at chat context limit after giving exact R14 Emser identity FIX; one new non-Pro replacement continued same-round check',
 'verdict':'CONTINUE — SAME-ROUND R14 FIX accepted, R013 authentic collection cleared; formal private weighted scoring only next distinct prime turn; not 13-room global DONE',
 'reviewer_changes':'NONE; independent READ ONLY',
 'source_submission_sha256':sha(src),
 'critic_dispatch_sha256':sha(dis),
 'original_critic_collection_sha256':sha(col),
 'r14_corrected_manifest_sha256':sha(r14),
 'r14_exact_fix_receipt_sha256':sha(fix),
 'source_candidates_verified':6,
 'authentic_critics_verified':12,
 'individual_criterion_scores':114,
 'unweighted_arithmetic_means':24,
 'local_markdown_evidence_links':333,
 'source_private_keys_preserved':True,
 'scoring_genuinely_next_distinct_prime_turn_only':True,
 'all_critic_scores':None,
 'weighted_scores':None,
 'original_13_room_four_unit_material_only_usd':23572.44,
 'original_15pct_waste_already_in_gross':True,
 'owner_approval':False,'procurement_release':False,
 'global_program_done':False,
 'open_holds':['native 1529 identity (current native 1527)','exact per-SKU raw numeric measured wet LEVEL and PAN DCOF','maker individual wet permissions for relief and Caviar','Brizo selected rough/grate/point/linear waterproof sections','true room areas, niche/cut grids, tubs and thresholds','current Chicago lot/cartons/installed bid','owner programs, fixture selections, cap and signature']
}
P.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS independent worker-14 R013/R14 CONTINUE clearance receipt SHA',sha(P),'R013 score NULL, full program OPEN')

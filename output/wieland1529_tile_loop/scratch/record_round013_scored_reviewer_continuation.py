"""One-time standing non-Pro Reviewer CONTINUE after formal scored R013/R15 FIX."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
dest=R/'state/ROUND013_SCORING_REVIEWER_CLEARANCE.json'
assert not dest.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
score=R/'state/ROUND013_SCORING.json'
r15=R/'deliverables/integrated-r15/MANIFEST.json'
fix=R/'state/ROUND013_R15_REVIEWER_FLOOR_PAN_SOURCE_FIX.json'
scored=json.loads(score.read_bytes())
manifest=json.loads(r15.read_bytes())
f=json.loads(fix.read_bytes())
assert f['new_manifest']['sha256']==sha(r15)
assert sha(score)=='f48ddc1935ee2aca5d2d5e30e6c978f7112de424a405a63b4c7e98ff10c27624'
assert sha(r15)=='c491339ca86161853630929c4804a7cccdb26e0a4e9a4142ab022299d46194df'
assert scored['verification']['valid'] and scored['verification']['criteria']==114
assert scored['verification']['recalculated_seat_means']==24 and scored['verification']['local_links']==333
assert len(scored['room_results'])==3 and all(v['status']=='blocked' and v['champion_id'] is None for v in scored['room_results'].values())
assert not scored['owner_approval'] and not scored['procurement_release']
assert manifest['room_count']==13 and manifest['trade_actions']==65 and not manifest['owner_approval'] and not manifest['procurement_release']
receipt={
 'round':13,'as_of':'2026-11-06','standing_non_pro_reviewer':'worker-14',
 'verdict':'CONTINUE - SAME-R013 formal scored and R15 13 room floor-pan source correction independently accepted; whole 13 room objective OPEN not DONE',
 'reviewer_performed_writes':False,
 'source_submission_sha256':sha(R/'state/ROUND013_SUBMISSION.json'),
 'critic_dispatch_sha256':sha(R/'state/ROUND013_CRITIC_DISPATCH.json'),
 'critic_collection_sha256':sha(R/'state/ROUND013_CRITIC_COLLECTION.json'),
 'formal_scoring_sha256':sha(score),
 'r15_corrected_manifest_sha256':sha(r15),
 'r15_exact_source_fix_receipt_sha256':sha(fix),
 'source_candidates_frozen':6,'authentic_critic_reports':12,
 'criterion_values':114,'independent_unweighted_arithmetic_means':24,
 'valid_local_citation_links':333,
 'four_specialist_weights':{'market':0.30,'design':0.25,'build':0.25,'cost':0.20},
 'three_PH_outcomes':{
  rid:{'historical_score':v['candidates'][v['historical_letter']]['weighted_score'],
       'revised_score':v['candidates'][v['revised_letter']]['weighted_score'],
       'margin':v['challenger_margin'],
       'minimum_revised_critic':v['candidates'][v['revised_letter']]['minimum_critic_score'],
       'status':'blocked','champion_id':None}
  for rid,v in scored['room_results'].items()},
 'r15_signed_output_count':4,'r15_room_release_rows':13,'r15_trade_action_rows':65,
 'r15_fixed_floor_pan_rows':13,
 'historic_material_only_four_copies_usd':23572.44,
 'historic_source_sf_already_includes_15pct_waste_once':True,
 'verified_native_1529':False,'owner_approved':False,'procurement_release':False,
 'whole_13_room_objective_done':False,
 'next_coherent_board_research':'research/products/R14_POWDER_3_ROOM_DRAWING_GROSS_CUT_AND_RESALE_PREP_20261106.md; no R014 blind candidate source yet',
 'unresolved':['exact native 1529 model vs open 1527','maker per SKU exact raw numerical measured wet LEVEL and PAN DCOF','individual wet relief/Caviar/Opal listing','approved Brizo point/linear/tub flange membrane/rough/flood','PH Bath2 0.496in nominal tub fit','PH Bath4 35/27 floor and Soft/AntiSlip','owner two Bath3 tub/walk-in and three basin selections','real Chicago installed bids and carton stock','owner samples, room caps and procurement signature']
}
dest.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS independent reviewer-14 R013 scored/R15 corrected CONTINUE signed local receipt SHA',sha(dest),'whole objective OPEN')

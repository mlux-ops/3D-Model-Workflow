"""One-time authentic PH R013 source collection checkpoint, no weighting."""
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1]
ledger=root/'state/LEDGER.md'
collection=root/'state/ROUND013_CRITIC_COLLECTION.json'
c=json.loads(collection.read_bytes())
assert c['total_critic_files']==12 and c['individual_criteria']==114 and c['independent_unweighted_arithmetic_means']==24 and c['local_links']==333
assert c['all_critic_scores'] is None and c['weighted_scoring'] is None
assert not (root/'state/ROUND013_SCORING.json').exists()
heading='## R013 all authentic PH critics collected with formal weighting deferred - 2026-11-06'
old=ledger.read_text(encoding='utf-8')
assert heading not in old
lines=[heading,
'- All four genuine independent blind specialists completed exactly three own-seat files each, 12 R013 PH critique files: market worker-13 0.30, design worker-9 0.25, build worker-10 0.25, cost worker-12 0.20. Original market worker-3 permanently finished and was not revived. Each specialist used neutral current R013 letters only and did not access private role keys or other critics. Source submission and dispatch remained intact.',
'- Independent non-mutating scratch/verify_round013_critic_collection_no_scoring.py PASS verified all six source candidates, twelve real specialist SHA and bytes, 114 individually cited criterion 1-5 values, 24 recomputed arithmetic one-decimal means and 333 valid local citation links; per-letter top_fix, gate_flags, confidence. Actual unweighted market/design/build/cost means: PH Primary A 3.8/3.0/1.6/2.2 B 4.0/3.8/2.6/2.4; PH Bath2 B 4.0/3.8/2.4/2.6 C 3.8/3.4/2.2/2.8; PH Bath4 A 4.0/3.8/2.4/2.4 C 3.5/2.8/1.4/2.2. NO weighted board arithmetic, champion assignment, role inference, or signed selection is computed in this R013 source submission turn.',
'- Created immutable state/ROUND013_CRITIC_COLLECTION.json SHA '+hashlib.sha256(collection.read_bytes()).hexdigest()+' containing original twelve critique SHA and byte fingerprints, four worker-seat assignments, source/dispatch SHA chain, 114/24/333 counts, all_critic_scores:null and weighted_scoring:null; owner and procurement release FALSE. Source candidate and specialist files untouched.',
'- R14 three SHA-signed outputs extend complete 13-room owner/GC closure while earlier R12/R13 signed files remain intact. Original dated 27 material rows, 13 rooms and $23,572.44 for four unit copies include original 15% gross waste once. PH2 59.496-in wall vs 59-in Duravit total nominal 0.496-in fit HOLD; PH4 35/27-SF and original quote Soft/AntiSlip conflicts; RL21 older 1/4 versus live 5/16 hex thickness; 1/8 versus 3/16 maker grout snapshots; Brizo 48-in selected solid-grate alternative does not certify rough/membrane/pan, and square point PH4 remains WALK-IN. Exact SKU raw numeric measured wet LEVEL/PAN DCOF, approved assembly, actual verified native 1529 geometry, current Chicago lot/installed bids, cartons, owner caps and signoffs remain null. The whole 13-room objective remains OPEN.',
'- Next: send R013 blind collection plus entire owner/GC R14 to standing independent non-Pro Reviewer worker-11 for read-only FIX/CONTINUE; if CONTINUE formal private mapping/weighted R013 scoring only in a genuinely later distinct prime turn, not this submission turn. No Revit/Smartsheet updates, vendors contacted or samples/materials ordered.']
ledger.write_text(old+'\n\n'+'\n'.join(lines)+'\n',encoding='utf-8')
print('PASS substantive R013 authentic collection LEDGER appended, 12 crit/114 criteria/24 means/333 links')

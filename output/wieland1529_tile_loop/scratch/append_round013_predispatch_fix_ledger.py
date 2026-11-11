"""One-time substantive independent pre-dispatch FIX/refreeze ledger checkpoint."""
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1]
ledger=root/'state/LEDGER.md'
f=json.loads((root/'state/ROUND013_PREDISPATCH_REVIEWER_FIX1.json').read_text(encoding='utf-8'))
sub=(root/'state/ROUND013_SUBMISSION.json')
assert hashlib.sha256(sub.read_bytes()).hexdigest()==f['submission_sha256_after']
assert json.loads(sub.read_bytes())['all_critic_scores'] is None
heading='## R013 Penthouse independent blind pre-dispatch FIX1 - 2026-11-06'
old=ledger.read_text(encoding='utf-8')
assert heading not in old
entry='\n\n'+heading+'\n'
entry+='- Independent standing non-Pro Reviewer worker-11 delivered **FIX** on original 6-candidate R013 PH source submission (SHA '+f['submission_sha256_before']+'), without changing scored R010/R012, issuing a critic dispatch, scoring, or approving purchase. Reviewer independently confirmed source fingerprints, local citations and main plumbing programs, but identified five precise room-specific pre-dispatch defects.\n'
entry+='- Prime executed one-time `scratch/correct_round013_predispatch_fix1.py` PASS; all six PH frozen neutral candidate SHA/bytes re-signed into current `state/ROUND013_SUBMISSION.json` SHA '+f['submission_sha256_after']+' and exact old/new audit `state/ROUND013_PREDISPATCH_REVIEWER_FIX1.json`. Only source candidates and their own submission/receipt changed; private role keys identical; scores remain NULL, four critics NOT DISPATCHED and no owner/vendor actions occurred. Updated all Bath2/Bath4 candidate-specific historic INCLUDED niche source gross 3.67 / 8.63 SF vs false PH Primary exclusion, face-displacement/back/returns/sill net once; Bath2 TUB NO PAN/Bath4 40.2 gross combined LEVEL+POINT PAN. Removed Bath2 prior-round/Glazzio role hint; corrected Daltile Prime RL21 1/8-in maker grout recommendation (instead of 3/16) in PH Primary/Bath2 proposed options; replaced Bath4 point-drain reference to linear-only maker sheet with individual RL21 point shower-floor application; added both Bath2 options nominal 59.496-in tub W1 vs 59-in Duravit tub, **0.496-in TOTAL nominal fit clearance**, subject to actual finishes/flange/tolerance and identity-correct 1529 model, no asserted compatibility.\n'
entry+='- Focused `scratch/verify_round013_ph_source_preflight.py` read-only PASS all six source-specific neutral packets, mandatory heading/line3, same five-column maker/cost/gate tables, **32 valid local links**, no detectable role terms, zero pre-dispatch critic files, source counts and original 15%-inclusive quotes unchanged. Standing Reviewer sent same-round five-section FIX1 correction report and requested exact independent FIX/CONTINUE before critic dispatch. No change to signed R12/R13 owner packages, original $23,572.44 material-only four-unit total, raw individual measured wet DCOF FAIL, actual 1529 model unavailable, or owner approvals/releases.\n'
ledger.write_text(old+entry,encoding='utf-8')
print('PASS auditable R013 five-finding FIX1 refreeze LEDGER update')

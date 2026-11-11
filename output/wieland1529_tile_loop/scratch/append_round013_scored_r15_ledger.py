"""One-time R013 successor-turn score + R15 entire-program owner/GC ledger checkpoint."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
ledger=R/'state/LEDGER.md'
scored=R/'state/ROUND013_SCORING.json'
m=R/'deliverables/integrated-r15/MANIFEST.json'
s=json.loads(scored.read_text(encoding='utf-8'))
mm=json.loads(m.read_text(encoding='utf-8'))
assert s['verification']=={
  'frozen_candidates':6,'original_critics':12,'criteria':114,
  'recalculated_seat_means':24,'local_links':333,'valid':True}
assert mm['room_count']==13 and mm['trade_actions']==65
assert mm['original_four_unit_material_only_usd']==23572.44
assert not mm['owner_approval'] and not mm['procurement_release']
assert mm['r013_scoring_sha256']==hashlib.sha256(scored.read_bytes()).hexdigest()
rooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
assert len(rooms)==13
for rid,r in s['room_results'].items():
    x=next(v for v in rooms if v['id']==rid)
    assert x['board_round_013']==r and x['status']=='blocked' and x['champion_id'] is None
heading='## Round013 formal next-distinct-turn PH scoring plus complete R15 all-room owner/GC advancement - 2026-11-06'
old=ledger.read_text(encoding='utf-8')
assert heading not in old
lines=[heading,
'- Following last separate R013 source-submission/collection-only prime turn (at 19:04 UTC), user explicitly resumed this genuinely new prime turn. First agents action=status confirmed all four independent critics complete and standing non-Pro worker-14 previously CONTINUE. Re-read OWNER_FEEDBACK.md, ROOMS.json, most recent full LEDGER and BOARD.md. Re-ran read-only scratch/verify_round013_critic_collection_no_scoring.py PASS 6 frozen candidates, 12 original independent critic SHA/bytes (market worker-13, design worker-9, build worker-10, cost worker-12), 114 individual 1-5 criteria, 24 reported arithmetic one-decimal means and 333 local evidence links. No stale last-turn resume work rerun or duplicate critics.',
'- New one-time scratch/score_round013_distinct_turn.py succeeded and produced separate state/ROUND013_SCORING.json SHA '+hashlib.sha256(scored.read_bytes()).hexdigest()+'. Rechecked original source/dispatch/collection SHA chain, exact 6 candidate and 12 independent critic fingerprints, 114 actual criterion values/24 printed means/333 links, private historical/revised mappings opened only AFTER authentic four-seat collection and worker-14 CONTINUE, exact Decimal market .30 / design .25 / build .25 / cost .20 and board gates of >=+.25 weighted and ALL specialist seats >=3.0 plus every wet/technical hard gate. Original submission/dispatch/collection retain all_critic_scores:null and no files in those old source folders were modified.',
'- PH-PRIMARY historical A 2.73, revised B 3.28, +0.55 (margin PASS), revised build 2.6 and cost 2.4 (<3 FAIL), exact maker raw numerical wet bath LEVEL/shared WC and separate 48-in LINEAR PAN DCOF FAIL. Source Reed wet WALL unlisted; proposed flat Bone wet PASS; Brizo selected Black Onyx BT0734816-BNX and BR73480 factory solid grate avoids tile-in insert thickness alone, not approved membrane/rough/sloped PAN. **BLOCKED**, no champion.',
'- PH-BATH2 historical C 3.10, revised B 3.27, +0.17 (margin FAIL), revised build 2.4/cost 2.6 (<3 FAIL), exact individual LEVEL wet DCOF FAIL. Individually wet-listed Sapphire/Sandstone tub walls remain PASS and selected actual Duravit 59-in/Hansgrohe Matte White TUB (NO tiled PAN) unchanged. Source wall W1 59.496-in versus nominal tub 59-in gives only 0.496-in TOTAL nominal fit difference before actual rough/flange/finishes and model verification. **BLOCKED**, no champion.',
'- PH-BATH4 historical C 2.54, revised A 3.23, +0.69 (margin PASS), revised build 2.4/cost 2.4 (<3 FAIL), separate exact LEVEL and square POINT PAN numeric wet DCOF FAIL. Selected Brizo Black Onyx BT062415-BNX 4-in SQUARE POINT actual WALK-IN (NOT tub) retained. Historical full 107.2-SF/unit Bone Ribbed wet WALL and Clara Caviar wet NICHE unlisted; revised maker-listed flat Bone/Soho Black design conditional. Owner 35-SF versus drawing 27-SF floor, source Soft-versus-AntiSlip mismatch, historical two-unit 214.4-SF vendor grand-total discrepancy remain unapproved quote audit only. **BLOCKED**, no champion.',
'- One-time scratch/apply_round013_scored_decisions.py PASS wrote exactly three PH Round013 ROUND_REPORT.md, current champion.md and history.md appendices, synchronized all 13 state/ROOMS.json with three scored R013 BLOCKED records while preserving entire R010 scored histories and all other 10 room statuses; original owner approvals/null, all procurement releases false. All historical source gross already include 15% waste ONCE; no duplicate shared WCs, unselected Primary niches, niche field face/returns, PAN/LEVEL alternate net, samples/trim.',
'- Substantive new additive four-output signed owner/GC R15 package in deliverables/integrated-r15/ created by scratch/build_r15_scored_owner_gc.py: room-by-room score + evidence construction/owner decision book, 13-row scored owner-to-release register, refreshed 65 independent trade-owned exact evidence closure rows and concise START_HERE. Read-only independent QA PASS all four output SHA/bytes and MANIFEST SHA '+hashlib.sha256(m.read_bytes()).hexdigest()+', 13 unique rooms, 65 actions, original 27 2026-09-03 material rows and material-only two PH/two TX copies total $23,572.44 with original 15% gross waste embedded exactly once, owner/GC release FALSE. Signed R12/R13/R14 previous outputs untouched; R15 is an additive owner/GC technical closure bridge, not a new supplier order or contractor cost.',
'- Critical open evidence: correct native 1529 Revit identity not verified (open model title 1527), exact SKU/finish independent raw numerical measured wet LEVEL/PAN DCOF, manufacturer individual relief/Caviar/Opal wet approvals, Brizo chosen rough/liner/drain/slope/flood and tub flange physical sections, true surveyed wall/niche/LEVEL/PAN areas and cartons, current Chicago available lot/lead/landed installed bids, owner material room caps and signed selections. PH Bath3/TX Bath3 tub-versus-walk-in and PH Bath3/TX Bath2/TX Powder2 basins remain owner-controlled UNSELECTED. No Revit/Smartsheet writes, vendors contacted, emails/forms, sample orders or purchases. Global entire thirteen-room design/procurement objective OPEN.',
'- Sent required five-section ≤4000-character R013 scored ROUND REPORT to standing non-Pro worker-14, plus additional 13-room signed R15 supplement for independent read-only audit. Await actual precise FIX or CONTINUE before claiming independent scored clearance; on CONTINUE continue meaningful next coherent board/research, never global DONE without explicit whole-program Reviewer declaration.']
ledger.write_text(old+'\n\n'+'\n'.join(lines)+'\n',encoding='utf-8')
print('PASS substantial R013 scored / R15 integrated thirteen-room auditable LEDGER entry appended')

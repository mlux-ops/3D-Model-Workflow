"""Add concise R025 dispatch and separate R026 prepared evidence to project histories."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
rounds={
 'PH-PRIMARY':('R025 formal blind SOURCE-FROZEN and four-seat dispatch','Flat Cortar Bone, no niche; two LFT LEVEL/LINEAR PAN schemes; factory BNX 48in LINEAR + BR73480 rough and PH-WC inherit once.'),
 'PH-BATH3':('R025 formal blind SOURCE-FROZEN and four-seat dispatch','Sapphire or Copper wet WALL with independently wet Sandstone niche; TUB/WALK-IN and basin unselected, Delta Chrome POINT PAN only WALK-IN.'),
 'PH-BATH4':('R025 formal blind SOURCE-FROZEN and four-seat dispatch','Flat Bone wet WALL, independent Sandstone/Copper niche; 24in+ LEVEL and four-plane POINT PAN; Brizo BNX selected WALK-IN retained.'),
 'TX-PRIMARY':('R026 distinct TX source-only alternatives PREPARED','Flat Clay/Riviera 24x48 LINEAR PAN versus controlled Copper-glazed wall accent/Luxe 24x24; BNX LINEAR/rough/no niches/TX-WC once.'),
 'TX-BATH3':('R026 distinct TX source-only alternatives PREPARED','Wet-listed Soho Emerald/Riviera versus quoted Tones Copper/Luxe, Sandstone wet niche; Brizo BNX POINT only with owner WALK-IN, tub remains undecided.')
}
for rid,(title,detail) in rounds.items():
 p=R/'rooms'/rid/'history.md'
 old=p.read_text(encoding='utf8')
 assert title not in old
 tail=(f'\n## {title} — 2026-11-07\n'
       f'- {detail}\n'
       '- Source item-specific Elm WALL/NICHE listings and F&D exact 24in+ LEVEL and conditional shower PAN published wet DCOF >=0.42 documented, but Chicago matching lot, full delivered budget and native element/door/drain cuts remain UNKNOWN.\n'
       '- R025 Reviewer22 permitted authentic independent blind DISPATCH only; source frozen 6/6, private roles segregated. R026 remains separately PREPARED, not frozen/reviewed/dispatched. No score, champion, owner approval, samples or orders.\n')
 p.write_text(old.rstrip()+'\n'+tail,encoding='utf8',newline='\n')
ledger=R/'state/LEDGER.md'
previous=ledger.read_text(encoding='utf8')
entries=[
'''## R025 formally frozen PH source, independent reviewer22 CONTINUE and four fresh critics dispatched — 2026-11-07
- Recovered verified R024 12/12 genuine critics and Reviewer21 FIX1 CONTINUE; no accepted champion because full delivered budget and native geometry UNKNOWN, certain COST seat scores <3.0; no redispatch of R024.
- Source-froze byte-identical corrected PH-PRIMARY/PH-BATH3/PH-BATH4 R025 six neutral A/B and three prime-only private _keys; 6/6 frozen SHA/bytes, 4/4 ancestor receipts and 3/3 private SHA PASS.
- Authentic independent worker22 CONTINUE for BLIND DISPATCH only, not scoring/approval; retained selected Primary BNX 48in LINEAR/BR73480 no niches and PH-WC once, PH4 BNX POINT WALK-IN, PH3 basin and TUB/WALK-IN owner undecided.
- Dispatched four fresh, strictly blinded independent seats MARKET worker23 (.30), DESIGN worker24 (.25), BUILD worker25 (.25), COST worker26 (.20), run 0a72848e-6cb2-462d-9478-1eccba986835; no private maps/prior critics/histories/ROOMS/LEDGER to specialists.
- Phase 2-board; next DISTINCT prime turn collect four reports, then hard gates and weighted scoring. Current geometry native cut, complete delivered budget/125% and Chicago stock/lot UNKNOWN; no score/champion/owner release in this turn.
''',
'''## R026 next TX wet-bath selection PREPARED, separate from R025 board — 2026-11-07
- New additive TX-PRIMARY/TX-BATH3 future cohort: two differentiated neutral options per blocked room, with source-specific Elm wet WALL/NICHE and exact F&D 24in+ LEVEL and conditional LINEAR/POINT PAN published wet DCOF>=0.42.
- Same-job Sep-04-2026 Elm flat Clay $8.14/SF, Tones Copper/Sandstone $6.95/SF; unquoted Soho Emerald NULL, F&D Luxe $3.49/Riviera $3.99-$4.39 retail non-Chicago; three product alternatives per surface documented, unsupported Porcelanosa floor excluded.
- TX Primary BNX 48in LINEAR+BR73480/no niches/TX-WC inherited; TX Bath3 BNX POINT only if owner WALK-IN, otherwise TUB program undecided. No made-up net PAN, geometry, lot, quote or owner selection.
- Seven add-on research/candidate/owner source files signed with three parent receipts in state/ROUND026_TX_FOUR_SCHEMES_TWO_OWNER_CARDS_SIGNED.json; not source-frozen, preflighted, dispatched or scored.
- All 13 identities/26 instances/27 historical material rows/$23,572.44 and 15% source waste once preserved; no Revit/Smartsheet changes, vendor contact, emails, samples, orders or Git.
''']
for e in entries:
 assert len(e.rstrip().splitlines())<=15 and e.splitlines()[0] not in previous
ledger.write_text(previous.rstrip()+'\n\n'+'\n'.join(e.rstrip() for e in entries)+'\n',encoding='utf8',newline='\n')
print('Room histories 5 updated, R025/R026 ledger entries',*[len(e.rstrip().splitlines()) for e in entries],'lines')

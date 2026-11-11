"""Append two <=15-line source-only/formal ledger entries once."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
P=R/"state/LEDGER.md"
source=P.read_text(encoding="utf8")
blocks=[
"""## R024 collected four original-role replacement critics, formal score/gate HOLD — 2026-11-07
- Authenticated worker17 MARKET/.30, worker18 DESIGN/.25, worker19 BUILD/.25, worker20 COST/.20 all finished 3 individual source-blind critic files each: 12/12 authentic reports, evidence criterion-level arithmetic PASS.
- Independent preflight Reviewer worker16 CONTINUE authorized DISPATCH only, not champion/score clearance; R024 6/6 SHA and predecessor signed source hashes unchanged.
- Prime weighted: PH-BATH2 A3.73 min3.4/B3.29 min2.0 FAIL; TX-BATH2 A3.59 min3.2/B3.19 min2.0 FAIL; TX-BATH4 A3.44 min2.2 FAIL/B2.99 min2.0 FAIL.
- Manufacturer exact Elm wet WALL/NICHE and F&D wet >=0.42 LEVEL listing PASS, all three selected Duravit TUB with PAN N/A; no source hard gate fabricated.
- Full delivered 125%-budget, carton trim/freight, native door/tub/niche focal cuts, Chicago exact stock/ETA UNKNOWN: NO new hard-gate compliant champion, all statuses unchanged; 8 blocked/3 active/2 seeded.
- Signed state/ROUND024_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json 12 critic hashes; cost-seat minimum fails all B and both TX Bath4; independent formal Reviewer worker21 requested.
""",
"""## R025 next PH blocked-room 3-cohort and 13 provisional owner decision briefs — 2026-11-07
- R025 PH-PRIMARY/PH-BATH3/PH-BATH4 six distinct neutral two-per-room tile schemes plus one manufacturer evidence file PREPARED only, not formal source-submitted or scored while R024 collection is resolved.
- Each uses exact Elm wet-listed flat Cortar/Tones WALL, separate wet NICHE or NO Primary niche, and F&D exact 24in+ SKU LEVEL and independently wet >=0.42 applicable LINEAR/POINT PAN, with 2026-09-04 same-job Elm quote and current public non-Chicago F&D prices.
- Retains Primary BNX 48in LINEAR/BR73480 rough/solid grate/no niche/PH-WC floor once; PH4 owner WALK-IN BNX four-inch POINT; PH3 TUB/WALK-IN and basin owner-UNSELECTED, Delta Chrome POINT conditional only.
- 7/7 R025 source SHA+bytes and four immutable parent receipt SHA; no old signed work regenerated, no Emser/Daltile/Platform supplier choices.
- All 13 revised one-page owner cards in deliverables/r025-13-owner-tiles-PROVISIONAL signed 13/13; costs, source surfaces, plumbing, OT01 photo-supported powder layering, OT05 unverified bathroom visual and owner-only decisions explicit, none final.
- Original 13 rooms/26 copies/27 source rows/$23,572.44 material-only, 15% original waste ONCE unchanged. Native Revit job b215004b-3b0b-4c31-8541-fa049b22b9c0 queued, inspected without resubmission; PROJECT_MEMORY error logged, no fabricated dimensions.
- Full 13-room objective OPEN; all releases FALSE and no email/vendor contact/orders/samples/installer engineering/Git actions.
"""
]
assert all(len(b.rstrip().splitlines())<=15 for b in blocks)
for block in blocks:assert block.splitlines()[0] not in source
P.write_text(source.rstrip()+"\n\n"+"\n".join(b.rstrip() for b in blocks)+"\n",encoding="utf8",newline="\n")
print("R024/R025 ledger entries appended, line counts",*[len(b.rstrip().splitlines()) for b in blocks])

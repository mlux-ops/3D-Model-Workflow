"""Document authenticated R024 results and R025 PH evidence, not a champion promotion."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
round24=json.loads((R/"state/ROUND024_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json").read_text(encoding="utf8"))
for rid in ("PH-BATH2","TX-BATH2","TX-BATH4"):
 z=round24["rooms"][rid]["candidates"]
 note=f"""\n## R024 completed four-seat blind scoring; hard-gate BLOCK (2026-11-07)

- Four genuine original-role replacement critics: MARKET worker17 0.30, DESIGN worker18 0.25, BUILD worker19 0.25, COST worker20 0.20. Source SHA, arithmetic, criteria and report collection independently checked in state/ROUND024_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json; independent pre-dispatch Reviewer worker16 CONTINUE was **dispatch-only**.
- Neutral A weighted {z['A']['weighted_arithmetic']:.2f}, minimum individual specialist {z['A']['seat_minimum']:.1f}; neutral B weighted {z['B']['weighted_arithmetic']:.2f}, minimum {z['B']['seat_minimum']:.1f}. For B, at least one COST score is below 3.0 and the mandatory 3.0 minimum is **FAIL**. {('A also fails min seat because COST=2.2; ' if rid=='TX-BATH4' else 'A passes individual minimum only; ')}all options fail complete acceptance because native geometry and full delivered 125% material-price gate remain **UNKNOWN**, with Chicago matching lots/ETA unknown. There was NO previous formal same-round incumbent to replace; +0.25 challenger rule is not a substitute for gate acceptance.
- All three source programs are selected Duravit TUBS with NO tiled shower PAN; exact F&D LEVEL SKU wet DCOF >=0.42 public listing and exact Elm wet WALL/NICHE listing documented. Current manufacturer page listing ≠ confirmed Chicago stock or live native room cuts. Original fixtures/finishes and owner-held basin/compatibility choices unchanged. No champion elected, no owner/fabrication/purchase approval.
"""
 p=R/"rooms"/rid/"history.md"
 s=p.read_text(encoding="utf8")
 assert "## R024 completed four-seat blind scoring; hard-gate BLOCK" not in s
 p.write_text(s.rstrip()+"\n"+note,encoding="utf8",newline="\n")

for rid in ("PH-PRIMARY","PH-BATH3","PH-BATH4"):
 note=f"""\n## R025 permitted-vendor PH source-only selection round PREPARED (2026-11-07)

- Two fresh neutral alternatives at rooms/{rid}/board/round-025/prepared/candidates/A.md and B.md; SHA and immutable parent receipts in state/ROUND025_PH_THREE_ROOM_PREPARED_NOT_SUBMITTED.json, not formally source-frozen or reviewed. Exact Elm Tones/flat Cortar individual wet WALL, independent Tones NICHE where applicable, and exact Floor & Decor 24x24/24x48 published wet DCOF >=0.42 LEVEL and conditional independent PAN. 2026-09-04 Elm same-job $6.95/SF Tones and $8.14/SF flat Cortar, floor site retail variable, no double historical 15%-gross waste.
- Original Brizo 48in LINEAR/BR73480 rough/no Primary niche/inherited PH-WC, selected PH Bath4 BNX four-inch POINT WALK-IN, and PH Bath3 UNSELECTED TUB/WALK-IN/Delta POINT conditional branch with basin unselected remain authoritative. Native element-specific room/pan lengths, Chicago dye lot/current delivery and complete budget remain unresolved, so neither source option passes full formal hard gates or earns champion.
"""
 p=R/"rooms"/rid/"history.md"
 s=p.read_text(encoding="utf8")
 assert "## R025 permitted-vendor PH source-only selection round PREPARED" not in s
 p.write_text(s.rstrip()+"\n"+note,encoding="utf8",newline="\n")
print("R024/R025 selection histories updated: 6 rooms, zero champions changed")

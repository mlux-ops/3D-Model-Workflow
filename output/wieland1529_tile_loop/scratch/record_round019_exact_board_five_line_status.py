"""One-time exact board/BOARD.md 5-line STATUS snapshot and SHA-audited ledger."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];S=R/"state"
P=S/"ROUND019_FIVE_LINE_STATUS.txt";L=S/"LEDGER.md"
assert not P.exists()
HEADER="## R019 exact five-line source-governed board STATUS after additive manufacturer research — 2026-11-06"
assert HEADER not in L.read_text(encoding="utf-8")
rooms=json.loads((S/"ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert len(rooms)==13
seen=[r["id"] for r in rooms]
want=["PH-PRIMARY","PH-BATH2","PH-BATH3","PH-BATH4","PH-POWDER","PH-WC","TX-PRIMARY","TX-BATH2","TX-BATH3","TX-BATH4","TX-POWDER","TX-POWDER2","TX-WC"]
assert seen==want
parts=[]
for r in rooms:
 champion=r["champion_id"] if r["champion_id"] else "null"
 score=("null" if r["champion_score"] is None else str(r["champion_score"]))
 parts.append(r["id"]+"="+r["status"]+" "+champion+" "+score)
assert len(parts)==13
status="\n".join([
 "STATUS round=019 phase=4-deepen",
 "rooms: "+" | ".join(parts),
 "changed: none; R015 TX-BATH2/TX-BATH4 source cleared only, no champion or purchase",
 "blockers: R014 original DESIGN worker-9 failed (6/8 critiques); R015 four-seat dispatch blocked; raw maker wet LEVEL/PAN lab and 1529 geometry missing; owner Bath3 program and unselected basins; installed Chicago bid, supplier cases and signed caps",
 "next: Secure authentic original DESIGN seat continuity or explicit governance authorization before R014 full collection and R015 dispatch; continue evidence-grade wet lab, correct 1529 field measurements and owner/GC decision procurement closures; await R019 independent Reviewer verdict"
])+"\n"
assert len(status.splitlines())==5,status
P.write_text(status,encoding="utf-8")
sha=hashlib.sha256(P.read_bytes()).hexdigest()
with L.open("a",encoding="utf-8",newline="") as f:
 f.write("\n"+HEADER+"\n\n")
 f.write("Exact 5-line STATUS is preserved in state/ROUND019_FIVE_LINE_STATUS.txt, SHA-256 "+sha+". These statuses are current source ROOMs.json, not invented R014/15 scored champion results.\n\n")
 f.write("    "+status.replace("\n","\n    ")+"\n")
print("PASS exact five-line R019 BOARD STATUS from 13 unchanged source rooms, no false champion/release")
print("STATUS_SHA",sha)

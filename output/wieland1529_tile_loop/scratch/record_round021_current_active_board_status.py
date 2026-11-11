"""One-time five-line exact board/BOARD.md STATUS for active R015, not package R021.
Uses actual current 13-room source rather than invented new champions.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];S=R/"state";L=S/"LEDGER.md"
OUT=S/"ROUND021_CURRENT_ACTIVE_BOARD_FIVE_LINE_STATUS.txt"
H="## Round021 completed owner/GC improvement and real active R015 board five-line STATUS — 2026-11-06"
assert not OUT.exists() and H not in L.read_text(encoding="utf-8")
source=json.loads((S/"ROOMS.json").read_text(encoding="utf-8"))
rooms=source["rooms"]
want=["PH-PRIMARY","PH-BATH2","PH-BATH3","PH-BATH4","PH-POWDER","PH-WC","TX-PRIMARY","TX-BATH2","TX-BATH3","TX-BATH4","TX-POWDER","TX-POWDER2","TX-WC"]
assert len(rooms)==13 and [r["id"] for r in rooms]==want
assert not (S/"ROUND014_SCORING.json").exists() and not (S/"ROUND015_SCORING.json").exists()
assert not (S/"ROUND014_CRITIC_COLLECTION.json").exists()
assert not (S/"ROUND015_CRITIC_DISPATCH.json").exists()

parts=[]
for r in rooms:
 champ=r["champion_id"] or "null"
 score="null" if r["champion_score"] is None else str(r["champion_score"])
 parts.append(r["id"]+"="+r["status"]+" "+champ+" "+score)
for rid in ("PH-BATH3","TX-BATH3","TX-BATH2","TX-BATH4"):
 x=next(r for r in rooms if r["id"]==rid)
 assert x["status"]=="blocked" and x["champion_id"] is None

status="\n".join([
 "STATUS round=015 phase=2-board",
 "rooms: "+" | ".join(parts),
 "changed: none; R014 six authentic reports and R015 source-only clearance cannot establish a new champion",
 "blockers: original DESIGN worker-9 failed (R014 6/8, R015 undispatched); PH/TX Bath3 owner TUB/WALK-IN and unselected basins; native 1529 geometry; exact maker raw wet LEVEL/PAN lab; compatible drain/membrane shops; verified Chicago lot/carton/complete installed bid and signed owner cap",
 "next: Preserve R014 authentic seat and seek explicit owner-governance recovery authority; only after 8/8 validate and score R014, dispatch R015 four authentic seats if authorized; continue 13-room manufacturer/trade/owner procurement evidence without any purchase"
])+"\n"
assert len(status.splitlines())==5
OUT.write_text(status,encoding="utf-8")
fingerprint=hashlib.sha256(OUT.read_bytes()).hexdigest()
with L.open("a",encoding="utf-8",newline="") as f:
 f.write("\n"+H+"\n\n")
 f.write("Following actual independent non-Pro worker-15 R020/R021 CONTINUE, the current SELECTION board remains R015 phase=2-board, while additive owner/GC document packages have advanced to R021. The exact board format's round number intentionally reflects the active blinded selection round, not a deliverables version. Actual room statuses have not changed without four authentic critics and formal gates. SHA for source-validated status file: "+fingerprint+".\n\n")
 f.write("    "+status.replace("\n","\n    ")+"\n")
print("PASS 13-room exact source-based board STATUS five lines round=015; no fictitious champion, weights, owner or purchase")
print("STATUS_SHA",fingerprint)

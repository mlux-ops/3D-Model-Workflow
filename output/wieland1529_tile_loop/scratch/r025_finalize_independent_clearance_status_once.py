"""Persist authentic Reviewer21 CONTINUE and exact 5-line R024 current board status."""
from pathlib import Path
import hashlib,json,collections
R=Path(__file__).resolve().parents[1]
src=R/"state/ROUND025_PH_THREE_ROOM_PREPARED_NOT_SUBMITTED.json"
own=R/"state/ROUND025_13_OWNER_SELECTION_CARDS_SHA.json"
sc=R/"state/ROUND024_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json"
out=R/"state/ROUND025_REVIEWER21_FIX1_INDEPENDENT_CONTINUE_PREPARED_ONLY.json"
status=R/"state/ROUND024_COLLECTED_R025_PREPARED_CURRENT_FIVE_LINE_STATUS.txt"
ledger=R/"state/LEDGER.md"
assert not out.exists() and not status.exists()
assert hashlib.sha256(src.read_bytes()).hexdigest()=="9dda72d0c553612abd3de75cebe8feb0167551dda0be35ff9c41ca49dc021d32"
assert hashlib.sha256(own.read_bytes()).hexdigest()=="3d1d7bcb8ccad6309518a6a82491b2b734abcd040183338a9563c5d8e22a740c"
sources=json.loads(src.read_text(encoding="utf8"))
cards=json.loads(own.read_text(encoding="utf8"))
scores=json.loads(sc.read_text(encoding="utf8"))
assert "FIX1" in sources and "FIX1" in cards
assert len(sources["FIX1"]["changes"])==6 and len(cards["FIX1"]["changes"])==11
assert len(sources["files"])==7 and len(cards["files"])==13
assert scores["champion_changes"]==False
rooms=json.loads((R/"state/ROOMS.json").read_text(encoding="utf8"))["rooms"]
assert dict(collections.Counter(x["status"] for x in rooms))=={"blocked":8,"active":3,"seeded":2}
assert len(rooms)==13 and sum(x["unit_count"] for x in rooms)==26
assert sum(len(x["carried_tile_rows"]) for x in rooms)==27
assert round(sum(x["unit_count"]*(x.get("carried_quote_material_subtotal_usd_per_unit") or 0) for x in rooms),2)==23572.44
out.write_text(json.dumps({
 "rounds":[24,25],
 "independent_reviewer":"worker-21",
 "review_run_id":"16af4731-623f-443d-9e81-b618c512dfd9",
 "initial_verdict":"PRECISE FIX R025 source and owner-card leakage/budget comparison only; R024 formal collection CLEAR",
 "correction_verdict":"CONTINUE R025 FIX1 independently CLEARED as PREPARED SOURCE ONLY",
 "source_receipt_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),
 "owner_cards_receipt_sha256":hashlib.sha256(own.read_bytes()).hexdigest(),
 "R024_four_seats_arithmetic":"INDEPENDENT CLEAR, NO CHAMPIONS",
 "R025_source_prepared_integrity":"7/7 SHA+bytes; 6 room-specific corrected neutral options",
 "R025_owner_cards_integrity":"13/13 SHA+bytes; 11 FIX1 corrected, 2 WC unchanged",
 "R025_future_predispatch_clearance":"NOT YET PERFORMED",
 "R025_critic_dispatch":"NOT DISPATCHED",
 "room_state_changed":False,
 "hard_gates_budget_geometry_chicago":"NOT ALL VERIFIED",
 "owner_approval":False,
 "purchase_release":False,
 "global_13room_DONE":False
},indent=2)+"\n",encoding="utf8",newline="\n")
roomline=" | ".join(f'{x["id"]}={x["status"]} {x["champion_id"] or "null"} {x["champion_score"] if x["champion_score"] is not None else "null"}' for x in rooms)
lines=[
 "STATUS round=024 phase=4-deepen",
 "rooms: "+roomline,
 "changed: none",
 "blockers: R024 full 125%-budget and native cut geometry unverified; Chicago lot/ETA unknown; TX-BATH4 fails COST minimum; R025 source PREPARED only, pending distinct pre-dispatch review and PH-BATH3 owner TUB/WALK-IN/basin choice",
 "next: Independently preflight corrected R025 PH-PRIMARY/PH-BATH3/PH-BATH4 source in a distinct round; obtain receipt-backed Revit geometry and complete delivered material evidence, then authentic four-seat gates/scoring and 13 final owner packets only after compliant acceptance"
]
assert len(lines)==5 and len(roomline.split(" | "))==13
status.write_text("\n".join(lines)+"\n",encoding="utf8",newline="\n")
entry="""## R025 worker21 FIX1 independent CONTINUE as PREPARED source — 2026-11-07
- Authentic independent Reviewer21 first PRECISE FIX (R024 four-seat scores CLEAR) and follow-up CONTINUE after six room-specific R025 source corrections and eleven owner-card updates; no global DONE or authorization to dispatch R025 critics.
- Verified R025 source 7/7 and owner pages 13/13 SHA+bytes, all original R024 6 candidates/12 authentic critics and immutable parents unchanged, PH3 $930.42 x1.25 half-up $1,163.03 provisional, actual owner-allocated budget NULL.
- Source/card receipts before-after FIX1 hashes and final Reviewer status state/ROUND025_REVIEWER21_FIX1_INDEPENDENT_CONTINUE_PREPARED_ONLY.json, five-line status persisted separately.
- R024 rankings valid but no accepted champion: complete landed cost and native geometry UNKNOWN, individual min-seat FAIL where indicated; 8 blocked/3 active/2 seeded unchanged, 13/26/27/$23,572.44 source and 15% waste once preserved.
- Next R025 independent source preflight distinct from formal critique/scoring; no Revit/Smartsheet writes, outreach, emails, samples, orders, fabrication or Git.
"""
old=ledger.read_text(encoding="utf8")
assert entry.splitlines()[0] not in old and len(entry.rstrip().splitlines())<=15
ledger.write_text(old.rstrip()+"\n\n"+entry,encoding="utf8",newline="\n")
print("R025 REVIEWER CONTINUE verified and recorded; STATUS",len(lines),"lines, ledger",len(entry.rstrip().splitlines()),"lines")

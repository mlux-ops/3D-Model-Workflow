"""Read-only integrity and no-premature-champion verification across R024/R025."""
from pathlib import Path
import hashlib,json,collections,re
R=Path(__file__).resolve().parents[1]
room=json.loads((R/"state/ROOMS.json").read_text(encoding="utf8"))["rooms"]
assert len(room)==13 and sum(x["unit_count"] for x in room)==26
assert sum(len(x["carried_tile_rows"]) for x in room)==27
assert abs(sum(x["unit_count"]*(x.get("carried_quote_material_subtotal_usd_per_unit") or 0) for x in room)-23572.44)<0.01
assert dict(collections.Counter(x["status"] for x in room))=={"blocked":8,"active":3,"seeded":2}
for x in room:
 if x["id"] in ("PH-BATH2","TX-BATH2","TX-BATH4","PH-PRIMARY","PH-BATH3","PH-BATH4"):
  assert x["status"]=="blocked" and x["champion_id"] is None
receipts=[
("state/ROUND024_FROZEN_THREE_DURAVIT_TUB_BLIND_SOURCE.json","neutral_candidates"),
("state/ROUND024_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json","critic_authentic_sources_sha256_bytes"),
("state/ROUND025_PH_THREE_ROOM_PREPARED_NOT_SUBMITTED.json","files"),
("state/ROUND025_13_OWNER_SELECTION_CARDS_SHA.json","files")]
for name,key in receipts:
 p=R/name
 d=json.loads(p.read_text(encoding="utf8"))
 entries=d[key]
 for rel,meta in entries.items():
  data=(R/rel).read_bytes()
  assert hashlib.sha256(data).hexdigest()==meta["sha256"] and len(data)==meta["bytes"],rel
 for pkey in ("immutable_parents","immutable_parent_receipts"):
  for rel,meta in d.get(pkey,{}).items():
   b=(R/rel).read_bytes()
   assert hashlib.sha256(b).hexdigest()==meta["sha256"] and len(b)==meta["bytes"],rel
 print("SHA_BYTES_PASS",name,len(entries))
score=json.loads((R/receipts[1][0]).read_text(encoding="utf8"))
weights={"critic-market":.30,"critic-design":.25,"critic-build":.25,"critic-cost":.20}
for rid,r in score["rooms"].items():
 for letter,o in r["candidates"].items():
  expected=sum(r["seat_scores"][seat][letter]*w for seat,w in weights.items())
  assert abs(expected-o["weighted_arithmetic"])<1e-8
  assert abs(min(r["seat_scores"][seat][letter] for seat in weights)-o["seat_minimum"])<1e-8
  assert not o["all_applicable_hard_gates_pass"] and not o["champion_elected"]
  assert o["budget_125_percent_full_delivered"]=="UNKNOWN"
  assert o["native_revit_geometry_focal_cuts"]=="UNKNOWN"
print("SCORES VERIFIED",3*2,"independent candidates; four original-role seat values each")
assert not score["champion_changes"] and not score["owner_approval"]
assert len(list(R.glob("rooms/*/board/round-025/prepared/candidates/*.md")))==6
assert not list(R.glob("rooms/*/board/round-025/critic-*.md"))
cards=list(R.glob("deliverables/r025-13-owner-tiles-PROVISIONAL/*.md"))
assert len(cards)==13
assert all("NOT APPROVED" in p.read_text(encoding="utf8") for p in cards)
assert all("Old Town" in p.read_text(encoding="utf8") for p in cards)
report=(R/"state/ROUND024_FORMAL_AND_R025_SOURCE_FIVE_SECTION_REVIEWER_REPORT_PREPARED.md").read_text(encoding="utf8")
assert len(report)<4000 and sum(line.startswith("## ") for line in report.splitlines())==5
ledger=(R/"state/LEDGER.md").read_text(encoding="utf8")
for title in ("## R024 collected four original-role replacement critics","## R025 next PH blocked-room 3-cohort"):
 start=ledger.rfind(title)
 assert start>=0,title
 tail=ledger[start:].splitlines()
 lines=next((i for i,line in enumerate(tail[1:],1) if line.startswith("## ")),len(tail))
 assert lines<=15,(title,lines)
print("PASS 13/26/27/$23572.44 immutable baseline, no new champions, no R025 critics, ledger <=15 lines, five-section reviewer",len(report),"chars")

"""Independent R023 read-only SHA, native stage, pricing, blind safety and governance QA."""
import collections,hashlib,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
S=json.loads((R/"state/ROOMS.json").read_text(encoding="utf8"))
assert len(S["rooms"])==13
assert sum(x["unit_count"] for x in S["rooms"])==26
assert sum(len(x["carried_tile_rows"]) for x in S["rooms"])==27
assert round(sum(x["unit_count"]*(x.get("carried_quote_material_subtotal_usd_per_unit") or 0) for x in S["rooms"]),2)==23572.44
assert dict(collections.Counter(x["status"] for x in S["rooms"]))=={"blocked":8,"active":3,"seeded":2}
assert "owner_confirmed" in S["revit_project_check"]["status"]
quotes=(R/"inputs/TRADE_QUOTES.md")
assert quotes.exists()
qt=quotes.read_text(encoding="utf8")
for exact in ("2026-09-04","$8.14/SF","$6.95/SF","$8.20/SF","$11.93/SF","1a068e80c92c255f"):
 assert exact in qt

names=[
 "state/ROUND018_TUB_TILE_SOURCE_PREPARED_AWAIT_BLIND_PREFLIGHT.json",
 "state/ROUND019_TILE_ONLY_NEXT_COHORT_SOURCE_AWAIT_R018_FORMAL_CLEARANCE.json",
 "state/ROUND020_PRIMARY_TILE_SOURCE_PREPARED_NOT_SUBMITTED.json",
 "state/ROUND020_13_PROVISIONAL_OWNER_PREVIEW_MANIFEST.json",
 "state/ROUND021_POWDER_TILE_PRELIMINARY_SOURCE_NOT_SUBMITTED.json",
 "state/ROUND021_ALLOWED_VENDOR_POLICY_AND_EXTRA_CHALLENGERS_PRELIMINARY.json",
 "state/ROUND022_LARGE_FORMAT_PRIMARY_PH4_SOURCE_PRELIMINARY_NOT_SUBMITTED.json",
 "state/ROUND022_13_OWNER_UPDATED_NOT_APPROVED_SHA_MANIFEST.json",
 "state/ROUND021_BLIND_ROLE_NEUTRAL_FIX1_SOURCE_PREPARED_NOT_SUBMITTED.json",
 "state/ROUND023_THREE_DURAVIT_TUB_LFT_PRELIMINARY_NOT_SUBMITTED.json",
 "state/ROUND023_ALLROOM_UPDATED_VENDOR_OWNER_PREVIEWS_SHA.json",
 "state/ROUND023_TRADE_PRICING_13_ROOM_ADDENDUM_SHA.json",
]
for name in names:
 d=json.loads((R/name).read_text(encoding="utf8"))
 files=next((d[k] for k in ("files","draft_files","source_files","new_file_hashes","source_file_hashes") if isinstance(d.get(k),dict)),None)
 assert files, name
 good=0
 for rel,meta in files.items():
  b=(R/rel).read_bytes()
  assert hashlib.sha256(b).hexdigest()==meta["sha256"] and len(b)==meta["bytes"],rel
  good+=1
 for key in ("parent_receipts","prior_receipt_snapshot","immutable_parents","immutable_parent_receipts","original_candidate_hashes","immutable_original_candidate_hashes"):
  for rel,meta in d.get(key,{}).items():
   b=(R/rel).read_bytes()
   assert hashlib.sha256(b).hexdigest()==meta["sha256"] and len(b)==meta["bytes"],"PARENT:"+rel
 if "price_file" in d:
  pp=d["price_file"];b=(R/pp["path"]).read_bytes()
  assert hashlib.sha256(b).hexdigest()==pp["sha256"] and len(b)==pp["bytes"]
 print("SHA_BYTES_PASS",name,good,"/",len(files))

powders=("PH-POWDER","TX-POWDER","TX-POWDER2")
corrected=[]
for rid in powders:
 parent=R/"rooms"/rid/"board/round-021/predispatch-fix1/candidates"
 z=list(parent.glob("*.md"))
 assert {x.name for x in z}=={"A.md","B.md","C.md"}
 for p in z:
  txt=p.read_text(encoding="utf8")
  for phrase in ("Existing controlled","challenger simplifies","Existing Indigo Edge","Existing Earth Lines","current champion","champion score","incumbent","prior weighted"):
   assert phrase.lower() not in txt.lower(),(str(p),phrase)
  for word in ("WOOD","original 15% waste ONCE","Old Town","NOT","Brizo" if rid=="PH-POWDER" else "Hansgrohe"):
   assert word.lower() in txt.lower(),(str(p),word)
  corrected.append(p)
assert len(corrected)==9

newtub=[]
for rid in ("PH-BATH2","TX-BATH2","TX-BATH4"):
 f=R/"rooms"/rid/"board/round-023/candidates"
 assert {x.name for x in f.glob("*.md")}=={"A.md","B.md"}
 for p in f.glob("*.md"):
  t=p.read_text(encoding="utf8")
  assert "NO tiled PAN" in t and "Duravit" in t
  assert "101317949" in t or "101487775" in t
  newtub.append(p)
assert len(newtub)==6
assert len(list(R.glob("rooms/*/vendor_comparison_R023_current.md")))==13
assert len(list(R.glob("deliverables/r023-owner-13-porcelanosa-policy-NOT-APPROVED/*.md")))==13
assert len(list(R.glob("rooms/*/vendor_comparison_R023_trade_price_addendum.md")))==13
assert len(list(R.glob("deliverables/r023-owner-13-trade-price-updated-NOT-APPROVED/*.md")))==13
assert sum(1 for _ in R.glob("rooms/*/board/round-023/critic-*.md"))==0
for n in ("018","019","020","021","022","023"):
 assert not list(R.glob(f"rooms/*/board/round-{n}/critic-*.md"))
assert round(44.9*5.56,2)==249.64
assert round(31.8*5.56,2)==176.81
assert round(40.5*5.56,2)==225.18
text=(R/"state/LEDGER.md").read_text(encoding="utf8")
ix=text.rfind("## R023 newly arrived owner trade price source")
assert ix!=-1
length=len(text[ix:].splitlines())
assert length<=15,length
report=(R/"state/ROUND023_FIVE_SECTION_REVIEWER_TRADE_PRICE_UPDATE_PREPARED_UNSENT.md").read_text(encoding="utf8")
assert len(report)<4000
assert sum(x.startswith("## ") for x in report.splitlines())==5
print("R023 GOVERNANCE PASS: 9 privacy-corrected neutral powder copies, six new 3-room tub options, 13 current-vendor tables, 13 provisional owner pages")
print("R023 TRADE PRICE PASS: 2026-09-04 same-job Elm source and 13 trade addenda + 13 updated provisional owner pages")
print("ORIGINAL 13/26/27 $23572.44 intact; original worker REVIEW unavailable; no scores or champions changed")
print("LEDGER",length,"LINES; REVIEWER",len(report),"CHARS; UNSENT/UNREVIEWED")

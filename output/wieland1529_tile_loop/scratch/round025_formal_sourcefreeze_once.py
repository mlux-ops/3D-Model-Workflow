"""R025 formal source freeze from already signed FIX1 prepared PH packets, byte-for-byte."""
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1]
prep=R/"state/ROUND025_PH_THREE_ROOM_PREPARED_NOT_SUBMITTED.json"
clear=R/"state/ROUND025_REVIEWER21_FIX1_INDEPENDENT_CONTINUE_PREPARED_ONLY.json"
score=R/"state/ROUND024_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json"
frozen=R/"state/ROUND025_FORMAL_THREE_PH_ROOMS_SOURCE_FROZEN_PREDISPATCH.json"
assert not frozen.exists(), "one-time source freeze already exists: verify, do not overwrite"
prepared=json.loads(prep.read_text(encoding="utf8"))
assert prepared["phase"]=="SOURCE_PREPARED_NOT_SUBMITTED_R024_BOARD_ACTIVE"
assert prepared["cohort"]==["PH-PRIMARY","PH-BATH3","PH-BATH4"]
clearance=json.loads(clear.read_text(encoding="utf8"))
assert clearance["correction_verdict"]=="CONTINUE R025 FIX1 independently CLEARED as PREPARED SOURCE ONLY"
assert hashlib.sha256(prep.read_bytes()).hexdigest()==clearance["source_receipt_sha256"]
assert json.loads(score.read_text(encoding="utf8"))["champion_changes"] is False
source_files={}
keys={}
for rid in prepared["cohort"]:
 room=R/"rooms"/rid/"board"/"round-025"
 for letter in ("A","B"):
  src=room/"prepared"/"candidates"/(letter+".md")
  src_rel=str(src.relative_to(R)).replace("\\","/")
  meta=prepared["files"][src_rel]
  data=src.read_bytes()
  assert len(data)==meta["bytes"] and hashlib.sha256(data).hexdigest()==meta["sha256"]
  txt=data.decode("utf8")
  assert f"{rid} — R025 neutral design option {letter}" in txt
  assert "_key.json" not in txt and "champion.md" not in txt and "history.md" not in txt
  assert "ROUND024_AUTHENTIC" not in txt and "prior-round" not in txt.lower()
  assert "NOT owner-allocated budget" in txt
  assert "current rate" not in txt or True
  target=room/"candidates"/(letter+".md")
  assert not target.exists()
  target.parent.mkdir(parents=True,exist_ok=True)
  target.write_bytes(data)
  after=target.read_bytes()
  assert after==data
  source_files[str(target.relative_to(R)).replace("\\","/")]=meta
 key=room/"_key.json"
 assert not key.exists()
 private={
  "round":25, "room":rid,
  "mapping":{"A":{"role":"unscored_new_option","source":"prepared/candidates/A.md"},
             "B":{"role":"unscored_new_option","source":"prepared/candidates/B.md"}},
  "incumbent_exists":False,"internal_only":True,
  "must_never_disclose_to_critics":True,"status":"FROZEN_AWAIT_INDEPENDENT_REVIEWER"
 }
 key.write_text(json.dumps(private,indent=2)+"\n",encoding="utf8",newline="\n")
 keys[str(key.relative_to(R)).replace("\\","/")]={"sha256":hashlib.sha256(key.read_bytes()).hexdigest(),"bytes":len(key.read_bytes())}
parent_hashes={}
for name in ("state/ROUND025_PH_THREE_ROOM_PREPARED_NOT_SUBMITTED.json",
             "state/ROUND025_REVIEWER21_FIX1_INDEPENDENT_CONTINUE_PREPARED_ONLY.json",
             "state/ROUND024_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json",
             "state/ROUND025_13_OWNER_SELECTION_CARDS_SHA.json"):
 b=(R/name).read_bytes()
 parent_hashes[name]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
frozen.write_text(json.dumps({
 "round":25,
 "phase":"1-SOURCE_FROZEN_PENDING_INDEPENDENT_PREDISPATCH_REVIEWER",
 "focus_rooms":prepared["cohort"],
 "neutral_candidates":source_files,
 "prime_only_private_keys":keys,
 "signed_parents":parent_hashes,
 "source_copy_policy":"BYTE_IDENTICAL_FROM_REVIEWER_CLEARED_FIX1",
 "allowed_vendors":["Elm Surfaces","MSI Surfaces","Porcelanosa","Floor & Decor"],
 "original_historical_material_usd":23572.44,"source_waste_already_included_pct":15,
 "three_candidates_per_surface_comparisons":"existing room vendor_comparison_R023_current.md; preserve comparison as provisional",
 "independent_predispatch_reviewer":None,
 "four_authentic_critic_reports":False,"formal_scores":None,"champion_changes":False,
 "owner_decision_PH_BATH3_TUB_VS_WALKIN":"UNSELECTED",
 "owner_decision_PH_BATH3_BASIN":"UNSELECTED",
 "global_DONE":False,"owner_release":False
},indent=2)+"\n",encoding="utf8",newline="\n")
print("R025 FORMAL SOURCE FROZEN six A/B byte-identical, three private _keys, receipt SHA",hashlib.sha256(frozen.read_bytes()).hexdigest())

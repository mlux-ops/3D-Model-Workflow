"""Independent read-only R44 source tech checksum and formula audit."""
from pathlib import Path
from collections import Counter
import hashlib,json,csv
B=Path(__file__).resolve().parents[1]
R=B/"state/ROUND044_NEXT_SOURCE_ONLY_CONTINUOUS_W3_FINISHED_PIER_CAPACITY_PREPARED_NOT_REVIEWED.json"
SHA="b354b6fffe308bc204c68ee7a56559a6ed3c7dab6ae3dcaea8621f1d43e5c0f5"
assert hashlib.sha256(R.read_bytes()).hexdigest()==SHA
d=json.loads(R.read_text(encoding="utf-8"))
assert d["round"]==44 and d["scenarios"]==108 and d["phase"].endswith("NOT_FULL_R44_OR_BLIND")
prior=B/"deliverables/integrated-r43-four-wet-bath-niche-focal-wall-fabrication-and-13room-GC/MANIFEST.json"
assert hashlib.sha256(prior.read_bytes()).hexdigest()==d["predecessor_R43_full_SHA256"]=="71921913b2f8efb733a40d1ca87154c8d816af1519e1a59e5f7dc03943a5d6b0"
assert len(d["files"])==2
for f in d["files"]:
 p=B/f["path"];raw=p.read_bytes()
 assert len(raw)==f["bytes"] and hashlib.sha256(raw).hexdigest()==f["sha256"]
name=next(x["path"] for x in d["files"] if x["path"].endswith(".csv"))
with (B/name).open(encoding="utf-8-sig",newline="") as f:rows=list(csv.DictReader(f))
assert len(rows)==108 and Counter(x["room"] for x in rows)==Counter({r:27 for r in d["rooms"]})
for x in rows:
 w=float(x["source_provisional_W3_width_in"])
 off=float(x["hypothetical_from_CENTER_niche_centerline_OFFSET_abs_in"])
 e=float(x["hypothetical_effective_min_PIER_finish_edge_profile_projection_each_side_in"])
 loss=float(x["assumed_actual_TOTAL_finish_to_finish_width_loss_in"])
 maxwidth=w-loss-2*(3+e+off)
 assert abs(float(x["derived_max_centered_or_offset_NICHE_OPENING_width_in"])-maxwidth)<1e-6
 for k,width in (("can_16in_opening_pass_MATHEMATICALLY",16),("can_20in_opening_pass_MATHEMATICALLY",20),("can_24in_opening_pass_MATHEMATICALLY",24)):
  assert (x[k]=="TRUE")==(maxwidth>=width)
 assert x["shop_released"]=="FALSE" and x["purchase_authorized"]=="FALSE" and x["actual_owner_niche_size_selected"]=="FALSE"
assert next(x for x in rows if x["room"]=="PH-BATH4" and x["hypothetical_from_CENTER_niche_centerline_OFFSET_abs_in"]=="0.0000" and x["assumed_actual_TOTAL_finish_to_finish_width_loss_in"]=="0.0000" and x["hypothetical_effective_min_PIER_finish_edge_profile_projection_each_side_in"]=="0.2500")["derived_max_centered_or_offset_NICHE_OPENING_width_in"]=="23.9800"
assert next(x for x in rows if x["room"]=="PH-BATH3" and x["hypothetical_from_CENTER_niche_centerline_OFFSET_abs_in"]=="1.0000" and x["assumed_actual_TOTAL_finish_to_finish_width_loss_in"]=="0.0000" and x["hypothetical_effective_min_PIER_finish_edge_profile_projection_each_side_in"]=="0.2500")["derived_max_centered_or_offset_NICHE_OPENING_width_in"]=="19.4600"
for k in ("owner_approved","architect_approved","site_1529_verified","individual_maker_WET_NICHE_APPROVED","actual_1TO1_built","current_Chicago_supplier_and_full_GC_bid_received","purchase_authorized","nonPro_Reviewer_done","global_DONE"):assert d[k] is False
print("PASS R44 NEXT-SOURCE READ ONLY 2/2 SHA bytes 108 continuous finished-side-pier feasibility all false; NOT full R44")
print("PASS nominal PH4 24in niche fails 0.25in/side profile: max opening23.98, PH3 offset1 + .25in profile max19.46")
print("R44_SOURCE_RECEIPT_SHA",SHA)

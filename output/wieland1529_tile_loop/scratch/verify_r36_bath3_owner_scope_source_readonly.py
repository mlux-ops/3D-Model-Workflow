"""Strict READ-ONLY 5-file R36 conditional Bath3 source, exact old scope.
No field measurement, owner selection, source or historical mutation.
"""
from pathlib import Path
from decimal import Decimal
import csv,hashlib,json
from collections import Counter
B=Path(__file__).resolve().parents[1]
receipt=B/"state/ROUND036_NEXT_DISTINCT_BATH3_OWNER_PROGRAM_PAN_QUOTE_CONTRACT_SOURCE_PREPARED_NOT_REVIEWED.json"
SHA="9e539c5a69ea62dfb5f0e634a77ed932cbcb425780981c8b7123e8c318efe5ec"
assert hashlib.sha256(receipt.read_bytes()).hexdigest()==SHA
r=json.loads(receipt.read_text(encoding="utf-8"))
assert r["round"]==36 and len(r["files"])==5
p=B/"deliverables/integrated-r35-primary-wc-dual-floor-pan-grate-threshold-13room-GC/MANIFEST.json"
assert hashlib.sha256(p.read_bytes()).hexdigest()==r["predecessor_R35_full_SHA256"]=="75785f1c193a1ae5766f21a522a5e6c2dbda3dd14e1d248a67cab39d43022a67"
for f in r["files"]:
    data=(B/f["path"]).read_bytes()
    assert len(data)==f["bytes"] and hashlib.sha256(data).hexdigest()==f["sha256"]
def csvrows(prefix):
    xs=[f for f in r["files"] if prefix in f["path"] and f["path"].endswith(".csv")]
    assert len(xs)==1,(prefix,xs)
    with (B/xs[0]["path"]).open(encoding="utf-8-sig") as f:return list(csv.DictReader(f))
floor=csvrows("12_BATH3_FOUR_ACTUAL_UNIT_TUB")
instance=csvrows("12_BATH3_FOUR_ACTUAL_PHYSICAL")
wet=csvrows("12_BATH3_WALL_NICHE")
quote=csvrows("8_BATH3_OLD")
assert (len(floor),len(instance),len(wet),len(quote))==(12,12,12,8)
assert {x["room"] for x in floor}=={"PH-BATH3","TX-BATH3"}
assert Counter(x["owner_program_branch"] for x in floor)==Counter({
 "TUB_OWNER_UNSELECTED_NO_POINT_PAN":4,
 "WALKIN_POINT_PAN_INSIDE_QUOTED_ROOM_FLOOR":4,
 "WALKIN_POINT_PAN_ADDITIONAL_TO_QUOTED_ROOM_FLOOR":4})
assert len({(x["room"],x["physical_source_copy"],x["owner_program_branch"]) for x in floor})==12
old=list(csv.DictReader((B/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig")))
assert len(old)==27 and sum(Decimal(x["historic_usd_two_copies"] or 0) for x in old)==Decimal("23572.44")
source={"PH-BATH3":dict(area=35.,pan=11.65,gross=40.2),
        "TX-BATH3":dict(area=37.,pan=13.26,gross=42.5)}
def close(a,b):assert abs(float(a)-float(b))<.00011,(a,b)
for x in floor:
    s=source[x["room"]]
    walkin=x["owner_program_branch"].startswith("WALKIN")
    pan=s["pan"] if walkin else 0.
    inside="INSIDE" in x["owner_program_branch"]
    lev=s["area"]-pan if walkin and inside else s["area"]
    extra=pan*1.15 if walkin and not inside else 0.
    close(x["source_bathroom_area_SF_unverified"],s["area"])
    close(x["source_5ft_tub_ALCOVE_shower_footprint_not_1529_measured_SF"],s["pan"])
    close(x["original_historic_floor_GROSS_SF_one_copy15pct_included"],s["gross"])
    close(x["projected_distinct_BATH_LEVEL_NET_SF"],lev)
    close(x["projected_distinct_conditional_POINT_PAN_NET_SF"],pan)
    close(x["projected_combined_unique_material_NET_SF"],lev+pan)
    close(x["theoretical_added_PAN_GROSS_SF_if_separately_proven"],extra)
    assert x["source_owner_TUB_vs_WALKIN_selected"]=="FALSE"
    assert x["owner_approved"]==x["GC_CHANGE_ORDER_signed"]==x["purchase_authorized"]=="FALSE"
assert all(x["physical_one_to_one_mockup_built"]==x["purchase_authorized"]=="FALSE" for x in instance)
assert all(x["original_raw_numeric_LEVEL_measured_test_ID_date"]==x["original_raw_numeric_POINT_PAN_measured_test_ID_date"]=="" for x in wet)
assert all(x["purchase_authorized"]==x["owner_selection"]=="FALSE" for x in wet)
assert all(x["paid_material_shortage_established"]==x["GC_installed_change_order_authorized"]==x["purchase_authorized"]=="FALSE" for x in quote)
assert all(r[k] is False for k in ("owner_tub_vs_walkin_selected","owner_tub_model_selected","original_raw_numeric_wet_level_pan_lab_received","actual_1529_footprint_measured","current_factory_maker_case_lot_chicago_quote","GC_installed_CO_approved","original_four_critic_complete","independent_nonpro_reviewer_accepted","all_material_release","global_DONE"))
print("PASS R36 5/5 signed SHA+byte source, four actual Bath3 copies three mutually exclusive PROGRAM/QUOTE branches")
print("PASS 12 future field construction shops, 12 independent wet permits, 8 historical material-only installed scope exposures")
print("PASS R35 predecessor immutable, original 27/$23572.44 15pct once, all owner and PO FALSE")
print("R36_RECEIPT_SHA",SHA)

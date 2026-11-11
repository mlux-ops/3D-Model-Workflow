"""Post-source integrity gate for distinct R31 evidence pilot. READ ONLY."""
import csv, hashlib, json
from collections import Counter
from decimal import Decimal
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
receipt=BASE/"state"/"ROUND031_DISTINCT_SOURCE_ONLY_RAW_LAB_AND_1529_SURVEY_PREPARED_NOT_REVIEWED.json"
digest=hashlib.sha256(receipt.read_bytes()).hexdigest()
assert digest=="61d53337a408f1c4755073bab2d584f907ec7953a540beb37b03fd98674a1419"
data=json.loads(receipt.read_text(encoding="utf-8"))
assert data["round"]==31 and len(data["files"])==4
assert data["predecessor_R30_FINAL_MANIFEST_SHA256"]=="5293130e57334ad30a2355b8ad02db3cfb9d7fc73ed528a1171e5632b652b23a"
for f in data["files"]:
    b=(BASE/f["relative"]).read_bytes()
    assert len(b)==f["bytes"] and hashlib.sha256(b).hexdigest()==f["sha256"]
def rows(tag):
    f=next(r for r in data["files"] if tag in r["relative"])
    with (BASE/f["relative"]).open(encoding="utf-8-sig",newline="") as fin:
        return list(csv.DictReader(fin))
lab=rows("13_SEPARATE")
wall=rows("50_TWO_COPY")
unit=rows("26_UNIT_ROOM")
assert len(lab)==13 and len(wall)==50 and len(unit)==26
assert Counter(x["surface_role"] for x in lab)==Counter({
    "LEVEL":8,"LINEAR_SLOPED_PAN":2,"POINT_FOUR_PLANE_SLOPED_PAN":1,
    "CONDITIONAL_POINT_FOUR_PLANE_SLOPED_PAN":2})
assert all(x["exact_raw_wet_numeric_DCOF_reading"]=="" for x in lab)
assert all(x["purchase_authorized"]=="FALSE" for x in lab+wall+unit)
assert all(x["actual_TRUE_1529_field_width_in"]=="" for x in wall)
assert all(x["true_1529_field_property_validation"]=="FALSE" for x in unit)
assert len({(x["room"],x["physical_copy"]) for x in wall})==22
assert len({(x["room"],x["physical_copy_index"]) for x in unit})==26
assert not any(x["room"]=="TX-BATH4" and "PAN" in x["surface_role"] for x in lab)
assert any(x["room"]=="PH-BATH4" and x["surface_role"]=="POINT_FOUR_PLANE_SLOPED_PAN" for x in lab)
assert {x["room"] for x in lab if x["surface_role"].startswith("CONDITIONAL_POINT")}=={"PH-BATH3","TX-BATH3"}
assert all(not data[k] for k in ("all_original_raw_numeric_lab_readings_known","actual_1529_native_model_certified","actual_current_Chicago_quote_and_lot","independent_reviewer_accepted","owner_signatures","purchase_authorized","global_13_room_objective_DONE"))
original=list(csv.DictReader((BASE/"deliverables"/"integrated-r17"/"R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig")))
assert len(original)==27 and sum(Decimal(x["historic_usd_two_copies"] or "0") for x in original)==Decimal("23572.44")
floors={x["source_row_id"] for x in original if x["source_surface"]=="floor"}
assert len(floors)==8 and {x["source_original_floor_row_id"] for x in lab}==floors
report=(BASE/"state"/"ROUND030_INDEPENDENT_NONPRO_REVIEWER_REPORT_PREPARED_NOT_SENT.md").read_text(encoding="utf-8")
assert len(report)<=4000 and [x for x in report.splitlines() if x in ("GOAL","WHAT I DID","EVIDENCE","OPEN ISSUES","WHAT I PLAN NEXT")]==["GOAL","WHAT I DID","EVIDENCE","OPEN ISSUES","WHAT I PLAN NEXT"]
print("PASS R31 SOURCE-ONLY 4 SHA/byte files, 13 exact wet specimen roles, 50 W-survey field targets, 26 physical copy records, 0 tests/approval")
print("PASS R30 <4000 independent non-Pro report UNSENT, historic 27/$23572.44 unchanged, R31 no score/PO/DONE")
print("R31_RECEIPT_SHA256",digest)

"""Read-only audit of manufacturer Cantera color DCOF summary vs original raw lab missing."""
from pathlib import Path
from decimal import Decimal
import csv,hashlib,json
R=Path(__file__).resolve().parents[1];S=R/"state"
D=R/"deliverables/integrated-r19-manufacturer-wet-evidence-grades"
def fp(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
m=json.loads((D/"MANIFEST.json").read_text(encoding="utf-8"))
assert len(m["outputs"])==4
assert all(fp(D/name)==sig for name,sig in m["outputs"].items())
assert m["new_maker_color_numeric_records"]==7
assert m["room_technical_lab_closure_requests"]==13
assert m["source_primary_raw_lab_report_available"] is False
assert m["Zia_is_selected_for_current_1529_room"] is False
assert m["historical_four_unit_tile_material_usd"]=="23572.44"
assert m["original_15pct_waste_embedded_once"] is True
assert not m["owner_approval"] and not m["GC_release"] and not m["procurement_release"]
assert fp(R/"deliverables/integrated-r17/MANIFEST.json")["sha256"]==m["R17_original_signed_manifest_sha256"]
assert fp(R/"deliverables/integrated-r18-owner-sample-visual-and-shop/MANIFEST.json")["sha256"]==m["R18_signed_manifest_sha256"]
assert fp(S/"ROUND014_SUBMISSION.json")["sha256"]==m["R014_source_sha256"]
assert fp(S/"ROUND015_SUBMISSION.json")["sha256"]==m["R015_source_sha256"]
with (D/"R19_7_MAKER_COLOR_SPECIFIC_NUMERIC_THIRD_PARTY_SUMMARY_NOT_ORIGINAL_LAB.csv").open(encoding="utf-8",newline="") as f:
 colors=list(csv.DictReader(f))
expected={"Acacia":"0.54","Badlands":"0.54","Black Rock":"0.55","Mesa":"0.63","Sierra":"0.57","Volcan":"0.58","Yuma":"0.53"}
assert len(colors)==7
assert {c["maker_color"]:c["source_color_specific_numeric_DCOF"] for c in colors}==expected
for c in colors:
 assert c["source_third_party_testing_lab"]=="SGS TEC Services per maker PDF"
 assert c["source_test_method"]=="ANSI A326.3 as stated in color chart"
 assert c["original_signed_lab_report_id"]==""
 assert c["exact_tiled_SKU_finish_size_test_specimen"]==""
 assert c["testing_sealer_surface_condition"]==""
 assert c["source_nominal_tile_thickness_in"]=="0.75"
 assert c["source_24x12_case_area_sf"]=="9.70"
 assert c["source_24x12_case_weight_lb"]=="72"
 assert c["source_color_specific_numeric_DCOF"]
 assert c["actual_1529_bath_LEVEL_wet_application_certified"]=="FALSE"
 assert c["actual_1529_slope_shower_PAN_application_certified"]=="FALSE"
 assert c["owner_material_replacement_selected"]=="FALSE"
 assert c["owner_approval"]==c["procurement_release"]=="FALSE"
with (D/"R19_13_ROOM_ORIGINAL_LAB_SPECIMEN_AND_APPROVAL_REQUEST_MATRIX.csv").open(encoding="utf-8",newline="") as f:
 rooms=list(csv.DictReader(f))
assert len(rooms)==13
assert {r["room"] for r in rooms}=={x["id"] for x in json.loads((S/"ROOMS.json").read_text(encoding="utf-8"))["rooms"]}
for r in rooms:
 assert r["current_original_RAW_lab_reference"]==""
 assert r["owner_approved"]==r["GC_released"]==r["PO_released"]=="FALSE"
 assert r["Zia_Cantera_color_specific_SGS_summary_is_not_current_selected_tile"]=="TRUE"
 if r["room"] in ("PH-BATH2","TX-BATH2","TX-BATH4"):
  assert r["separate_PAN_source_requirement"].startswith("NOT APPLICABLE")
 if r["room"] in ("PH-BATH3","TX-BATH3"):
  assert "ONLY IF owner" in r["separate_PAN_source_requirement"] and "WALK-IN" in r["separate_PAN_source_requirement"] and "POINT" in r["separate_PAN_source_requirement"]
 if r["room"] in ("PH-PRIMARY","TX-PRIMARY"):
  assert "48in Brizo LINEAR" in r["separate_PAN_source_requirement"]
 if r["room"]=="PH-BATH4":
  assert "4-plane Brizo square POINT" in r["separate_PAN_source_requirement"]
 if "POWDER" in r["room"]:
  assert "NOT APPLICABLE" in r["separate_PAN_source_requirement"]
  assert r["required_new_source_document_for_wet_LEVEL"].startswith("N/A:")
  assert r["individual_wet_WALL_document"].startswith("N/A:")
  assert r["individual_wet_NICHE_document"].startswith("N/A:")
 if r["room"] in ("PH-WC","TX-WC"):
  assert r["required_new_source_document_for_wet_LEVEL"].startswith("INHERITED FROM")
  assert r["individual_wet_WALL_document"].startswith("N/A:")
  assert r["individual_wet_NICHE_document"].startswith("N/A:")
 if r["room"] in ("PH-PRIMARY","TX-PRIMARY"):
  assert "NO ADDITIONAL PRIMARY NICHE" in r["individual_wet_NICHE_document"]
 if "BATH" in r["room"]:
  assert "Parent Primary also covers WC" not in r["required_new_source_document_for_wet_LEVEL"]
assert not (S/"ROUND014_SCORING.json").exists()
assert not (S/"ROUND015_SCORING.json").exists()
print("PASS R19 signed 4 source/CSV outputs, 7 maker color numeric ANSI A326.3 + SGS summaries (not original lab), 13 exact raw lab/surface/tub/POINT/LINEAR requests, no trade substitution/quote/approval")
print("R19_SHA",fp(D/"MANIFEST.json")["sha256"])

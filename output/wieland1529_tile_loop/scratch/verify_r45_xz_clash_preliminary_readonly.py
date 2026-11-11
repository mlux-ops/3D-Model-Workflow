"""Strict read-only independent R45 2D shop blocker source and executable test."""
from pathlib import Path
import json,hashlib,csv,importlib.util
B=Path(__file__).resolve().parents[1]
R=B/"state/ROUND045_XZ_2D_FIELD_COLLISION_FACTORY_WP_PRELIMINARY_NOT_REVIEWED.json"
SHA="bd1952dcd961ccfd8bb8857b6d398067bc716c145cd4066523f1537ef42047cf"
assert hashlib.sha256(R.read_bytes()).hexdigest()==SHA
d=json.loads(R.read_text(encoding="utf-8"))
assert d["round"]==45 and len(d["files"])==3 and d["source_physical_instances"]==8
P=B/"deliverables/integrated-r44-field-jig-wet-architecture-and-13room-procurement/MANIFEST.json"
assert hashlib.sha256(P.read_bytes()).hexdigest()==d["predecessor_R44_FULL_manifest_SHA256"]=="1d7115395e90dd5d0c38b2e8929676f011b0ab897ea4cbfc420f118f2f4d6910"
for f in d["files"]:
 p=B/f["path"];raw=p.read_bytes();assert len(raw)==f["bytes"] and hashlib.sha256(raw).hexdigest()==f["sha256"]
with (B/"research/products/R45_8_UNIT_ACTUAL_NICHE_XZ_OBSTRUCTION_AND_DEPTH_SURVEY_BLANK.csv").open(encoding="utf-8-sig",newline="") as f:rows=list(csv.DictReader(f))
assert len(rows)==8
for r in rows:
 assert r["ACTUAL_niche_X0_in"]=="" and r["ACTUAL_SIGNED_obstruction_rectangles_X0_X1_Z0_Z1"]==""
 for k in ("certified_TRUE_1529_site_survey","plumber_signed_XZ_obstructions","architect_approved_EXISTING_niche_location","maker_signed_individual_WET_WALL_and_NICHE_system","waterproofer_signed_backer_and_membrane","tile_installer_SIGNED_1TO1","owner_approved","purchased","purchase_authorized"):assert r[k]=="FALSE"
script=B/"research/products/R45_FIELD_W3_2D_XZ_NICHE_VALE_GLASS_OBSTRUCTION_SOLVER_SOURCE_ONLY.py"
spec=importlib.util.spec_from_file_location("R45_2D",script)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
base=dict(rows[0]);base.update({"actual_W3_FINISHED_WIDTH_in":"30.48","actual_W3_FINISHED_HEIGHT_in":"93",
 "ACTUAL_niche_X0_in":"7.24","ACTUAL_niche_X1_in":"23.24",
 "ACTUAL_niche_Z0_in":"38","ACTUAL_niche_Z1_in":"50",
 "ACTUAL_left_profile_and_tolerance_in":"0.25","ACTUAL_right_profile_and_tolerance_in":"0.25",
 "ACTUAL_available_niche_backing_depth_in":"5","ACTUAL_required_niche_assembly_depth_in":"4",
 "ACTUAL_SIGNED_obstruction_rectangles_X0_X1_Z0_Z1":"10:18:60:70"})
first=module.evaluate(base)
assert first["status"]=="GEOMETRY_XZ_PASS_SHOP_HOLDS" and not first["purchase_authorized"]
assert first["actual_pipe_glass_obstructions_checked"]==1
base["ACTUAL_SIGNED_obstruction_rectangles_X0_X1_Z0_Z1"]="10:18:42:48"
second=module.evaluate(base)
assert second["status"]=="REJECT_ACTUAL_TWO_DIMENSIONAL_CLASH"
base["ACTUAL_SIGNED_obstruction_rectangles_X0_X1_Z0_Z1"]=""
assert module.evaluate(base)["status"]=="HOLD_NO_SIGNED_2D_PIPE_VALVE_GLASS_SURVEY"
base["ACTUAL_SIGNED_obstruction_rectangles_X0_X1_Z0_Z1"]="NONE"
base["ACTUAL_available_niche_backing_depth_in"]="3"
assert module.evaluate(base)["status"]=="REJECT_ACTUAL_BACKING_DEPTH"
base["ACTUAL_available_niche_backing_depth_in"]="5"
base["ACTUAL_left_profile_and_tolerance_in"]="4.5"
assert module.evaluate(base)["status"]=="REJECT_FINISHED_W3_PIER_MINIMUM"
base["ACTUAL_left_profile_and_tolerance_in"]="0.25"
base["ACTUAL_niche_X1_in"]=""
assert module.evaluate(base)["status"]=="HOLD_REAL_SURVEY_MISSING"
for k in ("actual_TRUE1529_geometry_certified","exact_WET_WALL_NICHE_factory_system_received","original_raw_numerical_LEVEL_vs_POINT_LINEAR_PAN_labs_received","owner_selected_program_changed","owner_approved","architect_approved","plumber_approved","waterproofer_approved","installer_approved","supplier_approved","GC_approved","purchaser_approved","current_supplier_and_GC_bid","material_reserved","purchase_authorized","original_nonPro_Reviewer_DONE","global_DONE"):assert d[k] is False,k
print("PASS R45 3/3 SHA bytes, immutable R44, 8 blank true1529 source unit survey; six synthetic XZ/DEPTH/HOLD tests")
print("PASS X-only overlap above niche now allowed by 2D BUT actual XZ clash REJECT, purchasing always FALSE")
print("R45_SOURCE_RECEIPT_SHA",SHA)

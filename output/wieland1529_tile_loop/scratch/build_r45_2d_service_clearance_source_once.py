"""New substantial R45 X/Z clash source initiation, distinct from R44 full."""
from pathlib import Path
import hashlib,json,csv,io
B=Path(__file__).resolve().parents[1]
R44=B/"deliverables/integrated-r44-field-jig-wet-architecture-and-13room-procurement/MANIFEST.json"
H="1d7115395e90dd5d0c38b2e8929676f011b0ab897ea4cbfc420f118f2f4d6910"
assert hashlib.sha256(R44.read_bytes()).hexdigest()==H
script=B/"research/products/R45_FIELD_W3_2D_XZ_NICHE_VALE_GLASS_OBSTRUCTION_SOLVER_SOURCE_ONLY.py"
assert script.exists()
out=B/"research/products"
sheet=out/"R45_8_UNIT_ACTUAL_NICHE_XZ_OBSTRUCTION_AND_DEPTH_SURVEY_BLANK.csv"
doc=out/"R45_REAL_PIPE_VALVE_GLASS_NICHE_XZ_FACTORY_BACKING_WP_AND_GC_NEXT_CONSTRUCTION_SOURCE.md"
receipt=B/"state/ROUND045_XZ_2D_FIELD_COLLISION_FACTORY_WP_PRELIMINARY_NOT_REVIEWED.json"
assert not sheet.exists() and not doc.exists() and not receipt.exists()
F=("PH-BATH3","PH-BATH4","TX-BATH3","TX-BATH4")
rows=[]
for r in F:
 g=json.loads((B/"rooms"/r/"geometry.json").read_text(encoding="utf-8"))
 for u in g["revit_room_numbers"]:
  rows.append(dict(room=r,physical_copy=u,
   project_location_verified_TRUE_1529="FALSE",
   actual_W3_FINISHED_WIDTH_in="",actual_W3_FINISHED_HEIGHT_in="",
   ACTUAL_niche_X0_in="",ACTUAL_niche_X1_in="",ACTUAL_niche_Z0_in="",ACTUAL_niche_Z1_in="",
   ACTUAL_left_profile_and_tolerance_in="",ACTUAL_right_profile_and_tolerance_in="",
   ACTUAL_available_niche_backing_depth_in="",ACTUAL_required_niche_assembly_depth_in="",
   ACTUAL_SIGNED_obstruction_rectangles_X0_X1_Z0_Z1="",
   certified_TRUE_1529_site_survey="FALSE",plumber_signed_XZ_obstructions="FALSE",
   architect_approved_EXISTING_niche_location="FALSE",
   maker_signed_individual_WET_WALL_and_NICHE_system="FALSE",
   waterproofer_signed_backer_and_membrane="FALSE",
   tile_installer_SIGNED_1TO1="FALSE",owner_approved="FALSE",
   selected_original_rough_or_program_changed="FALSE",
   purchased="FALSE",purchase_authorized="FALSE"))
assert len(rows)==8
s=io.StringIO(newline="")
w=csv.DictWriter(s,list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
sheet_data=s.getvalue().encode("utf-8-sig")
documentation="""# R45 next distinct integrated problem: real W3 two-dimensional service/pipe/glass clearance

The full signed R44 fabrication jig tests actual finish side pier and ONE-dimensional X pipe/glass/valve overlap. That is intentionally conservative. A valve installed entirely ABOVE an actual niche may overlap its horizontal X range while NOT overlapping its X-Z rectangle. A real 1529 signed elevation should avoid falsely forcing tile or niche relocation, but clearance at the niche cavity BACKING DEPTH still must be independently satisfied.

New fail-closed source-only solver evaluates actual certified 1529 wall width and height, actual existing/owner-authorized niche X0/X1/Z0/Z1, LEFT/RIGHT installed trim+tolerance, actual pipe-free cavity depth versus manufacturer-required depth and a list of real signed obstacle rectangles with syntax X0:X1:Z0:Z1 separated by semicolons. It rejects true positive-area rectangle intersections (both X and Z), rejects minimum 3in finished side-pier failures, insufficient real backer depth and out-of-bounds niche, and HOLDS missing real obstacle survey. No simulated PASS is actual construction approval; it always reports purchase_authorized false. A 2D survey still cannot establish full 3D pipe intrusions, permitted valve trim depth, waterproofing or factory niche approvals without physical sectional inspection.

**Distinct building example, synthetic only:** W3=30.48in, H=93in, centered 16in wide/12in tall niche X=7.24..23.24 and Z=38..50. A valve/service exclusion X=10..18, Z=60..70 overlaps X but not Z, so geometry can pass after real signed backing-depth/wet manufacturer evidence. A second physical example X=10..18, Z=42..48 overlaps both dimensions, making niche geometrically REJECT. Equal Z=50 boundary merely touches; waterproof/clearance tolerances must still be added by plumber, architect and installer and may invalidate that boundary condition. Missing depth or signed exclusion map is HOLD.

**Contractor acceptance:** true 1529 architect field tape/level datum and photographs; existing or expressly owner-approved niche and glass/valve position; plumber seals actual service and pipe region, rough and accessible cartridge; waterproofer signs selected manufacturer approved exact wet WALL versus independent niche waterproof/backer/mortar penetration/corner/sill; tile installer signs 1:1 actual factory calibrated tile, grout, movement and trimmed LEFT/RIGHT finished piers; selected PH4 BNX POINT four-plane PAN, PH3/TX3 owner TUB/WALKIN unresolved, TX4 actual Duravit tub Matte White NO tiled PAN and unresolved R42 hydraulic control; independent original exact wet LEVEL and POINT/LINEAR PAN DCOF as applicable; current factory lot/Chicago bid and full GC original paid material/credit/labor before purchaser authority.

This is new R45 source-only 2D clearance engineering, NOT full R45 signed integrated package, current manufacturer installation authorization or original board critic submission. Original 13-room project OPEN, no native 1527 geometry transferred to 1529, no owner/vendor outreach, emails, orders or Revit/Smartsheet/Git changes.
"""
doc_data=(documentation.strip()+"\n").encode("utf-8")
with sheet.open("xb") as f:f.write(sheet_data)
with doc.open("xb") as f:f.write(doc_data)
spec=dict(round=45,date_local="2026-11-06",phase="PRELIMINARY_SOURCE_ONLY_DISTINCT_2D_XZ_NICHE_PIPE_GLASS_SERVICE_CLEARANCE",
 predecessor_R44_FULL_manifest_SHA256=H,focus_rooms=list(F),source_physical_instances=8,
 original_13room_objective_OPEN=True,formal_board_round=17,
 actual_TRUE1529_geometry_certified=False,exact_WET_WALL_NICHE_factory_system_received=False,
 original_raw_numerical_LEVEL_vs_POINT_LINEAR_PAN_labs_received=False,
 owner_selected_program_changed=False,owner_approved=False,architect_approved=False,
 plumber_approved=False,waterproofer_approved=False,installer_approved=False,
 supplier_approved=False,GC_approved=False,purchaser_approved=False,
 current_supplier_and_GC_bid=False,material_reserved=False,purchase_authorized=False,
 original_nonPro_Reviewer_DONE=False,global_DONE=False,
 files=[dict(path=str(p.relative_to(B)).replace("\\","/"),bytes=len(p.read_bytes()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
        for p in (script,sheet,doc)])
receipt.write_bytes((json.dumps(spec,indent=2)+"\n").encode("utf-8"))
print("R45_2D_NEW_SOURCE_FILES",len(spec["files"]),"R45_RECEIPT_SHA",hashlib.sha256(receipt.read_bytes()).hexdigest())

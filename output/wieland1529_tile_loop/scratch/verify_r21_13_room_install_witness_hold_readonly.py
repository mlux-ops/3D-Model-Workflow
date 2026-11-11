"""Read-only 156-row room/wet-assembly witness/owner/GC gate and historical SHA audit."""
from pathlib import Path
import hashlib,csv,json
R=Path(__file__).resolve().parents[1];S=R/"state"
D=R/"deliverables/integrated-r21-install-witness-sequence"
def fp(p):
 b=p.read_bytes();return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
m=json.loads((D/"MANIFEST.json").read_text(encoding="utf-8"))
assert len(m["outputs"])==3 and m["rooms"]==13 and m["evidence_hold_rows"]==156
assert all(fp(D/n)==sig for n,sig in m["outputs"].items())
assert (m["unique_wet_rooms"],m["actual_Duravit_tub_only_rooms"],m["actual_linear_shower_pan_rooms"],m["selected_point_walkin_rooms"],m["owner_held_conditional_POINT_pan_rooms"],m["dry_wood_floor_powder_rooms"],m["shared_primary_floor_WC_rooms"])==(8,3,2,1,2,3,2)
for dref,sha in (
 ("deliverables/integrated-r17/MANIFEST.json",m["original_R17_sha"]),
 ("deliverables/integrated-r18-owner-sample-visual-and-shop/MANIFEST.json",m["original_R18_sha"]),
 ("deliverables/integrated-r19-manufacturer-wet-evidence-grades/MANIFEST.json",m["original_R19_sha"]),
 ("deliverables/integrated-r20-tx-tub-public-retail-and-carton-holds/MANIFEST.json",m["original_R20_sha"]),
 ("state/ROUND014_SUBMISSION.json",m["original_R014_source_sha"]),
 ("state/ROUND015_SUBMISSION.json",m["original_R015_source_sha"])
):
 assert fp(R/dref)["sha256"]==sha,dref
assert m["original_hist_material_4unit_usd"]=="23572.44" and m["original_15pct_waste_in_old_gross_once"]
assert not any(m[x] for x in ("actual_1529_field_verified","actual_inspections_completed","owner_approval","GC_release","procurement_release"))
assert m["R014_scoring"] is None and m["R015_scoring"] is None
with (D/"R21_156_FIELD_INSPECTION_AND_TRADE_WITNESS_HOLD_POINTS.csv").open(encoding="utf-8",newline="") as f:
 rows=list(csv.DictReader(f))
assert len(rows)==156
rooms=json.loads((S/"ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert {x["room"] for x in rows}=={x["id"] for x in rooms}
for r in rooms:
 rr=[x for x in rows if x["room"]==r["id"]]
 assert len(rr)==12 and len({x["sequence_step"] for x in rr})==12,(r["id"],len(rr))
 assert {x["sequence_step"][:2] for x in rr}=={f"{i:02}" for i in range(1,13)}
 assert all(x["room_copy_count"]=="2" for x in rr)
 assert all(x["procurement_release"]=="FALSE" and x["owner_approval_id"]=="" and x["GC_acceptance_id"]=="" and x["purchase_order_ID"]=="" for x in rr)
 assert all(x["actual_1529_verified_dimension_record"]=="" and x["original_lab_certificate_or_test_ID"]=="" for x in rr)
 pan=next(x for x in rr if x["sequence_step"].startswith("05"))
 if r["id"] in ("PH-PRIMARY","TX-PRIMARY"):
  assert "48IN_LINEAR" in pan["applicability"] and "NO" in r["id"]+" NO"
 elif r["id"]=="PH-BATH4":
  assert "4PLANE_SQUARE_POINT" in pan["applicability"]
 elif r["id"] in ("PH-BATH3","TX-BATH3"):
  assert "CONDITIONAL_ONLY_IF_OWNER_WALKIN" in pan["applicability"]
 else:
  assert pan["applicability"]=="N/A_NO_TILED_SHOWER_PAN"
 level=next(x for x in rr if x["sequence_step"].startswith("04"))
 if "POWDER" in r["id"]:
  assert level["applicability"]=="N/A_WOOD_FLOOR"
 elif r["id"].endswith("-WC"):
  assert level["applicability"]=="INHERITED_PARENT_PRIMARY_ONCE"
 else:
  assert level["applicability"]=="REQUIRED_EXACT_RAW_NUMERIC_LEVEL_WET_LAB"
 step2=next(x for x in rr if x["sequence_step"].startswith("02"))
 step3=next(x for x in rr if x["sequence_step"].startswith("03"))
 step6=next(x for x in rr if x["sequence_step"].startswith("06"))
 if "POWDER" in r["id"] or r["id"].endswith("-WC"):
  assert step2["specific_evidence_scope"].startswith("N/A"),r["id"]
  assert step3["specific_evidence_scope"].startswith("N/A"),r["id"]
  assert level["specific_evidence_scope"].startswith("N/A") or level["specific_evidence_scope"].startswith("INHERITED"),r["id"]
 if r["id"] in ("PH-PRIMARY","TX-PRIMARY"):
  assert step3["specific_evidence_scope"].startswith("N/A") and "NO EXTRA PRIMARY SHOWER NICHE" in step3["specific_evidence_scope"]
  assert "48in LINEAR" in step6["specific_evidence_scope"] and "BR73480" in step6["specific_evidence_scope"]
 if r["id"] in ("PH-BATH2","TX-BATH2","TX-BATH4"):
  assert "Duravit TUB" in step6["specific_evidence_scope"] and "no tiled" in step6["specific_evidence_scope"].lower() and "PAN" in step6["specific_evidence_scope"]
 if r["id"] in ("PH-BATH3","TX-BATH3"):
  assert "WALK-IN" in step6["specific_evidence_scope"] and "NOT SELECTED" in step6["specific_evidence_scope"]
  assert "never tub waste" in step6["specific_evidence_scope"]
 if r["id"]=="PH-BATH3":
  assert "Delta DT062412 Chrome" in step6["specific_evidence_scope"]
 if r["id"]=="TX-BATH3":
  assert "Brizo BT062415-BNX Black Onyx" in step6["specific_evidence_scope"]
 if r["id"]=="PH-BATH4":
  assert "BT062415-BNX" in step6["specific_evidence_scope"] and "SQUARE POINT" in step6["specific_evidence_scope"]
 if r["id"]=="TX-POWDER2":
  assert "DECK-mounted" in step6["specific_evidence_scope"] and "UNSELECTED" in step6["specific_evidence_scope"]
 if "BATH" in r["id"] and r["id"] not in ("PH-PRIMARY","TX-PRIMARY"):
  assert "WC" not in level["specific_evidence_scope"],r["id"]
 niche=next(x for x in rr if x["sequence_step"].startswith("03"))
 if r["id"] in ("PH-PRIMARY","TX-PRIMARY","PH-WC","TX-WC","PH-POWDER","TX-POWDER","TX-POWDER2"):
  assert niche["applicability"]=="N/A_NO_WET_NICHE_OR_OWNER_NO_ADDED_PRIMARY_NICHE"
 assert all(x["completed"] in ("FALSE","N/A") for x in rr)
assert not (S/"ROUND014_SCORING.json").exists() and not (S/"ROUND015_SCORING.json").exists()
print("PASS R21 156 actual full 13-room witnessed construction/inspector evidence requests, exact 8 wet/5 dry-WC and 2 linear/1 POINT/2 owner conditional POINT/3 selected tub, 3 signed outputs and all predecessor SHA; no false approvals or actual model claim")
print("R21_SHA",fp(D/"MANIFEST.json")["sha256"])

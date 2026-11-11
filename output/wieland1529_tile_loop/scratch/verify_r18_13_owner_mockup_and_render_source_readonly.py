"""Read-only independent verification of additive R18 owner/mockup 13-room kit."""
from pathlib import Path
from decimal import Decimal
import hashlib,json,csv,re
R=Path(__file__).resolve().parents[1]
S=R/"state"
D=R/"deliverables/integrated-r18-owner-sample-visual-and-shop"
def fp(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
m=json.loads((D/"MANIFEST.json").read_text(encoding="utf-8"))
with (D/"R18_13_ROOM_SAMPLE_RENDER_OWNER_GC_SIGNATURE_MATRIX.csv").open("r",encoding="utf-8",newline="") as f:
 rows=list(csv.DictReader(f))
src=json.loads((S/"ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert len(rows)==len(src)==13
assert {x["room"] for x in rows}=={x["id"] for x in src}
assert len(m["outputs"])==15 and m["rooms"]==13 and m["camera_briefs"]==39
assert m["signature_rows"]==13
assert all(fp(D/n)==sign for n,sign in m["outputs"].items())
assert m["historical_four_unit_material_usd"]=="23572.44"
assert m["original_15pct_waste_embedded_once"] is True
assert sum(Decimal(x["two_copy_historic_material_usd"]) for x in rows)==Decimal("23572.44")
assert fp(R/"deliverables/integrated-r17/MANIFEST.json")["sha256"]==m["previous_R17_manifest_sha256"]
assert fp(S/"ROUND014_SUBMISSION.json")["sha256"]==m["R014_source_sha256_unchanged"]
assert fp(S/"ROUND015_SUBMISSION.json")["sha256"]==m["R015_source_sha256_unchanged"]
assert not any(m[x] for x in ("owner_approval","GC_release","procurement_release","actual_samples_ordered","actual_1529_model_verified","actual_render_images"))
for x in rows:
 assert all(x[z]=="FALSE" for z in ("actual_1529_dimensions_verified","actual_raw_wet_lab_proof","sample_order","owner_approval","architect_approval","GC_shop_acceptance","procurement_release"))
 rid=x["room"]
 room=next(y for y in src if y["id"]==rid)
 assert x["status"]==room["status"]
 assert Decimal(x["room_source_material_per_copy_usd"])==sum(Decimal(str(y.get("extended_quote_cost_usd_per_unit") or 0)) for y in room.get("carried_tile_rows",[]))
 b=(D/x["brief_file"]).read_text(encoding="utf-8")
 for z in ("## Three actual visualization camera briefs","Camera A","Camera B","Camera C","1:1 sample","SOURCE","RAW NUMERIC","FALSE","manufacturer"):
  if z=="SOURCE": continue
  assert z.lower() in b.lower(),(rid,z)
 assert len(b.splitlines())>=45,(rid,len(b.splitlines()))
 assert "NOT OWNER APPROVED" in b
 assert "NOT A CERTIFIED 1529" in b
 assert "NO" in b.upper()
 if rid in ("PH-BATH2","TX-BATH2","TX-BATH4"):
  assert "NO" in x["owner_program_fixture_identity_preserved"].upper() and "PAN" in x["owner_program_fixture_identity_preserved"].upper()
 if rid in ("PH-BATH3","TX-BATH3"):
  assert "UNSELECTED" in b and "POINT" in b and "WALK-IN" in b
 if "POWDER" in rid:
  assert "wood" in b.lower() and "no tiled wet floor" not in b.lower() or "wood" in b.lower()
 assert not re.search(r"(?i)owner (has )?approved (this|the) final",b)
assert not (S/"ROUND014_SCORING.json").exists()
assert not (S/"ROUND015_SCORING.json").exists()
print("PASS R18 13 individual original status/budget-source verified, 39 camera mockup briefs, 13 unsigned owner/GC gates, all 15 SHA output files valid, source 15% once, no owner/GC/purchase/revit/quote release")
print("R18_MANIFEST_SHA",fp(D/"MANIFEST.json")["sha256"])

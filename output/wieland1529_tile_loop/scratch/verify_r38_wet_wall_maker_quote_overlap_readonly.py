"""Strict separate READ ONLY R38 source sign/arithmetic, no write actions."""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import hashlib,csv,json
B=Path(__file__).resolve().parents[1]
R=B/"state/ROUND038_NEXT_DISTINCT_WET_WALL_MAKER_PERMISSION_FULL_FIELD_NICHE_OPENING_CONTRACT_SOURCE_PREPARED_NOT_REVIEWED.json"
SHA="34d5fa02c436cf94d06aa56e662dad27ffc57fbb11b4dd8a9a18a084b03a80f4"
assert hashlib.sha256(R.read_bytes()).hexdigest()==SHA
r=json.loads(R.read_text(encoding="utf-8"))
assert r["round"]==38 and len(r["files"])==5
prev=B/"deliverables/integrated-r37-powder-vanity-factory-finish-plane-dry-wall-mirror-13room-procurement/MANIFEST.json"
assert hashlib.sha256(prev.read_bytes()).hexdigest()==r["predecessor_R37_full_SHA256"]=="985f994993b3b118f9e507fc60309ac3144ca3c7bf3f20c19db10c31adba5c81"
for f in r["files"]:
    data=(B/f["path"]).read_bytes()
    assert len(data)==f["bytes"] and hashlib.sha256(data).hexdigest()==f["sha256"],f
def rows(prefix):
    xs=[f["path"] for f in r["files"] if prefix in f["path"] and f["path"].endswith(".csv")]
    assert len(xs)==1
    with (B/xs[0]).open(encoding="utf-8-sig") as f:return list(csv.DictReader(f))
wall=rows("9_FULL_THREE_WALL")
aperture=rows("36_6_PHYSICAL")
factory=rows("18_WET_WALL")
cost=rows("12_6_PHYSICAL")
assert (len(wall),len(aperture),len(factory),len(cost))==(9,36,18,12)
assert {x["room"] for x in wall}=={"PH-BATH3","PH-BATH4","TX-BATH3"}
assert Counter(x["room"] for x in wall)==Counter({"PH-BATH3":3,"PH-BATH4":3,"TX-BATH3":3})
original=list(csv.DictReader((B/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig")))
assert len(original)==27 and sum(Decimal(x["historic_usd_two_copies"] or "0") for x in original)==Decimal("23572.44")
quote={x["room"]:x for x in original if x["room"] in ("PH-BATH3","PH-BATH4","TX-BATH3") and x["source_surface"]=="wall"}
assert len(quote)==3
base={}
for x in wall:
    face=float(x["source_width_in_UNVERIFIED"])*float(x["source_height_in_UNVERIFIED"])/144
    assert abs(face-float(x["original_FULL_wall_field_before_openings_NET_SF"]))<.00011
    base[x["room"]]=base.get(x["room"],0)+face
    assert x["owner_approved"]==x["current_site_measured"]==x["purchase_authorized"]=="FALSE"
for room,face in base.items():
    q=float(quote[room]["source_gross_sf_one_copy_waste_15pct_once"])
    assert abs(face*1.15-q)<.2
assert len({(x["room"],x["source_physical_copy"],x["source_wall"],x["hypothetical_ONE_existing_NICHE_aperture_width_in"]) for x in aperture})==36
for x in aperture:
    a=float(x["hypothetical_ONE_existing_NICHE_aperture_width_in"])*float(x["hypothetical_existing_aperture_height_in"])/144
    assert abs(float(x["hypothetical_ONE_wall_FIELD_aperture_loss_SF"])-a)<.00011
    assert abs(float(x["theoretical_all_three_walls_after_ONE_aperture_NET_SF"])-(base[x["room"]]-a))<.00011
    assert abs(float(x["theoretical_original_15pct_equivalent_field_aperture_GROSS_SF_NOT_CREDIT"])-a*1.15)<.00011
    assert x["purchase_authorized"]==x["GC_payable_credit_or_change_order_approved"]=="FALSE"
assert Counter(x["room"] for x in factory)==Counter({"PH-BATH3":6,"PH-BATH4":6,"TX-BATH3":6})
assert all(x["owner_WALL_substitution_approved"]==x["maker_written_permission_verified"]==x["purchase_authorized"]=="FALSE" for x in factory)
assert all(x["selected_actual_owner_program_changed"]=="FALSE" for x in factory)
assert len(cost)==12
for x in cost:
    q=quote[x["room"]]
    rate=Decimal(q["historic_usd_two_copies"])/(Decimal(q["source_gross_sf_one_copy_waste_15pct_once"])*2)
    assert abs(float(x["old_BLENDED_wall_material_ONLY_RATE_per_GROSS_SF"])-float(rate))<.00011
    assert abs(float(x["source_material_only_value_of_one_aperture_not_paid_credit_USD"])-round(float(rate)*1.15,2))<.011
    assert x["pay_approved_CHANGE_ORDER_or_savings"]==x["owner_substitution_approved"]==x["purchase_authorized"]=="FALSE"
assert all(r[k] is False for k in ("source_true_1529_measurements_verified","maker_wet_WALL_missing_permissions_solved","owner_tub_walkin_program_changed","current_raw_measured_numeric_wet_LEVEL_POINT_labs_received","current_chicago_supplier_lot_case_bid","GC_signed_CO","original_four_specialist_reports_complete","independent_reviewer_accepted","owner_approved","purchase_authorized","global_DONE"))
print("PASS R38 5/5 SHA/byte exact R37 signed predecessor, source 9 original W1-W3 geometry math")
print("PASS R38 36 one-only opening, 18 individual wet WALL maker, 12 historic old-rate/GC installed source, release false")
print("PASS original 27 materials and $23572.44 15pct once, programs unchanged, no actual 1529 field or numeric wet lab")
print("R38_RECEIPT_SHA",SHA)

"""Independent local READ-ONLY integrity and arithmetic verifier for signed R34."""
import csv,hashlib,json
from pathlib import Path
from collections import Counter
from decimal import Decimal
B=Path(__file__).resolve().parents[1]
receipt=B/"state/ROUND034_DISTINCT_ORIGINAL_PRIMARY_WC_POINT_LINEAR_LEVEL_PAN_SOURCE_PREPARED_NOT_REVIEWED.json"
hash_expected="c00f011dfb83ad27360c2caebd7038a60caac4ba59647df51a6dea1c65b4ec22"
assert hashlib.sha256(receipt.read_bytes()).hexdigest()==hash_expected
r=json.loads(receipt.read_text(encoding="utf-8"))
assert hashlib.sha256((B/"deliverables/integrated-r33-three-duravit-tub-hydraulic-tile-quantity-and-13room-GC/MANIFEST.json").read_bytes()).hexdigest()==r["predecessor_R33_full_SHA256"]=="a8449c27730d790b6cc620f89c2e68dcb1d0ad10dd0ea29809bcdb0b3544a01e"
assert len(r["files"])==5
for f in r["files"]:
    b=(B/f["path"]).read_bytes()
    assert len(b)==f["bytes"] and hashlib.sha256(b).hexdigest()==f["sha256"]
def rows(fragment):
    files=[x for x in r["files"] if fragment in x["path"] and x["path"].endswith(".csv")]
    assert len(files)==1
    with (B/files[0]["path"]).open(encoding="utf-8-sig") as f:return list(csv.DictReader(f))
area=rows("18_SELECTED_SHOWER")
lab=rows("12_PHYSICAL")
drain=rows("6_SELECTED_BRIZO")
wc=rows("4_WC_PARENT")
assert (len(area),len(lab),len(drain),len(wc))==(18,12,6,4)
assert {x["room"] for x in area}=={"PH-PRIMARY","TX-PRIMARY","PH-BATH4"}
assert Counter(x["branch"] for x in area)==Counter({
  "A_ORIGINAL_PARENT_ROOM_AREA_INCLUDES_SHOWER_PAN":6,
  "B_ORIGINAL_PARENT_ROOM_AREA_EXCLUDES_SHOWER_PAN":6,
  "C_SHOWER_PAN_BOUNDARY_UNCONFIRMED_NO_ORDER":6})
for x in area:
    source=float(x["original_parent_room_floor_area_SF_UNVERIFIED"])
    w=float(x["original_WC_area_SOURCE_inherited_once_SF"])
    rect=float(x["original_source_selected_shower_footprint_rect_SF_UNVERIFIED"])
    old=float(x["original_historic_floor_GROSS_SF_one_copy_15pct_included"])
    assert abs(float(x["original_room_plus_WC_area_times_prior_1point15"])-(source+w)*1.15)<.00011
    assert abs(float(x["historical_quoted_minus_source_rebuilt_gross_SF"])-(old-(source+w)*1.15))<.00011
    if x["branch"].startswith("A"):
        assert abs(float(x["hypothetical_distinct_LEVEL_NET_including_WC_once_SF"])-(source-rect+w))<.00011
    if x["branch"].startswith("B"):
        assert abs(float(x["hypothetical_distinct_LEVEL_NET_including_WC_once_SF"])-(source+w))<.00011
    assert x["one_WC_tile_order_standalone"]==x["owner_signed"]==x["purchase_authorized"]=="FALSE"
assert len({(x["room"],x["physical_source_room"],x["role"]) for x in lab})==12
assert all(x["raw_original_measured_numeric_wet_DCOF"]=="" and x["other_surface_lab_interchangeable"]=="FALSE" and x["purchase_authorized"]=="FALSE" for x in lab)
assert len({(x["room"],x["source_physical_room"]) for x in drain})==6
assert all(x["actual_true_1529_shower_polygon_and_slab_thickness"]=="" and x["approved_factory_point_or_linear_bonding_and_collar_system"]=="FALSE" and x["purchase_authorized"]=="FALSE" for x in drain)
assert len({(x["parent_room"],x["parent_physical_room"]) for x in wc})==4
assert all(x["parent_and_wc_original_floor_paid_once"]=="TRUE" and x["supplier_additional_WC_purchase"]=="FALSE" and x["purchase_authorized"]=="FALSE" for x in wc)
old=list(csv.DictReader((B/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig")))
assert len(old)==27 and sum(Decimal(x["historic_usd_two_copies"] or 0) for x in old)==Decimal("23572.44")
assert all(r[k] is False for k in ("true_1529_native_geometry_certified","exact_original_raw_wet_lab_received","confirmed_level_pan_order_quantities","WC_second_purchase","selected_hydraulic_drain_and_original_program_changed","purchase_authorized","global_DONE"))
print("PASS R34 SOURCE 5/5 signed SHA+bytes, 18 mutually exclusive source area/WC/PAN cases, 12 individual lab roles")
print("PASS 6 chosen Brizo rough/membrane witnesses, 4 inherited WC floor no-double-order, original $23572.44 unchanged")
print("R34_SOURCE_RECEIPT_SHA256",hash_expected)

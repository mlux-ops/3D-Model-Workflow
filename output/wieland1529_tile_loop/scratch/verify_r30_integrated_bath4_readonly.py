"""R30 full technical package independent READ-ONLY verification. Never writes files."""
from __future__ import annotations
import csv
import hashlib
import json
from decimal import Decimal
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
OUT=BASE/"deliverables"/"integrated-r30-caviar-soho-niche-plane-tub-point-and-13room-procurement"
M=OUT/"MANIFEST.json"
manifest=json.loads(M.read_text(encoding="utf-8"))
file_rows=manifest["files"]
assert len(file_rows)==19, ("signed file count",len(file_rows))
assert len(list(OUT.iterdir()))==20
for f in file_rows:
    b=(OUT/f["relative_path"]).read_bytes()
    assert len(b)==f["bytes"],f["relative_path"]
    assert hashlib.sha256(b).hexdigest()==f["sha256"],f["relative_path"]
digest=hashlib.sha256(M.read_bytes()).hexdigest()
assert digest=="5293130e57334ad30a2355b8ad02db3cfb9d7fc73ed528a1171e5632b652b23a"

def rows(filename):
    with (OUT/filename).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

names={f["relative_path"] for f in file_rows}
tables={n:rows(n) for n in names if n.endswith(".csv")}
counts={n:len(v) for n,v in tables.items()}
def table_prefix(fragment):
    found=[v for n,v in tables.items() if fragment in n]
    assert len(found)==1,fragment
    return found[0]

original=table_prefix("27_ORIGINAL_HISTORICAL")
assert len(original)==27
assert sum(Decimal(x["original_two_copy_material_ONLY_USD"]) for x in original)==Decimal("23572.44")
assert sum(x["original_unpriced_niche_REFERENCE_NO_SCOPE_NO_ORDER"]=="TRUE" for x in original)==2
assert len({x["source_row_id"] for x in original})==27
assert all(x["purchase_authorized"]=="FALSE" and x["owner_signed"]=="FALSE" for x in original)
assert all(x["original_SOURCE_ROW_UNCHANGED"]=="TRUE" for x in original)

old=list(csv.DictReader((BASE/"deliverables"/"integrated-r17"/"R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig",newline="")))
assert len(old)==27
idx={r["source_row_id"]:r for r in old}
for x in original:
    r=idx[x["source_row_id"]]
    assert x["room"]==r["room"] and x["original_source_surface"]==r["source_surface"]
    assert Decimal(x["original_two_copy_material_ONLY_USD"])==Decimal(r["historic_usd_two_copies"] or "0")
    assert Decimal(x["original_gross_SF_one_copy_15pct_already_once"])==Decimal(r["source_gross_sf_one_copy_waste_15pct_once"] or "0")

W=list(csv.DictReader((BASE/"deliverables"/"integrated-r17"/"R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv").open(encoding="utf-8-sig",newline="")))
assert len(W)==25
trade_original=list(csv.DictReader((BASE/"deliverables"/"integrated-r24-room-branch-shop-quantity-and-owner-decisions"/"R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv").open(encoding="utf-8-sig",newline="")))
assert len(trade_original)==65

elev=table_prefix("84_W1_W3_FACTORY")
assert len(elev)==84
assert set(r["room"] for r in elev)=={"PH-BATH4","TX-BATH4"}
assert set(r["wall"] for r in elev)=={"W1","W3"}
assert all(r["true_1529_field_verified"]=="FALSE" and r["joint_maker_APPROVED"]=="UNVERIFIED" and r["purchase_authorized"]=="FALSE" for r in elev)
for r in elev:
    w=float(r["source_width_in_UNVERIFIED"])
    n=int(r["full_middle_tiles"]); t=float(r["manufacturer_face_length_on_this_axis_in"]); j=float(r["joint_in_ILLUSTRATIVE"])
    end=(w-n*t-(n+1)*j)/2
    assert abs(end-float(r["balanced_end_face_each_in"]))<0.00011,r
assert any(r["product"].startswith("CAVIAR") and r["manufacturer_face_length_on_this_axis_in"]=="8.1250" for r in elev)
assert any(r["product"].startswith("CAVIAR") and r["manufacturer_face_length_on_this_axis_in"]=="1.7500" for r in elev)

niches=table_prefix("144_NICHE_APERTURE")
assert len(niches)==144
assert all(r["owner_approved"]=="FALSE" and r["purchase_authorized"]=="FALSE" for r in niches)
assert all(r["true_field_width_position_riser_and_valve_clearance"]=="FALSE" for r in niches)
for r in niches:
    width=float(r["niche_opening_width_in_HYPOTHETICAL"])
    height=float(r["niche_opening_height_in_HYPOTHETICAL"])
    depth=float(r["niche_reveal_depth_in_HYPOTHETICAL"])
    wall=float(r["source_W3_width_in_UNVERIFIED"])
    j=float(r["proposed_joint_in_UNAPPROVED"])
    aperture=width*height/144
    sides=2*height*depth/144
    top=width*depth/144
    net=aperture+sides+2*top
    assert abs(aperture-float(r["one_field_wall_opening_deduct_ONCE_SF"]))<0.00011
    assert abs(aperture-float(r["separate_niche_back_SF"]))<0.00011
    assert abs(sides-float(r["two_side_returns_SF"]))<0.00011
    assert abs(top-float(r["niche_top_SF"]))<0.00011
    assert abs(top-float(r["niche_sill_SF"]))<0.00011
    assert abs(net-float(r["independent_niche_face_NET_SF_NO_WASTE"]))<0.00011
    assert abs((wall-width-2*j)/2-float(r["W3_side_pier_each_in_PROVISIONAL"]))<0.00011
    assert r["min_3in_pier"]==("PASS_PROVISIONAL" if (wall-width-2*j)/2>=3 else "FAIL_PROVISIONAL")

offcuts=table_prefix("72_PH4_TX4")
assert len(offcuts)==72 and all(r["purchase_authorized"]=="FALSE" for r in offcuts)
cases=table_prefix("13_SAME_LOT_HISTORIC")
assert len(cases)==13 and all(r["purchase_authorized"]=="FALSE" for r in cases)
assert all(int(r["pooled_whole_cartons_if_same_approved_LOT"])<=int(r["separately_rounded_four_receivers_whole_cartons"]) for r in cases)
assert sum(x["case_evidence_class"].startswith("ARTO_2026_GENERIC") for x in cases)==1

maker=table_prefix("10_MANUFACTURER")
assert len(maker)==10
assert any(x["exact_named_product"]=="Cortar Bone Ribbed 24x48 Relief" and "NO_WET_AREAS_LISTED" in x["individual_wet_permission_and_limits"] for x in maker)
assert any(x["exact_named_product"]=="Soho Ivory 2x10 Glossy" and "WET_AREAS" in x["individual_wet_permission_and_limits"] for x in maker)
assert any(x["exact_named_product"]=="Soho Black 2x10 Glossy" and "WET_AREAS" in x["individual_wet_permission_and_limits"] for x in maker)
assert any(x["exact_named_product"].startswith("72411701") and "PRESSURE_BALANCE" in x["individual_wet_permission_and_limits"] for x in maker)

tiers=table_prefix("6_PH4_TX4")
assert len(tiers)==6 and {x["tier"] for x in tiers}=={"GOOD","BETTER","BEST"}
assert all(("BT062415-BNX" in r["nonnegotiable_owner_fixture_program"] if r["room"]=="PH-BATH4" else
            ("Duravit" in r["nonnegotiable_owner_fixture_program"] and
             "BT062415" not in r["nonnegotiable_owner_fixture_program"])) for r in tiers)

rec=table_prefix("4_ACTUAL_ROOM_COPIES")
assert len(rec)==4
assert {r["source_room_copy"] for r in rec}=={"311A","311B","007A","007B"}
assert all(r["purchase_authorized"]=="FALSE" for r in rec)
geom=table_prefix("2_BATH4_W1W2W3")
assert len(geom)==2
ph=next(x for x in geom if x["room"]=="PH-BATH4")
assert abs(float(ph["W1_W2_W3_full_field_geometric_SF_before_openings"])-93.24)<.0001
assert ph["original_source_107_2_times_two_214_4_diagnostic"].startswith("ORIGINAL_GROSS_TWO_COPIES_214.4")

releases=table_prefix("13_ROOM_ORIGINAL_SOURCE_PROGRAM")
assert len(releases)==13
assert {x["room"] for x in releases}=={x["id"] for x in json.loads((BASE/"state"/"ROOMS.json").read_text(encoding="utf-8"))["rooms"]}
assert all(x["purchase_release"]==x["material_reservation"]==x["owner_selected_material_and_program_signed"]=="FALSE" for x in releases)
assert "FOUR_PLANE_PAN" in next(x for x in releases if x["room"]=="PH-BATH4")["independent_exact_RAW_numeric_wet_SLOPED_PAN_test"]
assert next(x for x in releases if x["room"]=="TX-BATH4")["independent_exact_RAW_numeric_wet_SLOPED_PAN_test"]=="N_A_TUB_OR_NO_SHOWER_PAN"
assert next(x for x in releases if x["room"]=="PH-POWDER")["original_exact_RAW_numeric_wet_LEVEL_test"]=="N_A_WOOD_FLOOR"
assert next(x for x in releases if x["room"]=="TX-POWDER2")["original_exact_RAW_numeric_wet_LEVEL_test"]=="N_A_WOOD_FLOOR"

trades=table_prefix("104_EIGHT_TRADE")
assert len(trades)==104
assert all(x["purchase_authorized"]==x["material_or_service_release"]=="FALSE" for x in trades)
assert set(x["trade"] for x in trades)=={"OWNER","ARCHITECT","PLUMBER","WATERPROOFING","TILE_INSTALLER","SUPPLIER","GC_ESTIMATOR","PURCHASER"}
normal=table_prefix("13_ROOM_TWO_COPY_HISTORICAL")
assert len(normal)==13
assert sum(Decimal(x["original_material_ONLY_USD_two_copies"]) for x in normal)==Decimal("23572.44")
assert all(x["purchase_authorized"]=="FALSE" for x in normal)
samples=table_prefix("12_ACTUAL_ROOM_INSTANCE")
assert len(samples)==12 and all(x["image_generated"]==x["physical_sample_obtained"]==x["purchase_authorized"]=="FALSE" for x in samples)
future=table_prefix("45_NEXT_CONSEQUENTIAL")
assert len(future)==45 and all(x["release"]=="FALSE" and x["technical_gate_closed"]=="FALSE" for x in future)

prior=manifest["immutable_predecessor_SHA256"]
assert prior["R029"]=="d3cf560c43c970e172cb2ebec187ebbc1b25472a2de86398a807cfca8300ef70"
assert prior["R030_preliminary_source_only"]=="b0afd03cd5f471234fceebbcc361ea769d9c0f1ccfaa77569bb40191ae3be604"
prevfile=BASE/"deliverables"/"integrated-r29-sandstone-niche-shared-cutstock"/"MANIFEST.json"
assert hashlib.sha256(prevfile.read_bytes()).hexdigest()==prior["R029"]
prevsrc=BASE/"state"/"ROUND030_NEXT_SOURCE_ONLY_CAVIAR_VS_SOHO_EVIDENCE_PREPARED_NOT_REVIEWED.json"
assert hashlib.sha256(prevsrc.read_bytes()).hexdigest()==prior["R030_preliminary_source_only"]
for n in range(12,30):
    matching=[d for d in (BASE/"deliverables").glob(f"integrated-r{n}*")
              if (d/"MANIFEST.json").is_file() and d.name!="integrated-r17-numeric-product-leads"]
    assert len(matching)==1,(n,matching)
    key=f"R{n:03d}_integrated_MANIFEST"
    assert hashlib.sha256((matching[0]/"MANIFEST.json").read_bytes()).hexdigest()==prior[key],key
fix=BASE/"state"/"ROUND030_MANIFEST_LOCAL_QA_PREDECESSOR_CHAIN_FIX1.json"
fix_data=json.loads(fix.read_text(encoding="utf-8"))
assert fix_data["new_sha256"]==digest
assert fix_data["original_19_R30_file_SHA256_and_bytes_unchanged"] is True
assert manifest["purchase_authorized"] is False and manifest["global_13_room_DONE"] is False
assert manifest["independent_nonpro_reviewer_accepted"] is False
print("PASS R30 INDEPENDENT READ-ONLY: 19/19 signed outputs and bytes; 13 room/27 historic source/25 original W/65 original trade, 104 new staged trades")
print("PASS R30 84 calibrated/nominal modules; 144 independently summed aperture/back/returns/sill; 72 offcuts; 13 nonorder case sensitivities")
print("PASS R30 PH4 WALKIN BT062415-BNX four-plane POINT vs TX4 DURAVIT tub NO PAN; original $23572.44 15pct once; owner/GC/PO/reviewer FALSE")
print("MANIFEST_SHA256",digest)

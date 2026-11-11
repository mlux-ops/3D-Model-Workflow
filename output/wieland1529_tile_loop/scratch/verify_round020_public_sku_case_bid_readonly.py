"""Read-only seven-source manufacturer-versus-retail SKU specificity and tub-only release gate audit."""
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
import csv,json,hashlib
R=Path(__file__).resolve().parents[1];S=R/"state"
D=R/"deliverables/integrated-r20-tx-tub-public-retail-and-carton-holds"
def fp(p):
 b=p.read_bytes();return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
m=json.loads((D/"MANIFEST.json").read_text(encoding="utf-8"))
assert m["public_data_rows"]==7 and m["two_tub_floor_conditional_release_rows"]==2
assert len(m["outputs"])==4 and all(fp(D/k)==v for k,v in m["outputs"].items())
assert m["source_material_four_unit_usd"]=="23572.44" and m["original_source_15pct_gross_once"]
assert m["R014_scoring"] is None and m["R015_scoring"] is None
assert not any(m[k] for k in ("current_verified_Chicago_exact_stock","actual_install_bid","actual_RAW_measured_wet_LEVEL_lab_available","owner_approval","GC_release","procurement_release"))
assert fp(R/"deliverables/integrated-r17/MANIFEST.json")["sha256"]==m["R17_signed_manifest_sha"]
assert fp(R/"deliverables/integrated-r18-owner-sample-visual-and-shop/MANIFEST.json")["sha256"]==m["R18_signed_manifest_sha"]
assert fp(R/"deliverables/integrated-r19-manufacturer-wet-evidence-grades/MANIFEST.json")["sha256"]==m["R19_signed_manifest_sha"]
assert fp(S/"ROUND015_SUBMISSION.json")["sha256"]==m["R015_original_frozen_submission_sha"]
with (D/"R20_7_PUBLIC_MAKER_VS_RETAIL_CODE_ORIGIN_JOINT_CARTON_PRICE_SOURCES.csv").open(encoding="utf-8",newline="") as f:
 evidence=list(csv.DictReader(f))
assert len(evidence)==7
assert all(x["quote_is_current_Chicagoland_supplier_bid"]=="FALSE" and x["verified_stock_lot_eta"]=="FALSE" and x["actual_1529_job_carton_confirmed"]=="FALSE" for x in evidence)
kc=next(x for x in evidence if x["public_or_exact_SKU"]=="KC041224J1PV")
assert kc["public_retail_usd_per_case"] if "public_retail_usd_per_case" in kc else True
assert Decimal(kc["published_case_price_usd"])==Decimal("59.29")
assert Decimal(kc["published_case_sf"])==Decimal("17.49")
assert (Decimal(kc["published_case_price_usd"])/Decimal(kc["published_case_sf"])).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)==Decimal("3.39")
el=next(x for x in evidence if x["public_or_exact_SKU"]=="EL301224J1PV")
assert el["published_case_sf"]=="17.49" and el["published_pieces_case"]=="8"
assert "CONFLICTS" in el["published_country_of_origin"]
assert "CONFLICTS" in el["published_grout_recommendation"]
assert "RETAILER SELF-CONTRADICTION" in el["source_reliability"]
assert "17.49 SF/8 = 2.18625 SF EACH" in el["source_reliability"]
assert "SUPPRESS any use as case yield" in el["source_reliability"]
assert "cannot be order basis" in el["size_specific_to_current_project"]
assert "MANDATORY PACKAGING HARD HOLD" in (D/"R20_PUBLIC_ORDER_CODE_CARTON_ORIGIN_AND_RETAIL_VARIANT_CAVEATS.md").read_text(encoding="utf-8")
assert all(x["room"] in ("TX-BATH2","TX-BATH4","TX-BATH2/TX-BATH4") for x in evidence)
with (D/"R20_TX2_TX4_CONDITIONAL_LEVEL_FLOOR_NET_CASE_AND_GC_BID_GATES.csv").open(encoding="utf-8",newline="") as f:
 gates=list(csv.DictReader(f))
assert len(gates)==2 and {x["room"] for x in gates}=={"TX-BATH2","TX-BATH4"}
assert {x["room"]:x["original_quote_floor_gross_SF_per_copy_with_15pct_once"] for x in gates}=={"TX-BATH2":"43.7","TX-BATH4":"44.3"}
assert {x["room"]:x["original_material_floor_usd_per_copy"] for x in gates}=={"TX-BATH2":"294.98","TX-BATH4":"299.02"}
for x in gates:
 assert "NO tiled shower PAN" in x["actual_selected_fixture"]
 assert all(x[f]=="" for f in ("actual_verified_1529_net_LEVEL_floor_SF","actual_ORDERABLE_full_case_quantity","current_Chicago_supplier_material_bid_ID","current_complete_installed_waterproof_labor_GC_bid_ID","signed_owner_room_cap"))
 assert all(x[f]=="FALSE" for f in ("owner_signature","GC_signature","procurement_release"))
assert not (S/"ROUND014_SCORING.json").exists() and not (S/"ROUND015_SCORING.json").exists()
print("PASS R20 7 independently categorized public maker/retailer product/size variants; two tub-only source floor gross/cost controls, no false installed supplier price/actual case/order, all 4 output SHA, predecessors preserved")
print("R20_SHA",fp(D/"MANIFEST.json")["sha256"])

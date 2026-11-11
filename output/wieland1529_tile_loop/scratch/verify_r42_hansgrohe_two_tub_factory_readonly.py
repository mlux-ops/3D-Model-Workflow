"""Strict independent READ ONLY R42 original Hansgrohe tub control compatibility audit."""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import hashlib,json,csv
B=Path(__file__).resolve().parents[1]
D=B/"deliverables/integrated-r42-matte-white-thermostat-diverter-tub-spout-field-rough-wet-wall-GC"
SHA="1659fb4bb1bb57b1a26e8ab17ad36ce40ed49ba41ebd33b6fb45807e21c94712"
M=D/"MANIFEST.json"
assert hashlib.sha256(M.read_bytes()).hexdigest()==SHA
m=json.loads(M.read_text(encoding="utf-8"))
assert m["round"]==42 and len(m["files"])==6 and len(list(D.iterdir()))==7
for f in m["files"]:
 data=(D/f["path"]).read_bytes()
 assert len(data)==f["bytes"] and hashlib.sha256(data).hexdigest()==f["sha256"],f["path"]
assert hashlib.sha256((B/"deliverables/integrated-r41-four-wet-bath-architectural-composition-and-field-shop-13room/MANIFEST.json").read_bytes()).hexdigest()==m["predecessor_signed_file_hashes"]["R41_FULL"]
assert m["predecessor_signed_file_hashes"]["R41_FULL"]=="7d14ca7d0acd29b6c85ffcaa90a4d6beecb20928fe1fd200073f67966a9fd3f0"
for src in ("R39_FULL","R40_FULL","R37_FULL","R33_FULL"):
 assert src in m["predecessor_signed_file_hashes"] and len(m["predecessor_signed_file_hashes"][src])==64
def rows(prefix):
 p=[f["path"] for f in m["files"] if f["path"].startswith(prefix) and f["path"].endswith(".csv")]
 assert len(p)==1,(prefix,p)
 with (D/p[0]).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def false(rs,keys):
 for row in rs:
  for k in keys:assert row[k]=="FALSE",(row.get("room"),k,row[k])
facts=rows("R42_7_ORIGINAL")
assert len(facts)==7
by={x["evidence_id"]:x for x in facts}
assert set(by)=={"selected_thermo","selected_spout","spout_specific_install","metal_drop","conditional_plain_spout","conditional_pressure_balance_family","rough"}
assert "pressure-balance valve ONLY" in by["selected_spout"]["manufacturer_specific_fact"]
assert "8-18in" in by["metal_drop"]["manufacturer_specific_fact"] and "ONE elbow" in by["metal_drop"]["manufacturer_specific_fact"]
assert "NO PEX" in by["metal_drop"]["manufacturer_specific_fact"]
assert all(x["official_manufacturer_URL"].startswith("https://") for x in facts)
false(facts,("actual_OWNER_change_signed","actual_factory_system_compatibility_final","purchasing_authorized"))
routes=rows("R42_12_FOUR")
assert len(routes)==12
assert Counter(x["room"] for x in routes)==Counter({"PH-BATH2":6,"TX-BATH4":6})
assert Counter(x["option"] for x in routes)==Counter({"A_KEEP_THERMOSTAT_SWAP_SPOUT_ONLY":4,"B_KEEP_DIVERTER_SPOUT_CHANGE_MIXER":4,"C_FACTORY_COMPLETE_REPLUMB_STAGED":4})
assert len({(x["room"],x["physical_copy"],x["option"]) for x in routes})==12
assert all(x["current_selected_trim"].startswith("15758701") and "72411701" in x["current_selected_diverter_spout"] and "01850181" in x["current_selected_rough"] for x in routes)
assert all(x["original_Duravit_TUB_NO_tiled_PAN"]=="TRUE" and x["independent_shower_PAN_numeric_lab"]=="N_A_TUB" for x in routes)
false(routes,("current_factory_supported_assembled_rough_trim_spout","owner_approved","plumber_approved","architect_approved","waterproof_approved","GC_approved","purchase_authorized"))
physical=rows("R42_24_SIX")
assert len(physical)==24
assert Counter(x["room"] for x in physical)==Counter({"PH-BATH2":12,"TX-BATH4":12})
assert len({(x["room"],x["physical_copy"],x["trade_hold"]) for x in physical})==24
assert all(x["factory_min_drop_in"]=="8" and x["factory_max_drop_in"]=="18" for x in physical)
assert all(x["manufacturer_allowed_MATERIAL_METAL_NO_PEX_and_one_elbow"]=="TRUE" for x in physical)
assert all(x["original_floors_RAW_numeric_wet_LEVEL_lab"]=="MISSING" and x["original_shower_PAN_test"]=="N_A_TUB" for x in physical)
false(physical,("owner_choice_signed","manufacturer_factory_installed_system_approved","plumber_signed","architect_signed","WP_tile_signed","GC_change_order_signed","purchase_authorized"))
z=rows("R42_16_TWO")
assert len(z)==16 and Counter(x["room"] for x in z)==Counter({"PH-BATH2":8,"TX-BATH4":8})
assert all("BACKER+MEMBRANE" in x["formula_finished_wall_from_stud"] for x in z)
false(z,("maker_rough_sleeve_and_ESCUTCHEON_sealing_gasket_depth_accepted","original_tub_flange_preserved_and_sealed","new_owner_rough_spout_change_selected","purchase_authorized"))
release=rows("R42_13_ROOM")
original=json.loads((B/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert len(release)==13 and {x["room"] for x in release}=={x["id"] for x in original}
assert all(x["formal_board_round"]=="17" for x in release)
assert all(x["R42_MatteWhite_TUB_high_risk"]=="PB_ONLY_DIVERTER_VS_THERMOSTATIC_HOLD" for x in release if x["room"] in ("PH-BATH2","TX-BATH4"))
false(release,("owner_selected_rough_or_finish_CHANGED","owner_approved","architect_approved","plumber_approved","waterproof_approved","installer_approved","supplier_approved","GC_approved","purchaser_approved","purchase_authorized"))
old=list(csv.DictReader((B/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig")))
assert len(old)==27 and sum(Decimal(x["historic_usd_two_copies"] or "0") for x in old)==Decimal("23572.44")
assert m["original_13room_count"]==13 and m["original_27_material_rows"]==27 and m["original_USD_material_only"]=="23572.44"
for k in ("actual_1529_spout_DROP_measurement_verified","exact_original_selected_current_trim_and_rough_AS_BUILT_verified","correct_FACTORY_complete_thermo_or_PB_spout_assembly_signed","owner_selects_changed_fixture_or_rough","source_fixture_silently_substituted","current_raw_numeric_LEVEL_wet_lab_received","physical_one_to_one_mockup_and_commission_completed","actual_paid_credit_current_Chicago_supplier_or_installed_GC_bid","original_four_specialists_complete","original_Reviewer15_DONE","owner_approved","architect_approved","plumber_approved","waterproof_approved","tile_approved","supplier_approved","GC_approved","purchaser_approved","purchase_authorized","global_DONE"):
 assert m[k] is False,k
assert (D/"START_HERE_R42_HANSGROHE_TWO_DURAVIT_TUB_FACTORY_DROP_AND_MATTE_WHITE_CORRECTION_BOOK.md").exists()
print("PASS R42 strict READ ONLY 6/6 SHA+bytes, immutable original R41 predecessor")
print("PASS manufacturer PB-only spout vs selected thermostat conflict, 8-18in metal nonPEX single elbow 24 physical shops")
print("PASS 4 source Duravit physical units x3 mutually exclusive correction routes, 16 finish planes and 13 room releases all FALSE")
print("PASS old original 27 rows USD23572.44 once, original LAB FLOOR missing, shower PAN N/A for both TUB")
print("R42_MANIFEST_SHA",SHA)

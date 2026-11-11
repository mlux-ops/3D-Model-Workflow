from pathlib import Path
import csv,json,hashlib,math
R=Path(__file__).resolve().parents[1]
O=R/"deliverables/integrated-r10";O.mkdir(exist_ok=True,parents=True)
r=json.loads((R/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert len(r)==13
maker={"PH-PRIMARY":"flat ELM Cortar Bone wet; HNC6615 level & Prime RL21 linear pan pending",
"PH-BATH2":"ELM Tones Sapphire wet PASS; HNC6615 level floor alternative pending",
"PH-BATH3":"ELM Tones Sandstone wet if owner program/Delta drain reconciled",
"PH-BATH4":"flat ELM Cortar Bone/Soho wet; HNC6615 LEVEL and HNC6715 point-pan conditional",
"PH-POWDER":"Earth Lines source feature dry wall",
"PH-WC":"inherits PH Primary tested level floor; no own order",
"TX-PRIMARY":"flat Clay wet; HNC6615 level/Prime RL21 linear pan pending",
"TX-BATH2":"Copper/Sandstone maker wet; HNC6615 level floor pending",
"TX-BATH3":"no new material spec until owner tub/shower program",
"TX-BATH4":"flat Charcoal/Soho wet; HNC6615 level floor pending",
"TX-POWDER":"Haze Camel/Wheat 70:30 dry wall board selection only",
"TX-POWDER2":"Indigo 6x6 dry wall retained; basin unselected",
"TX-WC":"inherits TX Primary tested level floor; no own order"}
owner={"PH-PRIMARY":"Select/approve sample scheme only after raw wet floor/pan tests, no niche",
"PH-BATH2":"Approve Sapphire retained versus alternative palette; source tub remains",
"PH-BATH3":"Determine basin and tub/point drain consistency",
"PH-BATH4":"Confirm 35 versus 27SF and original Soft/Anti-Slip finish issue",
"PH-POWDER":"Approve Earth Lines sample, mirror/trim and metal grout",
"PH-WC":"Approve inherited Primary floor only following wet test",
"TX-PRIMARY":"Approve flat Clay and linear mosaic after exact tests, NO NICHE",
"TX-BATH2":"Select basin only after owner review, confirm floor palette",
"TX-BATH3":"Decide tub versus shower before further pan/mosaic specification",
"TX-BATH4":"Approve flat Charcoal/Soho with tub, HNC level alternative",
"TX-POWDER":"Approve exact Camel/Wheat dry wall ratio and separate cartons",
"TX-POWDER2":"Select basin and mirror/backing, keep deck faucet",
"TX-WC":"Approve inherited Primary level floor only following wet test"}
rows=[];originals=[];tasks=[]
for x in r:
 rid=x["id"];status=x["status"]
 for z in x["carried_tile_rows"]:
  excluded=rid.endswith("PRIMARY") and z["surface"]=="accent"
  record={"room":rid,"copies":x["unit_count"],"source_row_id":z["smartsheet_row_id"],"original_surface":z["surface"],
  "original_spec":z["carried_description"],"source_gross_sf_per_copy_includes_15pct":z["qty_sf_per_unit"],
  "implied_net_before_waste_not_measured":round(z["qty_sf_per_unit"]/1.15,4),
  "historic_rate_usd_sf":z["quoted_rate_usd_per_sf"],"historic_extended_usd_copy":z["extended_quote_cost_usd_per_unit"],
  "historic_line_arithmetic_not_confirmed_payable":True,
  "potential_supplier_grand_total_omission":"PH-BATH4 Bone Ribbed 107.2 SF per PH x2 = 214.4 SF: itemized at $7.37/SF, reportedly omitted from historic vendor grand total; confirm signed original quote total" if rid=="PH-BATH4" and z["smartsheet_row_id"]=="6976633752321924" else None,
  "original_source_scope":"EXCLUDED historic unpriced Primary niche, do not procure" if excluded else "Quoted ELM 2026-09-03 historic only",
  "candidate_design_direction":maker[rid],"proposed_substitute_sku":None,
  "exact_finish_wet_listing_approved":False,"exact_raw_wet_DCOF_value":None,"accepted_lab_report_id":None,
  "actual_substitute_field_sf":None,"actual_pan_sf":None,"measured_niche_field_displacement_sf":None,
  "manufacturer_original_tile_box_sf":None,"order_cartons":None,"true_exposed_trim_lf":None,
  "trim_profile_spec":None,"waterproof_substrate_spec":None,
  "current_Chicago_exact_lot_quote_usd":None,"current_installed_cost_usd":None,
  "owner_room_material_cap_usd":None,"current_verified_lot_stock":None,"current_delivery_date":None,
  "owner_approved":False,"release_allowed":False,
  "next_reconciliation_action":"EXCLUDE line" if excluded else ("Reconcile omitted 214.4 SF original supplier-total Ribbed scope and approved 35/27-SF before new live quote" if rid=="PH-BATH4" and z["smartsheet_row_id"]=="6976633752321924" else "Confirm exact candidate SKU wet/level application, measured takeoff, dated Chicago price, owner approval")}
  rows.append(record)
 for scope in ("manufacturer_spec","dimensions_and_edge","floor_pan_and_drain","owner_approval","vendor_quote_and_stock"):
  state=("N/A dry wall, wood floor" if scope=="floor_pan_and_drain" and "POWDER" in rid else
         "Inherited Primary level-floor DCOF HOLD, no separate order" if scope=="floor_pan_and_drain" and rid.endswith("WC") else
         "EXACT measured floor/pan DCOF FAIL" if scope=="floor_pan_and_drain" else "HOLD")
  tasks.append({"room":rid,"unit_copies":x["unit_count"],"gate_group":scope,"current_evidence_state":state,
   "provisional_material_direction":maker[rid],"owner_decision":owner[rid],
   "tech_responsibility":"GC/architect verification" if scope in ("dimensions_and_edge","floor_pan_and_drain") else "manufacturer certificate review / procurement evidence",
   "actual_1529_verified":False,"source_quote_usd_per_copy":x["carried_quote_material_subtotal_usd_per_unit"],
   "approved_technical":False,"owner_approved":False,"release_allowed":False,
   "next_document_required":"Correct-model survey and site measurement" if scope=="dimensions_and_edge" else
   "Exact maker SKU raw lab test, selected drain/membrane and shower slope" if scope=="floor_pan_and_drain" else
   "Written owner approval, no autonomous selection" if scope=="owner_approval" else
   ("Reconcile original 214.4-SF Ribbed vendor grand-total omission; obtain current exact lot/price/lead" if rid=="PH-BATH4" else "Current dated Chicago supplier exact lot/price/lead") if scope=="vendor_quote_and_stock" else
   "Finish/size-specific maker wet-area permission and verified carton yield"})
assert len(rows)==27 and len(tasks)==65
for name,items in (("R10_27_ROW_BID_COMPARISON_AND_NON_ORDERABLE_GAPS.csv",rows),("R10_65_WORK_ITEM_OWNER_GC_EVIDENCE_CLOSURE.csv",tasks)):
 with (O/name).open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
assert sum("EXCLUDED" in z["original_source_scope"] for z in rows)==2
assert all(not z["release_allowed"] and z["current_Chicago_exact_lot_quote_usd"] is None for z in rows)
assert round(sum(x["carried_quote_material_subtotal_usd_per_unit"]*x["unit_count"] for x in r),2)==23572.44
print("PASS 27 original source rows, 65 technical closure actions, 13 rooms, $23572.44 old source, all current vendor/owner release null/false")

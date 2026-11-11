from pathlib import Path
import json,math,csv
R=Path(__file__).resolve().parents[1]
rooms=json.loads((R/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
O=R/"deliverables/integrated-r10";O.mkdir(exist_ok=True,parents=True)
modules={"PH-PRIMARY":24,"PH-BATH2":20,"PH-BATH3":20,"PH-BATH4":24,"PH-POWDER":None,"PH-WC":None,"TX-PRIMARY":24,"TX-BATH2":20,"TX-BATH3":20,"TX-BATH4":24,"TX-POWDER":5,"TX-POWDER2":6,"TX-WC":None}
detail={"PH-PRIMARY":"Brizo 48-in linear and NO NICHE; flat Bone wet wall; shower pan exact test HOLD","PH-BATH2":"Duravit tub/Matte White; Sapphire maker wet PASS; Grey Soft floor DCOF HOLD; NO tiled pan","PH-BATH3":"Owner unselected basin, tub versus Delta point drain HOLD, Opal unlisted wet, Sandstone wet PASS","PH-BATH4":"Walk-in shower (geometry.json) with Brizo BT062415-BNX square drain; 35-versus-27 SF and Soft/Anti-Slip hold","PH-POWDER":"Dry Earth Lines feature; wood floor, wet DCOF N/A","PH-WC":"Shares Primary wet level floor, exact DCOF HOLD; zero independent quote","TX-PRIMARY":"Brizo 48-in linear, NO NICHE; Flat Clay wet PASS, Ribbed wet listing absent, pan test HOLD","TX-BATH2":"Duravit tub Chrome Hansgrohe, owner basin unselected; no tiled shower pan; floor test HOLD","TX-BATH3":"Owner tub versus shower; no speculative shower-pan area; owner program HOLD","TX-BATH4":"Duravit tub Matte White, no tiled pan; Charcoal/Soho possible, Bone Ribbed/Caviar wet listing FAIL","TX-POWDER":"70:30 Haze dry wall board-only, wood floor, color carton cost and owner signoff HOLD","TX-POWDER2":"Indigo dry wall/wood floor, deck faucet 73072341, basin unselected","TX-WC":"Shares Primary level floor; exact wet floor DCOF HOLD; zero independent quote"}
rows=[];issues=[]
book=["# R10 | Construction-interface and full 13-room purchase-preparation book","",
"These are room-specific, source-dimensional builder coordination sheets, NOT released shop drawings or procurement purchase orders. Live documents.list identifies Autodesk Docs 25-006 1527 N Wieland, not verified 1529. All room openings, joint/caliber, edge trim, actual measured pan/level split and signed owner approval remain null.",
"","Source SF already includes exactly one 15% waste. Net = source gross/1.15 is ARITHMETIC ONLY. Do not add shared WC floors or excluded Primary niche. Original September 3 2026 ELM quote is historic material only, not a new alternate price or approved budget. Owner PH 2.8M, TX 2.7M, comps 2.4-3.2M, 14 listings/9 buildings, Old Town prioritized and four Armitage sales one building precedent; LP/GC secondary. No assumed listing bathroom tile evidence.",""]
for x in rooms:
 rid=x["id"];g=json.loads((R/"rooms"/rid/"geometry.json").read_text(encoding="utf-8"))
 active=[z for z in x["carried_tile_rows"] if not(rid.endswith("PRIMARY") and z["surface"]=="accent")]
 ex=[z for z in x["carried_tile_rows"] if z not in active]
 gross=sum(z["qty_sf_per_unit"] for z in active)
 oldwall=sum(z["qty_sf_per_unit"] for z in active if z["surface"] in ("wall","vanity_wall"))
 wallfaces=sum(w["length"]["value"]*w["tiled_height"]["value"] for w in g["tiled_walls"])
 if "POWDER" in rid:
  best="Dry powder: maker approval for the exact dry vanity wall, calibrated grout, mirror/basin/faucet backing, exposed trim and wood-floor threshold; shower/pan wet DCOF N/A and no waterproof pan requirement. Actual 1529 dimensions, source color and owner signoff held."
  install="**Dry feature wall sequence:** verify actual 1529 vanity wall, mirror, faucet and backing positions; maker dry-wall application; true tile caliber, grout/profile/adhesive, exposed edge and junction to existing WOOD floor. No tiled bath floor/pan, wet DCOF N/A and shower waterproof/pan detail N/A. Owner basin selection remains held where unselected. True exposed LF and sticks NULL."
 elif rid.endswith("WC"):
  best="Shared WC level tile: inherit the appropriate PRIMARY's exact measured wet level-floor DCOF and finished threshold; no independent tile quantity or second WC carton purchase. Owner/GC verification held."
  install="**Inherited level-floor sequence:** coordinate WC threshold, actual toilet flange finished elevation, grout/movement and waterproofed level-floor requirements with PRIMARY source/lot. The exact Primary level-floor DCOF remains FAIL/HOLD. No independent shower pan or separate WC tile order; actual threshold/trim LF null."
 else:
  best="Exact accepted manufacturer SKU wet floor test and separate shower-pan test ONLY where an actual walk-in shower exists, verified 1529 dimensions, actual drain membrane/slope/fixture interface, current dated Chicago installed bid, exact cartons, sample and written owner approval."
  install="**Actual detail and waterproofing instruction:** confirm correct-model plumbing fixture/drain geometry, tub flange or shower membrane and slope; verify substrate flatness and approved ceiling setting; use exact manufacturer tile finish/wet approval and exact wet-floor/pan DCOF report where a tiled shower exists; draw net niche opening/back/returns and finished sill drainage ONCE; draw actual tile color, grout sample, movement joint, threshold to adjoining floor and full-height outside corners. Actual edge LF, profile/tile sticks, mosaic sheet split, membrane area, grout bags, installed cost and survey status all null."
 book+=["","## "+rid+" | status "+x["status"].upper(),"","**Selection trace:** "+str(x["champion_id"])+", score "+str(x["champion_score"])+", signed owner "+str(x["owner_status"])+". **Existing selected plumbing/technical hold:** "+detail[rid]+".",
 "**GOOD — historical/current board source:** preserve the v4 surface list and any scored board decision below, never presume a release from the word GOOD. **BETTER — conditional source-supported study:** "+detail[rid]+". **BEST — technical and owner release target, NOT achieved:** "+best,
 "Historic ELM material $"+format(x["carried_quote_material_subtotal_usd_per_unit"],".2f")+"/unit, two unit copies; active source "+format(gross,".2f")+" gross SF with embedded 15% waste; excluded Primary niche "+format(sum(z["qty_sf_per_unit"] for z in ex),".2f")+" SF (NO ORDER).","",
 "| Source row | Original scheduled surface / short description | Gross SF with 15% / net audit only | Historical USD per room | Proposed price / actual purchase |","|---|---|---|---:|---|"]
 for z in x["carried_tile_rows"]:
  price="null" if z["extended_quote_cost_usd_per_unit"] is None else format(z["extended_quote_cost_usd_per_unit"],".2f")
  book.append("| "+str(z["smartsheet_row_id"])+" | "+z["surface"]+" / "+z["carried_description"].replace("|","/")[:80]+" | "+format(z["qty_sf_per_unit"],".2f")+" / "+format(z["qty_sf_per_unit"]/1.15,".2f")+" | "+price+" | null; "+("EXCLUDED" if z in ex else "source-only, NOT PURCHASE")+" |")
 book+=["","| Original wall | Provisional W × tiled height | Drawing plane SF, NOT historic quote | Initial symmetric module/end cuts | Final field/survey/trim |","|---|---:|---:|---|---|"]
 for w in g["tiled_walls"]:
  width=w["length"]["value"]*12;height=w["tiled_height"]["value"]*12
  m=modules[rid];n=max(0,math.floor((width-6)/m)) if m else None
  end=(width-n*m)/2 if m else None
  cut=(str(n)+" nominal "+str(m)+"-in full units + 2 x "+format(end,".2f")+"-in end edges BEFORE joint") if m else "actual tile module unknown"
  book.append("| "+w["id"]+" | "+format(width,".2f")+" x "+format(height,".2f")+" in | "+format(width*height/144,".2f")+" | "+cut+" | actual tile calibration, grout, door/window/valves, movement edge, trim LF all NULL |")
  rows.append({"room":rid,"wall":w["id"],"source_width_in":round(width,3),"source_tiled_height_in":round(height,3),"source_face_sf_no_waste":round(width*height/144,3),"nominal_module_in":m,"full_modules_nominal":n,"equal_end_cut_nominal_in":round(end,3) if end is not None else None,"nominal_two_vertical_edges_lf_only_if_both_exposed":round(2*height/12,3),"actual_open_vertical_edges_count":None,"actual_caliber_in":None,"actual_1529_field_width_in":None,"actual_joint_in":None,"actual_exposed_edge_lf":None,"trim_sticks_orderable":None,"verified":False})
 if oldwall:book+=["","**Quote-to-plane coordination:** historical wall gross "+format(oldwall,".2f")+" SF vs source W faces "+format(wallfaces,".2f")+" SF, arithmetic difference "+format(oldwall-wallfaces,"+.2f")+" SF. NOT a proven shortage because quote gross has embedded waste and may include other faces/ceiling/niche. Survey and document each field before revising quantity."]
 book+=["",install,
 "**Sample and owner render set (NOT ORDERED):** one full wall and one floor color/size reference, one applicable pan sheet ONLY for real showers, two grout/movement-profile selections, existing faucet/drain finish reference, W1-W3 orthographic elevations plus 3/4 view using selected plumbing only. All missing fixture-center locations, window geometry, basin selections and shower glass dashed/not fabricated. Market captions use Old Town independent amenity precedent only, not assumed comp tile photos."]
 issues.append({"room":rid,"status":x["status"],"champion":x["champion_id"],"score":x["champion_score"],"original_material_per_unit_usd":x["carried_quote_material_subtotal_usd_per_unit"],"two_copy_old_material_usd":round(x["carried_quote_material_subtotal_usd_per_unit"]*x["unit_count"],2),"source_active_gross_sf_with_15pct":round(gross,3),"excluded_primary_niche_sf":round(sum(z["qty_sf_per_unit"] for z in ex),3),"source_wall_gross_sf":round(oldwall,3),"W_source_wall_face_sf_without_waste":round(wallfaces,3),"actual_field_wet_sf":None,"actual_shower_pan_sf":None,"actual_trim_lf":None,"actual_floor_DCOF_raw_test":None,"manufacturer_box_yield_for_original_tile":None,"current_Chicago_supplier_quote":None,"current_lot_stock_eta":None,"approved_room_material_cap":None,"owner_approved":False,"release_allowed":False,"source_truth":detail[rid]})
book+=["","## Distinct actual SKU versus procurement scenarios","",
"Glazzio HNC6615 12x24 nominal, factory actual 11.73x23.62, 8.25mm DCOF Matte, original manufacturer box 9.69SF/5 pcs and maker wet DCOF >0.50 LOWER BOUND; not exact raw tested value. HNC6715 2x2 hex nominal, sheet 11.73x11.85, 8.25mm, 4.85SF/5 sheets, maker Shower Floor YES, reported >0.50 BOUND; not exact raw lab result. Prime RL21 mosaic has manufacturer linear-drain CATEGORY check but no exact raw SKU DCOF; old >=0.60/new >=0.42 targets conflict. These are independent alternatives requiring source-matched field/pan/fixture and owner confirmation.",
"","| Original floor gross | Source gross including single 15% waste | All-level HNC6615 carton thought experiment | Actual release control |","|---|---:|---:|---|"]
for x in rooms:
 for z in x["carried_tile_rows"]:
  if z["surface"]!="floor":continue
  q=z["qty_sf_per_unit"];n=math.ceil(q/9.69)
  typ="Tub: no tiled shower pan" if x["id"] in ("PH-BATH2","TX-BATH2","TX-BATH4") else "mixed level/pan or owner program unresolved"
  book.append("| "+x["id"]+" / "+z["smartsheet_row_id"]+" | "+format(q,".2f")+" SF | "+str(n)+" boxes = "+format(n*9.69,".2f")+" SF ILLUSTRATIVE ONLY | "+typ+"; actual mapped level/pan areas, exact lab report and current quote NULL, do not purchase |")
book+=["","## Project release and unselected decisions","",
"- PH Bath4 owner 35 versus old 27 SF is not resolved by quote floor gross 40.2 SF, though arithmetic 40.2/1.15 =34.9565 SF is close to 35; actual floor pan boundaries, walls and Soft-versus-Anti-Slip quoted finish require as-built reconciliation.",
"- PH Primary and TX Primary: existing Brizo linear drain preserved, no Primary shower niche; do not assume a point-drain 2x2 pan is approved for a selected linear product. Shared WCs are included in Primary floor and inherit wet DCOF.",
"- PH Bath4 is a sourced WALK-IN shower with 4-in Brizo square point drain. PH Bath2, TX Bath2 and TX Bath4 are sourced TUB BATHS: no speculative tiled pan. TX Bath3 and PH Bath3 program conflicts remain owner-held.",
"- PH Bath3, TX Bath2 and TX Powder2 basins UNSELECTED; no consultant, AI or GC may choose them. Dry powders on wood have wet floor tile DCOF N/A; their mirror/edge backing and color/carton quotes still held.",
"- Supplier price/lot/current Chicago ETA, delivery freight, available imported stock, room cap, final unit installed cost, trim LF and purchase orders are NULL. Historical quote total $23,572.44 for four units, not a current supplier offer. All 13 owner/release flags FALSE."]
(O/"R10_ROOM_BY_ROOM_CONSTRUCTION_AND_PROCUREMENT_BOOK.md").write_text("\n".join(book)+"\n",encoding="utf-8")
for name,items in (("R10_SOURCE_WALL_CUT_AND_TRIM_CHECKS.csv",rows),("R10_13_ROOM_SOURCE_COST_AND_RELEASE_HOLDS.csv",issues)):
 with (O/name).open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
assert len(rows)==25 and len(issues)==13 and round(sum(z["two_copy_old_material_usd"] for z in issues),2)==23572.44
assert all(z["actual_shower_pan_sf"] is None and not z["owner_approved"] and not z["release_allowed"] for z in issues)
print("PASS R10 13 room specs, 25 actual drawing source nominal cut rows, historic 23572.44, no release or duplicate WC/pan")

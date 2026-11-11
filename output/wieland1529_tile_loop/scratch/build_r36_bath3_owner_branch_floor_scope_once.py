"""R36 substantive distinct conditional Bath3 owner-program/GC material engineering.
Not another R29 Sandstone niche or R35 Primary/WC study. Original 4 source units,
actual floor quote vs mutually exclusive tub/walkin and pan included/excluded.
"""
from pathlib import Path
from decimal import Decimal
import hashlib,csv,json,io
B=Path(__file__).resolve().parents[1]
R35=B/"deliverables/integrated-r35-primary-wc-dual-floor-pan-grate-threshold-13room-GC/MANIFEST.json"
signed="75785f1c193a1ae5766f21a522a5e6c2dbda3dd14e1d248a67cab39d43022a67"
assert hashlib.sha256(R35.read_bytes()).hexdigest()==signed
out=B/"research/products"
p={
 "scope":out/"R36_20261106_12_BATH3_FOUR_ACTUAL_UNIT_TUB_VS_POINT_PAN_CONTRACT_QUOTE_BRANCH_BALANCE.csv",
 "instances":out/"R36_20261106_12_BATH3_FOUR_ACTUAL_PHYSICAL_UNIT_THREE_OWNER_PROGRAM_INSTALLED_SCOPE_GATES.csv",
 "maker":out/"R36_20261106_12_BATH3_WALL_NICHE_LEVEL_POINT_PAN_ORIGINAL_ITEM_PERMISSIONS_AND_LAB.csv",
 "price":out/"R36_20261106_8_BATH3_OLD_MATERIAL_RATE_LEVEL_PAN_NEW_INSTALL_SCOPE_EXPOSURE.csv",
 "book":out/"R36_20261106_OWNER_BRANCH_CONTRACT_EVIDENCE_AND_WATERPROOF_CHANGEORDER_BOOK.md"
}
receipt=B/"state/ROUND036_NEXT_DISTINCT_BATH3_OWNER_PROGRAM_PAN_QUOTE_CONTRACT_SOURCE_PREPARED_NOT_REVIEWED.json"
assert all(not x.exists() for x in [*p.values(),receipt])
old=list(csv.DictReader((B/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig")))
assert len(old)==27 and sum(Decimal(x["historic_usd_two_copies"] or "0") for x in old)==Decimal("23572.44")
focus=("PH-BATH3","TX-BATH3")
geos={r:json.loads((B/"rooms"/r/"geometry.json").read_text(encoding="utf-8")) for r in focus}
floors={r:next(x for x in old if x["room"]==r and x["source_surface"]=="floor") for r in focus}
selected={
 "PH-BATH3":dict(drain="DT062412_CHROME_DELTA_4IN_SQUARE_POINT_CONDITIONAL_WALKIN",
  selected_shower="HANSGROHE_CHROME",wall="Tones Opal exact individual WET wall NOT approved",
  niche="Tones Sandstone maker individual wet listed reported PASS",floor="Cortar Bone Soft LEVEL exact raw numeric wet lab missing",
  basin="UNSELECTED_OWNER_BASIN",tub="OWNER_UNSELECTED_TUB_AND_WASTE_OVERFLOW"),
 "TX-BATH3":dict(drain="BT062415-BNX_BRIZO_BNX_4IN_SQUARE_POINT_CONDITIONAL_WALKIN",
  selected_shower="BRIZO_BLACK_ONYX",wall="Tones Emerald wet maker prior PASS needs current individual page refresh",
  niche="Tones Sandstone individually wet listed reported PASS",floor="Cortar Grey Soft LEVEL exact raw numerical wet lab missing",
  basin="DO_NOT_TRANSFER_PH3_BASIN_UNSELECTED",tub="OWNER_UNSELECTED_TUB_AND_WASTE_OVERFLOW")
}
def F(x):return f"{x:.4f}"
def M(x):return f"{x:.2f}"
def csvb(rows):
    assert rows and len({tuple(x) for x in rows})==1
    s=io.StringIO(newline="");w=csv.DictWriter(s,fieldnames=list(rows[0]),lineterminator="\n")
    w.writeheader();w.writerows(rows);return s.getvalue().encode("utf-8-sig")
branches=[
 ("TUB_OWNER_UNSELECTED_NO_POINT_PAN","TUB","NO_SHOWER_PAN"),
 ("WALKIN_POINT_PAN_INSIDE_QUOTED_ROOM_FLOOR","WALKIN","PAN_INCLUDED"),
 ("WALKIN_POINT_PAN_ADDITIONAL_TO_QUOTED_ROOM_FLOOR","WALKIN","PAN_EXCLUDED")
]
scope=[];instances=[];maker=[];rate=[]
for room,g in geos.items():
    assert len(g["revit_room_numbers"])==2
    q=floors[room];floor=float(g["floor_area"]["value"])
    pan=float(g["shower_or_tub_footprint"]["width"]["value"])*float(g["shower_or_tub_footprint"]["depth"]["value"])
    gross=float(q["source_gross_sf_one_copy_waste_15pct_once"])
    historic=float(q["historic_usd_two_copies"])
    unit_rate=historic/(gross*2)
    assert abs(gross-floor*1.15)<0.11
    for copy in g["revit_room_numbers"]:
        for key,program,interpretation in branches:
            if program=="TUB":
                level=floor;panarea=0;extra=0
            elif interpretation=="PAN_INCLUDED":
                level=floor-pan;panarea=pan;extra=0
            else:
                level=floor;panarea=pan;extra=pan*1.15
            scope.append(dict(room=room,physical_source_copy=copy,owner_program_branch=key,
              source_bathroom_area_SF_unverified=F(floor),
              source_5ft_tub_ALCOVE_shower_footprint_not_1529_measured_SF=F(pan),
              original_historic_floor_GROSS_SF_one_copy15pct_included=F(gross),
              reconstructed_original_1point15_from_area_GROSS_SF=F(floor*1.15),
              original_floor_GROSS_minus_reconstructed_SF=F(gross-floor*1.15),
              projected_distinct_BATH_LEVEL_NET_SF=F(level),
              projected_distinct_conditional_POINT_PAN_NET_SF=F(panarea),
              projected_combined_unique_material_NET_SF=F(level+panarea),
              theoretical_added_PAN_GROSS_SF_if_separately_proven=F(extra),
              original_two_copy_floor_material_only_historic_USD=q["historic_usd_two_copies"],
              historical_blended_floor_rate_USD_per_GROSS_reference_only=F(unit_rate),
              theoretical_added_pan_at_BLENDED_rate_material_USD_nonpayable=M(extra*unit_rate),
              source_original_selected_4in_POINT_applies_only_walkin=selected[room]["drain"] if program=="WALKIN" else "N_A_TUB",
              actual_1529_polygon_and_original_quote_scope="UNKNOWN",
              exact_RAW_LEVEL_lab_and_conditional_POINT_PAN_lab="MISSING",
              original_historic_15pct_not_reapplied_to_prior_gross="TRUE",
              source_owner_TUB_vs_WALKIN_selected="FALSE",
              no_point_drain_purchase_in_tub_option="TRUE",
              owner_approved="FALSE",GC_CHANGE_ORDER_signed="FALSE",purchase_authorized="FALSE"))
            instances.append(dict(room=room,source_physical_copy=copy,owner_BRANCH=key,
              source_shower_plumbing_finish_preserved=selected[room]["selected_shower"],
              source_draining_point_only_if_walkin=selected[room]["drain"] if program=="WALKIN" else "N_A_TUB",
              tub_make_model_rough_waste_overflow_owner_selected="NONE" if program=="TUB" else "N_A_SHOWER",
              conditional_walkin_pan_four_plane_and_waterproof_assembly="FULL_POINT_PAN_FACTORY_WRITTEN_DETAIL_REQUIRED" if program=="WALKIN" else "N_A_TUB",
              conditional_new_tub_flange_3wall_rough_and_service="FULL_FACTORY_OWNER_SELECTION_REQUIRED" if program=="TUB" else "N_A_SHOWER",
              actual_1529_model_or_certified_stamped_site_identity="",
              valve_and_drain_axis_actual_1529_shop_location="",
              actual_tile_level_vs_pan_cut_waste_and_factory_lot="",
              actual_backer_waterproof_membrane_corner_edge_and_movement="",
              owner_basin_program=selected[room]["basin"],
              owner_program_TUB_WALKIN_selected="FALSE",
              architect_plumber_waterproof_tile_supplier_GC_signed="FALSE",
              physical_one_to_one_mockup_built="FALSE",current_chicago_installed_quote="",
              purchase_authorized="FALSE"))
        for part in ("WET_WALL","WET_NICHE","LEVEL_FLOOR"):
            maker.append(dict(room=room,source_physical_copy=copy,surface=part,
              actual_selected_tile_source=selected[room]["wall"] if part=="WET_WALL" else
                   selected[room]["niche"] if part=="WET_NICHE" else selected[room]["floor"],
              manufacturer_individual_exact_SKU_wet_application_permission=(
                  "FAIL_OR_UNVERIFIED_PH_OPAL" if room=="PH-BATH3" and part=="WET_WALL" else
                  "PASS_PRIOR_ITEM_REFRESH_MAKER_REVALIDATE" if part in ("WET_WALL","WET_NICHE") else
                  "ORIGINAL_EXACT_NUMERIC_RAW_LEVEL_WET_DCOF_MISSING"),
              conditional_WALKIN_independent_POINT_PAN_wet_DCOF="MISSING_IF_OWNER_WALKIN_ONLY",
              owner_TUB_has_no_tiled_shower_pan="TRUE",
              actual_drain_and_membrane_factory_approved="FALSE",
              exact_current_SKU_and_lot_and_suitable_substrate="UNKNOWN",
              original_raw_numeric_LEVEL_measured_test_ID_date="",
              original_raw_numeric_POINT_PAN_measured_test_ID_date="",
              owner_selection="FALSE",installer_approved="FALSE",purchase_authorized="FALSE"))
        for quote_branch in ("PAN_INSIDE_QUOTE","PAN_OUTSIDE_QUOTE"):
            rate.append(dict(room=room,source_physical_copy=copy,
              owner_TUB_vs_WALKIN_still_unselected="TRUE",
              hypothetical_WALKIN_quote_branch=quote_branch,
              original_quote_level_GROSS_with_15pct_once=F(gross),
              original_quoted_TWO_COPY_floor_material_only_USD=q["historic_usd_two_copies"],
              theoretical_point_pan_net_SF=F(pan),
              theoretical_point_pan_GROSS_if_new_separately_proven_SF=F(0 if quote_branch=="PAN_INSIDE_QUOTE" else pan*1.15),
              theoretical_old_BLENDED_material_RATE_USD_per_GROSS=F(unit_rate),
              hypothetical_material_only_PAN_reference_not_payable_USD=M(0 if quote_branch=="PAN_INSIDE_QUOTE" else pan*1.15*unit_rate),
              selected_DELTA_or_BRIZO_square_POINT_rough_compatibility="OWNER_BRANCH_CONDITIONAL_NEEDS_FACTORY_SHOP",
              selected_TUB_program_and_overflow_waste="NONE_SELECTED_DO_NOT_GUESS",
              actual_historic_vendor_quote_EXCLUSION_or_inclusion_proof="",
              actual_delivered_stock_receipt_material_credit="",
              actual_1529_floor_polygon_and_sloped_four_plane_screed_estimate="",
              current_independent_pan_tile_original_numeric_wet_lab="",
              current_factory_case_lot_US_chicago_offer_installed_labour="UNKNOWN",
              paid_material_shortage_established="FALSE",
              GC_installed_change_order_authorized="FALSE",purchase_authorized="FALSE"))
assert (len(scope),len(instances),len(maker),len(rate))==(12,12,12,8)
text="""# R36 actual Bath3 owner-program source/contract change-order engineering

This new R36 technical cycle builds on signed R35 but does NOT repeat R29 Sandstone niche cutstock or R23 original owner branch work. It performs materially NEW **per-source original historical quoted gross versus selected alternative physical PAN accounting and potential contractor changed-scope** for four original PH-BATH3/TX-BATH3 physical instances.

**Owner PH-BATH3 and TX-BATH3 TUB vs WALK-IN remain UNSELECTED.** There is NO selected bathtub/overflow/waste in either owner program. Preserve PH3 Hansgrohe Chrome and only conditional Delta DT062412 Chrome 4in POINT if owner chooses WALKIN. Preserve TX3 Brizo Black Onyx and only conditional BT062415-BNX square POINT for WALKIN. Tub branch requires completely separate owner-selected tub, manufacturer flange/support/waste/overflow, actual 1529 alcove fit and new signed plumbing; never convert existing square shower POINT to a tub waste. PH3 basin UNSELECTED, do not transfer to TX3.

**Quantitative new historical floor-provenance finding:** PH3 drawing-provisional 35SF x1.15 = 40.25 versus original historic quoted40.2 gross/copy, difference -0.05SF. TX3 drawing-provisional37SF x1.15=42.55 versus historic42.5 gross/copy, difference -0.05SF. PH3 5x2.33ft original provisional *tub alcove* footprint 11.65SF, TX3 5.1x2.6ft =13.26SF. These footprints are not certified shower polygon or owner WALKIN; they are numerical *sensitivities only*. For actual owner selected future TUB: bath LEVEL=source bath 35/37SF and shower PAN=N_A, with tub-flange wet-wall waterproofing distinct. For conditional WALKIN with original quoted bath-area PAN included: LEVEL=source bath-provisional rectangle, POINT PAN=rectangle, no additional gross purchase from original quote without evidence. For conditional WALKIN with PAN quote-excluded: LEVEL remains original bath area, added PAN gross is 13.3975SF PH /15.2490SF TX per physical copy if separate new future 15% is explicitly authorized. No second 15% on historic original quote. Each of 12 branch x copy cases identifies actual future owner choice, original vendor quote inclusion, exact original LEVEL wet raw lab, independent POINT pan raw lab, shower vs tub membrane and actual 1529 dimension/installed quote. No branch signed or payable.

Historic material-only two-copy floor amounts PH3 $542.70 and TX3 $573.76 already included inside original $23,572.44 four-unit total. Their old blended rate is not a current POINT PAN small-format tile cost or installed scope price, and a hypothetical extra PAN material reference is **not** a claim of shortage, unit credit or actual savings. Additional labor must be bid separately for either owner-selected future tub flange/rough/membrane/waste access OR four-plane shower point-drain slope/threshold/waterproof, proper small-format pan tile, grout/trim/profiles and wet test.

Separate factory wet WALL, NICHE and LEVEL original product permissions: PH3 selected Tones OPAL individual wet WALL is NOT verified/FAIL; Tones Sandstone niche individually wet listed, but prior maker item and real SKU/lot/installation need source confirmation. TX3 Emerald prior maker wet WALL reported PASS but current individual live page refresh needed; Sandstone niche wet listed; both LEVEL exact original measured wet numeric DCOF missing and conditional owner WALKIN POINT pan has separate unverified original raw numeric lab. No Bronze/Black Onyx/Delta cross-product drain/membrane approval. No fabricated samples, renders or 1529 site/rough numbers.

**Next owner/GC action without vendor outreach now:** obtain native true 1529 actual wall and floor geometry, source material item SKU, original quote current paid/received quantities and supplier lot, owner choice tub-vs-walkin and exact tub selection (if applicable), separate factory waterproof/rough and tub or point-shower complete sequence, 1:1 physical wet mockup, and current Chicago installed GC change-order bid with clear original scope credits. Only after all owner/architect/plumber/waterproof/tile/supplier/GC/purchaser approvals and independent four authentic specialist governance may orders release. Original board R017, original worker9 failed and reviewer15 finished. Global 13-room objective OPEN, zero owner selections/purchases.
"""
payload={p["scope"]:csvb(scope),p["instances"]:csvb(instances),p["maker"]:csvb(maker),
         p["price"]:csvb(rate),p["book"]:text.encode("utf-8")}
for path,data in payload.items():
    with path.open("xb") as f:f.write(data)
rec=dict(round=36,phase="NEXT_SUBSTANTIVE_TWO_BATH3_MUTUALLY_EXCLUSIVE_OWNER_PROGRAM_QUOTE_LEVEL_PAN_GC_SOURCE",
  date_local="2026-11-06",predecessor_R35_full_SHA256=signed,
  files=[dict(path=path.relative_to(B).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()) for path,data in payload.items()],
  quantities=dict(physical_source_bath3_copies=4,mutually_exclusive_three_program_and_quote_cases=len(scope),
     original_wet_wall_niche_level_permission_checks=len(maker),original_8_installed_quote_contract_receivers=len(rate)),
  original_historic_total_material_only_USD="23572.44",original_15pct_waste_in_historic_gross_once=True,
  owner_tub_vs_walkin_selected=False,owner_tub_model_selected=False,
  original_raw_numeric_wet_level_pan_lab_received=False,actual_1529_footprint_measured=False,
  current_factory_maker_case_lot_chicago_quote=False,GC_installed_CO_approved=False,
  original_four_critic_complete=False,independent_nonpro_reviewer_accepted=False,
  all_material_release=False,global_DONE=False)
receipt.write_bytes((json.dumps(rec,indent=2)+"\n").encode("utf-8"))
print("R36_SHA",hashlib.sha256(receipt.read_bytes()).hexdigest(),
      "COUNTS",len(scope),len(instances),len(maker),len(rate),"5_SIGNED_FILES")

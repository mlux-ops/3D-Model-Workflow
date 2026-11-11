"""R38 distinct wet-WALL site/old-quote-to-maker removal/GC safety optimization.
Physical PH3/PH4/TX3 wall coverage and original historic gross reconciled.
Not R29 niche cutstock or R30 Caviar/SOHO alternative layouts; NO owner choice.
"""
from pathlib import Path
from decimal import Decimal
import hashlib,json,csv,io
B=Path(__file__).resolve().parents[1]
parent=B/"deliverables/integrated-r37-powder-vanity-factory-finish-plane-dry-wall-mirror-13room-procurement/MANIFEST.json"
sha="985f994993b3b118f9e507fc60309ac3144ca3c7bf3f20c19db10c31adba5c81"
assert hashlib.sha256(parent.read_bytes()).hexdigest()==sha
R36=B/"state/ROUND036_NEXT_DISTINCT_BATH3_OWNER_PROGRAM_PAN_QUOTE_CONTRACT_SOURCE_PREPARED_NOT_REVIEWED.json"
assert hashlib.sha256(R36.read_bytes()).hexdigest()=="9e539c5a69ea62dfb5f0e634a77ed932cbcb425780981c8b7123e8c318efe5ec"
O=B/"research/products"
paths={
 "walls":O/"R38_20261106_9_FULL_THREE_WALL_WET_ROOM_FIELD_15PCT_ORIGINAL_GROSS_RECONCILIATIONS.csv",
 "aperture":O/"R38_20261106_36_6_PHYSICAL_WET_ROOMS_TWO_NICHE_APERTURES_AND_3_WALL_RECEIVER_CREDITS.csv",
 "factory":O/"R38_20261106_18_WET_WALL_OWNER_OLD_MAKER_VS_WET_LISTED_SUBSTITUTION_AND_WP_MOCKUP.csv",
 "cost":O/"R38_20261106_12_6_PHYSICAL_WET_WALL_QUOTE_MAKER_CONDITIONAL_INSTALLED_SCOPE_EXPOSURES.csv",
 "book":O/"R38_20261106_FOUR_DRY_TO_WET_MAKER_SOURCE_GATES_AND_3ROOM_ORIGINAL_WALL_QUOTE_SURFACE_BOOK.md"
}
rec=B/"state/ROUND038_NEXT_DISTINCT_WET_WALL_MAKER_PERMISSION_FULL_FIELD_NICHE_OPENING_CONTRACT_SOURCE_PREPARED_NOT_REVIEWED.json"
assert all(not x.exists() for x in [*paths.values(),rec])
def readcsv(p):
    with (B/p).open(encoding="utf-8-sig") as f:return list(csv.DictReader(f))
old=readcsv("deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv")
original_w=readcsv("deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv")
assert len(old)==27 and len(original_w)==25 and sum(Decimal(x["historic_usd_two_copies"] or 0) for x in old)==Decimal("23572.44")
rooms=("PH-BATH3","PH-BATH4","TX-BATH3")
fact={
"PH-BATH3":dict(original="Tones Opal 2x20 Glossy individual wet WALL UNVERIFIED",
 alternative="ELM Tones Sandstone 2x20 Glossy individually WET WALL listed but NOT owner selected",
 url="https://www.elmsurfaces.com/product/sandstone-tones",
 niche="Source existing Sandstone NICHE maker wet listed; preserve existing niche order once",
 program="TUB versus WALKIN owner UNSELECTED; Delta Chrome 4in POINT only WALKIN"),
"PH-BATH4":dict(original="ELM Cortar Bone Ribbed relief maker exact wet WALL permission ABSENT",
 alternative="ELM Cortar Bone flat wet application distinct NOT a permission for Ribbed; owner replacement UNSELECTED",
 url="https://www.elmsurfaces.com/product/cortar-bone-ribbed",
 niche="Original Clara Caviar 2x8 NICHE individual wet authorization ABSENT; SOHO only unselected",
 program="Owner WALKIN selected Brizo 4in Black Onyx SQUARE POINT; four-plane PAN and separate LEVEL"),
"TX-BATH3":dict(original="ELM Tones Emerald 2x20 Glossy individual wet WALL prior maker PASS; current item page source refresh required",
 alternative="Original Emerald retention conditional genuine current manufacturer item WET listing and same-lot not replacement",
 url="https://www.elmsurfaces.com/product/emerald-tones",
 niche="Original Tones Sandstone wet NICHE listed; separate actual back returns one-time",
 program="TUB versus WALKIN owner UNSELECTED; Brizo Black Onyx 4in POINT only WALKIN"),
}
W={(x["room"],x["wall"]):x for x in original_w}
S={(x["room"],x["source_surface"]):x for x in old}
assert all((r,"wall") in S for r in rooms)
walls=[];aperture=[];factory=[];cost=[]
def F(v):return f"{v:.4f}"
def M(v):return f"{v:.2f}"
def csvb(data):
    assert data and len({tuple(x.keys()) for x in data})==1
    s=io.StringIO(newline="");w=csv.DictWriter(s,list(data[0]),lineterminator="\n")
    w.writeheader();w.writerows(data);return s.getvalue().encode("utf-8-sig")
for r in rooms:
    g=json.loads((B/"rooms"/r/"geometry.json").read_text(encoding="utf-8"))
    assert len(g["revit_room_numbers"])==2 and len(g["tiled_walls"])==3
    summed=0.
    for wall in ("W1","W2","W3"):
        src=W[r,wall];face=float(src["source_width_in_UNVERIFIED"])*float(src["source_tiled_height_in_UNVERIFIED"])/144
        summed+=face
        walls.append(dict(room=r,source_wall=wall,
            source_width_in_UNVERIFIED=src["source_width_in_UNVERIFIED"],
            source_height_in_UNVERIFIED=src["source_tiled_height_in_UNVERIFIED"],
            original_FULL_wall_field_before_openings_NET_SF=F(face),
            historical_original_same_room_WALL_GROSS_per_copy_SF=S[r,"wall"]["source_gross_sf_one_copy_waste_15pct_once"],
            original_source_WET_WALL_maker_condition=fact[r]["original"],
            owner_current_PROGRAM=fact[r]["program"],
            true_native_1529_WALL_opening_recess_niche_lintel_toilet_valve="UNKNOWN",
            actual_measured_openings_and_existing_niche_aperture_TO_DEDUCT_ONCE="",
            actual_WALL_individual_wet_permission_maker_letter="",
            owner_approved="FALSE",current_site_measured="FALSE",purchase_authorized="FALSE"))
    quote=float(S[r,"wall"]["source_gross_sf_one_copy_waste_15pct_once"])
    assert abs(summed*1.15-quote)<.2,(r,summed*1.15,quote)
    for physical in g["revit_room_numbers"]:
        for possible in (12.,16.):
            # Hypothetical actual SINGLE existing 12-in-tall niche,
            # NOT installed; no explicit x,y wall or count inferred.
            surface=possible*12/144
            for wall in ("W1","W2","W3"):
                aperture.append(dict(room=r,source_physical_copy=physical,source_wall=wall,
                    hypothetical_ONE_existing_NICHE_aperture_width_in=F(possible),
                    hypothetical_existing_aperture_height_in=F(12.),
                    hypothetical_ONE_wall_FIELD_aperture_loss_SF=F(surface),
                    source_wall_base_net_before_any_apertures_SF=next(x["original_FULL_wall_field_before_openings_NET_SF"] for x in walls if x["room"]==r and x["source_wall"]==wall),
                    source_original_all_three_walls_NET_before_apertures_SF=F(summed),
                    theoretical_all_three_walls_after_ONE_aperture_NET_SF=F(summed-surface),
                    theoretical_original_15pct_equivalent_field_aperture_GROSS_SF_NOT_CREDIT=F(surface*1.15),
                    already_originally_quoted_wall_gross_no_second_waste=F(quote),
                    niche_back_side_top_sill_independent_original_scope="EXISTING_NICHE_LINE_SEPARATE_NO_NEW_ORDER",
                    need_actual_one_niche_count_and_location="TRUE",
                    source_wet_WALL_and_niche_permission_two_separate="TRUE",
                    actual_1529_niche_count_wall_plane_pipe_and_sill="",
                    live_maker_wet_wall_and_individual_niche_letter="",
                    true_field_credits_and_paid_returnable_inventory="UNKNOWN",
                    owner_authorized_replacement_fabrication="FALSE",
                    GC_payable_credit_or_change_order_approved="FALSE",purchase_authorized="FALSE"))
        for scheme in ("SOURCE_RETAIN_UNVERIFIED_MAKER_WET_WALL_NO_RELEASE",
                       "CONDITIONAL_INDIVIDUAL_WET_LISTED_SAME_WALL_SHOP_NO_OWNER_SUBSTITUTION",
                       "FULL_REDESIGNED_WATERPROOF_TO_TILE_EDGE_OWNER_PREAPPROVAL"):
            factory.append(dict(room=r,source_physical_copy=physical,conditional_system=scheme,
                original_owner_program=fact[r]["program"],
                original_WALL_exact_maker_wet_rating=fact[r]["original"],
                only_CONDITIONAL_wall_replacement_or_refresh=fact[r]["alternative"],
                original_or_candidate_maker_URL=fact[r]["url"],
                independently_original_niche_maker_gate=fact[r]["niche"],
                original_maker_wet_WALL_permission_if_required="UNRESOLVED" if r!="TX-BATH3" else "PRIOR_PASS_NEEDS_LIVE_CONFIRMATION",
                actual_wet_wall_tub_flange_or_walkin_maker_approved_membrane="FALSE",
                actual_1529_valve_escutcheon_glass_and_transition_1to1_corners="",
                actual_1529_wall_rough_caliber_joints_edge_LF_movement="",
                original_wall_tile_15pct_historic_gross_once=F(quote),
                new_owner_chosen_material_sku_color_finish_lot="",
                distinct_LEVEL_floor_original_exact_wet_numeric_DCOF="MISSING",
                independent_POINT_PAN_raw_numeric_if_walkin="MISSING_OR_N_A_IF_OWNER_TUB",
                selected_actual_owner_program_changed="FALSE",
                owner_WALL_substitution_approved="FALSE",maker_written_permission_verified="FALSE",
                current_supplier_and_GC_installed_bid="",
                physical_mockup_accepted="FALSE",purchase_authorized="FALSE"))
        for s in ("EXISTING_WET_WALL_WITH_PRODUCT_PERMISSION_HOLD",
                  "COMPLETE_WET_MAKER_AUTHORIZED_WALL_REPLACEMENT_OWNER_ONLY"):
            wallrate=float(Decimal(S[r,"wall"]["historic_usd_two_copies"])/(Decimal(str(quote))*2))
            cost.append(dict(room=r,source_physical_copy=physical,conditional_scope=s,
                original_WALL_GROSS_SF_per_copy_15pct_once=F(quote),
                original_WALL_two_copy_material_only_USD=S[r,"wall"]["historic_usd_two_copies"],
                old_BLENDED_wall_material_ONLY_RATE_per_GROSS_SF=F(wallrate),
                nominal_one_12in_by12in_existing_aperture_GROSS_equivalent_SF=F(1.15),
                source_material_only_value_of_one_aperture_not_paid_credit_USD=M(wallrate*1.15),
                actual_signed_existing_niche_area_and_wet_wall_accessories="",
                original_quoted_wall_and_excluded_openings_paid_inventory_receipt="",
                maker_current_exact_WALL_variant_wet_application_permission="",
                replacement_tile_material_current_chicago_stock_lot_case_cost_USD="",
                old_wall_returnable_material_original_credit_USD="",
                real_waterproof_membrane_movement_edge_valve_patch_installed_GC_bid_USD="",
                pay_approved_CHANGE_ORDER_or_savings="FALSE",owner_substitution_approved="FALSE",
                purchase_authorized="FALSE"))
assert (len(walls),len(aperture),len(factory),len(cost))==(9,36,18,12)
book="""# R38 new original whole-WALL wet maker and quoted-gross exposure study

After signed R37 three dry powder rooms, this substantive next source cycle audits **PH-BATH3, PH-BATH4 and TX-BATH3** (six physical source baths) against original full W1/W2/W3 gross and manufacturer-specific wet WALL use. It does NOT repeat R30 228 detailed niche tile-format cut studies or replace R36 TUB/WALKIN owner branches.

**New cross-room numerical finding:** three source wet-wall gross quantities approximate **(W1+W2+W3 full drawing faces) x original1.15** before any actual door/window/niche opening deduction, which makes source old quoted wet WALL and separately quoted niche openings an independent 1529 field reconciliation. PH3 W1 60in+W2/W3 27.96in each, height93in: full three-wall NET ~74.86 SF, gross reconstructed ~86.09 vs historic **86.2 SF/copy**. PH4 W1 60in, W2/W3 30.48in, height111in: full three-wall NET ~93.24 SF, gross107.226 vs historical **107.2 SF/copy**. TX3 W1 61.2in, W2/W3 31.2in, height93in: three-wall NET79.825 SF, gross91.79875 vs historic **91.8 SF/copy**. These differences do NOT prove original payable overquoted walls or actual 1529 openings; gross includes original 15% once, source area and actual niche location/count unverified.

New **9** distinct original W1/W2/W3 maker-material wall records, **36** physical wall x two hypothetical 12/16in aperture scenarios correctly deduct ONE actual wall opening from original FIELD once while separately preserving original niche back/side/top/sill quote, **18** physical maker authorization/owner-only replacement versus retained wet wall assembly branches and **12** manufacturer-specific old wall material rate versus future waterproof/movement/valve/GC installed labour exposure holds. No original wet WALL material of unverified type is deemed automatically forbidden by its manufacturer; lack of individual approval is a hard evidence HOLD.

PH Bath3: Original Tones Opal 2x20 Glossy wet WALL maker individual application absent, not authorized; individual ELM Tones Sandstone 2x20 Glossy Wet Areas listing is a **conditional unselected** wet WALL alternative, not owner approval or permission to transfer. Existing Sandstone niche maker wet listing is a separate scope and remains included original quote. Original Delta Chrome square POINT ONLY if owner chooses WALKIN, otherwise future separate owner-selected tub and waste; PH basin UNSELECTED.

PH Bath4: Owner WALKIN remains, selected Black Onyx Brizo 4-in square POINT with independent four-plane PAN and LEVEL. ELM Cortar Bone Ribbed maker listing Walls/Back Splash lacks verified individual Wet Areas for current original PH4 wet WALL; flat Bone permission does not transfer to Ribbed. Original Clara Caviar 2x8 individual niche wet listing separately missing; proposed Soho Ivory only conditional owner program, no substitute now. Original 35-versus27 floor and 214.4 vendor wall grand-total questions are not accepted payable shortages.

TX Bath3: Original Tones Emerald 2x20 Glossy wet WALL has prior individual maker Wet Areas PASS from archived source https://www.elmsurfaces.com/product/emerald-tones but current live individual product retrieval/source revision refresh pending; Sandstone wet niche original separately listed. Owner TUB vs WALKIN remains unselected, Brizo Black Onyx square POINT only conditional future WALKIN.

**All three** require genuine native verified 1529 W1/W2/W3 dimensions, actual existing wall openings and niche count/backs/returns/sill and pipe locations, physical water/corner/end/edge movement details, actual selected tile item size/color/finish and maker individually approved wet WALL and NICHE letters, actual physical 1:1 shop plus signed plumber/waterproof/tile and GC estimated newly installed waterproof/valve service/breakage. Original raw numeric measured wet LEVEL and separate POINT PAN only for actual/owner conditional shower branches; brochure targets NOT numeric test results. Original historical wall material rates are material-only blended quote and 15% already included; DO NOT treat old gross wall-aperture correlation as a verified paid credit or re-add 15%. Current Chicago factory lot/case/ETA/freight and full installed bid UNKNOWN. No vendor contacts, model edits, owner choice, purchases or independent Reviewer clearance. Entire thirteen-room objective OPEN, formal board R017 frozen.
"""
payload={paths["walls"]:csvb(walls),paths["aperture"]:csvb(aperture),
         paths["factory"]:csvb(factory),paths["cost"]:csvb(cost),paths["book"]:book.encode("utf-8")}
for path,data in payload.items():
    with path.open("xb") as f:f.write(data)
receipt=dict(round=38,phase="DISTINCT_POST_R37_WET_WALL_FULL_FIELD_MAKER_PERMISSIONS_APERTURE_SHOP_SCOPE_SOURCE",
 date_local="2026-11-06",predecessor_R37_full_SHA256=sha,
 files=[dict(path=path.relative_to(B).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()) for path,data in payload.items()],
 counts=dict(three_wall_original_source_records=len(walls),actual_physical_wall_hypothetical_aperture_contract_sensitivity=len(aperture),
    physical_maker_wet_permission_assembly_cases=len(factory),physical_original_rate_vs_installed_GC_scope_exposure=len(cost)),
 original_material_rows=27,original_hist_total_tile_only_USD="23572.44",
 original15pct_waste_in_gross_once=True,source_true_1529_measurements_verified=False,
 maker_wet_WALL_missing_permissions_solved=False,owner_tub_walkin_program_changed=False,
 current_raw_measured_numeric_wet_LEVEL_POINT_labs_received=False,
 current_chicago_supplier_lot_case_bid=False,GC_signed_CO=False,
 original_four_specialist_reports_complete=False,independent_reviewer_accepted=False,
 owner_approved=False,purchase_authorized=False,global_DONE=False)
rec.write_bytes((json.dumps(receipt,indent=2)+"\n").encode("utf-8"))
print("R38_SOURCE_SHA",hashlib.sha256(rec.read_bytes()).hexdigest())
print("R38_COUNTS",len(walls),len(aperture),len(factory),len(cost),"SIGNED_FILES",len(payload))

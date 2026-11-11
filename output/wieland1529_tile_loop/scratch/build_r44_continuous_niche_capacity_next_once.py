"""Distinct R44 quantitative 3in finished-pier width CAPACITY / profile jig.
Signed source engineering only; not next integrated R44, not a measured niche.
Never re-run one-time creator, never touch R43 or earlier signed outputs.
"""
from pathlib import Path
import json,csv,io,hashlib,math
B=Path(__file__).resolve().parents[1]
MAN=B/"deliverables/integrated-r43-four-wet-bath-niche-focal-wall-fabrication-and-13room-GC/MANIFEST.json"
R43="71921913b2f8efb733a40d1ca87154c8d816af1519e1a59e5f7dc03943a5d6b0"
assert hashlib.sha256(MAN.read_bytes()).hexdigest()==R43
OUT=B/"research/products"
receipt=B/"state/ROUND044_NEXT_SOURCE_ONLY_CONTINUOUS_W3_FINISHED_PIER_CAPACITY_PREPARED_NOT_REVIEWED.json"
csvname="R44_108_FINISHED_W3_NICHE_MAX_OPENING_EDGE_TRIM_ACTUAL_FIELD_LOSS_AND_CENTERLINE_SCENARIOS.csv"
mdname="R44_FIELD_MEASURED_MAX_NICHE_WIDTH_ACTUAL_W3_PROFILE_VALVE_GLASS_FABRICATION_SHOP_LEAD.md"
assert not receipt.exists() and not (OUT/csvname).exists() and not (OUT/mdname).exists()
rooms=("PH-BATH3","PH-BATH4","TX-BATH3","TX-BATH4")
W={}
with (B/"deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv").open(encoding="utf-8-sig") as f:
 for x in csv.DictReader(f):
  if x["room"] in rooms and x["wall"]=="W3":W[x["room"]]=float(x["source_width_in_UNVERIFIED"])
assert len(W)==4
rows=[]
for room,w in W.items():
 for offset in (0,.5,1):
  for total_field_loss in (0,.25,.5):
   for each_edge_finish in (0,.125,.25):
    source_w_after_loss=w-total_field_loss
    maxsize=source_w_after_loss-2*(3+each_edge_finish+abs(offset))
    # A factory opening should be at most the computed bound once actual
    # dimensions and real installed profile clearance are field verified.
    r=dict(room=room,source_provisional_W3_width_in=f"{w:.4f}",
     assumed_actual_TOTAL_finish_to_finish_width_loss_in=f"{total_field_loss:.4f}",
     hypothetical_from_CENTER_niche_centerline_OFFSET_abs_in=f"{offset:.4f}",
     hypothetical_effective_min_PIER_finish_edge_profile_projection_each_side_in=f"{each_edge_finish:.4f}",
     minimum_actual_FINISHED_tile_focal_pier_required_in="3.0000",
     derived_max_centered_or_offset_NICHE_OPENING_width_in=f"{maxsize:.4f}",
     formula="MAX_OPENING=W_ACTUAL-2*(PIER_MIN+EACH_EDGE_PROFILE+ABS_CENTER_OFFSET)",
     can_16in_opening_pass_MATHEMATICALLY="TRUE" if maxsize>=16 else "FALSE",
     can_20in_opening_pass_MATHEMATICALLY="TRUE" if maxsize>=20 else "FALSE",
     can_24in_opening_pass_MATHEMATICALLY="TRUE" if maxsize>=24 else "FALSE",
     true_SITE_1529_wall_finish_and_lot_caliber="UNKNOWN",
     actual_NICHE_location_valve_glass_blocking_and_profile="UNKNOWN",
     actual_manufacturer_WET_NICHE_application_and_system="UNAPPROVED",
     exact_original_LEVEL_vs_POINT_pan_numeric_lab="MISSING_OR_TUB_N_A",
     source_IS_NOT_ACTUAL_SITE_measurement="TRUE",
     actual_owner_niche_size_selected="FALSE",shop_released="FALSE",purchase_authorized="FALSE")
    rows.append(r)
assert len(rows)==108
f=io.StringIO(newline="");writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
writer.writeheader();writer.writerows(rows)
CSV=f.getvalue().encode("utf-8-sig")
DOC=f"""# R44 distinct precision-fabrication capacity technical start, not R43 repeat

**R43 integrated full predecessor** SHA {R43}. This is a NEW continuous *maximum feasible finished-opening width* decision function, not R43's four predetermined 12/16/20/24 source aperture illustrations, not an approved 1529 niche or an integrated full R44 release. Four original W3 wall source widths: PH3 27.96in, PH4 30.48in, TX3 31.20in, TX4 30.48in. All are drawing-provisional, NOT true measured 1529 geometry; accessible native 1527 not transferable. Actual owner-only PH3/TX3 TUB-vs-WALKIN unselected, PH4 Brizo BNX POINT fixed WALKIN, TX4 Duravit/Matte White TUB no tiled PAN and R42 spout/thermostat conflict all unchanged.

## New construction formula for an actual eventual field-surveyed finished pier

MAX possible niche opening = **measured finished W3 width - 2×(3in minimum finished focal pier + actual each-side edge profile/reveal projection + absolute proposed niche center offset from true wall centerline)**. This must additionally pass real valve/pipe/glass/opening/blocking clear-zone geometry and the manufacturer-approved NICHE membrane/substrate system. Factory tile caliber, grout and trim depth will adjust actual finish pier; values below are sensitivities only, not measurements or permits.

The new 108 numerical scenarios (four rooms × three hypothetical offset choices × three total finish width-loss × three each-edge profiles) demonstrate a **new release-critical counterexample**: PH4/TX4 raw centered 24in opening showed 3.24in piers in R43; allowing only **0.25in projection for each exposed profile**, even with zero field-width loss/zero offset, yields **MAX opening 23.98in**, so 24in now FAILS the desired finished 3in pier. PH3 with 20in opening: at centered and 0.25in profiles, MAX=21.46in PASS, but offset 1in reduces MAX to **19.46in**, so 20in now FAILS. TX3 centered 24in with 0.25in profiles has MAX=24.70in PASS while 1in offset reduces MAX=22.70in FAIL.

This is a genuine additional architectural/construction decision consequence: field shop may need a narrower niche, shift the VALVE (only if plumber and owner permit), adjust a vanity/glass clearance, or abandon niche if real 1529 blocking/piping prohibits minimum sides. No owner program, selected plumbing, tile or niche opening is modified. The original source full-wall vs actual opening invoice and original 15pct waste already included remain unchanged. Original full project historic material-only four-unit $23,572.44. No actual current case yield, supplier/GC material cost, new approved design, field sample or independent Reviewer approval.

**Next actual R44 multi-trade action**: architect/site verify each of eight physical original room copies' true W3 finished width, external corner and glass/valve/pipe offsets plus tile profile projection using manufacturer's actual selected material/caliber. Plumber fix pipe-free niche rectangle, waterproofer approve niche membrane/backer and sill, tile installer sign 1:1 minimum3in FINISHED pier sample, owner select exact niche dimension. Then integrate negative field aperture once and separately positive back, returns, head, sill, exposed edge trim, actual installed labor and old received/paid/returnable material credit with current factory lot/case and full GC bid. Original numerical wet bath LEVEL vs independent POINT/LINEAR PAN lab still missing. No emails, vendor inquiries, Revit/Smartsheet/Git writes, model edits or orders. Original Reviewer worker15 finished and formal R017 original specialists unavailable, so do not score or declare global DONE.
"""
doc=(DOC.strip()+"\n").encode("utf-8")
rec=dict(round=44,date_local="2026-11-06",phase="DISTINCT_NEXT_CONTINUOUS_3IN_FINISHED_PIER_CAPACITY_SOURCE_ENGINEERING_NOT_FULL_R44_OR_BLIND",
 predecessor_R43_full_SHA256=R43,
 scenarios=108,rooms=list(rooms),source_status="DRAWING_PROVISIONAL_NOT_MEASURED_TRUE1529",
 no_owner_SELECTION=True,original_four_unit_material_only_USD="23572.44",old_15pct_waste_in_GROSS_once=True,
 all_original_PROGRAMS_unchanged=True,formal_board_round=17,
 owner_approved=False,architect_approved=False,site_1529_verified=False,
 individual_maker_WET_NICHE_APPROVED=False,actual_1TO1_built=False,
 current_Chicago_supplier_and_full_GC_bid_received=False,purchase_authorized=False,
 nonPro_Reviewer_done=False,global_DONE=False,
 files=[dict(path=f"research/products/{n}",bytes=len(v),sha256=hashlib.sha256(v).hexdigest()) for n,v in ((csvname,CSV),(mdname,doc))])
for filename,data in ((csvname,CSV),(mdname,doc)):
 with (OUT/filename).open("xb") as z:z.write(data)
receipt.write_bytes((json.dumps(rec,indent=2)+"\n").encode("utf-8"))
print("R44_SOURCE_COUNT",len(rows),"R44_SOURCE_RECEIPT_SHA",hashlib.sha256(receipt.read_bytes()).hexdigest())

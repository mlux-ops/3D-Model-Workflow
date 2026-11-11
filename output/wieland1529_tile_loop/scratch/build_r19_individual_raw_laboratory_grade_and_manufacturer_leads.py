"""Additive signed R19 manufacturer-origin wet DCOF evidence-grade research.

No current board candidate role/score changes, no substitutions selected, no source
lab values invented. Zia individual color manufacturer table is summarized, not
an original signed laboratory report of specific SKU/finish/sealing.
"""
from pathlib import Path
import csv,hashlib,json
from decimal import Decimal
R=Path(__file__).resolve().parents[1];S=R/"state"
D=R/"deliverables/integrated-r19-manufacturer-wet-evidence-grades"
assert not D.exists()
def fp(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
R18=R/"deliverables/integrated-r18-owner-sample-visual-and-shop/MANIFEST.json"
R17=R/"deliverables/integrated-r17/MANIFEST.json"
assert fp(R18)["sha256"]=="c958b49e76f8f5b12b0aca267a8dfc1870527b04b12fd3714751fd024a565ebe"
assert fp(R17)["sha256"]=="78c0849c14a83dba65023d7ede812181d7360d2c7cd00eaa2f8cc0e33927aac1"
D.mkdir(parents=True)

official="https://support.ziatile.com/hc/en-us/article_attachments/25221619136148"
values=[("Acacia","0.54","723","2.3"),("Badlands","0.54","811","2.0"),
        ("Black Rock","0.55","542","2.0"),("Mesa","0.63","963","1.9"),
        ("Sierra","0.57","790","2.0"),("Volcan","0.58","1170","2.0"),
        ("Yuma","0.53","953","2.2")]
rows=[]
for color,listed_dcof,break_lbf,absorb in values:
 assert Decimal(listed_dcof)>=Decimal("0.42")
 rows.append({
 "manufacturer":"Zia Tile","collection":"Cantera","maker_color":color,
 "source_color_specific_numeric_DCOF":listed_dcof,
 "source_test_method":"ANSI A326.3 as stated in color chart",
 "source_third_party_testing_lab":"SGS TEC Services per maker PDF",
 "source_record_quality":"MANUFACTURER SUMMARY OF THIRD-PARTY TEST, NOT ORIGINAL RAW SPECIMEN REPORT",
 "original_signed_lab_report_id":"","exact_tiled_SKU_finish_size_test_specimen":"",
 "testing_sealer_surface_condition":"","source_nominal_tile_thickness_in":"0.75",
 "source_24x12_case_area_sf":"9.70","source_24x12_case_weight_lb":"72",
 "source_breaking_strength_lbf":break_lbf,"source_water_absorption_pct":absorb,
 "actual_1529_bath_LEVEL_wet_application_certified":"FALSE",
 "actual_1529_slope_shower_PAN_application_certified":"FALSE",
 "actual_1529_drain_membrane_assembly_certified":"FALSE",
 "owner_material_replacement_selected":"FALSE",
 "real_Chicago_installed_quote":"","actual_vendor_case_yield_confirmed":"",
 "current_lot_stock_eta":"","owner_approval":"FALSE",
 "procurement_release":"FALSE",
 "source_pdf":official,
 "note":"Do not transfer collection color value across format, sealing chemistry, physical sample, or installed slope; original test document and project condition required"
 })
with (D/"R19_7_MAKER_COLOR_SPECIFIC_NUMERIC_THIRD_PARTY_SUMMARY_NOT_ORIGINAL_LAB.csv").open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]))
 w.writeheader();w.writerows(rows)
assert len(rows)==7 and all(x["procurement_release"]=="FALSE" for x in rows)

maker_note=[
 "# R19 — manufacturer color-specific third-party numeric wet friction data, not a selected project lab",
 "",
 "**November 6, 2026. RESEARCH LEAD / NO OWNER APPROVAL OR GC/PO RELEASE.** This is independently sourced new evidence, not a redesign of the four frozen R014 or R015 neutral candidates. No tile is substituted.",
 "",
 "## Actual independently inspected primary manufacturer document",
 "",
 "Zia Tile's official [Cantera installation and specification PDF]("+official+") contains an ANSI A326.3 color-specific numerical DCOF table credited to third-party **SGS TEC Services**. It reports Acacia 0.54, Badlands 0.54, Black Rock 0.55, Mesa 0.63, Sierra 0.57, Volcan 0.58 and Yuma 0.53. This is meaningfully more specific than a threshold such as Daltile Target >=0.42 and more traceable than an uncited merchant spec. It still **does NOT supply the underlying individual original laboratory specimen certificate or report ID**, date, exact format/SKU, surface sealer and installed condition. Strict 1529 wet LEVEL and PAN release remains **FAIL/NULL** for every room until these are reconciled.",
 "",
 "## Why the material is NOT automatically interchangeable with the chosen 12x24 bath floor",
 "",
 "- Cantera is natural volcanic lava stone requiring experienced installer and controlled grout, cleaning and field sealing. It is not a porcelain drop-in for original ELM Cortar Soft or proposed Daltile Prime.",
 "- The official maker nominal thickness is **3/4 in**; 24x12 nominal tile carton covers 9.70 SF and weighs 72 lb for 5 pieces, versus thinner baseline 3/8-in nominal Daltile 12x24 alternatives. Finished floor elevation, load, thresholds, tub flange/door clearance, trowel/build-up, plumbing rough and substrate capacity require architect/structural/installer review.",
 "- The manufacturer describes 15–20% cut/breakage overage for its natural stone, with more for appearance sorting. This is NOT a new allowance applied to historic original gross: the original 2026-09-03 tile source gross already contains 15% once. A newly chosen cantera design would require true verified NET 1529 area and a separately owner/GC approved new cut allowance ONCE, never two full flooring orders or double historic waste.",
 "- Caution: Maker installation includes pre-grout seal and interior matte top-coat protective wax, but the DCOF chart DOES NOT identify which sealer and service state the exact tested tile used. Sealed wet dynamic friction can differ materially. Demand test record for exact final installed condition, rather than assuming 0.54-0.63 is post-wax slip.",
 "- Four-plane square POINT and 48in LINEAR sloped PANs require independent appropriate small-format pan tile, compliant slopes and separately tested result. A 12x24 heavy stone format should **NOT** be assigned to any POINT/LINEAR shower PAN merely because a color has a wet DCOF table; those schemes remain completely unapproved.",
 "",
 "## Evidence tiers enforceable across the complete 13-room program",
 "",
 "| Tier | Example | Actual project use |",
 "|---|---|---|",
 "| A — source-exact raw lab | Original lab certificate for exact SKU, size, finish, tested surface treatment, date, wet A326.3 numerical output and verified maker application | **Mandatory strict bath LEVEL and separately sloped PAN gate** when manufacturer/owner selects material; currently none supplied |",
 "| B — maker third-party numeric summary with named laboratory | Zia official color-specific Cantera A326.3 chart credited SGS TEC Services, seven 0.53-0.63 reported values | Promising source request lead but **NOT Tier A** without specimen ID, exact size/finish, sealer/report and project-compatible install |",
 "| C — merchant catalog exact SKU decimal, no original test report | TileBar New Rock Perla White/Fumo Chiseled 12x24 pages displaying DCOF 0.66 | Useful numeric prospect, no lab method/date or original report; FAIL current project strict gate |",
 "| D — maker product-page target or bound | Daltile Prime Target >=0.42, Emser >=0.60 or Glazzio >0.50 | Threshold/target is not actual raw measured result; FAIL project strict gate |",
 "| E — no documented SKU-level wet application | Historic ELM Opal wet WALL, Clara Caviar niche, Cortar Reed/Ribbed relief | Wet individual wall/niche permission FAIL even before LEVEL/PAN slip test |",
 "",
 "## Field and procurement next step, without contacting any supplier",
 "",
 "Architect and GC may compare the Cantera palette against the 12x24 LEVEL bath material only as an **unapproved sample concept** once owner authorizes a future study. Require original SGS specimen/lab report and sealing condition, exact current maker color/size/SKU, bathing barefoot application, wet results, SKU carton/gauge, exposed trim/structural load, true 1529 measurements, owner allowance and dated installed Chicago bid. No vendor communication, sample order, pictures or purchasing has occurred. Current project high-value design procurement remains the selected owner fixtures, R014/R015 independent governance and R17/R18 signed holds.",
 "",
 "## Documentation",
 "",
 "- Official maker PDF source: "+official,
 "- Refer to R19_7_MAKER_COLOR_SPECIFIC_NUMERIC_THIRD_PARTY_SUMMARY_NOT_ORIGINAL_LAB.csv for each published color number and absent primary lab/procurement fields.",
 "- Manufacturer summary and merchant numerical values must not be presented as project-accepted raw certified test data or compared directly with different tile formats.",
 "- External project goals: R014 original independent design seat unavailable, R015 source cleared but four-seat review not dispatched; 13-room objective **OPEN**."
]
(D/"R19_7_COLOR_SGS_DCOF_EVIDENCE_QUALITY_AND_INSTALLER_HOLDS.md").write_text("\n".join(maker_note)+"\n",encoding="utf-8")

lab=R/"deliverables/integrated-r17/R17_13_ROOM_WET_LAB_AND_PROGRAM_MATRIX.csv"
with lab.open(encoding="utf-8",newline="") as f:old=list(csv.DictReader(f))
assert len(old)==13
roomrequests=[]
for row in old:
 rid=row["room"]
 kind=row["required_PAN_lab_gate"]
 if "N/A" in kind or kind=="N/A":
  pan_request="NOT APPLICABLE, no tiled shower PAN for this room"
 elif "CONDITIONAL" in kind:
  pan_request="ONLY IF owner selects WALK-IN: exact separate small-format 4-plane square POINT pan maker wet numerical raw ANSI A326.3; tub PAN N/A"
 elif "LINEAR" in kind:
  pan_request="Exact independently tested small-format 48in Brizo LINEAR PAN tile and approved drain/membrane shop; no extra niche"
 elif "POINT" in kind:
  pan_request="Exact independently tested small-format 4-plane Brizo square POINT PAN tile with approved drain/membrane shop"
 else:
  raise ValueError((rid,kind))
 roomrequests.append({
 "room":rid,"existing_LEVEL_gate":row["required_LEVEL_lab_gate"],"existing_PAN_gate":kind,
 "required_new_source_document_for_wet_LEVEL":"Original manufacturer/laboratory PDF with exact planned bath LEVEL SKU, format, finish, sample ID, method ANSI A326.3, test date, numeric actual measured DCOF, surface sealer/treatment and wet application. Parent Primary also covers WC.",
 "separate_PAN_source_requirement":pan_request,
 "individual_wet_WALL_document":"Individual exact SKU/color/finish Wet Areas listing for every actual tub/shower wall, not flat-to-relief or Sapphire-to-Opal transfer",
 "individual_wet_NICHE_document":"Actual niche item/color/finish Wet Areas listing; absent Caviar/Opal not replaced by other colors",
 "Zia_Cantera_color_specific_SGS_summary_is_not_current_selected_tile":"TRUE",
 "source_master_research_pdf":official,
 "current_original_RAW_lab_reference":"","actual_1529_geometry_proven":"FALSE",
 "owner_approved":"FALSE","GC_released":"FALSE","PO_released":"FALSE"
 })
with (D/"R19_13_ROOM_ORIGINAL_LAB_SPECIMEN_AND_APPROVAL_REQUEST_MATRIX.csv").open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(roomrequests[0]))
 w.writeheader();w.writerows(roomrequests)
assert len(roomrequests)==13 and all(x["PO_released"]=="FALSE" for x in roomrequests)
(D/"START_HERE_R19.md").write_text("# R19 — manufacturer-origin numeric wet DCOF evidence hierarchy\n\nThis is an additive future manufacturer LAB source lead, NOT a replacement for v4 or R014/R015 frozen blind candidates. Official Zia Cantera color-specific ANSI A326.3 third-party SGS summary has seven published decimals but lacks underlying lab report, exact tested 12x24 SKU/finish/sealer and installed conditions; strict individual RAW original lab gate remains unclosed. The original $23,572.44 four-unit historic basis, 15% once, 13 owner rooms, selected plumbing, source scores null and release false remain. No sample, render, quote, vendor outreach or purchases.\n",encoding="utf-8")

files=sorted(p for p in D.iterdir() if p.is_file())
assert len(files)==4
manifest={
 "as_of":"2026-11-06","kind":"additive manufacturer exact color numeric third party DCOF evidence, original raw specimen gap and 13-room wet lab provenance requests",
 "new_maker_color_numeric_records":7,"room_technical_lab_closure_requests":13,
 "official_maker_pdf":official,
 "source_primary_raw_lab_report_available":False,
 "values_source_tier":"B color-specific manufacturer third-party summary, NOT original tested exact final SKU/sealed lot certificate",
 "Zia_is_selected_for_current_1529_room":False,
 "R17_original_signed_manifest_sha256":fp(R17)["sha256"],
 "R18_signed_manifest_sha256":fp(R18)["sha256"],
 "R014_source_sha256":fp(S/"ROUND014_SUBMISSION.json")["sha256"],
 "R015_source_sha256":fp(S/"ROUND015_SUBMISSION.json")["sha256"],
 "historical_four_unit_tile_material_usd":"23572.44",
 "original_15pct_waste_embedded_once":True,
 "owner_approval":False,"GC_release":False,"procurement_release":False,
 "R014_scoring":None,"R015_scoring":None,
 "outputs":{p.name:fp(p) for p in files}
}
(D/"MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert all(fp(D/n)==v for n,v in manifest["outputs"].items())
print("PASS R19 maker PDF independent named SGS 7 color numerical DCOF original-report gap + 13 application-specific raw lab requests, 4 signed outputs; no selections or release")
print("R19_MANIFEST_SHA",fp(D/"MANIFEST.json")["sha256"])

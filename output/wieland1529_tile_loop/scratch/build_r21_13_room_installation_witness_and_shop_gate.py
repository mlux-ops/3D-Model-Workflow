"""R21: independent installation/waterproof witness sequencing and procurement gate matrix.

Every source dimension remains PROVISIONAL, no manufacturer approval inferred.
Each of 13 rooms gets 12 sequenced witness/photo fields, N/A where physically
inapplicable. Keeps earlier R12-R20 signed source, original prices and boards.
"""
from pathlib import Path
import csv,json,hashlib
from decimal import Decimal

R=Path(__file__).resolve().parents[1];S=R/"state"
D=R/"deliverables/integrated-r21-install-witness-sequence"
assert not D.exists()
def fp(p):
    b=p.read_bytes()
    return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
R17=R/"deliverables/integrated-r17/MANIFEST.json"
R18=R/"deliverables/integrated-r18-owner-sample-visual-and-shop/MANIFEST.json"
R19=R/"deliverables/integrated-r19-manufacturer-wet-evidence-grades/MANIFEST.json"
R20=R/"deliverables/integrated-r20-tx-tub-public-retail-and-carton-holds/MANIFEST.json"
assert fp(R17)["sha256"]=="78c0849c14a83dba65023d7ede812181d7360d2c7cd00eaa2f8cc0e33927aac1"
assert fp(R18)["sha256"]=="c958b49e76f8f5b12b0aca267a8dfc1870527b04b12fd3714751fd024a565ebe"
assert fp(R19)["sha256"]=="cbbc76a1a0fb6cb03e2109c3d929e853b126053bfa6a1f4cdafea2a3e7b8cace"
assert fp(R20)["sha256"]=="c298f924085b22873b88e2a19850a0b7f2a3f2fcf85757b009ed607c13159fd0"

rooms=json.loads((S/"ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert len(rooms)==13
wet= {x["id"] for x in rooms if "BATH" in x["id"] or "PRIMARY" in x["id"]}
assert len(wet)==8,wet
tub={"PH-BATH2","TX-BATH2","TX-BATH4"}
conditional={"PH-BATH3","TX-BATH3"}
point={"PH-BATH4"}
linear={"PH-PRIMARY","TX-PRIMARY"}
dry={"PH-POWDER","TX-POWDER","TX-POWDER2"}
wc={"PH-WC","TX-WC"}
assert wet==tub|conditional|point|linear
assert len(wet|dry|wc)==13
assert not (S/"ROUND014_SCORING.json").exists() and not (S/"ROUND015_SCORING.json").exists()

fixtures={
 "PH-PRIMARY":"Brizo BT0734816-BNX 48in Black Onyx LINEAR + BR73480 rough; no extra niche, PH-WC LEVEL inherited",
 "TX-PRIMARY":"Brizo BT0734816-BNX 48in Black Onyx LINEAR + BR73480 rough; no extra niche, TX-WC LEVEL inherited",
 "PH-BATH2":"Selected Duravit TUB with Hansgrohe Matte White; no tiled shower PAN",
 "TX-BATH2":"Selected Duravit TUB with Hansgrohe Chrome, basin unselected; no tiled shower PAN",
 "TX-BATH4":"Selected Duravit TUB with Hansgrohe Matte White; no tiled shower PAN",
 "PH-BATH3":"Owner TUB vs WALK-IN UNSELECTED; Delta DT062412 Chrome 4in square POINT only as shower drain; PH basin unselected",
 "TX-BATH3":"Owner TUB vs WALK-IN UNSELECTED; Brizo BT062415-BNX Black Onyx 4in square POINT only as shower drain",
 "PH-BATH4":"Actual selected WALK-IN; Brizo BT062415-BNX Black Onyx 4in square POINT; NO tub",
 "PH-POWDER":"DRY vanity tile WALL and WOOD floor, wall faucet Luxe Gold",
 "TX-POWDER":"DRY vanity tile WALL and WOOD floor, Haze Camel/Wheat conditional 70:30",
 "TX-POWDER2":"DRY Indigo Edge vanity tile WALL and WOOD floor, Tecturis 73072341 DECK-mounted; basin unselected",
 "PH-WC":"Inherited PH-PRIMARY LEVEL only, no separate material order or PAN",
 "TX-WC":"Inherited TX-PRIMARY LEVEL only, no separate material order or PAN",
}
assert set(fixtures)=={x["id"] for x in rooms}
D.mkdir(parents=True)

phases=[
 ("01_NATIVE_MODEL_AND_FIELD_DIMENSIONS","Architect / field superintendent",
  "Verify actual 1529 project identity first; wet/dry room number, floor area, finish face, openings and true W1-W3, thresholds and actual signed rough conditions; never substitute live 1527 model"),
 ("02_INDIVIDUAL_MAKER_WALL_APPLICATION","Architect / tile specifier",
  "Obtain individual exact maker tile SKU/color/finish Wet Areas listing for actual tub/shower wet WALL; dry powder/WC not a tub surround"),
 ("03_INDIVIDUAL_NICHE_APPLICATION_AND_NET","Architect / tile setter",
  "Obtain distinct individual exact niche Wet Areas listing, survey aperture, back, returns, sill, positive inward slope; subtract displaced face once; Primaries forbid added niche"),
 ("04_LEVEL_FLOOR_RAW_WET_LAB","Architect / manufacturer technical",
  "Original raw exact measured numerical wet DCOF report with individual LEVEL SKU/format/finish, test method, specimen ID, date and surface treatment; shared WC inherits parent once"),
 ("05_INDEPENDENT_SHOWER_PAN_RAW_WET_LAB","Architect / manufacturer technical",
  "Distinct actual format/finish small PAN mosaic original raw measured wet DCOF; specify LINEAR vs four-plane POINT independently; N/A for actual tubs, powder and WCs"),
 ("06_SELECTED_PLUMBING_ROUGH_AND_MODEL_BRANCH","Plumber / architect",
  "Confirm selected Brizo 48in LINEAR/BR73480 or point drain and model; tub only original selected Duravit with dedicated waste/overflow; Bath3 owner TUB vs WALK-IN not chosen"),
 ("07_MEMBRANE_SLOPE_AND_TUB_FLANGE_SHOP","Waterproofing installer / plumber / architect",
  "Signed manufacturer-matched actual drain lower body, preslope, clamp/liner/weep or selected tub flange/backer/penetration detail; do not infer bonded membrane compatibility or invent drain position"),
 ("08_INSPECTION_LEAK_OR_FLOOD_TEST","GC / plumbing / waterproof inspector",
  "Witness required local code/selected manufacturer flood/leak test and photographed accepted drain/liner/curb or tub waste/tub flange before tile. Do not invent Chicago inspection duration"),
 ("09_CUT_JOINT_CALIBER_MOVEMENT_AND_TRIM","Tile setter / architect",
  "One-to-one actual calibrated tile/grout and field-balanced cut study around 1529 openings/niches/valves; approved movement joints and exposed metal/ceramic edge linear feet"),
 ("10_MEASURED_NET_AREA_AND_CONDITIONAL_FULL_CASES","Estimator / tile installer",
  "Measured NET each WALL/NICHE/LEVEL and applicable distinct PAN; actual maker carton SF, one approved future cut allowance only, historic gross 15% already once, no extra niche/WC/duplicate floor"),
 ("11_EXACT_LOT_INSTALLED_COST_AND_AVAILABILITY","GC procurement / estimator",
  "Dated exact SKU/color/size/caliber/shade/lot stock allocated Chicago source and ETA; landed material and separate waterproof/set/trim labor installed bid. Public catalog/store is not trade quote"),
 ("12_OWNER_ARCHITECT_GC_AND_PURCHASE_RELEASE","Owner / architect / GC / authorized purchaser",
  "Distinct signed owner program/finish/budget cap, architect lab/geometry/shop, GC waterproof/quantity/current bid, final separate PO release; no role may infer absent approval")
]
assert len(phases)==12

rows=[]
for r in rooms:
 rid=r["id"]
 g=json.loads((R/"rooms"/rid/"geometry.json").read_text(encoding="utf-8"))
 w="; ".join(z["id"]+" "+str(round(z["length"]["value"]*12,3))+"in source" for z in g.get("tiled_walls",[]))
 for name,role,task in phases:
  num=int(name[:2])
  if num==2:
   if rid in dry|wc:
    applicability="N/A_NO_WET_TUB_SHOWER_WALL"
   else:
    applicability="REQUIRED_EXACT_SKU_WET_WALL_PERMISSION"
  elif num==3:
   if rid in dry|wc or rid in linear:
    applicability="N/A_NO_WET_NICHE_OR_OWNER_NO_ADDED_PRIMARY_NICHE"
   else:
    applicability="REQUIRED_INDIVIDUAL_WET_NICHE_PERMISSION"
  elif num==4:
   applicability=("N/A_WOOD_FLOOR" if rid in dry else "INHERITED_PARENT_PRIMARY_ONCE" if rid in wc else "REQUIRED_EXACT_RAW_NUMERIC_LEVEL_WET_LAB")
  elif num==5:
   applicability=("REQUIRED_SEPARATE_48IN_LINEAR_PAN_RAW_LAB" if rid in linear else
       "REQUIRED_4PLANE_SQUARE_POINT_PAN_RAW_LAB" if rid in point else
       "CONDITIONAL_ONLY_IF_OWNER_WALKIN_4PLANE_POINT_PAN_RAW_LAB" if rid in conditional else
       "N/A_NO_TILED_SHOWER_PAN")
  elif num==7:
   applicability=("NO_SHOWER_SYSTEM_WOOD_FLOOR_ONLY" if rid in dry else
       "NO_SHOWER_SYSTEM_INHERITED_WC_LEVEL" if rid in wc else
       "TUB_FLANGE_WASTE_WALL_WATERPROOF_SHOP" if rid in tub else
       "TUB_OR_SQUARE_POINT_SHOWER_AS_OWNER_FUTURE_ELECTION" if rid in conditional else
       "SELECTED_BRIZO_LINEAR_MEMBRANE_SLOPE_SHOP" if rid in linear else
       "SELECTED_BRIZO_4IN_SQUARE_POINT_MEMBRANE_4PLANE_SHOP")
  elif num==8:
   applicability=("N/A_NO_WET_FIXTURE" if rid in dry|wc else
       "TUB_LEAK_AND_FLANGE_WATERPROOF_INSPECTION_NO_PAN" if rid in tub else
       "CONDITIONAL_OWNER_BRANCH_TEST_CANNOT_SELECT" if rid in conditional else
       "SHOWER_LINER_FLOOD_TEST_WITH_APPROVED_INSPECTOR_NO_INVENTED_DURATION")
  elif num==6:
   applicability=("PH_OR_TX_PRIMARY_BRIZO_48IN_LINEAR_BNX_BR73480" if rid in linear else
       "PH4_BRIZO_BNX_4IN_SQUARE_POINT" if rid in point else
       "PH3_DELTA_DT062412_CHROME_POINT_CONDITIONAL" if rid=="PH-BATH3" else
       "TX3_BRIZO_BT062415_BNX_POINT_CONDITIONAL" if rid=="TX-BATH3" else
       "OWNER_SELECTED_DURAVIT_TUB_NO_SHOWER_PAN" if rid in tub else
       "DRY_VANITY_ONLY_NO_WET_SHOWER_ROUGH" if rid in dry else
       "PARENT_PRIMARY_WC_SHARED_FLOOR_NO_SHOWER_ROUGH")
  else:
   applicability="REQUIRED_PROJECT_SPECIFIC_EVIDENCE_HOLD"
  na=applicability.startswith("N/A") or applicability.startswith("NO_SHOWER")
  rows.append({
    "room":rid,"room_copy_count":"2","owner_selected_fixture_and_program":fixtures[rid],
    "sequence_step":name,"trade_witness":role,"specific_evidence_scope":task,
    "applicability":applicability,"source_room_area_SF_PROVISIONAL":str(g["floor_area"]["value"]),
    "source_W_study_only_PROVISIONAL":w,
    "proof_photo_required":"NOT_APPLICABLE" if na else "YES_WITH_TRUE_1529_FIELD_DATETIME_AND_WITNESS",
    "actual_1529_verified_dimension_record":"",
    "exact_maker_SKU_finish_format_or_approved_tub_model":"",
    "original_lab_certificate_or_test_ID":"",
    "approved_drain_membrane_rough_shop_ID":"",
    "local_code_inspection_report_or_test_ID":"",
    "trade_witness_name_and_date":"",
    "net_area_and_case_calculation_ID":"",
    "actual_Chicago_lot_quote_installed_bid_ID":"",
    "owner_approval_id":"","architect_acceptance_id":"","GC_acceptance_id":"","purchase_order_ID":"",
    "completed":"N/A" if na else "FALSE",
    "procurement_release":"FALSE"})
assert len(rows)==156
assert sum(x["completed"]=="FALSE" for x in rows)>90
with (D/"R21_156_FIELD_INSPECTION_AND_TRADE_WITNESS_HOLD_POINTS.csv").open("w",encoding="utf-8",newline="") as f:
 wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)

book=[
 "# R21 — 13-room waterproofing, plumbing rough, bath-floor and procurement witness sequencing",
 "",
 "**NO APPROVED SHOP, LAB, FIELD MEASUREMENT, INSPECTION, OWNER SIGNATURE, CURRENT GC BID OR PURCHASE.** This is an actual construction-ready *evidence request and hold-point schedule*, not a completed inspection. It is separate from R17 source/estimator schedule and R18 owner visual mockups. All historic R12-R20 records unchanged.",
 "",
 "## Source-grounded eight wet-room systems, not generic floor/PAN tests",
 "",
 "| Room grouping | Actual owner-selected plumbing or unresolved program | Required distinct waterproof/shower evidence | Lab applicability |",
 "|---|---|---|---|",
 "| PH-PRIMARY / TX-PRIMARY | Selected Brizo Black Onyx BT0734816-BNX 48in LINEAR with BR73480 rough, no extra niche | Original exact linear rough, membrane, grate frame 7–18mm, slopes, threshold, actual float and flood-witness section; separate tub selected; shared WC inherited LEVEL | Exact raw wet LEVEL + independent small-format 48in LINEAR PAN; WC same LEVEL ONCE, no WC PAN |",
 "| PH-BATH4 | Selected WALK-IN with Brizo BT062415-BNX Black Onyx 4in SQUARE POINT | True four-plane shower PAN, actual drain center/height/clamp/membrane/curb/glass/shop/flood. NEVER 48in linear or tub | Separate exact raw LEVEL and small-format 4-plane POINT PAN. Source 35 vs 27SF requires owner/GC survey |",
 "| PH-BATH3 | Owner TUB / WALK-IN UNSELECTED, selected Delta DT062412 Chrome 4in square shower POINT (not tub waste), basin unselected | TUB: future owner-selected tub, dedicated overflow/waste/flange; no tile PAN. WALK-IN: Delta M&I 113919 Rev B selected compatible clamped-liner slope/shop and actual four-plane pan | LEVEL original exact wet lab regardless; independent POINT PAN only if owner elects walk-in |",
 "| TX-BATH3 | Owner TUB / WALK-IN UNSELECTED, selected Brizo BT062415-BNX Black Onyx shower POINT (not tub waste) | TUB: future owner-selected tub/waste/flange; no PAN; WALK-IN Brizo 113920 Rev C point drain compatible preslope/liner/weeps/flood shop | LEVEL original exact wet lab regardless; separate POINT PAN only conditional walk-in |",
 "| PH-BATH2 | Selected Duravit TUB, Hansgrohe Matte White, NO tiled shower PAN | Verify tub 59in vs nominal W1 59.496in rough gap before backer/flange, waste-and-overflow, positive sill, niche and tub flange waterproof | Individually wet Sapphire/Sandstone maker WALL/NICHE; LEVEL exact raw wet lab, shower PAN N/A |",
 "| TX-BATH2 | Selected Duravit TUB, Hansgrohe Chrome, basin UNSELECTED, no tiled PAN | Verify original Copper/Sandstone wet wall/niche, independent actual tub waste/flange; no square point or 48in linear shower pan | Clay Soft LEVEL vs conditional EL30 Mexico LEVEL separately exact raw wet lab, no PAN |",
 "| TX-BATH4 | Selected Duravit TUB, Hansgrohe Matte White, NO shower tiled PAN | Individually maker-wet-listed flat Charcoal and optional Soho Ivory niche vs historical unlisted Clara Caviar; match niche waterproof/tub rim | Bone Soft vs KC04 USA LEVEL exact raw wet lab, manufacturer 3/16 grout, PAN N/A |",
 "",
 "## Plumbing/waterproofing inspection sequence without unsupported code claims",
 "",
 "Before any mortar/pan/wet-wall installation, verify actual maker part number, lower-body rough, joint method, flange, clamp, liner and trap from the **exact original selected drain instruction**. Delta DT062412 [official 113919 Rev B](https://media.deltafaucet.com/MandI/113919%20Rev%20B.pdf) and Brizo BT062415 [113920 Rev C](https://media.brizo.com/MandI/113920%20Rev%20C.pdf) depict a traditional presloped mortar and clamped liner POINT sequence; **neither proves compatibility** with an arbitrary surface-bonded membrane, foam pan, separate 48in linear rough, or unselected BT062418/BR62400. Manufacturer has separate 1/4in-per-ft plumbing PIPE fall guidance and 1/4in-per-ft shower MORTAR preslope; drawings alone do not establish actual 1529 measured shower run. Do not assume code flood test duration; witness only actual specified city/manufacturer/inspector-approved test record. Any change in exact manufacturer drain or rough requires new signed owner and architect authority.",
 "",
 "## Real witness/photo sequence",
 "",
 "Rows 01–12 in R21_156_FIELD_INSPECTION_AND_TRADE_WITNESS_HOLD_POINTS.csv are actual GC stop-work/inspection requests. Each needs exact true 1529 project/room identification, field-dimension scan and witness photo/report. N/A rather than FALSE applies only when that physical item does not exist (dry wood-floor powders, absent shower pans, no extra Primary niche, shared WC). A false wet PAN requirement on a Duravit tub is not an additional safety gate. *No* field witness, quote or approval has been asserted completed.",
 "",
 "Do not conceal dimensional clashes: PH2 59in tub vs 59.496in source alcove, PH4 floor 35 vs 27SF, all 25 W1–W3 provisional wall face openings/niche field-face, true drip/tub flange, exact Brizo 7–18mm frame vs Daltile mosaic current 5/16 and old 1/4in, 1/8-vs-3/16 grout source revision, and all exact raw wet DCOF false. Field measured net takes priority over historical provisional geometry; actual full-case material orders use independently approved new net + cut allowance ONCE and confirmed lot cartons. Historical 15%-loaded GROSS must never receive additional waste or become two full LEVEL+PAN orders.",
 "",
 "## Five non-wet/powder/WC inspection branches",
 "",
 "PH/TX WC inherit respective parent Primary LEVEL, must photograph threshold and flange without duplicating floor cartons or requiring a WC shower PAN. PH Powder, TX Powder and TX Powder2 dry vanity WALL and WOOD floor have no tiled wet bath LEVEL or shower PAN; their inspections cover wall faucet/deck faucet correct rough, backing, 1:1 grout, movement, trims, wood junction and purchase signature. TX Powder2 Hansgrohe Tecturis 73072341 is **DECK**, not wall mounted, and owner basin is still unselected. A product's wet applications elsewhere in project never transfer to dry powder or relief material.",
 "",
 "## Exact release authority",
 "",
 "The four-unit dated tile MATERIAL historic source remains $23,572.44, with original 15% waste in gross exactly once. All 27 original material rows and two excluded unpriced Primary extra niche references (NO SCOPE/NO ORDER), 65 original trade actions and 25 provisional W schedules remain in signed R17. Current actual shade/lot supplier carton, Chicago ETA, freight/tax, complete installed GC bid, original manufacturer individual RAW wet LEVEL/PAN lab, owner room cap and all owner/architect/GC/purchaser signatures remain NULL/FALSE. No vendor contact, email, sample order, actual wet inspection or PO performed.",
 "",
 "## Source and trade cross-check",
 "",
 "- R17 13/27/65/25/13 source and technical release system, R18 thirteen buyer three-view/samples, R19 original SGS Zia manufacturer color numeric summary classified Tier B / not original wet raw lab, R20 actual public retail SKU/lot/case discrepancy register.",
 "- R014 6/8 original authentic critiques (worker-9 design FAILED), no formal weighting; R015 source 4 neutral original candidates independently cleared but four authentic worker dispatch held, no scoring. Neither conditional floor proposal is an owner change.",
 "- Eight wet room groups above, 3 wood-floor dry powder rooms and 2 inherited WC rooms total 13. Exact row count: 13 rooms × 12 explicit witness/hold steps = 156, across two copies per room. Rows are evidence requests only.",
 "",
 "**NO OWNER OR GC RELEASE.**"
]
(D/"R21_WET_ROOM_SHOP_AND_PHOTO_WITNESS_MANUAL.md").write_text("\n".join(book)+"\n",encoding="utf-8")
(D/"START_HERE_R21.md").write_text("# R21 field shop witness and release evidence hold schedule\n\nRead R21_WET_ROOM_SHOP_AND_PHOTO_WITNESS_MANUAL.md and 156-row trade witness CSV. This is a production GC evidence request only; no certified native 1529 model, approved membrane, raw individual wet lab, completed test, vendor order or PO is claimed. Owner and project approval FALSE. Previous signed R12–R20 and R014/R015 neutral sources preserved.\n",encoding="utf-8")
out=sorted(p for p in D.iterdir() if p.is_file());assert len(out)==3
manifest={
 "as_of":"2026-11-06","kind":"13-room installation/waterproofing 12-step per-room source-specific trade witness and inspection request",
 "rooms":13,"copies_per_room":2,"unique_wet_rooms":8,"actual_Duravit_tub_only_rooms":3,
 "actual_linear_shower_pan_rooms":2,"owner_held_conditional_POINT_pan_rooms":2,"selected_point_walkin_rooms":1,
 "dry_wood_floor_powder_rooms":3,"shared_primary_floor_WC_rooms":2,
 "evidence_hold_rows":156,
 "original_hist_material_4unit_usd":"23572.44","original_15pct_waste_in_old_gross_once":True,
 "original_R17_sha":fp(R17)["sha256"],"original_R18_sha":fp(R18)["sha256"],
 "original_R19_sha":fp(R19)["sha256"],"original_R20_sha":fp(R20)["sha256"],
 "original_R014_source_sha":fp(S/"ROUND014_SUBMISSION.json")["sha256"],
 "original_R015_source_sha":fp(S/"ROUND015_SUBMISSION.json")["sha256"],
 "R014_scoring":None,"R015_scoring":None,
 "actual_1529_field_verified":False,"actual_inspections_completed":False,
 "owner_approval":False,"GC_release":False,"procurement_release":False,
 "outputs":{p.name:fp(p) for p in out}
}
(D/"MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert all(fp(D/k)==v for k,v in manifest["outputs"].items())
print("PASS R21 156 independent room-specific original hold points, 13 rooms/8 wet/3 tub/2 linear/1 selected point/2 conditional point/3 powder/2 WC, 3 SHA signed outputs; no original source/release changes")
print("R21_MANIFEST_SHA",fp(D/"MANIFEST.json")["sha256"])

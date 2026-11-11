"""One-time R015 neutral source prep TX Bath2/Bath4, no critic dispatch or weighting.

User-selected Duravit tubs fixed; SOURCE packets role-neutral; private _key only prime/Reviewer.
No historical files modified. Maker data are bounded and raw wet test remains NULL.
"""
from pathlib import Path
from decimal import Decimal
import hashlib,json,re

R=Path(__file__).resolve().parents[1]
S=R/"state"
SUB=S/"ROUND015_SUBMISSION.json"
RESEARCH=R/"research/products/R15_TX_TUB_PAIR_EL30_KC04_INDIVIDUAL_MAKER_WET_APPLICATION_20261106.md"
assert not SUB.exists() and not RESEARCH.exists(), "R015 source already frozen"
ROOMS=["TX-BATH2","TX-BATH4"]
original={"TX-BATH2":"999.92","TX-BATH4":"1320.82"}
variants={
 "TX-BATH2":{
  "A":{
   "wall":"ELM Tones Copper 2×20 Glossy, vertical stack, wet surround",
   "niche":"ELM Tones Sandstone 2×20 Glossy, existing recess",
   "floor":"Daltile Prime White Elect EL30 12×24 Matte USA, LEVEL ONLY",
   "wallurl":"https://www.elmsurfaces.com/product/copper-tones",
   "nicheurl":"https://www.elmsurfaces.com/product/sandstone-tones",
   "floorurl":"https://www.daltile.com/products/stone-look/prime/white-elect",
   "levelgate":"Maker Prime White Elect EL30 Target wet ≥0.42 is NOT a raw exact measured wet lab reading; LEVEL FAIL; tub means shower tiled PAN N/A",
   "layout":"Vertical 2×20 Copper on W1–W3; balanced vertical cut heights after 93in assumed field and actual tub flange / shower valve axes; no 20in-wide field promise before calibrated size and grout.",
   "decision":"Warm Copper/Chrome tub surround and light White Elect 12x24 matte bath LEVEL. This creates an intentional luminous contrast while maintaining Sandstone existing niche and avoiding expensive partial tub-to-walk-in conversion.",
   "newquote":"No current White Elect SKU lot/carton/price or TX2 installed bid; historic $999.92/unit remains the dated source comparator only."
  },
  "C":{
   "wall":"ELM Tones Copper 2×20 Glossy, horizontal stacked wet surround",
   "niche":"ELM Tones Sandstone 2×20 Glossy, existing recess",
   "floor":"ELM Cortar Clay Soft 12×24, LEVEL ONLY",
   "wallurl":"https://www.elmsurfaces.com/product/copper-tones",
   "nicheurl":"https://www.elmsurfaces.com/product/sandstone-tones",
   "floorurl":"https://www.elmsurfaces.com/product/cortar-clay",
   "levelgate":"Exact original Cortar Clay Soft LEVEL raw measured individual wet DCOF is absent; LEVEL FAIL; no tested alternative gets transferred; TUB shower tiled PAN N/A",
   "layout":"Horizontal 2×20 Copper modules across W1–W3, W1 rough 62.484in; balanced cut and grout after true field width, actual 2×20 caliber and valve/niche piercings.",
   "decision":"Warm Copper/Chrome tub surround with Clay Soft 12x24 bath LEVEL and existing Sandstone niche; warm-on-warm palette must be mockup compared with Chrome and bath lighting.",
   "newquote":"Dated 2026-09-03 source rows total $999.92/unit only; not a current trade quote or signed GC allowance."
  }
 },
 "TX-BATH4":{
  "B":{
   "wall":"ELM flat Cortar Charcoal 24×48 Soft, wet tub surround; not relief",
   "niche":"ELM Soho Ivory 2×10 Glossy, conditional wet-listed recess",
   "floor":"Daltile Prime Grey Koncrete KC04 12×24 Matte USA, LEVEL ONLY",
   "wallurl":"https://www.elmsurfaces.com/product/cortar-charcoal",
   "nicheurl":"https://www.elmsurfaces.com/product/soho-ivory",
   "floorurl":"https://www.daltile.com/products/stone-look/prime/grey-koncrete",
   "levelgate":"Grey Koncrete KC04 Target wet ≥0.42 / 1/8in joint recommendation is NOT exact raw measured individual wet DCOF; LEVEL FAIL; Duravit tub means PAN N/A",
   "layout":"Set 24×48 flat Charcoal as zero-offset dry-laid panels around actual 60in source tub back and 30.48in side returns. Ivory 2×10 niche is independent 9.5mm tile; support returns and positive sill draining INTO tub, edge profiles/caliber, movement at every change of plane.",
   "decision":"Charcoal wet wall with reflective Ivory niche, neutral Grey Koncrete bath LEVEL and Matte White Hansgrohe. Improve reflection/usable niche daylight without representing Ivory as owner selected.",
   "newquote":"No current KC04/Soho supplier SKU, available lot, case yield, quote or installed bid; $1320.82/unit historical source only."
  },
  "C":{
   "wall":"ELM flat Cortar Charcoal 24×48 Soft, wet tub surround; not relief",
   "niche":"ELM Clara Tierra Madre Caviar 2×8, existing accent recess",
   "floor":"ELM Cortar Bone Soft 12×24, LEVEL ONLY",
   "wallurl":"https://www.elmsurfaces.com/product/cortar-charcoal",
   "nicheurl":"https://www.elmsurfaces.com/product-collection/clara-collection",
   "floorurl":"https://www.elmsurfaces.com/product/cortar-bone",
   "levelgate":"Original Cortar Bone Soft 12×24 exact LEVEL raw numeric wet test missing; LEVEL FAIL. Clara Caviar individually listed Wet Areas permission absent; NICHE FAIL. TUB PAN N/A.",
   "layout":"Zero offset nominal 24×48 Charcoal panels at tub alcove 60in back / 30.48in each return; niche 2×8 Caviar set in a single documented joint grid, actual niche face/back/returns/sill and external trim LF unmeasured.",
   "decision":"Contrast of Charcoal wet walls with Caviar accent and Bone Soft bath LEVEL; visually darker original niche variant requires separate Wet Areas authorization and lighting mockup.",
   "newquote":"Source $1320.82/unit dated 2026-09-03, including 15% source gross waste once; no current bid."
  }
 }
}

maker = """# R015 TX tub-room exact-maker palette and raw wet lab hold — neutral shared research, 2026-11-06

All material options are independently source-linked choices for a conditional board; this sheet does NOT mark any candidate as a source, a challenger, prior champion or winner. Each room's existing 2026-09-03 quoted source is preserved equally as common budget provenance; no new maker/retailer quote is implied. Owner has already selected Duravit TUB for BOTH rooms. TX Bath2 Hansgrohe CHROME and BASIN UNSELECTED; TX Bath4 Hansgrohe MATTE WHITE and no unselected basin clause. Both rooms have NO tiled shower PAN. PH/TX Primary 48-in LINEAR and Bath3 point drains do NOT belong in these tub rooms.

| Exact maker item | Source and application | Release gate |
|---|---|---|
| ELM Tones Copper 2×20 Glossy | [Individual Copper](https://www.elmsurfaces.com/product/copper-tones) Wet Areas-listed wet WALL; TX2 selected surround | Each actual finish/order code/lot and wall waterproof section must be matched |
| ELM Tones Sandstone 2×20 Glossy | [Individual Sandstone](https://www.elmsurfaces.com/product/sandstone-tones) Wet Areas-listed NICHE | Niche opening subtracted from field once, back/returns/sill plus positive inward fall verified |
| ELM flat Cortar Charcoal 24×48 Soft | [Individual flat Charcoal](https://www.elmsurfaces.com/product/cortar-charcoal) tub WALL Wet Areas-listed. NEVER transfer to ribbed/reed. | Flatness, bow, zero-offset grid, tub flange and wet joint/shop sample |
| ELM Clara Tierra Madre Caviar 2×8 | [Collection-level Clara](https://www.elmsurfaces.com/product-collection/clara-collection) lists floors/walls/outdoor, not individual Caviar Wet Areas | Individual Caviar wet NICHE authorization ABSENT, FAIL until provided |
| ELM Soho Ivory 2×10 Glossy | [Exact color Soho Ivory](https://www.elmsurfaces.com/product/soho-ivory) Wet Areas explicitly PASS (9.5mm nominal) | Niche only, not floor or inherited Caviar listing; actual carton/lot/edge and current installed bid UNKNOWN |
| ELM Cortar Clay Soft 12×24 | [Clay](https://www.elmsurfaces.com/product/cortar-clay) source bath LEVEL | No individual exact raw numeric wet DCOF. Does not inherit Emser/Prime tests |
| ELM Cortar Bone Soft 12×24 | [Bone](https://www.elmsurfaces.com/product/cortar-bone) source bath LEVEL | No individual exact raw numeric wet DCOF. Does not inherit newer maker tests |
| Daltile Prime White Elect EL30 12×24 Matte | [Exact White Elect](https://www.daltile.com/products/stone-look/prime/white-elect), USA 3/8in nominal | Wet LEVEL Target >=0.42 is a maker target, NOT actual raw lab data; grout suggestion and carton/yield/price confirmed separately |
| Daltile Prime Grey Koncrete KC04 12×24 Matte | [Exact Grey Koncrete](https://www.daltile.com/products/stone-look/prime/grey-koncrete), USA 3/8in nominal | Wet LEVEL Target >=0.42 is maker target NOT actual raw individual measured DCOF. Current maker joint 1/8in; verify revision/caliber |

**Scope and source:** Both selected Duravit tubs remain, NO tiled PAN; neither tub room may inherit LEVEL lab evidence from a differently colored, formatted or finished product, and dry wood-floor powders have no wet tile LEVEL floor to test. Exact measured 1529 W1-W3, niche dimensions, tube flange, current Chicago lot/ETA/carton SF, freight/installed bid, room cap and authorized sample/GC scope are NULL. [Manufacturer Daltile Prime catalog](https://www.daltile.com/products/stone-look/prime/white) records distinct EL30, KC01, BA30 white families; do not switch code by appearance. [KC04 manufacturer](https://www.daltile.com/products/stone-look/prime/grey-koncrete) is not EL32 Grey Elect.

Original 15% waste is already in 2026-09-03 GROSS per-copy quantities. TX2 material-only $999.92/copy, TX4 $1320.82/copy; two copies of each, plus remaining 11 rooms total exact FOUR-unit $23,572.44. No double niche field face, no newly invented SF or carton, no conversion of old retail/MSRP into current installed supplier bid. Market study 14 listings / 9 buildings; 405 W Armitage OT01–OT04 one building; Old Town preferred, Lincoln Park and Gold Coast secondary; PH ~$2.8M / TX ~$2.7M target band $2.4M-$3.2M, unverified competitor tile photographs never assumed.
"""
RESEARCH.write_text(maker,encoding="utf-8")

source_files={}
for rid in ROOMS:
    geometry=json.loads((R/"rooms"/rid/"geometry.json").read_text(encoding="utf-8"))
    room=json.loads((R/"state/ROOMS.json").read_text(encoding="utf-8"))
    record=next(x for x in room["rooms"] if x["id"]==rid)
    walls=geometry["tiled_walls"]
    wall_rows="\\n".join(
       "| "+w["id"]+" | "+str(round(w["length"]["value"]*12,3))+" | "+str(round(w["tiled_height"]["value"]*12,3))+
       " | "+str(round(w["length"]["value"]*w["tiled_height"]["value"],3))+
       " | Field-measure joints/caliber/valve and keep balanced focal end cuts >=3in where workable |"
       for w in walls
    )
    historical="\\n".join("| "+z["surface"]+" | "+z["smartsheet_row_id"]+" | "+str(z["qty_sf_per_unit"])+" | "+str(z["extended_quote_cost_usd_per_unit"])+" |" for z in record["carried_tile_rows"])
    assert abs(sum(Decimal(str(z["extended_quote_cost_usd_per_unit"])) for z in record["carried_tile_rows"])-Decimal(original[rid]))<Decimal("0.01")
    rr=R/"rooms"/rid/"board/round-015"
    assert not rr.exists(),"R015 room source already exists"
    (rr/"candidates").mkdir(parents=True)
    source_files[rid]={}
    for letter,v in variants[rid].items():
        tx2=rid=="TX-BATH2"
        title="# "+rid+" — Candidate "+letter+" — complete tile design option"
        fields=[
        title,
        "",
        "This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.",
        "",
        "## Exact maker/finish and room-wide physical design",
        "",
        "| Surface | Proposed independently reviewable material | Actual individual manufacturer reference | Gate |",
        "|---|---|---|---|",
        "| WET tub WALL | "+v["wall"]+" | [specific maker]("+v["wallurl"]+") | Individually source-supported Wet Areas, but verify variant, exact product and actual wet backer/flange |",
        "| WET NICHE | "+v["niche"]+" | [individual or collection source]("+v["nicheurl"]+") | "+("Clara Caviar exact individual wet listing ABSENT, FAIL" if "Caviar" in v["niche"] else "Individual maker Wet Areas PASS, installed niche detail still HOLD")+" |",
        "| Bath LEVEL floor | "+v["floor"]+" | [specific maker format/color]("+v["floorurl"]+") | "+v["levelgate"]+" |",
        "| Shower tiled PAN | **NONE — owner-selected Duravit TUB** | [selected room plumbing](../../plumbing.json) | **N/A; NO 4-in point or 48-in linear shower drain** |",
        "",
        "Owner-selected plumbing is Duravit actual tub with Hansgrohe "+("CHROME; sink/basin remains OWNER UNSELECTED" if tx2 else "MATTE WHITE; no TX Bath2 unselected-basin instruction imported")+". Preserve finished metal escutcheon, tub waste/overflow, flange to board waterproof interface, tub rim and niche positive fall, no shower tiled PAN.",
        "",
        "## Design intent and Old Town buyer value",
        "",
        v["decision"],
        "Existing market evidence has 14 listings but nine independent buildings; 405 W Armitage OT01–OT04 is only one building, no independently authenticated competing bathroom tile photos. Old Town within 24 months is primary; Lincoln Park/Gold Coast secondary. Expected TX sell ~$2.7M (PH ~$2.8M), band $2.4M–$3.2M. Do not use comp photos as precise competitor tile specifications. [Evidence](../../../../research/comps/COMPS.md).",
        "",
        "## Provisional measured dimensions, layout, movement, trims and opening deductions",
        "",
        "The actual 1529 native model has NOT been verified: the connected Revit project title is 1527. All dimensions are provisional copied from [room geometry](../../geometry.json); no unverified field wall measurements are certified.",
        "",
        "| Wall | W1–W3 assumed width (in) | Assumed tiled height (in) | Theoretical gross face SF BEFORE original waste | Balanced cuts to verify |",
        "|---|---:|---:|---:|---|",
        wall_rows,
        "",
        "Specific study: "+v["layout"],
        "Room plan area drawing "+str(geometry["floor_area"]["value"])+" SF is not the orderable net or approved shower-pan area; source original floor quantity already has a 15% factor ONCE. Recalculate at verified 1529 with measured door/window openings, tub rim/curb intersection, valve axes, actual niche aperture **subtract once**, add back/returns/sill each once, soft joint at changes of plane, isolation between tub and tile, exposed metal/ceramic edge linear feet and actual caliber/grout. Do not claim an exact reinstalled trim LF or grout width from the nominal source geometry.",
        "",
        "## Manufacturer wet application and numerical DCOF mandatory gates",
        "",
        "WALL: verify individual wall tile/color/finish Wet Areas authorization for tub wet surround. NICHE: separately confirm exact niche color/finish Wet Areas; do not transfer one collection member permission to another. LEVEL: "+v["levelgate"]+". PAN: **N/A — selected bathtub**, no shower floor drain. The strict project review requires **raw actual exact measured numeric wet DCOF**, not thresholds such as >=0.42, >0.50 or >=0.60 or a brochure Target. Neither this packet nor a maker catalog provides that specific reading. ALL OPTIONS TECHNICALLY HELD until actual raw lab + 1529 field evidence.",
        "",
        "## Historical fixed-scope commercial audit, no quote inferred",
        "",
        "| Original line scope | Original Smartsheet source ID | Gross SF per copy, includes original 15% once | Dated material-only $ per copy |",
        "|---|---|---:|---:|",
        historical,
        "",
        "Historical per-copy material total **$"+original[rid]+"**; two copies. "+v["newquote"]+" Maker MSRP, public retail, exact current Chicago supplier offer, real dye lot, carton SF, lead, freight, installation and owner budget remain distinct and null. No source quantity re-priced from historical ELM rates. No new independent niche face or trim order, or second 15% automatically. Actual purchasable cartons = ceil((verified material-specific net + approved one-time cut allowance)/manufacturer verified carton yield) after owner and GC signatures; presently NULL.",
        "",
        "## Separate architect, GC and owner decision gates",
        "",
        "- Architect and owner: room palette, selected plumbing and "+("OWNER-UNSELECTED sink" if tx2 else "existing selected Matte White tub suite")+", 1:1 samples, 2×20 joint/edge/lighting, $ room cap and recorded owner approval; none granted.",
        "- Plumber: installed selected Duravit tub envelope, correct independent tub waste/overflow, valve rough and accessible connections; NO tiled shower pan. Actual installed rough / shower wet surround flange detail required.",
        "- Waterproof/tile GC: tested local bath **LEVEL** SKU/finish lab number, accepted wet membrane and tub rim interface, niche sill fall, flatness, field-cut grid, movement/edge LF, installed bid, verified full-case stock and architect shop drawing; unknown.",
        "- Procurement: signed color/finish/SKU/carton/lot/ETA, current dated Chicago landed supplier quotation, taxes/freight/waterproof/setting labor and approved owner room allowance; no vendor communications, forms or orders.",
        "",
        "## Evidence",
        "",
        "- [Common source-neutral R015 maker application sheet](../../../../research/products/R15_TX_TUB_PAIR_EL30_KC04_INDIVIDUAL_MAKER_WET_APPLICATION_20261106.md)",
        "- [Actual permitted geometry](../../geometry.json) and [selected plumbing](../../plumbing.json)",
        "- [Four independent specialist rubric](../../../../board/BOARD.md) and [owner feedback](../../../../state/OWNER_FEEDBACK.md)",
        "- Exact maker links in the surface table; each individual Wet Areas and floor lab check remains distinct.",
        "",
        "**STATUS:** independent blind design option only; no weighted score, no owner acceptance, no verified 1529 model, no material or GC release."
        ]
        text="\\n".join(fields)+"\\n"
        p=rr/"candidates"/(letter+".md")
        p.write_text(text,encoding="utf-8")
        bb=p.read_bytes()
        source_files[rid][letter]={"file":str(p.relative_to(R)).replace("\\\\","/"),"sha256":hashlib.sha256(bb).hexdigest(),"bytes":len(bb)}
    private={"round":15,"room":rid,"confidential_prime_and_reviewer_only":True,
         "neutral_candidate_roles":({"A":"new White Elect EL30 level + vertical Copper", "C":"historical Clay Soft level + horizontal Copper"} if rid=="TX-BATH2" else {"B":"new Grey Koncrete KC04 level + Soho Ivory wet niche","C":"historical Cortar Bone Soft + Clara Caviar niche"}),
         "worker_exposure_prohibited":True,"previous_scored_round":12}
    (rr/"_key.json").write_text(json.dumps(private,indent=2)+"\\n",encoding="utf-8")

def fp(p):
    b=p.read_bytes()
    return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
assert not (S/"ROUND015_CRITIC_DISPATCH.json").exists()
assert not (S/"ROUND015_SCORING.json").exists()
payload={
  "round":15, "as_of":"2026-11-06", "phase":"2-board SOURCE_PREFLIGHT_PENDING_INDEPENDENT_REVIEW",
  "rooms":ROOMS,"source_authority":"owner tubs fixed, wet wall individual maker applications, exact source rows and raw bath LEVEL wet lab gaps, genuine new EL30/KC04 floor and TX4 wet niche study",
  "reassessment":"TX2/TX4 both triplex actual Duravit TUB rooms previously R012 blocked; no Bath3 program or shower PAN dependency",
  "candidate_files":source_files,
  "private_keys_prime_and_reviewer_only":{r:str((R/"rooms"/r/"board/round-015/_key.json").relative_to(R)).replace("\\\\","/") for r in ROOMS},
  "shared_neutral_maker_research":str(RESEARCH.relative_to(R)).replace("\\\\","/"),
  "shared_neutral_maker_research_sha256":fp(RESEARCH)["sha256"],
  "market_comps_entries":14,"market_independent_buildings":9,
  "owner_tubs_selected_both":True,"owner_TX_BATH2_basin_selected":False,
  "source_material_usd_per_copy":original,
  "source_15pct_waste_in_gross_once":True,
  "owner_signed":False,"procurement_release":False,"correct_native_1529_verified":False,
  "predispatch_reviewer_verdict":None,"critic_dispatch":"NOT_DISPATCHED",
  "all_critic_scores":None,"weighted_scoring":None
}
SUB.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\\n",encoding="utf-8")
print("PASS R015 two fixed-Duravit-tub TX rooms, 4 source neutral candidate SHA/bytes, common exact maker research; 4 roles private, NO critics dispatched, NO weighting/release")
print("SUBMISSION_SHA",fp(SUB)["sha256"])
print("RESEARCH_SHA",fp(RESEARCH)["sha256"])
for rid,files in source_files.items():
 for letter,x in files.items():
  print(rid,letter,x["bytes"],x["sha256"])

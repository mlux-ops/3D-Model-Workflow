"""Create only NEW, preliminary R020 Primary tile-selection source; never alter R018/R019."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = json.loads((ROOT / "state/ROOMS.json").read_text(encoding="utf-8"))
ROOMS = {x["id"]: x for x in STATE["rooms"]}
PRODUCTS = {
    "Bone": ("ELM Cortar Bone flat Soft porcelain 24x48", "https://www.elmsurfaces.com/product/cortar-bone", "24x48 FLAT Soft, individually listed Wet Areas for WALL, no Reed/Ribbed transfer"),
    "Clay": ("ELM Cortar Clay flat Soft porcelain 24x48", "https://www.elmsurfaces.com/product/cortar-clay", "24x48 FLAT Soft, individually listed Wet Areas for WALL, no Ribbed transfer"),
    "Black": ("ELM Soho Black 2x10 Glossy", "https://www.elmsurfaces.com/product/soho-black", "2x10 Glossy, 9.5mm, individually listed Wet Areas WALL only"),
    "Emerald": ("ELM Soho Emerald 2x10 Glossy", "https://www.elmsurfaces.com/product/soho-emerald", "2x10 Glossy, 9.5mm, individually listed Wet Areas WALL only"),
    "TechLevel": ("Emser Technique Ivory 12x24 Matte, F16TECHIV1224", "https://www.emser.com/product/technique-f16techiv1224", "12x24 pressed porcelain, 9mm, published DCOF >0.60, Commercial Floor Wet YES; LEVEL only"),
    "TechPan": ("Emser Technique Ivory 2x2 mesh Matte, F16TECHIV1212MO", "https://www.emser.com/product/technique-f16techiv1212mo", "2x2 shower mosaic 9.5mm, published DCOF >0.60, Residential Shower Floor YES; LINEAR PAN only"),
    "Trosa": ("Emser Capisco Trosa 12x24 Matte, F08CAPITR1224M", "https://www.emser.com/product/capisco-f08capitr1224m", "12x24 rectified 9mm, published DCOF >=0.60, Commercial Floor Wet YES; LEVEL only"),
    "Boden": ("Emser Capisco Boden 12x24 Matte, F08CAPIBO1224M", "https://www.emser.com/product/capisco-f08capibo1224m", "12x24 rectified 9mm, published DCOF >=0.60, Commercial Floor Wet YES; LEVEL only"),
    "SourcePan": ("Emser Source Pure White 2x2 mesh Matte, W71SOURPWH1212MO2", "https://www.emser.com/product/source-w71sourpwh1212mo2", "2x2 unglazed porcelain, 6mm, published DCOF >0.60, Residential Shower Floor YES; LINEAR PAN only; do NOT use 6mm tile in 7-18mm grate insert"),
}
CFG = {
    "PH-PRIMARY": {
        "A": {"wall": "Bone", "feature": None, "level": "TechLevel", "pan": "TechPan", "grate": "Solid BNX factory grate OR exact manufacturer-confirmed tile insert using a separately approved thickness-compatible 9.5mm tile: do not infer finished mortar/frame clearance.", "story": "Quiet limestone-like Bone field and closely coordinated warm Ivory 12x24 LEVEL / 2x2 LINEAR mosaic pair; black-on-black Brizo drain and shower controls remain the main contrast."},
        "C": {"wall": "Bone", "feature": "Black", "level": "Trosa", "pan": "SourcePan", "grate": "SOLID factory Black Onyx grate only for this proposed 6mm shower mosaic; 6mm is below Brizo's 7-18mm direct tile-in insert range, so never place the Source mosaic directly in the tile-in insert.", "story": "Low-relief Bone field with a bounded glossy black 2x10 WET WALL panel (not a niche); taupe stone-look LEVEL floor and crisp white LINEAR mosaic keep BNX equipment intentional."},
    },
    "TX-PRIMARY": {
        "B": {"wall": "Clay", "feature": None, "level": "TechLevel", "pan": "TechPan", "grate": "Solid BNX factory grate OR verified 9.5mm tile-in configuration when manufacturer and installer document entire section.", "story": "All-flat warm Clay stone-look shower walls against warm Ivory 12x24 LEVEL and related 2x2 LINEAR mosaic; elegant quiet counterpoint to extensive Brizo Black Onyx fixtures."},
        "C": {"wall": "Clay", "feature": "Emerald", "level": "Boden", "pan": "SourcePan", "grate": "SOLID factory Black Onyx grate only for this 6mm PAN mosaic; Brizo tile-in direct 7-18mm thickness range excludes an unmodified 6mm tile-in insert.", "story": "Clay flat main wet walls with a tightly bounded wet-listed glossy Emerald 2x10 focal plane replacing unverified Ribbed relief; pale Boden LEVEL and Source white LINEAR mosaic offset darker BNX hardware."},
    },
}
RESEARCH = {
    "research/products/R020_EMSER_TECHNIQUE_IVORY_F16TECHIV1224_LEVEL_INDIVIDUAL_WET_DCOF.md": """# R020 exact Technique Ivory LEVEL floor (observed 2026-11-06)

Official Emser individual https://www.emser.com/product/technique-f16techiv1224 confirms **Technique Ivory 12x24 Matte, F16TECHIV1224**, porcelain pressed edge, 9 mm, recommended 1/8-inch joint and 543 Driftwood grout. Individual page gives published **wet DCOF >0.60**, Commercial Floor Wet YES and Residential Floor YES. This meets board/BOARD.md's *published product-specific* wet DCOF >=0.42 for the **bath LEVEL** only. It is NOT a raw exact laboratory result or proof that large-format tile can follow a shower slope.

Matching separate manufacturer mosaic https://www.emser.com/product/technique-f16techiv1212mo has exact **F16TECHIV1212MO 2x2/12x12**, 9.5 mm, published **DCOF >0.60**, Residential Shower Floor YES, 1/8-inch recommended joint. LEVEL 9mm vs mosaic 9.5mm nominal difference **0.5mm**, NOT complete installed floor buildup. Product identity is manufacturer's 2x2, regardless of any retailer page mistakenly labeling the same SKU '1x3'; do not use retailer's format or price without correction.

Manufacturer US active pages support U.S. distribution, NOT Bensenville/Chicago on-hand boxes, lead time, factory shade lot, usable carton yield or local price. Seller evidence NOT quoted for this exact matched variant. No owner/GC/site/test release.
""",
    "research/products/R020_ELM_BONE_CLAY_EXACT_FLAT_WET_WALL_SOURCE.md": """# R020 individually permitted flat Bone and Clay wet WALL (observed 2026-11-06)

Official ELM https://www.elmsurfaces.com/product/cortar-bone and https://www.elmsurfaces.com/product/cortar-clay list the respective **Bone** and **Clay** flat product pages, **24x48** size, **Soft** finish, and **Walls / Wet Areas** among applications. These are flat individually listed wet WALL surfaces, not a transferable permit for distinct **Reed** / **Ribbed Relief** products. Both 24x48 flat tiles are proposed only for shower WALL and historical ceiling scope; manufacturer page's wall listing does not independently clear ceiling overhead bonding / fastening, which stays HOLD.

Selected Brizo Black Onyx shower trims are unchanged. A controlled BOUNDED Soho Black 2x10 glossy PH feature or Soho Emerald 2x10 glossy TX feature is another independently maker wet WALL listed product; each replaces part of existing quoted wall gross, not extra niche/tile. https://www.elmsurfaces.com/product/soho-black and https://www.elmsurfaces.com/product/soho-emerald each list Wet Areas and 9.5mm. Actual W2 wall interval, valving, vertical module, reveals, plane transitions, complete project cost and live dimensions are UNKNOWN. Never transfer maker wet permission to original Bone Reed or Clay Ribbed.

Original Smartsheet $8.14/SF wall rows are historical composite Bone/Clay wall+ceiling+relief rates, not a newly quoted purchase rate for alternate panel or verified currently available Chicago lot. No outreach or release.
""",
    "research/products/R020_BRIZO_BNX_48_LINEAR_TILE_FRAME_SOLID_AND_WP_GATE.md": """# R020 selected Brizo Black Onyx 48-inch LINEAR and separate rough — exact 2026 source

Official https://www.brizo.com/bath/product/BT0734816-BNX identifies **BT0734816-BNX**, 48-inch reversible linear shower drain **Brilliance Black Onyx**, delivered grate/frame. It explicitly supports **solid finish-matched metal grate** or **tile insert**; tile-adjustable frame specified for nominal tile thickness **7–18 mm**, not approval of any particular mortar, waterproof layer or field tile. Official https://www.brizo.com/bath/product/BR73480 identifies **BR73480** required separate 48-inch rough, stainless channel with integral slope, patented Water Protection System; drain trim and rough are separate items. Historical rough appearance in more than one Smartsheet row does NOT mean order two roughs.

**Gate option 1:** Emser Technique Ivory 2x2 mesh F16TECHIV1212MO, exact **9.5mm** and shower-floor wet DCOF >0.60 (maker), meets 7-18mm nominal tile insert range **numerically**, but full setting/waterproof/frame/linear slope compatibility must still be factory/installer verified; alternatively use factory BNX solid grate.

**Gate option 2:** Emser Source Pure White 2x2 mesh W71SOURPWH1212MO2 exact **6mm**, maker shower-floor wet >0.60, is **under** 7mm insert minimum; do not pretend it directly fits Brizo tile-in frame. Candidate using Source must use Brizo **factory BNX SOLID grate** and separately install the mosaic on the shower floor around the drain, subject to actual rough/membrane/flood-tested system. Neither design adds niches or converts 48in LINEAR to POINT.

Maker individual floor: https://www.emser.com/product/technique-f16techiv1212mo and https://www.emser.com/product/source-w71sourpwh1212mo2 . Both have individual Residential Shower Floor YES, maker DCOF >0.60 and 1/8in recommended joint; data are lower bounds, not raw laboratory point values. PH/TX separately need true site LINEAR pan and LEVEL boundaries, correct drain slope/path and substrate/membrane support. No complete system approval or PO.
""",
    "research/products/R020_PRIMARY_CHICAGO_AVAILABILITY_AND_PUBLIC_PRICE_NOT_LOCAL_QUOTE.md": """# R020 Primary manufacturer distribution and price source control (observed 2026-11-06)

Emser current individual US pages for F16TECHIV1224, F16TECHIV1212MO, F08CAPIBO1224M, F08CAPITR1224M, W71SOURPWH1212MO2 are live published listings. Official **Emser Chicago-region design showroom**, 880 Devon Ave, Bensenville IL 60106: https://www.emser.com/EnhanceDesignShowrooms . ELM current individually listed Bone, Clay and Soho Black/Emerald wet products indicate US catalog route. This confirms a **local showroom/contact route**, NOT a specific in-stock Chicago warehouse shade lot, quantity, sellable box, freight or vendor commitment; per-SKU local stock/ETA all UNKNOWN.

Exact external **Emser Source Pure White W71SOURPWH1212MO2** public US listings (not Chicago): https://www.gbtilecollections.com/emser-source-pure-white-matte-porcelain-mosaic.html posted $11.77 PER 0.95-SF PIECE, equivalent about $12.39/SF *unrounded illustration only*; https://stoneandtileshoppe.com/products/source-w71sourpwh-pure-white-solid-2x2-porcelain-mosaic posted $14.69/SF, retailer-claimed in stock, 0.95 SF/sheet and 10.44 SF/box. These *conflicting offers* are not local quotes or owner price approvals. Another retailer labels Emser Technique Ivory SKU F16TECHIV1212MO as '1x3' although manufacturer names it 2x2, so exclude that retailer's $/SF from specification identity. Exact Emser Technique and Capisco matched prices at Chicago are UNKNOWN. Do not price pan totals from guessed pan SF.

Original read-only Smartsheet rates: PH-PRIMARY WALL $8.14/SF 143.00 gross (includes ceiling), FLOOR blended $7.82/SF 135.60 gross (contains PH WC), total $2,224.41/copy; TX-PRIMARY WALL $8.14/SF 134.40 gross, FLOOR blended $7.80/SF 116.10 gross (contains TX WC), total $1,999.60/copy; both Primary no niche allowance, neither has split published LEVEL vs sloped LINEAR PAN net quantities. Historical 15% waste already once. Do not apply old blended rate to alternate Emser products or invent owner budget cap.
""",
}

def product(id):
    name, url, permission = PRODUCTS[id]
    return f"[{name}]({url})", permission

def make_candidate(room_id, letter, conf):
    room = ROOMS[room_id]
    g = json.loads((ROOT / "rooms" / room_id / "geometry.json").read_text(encoding="utf-8"))
    assert room["status"] == "blocked" and room["champion_id"] is None
    rr = {v["surface"]: v for v in room["carried_tile_rows"]}
    assert set(rr) == {"wall","floor","accent"} and rr["accent"]["extended_quote_cost_usd_per_unit"] is None
    field, fp = product(conf["wall"])
    level, lp = product(conf["level"])
    pan, pp = product(conf["pan"])
    feat = "NONE: use only flat wet-listed full-wall Bone/Clay, no relief or niches." if conf["feature"] is None else product(conf["feature"])[0] + ": replace a bounded existing wet-wall feature only, never add gross wall quantity or niche."
    walls = "; ".join(f'{w["id"]}: {w["length"]["value"]:.4f} ft x {w["tiled_height"]["value"]:.2f} ft (drawing-derived)' for w in g["tiled_walls"])
    floor_foot = g.get("shower_or_tub_footprint", {})
    return "\n".join([
        f"# {room_id} — Candidate {letter} — independent neutral tile-design option",
        "",
        "This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.",
        "",
        "## Confirmed selected plumbing/program and architectural choice",
        "Owner-selected Brizo **BT0734816-BNX** **48-inch Black Onyx LINEAR shower drain**, with required **separate BR73480 rough**, factory solid BNX grate or only dimensionally compatible tile-in insert. Keep Brizo Black Onyx selected fixture finish, freestanding tub if scheduled, and **NO additional PRIMARY niches**. WC tile flooring is inherited inside this Primary room floor quote; **no independent WC tile purchase**. Two copies per unit type; no change to fixtures or toilet.",
        f"**WET SHOWER WALL**: {field}. Feature sub-area: {feat}. **BATH LEVEL**: {level}. **SEPARATE 48-IN LINEAR SHOWER PAN**: {pan}; 2x2 mesh mosaic explicitly manufacturer-residential-shower-floor listed. **Drain grate variant**: {conf['grate']}",
        f"**Design thesis:** {conf['story']}",
        "",
        "## Exact manufacturer and source-rate evidence (original 15% waste included once)",
        "| Application / old Smartsheet row | Current candidate material; exact manufacturer document | Historical original SF gross per copy | Original quote USD/copy @ rate | Status / price limitation |",
        "|---|---|---:|---:|---|",
        f'| Wet wall plus historical ceiling / {rr["wall"]["smartsheet_row_id"]} | {field} (maker individual **Walls + Wet Areas YES**, only FLAT finish) | {rr["wall"]["qty_sf_per_unit"]:.2f} | ${rr["wall"]["extended_quote_cost_usd_per_unit"]:.2f} @ ${rr["wall"]["quoted_rate_usd_per_sf"]:.2f}/SF | Wet WALL product gate supported; any overhead ceiling fastening approval separate; alternate feature allocation/pricing unknown |',
        f'| Bath LEVEL including inherited WC / {rr["floor"]["smartsheet_row_id"]} | {level}, {lp} | {rr["floor"]["qty_sf_per_unit"]:.2f} **BLENDED LEVEL+PAN+WC original** | ${rr["floor"]["extended_quote_cost_usd_per_unit"]:.2f} @ ${rr["floor"]["quoted_rate_usd_per_sf"]:.2f}/SF | Manufacturer published wet >=0.42 threshold satisfied; no invented substitute $/SF or pan split |',
        f'| Distinct LINEAR PAN / same historic combined floor row, NOT additive old scope | {pan}; {pp} | NULL, actual sloped PAN boundaries needed | NULL (no separate historical item or replacement quote) | Separate residential wet shower-floor listing and published DCOF >0.60; exact drain and waterproof system pending |',
        "| Excluded historical Primary accent/niche | **NO NICHE, no tile, no purchase**, no additional allowance | Excluded historic reference quantity only | $0.00 priced | Never add new niche or count excluded reference gross |",
        "",
        "## Maker hard-gate proof and exact physical differences",
        f'Field wet permission: {fp}; if a 2x10 feature is used its *own* exact individual maker Wet Areas listing supports only wet WALL, not LEVEL/PAN. No Reed/Ribbed source permission may be borrowed from flat.',
        f'Bath LEVEL: {lp}. Separately sloping LINEAR PAN: {pp}. These published product-specific DCOF **bounds** exceed 0.42 under board/BOARD.md, not raw measured laboratory point test results. The LEVEL large-format tile is not proposed on the LINEAR shower slope.',
        'Drain: [official selected BT0734816-BNX](https://www.brizo.com/bath/product/BT0734816-BNX) + [independent required BR73480 rough](https://www.brizo.com/bath/product/BR73480). Manufacturer reversibility and tile-in nominal 7–18 mm range are NOT system waterproof or mortar clearance approvals. ' + conf["grate"],
        'Nominal manufacturer tile/thickness: technique LEVEL pressed 12x24 9mm; technique 2x2 shower mosaic 9.5mm; Capisco LEVEL rectified 12x24 9mm; Source 2x2 mosaic 6mm. 1/8-inch mosaic joint manufacturer recommended (not a 3/16 Prime RL21 substitution); grout sample color still to be approved. No assumed identical finished assembly heights.',
        "",
        "## Geometry, comp, local distribution, material cost and decision gates",
        "Owner confirmed native model title 25-006 1527 N Wieland **is the 1529 building**. Room-specific Revit wall/room element IDs, drain elevations and openings have NOT been certified; no fabricated receipt. Provisional source walls: " + walls + ". Validate nominal 24-in wall modules, focal return slivers >=3in with grout/caliber and fixtures, shower LINEAR slope/pan boundary and 48-in rough placement. Site and actual native element receipts required.",
        "Chicago availability: maker currently distributes in the US; official Emser Chicago-region showroom 880 Devon Ave, Bensenville IL ([official](https://www.emser.com/EnhanceDesignShowrooms)); no specific matching Chicago carton stock/lead or lot confirmed. Feature and substituted floor SKU current project price/box coverage/freight/installed labor NULL. [Product/pricing source detail](../../../../../research/products/R020_PRIMARY_CHICAGO_AVAILABILITY_AND_PUBLIC_PRICE_NOT_LOCAL_QUOTE.md).",
        f'Historical carried material-only total **${room["carried_quote_material_subtotal_usd_per_unit"]:.2f} per Primary copy**, including inherited WC floor and original 15% gross ONCE; existing blended floor quote must be deconvolved into LEVEL+LINEAR PAN+WC prior to alternate order. No allocated owner budget/cap is supplied; board 125% cost gate cannot be calculated from unknown current alternate price. Distinguish material from labor and never invent savings.',
        "Market: OT01–OT04 at 405 W Armitage share ONE Old Town boundary development; OT05 1849 N Mohawk separate. 405 W Armitage published primary program supports steam shower/tub competition, **not exact tile SKU/grout**. The individually inspected OT01 photo depicts a patterned powder-type bathroom, not a Primary wet wall ([photo observation](../../../../../research/comps/R020_OLD_TOWN_ATRIBUTABLE_BATH_PHOTO_OBSERVATIONS.md)). LP/GC remain secondary.",
        "Owner-only: confirm neutral palette/feature (if any), actual pan design and grate orientation, 1:1 wall/LEVEL/PAN grout and edge, final cost ceiling and sample palette. Installer-only: 48in rough/membrane slope, true opening/cut grid, shower floor and ceiling assemblies. All releases FALSE; no order, outreach, native model change or additional niche.",
        "",
    ])

receipt = ROOT / "state/ROUND020_PRIMARY_TILE_SOURCE_PREPARED_NOT_SUBMITTED.json"
assert not receipt.exists()
for path in RESEARCH:
    assert not (ROOT / path).exists()
for room in CFG:
    assert not (ROOT / "rooms" / room / "board" / "round-020").exists()
paths = {}
for name, body in RESEARCH.items():
    p = ROOT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8", newline="\n")
    b = p.read_bytes()
    paths[name] = {"sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)}
for room, letters in CFG.items():
    for letter, params in letters.items():
        name = f"rooms/{room}/board/round-020/candidates/{letter}.md"
        p = ROOT / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(make_candidate(room, letter, params), encoding="utf-8", newline="\n")
        b = p.read_bytes()
        paths[name] = {"sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)}
parents = {}
for name in ("state/ROUND018_TUB_TILE_SOURCE_PREPARED_AWAIT_BLIND_PREFLIGHT.json",
             "state/ROUND019_TILE_ONLY_NEXT_COHORT_SOURCE_AWAIT_R018_FORMAL_CLEARANCE.json"):
    b = (ROOT/name).read_bytes()
    parents[name] = {"sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)}
data = {"round":20, "as_of":"2026-11-06", "cohort":list(CFG),
        "phase":"PRELIMINARY_NEXT_PRIMARY_TILE_SOURCE_ONLY",
        "formal_board_submitted":False,"source_frozen_for_critics":False,
        "independent_predispatch_clearance":None,"four_specialist_critics_collected":False,
        "original_design_worker9":"FAILED", "original_reviewer_worker15":"FINISHED",
        "critic_dispatch":"NOT_DISPATCHED","weighted_scoring":None,
        "room_champions_changed":False,"owner_approval":False,"purchase_release":False,
        "private_key_created":False,"all_options_neutral":True,
        "selected_plumbing_BNX_48in_linear_with_BR73480":True,
        "primary_niches_added":False,"wc_floor_inherited_without_duplicate":True,
        "four_unit_historic_material_total_usd":23572.44,
        "original_gross_waste_15_percent_once":True,"prior_receipt_snapshot":parents,
        "draft_files":paths}
receipt.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8",newline="\n")
print("R020 PRELIMINARY SOURCE created",len(paths),"draft files; prior R018/R019 unchanged; receipt",receipt.name)
for key,val in paths.items():
    print(key,val["bytes"],val["sha256"])

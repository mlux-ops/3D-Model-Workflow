"""One-time additive R022 blocked wet-bath tile source; no signed predecessor edits."""
from pathlib import Path
import json
import hashlib

ROOT=Path(__file__).resolve().parents[1]
ROOMS={r["id"]:r for r in json.loads((ROOT/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]}
PRODUCTS={
 "luxe":dict(vendor="Floor & Decor",title="Vetta Elements Luxe Sand Matte Ivory Porcelain Tile",size="24x24",sku="101317949",finish="Matte, rectified, 8mm",price=3.49,box=54.08,coverage=4*3.88,url="https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html",wet="Individual product page: DCOF >=0.42; Shower Floors YES; Shower Walls YES; Bathroom Floor YES."),
 "riva":dict(vendor="Floor & Decor",title="Vetta Elements Riviera Oat Matte Beige Travertine-Look Porcelain Tile",size="24x48",sku="101487775",finish="Matte, rectified, 8mm",price=3.99,box=63.84,coverage=2*8,url="https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html",wet="Individual product page: DCOF >=0.42; Shower Floors YES; Shower Walls YES; Bathroom Floor YES."),
 "bone":dict(vendor="Elm Surfaces",title="Cortar Bone FLAT Soft 24x48",size="24x48",sku=None,finish="Soft / FLAT",price=None,url="https://www.elmsurfaces.com/product/cortar-bone",wet="Individual Bone FLAT Wet Areas WALL listing; does not transfer to Bone Ribbed."),
 "clay":dict(vendor="Elm Surfaces",title="Cortar Clay FLAT Soft 24x48",size="24x48",sku=None,finish="Soft / FLAT",price=None,url="https://www.elmsurfaces.com/product/cortar-clay",wet="Individual Clay FLAT Wet Areas WALL listing; does not transfer to Clay Ribbed."),
 "sohoblack":dict(vendor="Elm Surfaces",title="Soho Black 2x10 Glossy",size="2x10",sku=None,finish="Glossy, 9.5mm",price=None,url="https://www.elmsurfaces.com/product/soho-black",wet="Individual product Wet Areas WALL listed; not floor."),
 "sohoivory":dict(vendor="Elm Surfaces",title="Soho Ivory 2x10 Glossy",size="2x10",sku=None,finish="Glossy, 9.5mm",price=None,url="https://www.elmsurfaces.com/product/soho-ivory",wet="Individual product Wet Areas WALL/NICHE listed; not floor."),
 "sohoemerald":dict(vendor="Elm Surfaces",title="Soho Emerald 2x10 Glossy",size="2x10",sku=None,finish="Glossy, 9.5mm",price=None,url="https://www.elmsurfaces.com/product/soho-emerald",wet="Individual product Wet Areas WALL listed; not floor.")
}
DESIGN={
 "PH-PRIMARY":{
  "A":dict(wall="bone",feature=None,niche=None,floor="luxe",story="monochromatic ivory concrete-look 24x24 uninterrupted LEVEL-to-LINEAR-PAN, black BNX fixtures as contrast",grate="Black Onyx finished factory SOLID grate, not an inferred tile-in recess."),
  "B":dict(wall="bone",feature="sohoblack",niche=None,floor="riva",story="quiet flat Bone field with a controlled wet-listed Soho Black focal WALL and warmer Riviera Oat 24x48 travertine-look LEVEL-to-LINEAR-PAN",grate="Black Onyx finished factory SOLID grate; preserve 48-inch LINEAR drain identity.")
 },
 "TX-PRIMARY":{
  "A":dict(wall="clay",feature=None,niche=None,floor="riva",story="warm flat Clay shower envelope and continuous 24x48 Riviera Oat across LEVEL and sloped LINEAR-PAN, framing BNX black fixtures",grate="Factory SOLID BNX grate, no invented tile-in mortar/frame compatibility."),
  "B":dict(wall="clay",feature="sohoemerald",niche=None,floor="luxe",story="flat Clay main field and deliberately bounded green Soho Emerald 2x10 wet WALL panel, interrupted by quiet 24x24 Luxe Sand continuous LEVEL/PAN",grate="Factory SOLID BNX grate; no change to separately required BR73480 rough.")
 },
 "PH-BATH4":{
  "A":dict(wall="bone",feature=None,niche="sohoblack",floor="luxe",story="flat pale Bone shower walls, high-contrast Soho Black wet NICHE and matte Luxe Sand 24x24 continuous LEVEL-to-four-plane-POINT PAN",grate="Selected Brizo BT062415-BNX Black Onyx 4-inch square POINT; no substitute drain."),
  "B":dict(wall="bone",feature=None,niche="sohoivory",floor="riva",story="all-soft sand and ivory direction, flat Bone and wet-listed Soho Ivory NICHE, with Riviera Oat 24x48 continuous LEVEL-to-four-plane-POINT PAN",grate="Selected Brizo BT062415-BNX Black Onyx square POINT; four-plane field-cut tile by owner installer.")
 },
}
EVIDENCE = """# R022 large-format exact approved-vendor wet-floor source — 2026-11-06

**Latest owner 2026-11-07 supersedes prior small-format recommendations:** allowed vendors only **Elm/MSI/Platform/Floor & Decor**; **24in+ large format preferred for LEVEL AND SHOWER PAN**, owner GC cuts and slopes large-format on the selected drain. No Emser/Daltile current candidate. Published individual product wet DCOF >=0.42 and exact shower-floor use both required.

**Floor & Decor Luxe Sand 24x24 Matte Ivory, 101317949**: https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html individual item **24x24 nominal, 23.70x23.70 actual, 8mm rectified, DCOF >=0.42, Shower Floors YES, Shower Walls YES, Bathroom Floor YES**. Store-dependent posted **$3.49/SF; $54.08/box; four pieces at 3.88 SF each = 15.52 SF/box**. Recommended listed grout joint options 1/16, 1/8 or 3/16; design default **1/8 inch**, owner to sample. No source raw exact measured wet DCOF number beyond seller published threshold. Manufacturer/supplier U.S. catalog active; "87 boxes available"/pickup cited on site for default West Des Moines, NOT Chicago.

**Floor & Decor Riviera Oat 24x48 Matte Beige, 101487775**: https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html individual item **24x48 nominal, 23.58x47.28 actual, 8mm rectified, DCOF >=0.42, Shower Floors YES, Shower Walls YES, Bathroom Floor YES**. Store-dependent posted **$3.99/SF; $63.84/box; two pieces x 8.00 SF = 16 SF/box**. Listed grout joint 1/16, 1/8 or 3/16; proposed **1/8 inch** pending owner/sample. Product is through F&D U.S. route, **not** proof of Chicago matching lot/warehouse carton count, lead or guaranteed price. Beware similarly named Riviera Oat porcelain **PAVER SKU 101486116 20mm thick**: that is NOT the tile here.

**Both products genuinely qualify for proposed large-format LEVEL and independently wet-rated SHOWER FLOOR from the exact individual seller/product pages**, not from another size/color/mosaic. Product-use listing is **NOT approval of actual panelized four-plane POINT cut geometry, linear drain/waterproof assembly, installation thickness, installer acceptance or complete room price**. The owner specifically instructs installer cut/slope; do not reject LFT simply on 4-plane slope, but reject only actual unavoidable <3-in focal-edge slivers once source Revit/field geometry can confirm them. Need source-native receipt IDs for shower footprint, drain center/offset and actual level-pitch boundaries. No engineering/fabrication packet authorized.

**Wet WALL/NICHE remain distinct:** ELM individually listed FLAT Cortar Bone and Clay Soft 24x48 for Wet Areas WALL only; never transfer to Ribbed/Reed, ceilings or floor. ELM individually wet-listed Soho Black/Soho Ivory/Soho Emerald 2x10 Glossy for WALL/NICHE (where used), not floor. Exact manufacturer pages: https://www.elmsurfaces.com/product/cortar-bone , https://www.elmsurfaces.com/product/cortar-clay , https://www.elmsurfaces.com/product/soho-black , https://www.elmsurfaces.com/product/soho-ivory , https://www.elmsurfaces.com/product/soho-emerald . Factory order numbers and current ELM same-lot supplier quotes all NULL.

**Waste controls:** Original Smartsheet gross already contains **15% source waste ONCE**. New pricing model is based on true, subsequently receipt-verified net areas: level net x1.15 + PAN net x1.25 (15% standard plus 10 percentage points extra *only on net cut-heavy pan*) + inherited WC net x1.15; apply mutually exclusively as a **replacement scenario**, NOT on top of historical 15%-gross rows, and do NOT guess PAN net or release quantity now. Note both room origin and 26 physical copies. Shower PAN and LEVEL may share the **SAME SKU**, but are separate installation areas; same-stock physical pooling must not duplicate the WC floor.

**Brizo exact owner drains unchanged:** both Primary **BT0734816-BNX Black Onyx 48-inch LINEAR plus separate BR73480 rough, no niches, WC floor inherited**. R022 uses manufacturer's factory **SOLID Black Onyx grate**, avoiding 7-18mm tile-in frame inference; the new 8mm tile lies numerically within range but full setting stack remains unverified. PH-BATH4 WALK-IN fixed with **BT062415-BNX Black Onyx 4-inch square POINT**, four-plane PAN separate from LEVEL, but cut by selected installer. PH/TX Primary Wall ceiling use must separately be documented where source includes ceiling, not inferred from WALL. No owner program/basin/faucet modification.

**Alternative vendor controls:** MSI Architecta Beige (some individual item published floor wet DCOF >0.42 but 12x24 fallback), MSI Stowe individual 2x2 mosaic not preferred by owner; Platform Surfaces Bensenville real supplier, but maker exact wet floor PAN rating and live price not yet shown. F&D's earlier Luxe 12x24 and 3-in square mosaic now FALLBACK only. This cohort has two fully published eligible F&D large-format LEVEL/PAN products; remaining three-plus cross-vendor comparisons persist in each room's signed `vendor_comparison.md` and a future updated addendum, without pretending Platform price known. Old Town OT01 powder photograph does not establish competitor Primary PAN tile; OT05 no authenticated bathroom photo. All signals observational, not a scored champion.
"""
evidence="research/products/R022_FD_LUXE_SAND_RIVIERA_OAT_24PLUS_LEVEL_AND_SHOWER_PAN.md"
receipt="state/ROUND022_LARGE_FORMAT_PRIMARY_PH4_SOURCE_PRELIMINARY_NOT_SUBMITTED.json"
assert not (ROOT/evidence).exists() and not (ROOT/receipt).exists()
for room in DESIGN:
    assert not (ROOT/"rooms"/room/"board"/"round-022").exists()
p=ROOT/evidence
p.write_text(EVIDENCE,encoding="utf-8",newline="\n")
files={evidence:{"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":len(p.read_bytes())}}
for room, variants in DESIGN.items():
    r=ROOMS[room]
    assert r["status"]=="blocked" and r["champion_id"] is None
    rows={z["surface"]:z for z in r["carried_tile_rows"]}
    geom=json.loads((ROOT/"rooms"/room/"geometry.json").read_text(encoding="utf-8"))
    walls="; ".join(f'{z["id"]}: {z["length"]["value"]:.4f}ft x {z["tiled_height"]["value"]:.2f}ft' for z in geom["tiled_walls"])
    for letter,c in variants.items():
        floor=PRODUCTS[c["floor"]]
        wall=PRODUCTS[c["wall"]]
        feat=PRODUCTS[c["feature"]] if c["feature"] else None
        niche=PRODUCTS[c["niche"]] if c["niche"] else None
        is_primary=room.endswith("PRIMARY")
        plumbing=("Owner-selected Brizo BT0734816-BNX Black Onyx 48-inch LINEAR + separately required BR73480 rough; no new Primary NICHE; respective WC LEVEL flooring inherited once." if is_primary else "Owner-selected WALK-IN and Brizo BT062415-BNX Black Onyx four-inch square POINT; pan four-plane; no TUB program.")
        grout="Nominal 1/8-in grout joint for this 8mm rectified floor product, final color/sample owner-only; never substitute other tile/finish ratings."
        featured=("NONE; flat main wall remains visually quiet." if not feat else f'Bounded separate Wet Areas WALL plane [{feat["title"]}]({feat["url"]}), {feat["finish"]}; owner/geometry must confirm interval; not NICHE or FLOOR.')
        nichestr=("NO niches by owner instruction, original source accent is excluded/unpriced." if is_primary else f'Separate existing NICHE [{niche["title"]}]({niche["url"]}) independently Wet Areas WALL-listed, not the original unsupported Caviar; niche extent/pricing unknown and owner color not selected.')
        floorrow=rows["floor"]
        basis=floorrow["qty_sf_per_unit"]
        rate=floorrow["quoted_rate_usd_per_sf"]
        price=floor["price"]
        original=floorrow["extended_quote_cost_usd_per_unit"]
        theoretical=basis*price
        panlabel=("48in LINEAR PAN" if is_primary else "4-plane 4in POINT PAN")
        cut=("Factory SOLID BNX grate; manufacturer tile-in 7–18mm direct range not assumed as assembled waterproof detail." if is_primary else "POINT cuts and actual drain location constrained by manufacturer and native geometry; no automated four-plane refusal.")
        txt=f"""# {room} — neutral R022 candidate {letter} — LARGE FORMAT source only

This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified. It is NOT an R021 critic report or owner accepted champion.

## Surface-by-surface proposed actual maker products

**Selected plumbing:** {plumbing}

**SHOWER WET WALL:** [{wall['title']}]({wall['url']}) ({wall['size']}, {wall['finish']}): {wall['wet']} **Separate WALL feature:** {featured}

**NICHE:** {nichestr}

**BATH LEVEL:** [{floor['title']}]({floor['url']}) **exact SKU {floor['sku']}**, {floor['size']}, {floor['finish']}; {floor['wet']}.

**SEPARATE {panlabel}:** **SAME exact {floor['sku']} {floor['size']}** large-format tile as LEVEL, in installer-cut sloped planes. Its own manufacturer page states Shower Floors YES and wet DCOF >=0.42; this is product permission, not certified geometry, actual water test or raw numeric DCOF point. {cut} {grout}

**Design rationale:** {c['story']}. Preservation of selected Brizo finish/form is non-negotiable; no extra niches, basin, faucet or fixture substitutions.

## Historic source quantities and cost screening

| Surface | Original Smartsheet ID | Original gross SF per copy (15% waste ONCE) | Carried historic material cost / rate | Candidate new material price status |
|---|---|---:|---:|---|
| Wet WALL + any legacy ceiling allowance | `{rows['wall']['smartsheet_row_id']}` | {rows['wall']['qty_sf_per_unit']:.2f} | ${rows['wall']['extended_quote_cost_usd_per_unit']:.2f} @ ${rows['wall']['quoted_rate_usd_per_sf']:.2f}/SF | Exact alternate ELM wall/feature quote NULL; additional true ceiling tile application/price separately withheld |
| BATH LEVEL + {('inherited WC + LINEAR PAN' if is_primary else 'POINT PAN')} old blended original | `{floorrow['smartsheet_row_id']}` | {basis:.2f} | ${original:.2f} @ ${rate:.2f}/SF | F&D current online ${price:.2f}/SF, **illustrative old combined gross x posted rate = ${theoretical:.2f}/copy**, not box-rounded or installed quote |
| Wet NICHE / source reference | `{rows['accent']['smartsheet_row_id']}` | {rows['accent']['qty_sf_per_unit']:.2f} | {('EXCLUDED, no priced Primary niche' if is_primary else f'${rows["accent"]["extended_quote_cost_usd_per_unit"]:.2f} @ ${rows["accent"]["quoted_rate_usd_per_sf"]:.2f}/SF')} | {('NO new niche' if is_primary else 'Replacement Soho color, actual net/labor/material price NULL')} |

**Historical room material total** ${r['carried_quote_material_subtotal_usd_per_unit']:.2f}/copy x {r['unit_count']} copies; original full four-unit material $23,572.44 unchanged, 15% gross included once. Current total room price is **UNKNOWN**: ELM wall/niche real current price, floor split, true native surface areas, additional cut waste, carton rounding, Chicago lot and owner budget cap unavailable. Do not claim budget PASS or full room material savings. ${price:.2f}/SF is site/default online product rate, not Chicago store on-hand or project fixed quote.

**Quantity replacement scenario (NO invented PAN SF):** verified net LEVEL ×1.15 plus verified net PAN ×1.25, and for Primary include parent WC net ×1.15 exactly once, mutually replacing original combined floor quantity rather than adding waste to its 15%-inclusive original gross. A larger pan cut may require verified higher than 25%; no order quantity generated. The brand's online box rate ${floor['box']:.2f} for {floor['coverage']:.2f} SF, actual required complete cartons = ceil(new approved gross / box coverage) only AFTER geometry. All original 27 historical material rows preserved.

## Source/installation/market hard gates

Owner confirmed 1527=1529 same building. Prior drawing W1–W3 provisional wall lengths/heights: {walls}; these are not element-ID-verified native Revit or field openings. Owner GC installer cuts/slopes LFT through {panlabel}; do not disqualify format merely for slope. Reject only an actual measured unavoidable <3-in focal sliver or manufacturer wet application gap. Exact square/linear drain position, pitch, threshold, waterproof system and edge terminations await source-verified Revit receipts; no new fabrication jig, installation plan or order.

Manufacturer [R022 exact product evidence](../../../../../research/products/R022_FD_LUXE_SAND_RIVIERA_OAT_24PLUS_LEVEL_AND_SHOWER_PAN.md): current individual vendor item listing, DCOF >=0.42 and Shower Floor YES for this exact SKU. US distribution established by current retail page; Chicago actual SKU shade lot/on-hand/ETA unknown. Source seller defaults to non-Chicago store (not a local quote). Original hard gates, owner veto and four independent critics are mandatory before champion change.

Old Town: one photo-attributed OT01 powder-type room shows white wainscoting/patterned upper wall/dark vanity and contrasted floor, **not** Primary shower tile SKU. OT01–OT04 are one building; OT05 1849 Mohawk PH is a distinct sale but no verified interior bathroom photo ([proof](../../../../../research/comps/R021_OT05_PHOTO_PROVENANCE_AND_OLD_TOWN_COMPARISON.md)). Lincoln Park/Gold Coast secondary. No invented photographed competitor finish or premium.

**Review status:** SOURCE PRELIMINARY; no independent predipatch reviewer, no true four-seat critique, no weighted score, no owner selection. All GC/owner/PO releases FALSE.
"""
        rel=f"rooms/{room}/board/round-022/candidates/{letter}.md"
        pp=ROOT/rel
        pp.parent.mkdir(parents=True,exist_ok=True)
        pp.write_text(txt,encoding="utf-8",newline="\n")
        buf=pp.read_bytes()
        files[rel]={"sha256":hashlib.sha256(buf).hexdigest(),"bytes":len(buf)}
parents={}
for rel in ["state/ROUND018_TUB_TILE_SOURCE_PREPARED_AWAIT_BLIND_PREFLIGHT.json","state/ROUND019_TILE_ONLY_NEXT_COHORT_SOURCE_AWAIT_R018_FORMAL_CLEARANCE.json","state/ROUND020_PRIMARY_TILE_SOURCE_PREPARED_NOT_SUBMITTED.json","state/ROUND021_POWDER_TILE_PRELIMINARY_SOURCE_NOT_SUBMITTED.json","state/ROUND021_ALLOWED_VENDOR_POLICY_AND_EXTRA_CHALLENGERS_PRELIMINARY.json"]:
    buf=(ROOT/rel).read_bytes()
    parents[rel]={"sha256":hashlib.sha256(buf).hexdigest(),"bytes":len(buf)}
data=dict(round=22,phase="NEXT_ELIGIBLE_BLOCKED_SOURCE_PRELIMINARY_NOT_SUBMITTED",rooms=list(DESIGN),owner_large_format_floor_and_pan_directive="2026-11-07 latest OWNER_FEEDBACK lines 53-57",manufacturer_and_US_availability_gate="PRODUCT_PAGE_DOC_PASSES_NARROW_DCOF_SHOWER_USE, CHICAGO_LOT_UNVERIFIED",files=files,immutable_parents=parents,neutral_role_map="NONE: no incumbent champions in these blocked rooms, all options unaccepted",independent_predispatch=None,four_authentic_critics=False,formal_dispatch="NOT_DISPATCHED",score=None,champion_changes=False,owner_approved=False,procurement_release=False,native_1527_equals_1529_owner_confirmed=True,native_element_room_recheck_pending=True)
(ROOT/receipt).write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8",newline="\n")
print("R022 prepared",len(files),"source files, 6 neutral options in 3 blocked rooms; receipt",receipt)
for k,v in files.items():print(k,v["bytes"],v["sha256"])

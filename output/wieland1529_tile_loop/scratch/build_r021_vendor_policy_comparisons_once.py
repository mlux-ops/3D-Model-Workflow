"""Additive four-vendor comparison and 3 genuinely distinct R021 neutral C proposals.

Historical signed R018-R021 files are immutable; this does not submit/score/dispatch.
2026-11-06 research date (2026-11-07 UTC owner steering).
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
ROOMS = {r["id"]: r for r in json.loads((ROOT/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]}

# One exact product/finish/size per entry. Null means a vendor-specific current
# posted price per SF was NOT found; do not copy historic quote rates to it.
# 'gate' refers only to item/product published application, not project release.
P = {
 "earth":("Elm Surfaces","Vera Forma Earth Lines","2x10","Glossy Relief","https://www.elmsurfaces.com/product/earth-lines-vera-forma",None,"Dry WALL only; exact color page linked through collection; floor N/A"),
 "haze":("Elm Surfaces","Haze Camel + Wheat (shared 70/30 field)","1.6x5","Matte","https://www.elmsurfaces.com/product/haze-camel",None,"Dry WALL; individual Camel/Wheat pages separately; one source gross allowance"),
 "indigo":("Elm Surfaces","Vera Forma Indigo Edge","6x6","Glossy Relief","https://www.elmsurfaces.com/product/indigo-edge-vera-forma",None,"Dry WALL; wood floor N/A"),
 "sohoiv":("Elm Surfaces","Soho Ivory","2x10","Glossy","https://www.elmsurfaces.com/product/soho-ivory",None,"Individual Walls + Wet Areas YES; not rated floor"),
 "sohobl":("Elm Surfaces","Soho Black","2x10","Glossy","https://www.elmsurfaces.com/product/soho-black",None,"Individual Walls + Wet Areas YES; not rated floor"),
 "sohoem":("Elm Surfaces","Soho Emerald","2x10","Glossy","https://www.elmsurfaces.com/product/soho-emerald",None,"Individual Walls + Wet Areas YES; not rated floor"),
 "sohoblue":("Elm Surfaces","Soho Blue","2x10","Glossy","https://www.elmsurfaces.com/product/soho-blue",None,"Individual Walls + Wet Areas YES; only DRY powder use here"),
 "nohotaupe":("Elm Surfaces","Noho Taupe","2x10","Matte","https://www.elmsurfaces.com/product/noho-taupe",None,"Individual Walls + Wet Areas YES; powder use DRY WALL"),
 "nohoiv":("Elm Surfaces","Noho Ivory","2x10","Matte","https://www.elmsurfaces.com/product/noho-ivory",None,"Individual Walls + Wet Areas YES; floor DCOF unknown"),
 "bone":("Elm Surfaces","Cortar Bone FLAT","24x48","Soft","https://www.elmsurfaces.com/product/cortar-bone",None,"Individual Wet Areas WALL listed for flat; does NOT certify Reed/Ribbed or ceiling"),
 "clay":("Elm Surfaces","Cortar Clay FLAT","24x48","Soft","https://www.elmsurfaces.com/product/cortar-clay",None,"Individual Wet Areas WALL listed for flat; not Ribbed or ceiling"),
 "charcoal":("Elm Surfaces","Cortar Charcoal FLAT","24x48","Soft","https://www.elmsurfaces.com/product/cortar-charcoal",None,"Individual Wet Areas WALL listed; no implied wet floor DCOF"),
 "sapphire":("Elm Surfaces","Tones Sapphire","2x20","Glossy","https://www.elmsurfaces.com/product/sapphire-tones",None,"Individual Wet Areas WALL listed"),
 "copper":("Elm Surfaces","Tones Copper","2x20","Glossy","https://www.elmsurfaces.com/product/copper-tones",None,"Individual Wet Areas WALL listed"),
 "sandstone":("Elm Surfaces","Tones Sandstone","2x20","Glossy","https://www.elmsurfaces.com/product/sandstone-tones",None,"Individual wet WALL/niche face YES; still needs physical recess approval"),
 "ribbedbone":("Elm Surfaces","Cortar Bone Ribbed relief","24x48","Ribbed","https://www.elmsurfaces.com/product/cortar-bone",None,"FAIL / individual Ribbed Wet Areas listing UNVERIFIED; flat Bone approval not transferable"),
 "caviar":("Elm Surfaces","Clara Caviar original niche","2x8","Zellige","https://www.elmsurfaces.com/product-collection/clara",None,"FAIL / exact Caviar Wet Areas NICHE application unverified"),
 "msiivory":("MSI Surfaces","Brickstone Ivory","2x10","Matte","https://www.msisurfaces.com/porcelain-brickstone/brickstone-ivory-2x10/",None,"Residential Walls YES; DRY wall option, no wet WALL claim here"),
 "msila":("MSI Surfaces","Stella La Perla","2x10","Glossy","https://www.msisurfaces.com/porcelain-stella/la-perla-2x10/",None,"Individual Residential WALL YES; DRY powder only"),
 "msioceano":("MSI Surfaces","Stella Oceano","2x10","Glossy","https://www.msisurfaces.com/porcelain-stella/oceano-2x10/",None,"Individual Residential WALL YES; DRY powder only"),
 "msistowea":("MSI Surfaces","Traktion Stowe Desert Amber mosaic","2x2","Matte","https://www.msisurfaces.com/porcelain-stowe/desert-amber/",None,"SKU NSTODESAMB2X2, individual maker DCOF >0.42 / residential floors YES; specific shower PAN application to verify"),
 "msistowes":("MSI Surfaces","Traktion Stowe Silver Dune mosaic","2x2","Matte","https://www.msisurfaces.com/porcelain-stowe/silver-dune/",None,"SKU NSTOSILDUN2X2, individual maker DCOF >0.42 / residential floors YES; specific shower PAN application to verify"),
 "msiarch":("MSI Surfaces","Architecta Beige","12x24","Matte","https://www.msisurfaces.com/porcelain-architecta/beige/",None,"Individual maker DCOF >0.42 Residential Floor YES, LEVEL only, code NARCB... inspect exact SKU before order"),
 "msistowel":("MSI Surfaces","Traktion Stowe Desert Amber","15x30","Matte","https://www.msisurfaces.com/porcelain-stowe/desert-amber/",None,"SKU NSTODESAMB1530, maker wet DCOF >0.42 Residential Floor YES; LEVEL only"),
 "platfloor":("Platform Surfaces","Chicago Silver rectified","12x24","Matte","https://platformsurfaces.com/wp-content/uploads/2021/10/PS-Chicago-Catalog.pdf",None,"Actual maker catalog listing size/finish; third-party DCOF >=0.42, direct size-specific wet lab evidence pending, no current vendor price"),
 "platpan":("Platform Surfaces","Chicago Silver 2x2 mosaic","2x2 mosaic on 12x12 sheet","Matte","https://platformsurfaces.com/wp-content/uploads/2021/10/PS-Chicago-Catalog.pdf",None,"Catalog 2x2 mosaic; manufacturer shower-floor approval and product wet DCOF unresolved, CONDITIONAL only"),
 "fdpurity":("Floor & Decor","Canvas La Belle Purity","3x12","High Gloss","https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html",5.56,"SKU 100507722; $1.39/0.25 SF per piece; vendor says Shower Walls YES, NEVER floor"),
 "fdblue":("Floor & Decor","Canvas La Belle Antique Blue","3x12","High Gloss","https://www.flooranddecor.com/ceramic-tile/la-belle-antique-blue-high-gloss-ceramic-tile-100507706.html",5.56,"SKU 100507706; $1.39/0.25 SF per piece; Shower Walls YES, not floor"),
 "fdocean":("Floor & Decor","San Giorgio Ocean Azul","2x10","High Gloss","https://www.flooranddecor.com/porcelain-tile/ocean-azul-high-gloss-porcelain-tile-101234664.html",9.94,"SKU 101234664; $1.59/0.16 SF/piece = $9.9375; vendor says Shower Walls YES, never assume floor slip"),
 "fdedessa":("Floor & Decor","Villa Edessa Brick beige","2x8","Matte","https://www.flooranddecor.com/ceramic-tile/edessa-brick-matte-ceramic-tile-101000586.html",13.55,"SKU 101000586; $1.49/0.11 SF/piece = $13.545; Wall YES; too expensive after full box-rounding until separately priced"),
 "fdluxe12":("Floor & Decor","Vetta Elements Luxe Sand","12x24","Matte","https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317733.html",2.99,"SKU 101317733; DCOF >=0.42; Bathroom Floor YES; only LEVEL, not multi-plane pan"),
 "fdluxe24":("Floor & Decor","Vetta Elements Luxe Sand","24x48","Matte","https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317865.html",3.99,"SKU 101317865; DCOF >=0.42, Shower Walls YES; no automatic ceiling certificate"),
 "fdluxemos":("Floor & Decor","Vetta Elements Luxe Sand Square Mosaic","12x12 sheet; 3in chips","Matte","https://www.flooranddecor.com/porcelain-tile/luxe-sand-square-matte-porcelain-mosaic-101318145.html",16.48,"SKU 101318145; $15.99/0.97 SF per sheet; DCOF >=0.42 + Shower Floor YES, 3in chips geometry for four-plane POINT held"),
}
POWDER = {
 "PH-POWDER":["earth","sohoiv","msila","fdpurity"],
 "TX-POWDER":["haze","nohotaupe","msiivory","fdedessa","fdpurity"],
 "TX-POWDER2":["indigo","sohoblue","msioceano","fdblue","fdocean"]
}
WALL = {
 "PH-PRIMARY":["ribbedbone","bone","sohobl","fdluxe24"],
 "TX-PRIMARY":["clay","sohoem","fdluxe24"],
 "PH-BATH2":["sapphire","sohoiv","fdpurity"],
 "TX-BATH2":["copper","sohoiv","fdpurity"],
 "PH-BATH3":["sapphire","nohoiv","fdblue"],
 "TX-BATH3":["sohoem","nohoiv","fdblue"],
 "PH-BATH4":["ribbedbone","bone","sohobl","fdluxe24"],
 "TX-BATH4":["charcoal","sohoiv","fdluxe24"],
}
NICHE = ["sandstone","sohoiv","sohobl","fdpurity"]
LEVEL = ["msiarch","fdluxe12","platfloor","msistowel"]
PAN = ["msistowea","msistowes","fdluxemos","platpan"]
SOURCE_STATUS = {
 "PH-BATH3":"TUB/WALK-IN owner UNSELECTED: POINT PAN only if WALK-IN, Delta Chrome DT062412; basin UNSELECTED",
 "TX-BATH3":"TUB/WALK-IN owner UNSELECTED: POINT PAN only if WALK-IN, Brizo BNX BT062415-BNX",
 "PH-BATH4":"WALK-IN owner SELECTED: four-plane POINT PAN with Brizo BT062415-BNX square drain",
 "PH-PRIMARY":"WALK-IN 48-inch LINEAR with Brizo BT0734816-BNX + separate BR73480; NO niches; PH-WC inherited",
 "TX-PRIMARY":"WALK-IN 48-inch LINEAR with Brizo BT0734816-BNX + separate BR73480; NO niches; TX-WC inherited",
}
INHERITED = {"PH-WC":"PH-PRIMARY","TX-WC":"TX-PRIMARY"}
CHALL_C = {
 "PH-POWDER":("fdpurity","Warm beige gloss strips + Luxe Gold Brizo; a quiet cost-driven alternative to Earth Lines relief and Soho Ivory"),
 "TX-POWDER":("fdpurity","Warm beige gloss 3x12 versus original two-color matte Haze and proposed single-shade Noho Taupe; faucets remain owner-unselected"),
 "TX-POWDER2":("fdblue","Saturated blue 3x12 high-gloss field, a lower-priced rhythm than Indigo Edge relief or Soho Blue narrow strip, preserving deck-mounted black chrome"),
}

for rid in ROOMS:
    assert not (ROOT/"rooms"/rid/"vendor_comparison.md").exists()
for rid in CHALL_C:
    assert not (ROOT/"rooms"/rid/"board"/"round-021"/"candidates"/"C.md").exists()
receipt=ROOT/"state/ROUND021_ALLOWED_VENDOR_POLICY_AND_EXTRA_CHALLENGERS_PRELIMINARY.json"
assert not receipt.exists()

def render_rows(keys, surf, gross, source_rate, source_cost, id):
    assert len(keys)>=3
    out=[f"### {surf}", "", "| Vendor | Exact product | Size / finish | Posted $/SF | Status of application and cost evidence | Source |",
         "|---|---|---|---:|---|---|"]
    for k in keys:
        vendor,name,size,finish,url,price,gate=P[k]
        note=gate
        if price is not None and gross is not None and surf not in ("POINT PAN", "LINEAR PAN") and id not in INHERITED:
            note+=f"; **illustrative old gross x current posted rate** ${gross*price:.2f}/copy, not boxed/installed quote"
        value="NULL — published current vendor $/SF not established" if price is None else f"${price:.2f}/SF"
        out.append(f"| {vendor} | {name} | {size} / {finish} | {value} | {note} | [Vendor item]({url}) |")
    out+=["", f"Historical source gross: {gross if gross is not None else 'NULL'} SF per original room copy, **15% waste already once**, historical rate ${source_rate:.2f}/SF" if source_rate is not None else "Original independent source cost N/A or bundled within parent; no duplicate item."]
    return "\n".join(out)

files={}
for id,r in ROOMS.items():
    rows={v["surface"]:v for v in r["carried_tile_rows"]}
    lines=[f"# {id} — allowed-vendor tile option comparison (2026-11-06, PRELIMINARY)", "",
     "**Owner 2026-11-07 current vendor restriction:** only Elm Surfaces, MSI Surfaces, Platform Surfaces, Floor & Decor. **Emser and Daltile EXCLUDED from future acceptance.** These options are documented real products, not all approved or priced; a comparison candidate with an UNKNOWN hard gate is not eligible to be crowned champion.",
     f"**Current room status:** {r['status']} / currently recorded champion {r['champion_id'] or 'NULL'} / score {r['champion_score'] if r['champion_score'] is not None else 'NULL'}. Owner approval remains separate. **Actual room copies:** {r['unit_count']}.",
     f"**Carried ORIGINAL historical material-only total:** ${(r.get('carried_quote_material_subtotal_usd_per_unit') or 0):.2f}/copy (two copies), not per-room allocated upgrade cap; source project four-unit total $23,572.44; original waste included ONCE.",
     "**Cost comparison:** posted Floor & Decor vendor-online rate is store-dependent (observed changing/default non-Chicago storefronts); **NOT verified Chicago SKU stock/ETA**. Every new Elm, MSI or Platform project rate remains NULL unless a current vendor price can be shown. Gross-rate products are NOT complete installed/boxed quotes; no labor/tax/trim or separate niche/wet pan charge inferred. Vendor item pages and dates seen in the tables, no merchant outreach.",
     ""]
    if id in POWDER:
        x=rows["vanity_wall"]
        lines.append(render_rows(POWDER[id],"DRY vanity WALL",x["qty_sf_per_unit"],x["quoted_rate_usd_per_sf"],x["extended_quote_cost_usd_per_unit"],id))
        lines += ["", "**WOOD FLOOR:** no tile procurement or floor wet-DCOF gate. **Shower PAN/NICHE:** N/A. Never infer a floor tile purchase from product vendor's unrelated floor-use claims.", ""]
    elif id in INHERITED:
        parent=INHERITED[id]
        lines.append(render_rows(LEVEL, f"INHERITED LEVEL floor — {parent} combined historic allowance",None,None,None,id))
        lines+=["",f"**WC source:** no separate quoted tile row or independent purchase. Chosen tile must exactly follow eventual {parent} LEVEL-floor champion. New pan/mosaic N/A. Original WC floor already in parent blended old quantity, not another charge.", ""]
    else:
        wall=rows["wall"]
        lines.append(render_rows(WALL[id], "WET WALL", wall["qty_sf_per_unit"],wall["quoted_rate_usd_per_sf"],wall["extended_quote_cost_usd_per_unit"],id))
        if id not in ("PH-PRIMARY","TX-PRIMARY"):
            niche=rows["accent"]
            opts=(["caviar","sohoiv","sohobl","fdpurity"] if id in ("PH-BATH4","TX-BATH4") else NICHE)
            lines.append(render_rows(opts,"WET NICHE",niche["qty_sf_per_unit"],niche["quoted_rate_usd_per_sf"],niche["extended_quote_cost_usd_per_unit"],id))
        else:
            lines+=["", "**PRIMARY NICHE:** PROHIBITED. Historical excluded reference quantity is never a new purchase or scored candidate.", ""]
        floor=rows["floor"]
        lines.append(render_rows(LEVEL, "BATH LEVEL floor (separate from PAN)",floor["qty_sf_per_unit"],floor["quoted_rate_usd_per_sf"],floor["extended_quote_cost_usd_per_unit"],id))
        if id in SOURCE_STATUS:
            st="LINEAR PAN" if id.endswith("PRIMARY") else "POINT PAN"
            lines.append(render_rows(PAN,st,None,None,None,id))
            lines+=["", "**Owner program and precise drain:** "+SOURCE_STATUS[id], ""]
        else:
            lines+=["", "**SELECTED Duravit TUB program:** no tiled shower PAN; no POINT or LINEAR shower tile; this is a floor and wet tub WALL/NICHE comparison.", ""]
    lines += [
     "## Conditional assessment and market reference",
     "- **Hard gates:** ELM individually Wet Areas listed for specific flat/Soho/Tones wet WALL only; original Bone Ribbed/Caviar exact listing unsupported where noted. F&D La Belle is explicitly Shower Walls YES and floor NO; F&D Luxe Sand 12x24/3in mosaic individually publishes wet DCOF >=0.42, the latter Shower Floor YES. MSI Architecta and Stowe individual pages publish floor DCOF >0.42; match actual exact SKU/size before scoring. Platform Chicago Silver appears in maker catalog and 3P DCOF listing but manufacturer-specific shower-floor performance is NOT yet independently complete; conditional only.",
     "- **Design priorities:** match Black Onyx, Chrome, Matte White, Luxe Gold or Brushed Black Chrome to actual selected plumbing without substitution. Consider 2x10 glossy for focused wall contrast vs matte stone-like support floors; no wet PAN is finished by 12x24 tile on four-plane slopes. Flat level and mosaic pan are independent products.",
     "- **Old Town reference:** OT01 405 W Armitage powder photo truly depicts dark/light contrasting narrow rectilinear floor, patterned upper wall, white wainscoting and dark vanity, not certified exact SKU or a Primary shower. OT01–OT04 same building. OT05 1849 N Mohawk #PH real sold comp, but no authenticated interior bath photo so exact tile, grout and metal unknown ([evidence](../../research/comps/R021_OT05_PHOTO_PROVENANCE_AND_OLD_TOWN_COMPARISON.md)). LP/Gold Coast secondary.",
     "- **Native Revit:** owner confirmed 1527=1529; actual receipt-matched per-wall/sloped-PAN geometry and finish openings still require independent element evidence. Do not convert drawing-derived wall sizes into certified Revit measurements.",
     "- **Governance:** R018/R019/R020/R021 previous neutral sources remain immutable; new 2026-11-07 vendor restriction supersedes allowed eligibility of any Emser or Daltile product in those packets. This table is additive sourcing research, NOT independent Reviewer clearance, critique, scoring, owner decision, acceptance, or order.",
     ""
    ]
    p=ROOT/"rooms"/id/"vendor_comparison.md"
    p.write_text("\n".join(lines),encoding="utf-8",newline="\n")
    raw=p.read_bytes();files[str(p.relative_to(ROOT)).replace("\\","/")]={"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)}

prime={"round":21,"visibility":"PRIME-ONLY, NEVER READ BY CRITICS",
       "mapping":{"PH-POWDER":{"C":"new Floor & Decor La Belle Purity challenger"},
                  "TX-POWDER":{"C":"new Floor & Decor La Belle Purity challenger"},
                  "TX-POWDER2":{"C":"new Floor & Decor La Belle Antique Blue challenger"}},
       "existing_mapping":"state/ROUND021_PRIVATE_PRIME_ONLY_NEUTRAL_MAP_NOT_FOR_CRITICS.json"}
mp=ROOT/"state/ROUND021_EXTRA_C_PRIVATE_PRIME_ONLY_ROLE_MAP.json"
assert not mp.exists()
mp.write_text(json.dumps(prime,indent=2)+"\n",encoding="utf-8",newline="\n")

for rid,(item,thesis) in CHALL_C.items():
    r=ROOMS[rid]
    vendor,name,size,finish,url,price,gate=P[item]
    row=r["carried_tile_rows"][0]
    assert price is not None
    roomgeom=json.loads((ROOT/"rooms"/rid/"geometry.json").read_text(encoding="utf-8"))
    w=roomgeom["tiled_walls"][0]
    src = "research/products/R021_ALLOWED_VENDOR_PRICE_APPLICATION_SOURCE_WITH_FLOOR_DECOR.md"
    p=ROOT/"rooms"/rid/"board/round-021/candidates/C.md"
    content=f"""# {rid} — R021 neutral candidate C — PRELIMINARY unsubmitted

This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.

## Complete neutral scheme, exact item evidence
**DRY feature WALL:** [{vendor} {name} {size} {finish}]({url}), online item with exact manufacturer/vendor SKU and an individual **wall application**. {gate}. Single-colored tile in a CENTERED horizontally stacked 0-offset field on the existing vanity wall with tonal grout direction only for owner selection. No other walls tiled; no niches.

**Floor:** Original natural WOOD unchanged and no tile, no DCOF wet-floor test applies. **Shower WALL/NICHE/LEVEL/PAN:** N/A. This is a POWDER, not a shower bathroom.

**Design alternative:** {thesis}. Real choice requires actual finish sample and selected fixture mood (not fabricated approval).

**Historical Smartsheet provenance:** original `{row['smartsheet_row_id']}`, {row['qty_sf_per_unit']:.2f} SF gross per copy including **15% original waste once**, historical ${row['quoted_rate_usd_per_sf']:.2f}/SF, original ${row['extended_quote_cost_usd_per_unit']:.2f}/copy; two room copies. Proposed vendor web price ${price:.2f}/SF, not a Chicago project quote; **hypothetical same original gross * posted price = ${row['qty_sf_per_unit']*price:.2f}/copy**, excluding complete-box rounding, freight, setting material and owner approval. Official [vendor evidence](../../../../../{src}); exact SKU store/online routing can change. Shop-cartons, actual delivered quote and local Chicago stock/lot remain NULL; do not falsely imply presently orderable quantity.

**Drawing geometry:** historical W1 {w['length']['value']:.3f}ft x {w['tiled_height']['value']:.2f}ft is not a receipt-validated native Revit dimension; no fabricator shop template or cutting instruction implied. Grout/edge/mirror/faucet clearance remains design check, not a failed wet floor gate.

**Selected plumbing unchanged:** {('Brizo FLW T65722LF-GL wall-mount Luxe Gold, separate R65700 rough' if rid=='PH-POWDER' else 'Unresolved owner AXOR One 48140991 vs Hansgrohe Metropol 32526141 WALL faucet; 32526141 is not rough' if rid=='TX-POWDER' else 'Hansgrohe Tecturis E 73072341 DECK-mounted Brushed Black Chrome, basin owner UNSELECTED')}. No new fixture, washbasin, mounting or plumbing finish selected.

**Comp:** [OT01 source-photo notes](../../../../../research/comps/R020_OLD_TOWN_ATRIBUTABLE_BATH_PHOTO_OBSERVATIONS.md) truly show contrasting powder wall/vanity planes, not an exact tile or buyer premium; OT05 exact wet-bath photograph UNVERIFIED. Lincoln Park/Gold Coast secondary.

**Hard-gate and critique prerequisites:** Dry-wall-only item application supported; no shower wet testing required. Availability check limited to live vendor online item, not Chicago store inventory or lot. Historic owner budget-per-room stance remains NULL; the original material-only line is NOT an installed budget. No formal independent preflight, no current round critic dispatch, no same-round four-seat score, no owner acceptance or procurement authorization. All release flags FALSE.
"""
    p.write_text(content,encoding="utf-8",newline="\n")
    raw=p.read_bytes();files[str(p.relative_to(ROOT)).replace("\\","/")]={"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)}

body="""# R021 approved-vendor pricing + hard-gate evidence, individually checked 2026-11-06

Owner's latest 2026-11-07 vendor rule: only **Elm Surfaces, MSI Surfaces, Platform Surfaces, Floor & Decor**. The previous Emser FLOOR/POINT/LINEAR candidates in R018-R020 are now **owner-INELIGIBLE**, no matter their DCOF. Daltile is prohibited. No existing signed source file altered.

**Platform is real, verified**: https://platformsurfaces.com (Chicago line exact maker catalog https://platformsurfaces.com/wp-content/uploads/2021/10/PS-Chicago-Catalog.pdf); Bensenville IL warehouse/showroom address 330 County Line Rd; maker catalog lists Chicago Silver 12x24 8mm matte, and 2x2 mosaics on sheets. Separately https://www.materialbank.com/na/en-US/products/chicago-100558336 lists DCOF >=0.42 for collection, but no per-SKU maker shower-floor wet proof/current vendor $/SF. **Catalog exists, exact project stock, showroom price, wet PAN permission remain NULL**; do not claim present local stock on 'Quick Ship' generic.

**Exact Floor & Decor La Belle Purity 3x12 beige High Gloss**: https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html , SKU **100507722**, individual vendor page **$1.39/piece**, **0.25 SF/piece**, derived **$5.56/SF** (1.39/0.25) before any carton rounding. Maker/vendor lists *wall only*, shower wall YES, never shower floor. Vendor page may default Kirkwood/Timnath/West Des Moines; cannot claim this is Chicago price or warehouse stock.

**Exact Floor & Decor La Belle Antique Blue 3x12 High Gloss**: https://www.flooranddecor.com/ceramic-tile/la-belle-antique-blue-high-gloss-ceramic-tile-100507706.html , SKU **100507706**, **$1.39/0.25 SF = $5.56/SF**, 8.5mm, pressed ceramic wall, shower-wall YES, floor NO. True current Chicago stock/date availability NULL.

**Exact Floor & Decor Edessa Brick Beige 2x8 Matte**: https://www.flooranddecor.com/ceramic-tile/edessa-brick-matte-ceramic-tile-101000586.html SKU **101000586**, **$1.49/0.11 SF = $13.545/SF nominal**, display $13.55/SF (vendor published rounded coverage); direct page says 48 pieces/box, 2x8, floor NOT suitable, wall/shower wall YES. Not a free 15% discount and not a per-SF posted rate. Full-case rounding can easily push the final cost higher. No Chicago availability asserted.

**Exact Floor & Decor Ocean Azul 2x10 High Gloss** https://www.flooranddecor.com/porcelain-tile/ocean-azul-high-gloss-porcelain-tile-101234664.html SKU **101234664**, **$1.59/0.16 SF = $9.94/SF** rounded, wall/shower wall YES, never imply wet PAN. Online or non-Chicago store pickup is NOT Chicago stock.

**Floor & Decor Luxe Sand 12x24 matte ivory porcelain LEVEL** https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317733.html SKU **101317733** $2.99/SF, 8mm, manufacturer vendor page wet DCOF >=0.42, 'Bathroom Floor' YES, independently Shower Floor YES but **12x24 format not suitable on a four-plane POINT PAN; specify LEVEL only**. Separate 12x12 **mosaic** with 3-inch chip (NOT 2x2) https://www.flooranddecor.com/porcelain-tile/luxe-sand-square-matte-porcelain-mosaic-101318145.html SKU **101318145**, ${15.99}/0.97 SF = **$16.48/SF**, 8mm; Shower Floor YES, wet DCOF >=0.42, actual mesh/3-inch chip and drain slope still require a separate cut/layout gate. Vendor-online pricing does not establish Chicago stock.

**MSI approved vendor** exact individual SKU/catalog:
- https://www.msisurfaces.com/porcelain-stella/la-perla-2x10/ **NSTELAPEA2X10G** warm white glossy dry WALL 2x10, no individual vendor $/SF; no floor use;
- https://www.msisurfaces.com/porcelain-brickstone/brickstone-ivory-2x10/ **NCAPIVOBRI2X10** ivory matte dry WALL, no current price;
- https://www.msisurfaces.com/porcelain-stella/oceano-2x10/ **NSTEOCE2X10G** blue glossy dry WALL, no price;
- https://www.msisurfaces.com/porcelain-architecta/beige/ **Architecta Beige 12x24 Matte**, maker item published wet DCOF >0.42 and residential floor YES, LEVEL only;
- https://www.msisurfaces.com/porcelain-stowe/desert-amber/ **NSTODESAMB2X2** matte mosaic, individual product maker DCOF >0.42 and floor use yes; specific sloped residential Shower PAN inclusion is **conditional, not independently proven**;
- https://www.msisurfaces.com/porcelain-stowe/silver-dune/ **NSTOSILDUN2X2** corresponding silver mosaic, also exact floor DCOF >0.42; specific POINT/LINEAR PAN assembly needs review.

ELM Soho Ivory, Black, Emerald 2x10 Glossy and Noho Ivory/Taupe 2x10 Matte individually list **Wet Areas + Walls** (listed variant pages: https://www.elmsurfaces.com/product/soho-ivory, https://www.elmsurfaces.com/product/soho-black, https://www.elmsurfaces.com/product/soho-emerald, https://www.elmsurfaces.com/product/noho-ivory, https://www.elmsurfaces.com/product/noho-taupe). Do not transfer an original FLAT Cortar Wet Areas listing to differently ribbed finish, Caviar niche, generic collection or ceiling. **ELM current project replacement prices all NULL** unless direct vendor posted current price or fresh current READ-ONLY cost row exists.

All quoted old Smartsheet unit rates and material gross are historical and already include original 15% waste. No doubled waste, no vendor outreach, no owner acceptance, no shop/source signature alteration.
"""
evidence=ROOT/"research/products/R021_ALLOWED_VENDOR_PRICE_APPLICATION_SOURCE_WITH_FLOOR_DECOR.md"
assert not evidence.exists()
evidence.write_text(body,encoding="utf-8",newline="\n")
b=evidence.read_bytes();files[str(evidence.relative_to(ROOT)).replace("\\","/")]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}

prior={}
for name in [
 "state/ROUND018_TUB_TILE_SOURCE_PREPARED_AWAIT_BLIND_PREFLIGHT.json",
 "state/ROUND019_TILE_ONLY_NEXT_COHORT_SOURCE_AWAIT_R018_FORMAL_CLEARANCE.json",
 "state/ROUND020_PRIMARY_TILE_SOURCE_PREPARED_NOT_SUBMITTED.json",
 "state/ROUND020_13_PROVISIONAL_OWNER_PREVIEW_MANIFEST.json",
 "state/ROUND021_POWDER_TILE_PRELIMINARY_SOURCE_NOT_SUBMITTED.json",
]:
    b=(ROOT/name).read_bytes()
    prior[name]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
receipt.write_text(json.dumps({
 "owner_vendor_rule_date":"2026-11-07","as_of":"2026-11-06","round":"R021_VENDORS_additive",
 "status":"UNSUBMITTED_PRELIMINARY_COMPARISON_NOT_A_SCORED_ROUND",
 "approved_vendors":["Elm Surfaces","MSI Surfaces","Platform Surfaces","Floor & Decor"],
 "excluded_previous_future_candidates":["Emser","Daltile"],
 "vendor_matched_platform_surfaces":True,
 "rooms_compared":13,"round021_additive_challengers":["PH-POWDER C","TX-POWDER C","TX-POWDER2 C"],
 "prime_only_role_map":str(mp.relative_to(ROOT)).replace("\\","/"),
 "new_file_hashes":files,"immutable_parent_receipts":prior,
 "champion_changes":False,"independent_predispatch_clearance":None,
 "four_original_critic_reports":False,"score":None,
 "owner_approval":False,"procurement_approval":False,
 "manufacturer_gate_evidence_may_be_incomplete":True
},indent=2)+"\n",encoding="utf-8",newline="\n")
print("ADDITIVE VENDOR POLICY: ",len(files),"signed files; 13 room comparisons; 3 new R021 neutral candidates; receipt",receipt.name)
for name,meta in files.items():print(name,meta["bytes"],meta["sha256"])

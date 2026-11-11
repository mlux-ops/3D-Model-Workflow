"""Controlled additive R021 privacy correction; originals unmodified and source UNSUBMITTED."""
from pathlib import Path
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[1]
ROOMS={r["id"]:r for r in json.loads((ROOT/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]}
CONFIG={
"PH-POWDER":{
 "A":("Elm Surfaces","Vera Forma Earth Lines","2x10","Glossy Relief","8.6mm ceramic","https://www.elmsurfaces.com/product/earth-lines-vera-forma",None,"Handcrafted relief introduces directional light and shadow; a tonal grout keeps the small field legible."),
 "B":("Elm Surfaces","Soho Ivory","2x10","Glossy","9.5mm porcelain","https://www.elmsurfaces.com/product/soho-ivory",None,"Smooth ivory gloss creates a quiet continuous background for the gold wall-mounted faucet."),
 "C":("Floor & Decor","La Belle Purity","3x12","High Gloss","ceramic, exact thickness unconfirmed","https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html",5.56,"Wider glossy cream modules reduce horizontal joint density in the compact powder wall.")
 },
"TX-POWDER":{
 "A":("Elm Surfaces","Haze Camel 70% / Wheat 30%","1.6x5","Matte","exact thickness unconfirmed","https://www.elmsurfaces.com/product/haze-camel",None,"Warm mixed-color matte field emphasizes crafted rhythm and depth through controlled 70:30 distribution; maker Wheat item must be independently confirmed."),
 "B":("Elm Surfaces","Noho Taupe","2x10","Matte","9.5mm porcelain","https://www.elmsurfaces.com/product/noho-taupe",None,"Single warm taupe matte field reduces visual noise and supports both possible wall-mounted metallic finish directions."),
 "C":("Floor & Decor","La Belle Purity","3x12","High Gloss","ceramic, exact thickness unconfirmed","https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html",5.56,"Cream gloss introduces deliberate specular highlights and can complement either warm wall-faucet program.")
 },
"TX-POWDER2":{
 "A":("Elm Surfaces","Vera Forma Indigo Edge","6x6","Glossy Relief","8.6mm ceramic","https://www.elmsurfaces.com/product/indigo-edge-vera-forma",None,"Saturated indigo sculpted relief produces a tactile grid against Brushed Black Chrome deck-mounted fittings."),
 "B":("Elm Surfaces","Soho Blue","2x10","Glossy","9.5mm porcelain","https://www.elmsurfaces.com/product/soho-blue",None,"Narrow glossy blue bands create an architectural horizontal feature without relief projection."),
 "C":("Floor & Decor","La Belle Antique Blue","3x12","High Gloss","8.5mm ceramic","https://www.flooranddecor.com/ceramic-tile/la-belle-antique-blue-high-gloss-ceramic-tile-100507706.html",5.56,"Long blue high-gloss modules soften the visual joint count while sustaining a saturated color accent.")
 }}
PLUMB={
 "PH-POWDER":"Brizo Frank Lloyd Wright wall-mounted T65722LF-GL Luxe Gold with separate R65700 rough and RP72414GL drain.",
 "TX-POWDER":"WALL-mounted owner-unselected AXOR One 48140991 Polished Gold Optic or Hansgrohe Metropol 32526141 Brushed Bronze; 32526141 is trim and does not identify the rough.",
 "TX-POWDER2":"Hansgrohe Tecturis E 73072341 Brushed Black Chrome DECK-mounted, basin UNSELECTED."
}
OUT="round-021/predispatch-fix1/candidates"
receipt=ROOT/"state/ROUND021_BLIND_ROLE_NEUTRAL_FIX1_SOURCE_PREPARED_NOT_SUBMITTED.json"
assert not receipt.exists()
allfiles={}; lineages={}
for rid,opts in CONFIG.items():
  r=ROOMS[rid]; assert r["status"]=="active"
  row=r["carried_tile_rows"][0]; gross=row["qty_sf_per_unit"];old=row["extended_quote_cost_usd_per_unit"];rate=row["quoted_rate_usd_per_sf"]
  for letter,(vendor,product,size,finish,thick,url,price,thesis) in opts.items():
    original=ROOT/"rooms"/rid/"board"/"round-021"/"candidates"/(letter+".md")
    orig=original.read_bytes()
    lineages[str(original.relative_to(ROOT)).replace("\\","/")]={"sha256":hashlib.sha256(orig).hexdigest(),"bytes":len(orig)}
    target=ROOT/"rooms"/rid/"board"/OUT/(letter+".md")
    assert not target.exists()
    localcost="Published product price not available; proposed replacement $/SF and shipping unknown." if price is None else f"Floor & Decor current inspected non-Chicago online unit price ${price:.2f}/SF ($1.39 per 0.25 SF piece); indicative original gross x price ${gross*price:.2f}/copy before case rounding, tax and shipping; Chicago physical stock unknown."
    text=f"""# {rid} — R021 neutral tile option {letter} — corrected source copy

This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.

## Tile and physical application
**Dry vanity feature WALL:** [{vendor} {product} {size} {finish}]({url}), {thick}. Manufacturer or vendor wall-use listing applies to this exact named material; maker active U.S. catalog or retailer page indicates distribution, NOT verified Chicago dye lot/warehouse quantity. Grout proposed as tone-on-tone with 1/8-inch *design-starting assumption* subject to actual maker joint requirement and owner sampling. The wall can use centered horizontally stacked rows unless product relief and mirror/escutcheon require another owner-approved aesthetic layout. **Existing WOOD floor remains.** No wet shower WALL, NICHE, LEVEL tile or PAN; no wet-floor DCOF required for this dry-wall feature.

**Architectural thesis:** {thesis}

**Actual selected plumbing constraints:** {PLUMB[rid]} Preserve rough and existing mounting. No newly selected basin, faucet, drain, toilet or finish.

## Source economics and quantity
Historical original read-only Smartsheet `{row["smartsheet_row_id"]}`: {gross:.2f} SF gross per room copy including original 15% waste ONCE, original ${rate:.2f}/SF and ${old:.2f}/copy, two copies. This is a **historical original** material allocation, not the quoted price for this named option. **Proposed source price:** {localcost} No second 15%, no invented owner budget uplift or case count; actual installed cost, replacement vendor quotes, delivery and local lot remain NULL.

**Geometry provenance:** source vanity W1 dimensions reside in assigned geometry.json; they are drawing-derived and not yet certified by a native Revit element/receipt. Confirm actual wall geometry and vanity/mirror/escutcheon location before judging joint layout or geometry hard gate; no installation/shop drawing or order is authorized.

**Old Town comparator evidence:** OT01 405 W Armitage powder-like bathroom photograph shows a dark vanity, white wainscoting, patterned upper wall and contrasting floor, but its exact tile SKU/grout and warm metal alloy are UNKNOWN. OT01–OT04 are ONE building. OT05 1849 N Mohawk is a separate Old Town Triangle sale, with no authenticated bathroom interior photo; its tile/grout/finish are UNKNOWN. Sources: research/comps/R020_OLD_TOWN_ATRIBUTABLE_BATH_PHOTO_OBSERVATIONS.md and research/comps/R021_OT05_PHOTO_PROVENANCE_AND_OLD_TOWN_COMPARISON.md. Lincoln Park/Gold Coast secondary.

**Unresolved source gates:** exact current Chicago shade-lot stock, cartons, additional manufacturer documentation where specified, material total and native room measurements. Independent four-seat critique and owner approval not obtained. No product role/status, historical score or other candidate comparison is provided here.
"""
    assert not re.search(r"(?i)\b(champion|challenger|incumbent|existing scheme|previous round|score 3\.[0-9])\b",text)
    target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding="utf-8",newline="\n")
    b=target.read_bytes()
    allfiles[str(target.relative_to(ROOT)).replace("\\","/")]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
  assert len(opts)==3

receipt.write_text(json.dumps({"round":21,"classification":"CONTROLLED_ADDITIVE_ROLE_NEUTRAL_FIX1_PREPARED_NOT_DISPATCHED",
"revision_path":"rooms/<ROOM>/board/round-021/predispatch-fix1/candidates/",
"private_role_mapping":"PRESERVED separately; never a critic source",
"source_file_hashes":allfiles,"immutable_original_candidate_hashes":lineages,
"original_reviewer_clearance":None,"original_four_critiques":False,"source_frozen_formally":False,
"champions_changed":False,"owner_approved":False,"release":False,"powder_rooms":list(CONFIG),
"approved_vendors":["Elm Surfaces","MSI Surfaces","Porcelanosa","Floor & Decor"]},indent=2)+"\n",encoding="utf-8",newline="\n")
print("R021 BLIND FIX1",len(allfiles),"role-neutral options, originals",len(lineages),"untouched, new receipt",receipt.name)

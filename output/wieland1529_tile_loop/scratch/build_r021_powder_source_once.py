"""One-time PRELIMINARY R021 powder candidates: incumbent neutral copies plus challengers.

No critic dispatch, no scoring, no signed predecessor mutation, no state champion changes.
"""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]
rooms = {r['id']:r for r in json.loads((ROOT/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
config = {
 'PH-POWDER':{
  'inc':'ELM Vera Forma Earth Lines 2x10 Glossy Relief, DRY vanity WALL, existing wood floor; 2x10 ceramic relief 8.6 mm, walls only; manufacturer collection quick-ship general 2-4 weeks, exact Chicago inventory unverified',
  'incurl':'https://www.elmsurfaces.com/product/earth-lines-vera-forma',
  'incsrc':'research/products/elm-vera-forma-earth-lines-2x10.md',
  'chall':'ELM Soho Ivory 2x10 Glossy, 9.5 mm, DRY vanity WALL with flatter faucet landing, owner-unapproved substitution; wood floor unchanged',
  'challurl':'https://www.elmsurfaces.com/product/soho-ivory',
  'challsrc':'research/products/R021_SOHO_IVORY_2X10_GLOSSY_DRY_POWDER_WALL_PRODUCT.md',
  'plumb':'Owner-selected Brizo Frank Lloyd Wright wall faucet T65722LF-GL Luxe Gold with rough R65700 and RP72414GL drain. AXOR deck proposal NOT selected.',
  'owner':'Preserve selected wall faucet; owner may consider flatter Ivory vs Earth Lines relief, only after actual tile/Brizo mounting plane and selected grout/trim.',
  'rationale':'Existing Earth Lines provides sculptural relief; challenger is calmer Ivory glossy 2x10 designed to reduce competing surface texture against the architectural Brizo Luxe Gold wall faucet.',
  'original':'Earth Lines',
  'extras':'No wet WALL/NICHE, LEVEL, POINT/LINEAR PAN applies: scheduled *dry* powder feature wall and wood floor.',
 },
 'TX-POWDER':{
  'inc':'ELM Haze Camel + Wheat 1.6x5 Matte DRY vanity wall, current 70% Camel / 30% Wheat controlled mixed vertical/stacked arrangement, wood floor',
  'incurl':'https://www.elmsurfaces.com/product/haze-camel',
  'incsrc':'research/products/elm-haze-camel-1p6x5.md',
  'chall':'ELM Noho Taupe 2x10 Matte, 9.5 mm, single shade DRY vanity WALL 0-offset horizontal stack, owner-unapproved substitution, wood floor',
  'challurl':'https://www.elmsurfaces.com/product/noho-taupe',
  'challsrc':'research/products/R021_NOHO_TAUPE_2X10_MATTE_DRY_TX_POWDER_WALL_PRODUCT.md',
  'plumb':'WALL-mounted faucet program remains owner-UNSELECTED between AXOR One 48140991 Polished Gold Optic and Hansgrohe Metropol 32526141 Brushed Bronze; 32526141 is TRIM, not a rough.',
  'owner':'Resolve wall-mounted faucet and compatible rough; then choose whether 70/30 Haze visual richness or single-shade matte Taupe best suits actual finish and mirror.',
  'rationale':'Existing controlled 70/30 Haze reads nuanced warm handcrafted; challenger simplifies joints and dye-lot mixing to a restrained single-toned Taupe, potentially safer with disputed gold/bronze fixture, not an owner-approved choice.',
  'original':'70% Haze Camel + 30% Haze Wheat',
  'extras':'The 70%/30% division applies to the one gross wall quantity, not separate quantities per color; any blend is dry and floor remains wood.',
 },
 'TX-POWDER2':{
  'inc':'ELM Vera Forma Indigo Edge 6x6 Glossy Relief DRY vanity WALL, wood floor; source collection 8.6 mm ceramic, walls only',
  'incurl':'https://www.elmsurfaces.com/product/indigo-edge-vera-forma',
  'incsrc':'research/products/elm-vera-forma-indigo-edge-6x6.md',
  'chall':'ELM Soho Blue 2x10 Glossy, 9.5 mm, single blue DRY vanity WALL, centered 0-offset stack instead of raised 6x6 relief, wood floor',
  'challurl':'https://www.elmsurfaces.com/product/soho-blue',
  'challsrc':'research/products/R021_SOHO_BLUE_2X10_GLOSSY_DRY_TX_POWDER2_WALL_PRODUCT.md',
  'plumb':'Owner-selected Hansgrohe Tecturis E 73072341 Brushed Black Chrome faucet stays DECK-mounted; basin is UNSELECTED. Do not shift rough or wall-mount.',
  'owner':'Owner select basin, then compare glossy Indigo relief vs Soho Blue 2x10 flatter blue field; retain deck-mounted spout, select backsplash/edge within actual vanity.',
  'rationale':'Existing Indigo Edge creates blue depth and a tactile grid; challenger keeps blue direction but creates flatter horizontal ribbons and likely reduces shadows around mirror, with no claim of actual buyer premium.',
  'original':'Vera Forma Indigo Edge',
  'extras':'No shower/pan/LEVEL tile and no wet DCOF gate; original vanity tile on dry wall only, wood flooring unchanged.',
 },
}

dest = ROOT/'state/ROUND021_POWDER_TILE_PRELIMINARY_SOURCE_NOT_SUBMITTED.json'
assert not dest.exists()
for room in config:
    assert not (ROOT/'rooms'/room/'board'/'round-021').exists()
mapping = {}
files = {}
for room,cfg in config.items():
    r=rooms[room]
    assert r['status']=='active' and r['champion_id'] and r['champion_score'] is not None
    assert len(r['carried_tile_rows'])==1
    carried=r['carried_tile_rows'][0]
    gross=carried['qty_sf_per_unit']
    oldrate=carried['quoted_rate_usd_per_sf']
    oldcost=carried['extended_quote_cost_usd_per_unit']
    assert abs(oldcost-round(gross*oldrate,2))<0.02
    geom=json.loads((ROOT/'rooms'/room/'geometry.json').read_text(encoding='utf-8'))
    w=geom['tiled_walls'][0]
    assert geom['floor_finish']=='wood, no tile'
    assert not geom['shower_or_tub_footprint']
    # Prime-only role map, kept out of any critic allowed candidate folder.
    mapping[room]={'A':'existing active incumbent neutral copy','B':'new unsanctioned challenger'}
    for letter in ('A','B'):
        is_existing=letter=='A'
        scheme=cfg['inc'] if is_existing else cfg['chall']
        maker=cfg['incurl'] if is_existing else cfg['challurl']
        source=cfg['incsrc'] if is_existing else cfg['challsrc']
        # No role labels/status/history or past scores in candidate.
        text=f"""# {room} — neutral candidate {letter} — R021 PRELIMINARY

This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.

## Physical scheme

**Dry feature WALL:** {scheme}. **Other walls:** painted/untiled existing scope, no new tile. **FLOOR:** existing WOOD, not a tile floor. **Shower WALL/NICHE/PAN:** N/A. {cfg['extras']}

**Individual tile identity:** [{scheme.split(',')[0]}]({maker}); [maker research](../../../../../{source}). Manufacturer individual/collection evidence is restricted to exact dry WALL item, finish and nominal size, not arbitrary alternates. Exact factory order code/available cartons/Chicago lot and true shipping lead are UNKNOWN.

**Existing selected fixture/program unchanged:** {cfg['plumb']}

**Architectural hypothesis:** {cfg['rationale']}

## Historical gross/budget comparison

Original read-only Smartsheet source row **`{carried['smartsheet_row_id']}`**: **{gross:.2f} SF gross PER COPY**, original **15% waste included ONCE**, historical material-only line **${oldcost:.2f} per copy** at **${oldrate:.2f}/SF**; **2 physical copies**. Historical original quote is NOT the proposed replacement's quoted rate. Exact replacement unit price/quantity per carton, current Chicago stock, freight, tax and owner per-room budget = NULL. Only the historic material line is included in total project material budget; no new or duplicate source row.

Dry wall DCOF wet-floor and shower wet WALL/NICHE gates N/A, not a floor approval. BOARD active status and existing four-seat scoring are not presented in this blind packet. A challenger can only prevail after authentic four-seat review, wet/availability/geometry and price hard gates and **at least +0.25 weighted advantage over incumbent in same round, with all seats >=3.0**.

## Architectural geometry, grout and cost authenticity

Source vanity W1 **{w['length']['value']:.3f} ft x {w['tiled_height']['value']:.2f} ft**, drawing-derived/assumed, NOT a native measured wall with associated element/receipt. Confirm centered visual margins, wall-mounted escutcheon landing where applicable, mirror/light conflicts, joint width, edge and actual wall finish before authorizing installation; no fabrication jig or shop redesign.

**Old Town photo:** OT01 405 W Armitage powder-like bathroom visually shows patterned upper wallcovering, pale wainscoting, dark vanity, warm-looking metal, contrasting rectangular dark/white floor; exact tile SKU/size/grout/metal alloy unverified. [R020 photographic notes](../../../../../research/comps/R020_OLD_TOWN_ATRIBUTABLE_BATH_PHOTO_OBSERVATIONS.md). OT05 1849 N Mohawk PH is separate **sold comp**, but no independently authenticated bathroom tile photographs, so visible finish comparison there = NULL [OT05 evidence](../../../../../research/comps/R021_OT05_PHOTO_PROVENANCE_AND_OLD_TOWN_COMPARISON.md). OT01–04 same building; LP/GC secondary.

**Owner-only:** {cfg['owner']} Preserve existing wood FLOOR, specified wall/deck mounting and any unselected basin/program. No supplier contact, sample, procurement, approved color change or owner/GC release.
"""
        rel=f'rooms/{room}/board/round-021/candidates/{letter}.md'
        p=ROOT/rel
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(text,encoding='utf-8',newline='\n')
        b=p.read_bytes()
        files[rel]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}

private=ROOT/'state/ROUND021_PRIVATE_PRIME_ONLY_NEUTRAL_MAP_NOT_FOR_CRITICS.json'
assert not private.exists()
private.write_text(json.dumps({'visibility':'PRIME_ONLY_NEVER_SEND_TO_CRITICS',
                              'round':21,'map':mapping,
                              'no_score_or_approval':True},indent=2)+'\n',encoding='utf-8',newline='\n')
parents={}
for rel in ['state/ROUND018_TUB_TILE_SOURCE_PREPARED_AWAIT_BLIND_PREFLIGHT.json',
            'state/ROUND019_TILE_ONLY_NEXT_COHORT_SOURCE_AWAIT_R018_FORMAL_CLEARANCE.json',
            'state/ROUND020_PRIMARY_TILE_SOURCE_PREPARED_NOT_SUBMITTED.json',
            'state/ROUND020_13_PROVISIONAL_OWNER_PREVIEW_MANIFEST.json']:
    b=(ROOT/rel).read_bytes()
    parents[rel]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
additives=[
 'research/comps/R021_OT05_PHOTO_PROVENANCE_AND_OLD_TOWN_COMPARISON.md',
 'research/products/R021_SOHO_IVORY_2X10_GLOSSY_DRY_POWDER_WALL_PRODUCT.md',
 'research/products/R021_NOHO_TAUPE_2X10_MATTE_DRY_TX_POWDER_WALL_PRODUCT.md',
 'research/products/R021_SOHO_BLUE_2X10_GLOSSY_DRY_TX_POWDER2_WALL_PRODUCT.md',
 'research/products/R021_TECHNIQUE_IVORY_F16TECHIV1224_CURRENT_US_PUBLIC_RETAIL_PRICE_COMPARISON.md',
]
for rel in additives:
    b=(ROOT/rel).read_bytes()
    files[rel]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
data={
 'round':21,'phase':'PRELIMINARY_SOURCE_NOT_SUBMITTED','focus_rooms':list(config),
 'original_status':'THREE_ACTIVE_ROOMS_WITH_UNCHANGED_ACCEPTED_CHAMPIONS',
 'neutral_incumbent_challenger_map_location':'state/ROUND021_PRIVATE_PRIME_ONLY_NEUTRAL_MAP_NOT_FOR_CRITICS.json',
 'scope':'three dry-wall powder rooms, original wood floor unchanged, 2 candidates per room',
 'prior_signed_source_unchanged':True,'original_reviewer_available':False,
 'original_design_worker_available':False,'independent_predispatch_clearance':None,
 'four_authentic_independent_critiques':False,'critic_dispatch':'NOT_DISPATCHED',
 'weighted_scoring':None,'champion_changes':None,'owner_approval':False,
 'procurement_release':False,'submission_frozen':False,
 'native_revit_project_1527_equals_1529_owner_confirmed':True,
 'historical_13_rooms':13,'historical_26_copies':26,
 'historical_27_material_rows':27,'historical_material_usd_four_units':23572.44,
 'original_fifteen_percent_waste_included_once':True,
 'parent_receipts':parents,'source_files':files
}
dest.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
print('R021 PRELIMINARY',len(files),'source/evidence files',len(config),'rooms',len(config)*2,'candidates, prime-only private mapping, no board writes')
for name,meta in files.items():print(name,meta['bytes'],meta['sha256'])

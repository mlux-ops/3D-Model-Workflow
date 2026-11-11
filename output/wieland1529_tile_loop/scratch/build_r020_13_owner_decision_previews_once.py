"""Additive R020 13 one-page decision previews, NOT owner-review or champion approval."""
from pathlib import Path
import json
import hashlib

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "deliverables/r020-owner-tile-decision-previews-NOT-APPROVED"
assert not DEST.exists(), "Refuse to regenerate owner previews"
ROOMS = {r["id"]:r for r in json.loads((ROOT/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]}
SPECS = {
 "PH-PRIMARY":("R020 preliminary A / alternative C","Flat Cortar Bone Soft wet WALL (no Reed); 12x24 Technique Ivory LEVEL including inherited WC; Technique Ivory 2x2 LINEAR PAN; no niche. Alternative: bounded Soho Black wet WALL feature, Capisco Trosa LEVEL, Source Pure White 2x2 PAN with solid BNX grate.","Primary shower fixed Brizo Black Onyx BT0734816-BNX 48-inch LINEAR plus separate BR73480 rough, no Primary niches.","Approve flat Bone vs bounded wet-listed black feature; confirm exact WC/LEVEL vs PAN quantities, substrate/grate system, grout, total replacement price."),
 "PH-BATH2":("R018 preliminary A / B","Individually wet-listed Tones Sapphire 2x20 Glossy tub surround and existing Sandstone niche; Capisco Boden 12x24 Matte LEVEL, alternative Trosa. No shower tile PAN.","Selected Duravit tub + Hansgrohe Matte White.","Confirm tile palette, basin/cut/alcove fit if affected, grout/trim, actual floor source and replacement price."),
 "PH-BATH3":("R019 preliminary A / C","Sapphire 2x20 horizontal wet WALL, Sandstone wet niche, Capisco Boden LEVEL; conditional WALK-IN Technique Ivory 2x2 POINT PAN. Alternative Noho Ivory vertical wet WALL/Trosa LEVEL/Source Pure White POINT PAN.","Hansgrohe Chrome shower, Delta DT062412 Chrome POINT only if WALK-IN; basin UNSELECTED.","Choose TUB or WALK-IN; select basin; sample wet wall color and approve wet-PAN only after program determination."),
 "PH-BATH4":("R019 preliminary B / C","Cortar Bone FLAT 24x48 wet WALL (no Ribbed); Soho Black niche / Trosa LEVEL / Technique Ivory 2x2 POINT PAN; alternative Soho Ivory niche / Boden LEVEL / Source Pure White POINT PAN.","WALK-IN selected; Brizo Black Onyx BT062415-BNX 4-inch square POINT fixed.","Choose black vs ivory niche, settle 35-vs-27 SF source floor discrepancy, final four-plane PAN and black-on-ivory sample."),
 "PH-POWDER":("Existing active v4-PH-POWDER, score 3.69","Original Vera Forma Earth Lines 2x10 Glossy Relief **dry vanity feature WALL**; original wood FLOOR (no tile-level/PAN gate).","Brizo Frank Lloyd Wright T65722LF-GL Luxe Gold wall faucet, required R65700 rough.","Confirm real dry-wall feature placement, grout, ordered material code and wall-faucet alignment; active is not owner-approved."),
 "PH-WC":("Existing seeded v4-PH-WC, unscored","Inherited PH-PRIMARY LEVEL tile only (new R020 candidate would be 12x24 Technique Ivory, or Trosa alternative); NO independent WC tile order or shower PAN.","Existing WC fixture/door scope independent; bathroom Primary tile allocation governs finish.","Finalize Primary champion first, then carry identical WC floor/grout; verify true WC boundary and 15 SF historical allocation."),
 "TX-PRIMARY":("R020 preliminary B / C","Flat Cortar Clay Soft 24x48 wet WALL (no Ribbed), Technique Ivory 12x24 LEVEL including inherited TX WC, Technique Ivory 2x2 LINEAR PAN; alternative bounded wet-listed Soho Emerald wet WALL feature, Boden LEVEL, Source Pure White 2x2 PAN with solid BNX grate.","Brizo Roccesco Black Onyx BT0734816-BNX LINEAR 48-inch with separate BR73480 rough; NO Primary niches.","Choose full-flat warm field vs bounded Emerald focal panel; confirm actual LINEAR-pan/LEVEL/WC split, grate finish/sample and replacement cost."),
 "TX-BATH2":("R018 preliminary A / B","Maker-listed Tones Copper 2x20 wet tub WALL, Sandstone wet NICHE, Capisco Trosa LEVEL; alternative Boden LEVEL. No tiled PAN.","Selected Duravit tub, Hansgrohe Chrome; basin UNSELECTED.","Select basin, confirm tile/grout/Chrome pairing and actual tub-to-wall fit; price alternate floor and retain no PAN."),
 "TX-BATH3":("R019 preliminary A / B","Wet-listed Soho Emerald 2x10 vertical WALL/Sandstone NICHE/Capisco Trosa LEVEL, conditional Technique Ivory 2x2 POINT PAN; alternative Noho Ivory WALL/Soho Black NICHE/Boden LEVEL/Source White POINT PAN.","Brizo Roccesco Black Onyx, BT062415-BNX 4-inch square POINT only if WALK-IN.","Choose TUB or WALK-IN; decide green saturated vs warm neutral / black niche; approve actual PAN scope only if WALK-IN."),
 "TX-BATH4":("R018 preliminary B / A","Individually wet-listed FLAT Cortar Charcoal 24x48 Soft wet tub WALL and Soho Ivory 2x10 wet NICHE; Capisco Trosa LEVEL or alternative Boden. Original Clara Caviar wet NICHE listing remains unsupported.","Duravit tub with Hansgrohe Matte White; no tiled PAN.","Approve Ivory niche replacement, resolve thermostat/diverter/tub control compatibility (independent plumbing hold), size and floor price."),
 "TX-POWDER":("Existing active round-003-B, score 3.67","Original Haze Camel and Wheat matte 1.6x5 stacked **dry vanity WALL**; original wood FLOOR, no tiled PAN.","Competing owner source for wall faucet: AXOR One 48140991 Polished Gold Optic versus Hansgrohe Metropol 32526141 Brushed Bronze; neither rough inferred.","Owner must select the actual wall-mounted faucet/compatible rough before tonal tile/metal sign-off; active tile is not owner-approved."),
 "TX-POWDER2":("Existing active v4-TX-POWDER2, score 3.23","Original Vera Forma Indigo Edge 6x6 Glossy Relief **dry vanity WALL**; original wood FLOOR.","Hansgrohe Tecturis E 73072341 Brushed Black Chrome DECK-mounted faucet; basin UNSELECTED.","Select basin without converting faucet to wall mount; confirm grout, vanity/edge proportions, dry feature wall extent."),
 "TX-WC":("Existing seeded v4-TX-WC, unscored","Inherited TX-PRIMARY LEVEL floor only (R020 proposed Technique Ivory or Boden alternative); no independent material order and no shower PAN.","Existing WC plumbing, current TX203A source location not yet native element verified.","Finalize TX-PRIMARY champion before choosing identical WC LEVEL tile, and verify room placement/allocation; retain no new order."),
}
assert set(SPECS)==set(ROOMS) and len(SPECS)==13
files={}
for rid,(status,scheme,plumbing,owner) in SPECS.items():
 r=ROOMS[rid]
 per=r.get("carried_quote_material_subtotal_usd_per_unit") or 0
 amount="INCLUDED in Primary source (no independent WC allocation)" if rid.endswith("-WC") else f"${per:,.2f} material-only per room copy x {r['unit_count']} copies = ${per*r['unit_count']:,.2f} original quoted source"
 stage="ACTIVE but NOT owner-approved" if r["status"]=="active" else ("SEEDED/UNSCORED, no evaluated champion" if r["status"]=="seeded" else "BLOCKED, NO champion; candidate is a DESIGN OPTION only")
 content=f"""# {rid} — OWNER TILE DECISION PREVIEW (ONE ROOM, NOT APPROVED)

**Formal status:** {stage}. **Choice reference:** {status}. **Copies:** {r['unit_count']} identical physical instances. NOT a binding specification, GC release, purchase request or accepted board champion.

**Surface selections / proposed tile scheme:** {scheme}

**Architectural reasoning:** Deliberately constrain the accent to a wet-listed wall or dry powder feature where supported; keep a quiet LEVEL plane beneath actual fixtures and, in walk-in bathrooms only, use a distinct small-format manufacturer-shower-floor-rated PAN. This is a source-backed design interpretation, not an owner-selected final sample.

**Actual plumbing and finish constraint:** {plumbing}

**Old Town comparison:** OT01–OT04 at 405 W Armitage are ONE building; listing copy establishes primary-bath/tub/shower amenities but no known Primary tile SKU. An independently inspected OT01 bathroom photograph shows patterned upper wallcovering, white paneled lower walls, dark wood vanity, veined pale counter, alternating contrasting rectangular floor and warm-looking metals; it is a *powder-type room*, not evidence for a competitor wet shower. OT05 1849 N Mohawk is a separate Old Town Triangle sale without authenticated bath tile photography. See [photo notes](../../research/comps/R020_OLD_TOWN_ATRIBUTABLE_BATH_PHOTO_OBSERVATIONS.md) and [comp index](../../research/comps/COMPS.md). Lincoln Park and Gold Coast precedents remain explicitly secondary.

**Historical material versus current budget:** {amount}. Historical original gross quantities already include **15% waste ONCE**. This is an original quote comparison, NOT new Emser/ELM substitution pricing, true installed cost or signed per-room allowance. **Replacement-price delta = UNKNOWN**; owner's tile budget upgrade stance remains unselected.

**Owner-only decisions:** {owner}

**Evidence and release controls:** The current manufacturer item pages give individually scoped wet WALL/NICHE permissions or product-specific published wet DCOF for LEVEL/PAN where listed in the relevant R018/R019/R020 candidate packets. Any actual native Revit room length, openings, drain placement and fixture elevations require element IDs plus read-only receipt; 1527/1529 is confirmed one building. Exact Chicago dye-lot inventory, cartons, current landed material unit pricing, selected grout/edge and full installed GC approval remain outstanding. **Owner-approved = FALSE; four-critic compliant champion = FALSE unless existing formal state says otherwise (active and seeded remain unapproved); material ordered = FALSE.**
"""
 p=DEST/(rid+".md")
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(content,encoding="utf-8",newline="\n")
 raw=p.read_bytes()
 files[str(p.relative_to(ROOT)).replace("\\","/")]={"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)}
manifest=ROOT/"state/ROUND020_13_PROVISIONAL_OWNER_PREVIEW_MANIFEST.json"
assert not manifest.exists()
manifest.write_text(json.dumps({"round":20,"classification":"13_ROOM_ONE_PAGE_CONTENT_PREVIEWS_NOT_RELEASED","files":files,
 "room_count":13,"copies_total":26,"historical_quoted_total_four_units_usd":23572.44,
 "fifteen_percent_original_waste_included_once":True,"existing_champions_changed":False,
 "original_R018_R019_frozen_source_unchanged":True,"not_final_owner_review":True,
 "global_done":False,"owner_approved":False,"procurement_authorized":False},indent=2)+"\n",encoding="utf-8",newline="\n")
print("PREPARED",len(files),"owner decision previews, SHA manifest",manifest.name)
for k,v in files.items():print(k,v["bytes"],v["sha256"])

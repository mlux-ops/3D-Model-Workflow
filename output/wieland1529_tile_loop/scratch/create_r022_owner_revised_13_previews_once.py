"""Additive one-page-content owner previews, owner rules 2026-11-07, never approved."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
rooms={r["id"]:r for r in json.loads((ROOT/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]}
out=ROOT/"deliverables/r022-owner-13-updated-large-format-and-powder-NOT-APPROVED"
receipt=ROOT/"state/ROUND022_13_OWNER_UPDATED_NOT_APPROVED_SHA_MANIFEST.json"
assert not out.exists() and not receipt.exists()
spec={
 "PH-PRIMARY":("R022 A proposed: ELM FLAT Cortar Bone Soft 24x48 wet WALL; F&D Luxe Sand 24x24 matte SKU 101317949 same LEVEL and installer-cut LINEAR PAN, 8mm, shower-floor listing & wet DCOF >=0.42; no NICHE; inherited PH-WC LEVEL.","Alternative B: limited Soho Black wet WALL feature, Riviera Oat 24x48 same LEVEL/LINEAR PAN; BNX solid grate. Keep Brizo Black Onyx 48in BT0734816-BNX, separate BR73480 rough.","Select restrained ivory vs travertine/black focal palette; approve grout, true LEVEL/PAN/WC split, LFT cut scheme and exact alternate-wall material quote."),
 "PH-BATH2":("R018 original ELM Sapphire 2x20 Glossy wet WALL, Sandstone separately wet-listed NICHE; proposed F&D Luxe Sand 24x24 matte LEVEL (instead of now-disallowed Emser), no tiled PAN.","Owner-selected Duravit tub, Hansgrohe Matte White. Alternate eligible Riviera Oat 24x48 LEVEL if cuts/price suit.","Approve floor shade and grout; verify tub clearances against native model; no shower PAN or basin invented."),
 "PH-BATH3":("ELM Sapphire or Noho Ivory individually wet-listed WALL; Sandstone wet NICHE. Conditional approved-vendor F&D Luxe Sand 24x24 same LEVEL and (only if WALK-IN) square POINT PAN; Riviera Oat 24x48 variant pending cut check.","Hansgrohe Chrome; Delta DT062412 Chrome square POINT only if WALK-IN; basin UNSELECTED.","Owner TUB versus WALK-IN UNSELECTED and basin UNSELECTED. Choose program first; no pan with tub and no invented tub drain."),
 "PH-BATH4":("R022 A ELM FLAT Cortar Bone 24x48 wet WALL (not Ribbed) + Soho Black wet NICHE + F&D Luxe Sand 24x24 same LEVEL/installer-cut four-plane POINT PAN; R022 B Soho Ivory NICHE + Riviera Oat 24x48.","WALK-IN fixed; Brizo Black Onyx BT062415-BNX four-inch square POINT unchanged.","Select black/ivory niche and floor appearance; reconcile historical 35-vs-27 SF floor discrepancy and cut plan."),
 "PH-POWDER":("Three neutral R021 dry WALL options: original Elm Earth Lines 2x10 Glossy Relief; Elm Soho Ivory 2x10 Glossy; F&D La Belle Purity 3x12 Glossy SKU 100507722. WOOD floor; shower PAN N/A.","Existing active score 3.69 retains Earth Lines pending review. Brizo FLW T65722LF-GL Luxe Gold WALL-mounted with separate R65700 rough.","Owner compare sculptural relief with calm Ivory and less expensive Purity; no new faucet or material approved."),
 "PH-WC":("WC has NO independent tile order: selected future PH-PRIMARY LEVEL product inherited, proposed F&D Luxe Sand 24x24 or Riviera Oat 24x48; no niche, no shower PAN.","Original WC plumbing independent; PH-PRIMARY parent material covers WC floor once. Current SEEDED unscored v4-PH-WC.","Choose parent Primary champion first; confirm actual native WC placement and boundary, do not duplicate source gross."),
 "TX-PRIMARY":("R022 A ELM flat Cortar Clay Soft 24x48 wet WALL and F&D Riviera Oat 24x48 same LEVEL/LINEAR PAN; R022 B bounded Soho Emerald wet feature WALL, F&D Luxe Sand 24x24 same LEVEL/PAN. NO niches; TX-WC inherited.","Owner Brizo Black Onyx BT0734816-BNX 48in LINEAR and separate BR73480 rough, solid BNX grate.","Select warm flat/no feature versus emerald focal; verify native drain pan/WC split and current complete quote."),
 "TX-BATH2":("ELM Tones Copper 2x20 Glossy wet WALL, separately wet-listed Sandstone NICHE; owner-compliant 24x24 Luxe Sand or 24x48 Riviera Oat LEVEL, no tiled PAN.","Duravit tub and Hansgrohe Chrome selected. Basin remains UNSELECTED.","Select basin and floor tone; confirm tub wall layout, actual LEVEL square footage and grout."),
 "TX-BATH3":("ELM Soho Emerald or Noho Ivory wet WALL, Sandstone or Soho Black wet NICHE; conditional F&D Luxe Sand 24x24 LEVEL and POINT PAN only if owner chooses WALK-IN; Riviera Oat alternative.","Owner TUB versus WALK-IN UNSELECTED, Brizo Black Onyx BT062415-BNX square POINT conditional WALK-IN only.","Choose tub/walk-in, green/neutral palette and actual pan scope; no borrowing PH3 basin status."),
 "TX-BATH4":("ELM FLAT Cortar Charcoal wet tub WALL and separately wet-listed Soho Ivory NICHE (replaces unlisted Caviar), F&D Luxe Sand 24x24 or Riviera Oat 24x48 LEVEL, NO tiled PAN.","Owner Duravit tub, Hansgrohe Matte White fixture finish unchanged.","Approve niche substitution, floor color and resolve separately noted thermostatic diverter/tub-spout compatibility."),
 "TX-POWDER":("Three R021 neutral DRY WALL designs: existing 70% Haze Camel +30% Wheat 1.6x5 Matte, Elm Noho Taupe 2x10 Matte, F&D La Belle Purity 3x12 Glossy. WOOD floor.","Active 3.67 remains; WALL faucet program unresolved AXOR One 48140991 Polished Gold Optic vs Hansgrohe Metropol 32526141 Brushed Bronze. Neither is rough.","Owner choose wall faucet program and compatible rough first, then warm matte vs high-gloss wall tile."),
 "TX-POWDER2":("Three R021 neutral DRY WALL designs: original Indigo Edge 6x6 Glossy Relief, Elm Soho Blue 2x10 Glossy, F&D La Belle Antique Blue 3x12 Glossy; WOOD floor.","Active score 3.23 remains; Hansgrohe Tecturis E 73072341 Brushed Black Chrome DECK-mounted, basin UNSELECTED.","Owner select basin; compare two new flatter blue formats against original indigo relief."),
 "TX-WC":("WC inherits future TX-PRIMARY LEVEL floor exactly once, proposed F&D Riviera Oat 24x48 or Luxe Sand 24x24; no independent WC tile or PAN.","Current SEEDED v4-TX-WC unscored; source TX203A location needs native receipt verification.","Choose parent Primary champion and check WC true placement before final owner sheet.")
}
assert set(spec)==set(rooms)
files={}
for room,(surface,plumb,decision) in spec.items():
 r=rooms[room]
 gross=sum(float(x["qty_sf_per_unit"]) for x in r["carried_tile_rows"] if x.get("extended_quote_cost_usd_per_unit") is not None)
 old=r.get("carried_quote_material_subtotal_usd_per_unit") or 0
 priced=("No independent material line: WC tile included in Primary parent floor." if room.endswith("-WC") else f"Original source per copy **${old:.2f}** x {r['unit_count']} physical copies = **${old*r['unit_count']:.2f}** material-only, source 15% waste already included once. Historical *priced row gross sum* {gross:.2f} SF is not a new takeoff.")
 if room in ("PH-POWDER","TX-POWDER","TX-POWDER2"):
  public="F&D La Belle Purity/Antique Blue posted **$5.56/SF online**; original project gross × that rate is only a comparison, excluding cartons, freight, vendor pricing and owner upgrade authority."
 else:
  public="F&D Luxe Sand 24x24 current observed **$3.49/SF** at a non-Chicago store, Riviera Oat 24x48 **$3.99–$4.39/SF** across stores; current Chicago stock/lot/current price NULL, and ELM substitution wall/niche quote NULL. Neither gross nor new complete room cost is verified."
 status=("ACTIVE existing recorded champion only; not owner-approved" if r["status"]=="active" else "SEEDED unscored, not owner-approved" if r["status"]=="seeded" else "BLOCKED — no existing compliant reviewed champion")
 content=f"""# {room} — tile owner decision preview — 2026-11-06 / NOT APPROVED

**Formal room status:** {status}. **Physical copies:** {r['unit_count']}. **New R018–R022 alternatives are UNSCORED**, not independently cleared or approved.

**Surface-by-surface design direction:** {surface}

**Why this scheme:** Retain existing selected plumbing and original room hierarchy; use manufacturer-listed wet WALL/NICHE only where relevant, keep large-format tile (24in+ side) continuous between bath LEVEL and installer-cut PAN where the exact SKU individually allows wet shower floors. Powders remain dry tile features with wood floors; WC floors inherit their parent Primary.

**Actual plumbing and owner decisions:** {plumb}

**Original budget versus proposed price:** {priced} {public} Alternative per-room buyable/carton cost and the unselected owner tile-budget-upgrade ceiling remain **UNKNOWN**. No second 15% waste is added. Installer-cut PAN replacement scenario requires true native net LEVEL vs PAN area, with separate **illustrative 15% LEVEL / 25% PAN waste assumptions**, not quantities authorized for purchase.

**Old Town property/photo comparison:** OT01–OT04 405 W Armitage are **one building**. One OT01 powder-like photo shows contrasting rectangular floor, white wainscot, dense upper wall pattern and dark vanity; it does **not** identify specific manufacturer, grout or Primary wet shower finish. OT05 1849 N Mohawk #PH is a separate Old Town Triangle sold comp but **its bathroom interior photos remain unauthenticated**, so no tile/color/grout claims. [OT01 report](../../research/comps/R020_OLD_TOWN_ATRIBUTABLE_BATH_PHOTO_OBSERVATIONS.md) | [OT05 report](../../research/comps/R021_OT05_PHOTO_PROVENANCE_AND_OLD_TOWN_COMPARISON.md). Lincoln Park/Gold Coast secondary.

**Owner-only decision / release blocker:** {decision} See [three-plus allowed-vendor options by exact tiled surface](../../rooms/{room}/vendor_comparison.md), [large-format exact maker evidence](../../research/products/R022_FD_LUXE_SAND_RIVIERA_OAT_24PLUS_LEVEL_AND_SHOWER_PAN.md) and actual room source files for remaining manufacturer gates. Revit model `25-006 1527 N Wieland` = 1529 SAME BUILDING owner-confirmed; actual native bath-specific element IDs, tile placement, and true floor/PAN split not yet source-receipt matched.

**Release:** Current owner approval **FALSE**; final sample/quote **NOT REQUESTED**; four independent specialist board acceptance **NOT RECORDED**; material purchase **FALSE**. This is ONE provisional room sheet, not a signed specification.
"""
 path=out/(room+".md")
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(content,encoding="utf-8",newline="\n")
 b=path.read_bytes()
 files[str(path.relative_to(ROOT)).replace("\\","/")]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
parents={}
for name in ("state/ROUND018_TUB_TILE_SOURCE_PREPARED_AWAIT_BLIND_PREFLIGHT.json","state/ROUND019_TILE_ONLY_NEXT_COHORT_SOURCE_AWAIT_R018_FORMAL_CLEARANCE.json","state/ROUND020_PRIMARY_TILE_SOURCE_PREPARED_NOT_SUBMITTED.json","state/ROUND021_POWDER_TILE_PRELIMINARY_SOURCE_NOT_SUBMITTED.json","state/ROUND021_ALLOWED_VENDOR_POLICY_AND_EXTRA_CHALLENGERS_PRELIMINARY.json","state/ROUND022_LARGE_FORMAT_PRIMARY_PH4_SOURCE_PRELIMINARY_NOT_SUBMITTED.json"):
 b=(ROOT/name).read_bytes()
 parents[name]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
receipt.write_text(json.dumps({"round":22,"status":"13_NEW_SINGLE_PAGE_CONTENT_PREVIEWS_PROVISIONAL_NOT_APPROVED","rooms":list(spec),"copies":26,"historical_material_total_usd":23572.44,"source_15percent_waste_once":True,"files":files,"parent_receipts":parents,"champions_changed":False,"board_reviewed":False,"owner_approved":False,"purchased":False},indent=2)+"\n",encoding="utf-8",newline="\n")
print("R022 owner previews",len(files),"files + SHA receipt",receipt.name)

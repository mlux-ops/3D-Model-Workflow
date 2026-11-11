"""Additive, neutral R025 PH selection research; R024 scoring phase remains separate."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import hashlib, json

ROOT=Path(__file__).resolve().parents[1]
ROOMS={x["id"]:x for x in json.loads((ROOT/"state/ROOMS.json").read_text(encoding="utf8"))["rooms"]}
SOURCE="research/products/R025_PH_THREE_ROOM_QUOTED_ELM_FD_LFT_WET_GATE_EVIDENCE.md"
RECEIPT="state/ROUND025_PH_THREE_ROOM_PREPARED_NOT_SUBMITTED.json"
assert not (ROOT/SOURCE).exists() and not (ROOT/RECEIPT).exists()

wall={
 "Bone":("Elm Cortar Bone FLAT Soft","24x48","Soft flat, 9mm quoted","https://www.elmsurfaces.com/product/cortar-bone","8.14","Individual flat Bone wet WALL listing, not Reed/Ribbed"),
 "Sapphire":("Elm Tones Sapphire","2x20","Glossy 8.5mm","https://www.elmsurfaces.com/product/sapphire-tones","6.95","Individual Sapphire wet WALL listing"),
 "Copper":("Elm Tones Copper","2x20","Glossy 8.5mm","https://www.elmsurfaces.com/product/copper-tones","6.95","Individual Copper wet WALL listing"),
 "Sandstone":("Elm Tones Sandstone","2x20","Glossy 8.5mm","https://www.elmsurfaces.com/product/sandstone-tones","6.95","Individual Sandstone wet WALL/NICHE listing")}
floor={
 "Luxe":("Vetta Elements Luxe Sand Matte Ivory","24x24","23.70x23.70","rectified 8mm matte","101317949","https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html","3.49","3.49", "15.52"),
 "Riviera":("Vetta Elements Riviera Oat Matte Beige","24x48","23.58x47.28","rectified 8mm matte","101487775","https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html","3.99","4.39","16.00")}
spec={
 "PH-PRIMARY":{
  "A":dict(w="Bone",n=None,f="Luxe",design="A quiet, consistent ivory concrete-look 24x24 wet LEVEL + LINEAR PAN sets the Brilliance Black Onyx hardware against a composed flat Bone large-format wall.",program="Selected 48-inch Brizo BT0734816-BNX Black Onyx LINEAR with separate BR73480 rough, factory solid BNX grate and NO Primary NICHE; PH-WC inherits parent LEVEL tile once."),
  "B":dict(w="Bone",n=None,f="Riviera",design="Warm 24x48 travertine-look floor carried through the LINEAR PAN gives a softer Old Town-oriented stone appearance than the square concrete look; the same flat Bone wet WALL remains minimal.",program="Selected 48-inch Brizo BT0734816-BNX Black Onyx LINEAR plus separate BR73480 rough, solid BNX grate; NO niches, PH-WC inherits the LEVEL floor once.")},
 "PH-BATH3":{
  "A":dict(w="Sapphire",n="Sandstone",f="Luxe",design="Sapphire glossy vertical wet field adds controlled color against Hansgrohe Chrome and a restrained pale concrete-look 24x24 floor; Sandstone niche adds a measured warm note.",program="Hansgrohe Chrome wet fixtures. TUB vs WALK-IN OWNER-UNSELECTED. Delta DT062412 Chrome square POINT drain ONLY if WALK-IN is selected; no POINT PAN under TUB. Basin OWNER-UNSELECTED."),
  "B":dict(w="Copper",n="Sandstone",f="Riviera",design="Tones Copper glossy wet surround and beige Riviera Oat 24x48 LEVEL floor create a warmer tactile palette against Chrome; Sandstone niche connects the glazed wall to the stone-look floor.",program="Hansgrohe Chrome shower trim. TUB vs WALK-IN OWNER-UNSELECTED. Delta DT062412 Chrome square POINT only in WALK-IN branch; no shower PAN for TUB branch. Basin remains OWNER-UNSELECTED.")},
 "PH-BATH4":{
  "A":dict(w="Bone",n="Sandstone",f="Luxe",design="Flat Bone wet wall replaces unlisted Ribbed; a warm Sandstone glossy wet NICHE adds one focal insert, while 24x24 Luxe Sand continues across LEVEL and installer-cut POINT PAN against BNX.",program="Owner-selected WALK-IN retained, Brizo BT062415-BNX 4-inch square Black Onyx POINT drain unchanged; independent four-plane installer-cut PAN."),
  "B":dict(w="Bone",n="Copper",f="Riviera",design="Soft limestone-look Bone flat walls and Copper glazed niche introduce a bolder accent, balanced by 24x48 warm travertine-look LEVEL and four-plane POINT PAN alongside BNX.",program="Owner-selected WALK-IN, Brizo BT062415-BNX 4-inch square Black Onyx POINT fixed, not a TUB; large-format four-plane pan cut by installer.")}}
assert set(spec)=={"PH-PRIMARY","PH-BATH3","PH-BATH4"}
for rid in spec:
 assert ROOMS[rid]["status"]=="blocked"
 assert not (ROOT/"rooms"/rid/"board"/"round-025").exists()
def money(x):
 return str(Decimal(str(x)).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP))

source_text="""# R025 source-traceable PH tile alternatives: published wet WALL, NICHE, large-format LEVEL/PAN

Observed 2026-11-07. This is **next-cohort PREPARED source only** while formal R024 PH-BATH2/TX-BATH2/TX-BATH4 four-critic board is still active. R025 is NOT submitted, independently preflighted or scored. All signed R018-R024 source receipts remain immutable.

**Authoritative four vendors:** Elm Surfaces, MSI Surfaces, Porcelanosa and Floor & Decor. No Platform, Emser or Daltile proposed tile. Owner's 24-inch-plus preference for both bath LEVEL and shower PAN governs, with owner installer cutting/sloping; an actual verified focal sliver under ~3in remains a geometry gate. Same product SKU proposed in LEVEL and independently assessed LINEAR/POINT PAN; no PAN for a tub program.

**ELM exact individual products:** [Cortar Bone FLAT Soft 24x48](https://www.elmsurfaces.com/product/cortar-bone) Wet Areas WALL (NOT Bone Ribbed/Reed); [Tones Sapphire 2x20 Glossy](https://www.elmsurfaces.com/product/sapphire-tones) Wet Areas WALL; [Tones Copper 2x20 Glossy](https://www.elmsurfaces.com/product/copper-tones) Wet Areas WALL; [Tones Sandstone 2x20 Glossy](https://www.elmsurfaces.com/product/sandstone-tones) Wet Areas NICHE/WALL. Do not apply wet-wall use to FLOOR. Exact matching job-25-006 Elm quote dated 2026-09-04 thread 1a068e80c92c255f: flat Cortar Bone 24x48 **$8.14/SF** (15.39 SF/box; original import estimate 10–12 weeks) and Tones Sapphire/Copper/Sandstone Glossy 2x20 **$6.95/SF** (6.50 SF/box), no manufacturer price invention. Quote is not confirmed current Chicago stock or delivered total.

**F&D product-specific floor/pan use:** [Luxe Sand 24x24 matte rectified 8mm, SKU101317949](https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html) individual DCOF >=0.42, Bathroom Floor YES, Shower Floor YES, public observed **$3.49/SF**, 15.52SF/box. [Riviera Oat 24x48 matte rectified 8mm, SKU101487775](https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html) individual DCOF >=0.42, Bathroom Floor YES, Shower Floor YES, 16.00SF/box, public varied **$3.99–$4.39/SF** across store snapshots. These are product-specific published lower bounds, NOT fabricated raw lab point readings. Retail USA route evident; current Chicago matching-lot inventory, pickup quantity, current carton price and delivery ETA UNKNOWN. Proposed 1/8-inch grout (listed within maker 1/16/1/8/3/16) requires owner grout/color approval.

**Original cost discipline:** 13 original rooms / 26 physical instances / 27 material rows / four-unit $23,572.44 unchanged. Original gross SF already contains 15% waste ONCE. Quote-screen floor price on *original combined gross* is not a split across LEVEL, shower PAN and WC. For new quantity comparison only, independently verified LEVEL net x1.15 + PAN net x1.25 + inherited Primary WC net x1.15; never add this atop source gross. Actual native net PAN/waterproof/drawings, cabinet openings, cut-heavy box rounding and manufacturer wall-ceiling scope remain unresolved. Product-only look and price comparisons do NOT pass complete delivered-budget, geometry or Chicago stock gates.

**Existing plumbing/owner selection preserved:** PH-PRIMARY 48in LINEAR BNX BT0734816-BNX and separate BR73480 rough, solid factory grate, no niches, PH-WC inherits floor; PH-BATH4 selected WALK-IN BNX BT062415-BNX square POINT, installer-cut four-plane PAN; PH-BATH3 TUB-vs-WALK-IN owner undecided, Hansgrohe Chrome and conditional Delta DT062412 square POINT only under WALK-IN, PH3 basin unselected. No 6mm mosaic asserted compatible with 7–18mm tile-in assembly. Solid BNX factory grate preferred.

**Old Town photos:** research/comps/R020_OLD_TOWN_ATRIBUTABLE_BATH_PHOTO_OBSERVATIONS.md supports only a powder-like OT01 photographed layering and contrast. OT01–04 405 W Armitage are ONE design/building. OT05 separate sale, but its bathroom photograph is not authenticated; wet tub/primary wall SKU, grout and fixture finish remain UNKNOWN. Never substitute an unrelated stock photo, Lincoln Park and Gold Coast secondary.

**Receipt/approval:** Owner confirms 1527/1529 same building, not proof that earlier provisional W1–W3 lengths and openings are native-element-certified. Native Revit source job receipt IDs must accompany any future geometry clearance. Zero independent R025 preflight/critics; owner budget stance still unselected. No outreach, sample, PO, fabrication, jigs, construction documents or other original source modifications.
"""
p=ROOT/SOURCE
p.write_text(source_text,encoding="utf8",newline="\n")
manifest={SOURCE:{"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":len(p.read_bytes())}}

for rid,opts in spec.items():
 r=ROOMS[rid]
 rows={x["surface"]:x for x in r["carried_tile_rows"]}
 cw,cf,ca=rows["wall"],rows["floor"],rows["accent"]
 old_total=Decimal(str(r["carried_quote_material_subtotal_usd_per_unit"]))
 cap=old_total*Decimal("1.25")
 geom=json.loads((ROOT/"rooms"/rid/"geometry.json").read_text(encoding="utf8"))
 walls="; ".join(f'{x["id"]} provisional {x["length"]["value"]:.3f}ft x {x["tiled_height"]["value"]:.2f}ft' for x in geom.get("tiled_walls",[]))
 for letter,s in opts.items():
  w,n,f=wall[s["w"]],wall[s["n"]] if s["n"] else None,floor[s["f"]]
  wname,wsize,wfinish,wurl,wrate,wperm=w
  fname,fsize,factual,ffinish,fsku,furl,flow,fhigh,fbox=f
  wallcost=Decimal(str(cw["qty_sf_per_unit"]))*Decimal(wrate)
  nichecost=(Decimal(str(ca["qty_sf_per_unit"]))*Decimal(n[4]) if n is not None else Decimal("0"))
  floor_low=Decimal(str(cf["qty_sf_per_unit"]))*Decimal(flow)
  floor_high=Decimal(str(cf["qty_sf_per_unit"]))*Decimal(fhigh)
  screen_low=wallcost+nichecost+floor_low
  screen_high=wallcost+nichecost+floor_high
  allrows=f"Wall source {cw['smartsheet_row_id']} {cw['qty_sf_per_unit']:.2f} gross SF x exact Elm quote ${wrate}/SF = ${money(wallcost)}; bath LEVEL/PAN{'/PH-WC' if rid=='PH-PRIMARY' else ''} original source {cf['smartsheet_row_id']} {cf['qty_sf_per_unit']:.2f} combined gross SF x publicly observed F&D ${flow}–${fhigh}/SF = ${money(floor_low)}–${money(floor_high)}; accent source {ca['smartsheet_row_id']}"
  if n:
   allrows+=f" {ca['qty_sf_per_unit']:.2f} gross SF x actual quoted Tones ${n[4]}/SF = ${money(nichecost)}."
  else:allrows+=" HISTORICAL REFERENCE UNPRICED/EXCLUDED, NO PRIMARY NICHE."
  fpan=("Selected 48-inch LINEAR PAN" if rid=="PH-PRIMARY" else "Selected four-plane POINT PAN" if rid=="PH-BATH4" else "WALK-IN conditional four-plane POINT PAN; TUB branch has NO tiled PAN")
  niche_line=(f"[{n[0]} {n[1]} {n[2]}]({n[3]}) independently listed for Wet Areas NICHE/WALL; same-job Elm $6.95/SF quote; actual niche edge/cuts and shade lot pending." if n else "NONE. Owner explicitly rejected additional Primary niches; no niche area or purchase.")
  text=f"""# {rid} — R025 neutral design option {letter}, PREPARED only

This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified. Nothing is approved or score-selected.

**Actual selected program/fixtures:** {s['program']}

**SHOWER/TUB WET WALL:** [{wname}, {wsize}, {wfinish}]({wurl}), exact individual ELM product Wet Areas WALL listing. Not transferable to unlisted relief/Ribbed, ceiling or floor. Any existing source ceiling face requires separate ceiling application proof.

**Separate NICHE:** {niche_line}

**BATH LEVEL tile:** [Floor & Decor {fname} nominal {fsize} actual {factual}, {ffinish}, SKU {fsku}]({furl}). Exact published **wet DCOF >=0.42; Bathroom Floor YES**, U.S. product listing active.

**Separate SHOWER PAN:** {fpan}. If PAN applies, same exact {fsku} {fsize} tile individually listed **Shower Floor YES**, published wet DCOF >=0.42, owner installer cuts/slopes the larger tile to the selected POINT/LINEAR drain; not a claim of actual site slope/cut feasibility. No other pan SKU, no switch to unapproved Emser/Daltile mosaic. For the PH-BATH3 TUB branch there is NO pan and the conditional Delta POINT drain is not a tub waste. Proposed maker-listed 1/8-inch grout baseline, final grout color and cut layout owner/installer verification.

**Architecture/market reasoning:** {s['design']} OT01 a photographed DRY powder-like room supports the principle of layered contrasting materials, NOT an exact competing wet wall/floor SKU. OT05 interior bath photo remains unauthenticated, so no claimed tile/grout/fixture identity or buyer premium. Old Town primary, Lincoln Park/Gold Coast secondary.

**Historic one-copy cost screening and 125% board ceiling:** {allrows} Original carried **${money(old_total)}/copy** and board gate 125% **${money(cap)}/copy**. Screened *one-copy SF-extended product subtotal* **${money(screen_low)}–${money(screen_high)}** (the source gross already includes 15% waste ONCE); TWO historical room instances have source quantities doubled for four-unit accounting only. This is NOT a box-rounded, delivered, additional cut-pan waste, trim/grout, true area, installed or Chicago-stock confirmed total; therefore **complete budget gate remains UNKNOWN** even if source-SF screen is below cap. Actual contractual trade price is the 2026-09-04 1529 Elm quote for exact item; F&D public price not confirmed local/store.

**Quantity replacement (never double waste):** Resolve LEVEL net and separate PAN net/Primary WC net by native receipt and owner program. New-option illustrative gross = LEVEL net x1.15 + installer-cut PAN net x1.25 + inherited PH-WC net x1.15 only when Primary. If TUB branch, PAN N/A. This REPLACES the original blended 15%-inclusive gross; it is NOT an additional percentage on the original. Only then compute complete cartons by F&D {fbox} SF/box and exact Elm {('15.39' if s['w']=='Bone' else '6.50')} SF/box plus niche 6.50 SF/box.

**Geometry and owner hard-gate uncertainty:** Native model 25-006 1527 N Wieland is the same 1529 building per owner. Drawing-only source walls: {walls}. Exact Revit receipt and wall/door/niche/fixture offsets unavailable in this source; reject confirmed unavoidable visible <3in slivers, NOT large-format pan solely for installer-managed slope. Chicago exact F&D lot/on-hand/ETA, Elm current warehouse, imported flat wall lead and whole-room cut waste unknown. No owner program selected for PH3, no owner grout/budget upgrade endorsement, no fixture or basin substitutions.

**Research lineage:** research/products/R025_PH_THREE_ROOM_QUOTED_ELM_FD_LFT_WET_GATE_EVIDENCE.md; individual official links above; owner-provided inputs/TRADE_QUOTES.md 2026-09-04 source thread 1a068e80c92c255f. Three-vendor per-surface comparisons recorded in current vendor-comparison addenda; Porcelanosa Bottega Caliza exact wet DCOF unknown so not a qualified floor/pan.

**Status:** ADDITIVE PREPARED R025 option, not frozen/submitted/dispatched. No four independent critics, scored ratings, owner approval, supplier contact, samples or orders.
"""
  dest_rel=f"rooms/{rid}/board/round-025/prepared/candidates/{letter}.md"
  dest=ROOT/dest_rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding="utf8",newline="\n")
  buf=dest.read_bytes();manifest[dest_rel]={"sha256":hashlib.sha256(buf).hexdigest(),"bytes":len(buf)}
parents={}
for name in ("state/ROUND019_TILE_ONLY_NEXT_COHORT_SOURCE_AWAIT_R018_FORMAL_CLEARANCE.json",
             "state/ROUND022_LARGE_FORMAT_PRIMARY_PH4_SOURCE_PRELIMINARY_NOT_SUBMITTED.json",
             "state/ROUND023_TRADE_PRICING_13_ROOM_ADDENDUM_SHA.json",
             "state/ROUND024_FROZEN_THREE_DURAVIT_TUB_BLIND_SOURCE.json"):
 payload=(ROOT/name).read_bytes()
 parents[name]={"sha256":hashlib.sha256(payload).hexdigest(),"bytes":len(payload)}
(ROOT/RECEIPT).write_text(json.dumps({
 "round":25,"phase":"SOURCE_PREPARED_NOT_SUBMITTED_R024_BOARD_ACTIVE",
 "cohort":["PH-PRIMARY","PH-BATH3","PH-BATH4"],
 "files":manifest,"immutable_parents":parents,
 "allowed_vendors":["Elm Surfaces","MSI Surfaces","Porcelanosa","Floor & Decor"],
 "historical_material_total_usd":23572.44,
 "all_six_product_schemes":"ELM exact wet-listed wall/niche + F&D exact large-format wet LEVEL and conditional shower PAN",
 "PH_BATH3_owner_tub_vs_walkin":"UNSELECTED",
 "PH_BATH3_owner_basin":"UNSELECTED",
 "reviewer_preflight":None,"critic_dispatch":None,"weighted_scores":None,
 "champions_changed":False,"owner_approved":False,"samples_ordered":False
},indent=2)+"\n",encoding="utf8",newline="\n")
print("R025 PH PREPARED:",len(manifest),"new SHA/byte entries, 6 neutral options for 3 blocked PH rooms; no active board overlap")

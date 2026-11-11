"""R016 three dry powder rooms: two balanced neutral source designs each.

Source-only next-board design work, not original-critic dispatch or scoring.
All predecessor rounds, ledger/ROOMS, Revit, Smartsheet and purchasing unchanged.
"""
from pathlib import Path
from decimal import Decimal
import csv,hashlib,json,re
R=Path(__file__).resolve().parents[1]; S=R/"state"
OUT=S/"ROUND016_SUBMISSION.json"
assert not OUT.exists()
assert not (S/"ROUND016_CRITIC_DISPATCH.json").exists()
assert not (S/"ROUND016_SCORING.json").exists()
assert not (S/"ROUND014_SCORING.json").exists()
assert not (S/"ROUND015_SCORING.json").exists()
def sig(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}

base=json.loads((S/"ROOMS.json").read_text(encoding="utf-8"))
rooms={r["id"]:r for r in base["rooms"]}
expected={
 "PH-POWDER":{"area":"44.9","usd":"368.18","W":"4.224","faucet":"Brizo Frank Lloyd Wright T65722LF-GL Luxe Gold with R65700 wall rough and RP72414GL drain","letters":{"A":"Earth Lines uniform full-height 2x10 glossy relief dry wall","C":"Earth Lines 2x10 relief field flanking a FLAT PAINTED faucet mounting landing (not a second tile SKU)"}},
 "TX-POWDER":{"area":"31.8","usd":"379.37","W":"2.99","faucet":"Hansgrohe wall faucet 48140991 and wall rough 32526141, exact observed finish not verified","letters":{"B":"ELM Vera Forma Earth Lines 2x10 glossy relief on dry vanity wall","C":"ELM Haze Camel/Wheat 1.6x5 matte 70/30 controlled band on dry vanity wall"}},
 "TX-POWDER2":{"area":"40.5","usd":"332.10","W":"3.806","faucet":"Hansgrohe Tecturis E 73072341 Brushed Black Chrome DECK-mounted, owner sink/basin UNSELECTED","letters":{"A":"ELM Vera Forma Earth Lines 2x10 glossy relief at entire dry vanity wall","B":"ELM Vera Forma Indigo Edge 6x6 glossy relief at entire dry vanity wall"}}
}
assert all(rooms[k]["status"]=="active" for k in expected)
maker={
 "Earth Lines":{
  "title":"ELM Vera Forma Earth Lines 2x10 Glossy Relief",
  "url":"https://www.elmsurfaces.com/product-collection/vera-forma",
  "local":"research/products/elm-vera-forma-earth-lines-2x10.md",
  "role":"walls only; WET AREAS not listed; no DCOF required for dry wall",
  "source":"PH Powder original 2026-09-03 $8.20/SF only; not a current TX room quote or installed bid",
  "construction":"nominal 2x10, ceramic glossy relief 8.6mm; maintain planar grout/edge landing for wall rough; exact lot, carton and cut calibration unknown"
 },
 "Haze":{
  "title":"ELM Haze Camel / Wheat 1.6x5 Matte",
  "url":"https://www.elmsurfaces.com/product-collection/haze",
  "local":"research/products/elm-haze-camel-1p6x5.md ; research/products/elm-haze-wheat-1p6x5.md",
  "role":"walls only; wet authorization not listed; bath LEVEL/PAN N/A",
  "source":"TX Powder original 2026-09-03 blended Haze material $379.37/room copy; original quoted color-specific SKU/case split unknown",
  "construction":"two independent 8mm matte Haze colors, exact 70/30 cut and carton count held; no two full-wall quantities"
 },
 "Indigo":{
  "title":"ELM Vera Forma Indigo Edge 6x6 Glossy Relief",
  "url":"https://www.elmsurfaces.com/product/indigo-edge-vera-forma",
  "local":"research/products/elm-vera-forma-indigo-edge-6x6.md",
  "role":"walls only; no individual WET AREAS listing; no shower or floor",
  "source":"TX Powder2 original 2026-09-03 $8.20/SF, 40.5 gross SF = $332.10/copy (source gross 15% already)",
  "construction":"6x6 glossy relief 8.6mm, source 30 pieces/7.34 SF case is historical; actual lot/packing/Chicago fill/box calculation unverified"
 }
}
config={
 ("PH-POWDER","A"):("Earth Lines",
   "Full 4.224-ft source-width vanity feature WALL of 2x10 glossy relief with a controlled horizontal 2x10 running-bond study at the mirror and upper field, allowing a pre-determined planar faucet fixture block to be designed only AFTER actual escutcheon wall-plane shop dimensions. This layout prioritizes full feature-wall relief continuity; final real wall faucet penetrations in relief require an engineered FLAT sealing/escutcheon support that must not be assumed.",
   "Compare rich glossy earth relief against the selected Brizo Luxe Gold and existing wood-floor warmth, while keeping upper wall joints at a consistent module. Check reflective hotspots in direct downlight, not invented photos. No planned new surface or approved substitute.",
   "No new flat panel material cost assumed; existing historical 44.9 SF gross is merely the v4 baseline, not a current purchasable carton count."),
 ("PH-POWDER","C"):("Earth Lines",
   "Same manufacturer 2x10 relief limited to balanced vertical feature fields flanking an explicitly DRY painted, perfectly flat central faucet/escutcheon landing aligned with the actual Brizo rough; central painted area geometry and edge trim require the verified 1529 wall projection and selected mirror width. No flat tile SKU is invented. This is a physically different joint/cut/finish composition; do not assume the full original 44.9-SF relief source quote also applies after displaced center area.",
   "Creates intentional relief-to-flat visual hierarchy and an accessible Luxe Gold trim landing while preserving warm organic Old Town appeal. The painted strip is a concept, not owner-approved material/paint; evaluate full-size split under sconce and mirror light before comparing to uninterrupted relief.",
   "New relief net and paint/trim quantities are UNKNOWN; historical 44.9 SF v4 gross and $368.18/copy retained only as budget comparison, not a new same-scope promise."),
 ("TX-POWDER","B"):("Earth Lines",
   "Single dry 2x10 glossy relief Earth Lines material on the provisional 2.99-ft vanity wall; vertically align tile modules with the selected Hansgrohe wall faucet 48140991 and verified wall-mounted rough 32526141. Inset a documented future approved flat backer/escutcheon plane without importing PH Brizo fixture. This material's finish is a substantive alternative to matte 1.6x5 Haze, not a source-rate switch.",
   "A more sculptural glossy vanity focus echoing the penthouse material language; confirm adjacent lower-gloss finishes, mirror height and faucet contrast physically, not a photographic claim. Avoid a fake second tile niche or shower floor.",
   "Only PH Earth Lines historical $8.20/SF reference exists; no TX-specific Earth Lines offer and no current Chicago landed/installed price. Existing TX Powder $379.37/copy remains comparator only."),
 ("TX-POWDER","C"):("Haze",
   "Dry Haze Camel matte 70 percent plus Haze Wheat 30 percent in broad intentional bounded vertical bands and aligned 1.6x5 matte modules; center the Hansgrohe 48140991 and separate 32526141 rough on an actually verified flat planar landing. Both colors share ONE wall takeoff and proportioned actual cut plan, not two independently grossed 31.8-SF walls.",
   "Quiet contemporary two-tone Old Town powder to offset the colorful upper baths; use true 1:1 Camel/Wheat/grout/metal color study with wood floor and mirror. Lighting may alter Wheat/Camel contrast, do not assert manufacturer paint equivalence.",
   "The original two-color gross 31.8 SF/copy and $379.37/copy contain the first 15% once, but individual color cartons, lot, delivery, current installed labor and owner cap are unknown."),
 ("TX-POWDER2","A"):("Earth Lines",
   "Replace all of the provisional 3.806-ft dry vanity feature wall with nominal 2x10 Earth Lines glossy relief; center horizontal courses to future verified mirror, and keep the ALREADY SELECTED Hansgrohe 73072341 faucet on the COUNTERTOP, not through a tile wall. Actual sink/basin and deck penetration remain OWNER UNSELECTED and cannot be depicted as an approved fixture. No flat-tile splash insert or other new tile color is ordered.",
   "A linear, sculptural but reduced individual-joint composition compared to 6x6 Indigo relief; test warm Earth Lines against Brushed Black Chrome Tecturis and wood floor in physical light, not via unverified product photo.",
   "PH Earth Lines $8.20/SF is only a dated OTHER-ROOM material reference; 40.5 SF gross and $332.10/copy are original Indigo reference, NOT the new Earth Lines quote or orderable quantity."),
 ("TX-POWDER2","B"):("Indigo",
   "Continue 6x6 Indigo Edge glossy relief on the entire provisional 3.806-ft wide dry wall, with six full nominal modules and balanced end pieces about 4.84in BEFORE actual calibrated joints/openings. Keep lower wall tile as a single 6x6 SKU without the previously costly unpriced smooth tile insert; the selected Hansgrohe deck faucet must land in an owner-selected countertop/basin outside the tile, not on the wall.",
   "Retain more playful Indigo square relief and coordinate a centered mirror edge, TOTO toilet and Brushed Black Chrome deck faucet without falsely selecting a basin or placing a wall escutcheon. A physical 1:1 grout/edge mockup is still required.",
   "Original 40.5 SF/copy at $8.20/SF = $332.10/copy; 30 pieces/7.34SF historical case is unverified for actual lot, and installed bid remains absent.")
}
assert set(config)=={(r,l) for r,c in expected.items() for l in c["letters"]}
source_files={}
private_map={
 "PH-POWDER":{"A":"carried Earth Lines relief full wall with support details","C":"alternative Earth Lines flanks and flat DRY painted faucet landing"},
 "TX-POWDER":{"B":"alternative Earth Lines single-color sculptural wall","C":"board-carried Haze Camel/Wheat controlled 70/30"},
 "TX-POWDER2":{"A":"alternative Earth Lines 2x10 full dry wall","B":"carried Indigo 6x6 full dry wall with verified centered cuts"}
}
common=R/"research/products/R16_POWDER_THREE_ROOM_FLAT_LANDING_SHOP_AND_COMP_SOURCE_20261106.md"
assert not common.exists()
common.write_text("""# R016 maker-specific three dry powder wall evidence and shop conditions — 2026-11-06

PH Powder, TX Powder and TX Powder2 are DRY tile vanity-wall programs over WOOD floors. They have NO tiled bath LEVEL wet DCOF test and NO tiled shower PAN, drain slope, shower niche or wet-wall test. All maker Tiles here list WALLS only: never transfer to the other eight wet bath rooms.

Individual maker records:
- [ELM Vera Forma collection](https://www.elmsurfaces.com/product-collection/vera-forma): Earth Lines 2x10 glossy relief, wall-only 8.6mm. The only historical Earth Lines project rate is PH Powder $8.20/SF (2026-09-03); not a valid current TX room supplier/installed price. Color-specific exact current SKU, supplier cartons/lot, Chicago ETA, usable full-size trim and mockup remain null.
- [ELM Haze Camel](https://www.elmsurfaces.com/product/haze-camel) and [Haze Wheat](https://www.elmsurfaces.com/product/haze-wheat): matte 1.6x5 dry wall-only 8mm, candidate two-color quota shares ONE wall; the only carried TX Powder blended source is $379.37/copy, color-specific carton/yield unknown.
- [ELM Vera Forma Indigo Edge](https://www.elmsurfaces.com/product/indigo-edge-vera-forma): 6x6 glossy relief dry wall-only 8.6mm, TX Powder2 historic $332.10/copy and 40.5-SF gross with original 15% allowance once; nominal 30pc/7.34SF historical case not a live lot allocation.

Physically selected fixture distinctions: PH Powder Brizo Frank Lloyd Wright T65722LF-GL Luxe Gold with wall rough R65700, drain RP72414GL; proposed deck AXOR alternative not accepted. TX Powder Hansgrohe WALL faucet 48140991 with 32526141 rough; exact selected finish and alignment survey still hold. TX Powder2 Hansgrohe Tecturis E 73072341 Brushed Black Chrome is DECK-mounted and sink/basin is owner UNSELECTED; do not design a wall escutcheon or drill countertop holes. Verify porcelain/vitreous-ceramic relief plane versus flat mounting support, tile transition, soft joints and mirror/backing in a 1:1 mockup.

Source widths/heights are UNVERIFIED 1529: PH 4.224ft, TX Powder 2.990ft, TX Powder2 3.806ft; 9.25-ft drawing tiled height, no opening/niche/window or actual faucet plane confirmed by current model (open title 1527). Field net SF, trims LF and per-color case yields remain null. Original one-time 15% waste in gross cannot be applied again; floor wood and current quotes, freight, tax and setting labor out of old material numbers. No actual market photo supports a claimed competitor tile; 14 listing entries are nine buildings, Armitage repeated once, recent Old Town primary, Lincoln Park/Gold Coast secondary, PH $2.8M/TX $2.7M.

These are candidate-neutral maker/source conditions. Only prime or authorized independent Reviewer sees private mappings; no specialist scores, source role labels or implied owner approvals. Signed full-room GC work R17–R21 remains unchanged, no source tests/quotes/field measurements were invented.
""",encoding="utf-8")

for room,opts in expected.items():
 rec=rooms[room]
 w=Decimal(opts["W"])
 wall= (w*Decimal("9.25")).quantize(Decimal("0.001"))
 assert len(rec["carried_tile_rows"])==1
 assert Decimal(str(rec["carried_tile_rows"][0]["qty_sf_per_unit"]))==Decimal(opts["area"])
 assert Decimal(str(rec["carried_tile_rows"][0]["extended_quote_cost_usd_per_unit"]))==Decimal(opts["usd"])
 d=R/"rooms"/room/"board/round-016"
 assert not d.exists()
 (d/"candidates").mkdir(parents=True)
 source_files[room]={}
 for letter in opts["letters"]:
  makerkey,layout,visual,cost=config[(room,letter)]
  m=maker[makerkey]
  txt=[
   f"# {room} — Candidate {letter} — complete tile design option",
   "",
   "This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.",
   "",
   "## Complete physical scope and exact owner fixture",
   "",
   f"**Maker/finish:** {m['title']} — [manufacturer color/collection]({m['url']}); source-specific local evidence {m['local']}. **Application:** {m['role']}. Floor **WOOD**, no tile; no shower, tub, niche, tiled LEVEL or PAN. Two identical unit copies, no owner approval.",
   "",
   f"**Plumbing:** {opts['faucet']}. Preserve fixture type, selected metal and physical rough. No custom faucet/basin/owner changes are authorized. Check source [plumbing](../../../plumbing.json) and [provisional geometry](../../../geometry.json).",
   "",
   "## Layout, cuts, physical installation and 1:1 sample",
   "",
   layout,
   "",
   f"**Provisional wall:** W1 {opts['W']} ft × 9.25 ft = {wall} SF GROSS drawing face before openings (not verified 1529; openings and actual usable W1 plane NULL). Actual tile nominal module, grout width/finish, tile caliper, centered end cuts, mirror/rough centering, escutcheon flat landing, movement/edge termination and selected color swatch require verified 1529 survey. If any non-tile painted area is proposed, subtract it once from the tile net; do not invent its dimension or price.",
   "",
   "Sample 1:1 FULL tile, relief depth/flat landing, owner-selected faucet finish, actual substrate and grout/edge, wood-floor-to-wall transition and true warm/night illumination. Preserve the framed mirror and faucet clearances as UNVERIFIED, do not claim render truth until 1529 model verified.",
   "",
   "## Material, availability and historical cost basis",
   "",
   f"**Maker evidence:** {m['construction']} **Maker availability:** collection US-stocked/quick ship only; no dated local lot, lead, carton packing, trim or quote confirmed. **Source price:** {m['source']}.",
   f"**Original room-specific material comparator only:** {opts['area']} SF gross/copy (prior 15% waste INCLUDED ONCE), ${opts['usd']}/copy, two copies. Actual current option net, carton and installed cost `null`, independent owner upgrade budget `null`. {cost}",
   "",
   "No supplier order is calculable until actual exact SKU/color/finish and 1529 measured net, one approved new cut allowance and factory-confirmed carton SF, plus owner/architect/GC signatures, dated current Chicago supplier offer and complete installed quote. No phantom wall/floor, double waste, additional niches, price transfer or implicit acceptance.",
   "",
   "## Old Town buyer positioning and practical top fix",
   "",
   visual,
   "",
   f"Owner target PH $2.8M / TX $2.7M; 14 comparable entries = nine independent buildings, 405 W Armitage counted once. Recent Old Town primary; Lincoln Park/Gold Coast secondary. No unsupported competitor-bath photo finish assumptions. Source [common maker/GC brief](../../../../../research/products/R16_POWDER_THREE_ROOM_FLAT_LANDING_SHOP_AND_COMP_SOURCE_20261106.md).",
   "",
   "**Top coordination fix:** Verify true owner-selected faucet/rough face, mirror position, relief versus planar seal, wall measured net and complete same-SKU local installed quote. Unknowns remain explicit, not passed hard gates.",
   "",
   "**gate_flags:** DRY WALL wet-area and wet-floor PAN DCOF N/A; owner approval FALSE; actual 1529 geometry HOLD, Chicago current inventory/price/installed scope HOLD, owner room cap NULL; no source manufacturer discontinued/US distribution failure established; no selected plumbing substitution.",
   "",
   "**STATUS:** Source-neutral pre-dispatch design option only. No critic score, weighted score, owner acceptance, sample, render, GC acceptance or procurement authorization.",
   ""
  ]
  f=d/"candidates"/(letter+".md")
  f.write_text("\n".join(txt),encoding="utf-8")
  # Local evidence resolves from the candidate folder, and no source role mapping leaks.
  assert len(f.read_text(encoding="utf-8").splitlines())>=33
  assert not re.search(r"(?i)incumbent|challenger|prior round|original candidate|revised candidate|weighted champion",f.read_text(encoding="utf-8"))
  assert (f.parent/"../../../geometry.json").exists()
  assert (f.parent/"../../../../../research/products/R16_POWDER_THREE_ROOM_FLAT_LANDING_SHOP_AND_COMP_SOURCE_20261106.md").exists()
  source_files[room][letter]={"path":str(f.relative_to(R)).replace(chr(92),"/"),**sig(f)}
 priv={"round":16,"room":room,"confidential_prime_and_independent_reviewer_only":True,
       "neutral_candidate_roles":private_map[room],"no_blind_worker_access":True,
       "last_scored_round":rec["last_round"]}
 (d/"_key.json").write_text(json.dumps(priv,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 assert json.loads((d/"_key.json").read_text(encoding="utf-8"))["room"]==room

submission={
 "round":16,"as_of":"2026-11-06","phase":"1-comps SOURCE_PREPARED_AWAIT_INDEPENDENT_PREDISPATCH",
 "focus_rooms":list(expected),"reason":"three active DRY powder rooms not blocked by Bath3 owner TUB/WALK-IN; prior scored lower than stable 4.0; selected faucets and 1to1 relief mounting, exact local cost and mirror/calibrated cuts are independently closable",
 "room_source_per_copy_gross_and_usd":{k:{"gross_sf_with_original_15pct_once":v["area"],"material_usd":v["usd"],"copies":2} for k,v in expected.items()},
 "candidate_source":source_files,
 "confidential_mappings":{k:f"rooms/{k}/board/round-016/_key.json" for k in expected},
 "shared_maker_research":str(common.relative_to(R)).replace(chr(92),"/"),
 "shared_maker_research_fingerprint":sig(common),
 "owner_approved":False,"correct_1529_native_model_verified":False,
 "all_critic_scores":None,"R016_weighted_scoring":None,
 "predispatch_reviewer_verdict":None,"critic_dispatch":"NOT_DISPATCHED",
 "original_R014_design_absent":True,"original_R015_four_seat_undispatched":True,
 "owner_bath3_program_preserved":True,"no_vendor_contact_or_purchase":True,
 "R014_source_sha256":sig(S/"ROUND014_SUBMISSION.json")["sha256"],
 "R015_source_sha256":sig(S/"ROUND015_SUBMISSION.json")["sha256"],
 "last_signed_R21_manifest_sha256":sig(R/"deliverables/integrated-r21-install-witness-sequence/MANIFEST.json")["sha256"]
}
OUT.write_text(json.dumps(submission,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert sum(Decimal(x["usd"])*2 for x in expected.values())==Decimal("2159.30")
assert sig(R/"deliverables/integrated-r21-install-witness-sequence/MANIFEST.json")["sha256"]==submission["last_signed_R21_manifest_sha256"]
print("PASS R016 three active POWDER rooms, six balanced source-only neutral candidates, three confidential prime mappings, exact original quote subset $2159.30 across two units/room, all DRY wall/wood-floor, no critiques/dispatched/scoring")
print("R016_SOURCE_SHA",sig(OUT)["sha256"])

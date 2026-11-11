from pathlib import Path
R=Path(__file__).resolve().parents[1]
paths={"PH-PRIMARY":"C","PH-BATH2":"A","PH-BATH4":"C"}
newopening={
"PH-PRIMARY":"**Room and designed finish basis.** Corner walk-in shower with separately selected Duravit tub; two PH copies. Wet walls/ceiling include Cortar Bone 24x48 Soft and a Bone Reed 24x48 Relief feature, with Bone 24x48 Soft level plus Bone 12x24 Anti-Slip shower-pan portions documented in ONE historical source-floor line. Existing selected plumbing: Brizo BT0734816-BNX/BR73480 48-in linear, Brilliance Black Onyx; **NO PRIMARY NICHE**. Product-specific wet relief and both exact floor/pan DCOF tests remain FAIL. Source original ELM/Smartsheet prices dated 2026-09-03 are material-only comparisons, not current prices or approvals.",
"PH-BATH2":"**Room and designed finish basis.** Source confirms an actual Duravit 700332000000090 tub alcove, Hansgrohe Matte White shower/tub fittings, and two PH copies. Wet walls are Tones Sapphire 2x20 Glossy stacked with Sandstone wet niche; level bath floor is Cortar Grey 12x24 Soft. Sapphire **individual maker Wet Areas PASS**; Cortar Grey Soft bath-floor exact measured wet DCOF is unknown/FAIL. There is **NO separate tiled shower pan or selected Brizo linear shower drain** in this room. The dated 2026-09-03 ELM source prices are material-only references and not authorized current bids.",
"PH-BATH4":"**Room and designed finish basis.** Actual source geometry identifies a WALK-IN shower with Brizo BT062415-BNX Brilliance Black Onyx 4-in tile-in SQUARE point drain and Roccesco shower controls, two PH copies. Source wet shower walls are **full Cortar Bone Ribbed 24x48 Relief**, source niche Clara Tierra Madre Caviar 2x8, and source floor Cortar Charcoal 12x24 Soft with the original Soft-versus-Anti-Slip design discrepancy. No flat Bone appears in the quoted original wet-wall row; any flat Bone is a **separately evaluated wet-wall design option**, not in this packet's source wall quantity. Both original Bone Ribbed and Clara lack individual Wet Areas listed use (FAIL); point-drain pan/level exact DCOF FAIL. Actual floor area 35 SF owner versus prior 27 SF and separate shower-pan allocation unresolved. Dated source ELM 2026-09-03 prices material only, no approval."}
special={
"PH-PRIMARY":[
"- **Wet walls:** Flat Cortar Bone 24x48 Soft has maker Wet Areas application; specific Bone Reed 24x48 Relief proposed in the wet zone has no individual Wet Areas listing and FAILS. No derivative relief finish inherits flat Bone approval. Shower ceiling overhead substrate/attachment remains separately HOLD.",
"- **Level and linear pan:** Source floor row 2715002737917828 is Cortar Bone 24x48 Soft level plus Cortar Bone 12x24 Anti-Slip pan (not PF07). Neither exact finish has a raw measured wet DCOF certificate for its actual location (FAIL). A 12x24 large piece cannot be presumed to slope to selected 48-in Brizo linear, so actual pan design FAIL/HOLD independent of wet lab.",
"- **Source takeoff:** 143.0 SF gross wall+ceiling and ONE blended 135.6 SF gross floor (including PH WC 15 SF and linear pan), each already containing 15% waste. Historical 7.41-SF unpriced niche row is expressly EXCLUDED and cannot be added. Level/pan split needs real geometry; don't treat both as new orders.",
"- **Procurement and budget:** exact owner room material cap, current Chicago lot/rate/ETA, manufacturer original tile carton yield, actual trim LF, sample approval, drain membrane/slope and 1529 survey are null. No 125% pass/fail can be inferred; no purchase release."],
"PH-BATH2":[
"- **Actual wet tub wall:** Sapphire 2x20 Glossy individual maker Wet Areas **PASS** and Sandstone niche maker wet use evidenced; Grey Soft 12x24 bath-level floor exact SKU/finish raw measured wet DCOF **FAIL**. Wall approval does NOT substitute for the bath floor slip report.",
"- **Selected tub:** Duravit 700332000000090 and Hansgrohe **Matte White** fittings retained. This is a **TUB ALCOVE**, with no separate tiled shower pan, no selected Brizo 48-in linear drain and no invented linear slope/cut requirement. Verify tub flange, waterproof membrane and level-floor-to-tub/wood transition instead.",
"- **Correct takeoff:** source 89.7 SF gross walls, 3.67 SF gross Sandstone niche and 40.2 SF gross level floor already include 15% waste. Niche face displaces field face: actual opening, back/returns and sill must be measured ONCE rather than adding both full field and niche back without deduction.",
"- **Commercial HOLD:** original $623.42 wall + $271.35 floor + $25.51 niche = $920.28/unit only historical; no current Chicago quote, maker original grout/box yield, actual cut/trim LF or owner room cap. Current owner selection and all procurement null."],
"PH-BATH4":[
"- **Wet shower wall and niche:** proposed FULL Cortar Bone Ribbed 24x48 wet relief lacks product-specific Wet Areas listing, and Clara Caviar 2x8 niche lacks exact maker Wet Areas evidence. BOTH FAIL; flat Bone and Soho wet-listed properties do not transfer automatically into this relief/Caviar source option.",
"- **Actual selected POINT drain:** Brizo BT062415-BNX 4-in SQUARE tile-in Black Onyx drain with WALK-IN shower, not tub. Original source floor Cortar Charcoal 12x24 Soft has no exact raw measured wet DCOF for bath-level or sloped four-plane point-drain shower pan; required 2x2 compatible pan and selected waterproof assembly remain unverified. Do NOT reference a 48-in linear drain here.",
"- **Owner area and supplier finish conflict:** source 40.2 SF gross original floor with one 15% waste mathematically implies 34.96 SF net; this merely aligns with owner 35 SF, NOT actual confirmation against previous 27 SF. Original floor quoted Cortar Charcoal Soft versus intended Anti-Slip classification needs SKU/finish reconciliation; 40.2 SF source is pooled floor and actual pan split null.",
"- **Niche, cost and release:** original full Ribbed wall 107.2 SF gross and Clara niche 8.63 SF gross have no independently validated net field displacement, returns, grout, vertical trims or required four-plane pitch. Historic ELM source $790.06 wall + $271.35 floor + $290.83 accent = $1352.24/unit only; new stock, lot, lead, installed material budget and owner confirmation null."]}
market="Comp evidence: 14 listings/nine distinct buildings, Old Town OT01–OT05 preferred in previous 24 months; four sales OT01–OT04 at 405 W Armitage are ONE independent building precedent. Lincoln Park and Gold Coast secondary. PH buyer target $2.8M, TX $2.7M, $2.4M–$3.2M comparator. Listing copy provides amenity categories only, not verified actual tile format/colors or floor tests."
for rid,letter in paths.items():
 p=R/"rooms"/rid/"board/round-010/candidates"/(letter+".md")
 lines=p.read_text(encoding="utf-8").splitlines()
 assert len(lines)>=42 and lines[2].startswith("This specification is a design option")
 assert lines[4].startswith("## Exact historical material/")
 lines[4]="## Room finish, plumbing, material and technical comparison"
 lines[6]=newopening[rid]
 lines[8]=lines[8].replace("Surface / original source row","Surface / source row").replace("Historical gross SF","Source gross SF").replace("Original actual historic material USD","Dated ELM source material USD")
 for i,z in enumerate(lines):
  if z.startswith("| ") and " | historical " in z:
   lines[i]=z.replace(" | historical "," | ELM 2026-09-03 ").replace(" EXCLUDED HISTORICAL NO NICHE"," EXCLUDED non-orderable Primary niche")
  if z.startswith("| W") and "horizontal tub tile or vertical primary flat" in z:
   phrase={"PH-PRIMARY":"vertical flat/relief Bone panels, wet relief listing FAIL",
   "PH-BATH2":"horizontal stacked Sapphire 2x20 on tub walls, no tiled pan",
   "PH-BATH4":"full-height 24x48 Bone Ribbed wet panels, product-specific wet FAIL"}[rid]
   lines[i]=z.replace("horizontal tub tile or vertical primary flat",phrase)
 start=next(i for i,z in enumerate(lines) if z.startswith("## Test and manufacture evidence"))
 end=next(i for i,z in enumerate(lines) if z.startswith("## Independent market"))
 lines[start+2:end]=special[rid]+[""]
 mi=next(i for i,z in enumerate(lines) if z.startswith("Comp evidence:"))
 lines[mi]=market
 oi=next(i for i,z in enumerate(lines) if z.startswith("Owner decision remains null."))
 part={"PH-PRIMARY":"Selected existing Brizo Black Onyx 48-in linear and separate white Duravit tub in sample view; NO niche. Mock-up flat/relief comparison must show unapproved relief wet listing as HOLD and full floor/pan section; unverified wall openings, actual drains and trim dashed.",
 "PH-BATH2":"Existing Matte White Hansgrohe with Duravit tub, Sapphire wet wall and Sandstone niche in sample panel; no Black Onyx or invented pan. Draw tub flange/niche back/returns and tile-to-wood threshold with unknown dimensions dashed.",
 "PH-BATH4":"Existing Brizo Black Onyx shower with four-inch square point drain; full Bone Ribbed wet wall/Caviar niche source finish as unapproved evidence, no tub. Draw four-plane point-drain waterproof section and exact shower opening/trim withheld pending verified 1529 source."}[rid]
 lines[oi]="Owner color/sample and project room budget remain null. "+part
 p.write_text("\n".join(lines)+"\n",encoding="utf-8")
 print(rid,letter,p.stat().st_size)
print("PASS R010 three old-source candidates room-specific, no prior-role prefaces, correct wet/pan fixtures; SHA refresh still required")

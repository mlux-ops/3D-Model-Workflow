"""Resolve non-Pro Reviewer R004 factual and blind symmetry issues; refresh fingerprints."""
from pathlib import Path
import hashlib,json

R=Path(__file__).resolve().parents[1]
receipt=R/"state/ROUND004_SUBMISSION.json"
d=json.loads(receipt.read_text(encoding="utf-8"))

def fix(room,letter,replacements):
 p=R/"rooms"/room/"board/round-004/candidates"/(letter+".md")
 text=p.read_text(encoding="utf-8")
 for old,new in replacements:
  if old in text:
   text=text.replace(old,new)
  else:
   assert new in text,(room,letter,"missing target",old[:85])
 p.write_text(text,encoding="utf-8")

fix("PH-PRIMARY","A",[
 ("Historic whole blended floor amount ≈ **$1,060.29/unit** (104.32×8.14+31.28×6.75), **not a v4 all-Anti-Slip bid**.",
  "Actual carried historical floor quote is **135.6 SF × $7.82 = $1,060.39/unit**. A **separately inferred, UNVERIFIED** split of 104.32 SF×$8.14 + 31.28 SF×$6.75 is **$1,060.3048 unrounded / $1,060.30 rounded**, $0.09 below the carried quote. It is **NOT** independently quoted format pricing or a v4 all-Anti-Slip bid."),
 ("The original ELM reference totals $1,164.02 walls+ceiling and ≈$1,060.29 floor",
  "the carried ELM reference totals $1,164.02 walls+ceiling and $1,060.39 blended floor")
])
fix("PH-BATH2","B",[
 ("keep the approved **Tones Sandstone** niche within measured wall field.",
  "retain the **manufacturer-wet-listed, historically quoted Tones Sandstone** niche provisionally inside the tub wall field."),
 ("**$252.05/SF-rate basis** before whole cartons, freight and trim.",
  "**$252.05/unit illustrative cost at the public $6.27/SF area rate** before whole cartons, freight and trim; PH project quote null."),
 ("Round001 lessons from other PH rooms favor one deliberate accent and a clearly documented edge/cut datum, not guessed quantities.",
  "The proposed layout uses one deliberate accent and a source-coordinate-dependent edge/cut datum, not guessed niche or wall quantities.")
])
fix("PH-BATH3","C",[
 ("The alternative 86.2+8.63=94.83 SF /$659.07 is only an unverified non-netted upper scenario; neither is a confirmed purchase quantity.",
  "The HISTORIC QUOTED TWO-LINE gross allowance is **86.2+8.63=94.83 SF**, extended **$599.09+$59.98=$659.07** at the carried rates. The proposed **netted 86.20 SF / $599.09** is a *conditional field-overlap assumption*, NOT the historical quote or an approved savings. Neither figure is a confirmed purchasable takeoff.")
])
fix("PH-BATH4","B",[
 ("Round001 critics specifically required a measured 24×48 elevation, confirmed nook cuts, usable small-format point-drain strategy and pricing.",
  "The installation package still requires a measured 24×48 elevation, confirmed niche cuts, a small-format point-drain pan section and actual pricing.")
])

room_extra={
"PH-PRIMARY":"""## Cross-checked maker and fixture evidence for this complete scheme

The individual [flat Cortar Bone product evidence](../../../../../research/products/elm-cortar-bone-flat-24x48.md) records Wet Areas for flat Soft only. The separate [Bone Reed relief evidence](../../../../../research/products/elm-cortar-bone-reed-wet-hold.md) records **Walls/Back Splashes without Wet Areas** for dimensional Reed; do not transfer the flat rating. The source's Bone Soft/Anti-Slip floor line has **no published exact measured wet DCOF**, regardless of whether the drawing calls Anti-Slip across the full floor or the 2026-09-03 blended quote separates level field and pan. [Daltile's explicit target-versus-measured comparison](../../../../../research/products/daltile-portfolio-cream-pf07-12x24-matte.md) supplies a competing test threshold context, not approval of original Bone.

### Preliminary 1529 room-size / buildable elevation

The [geometry record](../../../geometry.json) has W1 **5.854 ft = 70.25 in**, W2 **4.646 ft = 55.75 in**, both assumed **9.25 ft / 111 in** tiled to ceiling. W1 is ~54.15 SF net, W2 ~42.98 SF net, assumed shower ceiling ~27.20 SF net; sum ~124.33 SF net and **143.0 SF with the source 15% allowance** before openings. Do NOT add a distinct ceiling line to the full wall-and-ceiling quote. An aligned 24x48 grid avoids assumed running-bond lippage but still requires true 1529 walls, overhead attachment approval, edges and full Brizo escutcheon/ceiling-arm cut templates. The selected 48-inch **Brizo BT0734816-BNX / BR73480** linear drain is real in [plumbing](../../../plumbing.json); its actual wall, finished elevation, slope, threshold and waterproofing must precede any proposed 12x24 shower-pan cut scheme. A 12x24 tile is not proven fit to a multi-plane fall.

### Material economy and wet-room release checkpoints

The historical materials comprise 143.0 SF wall+ceiling **$1,164.02/unit** and 135.6 SF quoted level+pan+WC **$1,060.39/unit**. Any Reed element is a **within-field** unmeasured allocation, not an extra invoice line; the original unpriced 7.41-SF niche record is **explicitly OUT OF SCOPE**. Gross tiles include 15% waste and WC floor area. Source quote does not include carton procurement, waterproof membrane, setting mortar, grout, profiles, tax/freight or labor, and cannot establish a 125% budget violation without an owner room cap. Current **Chicago lot/ETA is null**; historic ELM imported collection notes are not a current promise. Old Town [OT01–OT05](../../../../../research/comps/COMPS.md) substantiate premium primary tub/shower/dual vanity *program* only, not Bone color or dimensional relief. Final sample and cutting review must hold the selected Black Onyx fixtures and no-primary-niche decision.
""",
"PH-BATH2":"""## Independent source evidence and layout risk register

The source [PH Bath2 geometry](../../../geometry.json) provides a provisional **4.958-ft / 59.50-in tub back wall** plus two **2.55-ft / 30.60-in returns**, each assumed **7.75-ft / 93-in tiled above tub deck**. This yields approximately **77.95 SF net / 89.7 SF gross with 15% already embedded**. A full-size centered 2x20 wall field must coordinate fixture openings, corner joints, 1/3-style offset where appropriate to actual long pieces and the 59-inch Duravit tub; actual rough and niches remain unlocated. This 2x20 layout is not proven by the provisional old wall dimensions. The **Sandstone provisional 3.67-SF niche** is an overlapping *face allocation* rather than a verified additional dimensioned recess; do not invoice 89.7+3.67 SF without backing, jamb, shelf and field deductions.

The selected [plumbing record](../../../plumbing.json) includes **Duravit 700332000000090**, **Hansgrohe Matte White** Ecostat 15758701, Rainfinity 26866701 and Vivenis 75033701. The historical 04186703 matte-white arm carries a possible channel-discontinuation note; do not substitute silently, distinguish channel inventory from confirmed manufacturer end-of-life. For the source Tones Sapphire wet wall, a product-specific **Wet Areas** listing is not established in reviewed evidence; being a ceramic Walls product is insufficient in this tub enclosure. The separately documented [Tones Sandstone](../../../../../research/products/elm-tones-sandstone-2x20.md) Wet Areas listing applies to Sandstone only. Same-project rates do not establish wet approval or a refreshed quote.

The carried Cortar Grey **12x24 Soft** floor line is **40.2 SF gross at $6.75/SF = $271.35/unit**, but exact format/finish measured wet DCOF remains **null** and therefore FAIL. A floor-product name does not supply a wet-slip test. The owner has not allocated a PH Bath2 room budget and the 125%-threshold cannot be calculated. Existing quote **$920.28/unit** adds wall/floor/niche source gross extensions; true wall/niche overlap could change net ordering. Chicago stock/lead, cartons and installed edge/grout/labor remain unverified. [OT01–OT04](../../../../../research/comps/COMPS.md) market secondary wet-room amenities, not Sapphire appearance or individual metal finishes. Control only one niche accent, provide matte-white sample chip and precise grout/profile/threshold layout before construction.
""",
"PH-BATH3":"""## Exact product-use, historic quote and construction review

The historic wet tub field names Tones **Opal 2x20 Glossy**; **exact Opal Wet Areas listing was not found** and must be treated as FAIL in a tub/wet wall pending manufacturer proof, even if the project has an old quote. The separately [Wet Areas-listed Tones Sandstone](../../../../../research/products/elm-tones-sandstone-2x20.md) is shown for the existing niche; its manufacturer approval does **not** transfer to Opal. The proposed replacement composition is a separate alternative, not an implied owner choice. The old full [geometry](../../../geometry.json) is W1 **5.00 ft / 60 in**, returns W2/W3 **2.33 ft / 27.96 in**, tiled **7.75 ft / 93 in** above tub rim, gross source wall **86.2 SF**. The tub back nominal 60-inch width needs a balanced 20-inch course rather than an assumed no-cut fit once grout, actual size and niche penetrations are considered.

The [plumbing source](../../../plumbing.json) includes **Hansgrohe Chrome** shower head 04925000, valve trim 15758001 and a **Delta DT062412 4-in Chrome square tile-in shower drain**; source geometry names a tub alcove. These are conflicting program/rough evidence. Do not add a pan, remove a tub, select a basin or transfer a point-drain SKU to the tub without owner/model clarification. A sink/basin is marked **unselected** in this room. A credible section needs tub-flange waterproofing if tub governs; if a walk-in shower governs, wet wall heights and a newly measured pan, drain offset and small-format mosaic test are mandatory.

Source quote is **86.2 SF Opal wall at $6.95/SF = $599.09**, **8.63 SF Sandstone niche at $6.95/SF = $59.98**, and **40.2 SF Cortar Bone Soft floor at $6.75/SF = $271.35**: carried total **$930.42/unit**. Historic recorded **94.83 SF combined wall+niche gross** is NOT evidence that the niche does or does not overlap the field; deduct measured face when actual opening/back/returns are confirmed. The Bone Soft floor has exact measured wet DCOF **null**. Current Chicago SKU-specific lot/ETA, cartons, grout/edge, waterproofing, installation price and owner cap are null. [OT01–OT05](../../../../../research/comps/COMPS.md) confirm bath program quality, not an Opal tile buyer precedent.
""",
"PH-BATH4":"""## Source product compliance and finish-interface schedule

The [Cortar Bone Ribbed relief evidence](../../../../../research/products/elm-cortar-bone-ribbed-24x48-relief.md) lists Walls/Back Splashes, **no Wet Areas** for its wet enclosure application. The [flat Bone 24x48 evidence](../../../../../research/products/elm-cortar-bone-flat-24x48.md) has a **distinct** Wet Areas listing, which is not transferable to Ribbed. The current historic niche names Clara Tierra Madre **Caviar 2x8** and lacks Wet Areas listing for its shower niche; $33.70/SF project price cannot certify application. A separately [Wet Areas-listed Soho Black 2x10](../../../../../research/products/elm-soho-black-2x10.md) could be studied only as a **future substitution**, not a historic selected owner fixture. This source scheme therefore fails wet-wall/niche gate independent of its board score.

The source [geometry](../../../geometry.json) records a **5.00-ft / 60-in back wall**, **two 2.54-ft / 30.48-in returns** and **9.25-ft / 111-in tiled height** in a **walk-in shower**, gross source wet-wall **107.2 SF** with 15% waste. Critically, **owner-overridden bathroom floor 35 SF conflicts with older Revit-derived 27 SF** and the exact extent of the assumed shower footprint 5.00x2.54 is not live verified. Full wall tile and niche are not two full independent surfaces; field-to-recess deduction and jamb/shelf/returns must be calculated once. Large-format 24x48 requires flatness, centered cuts at actual trim, waterproofing and mortar suitability rather than an assumed no-sliver fit.

The [plumbing schedule](../../../plumbing.json) retains **Brizo BT062415-BNX 4-in square tile-in drain in Brilliance Black Onyx**, shower head 81392-BNX-2.5 and valve T755110-BNXLHP; do not replace point drain with a linear drain. A center/offset point drain ordinarily requires a four-plane sloped pan, for which the source **12x24 Cortar Charcoal Soft** quote is not a proven small-format pan design. The original v4 tile calls **Anti-Slip**, the quote calls **Soft**, and neither provides a published exact numeric wet DCOF result. Historic **107.2 SF Ribbed $790.06, 40.2 SF Soft floor $271.35, 8.63 SF Caviar $290.83** = **$1,352.24/unit** before overlap and unquoted installation. The two-unit old import minimum/lead is not verified as current 2026 stock; source budget allocation absent. [OT01–OT04](../../../../../research/comps/COMPS.md) support upgraded secondary wet-room program, not dimensional Ribbed/Clara colors.
"""
}

for room,letter in {"PH-PRIMARY":"C","PH-BATH2":"A","PH-BATH3":"B","PH-BATH4":"A"}.items():
 p=R/"rooms"/room/"board/round-004/candidates"/(letter+".md")
 text=p.read_text(encoding="utf-8")
 if room_extra[room].splitlines()[0] not in text:
  text=text.rstrip()+"\n\n"+room_extra[room].strip()+"\n"
  p.write_text(text,encoding="utf-8")

for room,leters in {"PH-PRIMARY":"AC","PH-BATH2":"AB","PH-BATH3":"BC","PH-BATH4":"AB"}.items():
 for letter in leters:
  p=R/"rooms"/room/"board/round-004/candidates"/(letter+".md")
  text=p.read_text(encoding="utf-8")
  lines=text.splitlines()
  assert lines[2]=="**Round 004 / per Penthouse unit; two units.** This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified."
  assert "Round001 critics" not in text and "Round001 lessons" not in text
  assert "actual challenger" not in text.lower() and "incumbent" not in text.lower()
  for m in __import__('re').findall(r"\]\(([^)]+)\)",text):
   if m.startswith(("https://","http://","mailto:")):continue
   assert (p.parent/m.split("#")[0]).resolve().exists(),(room,letter,m)
  d["candidate_files"][room][letter]={"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":len(p.read_bytes())}
  print(room,letter,len(p.read_bytes()))
receipt.write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8")
print("PASS: fixed source quote, owner language and eight equalized blind packets")

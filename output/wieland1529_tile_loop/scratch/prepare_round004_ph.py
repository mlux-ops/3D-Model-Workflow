"""Source-grounded four-room PH historical packets; no scores or approvals."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
state=json.loads((ROOT/"state/ROOMS.json").read_text(encoding="utf-8"))
rooms={r["id"]:r for r in state["rooms"]}
SCHEMES={
 "PH-PRIMARY":("C","Bone Soft plus Reed and historic two-format floor",[
  ("Wet shower wall and ceiling","ELM Cortar Bone 24×48 Soft; flat wet-listed product","wall","Wall and ceiling 143 SF gross includes prior 15% waste. 24×48 0-offset layout, verify substrate flatness, shower controls and ceiling attachment.","Flat Bone wet-area listing supported; adjoining Bone Reed's Wet Areas listing absent"),
  ("Shower wall relief panel","ELM Cortar Bone Reed 24×48 Relief","", "Unquantified share within the 143 SF wall/ceiling envelope; no added tile allowance or priced amount.","Wet-wall listing for exact Reed finish unverified; FAIL if in shower"),
  ("Bathroom level floor / shower pan / WC allowance","ELM Cortar Bone 24×48 Anti-Slip v4; existing ELM quote instead describes blended 24×48 Soft level floor + 12×24 Anti-Slip shower pan","floor","Quote 135.6 SF gross, includes WC allowance and 15% waste. Shower linear Brizo rough/trim listed; drain location and slope unknown.","Numeric exact wet DCOF for all relevant floor variants null => FAIL; v4 finish conflicts with blended quote"),
  ("Primary niche","No scheduled niche tile or selected extra accent","accent","Historical unpriced niche row is expressly excluded per 2026-10-01 project correction.","NO primary niche; no quantity or extra cost")
 ]),
 "PH-BATH2":("A","Sapphire/grey tub surround and Sandstone niche",[
  ("Tub surround","ELM Tones Sapphire 2×20 Glossy stacked; maker listing requires exact product confirmation","wall","Prior W1 back 4.958 ft, W2/W3 returns 2.55 ft, tiled 7.75 ft above tub deck; field 89.7 SF gross including 15% waste.","Wet Areas for Sapphire exact product not established in this packet; fail pending product-specific listing"),
  ("Level bathroom floor","ELM Cortar Grey 12×24 Soft","floor","40.2 SF gross with 15% waste, 0-offset centered nominal grid, threshold and edge elevations unknown.","Exact published wet DCOF >=0.42 missing => FAIL"),
  ("Recess accent","ELM Tones Sandstone 2×20 Glossy, niche","accent","3.67 SF provisional gross including 15% waste. Verify niche recess/opening returns, trim and deduct from field, never double count.","Manufacturer Wet Areas listed for Sandstone, substrate and sill fall TBD")
 ]),
 "PH-BATH3":("B","Opal/Sandstone tub surround and Bone floor",[
  ("Tub surround","ELM Tones Opal 2×20 Glossy","wall","Prior 5.0 ft back, 2.33 ft returns, tiled 7.75 ft above tub deck; 86.2 SF gross with 15% waste.","Exact Opal Wet Areas approval unavailable => FAIL for tub walls"),
  ("Level bathroom floor","ELM Cortar Bone 12×24 Soft","floor","40.2 SF gross with 15% waste; bath floor only, no inferred sloped pan.","Exact wet DCOF >=0.42 unverified => FAIL"),
  ("Tub niche","ELM Tones Sandstone 2×20 Glossy","accent","8.63 SF estimated gross, must deduct corresponding field face; sink remains owner-unselected.","Sandstone listed Wet Areas; unknown recess returns and sill.")
 ]),
 "PH-BATH4":("A","Bone Ribbed/Clara Caviar wet enclosure, Charcoal floor",[
  ("Full shower wall","ELM Cortar Bone Ribbed 24×48 Relief","wall","107.2 SF gross including 15% waste; W1 5.0 ft W2/W3 2.54 ft, 9.25 ft height prior drawings.","Exact Ribbed Wet Areas approval absent => FAIL for shower walls"),
  ("Bathroom floor and shower pan","ELM Cortar Charcoal 12×24 Anti-Slip v4; quoted Cortar Charcoal 12×24 Soft differs","floor","40.2 SF gross with 15% waste, no actual point-drain pan split; geometry records 35 SF owner area vs 27 SF earlier model takeoff.","Exact wet DCOF missing => FAIL; 12×24 needs geometric slope proof at 4-in point drain; Soft/Anti-Slip source conflict"),
  ("Wet shower niche","ELM Clara Tierra Madre Caviar 2×8 zellige","accent","8.63 SF gross provisional; niche displaces rather than augments Bone field; recess/sill unmeasured.","Clara Caviar product-specific Wet Areas listing absent => FAIL")
 ])
}
for rid,(letter,title,rows) in SCHEMES.items():
 room=rooms[rid]
 target=ROOT/"rooms"/rid/"board/round-004/candidates"
 target.mkdir(parents=True,exist_ok=True)
 file=target/(letter+".md")
 assert not file.exists(), file
 lines=["# "+rid+" — Candidate "+letter+" — "+title,"",
  "**Round 004 / per Penthouse unit; two units.** This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.","",
  "| Surface | Product / size / finish | Installation and geometry | Historical per-unit cost and quantity | Evidence and hard gate |",
  "|---|---|---|---|---|"]
 for surface,product,kind,layout,gate in rows:
  cost="No added SKU/quantity; unpriced history"
  if kind:
   r=next((r for r in room["carried_tile_rows"] if r["surface"]==kind),None)
   if r:
    q=r["qty_sf_per_unit"]; price=r["quoted_rate_usd_per_sf"]; ext=r["extended_quote_cost_usd_per_unit"]
    cost=f"Carried **{q} SF/unit** incl. 15% waste; "
    cost+=f"**${price:.2f}/SF**, **${ext:,.2f}/unit**" if price is not None and ext is not None else "rate/extended cost **null**"
    cost+=f"; Smartsheet row `{r['smartsheet_row_id']}`"
  lines.append("| "+" | ".join([surface,product,layout,cost,gate])+" |")
 lines.extend(["","## Evidence, compatibility and procurement",
  "- Verified current building model: **NO**. Drawing-derived `geometry.json` dimensions are provisional and cannot be represented as the measured 1529 building; the open model is named 1527 Wieland. No model, floor type, fixture or owner input was changed.",
  f"- Existing carried tile-only historical subtotal **${room['carried_quote_material_subtotal_usd_per_unit']:,.2f}/unit** from ELM September 3, 2026, and Smartsheet snapshot November 6, 2026; **not** a room budget, supplier reconfirmation or installed cost.",
  "- Materials are specified for two PH units. Rates exclude final cartons/attic stock, field-to-niche netting, mortar, substrate flatness, waterproof membrane, accessories, grout, trim, freight, tax, labor, current Chicago lot and ETA (all `null`). The 15% waste already exists in carried quantity.",
  "- Manufacturer application listings are finish/format-specific; collection-level Floors/Walls alone cannot substitute Wet Areas for wet wall, and Daltile 'Target DCOF Wet >=0.42' does not supply a tested exact-finish numeric floor value. Do not treat a fail as release-ready.",
  "- Compare against 14 Old Town-focused comparable listings from nine buildings in `research/comps/COMPS.md`; Old Town evidence relates to premium bath program, not verified visual tile duplicates. PH target **$2.8M** in owner feedback, comp range **$2.4–$3.2M**.",
  "- Source: room `geometry.json` / `plumbing.json`, governing v4 handoff and fixture deck, `state/ROOMS.json` quote snapshot, `research/products/`. No owner approval or selection inferred."])
 file.write_text("\n".join(lines)+"\n",encoding="utf-8")
 print(rid,letter,len(file.read_bytes()))

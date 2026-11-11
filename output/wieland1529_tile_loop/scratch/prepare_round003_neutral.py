"""Source-grounded Round003 neutral incumbents; no selection or score."""
from pathlib import Path
import json

R=Path(__file__).resolve().parents[1]
state=json.loads((R/"state/ROOMS.json").read_text(encoding="utf-8"))
rooms={x["id"]:x for x in state["rooms"]}
specs={
 "TX-PRIMARY": ("A", "Clay flat, relief panel and two-format floor", [
  ("Full-height shower walls and shower ceiling","ELM Cortar Clay 24×48 Soft, WT3","Flat porcelain. Straight vertical aligned panels, 0 offset; grout, trims, drain/valve penetrations and waterproof system require measured elevations","wall", "Manufacturer lists Wet Areas for **flat Clay**; dimensional **Clay Ribbed WT4** is a separate product with no proven Wet Areas approval"),
  ("Dimensional accent within wall field","ELM Cortar Clay Ribbed 24×48 relief, WT4","Actual wet-versus-dry location, area, cut grid and backplate landing **null**; never add an extra field area",None,"**FAIL** if applied in shower wet zone without product-specific Wet Areas documentation"),
  ("Bathroom level floor, shower pan and TX WC shared area","ELM Cortar Clay 24×48 Soft field and 12×24 Anti-Slip shower-pan portion, FT2","Blended quote is not a single finish; point/linear drain type, pan slope/geometry, tile division and actual format compatibility **unverified**","floor","**FAIL** exact published wet DCOF ≥0.42 missing for actual field and pan finish; manufacturer usage alone does not certify numeric slip resistance"),
  ("Shower niches","No extra selected niche tile or added niche design","The historical Smartsheet 8.63-SF niche line has no priced SKU and is **expressly excluded** from governing primary-bath scope",None,"Do not invent or price niche tile")
 ]),
 "TX-POWDER": ("C","Camel and Wheat dry-wall feature",[
  ("Dry vanity feature wall","ELM Haze Camel + Wheat 1.6×5 Matte, WT12","Stacked two-color composition. Color ratio, joint orientation and actual pattern to be locked at physical sample. Base, mirror and wall-mount faucet landing TBD","vanity_wall","Manufacturer Haze series lists Walls, not a floor/shower wet area. **Dry wall use only**; no wet-floor DCOF required"),
  ("Powder floor and other walls","Wood floor (existing scope), painted/dry walls","No separate tile floor or new wet enclosure; edge transition to vanity tile TBD",None,"Wet-floor DCOF gate inapplicable")
 ]),
 "TX-POWDER2": ("C","Indigo Edge relief dry-wall feature",[
  ("Dry vanity feature wall","ELM Vera Forma Indigo Edge 6×6 Glossy Relief, WT13","Full-height feature wall, grout/joint width, module balance and flat landing at selected Hansgrohe Tecturis E 73072341 Brushed Black Chrome faucet or mirror mount TBD","vanity_wall","Manufacturer wall-only listing; dry bathroom vanity feature, **not a shower wet wall**"),
  ("Powder floor and remaining surfaces","Existing wood flooring; no separate tile","Keep owner unselected sink unspecified, verify mirror/backsplash, cut and termination from actual elevation",None,"No tile wet-floor DCOF gate")
 ])
}
for rid,(letter,title,surfaces) in specs.items():
 room=rooms[rid]
 folder=R/"rooms"/rid/"board/round-003/candidates"
 folder.mkdir(parents=True,exist_ok=True)
 path=folder/(letter+".md")
 assert not path.exists(),str(path)
 lines=[f"# {rid} — Candidate {letter} — {title}","","**Round 003 / per Triplex unit; two units.** This is a complete design option evaluated against source selections and supplier history. Its technical viability, any substitution, current supplier acceptance and owner approval remain unconfirmed.","",
        "| Surface | Product / format / finish | Layout and construction detail | Gross quantity / historical supplier rate | Hard-gate status |",
        "|---|---|---|---|---|"]
 for surface,prod,layout,ratekey,gate in surfaces:
  if ratekey:
   row=next(x for x in room["carried_tile_rows"] if x["surface"]==ratekey)
   rate=row["quoted_rate_usd_per_sf"]
   money="rate **null**" if rate is None else f"**${rate:.2f}/SF**"
   quote=f"**{row['qty_sf_per_unit']} SF/unit** with carried 15% waste × {money} = **${row['extended_quote_cost_usd_per_unit']:,.2f}/unit**" if row["extended_quote_cost_usd_per_unit"] is not None else f"**{row['qty_sf_per_unit']} SF/unit** historical row only, unpriced"
   quote+=f"; Smartsheet row `{row['smartsheet_row_id']}`, historical 2026-09-03 ELM quote"
  else:quote="Area/rate **null**, no additional scoped tile allowance"
  lines.append("| "+ " | ".join((surface,prod,layout,quote,gate))+" |")
 lines+=["","## Product, procurement and actual geometry checks",
         f"- Prior room area: **{room['floor_area_sf_prior']} SF**, live model geometry still **unverified for 1529**. The current open Revit project is named 1527; owner permits only provisional reads if room/unit match is proven. Door, openings, rough heights and niche locations are unmeasured.",
         "- ELM project quote is dated **2026-09-03**; Smartsheet snapshot reviewed 2026-11-06. Manufacturer availability, exact Chicago inventory, delivery date, lot and full installation pricing are **null**. Carried material subtotal is not an approved room budget.",
         "- Prior quantity already includes **15% waste**. Carton rounding, setting labor, waterproofing (where applicable), trim, freight, grout, taxes and niche/field netting are not priced. Never double-count dry wall or shower-pan tile.",
         "- Sources: `geometry.json` and `plumbing.json` of this room, original v4 tile handoff, saved Smartsheet tile export, `research/products/`, `research/comps/` and public manufacturer product records.",
         "- Old Town comp text is the prioritized program/buyer baseline; 14 listings in nine building groups. Adjacent Lincoln Park/Gold Coast are flagged secondary; no authenticated competitor bath tile photos. No unverified tile format/color trend is asserted.",
         "- **Owner-only decisions:** product substitutions, exact wet floor approval, missing sink/basin selection (where applicable) and room upgrade budget. No fixture selected or order placed."]
 if rid=="TX-PRIMARY":
  lines+=["- Plumbing lists Brizo Black Onyx and a **48-in linear drain rough-in BR73480**; the quoted blended 24×48 Soft plus 12×24 Anti-Slip shower pan still has no geometry-verified slope/cut drawing. WT4 Ribbed is not approved for the wet shower. The 8.63-SF historical niche row is **excluded** per controlling 2026-10-01 correction. Exact room finish split **null**."]
 if rid=="TX-POWDER":
  lines+=["- Source wall length **2.99 ft × 9.25 ft ≈ 27.66 SF net**, versus carried **31.8 SF gross** with 15% waste, rounding/returns unverified. Exact Camel/Wheat color ratio, wall faucet penetration and trim require actual samples."]
 if rid=="TX-POWDER2":
  lines+=["- Source feature wall **3.806 ft × 9.25 ft ≈ 35.21 SF net**, carried **40.5 SF gross** with 15% waste, opening deductions unverified. Hansgrohe Tecturis E Brushed Black Chrome 73072341 is the carried faucet; **sink model is unselected**, and drain finish must be reconciled with plumbing notes before installation."]
 path.write_text("\n".join(lines)+"\n",encoding="utf-8")
 print(rid,letter,str(path.relative_to(R)),len(path.read_bytes()))

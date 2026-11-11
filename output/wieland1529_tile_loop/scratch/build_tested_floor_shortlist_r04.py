"""Floor/pan source-quantity allocation and test-backed speculative alternate index."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
rooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
dest=R/'deliverables/integrated-r04/TESTED_FLOOR_CANDIDATE_SHORTLIST_R04.md'
lines=['# Wet-floor test-backed alternatives and room-by-room takeoff gate — R04','',
 '## The new evidence lead versus the existing conditional floor sketches','',
 '**Manufacturer product-specific reported performance exists** for Glazzio Harmonic Rondo DCOF Matte, 12x24 level-floor **SKU HNC6615** and 2x2 Hex shower mosaic **SKU HNC6715**; exact individual pages each report **DCOF WET >0.50**. This differs from the Daltile Portfolio PF07/PF05/PF09 application table **Target DCOF Wet ≥0.42**, which is an intended-use target and does not provide an exact format-specific measured performance result.',
 'The **actual raw certified AcuTest numeric point result/test certificate** for Glazzio is not published in the reviewed HTML, and the maker’s >0.50 is a lower bound rather than a disclosed measured point. Classify as **promising SKU-specific reported test; formal laboratory verification held**, not an automatically released construction selection. Both performance, exact finish/color, price, Chicago lot/ETA, current available cases and owner approval must be reviewed before changing the existing round results.',
 'Proof: research/products/glazzio-harmonic-rondo-hnc6615-12x24-dcof-matte.md and glazzio-harmonic-rondo-hnc6715-2x2-hex-dcof-matte.md; each links to the exact maker product page. HNC6715 is explicitly Shower Floor YES; HNC6615 is proposed only on level floor and has 9.69 SF/box. HNC6715 is 4.85 SF/box, **not** part of original ELM quotes.',
 '',
 '| Room | Floor quote gross SF per unit including 15% waste | Wet program | Existing selection issues | Tested-claim alternative investigation | Quantity and pricing guardrails |',
 '|---|---:|---|---|---|---|']
for r in rooms:
 rid=r['id']
 floor=next((x for x in r['carried_tile_rows'] if x['surface']=='floor'),None)
 if not floor:
  if rid.endswith('-WC'):
   lines.append('| {} | 0 additional quoted | WC dry/level floor shared with Primary | No new row or double ordering | Copy primary confirmed level-floor SKU only after owner scope signoff | Unit quote is INCLUDED in primary floor line |'.format(rid))
  elif 'POWDER' in rid:
   lines.append('| {} | No tile floor | Existing wood | No tiled floor DCOF rule | **No proposed tile**, wood scope unchanged | Zero tile floor cost |'.format(rid))
  continue
 description=floor['carried_description']
 rate=floor['quoted_rate_usd_per_sf']
 ext=floor['extended_quote_cost_usd_per_unit']
 gross=floor['qty_sf_per_unit']
 if 'PRIMARY' in rid:
  prog='48in Brizo linear-drain shower; main bath/WC level field'
  issue='Original v4 versus blended supplier Soft/Anti-Slip floor; no exact DCOF'
  alt='HNC6615 12x24 level + HNC6715 2x2 mosaic pan (conditional)'
  note='Pan gross split from historic note, drain position and pitch unverified; no primary niche'
 elif rid=='PH-BATH4':
  prog='4in Brizo Black Onyx square point drain'
  issue='Charcoal Soft quote versus Anti-Slip v4, owner 35 SF versus historic 27 SF'
  alt='HNC6615 level + HNC6715 2x2 point-drain pan concept'
  note='If 35 SF total includes 12.70 SF wet pan, gross split ~25.6/14.6; tentative only'
 elif rid=='TX-BATH3':
  prog='4in Brizo square point drain in plumbing, tub in tile handoff'
  issue='Unresolved tub versus walk-in, no shower pan SF/price'
  alt='HNC6615 level, HNC6715 pan ONLY if walk-in program confirmed'
  note='Pan SF null; prohibit inferring from source tub footprint'
 elif rid=='PH-BATH3':
  prog='Tub alcove in tile handoff, Delta 4in square drain in selected plumbing'
  issue='Tub versus listed drain confirmation and owner basin needed'
  alt='HNC6615 12x24 level; HNC6715 pan only if shower confirmed'
  note='No extra pan quantity until real program and dimensions'
 else:
  prog='Tub surround with separate level bath floor'
  issue='Exact published wet floor DCOF absent for carried ELM Soft'
  alt='HNC6615 12x24 level floor only; no added pan for tub'
  note='Area already includes 15% waste, box rounding must be separate'
 lines.append('| {} | {} | {} | {} | {} | {} |'.format(rid,gross,prog,issue,alt,note))
lines+=['',
 '## Compare project scope before approving product material change','',
 '- **SKU performance:** Exact Glazzio maker page reports the >0.50 tested bound for each SKU. Request underlying ANSI A326.3 report before interpreting it as an exact measured finish and to satisfy the project strict acceptance language; do not backfill the published bounds as an invented point value.',
 '- **Maker suitability:** 12x24 level and 2x2 hex Shower Floors must remain separately approved, with pitch/curb/drain geometry confirmed. Actual 2x2 hex nominal geometry, grout and installed pattern may differ from the current PF07/PF05/PF09 straight-joint square mosaics; cannot swap without new layout drawing.',
 '- **Color/market:** New Rondo palette requires actual color, material transparency and grout inspection with each room’s carried Black Onyx/Matte White/Chrome metals. Old Town marketing sources prove only bath program, not matching Rondo tile.',
 '- **Money and availability:** No Glazzio project quote, installed labor, Chicago stock or lead. Existing ELM/Daltile rates are not transferable; room caps null. Floor alteration may require cost and separate threshold approval rather than assuming the tested product fits existing budget.',
 '- **Freeze protection:** Submitted Round004 eight blind candidates and prior Round001–003 score/acceptance history are unchanged. This document is a future independent research pool only; it cannot rescue a candidate or override a failed board gate retroactively.']
dest.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('PASS source-based floor candidate shortlist',len(lines),'lines')

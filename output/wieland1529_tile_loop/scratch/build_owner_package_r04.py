"""Build 13-room source-grounded owner package; no external/procurement writes."""
from pathlib import Path
import csv,json

root=Path(__file__).resolve().parents[1]
rooms=json.loads((root/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
dest=root/'deliverables'/'integrated-r04'
dest.mkdir(parents=True,exist_ok=True)
better={
 'PH-PRIMARY':'Flat Cortar Bone wet walls; 2x2 pan concept, no primary niche, floor DCOF held',
 'PH-BATH2':'Sapphire 2x20 Glossy maker wet-listed in existing tub wall; Copper/Sandstone alternate for palette testing, PF05 floor DCOF held',
 'PH-BATH3':'Sandstone wet walls instead of unapproved Opal; Bone floor DCOF held, sink unselected',
 'PH-BATH4':'Flat Bone + Soho wet walls instead of Ribbed/Clara; 2x2 pan conditional, room area conflict',
 'PH-POWDER':'Earth Lines 2x10 dry relief retained at 3.69; wood floor, Luxe Gold faucet landing',
 'PH-WC':'PH Primary floor tile already includes shared WC allowance, no separate purchase',
 'TX-PRIMARY':'Flat Clay wet walls, PF07 12x24 level / 2x2 pan conditional, no niche',
 'TX-BATH2':'Copper/Sandstone + PF07 Cream floor conditional; strict floor DCOF missing',
 'TX-BATH3':'Emerald/Sandstone + PF05 Ash Grey field/2x2 pan conditional; tub/shower conflict',
 'TX-BATH4':'Flat Charcoal/Soho Black wet niche conditional, Bone Soft floor DCOF missing',
 'TX-POWDER':'Board-selected Camel 70 percent/Wheat 30 percent Haze dry feature, wood floor',
 'TX-POWDER2':'Retained Indigo Edge 6x6 dry relief; unpriced smooth insert not accepted',
 'TX-WC':'14 SF WC included in TX Primary quoted floor 116.1 SF, no second purchase'
}
def price(x):return 'null' if x is None else '$'+format(x,',.2f')
rows=[]
for r in rooms:
 for item in r['carried_tile_rows']:
  rows.append({'room':r['id'],'unit_type':r['unit_type'],'copies':r['unit_count'],
    'surface':item['surface'],'carried_tile_description':item['carried_description'],
    'Smartsheet_row_id':item['smartsheet_row_id'],
    'gross_SF_per_unit_including_original_15pct_waste':item['qty_sf_per_unit'],
    'historical_USD_per_SF':item['quoted_rate_usd_per_sf'],
    'carried_extended_USD_per_unit':item['extended_quote_cost_usd_per_unit'],
    'quoted_line_status':item['v4_scope_status'],'room_board_status':r['status'],
    'model_1529_verified':False,'current_Chicago_stock_lead':'null',
    'exact_measured_floor_wet_DCOF':'null' if item['surface']=='floor' else 'not applicable or requires wet wall listing',
    'installed_trim_labor_tax_freight':'null'})
assert len(rooms)==13 and len(rows)>20
with (dest/'SURFACE_TAKEOFF_13_ROOMS.csv').open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

reg=['# 1529 Wieland: 13-room source-anchored design decision register, R04','',
 'As of 2026-11-06. Two Penthouse and two Triplex unit copies. PH target $2.8M; TX $2.7M; $2.4M–$3.2M comps. Old Town primary, Lincoln Park and Gold Coast secondary. Based on 14 transactions/listings in nine distinct building groups, with marketing text only; no authenticated comp bath tile photos.',
 '',
 '| Room | Status | Champion | Score | Historical quoted tile-only per unit | BETTER material direction |',
 '|---|---|---|---:|---:|---|']
for r in rooms:
 s=r.get('champion_score')
 reg.append('| {} | {} | {} | {} | {} | {} |'.format(
   r['id'],r['status'],r.get('champion_id') or 'none',format(s,'.2f') if s is not None else 'null',
   price(r['carried_quote_material_subtotal_usd_per_unit']),better[r['id']]))
reg+=['',
 '## Good / better / best — evidence levels not marketing grades','',
 '**GOOD, carried:** retain the original governing v4 scheme solely as a dated source/budget reference; any failed wet-floor/wet-wall item is not installable just because historically specified.',
 '**BETTER, board-tested:** see each improved material direction above. Conditional options are not owner decisions; TX Powder 70/30 is board-selected only. PH Powder Earth Lines at 3.69 has one defense, not stable.',
 '**BEST, qualified and releasable:** currently NO final SKU package for tiled wet rooms can be named without exact manufacturer measured wet DCOF, wet-wall approvals, verified 1529 survey, Chicago distributor price/lot/lead, install detail and owner approval.',
 '',
 '### Governing technical rules',
 '- Tones Opal tub walls, Clara Caviar wet niches, Cortar Bone Reed/Ribbed and Clay Ribbed inside shower lack individual documented Wet Areas listings; flat Bone/Clay, Tones Sandstone and Soho Black have separate maker wet-wall listings.',
 '- Daltile PF07/PF05 Target wet DCOF >=0.42 is NOT a tested exact finish/SKU reading; still fails strict tiled floor rule until certified figure provided. Dry powders with wood floor: tiled-floor DCOF N/A.',
 '- No dedicated primary niche is scheduled; do not add a tile SKU or multiply its historic unpriced row.',
 '- Parent 1527-titled active Revit model has not been verified as 1529; all shown source geometry remains provisional.',
 '- Current Chicago stock and lead, owner per-room budget and up-to-125-percent check remain unknown; historic quote is not an approved budget cap.',
 '- Round001 PH Bath3/Bath4 blocked, PH Powder active. Round002 TX Baths2/3/4 blocked. Round003 TX Primary blocked, TX Powder board B accepted, TX Powder2 historic v4 retained. No owner-approved or stable room.',
 '',
 'Source traceability: per-room geometry.json, plumbing.json, original v4 handoff, Smartsheet 8569278453206916 September 3 ELM source rows, manufacturer research/products records, research/comps/COMPS.md and complete round reports.']
(dest/'13_ROOM_SELECTION_AND_TIERS.md').write_text('\n'.join(reg)+'\n',encoding='utf-8')

layouts=['# 13-room provisional dimensioned tile elevations and trade coordination, R04','',
 'PRELIMINARY DRAWING-BASED VALUES ONLY: do not treat these as measured 1529 Revit/shop drawings. Each length and height comes from the room geometry.json and is subject to final room-identity, survey, openings and fixture coordination.',
 'Common installer details: zero offset for 24x48, stagger no more than 1/3 long dimension if used and if maker allows; center balanced focal cuts and check actual piece sizes, grout widths and any under-3-inch slivers; specify waterproof backing/continuous membrane, tub-flange/curb connection, sloped niche sill, compatible movement sealant; deduct niche face from wet field; true shower pan tile must accommodate measured fall to selected drain; verify drain frame, threshold, glass/curb, mortar thickness, grout and metal/ceramic edge with selected fixtures. Source 15-percent waste is already included; never apply twice.',
 '']
for r in rooms:
 rid=r['id'];g=json.loads((root/'rooms'/rid/'geometry.json').read_text(encoding='utf-8'))
 p=json.loads((root/'rooms'/rid/'plumbing.json').read_text(encoding='utf-8'))
 layouts+=['## '+rid,'',
  'Room source area: {} SF ({}); ceiling: {} ft; wet zone: {}.'.format(
   g['floor_area']['value'],g['floor_area']['classification'],g['ceiling_height']['value'],
   (g.get('shower_or_tub_footprint') or {}).get('kind','none')),
  '| Wall ID | Existing description | Provisional width | Tiled height | Face net SF before openings |',
  '|---|---|---:|---:|---:|']
 for wall in g.get('tiled_walls',[]):
  w=wall['length']['value'];h=wall['tiled_height']['value']
  layouts.append('| {} | {} | {} ft = {:.2f} in | {} ft | {:.2f} |'.format(
    wall['id'],wall['description'],w,w*12,h,w*h))
 if not g.get('tiled_walls'):layouts.append('| no independent feature wall | shared primary floor finish | null | null | null |')
 fp=g.get('shower_or_tub_footprint')
 if fp:
  ww=fp['width']['value'];dd=fp['depth']['value']
  layouts.append('Provisional {} footprint: {} x {} ft = {:.2f} net SF, NOT a verified shower-pan takeoff.'.format(fp['kind'],ww,dd,ww*dd))
 drain=[f for f in p['fixtures'] if 'shower drain' in (f['description'] or '').lower() and 'descoped' not in (f.get('status') or '').lower()]
 layouts.append('Listed shower drain SKU(s): '+(', '.join(str(f['model_or_sku']) for f in drain) if drain else 'none for tub or not explicitly listed')+'.')
 layouts.append('Tile-adjacent selected fixture SKUs: '+', '.join(str(f['model_or_sku']).replace('\n',' ') for f in p['fixtures'] if any(t in (f['description'] or '').lower() for t in ('faucet','showerhead','raincan','bathtub','drain')) and 'descoped' not in (f.get('status') or '').lower())[:250]+'.')
 layouts.append('Existing gross quote SF/unit already includes 15% waste: '+('; '.join(str(f['surface'])+' '+str(f['qty_sf_per_unit']) for f in r['carried_tile_rows']) or 'no independent floor line; included in primary')+'.')
 layouts.append('Direction: '+better[rid]+'.')
 layouts.append('Open geometry: '+('; '.join(r.get('open_gaps',[])[:5]) or 'verify room and current openings')+'.')
 layouts.append('Shop-drawing hold: verify the true address/model, glass, valves, sill and trim intersections; cut plan must be dimensioned after field survey.\n')
(dest/'13_ROOM_PROVISIONAL_DIMENSIONED_ELEVATIONS.md').write_text('\n'.join(layouts)+'\n',encoding='utf-8')

proc=['# 13-room procurement, waste and source-cost audit — R04','',
 'Historical project quote: ELM 2026-09-03, Smartsheet finish register read 2026-11-06. Gross per-unit quantities already include 15-percent waste. Landed Chicago inventory, date/ETA, cartons, installation rates, grout/edges, tax, freight and current quote remain null; historical quote is not a PO or budget cap.',
 '| Room | Historic surface quantities SF/unit | Extended material $/unit | Procurement and compliance hold |',
 '|---|---|---:|---|']
for r in rooms:
 rid=r['id']
 q='; '.join(str(it['surface'])+' '+str(it['qty_sf_per_unit']) for it in r['carried_tile_rows']) or 'shared primary; do not double count'
 hold=('; '.join(r['open_gaps'][:2]) or 'measure room and check existing primary floor')
 proc.append('| {} | {} | {} | {} |'.format(rid,q,price(r['carried_quote_material_subtotal_usd_per_unit']),hold))
proc+=['',
 '### Quantified source exceptions','',
 '- TX Primary source blended 116.1 x $7.80 = $905.58/unit. An UNVERIFIED illustrative Soft/Anti-Slip component allocation at 87.64 x $8.14 and 28.46 x $6.75 yields $905.4946 raw / $905.50 component-rounded. The $0.08 difference is not a supplier price change.',
 '- TX Bath4 source 44.3 x $6.75 raw $299.025, carried extended $299.02 vs one critic display $299.03; preserve source extension.',
 '- No primary wet niche/extra tile scope; historical unpriced primary accent rows are excluded, not quantities to order.',
 '- Caviar and Opal wet listing missing; Reed/Ribbed wet listing does not inherit from flat Cortar. Maker wet-area use is distinct from numeric floor wet DCOF.',
 '- PF07 / PF05 public retail $6.27/SF or $106.72 per 17.02-SF carton is third-party example, NOT current project quote. 2x2 mosaic pan rate, box size, measured wet DCOF, installed cost and Chicago lot/lead NULL.',
 '- Historic ELM Cortar 10–12 week import/300-SF threshold/50-percent deposit is NOT verified current per-SKU lead or pooled minimum. No supplier contact authorized.',
 '- Niche quoted face may overlap surrounding wall quantity: compute the measured field deduction plus returns before approving a buy quantity.',
 '- PH and TX WC floors are already included in their respective Primary quoted material takeoffs. No second quoted purchase allowed.',
 '','### Required evidence before any procurement approval','',
 'Exact manufacturer color/SKU/finish size, Wet Areas use, numeric wet DCOF where tiled floor, dated Chicago lot quantity/ETA, carton and attic-stock minimums, moisture-compatible substrate/adhesive/membrane, trim/grout edge SKUs, corrected net niche/pan takeoff, landed and installed quote, owner room cap and formal approval.']
(dest/'13_ROOM_PROCUREMENT_HOLDS.md').write_text('\n'.join(proc)+'\n',encoding='utf-8')

visual=['# Thirteen-room concept rendering and sample-kit design briefs, R04','',
 'NO samples were ordered, and no image should falsely depict verified 1529 geometry. Render static same-camera A/B palette studies on the original source plan, preserving exact selected tub/shower, original openings, ceiling and fixture locations. Mark geometry uncertain; no primary niche or invented sinks.',
 '| Room | Existing material specimens to compare at full size | Design improvement to visualize |',
 '|---|---|---|']
for r in rooms:
 source='; '.join(it['carried_description'].split(' - ')[0] for it in r['carried_tile_rows'] if 'excluded' not in (it.get('v4_scope_status') or '').lower()) or 'shared primary floor'
 visual.append('| {} | {} | {} |'.format(r['id'],source,better[r['id']]))
visual+=['',
 '## Mock-up and viewpoint sequence','',
 '1. Wet primary: eye-level shower wall/ceiling plus axonometric showing existing Brizo linear drain, room level floor-to-pan tile junction, waterproofed return, grille and control penetrations. No primary niche.',
 '2. Tub secondaries: 1:1 tub back and two returns, wet-approved tile samples next to actual manufacturer plumbing metal finish, niche recessed sill with membrane/edge trim and non-duplicated quantity.',
 '3. PH Bath4/TX Bath3: point-drain schematic section with actual 4-inch drain only if the room program supports a shower; never represent 12x24 as a verified four-way sloped pan.',
 '4. Powders: full-height vanity elevation, tile module centered to actual mirror/faucet; finish, grout and corner trim specimens; wood floor held. TX Powder2 basin unresolved, Hansgrohe deck faucet cannot move to wall.',
 '5. Capture two lighting conditions, diffused daylight and warm evening, once real lighting/finish swatches are supplied. Neither rendering nor listing text certifies product performance.']
(dest/'13_ROOM_SAMPLE_KIT_AND_RENDER_BRIEFS.md').write_text('\n'.join(visual)+'\n',encoding='utf-8')

owner=['# Owner decision sheet — 1529 Wieland R04','',
 'No owner approval or fixture selection inferred. PH $2.8M and TX $2.7M targets; Old Town first.',
 '| Decision required | Affected spaces | What continues without owner response |',
 '|---|---|---|',
 '| Confirm 1527-titled Revit session equals correct 1529 project by address, project number, room and unit identities | All 13 | Keep old handoff geometry visibly provisional, no model edit |',
 '| Confirm TX Bath3 tub versus Brizo 4in point-drain shower | TX Bath3 | Retain separate conceptual tub/shower packages; pan quantity unknown |',
 '| Confirm PH Bath4 35 SF owner floor vs 27 SF old model, Soft versus Anti-Slip quote | PH Bath4 | Develop wet-listed flat Bone + Soho and small-pan logic without release |',
 '| Select sinks/basins | PH Bath3, TX Bath2, TX Powder2 | Continue wall field samples and dimension ranges; do not invent basin |',
 '| Set room-by-room material upgrade budget and contingency | All | Compare historic quote rates, unknown actual installed cost |',
 '| Authorize wet wall alternate to Tones Opal, Clara Caviar and Bone/Clay Ribbed or Reed | PH Baths3/4, TX Bath4, primaries | Use verified individual flat and Sandstone/Soho applications in research |',
 '| Verify exact published wet floor DCOF >=0.42 for all selected floor tile formats and shower pan variants | Tiled full baths and WC | Hold approval, research proper maker certificates |',
 '| Confirm 70 percent Camel / 30 percent Wheat board selection and mirror/faucet/grout layout | TX Powder | Board choice accepted but NOT owner-approved |',
 '| Approve dated supplier quote, carton/lot, freight, trim, grout, Chicago availability, installed mock-up | All | Reconcile gross 15-percent waste and actual opening deductions |',
 '',
 '## Do not reinterpret completed board history','',
 '- Round001 PH Bath3/4 blocked; PH Powder active 3.69 (not stable).',
 '- Round002 TX Baths2/3/4 blocked with no qualified floors.',
 '- Round003 TX Primary blocked; TX Powder board-selected 70:30 Haze; TX Powder2 existing Indigo retained.',
 '- PH/TX primary niches excluded. PH/TX WCs are separate rooms but duplicate no tile quote.',
 '',
 '### Owner sign-off register — EMPTY until decision']
owner+=['| Room | Owner selection | Finish/SKU | DCOF and wet approval | Dated owner sign-off |','|---|---|---|---|---|']
owner+=['| {} | pending | pending | pending | pending |'.format(r['id']) for r in rooms]
(dest/'OWNER_DECISIONS_R04.md').write_text('\n'.join(owner)+'\n',encoding='utf-8')
manifest={'as_of':'2026-11-06','room_count':len(rooms),'quote_surface_rows':len(rows),
          'outputs':sorted(x.name for x in dest.iterdir())}
(dest/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print('PASS 13 rooms',len(rows),'source rows','files',len(list(dest.iterdir())))

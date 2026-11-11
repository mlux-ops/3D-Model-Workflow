from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
reg={x['id']:x for x in json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
basis={
 'TX-PRIMARY':('C','corner shower','ELM Cortar Clay flat 24x48 Soft walls and ceiling plus Clay Ribbed relief; Cortar Clay Anti-Slip floor','Brizo 48-in linear with existing BR73480 rough; NO NICHE'),
 'TX-BATH2':('A','built-in tub alcove','ELM Tones Copper 2x20 Glossy stacked tub walls; Tones Sandstone existing niche; Cortar Clay 12x24 Soft bath floor','Retain built-in tub and actual selected plumbing; basin UNSELECTED'),
 'TX-BATH4':('B','built-in tub alcove','ELM Cortar Charcoal 24x48 Soft wet walls with unverified Bone Ribbed relief, Clara Caviar 2x8 niche and Cortar Bone Soft floor','Duravit 700332000000090 and Hansgrohe Matte White; existing tub and waste/overflow')}
intro='This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.'
for rid,(letter,program,description,fixtures) in basis.items():
 d=R/'rooms'/rid/'board/round-009/candidates';d.mkdir(exist_ok=True,parents=True)
 path=d/(letter+'.md')
 assert not path.exists(),path
 row=reg[rid]
 g=json.loads((R/'rooms'/rid/'geometry.json').read_text(encoding='utf-8'))
 lines=['# '+rid+' — Candidate '+letter+' — complete tile design option','',''+intro,'',
 '## Room and source-controlled scope','',
 'Room program: '+program+'. Two identical unit copies; quantities and historical material extension per room per unit. '+fixtures+'.',
 'Design intent: '+description+'. This composition is a neutral board alternative; no signed owner/technical release, actual current supplier quote, approved per-room budget or verified native 1529 geometry exists.',
 '',
 '| Surface / edge | Tile, size, finish and proposed orientation | Source gross SF (one 15% waste included) / geometry | Historical source $ / alternative $ | Manufacturer/build gate and next proof |',
 '|---|---|---|---|---|']
 for z in row['carried_tile_rows']:
  surface=z['surface']
  q=z['qty_sf_per_unit'];rate=z['quoted_rate_usd_per_sf']; ext=z['extended_quote_cost_usd_per_unit']
  exclude=rid=='TX-PRIMARY' and surface=='accent'
  prod='Smartsheet row '+str(z['smartsheet_row_id'])+': '+z['carried_description'].replace('|',' / ')
  lines.append('| '+surface+' | '+prod+'; follow source stated orientation where available | '+format(q,'.2f')+' SF gross/unit, implied net '+format(q/1.15,'.2f')+' SF only as reverse math; actual field split null | Carried '+str(rate)+' USD/SF; '+str(ext)+' USD/unit; new supplier price null | '+('EXCLUDED non-purchasable primary niche; zero new scope. ' if exclude else '')+'Exact product intended wet-use and every tiled bathroom floor/pan DCOF unverified; confirm source finish, actual drain, cartons, field/wet net before release |')
 lines.append('| grout / exposed edges / membrane | Match actual metal/fixture finish; designer mock-up, no unverified profile selected | trim exposed LF, stick length, grout joint, actual niches/returns and membrane all null | historic setting/labor/trim prices null | Need survey, compatible waterproof/drain and cut details; no order |')
 lines+=['','## Existing drawing-derived wall check (NOT certified 1529)','',
 '| Wall | Source inside-face length x tiled height | Nominal centerline layout caution |',
 '|---|---|---|']
 for w in g['tiled_walls']:
  lines.append('| '+w['id']+' | '+format(w['length']['value']*12,'.2f')+' in x '+format(w['tiled_height']['value']*12,'.2f')+' in | Actual tile calibrated joint, true door/window, corners, valve face, niche opening and focal cuts null; no guaranteed >=3-in field cut |')
 lines+=['','## Hard gates and conditional comparison','',
 '- Wet walls: product-specific wet listing required, not collection-wide. Flat Cortar Clay and Charcoal maker Wet Areas listed; Clay Ribbed/Bone Ribbed individual pages say Walls/Back Splashes only; Clara Caviar collection listing omits Wet Areas. Thus relief/Caviar in actual wet zone remains FAIL. Copper/Sandstone maker individual wet-use is documented in project records; retain actual finish control.',
 '- Wet bath level floor: ELM Cortar Clay Soft / Bone Soft / mixed Anti-Slip per room has no published exact measured ANSI wet DCOF >=0.42 for selected finish and format. FAIL pending maker dated exact report. Large-format 24x48 cannot be presumed to slope to selected linear drain.',
 '- Tub vs shower: no extra shower pan is counted in the tub rooms. TX Primary chosen linear drain position/slope and 48-in wall side are not surveyed; manufacturer/product floor compatibility is not established.',
 '- Commercial: historical source subtotal '+format(row['carried_quote_material_subtotal_usd_per_unit'],'.2f')+' USD/unit is a 2026-09-03 ELM material-only record; full installed new product price, local lot, lead and room upgrade allowance null. Do not use source amount as approved owner room budget; 125% gate cannot be evaluated.',
 '- Geometry: source wall extents and estimated area are provisional 1529 export/handoff, not a verified native 1529 Revit view. Actual niche dimensions/field subtraction, trim LF, wet pan and grout/calibration remain null.',
 '- Owner: TX Bath2 basin owner-unselected; all alternatives need sample signoff. No primary niche; TX Bath4 existing tub remains unchanged. No steam discussion.',
 '',
 '## Market design basis','',
 '14 existing listing records/9 independently distinct buildings, Old Town within 24 months prioritized (four 405 W Armitage transactions = one building). Lincoln Park/Gold Coast are marked secondary, and no tile material is inferred from unavailable bathroom listing photos. PH target $2.8M, TX $2.7M, comparator $2.4M-$3.2M. Preserve coherent matte white/Black Onyx fixture relationship and avoid speculative high-cost accent layering.',
 '',
 '## Evidence references','',
 'Source: individual room geometry.json and plumbing.json; carried tile source rows and handoff v4/Smartsheet 2026-09-03; research/comps/R05_OLD_TOWN_DESIGN_EVIDENCE_AND_ROOM_TIERS.md; research/products/R05_WET_LISTINGS_DCOF_INSTALLATION_EVIDENCE.md; R06 and R07 Daltile/Glazzio manufacturer comparison; official ELM Cortar/Tones pages and manufacturer wet-use lists. Actual order SKU/lot, measured DCOF, price, Chicago availability and owner approval all remain null.']
 path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 assert path.read_text(encoding='utf-8').splitlines()[2]==intro
 print(rid,letter,path.stat().st_size)

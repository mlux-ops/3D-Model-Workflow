"""One-time R018 source-only candidate writer. Never run against existing outputs."""
from pathlib import Path
from datetime import date
import json, hashlib

ROOT=Path(__file__).resolve().parents[1]
ROOMS=json.loads((ROOT/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
LOOKUP={r['id']:r for r in ROOMS}
SPECS={
 'PH-BATH2':dict(wall=('ELM Tones Sapphire 2x20 Glossy','https://www.elmsurfaces.com/product/sapphire-tones'),niche=('ELM Tones Sandstone 2x20 Glossy','https://www.elmsurfaces.com/product/sandstone-tones'),plumbing='Owner-selected Duravit 59-in tub; Hansgrohe MATTE WHITE; no tiled shower pan.',basin='No unselected basin condition has been asserted for this room.',choice={'A':'Boden','B':'Trosa'},note='Existing nominal tub-to-wall dimensional allowance is not a certified installed clearance.'),
 'TX-BATH2':dict(wall=('ELM Tones Copper 2x20 Glossy','https://www.elmsurfaces.com/product/copper-tones'),niche=('ELM Tones Sandstone 2x20 Glossy','https://www.elmsurfaces.com/product/sandstone-tones'),plumbing='Owner-selected Duravit 59-in tub; Hansgrohe CHROME; no tiled shower pan.',basin='BASIN OWNER-UNSELECTED. No basin assignment permitted.',choice={'A':'Trosa','B':'Boden'},note='Selected Chrome fixtures govern tile-metal palette; tub waste is not a shower point drain.'),
 'TX-BATH4':dict(wall=('ELM Cortar Charcoal 24x48 flat Soft','https://www.elmsurfaces.com/product/cortar-charcoal'),niche=('ELM Soho Ivory 2x10 Glossy','https://www.elmsurfaces.com/product/soho-ivory'),plumbing='Owner-selected Duravit 59-in tub; Hansgrohe MATTE WHITE; no tiled shower pan.',basin='No basin selection changes proposed.',choice={'A':'Boden','B':'Trosa'},note='Niche replaces previously unlisted Caviar product only as an unapproved tile proposal; Hansgrohe thermostat/diverter-source compatibility remains held.'),
}
FLOORS={
 'Trosa':dict(name='Emser Capisco Trosa 12x24 Matte',sku='F08CAPITR1224M',color='taupe',grout='165 Delorean Gray',url='https://www.emser.com/product/capisco-f08capitr1224m'),
 'Boden':dict(name='Emser Capisco Boden 12x24 Matte',sku='F08CAPIBO1224M',color='ivory',grout='11 Snow White',url='https://www.emser.com/product/capisco-f08capibo1224m'),
}

files={}
for room, spec in SPECS.items():
 r=LOOKUP[room]
 assert r['status']=='blocked' and r['champion_id'] is None
 rows={z['surface']:z for z in r['carried_tile_rows']}
 assert set(rows)=={'wall','floor','accent'}
 outdir=ROOT/'rooms'/room/'board'/'round-018'/'candidates'
 assert not outdir.exists(),f'Existing round folder: {outdir}'
 for letter,floor_code in spec['choice'].items():
  floor=FLOORS[floor_code]
  per=r['carried_quote_material_subtotal_usd_per_unit']
  first=['# '+room+' — Candidate '+letter+' — tile scheme', '', 'This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.', '',
   '## Room program and proposed design',
   spec['plumbing']+' '+spec['basin'],
   'Wet tub wall: **'+spec['wall'][0]+'**, horizontal stacked layout (wall grout final color/joint TBD). Existing wet niche: **'+spec['niche'][0]+'**, oriented to the field joint rhythm (niche trim and grout TBD). Dry-zone bathroom LEVEL floor: **'+floor['name']+'** (`'+floor['sku']+'`, '+floor['color']+'), running bond 0-offset, manufacturer recommended 1/8-inch joint and '+floor['grout']+' grout color as mockup option. No tiled shower PAN.', '',
   '## Surface-specific manufacturer evidence and historical quote',
   '| Surface and original Smartsheet row | Proposed actual product and individual maker evidence | Original gross SF per copy, 15% waste INCLUDED | Carried historical price per copy | Distinct source and hard-gate condition |',
   '|---|---|---:|---:|---|']
  for surf in ('wall','floor','accent'):
   row=rows[surf]
   if surf=='wall':
    product,url=spec['wall'];detail='Individual wet WALL application documented for this exact source color; recheck wet listing and calibrated factory finish before freeze.'
   elif surf=='accent':
    product,url=spec['niche'];detail='Separate individual wet NICHE WALL application; physical niche dimensions and waterproofed sill/returns are not certified.'
   else:
    product,url=floor['name']+' '+floor['sku'],floor['url'];detail='Maker publishes DCOF >=0.60 and Commercial Floor Wet YES for exact SKU, exceeding BOARD.md published wet >=0.42 on LEVEL; not a raw measured lab reading or an owner/installer release.'
   first.append('| '+surf+' `'+str(row['smartsheet_row_id'])+'` | ['+product+']('+url+') | '+f"{row['qty_sf_per_unit']:.2f}"+' SF | $'+f"{row['extended_quote_cost_usd_per_unit']:.2f}"+' @ $'+f"{row['quoted_rate_usd_per_sf']:.2f}"+'/SF | '+detail+' |')
  first+=['', '## Design, evidence and comparison',
   'The '+floor['color']+' Capisco quartzite-look floor is deliberately a quiet supporting plane beneath the selected tub and '+spec['wall'][0]+' wet field. Match a real tile/grout/edge board to the selected plumbing metal before final design judgment. Exact maker [floor technical listing]('+floor['url']+') includes nominal 12x24, rectified 9-mm porcelain, shade variation V2, 1/8-inch recommended grout, Wet Commercial Floor YES and **published DCOF >=0.60**. The lower bound is documentation, **not** an invented raw AcuTest point.',
   'Market evidence: [Old Town comparisons](../../../../../research/comps/COMPS.md) OT01–OT04 are four units in ONE building; OT05 is a separate Old Town Triangle building. Current text describes bath programs, not verified competing tile dimensions, grout, or metal; do not award a buyer premium on uninspected photos.',
   '', '## Gating, quantity and commercial truth',
   'Published product-specific FLOOR wet DCOF >=0.60 is suitable evidence for the **board/BOARD.md section 46-62 published >=0.42 threshold** for a flat LEVEL bath floor; an earlier R012/R013 heightened raw-laboratory certificate release condition is a separate unfulfilled technical/reviewer condition, not a fabricated measured value. No sloping tiled shower PAN is proposed because this is the selected Duravit TUB program.',
   'Actual quoted old material-only subtotal **$'+f'{per:.2f}'+'/copy** (two copies) is a comparison basis, not a verified owner per-room budget. Exact Emser Chicago shade lot, sale carton coverage, supplier on-hand stock, lead time, current landed $/SF and revised room subtotal **UNKNOWN**; source quote rate is NOT applied to an alternate. Neither arbitrary upgrade allowance nor >125% budget approval can be inferred without a carried owner budget/current price. Source 15% original gross included ONCE; never apply a second waste factor or double count niche face area.',
   'US distribution evidence: the product remains individually listed in Emser US catalog, not marked discontinued on the observed page. Chicago warehouse lot/on-hand/ETA UNKNOWN and must be checked read-only before procurement decision. '+spec['note'],
   'Geometry: prior drawing W1/W2/W3 dimensions and wall openings are not independently traced to native Revit element/receipt IDs; owner confirmed 1527/1529 are SAME building on 2026-11-07, but existing dimensions remain to be verified against the read-only model and actual field conditions.',
   'No final grout/edge profile, niche net/back/sill area, installed GC budget, case order, owner samples, fixture substitution, vendor contact, email, order or owner approval is proposed. All source/owner/PO releases remain FALSE.', '']
  p=outdir/(letter+'.md'); p.parent.mkdir(parents=True,exist_ok=True)
  payload='\n'.join(first)
  p.write_text(payload,encoding='utf-8',newline='\n')
  b=p.read_bytes(); files[str(p.relative_to(ROOT)).replace('\\','/')]=dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))

research=ROOT/'research/products/R018_CAPISCO_BODEN_TROSA_INDIVIDUAL_LEVEL_FLOOR_BOARD_EVIDENCE.md'
assert not research.exists()
research.write_text('''# R018 individually published LEVEL-floor maker evidence (2026-11-06)

Two actual US manufacturer-listed Capisco rectified porcelain 12x24 Matte tiles, evaluated for LEVEL tub-bath floors ONLY:

- **Trosa / Taupe, F08CAPITR1224M**: https://www.emser.com/product/capisco-f08capitr1224m — 9 mm, V2, 1/8-in grout recommended (165 Delorean Gray), individual maker **DCOF >=0.60**, Commercial Floor Wet YES, Residential Floor YES.
- **Boden / Ivory, F08CAPIBO1224M**: https://www.emser.com/product/capisco-f08capibo1224m — 9 mm, V2, 1/8-in grout recommended (11 Snow White), individual maker **DCOF >=0.60**, Commercial Floor Wet YES, Residential Floor YES.

These are minimum maker-declared published wet-DCOF bounds, **not raw exact laboratory readings**. BOARD.md hard gate 2 is a published wet DCOF >=0.42, so both individually pass that narrow threshold for bath LEVEL use. Do not claim floor-slip evaluation proves waterproof assemblies, installation, or site safety. These are NOT tiled sloped shower PAN specifications here; PH-BATH2, TX-BATH2, TX-BATH4 remain owner-selected Duravit tubs.

The product pages demonstrate a current US catalog/distribution route, but **NOT Chicago physical stock**, actual shade/caliber lots, local pickup, orderable case/carton coverage, lead times, project retail $/SF, tax/freight or installed quote. The product page shows samples unavailable: do NOT request them. Manufacturer condition status beyond the observed catalog page is not independently authenticated by suppliers. Unknowns remain null and no vendor contact is authorized.

Shared other surface evidence: PH2 Sapphire exact wet WALL https://www.elmsurfaces.com/product/sapphire-tones; TX2 Copper exact wet WALL https://www.elmsurfaces.com/product/copper-tones; PH2/TX2 Sandstone exact wet NICHE https://www.elmsurfaces.com/product/sandstone-tones; TX4 Cortar Charcoal flat wet WALL https://www.elmsurfaces.com/product/cortar-charcoal; TX4 Soho Ivory 2x10 Glossy wet NICHE https://www.elmsurfaces.com/product/soho-ivory . Exact finish and product-specific use must remain a distinct maker gate.

Old Town OT01-OT05 listing imagery has not been authenticated to a specific bathroom tile surface in this research pass; no exact competitor size, layout, grout or fixture metal conclusions are made. OT01-OT04 share one building, not four design precedents.

Original Smartsheet per-copy totals (15% gross waste once): PH-BATH2 $920.28, TX-BATH2 $999.92, TX-BATH4 $1,320.82, sourced from current state/ROOMS.json. Replacement material current price and owner allocated room budget remain NULL. This evidence file is NOT owner approval, procurement authority, independent specialist critique or weighted board decision.
''',encoding='utf-8',newline='\n')
b=research.read_bytes();files[str(research.relative_to(ROOT)).replace('\\','/')]=dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
receipt=ROOT/'state/ROUND018_TUB_TILE_SOURCE_PREPARED_AWAIT_BLIND_PREFLIGHT.json'
assert not receipt.exists()
data={'round':18,'as_of':'2026-11-06','focus_rooms':list(SPECS),'phase':'1-comps_SOURCE_PREPARED_AWAIT_BLIND_PREFLIGHT','purpose':'Three blocked tub-room tile options, no pan or new plumbing decisions','files':files,'neutral_private_mapping':'NONE: both options are new nonchampion candidates; no incumbent exists','champion_assignment':None,'critic_dispatch':'NOT_DISPATCHED','original_design_worker9':'FAILED','four_independent_critic_reports':False,'weighted_board_scoring':None,'owner_approval':False,'procurement_release':False,'native_1527_equals_1529_owner_confirmed':True,'native_room_geometry_receipts_validated':False,'prior_signed_round_artifacts_unchanged':True}
receipt.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
print('CREATED 6 candidate packets and 1 research evidence file; receipt',receipt.name)
for k,v in files.items():print(k,v['bytes'],v['sha256'])

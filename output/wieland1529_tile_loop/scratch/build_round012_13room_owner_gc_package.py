"""Source-driven all-13-room owner/GC and purchasing controls; only new R12 outputs."""
from pathlib import Path
import hashlib,json,csv
R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r12'
O.mkdir(parents=True,exist_ok=True)
state=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))
scoring=json.loads((R/'state/ROUND011_SCORING.json').read_text(encoding='utf-8'))
assert len(state['rooms'])==13 and scoring['verification']['all_valid']
spec={
'PH-PRIMARY':('Flat Cortar Bone wet wall; 48in Brizo Black Onyx linear and Duravit tub; NO NICHE','HNC6615 level/WC and Prime RL21 mosaic linear pan concept','Raw SKU level and pan tests, linear membrane/rough, no WC duplication'),
'PH-BATH2':('Wet-listed Sapphire 2x20 and Sandstone tub niche, Duravit tub and Matte White','Retain wet wall; investigate HNC6615 certified level floor, NO tiled pan','Sapphire wall approval PASS; floor raw wet DCOF unresolved; actual tub flange'),
'PH-BATH3':('Opal 2x20 original wet wall HOLD, Bone Soft and Sandstone niche','Wet-listed Sandstone wall/niche, HNC6615 level; HNC6715 point pan only if walk-in','Owner tub/walk-in and sink UNSELECTED, Delta DT062412 Chrome square shower drain conflict'),
'PH-BATH4':('Full original Bone Ribbed wet wall + Clara Caviar niche not released','Maker-listed flat Bone/Soho, HNC6615 level and HNC6715 4-plane point pan','Actual WALK-IN, Brizo BT062415-BNX, 35/27SF, Soft/AntiSlip and 214.4SF vendor total hold'),
'PH-POWDER':('Earth Lines board direction 3.69; not owner-approved','Dimension actual dry vanity feature, grout/edge/fixtures and sample','Dry wall: do not misclassify as shower floor; signoff needed'),
'PH-WC':('Primary shared floor included, no separate line','Verify Primary-to-WC threshold and field continuity','No additional floor order; source quantity remains Primary only'),
'TX-PRIMARY':('Cortar Clay original, 48in linear study and no niche','Maker wet-listed flat Clay study, separately tested level/WC and linear mosaic','Clay Ribbed wet approval, raw floor/pan tests, drain build and WC double-count HOLD'),
'TX-BATH2':('Copper tub surround + Sandstone niche, Clay Soft bath level floor','Wet-listed wall retained if exact finish supported; tested floor alternative','TX Bath2 basin UNSELECTED; tub and waterproof flange; no assumed tiled pan'),
'TX-BATH3':('Wet-listed Emerald original horizontal stack, Sandstone niche, Grey Soft','Emerald vertical 2x20 / HNC6615 level; HNC6715 pan conditional owner walk-in','Brizo BT062415-BNX Black Onyx vs tub alcove; vertical 1.60in strips unresolved'),
'TX-BATH4':('Charcoal tub wall, Bone Soft level, Clara Caviar niche hold','Wet-listed alternate flat wall+niche and certified level floor','Original Caviar individual Wet Areas missing, tub details/quotes/survey held'),
'TX-POWDER':('70:30 Haze Camel/Wheat board-accepted 3.67, owner pending','Full-scale dry vanity mix grid and edge/fixture mock-up','Preserve 70:30 ratio and no source or color substitution'),
'TX-POWDER2':('Indigo Edge 6x6 board-retained 3.23, basin UNSELECTED','Dimension 6x6 dry wall cuts, grout, metal and reflectance','Owner sink decision required, no fabricated basin or pan'),
'TX-WC':('Primary shared floor included, no separate line','Survey shared floor/transition at WC','No double count or separate invoice')
}
assert {r['id'] for r in state['rooms']}==set(spec)
book=['# Round 012 — all 13 rooms: owner, GC and procurement control book','',
'**Not a construction release.** Room quantities and W wall dimensions originate from the 1529 handoff/export, not a verified native 1529 Revit model; observed live 1527 does not certify this property. All owner approvals, new supply and installed quotes and purchase authorizations remain false/null.','',
'## GOOD / BETTER / BEST design-and-release schedule','',
'GOOD = defensible historic material/accepted board direction with its current hold; BETTER = studied source-backed alternative; BEST = a future approved and verified installation package, not a new product or price claim.','',
'| Room | Current governing status | Source cost per copy (2026-09-03 USD) | GOOD | BETTER | BEST / release action |',
'|---|---|---:|---|---|---|']
for r in state['rooms']:
 rid=r['id'];good,better,gates=spec[rid]
 label=('BLOCKED' if r['status']=='blocked' else 'ACTIVE conditional' if r['status']=='active' else 'SHARED WC no separate order')
 book.append('| %s | %s | %.2f | %s | %s | %s |'%(rid,label,r['carried_quote_material_subtotal_usd_per_unit'],good,better,gates))
book+=['','## Construction packets and owner decision cards','']
source_rows=[];wall_rows=[];total=0
for r in state['rooms']:
 rid=r['id'];good,better,gates=spec[rid]
 geo=json.loads((R/'rooms'/rid/'geometry.json').read_text(encoding='utf-8'))
 original=r['carried_quote_material_subtotal_usd_per_unit']
 total+=original*r['unit_count']
 book+=['','### '+rid,'',
 '**Status:** '+r['status']+'; accepted champion '+str(r['champion_id'])+'; owner approval '+str(r['owner_status'])+'; procurement RELEASE **FALSE**. Historical material per copy $%.2f, %d copies; exact current alternate, installation and owner room cap NULL.'%(original,r['unit_count']),
 '**Required construction evidence:** '+gates+'. **Source geometry is provisional** until actual 1529 model identity and field verification; obtain measured net opening/niche/returns, signed valve/drain centers, threshold and true edge LF before procurement.',
 '**Samples and render brief:** dry field-wall mock-up with selected plumbing finish and color-calibrated grout/edge, room elevation with dashed unknowns, second cut/return sample and condition-specific tub flange or walk-in point/linear drain section; do not generate an unselected fixture or claim actual samples ordered.',
 '**Quantity discipline:** original gross source SF already include 15% waste; separate FIELD, LEVEL and conditional PAN net areas and apply exactly one approved waste rule. No double-counting primary shared WC floors, niche face/backs, trims or separate full-area pan. New carton and price NULL until actual pack SKU/area/quote.']
 if rid in scoring['room_results']:
  b=scoring['room_results'][rid];h=b['incumbent_letter'];n=b['challenger_letter']
  book.append('**Actual Round011 scoring:** historical %s %.2f, revised %s %.2f, delta %+.2f, minimum revised %.1f — **BLOCKED**, no accepted selection.'%(h,b['candidates'][h]['weighted_score'],n,b['candidates'][n]['weighted_score'],b['margin'],b['candidates'][n]['minimum_critic_score']))
 for row in r['carried_tile_rows']:
  qty=row['qty_sf_per_unit'];cost=row['extended_quote_cost_usd_per_unit'];excluded='PRIMARY' in rid and row['surface']=='accent'
  source_rows.append({'room':rid,'surface':row['surface'],'source_row_id':row['smartsheet_row_id'],'original_exact_description':row['carried_description'],'original_gross_sf_per_copy_15pct_included':qty,'arith_net_sf_not_survey':round(qty/1.15,4) if qty is not None else None,'historic_material_usd_per_copy':cost,'historic_rate_usd_per_sf':row['quoted_rate_usd_per_sf'],'historic_2copy_usd':round(cost*r['unit_count'],2) if cost is not None else None,'source_order_status':'EXCLUDE primary niche' if excluded else 'HISTORIC ONLY','new_sku':None,'new_exact_wet_listing':None,'raw_measured_wet_dcof':None,'actual_level_gross_sf':None,'actual_pan_gross_sf':None,'actual_box_yield':None,'actual_cartons':None,'local_confirmed_lot':None,'current_landed_price':None,'actual_install_cost':None,'owner_cap':None,'owner_approved':False,'release':False})
 for w in geo.get('tiled_walls',[]):
  ln=w.get('length',{}).get('value');ht=w.get('tiled_height',{}).get('value')
  wall_rows.append({'room':rid,'wall_tag':w['id'],'provisional_source_width_ft':ln,'provisional_source_tiled_height_ft':ht,'nominal_unadjusted_face_sf':round(ln*ht,3) if ln and ht else None,'verified_1529_model':False,'actual_openings':None,'actual_niche_face_and_returns':None,'actual_valve_and_drain_positions':None,'actual_tile_caliber_and_joint':None,'verified_cut_grid':None,'true_trim_lf':None,'movement_membrane_edge_detail':None,'gc_approval':False})
 assert r['owner_status'] is None or r['owner_status']!='approved'
book+=['','## Decision hierarchy and technical dependencies','',
'1. Preserve board-accepted TX Powder 70:30 Camel/Wheat and retained Indigo Edge, plus PH Powder Earth Lines; none is owner-signed. Do not treat dry vanity tile as wet shower-pan material.',
'2. Primary baths: no extra niche and shared WC floor is inside Primary quotation; keep selected linear drains. PH2 actual Duravit tub with no tiled shower pan. PH4 actual Brizo point-drain WALK-IN. PH3 and TX3 tub-alcove plans versus scheduled square shower drains remain owner-held.',
'3. Historical quoted PH4 full Bone Ribbed source wall 107.2 SF per unit is 214.4 SF for two copies and may be absent from old vendor GRAND TOTAL; no payable shortfall inferred. PH4 old floor quote Soft versus intended Anti-Slip and 35/27 SF conflict retained.',
'4. ELM individual Sapphire wet wall PASS. Opal and Clara Caviar wet listing unproven; flat Bone permission does not license Reed/Ribbed or Clay relief. Glazzio HNC6615/HNC6715 maker DCOF >0.50 is a BOUND, not raw numeric lab evidence; older Glazzio portal differs on threshold and grout/pack data.',
'5. Market: 14 listings / nine buildings; OT01–OT04 at 405 W Armitage ONE precedent; PH $2.8M, TX $2.7M, band $2.4M–$3.2M. No authenticated listing bathroom tile photos.',
'6. Raw test, finish-specific wet approval, calibrated cuts, drain/liner/flood and waterproof-system compatibility, exact Chicago lot/ETA, room cost cap and owner signatures remain separate release gates.',
'See research/products/R12_PUBLIC_MAKER_DRAIN_AND_SUPPLY_EVIDENCE_20261106.md and prior original R10 nine-file manifest; these are evidence controls, not vendor authorizations.']
(O/'R12_13_ROOM_GOOD_BETTER_BEST_AND_BUILD_CONTROL.md').write_text('\n'.join(book)+'\n',encoding='utf-8')
for name,rows in [('R12_27_ROW_SOURCE_AND_ALTERNATE_PROCUREMENT_CONTROL.csv',source_rows),('R12_13_ROOM_WALL_CUT_FIELD_SURVEY.csv',wall_rows)]:
 assert rows
 with (O/name).open('w',newline='',encoding='utf-8-sig') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
pack=[{'sku':'HNC6615','use':'LEVEL bathroom only','maker_reported_wet_dcof':'>0.50 lower bound, NOT raw numeric test','exact_lab_test':None,'maker_actual_size':'11.73x23.62in','maker_box_yield_sf':9.69,'formula':'ceil(approved LEVEL gross SF / 9.69)','approved_level_gross_sf':None,'approved_cases':None,'current_project_cost':None,'supplier_confirmed_stock':None,'owner_release':False},
{'sku':'HNC6715','use':'POINT PAN only if owner WALK-IN','maker_reported_wet_dcof':'>0.50 lower bound, NOT raw numeric test','exact_lab_test':None,'maker_actual_size':'11.73x11.85in sheet','maker_box_yield_sf':4.85,'formula':'ceil(approved PAN gross SF / 4.85) IF authorized shower; N/A if standalone tub','approved_level_gross_sf':None,'approved_cases':None,'current_project_cost':None,'supplier_confirmed_stock':None,'owner_release':False}]
with (O/'R12_MAKER_EXACT_PACK_AND_CONDITIONAL_PAN_ORDER_CALCULATOR.csv').open('w',newline='',encoding='utf-8-sig') as f:
 writer=csv.DictWriter(f,fieldnames=list(pack[0]));writer.writeheader();writer.writerows(pack)
manifest={'as_of':'2026-11-06','rooms':13,'source_rows':len(source_rows),'wall_surveys':len(wall_rows),'original_source_15pct_waste_included':True,'historic_material_four_copies_usd':round(total,2),'owner_approved':False,'procurement_release':False,'round011_scoring_sha256':hashlib.sha256((R/'state/ROUND011_SCORING.json').read_bytes()).hexdigest(),'outputs':{}}
assert len(source_rows)==27 and round(total,2)==23572.44
for file in sorted(O.glob('*')):
 if file.name!='MANIFEST.json':
  raw=file.read_bytes();manifest['outputs'][file.name]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
(O/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS R12',manifest['rooms'],'rooms',manifest['source_rows'],'source rows',manifest['wall_surveys'],'wall studies',len(manifest['outputs']),'SHA-signed outputs',manifest['historic_material_four_copies_usd'],'original 4-unit historic, owner/release false')

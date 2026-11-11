from pathlib import Path
import json,csv,math
R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r09';O.mkdir(parents=True,exist_ok=True)
rooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
choices={
'PH-PRIMARY':('Flat Cortar Bone wet wall + independently vetted level floor/pan','Brizo 48-in linear; no niche','exact field and pan wet DCOF; linear-drain manufacturer suitability'),
'PH-BATH2':('Retain Sapphire wet-approved wall; Grey Soft floor alternate study','Duravit tub/Hansgrohe Matte White','Cortar Grey floor exact measured wet DCOF'),
'PH-BATH3':('Wet-listed Sandstone wall only if owner approves','tub versus Delta square point drain; sink unselected','owner tub/drain reconciliation, basin and exact floor test'),
'PH-BATH4':('Flat Bone wet wall + Soho wet niche; PF09 or other separate pan test','Brizo 4-in point','35 vs 27 SF, Soft vs Anti-Slip, pan four-plane and DCOF'),
'PH-POWDER':('Earth Lines dry feature','wood floor','actual dry relief wall returns and selected grout'),
'PH-WC':('Inherit selected Primary level tile','no separate floor','inherited Primary level floor measured wet DCOF'),
'TX-PRIMARY':('Flat Clay wet wall; Prime RL mosaic linear-pan research','Brizo 48-in linear; no niche','pan maker target conflict and exact measured floor/pan test'),
'TX-BATH2':('Copper/Sandstone retained; optional HNC6615 level floor','existing tub; basin unselected','exact HNC6615 test, shade and current Chicago quote'),
'TX-BATH3':('Maintain tub/shower alternatives WITHOUT selecting either','owner tub versus Brizo point drain','owner program before pan area and wet wall determination'),
'TX-BATH4':('Flat Charcoal + Soho maker wet-listed niche; HNC6615 level floor','Duravit tub/Matte White','Caviar/Bone Ribbed not wet-listed, exact floor test'),
'TX-POWDER':('70:30 Camel/Wheat Haze board accepted','dry wall/wood floor','owner sample decision and independently quoted color cartons'),
'TX-POWDER2':('Retain Indigo relief','dry wall/wood floor/deck faucet','owner basin and actual backing'),
'TX-WC':('Inherit TX Primary approved level tile','no separate floor','inherited level floor measured wet DCOF')}
assert set(choices)=={r['id'] for r in rooms}
rows=[]
md=['# R09 | Source-to-selection construction procurement variance and 13-room owner cards','',
'**Scope:** 13 distinct room IDs replicated in 2 Penthouse +2 Triplex dwelling copies. Board status remains distinct from owner approval and release. This register is NOT an order, supplier price, available stock, certified slip result or finished construction takeoff.',
'',
'**Source arithmetic:** 27 historic ELM/Smartsheet rows are retained, INCLUDING two deliberately excluded unpriced Primary niche history lines. Exactly 25 rows carry original material scope; the historical 4-dwelling tile-material-only sum is USD 23,572.44. Historic SF per unit already include one 15% waste. Current replacement unit rate, landed installed total, eligible substitutions, true trim LF and actual order cartons are NULL for every proposed selection. WC has no independent tile row.',
'',
'**Current offer vs source:** Older 2026-09-03 ELM values are neither current procurement offers nor owner material budgets. Public Glazzio dealer examples are non-contract retail indications. Daltile wet DCOF application target is not a measured SKU point; Glazzio newer >0.50 versus legacy >0.42 are published lower bounds, not exact lab tests. Maker Wet Areas-listed Sapphire has no bearing on its separate Grey Soft floor.',
'']
for room in rooms:
 rid=room['id'];option,fixture,hold=choices[rid]
 active=0.0;all_gross=0.0;excluded=0.0
 for z in room['carried_tile_rows']:
  q=z['qty_sf_per_unit'];all_gross+=q
  exclusion=rid.endswith('PRIMARY') and z['surface']=='accent'
  if exclusion:excluded+=q
  else:active+=q
  rows.append({'room_id':rid,'unit_copies':room['unit_count'],'source_row_id':z['smartsheet_row_id'],
  'source_surface':z['surface'],'source_product_description':z['carried_description'],
  'source_gross_sf_already_includes_15pct':q,'source_implied_net_sf_NOT_MEASURED':round(q/1.15,4),
  'source_quoted_usd_sf':z['quoted_rate_usd_per_sf'],'source_quote_extension_usd_unit':z['extended_quote_cost_usd_per_unit'],
  'purchasable_original_scope':'EXCLUDED HISTORIC NO PRIMARY NICHE' if exclusion else 'HISTORICAL QUOTED LINE ONLY',
  'actual_substitute_sku':None,'substitute_surface_allocation_sf':None,'current_supplier_usd_sf':None,
  'substitute_landed_usd_unit':None,'variance_usd':None,'confirmed_chicago_lot_stock_lead':None,
  'actual_order_cartons':None,'owner_room_cap_usd':None,'manufacturer_exact_wet_dcof_point':None,
  'actual_1529_geometry_verified':False,'owner_approved':False,'procurement_release':False,
  'next_gate':hold})
 room['R09_active_source_gross_sf']=round(active,2)
 room['R09_excluded_historic_gross_sf']=round(excluded,2)
 md+=['','## '+rid+' | '+room['status'].upper()+' | source $'+format(room['carried_quote_material_subtotal_usd_per_unit'],'.2f')+'/unit','',
 'GOOD / governing historic scope: source tile selections retained for trace. BETTER / conditional comparison: '+option+'. BEST / release target: measured SKU test and use, correctly identified geometry, complete installed bid and written owner signoff; NOT currently achieved.',
 'Existing fixture/scope: '+fixture+'. **Owner/technical first hold:** '+hold+'.',
 'Current champion: '+str(room['champion_id'])+' / '+str(room['champion_score'])+'; owner approval NULL; all purchasing released FALSE.',
 'Gross source area active '+format(active,'.2f')+' SF/unit; excluded historic niche '+format(excluded,'.2f')+' SF/unit; all rows including excluded '+format(all_gross,'.2f')+' SF/unit. Do not add waste again. Source WC already inside Primary floor; niche net-back/returns not measured.',
 '',
 '| Original quote row | Surface | Gross SF per unit | Exact historical USD/unit | Current substitute/unit delta | Status |',
 '|---|---|---:|---:|---|---|']
 for z in room['carried_tile_rows']:
  excl=rid.endswith('PRIMARY') and z['surface']=='accent'
  md.append('| '+z['smartsheet_row_id']+' | '+z['surface']+' | '+format(z['qty_sf_per_unit'],'.2f')+' | '+str(z['extended_quote_cost_usd_per_unit'])+' | null / null | '+('EXCLUDED historic Primary niche' if excl else 'SPEC+PRICE VERIFY before purchase')+' |')
 if not room['carried_tile_rows']: md.append('| no separate quote line | shared Primary level tile | 0 add-on | 0.00 | N/A independent line | inherit Primary test HOLD |')
 md+=['',
 '**Owner decision card:** Present a physical material/metal/grout sample and annotated provisional W1–W3 tile sheet. Confirm/reject only the chosen palette and material allowance after lab evidence. Ask specifically: '+hold+'. Resolve applicable missing basin and tub/shower program directly with owner; do not infer. Show qualified cost difference only when comparable complete current supplier scope, shipping and labor bids are available. Owner disposition remains NULL.',
 '**GC/technical action:** Verify actual 1529 project model/session or surveyed wet wall/door/valves/drain, compatible waterproof system, real floor/pan split, niche field deduction, joint/movement/trim LF, actual dimensional tile module and complete carton procurement. No installer release.']
md+=['','## Quantity and carton math controls','',
 'A source floor gross quantity is one pool, not field area PLUS a whole separate shower pan pool. WC is included in Primary. Two excluded Primary historical niches are 7.41 and 8.63 gross SF, both NOT purchasable and NOT added to active tile gross.',
 'As purely conditional case-yield illustrations, TX Bath2 43.7 SF source bath level floor / manufacturer Glazzio HNC6615 9.69 SF/box = CEIL(4.51)=5 full cartons (48.45 SF); TX Bath4 44.3 SF /9.69 = CEIL(4.57)=5 cartons (48.45 SF). These are NOT actual orders because HNC color/finish sample approval, exact contract SKU, measured area, project price, lot/Chicago availability and DCOF method remain pending.',
 'PH Bath4 25.6 +14.6 SF level/pan and Daltile/Glazzio case scenarios from R05-R06 are STILL hypothetical and do not settle owner 35 vs27 SF; do not transfer floor-case yields to another manufacturer.',
 'Chicago source-control: public Troy, Illinois dealer asking prices are not verified Chicago stock and cannot establish job-site landed cost. Supplier outreach, forms and purchase requests are prohibited.']
(O/'R09_13_ROOM_PROCUREMENT_DELTA_AND_OWNER_CARDS.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
with (O/'R09_27_ROW_QUOTE_TO_SELECTION_AUDIT.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
assert len(rows)==27 and sum(1 for r in rows if 'EXCLUDED HISTORIC' in r['purchasable_original_scope'])==2
assert len({r['room_id'] for r in rows})==11
assert round(sum(r['carried_quote_material_subtotal_usd_per_unit']*r['unit_count'] for r in rooms),2)==23572.44
print('PASS 13 owner cards 27 quote rows 2 excluded; 2PH+2TX historic $23572.44')

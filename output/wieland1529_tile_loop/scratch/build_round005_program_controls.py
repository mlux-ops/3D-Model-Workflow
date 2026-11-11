from pathlib import Path
import csv,json,datetime
R=Path(__file__).resolve().parents[1]; out=R/'deliverables/integrated-r05';out.mkdir(parents=True,exist_ok=True)
reg=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
sc=json.loads((R/'state/ROUND004_SCORING.json').read_text(encoding='utf-8'))['room_results']
spec={
'PH-PRIMARY':('Soft Bone v4 + unlisted Reed relief / unverified Cortar floor','Maker-wet-listed flat Bone + PF07 Cream 12x24 level/2x2 pan (held)','Test-backed floor + pan selected after exact certification, drain layout and owner samples','linear 48in, no niche'),
'PH-BATH2':('Maker-wet-listed Sapphire + Sandstone niche; Grey Soft floor','Retain Sapphire as wall baseline; Copper/Sandstone design option only; PF05 floor held','Sapphire or verified palette alternate + quantified niche, wet-tested level floor','Duravit tub, Matte White Hansgrohe'),
'PH-BATH3':('Opal tub wet-wall listing missing; Bone Soft floor','Maker-listed Sandstone walls/niche; conditional PF07 Cream floor','Future signed Sandstone plan with certified floor after tub/point-drain and basin decision','Delta DT062412 point drain conflicts with tub; basin unselected'),
'PH-BATH4':('Bone Ribbed + Clara Caviar unlisted wet use; Charcoal Soft quote','Flat Bone+Soho wet-niche; PF09 12x24 + 2x2 point pan held','Test-certified point-drain pan, measured 35/27 area, current two-format quote','Black Onyx Brizo square point; Soft/Anti-Slip conflict'),
'PH-POWDER':('Earth Lines dry wall + existing wood','Retain defended 3.69 dry relief, refine grout/mirror/faucet elevation','Owner-confirmed Earth Lines, measured centered cuts and profile schedule','Dry wall: no tiled-floor DCOF; not stable'),
'PH-WC':('Floor already inside PH Primary gross','Same Primary field finish with no separate order row','Owner-approved threshold/finish tied to valid Primary floor test','No duplicate tile area or cartons'),
'TX-PRIMARY':('Clay wet field + Ribbed relief unlisted; Cortar Soft/Anti-Slip source split','Flat maker-wet-listed Clay + PF07 12x24/2x2 concept; no niche','Accepted tested level floor/pan matching 48in linear drain and approved quantity','Round003 blocked; no primary niche'),
'TX-BATH2':('Historic tub surround + unverified floor slip','Maker-wet-listed Copper/Sandstone concept; PF07 Cream level floor pending tests','Owner basin and measured alcove; floor certified and quoted','Basin owner-unselected'),
'TX-BATH3':('Quoted tub scheme conflicts with selected point drain','Separate tub-preserving concept and shower conditional scheme without inventing pan','Owner chooses fixture program, then verified pan geometry and floor certification','Tub versus Brizo BT062415-BNX square drain'),
'TX-BATH4':('Charcoal field + unlisted wet Clara/Bone Ribbed; Bone Soft floor','Flat Charcoal/Sandstone + wet-listed Soho niche conditional','Measured tub wet enclosure, certified floor, niche deduced once','Do not transfer relief approval from flat product'),
'TX-POWDER':('Camel/Wheat Haze dry-wall mixed quote','Round003 board-accepted 70:30 Camel/Wheat dry wall, wood floor retained','Owner signed color blend/trim/faucet/mirror; exact two-color cartons','Board accepted at 3.67, not owner approved'),
'TX-POWDER2':('Indigo Edge 6x6 dry feature, wood floor','Round003 retained Indigo; optional smooth mirror backing remains unpriced/unselected','Owner basin with Hansgrohe deck faucet and quantified backing if authorized','Sink owner-unselected; deck 73072341'),
'TX-WC':('Floor already inside TX Primary gross','Same Primary level finish with no duplicate allowance','Verified shared floor threshold and certified Primary selection','No duplicate tile area or cartons')
}
assert len(spec)==len(reg)==13
rows=[];md=['# 1529 Wieland | Round 005 integrated owner selection board','',
'GOOD/BETTER/BEST are evidence tiers, not approvals. All current wet-floor schemes lack a fully accepted exact manufacturer measured numeric test and purchase-ready approval. PH $2.8M, TX $2.7M; comps $2.4M–$3.2M, 14 listings across 9 buildings; Old Town first.','',
'## 13-room detailed status / quoted material / technical selection comparison','',
'| Room | Board | Per unit old tile $ | GOOD: v4 held baseline | BETTER: conditional design only | BEST: qualified future target | Critical governing interface |',
'|---|---|---:|---|---|---|---|']
for x in reg:
  rid=x['id'];good,better,best,scope=spec[rid];status=x['status'];amount=x['carried_quote_material_subtotal_usd_per_unit'];copies=x['unit_count']
  md.append('| %s | %s | $%.2f | %s | %s | %s | %s |'%(rid,status,amount,good,better,best,scope))
  sid=sc.get(rid);score=sid['candidates'][sid['challenger_letter']]['weighted_score'] if sid else x.get('champion_score')
  excluded_primary_niche=sum(z['qty_sf_per_unit'] for z in x['carried_tile_rows'] if rid.endswith('PRIMARY') and z['surface']=='accent')
  source_all_rows_gross=sum(z['qty_sf_per_unit'] for z in x['carried_tile_rows'])
  source_active_gross=source_all_rows_gross-excluded_primary_niche
  rows.append({'room':rid,'unit_type':x['unit_type'],'copies':copies,'status':status,'champion_id':x['champion_id'] or '',
  'board_score':score if score is not None else '', 'historic_tile_material_per_unit_usd':f'{amount:.2f}',
  'historic_2_unit_total_usd':f'{amount*copies:.2f}','historic_surface_rows':len(x['carried_tile_rows']),
  'quote_gross_15pct_waste_included':'yes','source_gross_sf':f"{source_active_gross:.2f}",
  'source_all_historical_rows_gross_sf':f"{source_all_rows_gross:.2f}",
  'excluded_primary_niche_history_gross_sf':f"{excluded_primary_niche:.2f}",
  'indicative_net_before_existing_waste_sf':f"{source_active_gross/1.15:.2f}" if source_active_gross else '0',
  'new_substitution_material_cost_usd':'','installed_cost_usd':'','exact_floor_dcof_cleared':'N/A dry wall' if rid in ('PH-POWDER','TX-POWDER','TX-POWDER2') else 'NO / held with primary' if rid in ('PH-WC','TX-WC') else 'NO',
  'actual_verified_1529_geometry':'NO','current_chicago_stock_lot_lead':'','owner_approved':'NO','open_decision':scope})
md+=['','## Source-cost and quantities rule','',
'ELM September 3 2026 historic source rows are preserved at exact stored extended values: 27 source rows across one PH+one TX schedule, including TWO unpriced, expressly excluded historical Primary niche rows (PH 7.41 SF; TX 8.63 SF). CSV source_gross_sf is ACTIVE historical gross only; new source_all_historical_rows_gross_sf retains excluded lines separately and excluded_primary_niche_history_gross_sf identifies the difference. These three source totals are NOT three additive quantities. All source gross includes single 15% waste; dividing ACTIVE gross by 1.15 is an audit ratio, not measured takeoff. WC floor has no independent source tile and is already included within Primary floor gross. Costs exclude freight, labor, setting, membranes, grout, tax and alternate pricing.','',
'Historic material across two PH units: $11,591.06; two TX units: $11,981.38; complete four-unit material-only baseline $23,572.44. New proposed total, quote variance, 125%-room cap comparison and current installed project price: null (no supplier alternate prices or owner room caps).','',
'## Hard release requirements','',
'1. Exactly match every wet wall tile size/finish to the manufacturer individual Wet Areas listing. Sapphire 2x20 Glossy PASS. Tones Opal, Bone Reed/Ribbed, Clay Ribbed and Clara Caviar have unresolved or absent exact wet approval; flat Bone/Clay and Soho individual approvals do not transfer across relief.',
'2. Exact selected floor and pan SKU wet DCOF >=0.42 by acceptable specific manufacturer documentation, and geometry-compatible wet-drain assembly. Daltile PF05/PF07/PF09 maker Target >=0.42 is not an actual SKU reading. Glazzio >0.50 manufacturer lower bound is a research lead; exact test point/certificate null and not retroactively inserted into the frozen board.',
'3. Verified 1529 identity, as-built measured wall heights, openings, actual floor and pan split, niches back/returns with field-face deduction, shower curb/linear or square drain elevation, trim exposed edges and carton case sizes.',
'4. Dated local exact SKU/finish/lot supplier quote and Chicago availability/lead, tax/freight/accessory/installation total, owner room budget, documented samples and final written owner selection. No purchase or substitution made.',
'', '## Important board disposition','',
'Round004 PH Primary v4 2.83, revised 3.47 (+0.64); Bath2 v4 3.42, revised 3.45 (+0.03); Bath3 v4 2.79, revised 3.35 (+0.56); Bath4 v4 2.46, revised 3.36 (+0.90). All four remain BLOCKED by missing accepted floor wet-DCOF. No challenger accepted; Bath2 additionally fails >=+0.25; challenger cost critic below 3 in all except Bath2, where 2.8. TX Powder 70:30 Haze board decision and TX Powder2 Indigo retention from Round003 preserved. All approvals null.']
(out/'R05_OWNER_EXECUTIVE_SELECTION_BOARD.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
with (out/'R05_RELEASE_GATE_AND_QUOTE_BASIS_13_ROOMS.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
assert len(rows)==13 and sum(len(x['carried_tile_rows']) for x in reg)==27
assert round(sum(float(x['historic_2_unit_total_usd']) for x in rows),2)==23572.44
print('PASS 13 rooms, 27 source rows, exact 23572.44 historical total, all 15%-waste and release-gate fields')

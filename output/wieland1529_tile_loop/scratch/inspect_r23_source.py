"""Read-only source inventory; no original file edits."""
import csv, json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
rooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
print('13-room statuses')
for x in rooms:
 print(x['id'],x['status'],x['champion_id'],x['champion_score'],'historical_material_usd_copy',x.get('carried_quote_material_subtotal_usd_per_unit'))
focus=['PH-BATH3','TX-BATH3','PH-BATH4','PH-PRIMARY']
for room in focus:
 g=json.loads((R/'rooms'/room/'geometry.json').read_text(encoding='utf-8'))
 p=json.loads((R/'rooms'/room/'plumbing.json').read_text(encoding='utf-8'))
 print('\nFOCUS',room,'room nums',g.get('revit_room_numbers'),'floor',g.get('floor_area'),'ceiling',g.get('ceiling_height'))
 print('walls')
 for w in g.get('tiled_walls',[]):
  print(w['id'],w.get('description'),'width_ft',w.get('length',{}).get('value'),'height_ft',w.get('tiled_height',{}).get('value'),'openings',w.get('openings'),'niches',w.get('niches'))
 print('footprint',g.get('shower_or_tub_footprint'),'drain',g.get('shower_floor_drain_type'))
 print('plumbing',[(f.get('manufacturer'),f.get('model_or_sku'),f.get('finish'),f.get('description')) for f in p.get('fixtures',[])])
 print('unselected',p.get('unselected_fixtures'))
print('\nR17 25 studies rows')
with (R/'deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv').open(encoding='utf-8-sig',newline='') as f:
 rows=list(csv.DictReader(f))
 print('fields',list(rows[0]));print('count',len(rows))
 for x in rows:
  if x.get('room') in focus:print(x['room'],x.get('wall_id'),x.get('source_width_in'),x.get('tiled_height_in'),x.get('provisional_face_area_sf'),x.get('nominal_cut_study'))
print('\nR17 material rows')
with (R/'deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv').open(encoding='utf-8-sig',newline='') as f:
 rows=list(csv.DictReader(f));print('count',len(rows),'fields',list(rows[0]))
 for x in rows:
  if x.get('room') in focus:print(x['room'],x['source_row_id'],x['source_surface'],x['source_gross_sf_one_copy_waste_15pct_once'],x['historic_usd_one_copy'])
print('R22 manifest SHA',__import__('hashlib').sha256((R/'deliverables/integrated-r22-three-powder-faucet-and-shop-release/MANIFEST.json').read_bytes()).hexdigest())

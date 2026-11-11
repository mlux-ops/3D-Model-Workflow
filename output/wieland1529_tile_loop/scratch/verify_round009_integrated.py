from pathlib import Path
import json,csv,hashlib,re
R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r09'
reg=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']; ids={x['id'] for x in reg}
assert len(reg)==len(ids)==13
source27={(x['id'],z['smartsheet_row_id']):(x,z) for x in reg for z in x['carried_tile_rows']}
assert len(source27)==27
with (O/'R09_27_ROW_QUOTE_TO_SELECTION_AUDIT.csv').open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
assert len(rows)==27 and {(x['room_id'],x['source_row_id']) for x in rows}==set(source27)
for row in rows:
 x,z=source27[(row['room_id'],row['source_row_id'])]
 assert abs(float(row['source_gross_sf_already_includes_15pct'])-z['qty_sf_per_unit'])<.0001
 if z['extended_quote_cost_usd_per_unit'] is None:assert row['source_quote_extension_usd_unit'] in ('','None')
 else: assert abs(float(row['source_quote_extension_usd_unit'])-z['extended_quote_cost_usd_per_unit'])<.0001
 assert row['owner_approved']=='False' and row['procurement_release']=='False'
assert sum('EXCLUDED HISTORIC' in r['purchasable_original_scope'] for r in rows)==2
with (O/'R09_NOMINAL_WALL_CUT_REGISTER.csv').open(encoding='utf-8-sig',newline='') as f: cuts=list(csv.DictReader(f))
assert len(cuts)==25 and all(x['release']=='False' and x['verified_actual_opening']=='' for x in cuts)
for c in cuts:
 g=json.loads((R/'rooms'/c['room']/'geometry.json').read_text(encoding='utf-8'))
 w=next(w for w in g['tiled_walls'] if w['id']==c['wall'])
 assert abs(float(c['drawing_width_in'])-12*w['length']['value'])<.002
 assert abs(float(c['drawing_tiled_height_in'])-12*w['tiled_height']['value'])<.002
assert round(sum(x['carried_quote_material_subtotal_usd_per_unit']*x['unit_count'] for x in reg),2)==23572.44
assert all(x['owner_status'] is None for x in reg)
for rid in ('TX-PRIMARY','TX-BATH2','TX-BATH4'):
 x=next(x for x in reg if x['id']==rid)
 assert x['status']=='blocked' and x['champion_id'] is None and x['champion_score'] is None
for rid in ('PH-WC','TX-WC'):assert not next(x for x in reg if x['id']==rid)['carried_tile_rows']
a=(O/'R09_13_ROOM_PROCUREMENT_DELTA_AND_OWNER_CARDS.md').read_text(encoding='utf-8')
b=(O/'R09_DIMENSIONED_ROOM_LAYOUT_AND_RENDER_BRIEFS.md').read_text(encoding='utf-8')
assert all(a.count('## '+rid+' |')==1 and b.count('## '+rid+' |')==1 for rid in ids)
assert 'Sapphire' in a and 'NO NICHE' not in a or 'Sapphire' in b
p=R/'state/ROUND009_SUBMISSION.json'
if p.exists():
 sub=json.loads(p.read_text(encoding='utf-8'))
 assert sub['all_critic_scores'] is None
 assert set(sub['candidate_files'])=={'TX-PRIMARY','TX-BATH2','TX-BATH4'}
 for rid,cs in sub['candidate_files'].items():
  assert len(cs)==2
  for letter,rec in cs.items():
   content=(R/'rooms'/rid/'board/round-009/candidates'/(letter+'.md')).read_bytes()
   assert hashlib.sha256(content).hexdigest()==rec['sha256'] and len(content)==rec['bytes']
broken=[]
for f in O.glob('*.md'):
 for url in re.findall(r'\]\(([^)]+)\)',f.read_text(encoding='utf-8')):
  if not url.startswith(('http://','https://','#','mailto:')) and not (f.parent/url.split('#')[0]).exists():broken.append((f.name,url))
assert not broken,broken
m={'round':9,'status':'conditional owner/GC design and procurement comparison, not released','room_count':13,'source_quote_rows':27,'source_excluded_primary_niche_rows':2,'source_historic_2PH_2TX_USD':23572.44,'actual_wet_dcof_approved':False,'owner_selection_approved':False,'procurement_released':False,'source_1529_native_geometry_verified':False,'files':[]}
for f in sorted(O.iterdir()):
 if f.is_file() and f.name!='MANIFEST.json':m['files'].append({'file':f.name,'size':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(O/'MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
print('PASS R09 13 rooms / 25 nominal wall cuts / 27 source rows / 2 excluded niches / $23,572.44, no owner/release and no broken links; frozen board',p.exists())

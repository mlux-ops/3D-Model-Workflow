from pathlib import Path
import json,csv,re,hashlib,collections
R=Path(__file__).resolve().parents[1]; out=R/'deliverables/integrated-r05'
roomdata=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']; IDs={x['id'] for x in roomdata}
assert len(IDs)==13 and len(roomdata)==13
sc=json.loads((R/'state/ROUND004_SCORING.json').read_text(encoding='utf-8'))
submission=json.loads((R/'state/ROUND004_SUBMISSION.json').read_text(encoding='utf-8'))
assert len(sc['room_results'])==4 and sc['verification']['criterion_checks']==152 and sc['verification']['all_16_valid']
assert submission['all_critic_scores'] is None
for room,entry in sc['room_results'].items():
 assert entry['status']=='blocked' and not entry['accepted_challenger']
 actual=next(x for x in roomdata if x['id']==room)
 assert actual['champion_id'] is None and actual['owner_status'] is None and actual['board_round_004']['candidates']==entry['candidates']
 for role,rec in entry['critic_file_fingerprints'].items():
  f=R/'rooms'/room/'board/round-004'/('critic-'+role+'.md');b=f.read_bytes()
  assert len(b)==rec['bytes'] and hashlib.sha256(b).hexdigest()==rec['sha256'],(room,role)
 for letter,original in submission['candidate_files'][room].items():
  b=(R/'rooms'/room/'board/round-004/candidates'/ (letter+'.md')).read_bytes()
  assert hashlib.sha256(b).hexdigest()==original['sha256'] and len(b)==original['bytes']
csvpath=out/'CARTON_COVERAGE_AND_TAKEOFF_R05.csv'
with csvpath.open(encoding='utf-8-sig',newline='') as f: raw=list(csv.DictReader(f))
source=[x for x in raw if x['record_type']=='SOURCE_ROW'];illustrative=[x for x in raw if x['record_type']=='ILLUSTRATION_ONLY']
assert len(source)==27 and len(illustrative)==2
lookup={(x['id'],str(z['smartsheet_row_id'])):(z,x) for x in roomdata for z in x['carried_tile_rows']}
assert len(lookup)==27
for x in source:
 z,rm=lookup[(x['room'],x['Smartsheet_row_id'])]
 assert abs(float(x['source_gross_SF_unit_already_15pct_waste'])-z['qty_sf_per_unit'])<1e-7
 if z['quoted_rate_usd_per_sf'] is not None: assert abs(float(x['historical_USD_per_SF_2026_09_03'])-z['quoted_rate_usd_per_sf'])<1e-7
 if z['extended_quote_cost_usd_per_unit'] is not None: assert abs(float(x['historical_USD_per_unit_carried'])-z['extended_quote_cost_usd_per_unit'])<1e-7
assert round(sum(x['carried_quote_material_subtotal_usd_per_unit']*x['unit_count'] for x in roomdata),2)==23572.44
assert all(not x['carried_tile_rows'] for x in roomdata if x['id'].endswith('-WC'))
assert next(x for x in roomdata if x['id']=='TX-POWDER')['champion_id']=='round-003-B'
assert next(x for x in roomdata if x['id']=='TX-POWDER2')['champion_id']=='v4-TX-POWDER2'
assert next(x for x in roomdata if x['id']=='PH-POWDER')['status']=='active'
with (out/'R05_RELEASE_GATE_AND_QUOTE_BASIS_13_ROOMS.csv').open(encoding='utf-8-sig',newline='') as f: ledger=list(csv.DictReader(f))
assert {r['room'] for r in ledger}==IDs and len(ledger)==13
assert sum(float(r['historic_2_unit_total_usd']) for r in ledger)==23572.44
assert all(r['owner_approved']=='NO' and r['actual_verified_1529_geometry']=='NO' and not r['installed_cost_usd'] for r in ledger)
with (out/'R08_ROOM_EVIDENCE_CLOSEOUT_TRACKER.csv').open(encoding='utf-8-sig',newline='') as f: r08=list(csv.DictReader(f))
assert len(r08)==13 and {r['room_id'] for r in r08}==IDs
assert sum(int(r['quote_source_rows']) for r in r08)==27
assert round(sum(float(r['historic_tile_cost_usd_per_unit'])*int(r['copies']) for r in r08),2)==23572.44
assert all(r['release_allowed']=='false' and r['owner_selection_approved']=='false' and r['correct_project_1529_native_identity']=='false' for r in r08)
assert all(r['exact_wet_dcof_certificate']=='HOLD inherited Primary level floor DCOF test null/FAIL' for r in r08 if r['room_id'].endswith('-WC'))
assert all(r['exact_wet_dcof_certificate']=='N/A dry powder wood floor' for r in r08 if r['room_id'] in ('PH-POWDER','TX-POWDER','TX-POWDER2'))
files=list(out.glob('*.md'))+list((R/'research/products').glob('R05*.md'))+list((R/'research/products').glob('R06*.md'))+list((R/'research/products').glob('R07*.md'))+list((R/'research/comps').glob('R05*.md'))
broken=[]
for p in files:
 content=p.read_text(encoding='utf-8')
 for path in re.findall(r'\]\(([^)]+)\)',content):
  if path.startswith(('http://','https://','#','mailto:')):continue
  if not (p.parent/path.split('#')[0]).exists():broken.append((p.name,path))
assert not broken,broken[:10]
for filename in ['R05_OWNER_EXECUTIVE_SELECTION_BOARD.md','13_ROOM_ELEVATION_SAMPLE_AND_PATTERN_BOOK_R05.md','13_ROOM_QUOTE_VS_PROPOSED_PROCUREMENT_MATRIX_R05.md','13_ROOM_DRAIN_AND_WATERPROOF_DETAILS_R05.md','START_HERE_R05_OWNER_AND_GC.md']:
 p=out/filename;assert p.is_file() and p.stat().st_size>2000
assert (out/'R08_OWNER_GC_CLOSEOUT_ACTION_SHEETS.md').is_file()
t=(out/'R05_OWNER_EXECUTIVE_SELECTION_BOARD.md').read_text(encoding='utf-8')
assert all(t.count('| '+rid+' |')==1 for rid in IDs)
assert 'Sapphire' in t and 'Wet' in t and 'no niche' in t.lower()
index=(out/'START_HERE_R05_OWNER_AND_GC.md').read_text(encoding='utf-8')
assert 'Sapphire' in index and '23,572.44' in index and ('not owner-approved' in index.lower() or 'not construction issue' in index.lower())
manifest={'date':'2026-11-06','round':5,'owner_approved':False,'project_1529_native_geometry_verified':False,'room_count':13,'source_quote_rows':27,'critic_files':16,'criteria_verified':152,'candidate_sha_receipts':8,'historic_four_dwellings_material_usd':23572.44,'r05_deliverables':[],'linked_research':[]}
for p in sorted(out.iterdir()):
 if p.is_file() and p.name!='MANIFEST.json': manifest['r05_deliverables'].append({'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for p in sorted(list((R/'research/products').glob('R05*.md'))+list((R/'research/products').glob('R06*.md'))+list((R/'research/products').glob('R07*.md'))+list((R/'research/comps').glob('R05*.md'))):
 manifest['linked_research'].append({'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(out/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS R05 QA: 13 rooms, 27 exact supplier rows, 2 nonorderable scenarios, 16 critique hashes, 8 frozen SHA, 152 rubric scores, no broken local links, 23572.44 total; MANIFEST',len(manifest['r05_deliverables']),'outputs',len(manifest['linked_research']),'research')

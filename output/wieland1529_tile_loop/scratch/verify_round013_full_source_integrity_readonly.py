"""Read-only cross-version audit R012/R013 board, signed packages, 13-room release holds."""
from pathlib import Path
import json,hashlib,csv

ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 return hashlib.sha256(p.read_bytes()).hexdigest()
sub=json.loads((ROOT/'state/ROUND013_SUBMISSION.json').read_bytes())
fix=json.loads((ROOT/'state/ROUND013_PREDISPATCH_REVIEWER_FIX1.json').read_bytes())
assert sha(ROOT/'state/ROUND013_SUBMISSION.json')==fix['submission_sha256_after']
assert sub['critic_dispatch']=='NOT DISPATCHED' and sub['all_critic_scores'] is None
assert len(sub['candidate_files'])==3
for rid,parts in sub['candidate_files'].items():
 assert len(parts)==2
 for letter,f in parts.items():
  p=ROOT/f'rooms/{rid}/board/round-013/candidates/{letter}.md'
  assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes']
 for seat in ('market','design','build','cost'):
  assert not (ROOT/f'rooms/{rid}/board/round-013/critic-{seat}.md').exists()
assert fix['source_private_keys_unchanged']

old=json.loads((ROOT/'state/ROUND012_SCORING.json').read_bytes())
assert sha(ROOT/'state/ROUND012_SCORING.json')=='4821b98e4958852ec21263a33437ecf5d149fa9f2f5fd0784803253f2cb235fe'
orig=json.loads((ROOT/'state/ROUND012_SUBMISSION.json').read_bytes())
assert orig['all_critic_scores'] is None
coll=json.loads((ROOT/'state/ROUND012_CRITIC_COLLECTION.json').read_bytes())
assert coll['all_critic_scores'] is None
for rid,row in old['room_results'].items():
 assert row['status']=='blocked' and row['champion_id'] is None
 assert not row['owner_approved'] and not row['procurement_release']
 for c in row['candidates'].values():
  assert c['frozen_candidate_sha256'] in {d['sha256'] for d in orig['candidate_files'][rid].values()}

for version,expected in (('12',6),('13',5)):
 root=ROOT/f'deliverables/integrated-r{version}'
 m=json.loads((root/'MANIFEST.json').read_bytes())
 assert len(m['outputs'])==expected
 for name,f in m['outputs'].items():
  p=root/name
  assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],(version,name)
 assert not m['owner_approved'] and not m['procurement_release']

rooms=json.loads((ROOT/'state/ROOMS.json').read_bytes())['rooms']
assert len(rooms)==13
assert all(r['owner_status'] is None for r in rooms)
for r in rooms:
 if r['id'] in sub['candidate_files']:
  assert r['last_round']==13 and r['status']=='blocked' and r['champion_id'] is None
  assert r['board_round_010']['status']=='blocked'
  assert r['board_round_013']['all_critic_scores'] is None and r['board_round_013']['status']=='pending_blind_four_seat_critic_reports_unscored'
 if 'board_round_012' in r:
  assert r['status']=='blocked' and not r['board_round_012']['owner_approved'] and not r['board_round_012']['procurement_release']
assert round(sum(r['carried_quote_material_subtotal_usd_per_unit']*r['unit_count'] for r in rooms),2)==23572.44
print('PASS 6 R013 frozen corrected SHA and bytes, 6 R012 original candidate fingerprints referenced, 6 R12 + 5 R13 signed owners verified; 13 rooms, no owner approval/release, source USD 23572.44, R013 scores NULL')

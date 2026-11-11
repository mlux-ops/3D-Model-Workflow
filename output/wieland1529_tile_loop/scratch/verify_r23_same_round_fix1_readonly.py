"""Read-only independent local post-Reviewer FIX1 invariants, not a Reviewer verdict."""
from pathlib import Path
import hashlib,json,csv,re
from decimal import Decimal

R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc'
sha=lambda p: {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':len(p.read_bytes())}
M=O/'MANIFEST.json';manifest=json.loads(M.read_text(encoding='utf-8'))
assert sha(M)['sha256']=='81932937b1b7c9eae11cfda68a2e62661b6b41bbd6a21c2a7fc8d42b90608025'
assert len(manifest['outputs'])==9
for name,s in manifest['outputs'].items():assert sha(O/name)==s
fix=json.loads((R/'state/ROUND023_REVIEWER_PROGRAM_SPECIFIC_SAME_PACKAGE_FIX1.json').read_text(encoding='utf-8'))
assert fix['old_manifest']['sha256']=='2eec511f9b6920fd7553e634a1178b85f43f72bf4abb26a832114bc8d7a80ee5'
assert fix['new_manifest']['sha256']==sha(M)['sha256']
assert len(fix['changed_only_three_R23_outputs'])==3 and len(fix['other_six_R23_files_byte_SHA_unchanged'])==6

def table(file):
 with (O/file).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
actions=table('R23_65_ROOM_TRADE_ACTIONS_REVIEW_BRIDGE_NEW_COPY.csv')
assert len(actions)==65
rooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
ids={x['id'] for x in rooms}
assert len(ids)==13 and {x['room'] for x in actions}==ids
assert len({(x['room'],x['workstream']) for x in actions})==65

groups={
 'powder':{'PH-POWDER','TX-POWDER','TX-POWDER2'},
 'wc':{'PH-WC','TX-WC'},
 'tub':{'PH-BATH2','TX-BATH2','TX-BATH4'},
 'branch':{'PH-BATH3','TX-BATH3'},
 'point':{'PH-BATH4'},
 'linear':{'PH-PRIMARY','TX-PRIMARY'}
}
assert set.union(*groups.values())==ids
def get(room,cat):return next(x['specific_action'] for x in actions if x['room']==room and x['workstream']==cat)
for r in ids:
 assert all(x['approved']=='FALSE' and x['procurement_release']=='FALSE' for x in actions if x['room']==r)
 if r in groups['powder']:
  assert 'N/A' in get(r,'maker_lab') and 'wet LEVEL/PAN' in get(r,'maker_lab') or ('N/A' in get(r,'maker_lab') and 'wet floor LEVEL/PAN' in get(r,'maker_lab'))
  assert 'W1 ONLY' in get(r,'field_geometry') and 'no W3' in get(r,'field_geometry')
  assert 'shower' in get(r,'waterproofing_shop').lower() and ('no ' in get(r,'waterproofing_shop').lower() or 'not ' in get(r,'waterproofing_shop').lower())
 if r in groups['wc']:
  assert any(s in get(r,'maker_lab') for s in ['inherits','inherit','same exact individual wet LEVEL tile/raw laboratory report in parent'])
  assert 'no W1-W3' in get(r,'field_geometry') or 'NO independent W1-W3' in get(r,'field_geometry')
  assert re.search(r'no (tiled )?shower',get(r,'waterproofing_shop'),re.I)
 if r in groups['tub']:
  assert 'PAN N/A' in get(r,'maker_lab') or 'PAN N/A' in get(r,'maker_lab').upper()
  assert re.search(r'no (tiled )?shower',get(r,'waterproofing_shop'),re.I)
 if r in groups['branch']:
  assert 'TUB' in get(r,'waterproofing_shop') and 'WALK-IN' in get(r,'waterproofing_shop')
  assert 'POINT' in get(r,'maker_lab') and 'LEVEL' in get(r,'maker_lab')
 if r in groups['point']:
  assert 'BT062415-BNX SQUARE POINT' in get(r,'owner_selection')
  assert 'flood' in get(r,'waterproofing_shop')
 if r in groups['linear']:
  assert '48-in' in get(r,'owner_selection')
  assert 'NO' in get(r,'maker_lab') or 'no' in get(r,'maker_lab')

sample=(O/'R23_13_ROOM_1TO1_SAMPLE_RENDER_SHOP_AND_PRICE_ORIGINS.md').read_text(encoding='utf-8')
cards={}
for line in sample.splitlines():
 if line.startswith('| '):
  cells=[x.strip() for x in line.strip().strip('|').split('|')]
  if cells and cells[0] in ids:
   assert len(cells)==4
   cards[cells[0]]=cells
assert len(cards)==13
for r,c in cards.items():
 txt=' | '.join(c)
 assert 'FALSE' in txt
 if r in groups['powder']:
  assert 'W1' in txt and 'no W3' in txt and 'shower' in txt.lower() and ('no ' in txt.lower() or '/shower' in txt.lower())
 if r in groups['wc']:
  assert 'NO W1/W3' in txt or 'no W1/W3' in txt or 'no W1' in txt
 if r in groups['tub']:
  assert 'no tiled' in txt.lower() or 'NO PAN' in txt
 if r in groups['linear']:
  assert 'no W3/niche' in txt or 'NO W3/niche' in txt
 if r in groups['branch']:
  assert 'TUB' in txt and 'WALK-IN' in txt

owner=(O/'R23_ALL_13_ROOM_GOOD_BETTER_BEST_OWNER_DECISION_BOOK.md').read_text(encoding='utf-8')
assert owner.count('**Approval boundary:**')==13
for rid in groups['powder']:
 segment=owner[owner.index('## '+rid)+len('## '+rid):].split('\n## ',1)[0]
 assert 'N/A' in segment and 'WOOD' in segment
for rid in groups['wc']:
 segment=owner[owner.index('## '+rid)+len('## '+rid):].split('\n## ',1)[0]
 assert 'ONCE' in segment and 'no WC wet WALL/NICHE or PAN requirement' in segment

for file,count in [('R23_13_ROOM_SKU_WET_WALL_NICHE_LEVEL_PAN_RELEASE_MATRIX.csv',13),('R23_25_W1_W3_PROVISIONAL_ELEVATIONS_NET_TRIM_MOVEMENT_CUT_SHOP.csv',25),('R23_27_HISTORICAL_ROWS_TO_NET_CARTON_COST_PROVENANCE_CONTROL.csv',27),('R23_8_WET_UNIT_INSTANCE_OWNER_TRADE_WITNESS_CHECKPOINTS.csv',8)]:assert len(table(file))==count
orig=table('R23_27_HISTORICAL_ROWS_TO_NET_CARTON_COST_PROVENANCE_CONTROL.csv')
assert sum(Decimal(x['historic_usd_two_copies']) for x in orig if x['historic_usd_two_copies'])==Decimal('23572.44')
assert sum(1 for x in orig if x['historic_niche_excluded_no_scope']=='TRUE')==2
assert all(x['procurement_release']=='FALSE' for x in orig)
assert manifest['owner_approval'] is False and manifest['GC_release'] is False and manifest['procurement_release'] is False
assert sha(R/'deliverables/integrated-r22-three-powder-faucet-and-shop-release/MANIFEST.json')['sha256']=='32e5ceb807e33e642680dec47aa378d21d5ba9f7b05462214277cb89e7d76df1'
print('PASS R23 same-round FIX1 local content QA: 9 signed outputs, 65 program-specific action rows, 13 distinct room sample/camera rows, 13 N/A/inherited owner approvals, 13/25/27/8 source schedules, $23,572.44 old materials and all release FALSE')
print('R23_SHA',sha(M)['sha256'])

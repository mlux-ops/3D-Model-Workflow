"""Integrate the original R035 four-seat Duravit-tub board without rewriting history.

Run once after twelve authentic critic files pass r035_board_arithmetic.py.
This changes only state/ROOMS.json; additive room records, packet and LEDGER follow.
"""
from pathlib import Path
from decimal import Decimal
import copy
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'state' / 'ROOMS.json'
payload = json.loads(subprocess.run(
    [sys.executable, '-B', str(ROOT / 'scratch' / 'r035_board_arithmetic.py')],
    capture_output=True, text=True, check=True
).stdout)
assert (payload['criterion_count'], payload['seat_means_count'], payload['weighted_count']) == (114, 24, 6)

# The sealed incumbent keys are consulted only AFTER all blind specialist reports exist.
spec = {
    'PH-BATH2': dict(inc='round-031-A', old='3.880', incletter='A', challenger='B',
                     current='3.670', other='3.600', new='round-031-A', cost_a='789.23', cost_b='679.54'),
    'TX-BATH2': dict(inc='round-031-B', old='3.850', incletter='B', challenger='A',
                     current='3.590', other='3.470', new='round-031-B', cost_a='879.30', cost_b='845.46'),
    'TX-BATH4': dict(inc='round-031-B', old='3.650', incletter='A', challenger='B',
                     current='3.350', other='3.630', new='round-035-B', cost_a='583.04', cost_b='572.89'),
}
current = json.loads(STATE.read_text(encoding='utf-8-sig'))
assert len(current['rooms']) == 13
assert sum(r['unit_count'] for r in current['rooms']) == 26
assert sum(len(r['carried_tile_rows']) for r in current['rooms']) == 27
assert sum(Decimal(str(r['carried_quote_material_subtotal_usd_per_unit'])) *
           r['unit_count'] for r in current['rooms']) == Decimal('23572.44')
carried_snapshot = {r['id']: copy.deepcopy(r['carried_tile_rows']) for r in current['rooms']}
original_fields = {r['id']: (r['unit_count'], r['carried_quote_material_subtotal_usd_per_unit'],
                               r['carried_budget_material_only_usd_per_unit'], r['owner_status'])
                   for r in current['rooms']}

for room_id, e in spec.items():
    r = next(r for r in current['rooms'] if r['id'] == room_id)
    assert r['status'] == 'provisional champion' and r['champion_id'] == e['inc']
    assert Decimal(str(r['champion_score'])) == Decimal(e['old'])
    assert r['last_round'] == 31 and r['owner_status'] is None
    assert r['board_round_031']['decision'] == 'provisional_champion_' + e['inc'][-1]
    key = json.loads((ROOT/'rooms'/room_id/'board'/'round-035'/'_key.json').read_text(encoding='utf-8'))
    assert key['previous_genuine_provisional_board_incumbent_letter'] == e['incletter']
    assert key['new_challenger_letter'] == e['challenger']
    assert key['existing_provisional_champion_identity'] == e['inc']
    x = payload['room_boards'][room_id]
    assert Decimal(x[e['incletter']]['weighted']) == Decimal(e['current'])
    assert Decimal(x[e['challenger']]['weighted']) == Decimal(e['other'])
    assert all(x[k]['specialist_gate_pass'] for k in ('A', 'B'))
    assert all(Decimal(x[k]['minimum_seat']) >= 3 for k in ('A','B'))
    for k in ('A', 'B'):
        source = (ROOT/'rooms'/room_id/'board'/'round-035'/'candidates'/(k+'.md')).read_text(encoding='utf-8')
        low = source.casefold()
        assert all(term in low for term in ('duravit', 'tub', 'no tiled shower pan', 'dcof', 'niche', 'wet'))
    margin = Decimal(e['other']) - Decimal(e['current'])
    displace = margin >= Decimal('0.250')
    assert displace == (room_id == 'TX-BATH4')
    e['decision'] = ('replace_with_R035_challenger_B' if displace else 'retain_genuine_R031_incumbent')
    r['last_round'] = 35
    r['champion_id'] = e['new']
    r['champion_score'] = float(Decimal(e['other']) if displace else Decimal(e['current']))
    r['board_round_035'] = {
        'status': 'genuine_four_seat_strict_blind_product_board_provisional',
        'source': 'state/ROUND035_THREE_DURAVIT_TUB_BOARD_DECISIONS_20261107.md',
        'workers': {'market':69, 'design':70, 'build':71, 'cost':72},
        'weights': {'market':.30, 'design':.25, 'build':.25, 'cost':.20},
        'original_criterion_count_cohort':114,
        'previous_provisional_champion_id': e['inc'],
        'previous_champion_score_historical':float(Decimal(e['old'])),
        'incumbent_letter_private_after_blind_collection':e['incletter'],
        'challenger_letter_private_after_blind_collection':e['challenger'],
        'defense_threshold':.25,
        'challenger_minus_incumbent_same_round':float(margin),
        'decision':e['decision'],
        'selected_champion_id':e['new'],
        'candidates':{k:{'seat_scores':{s:float(x[k][s]['mean']) for s in ('market','design','build','cost')},
                          'weighted_score':float(Decimal(x[k]['weighted'])),
                          'minimum_seat':float(Decimal(x[k]['minimum_seat'])),
                          'all_specialists_at_least_3':True,
                          'legacy_material_rate_screen_per_copy_usd':float(Decimal(e['cost_'+k.lower()])),
                          'owner_approved':False} for k in ('A','B')},
        'technical_product_gates':'Exact named allowed-vendor wet tub WALL/vertical niche and bath LEVEL floor maker permissions/DCOF>=0.42 PASS; tub PAN, POINT drain and tiled ceiling N/A; full horizontal niche sill, flange and installed assembly NOT released',
        'original_waste_15_percent':'historical gross includes once; no duplicate or extra pan',
        'open_items':['tub actual rough/finished opening, flange, overflow, waterproof membrane and niche sill positive fall',
                      'door/niche and 3-inch visible edge cut layout, floor flatness and substrate',
                      'Chicago exact SKU matching lot, local stock, lead time and landed plus installed costs',
                      'owner room budget FILL IN, real samples and final owner tile approval']+
                     (['TX-BATH2 ~59-in Duravit vs 59.496-in drawing opening: fit unresolved',
                       'TX-BATH2 basin owner UNSELECTED'] if room_id=='TX-BATH2' else []),
        'owner_approved':False,
        'procurement_released':False,
    }
    extra = 'R035 current gates: wet tile maker use and LEVEL DCOF verified; tub flange/niche horizontal sill, field dimensions/cuts, Chicago lot/landed, FILL IN budget and owner signature remain open; no tiled PAN.'
    if extra not in r['open_gaps']:
        r['open_gaps'].append(extra)

assert all(r['carried_tile_rows'] == carried_snapshot[r['id']] for r in current['rooms'])
assert all((r['unit_count'], r['carried_quote_material_subtotal_usd_per_unit'],
            r['carried_budget_material_only_usd_per_unit'],r['owner_status']) == original_fields[r['id']]
           for r in current['rooms'])
assert sum(r['status']=='provisional champion' for r in current['rooms']) == 9
assert sum(r['status']=='blocked' for r in current['rooms']) == 4
assert all(next(r for r in current['rooms'] if r['id']==wc)['champion_id'] is None for wc in ('PH-WC','TX-WC'))
assert sum(Decimal(str(r['carried_quote_material_subtotal_usd_per_unit'])) *
           r['unit_count'] for r in current['rooms']) == Decimal('23572.44')
STATE.write_text(json.dumps(current, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
for room_id,e in spec.items():
    print(room_id, 'DECISION',e['decision'], 'INCUMBENT_R035', e['current'],
          'CHALLENGER_R035',e['other'],'CHAMPION',e['new'])
print('PASS R035 authentic 114/24/6; 1 material-scheme change, 2 defended, 13/26/27/$23572.44/9 provisional+4 blocked/0 approvals')

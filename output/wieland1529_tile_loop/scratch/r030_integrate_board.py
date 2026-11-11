from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
path = ROOT/'state'/'ROOMS.json'
raw = path.read_text(encoding='utf-8-sig')
doc = json.loads(raw)
assert len(doc['rooms']) == 13
by = {r['id']:r for r in doc['rooms']}
assert len(by)==13
results = {
 'PH-PRIMARY': {'A': (4.3,4.2,3.6,3.0,3.840), 'B': (3.6,3.4,3.2,3.6,3.450)},
 'TX-PRIMARY': {'A': (4.2,4.2,3.6,3.0,3.810), 'B': (4.0,3.4,3.0,2.8,3.360)},
 'PH-BATH4': {'A': (4.2,4.0,3.0,2.8,3.570), 'B': (3.9,3.6,3.2,3.4,3.550)},
 'PH-BATH3': {'A': (4.3,3.8,3.6,3.2,3.780), 'B': (3.9,3.6,3.4,3.4,3.600)}
}
for room,candidates in results.items():
 r=by[room]
 assert r['owner_status'] is None and r['status']=='blocked'
 r['last_round']=30
 r['board_round_030']={
  'status':'authentic_four_seat_scored',
  'source':'state/ROUND030_FOUR_ROOM_BOARD_DECISIONS.md',
  'workers':{'market':63,'design':64,'build':65,'cost':66},
  'seat_weights':{'market':.30,'design':.25,'build':.25,'cost':.20},
  'candidates':{k:{'seat_scores':dict(zip(('market','design','build','cost'),v[:4])),'weighted_score':v[4],
     'all_seats_at_least_3':min(v[:4])>=3.0,'product_wet_wall_floor_pan_gates':'pass',
     'owner_approved':False,'procurement_authorized':False} for k,v in candidates.items()},
 }
 r['board_round_030']['real_accepted_incumbent_existed']=False
 r['board_round_030']['challenger_margin_rule_applied']=False
 if room=='PH-BATH4':
  r['status']='provisional champion'
  r['champion_id']='round-030-B'
  r['champion_score']=3.55
  r['board_round_030']['decision']='provisional_champion_B_A_cost_below_3'
  r['board_round_030']['open_items']=['POINT pan real cuts and drain interface','niche sill/returns/trim/waterproof assembly','35-vs-27-SF floor quantity','Chicago lot/ETA/landed cost','owner budget FILL IN','owner final approval']
 elif room=='PH-BATH3':
  r['status']='provisional champion'
  r['champion_id']='round-030-A'
  r['champion_score']=3.78
  r['board_round_030']['decision']='provisional_champion_A_branch_neutral'
  r['board_round_030']['open_items']=['TUB vs WALK-IN unselected','basin unselected','conditional POINT pan net/rough and waterproof','niche waterproof/edge','Chicago lot/ETA/landed','owner budget FILL IN','owner approval']
 else:
  r['board_round_030']['decision']='surface_qualified_candidate_A_room_blocked_tiled_ceiling_technical'
  r['board_round_030']['surface_preference']='A'
  r['board_round_030']['open_items']=['shower tiled CEILING independently unqualified: manufacturer overhead/assembly required','native layout/drain cuts','Chicago lot/ETA/landed','owner budget FILL IN']
  # Do not invent full-room champion while actual shower ceiling is unspecified.
  r['status']='blocked'
  r['champion_id']=None
  r['champion_score']=None
assert sum(r['status']=='provisional champion' for r in doc['rooms'])==2
assert all(r['owner_status'] is None for r in doc['rooms'] if r['id'] in results)
new=json.dumps(doc,indent=2,ensure_ascii=False)+'\n'
json.loads(new)
path.write_text(new,encoding='utf-8')
print('UPDATED 13 ROOMS; provisional PH-BATH4 B=3.55, PH-BATH3 A=3.78; primary ceilings remain blocked')

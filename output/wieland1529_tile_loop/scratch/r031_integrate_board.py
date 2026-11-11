from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'state'/'ROOMS.json'
doc=json.loads(path.read_text(encoding='utf-8-sig'))
assert len(doc['rooms'])==13
R={
'PH-BATH2':{'pick':'A','score':3.880,'A':(4.3,4.0,3.8,3.2,3.880),'B':(4.2,3.8,3.8,3.2,3.800)},
'TX-BATH2':{'pick':'B','score':3.850,'A':(4.1,3.8,3.4,3.0,3.630),'B':(4.4,4.0,3.4,3.4,3.850)},
'TX-BATH3':{'pick':'B','score':3.830,'A':(4.3,4.0,3.6,3.2,3.830),'B':(4.2,3.8,3.6,3.6,3.830)},
'TX-BATH4':{'pick':'B','score':3.650,'A':(4.1,3.8,3.4,2.8,3.590),'B':(3.9,3.8,3.4,3.4,3.650)}
}
for room,rr in R.items():
 r=next(x for x in doc['rooms'] if x['id']==room)
 assert r['status']=='blocked' and r['owner_status'] is None and r['champion_id'] is None,(room,r['status'])
 r['status']='provisional champion'
 r['last_round']=31
 r['champion_id']='round-031-'+rr['pick']
 r['champion_score']=rr['score']
 r['board_round_031']={
  'status':'authentic_four_seat_scored',
  'source':'state/ROUND031_FOUR_ROOM_BOARD_DECISIONS.md',
  'workers':{'market':63,'design':64,'build':65,'cost':66},
  'weights':{'market':.30,'design':.25,'build':.25,'cost':.20},
  'real_accepted_incumbent_existed':False,
  'challenger_margin_rule_applied':False,
  'candidates':{c:{'seat_scores':dict(zip(('market','design','build','cost'),rr[c][:4])),'weighted_score':rr[c][4], 'seat_minimum_pass':min(rr[c][:4])>=3.0, 'technical_product_gates':'exact manufacturer wet wall and LEVEL and conditional PAN approved', 'owner_approved':False,'procurement_release':False} for c in ('A','B')},
  'decision':'provisional_champion_'+rr['pick'],
  'ties':'B selected on lower tile-material-only cost among equal 3.830 scores' if room=='TX-BATH3' else None,
  'open_items':['actual floor/niche layout, sill/edge/waterproof assembly','Chicago matching lot/ETA, freight, all-in landed price','owner tile budget FILL IN and approval']+(['owner TUB versus WALK-IN unselected; conditional POINT PAN net and cost null'] if room=='TX-BATH3' else [])+(['basin unselected'] if room=='TX-BATH2' else [])
 }
assert sum(x['status']=='provisional champion' for x in doc['rooms'])==6
assert sum(x['status']=='blocked' for x in doc['rooms'])==2
path.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS: R031 4 provisional champions added; six total provisional, two Primary ceiling blocked, three active, two WC seeded; owner approved ZERO')

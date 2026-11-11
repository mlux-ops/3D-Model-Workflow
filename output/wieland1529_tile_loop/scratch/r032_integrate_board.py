from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'state'/'ROOMS.json'
d=json.loads(path.read_text(encoding='utf-8-sig'))
assert len(d['rooms'])==13
R={
'PH-POWDER':('v4-PH-POWDER',3.69,3.86,{'A':(4.4,4.2,3.4,3.2,3.86),'B':(4.1,4.0,3.8,3.4,3.86)}),
'TX-POWDER':('round-003-B',3.67,3.64,{'A':(4.3,3.8,3.2,3.0,3.64),'B':(4.0,3.6,3.8,3.4,3.73)}),
'TX-POWDER2':('v4-TX-POWDER2',3.23,3.78,{'A':(4.3,4.0,3.4,3.2,3.78),'B':(4.1,4.0,3.8,3.4,3.86)}),
}
for id,(inc,old,score,candidates) in R.items():
 r=next(x for x in d['rooms'] if x['id']==id)
 assert r['status']=='active' and r['champion_id']==inc and abs(r['champion_score']-old)<.001 and r['owner_status'] is None,(id,r['champion_id'],r['champion_score'])
 assert candidates['B'][4]-candidates['A'][4] < .25
 r['last_round']=32
 r['status']='provisional champion'
 r['champion_score']=score
 r['board_round_032']={
  'source':'state/ROUND032_THREE_POWDER_FOUR_SEAT_DECISIONS.md',
  'status':'authentic_four_seat_blind_replacement_build',
  'workers':{'market':63,'design':64,'build_replacement':68,'cost':66},
  'excluded_build_worker65':'disclosed exposure to prior outcomes in linked research aggregator; NOT used in current score',
  'weights':{'market':.30,'design':.25,'build':.25,'cost':.20},
  'genuine_historical_board_incumbent_id':inc,'historical_predecessor_score':old,
  'current_incumbent_letter':'A','challenger_letter':'B',
  'challenger_margin_required':.25,'challenger_margin_actual':round(candidates['B'][4]-candidates['A'][4],3),
  'decision':'retain incumbent A; no +0.25 challenge displacement; dry wall only',
  'candidates':{c:{'seat_scores':dict(zip(('market','design','build_replacement','cost'),vals[:4])),'weighted_score':vals[4],'seat_minimum_pass':min(vals[:4])>=3.0,'owner_approved':False} for c,vals in candidates.items()},
  'open_items':['dry wall mirror/cabinet/trim/fixture coordinate and actual maker tile thickness','current Chicago lot/ETA/landed cost','owner budget FILL IN','final owner approval']+(['TX faucet visible finish unknown'] if id=='TX-POWDER' else [])+(['TX-POWDER2 basin owner unselected; suffix341 Brushed Black Chrome'] if id=='TX-POWDER2' else [])
 }
assert sum(x['status']=='provisional champion' for x in d['rooms'])==9
assert sum(x['status']=='blocked' for x in d['rooms'])==2
assert sum(x['status']=='seeded' for x in d['rooms'])==2
path.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS: 9 provisional, 2 Primaries blocked, 2 WCs inherited seeded; 3 preserved incumbent identities; zero owner approvals')

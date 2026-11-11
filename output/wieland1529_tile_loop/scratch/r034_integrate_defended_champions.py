"""Guarded R034 score integration for three defended provisional tile schemes.

Historic champion identities, original material rows and owner decisions preserved.
No procurement / owner release or cross-room geometry changes.
"""
from pathlib import Path
from decimal import Decimal
import json,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'state'/'ROOMS.json'
d=json.loads(path.read_text(encoding='utf-8-sig'))
assert len(d['rooms'])==13
assert sum(x['unit_count'] for x in d['rooms'])==26
assert sum(len(x['carried_tile_rows']) for x in d['rooms'])==27
cmd=subprocess.run([sys.executable,'-B',str(ROOT/'scratch'/'r034_board_arithmetic.py')],capture_output=True,text=True,check=True)
data=json.loads(cmd.stdout)
assert data['criterion_count']==114 and data['seat_means_count']==24 and data['weighted_count']==6
R={
 'PH-BATH4':('round-030-B',Decimal('3.55'),'A',Decimal('3.370'),'B',Decimal('3.570')),
 'PH-BATH3':('round-030-A',Decimal('3.78'),'B',Decimal('3.570'),'A',Decimal('3.490')),
 'TX-BATH3':('round-031-B',Decimal('3.83'),'A',Decimal('3.590'),'B',Decimal('3.630'))
}
for id,(inc,old,letter,score,challenge,other) in R.items():
 r=next(x for x in d['rooms'] if x['id']==id)
 assert r['status']=='provisional champion' and r['champion_id']==inc and Decimal(str(r['champion_score']))==old,(id,r['status'],r['champion_id'],r['champion_score'])
 assert r['owner_status'] is None
 x=data['room_boards'][id]
 assert Decimal(x[letter]['weighted'])==score and Decimal(x[challenge]['weighted'])==other
 assert x[letter]['specialist_gate_pass'] and x[challenge]['specialist_gate_pass']
 assert other-score<Decimal('.250'),id
 r['last_round']=34
 r['champion_score']=float(score)
 r['board_round_034']={
  'status':'genuine_four_seat_strict_blind_scored_defended_provisional',
  'source':'state/ROUND034_THREE_WET_BATH_BLIND_BOARD_DECISIONS_20261107.md',
  'workers':{'market':69,'design':70,'build':71,'cost':72},
  'weights':{'market':.30,'design':.25,'build':.25,'cost':.20},
  'original_criterion_count_cohort':114,
  'previous_provisional_champion_id':inc,
  'previous_champion_score_historical':float(old),
  'current_incumbent_letter_private_after_blind_collection':letter,
  'current_challenger_letter_private_after_blind_collection':challenge,
  'true_boarded_incumbent_defense_margin':.25,
  'challenger_minus_incumbent_weighted':float(other-score),
  'decision':'retain existing genuine provisionally boarded incumbent; 0.25 replacement margin not reached',
  'candidates':{k:{'seat_scores':{s:float(x[k][s]['mean']) for s in ('market','design','build','cost')},
                   'weighted_score':float(x[k]['weighted']),
                   'all_specialists_at_least_3':x[k]['specialist_gate_pass'],
                   'owner_approved':False} for k in ('A','B')},
  'tile_product_gates':'exact maker wet WALL, floor DCOF>=.42, floor Shower Floor independent permission PASS; assembly/field geometry/owner/commercial holds continue',
  'owner_approved':False,'procurement_released':False,
  'original_waste_15_percent':'included once; never add again',
  'open_items':['actual room wall/niche/door cuts and floor/pan geometries','niche waterproof assembly and sill fall',
                'Chicago lots, ETA, delivered price and complete installed cost','owner budget FILL IN','final owner approval']+
               (['PH4 owner 35 SF floor vs earlier 27 SF conflict'] if id=='PH-BATH4' else
                ['TUB versus WALK-IN owner UNSELECTED; WALK-IN pan SF and cost NULL','PH3 basin UNSELECTED'] if id=='PH-BATH3' else
                ['TUB versus WALK-IN owner UNSELECTED; conditional BNX point PAN SF and cost NULL'])
 }
assert sum(x['status']=='provisional champion' for x in d['rooms'])==9
assert sum(x['status']=='blocked' for x in d['rooms'])==4
assert all(x['owner_status'] is None for x in d['rooms'])
assert all(next(x for x in d['rooms'] if x['id']==wc)['champion_id'] is None for wc in ('PH-WC','TX-WC'))
path.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS R034 integrated: three genuine provisional incumbents defended, 13/26/27; 9 provisional, 4 blocked, no owner approval or WC duplicate')

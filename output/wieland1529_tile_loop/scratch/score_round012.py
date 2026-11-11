"""Score original R012 frozen independent board in a distinct continuation.
Only creates new scored receipt. All original source/dispatch/critic fingerprints immutable.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import hashlib,json,re
R=Path(__file__).resolve().parents[1]
sp=R/'state/ROUND012_SUBMISSION.json'
dp=R/'state/ROUND012_CRITIC_DISPATCH.json'
cp=R/'state/ROUND012_CRITIC_COLLECTION.json'
source=json.loads(sp.read_text(encoding='utf-8'))
dispatch=json.loads(dp.read_text(encoding='utf-8'))
collection=json.loads(cp.read_text(encoding='utf-8'))
assert source['round']==dispatch['round']==collection['round']==12
assert all(v['phase']=='2-board' and v['all_critic_scores'] is None for v in (source,dispatch,collection))
assert collection['weighted_scoring_complete'] is False and dispatch['scoring_deferred_to_next_distinct_turn']
assert dispatch['source_submission_sha256']==hashlib.sha256(sp.read_bytes()).hexdigest()
assert collection['source_submission_sha256']==hashlib.sha256(sp.read_bytes()).hexdigest()
assert collection['source_dispatch_sha256']==hashlib.sha256(dp.read_bytes()).hexdigest()
assert set(source['candidate_files'])==set(collection['report_files'])=={'TX-PRIMARY','TX-BATH2','TX-BATH4'}
seats={'market':(Decimal('.30'),4),'design':(Decimal('.25'),5),'build':(Decimal('.25'),5),'cost':(Decimal('.20'),5)}
reported={'TX-PRIMARY':{'B':{'market':3.5,'design':3.0,'build':2.0,'cost':2.4},'C':{'market':3.7,'design':3.8,'build':2.6,'cost':2.2}},
 'TX-BATH2':{'A':{'market':3.7,'design':4.0,'build':3.0,'cost':2.6},'C':{'market':3.7,'design':3.4,'build':2.6,'cost':2.8}},
 'TX-BATH4':{'A':{'market':3.4,'design':2.8,'build':2.4,'cost':2.2},'B':{'market':3.7,'design':3.8,'build':2.8,'cost':2.4}}}
dest=R/'state/ROUND012_SCORING.json'
assert not dest.exists(),'Scored receipt already exists; do not rewrite.'
result={'round':12,'as_of':'2026-11-06','scoring_turn':'distinct successor to frozen R012 submission and independent worker-11 CONTINUE clearance','source_submission':'state/ROUND012_SUBMISSION.json','source_submission_sha256':hashlib.sha256(sp.read_bytes()).hexdigest(),
 'source_dispatch_sha256':hashlib.sha256(dp.read_bytes()).hexdigest(),'source_collection_sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),
 'reviewer_clearance':'worker-11 non-Pro CONTINUE after 12-critique and R12B SHA audit; formal scoring NEXT DISTINCT prime turn',
 'rubric_weights':{k:float(w) for k,(w,_) in seats.items()},
 'verification':{'frozen_candidates':0,'original_critics':0,'criteria':0,'recalculated_seat_means':0,'local_links':0,'valid':False},
 'room_results':{}}
for rid,letters in source['candidate_files'].items():
 roomdir=R/'rooms'/rid/'board/round-012'
 keys=json.loads((roomdir/'_key.json').read_text(encoding='utf-8'))
 assert set(keys)==set(letters)
 historical=next(k for k,v in keys.items() if 'historic' in v.lower())
 revised=next(k for k in keys if k!=historical)
 for letter,record in letters.items():
  b=(roomdir/'candidates'/f'{letter}.md').read_bytes()
  assert record['sha256']==hashlib.sha256(b).hexdigest() and record['bytes']==len(b)
  result['verification']['frozen_candidates']+=1
 score={k:{} for k in letters}
 criteria={k:{} for k in letters}
 sha={}
 for seat,(weight,required) in seats.items():
  f=roomdir/f'critic-{seat}.md'
  b=f.read_bytes();t=b.decode('utf-8')
  ref=collection['report_files'][rid][seat]
  assert ref['sha256']==hashlib.sha256(b).hexdigest() and ref['bytes']==len(b)
  assert ref['worker']==dispatch['critic_worker_seats'][f'critic-{seat}']
  assert not re.search(r'(?i)_key\.json|state/ROOMS\.json|state/LEDGER\.md',t)
  sha[seat]=ref
  result['verification']['original_critics']+=1
  for link in re.findall(r'\]\(([^)]+)\)',t):
   if link.startswith(('https://','http://','#','mailto:')):continue
   assert (f.parent/link.split('#')[0]).exists(),(rid,seat,link)
   result['verification']['local_links']+=1
  blocks=re.split(r'(?im)^##\s+Candidate\s+([A-Z])\b[^\n]*\n',t)
  assert len(blocks)==5 and set(blocks[1::2])==set(letters)
  for letter,block in zip(blocks[1::2],blocks[2::2]):
   vals=[]
   for line in block.splitlines():
    if not line.startswith('|'):continue
    cells=[c.strip() for c in line.strip('|').split('|')]
    if len(cells)!=3:continue
    v=re.sub(r'\s*/\s*5(?:\.0)?\s*$','',cells[1].replace('*','')).strip()
    if re.fullmatch(r'[1-5](?:\.\d+)?',v):
     assert len(cells[2])>35 and ('[' in cells[2] or 'http' in cells[2])
     vals.append(Decimal(v))
   assert len(vals)==required,(rid,letter,seat)
   assert all(k in block.lower() for k in ('top_fix','gate_flags','confidence'))
   mean=(sum(vals,Decimal('0'))/Decimal(required)).quantize(Decimal('.1'),rounding=ROUND_HALF_UP)
   assert mean==Decimal(str(reported[rid][letter][seat])),(rid,letter,seat,mean)
   score[letter][seat]=float(mean)
   criteria[letter][seat]={'values':[float(v) for v in vals],'arithmetic_mean':float(mean)}
   result['verification']['criteria']+=required
   result['verification']['recalculated_seat_means']+=1
 row={'room':rid,'round':12,'historical_letter':historical,'revised_letter':revised,'critic_file_fingerprints':sha,'candidates':{},'status':'blocked',
      'champion_id':None,'champion_score':None,'owner_approved':False,'procurement_release':False,'accepted_challenger':False,'source_selection_preserved':True}
 for letter in sorted(letters):
  x=score[letter]
  weighted=sum(Decimal(str(x[s]))*seats[s][0] for s in seats).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
  if letter==historical:
   sourcefloor={'TX-PRIMARY':'original Cortar Clay Soft LEVEL','TX-BATH2':'original Cortar Clay Soft LEVEL','TX-BATH4':'original Cortar Bone Soft LEVEL'}[rid]
   reasons=['FAIL: '+sourcefloor+' exact manufacturer SKU/finish raw numeric measured wet DCOF certificate absent. No Emser alternative laboratory result transfers to this source floor.']
  else:
   reasons=['FAIL: revised Emser Capisco Trosa F08CAPITR1224M LEVEL tile published maker wet DCOF >=0.60 is only a lower bound, NOT the individual exact raw numerical laboratory result.']
  if rid=='TX-PRIMARY':
   if letter==historical:
    reasons+=['FAIL: original Cortar Clay Anti-Slip 12x24 LINEAR PAN wet DCOF exact raw numerical manufacturer test absent; actual pan geometry/slope and compatibility unverified.',
             'HOLD: selected Brizo BT0734816-BNX 48-in Black Onyx LINEAR and separate BR73480 rough need original Clay Anti-Slip pan/liner/flood-tested shop section; Prime RL21 is NOT part of this historical option.']
   else:
    reasons+=['FAIL: proposed separate Daltile Prime RL21 hex mosaic LINEAR PAN has brochure TARGET only, no exact product raw measured wet DCOF certificate.',
             'HOLD: revised proposed Prime RL21 nominal 6.35mm tile vs selected Brizo adjustable frame 7–18mm = 0.65mm nominal stack-up coordination, NOT proven incompatibility; require manufacturer-approved full carrier/setting/liner/rough/flood section.']
   reasons+=['HOLD: no Primary niche; TX WC floor gross already included in Primary original source, actual LEVEL/PAN split unmeasured.']
   if letter==historical:reasons+=['FAIL: source Cortar Clay Ribbed relief does not have individual manufacturer Wet Areas approval.']
   else:reasons+=['PASS WALL ONLY: exact flat Cortar Clay individual Wet Areas listing; no implied relief permission.']
  elif rid=='TX-BATH2':
   reasons+=['PASS WALL ONLY: individually wet-listed Copper 2x20 and existing Sandstone niche.',
             'HOLD: actual Duravit tub/Chrome Hansgrohe; NO tiled shower pan; actual tub flange and niche dimensions unverified.',
             'HOLD: TX Bath2 sink/basin OWNER UNSELECTED; proposed calibrated W1 cut must be checked with true tile and grout.']
  else:
   reasons+=['PASS WALL ONLY: flat Cortar Charcoal wet tub wall individually listed; Duravit/Matte White tub is selected and NO tiled shower pan exists.',
             'FAIL: individually wet-listed Clara Caviar niche absent.' if letter==historical else 'PASS WET NICHE ONLY: maker wet-listed Soho Ivory 2x10 Glossy, subject to actual measured niche face/back/returns and new bid.']
  reasons+=['HOLD: authenticated 1529 Revit model/site geometry, current exact Chicago supplier lot/landed bid/ETA, installed cost, signed owner samples and room material cap unavailable; do not invent 125% budget gate status.']
  row['candidates'][letter]={'role':keys[letter],'individual_critic_scores':x,'individual_criterion_scores':criteria[letter],
      'weighted_score':float(weighted),'minimum_critic_score':min(x.values()),'all_critics_at_least_3':min(x.values())>=3.0,
      'all_hard_gates_pass':False,'gate_reasons':reasons,'frozen_candidate_sha256':letters[letter]['sha256']}
 a=row['candidates'][historical];b=row['candidates'][revised]
 margin=(Decimal(str(b['weighted_score']))-Decimal(str(a['weighted_score']))).quantize(Decimal('.01'))
 row['challenger_margin']=float(margin)
 row['challenger_margin_at_least_025']=margin>=Decimal('.25')
 row['challenger_acceptance_pass']=False
 row['gate_qualified_champion']=None
 row['conditional_visual_direction']=revised if margin>0 else historical
 row['decision']='BLOCKED: no wet-test gate-qualified or cost/minimum-qualified champion; conditional design directions only.'
 result['room_results'][rid]=row
assert result['verification']['frozen_candidates']==6
assert result['verification']['original_critics']==12
assert result['verification']['criteria']==114
assert result['verification']['recalculated_seat_means']==24
assert result['verification']['local_links']==collection['local_links']==380
result['verification']['valid']=True
dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
for rid,r in result['room_results'].items():
 a=r['candidates'][r['historical_letter']];b=r['candidates'][r['revised_letter']]
 print(rid,'historic',a['weighted_score'],'revised',b['weighted_score'],'margin',r['challenger_margin'],'minimum',b['minimum_critic_score'],'BLOCKED')
print('PASS 6 frozen candidates, 12 original critics, 114 criteria, 24 means, 380 local links; owner/procurement release FALSE')

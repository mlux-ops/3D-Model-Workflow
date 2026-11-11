"""Formal R011 four-seat score in a distinct continuation, preserving submission history."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import json,hashlib,re
R=Path(__file__).resolve().parents[1]
ROOMS=('PH-BATH3','TX-BATH3')
SEATS={'market':('.30',4),'design':('.25',5),'build':('.25',5),'cost':('.20',5)}
subpath=R/'state/ROUND011_SUBMISSION.json';collectionpath=R/'state/ROUND011_CRITIC_COLLECTION.json';dispatchpath=R/'state/ROUND011_CRITIC_DISPATCH.json'
sub=json.loads(subpath.read_text(encoding='utf-8'));coll=json.loads(collectionpath.read_text(encoding='utf-8'));dispatch=json.loads(dispatchpath.read_text(encoding='utf-8'))
assert sub['round']==coll['round']==dispatch['round']==11
assert all(z['phase']=='2-board' and z['all_critic_scores'] is None for z in (sub,coll,dispatch))
assert coll['weighted_scoring_complete'] is False and dispatch['scoring_deferred_to_next_distinct_turn'] is True
assert coll['source_submission_sha256']==dispatch['source_submission_sha256']==hashlib.sha256(subpath.read_bytes()).hexdigest()
assert coll['source_dispatch_sha256']==hashlib.sha256(dispatchpath.read_bytes()).hexdigest()
assert set(coll['report_files'])==set(sub['candidate_files'])==set(ROOMS)
result={'as_of':'2026-11-06','round':11,'reviewer_prior_clearance':'worker-8 CONTINUE — formal scoring in NEXT DISTINCT TURN','source_submission':'state/ROUND011_SUBMISSION.json','source_submission_sha256':hashlib.sha256(subpath.read_bytes()).hexdigest(),'source_critic_collection':'state/ROUND011_CRITIC_COLLECTION.json','source_collection_sha256':hashlib.sha256(collectionpath.read_bytes()).hexdigest(),'source_dispatch_sha256':hashlib.sha256(dispatchpath.read_bytes()).hexdigest(),'verification':{'candidate_frozen_files':4,'actual_independent_critiques':8,'criterion_checks':0,'seat_means_verified':0,'local_links':0,'all_valid':False},'room_results':{}}
expected={'PH-BATH3':{'A':{'market':3.7,'design':3.4,'build':2.4,'cost':2.6},'B':{'market':3.5,'design':2.8,'build':1.8,'cost':2.6}},'TX-BATH3':{'B':{'market':3.7,'design':3.4,'build':2.4,'cost':2.6},'C':{'market':3.6,'design':3.2,'build':2.0,'cost':2.8}}}
for rid in ROOMS:
 folder=R/'rooms'/rid/'board/round-011'
 keys=json.loads((folder/'_key.json').read_text(encoding='utf-8'))
 src=sub['candidate_files'][rid]
 assert set(keys)==set(src) and len(keys)==2
 hist=next(k for k,v in keys.items() if 'historic' in v.lower())
 revised=next(k for k in keys if k!=hist)
 for letter,v in src.items():
  raw=(folder/'candidates'/f'{letter}.md').read_bytes()
  assert hashlib.sha256(raw).hexdigest()==v['sha256'] and len(raw)==v['bytes']
 crit_scores={letter:{} for letter in src};evidence={letter:{} for letter in src};hashes={}
 for seat,(weight,n) in SEATS.items():
  f=folder/f'critic-{seat}.md';raw=f.read_bytes();t=raw.decode('utf-8')
  receipt=coll['report_files'][rid][seat]
  assert len(raw)==receipt['bytes'] and hashlib.sha256(raw).hexdigest()==receipt['sha256'],(rid,seat,'fingerprint')
  assert receipt['worker']==dispatch['critic_worker_seats'][f'critic-{seat}']
  assert not re.search(r'(?i)_key\.json|state/ROOMS\.json|state/LEDGER\.md|\bincumbent\b|\bchampion\b|\bsteam\b',t),(rid,seat,'blindness')
  parts=re.split(r'(?im)^##\s+Candidate\s+([A-Z])\b[^\n]*\n',t)
  assert len(parts)==5 and set(parts[1::2])==set(src),(rid,seat,'sections',parts[1::2])
  hashes[seat]={'sha256':receipt['sha256'],'bytes':receipt['bytes'],'worker':receipt['worker']}
  # Collection verified all links including preface/source basis; criterion parser below
  # counts candidate-section links separately, so never compare subset against whole-file count.
  for link in re.findall(r'\]\(([^)]+)\)',t):
   if link.startswith(('http://','https://','#','mailto:')):continue
   assert (f.parent/link.split('#')[0]).exists(),(rid,seat,'whole-file citation',link)
   result['verification']['local_links']+=1
  for letter,block in zip(parts[1::2],parts[2::2]):
   table=[]
   for line in block.splitlines():
    if not line.startswith('|'):continue
    cells=[v.strip() for v in line.strip('|').split('|')]
    if len(cells)!=3:continue
    value=re.sub(r'\*','',cells[1]).strip()
    value=re.sub(r'\s*/\s*5(?:\.0)?\s*$','',value).strip()
    if re.fullmatch(r'[1-5](?:\.\d+)?',value):table.append((Decimal(value),cells[2]))
   assert len(table)==n,(rid,seat,letter,'criterion count',len(table))
   assert all(len(note)>35 and ('[' in note or 'http' in note or 'OT0' in note) for _,note in table),(rid,seat,letter,'evidence')
   score=(sum((v for v,_ in table),Decimal(0))/Decimal(n)).quantize(Decimal('.1'),rounding=ROUND_HALF_UP)
   assert score==Decimal(str(expected[rid][letter][seat])),(rid,seat,letter,'arithmetic mean',score)
   assert re.search(r'(?i)top_fix\s*:',block) and re.search(r'(?i)gate_flags\s*:',block) and re.search(r'(?i)confidence\s*:',block)
   result['verification']['criterion_checks']+=n
   result['verification']['seat_means_verified']+=1
   crit_scores[letter][seat]=float(score)
   evidence[letter][seat]={'criterion_scores':[float(v) for v,_ in table],'mean':float(score)}
 rr={'room':rid,'round':11,'critics_complete':True,'critic_file_fingerprints':hashes,'weights':{s:float(v[0]) for s,v in SEATS.items()},'incumbent_letter':hist,'challenger_letter':revised,'candidates':{}}
 for letter in sorted(src):
  ss=crit_scores[letter];weighted=sum(Decimal(str(ss[s]))*Decimal(SEATS[s][0]) for s in SEATS).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
  failures=['FAIL: exact maker-SKU-and-finish raw measured numeric wet DCOF certificate for LEVEL floor remains unavailable; published >0.50 lower bounds and Daltile targets are not accepted raw test values']
  if rid=='PH-BATH3':
   if letter==hist:failures+=['FAIL: original ELM Tones Opal 2x20 Glossy lacks individual maker Wet Areas authorization for wet wall']
   else:failures+=['PASS WALL ONLY: individual ELM Tones Sandstone 2x20 Glossy wet field and existing niche Wet Areas listed']
   failures+=['HOLD: PH sink UNSELECTED and drawing-origin tub alcove conflicts with scheduled Delta DT062412 Chrome 4-inch square shower point drain']
  else:
   failures+=['PASS WALL ONLY: individual ELM Tones Emerald wet field and Sandstone niche Wet Areas documented']
   failures+=['HOLD: drawing tub alcove versus selected Brizo BT062415-BNX Brilliance Black Onyx 4-inch square shower point drain, owner tub/walk-in election unresolved']
   if letter==revised:failures+=['HOLD: nominal vertical 1.60-inch strips must be eliminated/re-dimensioned after actual caliber and elevations; not automatically the unrelated 24x48 under-3-inch geometry gate']
  if letter==revised:failures+=['FAIL if owner elects WALK-IN: HNC6715 conditional 2x2 point-pan maker >0.50 bound is not accepted raw tested numeric DCOF; pan polygon/membrane/grate interface not certified']
  else:failures+=['FAIL if owner elects WALK-IN: no selected compatible tested small-format point-pan material or verified four-plane drain slope detail']
  failures+=['HOLD: correct 1529 native model/site dimensions, original niche field-face deduction, approved drain/membrane/threshold, current Chicago lot/quote/ETA, room material cap, owner signature all unverified; no invented 125% budget failure']
  rr['candidates'][letter]={'role':keys[letter],'seat_scores':ss,'criterion_scores':evidence[letter],'weighted_score':float(weighted),'minimum_critic_score':min(ss.values()),'all_seat_minimum_3_pass':min(ss.values())>=3.0,'hard_gates_pass':False,'gate_reasons':failures,'source_candidate_sha256':src[letter]['sha256']}
 old=rr['candidates'][hist];new=rr['candidates'][revised]
 rr['margin']=float((Decimal(str(new['weighted_score']))-Decimal(str(old['weighted_score']))).quantize(Decimal('.01')))
 rr.update(status='blocked',decision='both_candidates_blocked_floor_and_conditional_point_pan_exact_dcof_and_owner_program',champion_id=None,champion_score=None,accepted_challenger=False,owner_approved=False,procurement_release=False,provisional_design_preference=revised if rr['margin']>0 else hist,report='board/round-011/ROUND_REPORT.md')
 result['room_results'][rid]=rr
assert result['verification']['criterion_checks']==76 and result['verification']['seat_means_verified']==16
assert result['verification']['local_links']==coll['resolved_local_links'],(result['verification']['local_links'],coll['resolved_local_links'])
result['verification']['all_valid']=True
dest=R/'state/ROUND011_SCORING.json';assert not dest.exists(),'Original scored receipt already exists, do not overwrite'
dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
for rid,rr in result['room_results'].items():
 a,b=rr['incumbent_letter'],rr['challenger_letter']
 print(rid,'historic',a,rr['candidates'][a]['weighted_score'],'revised',b,rr['candidates'][b]['weighted_score'],'delta',rr['margin'],'min revised',rr['candidates'][b]['minimum_critic_score'],'BLOCKED')
print('PASS 8 frozen critics, 4 candidate SHA, 76 criteria, 16 means, 236 citations; no owner/procurement release')

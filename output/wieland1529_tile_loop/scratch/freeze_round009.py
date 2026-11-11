from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1]
expected={'TX-PRIMARY':{'C':'historic v4 source','A':'revised design option'},'TX-BATH2':{'A':'historic v4 source','C':'revised design option'},'TX-BATH4':{'B':'historic v4 source','A':'revised design option'}}
intro='This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.'
out={'as_of':'2026-11-06','round':9,'phase':'2-board','all_critic_scores':None,'candidate_files':{},'critic_seats':['critic-market','critic-design','critic-build','critic-cost'],'owner_approval':None,'native_1529_confirmed':False,'release_allowed':False,'prior_round004_candidate_files_untouched':True}
frozen=R/'state/ROUND009_SUBMISSION.json'
assert not frozen.exists(),'Existing frozen Round009 receipt: must not re-freeze/alter packets'
regpath=R/'state/ROOMS.json';reg=json.loads(regpath.read_text(encoding='utf-8'))
assert len(reg['rooms'])==13
for rid,letters in expected.items():
 room=next(x for x in reg['rooms'] if x['id']==rid)
 assert room['status']=='blocked' and room['champion_id'] is None and room['owner_status'] is None
 directory=R/'rooms'/rid/'board/round-009';candidate_dir=directory/'candidates'
 paths=sorted(candidate_dir.glob('*.md'))
 assert {p.stem for p in paths}==set(letters),(rid,[x.stem for x in paths])
 hashes={}
 sizes=[]
 for p in paths:
  b=p.read_bytes();t=b.decode('utf-8')
  lines=t.splitlines()
  assert lines[0]=='# '+rid+' — Candidate '+p.stem+' — complete tile design option',(rid,p.name,lines[0])
  assert lines[1]=='' and lines[2]==intro,(rid,p.name,lines[:4])
  assert len(b)>5000,(rid,p.name,len(b))
  assert '|' in t and t.count('|')>30 and 'http' in t,(rid,p.name,'need real 5-col source and maker citation')
  assert 'DCOF' in t and ('null' in t.lower() or 'FAIL' in t),(rid,p.name,'must carry exact test hold')
  assert '15%' in t and '$' in t or 'USD' in t,(rid,p.name,'quantity/cost basis')
  assert not re.search(r'(?i)\bincumbent\b|\bchallenger\b|round[- ]?00[1-8]\b|_key\.json|read state/ROOMS\.json|read state/LEDGER\.md',t),(rid,p.name,'blind role leak')
  hashes[p.stem]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
  sizes.append(len(b))
 assert max(sizes)/min(sizes)<2.0,(rid,'role-sensitive packet depth contrast',sizes)
 out['candidate_files'][rid]=hashes
for rid,letters in expected.items():
 directory=R/'rooms'/rid/'board/round-009'
 key=directory/'_key.json'
 assert not key.exists()
 key.write_text(json.dumps(letters,indent=2)+'\n',encoding='utf-8')
 room=next(x for x in reg['rooms'] if x['id']==rid)
 room['last_round']=9
 room['round_009_submission']={'status':'blind_review_pending','scores':None,'candidate_count':2,'critics_required':['critic-market','critic-design','critic-build','critic-cost'],'owner_approved':False,'source_sha_state':'frozen receipt state/ROUND009_SUBMISSION.json','prior_board':'preserved'}
 room['provisional_research_target']='Round009 neutral source and alternative comparison; board pending, no accepted champion'
frozen.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
regpath.write_text(json.dumps(reg,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS ROUND009 frozen 6 candidate SHA, 3 private mappings, 13-room state retained; all scores NULL and four critic seats PENDING')
for rid,letters in out['candidate_files'].items():print(rid,' '.join(k+'='+v['sha256'][:12] for k,v in sorted(letters.items())))

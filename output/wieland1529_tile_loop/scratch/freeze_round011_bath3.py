from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1]
mp={'PH-BATH3':{'B':'historic v4 source','A':'revised owner-program-conditional design'},'TX-BATH3':{'C':'historic v4 source','B':'revised owner-program-conditional design'}}
intro='This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.'
dest=R/'state/ROUND011_SUBMISSION.json'
assert not dest.exists(),'Round011 original source receipt exists: never silently overwrite'
rp=R/'state/ROOMS.json';state=json.loads(rp.read_text(encoding='utf-8'))
assert len(state['rooms'])==13
staged={}
d={'round':11,'as_of':'2026-11-06','phase':'2-board','all_critic_scores':None,
'candidate_files':{},'critic_seats':['critic-market','critic-design','critic-build','critic-cost'],
'owner_program_selected':False,'revit_1529_native_verified':False,'procurement_released':False,
'independent_preflight_status':'pending independent non-Pro Reviewer','new_board_dispatch_status':'NOT DISPATCHED; await Reviewer FIX or CONTINUE',
'prior_rounds_001_through_010_scoring_and_source_unchanged':True}
for rid,roles in mp.items():
 room=next(x for x in state['rooms'] if x['id']==rid)
 assert room['status']=='blocked' and room['champion_id'] is None and room['owner_status'] is None
 d['candidate_files'][rid]={}
 p=R/'rooms'/rid/'board/round-011'
 assert not (p/'_key.json').exists()
 files=sorted((p/'candidates').glob('*.md'))
 assert {x.stem for x in files}==set(roles) and len(files)==2
 for f in files:
  b=f.read_bytes();t=b.decode('utf-8');l=t.splitlines()
  assert len(b)>=8500 and l[0]=='# '+rid+' — Candidate '+f.stem+' — complete tile design option' and l[1]=='' and l[2]==intro,(rid,f.stem,'identity/intro')
  assert not re.search(r'(?i)\bincumbent\b|\bchallenger\b|\bchampion\b|_key\.json|state/ROOMS\.json|state/LEDGER\.md|\bsteam\b',t),(rid,f.stem,'role/owner topic')
  assert 'DCOF' in t and '15%' in t and ('tub' in t.lower()) and ('WALK-IN' in t) and 'null' in t.lower()
  assert sum(len(x.strip('|').split('|'))==5 for x in l if x.startswith('|'))>=5
  for z in room['carried_tile_rows']:assert z['smartsheet_row_id'] in t,(rid,f.stem,z['smartsheet_row_id'])
  for link in re.findall(r'\]\(([^)]+)\)',t):
   if link.startswith(('https://','http://','#','mailto:')):continue
   assert (f.parent/link.split('#')[0]).exists(),(rid,f.stem,'broken local maker link',link)
  if rid=='PH-BATH3':assert 'DT062412' in t and 'UNSELECTED' in t
  if rid=='TX-BATH3':assert 'BT062415-BNX' in t and 'Black Onyx' in t
  d['candidate_files'][rid][f.stem]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
 assert max(z['bytes'] for z in d['candidate_files'][rid].values())/min(z['bytes'] for z in d['candidate_files'][rid].values())<1.5
 room['last_round']=11
 room['round_011_submission']={'status':'independent_blind_preflight_pending','scores':None,'candidate_count':2,'critic_seats_required':['market','design','build','cost'],'owner_approved':False,'release_allowed':False,'source':'state/ROUND011_SUBMISSION.json','owner_tub_or_walkin_selection':None,'preflight_completed':False}
 hp=R/'rooms'/rid/'history.md';h=hp.read_text(encoding='utf-8')
 assert 'Round011' not in h
 h+='\n- 2026-11-06 Round011: two coherent neutral source-backed tub-versus-point-shower conditional tile options frozen for INDEPENDENT PRE-DISPATCH reviewer; owner program UNSELECTED and original previous scored BLOCKED decisions preserved. 4 original specialist seats NOT yet dispatched, all critic scores null, original v4/maker data and current plumbing unchanged. Source SHA state/ROUND011_SUBMISSION.json; private role key withheld from all critics.\n'
 staged[rid]={'key':p/'_key.json','roles':roles,'history_path':hp,'history_text':h}
# Complete both rooms' source, role, receipt and history checks before the first write.
assert len(staged)==2 and set(staged)==set(mp)
for values in staged.values():
 assert not values['key'].exists()
 assert 'Round011' in values['history_text']
for values in staged.values():
 values['key'].write_text(json.dumps(values['roles'],indent=2)+'\n',encoding='utf-8')
 values['history_path'].write_text(values['history_text'],encoding='utf-8')
dest.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
rp.write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS Round011 4 frozen source SHA with 2 private role keys, room scores null; independent reviewer PREFLIGHT pending, critics NOT dispatched')
for rid,x in d['candidate_files'].items():print(rid,[(k,v['sha256'][:14],v['bytes']) for k,v in x.items()])

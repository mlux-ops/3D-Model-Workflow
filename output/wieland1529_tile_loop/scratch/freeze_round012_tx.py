"""Controlled one-time R012 neutral TX source freeze, pre-review and pre-dispatch."""
from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1]
mp={'TX-PRIMARY':{'B':'historic v4 source','C':'revised exact-SKU conditional Emser/flat Clay design'},
    'TX-BATH2':{'C':'historic v4 source','A':'revised Emser level/Copper horizontal design'},
    'TX-BATH4':{'A':'historic v4 source','B':'revised Emser/Soho Ivory wet design'}}
receipt=R/'state/ROUND012_SUBMISSION.json'
assert not receipt.exists()
path=R/'state/ROOMS.json';data=json.loads(path.read_text(encoding='utf-8'))
assert len(data['rooms'])==13
intro='This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.'
out={'as_of':'2026-11-06','round':12,'phase':'2-board','all_critic_scores':None,'candidate_files':{},'independent_preflight':'pending non-Pro worker-8 read-only','critic_dispatch':'NOT DISPATCHED','owner_approval':False,'procurement_release':False,'revit_1529_verified':False,'prior_rounds_unmodified':True}
staged={}
for rid,roles in mp.items():
 room=next(x for x in data['rooms'] if x['id']==rid)
 assert room['status']=='blocked' and room['champion_id'] is None and room['owner_status'] is None
 folder=R/'rooms'/rid/'board/round-012'
 assert not (folder/'_key.json').exists()
 files=sorted((folder/'candidates').glob('*.md'))
 assert {f.stem for f in files}==set(roles) and len(files)==2
 out['candidate_files'][rid]={}
 for f in files:
  raw=f.read_bytes();body=raw.decode('utf-8');lines=body.splitlines()
  assert len(raw)>=7600 and lines[:3]==[f'# {rid} — Candidate {f.stem} — complete tile design option','',intro]
  assert not re.search(r'(?i)\bincumbent\b|\bchallenger\b|\bchampion\b|_key\.json|state/ROOMS\.json|state/LEDGER\.md|\bsteam\b|round[- ]?00[0-9]',body),(rid,f.stem,'role leak')
  assert sum(len(x.strip('|').split('|'))==5 for x in lines if x.startswith('|'))>=5
  assert '15%' in body and 'DCOF' in body and 'NULL' in body
  for row in room['carried_tile_rows']:assert row['smartsheet_row_id'] in body,(rid,f.stem,'row',row['smartsheet_row_id'])
  for link in re.findall(r'\]\(([^)]+)\)',body):
   if link.startswith(('https://','http://','#','mailto:')):continue
   assert (f.parent/link.split('#')[0]).exists(),(rid,f.stem,'broken link',link)
  if rid=='TX-PRIMARY':assert 'BT0734816-BNX' in body and 'BR73480' in body and 'NO PRIMARY NICHE' in body
  if rid=='TX-BATH2':assert '700332000000090' in body and 'UNSELECTED' in body and 'CHROME' in body
  if rid=='TX-BATH4':assert '700332000000090' in body and 'Matte White' in body and 'NO tiled pan' in body
  out['candidate_files'][rid][f.stem]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
 hp=R/'rooms'/rid/'history.md';h=hp.read_text(encoding='utf-8')
 assert 'Round012' not in h
 h+='\n- 2026-11-06 Round012: 2 neutral frozen source-backed TX options submitted for independent blind PRE-DISPATCH REVIEW; all specialist scores null. Preserves original v4 quotes, previous scored BLOCKED status, original 15% waste once, owner/field/price/DCOF holds and current fixtures. Source receipt state/ROUND012_SUBMISSION.json, private mapping withheld from critics.\n'
 room['last_round']=12
 room['round_012_submission']={'status':'independent_blind_preflight_pending','scores':None,'critic_seats_required':['market','design','build','cost'],'owner_approved':False,'release_allowed':False,'preflight_completed':False,'source':'state/ROUND012_SUBMISSION.json'}
 staged[rid]=(folder/'_key.json',roles,hp,h)
assert len(staged)==3
for key,roles,hp,h in staged.values():
 key.write_text(json.dumps(roles,indent=2)+'\n',encoding='utf-8')
 hp.write_text(h,encoding='utf-8')
receipt.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS R012 6 neutral frozen SHA, 3 private keys, no critics and all scores null, 3 rooms still BLOCKED')
for rid,files in out['candidate_files'].items():print(rid,[(k,v['sha256'][:15],v['bytes']) for k,v in files.items()])

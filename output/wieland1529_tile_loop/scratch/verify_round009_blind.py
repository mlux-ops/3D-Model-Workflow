from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1]
receipt=json.loads((R/'state/ROUND009_SUBMISSION.json').read_text(encoding='utf-8'))
reg=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))
scored=(R/'state/ROUND009_SCORING.json').exists()
scoring=json.loads((R/'state/ROUND009_SCORING.json').read_text(encoding='utf-8')) if scored else None
intro='This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.'
assert receipt['all_critic_scores'] is None and receipt['phase']=='2-board' and receipt['round']==9
assert set(receipt['candidate_files'])=={'TX-PRIMARY','TX-BATH2','TX-BATH4'}
count=0; links=0; weights=[.30,.25,.25,.20]
for rid,letters in receipt['candidate_files'].items():
 key=json.loads((R/'rooms'/rid/'board/round-009/_key.json').read_text(encoding='utf-8'))
 assert set(key)==set(letters) and sum('historic v4 source'==v for v in key.values())==1
 item=next(x for x in reg['rooms'] if x['id']==rid)
 assert item['status']=='blocked' and item['owner_status'] is None and item['champion_id'] is None and item['champion_score'] is None
 assert item['round_009_submission']['status']==('review_complete_scored' if scored else 'blind_review_pending')
 if scored:
  assert item['round_009_submission']['scores']=={k:v['weighted_score'] for k,v in scoring['room_results'][rid]['candidates'].items()}
  assert item['board_round_009']['critics_complete'] and item['board_round_009']['status']=='blocked'
 else:
  assert item['round_009_submission']['scores'] is None
 for letter,data in letters.items():
  p=R/'rooms'/rid/'board/round-009/candidates'/(letter+'.md')
  b=p.read_bytes();t=b.decode('utf-8');lines=t.splitlines()
  assert len(b)==data['bytes'] and hashlib.sha256(b).hexdigest()==data['sha256']
  assert lines[0]=='# '+rid+' — Candidate '+letter+' — complete tile design option' and lines[1]=='' and lines[2]==intro,(rid,letter,lines[:4])
  assert not re.search(r'(?i)\bincumbent\b|\bchallenger\b|round[- ]?00[1-4]\b|\bR02 independent critics\b|\bindependent critics\b|\bprevious critics\b|_key\.json|state/ROOMS\.json|state/LEDGER\.md|champion\.md|history\.md|critic-(market|design|build|cost)',t),(rid,letter,'role leak')
  assert not re.search(r'(?i)\bsteam\b',t),(rid,letter,'owner excluded subject')
  if rid in ('TX-BATH2','TX-BATH4'):
   assert not re.search('(?i)slope into selected linear drain|24x48.*slope.*selected linear drain|TX Primary chosen linear drain',t),(rid,letter,'tub has no selected linear shower drain')
  if rid=='TX-BATH2':
   assert not re.search('(?i)matte white/Black Onyx fixture relationship',t),(rid,letter,'actual selected Chrome fixture finish')
  assert 'DCOF' in t and '15%' in t and ('null' in t.lower() or 'FAIL' in t)
  tables=[]
  for line in lines:
   if line.startswith('|'):
    cells=[x.strip() for x in line.strip('|').split('|')]
    tables.append(cells)
  assert len(tables)>=5 and sum(len(x)==5 for x in tables)>=5,(rid,letter,'missing five-column spec table')
  for link in re.findall(r'\]\(([^)]+)\)',t):
   if link.startswith(('https://','http://','#','mailto:')):continue
   assert (p.parent/link.split('#')[0]).exists(),(rid,letter,'broken evidence',link)
   links+=1
  for z in item['carried_tile_rows']:
   assert z['smartsheet_row_id'] in t,(rid,letter,'original source quote ID missing',z['smartsheet_row_id'])
  count+=1
assert count==6
print('PASS Round009 6/6 frozen SHA/byte, 3/3 private role keys, blind neutral line3, five-col source tables, source ID evidence,',links,'local links, immutable submission score null;', 'separate scored room register' if scored else 'pending board')

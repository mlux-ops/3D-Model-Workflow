"""Frozen PH Round004 blind-board integrity check; no writes."""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[1]
receipt=json.loads((R/'state/ROUND004_SUBMISSION.json').read_text(encoding='utf-8'))
state={x['id']:x for x in json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
expected={'PH-PRIMARY':{'A','C'},'PH-BATH2':{'A','B'},'PH-BATH3':{'B','C'},'PH-BATH4':{'A','B'}}
intro='**Round 004 / per Penthouse unit; two units.** This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.'
baseline_bytes=[];revised_bytes=[];links=0
scoring_path=R/'state/ROUND004_SCORING.json'
scored=scoring_path.exists()
scoring=json.loads(scoring_path.read_text(encoding='utf-8')) if scored else None
for rid,letters in expected.items():
 d=R/'rooms'/rid/'board/round-004'
 key=json.loads((d/'_key.json').read_text(encoding='utf-8'))
 assert set(k for k in key if k in 'ABC')==letters
 assert len([k for k in letters if 'historic v4 source' in key[k]])==1
 assert len(list((d/'candidates').glob('*.md')))==2
 assert state[rid]['round_004_submission']['status']==('review_complete_scored' if scored else 'blind_review_pending')
 if scored:
  assert state[rid]['round_004_submission']['scores']=={k:v['weighted_score'] for k,v in scoring['room_results'][rid]['candidates'].items()}
  assert state[rid]['status']=='blocked' and state[rid]['board_round_004']['critics_complete']
 else:
  assert state[rid]['round_004_submission']['scores'] is None
 assert state[rid]['owner_status'] is None
 for letter in letters:
  p=d/'candidates'/(letter+'.md');data=p.read_bytes()
  a=receipt['candidate_files'][rid][letter]
  assert len(data)==a['bytes'] and hashlib.sha256(data).hexdigest()==a['sha256']
  t=data.decode('utf-8')
  lines=t.splitlines()
  assert lines[0].startswith('# '+rid+' — Candidate '+letter+' —'),(rid,letter,lines[0])
  assert lines[2]==intro
  assert all(phrase not in t.lower() for phrase in ('actual challenger','round001 critics','round001 lessons','incumbent','round001 preferred','round001 rejected'))
  tbl=[x for x in lines if x.startswith('|')]
  assert len(tbl)>=5 and all(len(x.split('|'))==7 for x in tbl),(rid,letter,'five column table')
  for link in re.findall(r'\]\(([^)]+)\)',t):
   if link.startswith(('https://','http://','mailto:')):continue
   assert (p.parent/link.split('#')[0]).resolve().exists(),(rid,letter,link)
   links+=1
  if 'historic v4 source' in key[letter]:
   baseline_bytes.append(len(data))
   assert 'research/products/' in t and 'research/comps/' in t
  else:revised_bytes.append(len(data))
 print(rid,sorted((k,v['bytes']) for k,v in receipt['candidate_files'][rid].items()),'scored in Round005' if scored else 'board pending')
assert min(baseline_bytes)>5000 and max(baseline_bytes)<max(revised_bytes)
assert all(r['status']==('blocked' if scored else 'active') and r['last_round']>=4 for r in (state[k] for k in expected))
assert all('board_round_004' in r and r['board_round_004']['status']=='blocked' for r in (state[k] for k in expected)) if scored else True
assert receipt['all_critic_scores'] is None
print('PASS 8/8 immutable submission SHA; intro identical; five columns;',links,'local links; submission frozen scores NULL; separately scored room register' if scored else 'board still pending')

"""R012 source SHA, neutrality, source ID, owner and local citation read-only QA."""
from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1]
s=json.loads((R/'state/ROUND012_SUBMISSION.json').read_text(encoding='utf-8'))
data=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))
assert s['round']==12 and s['phase']=='2-board' and s['all_critic_scores'] is None
assert s['critic_dispatch']=='NOT DISPATCHED' and not s['procurement_release']
assert set(s['candidate_files'])=={'TX-PRIMARY','TX-BATH2','TX-BATH4'}
count=0;links=0
intro='This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.'
for rid,files in s['candidate_files'].items():
 room=next(x for x in data['rooms'] if x['id']==rid)
 assert room['status']=='blocked' and room['champion_id'] is None and room['round_012_submission']['scores'] is None
 folder=R/'rooms'/rid/'board/round-012'
 assert not list(folder.glob('critic-*.md'))
 assert (folder/'_key.json').is_file()
 assert {f.stem for f in (folder/'candidates').glob('*.md')}==set(files)
 for letter,x in files.items():
  f=folder/'candidates'/f'{letter}.md';raw=f.read_bytes();t=raw.decode('utf-8');a=t.splitlines()
  assert hashlib.sha256(raw).hexdigest()==x['sha256'] and len(raw)==x['bytes']
  assert a[:3]==[f'# {rid} — Candidate {letter} — complete tile design option','',intro]
  assert not re.search(r'(?i)\bincumbent\b|\bchallenger\b|\bchampion\b|_key\.json|state/ROOMS\.json|state/LEDGER\.md|\bsteam\b',t)
  assert sum(len(z.strip('|').split('|'))==5 for z in a if z.startswith('|'))>=5
  for row in room['carried_tile_rows']:assert row['smartsheet_row_id'] in t
  for link in re.findall(r'\]\(([^)]+)\)',t):
   if link.startswith(('https://','http://','#','mailto:')):continue
   assert (f.parent/link.split('#')[0]).exists(),(rid,letter,link)
   links+=1
  if rid=='TX-PRIMARY':assert 'NO PRIMARY NICHE' in t and '48-in LINEAR' in t and 'BR73480' in t
  if rid=='TX-BATH2':assert 'UNSELECTED' in t and 'CHROME' in t and 'NO tiled' in t
  if rid=='TX-BATH4':assert 'Matte White' in t and 'Duravit' in t and 'NO tiled' in t
  count+=1
print('PASS R012',count,'frozen neutral source SHA,',links,'local links, 3 BLOCKED rooms, all scores null, no critics')

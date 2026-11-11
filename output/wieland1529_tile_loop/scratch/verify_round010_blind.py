from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'state/ROUND010_SUBMISSION.json').read_text(encoding='utf-8'))
reg={x['id']:x for x in json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
intro='This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.'
assert d['all_critic_scores'] is None and set(d['candidate_files'])=={'PH-PRIMARY','PH-BATH2','PH-BATH4'}
for rid,cs in d['candidate_files'].items():
 assert len(cs)==2
 if (R/'state/ROUND010_SCORING.json').exists():
  assert reg[rid]['round_010_submission']['status']=='review_complete_scored'
  assert reg[rid]['board_round_010']['status']=='blocked' and reg[rid]['champion_id'] is None and reg[rid]['owner_status'] is None
 else:
  assert reg[rid]['round_010_submission']['scores'] is None
 roles=json.loads((R/'rooms'/rid/'board/round-010/_key.json').read_text(encoding='utf-8'))
 assert set(roles)==set(cs) and sum('historic' in r for r in roles.values())==1
 assert all(z.name in ('critic-market.md','critic-design.md','critic-build.md','critic-cost.md') for z in (R/'rooms'/rid/'board/round-010').glob('critic-*.md')),rid
 for letter,rec in cs.items():
  p=R/'rooms'/rid/'board/round-010/candidates'/(letter+'.md')
  b=p.read_bytes();t=b.decode('utf-8');lines=t.splitlines()
  assert hashlib.sha256(b).hexdigest()==rec['sha256'] and len(b)==rec['bytes']
  assert lines[:3]==['# '+rid+' — Candidate '+letter+' — complete tile design option','',intro]
  assert not re.search(r'(?i)\bincumbent\b|\bchallenger\b|\bchampion\b|exact historical material/fixture scope|no new finishes or replacement fixture selected|round[- ]?00[1-9]\b|_key\.json|state/ROOMS\.json|state/LEDGER\.md|\bsteam\b',t),(rid,letter,'blind leak')
  assert 'DCOF' in t and '15%' in t and 'null' in t.lower()
  assert sum(len(x.strip('|').split('|'))==5 for x in lines if x.startswith('|'))>=5
  for z in reg[rid]['carried_tile_rows']: assert z['smartsheet_row_id'] in t,(rid,letter,z['smartsheet_row_id'])
  for url in re.findall(r'\]\(([^)]+)\)',t):
   if not url.startswith(('https://','http://','#','mailto:')):assert (p.parent/url.split('#')[0]).exists(),(p,url)
  if rid=='PH-BATH2':
   assert 'Sapphire' in t and ('Matte White' in t or 'MATTE WHITE' in t)
   assert not re.search(r'(?i)selected 48-in brizo|Brizo BNX/Matte White|slop(?:e|ing).*48-in.*linear',t)
   assert 'Duravit' in t and 'tub' in t.lower()
  if rid=='PH-BATH4':
   assert 'BT062415-BNX' in t and 'WALK-IN' in t.upper()
   assert not re.search(r'(?i)selected 48-in brizo|brizo linear drain',t)
   if 'Duravit tub' in t:assert 'no PH-BATH4 Duravit tub' in t or 'no Duravit tub' in t
  if rid=='PH-PRIMARY':assert 'NO PRIMARY NICHE' in t or 'NO NICHE' in t
print('PASS six original R010 candidate SHA and neutral evidence, room-specific fixtures; immutable submission scores null and separately scored room registry as applicable')

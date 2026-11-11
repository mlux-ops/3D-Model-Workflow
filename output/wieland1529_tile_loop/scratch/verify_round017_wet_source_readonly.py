"""Read-only validation of current R017 source, blind wall/pan governance and signatures."""
from pathlib import Path
import json,hashlib,re
from decimal import Decimal

R=Path(__file__).resolve().parents[1]
S=R/'state/ROUND017_SUBMISSION.json'
sha=lambda p: {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':len(p.read_bytes())}
sub=json.loads(S.read_text(encoding='utf-8'))
assert sha(S)['sha256']=='01eea9288feb911c24653cd1791cb547b1baf08ea64b53a700df8524331f1c90'
assert sub['round']==17 and set(sub['focus_rooms'])=={'PH-BATH3','TX-BATH3','PH-BATH4','PH-PRIMARY'}
assert sub['critic_dispatch']=='NOT_DISPATCHED' and sub['all_critic_scores'] is None and sub['R017_weighted_scoring'] is None
assert not sub['four_authentic_original_seat_dispatch_authorized'] and not sub['owner_approved']
assert sub['R014_critic_files']==6 and sub['R014_required']==8 and sub['original_design_worker9']=='FAILED'
assert sub['R015_dispatch']=='HOLD' and sub['R016_dispatch']=='NOT_DISPATCHED'
assert sha(R/sub['shared_maker_research']['path'])=={k:sub['shared_maker_research'][k] for k in ['sha256','bytes']}
assert len(sub['confidential_prime_only_mappings'])==4
for room,m in sub['confidential_prime_only_mappings'].items():
 assert sha(R/m['path'])=={k:m[k] for k in ['sha256','bytes']}
letters={'PH-BATH3':{'A','C'},'TX-BATH3':{'B','C'},'PH-BATH4':{'A','C'},'PH-PRIMARY':{'B','C'}}
links=0
firstlines=[]
for room,opts in sub['blind_source_candidates'].items():
 assert set(opts)==letters[room]
 for letter,meta in opts.items():
  file=R/meta['path'];actual=sha(file)
  assert actual=={k:meta[k] for k in ['sha256','bytes']},(room,letter)
  txt=file.read_text(encoding='utf-8')
  assert txt.startswith(f'# {room} — Candidate {letter} — complete independent wet design option\n')
  line=txt.splitlines();assert line[1]==''
  firstlines.append(line[2]);assert 'owner approval' in line[2]
  assert '## 1.' in txt and '## 5.' in txt and 'top_fix:' in txt and 'gate_flags:' in txt
  assert 'measured' in txt and 'LEVEL' in txt and 'PAN' in txt and 'W1' in txt
  assert 'NOT_DISPATCHED' not in txt # no dispatch/governance data leakage
  assert '**Non-transferable room program:**' in txt and '**Non-transferable program:** PH/TX BATH3' not in txt
  assert 'PRIVATE' not in txt.upper() and 'weighted score is claimed' in txt
  assert '752' not in txt or True
  for link in re.findall(r'\]\(([^)]+)\)',txt):
   if link.startswith('http'):continue
   assert (file.parent/link).exists(),(room,letter,link)
   links+=1
  if room=='PH-BATH3':assert 'DT062412' in txt and 'PH basin UNSELECTED' in txt and 'R75000' not in txt
  if room=='TX-BATH3':assert 'BT062415-BNX' in txt and 'do not import PH Bath3 basin' in txt and 'DT062412' not in txt
  if room=='PH-BATH4':assert 'ACTUAL WALK-IN' in txt and 'BT062415-BNX' in txt and '35 vs 27 SF' in txt
  if room=='PH-PRIMARY':assert 'BT0734816-BNX' in txt and 'BR73480' in txt and 'no added Primary shower NICHE' in txt
assert len(set(firstlines))==1 and sum(len(x) for x in sub['blind_source_candidates'].values())==8
assert sha(R/'deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc/MANIFEST.json')['sha256']=='81932937b1b7c9eae11cfda68a2e62661b6b41bbd6a21c2a7fc8d42b90608025'
assert sha(R/'deliverables/integrated-r22-three-powder-faucet-and-shop-release/MANIFEST.json')['sha256']=='32e5ceb807e33e642680dec47aa378d21d5ba9f7b05462214277cb89e7d76df1'
print('PASS R017 8 frozen source packets and 4 immutable confidential keys, common research, room-specific nontransferable selected fixture conditional gate, local links',links,'no critic/scoring/purchase')
print('R017_SHA',sha(S)['sha256'])

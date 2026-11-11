"""Non-mutating PH R013 source preflight. Role keys and scores are not inspected."""
from pathlib import Path
import re
import hashlib

ROOT = Path(__file__).resolve().parents[1]
cases = {'PH-PRIMARY': {'A','B'},'PH-BATH2': {'B','C'},'PH-BATH4': {'A','C'}}
disclaimer = 'This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.'
url = re.compile(r'\]\(([^)]+)\)')
bad_roles = re.compile(r'(?i)\b(?:incumbent|challenger|historical candidate|revised candidate|previous critic|round010|round-010|compared to candidate|source option|this challenger|champion)\b')
links = 0
for rid, letters in cases.items():
 paths = sorted((ROOT/f'rooms/{rid}/board/round-013/candidates').glob('*.md'))
 assert {p.stem for p in paths} == letters, (rid, paths)
 sizes = []
 for p in paths:
  b = p.read_bytes(); t = b.decode('utf-8'); lines = t.splitlines(); sizes.append(len(b))
  assert lines[0] == f'# {rid} — Candidate {p.stem} — complete tile design option'
  assert lines[1] == '' and lines[2] == disclaimer
  assert t.count('|---|---|---|---|---|') == 1
  assert t.count('| ') >= 5 and t.count('## ') == 5
  assert not bad_roles.search(t), (p, bad_roles.findall(t))
  for target in url.findall(t):
   if target.startswith('http'): continue
   assert (p.parent/target).resolve().is_file(), (p,target)
   links += 1
  assert all(s in t for s in ['15%', 'DCOF', 'owner', 'null', '2026-09-03', 'Chicago'])
  print(rid,p.stem,'bytes',len(b),'sha256',hashlib.sha256(b).hexdigest(),'local_links',len([x for x in url.findall(t) if not x.startswith('http')]))
 assert max(sizes)/min(sizes) < 1.17, (rid,sizes)
 assert all(not (ROOT/f'rooms/{rid}/board/round-013/{n}').exists() for n in ('critic-market.md','critic-design.md','critic-build.md','critic-cost.md'))
print('PASS 6 neutral R013 PH source packets, 3 room-pairs, source links',links,'zero existing critiques/roles in visible text; no scoring')

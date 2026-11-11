"""Read-only eight authentic R014 critic reports, printed arithmetic and evidence SHA.
Do not read private mappings, prior scored files or weight and do not mutate reports.
"""
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
import re,hashlib,json
R=Path(__file__).resolve().parents[1]
source=R/'state/ROUND014_SUBMISSION.json'
dispatch=R/'state/ROUND014_CRITIC_DISPATCH.json'
s=json.loads(source.read_text(encoding='utf-8'))
d=json.loads(dispatch.read_text(encoding='utf-8'))
assert s['all_critic_scores'] is None and s['weighted_scoring'] is None
assert d['all_critic_scores'] is None and d['weighted_scoring'] is None
assert d['source_submission_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
assert d['room_ids']==s['rooms']
seats={'market':4,'design':5,'build':5,'cost':5}
result={}
missing=[]
criterion=means=links=0
for rid,letters in s['candidate_files'].items():
 root=R/'rooms'/rid/'board/round-014'
 for letter,record in letters.items():
  b=(R/record['file']).read_bytes()
  assert hashlib.sha256(b).hexdigest()==record['sha256'] and len(b)==record['bytes']
 result[rid]={}
 for seat,needed in seats.items():
  path=root/f'critic-{seat}.md'
  if not path.exists():
   missing.append((rid,seat))
   continue
  b=path.read_bytes()
  t=b.decode('utf-8')
  assert not re.search(r'(?i)_key\.json|state/ROOMS\.json|state/LEDGER\.md|ROUND014_SCORING\.json',t),(rid,seat)
  blocks=re.split(r'(?im)^##\s+(?:Neutral\s+)?Candidate\s+([A-Z])\b[^\n]*\n',t)
  assert len(blocks)==5 and set(blocks[1::2])==set(letters),(rid,seat,'sections')
  ratings={}
  for letter,block in zip(blocks[1::2],blocks[2::2]):
   vals=[]
   for line in block.splitlines():
    if not line.startswith('|'):continue
    cells=[c.strip() for c in line.strip('|').split('|')]
    if len(cells)!=3:continue
    v=re.sub(r'\s*/\s*5(?:\.0)?\s*$','',cells[1].replace('**','')).strip()
    if re.fullmatch(r'[1-5](?:\.\d+)?',v):
     assert len(cells[2])>=30 and ('[' in cells[2] or 'http' in cells[2]),(rid,letter,seat,'criterion unlinked')
     vals.append(Decimal(v))
   assert len(vals)==needed,(rid,letter,seat,vals)
   mean=(sum(vals,Decimal('0'))/Decimal(needed)).quantize(Decimal('0.1'),rounding=ROUND_HALF_UP)
   assert all(z in block.lower() for z in ('top_fix','gate_flags','confidence')),(rid,letter,seat)
   assert any(str(mean) in line for line in block.splitlines() if 'mean' in line.lower() or 'overall' in line.lower()),(rid,letter,seat,'arithmetic printed',mean)
   ratings[letter]={'criterion_values':[float(z) for z in vals],'arithmetic_mean':float(mean)}
   criterion+=needed;means+=1
  for link in re.findall(r'\]\(([^)]+)\)',t):
   if link.startswith(('http:','https:','#','mailto:')):continue
   assert (root/link.split('#')[0]).exists(),(rid,seat,link)
   links+=1
  result[rid][seat]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),
    'worker_id':d['worker_seats']['critic-'+seat],
    'candidate_letters':sorted(letters),
    'unweighted_independent_criteria':ratings}
print('R014_READ_ONLY',json.dumps({'original_critic_reports':sum(len(v) for v in result.values()),'missing':missing,'individual_criteria':criterion,'unweighted_means':means,'local_links':links,'reports':result},indent=2))
assert not (R/'state/ROUND014_SCORING.json').exists()
if missing:raise SystemExit('R014 critic collection not complete. DO NOT SCORE.')
assert len(result)==2 and sum(len(v) for v in result.values())==8
assert criterion==76 and means==16
print('PASS eight original specialist reports/76 criteria/16 arithmetic means; no weighted R014 score or owner/GC release')

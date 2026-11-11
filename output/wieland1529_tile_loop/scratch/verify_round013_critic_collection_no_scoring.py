"""Read-only R013 12 authentic independent reports/criterion math; NEVER weights or source roles."""
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
import hashlib,json,re,sys

ROOT=Path(__file__).resolve().parents[1]
sub=json.loads((ROOT/'state/ROUND013_SUBMISSION.json').read_bytes())
dis=json.loads((ROOT/'state/ROUND013_CRITIC_DISPATCH.json').read_bytes())
assert sub['all_critic_scores'] is None and dis['all_critic_scores'] is None
assert not (ROOT/'state/ROUND013_SCORING.json').exists()
expected={'PH-PRIMARY':{'A','B'},'PH-BATH2':{'B','C'},'PH-BATH4':{'A','C'}}
n_criteria={'market':4,'design':5,'build':5,'cost':5}
partial='--partial' in sys.argv
report={};criterion_count=0;seat_means=0;linked=0;missing=[]
for rid,letters in expected.items():
 assert set(sub['candidate_files'][rid])==letters
 path=ROOT/'rooms'/rid/'board/round-013'
 report[rid]={}
 for seat,n in n_criteria.items():
  p=path/f'critic-{seat}.md'
  if not p.is_file():
   assert partial, f'WAIT {rid} {seat} report absent'
   missing.append(f'{rid}/{seat}')
   continue
  b=p.read_bytes(); t=b.decode('utf-8')
  for target in re.findall(r'\]\(([^)]+)\)',t):
   if target.startswith(('https://','http://','#','mailto:')):continue
   assert (path/target.split('#')[0]).resolve().is_file(),(rid,seat,target)
   linked+=1
  chunks=re.split(r'(?im)^##\s+(?:Neutral\s+)?Candidate\s+([A-Z])\b[^\n]*\n',t)
  assert len(chunks)==5,(rid,seat,'expected two neutral candidate sections',len(chunks))
  assert set(chunks[1::2])==letters,(rid,seat,chunks[1::2])
  report[rid][seat]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'candidate_unweighted_means':{}}
  for letter,section in zip(chunks[1::2],chunks[2::2]):
   values=[]
   for line in section.splitlines():
    if not line.startswith('|'): continue
    cells=[c.strip() for c in line.strip('|').split('|')]
    if len(cells)!=3:continue
    score=re.sub(r'\s*/\s*5(?:\.0)?\s*$','',cells[1].replace('**','').strip())
    if re.fullmatch(r'[1-5](?:\.\d+)?',score):
     assert len(cells[2])>30 and '[' in cells[2],(rid,seat,letter,'criterion missing individual evidence source')
     values.append(Decimal(score))
   assert len(values)==n,(rid,seat,letter,'number criteria',len(values))
   calc=(sum(values,Decimal(0))/Decimal(n)).quantize(Decimal('0.1'),rounding=ROUND_HALF_UP)
   for key in ('top_fix','gate_flags','confidence'):
    assert key in section.lower(),(rid,seat,letter,key)
   # Generic mean representations; an independently computed value is recorded without weighting.
   assert re.search(r'(?i)(?:overall|seat mean|arithmetic|mean|average|score)',section),(rid,seat,letter,'missing mean declaration')
   report[rid][seat]['candidate_unweighted_means'][letter]=str(calc)
   criterion_count+=n; seat_means+=1

if partial:
 assert seat_means>=18 and criterion_count>=84
else:
 assert not missing and criterion_count==114 and seat_means==24
print('PASS R013',seat_means//2,'own-seat reports, 6 source-frozen candidates,',criterion_count,'independently recomputed criterion values/',seat_means,'arithmetic means,',linked,'valid local citations; NO private roles, weights, scoring or release applied; absent',missing)
print(json.dumps(report,indent=2))

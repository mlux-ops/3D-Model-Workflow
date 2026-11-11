"""Independent R034 four-seat rubric arithmetic from original critic criterion rows."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import re,json

ROOT=Path(__file__).resolve().parents[1]
ROOMS=('PH-BATH4','PH-BATH3','TX-BATH3')
WEIGHTS={'market':Decimal('.30'),'design':Decimal('.25'),'build':Decimal('.25'),'cost':Decimal('.20')}
SIZES={'market':4,'design':5,'build':5,'cost':5}
Q=lambda x:x.quantize(Decimal('.1'),rounding=ROUND_HALF_UP)
line_table=re.compile(r'^\|[^|]+\|\s*(?:\*\*)?([1-5](?:\.\d+)?)(?:\s*/\s*5)?(?:\*\*)?\s*\|')
line_numbered=re.compile(r'^\s*\d+[.)]\s+.+?\s+[—–-]\s*([1-5](?:\.\d+)?)\s*/\s*5\b')
out={}
count=0
for id in ROOMS:
 scores={}
 for seat,weight in WEIGHTS.items():
  p=ROOT/'rooms'/id/'board'/'round-034'/('critic-'+seat+'.md')
  t=p.read_text(encoding='utf-8-sig')
  parts=re.split(r'(?m)^## Candidate ([AB])\b[^\n]*\n',t)
  assert len(parts)==5,(id,seat,len(parts))
  assert set([parts[1],parts[3]])=={'A','B'},(id,seat,parts[1::2])
  for i in (1,3):
   letter=parts[i]
   section=parts[i+1]
   vals=[]
   for line in section.splitlines():
    m=line_table.match(line) or line_numbered.match(line)
    if m: vals.append(Decimal(m.group(1)))
   assert len(vals)==SIZES[seat],(id,seat,letter,vals)
   assert all(Decimal(1)<=x<=Decimal(5) for x in vals)
   count+=len(vals)
   mean=Q(sum(vals)/Decimal(len(vals)))
   assert all(re.search(w,section,re.I) for w in ('top_fix','gate_flags','confidence')),(id,seat,letter)
   quoted=[Decimal(x) for x in re.findall(r'(?:seat_mean|Arithmetic mean|Overall .*?(?:mean|score))[^\n]{0,100}?([1-5]\.\d)\s*/\s*5',section,re.I)]
   if quoted:assert mean in quoted,(id,seat,letter,str(mean),quoted)
   scores.setdefault(letter,{})[seat]={'criteria':[str(x) for x in vals],'mean':str(mean)}
 for letter in ('A','B'):
  means=[Decimal(scores[letter][seat]['mean']) for seat in WEIGHTS]
  weighted=sum(Decimal(scores[letter][s]['mean'])*w for s,w in WEIGHTS.items()).quantize(Decimal('.001'))
  scores[letter]['weighted']=str(weighted)
  scores[letter]['minimum_seat']=str(min(means))
  scores[letter]['specialist_gate_pass']=min(means)>=3
 out[id]=scores
assert count==114,count
print(json.dumps({'criterion_count':count,'seat_means_count':24,'weighted_count':6,'room_boards':out},indent=2))

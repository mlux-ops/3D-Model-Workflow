from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import re, json
ROOT = Path(__file__).resolve().parents[1]
ROOMS = ['PH-BATH2','TX-BATH2','TX-BATH3','TX-BATH4']
WEIGHTS = {'market':Decimal('.30'),'design':Decimal('.25'),'build':Decimal('.25'),'cost':Decimal('.20')}
RX = re.compile(r'^\|[^|]+\|\s*(?:\*\*)?([1-5](?:\.\d+)?)(?:/5)?(?:\*\*)?\s*\|')
Q = lambda x: x.quantize(Decimal('.1'), rounding=ROUND_HALF_UP)
out = {}
for room in ROOMS:
  data = {}
  for seat in WEIGHTS:
    text = (ROOT/'rooms'/room/'board'/'round-031'/('critic-'+seat+'.md')).read_text(encoding='utf-8')
    parts = re.split(r'(?m)^## Candidate ([AB])\b',text)
    assert len(parts)==5, (room,seat,len(parts))
    for i in (1,3):
      letter = parts[i]
      section = parts[i+1]
      vals = [Decimal(m.group(1)) for line in section.splitlines() if (m:=RX.match(line))]
      assert len(vals) in (4,5), (room,seat,letter,vals)
      mean = Q(sum(vals)/len(vals))
      data.setdefault(letter,{})[seat]={'criteria':[float(v) for v in vals], 'mean':float(mean)}
  for letter in ('A','B'):
    assert len(data[letter])==4
    s = sum(Decimal(str(data[letter][seat]['mean']))*wt for seat,wt in WEIGHTS.items())
    data[letter]['weighted'] = float(s.quantize(Decimal('.001')))
    data[letter]['min_seat'] = min(data[letter][seat]['mean'] for seat in WEIGHTS)
    data[letter]['all_seats_at_least_3'] = data[letter]['min_seat'] >=3.0
  out[room] = data
print(json.dumps(out,indent=2))

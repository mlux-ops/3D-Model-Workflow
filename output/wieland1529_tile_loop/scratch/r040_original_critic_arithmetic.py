"""R040 authentic four-seat scoring, source-parsed only; cannot invent a critic."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import json,re

ROOT=Path(__file__).resolve().parents[1]
ROOMS=('TX-POWDER','TX-POWDER2')
WEIGHTS={'market':Decimal('.30'),'design':Decimal('.25'),
         'build':Decimal('.25'),'cost':Decimal('.20')}
SIZE={'market':4,'design':5,'build':5,'cost':5}
Q=lambda x:x.quantize(Decimal('.1'),rounding=ROUND_HALF_UP)
TABLE=re.compile(r'^\|[^|]+\|\s*\*{0,2}([1-5](?:\.\d+)?)\*{0,2}(?:\s*/\s*5)?\s*\|')
UNIFIED=re.compile(r'^\|\s*([AB])\s*\|[^|]+\|\s*\*{0,2}([1-5](?:\.\d+)?)\*{0,2}\s*\|')
NUMBERED=re.compile(r'^\s*\d+[.)]\s+.+?\s+[—–-]\s*([1-5](?:\.\d+)?)\s*/\s*5\b')
out={};count=0;missing=[]
for rid in ROOMS:
    scores={}
    for seat in WEIGHTS:
        path=ROOT/'rooms'/rid/'board'/'round-040'/('critic-'+seat+'.md')
        if not path.is_file():
            missing.append(str(path.relative_to(ROOT)))
            continue
        t=path.read_text(encoding='utf-8-sig')
        assert all(re.search(f,t,re.I) for f in ('top[_ ]fix','gate[_ ]flags','confidence')),(rid,seat,'missing review fields')
        sections=re.split(r'(?mi)^## (?:Neutral\s+)?Candidate\s+([AB])\b[^\n]*\n',t)
        if len(sections)==5:
            pairs={}
            for i in (1,3):
                letter,body=sections[i],sections[i+1]
                vals=[]
                for line in body.splitlines():
                    match=TABLE.match(line) or NUMBERED.match(line)
                    if match:vals.append(Decimal(match.group(1)))
                pairs[letter]=(vals,body)
        else:
            grouped={'A':[],'B':[]}
            for line in t.splitlines():
                match=UNIFIED.match(line)
                if match:grouped[match.group(1)].append(Decimal(match.group(2)))
            pairs={letter:(vals,t) for letter,vals in grouped.items()}
        assert set(pairs)=={'A','B'},(rid,seat,pairs.keys())
        for letter,(values,body) in pairs.items():
            assert len(values)==SIZE[seat],(rid,seat,letter,values)
            assert all(Decimal(1)<=x<=Decimal(5) and x==x.to_integral_value() for x in values),(rid,seat,letter,'criterion must be integer 1..5',values)
            mean=Q(sum(values)/Decimal(len(values)))
            # Where a mean is explicitly printed, it must agree with source ratings.
            for raw in re.findall(r'(?mi)^(?:\*\*)?(?:Seat mean|Arithmetic (?:seat )?mean|Overall mean)\b[^\n]*?=\s*\*{0,2}([1-5]\.\d)(?:\s*/\s*5)?',body):
                assert Decimal(raw)==mean,(rid,seat,letter,'declared mean mismatch',mean,raw)
            scores.setdefault(letter,{})[seat]={'criteria':[str(x) for x in values],'mean':str(mean)}
            count+=len(values)
    for letter in ('A','B'):
        if len(scores.get(letter,{}))==4:
            vals=[Decimal(scores[letter][s]['mean']) for s in WEIGHTS]
            weighted=sum(Decimal(scores[letter][s]['mean'])*w for s,w in WEIGHTS.items())
            scores[letter]['weighted']=str(weighted.quantize(Decimal('.001')))
            scores[letter]['minimum_seat']=str(min(vals))
            scores[letter]['specialist_gate_pass']=min(vals)>=3
    out[rid]=scores
if missing:
    print(json.dumps({'status':'INCOMPLETE','missing':missing,'criteria_present':count,'room_boards':out},indent=2))
    raise SystemExit(2)
assert count==76,count
assert sum(len([s for s in out[r][l] if s in WEIGHTS]) for r in ROOMS for l in ('A','B'))==16
print(json.dumps({'status':'PASS','criterion_count':76,'seat_means_count':16,'weighted_count':4,'room_boards':out},indent=2))

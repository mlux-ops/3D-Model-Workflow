"""Check six new neutral A/B source files before any independent worker sees them."""
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
import json,re

ROOT=Path(__file__).resolve().parents[1]
ROOMS=('PH-BATH2','TX-BATH2','TX-BATH4')
for room in ROOMS:
 cand=ROOT/'rooms'/room/'board'/'round-035'/'candidates'
 a,b=(cand/(x+'.md') for x in ('A','B'))
 assert all(p.is_file() for p in (a,b))
 texts=[p.read_text(encoding='utf-8-sig') for p in (a,b)]
 assert all(len(t)>7000 for t in texts),(room,[len(t) for t in texts])
 assert all(len(t.splitlines())>=24 for t in texts),room
 for letter,t in zip(('A','B'),texts):
  assert t.startswith('# R035 neutral candidate '+letter+' — '+room),room
  assert t.count('| WET TUB WALL')==1 and t.count('| Bathroom LEVEL only')==1,room
  assert t.count('| Existing/conditional NICHE')==1 and t.count('| Tiled PAN / Shower drain / tiled CEILING')==1
  assert 'NO tiled PAN' in t or 'NO tiled shower PAN' in t or 'no tiled PAN' in t
  assert 'Floor YES' in t and 'DCOF >=0.42' in t
  assert 'Owner' in t or 'owner' in t
  assert '15%' in t and 'Chicago' in t
  assert 'TILE-SELECTION' not in t
  assert not re.search(r'\bR0(?:30|31|32|33|34)\b',t)
  assert not any(p in t for p in ('state/ROOMS.json','state/LEDGER.md','/_key.json','champion.md','history.md','critic-design.md','critic-build.md','critic-cost.md','critic-market.md'))
  assert 'research/products/R030_NINE_ROOM' not in t
  urls=set(re.findall(r'https://[^)\s>]+',t))
  assert len(urls)>=10,(room,letter,len(urls))
 assert abs(len(texts[0])-len(texts[1]))<1200,(room,'blind packet unbalanced')
 print(room,'PASS 2 neutral candidates, no prior role leaks; all actual TUB with NO PAN, product links and cost basis',flush=True)
print('PASS R035 3 rooms/6 full product A/B sources. Await R034 Reviewer verdict before blind critic dispatch.')

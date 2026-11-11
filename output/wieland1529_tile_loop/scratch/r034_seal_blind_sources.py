"""One-time blind A/B assignment and source validation; do not rerun after dispatch."""
from pathlib import Path
import json
import re
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
IDS=['PH-BATH4','PH-BATH3','TX-BATH3']
for id in IDS:
 p=ROOT/'rooms'/id/'board'/'round-034'
 a,b=p/'candidates'/'A.md',p/'candidates'/'B.md'
 assert a.is_file() and b.is_file()
 key=p/'_key.json'
 assert not key.exists(), (id,'already sealed')
 av,bv=a.read_text(encoding='utf-8'),b.read_text(encoding='utf-8')
 assert av.startswith(f'# R034 neutral candidate A — {id}')
 assert bv.startswith(f'# R034 neutral candidate B — {id}')
 # Alternate assignment on PH-BATH3 means incumbents are not all letter A.
 if id=='PH-BATH3':
  av,bv=bv.replace('candidate B —','candidate A —',1),av.replace('candidate A —','candidate B —',1)
  a.write_text(av,encoding='utf-8');b.write_text(bv,encoding='utf-8')
  incumbent='B'
 else:
  incumbent='A'
 for f in (a,b):
  t=f.read_text(encoding='utf-8')
  # Do not expose a prior-round-named photographic research filename to blind seats.
  neutral=t.replace('research/comps/R030_AUTHENTIC_OLD_TOWN_PHOTOGRAPHIC_EVIDENCE_20261107.md','research/comps/COMPS.md')
  if neutral!=t:
   f.write_text(neutral,encoding='utf-8')
   t=neutral
  assert len(t)>6500,(id,f,len(t))
  assert t.count('| WET WALL field |')==1 and t.count('| Bathroom dry/wet LEVEL |')==1
  assert t.count('| Existing or conditional wet NICHE')==1
  assert 'Old Town' in t and 'wet DCOF >=0.42' in t and 'POINT' in t
  assert 'prior score' not in t.lower().split('**strict blind')[0]
  assert 'COST/' not in t
  assert 'state/ROOMS.json' not in t and 'state/LEDGER.md' not in t and '/_key.json' not in t
  assert 'R030' not in t and 'R031' not in t and 'R032' not in t and 'R033' not in t
  urls=re.findall(r'https://[^)\s>]+',t)
  assert len(urls)>=6,(id,f,len(urls))
  assert all(urlparse(u).hostname in {'www.elmsurfaces.com','www.flooranddecor.com','www.msisurfaces.com','store.porcelanosa.com'} for u in urls),(id,f,urls)
 key.write_text(json.dumps({'round':34,'room':id,'incumbent':incumbent,'challenger':('A' if incumbent=='B' else 'B'),
  'source_prepared':'2026-11-07','status':'private_prime_only',
  'notes':'Historically provisional incumbent is not final owner-accepted; apply .25 rule only if genuinely accepted.'},indent=2)+'\n',encoding='utf-8')
 print(id,'blind source PASS','private key generated; not to be read by workers')
print('PASS 6 original neutral sources; three room cohort; ready for authentic independent board')

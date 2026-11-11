"""Read-only 12 original R012 critic file SHA/criterion/mean QA, WITHOUT board weighting."""
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
import json,hashlib,re
R=Path(__file__).resolve().parents[1]
s=json.loads((R/'state/ROUND012_SUBMISSION.json').read_text(encoding='utf-8'))
d=json.loads((R/'state/ROUND012_CRITIC_DISPATCH.json').read_text(encoding='utf-8'))
c=json.loads((R/'state/ROUND012_CRITIC_COLLECTION.json').read_text(encoding='utf-8'))
assert all(x['phase']=='2-board' and x['all_critic_scores'] is None for x in (s,d,c))
assert not (R/'state/ROUND012_SCORING.json').exists()
expected={
'TX-PRIMARY':{'B':{'market':3.5,'design':3.0,'build':2.0,'cost':2.4},'C':{'market':3.7,'design':3.8,'build':2.6,'cost':2.2}},
'TX-BATH2':{'A':{'market':3.7,'design':4.0,'build':3.0,'cost':2.6},'C':{'market':3.7,'design':3.4,'build':2.6,'cost':2.8}},
'TX-BATH4':{'A':{'market':3.4,'design':2.8,'build':2.4,'cost':2.2},'B':{'market':3.7,'design':3.8,'build':2.8,'cost':2.4}}
}
counts={'market':4,'design':5,'build':5,'cost':5}
criteria=0;means=0;local=0
for rid,letters in expected.items():
 folder=R/'rooms'/rid/'board/round-012'
 assert set(letters)==set(s['candidate_files'][rid])
 for seat,n in counts.items():
  p=folder/f'critic-{seat}.md';raw=p.read_bytes();t=raw.decode('utf-8')
  receipt=c['report_files'][rid][seat]
  assert hashlib.sha256(raw).hexdigest()==receipt['sha256'] and len(raw)==receipt['bytes']
  for link in re.findall(r'\]\(([^)]+)\)',t):
   if link.startswith(('https://','http://','#','mailto:')):continue
   assert (folder/link.split('#')[0]).exists(),(rid,seat,link)
   local+=1
  splits=re.split(r'(?im)^##\s+Candidate\s+([A-Z])\b[^\n]*\n',t)
  assert len(splits)==5,(rid,seat,'expected 2 lettered sections')
  assert set(splits[1::2])==set(letters)
  for letter,block in zip(splits[1::2],splits[2::2]):
   values=[]
   for line in block.splitlines():
    if not line.startswith('|'):continue
    cells=[x.strip() for x in line.strip('|').split('|')]
    if len(cells)!=3:continue
    z=cells[1].replace('*','')
    z=re.sub(r'\s*/\s*5(?:\.0)?\s*$','',z).strip()
    if re.fullmatch(r'[1-5](?:\.\d+)?',z):
     assert len(cells[2])>35 and ('[' in cells[2] or 'http' in cells[2]),(rid,letter,seat,'unlinked criterion')
     values.append(Decimal(z))
   assert len(values)==n,(rid,seat,letter,'actual criterion count',len(values))
   score=(sum(values,Decimal(0))/Decimal(n)).quantize(Decimal('0.1'),rounding=ROUND_HALF_UP)
   assert score==Decimal(str(expected[rid][letter][seat])),(rid,seat,letter,score,expected[rid][letter][seat])
   assert all(k in block.lower() for k in ('top_fix','gate_flags','confidence'))
   criteria+=n;means+=1
assert criteria==114 and means==24 and local==c['local_links'],(criteria,means,local,c['local_links'])
print('PASS R012 12 authentic frozen critics, 6 candidate SHA, 114 individual criteria, 24 independent unweighted one-decimal means and',local,'local evidence links; NO weighted board scoring')

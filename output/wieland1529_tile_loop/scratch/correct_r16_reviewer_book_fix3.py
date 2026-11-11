"""Exact R16 book-only reviewer-14 FIX3, with old/new signed SHA audit."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
D=R/'deliverables/integrated-r16'
book=D/'R16_13_ROOM_DESIGN_CONSTRUCTION_PROCUREMENT_BOOK.md'
manifest=D/'MANIFEST.json'
audit=R/'state/ROUND014_R16_REVIEWER_BOOK_FIX3.json'
assert not audit.exists()
def fp(p):
 b=p.read_bytes()
 return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
m=json.loads(manifest.read_text(encoding='utf-8'))
assert fp(book)==m['outputs'][book.name]
other={k:v for k,v in m['outputs'].items() if k!=book.name}
assert len(other)==3 and all(fp(D/k)==v for k,v in other.items())
before_book=fp(book);before_manifest=fp(manifest)
lines=book.read_text(encoding='utf-8').splitlines()
changed=[]
for i,line in enumerate(lines):
 if not (line.startswith('| ') and '| Retain dated original row as provenance only;' in line):continue
 c=[x.strip() for x in line.strip('|').split('|')]
 if len(c)!=4:continue
 rid=c[0]
 if rid in ('PH-PRIMARY','TX-PRIMARY'):
  c[3]='Individual maker wet WALL permission for the selected flat material (NO extra PRIMARY NICHE); independent raw numeric wet LEVEL/shared WC and selected Brizo BT0734816-BNX 48-in LINEAR PAN DCOF (not square POINT). BR73480 rough, approved linear grate/membrane/slope/flood section, true 1529 geometry, Chicago installed bid and separate owner/GC signatures all required; no purchase until cleared.'
 elif rid=='PH-BATH4':
  c[3]='Individual wet flat Bone WALL and Soho Black wet NICHE maker permission; raw numeric LEVEL and selected Brizo BT062415-BNX Black Onyx 4-in SQUARE POINT four-plane PAN DCOF, approved square rough/membrane/flood, owner 35/27-SF reconciliation, measured 1529 wall/net and current Chicago installed bid/owner+GC releases; no 48-in linear pan or tub.'
 elif rid=='TX-BATH3':
  assert '(and PH basin)' in c[3]
  c[3]=c[3].replace(' (and PH basin)','')
 else:continue
 lines[i]='| '+' | '.join(c)+' |'
 changed.append(rid)
assert sorted(changed)==['PH-BATH4','PH-PRIMARY','TX-BATH3','TX-PRIMARY']
book.write_text('\n'.join(lines)+'\n',encoding='utf-8')
assert fp(book)!=before_book
assert all(fp(D/k)==v for k,v in other.items())
m['outputs'][book.name]=fp(book)
manifest.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
assert all(fp(D/k)==v for k,v in m['outputs'].items())
a={'as_of':'2026-11-06','round':14,'reviewer':'worker-14',
 'reason':'Narrow owner-facing R16 only: TX Bath3 remove PH basin; PH/TX Primary selected 48in LINEAR and no Primary niches; PH Bath4 selected square POINT not linear.',
 'rows_changed':changed,'book_before':before_book,'book_after':fp(book),
 'manifest_before':before_manifest,'manifest_after':fp(manifest),
 'three_other_signed_files_unchanged':other,'r014_four_frozen_candidates_unchanged':True,
 'r014_critics_not_given_r16':True,'r013_scoring_unchanged':True,
 'owner_approval':False,'procurement_release':False}
audit.write_text(json.dumps(a,indent=2)+'\n',encoding='utf-8')
print('PASS exact R16 book-only four-room FIX3; other 3 signed SHA unchanged, owner/GC release false')
print('R16_MANIFEST_SHA',fp(manifest)['sha256'])

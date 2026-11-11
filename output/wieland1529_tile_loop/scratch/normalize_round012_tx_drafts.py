"""Pre-freeze editorial source/role-neutrality corrections to six R012 drafts only."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
files=sorted((R/'rooms').glob('TX-*/board/round-012/candidates/*.md'))
assert len(files)==6
replace={
 'Soft+Ribbed relief wet field/ceiling from v4 source':'Soft and Ribbed relief wet field/ceiling according to carried tile schedule',
 'Soft/AntiSlip blended original floor+linear pan':'Soft/AntiSlip blended level+linear pan from carried quote',
 'not specified under v4 primary NO NICHE':'NO PRIMARY NICHE (separate unpriced archived source row excluded)',
 'historic Ribbed individual wet use absent FAIL':'Ribbed relief individual wet use absent FAIL',
 'historic original':'carried',
 'original floor+linear pan':'carried level+linear pan',
 'Alternative Emser [Capisco':'Reference floor evidence: Emser [Capisco',
 'The 3-in small-strip example for 24x48 large-format focal cuts is not transferable verbatim to each 2x20 module; every small-format cut still requires a deliberate mock-up.':'An under-3-in sliver at a focal 24x48 large-format panel warrants re-layout; a 2x20 small-format edge is judged in its own module/adjacency context and still requires a deliberate mock-up.',
 'for source Soft/AntiSlip or proposed Emser bound >=0.60':'for source Soft/AntiSlip or referenced Emser reported >=0.60 lower bound',
 'no unselected sink, change tub to shower or introduce a primary niche':'no unselected basin, change the actual tub/shower program or introduce a primary niche'
}
for f in files:
 s=f.read_text(encoding='utf-8')
 for old,new in replace.items():s=s.replace(old,new)
 if f.parents[3].name=='TX-BATH4':
  s=s.replace('conditional liner/slopes unverified','tub threshold/membrane and floor finish elevation unverified')
 if f.parents[3].name=='TX-BATH2':
  s=s.replace('conditional liner/slopes unverified','tub flange/wall membrane and LEVEL threshold unverified')
 f.write_text(s,encoding='utf-8')
 lines=s.splitlines()
 assert lines[2]=='This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.'
 assert 'from v4 source' not in s and 'not specified under v4' not in s
 print(f.parents[3].name,f.stem,len(f.read_bytes()))
print('PASS R012 6 pre-freeze neutral drafts normalized; no receipt or critics yet')

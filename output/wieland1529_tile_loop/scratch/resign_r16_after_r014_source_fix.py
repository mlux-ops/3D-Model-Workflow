"""Controlled R16 manifest reference to re-frozen corrected R014 source (no output rewrite)."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
M=R/'deliverables/integrated-r16/MANIFEST.json'
sub=R/'state/ROUND014_SUBMISSION.json'
receipt=R/'state/ROUND014_R16_SOURCE_RELINK.json'
assert not receipt.exists()
def fp(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
m=json.loads(M.read_text(encoding='utf-8'))
old=fp(M)
before=m['r014_source_sha256']
assert before!=fp(sub)['sha256']
assert len(m['outputs'])==4 and all(fp(M.parent/n)==v for n,v in m['outputs'].items())
m['r014_source_sha256']=fp(sub)['sha256']
M.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
after=fp(M)
assert all(fp(M.parent/n)==v for n,v in m['outputs'].items())
receipt.write_text(json.dumps({'round':14,'why':'Only R16 signed manifest source pointer updated after independently requested controlled R014 pre-dispatch source FIX1; four signed deliverable file bytes/SHAs untouched','old_r014_source_sha256':before,'new_r014_source_sha256':m['r014_source_sha256'],'old_r16_manifest':old,'new_r16_manifest':after,'four_outputs_unchanged':m['outputs'],'owner_approval':False,'procurement_release':False},indent=2)+'\n',encoding='utf-8')
print('PASS R16 4 file SHA unchanged; source manifest corrected to R014 FIX1 SHA',after['sha256'])

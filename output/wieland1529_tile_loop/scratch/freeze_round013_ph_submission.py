"""One-time R013 three-PH-room blind submission with immutable neutral SHA; no scores."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'state/ROUND013_SUBMISSION.json'
assert not DEST.exists(), 'Round013 already frozen. Do not overwrite or resubmit silently.'
r=subprocess.run([sys.executable,str(ROOT/'scratch/verify_round013_ph_source_preflight.py')],cwd=ROOT,text=True,capture_output=True)
assert r.returncode==0,r.stdout+'\n'+r.stderr

def fingerprint(p):
 b=p.read_bytes()
 return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}

roles={
 'PH-PRIMARY': {'A':'historic v4 Bone Soft/Reed relief, Cortar Bone Soft LEVEL and AntiSlip linear PAN','B':'revised flat Bone, distinct Prime RL21 level/hex linear PAN, Brizo solid grate study'},
 'PH-BATH2': {'B':'revised Sapphire/Sandstone with Prime RL21 12x24 LEVEL and retained Duravit tub','C':'historic v4 Sapphire/Sandstone, Cortar Grey Soft LEVEL, retained Duravit tub'},
 'PH-BATH4': {'A':'revised flat Bone/Soho, Prime RL21 level/hex square PAN, selected Brizo point drain','C':'historic v4 full Ribbed/Caviar/Charcoal source with selected Brizo point drain'},
}
files={}
for rid, key in roles.items():
 d=ROOT/f'rooms/{rid}/board/round-013'
 private=d/'_key.json'
 assert not private.exists()
 private.write_text(json.dumps(key,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 files[rid]={letter:fingerprint(d/'candidates'/f'{letter}.md') for letter in sorted(key)}

receipt={
 'round':13,'as_of':'2026-11-06','phase':'2-board',
 'rooms':list(roles),'candidate_files':files,
 'private_role_keys':{rid:f'rooms/{rid}/board/round-013/_key.json' for rid in roles},
 'historic_source_round':'R010 (PH focus), unchanged',
 'source_basis':'Original source dated 2026-09-03; latest maker product pages/PH RL21 research R13',
 'new_material_changes':'Cross-room RL21 12x24 LEVEL; distinct RL21 hex linear/point PAN; Brizo solid grate primary; individual wet-listed flat wall/niche; dated quote and raw-lab holds explicit',
 'round012_reviewer_clearance':'worker-11 CONTINUE after FIX2, original R012 scored and signed R12/R13 packages untouched',
 'pre_dispatch_reviewer':'pending independent worker-11 read-only',
 'critic_dispatch':'NOT DISPATCHED','critic_reports_present':False,
 'all_critic_scores':None,'weighted_scoring':None,
 'owner_approval':False,'procurement_release':False,
 'revit_1529_verified':False,
 'source_preflight':'PASS neutral 6 source packets/3 pairs, 33 resolved local links, maker-specific and SHA freeze',
 'historic_material_four_units_usd':23572.44,
 'historic_gross_includes_15pct_once':True,
}
DEST.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
assert all(fingerprint(ROOT/f'rooms/{rid}/board/round-013/candidates/{letter}.md')==data for rid,options in files.items() for letter,data in options.items())
print('PASS R013 3 PH room pairs/6 source candidates, private role keys 3, neutral SHA receipt frozen, independent preflight pending, scores NULL')
print('submission SHA',fingerprint(DEST))

"""Create sealed private candidate-role mappings after neutral R035 preflight.

This changes no neutral candidate content and never sends the key to critics.
Only run once, before any R035 worker dispatch.
"""
from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
check=subprocess.run([sys.executable,'-B',str(ROOT/'scratch'/'r035_preflight_three_tub_sources.py')],capture_output=True,text=True,check=True)
assert 'PASS R035 3 rooms/6 full product A/B sources.' in check.stdout
R={'PH-BATH2':('A','B','round-031-A'),
   'TX-BATH2':('B','A','round-031-B'),
   'TX-BATH4':('A','B','round-031-B')}
for id,(inc,challenger,source_id) in R.items():
 path=ROOT/'rooms'/id/'board'/'round-035'/'_key.json'
 assert not path.exists(),(id,'no overwrite/reseal after dispatch')
 d={'room':id,'round':35,'private_only':True,
    'previous_genuine_provisional_board_incumbent_letter':inc,
    'new_challenger_letter':challenger,
    'existing_provisional_champion_identity':source_id,
    'owner_approved':False,
    'displacement_rule':'only previously genuine independent product-board accepted incumbent protected; must >=+.250 and gate pass',
    'source':'R031 authentic 4-seat decisions retained in original source history; no owner approval or new authorizations'}
 path.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
 print('SEALED PRIVATE',id,'critic files must not read _key.json')
print('PASS private incumbent identities sealed; no R035 specialist assigned yet.')

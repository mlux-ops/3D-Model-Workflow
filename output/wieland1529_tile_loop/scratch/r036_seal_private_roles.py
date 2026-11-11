"""Seal R036 private prime-only role maps; NEVER pass to blind R036 critics.

Source preparation only, NOT dispatch nor scoring. R034 incumbent statuses
are unchanged by the unrelated Duravit-tub R035 cohort.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'state'/'ROOMS.json').read_text(encoding='utf-8'))
roles={
 'PH-BATH4':('round-030-B','3.370','A','B'),
 'PH-BATH3':('round-030-A','3.570','B','A'),
 'TX-BATH3':('round-031-B','3.590','A','B'),
}
for rid,(champ,score,inc,ch) in roles.items():
 r=next(x for x in d['rooms'] if x['id']==rid)
 assert r['status']=='provisional champion' and r['champion_id']==champ
 assert f"{r['champion_score']:.3f}"==score
 assert r['owner_status'] is None
 root=ROOT/'rooms'/rid/'board'/'round-036'
 assert (root/'candidates'/'A.md').is_file() and (root/'candidates'/'B.md').is_file()
 dst=root/'_key.json'
 assert not dst.exists(),('R036 role mapping already sealed; do not silently overwrite',dst)
 doc={
  'room':rid,'round':36,'private_only':True,
  'previous_genuinely_product_board_qualified_provisional_incumbent':champ,
  'previous_same_room_current_score':'R034 '+score,
  'incumbent_neutral_letter':inc,'new_material_challenger_neutral_letter':ch,
  'blind_workers_may_read_this':False,
  'owner_approved':False,
  'threshold':'+0.250 same-round weighted displacement ONLY against qualifying prior product-board incumbent',
  'status':'SEALED BEFORE FOUR-SEAT DISPATCH; R035 INDEPENDENT REVIEW VERDICT STILL PENDING; NO R036 CRITIC ASSIGNED'
 }
 dst.write_text(json.dumps(doc,indent=2)+'\n',encoding='utf-8')
 print(rid,'private mapping sealed; critic candidate files unchanged')
print('PASS three R036 role mappings sealed but no board dispatched and no scores fabricated')

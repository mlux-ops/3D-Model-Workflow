"""Sign additive R026 TX research and owner-preview evidence, never past sources."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
out=R/'state/ROUND026_TX_FOUR_SCHEMES_TWO_OWNER_CARDS_SIGNED.json'
assert not out.exists()
paths=['research/products/R026_TX_WET_BATH_SOURCED_SELECTION_COMPARISON.md',
       'deliverables/r026-two-TX-source-decision-addenda-PROVISIONAL/TX-PRIMARY.md',
       'deliverables/r026-two-TX-source-decision-addenda-PROVISIONAL/TX-BATH3.md']
original=R/'state/ROUND026_TWO_TX_WET_BATHS_PREPARED_NOT_SUBMITTED.json'
previous=json.loads(original.read_text(encoding='utf8'))
files=dict(previous['neutral_options'])
assert len(files)==4
for rel,meta in files.items():
 b=(R/rel).read_bytes()
 assert len(b)==meta['bytes'] and hashlib.sha256(b).hexdigest()==meta['sha256']
for rel in paths:
 b=(R/rel).read_bytes()
 files[rel]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
parents={}
for rel in ('state/ROUND026_TWO_TX_WET_BATHS_PREPARED_NOT_SUBMITTED.json',
            'state/ROUND025_FOUR_AUTHENTIC_CRITIC_DISPATCH.json',
            'state/ROUND024_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json'):
 b=(R/rel).read_bytes()
 parents[rel]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
out.write_text(json.dumps({'round':26,'phase':'SOURCE_PREPARED_NOT_SUBMITTED_R025_ACTIVE',
 'rooms':['TX-PRIMARY','TX-BATH3'],'files':files,'parents':parents,
 'original_historical_four_unit_material_usd':23572.44,
 'source_waste_applied_once_pct':15,
 'TX_BATH3_owner_program':'TUB_vs_WALKIN_UNSELECTED',
 'preflight':None,'critic_dispatch':None,'weighted_score':None,'champion_changes':False,
 'owner_approval':False,'global_DONE':False},indent=2)+'\n',encoding='utf8',newline='\n')
print('R026 signed',len(files),'files and',len(parents),'parents; no formal phase overlap')

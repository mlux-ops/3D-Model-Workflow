from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
receiptpath=R/'state/ROUND009_SUBMISSION.json';receipt=json.loads(receiptpath.read_text(encoding='utf-8'))
assert receipt['all_critic_scores'] is None
repls={
'TX-PRIMARY':{
'- Wet walls: product-specific wet listing required, not collection-wide. Flat Cortar Clay and Charcoal maker Wet Areas listed; Clay Ribbed/Bone Ribbed individual pages say Walls/Back Splashes only; Clara Caviar collection listing omits Wet Areas. Thus relief/Caviar in actual wet zone remains FAIL. Copper/Sandstone maker individual wet-use is documented in project records; retain actual finish control.':
'- Wet walls: product-specific listing governs this Clay shower. Cortar Clay flat Wet Areas PASS for wall application; Cortar Clay Ribbed individually lists Walls/Back Splashes, NOT Wet Areas, so the historic wet relief remains FAIL pending exact written manufacturer approval. No wet-wall approval inferred for a different texture or finish.',
'- Wet bath level floor: ELM Cortar Clay Soft / Bone Soft / mixed Anti-Slip per room has no published exact measured ANSI wet DCOF >=0.42 for selected finish and format. FAIL pending maker dated exact report. Large-format 24x48 cannot be presumed to slope to selected linear drain.':
'- Wet bathroom/WC level floor and shower pan: blended historic Cortar Clay Soft and Anti-Slip finishes lack exact measured SKU/finish wet DCOF >=0.42; separate level and linear-drain pan results FAIL. A 24x48 large-format tile cannot be assumed to meet the selected Brizo 48-in linear fall/geometry; actual pan size and slope require design.',
'- Tub vs shower: no extra shower pan is counted in the tub rooms. TX Primary chosen linear drain position/slope and 48-in wall side are not surveyed; manufacturer/product floor compatibility is not established.':
'- Existing 48-in Brizo linear shower: drain side, position, slope, membrane/throat and actual shower-pan gross SF remain null. Any pan format must replace part of existing blended bathroom/WC source floor allowance; do not add a second pan or WC tile amount.',
'- Owner: TX Bath2 basin owner-unselected; all alternatives need sample signoff. No primary niche; TX Bath4 existing tub remains unchanged. No steam discussion.':
'- Owner/fixture authority: preserve selected Brizo Black Onyx and 48-in linear drain, no primary shower niche and no changed fixture specification. Owner sample/finish approval, current contractor bid and room cap are null.',
'Preserve coherent matte white/Black Onyx fixture relationship and avoid speculative high-cost accent layering.':
'Preserve coherent selected Brizo Black Onyx fixture relationship and avoid unapproved high-cost accent layering.'
},
'TX-BATH2':{
'- Wet walls: product-specific wet listing required, not collection-wide. Flat Cortar Clay and Charcoal maker Wet Areas listed; Clay Ribbed/Bone Ribbed individual pages say Walls/Back Splashes only; Clara Caviar collection listing omits Wet Areas. Thus relief/Caviar in actual wet zone remains FAIL. Copper/Sandstone maker individual wet-use is documented in project records; retain actual finish control.':
'- Wet tub walls and niche: ELM Tones Copper 2x20 Glossy and Sandstone 2x20 Glossy are separately recorded as manufacturer Wet Areas-listed (specific color/finish). This does not confirm exact niche back/return/sill quantities, grout, current local stock or owner-selected finish.',
'- Wet bath level floor: ELM Cortar Clay Soft / Bone Soft / mixed Anti-Slip per room has no published exact measured ANSI wet DCOF >=0.42 for selected finish and format. FAIL pending maker dated exact report. Large-format 24x48 cannot be presumed to slope to selected linear drain.':
'- Tiled level bath floor: original Cortar Clay Soft 12x24 lacks exact finish/SKU measured wet DCOF >=0.42 and fails until tested. This is a retained Duravit tub; there is no tiled shower pan, linear-drain slope requirement or extra pan procurement in this room.',
'- Tub vs shower: no extra shower pan is counted in the tub rooms. TX Primary chosen linear drain position/slope and 48-in wall side are not surveyed; manufacturer/product floor compatibility is not established.':
'- Selected tub and source niche: preserve existing Duravit tub and Hansgrohe Chrome fixture package; verify tub flange/membrane, actual tub back/returns, niche opening/back/sill and field-face deduction exactly once. Sink/basin is owner-unselected.',
'- Owner: TX Bath2 basin owner-unselected; all alternatives need sample signoff. No primary niche; TX Bath4 existing tub remains unchanged. No steam discussion.':
'- Owner authority: TX Bath2 sink/basin remains UNSELECTED; actual 1529 geometry and niches and installed material allowance unverified. No owner-approved tile substitution.',
'Preserve coherent matte white/Black Onyx fixture relationship and avoid speculative high-cost accent layering.':
'Preserve the room’s actual Hansgrohe Chrome finish with warm Copper/Sandstone, and avoid unsupported cost escalation.'
},
'TX-BATH4':{
'- Wet walls: product-specific wet listing required, not collection-wide. Flat Cortar Clay and Charcoal maker Wet Areas listed; Clay Ribbed/Bone Ribbed individual pages say Walls/Back Splashes only; Clara Caviar collection listing omits Wet Areas. Thus relief/Caviar in actual wet zone remains FAIL. Copper/Sandstone maker individual wet-use is documented in project records; retain actual finish control.':
'- Wet tub walls and niche: flat Cortar Charcoal maker Wet Areas PASS; historical Bone Ribbed maker lists Walls/Back Splashes only and Clara Caviar collection fails to demonstrate Wet Areas for its niche. These two historic wet materials remain FAIL pending exact written product-use approval; proposed flat/Soho alternative not assumed approved in this source scheme.',
'- Wet bath level floor: ELM Cortar Clay Soft / Bone Soft / mixed Anti-Slip per room has no published exact measured ANSI wet DCOF >=0.42 for selected finish and format. FAIL pending maker dated exact report. Large-format 24x48 cannot be presumed to slope to selected linear drain.':
'- Tiled level bath floor: source Cortar Bone 12x24 Soft wet DCOF >=0.42 measured numeric point is absent and strict project gate FAIL. Existing source is a Duravit tub, with no new tiled shower pan or selected linear drain. Historical floor extension $299.02/unit controls, not a separately quoted alternative.',
'- Tub vs shower: no extra shower pan is counted in the tub rooms. TX Primary chosen linear drain position/slope and 48-in wall side are not surveyed; manufacturer/product floor compatibility is not established.':
'- Tub/membrane detail: retain selected Duravit 700332000000090 and Hansgrohe Matte White fixtures, verify tub flange and transition; actual niche opening and positive-draining sill netted against wall field, Bone Ribbed relief area split unmeasured and not added as extra.',
'- Owner: TX Bath2 basin owner-unselected; all alternatives need sample signoff. No primary niche; TX Bath4 existing tub remains unchanged. No steam discussion.':
'- Owner authority: retain TX Bath4 tub, Hansgrohe Matte White and historical tile scope only as reference; actual sample choice, current Chicago lot/price, niche geometry and written owner approval are null.',
'Preserve coherent matte white/Black Onyx fixture relationship and avoid speculative high-cost accent layering.':
'Preserve this room’s actual Hansgrohe Matte White faucet/shower fixture relationship with Charcoal and Bone; do not infer other bath metal finishes.'
}
}
changed=0
for rid,m in repls.items():
 letters={'TX-PRIMARY':'C','TX-BATH2':'A','TX-BATH4':'B'}
 p=R/'rooms'/rid/'board/round-009/candidates'/(letters[rid]+'.md')
 content=p.read_text(encoding='utf-8')
 for a,b in m.items():
  assert content.count(a)==1,(rid,'expected one substitution',a[:80],content.count(a))
  content=content.replace(a,b)
  changed+=1
 p.write_text(content,encoding='utf-8')
chall=R/'rooms/TX-BATH2/board/round-009/candidates/C.md'
content=chall.read_text(encoding='utf-8')
a='Existing **R02 independent critics** identified exact floor wet-DCOF test, unselected sink, niche field netting, 24-in floor cuts, full landed quote and Chicago inventory as next fixes; all remain disclosed.'
b='Technical release requires exact floor wet-DCOF evidence, owner sink selection, measured niche field netting, 24-in floor cut layout, a complete landed quote and verified Chicago inventory; none is currently supplied.'
assert content.count(a)==1
chall.write_text(content.replace(a,b),encoding='utf-8')
for rid,files in receipt['candidate_files'].items():
 for letter in files:
  p=R/'rooms'/rid/'board/round-009/candidates'/(letter+'.md')
  data=p.read_bytes()
  receipt['candidate_files'][rid][letter]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
receipt['pre_dispatch_reviewer_blind_scope_fix']='Reviewer R009 preliminary FIX: removed R02 critic mention, all prohibited steam words, irrelevant cross-room boilerplate, tub/linear-drain false claims; six SHA/bytes refreshed before critic dispatch'
receiptpath.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print('PASS',changed,'baseline corrections and one challenger blind reference correction; all six SHA refreshed; scores null')

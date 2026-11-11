from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
rs=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
o=R/'deliverables/integrated-r10'
questions={
'PH-PRIMARY':'Approve flat Bone and floor/pan sample only after exact wet tests? NO NICHE.',
'PH-BATH2':'Retain maker Wet Areas-PASS Sapphire tub walls and Matte White? No tiled pan.',
'PH-BATH3':'Select sink and confirm tub versus Delta point-drain compatibility.',
'PH-BATH4':'Resolve 35-versus-27 SF, Soft-versus-Anti-Slip and wet Ribbed/Caviar replacement.',
'PH-POWDER':'Approve dry Earth Lines and mirror/trim/color sample.',
'PH-WC':'Approve inherited PH Primary level floor only after wet-floor test.',
'TX-PRIMARY':'Approve wet flat Clay and linear drain after raw wet tests; NO NICHE.',
'TX-BATH2':'Select basin; maintain actual tub and Chrome fitting palette.',
'TX-BATH3':'Choose tub versus walk-in shower before any pan layout.',
'TX-BATH4':'Approve flat Charcoal/Soho wet surfaces with original tub.',
'TX-POWDER':'Approve 70:30 Haze color samples and separate cartons.',
'TX-POWDER2':'Select basin and dry mirror/backing panel for retained Indigo.',
'TX-WC':'Approve inherited TX Primary level floor only after wet-floor test.'}
assert len(rs)==len(questions)==13
p=['# 1529 Wieland | Round010 compact owner decision cards','',
'These are explicit decision REQUESTS, not approvals, procurement orders or construction drawings. Original material values are dated September 3, 2026, per one room copy, 15% source waste already embedded. Live model 1527 N Wieland is NOT verified as this 1529 site. The 14 market listings cover nine buildings, Old Town first, PH $2.8M and TX $2.7M; LP/GC secondary.','',
'Every room: current Chicago exact lot/price/lead, approved room cap, exact order cartons, surveyed edge LF and signed owner selection are NULL. Glazzio maker wet >0.50 is a reported bound, Daltile Prime Target is not exact raw lab DCOF. No floor/pan or owner clearance.','']
for r in rs:
 rid=r['id'];title=rid+' — '+r['status']+' | current champion '+str(r['champion_id'])+' / '+str(r['champion_score'])
 p+=['','## '+title,'',
 '**Owner question:** '+questions[rid],
 '**GOOD / carried original:** retain v4 original tile quote and any valid prior board choice, without interpreting a blocked room as accepted.',
 '**BETTER / conditional study:** refer to the room-by-room R10 coordination book, exact maker SKU research and current pending blind PH options where relevant.',
 '**BEST / release-ready only after evidence:** correct 1529 dimensions, exact maker wet/floor certificates where required, actual fixture/tub/point/linear detail and membrane, measured net surface/trim/cartons, current Chicago pricing and signed owner approval.',
 '**Historic ELM material per one unit:** USD '+format(r['carried_quote_material_subtotal_usd_per_unit'],'.2f')+'. Original Smartsheet source SF including waste: '+', '.join(str(z['smartsheet_row_id'])+' '+z['surface']+' '+format(z['qty_sf_per_unit'],'.2f')+' SF'+(' NONORDERABLE PRIMARY NICHE' if rid.endswith('PRIMARY') and z['surface']=='accent' else '') for z in r['carried_tile_rows'])+'.',
 '**Mockup/sample and drawing action (not generated or ordered):** tile sample beside the actual selected fitting, grout/edge comparison, W1–W3 cut overlay with unverified dimensions dashed, floor or tub flange/drain/threshold cross-section where applicable; do not invent unchosen basin or extra niche.',
 '**Recorded owner response:** null; sample date null; approved lot/color null; current supplier bid null; signed procurement release false.']
if rid in ('PH-POWDER','TX-POWDER','TX-POWDER2'):p.append('**Wet DCOF:** N/A dry vanity tile on original wood floor; no tiled shower/pan.')
if rid in ('PH-WC','TX-WC'):p.append('**Wet DCOF:** inherited Primary level-floor HOLD; WC independent SF/order ZERO.')
if rid in ('PH-PRIMARY','TX-PRIMARY'):p.append('**Scope:** NO PRIMARY NICHE; one blended source floor includes shared WC and pan, no duplicate purchase.')
if rid=='PH-BATH4':p.append('**Source:** actual walk-in Brizo BT062415-BNX square point drain; do NOT describe a Duravit tub.')
if rid=='PH-BATH2':p.append('**Source:** actual Duravit tub and Hansgrohe Matte White; Tones Sapphire 2x20 Glossy Wet Areas PASS. No tiled shower pan.')
(o/'R10_13_OWNER_DECISIONS_AND_SAMPLE_PRESENTATION_CARDS.md').write_text('\n'.join(p)+'\n',encoding='utf-8')
print('PASS owner card set',len(rs),'rooms, actual source row IDs and decisions, owner approval null')

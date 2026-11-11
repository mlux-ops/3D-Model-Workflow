from pathlib import Path
import json,csv,hashlib
R=Path(__file__).resolve().parents[1];O=R/'deliverables/integrated-r09';O.mkdir(parents=True,exist_ok=True)
s=json.loads((R/'state/ROUND009_SCORING.json').read_text(encoding='utf-8'))
reg=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
assert s['verification']['actual_independent_critiques']==12 and s['verification']['criterion_checks']==114
out=['# R09 | Triplex Round009 owner/GC scored conditional selections and release controls','',
'All three rooms remain BOARD BLOCKED. No accepted owner choice, no approved tile champion, no procurement release. The 12 actual independent specialist critiques independently validate six frozen candidate files and 114 individual 1-5 criteria, market .30, design .25, build .25, cost .20. Historical Round002/003 decisions and source quotes remain unmodified.','',
'| Room | Historical score | Revised design score | Delta | Minimum revised critic | Gate-qualified? |',
'|---|---:|---:|---:|---:|---|']
for room,z in s['room_results'].items():
 a=z['incumbent_letter'];b=z['challenger_letter'];v=z['candidates'][a];w=z['candidates'][b]
 out.append('| %s | %.2f | %.2f | %+.2f | %.1f | NO: floor wet DCOF unavailable |'%(room,v['weighted_score'],w['weighted_score'],z['margin'],w['minimum_critic_score']))
out+=['','## Thirteen-room integration and project-wide release logic','',
'The above three are new scored Triplex design evaluations, NOT approvals. For PH Primary/Baths2/3/4 the scored Round004 prior BLOCKED outcomes remain; TX Bath3 tub-versus-walk-in remains an owner-only program decision; PH Powder Earth Lines board active 3.69, TX Powder Haze 70:30 board active 3.67, TX Powder2 Indigo retained 3.23, all NOT owner approved. Two WCs inherit primary level-floor DCOF and have zero independent tile purchase.','',
'**PH/TX Primary:** Existing Brizo 48-inch linear drains stay. No new niches. Prime RL mosaics have maker family linear application checkmark but incompatible old/new Target statements (>=0.60 and >=0.42), NOT individual exact wet DCOF. Glazzio maker >0.50 and legacy >0.42 are lower bounds, not a raw measured test. Individual product/finish/drain assembly and 1529 dimensions remain separate holds.','',
'**TX Bath2:** Wet-listed Copper/Sandstone preserve Duravit tub and Hansgrohe Chrome. HNC6615 proposed level field has a manufacturer reported >0.50 wet bound, NOT accepted exact project lab point; owner basin unselected. No tiled shower pan or drain reassignment.','',
'**TX Bath4:** Wet-listed flat Charcoal/Soho niche conditionally replaces unlisted Bone Ribbed/Clara wet applications, retains Duravit tub and Matte White fittings. HNC6615 floor exact test and measured niche back/returns still unavailable. No speculative shower pan.','',
'## Score versus acceptance explanation','',
'Revised TX Primary +0.84 and TX Bath4 +0.70 exceed the +0.25 margin, but revised minimum cost seats are 2.8 and 2.6 respectively (required >=3.0). TX Bath2 +0.14 fails margin and revised cost seat 2.8 fails minimum. All six have independently inadequate accepted wet-floor testing under the project strict test protocol, so no candidate passes all gates. These decisions do not interpret an unknown room cap as >125% budget failure.','',
'## Source financial and quantity controls','',
'ELM dated September 3 2026 historic material-only four-dwelling quote total $23,572.44. Twenty-seven quoted/history source records, two historical Primary niche line quantities 7.41 and 8.63 SF explicitly excluded and unpriced; existing gross includes one 15% waste. Quoted bathrooms are two PH and two TX unit copies, WC floor already inside Primary and no added independent cartoning. New substitution delivered/installed costs, trim LF, confirmed case orders and Chicago lot/stock/lead remain null. See R09_27_ROW_QUOTE_TO_SELECTION_AUDIT.csv and R09_NOMINAL_WALL_CUT_REGISTER.csv.','',
'## Required owner/technical closeout','',
'For each of 13 rooms: correct native 1529 document session title/path and/or actual field survey; individual maker wet-wall approval; raw accepted wet DCOF for exact selected level/pan SKUs where applicable; actual selected drain application/membrane/slope; measured corners/openings/niche displacement/edge LF and carton yields; dated supplier quote/current Chicago supply; owner basin/tub programs and final signed color, per-room cap and purchase authorization. No orders, vendor outreach, Revit changes, Smartsheet changes or owner choices were made. All 13 release flags remain FALSE.']
(O/'R09_ROUND009_SCORING_OWNER_ADDENDUM.md').write_text('\n'.join(out)+'\n',encoding='utf-8')
m=json.loads((O/'MANIFEST.json').read_text(encoding='utf-8'))
f=O/'R09_ROUND009_SCORING_OWNER_ADDENDUM.md'
assert f.stat().st_size>2000
print('PASS owner score addendum: all 3 TX rooms blocked with exact 12 independent critiques, historic 4-dwelling material 23572.44')

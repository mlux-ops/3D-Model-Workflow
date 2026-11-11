"""Persist subsequent-turn scored R011 outcome, without editing blind packets."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
s=json.loads((R/'state/ROUND011_SCORING.json').read_text(encoding='utf-8'))
path=R/'state/ROOMS.json';data=json.loads(path.read_text(encoding='utf-8'))
assert len(data['rooms'])==13 and s['verification']['all_valid'] and s['verification']['criterion_checks']==76
notes={
 'PH-BATH3':(
  'Conditional visual study only: individually Wet Areas-listed Tones Sandstone 2x20 glossy wet field/niche, Glazzio HNC6615 level study, HNC6715 hex POINT pan only after owner walk-in election; Hansgrohe/Delta Chrome retained, sink UNSELECTED',
  'Owner tub versus walk-in and PH basin; reconcile Delta DT062412 square drain versus tub-alcove drawing; exact HNC6615/HNC6715 SKU raw wet DCOF certificates, maker-approved drain/membrane assembly, proper 1529 W1-W3 and level/pan geometry, niche deduction, current price/lot'),
 'TX-BATH3':(
  'Conditional visual study only: wet-listed Tones Emerald vertical 2x20 with existing Sandstone niche, Glazzio HNC6615 level and conditional HNC6715 square-point pan; selected Brizo Black Onyx BT062415-BNX retained; vertical 1.60-in nominal returns are mockup HOLD',
  'Owner tub versus walk-in and Brizo square point-drain conflict with tub-alcove source; exact floor/pan numeric wet DCOF, 1529 measured vertical 2x20 cuts, point-pan waterproof/slope/threshold, original niche field deduction, current Chicago quote/lot/ETA and written material cap')
}
for rid,rr in s['room_results'].items():
 item=next(v for v in data['rooms'] if v['id']==rid)
 assert item['status']=='blocked' and item['owner_status'] is None and item['champion_id'] is None
 assert item['round_011_submission']['scores'] is None
 assert 'board_round_011' not in item
 assert rr['status']=='blocked' and not rr['accepted_challenger']
 a=rr['incumbent_letter'];b=rr['challenger_letter'];old=rr['candidates'][a];new=rr['candidates'][b]
 item['round_011_submission'].update(status='review_complete_scored',scores={k:v['weighted_score'] for k,v in rr['candidates'].items()},critic_files_complete=8,owner_approved=False,release_allowed=False)
 item['board_round_011']=rr;item['last_round']=11
 item['round_011_conditional_design_direction']=notes[rid][0];item['round_011_evidence_priority']=notes[rid][1]
 item['open_gaps']=list(dict.fromkeys(item.get('open_gaps',[])+[notes[rid][1]]))
 d=R/'rooms'/rid;f=d/'board/round-011/ROUND_REPORT.md'
 assert not f.exists(),(rid,'prior room scored report')
 t=['# '+rid+' — Round011 scored four-seat blind board','',
 '**BLOCKED.** Neither historical nor revised candidate qualifies for board acceptance or owner/GC release. Four independently authentic blinded specialists per room were collected and SHA verified BEFORE prime opened the private historical/revised role mapping; original source and critic packets and submission remain frozen.','',
 '| Private source role | Letter | Market .30 | Design .25 | Build .25 | Cost .20 | Weighted | Minimum critic | Hard gates |',
 '|---|---|---:|---:|---:|---:|---:|---:|---:|---|']
 for label,k in [('Historical v4',a),('Revised conditional',b)]:
  z=rr['candidates'][k];x=z['seat_scores']
  t.append('| %s | %s | %.1f | %.1f | %.1f | %.1f | %.2f | %.1f | FAIL |'%(label,k,x['market'],x['design'],x['build'],x['cost'],z['weighted_score'],z['minimum_critic_score']))
 t+=['','Revised margin **%+.2f** versus required **+0.25**; revised minimum seat **%.1f** versus all-seat **>=3.0**. These are separate from mandatory manufacturer wall/floor/pan and owner/geometry conditions. Positive weighted preference is not compliance or owner approval.'%(rr['margin'],new['minimum_critic_score']),'']
 for k in (a,b):t.append('**Candidate '+k+' ('+rr['candidates'][k]['role']+'):** '+'; '.join(rr['candidates'][k]['gate_reasons']))
 t+=['','**Conditional design direction, not qualified selection:** '+notes[rid][0],
 '**Priority technical/owner closure:** '+notes[rid][1],
 'The historical 2026-09-03 ELM material-only source subtotal is **$%.2f per copy**, two copies, and all original gross SF already include 15%% waste once. Historical quoted totals are not current alternative quotes, room material budget caps or installed cost. Shared primary WC floors, niche face/returns, trims and any new tiled point-pan must never be duplicated. Exact owner-approved cap, installed bid, cartons, local lot and ETA = null; no invented 125%%-of-budget gate outcome.'%item['carried_quote_material_subtotal_usd_per_unit'],
 'Relevant market evidence: 14 listings / nine distinct buildings, 405 W Armitage OT01–OT04 one design precedent, Old Town primary, Lincoln Park/Gold Coast secondary, PH $2.8M/TX $2.7M; no authenticated listing bathroom tile images.',
 'Formal records: state/ROUND011_SCORING.json; original immutable state/ROUND011_SUBMISSION.json (all_critic_scores:null), ROUND011_CRITIC_DISPATCH.json and ROUND011_CRITIC_COLLECTION.json; all four original critic-market/design/build/cost.md files. Neither owner approval nor procurement authorization occurred.']
 f.write_text('\n'.join(t)+'\n',encoding='utf-8')
 cp=d/'champion.md';text=cp.read_text(encoding='utf-8')
 header=text.splitlines()[0]
 text=text.replace(header,'# '+rid+' — Round011 BLOCKED (historic v4 preserved as audit only)',1)
 lines=text.splitlines()
 update='**Current status:** Round011 **BLOCKED**. Historic %s %.2f; revised %s %.2f; delta %+.2f; revised minimum critic %.1f. No gate-qualified champion, owner approval or order. Historic material schedule below retained for audit, NOT a newly approved design.'%(a,old['weighted_score'],b,new['weighted_score'],rr['margin'],new['minimum_critic_score'])
 ix=next((j for j,v in enumerate(lines[:9]) if v.startswith('**Status:**') or v.startswith('**Current status:**')),None)
 if ix is None:lines.insert(1,update)
 else:lines[ix]=update
 text='\n'.join(lines)+'\n'
 assert '## Round011 governing scored board' not in text
 text+='\n## Round011 governing scored board\n\n**BLOCKED**. '+notes[rid][0]+'. Release holds: '+notes[rid][1]+'. See board/round-011/ROUND_REPORT.md.\n'
 cp.write_text(text,encoding='utf-8')
 hp=d/'history.md';hist=hp.read_text(encoding='utf-8')
 assert 'Round011 scored after' not in hist
 hist+='\n- 2026-11-06 Round011 scored after separate submission/reviewer CONTINUE: historic %s %.2f, revised %s %.2f, margin %+.2f, revised minimum %.1f. Both hard-gate BLOCKED; no qualified design/owner approval/order; original frozen SHA, private mapping, prior scored rounds and v4 source preserved. See board/round-011/ROUND_REPORT.md.\n'%(a,old['weighted_score'],b,new['weighted_score'],rr['margin'],new['minimum_critic_score'])
 hp.write_text(hist,encoding='utf-8')
 print(rid,'historic',old['weighted_score'],'revised',new['weighted_score'],'BLOCKED')
path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS two R011 reports/champions/histories and 13-room state updated; eight critics and four candidates untouched')

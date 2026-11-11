"""Apply score results only; preserve prior rounds and original frozen evidence."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
scoring=json.loads((R/'state/ROUND012_SCORING.json').read_text(encoding='utf-8'))
assert scoring['verification']['valid'] and scoring['verification']['original_critics']==12
path=R/'state/ROOMS.json'
data=json.loads(path.read_text(encoding='utf-8'))
assert len(data['rooms'])==13
for rid,rr in scoring['room_results'].items():
 room=next(v for v in data['rooms'] if v['id']==rid)
 assert room['status']=='blocked' and room['owner_status'] is None and room['champion_id'] is None
 assert room['round_012_submission']['scores'] is None and 'board_round_012' not in room
 assert rr['status']=='blocked' and rr['champion_id'] is None
 old=rr['historical_letter'];new=rr['revised_letter']
 a=rr['candidates'][old];b=rr['candidates'][new]
 room['round_012_submission'].update(status='review_complete_scored',scores={k:v['weighted_score'] for k,v in rr['candidates'].items()},
                                     critic_files_complete=4,owner_approved=False,release_allowed=False)
 room['board_round_012']=rr
 room['last_round']=12
 detailed='; '.join(b['gate_reasons'])
 room['round_012_conditional_design_direction']='Letter '+new+' has weighted '+str(b['weighted_score'])+' but is NOT gate-qualified; owner sample only.'
 room['round_012_evidence_priority']=detailed
 room['open_gaps']=list(dict.fromkeys(room.get('open_gaps',[])+[detailed]))
 roomdir=R/'rooms'/rid
 report=roomdir/'board/round-012/ROUND_REPORT.md'
 assert not report.exists()
 lines=['# '+rid+' — Round012 independently scored four-seat blind board','',
        '**BLOCKED. Neither historical nor revised design is a gate-qualified champion, owner-approved selection, or purchasable construction specification.** Original neutral source SHA, 12 authentic four-seat reports and the original all-null submission/dispatch/collection remain immutable. Prime opened the private mapping after all authentic critiques were collected and the standing non-Pro Reviewer authorized scoring in this separate turn.','',
        '| Identity | Neutral letter | Market 0.30 | Design 0.25 | Build 0.25 | Cost 0.20 | Weighted | Minimum individual | Hard gates |',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|']
 for title,letter in (('Historical source',old),('Revised conditional',new)):
  q=rr['candidates'][letter];scores=q['individual_critic_scores']
  lines.append('| %s | %s | %.1f | %.1f | %.1f | %.1f | %.2f | %.1f | FAIL |'%(title,letter,scores['market'],scores['design'],scores['build'],scores['cost'],q['weighted_score'],q['minimum_critic_score']))
 lines+=['','**Revised-versus-source improvement:** %+.2f, required >= +0.25: **%s**. Revised minimum individual specialist %.1f, required >=3.0: **%s**. All applicable wet/floor/pan gates: **FAIL**.'%(rr['challenger_margin'],'PASS' if rr['challenger_margin_at_least_025'] else 'FAIL',b['minimum_critic_score'],'PASS' if b['all_critics_at_least_3'] else 'FAIL'),'']
 for letter in (old,new):
  q=rr['candidates'][letter]
  lines+=['### Candidate '+letter+' — '+q['role'],'','; '.join(q['gate_reasons']),'']
 lines+=['**Technical visual study only (not an accepted selection):** Candidate '+new+' can inform owner sample/mockup work only after its evidence gap and cited cost critic weaknesses are resolved.',
         '**Historical source:** Original dated 2026-09-03 ELM material-only $%.2f per copy; two unit copies; all source SF include one 15%% waste factor. No duplicate shared WC, niche face/returns, added pan or independent trim order.'%room['carried_quote_material_subtotal_usd_per_unit'],
         '**Current procurement:** alternate exact current installed/landed price, carton quantity, Chicago lot/ETA, room owner cost cap, site-measured true dimensions and written owner approval all null. Unknown room material budget -> do not invent a >125% cap determination.',
         '**Market:** 14 Old Town/adjacent comparable listings represent nine buildings; 405 W Armitage OT01–OT04 is one independent precedent. $2.8M PH/$2.7M TX; $2.4M–$3.2M comparison band; no authenticated listing bathroom-tile photos.',
         '**Records:** state/ROUND012_SCORING.json (distinct scoring); original state/ROUND012_SUBMISSION.json, ROUND012_CRITIC_DISPATCH.json and ROUND012_CRITIC_COLLECTION.json retain all_critic_scores:null, source SHA; critic-market/design/build/cost.md remain unchanged. No real owner or GC procurement release.']
 report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 cp=roomdir/'champion.md'
 body=cp.read_text(encoding='utf-8');sections=body.splitlines()
 assert '## Round012 governing scored board' not in body
 sections[0]='# '+rid+' — Round012 BLOCKED (historic v4 remains source record only)'
 headline=('**Current status:** Round012 **BLOCKED**. Historical %s %.2f; revised %s %.2f; margin %+.2f; minimum revised specialist %.1f. No gate-qualified champion, owner selection or purchase authorization. Historic v4 material table below retained for audit, not approved.'%
           (old,a['weighted_score'],new,b['weighted_score'],rr['challenger_margin'],b['minimum_critic_score']))
 ix=next((i for i,x in enumerate(sections[:9]) if x.startswith(('**Current status:**','**Status:**'))),None)
 if ix is None:sections.insert(1,headline)
 else:sections[ix]=headline
 cp.write_text('\n'.join(sections)+'\n\n## Round012 governing scored board\n\n**BLOCKED.** '+detailed+'\n\nSee board/round-012/ROUND_REPORT.md.\n',encoding='utf-8')
 hp=roomdir/'history.md';history=hp.read_text(encoding='utf-8')
 assert 'Round012 scored in distinct continuation' not in history
 history+='\n- 2026-11-06 Round012 scored in distinct continuation after worker-11 non-Pro CONTINUE: historic %s %.2f, revised %s %.2f, margin %+.2f, revised minimum specialist %.1f; source and revised BOTH hard-gate BLOCKED, no valid champion/owner acceptance/order. Twelve original blind critic/source fingerprints unchanged, original submission scores remain null. See board/round-012/ROUND_REPORT.md.\n'%(old,a['weighted_score'],new,b['weighted_score'],rr['challenger_margin'],b['minimum_critic_score'])
 hp.write_text(history,encoding='utf-8')
 print(rid,'historic',a['weighted_score'],'revised',b['weighted_score'],'BLOCKED')
path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS R012 3 room scored reports, champions, histories and ROOMS 13 register updated; original candidate/critique fingerprints untouched')

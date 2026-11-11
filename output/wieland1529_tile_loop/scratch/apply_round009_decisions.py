from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
s=json.loads((R/'state/ROUND009_SCORING.json').read_text(encoding='utf-8'))
p=R/'state/ROOMS.json';data=json.loads(p.read_text(encoding='utf-8'))
assert len(data['rooms'])==13 and s['verification']['all_valid']
notes={
'TX-PRIMARY':('Wet-listed flat Clay with original Brizo 48-in linear, NO NICHE; HNC6615 level/WC and Prime RL21 mosaic pan are only unqualified research alternatives','Exact wet DCOF for level and pan, RL21 item code, linear membrane/drain slope, surveyed 1529 geometry and current supplier quote'),
'TX-BATH2':('Wet-listed Copper/Sandstone tub walls, actual Chrome Hansgrohe and Duravit tub; HNC6615 level floor remains conditional','Exact wet-floor test, owner basin selection, measured niche face/returns and delivered quote; no tiled shower pan'),
'TX-BATH4':('Wet-listed flat Charcoal with Soho Black niche and Matte White Hansgrohe/Duravit tub; HNC6615 level floor conditional','Exact wet-floor test, niche netting and return geometry, replacement of unlisted Ribbed/Clara, current supplier quote')}
for rid,rr in s['room_results'].items():
 item=next(x for x in data['rooms'] if x['id']==rid)
 assert item['status']=='blocked' and item['owner_status'] is None and item['champion_id'] is None
 assert item['round_009_submission']['scores'] is None
 a=rr['incumbent_letter'];b=rr['challenger_letter'];old=rr['candidates'][a];new=rr['candidates'][b]
 assert not rr['accepted_challenger'] and not old['hard_gates_pass'] and not new['hard_gates_pass']
 item['round_009_submission'].update(status='review_complete_scored',scores={k:v['weighted_score'] for k,v in rr['candidates'].items()},owner_approved=False,release_allowed=False,critic_files_complete=12)
 item['board_round_009']=rr;item['last_round']=9
 item['round_009_conditional_design_direction']=notes[rid][0]
 item['round_009_evidence_priority']=notes[rid][1]
 item['open_gaps']=list(dict.fromkeys(item.get('open_gaps',[])+[notes[rid][1]]))
 d=R/'rooms'/rid;f=d/'board/round-009/ROUND_REPORT.md'
 t=['# '+rid+' — Round009 scored four-seat blind board','',
 '**BLOCKED**: neither candidate has a gate-qualified floor SKU; no accepted champion, owner approval or order release. Four independent critic reports for each packet, private roles opened only after all 12 complete. Candidate SHA unchanged.','',
 '| Private role | Letter | Market .30 | Design .25 | Build .25 | Cost .20 | Weighted | Minimum | Hard gate |',
 '|---|---|---:|---:|---:|---:|---:|---:|---|']
 for role,k in [('Historic v4',a),('Revised conditional',b)]:
  z=rr['candidates'][k];x=z['seat_scores']
  t.append('| %s | %s | %.1f | %.1f | %.1f | %.1f | %.2f | %.1f | FAIL |'%(role,k,x['market'],x['design'],x['build'],x['cost'],z['weighted_score'],z['minimum_critic_score']))
 t+=['','Margin %+0.2f versus +0.25; revised minimum %.1f versus required >=3.0. Both candidates fail exact manufacturer SKU wet-floor DCOF, and TX Primary linear pan separately fails exact wet test; numeric gains alone never promote a champion.'%(rr['margin'],new['minimum_critic_score']),'']
 for k in [a,b]:
  t.append('Candidate '+k+' '+rr['candidates'][k]['role']+': '+'; '.join(rr['candidates'][k]['gate_reasons']))
 t+=['','Conditional visual direction, NOT owner selection: '+notes[rid][0], 'Next technical/owner evidence: '+notes[rid][1],
 'Historical ELM material-only tile quote $%.2f per unit x2 copies, original 15%% waste included, no WC duplicate, no new Primary niche. Proposed rate, installed price, exact lot, Chicago stock/ETA, owner room cap, trim and carton quantities null. Live Revit 1527 is not confirmed 1529, so cuts and drain slopes remain drawing-provisional. Independent comp basis 14 listings/9 buildings, Old Town prioritized.'%item['carried_quote_material_subtotal_usd_per_unit'],
 'Authoritative source file: state/ROUND009_SCORING.json, source receipt state/ROUND009_SUBMISSION.json, and each critic-market/design/build/cost.md.']
 f.write_text('\n'.join(t)+'\n',encoding='utf-8')
 cp=d/'champion.md';h=cp.read_text(encoding='utf-8');head=h.splitlines()[0]
 h=h.replace(head,'# '+rid+' — Round009 BLOCKED (historical v4 retained)',1)
 arr=h.splitlines();ix=next((i for i,v in enumerate(arr[:8]) if v.startswith('**Status:**') or v.startswith('**Current status:**')),None)
 if ix is not None:arr[ix]=f"**Current status:** Round009 **BLOCKED**. Historical {a} {old['weighted_score']:.2f}; revised {b} {new['weighted_score']:.2f}; delta {rr['margin']:+.2f}. No gate-qualified champion, owner approval or order. Historical v4 specification below remains a source record, not an accepted selection."
 h='\n'.join(arr)+'\n'
 if '## Round009 governing scored board' not in h:h+='\n## Round009 governing scored board\n\n**BLOCKED**. '+notes[rid][0]+'. Release holds: '+notes[rid][1]+'. See board/round-009/ROUND_REPORT.md.\n'
 cp.write_text(h,encoding='utf-8')
 hp=d/'history.md';hist=hp.read_text(encoding='utf-8')
 if 'Round009 scored' not in hist:hist+=f"\n- 2026-11-06 Round009 scored: historic {a} {old['weighted_score']:.2f}, revised {b} {new['weighted_score']:.2f}, margin {rr['margin']:+.2f}, minimum revised {new['minimum_critic_score']:.1f}. Both hard-gate BLOCKED; no owner approval or tile release. See board/round-009/ROUND_REPORT.md.\n"
 hp.write_text(hist,encoding='utf-8')
 print(rid,'historic',old['weighted_score'],'revised',new['weighted_score'],'BLOCKED')
p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS 3 reports, 3 champions, 3 histories, 13-room register updated')

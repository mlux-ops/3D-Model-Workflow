from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
s=json.loads((R/'state/ROUND010_SCORING.json').read_text(encoding='utf-8'))
p=R/'state/ROOMS.json';data=json.loads(p.read_text(encoding='utf-8'))
assert len(data['rooms'])==13 and s['verification']['all_valid'] and s['verification']['criterion_checks']==114
notes={
'PH-PRIMARY':('Source-backed visual direction only: flat ELM Cortar Bone wet wall/ceiling, HNC6615 level/WC study, Daltile Prime RL21 1.5-in hex linear pan; actual Brizo Black Onyx 48-in linear, NO NICHE','Independent exact numerical wet DCOF lab certificates for both HNC level and Prime RL21 pan; manufacturer linear drain/membrane/slope/overhead 24x48 system; true 1529 project geometry and price/cap'),
'PH-BATH2':('Preserve maker Wet Areas-PASS ELM Tones Sapphire 2x20 Glossy with Duravit 59-in tub and Matte White Hansgrohe; study HNC6615 level floor; NO tiled shower pan','Exact product-specific HNC6615/other level-floor numeric wet DCOF raw test, actual tub flange and niche net return, joint/grout/threshold, verified local quote and owner sample sign-off'),
'PH-BATH4':('Only source-backed revised design study: wet-listed flat Cortar Bone/Soho Black niche, HNC6615 LEVEL and HNC6715 2x2 HEX square-point pan, Brizo BT062415-BNX actual WALK-IN shower, NOT TUB','Exact 1529 walk-in point-drain footprint and four-plane slope, independent level and pan raw wet DCOF tests, original owner 35 versus former 27 SF and Soft-versus-Anti-Slip supplier finish/omitted Ribbed supplier-total reconciliation, current lot and owner signoff')}
for rid,rr in s['room_results'].items():
 item=next(x for x in data['rooms'] if x['id']==rid)
 assert item['status']=='blocked' and item['owner_status'] is None and item['champion_id'] is None
 assert item['round_010_submission']['scores'] is None
 a=rr['incumbent_letter'];b=rr['challenger_letter'];old=rr['candidates'][a];new=rr['candidates'][b]
 assert not rr['accepted_challenger'] and not old['hard_gates_pass'] and not new['hard_gates_pass']
 item['round_010_submission'].update(status='review_complete_scored',scores={k:v['weighted_score'] for k,v in rr['candidates'].items()},owner_approved=False,release_allowed=False,critic_files_complete=12)
 item['board_round_010']=rr;item['last_round']=10
 item['round_010_conditional_design_direction']=notes[rid][0]
 item['round_010_evidence_priority']=notes[rid][1]
 item['open_gaps']=list(dict.fromkeys(item.get('open_gaps',[])+[notes[rid][1]]))
 d=R/'rooms'/rid;f=d/'board/round-010/ROUND_REPORT.md'
 t=['# '+rid+' — Round010 scored four-seat blind board','',
 '**BLOCKED:** neither candidate has a qualified exact numeric measured floor (and where applicable shower-pan) wet DCOF. No accepted champion, owner authorization or material purchasing release. All four independent critiques were completed and SHA checked for BOTH letters before the prime privately opened room role keys. Original neutral candidate packets and submission receipt remain frozen.','',
 '| Private role | Letter | Market .30 | Design .25 | Build .25 | Cost .20 | Weighted | Minimum | Wet gate |',
 '|---|---|---:|---:|---:|---:|---:|---:|---:|---|']
 for role,k in [('Historic v4 source',a),('Revised conditional',b)]:
  z=rr['candidates'][k];x=z['seat_scores']
  t.append('| %s | %s | %.1f | %.1f | %.1f | %.1f | %.2f | %.1f | FAIL |'%(role,k,x['market'],x['design'],x['build'],x['cost'],z['weighted_score'],z['minimum_critic_score']))
 t+=['','Revised weighted margin %+0.2f against required +0.25; revised minimum seat %.1f against required >=3.0. Even a positive score margin does NOT remove DCOF gate failure and cannot establish owner acceptance or purchase authorization.'%(rr['margin'],new['minimum_critic_score']),'']
 for k in [a,b]:t.append('Candidate '+k+' ('+rr['candidates'][k]['role']+'): '+'; '.join(rr['candidates'][k]['gate_reasons']))
 t+=['','Conditional material and fixture direction, NOT owner selection: '+notes[rid][0],
 'Independent next technical/owner evidence: '+notes[rid][1],
 'Historical ELM 2026-09-03 material-only tile quote $%.2f/unit x2 copies, original 15%% gross source waste already included; primary WCs share Primary floor; historic unpriced Primary niche excluded. Exact new material/installed offer, current Chicago lot, signed owner room cap, real 1529 field geometry, trim LF/cartons and accepted test report all null. No 125%% gate conclusion without actual room cap. Verified market set 14 listings/9 building groups, Old Town first, LP/GC secondary; 405 W Armitage four sales one precedent.'%item['carried_quote_material_subtotal_usd_per_unit'],
 'Formal evidence: state/ROUND010_SCORING.json; separately immutable state/ROUND010_SUBMISSION.json (original all_critic_scores:null); state/ROUND010_CRITIC_COLLECTION.json with all 12 SHA; each critic-market/design/build/cost.md.']
 f.write_text('\n'.join(t)+'\n',encoding='utf-8')
 cp=d/'champion.md';h=cp.read_text(encoding='utf-8');head=h.splitlines()[0]
 h=h.replace(head,'# '+rid+' — Round010 BLOCKED (historical v4 source retained for audit)',1)
 arr=h.splitlines();ix=next((i for i,v in enumerate(arr[:9]) if v.startswith('**Status:**') or v.startswith('**Current status:**')),None)
 line=f"**Current status:** Round010 **BLOCKED**. Historical {a} {old['weighted_score']:.2f}; revised {b} {new['weighted_score']:.2f}; delta {rr['margin']:+.2f}; new minimum critic {new['minimum_critic_score']:.1f}. No gate-qualified champion, owner approval or order. Prior v4 material source below is historical, not a new accepted specification."
 if ix is not None:arr[ix]=line
 else:arr.insert(1,line)
 h='\n'.join(arr)+'\n'
 if '## Round010 governing scored board' not in h:h+='\n## Round010 governing scored board\n\n**BLOCKED**. '+notes[rid][0]+'. Release holds: '+notes[rid][1]+'. See board/round-010/ROUND_REPORT.md.\n'
 cp.write_text(h,encoding='utf-8')
 hp=d/'history.md';hist=hp.read_text(encoding='utf-8')
 if 'Round010 scored' not in hist:hist+=f"\n- 2026-11-06 Round010 scored after separate submission turn: historic {a} {old['weighted_score']:.2f}, revised {b} {new['weighted_score']:.2f}, margin {rr['margin']:+.2f}, minimum revised {new['minimum_critic_score']:.1f}. Both hard-gate BLOCKED, unapproved; source-v4 history, previous Round004 and separate R010 candidate SHA preserved. See board/round-010/ROUND_REPORT.md.\n"
 hp.write_text(hist,encoding='utf-8')
 print(rid,'historic',old['weighted_score'],'revised',new['weighted_score'],'BLOCKED')
p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS 3 Round010 room reports, champions, histories and current 13-room register updated without changing frozen candidate/critique packets')

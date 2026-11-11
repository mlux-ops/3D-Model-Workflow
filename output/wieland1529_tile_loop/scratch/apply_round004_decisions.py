from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
s=json.loads((R/'state/ROUND004_SCORING.json').read_text(encoding='utf-8'))
p=R/'state/ROOMS.json'; data=json.loads(p.read_text(encoding='utf-8'))
assert len(data['rooms'])==13 and len(s['room_results'])==4
directions={
'PH-PRIMARY':('Flat Bone wet walls; PF07 field/2x2 pan, existing 48-in linear drain; NO NICHE','Exact floor and mosaic wet-DCOF; verified drain/slope/1529 geometry and quotes'),
'PH-BATH2':('Historic Sapphire 2x20 Glossy wet wall is approved by maker; Copper is palette alternate only','Exact Grey Soft/PF05 floor wet-DCOF; niche netting and current price'),
'PH-BATH3':('Wet-listed Sandstone tub walls/niche, conditional PF07 level floor','Resolve tub versus Delta point drain; owner basin; floor DCOF'),
'PH-BATH4':('Wet-listed flat Bone and Soho niche; PF09 12x24/2x2 point-drain scheme','Resolve 35/27-SF and Soft/Anti-Slip; slope and exact floor/pan wet-DCOF')}
for room,x in s['room_results'].items():
  item=next(v for v in data['rooms'] if v['id']==room)
  assert item.get('owner_status') is None and item.get('last_round')==4
  old_scores=item.get('round_004_submission',{}).get('scores')
  expected_scores={k:v['weighted_score'] for k,v in x['candidates'].items()}
  assert old_scores is None or old_scores==expected_scores
  a=x['incumbent_letter']; b=x['challenger_letter']; old=x['candidates'][a]; new=x['candidates'][b]
  if old_scores is None:
    item['prior_champion_id']=item.get('champion_id')
  item['status']='blocked'; item['champion_id']=None; item['champion_score']=None
  item['round_004_submission'].update(status='review_complete_scored', scores={k:v['weighted_score'] for k,v in x['candidates'].items()}, owner_approved=False, exact_floor_wet_dcof_verified=False)
  item['board_round_004']=x
  item['provisional_preference_id']='round-004-'+b if x['margin']>0 else 'v4-'+room
  item['decision_blockers']=[directions[room][1], 'Correct 1529 native document identity before dimensions certified', 'Current Chicago stock, owner room cap, landed and installed quote unknown']
  d=R/'rooms'/room; q=d/'board/round-004/ROUND_REPORT.md'
  t=['# '+room+' | Round004 final scored board report (subsequent Round005 turn)','',
  'BLOCKED. Neither candidate passes floor DCOF hard gate. No owner approval or procurement clearance. Private historic/challenger identity opened only after all 16 independent reviews.','',
  '| Role | Letter | Market 0.30 | Design 0.25 | Build 0.25 | Cost 0.20 | Weighted | Min seat | Gate |',
  '|---|---|---:|---:|---:|---:|---:|---:|---|']
  for role,k in [('historic',a),('revised',b)]:
    v=x['candidates'][k];z=v['seat_scores']
    t.append('| %s | %s | %.1f | %.1f | %.1f | %.1f | %.2f | %.1f | FAIL |' % (role,k,z['market'],z['design'],z['build'],z['cost'],v['weighted_score'],v['minimum_critic_score']))
  t.extend(['','Revised margin %+0.2f (required >=+0.25), revised minimum %.1f (required >=3.0); BOTH gate-failed, so challenger NOT accepted.'%(x['margin'],new['minimum_critic_score']),''])
  for k in [a,b]: t.append('Candidate '+k+' '+x['candidates'][k]['role']+': '+'; '.join(x['candidates'][k]['gate_reasons']))
  t.extend(['','Conditional design direction, not accepted champion: '+directions[room][0], 'Next fix: '+directions[room][1],
  'Source ELM historical tile rates are not substitute quotes. Source 15% waste included. US availability and room budget not established; no automatic >125% gate. Native Revit 1527 identity does not certify 1529. Historical decisions remain in prior room files.',
  'Source: state/ROUND004_SCORING.json, four room critic files, frozen state/ROUND004_SUBMISSION.json.'])
  q.write_text('\n'.join(t)+'\n',encoding='utf-8')
  cp=d/'champion.md'; existing=cp.read_text(encoding='utf-8')
  if '## Round 004 governing board update' not in existing:
    existing+='\n\n## Round 004 governing board update\n\nBLOCKED: no gate-qualified champion. Historical %s %.2f, revised %s %.2f, delta %+0.2f; revised minimum critic %.1f. Revised not accepted. %s. %s. Historic v4 contents above retained for reference, not approval. See board/round-004/ROUND_REPORT.md.\n'%(a,old['weighted_score'],b,new['weighted_score'],x['margin'],new['minimum_critic_score'],directions[room][0],directions[room][1])
  cp.write_text(existing,encoding='utf-8')
  hp=d/'history.md';h=hp.read_text(encoding='utf-8')
  if 'Round004 scored in Round005' not in h:
    h+='\n- 2026-11-06 Round004 scored in Round005: historic %s %.2f, revised %s %.2f, delta %+0.2f, revised minimum %.1f. Neither eligible due exact wet floor DCOF; challenger not accepted; no owner approval. See board/round-004/ROUND_REPORT.md.\n'%(a,old['weighted_score'],b,new['weighted_score'],x['margin'],new['minimum_critic_score'])
  hp.write_text(h,encoding='utf-8')
  print(room, 'BLOCKED',old['weighted_score'],new['weighted_score'])
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: four room reports, champions, histories, 13-room register')

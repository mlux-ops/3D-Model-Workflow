from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
receipt=json.loads((R/'state/ROUND009_SUBMISSION.json').read_text(encoding='utf-8'))
assert receipt['all_critic_scores'] is None
p=R/'state/ROOMS.json';reg=json.loads(p.read_text(encoding='utf-8'))
for rid in ('TX-PRIMARY','TX-BATH2','TX-BATH4'):
 item=next(x for x in reg['rooms'] if x['id']==rid)
 assert item['status']=='blocked' and item['champion_id'] is None and item['champion_score'] is None and item['owner_status'] is None
 old=item.get('round_009_submission')
 assert old is None or old.get('status')=='blind_review_pending'
 item['last_round']=9
 item['round_009_submission']={'status':'blind_review_pending','scores':None,'candidate_count':2,'critics_required':['critic-market','critic-design','critic-build','critic-cost'],'owner_approved':False,'release_allowed':False,'frozen_source':'state/ROUND009_SUBMISSION.json','previous_round_decision':'preserved'}
 f=R/'rooms'/rid/'history.md';t=f.read_text(encoding='utf-8')
 if 'Round009 blind submission' not in t:
  t+='\\n- 2026-11-06 Round009 blind submission: TWO frozen neutral design options prepared, four independent seat reports pending; NO Round009 scores, accepted champion, owner selection or procurement release. Prior scored board outcome and existing blocked status preserved. Source SHA receipt state/ROUND009_SUBMISSION.json; private mapping withheld from critics.\\n'
  f.write_text(t,encoding='utf-8')
p.write_text(json.dumps(reg,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS three blocked TX rooms round009 pending, histories appended; no scores/owner releases, all 13 rooms preserved')

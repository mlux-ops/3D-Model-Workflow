from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
score=json.loads((R/'state/ROUND003_SCORING.json').read_text(encoding='utf-8'))['room_results']
path=R/'state/ROOMS.json'
state=json.loads(path.read_text(encoding='utf-8'))
fix={
 'TX-PRIMARY':['Exact measured DCOF for level floor and 2x2 pan is missing','Clay Ribbed cannot occupy wet shower walls without listing','Brizo 48in linear drain wall and pitch are unverified','Primary niche excluded; historic blended floor 905.58 not a separately quoted split'],
 'TX-POWDER':['Verify wall-mounted faucet 48140991 finish and 32526141 rough position','Coordinate 70/30 Camel/Wheat with measured mirror/elevation','Current two-color cartons, Chicago lead and owner approval not verified'],
 'TX-POWDER2':['Owner sink selection missing; Hansgrohe 73072341 is deck-mounted','Revisit unpriced flush insert only after panel dimensions, cleaning and quote','Preserve dry wall Indigo, wood floor, centered tile and mirror supports']
}
seen=set()
for room in state['rooms']:
 rid=room['id']
 if rid not in score:continue
 r=score[rid]
 assert room['round_003_submission']['status']=='blind_review_pending'
 room.update(status=r['status'],champion_id=r['champion_id'],champion_score=r['champion_score'],
             board_round_003=r,decision_blockers=fix[rid],last_round=3)
 room['round_003_submission'].update(status='review_complete_scored',scores={k:v['weighted_score'] for k,v in r['candidates'].items()},owner_approved=False)
 for item in fix[rid]:
  if item not in room['open_gaps']:room['open_gaps'].append(item)
 seen.add(rid)
folder_note={
 'TX-PRIMARY':'BLOCKED: both historic and proposed floor/pan variants lack measured exact wet DCOF; Ribbed wet approval absent and Brizo 48in linear drain pitch unverified. No primary niche. Revised scheme cannot pass cost critic minimum 3.0.',
 'TX-POWDER':'ACCEPTED AT BOARD: 70 percent Camel / 30 percent Wheat Haze 1.6x5 matte on dry vanity wall; wood floor unchanged. Geometry, wall faucet, colored grout and actual Chicago carton split held; NOT owner-approved.',
 'TX-POWDER2':'RETAIN historic v4 Indigo Edge relief dry feature wall. Revised hybrid flat insert cost critic 2.4 fails minimum 3.0, despite higher weighted score. Basin UNSELECTED, Hansgrohe deck faucet preserved.'
}
for rid in seen:
 r=score[rid];folder=R/'rooms'/rid
 inc=r['incumbent_letter'];ch=r['challenger_letter']
 s=r['candidates']
 rows=[]
 for k in (inc,ch):
  v=s[k]['seat_scores']
  rows.append('| {} | {:.1f} | {:.1f} | {:.1f} | {:.1f} | {:.2f} |'.format(k,v['market'],v['design'],v['build'],v['cost'],s[k]['weighted_score']))
 report=['# '+rid+' Round 003 final board','',
   'All 12 specialist critiques present and independent; exact six candidate SHA fingerprints matched before scoring.',
   '','| Candidate | Market .30 | Design .25 | Build .25 | Cost .20 | Weighted |',
   '|---|---:|---:|---:|---:|---:|']+rows+[
   '','Private mapping opened by prime only after all four critiques: incumbent '+inc+', challenger '+ch+'.',
   'Challenger delta {:+.2f}, minimum critic {:.1f}.'.format(r['margin'],s[ch]['minimum_critic_score']),
   '','**'+folder_note[rid]+'**','',
   '### Next fixes']+['- '+x for x in fix[rid]]+[
   '','No order, owner approval, vendor contacts or model/sheet writes. Prices are historical ELM 2026-09-03 not verified installed/landed costs; 15 percent source waste already in quantities.',
   'Sources: current four critic files, geometry.json, plumbing.json, manufacturer records, shared Old Town comps, state/ROUND003_SCORING.json.']
 (folder/'board/round-003/ROUND_REPORT.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
 with (folder/'history.md').open('a',encoding='utf-8') as f:
  f.write('\n- 2026-11-06 Round003: v4 {} {:.2f}, revised {} {:.2f} (delta {:+.2f}); {}. Owner not approved; see board/round-003/ROUND_REPORT.md.\n'.format(inc,s[inc]['weighted_score'],ch,s[ch]['weighted_score'],r['margin'],r['decision']))
 champion=folder/'champion.md'
 with champion.open('a',encoding='utf-8') as f:
  f.write('\n## Round 003 governing board update\n\n**'+folder_note[rid]+'** Weighted v4 {:.2f}; revised {:.2f}, delta {:+.2f}. Historical seeded wording above is superseded. Owner approval remains null.\n'.format(s[inc]['weighted_score'],s[ch]['weighted_score'],r['margin']))
 print('applied',rid,r['status'],r['champion_id'])
assert seen==set(score)
path.write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS round003 decisions applied')

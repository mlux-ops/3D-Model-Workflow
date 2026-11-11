"""Apply the independently collected PH R013 formal distinct-turn scored decision.

Never rewrite source candidates, critiques, submission/dispatch/collection or
earlier signed owner packages. Prior R010 scores remain in each room.
"""
from pathlib import Path
from decimal import Decimal
import hashlib,json

R=Path(__file__).resolve().parents[1]
scored=R/'state/ROUND013_SCORING.json'
data=json.loads(scored.read_text(encoding='utf-8'))
assert data['round']==13 and data['verification']['valid']
assert data['verification']['original_critics']==12 and data['verification']['criteria']==114
assert data['verification']['recalculated_seat_means']==24 and data['verification']['local_links']==333
assert not data['owner_approval'] and not data['procurement_release']
rooms_file=R/'state/ROOMS.json'
rooms=json.loads(rooms_file.read_text(encoding='utf-8'))
assert len(rooms['rooms'])==13
by={v['id']:v for v in rooms['rooms']}
assert set(data['room_results'])=={'PH-PRIMARY','PH-BATH2','PH-BATH4'}
for rid,x in data['room_results'].items():
    row=by[rid]
    assert row['status']=='blocked' and row['owner_status'] is None
    assert row['champion_id'] is None and row['champion_score'] is None and row['last_round']==13
    assert row['board_round_013']['status']=='pending_blind_four_seat_critic_reports_unscored'
    assert row['board_round_013']['all_critic_scores'] is None
    assert row['board_round_010']['status']=='blocked' and row['board_round_010']['champion_id'] is None
    assert x['status']=='blocked' and x['champion_id'] is None and x['champion_score'] is None
    assert not x['accepted_challenger'] and not x['owner_approved'] and not x['procurement_release']
    assert all(not v['all_hard_gates_pass'] for v in x['candidates'].values())
    assert not (R/'rooms'/rid/'board/round-013/ROUND_REPORT.md').exists()

scored_sha=hashlib.sha256(scored.read_bytes()).hexdigest()
prior_state=hashlib.sha256(rooms_file.read_bytes()).hexdigest()
for rid,x in data['room_results'].items():
    row=by[rid]
    folder=R/'rooms'/rid
    historic=x['historical_letter']; revised=x['revised_letter']
    a=x['candidates'][historic]; b=x['candidates'][revised]
    report=folder/'board/round-013/ROUND_REPORT.md'
    lines=[
      '# '+rid+' — Round013 four-independent-seat formally scored board','',
      '**BLOCKED. No candidate passes all mandatory wet-floor/pan evidence, installation, cost-specialist and owner gates. This is a conditional design study, not a gate-qualified champion, owner-signed finish selection, or purchasable specification.**','',
      '| Identity | Neutral letter | Market 0.30 | Design 0.25 | Build 0.25 | Cost 0.20 | Weighted | Minimum seat | Hard gates |',
      '|---|---|---:|---:|---:|---:|---:|---:|---:|',
    ]
    for title,letter in (('Historical source',historic),('Revised conditional',revised)):
        s=x['candidates'][letter]['individual_critic_scores']
        q=x['candidates'][letter]
        lines.append('| %s | %s | %.1f | %.1f | %.1f | %.1f | %.2f | %.1f | FAIL |'%(
          title,letter,s['market'],s['design'],s['build'],s['cost'],
          q['weighted_score'],q['minimum_critic_score']))
    lines.extend(['',
      '**Revised improvement:** %+.2f (must reach +0.25): **%s**. Minimum revised critic %.1f (must reach 3.0): **%s**. Independent wet and floor/pan hard gates: **FAIL**. No budget >125%% failure asserted because owner room cap and current installed quote are unavailable.'%(
        x['challenger_margin'],'PASS' if x['challenger_margin_at_least_025'] else 'FAIL',
        b['minimum_critic_score'],'PASS' if b['all_critics_at_least_3'] else 'FAIL'),
      '',
    ])
    for letter in (historic,revised):
        q=x['candidates'][letter]
        lines.extend(['### Candidate '+letter+' — '+q['role'],'',
          *['- '+g for g in q['gate_reasons']],''])
    lines.extend([
      '### Owner/GC release classification','',
      '**Design/sample direction only:** revised candidate '+revised+' scored %.2f; it has no gate-qualified champion, and the source historical selection remains a dated procurement reference, not accepted.'%b['weighted_score'],
      '**Original dated material-only source:** $%.2f per copy, two PH copies; all original gross includes 15%% waste ONCE; no duplicated shared WC or niche and no independent extra pan or trims.'%row['carried_quote_material_subtotal_usd_per_unit'],
      '**Original source basis:** 2026-09-03 Smartsheet quote; existing 13-room historic four-unit material total $23,572.44. No current Chicago landed/installed bid or owner-approved cap.',
      '**Model identity:** live Revit title 1527, not certified 1529; source W1/W2/W3 and tub/drain positions remain provisional; Revit/Smartsheet READ ONLY.',
      '**Audit:** state/ROUND013_SCORING.json SHA '+scored_sha+' is distinct-turn formal scoring. Original submission/dispatch/collection remain all_critic_scores:null; six frozen neutral source packets and twelve authentic four-seat reports untouched.',
      '**Owner/procurement:** unapproved and not ordered; no emails, vendor calls, sample orders or procurement release.',
    ])
    report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    row['board_round_013']=x
    row['round_013_conditional_design_direction']='Letter '+revised+' weighted '+str(b['weighted_score'])+' is visual/sample study ONLY. All gates FAIL and cost/build minimum <3.'
    row['round_013_evidence_priority']='; '.join(b['gate_reasons'])
    row['open_gaps']=list(dict.fromkeys(row.get('open_gaps',[])+['Round013 revised conditional: '+row['round_013_evidence_priority']]))
    row['status']='blocked';row['champion_id']=None;row['champion_score']=None;row['last_round']=13
    path=folder/'champion.md'
    text=path.read_text(encoding='utf-8')
    assert '## Round013 governing scored board' not in text
    lines=text.splitlines()
    lines[0]='# '+rid+' — Round013 BLOCKED (historic v4 source retained for audit)'
    head=('**Current status:** Round013 BLOCKED. Historical %s %.2f; revised %s %.2f, margin %+.2f; revised minimum critic %.1f. No accepted champion, owner selection, or purchase authorization. V4 source below remains historical only.'%(
      historic,a['weighted_score'],revised,b['weighted_score'],
      x['challenger_margin'],b['minimum_critic_score']))
    idx=next((i for i,z in enumerate(lines[:9]) if z.startswith(('**Current status:**','**Status:**'))),None)
    if idx is None:lines.insert(1,head)
    else:lines[idx]=head
    text='\n'.join(lines)+'\n\n## Round013 governing scored board\n\n**BLOCKED; original source and all twelve critics preserved.**\n\n'+'\n'.join('- '+g for g in b['gate_reasons'])+'\n\nSee board/round-013/ROUND_REPORT.md.\n'
    path.write_text(text,encoding='utf-8')
    history=folder/'history.md'
    old=history.read_text(encoding='utf-8')
    assert 'Round013 formal distinct-turn scoring' not in old
    more=(
      '\n- 2026-11-06 Round013 formal distinct-turn scoring after worker-14 non-Pro CONTINUE and 12 authentic independent reports: historical %s %.2f, revised %s %.2f, margin %+.2f, revised minimum %.1f. BOTH blocked by floor/pan DCOF and other technical/price/owner holds; no valid champion or purchase. Original six candidate/twelve critic source hashes and null-scored source/dispatch/collection unchanged. See board/round-013/ROUND_REPORT.md.\n'
      %(historic,a['weighted_score'],revised,b['weighted_score'],x['challenger_margin'],b['minimum_critic_score']))
    history.write_text(old+more,encoding='utf-8')
rooms_file.write_text(json.dumps(rooms,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
for rid,x in data['room_results'].items():
    a=x['candidates'][x['historical_letter']]
    b=x['candidates'][x['revised_letter']]
    print(rid,'hist',a['weighted_score'],'revised',b['weighted_score'],'BLOCKED; champion NULL')
print('PASS R013 scored reports/champions/histories and 13-room register synchronized; earlier scores/evidence preserved, scores source receipts untouched')
print('ROOMS SHA',prior_state,'=>',hashlib.sha256(rooms_file.read_bytes()).hexdigest())

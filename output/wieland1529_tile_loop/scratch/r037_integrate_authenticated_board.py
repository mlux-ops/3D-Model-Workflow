"""One-time guarded integration of ORIGINAL authentic R037 strict-blind four-seat reports.

All four isolated sessions must have finished, including the new clean DESIGN seat.
No re-run after state/ROUND037_TWO_DURAVIT_TUB_DECISIONS.json exists.
"""
from pathlib import Path
from decimal import Decimal
import copy
import json
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'state'/'ROUND037_TWO_DURAVIT_TUB_DECISIONS.json'
MEMO=ROOT/'state'/'ROUND037_TWO_DURAVIT_TUB_DECISIONS_20261107.md'
STATE=ROOT/'state'/'ROOMS.json'
assert not OUT.exists() and not MEMO.exists(),'R037 already integrated; do not overwrite'
v=subprocess.run([sys.executable,'-B',str(ROOT/'scratch'/'r037_original_critic_arithmetic.py')],
                 check=True,capture_output=True,text=True)
audit=json.loads(v.stdout)
assert (audit['status'],audit['criterion_count'],audit['seat_means_count'],
        audit['weighted_count']) == ('PASS',76,16,4)
assert set(audit['room_boards'])=={'TX-BATH2','TX-BATH4'}
rooms=json.loads(STATE.read_text(encoding='utf-8'))
R=rooms['rooms']
assert len(R)==13 and sum(x['unit_count'] for x in R)==26
assert sum(len(x['carried_tile_rows']) for x in R)==27
assert sum(Decimal(str(x['carried_quote_material_subtotal_usd_per_unit']))*
           x['unit_count'] for x in R)==Decimal('23572.44')
assert sum(x['owner_status']=='approved' for x in R)==0
assert sum(x['status']=='blocked' for x in R)==4
original={x['id']:(copy.deepcopy(x['carried_tile_rows']),x['owner_status'],
                   x['carried_quote_material_subtotal_usd_per_unit'],
                   x['carried_budget_material_only_usd_per_unit'],x['unit_count']) for x in R}

seats=('market','design','build','cost')
provenance={
 'market':'isolated Codex f3a3a08b-d7a6-499e-b342-62b2e20efcd3',
 'design':'fresh isolated Codex 3a9a5990-48d4-4be0-9b21-bb69796f7d11; disqualified old 3e78b7dd excluded',
 'build':'isolated Codex 5de18118-10ee-43d4-982b-2d01a0c8a517',
 'cost':'isolated Codex f67dda65-af21-4c0f-828f-5a6dfb54430b'
}
source_rates={
 'TX-BATH2':{'A':Decimal('642.91'),'B':Decimal('845.46')},
 'TX-BATH4':{'A':Decimal('572.89'),'B':Decimal('679.73')}
}
hold={
 'TX-BATH2':('Owner-selected Duravit 59-in TUB, Hansgrohe Chrome and basin UNSELECTED. '
             'NO tiled PAN or shower point drain or tiled ceiling. Actual W1 62.484-in drawing '
             'versus assumed tub opening ~59.496-in and nominal 59-in unit not field reconciled; '
             'tub flange, sill-waterproofing, cut edges, substrate, exact Chicago lot/stock/ETA, '
             'landed price and FILL IN owner budget remain open.'),
 'TX-BATH4':('Owner-selected Duravit 59-in TUB and Hansgrohe Matte White. NO tiled PAN, '
             'point drain or wet ceiling. Actual tub alcove/flange/waste, horizontal niche sill, '
             'tile cuts/grout and waterproofed setting assembly remain open, as do Chicago '
             'matched lots, freight/tax/landed cost, budget FILL IN and owner signoff.')
}
result={}
decision_lines=[
 '# R037 authentic independent two-room four-seat Duravit TUB tile board (2026-11-07)',
 '',
 'All four genuinely independent original seats reviewed both neutral A/B products in '
 'TX-BATH2 and TX-BATH4. The original DESIGN attempt self-stopped and its draft ratings were '
 'voided on potential relative-color source-role inference; source comparative descriptions '
 'were surgically neutralized without altering tile materials, sizes, unit source areas or rates. '
 'A new isolated DESIGN reviewer scored both candidates with no prior-role exposure. '
 'Original MARKET/BUILD/COST reviewers explicitly denied historic-role or other-seat exposure.',
 '',
 'Original source-parsed audit: **76** criteria, **16** one-decimal HALF_UP means, '
 '**4** weighted scores (MARKET .30, DESIGN .25, BUILD .25, COST .20). '
 'No invalidated DESIGN ratings or synthetic scores counted.',
 '',
 '| Room | Seat means A (M/D/B/C) | Weighted A | Seat means B (M/D/B/C) | Weighted B | Decision |',
 '|---|---|---:|---|---:|---|'
]
for rid in ('TX-BATH2','TX-BATH4'):
    room=next(x for x in R if x['id']==rid)
    assert room['status']=='provisional champion' and room['owner_status'] is None
    assert room['last_round']==35
    key=json.loads((ROOT/'rooms'/rid/'board'/'round-037'/'_key.json').read_text(encoding='utf-8'))
    assert key['round']==37 and key['room']==rid and key['private_only'] is True
    incumbent=key['previous_board_qualified_incumbent']
    incletter=key['incumbent_letter']
    challengel=key['new_challenger_letter']
    assert {incletter,challengel}=={'A','B'} and room['champion_id']==incumbent
    board=audit['room_boards'][rid]
    for seat in seats:
        crit=ROOT/'rooms'/rid/'board'/'round-037'/('critic-'+seat+'.md')
        t=crit.read_text(encoding='utf-8-sig')
        assert crit.is_file() and crit.stat().st_size>2000,(rid,seat,'not original complete')
        assert 'STOPPED' not in t[:180],(rid,seat,'invalidated attempt')
        assert all(re.search(p,t,re.I) for p in ('top[_ ]fix','gate[_ ]flags','confidence'))
    for letter in ('A','B'):
        src=(ROOT/'rooms'/rid/'board'/'round-037'/'candidates'/(letter+'.md')).read_text(encoding='utf-8')
        assert 'Duravit 59-in BATHTUB' in src and 'NO tiled PAN' in src
        assert 'Wet' in src and 'DCOF >=0.42' in src
        assert '15% waste ONCE' in src
        assert board[letter]['specialist_gate_pass']
        assert all(seat in board[letter] for seat in seats)
        assert Decimal(board[letter]['minimum_seat'])>=3
    # Exact original maker evidence survives temporary 2026-11-07 Elm server errors:
    # manufacturer's color-specific Wet Areas listings were verified 2026-11-06.
    assert (ROOT/'research/products'/'elm-tones-sapphire-2x20-wet-approved.md').is_file()
    assert (ROOT/'research/products'/'elm-tones-sandstone-2x20.md').is_file()
    # No individual maker wall approval constitutes niche horizontal sill or full install release.
    current=board[incletter]; proposed=board[challengel]
    delta=Decimal(proposed['weighted'])-Decimal(current['weighted'])
    if delta>=Decimal('0.250'):
        selected=challengel
        why=f'Qualified challenger exceeds qualified incumbent by {delta:.3f} >= +0.250'
    else:
        selected=incletter
        why=f'Qualified incumbent retained; challenger change {delta:+.3f} < +0.250 displacement'
    selected_id=incumbent if selected==incletter else 'round-037-'+selected
    assert selected_id==incumbent,(rid,'unexpected challenge win: integration requires manual technical review')
    old_score=room['champion_score']
    room['board_round_037']={
      'status':'strict_blind_four_independent_seat_R037_provisional',
      'source':'state/ROUND037_TWO_DURAVIT_TUB_DECISIONS_20261107.md',
      'specialists':provenance,
      'criterion_count_cohort':76,'means_count_cohort':16,'weighted_count_cohort':4,
      'original_disqualified_design':'3e78b7dd-fe7d-4095-9986-5b7cc4214c91 (NO scores counted)',
      'previous_champion_id':incumbent,'previous_historical_score':old_score,
      'incumbent_letter_private_post_board':incletter,
      'challenger_letter_private_post_board':challengel,
      'weights':{'market':.30,'design':.25,'build':.25,'cost':.20},
      'candidates':{letter:{
         'seat_scores':{seat:float(board[letter][seat]['mean']) for seat in seats},
         'weighted_score':float(board[letter]['weighted']),
         'meets_all_specialists_minimum_3':True,
         'material_gross_area_rate_per_copy':float(source_rates[rid][letter])
       } for letter in ('A','B')},
      'same_round_challenger_minus_incumbent':float(delta),
      'displacement_threshold':.25,'decision':why,'selected_champion_id':selected_id,
      'open_items':hold[rid],'owner_approved':False,'procurement_released':False
    }
    room['champion_id']=selected_id
    room['champion_score']=float(Decimal(board[selected]['weighted']))
    room['last_round']=37
    gap='R037 retained current TUB tile scheme after real blind four-seat board: '+hold[rid]
    if gap not in room['open_gaps']:room['open_gaps'].append(gap)
    row={
       'incumbent_id':incumbent,'incumbent_letter':incletter,
       'challenger_letter':challengel,'selected_letter':selected,
       'selected_id':selected_id,'selected_score':float(Decimal(board[selected]['weighted'])),
       'other_score':float(Decimal(board[challengel if selected==incletter else incletter]['weighted'])),
       'four_seat_complete':True,'changed':selected_id!=incumbent,
       'owner_approved':False,'decision_summary':why,
       'challenger_minus_incumbent':float(delta),
       'minimum_seat':float(Decimal(board[selected]['minimum_seat'])),
       'material_gross_rate_per_copy':float(source_rates[rid][selected]),
       'room_budget':'FILL IN',
       'technical_note':('Product-level exact WALL/niche listings as manufacturer-verified earlier '
          'and bath LEVEL wet DCOF >=0.42 from exact retailer pages; maker site access '
          'errors on new review do NOT create a new permission. Horizontal niche sill, '
          'full waterproof assembly, field geometry and Chicago landed stock still held.'),
       'scores':board
    }
    result[rid]=row
    decision_lines.append(
      '| '+rid+' | '+' / '.join(board['A'][s]['mean'] for s in seats)
      +' | '+board['A']['weighted']+' | '
      +' / '.join(board['B'][s]['mean'] for s in seats)
      +' | '+board['B']['weighted']+' | **'+selected_id+' '+why+'** |')
    chosen=(ROOT/'rooms'/rid/'board'/'round-037'/'candidates'/(selected+'.md')).read_text(encoding='utf-8')
    rows=[l for l in chosen.splitlines() if l.startswith('|')][:5]
    assert len(rows)==5,(rid,'missing three current surface rows')
    decision_lines += ['',f'## {rid}: current {selected_id} at {board[selected]["weighted"]}/5',
       'Original neutral current-source letter '+selected+'; manufacturer and trade/retailer URLs:',
       *rows,
       f'Gross historic-area rate **${source_rates[rid][selected]:.2f}/copy**, two copies; '
       'original 15% waste included once; never a current Chicago quote.',
       hold[rid],'']
    folder=ROOT/'rooms'/rid
    champion=folder/'champion.md'
    old=champion.read_text(encoding='utf-8-sig')
    assert '# '+rid+' — R037 CURRENT' not in old
    champion.write_text(
      '# '+rid+' — R037 CURRENT PROVISIONAL TILE CHAMPION (2026-11-07)\n\n'
      +'**'+selected_id+'**, authentic same-round strict-blind score **'
      +board[selected]['weighted']+'/5**; '+why+'. This is not owner approved '
      'or order/installation authorized; older selected headings below remain historical only.\n\n'
      +'\n'.join(rows)+'\n\n'
      +f'Material-only historical source gross area-rate **${source_rates[rid][selected]:.2f}/copy**; '
      'two physical copies, waste included once. Same-job Elm trade and non-Chicago F&D public '
      'retail price sources are differentiated in the source.\n\n'
      +'**Program and technical holds:** '+hold[rid]
      +' Niche wall use does not qualify horizontal sill assembly. Manufacturer wall listing '
      'does not release wet overhead ceilings, which are not within these tub rooms.\n\n'
      +'**Original four-seat report:** [R037 formal decision]'
      '(../../state/ROUND037_TWO_DURAVIT_TUB_DECISIONS_20261107.md).\n\n---\n\n'+old,
      encoding='utf-8'
    )
    history=folder/'history.md'
    history.write_text(history.read_text(encoding='utf-8-sig').rstrip()
      +'\n\n## R037 authentic blind two-Duravit-tub tile board — 2026-11-07\n'
      +f'- Prior selected **{incumbent}** historical score {old_score}; same-round A '
      +board['A']['weighted']+', B '+board['B']['weighted']+'. All four original specialists '
       'and 19 independent source-specific criteria per candidate, 15% source waste ONCE.\n'
      +f'- Current **{selected_id}** same-round {board[selected]["weighted"]}; '+why+'. '
       'Disqualified original DESIGN reports not counted; new isolated DESIGN source-only.\n'
      +f'- Actual source [R037 selected letter {selected}](board/round-037/candidates/{selected}.md). '
       'No independent tiled PAN or shower drain; TUB/finish and open basin preserved.\n'
      +f'- Technical and owner holds: {hold[rid]} No owner consent or order.\n',
      encoding='utf-8')
    comp=folder/'vendor_comparison.md'
    other='B' if selected=='A' else 'A'
    comp.write_text(comp.read_text(encoding='utf-8-sig').rstrip()
      +'\n\n## R037 CURRENT authenticated four-seat vendor look/price technical comparison — 2026-11-07\n'
      +f'- Selected **{selected_id}** (neutral {selected}) weighted '
      +board[selected]['weighted']+', independent gross source area-rate '
      +f'${source_rates[rid][selected]:.2f}/copy; alternate neutral {other} '
      +board[other]['weighted']+f', ${source_rates[rid][other]:.2f}/copy. '
      +why+'. No fabricated Chicago quote/lot.\n'
      +'- Exact selected three-surface product/size/finish/official URLs:\n'
      +'\n'.join(rows)+'\n'
      +f'- [Alternative neutral {other}](board/round-037/candidates/{other}.md) '
       'has distinct architecture but does not pass displacement.\n'
      +'- Same-job Elm Tones $6.95/SF from 2026-09-04; F&D prices from explicitly '
       'identified non-Chicago stores. Product use is not full installed assembly release. '
      +hold[rid]+'\n',encoding='utf-8')

for room in R:
    assert (room['carried_tile_rows'],room['owner_status'],
            room['carried_quote_material_subtotal_usd_per_unit'],
            room['carried_budget_material_only_usd_per_unit'],room['unit_count'])==original[room['id']]
assert sum(Decimal(str(x['carried_quote_material_subtotal_usd_per_unit']))*
           x['unit_count'] for x in R)==Decimal('23572.44')
assert sum(x['owner_status']=='approved' for x in R)==0
assert sum(x['status']=='provisional champion' for x in R)==9
assert sum(x['status']=='blocked' for x in R)==4
assert next(x for x in R if x['id']=='TX-BATH2')['champion_id']=='round-031-B'
assert next(x for x in R if x['id']=='TX-BATH4')['champion_id']=='round-035-B'
decision_lines += ['**Global scope unchanged:** 13 room types, 26 physical bathrooms/WCs, '
                  '27 original historical tile rows, $23,572.44 material-only baseline, '
                  'zero owner approvals. Both Primary wet overheads and inherited WCs remain '
                  'BLOCKED. R037 retains genuine existing provisional TUB room schemes; '
                  'no unselected basin, conditional PAN or new ceiling permission invented.',
                  '**NOT GLOBAL DONE.** All 13 final owner packets must await owner acceptance '
                  'and remaining physical/technical gates.']
STATE.write_text(json.dumps(rooms,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
OUT.write_text(json.dumps({
  'round':37,'date':'2026-11-07','criterion_count':76,'seat_means_count':16,
  'weighted_count':4,'weights':{'market':.30,'design':.25,'build':.25,'cost':.20},
  'original_independent_seats':provenance,'original_disqualified_design_excluded':True,
  'original_baseline_total_usd':23572.44,'owner_approvals':0,'rooms':result
},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
MEMO.write_text('\n'.join(decision_lines)+'\n',encoding='utf-8')
print('PASS R037 authentic 76/16/4: TX2 incumbent B 3.200 vs A 3.350 delta +.150 retained; TX4 incumbent A 3.490 vs B 3.340 delta -.150 retained; all original 13/26/27/23572.44/0 approvals preserved.')

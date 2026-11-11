"""Integrate ONLY a complete, authenticated R036 four-seat tile-selection board.

Precondition: 12 original uncontaminated critic files, original report provenance,
independent 114/24/6 arithmetic and exact manufacturer hard gates confirmed by prime.
No further workers, procurement or external-system actions here.
"""
from pathlib import Path
from decimal import Decimal
from datetime import date
import copy
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'state' / 'ROOMS.json'
MEMO = ROOT / 'state' / 'ROUND036_THREE_WET_BATH_DECISIONS_20261107.md'
JOUT = ROOT / 'state' / 'ROUND036_THREE_WET_BATH_DECISIONS.json'
SEATS = ('market', 'design', 'build', 'cost')
WEIGHTS = {'market': .30, 'design': .25, 'build': .25, 'cost': .20}
ROLES = {
    'PH-BATH4': ('round-030-B', 'A', 'B'),
    'PH-BATH3': ('round-030-A', 'B', 'A'),
    'TX-BATH3': ('round-031-B', 'A', 'B'),
}
RATES = {
    'PH-BATH4': {'A': '616.01', 'B': '500.70'},
    'PH-BATH3': {'A': '598.71', 'B': '799.37'},
    'TX-BATH3': {'A': '685.92', 'B': '792.27'},
}
HOLD = {
    'PH-BATH4': ('Owner WALK-IN selected; Brizo Brilliance BNX BT062415-BNX square POINT. '
                 'Single original 40.2 SF combined LEVEL/PAN gross per copy, already includes 15% waste once; '
                 'owner 35 vs drawing 27 SF floor discrepancy. Confirm field four-plane cuts/slopes, '
                 '>=3-in visible cuts, drain grate/rough, niche sill/penetration waterproofing, '
                 'Chicago matching lot/ETA/landed price, FILL IN budget and owner consent.'),
    'PH-BATH3': ('Owner TUB/WALK-IN UNSELECTED, basin UNSELECTED; Hansgrohe Chrome unchanged. '
                 'Delta Chrome DT062412 POINT exclusively if WALK-IN, never a bathtub waste. '
                 'Original bathroom LEVEL 40.2 SF per copy; conditional additional WALK-IN PAN SF/cost '
                 'NULL (not zero), independent of LEVEL gross. Verify tub flange versus point rough, '
                 'niche sill, field cuts, Chicago lots and owner budget FILL IN.'),
    'TX-BATH3': ('Owner TUB/WALK-IN UNSELECTED; Brizo BNX BT062415-BNX POINT exclusively if WALK-IN. '
                 'Original bathroom LEVEL 42.5 SF per copy, 15% gross waste counted once; '
                 'additional conditional WALK-IN PAN SF/cost NULL (not zero). Verify independent tub waste '
                 'if TUB, BNX grate/rough/slopes if WALK-IN, niche sill, Chicago lots and owner budget FILL IN.'),
}
assert not MEMO.exists() and not JOUT.exists(), 'R036 already integrated; never overwrite'
p = subprocess.run([sys.executable, '-B', str(ROOT/'scratch'/'r036_original_critic_arithmetic.py')],
                   capture_output=True, text=True, check=True)
payload = json.loads(p.stdout)
assert payload['status'] == 'PASS'
assert (payload['criterion_count'],payload['seat_means_count'],payload['weighted_count'])==(114,24,6)
state = json.loads(STATE.read_text(encoding='utf-8'))
rooms = state['rooms']
assert (len(rooms),sum(r['unit_count'] for r in rooms),
        sum(len(r['carried_tile_rows']) for r in rooms)) == (13,26,27)
carried = {r['id']:copy.deepcopy(r['carried_tile_rows']) for r in rooms}
owner_vals = {r['id']:(r['owner_status'],r['carried_quote_material_subtotal_usd_per_unit'],
                      r['carried_budget_material_only_usd_per_unit'],r['unit_count']) for r in rooms}
total = sum(Decimal(str(r['carried_quote_material_subtotal_usd_per_unit'])) *
            r['unit_count'] for r in rooms)
assert total == Decimal('23572.44')
assert sum(r['owner_status']=='approved' for r in rooms)==0
assert sum(r['status']=='provisional champion' for r in rooms)==9
assert sum(r['status']=='blocked' for r in rooms)==4

plans={}
for rid,(inc_id,incletter,challletter) in ROLES.items():
    room = next(r for r in rooms if r['id']==rid)
    assert (room['champion_id'],room['last_round'],room['status']) == (inc_id,34,'provisional champion')
    assert room['owner_status'] is None
    key = json.loads((ROOT/'rooms'/rid/'board'/'round-036'/'_key.json').read_text(encoding='utf-8'))
    # Read sealed roles only after all 12 critiques and 114 original criteria exist.
    assert key.get('incumbent_neutral_letter') == incletter,(rid,'sealed incumbent mismatch',key)
    assert key.get('new_material_challenger_neutral_letter') == challletter,(rid,'sealed challenger mismatch',key)
    assert key.get('previous_genuinely_product_board_qualified_provisional_incumbent') == inc_id,(rid,'sealed identity mismatch',key)
    scores = payload['room_boards'][rid]
    assert set(scores)=={'A','B'}
    for letter in ('A','B'):
        assert all(s in scores[letter] for s in SEATS),(rid,letter,'incomplete critics')
        for s in SEATS:
            path=ROOT/'rooms'/rid/'board'/'round-036'/('critic-'+s+'.md')
            assert path.is_file() and path.stat().st_size>800,(rid,s,'missing original')
            text=path.read_text(encoding='utf-8-sig')
            assert re.search(r'(?i)top[_ ]fix',text) and re.search(r'(?i)gate[_ ]flags',text) and re.search(r'(?i)confidence',text),(rid,s)
        candidate=ROOT/'rooms'/rid/'board'/'round-036'/'candidates'/(letter+'.md')
        source=candidate.read_text(encoding='utf-8')
        assert '15% waste ONCE' in source and 'https://www.flooranddecor.com/' in source
        assert 'DCOF >=0.42' in source and 'Shower Floors YES' in source
        assert 'Wet WALL' in source and 'Bathroom LEVEL' in source
        assert not re.search(r'(?i)discontinued|owner veto',source[:1000])
    inc,chall = scores[incletter],scores[challletter]
    incpass = bool(inc['specialist_gate_pass'])
    chpass = bool(chall['specialist_gate_pass'])
    delta = Decimal(chall['weighted'])-Decimal(inc['weighted'])
    if not incpass and chpass:
        selectedletter=challletter
        why='incumbent fails minimum specialist >=3.0; eligible challenger takes over'
    elif incpass and chpass and delta>=Decimal('0.250'):
        selectedletter=challletter
        why=f'eligible challenger beats qualified incumbent by {delta:.3f} >=0.250'
    elif incpass:
        selectedletter=incletter
        why=f'eligible incumbent defended; challenger delta {delta:.3f} below effective displacement'
    else:
        raise RuntimeError(f'{rid} has no eligible candidate: do NOT promote or write R036 selection')
    selected_id = inc_id if selectedletter==incletter else 'round-036-'+challletter
    selected = scores[selectedletter]
    otherletter = 'B' if selectedletter=='A' else 'A'
    plans[rid]={
        'incumbent_id':inc_id,
        'incumbent_letter':incletter,
        'challenger_letter':challletter,
        'selected_letter':selectedletter,
        'selected_id':selected_id,
        'selected_score':float(selected['weighted']),
        'other_score':float(scores[otherletter]['weighted']),
        'four_seat_complete':True,
        'changed':selected_id!=inc_id,
        'decision_summary':why,
        'challenger_minus_incumbent':float(delta),
        'incumbent_eligible_minimum':incpass,
        'challenger_eligible_minimum':chpass,
        'minimum_seat':float(selected['minimum_seat']),
        'room_budget':'FILL IN',
        'owner_approved':False,
        'allowed_vendor_maker_applications':'Product-level maker wet WALL/vertical niche and separate exact LEVEL/PAN Shower Floor YES, wet DCOF>=0.42 checked; full physical assembly/field cuts NOT released',
        'material_gross_rate_per_copy':float(Decimal(RATES[rid][selectedletter])),
        'original_15_percent_waste':'included once; no new per-copy area or duplicated PAN purchase',
        'conditional_pan_extra_sf':None,
        'conditional_pan_extra_cost':None,
        'scores':scores,
    }
    old_score = room['champion_score']
    room['board_round_036']={
        'status':'strict_blind_four_independent_seat_R036_provisional',
        'source':'state/ROUND036_THREE_WET_BATH_DECISIONS_20261107.md',
        'specialists':{
            'market':'worker-74',
            'design':'codex isolated 8524a1a2-6920-4242-ad32-5429899ee16d',
            'build':'worker-78',
            'cost':'codex isolated dc724613-91ef-4e80-b891-0d38b51c7b9c; same blinded evaluator corrected source in 810eda39-5591-4a26-886f-3e446ebcb265'
        },
        'weights':WEIGHTS,
        'criterion_count_cohort':114,
        'previous_champion_id':inc_id,
        'previous_champion_score_historical':old_score,
        'incumbent_letter_private_after_scoring':incletter,
        'challenger_letter_private_after_scoring':challletter,
        'qualified_incumbent':incpass,
        'qualified_challenger':chpass,
        'displacement_threshold':0.25,
        'margin_same_round':float(delta),
        'decision':why,
        'candidates':{letter:{
            'seat_scores':{s:float(scores[letter][s]['mean']) for s in SEATS},
            'weighted_score':float(scores[letter]['weighted']),
            'meets_all_specialists_minimum_3':bool(scores[letter]['specialist_gate_pass']),
            'material_rate_screen_usd_per_copy':float(Decimal(RATES[rid][letter])),
        } for letter in ('A','B')},
        'selected_champion_id':selected_id,
        'owner_approved':False,'procurement_released':False,
        'open_items':HOLD[rid]
    }
    room['last_round']=36
    room['champion_id']=selected_id
    room['champion_score']=float(selected['weighted'])
    note='R036 original four-seat selections: '+HOLD[rid]
    if note not in room['open_gaps']:room['open_gaps'].append(note)

for room in rooms:
    assert room['carried_tile_rows']==carried[room['id']]
    assert (room['owner_status'],room['carried_quote_material_subtotal_usd_per_unit'],
            room['carried_budget_material_only_usd_per_unit'],room['unit_count'])==owner_vals[room['id']]
assert sum(Decimal(str(r['carried_quote_material_subtotal_usd_per_unit'])) *
           r['unit_count'] for r in rooms)==Decimal('23572.44')
assert sum(r['owner_status']=='approved' for r in rooms)==0
assert next(r for r in rooms if r['id']=='TX-BATH4')['champion_id']=='round-035-B'
assert all(next(r for r in rooms if r['id']==rid)['status']=='blocked' for rid in ('PH-PRIMARY','TX-PRIMARY','PH-WC','TX-WC'))

decision={
    'round':36,'date':'2026-11-07',
    'original_criterion_count':114,
    'criterion_count':114,'seat_means_count':24,'weighted_count':6,
    'weights':WEIGHTS,
    'blind_integrity':'Original MARKET74 and BUILD78 strict-blind verified; isolated DESIGN 8524a1a2 and COST dc724613 (continued 810eda39) independently source-only; contaminated attempts 75/76/77/79/80 excluded',
    'technical_note':'Only exact tile product applications checked; assembly/geometry/owner/commercial holds retained',
    'owner_approvals':0,'rooms':plans
}
lines=['# R036 three-room authentic four-seat tile selection (2026-11-07)',
       '',
       '**Independent review:** 114 original criterion ratings, 24 one-decimal HALF_UP specialist means, six weighted scores. Weights MARKET .30, DESIGN .25, BUILD .25, COST .20. Contaminated attempted seats excluded; no invented scores. Product-level use pass is not installation or owner acceptance.',
       '',
       '| Room | Incumbent A/B | Same-round scores A / B | Min seats A / B | Decision |',
       '|---|---|---|---|---|']
for rid,pick in plans.items():
    scores=pick['scores']
    a=scores['A'];b=scores['B']
    lines.append(f"| {rid} | {pick['incumbent_id']} ({pick['incumbent_letter']}) | "
                 f"{a['weighted']} / {b['weighted']} | {a['minimum_seat']} / {b['minimum_seat']} | "
                 f"**{pick['selected_id']}** ({pick['decision_summary']}) |")
lines.extend(['',
   '## Exact current selected tile surfaces by room',
   ''])
for rid,pick in plans.items():
    letter=pick['selected_letter']
    candidate=(ROOT/'rooms'/rid/'board'/'round-036'/'candidates'/(letter+'.md')).read_text(encoding='utf-8')
    table=candidate.split('| Surface |',1)[1].split('**Floor/pan gate',1)[0].strip()
    lines.extend([f"### {rid}: {pick['selected_id']}, score {pick['selected_score']:.3f}",
                  f"Selected **R036 letter {letter}**. Exact source [candidate {letter}](../rooms/{rid}/board/round-036/candidates/{letter}.md); maker URLs and full per-SF/box source details reproduced:",
                  '| Surface |'+table,
                  f"Material-only gross rate **${RATES[rid][letter]} per copy**, not current Chicago quote; 2 physical copies. {HOLD[rid]}",
                  f"Unselected A/B original independent critics remain in rooms/{rid}/board/round-036/critic-{{market,design,build,cost}}.md.",
                  ''])
lines.extend(['**Global unchanged:** 13 room types / 26 physical instances / 27 original material rows / original $23,572.44 material-only basis / historical 15% once / 0 owner approvals. Three Duravit TUB bath programs, wet-ceiling BLOCKED Primaries and WC inheritance, dry powders and existing wood floors, factory-solid Brizo 48-in BNX LINEAR Primary drains with no niches all unchanged.',
              '**No global DONE** without exact maker wet-overhead ceiling permission, documented compatible ceiling assembly, owner approvals and physically verified final one-page packets.'])

# All preconditions have passed; make authorized, additive current-file changes.
STATE.write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
JOUT.write_text(json.dumps(decision,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
MEMO.write_text('\n'.join(lines)+'\n',encoding='utf-8')
for rid,pick in plans.items():
    base=ROOT/'rooms'/rid
    selected=pick['selected_letter']
    source=(base/'board'/'round-036'/'candidates'/(selected+'.md')).read_text(encoding='utf-8')
    table='| Surface |'+source.split('| Surface |',1)[1].split('**Floor/pan gate',1)[0].strip()
    old=(base/'champion.md').read_text(encoding='utf-8-sig')
    assert '# '+rid+' — R036 CURRENT' not in old
    curr=(f"# {rid} — R036 CURRENT PROVISIONAL TILE CHAMPION (2026-11-07)\n\n"
          f"**{pick['selected_id']}** at independent R036 **{pick['selected_score']:.3f}/5**, "
          f"{pick['decision_summary']}. This current recommendation supersedes older 'current' headings below, "
          f"which are retained exclusively as historical evidence. NOT owner-approved, ordered or installation-authorized.\n\n"
          f"{table}\n\n"
          f"**Original gross material-rate screen:** ${RATES[rid][selected]}/copy, two copies. "
          f"Same-job 2026-09-04 Elm quote and dated out-of-state Floor & Decor retailer pricing are "
          f"separately identified above; Chicago landed cost/stock not verified; 15% source gross waste ONCE.\n\n"
          f"**Plumbing, program and maker/field holds:** {HOLD[rid]} No manufacturer wet-wall "
          f"permission alone certifies the horizontal niche sill or an overhead wet shower ceiling.\n\n"
          f"**Four original seat critiques:** [formal R036 decision](../../state/ROUND036_THREE_WET_BATH_DECISIONS_20261107.md), "
          f"R036 current neutral source A/B and original critics in board/round-036.\n\n---\n\n")
    (base/'champion.md').write_text(curr+old,encoding='utf-8')
    history=base/'history.md'
    prev=history.read_text(encoding='utf-8-sig').rstrip()
    history.write_text(prev+f"\n\n## R036 current strict-blind independent tile board — 2026-11-07\n\n"
                       f"- Retained previously selected **{pick['incumbent_id']}** historic original score in older sections; new same-round reassessment A {pick['scores']['A']['weighted']}, B {pick['scores']['B']['weighted']}.\n"
                       f"- Current **{pick['selected_id']}**, R036 {pick['selected_score']:.3f}; {pick['decision_summary']}. Specialist minimum A {pick['scores']['A']['minimum_seat']}, B {pick['scores']['B']['minimum_seat']}.\n"
                       f"- Exact selected maker/SKU/size/finish/price/official URLs are in current [neutral source {selected}](board/round-036/candidates/{selected}.md) and formal [R036 decision](../../state/ROUND036_THREE_WET_BATH_DECISIONS_20261107.md).\n"
                       f"- Technical and owner holds: {HOLD[rid]} Original rows and source amounts unchanged. No owner acceptance.\n",encoding='utf-8')
    comp=base/'vendor_comparison.md'
    prev=comp.read_text(encoding='utf-8-sig').rstrip()
    other='B' if selected=='A' else 'A'
    csrc=(base/'board'/'round-036'/'candidates'/(other+'.md')).read_text(encoding='utf-8')
    ctable='| Surface |'+csrc.split('| Surface |',1)[1].split('**Floor/pan gate',1)[0].strip()
    comp.write_text(prev+f"\n\n## R036 CURRENT four-seat maker/gate/cost comparison — 2026-11-07\n\n"
                    f"**Selected:** {pick['selected_id']} ({selected}) score {pick['selected_score']:.3f}; "
                    f"material-only historical-gross rate ${RATES[rid][selected]}/copy. "
                    f"{pick['decision_summary']}. Only Elm, MSI, Porcelanosa, Floor & Decor eligible for new selections.\n\n"
                    f"Selected exact products and source-proven permissions/prices:\n\n{table}\n\n"
                    f"Alternate {other}: score {pick['other_score']:.3f}; "
                    f"${RATES[rid][other]}/copy, same historical gross basis:\n\n{ctable}\n\n"
                    f"**Hard product gates / field holds:** {HOLD[rid]} Product wet-wall YES does not release niche sill; "
                    f"conditional PAN is NULL when TUB/WALK-IN undecided; shower-floor YES plus DCOF>=0.42 independently required. "
                    f"F&D published rates are out-of-state public, not Chicago quote; no repeated material waste. "
                    f"Do not revive historic disallowed vendor picks.\n",encoding='utf-8')
    print(rid,'CHAMPION',pick['selected_id'],f"{pick['selected_score']:.3f}",pick['decision_summary'])
print('PASS authenticated R036 state, formal memo, additive current-room records and invariant preservation')

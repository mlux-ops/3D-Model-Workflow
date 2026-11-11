"""One-time guarded R038 authentic board integration. Never re-execute."""
from pathlib import Path
from decimal import Decimal
import json,subprocess,sys,re,copy
P=Path(__file__).resolve().parents[1]
OUT=P/'state/ROUND038_TWO_WET_BATH_DECISIONS.json'
MEMO=P/'state/ROUND038_TWO_WET_BATH_DECISIONS_20261107.md'
STATE=P/'state/ROOMS.json'
assert not OUT.exists() and not MEMO.exists(),'R038 already integrated'
a=json.loads(subprocess.run([sys.executable,'-B',str(P/'scratch/r038_original_critic_arithmetic.py')],capture_output=True,text=True,check=True).stdout)
assert (a['status'],a['criterion_count'],a['seat_means_count'],a['weighted_count'])==('PASS',76,16,4)
d=json.loads(STATE.read_text(encoding='utf8'))
R=d['rooms']
assert len(R)==13 and sum(x['unit_count'] for x in R)==26 and sum(len(x['carried_tile_rows']) for x in R)==27
assert sum(Decimal(str(x['carried_quote_material_subtotal_usd_per_unit']))*x['unit_count'] for x in R)==Decimal('23572.44')
assert all(x['owner_status']!='approved' for x in R)
orig={x['id']:(copy.deepcopy(x['carried_tile_rows']),x['unit_count'],x['owner_status'],x['carried_quote_material_subtotal_usd_per_unit'],x['carried_budget_material_only_usd_per_unit']) for x in R}
SEATS=('market','design','build','cost')
PROVENANCE={'market':'original isolated Codex eb487068-8083-4dd2-9d80-c22b5c34644a; both completed files before cancelled status','design':'isolated replacement Codex 50b71d75-35d4-4f5d-aa91-e869c6369592','build':'isolated Codex 6acb51e1-d2bd-4410-a082-b45e4c533f6d','cost':'isolated Codex f0cd5541-7e77-4082-babf-1c9edbf2436a'}
PRICES={'PH-BATH2':{'A':'789.22','B':'574.71'},'TX-BATH3':{'A':'685.92','B':'1071.52'}}
HOLDS={'PH-BATH2':'Owner-selected Duravit 59-inch TUB/Hansgrohe Matte White; NO tiled PAN or POINT drain. Niche horizontal sill, tub flange, waterproof assembly, field cuts, current Chicago matched lot/landed price and FILL IN budget unverified.','TX-BATH3':'TUB/WALK-IN UNSELECTED; Brizo BNX BT062415-BNX four-inch POINT only if WALK-IN. Original 42.5 SF bath LEVEL with waste once; extra WALK-IN PAN SF/cost NULL, never zero or included. Niche sill, drain/waterproof assembly, Chicago lot/landed price and FILL IN budget unverified.'}
result={}
memo=['# R038 authentic four-seat tile decision 2026-11-07','', 'Initial MARKET and DESIGN sessions stopped before scoring on historical owner-feedback exposure; excluded. Fresh isolated MARKET/DESIGN used role-neutral current owner directives. A redundant later MARKET assignment was canceled without writes. BUILD and COST genuine original independent reports preserved.','', 'Source-parsed **76** integer ratings, **16** HALF_UP means and **4** .30/.25/.25/.20 weighted totals.','', '| Room | A M/D/B/C | A weighted | B M/D/B/C | B weighted | Decision |','|---|---|---:|---|---:|---|']
for rid in ('PH-BATH2','TX-BATH3'):
    x=next(t for t in R if t['id']==rid)
    k=json.loads((P/'rooms'/rid/'board/round-038/_key.json').read_text(encoding='utf8'))
    assert k['round']==38 and k['room']==rid
    incumbent=k['previous_genuinely_product_board_qualified_provisional_incumbent']
    il=k['incumbent_neutral_letter'];cl=k['new_material_challenger_neutral_letter']
    assert x['champion_id']==incumbent and {il,cl}=={'A','B'}
    b=a['room_boards'][rid]
    for seat in SEATS:
        t=(P/'rooms'/rid/'board/round-038'/('critic-'+seat+'.md')).read_text(encoding='utf-8-sig')
        assert len(t)>2600 and '## Candidate A' in t and '## Candidate B' in t
        for letter in ('A','B'):
            section=t.split('## Candidate '+letter,1)[1].split('## Candidate ',1)[0]
            assert all(re.search(f,section,re.I) for f in ('top[_ ]fix','gate[_ ]flags','confidence'))
    for letter in ('A','B'):
        source=(P/'rooms'/rid/'board/round-038/candidates'/(letter+'.md')).read_text(encoding='utf8')
        assert 'DCOF >=0.42' in source and '15% waste ALREADY included ONCE' in source
        assert 'Wet Areas YES' in source or 'Shower Walls YES' in source
    assert b[il]['specialist_gate_pass'] and Decimal(b[il]['minimum_seat'])>=3
    delta=Decimal(b[cl]['weighted'])-Decimal(b[il]['weighted'])
    selected=cl if b[cl]['specialist_gate_pass'] and delta>=Decimal('.250') else il
    assert selected==il,'unexpected displacement: needs separate source adjudication'
    reason='Qualified incumbent defends; challenger delta '+str(delta)+' below +0.250'+(' and challenger minimum-seat FAIL' if not b[cl]['specialist_gate_pass'] else '')
    old_score=x['champion_score']
    x['champion_score']=float(b[selected]['weighted']);x['last_round']=38
    x['board_round_038']={'status':'authentic_four_seat_provisional','previous_id':incumbent,'previous_score':old_score,'selected_id':incumbent,'selected_letter_private_post_board':selected,'challenger_letter_private_post_board':cl,'weights':{'market':.3,'design':.25,'build':.25,'cost':.2},'original_criteria_cohort':76,'original_means_cohort':16,'original_weighted_cohort':4,'specialists':PROVENANCE,'challenger_delta':float(delta),'decision':reason,'scores':{letter:{'seat_means':{seat:float(b[letter][seat]['mean']) for seat in SEATS},'weighted':float(b[letter]['weighted']),'min_pass':b[letter]['specialist_gate_pass']} for letter in ('A','B')},'open':HOLDS[rid],'owner_approved':False}
    tag='R038 authentic decision: '+HOLDS[rid]
    if tag not in x['open_gaps']:x['open_gaps'].append(tag)
    result[rid]={'incumbent_id':incumbent,'incumbent_letter':il,'challenger_letter':cl,'selected_letter':selected,'selected_id':incumbent,'selected_score':float(b[selected]['weighted']),'other_score':float(b[cl]['weighted']),'changed':False,'four_seat_complete':True,'owner_approved':False,'challenger_delta':float(delta),'decision_summary':reason,'material_gross_rate_per_copy_usd':float(PRICES[rid][selected]),'technical_holds':HOLDS[rid],'scores':b}
    memo.append('| '+rid+' | '+' / '.join(b['A'][seat]['mean'] for seat in SEATS)+' | '+b['A']['weighted']+' | '+' / '.join(b['B'][seat]['mean'] for seat in SEATS)+' | '+b['B']['weighted']+' | '+reason+' |')
    src=(P/'rooms'/rid/'board/round-038/candidates'/(selected+'.md')).read_text(encoding='utf8')
    lines=src.splitlines();i=next(i for i,v in enumerate(lines) if v.startswith('| Actual surface |'))
    table='\n'.join(lines[i:i+5])
    memo += ['', '## '+rid+' '+incumbent+' '+b[selected]['weighted']+'/5',table,'Historical source gross area-rate $'+PRICES[rid][selected]+'/copy, 15% waste once, two physical copies. '+HOLDS[rid],'Not owner approved.']
    folder=P/'rooms'/rid
    cp=folder/'champion.md';old=cp.read_text(encoding='utf-8-sig')
    assert '# '+rid+' — R038' not in old
    cp.write_text('# '+rid+' — R038 CURRENT PROVISIONAL TILE CHAMPION (2026-11-07)\n\n**'+incumbent+'**, authentic R038 same-round '+b[selected]['weighted']+'/5; '+reason+'. Prior score '+str(old_score)+' retained below. No owner approval.\n\n'+table+'\n\nCost: $'+PRICES[rid][selected]+'/copy original gross area-rate, 15% waste included once, not Chicago landed. '+HOLDS[rid]+'\n\n---\n\n'+old,encoding='utf8')
    hp=folder/'history.md'
    hp.write_text(hp.read_text(encoding='utf-8-sig').rstrip()+'\n\n## R038 authentic four-seat board — 2026-11-07\n- Prior '+incumbent+' '+str(old_score)+'; same-round A '+b['A']['weighted']+', B '+b['B']['weighted']+'. '+reason+'.\n- Original independent 76/16/4; contaminated STOP attempts excluded. '+HOLDS[rid]+'\n',encoding='utf8')
    vp=folder/'vendor_comparison.md'
    vp.write_text(vp.read_text(encoding='utf-8-sig').rstrip()+'\n\n## R038 CURRENT allowed-vendor tile comparison — 2026-11-07\n- Selected '+incumbent+' '+b[selected]['weighted']+'/5, $'+PRICES[rid][selected]+'/copy; distinct alternative '+b[cl]['weighted']+'/5 and $'+PRICES[rid][cl]+'/copy. '+reason+'.\n'+table+'\n- Elm prices same-job 2026-09-04; Floor & Decor public retail from outside Chicago; physical order/lot and installed assembly not approved. '+HOLDS[rid]+'\n',encoding='utf8')
for x in R:
    assert (x['carried_tile_rows'],x['unit_count'],x['owner_status'],x['carried_quote_material_subtotal_usd_per_unit'],x['carried_budget_material_only_usd_per_unit'])==orig[x['id']]
assert sum(Decimal(str(x['carried_quote_material_subtotal_usd_per_unit']))*x['unit_count'] for x in R)==Decimal('23572.44')
assert sum(x['status']=='blocked' for x in R)==4 and all(x['owner_status']!='approved' for x in R)
assert next(x for x in R if x['id']=='TX-BATH4')['champion_id']=='round-035-B'
assert next(x for x in R if x['id']=='TX-BATH2')['champion_score']==3.2
assert next(x for x in R if x['id']=='TX-BATH4')['champion_score']==3.49
STATE.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
OUT.write_text(json.dumps({'round':38,'date':'2026-11-07','criterion_count':76,'seat_means_count':16,'weighted_count':4,'original_seats':PROVENANCE,'owner_approvals':0,'rooms':result},indent=2,ensure_ascii=False)+'\n',encoding='utf8')
MEMO.write_text('\n'.join(memo)+'\n',encoding='utf8')
print('PASS R038 76/16/4: PH2 incumbent 3.480 vs B3.440 retains; TX3 incumbent 3.400 vs B3.260 COST2.8 FAIL; invariants 13/26/27/23572.44/0.')

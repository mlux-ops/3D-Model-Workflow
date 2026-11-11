"""Guarded one-time R039 original strict-blind four-seat source integration."""
from pathlib import Path
from decimal import Decimal
import json, subprocess, sys, re, copy

P=Path(__file__).resolve().parents[1]
OUT=P/'state/ROUND039_TWO_DRY_POWDER_DECISIONS.json'
MEMO=P/'state/ROUND039_TWO_DRY_POWDER_DECISIONS_20261107.md'
STATE=P/'state/ROOMS.json'
assert not OUT.exists() and not MEMO.exists(), 'R039 already integrated; no rerun'
a=json.loads(subprocess.run([sys.executable,'-B',str(P/'scratch/r039_original_critic_arithmetic.py')],capture_output=True,text=True,check=True).stdout)
assert (a['status'],a['criterion_count'],a['seat_means_count'],a['weighted_count'])==('PASS',76,16,4)
d=json.loads(STATE.read_text(encoding='utf-8'))
R=d['rooms']
assert len(R)==13 and sum(r['unit_count'] for r in R)==26 and sum(len(r['carried_tile_rows']) for r in R)==27
assert sum(Decimal(str(r['carried_quote_material_subtotal_usd_per_unit']))*r['unit_count'] for r in R)==Decimal('23572.44')
assert all(r['owner_status']!='approved' for r in R)
orig={r['id']:(copy.deepcopy(r['carried_tile_rows']),r['unit_count'],r['owner_status'],r['carried_quote_material_subtotal_usd_per_unit'],r['carried_budget_material_only_usd_per_unit']) for r in R}
SEATS=('market','design','build','cost')
WORKERS={'market':'worker-84','design':'worker-88 strict-blind replacement','build':'worker-86','cost':'worker-87'}
PRICES={'TX-POWDER':{'A':'379.37','B':'95.08'},'TX-POWDER2':{'A':'332.10','B':'281.48'}}
HOLDS={
 'TX-POWDER':'DRY vanity WALL only, existing WOOD floor retained. Wall-mounted Hansgrohe faucet visible finish UNCONFIRMED, mirror/cuts/substrate unmeasured. Prior Haze incumbent COST2.8 <3.0 and Pienza challenger DESIGN2.8 <3.0; neither passes strict four-seat minimum. New materially distinct allowed-vendor WALL alternatives required. Chicago exact lot, landed pricing and owner budget FILL IN pending.',
 'TX-POWDER2':'DRY vanity WALL only, existing WOOD floor retained; Hansgrohe Tecturis E 73072341 deck-mounted Brushed Black Chrome; basin UNSELECTED. Manufacturer product-specific item and current exact matching lot, 6x6 relief edge/mirror/vanity setout, carton/Chicago landed pricing and budget FILL IN pending.'
}
decision={}
memo=['# R039 original strict-blind four-seat selection — 2026-11-07','','Four genuine original independent specialist seats: MARKET worker84; DESIGN clean worker88; BUILD worker86; COST worker87. Original DESIGN worker85 read extraneous PROJECT_MEMORY containing unrelated historical bath role cues; its original two files were preserved under scratch/r039_disqualified_design_ancillary_exposure and EXCLUDED before aggregation. No role-exposed rating counted.','', 'Source-parsed 76 individual INTEGER criteria, 16 HALF_UP seat means and four .30/.25/.25/.20 weighted scores; maker dry-wall and genuine owner-program gates applied.','', '| Room | A M/D/B/C | A weighted | B M/D/B/C | B weighted | Formal result |','|---|---|---:|---|---:|---|']
for rid in ('TX-POWDER','TX-POWDER2'):
 x=next(z for z in R if z['id']==rid)
 k=json.loads((P/'rooms'/rid/'board/round-039/_key.json').read_text(encoding='utf-8'))
 assert k['round']==39 and k['room']==rid and {k['incumbent_letter'],k['challenger_letter']}=={'A','B'}
 assert x['champion_id']==k['qualified_incumbent_id']
 il=k['incumbent_letter'];cl=k['challenger_letter'];b=a['room_boards'][rid]
 for seat in SEATS:
  t=(P/'rooms'/rid/'board/round-039'/('critic-'+seat+'.md')).read_text(encoding='utf-8-sig')
  assert len(t)>2100 and re.search('top[_ ]fix',t,re.I) and re.search('gate[_ ]flags',t,re.I) and re.search('confidence',t,re.I)
  assert re.search(r'(?mi)^## (?:Neutral\s+)?Candidate\s+A\b',t) and re.search(r'(?mi)^## (?:Neutral\s+)?Candidate\s+B\b',t)
 assert all((P/'rooms'/rid/'board/round-039/candidates'/(c+'.md')).is_file() for c in ('A','B'))
 assert all('WOOD' in (P/'rooms'/rid/'board/round-039/candidates'/(c+'.md')).read_text(encoding='utf-8') for c in ('A','B'))
 pa=bool(b[il]['specialist_gate_pass']);pb=bool(b[cl]['specialist_gate_pass'])
 delta=Decimal(b[cl]['weighted'])-Decimal(b[il]['weighted'])
 if rid=='TX-POWDER':
  assert not pa and not pb and b['A']['cost']['mean']=='2.8' and b['B']['design']['mean']=='2.8'
  selected=None;reason='NO gate-qualified candidate: incumbent A COST2.8 FAIL, challenger B DESIGN2.8 FAIL; prior incumbent demoted, room BLOCKED pending fresh allowed-vendor board.'
  x['status']='blocked';x['champion_id']=None;x['champion_score']=None
 else:
  assert pa and pb and delta==Decimal('0.080')
  selected=il;reason='Both A/B pass specialist and product dry WALL gates; B +0.080 below qualified A incumbent displacement +0.250. Retain Indigo Edge.'
  x['champion_score']=float(b[selected]['weighted'])
  x['status']='provisional'
 x['last_round']=39
 record={'status':'authentic_four_seat_strict_blind_provisional','previous_id':k['qualified_incumbent_id'],'previous_score':3.640 if rid=='TX-POWDER' else 3.780,'selected_letter_private_post_board':selected,'selected_id':x['champion_id'],'challenger_delta':float(delta),'original_criteria_cohort':76,'original_means_cohort':16,'original_weighted_cohort':4,'specialists':WORKERS,'excluded_design':'worker-85 ancillary PROJECT_MEMORY exposure; archive only, not scored','scores':{letter:{'seat_means':{s:float(b[letter][s]['mean']) for s in SEATS},'weighted':float(b[letter]['weighted']),'minimum_seat':float(b[letter]['minimum_seat']),'specialist_gate_pass':bool(b[letter]['specialist_gate_pass'])} for letter in ('A','B')},'decision':reason,'open':HOLDS[rid],'owner_approved':False}
 x['board_round_039']=record
 tag='R039 original strict-blind decision: '+HOLDS[rid]
 if tag not in x['open_gaps']:x['open_gaps'].append(tag)
 decision[rid]={'previous_id':k['qualified_incumbent_id'],'incumbent_letter':il,'challenger_letter':cl,'selected_letter':selected,'selected_id':x['champion_id'],'selected_score':None if selected is None else float(b[selected]['weighted']),'other_score':float(b[cl]['weighted']) if selected else None,'changed':selected is None,'four_seat_complete':True,'owner_approved':False,'challenger_delta':float(delta),'decision_summary':reason,'material_gross_rate_per_copy_usd':None if selected is None else float(PRICES[rid][selected]),'technical_holds':HOLDS[rid],'scores':b}
 memo.append('| '+rid+' | '+' / '.join(b['A'][s]['mean'] for s in SEATS)+' | '+b['A']['weighted']+' | '+' / '.join(b['B'][s]['mean'] for s in SEATS)+' | '+b['B']['weighted']+' | '+reason+' |')
 memo += ['', '## '+rid,reason,'Original 15% waste counted once, two physical copies; DRY vanity WALL only, WOOD floor retained. '+HOLDS[rid]]
 if selected:
  src=(P/'rooms'/rid/'board/round-039/candidates'/(selected+'.md')).read_text(encoding='utf-8')
  memo += ['Selected source WALL: '+next(z for z in src.splitlines() if z.startswith('| ONE DRY vanity WALL only |')),'Rate-only gross SF $'+PRICES[rid][selected]+'/copy; not an order or Chicago landed value.']
 else:
  memo += ['Historic Haze is NOT currently a qualified champion. Candidate A/B source WALLs remain compared but neither is selected; replacement tile must clear all four specialist thresholds.']
 memo += ['Zero owner approvals; neither packet nor any material released.']
 folder=P/'rooms'/rid
 cp=folder/'champion.md';old=cp.read_text(encoding='utf-8-sig')
 assert '# '+rid+' — R039' not in old
 cp.write_text('# '+rid+' — R039 '+('BLOCKED, NO TILE CHAMPION' if selected is None else 'CURRENT PROVISIONAL TILE CHAMPION')+' (2026-11-07)\n\n'+reason+'\n\n'+HOLDS[rid]+'\n\n---\n\n'+old,encoding='utf-8')
 hp=folder/'history.md'
 hp.write_text(hp.read_text(encoding='utf-8-sig').rstrip()+'\n\n## R039 original four-seat board — 2026-11-07\n- '+reason+'\n- Strict-blind original 76/16/4; worker85 disqualified for ancillary read, independent worker88 clean original replacement. '+HOLDS[rid]+'\n',encoding='utf-8')
 vp=folder/'vendor_comparison.md'
 vp.write_text(vp.read_text(encoding='utf-8-sig').rstrip()+'\n\n## R039 current allowed-vendor DRY powder wall comparison — 2026-11-07\n- A '+b['A']['weighted']+'/5, original rate-only $'+PRICES[rid]['A']+'/copy; B '+b['B']['weighted']+'/5, original rate-only $'+PRICES[rid]['B']+'/copy. '+reason+'\n- Elm 2026-09-04 same-job quote vs F&D public Kirkwood GA retail where relevant; existing wood floor, no wet PAN/LEVEL, no additional waste. Third distinct family options referenced in neutral packets. '+HOLDS[rid]+'\n',encoding='utf-8')
for z in R:
 assert (z['carried_tile_rows'],z['unit_count'],z['owner_status'],z['carried_quote_material_subtotal_usd_per_unit'],z['carried_budget_material_only_usd_per_unit'])==orig[z['id']]
assert sum(Decimal(str(z['carried_quote_material_subtotal_usd_per_unit']))*z['unit_count'] for z in R)==Decimal('23572.44')
assert sum(z['status']=='blocked' for z in R)==5 and all(z['owner_status']!='approved' for z in R)
assert next(z for z in R if z['id']=='TX-BATH4')['champion_id']=='round-035-B'
assert next(z for z in R if z['id']=='TX-BATH2')['champion_score']==3.2
assert next(z for z in R if z['id']=='TX-BATH4')['champion_score']==3.49
STATE.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
OUT.write_text(json.dumps({'round':39,'date':'2026-11-07','criterion_count':76,'seat_means_count':16,'weighted_count':4,'original_seats':WORKERS,'excluded_original_design':'worker-85 — archived, not counted','owner_approvals':0,'rooms':decision},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
MEMO.write_text('\n'.join(memo)+'\n',encoding='utf-8')
print('PASS R039 76/16/4: TX-POWDER A3.410 COST2.8 FAIL, B2.950 DESIGN2.8 FAIL, BLOCKED; TX-POWDER2 Indigo A3.660 defended vs B3.740 delta+0.080; 13/26/27/23572.44/0.')

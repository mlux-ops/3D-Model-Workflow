"""Round013 formal scoring in NEXT DISTINCT user/prime turn, with frozen source audit.

One-time creates state/ROUND013_SCORING.json. Never changes original R013
neutral candidates, authentic independent critiques, private keys, or
source/dispatch/collection receipts whose all_critic_scores MUST remain null.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import re

R = Path(__file__).resolve().parents[1]
srcp = R/'state/ROUND013_SUBMISSION.json'
disp = R/'state/ROUND013_CRITIC_DISPATCH.json'
colp = R/'state/ROUND013_CRITIC_COLLECTION.json'
reviewp = R/'state/ROUND013_COLLECTION_REVIEWER_CLEARANCE.json'
out = R/'state/ROUND013_SCORING.json'
assert not out.exists(), 'Original R013 distinct-turn scoring receipt already exists; no overwrite.'

def fingerprint(p):
    b = p.read_bytes()
    return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}

source = json.loads(srcp.read_text(encoding='utf-8'))
dispatch = json.loads(disp.read_text(encoding='utf-8'))
collection = json.loads(colp.read_text(encoding='utf-8'))
clearance = json.loads(reviewp.read_text(encoding='utf-8'))
assert source['round']==dispatch['round']==collection['round']==clearance['round']==13
assert source['all_critic_scores'] is None and source['weighted_scoring'] is None
assert dispatch['all_critic_scores'] is None and collection['all_critic_scores'] is None
assert collection['weighted_scoring'] is None and clearance['all_critic_scores'] is None
assert clearance['weighted_scores'] is None and clearance['global_program_done'] is False
assert clearance['standing_reviewer']=='worker-14' and clearance['scoring_genuinely_next_distinct_prime_turn_only']
assert clearance['verdict'].startswith('CONTINUE') and clearance['scoring_genuinely_next_distinct_prime_turn_only']
assert fingerprint(srcp)['sha256']==clearance['source_submission_sha256']==dispatch['source_submission_sha256']==collection['source_submission_sha256']
assert fingerprint(disp)['sha256']==clearance['critic_dispatch_sha256']==collection['dispatch_receipt_sha256']
assert fingerprint(colp)['sha256']==clearance['original_critic_collection_sha256']
assert fingerprint(R/'deliverables/integrated-r14/MANIFEST.json')['sha256']==clearance['r14_corrected_manifest_sha256']
assert collection['total_critic_files']==12 and collection['distinct_seats']==4
assert collection['individual_criteria']==114 and collection['independent_unweighted_arithmetic_means']==24
assert collection['local_links']==333

seats={'market':(Decimal('0.30'),4),
       'design':(Decimal('0.25'),5),
       'build':(Decimal('0.25'),5),
       'cost':(Decimal('0.20'),5)}
assert set(dispatch['critic_worker_seats'])=={'critic-'+s for s in seats}
assert len(set(dispatch['critic_worker_seats'].values()))==4

expected={'PH-PRIMARY':('A','B'),'PH-BATH2':('C','B'),'PH-BATH4':('C','A')}
assert set(expected)==set(source['candidate_files'])==set(collection['report_files'])
room_status={r['id']:r for r in json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
for rid in expected:
    r=room_status[rid]
    assert r['status']=='blocked' and r['owner_status'] is None
    assert r['last_round']==13 and r['champion_id'] is None and r['champion_score'] is None
    assert r['board_round_013']['status']=='pending_blind_four_seat_critic_reports_unscored'
    assert r['board_round_013']['all_critic_scores'] is None

gates={
 'PH-PRIMARY':{
  'A':[
   'FAIL WET WALL/CEILING: exact ELM Cortar Bone Reed 24x48 relief has no individual Wet Areas listing; flat Cortar Bone wet listing is NOT transferable.',
   'FAIL LEVEL: original Cortar Bone Soft 24x48 bath and PH WC floor exact individual SKU/finish raw numerical measured wet DCOF certificate absent.',
   'FAIL LINEAR PAN: original Cortar Bone Anti-Slip 12x24 sloped pan exact individual raw measured wet DCOF and approved 48-in linear-drain slope/format absent.',
   'HOLD: selected Brizo Black Onyx BT0734816-BNX 48-in LINEAR + mandatory BR73480 rough needs actual liner/membrane/grate/curb/flood-test assembly; no Primary niche.',
  ],
  'B':[
   'PASS WET WALL LISTING ONLY: individual ELM Cortar Bone flat Soft 24x48 maker Wet Areas yes; 111-in wet ceiling fastening still needs qualified installation system.',
   'FAIL LEVEL: proposed Daltile Prime RL21 Dynamic Beige 12x24 Matte USA 3/8-in for LEVEL bath and shared PH WC has maker Target wet DCOF >=0.42, NOT exact raw measured numerical laboratory test.',
   'FAIL LINEAR PAN: distinct RL21 1.5-in Hex Matte Mexico 5/16-in linear-shower mosaic has maker application Target only, no exact raw measured numerical wet DCOF test.',
   'HOLD: Brizo BT0734816-BNX factory solid grate bypasses decorative tile-in insert chip-thickness tolerance ONLY; BR73480 rough/membrane/pan slope and flood-tested assembly remain unapproved; older 1/4-in vs current 5/16-in mosaic nominal conflicting, not proven incompatibility.',
   'HOLD: source packet 1/8-in RL21 grout study vs manufacturer page 3/16-in variant requires exact product-revision/physical joint approval.',
  ]},
 'PH-BATH2':{
  'C':[
   'PASS WET TUB WALL AND NICHE: individual ELM Tones Sapphire 2x20 Glossy and Tones Sandstone 2x20 wet application listings both confirmed; no tiled shower PAN exists.',
   'FAIL LEVEL: original ELM Cortar Grey Soft 12x24 bath floor has no exact SKU/finish raw numerical measured wet DCOF certificate; no PAN floor test is applicable.',
   'HOLD: drawing W1 59.496-in vs selected Duravit 700332000000090 nominal 59-in tub leaves only 0.496-in TOTAL nominal difference before rough, flange, waterproof backer, tile and tolerances; fit neither proven nor disproven.',
  ],
  'B':[
   'PASS WET TUB WALL AND NICHE: individual ELM Tones Sapphire 2x20 Glossy and Sandstone 2x20 listings; selected Duravit 700332000000090 TUB and Hansgrohe MATTE WHITE, NO tiled PAN.',
   'FAIL LEVEL: proposed Daltile Prime Dynamic Beige RL21 12x24 Matte bath LEVEL uses maker Target >=0.42, not individual exact raw numerical measured wet DCOF laboratory result; PAN N/A.',
   'HOLD: drawing W1 59.496-in vs nominal 59-in Duravit tub gives only 0.496-in total before backer, finish, flange and rough clearances. Exact manufacturer tub envelope, waterproof flange and correct 1529 rough opening mandatory.',
   'HOLD: RL21 maker grout 1/8 vs 3/16 conflicting page snapshots and actual shade/lot/caliber/installed quote require manufacturer/GC verification.',
  ]},
 'PH-BATH4':{
  'C':[
   'FAIL WET WALL: full 107.2-SF/unit Cortar Bone Ribbed 24x48 Relief has no individual maker Wet Areas listing; flat Bone permission cannot transfer.',
   'FAIL WET NICHE: original Clara Tierra Madre Caviar 2x8 individually Wet Areas unlisted, even though other finishes may be listed.',
   'FAIL LEVEL: original Cortar Charcoal Soft 12x24 LEVEL exact individual raw wet numerical measured DCOF unavailable; source Soft vs handoff Anti-Slip finish conflicting.',
   'FAIL SQUARE POINT PAN: original Charcoal Soft/Anti-Slip sloped walk-in POINT PAN exact format, maker listing, numerical raw measured wet DCOF and 4-plane suitable drain assembly unavailable.',
   'HOLD: selected Brizo Black Onyx BT062415-BNX 4-in SQUARE POINT on actual WALK-IN shower, NOT a tub, requiring measured rough/membrane/four-plane slope/flood section.',
  ],
  'A':[
   'PASS WET WALL/NICHE ONLY: ELM flat Cortar Bone Soft 24x48 is individually Wet Areas listed; independently listed Soho Black 2x10 Glossy wet niche. Not permission for Ribbed Bone or Clara Caviar.',
   'FAIL LEVEL: proposed Prime RL21 Dynamic Beige 12x24 Matte LEVEL maker Target wet DCOF >=0.42 is NOT the exact raw numerical measured SKU test.',
   'FAIL POINT PAN: distinct Prime RL21 1.5-in Hex Matte shower POINT PAN Target only, not exact raw measured wet DCOF; actual maker-approved four-plane Brizo square point install/waterproof detail missing.',
   'HOLD: selected actual 4-in SQUARE POINT Brizo BT062415-BNX Black Onyx WALK-IN; owner 35-SF vs old 27-SF area, source Soft/Anti-Slip and combined 40.2 gross level/pan source must be reconciled, no tub.',
   'HOLD: original 107.2-SF/unit full Ribbed itemization potentially absent from old supplier grand total (214.4 SF across two copies) is vendor reconciliation only, NOT payable shortage or approved credit.',
  ]},
}
shared=[
 'HOLD: correct live native 1529 Revit project not verified (open native 1527); drawing sizes/openings/valve/threshold/niche/floor-pan boundaries are provisional.',
 'HOLD: exact SKU/carton yield, project quantity, current Chicago available dye lot/ETA, installed supplier bid and signed owner per-room cost cap missing; do not invent budget 125% gate FAIL.',
 'HOLD: source quote gross already includes 15% waste ONCE, two copies; no duplicate WC, field+niche faces, split LEVEL/PAN gross, samples or trim order.',
 'HOLD: owner has NOT signed final 1:1 tile/grout/fixture selections or procurement authorization; material and GC release FALSE.',
]

result={
 'round':13,'as_of':'2026-11-06',
 'scoring_turn':'2026-11-06 NEW DISTINCT user/prime continuation after source-only 19:04 UTC R013 submission turn',
 'source_submission':'state/ROUND013_SUBMISSION.json',
 'source_submission_sha256':fingerprint(srcp)['sha256'],
 'source_dispatch_sha256':fingerprint(disp)['sha256'],
 'source_collection_sha256':fingerprint(colp)['sha256'],
 'reviewer_clearance_receipt_sha256':fingerprint(reviewp)['sha256'],
 'independent_reviewer':'worker-14 (successor to permanently exhausted worker-11); read-only CONTINUE on R013 collection and R14 FIX',
 'rubric_weights':{k:float(v[0]) for k,v in seats.items()},
 'verification':{'frozen_candidates':0,'original_critics':0,'criteria':0,'recalculated_seat_means':0,'local_links':0,'valid':False},
 'room_results':{},
 'owner_approval':False,'procurement_release':False,'global_program_done':False,
}

for rid,(historical,revised) in expected.items():
    p=R/'rooms'/rid/'board/round-013'
    letters=source['candidate_files'][rid]
    assert set(letters)=={historical,revised}
    role_keys=json.loads((p/'_key.json').read_text(encoding='utf-8'))
    assert set(role_keys)==set(letters)
    assert 'historic' in role_keys[historical].lower() and 'revised' in role_keys[revised].lower(),(rid,role_keys)
    for letter,item in letters.items():
        assert fingerprint(p/'candidates'/f'{letter}.md')==item
        result['verification']['frozen_candidates']+=1
    scores={k:{} for k in letters}
    criteria={k:{} for k in letters}
    report_hashes={}
    for seat, (weight, required) in seats.items():
        path=p/f'critic-{seat}.md'
        exact=fingerprint(path)
        proof=collection['report_files'][rid]['critic-'+seat]
        assert exact['sha256']==proof['sha256'] and exact['bytes']==proof['bytes']
        assert proof['worker_id']==dispatch['critic_worker_seats']['critic-'+seat]
        assert set(proof['candidate_letters'])==set(letters)
        report_hashes[seat]={'file':str(path.relative_to(R)).replace('\\','/'),
                             'worker':proof['worker_id'],**exact}
        text=path.read_text(encoding='utf-8')
        assert not re.search(r'(?i)_key\.json|state/ROOMS\.json|state/LEDGER\.md',text)
        result['verification']['original_critics']+=1
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if target.startswith(('http://','https://','#','mailto:')): continue
            assert (p/target.split('#')[0]).resolve().is_file(),(rid,seat,target)
            result['verification']['local_links']+=1
        sections=re.split(r'(?im)^##\s+(?:Neutral\s+)?Candidate\s+([A-Z])\b[^\n]*\n',text)
        assert len(sections)==5 and set(sections[1::2])==set(letters),(rid,seat)
        for letter,block in zip(sections[1::2],sections[2::2]):
            vals=[]
            for line in block.splitlines():
                if not line.startswith('|'):continue
                parts=[x.strip() for x in line.strip('|').split('|')]
                if len(parts)!=3:continue
                v=re.sub(r'\s*/\s*5(?:\.0)?\s*$','',parts[1].replace('**','')).strip()
                if re.fullmatch(r'[1-5](?:\.\d+)?',v):
                    assert len(parts[2])>=30 and '[' in parts[2],(rid,letter,seat,'uncited criterion')
                    vals.append(Decimal(v))
            assert len(vals)==required,(rid,letter,seat,len(vals),required)
            mean=(sum(vals,Decimal('0'))/Decimal(required)).quantize(Decimal('.1'),rounding=ROUND_HALF_UP)
            # Confirm each worker's own reported arithmetic number, not merely recalculated value.
            printed=re.search(r'(?im)^\*\*(?:Arithmetic\s+(?:seat\s+)?mean):\*\*[^\n]*?=\s*\*\*([1-5]\.\d)\s*/\s*5(?:\.0)?\*\*',block)
            assert printed and Decimal(printed.group(1))==mean,(rid,letter,seat,'reported mean mismatch',mean)
            assert all(k in block.lower() for k in ('top_fix','gate_flags','confidence'))
            scores[letter][seat]=float(mean)
            criteria[letter][seat]={'criterion_scores':[float(z) for z in vals],'arithmetic_mean':float(mean)}
            result['verification']['criteria']+=required
            result['verification']['recalculated_seat_means']+=1
    r={'room':rid,'round':13,'historical_letter':historical,'revised_letter':revised,
       'critic_file_fingerprints':report_hashes,'candidates':{},
       'status':'blocked','champion_id':None,'champion_score':None,
       'accepted_challenger':False,'owner_approved':False,'procurement_release':False,
       'source_selection_preserved':True,
       'previous_scored_round':10,'previous_scored_status':'blocked'}
    for letter in sorted(letters):
        x=scores[letter]
        mean=sum(Decimal(str(x[s]))*seats[s][0] for s in seats).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
        reason=gates[rid][letter]+shared
        assert any('FAIL LEVEL' in x for x in reason)
        if rid!='PH-BATH2':
            assert any('FAIL LINEAR PAN' in x or 'FAIL POINT PAN' in x or 'FAIL SQUARE POINT PAN' in x for x in reason)
        else:
            assert any('NO tiled PAN' in x or 'no tiled shower PAN' in x for x in reason)
        r['candidates'][letter]={
            'role':role_keys[letter],
            'individual_critic_scores':x,
            'individual_criterion_scores':criteria[letter],
            'weighted_score':float(mean),
            'minimum_critic_score':min(x.values()),
            'all_critics_at_least_3':min(x.values())>=3.0,
            'all_hard_gates_pass':False,
            'gate_reasons':reason,
            'frozen_candidate_sha256':letters[letter]['sha256'],
        }
    old=r['candidates'][historical]
    new=r['candidates'][revised]
    margin=(Decimal(str(new['weighted_score']))-Decimal(str(old['weighted_score']))).quantize(Decimal('.01'))
    r['challenger_margin']=float(margin)
    r['challenger_margin_at_least_025']=margin>=Decimal('.25')
    r['challenger_acceptance_pass']=False
    r['gate_qualified_champion']=None
    r['conditional_visual_direction']=revised if margin>0 else historical
    r['decision']='BLOCKED: no fully wet-tested or installation/owner/cost-gate qualified source or revised champion. Revised visual/sample study remains conditional only.'
    assert new['minimum_critic_score']<3 and not new['all_hard_gates_pass']
    result['room_results'][rid]=r

assert result['verification']=={
 'frozen_candidates':6,
 'original_critics':12,
 'criteria':114,
 'recalculated_seat_means':24,
 'local_links':333,
 'valid':False,
}
result['verification']['valid']=True
out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
for rid,row in result['room_results'].items():
    a=row['candidates'][row['historical_letter']]
    b=row['candidates'][row['revised_letter']]
    print(rid,'historic',a['weighted_score'],'revised',b['weighted_score'],
          'margin',row['challenger_margin'],'revised_min',b['minimum_critic_score'],'BLOCKED')
print('PASS exact 6 frozen candidate SHA, 12 real report SHA, 114 values, 24 printed unweighted means, 333 local citations; board weighted in distinct turn; all 3 BLOCKED')

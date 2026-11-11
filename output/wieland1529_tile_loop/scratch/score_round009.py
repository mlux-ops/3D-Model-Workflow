from pathlib import Path
import json,re,hashlib,decimal
ROOT=Path(__file__).resolve().parents[1]
ROOMS=('TX-PRIMARY','TX-BATH2','TX-BATH4')
SEATS={'market':(.30,4),'design':(.25,5),'build':(.25,5),'cost':(.20,5)}
submission=json.loads((ROOT/'state/ROUND009_SUBMISSION.json').read_text(encoding='utf-8'))
assert submission['round']==9 and submission['phase']=='2-board' and submission['all_critic_scores'] is None
assert set(submission['candidate_files'])==set(ROOMS)
result={'as_of':'2026-11-06','round':9,'source_submission':'state/ROUND009_SUBMISSION.json','source_submission_sha256':hashlib.sha256((ROOT/'state/ROUND009_SUBMISSION.json').read_bytes()).hexdigest(),'verification':{'candidate_frozen_files':6,'actual_independent_critiques':12,'criterion_checks':0,'local_links':0,'all_valid':False},'room_results':{}}
def one_decimal_mean(vals):
    return float((decimal.Decimal(str(sum(vals)))/decimal.Decimal(len(vals))).quantize(decimal.Decimal('0.1'),rounding=decimal.ROUND_HALF_UP))
def parse_score(block,seat,rid,letter):
    patterns=[
        r'(?im)^\*\*overall\s+seat\s+mean:\s*([1-5](?:\.\d)?)\s*/\s*5\.0\*\*',
        r'(?im)^\*\*overall_score:\s*([1-5](?:\.\d)?)\s*/\s*5\.0\*\*',
        r'(?im)^\*\*seat_score:\s*([1-5](?:\.\d)?)\s*/\s*5\.0\*\*',
        r'(?im)^\*\*Overall(?:\s+build)?\s+seat\s+mean:\*\*\s*.*?=\s*([1-5](?:\.\d)?)\s*/\s*5\.0'
    ]
    matches=[float(m.group(1)) for pat in patterns for m in re.finditer(pat,block)]
    assert len(matches)==1,(rid,seat,letter,'overall seat score parse',matches)
    return matches[0]
for rid in ROOMS:
    roomdir=ROOT/'rooms'/rid/'board/round-009'
    original=submission['candidate_files'][rid]
    assert len(original)==2
    role_mapping=json.loads((roomdir/'_key.json').read_text(encoding='utf-8'))
    assert set(role_mapping)==set(original)
    hist=next(letter for letter,role in role_mapping.items() if 'historic' in role)
    revised=next(letter for letter in role_mapping if letter!=hist)
    for letter,rec in original.items():
        actual=(roomdir/'candidates'/(letter+'.md')).read_bytes()
        assert len(actual)==rec['bytes'] and hashlib.sha256(actual).hexdigest()==rec['sha256'],(rid,letter,'candidate SHA mismatch')
    crit_hashes={}
    crit_scores={l:{} for l in original}
    crit_evidence={}
    for seat,(weight,n) in SEATS.items():
        f=roomdir/('critic-'+seat+'.md')
        assert f.is_file(),(rid,seat,'critic missing')
        raw=f.read_bytes();t=raw.decode('utf-8')
        assert len(raw)>2000 and all(tag in t.lower() for tag in ('top_fix','gate_flags','confidence','dcof')),(rid,seat,'report not complete')
        assert not re.search(r'(?i)_key\.json|state/ROOMS\.json|state/LEDGER\.md|room[s]?/[^ \n]*history\.md|room[s]?/[^ \n]*champion\.md|round.?00[1-8]',t),(rid,seat,'blind/historical leak')
        assert not re.search(r'(?i)\bsteam\b',t),(rid,seat,'owner-excluded topic')
        chunks=re.split(r'(?im)^##\s+Candidate\s+([A-Z])\b[^\n]*\n',t)
        assert len(chunks)==5,(rid,seat,len(chunks))
        assert set(chunks[1::2])==set(original),(rid,seat,chunks[1::2])
        crit_hashes[seat]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
        for letter,block in zip(chunks[1::2],chunks[2::2]):
            table=[]
            for line in block.splitlines():
                if not line.startswith('|'): continue
                cells=[x.strip() for x in line.strip('|').split('|')]
                if len(cells)!=3:continue
                sc=re.sub(r'\*','',cells[1]).strip()
                sc=re.sub(r'\s*/\s*5\s*$','',sc).strip()
                if re.fullmatch(r'[1-5](?:\.\d+)?',sc):
                    table.append((float(sc),cells[2]))
            assert len(table)==n,(rid,seat,letter,'criterion count',len(table),table)
            assert all(len(ev)>35 and ('[' in ev or 'http' in ev or 'OT0' in ev or 'source' in ev.lower()) for _,ev in table),(rid,seat,letter,'missing row evidence')
            scores=[v for v,_ in table]
            actual_score=one_decimal_mean(scores)
            reported=parse_score(block,seat,rid,letter)
            assert reported==actual_score,(rid,seat,letter,'score arithmetic',reported,actual_score,scores)
            assert len(re.findall(r'(?i)\btop_fix\s*:',block))==1 and len(re.findall(r'(?i)\bgate_flags\s*:',block))==1,(rid,seat,letter,'gate/fix count')
            assert 'FAIL' in block and 'confidence' in block.lower(),(rid,seat,letter,'hard gate statement')
            for link in re.findall(r'\]\(([^)]+)\)',block):
                if link.startswith(('https://','http://','#','mailto:')):continue
                target=(f.parent/link.split('#')[0])
                assert target.exists(),(rid,seat,letter,'missing local citation',link)
                result['verification']['local_links']+=1
            crit_scores[letter][seat]=reported
            crit_evidence.setdefault(letter,{})[seat]={'criterion_scores':scores,'mean':reported}
            result['verification']['criterion_checks']+=n
    rr={'room':rid,'round':9,'critics_complete':True,'critic_file_fingerprints':crit_hashes,'weights':{seat:weight for seat,(weight,_) in SEATS.items()},'incumbent_letter':hist,'challenger_letter':revised,'candidates':{}}
    for letter in sorted(original):
        ss=crit_scores[letter]
        weighted=round(sum(ss[s]*SEATS[s][0] for s in SEATS)+1e-9,2)
        fails=['FAIL: exact measured product-specific bath level-floor wet DCOF unavailable for selected source/alternative SKU']
        if rid=='TX-PRIMARY':
            fails+=['FAIL: selected 48-in Brizo linear shower pan exact measured SKU wet DCOF unavailable',
                    'HOLD: actual RL21 Prime mosaic order SKU, liner/slope/48-in linear drain connection, 1529 geometry and manufacturer brochure version reconciliation unavailable']
            if letter==hist:fails+=['FAIL: Cortar Clay Ribbed relief individual Wet Areas approval absent']
        if rid=='TX-BATH2':
            fails+=['HOLD: actual niche face netting, unselected owner basin, 1529 tub/finish geometry and supplier availability unknown']
        if rid=='TX-BATH4':
            fails+=['HOLD: actual tub niche returns/sill and measured floor/transition geometry unavailable']
            if letter==hist:fails+=['FAIL: Cortar Bone Ribbed and Clara Caviar niche exact Wet Areas listings absent']
        fails+=['HOLD: current landed Chicago pricing/lot/lead and owner room budget/signoff unavailable; cannot infer >125% gate failure']
        rr['candidates'][letter]={'role':role_mapping[letter],'seat_scores':ss,'criterion_scores':crit_evidence[letter],'weighted_score':weighted,'minimum_critic_score':min(ss.values()),'all_seat_minimum_3_pass':min(ss.values())>=3.0,'hard_gates_pass':False,'gate_reasons':fails,'source_candidate_sha256':original[letter]['sha256']}
    old=rr['candidates'][hist];new=rr['candidates'][revised]
    rr['margin']=round(new['weighted_score']-old['weighted_score'],2)
    rr.update(status='blocked',decision='retain_no_qualified_candidate_due_exact_wet_floor_test_holds',champion_id=None,champion_score=None,accepted_challenger=False,owner_approved=False,provisional_design_preference=revised if rr['margin']>0 else hist,report='board/round-009/ROUND_REPORT.md')
    result['room_results'][rid]=rr
result['verification']['all_valid']=True
dest=ROOT/'state/ROUND009_SCORING.json'
assert not dest.exists(),'Existing Round009 scoring file exists; inspect before ever replacing'
dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
for rid,rr in result['room_results'].items():
    a,b=rr['incumbent_letter'],rr['challenger_letter']
    print(rid,'hist',a,rr['candidates'][a]['weighted_score'],'revised',b,rr['candidates'][b]['weighted_score'],'delta',rr['margin'],'min_revised',rr['candidates'][b]['minimum_critic_score'],'BLOCKED')
print('PASS 12 authentic SHA critics, six immutable frozen candidate SHA,',result['verification']['criterion_checks'],'independent rubric scores,',result['verification']['local_links'],'resolved local links; scorer wrote state/ROUND009_SCORING.json')

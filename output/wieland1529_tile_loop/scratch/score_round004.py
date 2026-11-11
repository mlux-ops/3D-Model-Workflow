from pathlib import Path
import json,re,hashlib,statistics,decimal,datetime
ROOT=Path(__file__).resolve().parents[1]
ROOMS=['PH-PRIMARY','PH-BATH2','PH-BATH3','PH-BATH4']
SEATS={'market':(.30,4),'design':(.25,5),'build':(.25,5),'cost':(.20,5)}
manifest=json.loads((ROOT/'state/ROUND004_SUBMISSION.json').read_text(encoding='utf-8'))
assert manifest['all_critic_scores'] is None and manifest['phase']=='2-board'
assert set(manifest['candidate_files'])==set(ROOMS)
out={'as_of':'2026-11-06','source_submission':'state/ROUND004_SUBMISSION.json','round':4,'verification':{'candidate_immutable_files':8,'independent_critique_files':16,'criterion_checks':0,'source_links_count':0,'all_16_valid':False},'room_results':{}}
def half_up(x):
    return float(decimal.Decimal(str(x)).quantize(decimal.Decimal('.1'),rounding=decimal.ROUND_HALF_UP))
for rid in ROOMS:
    rd=ROOT/'rooms'/rid/'board/round-004'
    candidates=manifest['candidate_files'][rid]
    key=json.loads((rd/'_key.json').read_text(encoding='utf-8'))
    actual_letters=set(candidates)
    assert len(actual_letters)==2
    hist=next(k for k in actual_letters if 'historic' in key[k].lower())
    chal=next(k for k in actual_letters if k!=hist)
    for letter,receipt in candidates.items():
        b=(rd/'candidates'/f'{letter}.md').read_bytes()
        assert len(b)==receipt['bytes'] and hashlib.sha256(b).hexdigest()==receipt['sha256'],(rid,letter)
    scores={k:{} for k in actual_letters}
    critique_hashes={}
    for seat,(weight,ncrit) in SEATS.items():
        f=rd/f'critic-{seat}.md'; blob=f.read_bytes(); content=blob.decode('utf-8')
        assert len(blob)>1000 and 'top_fix' in content.lower() and 'gate_flags' in content.lower() and 'confidence' in content.lower(),str(f)
        assert not re.search(r'(?i)_key\.json|round.?00[123]|state/ROOMS\.json|state/LEDGER\.md|historic\s+v4\s+source\s+\b[A-C]\b',content),f
        chunks=re.split(r'(?im)^##\s+Candidate\s+([A-C])\s+[^\n]*\n',content)
        assert len(chunks)==5, (rid,seat,'chunks',len(chunks))
        assert set(chunks[1::2])==actual_letters,(rid,seat,chunks[1::2])
        critique_hashes[seat]={'sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob)}
        for letter,block in zip(chunks[1::2],chunks[2::2]):
            lines=block.splitlines()
            table=[x for x in lines if x.startswith('|') and not re.match(r'^\|\s*:?-{2,}',x)]
            criterion=[]
            for row in table:
                cells=[x.strip() for x in row.strip('|').split('|')]
                if len(cells)<3 or 'score' in cells[1].lower() or 'criterion' in cells[0].lower(): continue
                m=re.search(r'(?<!\d)([1-5](?:\.\d+)?)(?:\s*/\s*5)?(?!\d)',re.sub(r'\*','',cells[1]))
                if m and (len(cells[2])>=20):
                    criterion.append(float(m.group(1)))
                    assert ('[' in cells[2] or 'http' in cells[2] or 'OT0' in cells[2] or 'PF0' in cells[2] or 'source' in cells[2].lower() or 'candidate' in cells[2].lower() or 'quote' in cells[2].lower()),(rid,seat,letter,cells[2][:50])
            assert len(criterion)==ncrit,(rid,seat,letter,len(criterion),criterion)
            assert all(1<=x<=5 for x in criterion)
            hit=re.search(r'(?im)^\*\*\s*overall(?:\s+cost)?[\s_]*(?:seat_score|score)?\s*:\s*([1-5]\.\d)\s*/\s*5(?:\.0)?',block)
            if hit is None:
                hit=re.search(r'(?im)^\*\*\s*Overall seat mean\s*:\s*[^\n=]*=\s*([1-5]\.\d)\s*/\s*5(?:\.0)?',block)
            assert hit is not None,(rid,seat,letter,'overall missing')
            reported=float(hit.group(1)); actual=half_up(sum(criterion)/len(criterion))
            assert reported==actual,(rid,seat,letter,reported,actual,criterion)
            assert len(re.findall(r'(?i)\btop_fix\s*:',block))==1 and len(re.findall(r'(?i)\bgate_flags\s*:',block))==1,(rid,seat,letter,'flags')
            assert 'DCOF' in block and ('FAIL' in block) and 'confidence' in block.lower(),(rid,seat,letter,'gate')
            scores[letter][seat]=reported
            out['verification']['criterion_checks']+=ncrit
            out['verification']['source_links_count']+=len(re.findall(r'\]\(([^)]+)\)',block))
    rr={'room':rid,'round':4,'critics_complete':True,'weights':{x:y[0] for x,y in SEATS.items()},'critic_file_fingerprints':critique_hashes,'candidates':{},'incumbent_letter':hist,'challenger_letter':chal}
    for letter in sorted(actual_letters):
        s=scores[letter]; weighted=round(sum(s[x]*SEATS[x][0] for x in SEATS)+1e-9,2)
        flags=['FAIL: floor exact measured SKU wet DCOF unavailable']
        if rid in ('PH-PRIMARY','PH-BATH4'):flags.append('FAIL: shower pan exact measured SKU wet DCOF unavailable')
        if (rid,letter) in [('PH-PRIMARY','C'),('PH-BATH3','B'),('PH-BATH4','A')]:flags.append('FAIL: wet-wall relief or niche product-specific approval absent')
        if rid=='PH-BATH3': flags.append('HOLD: tub/Delta square point-drain configuration and unselected basin')
        if rid=='PH-BATH4': flags.append('HOLD: 35-vs-27-SF floor and Soft-versus-Anti-Slip quoted finish')
        rr['candidates'][letter]={'role':key[letter],'seat_scores':s,'weighted_score':weighted,'minimum_critic_score':min(s.values()),'all_seat_minimum_3_pass':min(s.values())>=3,'hard_gates_pass':False,'gate_reasons':flags,'source_candidate_sha256':candidates[letter]['sha256']}
    rr['margin']=round(rr['candidates'][chal]['weighted_score']-rr['candidates'][hist]['weighted_score'],2)
    rr.update(decision='both_candidates_blocked_floor_gate',status='blocked',champion_id=None,champion_score=None,accepted_challenger=False,owner_approved=False,provisional_design_preference=(chal if rr['margin']>0 else hist),report='board/round-004/ROUND_REPORT.md')
    out['room_results'][rid]=rr
out['verification']['all_16_valid']=True
path=ROOT/'state/ROUND004_SCORING.json'
path.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
for rid,rr in out['room_results'].items():
    print(rid,'incumbent',rr['incumbent_letter'],rr['candidates'][rr['incumbent_letter']]['weighted_score'],'challenger',rr['challenger_letter'],rr['candidates'][rr['challenger_letter']]['weighted_score'],'delta',rr['margin'],'min challenger',rr['candidates'][rr['challenger_letter']]['minimum_critic_score'],'BLOCKED')
print('PASS',out['verification']['criterion_checks'],'actual criterion scores in 16 independent files; 8 immutable SHA; scoring persisted')

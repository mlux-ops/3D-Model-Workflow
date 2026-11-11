"""Read-only pre-dispatch 2-Bath3 independent source freeze and owner gate auditor."""
from pathlib import Path
import hashlib,json,re
from decimal import Decimal
R=Path(__file__).resolve().parents[1]
sub=R/'state/ROUND014_SUBMISSION.json'
fix=R/'state/ROUND014_PREDISPATCH_REVIEWER_FIX1.json'
data=json.loads(sub.read_text(encoding='utf-8'))
f=json.loads(fix.read_text(encoding='utf-8'))
assert data['round']==14 and data['all_critic_scores'] is None and data['weighted_scoring'] is None
assert data['critic_dispatch']=='NOT DISPATCHED'
fix2=R/'state/ROUND014_R16_REVIEWER_FIX2.json'
if fix2.exists():
    f2=json.loads(fix2.read_text(encoding='utf-8'))
    assert f2['source_submission_before_after']['old']['sha256']==f['source_submission_after']['sha256']
    assert f2['source_submission_before_after']['new']['sha256']==hashlib.sha256(sub.read_bytes()).hexdigest()
else:
    assert f['source_submission_after']['sha256']==hashlib.sha256(sub.read_bytes()).hexdigest()
assert set(data['rooms'])=={'PH-BATH3','TX-BATH3'}
rows=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
assert len(rows)==13
def scorelinks(p):
    t=p.read_text(encoding='utf-8')
    paths=[]
    for url in re.findall(r'\]\(([^)]+)\)',t):
        if url.startswith(('http:','https:','#','mailto:')):continue
        assert (p.parent/url.split('#')[0]).exists(),url
        paths.append(url)
    return len(paths)
count=0
for rid,letters in data['candidate_files'].items():
    assert len(letters)==2
    room=R/'rooms'/rid/'board/round-014'
    assert not list(room.glob('critic-*.md'))
    keys=json.loads((room/'_key.json').read_text(encoding='utf-8'))
    assert set(keys)==set(letters)
    def is_original(k):return ('historic' in k.lower() or k.lower().startswith('source '))
    assert sorted([is_original(k) for k in keys.values()])==[False,True]
    earlier=next(v for v in rows if v['id']==rid)
    assert earlier['last_round']==11 and earlier['status']=='blocked' and earlier['champion_id'] is None
    assert earlier['owner_status'] is None
    for letter,record in letters.items():
        p=R/record['file'];b=p.read_bytes();t=b.decode('utf-8')
        assert hashlib.sha256(b).hexdigest()==record['sha256'] and len(b)==record['bytes']
        lines=t.splitlines()
        assert lines[0]==f'# {rid} — Candidate {letter} — complete tile design option'
        assert lines[1]==''
        assert lines[2]=='This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.'
        assert 'incumbent candidate' not in t.lower() and 'challenger candidate' not in t.lower()
        assert 'actual owner TUB/WALK-IN program remain unchanged/unselected' in t
        assert '## Source-faithful same-depth five-column' in t
        assert 'Owner has NOT chosen TUB or WALK-IN' in t
        assert 'owner-signed' not in t.lower() or 'no' in t.lower()
        assert 'proposed RL21 maker Target' not in t
        if is_original(keys[letter]):
            assert 'Maker current RL21 1.5-in Hex thickness' not in t
            assert 'individual RL21 maker test/application' not in t
            assert 'no point pan tile selected at this program stage' in t
            if rid=='PH-BATH3':assert 'individual Opal wet gate NOT established' in t and 'source maker research](../../../../../research/products/elm-tones-sapphire' not in t
            else:assert 'original Grey Soft source and absent raw test' in t
        else:
            assert 'versioned maker 1/8-in versus 3/16-in grout recommendations CONFLICT' in t
            assert 'maker RL21 1.5-in Hex' in t
        count+=scorelinks(p)
        assert len([l for l in lines if l.startswith('| WALL ')])==1
        assert len([l for l in lines if l.startswith('| LEVEL ')])==1
        assert len([l for l in lines if l.startswith('| NICHE ')])==1
assert count==32
assert data['original_per_copy_usd']=={'PH-BATH3':930.42,'TX-BATH3':958.88}
assert not data['owner_approved'] and not data['procurement_release'] and not data['correct_native_1529_verified']
assert f['authentic_critic_files']==0 and f['all_critic_scores'] is None
assert 'Revised PH wet' not in (R/'research/products/R14_BATH3_MAKER_BRANCH_AND_POINT_PAN_20261106.md').read_text(encoding='utf-8')
print('PASS R014 4 SHA-frozen balanced neutral PH/TX BATH3 sources, 32 local links, historical maker relevance, explicit owner branch and no critic/scoring/release')
print('CURRENT_SHA',hashlib.sha256(sub.read_bytes()).hexdigest())

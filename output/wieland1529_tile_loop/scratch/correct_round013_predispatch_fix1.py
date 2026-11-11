"""One-time controlled refreeze of six PH R013 packets following worker-11 exact FIX."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SUB = ROOT/'state/ROUND013_SUBMISSION.json'
RECEIPT = ROOT/'state/ROUND013_PREDISPATCH_REVIEWER_FIX1.json'
assert not RECEIPT.exists()
before_sub = SUB.read_bytes()
before_sha = hashlib.sha256(before_sub).hexdigest()
assert before_sha == '5e2eff14139a90bdfffde8477b6f9ff0bfc18a413f681b3a913d37057612bd3c'
data = json.loads(before_sub)
assert data['all_critic_scores'] is None and data['critic_dispatch'] == 'NOT DISPATCHED'
assert data['critic_reports_present'] is False and not data['owner_approval'] and not data['procurement_release']

common_old = 'PH Primary WC is inherited in Primary floor, and a niche is excluded. Niche faces/back/returns cannot be double counted.'
arithmetic = {
    'PH-PRIMARY': 'PH Primary WC is included in Primary original floor gross, and the unselected Primary niche is expressly excluded. No separate WC or niche purchase.',
    'PH-BATH2': 'The existing Sandstone wet niche carries 3.67 gross SF in the original source; subtract its physical wall opening and add only verified recess back/returns/sill once. The selected Duravit tub has NO tiled shower pan.',
    'PH-BATH4': 'The existing 8.63-gross-SF Caviar niche source is not excluded; physically deduct its field opening and measure back/returns/sill for any proposed wet-listed niche finish. The original 40.2 gross SF LEVEL+POINT PAN is a single pooled amount, not two separate orders.',
}
maker = '[Daltile Prime RL21 product](https://www.daltile.com/products/stone-look/prime/dynamic-beige)'
fixes = {
    ('PH-PRIMARY','B'): [
        ('3/16-in manufacturer page grout note subject to sample', '1/8-in manufacturer page grout recommendation for the RL21 exact family, subject to actual tile caliber, installer joint and physical sample'),
    ],
    ('PH-BATH2','B'): [
        ('grout maker 3/16-in target study', 'individual RL21 maker 1/8-in grout recommendation, actual joint/caliber to be approved'),
        ('It is a different tile format/source family from the previous Glazzio floor study, not an already purchased substitute.', 'The selected RL21 LEVEL floor is a conditional, independently specified 12x24 product; manufacturer reported application suitability does not equal an exact wet laboratory test or an already purchased material.'),
    ],
    ('PH-BATH4','A'): [
        ('[Prime versioned maker application](../../../../../research/products/R07_DALTILE_PRIME_LINEAR_DRAIN_ALTERNATIVE_VERSIONED_EVIDENCE.md) shower-floor mosaic suitability is conditional maker application', f'{maker} manufacturer mosaic shower-floor suitability is a POINT PAN application study, not approved Brizo square-drain slope/liner or exact raw numeric slip test'),
    ]
}
prefix='**Nominal wall coordinates:** W1 59.496 in, W2/W3 30.60 in, height 93 in.'
fit = (" The nominal W1 tub-back wall width 59.496 in versus selected 59-in Duravit 700332000000090 nominal tub length yields only 0.496 in total nominal difference BEFORE actual rough opening, tub flange/tiling/backer thickness and field tolerance. This is an exact documented dimensional FIT HOLD, neither proven fit nor proven clash; obtain the correct 1529 as-built rough opening, manufacturer's actual installation envelope, both end clearances, waterproof flange and finished tile section before approval.")
for letter in ('B','C'):
    fixes.setdefault(('PH-BATH2',letter), []).append((prefix, prefix+fit))

def fp(b):
    return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}

old_new = {}
replacement_counts = {}
output = {}
for rid, variants in data['candidate_files'].items():
    old_new[rid] = {}
    for letter, frozen in variants.items():
        p=ROOT/f'rooms/{rid}/board/round-013/candidates/{letter}.md'
        old=p.read_bytes()
        assert fp(old)==frozen, (rid,letter,'source mutation before reviewer FIX')
        text=old.decode('utf-8')
        count=0
        assert text.count(common_old)==1
        text=text.replace(common_old,arithmetic[rid])
        count+=1
        for source,target in fixes.get((rid,letter),[]):
            assert text.count(source)==1,(rid,letter,source,text.count(source))
            text=text.replace(source,target)
            count+=1
        new=text.encode('utf-8')
        assert new!=old
        output[(rid,letter)]=(p,new)
        old_new[rid][letter]={'before':fp(old),'after':fp(new)}
        replacement_counts[f'{rid}/{letter}']=count

# No source bytes are changed until all six exact original fingerprint and replacement checks pass.
for p,new in output.values():
    p.write_bytes(new)
for rid, variants in old_new.items():
    for letter, values in variants.items():
        path=ROOT/f'rooms/{rid}/board/round-013/candidates/{letter}.md'
        assert fp(path.read_bytes())==values['after']
        data['candidate_files'][rid][letter]=values['after']

data['independent_preflight']='worker-11 precise FIX1 corrected, same-round independent rereview PENDING'
data['pre_dispatch_reviewer']='worker-11 FIX1 resubmission pending'
data['pre_dispatch_reviewer_fix1']={
    'reviewer':'worker-11',
    'before_submission_sha256': before_sha,
    'corrected_candidate_fingerprints': old_new,
    'changes_per_candidate': replacement_counts,
    'role_keys_changed':False,
    'critic_files_created':False,
    'scoring_performed':False,
    'owner_approval':False,
    'procurement_release':False
}
SUB.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
result = {
    'round':13,'as_of':'2026-11-06','reviewer':'worker-11',
    'verdict':'FIX five specific pre-dispatch neutral/source/geometry defects',
    'submission_sha256_before': before_sha,
    'submission_sha256_after': hashlib.sha256(SUB.read_bytes()).hexdigest(),
    'candidate_sha_before_after':old_new,
    'replacement_counts':replacement_counts,
    'source_private_keys_unchanged':True,
    'original_scored_round010_round012_untouched':True,
    'critics_absent':True,'all_critic_scores':None,
    'owner_approved':False,'procurement_release':False,
}
RECEIPT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS precise R013 reviewer FIX1, six controlled candidate SHA/byte refreeze and separate receipt',result['submission_sha256_after'])

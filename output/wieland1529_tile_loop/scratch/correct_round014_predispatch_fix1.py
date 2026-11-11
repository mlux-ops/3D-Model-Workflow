"""One-time precise independent Reviewer-14 R014 source and neutral-role FIX1.

No critics have been dispatched. Explicit SHA/byte old-new audit; freeze is updated
only before authentic independent blind specialists see the packet.
"""
from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1]
submission=R/'state/ROUND014_SUBMISSION.json'
receipt=R/'state/ROUND014_PREDISPATCH_REVIEWER_FIX1.json'
research=R/'research/products/R14_BATH3_MAKER_BRANCH_AND_POINT_PAN_20261106.md'
assert not receipt.exists()
data=json.loads(submission.read_text(encoding='utf-8'))
assert data['critic_dispatch']=='NOT DISPATCHED' and data['all_critic_scores'] is None and data['weighted_scoring'] is None
assert data['reviewer_preflight_verdict'] is None
for rid in ('PH-BATH3','TX-BATH3'):
    assert not list((R/'rooms'/rid/'board/round-014').glob('critic-*.md'))
def fp(p):
    b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
old_source=fp(submission)
oldkeys={rid:fp(R/'rooms'/rid/'board/round-014/_key.json') for rid in data['rooms']}
old_research=fp(research)

old_line='Grout recommendation maker webpage **1/8 in**; older alternate snapshots may differ, verify exact format/version.'
new_line='Manufacturer product webpages and earlier technical snapshots conflict on **1/8 in vs 3/16 in grout recommendation**. No universal joint approved; obtain exact item/format version, grout joint maker confirmation and physical mock-up before cut/grid or order.'
rtext=research.read_text(encoding='utf-8')
assert rtext.count(old_line)==1
research.write_text(rtext.replace(old_line,new_line),encoding='utf-8')

all_before_after={}
for rid,items in data['candidate_files'].items():
    room=R/'rooms'/rid/'board/round-014'
    role=json.loads((room/'_key.json').read_text(encoding='utf-8'))
    role_new={}
    for letter,record in items.items():
        p=R/record['file']
        assert fp(p)['sha256']==record['sha256'] and fp(p)['bytes']==record['bytes']
        orig=fp(p);t=p.read_text(encoding='utf-8')
        historic='historic' in role[letter].lower()
        assert historic or 'revised' in role[letter].lower()
        # Symmetrical, neutral style; a specialist sees the actual specified product
        # but never sees role tags or an alternative's hidden identity.
        lines=t.splitlines()
        assert lines[8].startswith('**Material specification:**')
        m=re.search(r'Wet wall field: (.*?), nominal 2x20 Glossy,',lines[8])
        assert m
        material=m.group(1)
        level='Cortar Bone 12x24 Soft' if rid=='PH-BATH3' and historic else 'Cortar Grey 12x24 Soft' if rid=='TX-BATH3' and historic else 'Daltile Prime Dynamic Beige RL21 12x24 Matte LEVEL'
        pan='no point pan tile selected at this program stage' if historic else 'Daltile Prime Dynamic Beige RL21 1.5-in Hex Matte POINT PAN for owner-signed WALK-IN only'
        lines[8]=(f'**Material specification:** {material} 2x20 Glossy field with Tones Sandstone 2x20 Glossy wet-listed niche; nominal 2x20 tile orientation, grout and geometry are subject to a 1:1 sample and exact maker permission. '
                  f'LEVEL bath floor study: {level}. Conditional point-shower material: {pan}. Selected square drain and actual owner TUB/WALK-IN program remain unchanged/unselected. Actual field aperture, niche back/returns/sill, installer details and verified 1529 geometry are required before release.')
        t='\n'.join(lines)+'\n'
        if rid=='PH-BATH3' and historic:
            old='[source maker research](../../../../../research/products/elm-tones-sapphire-2x20-wet-approved.md)'
            new='[individual Opal wet gate NOT established](../../../../../research/products/R14_BATH3_MAKER_BRANCH_AND_POINT_PAN_20261106.md)'
            assert t.count(old)==1;t=t.replace(old,new)
        if historic:
            old='[individual RL21 maker test/application](../../../../../research/products/R14_BATH3_MAKER_BRANCH_AND_POINT_PAN_20261106.md), distinct original finish'
            if rid=='PH-BATH3':
                new='[individual original Bone Soft finish evidence](../../../../../research/products/elm-cortar-bone-soft-12x24.md), exact raw wet lab test unavailable'
            else:
                new='[original Grey Soft source and absent raw test explicitly recorded](../../../../../research/products/R14_BATH3_MAKER_BRANCH_AND_POINT_PAN_20261106.md), no proposed alternate maker test transfers'
            assert t.count(old)==1;t=t.replace(old,new)
            old='Original v4 LEVEL Soft fails exact raw measured wet DCOF regardless of aesthetic or Target literature; proposed RL21 maker Target also fails exact raw test. No physical shower-pan approval.'
            new='This specified original Soft LEVEL lacks the exact individual raw measured numerical wet certificate. If WALK-IN selected, it does NOT nominate any pan tile or maker test; no four-plane point-pan layout or signed waterproof section is approved.'
            assert t.count(old)==1;t=t.replace(old,new)
            old='- Maker current RL21 1.5-in Hex thickness 5/16-in versus older 1/4-in brochure; manufacturer web grout 1/8-in recommendation. Chip/caliber/joint/mesh and selected 4-in SQUARE POINT throat/liner must be checked in actual sourced/approved assembly. Do not transfer Primary Brizo 48-in linear tile-in 7-18mm frame to this point-drain room.'
            new='- This specific original Soft 12x24 LEVEL format has no identified small-format four-plane point-drain pan tile. Manufacturer original Soft finish, actual grout/joint, substrate, 4-in POINT drain rough/membrane and separate small-format PAN must be verified from source after owner WALK-IN election. No unrelated maker mosaic/linear frame is part of this option.'
            assert t.count(old)==1;t=t.replace(old,new)
        else:
            old='Original v4 LEVEL Soft fails exact raw measured wet DCOF regardless of aesthetic or Target literature; proposed RL21 maker Target also fails exact raw test. No physical shower-pan approval.'
            new='This particular RL21 12x24 LEVEL and separately 1.5-in Hex POINT PAN rely on maker Target suitability only; neither individual exact raw numerical measured wet DCOF is supplied. The 4-in square point-drain and full waterproof section remain unapproved.'
            assert t.count(old)==1;t=t.replace(old,new)
            old='manufacturer web grout 1/8-in recommendation.'
            new='versioned maker 1/8-in versus 3/16-in grout recommendations CONFLICT (HOLD; verify exact SKU and latest written joint requirement).'
            assert t.count(old)==1;t=t.replace(old,new)
        assert 'proposed RL21 maker Target' not in t
        assert not (historic and ('Maker current RL21 1.5-in Hex thickness' in t or 'source maker research](../../../../../research/products/elm-tones-sapphire' in t))
        p.write_text(t,encoding='utf-8')
        now=fp(p)
        record.update(sha256=now['sha256'],bytes=now['bytes'])
        all_before_after[record['file']]={'old':orig,'new':now}
    if rid=='TX-BATH3':
        role_new={k:('source Tones Emerald Wet Areas-listed and Cortar Grey Soft LEVEL; no PAN specified' if 'historic' in v.lower() else 'conditional Tones Emerald Wet Areas-listed; Daltile RL21 distinct LEVEL/POINT PAN study') for k,v in role.items()}
        (room/'_key.json').write_text(json.dumps(role_new,indent=2)+'\n',encoding='utf-8')

data['revision']='pre-dispatch source-only FIX1 after independent worker-14 precise review; NO critics dispatched, no scored arithmetic'
data['source_fix_receipt']='state/ROUND014_PREDISPATCH_REVIEWER_FIX1.json'
data['reviewer_preflight_verdict']=None
submission.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
audit={
 'round':14,'as_of':'2026-11-06','reviewer':'worker-14',
 'fix':'Original historical PH Opal wet cited its own unlisted record instead of Sapphire; original Cortar Bone/Grey Soft LEVEL no RL21 maker transferred; remove revised-role prose and wrong cross-option floor/pan tests; point-only RL21 candidates versioned grout 1/8-vs-3/16 conflict; neutralize TX private mapping wording',
 'source_submission_before':old_source,'source_submission_after':fp(submission),
 'four_candidate_before_after':all_before_after,
 'maker_research_before':old_research,'maker_research_after':fp(research),
 'private_keys_before':oldkeys,'private_keys_after':{rid:fp(R/'rooms'/rid/'board/round-014/_key.json') for rid in data['rooms']},
 'authentic_critic_files':0,'all_critic_scores':None,'weighted_scores':None,
 'original_R013_or_earlier_signed_files_changed':False,'owner_approval':False,'procurement_release':False}
receipt.write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
print('PASS R014 independent precise FIX1 re-freeze four candidates and maker note with role/maker source separation; 0 critics')
print('SOURCE_SHA',fp(submission)['sha256'])

"""One-time in-place controlled R019 source FIX1; preserve audit lineage."""
import json
import pathlib
import hashlib

root = pathlib.Path(__file__).resolve().parents[1]
receipt = root/'state/ROUND019_TILE_ONLY_NEXT_COHORT_SOURCE_AWAIT_R018_FORMAL_CLEARANCE.json'
data = json.loads(receipt.read_text(encoding='utf-8'))
assert data['round'] == 19 and 'FIX1' not in data
old = {k: dict(v) for k,v in data['files'].items()}
changes = []
for room in ('PH-BATH3', 'PH-BATH4', 'TX-BATH3'):
    for letter in {'PH-BATH3':'AC','PH-BATH4':'BC','TX-BATH3':'AB'}[room]:
        rel = f'rooms/{room}/board/round-019/candidates/{letter}.md'
        p = root / rel
        before = p.read_text(encoding='utf-8')
        b = p.read_bytes()
        assert hashlib.sha256(b).hexdigest() == old[rel]['sha256'] and len(b) == old[rel]['bytes']
        after = before
        if room == 'PH-BATH4':
            after = after.replace('2x2 mosaic in separate four-plane sloping footprint only if owner-program includes WALK-IN. Tub branch: **tiled PAN N/A**; never replace a tub waste with shower drain.',
                                  '2x2 mosaic in separate four-plane sloping footprint because owner-selected WALK-IN is FIXED; no TUB branch applies.')
            after = after.replace('**UNKNOWN** pending owner TUB/WALK-IN + actual pan/level boundary; WALK-IN FIXED, but actual four-plane pan SF still UNKNOWN',
                                  '**UNKNOWN** actual four-plane POINT pan SF and LEVEL/PAN boundary; owner WALK-IN FIXED')
        if room != 'PH-BATH4':
            after = after.replace('For PH-BATH4 selected WALK-IN, 24x48 flat WALL is never laid on the four-plane PAN.',
                                  'For this Bath3 room, owner TUB versus WALK-IN remains UNSELECTED; a separately wet-listed 2x2 PAN is conditional on WALK-IN only, and no WALL field tile substitutes for POINT PAN.')
        assert after != before, f'No text change for {rel}'
        p.write_text(after,encoding='utf-8',newline='\n')
        updated = p.read_bytes()
        data['files'][rel] = {'sha256':hashlib.sha256(updated).hexdigest(),'bytes':len(updated)}
        changes.append({'path':rel,'previous':old[rel],'updated':data['files'][rel]})
data['FIX1'] = {'reason':'Correct conditional vs fixed shower program and eliminate cross-room PH4 wording from Bath3 neutral packets',
                'controlled_old_new':changes,'original_candidates_preserved_except_targeted_branch_text':True}
receipt.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
print('R019 controlled FIX1:',len(changes),'changed candidate hashes, new receipt, no original signed predecessors changed')

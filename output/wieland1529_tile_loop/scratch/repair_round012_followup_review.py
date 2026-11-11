"""One-time narrow correction for worker-11's R012 follow-up FIX; NOT a rescore."""

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOMS = ROOT / 'state/ROOMS.json'
SCORER = ROOT / 'scratch/score_round012.py'
SCORING = ROOT / 'state/ROUND012_SCORING.json'
RECEIPT = ROOT / 'state/ROUND012_POST_SCORE_REVIEWER_FIX2.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


assert not RECEIPT.exists(), 'Refusing duplicate receipt or a repeat mutation.'
original = ROOMS.read_bytes()
rooms = json.loads(original)
assert (json.dumps(rooms, indent=2, ensure_ascii=False) + '\n').replace('\n', '\r\n').encode('utf-8') == original, 'ROOMS format changed: stop, no write.'
assert sha(ROOMS) == '61720b25b05bb3a91ff8eb5af98729d540b7a718031167e435e6f375c1218606'
assert sha(SCORING) == '4821b98e4958852ec21263a33437ecf5d149fa9f2f5fd0784803253f2cb235fe'
ast.parse(SCORER.read_text(encoding='utf-8'), filename=str(SCORER))

# The previous shared paragraph incorrectly made Emser/Prime appear to be source products.
# Each replacement names the source and proposed floor/pan separately and keeps every
# prior room decision, score, release flag, quote row, and signed package unchanged.
fix = {
    'TX-PRIMARY': (
        'R012 source B: Cortar Clay Soft LEVEL and Cortar Clay Anti-Slip LINEAR PAN each lack exact SKU raw numerical wet DCOF; Cortar Clay Ribbed relief wet-wall listing FAIL. Source Brizo Black Onyx 48-in LINEAR/BR73480 membrane, slope and flood section HOLD. Revised C: wet-listed flat Clay WALL PASS; Emser Capisco Trosa LEVEL published >=0.60 is a bound, and Daltile Prime RL21 LINEAR PAN Target is not an exact lab result; nominal 0.65-mm Prime/Brizo frame build-up HOLD, not proven incompatible. Primary niche excluded; WC floor source gross included.',
        'R012 both source and proposed options are BLOCKED on individual raw wet floor/pan tests, source relief listing and/or physical coordination; no owner approval or release.'
    ),
    'TX-BATH2': (
        'R012 source C: Cortar Clay Soft LEVEL exact SKU raw numerical wet DCOF absent; manufacturer-wet-listed Copper/Sandstone tub-wall palette retained. Revised A: Emser Capisco Trosa LEVEL published >=0.60 is a bound, not an exact SKU raw laboratory result; both LEVEL tests remain FAIL. Actual Duravit tub and Chrome Hansgrohe; NO tiled shower PAN; basin OWNER UNSELECTED. Owner signoff, niche/tub flange survey and Chicago installed quote HOLD.',
        'R012 source and revised LEVEL floors independently blocked; tub/no-pan program unaffected, no owner approval or procurement release.'
    ),
    'TX-BATH4': (
        'R012 source A: Cortar Bone Soft LEVEL exact SKU raw numerical wet DCOF absent, Clara Caviar niche individual wet listing FAIL; flat Cortar Charcoal tub wall wet-listed. Revised B: Emser Capisco Trosa LEVEL published >=0.60 is a bound not an exact SKU raw lab result, Soho Ivory 2x10 Glossy niche Wet Areas PASS; level-floor test remains FAIL. Actual Duravit tub with Matte White Hansgrohe, NO tiled shower PAN. Niche dimensions, owner signature and current Chicago bid HOLD.',
        'R012 source Bone Soft/Caviar and revised Emser/Soho gate attribution is separate; both options BLOCKED, no owner approval or procurement release.'
    ),
}

snapshot = {r['id']: r for r in rooms['rooms']}
for rid, (text, note) in fix.items():
    row = snapshot[rid]
    assert row['last_round'] == 12 and row['status'] == 'blocked' and row['champion_id'] is None
    assert row['owner_status'] is None and row['board_round_012']['owner_approved'] is False
    assert row['board_round_012']['procurement_release'] is False
    gaps = row['open_gaps']
    bad = [i for i, item in enumerate(gaps) if item.startswith('FAIL: exact manufacturer SKU/finish raw numeric measured wet DCOF on LEVEL bath floor absent; published Emser >=0.60')]
    notice = [i for i, item in enumerate(gaps) if item.startswith('R012 scored source-vs-revised product gate attribution corrected:')]
    assert len(bad) == len(notice) == 1 and bad[0] + 1 == notice[0], rid
    gaps[bad[0]] = text
    gaps[notice[0]] = note

updated = (json.dumps(rooms, indent=2, ensure_ascii=False) + '\n').replace('\n', '\r\n').encode('utf-8')
assert updated != original
assert len(rooms['rooms']) == 13
check = json.loads(updated)
for rid in fix:
    a, b = (next(r for r in d['rooms'] if r['id'] == rid) for d in (json.loads(original), check))
    for k in a:
        if k != 'open_gaps':
            assert a[k] == b[k], (rid, k)
    assert len(a['open_gaps']) == len(b['open_gaps'])
    assert all(x == y for i, (x, y) in enumerate(zip(a['open_gaps'], b['open_gaps'])) if i < len(a['open_gaps']) - 2)

stable = ['state/ROUND012_SCORING.json', 'state/ROUND012_SUBMISSION.json',
          'state/ROUND012_CRITIC_DISPATCH.json', 'state/ROUND012_CRITIC_COLLECTION.json',
          'deliverables/integrated-r12/MANIFEST.json', 'deliverables/integrated-r13/MANIFEST.json']
stable_before = {name: sha(ROOT / name) for name in stable}
scorer_before = '0c44336b30e5ad64d92fdd731e36253027229123665bacaf8d5dee0f2367a8c9e'
scorer_after = sha(SCORER)
assert scorer_before != scorer_after
room_before = hashlib.sha256(original).hexdigest()
ROOMS.write_bytes(updated)
assert json.loads(ROOMS.read_bytes()) == check
assert all(sha(ROOT / name) == digest for name, digest in stable_before.items())

receipt = {
    'as_of': '2026-11-06', 'round': 12, 'independent_reviewer': 'worker-11',
    'verdict_addressed': 'FIX scorer syntax and obsolete three TX open_gaps source/revised attribution',
    'scorer_script_sha256_before': scorer_before,
    'scorer_script_sha256_after': scorer_after,
    'scorer_ast_parse_pass': True, 'formal_scoring_rerun': False,
    'rooms_sha256_before': room_before,
    'rooms_sha256_after': sha(ROOMS),
    'only_room_open_gaps_entries_replaced': True,
    'rooms': sorted(fix), 'two_entries_replaced_per_room': True,
    'immutable_artifact_hashes': stable_before,
    'original_candidate_or_critic_modified': False,
    'scores_and_statuses_unchanged': True,
    'owner_approved': False, 'procurement_release': False,
}
RECEIPT.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print('PASS R012 followup exact FIX: scorer ast.parse, three room open_gaps two entries each, 6 stable evidence/manifest SHA, unchanged source/critic/scoring/release.')
print('scorer SHA', scorer_after, 'ROOMS SHA', sha(ROOMS), 'receipt SHA', sha(RECEIPT))

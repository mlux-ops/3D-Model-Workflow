"""R036 independently reproduce original criterion arithmetic; never generate critics."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import re, json

ROOT = Path(__file__).resolve().parents[1]
ROOMS = ('PH-BATH4', 'PH-BATH3', 'TX-BATH3')
WEIGHTS = {'market': Decimal('.30'), 'design': Decimal('.25'),
           'build': Decimal('.25'), 'cost': Decimal('.20')}
EXPECTED = {'market': 4, 'design': 5, 'build': 5, 'cost': 5}
Q = lambda x: x.quantize(Decimal('.1'), rounding=ROUND_HALF_UP)
line_table = re.compile(r'^\|[^|]+\|\s*(?:\*\*)?([1-5](?:\.\d+)?)(?:\s*/\s*5)?(?:\*\*)?\s*\|')
line_numbered = re.compile(r'^\s*\d+[.)]\s+.+?\s+[—–-]\s*([1-5](?:\.\d+)?)\s*/\s*5\b')
line_unified = re.compile(r'^\|\s*([AB])\s*\|[^|]+\|\s*\*{0,2}([1-5](?:\.\d+)?)\*{0,2}\s*\|')
out = {}
count = 0
missing = []
for room_id in ROOMS:
    scores = {}
    for seat, weight in WEIGHTS.items():
        path = ROOT / 'rooms' / room_id / 'board' / 'round-036' / ('critic-' + seat + '.md')
        if not path.exists():
            missing.append(str(path.relative_to(ROOT)))
            continue
        content = path.read_text(encoding='utf-8-sig')
        sections = re.split(r'(?m)^## Candidate ([AB])\b[^\n]*\n', content)
        if len(sections) == 5:
            assert {sections[1], sections[3]} == {'A', 'B'}, (room_id, seat, sections[1::2])
            per_candidate = {}
            for i in (1, 3):
                letter, body = sections[i], sections[i+1]
                values = []
                for line in body.splitlines():
                    match = line_table.match(line) or line_numbered.match(line)
                    if match:
                        values.append(Decimal(match.group(1)))
                per_candidate[letter] = (values, body)
        else:
            # Original critics may use one unified table: Candidate | Criterion | Rating | Reason.
            unified = {'A': [], 'B': []}
            for line in content.splitlines():
                match = line_unified.match(line)
                if match:
                    unified[match.group(1)].append(Decimal(match.group(2)))
            assert any(unified.values()), (room_id, seat, 'unrecognized candidate rating layout')
            per_candidate = {letter: (values, content) for letter, values in unified.items()}
        for letter, (values, body) in per_candidate.items():
            assert len(values) == EXPECTED[seat], (room_id, seat, letter, values)
            assert all(Decimal(1) <= x <= Decimal(5) for x in values)
            assert all(re.search(field, body, re.I) for field in
                       (r'top[_ ]fix', r'gate[_ ]flags', r'confidence')), (room_id,seat,letter,'missing decision fields')
            mean = Q(sum(values) / Decimal(len(values)))
            declared = [Decimal(x) for x in re.findall(
                r'(?:seat[_ ]mean|Arithmetic (?:seat )?mean|Overall .*?(?:mean|score))[^\n]{0,125}?([1-5]\.\d)\s*/\s*5',
                body, re.I)]
            if len(sections) == 5 and declared:
                assert mean in declared, (room_id, seat, letter, str(mean), declared)
            if len(sections) == 5:
                seat_decl = re.search(r'(?mi)^Seat mean:\s*[^\n]*?=\s*([1-5]\.\d)\s*\.?\s*$',body)
                if seat_decl:
                    assert mean == Decimal(seat_decl.group(1)),(room_id,seat,letter,mean,seat_decl.group(1))
            if len(sections) != 5:
                arithmetic = re.search(r'(?mi)^\*\*'+letter+r' arithmetic:\*\*[^\n]*?([1-5]\.\d)\s*/\s*5', content)
                if arithmetic:
                    assert mean == Decimal(arithmetic.group(1)), (room_id, seat, letter, mean, arithmetic.group(1))
            scores.setdefault(letter, {})[seat] = {'criteria': [str(x) for x in values], 'mean': str(mean)}
            count += len(values)
    if len(scores.get('A', {})) == 4 and len(scores.get('B', {})) == 4:
        for letter in ('A', 'B'):
            means = [Decimal(scores[letter][seat]['mean']) for seat in WEIGHTS]
            weighted = sum(Decimal(scores[letter][seat]['mean']) * w for seat, w in WEIGHTS.items())
            scores[letter]['weighted'] = str(weighted.quantize(Decimal('.001')))
            scores[letter]['minimum_seat'] = str(min(means))
            scores[letter]['specialist_gate_pass'] = min(means) >= 3
    out[room_id] = scores
if missing:
    print(json.dumps({'status': 'INCOMPLETE', 'missing': missing, 'criteria_present': count, 'scores': out}, indent=2))
    raise SystemExit(2)
assert count == 114, count
print(json.dumps({'status': 'PASS', 'criterion_count': count,
                  'seat_means_count': 24, 'weighted_count': 6, 'room_boards': out}, indent=2))

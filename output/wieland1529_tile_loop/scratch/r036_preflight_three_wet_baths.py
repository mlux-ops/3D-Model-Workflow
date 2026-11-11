"""Check neutral R036 technical A/B sources, not critiques or historic outcomes."""
from pathlib import Path
import re
from decimal import Decimal, ROUND_HALF_UP

ROOT=Path(__file__).resolve().parents[1]
IDS=('PH-BATH4','PH-BATH3','TX-BATH3')
deny=(r'(?i)round[- ]0(?:30|31|34|35)',r'(?i)previous[ _-]champion',r'(?i)incumbent',
      r'(?i)weighted (?:board )?score',r'(?i)critic[-_](?:build|design|cost|market)\.md',
      r'(?i)state/ROOMS\.json',r'(?i)state/LEDGER\.md',r'(?i)_key\.json',
      r'(?i)\b(winner|defended incumbent|challenger)\b')
for rid in IDS:
    lengths=[]
    for letter in ('A','B'):
        p=ROOT/'rooms'/rid/'board'/'round-036'/'candidates'/(letter+'.md')
        data=p.read_text(encoding='utf-8')
        lengths.append(len(data))
        for pattern in deny:
            assert not re.search(pattern,data),(rid,letter,'blind source leakage',pattern)
        assert data.startswith(f'# R036 neutral candidate {letter} - {rid}')
        assert all(x in data for x in ('BLIND A/B','Actual two instances','Wet WALL',
                                       'NICHE','Bathroom LEVEL','DCOF >=0.42',
                                       'Shower Floors YES','15% waste ONCE',
                                       'price','top_fix','gate_flags','confidence'))
        assert 'PRICE ON REQUEST' in data or 'FILL IN' in data
        assert 'https://www.flooranddecor.com/porcelain-tile/' in data
        assert 'owner' in data.casefold() and 'Chicago' in data
        assert 'OT01' in data and 'OT04' in data and 'one 405 w armitage development' in data.casefold()
        assert data.count('| Wet WALL |')==1
        assert data.count('| Bathroom LEVEL |')==1
        assert data.count('| One existing NICHE all-face pool |')==1
        if rid=='PH-BATH4':
            assert 'WALK-IN selected' in data and '40.2 SF' in data and 'BNX' in data and 'POINT' in data
            assert '35 SF' in data and '27 SF' in data
        else:
            assert 'TUB or WALK-IN UNSELECTED' in data and 'NULL' in data
        if rid=='PH-BATH3':
            assert 'basin OWNER UNSELECTED' in data and 'Delta Chrome DT062412' in data
        if rid=='TX-BATH3':
            assert 'Brizo Brilliance Black Onyx' in data
        print(rid,letter,len(data),'neutral content PASS')
    assert max(lengths)/min(lengths)<1.15,(rid,lengths,'source depth asymmetry')
print('PASS R036 three-room six-candidate substantive neutral-source preflight; NO board scores or reviewer verdict implied')

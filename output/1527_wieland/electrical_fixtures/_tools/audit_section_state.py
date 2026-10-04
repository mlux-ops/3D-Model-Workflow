"""Summarize existing electrical family evidence without rebuilding anything."""
from pathlib import Path
import json
import re
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def main():
    inventory = load(ROOT / 'ITEMS.json')['items']
    groups = load(ROOT / 'GROUPS.json')['groups']
    records = []
    for group in groups:
        folder = ROOT / group['canonical_item']
        path = folder / 'validation.json'
        validation = load(path) if path.exists() else {}
        record = dict(key=group['key'], rows=len(group['rows']), folder=group['canonical_item'],
                      rfas=[p.name for p in folder.glob('*.rfa') if not re.search(r'\.\d{4}$', p.stem)],
                      technical_pass=validation.get('technical_pass'),
                      stage=validation.get('stage'),
                      actual=validation.get('measured_saved_dimensions_in', validation.get('actual_dimensions_in')),
                      fail_gates=[k for k, v in validation.get('gates', {}).items() if not v],
                      note=(folder / 'NOTES.md').exists())
        records.append(record)
        print('{rows:2d} | {key:44s} | pass={technical_pass!s:5s} | {stage!s:16s} | {rfas}'.format(**record))
        if record['fail_gates']:
            print('  FAILED:', record['fail_gates'])
    print('ITEM TOTAL', len(inventory), 'GROUP TOTAL', len(groups))
    print('CANONICAL PASSES', sum(r['technical_pass'] is True for r in records))
    print('ROW NOTES', sum((ROOT / i['item_key'] / 'NOTES.md').exists() for i in inventory))
    print('ROW VALIDATIONS', sum((ROOT / i['item_key'] / 'validation.json').exists() for i in inventory))
    print('RFA FILES', len(list(ROOT.glob('*/*.rfa'))))
    (ROOT / '_review' / 'resume_audit.json').write_text(json.dumps(records, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()

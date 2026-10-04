"""Print the measured inventory of inspected native sources."""
from pathlib import Path
from collections import Counter
import json
ROOT = Path(__file__).resolve().parents[1]
for row in json.loads((ROOT / 'NATIVE_SOURCE_INSPECTION.json').read_text()):
    print('\n%s | %s | %s | saved %s' % (row['key'], row['stage'], row.get('category'), row.get('saved_format')))
    if row.get('error'):
        print(row['error'])
        continue
    forms = [f for f in row['forms'] if f.get('native_bounds_in') and not (f['native_bounds_in'][5] <= 0.001 and f['native_bounds_in'][0] < -40)]
    if forms:
        bounds = [min(f['native_bounds_in'][a] for f in forms) for a in range(3)] + [max(f['native_bounds_in'][a+3] for f in forms) for a in range(3)]
        print('DIMENSIONS:', [round(bounds[a+3]-bounds[a], 6) for a in range(3)])
    print('PARTS:', dict(Counter(f.get('category') for f in forms)))
    print('MATERIALS:', [(p['name'], p.get('element_name')) for p in row['parameters'] if 'material' in p['data_type']])
    print('LENGTHS:', [(p['name'], round((p.get('double_internal') or 0)*12, 6), p['formula']) for p in row['parameters'] if 'length' in p['data_type']])

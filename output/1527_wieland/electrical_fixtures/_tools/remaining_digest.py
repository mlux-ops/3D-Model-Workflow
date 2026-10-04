"""Print only remaining primary links and the two OEM native inventories."""
from pathlib import Path
import json, sys
sys.stdout.reconfigure(errors='replace')
ROOT = Path(__file__).resolve().parents[1]
for row in json.loads((ROOT / 'REMAINING_PRIMARY.json').read_text()):
    print('\nPRIMARY', row['group'], row.get('url'), row.get('error', ''))
    for link in row.get('technical_links', []):
        if any(x in link['url'].lower() for x in ['.pdf', '.rfa', '.zip', 'download', 'spec']):
            print(link['label'][:70], link['url'])
for row in json.loads((ROOT / 'OEM_ADDITIONAL_INSPECTION.json').read_text()):
    print('\nOEM', row['key'], row['stage'], row.get('category'), row.get('warnings'), row.get('types'))
    for p in row.get('parameters', []):
        if p['name'] in ['Model', 'Manufacturer'] or 'material' in p.get('data_type', ''):
            print(' PARAM', p)
    for f in row.get('forms', []):
        if f.get('native_bounds_in'):
            print(' FORM', f)

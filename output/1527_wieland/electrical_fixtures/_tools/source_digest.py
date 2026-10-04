"""Print concise identity and technical-link evidence from retained public pages."""
from pathlib import Path
import json
import re
import sys
sys.stdout.reconfigure(errors='replace')
ROOT = Path(__file__).resolve().parents[1]
records = json.loads((ROOT / 'SOURCE_COLLECTION.json').read_text(encoding='utf-8'))
if (ROOT / 'OEM_COLLECTION.json').exists():
    records.extend(json.loads((ROOT / 'OEM_COLLECTION.json').read_text(encoding='utf-8')))
if (ROOT / 'REMAINING_PRIMARY.json').exists():
    records.extend(json.loads((ROOT / 'REMAINING_PRIMARY.json').read_text(encoding='utf-8')))
chosen = set(sys.argv[1:])
for record in records:
    if chosen and record['group'] not in chosen:
        continue
    print('\n' + record['group'] + ' | ' + (record.get('title') or record.get('error', '')))
    if record.get('text_path'):
        text = Path(record['text_path']).read_text(encoding='utf-8')
        lines = text.splitlines()
        try:
            start = lines.index('Product Details')
        except ValueError:
            start = 0
        for idx, line in enumerate(lines[start:], start):
            if re.match(r'^(Size:|Finish:|Color:|Canopy:|Backplate:|Cord Length:|Adjustable|Overall|Width:|Height:|Depth:)', line):
                print('  ' + ' '.join(lines[idx:idx + 2]))
            if idx > start + 125:
                break
    for link in record.get('technical_links', []):
        if 'installation_gallery' not in link['url']:
            print('  FILE ' + link['label'] + ' | ' + link['url'])

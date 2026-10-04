"""Reconcile explicit selection corrections and preserve every inventory row."""
from pathlib import Path
import json
import re
from collections import OrderedDict

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'ITEMS.json').read_text(encoding='utf-8-sig'))
groups = OrderedDict()
for item in data['items']:
    raw = item.get('model_number') or ''
    desc = item.get('description') or ''
    model = raw
    if '57670WTBK' in raw or raw == 'MAX1023280':
        model = '57670WTBK'
    elif '54654241-4PK' in raw:
        model = '54654241-4PK'
    elif not model:
        model = 'HOLD_PERGOLA' if 'pergola' in desc.lower() else ('HOLD_LED_STRIP' if 'LED Strip' in desc else 'ORION_TUBE_UNSPECIFIED')
    key = re.sub(r'[^A-Za-z0-9._-]+', '_', model)
    group = groups.setdefault(key, {'key': key, 'model': model, 'description': desc.split(' | ')[0],
                                   'canonical_item': item['item_key'], 'rows': [], 'urls': [], 'source_notes': []})
    group['rows'].append({'row_id': str(item['row_id']), 'item_key': item['item_key'],
                          'tag': item.get('item_tag_or_code'), 'unit': item.get('unit_type'),
                          'room': item.get('room_type'), 'agent_ignore': item.get('agent_ignore', False)})
    for url in item.get('product_urls') or []:
        if url not in group['urls']:
            group['urls'].append(url)
    if item.get('source_notes') and item['source_notes'] not in group['source_notes']:
        group['source_notes'].append(item['source_notes'])
    folder = ROOT / item['item_key']
    (folder / 'source').mkdir(parents=True, exist_ok=True)
    (folder / 'inventory_row.json').write_text(json.dumps(item, indent=2), encoding='utf-8')
result = {'row_count': len(data['items']), 'group_count': len(groups), 'groups': list(groups.values())}
(ROOT / 'GROUPS.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print('Rows: %d; distinct identity groups: %d' % (result['row_count'], result['group_count']))
for group in groups.values():
    print('%2d | %-44s | %s' % (len(group['rows']), group['model'], group['description'][:90]))

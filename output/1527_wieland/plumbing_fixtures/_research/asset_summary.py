"""Print only product assets from captured source pages, excluding site navigation."""
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parent
for path in sorted(root.glob('*/sources.json')):
    data = json.loads(path.read_text(encoding='utf-8'))
    assets = []
    issues = []
    for page in data['pages']:
        if page.get('error'):
            issues.append(page['error'])
        if any(term in page.get('title', '').lower() for term in ['interruption', 'access denied', 'just a moment']):
            issues.append('HTTP 200 challenge page; not product content')
        for link in page.get('asset_links', []):
            if re.search(r'(?i)\.(rfa|zip|pdf|dwg|dxf|stp)(\?|$)|bimsmith|bimobject', link['url']):
                assets.append(link['url'])
    print(json.dumps({'sku': data['sku'], 'assets': list(dict.fromkeys(assets)), 'issues': list(dict.fromkeys(issues))}))

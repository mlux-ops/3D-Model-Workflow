"""Read revised first-party resource pages and preserve their public links."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json, sys
from collect_sources import fetch
sys.stdout.reconfigure(errors='replace')
ROOT = Path(__file__).resolve().parents[1]
groups = {g['key']: g for g in json.loads((ROOT/'GROUPS.json').read_text())['groups']}
sources = [
    ('MFR918914', 'https://modernforms.com/product/zephyr-52/'),
    ('MFR918914', 'https://aispire.com/product/zephyr-52/'),
    ('4BEMW_SWW5_90CRI_M6', 'https://www.acuitybrands.com/products/detail/1897044/juno/e-series-led-trim-kit/4in-5-and-6in-switchable-white-led-downlights-in-smooth-or-baffle-trim-styles'),
    ('ARC1334006', 'https://www.artcraftlighting.com/en/products/2024-products/ac11976sm-modena-6lt-chandelier'),
    ('54654241-4PK', 'https://www.manualshelf.com/manual/commercial-electric/54654241-4pk/specification.html'),
]
jobs = [(key,groups[key]['canonical_item'],80+i,url) for i,(key,url) in enumerate(sources)]
with ThreadPoolExecutor(max_workers=3) as pool:
    records = list(pool.map(fetch,jobs))
(ROOT/'COMPLETION_DISCOVERY.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
for row in records:
    print('\n',row['group'],row.get('title',row.get('error')))
    for link in row.get('technical_links',[]):
        if any(s in (link['label']+' '+link['url']).lower() for s in ['.rfa','.zip','spec','revit']):
            print(link['label'][:55],link['url'])

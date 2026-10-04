"""Download additional exact-model manufacturer CAD and dimensional evidence."""
import concurrent.futures
import json
from source_fetch import fetch, ROOT

ASSETS = [
    ('miele_kwt6722is', 'manufacturer.zip', 'https://media.miele.com/downloads/a5/52/05_70A8A51285B71FE1ABFA89BF1ABCA552.zip'),
    ('miele_kwtus7172f', 'manufacturer.zip', 'https://media.miele.com/downloads/e5/64/05_70A8A51285B71FE1AC82B3099AE9E564.zip'),
    ('miele_kfmc3858fd', 'manufacturer.zip', 'https://media.miele.com/downloads/a5/64/03_70A8A51285B71FE1AC8273C8621BA564.zip'),
    ('miele_kwt6722is', 'product_sheet.pdf', 'https://media.miele.com/downloads/n-/us/FS_11329860_USE_US-en-US.pdf'),
    ('miele_kwtus7172f', 'product_sheet.pdf', 'https://media.miele.com/downloads/n-/us/FS_12519520_USE_US-en-US.pdf'),
    ('miele_kfmc3858fd', 'product_sheet.pdf', 'https://media.miele.com/downloads/n-/us/FS_12489440_USE_US-en-US.pdf'),
    ('miele_km3054_1g', 'product_sheet.pdf', 'https://media.miele.com/downloads/n-/us/FS_11766750_USE_US-en-US.pdf'),
    ('miele_h7270bm', 'product_sheet.pdf', 'https://media.miele.com/downloads/n-/us/FS_11968190_USE_US-en-US.pdf'),
    ('miele_g5051scvi', 'product_sheet.pdf', 'https://media.miele.com/downloads/n-/us/FS_11636710_USE_US-en-US.pdf'),
]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(fetch, ASSETS))
(ROOT / 'source_downloads_more.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
for r in results:
    print(json.dumps({k:v for k,v in r.items() if k in ('item','ok','error','entries','size')}))

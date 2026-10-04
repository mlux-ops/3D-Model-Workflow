"""Fetch explicit variant and primary manufacturer pages without authentication."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from collect_sources import fetch
ROOT = Path(__file__).resolve().parents[1]
GROUPS = {g['key']: g for g in json.loads((ROOT / 'GROUPS.json').read_text())['groups']}
URLS = {
    '57670WTBK': ['https://www.maximlighting.com/product/indoor-lighting/flush-mounts/trim-16-rd-led-flush-mount-3000k/57670WTBK', 'https://www.maximlighting.com/photometric'],
    'KZC1009522': ['https://kuzcolighting.com/products/motif-mp75121-kuzco'],
    'KZC1193209': ['https://www.lightology.com/index.php?module=prod_detail&prod_id=1193209', 'https://kuzcolighting.com/products/cedar-ws52505-kuzco'],
    'KZC1285334': ['https://www.lightology.com/index.php?module=prod_detail&prod_id=1285332&option_id=1285334'],
    'VCS1537517': ['https://www.lightology.com/index.php?module=prod_detail&prod_id=1537513&option_id=1537517'],
    'SEE1486624': ['https://www.lightology.com/index.php?module=prod_detail&prod_id=880817&option_id=1486624'],
    'PBL1034468': ['https://pablodesigns.com/product/sky-dome'],
    'PBL1129156': ['https://pablodesigns.com/product/sky-flush', 'https://www.bimobject.com/en-us/pablo-designs/product/sky-dome-flush'],
    'DP-WS-S1-AA04-30-10_TRIAC_120V-IP65': ['https://rbw.com/products/dimple-sconce/dimple-sconce'],
    'HNM1353351': ['https://hollisandmorris.com/products/oyster-sconce2'],
    '700BCTRS3C-LED930': ['https://www.visualcomfort.com/us/p/tris-3-light-bath-700bctrs3'],
    '700TRSPPYL1RNB-LED930': ['https://www.visualcomfort.com/us/p/pylon-1-light-pendant-700trsppyl1'],
}
jobs = [(k, GROUPS[k]['canonical_item'], 10 + i, u) for k, urls in URLS.items() for i, u in enumerate(urls)]
results = []
with ThreadPoolExecutor(max_workers=4) as pool:
    for future in as_completed([pool.submit(fetch, j) for j in jobs]):
        r = future.result()
        results.append(r)
        print(r['group'] + ' | ' + (r.get('error') or r.get('title', ''))[:180], flush=True)
(ROOT / 'OEM_COLLECTION.json').write_text(json.dumps(results, indent=2), encoding='utf-8')

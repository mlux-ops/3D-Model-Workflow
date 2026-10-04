"""Collect primary product pages and public, explicitly linked native downloads."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import json, re, sys
sys.stdout.reconfigure(errors='replace')
from collect_sources import fetch
from download_resource import download
ROOT=Path(__file__).resolve().parents[1]
groups={g['key']:g for g in json.loads((ROOT/'GROUPS.json').read_text())['groups']}
urls={
'KZC1009570':'https://kuzcolighting.com/products/trinity-pd62014-kuzco',
'KZC1403797':'https://kuzcolighting.com/products/stephord-ws97204-kuzco',
'KZC1009577':'https://kuzcolighting.com/products/motif-pd75027-kuzco',
'KZC780336':'https://kuzcolighting.com/products/rona-vl17024-kuzco',
'KZC862138':'https://kuzcolighting.com/products/pandora-ws25118-kuzco',
'KZC610420':'https://kuzcolighting.com/products/vista-ew22109-kuzco',
'KZC1285334':'https://kuzcolighting.com/products/vera-vl20338-kuzco',
'TLG604508':'https://www.visualcomfort.com/us/p/milan-24-bath-700bcmln24',
'VCS1537517':'https://www.visualcomfort.com/us/p/silas-large-sconce-slw1102',
'KRK1205030':'https://www.tomkirk.com/shop/reed-wall-light/',
'DCW1122128':'https://www.dcwservices.fr/en/focus/4320-focus-x3.html',
'NEIG-613941':'https://us.busterandpunch.com/products/exhaust-pendant-cross-graphite',
'4BEMW_SWW5_90CRI_M6':'https://www.acuitybrands.com/products/detail/1897044/juno/e-series-led-trim-kit/4in-5-and-6in-switchable-white-led-downlights-in-smooth-or-baffle-trim-styles',
}
results=[]
def collect(key,url):
    folder=ROOT/groups[key]['canonical_item']/'source'
    for name in ['page_20_resources.json','page_20_error.json']:
        path=folder/name
        if path.exists():return json.loads(path.read_text(encoding='utf-8'))
    return fetch((key,groups[key]['canonical_item'],20,url))
with ThreadPoolExecutor(max_workers=4) as pool:
    for future in as_completed([pool.submit(collect,key,url) for key,url in urls.items()]):
        r=future.result();results.append(r)
        print(r['group']+' | '+(r.get('error') or r.get('title',''))[:130],flush=True)
(ROOT/'MANUFACTURER_COLLECTION.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
downloads=[]
for r in results:
    for link in r.get('technical_links',[]):
        if re.search(r'\.rfa(?:\?|$)|\.zip(?:\?|$)',link['url'],re.I) and re.search(r'revit|\.rfa',link['label']+' '+link['url'],re.I):
            filename='OEM_'+Path(urlparse(link['url']).path).name
            target=ROOT/groups[r['group']]['canonical_item']/'source'/filename
            if target.exists():continue
            downloads.append(download(r['group'],link['url'],filename,r['url']))
(ROOT/'MANUFACTURER_NATIVE_DOWNLOADS.json').write_text(json.dumps(downloads,indent=2),encoding='utf-8')

"""Retain remaining primary public pages and their linked technical downloads."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib.request import Request,urlopen
import sys,json,re,gzip
from collect_sources import fetch
from download_resource import download
sys.stdout.reconfigure(errors='replace')
ROOT=Path(__file__).resolve().parents[1]
groups={g['key']:g for g in json.loads((ROOT/'GROUPS.json').read_text())['groups']}
urls={
'SKL924074':'https://www.sklo.com/light/hold-sconce/',
'BOM1273301':'https://www.bomma.cz/lighting/dew-drops/',
'VIS1256139':'https://vistosi.it/prodotti-lampade-vetro/faro-sp/',
'VIS1486649':'https://vistosi.it/prodotti-lampade-vetro/jube-ap/',
'ORION_TUBE_UNSPECIFIED':'https://leebroom.com/lighting/orion-tube-light-polished-gold/',
'RG-C811A':'https://iaq.na.panasonic.com/resources/resource-center/bim-library',
'HIN1284470':'https://www.hinkley.com/28914bk-ll.html',
'AMB-MB-56-EB-870-CC':'https://modernfan.com/ambit/',
'MFR918914':'https://www.modernforms.com/product/zephyr/',
'MKL1417874':'https://www.minkagroup.net/3114-732-l.html',
'SID660347':'https://www.lodes.com/en/products/a-tube-nano/',
'SEE1486624':'https://seeddesignusa.com/products/castle-muse-pendant',
'ARC1334006':'https://www.artcraftlighting.com/products/ac11976sm-modena-6-light-chandelier',
}
def collect(key,url):
    folder=ROOT/groups[key]['canonical_item']/'source'
    for name in ['page_30_resources.json','page_30_error.json']:
        if (folder/name).exists():return json.loads((folder/name).read_text())
    return fetch((key,groups[key]['canonical_item'],30,url))
results=[]
with ThreadPoolExecutor(max_workers=4) as pool:
    for future in as_completed([pool.submit(collect,k,u) for k,u in urls.items()]):
        r=future.result();results.append(r)
        print(r['group']+' | '+(r.get('error') or r.get('title',''))[:120],flush=True)
(ROOT/'REMAINING_PRIMARY.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
for key,url,name in [
 ('KRK1205030','https://www.tomkirk.com/site/assets/files/7382/tom_kirk_lighting-reed_wall_light.pdf','Reed_manufacturer_spec.pdf'),
 ('RG-C811A','https://ftp.panasonic.com/ventilationfan/installation/rg-c811a_rg-c811ha_eng.pdf','Panasonic_RG-C811A_installation.pdf'),
 ('MXG1933070','https://nola.gov/getattachment/NEXT/City-Planning/Meetings/Previous-Years-Meetings/Previous-Years/2024-Year/January/Design-Advisory-Committee/1-17-2024-10-00-00-AM/Item-3_.pdf/','Published_Lumens_Silvio_spec_packet.pdf')]:
    if not (ROOT/groups[key]['canonical_item']/'source'/name).exists():download(key,url,name,url)
folder=ROOT/'B3-2__7086825876815748/source/frontend_reference'
for endpoint in ['/blocks/product-details/product-details.js','/blocks/product-details-custom/ProductDetailsSidebar.js','/configs/us/config-prod.json']:
    try:
        with urlopen(Request('https://www.visualcomfort.com'+endpoint,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as r:data=r.read(5*1024*1024)
        if data[:2]==b'\x1f\x8b':data=gzip.decompress(data)
        name=endpoint.rsplit('/',1)[1];(folder/name).write_bytes(data)
        text=data.decode('utf-8',errors='replace')
        print(endpoint)
        for line in text.splitlines():
            if re.search(r'technical|resource|media|cdn|document|Download|\.js',line,re.I):print(line[:300])
    except Exception as exc:print(endpoint+' | '+str(exc))

"""Resolve public technical resource links and retain validated archive sources."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlparse
import gzip,json,re,sys,zipfile
from download_resource import download
sys.stdout.reconfigure(errors='replace')
ROOT=Path(__file__).resolve().parents[1]
groups={g['key']:g for g in json.loads((ROOT/'GROUPS.json').read_text())['groups']}
folder=ROOT/'B3-2__7086825876815748/source/frontend_reference'
endpoint='https://www.visualcomfort.com/blocks/product-details/slots/InfoContent.js'
with urlopen(Request(endpoint,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as response:data=response.read(3*1024*1024)
if data[:2]==b'\x1f\x8b':data=gzip.decompress(data)
(folder/'InfoContent.js').write_bytes(data)
for line in data.decode('utf-8',errors='replace').splitlines():
    if re.search(r'media|resource|document|download|\.js',line,re.I):print(line[:350])
for key,relative in [('700BCTRS3C-LED930','revit/t/r/rv_tris_3-light_bath.zip'),('TLG604508','revit/m/i/rv_milan_24_bath.zip')]:
    target=ROOT/groups[key]['canonical_item']/'source'/('OEM_'+Path(relative).name)
    if not target.exists():
        r=download(key,'https://www.visualcomfort.com/media/docs/'+relative,target.name,
                   'Published relative technical resource on the primary product page; /media/docs/ base observed in public product frontend.')
        if target.exists():print(target.name+' | valid_zip='+str(zipfile.is_zipfile(target)))
records=[]
for name in ['OEM_COLLECTION.json','MANUFACTURER_COLLECTION.json','REMAINING_PRIMARY.json']:
    records.extend(json.loads((ROOT/name).read_text()))
for record in records:
    if record['group'] not in ['SKL924074','BOM1273301','DCW1122128','VIS1256139','VIS1486649','SID660347','MKL1417874','SEE1486624','RG-C811A']:continue
    print('\n'+record['group'])
    for link in record.get('technical_links',[]):
        if re.search(r'\.(zip|rfa|pdf|stp|3ds|obj)(?:\?|$)|attachment|bimsmith',link['url'],re.I):
            print((link['label']+' | '+link['url'])[:500])

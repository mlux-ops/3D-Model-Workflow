"""Read public product resources without accounts or acceptance flows."""
import concurrent.futures
import html
import json
import re
import urllib.request
from pathlib import Path
from source_fetch import ROOT, fetch

MODELS=json.loads((ROOT/'custom_models.json').read_text(encoding='utf-8'))

def collect(model):
    folder=ROOT/model['slug']/'source'
    record={'slug':model['slug'],'url':model['spec_url']}
    if model['brand'] not in ('GE','Summit'):
        return None
    try:
        cached=folder/'official_page.html'
        if cached.exists():
            raw=cached.read_text(encoding='utf-8')
        else:
            request=urllib.request.Request(model['spec_url'],headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(request,timeout=40) as response:
                raw=response.read().decode('utf-8',errors='replace')
            cached.write_text(raw,encoding='utf-8')
        raw=html.unescape(raw)
        images=re.findall(r'<meta[^>]*(?:property|name)=[\"\x27]og:image[\"\x27][^>]*content=[\"\x27]([^\"\x27]+)',raw)
        record['images']=images
        record['contexts']=[]
        for m in re.finditer(r'CAD Files 3D|Quick Specs|\.rfa|\.dwg|\.zip|_pdf|\.pdf',raw,re.I):
            excerpt=raw[max(0,m.start()-160):m.end()+200]
            if excerpt not in record['contexts']:
                record['contexts'].append(excerpt)
        if images:
            record['image_download']=fetch((model['slug'],'official_product.jpg',images[0]))
        record['ok']=True
        (folder/'resource_discovery.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    except Exception as exc:
        record.update(ok=False,error=str(exc))
    return record

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    records=[r for r in pool.map(collect,MODELS) if r]
(ROOT/'additional_source_search.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
for r in records:
    print(json.dumps({'slug':r['slug'],'ok':r['ok'],'error':r.get('error'),'images':r.get('images'), 'contexts':r.get('contexts',[])[:16]}))

for path in ROOT.glob('thermador*/source/official_page.html'):
    raw=path.read_text(encoding='utf-8')
    urls=sorted(set(re.findall(r'https://media3\.bsh-group\.com/Documents/[^\s\"\\<>]+\.pdf',raw)))
    print(json.dumps({'slug':path.parent.parent.name,'pdf_urls':urls}))

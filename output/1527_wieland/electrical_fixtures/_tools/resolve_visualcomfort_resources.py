"""Read public frontend configuration to resolve published relative file URLs."""
from pathlib import Path
from urllib.request import urlopen,Request
import re,json
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'B3-2__7086825876815748/source/frontend_reference'
folder.mkdir(exist_ok=True)
results=[]
for name in ['configs.js','commerce.js','scripts.js']:
    url='https://www.visualcomfort.com/scripts/'+name
    with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as response:
        data=response.read(3*1024*1024)
    path=folder/name;path.write_bytes(data)
    text=data.decode('utf-8',errors='replace')
    matches=[]
    for line in text.splitlines():
        if re.search(r'resource|media|technical|pdp|product.details|\.js',line,re.I):
            matches.append(line[:350])
    results.append({'url':url,'path':str(path),'matches':matches[:35]})
print(json.dumps(results,indent=2))

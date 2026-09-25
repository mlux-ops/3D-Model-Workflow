import os,re,json,urllib.request,hashlib,concurrent.futures
from pathlib import Path
root=Path(__file__).resolve().parents[1]
items=[('f09_1254269','1254269','1254270'),('f11_1476233','1476233','1476232')]
def task(item):
    folder,product,option=item;dest=root/folder/'prime_sources';dest.mkdir(parents=True,exist_ok=True)
    page='https://www.lightology.com/index.php?module=prod_detail&prod_id='+product+'&option_id='+option
    url='https://www.lightology.com/img/prod/original/'+option+'.jpg';manifest=[]
    for target,name in [(page,'product.html'),(url,'product.jpg')]:
        path=dest/name
        try:
            if path.exists():data=path.read_bytes()
            else:
                with urllib.request.urlopen(urllib.request.Request(target,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as r:data=r.read()
                path.write_bytes(data)
            manifest.append({'url':target,'path':str(path),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
            if name=='product.html':
                text=data.decode('utf8','replace')
                links=sorted(set(re.findall(r'(?:href|src)=[\"\']([^\"\']+(?:\.pdf|\.jpg|\.png|\.rfa)[^\"\']*)',text,re.I)))
                relevant=[x for x in links if '/prod/' in x or 'madame' in x.lower() or 'mizu' in x.lower()]
                (dest/'discovered_links.json').write_text(json.dumps(relevant,indent=2))
                print(folder+' links='+json.dumps(relevant[:40]))
        except Exception as error:
            manifest.append({'url':target,'error':str(error)})
            with (root.parents[1]/'PROJECT_MEMORY.md').open('a',encoding='utf8') as f:f.write('\n- 2026-09-23 '+folder+' reference preparation error: '+str(error)+' for '+target+'; unresolved, preserve other sources.\n')
    (dest/'manifest.json').write_text(json.dumps(manifest,indent=2))
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(task,items))
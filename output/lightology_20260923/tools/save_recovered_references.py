import os,json,urllib.request,re,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
items=[('f04_1149899','https://www.lightology.com/index.php?module=prod_detail&prod_id=1149899',['https://www.lightology.com/img/prod/original/1149899.jpg','https://www.lightology.com/img/prod/original/forked-shade-pend-bp-add3.jpg']),('f06_1418164','https://www.lightology.com/index.php?module=prod_detail&prod_id=1418164&option_id=1418168',['https://www.lightology.com/img/prod/original/1418168.jpg'])]
for folder,page,images in items:
    dest=root/folder/'references';dest.mkdir(parents=True,exist_ok=True)
    rows=[]
    for url in [page]+images:
        name='lightology_product.html' if url==page else url.rsplit('/',1)[-1]
        target=dest/name
        try:
            if target.exists():data=target.read_bytes()
            else:
                request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
                with urllib.request.urlopen(request,timeout=30) as response:data=response.read()
                target.write_bytes(data)
            rows.append({'url':url,'file':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
            if url==page:
                html=data.decode('utf-8','replace')
                refs=sorted(set(re.findall(r'(?:href|src)=[\"\']([^\"\']+(?:\.pdf|\.rfa|\.dwg)[^\"\']*)',html,re.I)))
                print(folder+' technical_links='+json.dumps(refs))
        except Exception as error:
            rows.append({'url':url,'error':str(error)})
            with (root.parents[1]/'PROJECT_MEMORY.md').open('a',encoding='utf-8') as log:log.write('\n- 2026-09-23 '+folder+' reference download failed: '+str(error)+'; URL '+url+'. Cause unconfirmed; inspect or use available preserved references.\n')
    (dest/'DOWNLOAD_MANIFEST.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    print(folder+' saved='+str(sum('file'in r for r in rows)))
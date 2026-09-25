import urllib.request,json,sys,concurrent.futures
from pathlib import Path
root=Path(__file__).resolve().parents[1]
urls=[('f09_1254269','https://www.lightology.com/img/prod/original/IF-madame-wall-spec.png'),('f09_1254269','https://www.lightology.com/img/prod/pdf/IF-IM_288.10_R02-092723.pdf'),('f09_1254269','https://www.lightology.com/img/prod/original/IF-madame-wall-morocco-grafene-add.jpg'),('f11_1476233','https://www.lightology.com/img/prod/original/terz-mizu-3lt-pendant-gold-add.jpg'),('f11_1476233','https://www.lightology.com/img/prod/original/1476233.jpg'),('f11_1476233','https://www.lightology.com/img/prod/original/terz-mizu-multi-light-spec.png')]
rows=[]
def one(item):
    folder,url=item;p=root/folder/'prime_sources'/url.rsplit('/',1)[-1]
    try:
        if not p.exists():
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as r:p.write_bytes(r.read())
        return {'folder':folder,'url':url,'path':str(p),'bytes':p.stat().st_size}
    except Exception as e:return {'folder':folder,'url':url,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(one,urls))
(root/'tools'/'stalled_asset_downloads.json').write_text(json.dumps(rows,indent=2))
for row in rows:
    print(json.dumps(row))
    if 'error' in row:
        with (root.parents[1]/'PROJECT_MEMORY.md').open('a',encoding='utf8') as f:f.write('\n- 2026-09-23 source asset download error '+row['folder']+': '+row['error']+' URL '+row['url']+'; preserve alternative photographs and review exact selection.\n')
sys.path.insert(0,str(root/'tools'/'pdf_runtime'));import pymupdf
p=root/'f09_1254269'/'prime_sources'/'IF-IM_288.10_R02-092723.pdf'
if p.exists():
    d=pymupdf.open(p)
    for i,page in enumerate(d):
        page.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(p.parent/('Madame_Install_%d.png'%(i+1)))
        print('MADAME PDF PAGE',i+1,page.get_text()[:1000])
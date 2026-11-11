"""Collect two source-backed exact F&D product illustrations for NEW R036 proposals.

Only digital product image downloads; not listing photos, samples, orders or outreach.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from io import BytesIO
from PIL import Image,ImageOps
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables'/'assets'/'tile_thumbs'
OUT.mkdir(parents=True,exist_ok=True)
provenance=OUT/'provenance.json'
d=json.loads(provenance.read_text(encoding='utf-8'))
items={
 'pienza':('110850387','pienza-terra-matte-porcelain-tile',
  'https://www.flooranddecor.com/porcelain-tile/pienza-terra-matte-porcelain-tile-110850387.html',
  'Exact SKU 110850387 product-image illustration; digital 24x48 tile color/pattern, not delivered lot or installed layout'),
 'derossi':('100996800','de-rossi-ivory-matte-porcelain-tile',
  'https://www.flooranddecor.com/porcelain-tile/de-rossi-ivory-matte-porcelain-tile-100996800.html',
  'Exact SKU 100996800 product-image illustration; digital 24x24 terrazzo pattern, not a tile sample or delivered shade'),
}
for key,(sku,slug,page,note) in items.items():
    source=f'https://i8.amplience.net/i/flooranddecor/{sku}_{slug}_display?fmt=auto&qlt=85'
    url=source.replace('fmt=auto','fmt=jpg')
    dst=OUT/(key+'.jpg')
    if not dst.exists():
        request=Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'image/jpeg,image/png,image/webp,*/*'})
        with urlopen(request,timeout=25) as response:
            assert response.status==200
            data=response.read(6000000)
        assert len(data)>1000,(key,len(data))
        with Image.open(BytesIO(data)) as im:
            im.load()
            assert im.width>=200 and im.height>=200
            im=ImageOps.exif_transpose(im).convert('RGB')
            im.thumbnail((450,450),Image.Resampling.LANCZOS)
            im.save(dst,'JPEG',quality=87,optimize=True)
    with Image.open(dst) as img:
        img.verify()
    with Image.open(dst) as img:
        dims=list(img.size)
    d[key]={'source_url':source,'retrieved_url':url,'maker_product_page':page,
            'local_thumbnail':'deliverables/assets/tile_thumbs/'+key+'.jpg',
            'image_size':dims,'observation_date':'2026-11-07',
            'interpretation_limit':note}
    print(key,sku,dims,dst.stat().st_size,flush=True)
emerald_src='https://cdn.prod.website-files.com/6508c8490fee3dfe75080d5e/69a9eb99e5d9113482d0e6e5_emerald.png'
emerald_dst=OUT/'emerald.jpg'
if not emerald_dst.exists() or emerald_dst.stat().st_size<4000:
    request=Request(emerald_src,headers={'User-Agent':'Mozilla/5.0','Accept':'image/png,image/jpeg,image/webp,*/*'})
    with urlopen(request,timeout=25) as response:
        assert response.status==200
        data=response.read(6000000)
    with Image.open(BytesIO(data)) as im:
        im.load()
        assert im.width>=150 and im.height>=150
        im=ImageOps.exif_transpose(im).convert('RGB')
        im.thumbnail((450,450),Image.Resampling.LANCZOS)
        im.save(emerald_dst,'JPEG',quality=87,optimize=True)
with Image.open(emerald_dst) as im:
    dims=list(im.size)
d['emerald']={'source_url':emerald_src,'retrieved_url':emerald_src,
              'maker_product_page':'https://www.elmsurfaces.com/product/emerald-tones',
              'local_thumbnail':'deliverables/assets/tile_thumbs/emerald.jpg',
              'image_size':dims,'observation_date':'2026-11-07',
              'interpretation_limit':'Elm maker Emerald 2x20 product-page image, digital installation/pattern illustration not a physical shade/lot sample'}
print('emerald exact maker-photo',dims,emerald_dst.stat().st_size,flush=True)
provenance.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS exact SKU product-photo illustration provenance for R036, existing assets retained')

"""Collect only individually sourced tile PRODUCT images used by the 13 owner reviews.

Not listing photos, not samples and not procurement. One original URL per maker
product/collection, reduced to 450x450 JPEG for small local preview thumbnails.
Each provenance entry states when maker photo might show different format/variant.
No third-party or assumed product-image URLs. Do not collect listing photos.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
from PIL import Image,ImageOps
from io import BytesIO
import json
import importlib.util
from datetime import date

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('owner',ROOT/'scratch'/'build_r033_owner_review.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
OUT=ROOT/'deliverables'/'assets'/'tile_thumbs'
OUT.mkdir(parents=True,exist_ok=True)
notes={
 'bone':'Maker Cortar Bone product-page image; verify actual 24x48 FLAT Soft variant before accepting',
 'clay':'Maker Cortar Clay product-page image depicts 60x60 format; color illustration ONLY, not selected 24x48 flat geometry',
 'charcoal':'Maker Cortar Charcoal project image; installation illustration not exact selected-size confirmation',
 'sapphire':'Elm Tones Sapphire maker product image, actual color/lot sample needed',
 'copper':'Elm Tones Copper maker product image, actual color/lot sample needed',
 'sandstone':'Elm Sandstone maker page image filename includes copper; possible combined color composition, NOT exact selected color proof',
 'earth':'Elm Vera Forma Earth Lines maker product-page image, relief/actual 2x10 variant sample needed',
 'indigo':'Elm Indigo Edge maker collection image containing multiple related variants; selected 6x6 finish unproved in photo',
 'haze':'Elm Haze Camel maker photo; proposed Camel/Wheat blend NOT visually certified by Camel-only image',
 'luxe':'Floor & Decor exact 101317949 displayed product image, digital photo only',
 'riviera':'Floor & Decor exact 101487775 displayed product image, digital photo only',
 'perimeter':'Floor & Decor exact 101239218 displayed product image, digital photo only',
 'purity':'Floor & Decor exact 100507722 displayed product image, digital photo only',
 'antique':'Floor & Decor exact 100507706 displayed product image, digital photo only',
}
assert set(notes)==set(mod.I)
manifest={}
for key,url in mod.I.items():
  u=urlsplit(url)
  assert u.scheme=='https' and u.hostname in {'cdn.prod.website-files.com','i8.amplience.net'},(key,url)
  requested_url=url.replace('fmt=auto','fmt=jpg') if u.hostname=='i8.amplience.net' else url
  target=OUT/(key+'.jpg')
  if not target.is_file():
    req=Request(requested_url,headers={'User-Agent':'Mozilla/5.0','Accept':'image/jpeg,image/png,image/webp,*/*'})
    with urlopen(req,timeout=20) as r:
      assert r.status==200,(key,r.status)
      b=r.read(8000000)
      mime=r.headers.get('Content-Type','')
    assert len(b)>700,(key,len(b),mime)
    with Image.open(BytesIO(b)) as im:
      im.load()
      assert im.width>=90 and im.height>=90,(key,im.size)
      im=ImageOps.exif_transpose(im).convert('RGB')
      im.thumbnail((450,450),Image.Resampling.LANCZOS)
      im.save(target,'JPEG',quality=86,optimize=True)
  with Image.open(target) as im:
    assert im.width>=90 and im.height>=90,(key,im.size)
    width,height=im.size
  manifest[key]={'source_url':url,'retrieved_url':requested_url,'maker_product_page':mod.U[key],
                 'local_thumbnail':'deliverables/assets/tile_thumbs/'+key+'.jpg',
                 'image_size':[width,height],'observation_date':'2026-11-07',
                 'interpretation_limit':notes[key]}
  print(key,width,height,target.stat().st_size,flush=True)
(OUT/'provenance.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS',len(manifest),'tile product image thumbnails, all visually illustrative, no listing-image collection')

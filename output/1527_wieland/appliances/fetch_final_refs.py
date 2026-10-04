"""Preserve exact published cut sheets and CAD references discovered on official pages."""
import concurrent.futures
import json
import re
import sys
from source_fetch import ROOT,fetch
sys.path.insert(0,str(ROOT/'_python_deps'))
import pymupdf

ASSETS=[
 ('ge_gfw550ssnww','product_sheet.pdf','https://images.salsify.com/image/upload/s--QojF4Tcy--/e04777f39886e35f1e867cdfc522c90b23c23daf.pdf'),
 ('ge_gfd55gssnww','product_sheet.pdf','https://images.salsify.com/image/upload/s--VBxQtwSo--/5bb2a02635c02de483dad44b5d164513c2baf6de.pdf'),
 ('ge_gfw550ssnww','official_3D.dwg','https://images.salsify.com/raw/upload/s--100n_wPP--/xhnym606jjrsbv8qgioq.dwg'),
 ('ge_gfd55gssnww','official_3D.dwg','https://images.salsify.com/raw/upload/s--Ghj2_qby--/o7ndvfxdcod1hde4qmaf.dwg'),
 ('summit_sdhwc98pnr','product_sheet.pdf','https://www.summitappliance.com/brochure/8799.pdf'),
 ('summit_sdhwc98pnr','assembly.pdf','https://drtr5fjqqz6ee.cloudfront.net/uploads/fsi/drawing/file/16133/SDHWC98PNR-Assembly.pdf')
]
for path in ROOT.glob('thermador*/source/official_page.html'):
    raw=path.read_text(encoding='utf-8')
    urls=sorted(set(re.findall(r'https://media3\.bsh-group\.com/Documents/[^\s\"\\<>]+Specifications\.pdf',raw)))
    if urls:
        ASSETS.append((path.parent.parent.name,'product_sheet.pdf',urls[0]))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    results=list(pool.map(fetch,ASSETS))
(ROOT/'final_reference_downloads.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
for path in ROOT.glob('*/source/*.pdf'):
    if path.name not in ('product_sheet.pdf','assembly.pdf'):
        continue
    doc=pymupdf.open(path)
    content=[]
    for i,page in enumerate(doc):
        text=page.get_text()
        content.append('PAGE %d\n%s'%(i+1,text))
        if i<3:
            page.get_pixmap(matrix=pymupdf.Matrix(1.7,1.7)).save(str(path.parent/('%s_page_%d.png'%(path.stem,i+1))))
    (path.parent/(path.stem+'.txt')).write_text('\n'.join(content),encoding='utf-8')
    if path.parent.parent.name.startswith('thermador'):
        text=' '.join(content)
        match=re.search(r'(?:Overall Appliance Dimensions|Overall Dimensions|Product Dimensions|Dimensions of the product)',text,re.I)
        print(json.dumps({'item':path.parent.parent.name,'pages':len(doc),'dimension_text':text[match.start():match.start()+450] if match else 'Read source text/diagram'}))
for r in results:
    print(json.dumps({k:v for k,v in r.items() if k in ('item','ok','error','size')}))

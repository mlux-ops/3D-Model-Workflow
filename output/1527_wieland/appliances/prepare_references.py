"""Fetch manufacturer-authored cut sheets and render local dimensional references."""
import json
import sys
from pathlib import Path
from source_fetch import fetch, ROOT
sys.path.insert(0, str(ROOT / '_python_deps'))
ASSETS = [
 ('lg_dlgx4001b','product_sheet.pdf','https://content.abt.com/documents/129668/SpecificationSheet-DLXX400X-1.pdf'),
 ('tradewind_i32363rc','product_sheet.pdf','https://linqcdn.avbportal.com/documents/3512c644-ff49-413e-aaf5-5805aa9aad84.pdf'),
]
results=[]
for a in ASSETS:
    target = ROOT / a[0] / 'source' / a[1]
    result = dict(item=a[0],ok=True,size=target.stat().st_size,url=a[2],cached=True) if target.exists() else fetch(a)
    results.append(result)
(ROOT/'reference_downloads.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
try:
    import fitz
    for slug in ['miele_km3054_1g','tradewind_i32363rc','lg_wm4000hba']:
        path=ROOT/slug/'source'/'product_sheet.pdf'
        if not path.exists():
            continue
        doc=fitz.open(path)
        text=[]
        for i,page in enumerate(doc):
            text.append('PAGE %d\n%s' % (i+1,page.get_text()))
            page.get_pixmap(matrix=fitz.Matrix(1.8,1.8)).save(str(path.parent/('reference_page_%d.png'%(i+1))))
        (path.parent/'product_sheet.txt').write_text('\n'.join(text),encoding='utf-8')
        print(json.dumps({'item':slug,'pages':len(doc),'rendered':True}))
except ImportError as exc:
    print(json.dumps({'render_error':str(exc)}))
for r in results:
    print(json.dumps({k:v for k,v in r.items() if k in ('item','ok','error','size')}))

"""Retrieve publicly served manufacturer specification PDFs, verifying signatures and SKU text."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import re
import sys
import urllib.request

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
sys.path.insert(0,str(REPO/'output/lightology_20260923/tools/pdf_runtime'))
import pymupdf
groups=json.loads((ROOT/'groups.json').read_text(encoding='utf-8'))
exact={
 'T704110-BNXLHP':'https://media.brizo.com/SpecSheet/BSP-B-T704110-LHP%20Rev%20B.pdf',
 '653110LF-BNXLHP':'https://media.brizo.com/SpecSheet/BSP-L-653110LF-LHP%20Rev%20A.pdf'
}

def recover(group):
    sku=group['sku'];key=group['key'];prefix=sku.split('-')[0]
    folder=ROOT/key/'downloads';folder.mkdir(parents=True,exist_ok=True)
    existing=[]
    for pdf in folder.glob('*.pdf'):
        try:
            doc=pymupdf.open(pdf)
            text=''.join(page.get_text() for page in doc)
            if prefix in text:existing.append(str(pdf))
        except Exception:
            pass
    if existing:return {'key':key,'sku':sku,'existing':existing}
    candidates=[]
    if sku in exact:candidates.append(exact[sku])
    variants=[sku]
    for finish in ['BNX','GL']:
        if finish in sku:
            variants.extend([sku.replace(finish,'BL'),sku.replace(finish,'PC')])
    if '-BL' in sku:variants.append(sku.replace('-BL','-PC'))
    for model in dict.fromkeys(variants):
        candidates.append('https://bravo.requested-info.com/brands/BRZ/documents/specSheets/'+model+'_Spec.pdf')
    attempts=[]
    for url in candidates:
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=20) as response:
                data=response.read()
            if not data.startswith(b'%PDF-'):raise ValueError('Response is not PDF')
            doc=pymupdf.open(stream=data,filetype='pdf')
            content=''.join(page.get_text() for page in doc)
            if prefix not in content:
                raise ValueError('Requested model prefix absent from PDF text')
            filename=urllib.parse.unquote(url.rsplit('/',1)[-1]).replace(' ','_')
            pdf=folder/filename
            pdf.write_bytes(data)
            target=folder/(pdf.stem+'_pages');target.mkdir(exist_ok=True)
            for i,page in enumerate(doc):
                (target/('page_%02d.txt'%(i+1))).write_text(page.get_text(),encoding='utf-8')
                page.get_pixmap(matrix=pymupdf.Matrix(2,2)).save(target/('page_%02d.png'%(i+1)))
            receipt={'key':key,'sku':sku,'url':url,'path':str(pdf),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
                     'manufacturer_document':True,'exact_finish_pdf':sku in content,'model_prefix_verified':prefix,'attempts':attempts}
            (ROOT/key/'spec_recovery.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
            return receipt
        except Exception as exc:attempts.append({'url':url,'error':type(exc).__name__+': '+str(exc)})
    receipt={'key':key,'sku':sku,'attempts':attempts,'result':'NO_VERIFIED_PDF_RECOVERED'}
    (ROOT/key/'spec_recovery.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    return receipt

selected=[g for g in groups if g['sku'] and any('brizo' in str(r.get('manufacturer','')).lower() for r in g['rows']) and ',' not in g['sku']]
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for result in pool.map(recover,selected):
        results.append(result)
        print(json.dumps({'sku':result['sku'],'path':result.get('path'),'existing':len(result.get('existing',[])),
                          'failed_attempts':len(result.get('attempts',[])),'result':result.get('result','RECOVERED')}),flush=True)
(ROOT/'brizo_spec_recovery.json').write_text(json.dumps(results,indent=2),encoding='utf-8')

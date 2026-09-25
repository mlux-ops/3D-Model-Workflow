import urllib.request,importlib.util,json,sys
from pathlib import Path
base=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(base/'tools'/'pdf_runtime'))
pdf=base/'f04_1149899'/'references'/'Forked_Manufacturer.pdf'
if not pdf.exists():
    req=urllib.request.Request('https://www.lightology.com/img/prod/pdf/NA_BP_TS_FORKED_PENDANT_SHADE__MAY_2022.pdf',headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=30) as r:pdf.write_bytes(r.read())
print('PDF_BYTES',pdf.stat().st_size)
print('LIBRARIES', {x:importlib.util.find_spec(x) is not None for x in ['fitz','PIL','pypdf']})
if importlib.util.find_spec('fitz'):
    import fitz
    doc=fitz.open(pdf)
    for i,p in enumerate(doc):
        (pdf.parent/('Forked_Page_%d.png'%(i+1))).write_bytes(p.get_pixmap(matrix=fitz.Matrix(1.8,1.8)).tobytes('png'))
        print('PAGE',i+1,p.get_text())
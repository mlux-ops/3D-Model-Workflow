import sys,json,urllib.request,re
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'/'pdf_runtime'));import pymupdf
folder=root/'f01_816712'/'sources'
url='https://www.visualcomfort.com/us/p/maverick-52-led-ceiling-fan-3mavr52d?selected_product=3MAVR52BKBKD'
req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
with urllib.request.urlopen(req,timeout=30) as r:html=r.read()
(folder/'visualcomfort_current_page.html').write_bytes(html)
text=html.decode('utf8','replace')
links=sorted(set(re.findall(r'https[^\s"<>]+(?:ss_3mavr52bkbkd|TS_3MAVR52BKBKD)[^\s"<>]*',text)))
print('EMBEDDED_SPEC_LINKS',links[:8])
# Manufacturer exposes relative technical_resources under the shared docs route.
pdfurl='https://www.visualcomfort.com/media/docs/spec_sheet/3/m/ss_3mavr52bkbkd.pdf'
try:
    with urllib.request.urlopen(urllib.request.Request(pdfurl,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as r:pdf=r.read()
    if not pdf.startswith(b'%PDF'):raise ValueError('Response is not a PDF')
    p=folder/'VisualComfort_3MAVR52BKBKD_Spec.pdf';p.write_bytes(pdf)
    doc=pymupdf.open(p)
    for i,page in enumerate(doc):
        page.get_pixmap(matrix=pymupdf.Matrix(2,2)).save(folder/('VisualComfort_Spec_Page%d.png'%(i+1)))
        print('PAGE',i+1,page.get_text())
    (folder/'manufacturer_height_resolution.json').write_text(json.dumps({'page':url,'spec':pdfurl,'manufacturer_overall_height_in':13.8,'retailer_height_in':19.8,'status':'manufacturer drawing to be visually reviewed'},indent=2))
except Exception as e:
    print('SPEC_DOWNLOAD_ERROR',str(e))
    with (root.parents[1]/'PROJECT_MEMORY.md').open('a',encoding='utf8') as f:f.write('\n- 2026-09-23 Maverick official spec retrieval failed: '+str(e)+'; relative resources route inferred from manufacturer page; page13.8in source remains preserved, exact drawing pending.\n')
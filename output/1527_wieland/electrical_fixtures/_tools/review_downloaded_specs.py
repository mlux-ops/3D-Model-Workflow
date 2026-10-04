"""Prepare local drawing evidence from already archived manufacturer PDFs."""
from pathlib import Path
import json, sys, re
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO / 'output/lightology_20260923/tools/pdf_runtime'))
import pymupdf as fitz
sys.stdout.reconfigure(errors='replace')
records = json.loads((ROOT/'COMPLETION_SOURCE_RECEIPTS.json').read_text())
result = []
for row in records:
    path = Path(row.get('path',''))
    if not path.is_file() or path.suffix.lower() != '.pdf':
        continue
    out = path.parent / (path.stem+'_review')
    out.mkdir(exist_ok=True)
    doc = fitz.open(path)
    texts = [page.get_text() for page in doc]
    (out/'pages.txt').write_text('\n\n'.join('PAGE %d\n%s'%(i+1,t) for i,t in enumerate(texts)),encoding='utf-8')
    for page in range(min(2,len(doc))):
        doc[page].get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(out/('page_%02d.png'%(page+1)))
    record={'path':str(path),'pages':len(doc),'review_folder':str(out),'page_text':[{'page':i+1,'text':t[:2200]} for i,t in enumerate(texts) if i<2 or re.search(r'13\.7|13\.8|56|dimension',t,re.I)]}
    result.append(record)
    print(path.stem, len(doc), 'pages')
    for entry in record['page_text']:
        print('PAGE',entry['page'],entry['text'][:1400].replace('\n',' | '))
(ROOT/'COMPLETION_SPEC_REVIEW.json').write_text(json.dumps(result,indent=2),encoding='utf-8')

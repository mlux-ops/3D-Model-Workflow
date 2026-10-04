"""Render downloaded PDF sheets through the existing local PDF runtime."""
from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
sys.path.insert(0,str(REPO / 'output/lightology_20260923/tools/pdf_runtime'))
import pymupdf
results = []
for pdf in sorted(ROOT.glob('*/downloads/**/*.pdf')):
    if pdf.name == 'hansgrohe_2026_Price_Book_en_US.pdf':
        continue
    target = pdf.parent / (pdf.stem + '_pages')
    target.mkdir(exist_ok=True)
    try:
        document = pymupdf.open(pdf)
        for i,page in enumerate(document):
            (target / ('page_%02d.txt' % (i+1))).write_text(page.get_text(),encoding='utf-8')
            png = target / ('page_%02d.png' % (i+1))
            if not png.exists():
                page.get_pixmap(matrix=pymupdf.Matrix(2,2)).save(png)
        results.append({'pdf':str(pdf.relative_to(ROOT)), 'pages':len(document), 'folder':str(target.relative_to(ROOT))})
    except Exception as exc:
        results.append({'pdf':str(pdf.relative_to(ROOT)), 'error':repr(exc)})
(ROOT / 'rendered_specs.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results))

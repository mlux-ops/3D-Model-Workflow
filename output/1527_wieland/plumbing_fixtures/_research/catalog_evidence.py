"""Save exact SKU catalog pages as text and full-page review images."""
from pathlib import Path
import json
import re
import sys

REPO = Path(__file__).resolve().parents[4]
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / 'output/lightology_20260923/tools/pdf_runtime'))
import pymupdf

catalog = ROOT / 'Hansgrohe_2026_Catalog/downloads/hansgrohe_2026_Price_Book_en_US.pdf'
groups = json.loads((ROOT / 'groups.json').read_text(encoding='utf-8'))
dest = ROOT / 'catalog_pages'
dest.mkdir(exist_ok=True)
document = pymupdf.open(catalog)
text_pages = [page.get_text() for page in document]
records = []
rendered = set()
for group in groups:
    sku = group['sku']
    if not re.fullmatch(r'\d{8}', sku):
        continue
    exact = [index for index, text in enumerate(text_pages) if sku in re.sub(r'\s+', '', text)]
    family = [index for index, text in enumerate(text_pages) if sku[:5] in re.sub(r'\s+', '', text)]
    pages = sorted(set(exact + family))
    records.append({'sku': sku, 'exact_pages': [p + 1 for p in exact], 'family_pages': [p + 1 for p in family]})
    for index in pages:
        if index in rendered:
            continue
        (dest / ('page_%03d.txt' % (index + 1))).write_text(text_pages[index], encoding='utf-8')
        image_path = dest / ('page_%03d.png' % (index + 1))
        if not image_path.exists():
            document[index].get_pixmap(matrix=pymupdf.Matrix(1.8, 1.8)).save(image_path)
        rendered.add(index)
(dest / 'index.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
print(json.dumps({'catalog_pages': len(document), 'rendered_pages': len(rendered), 'matches': records}))

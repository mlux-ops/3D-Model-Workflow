"""Render named reference PDFs for visual review, keeping the source untouched."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
sys.path.insert(0,str(REPO/'output/lightology_20260923/tools/pdf_runtime'))
import pymupdf
from PIL import Image
parser=argparse.ArgumentParser();parser.add_argument('paths',nargs='+');args=parser.parse_args()
results=[]
for value in args.paths:
    path=ROOT/value
    if path.suffix.lower()=='.pdf':
        doc=pymupdf.open(path);dest=path.parent/(path.stem+'_pages');dest.mkdir(exist_ok=True)
        for i in range(min(3,len(doc))):
            page=doc[i];scale=min(2,1800/max(page.rect.width,page.rect.height))
            page.get_pixmap(matrix=pymupdf.Matrix(scale,scale),alpha=False).save(dest/('page_%02d.png'%(i+1)))
            (dest/('page_%02d.txt'%(i+1))).write_text(page.get_text(),encoding='utf-8')
        results.append({'source':str(path),'pages':len(doc),'images':str(dest)})
    else:
        im=Image.open(path).convert('RGB');im.thumbnail((1600,1600))
        dest=path.with_name(path.stem+'_review.png');im.save(dest)
        results.append({'source':str(path),'review':str(dest),'size':im.size})
print(json.dumps(results,indent=2))

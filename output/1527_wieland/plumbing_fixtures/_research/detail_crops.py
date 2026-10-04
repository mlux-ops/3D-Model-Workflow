"""Render selected catalog technical drawings at readable vector resolution."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[3]/'output/lightology_20260923/tools/pdf_runtime'))
import pymupdf
doc=pymupdf.open(ROOT/'Hansgrohe_2026_Catalog/downloads/hansgrohe_2026_Price_Book_en_US.pdf')
crops=[(374,(198,90,335,205)),(266,(200,85,420,230)),(387,(235,100,325,220)),(386,(210,100,320,220)),
       (204,None),(274,None)]
for page,clip in crops:
    kwargs={'matrix':pymupdf.Matrix(4,4)}
    if clip:kwargs['clip']=pymupdf.Rect(*clip)
    target=ROOT/'catalog_pages'/('detail_%03d.png'%page)
    doc[page-1].get_pixmap(**kwargs).save(target)
    print(str(target))

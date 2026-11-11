from pathlib import Path
from pypdf import PdfReader, PdfWriter
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'deliverables'/'r034-13-owner-review-PROVISIONAL'
src=OUT/'R034_13_ROOM_OWNER_REVIEW_PAGES.pdf'
ids=['PH-PRIMARY','PH-BATH2','PH-BATH3','PH-BATH4','PH-POWDER','PH-WC','TX-PRIMARY','TX-BATH2','TX-BATH3','TX-BATH4','TX-POWDER','TX-POWDER2','TX-WC']
reader=PdfReader(src)
assert len(reader.pages)==len(ids),(len(reader.pages),len(ids))
for idx,(page,id) in enumerate(zip(reader.pages,ids),1):
 text=page.extract_text() or ''
 assert id in text,(idx,id,'header absent')
 assert 'OWNER TILE REVIEW' in text,(idx,id,'cover text missing')
 assert 'not a final approved selection' in text.lower(),(idx,id,'status footer absent')
 assert 'UNRESOLVED OWNER' in text,(idx,id,'open holds absent')
 assert 'MATERIAL-ONLY COST BASIS' in text,(idx,id,'cost section absent')
 if id in ('PH-WC','TX-WC'):
  assert 'R033 A' in text and 'BLOCKED' in text,(idx,id,'R033 conditional state absent')
  assert '0 SF' in text and '$0' in text,(idx,id,'standalone WC cost wrongly added')
 if id in ('PH-POWDER','TX-POWDER','TX-POWDER2'):
  assert 'R032 A' in text,(idx,id,'R032 incumbent defense absent')
 assert int(float(page.mediabox.width))==612 and int(float(page.mediabox.height))==792,(idx,id,'unexpected page size')
 writer=PdfWriter();writer.add_page(page)
 dst=OUT/(id+'.pdf')
 with dst.open('wb') as f: writer.write(f)
 assert len(PdfReader(dst).pages)==1
 print(f'{idx:02d} {id:14} 1 letter-size page; text={len(text)} chars; {dst.stat().st_size} bytes')
print('PASS: 13 unique provisional PDFs, 13/13 physical page count; text/footer and page-size checks. Visual raster QA remains separate.')

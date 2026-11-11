"""Read-only owner presentation image and source review, no downloads."""
from pathlib import Path
from html.parser import HTMLParser
import json,re
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
class P(HTMLParser):
 def __init__(self):super().__init__();self.images=[];self.links=[];self.cards=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='img':self.images.append(a)
  if tag=='a':self.links.append(a)
  if tag=='article' and 'room' in a.get('class','').split():self.cards+=1
html=ROOT/'deliverables'/'TILE_SELECTIONS_REVIEW.html'
p=P();p.feed(html.read_text(encoding='utf-8'))
assert p.cards==13,p.cards
assert len(p.images)>=30,len(p.images)
for n,img in enumerate(p.images,1):
 src=img.get('src')
 assert src and not src.startswith('http'),(n,src)
 target=ROOT/'deliverables'/src
 assert target.is_file() and target.stat().st_size>3000,(n,target)
 assert img.get('alt'),(n,'alt missing')
assert len([x for x in p.links if x.get('href','').startswith('https://')])>=30
out=ROOT/'deliverables'/'r033-13-owner-review-PROVISIONAL'
ids=['PH-PRIMARY','PH-BATH2','PH-BATH3','PH-BATH4','PH-POWDER','PH-WC','TX-PRIMARY','TX-BATH2','TX-BATH3','TX-BATH4','TX-POWDER','TX-POWDER2','TX-WC']
for id in ids:
 h=out/(id+'.html')
 q=P();q.feed(h.read_text(encoding='utf-8'))
 assert q.images,(id,'no visual source photos')
 for img in q.images:
  src=img.get('src','')
  if src.startswith('http'): continue
  target=(h.parent/src).resolve()
  assert target.is_file() and target.stat().st_size>3000,(id,src)
 pdf=PdfReader(out/(id+'.pdf'))
 assert len(pdf.pages)==1 and int(pdf.pages[0].mediabox.width)==612 and int(pdf.pages[0].mediabox.height)==792,id
 assert pdf.pages[0].images,(id,'no embedded visual images')
 assert 'not a final approved selection' in (pdf.pages[0].extract_text() or '').lower()
print('PASS: 13 HTML review cards; '+str(len(p.images))+' locally verified vendor tile thumbnails, 13 HTML owner pages with resolved image references, 13 PDFs each 1 US Letter with embedded imagery and non-final wording.')

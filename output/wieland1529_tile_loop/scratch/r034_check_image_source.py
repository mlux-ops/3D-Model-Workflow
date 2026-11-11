"""Read-only metadata check of publicly listed exact tile-product pages.

No scraping around access restrictions; if vendor blocks request, report blocked.
No files or images downloaded; this only prints product-page og:image metadata.
"""
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from html.parser import HTMLParser
from pathlib import Path
import ast, re, sys

ROOT=Path(__file__).resolve().parents[1]
t=(ROOT/'scratch'/'build_r033_owner_review.py').read_text(encoding='utf-8')
st=t.index("U = {") + len("U = ")
en=t.index("\nI=",st)
U=ast.literal_eval(t[st:en])
class Parser(HTMLParser):
  def __init__(self): super().__init__(); self.images=[]; self.titles=[];self.imgtags=[]
  def handle_starttag(self,tag,attrs):
    a=dict(attrs)
    if tag=='img':
      self.imgtags.append({k:a.get(k,'') for k in ('alt','src','srcset','data-src')})
    if tag!='meta': return
    if a.get('property') in ('og:image','og:image:secure_url') and a.get('content'):self.images.append(a['content'])
    if a.get('property')=='og:title':self.titles.append(a.get('content',''))
for k,u in U.items():
  if len(sys.argv)>1 and k not in sys.argv[1:]: continue
  try:
    req=Request(u,headers={'User-Agent':'Mozilla/5.0 (compatible; ResearchValidation/1.0)','Accept':'text/html'})
    with urlopen(req,timeout=12) as resp:html=resp.read(2500000).decode('utf-8','ignore');code=resp.status
    p=Parser();p.feed(html)
    print(k,'HTTP',code,'PAGE',p.titles[:1],'IMAGES',p.images[:2],'TAGS',[x for x in p.imgtags if k.lower() in str(x).lower()][:3],flush=True)
  except (HTTPError,URLError,TimeoutError,ValueError) as e:
    print(k,'BLOCKED',type(e).__name__,str(e)[:90],flush=True)

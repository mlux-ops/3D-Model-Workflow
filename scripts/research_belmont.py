import urllib.request,json,concurrent.futures
from html.parser import HTMLParser
from pathlib import Path
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.items=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='img' and any(k in str(d).lower() for k in ['ivory','honey','comb','1x6','bermuda','greige','jute']):self.items.append(d)
p=Path('references/belmont_tiles/web_images.json');urls=[i['url'] for i in json.loads(p.read_text())]
def get(u):
 try:
  h=urllib.request.urlopen(u,timeout=25).read().decode();s=Parser();s.feed(h);return {'url':u,'images':s.items}
 except Exception as e:return {'url':u,'error':str(e)}
res=list(concurrent.futures.ThreadPoolExecutor(6).map(get,urls));p.write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))

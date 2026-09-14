import json,urllib.request,concurrent.futures
from pathlib import Path
from PIL import Image
from io import BytesIO
p=Path('references/belmont_tiles');data=json.loads((p/'web_images.json').read_text())
jobs=[(key,d['images'][0]['src']) for key,d in zip(['soreno','honey','domino','clara','raw','jute'],data)]
def get(job):
 k,u=job
 try:
  b=urllib.request.urlopen(u,timeout=30).read();im=Image.open(BytesIO(b));(p/(k+'_original.jpg')).write_bytes(b);return {'id':k,'url':u,'pixels':im.size}
 except Exception as e:return {'id':k,'error':str(e)}
r=list(concurrent.futures.ThreadPoolExecutor(6).map(get,jobs));(p/'source_audit.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))

import urllib.request,json
from pathlib import Path
u='https://solidshape.com/products/soreno-ivory-24x48-matte-porcelain-tile.js'
d=json.load(urllib.request.urlopen(u,timeout=30));Path('references/belmont_tiles/soreno_dealer.json').write_text(json.dumps(d));print(json.dumps(d.get('images',[])))

"""Decode retained compressed public scripts for resource-base inspection."""
from pathlib import Path
import gzip,zlib,re,json
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'B3-2__7086825876815748/source/frontend_reference'
for path in folder.glob('*.js'):
    if '.decoded.' in path.name:continue
    data=path.read_bytes()
    print(path.name+' | signature '+data[:8].hex())
    if data[:2]==b'\x1f\x8b':data=gzip.decompress(data)
    elif data[:1]==b'\x78':
        try:data=zlib.decompress(data)
        except zlib.error:pass
    text=data.decode('utf-8',errors='replace')
    path.with_name(path.stem+'.decoded.js').write_text(text,encoding='utf-8')
    for line in text.splitlines():
        if re.search(r'resource|media|technical|pdp|product.details|\.js',line,re.I):
            print(line[:500].encode('ascii',errors='replace').decode())

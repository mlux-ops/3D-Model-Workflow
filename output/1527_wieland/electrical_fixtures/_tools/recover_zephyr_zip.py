"""Inspect and recover intact local ZIP entries from the official damaged archive."""
from pathlib import Path
import struct,zlib,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
path=next(ROOT.glob('*/source/Zephyr52_manufacturer_Revit_browser_headers.zip'))
data=path.read_bytes();pos=0;entries=[]
dest=path.parent/'Zephyr52_recovered_entries';dest.mkdir(exist_ok=True)
while data[pos:pos+4]==b'PK\x03\x04':
    fields=struct.unpack_from('<4s5H3I2H',data,pos)
    _,version,flags,method,tm,dt,crc,compressed,uncompressed,nlen,xlen=fields
    name=data[pos+30:pos+30+nlen].decode('utf-8',errors='replace')
    begin=pos+30+nlen+xlen
    row=dict(name=name,flags=flags,method=method,compressed=compressed,uncompressed=uncompressed,offset=pos)
    if flags&8:
        row['error']='Data descriptor requires stream inspection; not extracted';entries.append(row);break
    compressed_data=data[begin:begin+compressed]
    try:
        plain=zlib.decompress(compressed_data,-15) if method==8 else compressed_data
        row.update(actual_size=len(plain),size_pass=len(plain)==uncompressed,crc_pass=(zlib.crc32(plain)&0xffffffff)==crc)
        target=dest/name
        if not target.resolve().is_relative_to(dest.resolve()):raise ValueError('entry outside source folder')
        if row['size_pass'] and row['crc_pass'] and name.lower().endswith(('.rfa','.txt')):
            target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():target.write_bytes(plain)
            row.update(path=str(target),sha256=hashlib.sha256(plain).hexdigest())
    except Exception as exc:row['error']=str(exc)
    entries.append(row);pos=begin+compressed
result=dict(source=str(path),archive_sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),end_signature_offset=data.rfind(b'PK\x05\x06'),next_signature=data[pos:pos+20].hex(),tail=data[-40:].hex(),entries=entries)
(ROOT/'ZEPHYR_ZIP_RECOVERY.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))

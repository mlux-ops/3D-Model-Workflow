from pathlib import Path
import struct
r=Path(__file__).resolve().parent;total=0
for p in r.glob('*.stl'):
 data=p.read_bytes();n=struct.unpack_from('<I',data,80)[0];seen=set();faces=[]
 for i in range(n):
  face=data[84+50*i:134+50*i];v=struct.unpack('<12fH',face)
  key=tuple(sorted(tuple(round(q,6) for q in v[j:j+3]) for j in [3,6,9]))
  if key in seen or len(set(key))<3:total+=1;continue
  seen.add(key);faces.append(face)
 p.write_bytes(data[:80]+struct.pack('<I',len(faces))+b''.join(faces))
print('Removed duplicate or collapsed triangles:',total)

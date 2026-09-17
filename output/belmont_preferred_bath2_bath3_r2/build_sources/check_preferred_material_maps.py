"""Numerical gates, separate from required visual/native-render review."""
import json, sys, hashlib
from pathlib import Path
import numpy as np
from PIL import Image

folder = Path(sys.argv[1])
results = []
for s in json.loads((folder / 'manifest.json').read_text()):
    failures = []
    if min(s['repeat_inches']) < 180:
        failures.append('atlas is smaller than the 15-foot review surface')
    arrays = {}
    for suffix in ['Color', 'Bump', 'Roughness'] if s.get('revision') == 2 else ['Color', 'Bump']:
        p = folder/s['id']/'textures'/f"{s['id']}_{suffix}.png"
        with Image.open(p) as im:
            im.load()
            arrays[suffix] = np.asarray(im)
        if suffix=='Bump' and p.read_bytes()[24] != 16:
            failures.append('bump PNG is not 16-bit')
        a = arrays[suffix]
        if not np.array_equal(a[0], a[-1]) or not np.array_equal(a[:,0], a[:,-1]):
            failures.append(suffix + ' opposite-edge samples differ')
    if arrays['Color'].shape[:2] != arrays['Bump'].shape:
        failures.append('map dimensions differ')
    nx, ny = s.get('atlas_tiles', [2,2])
    a = arrays['Color']; h,w = a.shape[:2]; cw,ch = w//nx,h//ny
    faces = [a[y*ch+ch//8:(y+1)*ch-ch//8,x*cw+cw//8:(x+1)*cw-cw//8]
             for y in range(ny) for x in range(nx)]
    unique = len({hashlib.sha256(f.tobytes()).hexdigest() for f in faces})
    if unique != nx*ny:
        failures.append('exact duplicate tile interiors')
    results.append({'id':s['id'], 'failures':failures, 'unique_interiors':unique,
                    'tiles':nx*ny, 'repeat_inches':s['repeat_inches']})
print(json.dumps(results, indent=2))
sys.exit(int(any(r['failures'] for r in results)))

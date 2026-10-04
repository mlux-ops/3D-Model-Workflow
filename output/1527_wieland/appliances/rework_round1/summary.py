"""Bounded read-only progress output for the round-1 files."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
for c in json.loads((HERE/'configs.json').read_text()):
    p=ROOT/c['slug']/'source'/'rework_r1'
    line={'slug':c['slug']}
    for name in ['build_result','validation']:
        file=p/(name+'.json')
        if not file.exists():
            line[name]='not yet written'
            continue
        try:
            r=json.loads(file.read_text())
            line[name]={'ok':r.get('ok'),'stage':r.get('stage'),'error':r.get('error'),
                        'dimensions':r.get('placed_bounds',r.get('build_bounds',{})).get('xyz_size_mm'),
                        'delta':r.get('dimension_delta_mm'),'identity':r.get('identity_gate'),
                        'material':r.get('material_gate'),'bitmap':r.get('bitmap_gate'),
                        'previews':len(r.get('previews',[]))}
        except Exception as e:
            line[name]={'read_error':str(e)}
    print(json.dumps(line))

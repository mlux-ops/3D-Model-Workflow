"""Print current measured gates and selected source dimensional passages."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
for path in sorted(ROOT.glob('*/validation.json')):
    r=json.loads(path.read_text())
    flex=r.get('parameter_flex',[])
    print(json.dumps({'slug':r['slug'],'ok':r.get('ok'),'stage':r['stage'],
        'family_warning_count':len(r.get('warnings',[])),'project_warnings':r.get('placed_warnings',[]),
        'materials':[(p['name'],p.get('pass',p.get('substitution_pass')),p.get('material_element_references',p.get('geometry_bindings'))) for p in flex],
        'dimension_gate':r.get('dimension_gate'),'error':r.get('error','')[-400:]}))
for path in sorted(ROOT.glob('miele*/source/product_sheet.txt')):
    lines=path.read_text(encoding='utf-8').splitlines()
    excerpts=[]
    for i,line in enumerate(lines):
        if re.search(r'appliance dimensions|width in|height in|depth in',line,re.I):
            excerpts.append(' '.join(lines[i:i+4]))
    print(json.dumps({'source':str(path.relative_to(ROOT)),'dimensions':excerpts}))

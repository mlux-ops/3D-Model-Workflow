"""Summarize preserved item sources and native evidence without changing them."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
groups = json.loads((ROOT / '_research/groups.json').read_text(encoding='utf-8'))
out = []
for group in groups:
    if not group['sku']:
        continue
    key = group['key']
    validation = ROOT / key / 'validation.json'
    native = json.loads(validation.read_text(encoding='utf-8')) if validation.exists() else {}
    sources = ROOT / '_research' / key
    pdfs = [str(p.relative_to(ROOT)) for p in sources.rglob('*.pdf')]
    images = [str(p.relative_to(ROOT)) for p in sources.rglob('page_01.png')]
    out.append({'key':key,'sku':group['sku'],'rows':len(group['rows']),
                'native_pass':native.get('native_gates_pass',False),'stage':native.get('stage'),
                'spec_exists':(ROOT / key / 'source/model_spec.json').exists(),
                'pdfs':pdfs,'first_pages':images,
                'errors':[native.get('error')] if native.get('error') else []})
(ROOT / '_harness/resume_inventory.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'rows':sum(len(g['rows']) for g in groups),'product_groups':len(out),
                  'native_pass':sum(x['native_pass'] for x in out),
                  'remaining':[x for x in out if not x['native_pass']]},indent=2))

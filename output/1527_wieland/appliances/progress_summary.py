"""Print bounded audit summaries; never dump malformed documents to the terminal."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
for p in sorted(ROOT.glob('native_audit*.json')):
    try:
        r = json.loads(p.read_text(encoding='utf-8'))
        for item in r.get('items', []):
            print(json.dumps(dict(report=p.name, item=item['slug'], stage=item.get('stage'),
                category=item.get('category'), dimensions=item.get('reopened_bounds',{}).get('xyz_size_mm'),
                error=item.get('error','')[-700:], version=item.get('saved_revit_format'))))
    except Exception as exc:
        print(json.dumps(dict(report=p.name,error=str(exc))))

"""Summarize embedded technical resources without dumping large product HTML."""
from pathlib import Path
import json
import re
import sys
ROOT = Path(__file__).resolve().parents[1]
groups = {g['key']: g for g in json.loads((ROOT / 'GROUPS.json').read_text())['groups']}
for key in sys.argv[1:]:
    folder = ROOT / groups[key]['canonical_item'] / 'source'
    print('\n' + key)
    for file in sorted(folder.glob('page_*.html')):
        content = file.read_text(encoding='utf-8', errors='replace')
        for pattern in [r'.{0,140}rv_tris.{0,300}', r'.{0,100}revit/.{0,280}',
                        r'.{0,120}searchpageItemID.{0,200}', r'.{0,80}photometricdata.{0,220}',
                        r'.{0,80}ajax\(.{0,220}']:
            for match in re.findall(pattern, content, re.I)[:8]:
                print(file.name + ': ' + match)

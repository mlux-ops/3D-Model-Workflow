"""Stage a task-local native helper and portable uniform material bitmaps."""
from pathlib import Path
import json
import shutil
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
source = REPO / 'output/lightology_20260923/tools/native_fixture_support.py'
target = ROOT / '_tools/native_fixture_support.py'
if not target.exists():
    shutil.copy2(source, target)
groups = {g['key']: g for g in json.loads((ROOT / 'GROUPS.json').read_text())['groups']}
out = ROOT / groups['57670WTBK']['canonical_item']
texture = out / 'source/textures'
texture.mkdir(parents=True, exist_ok=True)
for name, rgb in [('Black_Housing', (24, 24, 24)), ('White_Diffuser', (244, 244, 240))]:
    Image.new('RGB', (32, 32), rgb).save(texture / (name + '.png'))
entry = out / 'source/build_family.py'
entry.write_text('''# -*- coding: utf-8 -*-
import os, sys
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(OUT), '_tools'))
from wieland_native import build_maxim
build_maxim(__revit__.Application, OUT)
''', encoding='utf-8')
print('Native entry: ' + str(entry))
print('Helper source: ' + str(source))

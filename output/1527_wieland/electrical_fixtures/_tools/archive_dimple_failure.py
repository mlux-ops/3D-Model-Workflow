"""Preserve the failed candidate before its documented native rebuild."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]/'B2-2__5960925969973124'
target=ROOT/'history/failed_oem_adaptation'
target.mkdir(parents=True,exist_ok=True)
for p in list(ROOT.glob('*.rfa'))+list(ROOT.glob('*validation.json')):
    if not (target/p.name).exists():shutil.copy2(p,target/p.name)
if not (target/'evidence').exists():shutil.copytree(ROOT/'evidence',target/'evidence')
entry=ROOT/'source/build_family.py'
entry.write_text("# -*- coding: utf-8 -*-\nimport os\nexecfile(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),'_tools','build_dimple_current.py'))\n",encoding='utf-8')
print('Failed Dimple evidence archived: '+str(target))

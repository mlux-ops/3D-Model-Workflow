"""Archive failed candidates once and stage only the three justified native repairs."""
from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parents[1]
keys=['RG-C811A','HIN1284470','KZC610420']
jobs=json.loads((ROOT/'CATALOG_JOBS.json').read_text())
for job in jobs:
    if job['key'] not in keys:continue
    out=Path(job['out']);archive=out/'history/first_catalog_failure'
    archive.mkdir(parents=True,exist_ok=True)
    for path in list(out.glob('*.rfa'))+list(out.glob('*validation.json')):
        if not (archive/path.name).exists():shutil.copy2(path,archive/path.name)
    if (out/'evidence').exists() and not (archive/'evidence').exists():shutil.copytree(out/'evidence',archive/'evidence')
(ROOT/'CATALOG_RUN_KEYS.json').write_text(json.dumps(keys,indent=2))
archive=ROOT/'_review/history';archive.mkdir(exist_ok=True)
if not (archive/'CATALOG_BATCH_INITIAL.json').exists():shutil.copy2(ROOT/'CATALOG_BATCH_RESULT.json',archive/'CATALOG_BATCH_INITIAL.json')
print('Three failed candidates archived; three native repairs selected')

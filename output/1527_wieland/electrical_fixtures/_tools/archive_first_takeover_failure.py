"""Preserve failed native receipts before retrying corrected scripts."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
archive=ROOT/'_review'/'failed_worker4_first_run'
archive.mkdir(exist_ok=True)
files=[ROOT/'ORION_BUILD_ERROR.txt',ROOT/'GEOMETRY_REVIEW_EXPORT.json',ROOT/'Best_option_-_Orion_Tube_Pendant__1967952628416388'/'validation.json']
files.extend(ROOT.glob('*/evidence/geometry_review.json'))
for source in files:
    target=archive/source.relative_to(ROOT)
    if source.exists() and not target.exists():
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
print('Preserved',len(files),'failure receipts.')

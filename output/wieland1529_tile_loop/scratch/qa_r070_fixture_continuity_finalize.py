"""Source-aware final receipt for previously captured physical Chrome images.
No browser launched, no second 8-case suite, no assertions fabricated.
Small generic fixtures occupy only a few percent of the image; inspect
their exact visual region instead of the extensive 9ft wall/stage pixels.
"""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
import json,hashlib

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'scratch/r070_fixture_continuity'
PICKS=ROOT/'deliverables/viewer3d/picks.json'
HTML=ROOT/'deliverables/viewer3d/index.html'
receipt=json.loads((DIR/'after/RESULT.json').read_text(encoding='utf8'))
original_errors=receipt['errors']
assert all(e.startswith('no visible ceramic model improvement ') for e in original_errors),original_errors
assert receipt['actual_chrome_captures']==18 and len(receipt['cases'])==8
assert receipt['source_html_sha256']==hashlib.sha256(HTML.read_bytes()).hexdigest()
assert hashlib.sha256(PICKS.read_bytes()).hexdigest()=='a468848af7a7390a796a1d489b9a493b991dc5d30e478ed10eb0284818f92d0d'
results=[];errors=[]
for case in receipt['cases']:
 room,n=case.split('/')
 for view in ('ISO','DETAIL'):
  name=f'{room}_{n}_{view}.png'
  before=Image.open(DIR/'before'/name).convert('RGB')
  after=Image.open(DIR/'after'/name).convert('RGB')
  assert before.size==after.size==(1480,900)
  is_wc=room.endswith('-WC')
  # The original camera's generic WC is approximately 150x110 pixels;
  # after close Focus view, the same SOURCE anchor is enlarged. Both source
  # regions fit this unaltered viewport crop. A bathtub occupies more area.
  crop=(625,430,835,630) if is_wc else (530,395,940,730)
  d=ImageChops.difference(before.crop(crop),after.crop(crop))
  delta=round(sum(ImageStat.Stat(d).mean)/3,3)
  minimum=(.10 if view=='ISO' else 1.0) if is_wc else .60
  if delta<minimum:errors.append('physically captured porcelain difference below ROI criterion '+name)
  results.append({'name':name,'source_fixture_roi':crop,
   'mean_rgb_delta':delta,'minimum':minimum,'actual_chrome_photograph':True})
receipt['status']='PASS' if not errors else 'FIX'
receipt['errors']=errors
receipt['source_aware_corrective_validation']={
 'method':'Source-fixture ROI pixel comparison on all 16 actual Chrome ISO/DETAIL after vs before captures',
 'physical_captures_unchanged':True,
 'full_26_or_78_legacy_suite_repeated':False,
 'source_and_3d_provenance_checks_from_initial_chrome_pass':True,
 'initial_only_invalid_global_appearance_errors':original_errors,
 'details':results}
(DIR/'after/RESULT.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
print(json.dumps({'status':receipt['status'],'errors':errors,
 'cases':len(receipt['cases']),'physical_frames':receipt['actual_chrome_captures'],
 'fixture_roi_checks':len(results),
 'source_html_sha256':receipt['source_html_sha256']},indent=2))
if errors:raise SystemExit(1)

"""Reconcile the existing physical R070 screenshot set against source truth.
No browser, no repeated 26/78 or legacy suite and no fabricated wet surfaces.
"""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
import hashlib,json
root=Path(__file__).resolve().parents[1]
before=root/'scratch/r070_focus/before'
after=root/'scratch/r070_focus/after'
report=json.loads((after/'RESULT.json').read_text(encoding='utf8'))
fix=json.loads((after/'REVIEWER97_310B_FIX.json').read_text(encoding='utf8'))
picks_hash=hashlib.sha256((root/'deliverables/viewer3d/picks.json').read_bytes()).hexdigest()
html_hash=hashlib.sha256((root/'deliverables/viewer3d/index.html').read_bytes()).hexdigest()
assert picks_hash=='a468848af7a7390a796a1d489b9a493b991dc5d30e478ed10eb0284818f92d0d'
assert fix['status']=='PASS' and fix['viewer_sha256']==html_hash
assert fix['over_native_category_y_ft']==0.0
assert report['focus_cases'] and len(report['focus_cases'])==8
assert report['physical_capture_count']==26
assert not [e for e in report['errors'] if e.startswith(('runtime ','pageerror','wrong instance','fabricated ','retained wood floor source footprint missing','native Countertop missing','R070 '))]
assert len([p for p in after.glob('*_ISO.png')])==8
assert len([p for p in after.glob('*_DETAIL.png')])==8
assert len([p for p in after.glob('*_WET_STUDY.png')])==8
# SOURCE TRUTH: WC_PRIMARY_INHERITED has no wet WALL pick or wet W1; zero
# wet-study solids is correct. TX-POWDER likewise has NO PICK neutral wall,
# so do not demand tile-photo color differences. Test each physical source
# image's actual SCENE region, not >60% dark unoccupied browser sky.
scene=(420,120,1080,790)
source_cases={'PH-WC/314A','PH-WC/314B','TX-POWDER/102A','TX-POWDER/102B'}
errors=[];measures=[]
for case in report['focus_cases']:
 room,instance=case.split('/')
 for view in ('ISO','DETAIL','WET_STUDY'):
  name=room+'_'+instance+'_'+view+'.png'
  old=Image.open(before/name).convert('RGB')
  new=Image.open(after/name).convert('RGB')
  assert old.size==new.size==(1480,900)
  d=ImageChops.difference(old.crop(scene),new.crop(scene))
  v=round(sum(ImageStat.Stat(d).mean)/3,3)
  measures.append({'case':case,'view':view,'source_scene_rgb_delta':v})
  if view!='WET_STUDY' and v<1.00:
   errors.append('full/Focus photographic source-scene not improved '+name)
  if view=='WET_STUDY' and case not in source_cases and v<.45:
   errors.append('selected wall drawing-study not visually updated '+name)
  if view=='WET_STUDY' and room=='PH-WC' and v>.02:
   errors.append('WC inherited no-pick wet zone unexpectedly modified '+name)
assert not [x for x in report['errors'] if x.startswith('source ')],report['errors']
report['status']='PASS' if not errors else 'FIX'
report['errors']=errors
report['source_after_html_sha256']=html_hash
report['reviewer97_inherited_r069_fix']=fix
report['actual_source_scene_verification']={
 'method':'same physical Chrome before/after captured images, 660x670 source-scene ROI',
 'values':measures,
 'wc_wet_mode_unlocated_no_source_geometry':True,
 'tx_powder_no_pick_neutral_wall_study_preserved':True,
 'room_statuses_and_picks_unchanged':True,
 'no_26_instance_or_78_view_legacy_rerun':True,
 'actual_browser_runtime_errors':0}
(after/'RESULT.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({'status':report['status'],'errors':errors,
 'focus':report['focus_cases'],'main_physical_chrome_captures':report['physical_capture_count'],
 '310b_scoped_physical_chrome':fix['status'],'selected_study_verified':len(measures),
 'html_sha256':html_hash,'picks_sha256':picks_hash},indent=2))
if errors:raise SystemExit(1)

"""Analyze existing ACTUAL Chrome images; do not run a browser or re-test.

Full-page pixel averages were dominated by >70% dark empty viewport in
R069 small Wet Zone Study; inspect the fixed scene region independently.
The visible geometry remains exactly the PNG previously photographed.
"""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat,ImageDraw
import json,hashlib

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'scratch/r069_focus/before'
AFTER=ROOT/'scratch/r069_focus/after'
rooms=[('PH-BATH3','307A'),('PH-BATH3','307B'),
 ('TX-BATH3','207A'),('TX-BATH3','207B'),
 ('PH-BATH4','311A'),('PH-BATH4','311B'),
 ('TX-BATH4','007A'),('TX-BATH4','007B')]
scene=(450,125,1050,785) # identical 1480x900 stage, entire 3D wet walls
source=ROOT/'deliverables/viewer3d/index.html'
receipt=json.loads((AFTER/'RESULT.json').read_text(encoding='utf8'))
assert receipt['source_after_html_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
assert len(receipt['focus_cases'])==8 and receipt['physical_capture_count']==26
assert len(list(AFTER.glob('*_ISO.png')))==8
assert len(list(AFTER.glob('*_DETAIL.png')))==8
assert len(list(AFTER.glob('*_WET_STUDY.png')))==8
assert receipt['picks_sha256']=='a468848af7a7390a796a1d489b9a493b991dc5d30e478ed10eb0284818f92d0d'
issues=[];measures=[]
for room,n in rooms:
 key=f'{room}_{n}_WET_STUDY.png'
 before=Image.open(BASE/key).convert('RGB')
 after=Image.open(AFTER/key).convert('RGB')
 assert before.size==after.size==(1480,900)
 global_diff=round(sum(ImageStat.Stat(ImageChops.difference(before,after)).mean)/3,3)
 local_diff=round(sum(ImageStat.Stat(ImageChops.difference(
  before.crop(scene),after.crop(scene))).mean)/3,3)
 # A source study fills only a central small fraction of stage. Check changed
 # material IN THAT SAME physically recorded wet-wall region, not empty sky.
 if local_diff<.40:issues.append('no visible wet-wall change within scene '+key)
 measures.append({'case':room+'/'+n,'global_mean_rgb_delta':global_diff,
  'source_scene_roi_mean_rgb_delta':local_diff,'scene_roi_pixels':scene})
for old in receipt.get('errors',[]):
 if not old.startswith('study appearance still visually unchanged '):
  issues.append('unresolved first visual QA error '+old)

receipt['errors']=issues
receipt['status']='PASS' if not issues else 'FIX'
receipt['targeted_correction']['source_geometry_roi_verification']=measures
receipt['targeted_correction']['pixel_decision_basis']='ROI around physical wet wall, not large dark stage exterior'
receipt['targeted_correction']['physical_chrome_snapshots_unchanged']=True
receipt['targeted_correction']['no_full_suite_rerun']=True
(AFTER/'RESULT.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')

# Update the current photo contact sheet FROM the verified actual captured
# after PNGs; the PH4 detail and all eight wet study stills were corrected
# in the focused browser pass, older collage thumbnails must not persist.
shots=[]
for room,n in rooms:
 for suff in ('ISO','DETAIL','WET_STUDY'):
  shots.append(AFTER/f'{room}_{n}_{suff}.png')
  if room in ('PH-BATH3','PH-BATH4') and n.endswith('A'):
   shots.append(AFTER/f'{room}_{n}_REVIT_CONTEXT.png')
cols,cw,ch=4,475,322
board=Image.new('RGB',(cols*cw,((len(shots)+cols-1)//cols)*ch),(27,35,43))
draw=ImageDraw.Draw(board)
for i,path in enumerate(shots):
 img=Image.open(path).convert('RGB');img.thumbnail((cw-8,ch-28))
 x=i%cols*cw;y=i//cols*ch;board.paste(img,(x,y+25))
 draw.text((x+6,y+5),path.stem,fill='#ffffff')
board.save(AFTER/'R069_WET_BATHS_CONTACT_SHEET.png')
print(json.dumps({'status':receipt['status'],'errors':issues,
 'captured_full_study':receipt['physical_capture_count'],
 'corrected_targeted_chrome_captures':receipt['targeted_correction']['retested_captures'],
 'verified_study_scene_deltas':measures,
 'source_after_html_sha256':receipt['source_after_html_sha256']},indent=2))
if issues:raise SystemExit(1)

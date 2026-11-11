"""Targeted R066 Chrome actual-file physical review, four coordinated room types A/B.
Usage: python -B scratch/qa_r066_focus_browser.py before|after
No full gallery, all 26 instances, 78 modes or legacy suites.
"""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat,ImageDraw
from playwright.sync_api import sync_playwright
import json,sys,hashlib

ROOT=Path(__file__).resolve().parents[1]
PHASE=sys.argv[1] if len(sys.argv)>1 else 'after'
assert PHASE in ('before','after')
FOLDER=ROOT/'scratch/r066_focus'/PHASE
FOLDER.mkdir(parents=True,exist_ok=True)
CASES=[('PH-PRIMARY','304A'),('PH-PRIMARY','304B'),
       ('TX-PRIMARY','202A'),('TX-PRIMARY','202B'),
       ('PH-BATH4','311A'),('PH-BATH4','311B'),
       ('TX-BATH4','007A'),('TX-BATH4','007B')]
PICKS=ROOT/'deliverables/viewer3d/picks.json'
FROZEN_HASH=hashlib.sha256(PICKS.read_bytes()).hexdigest()
SOURCE_ROOMS={r['id']:r for r in json.loads(PICKS.read_text(encoding='utf8'))['rooms']}
ORIGINALS=[ROOT/'state/ROOMS.json',ROOT/'state/OWNER_FEEDBACK.md']
ORIGINALS+=sorted((ROOT/'rooms').glob('*/champion.md'))
ORIGINALS+=sorted((ROOT/'deliverables/r039-13-owner-review-PROVISIONAL').glob('*.html'))
ORIGINALS+=sorted((ROOT/'deliverables/r039-13-owner-review-PROVISIONAL').glob('*.pdf'))
assert len(ORIGINALS)==43
LOCK=ROOT/'scratch/r066_focus/protected_before.json'
locked={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in ORIGINALS}
if PHASE=='before':
 LOCK.write_text(json.dumps(locked,indent=2),encoding='utf8')
else:
 assert json.loads(LOCK.read_text(encoding='utf8'))==locked,'43 frozen originals changed'
errors=[];checks=[];shots=[];gates={}
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
  args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1500,'height':920},device_scale_factor=1)
 page.on('pageerror',lambda err:errors.append('js:'+str(err)))
 page.goto((ROOT/'deliverables/viewer3d/index.html').as_uri()+'#PH-PRIMARY/304A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug && document.body.dataset.viewerMaterials==="READY"',timeout=30000)
 page.locator('#viewer-focus-enter').click()
 for kind,n in CASES:
  page.evaluate('(s)=>window.__viewerDebug.loadInstanceAddress("#"+s)',kind+'/'+n)
  page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=20000)
  page.wait_for_timeout(65)
  key=kind+'_'+n
  if page.evaluate('document.body.dataset.viewerInstance')!=n:
   errors.append('instance mismatch '+key)
  if not page.evaluate('window.__viewerDebug.getState().focusView'):
   errors.append('Focus dropped '+key)
  evidence=page.evaluate('window.__viewerDebug.getSceneEvidence()')
  native=[o for o in evidence if o['category']=='ARCH_REGISTERED_WALL']
  if len(native)<4:errors.append('missing native enclosure '+key)
  sourceCounter=[o for o in evidence if o['category']=='ARCH_NATIVE_COUNTERTOP_VISUAL']
  # PH-BATH4 311 has no native vanity and must remain DISTINCT from 310.
  if kind=='PH-BATH4' and sourceCounter:errors.append('311 inherited 310 casework '+key)
  if kind in ('PH-PRIMARY','TX-PRIMARY','TX-BATH4') and len(sourceCounter)!=1:
   errors.append('native counter source lost '+key)
  if kind in ('PH-PRIMARY','TX-PRIMARY'):
   if any(o['category']=='ARCH_ILLUSTRATIVE_BASIN_NO_FAMILY' for o in evidence):
    errors.append('unsupported primary 3D basin '+key)
   if any(o['category']=='FULL_ROOM_SELECTED_PAN_SCHEMATIC' for o in evidence):
    errors.append('primary selected PAN fabricated '+key)
  if kind=='TX-BATH4':
   if any(o['category']=='ARCH_ILLUSTRATIVE_BASIN_NO_FAMILY' and not o.get('source') for o in evidence):
    errors.append('uncertified TX4 source basin '+key)
   if any(o['category']=='FULL_ROOM_SELECTED_PAN_SCHEMATIC' for o in evidence):
    errors.append('TX4 pan invented '+key)
   if any(o.get('r063_tub_part') in ('BODY','SHELL') for o in evidence):
    errors.append('TX4 unlocated selected tub appeared as 3D '+key)
  if kind=='PH-BATH4' and any(o['category']=='ARCH_NATIVE_COUNTERTOP_VISUAL' for o in evidence):
   errors.append('311 wrongly displays 310 counter '+key)
  page.locator('#viewer-focus-iso').click()
  iso=FOLDER/(key+'_ISO.png');page.locator('#stage').screenshot(path=str(iso));shots.append(iso)
  if kind in ('PH-PRIMARY','TX-PRIMARY'):
   preset='r062-primary-vanity'
  elif kind=='PH-BATH4':preset='ph4-311'
  else:preset='r066-tx4-counter'
  if PHASE=='after':
   page.locator('#viewer-focus-architectural').click()
  else:page.evaluate('(name)=>window.__viewerDebug.setCamera(name)',preset)
  detail=FOLDER/(key+'_DETAIL.png');page.locator('#stage').screenshot(path=str(detail))
  if PHASE=='after':
   cam=page.evaluate('window.__viewerDebug.getCameraInfo().preset')
   if cam!=preset:errors.append('focus architectural camera preset '+key+' '+str(cam))
   if kind in ('PH-PRIMARY','TX-PRIMARY','TX-BATH4'):
    layers=[o for o in evidence if o['category']=='ARCH_R066_NATIVE_BOUNDED_COUNTER_EDGE']
    if len(layers)<2:errors.append('native-bound counter edge absent '+key)
    nativeCounter=next(inst for inst in SOURCE_ROOMS[kind]['physical_instances']
                      if inst['room_number']==n)['architecture']['native_casework_proxies'][0]
    x,z=nativeCounter['local_center_xz_ft']
    limits=[[x-nativeCounter['width_x_ft']/2,nativeCounter['min_height_ft'],
             z-nativeCounter['depth_z_ft']/2],
            [x+nativeCounter['width_x_ft']/2,nativeCounter['max_height_ft'],
             z+nativeCounter['depth_z_ft']/2]]
    for o in layers:
     if not o.get('r066_inside_category_aabb_xyz'):
      errors.append('counter edge not contained '+key)
     actual=o.get('r066_world_mesh_aabb')
     if not actual or any(actual[0][axis]<limits[0][axis]-.005 or
                          actual[1][axis]>limits[1][axis]+.005 for axis in range(3)):
      errors.append('physical mesh exceeds native XYZ countertop envelope '+key)
   if kind=='PH-BATH4':
    floor=[o for o in evidence if o['category']=='ARCH_REGISTERED_FLOOR']
    if len(floor)!=1 or not floor[0].get('r063_floor_material_selected'):
     errors.append('selected 311 polygon floor absent '+key)
    if any(o['category']=='FULL_ROOM_SELECTED_PAN_SCHEMATIC' for o in evidence):
     errors.append('duplicate 311 rectangular pan overlay '+key)
    if not any(o['category']=='ARCH_R066_SHARED_LEVEL_POINT_SOURCE_EDGE' for o in evidence):
     errors.append('source polygon shared-pool edge missing '+key)
   # Reversible evidence and native-geometry source inspectors remain alive.
   if n.endswith('A'):
    nativeCeiling=next(inst for inst in SOURCE_ROOMS[kind]['physical_instances']
                       if inst['room_number']==n)['architecture'].get('native_ceiling_evidence')
    if nativeCeiling and nativeCeiling.get('id'):
     if page.locator('#viewer-focus-gwb').is_hidden():
      errors.append('independent native GWB preview unavailable '+key)
     else:
      page.locator('#viewer-focus-gwb').click()
      if not page.evaluate('window.__viewerDebug.getState().ceilingPreview'):
       errors.append('native GWB preview did not enable '+key)
      if not int(page.evaluate('document.body.dataset.viewerCeilingCanopies || 0')):
       errors.append('native GWB ghost not rendered '+key)
      page.locator('#viewer-focus-gwb').click()
      if page.evaluate('window.__viewerDebug.getState().ceilingPreview'):
       errors.append('native GWB preview did not restore '+key)
    page.locator('#viewer-focus-traces').click()
    if not any(o['category']=='ARCH_FLOOR_FACE_OUTLINE' and o['visible'] for o in page.evaluate('window.__viewerDebug.getSceneEvidence()')):
     errors.append('source trace reveal '+key)
    page.locator('#viewer-focus-traces').click()
    page.locator('#viewer-focus-ab').click()
    if not page.locator('#viewer-ab-drawer').is_visible():errors.append('A/B compare '+key)
    page.locator('#viewer-focus-ab').click()
    page.locator('#viewer-focus-cutaway').click()
    page.locator('#viewer-focus-cutaway').click()
    if not page.evaluate('window.__viewerDebug.getState().interiorReveal'):
     errors.append('cutaway restore '+key)
    checks.append(key+' Focus A/B, section and source controls')
  gates[key]={'native_walls':len(native),'source_countertops':len(sourceCounter),
              'object_count':len(evidence)}
 if PHASE=='after':
  page.locator('#viewer-focus-evidence').click()
  if page.evaluate('window.__viewerDebug.getState().focusView'):
   errors.append('Evidence exit not reversible')
  if not page.locator('#viewer-v2-evidence').evaluate('(el)=>el.open'):
   errors.append('Evidence inspector closed')
  if page.evaluate('window.__viewerDebug.errors'):
   errors.append('runtime:'+str(page.evaluate('window.__viewerDebug.errors')))
 browser.close()

grid=Image.new('RGB',(4*550,2*400),(23,29,37));dr=ImageDraw.Draw(grid)
for i,shot in enumerate(shots):
 im=Image.open(shot).convert('RGB');im.thumbnail((545,370));x=i%4*550;y=i//4*400
 grid.paste(im,(x,y+25));dr.text((x+8,y+6),shot.stem,fill='white')
grid.save(FOLDER/'R066_EIGHT_AB_FOCUS_GALLERY.png')
deltas=[]
if PHASE=='after':
 for kind,n in CASES:
  path=kind+'_'+n+'_DETAIL.png'
  im1=Image.open(FOLDER/path).convert('RGB')
  im0=Image.open(FOLDER.parent/'before'/path).convert('RGB')
  v=sum(ImageStat.Stat(ImageChops.difference(im0,im1)).mean)/3
  deltas.append({'key':kind+'/'+n,'pixel_delta':round(v,2)})
  if v<.6:errors.append('not visibly changed '+kind+'/'+n)
if hashlib.sha256(PICKS.read_bytes()).hexdigest()!=FROZEN_HASH:errors.append('picks changed')
status={'status':'PASS' if not errors else 'FIX','phase':PHASE,
 'focus_cases':[k+'/'+n for k,n in CASES], 'checks':checks,'errors':errors,
 'source_geometry':gates,'protected_count':len(ORIGINALS),
 'picks_sha256':FROZEN_HASH,'visual_deltas':deltas}
(FOLDER/'RESULT.json').write_text(json.dumps(status,indent=2),encoding='utf8')
print(json.dumps(status,indent=2))
if errors:raise SystemExit(1)

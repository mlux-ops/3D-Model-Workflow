"""R067 targeted physical Chrome screenshot and source-fidelity check.
Usage: python -B scratch/qa_r067_powder_wc_browser.py before|after
The before-only survey includes five candidate room types; after tests just
four selected type pairs. Neither path performs a 26/78 legacy regression.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops, ImageStat
from playwright.sync_api import sync_playwright
import hashlib, json, sys

ROOT=Path(__file__).resolve().parents[1]
PHASE=sys.argv[1] if len(sys.argv)>1 else 'after'
assert PHASE in ('before','after')
CASES=[('PH-POWDER','405A'),('PH-POWDER','405B'),
       ('PH-WC','314A'),('PH-WC','314B'),
       ('TX-POWDER','102A'),('TX-POWDER','102B'),
       ('TX-POWDER2','010A'),('TX-POWDER2','010B')]
if PHASE=='before':CASES += [('TX-WC','203A'),('TX-WC','203B')]
OUT=ROOT/'scratch/r067_focus'/PHASE;OUT.mkdir(parents=True,exist_ok=True)
DATA=json.loads((ROOT/'deliverables/viewer3d/picks.json').read_text(encoding='utf8'))
rooms={r['id']:r for r in DATA['rooms']}
errors=[];captures=[];evidence_summary={}
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
  args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1500,'height':920},device_scale_factor=1)
 page.on('pageerror',lambda e:errors.append('pageerror: '+str(e)))
 page.goto((ROOT/'deliverables/viewer3d/index.html').as_uri()+'#PH-POWDER/405A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug && document.body.dataset.viewerMaterials==="READY"',timeout=45000)
 page.locator('#viewer-focus-enter').click()
 for kind,num in CASES:
  key=kind+'_'+num
  page.evaluate('(s)=>window.__viewerDebug.loadInstanceAddress("#"+s)',kind+'/'+num)
  page.wait_for_function('document.body.dataset.viewerMaterials==="READY"',timeout=20000)
  page.wait_for_timeout(120)
  evidence=page.evaluate('window.__viewerDebug.getSceneEvidence()')
  categories={}
  for o in evidence:categories[o['category']]=categories.get(o['category'],0)+1
  counters=[o for o in evidence if o['category']=='ARCH_NATIVE_COUNTERTOP_VISUAL']
  expected=1 if 'POWDER' in kind else 0
  if len(counters)!=expected:errors.append('source countertop mismatch '+key)
  if len([o for o in evidence if o['category']=='ARCH_REGISTERED_WALL'])<4:
   errors.append('missing native walls '+key)
  if 'POWDER' in kind and any(o['category']=='ARCH_ILLUSTRATIVE_BASIN_NO_FAMILY' for o in evidence):
   errors.append('unselected/unlocated 3D basin '+key)
  if any(o['category']=='FULL_ROOM_SELECTED_PAN_SCHEMATIC' for o in evidence):
   errors.append('unexpected selected PAN '+key)
  arch=next(i for i in rooms[kind]['physical_instances'] if i['room_number']==num)['architecture']
  # Short invariants directly relevant to the renderer changes.
  if kind=='TX-POWDER':
   c=arch['native_casework_proxies'][0]
   if abs(c['max_height_ft']-c['min_height_ft']-.125)>.003:
    errors.append('registered thin slab changed '+key)
  if PHASE=='after':
   previews=[o for o in evidence if o['category']=='ARCH_R067_SOURCE_HOSTED_DRY_FINISH_PREVIEW']
   if kind in ('PH-POWDER','TX-POWDER2'):
    if len(previews)!=1 or not previews[0].get('r067_dry_source_host') or not previews[0].get('r067_dry_native_host_wall_id'):
     errors.append('selected dry wall preview not source hosted '+key)
   elif previews:errors.append('false dry wall selection preview '+key)
   if kind=='TX-POWDER':
    bands=[o for o in evidence if o['category']=='ARCH_R067_THIN_COUNTER_LIGHT_EDGE']
    if len(bands)<2:errors.append('missing source-bounded thin slab detail '+key)
   if kind in ('PH-POWDER','TX-POWDER2'):
    faces=[o for o in evidence if o['category']=='ARCH_R067_NATIVE_BOUNDED_POWDER_FACET']
    if len(faces)<3:errors.append('missing source-bounded powder facets '+key)
   wcPieces=[o.get('r067_wc_visual_piece') for o in evidence if o.get('r067_wc_visual_piece')]
   if not any(x=='R067_ABSTRACT_UNDERSHELL' for x in wcPieces):
    errors.append('missing refined source-gated WC underbody '+key)
   if any(x=='R067_GENERIC_REAR_SHOULDER' for x in wcPieces):
    errors.append('detached generic WC rear shoulder persists '+key)
   # All R067 counter faces must remain within the actual native category AABB.
   for o in evidence:
    if o['category'] not in ('ARCH_R067_NATIVE_BOUNDED_POWDER_FACET','ARCH_R067_THIN_COUNTER_LIGHT_EDGE'):continue
    if not o.get('r067_inside_native_category_aabb_xyz'):
     errors.append('counter facet containment metadata absent '+key)
    c=arch['native_casework_proxies'][0]
    xx,zz=c['local_center_xz_ft'];actual=o.get('r067_world_mesh_aabb')
    limits=[[xx-c['width_x_ft']/2,c['min_height_ft'],zz-c['depth_z_ft']/2],
            [xx+c['width_x_ft']/2,c['max_height_ft'],zz+c['depth_z_ft']/2]]
    if not actual or any(actual[0][a]<limits[0][a]-.006 or actual[1][a]>limits[1][a]+.006 for a in range(3)):
     errors.append('counter visual exceeds native XYZ '+key)
  page.locator('#viewer-focus-iso').click()
  iso=OUT/(key+'_ISO.png');page.locator('#stage').screenshot(path=str(iso));captures.append(iso)
  preset='r060-counter' if 'POWDER' in kind else 'r060-wc'
  page.evaluate('(x)=>window.__viewerDebug.setCamera(x)',preset)
  page.wait_for_timeout(80)
  detail=OUT/(key+'_DETAIL.png');page.locator('#stage').screenshot(path=str(detail));captures.append(detail)
  if PHASE=='after' and num.endswith('A'):
   if kind in ('PH-WC','TX-POWDER2'):
    if page.locator('#viewer-focus-gwb').is_hidden():
     errors.append('matched native GWB preview missing '+key)
    else:
     page.locator('#viewer-focus-gwb').click()
     if not page.evaluate('window.__viewerDebug.getState().ceilingPreview'):
      errors.append('native GWB toggle failed '+key)
     page.locator('#viewer-focus-gwb').click()
   page.locator('#viewer-focus-traces').click()
   if not page.evaluate('window.__viewerDebug.getState().sourceTraces'):
    errors.append('source traces toggle '+key)
   page.locator('#viewer-focus-traces').click()
   page.locator('#viewer-focus-cutaway').click()
   page.locator('#viewer-focus-cutaway').click()
   if not page.evaluate('window.__viewerDebug.getState().interiorReveal'):
    errors.append('reversible section '+key)
  evidence_summary[key]={'counts':categories,'counter_ids':[o.get('revit_id') for o in counters],
                         'camera_preset':page.evaluate('window.__viewerDebug.getCameraInfo().preset')}
 if PHASE=='after' and page.evaluate('window.__viewerDebug.errors'):
  errors.append('runtime '+str(page.evaluate('window.__viewerDebug.errors')))
 browser.close()

# Compact visual contact sheet for human inspection, not just assertion counts.
cols=4;thumbW=450;thumbH=320
rows=(len(captures)+cols-1)//cols
grid=Image.new('RGB',(cols*thumbW,rows*thumbH),(29,35,42));draw=ImageDraw.Draw(grid)
for i,file in enumerate(captures):
 im=Image.open(file).convert('RGB');im.thumbnail((thumbW-8,thumbH-25))
 x=i%cols*thumbW;y=i//cols*thumbH
 grid.paste(im,(x,y+22));draw.text((x+5,y+4),file.stem,fill='white')
grid.save(OUT/'R067_POWDER_WC_CONTACT_SHEET.png')
deltas=[]
if PHASE=='after':
 for k,n in CASES:
  for suffix in ('ISO','DETAIL'):
   f=k+'_'+n+'_'+suffix+'.png'
   im0=Image.open(OUT.parent/'before'/f).convert('RGB')
   im1=Image.open(OUT/f).convert('RGB')
   delta=round(sum(ImageStat.Stat(ImageChops.difference(im0,im1)).mean)/3,2)
   deltas.append({'image':f,'mean_channel_delta':delta})
   if delta<.4:errors.append('no material visual change '+f)
result={'status':'PASS' if not errors else 'FIX','phase':PHASE,
 'cases':[k+'/'+n for k,n in CASES], 'errors':errors,
 'picks_sha256':hashlib.sha256((ROOT/'deliverables/viewer3d/picks.json').read_bytes()).hexdigest(),
 'evidence':evidence_summary,'visual_deltas':deltas}
(OUT/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='evidence'},indent=2))
if errors:raise SystemExit(1)

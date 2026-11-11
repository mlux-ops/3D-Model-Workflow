"""R043 actual Chrome GPU and control QA, including complete 13-room gallery."""
import json
from pathlib import Path
from PIL import Image,ImageStat
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scratch/r043_arch_gallery';OUT.mkdir(exist_ok=True)
ROOMS=json.loads((ROOT/'deliverables/viewer3d/picks.json').read_text())['rooms']
NATIVE=json.loads((ROOT/'scratch/viewer3d_revit_sources.json').read_text())['categories']
WINDOW_BY_ID={x['id']:x for x in NATIVE['windows']['items']}
DOOR_BY_ID={x['id']:x for x in NATIVE['doors']['items']}
URL=(ROOT/'deliverables/viewer3d/index.html').as_uri()
CHROME=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
errors=[];scenes=[];images=[];all_images=[]
hosted_depth_count=0
native_window_aabb_count=0
native_door_aabb_count=0
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=CHROME,headless=True,
  args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
 page=browser.new_page(viewport={'width':1500,'height':980},device_scale_factor=1)
 page.on('pageerror',lambda x:errors.append('pageerror:'+str(x)))
 page.goto(URL+'#PH-BATH4/311A',wait_until='load')
 page.wait_for_function('!!window.__viewerDebug && document.body.dataset.viewerMode==="full"',timeout=25000)
 for room in ROOMS:
  for idx,inst in enumerate(room['physical_instances']):
   name=room['id']+'_'+inst['room_number'];key=room['id']+'/'+inst['room_number']
   good=page.evaluate('(key)=>window.__viewerDebug.loadInstanceAddress("#"+key)',key)
   probe=page.evaluate('''() => ({
    room:document.body.dataset.viewerRoom,instance:document.body.dataset.viewerInstance,
    mode:document.body.dataset.viewerMode,count:window.__viewerDebug.getState().objectCount,
    errors:window.__viewerDebug.errors.slice(),
    native:document.getElementById('viewer-v2-fidelity').textContent.includes('REGISTERED') ||
       document.getElementById('viewer-v2-fidelity').textContent.includes('source wall-face')
    })''')
   if not good or probe['room']!=room['id'] or probe['instance']!=inst['room_number']:
    errors.append('incorrect-link:'+key)
   if probe['count']<5:errors.append('too-few-objects:'+key)
   if probe['errors']:errors.extend(probe['errors'])
   # R056 conservative fixture gate: the two PH dry-powder native plumbing
   # points are near countertop edges, but the generic basin footprint cannot
   # fit wholly on those native category bounds. Keep the source point visible
   # as UNLOCATED, never fabricate a shifted sink or physical cabinet cutout.
   if room['id']=='PH-POWDER':
    basin_ev=page.evaluate('window.__viewerDebug.getSceneEvidence().filter(x=>x.category==="ARCH_NATIVE_BASIN_UNLOCATED_LOCATOR"||x.category==="ARCH_ILLUSTRATIVE_BASIN_NO_FAMILY")')
    if len([x for x in basin_ev if x['category']=='ARCH_NATIVE_BASIN_UNLOCATED_LOCATOR'])!=1 or any(x['category']=='ARCH_ILLUSTRATIVE_BASIN_NO_FAMILY' for x in basin_ev):
     errors.append('R056-native-countertop-basin-envelope-gate:'+key)
    elif not basin_ev[0].get('not_family_solid') or basin_ev[0].get('not_installed_clearance') is not True:
     errors.append('R056-basin-source-limitations-missing:'+key)
    elif '3D BASIN UNLOCATED' not in page.locator('#viewer-evidence-content').text_content():
     errors.append('R056-basin-source-hold-not-visible-in-owner-inspector:'+key)
    else:
     loc=basin_ev[0]
     counter=next(c for c in inst['architecture']['native_casework_proxies'] if c['id']==loc['revit_id'])
     native=counter['closest_native_plumbing_insertion']['location_native_ft']
     native_y=native[2]-inst['architecture']['native_level_elevation_ft']
     display_y=counter['max_height_ft']+.14
     if not loc.get('not_exact_native_3d_insertion') or any(abs(a-b)>1e-4 for a,b in zip(loc['source_plumbing_native_xyz_ft'],native)):
      errors.append('R056-basin-native-XYZ-or-projection-disclosure:'+key)
     if abs(loc['source_plumbing_local_y_ft']-native_y)>1e-4 or abs(loc['displayed_locator_y_ft']-display_y)>1e-4 or abs(loc['position'][1]-display_y)>1e-4:
      errors.append('R056-basin-actual-ring-Y-metadata-disagreement:'+key)
     if abs(loc['visual_y_offset_from_source_ft']-(display_y-native_y))>1e-4 or not .49<loc['visual_y_offset_from_source_ft']<.52:
      errors.append('R056-basin-raised-plan-locator-offset-undisclosed:'+key)
     visible=page.locator('#viewer-evidence-content').text_content()
     if 'PLAN-XY locator (NOT native 3D point)' not in visible or 'visual Y offset' not in visible:
      errors.append('R056-basin-XY-vs-native-Z-not-explained:'+key)
   # R055 original Revit hosted DOOR element category AABB, explicitly
   # distinct from nominal leaf type and actual unknown clear opening/swing.
   zones=[(inst.get('architecture') or {},inst['room_number'])]
   adjacent=(inst.get('architecture') or {}).get('adjacent_zone_geometry') or {}
   if adjacent:zones.append((adjacent,adjacent.get('number')))
   expected_doors={(x['id'],label) for zone,label in zones for x in zone.get('openings',[])
       if x.get('kind')=='door' and x.get('native_door_family_aabb')}
   door_wires=page.evaluate('window.__viewerDebug.getSceneEvidence().filter(x=>x.category==="ARCH_NATIVE_DOOR_FAMILY_AABB_WITNESS")')
   native_door_aabb_count+=len(door_wires)
   actual_doors={(x['revit_id'],x['room_number']) for x in door_wires}
   if actual_doors!=expected_doors:
    errors.append('native-door-AABB-room-or-ID-mismatch:'+key+':'+str(sorted(actual_doors))+' vs '+str(sorted(expected_doors)))
   for obj in door_wires:
    src=DOOR_BY_ID.get(obj['revit_id'])
    if not src or obj['host_id']!=src['host_id'] or obj['receipt_id']!=NATIVE['doors']['receipt_id']:
     errors.append('native-door-AABB-host-or-receipt-mismatch:'+key+':'+str(obj['revit_id']))
     continue
    lo,hi=src['bounds']['min'],src['bounds']['max']
    expectedDims=[hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]]
    actualDims=obj.get('native_aabb_dimensions_ft')
    if not actualDims or len(actualDims)!=3 or any(abs(a-b)>.0001 for a,b in zip(actualDims,expectedDims)):
     errors.append('native-door-AABB-geometry-vs-source-Revit-bounds:'+key+':'+str(obj['revit_id']))
    if obj.get('not_family_solid') is not True or obj.get('not_swing_or_rough_opening') is not True:
     errors.append('native-door-AABB-falsely-certified-leaf-or-clearance:'+key+':'+str(obj['revit_id']))
   if expected_doors:
    panel=page.locator('#viewer-evidence-content').text_content() or ''
    if 'Actual native Revit door ELEMENT AABB witnesses' not in panel:
     errors.append('native-door-AABB-not-visibly-separated-from-nominal:'+key)
    for nativeid,label in expected_doors:
     if str(nativeid) not in panel or str(label) not in panel:
      errors.append('native-door-AABB-missing-UI-source-ID-or-room-label:'+key+':'+str(nativeid))
   # R054: actual Revit WINDOW FAMILY ELEMENT AABB must stay distinguishable
   # from nominal opening dimensions and generic transparent glazing plane.
   zones=[(inst.get('architecture') or {},inst['room_number'])]
   adjacent=(inst.get('architecture') or {}).get('adjacent_zone_geometry') or {}
   if adjacent:zones.append((adjacent,adjacent.get('number')))
   expected_windows={(x['id'],label) for zone,label in zones for x in zone.get('openings',[])
       if x.get('kind')=='window' and x.get('native_window_family_aabb')}
   rendered_windows=page.evaluate('window.__viewerDebug.getSceneEvidence().filter(x=>x.category==="ARCH_NATIVE_WINDOW_FAMILY_AABB_WITNESS")')
   native_window_aabb_count+=len(rendered_windows)
   actual_windows={(x['revit_id'],x['room_number']) for x in rendered_windows}
   if actual_windows!=expected_windows:
    errors.append('native-window-AABB-room-or-ID-mismatch:'+key+':'+str(sorted(actual_windows))+' vs '+str(sorted(expected_windows)))
   for win in rendered_windows:
    src=WINDOW_BY_ID.get(win['revit_id'])
    if not src or win['host_id']!=src['host_id'] or win['receipt_id']!=NATIVE['windows']['receipt_id']:
     errors.append('native-window-AABB-host-or-receipt-mismatch:'+key+':'+str(win['revit_id']))
     continue
    lo,hi=src['bounds']['min'],src['bounds']['max']
    actualDims=win.get('native_aabb_dimensions_ft')
    expectedDims=[hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]]
    if not actualDims or any(abs(a-b)>.0001 for a,b in zip(actualDims,expectedDims)):
     errors.append('native-window-AABB-geometry-vs-original-Revit-bounds:'+key+':'+str(win['revit_id']))
    if win.get('not_family_solid') is not True or win.get('not_glazing_or_rough_opening') is not True:
     errors.append('native-window-AABB-falsely-certified-solid:'+key+':'+str(win['revit_id']))
   if expected_windows:
    panel=page.locator('#viewer-evidence-content').text_content() or ''
    if 'Actual native Revit window ELEMENT AABB witnesses' not in panel:
     errors.append('native-window-AABB-not-separated-from-nominal-in-visible-evidence:'+key)
    for nativeid,label in expected_windows:
     if str(nativeid) not in panel or str(label) not in panel:
      errors.append('native-window-AABB-invisible-ID-or-310-vs-311-label:'+key+':'+str(nativeid))
   # R053 Reviewer96 FIX: test the ACTUAL vertex-measured opening witness span,
   # not merely nominal family metadata. Shortened room-face runs and visual
   # wall cutaways must be declared instead of silently appearing full size.
   if inst.get('architecture'):
    depth=page.evaluate('window.__viewerDebug.getSceneEvidence().filter(x=>x.category==="ARCH_NATIVE_HOST_OPENING_DEPTH_WITNESS")')
    arch=inst['architecture']
    expected=len(arch.get('openings') or [])+len((arch.get('adjacent_zone_geometry') or {}).get('openings') or [])
    if len(depth)!=expected:
     errors.append('hosted-depth-records-vs-source-openings:'+key+':'+str(len(depth))+'/'+str(expected))
    hosted_depth_count+=len(depth)
    for witness in depth:
     nr=witness.get('nominal_width_ft');nh=witness.get('nominal_height_ft')
     rw=witness.get('rendered_width_ft');rh=witness.get('rendered_height_ft')
     gw=witness.get('geometry_rendered_width_ft');gh=witness.get('geometry_rendered_height_ft')
     if any(not isinstance(v,(float,int)) for v in (nr,nh,rw,rh,gw,gh)):
      errors.append('missing-physical-opening-witness-measurements:'+key+':'+str(witness['revit_id']))
      continue
     if abs(gw-rw)>.005 or abs(gh-rh)>.005:
      errors.append('3D-witness-vertices-vs-reported-render-span:'+key+':'+str(witness['revit_id']))
     if rw>nr+.005 or rh>nh+.005 or rw<0 or rh<0:
      errors.append('3D-witness-invented-or-negative-nominal-span:'+key+':'+str(witness['revit_id']))
     face_clip=witness.get('clipped_by_inferred_face')
     height_clip=witness.get('clipped_by_visual_cutaway')
     if nr-rw>.008 and face_clip is not True:
      errors.append('3D-witness-undisclosed-wall-face-width-clipping:'+key+':'+str(witness['revit_id']))
     if nh-rh>.008 and height_clip is not True:
      errors.append('3D-witness-undisclosed-visual-height-clipping:'+key+':'+str(witness['revit_id']))
     if witness.get('visual_classification')!=('VISUALLY_CLIPPED' if face_clip or height_clip else 'NOMINAL_SPAN_WITHIN_SOURCE_FACE'):
      errors.append('3D-witness-incorrect-visual-classification:'+key+':'+str(witness['revit_id']))
    if key=='PH-PRIMARY/304A':
     source_front=next((x for x in depth if x['revit_id']==16428722),None)
     if not source_front or not source_front['clipped_by_visual_cutaway'] or abs(source_front['rendered_height_ft']-3.05)>.02 or abs(source_front['nominal_height_ft']-8)>.02:
      errors.append('R053-304A-front-cutaway-no-longer-explicit:'+key)
    if any(o['visual_classification']=='VISUALLY_CLIPPED' for o in depth):
     panel=page.locator('#viewer-evidence-content').text_content() or ''
     if 'VISUALLY CLIPPED opening DEPTH wires' not in panel or 'UNRESOLVED' not in panel:
      errors.append('R053-displayed-clipped-extent-not-explained-in-owner-inspector:'+key)
   anchor=inst.get('architecture',{}).get('toilet_proxy_anchor')
   if anchor and anchor.get('native_family_aabb'):
    witness=page.evaluate('window.__viewerDebug.getSceneEvidence().filter(x=>x.category==="ARCH_NATIVE_TOILET_FAMILY_AABB_WITNESS")')
    if not any(x['revit_id']==anchor['native_plumbing_id'] and
      x['room_number']==inst['room_number'] and x['not_family_solid'] is True and
      len(x.get('native_aabb_dimensions_ft') or [])==3 for x in witness):
     errors.append('missing-native-toilet-AABB-vs-illustrative-proxy:'+key)
   scenes.append({'key':key,'objects':probe['count'],'registered':bool(inst.get('architecture')),'mode':probe['mode']})
   # Prevent the previously reproduced rapid-navigation black-tile capture:
   # the viewer now reports READY only after maker-image maps are uploaded
   # and the active WebGL scene is rendered. Check that real UI condition.
   try:
    page.wait_for_function('document.body.dataset.viewerMaterials === "READY"',timeout=25000)
   except Exception:
    errors.append('materials-not-ready:'+key+':'+str(page.evaluate('document.body.dataset.viewerMaterials')))
   page.wait_for_timeout(120)
   imagepath=OUT/(name+'.png')
   page.screenshot(path=str(imagepath))
   im=Image.open(imagepath).convert('RGB').crop((350,165,1180,820))
   stat=ImageStat.Stat(im)
   if sum(stat.stddev)/3<8:errors.append('low-variation-screenshot:'+key)
   all_images.append(str(imagepath))
   if idx==0:images.append(str(imagepath))
   if key in ('PH-BATH4/311A','PH-BATH4/311B'):
    page.screenshot(path=str(OUT/(name+'_detail.png')))
 # Prevent the independent reviewer96 R049 FIX from regressing: 310 is a
 # separate compartment and cannot inherit a 311-specific native ceiling ID.
 for wing in ('A','B'):
  page.evaluate('(wing)=>window.__viewerDebug.loadInstanceAddress("#PH-BATH4/311"+wing)',wing)
  expected_door,expected_host=(16428621,16428619) if wing=='A' else (12459987,12459984)
  opening_depths=page.evaluate('window.__viewerDebug.getSceneEvidence().filter(x=>x.category==="ARCH_NATIVE_HOST_OPENING_DEPTH_WITNESS")')
  if not any(o['revit_id']==expected_door and o['host_id']==expected_host and
    abs(o['native_host_thickness_ft']-.3958333)<.002 and
    abs(o['nominal_width_ft']-28/12)<.002 for o in opening_depths):
   errors.append('PH4-native-host-opening-depth-not-source-linked:'+wing)
  if wing=='A':
   for oid in (16428620,10768140):
    cut=next((x for x in opening_depths if x['revit_id']==oid and x['room_number']=='310A'),None)
    if not cut or not cut['clipped_by_visual_cutaway'] or cut['nominal_height_ft']-cut['rendered_height_ft']<2.0:
     errors.append('R053-310A-context-source-height-clipping-not-exposed:'+str(oid))
  adjacent=next(r for r in ROOMS if r['id']=='PH-BATH4')['physical_instances'][0 if wing=='A' else 1]['architecture']['adjacent_zone_geometry']
  counters=[x for x in adjacent['native_fixture_evidence'] if x['kind']=='countertop']
  expected_counter=16438318 if wing=='A' else 16438253
  if len(counters)!=1 or counters[0]['id']!=expected_counter:
   errors.append('310-missing-native-countertop-AABB-record:'+wing)
  elif counters[0]['coordinate_reference_kind']!='NATIVE_BOUNDS_CENTER' or counters[0]['native_insertion_ft'] is not None:
   errors.append('310-countertop-bounds-center-falsely-native-insertion:'+wing)
  casework=page.evaluate('window.__viewerDebug.getSceneEvidence().filter(x=>x.category==="ARCH_NATIVE_CASEWORK_AABB_STUDY")')
  if wing=='A':
   # R059 drawing A2.2 identifies 310A as WIC4, not an assigned bathroom.
   # Nearby native countertop CATEGORY bounds are real but cannot establish
   # that a floor-to-counter cabinet belongs in the closet. Preserve the
   # record as a source-only witness instead of falsely installing a sink.
   witness=page.evaluate('window.__viewerDebug.getSceneEvidence().filter(x=>x.category==="ARCH_R059_310A_UNATTRIBUTED_CASEWORK_WITNESS")')
   if any(x['revit_id']==expected_counter for x in casework):
    errors.append('R059-310A-incorrect-native-countertop-AABB-promoted-to-cabinet')
   if not any(x['revit_id']==expected_counter and x['room_number']=='310A' and
      x['not_family_solid'] is True and x['visible'] is False and
      x['receipt_id']==counters[0]['receipt_id'] for x in witness):
    errors.append('R059-310A-unattributed-native-source-countertop-witness-missing')
  elif not any(x['revit_id']==expected_counter and x['room_number']=='310B' and
    x['coordinate_reference_kind']=='NATIVE_BOUNDS_CENTER' and x['native_insertion_ft'] is None
    for x in casework):
   errors.append('310B-native-countertop-not-rendered-with-provenance')
  ph4toilet=16428804 if wing=='A' else 16377760
  srcwc=page.evaluate('window.__viewerDebug.getSceneEvidence().filter(x=>x.category==="ARCH_NATIVE_TOILET_FAMILY_AABB_WITNESS")')
  if not any(x['revit_id']==ph4toilet and x['room_number']=='310'+wing and
    x['not_family_solid'] is True for x in srcwc):
   errors.append('missing-310-native-toilet-AABB-source-witness:'+wing)
  wires=page.evaluate('window.__viewerDebug.getSceneEvidence().filter(x=>x.category==="ARCH_CEILING_EXTENT_DATUM")')
  main=next((x for x in wires if x['room_number']=='311'+wing),None)
  adj=next((x for x in wires if x['room_number']=='310'+wing),None)
  if not main or not adj:errors.append('missing-310-311-independent-ceiling-datum:'+wing)
  elif main['native_ceiling_id'] and adj['native_ceiling_id']==main['native_ceiling_id']:
   errors.append('310-inherited-311-native-GWB-id:'+wing)
  if adj and adj['native_ceiling_id'] is None and abs(adj['height_ft']-9.25)>.001:
   errors.append('310-unmatched-ceiling-not-drawing-datum:'+wing)
  gwb=page.evaluate('window.__viewerDebug.getSceneEvidence().filter(x=>x.category==="ARCH_NATIVE_GWB_AABB_WITNESS")')
  if main and main['native_ceiling_id'] and not any(x['native_ceiling_id']==main['native_ceiling_id'] for x in gwb):
   errors.append('missing-311-native-gwb-rectangle:'+wing)
  if adj and adj['native_ceiling_id'] and not any(x['native_ceiling_id']==adj['native_ceiling_id'] and x['room_number']=='310'+wing for x in gwb):
   errors.append('missing-310-independent-native-gwb-rectangle:'+wing)
  if adj and not adj['native_ceiling_id'] and any(x['room_number']=='310'+wing for x in gwb):
   errors.append('fabricated-310-native-gwb-rectangle:'+wing)
 # Source-trace toggle must affect analytical witness DRAWING visibility only:
 # original AABB data, material selection, registered solids and room evidence
 # stay unchanged; hide/show must not make invisible geometry pickable.
 for room_address in ('#PH-BATH4/311A','#TX-BATH4/007B'):
  page.evaluate('(address)=>window.__viewerDebug.loadInstanceAddress(address)',room_address)
  before=page.evaluate('window.__viewerDebug.getSceneEvidence()')
  evidence_cats=('ARCH_NATIVE_DOOR_FAMILY_AABB_WITNESS','ARCH_NATIVE_WINDOW_FAMILY_AABB_WITNESS',
     'ARCH_NATIVE_TOILET_FAMILY_AABB_WITNESS','ARCH_NATIVE_GWB_AABB_WITNESS',
     'ARCH_NATIVE_HOST_OPENING_DEPTH_WITNESS','ARCH_HOSTED_OPENING_NOMINAL_TRACE')
  trace_before=[x for x in before if x['category'] in evidence_cats]
  if not trace_before or any(x['visible'] is not False for x in trace_before):
   errors.append('R057-source-traces-not-in-clean-presentation-default:'+room_address)
  wall_before=sum(x['visible'] is True for x in before if x['category']=='ARCH_REGISTERED_WALL')
  page.locator('#viewer-toggle-source-traces').click()
  shown=page.evaluate('window.__viewerDebug.getSceneEvidence()')
  if any(x['visible'] is not True for x in shown if x['category'] in evidence_cats):
   errors.append('R057-source-trace-toggle-failed-to-restore:'+room_address)
  if sum(x['visible'] is True for x in shown if x['category']=='ARCH_REGISTERED_WALL')!=wall_before:
   errors.append('R055-source-trace-toggle-inadvertently-hidden-native-walls:'+room_address)
  if page.evaluate('window.__viewerDebug.getState().sourceTraces') is not True:
   errors.append('R055-source-trace-toggle-bad-state:'+room_address)
  page.locator('#viewer-toggle-source-traces').click()
  hidden=page.evaluate('window.__viewerDebug.getSceneEvidence()')
  if any(x['visible'] is not False for x in hidden if x['category'] in evidence_cats):
   errors.append('R057-source-trace-toggle-failed-to-hide:'+room_address)
 for wing,toilet_id in (('A',16306773),('B',16297835)):
  page.evaluate('(wing)=>window.__viewerDebug.loadInstanceAddress("#TX-BATH4/007"+wing)',wing)
  ev=page.evaluate('window.__viewerDebug.getSceneEvidence()')
  expected_door,expected_host=(16306701,16306739) if wing=='A' else (17133384,16275464)
  if not any(x['category']=='ARCH_NATIVE_HOST_OPENING_DEPTH_WITNESS' and
    x['revit_id']==expected_door and x['host_id']==expected_host and
    x['native_host_thickness_ft']>0 for x in ev):
   errors.append('007-native-host-opening-depth-not-registered:'+wing)
  if wing=='A':
   cut=next((x for x in ev if x['category']=='ARCH_NATIVE_HOST_OPENING_DEPTH_WITNESS' and x['revit_id']==16306701),None)
   if not cut or cut['clipped_by_inferred_face'] is not True or abs(cut['nominal_width_ft']-2.5)>.01 or not 2.34<cut['rendered_width_ft']<2.40:
    errors.append('R053-007A-source-face-clipped-width-not-exposed')
  if not any(x['category']=='ARCH_NATIVE_PLUMBING_INSERTION_WITNESS' and x['revit_id']==toilet_id and x['room_number']=='007'+wing for x in ev):
   errors.append('missing-007-native-toilet-insertion-witness:'+wing)
  if not any(x['category']=='PLAN_SCHEMATIC_FIXTURE' and x['kind']=='tub (UNLOCATED 2D)' for x in ev):
   errors.append('007-selected-tub-not-explicitly-unlocated:'+wing)
 tx4=next(r for r in ROOMS if r['id']=='TX-BATH4')
 for inst in tx4['physical_instances']:
  arch=inst['architecture']
  if arch.get('selected_tub_proxy') or not arch.get('selected_tub_unlocated_reason'):
   errors.append('007-native-AABB-gated-tub-false-3D:'+inst['room_number'])
 # Test documented three modes, all camera controls, walls, orbit/zoom.
 page.evaluate('window.__viewerDebug.loadInstanceAddress("#PH-BATH4/311A")')
 page.locator('#viewer-camera-top').click()
 page.screenshot(path=str(OUT/'PH4_A_plan.png'))
 page.locator('#viewer-camera-front').click()
 page.screenshot(path=str(OUT/'PH4_A_elevation.png'))
 page.locator('#viewer-camera-iso').click()
 page.locator('#toggle-walls').click()
 if page.locator('#toggle-walls').inner_text()!='Show walls':errors.append('wall-hide-failed')
 page.locator('#toggle-walls').click()
 if page.locator('#toggle-walls').inner_text()!='Hide walls':errors.append('wall-restore-failed')
 page.locator('#viewer-mode-study').click()
 if page.evaluate('document.body.dataset.viewerMode')!='study':errors.append('study-failed')
 page.locator('#viewer-mode-context').click()
 if page.evaluate('document.body.dataset.viewerMode')!='context':errors.append('context-failed')
 page.locator('#viewer-mode-full').click()
 if page.evaluate('document.body.dataset.viewerMode')!='full':errors.append('full-failed')
 # Real DOM specification inspector, rather than only a data assertion:
 page.evaluate('window.__viewerDebug.loadInstanceAddress("#PH-BATH4/311A")')
 product=page.locator('#surfaces button.surface').filter(has_text='Pienza').first
 if not product.count():errors.append('material-card-not-found')
 else:
  product.click()
  selected=page.locator('#surfaces button.surface.selected').count()
  inspector=page.locator('#material-info')
  if selected!=1 or inspector.is_hidden() or 'Pienza' not in inspector.inner_text():
   errors.append('material-inspector-card-failed')
 page.locator('#viewer-camera-inside').click()
 if page.evaluate('window.__viewerDebug.getState().preset')!='interior':
  errors.append('inside-camera-control-failed')
 page.screenshot(path=str(OUT/'PH4_A_inside_entry.png'))
 page.locator('#viewer-camera-iso').click()
 rect=page.locator('#render').bounding_box()
 if rect:
  x=rect['x']+rect['width']*.49;y=rect['y']+rect['height']*.52
  page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+150,y-75,steps=8);page.mouse.up()
  page.mouse.wheel(0,-250);page.wait_for_timeout(240)
  page.screenshot(path=str(OUT/'PH4_A_orbit_zoom.png'))
  page.locator('#reset').click()
 else:errors.append('canvas-missing')
 errors.extend(page.evaluate('window.__viewerDebug.errors.slice()'))
 browser.close()

# Gallery certification must check that every one of the 13 representative
# screenshots was physically written, decoded, and not uniformly black.
assert len(images)==13,images
from PIL import ImageOps,ImageDraw
tileW,tileH=540,360
gallery=Image.new('RGB',(tileW*4,tileH*4),(18,28,36))
draw=ImageDraw.Draw(gallery)
for i,path in enumerate(images):
 im=Image.open(path).convert('RGB');im.thumbnail((tileW-14,tileH-45))
 x=(i%4)*tileW+7;y=(i//4)*tileH+27
 gallery.paste(im,(x,y))
 draw.text((x,y-21),Path(path).stem,fill=(238,226,205))
gallery_path=OUT/'R043_ALL_13_COMPLETE_GALLERY.png'
gallery.save(gallery_path)
all_tileW,all_tileH=525,345
gallery26=Image.new('RGB',(all_tileW*4,all_tileH*7),(18,28,36))
g26=ImageDraw.Draw(gallery26)
for i,path in enumerate(all_images):
 im=Image.open(path).convert('RGB');im.thumbnail((all_tileW-15,all_tileH-44))
 x=(i%4)*all_tileW+7;y=(i//4)*all_tileH+27
 gallery26.paste(im,(x,y));g26.text((x,y-21),Path(path).stem,fill=(238,226,205))
path26=OUT/'R047_ALL_26_AB_VISUAL_GALLERY.png'
gallery26.save(path26)
result={'status':'PASS' if not errors else 'FIX','instances':len(scenes),'registered':sum(x['registered'] for x in scenes),
 'screenshots':len(images),'physical_screenshots':len(all_images),
 'source_hosted_depth_witnesses_physically_measured':hosted_depth_count,
 'source_native_window_aabb_witnesses_physically_verified':native_window_aabb_count,
 'source_native_door_aabb_witnesses_physically_verified':native_door_aabb_count,
 'gallery':str(gallery_path),'gallery_26':str(path26),'scene_results':scenes,'errors':list(dict.fromkeys(errors))}
(ROOT/'scratch/r043_arch_browser_result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='scene_results'},indent=2))
if errors:raise SystemExit(1)

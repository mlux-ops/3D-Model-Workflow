"""Physical Chrome QA for source-door-relative interior camera; scratch or final HTML.

All assertions are DISPLAY-only geometry/provenance, never room/clearance BIM QA.
"""
import json
import sys
from pathlib import Path
from PIL import Image,ImageStat,ImageDraw
from shapely.geometry import Polygon,Point
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
FINAL='--principal' in sys.argv
URL=(ROOT/('deliverables/viewer3d/index.html' if FINAL else 'scratch/r054_door_camera_preview.html')).as_uri()
DEST=ROOT/'scratch/r054_entry_gallery'
DEST.mkdir(exist_ok=True)
ROOMS=json.loads((ROOT/'deliverables/viewer3d/picks.json').read_text(encoding='utf-8'))['rooms']
CHROME=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
errors=[]
scenes=[]
images=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=CHROME,headless=True,
     args=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--no-sandbox'])
    page=browser.new_page(viewport={'width':1500,'height':980},device_scale_factor=1)
    page.on('pageerror',lambda x:errors.append('pageerror:'+str(x)))
    page.goto(URL+'#PH-BATH4/311A',wait_until='load')
    page.wait_for_function('!!window.__viewerDebug',timeout=30000)
    for room in ROOMS:
        for inst in room['physical_instances']:
            k=room['id']+'/'+inst['room_number']
            if not page.evaluate('(k)=>window.__viewerDebug.loadInstanceAddress("#"+k)',k):
                errors.append('deep-link-invalid:'+k)
                continue
            page.wait_for_function('document.body.dataset.viewerMaterials === "READY"',timeout=30000)
            page.locator('#viewer-camera-inside').click()
            e=page.evaluate('window.__viewerDebug.getCameraEvidence()')
            if not e or e['category'] not in ('CAMERA_HOSTED_DOOR_ALIGNED_EXTERIOR_CUTAWAY','CAMERA_EXTERIOR_CUTAWAY_FALLBACK'):
                errors.append('missing-exterior-cutaway-view:'+k+':'+str(e))
                continue
            if e['category']=='CAMERA_EXTERIOR_CUTAWAY_FALLBACK':
                if 'fallback' not in page.locator('#viewer-camera-state').inner_text().lower():
                    errors.append('camera-fallback-unlabeled:'+k)
                path=DEST/(room['id']+'_'+inst['room_number']+'_entry.png')
                page.screenshot(path=str(path))
                images.append(path)
                scenes.append({'room':k,'fallback_exterior_cutaway':True})
                continue
            arch=inst['architecture']
            door=next((o for o in arch['openings'] if o['id']==e['revit_id']),None)
            if not door or door['host_id']!=e['host_id']:
                errors.append('camera-not-registered-native-host:'+k)
            if e['room_assignment']!='DRAWING-INFERRED; NOT NATIVE OST_Rooms':
                errors.append('camera-false-native-room-claim:'+k)
            if not e['not_construction_clearance'] or not e['not_verified_main_entry'] or not e['not_an_interior_eye']:
                errors.append('camera-false-entry-clearance-claim:'+k)
            eye=e['eye_local_xyz_ft'];target=e['target_local_xyz_ft']
            polygon=Polygon(arch['floor_polygon_local_xz_ft'])
            if polygon.contains(Point(eye[0],eye[2])):
                errors.append('exterior-camera-incorrectly-placed-inside-room:'+k)
            if not polygon.contains(Point(target[0],target[2])):
                errors.append('camera-target-outside-inferred-room-face:'+k)
            if not .89<=e['source_inward_probe_ft']<=1.16:
                errors.append('camera-unbounded-source-wall-side-probe:'+k)
            if not page.locator('#viewer-camera-state').is_visible() or 'EXTERIOR' not in page.locator('#viewer-camera-state').inner_text():
                errors.append('camera-source-classification-not-visible:'+k)
            if e['shared_compartment_connector'] and 'connector' not in page.locator('#viewer-camera-state').inner_text():
                errors.append('shared-connector-falsely-main-entry:'+k)
            if page.evaluate('window.__viewerDebug.getState().preset')!='interior':
                errors.append('camera-control-failed:'+k)
            path=DEST/(room['id']+'_'+inst['room_number']+'_entry.png')
            page.wait_for_timeout(130)
            page.screenshot(path=str(path))
            im=Image.open(path).convert('RGB').crop((350,170,1180,825))
            if sum(ImageStat.Stat(im).stddev)/3<8:
                errors.append('camera-low-variation:'+k)
            images.append(path)
            scenes.append({'room':k,'native_door_id':e['revit_id'],
                'host_id':e['host_id'],'shared_connector':e['shared_compartment_connector'],
                'eye_local_xyz_ft':eye,'target_local_xyz_ft':target})
    errors.extend(page.evaluate('window.__viewerDebug.errors.slice()'))
    browser.close()

assert len(images)==26,(len(images),errors)
gallery=Image.new('RGB',(4*525,7*345),(17,25,33))
draw=ImageDraw.Draw(gallery)
for j,p in enumerate(images):
    img=Image.open(p).convert('RGB')
    img.thumbnail((515,305))
    x=(j%4)*525+5;y=(j//4)*345+28
    gallery.paste(img,(x,y))
    draw.text((x,y-21),p.stem,fill=(243,227,202))
gallery_path=DEST/'R054_DOORWAY_ALL26.png'
gallery.save(gallery_path)
result={'status':'PASS' if not errors else 'FIX','source':'principal' if FINAL else 'scratch-preview',
        'instance_count':len(scenes),'screenshots':len(images),
        'gallery':str(gallery_path),'scenes':scenes,'errors':list(dict.fromkeys(errors))}
out=ROOT/('scratch/r054_principal_camera_qa.json' if FINAL else 'scratch/r054_preview_camera_qa.json')
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='scenes'},indent=2))
if errors:raise SystemExit(1)

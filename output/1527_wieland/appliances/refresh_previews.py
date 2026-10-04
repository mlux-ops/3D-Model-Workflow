# -*- coding: utf-8 -*-
"""Re-export native views only; do not rebuild or save family geometry."""
import os,sys,traceback,datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from family_common import *
app=__revit__.Application
results=[]
for path in glob.glob(os.path.join(ROOT,'*','validation.json')):
    r=json.load(open(path))
    if not r.get('ok') or not r.get('saved_rfa'):continue
    project=None
    try:
        project,instance,placement=place_family(app,r['saved_rfa'])
        bounds=measure([instance])
        name='placed_oblique' if r.get('status')=='DOWNLOADED' else 'oblique'
        forward=(-1,1.5,0.8) if r['slug']=='tradewind_i32363rc' else (-1,1.5,-0.7)
        r['previews']=export_view(project,os.path.join(ROOT,r['slug'],'views'),name,bounds,forward,instance.Category.Id)
        if r.get('status')!='DOWNLOADED':
            r['previews']+=export_view(project,os.path.join(ROOT,r['slug'],'views'),'front',bounds,(0,1,-0.025),instance.Category.Id)
        r['preview_refresh_utc']=str(datetime.datetime.utcnow())
        write_json(path,r)
        results.append({'slug':r['slug'],'ok':True,'previews':r['previews']})
    except Exception:
        results.append({'slug':r['slug'],'ok':False,'error':traceback.format_exc()})
    finally:
        if project:
            try:project.Close(False)
            except Exception:pass
    write_json(os.path.join(ROOT,'preview_refresh.json'),results)

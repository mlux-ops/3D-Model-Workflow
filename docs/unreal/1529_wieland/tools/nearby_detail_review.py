"""Isolated native facade pilots plus neighbour grazing checks, with exact restoration."""
import asyncio
import json
import math
from pathlib import Path
import unreal
import wieland_site as ws
import wieland_lighting as wl
import wieland_truth as wt
import wieland_interiors as wi

OUT=Path(__file__).resolve().parent.parent/'review/phase20/nearby_detail/native_review'
DATA=Path('E:/Wieland1529_site_data/phase20/nearby_detail/meshes_facade')
TASK=None
STATE={}

def pilot_view(bid):
    d=json.loads((DATA/('NDF_'+bid+'.json')).read_text(encoding='utf-8'))
    r=json.loads((DATA/('NDF_'+bid+'.record.json')).read_text(encoding='utf-8'))
    probes=r['opening_ray_probes'];groups={}
    for p in probes:
        key=tuple(round(x,1) for x in p['direction'])
        groups.setdefault(key,[]).append(p)
    group=max(groups.values(),key=len)
    direction=group[0]['direction'];pivot=d['pivot']
    target=[sum(p['origin'][i] for p in group)/len(group)+pivot[i] for i in range(3)]
    target[2]=pivot[2]+r['measured_top_cm']*.48
    vertices=d['vertices']
    span=max(max(v[i] for v in vertices)-min(v[i] for v in vertices) for i in range(3))
    distance=max(1400,span*.95)
    loc=[target[i]-direction[i]*distance for i in range(3)]
    loc[2]+=r['measured_top_cm']*.13
    return loc,target

async def run(ids,neighbour=True):
    OUT.mkdir(parents=True,exist_ok=True)
    pre=wt.cvar('r.EyeAdaptation.CachedLightingPreExposure')
    sun=wl.by_label('LGT_Sun');sun_before=sun.get_actor_rotation()
    hidden=[];rows=[]
    try:
        wt.cvar('r.EyeAdaptation.CachedLightingPreExposure',7)
        unreal.SystemLibrary.execute_console_command(wl.world(),'DisableAllScreenMessages')
        for bid in ids:
            name='NDF_'+bid
            loc,target=pilot_view(bid)
            for actor in ws.actors():
                label=actor.get_actor_label()
                if label!=name and label.startswith(('R15_PART_','P17Z_','P17T_','NDF_','ND_')):
                    for comp in actor.get_components_by_class(unreal.PrimitiveComponent):
                        hidden.append((comp,bool(comp.get_editor_property('visible'))))
                        comp.set_visibility(False,False)
            for grazing in (False,True):
                wt.begin('S2');cam=wl.by_label(wt.CAMERA_LABEL)
                cam.set_actor_location(unreal.Vector(*loc),False,False)
                cam.set_actor_rotation(wi.look_at(loc,target),False)
                cam.camera_component.set_editor_property('field_of_view',65)
                wt._camera_exposure(cam.camera_component,13.644 if grazing else 14.644)
                if grazing:sun.set_actor_rotation(wl.sun_rotation(135,10),False)
                else:sun.set_actor_rotation(sun_before,False)
                await asyncio.sleep(2)
                rec=await wt.render(name+('_grazing' if grazing else '_neutral'),'rt',str(OUT),1920,1080,samples=8,warm_up_frames=64,nanite_mode=0)
                rec.update(isolated_pilot=True,camera_cm=loc,target_cm=target)
                rows.append(rec)
            for comp,visible in hidden:comp.set_visibility(visible,False)
            hidden=[];STATE['completed']=len(rows)
        if neighbour:
            for grazing in (False,True):
                wt.begin('S2');cam=wl.by_label(wt.CAMERA_LABEL)
                loc=(-1000,-900,2100);target=(-2650,-1250,1400)
                cam.set_actor_location(unreal.Vector(*loc),False,False)
                cam.set_actor_rotation(wi.look_at(loc,target),False)
                cam.camera_component.set_editor_property('field_of_view',65)
                wt._camera_exposure(cam.camera_component,13.644 if grazing else 14.644)
                sun.set_actor_rotation(wl.sun_rotation(135,10) if grazing else sun_before,False)
                await asyncio.sleep(2)
                rows.append(await wt.render('1533_roofXY'+('_grazing' if grazing else '_neutral'),'rt',str(OUT),1920,1080,samples=8,warm_up_frames=64,nanite_mode=0))
    finally:
        for comp,visible in hidden:comp.set_visibility(visible,False)
        wt.end();sun.set_actor_rotation(sun_before,False)
        wt.cvar('r.EyeAdaptation.CachedLightingPreExposure',pre)
        unreal.SystemLibrary.execute_console_command(wl.world(),'EnableAllScreenMessages')
    after=sun.get_actor_rotation()
    result={'views':rows,'pre_exposure_restored':wt.cvar('r.EyeAdaptation.CachedLightingPreExposure'),
            'sun_before':[sun_before.pitch,sun_before.yaw,sun_before.roll],'sun_after':[after.pitch,after.yaw,after.roll],
            'nanite':wt.cvar(wt.NANITE_MODE),'append':wt.cvar(wt.APPEND)}
    (OUT/'pilot_review.json').write_text(json.dumps(result,indent=2,default=str),encoding='utf-8')
    STATE.update(active=False,result=result)

def start(ids,neighbour=True):
    global TASK
    if STATE.get('active'):raise RuntimeError('Review already active')
    STATE.clear();STATE.update(active=True,completed=0)
    TASK=asyncio.create_task(run(ids,neighbour))
    return dict(STATE)

def status():
    if TASK is not None and TASK.done() and TASK.exception():STATE.update(active=False,error=repr(TASK.exception()))
    return dict(STATE)

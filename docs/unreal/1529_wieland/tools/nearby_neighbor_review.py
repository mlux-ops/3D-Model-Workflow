"""Immediate neighbours: real street context plus isolated side/roof diagnostics. All hiding is restored."""
import asyncio
import json
from pathlib import Path

import unreal
import wieland_lighting as wl
import wieland_truth as wt
import wieland_interiors as wi

OUT=Path(__file__).resolve().parent.parent/'review/phase20/nearby_detail/neighbours'
TASK=None
STATE={}
VIEWS=[
 ('1533_street',(-1850,1000,260),(-2700,-650,750),False),
 ('1533_lot_side_full',(-100,-1100,750),(-1600,-1100,750),True),
 ('1533_roof',(-1000,-900,2100),(-2650,-1250,1400),False),
 ('1525_street',(1000,800,200),(350,-650,450),False),
 ('1525_lot_side_full',(-1400,-1050,450),(300,-1050,450),True),
 ('1525_roof_clear',(-800,-800,1650),(350,-1000,700),True)]


async def run():
    OUT.mkdir(parents=True,exist_ok=True)
    pre=wt.cvar('r.EyeAdaptation.CachedLightingPreExposure')
    hidden=[]
    rows=[]
    try:
        wt.cvar('r.EyeAdaptation.CachedLightingPreExposure',7)
        unreal.SystemLibrary.execute_console_command(wl.world(),'DisableAllScreenMessages')
        for name,loc,target,isolate in VIEWS:
            wt.begin('S2')
            cam=wl.by_label(wt.CAMERA_LABEL)
            cam.set_actor_location(unreal.Vector(*loc),False,False)
            cam.set_actor_rotation(wi.look_at(loc,target),False)
            cam.camera_component.set_editor_property('field_of_view',90 if name=='1533_lot_side_full' else 65)
            if isolate:
                for actor in wl.actors():
                    if '/Interiors/Levels/' in actor.get_level().get_outermost().get_name():
                        for comp in actor.get_components_by_class(unreal.PrimitiveComponent):
                            hidden.append((comp,bool(comp.get_editor_property('visible'))))
                            comp.set_visibility(False,False)
            await asyncio.sleep(2)
            rec=await wt.render(name,'rt',str(OUT),1920,1080,samples=8,warm_up_frames=64,nanite_mode=0)
            rec.update(isolated_project_for_side_review=isolate,camera_cm=loc,target_cm=target)
            rows.append(rec)
            for comp,visible in hidden:comp.set_visibility(visible,False)
            hidden=[]
            STATE['completed']=len(rows)
    finally:
        for comp,visible in hidden:comp.set_visibility(visible,False)
        wt.end()
        wt.cvar('r.EyeAdaptation.CachedLightingPreExposure',pre)
        unreal.SystemLibrary.execute_console_command(wl.world(),'EnableAllScreenMessages')
    result={'views':rows,'pre_exposure_restored':wt.cvar('r.EyeAdaptation.CachedLightingPreExposure'),
            'nanite':wt.cvar(wt.NANITE_MODE),'append':wt.cvar(wt.APPEND)}
    (OUT/'review_record.json').write_text(json.dumps(result,indent=2,default=str),encoding='utf-8')
    STATE.update(active=False,result=result)


def start():
    global TASK
    STATE.clear();STATE.update(active=True,completed=0)
    TASK=asyncio.create_task(run())
    return dict(STATE)


def status():
    if TASK is not None and TASK.done() and TASK.exception():STATE.update(active=False,error=repr(TASK.exception()))
    return dict(STATE)

"""Above-canopy material diagnostics; never represented as deck views."""
import asyncio
import importlib.util
import json
from pathlib import Path

import unreal
import wieland_lighting as wl
import wieland_truth as wt

DOCS=Path(__file__).resolve().parent.parent
OUT=DOCS/'review/phase20/round2/panorama'
TASK=None
RESULT=None


async def run():
    global RESULT
    spec=importlib.util.spec_from_file_location('p20_clear_pano',DOCS/'tools/phase20r2_panorama_render.py')
    pano=importlib.util.module_from_spec(spec);spec.loader.exec_module(pano)
    sun=wl.by_label('LGT_Sun');before=sun.get_actor_rotation()
    pre=wt.cvar('r.EyeAdaptation.CachedLightingPreExposure')
    rows=[]
    try:
        wt.cvar('r.EyeAdaptation.CachedLightingPreExposure',7)
        unreal.SystemLibrary.execute_console_command(wl.world(),'DisableAllScreenMessages')
        sun.set_actor_rotation(wl.sun_rotation(75,10),False)
        for yaw in (-50,-15):
            pano.place_camera((-208.8,-1560,4000),yaw)
            cam=wl.by_label(wt.CAMERA_LABEL)
            wt._camera_exposure(cam.camera_component,12.644)
            await asyncio.sleep(2)
            rec=await wt.render('grazing_clear_y%+04d'%yaw,'rt',str(OUT),1920,1080,
                                samples=1,warm_up_frames=64,nanite_mode=0)
            rows.append(rec)
    finally:
        wt.end()
        sun.set_actor_rotation(before,False)
        wt.cvar('r.EyeAdaptation.CachedLightingPreExposure',pre)
        unreal.SystemLibrary.execute_console_command(wl.world(),'EnableAllScreenMessages')
    after=sun.get_actor_rotation()
    RESULT={'frames':rows,'diagnostic_camera_cm':[-208.8,-1560,4000],'camera_ev100':12.644,
            'sun_diagnostic':{'bearing':75,'height':10},
            'sun_before':[before.pitch,before.yaw,before.roll],'sun_after':[after.pitch,after.yaw,after.roll],
            'pre_exposure_restored':wt.cvar('r.EyeAdaptation.CachedLightingPreExposure'),
            'nanite_mode':wt.cvar(wt.NANITE_MODE),'append':wt.cvar(wt.APPEND)}
    (DOCS/'review/phase20/round2/grazing_clear_result.json').write_text(json.dumps(RESULT,indent=2,default=str),encoding='utf-8')


def start():
    global TASK
    if TASK is not None and not TASK.done():raise RuntimeError('Already running')
    TASK=asyncio.create_task(run())
    return {'started':True}


def status():return {'active':TASK is not None and not TASK.done(),'result':RESULT,
                     'error':repr(TASK.exception()) if TASK is not None and TASK.done() and TASK.exception() else None}

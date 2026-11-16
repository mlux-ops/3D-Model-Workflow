"""Final-model captures in a fresh folder. Start only after native visual acceptance."""
import asyncio
import json
from pathlib import Path
import unreal
import wieland_truth as wt
import wieland_lighting as wl
import phase20r2_panorama_render as panorama
import phase9_profile_m7 as profile

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'review/phase20/final_extension'
TASK=None
STATE={}

async def run(kind):
    pre=wt.cvar('r.EyeAdaptation.CachedLightingPreExposure')
    append=wt.cvar(wt.APPEND)
    sun=wl.by_label('LGT_Sun');sun_before=sun.get_actor_rotation()
    rows=[]
    try:
        if wt.cvar(wt.NANITE_MODE)!=0:raise RuntimeError('Nanite ray tracing must remain0')
        wt.cvar('r.EyeAdaptation.CachedLightingPreExposure',7)
        unreal.SystemLibrary.execute_console_command(wl.world(),'DisableAllScreenMessages')
        if kind in ('rt','pt'):
            folder=OUT/'stills';folder.mkdir(parents=True,exist_ok=True)
            for name in wt.VIEWS if kind=='rt' else ('D1',):
                target=folder/(name+('_realtime' if kind=='rt' else '_pathtraced')+'.0000.png')
                if target.exists():raise RuntimeError('Preserve existing capture; choose new output folder: '+str(target))
                wt.begin(name);await asyncio.sleep(2)
                rows.append(await wt.render(name,kind,str(folder),1920,1080,samples=1 if kind=='rt' else 1024,warm_up_frames=64,nanite_mode=0))
                wt.end()
                STATE['completed']=len(rows)
        elif kind in ('D1','D1S'):
            panorama.OUT=str(OUT/'panorama')
            if (OUT/'panorama'/(kind+'_y-090.0000.png')).exists():raise RuntimeError('Deck captures already exist')
            rows,end=await panorama.run(kind)
        elif kind=='grazing':
            folder=OUT/'grazing';folder.mkdir(parents=True,exist_ok=True)
            sun.set_actor_rotation(wl.sun_rotation(75,10),False)
            for yaw in (-50,-15):
                name='grazing_final_y%+04d'%yaw
                if (folder/(name+'_realtime.0000.png')).exists():raise RuntimeError('Grazing capture already exists')
                panorama.place_camera((-208.8,-1560,4000),yaw)
                wt._camera_exposure(wl.by_label(wt.CAMERA_LABEL).camera_component,12.644)
                await asyncio.sleep(2)
                rows.append(await wt.render(name,'rt',str(folder),1920,1080,samples=1,warm_up_frames=64,nanite_mode=0))
                STATE['completed']=len(rows)
        elif kind=='profile':
            folder=ROOT/'profiles/2026-11-15_P20EXT'
            rows=await profile.run(str(folder),'P20EXT',parts=('exterior','roofdeck'),skip_first_walk=True,note='Final four-block refinement with detailed neighbours')
        else:raise ValueError(kind)
        STATE.update(active=False,result=rows)
    except Exception as exc:STATE.update(active=False,error=repr(exc))
    finally:
        wt.end();sun.set_actor_rotation(sun_before,False);wt.cvar(wt.APPEND,append)
        wt.cvar('r.EyeAdaptation.CachedLightingPreExposure',pre)
        unreal.SystemLibrary.execute_console_command(wl.world(),'EnableAllScreenMessages')
        STATE['settings_after']={'nanite':wt.cvar(wt.NANITE_MODE),'append':wt.cvar(wt.APPEND),'pre_exposure':wt.cvar('r.EyeAdaptation.CachedLightingPreExposure')}
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/(kind+'_receipt.json')).write_text(json.dumps(STATE,indent=2,default=str),encoding='utf-8')

def start(kind):
    global TASK
    if STATE.get('active'):raise RuntimeError('Capture already active')
    STATE.clear();STATE.update(active=True,kind=kind,completed=0)
    TASK=asyncio.create_task(run(kind));return dict(STATE)

def status():return dict(STATE)

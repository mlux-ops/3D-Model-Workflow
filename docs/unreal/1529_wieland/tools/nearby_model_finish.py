"""Finish staged geometry after the current facade import. No final renders or videos."""
import asyncio
import importlib
import json
from pathlib import Path
import unreal
import nearby_facade_import as fi
import nearby_streets_import as si
import nearby_ground_import as gi
import wieland_site as ws

OUT=Path(__file__).resolve().parent.parent/'review/phase20/nearby_detail'
STATE={}
TASK=None

def record(stage,**values):
    STATE.update(stage=stage,**values)
    (OUT/'model_finish_status.json').write_text(json.dumps(STATE,indent=2,default=str),encoding='utf-8')

async def run():
    try:
        record('waiting_for_facade_import',active=True)
        if fi.TASK is not None:await fi.TASK
        if fi.status().get('error'):raise RuntimeError(fi.status()['error'])
        if fi.status().get('completed')!=679:raise RuntimeError('679 remaining facade imports required')
        importlib.reload(fi)
        record('updating_shared_roof_finish')
        roof=unreal.load_asset(fi.MATERIALS+'/MI_NDF_Roof')
        for key,name in [('BaseColorMap','BaseColor'),('NormalMap','Normal')]:
            texture=unreal.load_asset(fi.BITUMEN+name)
            if texture is None or not unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(roof,key,texture):raise RuntimeError('Roof texture update failed')
        unreal.MaterialEditingLibrary.update_material_instance(roof)
        unreal.EditorAssetLibrary.save_loaded_asset(roof,False)
        await asyncio.sleep(0)
        record('copying_bare_earth_ground')
        ground=gi.apply()
        record('importing_all_streets',ground=ground)
        qc=json.loads((OUT/'street_qc.json').read_text())
        if not qc['passed'] or qc['tiles']!=180:raise RuntimeError('Full street QC required')
        si.start([r['name'] for r in qc['records']])
        await si.TASK
        if si.status().get('error'):raise RuntimeError(si.status()['error'])
        record('activating_facades')
        facade=json.loads((OUT/'facade_qc_all.json').read_text())
        if facade['passed']!=682 or facade['failures']:raise RuntimeError('Full facade QC required')
        result=fi.activate([r['county_id'] for r in facade['records']],save=True)
        record('geometry_ready_for_visual_review',active=False,facade=result,streets=si.status(),dirty=ws.dirty())
    except Exception as exc:record('error',active=False,error=repr(exc))

def start():
    global TASK
    if TASK is not None and not TASK.done():raise RuntimeError('Already active')
    TASK=asyncio.create_task(run());return {'started':True}

def status():return dict(STATE)

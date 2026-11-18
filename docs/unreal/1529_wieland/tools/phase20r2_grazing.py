"""Phase 20 round 2: the changed materials under grazing light, as round 1's J7.

Two real-time frames from the D1S eye (pitch 4, 30 degree field): yaw -50 (Gold Coast: Hancock, Water Tower
Place, 900 N Michigan, Palmolive, Park Tower, Lake Point) and yaw -15 (River North and the Loop: Trump, 330 N
Wabash, Aqua, St. Regis, Chase, 300 N LaSalle, NEMA), with the sun 10 degrees up from the east, so the east
faces are lit at a grazing angle. The sun's rotation is read before, put back after, and read back; its level is
saved by name afterwards only if it had no unsaved change before.
In execute_python:  exec(...); out = await g['run']()
"""
import os
import sys

import unreal

TOOLS = r'E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools'
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import wieland_lighting as wl  # noqa: E402
import wieland_truth as wt  # noqa: E402

PANO = TOOLS + '/phase20r2_panorama_render.py'
_g = {'__name__': 'pano'}
exec(compile(open(PANO).read(), PANO, 'exec'), _g)
OUT = TOOLS.replace('/tools', '/review/phase20/round2/panorama')


async def run():
    sun = wl.by_label('LGT_Sun')
    before = sun.get_actor_rotation()
    pkg = sun.get_level().get_outermost()
    was_dirty = pkg.get_name() in [p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
    records = []
    try:
        sun.set_actor_rotation(wl.sun_rotation(90.0, 10.0), False)
        await wl.wait_frames(5.0)
        for yaw in (-50.0, -15.0):
            name = 'grazing_D1S_y%+04d' % int(yaw)
            _g['place_camera'](_g['EYES']['D1S'], yaw)
            await wl.wait_frames(15.0)
            rec = await wt.render(name, 'rt', OUT, 1920, 1080, warm_up_frames=64, nanite_mode=0)
            records.append((name, rec.get('file_bytes'), wt.cvar(wt.NANITE_MODE)))
    finally:
        wt.end()
        sun.set_actor_rotation(before, False)
    after = sun.get_actor_rotation()
    saved = None
    if not was_dirty:
        saved = unreal.EditorLoadingAndSavingUtils.save_packages([pkg], True)
    return {'frames': records, 'sun_before': [round(before.pitch, 2), round(before.yaw, 2)],
            'sun_after': [round(after.pitch, 2), round(after.yaw, 2)], 'sun_level': pkg.get_name(),
            'level_was_dirty': was_dirty, 'level_saved_back': saved, 'read_sun': wl.read_sun()}

"""Phase 20 round 2: the roof-deck panorama frames, as round 1 (J6) and Phase 17 (J18): five real-time frames
per deck, yaw -90 to +30 in 30 degree steps (yaw 0 looks level south, -90 east), pitch 4 degrees up, 30 degree
horizontal field, 1,920 by 1,080, through the Movie Render Graph (wieland_truth.render), one at a time, with
r.RayTracing.Nanite.Mode read back 0 for every frame.

Run inside the editor with DECK set in the exec globals ('D1' or 'D1S'); call_tool and asyncio are not needed.
Writes review/phase20/round2/panorama/<deck>_y<yaw>.0000.png and appends a record per frame to frames.jsonl.
"""
import json
import os
import shutil
import sys

import unreal

TOOLS = r'E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools'
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import wieland_lighting as wl  # noqa: E402
import wieland_truth as wt  # noqa: E402

OUT = TOOLS.replace('/tools', '/review/phase20/round2/panorama')
EYES = {'D1': (-1300.0, -1560.0, 1684.0), 'D1S': (-208.8, -1560.0, 1684.0)}
YAWS = (-90.0, -60.0, -30.0, 0.0, 30.0)
PITCH = 4.0
FOV = 30.0


def place_camera(loc, yaw):
    wt.end(restore_nanite=False)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    rot = unreal.Rotator(pitch=PITCH, yaw=yaw, roll=0.0)
    cam = eas.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), rot)
    cam.set_actor_label(wt.CAMERA_LABEL)
    cam.tags = [wl.TAG_TEMP, 'panorama']
    comp = cam.camera_component
    comp.set_editor_property('field_of_view', FOV)
    comp.set_editor_property('constrain_aspect_ratio', True)
    comp.set_editor_property('aspect_ratio', 16.0 / 9.0)
    label, ev100 = wt.exposure_at(unreal.Vector(*loc))
    wt._camera_exposure(comp, ev100)
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.pilot_level_actor(cam)
    les.editor_set_viewport_realtime(True)
    unreal.SystemLibrary.execute_console_command(wl.world(), 'viewmode lit')
    return {'exposure_from': label, 'ev100': round(ev100, 3), 'stand_ins_hidden': wt._stand_ins(True)}


async def run(deck, yaws=YAWS):
    """Render the given yaws of one deck (two at a time keeps each call short of the tool's time limit)."""
    os.makedirs(OUT, exist_ok=True)
    if wt.cvar(wt.NANITE_MODE) != 0:
        raise RuntimeError('r.RayTracing.Nanite.Mode does not read 0; not rendering')
    records = []
    try:
        for yaw in yaws:
            name = '%s_y%+04d' % (deck, int(yaw))
            info = place_camera(EYES[deck], yaw)
            await wl.wait_frames(15.0)
            rec = await wt.render(name, 'rt', OUT, 1920, 1080, warm_up_frames=64, nanite_mode=0)
            src = os.path.join(OUT, name + '_realtime.0000.png')
            dst = os.path.join(OUT, name + '.0000.png')
            if os.path.exists(src):
                shutil.move(src, dst)
            rec.update(info)
            rec.update({'deck': deck, 'yaw': yaw, 'pitch': PITCH, 'fov': FOV, 'image': dst,
                        'nanite_mode_after': wt.cvar(wt.NANITE_MODE), 'bytes': os.path.getsize(dst) if os.path.exists(dst) else 0})
            records.append(rec)
            with open(os.path.join(OUT, 'frames.jsonl'), 'a', encoding='utf-8') as h:
                h.write(json.dumps(rec, default=str) + '\n')
    finally:
        end = wt.end()
    return records, end


def summary(records, end):
    return '; '.join('%s %s bytes, %s s, nanite %s' % (os.path.basename(r['image']), r['bytes'], r.get('seconds_waited'),
                                                      r['nanite_mode_after']) for r in records) + ' | end ' + json.dumps(end, default=str)
# In execute_python:  exec(...definitions...); records, end = await g['run']('D1'); g['summary'](records, end)

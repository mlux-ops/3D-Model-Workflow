"""Phase 11, step 11.5: make the level sequences that carry the fixed camera paths into the packaged build. NEW assets.

The packaged build has no editor and no Python, so the paths and holds that Phase 9 measured with the editor's camera
(tools/phase6_profile_m4.py, tools/phase9_profile_m7.py, tools/wieland_profile.py) are written into level sequences:

    /Game/Wieland1529/Delivery/Profile/SEQ_W1529_Prof_<segment>   one per path or hold, a plain camera (90 degrees,
                                                                  like the editor's camera) that the sequence creates
                                                                  itself, a key on every frame, a camera cut
    /Game/Wieland1529/Delivery/Profile/SEQ_W1529_ProfilePaths     the master: one shot per segment, end to end

Each shot is named after its segment. The engine writes the shot's name into the frame-time record (CSV profiler)
when the shot starts (LevelSequencePlayer.cpp, CSV_EVENT_GLOBAL), so every frame of the record can be given to its
segment. Each part starts with an 8-second hold at its first point ("settle_<part>") so that the unit levels of
the building stream in before the measured path begins, as Phase 9 waited 8 seconds before each recording.

Geometry is the same as Phase 9's: "path" moves in a straight line and looks at a target; "route" walks at one speed
along points and looks 150 cm ahead, level (pitch 0); a hold stands still. Nothing is added to any level. Saves the
new assets only; refuses to run if the master already exists. Writes review/phase11/profile_segments.json.
"""
import sys, json, math, os, importlib
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import phase6_profile_m4 as m4
import wieland_interiors as wi
importlib.reload(m4)

BASE = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase11/"
FOLDER = "/Game/Wieland1529/Delivery/Profile"
MASTER = FOLDER + "/SEQ_W1529_ProfilePaths"
FPS = 30
SETTLE = 8.0
LOOK_AHEAD = 150.0


def route_point(points, distance):
    for index in range(len(points) - 1):
        a, b = points[index], points[index + 1]
        leg = sum((b[k] - a[k]) ** 2 for k in range(3)) ** 0.5
        if distance <= leg or index == len(points) - 2:
            t = min(1.0, distance / leg) if leg > 0.0 else 1.0
            return [a[k] + (b[k] - a[k]) * t for k in range(3)]
        distance -= leg
    return list(points[-1])


def look_at(loc, target):
    dx, dy, dz = (target[k] - loc[k] for k in range(3))
    return [math.degrees(math.atan2(dz, (dx * dx + dy * dy) ** 0.5)), math.degrees(math.atan2(dy, dx)), 0.0]


def frames_for(job, seconds):
    """[(loc, [pitch, yaw, roll])] for every frame of a job, as wieland_profile._place does it."""
    count = int(round(seconds * FPS))
    out = []
    if job["kind"] == "route":
        points = job["points"]
        total = sum(sum((points[i + 1][k] - points[i][k]) ** 2 for k in range(3)) ** 0.5 for i in range(len(points) - 1))
        yaw = None
        for f in range(count):
            fraction = f / float(count - 1) if count > 1 else 0.0
            here = route_point(points, total * fraction)
            ahead = route_point(points, min(total, total * fraction + LOOK_AHEAD))
            dx, dy = ahead[0] - here[0], ahead[1] - here[1]
            if (dx * dx + dy * dy) ** 0.5 > 5.0 or yaw is None:
                yaw = math.degrees(math.atan2(dy, dx))
            out.append((here, [0.0, yaw, 0.0]))
        return out
    for f in range(count):
        fraction = f / float(count - 1) if count > 1 else 0.0
        loc = list(job["loc"])
        if job["kind"] == "path":
            loc = [loc[k] + (job["end"][k] - loc[k]) * fraction for k in range(3)]
        rot = look_at(loc, job["target"]) if job.get("target") is not None else list(job["rot"])
        out.append((loc, rot))
    return out


def settle_of(job):
    first = frames_for(job, 2.0 / FPS)[0]
    return {"kind": "view", "loc": first[0], "rot": first[1]}


def unwrap(values):
    out, offset, last = [], 0.0, None
    for v in values:
        if last is not None:
            while v + offset - last > 180.0:
                offset -= 360.0
            while v + offset - last < -180.0:
                offset += 360.0
        out.append(v + offset)
        last = v + offset
    return out


# The segments, in order: (name, job, seconds). Jobs are Phase 9's, read from its tools so they cannot drift.
P = {name: dict(job) for part in m4.PARTS.values() for job in part[1] for name in [job["name"].replace("M4_", "", 1)]}
SEGMENTS = [
    ("settle_exterior", settle_of(P["exterior_path"]), SETTLE),
    ("exterior_path", P["exterior_path"], 60.0),
    ("hold_S1", P["hold_S1"], 10.0),
    ("hold_S2", P["hold_S2"], 10.0),
    ("hold_S6", P["hold_S6"], 10.0),
    ("settle_triplex", settle_of(P["triplex_path"]), SETTLE),
    ("triplex_path", P["triplex_path"], 30.0),
    ("hold_D5", P["hold_D5"], 10.0),
    ("settle_penthouse", settle_of(P["penthouse_path_indoors"]), SETTLE),
    ("penthouse_path_indoors", P["penthouse_path_indoors"], 20.0),
    ("hold_D2", P["hold_D2"], 10.0),
    ("settle_roofdeck", settle_of(P["penthouse_path_roof_deck"]), SETTLE),
    ("roof_deck_path", P["penthouse_path_roof_deck"], 10.0),
]

if unreal.EditorAssetLibrary.does_asset_exist(MASTER):
    raise RuntimeError("the asset %s already exists; this tool does not overwrite" % MASTER)
tools = unreal.AssetToolsHelpers.get_asset_tools()
LINEAR = unreal.MovieSceneKeyInterpolation.LINEAR
CONSTANT = unreal.MovieSceneKeyInterpolation.CONSTANT
made, record, start = [], [], 0
for name, job, seconds in SEGMENTS:
    frames = frames_for(job, seconds)
    asset = "SEQ_W1529_Prof_" + name
    sub = tools.create_asset(asset, FOLDER, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    sub.set_display_rate(unreal.FrameRate(FPS, 1))
    sub.set_playback_start(0)
    sub.set_playback_end(len(frames))
    camera = sub.add_spawnable_from_class(unreal.CameraActor)
    camera.set_display_name("W1529_ProfileCamera")
    track = camera.add_track(unreal.MovieScene3DTransformTrack)
    section = track.add_section()
    section.set_range(0, len(frames))
    channels = section.get_all_channels()
    yaws = unwrap([rot[1] for _, rot in frames])
    for f, ((loc, rot), yaw) in enumerate(zip(frames, yaws)):
        interp = CONSTANT if f == len(frames) - 1 else LINEAR
        for index, value in enumerate((loc[0], loc[1], loc[2], rot[2], rot[0], yaw)):
            channels[index].add_key(unreal.FrameNumber(f), value, 0.0, unreal.MovieSceneTimeUnit.DISPLAY_RATE, interp)
    cut = sub.add_track(unreal.MovieSceneCameraCutTrack)
    cut_section = cut.add_section()
    cut_section.set_range(0, len(frames))
    cut_section.set_camera_binding_id(sub.get_binding_id(camera))
    made.append((name, sub, len(frames)))
    record.append({"segment": name, "kind": job["kind"], "start_s": start / float(FPS), "seconds": len(frames) / float(FPS),
                   "first": {"loc": [round(v, 1) for v in frames[0][0]], "rot": [round(v, 2) for v in frames[0][1]]},
                   "last": {"loc": [round(v, 1) for v in frames[-1][0]], "rot": [round(v, 2) for v in frames[-1][1]]},
                   "keys": [len(c.get_keys()) for c in channels[:6]]})
    start += len(frames)

master = tools.create_asset("SEQ_W1529_ProfilePaths", FOLDER, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
master.set_display_rate(unreal.FrameRate(FPS, 1))
master.set_playback_start(0)
master.set_playback_end(start)
shots = master.add_track(unreal.MovieSceneCinematicShotTrack)
at = 0
for name, sub, count in made:
    shot = shots.add_section()
    shot.set_sequence(sub)
    shot.set_range(at, at + count)
    shot.set_shot_display_name(name)
    at += count

saved = {}
for name, sub, _ in made:
    saved[name] = bool(unreal.EditorAssetLibrary.save_asset(sub.get_path_name().split(".")[0], False))
saved["master"] = bool(unreal.EditorAssetLibrary.save_asset(MASTER, False))
with open(BASE + "profile_segments.json", "w", encoding="utf-8") as handle:
    json.dump({"master": MASTER, "fps": FPS, "total_seconds": start / float(FPS), "segments": record}, handle, indent=1)
dirty = [p.get_name() for p in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())]
json.dumps({"master": MASTER, "frames": start, "seconds": start / float(FPS), "shots": [str(s.get_shot_display_name()) for s in shots.get_sections()],
            "saved": saved, "dirty": dirty})

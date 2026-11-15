"""Phase 19: turn a walking path the owner drew on the plan page into a video.

The page (owner_review/paths/index.html, served by path_server.py) saves each path as owner_review/paths/<name>.json
(format in KICKOFF_PHASE19.md). This module:

1. plan(path)             camera frames: a smooth curve through the points (centripetal Catmull-Rom) walked at the
                          path's speed, easing in and out of every start, stop and pause; stair segments go straight from
                          point to point, rising evenly, at 60 percent of the walking speed; lift segments rise
                          vertically at 1.0 m/s at the first point, then move level to the next; the look follows each
                          point's mode ("forward": a point 1.5 m ahead on the path; "target": a point; "yaw": a held
                          direction, page dial yaw_deg, Unreal yaw = yaw_deg - 90, see plans/manifest.json), smoothed
                          forward and backward so turns ease in and out and the picture never jerks.
2. check_sight(path, frames)  in the editor: a line trace along every walked segment at eye height; a hit on a wall,
                          floor or other solid object refuses the path, with the object and the place. Doors and door
                          panels, glass sliding panels, curtains and furniture under 0.5 m high are passable; stair and
                          lift segments are not checked.
3. build_sequence(...)    in the editor: a level sequence (a new asset under /Game/Wieland1529/Delivery/Paths/, named by
                          the path and its checksum, so nothing is overwritten or deleted) with a spawned camera keyed
                          on every frame (place, direction, exposure), as Phase 11's seq_build.py.
4. start_render(...)      Movie Render Graph quick render of that sequence in the editor's world, real time (path traced
                          only if the path asks "pathtraced"), at the path's resolution and frame rate, one run with a
                          long warm-up (Phase 11's lesson: runs joined later show brightness steps).
5. encode(...)            ffmpeg to H.264 MP4 in delivery/video_paths/<name>.mp4, with <name>.json beside it (duration,
                          frames, path checksum, render time).
6. render_requested()     one call: every path with render_requested_at set and no up-to-date video (newer than the
                          request and made from the same checksum) is checked, rendered and encoded, one at a time, on the
                          editor's ticks (it returns at once); writes owner_review/paths/last_render.json.

Rules kept: r.RayTracing.Nanite.Mode must read 0 (never changed here); every console variable changed for a render is
put back and read back; named assets only are saved (the new sequence); no editor restart.
"""

import datetime
import hashlib
import json
import math
import os
import re
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, "/")
DOCS = HERE.rsplit("/", 1)[0]
PATHS_DIR = DOCS + "/owner_review/paths"
VIDEO_DIR = DOCS + "/delivery/video_paths"
FRAMES_ROOT = "D:/Wieland1529_delivery/video_paths_frames"
SEQ_FOLDER = "/Game/Wieland1529/Delivery/Paths"
FFMPEG = ("C:/Users/cowey/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/"
          "ffmpeg-9.0.2-full_build/bin/")
NAME_OK = re.compile(r"^[A-Za-z0-9 _-]{1,80}$")
LOOK_AHEAD_CM = 150.0
STAIR_FACTOR = 0.6
LIFT_CM_S = 100.0
EASE_S = 0.8
LOOK_TAU_S = 0.6
EV_TAU_S = 0.6
WARM_UP = 256
QUALITY = ("sg.GlobalIlluminationQuality", "sg.ReflectionQuality", "sg.ShadowQuality")
PRE_EXPOSURE = "r.EyeAdaptation.CachedLightingPreExposure"
BASE_EV = 14.644


# ------------------------------------------------------------------------------------------------- reading a path

def safe_name(name):
    return re.sub(r"[^A-Za-z0-9_-]+", "_", name.strip())


def checksum(file_path):
    return hashlib.sha256(open(file_path, "rb").read()).hexdigest()


def load(file_path):
    """The path as saved by the page, with defaults; raises ValueError with a plain reason if it cannot be used."""
    with open(file_path, encoding="utf-8") as h:
        p = json.load(h)
    name = str(p.get("name", ""))
    if not NAME_OK.match(name):
        raise ValueError("name %r: only letters, digits, spaces, hyphens and underscores are allowed" % name)
    pts = p.get("points") or []
    if len(pts) < 2:
        raise ValueError("a path needs at least two points")
    for k, q in enumerate(pts):
        for key in ("x_cm", "y_cm", "z_cm"):
            if not isinstance(q.get(key), (int, float)):
                raise ValueError("point %d has no number for %s" % (k + 1, key))
    p.setdefault("speed_m_per_s", 1.2)
    p.setdefault("fps", 30)
    p.setdefault("resolution", [1920, 1080])
    p.setdefault("quality", "realtime")
    if not (0.2 <= float(p["speed_m_per_s"]) <= 5.0):
        raise ValueError("speed %.2f m/s is outside 0.2 to 5.0" % float(p["speed_m_per_s"]))
    if int(p["fps"]) not in (24, 25, 30, 50, 60):
        raise ValueError("frame rate %s is not one of 24, 25, 30, 50, 60" % p["fps"])
    return p


# ------------------------------------------------------------------------------------------------- planning

def _catmull(p0, p1, p2, p3, n):
    """Centripetal Catmull-Rom from p1 to p2 (alpha 0.5), n + 1 samples including both ends."""
    def tj(ti, a, b):
        d = math.dist(a, b)
        return ti + max(d, 1e-3) ** 0.5
    t0 = 0.0
    t1 = tj(t0, p0, p1)
    t2 = tj(t1, p1, p2)
    t3 = tj(t2, p2, p3)
    out = []
    for k in range(n + 1):
        t = t1 + (t2 - t1) * k / n
        def lerp(a, b, ta, tb):
            w = (t - ta) / (tb - ta) if tb != ta else 0.0
            return [a[i] + (b[i] - a[i]) * w for i in range(3)]
        a1, a2, a3 = lerp(p0, p1, t0, t1), lerp(p1, p2, t1, t2), lerp(p2, p3, t2, t3)
        b1, b2 = lerp(a1, a2, t0, t2), lerp(a2, a3, t1, t3)
        out.append(lerp(b1, b2, t1, t2))
    return out


def _segments(p):
    """Dense polyline of every segment: [(kind, [[x, y, z], ...], start point index)]."""
    P = [[float(q["x_cm"]), float(q["y_cm"]), float(q["z_cm"])] for q in p["points"]]
    kinds = [str(q.get("segment", "walk")) for q in p["points"]]
    segs = []
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]
        kind = kinds[i] if kinds[i] in ("stair", "lift") else "walk"
        if kind == "stair":
            n = max(2, int(math.dist(a, b) / 2.0))
            pts = [[a[j] + (b[j] - a[j]) * k / n for j in range(3)] for k in range(n + 1)]
        elif kind == "lift":
            n1 = max(2, int(abs(b[2] - a[2]) / 2.0))
            up = [[a[0], a[1], a[2] + (b[2] - a[2]) * k / n1] for k in range(n1 + 1)]
            n2 = max(2, int(math.dist(a[:2], b[:2]) / 2.0))
            level = [[a[0] + (b[0] - a[0]) * k / n2, a[1] + (b[1] - a[1]) * k / n2, b[2]] for k in range(1, n2 + 1)]
            pts = up + level
        else:
            # Neighbours across a floor change, or at the ends, are reflected so the curve does not reach for them.
            p0 = P[i - 1] if i > 0 and kinds[i - 1] not in ("stair", "lift") else [2 * a[j] - b[j] for j in range(3)]
            p3 = P[i + 2] if i + 2 < len(P) and kinds[i + 1] not in ("stair", "lift") else [2 * b[j] - a[j] for j in range(3)]
            n = max(4, int(math.dist(a, b) / 2.0))
            pts = _catmull(p0, a, b, p3, n)
            for k, q in enumerate(pts):  # walking stays level between two points on one floor
                q[2] = a[2] + (b[2] - a[2]) * (k / max(len(pts) - 1, 1))
        segs.append((kind, pts, i))
    return segs


def _speed_profile(total, v, fps):
    """Arc-length positions, one per frame, for one stretch walked from rest to rest: trapezoid of speed with ramps
    of EASE_S (shorter when the stretch is short)."""
    if total <= 0:
        return [0.0]
    ramp = min(EASE_S, total / v / 2.0)
    acc = v / ramp if ramp > 0 else 1e9
    d_ramp = 0.5 * acc * ramp * ramp
    if 2 * d_ramp > total:
        ramp = math.sqrt(total / acc)
        vmax = acc * ramp
        cruise = 0.0
    else:
        vmax = v
        cruise = (total - 2 * d_ramp) / v
    T = 2 * ramp + cruise
    n = max(1, int(round(T * fps)))
    out = []
    for k in range(n + 1):
        t = T * k / n
        if t < ramp:
            s = 0.5 * acc * t * t
        elif t < ramp + cruise:
            s = 0.5 * acc * ramp * ramp + vmax * (t - ramp)
        else:
            td = T - t
            s = total - 0.5 * acc * td * td
        out.append(min(max(s, 0.0), total))
    return out


def _resample(poly, positions):
    cum = [0.0]
    for a, b in zip(poly, poly[1:]):
        cum.append(cum[-1] + math.dist(a, b))
    out, j = [], 0
    for s in positions:
        while j < len(cum) - 2 and cum[j + 1] < s:
            j += 1
        seg = cum[j + 1] - cum[j]
        w = (s - cum[j]) / seg if seg > 0 else 0.0
        a, b = poly[j], poly[j + 1]
        out.append([a[i] + (b[i] - a[i]) * w for i in range(3)])
    return out, cum[-1]


def _smooth(values, tau_frames):
    """Forward then backward exponential smoothing: no lag, eased starts and ends of every turn."""
    if tau_frames <= 0 or len(values) < 3:
        return list(values)
    a = 1.0 - math.exp(-1.0 / tau_frames)
    f = list(values)
    for k in range(1, len(f)):
        f[k] = f[k - 1] + a * (f[k] - f[k - 1])
    for k in range(len(f) - 2, -1, -1):
        f[k] = f[k + 1] + a * (f[k] - f[k + 1])
    return f


def plan(p):
    """Frames [{"f", "loc", "rot" (pitch, yaw, roll)}] and a summary. Walking stretches run from rest to rest: a
    stretch ends at a pause, at a floor change, and at the end of the path."""
    fps = int(p["fps"])
    v = float(p["speed_m_per_s"]) * 100.0
    segs = _segments(p)
    pts_meta = p["points"]
    locs, seg_of = [], []
    stretch, stretch_segs = [], []

    def flush():
        if not stretch:
            return
        poly = []
        for s_ in stretch:
            poly += s_ if not poly else s_[1:]
        total = sum(math.dist(a, b) for a, b in zip(poly, poly[1:]))
        kind = segs[stretch_segs[0]][0]
        speed = v * (STAIR_FACTOR if kind == "stair" else 1.0)
        if kind == "lift":
            speed = LIFT_CM_S
        pos = _speed_profile(total, speed, fps)
        out, _ = _resample(poly, pos)
        # which segment each frame belongs to (for the look and the sight check)
        bounds, acc = [], 0.0
        for k, s_ in zip(stretch_segs, stretch):
            acc += sum(math.dist(a, b) for a, b in zip(s_, s_[1:]))
            bounds.append((acc, k))
        for s, q in zip(pos, out):
            k = next((kk for b, kk in bounds if s <= b + 1e-6), bounds[-1][1])
            if locs and math.dist(locs[-1], q) < 1e-6 and seg_of and seg_of[-1] == k:
                continue
            locs.append(q)
            seg_of.append(k)
        stretch.clear()
        stretch_segs.clear()
    for k, (kind, poly, i) in enumerate(segs):
        prev_kind = segs[k - 1][0] if k else None
        if stretch and (kind != "walk" or prev_kind != "walk"):
            flush()
        stretch.append(poly)
        stretch_segs.append(k)
        pause = float(pts_meta[i + 1].get("pause_s", 0) or 0) if i + 1 < len(pts_meta) - 1 else 0.0
        if kind != "walk" or pause > 0:
            flush()
        if pause > 0:
            for _ in range(int(round(pause * fps))):
                locs.append(list(locs[-1]))
                seg_of.append(k)
    flush()
    # Hold at the end, so the last view can be read: 0.5 s, or the last point's pause; during it the last point's own
    # look applies (a target or a held direction set on the last point turns the camera there as it stops).
    n_walk = len(locs)
    for _ in range(max(int(fps * 0.5), int(round(float(pts_meta[-1].get("pause_s", 0) or 0) * fps)))):
        locs.append(list(locs[-1]))
        seg_of.append(seg_of[-1])
    last_look = pts_meta[-1].get("look") or {"mode": "forward"}
    # Look: each point's mode applies from that point to the next.
    yaws, pitches = [], []
    for f, (q, k) in enumerate(zip(locs, seg_of)):
        look = pts_meta[segs[k][2]].get("look") or {"mode": "forward"}
        if f >= n_walk and last_look.get("mode") in ("target", "yaw"):
            look = last_look
        mode = look.get("mode", "forward")
        if mode == "target" and all(isinstance(look.get(c), (int, float)) for c in ("x_cm", "y_cm", "z_cm")):
            dx, dy, dz = look["x_cm"] - q[0], look["y_cm"] - q[1], look["z_cm"] - q[2]
            yaw = math.degrees(math.atan2(dy, dx))
            pitch = math.degrees(math.atan2(dz, math.hypot(dx, dy)))
        elif mode == "yaw":
            yaw = float(look.get("yaw_deg", 0.0)) - 90.0
            pitch = float(look.get("pitch_deg", 0.0))
        else:
            ahead, dist, j = q, 0.0, f
            while j + 1 < len(locs) and dist < LOOK_AHEAD_CM:
                dist += math.dist(locs[j], locs[j + 1])
                j += 1
                ahead = locs[j]
            dx, dy = ahead[0] - q[0], ahead[1] - q[1]
            if math.hypot(dx, dy) < 5.0:
                yaw = yaws[-1] if yaws else 0.0
            else:
                yaw = math.degrees(math.atan2(dy, dx))
            pitch = -4.0 if segs[k][0] == "walk" else max(-25.0, min(15.0, math.degrees(math.atan2(ahead[2] - q[2], max(math.hypot(dx, dy), 1.0)))))
        if yaws:  # unwrap
            while yaw - yaws[-1] > 180.0:
                yaw -= 360.0
            while yaw - yaws[-1] < -180.0:
                yaw += 360.0
        yaws.append(yaw)
        pitches.append(pitch)
    yaws = _smooth(yaws, LOOK_TAU_S * fps)
    pitches = _smooth(pitches, LOOK_TAU_S * fps)
    frames = [{"f": f, "loc": [round(c, 2) for c in q], "rot": [round(pi, 3), round(ya, 3), 0.0], "segment": seg_of[f]}
              for f, (q, pi, ya) in enumerate(zip(locs, pitches, yaws))]
    steps = [math.dist(a["loc"], b["loc"]) for a, b in zip(frames, frames[1:])] or [0.0]
    turns = [abs(b["rot"][1] - a["rot"][1]) for a, b in zip(frames, frames[1:])] or [0.0]
    walk_len = sum(sum(math.dist(a, b) for a, b in zip(poly, poly[1:])) for _, poly, _ in segs)
    summary = {"frames": len(frames), "seconds": round(len(frames) / fps, 2), "length_m": round(walk_len / 100.0, 2),
               "max_step_cm_per_frame": round(max(steps), 2), "walking_step_cm_per_frame": round(v / fps, 2),
               "max_turn_deg_per_frame": round(max(turns), 3), "segments": [s[0] for s in segs]}
    return frames, summary


# ------------------------------------------------------------------------------------------------- in the editor

def _unreal():
    import unreal  # noqa: F401  (only inside the editor)
    return unreal


def _world():
    unreal = _unreal()
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def _passable(hit_actor, hit_component):
    unreal = _unreal()
    words = " ".join([hit_actor.get_actor_label() if hit_actor else "", hit_actor.get_class().get_name() if hit_actor else "",
                      hit_component.get_name() if hit_component else ""]).lower()
    if isinstance(hit_component, unreal.StaticMeshComponent) and hit_component.static_mesh:
        words += " " + hit_component.static_mesh.get_name().lower()
        for k in range(hit_component.get_num_materials()):
            m = hit_component.get_material(k)
            if m:
                words += " " + m.get_name().lower()
    # Doors, sliding glass panels and curtains pass; fixed glazing and curtain walls (the building's skin) do not.
    words_cw = words.replace("curtain wall", "curtainwall").replace("curtain_wall", "curtainwall")
    if any(w in words_cw for w in ("door", "slider", "sliding", "drape", "blind", "shade")):
        return True
    if "curtain" in words_cw.replace("curtainwall", ""):
        return True
    if "panel" in words and any(w in words for w in ("glass", "slid", "door")):
        return True
    if any(w in words for w in ("camera", "volume", "trigger", "decal", "fog", "skyatmosphere", "reflectioncapture")):
        return True
    if hit_actor:
        origin, extent = hit_actor.get_actor_bounds(True)
        if extent.z * 2.0 < 50.0:
            return True  # furniture and objects under 0.5 m high
    return False


def check_sight(p, frames, step_cm=25.0):
    """Line traces along the walked segments at eye height. Returns [] when clear, else a list of refusals
    {"segment", "from_point", "to_point", "at_cm", "object", "component"} (the first solid hit of each segment)."""
    unreal = _unreal()
    import wieland_interiors as wi
    world = _world()
    segs = _segments(p)
    refusals = []
    # Revit's grade slab and surrounding-building massing are hidden in every render (start_render), so the check
    # ignores them too and tests what the video shows: the Phase 17 buildings, which are solid to the trace.
    ignore = [a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
              if a.get_actor_label() in wi.REVIT_STAND_INS]
    for k, (kind, poly, i) in enumerate(segs):
        if kind != "walk":
            continue
        # Points along the frames of this segment, every step_cm.
        q = [f["loc"] for f in frames if f["segment"] == k]
        if len(q) < 2:
            continue
        pts, acc = [q[0]], 0.0
        for a, b in zip(q, q[1:]):
            acc += math.dist(a, b)
            if acc >= step_cm:
                pts.append(b)
                acc = 0.0
        if pts[-1] != q[-1]:
            pts.append(q[-1])
        hit_found = None
        for a, b in zip(pts, pts[1:]):
            hits = unreal.SystemLibrary.line_trace_multi(world, unreal.Vector(*a), unreal.Vector(*b),
                                                         unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, ignore,
                                                         unreal.DrawDebugTrace.NONE, True)
            for h in hits or []:
                t = h.to_tuple()
                actor, comp, loc = t[9], t[10], t[4]
                if actor is None or not _passable(actor, comp):
                    hit_found = {"segment": k + 1, "from_point": i + 1, "to_point": i + 2,
                                 "at_cm": [round(loc.x, 1), round(loc.y, 1), round(loc.z, 1)],
                                 "object": actor.get_actor_label() if actor else "unknown",
                                 "component": comp.get_name() if comp else ""}
                    break
            if hit_found:
                break
        if hit_found:
            refusals.append(hit_found)
    return refusals


def _exposures(frames, fps):
    unreal = _unreal()
    import wieland_truth as wt
    evs = []
    for f in frames:
        _, ev = wt.exposure_at(unreal.Vector(*f["loc"]))
        evs.append(float(ev))
    return _smooth(evs, EV_TAU_S * fps)


def build_sequence(p, frames, asset):
    """A new level sequence asset with a spawned camera keyed on every frame (as Phase 11's seq_build.py)."""
    unreal = _unreal()
    import wieland_lighting as wl
    import wieland_truth as wt
    path = SEQ_FOLDER + "/" + asset
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path), "existing"
    fps = int(p["fps"])
    evs = _exposures(frames, fps)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    seq = tools.create_asset(asset, SEQ_FOLDER, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    seq.set_display_rate(unreal.FrameRate(fps, 1))
    seq.set_playback_start(0)
    seq.set_playback_end(len(frames))
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    first = frames[0]
    cam = actors.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(*first["loc"]),
                                        unreal.Rotator(pitch=first["rot"][0], yaw=first["rot"][1], roll=0.0))
    cam.set_actor_label("TEMP_path_camera")
    cam.tags = [wl.TAG_TEMP]
    comp = cam.get_cine_camera_component()
    fb = comp.get_editor_property("filmback")
    fb.set_editor_property("sensor_width", 36.0)
    fb.set_editor_property("sensor_height", 36.0 * p["resolution"][1] / p["resolution"][0])
    comp.set_editor_property("filmback", fb)
    lens = comp.get_editor_property("lens_settings")
    lens.set_editor_property("min_focal_length", 20.0)
    lens.set_editor_property("max_focal_length", 20.0)
    lens.set_editor_property("min_f_stop", 1.2)
    lens.set_editor_property("max_f_stop", 22.0)
    comp.set_editor_property("lens_settings", lens)
    comp.set_editor_property("current_focal_length", 20.0)
    comp.set_editor_property("current_aperture", 8.0)
    focus = comp.get_editor_property("focus_settings")
    focus.set_editor_property("focus_method", unreal.CameraFocusMethod.DISABLE)
    comp.set_editor_property("focus_settings", focus)
    wt._camera_exposure(comp, BASE_EV)
    pps = comp.get_editor_property("post_process_settings")
    pps.set_editor_property("override_auto_exposure_bias", True)
    pps.set_editor_property("auto_exposure_bias", BASE_EV - evs[0])
    pps.set_editor_property("override_motion_blur_amount", True)
    pps.set_editor_property("motion_blur_amount", 0.2)
    comp.set_editor_property("post_process_settings", pps)
    cam_b = seq.add_spawnable_from_instance(cam)
    comp_b = seq.add_possessable(comp)
    comp_b.set_parent(cam_b)
    cam_b.set_display_name("W1529_PathCamera")
    for b in list(seq.get_bindings()):
        if str(b.get_display_name()) == "TEMP_path_camera" and not b.get_tracks() and not b.get_child_possessables():
            b.remove()
    actors.destroy_actor(cam)
    LIN = unreal.MovieSceneKeyInterpolation.LINEAR
    tr = cam_b.add_track(unreal.MovieScene3DTransformTrack).add_section()
    tr.set_range(0, len(frames))
    ch = tr.get_all_channels()
    for f in frames:
        t = unreal.FrameNumber(f["f"])
        for idx, val in enumerate((f["loc"][0], f["loc"][1], f["loc"][2], 0.0, f["rot"][0], f["rot"][1])):
            ch[idx].add_key(t, val, 0.0, unreal.MovieSceneTimeUnit.DISPLAY_RATE, LIN)
    ex = comp_b.add_track(unreal.MovieSceneFloatTrack)
    ex.set_property_name_and_path("AutoExposureBias", "PostProcessSettings.AutoExposureBias")
    exs = ex.add_section()
    exs.set_range(0, len(frames))
    ech = exs.get_all_channels()[0]
    for f, ev in zip(frames, evs):
        ech.add_key(unreal.FrameNumber(f["f"]), BASE_EV - ev, 0.0, unreal.MovieSceneTimeUnit.DISPLAY_RATE, LIN)
    cut = seq.add_track(unreal.MovieSceneCameraCutTrack).add_section()
    cut.set_range(0, len(frames))
    cut.set_camera_binding_id(seq.get_binding_id(cam_b))
    unreal.EditorAssetLibrary.save_asset(path, False)
    return seq, "made"


_STATE = {}


def start_render(p, seq, folder):
    """Quick render of the sequence (as Phase 11's seq_render.py); returns the settings it changed, to put back."""
    unreal = _unreal()
    import wieland_lighting as wl
    import wieland_truth as wt
    queue = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    if queue.is_rendering():
        raise RuntimeError("a render is already running")
    if wt.cvar(wt.NANITE_MODE) != 0:
        raise RuntimeError("r.RayTracing.Nanite.Mode does not read 0; not rendering")
    pt = p.get("quality") == "pathtraced"
    os.makedirs(folder, exist_ok=True)
    # wt.cvar(name, value) sets and returns the NEW value, so every value is read before it is changed, and the
    # values read are what end_render puts back (found on the first test render, Phase 19 error 2).
    names = [PRE_EXPOSURE] + ([wt.APPEND] if pt else list(QUALITY))
    state = {"before": {n: wt.cvar(n) for n in names}, "stand_ins_hidden": wt._stand_ins(True)}
    wt.cvar(PRE_EXPOSURE, 7)
    unreal.SystemLibrary.execute_console_command(wl.world(), "DisableAllScreenMessages")
    if pt:
        wt.cvar(wt.APPEND, wt.APPEND_FOR_TREES)
    else:
        for name, level in zip(QUALITY, (3, 4, 4)):
            wt.cvar(name, level)
    s = unreal.MovieGraphQuickRenderModeSettings()
    s.set_configuration_type(unreal.MovieGraphQuickRenderConfigurationType.BASIC)
    s.set_editor_property("post_render_behavior", unreal.MoviePipelinePostRenderActionType.DO_NOTHING)
    s.set_editor_property("execution_mode", unreal.MovieGraphQuickRenderExecutionMode.EDITOR_WORLD)
    s.set_editor_property("level_sequence_override", seq)
    s.set_editor_property("frame_range_type", unreal.MovieGraphQuickRenderFrameRangeType.CUSTOM)
    s.set_editor_property("override_custom_start_frame", True)
    s.set_editor_property("custom_start_frame", 0)
    s.set_editor_property("override_custom_end_frame", True)
    s.set_editor_property("custom_end_frame", int(seq.get_playback_end()))
    basic = s.get_basic_config()

    def ov(prop, value, flag=None):
        basic.set_editor_property(flag or ("override_" + prop), True)
        basic.set_editor_property(prop, value)
    ov("use_path_traced_renderer", pt, "override_b_use_path_traced_renderer")
    ov("use_deferred_renderer", not pt, "override_b_use_deferred_renderer")
    if pt:
        ov("path_traced_spatial_sample_count", 256)
    else:
        ov("deferred_spatial_sample_count", 8)
    ov("temporal_sample_count", 1)
    ov("num_warm_up_frames", WARM_UP)
    ov("output_resolution", unreal.MovieGraphLibrary.named_resolution_from_size(int(p["resolution"][0]), int(p["resolution"][1])))
    ov("output_directory", unreal.DirectoryPath(path=folder))
    ov("file_name_format", "frame.{frame_number}")
    unreal.get_editor_subsystem(unreal.MovieGraphQuickRenderSubsystem).begin_quick_render(
        unreal.MovieGraphQuickRenderMode.CURRENT_SEQUENCE, s)
    state["nanite_mode"] = wt.cvar(wt.NANITE_MODE)
    return state


def rendering():
    unreal = _unreal()
    return bool(unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering())


def end_render(state):
    """Put back what start_render changed, and read it back."""
    import wieland_truth as wt
    back = {}
    for name, value in state.get("before", {}).items():
        wt.cvar(name, value)
        back[name] = {"put_back": value, "reads": wt.cvar(name)}
    wt._stand_ins(False)
    back["nanite_mode"] = wt.cvar(wt.NANITE_MODE)
    return back


def encode(name, folder, fps, out_mp4):
    """frame.NNNN.png to H.264 (CRF 18, BT.709, 4:2:0); returns the frame count read back by ffprobe."""
    os.makedirs(os.path.dirname(out_mp4), exist_ok=True)
    files = sorted(f for f in os.listdir(folder) if f.startswith("frame.") and f.endswith(".png"))
    if not files:
        raise RuntimeError("no frames in " + folder)
    first = int(files[0].split(".")[1])
    cmd = [FFMPEG + "ffmpeg.exe", "-y", "-hide_banner", "-loglevel", "error", "-framerate", str(fps), "-start_number", str(first),
           "-i", folder + "/frame.%04d.png", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
           "-vf", "scale=in_range=full:out_range=tv,format=yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
           "-color_trc", "bt709", "-movflags", "+faststart", out_mp4]
    subprocess.run(cmd, check=True, capture_output=True, timeout=3600)
    probe = subprocess.run([FFMPEG + "ffprobe.exe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                            "-show_entries", "stream=nb_read_frames,duration", "-of", "json", out_mp4],
                           check=True, capture_output=True, text=True, timeout=600)
    st = json.loads(probe.stdout)["streams"][0]
    return int(st["nb_read_frames"]), float(st.get("duration") or 0.0), len(files)


# ------------------------------------------------------------------------------------------------- requests

def up_to_date(file_path, p):
    side = VIDEO_DIR + "/" + safe_name(p["name"]) + ".json"
    mp4 = VIDEO_DIR + "/" + safe_name(p["name"]) + ".mp4"
    if not (os.path.exists(side) and os.path.exists(mp4)):
        return False
    meta = json.load(open(side, encoding="utf-8"))
    if meta.get("path_sha256") != checksum(file_path):
        return False
    req = p.get("render_requested_at")
    if not req:
        return True

    def when(text):
        # path_server.py writes local time without a zone, as this tool does; a value with a zone (for example a
        # trailing Z) is turned into local time, so the two always compare as times, not as text.
        t = datetime.datetime.fromisoformat(str(text).replace("Z", "+00:00"))
        return t.astimezone().replace(tzinfo=None) if t.tzinfo else t
    try:
        return when(meta.get("rendered_at", "")) >= when(req)
    except ValueError:
        return False


def requested_paths(include_test=False):
    out = []
    for f in sorted(os.listdir(PATHS_DIR)):
        if not f.endswith(".json") or f in ("last_render.json",):
            continue
        if f.startswith("_") and not include_test:
            continue
        fp = PATHS_DIR + "/" + f
        try:
            p = json.load(open(fp, encoding="utf-8"))
        except ValueError:
            continue
        if not isinstance(p, dict) or "points" not in p:
            continue
        if p.get("render_requested_at") or (include_test and f.startswith("_")):
            out.append(fp)
    return out


def _job(file_path):
    """Plan, check, build: returns a job dict or a refusal dict."""
    try:
        p = load(file_path)
    except ValueError as exc:
        return {"path": os.path.basename(file_path), "refused": str(exc)}
    frames, summary = plan(p)
    refusals = check_sight(p, frames)
    if refusals:
        r = refusals[0]
        return {"path": os.path.basename(file_path), "name": p["name"], "refused":
                "segment %d (point %d to %d) passes through %s at x %.0f, y %.0f, z %.0f cm" %
                (r["segment"], r["from_point"], r["to_point"], r["object"], r["at_cm"][0], r["at_cm"][1], r["at_cm"][2]),
                "refusals": refusals, "summary": summary}
    sha = checksum(file_path)
    asset = "SEQ_Path_%s_%s" % (safe_name(p["name"]), sha[:8])
    seq, how = build_sequence(p, frames, asset)
    folder = FRAMES_ROOT + "/" + safe_name(p["name"]) + "_" + sha[:8]
    return {"path": os.path.basename(file_path), "file": file_path, "name": p["name"], "p": p, "sha": sha,
            "asset": asset, "sequence": seq, "sequence_made": how, "folder": folder, "summary": summary}


def render_requested(include_test=False, on_done=None, only=None):
    """Render every requested path that has no up-to-date video, one at a time, on the editor's ticks. Returns at
    once; progress in _STATE and, at the end, owner_review/paths/last_render.json. only: a list of path names
    (as saved on the page) to restrict this run to, e.g. ["Grade Level"] to render and look at one video first."""
    unreal = _unreal()
    if _STATE.get("active"):
        return {"already_running": True, "queue": [os.path.basename(f) for f in _STATE.get("queue", [])]}
    queue = []
    skipped = []
    for fp in requested_paths(include_test):
        if only is not None and os.path.splitext(os.path.basename(fp))[0] not in only:
            continue
        try:
            p = load(fp)
        except ValueError as exc:
            skipped.append({"path": os.path.basename(fp), "refused": str(exc)})
            continue
        if up_to_date(fp, p):
            skipped.append({"path": os.path.basename(fp), "skipped": "video up to date"})
            continue
        queue.append(fp)
    _STATE.clear()
    _STATE.update({"active": True, "queue": queue, "done": [], "refused": [x for x in skipped if "refused" in x],
                   "skipped": [x for x in skipped if "skipped" in x], "current": None, "started": time.time(),
                   "phase": "next", "on_done": on_done})

    def finish():
        rec = {"time": datetime.datetime.now().isoformat(timespec="seconds"), "rendered": _STATE["done"],
               "refused": _STATE["refused"], "skipped": _STATE["skipped"]}
        with open(PATHS_DIR + "/last_render.json", "w", encoding="utf-8") as h:
            json.dump(rec, h, indent=1)
        _STATE["active"] = False
        _STATE["phase"] = "finished"
        if _STATE.get("handle") is not None:
            unreal.unregister_slate_post_tick_callback(_STATE["handle"])
            _STATE["handle"] = None
        if _STATE.get("on_done"):
            _STATE["on_done"](rec)

    def tick(_dt):
        try:
            ph = _STATE["phase"]
            if ph == "next":
                if not _STATE["queue"]:
                    finish()
                    return
                fp = _STATE["queue"].pop(0)
                job = _job(fp)
                if "refused" in job:
                    _STATE["refused"].append({k: v for k, v in job.items() if k in ("path", "name", "refused", "refusals")})
                    return
                job["render_started"] = time.time()
                job["state"] = start_render(job["p"], job["sequence"], job["folder"])
                _STATE["current"] = job
                _STATE["phase"] = "rendering"
                _STATE["since"] = time.time()
            elif ph == "rendering":
                if rendering() or time.time() - _STATE["since"] < 5.0:
                    return
                job = _STATE["current"]
                job["restored"] = end_render(job["state"])
                job["render_seconds"] = round(time.time() - job["render_started"], 1)
                mp4 = VIDEO_DIR + "/" + safe_name(job["name"]) + ".mp4"
                n_mp4, dur, n_png = encode(job["name"], job["folder"], int(job["p"]["fps"]), mp4)
                meta = {"name": job["name"], "path_file": job["path"], "path_sha256": job["sha"],
                        "rendered_at": datetime.datetime.now().isoformat(timespec="seconds"),
                        "duration_s": round(dur, 3), "frames": n_mp4, "frames_rendered": n_png,
                        "planned_frames": job["summary"]["frames"], "fps": int(job["p"]["fps"]),
                        "resolution": job["p"]["resolution"], "quality": job["p"].get("quality", "realtime"),
                        "speed_m_per_s": job["p"]["speed_m_per_s"], "length_m": job["summary"]["length_m"],
                        "max_step_cm_per_frame": job["summary"]["max_step_cm_per_frame"],
                        "max_turn_deg_per_frame": job["summary"]["max_turn_deg_per_frame"],
                        "render_seconds": job["render_seconds"], "sequence": SEQ_FOLDER + "/" + job["asset"],
                        "frames_folder": job["folder"], "settings_put_back": job["restored"]}
                with open(VIDEO_DIR + "/" + safe_name(job["name"]) + ".json", "w", encoding="utf-8") as h:
                    json.dump(meta, h, indent=1)
                _STATE["done"].append(meta)
                _STATE["current"] = None
                _STATE["phase"] = "next"
        except Exception as exc:  # one failed path must not stop the rest; it is recorded
            job = _STATE.get("current") or {}
            if job.get("state"):
                try:
                    end_render(job["state"])
                except Exception:
                    pass
            _STATE["refused"].append({"path": job.get("path", "?"), "refused": "error: %r" % (exc,)})
            _STATE["current"] = None
            _STATE["phase"] = "next"

    _STATE["handle"] = unreal.register_slate_post_tick_callback(tick)
    return {"queued": [os.path.basename(f) for f in queue], "skipped": skipped}


def status():
    s = {k: v for k, v in _STATE.items() if k in ("active", "phase", "done", "refused", "skipped")}
    s["queue"] = [os.path.basename(f) for f in _STATE.get("queue", [])]
    cur = _STATE.get("current")
    s["current"] = cur and {"name": cur["name"], "frames": cur["summary"]["frames"],
                            "on_disk": len([f for f in os.listdir(cur["folder"]) if f.endswith(".png")]) if os.path.isdir(cur["folder"]) else 0}
    return s

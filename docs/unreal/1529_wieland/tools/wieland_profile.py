"""Editor-side capture helper for the 1529 N. Wieland performance profiles.

Runs inside the Unreal editor's Python interpreter. It drives the level
viewport camera from a Slate tick callback, so no call blocks the editor's
main thread: start() returns at once and the jobs run frame by frame.

Each job holds or moves the camera, warms up, then records the engine's CSV
profile (console commands "CsvProfile Start" and "CsvProfile Stop"). When the
last job ends, a JSON record is written to the path given to start().

Usage from the agent server's Python tool (each call has a fresh namespace,
but the module stays loaded, so its state persists between calls):

    import sys
    sys.dont_write_bytecode = True
    sys.path.insert(0, "<this folder>")
    import wieland_profile
    wieland_profile.start(jobs, "<result file>", info={...})
    ...
    wieland_profile.status()

A job is a dict:
    name     label used in the record
    kind     "view" (camera held still) or "path" (camera moves loc -> end)
    loc      [x, y, z] in level units (cm)
    end      [x, y, z], path jobs only
    target   [x, y, z] the camera looks at; or give "rot" for view jobs
    rot      [pitch, yaw, roll] in degrees, view jobs only
    seconds  length of the recorded part
    cvars    optional {console variable: value}, applied before the warm-up

Nothing here saves an asset or a level.
"""

import ctypes
import json
import os
import time

import unreal

_S = {"active": False}


def _world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def _cmd(command):
    unreal.SystemLibrary.execute_console_command(_world(), command)


def _foreground():
    """True when the editor's process owns the foreground window."""
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        pid = ctypes.c_ulong(0)
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return pid.value == os.getpid()
    except Exception:
        return None


def csv_dir():
    saved = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())
    return os.path.join(saved, "Profiling", "CSV")


def _list_csv():
    folder = csv_dir()
    if not os.path.isdir(folder):
        return set()
    return set(os.listdir(folder))


def _place(job, fraction):
    loc = job["loc"]
    if job["kind"] == "path":
        end = job["end"]
        loc = [loc[k] + (end[k] - loc[k]) * fraction for k in range(3)]
    location = unreal.Vector(loc[0], loc[1], loc[2])
    if job.get("target") is not None:
        tgt = job["target"]
        rotation = unreal.MathLibrary.find_look_at_rotation(location, unreal.Vector(tgt[0], tgt[1], tgt[2]))
    else:
        rot = job["rot"]
        rotation = unreal.Rotator(pitch=rot[0], yaw=rot[1], roll=rot[2])
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(location, rotation)
    return loc, [rotation.pitch, rotation.yaw, rotation.roll]


def _percentile_floor(sorted_values, q):
    """The October method: the value at index floor(q * (n - 1))."""
    if not sorted_values:
        return None
    return sorted_values[int(q * (len(sorted_values) - 1))]


def _finish():
    handle = _S.get("handle")
    if handle is not None:
        try:
            unreal.unregister_slate_post_tick_callback(handle)
        except Exception as exc:  # the record still gets written
            _S["error"] = (_S.get("error") or "") + " unregister: " + repr(exc)
        _S["handle"] = None
    record = {
        "info": _S.get("info"),
        "started_unix": _S.get("started"),
        "finished_unix": time.time(),
        "warmup_seconds": _S.get("warmup"),
        "csv_folder": csv_dir(),
        "error": _S.get("error"),
        "jobs": _S.get("results", []),
    }
    path = _S.get("result_path")
    if path:
        with open(path, "w", encoding="utf-8") as handle_out:
            json.dump(record, handle_out, indent=1)
    _S["active"] = False
    _S["phase"] = "done"


def _step(delta_seconds):
    now = time.perf_counter()
    state = _S
    if state["phase"] == "idle":
        state["i"] += 1
        if state["i"] >= len(state["jobs"]):
            _finish()
            return
        job = state["jobs"][state["i"]]
        for name, value in (job.get("cvars") or {}).items():
            _cmd("%s %s" % (name, value))
        _place(job, 0.0)
        state["phase"] = "warmup"
        state["t0"] = now
        return
    job = state["jobs"][state["i"]]
    if state["phase"] == "warmup":
        _place(job, 0.0)
        if now - state["t0"] >= state["warmup"]:
            state["before"] = _list_csv()
            _cmd("CsvProfile Start")
            state["phase"] = "capture"
            state["t0"] = now
            state["dts"] = []
            state["fg"] = 0
            state["wall_start"] = time.time()
            state["first"] = None
        return
    if state["phase"] == "capture":
        elapsed = now - state["t0"]
        loc, rot = _place(job, min(1.0, elapsed / job["seconds"]))
        if state["first"] is None:
            state["first"] = {"loc": loc, "rot_pitch_yaw_roll": rot}
        state["last"] = {"loc": loc, "rot_pitch_yaw_roll": rot}
        state["dts"].append(delta_seconds)
        if _foreground():
            state["fg"] += 1
        if elapsed >= job["seconds"]:
            _cmd("CsvProfile Stop")
            state["phase"] = "settle"
            state["t0"] = now
            state["elapsed"] = elapsed
        return
    if state["phase"] == "settle":
        if now - state["t0"] >= state["settle"]:
            dts_ms = sorted(d * 1000.0 for d in state["dts"])
            count = len(dts_ms)
            state["results"].append({
                "name": job["name"],
                "kind": job["kind"],
                "job": job,
                "wall_start_unix": state["wall_start"],
                "recorded_seconds": state["elapsed"],
                "ticks": count,
                "foreground_fraction": (state["fg"] / count) if count else None,
                "tick_ms_mean": (sum(dts_ms) / count) if count else None,
                "tick_ms_p95": _percentile_floor(dts_ms, 0.95),
                "tick_ms_max": dts_ms[-1] if count else None,
                "camera_first": state["first"],
                "camera_last": state.get("last"),
                "new_csv_files": sorted(_list_csv() - state["before"]),
                "tick_ms_series": [round(d * 1000.0, 3) for d in state["dts"]] if job.get("keep_series") else None,
            })
            state["phase"] = "idle"
        return


def _tick(delta_seconds):
    if not _S.get("active"):
        return
    try:
        _step(delta_seconds)
    except Exception as exc:
        _S["error"] = repr(exc)
        try:
            _cmd("CsvProfile Stop")
        except Exception:
            pass
        _finish()


def start(jobs, result_path, info=None, warmup_seconds=8.0, settle_seconds=2.0):
    """Begin the jobs. Returns at once; the jobs run on the editor's ticks."""
    if _S.get("active"):
        raise RuntimeError("a capture is already running: " + json.dumps(status()))
    if os.path.exists(result_path):
        raise RuntimeError("result file already exists: " + result_path)
    _S.clear()
    _S.update(
        active=True,
        jobs=jobs,
        i=-1,
        phase="idle",
        t0=0.0,
        results=[],
        result_path=result_path,
        info=info,
        warmup=float(warmup_seconds),
        settle=float(settle_seconds),
        error=None,
        started=time.time(),
        handle=None,
    )
    _S["handle"] = unreal.register_slate_post_tick_callback(_tick)
    total = sum(float(j["seconds"]) + float(warmup_seconds) + float(settle_seconds) for j in jobs)
    return "started %d jobs, about %.0f seconds" % (len(jobs), total)


def status():
    return {
        "active": bool(_S.get("active")),
        "phase": _S.get("phase"),
        "job_index": _S.get("i"),
        "jobs": len(_S.get("jobs", [])),
        "finished_jobs": len(_S.get("results", [])),
        "error": _S.get("error"),
    }


def cancel():
    """Stop after the current tick and write whatever was recorded."""
    if _S.get("active"):
        try:
            _cmd("CsvProfile Stop")
        except Exception:
            pass
        _S["error"] = (_S.get("error") or "") + " cancelled"
        _finish()
    return status()

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


def _finish_soak():
    handle = _S.get("handle")
    if handle is not None:
        try:
            unreal.unregister_slate_post_tick_callback(handle)
        except Exception as exc:
            _S["error"] = (_S.get("error") or "") + " unregister: " + repr(exc)
        _S["handle"] = None
    summary = {
        "info": _S.get("info"),
        "job": _S.get("job"),
        "loops_asked": _S.get("loops"),
        "loops_finished": _S.get("loop", 0),
        "ticks_total": _S.get("ticks_total", 0),
        "ticks_over_33ms_total": _S.get("over33_total", 0),
        "worst_tick_ms": _S.get("worst_ms"),
        "run_started_unix": _S.get("run_started"),
        "finished_unix": time.time(),
        "error": _S.get("error"),
    }
    with open(_S["log_path"] + ".summary.json", "w", encoding="utf-8") as handle_out:
        json.dump(summary, handle_out, indent=1)
    _S["active"] = False
    _S["phase"] = "done"


def _soak_step(delta_seconds):
    now = time.perf_counter()
    state = _S
    job = state["job"]
    if state["phase"] == "warmup":
        _place(job, 0.0)
        if now - state["t0"] >= state["warmup"]:
            state["phase"] = "run"
            state["t0"] = now
            state["dts"] = []
            state["fg"] = 0
            state["run_started"] = time.time()
        return
    elapsed = now - state["t0"]
    _place(job, min(1.0, elapsed / job["seconds"]))
    state["dts"].append(delta_seconds)
    if _foreground():
        state["fg"] += 1
    # every few loops, record a short CSV profile so the engine's own video-memory figure is on file
    every = state.get("csv_every") or 0
    if every and state["loop"] % every == 0:
        if state.get("csv_state") is None and elapsed < 1.0:
            state["csv_before"] = _list_csv()
            _cmd("CsvProfile Start")
            state["csv_state"] = "on"
        elif state.get("csv_state") == "on" and elapsed >= state["csv_seconds"]:
            _cmd("CsvProfile Stop")
            state["csv_state"] = "stopped"
    if elapsed < job["seconds"]:
        return
    dts_ms = sorted(d * 1000.0 for d in state["dts"])
    count = len(dts_ms)
    over33 = sum(1 for d in dts_ms if d > 33.333)
    state["loop"] += 1
    state["ticks_total"] += count
    state["over33_total"] += over33
    state["worst_ms"] = max(state["worst_ms"] or 0.0, dts_ms[-1])
    line = {
        "loop": state["loop"],
        "unix": round(time.time(), 1),
        "ticks": count,
        "ms_mean": round(sum(dts_ms) / count, 3),
        "ms_p95": round(_percentile_floor(dts_ms, 0.95), 3),
        "ms_max": round(dts_ms[-1], 3),
        "over_33ms": over33,
        "foreground_fraction": round(state["fg"] / count, 2),
    }
    if state.get("csv_state") == "stopped":
        line["csv"] = sorted(_list_csv() - state["csv_before"])
    state["csv_state"] = None
    with open(state["log_path"], "a", encoding="utf-8") as handle_out:
        handle_out.write(json.dumps(line) + "\n")
    if state["loop"] >= state["loops"]:
        _finish_soak()
        return
    state["t0"] = now
    state["dts"] = []
    state["fg"] = 0


def _tick(delta_seconds):
    if not _S.get("active"):
        return
    soaking = _S.get("mode") == "soak"
    try:
        if soaking:
            _soak_step(delta_seconds)
        else:
            _step(delta_seconds)
    except Exception as exc:
        _S["error"] = repr(exc)
        if soaking:
            _finish_soak()
            return
        try:
            _cmd("CsvProfile Stop")
        except Exception:
            pass
        _finish()


def soak(job, loops, log_path, info=None, warmup_seconds=8.0, csv_every=5, csv_seconds=2.0):
    """Walk one path job over and over.

    After every loop one JSON line (frame count, mean, 95th percentile and
    worst frame) is appended to log_path, so a crash leaves the record so far.
    Every csv_every loops (0 turns this off) the first csv_seconds of the loop
    are also recorded with the engine's CSV profile, whose file name goes into
    that loop's line; it carries the engine's own video-memory figure.
    When the last loop ends, log_path + ".summary.json" is written. Returns at
    once; the loops run on the editor's ticks.
    """
    if _S.get("active"):
        raise RuntimeError("a capture is already running: " + json.dumps(status()))
    if os.path.exists(log_path) or os.path.exists(log_path + ".summary.json"):
        raise RuntimeError("log already exists: " + log_path)
    if job.get("kind") != "path":
        raise RuntimeError("soak needs a path job")
    _S.clear()
    _S.update(
        active=True,
        mode="soak",
        job=job,
        loops=int(loops),
        loop=0,
        phase="warmup",
        t0=time.perf_counter(),
        log_path=log_path,
        info=info,
        warmup=float(warmup_seconds),
        error=None,
        started=time.time(),
        handle=None,
        ticks_total=0,
        over33_total=0,
        worst_ms=None,
        dts=[],
        fg=0,
    )
    for name, value in (job.get("cvars") or {}).items():
        _cmd("%s %s" % (name, value))
    _place(job, 0.0)
    _S["handle"] = unreal.register_slate_post_tick_callback(_tick)
    return "soak started: %d loops of %.0f seconds" % (int(loops), float(job["seconds"]))


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
    if _S.get("mode") == "soak":
        return {
            "active": bool(_S.get("active")),
            "mode": "soak",
            "phase": _S.get("phase"),
            "loops_finished": _S.get("loop", 0),
            "loops_asked": _S.get("loops"),
            "worst_tick_ms": _S.get("worst_ms"),
            "error": _S.get("error"),
        }
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
        _S["error"] = (_S.get("error") or "") + " cancelled"
        if _S.get("mode") == "soak":
            _finish_soak()
            return status()
        try:
            _cmd("CsvProfile Stop")
        except Exception:
            pass
        _finish()
    return status()

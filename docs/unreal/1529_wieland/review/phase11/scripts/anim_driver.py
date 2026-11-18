"""Phase 11, step 11.2: render the frames of one camera move in runs, resuming from whatever is already on disk.

    python -B review/phase11/scripts/anim_driver.py <name> <asset> <folder> [--run 150] [--samples 8]
           [--first N --last M] [--min-free 26] [--tier rt] [--anti-aliasing TSR] [--warm-up 64] [--quality 4,4,4]

Runs outside the editor, from the folder docs/unreal/1529_wieland. In a loop it lists the frames of the move that
have no file yet (<folder>/<name>.<frame, four digits>.png), takes the first unbroken run of them (at most --run
frames), waits for free commit memory, asks the editor to render that run (seq_render.py) and watches the files
arrive. A run that stops early is simply followed by the next run of missing frames, so an interruption of any
kind resumes from the last finished frame. Three runs in a row without one new file end the driver with exit 3.
Every step is written to review/phase11/anim_driver.log.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import time

LOG = "review/phase11/anim_driver.log"
FRAMES = 900


def log(text):
    line = "%s %s" % (datetime.datetime.now().strftime("%H:%M:%S"), text)
    with open(LOG, "a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    print(line, flush=True)


def free_gb():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreeVirtualMemory/1MB,1)"],
                         capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


def call(script, timeout):
    """Run a script in the editor; returns the parsed return value, or None when the editor does not answer."""
    try:
        out = subprocess.run([sys.executable, "-B", "tools/ue_call.py", "py", script, str(timeout)],
                             capture_output=True, text=True, timeout=timeout + 60).stdout
    except subprocess.TimeoutExpired:
        return None
    try:
        value = json.loads(out.strip().splitlines()[0])["returnValue"]
        return json.loads(value) if isinstance(value, str) else value
    except (ValueError, KeyError, IndexError):
        log("editor said: " + " ".join(out.split())[:300])
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("asset")
    parser.add_argument("folder")
    parser.add_argument("--run", type=int, default=150)
    parser.add_argument("--samples", type=int, default=8)
    parser.add_argument("--first", type=int, default=0)
    parser.add_argument("--last", type=int, default=FRAMES - 1)
    parser.add_argument("--min-free", type=float, default=26.0)
    parser.add_argument("--tier", default="rt")
    parser.add_argument("--anti-aliasing", default=None)
    parser.add_argument("--warm-up", type=int, default=64)
    parser.add_argument("--quality", default="4,4,4", help="levels for bounced light, reflections, shadows")
    args = parser.parse_args()
    os.makedirs(args.folder, exist_ok=True)

    def have(frame):
        path = os.path.join(args.folder, "%s.%04d.png" % (args.name, frame))
        return os.path.exists(path) and os.path.getsize(path) > 0

    def missing():
        return [f for f in range(args.first, args.last + 1) if not have(f)]

    barren = 0
    while True:
        todo = missing()
        if not todo:
            log("%s: every frame %d to %d has a file. DONE" % (args.name, args.first, args.last))
            return 0
        start = todo[0]
        end = start
        while end + 1 in todo and end + 1 - start < args.run:
            end += 1
        tries = 0
        free = free_gb()
        while free < args.min_free and tries < 40:
            log("%s waits: %.1f GB of commit memory free" % (args.name, free))
            time.sleep(30)
            tries += 1
            free = free_gb()
        if free < args.min_free:
            log("%s STOP: %.1f GB free after 20 minutes" % (args.name, free))
            return 2
        state = call("review/phase11/scripts/state.py", 120)
        if state is None:
            log("%s: the editor does not answer; waiting 60 s" % args.name)
            time.sleep(60)
            barren += 1
            if barren >= 10:
                log("%s STOP: the editor did not answer ten times" % args.name)
                return 4
            continue
        if state.get("world") != "/Game/Wieland1529/L_Site_M4":
            log("%s STOP: the editor has %s open, not L_Site_M4" % (args.name, state.get("world")))
            return 5
        if state.get("rendering"):
            log("%s: a render is running already; waiting 30 s" % args.name)
            time.sleep(30)
            continue
        job = {"asset": args.asset, "name": args.name, "folder": args.folder.replace("\\", "/"), "start": start, "end": end + 1,
               "tier": args.tier, "samples": args.samples, "warm_up_frames": args.warm_up, "anti_aliasing": args.anti_aliasing,
               "quality": [int(v) for v in args.quality.split(",")]}
        with open("review/phase11/seq_render_job.json", "w", encoding="utf-8") as handle:
            json.dump(job, handle)
        before = len(todo)
        began = time.time()
        reply = call("review/phase11/scripts/seq_render.py", 300)
        log("%s frames %d to %d start, %.1f GB free: %s" % (args.name, start, end, free, json.dumps(reply)[:400]))
        last_count, last_change = before, time.time()
        while True:
            time.sleep(15)
            left = len([f for f in range(start, end + 1) if not have(f)])
            now_missing = len(missing())
            if now_missing != last_count:
                last_count, last_change = now_missing, time.time()
            if left == 0:
                break
            if time.time() - last_change > 600:
                log("%s: no new frame for 10 minutes (%d of this run left)" % (args.name, left))
                break
        # the last file may still be open; wait until the editor says the render has ended
        for _ in range(40):
            state = call("review/phase11/scripts/state.py", 120)
            if state is not None and not state.get("rendering"):
                break
            time.sleep(15)
        done = before - len(missing())
        seconds = time.time() - began
        log("%s frames %d to %d: %d new files in %.0f s (%.2f s a frame)" % (args.name, start, end, done, seconds, seconds / max(1, done)))
        barren = barren + 1 if done == 0 else 0
        if barren >= 3:
            log("%s STOP: three runs in a row without a new file" % args.name)
            return 3


sys.exit(main())

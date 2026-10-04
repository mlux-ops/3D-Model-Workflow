"""Serialized headless Revit runner shared by the sconce trial arms.

Usage: python revit_run.py <absolute path to pyRevit script.py> [timeout_seconds]

Only one arm may drive a headless Revit at a time, so every run takes an exclusive lock on
revit.lock beside this file, then starts `pyrevit run <script> --revit=2025` and waits for it.
On timeout it kills only the process tree it started (by PID), never Revit by name, so the
owner's own Revit session is never touched. The exit code is the pyrevit exit code, or 124 on
timeout. A zero exit code does not mean the script succeeded: read the script's own output file.
"""
import msvcrt
import os
import subprocess
import sys
import time

PYREVIT = r"D:\Games\pyRevit-Master\bin\pyrevit.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
LOCK = os.path.join(HERE, "revit.lock")
LEDGER = os.path.join(HERE, "revit_runs.log")


def log(line):
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%S") + " " + line + "\n")


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python revit_run.py <absolute script.py> [timeout_seconds]")
    script = os.path.abspath(sys.argv[1])
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 900
    if not os.path.isfile(script):
        raise SystemExit("script not found: " + script)

    fh = open(LOCK, "a+b")
    waited = time.time()
    while True:
        try:
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            break
        except OSError:
            time.sleep(2)
    waited = time.time() - waited
    print("revit lock acquired after %.0f s" % waited, flush=True)
    log("START wait=%.0fs %s" % (waited, script))
    t0 = time.time()
    code = None
    try:
        # Below-normal priority (inherited by the Revit it launches) keeps the owner's own Revit responsive.
        proc = subprocess.Popen([PYREVIT, "run", script, "--revit=2025"],
                                creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        try:
            code = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            subprocess.call(["taskkill", "/T", "/F", "/PID", str(proc.pid)])
            code = 124
            print("TIMEOUT after %d s; killed process tree of PID %d" % (timeout, proc.pid), flush=True)
    finally:
        log("END code=%s run=%.0fs %s" % (code, time.time() - t0, script))
        fh.seek(0)
        msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
        fh.close()
    print("pyrevit exit code %s after %.0f s" % (code, time.time() - t0), flush=True)
    sys.exit(code)


if __name__ == "__main__":
    main()

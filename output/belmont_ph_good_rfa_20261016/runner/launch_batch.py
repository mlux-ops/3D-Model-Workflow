"""CPython 3 / Windows offline launcher. Never terminates a Revit process."""
from __future__ import print_function
import argparse
import datetime
import json
import msvcrt
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent
RECEIPTS = ROOT / 'receipts'
RUNNER = ROOT / 'batch_runner.py'
MANIFEST = ROOT / 'manifest.json'

def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2), encoding='utf-8')
    os.replace(tmp, path)

def existing_revit_processes():
    # Read-only snapshot; process IDs are never passed to termination commands.
    script = ("Get-CimInstance Win32_Process -Filter \"Name='Revit.exe'\" | "
              "Select-Object ProcessId,CreationDate,ExecutablePath | ConvertTo-Json -Compress")
    result = subprocess.run(['powershell.exe', '-NoProfile', '-Command', script],
                            capture_output=True, text=True, timeout=25, check=True)
    if not result.stdout.strip():
        return []
    data = json.loads(result.stdout)
    return data if isinstance(data, list) else [data]

def verify_manifest():
    if not MANIFEST.is_file():
        raise ValueError('Create manifest.json from manifest.example.json before launch')
    data = json.loads(MANIFEST.read_text(encoding='utf-8-sig'))
    jobs = data.get('families')
    if data.get('schema_version') != 1 or not isinstance(jobs, list) or len(jobs) != 6:
        raise ValueError('manifest.json must contain exactly six jobs')
    seen_ids = set()
    seen_targets = set()
    allowed = ROOT.parent.resolve()
    for job in jobs:
        jid = job.get('id', '')
        if not jid.replace('_', '').isalnum() or jid in seen_ids:
            raise ValueError('Invalid/duplicate family id: %s' % jid)
        seen_ids.add(jid)
        mode = job.get('mode')
        if mode not in ('oem', 'custom'):
            raise ValueError('Invalid mode for ' + jid)
        field = 'source_rfa' if mode == 'oem' else 'builder_script'
        source = pathlib.Path(job.get(field, ''))
        target = pathlib.Path(job.get('target_rfa', ''))
        if not source.is_absolute() or not source.is_file():
            raise ValueError('Missing absolute source/build file: ' + str(source))
        if not target.is_absolute() or target.suffix.lower() != '.rfa':
            raise ValueError('Missing absolute .rfa target')
        if target.exists():
            raise ValueError('Target already exists (do not overwrite): ' + str(target))
        resolved_target = target.resolve()
        if allowed not in resolved_target.parents:
            raise ValueError('Output outside Belmont task: ' + str(target))
        if str(target).casefold() in seen_targets:
            raise ValueError('Duplicate output: ' + str(target))
        seen_targets.add(str(target).casefold())
        if mode == 'oem' and source.suffix.lower() != '.rfa':
            raise ValueError('OEM input must be an RFA')
        if mode == 'custom' and source.suffix.lower() != '.py':
            raise ValueError('Builder input must be Python')
        if job.get('expected_dimensions_mm'):
            for axis in ('width', 'depth', 'height'):
                if float(job['expected_dimensions_mm'][axis]) <= 0:
                    raise ValueError('Dimension must be positive')
    if (RECEIPTS / 'batch_final.json').exists() or (RECEIPTS / 'batch_error.json').exists():
        raise ValueError('Previous batch evidence exists. Archive and reconcile before a new run.')
    return data

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--timeout-seconds', type=int, default=2400)
    p.add_argument('--pyrevit', default=r'D:\Games\pyRevit-Master\bin\pyrevit.exe')
    p.add_argument('--preflight-only', action='store_true')
    opts = p.parse_args()
    if opts.timeout_seconds < 60 or opts.timeout_seconds > 7200:
        raise ValueError('Timeout must be between 60 and 7200 seconds')
    manifest = verify_manifest()
    processes = existing_revit_processes()
    print('Preexisting Revit processes (never targeted):', json.dumps(processes), flush=True)
    if opts.preflight_only:
        print('OFFLINE_PREFLIGHT_PASS: six jobs, sources, target paths and process inventory')
        return 0
    exe = pathlib.Path(opts.pyrevit).resolve()
    if not exe.is_file() or not RUNNER.is_file():
        raise ValueError('pyRevit CLI or runner missing')
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    lock = open(str(ROOT / 'batch.lock'), 'a+b')
    locked = False
    proc = None
    info = {'started_utc': stamp(), 'runner': str(RUNNER), 'manifest': str(MANIFEST),
            'preexisting_revit': processes, 'command': [str(exe), 'run', str(RUNNER), '--revit=2025']}
    try:
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
                locked = True
                break
            except OSError:
                time.sleep(0.5)
        if not locked:
            raise RuntimeError('Another Belmont batch owns batch.lock')
        if (RECEIPTS / 'batch_final.json').exists():
            raise RuntimeError('Batch already completed')
        with open(RECEIPTS / 'pyrevit_stdout.log', 'wb') as out:
            proc = subprocess.Popen(info['command'], stdout=out, stderr=subprocess.STDOUT,
                                    cwd=str(ROOT), creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            info['owned_pyrevit_pid'] = proc.pid
            write(RECEIPTS / 'launcher_state.json', info)
            print('Launched only pyRevit PID', proc.pid, flush=True)
            end = time.monotonic() + opts.timeout_seconds
            last_stage = ''
            while proc.poll() is None and time.monotonic() < end:
                progress = RECEIPTS / 'progress.jsonl'
                if progress.is_file():
                    lines = progress.read_text(encoding='utf-8', errors='replace').splitlines()
                    if lines and lines[-1] != last_stage:
                        last_stage = lines[-1]
                        print('Progress:', last_stage[:500], flush=True)
                time.sleep(2)
            if proc.poll() is None:
                info['status'] = 'TIMEOUT_UNKNOWN_NATIVE_STATE'
                # Stop the owned CLI only, never kill Revit.exe or a process tree.
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=10)
                print('pyRevit CLI timed out. No Revit process was terminated.', flush=True)
                code = 124
            else:
                code = proc.returncode
                final = RECEIPTS / 'batch_final.json'
                if final.is_file():
                    payload = json.loads(final.read_text(encoding='utf-8'))
                    info['status'] = 'PASS' if payload.get('all_pass') and payload.get('complete_count') == 6 else 'NATIVE_HOLD'
                else:
                    info['status'] = 'MISSING_NATIVE_FINAL_RECEIPT'
                if code == 0 and info['status'] != 'PASS':
                    code = 3
            info['pyrevit_exit_code'] = proc.returncode
            info['completed_utc'] = stamp()
            write(RECEIPTS / 'launcher_state.json', info)
            print('Launcher status:', info['status'], 'exit:', code, flush=True)
            return code
    finally:
        if locked:
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
        lock.close()

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print('LAUNCHER_ERROR:', str(exc), file=sys.stderr)
        sys.exit(2)

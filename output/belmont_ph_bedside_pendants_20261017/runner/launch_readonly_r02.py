"""CPython safe preflight and ONE evidence-backed isolated native QA launch.

Default is read-only preflight, never a Revit launch. --launch requires a new
worker recovery-evidence file and no unresolved visible Revit processes.
Never attaches to, terminates or saves an existing user's Revit process.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'qa/native_readonly_oem_r02.py'
CLI = Path(r'D:\Games\pyRevit-Master\bin\pyrevit.exe')


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def path_for(*parts):
    path = ROOT.joinpath(*parts).resolve()
    if ROOT not in path.parents:
        raise ValueError('Write outside task root')
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_new(path, data):
    with path.open('x', encoding='utf-8') as handle:
        json.dump(data, handle, indent=2)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot():
    # Get-Process is a verified read-only fallback for this restricted context;
    # CIM is known to return access denied, so it is not retried.
    command = ("@(Get-Process -Name Revit,pyrevit -ErrorAction SilentlyContinue | "
               "Select-Object Id,ProcessName,Path,SessionId,Responding,MainWindowTitle,"
               "@{Name='StartTimeUtc';Expression={$_.StartTime.ToUniversalTime().ToString('o')}}) | "
               "ConvertTo-Json -Compress")
    process = subprocess.run(['powershell.exe', '-NoProfile', '-Command', command],
                             capture_output=True, text=True, timeout=20)
    if process.returncode:
        raise RuntimeError('Cannot establish process state: ' + process.stderr.strip())
    data = json.loads(process.stdout) if process.stdout.strip() else []
    return data if isinstance(data, list) else [data]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', default='r02')
    parser.add_argument('--launch', action='store_true')
    parser.add_argument('--recovery-evidence', type=Path)
    args = parser.parse_args()
    if not args.run_id.replace('_', '').isalnum():
        raise ValueError('Invalid run identifier')
    manifest_path = ROOT / 'qa/OEM_BYTE_IDENTITY.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    families = manifest['families']
    if len(families) != 4:
        raise ValueError('Exactly four original OEM families are expected')
    for row in families:
        path = Path(row['file']).resolve()
        if ROOT not in path.parents or sha(path) != row['original_rfa_sha256']:
            raise ValueError('Original RFA path/hash conflict: ' + str(path))
    processes = snapshot()
    report = {'utc': now(), 'mode': 'PREFLIGHT_ONLY', 'run_id': args.run_id,
              'original_hashes_verified': 4, 'visible_processes': processes,
              'native_script': str(SCRIPT), 'native_script_sha256': sha(SCRIPT),
              'pyrevit_cli_exists': CLI.is_file(),
              'status': 'HOLD_UNRESOLVED_EXISTING_PROCESS' if processes else 'OFFLINE_PREFLIGHT_READY',
              'recovery_evidence_required_before_launch': True,
              'native_launch_performed': False}
    preflight = path_for('runner', 'receipts', 'readonly_preflight_' + args.run_id + '.json')
    write_new(preflight, report)
    print(json.dumps(report, indent=2), flush=True)
    if not args.launch:
        return 0
    if processes:
        raise RuntimeError('No launch: existing Revit/pyrevit process state must be reconciled first')
    evidence = args.recovery_evidence.resolve() if args.recovery_evidence else None
    if evidence is None or ROOT not in evidence.parents or not evidence.is_file():
        raise RuntimeError('No launch: missing task-local recovery evidence')
    if evidence.stat().st_size < 20:
        raise RuntimeError('No launch: empty/insufficient recovery evidence')
    # The caller must inspect this evidence and state the changed approach in
    # the review notes before --launch. Its existence is NOT automatic proof
    # that the runtime is fixed, and no successful native gate is prepopulated.
    native = path_for('qa', 'native_readonly_' + args.run_id + '.json')
    if native.exists():
        raise RuntimeError('Existing native evidence: no replay')
    lock = path_for('runner', 'NATIVE_EXECUTION_ACTIVE.json')
    request_path = path_for('runner', 'requests', args.run_id + '.json')
    token = uuid.uuid4().hex
    request = {'run_id': args.run_id, 'token': token, 'utc': now(), 'families': families,
               'preexisting_revit_pids': [], 'recovery_evidence': str(evidence),
               'recovery_evidence_sha256': sha(evidence)}
    write_new(lock, {'run_id': args.run_id, 'utc': now(), 'status': 'SINGLE_NATIVE_WRITER_RESERVED'})
    write_new(request_path, request)
    env = os.environ.copy()
    temp = path_for('temp', 'readonly_' + args.run_id, 'placeholder').parent
    env.update({'TEMP': str(temp), 'TMP': str(temp),
                'BELMONT_READONLY_RUN_ID': args.run_id, 'BELMONT_READONLY_TOKEN': token})
    command = [str(CLI), 'run', str(SCRIPT), '--revit=2025']
    state_path = path_for('runner', 'receipts', 'readonly_launcher_' + args.run_id + '.json')
    state = {'started_utc': now(), 'command': command, 'status': 'STARTING',
             'recovery_evidence': str(evidence), 'recovery_evidence_sha256': sha(evidence),
             'native_receipt': str(native), 'native_launch_performed': True}
    with path_for('runner', 'receipts', 'readonly_stdout_' + args.run_id + '.log').open('xb') as handle:
        process = subprocess.Popen(command, cwd=str(ROOT), env=env,
                                   stdout=handle, stderr=subprocess.STDOUT,
                                   creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS | subprocess.CREATE_NO_WINDOW)
        state['owned_cli_pid'] = process.pid
        write_new(state_path, state)
        print('OWNED CLI PID ' + str(process.pid), flush=True)
        end = time.monotonic() + 240
        last_line = None
        while process.poll() is None and time.monotonic() < end:
            progress_path = ROOT / ('qa/native_readonly_' + args.run_id + '_progress.jsonl')
            if progress_path.exists():
                lines = progress_path.read_text(encoding='utf-8').splitlines()
                if lines and lines[-1] != last_line:
                    last_line = lines[-1]
                    print(last_line, flush=True)
            if native.exists():
                break
            time.sleep(2)
        state['cli_exit_code'] = process.poll()
        state['native_receipt_exists'] = native.exists()
        state['completed_observation_utc'] = now()
        state['status'] = 'RECEIPT_AVAILABLE' if native.exists() else 'STALLED_OR_EXITED_WITHOUT_NATIVE_RECEIPT'
        state['processes_after'] = snapshot()
        if native.exists():
            data = json.loads(native.read_text(encoding='utf-8'))
            state['native_status'] = data['status']
            state['originals_unchanged'] = data['all_originals_unchanged']
        write_new(path_for('runner', 'receipts', 'readonly_launcher_final_' + args.run_id + '.json'), state)
        # Never terminate Revit or the CLI here. If native state is unresolved,
        # keep the reservation file to prevent another launch. Reconciliation
        # must first establish the owned process actually exited.
        print(json.dumps(state, indent=2), flush=True)
    return 0 if native.exists() else 3


if __name__ == '__main__':
    raise SystemExit(main())

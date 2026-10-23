"""Task-local launcher; native receipt, never CLI exit, establishes completion."""
import argparse, datetime, json, os, pathlib, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[1]
def write(p, obj):
    p = p.resolve()
    if ROOT not in p.parents: raise ValueError('Write outside task root')
    p.write_text(json.dumps(obj, indent=2), encoding='utf-8')
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('phase', choices=['probe','build','qa'])
    ap.add_argument('--revision', default='r01')
    args=ap.parse_args()
    names={'probe':'probe_native.py','build':'build_batch.py','qa':'qa_batch.py'}
    scripts={'probe':'runner','build':'scripts','qa':'qa'}
    script=ROOT / scripts[args.phase] / names[args.phase]
    receipt=ROOT / 'runner' / 'receipts' / (args.phase+'_launcher_'+args.revision+'.json')
    if receipt.exists(): raise RuntimeError('No replay or overwrite')
    native=ROOT / 'runner' / 'receipts' / ('probe_native.json' if args.phase=='probe' else args.phase+'_final_'+args.revision+'.json')
    if native.exists(): raise RuntimeError('Native receipt exists')
    env=os.environ.copy()
    env['TEMP']=str(ROOT/'temp');env['TMP']=str(ROOT/'temp')
    env['BELMONT_PHASE_REVISION']=args.revision
    command=[r'D:\Games\pyRevit-Master\bin\pyrevit.exe','run',str(script),'--revit=2025']
    log=ROOT/'runner'/'receipts'/(args.phase+'_stdout_'+args.revision+'.log')
    rec={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':command,'native_receipt':str(native),'status':'STARTING'}
    with log.open('xb') as out:
        proc=subprocess.Popen(command,cwd=str(ROOT),env=env,stdout=out,stderr=subprocess.STDOUT,creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        rec['owned_cli_pid']=proc.pid;write(receipt,rec)
        print('Started task-local pyRevit CLI PID',proc.pid,flush=True)
        deadline=time.monotonic()+300
        while proc.poll() is None and time.monotonic()<deadline: time.sleep(2)
        rec['cli_exit_code']=proc.poll()
        rec['status']='NATIVE_RECEIPT_PRESENT' if native.exists() else ('TIMEOUT_NO_RECEIPT' if proc.poll() is None else 'MISSING_NATIVE_RECEIPT')
        if native.exists():
            data=json.loads(native.read_text(encoding='utf-8-sig'))
            rec['native_status']=data.get('status');rec['native_all_pass']=data.get('all_pass')
        write(receipt,rec)
    print(json.dumps(rec),flush=True)
    return 0 if rec.get('native_status')=='PASS' or rec.get('native_all_pass') is True else 3
if __name__=='__main__': sys.exit(main())

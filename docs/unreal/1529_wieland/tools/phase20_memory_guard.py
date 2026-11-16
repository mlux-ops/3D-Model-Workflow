"""Poll device memory independently of the editor; cancel a render at the supplied MiB limit.

Run beside memory_log.ps1. Never terminates the editor. A stop file ends monitoring.
"""
import datetime
import json
import pathlib
import subprocess
import sys
import time

import ue_call

target = pathlib.Path(sys.argv[1])
limit = int(sys.argv[2])
stop = pathlib.Path(str(target) + '.stop')
target.parent.mkdir(parents=True, exist_ok=True)
with target.open('a', encoding='utf-8') as log:
    while not stop.exists():
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total',
                                 '--format=csv,noheader,nounits'], capture_output=True, text=True, check=True)
        used, total = [int(x.strip()) for x in result.stdout.strip().split(',')]
        record = {'time': datetime.datetime.now().isoformat(), 'used_mib': used, 'total_mib': total}
        if used >= limit:
            client = ue_call.Client()
            client.open()
            record['cancel'] = client.call('call_tool', {
                'toolset_name': ue_call.PY_TOOLSET, 'tool_name': ue_call.PY_TOOL,
                'arguments': {'script': {'content':
                    'q=unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)\n'
                    'e=q.get_active_executor()\n'
                    'e.cancel_all_jobs() if e else None\n'
                    '{"cancel_requested":e is not None}', 'language': 'Python'}}}, 30)
        log.write(json.dumps(record) + chr(10))
        log.flush()
        if used >= limit:
            break
        time.sleep(3)

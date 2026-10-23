# -*- coding: utf-8 -*-
import os, json, time, traceback
BASE = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017'
receipt = os.path.join(BASE, 'runner', 'receipts', 'probe_native.json')
if os.path.exists(receipt): raise RuntimeError('Receipt exists; do not replay')
report = {'status': 'STARTED', 'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
try:
    app = __revit__.Application
    if getattr(__revit__, 'ActiveUIDocument', None) is not None:
        raise RuntimeError('Refuse active document; isolated empty session required')
    report['version'] = str(app.VersionNumber)
    report['pid'] = __import__('System').Diagnostics.Process.GetCurrentProcess().Id
    report['documents'] = [d.Title for d in app.Documents]
    report['status'] = 'PASS' if report['version'] == '2025' and not report['documents'] else 'HOLD'
except Exception:
    report['status'] = 'ERROR'
    report['error'] = traceback.format_exc()
    raise
finally:
    with open(receipt, 'w') as f: json.dump(report, f, indent=2, default=str)

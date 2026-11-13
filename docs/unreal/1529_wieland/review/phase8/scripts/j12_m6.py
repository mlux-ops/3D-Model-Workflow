"""Phase 8, step 8.11: one run of profile M6. Reads profiles/2026-11-12_M6/job.json =
{"parts": [...], "tag": "", "trial_seconds": null, "cvars": {}} and returns the record of
tools/phase8_profile_m6.py. Saves nothing."""
import importlib
import json
import os

import wieland_lighting as wl
import phase8_profile_m6 as m6

importlib.reload(m6)
folder = os.path.join(os.path.dirname(os.path.dirname(wl.REVIEW)), "profiles", "2026-11-12_M6")
with open(os.path.join(folder, "job.json"), "r", encoding="utf-8") as handle:
    job = json.load(handle)
record = await m6.run(folder.replace("\\", "/"), parts=tuple(job["parts"]), tag=job.get("tag", ""),
                      trial_seconds=job.get("trial_seconds"), cvars=job.get("cvars") or {})
json.dumps(record)

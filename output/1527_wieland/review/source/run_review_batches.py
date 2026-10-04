import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REVIEW = os.path.dirname(HERE)
BATCH_DIR = os.path.join(REVIEW, "batches")
TARGETS = os.path.join(REVIEW, "review_targets.json")
NATIVE = os.path.join(REVIEW, "native_review.json")
SCRIPT = os.path.join(HERE, "review_rfas.py")
RUNNER = os.path.abspath(os.path.join(
    REVIEW, "..", "..", "effort-trial-2026-09-29-sonnet",
    "sconce", "_harness", "revit_run.py"
))

with open(os.path.join(BATCH_DIR, "manifest.json"), "r", encoding="utf-8") as f:
    manifest = json.load(f)

summary = {"runs": [], "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
for entry in manifest["batches"]:
    src = os.path.join(BATCH_DIR, entry["name"])
    result_path = os.path.join(BATCH_DIR, entry["name"].replace("targets_", "result_"))
    if os.path.isfile(result_path):
        try:
            old = json.load(open(result_path, "r", encoding="utf-8"))
            if len(old.get("targets", [])) == entry["count"] and not old.get("errors"):
                summary["runs"].append({
                    "batch": entry["name"],
                    "count": entry["count"],
                    "exit_code": 0,
                    "skipped_existing_complete": True,
                })
                print("SKIP complete", entry["name"], flush=True)
                continue
        except Exception:
            pass

    shutil.copyfile(src, TARGETS)
    if os.path.exists(NATIVE):
        os.remove(NATIVE)
    print("RUN", entry["name"], "count", entry["count"], flush=True)
    proc = subprocess.run([sys.executable, RUNNER, SCRIPT, "240"])
    record = {
        "batch": entry["name"],
        "count": entry["count"],
        "exit_code": proc.returncode,
        "result_path": result_path,
    }
    if os.path.isfile(NATIVE):
        shutil.copyfile(NATIVE, result_path)
        try:
            data = json.load(open(result_path, "r", encoding="utf-8"))
            record["processed"] = len(data.get("targets", []))
            record["errors"] = len(data.get("errors", []))
        except Exception as exc:
            record["parse_error"] = str(exc)
    summary["runs"].append(record)
    print(json.dumps(record), flush=True)

summary["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
with open(os.path.join(BATCH_DIR, "batch_run_summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)
print(json.dumps(summary, indent=2), flush=True)

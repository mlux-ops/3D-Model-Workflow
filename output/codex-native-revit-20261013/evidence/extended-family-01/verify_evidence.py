"""Independent detached verification of native operation receipts; no Revit mutations."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
report = json.loads((ROOT / "extended-family-report.json").read_text(encoding="utf-8"))
steps = report["steps"]
checks = {}


def check(key, actual, expected, tolerance=1e-6):
    passed = actual == expected if isinstance(expected, (str, bool)) else math.isclose(actual, expected, abs_tol=tolerance, rel_tol=1e-7)
    checks[key] = {"actual": actual, "expected": expected, "tolerance": tolerance, "pass": passed}


check("isolated-process", report["capabilities"]["process_id"], 27208)
casework = report["parametric_casework"]
flex = steps["cabinet-attempt-1-flex"]
check("flex-native-job-completed", flex["status"], "completed")
check("flex-native-group-rolled-back", flex["result"]["transaction_status"], "rolled_back")
check("flex-restoration-confirmed", flex["result"]["original_state_restored"], True)
uid = casework["geometry_unique_id"]
for index, (scenario, snapshot) in enumerate(zip(flex["request"]["arguments"]["types"], flex["result"]["snapshots"])):
    native = next(f for f in snapshot["result"]["geometry"]["forms"] if f["element"]["unique_id"] == uid)
    bounds = native["geometry"]["bounds"]
    dimensions = [scenario["values"][name] for name in ("CodexWidth", "CodexDepth", "CodexHeight")]
    for axis, requested in enumerate(dimensions):
        check(f"flex-{index}-axis-{axis}", bounds["max"][axis] - bounds["min"][axis], requested)
    check(f"flex-{index}-volume", sum(s["volume"] for s in native["geometry"]["solids"]), math.prod(dimensions))
reopen = steps["saved-casework-reopen-geometry"]["result"]
inspect = steps["saved-casework-reopen-inspect"]["result"]
type_info = next(t for t in inspect["types"] if t["name"] == "Codex_Parametric_Box")
native = next(f for f in reopen["forms"] if f["element"]["unique_id"] == uid)
bounds = native["geometry"]["bounds"]
parameters = [next(v["value"] for v in type_info["values"] if v["parameter"]["name"] == p) for p in ("CodexWidth", "CodexDepth", "CodexHeight")]
for axis, param in enumerate(parameters):
    check(f"saved-native-axis-matches-parameter-{axis}", bounds["max"][axis] - bounds["min"][axis], param)
check("saved-native-volume-matches-parameters", sum(s["volume"] for s in native["geometry"]["solids"]), math.prod(parameters))
check("saved-native-category", inspect["category"], "Casework")
path = Path(casework["family_file"]).resolve()
check("saved-path-contained-in-evidence", path.is_relative_to(ROOT), True)
check("saved-file-hash", hashlib.sha256(path.read_bytes()).hexdigest(), report["saved_casework_reopen"]["sha256"])
check("saved-file-nonempty", path.stat().st_size > 0, True)
for name, outcome in report["effective_smokes"].items():
    check("effective-smoke-" + name, outcome.startswith("passed"), True)
for repair in ("revolution-1", "material-1"):
    check("repair-receipt-" + repair, report["smoke_repairs"][repair]["status"], "passed")
original_failures = [{"check": k, **v} for k, v in report["checks"].items() if not v["pass"]]
check("unexplained-original-check-failures", any(r["check"] != "revolution-native-volume" for r in original_failures), False)
result = {"native_process_id": 27208, "technical_pass": all(c["pass"] for c in checks.values()),
          "checks": checks, "first_attempt_failed_checks_retained": original_failures,
          "assisted_repairs": report["smoke_repairs"], "visual_acceptance": "not assessed",
          "boundary": "Native synthetic Casework parametric geometry and targeted basic family API smokes; no production/manufacturer design acceptance."}
(ROOT / "independent-verification.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"technical_pass": result["technical_pass"], "checks": len(checks)}))
raise SystemExit(0 if result["technical_pass"] else 1)

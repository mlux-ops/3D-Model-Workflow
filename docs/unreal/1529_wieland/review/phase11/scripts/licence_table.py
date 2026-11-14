"""Phase 11, step 11.6: the licence table of the packaged build.

    python -B review/phase11/scripts/licence_table.py <cooked folder> <out LICENCES.csv> [<out summary .json>]

<cooked folder> is the cook's output for Windows (the project's Saved\\Cooked\\Windows), which holds exactly the assets
the build contains, before they are packed. Every cooked asset (.uasset or .umap) of the project's own content is
looked up by path in the project's licence record (asset_licences.csv, one row per file, made in Phase 5) and counted
under its group (asset_licence_groups.csv: source, licence, status, evidence). Assets made after that record:
those under Content/Wieland1529/ are this project's own work; anything else is listed as "not in the licence record".
Engine and engine-plugin content is one row (Epic Games, Unreal Engine licence).
The output has one row for every group found in the build, with the number and size of its cooked files.
"""
import csv
import json
import os
import sys

PLAN = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
cooked, out_csv = sys.argv[1], sys.argv[2]
out_json = sys.argv[3] if len(sys.argv) > 3 else None

with open(os.path.join(PLAN, "asset_licences.csv"), newline="", encoding="utf-8-sig") as handle:
    by_file = {row["file"].replace("\\", "/"): row for row in csv.DictReader(handle)}
with open(os.path.join(PLAN, "asset_licence_groups.csv"), newline="", encoding="utf-8-sig") as handle:
    groups = {row["group"]: row for row in csv.DictReader(handle)}

project_root = None
for name in os.listdir(cooked):
    if os.path.isdir(os.path.join(cooked, name, "Content")) and name != "Engine":
        project_root = os.path.join(cooked, name)
if project_root is None:
    raise SystemExit("no project folder with Content under " + cooked)

found = {}


per_file = []  # every cooked asset of the build with its group: the per-asset form of the table


def add(group, rel, size):
    entry = found.setdefault(group, {"files": 0, "bytes": 0, "example": rel})
    entry["files"] += 1
    entry["bytes"] += size
    per_file.append((rel, group, size))


def companions(path):
    """The asset file plus the .uexp/.ubulk/.uptnl files the cook writes beside it."""
    base = os.path.splitext(path)[0]
    total = 0
    for ext in (".uasset", ".umap", ".uexp", ".ubulk", ".uptnl", ".m.ubulk"):
        if os.path.exists(base + ext):
            total += os.path.getsize(base + ext)
    return total


content = os.path.join(project_root, "Content")
for root, _, files in os.walk(content):
    for f in files:
        if not f.endswith((".uasset", ".umap")):
            continue
        full = os.path.join(root, f)
        rel = "Content/" + os.path.relpath(full, content).replace(os.sep, "/")
        row = by_file.get(rel)
        if row:
            group = row["group"]
        elif rel.startswith("Content/Wieland1529/"):
            group = "This project's own work, made after the licence record of Phase 5"
        else:
            group = "Not in the licence record: " + "/".join(rel.split("/")[:3])
        add(group, rel, companions(full))

engine_files = engine_bytes = 0
engine_root = os.path.join(cooked, "Engine")
if os.path.isdir(engine_root):
    for root, _, files in os.walk(engine_root):
        for f in files:
            if f.endswith((".uasset", ".umap")):
                size = companions(os.path.join(root, f))
                engine_files += 1
                engine_bytes += size
                per_file.append(("Engine/" + os.path.relpath(os.path.join(root, f), engine_root).replace(os.sep, "/"),
                                 "Unreal Engine and engine-plugin content", size))

rows = []
for group, entry in sorted(found.items(), key=lambda kv: -kv[1]["bytes"]):
    info = groups.get(group, {})
    if group.startswith("This project's own work"):
        status, licence, source, note = "owner's own", "No outside licence needed", "Made in this project (Phases 6 to 15)", "Path under Content/Wieland1529/ and not in the Phase 5 record"
    elif group.startswith("Not in the licence record"):
        status, licence, source, note = "NOT RECORDED", "Not recorded", "Not recorded", "Found in the build but absent from asset_licences.csv; owner to identify"
    else:
        status = info.get("status", "")
        licence = info.get("licence", "")
        source = info.get("source", "")
        note = info.get("evidence_or_note", "")
    rows.append({"group": group, "status": status, "licence_as_recorded": licence, "source": source,
                 "cooked_files": entry["files"], "cooked_mb": round(entry["bytes"] / 1048576.0, 1),
                 "example_in_build": entry["example"], "evidence_or_note": note})
rows.append({"group": "Unreal Engine and engine-plugin content", "status": "recorded",
             "licence_as_recorded": "Unreal Engine End User License Agreement (Epic Games): engine content may be distributed inside a packaged build",
             "source": "Epic Games, Unreal Engine 5.9", "cooked_files": engine_files, "cooked_mb": round(engine_bytes / 1048576.0, 1),
             "example_in_build": "Engine/Content/...", "evidence_or_note": "Comes with the engine"})

with open(out_csv, "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
status_of = {r["group"]: (r["status"], r["licence_as_recorded"]) for r in rows}
files_csv = os.path.splitext(out_csv)[0] + "_per_asset.csv"
with open(files_csv, "w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["asset_in_build", "group", "status", "licence_as_recorded", "cooked_bytes"])
    for rel, group, size in sorted(per_file):
        writer.writerow([rel, group, status_of[group][0], status_of[group][1], size])
summary = {"cooked_folder": cooked, "groups": len(rows),
           "not_recorded_groups": [r["group"] for r in rows if r["status"] in ("NO RECORD", "NOT RECORDED")],
           "not_recorded_mb": round(sum(r["cooked_mb"] for r in rows if r["status"] in ("NO RECORD", "NOT RECORDED")), 1),
           "project_asset_files": sum(r["cooked_files"] for r in rows[:-1]), "engine_asset_files": engine_files}
if out_json:
    with open(out_json, "w", encoding="utf-8") as handle:
        json.dump({"summary": summary, "rows": rows}, handle, indent=1)
print(json.dumps(summary))

"""Phase 11, step 11.6: the licence table of the packaged build.

    python -B review/phase11/scripts/licence_table.py <Manifest_UFSFiles_Win64.txt> <project Content folder> <out LICENCES.csv> [<out summary .json>]

The build's own list of packed files (Manifest_UFSFiles_Win64.txt, written by the packaging tool beside the build)
names exactly the assets the build contains. Every packed asset (.uasset or .umap) of the project's own content
(Wieland1527/Content/...) is looked up by path in the project's licence record (asset_licences.csv, one row per file,
made in Phase 5) and counted under its group (asset_licence_groups.csv: source, licence, status, evidence). Assets
made after that record: those under Content/Wieland1529/ are this project's own work; anything else is listed as
"not in the licence record". Engine and engine-plugin content (Engine/...) is one group (Epic Games, Unreal Engine
licence). Sizes are those of the source assets in the project (the packed sizes are compressed inside one container).
Writes the table (one row per group) and <table>_per_asset.csv (one row per packed asset, with its group).
"""
import csv
import json
import os
import sys

PLAN = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
manifest, content_root, out_csv = sys.argv[1], sys.argv[2], sys.argv[3]
out_json = sys.argv[4] if len(sys.argv) > 4 else None

with open(os.path.join(PLAN, "asset_licences.csv"), newline="", encoding="utf-8-sig") as handle:
    by_file = {row["file"].replace("\\", "/"): row for row in csv.DictReader(handle)}
with open(os.path.join(PLAN, "asset_licence_groups.csv"), newline="", encoding="utf-8-sig") as handle:
    groups = {row["group"]: row for row in csv.DictReader(handle)}

ENGINE_GROUP = "Unreal Engine and engine-plugin content"
OWN_GROUP = "This project's own work, made after the licence record of Phase 5"
found, per_file = {}, []


def source_bytes(rel):
    base = os.path.splitext(os.path.join(content_root, rel[len("Content/"):]))[0]
    return sum(os.path.getsize(base + ext) for ext in (".uasset", ".umap", ".uexp", ".ubulk") if os.path.exists(base + ext))


with open(manifest, encoding="utf-8", errors="replace") as handle:
    for line in handle:
        path = line.split("\t")[0].strip().replace("\\", "/")
        if not path.endswith((".uasset", ".umap")):
            continue
        if path.startswith("Engine/"):
            group, rel, size = ENGINE_GROUP, path, 0
        else:
            rel = path.split("/", 1)[1] if "/" in path else path  # drop the project folder name
            row = by_file.get(rel)
            if row:
                group = row["group"]
            elif rel.startswith("Content/Wieland1529/"):
                group = OWN_GROUP
            else:
                group = "Not in the licence record: " + "/".join(rel.split("/")[:3])
            size = source_bytes(rel)
        entry = found.setdefault(group, {"files": 0, "bytes": 0, "example": path})
        entry["files"] += 1
        entry["bytes"] += size
        per_file.append((path, group, size))

rows = []
for group, entry in sorted(found.items(), key=lambda kv: (kv[0] == ENGINE_GROUP, -kv[1]["bytes"])):
    info = groups.get(group, {})
    if group == ENGINE_GROUP:
        status = "recorded"
        licence = "Unreal Engine End User License Agreement (Epic Games): engine and engine-plugin content may be distributed inside a packaged build"
        source, note = "Epic Games, Unreal Engine 5.9 and its plugins", "Comes with the engine; sizes not counted"
    elif group == OWN_GROUP:
        status, licence, source, note = "owner's own", "No outside licence needed", "Made in this project (Phases 6 to 15)", "Path under Content/Wieland1529/ and not in the Phase 5 record"
    elif group.startswith("Not in the licence record"):
        status, licence, source, note = "NOT RECORDED", "Not recorded", "Not recorded", "Packed in the build but absent from asset_licences.csv; owner to identify"
    else:
        status, licence, source, note = info.get("status", ""), info.get("licence", ""), info.get("source", ""), info.get("evidence_or_note", "")
    rows.append({"group": group, "status": status, "licence_as_recorded": licence, "source": source,
                 "assets_in_build": entry["files"], "source_mb": round(entry["bytes"] / 1048576.0, 1),
                 "example_in_build": entry["example"], "evidence_or_note": note})

with open(out_csv, "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
status_of = {r["group"]: (r["status"], r["licence_as_recorded"]) for r in rows}
files_csv = os.path.splitext(out_csv)[0] + "_per_asset.csv"
with open(files_csv, "w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["asset_in_build", "group", "status", "licence_as_recorded", "source_bytes"])
    for path, group, size in sorted(per_file):
        writer.writerow([path, group, status_of[group][0], status_of[group][1], size])
unrecorded = [r for r in rows if r["status"] in ("NO RECORD", "NOT RECORDED")]
summary = {"manifest": manifest, "groups": len(rows), "assets_in_build": len(per_file),
           "not_recorded_groups": [(r["group"], r["assets_in_build"]) for r in unrecorded],
           "not_recorded_assets": sum(r["assets_in_build"] for r in unrecorded)}
if out_json:
    with open(out_json, "w", encoding="utf-8") as handle:
        json.dump({"summary": summary, "rows": rows}, handle, indent=1)
print(json.dumps(summary))

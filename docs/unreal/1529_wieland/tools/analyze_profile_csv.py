"""Reduce the engine's CSV profile captures named in a capture record.

Usage:
    python analyze_profile_csv.py <capture record .json> [--copy-to <folder>]

The capture record is the JSON that wieland_profile.py writes. For each job
it names the CSV file the engine wrote. This script reads each CSV and
prints, and writes beside the record as <record>.analysis.json:

    frames, mean, 95th percentile, worst and best frame time (ms);
    graphics-card, game-thread, render-thread and RHI-thread times;
    peak video memory used by the editor process; draw calls; primitives.

The method matches the October 2026 benchmark so the numbers can be set side
by side: the header row repeated at the end of the file is authoritative,
every row with a positive numeric FrameTime counts (outliers included), and
the 95th percentile is the value at index floor(0.95 * (n - 1)) of the sorted
frame times.

With --copy-to, each CSV is copied into that folder as <job name>.csv.gz.
"""

import csv
import gzip
import json
import os
import shutil
import sys

STATS = [
    "FrameTime",
    "GPUTime",
    "GameThreadTime",
    "RenderThreadTime",
    "RHIThreadTime",
    "GPUMem/LocalUsedMB",
    "GPUMem/LocalBudgetMB",
    "RHI/DrawCalls",
    "RHI/PrimitivesDrawn",
    "TextureStreaming/DesiredDataLoadedPercent",
    "MemoryFreeMB",
    "PhysicalUsedMB",
]


def read_capture_csv(path):
    with open(path, newline="", encoding="utf-8", errors="replace") as handle:
        rows = list(csv.reader(handle))
    header_index = None
    for index in range(len(rows) - 1, -1, -1):
        if "FrameTime" in rows[index]:
            header_index = index
            break
    if header_index is None:
        raise ValueError("no header row with FrameTime in " + path)
    header = rows[header_index]
    metadata = {}
    for row in rows[header_index + 1:]:
        for position in range(0, len(row) - 1, 2):
            key = row[position]
            if key.startswith("[") and key.endswith("]"):
                metadata[key[1:-1]] = row[position + 1]
    frame_column = header.index("FrameTime")
    columns = {name: header.index(name) for name in STATS if name in header}
    series = {name: [] for name in columns}
    for index, row in enumerate(rows):
        if index == header_index or "FrameTime" in row:
            continue
        if len(row) <= frame_column:
            continue
        try:
            frame_time = float(row[frame_column])
        except ValueError:
            continue
        if frame_time <= 0.0:
            continue
        for name, column in columns.items():
            if column < len(row):
                try:
                    series[name].append(float(row[column]))
                except ValueError:
                    pass
    return series, metadata, len(header)


def reduce(values):
    if not values:
        return None
    ordered = sorted(values)
    count = len(ordered)
    return {
        "mean": sum(ordered) / count,
        "p95": ordered[int(0.95 * (count - 1))],
        "min": ordered[0],
        "max": ordered[-1],
    }


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    record_path = argv[1]
    copy_to = None
    if "--copy-to" in argv:
        copy_to = argv[argv.index("--copy-to") + 1]
        os.makedirs(copy_to, exist_ok=True)
    with open(record_path, encoding="utf-8") as handle:
        record = json.load(handle)
    folder = record["csv_folder"]
    output = {"source_record": os.path.basename(record_path), "info": record.get("info"), "method": "final header row; every positive FrameTime row; p95 = value at floor(0.95 * (n - 1))", "jobs": []}
    for job in record["jobs"]:
        files = job.get("new_csv_files") or []
        entry = {"name": job["name"], "kind": job["kind"], "csv": files, "foreground_fraction": job.get("foreground_fraction"), "recorded_seconds": job.get("recorded_seconds"), "tick_ms_mean": job.get("tick_ms_mean"), "tick_ms_p95": job.get("tick_ms_p95"), "tick_ms_max": job.get("tick_ms_max")}
        if len(files) != 1:
            entry["error"] = "expected one new CSV file, found %d" % len(files)
            output["jobs"].append(entry)
            continue
        path = os.path.join(folder, files[0])
        series, metadata, column_count = read_capture_csv(path)
        frame_times = series.get("FrameTime", [])
        entry["frames"] = len(frame_times)
        entry["columns"] = column_count
        entry["mean_fps"] = (1000.0 / (sum(frame_times) / len(frame_times))) if frame_times else None
        entry["frames_over_16_667ms"] = sum(1 for value in frame_times if value > 16.667)
        entry["frames_over_33_333ms"] = sum(1 for value in frame_times if value > 33.333)
        entry["stats"] = {name: reduce(values) for name, values in series.items()}
        entry["metadata"] = {key: metadata[key] for key in sorted(metadata) if key in ("Platform", "Config", "BuildVersion", "EngineVersion", "DeviceProfile", "CPU", "DesktopGPU", "RenderingGPU", "TargetFramerate", "Commandline", "StartTimestamp", "EndTimestamp", "NamedEvents", "ASAN", "PGO", "LoginID", "OS")}
        entry["metadata"].pop("LoginID", None)
        entry["metadata"].pop("Commandline", None)
        if copy_to:
            target = os.path.join(copy_to, job["name"] + ".csv.gz")
            with open(path, "rb") as source, gzip.open(target, "wb", compresslevel=9) as packed:
                shutil.copyfileobj(source, packed)
            entry["copied_to"] = os.path.basename(target)
            entry["copied_bytes"] = os.path.getsize(target)
        output["jobs"].append(entry)
    analysis_path = os.path.splitext(record_path)[0] + ".analysis.json"
    with open(analysis_path, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=1)
    for entry in output["jobs"]:
        if "error" in entry:
            print(entry["name"], "ERROR", entry["error"])
            continue
        stats = entry["stats"]
        frame = stats["FrameTime"]
        line = "%-22s frames %5d  frame mean %6.3f p95 %6.3f worst %7.3f ms  (%.1f fps)" % (entry["name"], entry["frames"], frame["mean"], frame["p95"], frame["max"], entry["mean_fps"])
        for name, label in (("GPUTime", "gpu"), ("GameThreadTime", "game"), ("RenderThreadTime", "render"), ("RHIThreadTime", "rhi")):
            if stats.get(name):
                line += "  %s %.2f" % (label, stats[name]["mean"])
        if stats.get("GPUMem/LocalUsedMB"):
            line += "  vram peak %.0f MB" % stats["GPUMem/LocalUsedMB"]["max"]
        line += "  fg %.2f  >16.7ms %d  >33.3ms %d" % (entry["foreground_fraction"] or 0.0, entry["frames_over_16_667ms"], entry["frames_over_33_333ms"])
        print(line)
    print("written", analysis_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

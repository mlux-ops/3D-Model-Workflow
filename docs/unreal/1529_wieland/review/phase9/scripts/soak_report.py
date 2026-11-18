"""Phase 9, step 9.11: reduce the soak's files to the figures of the acceptance line.

Usage:
    python -B soak_report.py [<soak folder name, default "soak">]

Reads profiles/2026-11-13_M7/<folder>/soak_log.jsonl (one line per walk of the exterior path), soak_watch.jsonl
(one line every five seconds about the editor's window) and the engine's own short recordings named in the log
(in the project's Saved/Profiling/CSV), which carry the video memory in use. Copies the video-memory figures to
<folder>/soak_video_memory.csv, writes <folder>/soak_report.json and prints the figures. Can be run while the soak
is still going; it then reports the walks so far.
"""

import csv
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, "/")
ROOT = HERE.rsplit("/review/", 1)[0]
CSV_DIR = "D:/Unreal_Engine_Projects/Wieland1527 5.9/Saved/Profiling/CSV"
EDITOR_LOG = "D:/Unreal_Engine_Projects/Wieland1527 5.9/Saved/Logs/Wieland1527.log"
MEMORY_LOG =ROOT + "/profiles/2026-11-13_M7/memory_log_phase9.csv"


def video_memory(name):
    """Mean and highest video memory in use (MB) and the count of frames in one of the engine's recordings."""
    path = CSV_DIR + "/" + name
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8", errors="replace") as handle:
        rows = list(csv.reader(handle))
    head = rows[0]
    if "GPUMem/LocalUsedMB" not in head:
        return None
    column = head.index("GPUMem/LocalUsedMB")
    values = []
    for row in rows[1:]:
        try:
            value = float(row[column])
        except (ValueError, IndexError):
            continue
        if value > 0:
            values.append(value)
    if not values:
        return None
    return {"mean_mb": sum(values) / len(values), "max_mb": max(values), "frames": len(values)}


def autosave_times():
    """Unix times of the editor's autosaves, one per burst, read from the editor's log (its stamps are UTC)."""
    import calendar
    import re

    if not os.path.exists(EDITOR_LOG):
        return None
    stamp = re.compile(r"^\[(\d{4})\.(\d\d)\.(\d\d)-(\d\d)\.(\d\d)\.(\d\d):\d+\]")
    moments = []
    with open(EDITOR_LOG, encoding="utf-8", errors="replace") as handle:
        for text in handle:
            if "/Temp/Autosaves/" not in text:
                continue
            found = stamp.match(text)
            if not found:
                continue
            moment = calendar.timegm(tuple(int(part) for part in found.groups()) + (0, 0, 0))
            if not moments or moment - moments[-1] > 30:
                moments.append(moment)
    return moments


def main(argv):
    folder = "%s/profiles/2026-11-13_M7/%s" % (ROOT, argv[1] if len(argv) > 1 else "soak")
    with open(folder + "/soak_log.jsonl", encoding="utf-8") as handle:
        lines = [json.loads(line) for line in handle if line.strip()]
    watch = []
    if os.path.exists(folder + "/soak_watch.jsonl"):
        with open(folder + "/soak_watch.jsonl", encoding="utf-8") as handle:
            watch = [json.loads(line) for line in handle if line.strip()]
    ended = os.path.exists(folder + "/soak_end.json")
    with_csv = [line for line in lines if "csv" in line]
    without_csv = [line for line in lines if "csv" not in line]
    expected_csv = [line for line in lines if (line["loop"] - 1) % 3 == 0]
    memory = []
    for line in with_csv:
        for name in line["csv"]:
            figures = video_memory(name)
            if figures:
                memory.append(dict(figures, loop=line["loop"], unix=line["unix"], file=name))
    with open(folder + "/soak_video_memory.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["walk", "time", "video_memory_mean_mb", "video_memory_max_mb", "frames", "engine_recording"])
        for item in memory:
            writer.writerow([item["loop"], time.strftime("%H:%M:%S", time.localtime(item["unix"])), "%.0f" % item["mean_mb"],
                             "%.0f" % item["max_mb"], item["frames"], item["file"]])
    ticks = sum(line["ticks"] for line in lines)
    report = {
        "soak_ended": ended,
        "walks_finished": len(lines),
        "first_walk_ended": time.strftime("%H:%M:%S", time.localtime(lines[0]["unix"])),
        "last_walk_ended": time.strftime("%H:%M:%S", time.localtime(lines[-1]["unix"])),
        "hours_walked": round(len(lines) * 60.0 / 3600.0, 2),
        "frames": ticks,
        "frame_mean_ms": round(sum(line["ms_mean"] * line["ticks"] for line in lines) / ticks, 3),
        "p95_ms_of_walks_lowest_highest": [min(line["ms_p95"] for line in lines), max(line["ms_p95"] for line in lines)],
        "walks_with_p95_over_16_67ms": sum(1 for line in lines if line["ms_p95"] > 16.667),
        "worst_frame_ms": max(line["ms_max"] for line in lines),
        "frames_over_33_3ms": sum(line["over_33ms"] for line in lines),
        "walks_with_a_frame_over_33_3ms": sum(1 for line in lines if line["over_33ms"]),
        "walks_recorded_by_the_engine_too": len(with_csv),
        "walks_that_should_carry_a_csv_entry_and_do": "%d of %d" % (sum(1 for line in expected_csv if "csv" in line), len(expected_csv)),
        "frames_over_33_3ms_in_walks_recorded_by_the_engine_too": sum(line["over_33ms"] for line in with_csv),
        "frames_over_33_3ms_in_the_other_walks": sum(line["over_33ms"] for line in without_csv),
        "worst_frame_ms_in_the_other_walks": max([line["ms_max"] for line in without_csv] or [0.0]),
        "walks_with_editor_in_front_all_the_time": sum(1 for line in lines if line["foreground_fraction"] >= 0.99),
        "walks_with_editor_not_in_front_at_all": sum(1 for line in lines if line["foreground_fraction"] <= 0.01),
        "times_window_put_back_on_screen": sum(int(item.get("window_restored") or 0) for item in watch),
        "watch_lines": len(watch),
        "watch_lines_with_somebody_at_keyboard_or_mouse": sum(1 for item in watch if item.get("idle_seconds", 999) < 10),
    }
    if memory:
        first, last = memory[0]["mean_mb"], memory[-1]["mean_mb"]
        highest = max(item["max_mb"] for item in memory)
        report.update({
            "video_memory_first_mb": round(first), "video_memory_last_mb": round(last),
            "video_memory_lowest_mean_mb": round(min(item["mean_mb"] for item in memory)),
            "video_memory_peak_mb": round(highest),
            "video_memory_growth_first_to_last_percent": round(100.0 * (last - first) / first, 2),
            "video_memory_growth_first_to_peak_percent": round(100.0 * (highest - first) / first, 2),
        })
    if os.path.exists(MEMORY_LOG):
        with open(MEMORY_LOG, encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(lines[0]["unix"] - 60))
        end = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(lines[-1]["unix"]))
        rows = [row for row in rows if start <= row["time"] <= end]
        if rows:
            report.update({
                "memory_log_lines_during_soak": len(rows),
                "editor_committed_gb_first_last_highest": [float(rows[0]["editor_committed_gb"]), float(rows[-1]["editor_committed_gb"]),
                                                           max(float(row["editor_committed_gb"]) for row in rows)],
                "free_commit_gb_lowest": min(float(row["free_commit_gb"]) for row in rows),
            })
    # The editor saves a spare copy of every level marked unsaved every ten minutes (autosave), which stalls it for
    # about a second. The editor's log gives the times (in UTC); walks in which one fell are counted apart.
    saves = autosave_times()
    if saves is not None:
        hit = [line for line in lines if any(line["unix"] - 61.0 <= moment <= line["unix"] + 1.0 for moment in saves)]
        clean = [line for line in lines if line not in hit and "csv" not in line]
        report.update({
            "autosaves_of_the_editor_during_the_soak": sum(1 for moment in saves if lines[0]["unix"] - 61.0 <= moment <= lines[-1]["unix"]),
            "walks_with_an_autosave": len(hit),
            "frames_over_33_3ms_in_walks_with_an_autosave": sum(line["over_33ms"] for line in hit),
            "walks_with_neither_autosave_nor_engine_recording": len(clean),
            "frames_over_33_3ms_in_those_walks": sum(line["over_33ms"] for line in clean),
            "worst_frame_ms_in_those_walks": max([line["ms_max"] for line in clean] or [0.0]),
            "p95_ms_highest_in_those_walks": max([line["ms_p95"] for line in clean] or [0.0]),
        })
    with open(folder + "/soak_report.json", "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=1)
    for key, value in report.items():
        print("%-58s %s" % (key, value))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

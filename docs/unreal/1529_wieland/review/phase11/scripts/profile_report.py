"""Phase 11, step 11.5: reduce the packaged build's frame-time record to the final profile.

    python -B review/phase11/scripts/profile_report.py <capture .csv> <video_memory.csv> <out folder> <label> <card baseline MB>

The record's first column (EVENTS) carries the name of each shot of SEQ_W1529_ProfilePaths when it starts
(written by the engine), so every frame is given to the path or hold the camera was on. A "pass" is one play of the
whole sequence; it begins at the event "settle_exterior". The first pass loads and warms the program (Phase 9's
"first walk"); the profile is the second pass, and every later complete pass is reported beside it.

Statistics follow tools/analyze_profile_csv.py (the October method): every row with a positive FrameTime counts,
the 95th percentile is the sorted value at index floor(0.95 * (n - 1)). Video memory: the record's
GPUMem/LocalUsedMB (the engine's own reading, as Phase 9) and the dedicated memory Windows reports for the program.
Writes <out>/final_profile_<label>.json and .md.
"""
import csv
import json
import math
import os
import sys

SETTLE_PREFIX = "settle_"
LIMIT_MS, BUDGET_GPU_MS, LIMIT_VRAM_MB = 16.67, 14.5, 13.0 * 1024
# The shot names of SEQ_W1529_ProfilePaths (review/phase11/profile_segments.json, written by profile_seq_build.py).
_SEGMENTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "profile_segments.json")
with open(_SEGMENTS_FILE, encoding="utf-8") as _handle:
    KNOWN = {s["segment"] for s in json.load(_handle)["segments"]}


def pct(sorted_values, q):
    return sorted_values[int(math.floor(q * (len(sorted_values) - 1)))] if sorted_values else None


def read(path):
    with open(path, newline="", encoding="utf-8", errors="replace") as handle:
        rows = list(csv.reader(handle))
    header = rows[0]
    metadata = {}
    body = []
    for row in rows[1:]:
        if row and row[0] == "EVENTS" or (row and "FrameTime" in row):
            continue
        if row and row[0].startswith("[") and len(row) > 1 and row[0].endswith("]"):
            for i in range(0, len(row) - 1, 2):
                if row[i].startswith("[") and row[i].endswith("]"):
                    metadata[row[i][1:-1]] = row[i + 1]
            continue
        body.append(row)
    return header, body, metadata


def main():
    capture, vram_csv, out = sys.argv[1], sys.argv[2], sys.argv[3]
    label = sys.argv[4] if len(sys.argv) > 4 else "packaged"
    header, body, metadata = read(capture)
    col = {name: header.index(name) for name in header}
    need = ["FrameTime", "GPUTime", "GameThreadTime", "RenderThreadTime", "RHIThreadTime", "GPUMem/LocalUsedMB",
            "GPUMem/LocalBudgetMB", "RHI/DrawCalls"]
    have = [n for n in need if n in col]
    segment, passno = None, 0
    frames = []
    events_seen = []
    for row in body:
        events = [e for e in (row[0].split(";") if row and row[0] else []) if e]
        for event in events:
            name = event.strip()
            if name not in KNOWN:  # other engine events (console commands and the like) do not move the camera
                continue
            events_seen.append(name)
            if name == "settle_exterior":
                passno += 1
            segment = name
        try:
            frame_time = float(row[col["FrameTime"]])
        except (ValueError, IndexError):
            continue
        if frame_time <= 0.0:
            continue
        values = {}
        for n in have:
            try:
                values[n] = float(row[col[n]])
            except (ValueError, IndexError):
                pass
        frames.append({"pass": passno, "segment": segment, **values})

    def stats(subset):
        ft = sorted(f["FrameTime"] for f in subset)
        if not ft:
            return None
        out = {"frames": len(ft), "seconds": round(sum(ft) / 1000.0, 1), "mean_ms": round(sum(ft) / len(ft), 2),
               "p95_ms": round(pct(ft, 0.95), 2), "worst_ms": round(ft[-1], 2),
               "over_16_67": sum(1 for v in ft if v > LIMIT_MS), "over_33_3": sum(1 for v in ft if v > 33.3)}
        for n, key in (("GPUTime", "gpu_mean_ms"), ("GameThreadTime", "game_thread_mean_ms"), ("RenderThreadTime", "render_thread_mean_ms")):
            v = [f[n] for f in subset if n in f]
            if v:
                out[key] = round(sum(v) / len(v), 2)
        v = [f["GPUMem/LocalUsedMB"] for f in subset if "GPUMem/LocalUsedMB" in f]
        if v:
            out["vram_peak_mb_engine"] = round(max(v))
        return out

    passes = sorted({f["pass"] for f in frames if f["pass"] >= 1})
    complete = []
    for p in passes:
        segs = {f["segment"] for f in frames if f["pass"] == p}
        if "roof_deck_path" in segs and any(f["pass"] == p + 1 for f in frames):
            complete.append(p)
    report = {"label": label, "capture": os.path.basename(capture), "metadata": metadata, "frames_in_record": len(frames),
              "passes_started": len(passes), "complete_passes": complete, "per_pass": {}}
    order = []
    for e in events_seen:
        if e not in order:
            order.append(e)
    for p in complete:
        rows = [f for f in frames if f["pass"] == p]
        per = {seg: stats([f for f in rows if f["segment"] == seg]) for seg in order}
        measured = [f for f in rows if f["segment"] and not f["segment"].startswith(SETTLE_PREFIX)]
        per["ALL_PATHS_AND_HOLDS"] = stats(measured)
        report["per_pass"][str(p)] = per
    card = []
    with open(vram_csv, newline="", encoding="ascii", errors="replace") as handle:
        for row in csv.DictReader(handle):
            try:
                card.append(float(row["card_dedicated_mb"]))
            except (ValueError, KeyError):
                pass
    baseline = float(sys.argv[5]) if len(sys.argv) > 5 else None
    report["card_dedicated_peak_mb"] = round(max(card)) if card else None
    report["card_dedicated_baseline_mb"] = baseline
    report["card_peak_minus_baseline_mb"] = round(max(card) - baseline) if card and baseline is not None else None
    budget = [f["GPUMem/LocalBudgetMB"] for f in frames if "GPUMem/LocalBudgetMB" in f]
    report["engine_local_budget_mb"] = [round(min(budget)), round(max(budget))] if budget else None
    profile_pass = str(complete[1]) if len(complete) > 1 else (str(complete[0]) if complete else None)
    report["profile_pass"] = profile_pass
    if profile_pass:
        allp = report["per_pass"][profile_pass]["ALL_PATHS_AND_HOLDS"]
        peak_engine = max((s.get("vram_peak_mb_engine") or 0) for s in report["per_pass"][profile_pass].values() if s)
        peak_engine_all = max((f.get("GPUMem/LocalUsedMB") or 0) for f in frames)
        report["acceptance"] = {
            "p95_all_paths_ms": allp["p95_ms"], "p95_limit_ms": LIMIT_MS, "p95_met": allp["p95_ms"] <= LIMIT_MS,
            "worst_path_p95_ms": max(s["p95_ms"] for k, s in report["per_pass"][profile_pass].items() if s and not k.startswith(SETTLE_PREFIX) and k != "ALL_PATHS_AND_HOLDS"),
            "vram_peak_mb_engine_profile_pass": peak_engine, "vram_peak_mb_engine_whole_record": round(peak_engine_all),
            "card_peak_minus_baseline_mb": report["card_peak_minus_baseline_mb"],
            "vram_limit_mb": LIMIT_VRAM_MB, "vram_met": peak_engine_all <= LIMIT_VRAM_MB}
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "final_profile_%s.json" % label), "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=1)
    lines = ["# Final profile, packaged build (%s)" % label, "",
             "Record: `%s`, %d frames, passes started %d, complete passes %s; the profile is pass %s." % (
                 os.path.basename(capture), len(frames), len(passes), complete, profile_pass), ""]
    for p in complete:
        lines += ["## Pass %s%s" % (p, " (the profile)" if str(p) == profile_pass else ""), "",
                  "| Path or hold | Frames | Mean (ms) | 95th percentile (ms) | Worst (ms) | Over 16.67 ms | Over 33.3 ms | Graphics card mean (ms) | Game thread mean (ms) | Render thread mean (ms) | Video memory peak, engine (MB) |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
        for seg, s in report["per_pass"][str(p)].items():
            if not s:
                continue
            lines.append("| %s | %d | %s | %s | %s | %d | %d | %s | %s | %s | %s |" % (
                seg, s["frames"], s["mean_ms"], s["p95_ms"], s["worst_ms"], s["over_16_67"], s["over_33_3"],
                s.get("gpu_mean_ms", ""), s.get("game_thread_mean_ms", ""), s.get("render_thread_mean_ms", ""), s.get("vram_peak_mb_engine", "")))
        lines.append("")
    lines += ["Video memory, whole graphics card as Windows reports it (dedicated): peak %s MB, %s MB in use before the program started (the editor on an empty level and the desktop), difference %s MB. The engine's own budget for the program: %s MB." % (
        report["card_dedicated_peak_mb"], report["card_dedicated_baseline_mb"], report["card_peak_minus_baseline_mb"], report["engine_local_budget_mb"]), ""]
    if report.get("acceptance"):
        lines += ["Acceptance: " + json.dumps(report["acceptance"]), ""]
    with open(os.path.join(out, "final_profile_%s.md" % label), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    print(json.dumps({k: report[k] for k in ("frames_in_record", "passes_started", "complete_passes", "profile_pass", "card_dedicated_peak_mb", "card_peak_minus_baseline_mb", "engine_local_budget_mb")}))
    print(json.dumps(report.get("acceptance")))


main()

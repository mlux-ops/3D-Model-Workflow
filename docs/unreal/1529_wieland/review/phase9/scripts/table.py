"""Phase 9: print the recordings of one state of the scene as a table, or two states side by side.

Usage:
    python -B table.py <label>               one row per recording of profiles/2026-11-13_M7/<label>/
    python -B table.py <before> <after>      frame mean, 95th percentile, graphics-card mean and video memory, before and after

Reads the *.analysis.json files that tools/analyze_profile_csv.py wrote. First walks are left out.
"""

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, "/").rsplit("/review/", 1)[0]
ORDER = ["exterior_path", "triplex_path", "penthouse_path_indoors", "penthouse_path_roof_deck", "hold_S1", "hold_S2", "hold_S6",
         "hold_D5", "hold_D2"]
NAMES = {"exterior_path": "Exterior path, 60 s", "triplex_path": "Triplex path, 30 s", "penthouse_path_indoors": "Penthouse path indoors, 20 s",
         "penthouse_path_roof_deck": "Penthouse path roof deck, 10 s", "hold_S1": "Hold S1", "hold_S2": "Hold S2", "hold_S6": "Hold S6",
         "hold_D5": "Hold D5", "hold_D2": "Hold D2"}


def video_memory(stats):
    """Peak of the video memory in use, in megabytes (the budget column is the card's limit, not the use)."""
    used = stats.get("GPUMem/LocalUsedMB")
    return used.get("max") if used else None


def load(label):
    out = {}
    for path in sorted(glob.glob("%s/profiles/2026-11-13_M7/%s/*.analysis.json" % (ROOT, label))):
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        for job in data["jobs"]:
            name = job["name"]
            if name.endswith("_first_walk") or "stats" not in job:
                continue
            key = name.split("_", 1)[1]
            stats = job["stats"]
            out[key] = {"frames": job["frames"], "mean": stats["FrameTime"]["mean"], "p95": stats["FrameTime"]["p95"],
                        "worst": stats["FrameTime"]["max"], "over33": job["frames_over_33_333ms"], "over16": job["frames_over_16_667ms"],
                        "gpu": stats["GPUTime"]["mean"], "game": stats["GameThreadTime"]["mean"],
                        "render": stats["RenderThreadTime"]["mean"], "vram": job.get("vram_peak_mb") or video_memory(stats),
                        "front": job.get("foreground_fraction")}
    return out


def main(argv):
    if len(argv) == 2:
        rows = load(argv[1])
        print("| Recording | Frame mean (ms) | 95th percentile | Worst | Frames over 33.3 ms | Frames over 16.67 ms | Graphics card mean | "
              "Game thread mean | Render thread mean | Video memory peak (MB) | In front |")
        print("|---|---|---|---|---|---|---|---|---|---|---|")
        for key in ORDER:
            if key in rows:
                r = rows[key]
                print("| %s | %.2f | %.2f | %.2f | %d of %s | %d | %.2f | %.2f | %.2f | %s | %.2f |" % (
                    NAMES[key], r["mean"], r["p95"], r["worst"], r["over33"], format(r["frames"], ","), r["over16"], r["gpu"], r["game"],
                    r["render"], format(int(round(r["vram"])), ",") if r["vram"] else "n/a", r["front"] or 0.0))
        return 0
    before, after = load(argv[1]), load(argv[2])
    print("| Recording | Frame mean (ms) | 95th percentile | Worst | Graphics card mean | Video memory peak (MB) |")
    print("|---|---|---|---|---|---|")
    for key in ORDER:
        if key in before and key in after:
            b, a = before[key], after[key]
            print("| %s | %.2f to %.2f | %.2f to %.2f | %.2f to %.2f | %.2f to %.2f | %s to %s |" % (
                NAMES[key], b["mean"], a["mean"], b["p95"], a["p95"], b["worst"], a["worst"], b["gpu"], a["gpu"],
                format(int(round(b["vram"])), ",") if b["vram"] else "n/a", format(int(round(a["vram"])), ",") if a["vram"] else "n/a"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

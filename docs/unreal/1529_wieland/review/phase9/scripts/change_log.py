"""Phase 9: write the change log, profiles/2026-11-13_M7/change_log.csv.

Usage:
    python -B change_log.py

One block of rows per change: the change, where it is stored, and for every recording the frame time, the
graphics-card time and the video memory before and after it. The figures come from the recordings of the state
before the change and the state after it (the *.analysis.json files of the two folders). Add a change to CHANGES
and run again; the file is rewritten whole.
"""

import csv
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import table  # noqa: E402

CHANGES = [
    {"number": 1, "step": "9.7", "before": "B0", "after": "C1",
     "change": "MegaLights switched on for the fixture lights (284 lit lamps, all casting shadows): the lamps are lit and "
               "shadowed together by ray tracing instead of one shadow map each",
     "stored": "post-process volume LGT_Exposure_Outdoors (unbound) in /Game/Wieland1529/Lighting/L_Light_SummerAfternoon, "
               "setting MegaLights = on; the level was saved by name",
     "gives_up": "less accurate shadow edges of the lamps (listed trade); same-moment picture check D2 -0.3 % mean, no block "
                 "off by a stop"},
    {"number": 2, "step": "9.4", "before": "C1", "after": "C2",
     "change": "Lumen indoors: rays that carry indirect light are lit from Lumen's surface cache; only reflections are "
               "still lit in full at the point the ray hits (ray lighting mode 'hit lighting for reflections')",
     "stored": "post-process volumes LGT_Exposure_Interior_4th and LGT_Exposure_Interior_LowerTo3rd in "
               "/Game/Wieland1529/Lighting/L_Light_SummerAfternoon, setting Lumen ray lighting mode; the level was saved by name",
     "gives_up": "less detailed indirect light indoors (listed trade); same-moment picture check D1 to D5: mean brightness "
                 "moves by at most 0.6 points. Condition of the 'after' recording: somebody was working in a web browser, "
                 "the editor was not the window in front (in front for 49 % of the exterior path only); the three long "
                 "frames of the exterior path after are game-thread stalls at 45 to 50 s with the graphics card steady"},
]

FIELDS = ["change", "plan_step", "what", "where_stored", "what_it_gives_up", "state_before", "state_after", "recording",
          "frame_mean_ms_before", "frame_mean_ms_after", "frame_p95_ms_before", "frame_p95_ms_after",
          "frame_worst_ms_before", "frame_worst_ms_after", "frames_over_33_3ms_before", "frames_over_33_3ms_after",
          "graphics_card_mean_ms_before", "graphics_card_mean_ms_after", "render_thread_mean_ms_before",
          "render_thread_mean_ms_after", "video_memory_peak_mb_before", "video_memory_peak_mb_after"]


def main():
    out = table.ROOT + "/profiles/2026-11-13_M7/change_log.csv"
    rows = []
    for change in CHANGES:
        before, after = table.load(change["before"]), table.load(change["after"])
        for key in table.ORDER:
            if key not in before or key not in after:
                continue
            b, a = before[key], after[key]
            rows.append([change["number"], change["step"], change["change"], change["stored"], change["gives_up"],
                         change["before"], change["after"], table.NAMES[key],
                         "%.2f" % b["mean"], "%.2f" % a["mean"], "%.2f" % b["p95"], "%.2f" % a["p95"],
                         "%.2f" % b["worst"], "%.2f" % a["worst"], b["over33"], a["over33"],
                         "%.2f" % b["gpu"], "%.2f" % a["gpu"], "%.2f" % b["render"], "%.2f" % a["render"],
                         "%.0f" % b["vram"] if b["vram"] else "", "%.0f" % a["vram"] if a["vram"] else ""])
    with open(out, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(FIELDS)
        writer.writerows(rows)
    print("written", out, len(rows), "rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Phase 9: print the budget rows of one or more gpu_passes summaries on one line per station.

Usage: python -B rows.py <label> [<label> ...]
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, "/")
ROOT = HERE.rsplit("/review/", 1)[0]
KEYS = ["geometry", "shadows", "lumen_scene", "gi", "reflections", "direct", "sky", "translucent", "wind", "upscaling", "post", "other"]
SHORT = ["geo", "shad", "lscn", "gi", "refl", "dir", "sky", "trans", "wind", "ups", "post", "other"]

print("%-22s %-3s %s  gpu   frame" % ("label", "st", " ".join("%5s" % name for name in SHORT)))
for label in sys.argv[1:]:
    with open("%s/profiles/2026-11-13_M7/%s/gpu_passes_%s.summary.json" % (ROOT, label, label), encoding="utf-8") as handle:
        data = json.load(handle)
    for result in data["results"]:
        rows = result["rows_ms"]
        print("%-22s %-3s %s %5.2f %5.2f  (sp %s)" % (label, result["station"], " ".join("%5.2f" % rows[key] for key in KEYS),
                                                 result["frame_gpu_ms"], result["frame_ms"], result["screen_percentage"]))

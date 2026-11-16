"""Phase 9: the per-pass budget check of one state, with the two full-picture passes scaled to 2560 by 1440.

Usage:
    python -B pass_budget.py <label>

Reads profiles/2026-11-13_M7/<label>/gpu_passes_<label>.summary.json. The editor's viewport finishes a picture of
2.44 million pixels, the plan's tier one of 3.69 million, so upscaling and post-processing are multiplied by 1.51
("scaled"); every other pass works on the computed pixels, which are the same number. Prints, as a table for the
journal, each pass against its budget at each station, and under it the passes over budget, by how much, and the
named passes under budget that offset them.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, "/")
ROOT = HERE.rsplit("/review/", 1)[0]
SCALED = {"upscaling": 1.51, "post": 1.51}
ORDER = ["S1", "S2", "S6", "D2", "D5"]
SHORT = {"geometry": "geometry", "shadows": "shadows", "lumen_scene": "Lumen scene", "gi": "Lumen global illumination",
         "reflections": "reflections", "direct": "direct light", "sky": "sky", "translucent": "translucent surfaces",
         "wind": "foliage wind", "upscaling": "upscaling", "post": "post-processing"}


def main(argv):
    label = argv[1]
    with open("%s/profiles/2026-11-13_M7/%s/gpu_passes_%s.summary.json" % (ROOT, label, label), encoding="utf-8") as handle:
        data = json.load(handle)
    rows = [row for row in data["budget_rows"] if row["budget_ms"] is not None]
    results = {item["station"]: item for item in data["results"]}
    stations = [name for name in ORDER if name in results]
    value = {name: {row["key"]: results[name]["rows_ms"][row["key"]] * SCALED.get(row["key"], 1.0) for row in rows} for name in stations}
    print("| Pass | Budget (ms) | " + " | ".join(stations) + " |")
    print("|---|---|" + "---|" * len(stations))
    for row in rows:
        cells = []
        for name in stations:
            figure = value[name][row["key"]]
            cells.append(("**%.2f**" if figure > row["budget_ms"] else "%.2f") % figure)
        print("| %s%s | %.1f | %s |" % (row["label"], " (scaled)" if row["key"] in SCALED else "", row["budget_ms"], " | ".join(cells)))
    total = sum(row["budget_ms"] for row in rows)
    print("| Sum of the passes | %.1f | %s |" % (total, " | ".join("%.2f" % sum(value[name].values()) for name in stations)))
    extra = {name: sum(results[name]["rows_ms"][key] * (factor - 1.0) for key, factor in SCALED.items()) for name in stations}
    keys = [key for key in results[stations[0]] if "gpu" in key.lower() or "frame" in key.lower()]
    print()
    print("other keys per station:", keys)
    for name in stations:
        print(name, {key: results[name][key] for key in keys}, "added by scaling: %.2f ms" % extra[name])
    print()
    for name in stations:
        over = [(row, value[name][row["key"]] - row["budget_ms"]) for row in rows if value[name][row["key"]] > row["budget_ms"]]
        under = [(row, row["budget_ms"] - value[name][row["key"]]) for row in rows if value[name][row["key"]] <= row["budget_ms"]]
        print("- %s: over budget: %s (together %.2f ms); offset by %s (together %.2f ms under)." % (
            name, ", ".join("%s by %.2f" % (SHORT[row["key"]], amount) for row, amount in over) or "none",
            sum(amount for _, amount in over),
            ", ".join("%s %.2f" % (SHORT[row["key"]], amount) for row, amount in sorted(under, key=lambda item: -item[1]) if amount >= 0.1),
            sum(amount for _, amount in under)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

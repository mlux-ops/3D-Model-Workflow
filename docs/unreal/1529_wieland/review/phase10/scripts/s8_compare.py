"""Phase 10, station S8: the real-time plan picture against the path-traced plan picture, by the same measure
as the twelve views (review/phase8/scripts/compare_tiers.py, unchanged).

    python -B review/phase10/scripts/s8_compare.py

Run from the plan folder. Reads review/phase10/realtime/S8/S8_pathtraced.0000.png and S8_realtime.0000.png
(both 2,160 by 2,160) and writes review/phase10/compare/S8/compare.json and compare.csv. The three-panel sheet
that compare_tiers.py draws is made for 16:9 pictures and would squeeze the square plan, so it goes to
review/phase10/scratch/ and is not used; the S8 sheet of station_sheets.py shows the panels square.

The path-traced plan picture was made with r.RayTracing.Nanite.Mode 0: the Path Tracer traced each mesh's
simplified fallback copy. The twelve ground-truth pictures of Phase 12 were made with mode 2. The record says so.
"""
import csv
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, "review/phase8/scripts")
import compare_tiers  # noqa: E402

FOLDER = "review/phase10/realtime/S8"
OUT = "review/phase10/compare/S8"
SCRATCH = "review/phase10/scratch/S8_compare"

result = compare_tiers.compare("S8", FOLDER, FOLDER, SCRATCH, "")
result.pop("sheet", None)
result["path_traced_with_nanite_ray_tracing_mode"] = 0
result["note"] = ("path-traced picture traced the meshes' fallback copies (mode 0); the twelve views' ground truth "
                  "of Phase 12 used mode 2")
os.makedirs(OUT, exist_ok=True)
with open(OUT + "/compare.json", "w", encoding="utf-8") as handle:
    json.dump([result], handle, indent=1)
with open(OUT + "/compare.csv", "w", encoding="utf-8", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["view", "mean_difference_percent", "mean_within_10_percent", "pixels_used_percent",
                     "blocks_off_by_over_one_stop_percent", "largest_region_percent", "regions_over_2_percent",
                     "passes", "failing_regions"])
    if "mean_difference_percent" in result:
        writer.writerow([result["view"], result["mean_difference_percent"], result["mean_within_10_percent"],
                         result["pixels_used_percent"], result["blocks_off_by_over_one_stop_percent"],
                         result["largest_region_percent"], len(result["regions_over_2_percent"]), result["passes"],
                         "; ".join("%s %s %.1f%% of frame %+.2f stops" % (
                             f["where"], f["real_time_is"], f["share_of_frame_percent"], f["mean_stops"])
                             for f in result["regions_over_2_percent"])])
    else:
        writer.writerow([result["view"], "", "", "", "", "", "", "", json.dumps(result)])
print(json.dumps(result))

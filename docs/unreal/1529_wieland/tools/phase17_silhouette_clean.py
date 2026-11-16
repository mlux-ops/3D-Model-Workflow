"""Phase 17: the silhouette check of J19 carried over to the clean built tower tops (J23, J23b).

Usage:
    python -B -P phase17_silhouette_clean.py <tops csv from phase17_silhouette.py> [...] <out csv>

The camera of each photograph was solved in J19 from landmarks that do not depend on tower tops (the horizontal
centres of 875 and 900 N Michigan and the far shore's water line), so it stands. Each tower's model elevation is moved
from the J19 model top to the clean model's top (highest vertex, masts included; towers_record.jsonl of
meshes_towers_clean): el_new = atan(tan(el_old) + (top_clean - top_old) / distance). The curvature and refraction
term is the same for both tops and cancels. Error = photograph minus model, as in J19.
"""

import csv
import json
import math
import os
import sys

RECORDS = "E:/Wieland1529_site_data/phase17/meshes_towers_clean/towers_record.jsonl"
# Towers whose top is the photograph's own sky line (checked on the J19 overlays); the others stand behind nearer
# buildings that are not modelled, so their photograph edge is not their top.
SKYLINE = {"nab2023": {"824823", "821343", "859995", "835763"},
           "nab2014": {"821343", "821651", "889662", "824823"}}


def main(argv):
    tops_files, out = argv[1:-1], argv[-1]
    clean = {}
    for line in open(RECORDS, encoding="utf-8"):
        r = json.loads(line)
        clean[str(r["id"])] = float(r["top_incl_masts_m"])
    rows = []
    for path in tops_files:
        photo = os.path.basename(path).split("_tops")[0]
        for r in csv.DictReader(open(path, encoding="utf-8")):
            cid = r["county_id"]
            if cid not in clean:
                continue
            d = float(r["distance_m"])
            old_top, new_top = float(r["model_top_m"]), clean[cid]
            el_old = float(r["model_el_deg"])
            el_new = math.degrees(math.atan(math.tan(math.radians(el_old)) + (new_top - old_top) / d))
            err = float(r["photo_el_deg"]) - el_new
            rows.append({"photo": photo, "county_id": cid, "name": r["name"], "distance_m": d,
                         "model_top_j19_m": old_top, "model_top_clean_m": round(new_top, 2),
                         "photo_el_deg": float(r["photo_el_deg"]), "model_el_clean_deg": round(el_new, 4),
                         "el_err_clean_deg": round(err, 4),
                         "el_err_clean_m_at_distance": round(math.tan(math.radians(abs(err))) * d * (1 if err >= 0 else -1), 2),
                         "el_err_j19_deg": float(r["el_err_deg"]),
                         "top_is_photo_skyline": cid in SKYLINE.get(photo, set())})
    with open(out, "w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for photo in sorted({r["photo"] for r in rows}):
        sk = [r for r in rows if r["photo"] == photo and r["top_is_photo_skyline"]]
        errs = sorted(abs(r["el_err_clean_deg"]) for r in sk)
        med = errs[len(errs) // 2] if len(errs) % 2 else (errs[len(errs) // 2 - 1] + errs[len(errs) // 2]) / 2
        print(json.dumps({"photo": photo, "skyline_towers": [(r["name"], r["el_err_clean_deg"], r["el_err_clean_m_at_distance"]) for r in sk],
                          "median_abs_deg": round(med, 3), "worst_abs_deg": round(errs[-1], 3)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

"""Phase 9, step 9.9: render named views in real time in one state of the scene and compare them with the
Phase 12 ground truth.

Usage:
    python -B rt_check.py <tag> <views, comma separated, or "all"> [<console variables as JSON>]

Writes the pictures to review/phase9/realtime/<tag>/ and the sheets and numbers to review/phase9/compare/<tag>/
(compare.csv and compare.json), with review/phase8/scripts/compare_tiers.py unchanged, so that the numbers
compare with review/phase12/compare/compare.csv.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, "/")
ROOT = HERE.rsplit("/review/", 1)[0]
ALL = ["S1", "S2", "S3", "S4", "S5", "S6", "S9", "D1", "D2", "D3", "D4", "D5"]


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    tag = argv[1]
    views = ALL if argv[2] == "all" else argv[2].split(",")
    cvars = json.loads(argv[3]) if len(argv) > 3 and argv[3] else {}
    base = ROOT + "/review/phase9/realtime"
    os.makedirs(base, exist_ok=True)
    with open(base + "/job.json", "w", encoding="utf-8") as handle:
        json.dump({"tag": tag, "views": views, "settle": 25, "warm_up_frames": 64, "cvars": cvars}, handle)
    code = subprocess.call([sys.executable, "-B", ROOT + "/tools/ue_call.py", "py", HERE + "/rt_views.py", str(120 + 90 * len(views))])
    if code:
        return code
    out = "%s/review/phase9/compare/%s" % (ROOT, tag)
    os.makedirs(out, exist_ok=True)
    code = subprocess.call([sys.executable, "-B", ROOT + "/review/phase8/scripts/compare_tiers.py",
                            ROOT + "/review/phase12/ground_truth", "%s/%s" % (base, tag), out])
    with open(out + "/compare.csv", encoding="utf-8") as handle:
        print(handle.read())
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))

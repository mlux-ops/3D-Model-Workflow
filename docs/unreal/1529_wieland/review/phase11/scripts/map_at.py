"""Phase 11: what the floor map holds at given points.  python -B map_at.py <floor> x,y [x,y ...]"""
import json
import sys

data = json.load(open("review/phase11/paths/map_%s.json" % sys.argv[1]))
for pair in sys.argv[2:]:
    x, y = [float(v) for v in pair.split(",")]
    i, j = int((x - data["x0"]) / data["cell"]), int((y - data["y0"]) / data["cell"])
    block, height = data["cells"][i][j]
    print(pair, "blocked by: %s" % data["labels"][block] if block >= 0 else "free", "surface:", height)

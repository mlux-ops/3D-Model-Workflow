"""Phase 11: print part of a floor map as text.  python -B map_text.py <floor> <y_west> <y_east> [step]
North is up, east is right. '.' free at floor height, '^' free with the surface above or below the floor,
' ' free with no surface, a capital letter: blocked at eye height (first letter of what blocks: W wall,
D door, F furniture, C casework, R railing, S stairs or specialty, P plumbing, G generic model, other)."""
import json
import sys

floor, west, east = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
data = json.load(open("review/phase11/paths/map_%s.json" % floor))
labels = data["labels"]
j_hi, j_lo = int((west - data["y0"]) / data["cell"]), int((east - data["y0"]) / data["cell"])
print("       " + "".join(("%-10d" % (data["y0"] + j * data["cell"] + 5)) for j in range(j_hi, j_lo, -10)))
for i in range(data["nx"]):
    x = data["x0"] + (i + 0.5) * data["cell"]
    text = ""
    for j in range(j_hi, j_lo, -1):
        block, height = data["cells"][i][j]
        if block >= 0:
            text += labels[block][0].upper()
        elif height is None:
            text += " "
        elif abs(height) > 6.0:
            text += "^"
        else:
            text += "."
    print("%6d %s" % (x, text))

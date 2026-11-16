"""Phase 11, step 11.2 preparation: one plan picture per floor of the north half, drawn from the bounding
boxes in interior_levels.csv, to lay out the camera moves. Read-only; writes review/phase11/scratch/plan_<floor>.png.

    python -B review/phase11/scripts/plan_sheets.py [route.json]
"""
import csv
import json
import sys

from PIL import Image, ImageDraw

FLOOR_Z = {"L": -152.4, "1": 203.2, "2": 528.3, "3": 853.4, "4": 1178.6, "R": 1524.0}
SCALE = 0.8  # pixels per cm
X0, X1, Y0, Y1 = -1560.0, -560.0, -3200.0, 150.0
COLOURS = {"Walls": (40, 40, 40), "Doors": (220, 30, 30), "Windows": (60, 160, 255), "Stairs": (40, 60, 220),
           "Landings": (120, 140, 255), "Railings": (0, 160, 60), "Casework": (190, 170, 130),
           "Furniture": (215, 200, 215), "Plumbing Fixtures": (150, 210, 210), "Generic Models": (0, 200, 120),
           "Specialty Equipment": (200, 120, 0), "Structural Columns": (120, 0, 120)}


def px(x, y):
    # north (-X) up, east (-Y) right
    return ((Y1 - y) * SCALE, (x - X0) * SCALE)


def main():
    route = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
    rows = list(csv.DictReader(open("interior_levels.csv", encoding="utf-8")))
    for floor, z in FLOOR_Z.items():
        lo, hi = z + 20.0, z + 200.0
        image = Image.new("RGB", (int((Y1 - Y0) * SCALE), int((X1 - X0) * SCALE)), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        for order in ("Furniture", "Casework", "Plumbing Fixtures", "Walls", "Structural Columns", "Windows",
                      "Stairs", "Landings", "Railings", "Generic Models", "Specialty Equipment", "Doors"):
            for row in rows:
                if row["category"] != order:
                    continue
                try:
                    b = [float(row[k]) for k in ("x_min", "y_min", "z_min", "x_max", "y_max", "z_max")]
                except ValueError:
                    continue
                if b[5] < lo or b[2] > hi or b[3] < X0 or b[0] > X1:
                    continue
                if order == "Walls" and b[5] < z + 100.0:
                    continue
                a, c = px(b[0], b[1]), px(b[3], b[4])
                box = [min(a[0], c[0]), min(a[1], c[1]), max(a[0], c[0]), max(a[1], c[1])]
                if order in ("Walls", "Structural Columns", "Casework", "Furniture", "Plumbing Fixtures"):
                    draw.rectangle(box, fill=COLOURS[order])
                else:
                    draw.rectangle(box, outline=COLOURS[order], width=2)
        for gx in range(-1500, -500, 100):
            p = px(gx, Y1)
            draw.text((2, p[1]), str(gx), fill=(150, 0, 0))
        for gy in range(-3200, 200, 100):
            p = px(X0, gy)
            draw.line([p[0], 0, p[0], 6], fill=(150, 0, 0))
            if gy % 200 == 0:
                draw.text((p[0] - 12, 8), str(gy), fill=(150, 0, 0))
        for name, points in route.items():
            pts = [px(p[0], p[1]) for p in points if abs(p[2] - (z + 160.0)) < 165.0]
            if len(pts) > 1:
                draw.line(pts, fill=(255, 0, 255), width=3)
            for p in pts:
                draw.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], outline=(255, 0, 255))
        image.save("review/phase11/scratch/plan_%s.png" % floor)
    return "done"


print(main())

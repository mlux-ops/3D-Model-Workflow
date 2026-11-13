"""Phase 13, step 13.1, off line and read-only: the county parcels between the lot of 1529 N. Wieland and
N. Wells Street, in the project's own coordinates.

Site coordinates: feet north and feet east of the lot's south-west corner, along the level's axes
(the level's north is -X, its east is -Y; `review/phase2/level_frame.json`).
Writes review/phase13/parcels_block.csv (one line per parcel) and review/phase13/parcels_block.png.
Usage: python -B review/phase13/scripts/parcels_block.py   (from the plan folder)
"""
import csv
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(PLAN, "tools"))
import wieland_geo  # noqa: E402

PARCELS = "E:/Wieland1529_site_data/county_parcels_2025.json"
FOOTPRINTS = "E:/Wieland1529_site_data/county_footprints_2022.json"
OUT = os.path.join(PLAN, "review", "phase13")
# The window looked at, in site feet: from 160 ft south to 260 ft north of the origin, from the front
# lot line to 420 ft east (Wells Street's far side).
WINDOW = (-160.0, 260.0, -20.0, 420.0)

frame = wieland_geo.LevelFrame.load(os.path.join(PLAN, "review", "phase2", "level_frame.json"))


def site(east_ft, north_ft):
    x, y = frame.level_from_map(east_ft, north_ft)
    return frame.site_from_level(x, y)   # (north ft, east ft)


def area(points):
    total = 0.0
    for (n0, e0), (n1, e1) in zip(points, points[1:] + points[:1]):
        total += e0 * n1 - e1 * n0
    return abs(total) / 2.0


def read(path, key):
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    out = []
    for feature in data["features"]:
        attributes = feature.get("attributes") or feature.get("properties") or {}
        geometry = feature["geometry"]
        rings = geometry.get("rings") or geometry.get("coordinates") or []
        if rings and isinstance(rings[0][0][0], list):
            rings = [ring for polygon in rings for ring in polygon]
        for ring in rings:
            points = [site(p[0], p[1]) for p in ring]
            if points[0] == points[-1]:
                points = points[:-1]
            out.append((attributes, points))
    return out


def inside(points):
    north = [p[0] for p in points]
    east = [p[1] for p in points]
    return max(north) > WINDOW[0] and min(north) < WINDOW[1] and max(east) > WINDOW[2] and min(east) < WINDOW[3]


parcels = [(a, p) for a, p in read(PARCELS, "Name") if inside(p)]
footprints = [(a, p) for a, p in read(FOOTPRINTS, None) if inside(p)]
rows = []
for attributes, points in parcels:
    north = [p[0] for p in points]
    east = [p[1] for p in points]
    rows.append({
        "pin": attributes.get("Name"),
        "class": attributes.get("AssessorBLDGclass"),
        "type": attributes.get("PARCELTYPE"),
        "south_ft": round(min(north), 2), "north_ft": round(max(north), 2),
        "west_ft": round(min(east), 2), "east_ft": round(max(east), 2),
        "along_north_ft": round(max(north) - min(north), 2), "along_east_ft": round(max(east) - min(east), 2),
        "area_sqft": round(area(points), 1),
        "corners": len(points),
        "outline_site_ft": " ".join("%.2f,%.2f" % p for p in points),
    })
rows.sort(key=lambda r: (round(r["west_ft"] / 20.0), r["south_ft"]))
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "parcels_block.csv"), "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

try:
    from PIL import Image, ImageDraw
    scale = 4.0   # pixels per foot
    width = int((WINDOW[3] - WINDOW[2]) * scale)
    height = int((WINDOW[1] - WINDOW[0]) * scale)

    def px(point):
        return ((point[1] - WINDOW[2]) * scale, (WINDOW[1] - point[0]) * scale)

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    for attributes, points in footprints:
        draw.polygon([px(p) for p in points], fill=(225, 225, 235), outline=(150, 150, 190))
    for attributes, points in parcels:
        draw.polygon([px(p) for p in points], outline=(200, 60, 40))
        north = sum(p[0] for p in points) / len(points)
        east = sum(p[1] for p in points) / len(points)
        draw.text(px((north + 3, east - 22)), str(attributes.get("Name"))[4:10], fill=(120, 30, 20))
    lot = [(0, 0), (49.5, 0), (49.5, 102.2), (0, 102.2)]
    draw.polygon([px(p) for p in lot], outline=(0, 120, 0), width=3)
    draw.text(px((30, 20)), "1529 N. Wieland (lot)", fill=(0, 100, 0))
    for east in range(0, 420, 50):
        draw.text(px((WINDOW[0] + 8, east)), "%d ft E" % east, fill=(90, 90, 90))
    for north in range(-150, 260, 50):
        draw.text(px((north, WINDOW[2] + 2)), "%d N" % north, fill=(90, 90, 90))
    image.save(os.path.join(OUT, "parcels_block.png"))
except ImportError:
    print("no image library: picture not written")

for row in rows:
    print("%s class %-5s S %7.1f N %7.1f W %7.1f E %7.1f  (%5.1f x %5.1f ft) %7.0f sqft" % (
        row["pin"], row["class"], row["south_ft"], row["north_ft"], row["west_ft"], row["east_ft"],
        row["along_north_ft"], row["along_east_ft"], row["area_sqft"]))
print(len(rows), "parcels,", len(footprints), "footprints in the window")

"""Phase 17, step 17.3: exterior wall, roof covering, age and use of the Zone 1 and 2 buildings from the
Cook County Assessor's public records (Cook County Open Data, no account):
  Parcel Universe (nj4t-kc8j): pin, class and the lot's point in State Plane feet (x_3435, y_3435).
  Single and Multi-Family Improvement Characteristics (x54s-btds): char_ext_wall, char_roof_cnst, char_yrblt,
  char_type_resd, char_use per pin (houses and flats of up to six units; condominiums and commercial have none).
Each parcel point is given to the county 2022 footprint that holds it, else to the nearest footprint within 15 ft.
Writes E:\\Wieland1529_site_data\\phase17\\assessor\\parcels.json, chars.json and zone12_assessor.csv.

Usage: python -B -P phase17_assessor.py
"""

import collections
import csv
import json
import os
import time
import urllib.parse
import urllib.request

from shapely.geometry import Point, Polygon
from shapely.strtree import STRtree

BASE = "E:/Wieland1529_site_data/phase17"
OUT = os.path.join(BASE, "assessor")
API = "https://datacatalog.cookcountyil.gov/resource/"
HEADERS = {"User-Agent": "Wieland1529 site model (Phase 17)"}
YEAR = "2025"


def get(dataset, params):
    url = API + dataset + ".json?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=120) as r:
                return json.load(r)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))


def main():
    os.makedirs(OUT, exist_ok=True)
    targets = list(csv.DictReader(open(os.path.join(BASE, "targets_zone12.csv"), encoding="utf-8")))
    boxes = [list(map(float, t["box"].split())) for t in targets]
    x0, y0 = min(b[0] for b in boxes) - 50, min(b[1] for b in boxes) - 50
    x1, y1 = max(b[2] for b in boxes) + 50, max(b[3] for b in boxes) + 50

    pfile = os.path.join(OUT, "parcels.json")
    if not os.path.exists(pfile):
        where = "year='%s' AND x_3435 between %f and %f AND y_3435 between %f and %f" % (YEAR, x0, x1, y0, y1)
        parcels = get("nj4t-kc8j", {"$select": "pin,class,x_3435,y_3435", "$where": where, "$limit": 50000})
        json.dump(parcels, open(pfile, "w"))
    parcels = json.load(open(pfile))

    cfile = os.path.join(OUT, "chars.json")
    if not os.path.exists(cfile):
        chars = []
        pins = sorted({p["pin"] for p in parcels})
        for i in range(0, len(pins), 80):
            group = ",".join("'%s'" % p for p in pins[i:i + 80])
            chars += get("x54s-btds", {"$select": "pin,card,class,char_yrblt,char_ext_wall,char_roof_cnst,char_type_resd,char_use,char_bldg_sf",
                                       "$where": "year='%s' AND pin in(%s)" % (YEAR, group), "$limit": 5000})
            time.sleep(1)
        json.dump(chars, open(cfile, "w"))
    chars = json.load(open(cfile))

    county = {str(f["attributes"]["OBJECTID"]): f for f in
              json.load(open(os.path.join(BASE, "county", "county_footprints_2022_viewbox.json")))["features"]}
    ids = [t["bldg_id"] for t in targets]
    polys = [Polygon(county[i]["geometry"]["rings"][0]).buffer(0) for i in ids]
    tree = STRtree(polys)

    by_pin = collections.defaultdict(list)
    for c in chars:
        by_pin[c["pin"]].append(c)
    per_bldg = collections.defaultdict(list)
    for p in parcels:
        pt = Point(float(p["x_3435"]), float(p["y_3435"]))
        hit = [int(j) for j in tree.query(pt, predicate="within")]
        if not hit:
            j = int(tree.nearest(pt))
            if polys[j].distance(pt) > 15.0:
                continue
            hit = [j]
        per_bldg[ids[hit[0]]].append(p)

    rows = []
    for bid, t in zip(ids, targets):
        ps = per_bldg.get(bid, [])
        cs = [c for p in ps for c in by_pin.get(p["pin"], [])]
        walls = collections.Counter(c.get("char_ext_wall", "") for c in cs if c.get("char_ext_wall"))
        roofs = collections.Counter(c.get("char_roof_cnst", "") for c in cs if c.get("char_roof_cnst"))
        years = sorted(int(float(c["char_yrblt"])) for c in cs if c.get("char_yrblt"))
        classes = collections.Counter(p["class"] for p in ps)
        rows.append({"bldg_id": bid, "zone": t["zone"], "parcels": len(ps), "pins": " ".join(sorted({p["pin"] for p in ps})),
                     "classes": " ".join("%s:%d" % kv for kv in classes.most_common()),
                     "ext_wall": walls.most_common(1)[0][0] if walls else "",
                     "ext_wall_votes": " ".join("%s:%d" % kv for kv in walls.most_common()),
                     "roof": roofs.most_common(1)[0][0] if roofs else "",
                     "year_built": years[len(years) // 2] if years else "",
                     "type": collections.Counter(c.get("char_type_resd", "") for c in cs).most_common(1)[0][0] if cs else "",
                     "use": collections.Counter(c.get("char_use", "") for c in cs).most_common(1)[0][0] if cs else ""})
    with open(os.path.join(OUT, "zone12_assessor.csv"), "w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(json.dumps({"parcels": len(parcels), "chars": len(chars), "buildings": len(rows),
                      "with_wall": sum(1 for r in rows if r["ext_wall"]),
                      "walls": collections.Counter(r["ext_wall"] for r in rows).most_common(),
                      "zone1_with_wall": sum(1 for r in rows if r["ext_wall"] and r["zone"] == "1")}))


if __name__ == "__main__":
    main()

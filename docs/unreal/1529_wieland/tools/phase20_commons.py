"""Phase 20: reference photographs from Wikimedia Commons for the work-list buildings.

Usage: python -B -P phase20_commons.py <worklist csv> <out folder>

For each skyline tower with a name: a text search of Commons files ("<name>" Chicago), up to 5 files. For each
skyline tower: geotagged files within 150 m of its centre, up to 5. For Zones 1 and 2: geotagged files within 400 m
of the lot centre, up to 120, shared by all of them (which building each shows is decided by looking).
Each file's licence, author and address come from its page data (imageinfo extmetadata). Kept: CC0, public domain,
CC BY and CC BY-SA files that are images; refused: anything marked non-free or "fair use", and any file whose title
or description mentions Google. Thumbnails 1,280 px wide are saved (never the originals); index in
<out folder>/commons_index.csv. Reference only: never a texture, never traced.
The public interface is used politely: one request at a time, a pause of 1 s, a project User-Agent with no contact
details.
"""

import csv
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wieland_geo as g  # noqa: E402

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "Wieland1529-scene-research/1.0 (reference photographs, low volume)"}
DATA = "E:/Wieland1529_site_data/phase17"
SITE_EN = (1174226.2, 1910663.1)  # D1 on the lot, State Plane ft (LevelFrame.map_from_level(-1300, -1560))
FREE = re.compile(r"^(cc0|public domain|pd|cc[- ]by(-sa)?[- ]?\d|cc by(-sa)? \d)", re.I)


def api(params):
    params = dict(params, format="json", formatversion="2")
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                data = json.loads(r.read().decode("utf-8"))
            time.sleep(1.0)
            return data
        except Exception:
            time.sleep(5.0 * (attempt + 1))
    return {}


def text_search(q, limit):
    d = api({"action": "query", "list": "search", "srsearch": q, "srnamespace": 6, "srlimit": limit})
    return [s["title"] for s in d.get("query", {}).get("search", [])]


def geo_search(lat, lon, radius, limit):
    d = api({"action": "query", "list": "geosearch", "gscoord": "%f|%f" % (lat, lon), "gsradius": radius,
             "gsnamespace": 6, "gslimit": limit})
    return [(s["title"], s.get("dist")) for s in d.get("query", {}).get("geosearch", [])]


def info(titles):
    out = {}
    for k in range(0, len(titles), 40):
        d = api({"action": "query", "titles": "|".join(titles[k:k + 40]), "prop": "imageinfo",
                 "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 1280})
        for p in d.get("query", {}).get("pages", []):
            ii = (p.get("imageinfo") or [{}])[0]
            out[p["title"]] = ii
    return out


def strip(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def accept(title, ii):
    if not ii or ii.get("mime") not in ("image/jpeg", "image/png"):
        return None
    md = ii.get("extmetadata", {})
    lic = strip(md.get("LicenseShortName", {}).get("value", ""))
    nonfree = strip(md.get("NonFree", {}).get("value", ""))
    desc = strip(md.get("ImageDescription", {}).get("value", ""))
    if nonfree.lower() in ("true", "1") or "fair use" in lic.lower() or not FREE.match(lic):
        return None
    if "google" in (title + " " + desc).lower():
        return None
    return {"licence": lic, "licence_url": strip(md.get("LicenseUrl", {}).get("value", "")),
            "author": strip(md.get("Artist", {}).get("value", ""))[:120],
            "date": strip(md.get("DateTimeOriginal", {}).get("value", ""))[:19],
            "description": desc[:200], "page_url": ii.get("descriptionurl", ""), "thumb_url": ii.get("thumburl", ""),
            "width": ii.get("width"), "height": ii.get("height")}


def safe(title):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", title.replace("File:", ""))[:120]


def main(argv):
    worklist, out = argv[1], argv[2]
    os.makedirs(out, exist_ok=True)
    rows = list(csv.DictReader(open(worklist, encoding="utf-8")))
    cents = {}
    for f in ("targets.csv", "targets_zone12.csv"):
        for r in csv.DictReader(open(os.path.join(DATA, f), encoding="utf-8")):
            cents[r["bldg_id"]] = (float(r["centroid_east_ft"]), float(r["centroid_north_ft"]))
    wanted = {}  # title -> {"buildings": set, "how": set, "dist": float}

    def add(title, bid, how, dist=None):
        w = wanted.setdefault(title, {"buildings": set(), "how": set(), "dist": None})
        w["buildings"].add(bid)
        w["how"].add(how)
        if dist is not None:
            w["dist"] = dist
    for r in rows:
        if r["group"] != "skyline":
            continue
        bid = r["county_id"]
        if r["name"]:
            for t in text_search('"%s" Chicago' % r["name"], 5):
                add(t, bid, "text search")
        if bid in cents:
            lat, lon = g.lat_lon_from_state_plane(*cents[bid])
            for t, dd in geo_search(lat, lon, 150, 5):
                add(t, bid, "geotagged within 150 m", dd)
    lat, lon = g.lat_lon_from_state_plane(*SITE_EN)
    for t, dd in geo_search(lat, lon, 400, 120):
        add(t, "zone12", "geotagged within 400 m of the lot", dd)
    meta = info(sorted(wanted))
    index = []
    for title, w in sorted(wanted.items()):
        a = accept(title, meta.get(title))
        if a is None or not a["thumb_url"]:
            continue
        sub = os.path.join(out, "zone12" if w["buildings"] == {"zone12"} else "skyline")
        os.makedirs(sub, exist_ok=True)
        path = os.path.join(sub, safe(title) + (".png" if title.lower().endswith(".png") else ".jpg"))
        if not os.path.exists(path):
            try:
                with urllib.request.urlopen(urllib.request.Request(a["thumb_url"], headers=UA), timeout=90) as r:
                    open(path, "wb").write(r.read())
                time.sleep(1.0)
            except Exception as exc:
                print("download failed", title, exc)
                continue
        index.append(dict(a, title=title, buildings=" ".join(sorted(w["buildings"])), how="; ".join(sorted(w["how"])),
                          camera_dist_m=w["dist"], file=path.replace(os.sep, "/"), bytes=os.path.getsize(path)))
    with open(os.path.join(out, "commons_index.csv"), "w", newline="", encoding="utf-8") as h:
        wr = csv.DictWriter(h, fieldnames=list(index[0].keys()), lineterminator="\n")
        wr.writeheader()
        wr.writerows(index)
    print(json.dumps({"candidates": len(wanted), "kept": len(index), "refused": len(wanted) - len(index),
                      "megabytes": round(sum(i["bytes"] for i in index) / 1e6, 1)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

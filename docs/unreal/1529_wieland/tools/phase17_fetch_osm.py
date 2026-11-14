"""Phase 17: fetch OpenStreetMap buildings and building parts (ways and relations, with geometry and tags) in
small boxes through the Overpass API, politely (one query at a time, a pause between queries, a named agent).

Usage:
    python -B -P phase17_fetch_osm.py <out folder> <south> <west> <north> <east> [step deg 0.01]

Writes one JSON per box (osm_<s>_<w>.json, skipped if present) and a .source.txt. Data (c) OpenStreetMap
contributors, available under the Open Database Licence (ODbL) 1.0.
"""

import datetime
import json
import os
import sys
import time
import urllib.parse
import urllib.request

URL = "https://overpass-api.de/api/interpreter"
UA = "Wieland1529-site-model/1.0 (private architectural visualisation, one query at a time)"
QUERY = """[out:json][timeout:120];
(
  way["building"]({s},{w},{n},{e});
  way["building:part"]({s},{w},{n},{e});
  relation["building"]({s},{w},{n},{e});
  relation["building:part"]({s},{w},{n},{e});
  way["man_made"~"mast|tower|antenna"]({s},{w},{n},{e});
  node["man_made"~"mast|tower|antenna"]({s},{w},{n},{e});
);
out tags geom;"""


def main(argv):
    folder = argv[1]
    s0, w0, n0, e0 = (float(v) for v in argv[2:6])
    step = float(argv[6]) if len(argv) > 6 else 0.01
    os.makedirs(folder, exist_ok=True)
    s = s0
    log = []
    while s < n0 - 1e-9:
        w = w0
        while w < e0 - 1e-9:
            n, e = min(s + step, n0), min(w + step, e0)
            path = os.path.join(folder, "osm_%.4f_%.4f.json" % (s, w))
            if not os.path.exists(path):
                q = QUERY.format(s=s, w=w, n=n, e=e)
                for attempt in range(5):
                    try:
                        req = urllib.request.Request(URL, data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": UA})
                        with urllib.request.urlopen(req, timeout=200) as r:
                            data = r.read()
                        json.loads(data)
                        break
                    except Exception as error:
                        print("retry", path, error)
                        time.sleep(30 * (attempt + 1))
                else:
                    raise RuntimeError("failed " + path)
                with open(path, "wb") as handle:
                    handle.write(data)
                log.append("%s box s=%.4f w=%.4f n=%.4f e=%.4f bytes=%d fetched=%s" % (
                    os.path.basename(path), s, w, n, e, len(data), datetime.datetime.now().astimezone().isoformat(timespec="seconds")))
                print(log[-1])
                time.sleep(5)
            w += step
        s += step
    with open(os.path.join(folder, "osm.source.txt"), "a", encoding="utf-8") as handle:
        handle.write("service: %s\nlicence: (c) OpenStreetMap contributors, ODbL 1.0, https://www.openstreetmap.org/copyright\nquery:\n%s\n" % (URL, QUERY))
        handle.write("\n".join(log) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

"""Phase 17: stream the point-cloud tiles that hold the visible towers (and the 300 m square), within a byte cap.

Usage:
    python -B -P phase17_pc_batch.py <phase17 data folder> <out folder> [cap GB 23]

Tiles are ranked by the summed visible height of their targets (viewshed, D1, D1S, D2); the tile with the
300 m square is always included. Streaming stops before the running total of compressed tile sizes would pass
the cap (the owner's 25 GB limit; already-streamed tiles count). For each tile, the boxes are every target's
padded outline box that touches the tile, plus "SITE300" (the 300 m square grown by 50 ft) on the site tile.
Output per tile: <out>/pc_<tile>.npz via phase17_las_stream.py; a ledger pc_ledger.csv with streamed bytes.
"""

import collections
import csv
import glob
import json
import math
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_CENTRE = (1174227.19, 1910645.18)
SITE_HALF = 492.125 + 50.0
SITE_TILE = "17259100"


def tile_of(e, n):
    return "%04d%04d" % ((math.floor(e / 2500) * 2500 - 1e6) / 100, (math.floor(n / 2500) * 2500 - 1e6) / 100)


def main(argv):
    base, out = argv[1], argv[2]
    cap = float(argv[3]) * 1e9 if len(argv) > 3 else 23e9
    os.makedirs(out, exist_ok=True)
    sizes = {}
    for f in glob.glob(os.path.join(base, "isgs_index", "part*_members.csv")):
        for r in csv.DictReader(open(f)):
            n = r["name"].split("/")[-1][:-4]
            if n:
                sizes[n] = (int(r["part"]), int(r["compressed_bytes"]))
    rows = list(csv.DictReader(open(os.path.join(base, "targets.csv"), encoding="utf-8")))
    boxes = collections.defaultdict(dict)
    weight = collections.defaultdict(float)
    for r in rows:
        b = [float(v) for v in r["box"].split()]
        tiles = {tile_of(e, n) for e in (b[0], b[2]) for n in (b[1], b[3])}
        for t in tiles:
            boxes[t][r["bldg_id"]] = b
            weight[t] += float(r["visible_height_m_bare"] or 0)
    s = [SITE_CENTRE[0] - SITE_HALF, SITE_CENTRE[1] - SITE_HALF, SITE_CENTRE[0] + SITE_HALF, SITE_CENTRE[1] + SITE_HALF]
    boxes[SITE_TILE]["SITE300"] = s
    weight[SITE_TILE] += 1e9
    order = sorted(boxes, key=lambda t: -weight[t])
    ledger_path = os.path.join(out, "pc_ledger.csv")
    done = {}
    if os.path.exists(ledger_path):
        for r in csv.DictReader(open(ledger_path)):
            done[r["tile"]] = int(r["streamed_bytes"])
    total = sum(done.values())
    # The Willis trial tile (streamed once for the test) counts against the cap.
    trial = os.path.join(out, "pc_17258975_willis.npz")
    if os.path.exists(trial) and "17258975_willis" not in done:
        done["17258975_willis"] = sizes["17258975"][1]
        total += sizes["17258975"][1]
        with open(ledger_path, "a", newline="") as handle:
            w = csv.writer(handle)
            if handle.tell() == 0:
                w.writerow(["tile", "part", "streamed_bytes", "stored_bytes", "boxes", "finished"])
            w.writerow(["17258975_willis", 5, sizes["17258975"][1], os.path.getsize(trial), 1, "trial"])
    for t in order:
        if t in done or t not in sizes:
            continue
        part, nbytes = sizes[t]
        if total + nbytes > cap:
            print("cap reached before", t, "total GB %.2f" % (total / 1e9), flush=True)
            break
        bpath = os.path.join(out, "boxes_%s.json" % t)
        with open(bpath, "w") as handle:
            json.dump(boxes[t], handle)
        npz = os.path.join(out, "pc_%s.npz" % t)
        started = time.time()
        res = subprocess.run([sys.executable, "-B", "-P", os.path.join(HERE, "phase17_las_stream.py"), str(part), t, bpath, npz],
                             capture_output=True, text=True)
        if res.returncode != 0 or not os.path.exists(npz):
            print("FAILED", t, res.stderr[-800:], flush=True)
            continue
        total += nbytes
        with open(ledger_path, "a", newline="") as handle:
            w = csv.writer(handle)
            if handle.tell() == 0:
                w.writerow(["tile", "part", "streamed_bytes", "stored_bytes", "boxes", "finished"])
            w.writerow([t, part, nbytes, os.path.getsize(npz), len(boxes[t]), time.strftime("%Y-%m-%d %H:%M:%S")])
        print(t, res.stdout.strip(), "total GB %.2f" % (total / 1e9), "%.0f s" % (time.time() - started), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

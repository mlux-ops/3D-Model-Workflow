"""Phase 20 round 2: build the sheet's landmarks that Phase 17 left out, from the laser scan.

Phase 17 built only buildings with at least three visible 6 ft cells from D1, D1S or D2 (leaf-off), so
landmarks hidden behind nearer towers were never built. This fetches the ISGS 1 ft surface model over each
county outline (plus 30 ft), exactly as phase17_targets.py does, then runs the Phase 17 clean-roof builder
(phase17_clean.build) on those ids, writing P17R_<id>.json into meshes_towers_clean and appending to
towers_record.jsonl.

Usage:  python -B phase20r2_add_towers.py <id> [<id> ...]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import phase17_fetch_rasters as fr  # noqa: E402

BASE = r'E:/Wieland1529_site_data/phase17'
OUT = BASE + '/meshes_towers_clean'


def fetch_dsm(bid, county):
    path = os.path.join(BASE, 'rasters', 'bldg1ft', '%s_dsm.npz' % bid)
    if os.path.exists(path):
        return path, 'present'
    rings = county[bid]['geometry']['rings']
    es = [p[0] for r in rings for p in r]
    ns = [p[1] for r in rings for p in r]
    box = [min(es) - 30, min(ns) - 30, max(es) + 30, max(ns) + 30]
    z, x0, y1, urls = fr.fetch(fr.SERVICES['dsm'], box, 1.0)
    np.savez_compressed(path, z=z, x0=x0, y1=y1, cell=1.0, url=urls[0])
    return path, 'fetched'


def main(ids):
    with open(os.path.join(BASE, 'county', 'county_footprints_2022_viewbox.json')) as handle:
        county = {str(f['attributes']['OBJECTID']): f for f in json.load(handle)['features']}
    for bid in ids:
        if bid not in county:
            print('not in the county footprints', bid)
            continue
        print(bid, *fetch_dsm(bid, county), flush=True)
    import phase17_clean
    return phase17_clean.main(['phase17_clean.py', BASE, OUT] + list(ids))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

"""Phase 20 round 2: narrow the round-2 Wikimedia Commons set before looking at it.

Zones 1 and 2: keep a file if it is geotagged within 250 m of the lot, or if its title or
description names a street or place next to the lot (Wells, Wieland, North Avenue, North Park,
Schiller, Burton, Old Town, Zanies, Up Down Cigar, Ale House) and it is not geotagged more than
700 m away. Towers and landmarks: keep every file, grouped by what it was gathered for.

Reads  E:/Wieland1529_site_data/phase20/round2/round2_index.csv
Writes review/phase20/round2/zone12_candidates.csv and review/phase20/round2/tower_groups.csv
(file lists only; the photographs stay outside the repository).
"""
import csv
import math
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = r'E:/Wieland1529_site_data/phase20/round2/round2_index.csv'
OUT = os.path.join(ROOT, 'review', 'phase20', 'round2')
LOT_LAT, LOT_LON = 41.9102490, -87.6353897   # 1529 N Wieland, tools/wieland_geo.py
NEAR_M = 250.0
KEYWORD_MAX_M = 700.0
KEYS = [r'\bwells (st|street)\b', r'\bwieland\b', r'north avenue(?! beach)', r'\bnorth ave\b(?! beach)',
        r'north park ave', r'\bschiller\b', r'\bburton\b', r'old town(?! school)', r'zanies',
        r'up down cigar', r'ale house', r'wells and north', r'north and wells']


def dist_m(lat, lon):
    return math.hypot((lat - LOT_LAT) * 111320.0,
                      (lon - LOT_LON) * 111320.0 * math.cos(math.radians(LOT_LAT)))


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = list(csv.DictReader(open(INDEX, encoding='utf-8')))
    zone, towers = [], []
    for r in rows:
        d = dist_m(float(r['lat']), float(r['lon'])) if r['lat'] and r['lon'] else None
        text = (r['title'] + ' ' + r['description']).lower()
        hits = [k for k in KEYS if re.search(k, text)]
        groups = [g.strip() for g in r['for'].split(';')]
        if 'zone12' in groups and ((d is not None and d <= NEAR_M) or (hits and (d is None or d <= KEYWORD_MAX_M))):
            zone.append(dict(r, distance_m='' if d is None else '%.0f' % d, matched=' '.join(hits)))
        for g in groups:
            if g != 'zone12':
                towers.append(dict(r, group=g, distance_m='' if d is None else '%.0f' % d))
    zone.sort(key=lambda r: (r['distance_m'] == '', float(r['distance_m'] or 0)))
    cols = ['distance_m', 'matched', 'title', 'licence', 'author', 'date', 'page_url', 'file']
    with open(os.path.join(OUT, 'zone12_candidates.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(zone)
    cols = ['group', 'title', 'licence', 'author', 'date', 'page_url', 'distance_m', 'file']
    with open(os.path.join(OUT, 'tower_groups.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(sorted(towers, key=lambda r: r['group']))
    near = sum(1 for r in zone if r['distance_m'] and float(r['distance_m']) <= NEAR_M)
    print('index rows', len(rows), 'zone12 candidates', len(zone), 'geotagged within 250 m', near,
          'tower rows', len(towers), 'tower groups', len(set(r['group'] for r in towers)))


if __name__ == '__main__':
    main()

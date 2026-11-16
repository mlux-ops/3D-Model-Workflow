"""Phase 20 round 2: four sheet landmarks that the 2022 survey surface does not hold.

Lake Point Tower, Park Tower, NEMA Chicago and the upper tower of the Palmolive Building stand in photographs
and in OpenStreetMap, but the ISGS 2022 surface model over their outlines reaches only 56 to 101 m (their roofs
are 172 to 273 m). With no measured height to keep, they are built as clean forms from their OpenStreetMap
outlines (building parts) and published heights, and recorded as assumptions:
  - Lake Point Tower: OSM part 150408224 (the three-lobed tower, height 191 m) and part 284814462 (roof
    structure, 197.5 m);
  - Park Tower: OSM part 686187393 (tower, 257 m) and its two low parts 686187396 (7 storeys) and
    1283005796 (8 storeys);
  - NEMA Chicago: OSM parts 1333503937 to 1333503946 (stepped, 24 to 81 storeys; the 81-storey part is 273 m;
    the others at 273 m x storeys / 81);
  - Palmolive Building: the scan keeps the base (county 821196, 80.9 m); above it the published tower (roof
    565 ft, 172.2 m) as two setbacks of the OSM outline 143756601 (inset to 70 % and 50 % of its size, the second
    from 130 m), and the Lindbergh beacon mast to 615 ft (187.5 m). The setback sizes are assumptions.
Each is written as P17R_osm<way id>.json in the Phase 17 mesh format (CleanMesh: level cm about a pivot, the
earth-curvature drop from D1 applied, wall/roof/mast material numbers), into meshes_towers_clean.

Usage:  python -B phase20r2_osm_towers.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
from shapely.geometry import Polygon  # noqa: E402
from shapely import affinity  # noqa: E402

import wieland_geo as g  # noqa: E402
import phase17_towers as T  # noqa: E402
from phase17_clean import CleanMesh  # noqa: E402

OVERPASS = r'E:/Wieland1529_site_data/phase20/round2/osm/overpass.json'
OUT = r'E:/Wieland1529_site_data/phase17/meshes_towers_clean'
DTM = r'E:/Wieland1529_site_data/phase17/rasters/view6ft_dtm.npz'
FT = 0.3048

# name -> list of (way id, top m, base m, material) ; mast entries have their own size.
BUILDINGS = {
    'Lake Point Tower': [(150408224, 191.0, None), (284814462, 197.5, 191.0)],
    'Park Tower': [(686187393, 257.0, None), (686187396, 7 * 3.6, None), (1283005796, 8 * 3.6, None)],
    'NEMA Chicago': [(1333503937, 273.0 * 24 / 81, None), (1333503938, 273.0 * 33 / 81, None),
                     (1333503939, 273.0 * 42 / 81, None), (1333503940, 273.0 * 55 / 81, None),
                     (1333503941, 273.0 * 62 / 81, None), (1333503942, 273.0 * 69 / 81, None),
                     (1333503943, 273.0 * 77 / 81, None), (1333503944, 273.0 * 74 / 81, None),
                     (1333503945, 273.0, None), (1333503946, 273.0 * 66 / 81, None)],
    'Palmolive Building': 'palmolive',
}
FILE_ID = {'Lake Point Tower': 150408224, 'Park Tower': 686187393, 'NEMA Chicago': 1333503945,
           'Palmolive Building': 143756601}


def load_ways():
    data = json.load(open(OVERPASS, encoding='utf-8'))
    ways = {}
    for el in data['elements']:
        if el['type'] == 'way' and el.get('geometry'):
            pts = [g.state_plane_from_lat_lon(p['lat'], p['lon']) for p in el['geometry']]
            poly = Polygon(pts).buffer(0)
            if poly.geom_type != 'Polygon':
                poly = max(poly.geoms, key=lambda q: q.area)
            ways[el['id']] = poly
    return ways


def ground_ft(dtm, e, n):
    c = int((e - float(dtm['x0'])) / 6.0)
    r = int((float(dtm['y1']) - n) / 6.0)
    z = dtm['z'][max(r - 3, 0):r + 4, max(c - 3, 0):c + 4]
    return float(np.nanmedian(z))


def main():
    frame = g.LevelFrame.load(T.FRAME)
    dtm = np.load(DTM)
    ways = load_ways()
    d1e, d1n = frame.map_from_level(T.D1[0], T.D1[1])

    def drop(e, n):
        d = math.hypot(e - d1e, n - d1n) * FT
        return d * d / (2.0 * T.R_EARTH_M) * (1.0 - T.K_REFRACTION)

    records = []
    for name, parts in BUILDINGS.items():
        main_way = ways[FILE_ID[name]]
        c = main_way.centroid
        gft = ground_ft(dtm, c.x, c.y)
        mesh = CleanMesh(frame, (c.x, c.y, gft), drop)
        top_m = 0.0
        if parts == 'palmolive':
            base_top = 80.9                      # the scan's base roof, county 821196
            roof = 565.0 * FT                    # published roof 172.2 m
            mast = 615.0 * FT                    # Lindbergh beacon mast top 187.5 m
            tiers = [(0.70, base_top - 1.0, 130.0), (0.50, 129.0, roof)]
            for scale, z0, z1 in tiers:
                shape = affinity.scale(main_way, xfact=scale, yfact=scale, origin='centroid')
                mesh.walls(shape, gft + z0 / FT, gft + z1 / FT, 0)
                mesh.cap(shape, gft + z1 / FT, 1)
            half = 1.0 / FT                      # mast 2 m square
            m = Polygon([(c.x - half, c.y - half), (c.x + half, c.y - half), (c.x + half, c.y + half), (c.x - half, c.y + half)])
            mesh.walls(m, gft + roof / FT - 1.0, gft + mast / FT, 2)
            mesh.cap(m, gft + mast / FT, 2)
            top_m = mast
        else:
            for way_id, top, base in parts:
                shape = ways[way_id]
                z0 = gft - 1.0 / FT if base is None else gft + (base - 0.5) / FT
                mesh.walls(shape, z0, gft + top / FT, 0)
                mesh.cap(shape, gft + top / FT, 1)
                top_m = max(top_m, top)
        dist = math.hypot(c.x - d1e, c.y - d1n) * FT
        file_name = 'P17R_osm%d' % FILE_ID[name]
        data = {'name': file_name, 'kind': 'building', 'zone': 4,
                'pivot': [round(v, 2) for v in mesh.pivot], 'vertices': mesh.v, 'triangles': mesh.t,
                'tri_mat': mesh.m, 'uv0_m': mesh.uv}
        with open(os.path.join(OUT, file_name + '.json'), 'w', encoding='utf-8') as handle:
            json.dump(data, handle)
        rec = {'id': 'osm%d' % FILE_ID[name], 'name': file_name, 'landmark': name, 'distance_m': round(dist, 1),
               'ground_ft': round(gft, 3), 'form': 'OpenStreetMap outline, published height (assumption)',
               'roof_top_m': round(top_m if parts != 'palmolive' else 565.0 * FT, 2),
               'top_incl_masts_m': round(top_m, 2), 'curvature_drop_m': round(drop(c.x, c.y), 3),
               'triangles': len(mesh.t), 'height_source': 'published / OpenStreetMap (not in the 2022 survey surface)'}
        records.append(rec)
        print(file_name, name, 'ground %.1f ft' % gft, 'top %.1f m' % top_m, 'tris', len(mesh.t), 'dist %.0f m' % dist)
    with open(os.path.join(OUT, 'osm_assumption_record.jsonl'), 'w', encoding='utf-8') as handle:
        for rec in records:
            handle.write(json.dumps(rec) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())

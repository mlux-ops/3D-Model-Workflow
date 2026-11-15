"""Prepare measured coverage for the owner's street-bounded nearby detail extension.

Reuses cached measurements and fetches only one bounding DSM for missing buildings.
No facade layout is inferred by this step.
"""
import csv
import json
import math
import os
from pathlib import Path

import numpy as np

import phase17_fetch_rasters as rasters

DOCS=Path(__file__).resolve().parent.parent
BASE=Path('E:/Wieland1529_site_data/phase17')
WORK=Path('E:/Wieland1529_site_data/phase20/nearby_detail')


def main():
    WORK.mkdir(parents=True,exist_ok=True)
    rows=list(csv.DictReader((DOCS/'review/phase20/nearby_detail/building_scope.csv').open(encoding='utf-8')))
    county={str(f['attributes']['OBJECTID']):f for f in json.loads((BASE/'county/county_footprints_2022_viewbox.json').read_text(encoding='utf-8'))['features']}
    missing=[r['county_id'] for r in rows if not (BASE/'rasters/bldg1ft'/(r['county_id']+'_dsm.npz')).exists()]
    outlines=[p for bid in missing for ring in county[bid]['geometry']['rings'] for p in ring]
    box=[min(p[0] for p in outlines)-40,min(p[1] for p in outlines)-40,
         max(p[0] for p in outlines)+40,max(p[1] for p in outlines)+40]
    source=WORK/'scope1ft_dsm.npz'
    if not source.exists():
        print('Fetching missing-coverage DSM',len(missing),'buildings; box',box,flush=True)
        result=rasters.main(['phase17_fetch_rasters',str(WORK),'scope1ft',*[str(v) for v in box],'1','dsm'])
        if result:raise RuntimeError('DSM fetch failed')
    data=np.load(source)
    z=data['z'];x0=float(data['x0']);y1=float(data['y1'])
    for bid in missing:
        pts=[p for ring in county[bid]['geometry']['rings'] for p in ring]
        c0=max(0,math.floor(min(p[0] for p in pts)-30-x0))
        c1=min(z.shape[1],math.ceil(max(p[0] for p in pts)+30-x0))
        r0=max(0,math.floor(y1-max(p[1] for p in pts)-30))
        r1=min(z.shape[0],math.ceil(y1-min(p[1] for p in pts)+30))
        if c1<=c0 or r1<=r0:raise RuntimeError('Empty DSM crop '+bid)
        np.savez_compressed(BASE/'rasters/bldg1ft'/(bid+'_dsm.npz'),z=z[r0:r1,c0:c1],x0=x0+c0,y1=y1-r0,cell=1.0)
    targets=[]
    for r in rows:
        if r['earlier_detail_available']=='True':continue
        bid=r['county_id'];a=county[bid]['attributes']
        targets.append({'bldg_id':bid,'name':'','ground_z_ft':a.get('Ground_Z',''),
                        'centroid_east_ft':r['centroid_east_ft'],'centroid_north_ft':r['centroid_north_ft'],
                        'zone':2,'band':r['band']})
    with (WORK/'targets.csv').open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(targets[0]));writer.writeheader();writer.writerows(targets)
    (WORK/'zones.json').write_text(json.dumps({r['bldg_id']:2 for r in targets}),encoding='utf-8')
    print(json.dumps({'targets':len(targets),'new_dsm_crops':len(missing),'source':str(source),'source_bytes':source.stat().st_size}),flush=True)


if __name__=='__main__':main()

"""Build only clean measured forms for the nearby-detail extension, preserving all prior meshes."""
import csv
import json
import os
from pathlib import Path

WORK=Path('E:/Wieland1529_site_data/phase20/nearby_detail')
BASE=Path('E:/Wieland1529_site_data/phase17')
OUT=WORK/'meshes_clean'
os.environ['P17_ZONES']=str(WORK/'zones.json')
os.environ['P17_PREFIX']='ND'

import phase17_clean as clean
import phase17_towers as towers
import wieland_geo as geo


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    frame=geo.LevelFrame.load(towers.FRAME)
    county={str(f['attributes']['OBJECTID']):f for f in json.loads((BASE/'county/county_footprints_2022_viewbox.json').read_text(encoding='utf-8'))['features']}
    targets=list(csv.DictReader((WORK/'targets.csv').open(encoding='utf-8')))
    towers.ZONES.update(json.loads((WORK/'zones.json').read_text(encoding='utf-8')))
    dtm=towers.load(str(BASE/'rasters/view6ft_dtm.npz'))
    failed=[];made=0;reused=0;kept=0
    with (OUT/'build_record.jsonl').open('a',encoding='utf-8',buffering=1) as log:
        for i,r in enumerate(targets):
            bid=r['bldg_id'];target=OUT/('ND_'+bid+'.json')
            if target.exists():kept+=1;continue
            old=next((p for p in (BASE/'meshes_zone12_clean'/('P17RZ_'+bid+'.json'),BASE/'meshes_towers_clean'/('P17R_'+bid+'.json')) if p.exists()),None)
            try:
                if old:
                    data=json.loads(old.read_text(encoding='utf-8'));data['name']='ND_'+bid
                    target.write_text(json.dumps(data),encoding='utf-8')
                    rec={'bldg_id':bid,'source_mesh':str(old),'triangles':len(data['triangles']),'status':'reused clean measured form'}
                    reused+=1
                else:
                    rec=clean.build(bid,str(BASE),frame,county,dtm,str(OUT))
                    if rec is None:rec=clean.fallback_prism(bid,str(BASE),frame,county,dtm,str(OUT))
                    if rec is None:raise RuntimeError('No measured form could be built')
                    rec['status']='new measured clean form';made+=1
                log.write(json.dumps(rec)+chr(10))
                print(i+1,len(targets),bid,rec['status'],'tris',rec.get('triangles'),flush=True)
            except Exception as exc:
                failure={'bldg_id':bid,'error':repr(exc)};failed.append(failure)
                log.write(json.dumps(failure)+chr(10));print('FAILED',failure,flush=True)
    summary={'new':made,'reused':reused,'kept':kept,'failed':failed,'targets':len(targets)}
    (OUT/'build_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary),flush=True)
    return 1 if failed else 0


if __name__=='__main__':raise SystemExit(main())

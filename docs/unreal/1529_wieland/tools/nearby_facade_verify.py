"""Independent geometry verification for measured clean meshes and inferred facades."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

DATA=Path('E:/Wieland1529_site_data/phase20/nearby_detail')
RECORDS=Path(__file__).resolve().parents[1]/'review'/'phase20'/'nearby_detail'

def verify(bid):
    source=json.loads((DATA/'meshes_clean'/('ND_'+bid+'.json')).read_text())
    final=json.loads((DATA/'meshes_facade'/('NDF_'+bid+'.json')).read_text())
    record=json.loads((DATA/'meshes_facade'/('NDF_'+bid+'.record.json')).read_text())
    sverts=np.asarray(source['vertices'],dtype=float)
    verts=np.asarray(final['vertices'],dtype=float)
    tris=np.asarray(final['triangles'],dtype=int)
    mats=np.asarray(final['tri_mat'],dtype=int)
    tri=verts[tris]
    uv=np.asarray(final['uv0_m'],dtype=float)[tris]
    area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2
    assert np.isfinite(verts).all() and np.isfinite(uv).all(),'Non-finite vertex/UV'
    assert area.min()>1e-7,'Degenerate triangle'
    assert source['pivot']==final['pivot'],'Pivot changed'
    assert set(mats).issubset(set(range(6))),'Material slot outside 0..5'
    assert abs(verts[:,2].max()-sverts[:,2].max())<1e-5,'Measured top changed'
    assert len(tris)==len(mats),'Material count mismatch'
    retained=[]
    for indices,mat in zip(source['triangles'],source['tri_mat']):
        p=sverts[indices]
        n=np.cross(p[1]-p[0],p[2]-p[0]);n/=np.linalg.norm(n)
        if mat!=0 or abs(n[2])>.06:
            retained.append((p,int(mat),np.asarray(source['uv0_m'])[indices]))
    assert len(retained)==record['preserved_nonwall_triangles'],'Retained count mismatch'
    # Retained source triangles are first in the output. Verify all coordinates,
    # UVs, material indices, and winding, independently of builder internals.
    for i,(p,m,u) in enumerate(retained):
        assert np.allclose(tri[i],p,atol=.00006,rtol=0),'Roof/mast geometry changed'
        assert mats[i]==m,'Roof/mast material changed'
        assert np.allclose(uv[i],u,atol=.00006,rtol=0),'Roof/mast UV changed'
    # Moller-Trumbore intersections from outside each opening toward the interior.
    # The first hit must be recessed glass 48 cm away (30 cm exterior + 18 cm recess).
    e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0]
    distances=[]
    for probe in record['opening_ray_probes']:
        origin=np.asarray(probe['origin']);direction=np.asarray(probe['direction'])
        h=np.cross(np.broadcast_to(direction,e2.shape),e2)
        a=np.einsum('ij,ij->i',e1,h)
        valid=np.abs(a)>1e-9
        f=np.zeros_like(a);f[valid]=1/a[valid]
        s=origin-tri[:,0]
        u=f*np.einsum('ij,ij->i',s,h)
        q=np.cross(s,e1)
        v=f*np.einsum('j,ij->i',direction,q)
        dist=f*np.einsum('ij,ij->i',e2,q)
        valid&=(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(dist>1e-6)
        assert valid.any(),'Opening ray missed mesh'
        hit=np.where(valid,dist,np.inf).argmin()
        assert mats[hit]==3,f'Opening obstructed by slot {mats[hit]}'
        assert abs(dist[hit]-48)<.005,f'Glazing at incorrect depth {dist[hit]}'
        cross=np.cross(e1[hit],e2[hit])
        assert np.dot(cross,direction)>0,'Glass winding not inward as source convention'
        distances.append(float(dist[hit]))
    return {'county_id':bid,'triangles':len(tris),'min_final_area_cm2':float(area.min()),
            'preserved_roof_mast_triangles_exact':len(retained),
            'opening_first_hit_glass_count':len(distances),
            'opening_glass_distance_range_cm':[min(distances),max(distances)] if distances else [],
            'pivot_unchanged':True,'measured_top_unchanged':True,'result':'PASS'}

def main():
    p=argparse.ArgumentParser();p.add_argument('ids',nargs='*');p.add_argument('--all',action='store_true');args=p.parse_args()
    if args.all:
        import csv
        with (DATA/'active_targets.csv').open(encoding='utf-8-sig',newline='') as f:
            ids=[r['bldg_id'] for r in csv.DictReader(f)]
    else:ids=args.ids or ['777585','780284','781722']
    rows=[];failures=[]
    for bid in ids:
        try:rows.append(verify(bid))
        except Exception as ex:failures.append({'county_id':bid,'error':repr(ex)})
    summary={'tested':len(ids),'passed':len(rows),'failures':failures,'records':rows}
    path=RECORDS/('facade_qc_all.json' if args.all else 'facade_qc_pilots.json')
    path.write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='records'}))
    return 1 if failures else 0

if __name__=='__main__':raise SystemExit(main())
